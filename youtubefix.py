import os
import re

# API kulcsok (későbbi felhasználásra)
YOUTUBE_API_KEY = "AIzaSyAXedHcSZ4zUaqSaD3MFahLz75IvSmxggM"
RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"

# Mappa, ahol a HTML fájlok vannak
folder = r"C:\ai_blog\generated_posts"
# Default YouTube videó, ha hiányzik vagy helytelen
default_video = "https://www.youtube.com/embed/iGP8SqoEQOQ"

# Végigmegyünk minden .html fájlon
for filename in os.listdir(folder):
    if filename.endswith(".html"):
        filepath = os.path.join(folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Ellenőrizzük, van-e <iframe> YouTube embed link
        youtube_embed = re.search(r'<iframe[^>]+src=["\']https://www\.youtube\.com/embed/[^"\']+', content)
        if not youtube_embed:
            print(f"Hiányzó vagy nem megfelelő videó: {filename}")
            # Ellenőrizzük, van-e <h2>Gameplay Video</h2>
            if "<h2>Gameplay Video</h2>" in content:
                # Beillesztjük a default videót a <h2>Gameplay Video</h2> alá
                new_content = re.sub(
                    r"(<h2>Gameplay Video</h2>)",
                    r"\1\n<iframe width=\"100%\" height=\"400\" src=\"" + default_video + "\" frameborder=\"0\" allowfullscreen></iframe>",
                    content
                )
            else:
                # Ha nincs <h2>, akkor a fájl végére illesztjük
                new_content = content + f"\n<h2>Gameplay Video</h2>\n<iframe width=\"100%\" height=\"400\" src=\"{default_video}\" frameborder=\"0\" allowfullscreen></iframe>"

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)

print("YouTube ellenőrzés és javítás kész.")
