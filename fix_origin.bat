@echo off
cd /d C:\ai_blog
echo ---- Jelenlegi remote beállítások ----
git remote -v

echo.
echo ---- Origin törlése (ha létezik) ----
git remote remove origin

echo.
echo ---- Új origin hozzáadása ----
git remote add origin https://github.com/nagytibormobil/ai-blog.git

echo.
echo ---- Ellenőrzés ----
git remote -v

echo.
echo Kész! Mostantól a helyes repo-ra mutat: nagytibormobil/ai-blog
pause
