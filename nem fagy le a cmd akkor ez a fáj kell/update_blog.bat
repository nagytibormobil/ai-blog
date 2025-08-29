@echo off
cd /d C:\ai_blog

echo ===============================
echo 🔹 Virtuális környezet aktiválása...
echo ===============================
call ai-env\Scripts\activate.bat

echo ===============================
echo 🔹 Új posztok generálása 12 db (lépcsőzetesen)...
echo ===============================

REM Generálás 4-es blokkokban, hogy ne akadjon le
for /L %%i in (1,4,12) do (
    set /a to_generate=4
    REM Ha a maradék kevesebb, csak annyit generálunk
    set /a remaining=12-%%i+1
    if !remaining! LSS 4 set /a to_generate=!remaining!
    echo 🔹 Generálás %%i-től !to_generate! poszt
    python generate_and_save.py --num_posts !to_generate!
)

echo ===============================
echo 🔹 Affiliate blokk hozzáadása a posztokhoz...
echo ===============================
python append_affiliate.py

echo ===============================
echo 🔹 Git add/commit/push...
echo ===============================
git add .
git commit -m "Automatikus frissítés új HTML posztokkal"
git push origin main

echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================
pause
