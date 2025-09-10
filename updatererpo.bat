@echo off
cd /d C:\ai_blog

:: Ha van rebase folyamatban, abortáljuk
git rebase --abort 2>nul

:: Biztosítjuk, hogy a main ágon vagyunk
git switch main

:: Hozzáadjuk az összes változást
git add .

:: Commit-olás a mai dátummal és idővel
setlocal enabledelayedexpansion
for /f "tokens=1-4 delims=/: " %%a in ("%date% %time%") do (
    set TODAY=%%a-%%b-%%c
    set NOW=%%d
)
g
