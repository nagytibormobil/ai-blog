import os
import re
import json
import random
import datetime
from pathlib import Path

import requests

# ========= Paths / Settings =========
BASE_DIR = Path(r"C:\ai_blog")
PICTURE_DIR = BASE_DIR / "Picture"
POST_DIR = BASE_DIR / "generated_posts"
TEMPLATE_FILE = BASE_DIR / "templates" / "post_template.html"
INDEX_FILE = BASE_DIR / "index.html"

RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"  # only this, as requested
RAWG_LIST_URL = "https://api.rawg.io/api/games"

# ========= Helpers =========
def slug_kebab(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "game"

def star_rating() -> float:
    return round(random.uniform(3.0, 5.0), 1)

CHEATS_POOL = [
    "God Mode", "Infinite Ammo", "Unlimited Money", "No Clip", "Unlock All Levels",
    "Max Stats", "Spawn Vehicle", "One-Hit Kill", "Invisibility", "Infinite Stamina",
    "Max Resources", "Fast Travel Anywhere", "Disable Police/Aggro", "Super Jump", "Bullet Time",
    "Weather Control", "Unlock All Cosmetics", "Free Crafting", "Fly Mode", "Freeze Time"
]

def ensure_dirs():
    PICTURE_DIR.mkdir(parents=True, exist_ok=True)
    POST_DIR.mkdir(parents=True, exist_ok=True)

def fetch_popular_games(page_size=40):
    params = {"key": RAWG_API_KEY, "page_size": page_size, "ordering": "-rating"}
    r = requests.get(RAWG_LIST_URL, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    return data.get("results", [])

def download_image(img_url: str, dest: Path):
    try:
        if not img_url:
            raise ValueError("No image url")
        resp = requests.get(img_url, timeout=30)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        return True
    except Exception:
        # Fallback placeholder (saved locally as jpg)
        try:
            ph = f"https://placehold.co/800x450/jpg?text={dest.stem.replace('-', '+')}"
            resp = requests.get(ph, timeout=15)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
            return True
        except Exception:
            return False

def render_template(context: dict) -> str:
    tpl = TEMPLATE_FILE.read_text(encoding="utf-8")
    # build cheats HTML
    cheats = context.get("cheats", [])[:15]
    cheats_html = "".join(f"<li>{c}</li>" for c in cheats)
    html = (
        tpl.replace("{{title}}", context["title"])
           .replace("{{short_description}}", context["short_description"])
           .replace("{{about}}", context["about"])
           .replace("{{rating}}", f"{context['rating']}")
           .replace("{{image}}", context["image"])
           .replace("{{cheats}}", cheats_html)
           .replace("{{extra_cheats_instruction}}", context["extra_cheats_instruction"])
           .replace("{{year}}", str(context["year"]))
           .replace("{{date_iso}}", context["date_iso"])
    )
    return html

def parse_posts_from_index(index_text: str):
    # Extract JSON between AUTO-GENERATED markers
    start_tag = "AUTO-GENERATED POSTS START"
    end_tag = "AUTO-GENERATED POSTS END"
    start_idx = index_text.find(start_tag)
    end_idx = index_text.find(end_tag)
    if start_idx == -1 or end_idx == -1:
        return [], None, None
    # find "const POSTS = [ ... ]"
    const_idx = index_text.find("const POSTS =", start_idx)
    if const_idx == -1:
        return [], None, None
    open_br = index_text.find("[", const_idx)
    close_br = index_text.find("];", open_br)
    if open_br == -1 or close_br == -1 or close_br < open_br:
        return [], None, None
    json_text = index_text[open_br:close_br+1]
    try:
        posts = json.loads(json_text)
    except Exception:
        posts = []
    return posts, open_br, close_br+2  # slice bounds for replacement

def write_posts_to_index(index_text: str, posts: list, start: int, end: int):
    new_json = json.dumps(posts, indent=2, ensure_ascii=False)
    return index_text[:start] + new_json + index_text[end:]

# ========= Core generation =========
def build_context_from_rawg(game: dict):
    title = game.get("name", "Unknown Game")
    slug = slug_kebab(title)
    img_name = f"{slug}.jpg"
    short_desc = f"{title} – popular action/adventure title. This post covers gameplay impressions, graphics, tips and cheat ideas."
    about = (
        f"<p><strong>{title}</strong> blends engaging gameplay loops with satisfying progression. "
        f"This review looks at controls, combat systems, world design and performance on modern hardware.</p>"
        f"<p>We discuss recommended settings, difficulty options, and strategies for both casual and veteran players. "
        f"Expect stability notes and quality-of-life tweaks that improve the overall experience.</p>"
        f"<p>Below you'll also find practical cheat-style tips to experiment with the sandbox – use responsibly.</p>"
    )
    rating = star_rating()
    tips = random.sample(CHEATS_POOL, k=min(15, max(8, random.randint(8, 15))))
    extra = "Open the in-game console (often the `~` key) or a trainer menu. Cheats may disable achievements; use at your own risk."

    return {
        "title": title,
        "slug": slug,
        "image": img_name,
        "short_description": short_desc,
        "about": about,
        "rating": rating,
        "cheats": tips,
        "extra_cheats_instruction": extra,
        "year": datetime.datetime.now().year,
        "date_iso": datetime.datetime.now().strftime("%Y-%m-%d")
    }

def generate_posts(num_posts: int = 4):
    ensure_dirs()

    # load index current posts for duplicate check
    index_text = INDEX_FILE.read_text(encoding="utf-8")
    current_posts, s, e = parse_posts_from_index(index_text)
    existing_urls = {p.get("url","") for p in current_posts}
    existing_slugs = {Path(p.get("url","")).stem for p in current_posts}

    rawg_games = fetch_popular_games(page_size=60)
    random.shuffle(rawg_games)

    new_posts_meta = []
    generated = 0

    for g in rawg_games:
        if generated >= num_posts:
            break

        ctx = build_context_from_rawg(g)
        slug = ctx["slug"]

        html_path = POST_DIR / f"{slug}.html"
        img_path = PICTURE_DIR / f"{slug}.jpg"

        # Skip duplicates if file exists or already in index
        if html_path.exists() or slug in existing_slugs:
            continue

        # Download image
        bg = g.get("background_image") or ""
        ok_img = download_image(bg, img_path)

        # Render HTML
        html = render_template(ctx)
        html_path.write_text(html, encoding="utf-8")

        # Prepare index meta (relative paths for root index.html)
        platforms = []
        for pl in g.get("platforms", []):
            name = pl.get("platform", {}).get("name")
            if name:
                platforms.append(name)

        meta = {
            "title": ctx["title"],
            "url": f"generated_posts/{slug}.html",
            "platform": platforms or ["PC","PS","Xbox"],
            "date": ctx["date_iso"],
            "rating": ctx["rating"],
            "cover": f"Picture/{slug}.jpg",
            "views": 0,
            "comments": 0
        }

        # prevent dup by URL
        if meta["url"] not in existing_urls:
            new_posts_meta.append(meta)
            existing_urls.add(meta["url"])
            existing_slugs.add(slug)
            generated += 1
            print(f"Generated post: {html_path}")

    # Update index.html POSTS array (append, don't delete older)
    if new_posts_meta and s is not None and e is not None:
        updated = current_posts + new_posts_meta
        # optional: keep only last N=60 to avoid huge file
        if len(updated) > 60:
            updated = updated[-60:]
        index_text2 = write_posts_to_index(index_text, updated, s, e)
        INDEX_FILE.write_text(index_text2, encoding="utf-8")
        print("Updated index.html")
    else:
        print("No index update (no new posts or markers missing).")

def main():
    # how many per run – your batch file may call it multiple times
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--num_posts", type=int, default=4)
    args = ap.parse_args()
    generate_posts(args.num_posts)

if __name__ == "__main__":
    main()
