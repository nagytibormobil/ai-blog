@echo off
REM ===== Aktiválja a virtuális környezetet, ha szükséges =====
REM call ai-env\Scripts\activate.bat

SET REPO_DIR=C:\ai_blog
SET GENERATED_DIR=%REPO_DIR%\generated_posts
SET PICTURE_DIR=%REPO_DIR%\Picture
SET INDEX_FILE=%REPO_DIR%\index.html

REM ===== 1. Törli az összes HTML fájlt a generated_posts mappából =====
del /Q "%GENERATED_DIR%\*.html"

REM ===== 2. Törli az összes képet a Picture mappából =====
del /Q "%PICTURE_DIR%\*.jpg"

REM ===== 3. Teljesen eltávolítja a generated_posts mappát =====
rmdir /S /Q "%GENERATED_DIR%"

REM ===== 4. Újra létrehozza a generated_posts mappát =====
mkdir "%GENERATED_DIR%"

REM ===== 5. Index.html POSTS tömb kiürítése =====
powershell -Command ^
"(gc '%INDEX_FILE%') -replace '(?s)const POSTS = \[.*?\];', 'const POSTS = [];' | Out-File -Encoding UTF8 '%INDEX_FILE%'"

REM ===== 6. Git műveletek =====
cd /d "%REPO_DIR%"
git add -A
git commit -m "Teljesen törölve a generated_posts és a POSTS tömb az index.html-ből"
git push origin main

echo.
echo ✅ Minden poszt törölve, az index.html frissítve, a repository push-olva!
pause


