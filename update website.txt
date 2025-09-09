@echo off
cd /d C:\ai_blog

echo ---- Valtozasok hozzaadasa ----
git add -A

echo ---- Commit keszitese ----
git commit -m "Automatikus frissites: %date% %time%"

echo ---- Feltoltes a GitHub-ra ----
git push origin main

echo.
echo Kesz! A weboldal frissult a GitHub Pages-en.
pause
