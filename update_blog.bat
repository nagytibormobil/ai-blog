@echo off
cd /d C:\ai_blog
call ai-env\Scripts\activate.bat

REM fix: poszt szám beállítása
set NUM_POSTS=12
python generate_and_save.py --num_posts %NUM_POSTS%

REM affiliate blokk hozzáadása
python append_affiliate.py

git add .
git commit -m "Automatikus frissítés új HTML posztokkal"
git push origin main

echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================
pause
