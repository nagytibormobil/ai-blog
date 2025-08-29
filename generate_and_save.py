import os
import random
import argparse
import datetime
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup

# ============== SETTINGS ==============
OUTPUT_DIR = "generated_posts"
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)

INDEX_FILE = "index.html"
RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"

# Tiltott szavak a kommentekhez
BLOCKED_WORDS = ["sex", "porn", "drugs", "violence", "terror", "fuck", "shit"]

# Sample game pool
GAMES = [
    {"name": "Elden Ring", "platforms": ["PC", "PS", "Xbox"], "year": 2022, "publisher": "FromSoftware", "version": "1.09"},
    {"name": "GTA V", "platforms": ["PC", "PS", "Xbox"], "year": 2013, "publisher": "Rockstar Games", "version": "Latest"},
    {"name": "The Witcher 3 Wild Hunt", "platforms": ["PC", "PS", "Xbox", "Switch"], "year": 2015, "publisher": "CD Projekt Red", "version": "Next-Gen"},
    {"name": "Minecraft", "platforms": ["PC", "Mobile", "Xbox", "PS"], "year": 2011, "publisher": "Mojang", "version": "1.20"},
    {"name": "Fortnite", "platforms": ["PC", "PS", "Xbox", "Mobile"], "year": 2017, "publisher": "Epic Games", "version": "Chapter 4"},
    {"name": "Call of Duty Modern Warfare II", "platforms": ["PC", "PS", "Xbox"], "year": 2022, "publisher": "Activision", "version": "1.0"},
    {"name": "League of Legends", "platforms": ["PC"], "year": 2009, "publisher": "Riot Games", "version": "13.8"},
    {"name": "FIFA 23", "platforms": ["PC", "PS", "Xbox"], "year": 2022, "publisher": "EA Sports", "version": "Final"},
]

CHEATS_EXAMPLES = [
    "God Mode: IDDQD",
    "Infinite Ammo: GIVEALL",
    "Unlock All Levels: LEVELUP",
    "Max Money: RICHGUY",
    "No Clip Mode: NOCLIP"
]

# ============== HELPERS ==============
def slugify(name):
    return name.lower().replace(" ", "-").replace(":", "").replace("_", "-") + "-cheats-tips.html"

def download_cover(game_name):
    """Letölt egy valós képet a RAWG API-ról és menti az images mappába."""
    try:
        url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={game_name}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        results = r.json().get("results", [])
        if results:
            img_url = results[0].get("background_image")
            if img_url:
                ext = os.path.splitext(img_url)[1].split("?")[0] or ".jpg"
                filename = slugify(game_name).replace(".html", ext)
                filepath = os.path.join(IMAGES_DIR, filename)
                if not os.path.exists(filepath):
                    img_data = requests.get(img_url, timeout=10).content
                    with open(filepath, "wb") as f:
                        f.write(img_data)
                return f"images/{filename}"
    except Exception as e:
        print(f"Error fetching image for {game_name}: {e}")
    # Placeholder kép hiba esetén
    return "https://placehold.co/800x450?text="+game_name.replace(" ","+")

