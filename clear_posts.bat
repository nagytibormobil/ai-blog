@echo off
chcp 65001
cd /d C:\ai_blog

echo ===============================
echo 🔹 Reset: Generált tartalom törlése...
echo ===============================

REM 1. Generált HTML posztok törlése
if exist "generated_posts" (
    rmdir /S /Q "generated_posts"
)
mkdir "generated_posts"

REM 2. Képek törlése
if exist "Picture" (
    rmdir /S /Q "Picture"
)
mkdir "Picture"

REM 3. Kommentek törlése
if exist "comments" (
    rmdir /S /Q "comments"
)
mkdir "comments"

echo ===============================
echo 🔹 Git frissítés a változásokkal...
echo ===============================
git add -A
git commit -m "Reset: Törölve a generated_posts, Picture és comments mappák"
git push origin main

echo ===============================
echo ✅ Minden generált tartalom törölve, repository frissítve!
echo ===============================
pause
