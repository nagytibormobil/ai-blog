import requests
import os
from bs4 import BeautifulSoup

# ---------- SETTINGS ----------
OUTPUT_DIR = "generated_posts"
BLOG_TEMPLATE = """
<section class="section">
  <h2>Full Review</h2>
  <div class="content">
    {review}
  </div>
</section>

<section class="section">
  <h2>Cheats & Tips</h2>
  <div class="content">
    {tips}
  </div>
</section>

<section class="section">
  <h2>Sources</h2>
  <ul>
    {sources}
  </ul>
</section>
"""

# ---------- FUNCTIONS ----------
def fetch_wiki_summary(game_title: str):
    url = f"https://en.wikipedia.org/wiki/{game_title.replace(' ', '_')}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    
    soup = BeautifulSoup(r.text, "html.parser")
    paragraphs = soup.select("p")
    summary = " ".join([p.text for p in paragraphs[:5]])
    return summary.strip(), url

def generate_post(game_title: str):
    print(f"Generating post for: {game_title}")

    # Fetch Wikipedia (for Review)
    wiki_summary, wiki_url = fetch_wiki_summary(game_title) or ("", "")

    # Dummy gameplay expansion (in practice: AI model call)
    review = f"""
    <h3>Gameplay Overview</h3>
    <p>{wiki_summary}</p>
    <p>{game_title} offers a deep gameplay experience with multiple mechanics.
    This section can be expanded 5x using AI with verified facts.</p>
    
    <h3>Graphics & Sound</h3>
    <p>The game features immersive visuals and audio design, as confirmed by community reviews.</p>
    
    <h3>Pros & Cons</h3>
    <ul>
      <li><b>Pros:</b> Team-based mechanics, fast-paced action, unique characters.</li>
      <li><b>Cons:</b> Steep learning curve, community size fluctuates.</li>
    </ul>
    """

    # Cheats & Tips – placeholder (to be expanded with AI + community guides)
    tips = f"""
    <h3>General Tips</h3>
    <ul>
      <li>Focus on objectives instead of kills.</li>
      <li>Learn the maps to gain tactical advantage.</li>
      <li>Use each character's abilities strategically.</li>
    </ul>
    
    <h3>Advanced Strategies</h3>
    <p>Players recommend timing respawns, controlling choke points,
    and using merc synergies effectively.</p>
    """

    # Sources
    sources = f"""
    <li><a href="{wiki_url}" target="_blank">Wikipedia</a></li>
    <li><a href="https://store.steampowered.com/" target="_blank">Steam Store</a></li>
    """

    # Combine
    html_content = BLOG_TEMPLATE.format(review=review, tips=tips, sources=sources)

    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, f"{game_title.lower().replace(' ', '-')}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Post generated: {filepath}")


# ---------- RUN ----------
if __name__ == "__main__":
    games = ["Dirty Bomb", "Half-Life 2", "Counter-Strike: Global Offensive"]
    for g in games:
        generate_post(g)
