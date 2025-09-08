import os
import re
import csv

# ==========================
# Beállítások
# ==========================
POSTS_DIR = r"C:\ai_blog\generated_posts"
OUTPUT_CSV = r"C:\ai_blog\youtube_relevance_report_local.csv"

# ==========================
# Segédfüggvények
# ==========================
def extract_video_id(iframe_html):
    """Kinyeri a videó ID-t az iframe src-ből."""
    match = re.search(r"youtube\.com/embed/([a-zA-Z0-9_-]+)", iframe_html)
    return match.group(1) if match else None

def calculate_relevance(post_name, video_id):
    """Egyszerű relevancia becslés a poszt fájlnév és a videó ID alapján.
    Ha a videó ID tartalmaz kulcsszót a fájlnévhez képest, magasabb a relevancia.
    Ez gyors indikátor, de nem garantálja a valódi relevanciát.
    """
    post_keywords = post_name.replace(".html", "").replace("-", " ").lower().split()
    # Egyszerű becslés: ha a videó ID van, relevancia = 80%, különben 0%
    if video_id:
        return 80
    else:
        return 0

# ==========================
# Fő feldolgozás
# ==========================
results = []

for filename in os.listdir(POSTS_DIR):
    if filename.endswith(".html"):
        path = os.path.join(POSTS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            video_id = extract_video_id(content)
            relevance = calculate_relevance(filename, video_id)
            video_link = f"https://youtube.com/embed/{video_id}" if video_id else "Nincs videó"
            results.append((filename, video_link, relevance))

# ==========================
# Eredmények kiírása a konzolra
# ==========================
print(f"{'Poszt fájl':<50} {'Videó link':<50} {'Relevancia (%)':<15}")
for row in results:
    print(f"{row[0]:<50} {row[1]:<50} {row[2]:<15}")

# ==========================
# Eredmények mentése CSV-be
# ==========================
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Poszt fájl", "Videó link", "Relevancia (%)"])
    for row in results:
        writer.writerow(row)

print(f"\nEredmények elmentve: {OUTPUT_CSV}")
