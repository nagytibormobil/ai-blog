import os
from bs4 import BeautifulSoup

# Könyvtárak
BASE_DIR = r"C:\Users\User\OneDrive\ai_blog"
POST_DIR = os.path.join(BASE_DIR, "generated_posts")
INDEX_FILE = os.path.join(BASE_DIR, "index.html")
OUTPUT_FILE = os.path.join(BASE_DIR, "index_clean.html")  # ide mentjük az új verziót

# index.html betöltése
with open(INDEX_FILE, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Végigmegyünk minden linken
links = soup.find_all("a", href=True)
removed = 0
for link in links:
    href = link["href"]
    if "generated_posts/" in href and href.endswith(".html"):
        filename = href.split("/")[-1]
        file_path = os.path.join(POST_DIR, filename)
        if not os.path.exists(file_path):
            print(f"[TÖRÖLVE] {href}")
            link.decompose()  # eltávolítja a hibás linket
            removed += 1

# Új HTML mentése
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(str(soup))

print(f"Kész! {removed} hibás link törölve. Új fájl: {OUTPUT_FILE}")
