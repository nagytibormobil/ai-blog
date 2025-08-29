import os
import re
import requests
import random
import datetime
from jinja2 import Template

# ============= Beállítások =============
OUTPUT_DIR = "generated_posts"
INDEX_FILE = "index.html"
RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"
YOUTUBE_API_KEY = "AIzaSyAXedHcSZ4zUaqSaD3MFahLz75IvSmxggM"

# Placeholder kép minden játékhoz
PLACEHOLDER_IMAGE = "https://via.placeholder.com/800x400.png?text=Game+Image"

# RAWG API URL
RAWG_URL = "https://api.rawg.io/api/games"

# ========================================

# Slug generáló függvény (biztonságos fájlnevekhez és URL-ekhez)
def slugify(name):
    s = name.lower()
    s = s.replace(":", "").replace("'", "").replace('"', "")
    s = re.sub(r"[^a-z0-9\s-]", "", s)  # csak betű, szám, szóköz, kötőjel
    s = re.sub(r"\s+", "-", s.strip())  # szóköz -> kötőjel
    return s

# YouTube videó keresés
def get_youtube_video(game_name):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"{game_name} trailer",
        "type": "video",
        "key": YOUTUBE_API_KEY,
        "maxResults": 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            return f"https://www.youtube.com/embed/{data['items'][0]['id']['videoId']}"
    return None

# HTML sablon posztokhoz
POST_TEMPLATE = Template("""
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ title }}</h1>
    <img src="{{ image }}" alt="{{ title }}" style="max-width:100%;height:auto;">
    <p>{{ description }}</p>
    {% if youtube %}
    <iframe width="560" height="315" src="{{ youtube }}" frameborder="0" allowfullscreen></iframe>
    {% endif %}
</body>
</html>
""")

# HTML sablon indexhez
INDEX_TEMPLATE = Template("""
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Blog</title>
</head>
<body>
    <h1>AI Blog – Játékposztok</h1>
    <ul>
    {% for post in posts %}
        <li><a href="{{ post.url }}">{{ post.title }}</a></li>
    {% endfor %}
    </ul>
</body>
</html>
""")

# Egy poszt generálása
def generate_post(game):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    slug = slugify(game["name"])
    filename = f"{timestamp}-{slug}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # kép kiválasztása vagy placeholder
    image = game.get("background_image") or PLACEHOLDER_IMAGE

    # YouTube videó lekérése
    youtube_url = get_youtube_video(game["name"])

    # HTML renderelés
    html_content = POST_TEMPLATE.render(
        title=game["name"],
        image=image,
        description=game.get("description_raw", "Nincs leírás."),
        youtube=youtube_url
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    return {
        "title": game["name"],
        "url": f"generated_posts/{filename}"
    }

# Index frissítése
def update_index(posts):
    html_content = INDEX_TEMPLATE.render(posts=posts)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

# Fő folyamat
def main(num_posts=5):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    params = {"key": RAWG_API_KEY, "page_size": num_posts}
    response = requests.get(RAWG_URL, params=params)

    if response.status_code != 200:
        print("Hiba az adatok lekérésekor a RAWG API-ból")
        return

    data = response.json()
    games = data.get("results", [])

    posts = []
    for game in games:
        post_info = generate_post(game)
        posts.append(post_info)
        print(f"Generated: {game['name']} → {post_info['url']}")

    update_index(posts)
    print("index.html updated.")

if __name__ == "__main__":
    main()
