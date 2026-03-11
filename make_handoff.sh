#!/bin/bash
# Run from ~/NT
OUT=~/corpus_handoff_$(date +%Y%m%d).tar.gz

tar czf $OUT \
  README.md \
  docs/index.html \
  docs/data/index.json \
  docs/data/wars6.json \
  docs/data/marcion.json \
  sources/wars6_greek.txt \
  sources/wars6_english.txt \
  sources/wars6_whiston.txt \
  sources/marcion_normalized.txt \
  sources/marcion_english.txt \
  build_all_json.py \
  build_josephus_json.py \
  build_marcion_json.py \
  translate_marcion.py \
  2>/dev/null

# One sample NT book so the format is clear
tar rzf $OUT docs/data/64-Jn.json 2>/dev/null

echo "Created: $OUT"
tar tzf $OUT
