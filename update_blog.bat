@echo off
REM ===============================
REM Weboldal frissítése GitHub Pages-re
REM ===============================

cd /d C:\ai_blog

echo 🔄 Git státusz ellenőrzése...
git status

REM Add hozzá az összes változást (index.html, generated_posts, Picture stb.)
git add -A

REM Commit üzenet dátummal és idővel
git commit -m "Auto update: %date% %time%"

REM Push a main branch-re
git push origin main

echo.
echo ✅ Weboldal frissítve a GitHub Pages-en!
echo 🔁 Ne felejtsd: frissítsd a böngészőt CTRL+F5-tel.

pause
