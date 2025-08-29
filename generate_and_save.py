import os
import random
import argparse
from datetime import datetime

# ====== BEÁLLÍTÁSOK ======
POSTS_DIR = "generated_posts"
PICTURE_DIR = "Picture"   # relatív elérési út
MAX_POSTS = 12

# SEO-barát affiliate szekció
AFFILIATE_SECTION = """
<div class="affiliate">
  <h3>Sponsored Links</h3>
  <p>💸 Earn Real Money While You Play 📱<br>
  Simple passive income by sharing a bit of your internet. Runs in the background while you game.<br>
  <a href="https://r.honeygain.me/" target="_blank">👉 Try Honeygain now</a></p>

  <p>🌍 IC Markets – Trade like a pro<br>
  <a href="https://www.icmarkets.com/" target="_blank">👉 Open an account</a></p>

  <p>🏦 Dukascopy – Promo code: E12831<br>
  <a href="https://www.dukascopy.com/" target="_blank">👉 Start here</a></p>
</div>
"""

# Példa játéklista
GAMES = [
    "Minecraft", "Fortnite", "GTA V", "The Witcher 3: Wild Hunt",
    "League of Legends", "FIFA 23", "Elden Ring", "Call of Duty: Modern Warfare II"
]

# Példaszövegek
REVIEW_TEMPLATES = [
    "In this review, we dive into the unique mechanics, immersive visuals, and lasting appeal of {game}.",
    "Players love {game} for its depth, graphics, and engaging storyline that keeps gamers hooked.",
    "The gameplay of {game} offers challenges, rewards, and a sense of accomplishment unmatched by others."
]


def generate_post(game):
    """Egy játékhoz poszt HTML fájlt készít"""
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{now}-{game.replace(' ', '_').replace(':', '')}.html"
    filepath = os.path.join(POSTS_DIR, filename)

    # Kép kezelése
    picture_file = os.path.join(PICTURE_DIR, f"{game.replace(' ', '_')}.jpg")
    if not os.path.exists(picture_file):
        # ha nincs kép, akkor placeholder
        picture_tag = '<img src="../Picture/placeholder.jpg" alt="No image available">'
    else:
        picture_tag = f'<img src="../{picture_file}" alt="{game} image">'

    # Review szöveg
    review_text = random.choice(REVIEW_TEMPLATES).format(game=game)

    # HTML tartalom
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{game} - Game Review</title>
  <meta name="description" content="Review of {game}, including gameplay, graphics, and community insights.">
  <meta name="keywords" content="{game}, video game review, gameplay, graphics">
  <link rel="stylesheet" href="../style.css">
</head>
<body>
  <div class="post-container">
    <a href="../index.html" class="home-btn">🏠 Back to Home</a>
    <h1>{game}</h1>
    {picture_tag}
    <p>{review_text}</p>
    {AFFILIATE_SECTION}
  </div>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Generated: {game} → {filepath}")
    return filename


def generate_index(posts):
    """Index oldal frissítése"""
    links = ""
    for game, file in posts:
        img_path = os.path.join(PICTURE_DIR, f"{game.replace(' ', '_')}.jpg")
        if os.path.exists(img_path):
            img_tag = f'<img src="{img_path}" alt="{game} cover">'
        else:
            img_tag = '<img src="Picture/placeholder.jpg" alt="No image available">'
        links += f"""
        <div class="card">
          <a href="{POSTS_DIR}/{file}">
            {img_tag}
            <h2>{game}</h2>
          </a>
        </div>
        """

    # index.html
    html_index = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AI Game Blog</title>
  <meta name="description" content="AI-generated video game reviews">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <h1>🎮 AI Game Blog</h1>
    <nav>
      <label for="game-select">Browse A–Z:</label>
      <select id="game-select" onchange="location = this.value;">
        <option value="">-- Choose a game --</option>
        {''.join([f'<option value="{POSTS_DIR}/{f}">{g}</option>' for g,f in posts])}
      </select>
    </nav>
  </header>
  <main>
    <div class="grid">
      {links}
    </div>
  </main>
  {AFFILIATE_SECTION}
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_index)
    print("index.html updated.")


def main(num_posts):
    os.makedirs(POSTS_DIR, exist_ok=True)
    os.makedirs(PICTURE_DIR, exist_ok=True)

    # véletlenszerű játékok, de duplikátum nélkül
    chosen_games = random.sample(GAMES, min(num_posts, len(GAMES)))

    posts = []
    for game in chosen_games:
        file = generate_post(game)
        posts.append((game, file))

    generate_index(posts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_posts", type=int, default=MAX_POSTS)
    args = parser.parse_args()
    main(args.num_posts)
