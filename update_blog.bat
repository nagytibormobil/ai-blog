@echo off
cd /d C:\ai_blog

REM enable delayed expansion for variable math in loops
setlocal enabledelayedexpansion

echo ===============================
echo 🔹 Virtuális környezet aktiválása...
echo ===============================
call ai-env\Scripts\activate.bat

echo ===============================
echo 🔹 Új posztok generálása 1 db 
echo ===============================

set TOTAL=1

echo ===============================
echo 🔹 Git add/commit/push (új képek és posztok)...
echo ===============================
git add .
git commit -m "Automatikus frissítés új HTML posztokkal és képekkel"
git push origin main

echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================
endlocal
