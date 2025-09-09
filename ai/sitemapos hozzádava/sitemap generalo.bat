import os
from datetime import datetime

# Mappa, ahol a generált posztok vannak
posts_dir = "generated_posts"
base_url = "https://nagytibormobil.github.io/ai-blog/generated_posts/"

# Lista az összes poszt URL-jére
urls = []
for filename in os.listdir(posts_dir):
    if filename.endswith(".html"):
        file_path = os.path.join(posts_dir, filename)
        # Utolsó módosítás dátuma
        lastmod = datetime.utcfromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d")
        urls.append((base_url + filename, lastmod))

# Sitemap XML létrehozása
sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>\n"""
sitemap_content += """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n"""

for url, lastmod in urls:
    sitemap_content += f"  <url>\n"
    sitemap_content += f"    <loc>{url}</loc>\n"
    sitemap_content += f"    <lastmod>{lastmod}</lastmod>\n"
    sitemap_content += f"    <changefreq>daily</changefreq>\n"
    sitemap_content += f"    <priority>0.8</priority>\n"
    sitemap_content += f"  </url>\n"

sitemap_content += "</urlset>"

# Mentés sitemap.xml néven a főkönyvtárba
with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(sitemap_content)

print("Sitemap elkészült!")
