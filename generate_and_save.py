#!/usr/bin/env python3
# generate_and_save.py
# Stabil, önálló verzió, minden függvény benne van

import os
import random
import datetime
import json
import re
from pathlib import Path
import requests

OUTPUT_DIR = "generated_posts"
INDEX_FILE = "index.html"
PICTURE_DIR = "Picture"

RAWG_API_KEY = "2fafa16ea4c147438f3b0cb031f8dbb7"
YOUTUBE_API_KEY = ""  # Ha nincs, fallback lesz

NUM_TOTAL = 12
NUM_POPULAR = 2
RAWG_PAGE_SIZE = 40
USER_AGENT = "AI-Gaming-Blog-Agent/1.0"

Path(OUTPUT_DIR).mkdir(exist_ok=True)
Path(PICTURE_DIR).mkdir(exist_ok=True)

def slugify(name):
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s

def safe_get(d, *keys, default=None):
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return default
    return d

def rawg_fetch(url, params):
    try:
        r = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=10)
        r.raise_for_status()
        return r.json().get("results", [])
    except:
        return []

def rawg_search_random(page=1):
    url = "https://api.rawg.io/api/games"
    params = {"key": RAWG_API_KEY, "page": page, "page_size": RAWG_PAGE_SIZE}
    return rawg_fetch(url, params)

def rawg_get_popular(page=1):
    url = "https://api.rawg.io/api/games"
    params = {"key": RAWG_API_KEY, "page": page, "page_size": RAWG_PAGE_SIZE, "ordering": "-added"}
    return rawg_fetch(url, params)

def download_image(url, dest):
    try:
        r = requests.get(url, stream=True, timeout=15)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return True
    except:
        return False

def get_youtube_embed(game_name):
    if not YOUTUBE_API_KEY:
        return "https://www.youtube.com/embed/dQw4w9WgXcQ"
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {"part":"snippet","q":f"{game_name} gameplay","type":"video","maxResults":1,"key":YOUTUBE_API_KEY}
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        items = r.json().get("items", [])
        if items:
            video_id = items[0]["id"]["videoId"]
            return f"https://www.youtube.com/embed/{video_id}"
    except:
        pass
    return "https://www.youtube.com/embed/dQw4w9WgXcQ"

def read_index_posts():
    if not os.path.exists(INDEX_FILE):
        return []
    try:
        with open(INDEX_FILE,"r",encoding="utf-8") as f:
            html=f.read()
        m=re.search(r"POSTS\s*=\s*(\[[\s\S]*?\])\s*;",html)
        if not m:
            return []
        posts=json.loads(m.group(1))
        return posts if isinstance(posts,list) else []
    except:
        return []

def write_index_posts(all_posts):
    if not os.path.exists(INDEX_FILE):
        return
    with open(INDEX_FILE,"r",encoding="utf-8") as f:
        html=f.read()
    new_json=json.dumps(all_posts,indent=2,ensure_ascii=False)
    if "// <<< AUTO-GENERATED POSTS START >>>" in html:
        new_html=re.sub(r"// <<< AUTO-GENERATED POSTS START >>>[\s\S]*?// <<< AUTO-GENERATED POSTS END >>>",
                        f"// <<< AUTO-GENERATED POSTS START >>>\n    const POSTS = {new_json};\n    // <<< AUTO-GENERATED POSTS END >>>",html)
    else:
        new_html=re.sub(r"POSTS\s*=\s*\[[\s\S]*?\]",f"POSTS = {new_json}",html)
    with open(INDEX_FILE,"w",encoding="utf-8") as f:
        f.write(new_html)

def generate_more_to_explore(posts,n=3):
    if not posts: return ""
    selected=random.sample(posts,min(n,len(posts)))
    html='<section class="more-to-explore">\n<h2>More to Explore</h2>\n<div class="explore-grid">\n'
    for p in selected:
        html+=f'''
        <div class="explore-item">
            <a href="../{p['url']}">
                <img src="../{p['cover']}" alt="{p['title']}">
                <div class="explore-item-title">{p['title']}</div>
            </a>
        </div>
        '''
    html+='</div>\n</section>\n'
    return html

