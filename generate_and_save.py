import os
import random
import argparse
import datetime
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote

# =========================
# SETTINGS
# =========================
OUTPUT_DIR = "generated_posts"
PICTURE_DIR = "Picture"
INDEX_FILE = "index.html"

# Játék adatbázis (példa)
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

BAD_WORDS = ["sex", "porn", "fuck", "shit", "drugs", "violence"]  # például

# =========================
# HELPERS
# =========================
def slugify(name):
    return name.lower().replace(" ", "-").replace(":", "").replace("_", "-") + ".html"

def download_placeholder_image(game_name):
    Path(PICTURE_DIR).mkdir(exist_ok=True)
    filename = os.path.join(PICTURE_DIR, slugify(game_name).replace(".html", ".jpg"))
    if not os.path.exists(filename):
        # egyszerű placeholder kép letöltés
        url = f"https://placehold.co/800x450?text={quote(game_name)}"
        try:
            r = requests.get(url)
            r.raise_for_status()
            with open(filename, "wb") as f:
                f.write(r.content)
        except:
            pass
    return filename.replace("\\", "/")

def generate_post(game):
    now = datetime.datetime.now()
    filename = slugify(game["name"])
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Ha már létezik, ne generáljuk újra
    if os.path.exists(filepath):
        print(f"Skipping '{game['name']}' (already exists).")
        return None

    title = f"{game['name']} Cheats & Tips"
    rating = round(random.uniform(2.5, 5.0), 1)
    cheats = random.sample(CHEATS_EXAMPLES, k=2)
    cover = download_placeholder_image(game["name"])

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

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<meta name="description" content="Review, cheats, and gameplay tips for {game['name']}">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{{font-family:Arial,sans-serif; max-width:800px;margin:0 auto;line-height:1.6;padding:20px; background:#0b0f14; color:#eaf1f8;}}
h1,h2{{color:#5cc8ff}}
textarea{{width:100%;height:100px;}}
button{{padding:10px;border-radius:6px;cursor:pointer;background:#121821;color:#eaf1f8;border:1px solid #1f2a38}}
</style>
</head>
<body>
<h1>{title}</h1>
<img src="../{cover}" alt="{game['name']}" style="width:100%; border-radius:8px;">
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
<p><em>Leave your thoughts below. Max 10 comments/day. All comments are moderated.</em></p>
<textarea></textarea>
<br><button>Submit</button>

<hr>
<h2>Sponsored</h2>
<p><a href="https://r.honeygain.me/NAGYT86DD6" target="_blank">📱 Earn real money while you play – Honeygain</a></p>
<p><a href="https://icmarkets.com/?camp=3992" target="_blank">🌍 ICMarkets – trade like a pro</a></p>
<p><a href="https://www.dukascopy.com/api/es/12831/type-S/target-id-149" target="_blank">🏦 Dukascopy – promo code: E12831</a></p>

<hr>
<footer style="font-size:12px; color:#666;">
<p><strong>Comment Policy:</strong> No spam, ads, offensive language, or disallowed topics (adult, drugs, war, terrorism). Max 10 comments per day. All comments are moderated. No images or links allowed in comments.</p>
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
        "cover": cover,
        "views": 0,
        "comments": 0
    }

# =========================
# UPDATE INDEX
# =========================
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

# =========================
# MAIN
# =========================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=5)
    args = parser.parse_args()

    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    Path(PICTURE_DIR).mkdir(exist_ok=True)

    existing_files = set(os.listdir(OUTPUT_DIR))
    posts = []
    attempts = 0
    while len(posts) < args.num_posts and attempts < 50:
        attempts += 1
        game = random.choice(GAMES)
        slug = slugify(game["name"])
        if slug in existing_files:
            continue  # már létezik, próbáljunk másikat
        post = generate_post(game)
        if post:
            posts.append(post)
            existing_files.add(slug)
            print(f"✅ Generated post: {post['url']}")

    update_index(posts)
    print(f"Done. New posts added: {len(posts)}")
    for p in posts:
        print(f" - {p['title']} -> {p['url']}")

if __name__ == "__main__":
    main()
