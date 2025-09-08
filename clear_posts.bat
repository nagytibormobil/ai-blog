@echo off
REM Aktiválja a virtuális környezetet, ha szükséges
REM call ai-env\Scripts\activate.bat

REM 1. Törli az összes HTML fájlt a generated_posts mappából
del /Q "C:\ai_blog\generated_posts\*.html"
del /Q "C:\ai_blog\Picture\*.jpg"


REM 2. Teljesen eltávolítja a generated_posts mappát
rmdir /S /Q "C:\ai_blog\generated_posts"

REM 3. Újra létrehozza a generated_posts mappát az üres állapothoz
mkdir "C:\ai_blog\generated_posts"

REM 4. Git műveletek a repository frissítéséhez
git add -A
git commit -m "Teljesen törölve a generated_posts mappa tartalma"
git push origin main

echo.
echo ✅ Minden poszt törölve, a repository frissítve!

