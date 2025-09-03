#!/usr/bin/env python3
import os
import random
import argparse
import datetime
import json
import time
import re
from pathlib import Path
import requests

OUTPUT_DIR = "generated_posts"
INDEX_FILE = "index.html"
PICTURE_DIR = "Picture"
RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"
YOUTUBE_API_KEY = "AIzaSyAXedHcSZ4zUaqSaD3MFahLz75IvSmxggM"
USER_AGENT = "AI-Gaming-Blog-Agent/1.0"
NUM_TOTAL = 12
NUM_POPULAR = 2
RAWG_PAGE_SIZE = 40

Path(OUTPUT_DIR).mkdir(exist_ok=True)
Path(PICTURE_DIR).mkdir(exist_ok=True)

def slugify(name):
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s

def rawg_search_random(page=1, page_size=RAWG_PAGE_SIZE):
    url = "https://api.rawg.io/api/games"
    params = {"key": RAWG_API_KEY,"page": page,"page_size": page_size}
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
    params = {"part": "snippet","q": f"{game_name} gameplay","type": "video","maxResults": 1,"key": YOUTUBE_API_KEY}
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        j = r.json()
        items = j.get("items", [])
        if items:
            return f"<https://www.youtube.com/embed/{items>[0]['id']['videoId']}"
    except Exception:
        pass
    return "https://www.youtube.com/embed/dQw4w9WgXcQ"

def read_index_posts():
    if not os.path.exists(INDEX_FILE):
        return []
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"POSTS\s*=\s*(\[\s*[\s\S]*?\])\s*;", html)
    if not m:
        m = re.search(r"POSTS\s*=\s*(\[\s*[\s\S]*?\])\s*\n", html)
    if not m:
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
        cleaned = re.sub(r",\s*}", "}", arr_text)
        cleaned = re.sub(r",\s*\]", "]", cleaned)
        try:
            return json.loads(cleaned)
        except Exception:
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

def build_long_review(game_name, publisher, year):
    if game_name.lower() == "half-life 2: episode two":
        return """
        <p><strong>Half-Life 2: Episode Two</strong> continues the story after Episode One. Adventure with Gordon Freeman and Alyx Vance as they face new threats.</p>
        <p>The game blends exploration, tactical combat, and a gripping narrative to deliver an immersive experience.</p>
        <p>Graphics and AI are improved, offering fresh challenges to players.</p>
        """
    else:
        parts = []
        intro = (f"<p><strong>{game_name}</strong> ({year}), developed by {publisher}, is explored below focusing on gameplay, mechanics, and tips for all players.</p>")
        parts.append(intro)
        templates = [
            "The world design rewards exploration and curiosity.",
            "Combat systems support multiple playstyles.",
            "Visuals contribute to a distinct atmosphere.",
            "Pacing balances intense moments and exploration.",
            "Progression feels meaningful.",
            "Multiplayer expands replayability.",
            "AI behavior creates tactical combat.",
            "Maps encourage discovering secrets.",
            "Performance is generally good on modern hardware.",
            "Sound and ambiance enhance immersion."
        ]
        parts.extend(f"<p>{templates[i % len(templates)]}</p>" for i in range(10))
        conclusion = "<p>In short: this game offers a memorable experience with depth and polish. Use the tips below.</p>"
        parts.append(conclusion)
        return "\n".join(parts)

def get_age_rating(game):
    if "esrb_rating" in game and game["esrb_rating"]:
        return game["esrb_rating"].get("name")
    elif "age_rating" in game and game["age_rating"]:
        return game["age_rating"].get("name")
    return "N/A"

def get_cheats_and_tips(game_name):
    if "half-life 2" in game_name.lower():
        return [
            "Enable cheats: type sv_cheats 1 in console.",
            "Use 'noclip' to fly freely.",
            "Press F5 + H for multiple weapons."
        ]
    return [
        "Experiment with different playstyles.",
        "Explore all areas for hidden rewards.",
        "Prepare well for bosses."
    ]

