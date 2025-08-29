@echo off
cd /d C:\ai_blog

:: Virtuális környezet aktiválás
call ai-env\Scripts\activate.bat

:: Új poszt generálása (ha több kell: --num_posts 5 stb.)
python generate_and_save.py --num_posts 1

:: Index.html frissítése posts.json alapján
python rebuild_index.py

:: Git feltöltés
git add .
git commit -m "Automatikus frissítés új posztokkal és index frissítéssel"
git push origin main

echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================