def post_footer_html():
    return f"""
    <section class="footer">
      <div class="row">
        <div><p class="tiny">
        <a href="../terms.html" target="_blank">Terms & Conditions</a></p></div>
      </div>
      <p class="tiny">© {datetime.datetime.now().year} AI Gaming Blog</p>
    </section>
    """

def build_review(game_name):
    # egyszerű, beágyazott review
    return f"<h2>{game_name} Full Review</h2><p>This is a detailed review of {game_name}. Gameplay, tips, and cheats included.</p>"

def generate_post_for_game(game,all_posts):
    name=game.get("name","Unknown Game")
    slug=slugify(name)
    filename=f"{slug}.html"
    out_path=os.path.join(OUTPUT_DIR,filename)
    if os.path.exists(out_path): return None

    img_url=game.get("background_image") or ""
    img_filename=f"{slug}.jpg"
    img_path=os.path.join(PICTURE_DIR,img_filename)
    if not os.path.exists(img_path):
        if img_url:
            if not download_image(img_url,img_path):
                download_image(f"https://placehold.co/800x450?text={name.replace(' ','+')}",img_path)
        else:
            download_image(f"https://placehold.co/800x450?text={name.replace(' ','+')}",img_path)

    youtube_embed=get_youtube_embed(name)
    review_html=build_review(name)
    now=datetime.datetime.now()
    title=f"{name} Full Review"
    cover_src=f"../{PICTURE_DIR}/{img_filename}"

    html=f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title}</title>
<style>
body{{background:#0b0f14;color:#eaf1f8;font-family:system-ui,sans-serif;}}
.wrap{{max-width:900px;margin:24px auto;padding:18px;background:#121821;border-radius:12px;border:1px solid #1f2a38}}
img.cover{{width:100%;border-radius:8px}}
h1{{font-size:28px}}
a{{color:#5cc8ff}}
.explore-grid{{display:flex;gap:12px;flex-wrap:wrap}}
.explore-item{{flex:1 1 calc(33.333% - 8px);border:1px solid #1f2a38;border-radius:8px;overflow:hidden;background:#0f141c}}
.explore-item img{{width:100%}}
.explore-item-title{{padding:6px;font-size:14px;text-align:center}}
</style>
</head>
<body>
<div class="wrap">
<a href="../index.html">⬅ Back</a>
<h1>{title}</h1>
<img class="cover" src="{cover_src}" alt="{name} cover"/>
{review_html}
<h2>Gameplay Video</h2>
<iframe width="100%" height="400" src="{youtube_embed}" frameborder="0" allowfullscreen></iframe>
{generate_more_to_explore([p for p in all_posts if p['title']!=name])}
{post_footer_html()}
</div>
</body>
</html>
"""
    with open(out_path,"w",encoding="utf-8") as f:
        f.write(html)

    return {
        "title":name,
        "url":f"{OUTPUT_DIR}/{filename}",
        "platform":[safe_get(p,'platform','name','') for p in game.get('platforms',[])] if game.get('platforms') else [],
        "date":now.strftime("%Y-%m-%d %H:%M:%S"),
        "rating":round(random.uniform(2.5,5.0),1),
        "cover":f"{PICTURE_DIR}/{img_filename}",
        "views":0,
        "comments":0
    }

def gather_candidates(total_needed,num_popular):
    popular=[]
    page=1
    while len(popular)<num_popular and page<5:
        res=rawg_get_popular(page)
        if not res: break
        popular.extend(res)
        page+=1
    popular=popular[:num_popular]

    random_candidates=[]
    attempts=0
    while len(random_candidates)<(total_needed-len(popular)) and attempts<10:
        page=random.randint(1,20)
        res=rawg_search_random(page)
        random_candidates.extend(res)
        attempts+=1
    random.shuffle(random_candidates)
    random_candidates=random_candidates[:total_needed-len(popular)]
    return random_candidates,popular

def main():
    all_posts=read_index_posts()
    random_candidates,popular_candidates=gather_candidates(NUM_TOTAL,NUM_POPULAR)
    selected_games=popular_candidates+random_candidates
    for g in selected_games:
        post=generate_post_for_game(g,all_posts)
        if post: all_posts.append(post)
    all_posts.sort(key=lambda x:x.get("date",""),reverse=True)
    write_index_posts(all_posts)
    print("✅ Posts generated and index updated.")

if __name__=="__main__":
    main()
