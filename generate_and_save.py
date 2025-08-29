# generate_and_save.py
# -*- coding: utf-8 -*-
import os
import re
import json
import time
import random
import argparse
import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# =========================
# ÁLLANDÓK / BEÁLLÍTÁSOK
# =========================
ROOT_DIR     = Path(__file__).resolve().parent
OUTPUT_DIR   = ROOT_DIR / "generated_posts"
PICTURE_DIR  = ROOT_DIR / "Picture"
INDEX_FILE   = ROOT_DIR / "index.html"
POSTS_JSON   = ROOT_DIR / "posts.json"

# API kulcsok
RAWG_API_KEY     = "2fafa16ea4c147438f3b0cb031f8dbb7"
YOUTUBE_API_KEY  = "AIzaSyAXedHcSZ4zUaqSaD3MFahLz75IvSmxggM"

# Biztonság kedvéért mappák létrehozása
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PICTURE_DIR.mkdir(parents=True, exist_ok=True)

# Alap játéklista (ha kifogyunk, RAWG-ból pótoljuk)
BASE_GAMES = [
    {"name": "Elden Ring", "platforms": ["PC","PS","Xbox"], "year": 2022, "publisher": "FromSoftware", "version": "1.09"},
    {"name": "GTA V", "platforms": ["PC","PS","Xbox"], "year": 2013, "publisher": "Rockstar Games", "version": "Latest"},
    {"name": "The Witcher 3: Wild Hunt", "platforms": ["PC","PS","Xbox","Switch"], "year": 2015, "publisher": "CD Projekt Red", "version": "Next-Gen"},
    {"name": "Minecraft", "platforms": ["PC","Mobile","Xbox","PS"], "year": 2011, "publisher": "Mojang", "version": "1.20"},
    {"name": "Fortnite", "platforms": ["PC","PS","Xbox","Mobile"], "year": 2017, "publisher": "Epic Games", "version": "Chapter 4"},
    {"name": "Call of Duty: Modern Warfare II", "platforms": ["PC","PS","Xbox"], "year": 2022, "publisher": "Activision", "version": "1.0"},
    {"name": "League of Legends", "platforms": ["PC"], "year": 2009, "publisher": "Riot Games", "version": "13.8"},
    {"name": "FIFA 23", "platforms": ["PC","PS","Xbox"], "year": 2022, "publisher": "EA Sports", "version": "Final"},
]

CHEATS_EXAMPLES = [
    "God Mode: IDDQD",
    "Infinite Ammo: GIVEALL",
    "Unlock All Levels: LEVELUP",
    "Max Money: RICHGUY",
    "No Clip Mode: NOCLIP",
    "Infinite Stamina: RUNFOREVER",
    "One-Hit Kill: SMASH"
]

AFFILIATE_HTML = """
<hr>
<section>
  <div style="background:linear-gradient(180deg,rgba(255,209,102,.12),transparent);border:1px dashed #ffd166;padding:16px;border-radius:14px">
    <h3>Earn Real Money While You Play 📱</h3>
    <p>Simple passive income by sharing a bit of your internet. Runs in the background while you game.</p>
    <p><a href="https://r.honeygain.me/NAGYT86DD6" target="_blank"><strong>Try Honeygain now</strong></a></p>
    <div style="font-size:12px;color:#9fb0c3">Sponsored. Use at your own discretion.</div>
  </div>
  <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:12px">
    <div style="flex:1 1 320px;background:#0f141c;border:1px solid #1f2a38;padding:16px;border-radius:14px">
      <h3>IC Markets – Trade like a pro 🌍</h3>
      <p><a href="https://icmarkets.com/?camp=3992" target="_blank">Open an account</a></p>
    </div>
    <div style="flex:1 1 320px;background:#0f141c;border:1px solid #1f2a38;padding:16px;border-radius:14px">
      <h3>Dukascopy – Promo code: <code>E12831</code> 🏦</h3>
      <p><a href="https://www.dukascopy.com/api/es/12831/type-S/target-id-149" target="_blank">Start here</a></p>
    </div>
  </div>
</section>
"""

# =========================
# SEGÉDFÜGGVÉNYEK
# =========================
def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "game"

