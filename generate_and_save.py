#!/usr/bin/env python3
# generate_and_save.py
# Automatikus post-generálás: RAWG -> kép letöltés, YouTube embed, hosszú review, index frissítés.
# Kiterjesztés: fájl-alapú komment rendszer + beépített (kicsi) local HTTP endpoint a kommentek beküldéséhez.
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
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse, unquote_plus

# ==============
# SETTINGS (API kulcsok beállítva)
# ==============
OUTPUT_DIR = "generated_posts"
INDEX_FILE = "index.html"
PICTURE_DIR = "Picture"

# LOCAL ABSOLUTE COMMENTS DIR as requested
COMMENTS_DIR = r"C:\ai_blog\comments"

RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"
YOUTUBE_API_KEY = "AIzaSyAXedHcSZ4zUaqSaD3MFahLz75IvSmxggM"

NUM_TOTAL = 12
NUM_POPULAR = 2
RAWG_PAGE_SIZE = 40
USER_AGENT = "AI-Gaming-Blog-Agent/1.0"

# constraints from your specification
MAX_NAME_LENGTH = 12      # you had two values (10 and 12); using 12 (later point)
MAX_COMMENT_LENGTH = 200
DAILY_COMMENT_LIMIT = 15  # maximum new comments per day (global)

Path(OUTPUT_DIR).mkdir(exist_ok=True)
Path(PICTURE_DIR).mkdir(exist_ok=True)
Path(COMMENTS_DIR).mkdir(parents=True, exist_ok=True)

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
# COMMENTS / MODERATION
# ==============
# Moderation patterns and helper functions based on your rules:
BANNED_PATTERNS = [
    # sample profanity / offensive tokens (extend as needed)
    r"\b(fuck|shit|bitch|asshole|cunt|motherfucker)\b",
    # adult/drugs/war/terror topics (keywords)
    r"\b(sex|porn|xxx|nude|drugs|cocaine|heroin|meth|war|terror|bomb|kill\b|rape)\b",
    # obvious spam/ad words:
    r"\b(buy now|free money|earn money|visit my|subscribe|click here)\b"
]
BANNED_RE = re.compile("|".join(BANNED_PATTERNS), flags=re.IGNORECASE)

URL_RE = re.compile(r"https?://|www\.|[\w-]+\.(com|net|io|org|ru|xyz|info|biz)\b", flags=re.IGNORECASE)
HTML_TAG_RE = re.compile(r"<[^>]+>")
IMG_DATA_RE = re.compile(r"data:image|<img|iframe|<video", flags=re.IGNORECASE)

def load_comments_file(slug):
    path = os.path.join(COMMENTS_DIR, f"{slug}.json")
    if not os.path.exists(path):
        return {"post": "", "slug": slug, "comments": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"post": "", "slug": slug, "comments": []}

def save_comments_file(slug, post_name, comments_list):
    path = os.path.join(COMMENTS_DIR, f"{slug}.json")
    data = {"post": post_name, "slug": slug, "comments": comments_list}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path

def moderate_text(text):
    """Return (allowed(bool), reason_or_clean_text)."""
    if not isinstance(text, str):
        return False, "Invalid text"
    # remove leading/trailing whitespace
    s = text.strip()
    if not s:
        return False, "Empty"
    # block HTML tags
    if HTML_TAG_RE.search(s):
        return False, "HTML tags not allowed"
    # block images / video
    if IMG_DATA_RE.search(s):
        return False, "Images or video not allowed"
    # block URLs
    if URL_RE.search(s):
        return False, "Links are not allowed"
    # block banned words
    if BANNED_RE.search(s):
        return False, "Contains prohibited words/topics"
    # final safety: collapse excessive whitespace and return
    s = re.sub(r"\s+", " ", s)
    return True, s

