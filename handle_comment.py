#!/usr/bin/env python3
# handle_comment.py
# Kommentek kezelése minden poszthoz, moderációval és CORS engedéllyel

import os
import json
import datetime
import re
from flask import Flask, request, jsonify
from flask_cors import CORS  # ← CORS importálása

# Mindig ide mentjük a kommenteket
COMMENT_DIR = r"C:\ai_blog\comments"
os.makedirs(COMMENT_DIR, exist_ok=True)

# Szabályok
MAX_COMMENTS_PER_DAY = 15
MAX_NAME_LENGTH = 12
MAX_COMMENT_LENGTH = 200

FORBIDDEN_PATTERNS = [
    r"http[s]?://",        # semmilyen link
    r"\.com", r"\.net", r"\.org", r"\.ru", r"\.cn",
    r"fuck", r"shit", r"bitch",  # csúnya szavak
    r"nigger", r"hitler", r"terror", r"isis",
    r"drug", r"cocaine", r"heroin", r"sex", r"porn"
]

def is_valid_comment(name, text):
    """Komment moderációs szabályok"""
    if not name or not text:
        return False
    if len(name) > MAX_NAME_LENGTH or len(text) > MAX_COMMENT_LENGTH:
        return False
    for pat in FORBIDDEN_PATTERNS:
        if re.search(pat, name, re.IGNORECASE) or re.search(pat, text, re.IGNORECASE):
            return False
    return True

def save_comment(slug, name, text):
    """Komment mentése adott poszthoz (slug alapján)"""
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")

    filepath = os.path.join(COMMENT_DIR, f"{slug}.json")
    comments = []

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                comments = json.load(f)
            except:
                comments = []

    # napi limit
    todays_comments = [c for c in comments if c["date"].startswith(today)]
    if len(todays_comments) >= MAX_COMMENTS_PER_DAY:
        return False, "Daily limit reached."

    # új komment
    comment = {
        "name": name[:MAX_NAME_LENGTH],
        "text": text[:MAX_COMMENT_LENGTH],
        "date": now.strftime("%Y-%m-%d %H:%M:%S")
    }

    comments.append(comment)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(comments, f, indent=2, ensure_ascii=False)

    return True, "Comment saved."

# =========================
# Flask API
# =========================
app = Flask(__name__)
CORS(app)  # ← CORS engedélyezése minden oldalról

@app.route("/api/comment", methods=["POST"])
def api_comment():
    data = request.get_json(force=True)
    slug = data.get("slug", "").strip()
    name = data.get("name", "").strip()
    text = data.get("text", "").strip()

    if not is_valid_comment(name, text):
        return jsonify({"success": False, "message": "Rejected by moderation."})

    ok, msg = save_comment(slug, name, text)
    return jsonify({"success": ok, "message": msg})

# Példa futtatás parancssorból
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add a comment to a post.")
    parser.add_argument("slug", help="Post slug (pl. jatek-neve)")
    parser.add_argument("name", help="Kommentelő neve (max 12 karakter)")
    parser.add_argument("text", help="Komment szöveg (max 200 karakter)")

    args = parser.parse_args()

    if not is_valid_comment(args.name, args.text):
        print("❌ Comment rejected by moderation rules.")
    else:
        ok, msg = save_comment(args.slug, args.name, args.text)
        if ok:
            print("✅", msg)
        else:
            print("❌", msg)

    # Flask szerver indítása
    # API indítása pl. http://127.0.0.1:5000/api/comment
    app.run(host="0.0.0.0", port=5000, debug=True)
