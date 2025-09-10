@echo off
cd /d C:\ai_blog

echo --- YouTube javítás futtatása ---
python youtubefix.py

echo --- Git változtatások hozzáadása ---
git add .

:: Commit a mai dátummal és idővel
for /f "tokens=1-4 delims=/:. " %%a in ("%date% %time%") do (
    set TODAY=%%a-%%b-%%c
    set NOW=%%d-%%e-%%f
)
git commit -m "YouTube javítás és HTML update !TODAY! !NOW!" 2>nul

echo --- Git push a GitHub-ra ---
git push origin main --force

echo --- Kész! ---
pause
