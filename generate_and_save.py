#!/usr/bin/env python3
# generate_and_save.py
# Automatikus post-generálás: RAWG -> kép letöltés, YouTube embed, hosszú review, index frissítés.
# Elvárások: requests, bs4 telepítve (pip install requests beautifulsoup4)

import os
import random
import argparse
import datetime
import json
import time
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# ==============
# SETTINGS (API kulcsok beállítva)
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
# NEW HELPERS FOR CONTENT
# ==============
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
    conclusion = "<p>Overall, this game provides a mix of exploration, strategy, and fun. Use the tips and cheats wisely to enhance your gameplay.</p>"
    parts.append(conclusion)
    return "\n".join(parts)

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
    if not tips:
        return "<p>No cheats or tips found for this game.</p>"
    else:
        items = "".join(f"<li>{tip}</li>" for tip in tips[:15])
        return f"<ul>{items}</ul>"

def get_age_rating(game):
    rating = game.get("esrb_rating") or game.get("age_rating") or {"name":"Not specified"}
    name = rating.get("name") if isinstance(rating, dict) else str(rating)
    return f"{name}*" if name else "Not specified*"

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

    img_url = game.get("background_image") or game.get("background_image_additional") or ""
    img_filename = f"{slug}.jpg"
    img_path = os.path.join(PICTURE_DIR, img_filename)

    if os.path.exists(img_path):
        print(f"⚠️  Image already exists for '{name}' -> {img_filename} (skipping)")
        return None

    if img_url:
        ok = download_image(img_url, img_path)
        if not ok:
            ph_url = f"https://placehold.co/800x450?text={name.replace(' ', '+')}"
            download_image(ph_url, img_path)
    else:
        ph_url = f"https://placehold.co/800x450?text={name.replace(' ', '+')}"
        download_image(ph_url, img_path)

    youtube_embed = get_youtube_embed(name)

    year = game.get("released") or ""
    publisher = game.get("publisher") or game.get("developers", [{}])[0].get("name", "") if isinstance(game.get("developers"), list) else ""
    review_html = build_long_review(name, publisher or "the studio", year)
    cheats_html = generate_cheats_tips(name)
    age_rating = get_age_rating(game)

    now = datetime.datetime.now()
    title = f"{name} Cheats, Tips & Full Review"
    cover_src = f"../{PICTURE_DIR}/{img_filename}"
    footer_block = post_footer_html()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{title}</title>
  <meta name="description" content="Cheats, tips and a long review for {name}."/>
  <style>
    :root{{--bg:#0b0f14;--panel:#121821;--muted:#9fb0c3;--text:#eaf1f8;--accent:#5cc8ff;--card:#0f141c;--border:#1f2a38}}
    html,body{{margin:0;padding:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,Segoe UI,Roboto,Inter,Arial,sans-serif}}
    .wrap{{max-width:900px;margin:24px auto;padding:18px;background:var(--panel);border-radius:12px;border:1px solid var(--border)}}
    img.cover{{width:100%;height:auto;border-radius:8px;display:block}}
    h1{{margin:10px 0 6px;font-size:28px}}
    h2{{margin-top:18px}}
    p{{color:var(--text);line-height:1.6}}
    .tiny{{color:var(--muted);font-size:13px}}
    .ad{{background:linear-gradient(180deg,rgba(255,209,102,.06),transparent);padding:12px;border-radius:10px;border:1px dashed #ffd166;color:var(--text)}}
    a{{color:var(--accent)}}
  </style>
</head>
<body>
  <div class="wrap">
    <a href="../index.html" style="color:var(--accent)">⬅ Back to Home</a>
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
    <iframe width="100%" height="400" src="{youtube_embed}" frameborder="0" allowfullscreen></iframe>
    <h2>Cheats & Tips</h2>
    {cheats_html}

    <h2 class="tiny">AI Rating</h2>
    <p class="tiny">⭐ {round(random.uniform(2.5,5.0),1)}/5</p>

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
    page = 1
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

def post_footer_html():
    footer = """
    <hr>
    <section class="ad">
      <h3>Earn Real Money While You Play 📱</h3>
      <p>Simple passive income by sharing a bit of your internet. Runs in the background while you game.</p>
      <p><a href="https://r.honeygain.me/NAGYT86DD6" target="_blank"><strong>Try Honeygain now</strong></a></p>
      <div class="tiny">Sponsored. Use at your own discretion.</div>
    </section>
    <div class="row" style="margin-top:12px">
      <div class="ad" style="border-style:solid;border-color:#1f2a38">
        <h3>IC Markets – Trade like a pro 🌍</h3>
        <p><a href="https://icmarkets.com/?camp=3992" target="_blank">Open an account</a></p>
      </div>
      <div class="ad" style="border-style:solid;border-color:#1f2a38">
        <h3>Dukascopy – Promo code: <code>E12831</code> 🏦</h3>
        <p><a href="https://www.dukascopy.com/api/es/12831/type-S/target-id-149" target="_blank">Start here</a></p>
      </div>
    </div>
    <section class="footer">
      <div class="row">
        <div>
          <strong>Comment Policy</strong>
          <ul class="list tiny">
            <li>No spam, ads, or offensive content.</li>
            <li>No adult/drugs/war/terror topics.</li>
            <li>Max 10 comments/day per person.</li>
            <li>Be respectful. We moderate strictly.</li>
          </ul>
        </div>
        <div>
          <strong>Terms</strong>
          <p class="tiny">All content is for informational/entertainment purposes only. Trademarks belong to their respective owners. Affiliate links may generate commissions.</p>
        </div>
      </div>
      <p class="tiny">© {year} AI Gaming Blog</p>
    </section>
    """.format(year=datetime.datetime.now().year)
    return footer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=NUM_TOTAL)
    args = parser.parse_args()
    total = args.num_posts

    existing_posts = read_index_posts()
    existing_titles = set(p.get("title","").lower() for p in existing_posts)
    existing_filenames = set(os.path.basename(p.get("url","")) for p in existing_posts if p.get("url"))

    random_candidates, popular_candidates = gather_candidates(total, NUM_POPULAR)
    candidates = []
    candidates.extend(popular_candidates)
    candidates.extend(random_candidates)

    posts_added = []
    for cand in candidates:
        name = cand.get("name","").strip()
        if not name:
            continue
        slug = slugify(name)
        filename = f"{slug}.html"
        if name.lower() in existing_titles or filename in existing_filenames or os.path.exists(os.path.join(PICTURE_DIR, f"{slug}.jpg")):
            print(f"Skipping '{name}' (already exists).")
            continue
        post = generate_post_for_game(cand)
        if post:
            posts_added.append(post)
            existing_titles.add(post["title"].lower())
            existing_filenames.add(os.path.basename(post["url"]))
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
    if posts_added:
        for p in posts_added:
            print(" -", p["title"], "->", p["url"])

if __name__ == "__main__":
    main()
