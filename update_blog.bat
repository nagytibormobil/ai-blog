@echo off
cd /d C:\ai_blog

:: Generál 5 új HTML posztot
py generate_and_save.py --num_posts 5

:: Frissít GitHubra
git add .
git commit -m "Automatikus frissítés új HTML posztokkal"
git push

echo.
echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================
