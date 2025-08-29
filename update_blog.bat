@echo off
cd /d C:\ai_blog

:: Activate Python virtual environment
call ai-env\Scripts\activate.bat

:: Generate new posts
python generate_and_save.py --num_posts 5

:: Git add, commit, push
git add .
git commit -m "Automatikus frissítés új HTML posztokkal"
git push origin main

echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================
