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
    return "https://www.youtube.com/watch?v=p4GFQRyZpgg"

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

    paragraphs = []

    # Intro - first impressions
    paragraphs.append(
        f"When I first started playing **{name}** (Release date: {release}, developer: {developer}), "
        "it felt like I suddenly jumped into a whole new world. Right from the start it was super exciting, "
        "and I couldn’t wait to see what the game had in store for me."
    )

    # Gameplay and experiences
    paragraphs.append(
        "The gameplay kept surprising me. Sometimes everything went smoothly, but other times it was so hard "
        "that I almost wanted to rage quit. But that’s what made it fun: when I finally got through a tough part, "
        "I felt so proud of myself, like I was a real hero. "
        "The sounds, graphics, and controls were often really cool, but sometimes a bit weird too."
    )

    # Cheats / tips
    if game.get("official_cheats") and len(game["official_cheats"]) > 0:
        cheat_list = []
        for cheat in game["official_cheats"]:
            src = cheat.get('source', 'internet')
            cheat_list.append(f"- {cheat['description']} (Source: {src})")
        cheat_text = "\n".join(cheat_list)
        paragraphs.append(
            "Guess what, I even found some cheat codes online! Trying them out was hilarious:\n"
            f"{cheat_text}\n"
            "It honestly felt like I had superpowers inside the game."
        )
    else:
        paragraphs.append(
            "I tried looking for cheat codes, but sadly I couldn’t find any. "
            "It would be awesome to have one that makes me invincible, or helps me escape from enemies more easily! :)"
        )

    # Exploration and multiplayer
    paragraphs.append(
        "Exploring the maps was always fun: hidden spots, surprises, and lots of funny moments. "
        "But the best part was when I played multiplayer with my friends. Sometimes we messed up and laughed like crazy, "
        "other times we played like a real team, and in those moments I honestly felt like we were the best players in the world!"
    )

    # Negatives (kid-style honesty)
    paragraphs.append(
        "Of course, not everything was perfect. Sometimes the graphics looked a little blurry, or the maps felt repetitive and boring. "
        "Other times the sound effects didn’t feel real, more like plastic. These things bugged me a bit, "
        "but they never stopped me from playing, because I was always excited to see what would happen next."
    )

    # Closing
    paragraphs.append(
        f"Overall, I think **{name}** is a super cool game! "
        "Whether I played alone or with friends, it always stayed exciting. "
        "I’m definitely going to play it again, because it just gave me too many awesome memories."
    )

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
    :root{{--bg:#0b0f14;--panel:#121821;--muted:#9fb0c3;--text:#eaf1f8;--accent:#5cc8ff;--card:#0f141c;--border:#1f2a38}}
    html,body{{margin:0;padding:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,Segoe UI,Roboto,Inter,Arial,sans-serif;font-size:18px}}
    .wrap{{max-width:900px;margin:24px auto;padding:18px;background:var(--panel);border-radius:12px;border:1px solid var(--border)}}
    img.cover{{width:100%;height:auto;border-radius:8px;display:block}}
    h1{{margin:10px 0 6px;font-size:28px}}
    h2{{margin-top:18px}}
    p{{color:var(--text);line-height:1.6}}
    .tiny{{color:var(--muted);font-size:13px}}
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
    {review_html}
    <h2>Gameplay Video</h2>
    <iframe width="100%" height="400" src="{youtube_embed}" frameborder="0" allowfullscreen></iframe>
    <!-- More to Explore -->
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
