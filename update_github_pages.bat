@echo off
chcp 65001
setlocal

REM ---------- Paths ----------
set REPO_DIR=C:\ai_blog
set GENERATED_DIR=%REPO_DIR%\generated_posts
set PICTURE_DIR=%REPO_DIR%\Picture

REM ---------- 1. Törlés ----------
echo 🔹 Törlés...
del /Q "%GENERATED_DIR%\*.html"
del /Q "%PICTURE_DIR%\*.jpg"
rmdir /S /Q "%GENERATED_DIR%"
mkdir "%GENERATED_DIR%"

REM ---------- 2. Repo update ----------
cd /d %REPO_DIR%
echo 🔹 Git pull...
git checkout main
git pull

REM ---------- 3. Commit changes ----------
git add -A
git commit -m "Clean generated posts for rebuild" 2>nul
git push origin main

REM ---------- 4. Trigger GitHub Pages rebuild ----------
echo 🔹 Trigger GitHub Pages rebuild...
REM Üres commit a build újraindításához
git commit --allow-empty -m "Trigger GitHub Pages rebuild"
git push origin main

echo.
echo ✅ GitHub Pages rebuild triggered!
pause
endlocal
