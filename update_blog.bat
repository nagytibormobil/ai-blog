@echo off
REM ==========================================
REM AI Gaming Blog – Automatikus frissítés
REM ==========================================

cd /d C:\ai_blog

REM Aktiváljuk a Python virtuális környezetet
call ai-env\Scripts\activate.bat

REM Generáljunk 3 új HTML posztot
python generate_and_save.py --num_posts 3

REM Git commit & push automatikusan
git add .
git commit -m "Automatikus frissítés új HTML posztokkal"
git push

echo.
echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================
pause
