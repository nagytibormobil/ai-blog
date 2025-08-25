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
    # ha nincs pad token, használjuk az eos-t
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({'pad_token': tokenizer.eos_token})
    model = AutoModelForCausalLM.from_pretrained(model_name)
    # ha hozzáadtunk token-t, méreteket frissítjük
    model.resize_token_embeddings(len(tokenizer))
    device = torch.device("cpu")
    model.to(device)
    model.eval()
    return tokenizer, model, device

def generate_text(tokenizer, model, device, prompt, max_new_tokens=150, temperature=0.8, top_p=0.92):
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    try:
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
    except TypeError:
        # régebbi transformers esetén fallback max_length-re
        max_length = inputs["input_ids"].shape[1] + max_new_tokens
        with torch.no_grad():
            out = model.generate(
                **inputs,
                do_sample=True,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1,
                num_return_sequences=1
            )
    text = tokenizer.decode(out[0], skip_special_tokens=True)
    # eltávolítjuk a prompt ismétlődő részét, ha benne marad
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
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{body}\n")
    return path

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
        # alapértelmezett prompt
        prompts = [
            "Írj egy hasznos, könnyen olvasható blogposztot a következő témában: házi praktikák a mindennapi életben. Kezdd egy figyelemfelkeltő bevezetéssel és adj 5 gyakorlati tippet.",
            "Írj egy rövid, SEO-barát cikket arról, hogyan válassz futócipőt kezdőknek. Tartsd egyszerűen és gyakorlati tanácsokat adj.",
            "Írj egy 6-8 mondatos Facebook-posztot, ami promózza egy kisvállalkozás kézműves termékeit, hangsúlyozva az egyedi jelleget."
        ]

    created = []
    for i in range(args.num_posts):
        prompt = prompts[i % len(prompts)]
        print(f"\nGenerálás {i+1}/{args.num_posts} — prompt: {prompt[:60]}...")
        body = generate_text(tokenizer, model, device, prompt, max_new_tokens=args.max_new_tokens, temperature=args.temperature, top_p=args.top_p)
        title = make_title(body)
        path = save_markdown(args.outdir, title, body)
        created.append(path)
        print("Létrehozva:", path)

    print("\nKész. Összes létrehozott fájl:")
    for p in created:
        print(" -", p)

if __name__ == "__main__":
    main()
