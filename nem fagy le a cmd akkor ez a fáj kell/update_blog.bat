@echo off
REM ===============================
REM Update AI Gaming Blog - Batch
REM ===============================

REM Aktiválja a virtuális környezetet
call ai-env\Scripts\activate.bat

echo ===============================
echo › Virtuális környezet aktiválása...
echo ===============================

REM Generál új posztokat
echo ===============================
echo › Új posztok generálása (12 db)...
echo ===============================

python generate_and_save.py --num_posts 12

REM Affiliate blokk hozzáadása a posztokhoz
echo ===============================
echo › Affiliate blokk hozzáadása a posztokhoz...
echo ===============================
python append_affiliate.py

REM Git commit/push
echo ===============================
echo › Git add/commit/push...
echo ===============================
git add .
git commit -m "Automatikus frissítés új HTML posztokkal"
git push origin main

echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================
