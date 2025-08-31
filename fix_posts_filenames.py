# fix_posts_filenames.py
import os, json, re, shutil, argparse
from urllib.parse import unquote
from datetime import datetime
import subprocess

BASE_DIR = r"C:\Users\User\OneDrive\ai_blog"
POST_DIR = os.path.join(BASE_DIR, "generated_posts")
POSTS_JSON = os.path.join(BASE_DIR, "posts.json")
REBUILD_SCRIPT = os.path.join(BASE_DIR, "rebuild_index.py")  # ha van

def backup_file(path):
    if os.path.exists(path):
        bak = f"{path}.bak.{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(path, bak)
        print(f"Backup készítve: {bak}")

def sanitize_name(name):
    # decode esetleges %-os kódolást
    name = unquote(name)
    base, ext = os.path.splitext(name)
    # Windows tiltott karakterek: <>:"/\\|?*
    base = re.sub(r'[<>:"/\\\\|?*\n\r\t]+', '-', base)
    base = re.sub(r'\s+', '-', base)          # szóköz -> -
    base = re.sub(r'-{2,}', '-', base)        # többszörös - -> egy -
    base = base.strip('-.')
    return base + ext

def find_generated_filename_in_obj(obj):
    s = json.dumps(obj, ensure_ascii=False)
    m = re.search(r'generated_posts/([^"\']+?\.html)', s)
    return m.group(1) if m else None

def replace_in_obj(obj, old, new):
    if isinstance(obj, dict):
        for k,v in list(obj.items()):
            if isinstance(v, str):
                if old in v:
                    obj[k] = v.replace(old, new)
            else:
                replace_in_obj(v, old, new)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str):
                if old in v:
                    obj[i] = v.replace(old, new)
            else:
                replace_in_obj(v, old, new)

def main(dry_run=True, apply_changes=False, rebuild=False, remove_missing=False):
    if not os.path.exists(POSTS_JSON):
        print("posts.json nem található:", POSTS_JSON)
        return
    backup_file(POSTS_JSON)
    with open(POSTS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    kept = []
    removed_entries = []
    changed = []
    total = 0

    if isinstance(data, dict) and "posts" in data and isinstance(data["posts"], list):
        entries = data["posts"]
        container_type = "posts"
    elif isinstance(data, list):
        entries = data
        container_type = "list"
    else:
        # általános eset: kezeljük maga a data-t, mint lista
        entries = data
        container_type = "list"

    for entry in entries:
        total += 1
        found = find_generated_filename_in_obj(entry)
        if not found:
            kept.append(entry)
            continue

        orig_filename = found
        orig_path = os.path.join(POST_DIR, orig_filename)
        safe_filename = sanitize_name(orig_filename)
        safe_path = os.path.join(POST_DIR, safe_filename)

        # ellenőrzések
        exists_orig = os.path.exists(orig_path)
        exists_safe = os.path.exists(safe_path)

        if exists_orig:
            action = f"FOUND orig file: {orig_filename} -> will rename to {safe_filename}"
            if dry_run:
                print("[DRY] " + action)
            else:
                os.rename(orig_path, safe_path)
                print("[RENAMED] " + action)
            # update entry
            replace_in_obj(entry, orig_filename, safe_filename)
            changed.append((orig_filename, safe_filename))
            kept.append(entry)
        elif exists_safe:
            action = f"Found safe file already: {safe_filename} (updating posts.json)"
            print(action if not dry_run else "[DRY] " + action)
            replace_in_obj(entry, orig_filename, safe_filename)
            changed.append((orig_filename, safe_filename))
            kept.append(entry)
        else:
            # semmi nincs -- hiányzó fájl
            msg = f"MISSING file for entry: {orig_filename}"
            print(msg)
            if remove_missing and apply_changes:
                removed_entries.append(entry)
                print(" -> bejegyzés eltávolítva (remove_missing=True).")
            else:
                # megtartjuk a bejegyzést, csak jelzünk
                kept.append(entry)
    # kész adat összeállítása
    if container_type == "posts":
        data_out = {"posts": kept}
    else:
        data_out = kept

    out_path = POSTS_JSON if apply_changes else POSTS_JSON + ".cleaned.json"
    if apply_changes:
        # backup már készült fent
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data_out, f, ensure_ascii=False, indent=2)
        print(f"posts.json frissítve: {out_path}")
    else:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data_out, f, ensure_ascii=False, indent=2)
        print(f"[DRY-RUN] Új fájl készítve: {out_path} (nem léptetve életbe)")

    if rebuild and apply_changes and os.path.exists(REBUILD_SCRIPT):
        print("Index újragenerálása rebuild_index.py-vel...")
        subprocess.run(["python", REBUILD_SCRIPT], cwd=BASE_DIR)
        print("Újraépítés lefutott (ha a script sikeres volt).")
    elif rebuild and not os.path.exists(REBUILD_SCRIPT):
        print("Nincs rebuild_index.py a projektben, ezért nem lehet automatikusan újragenerálni.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix posts.json / generated_posts filename mismatches")
    parser.add_argument("--apply", action="store_true", help="Alkalmazza a változtatásokat (felülírja posts.json és átnevezi fájlokat).")
    parser.add_argument("--rebuild", action="store_true", help="apply mellett: futtatja a rebuild_index.py-t a index újragenerálásához.")
    parser.add_argument("--remove-missing", action="store_true", help="apply mellett: eltávolítja a teljes bejegyzést, ha nincs hozzá fájl.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Csak listáz, alapértelmezett. Használd --apply-vel a módosításhoz.")
    args = parser.parse_args()
    # ha --apply nincs meg, akkor dry-run marad True
    main(dry_run=not args.apply, apply_changes=args.apply, rebuild=args.rebuild, remove_missing=args.remove_missing)
