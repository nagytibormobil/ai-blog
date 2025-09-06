@echo off
REM =====================================
REM 🔹 AI Blog gyorsindító
REM =====================================

REM Navigálás a blog mappába
cd /d C:\ai_blog

REM Virtuális környezet aktiválása
call ai-env\Scripts\activate.bat

REM Blog frissítése
call update_blog.bat

REM Várakozás, hogy lássuk az eredményt

