@echo off
REM ===============================
REM GitHub Pages frissítés batch fájl
REM ===============================

REM 1. Menj a repo könyvtárába
cd /d "%~dp0"

REM 2. Helyi változások hozzáadása
echo Adding new generated posts and index...
git add generated_posts/ index.html

REM 3. Commit üzenet a frissítéshez
set /p COMMITMSG=Enter commit message (or leave empty for default): 
if "%COMMITMSG%"=="" set COMMITMSG=Update posts for new style

git commit -m "%COMMITMSG%"

REM 4. Push a main branch-re
echo Pushing to GitHub...
git push origin main

REM 5. Pages újra build (trigger a commit által)
echo GitHub Pages should rebuild automatically after push.
echo If changes do not appear, hard-refresh your browser (Ctrl+Shift+R).

pause