def generate_post(game, existing_titles):
    now = datetime.datetime.now()
    if game["name"] in existing_titles:
        print(f"Skipping '{game['name']}' (already exists).")
        return None

    filename = slugify(game["name"])
    filepath = os.path.join(OUTPUT_DIR, filename)
    cover = download_cover(game["name"])
    rating = round(random.uniform(2.5,5.0),1)
    cheats = random.sample(CHEATS_EXAMPLES, k=2)
    description = f"""
    <p><strong>{game['name']}</strong> is one of the most exciting games released in {game['year']}. 
    Developed by {game['publisher']}, it has become a landmark title for {', '.join(game['platforms'])} gamers worldwide.</p>
    <p>Explore the gameplay mechanics, storyline, and graphics in detail. Our AI-generated guide gives you tips and cheats 
    to improve your experience and discover hidden secrets in {game['name']}.</p>
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>{game['name']} Cheats & Tips</title>
  <meta name="description" content="Review, cheats, and gameplay tips for {game['name']}."/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <style>
    body{{background:#0b0f14;color:#eaf1f8;font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px;line-height:1.6;}}
    a{{color:#5cc8ff;text-decoration:none;}} a:hover{{text-decoration:underline;}}
    h1,h2{{color:#eaf1f8;}}
    ul{{list-style:none;padding:0;}}
    li{{margin-bottom:4px;}}
    textarea{{width:100%;height:100px;}}
    button{{padding:8px 12px;margin-top:4px;cursor:pointer;}}
    footer{{font-size:12px;color:#666;margin-top:36px;border-top:1px solid #1f2a38;padding-top:12px;}}
  </style>
</head>
<body>
<a href="index.html" style="display:inline-block;margin-bottom:12px;color:#9bff9b;">🏠 Home</a>
<h1>{game['name']} Cheats & Tips</h1>
<img src="{cover}" alt="{game['name']} gameplay" style="width:100%;border-radius:8px;"/>
<h2>About the Game</h2>
<ul>
<li><strong>Release Year:</strong> {game['year']}</li>
<li><strong>Publisher:</strong> {game['publisher']}</li>
<li><strong>Version:</strong> {game['version']}</li>
<li><strong>Platforms:</strong> {', '.join(game['platforms'])}</li>
<li><strong>Offline:</strong> {random.choice(['Yes','No'])}</li>
<li><strong>Multiplayer:</strong> {random.choice(['Yes','No'])}</li>
</ul>

<h2>Full Review</h2>
{description}

<h2>Cheats & Tips</h2>
<ul>
{''.join(f"<li>{c}</li>" for c in cheats)}
</ul>

<h2>AI Rating</h2>
<p>⭐ {rating}/5</p>

<h2>User Comments</h2>
<p><em>Leave your thoughts below. Max 10 comments/day. Comments are moderated. No links, images, or banned words allowed.</em></p>
<textarea id="commentBox"></textarea>
<br><button onclick="submitComment()">Submit</button>
<ul id="commentList"></ul>

<hr>
<footer>
<p><strong>Comment Policy:</strong> No spam, ads, offensive language, or disallowed topics (adult, drugs, war, terrorism). Max 10 comments/day. All comments are moderated.</p>
<p><strong>Terms:</strong> Informational purposes only. Trademarks belong to their owners. Affiliate links may generate commission.</p>
<p>© {now.year} AI Gaming Blog</p>
</footer>

<script>
let comments = [];
function submitComment(){{
  const box = document.getElementById('commentBox');
  let text = box.value.trim();
  if(!text) return alert("Comment empty.");
  const banned = {BLOCKED_WORDS};
  for(let word of banned){{
    if(text.toLowerCase().includes(word)) return alert("Comment contains forbidden word.");
  }}
  if(text.includes("http")||text.includes("<img")) return alert("No links or images allowed.");
  if(comments.length>=10) return alert("Max 10 comments/day reached.");
  comments.push(text);
  const ul = document.getElementById('commentList');
  ul.innerHTML = comments.map(c=>`<li>${c}</li>`).join("");
  box.value="";
}}
</script>
</body>
</html>
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return {
        "title": game["name"],
        "url": filepath.replace("\\","/"),
        "platform": game["platforms"],
        "date": now.strftime("%Y-%m-%d"),
        "rating": rating,
        "cover": cover,
        "views": 0,
        "comments": 0
    }

# ============== UPDATE INDEX ==============
def update_index(posts):
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    scripts = soup.find_all("script")
    for s in scripts:
        if "AUTO-GENERATED POSTS START" in s.text:
            before = s.text.split("POSTS =")[0]
            after = s.text.split("// <<< AUTO-GENERATED POSTS END >>>")[1]
            new_json = json.dumps(posts, indent=2)
            s.string = f"    // <<< AUTO-GENERATED POSTS START >>>\n    const POSTS = {new_json};\n    // <<< AUTO-GENERATED POSTS END >>>{after}"
            break

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(str(soup))

# ============== MAIN ==============
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=5)
    args = parser.parse_args()

    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    # Létező posztok címei
    existing_titles = set()
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith(".html"):
            existing_titles.add(f.split("-cheats-tips.html")[0].replace("-"," ").title())

    posts = []
    generated = 0
    while generated < args.num_posts:
        game = random.choice(GAMES)
        post = generate_post(game, existing_titles)
        if post:
            posts.append(post)
            existing_titles.add(game["name"])
            generated += 1
            print(f"✅ Generated post: {post['url']}")

    update_index(posts)
    print(f"✅ index.html POSTS updated. Done. New posts added: {len(posts)}")

if __name__ == "__main__":
    main()
