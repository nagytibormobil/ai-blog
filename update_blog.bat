@echo off
cd /d C:\ai_blog

echo ===============================
echo 🔹 Virtuális környezet aktiválása...
echo ===============================
call ai-env\Scripts\activate.bat

echo ===============================
echo 🔹 Új posztok generálása (1 db)...
echo ===============================
python generate_and_save.py --num_posts 1

echo ===============================
echo 🔹 Affiliate blokkok hozzáadása posztokhoz...
echo ===============================
python append_affiliate.py

echo ===============================
echo 🔹 GitHub feltöltés indul...
echo ===============================
git add .
git commit -m "Automatikus frissítés új HTML posztokkal és affiliate blokkokkal"
git push origin main

echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================
pause
