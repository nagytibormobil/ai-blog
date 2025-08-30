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
# SETTINGS (API kulcsok beállítva az általad megadottakkal)
# ==============
OUTPUT_DIR = "generated_posts"
INDEX_FILE = "index.html"
PICTURE_DIR = "Picture"

RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"    # provided
YOUTUBE_API_KEY = "AIzaSyAXedHcSZ4zUaqSaD3MFahLz75IvSmxggM"  # provided

# Generálási beállítások
NUM_TOTAL = 12        # alapértelmezett ha futtatod --num_posts nélkül
NUM_POPULAR = 2       # hány "népszerű" (popular) legyen a futáson belül
RAWG_PAGE_SIZE = 40   # mennyi játékot kérünk le egy hívással (max 40)
USER_AGENT = "AI-Gaming-Blog-Agent/1.0"

# Ensure folders exist
Path(OUTPUT_DIR).mkdir(exist_ok=True)
Path(PICTURE_DIR).mkdir(exist_ok=True)

# ==============
# HELPERS
# ==============
def slugify(name):
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)            # remove punctuation
    s = re.sub(r"\s+", "-", s)               # spaces -> hyphens
    s = re.sub(r"-+", "-", s)                # collapse hyphens
    return s

def rawg_search_random(page=1, page_size=RAWG_PAGE_SIZE):
    """Fetch a page of RAWG games (general popular list). Returns JSON list 'results'."""
    url = "https://api.rawg.io/api/games"
    params = {
        "key": RAWG_API_KEY,
        "page": page,
        "page_size": page_size
    }
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json().get("results", [])

def rawg_get_popular(page=1, page_size=RAWG_PAGE_SIZE):
    """Fetch popular games (ordering by -added or -rating)."""
    url = "https://api.rawg.io/api/games"
    params = {"key": RAWG_API_KEY, "page": page, "page_size": page_size, "ordering": "-added"}
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json().get("results", [])

def download_image(url, dest_path):
    """Download image from URL and save to dest_path as JPG-like binary."""
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
    """Use YouTube Data API v3 to get first relevant video id for 'game_name gameplay' search."""
    if not YOUTUBE_API_KEY:
        return None
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"{game_name} gameplay",
        "type": "video",
        "maxResults": 1,
        "key": YOUTUBE_API_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        j = r.json()
        items = j.get("items", [])
        if items:
            video_id = items[0]["id"]["videoId"]
            return f"https://www.youtube.com/embed/{video_id}"
    except requests.exceptions.HTTPError as he:
        print(f"Error fetching YouTube video for {game_name}: {he}")
    except Exception as e:
        print(f"Error fetching YouTube video for {game_name}: {e}")
    # Fallback: return a generic search embed (works as redirect) or rickroll id as last resort
    return "https://www.youtube.com/embed/dQw4w9WgXcQ"

def read_index_posts():
    """Read existing POSTS array from index.html (if exists) and return list of post dicts."""
    if not os.path.exists(INDEX_FILE):
        return []
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()
    # Find the POSTS = [ ... ] block
    m = re.search(r"POSTS\s*=\s*(\[\s*[\s\S]*?\])\s*;", html)
    # Some index.html variants don't have a semicolon; try alternate
    if not m:
        m = re.search(r"POSTS\s*=\s*(\[\s*[\s\S]*?\])\s*\n", html)
    if not m:
        # fallback: try to find between our markers
        m2 = re.search(r"// <<< AUTO-GENERATED POSTS START >>>\s*const POSTS =\s*(\[\s*[\s\S]*?\])\s*;?\s*// <<< AUTO-GENERATED POSTS END >>>", html)
        if m2:
            arr_text = m2.group(1)
        else:
            return []
    else:
        arr_text = m.group(1)
    try:
        posts = json.loads(arr_text)
        return posts if isinstance(posts, list) else []
    except Exception:
        # try to fix trailing commas
        cleaned = re.sub(r",\s*}", "}", arr_text)
        cleaned = re.sub(r",\s*\]", "]", cleaned)
        try:
            return json.loads(cleaned)
        except Exception as e:
            print("Could not parse existing POSTS JSON:", e)
            return []

