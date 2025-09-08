@echo off
REM ===============================
REM Weboldal frissítése GitHub Pages-re (index, postok, képek)
REM ===============================

REM Lépj a projekt könyvtárba
cd /d C:\ai_blog

REM Ellenőrizd a git státuszt
git status

REM Add hozzá az index.html-t, a postokat és a képeket
git add index.html generated_posts/* Picture/*

REM Commit üzenet (tetszőleges)
git commit -m "Manual update: frissítés meglévő postokkal és képekkel"

REM Push a GitHub-ra
git push origin main

echo Weboldal frissítve a GitHub Pages-en!
pause
