@echo off
chcp 65001 >nul

echo ===============================
echo 🔹 Virtuális környezet aktiválása...
echo ===============================
cd /d C:\ai_blog
call venv\Scripts\activate

echo ===============================
echo 🔹 Könyvtár és csomagok ellenőrzése...
echo ===============================
REM Ha nincs openai, telepíti
pip show openai >nul 2>&1
IF ERRORLEVEL 1 (
    echo OpenAI nincs telepítve, telepítés indul...
    pip install openai
)

echo ===============================
echo 🔹 Új posztok generálása...
echo ===============================
python generate_and_save.py

IF ERRORLEVEL 1 (
    echo ❌ Hiba a Python futtatás közben!
    pause
    exit /b 1
)

echo ===============================
echo 🔹 Git commit és push automatikusan...
echo ===============================
git add .
git commit -m "Automatikus frissítés: új posztok"
git push origin main

echo ===============================
echo ✅ Kész! Minden sikeresen lefutott.
echo ===============================
pause
