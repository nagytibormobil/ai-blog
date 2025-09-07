#!/usr/bin/env python3
# generate_and_save.py
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

# SETTINGS
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

# HELPERS
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
    if "POSTS" in html:
        new_html = re.sub(r"POSTS\s*=\s*\[[\s\S]*?\];", f"POSTS = {new_json};", html)
    else:
        new_html = html
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("✅ index.html POSTS updated.")

# CONTENT HELPERS
def build_long_review(game_name, publisher, year):
    return f"<p><strong>{game_name}</strong> ({year}), developed by {publisher}, is explored in depth below. Tips, walkthroughs and cheat codes included.</p>"

def generate_cheats_tips(game_name):
    tips = [
        "Use special abilities strategically.",
        "Collect resources early.",
        "Explore hidden areas.",
        "Save frequently.",
        "Learn enemy patterns.",
        "Complete side quests.",
        "Upgrade equipment early.",
        "Combine items for effects.",
        "Take advantage of tutorials.",
        "Interact with NPCs for hidden missions."
    ]
    items = "".join(f"<li>{tip}</li>" for tip in tips[:15])
    return f"<ul>{items}</ul>"

def get_age_rating(game):
    rating = game.get("esrb_rating") or {"name":"Not specified"}
    name = rating.get("name") if isinstance(rating, dict) else str(rating)
    return f"{name}*" if name else "Not specified*"

# MORE TO EXPLORE

def more_to_explore_html(current_title, all_posts):
    candidates = [p for p in all_posts if p['title'].lower() != current_title.lower()]
    selected = random.sample(candidates, min(3, len(candidates)))
    cards_html = ""
    for p in selected:
        cards_html += f"""
        <div class=\"card\">
          <a href=\"../{p['url']}\">
            <img src=\"../{p['cover']}\" alt=\"{p['title']}\">
            <div class=\"card-title\">{p['title']}</div>
          </a>
        </div>
        """
    html = f"""
    <section class=\"more-explore\">
      <h2>More to Explore</h2>
      <div class=\"row\">
        {cards_html}
      </div>
    </section>
    <style>
      .more-explore .row {{ display: flex; gap: 12px; flex-wrap: wrap; justify-content: space-between; }}
      .more-explore .card {{ flex: 1 1 calc(33% - 8px); max-width: calc(33% - 8px); background: var(--card); border-radius: 12px; overflow: hidden; border: 1px solid var(--border); text-align: center; transition: transform 0.2s; cursor: pointer; }}
      .more-explore .card img {{ width: 100%; height: auto; display: block; }}
      .more-explore .card:hover {{ transform: scale(1.03); }}
      .more-explore .card-title {{ padding: 8px; color: var(--accent); font-weight: 600; font-size: 14px; }}
    </style>
    """
    return html

# FOOTER

def post_footer_html():
    footer = f"""
    <hr>
    <section class=\"footer\">
      <p class=\"tiny\"><a href=\"file:///C:/ai_blog/terms.html\">You can read all terms and conditions by clicking here.</a></p>
    </section>
    """
    return footer

# POST GENERATION

def generate_post_for_game(game, all_posts):
    name = game.get("name") or "Unknown Game"
    slug = slugify(name)
    filename = f"{slug}.html"
    out_path = os.path.join(OUTPUT_DIR, filename)

    img_url = game.get("background_image") or ""
    img_filename = f"{slug}.jpg"
    img_path = os.path.join(PICTURE_DIR, img_filename)

    if not os.path.exists(img_path) and img_url:
        download_image(img_url, img_path)

    youtube_embed = get_youtube_embed(name)
    year = game.get("released") or ""
    publisher = game.get("publisher") or "the studio"
    review_html = build_long_review(name, publisher, year)
    cheats_html = generate_cheats_tips(name)
    age_rating = get_age_rating(game)

    now = datetime.datetime.now()
    title = f"{name} Cheats, Tips & Full Review"
    cover_src = f"../{PICTURE_DIR}/{img_filename}"
    footer_block = post_footer_html()
    more_block = more_to_explore_html(name, all_posts)

    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
