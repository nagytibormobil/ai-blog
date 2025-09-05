@echo off
chcp 65001
cd /d C:\ai_blog

REM ===============================
REM Virtuális környezet aktiválása
REM ===============================
echo ===============================
echo 🔹 Virtuális környezet aktiválása...
echo ===============================
call ai-env\Scripts\activate.bat

REM ===============================
REM Flask és szükséges modulok telepítése
REM ===============================
echo ===============================
echo 🔹 Flask és szükséges modulok telepítése...
echo ===============================
pip install --upgrade pip
pip install flask flask-cors requests

REM ===============================
REM Új posztok generálása
REM ===============================
set TOTAL=12
echo ===============================
echo 🔹 Új posztok generálása %TOTAL% db (lépcsőzetesen)...
echo ===============================

REM Blokkonként generálás (4-esével)
setlocal enabledelayedexpansion
for /L %%i in (1,4,%TOTAL%) do (
    set /a remaining=%TOTAL%-%%i+1
    if !remaining! GTR 3 (
        set /a to_generate=4
    ) else (
        set /a to_generate=!remaining!
    )
    echo 🔹 Generálás %%i - %%i+!to_generate!-1 (összesen !to_generate! poszt)
    python generate_and_save.py --num_posts !to_generate!
)
endlocal

REM ===============================
REM Git add/commit/push (csak ha van változás)
REM ===============================
echo ===============================
echo 🔹 Git add/commit/push (új képek és posztok)...
echo ===============================
git add .
REM Ellenőrizzük, van-e változás
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "Automatikus frissítés új HTML posztokkal és képekkel"
    git push origin main
) else (
    echo 🔹 Nincs új változás, nem commitolunk
)

REM ===============================
REM Flask komment-szerver indítása
REM ===============================
echo ===============================
echo 🔹 Flask komment-szerver indítása (handle_comment.py)...
echo ===============================
start cmd /k python handle_comment.py

REM ===============================
REM Lokális HTTP szerver indítása
REM ===============================
echo ===============================
echo 🔹 Lokális HTTP szerver indítása (http://127.0.0.1:8000)...
echo ===============================
start cmd /k python -m http.server 8000

echo ===============================
echo ✅ Blog frissítve, komment-szerver és HTTP szerver elindítva!
echo ===============================
