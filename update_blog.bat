@echo off
cd /d C:\ai_blog

:: Virtuális környezet aktiválása
call ai-env\Scripts\activate.bat

:: Régi posztok törlése
echo ===============================
echo 🗑 Régi posztok törlése...
echo ===============================
if exist generated_posts rmdir /s /q generated_posts
mkdir generated_posts

:: Blog újragenerálása (pl. 12 poszt)
echo ===============================
echo 📝 Új posztok generálása...
echo ===============================
python generate_and_save.py --num_posts 12

:: GitHub commit és push
echo ===============================
echo 🚀 Feltöltés GitHubra...
echo ===============================
git add .
git commit -m "Automatikus frissítés új HTML posztokkal %date% %time%"
git push origin main

echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================

pause
