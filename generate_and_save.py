import os
import random
import argparse
import datetime
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup

# ==============
# SETTINGS
# ==============
OUTPUT_DIR = "generated_posts"
PICTURE_DIR = r"C:\ai_blog\Picture"
INDEX_FILE = "index.html"
RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"

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
    {"name": "Tomb Raider: Legend", "platforms": ["PC", "PS", "Xbox"], "year": 2006, "publisher": "Eidos Interactive", "version": "1.0"},
    {"name": "Deathloop", "platforms": ["PC", "PS"], "year": 2021, "publisher": "Arkane Studios", "version": "1.0"},
]

CHEATS_EXAMPLES = [
    "God Mode: IDDQD",
    "Infinite Ammo: GIVEALL",
    "Unlock All Levels: LEVELUP",
    "Max Money: RICHGUY",
    "No Clip Mode: NOCLIP"
]

# ==============
# HELPERS
# ==============
def slugify(name):
    return name.lower().replace(" ", "-").replace(":", "").replace("_", "-") + ".html"

def get_game_cover(game_name):
    """Fetch game cover from RAWG API and save locally."""
    url = "https://api.rawg.io/api/games"
    params = {
        "key": RAWG_API_KEY,
        "search": game_name,
        "page_size": 1
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        results = r.json().get("results", [])
        if results:
            img_url = results[0].get("background_image")
            if img_url:
                filename = slugify(game_name).replace(".html", ".jpg")
                filepath = os.path.join(PICTURE_DIR, filename)
                if not os.path.exists(filepath):
                    img_data = requests.get(img_url).content
                    with open(filepath, "wb") as f:
                        f.write(img_data)
                return filepath.replace("\\", "/")
    except Exception as e:
        print(f"Error fetching cover for {game_name}: {e}")
    # fallback placeholder
    return f"https://placehold.co/800x450?text={game_name.replace(' ','+')}"

def generate_post(game, existing_files):
    now = datetime.datetime.now()
    filename = slugify(game["name"])
    if filename in existing_files:
        print(f"Skipping '{game['name']}' (already exists).")
        return None

    filepath = os.path.join(OUTPUT_DIR, filename)
    title = f"{game['name']} Cheats & Tips"
    rating = round(random.uniform(2.5, 5.0), 1)
    cheats = random.sample(CHEATS_EXAMPLES, k=2)
    cover = get_game_cover(game["name"])

    description = f"""
    <p><strong>{game['name']}</strong> is one of the most exciting games released in {game['year']}. 
    Developed by {game['publisher']}, it has become a landmark title for {', '.join(game['platforms'])} gamers worldwide.</p>

    <p>In this in-depth review, we explore the storyline, graphics, gameplay mechanics, and why this game continues to capture players' attention. 
    From immersive open-world exploration to breathtaking visuals, {game['name']} delivers a unique gaming experience.</p>

    <p>We also cover tips and tricks to enhance your playthrough, secrets hidden across the game world, 
    and strategies to maximize your performance whether you are a casual or hardcore gamer.</p>
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{title}</title>
  <meta name="description" content="Review, cheats, and gameplay tips for {game['name']}." />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>
<body style="font-family:Arial,sans-serif; max-width:800px; margin:0 auto; line-height:1.6; padding:20px; background-color:#0b0f14; color:#eaf1f8;">
  <nav><a href="../index.html" style="color:#5cc8ff;">🏠 Home</a></nav>
  <h1>{title}</h1>
  <img src="{cover}" alt="{game['name']} gameplay and tips" style="width:100%; border-radius:8px;" />
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
  <p><em>Leave your thoughts below. Max 10 comments/day. All comments are moderated. No links, images, or inappropriate words.</em></p>
  <textarea id="comment" style="width:100%;height:100px;"></textarea><br>
  <button onclick="submitComment()">Submit</button>
  <ul id="commentsList"></ul>

  <hr>
  <footer style="font-size:12px; color:#666;">
    <p><strong>Comment Policy:</strong> No spam, ads, offensive language, or disallowed topics (adult, drugs, war, terrorism). Max 10 comments per day. All comments are moderated.</p>
    <p><strong>Terms:</strong> Informational purposes only. Trademarks belong to their owners. Affiliate links may generate commission.</p>
    <p>© {now.year} AI Gaming Blog</p>
  </footer>

  <script>
    let commentsCount = 0;
    function submitComment(){{
      const txt = document.getElementById('comment').value.trim();
      if(!txt) return alert('Empty comment');
      if(commentsCount>=10) return alert('Max 10 comments/day');
      const banned = ['sex','porn','fuck','shit','drugs','terror','http','www','<','>','img','href'];
      if(banned.some(w=>txt.toLowerCase().includes(w))) return alert('Comment rejected');
      const li = document.createElement('li'); li.textContent = txt;
      document.getElementById('commentsList').appendChild(li);
      commentsCount++;
      document.getElementById('comment').value='';
    }}
  </script>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return {
        "title": game["name"],
        "url": filepath.replace("\\", "/"),
        "platform": game["platforms"],
        "date": now.strftime("%Y-%m-%d"),
        "rating": rating,
        "cover": cover,
        "views": 0,
        "comments": 0
    }

# ==============
# UPDATE INDEX
# ==============
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

# ==============
# MAIN
# ==============
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=5)
    args = parser.parse_args()

    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    Path(PICTURE_DIR).mkdir(exist_ok=True)

    # collect existing files
    existing_files = set(os.listdir(OUTPUT_DIR))

    posts = []
    attempts = 0
    while len(posts) < args.num_posts and attempts < 50:
        game = random.choice(GAMES)
        post = generate_post(game, existing_files)
        attempts += 1
        if post:
            posts.append(post)
            existing_files.add(slugify(game["name"]))
            print(f"✅ Generated post: {post['url']}")

    update_index(posts)
    print(f"Done. New posts added: {len(posts)}")

if __name__ == "__main__":
    main()
