#!/usr/bin/env python3
# build_josephus_json.py
# Converts wars6_greek.txt + wars6_english.txt + wars6_whiston.txt
# → docs/data/wars6.json and updates docs/data/index.json
#
# Run from your NT project root:
#   python3 build_josephus_json.py
#
# Copy files first:
#   cp ~/text-helper/wars6_greek.txt sources/
#   cp ~/text-helper/wars6_english.txt sources/
#   cp sources/wars6_whiston.txt sources/   (already there)

import json, os, re

GREEK_FILE   = "sources/wars6_greek.txt"
ENGLISH_FILE = "sources/wars6_english.txt"
WHISTON_FILE = "sources/wars6_whiston.txt"
OUT_JSON     = "docs/data/wars6.json"
INDEX_JSON   = "docs/data/index.json"

# ── Load Greek sentences ──
with open(GREEK_FILE, encoding="utf-8") as f:
    greek_lines = [l.strip() for l in f if l.strip()]

# ── Load English (tab-separated: N\ttranslation) ──
english = {}
with open(ENGLISH_FILE, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t', 1)
        if len(parts) == 2:
            try:
                english[int(parts[0])] = parts[1]
            except ValueError:
                pass

# ── Load Whiston (plain prose, strip section headers in ALL CAPS) ──
whiston_text = ""
if os.path.exists(WHISTON_FILE):
    with open(WHISTON_FILE, encoding="utf-8") as f:
        raw = f.read()
    # Remove all-caps section headings
    raw = re.sub(r'\n[A-Z][A-Z ,\.\'\-]{20,}\n', '\n', raw)
    # Collapse whitespace
    whiston_text = re.sub(r'\s+', ' ', raw).strip()
    print(f"Whiston text:         {len(whiston_text)} chars")
else:
    print(f"WARNING: {WHISTON_FILE} not found — Whiston tab will be empty")

print(f"Greek sentences:      {len(greek_lines)}")
print(f"English translations: {len(english)}")

# ── Build verses ──
verses = []
for i, greek in enumerate(greek_lines, 1):
    verses.append({
        "ref":     f"Wars VI.{i}",
        "n":       i,
        "greek":   greek,
        "mistral": english.get(i, ""),
        "kjv":     ""
    })

# ── Book JSON ──
book = {
    "code":           "wars6",
    "name":           "Jewish War VI",
    "author":         "Flavius Josephus",
    "type":           "prose",
    "group":          "josephus",
    "verseCount":     len(verses),
    "hasTranslation": True,
    "hasKjv":         False,
    "hasWhiston":     bool(whiston_text),
    "whiston_text":   whiston_text,
    "attribution": {
        "greek":       "Flavius Josephus, De Bello Judaico (Jewish War). Greek text from open corpus.",
        "translation": "Translated by Mistral 7B (mistral:7b via Ollama). Machine translation, unreviewed.",
        "whiston":     "W. Whiston (1737). Public domain. Reproduced for comparison only."
    },
    "verses": verses
}

os.makedirs("docs/data", exist_ok=True)
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(book, f, ensure_ascii=False, indent=2)
print(f"Written:  {OUT_JSON}")

# ── Update index.json ──
if os.path.exists(INDEX_JSON):
    with open(INDEX_JSON, encoding="utf-8") as f:
        index = json.load(f)
    if isinstance(index, dict):
        books = index.get("books", [])
    else:
        books = index
else:
    books = []

books = [b for b in books if b.get("code") != "wars6"]
books.append({
    "code":           "wars6",
    "name":           "Jewish War VI",
    "author":         "Flavius Josephus",
    "type":           "prose",
    "group":          "josephus",
    "verseCount":     len(verses),
    "hasTranslation": True,
    "hasKjv":         False,
    "hasWhiston":     bool(whiston_text)
})

with open(INDEX_JSON, "w", encoding="utf-8") as f:
    json.dump(books, f, ensure_ascii=False, indent=2)
print(f"Updated:  {INDEX_JSON}")
print(f"\nDone — {len(verses)} sentences ready.")
