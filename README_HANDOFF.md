# Greek-English Corpus — Project Handoff

## What This Is

A static website serving Greek texts with machine translations (Mistral 7B, local via Ollama).
No canonical hierarchy — NT, Josephus, and apocrypha treated as equal source texts.
Hosted on GitHub Pages. Built with plain Python + vanilla JS, no frameworks.

**Thesis context**: The project deliberately avoids privileging "biblical" texts over
contemporary sources. Mary of Bethezuba (Josephus) sits alongside Mary of Nazareth.
Jesus son of Ananus (Josephus) alongside Jesus of Nazareth. Mistral 7B translates
both neutrally because it is not told what it is translating.

---

## Repository

- **Repo**: `github.com/Bethezuba/NT.git`
- **Active branch**: `corpus` (working branch — do not touch master until ready to merge)
- **GitHub Pages**: served from `/docs` on `master`
- **Local path**: `~/NT/`

---

## Project Structure

```
~/NT/
├── docs/                        ← GitHub Pages root
│   ├── index.html               ← Single-page viewer (Study + Read modes)
│   └── data/
│       ├── index.json           ← Book list (plain JSON array)
│       ├── 61-Mt.json           ← NT books (27 total)
│       ├── 62-Mk.json
│       ├── ...
│       └── wars6.json           ← Josephus Jewish War VI
│
├── sources/
│   ├── wars6_greek.txt          ← 38 sentences, one per line
│   ├── wars6_english.txt        ← tab-separated: N\ttranslation
│   ├── wars6_whiston.txt        ← Whiston 1737, plain prose block
│   ├── 61-Mt-morphgnt.txt       ← MorphGNT source files
│   ├── ...
│   ├── KJV-TXT-Files/           ← KJV plain text
│   └── canonical-greekLit/      ← Perseus XML corpus
│
├── lexicon/
│   └── Dodson-Greek-Lexicon/
│       └── dodson.csv
│
├── translations/
│   ├── 61-Mt-english.txt        ← Mistral translations, tab-separated
│   └── ...
│
├── build_all_json.py            ← Builds all 27 NT book JSONs
├── build_josephus_json.py       ← Builds wars6.json
└── translate_thomas.py          ← Translation script for Acts of Thomas
```

---

## Data Formats

### index.json (plain array)
```json
[
  {"code": "61-Mt", "name": "Matthew", "verseCount": 1068,
   "hasTranslation": true, "hasKjv": true},
  ...
  {"code": "wars6", "name": "Jewish War VI", "author": "Flavius Josephus",
   "type": "prose", "group": "josephus", "verseCount": 38,
   "hasTranslation": true, "hasKjv": false, "hasWhiston": true}
]
```

### NT book JSON (e.g. 61-Mt.json)
```json
{
  "code": "61-Mt", "name": "Matthew",
  "verseCount": 1068, "hasTranslation": true, "hasKjv": true,
  "verses": [
    {
      "ref": "1:1", "greek": "Βίβλος γενέσεως...",
      "mistral": "The book of the generation...",
      "kjv": "The book of the generation of Jesus Christ...",
      "words": [
        {"greek": "Βίβλος", "lemma": "βίβλος", "gloss": "book",
         "strongs": "G976", "isNew": true},
        ...
      ]
    }
  ]
}
```

### Josephus JSON (wars6.json)
```json
{
  "code": "wars6", "name": "Jewish War VI",
  "author": "Flavius Josephus", "type": "prose", "group": "josephus",
  "verseCount": 38, "hasTranslation": true, "hasKjv": false, "hasWhiston": true,
  "whiston_text": "There was a certain woman...[full Whiston prose block]",
  "verses": [
    {"ref": "Wars VI.1", "n": 1,
     "greek": "Μαρία τοὔνομα...",
     "mistral": "Mary, of the house of Jesse...",
     "kjv": ""}
  ]
}
```

---

## Translation Pipeline

**Model**: `mistral:7b` running locally via Ollama on an N100 mini PC.

**Critical prompt rule**: DO NOT tell Mistral what text it is translating.
No author name, no book title. It sees only "Koine Greek" and a verse number.
This prevents bias. Tested: Mistral translates Mary of Bethezuba and Mary of
Nazareth with identical register. Whiston (1737) does not.

**Prompt template** (must not change):
```python
f"You are translating Koine Greek into formal English. "
f"Verse: {ref}. "
f"Previous verse for context: {prev}. "
f"Translate the Greek below into English. "
f"Output only the English translation — no notes, no alternatives, no Latin, "
f"no Greek characters, no preamble, no commentary. "
f"Begin your response immediately with the first word of the English translation.{strictness} "
f"Greek: {greek}"
```

