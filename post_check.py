import os
import requests
from bs4 import BeautifulSoup

# === CONFIG ===
POST_DIR = r"C:\ai_blog\generated_posts"
INDEX_FILE = r"C:\ai_blog\index.html"

# YouTube API kulcs
YOUTUBE_API_KEY = "AIzaSyAXedHcSZ4zUaqSaD3MFahLz75IvSmxggM"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

def get_all_posts():
    return [f for f in os.listdir(POST_DIR) if f.endswith(".html")]

def search_youtube_video(query):
    """Keres releváns videót a YouTube-on a játék címére (biztonságos verzió)"""
    params = {
        "part": "snippet",
        "q": query,
        "key": YOUTUBE_API_KEY,
        "maxResults": 5,
        "type": "video"
    }
    r = requests.get(YOUTUBE_SEARCH_URL, params=params)
    data = r.json()
    items = data.get("items", [])
    for item in items:
        title = item["snippet"]["title"].lower()
        # lazább kulcsszó-ellenőrzés: legalább a felét a fő szavaknak tartalmazza
        match_count = sum(1 for word in query.split() if len(word) > 2 and word.lower() in title)
        if match_count >= max(1, len(query.split()) // 2):
            video_id = item["id"]["videoId"]
            return f"https://www.youtube.com/embed/{video_id}"
    return None  # ha nem talál releváns videót, nem törlünk

def check_and_fix_post(post_file):
    post_path = os.path.join(POST_DIR, post_file)
    with open(post_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Játék neve a post címéből
    title_tag = soup.find("h1")
    game_title = title_tag.text.strip() if title_tag else ""
    if not game_title:
        print(f"{post_file}: Nem találtam címet, postot nem törlöm!")
        return False

    # Meglévő iframe
    iframe = soup.find("iframe")
    current_video = iframe.get("src") if iframe else None

    # Keresés releváns videóra
    new_video = search_youtube_video(game_title)
    if not new_video:
        print(f"{post_file}: Nem találtam releváns videót, postot nem törlöm!")
        return False

    # Ha nincs iframe, vagy nem egyezik az új videóval → frissítés
    if not current_video or current_video != new_video:
        if iframe:
            iframe["src"] = new_video
        else:
            new_iframe = soup.new_tag(
                "iframe", width="100%", height="400", src=new_video,
                frameborder="0", allowfullscreen=True
            )
            h2_tag = soup.find("h2", string="Gameplay Video")
            if h2_tag:
                h2_tag.insert_after(new_iframe)
            else:
                soup.body.append(new_iframe)
        with open(post_path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        print(f"{post_file}: YouTube videó frissítve -> {new_video}")
        return True

    # Ha a videó már releváns, nem csinálunk semmit
    return True

def rebuild_index():
    posts = get_all_posts()
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("<html><body><h1>Blog Posts</h1><ul>\n")
        for post in posts:
            f.write(f'<li><a href="generated_posts/{post}">{post}</a></li>\n')
        f.write("</ul></body></html>")
    print("Index újragenerálva!")

if __name__ == "__main__":
    for post in get_all_posts():
        check_and_fix_post(post)
    rebuild_index()
    print("===== Kész! =====")
