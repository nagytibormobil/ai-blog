@echo off
cd /d C:\ai_blog

:: Aktiváljuk a Python virtuális környezetet
call ai-env\Scripts\activate.bat

:: Generál új HTML posztokat
python generate_and_save.py --num_posts 1

:: GitHub frissítés és feltöltés
git add .
git commit -m "Automatikus frissítés új HTML posztokkal"
git push origin main

echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================
