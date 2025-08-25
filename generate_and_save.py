#!/usr/bin/env python3
# generate_and_save.py
import os
import argparse
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

OUTDIR_DEFAULT = "generated_posts"

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

def save_html(outdir, title, body):
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    fn = f"{ts}-{safe_filename(title)[:100]}.html"
    path = os.path.join(outdir, fn)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="hu">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
</head>
<body>
  <h1>{title}</h1>
  <p>{body}</p>

  <hr>
  <h2>💰 Ajánlott lehetőségek</h2>
  <ul>
    <li><a href="https://icmarkets.com/?camp=3992" target="_blank">🌍 ICMarkets - kereskedj profi szinten</a></li>
    <li><a href="https://www.dukascopy.com/api/es/12831/type-S/target-id-149" target="_blank">🏦 Dukascopy - nyiss számlát promóciós kóddal: E12831</a></li>
    <li><a href="https://r.honeygain.me/NAGYT86DD6" target="_blank">📱 Honeygain - keress passzív jövedelmet az internet megosztásával</a></li>
  </ul>
</body>
</html>""")
    return path

def main():
    parser = argparse.ArgumentParser(description="AI poszt generáló (HTML verzió).")
    parser.add_argument("--model", type=str, default="gpt2")
    parser.add_argument("--num_posts", type=int, default=1)
    parser.add_argument("--outdir", type=str, default=OUTDIR_DEFAULT)
    args = parser.parse_args()

    ensure_dir(args.outdir)
    tokenizer, model, device = load_model(args.model)

    prompt = "Írj egy rövid blogposztot a mesterséges intelligenciáról."
    for i in range(args.num_posts):
        body = generate_text(tokenizer, model, device, prompt)
        title = make_title(body)
        path = save_html(args.outdir, title, body)
        print("Létrehozva:", path)

if __name__ == "__main__":
    main()
