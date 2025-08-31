#!/usr/bin/env python3
# update_index.py
import os

OUTDIR = "generated_posts"
INDEX_FILE = "index.html"

def generate_index():
    posts = [f for f in os.listdir(OUTDIR) if f.endswith(".html")]
    posts.sort(reverse=True)  # legújabb legyen elöl

    items = []
    for p in posts:
        items.append(f'<li><a href="{OUTDIR}/{p}">{p}</a></li>')

    html = f"""<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <title>AI Blog</title>
</head>
<body>
    <h1>Üdv a blogomon 👋</h1>
    <p>Ez egy AI által generált blog.</p>
    <h2>Legújabb posztok</h2>
    <ul>
        {"".join(items)}
    </ul>
    <hr>
    <h2>💰 Ajánlott lehetőségek</h2>
    <ul>
      <li><a href="https://icmarkets.com/?camp=3992" target="_blank">🌍 ICMarkets - kereskedj profi szinten</a></li>
      <li><a href="https://www.dukascopy.com/api/es/12831/type-S/target-id-149" target="_blank">🏦 Dukascopy - nyiss számlát promóciós kóddal: E12831</a></li>
      <li><a href="https://r.honeygain.me/NAGYT86DD6" target="_blank">📱 Honeygain - keress passzív jövedelmet az internet megosztásával</a></li>
    </ul>
</body>
</html>"""

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Frissítve: {INDEX_FILE} ({len(posts)} poszt link)")

if __name__ == "__main__":
    generate_index()
