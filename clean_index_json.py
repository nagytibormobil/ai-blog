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

def main():
    html = load_index()

    # <<< AUTO-GENERATED POSTS START >>> blokk keresése
    match = re.search(
        r'POSTS\s*=\s*(\[[\s\S]*?\])',
        html
    )
    if not match:
        raise RuntimeError("Nem található POSTS tömb az index.html-ben!")

    posts_json = match.group(1)

    # Debug: ha JSON hiba van, mentjük a tartalmat
    try:
        posts = json.loads(posts_json)
    except Exception as e:
        with open("posts_debug.json", "w", encoding="utf-8") as dbg:
            dbg.write(posts_json)
        raise RuntimeError(f"Hibás JSON a POSTS tömbben, mentve: posts_debug.json\n{e}")

    # Ellenőrizd, hogy létezik-e a fájl a generated_posts mappában
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

    # Új JSON visszaírása
    new_json = json.dumps(valid_posts, indent=2, ensure_ascii=False)
    replacement = "const POSTS = " + new_json

    new_html = re.sub(
        r'POSTS\s*=\s*\[[\s\S]*?\]',
        replacement,
        html
    )

    save_index(new_html)

    print(f"Kész! {removed} hibás bejegyzés törölve az index.html-ből.")

if __name__ == "__main__":
    main()
