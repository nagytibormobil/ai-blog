#!/usr/bin/env python3
# generate_and_save.py
# Automatic post generation: RAWG -> image download, YouTube embed, narrative review, index update.
# Requirements: requests, bs4 installed (pip install requests beautifulsoup4)

import os
import random
import datetime
import json
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup

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
        print(f"⚠️ Image download failed: {e}")
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
# CONTENT HELPERS
# ==============
def build_narrative_review(game):
    name = game.get("name") or "Unknown Game"
    year = game.get("released") or "N/A"
    publisher = game.get("publisher") or (game.get("developers",[{}])[0].get("name","Unknown") if isinstance(game.get("developers"), list) else "Unknown")
    wiki_url = game.get("wiki_url", "#")
    steam_url = game.get("steam_url", "#")
    metacritic_url = game.get("metacritic_url", "#")

    # Random narrative style
    intros = [
        f"I just jumped into **{name.upper()}** ({year}), developed by {publisher}. The moment I loaded the game, my eyes widened with excitement.",
        f"Starting **{name}**, I felt like I was stepping into an entirely new world. Developed by {publisher}, released in {year}, this adventure is unforgettable.",
        f"Launching **{name}** ({year}) by {publisher} instantly drew me into its universe."
    ]
    intro = random.choice(intros)

    gameplay_paragraphs = [
        f"The **gameplay** is engaging from the first second. I found myself exploring secret corners, uncovering hidden collectibles, and tackling challenges that felt both fresh and rewarding.",
        f"Every level of **{name}** brings something new. From tricky puzzles to intense battles, the variety kept me glued to the screen.",
        f"Playing online with friends adds a layer of excitement and strategy. Each session feels unique, and I loved coordinating with my teammates to overcome obstacles.",
        f"The controls feel natural, and mastering the character's abilities is a thrill. Timing attacks and using skills strategically makes the battles so satisfying.",
        f"Visually, the game is stunning. Environments are richly detailed, and I often paused just to admire the scenery."
    ]
    random.shuffle(gameplay_paragraphs)
    gameplay_text = " ".join(gameplay_paragraphs[:3])

    # Cheats & Tips
    cheats_found = game.get("official_cheats", [])
    if cheats_found:
        cheats_text = "During my playthrough, I discovered the following **cheats and tips** that enhanced my experience: "
        cheats_text += " ".join([f"<span style='color:#FFD700;font-weight:bold'>{c}</span> (Source: {game.get('cheats_source', 'Official')})." for c in cheats_found])
    else:
        cheats_text = "I searched online but couldn’t find any official cheats or tips for this game."

    review_html = f"""
<p>{intro}</p>
<div style="height:12px"></div>
<p>{gameplay_text}</p>
<div style="height:12px"></div>
<p>{cheats_text}</p>
<p>For more details, check <a href="{wiki_url}">Wikipedia</a>, <a href="{steam_url}">Steam</a>, or <a href="{metacritic_url}">Metacritic</a>.</p>
"""
    return review_html

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

def download_cover_image(game, slug):
    img_url = game.get("background_image") or game.get("background_image_additional") or ""
    img_filename = f"{slug}.jpg"
    img_path = os.path.join(PICTURE_DIR, img_filename)
    if not os.path.exists(img_path):
        if img_url:
            if not download_image(img_url, img_path):
                ph_url = f"https://placehold.co/800x450?text={slug.replace('-', '+')}"
                download_image(ph_url, img_path)
        else:
            ph_url = f"https://placehold.co/800x450?text={slug.replace('-', '+')}"
            download_image(ph_url, img_path)
    return img_filename

def generate_post_for_game(game, all_posts):
    name = game.get("name") or "Unknown Game"
    slug = slugify(name)
    filename = f"{slug}.html"
    out_path = os.path.join(OUTPUT_DIR, filename)

    if os.path.exists(out_path):
        print(f"⚠️ Post already exists for '{name}' -> {filename} (skipping)")
        return None

    img_filename = download_cover_image(game, slug)
    youtube_embed = get_youtube_embed(name)
    review_html = build_narrative_review(game)

    now = datetime.datetime.now()
    title = f"{name} - Full Review & Gameplay Experience"
    cover_src = f"../{PICTURE_DIR}/{img_filename}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title}</title>
