import os
from pathlib import Path
import datetime

# Mappák
BASE_DIR = Path("C:/ai_blog")
PICTURE_DIR = BASE_DIR / "Picture"
POST_DIR = BASE_DIR / "generated_posts"
TEMPLATE_FILE = BASE_DIR / "templates/post_template.html"

# Példa játék adatok
GAMES = [
    {
        "title": "GTA V",
        "about": "Open world action-adventure game set in Los Santos.",
        "image_name": "gta-v.jpg",
        "rating": 4.7,
        "cheats": [
            "Unlimited ammo",
            "Invincibility",
            "Spawn vehicle",
            "Lower wanted level",
            "Increase wanted level"
        ],
        "affiliate_links": [
            '<p><a href="https://example.com/affiliate1" target="_blank">Buy Game Here</a></p>',
            '<p><a href="https://example.com/affiliate2" target="_blank">Get Bonus Items</a></p>'
        ]
    },
    {
        "title": "FIFA 23",
        "about": "Realistic football simulation game with updated rosters.",
        "image_name": "fifa-23.jpg",
        "rating": 4.4,
        "cheats": [
            "Unlock all stadiums",
            "Max player stats",
            "Infinite coins"
        ],
        "affiliate_links": [
            '<p><a href="https://example.com/affiliate3" target="_blank">Buy FIFA 23</a></p>'
        ]
    }
]

def sanitize_filename(title):
    return "".join(c if c.isalnum() else "_" for c in title.lower())

def generate_post(game):
    filename = sanitize_filename(game["title"]) + ".html"
    post_path = POST_DIR / filename

    if post_path.exists():
        print(f"Skipping '{game['title']}' (already exists).")
        return

    # Cheats HTML max 15
    cheats = game["cheats"][:15]
    cheats_html = "".join(f"<li>{c}</li>" for c in cheats)
    extra_instruction = ""
    if len(game["cheats"]) > 15:
        extra_instruction = "<p>Use the following keys to activate extra cheats in-game.</p>"

    # Betöltjük a template-et
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    # Placeholder cserék
    html = template.replace("{{title}}", game["title"])
    html = html.replace("{{short_description}}", game["about"])
    html = html.replace("{{about}}", game["about"])
    html = html.replace("{{rating}}", str(game["rating"]))
    html = html.replace("{{image}}", game["image_name"])
    html = html.replace("{{cheats}}", cheats_html)
    html = html.replace("{{extra_cheats_instruction}}", extra_instruction)
    html = html.replace("{{affiliate_links}}", "\n".join(game["affiliate_links"]))
    html = html.replace("{{year}}", str(datetime.datetime.now().year))

    POST_DIR.mkdir(parents=True, exist_ok=True)
    with open(post_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated post: {post_path}")

def main():
    for game in GAMES:
        generate_post(game)
    print("All posts generated successfully.")

if __name__ == "__main__":
    main()