def todays_comment_count():
    """Count how many comments exist today across all comment files."""
    total = 0
    today = datetime.date.today().isoformat()
    for fname in os.listdir(COMMENTS_DIR):
        if not fname.lower().endswith(".json"):
            continue
        try:
            with open(os.path.join(COMMENTS_DIR, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
            for c in data.get("comments", []):
                dt = c.get("datetime", "")
                # expected ISO format: YYYY-MM-DDTHH:MM:SS
                if dt.startswith(today):
                    total += 1
        except Exception:
            continue
    return total

# ==============
# POST GENERATION
# ==============
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
            <li>No links or images — plain text only.</li>
            <li>Max 12 characters for name, max 200 characters for comment.</li>
            <li>Max 15 new comments/day total (site-wide).</li>
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
        print(f"⚠️  Image already exists for '{name}' -> {img_filename} (skipping image download)")
    else:
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

    # generate HTML including comment form and script to load comments from ../comments/<slug>.json
    # The form posts to http://localhost:8000/comment by default (local server implemented below).
    # On static hosting (e.g. GitHub Pages) the POST endpoint won't exist, but the comments.json can be uploaded/managed via your laptop workflow.
    comment_json_path = f"../comments/{slug}.json"

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
    /* Comment form styling per your requirements */
    .comment-section{{margin-top:18px}}
    .comment-box{{width:100%;padding:10px;border-radius:8px;border:1px solid var(--border);background:transparent;color:var(--text);resize:vertical;min-height:80px;box-sizing:border-box}}
    .name-input{{width:220px;padding:8px;border-radius:6px;border:1px solid var(--border);background:transparent;color:var(--text);box-sizing:border-box}}
    .comment-submit{{margin-top:8px;padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:transparent;color:var(--text);cursor:pointer}}
    .comment-list{{margin-top:12px;}}
    .comment-item{{padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,0.03);margin-bottom:8px;background:rgba(255,255,255,0.01)}}
    .comment-meta{{font-size:12px;color:var(--muted)}}
    .error{{color:#ff6b6b}}
    .success{{color:#6bff9a}}
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

    <!-- COMMENT SECTION (always visible, even if no comments yet) -->
    <div class="comment-section" id="comments-root">
      <div><strong>Leave a comment (will be moderated)</strong></div>
      <div style="margin-top:8px">
        <input id="comment-name" class="name-input" maxlength="{MAX_NAME_LENGTH}" placeholder="Your name (max {MAX_NAME_LENGTH} chars)"/>
      </div>
      <div style="margin-top:8px">
        <textarea id="comment-text" class="comment-box" maxlength="{MAX_COMMENT_LENGTH}" placeholder="Write your comment (max {MAX_COMMENT_LENGTH} chars)"></textarea>
      </div>
      <div style="margin-top:6px; font-size:13px; color:var(--muted)">Plain text only — no links or images. Comments are moderated and must follow the site policy.</div>
      <div style="margin-top:8px">
        <button id="comment-submit" class="comment-submit">Post comment</button>
        <span id="comment-feedback" style="margin-left:12px"></span>
      </div>

      <div class="comment-list" id="comment-list">
        <!-- comments loaded here -->
      </div>
    </div>

    {footer_block}
  </div>

<script>
const SLUG = "{slug}";
const COMMENT_JSON = "{comment_json_path}";
const MAX_NAME_LEN = {MAX_NAME_LENGTH};
const MAX_COMMENT_LEN = {MAX_COMMENT_LENGTH};
const POST_ENDPOINT = "http://localhost:8000/comment"; // local endpoint (optional). If you host only static files, you'll need a server to accept POSTs.

function escapeHtml(s){ return s.replace(/[&<>"']/g, function(m){ return ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[m]; }); }

async function loadComments(){
  try{
    const res = await fetch(COMMENT_JSON + "?_=" + Date.now());
    if(!res.ok) throw new Error("No comments file");
    const data = await res.json();
    const list = data.comments || [];
    const container = document.getElementById("comment-list");
    container.innerHTML = "";
    if(list.length === 0){
      container.innerHTML = "<div class='tiny' style='color:var(--muted)'>No comments yet — be the first to comment.</div>";
      return;
    }
    list.forEach(c=>{
      const d = document.createElement("div");
      d.className = "comment-item";
      d.innerHTML = "<div style='font-weight:600;'>"+escapeHtml(c.name || "Anonymous")+"</div>"
                  + "<div style='margin-top:6px;'>"+escapeHtml(c.text)+"</div>"
                  + "<div class='comment-meta' style='margin-top:8px;'>"+escapeHtml(c.datetime || "")+"</div>";
      container.appendChild(d);
    });
  }catch(err){
    // no comments yet
    const container = document.getElementById("comment-list");
    container.innerHTML = "<div class='tiny' style='color:var(--muted)'>No comments yet — be the first to comment.</div>";
  }
}

function showFeedback(msg, ok){
  const el = document.getElementById("comment-feedback");
  el.textContent = msg;
  el.className = ok ? "success" : "error";
  setTimeout(()=>{ el.textContent = ""; el.className = ""; }, 5000);
}

async function submitComment(){
  const name = document.getElementById("comment-name").value.trim();
  const text = document.getElementById("comment-text").value.trim();
  if(name.length === 0 || text.length === 0){
    showFeedback("Name and comment required.", false); return;
  }
  if(name.length > MAX_NAME_LEN){ showFeedback("Name too long.", false); return; }
  if(text.length > MAX_COMMENT_LEN){ showFeedback("Comment too long.", false); return; }
  // basic client-side validations per rules
  const badRe = /https?:\\/\\/|www\\.|\\<img|<video|<iframe|<\\/?[a-z][\\s\\S]*>/i;
  if(badRe.test(text) || badRe.test(name)){
    showFeedback("Links, images or HTML are not allowed.", false); return;
  }
  // post to local endpoint
  try{
    const payload = {
      slug: SLUG,
      post: "{name}",
      name: name,
      text: text
    };
    const res = await fetch(POST_ENDPOINT, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
    if(!res.ok){
      const txt = await res.text();
      throw new Error(txt || "Server error");
    }
    const j = await res.json();
    if(j.ok){
      showFeedback("Comment submitted and approved.", true);
      // reload comments from JSON file (assuming server wrote it and you upload it)
      setTimeout(loadComments, 400);
      document.getElementById("comment-text").value = "";
      return;
    } else {
      showFeedback(j.error || "Rejected by moderation.", false);
      return;
    }
  }catch(err){
    // fallback: cannot contact local server — tell user to run the local comments server or upload comments manually
    showFeedback("Could not submit: local comment server not running. Run the local server on your laptop or manage comments via C:\\\\ai_blog\\\\comments.", false);
    console.warn(err);
  }
}

document.getElementById("comment-submit").addEventListener("click", submitComment);
window.addEventListener("load", loadComments);
</script>

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
# SIMPLE LOCAL COMMENT SERVER (no external deps)
# ==============
# This small server accepts POST /comment with JSON body {slug, post, name, text}
# It applies moderation rules, daily limit, and writes to C:\ai_blog\comments\<slug>.json
# To run it: python generate_and_save.py --serve
class CommentHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/comment":
            self._set_headers(404)
            self.wfile.write(json.dumps({"ok": False, "error": "Not found"}).encode("utf-8"))
            return
        length = int(self.headers.get('content-length', 0))
        raw = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(raw)
        except Exception:
            # maybe form-encoded?
            data = parse_qs(raw)
            # convert bytes + lists to strings
            for k in data:
                data[k] = data[k][0] if isinstance(data[k], list) and data[k] else data[k]
        slug = data.get("slug", "").strip()
        post_name = data.get("post", "").strip()
        name = data.get("name", "").strip()
        text = data.get("text", "").strip()

        # basic validation
        if not slug or not text:
            self._set_headers(400)
            self.wfile.write(json.dumps({"ok": False, "error": "Missing slug or text"}).encode("utf-8"))
            return

        if len(name) == 0:
            name = "Anonymous"
        if len(name) > MAX_NAME_LENGTH:
            self._set_headers(400)
            self.wfile.write(json.dumps({"ok": False, "error": f"Name too long (max {MAX_NAME_LENGTH})"}).encode("utf-8"))
            return
        if len(text) > MAX_COMMENT_LENGTH:
            self._set_headers(400)
            self.wfile.write(json.dumps({"ok": False, "error": f"Comment too long (max {MAX_COMMENT_LENGTH})"}).encode("utf-8"))
            return

        # moderate
        ok_name, cleaned_name_or_reason = moderate_text(name)
        if not ok_name:
            self._set_headers(400)
            self.wfile.write(json.dumps({"ok": False, "error": "Name rejected: " + cleaned_name_or_reason}).encode("utf-8"))
            return
        ok_text, cleaned_text_or_reason = moderate_text(text)
        if not ok_text:
            self._set_headers(400)
            self.wfile.write(json.dumps({"ok": False, "error": "Comment rejected: " + cleaned_text_or_reason}).encode("utf-8"))
            return

        # daily limit check
        today_count = todays_comment_count()
        if today_count >= DAILY_COMMENT_LIMIT:
            self._set_headers(429)
            self.wfile.write(json.dumps({"ok": False, "error": "Daily comment limit reached."}).encode("utf-8"))
            return

        # load existing comments for this slug
        data_obj = load_comments_file(slug)
        comments_list = data_obj.get("comments", [])
        # append new comment (moderated automatically)
        now = datetime.datetime.now().replace(microsecond=0)
        new_comment = {"name": cleaned_name_or_reason, "text": cleaned_text_or_reason, "datetime": now.isoformat()}
        comments_list.append(new_comment)
        # save (overwrite same file each time)
        save_comments_file(slug, post_name or data_obj.get("post", slug), comments_list)

        self._set_headers(200)
        self.wfile.write(json.dumps({"ok": True, "message": "Comment saved"}).encode("utf-8"))

def run_comment_server(host="127.0.0.1", port=8000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, CommentHandler)
    print(f"✅ Comment server running at http://{host}:{port}/comment — POST JSON {{slug,post,name,text}}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down comment server...")
        httpd.server_close()

# ==============
# CANDIDATE GATHER / MAIN
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=NUM_TOTAL)
    parser.add_argument("--serve", action="store_true", help="Run local comment server at 127.0.0.1:8000")
    args = parser.parse_args()
    if args.serve:
        # run only the comment server (useful for local testing / allowing visitors to post)
        run_comment_server()
        return

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