def write_index_posts(all_posts):
    """Replace the POSTS array in index.html with all_posts (list)."""
    if not os.path.exists(INDEX_FILE):
        print("index.html not found, skipping index update.")
        return
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # Prepare JSON string
    new_json = json.dumps(all_posts, indent=2, ensure_ascii=False)

    # Insert between markers if present
    if "// <<< AUTO-GENERATED POSTS START >>>" in html and "// <<< AUTO-GENERATED POSTS END >>>" in html:
        new_html = re.sub(
            r"// <<< AUTO-GENERATED POSTS START >>>[\s\S]*?// <<< AUTO-GENERATED POSTS END >>>",
            f"// <<< AUTO-GENERATED POSTS START >>>\n    const POSTS = {new_json};\n    // <<< AUTO-GENERATED POSTS END >>>",
            html
        )
    else:
        # Fallback replace POSTS = [...]
        new_html = re.sub(r"POSTS\s*=\s*\[[\s\S]*?\]", f"POSTS = {new_json}", html)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("✅ index.html POSTS updated.")

def build_long_review(game_name, publisher, year):
    """Return a long review text — ~25-30 short paragraphs (SEO-friendly)."""
    parts = []
    intro = (f"<p><strong>{game_name}</strong> ({year}), developed by {publisher}, "
             "is explored in depth below. This review focuses on gameplay, mechanics, graphics, "
             "and tips to help both newcomers and veterans.</p>")
    parts.append(intro)
    templates = [
        "The world design offers a blend of open exploration and carefully crafted encounters that reward curiosity.",
        "Combat systems are balanced in ways that allow for multiple playstyles; learning them increases enjoyment significantly.",
        "Visuals and art direction contribute to a distinct atmosphere, with standout set-pieces and environmental storytelling.",
        "Players will appreciate the pacing — a mixture of intense moments and quieter exploration that gives the game breathing room.",
        "Progression systems feel meaningful, with upgrades and unlocks that influence player choice.",
        "Multiplayer or community elements expand replayability and provide a broader set of challenges.",
        "AI behavior in the game is believable and presents tactical encounters with satisfying outcomes.",
        "Maps and locations are designed to encourage exploration — hidden secrets and side objectives reward attentive players.",
        "Performance and technical polish are important; this title generally performs well on modern hardware.",
        "Sound design, music and ambiance are used effectively to build immersion.",
        "Controls and responsiveness are tuned to deliver a satisfying player experience.",
        "Difficulty options are available to accommodate casual and hardcore audiences.",
        "A well-crafted tutorial and onboarding help players learn core mechanics early on.",
        "Narrative and character design provide motivation for continuing through the campaign.",
        "Mod support or creative tools (where present) add longevity to the experience.",
        "Quality-of-life features help reduce friction, making repeat sessions more enjoyable.",
        "Customization options allow players to express themselves and tweak gameplay.",
        "Community-driven content or events can boost long-term interest in the game.",
        "Achievements and in-game goals provide additional incentives to explore thoroughly.",
        "The economy or resource systems are balanced to reward strategy over grind.",
        "Boss fights or major encounters often require thoughtful preparation and adaptation.",
        "Exploration rewards and collectibles are sprinkled across the map in clever ways.",
        "Replay value is high when multiple endings, builds, or playstyles are supported.",
        "Technical updates post-launch have shown developer commitment to improving the experience.",
        "If you enjoy titles that reward curiosity and mastery, this game is likely a strong fit.",
    ]
    # choose ~25 sentences: start with intro + sample from templates repeated/varied
    parts.extend(f"<p>{templates[i % len(templates)]}</p>" for i in range(24))
    conclusion = "<p>In short: this title delivers a memorable experience for players who enjoy depth, polish, and replayability. Use the tips below to maximize your enjoyment.</p>"
    parts.append(conclusion)
    return "\n".join(parts)

def post_footer_html():
    """Return the footer HTML (affiliate + policies) identical to index footer."""
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