def generate_title_and_description(game_name, year):
    title = f"{game_name} Review, Cheats & Tips - AI Gaming Blog"
    description = (f"Discover review, cheats, tips for {game_name} ({year}). Master the game with expert insights.")
    return title, description

def post_footer_html():
    year_now = datetime.datetime.now().year
    return f"""
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
    <section class="paypal-support" style="margin-top: 20px; padding: 10px; border: 2px solid #0070ba; border-radius: 8px; background:#f0f8ff; color:#003087; text-align:center;">
      <p><strong>Support the website with PayPal, even regularly!</strong><br>
      Every month, supporters have a chance to win a gift.</p>
      <a href="https://www.paypal.me/nagytibormobil" target="_blank" style="
        display: inline-block;
        padding: 10px 20px;
        background-color: #0070ba;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        text-decoration: none;
      ">Donate via PayPal</a>
    </section>
    <section class="download-links" style="margin-top: 20px; padding: 10px; border: 1px solid #4CAF50; border-radius: 8px; background:#e8f5e9; color:#2e7d32;">
      <h3>Download the Game</h3>
      <p>Choose from the following options:</p>
      <a href="https://affiliate-link1.com" target="_blank" style="margin-right: 10px; background-color:#4CAF50; color:white; padding:8px 15px; border-radius:5px; text-decoration:none;">Download Option 1</a>
      <a href="https://affiliate-link2.com" target="_blank" style="background-color:#388E3C; color:white; padding:8px 15px; border-radius:5px; text-decoration:none;">Download Option 2</a>
    </section>
    <section class="footer">
      <div class="row">
        <div>
          <strong>Comment Policy</strong>
          <ul class="list tiny" style="color:#666;">
            <li>No spam, ads, or offensive content.</li>
            <li>No adult/drugs/war/terror topics.</li>
            <li>Max 10 comments/day per person.</li>
            <li>Be respectful. We moderate strictly.</li>
          </ul>
        </div>
        <div>
          <strong>Terms</strong>
          <p class="tiny" style="color:#666;">All content is for informational/entertainment purposes only. Trademarks belong to their respective owners. Affiliate links may generate commissions.</p>
        </div>
      </div>
      <p class="tiny" style="color:#666;">© {year_now} AI Gaming Blog</p>
    </section>
    """

