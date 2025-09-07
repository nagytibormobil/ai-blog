#!/usr/bin/env python3
# generate_and_save.py (MODIFIED)
# Automatikus post-generálás: RAWG -> kép letöltés, YouTube embed, hosszú review, index frissítés.

import os
import random
import argparse
import datetime
import json
import time
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
    return None  # ha nincs, akkor None → nem generálunk posztot

# ==============
# CONTENT HELPERS
# ==============
def build_long_review(game_name, publisher, year):
    return f"<p><strong>{game_name}</strong> ({year}), developed by {publisher}, is explored in depth below. This review covers gameplay walkthroughs and cheat codes.</p>"

def generate_cheats_tips(game_name):
    tips = [
        "Use special abilities strategically to overcome tough enemies.",
        "Collect resources early to prepare for late-game challenges.",
        "Explore hidden areas to find rare items."
    ]
    items = "".join(f"<li>{tip}</li>" for tip in tips)
    return f"<ul>{items}</ul>"

def get_age_rating(game):
    rating = game.get("esrb_rating") or {"name":"Not specified"}
    name = rating.get("name") if isinstance(rating, dict) else str(rating)
    return f"{name}*" if name else "Not specified*"

# ==============
# FOOTER + MORE TO EXPLORE
# ==============
def more_to_explore_html():
    return """
    <div class="more-to-explore">
      <h2>More to Explore</h2>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <div style="flex:1;min-width:250px;border:1px solid #1f2a38;border-radius:12px;padding:8px">
          <img src="../Picture/sample1.jpg" alt="Explore 1" style="width:100%;border-radius:8px"/>
        </div>
        <div style="flex:1;min-width:250px;border:1px solid #1f2a38;border-radius:12px;padding:8px">
          <img src="../Picture/sample2.jpg" alt="Explore 2" style="width:100%;border-radius:8px"/>
        </div>
        <div style="flex:1;min-width:250px;border:1px solid #1f2a38;border-radius:12px;padding:8px">
          <img src="../Picture/sample3.jpg" alt="Explore 3" style="width:100%;border-radius:8px"/>
        </div>
      </div>
    </div>
    """

def post_footer_html():
    footer = f"""
    <hr>
    <section class="footer">
      <p><a href="file:///C:/ai_blog/terms.html">You can read all terms and conditions by clicking here.</a></p>
      <p class="tiny">© {datetime.datetime.now().year} AI Gaming Blog</p>
    </section>
    """
    return footer

# ==============
# POST GENERATION
# ==============
def generate_post_for_game(game):
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

    has_image = False
    if img_url:
        has_image = download_image(img_url, img_path)

    youtube_embed = get_youtube_embed(name)
    has_video = youtube_embed is not None

    # ⛔ ha nincs kép ÉS nincs videó → ne generáljon posztot
    if not (has_image or has_video):
        print(f"❌ Skipping '{name}' – no image or video found.")
        return None

    year = game.get("released") or ""
    publisher = game.get("publishers", [{}])[0].get("name", "the studio") if game.get("publishers") else "the studio"
    review_html = build_long_review(name, publisher, year)
    cheats_html = generate_cheats_tips(name)
    age_rating = get_age_rating(game)

    now = datetime.datetime.now()
    title = f"{name} Cheats, Tips & Full Review"
    cover_src = f"../{PICTURE_DIR}/{img_filename}"
    footer_block = post_footer_html()
    more_explore = more_to_explore_html()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{title}</title>
</head>
<body>
  <div class="wrap">
    <a href="../index.html">⬅ Back to Home</a>
    <h1>{title}</h1>
    <img class="cover" src="{cover_src}" alt="{name} cover"/>
    <h2>About the Game</h2>
    <ul>
      <li><strong>Release:</strong> {year}</li>
      <li><strong>Recommended Age:</strong> {age_rating}</li>
      <li><strong>Platforms:</strong> {', '.join([p['platform']['name'] for p in game.get('platforms', [])]) if game.get('platforms') else '—'}</li>
    </ul>
    <h2>Full Review</h2>
    {review_html}
    <h2>Gameplay Video</h2>
    {"<iframe width='100%' height='400' src='"+youtube_embed+"' frameborder='0' allowfullscreen></iframe>" if has_video else "<p>No video available.</p>"}
    <h2>Cheats & Tips</h2>
    {cheats_html}

    <h2 class="tiny">AI Rating</h2>
    <p class="tiny">⭐ {round(random.uniform(2.5,5.0),1)}/5</p>

    {more_explore}
    {footer_block}
  </div>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    post_dict = {
        "title": name,
        "url": f"{OUTPUT_DIR}/{filename}",
        "platform": [p['platform']['name'] for p in game.get('platforms', [])] if game.get('platforms') else [],
        "date": now.strftime("%Y-%m-%d"),
        "rating": round(random.uniform(2.5,5.0),1),
        "cover": f"{PICTURE_DIR}/{img_filename}",
        "views": 0,
        "comments": 0
    }
    print(f"✅ Generated post: {out_path}")
    return post_dict

# ==============
# MAIN FLOW (unchanged)
# ==============
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=NUM_TOTAL)
    args = parser.parse_args()
    total = args.num_posts

    # ... itt a fő ciklus változatlan marad ...
    print("⚡ Run complete.")

if __name__ == "__main__":
    main()
