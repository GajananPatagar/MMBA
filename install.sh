#!/bin/bash
# MMBA One-Command Installer
# Run this on PC: curl -fsSL https://raw.githubusercontent.com/GajananPatagar/MMBA/main/install.sh | bash

set -e

echo "╔══════════════════════════════════════════╗"
echo "║   MMBA Auto-Installer                   ║"
echo "║   IHTM Department                       ║"
echo "╚══════════════════════════════════════════╝"

OS=$(uname -s)
ARCH=$(uname -m)
INSTALL_DIR="$HOME/MMBA"
REPO="GajananPatagar/MMBA"

echo "[1/5] Detecting system..."
echo "  OS   : $OS"
echo "  ARCH : $ARCH"

echo "[2/5] Installing Python if needed..."
if ! command -v python3 &>/dev/null; then
    if [ "$OS" = "Linux" ]; then
        sudo apt-get install -y python3 python3-pip 2>/dev/null || \
        sudo yum install -y python3 2>/dev/null || \
        echo "Please install Python3 manually"
    elif [ "$OS" = "Darwin" ]; then
        brew install python3
    fi
fi

echo "[3/5] Downloading MMBA..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Get latest release binary
LATEST=$(curl -s "https://api.github.com/repos/$REPO/releases/latest" | \
    grep '"tag_name"' | cut -d'"' -f4)

if [ -z "$LATEST" ]; then
    echo "  No release found. Downloading from source..."
    curl -fsSL "https://github.com/$REPO/archive/refs/heads/main.zip" -o mmba.zip
    unzip -q mmba.zip
    mv MMBA-main/* .
    rm -rf MMBA-main mmba.zip
else
    echo "  Latest version: $LATEST"
    if [ "$OS" = "Linux" ]; then
        curl -fsSL "https://github.com/$REPO/releases/download/$LATEST/MMBA-Linux.zip" -o mmba.zip
        unzip -q mmba.zip
        chmod +x MMBA
    fi
fi

echo "[4/5] Installing brain automatically..."
python3 installer.py

echo "[5/5] Starting MMBA..."
echo ""
echo "════════════════════════════════════════════"
echo "  ✓ MMBA Installed at: $INSTALL_DIR"
echo "════════════════════════════════════════════"
echo ""
echo "  Run anytime with:"
echo "  cd $HOME/MMBA && python3 main.py --mode manual"
echo ""

python3 main.py --mode status
