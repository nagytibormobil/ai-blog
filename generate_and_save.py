#!/usr/bin/env python3
# generate_and_save.py
# Automatikus post-generálás + fájl-alapú komment moderálás és beillesztés a generált posztokba.
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

RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"  # provided
YOUTUBE_API_KEY = "AIzaSyAXedHcSZ4zUaqSaD3MFahLz75IvSmxggM"  # provided

# Komment-mappák (fájlrendszeres workflow)
PENDING_COMMENTS_DIR = "comments_pending"  # ide helyezd a beküldött komment JSON fájlokat
APPROVED_COMMENTS_DIR = os.path.join(OUTPUT_DIR, "comments")  # ide kerülnek az elfogadott kommentek, per-post json fájlok
REJECTED_COMMENTS_DIR = "comments_rejected"  # ide kerülnek az elutasított kommentek (with reason)
# Generálási beállítások
NUM_TOTAL = 12  # alapértelmezett ha futtatod --num_posts nélkül
NUM_POPULAR = 2  # hány "népszerű" (popular) legyen a futáson belül
RAWG_PAGE_SIZE = 40  # mennyi játékot kérünk le egy hívással (max 40)
USER_AGENT = "AI-Gaming-Blog-Agent/1.0"

# Biztonsági / moderációs beállítások
COMMENT_MAX_LENGTH = 200
COMMENT_MAX_PER_AUTHOR_PER_DAY = 10
# egyszerű tiltott kulcsszavak listája (bővíthető)
BANNED_KEYWORDS = [
    "http://", "https://", "www.", ".com", ".ru", ".cz", ".biz", "buy now", "click here",
    "sex", "porn", "drug", "drugs", "terror", "bomb", "kill", "war", "nazi",
    "f***", "fuck", "bitch", "asshole", "shit", "szar", "kurva", "basz", "háború"
]

PROFANITY_LIST = [
    # rövid, egyszerű magyar és angol trágár szavak (nem teljes lista - bővíthető)
    "kurva", "baszd", "basz", "fasz", "fasz", "picsa", "segg", "seggfej", "szar",
    "fuck", "shit", "bitch", "asshole"
]

# Ensure folders exist
Path(OUTPUT_DIR).mkdir(exist_ok=True)
Path(PICTURE_DIR).mkdir(exist_ok=True)
Path(PENDING_COMMENTS_DIR).mkdir(exist_ok=True)
Path(APPROVED_COMMENTS_DIR).mkdir(parents=True, exist_ok=True)
Path(REJECTED_COMMENTS_DIR).mkdir(exist_ok=True)


# ==============
# HELPERS
# ==============
def slugify(name):
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)  # remove punctuation
    s = re.sub(r"\s+", "-", s)  # spaces -> hyphens
    s = re.sub(r"-+", "-", s)  # collapse hyphens
    return s


def rawg_search_random(page=1, page_size=RAWG_PAGE_SIZE):
    """Fetch a page of RAWG games (general popular list). Returns JSON list 'results'."""
    url = "https://api.rawg.io/api/games"
    params = {"key": RAWG_API_KEY, "page": page, "page_size": page_size}
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
    """Download image from URL and save to dest_path as binary."""
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
    """Use YouTube Data API v3 to get first relevant video id for 'game_name gameplay' search."""
    if not YOUTUBE_API_KEY:
        return None
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"{game_name} gameplay",
        "type": "video",
        "maxResults": 1,
        "key": YOUTUBE_API_KEY,
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
    # Fallback: rickroll id as last resort
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
        m2 = re.search(
            r"// <<< AUTO-GENERATED POSTS START >>>\s*const POSTS =\s*(\[\s*[\s\S]*?\])\s*;?\s*// <<< AUTO-GENERATED POSTS END >>>",
            html,
        )
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
            f"// <<< AUTO-GENERATED POSTS START >>>\n const POSTS = {new_json};\n // <<< AUTO-GENERATED POSTS END >>>",
            html,
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
    intro = (
        f"<p><strong>{game_name}</strong> ({year}), developed by {publisher}, "
        "is explored in depth below. This review focuses on gameplay, mechanics, graphics, "
        "and tips to help both newcomers and veterans.</p>"
    )
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
    """Return the footer HTML (affiliate + policies) identical to index footer, expanded Comment Policy."""
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
            <li>Only plain text allowed — <strong>no images, no links, no HTML</strong>.</li>
            <li>Max 200 characters per comment.</li>
            <li>Comments containing profanity, hate speech, calls to violence, or advertising will be rejected.</li>
            <li>All comments are automatically moderated; csak az elfogadott kommentek jelennek meg.</li>
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
# COMMENT MODERATION
# ==============
def load_json_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Could not load JSON {path}: {e}")
        return None


