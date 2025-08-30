import json
import os
from datetime import datetime

# Paths
TEMPLATE_PATH = "templates/index_template.html"
OUTPUT_PATH = "index.html"
GENERATED_POSTS_DIR = "generated_posts"

# Beolvassuk az összes generált post adatát
posts = []

for filename in os.listdir(GENERATED_POSTS_DIR):
    if filename.endswith(".html"):
        filepath = os.path.join(GENERATED_POSTS_DIR, filename)
        # Feltételezzük, hogy minden post file-nál van egy metadata rész JSON-ben vagy
        # a file nevéből generáljuk az adatokat
        title = filename.replace(".html", "").replace("_", " ").title()
        url = os.path.join(GENERATED_POSTS_DIR, filename).replace("\\", "/")
        cover_name = filename.replace(".html", ".jpg")
        cover = f"Picture/{cover_name}"
        # Alapadatok, később módosíthatók
        post_data = {
            "title": title,
            "url": url,
            "platform": ["PC", "PS", "Xbox"],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "rating": round(3 + 2 * os.urandom(1)[0] / 255, 1),  # random 3-5
            "cover": cover,
            "views": 0,
            "comments": 0
        }
        posts.append(post_data)

# Sort by date descending
posts.sort(key=lambda x: x["date"], reverse=True)

# Beolvassuk a template HTML-t
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template_html = f.read()

# Generáljuk a POSTS tömb JSON formátumban
posts_json = json.dumps(posts, indent=2)

# Cseréljük ki a POSTS tömböt a template-ben
import re
pattern = r'// <<< AUTO-GENERATED POSTS START >>>.*// <<< AUTO-GENERATED POSTS END >>>'
replacement = f'// <<< AUTO-GENERATED POSTS START >>>\n    const POSTS = {posts_json};\n    // <<< AUTO-GENERATED POSTS END >>>'
updated_html = re.sub(pattern, replacement, template_html, flags=re.DOTALL)

# Kiírjuk az index.html-t
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(updated_html)

print(f"✅ {OUTPUT_PATH} frissítve {len(posts)} poszttal.")
