@echo off
setlocal enabledelayedexpansion

REM Projekt könyvtár
set BASEDIR=C:\Users\User\OneDrive\ai_blog
set POSTDIR=%BASEDIR%\generated_posts
set INDEXFILE=%BASEDIR%\index.html
set TEMPFILE=%BASEDIR%\index_temp.html

echo Ellenorzes indul...

REM Új index fájl készítése
del "%TEMPFILE%" >nul 2>&1
type nul > "%TEMPFILE%"

for /f "usebackq delims=" %%A in ("%INDEXFILE%") do (
    set "LINE=%%A"
    echo !LINE! | findstr /i "generated_posts/.*\.html" >nul
    if !errorlevel! == 0 (
        REM Linket tartalmaz
        for /f "tokens=2 delims== " %%B in ('echo !LINE! ^| findstr /o "generated_posts/"') do (
            REM Keressük a fájl nevét a sorban
        )
        for /f "tokens=2 delims==\"" %%C in ("!LINE!") do (
            set LINK=%%C
            set FILENAME=!LINK:*=generated_posts\!
            if exist "%POSTDIR%\!FILENAME!" (
                REM létezik a fájl -> sor megmarad
                echo !LINE!>>"%TEMPFILE%"
            ) else (
                REM Nincs fájl -> kihagyjuk (404 hibás link törlés)
                echo [TOROLVE] !FILENAME!
            )
        )
    ) else (
        REM Nem tartalmaz linket -> simán bemásoljuk
        echo !LINE!>>"%TEMPFILE%"
    )
)

REM Eredeti index lecserélése
move /Y "%TEMPFILE%" "%INDEXFILE%" >nul

echo Kesz! Az index.html-bol torolve lettek a 404-es linkek.
pause
