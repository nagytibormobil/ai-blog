import os
import json
import random
import shutil
from datetime import datetime
import requests

# ======== BEÁLLÍTÁSOK ========
BASE_DIR = r"C:\ai_blog"
PICTURE_DIR = os.path.join(BASE_DIR, "Picture")
GENERATED_POSTS_DIR = os.path.join(BASE_DIR, "generated_posts")
INDEX_HTML = os.path.join(BASE_DIR, "index.html")
RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"
MAX_POSTS_GENERATE = 12

os.makedirs(PICTURE_DIR, exist_ok=True)
os.makedirs(GENERATED_POSTS_DIR, exist_ok=True)

# ======== SEGÉDFÜGGVÉNYEK ========
def safe_filename(title):
    return title.lower().replace(" ", "-").replace(":", "").replace("'", "").replace(".", "")

def download_game_image(title, url):
    """Letölti a képet a Picture mappába és visszaadja az index.html-be használandó relatív útvonalat"""
    filename = f"{safe_filename(title)}.jpg"
    path = os.path.join(PICTURE_DIR, filename)
    if os.path.exists(path):
        return f"Picture/{filename}"

    try:
        r = requests.get(url, stream=True, timeout=10)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            print(f"✅ Kép letöltve: {filename}")
        else:
            print(f"⚠️ Nem sikerült letölteni a képet: {title}")
            return ""
    except Exception as e:
        print(f"⚠️ Hiba a kép letöltésnél {title}: {e}")
        return ""
    return f"Picture/{filename}"

def get_random_game(existing_titles):
    """Lekéri a RAWG API-ból a játékot, ami még nincs generálva"""
    url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&page_size=50"
    try:
        r = requests.get(url)
        data = r.json()
        games = [g for g in data['results'] if g['name'] not in existing_titles]
        if not games:
            return None
        game = random.choice(games)
        return {
            "title": game['name'],
            "platform": [p['platform']['name'] for p in game['platforms']],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "rating": round(random.uniform(2.5, 5.0), 1),
            "cover_url": game['background_image'] if 'background_image' in game else "",
            "cheats": [f"Cheat tip {i+1}" for i in range(random.randint(3,15))]
        }
    except Exception as e:
        print(f"⚠️ Hiba a játék lekérésnél: {e}")
        return None

# ======== LÉTREHOZÁS ========
def generate_posts(num_posts):
    posts = []
    existing_files = os.listdir(GENERATED_POSTS_DIR)
    existing_titles = [f.split(".")[0].replace("-", " ").title() for f in existing_files]

    while len(posts) < num_posts:
        game = get_random_game(existing_titles)
        if not game:
            print("⚠️ Nincs több új játék!")
            break
        title_safe = safe_filename(game['title'])
        filename = f"{title_safe}.html"
        if filename in existing_files:
            continue

        cover = download_game_image(game['title'], game['cover_url'])
        post = {
            "title": game['title'],
            "url": f"generated_posts/{filename}",
            "platform": game['platform'],
            "date": game['date'],
            "rating": game['rating'],
            "cover": cover,
            "cheats": game['cheats'],
            "comments": []
        }
        posts.append(post)
        existing_titles.append(game['title'])
        existing_files.append(filename)

        # ======== HTML LÉTREHOZÁS ========
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{game['title']} – AI Gaming Blog</title>
<meta name="description" content="AI-generated cheats, guides, reviews, and tips for {game['title']}.">
<style>
body{{background:#0b0f14;color:#eaf1f8;font-family:system-ui,sans-serif;margin:0;padding:0}}
.wrap{{max-width:900px;margin:auto;padding:24px}}
h1{{margin:0 0 10px 0}}
img{{max-width:100%;border-radius:12px}}
.footer{{margin-top:36px;padding:18px;border-top:1px solid #1f2a38;color:#9fb0c3;font-size:13px}}
.comment-box{{margin-top:20px}}
textarea{{width:100%;padding:10px;border-radius:10px;background:#121821;color:#eaf1f8;border:1px solid #1f2a38}}
button{{padding:8px 12px;border-radius:10px;background:#5cc8ff;border:none;color:#000;cursor:pointer}}
.comment-list{{margin-top:12px}}
.comment-list li{{margin-bottom:8px}}
</style>
</head>
<body>
<div class="wrap">
<h1>{game['title']}</h1>
<img src="../{cover}" alt="{game['title']}"/>
<h2>AI Rating</h2>
<p>⭐ {game['rating']}/5</p>

<h2>Cheats & Tips</h2>
<ul>
{''.join([f"<li>{tip}</li>" for tip in game['cheats']])}
</ul>
{'' if len(game['cheats'])<15 else '<p>Use the above cheats in-game by pressing the indicated keys.</p>'}

<h2>User Comments</h2>
<div class="comment-box">
<textarea id="comment_input" placeholder="Leave your comment (max 10/day)"></textarea>
<button id="add_comment">Post Comment</button>
<ul class="comment-list" id="comments_list"></ul>
</div>

<div class="footer">
<div><strong>Comment Policy</strong>
<ul>
<li>No spam, ads, or offensive content.</li>
<li>No adult/drugs/war/terror topics.</li>
<li>Max 10 comments/day per person.</li>
<li>Be respectful. We moderate strictly.</li>
</ul></div>
<div><strong>Terms</strong>
<p>All content is for informational/entertainment purposes only. Trademarks belong to their respective owners. Affiliate links may generate commissions.</p></div>
<p>© {datetime.now().year} AI Gaming Blog</p>
</div>

<script>
// Simple client-side comment system
const comments = [];
const blockedWords = ["sex","fuck","porn","drugs","war"];
document.getElementById('add_comment').onclick = () => {{
    const input = document.getElementById('comment_input');
    const text = input.value.trim();
    if(!text) return alert("Comment cannot be empty.");
    if(comments.length>=10) return alert("Max 10 comments/day.");
    for(const w of blockedWords) if(text.toLowerCase().includes(w)) return alert("Inappropriate content.");
    comments.push(text);
    const li = document.createElement('li'); li.textContent=text;
    document.getElementById('comments_list').appendChild(li);
    input.value="";
}}
</script>

<p><a href="../index.html">Home</a></p>

</div>
</body>
</html>
"""
        with open(os.path.join(GENERATED_POSTS_DIR, filename), "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"✅ Generated post: {filename}")

    return posts

# ======== INDEX.HTML FRISSÍTÉS ========
def update_index(posts):
    index_data = []
    for p in posts:
        index_data.append({
            "title": p['title'],
            "url": p['url'],
            "platform": p['platform'],
            "date": p['date'],
            "rating": p['rating'],
            "cover": p['cover'],
            "views": 0,
            "comments": 0
        })
    # Beillesztés a meglévő index.html-be
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        content = f.read()
    start_tag = "// <<< AUTO-GENERATED POSTS START >>>"
    end_tag = "// <<< AUTO-GENERATED POSTS END >>>"
    new_posts_json = json.dumps(index_data, indent=2)
    new_content = f"{start_tag}\nconst POSTS = {new_posts_json};\n{end_tag}"
    content = content.split(start_tag)[0] + new_content + content.split(end_tag)[1]
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ index.html POSTS updated.")

# ======== FŐ PROGRAM ========
if __name__=="__main__":
    new_posts = generate_posts(MAX_POSTS_GENERATE)
    update_index(new_posts)
