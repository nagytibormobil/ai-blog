import os
import random
import argparse
import datetime
import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# ===================
# SETTINGS
# ===================
OUTPUT_DIR = "generated_posts"
INDEX_FILE = "index.html"
PICTURE_DIR = "Picture"

Path(PICTURE_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# Games pool
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

YOUTUBE_API_KEY = "AIzaSyAXedHcSZ4zUaqSaD3MFahLz75IvSmxggM"

CHEATS_EXAMPLES = [
    "God Mode: IDDQD",
    "Infinite Ammo: GIVEALL",
    "Unlock All Levels: LEVELUP",
    "Max Money: RICHGUY",
    "No Clip Mode: NOCLIP"
]

AFFILIATE_HTML = """
<section class="section" id="affiliates">
<div class="ad">
<h3>Earn Real Money While You Play 📱</h3>
<p>Simple passive income by sharing a bit of your internet. Runs in the background while you game.</p>
<p><a href="https://r.honeygain.me/NAGYT86DD6" target="_blank"><strong>Try Honeygain now</strong></a></p>
<div class="tiny">Sponsored. Use at your own discretion.</div>
</div>
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
</section>
"""

# ===================
# HELPER FUNCTIONS
# ===================
def fetch_youtube_video(game_name):
    import urllib.parse
    query = urllib.parse.quote(f"{game_name} gameplay")
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={YOUTUBE_API_KEY}&type=video&maxResults=1"
    try:
        resp = requests.get(url).json()
        video_id = resp["items"][0]["id"]["videoId"]
        return f"https://www.youtube.com/embed/{video_id}"
    except Exception:
        return "https://www.youtube.com/embed/dQw4w9WgXcQ"

def download_cover_image(game_name):
    filename = f"{game_name.replace(' ', '_')}.jpg"
    filepath = os.path.join(PICTURE_DIR, filename)
    if not os.path.exists(filepath):
        try:
            rawg_api_key = "2fafa16ea4c147438f3b0cb031f8dbb7"
            resp = requests.get(f"https://api.rawg.io/api/games?search={game_name}&key={rawg_api_key}").json()
            img_url = resp["results"][0]["background_image"]
            r = requests.get(img_url)
            if r.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(r.content)
        except:
            r = requests.get(f"https://placehold.co/800x450?text={game_name.replace(' ','+')}") 
            with open(filepath, "wb") as f:
                f.write(r.content)
    return filepath.replace("\\","/")

def generate_post(game):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}-{game['name'].replace(' ', '_').lower()}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)
    title = f"{game['name']} Review & Guide"
    rating = round(random.uniform(2.5, 5.0), 1)
    youtube = fetch_youtube_video(game['name'])
    cheats = random.sample(CHEATS_EXAMPLES, k=2)
    cover_path = download_cover_image(game['name'])

    description = f"""
    <p><strong>{game['name']}</strong> is one of the most exciting games released in {game['year']}. 
    Developed by {game['publisher']}, it has become a landmark title for {', '.join(game['platforms'])} gamers worldwide.</p>
    <p>In this review, we explore gameplay mechanics, graphics, and tips unique to {game['name']}.</p>
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>{title}</title>
<meta name="description" content="Review, cheats, and gameplay tips for {game['name']}."/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>
<body style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px;line-height:1.6;">
<a href="../index.html">⬅ Back to Home</a>
<h1>{game['name']}</h1>
<img src="{cover_path}" alt="{game['name']} gameplay cover" style="width:100%;border-radius:8px;"/>
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
{AFFILIATE_HTML}
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
        "cover": cover_path,
        "views": 0,
        "comments": 0
    }

def update_index(posts):
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    scripts = soup.find_all("script")
    for s in scripts:
        if "AUTO-GENERATED POSTS START" in s.text:
            before = s.text.split("POSTS =")[0]
            after = s.text.split("// <<< AUTO-GENERATED POSTS END >>>")[1]
            unique_posts = {p["title"]: p for p in posts}
            new_json = json.dumps(list(unique_posts.values()), indent=2)
            s.string = f"    // <<< AUTO-GENERATED POSTS START >>>\n    const POSTS = {new_json};\n    // <<< AUTO-GENERATED POSTS END >>>{after}"
            break

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(str(soup))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=12)
    args = parser.parse_args()

    # Prevent duplicate posts
    existing_titles = set()
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith(".html"):
            existing_titles.add(f.split("-",1)[1].rsplit(".",1)[0].replace("_"," ").title())

    posts = []
    available_games = [g for g in GAMES if g["name"] not in existing_titles]
    random.shuffle(available_games)
    to_create = min(args.num_posts, len(available_games))

    for i in range(to_create):
        post = generate_post(available_games[i])
        posts.append(post)
        print(f"Generated: {post['title']} → {post['url']}")

    update_index(posts)
    print("index.html updated.")

if __name__=="__main__":
    main()
