#!/usr/bin/env python3
# build_json.py — convert all NT sources to JSON for the website
#
# Run from ~/translate/:
#   python3 build_json.py
#
# Produces: web/data/{book-code}.json + web/data/index.json

import os, re, json, csv, glob

SOURCES_DIR      = "sources"
TRANSLATIONS_DIR = "translations"
KJV_DIR          = "KJV-TXT-Files"
DODSON_CSV       = "Dodson-Greek-Lexicon/dodson.csv"
OUTPUT_DIR       = "docs/data"


# ── Book metadata ──
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

# ── Betacode to Unicode (basic, covers Dodson's format) ──
def betacode_to_unicode(b):
    """Very basic betacode conversion sufficient for lemma matching.
    Strips accents/breathings and normalises to lowercase Greek Unicode."""
    import unicodedata
    # Strip anything that isn't a Greek letter in betacode (punctuation, digits in parens)
    b = re.sub(r'[^a-zA-Z]', '', b)
    table = {
        'a':'α','b':'β','g':'γ','d':'δ','e':'ε','z':'ζ','h':'η','q':'θ',
        'i':'ι','k':'κ','l':'λ','m':'μ','n':'ν','c':'ξ','o':'ο','p':'π',
        'r':'ρ','s':'σ','t':'τ','u':'υ','f':'φ','x':'χ','y':'ψ','w':'ω',
    }
    result = ''.join(table.get(c.lower(), '') for c in b)
    return result

# ── Load Dodson lexicon ──
def load_dodson(path):
    """Returns dict: normalised_greek_lemma -> gloss
    Columns (tab-separated):
      Strong's | GK | Greek Word (betacode) | Brief Definition | Longer Definition
    """
    lexicon = {}
    if not os.path.exists(path):
        print(f"  WARNING: Dodson not found at {path}")
        return lexicon
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # skip header
        for row in reader:
            if len(row) < 4:
                continue
            betacode = row[2].strip().strip('"')
            gloss    = row[3].strip().strip('"')
            strongs  = row[0].strip().strip('"')
            # Convert betacode lemma to plain Greek for matching
            key = betacode_to_unicode(betacode)
            if key:
                lexicon[key] = {"gloss": gloss, "strongs": strongs}
    print(f"  Loaded {len(lexicon)} Dodson entries")
    return lexicon

def normalise_lemma(lemma):
    """Strip accents/diacritics from a Unicode Greek string for matching."""
    import unicodedata
    # Decompose, then keep only base Greek letters
    decomposed = unicodedata.normalize('NFD', lemma)
    return ''.join(c for c in decomposed if unicodedata.category(c) != 'Mn').lower()

# ── Load MorphGNT ──
def load_morphgnt(path):
    """Returns dict: (ch, vs) -> list of {word, lemma}
    MorphGNT columns (space separated):
      bcv | pos | parsing | text | word | normalised | lemma
    """
    verses = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 7:
                continue
            ref   = parts[0]
            ch, vs = int(ref[-4:-2]), int(ref[-2:])
            word  = parts[3]   # surface form
            lemma = parts[6]   # lemma is column 7
            verses.setdefault((ch, vs), []).append({
                "word":  word,
                "lemma": lemma,
            })
    return verses

# ── Load Mistral translation ──
def load_translation(path):
    """Returns dict: 'ch:vs' -> translation string"""
    result = {}
    if not os.path.exists(path):
        return result
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"(\d+:\d+)\s+(.*)", line.strip())
            if m:
                result[m.group(1)] = m.group(2)
    return result

# ── Load KJV ──
def load_kjv(path):
    """Returns dict: 'ch:vs' -> kjv string
    KJV files format:
        CHAPTER 1
        1 Verse text here...
        2 Next verse...
        CHAPTER 2
        1 First verse of chapter 2...
    """
    result = {}
    if not os.path.exists(path):
        return result
    current_chapter = 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Detect chapter header: "CHAPTER 3" or "CHAPTER THE FIRST" etc.
            ch_match = re.match(r"CHAPTER\s+(\d+)", line, re.IGNORECASE)
            if ch_match:
                current_chapter = int(ch_match.group(1))
                continue
            # Single-chapter books (Jude, Philemon, 2&3 John, Obadiah etc.)
            # have no CHAPTER line — default to chapter 1
            if current_chapter == 0 and re.match(r"^\d+\s+\S", line):
                current_chapter = 1
            # Verse line: starts with a number then space
            vs_match = re.match(r"^(\d+)\s+(.*)", line)
            if vs_match and current_chapter > 0:
                vs   = int(vs_match.group(1))
                text = vs_match.group(2).strip()
                key  = f"{current_chapter:02d}:{vs:02d}"
                result[key] = text
    return result

# ── Build one book ──
def build_book(code, name, kjv_filename, lexicon):
    src_path   = os.path.join(SOURCES_DIR, f"{code}-morphgnt.txt")
    trans_path = os.path.join(TRANSLATIONS_DIR, f"{code}-english.txt")
    kjv_path   = os.path.join(KJV_DIR, kjv_filename)

    if not os.path.exists(src_path):
        print(f"  SKIP {name} — no morphgnt source")
        return None

    morphgnt    = load_morphgnt(src_path)
    translation = load_translation(trans_path)
    kjv         = load_kjv(kjv_path)

    has_translation = bool(translation)
    has_kjv         = bool(kjv)

    # Track seen lemmas for new-word flagging
    seen_lemmas = set()
    verses_out  = []

    for (ch, vs), word_list in sorted(morphgnt.items()):
        ref_key = f"{ch:02d}:{vs:02d}"
        ref_display = f"{ch}:{vs}"

        # Greek text
        greek = " ".join(w["word"] for w in word_list)

        # Build word entries
        words = []
        for w in word_list:
            lemma = w["lemma"]
            # Normalise lemma (strip accents) for Dodson lookup
            key   = normalise_lemma(lemma)
            lex   = lexicon.get(key, {})
            gloss   = lex.get("gloss", "")
            strongs = lex.get("strongs", "")
            is_new = lemma not in seen_lemmas
            seen_lemmas.add(lemma)
            words.append({
                "greek":   w["word"],
                "lemma":   lemma,
                "gloss":   gloss,
                "strongs": strongs,
                "isNew":   is_new,
            })

        verse = {
            "ref":     ref_display,
            "greek":   greek,
            "mistral": translation.get(ref_key, ""),
            "kjv":     kjv.get(ref_key, ""),
            "words":   words,
        }
        verses_out.append(verse)

    return {
        "code":           code,
        "name":           name,
        "verseCount":     len(verses_out),
        "hasTranslation": has_translation,
        "hasKjv":         has_kjv,
        "verses":         verses_out,
    }

# ── Main ──
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading Dodson lexicon...")
    lexicon = load_dodson(DODSON_CSV)

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
            "code":           code,
            "name":           name,
            "verseCount":     data["verseCount"],
            "hasTranslation": data["hasTranslation"],
            "hasKjv":         data["hasKjv"],
        })
        status = []
        if data["hasTranslation"]: status.append("mistral")
        if data["hasKjv"]:         status.append("kjv")
        print(f"  {data['verseCount']} verses [{', '.join(status) if status else 'greek only'}]")

    # Write index
    index_path = os.path.join(OUTPUT_DIR, "index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"\nDone — {len(index)} books written to {OUTPUT_DIR}/")
    print(f"Run the site with:")
    print(f"  cd web && python3 -m http.server 8080")
    print(f"  then open http://localhost:8080")

if __name__ == "__main__":
    main()
