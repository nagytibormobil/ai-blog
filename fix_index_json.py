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

def clean_json_text(json_text):
    # Eltávolít minden sorvégi kommentet és whitespace-t
    lines = json_text.splitlines()
    cleaned_lines = []
    for line in lines:
        line = line.split("//")[0].strip()
        if line:
            cleaned_lines.append(line)
    cleaned_text = "\n".join(cleaned_lines)
    
    # Ha van felesleges utolsó vessző a tömb végén, eltávolítja
    cleaned_text = re.sub(r",\s*(\]|\})", r"\1", cleaned_text)
    return cleaned_text

def main():
    html = load_index()

    match = re.search(r'POSTS\s*=\s*(\[[\s\S]*?\])', html)
    if not match:
        raise RuntimeError("Nem található POSTS tömb az index.html-ben!")

    posts_json = match.group(1)
    posts_json_clean = clean_json_text(posts_json)

    # Próbálja betölteni JSON-ként
    try:
        posts = json.loads(posts_json_clean)
    except Exception as e:
        # Ha nem megy, üzenet és mentés debughoz
        with open("posts_debug.json", "w", encoding="utf-8") as dbg:
            dbg.write(posts_json_clean)
        raise RuntimeError(f"Hibás JSON a POSTS tömbben, mentve posts_debug.json\n{e}")

    # Törli a nem létező posztokat
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

    # Visszaírja az új JSON-t az index.html-be
    new_json = json.dumps(valid_posts, indent=2, ensure_ascii=False)
    replacement = "const POSTS = " + new_json

    new_html = re.sub(r'POSTS\s*=\s*\[[\s\S]*?\]', replacement, html)

    save_index(new_html)

    print(f"Kész! {removed} hibás bejegyzés törölve az index.html-ből.")
    print(f"Összes érvényes poszt: {len(valid_posts)}")

if __name__ == "__main__":
    main()
