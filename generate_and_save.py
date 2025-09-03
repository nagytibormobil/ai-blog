#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_and_save.py
Automatikus poszt-generálás RAWG + YouTube alapján, képek a helyi Picture mappából.
- C:\ai_blog\generated_posts -> ide mentjük a posztokat
- C:\ai_blog\Picture         -> innen vesszük a borítóképeket (nem töltünk le)
- Csak akkor generálunk posztot, ha találunk releváns YouTube videót.
- Egyedi SEO title + meta description.
- Publisher/Developer: ha nincs, nem jelenik meg; age rating külön sor (ha van).
- Cheats: valós parancsok a Source engine / Half-Life 2-hoz. Más játékoknál max 3 célzott tip.
- Affiliate blokkok placeholder URL-lel (#) – később cserélhetők.
- PayPal gomb (USD) a megadott email címhez.
- Kommentszekció: csak szöveg, link/HTML tiltva, helyi tárolás (localStorage).

Előfeltételek: pip install requests beautifulsoup4
"""

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

# ====== Beállítások ======
REPO_ROOT      = r"C:\ai_blog"
OUTPUT_DIR     = os.path.join(REPO_ROOT, "generated_posts")
PICTURE_DIR    = os.path.join(REPO_ROOT, "Picture")
INDEX_FILE     = os.path.join(REPO_ROOT, "index.html")

RAWG_API_KEY   = "2fafa16ea4c147438f3b0cb031f8dbb7"
YOUTUBE_API_KEY= "AIzaSyAXedHcSZ4zUaqSaD3MFahLz75IvSmxggM"

USER_AGENT     = "AI-Gaming-Blog-Agent/2.0"
NUM_TOTAL      = 8          # hány posztot próbáljon generálni futásonként
NUM_POPULAR    = 2
RAWG_PAGE_SIZE = 40

PAYPAL_EMAIL   = "nagytibormobil@gmail.com"
CURRENCY       = "USD"

# ====== Segédfüggvények ======
def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s

def ensure_dirs():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(PICTURE_DIR).mkdir(parents=True, exist_ok=True)

def rawg_fetch(page=1, ordering=None):
    url = "https://api.rawg.io/api/games"
    params = {"key": RAWG_API_KEY, "page": page, "page_size": RAWG_PAGE_SIZE}
    if ordering:
        params["ordering"] = ordering
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json().get("results", [])

def rawg_game_details(game_id: int) -> dict:
    url = f"https://api.rawg.io/api/games/{game_id}"
    params = {"key": RAWG_API_KEY}
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()

def pick_local_image(slug: str) -> str or None:
    """A Picture mappában keres borítóképet a slug alapján."""
    candidates = [
        os.path.join(PICTURE_DIR, f"{slug}.jpg"),
        os.path.join(PICTURE_DIR, f"{slug}.jpeg"),
        os.path.join(PICTURE_DIR, f"{slug}.png"),
        os.path.join(PICTURE_DIR, f"{slug}.webp"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

def youtube_search_embed(game_name: str) -> str or None:
    """YouTube keresés. Relevánsnak akkor vesszük, ha a videó címe tartalmazza a játék nevét (lazán)."""
    if not YOUTUBE_API_KEY:
        return None
    url = "https://www.googleapis.com/youtube/v3/search"
    q = f"{game_name} gameplay"
    params = {
        "part": "snippet",
        "q": q,
        "type": "video",
        "maxResults": 1,
        "key": YOUTUBE_API_KEY,
        "safeSearch": "moderate",
    }
    try:
        r = requests.get(url, params=params, timeout=12)
        r.raise_for_status()
        j = r.json()
        items = j.get("items", [])
        if not items:
            return None
        vid = items[0]["id"]["videoId"]
        title = items[0]["snippet"]["title"].lower()
        # laza relevancia: a játék név bármely fő szava szerepeljen a címben
        tokens = [t for t in re.split(r"[\s:\-\|]+", game_name.lower()) if len(t) > 2]
        if any(tok in title for tok in tokens):
            return f"https://www.youtube.com/embed/{vid}"
        return None
    except Exception:
        return None

def read_index_posts() -> list:
    if not os.path.exists(INDEX_FILE):
        return []
    html = Path(INDEX_FILE).read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"POSTS\s*=\s*(\[\s*[\s\S]*?\])\s*;", html)
    if not m:
        m = re.search(r"POSTS\s*=\s*(\[\s*[\s\S]*?\])", html)
    if not m:
        return []
    arr_text = m.group(1)
    try:
        return json.loads(arr_text)
    except Exception:
        cleaned = re.sub(r",\s*}", "}", arr_text)
        cleaned = re.sub(r",\s*\]", "]", cleaned)
        try:
            return json.loads(cleaned)
        except Exception:
            return []

def write_index_posts(all_posts: list):
    if not os.path.exists(INDEX_FILE):
        print("index.html not found – skipping index update.")
        return
    html = Path(INDEX_FILE).read_text(encoding="utf-8", errors="ignore")
    new_json = json.dumps(all_posts, indent=2, ensure_ascii=False)
    if "// <<< AUTO-GENERATED POSTS START >>>" in html and "// <<< AUTO-GENERATED POSTS END >>>" in html:
        new_html = re.sub(
            r"// <<< AUTO-GENERATED POSTS START >>>[\s\S]*?// <<< AUTO-GENERATED POSTS END >>>",
            f"// <<< AUTO-GENERATED POSTS START >>>\n    const POSTS = {new_json};\n    // <<< AUTO-GENERATED POSTS END >>>",
            html
        )
    else:
        new_html = re.sub(r"POSTS\s*=\s*\[[\s\S]*?\]", f"POSTS = {new_json}", html)
    Path(INDEX_FILE).write_text(new_html, encoding="utf-8")
    print("✅ index.html updated.")

def compose_seo_title(name: str) -> str:
    base = f"{name} Cheats, Console Commands & Tips"
    return (base[:68] + "…") if len(base) > 70 else base

def compose_meta_description(name: str, platforms: list, year: str) -> str:
    plat = ", ".join(platforms) if platforms else "PC & Console"
    desc = f"All working cheats, console commands and quick tips for {name} ({year}) on {plat}. Plus short review and gameplay video."
    return (desc[:156] + "…") if len(desc) > 158 else desc

def extract_age_rating(details: dict) -> str:
    esrb = details.get("esrb_rating", {}) or {}
    if isinstance(esrb, dict) and esrb.get("name"):
        return f"ESRB: {esrb['name']}"
    # RAWG nem mindig ad PEGI-t; ha tags között megtalálható, kiolvashatnánk,
    # de biztonságosan csak az ESRB-t használjuk, ha van.
    return ""

def extract_publishers(details: dict) -> str:
    pubs = details.get("publishers") or []
    names = [p.get("name") for p in pubs if p.get("name")]
    return ", ".join(names)

def extract_developers(details: dict) -> str:
    devs = details.get("developers") or []
    names = [d.get("name") for d in devs if d.get("name")]
    return ", ".join(names)

def short_review_for(details: dict) -> str:
    """Játék-specifikus, rövid (3-5 bekezdés) összefoglaló, spoilermentesen."""
    name = details.get("name") or "The game"
    desc_raw = (details.get("description_raw") or "").strip()
    # Csapjunk le 3-4 fontos aspektusra a leírásból.
    summary = " ".join(desc_raw.split())[:800]
    if not summary:
        summary = f"{name} delivers focused gameplay with memorable set-pieces and solid pacing."
    parts = []
    parts.append(f"<p><strong>{name}</strong> is a story-driven experience with set-piece moments and tight moment-to-moment gameplay. Below you'll find a spoiler-light overview, quick tips, and (where available) console commands.</p>")
    parts.append(f"<p>{summary}</p>")
    # Fő játékelemek
    tags = [t.get("name") for t in (details.get("tags") or []) if t.get("name")]
    if tags:
        parts.append(f"<p><em>Core elements:</em> " + ", ".join(tags[:8]) + ".</p>")
    return "\n".join(parts)

# ====== Cheats & Tips ======
SOURCE_ENGINE_COMMANDS = [
    "sv_cheats 1 – Enable cheat mode",
    "god – God mode (invincible)",
    "noclip – Fly through walls",
    "notarget – Enemies ignore you",
    "impulse 101 – All weapons & ammo",
    "givecurrentammo – Fill ammo for current weapon",
    "buddha – Health never drops below 1",
    "give weapon_ar2 – Spawn AR2",
    "give weapon_shotgun – Spawn shotgun",
    "give weapon_rpg – Spawn RPG",
    "give item_healthkit – Spawn health kit",
    "give item_battery – Spawn suit battery",
    "mat_wireframe 1 – See world wireframe (debug)",
    "thirdperson – Toggle third-person view",
    "npc_create npc_metropolice – Spawn Metro Cop"
][:15]

def game_has_source_cheats(details: dict) -> bool:
    name = (details.get("name") or "").lower()
    slug = (details.get("slug") or "").lower()
    if "half-life 2" in name or slug.startswith("half-life-2"):
        return True
    # Egyes Source játékokra kiterjeszthető:
    for kw in ["episode-one", "episode-two", "lost-coast", "portal", "counter-strike", "garrys-mod"]:
        if kw in slug:
            return True
    return False

def compose_cheats_block(details: dict) -> str:
    if game_has_source_cheats(details):
        items = "".join(f"<li><code>{c}</code></li>" for c in SOURCE_ENGINE_COMMANDS[:15])
        return f"<ul>{items}</ul>"
    # Nincs valós cheat: adjunk legfeljebb 3 célzott tippet
    tips = []
    # Egyszerű, releváns tippek a description alapján
    desc = (details.get("description_raw") or "").lower()
    if "stealth" in desc or "sneak" in desc:
        tips.append("Use stealth routes where possible; watch enemy cone of vision.")
    if "boss" in desc or "arena" in desc:
        tips.append("Before boss fights, stock up on ammo and health kits; learn attack patterns.")
    tips.append("Explore off-path areas for hidden resources and upgrades.")
    tips = tips[:3]
    items = "".join(f"<li>{t}</li>" for t in tips)
    return f"<ul>{items}</ul>"

# ====== Komment szekció (kliensoldali) ======
COMMENT_WIDGET = r"""
<section id="comments" style="margin-top:24px">
  <h2>Comments</h2>
  <p class="tiny">Text only. No links, HTML, images. Max 500 chars. Game-related and respectful.</p>
  <form id="cform" onsubmit="return addComment(event)">
    <textarea id="cbody" rows="4" maxlength="500" placeholder="Share a helpful tip or question..."></textarea>
    <div style="margin-top:8px;display:flex;gap:8px;align-items:center">
      <input id="cname" type="text" placeholder="Name (optional)" style="flex:1">
      <button type="submit">Post comment</button>
    </div>
  </form>
  <ul id="clist" class="list"></ul>
</section>
<script>
(function(){
  const KEY = "comments:" + location.pathname;
  const banned = [/http/i, /www\./i, /<[^>]+>/, /sex|porn|drugs|terror|violence|casino|bet|bitcoin|crypto/i];
  const spammy = [/buy now/i, /free money/i, /work from home/i, /visit my/i, /promo code/i];

  function load(){
    try { return JSON.parse(localStorage.getItem(KEY) || "[]"); } catch(e){ return []; }
  }
  function save(list){
    localStorage.setItem(KEY, JSON.stringify(list.slice(-100)));
  }
  function reject(txt){
    const t = (txt||"").trim();
    if (!t) return "Empty comment";
    if (t.length > 500) return "Too long";
    if (banned.some(rx => rx.test(t))) return "Links/HTML or prohibited words are not allowed";
    if (spammy.some(rx => rx.test(t))) return "Looks like spam/ads – rejected";
    return "";
  }
  window.addComment = function(e){
    e.preventDefault();
    const body = document.getElementById("cbody").value.trim();
    const name = (document.getElementById("cname").value || "Guest").trim().slice(0,40);
    const err = reject(body);
    if (err){ alert(err); return false; }
    const list = load();
    list.push({name, body, ts: Date.now()});
    save(list);
    document.getElementById("cbody").value = "";
    render();
    return false;
  }
  function render(){
    const list = load().slice().reverse();
    const ul = document.getElementById("clist");
    ul.innerHTML = "";
    list.forEach(c=>{
      const li = document.createElement("li");
      const d = new Date(c.ts);
      li.innerHTML = "<strong>"+escapeHtml(c.name)+"</strong> <span class='tiny'>("+d.toLocaleString()+")</span><br>"+escapeHtml(c.body);
      ul.appendChild(li);
    });
  }
  function escapeHtml(s){
    return (s||"").replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  }
  render();
})();
</script>
"""

# ====== Footer ======
def post_footer_html():
    year = datetime.datetime.now().year
    return f"""
<hr>
<section class="ad">
  <h3>Support the site 💖</h3>
  <p>If you enjoy our guides, you can support us via PayPal. Every bit helps us write more!</p>
  <a class="btn" href="https://www.paypal.com/donate?business={PAYPAL_EMAIL}&currency_code={CURRENCY}" target="_blank" rel="nofollow noopener">Donate via PayPal (USD)</a>
</section>

<section class="footer" style="margin-top:18px">
  <div class="tiny">
    <p><strong>Comment Policy</strong>: No spam/ads/offensive content. No adult/drugs/war/terror topics. Max 10 comments/day/person. Be respectful. Text only.</p>
    <p><strong>Terms & Disclaimers</strong>: All content is for informational and entertainment purposes only. We do not guarantee the accuracy or availability of third-party offers or downloads. We are not responsible for any purchase decisions or consequences of game usage. Video games may be habit-forming and may negatively affect health if used excessively — please play responsibly. Trademarks belong to their respective owners. This site may contain affiliate links that can generate commissions.</p>
    <p class="tiny">© {year} AI Gaming Blog</p>
  </div>
</section>
"""

# ====== HTML sablon ======
BASE_STYLES = """
:root{--bg:#0b0f14;--panel:#121821;--muted:#9fb0c3;--text:#eaf1f8;--accent:#5cc8ff;--card:#0f141c;--border:#1f2a38}
html,body{margin:0;padding:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,Segoe UI,Roboto,Inter,Arial,sans-serif}
.wrap{max-width:900px;margin:24px auto;padding:18px;background:var(--panel);border-radius:12px;border:1px solid var(--border)}
img.cover{width:100%;height:auto;border-radius:8px;display:block}
h1{margin:10px 0 6px;font-size:28px}
h2{margin-top:18px}
p{line-height:1.6}
.tiny{color:var(--muted);font-size:13px}
.ad{background:linear-gradient(180deg,rgba(255,209,102,.06),transparent);padding:12px;border-radius:10px;border:1px dashed #ffd166}
a{color:var(--accent)}
.btn{display:inline-block;padding:10px 14px;border-radius:10px;border:1px solid var(--accent);text-decoration:none}
.list{list-style:disc;padding-left:20px}
code{background:#0b1220;border:1px solid #223049;border-radius:6px;padding:2px 6px}
.badge{display:inline-block;background:#0d1622;border:1px solid #223049;border-radius:999px;padding:2px 8px;margin-right:6px}
"""

def build_post_html(details: dict, youtube_embed: str, cover_rel: str) -> str:
    name = details.get("name") or "Unknown Game"
    slug = details.get("slug") or slugify(name)
    released = details.get("released") or ""
    year = released.split("-")[0] if released else ""
    platforms = [p["platform"]["name"] for p in (details.get("platforms") or []) if p.get("platform")]
    pubs = extract_publishers(details)
    devs = extract_developers(details)
    age = extract_age_rating(details)

    title = compose_seo_title(name)
    meta_desc = compose_meta_description(name, platforms, year)
    review_html = short_review_for(details)
    cheats_html = compose_cheats_block(details)

    # Publisher/Developer és Age külön sorok – csak ha van adat
    about_items = []
    if released:
        about_items.append(f"<li><strong>Release:</strong> {released}</li>")
    if pubs:
        about_items.append(f"<li><strong>Publisher:</strong> {pubs}</li>")
    if devs:
        about_items.append(f"<li><strong>Developer:</strong> {devs}</li>")
    if age:
        about_items.append(f"<li><strong>Age Rating:</strong> {age}</li>")
    if platforms:
        about_items.append(f"<li><strong>Platforms:</strong> {', '.join(platforms)}</li>")
    about_ul = "<ul>\n" + "\n".join(about_items) + "\n</ul>" if about_items else ""

    # Affiliate blokk a Cheats alatt + kis link a végén
    download_block = """
    <div class="ad" style="margin-top:12px">
      <h3>Download the game (official stores)</h3>
      <p><span class="tiny">We only recommend official sources.</span></p>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <a class="btn" href="#" rel="nofollow noopener" target="_blank">Steam (affiliate)</a>
        <a class="btn" href="#" rel="nofollow noopener" target="_blank">Humble Bundle (affiliate)</a>
        <a class="btn" href="#" rel="nofollow noopener" target="_blank">Amazon Gaming (affiliate)</a>
      </div>
      <p class="tiny" style="margin-top:8px">⚠️ Please note: We don’t allow sharing illegal download links in comments. Use the official download options above.</p>
    </div>
    """

    footer_small_download = """
    <p style="margin-top:16px"><a href="#" rel="nofollow noopener" target="_blank">Download here</a></p>
    """

    # JSON-LD (structured data)
    json_ld = {
        "@context":"https://schema.org",
        "@type":"VideoGame",
        "name": name,
        "genre": [t.get("name") for t in (details.get("tags") or []) if t.get("name")][:5],
        "publisher": pubs or None,
        "developer": devs or None,
        "datePublished": released or None,
        "description": BeautifulSoup(details.get("description") or "", "html.parser").get_text()[:500],
        "image": cover_rel.replace("../", ""),  # relatív az oldalhoz képest
        "url": f"generated_posts/{slug}.html",
        "operatingSystem": ", ".join(platforms) if platforms else None
    }

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{title}</title>
  <meta name="description" content="{meta_desc}"/>
  <style>{BASE_STYLES}</style>
  <script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False)}</script>
</head>
<body>
  <div class="wrap">
    <a href="../index.html">⬅ Back to Home</a>
    <h1>{title}</h1>
    <img class="cover" src="{cover_rel}" alt="{name} cover"/>

    <h2>About the Game</h2>
    {about_ul}

    <h2>Short Review</h2>
    {review_html}

    <h2>Gameplay Video</h2>
    <iframe width="100%" height="400" src="{youtube_embed}" frameborder="0" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>

    <h2>Cheats & Tips</h2>
    {cheats_html}

    {download_block}

    <h2 class="tiny">AI Rating</h2>
    <p class="tiny">⭐ {round(random.uniform(3.0,5.0),1)}/5</p>

    {COMMENT_WIDGET}

    {footer_small_download}

    {post_footer_html()}
  </div>
</body>
</html>
"""
    return html

# ====== Generálás ======
def gather_candidates(total_needed, num_popular):
    popular = []
    page = 1
    tries = 0
    while len(popular) < num_popular and tries < 8:
        try:
            res = rawg_fetch(page=page, ordering="-added")
            if not res: break
            popular.extend(res)
            page += 1
        except Exception as e:
            print("RAWG popular fetch error:", e)
            break
        tries += 1

    randoms = []
    tries = 0
    while len(randoms) < (total_needed - len(popular)) and tries < 12:
        try:
            page_rand = random.randint(1, 20)
            res = rawg_fetch(page=page_rand)
            if res:
                randoms.extend(res)
        except Exception:
            pass
        tries += 1

    random.shuffle(randoms)
    needed = total_needed - len(popular)
    return popular[:num_popular], randoms[:needed]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=NUM_TOTAL)
    args = parser.parse_args()
    total = args.num_posts

    ensure_dirs()

    existing_posts = read_index_posts()
    existing_titles = set(p.get("title","").lower() for p in existing_posts)
    existing_files  = set(os.path.basename(p.get("url","")) for p in existing_posts if p.get("url"))

    popular, randoms = gather_candidates(total, NUM_POPULAR)
    candidates = popular + randoms

    new_posts = []
    for g in candidates:
        try:
            name = (g.get("name") or "").strip()
            if not name:
                continue
            slug = slugify(name)
            out_file = os.path.join(OUTPUT_DIR, f"{slug}.html")
            if os.path.exists(out_file) or (f"{slug}.html" in existing_files) or (name.lower() in existing_titles):
                print(f"Skipping existing: {name}")
                continue

            # Kell helyi borítókép
            local_image = pick_local_image(slug)
            if not local_image:
                print(f"❌ No local image for: {name} (expected {slug}.jpg/png/webp) – skipping.")
                continue

            # Részletes adat
            gid = g.get("id")
            if not gid:
                continue
            details = rawg_game_details(gid)

            # YouTube relevancia kötelező
            ytembed = youtube_search_embed(name)
            if not ytembed:
                print(f"❌ No relevant YouTube video found for: {name} – skipping.")
                continue

            # HTML előállítás
            cover_rel = f"../Picture/{os.path.basename(local_image)}"
            html = build_post_html(details, ytembed, cover_rel)
            Path(out_file).write_text(html, encoding="utf-8")
            print(f"✅ Generated: {out_file}")

            # Index-bejegyzés
            now = datetime.datetime.now()
            platforms = [p["platform"]["name"] for p in (details.get("platforms") or []) if p.get("platform")]
            post_rec = {
                "title": name,
                "url": f"generated_posts/{slug}.html",
                "platform": platforms,
                "date": now.strftime("%Y-%m-%d"),
                "rating": round(random.uniform(3.0,5.0),1),
                "cover": f"Picture/{os.path.basename(local_image)}",
                "views": 0,
                "comments": 0
            }
            new_posts.append(post_rec)
            # Kisebb késleltetés az API-k felé
            time.sleep(0.6)

        except Exception as e:
            print("⚠️ Error on candidate:", e)
            continue

    # Index frissítés
    if new_posts:
        merged = new_posts + existing_posts
        seen = set()
        unique = []
        for p in merged:
            t = (p.get("title","") or "").lower()
            if t in seen:
                continue
            seen.add(t)
            unique.append(p)
        # dátum szerint csökkenő
        unique.sort(key=lambda x: x.get("date",""), reverse=True)
        write_index_posts(unique)
    print(f"Done. New posts added: {len(new_posts)}")
    if new_posts:
        for p in new_posts:
            print(" -", p["title"], "->", p["url"])

if __name__ == "__main__":
    main()
