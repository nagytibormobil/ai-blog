@echo off
cd C:\ai_blog
call ai-env\Scripts\activate.bat
python generate_and_save.py --num_posts 30
