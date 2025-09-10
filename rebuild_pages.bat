@echo off
REM ==========================================
REM Rebuild GitHub Pages with new style posts
REM ==========================================

REM 1. Menj a repo könyvtárába
cd /d "%~dp0"

REM 2. (Opcionális) Töröld a régi generált postokat, ha teljesen tiszta build kell
echo Deleting old generated posts...
rd /s /q generated_posts
mkdir generated_posts

REM 3. Futassuk az új generate_and_save.py-t
echo Generating new posts with updated style...
python generate_and_save.py

REM 4. Helyi változások hozzáadása
echo Adding new generated posts and index...
git add generated_posts/ index.html

REM 5. Commit üzenet
set /p COMMITMSG=Enter commit message (or leave empty for default): 
if "%COMMITMSG%"=="" set COMMITMSG=Update posts with new style

git commit -m "%COMMITMSG%"

REM 6. Push a main branch-re
echo Pushing to GitHub...
git push origin main

REM 7. Hard-refresh Pages cache trigger (Chrome, Firefox, Edge)
echo GitHub Pages should rebuild automatically.
echo After push, do a hard-refresh in your browser (Ctrl+Shift+R) to see changes.

pause