# ==============
# POST GENERATION
# ==============
def generate_post_for_game(game):
    """game is a RAWG result dict containing 'name', 'released', 'background_image', etc."""
    name = game.get("name") or "Unknown Game"
    slug = slugify(name)
    filename = f"{slug}.html"   # SEO-friendly filename (no timestamp)
    out_path = os.path.join(OUTPUT_DIR, filename)

    # If post already exists, skip (we do not overwrite)
    if os.path.exists(out_path):
        print(f"⚠️  Post already exists for '{name}' -> {filename} (skipping)")
        return None

    # Image download: pick background_image if available
    img_url = game.get("background_image") or game.get("background_image_additional") or ""
    img_filename = f"{slug}.jpg"
    img_path = os.path.join(PICTURE_DIR, img_filename)

    # If image file already exists, skip this game to avoid duplicates (user requested unique pics too)
    if os.path.exists(img_path):
        print(f"⚠️  Image already exists for '{name}' -> {img_filename} (skipping)")
        return None

    # Try download image
    if img_url:
        ok = download_image(img_url, img_path)
        if not ok:
            # fallback placeholder download
            ph_url = f"https://placehold.co/800x450?text={name.replace(' ', '+')}"
            download_image(ph_url, img_path)
    else:
        ph_url = f"https://placehold.co/800x450?text={name.replace(' ', '+')}"
        download_image(ph_url, img_path)

    # YouTube embed
    youtube_embed = get_youtube_embed(name)

    # long review
    year = game.get("released") or ""
    publisher = game.get("publisher") or game.get("developers", [{}])[0].get("name", "") if isinstance(game.get("developers"), list) else ""
    review_html = build_long_review(name, publisher or "the studio", year)

    # Build HTML content (keeps dark theme style but inline minimal CSS to avoid external dependencies)
    now = datetime.datetime.now()
    title = f"{name} Cheats, Tips & Full Review"
    cover_src = f"../{PICTURE_DIR}/{img_filename}"  # relative to generated_posts/
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
      <li><strong>Publisher/Developer:</strong> {publisher or '—'}</li>
      <li><strong>Platforms:</strong> {', '.join([p['platform']['name'] for p in game.get('platforms', [])]) if game.get('platforms') else '—'}</li>
    </ul>
    <h2>Full Review</h2>
    {review_html}
    <h2>Gameplay Video</h2>
    <iframe width="100%" height="400" src="{youtube_embed}" frameborder="0" allowfullscreen></iframe>
    <h2>Cheats & Tips</h2>
    <ul>
      <li>Use adaptive playstyles and experiment with builds.</li>
      <li>Explore offbeat areas for hidden rewards.</li>
      <li>Balance risk and reward when tackling optional bosses.</li>
    </ul>

    <h2 class="tiny">AI Rating</h2>
    <p class="tiny">⭐ {round(random.uniform(2.5,5.0),1)}/5</p>

    {footer_block}
  </div>
</body>
</html>
"""
    # Save post
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
    """
    Return two lists: random_candidates, popular_candidates
    We will sample from RAWG pages until we collect enough unique candidates.
    """
    random_candidates = []
    popular_candidates = []
    attempts = 0
    # popular first
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

    # then random fill (fetch a few pages and sample)
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
    # shuffle and trim
    random.shuffle(collected)
    needed = total_needed - len(popular_candidates)
    random_candidates = collected[:needed]
    return random_candidates, popular_candidates

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=NUM_TOTAL)
    args = parser.parse_args()
    total = args.num_posts

    # load existing posts from index -> to not duplicate titles/URLs
    existing_posts = read_index_posts()
    existing_titles = set(p.get("title","").lower() for p in existing_posts)
    existing_filenames = set(os.path.basename(p.get("url","")) for p in existing_posts if p.get("url"))

    # gather candidates
    random_candidates, popular_candidates = gather_candidates(total, NUM_POPULAR)
    # combine: make sure popular are included
    candidates = []
    # interleave popular for visibility: place 2 popular among the list
    candidates.extend(popular_candidates)
    candidates.extend(random_candidates)

    posts_added = []
    for cand in candidates:
        name = cand.get("name","").strip()
        if not name:
            continue
        slug = slugify(name)
        filename = f"{slug}.html"
        # skip if title exists or filename exists or picture exists
        if name.lower() in existing_titles or filename in existing_filenames or os.path.exists(os.path.join(PICTURE_DIR, f"{slug}.jpg")):
            print(f"Skipping '{name}' (already exists).")
            continue
        # attempt to generate post for this candidate
        post = generate_post_for_game(cand)
        if post:
            posts_added.append(post)
            existing_titles.add(post["title"].lower())
            existing_filenames.add(os.path.basename(post["url"]))
        # small delay to respect APIs
        time.sleep(0.7)

    # merge posts_added into existing_posts (keep existing first, then new on top)
    combined = posts_added + existing_posts
    # remove duplicates by title, keep first occurrence
    seen = set()
    unique_posts = []
    for p in combined:
        t = p.get("title","").lower()
        if t in seen:
            continue
        seen.add(t)
        unique_posts.append(p)

    # Sort by date desc (newer first) — ensure date present
    def date_key(item):
        try:
            return item.get("date","")
        except:
            return ""
    unique_posts.sort(key=lambda x: x.get("date",""), reverse=True)

    # write back to index
    write_index_posts(unique_posts)

    # Print summary
    print(f"Done. New posts added: {len(posts_added)}")
    if posts_added:
        for p in posts_added:
            print(" -", p["title"], "->", p["url"])

if __name__ == "__main__":
    main()
