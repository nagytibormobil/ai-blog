import os
import random
import argparse
import datetime
import json
from pathlib import Path
from bs4 import BeautifulSoup
import requests

# =====================
# SETTINGS
# =====================
OUTPUT_DIR = "generated_posts"
PICTURE_DIR = r"C:\ai_blog\Picture"
INDEX_FILE = "index.html"
YOUTUBE_API_KEY = "AIzaSyAXedHcSZ4zUaqSaD3MFahLz75IvSmxggM"

# Sample game pool
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

# =====================
# HELPER FUNCTIONS
# =====================
def sanitize_filename(name):
    return name.lower().replace(" ", "-").replace(":", "")

def download_game_image(game_name):
    filename = f"{sanitize_filename(game_name)}.jpg"
    path = os.path.join(PICTURE_DIR, filename)
    if not os.path.exists(path):
        # Placeholder image
        url = f"https://placehold.co/800x450?text={game_name.replace(' ', '+')}"
        r = requests.get(url)
        os.makedirs(PICTURE_DIR, exist_ok=True)
        with open(path, "wb") as f:
            f.write(r.content)
    return os.path.relpath(path).replace("\\", "/")

def fetch_youtube_video(game_name):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={game_name}+gameplay&key={YOUTUBE_API_KEY}&type=video"
    r = requests.get(url).json()
    items = r.get("items", [])
    if not items:
        return "https://www.youtube.com/embed/dQw4w9WgXcQ"
    video_id = items[0]["id"]["videoId"]
    return f"https://www.youtube.com/embed/{video_id}"

# =====================
# GENERATE POST
# =====================
def generate_post(game):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}-{sanitize_filename(game['name'])}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)

    title = f"{game['name']} Review & Guide"
    rating = round(random.uniform(2.5, 5.0), 1)
    youtube = fetch_youtube_video(game['name'])
    cheats = random.sample(CHEATS_EXAMPLES, k=2)
    cover = download_game_image(game['name'])

    description = f"""
    <p><strong>{game['name']}</strong> is one of the most popular games released in {game['year']}, developed by {game['publisher']}. 
    Platforms: {', '.join(game['platforms'])}. In this review we explore gameplay, graphics, and tips.</p>
    <p>Discover strategies, secrets, and tricks to enhance your experience. Enjoy replay value and maximize fun with our AI-generated guide.</p>
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
<a href="../index.html">🏠 Home</a>
<h1>{game['name']}</h1>
<img src="{cover}" alt="{game['name']} Gameplay & Tips" style="width:100%; border-radius:8px;" />
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
<ul>
{''.join(f"<li>{c}</li>" for c in cheats)}
</ul>
<h2>AI Rating</h2>
<p>⭐ {rating}/5</p>
</body>
</html>"""

    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return {
        "title": game["name"],
        "url": f"{OUTPUT_DIR}/{filename}".replace("\\", "/"),
        "platform": game["platforms"],
        "date": now.strftime("%Y-%m-%d"),
        "rating": rating,
        "cover": cover,
        "views": 0,
        "comments": 0
    }

# =====================
# UPDATE INDEX
# =====================
def update_index(posts):
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Remove duplicates by title
    unique_posts = []
    titles = set()
    for p in posts:
        if p["title"] not in titles:
            titles.add(p["title"])
            unique_posts.append(p)

    # Update POSTS array
    scripts = soup.find_all("script")
    for s in scripts:
        if "AUTO-GENERATED POSTS START" in s.text:
            before = s.text.split("POSTS =")[0]
            after = s.text.split("// <<< AUTO-GENERATED POSTS END >>>")[1]
            new_json = json.dumps(unique_posts, indent=2)
            s.string = f"    // <<< AUTO-GENERATED POSTS START >>>\n    const POSTS = {new_json};\n    // <<< AUTO-GENERATED POSTS END >>>{after}"
            break

    with open(INDEX_FI_
