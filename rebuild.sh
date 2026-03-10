#!/bin/bash
# build_all.sh — rebuild all NT JSON from scratch

set -e

OUTPUT=docs/data
mkdir -p "$OUTPUT"

echo "Building NT JSON..."

for f in sources/*-morphgnt.txt; do
    CODE=$(basename "$f" -morphgnt.txt)
    echo "Building $CODE..."
    python3 tools/build_json.py "$f" "$OUTPUT"
done

echo "Done. JSON files in $OUTPUT/"