def generate_comment_section_html():
    return """
    <section id="comments-section" style="margin-top: 40px; border-top: 2px solid #0366d6; padding-top: 20px;">
      <h2>Comments</h2>
      <form id="commentForm" style="margin-bottom: 15px;">
        <textarea id="commentText" rows="4" style="width:100%; font-size: 1rem; padding: 8px; border: 1px solid #ccc; border-radius: 6px;" placeholder="Write your comment here (text only)..."></textarea>
        <br/>
        <button type="submit" style="margin-top: 8px; padding: 8px 15px; background-color: #0366d6; color: white; border: none; border-radius: 6px; cursor: pointer;">Post Comment</button>
      </form>
      <div id="commentsList" style="max-height: 300px; overflow-y: auto; border-top: 1px solid #ccc; padding-top: 10px;"></div>
      <p style="font-size: 0.85rem; color: #555; margin-top: 10px;">
        Comment Policy: No spam, ads, offensive content, adult/drugs/war/terror topics. Max 10 comments/day per person. Please be respectful. Only game-related comments allowed.
      </p>
    </section>
    <script>
      (function() {
        const forbiddenWords = ['spam', 'ads', 'advertisement', 'sex', 'adult', 'drugs', 'war', 'terror', 'offensive', 'racist', 'hate', 'kill', 'bomb', 'attack', 'porn'];
        const maxCommentsPerDay = 10;
        const storageKey = window.location.pathname + '-comments';

        function containsForbidden(text) {
          const lowered = text.toLowerCase();
          return forbiddenWords.some(word => lowered.includes(word));
        }

        function loadComments() {
          const saved = localStorage.getItem(storageKey);
          return saved ? JSON.parse(saved) : [];
        }

        function saveComments(comments) {
          localStorage.setItem(storageKey, JSON.stringify(comments));
        }

        function countTodayComments() {
          const comments = loadComments();
          const today = new Date().toDateString();
          return comments.filter(c => c.date === today).length;
        }

        function addComment(text) {
          const comments = loadComments();
          comments.push({ text, date: new Date().toDateString() });
          saveComments(comments);
        }

        function renderComments() {
          const comments = loadComments();
          const container = document.getElementById('commentsList');
          container.innerHTML = '';
          if (comments.length === 0) {
            container.innerHTML = '<p>No comments yet. Be the first to comment!</p>';
            return;
          }
          comments.slice(-50).reverse().forEach(c => {
            const div = document.createElement('div');
            div.style.borderBottom = '1px solid #ddd';
            div.style.padding = '8px 0';
            div.style.whiteSpace = 'pre-wrap';
            div.textContent = c.text;
            container.appendChild(div);
          });
        }

        const form = document.getElementById('commentForm');
        const textarea = document.getElementById('commentText');

        form.addEventListener('submit', e => {
          e.preventDefault();
          const text = textarea.value.trim();
          if (!text) {
            alert('Please write a comment before submitting.');
            return;
          }
          if (containsForbidden(text)) {
            alert('Your comment contains forbidden content. Please revise it.');
            return;
          }
          if (countTodayComments() >= maxCommentsPerDay) {
            alert('You have reached the maximum number of comments allowed per day.');
            return;
          }
          addComment(text);
          textarea.value = '';
          renderComments();
          alert('Thank you for your comment! It is now visible below.');
        });

        renderComments();
      })();
    </script>
    """

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
    publisher = game.get("publisher") or (game.get("developers", [{}])[0].get("name", "") if isinstance(game.get("developers"), list) else "")
    age_rating = get_age_rating(game)
    review_html = build_long_review(name, publisher or "the studio", year)
    cheats = get_cheats_and_tips(name)
    cheats_html = "\n".join(f"<li>{c}</li>" for c in cheats)
    title, description = generate_title_and_description(name, year)
    cover_src = f"../{PICTURE_DIR}/{img_filename}"
    footer_block = post_footer_html()
    comment_section = generate_comment_section_html()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{title}</title>
  <meta name="description" content="{description}"/>
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
      <li><strong>Age Rating:</strong> {age_rating}</li>
      <li><strong>Publisher/Developer:</strong> {publisher or '—'}</li>
      <li><strong>Platforms:</strong> {', '.join([p['platform']['name'] for p in game.get('platforms', [])]) if game.get('platforms') else '—'}</li>
    </ul>
    <h2>Full Review</h2>
    {review_html}
    <h2>Gameplay Video</h2>
    <iframe width="100%" height="400" src="{youtube_embed}" frameborder="0" allowfullscreen></iframe>
    <h2>Cheats & Tips</h2>
    <ul>
    {cheats_html}
    </ul>
    {footer_block}
    {comment_section}
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
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "rating": round(random.uniform(2.5,5.0),1),
        "cover": f"{PICTURE_DIR}/{img_filename}",
        "views": 0,
        "comments": 0
    }
    print(f"✅ Generated post: {out_path}")
    return post_dict

