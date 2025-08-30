import os
import json
import random
import datetime
from jinja2 import Template

# --- Config ---
POSTS_DIR = "generated_posts"
PICTURE_DIR = "Picture"
TEMPLATE_PATH = "templates/post_template.html"
NUM_POSTS = 5  # Alapértelmezett, --num_posts opcióval felülírható

# Példa játék lista, a valós adat lehet API-ból
GAMES = [
    {"title": "GTA V", "platforms": ["PC", "PS", "Xbox"], "description": "Open-world action game by Rockstar."},
    {"title": "FIFA 23", "platforms": ["PC", "PS", "Xbox"], "description": "Soccer simulation with realistic gameplay."},
    {"title": "Minecraft", "platforms": ["PC", "Mobile", "Xbox", "PS"], "description": "Block-building sandbox adventure."},
    {"title": "The Witcher 3 Wild Hunt", "platforms": ["PC", "PS", "Xbox", "Switch"], "description": "Story-driven fantasy RPG."},
    {"title": "Half-Life 2 Episode Two", "platforms": ["PC"], "description": "Sci-fi FPS sequel with immersive story."},
    # ... további játékok
]

# --- Segéd függvények ---
def load_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return Template(f.read())

def sanitize_filename(title):
    # kisbetű, szóköz -> aláhúzás
    return "".join(c.lower() if c.isalnum() else "_" for c in title)

def generate_cheats():
    num = random.randint(5, 15)
    cheats = [f"Cheat tip {i+1}" for i in range(num)]
    if num >= 15:
        cheats.append("How to activate cheats: press specific keys as indicated in the game.")
    return cheats

def get_image_path(title):
    # ellenőrzi, hogy létezik-e kép a Picture mappában
    filename = sanitize_filename(title) + ".jpg"
    path = os.path.join(PICTURE_DIR, filename)
    if os.path.exists(path):
        return f"../{PICTURE_DIR}/{filename}"
    else:
        return ""  # placeholder sablon template fogja kezelni

# --- Fő logika ---
def main(num_posts=NUM_POSTS):
    os.makedirs(POSTS_DIR, exist_ok=True)
    template = load_template()

    # Beolvasott már létező posztok
    existing_files = set(os.listdir(POSTS_DIR))

    new_posts = []
    random.shuffle(GAMES)
    for game in GAMES:
        file_name = sanitize_filename(game["title"]) + ".html"
        if file_name in existing_files:
            print(f"Skipping '{game['title']}' (already exists).")
            continue

        post_path = os.path.join(POSTS_DIR, file_name)

        # Cheats & Tips
        cheats_list = generate_cheats()

        # AI Rating random
        ai_rating = round(random.uniform(3.0, 5.0), 1)

        # Affiliate link példa (később API-val bővíthető)
        affiliate_links = [
            {"name": "Honeygain", "url": "https://r.honeygain.me/NAGYT86DD6"},
            {"name": "IC Markets", "url": "https://icmarkets.com/?camp=3992"},
            {"name": "Dukascopy", "url": "https://www.dukascopy.com/api/es/12831/type-S/target-id-149"}
        ]

        # Generálás sablon alapján
        html = template.render(
            title=game["title"],
            date=datetime.datetime.now().strftime("%Y-%m-%d"),
            platforms=", ".join(game["platforms"]),
            description=game["description"],
            cheats_list=cheats_list,
            ai_rating=ai_rating,
            image=get_image_path(game["title"]),
            affiliate_links=affiliate_links
        )

        with open(post_path, "w", encoding="utf-8") as f:
            f.write(html)

        new_posts.append(file_name)
        print(f"Generated post: {post_path}")

        if len(new_posts) >= num_posts:
            break

    print(f"✅ Generated {len(new_posts)} new posts.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=NUM_POSTS)
    args = parser.parse_args()
    main(args.num_posts)
