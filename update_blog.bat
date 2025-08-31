@echo off
cd /d C:\ai_blog

REM enable delayed expansion for variable math in loops
setlocal enabledelayedexpansion

echo ===============================
echo 🔹 Virtuális környezet aktiválása...
echo ===============================
call ai-env\Scripts\activate.bat

echo ===============================
echo 🔹 Új posztok generálása 12 db (lépcsőzetesen)...
echo ===============================

REM Generálás 4-es blokkokban, hogy ne akadjon le
set TOTAL=12
for /L %%i in (1,4,%TOTAL%) do (
    set /a remaining=%TOTAL%-%%i+1
    if !remaining! GTR 3 (
        set /a to_generate=4
    ) else (
        set /a to_generate=!remaining!
    )
    echo 🔹 Generálás %%i - %%i+!to_generate!-1 (összesen !to_generate! poszt)
    python generate_and_save.py --num_posts !to_generate!
)

echo ===============================
echo 🔹 Git add/commit/push (új képek és posztok)...
echo ===============================
git add .
git commit -m "Automatikus frissítés új HTML posztokkal és képekkel"
git push origin main

echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================
endlocal
