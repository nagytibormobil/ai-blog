@echo off
cd /d C:\ai_blog
call ai-env\Scripts\activate.bat

echo ===============================
echo 🔹 Generating posts...
echo ===============================
python generate_and_save.py

echo ===============================
echo 🔹 Git add/commit/push...
echo ===============================
git add .
git commit -m "Automatic update: new posts and images"
git push origin main

echo ===============================
echo ✅ Blog updated and uploaded!
pause
