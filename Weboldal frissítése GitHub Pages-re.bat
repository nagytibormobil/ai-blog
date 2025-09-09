@echo off
REM ===============================
REM Weboldal frissítése GitHub Pages-re (index, postok, képek)
REM ===============================

cd /d C:\ai_blog

REM Másold át a friss tartalmakat a gyökérbe
echo 🔄 Friss fájlok másolása a repo gyökerébe...
xcopy /E /Y /I generated_posts generated_posts
xcopy /E /Y /I Picture Picture
copy /Y index.html index.html

REM Git státusz kiíratása
git status

REM Add hozzá az összes változást
git add -A

REM Commit üzenet dátummal és idővel
git commit -m "Auto update: %date% %time%"

REM Push a main branch-re
git push origin main

echo.
echo ✅ Weboldal frissítve a GitHub Pages-en!
echo 🔁 Ne felejtsd: frissítsd a böngészőt CTRL+F5-tel.