**Translation scripts**:
- `~/text-helper/translate_wars6.py` — Josephus Wars VI (done, 38/38)
- `~/NT/translate_thomas.py` — Acts of Thomas (not yet run)
- NT was translated by an earlier version of the same pipeline

**Output format** (all translation files):
```
1\tFirst sentence translation here
2\tSecond sentence translation here
```
Tab-separated, resumable (script checks what's done and skips).

---

## Sources & Attribution

| Source | Location | License |
|--------|----------|---------|
| MorphGNT (Greek NT) | `sources/61-Mt-morphgnt.txt` etc. | CC BY-SA 3.0 |
| Dodson Lexicon | `lexicon/Dodson-Greek-Lexicon/dodson.csv` | Public domain |
| KJV | `sources/KJV-TXT-Files/` | Public domain |
| Josephus Greek | `corpus_OLD/flavius_josephus.txt` (in `~/text-helper/`) | Open corpus |
| Whiston (1737) | `sources/wars6_whiston.txt` | Public domain |
| Mistral 7B | via Ollama | Apache 2.0 |

**Forthcoming / planned**:
- BeDuhn–Bilby Greek reconstruction of Marcion's Evangelion
  (Journal of Open Humanities Data, 2023, CC BY-NC-ND)
  Download from: https://openhumanitiesdata.metajnl.com/articles/10.5334/johd.126
  Want the UTF-8 TXT with morphological tagging (closest to MorphGNT format)

---

## Viewer (docs/index.html)

Single HTML file, no build step, no framework.

**Modes**:
- **Study**: one verse/sentence at a time, Greek block + word grid (NT only,
  requires `words` array) + Mistral + KJV translations
- **Read**: flowing prose, no verse numbers, tabs for Greek / English / KJV (NT)
  or Greek / English / Whiston 1737 (Josephus)

**Sidebar groups**:
- New Testament (27 books, from index.json entries without `group: josephus`)
- Josephus (entries with `group: "josephus"`)
- Add more groups by adding new `group` values to index.json entries

**Adding a new text**:
1. Get Greek source, produce `{code}_greek.txt` (one sentence/verse per line)
2. Run translation script → `{code}_english.txt` (tab-separated)
3. Write `build_{code}_json.py` following `build_josephus_json.py` pattern
4. Run it → `docs/data/{code}.json` + updates `docs/data/index.json`
5. Commit and push to `corpus` branch

---

## Next Task: Marcion's Evangelion

**What it is**: BeDuhn–Bilby (2023) Greek reconstruction of Marcion's gospel.
Predates canonical gospels in manuscript tradition. No infancy narrative.
Scholars have avoided it for 200 years. Treat it identically to Matthew/Luke.

**Where to get it**:
https://openhumanitiesdata.metajnl.com/articles/10.5334/johd.126

Download the **UTF-8 TXT with morphological tagging** — this is closest to
MorphGNT format and may allow word-level glossing like the NT books.
Also download the plain UTF-8 TXT as fallback.

**Expected pipeline**:
1. Inspect the TXT format: `head -30 marcion_morphtagged.txt`
2. If columns match MorphGNT: adapt `build_all_json.py` directly
3. If different format: write `build_marcion_json.py` following Josephus pattern
4. Add to sidebar under a new group, e.g. `"group": "apocrypha"` or `"group": "marcion"`
5. Translation: same script pattern as wars6/thomas, same prompt, no title given

**Key issue to check**: The BeDuhn–Bilby text is a *reconstruction* — it has
critical apparatus and footnotes. The TXT version should strip these. Verify
the Greek is clean Unicode before running through Mistral.

---

## Known Issues / To-Do

- [ ] Acts of Thomas translation not yet run (`translate_thomas.py` written, ready)
- [ ] Marcion Evangelion not yet downloaded
- [ ] `corpus` branch not yet merged to `master`
- [ ] Josephus study mode has no word grid (no MorphGNT data — acceptable)
- [ ] Long Josephus sentences (800-1500 chars) required timeout=1200 in translate script
- [ ] Verify all 38 Wars VI sentences translated: `sort -n wars6_english.txt | awk -F'\t' '{print $1}'`

---

## Dev Server

```bash
cd ~/NT/docs
python3 -m http.server 8080
# open http://localhost:8080
```

## Deploy

```bash
cd ~/NT
git add -A
git commit -m "your message"
git push origin corpus
# GitHub Pages auto-deploys from master — merge corpus→master when ready
git checkout master && git merge corpus && git push origin master
```
