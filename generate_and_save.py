import os
import random
import argparse
import datetime
import json
from pathlib import Path
from bs4 import BeautifulSoup

# ==============
# SETTINGS
# ==============
OUTPUT_DIR = "generated_posts"
INDEX_FILE = "index.html"

# Sample game pool (népszerűbb címekből válogatva)
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

YOUTUBE_EXAMPLES = [
    "https://www.youtube.com/embed/dQw4w9WgXcQ",
    "https://www.youtube.com/embed/9bZkp7q19f0",
    "https://www.youtube.com/embed/3fumBcKC6RE"
]

CHEATS_EXAMPLES = [
    "God Mode: IDDQD",
    "Infinite Ammo: GIVEALL",
    "Unlock All Levels: LEVELUP",
    "Max Money: RICHGUY",
    "No Clip Mode: NOCLIP"
]

# ==============
# GENERATE POST
# ==============
def generate_post(game):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}-{game['name'].replace(' ', '_')}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)

    title = f"{game['name']} Review & Guide"
    rating = round(random.uniform(2.5, 5.0), 1)
    youtube = random.choice(YOUTUBE_EXAMPLES)
    cheats = random.sample(CHEATS_EXAMPLES, k=2)

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
  <meta charset="UTF-8" />
  <title>{title}</title>
  <meta name="description" content="Review, cheats, and gameplay tips for {game['name']}." />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>
<body style="font-family:Arial, sans-serif; max-width:800px; margin:0 auto; line-height:1.6; padding:20px;">
  <h1>{game['name']}</h1>
  <img src="https://placehold.co/800x450?text={game['name'].replace(' ','+')}" alt="{game['name']}" style="width:100%; border-radius:8px;" />

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

  <h2>Gameplay Video</h2>
  <iframe width="100%" height="400" src="{youtube}" frameborder="0" allowfullscreen></iframe>

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
    <p><strong>Comment Policy:</strong> No spam, ads, offensive language, or disallowed topics (adult, drugs, war, terrorism). Max 10 comments per day. All comments are moderated.</p>
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
        "cover": f"https://placehold.co/800x450?text={game['name'].replace(' ','+')}",
        "views": 0,
        "comments": 0
    }

# ==============
# UPDATE INDEX
# ==============
def update_index(posts):
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Find JS POSTS array
    scripts = soup.find_all("script")
    for s in scripts:
        if "AUTO-GENERATED POSTS START" in s.text:
            # replace JSON array
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

    posts = []
    for i in range(args.num_posts):
        game = random.choice(GAMES)
        post = generate_post(game)
        posts.append(post)
        print(f"Generated: {post['title']} → {post['url']}")

    update_index(posts)
    print("index.html updated.")

if __name__ == "__main__":
    main()
