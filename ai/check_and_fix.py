import os
import shutil
import subprocess

# Alap mappa
BASE_DIR = r"C:\ai_blog"
AI_BLOG = BASE_DIR   # nincs almappa, maga a gyökérmappa a "blog"
AI_DIR = os.path.join(BASE_DIR, "ai")

def check_dirs():
    print("📂 Könyvtárak ellenőrzése...")
    if not os.path.exists(BASE_DIR):
        print(f"❌ Hiányzik: {BASE_DIR}")
        return False
    if not os.path.exists(os.path.join(BASE_DIR, "index.html")):
        print("⚠️ Figyelem: nincs index.html a főkönyvtárban!")
    return True

def sync_ai():
    print("🔄 Szinkronizálás: ai_blog ➝ ai")
    if os.path.exists(AI_DIR):
        shutil.rmtree(AI_DIR)
    shutil.copytree(AI_BLOG, AI_DIR, ignore=shutil.ignore_patterns(".git", "ai"))
    print("✅ Másolás kész.")

def git_push():
    print("⬆️ Git feltöltés...")
    try:
        subprocess.run(["git", "-C", BASE_DIR, "add", "."], check=True)
        subprocess.run(["git", "-C", BASE_DIR, "commit", "-m", "Auto fix ai site"], check=False)
        subprocess.run(["git", "-C", BASE_DIR, "push"], check=True)
        print("✅ Feltöltve GitHub-ra.")
    except Exception as e:
        print(f"❌ Git hiba: {e}")

if __name__ == "__main__":
    if check_dirs():
        sync_ai()
        git_push()
