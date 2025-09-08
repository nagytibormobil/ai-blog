@echo off
REM ==============================
REM Move index.html to root and push
REM ==============================

REM Beállítjuk a repo könyvtárat
set REPO_DIR=C:\ai_blog
cd /d %REPO_DIR%

REM Ellenőrizzük, hogy van-e index.html a generated_posts mappában
if exist "generated_posts\index.html" (
    echo 🔹 Moving index.html from generated_posts to root...
    move /Y "generated_posts\index.html" "%REPO_DIR%\index.html"
) else (
    echo ⚠️  No index.html found in generated_posts. Exiting.
    pause
    exit /b
)

REM Git műveletek
echo 🔹 Adding index.html to git...
git add index.html

echo 🔹 Committing changes...
git commit -m "Move index.html to root for GitHub Pages"

echo 🔹 Pushing to main branch...
git push origin main

echo.
echo ✅ index.html moved to root and pushed. GitHub Pages build should start shortly.
pause
