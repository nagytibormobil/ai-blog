#!/usr/bin/env python3
# generate_and_save.py - Updated

import os
import random
import argparse
import datetime
import json
import time
import re
from pathlib import Path
import requests

OUTPUT_DIR = "generated_posts"
INDEX_FILE = "index.html"
PICTURE_DIR = "Picture"

RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"
YOUTUBE_API_KEY = "AIzaSyAXedHcSZ4zUaqSaD3MFahLz75IvSmxggM"

NUM_TOTAL = 12
NUM_POPULAR = 2
RAWG_PAGE_SIZE = 40
USER_AGENT = "AI-Gaming-Blog-Agent/1.0"

Path(OUTPUT_DIR).mkdir(exist_ok=True)
Path(PICTURE_DIR).mkdir(exist_ok=True)

# Helpers
def slugify(name):
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s

# RAWG API Functions
def rawg_search_random(page=1, page_size=RAWG_PAGE_SIZE):
    url = "https://api.rawg.io/api/games"
    params = {"key": RAWG_API_KEY, "page": page, "page_size": page_size}
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json().get("results", [])

def rawg_get_popular(page=1, page_size=RAWG_PAGE_SIZE):
    url = "https://api.rawg.io/api/games"
    params = {"key": RAWG_API_KEY, "page": page, "page_size": page_size, "ordering": "-added"}
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json().get("results", [])

# Download Image
def download_image(url, dest_path):
    try:
        headers = {"User-Agent": USER_AGENT}
        r = requests.get(url, headers=headers, stream=True, timeout=20)
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"⚠️  Image download failed: {e}")
        return False

# YouTube Embed
def get_youtube_embed(game_name):
    if not YOUTUBE_API_KEY:
        return None
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {"part": "snippet", "q": f"{game_name} gameplay", "type": "video", "maxResults": 1, "key": YOUTUBE_API_KEY}
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        items = r.json().get("items", [])
        if items:
            video_id = items[0]["id"]["videoId"]
            return f"https://www.youtube.com/embed/{video_id}"
    except Exception as e:
        print(f"Error fetching YouTube video for {game_name}: {e}")
    return "https://www.youtube.com/embed/dQw4w9WgXcQ"

# Read and Write index posts
def read_index_posts():
    if not os.path.exists(INDEX_FILE):
        return []
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"POSTS\s*=\s*(\[\s*[\s\S]*?\])\s*;", html)
    if not m:
        return []
    arr_text = m.group(1)
    try:
        posts = json.loads(arr_text)
        return posts if isinstance(posts, list) else []
    except Exception:
        return []

def write_index_posts(all_posts):
    if not os.path.exists(INDEX_FILE):
        print("index.html not found, skipping index update.")
        return
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()
    new_json = json.dumps(all_posts, indent=2, ensure_ascii=False)
    if "// <<< AUTO-GENERATED POSTS START >>>" in html and "// <<< AUTO-GENERATED POSTS END >>>" in html:
        new_html = re.sub(
            r"// <<< AUTO-GENERATED POSTS START >>>[\s\S]*?// <<< AUTO-GENERATED POSTS END >>>",
            f"// <<< AUTO-GENERATED POSTS START >>>\n    const POSTS = {new_json};\n    // <<< AUTO-GENERATED POSTS END >>>",
            html
        )
    else:
        new_html = re.sub(r"POSTS\s*=\s*\[[\s\S]*?\]", f"POSTS = {new_json}", html)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("✅ index.html POSTS updated.")

# Build Long Review
def build_long_review(game_name, publisher, year):
    parts = []
    intro = f"<p><strong>{game_name}</strong> ({year}), developed by {publisher}, is explored in depth below. This review covers gameplay walkthroughs and cheat codes.</p>"
    parts.append(intro)
    walkthrough_sentences = [
        "The game starts with a tutorial guiding new players through the core mechanics.",
        "Early levels introduce basic enemies and gradually increase the difficulty.",
        "Players will encounter several side quests that enrich the main storyline.",
        "Inventory management and crafting play a key role in progression.",
        "Boss fights require strategic use of character skills and abilities.",
        "Certain areas hide collectibles and secrets that reward exploration.",
        "Multiplayer or co-op challenges provide additional replay value.",
        "Advanced techniques and combos can be learned for mastery.",
        "Leveling up characters unlocks new abilities and perks.",
        "Some puzzles require logical thinking and observation skills.",
        "Story-driven choices can affect game outcomes and endings.",
        "Timed challenges test player reflexes and decision-making.",
        "Exploration of optional zones gives bonus items and experience.",
        "Achievements can be unlocked by completing specific objectives.",
        "Replay modes allow experimentation with different strategies.",
    ]
    cheat_sentences = [
        "Using the console command `godmode` enables invincibility.",
        "Entering `unlock_all_weapons` grants access to all weapons instantly.",
        "The `add_gold 1000` cheat adds gold to your inventory.",
        "Using `noclip` allows walking through walls.",
        "Cheat codes may vary between platform versions.",
        "Some cheats are hidden and discovered through exploration.",
        "Always save progress before using cheats to avoid issues.",
        "Certain cheats affect achievements and may disable them.",
        "Debug mode can be activated for testing new features.",
        "Combining specific cheats can produce unexpected effects.",
    ]
    for i in range(15):
        if i % 2 == 0 and i//2 < len(walkthrough_sentences):
            parts.append(f"<p>{walkthrough_sentences[i//2]}</p>")
        elif i//2 < len(cheat_sentences):
            parts.append(f"<p>{cheat_sentences[i//2]}</p>")
    parts.append("<p>Overall, this game provides a mix of exploration, strategy, and fun. Use the tips and cheats wisely to enhance your gameplay.</p>")
    return "\n".join(parts)

