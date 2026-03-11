# Greek-English Corpus

A static website presenting Greek texts with machine translations. No canonical hierarchy — the New Testament, Marcion's Evangelion, and Josephus are treated as equal sources. Hosted on GitHub Pages.

**Thesis context**: The project deliberately avoids privileging "biblical" texts over contemporary sources. Mary of Bethezuba (Josephus) sits alongside Mary of Nazareth. Jesus son of Ananus (Josephus) alongside Jesus of Nazareth. Marcion's Evangelion sits alongside Matthew and Luke. Mistral 7B translates all of them neutrally because it is not told what it is translating.

Live site: `https://bethezuba.github.io/NT/`

---

## Texts Included

| Text | Author | Verses | Greek source |
|------|--------|--------|--------------|
| New Testament (27 books) | — | ~7,959 | MorphGNT, CC BY-SA 3.0 |
| Evangelion | Marcion of Sinope (BeDuhn–Bilby reconstruction) | 552 | JOHD 2023, CC BY-NC-ND |
| Jewish War VI (Mary–Vespasian oracle passage) | Flavius Josephus | 38 | Open corpus |

---

## Translation Method

**Model**: Mistral 7B (Mistral AI).

**Critical rule**: Mistral is never told what text it is translating — no author, no title, no context beyond "Koine Greek." Each unit is translated independently with a fixed prompt:

```
You are translating Koine Greek into formal English.
Verse: {ref}.
Previous verse for context: {prev}.
Translate the Greek below into English.
Output only the English translation — no notes, no alternatives, no Latin,
no Greek characters, no preamble, no commentary.
Begin your response immediately with the first word of the English translation.
Greek: {greek}
```

No content restrictions applied. Machine translation, unreviewed. Not for citation without verification against the Greek.

---

## Viewer

Single HTML file (`docs/index.html`), no framework, no build step.

**Study mode**: one verse at a time, Greek text, word-by-word lexicon grid (NT only), Mistral translation, KJV.

**Read mode**: flowing prose, no verse numbers. Tabs: Greek / English / KJV (NT) or Greek / English / Whiston 1737 (Josephus).

---

## Sources & Attribution

**Greek New Testament**: MorphGNT (https://github.com/morphgnt/morphgnt), CC BY-SA 3.0.

**Greek Lexicon**: Dodson Greek Lexicon (https://github.com/morphgnt/dodson-lexicon), public domain.

**King James Version**: KJV 1611, public domain.

**Marcion's Evangelion**: BeDuhn–Bilby Greek reconstruction. Mark G. Bilby and Jason D. BeDuhn, *Journal of Open Humanities Data* (2023). CC BY-NC-ND. https://openhumanitiesdata.metajnl.com/articles/10.5334/johd.126

**Josephus — Jewish War**: Greek text from open corpus. W. Whiston (1737) translation reproduced in read mode for comparison, public domain.

**English translations**: Mistral 7B (Mistral AI). See method above.

---

## Adding a New Text

1. Produce `{code}_greek.txt` — one sentence or verse per line
2. Run `translate_{code}.py` → `{code}_english.txt` (tab-separated: `N\ttranslation`)
3. Run `build_{code}_json.py` → `docs/data/{code}.json` + updates `docs/data/index.json`
4. Commit and push

Translation scripts are resumable — interrupt and restart freely.

---

## Dev

```bash
cd ~/NT/docs
python3 -m http.server 8080
```

```bash
cd ~/NT
git add -A
git commit -m "message"
git push origin master
```
