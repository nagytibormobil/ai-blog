#!/usr/bin/env python3
# app.py
# Teljes poszt-generátor + Flask komment API

import os
import random
import datetime
import json
import time
import re
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# ==============
# KONFIG
# ==============
BASE_DIR = r"C:\ai_blog"
OUTPUT_DIR = os.path.join(BASE_DIR, "generated_posts")
INDEX_FILE = os.path.join(BASE_DIR, "index.html")
PICTURE_DIR = os.path.join(BASE_DIR, "Picture")
COMMENT_DIR = os.path.join(BASE_DIR, "comments")

RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"
YOUTUBE_API_KEY = "AIzaSyAXedHcSZ4zUaqSaD3MFahLz75IvSmxggM"

NUM_TOTAL = 12
NUM_POPULAR = 2
RAWG_PAGE_SIZE = 40
USER_AGENT = "AI-Gaming-Blog-Agent/1.0"

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(PICTURE_DIR).mkdir(parents=True, exist_ok=True)
Path(COMMENT_DIR).mkdir(parents=True, exist_ok=True)

# ==============
# SEGÉDFÜGGVÉNYEK
# ==============
def slugify(name: str) -> str:
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
        if re.search(r"POSTS\s*=\s*\[[\s\S]*?\]", html):
            new_html = re.sub(r"POSTS\s*=\s*\[[\s\S]*?\]", f"POSTS = {new_json}", html)
        else:
            new_html = html + f"\n<!-- AUTO-GENERATED POSTS START -->\n<script>\nconst POSTS = {new_json};\n</script>\n<!-- AUTO-GENERATED POSTS END -->\n"
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("✅ index.html POSTS updated.")

# ======================
# Tartalom generálás
# ======================
def build_long_review(game_name, publisher, year):
    parts = []
    intro = f"<p><strong>{game_name}</strong> ({year}), developed by {publisher}, is explored in depth below. This review covers gameplay walkthroughs and tips.</p>"
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
    conclusion = "<p>Overall, this game provides a mix of exploration, strategy, and fun. Use the tips wisely to enhance your gameplay.</p>"
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
    items = "".join(f"<li>{tip}</li>" for tip in tips[:15])
    return f"<ul>{items}</ul>"

def get_age_rating(game):
    rating = game.get("esrb_rating") or game.get("age_rating") or {"name":"Not specified"}
    name = rating.get("name") if isinstance(rating, dict) else str(rating)
    return f"{name}*" if name else "Not specified*"

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
            <li>No links or images in comments.</li>
            <li>Max 15 comments/day (per post). Moderated automatically.</li>
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

