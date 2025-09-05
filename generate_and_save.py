def generate_post_for_game(game):
    name = game.get("name") or "Unknown Game"
    slug = slugify(name)
    filename = f"{slug}.html"
    out_path = os.path.join(OUTPUT_DIR, filename)

    if os.path.exists(out_path):
        print(f"⚠️  Post already exists for '{name}' -> {filename} (skipping)")
        return None

    img_url = game.get("background_image") or game.get("background_image_additional") or ""
    img_filename = f"{slug}.jpg"
    img_path = os.path.join(PICTURE_DIR, img_filename)

    if os.path.exists(img_path):
        print(f"⚠️  Image already exists for '{name}' -> {img_filename} (skipping)")
        return None

    if img_url:
        ok = download_image(img_url, img_path)
        if not ok:
            ph_url = f"https://placehold.co/800x450?text={name.replace(' ', '+')}"
            download_image(ph_url, img_path)
    else:
        ph_url = f"https://placehold.co/800x450?text={name.replace(' ', '+')}"
        download_image(ph_url, img_path)

    youtube_embed = get_youtube_embed(name)

    year = game.get("released") or ""
    review_html = build_long_review(name, "the studio", year)
    cheats_html = generate_cheats_tips(name)
    age_rating = get_age_rating(game)

    now = datetime.datetime.now()
    title = f"{name} Cheats, Tips & Full Review"
    cover_src = f"../{PICTURE_DIR}/{img_filename}"
    footer_block = post_footer_html()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{title}</title>
  <meta name="description" content="Cheats, tips and a long review for {name}."/>
  <style>
    :root{{--bg:#0b0f14;--panel:#121821;--muted:#9fb0c3;--text:#eaf1f8;--accent:#5cc8ff;--card:#0f141c;--border:#1f2a38}}
    html,body{{margin:0;padding:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,Segoe UI,Roboto,Inter,Arial,sans-serif}}
    .wrap{{max-width:900px;margin:24px auto;padding:18px;background:var(--panel);border-radius:12px;border:1px solid var(--border)}}
    img.cover{{width:100%;height:auto;border-radius:8px;display:block}}
    h1{{margin:10px 0 6px;font-size:28px}}
    h2{{margin-top:18px}}
    p{{color:var(--text);line-height:1.6}}
    .tiny{{color:var(--muted);font-size:13px}}
    .ad{{background:linear-gradient(180deg,rgba(255,209,102,.06),transparent);padding:12px;border-radius:10px;border:1px dashed #ffd166;color:var(--text)}}
    a{{color:var(--accent)}}
    input,textarea{{background:var(--panel);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:6px;width:100%;margin-bottom:6px}}
    button{{padding:8px 12px;background:var(--accent);color:var(--bg);border:none;border-radius:6px;cursor:pointer}}
  </style>
</head>
<body>
  <div class="wrap">
    <a href="../index.html" style="color:var(--accent)">⬅ Back to Home</a>
    <h1>{title}</h1>
    <img class="cover" src="{cover_src}" alt="{name} cover"/>
    <h2>About the Game</h2>
    <ul>
      <li><strong>Release:</strong> {year}</li>
      <li><strong>Recommended Age:</strong> {age_rating}</li>
      <li><strong>Platforms:</strong> {', '.join([p['platform']['name'] for p in game.get('platforms', [])]) if game.get('platforms') else '—'}</li>
    </ul>
    <h2>Full Review</h2>
    {review_html}
    <h2>Gameplay Video</h2>
    <iframe width="100%" height="400" src="{youtube_embed}" frameborder="0" allowfullscreen></iframe>
    <h2>Cheats & Tips</h2>
    {cheats_html}

    <h2 class="tiny">AI Rating</h2>
    <p class="tiny">⭐ {round(random.uniform(2.5,5.0),1)}/5</p>

    <!-- Comments Section -->
    <h2>Comments</h2>
    <div id="comments-section">
      <form id="comment-form">
        <input type="text" id="comment-name" placeholder="Your name (max 10)" maxlength="10" required>
        <textarea id="comment-text" placeholder="Write a comment (max 200)" maxlength="200" required></textarea>
        <button type="submit">Post Comment</button>
      </form>
      <div id="comments-list"></div>
    </div>

    {footer_block}
  </div>

  <script>
    document.getElementById("comment-form").addEventListener("submit", function(e){
      e.preventDefault();
      const name = document.getElementById("comment-name").value.trim().substring(0,10);
      const text = document.getElementById("comment-text").value.trim().substring(0,200);
      if(!name || !text) return;

      const commentDiv = document.createElement("div");
      commentDiv.style.background = "#121821";
      commentDiv.style.color = "#eaf1f8";
      commentDiv.style.padding = "8px";
      commentDiv.style.marginBottom = "6px";
      commentDiv.style.borderRadius = "6px";
      commentDiv.innerHTML = `<strong>${name}:</strong> <span>${text}</span>`;

      document.getElementById("comments-list").prepend(commentDiv);

      document.getElementById("comment-form").reset();
    });
  </script>
</body>
</html>
"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    post_dict = {
        "title": name,
        "url": f"{OUTPUT_DIR}/{filename}",
        "platform": [p['platform']['name'] for p in game.get('platforms', [])] if game.get('platforms') else [],
        "date": now.strftime("%Y-%m-%d"),
        "rating": round(random.uniform(2.5,5.0),1),
        "cover": f"{PICTURE_DIR}/{img_filename}",
        "views": 0,
        "comments": 0
    }
    print(f"✅ Generated post: {out_path}")
    return post_dict
