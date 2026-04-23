#!/bin/bash
set -e
echo "[MMBA] Pushing to GitHub..."
git add .
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
git commit -m "MMBA update — $TIMESTAMP" --allow-empty
git push -u origin main
echo "✓ Push complete!"
