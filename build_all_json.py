#!/usr/bin/env python3
# build_all_json.py — convert all NT sources to JSON for the website
#
# Run from the project root (same folder as sources/, translations/, etc.):
#   python3 build_all_json.py
#
# Produces: docs/data/{book-code}.json + docs/data/index.json

import os, re, json, csv, unicodedata

SOURCES_DIR      = "sources"
TRANSLATIONS_DIR = "translations"
KJV_DIR          = "KJV-TXT-Files"
DODSON_CSV       = "lexicon/Dodson-Greek-Lexicon/dodson.csv"   # ← correct path
OUTPUT_DIR       = "docs/data"

BOOKS = [
    ("61-Mt",  "Matthew",          "Matthew.txt"),
    ("62-Mk",  "Mark",             "Mark.txt"),
    ("63-Lk",  "Luke",             "Luke.txt"),
    ("64-Jn",  "John",             "John.txt"),
    ("65-Ac",  "Acts",             "Acts.txt"),
    ("66-Ro",  "Romans",           "Romans.txt"),
    ("67-1Co", "1 Corinthians",    "1 Corinthians.txt"),
    ("68-2Co", "2 Corinthians",    "2 Corinthians.txt"),
    ("69-Ga",  "Galatians",        "Galatians.txt"),
    ("70-Eph", "Ephesians",        "Ephesians.txt"),
    ("71-Php", "Philippians",      "Philippians.txt"),
    ("72-Col", "Colossians",       "Colossians.txt"),
    ("73-1Th", "1 Thessalonians",  "1 Thessalonians.txt"),
    ("74-2Th", "2 Thessalonians",  "2 Thessalonians.txt"),
    ("75-1Ti", "1 Timothy",        "1 Timothy.txt"),
    ("76-2Ti", "2 Timothy",        "2 Timothy.txt"),
    ("77-Tit", "Titus",            "Titus.txt"),
    ("78-Phm", "Philemon",         "Philemon.txt"),
    ("79-Heb", "Hebrews",          "Hebrews.txt"),
    ("80-Jas", "James",            "James.txt"),
    ("81-1Pe", "1 Peter",          "1 Peter.txt"),
    ("82-2Pe", "2 Peter",          "2 Peter.txt"),
    ("83-1Jn", "1 John",           "1 John.txt"),
    ("84-2Jn", "2 John",           "2 John.txt"),
    ("85-3Jn", "3 John",           "3 John.txt"),
    ("86-Jud", "Jude",             "Jude.txt"),
    ("87-Re",  "Revelation",       "Revelation.txt"),
]

# ── Betacode → Unicode (for Dodson key matching) ──
BETACODE_TABLE = {
    'a':'α','b':'β','g':'γ','d':'δ','e':'ε','z':'ζ','h':'η','q':'θ',
    'i':'ι','k':'κ','l':'λ','m':'μ','n':'ν','c':'ξ','o':'ο','p':'π',
    'r':'ρ','s':'σ','t':'τ','u':'υ','f':'φ','x':'χ','y':'ψ','w':'ω',
}

def betacode_to_unicode(b):
    # Dodson col 2 looks like "qeo/s, ou(" — strip genitive/article suffix after comma
    b = b.split(',')[0]
    b = re.sub(r'[^a-zA-Z]', '', b)
    return ''.join(BETACODE_TABLE.get(c.lower(), '') for c in b)

def normalise_lemma(lemma):
    """Strip accents/diacritics from a Unicode Greek string for matching.
    Also unify final sigma ς (U+03C2) → σ (U+03C3) so MorphGNT lemmas
    match Dodson keys (betacode 's' always converts to σ, never ς)."""
    decomposed = unicodedata.normalize('NFD', lemma)
    stripped = ''.join(c for c in decomposed if unicodedata.category(c) != 'Mn').lower()
    return stripped.replace('ς', 'σ')

# ── Load Dodson lexicon ──
def load_dodson(path):
    """
    Columns (tab-separated, with header row):
      Strong's | GK | Greek (betacode) | Brief Definition | Longer Definition
    Returns: { normalised_greek -> {gloss, strongs} }
    """
    lexicon = {}
    if not os.path.exists(path):
        print(f"  ERROR: Dodson CSV not found at: {path}")
        print(f"  Searched from: {os.getcwd()}")
        return lexicon
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)   # ← skip header row
        for row in reader:
            if len(row) < 4:
                continue
            strongs  = row[0].strip().strip('"')
            betacode = row[2].strip().strip('"')
            gloss    = row[3].strip().strip('"')
            key = betacode_to_unicode(betacode)
            if key:
                lexicon[key] = {"gloss": gloss, "strongs": strongs}
    print(f"  Loaded {len(lexicon)} Dodson entries from {path}")
    return lexicon

