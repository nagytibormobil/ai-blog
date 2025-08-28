@echo off
cd /d C:\ai_blog

:: Aktiváljuk a virtuális környezetet
call ai-env\Scripts\activate.bat

:: Generáljunk 5 új SEO-barát HTML posztot képekkel és releváns YouTube videókkal
python generate_and_save.py --num_posts 5

:: Frissítjük és feltöltjük GitHubra
git add .
git commit -m "Automatikus frissítés - új SEO-barát posztok"
git push

echo.
echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================
