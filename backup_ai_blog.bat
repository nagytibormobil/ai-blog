@echo off
chcp 65001

set SOURCE=C:\ai_blog
set BACKUP_DIR=C:\ai_blog_backup

REM Ellenőrzi, hogy létezik-e a backup könyvtár, ha nem, létrehozza
if not exist "%BACKUP_DIR%" (
    mkdir "%BACKUP_DIR%"
)

REM PowerShell segítségével dátum és idő generálása Windows-barát formátumban
for /f %%i in ('powershell -NoProfile -Command "(Get-Date).ToString(\'yyyy-MM-dd_HH-mm-ss\')"') do set TIMESTAMP=%%i

set DEST=%BACKUP_DIR%\backup_%TIMESTAMP%

echo ===============================
echo 🔹 Biztonsági mentés készítése...
echo Eredeti: %SOURCE%
echo Mentés helye: %DEST%
echo ===============================

REM Létrehozza a célmappát (hiányzó szülőmappákkal)
mkdir "%DEST%"

REM Másolja az összes fájlt és mappát
xcopy "%SOURCE%\*" "%DEST%\" /E /I /H /C /Y

echo ✅ Biztonsági mentés kész!
pause
