@echo off
chcp 65001
cd /d C:\ai_blog

REM Enable delayed expansion for variable math in loops
setlocal enabledelayedexpansion

echo ===============================
echo 🔹 Virtuális környezet aktiválása...
echo ===============================
call ai-env\Scripts\activate.bat

echo ===============================
echo 🔹 Új posztok generálása 12 db (lépcsőzetesen)...
echo ===============================

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
echo 🔹 Git commit és push automatikusan SSH kulccsal...
echo ===============================
if exist .git (
    git add .
    git commit -m "Automatikus frissítés új HTML posztokkal és képekkel"
    git push origin main
    if errorlevel 1 (
        echo ⚠️ Hiba történt a git push során. Ellenőrizd az SSH kulcsot vagy GitHub CLI hitelesítést.
    ) else (
        echo ✅ Változások feltöltve a GitHub repository-ba.
    )
) else (
    echo ⚠️ Nincs git repository, a weboldal nem frissül online.
)

echo ===============================
echo 🔹 Kész! A GitHub Pages frissítése 1-5 perc alatt várható...
echo ===============================
endlocal
pause
