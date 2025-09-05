import os
import requests
import random
from datetime import datetime

# ===============================
# Konfigurációk
# ===============================
RAWG_API_KEY = "ide_kerül_az_api_kulcsod"  # Ha van API kulcsod
RAWG_PAGE_SIZE = 20  # hány játékot kérünk le egyszerre
OUTPUT_DIR = "generated_posts"
PICTURE_DIR = "Picture"
USER_AGENT = "Mozilla/5.0"

# Mappák ellenőrzése
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PICTURE_DIR, exist_ok=True)

# ===============================
# RAWG API véletlenszerű játék lekérés
# ===============================
def rawg_search_random(page=1, page_size=RAWG_PAGE_SIZE):
    url = f"https://api.rawg.io/api/games?page={page}&page_size={page_size}&key={RAWG_API_KEY}"
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data.get("results", [])

# ===============================
# Poszt mentése HTML-be
# ===============================
def save_post(game):
    title = game.get("name", "Név nélkül")
    description = game.get("description_raw", "Nincs leírás")
    image_url = game.get("background_image")

    # Kép letöltés
    image_filename = None
    if image_url:
        ext = os.path.splitext(image_url)[-1]
        image_filename = os.path.join(PICTURE_DIR, f"{title[:20].replace(' ', '_')}{ext}")
        try:
            r = requests.get(image_url, headers={"User-Agent": USER_AGENT})
            with open(image_filename, "wb") as f:
                f.write(r.content)
        except Exception as e:
            print(f"⚠️ Hiba kép letöltésénél: {e}")
            image_filename = None

    # HTML fájl mentése
    safe_title = title.replace(" ", "_")[:30]
    filename = os.path.join(OUTPUT_DIR, f"{safe_title}.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"<h1>{title}</h1>\n")
        f.write(f"<p>{description}</p>\n")
        if image_filename:
            f.write(f"<img src='../{PICTURE_DIR}/{os.path.basename(image_filename)}' alt='{title}'>\n")
    print(f"✅ Poszt mentve: {filename}")

# ===============================
# Több poszt generálása
# ===============================
def generate_posts(num_posts=4):
    page = 1
    count = 0
    while count < num_posts:
        try:
            games = rawg_search_random(page=page)
            if not games:
                print("⚠️ Nincs több játék az API-tól.")
                break
            for game in games:
                if count >= num_posts:
                    break
                save_post(game)
                count += 1
            page += 1
        except Exception as e:
            print(f"⚠️ Hiba poszt generálásánál: {e}")
            break

# ===============================
# Fő
# ===============================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=4, help="Hány posztot generáljon")
    args = parser.parse_args()

    print(f"🔹 Posztok generálása: {args.num_posts} db")
    generate_posts(args.num_posts)
    print("✅ Poszt generálás kész!")