<meta name="description" content="Full narrative review and gameplay experience for {name}."/>
<style>
:root{{--bg:#0b0f14;--panel:#121821;--muted:#9fb0c3;--text:#eaf1f8;--accent:#5cc8ff;--card:#0f141c;--border:#1f2a38}}
html,body{{margin:0;padding:0;background:var(--bg);color:var(--text);font-family:'Inter','Roboto',sans-serif;font-size:18px}}
.wrap{{max-width:900px;margin:24px auto;padding:18px;background:var(--panel);border-radius:12px;border:1px solid var(--border)}}
img.cover{{width:100%;height:auto;border-radius:8px;display:block}}
h1{{margin:10px 0 6px;font-size:28px}}
h2{{margin-top:18px}}
p{{color:var(--text);line-height:1.6}}
a{{color:var(--accent)}}
.more-to-explore{{margin-top:32px}}
.explore-grid{{display:flex;gap:12px;flex-wrap:wrap}}
.explore-item{{flex:1 1 calc(33.333% - 8px);border:1px solid var(--border);border-radius:8px;overflow:hidden;background:var(--card)}}
.explore-item img{{width:100%;display:block}}
.explore-item-title{{padding:6px;color:var(--text);font-size:14px;text-align:center}}
</style>
</head>
<body>
<div class="wrap">
<a href="../index.html" style="color:var(--accent)">⬅ Back to Home</a>
<h1>{title}</h1>
<img class="cover" src="{cover_src}" alt="{name} cover"/>
<div style="height:12px"></div>
{review_html}
<h2>Gameplay Video</h2>
<iframe width="100%" height="400" src="{youtube_embed}" frameborder="0" allowfullscreen></iframe>
{generate_more_to_explore([p for p in all_posts if p['title'] != name])}
{post_footer_html()}
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
        "date": now.strftime("%Y-%m-%d %H:%M:%S"),
        "cover": f"{PICTURE_DIR}/{img_filename}",
        "views": 0,
        "comments": 0
    }
    print(f"✅ Generated post: {out_path}")
    return post_dict

# ==============
# FOOTER
# ==============
def post_footer_html():
    return f"""
<section class="footer">
<p class="tiny">© {datetime.datetime.now().year} AI Gaming Blog</p>
</section>
"""

# ==============
# MAIN FLOW
# ==============
def gather_candidates(total_needed, num_popular):
    random_candidates = []
    popular_candidates = []
    attempts = 0
    page = 1
    while len(popular_candidates) < num_popular and attempts < 8:
        try:
            res = rawg_get_popular(page=page)
            if not res:
                break
            for g in res:
                if len(popular_candidates) >= num_popular:
                    break
                popular_candidates.append(g)
            page += 1
        except Exception as e:
            print("RAWG popular fetch error:", e)
            break
        attempts += 1

    collected = []
    attempts = 0
    while len(collected) < (total_needed - len(popular_candidates)) and attempts < 12:
        try:
            page_rand = random.randint(1, 20)
            res = rawg_search_random(page=page_rand)
            if res:
                collected.extend(res)
        except Exception as e:
            print("RAWG fetch error:", e)
        attempts += 1

    random.shuffle(collected)
    needed = total_needed - len(popular_candidates)
    random_candidates = collected[:needed]
    return random_candidates, popular_candidates

def main():
    all_posts = read_index_posts()
    random_candidates, popular_candidates = gather_candidates(NUM_TOTAL, NUM_POPULAR)
    selected_games = popular_candidates + random_candidates

    for game in selected_games:
        post = generate_post_for_game(game, all_posts)
        if post:
            all_posts.append(post)

    all_posts.sort(key=lambda x: x.get("date", ""), reverse=True)
    write_index_posts(all_posts)

if __name__ == "__main__":
    main()
