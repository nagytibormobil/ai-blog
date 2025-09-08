@echo off
REM =========================
REM Teljesen automatikus tisztítás és push
REM =========================

REM 0. Ellenőrzés: git telepítve van-e
git --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Git nincs telepitve vagy nincs PATH-ban!
    pause
    exit /b 1
)

REM 1. Ellenőrizzük, hogy ez egy git repo
git rev-parse --is-inside-work-tree >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Nem git repository mappaban vagy.
    pause
    exit /b 1
)

REM 2. Telepített-e git-filter-repo?
python -m pip show git-filter-repo >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo git-filter-repo nincs telepitve, telepites...
    python -m pip install git-filter-repo
)

REM 3. Ellenőrizzük az ágat, átnevezés main-re
FOR /F "tokens=1" %%i IN ('git branch --show-current') DO SET CURR_BRANCH=%%i
IF "%CURR_BRANCH%"=="master" (
    echo Atnevezes master -> main
    git branch -m master main
)

REM 4. Titkos fájlok törlése a történelemből
echo Toroljuk a titkos fajlokat a tortenelmbol...
git filter-repo --invert-paths --path "open ai kulcs másolata.txt" --path "open ai kulcs.txt" --path "type.env" --force

REM 5. Remote beállítása
git remote remove origin >nul 2>&1
git remote add origin https://github.com/nagytibormobil/ai-blog-new.git

REM 6. Commit ellenőrzés, ha nincs commit
git log --oneline >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Nincs commit, hozzaadjuk a jelenlegi fajlokat...
    git add .
    git commit -m "Initial cleaned commit"
)

REM 7. Push a main ágra force-olva
echo Feltoltes GitHub-ra...
git push -u origin main --force
git push origin --tags --force

echo.
echo ===============================
echo Repo tisztitas es push kesz!
echo ===============================
pause
