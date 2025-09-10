@echo off
echo ---- Valtozasok hozzaadasa ----
git add .

echo ---- Commit keszitese ----
git commit -m "Local changes commit"
if %errorlevel% neq 0 (
    echo Nincs uj commit, tovabb a feltolteshez...
)

echo ---- Frissites a GitHubrol ----
git pull origin main --rebase

echo ---- Feltoltes a GitHub-ra ----
git push origin main

echo ---- Kesz! A weboldal frissult a GitHub Pages-en ----
pause