# ======================
# Poszt generálás
# ======================
def generate_post_for_game(game):
    name = game.get("name") or "Unknown Game"
    slug = slugify(name)
    filename = f"{slug}.html"
    out_path = os.path.join(OUTPUT_DIR, filename)

    if os.path.exists(out_path):
        print(f"⚠️  Post already exists for '{name}' -> {filename} (skipping)")
        return None

    # Kép
    img_url = game.get("background_image") or game.get("background_image_additional") or ""
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
    else:
        print(f"ℹ️  Image already present: {img_filename}")

    youtube_embed = get_youtube_embed(name)

    year = game.get("released") or ""
    publisher = ""
    if isinstance(game.get("developers"), list) and game.get("developers"):
        publisher = game.get("developers")[0].get("name", "")
    elif isinstance(game.get("publishers"), list) and game.get("publishers"):
        publisher = game.get("publishers")[0].get("name", "")
    else:
        publisher = game.get("publisher") or ""

    review_html = build_long_review(name, publisher or "the studio", year)
    cheats_html = generate_cheats_tips(name)
    age_rating = get_age_rating(game)

    now = datetime.datetime.now()
    title = f"{name} Cheats, Tips & Full Review"
    cover_src = f"../Picture/{img_filename}"

    # Komment fájl
    comments_file = os.path.join(COMMENT_DIR, f"{slug}.json")
    if not os.path.exists(comments_file):
        with open(comments_file, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    footer_block = post_footer_html()

    # Komment UI + JS
    comments_html = f"""
    <h2>Leave a comment (will be moderated)</h2>
    <form id="commentForm">
      <input type="text" id="commentName" maxlength="12" placeholder="Your name (max 12 chars)" required style="width:100%;padding:8px;border-radius:6px;border:1px solid #ccc;box-sizing:border-box;">
      <br><br>
      <textarea id="commentText" maxlength="200" placeholder="Write your comment (max 200 chars)" required style="width:100%;height:100px;padding:8px;border-radius:6px;border:1px solid #ccc;box-sizing:border-box;"></textarea>
      <br><br>
      <button id="commentSubmit" type="submit" style="padding:8px 14px;border-radius:8px;border:0;background:#5cc8ff;color:#032">Submit</button>
    </form>
    <p class="tiny">Plain text only — no links or images. Comments are moderated and must follow the site policy.</p>
    <div id="commentsList" style="margin-top:12px"></div>

    <script>
    (function(){{
      const slug = "{slug}";
      const tryUrls = ['http://127.0.0.1:5000/api/comment'];

      async function fetchComments() {{
        try {{
          const res = await fetch('http://127.0.0.1:5000/api/comments/' + slug + '?_=' + Date.now());
          if (!res.ok) throw 'Error';
          const data = await res.json();
          renderComments(data);
        }} catch(e) {{
          renderComments([]);
        }}
      }}

      function renderComments(arr) {{
        const list = document.getElementById('commentsList');
        list.innerHTML = '';
        if (!Array.isArray(arr) || arr.length===0) {{
          list.innerHTML = '<p class="tiny">No comments yet. Be the first to comment!</p>';
          return;
        }}
        arr.forEach(c => {{
          const d = document.createElement('div');
          d.style.padding = '8px';
          d.style.borderRadius = '8px';
          d.style.border = '1px solid rgba(0,0,0,0.06)';
          d.style.marginBottom = '8px';
          const name = document.createElement('div');
          name.innerHTML = '<strong>' + escapeHtml(c.name) + '</strong> <span class="tiny" style="color:#666;font-size:12px;">' + escapeHtml(c.date) + '</span>';
          const text = document.createElement('div');
          text.style.marginTop = '6px';
          text.innerText = c.text;
          d.appendChild(name);
          d.appendChild(text);
          list.appendChild(d);
        }});
      }}

      function escapeHtml(s) {{
        if (!s) return '';
        return s.replace(/[&<>"']/g, function(m) {{ return {{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}}[m]; }});
      }}

      function clientValidate(name, text) {{
        if (!name || !text) return 'Name and comment required.';
        if (name.length>12) return 'Name too long (max 12).';
        if (text.length>200) return 'Comment too long (max 200).';
        const forbidden = /(http[s]?:\\/\\/|www\\.|\\.com|\\.net|\\.org|<|>)/i;
        if (forbidden.test(name) || forbidden.test(text)) return 'No links or HTML allowed.';
        return null;
      }}

      async function postComment(payload) {{
        try {{
          const res = await fetch(tryUrls[0], {{
            method:'POST',
            headers:{{'Content-Type':'application/json'}},
            body:JSON.stringify(payload)
          }});
          if (!res.ok) throw 'Failed';
          const rdata = await res.json();
          if (!rdata.ok) throw rdata.msg || 'Rejected';
          await fetchComments();
        }} catch(e) {{
          alert('Comment rejected: ' + (e||'Cannot reach server.'));
        }}
      }}

      document.getElementById('commentForm').addEventListener('submit', async function(ev){{
        ev.preventDefault();
        const name = document.getElementById('commentName').value.trim();
        const text = document.getElementById('commentText').value.trim();
        const err = clientValidate(name,text);
        if(err){{alert('Comment rejected: '+err);return;}}
        await postComment({{slug,name,text}});
        document.getElementById('commentForm').reset();
      }});

      fetchComments();
    }})();
    </script>
    """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>{title}</title>
      <link rel="stylesheet" href="../style.css">
    </head>
    <body>
      <h1>{title}</h1>
      <img src="{cover_src}" alt="{name}" style="max-width:100%;border-radius:12px;">
      <p><strong>Age rating:</strong> {age_rating}</p>
      <iframe width="560" height="315" src="{youtube_embed}" frameborder="0" allowfullscreen style="margin-top:12px;"></iframe>
      {review_html}
      <h2>Cheat & Tip List</h2>
      {cheats_html}
      {comments_html}
      {footer_block}
    </body>
    </html>
    """

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Generated post: {filename}")
    return {
        "title": title,
        "slug": slug,
        "filename": filename,
        "cover": f"Picture/{img_filename}",
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ======================
# Flask komment API
# ======================
app = Flask(__name__)
CORS(app)

def sanitize_comment(text):
    forbidden = ["spam", "ad", "http", "www", "<", ">", "sex", "drug", "war", "terror"]
    text_lower = text.lower()
    for w in forbidden:
        if w in text_lower:
            return False
    return True

@app.route("/api/comment", methods=["POST"])
def handle_comment():
    data = request.get_json()
    slug = data.get("slug")
    name = data.get("name", "").strip()
    text = data.get("text", "").strip()
    if not slug or not name or not text:
        return jsonify({"ok": False, "msg": "Missing data"}), 400
    if len(name) > 12 or len(text) > 200:
        return jsonify({"ok": False, "msg": "Too long"}), 400
    if not sanitize_comment(name) or not sanitize_comment(text):
        return jsonify({"ok": False, "msg": "Forbidden content"}), 400

    comments_file = os.path.join(COMMENT_DIR, f"{slug}.json")
    comments = []
    if os.path.exists(comments_file):
        with open(comments_file, "r", encoding="utf-8") as f:
            comments = json.load(f)
    if len(comments) >= 15:
        return jsonify({"ok": False, "msg": "Max comments reached"}), 400

    comment_obj = {
        "name": name,
        "text": text,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    comments.append(comment_obj)
    with open(comments_file, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True})

@app.route("/api/comments/<slug>", methods=["GET"])
def get_comments(slug):
    comments_file = os.path.join(COMMENT_DIR, f"{slug}.json")
    if os.path.exists(comments_file):
        with open(comments_file, "r", encoding="utf-8") as f:
            comments = json.load(f)
    else:
        comments = []
    return jsonify(comments)

# ======================
# Main
# ======================
def main():
    # Popular first
    posts = []
    try:
        popular_games = rawg_get_popular(page=1, page_size=NUM_POPULAR)
    except Exception as e:
        print("⚠️ Could not fetch popular games:", e)
        popular_games = []
    for g in popular_games:
        p = generate_post_for_game(g)
        if p:
            posts.append(p)
    # Random games
    total_random = NUM_TOTAL - len(posts)
    try:
        random_games = rawg_search_random(page=1, page_size=total_random*2)
    except Exception as e:
        print("⚠️ Could not fetch random games:", e)
        random_games = []
    selected_games = random.sample(random_games, min(total_random, len(random_games)))
    for g in selected_games:
        p = generate_post_for_game(g)
        if p:
            posts.append(p)

    # Update index
    all_posts = read_index_posts()
    all_posts = posts + all_posts
    all_posts.sort(key=lambda x: x["date"], reverse=True)
    write_index_posts(all_posts)
    print("✅ All posts generated and index updated.")

if __name__ == "__main__":
    main()
    app.run(debug=True, port=5000)
