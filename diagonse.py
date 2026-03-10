#!/usr/bin/env python3
"""
Run from your project root:
  python3 diagnose_lexicon.py

This checks exactly why Greek lemmas don't match Dodson entries.
"""
import os, re, csv, unicodedata

DODSON_CSV = "lexicon/Dodson-Greek-Lexicon/dodson.csv"

BETACODE_TABLE = {
    'a':'α','b':'β','g':'γ','d':'δ','e':'ε','z':'ζ','h':'η','q':'θ',
    'i':'ι','k':'κ','l':'λ','m':'μ','n':'ν','c':'ξ','o':'ο','p':'π',
    'r':'ρ','s':'σ','t':'τ','u':'υ','f':'φ','x':'χ','y':'ψ','w':'ω',
}

def betacode_to_unicode(b):
    b = re.sub(r'[^a-zA-Z]', '', b)
    return ''.join(BETACODE_TABLE.get(c.lower(), '') for c in b)

def normalise(lemma):
    decomposed = unicodedata.normalize('NFD', lemma)
    stripped = ''.join(c for c in decomposed if unicodedata.category(c) != 'Mn').lower()
    return stripped.replace('ς', 'σ')

# ── 1. Show raw CSV structure ──
print("=" * 60)
print("RAW CSV INSPECTION")
print("=" * 60)
if not os.path.exists(DODSON_CSV):
    print(f"ERROR: {DODSON_CSV} not found! (cwd={os.getcwd()})")
    exit(1)

with open(DODSON_CSV, encoding="utf-8") as f:
    lines = [f.readline() for _ in range(5)]

print("First 5 raw lines:")
for i, l in enumerate(lines):
    print(f"  [{i}] {repr(l[:100])}")

# Detect delimiter
has_tab   = any('\t' in l for l in lines)
has_comma = any(',' in l for l in lines[1:])
delim = '\t' if has_tab else ','
print(f"\nDetected delimiter: {repr(delim)}")

# ── 2. Load and show first few parsed rows ──
print("\nFirst 5 parsed rows:")
with open(DODSON_CSV, encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=delim)
    all_rows = list(reader)

for i, row in enumerate(all_rows[:5]):
    print(f"  [{i}] {row}")

print(f"\nTotal rows: {len(all_rows)}")
print(f"Columns per row (row 1): {len(all_rows[1]) if len(all_rows)>1 else '?'}")

# ── 3. Determine if row[0] is a header ──
row0 = all_rows[0]
looks_like_header = not row0[0].strip().lstrip('"').isdigit()
print(f"\nRow 0 looks like header: {looks_like_header}  ({row0[0]!r})")
start = 1 if looks_like_header else 0

# ── 4. Find which columns hold betacode and gloss ──
# Scan for a known word to identify columns
known = {"qeos": "θεός", "kurios": "κύριος", "apostolos": "ἀπόστολος",
         "elpis": "ἐλπίς", "soter": "σωτήρ"}

print("\n── Column scan for known betacode words ──")
for test_bc, test_greek in known.items():
    for row in all_rows[start:start+200]:
        for ci, cell in enumerate(row):
            clean = re.sub(r'[^a-zA-Z]', '', cell.strip().strip('"')).lower()
            if clean == test_bc:
                print(f"  '{test_bc}' ({test_greek}) found in col {ci}: row={[c[:30] for c in row]}")
                break

# ── 5. Build lexicon with detected settings and spot-check ──
print("\n── Building lexicon and spot-checking NT words ──")

lexicon = {}
for row in all_rows[start:]:
    if len(row) < 4:
        continue
    try:
        strongs  = row[0].strip().strip('"')
        betacode = row[2].strip().strip('"')
        gloss    = row[3].strip().strip('"')
        key = normalise(betacode_to_unicode(betacode))
        if key:
            lexicon[key] = {"gloss": gloss, "strongs": strongs}
    except Exception as e:
        print(f"  Row error: {e} — {row}")

print(f"Lexicon size: {len(lexicon)}")

test_words = [
    "θεός","κύριος","ἀπόστολος","Χριστός","Ἰησοῦς",
    "ἐλπίς","σωτήρ","ἐπιταγή","ὁ","πατήρ","ἁγίος",
    "πιστός","καί","ἐν","ἐγώ",
]
print("\nLookup results for common NT lemmas:")
print(f"  {'Lemma':<20} {'Normalised key':<20} {'Result'}")
print(f"  {'-'*20} {'-'*20} {'-'*30}")
for w in test_words:
    k = normalise(w)
    hit = lexicon.get(k)
    result = hit['gloss'] if hit else "✗ NOT FOUND"
    print(f"  {w:<20} {k:<20} {result}")

# ── 6. Show a few actual keys around "θεοσ" ──
target = normalise("θεός")
print(f"\nKeys near '{target}' in lexicon:")
near = [k for k in lexicon if abs(len(k)-len(target)) <= 1 and k[0] == target[0]]
for k in sorted(near)[:10]:
    print(f"  {repr(k)} → {lexicon[k]['gloss']}")
