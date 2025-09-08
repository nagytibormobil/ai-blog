@echo off
setlocal

REM --- CONFIG ---
set REPO_DIR=C:\ai_blog
set PAGES_URL=https://nagytibormobil.github.io/ai-blog/

echo ===== Starting update_and_open_pages =====

REM --- Navigate to repo ---
cd /d "%REPO_DIR%" || (
    echo ERROR: Repository directory not found: %REPO_DIR%
    pause
    exit /b 1
)

REM --- Pull latest changes ---
echo --- Git pull ---
git checkout main
git pull

REM --- Show last commit ---
echo --- Last commit ---
git log -1 --oneline

REM --- Open GitHub Pages ---
echo --- Opening GitHub Pages ---
start "" "%PAGES_URL%"

echo ===== Done =====
pause
