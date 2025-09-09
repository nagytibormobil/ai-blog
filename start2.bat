@echo off
REM ===============================
REM Weboldal frissítése GitHub Pages-re (index, postok, képek)
REM ===============================

cd /d C:\ai_blog

REM Git státusz kiíratása
git status

REM Add hozzá az összes változást
git add -A

REM Commit üzenet dátummal
git commit -m "Manual update: %date% %time%"

REM Push a main branch-re
git push origin main

echo.
echo ✅ Weboldal frissítve a GitHub Pages-en!
