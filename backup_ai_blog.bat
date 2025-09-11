@echo off
chcp 65001

set SOURCE=C:\ai_blog
set BACKUP_DIR=C:\ai_blog_backup

REM Windows-barát dátum és idő (YYYY-MM-DD_HH-MM-SS)
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do set DATE=%%c-%%a-%%b
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (
    set HOUR=%%a
    set MINUTE=%%b
)
REM Ha AM/PM van, eltávolítjuk
set HOUR=%HOUR: =%
set MINUTE=%MINUTE: =%
set TIMESTAMP=%DATE%_%HOUR%-%MINUTE%

set DEST=%BACKUP_DIR%\backup_%TIMESTAMP%

echo ===============================
echo 🔹 Biztonsági mentés készítése...
echo Eredeti: %SOURCE%
echo Mentés helye: %DEST%
echo ===============================

mkdir "%DEST%"

xcopy "%SOURCE%\*" "%DEST%\" /E /I /H /C /Y

echo ✅ Biztonsági mentés kész!
pause
