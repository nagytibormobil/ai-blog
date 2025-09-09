import os

# ===================
# AFFILIATE BLOKK (minden poszt végére)
# ===================
AFFILIATE_BLOCK = """
<hr>
<section class="ad">
  <h3>Earn Real Money While You Play 📱</h3>
  <p>Simple passive income by sharing a bit of your internet. Runs in the background while you game.</p>
  <p><a href="https://r.honeygain.me/NAGYT86DD6" target="_blank"><strong>Try Honeygain now</strong></a></p>
  <div class="tiny">Sponsored. Use at your own discretion.</div>
</section>
<div class="row" style="margin-top:12px">
  <div class="ad" style="border-style:solid;border-color:#1f2a38">
    <h3>IC Markets – Trade like a pro 🌍</h3>
    <p><a href="https://icmarkets.com/?camp=3992" target="_blank">Open an account</a></p>
  </div>
  <div class="ad" style="border-style:solid;border-color:#1f2a38">
    <h3>Dukascopy – Promo code: <code>E12831</code> 🏦</h3>
    <p><a href="https://www.dukascopy.com/api/es/12831/type-S/target-id-149" target="_blank">Start here</a></p>
  </div>
</div>
"""

# ===================
# BEÁLLÍTÁSOK
# ===================
POSTS_DIR = "generated_posts"

def main():
    # Ellenőrizzük a könyvtárat
    if not os.path.exists(POSTS_DIR):
        print(f"❌ Nem találom a {POSTS_DIR} könyvtárat!")
        return

    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith(".html"):
            continue
        path = os.path.join(POSTS_DIR, filename)

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Ha már benne van a blokk → hagyjuk
        if "Earn Real Money While You Play" in content:
            print(f"✅ {filename} már tartalmazza az affiliate blokkot.")
            continue

        # Blokk beillesztése </body> elé
        if "</body>" in content:
            new_content = content.replace("</body>", AFFILIATE_BLOCK + "\n</body>")
        else:
            new_content = content + "\n" + AFFILIATE_BLOCK

        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"➕ Affiliate blokk hozzáadva: {filename}")

if __name__ == "__main__":
    main()
