cd C:\ai_blog
python generate_and_save.py --num_posts 1
python update_index.py
git add .
git commit -m "Automatikus frissítés új posztokkal"
git push
