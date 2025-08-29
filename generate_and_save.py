import os
import json
import datetime
from pathlib import Path

# --- Beállítások ---
POSTS_FILE = "posts.json"
GENERATED_DIR = "generated_posts"
PICTURE_DIR = "Picture"

# Mappák létrehozása, ha nem léteznek
os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(PICTURE_DIR, exist_ok=True)

# Affiliate blokkok (minden poszt végére bekerül)
AFFILIATE_HTML = """
<hr>
<section>
  <h3>Sponsored</h3>
  <p><a href="https://r.honeygain.me/NAGYT86DD6" target="_blank">Earn with Honeygain</a></p>
  <p><a href="https://icmarkets.com/?camp=3992" target="_blank">Trade with IC Markets</a></p>
  <p><a href="https://www.dukascopy.com/api/es/12831/type-S/target-id-149" target="_blank">Bank with Dukascopy</a></p>
</section>
"""

def load_posts():
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_posts(posts):
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

def safe_filename(title: str) -> str:
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in title)

def add_post(title, content, platform, rating, cover_image_path=None):
    posts = load_posts()

    safe_title = safe_filename(title)
    date_str = datetime.date.today().isoformat()
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # HTML fájl neve
    html_filename = f"{timestamp}-{safe_title}.html"
    html_path = os.path.join(GENERATED_DIR, html_filename)

    # Cover kép mentése, ha van
    cover_rel_path = ""
    if cover_image_path and os.path.exists(cover_image_path):
        ext = os.path.splitext(cover_image_path)[1].lower()
        cover_rel_path = f"{PICTURE_DIR}/{safe_title}{ext}"
        cover_abs_path = os.path.join(cover_rel_path)
        with open(cover_image_path, "rb") as src, open(cover_abs_path, "wb") as dst:
            dst.write(src.read())

    # Új bejegyzés dict
    new_post = {
        "title": title,
        "url": f"{GENERATED_DIR}/{html_filename}",
        "platform": platform,
        "date": date_str,
        "rating": rating,
        "cover": cover_rel_path,
        "views": 0,
        "comments": 0
    }
    posts.append(new_post)
    save_posts(posts)

    # HTML fájl írása
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title} – AI Gaming Blog</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{
      font-family: Arial, sans-serif;
      background: #0b0f14;
      color: #eaf1f8;
      max-width: 800px;
      margin: auto;
      padding: 20px;
    }}
    img {{
      max-width: 100%;
      border-radius: 12px;
      margin: 16px 0;
    }}
    h1 {{ color: #5cc8ff; }}
    a {{ color: #5cc8ff; }}
    section {{
      margin-top: 32px;
      padding: 16px;
      border: 1px solid #1f2a38;
      border-radius: 12px;
      background: #121821;
    }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  {"<img src='../" + cover_rel_path + "' alt='" + title + "'>" if cover_rel_path else ""}
  <article>
    {content}
  </article>
  {AFFILIATE_HTML}
  <p><a href="../index.html">← Back to Home</a></p>
</body>
</html>
""")

    print(f"Post added: {title}")

# Példa hívás
if __name__ == "__main__":
    add_post(
        title="GTA V",
        content="<p>Review of GTA V with gameplay impressions...</p>",
        platform=["PC", "PS", "Xbox"],
        rating=4.6,
        cover_image_path="sample.jpg"  # ha nincs, hagyd None
    )
