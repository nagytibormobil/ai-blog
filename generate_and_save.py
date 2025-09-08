#!/usr/bin/env python3
# generate_and_save.py
# Automatic narrative post generation: RAWG -> image download, YouTube embed, immersive review, index update.
# Requirements: requests, bs4 (pip install requests beautifulsoup4)

import os
import random
import datetime
import json
import re
from pathlib import Path
import requests

# ==============
# SETTINGS
# ==============
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

# ==============
# HELPERS
# ==============
def slugify(name):
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s

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

def read_index_posts():
    if not os.path.exists(INDEX_FILE):
        return []
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"POSTS\s*=\s*(\[\s*[\s\S]*?\])\s*;", html)
    if not m:
        m = re.search(r"// <<< AUTO-GENERATED POSTS START >>>\s*const POSTS =\s*(\[\s*[\s\S]*?\])\s*;?\s*// <<< AUTO-GENERATED POSTS END >>>", html)
        if m:
            arr_text = m.group(1)
        else:
            return []
    else:
        arr_text = m.group(1)
    try:
        posts = json.loads(arr_text)
        return posts if isinstance(posts, list) else []
    except Exception:
        cleaned = re.sub(r",\s*}", "}", arr_text)
        cleaned = re.sub(r",\s*\]", "]", cleaned)
        try:
            return json.loads(cleaned)
        except:
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

# ==============
# NARRATIVE CONTENT GENERATOR
# ==============
def build_narrative_review(game):
    name = game.get("name") or "Unknown Game"
    release = game.get("released") or "Unknown"
    developer = game.get("developers", [{}])[0].get("name", "Unknown Studio") if isinstance(game.get("developers"), list) else "Unknown Studio"
    wiki_url = game.get("wiki_url") or f"https://en.wikipedia.org/wiki/{name.replace(' ','_')}"
    steam_url = game.get("steam_url") or "#"
    metacritic_url = game.get("metacritic_url") or "#"

    paragraphs = []

    paragraphs.append(f"I recently dived into **{name.upper()}** (Released: {release}) developed by **{developer}**. From the first moment, I felt immersed in its **AMAZING WORLD**. For details, check [Wikipedia]({wiki_url}), [Steam page]({steam_url}), or [Metacritic]({metacritic_url}).")

    paragraphs.append(f"As I explored, the **environments and level design** were breathtaking. Every shadow, every sound made the adventure feel real. The first combat surprised me – learning the mechanics was a thrill, and victories felt personally rewarding.")

    if game.get("official_cheats"):
        cheat_texts = []
        for cheat in game["official_cheats"]:
            cheat_texts.append(f"{cheat['description']} (Source: {cheat.get('source','official')})")
        cheat_paragraph = " ".join(cheat_texts)
        paragraphs.append(f"During play, I used official tips/cheats: {cheat_paragraph}. They enhanced the experience without breaking immersion.")
    else:
        paragraphs.append("I searched online but found **no official cheats or tips**, so all experiences are from personal gameplay.")

    paragraphs.append(f"Hidden secrets and side quests kept me entertained for hours. Multiplayer or co-op added **EXCITEMENT**, requiring strategy and teamwork. Every match felt fresh and engaging.")

    paragraphs.append(f"Mastering abilities and controls was satisfying. Weapon sounds, character animations, vehicle handling – all details made gameplay tangible. Timing and strategy often gave me an edge in challenges.")

    paragraphs.append(f"Patch updates and improvements influenced strategies, keeping tips relevant. Overall, **{name}** provided an unforgettable adventure. Each session felt like a new story to tell friends, full of discoveries and thrills.")

    return "\n\n".join(paragraphs)

def get_age_rating(game):
    rating = game.get("esrb_rating") or game.get("age_rating") or {"name":"Not specified"}
    name = rating.get("name") if isinstance(rating, dict) else str(rating)
    return f"{name}*" if name else "Not specified*"

def generate_more_to_explore(posts, n=3):
    selected = random.sample(posts, min(n, len(posts)))
    html = '<section class="more-to-explore">\n<h2>More to Explore</h2>\n<div class="explore-grid">\n'
    for post in selected:
        html += f'''
        <div class="explore-item">
            <a href="../{post['url']}">
                <img src="../{post['cover']}" alt="{post['title']}">
                <div class="explore-item-title">{post['title']}</div>
            </a>
        </div>
        '''
    html += '</div>\n</section>\n'
    return html

def post_footer_html():
    footer = f"""
    <section class="footer">
      <div class="row">
        <div>
          <p class="tiny">
            <a href="../terms.html" target="_blank">
              You can read all terms and conditions by clicking here.
            </a>
          </p>
        </div>
      </div>
      <p class="tiny">© {datetime.datetime.now().year} AI Gaming Blog</p>
    </section>
    """
    return footer

def generate_post_for_game(game, all_posts):
    name = game.get("name") or "Unknown Game"
    slug = slugify(name)
    filename = f"{slug}.html"
    out_path = os.path.join(OUTPUT_DIR, filename)

    if os.path.exists(out_path):
        print(f"⚠️  Post already exists for '{name}' -> {filename} (skipping)")
        return None

    img_url = game.get("background_image") or ""
    img_filename = f"{slug}.jpg"
    img_path = os.path.join(PICTURE_DIR, img_filename)
    if not os.path.exists(img_path):
        if img_url:
            ok = download_image(img_url, img_path)
            if not ok:
                ph_url = f"https://placehold.co/800x450?text={name.replace(' ', '+')}"
                download_image(ph_url, img_path)
        else:
            ph_url = f"https://placehold.co/800x450?text={name.replace(' ', '+')}"
            download_image(ph_url, img_path)

    youtube_embed = get_youtube_embed(name)
    review_html = build_narrative_review(game)
    age_rating = get_age_rating(game)

    now = datetime.datetime.now()
    title = f"{name} Full Narrative Review"
    cover_src = f"../{PICTURE_DIR}/{img_filename}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{title}</title>
  <meta name="description" content="Narrative review and immersive gameplay experience of {name}."/>
  <style>
   
