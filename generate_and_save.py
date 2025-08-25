#!/usr/bin/env python3
# generate_and_save.py
import os
import argparse
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

OUTDIR_DEFAULT = "generated_posts"
INDEX_FILE = "index.html"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def load_model(model_name="gpt2"):
    print("Modell és tokenizer betöltése:", model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({'pad_token': tokenizer.eos_token})
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.resize_token_embeddings(len(tokenizer))
    device = torch.device("cpu")
    model.to(device)
    model.eval()
    return tokenizer, model, device

def generate_text(tokenizer, model, device, prompt, max_new_tokens=150, temperature=0.8, top_p=0.92):
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model.generate(
            **inputs,
            do_sample=True,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.1,
            num_return_sequences=1
        )
    text = tokenizer.decode(out[0], skip_special_tokens=True)
    if text.startswith(prompt):
        text = text[len(prompt):].strip()
    return text.strip()

def make_title(text, fallback="AI poszt"):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if lines:
        title = lines[0][:80]
    else:
        title = fallback
    return title

def safe_filename(s):
    keep = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(c if c in keep else "_" for c in s).strip().replace(" ", "_")

def save_markdown(outdir, title, body):
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    fn = f"{ts}-{safe_filename(title)[:100]}.md"
    path = os.path.join(outdir, fn)

    affiliate_block = """
---

💸 **Támogasd a blogot az ajánlott partnereken keresztül**

- 📈 [ICMarkets](https://icmarkets.com/?camp=3992)  
- 🏦 [Dukascopy](https://www.dukascopy.com/api/es/12831/type-S/target-id-149) (Promóciós kód: E12831)  
- 🐝 [Honeygain – passzív jövedelem internetmegosztással](https://r.honeygain.me/NAGYT86DD6)  
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{body}\n\n{affiliate_block}")
    return path, fn, title

def update_index(outdir, index_file):
    files = sorted(os.listdir(outdir), reverse=True)
    links = []
    for fn in files:
        if fn.endswith(".md"):
            title = fn.split("-", 1)[-1].rsplit(".", 1)[0].replace("_", " ")
            links.append(f'- <a href="{outdir}/{fn}">{title}</a>')
    html_content = f"""<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <title>AI Blog</title>
</head>
<body>
    <h1>Üdv a blogomon 👋</h1>
    <p>Ez egy AI által generált blog.</p>
    <h2>Legújabb posztok</h2>
    <ul>
        {' '.join(f'<li>{l}</li>' for l in links)}
    </ul>
</body>
</html>"""
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Index frissítve:", index_file)

def load_prompts_from_file(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    return lines

def main():
    parser = argparse.ArgumentParser(description="Egyszerű AI poszt generáló (GPT-2).")
    parser.add_argument("--model", type=str, default="gpt2", help="Hugging Face modell neve (alap: gpt2)")
    parser.add_argument("--num_posts", type=int, default=3, help="Hány posztot generáljon")
    parser.add_argument("--prompt", type=str, default="", help="Ha megadsz egy promptot, azt használja")
    parser.add_argument("--prompt_file", type=str, default="", help="Promptok fájl (egy sor = egy prompt)")
    parser.add_argument("--outdir", type=str, default=OUTDIR_DEFAULT, help="Kimeneti mappa")
    parser.add_argument("--max_new_tokens", type=int, default=160, help="Maximálisan generált token (szöveg hossza)")
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top_p", type=float, default=0.92)
    args = parser.parse_args()

    ensure_dir(args.outdir)
    tokenizer, model, device = load_model(args.model)

    prompts = []
    if args.prompt_file:
        prompts = load_prompts_from_file(args.prompt_file)
    if args.prompt:
        prompts.insert(0, args.prompt)
    if not prompts:
        prompts = [
            "Írj egy hasznos, könnyen olvasható blogposztot a következő témában: házi praktikák a mindennapi életben.",
            "Írj egy rövid, SEO-barát cikket arról, hogyan válassz futócipőt kezdőknek.",
            "Írj egy 6-8 mondatos Facebook-posztot, ami promózza egy kisvállalkozás kézműves termékeit."
        ]

    created = []
    for i in range(args.num_posts):
        prompt = prompts[i % len(prompts)]
        print(f"\nGenerálás {i+1}/{args.num_posts} — prompt: {prompt[:60]}...")
        body = generate_text(tokenizer, model, device, prompt,
                             max_new_tokens=args.max_new_tokens,
                             temperature=args.temperature,
                             top_p=args.top_p)
        title = make_title(body)
        path, fn, title = save_markdown(args.outdir, title, body)
        created.append(path)
        print("Létrehozva:", path)

    update_index(args.outdir, INDEX_FILE)

    print("\nKész. Összes létrehozott fájl:")
    for p in created:
        print(" -", p)

if __name__ == "__main__":
    main()
