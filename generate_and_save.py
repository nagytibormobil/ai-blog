import os
import json
import random
import datetime
import requests
from pathlib import Path
from slugify import slugify  # pip install python-slugify

# Konfiguráció
BLOG_DIR = Path("C:/ai_blog")
POST_DIR = BLOG_DIR / "generated_posts"
PIC_DIR = BLOG_DIR / "Picture"
INDEX_FILE = BLOG_DIR / "index.html"
RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"
MAX_TIPS = 15

# Példa játék lista (később akár RAWG API-val is bővíthető)
GAMES = [
    {"title":"GTA V","platform":["PC","PS","Xbox"]},
    {"title":"FIFA 23","platform":["PC","PS","Xbox"]},
    {"title":"The Witcher 3 Wild Hunt","platform":["PC","PS","Xbox","Switch"]},
    {"title":"Minecraft","platform":["PC","Mobile","Xbox","PS"]},
    {"title":"Fortnite","platform":["PC","PS","Xbox","Mobile"]},
]

POST_DIR.mkdir(exist_ok=True)
PIC_DIR.mkdir(exist_ok=True)

# Betöltött postok, hogy ne generáljon duplikált fájlokat
existing_posts = {f.stem for f in POST_DIR.glob("*.html")}

def fetch_image(game_title):
    # RAWG API lekérés a játék képre
    url = f"https://api.rawg.io/api/games?search={game_title}&key={RAWG_API_KEY}"
    resp = requests.get(url).json()
    results = resp.get("results", [])
    if results:
        img_url = results[0].get("background_image")
        if img_url:
            ext = img_url.split(".")[-1].split("?")[0]
            filename = slugify(game_title) + "." + ext
            path = PIC_DIR / filename
            r = requests.get(img_url)
            with open(path, "wb") as f:
                f.write(r.content)
            return filename
    # Ha nincs kép, placeholder
    return None

def generate_post(game):
    slug = slugify(game["title"])
    if slug in existing_posts:
        print(f"Skipping '{game['title']}' (already exists).")
        return None

    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    rating = round(random.uniform(3.0, 5.0), 1)
    tips = [f"Tip {i+1} for {game['title']}" for i in range(random.randint(3, MAX_TIPS))]

    # Kép letöltése
    img_file = fetch_image(game["title"])
    if not img_file:
        img_file = "placeholder.jpg"

    post_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{game['title']} – AI Gaming Blog</title>
<meta name="description" content="{game['title']} review, cheats, tips, gameplay insights.">
<meta name="robots" content="index,follow">
<style>
body{{margin:0;padding:0;background:#0b0f14;color:#eaf1f8;font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif;}}
a{{color:#5cc8ff;text-decoration:none;}}
a:hover{{text-decoration:underline;}}
header,.content,.footer{{max-width:900px;margin:0 auto;padding:16px;}}
header a.btn{{display:inline-block;padding:6px 12px;background:#121821;border-radius:8px;border:1px solid #1f2a38;}}
.thumb img{{width:100%;height:auto;border-radius:10px;}}
.section{{margin-top:24px;}}
.badge{{background:rgba(92,200,255,.12);padding:2px 6px;border-radius:6px;}}
.tiny{{font-size:12px;color:#9fb0c3;}}
</style>
</head>
<body>
<header>
<a class="btn" href="../index.html">🏠 Home</a>
<h1>{game['title']}</h1>
<p class="tiny">Platforms: {', '.join(game['platform'])} | Release: {date_str} | AI Rating: ⭐ {rating} / 5</p>
</header>

<section class="thumb">
<img src="../Picture/{img_file}" alt="{game['title']}">
</section>

<section class="section" id="about">
<h2>About the Game</h2>
<p>This is an AI-generated summary about {game['title']}.</p>
</section>

<section class="section" id="review">
<h2>AI Review</h2>
<p>The AI review provides detailed insights and gameplay opinions for {game['title']}.</p>
</section>

<section class="section" id="cheats">
<h2>Cheats & Tips</h2>
<ul>
{''.join(f'<li>{tip}</li>' for tip in tips)}
</ul>
{'<p>To enter cheats in-game, press the designated keys listed in each tip above.</p>' if len(tips)>=MAX_TIPS else ''}
</section>

<section class="section" id="affiliate">
<h2>Affiliate</h2>
<p>Earn passive income while gaming:</p>
<a href="https://r.honeygain.me/NAGYT86DD6" target="_blank"><strong>Try Honeygain now</strong></a>
<p class="tiny">Sponsored. Use at your own discretion.</p>
</section>

<section class="section" id="comments">
<h2>User Comments</h2>
<p>Leave your thoughts below. Max 10 comments/day. All comments are moderated.</p>
<div id="commentList"></div>
<textarea id="commentInput" placeholder="Write a comment..."></textarea>
<button onclick="submitComment()">Submit</button>
</section>

<section class="footer">
<p class="tiny">© <span id="year"></span> AI Gaming Blog</p>
</section>

<script>
document.getElementById('year').textContent = new Date().getFullYear();
const bannedWords = ["sex","fuck","porn","drugs","war","terror"];
let comments = [];
function submitComment(){{
  const input = document.getElementById('commentInput');
  const text = input.value.trim();
  if(!text) return alert("Empty comment!");
  if(text.length > 500) return alert("Comment too long!");
  if(comments.length >= 10) return alert("Max 10 comments/day reached!");
  for(let word of bannedWords) if(text.toLowerCase().includes(word)) return alert("Forbidden word detected!");
  if(/<img|<a/i.test(text)) return alert("Images and links are not allowed!");
  comments.push(text);
  const list = document.getElementById('commentList');
  const div = document.createElement('div');
  div.textContent = text;
  list.appendChild(div);
  input.value = "";
}}
</script>
</body>
</html>
"""

    filename = POST_DIR / f"{slug}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(post_content)
    existing_posts.add(slug)
    print(f"✅ Generated post: {filename.name}")
    return {
        "title": game['title'],
        "url": f"generated_posts/{filename.name}",
        "platform": game['platform'],
        "date": date_str,
        "rating": rating,
        "cover": f"Picture/{img_file}",
        "views": 0,
        "comments": 0
    }

# Generálás
new_posts = []
for game in random.sample(GAMES, len(GAMES)):
    post_data = generate_post(game)
    if post_data:
        new_posts.append(post_data)

# Frissítjük az index.html POSTS tömbjét
if new_posts:
    # Betöltés
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()
    # POSTS rész újragenerálása
    start_tag = "// <<< AUTO-GENERATED POSTS START >>>"
    end_tag = "// <<< AUTO-GENERATED POSTS END >>>"
    start_idx = html.find(start_tag)
    end_idx = html.find(end_tag)
    posts_json = json.dumps(new_posts, indent=2)
    new_html = html[:start_idx+len(start_tag)] + "\n    " + posts_json + "\n    " + html[end_idx:]
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"✅ index.html POSTS updated.")
