import os
import random
import argparse
import datetime
import json
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote

# ========================
# SETTINGS
# ========================
OUTPUT_DIR = "generated_posts"
INDEX_FILE = "index.html"
PICTURE_DIR = r"C:\ai_blog\Picture"

GAMES = [
    {"name": "Elden Ring", "platforms": ["PC", "PS", "Xbox"], "year": 2022, "publisher": "FromSoftware", "version": "1.09"},
    {"name": "GTA V", "platforms": ["PC", "PS", "Xbox"], "year": 2013, "publisher": "Rockstar Games", "version": "Latest"},
    {"name": "The Witcher 3: Wild Hunt", "platforms": ["PC", "PS", "Xbox", "Switch"], "year": 2015, "publisher": "CD Projekt Red", "version": "Next-Gen"},
    {"name": "Minecraft", "platforms": ["PC", "Mobile", "Xbox", "PS"], "year": 2011, "publisher": "Mojang", "version": "1.20"},
    {"name": "Fortnite", "platforms": ["PC", "PS", "Xbox", "Mobile"], "year": 2017, "publisher": "Epic Games", "version": "Chapter 4"},
    {"name": "Call of Duty: Modern Warfare II", "platforms": ["PC", "PS", "Xbox"], "year": 2022, "publisher": "Activision", "version": "1.0"},
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

YOUTUBE_API_KEY = "AIzaSyAXedHcSZ4zUaqSaD3MFahLz75IvSmxggM"

# ========================
# HELPER FUNCTIONS
# ========================

def get_cover_image(game_name):
    filename = f"{game_name.replace(' ','_')}.jpg"
    path = os.path.join(PICTURE_DIR, filename)
    if os.path.exists(path):
        # relative path for HTML
        return f"../Picture/{quote(filename)}"
    else:
        # placeholder
        init = "".join([w[0].upper() for w in game_name.split()[:2]])
        svg = quote(f"<svg xmlns='http://www.w3.org/2000/svg' width='800' height='450'>"
                    f"<rect fill='#0f141c' width='100%' height='100%'/>"
                    f"<text x='50%' y='54%' dominant-baseline='middle' text-anchor='middle' fill='#5cc8ff' font-size='120'>{init}</text>"
                    f"</svg>")
        return f"data:image/svg+xml,{svg}"

def generate_youtube_embed(game_name):
    # egyszerűség kedvéért itt véletlenszerű embed URL, de lehet YouTube API-val cserélni
    examples = [
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/9bZkp7q19f0",
        "https://www.youtube.com/embed/3fumBcKC6RE"
    ]
    return random.choice(examples)

# ========================
# GENERATE POST
# ========================

def generate_post(game):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}-{game['name'].replace(' ', '_')}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)

    title = f"{game['name']} Review & Guide"
    rating = round(random.uniform(2.5, 5.0), 1)
    youtube = generate_youtube_embed(game['name'])
    cheats = random.sample(CHEATS_EXAMPLES, k=2)
    cover = get_cover_image(game['name'])

    description = f"""
    <p><strong>{game['name']}</strong> is a game released in {game['year']} by {game['publisher']} for {', '.join(game['platforms'])}.</p>
    <p>Explore storyline, graphics, and gameplay mechanics unique to {game['name']}.</p>
    <p>Tips, cheats, and strategies are included to enhance your experience.</p>
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{title}</title>
  <meta name="description" content="Review, cheats, and gameplay tips for {game['name']}." />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>
<body style="font-family:Arial, sans-serif; max-width:800px; margin:0 auto; line-height:1.6; padding:20px;">
  <a href="../index.html">← Back to Home</a>
  <h1>{game['name']}</h1>
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

  <h2>Gameplay Video</h2>
  <iframe width="100%" height="400" src="{youtube}" frameborder="0" allowfullscreen></iframe>

  <h2>Cheats & Tips</h2>
  <ul>{''.join(f"<li>{c}</li>" for c in cheats)}</ul>

  <h2>AI Rating</h2>
  <p>⭐ {rating}/5</p>

  <hr>
  <h2>Sponsored</h2>
  <p><a href="https://r.honeygain.me/NAGYT86DD6" target="_blank">📱 Earn real money while you play – Honeygain</a></p>
  <p><a href="https://icmarkets.com/?camp=3992" target="_blank">🌍 ICMarkets – trade like a pro</a></p>
  <p><a href="https://www.dukascopy.com/api/es/12831/type-S/target-id-149" target="_blank">🏦 Dukascopy – promo code: E12831</a></p>

  <footer style="font-size:12px; color:#666; margin-top:20px;">
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

# ========================
# UPDATE INDEX
# ========================

def update_index(posts):
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Filter out duplicate titles
    seen = set()
    unique_posts = []
    for p in posts:
        if p['title'] not in seen:
            seen.add(p['title'])
            unique_posts.append(p)

    scripts = soup.find_all("script")
    for s in scripts:
        if "AUTO-GENERATED POSTS START" in s.text:
            before = s.text.split("POSTS =")[0]
            after = s.text.split("// <<< AUTO-GENERATED POSTS END >>>")[1]
            new_json = json.dumps(unique_posts, indent=2)
            s.string = f"    // <<< AUTO-GENERATED POSTS START >>>\n    const POSTS = {new_json};\n    // <<< AUTO-GENERATED POSTS END >>>{after}"
            break

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(str(soup))

# ========================
# MAIN
# ========================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=5)
    args = parser.parse_args()

    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    Path(PICTURE_DIR).mkdir(exist_ok=True)

    posts = []
    for _ in range(args.num_posts):
        game = random.choice(GAMES)
        post = generate_post(game)
        posts.append(post)
        print(f"Generated: {post['title']} → {post['url']}")

    update_index(posts)
    print("index.html updated.")

if __name__ == "__main__":
    main()
