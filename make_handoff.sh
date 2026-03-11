#!/bin/bash
# make_handoff.sh
# Creates a minimal tar for LLM handoff — no large corpus files, no node_modules etc.
# Run from ~/NT:
#   bash make_handoff.sh

set -e
OUT="corpus_handoff_$(date +%Y%m%d).tar.gz"

tar czf ~/$OUT \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='sources/canonical-greekLit' \
  --exclude='sources/First1KGreek' \
  --exclude='sources/KJV-TXT-Files' \
  --exclude='sources/*-morphgnt.txt' \
  README_HANDOFF.md \
  docs/index.html \
  docs/data/index.json \
  docs/data/wars6.json \
  sources/wars6_greek.txt \
  sources/wars6_english.txt \
  sources/wars6_whiston.txt \
  build_josephus_json.py \
  build_all_json.py \
  translate_thomas.py \
  2>/dev/null || true

# Also grab a sample NT book so the format is clear
tar rzf ~/$OUT docs/data/64-Jn.json 2>/dev/null || true

echo "Created: ~/$OUT"
echo ""
echo "Contents:"
tar tzf ~/$OUT