# ── Load MorphGNT source ──
def load_morphgnt(path):
    """
    Columns (space-separated):
      bcv | pos | parsing | text | word | normalised | lemma
    Returns: { (ch, vs) -> [{word, lemma}] }
    """
    verses = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 7:
                continue
            ref        = parts[0]
            ch, vs     = int(ref[-4:-2]), int(ref[-2:])
            word, lemma = parts[3], parts[6]
            verses.setdefault((ch, vs), []).append({"word": word, "lemma": lemma})
    return verses

# ── Load Mistral translation ──
def load_translation(path):
    """Returns { 'ch:vs' -> text }"""
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"(\d+:\d+)\s+(.*)", line.strip())
            if m:
                out[m.group(1)] = m.group(2)
    return out

# ── Load KJV ──
def load_kjv(path):
    """Returns { 'ch:vs' -> text }"""
    out = {}
    if not os.path.exists(path):
        return out
    chapter = 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = re.match(r"CHAPTER\s+(\d+)", line, re.IGNORECASE)
            if m:
                chapter = int(m.group(1))
                continue
            # Single-chapter books have no CHAPTER header
            if chapter == 0 and re.match(r"^\d+\s+\S", line):
                chapter = 1
            vs = re.match(r"^(\d+)\s+(.*)", line)
            if vs and chapter > 0:
                out[f"{chapter:02d}:{int(vs.group(1)):02d}"] = vs.group(2).strip()
    return out

# ── Build one book ──
def build_book(code, name, kjv_file, lexicon):
    src_path   = os.path.join(SOURCES_DIR,      f"{code}-morphgnt.txt")
    trans_path = os.path.join(TRANSLATIONS_DIR, f"{code}-english.txt")
    kjv_path   = os.path.join(KJV_DIR,          kjv_file)

    if not os.path.exists(src_path):
        print(f"  SKIP {name} — missing {src_path}")
        return None

    morphgnt    = load_morphgnt(src_path)
    translation = load_translation(trans_path)
    kjv         = load_kjv(kjv_path)

    seen_lemmas = set()
    verses_out  = []
    gloss_hits  = 0

    for (ch, vs), word_list in sorted(morphgnt.items()):
        ref_key = f"{ch:02d}:{vs:02d}"
        greek   = " ".join(w["word"] for w in word_list)
        words   = []

        for w in word_list:
            lemma   = w["lemma"]
            key     = normalise_lemma(lemma)
            lex     = lexicon.get(key, {})
            gloss   = lex.get("gloss", "")
            strongs = lex.get("strongs", "")
            if gloss:
                gloss_hits += 1
            words.append({
                "greek":   w["word"],
                "lemma":   lemma,
                "gloss":   gloss,
                "strongs": strongs,
                "isNew":   lemma not in seen_lemmas,
            })
            seen_lemmas.add(lemma)

        verses_out.append({
            "ref":     f"{ch}:{vs}",
            "greek":   greek,
            "mistral": translation.get(ref_key, ""),
            "kjv":     kjv.get(ref_key, ""),
            "words":   words,
        })

    total_words = sum(len(v["words"]) for v in verses_out)
    pct = (gloss_hits / total_words * 100) if total_words else 0
    status = []
    if translation: status.append("mistral")
    if kjv:         status.append("kjv")
    print(f"  {len(verses_out)} verses | {pct:.0f}% glossed | [{', '.join(status) or 'greek only'}]")

    return {
        "code":           code,
        "name":           name,
        "verseCount":     len(verses_out),
        "hasTranslation": bool(translation),
        "hasKjv":         bool(kjv),
        "verses":         verses_out,
    }

# ── Main ──
def main():
    print(f"Working directory: {os.getcwd()}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\nLoading Dodson lexicon...")
    lexicon = load_dodson(DODSON_CSV)
    if not lexicon:
        print("\n  *** No lexicon loaded — all glosses will be empty. ***")
        print(f"  Make sure you run this script from the project root,")
        print(f"  and that {DODSON_CSV} exists.\n")

    index = []
    for code, name, kjv_file in BOOKS:
        print(f"Building {name}...")
        data = build_book(code, name, kjv_file, lexicon)
        if data is None:
            continue
        out_path = os.path.join(OUTPUT_DIR, f"{code}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        index.append({
            "code":           data["code"],
            "name":           data["name"],
            "verseCount":     data["verseCount"],
            "hasTranslation": data["hasTranslation"],
            "hasKjv":         data["hasKjv"],
        })

    with open(os.path.join(OUTPUT_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"\nDone — {len(index)} books written to {OUTPUT_DIR}/")
    print(f"Serve with:  cd docs && python3 -m http.server 8080")

if __name__ == "__main__":
    main()