# Generate Cheats & Tips
def generate_cheats_tips(game_name):
    tips = [
        "Use special abilities strategically to overcome tough enemies.",
        "Collect resources early to prepare for late-game challenges.",
        "Explore hidden areas to find rare items.",
        "Experiment with different weapons and skills combinations.",
        "Save frequently to avoid losing progress.",
        "Learn enemy patterns to improve combat efficiency.",
        "Complete side quests for bonus rewards.",
        "Use fast travel to save time between zones.",
        "Upgrade equipment as soon as possible for better performance.",
        "Watch for environmental clues to solve puzzles.",
        "Use stealth when facing stronger foes.",
        "Combine items for special effects.",
        "Take advantage of in-game tutorials for mastery.",
        "Interact with NPCs to unlock hidden missions.",
        "Prioritize main objectives to progress efficiently."
    ]
    items = "".join(f"<li>{tip}</li>" for tip in tips[:15])
    return f"<ul>{items}</ul>"

# Age Rating
def get_age_rating(game):
    rating = game.get("esrb_rating") or game.get("age_rating") or {"name":"Not specified"}
    name = rating.get("name") if isinstance(rating, dict) else str(rating)
    return f"{name}*" if name else "Not specified*"

# Footer with updated Terms link
def post_footer_html():
    footer = f"""
    <hr>
    <section class=\"footer\">
      <p class=\"tiny\"><a href=\"file:///C:/ai_blog/terms.html\">You can read all terms and conditions by clicking here.</a></p>
      <p class=\"tiny\">© {datetime.datetime.now().year} AI Gaming Blog</p>
    </section>
    """
    return footer

# Generate Post
def generate_post_for_game(game):
    name = game.get("name") or "Unknown Game"
    slug = slugify(name)
    filename = f"{slug}.html"
    out_path = os.path.join(OUTPUT_DIR, filename)

    img_url = game.get("background_image") or game.get("background_image_additional") or ""
    img_filename = f"{slug}.jpg"
    img_path = os.path.join(PICTURE_DIR, img_filename)
    if img_url:
        download_image(img_url, img_path)
    else:
        download_image(f"https://placehold.co/800x450?text={name.replace(' ', '+')}", img_path)

    youtube_embed = get_youtube_embed(name)
    year = game.get("released") or ""
    publisher = game.get("publisher") or "Unknown"
    review_html = build_long_review(name, publisher, year)
    cheats_html = generate_cheats_tips(name)
    age_rating = get_age_rating(game)
    cover_src = f"../{PICTURE_DIR}/{img_filename}"

    more_to_explore_html = f"<h2>More to Explore</h2><div class=\"more-explore\">[Randomized sample posts here]</div>"

    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\"/>
<title>{name}</title>
</head>
<body>
<a href=\"../index.html\">⬅ Back to Home</a>
<h1>{name} Cheats, Tips & Full Review</h1>
<img src=\"{cover_src}\" alt=\"{name}\"/>
{review_html}
{cheats_html}
<h2 class=\"tiny\">AI Rating</h2>
<p class=\"tiny\">⭐ {round(random.uniform(2.5,5.0),1)}/5</p>
{more_to_explore_html}
{post_footer_html()}
</body>
</html>"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    return {
        "title": name,
        "url": f"{OUTPUT_DIR}/{filename}",
        "platform": [p['platform']['name'] for p in game.get('platforms', [])] if game.get('platforms') else [],
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "rating": round(random.uniform(2.5,5.0),1),
        "cover": f"{PICTURE_DIR}/{img_filename}",
        "views": 0,
        "comments": 0
    }

# Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=NUM_TOTAL)
    args = parser.parse_args()

    existing_posts = read_index_posts()
    existing_titles = set(p["title"].lower() for p in existing_posts)

    random_candidates, popular_candidates = [], []  # Keep original gather logic if needed
    candidates = random_candidates + popular_candidates

    posts_added = []
    for cand in candidates:
        post = generate_post_for_game(cand)
        if post:
            posts_added.append(post)

    combined = posts_added + existing_posts
    seen = set()
    unique_posts = []
    for p
