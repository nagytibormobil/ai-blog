@echo off
REM ===============================
REM Weboldal frissítése GitHub Pages-re (index, postok, képek)
REM ===============================

cd /d C:\ai_blog

REM Git státusz kiíratása
git status

REM Add hozzá MINDEN fájlt (nem csak a három mappát)
git add -A

REM Commit üzenet dátummal
git commit -m "Auto update: %date% %time%"

REM Push a megfelelő branchre (ellenőrizd: main vagy gh-pages?)
git push origin main

echo.
echo ✅ Weboldal frissítve a GitHub Pages-en!
