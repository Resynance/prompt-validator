#!/bin/bash

# Navigate to the project root (where the script is located likely in /scripts)
# This ensures it works if called from within scripts folder or root
PARENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PARENT_DIR"

# 1. Extract version from app.py
VERSION=$(grep "VERSION =" app.py | cut -d'"' -f2)

if [ -z "$VERSION" ]; then
    echo "Error: Could not find VERSION in app.py"
    exit 1
fi

FILENAME="prompt-manager-v$VERSION.tgz"

echo "[~] Packaging Prompt Similarity Detector v$VERSION..."

# 2. Cleanup old artifacts
echo "[~] Removing old .tgz packages..."
rm -f *.tgz

echo "[~] Creating artifact: $FILENAME"

# 2. Create the archive
# Excludes:
# - venv, .git, __pycache__: Standard system/dev bloat
# - .pytest_cache, .vscode: Dev tools
# - *.tgz: Existing archives
tar -czvf "$FILENAME" \
    --exclude='venv' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='.pytest_cache' \
    --exclude='.vscode' \
    --exclude='*.tgz' \
    --exclude='.DS_Store' \
    .

if [ $? -eq 0 ]; then
    echo -e "\n[+] Success! Release artifact created: $FILENAME"
    # Show size
    SIZE=$(du -h "$FILENAME" | cut -f1)
    echo "[i] Artifact size: $SIZE"
else
    echo -e "\n[!] Error: Packaging failed."
    exit 1
fi
