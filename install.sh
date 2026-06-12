#!/bin/bash
# ============================================================
#  Yukioh_Ōkami — Termux Installer
# ============================================================

echo ""
echo "🐺 Installing Yukioh_Ōkami dependencies..."
echo "════════════════════════════════════════"

pkg update -y && pkg upgrade -y
pkg install python python-pip -y
pkg install clang libffi openssl -y

pip install --upgrade pip

pip install gmalg
pip install pycryptodome
pip install zstandard
pip install rich

echo ""
echo "════════════════════════════════════════"
echo "✅ Installation complete!"
echo ""
echo "📂 Copy the tool folder to:"
echo "   /sdcard/Download/Yukioh_Okami_Tool/"
echo ""
echo "▶  Run with:  python Yukioh_Okami.py"
echo "════════════════════════════════════════"
echo ""
