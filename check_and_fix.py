import os
import shutil
import subprocess
import datetime
import sys

BASE_DIR = r"C:\ai_blog"           # a te projekt gyökérmappád
AI_DIR = os.path.join(BASE_DIR, "ai")
ROOT_INDEX = os.path.join(BASE_DIR, "index.html")

def find_best_index():
    candidates = [
        os.path.join(AI_DIR, "index.html"),
        os.path.join(BASE_DIR, "index.html"),
        os.path.join(BASE_DIR, "ai-blog", "index.html"),
    ]
    existing = [p for p in candidates if os.path.exists(p)]
    if not existing:
        return None
    existing.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return existing[0]

def backup(path):
    if os.path.exists(path):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new = f"{path}_backup_{ts}"
        print(f"📦 Mentés: '{path}' -> '{new}'")
        shutil.move(path, new)

def copy_index(src, dst):
    print(f"📄 Index másolása: {src} -> {dst}")
    backup(dst)
    shutil.copy2(src, dst)

def copy_tree(src, dst):
    if not os.path.exists(src):
        print(f"⚠️ Forrás nem létezik: {src}  — kihagyva.")
        return False
    # ha létezik cél, mentsük el
    backup(dst)
    print(f"📁 Mappa másolása: {src} -> {dst}")
    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", "ai"))
    return True

def git_remote_info():
    try:
        p = subprocess.run(["git", "-C", BASE_DIR, "remote", "-v"], capture_output=True, text=True, check=True)
        return p.stdout.strip()
    except Exception as e:
        return f"(git remote lekérdezés sikertelen: {e})"

def git_commit_and_push(msg):
    try:
        subprocess.run(["git", "-C", BASE_DIR, "add", "."], check=True)
        subprocess.run(["git", "-C", BASE_DIR, "commit", "-m", msg], check=False)
        subprocess.run(["git", "-C", BASE_DIR, "push"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git hiba: {e}")
        return False

def main():
    print("📂 Ellenőrzés: források és célok...")
    if not os.path.exists(BASE_DIR):
        print(f"❌ Hiányzik a BASE_DIR: {BASE_DIR}")
        sys.exit(1)

    best_index = find_best_index()
    if not best_index:
        print("❌ Nem található index.html sehol (se base, se ai).")
    else:
        if os.path.abspath(best_index) != os.path.abspath(ROOT_INDEX):
            copy_index(best_index, ROOT_INDEX)
        else:
            print("ℹ️ Az index.html már a gyökérben van és aktuális.")

    # generated_posts mappa szinkron
    src_generated = None
    for candidate in [os.path.join(AI_DIR, "generated_posts"), os.path.join(BASE_DIR, "generated_posts")]:
        if os.path.exists(candidate):
            src_generated = candidate
            break
    if src_generated:
        copy_tree(src_generated, os.path.join(BASE_DIR, "generated_posts"))
    else:
        print("⚠️ Nincs generated_posts mappa sehol (kihagyva).")

    # Picture mappa szinkron
    src_picture = None
    for candidate in [os.path.join(AI_DIR, "Picture"), os.path.join(BASE_DIR, "Picture"), os.path.join(BASE_DIR, "Picture postok")]:
        if os.path.exists(candidate):
            src_picture = candidate
            break
    if src_picture:
        copy_tree(src_picture, os.path.join(BASE_DIR, "Picture"))
    else:
        print("⚠️ Nincs Picture mappa sehol (kihagyva).")

    print("\n🔎 Git távoli (remote) információk:")
    remote_info = git_remote_info()
    print(remote_info)
    if "ai-blog.git" not in remote_info and "ai-blog" not in remote_info:
        print("\n⚠️ Figyelem: a remote nem tűnik a 'nagytibormobil/ai-blog' repo-nak.")
        print("Ha a remote rossz, ezt a parancsot futtasd (helyesen beállítva a címet):")
        print("    git -C C:\\ai_blog remote set-url origin https://github.com/nagytibormobil/ai-blog.git")

    print("\n⬆️ Git commit & push indítása...")
    ok = git_commit_and_push("Auto publish: sync index + generated_posts for ai-blog")
    if ok:
        print("✅ Feltöltve a távoli repóba.")
    else:
        print("❌ A feltöltés nem sikerült — nézd meg a hibát fentebb.")

if __name__ == "__main__":
    main()