def load_posts_manifest():
    if POSTS_JSON.exists():
        try:
            with open(POSTS_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_posts_manifest(posts):
    # Egyértelmű sorrend: dátum szerint csökkenő
    posts_sorted = sorted(posts, key=lambda p: p.get("date",""), reverse=True)
    with open(POSTS_JSON, "w", encoding="utf-8") as f:
        json.dump(posts_sorted, f, ensure_ascii=False, indent=2)

def unique_by_slug(posts):
    seen = set()
    out = []
    for p in posts:
        slug = p.get("slug") or slugify(p.get("title",""))
        if slug not in seen:
            seen.add(slug)
            p["slug"] = slug
            out.append(p)
    return out

def fetch_rawg_games(need_count=20):
    """Top játékok lekérése RAWG-ból, hogy legyen utánpótlás."""
    url = "https://api.rawg.io/api/games"
    params = {
        "key": RAWG_API_KEY,
        "page_size": min(need_count, 40),
        "ordering": "-rating"
    }
    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        games = []
        for g in data.get("results", []):
            name = g.get("name") or "Unknown Game"
            # platformok tömörítése
            plats = []
            for pp in (g.get("parent_platforms") or []):
                n = (pp.get("platform") or {}).get("name")
                if n: plats.append(n)
            year = (g.get("released") or "2000-01-01")[:4]
            games.append({
                "name": name,
                "platforms": plats or ["PC"],
                "year": int(year) if year.isdigit() else 2000,
                "publisher": "Unknown",
                "version": "1.0"
            })
        return games
    except Exception:
        return []

def ensure_cover_image(game_name: str) -> str:
    """
    Kép biztosítása a Picture mappában SEO-barát névvel.
    1) ha létezik: használjuk
    2) ha nem, RAWG keresés -> background_image letöltés
    3) ha az sem sikerül: placehold.co mentése
    Visszatér: relatív webes útvonal (Picture/slug.jpg)
    """
    slug = slugify(game_name)
    filename = f"{slug}.jpg"
    local_path = PICTURE_DIR / filename
    if local_path.exists() and local_path.stat().st_size > 1000:
        return f"Picture/{filename}"

    # Próbáljuk RAWG kereséssel
    try:
        s_url = "https://api.rawg.io/api/games"
        params = {"search": game_name, "key": RAWG_API_KEY, "page_size": 1}
        r = requests.get(s_url, params=params, timeout=20)
        img = None
        if r.ok:
            items = r.json().get("results", [])
            if items:
                img = items[0].get("background_image")
        if img:
            img_resp = requests.get(img, timeout=20)
            if img_resp.ok:
                with open(local_path, "wb") as f:
                    f.write(img_resp.content)
                return f"Picture/{filename}"
    except Exception:
        pass

    # Fallback placeholder (de lokálisan is mentsük el!)
    try:
        ph = f"https://placehold.co/800x450?text={requests.utils.quote(game_name)}"
        ph_resp = requests.get(ph, timeout=20)
        if ph_resp.ok:
            with open(local_path, "wb") as f:
                f.write(ph_resp.content)
    except Exception:
        # végső fallback: üres fájl helyett inkább kihagyjuk – de relatív elérési út akkor is kell
        local_path.touch()

    return f"Picture/{filename}"

def fetch_youtube_embed(game_name: str) -> str:
    """YouTube keresés a legrelevánsabb gameplay videóra."""
    try:
        q = f"{game_name} gameplay"
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": q,
            "key": YOUTUBE_API_KEY,
            "type": "video",
            "maxResults": 1,
            "safeSearch": "moderate"
        }
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        items = r.json().get("items", [])
        if items:
            vid = items[0]["id"]["videoId"]
            return f"https://www.youtube.com/embed/{vid}"
    except Exception:
        pass
    # fallback
    return "https://www.youtube.com/embed/dQw4w9WgXcQ"

