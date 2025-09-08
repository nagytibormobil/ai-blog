@echo off
REM ====================================================
REM Check GitHub Pages build status and trigger rebuild
REM Requires: GitHub CLI (https://cli.github.com/)
REM ====================================================

REM --- Settings ---
set REPO="nagytibormobil/ai-blog"
set BRANCH="main"

echo ===== Checking GitHub Pages build status =====

REM Get last Pages build info
gh run list --repo %REPO% --workflow "pages build and deployment" --limit 1 --json status,name,conclusion > last_run.json

for /f "tokens=*" %%i in ('type last_run.json') do set LAST_RUN=%%i

echo Last run info: %LAST_RUN%

REM Check if last run is "waiting" or "failure"
echo Checking for errors or canceled runs...

REM Using findstr to see if status is queued or in_progress
type last_run.json | findstr /i "queued in_progress failure cancelled" > nul
if %errorlevel%==0 (
    echo WARNING: Last Pages build is still queued or failed. Triggering new build...
    
    REM Trigger a dummy commit to restart Pages build
    git add .
    git commit -m "Trigger GitHub Pages rebuild: %date% %time%" > nul 2>&1
    git push origin %BRANCH%
    
    echo ✅ Triggered rebuild. Wait a few minutes and refresh your Pages site.
) else (
    echo ✅ Last Pages build completed successfully.
)

del last_run.json
pause
