#!/usr/bin/env python3
# build_lucian_fly_json.py
# Converts fly_greek.txt + fly_english.txt → docs/data/lucian-fly.json
# and updates docs/data/index.json
#
# Run from ~/NT:
#   python3 build_lucian_fly_json.py
#
# Copy files first:
#   cp ~/text-helper/fly_greek.txt sources/
#   cp ~/text-helper/fly_english.txt sources/

import json, os, re

GREEK_FILE   = "sources/fly_greek.txt"
ENGLISH_FILE = "sources/fly_english.txt"
OUT_JSON     = "docs/data/lucian-fly.json"
INDEX_JSON   = "docs/data/index.json"

with open(GREEK_FILE, encoding="utf-8") as f:
    greek_lines = [l.strip() for l in f if l.strip()]

english = {}
if os.path.exists(ENGLISH_FILE):
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

print(f"Greek sentences:      {len(greek_lines)}")
print(f"English translations: {len(english)}")

verses = []
for i, greek in enumerate(greek_lines, 1):
    verses.append({
        "ref":     f"Fly.{i}",
        "n":       i,
        "greek":   greek,
        "mistral": english.get(i, ""),
        "kjv":     ""
    })

book = {
    "code":           "lucian-fly",
    "name":           "In Praise of the Fly",
    "author":         "Lucian of Samosata",
    "type":           "prose",
    "group":          "apocrypha",
    "verseCount":     len(verses),
    "hasTranslation": any(v["mistral"] for v in verses),
    "hasKjv":         False,
    "hasWhiston":     False,
    "attribution": {
        "greek":       "Lucian of Samosata, Μυίας Ἐγκώμιον (c.160 CE). Greek text from open corpus.",
        "translation": "Translated by Mistral 7B (Mistral AI). Machine translation, unreviewed."
    },
    "verses": verses
}

os.makedirs("docs/data", exist_ok=True)
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(book, f, ensure_ascii=False, indent=2)
print(f"Written:  {OUT_JSON}")

if os.path.exists(INDEX_JSON):
    with open(INDEX_JSON, encoding="utf-8") as f:
        books = json.load(f)
    if isinstance(books, dict):
        books = books.get("books", [])
else:
    books = []

books = [b for b in books if b.get("code") != "lucian-fly"]
books.append({
    "code":           "lucian-fly",
    "name":           "In Praise of the Fly",
    "author":         "Lucian of Samosata",
    "type":           "prose",
    "group":          "apocrypha",
    "verseCount":     len(verses),
    "hasTranslation": any(v["mistral"] for v in verses),
    "hasKjv":         False,
    "hasWhiston":     False
})

with open(INDEX_JSON, "w", encoding="utf-8") as f:
    json.dump(books, f, ensure_ascii=False, indent=2)
print(f"Updated:  {INDEX_JSON}")
print(f"\nDone — {len(verses)} sentences ready.")