def generate_index_html(posts):
    now = datetime.datetime.now()
    year = now.year
    posts_html = ""
    for post in posts[:8]:
        posts_html += f"""
        <article style="border-bottom:1px solid #ccc; padding:15px 0;">
          <a href="{post['url']}" style="text-decoration:none; color:#0366d6;">
            <img src="{post['cover']}" alt="{post['title']} cover" style="width:150px; height:auto; float:left; margin-right:15px; border-radius:6px;"/>
            <h3 style="margin:0 0 5px 0;">{post['title']}</h3>
            <small style="color:#555;">{post.get('date', '')}</small>
          </a>
          <div style="clear:both;"></div>
        </article>
        """
    popular_html = ""
    popular_posts = sorted(posts, key=lambda p: p.get('views',0)+p.get('comments',0), reverse=True)[:3]
    for pop in popular_posts:
        popular_html += f"""
        <div style="margin-bottom:15px;">
          <a href="{pop['url']}" style="text-decoration:none; color:#0366d6;">
            <h4 style="margin-bottom:5px;">{pop['title']}</h4>
            <img src="{pop['cover']}" alt="{pop['title']} cover" style="width:100%; border-radius:6px;"/>
          </a>
        </div>
        """
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AI Gaming Blog - Latest Game Reviews, Cheats & Tips</title>
<meta name="description" content="Latest game reviews, cheats, tips and guides to enhance your gaming experience. Discover new games and master them with expert help." />
<style>
  body {{
    font-family: system-ui, -apple-system, Segoe UI, Roboto, Inter, Arial, sans-serif;
    margin:0; padding:0;
    background-color:#f9f9f9;
    color:#222;
  }}
  .container {{
    max-width: 1000px;
    margin: 20px auto;
    padding: 0 15px;
  }}
  header {{
    border-bottom: 2px solid #0366d6;
    padding-bottom: 16px;
    margin-bottom: 20px;
  }}
  h1 {{
    margin: 0;
    font-weight: 700;
    font-size: 2.2rem;
    color: #0366d6;
  }}
  nav a {{
    margin-right: 20px;
    text-decoration: none;
    color: #555;
    font-weight: 600;
  }}
  nav a:hover {{
    color: #0366d6;
  }}
  #search-form {{
    margin-bottom: 30px;
  }}
  #search-input {{
    width: 100%;
    padding: 10px 15px;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 8px;
  }}
  section#latest-posts article:hover {{
    background-color: #e8f5ff;
  }}
  section#latest-posts article img {{
    max-width: 150px;
  }}
  h2 {{
    border-bottom: 1px solid #0366d6;
    color: #0366d6;
    padding-bottom: 6px;
    margin-bottom: 15px;
  }}
  section#popular-posts div:hover {{
    background-color: #e0f0ff;
  }}
  section#ad-section {{
    background: #e1f0ff;
    border-radius: 10px;
    padding: 15px;
    margin: 30px 0;
    text-align: center;
  }}
  section#ad-section a {{
    text-decoration: none;
    color: white;
    background-color: #0366d6;
    padding: 10px 25px;
    border-radius: 8px;
    font-weight: 600;
  }}
  footer {{
    border-top: 1px solid #ccc;
    margin-top: 40px;
    padding: 15px 0;
    font-size: 0.85rem;
    color: #666;
    text-align: center;
  }}
</style>
</head>
<body>
  <div class="container">
    <header>
      <h1>AI Gaming Blog</h1>
      <nav>
        <a href="index.html">Home</a>
        <a href="#">Blog</a>
        <a href="#">About</a>
        <a href="#">Contact</a>
      </nav>
    </header>
    <section id="search-form">
      <input id="search-input" type="search" placeholder="Search games or posts..." aria-label="Search games or posts" />
    </section>
    <section id="latest-posts">
      <h2>Latest Posts</h2>
      {posts_html}
    </section>
    <section id="popular-posts">
      <h2>Top 3 Popular</h2>
      {popular_html}
    </section>
    <section id="ad-section">
      <h3>Earn Real Money While You Play 📱</h3>
      <p>Simple passive income by sharing a bit of your internet. Runs in the background while you game.</p>
      <a href="https://r.honeygain.me/NAGYT86DD6" target="_blank">Try Honeygain now</a>
    </section>
    <footer>
      &copy; {year} AI Gaming Blog
    </footer>
  </div>
  <script>
    const searchInput = document.getElementById('search-input');
    const posts = document.querySelectorAll('#latest-posts article');
    searchInput.addEventListener('input', e => {{
      const val = e.target.value.toLowerCase();
      posts.forEach(post => {{
        const text = post.innerText.toLowerCase();
        post.style.display = text.includes(val) ? '' : 'none';
      }});
    }});
  </script>
</body>
</html>
"""
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ {INDEX_FILE} generated.")

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
    generate_index_html(unique_posts)
    print(f"Done. New posts added: {len(posts_added)}")
    if posts_added:
        for p in posts_added:
            print(" -", p["title"], "->", p["url"])

if __name__ == "__main__":
    main()
