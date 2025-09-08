@echo off
setlocal enabledelayedexpansion

REM --------------------------------------------------------
REM Konfiguráld a változókat
REM --------------------------------------------------------
set OLD_REPO=git@github.com:nagytibormobil/ai-blog.git
set NEW_REPO=git@github.com:nagytibormobil/ai-blog-new.git

REM Titkos fájlok amiket törölni kell
set FILES_TO_REMOVE="open ai kulcs másolata.txt" "open ai kulcs.txt" "type.env"

REM Temp mappa
set CLEAN_DIR=C:\ai_blog_clean
if exist %CLEAN_DIR% rd /s /q %CLEAN_DIR%
mkdir %CLEAN_DIR%
cd %CLEAN_DIR%

REM --------------------------------------------------------
REM Repo klónozása mirror módban
REM --------------------------------------------------------
echo Cloning repo as mirror...
git clone --mirror %OLD_REPO%
cd ai-blog.git

REM --------------------------------------------------------
REM Titkos fájlok eltávolítása
REM --------------------------------------------------------
echo Removing secret files from git history...
git filter-repo --invert-paths %FILES_TO_REMOVE% --force

REM --------------------------------------------------------
REM Remote beállítása az új repo-ra
REM --------------------------------------------------------
echo Setting new remote...
git remote set-url origin %NEW_REPO%

REM --------------------------------------------------------
REM Új munka könyvtár létrehozása a .gitignore-hoz
REM --------------------------------------------------------
cd ..
mkdir ai-blog-cleaned
cd ai-blog-cleaned
git init
git remote add origin %NEW_REPO%

REM Másoljuk a megtisztított repo fájljait ide
echo Copying cleaned files...
xcopy "%CLEAN_DIR%\ai-blog.git\*" "%CD%" /E /H /K

REM --------------------------------------------------------
REM .gitignore létrehozása
REM --------------------------------------------------------
echo Creating .gitignore...
echo *.env > .gitignore
echo *.txt >> .gitignore

REM --------------------------------------------------------
REM Commit és push
REM --------------------------------------------------------
git add .
git commit -m "Initial commit: Clean repo without secrets"
git push -u origin main --force

echo.
echo Repo successfully cleaned, .gitignore added, and pushed to %NEW_REPO%.
pause
