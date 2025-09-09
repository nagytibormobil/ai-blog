import requests
import os
from bs4 import BeautifulSoup
import openai

# ---------- SETTINGS ----------
OUTPUT_DIR = "generated_posts"
openai.api_key = os.getenv("OPENAI_API_KEY")  # API kulcs környezeti változóból

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
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return "", url
        soup = BeautifulSoup(r.text, "html.parser")
        paragraphs = soup.select("p")
        summary = " ".join([p.text for p in paragraphs[:5]])
        return summary.strip(), url
    except:
        return "", url

def ai_expand_text(base_text: str, section: str):
    """Adds ~15% human-like expansion to factual text."""
    prompt = f"""
    I will give you a factual text about a video game.
    Expand it slightly (max +15%) in a natural, human-like style,
    as if written by a gaming journalist. 

    Rules:
    - Do NOT invent new facts (no new characters, maps, features).
    - Only add context, examples, summaries.
    - Keep the tone engaging and personal.

    Section: {section}
    Text:
    {base_text}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response["choices"][0]["message"]["content"].strip()

def find_official_cheats(game_title: str):
    """
    Check Wikipedia and Steam for official cheat codes.
    Returns a list of dicts: [{"source": url, "description": text}]
    """
    cheats_found = []

    # Wikipedia check
    wiki_url = f"https://en.wikipedia.org/wiki/{game_title.replace(' ', '_')}"
    try:
        r = requests.get(wiki_url, timeout=5)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            cheat_sections = soup.find_all(text=lambda t: t and "cheat" in t.lower())
            if cheat_sections:
                cheats_found.append({
                    "source": wiki_url,
                    "description": "Official cheats listed on Wikipedia"
                })
    except:
        pass

    # Steam check
    steam_search_url = f"https://store.steampowered.com/search/?term={game_title.replace(' ', '+')}"
    try:
        r = requests.get(steam_search_url, timeout=5)
        if r.status_code == 200 and "cheat" in r.text.lower():
            cheats_found.append({
                "source": steam_search_url,
                "description": "Potential cheat info on Steam store"
            })
    except:
        pass

    return cheats_found

def generate_post(game_title: str):
    print(f"Generating post for: {game_title}")

    # Fetch Wikipedia summary
    wiki_summary, wiki_url = fetch_wiki_summary(game_title)

    # Expand review with human-like style
    review_text = ai_expand_text(wiki_summary, "Review & Gameplay")
    review = f"""
    <h3>Gameplay Overview</h3>
    <p>{review_text}</p>
    
    <h3>Graphics & Sound</h3>
    <p>{ai_expand_text("The game features visuals and audio typical of its era, with emphasis on atmosphere and immersion.", "Graphics & Sound")}</p>
    
    <h3>Pros & Cons</h3>
    <ul>
      <li><b>Pros:</b> Team-based mechanics, fast-paced action, unique characters.</li>
      <li><b>Cons:</b> Steep learning curve, community size fluctuates.</li>
    </ul>
    """

    # Narrative-style Tips (mesélő, emberi stílus)
    tips_base = """
As you play, focus on understanding your objectives and using your characters' abilities wisely. 
Rather than just chasing kills, think about your strategy and approach each scenario carefully. 
Take time to learn the m
