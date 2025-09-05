from flask import Flask, request, jsonify
from pathlib import Path
import json
import datetime
import re

app = Flask(__name__)

COMMENT_DIR = Path("comments")
COMMENT_DIR.mkdir(exist_ok=True)

# egyszerű csúnya szó lista
BAD_WORDS = ["csunya1","csunya2","badword"]

def moderate_comment(name, text):
    pattern = re.compile("|".join(BAD_WORDS), re.IGNORECASE)
    if pattern.search(name) or pattern.search(text):
        return False
    # linkek tilalma
    if re.search(r"(http[s]?://|www\.|\.com|\.net|\.org)", text):
        return False
    return True

@app.route("/api/comments/<slug>", methods=["GET"])
def get_comments(slug):
    file = COMMENT_DIR / f"{slug}.json"
    if not file.exists():
        return jsonify([])
    with file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/comment", methods=["POST"])
def post_comment():
    data = request.get_json()
    slug = data.get("slug")
    name = data.get("name","").strip()
    text = data.get("text","").strip()

    if not slug or not name or not text:
        return jsonify(success=False, message="Missing fields"), 400

    if not moderate_comment(name, text):
        return jsonify(success=False, message="Comment contains forbidden words or links."), 403

    file = COMMENT_DIR / f"{slug}.json"
    comments = []
    if file.exists():
        with file.open("r", encoding="utf-8") as f:
            comments = json.load(f)
    new_comment = {"name": name, "text": text, "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
    comments.append(new_comment)
    with file.open("w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

    return jsonify(success=True, comments=comments)
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)
