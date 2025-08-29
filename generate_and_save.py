import os
import random
import argparse
import datetime
import json
from pathlib import Path
from bs4 import BeautifulSoup
import requests

# =================
# SETTINGS
# =================
OUTPUT_DIR = "generated_posts"
INDEX_FILE = "index.html"
PICTURE_DIR = r"C:\Users\User\OneDrive\blogok\v3\ai_blog\Picture"
YOUTUBE_API_KEY = "AIzaSyAXedHcSZ4zUaqSaD3MFahLz75IvSmxggM"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

# =================
# SAMPLE GAME POOL
# =================
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

# =================
# HELPERS
# =================
def slugify(name, extra="cheats-tips"):
    return name.lower().replace(" ", "-").replace(":", "").replace("_", "-") + f"-{extra}.html"

def get_youtube_video(game_name):
    params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet",
        "type": "video",
        "maxResults": 1,
        "q": f"{game_name} gameplay"
    }
    response = requests.get(YOUTUBE_SEARCH_URL, params=params)
    data = response.json()
    if "items" in data and len(data["items"]) > 0:
        video_id = data["items"][0]["id"]["videoId"]
        return f"https://www.youtube.com/embed/{video_id}"
    return None

def ensure_picture(game_name):
    seo_name = game_name.lower().replace(" ", "-")
    file_path = os.path.join(PICTURE_DIR, f"{seo_name}.jpg")
    if os.path.exists(file_path):
        return file_path.replace("\\", "/")
    return f"https://placehold.co/800x450?text={game_name.replace(' ','+')}"


# =================
# GENERATE POST
# =================
def generate_post(game):
    now = datetime.datetime.now()
    filename = slugify(game["name"])
    filepath = os.path.join(OUTPUT_DIR, filename)

    title = f"{game['name']} Cheats & Tips"
    rating = round(random.uniform(2.5, 5.0), 1)
    youtube = get_youtube_video(game["name"])
    cheats = random.sample(CHEATS_EXAMPLES, k=2)
    cover = ensure_picture(game["name"])

    description = f"""
<p><strong>{game['name']}</strong> is a top title released in {game['year']} by {game['publisher']}. 
Supports {', '.join(game['platforms'])}.</p>
<p>This guide explores the core gameplay, key mechanics, and tips to excel in {game['name']}.</p>
<p>Unlock cheats, strategies, and hidden secrets to maximize your experience.</p>
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
  <h1>{title}</h1>
  <img src="{cover}" alt="{game['name']} gameplay and tips" style="width:100%; border-radius:8px;" />

  <h2>About the Game</h2>
  <ul>
    <li><strong>Release Year:</strong> {game['year']}</li>
    <li><strong>Publisher:</strong> {game['publisher']}</li>
    <li><strong>Version:</strong> {game['version']}</li>
    <li><strong>Platforms:</strong> {', '.join(game['platforms'])}</li>
    <li><strong>Offline:</strong> {random.choice(["Yes","No"])}</li>
    <li><strong>Multiplayer:</strong> {random.choice(["Yes","No"])}</li>
  </ul>

  <h2>Full Review</h2>
  {description}
"""

    if youtube:
        html += f"""
<h2>Gameplay Video</h2>
<iframe width="100%" height="400" src="{youtube}" frameborder="0" allowfullscreen></iframe>
"""

    html += f"""
<h2>Cheats & Tips</h2>
<ul>
{''.join(f"<li>{c}</li>" for c in cheats)}
</ul>

<h2>AI Rating</h2>
<p>⭐ {rating}/5</p>

<h2>User Comments</h2>
<p><em>Leave your thoughts below. Max 10 comments/day. All comments are moderated.</em></p>
<textarea style="width:100%;height:100px;"></textarea>
<br><button>Submit</button>

<hr>
<h2>Sponsored</h2>
<p><a href="https://r.honeygain.me/NAGYT86DD6" target="_blank" style="font-size:18px;">📱 Earn real money while you play – Honeygain</a></p>
<p><a href="https://icmarkets.com/?camp=3992" target="_blank">🌍 ICMarkets – trade like a pro</a></p>
<p><a href="https://www.dukascopy.com/api/es/12831/type-S/target-id-149" target="_blank">🏦 Dukascopy – promo code: E12831</a></p>

<hr>
<footer style="font-size:12px; color:#666;">
<p><strong>Comment Policy:</strong> No spam, ads, offensive language. Max 10 comments/day.</p>
<p><strong>Terms:</strong> Informational purposes only. Trademarks belong to their owners.</p>
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

# =================
# UPDATE INDEX
# =================
def update_index(posts):
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    scripts = soup.find_all("script")
    for s in scripts:
        if "AUTO-GENERATED POSTS START" in s.text:
            new_json = json.dumps(posts[-12:], indent=2)
            s.string = f"// <<< AUTO-GENERATED POSTS START >>>\nconst POSTS = {new_json};\n// <<< AUTO-GENERATED POSTS END >>>"
            break

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(str(soup))

# =================
# MAIN
# =================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=5)
    args = parser.parse_args()

    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    Path(PICTURE_DIR).mkdir(exist_ok=True)

    posts = []
    seen_titles = set()
    for _ in range(args.num_posts):
        game = random.choice(GAMES)
        if game["name"] in seen_titles:
            continue
        post = generate_post(game)
        posts.append(post)
        seen_titles.add(game["name"])
        print(f"Generated: {post['title']} → {post['url']}")

    update_index(posts)
    print("index.html updated.")

if __name__ == "__main__":
    main()
