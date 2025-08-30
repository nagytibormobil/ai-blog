import os
import random
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# --- PATHOK ---
BASE_DIR = r"C:\ai_blog"
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
GENERATED_POSTS_DIR = os.path.join(BASE_DIR, "generated_posts")
PICTURE_DIR = os.path.join(BASE_DIR, "Picture")

# API KEY RAWG.IO
RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"
RAWG_URL = "https://api.rawg.io/api/games"

# --- SEGÉDFÜGGVÉNYEK ---

def get_game_data():
    """Lekér egy random népszerű játékot RAWG API-ról"""
    page = random.randint(1, 50)
    params = {"key": RAWG_API_KEY, "page": page, "page_size": 1}
    r = requests.get(RAWG_URL, params=params)
    r.raise_for_status()
    data = r.json()["results"][0]
    return {
        "title": data["name"],
        "about": f"{data['name']} is a {data.get('genres',[{'name':'game'}])[0]['name']} game released on {data.get('released','N/A')}.",
        "image_url": data["background_image"]
    }

def download_image(image_url, title):
    """Kép letöltése a Picture mappába"""
    if not os.path.exists(PICTURE_DIR):
        os.makedirs(PICTURE_DIR)

    safe_name = title.lower().replace(" ", "_").replace(":", "") + ".jpg"
    image_path = os.path.join(PICTURE_DIR, safe_name)

    if not os.path.exists(image_path):  # csak akkor töltsük le, ha nincs meg
        img_data = requests.get(image_url).content
        with open(image_path, "wb") as f:
            f.write(img_data)

    return safe_name  # relatív név kell majd a HTML-hez

def load_template(template_name):
    with open(os.path.join(TEMPLATES_DIR, template_name), "r", encoding="utf-8") as f:
        return f.read()

def save_html(content, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

# --- POSZT GENERÁLÁSA ---

def generate_post():
    game = get_game_data()

    # kép letöltése
    image_file = download_image(game["image_url"], game["title"])

    # review + cheats dummy tartalom
    review = f"{game['title']} offers an immersive experience with dynamic gameplay and exciting features."
    cheats = "".join([f"<li>Cheat tip {i}</li>" for i in range(1, random.randint(3, 15))])
    rating = round(random.uniform(3.0, 5.0), 1)

    # post sablon betöltése
    template = load_template("post_template.html")

    html = (
        template.replace("{{TITLE}}", game["title"])
        .replace("{{ABOUT}}", game["about"])
        .replace("{{REVIEW}}", review)
        .replace("{{CHEATS}}", cheats)
        .replace("{{IMAGE}}", image_file)
        .replace("{{RATING}}", str(rating))
    )

    # fájlnév
    safe_name = game["title"].lower().replace(" ", "_").replace(":", "")
    filename = os.path.join(GENERATED_POSTS_DIR, f"{safe_name}.html")

    # ha már létezik, ne írjuk felül → keresünk másik játékot
    if os.path.exists(filename):
        print(f"Skipping '{game['title']}' (already exists).")
        return None

    save_html(html, filename)
    print(f"Generated post: {filename}")
    return {"title": game["title"], "file": filename, "image": image_file}

# --- INDEX FRISSÍTÉSE ---

def update_index(posts):
    index_template = load_template("index_template.html")

    posts_html = ""
    for post in posts:
        posts_html += f"""
        <article>
            <h3><a href="generated_posts/{os.path.basename(post['file'])}">{post['title']}</a></h3>
            <img src="Picture/{post['image']}" alt="{post['title']} image">
        </article>
        """

    final_html = index_template.replace("<!-- POSTS_BLOCK -->", posts_html)

    save_html(final_html, os.path.join(BASE_DIR, "index.html"))
    print("Updated index.html")

# --- FŐ FOLYAMAT ---

def main(num_posts=3):
    if not os.path.exists(GENERATED_POSTS_DIR):
        os.makedirs(GENERATED_POSTS_DIR)

    new_posts = []
    for _ in range(num_posts):
        post = generate_post()
        if post:
            new_posts.append(post)

    if new_posts:
        update_index(new_posts)

if __name__ == "__main__":
    main(num_posts=5)
