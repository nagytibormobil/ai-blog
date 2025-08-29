<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{GAME_TITLE}} – AI Gaming Blog</title>
<meta name="description" content="{{GAME_TITLE}} review, cheats, tips, gameplay insights.">
<meta name="robots" content="index,follow">
<style>
  :root{--bg:#0b0f14;--card:#121821;--text:#eaf1f8;--muted:#9fb0c3;--accent:#5cc8ff;--border:#1f2a38;}
  body{margin:0;padding:0;background:var(--bg);color:var(--text);font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif;}
  a{color:var(--accent);text-decoration:none;}
  a:hover{text-decoration:underline;}
  header, .content, .footer{max-width:900px;margin:0 auto;padding:16px;}
  header a.btn{display:inline-block;padding:6px 12px;background:var(--card);border-radius:8px;border:1px solid var(--border);}
  .thumb img{width:100%;height:auto;border-radius:10px;}
  .section{margin-top:24px;}
  .badge{background:rgba(92,200,255,.12);padding:2px 6px;border-radius:6px;}
  .tiny{font-size:12px;color:var(--muted);}
</style>
</head>
<body>
<header>
  <a class="btn" href="../index.html">🏠 Home</a>
  <h1>{{GAME_TITLE}}</h1>
  <p class="tiny">Platforms: {{PLATFORMS}} | Release: {{DATE}} | AI Rating: ⭐ {{RATING}} / 5</p>
</header>

<section class="thumb">
  <img src="../Picture/{{IMAGE_FILE}}" alt="{{GAME_TITLE}}">
</section>

<section class="section" id="about">
  <h2>About the Game</h2>
  <p>{{ABOUT_TEXT}}</p>
</section>

<section class="section" id="review">
  <h2>AI Review</h2>
  <p>{{REVIEW_TEXT}}</p>
</section>

<section class="section" id="cheats">
  <h2>Cheats & Tips</h2>
  <ul>
    {% for tip in TIPS %}
      <li>{{tip}}</li>
    {% endfor %}
  </ul>
  {% if TIPS|length >= 15 %}
    <p>To enter cheats in-game, press the designated keys listed in each tip above.</p>
  {% endif %}
</section>

<section class="section" id="affiliate">
  <h2>Affiliate</h2>
  <div>
    <p>Earn passive income while gaming:</p>
    <a href="https://r.honeygain.me/NAGYT86DD6" target="_blank"><strong>Try Honeygain now</strong></a>
    <p class="tiny">Sponsored. Use at your own discretion.</p>
  </div>
</section>

<section class="section" id="comments">
  <h2>User Comments</h2>
  <p>Leave your thoughts below. Max 10 comments/day. All comments are moderated.</p>
  <div id="commentList"></div>
  <textarea id="commentInput" placeholder="Write a comment..."></textarea>
  <button onclick="submitComment()">Submit</button>
</section>

<section class="footer">
  <p class="tiny">© <span id="year"></span> AI Gaming Blog</p>
</section>

<script>
  document.getElementById('year').textContent = new Date().getFullYear();

  const bannedWords = ["sex","fuck","porn","drugs","war","terror"];
  let comments = [];

  function submitComment() {
    const input = document.getElementById('commentInput');
    const text = input.value.trim();
    if(!text) return alert("Empty comment!");
    if(text.length > 500) return alert("Comment too long!");
    if(comments.length >= 10) return alert("Max 10 comments/day reached!");
    for(let word of bannedWords) if(text.toLowerCase().includes(word)) return alert("Forbidden word detected!");
    if(/<img|<a/i.test(text)) return alert("Images and links are not allowed in comments!");
    comments.push(text);
    const list = document.getElementById('commentList');
    const div = document.createElement('div');
    div.textContent = text;
    list.appendChild(div);
    input.value = "";
  }
</script>
</body>
</html>
