@echo off
setlocal enabledelayedexpansion

echo ===== Checking GitHub Remote and Pages Settings =====
set REPO_DIR=C:\ai_blog
cd /d %REPO_DIR%

:: lekérdezi a remote URL-t
for /f "tokens=2" %%i in ('git remote get-url origin') do (
    set CURRENT_REMOTE=%%i
)

echo Current remote: %CURRENT_REMOTE%

:: helyes repo URL
set CORRECT_REMOTE=https://github.com/nagytibormobil/ai-blog.git

if /i "%CURRENT_REMOTE%"=="%CORRECT_REMOTE%" (
    echo Remote is already correct: %CURRENT_REMOTE%
) else (
    echo Remote mismatch detected!
    echo Changing remote from:
    echo    %CURRENT_REMOTE%
    echo to:
    echo    %CORRECT_REMOTE%
    git remote set-url origin %CORRECT_REMOTE%
)

echo.
echo --- Pulling latest changes ---
git pull origin main

echo.
echo --- Staging local changes ---
git add .

echo.
echo --- Committing ---
git commit -m "Auto update via script" || echo Nothing to commit

echo.
echo --- Pushing to correct repo ---
git push origin main

echo.
echo ===== DONE. Check your site at =====
echo https://nagytibormobil.github.io/ai-blog/index.html
pause
