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

# ==============
# CONTENT HELPERS
# ==============
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

# ==============
# MORE TO EXPLORE
# ==============
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
    """
    return html

# ==============
# FOOTER
# ==============
def post_footer_html():
    footer = f"""
    <hr>
    <section class=\"footer\">
      <p class=\"tiny\"><a href=\"file:///C:/ai_blog/terms.html\">You can read all terms and conditions by clicking here.</a></p>
    </section>
    """
    return footer

# ==============
# POST GENERATION
# ==============
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
  <meta charset=\"utf-8\"/>
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>
  <title>{title}</title>
  <meta name=\"description\" content=\"Cheats, tips and a long review for {name}.\"/>
  <style>
    :root{{--bg:#0b0f14;--panel:#121821;--muted:#9fb0c3;--text:#eaf1f8;--accent:#5cc8ff;--card:#0f141c;--border:#1f2a38}}
    html,body{{margin:0;padding:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,Segoe UI,Roboto,Inter,Arial,sans-serif}}
    .wrap{{max-width:900px;margin:24px auto;padding:18px;background:var(--panel);border-radius:12px;border:1px solid var(--border)}}
    img.cover{{width:100%;height:auto;border-radius:8px;display:block}}
    h1{{margin:10px 0 6px;font-size:28px}}
    h2{{margin-top:18px}}
    p{{color:var(--text);line-height:1.6}}
    .tiny{{color:var(--muted);font-size:13px}}
    a{{color:var(--accent)}}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <a href=\"../index.html\" style=\"color:var(--accent)\">⬅ Back to Home</a>
    <h1>{title}</h1>
    <img class=\"cover\" src=\"{cover_src}\" alt=\"{name} cover\"/>
    <h2>About the Game</h2>
    <ul>
      <li><strong>Release:</strong> {year}</li>
      <li><strong>Recommended Age:</strong> {age_rating}</li>
      <li><strong>Platforms:</strong> {', '.join([p['platform']['name'] for p in game.get('platforms', [])]) if game.get('platforms') else '—'}</li>
    </ul>
    <h2>Full Review</h2>
    {review_html}
    <h2>Gameplay Video</h2>
    <iframe width=\"100%\" height=\"400\" src=\"{youtube_embed}\" frameborder=\"0\" allowfullscreen></iframe>
    <h2>Cheats & Tips</h2>
    {cheats_html}
    <h2 class=\"tiny\">AI Rating</h2>
    <p class=\"tiny\">⭐ {round(random.uniform(2.5,5.0),1)}/5</p>
    {more_block}
    {footer_block}
  </div>
</body>
</html>"""

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
# MAIN
# ==============
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=NUM_TOTAL)
    args = parser.parse_args()
    total = args.num_posts

    existing_posts = read_index_posts()
    existing_titles = set(p.get("title","").lower() for p in existing_posts)

    # Gyűjtés
    random_candidates = rawg_search_random()
    popular_candidates = rawg_get_popular()
    candidates = popular_candidates + random_candidates

    posts_added = []
    for cand in candidates[:total]:
        name = cand.get("name","")
        if not name or name.lower() in existing_titles:
            continue
        post = generate_post_for_game(cand, existing_posts)
        if post:
            posts_added.append(post)
            existing_titles.add(name.lower())
        time.sleep(0.7)

    combined = posts_added + existing_posts
    seen = set()
    unique_posts = []
    for p in combined:
        t = p.get("title","").lower()
        if t in seen:
            continue
        seen.add(t)
        unique_posts.append(p)

    unique_posts.sort(key=lambda x: x.get("date",""), reverse=True)
    write_index_posts(unique_posts)

    print(f"Done. New posts added: {len(posts_added)}")

if __name__ == "__main__":
    main()
