import os
import re

# Könyvtárak
BASE_DIR = r"C:\Users\User\OneDrive\ai_blog"
POST_DIR = os.path.join(BASE_DIR, "generated_posts")
INDEX_FILE = os.path.join(BASE_DIR, "index.html")
OUTPUT_FILE = os.path.join(BASE_DIR, "index_clean.html")  # biztonság kedvéért új fájl

# Betöltjük az index.html tartalmát
with open(INDEX_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Regex minta a blokkokhoz
pattern = re.compile(r'\{\s*"title":.*?"url":\s*"([^"]+\.html)".*?\}', re.DOTALL)

removed = []
cleaned_content = content

for match in pattern.finditer(content):
    url = match.group(1)
    filename = os.path.basename(url)
    file_path = os.path.join(POST_DIR, filename)

    # Ha nincs ilyen fájl → töröljük a blokkot
    if not os.path.exists(file_path):
        print(f"[TÖRÖLVE] {url}")
        cleaned_content = cleaned_content.replace(match.group(0), "")
        removed.append(filename)

# Új index mentése
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(cleaned_content)

print(f"Kész! {len(removed)} hibás blokk törölve az index.html-ből.")
if removed:
    print("Töröltek:")
    for r in removed:
        print(" -", r)
