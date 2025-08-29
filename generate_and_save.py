import os
import random
import argparse
import datetime
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote

# =====================
# SETTINGS
# =====================
OUTPUT_DIR = "generated_posts"
PICTURE_DIR = r"C:\ai_blog\Picture"
INDEX_FILE = "index.html"
RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"

# Sample game pool
GAMES = [
    {"name": "Elden Ring", "platforms": ["PC", "PS", "Xbox"], "year": 2022, "publisher": "FromSoftware", "version": "1.09", "cheat_keys": "None"},
    {"name": "GTA V", "platforms": ["PC", "PS", "Xbox"], "year": 2013, "publisher": "Rockstar Games", "version": "Latest", "cheat_keys": "F1-F12"},
    {"name": "The Witcher 3 Wild Hunt", "platforms": ["PC", "PS", "Xbox", "Switch"], "year": 2015, "publisher": "CD Projekt Red", "version": "Next-Gen", "cheat_keys": "None"},
    {"name": "Minecraft", "platforms": ["PC", "Mobile", "Xbox", "PS"], "year": 2011, "publisher": "Mojang", "version": "1.20", "cheat_keys": "T+Enter"},
    {"name": "Fortnite", "platforms": ["PC", "PS", "Xbox", "Mobile"], "year": 2017, "publisher": "Epic Games", "version": "Chapter 4", "cheat_keys": "None"},
    {"name": "Call of Duty Modern Warfare II", "platforms": ["PC", "PS", "Xbox"], "year": 2022, "publisher": "Activision", "version": "1.0", "cheat_keys": "None"},
    {"name": "League of Legends", "platforms": ["PC"], "year": 2009, "publisher": "Riot Games", "version": "13.8", "cheat_keys": "None"},
    {"name": "FIFA 23", "platforms": ["PC", "PS", "Xbox"], "year": 2022, "publisher": "EA Sports", "version": "Final", "cheat_keys": "None"},
]

CHEATS_EXAMPLES = [
    "God Mode: IDDQD",
    "Infinite Ammo: GIVEALL",
    "Unlock All Levels: LEVELUP",
    "Max Money: RICHGUY",
    "No Clip Mode: NOCLIP",
    "Super Jump: JUMPUP",
    "Invincible Vehicles: VEHICLEINV"
]

# =====================
# HELPERS
# =====================
def slugify(name):
    return name.lower().replace(" ", "-").replace(":", "").replace("_", "-") + "-cheats-tips.html"

def download_image(game_name):
    """Download image from RAWG API and save locally."""
    os.makedirs(PICTURE_DIR, exist_ok=True)
    url = f"https://api.rawg.io/api/games?search={quote(game_name)}&key={RAWG_API_KEY}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        results = r.json().get("results", [])
        if results:
            image_url = results[0].get("background_image")
            if image_url:
                ext = os.path.splitext(image_url)[1] or ".jpg"
                filename = os.path.join(PICTURE_DIR, slugify(game_name).replace(".html", ext))
                if not os.path.exists(filename):
                    img_data = requests.get(image_url).content
                    with open(filename, "wb") as f:
                        f.write(img_data)
                return filename
    except Exception as e:
        print(f"Error downloading image for {game_name}: {e}")
    # Placeholder
    return os.path.join(PICTURE_DIR, "placeholder.jpg")

# =====================
# GENERATE POST
# =====================
def generate_post(game, existing_slugs):
    now = datetime.datetime.now()
    filename = slugify(game["name"])
    if filename in existing_slugs:
        print(f"Skipping '{game['name']}' (already exists).")
        return None

    filepath = os.path.join(OUTPUT_DIR, filename)
    cover_path = download_image(game["name"])
    cover_rel = os.path.relpath(cover_path, os.path.dirname(filepath)).replace("\\","/")

    title = f"{game['name']} Cheats & Tips"
    rating = round(random.uniform(2.5, 5.0), 1)
    cheats = random.sample(CHEATS_EXAMPLES, k=min(15,len(CHEATS_EXAMPLES)))

    description = f"""
    <p><strong>{game['name']}</strong> is one of the most exciting games released in {game['year']}. 
    Developed by {game['publisher']}, it has become a landmark title for {', '.join(game['platforms'])} gamers worldwide.</p>

    <p>In this in-depth review, we explore the storyline, graphics, gameplay mechanics, and why this game continues to capture players' attention. 
    From immersive open-world exploration to breathtaking visuals, {game['name']} delivers a unique gaming experience.</p>

    <p>We also cover tips and tricks to enhance your playthrough, secrets hidden across the game world, 
    and strategies to maximize your performance whether you are a casual or hardcore gamer.</p>

    <p>Fans of {game['name']} often praise its replay value, and with our AI-generated guide, 
    you’ll be able to uncover even more details that make this title worth playing again and again.</p>
    """

    cheats_html = "".join(f"<li>{c}</li>" for c in cheats)
    if len(cheats) >= 15 and game.get("cheat_keys"):
        cheats_html += f"<li>Activate cheats in-game with keys: {game['cheat_keys']}</li>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>{title}</title>
<meta name="description" content="Review, cheats, and gameplay tips for {game['name']}."/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>
<body style="font-family:Arial,sans-serif; max-width:800px; margin:0 auto; background:#0b0f14; color:#eaf1f8; line-height:1.6; padding:20px;">
<a href="../index.html">🏠 Home</a>
<h1>{title}</h1>
<img src="{cover_rel}" alt="{game['name']} gameplay" style="width:100%; border-radius:8px;"/>
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
{cheats_html}
</ul>
<h2>AI Rating</h2>
<p>⭐ {rating}/5</p>
<h2>User Comments</h2>
<p><em>Leave your thoughts below. Max 10 comments/day. All comments are moderated.</em></p>
<textarea style="width:100%;height:100px;"></textarea><br>
<button>Submit</button>
<hr>
<footer style="font-size:12px; color:#666;">
<p><strong>Comment Policy:</strong> No spam, ads, offensive language, or disallowed topics (adult, drugs, war, terrorism). Max 10 comments per day. All comments are moderated. No links or images allowed.</p>
<p><strong>Terms:</strong> Informational purposes only. Trademarks belong to their owners. Affiliate links may generate commission.</p>
<p>© {now.year} AI Gaming Blog</p>
</footer>
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
        "cover": cover_rel,
        "views": 0,
        "comments": 0
    }

# =====================
# UPDATE INDEX
# =====================
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

# =====================
# MAIN
# =====================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=5)
    args = parser.parse_args()

    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    existing_slugs = {f for f in os.listdir(OUTPUT_DIR) if f.endswith("-cheats-tips.html")}

    posts = []
    attempts = 0
    while len(posts) < args.num_posts and attempts < 50:
        game = random.choice(GAMES)
        post = generate_post(game, existing_slugs)
        if post:
            posts.append(post)
            existing_slugs.add(slugify(game["name"]))
            print(f"✅ Generated post: {post['url']}")
        attempts += 1

    if posts:
        update_index(posts)
        print(f"✅ index.html POSTS updated. New posts added: {len(posts)}")
    else:
        print("⚠️ No new posts generated.")

if __name__ == "__main__":
    main()