def build_post_html(game, cover_rel, youtube_url, rating, now_iso, slug) -> str:
    title = f"{game['name']} Review & Guide"
    desc  = f"Review, cheats, and gameplay tips for {game['name']}."
    year  = game.get("year") or ""
    publisher = game.get("publisher") or "Unknown"
    version = game.get("version") or "1.0"
    platforms = ", ".join(game.get("platforms") or [])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>{title}</title>
  <meta name="description" content="{desc}"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <link rel="canonical" href="../generated_posts/{slug}.html"/>
  <meta property="og:title" content="{title}"/>
  <meta property="og:description" content="{desc}"/>
  <meta property="og:type" content="article"/>
  <meta property="og:image" content="../{cover_rel}"/>
  <meta property="article:published_time" content="{now_iso}"/>
  <style>
    body{{font-family:Arial, sans-serif; max-width:900px; margin:0 auto; line-height:1.6; padding:20px; background:#0b0f14; color:#eaf1f8}}
    a{{color:#5cc8ff}}
    img{{border-radius:8px}}
    .btn{{display:inline-block;padding:10px 14px;border:1px solid #1f2a38;border-radius:10px;background:#0f141c;text-decoration:none;margin:10px 0}}
    .meta{{font-size:12px;color:#9fb0c3}}
    ul{{padding-left:20px}}
    hr{{border:0;border-top:1px solid #1f2a38;margin:24px 0}}
  </style>
</head>
<body>
  <a class="btn" href="../index.html">⬅ Back to Home</a>
  <h1>{game['name']}</h1>
  <img src="../{cover_rel}" alt="{game['name']} gameplay cover" style="width:100%; aspect-ratio:16/9; object-fit:cover;"/>
  <p class="meta">Published: {now_iso.split('T')[0]} • Platforms: {platforms} • Version: {version}</p>

  <h2>About the Game</h2>
  <ul>
    <li><strong>Release Year:</strong> {year}</li>
    <li><strong>Publisher:</strong> {publisher}</li>
    <li><strong>Platforms:</strong> {platforms}</li>
    <li><strong>Offline:</strong> {random.choice(['Yes','No'])}</li>
    <li><strong>Multiplayer:</strong> {random.choice(['Yes','No'])}</li>
  </ul>

  <h2>Full Review</h2>
  <p><strong>{game['name']}</strong> focuses on its own strengths: mechanics, pacing and the core loop that keeps players coming back.
  Below you’ll find practical, game-specific tips (combat, builds, progression) instead of generic filler. We keep it short and actionable.</p>

  <h3>Key Tips</h3>
  <ul>
    <li>Progression: identify early-game bottlenecks and unlock core systems quickly.</li>
    <li>Combat: leverage the game’s unique mechanics (parry/aim/timing/skill synergy) against tough encounters.</li>
    <li>Economy: spend resources on long-term upgrades first; avoid waste on low-impact items.</li>
    <li>Exploration: check high-value POI routes; revisit areas after gear spikes.</li>
  </ul>

  <h2>Gameplay Video</h2>
  <iframe width="100%" height="420" src="{youtube_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

  <h2>Cheats & Tips</h2>
  <ul>
    {''.join(f"<li>{c}</li>" for c in random.sample(CHEATS_EXAMPLES, k=3))}
  </ul>

  <h2>AI Rating</h2>
  <p>⭐ {rating:.1f}/5</p>

  {AFFILIATE_HTML}

  <hr>
  <footer style="font-size:12px; color:#9fb0c3">
    <p><strong>Comment Policy:</strong> No spam, ads, offensive language, or disallowed topics (adult, drugs, war, terrorism). Max 10 comments/day. All comments are moderated.</p>
    <p><strong>Terms:</strong> Informational purposes only. Trademarks belong to their owners. Affiliate links may generate commission.</p>
    <p>© {datetime.datetime.now().year} AI Gaming Blog</p>
  </footer>
</body>
</html>
"""

def write_post(game):
    """Egy poszt generálása + fájl írása. Visszaad: poszt meta dict."""
    now = datetime.datetime.now()
    now_iso = now.isoformat(timespec="seconds")
    slug = slugify(game["name"])

    # fájlnév: YYYYmmdd-HHMMSS-slug.html
    filename = f"{now.strftime('%Y%m%d-%H%M%S')}-{slug}.html"
    filepath = OUTPUT_DIR / filename

    # borítókép és youtube
    cover_rel = ensure_cover_image(game["name"])
    youtube_url = fetch_youtube_embed(game["name"])
    rating = round(random.uniform(2.8, 5.0), 1)

    html = build_post_html(game, cover_rel, youtube_url, rating, now_iso, slug)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return {
        "title": game["name"],
        "slug": slug,
        "url": f"generated_posts/{filename}".replace("\\","/"),
        "platform": game.get("platforms") or [],
        "date": now.strftime("%Y-%m-%d"),
        "rating": rating,
        "cover": cover_rel,  # relatív: Picture/slug.jpg
        "views": 0,
        "comments": 0
    }

def append_affiliate_if_missing(html_path: Path):
    """Régi posztokhoz is illessze be az affiliate blokkot, ha hiányzik."""
    try:
        txt = html_path.read_text(encoding="utf-8")
    except Exception:
        return
    if "Earn Real Money While You Play" in txt:
        return  # már benne van
    # beszúrjuk a </body> elé
    new_txt = txt.replace("</body>", f"{AFFILIATE_HTML}\n</body>")
    try:
        html_path.write_text(new_txt, encoding="utf-8")
    except Exception:
        pass

def update_index_with_posts(all_posts):
    """index.html-ben a marker között lecseréli a POSTS tömböt MINDEN posztra."""
    if not INDEX_FILE.exists():
        print("index.html NEM található – kihagyva.")
        return
    html = INDEX_FILE.read_text(encoding="utf-8")

    posts_json = json.dumps(all_posts, ensure_ascii=False, indent=2)
    pattern = r"(// <<< AUTO-GENERATED POSTS START >>>)(.|\s)*(// <<< AUTO-GENERATED POSTS END >>>)"
    repl = r"\1\n    const POSTS = " + posts_json + r";\n    \3"
    new_html = re.sub(pattern, repl, html, flags=re.MULTILINE)

    INDEX_FILE.write_text(new_html, encoding="utf-8")

# =========================
# FŐ LOGIKA
# =========================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=12, help="Hány új poszt készüljön (alapértelmezett: 12)")
    args = parser.parse_args()

    # 1) eddigi posztok betöltése (manifest)
    posts = load_posts_manifest()
    posts = unique_by_slug(posts)
    existing_slugs = {p["slug"] for p in posts}

    # 2) legyen elegendő játék a poolban
    pool = BASE_GAMES[:]
    # egészítsük ki RAWG top játékokkal, hogy biztosan legyen mit generálni
    if len(pool) < args.num_posts * 2:
        pool.extend(fetch_rawg_games(need_count=args.num_posts * 3))

    # 3) válasszunk pontosan 12 OLYAN játékot, ami még nincs meg slug alapján
    random.shuffle(pool)
    to_make = []
    for g in pool:
        slug = slugify(g["name"])
        if slug not in existing_slugs and slug not in {slugify(x["name"]) for x in to_make}:
            to_make.append(g)
        if len(to_make) >= args.num_posts:
            break

    # ha még mindig kevés, próbáljunk még RAWG-ból húzni
    tries = 0
    while len(to_make) < args.num_posts and tries < 3:
        more = fetch_rawg_games(need_count=args.num_posts * 2)
        for g in more:
            s = slugify(g["name"])
            if s not in existing_slugs and s not in {slugify(x["name"]) for x in to_make}:
                to_make.append(g)
            if len(to_make) >= args.num_posts:
                break
        tries += 1

    # 4) generáljuk a posztokat
    created = []
    for g in to_make:
        meta = write_post(g)
        created.append(meta)
        print(f"Generated: {meta['title']} → {meta['url']}")

    # 5) affiliate blokk ellenőrzése MINDEN posztnál (régiekre is)
    for p in OUTPUT_DIR.glob("*.html"):
        append_affiliate_if_missing(p)

    # 6) manifest frissítése (újak + régiek, duplikátum nélkül)
    posts.extend(created)
    posts = unique_by_slug(posts)
    # dátum szerint rendezve (újabb elöl)
    posts = sorted(posts, key=lambda p: p.get("date",""), reverse=True)
    save_posts_manifest(posts)

    # 7) index frissítése: a POSTS tömb MINDEN posztot tartalmazni fog
    update_index_with_posts(posts)

    print("index.html updated with all posts.")
    print(f"Total posts in manifest: {len(posts)}")


if __name__ == "__main__":
    main()
