@echo off
cd /d C:\ai_blog

call ai-env\Scripts\activate.bat

python generate_and_save.py --num_posts 3

git add .
git commit -m "Automatikus frissítés új HTML posztokkal"
git push origin main

echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================
