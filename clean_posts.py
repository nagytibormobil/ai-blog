import os
import json

# Könyvtárak
BASE_DIR = r"C:\Users\User\OneDrive\ai_blog"
POST_DIR = os.path.join(BASE_DIR, "generated_posts")
POSTS_JSON = os.path.join(BASE_DIR, "posts.json")

# posts.json betöltése
with open(POSTS_JSON, "r", encoding="utf-8") as f:
    posts = json.load(f)

cleaned_posts = []
removed = []

# Ellenőrzés
for post in posts:
    href = post.get("href", "")
    if href.endswith(".html"):
        filename = os.path.basename(href)
        file_path = os.path.join(POST_DIR, filename)
        if os.path.exists(file_path):
            cleaned_posts.append(post)
        else:
            removed.append(filename)

# Új JSON mentése
with open(POSTS_JSON, "w", encoding="utf-8") as f:
    json.dump(cleaned_posts, f, indent=2, ensure_ascii=False)

print(f"Kész! {len(removed)} hibás bejegyzés törölve a posts.json-ból.")
if removed:
    print("Töröltek:")
    for r in removed:
        print(" -", r)