def save_json_file(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Could not save JSON {path}: {e}")
        return False


def sanitize_comment_text(text):
    """Strip tags and reduce whitespace. Return None if text contains HTML tags."""
    if not isinstance(text, str):
        return None
    # reject if contains HTML tags
    if re.search(r"<[^>]+>", text):
        return None
    # normalize whitespace
    t = text.strip()
    t = re.sub(r"\s+", " ", t)
    return t


def contains_banned_keyword(text):
    low = text.lower()
    for k in BANNED_KEYWORDS:
        if k in low:
            return True
    for p in PROFANITY_LIST:
        if p in low:
            return True
    # basic link detection
    if re.search(r"https?://", low) or re.search(r"www\.", low) or re.search(r"\.[a-z]{2,4}", low):
        return True
    return False


def count_author_comments_today(author):
    """Count approved comments for this author today across all posts."""
    if not author:
        return 0
    today = datetime.date.today().isoformat()
    count = 0
    # iterate approved comment files
    for fn in os.listdir(APPROVED_COMMENTS_DIR):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(APPROVED_COMMENTS_DIR, fn)
        j = load_json_file(path)
        if not isinstance(j, list):
            continue
        for c in j:
            if c.get("author", "").strip().lower() == author.strip().lower():
                # expect c["date"] in ISO or with datetime; check prefix
                d = c.get("date", "")
                if d.startswith(today):
                    count += 1
    return count


def process_pending_comments():
    """Process all JSON files in PENDING_COMMENTS_DIR. Move them to approved or rejected."""
    files = [f for f in os.listdir(PENDING_COMMENTS_DIR) if f.lower().endswith(".json")]
    processed = 0
    for fn in files:
        path = os.path.join(PENDING_COMMENTS_DIR, fn)
        data = load_json_file(path)
        if not data:
            # move to rejected with reason
            reason = "Invalid JSON"
            move_to_rejected(path, fn, reason)
            continue

        # Expected fields: post_slug OR post_url OR post_title, author, text, date (optional)
        post_slug = data.get("post_slug") or data.get("slug") or ""
        post_url = data.get("post_url") or data.get("url") or ""
        post_title = data.get("post_title") or data.get("title") or ""
        author = data.get("author", "").strip() or "Anonymous"
        text = data.get("text", "") or ""
        now_iso = datetime.datetime.now().isoformat(sep=" ")
        # Basic sanitation
        text_clean = sanitize_comment_text(text)
        if text_clean is None:
            move_to_rejected(path, fn, "Contains HTML/tags or invalid characters")
            continue
        if len(text_clean) == 0:
            move_to_rejected(path, fn, "Empty comment")
            continue
        if len(text_clean) > COMMENT_MAX_LENGTH:
            move_to_rejected(path, fn, f"Too long (> {COMMENT_MAX_LENGTH} chars)")
            continue
        if contains_banned_keyword(text_clean):
            move_to_rejected(path, fn, "Contains banned words/links/ads/profanity")
            continue
        # determine slug if not set: try from post_url or title
        if not post_slug:
            if post_url:
                # attempt to extract filename
                base = os.path.basename(post_url)
                post_slug = os.path.splitext(base)[0]
            elif post_title:
                post_slug = slugify(post_title)
            else:
                # no target post/info => reject
                move_to_rejected(path, fn, "No target post (slug/url/title missing)")
                continue

        # enforce per-author per-day limit
        cnt_today = count_author_comments_today(author)
        if cnt_today >= COMMENT_MAX_PER_AUTHOR_PER_DAY:
            move_to_rejected(path, fn, "Author exceeded daily comment limit")
            continue

        # Build approved comment record
        comment_record = {
            "author": author,
            "text": text_clean,
            "date": now_iso,
        }

        # Save into APPROVED_COMMENTS_DIR per post slug
        approved_path = os.path.join(APPROVED_COMMENTS_DIR, f"{post_slug}.json")
        comments_list = []
        if os.path.exists(approved_path):
            existing = load_json_file(approved_path)
            if isinstance(existing, list):
                comments_list = existing
        comments_list.append(comment_record)
        # keep at most e.g. 500 comments per post to avoid huge files
        if len(comments_list) > 500:
            comments_list = comments_list[-500:]
        ok = save_json_file(approved_path, comments_list)
        if ok:
            # remove pending file
            try:
                os.remove(path)
            except Exception as e:
                print(f"Warning: unable to remove pending file {path}: {e}")
            processed += 1
            print(f"✅ Approved comment by '{author}' for post '{post_slug}'")
        else:
            move_to_rejected(path, fn, "Failed to save approved comment")
    if processed:
        print(f"Processed and approved {processed} pending comments.")
    else:
        print("No pending comments processed.")


def move_to_rejected(pending_path, filename, reason):
    """Move pending file to rejected folder with a reason (create metadata)."""
    try:
        with open(pending_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        content = ""
    now_iso = datetime.datetime.now().isoformat(sep=" ")
    rej = {
        "rejected_at": now_iso,
        "reason": reason,
        "original_filename": filename,
        "original_content": content,
    }
    ts = int(time.time())
    rej_fn = f"rejected_{ts}_{filename}"
    rej_path = os.path.join(REJECTED_COMMENTS_DIR, rej_fn)
    try:
        with open(rej_path, "w", encoding="utf-8") as f:
            json.dump(rej, f, ensure_ascii=False, indent=2)
        os.remove(pending_path)
    except Exception as e:
        print(f"Could not move to rejected: {e}")
    print(f"❌ Rejected comment file {filename}: {reason}")


# ==============
# POST GENERATION
# ==============
def load_approved_comments_for_slug(slug):
    """Return list of approved comments for given post slug (most recent first)."""
    path = os.path.join(APPROVED_COMMENTS_DIR, f"{slug}.json")
    if not os.path.exists(path):
        return []
    j = load_json_file(path)
    if isinstance(j, list):
        # Return reverse chronological
        return sorted(j, key=lambda x: x.get("date", ""), reverse=True)
    return []


def generate_post_for_game(game):
    """game is a RAWG result dict containing 'name', 'released', 'background_image', etc."""
    name = game.get("name") or "Unknown Game"
    slug = slugify(name)
    filename = f"{slug}.html"
    out_path = os.path.join(OUTPUT_DIR, filename)
    # If post already exists, skip (we do not overwrite) — keep behavior
    if os.path.exists(out_path):
        print(f"⚠️ Post already exists for '{name}' -> {filename} (skipping)")
        return None
    # Image download: pick background_image if available
    img_url = game.get("background_image") or game.get("background_image_additional") or ""
    img_filename = f"{slug}.jpg"
    img_path = os.path.join(PICTURE_DIR, img_filename)
    # If image file already exists, skip this game to avoid duplicates (user requested unique pics too)
    if os.path.exists(img_path):
        print(f"⚠️ Image already exists for '{name}' -> {img_filename} (skipping)")
        return None
    # Try download image if img_url:
    if img_url:
        ok = download_image(img_url, img_path)
        if not ok:
            # fallback placeholder
            ph_url = f"https://placehold.co/800x450?text={name.replace(' ', '+')}"
            download_image(ph_url, img_path)
    else:
        ph_url = f"https://placehold.co/800x450?text={name.replace(' ', '+')}"
        download_image(ph_url, img_path)
    # YouTube embed
    youtube_embed = get_youtube_embed(name)
    # long review
    year = game.get("released") or ""
    publisher = ""
    if isinstance(game.get("developers"), list) and game.get("developers"):
        publisher = game.get("developers", [{}])[0].get("name", "") or ""
    else:
        publisher = game.get("publisher") or ""
    if not publisher:
        publisher = "the studio"
    review_html = build_long_review(name, publisher, year)
    # Build HTML content (keeps dark theme style but inline minimal CSS to avoid external dependencies)
    now = datetime.datetime.now()
    title = f"{name} Cheats, Tips & Full Review"
    cover_src = f"../{PICTURE_DIR}/{img_filename}"  # relative to generated_posts/
    footer_block = post_footer_html()

    # Load approved comments for this post (will be displayed under Cheats & Tips)
    approved_comments = load_approved_comments_for_slug(slug)
    comments_html = ""
    if approved_comments:
        comments_html += '<div id="comments" style="margin-top:12px">'
        comments_html += '<h3>Comments</h3>'
        comments_html += '<ul class="comments-list">'
        # Show up to 50 recent comments to keep page light
        for c in approved_comments[:50]:
            author = c.get("author", "Anonymous")
            text = c.get("text", "")
            date = c.get("date", "")
            comments_html += f'<li><div class="comment-meta tiny">{author} — {date}</div><div class="comment-text">{text}</div></li>'
        comments_html += "</ul></div>"
    else:
        # Display comment box placeholder (submission disabled here — backend file workflow)
        comments_html += '<div id="comments" style="margin-top:12px">'
        comments_html += '<h3>Comments</h3>'
        comments_html += '<p class="tiny">Nincsenek még kommentek. Komment beküldéshez helyezz el egy JSON fájlt a <code>comments_pending/</code> mappába (a rendszer automatikusan moderálja a kommenteket).</p>'
        comments_html += "</div>"

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
    .comments-list{{list-style:none;padding:0;margin:0}}
    .comments-list li{{background:var(--card);padding:10px;border-radius:8px;margin-bottom:6px;border:1px solid var(--border)}}
    .comment-meta{{font-size:12px;color:var(--muted);margin-bottom:6px}}
    .comment-text{{font-size:15px;color:var(--text)}}
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

    <!-- Comments are displayed here under Cheats & Tips -->
    {comments_html}

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
        "platform": [p["platform"]["name"] for p in game.get("platforms", [])] if game.get("platforms") else [],
        "date": now.strftime("%Y-%m-%d"),
        "rating": round(random.uniform(2.5, 5.0), 1),
        "cover": f"{PICTURE_DIR}/{img_filename}",
        "views": 0,
        "comments": len(load_approved_comments_for_slug(slug)),
    }
    print(f"✅ Generated post: {out_path}")
    return post_dict


# ==============
# MAIN FLOW
# ==============
def gather_candidates(total_needed, num_popular):
    """ Return two lists: random_candidates, popular_candidates
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=NUM_TOTAL)
    parser.add_argument("--process_comments_only", action="store_true", help="Csak a pending kommentek feldolgozása (ne generáljon új posztokat).")
    args = parser.parse_args()
    total = args.num_posts

    # FIRST: process pending comments automatically (this implements the 'azonnali' ellenőrzést)
    print("Processing pending comments...")
    process_pending_comments()

    if args.process_comments_only:
        print("process_comments_only flag set — exiting after processing comments.")
        return

    # load existing posts from index -> to not duplicate titles/URLs
    existing_posts = read_index_posts()
    existing_titles = set(p.get("title", "").lower() for p in existing_posts)
    existing_filenames = set(os.path.basename(p.get("url", "")) for p in existing_posts if p.get("url"))

    # gather candidates
    random_candidates, popular_candidates = gather_candidates(total, NUM_POPULAR)
    # combine: make sure popular are included
    candidates = []
    candidates.extend(popular_candidates)
    candidates.extend(random_candidates)

    posts_added = []
    for cand in candidates:
        name = cand.get("name", "").strip()
        if not name:
            continue
        slug = slugify(name)
        filename = f"{slug}.html"
        # skip if already exists
        if name.lower() in existing_titles or filename in existing_filenames or os.path.exists(os.path.join(PICTURE_DIR, f"{slug}.jpg")):
            print(f"Skipping '{name}' (already exists).")
            continue
        # attempt to generate post for this candidate
        try:
            post = generate_post_for_game(cand)
            if post:
                posts_added.append(post)
                existing_titles.add(post["title"].lower())
                existing_filenames.add(os.path.basename(post["url"]))
            # small delay to respect APIs
            time.sleep(0.7)
        except Exception as e:
            print(f"Error generating post for {name}: {e}")
            continue

    # merge posts_added into existing_posts (keep existing first, then new on top)
    combined = posts_added + existing_posts
    # remove duplicates by title, keep first occurrence
    seen = set()
    unique_posts = []
    for p in combined:
        t = p.get("title", "").lower()
        if t in seen:
            continue
        seen.add(t)
        unique_posts.append(p)
    # Sort by date desc (newer first)
    unique_posts.sort(key=lambda x: x.get("date", ""), reverse=True)
    # write back to index
    write_index_posts(unique_posts)

    print(f"Done. New posts added: {len(posts_added)}")
    if posts_added:
        for p in posts_added:
            print(" -", p["title"], "->", p["url"])


if __name__ == "__main__":
    main()
