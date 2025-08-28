@echo off
cd /d C:\ai_blog

:: Aktiváld a virtuális környezetet
call ai-env\Scripts\activate.bat

:: Generál 5 új HTML posztot placeholder képekkel
python generate_and_save.py --num_posts 5

:: Frissít GitHubra
git add .
git commit -m "Automatikus frissítés új HTML posztokkal"
git push

echo.
echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================
pause
