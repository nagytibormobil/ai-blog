@echo off
cd /d C:\ai_blog

call ai-env\Scripts\activate.bat

python generate_and_save.py --num_posts 5

git add .
git commit -m "Automatikus frissítés új HTML posztokkal" || echo "⚠️ Nincs új változás a commit-hoz"
git push origin main

echo ===============================
echo ✅ Blog frissítve és feltöltve!
echo ===============================

:: Automatikusan megnyitja a böngészőben a blog főoldalt
start https://nagytibormobil.github.io/ai-blog/
