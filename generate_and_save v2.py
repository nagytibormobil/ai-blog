def rawg_search_random(page=1, page_size=RAWG_PAGE_SIZE):
    url = "https://api.rawg.io/api/games"
    params = {"key": RAWG_API_KEY, "page": page, "page_size": page_size}
    headers = {"User-Agent": USER_AGENT}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        results = r.json().get("results", [])
        print(f"[DEBUG] RAWG random search page {page} returned {len(results)} games")
        return results
    except Exception as e:
        print(f"[ERROR] RAWG random search failed: {e}")
        return []

def rawg_get_popular(page=1, page_size=RAWG_PAGE_SIZE):
    url = "https://api.rawg.io/api/games"
    params = {"key": RAWG_API_KEY, "page": page, "page_size": page_size, "ordering": "-added"}
    headers = {"User-Agent": USER_AGENT}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        results = r.json().get("results", [])
        print(f"[DEBUG] RAWG popular search page {page} returned {len(results)} games")
        return results
    except Exception as e:
        print(f"[ERROR] RAWG popular search failed: {e}")
        return []

def generate_post_for_game(game):
    name = game.get("name") or "Unknown Game"
    slug = slugify(name)
    filename = f"{slug}.html"
    out_path = os.path.join(OUTPUT_DIR, filename)
    print(f"[DEBUG] Generating post for: {name} (slug: {slug}) -> {filename}")

    if os.path.exists(out_path):
        print(f"[DEBUG] Post already exists, skipping: {out_path}")
        return None

    img_url = game.get("background_image") or game.get("background_image_additional") or ""
    img_filename = f"{slug}.jpg"
    img_path = os.path.join(PICTURE_DIR, img_filename)

    if not os.path.exists(img_path):
        if img_url:
            ok = download_image(img_url, img_path)
            if ok:
                print(f"[DEBUG] Image downloaded: {img_filename}")
            else:
                print(f"[WARNING] Image download failed for {img_filename}")
        else:
            print(f"[WARNING] No image URL for {name}, creating placeholder")
            ph_url = f"https://placehold.co/800x450?text={name.replace(' ', '+')}"
            download_image(ph_url, img_path)
    else:
        print(f"[DEBUG] Image already exists: {img_filename}")

    # További debug: YouTube embed
    youtube_embed = get_youtube_embed(name)
    print(f"[DEBUG] YouTube embed URL: {youtube_embed}")

    # HTML generálás
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("<html>DEBUG CONTENT</html>")  # Ide jön a teljes HTML kód
        print(f"[DEBUG] HTML post created: {out_path}")
    except Exception as e:
        print(f"[ERROR] Failed to write HTML: {e}")

    return {"title": name, "url": filename}
