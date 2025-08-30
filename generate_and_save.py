import os
import json
import requests
from datetime import datetime
from pathlib import Path
from slugify import slugify

# Config
POSTS_DIR = Path("generated_posts")
PICTURES_DIR = Path("Picture")
TEMPLATE_FILE = Path("templates/post_template.html")
RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"
NUM_POSTS = 12

# Ensure folders exist
POSTS_DIR.mkdir(exist_ok=True)
PICTURES_DIR.mkdir(exist_ok=True)

# Load games list (example: from RAWG)
def fetch_random_games(n):
    url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&page_size={n}&ordering=-rating"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    games = []
    for g in data["results"]:
        games.append({
            "title": g["name"],
            "platform": [p["platform"]["name"] for p in g.get("platforms", [])],
            "rating": g.get("rating", 0),
            "image_url": g.get("background_image", ""),
            "release": g.get("released", ""),
            "id": g.get("id")
        })
    return games

# Check existing posts
existing_slugs = set(p.stem for p in POSTS_DIR.glob("*.html"))

# Load post template
with open(TEMPLATE_FILE, encoding="utf-8") as f:
    POST_TEMPLATE = f.read()

# Generate posts
games = fetch_random_games(NUM_POSTS * 2)  # Fetch more to avoid duplicates
generated_count = 0

for game in games:
    slug = slugify(game["title"])
    if slug in existing_slugs:
        continue  # Skip existing
    filename = POSTS_DIR / f"{slug}.html"

    # Download image
    image_path = PICTURES_DIR / f"{slug}.jpg"
    if game["image_url"]:
        try:
            img_data = requests.get(game["image_url"]).content
            with open(image_path, "wb") as img_file:
                img_file.write(img_data)
        except Exception as e:
            print(f"⚠️ Image download failed for {game['title']}: {e}")
            image_path = ""

    # Cheats & Tips placeholder (max 15)
    cheats = [f"Cheat tip {i+1}" for i in range(min(15, 5))]

    # Fill template
    post_html = POST_TEMPLATE.format(
        title=game["title"],
        rating=game["rating"],
        release=game["release"] or datetime.now().strftime("%Y-%m-%d"),
        platforms=", ".join(game["platform"]) or "PC",
        image=str(image_path).replace("\\", "/"),
        cheats="\n".join(f"<li>{c}</li>" for c in cheats)
    )

    # Save post
    with open(filename, "w", encoding="utf-8") as f:
        f.write(post_html)
    generated_count += 1
    existing_slugs.add(slug)

    if generated_count >= NUM_POSTS:
        break

print(f"✅ Generated {generated_count} new posts in {POSTS_DIR}")
