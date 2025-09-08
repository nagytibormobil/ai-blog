@echo off
REM ====================================================
REM Smart GitHub Pages rebuild trigger
REM Only commits if there are real changes
REM ====================================================

set REPO_DIR=C:\ai_blog
set BRANCH=main

echo ===== Starting GitHub Pages update =====
cd /d %REPO_DIR%

REM Ensure on main branch
git checkout %BRANCH%

REM Check if there are changes
git status --porcelain > temp_status.txt
set /p STATUS_CHECK=<temp_status.txt
del temp_status.txt

if "%STATUS_CHECK%"=="" (
    echo No changes detected. Nothing to commit.
) else (
    echo Changes detected. Committing and pushing...
    git add .
    git commit -m "Auto-update for GitHub Pages: %date% %time%"
    git push origin %BRANCH%
    echo ✅ Changes pushed. GitHub Pages build should start automatically.
)

pause
