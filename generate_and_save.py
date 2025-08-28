import os
import random
import datetime
import json
from pathlib import Path
from bs4 import BeautifulSoup

# =====================
# SETTINGS
# =====================
OUTPUT_DIR = "generated_posts"
INDEX_FILE = "index.html"

# Játékok listája
GAMES = [
    {"name": "Elden Ring", "platforms": ["PC", "PS", "Xbox"], "year": 2022, "publisher": "FromSoftware"},
    {"name": "GTA V", "platforms": ["PC", "PS", "Xbox"], "year": 2013, "publisher": "Rockstar Games"},
    {"name": "The Witcher 3 Wild Hunt", "platforms": ["PC", "PS", "Xbox", "Switch"], "year": 2015, "publisher": "CD Projekt Red"},
    {"name": "Minecraft", "platforms": ["PC", "Mobile", "Xbox", "PS"], "year": 2011, "publisher": "Mojang"},
    {"name": "Fortnite", "platforms": ["PC", "PS", "Xbox", "Mobile"], "year": 2017, "publisher": "Epic Games"},
    {"name": "Call of Duty Modern Warfare II", "platforms": ["PC", "PS", "Xbox"], "year": 2022, "publisher": "Activision"},
    {"name": "League of Legends", "platforms": ["PC"], "year": 2009, "publisher": "Riot Games"},
    {"name": "FIFA 23", "platforms": ["PC", "PS", "Xbox"], "year": 2022, "publisher": "EA Sports"},
]

# YouTube videók játékhoz kapcsolva
YOUTUBE_MAP = {
    "Elden Ring": "https://www.youtube.com/embed/9iUuT2y7gC8",
    "GTA V": "https://www.youtube.com/embed/ZpNZ9cZY-2I",
    "The Witcher 3 Wild Hunt": "https://www.youtube.com/embed/ndl1W4ltcmg",
    "Minecraft": "https://www.youtube.com/embed/aqz-KE-bpKQ",
    "Fortnite": "https://www.youtube.com/embed/2gUtfBmw86Y",
    "Call of Duty Modern Warfare II": "https://www.youtube.com/embed/xmC1M5DZ4xM",
    "League of Legends": "https://www.youtube.com/embed/UZi6wZy3cpc",
    "FIFA 23": "https://www.youtube.com/embed/8lzMx7JzH4o",
}

CHEATS_EXAMPLES = [
    "God Mode: IDDQD",
    "Infinite Ammo: GIVEALL",
    "Unlock All Levels: LEVELUP",
    "Max Money: RICHGUY",
    "No Clip Mode: NOCLIP"
]

# =====================
# HELPERS
# =====================
def slugify(name, extra="cheats-tips"):
    return name.lower().replace(" ", "-").replace(":", "").replace("_", "-") + f"-{extra}.html"

def placeholder_image(game_name):
    return f"https://placehold.co/800x450?text={game_name.replace(' ','+')}"

# =====================
# GENERATE POST
# =====================
def generate_post(game):
    filename = slugify(game["name"])
    filepath = os.path.join(OUTPUT_DIR, filename)
    title = f"{game['name']} Cheats & Tips"
    rating = round(random.uniform(2.5, 5.0), 1)
    youtube = YOUTUBE_MAP.get(game["name"], None)
    cheats = random.sample(CHEATS_EXAMPLES, k=2)
    cover = placeholder_image(game["name"])

    description = f"""
    <p><strong>{game['name']}</strong> is one of the most exciting games released in {game['year']}. Developed by {game['publisher']}.</p>
    <p>Explore gameplay, tips, secrets, and strategies to maximize your performance.</p>
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>{title}</title>
<meta name="description" content="Cheats, tips and gameplay guide for {game['name']}" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>
<body style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px;">
<h1>{game['name']} Cheats & Tips</h1>
<img src="{cover}" alt="{game['name']} gameplay and tips" style="width:100%; border-radius:8px;" />
<h2>About the Game</h2>
<ul>
<li><strong>Year:</strong> {game['year']}</li>
<li><strong>Publisher:</strong> {game['publisher']}</li>
<li><strong>Platforms:</strong> {', '.join(game['platforms'])}</li>
</ul>
<h2>Review & Guide</h2>
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
{''.join(f'<li>{c}</li>' for c in cheats)}
</ul>
<h2>AI Rating</h2>
<p>⭐ {rating}/5</p>
<hr>
<footer style="font-size:12px;color:#666;">
<p>© {datetime.datetime.now().year} AI Gaming Blog</p>
</footer>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return {
        "title": game["name"],
        "url": f"{OUTPUT_DIR}/{filename}",
        "platform": game["platforms"],
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
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
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    posts = []
    for _ in range(5):
        game = random.choice(GAMES)
        post = generate_post(game)
        posts.append(post)
        print(f"Generated: {post['title']} → {post['url']}")

    update_index(posts)
    print("index.html updated with 5 posts.")

if __name__ == "__main__":
    main()
