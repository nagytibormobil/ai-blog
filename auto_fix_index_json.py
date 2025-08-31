import re
import json
import os

INDEX_PATH = "index.html"
POSTS_DIR = "generated_posts"

def load_index():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return f.read()

def save_index(content):
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(content)

def fix_posts_block(posts_text):
    """Próbáljuk meg soronként lezárni a hiányzó objektumokat."""
    lines = posts_text.splitlines()
    fixed_lines = []
    open_braces = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("{"):
            open_braces += 1
        if stripped.endswith("}"):
            open_braces -= 1
        fixed_lines.append(line)
    # Ha maradt nyitott objektum, zárjuk le
    for _ in range(open_braces):
        fixed_lines.append("}")
    # Biztosítsuk a tömb lezárását
    if not any("]" in line for line in fixed_lines):
        fixed_lines.append("]")
    # Eltávolítjuk a felesleges vesszőket a végéről
    fixed_text = "\n".join(fixed_lines)
    fixed_text = re.sub(r",\s*(\])", r"\1", fixed_text)
    return fixed_text

def main():
    html = load_index()

    match = re.search(r'POSTS\s*=\s*(\[[\s\S]*?\])', html)
    if not match:
        raise RuntimeError("Nem található POSTS tömb az index.html-ben!")

    posts_json_text = match.group(1)

    # Aggresszív javítás
    fixed_text = fix_posts_block(posts_json_text)

    # JSON betöltés
    try:
        posts = json.loads(fixed_text)
    except Exception as e:
        # Ha még mindig hibás, mentjük debughoz
        with open("posts_debug.json", "w", encoding="utf-8") as dbg:
            dbg.write(fixed_text)
        raise RuntimeError(f"Még mindig hibás JSON, mentve posts_debug.json\n{e}")

    # Töröljük a nem létező fájlokra mutató posztokat
    valid_posts = []
    removed = 0
    for post in posts:
        url = post.get("url", "")
        filepath = os.path.join(POSTS_DIR, os.path.basename(url))
        if os.path.exists(filepath):
            valid_posts.append(post)
        else:
            removed += 1
            print(f"Törölve (nem létező fájl): {url}")

    # Visszaírjuk a HTML-be
    new_json = json.dumps(valid_posts, indent=2, ensure_ascii=False)
    replacement = "const POSTS = " + new_json

    new_html = re.sub(r'POSTS\s*=\s*\[[\s\S]*?\]', replacement, html)

    save_index(new_html)

    print(f"Kész! {removed} hibás bejegyzés törölve az index.html-ből.")
    print(f"Összes érvényes poszt: {len(valid_posts)}")

if __name__ == "__main__":
    main()
