@echo off
rem update_and_check.bat
rem Usage: save this file into C:\ai_blog and run it there (or run anywhere, it CD-s into C:\ai_blog)
rem What it does:
rem  - git pull
rem  - git add . && git commit (if changes)
rem  - git push origin main
rem  - create an empty commit to force GitHub Pages rebuild (optional, enabled below)
rem  - download remote index.html and compare SHA256 with local index.html using certutil
rem  - print results

setlocal EnableDelayedExpansion

rem ====== CONFIG ======
set REPO_DIR=C:\ai_blog
set REMOTE_URL=https://nagytibormobil.github.io/ai-blog/index.html
set BRANCH=main
set FORCE_REBUILD=1    rem set to 1 to create an empty commit to force Pages rebuild, 0 to skip
rem ====================

rem timestamp for commit messages
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TIMESTAMP=%%i

echo.
echo ===== Starting update_and_check at %TIMESTAMP% =====
echo Repo dir: %REPO_DIR%
echo Remote page: %REMOTE_URL%
echo Branch: %BRANCH%
echo.

rem check tools
where git >nul 2>&1
if errorlevel 1 (
  echo ERROR: git not found in PATH. Install Git for Windows and ensure git is in PATH.
  pause
  exit /b 2
)
where curl >nul 2>&1
if errorlevel 1 (
  echo WARNING: curl not found in PATH. The script will try to continue but cannot fetch the remote page.
)
where certutil >nul 2>&1
if errorlevel 1 (
  echo WARNING: certutil not found in PATH. SHA compare will not work.
)

rem go to repo dir
if not exist "%REPO_DIR%" (
  echo ERROR: Repo folder "%REPO_DIR%" does not exist.
  pause
  exit /b 3
)
pushd "%REPO_DIR%"

echo --- Git pull ---
git pull origin %BRANCH%
if errorlevel 1 (
  echo WARNING: git pull returned an error. Continuing...
)

echo --- Staging changes ---
git add -A
rem try to commit if there are changes
rem Use a message with timestamp
git commit -m "Auto-update: %TIMESTAMP%" >nul 2>&1
if errorlevel 1 (
  echo No local changes to commit.
) else (
  echo Committed local changes.
)

echo --- Pushing to remote ---
git push origin %BRANCH%
if errorlevel 1 (
  echo WARNING: git push failed. Check your credentials and network.
) else (
  echo Push succeeded.
)

if "%FORCE_REBUILD%"=="1" (
  echo --- Creating empty commit to force GitHub Pages rebuild ---
  git commit --allow-empty -m "Force rebuild Pages: %TIMESTAMP%" >nul 2>&1
  if errorlevel 1 (
    echo Failed to create empty commit (maybe git error). Continuing...
  ) else (
    git push origin %BRANCH%
    if errorlevel 1 (
      echo WARNING: push of empty commit failed.
    ) else (
      echo Empty commit pushed to trigger Pages rebuild.
    )
  )
) else (
  echo (Skipping empty commit — FORCE_REBUILD is 0)
)

rem Wait a short moment to allow GitHub to start rebuild (optional)
echo.
echo Waiting 5 seconds for GitHub Pages to begin rebuild...
ping -n 6 127.0.0.1 >nul

rem Fetch remote page
set TEMP_REMOTE_FILE=%TEMP%\remote_index_%TIMESTAMP%.html
if exist "%TEMP_REMOTE_FILE%" del /f /q "%TEMP_REMOTE_FILE%" >nul 2>&1

where curl >nul 2>&1
if errorlevel 0 (
  echo --- Downloading remote index.html via curl ---
  curl -s -L "%REMOTE_URL%" -o "%TEMP_REMOTE_FILE%"
  if errorlevel 1 (
    echo WARNING: curl failed to download remote page.
  ) else (
    echo Remote page saved to %TEMP_REMOTE_FILE%.
  )
) else (
  echo SKIPPING remote download: curl not available.
)

rem Compare hashes if both files exist
set LOCAL_INDEX=%REPO_DIR%\index.html
if exist "%LOCAL_INDEX%" (
  if exist "%TEMP_REMOTE_FILE%" (
    where certutil >nul 2>&1
    if errorlevel 0 (
      echo --- Computing SHA256 hashes ---
      certutil -hashfile "%LOCAL_INDEX%" SHA256 > "%TEMP%\local_hash_%TIMESTAMP%.txt"
      certutil -hashfile "%TEMP_REMOTE_FILE%" SHA256 > "%TEMP%\remote_hash_%TIMESTAMP%.txt"
      for /f "tokens=
