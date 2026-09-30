#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

BUNDLE_FILE="${1:-$HOME/archinstall-termux-bundle-arm64.tar.gz}"

if [ ! -f "$BUNDLE_FILE" ]; then
    if [ -f "/sdcard/Download/archinstall-termux-bundle-arm64.tar.gz" ]; then
        BUNDLE_FILE="/sdcard/Download/archinstall-termux-bundle-arm64.tar.gz"
    else
        echo "[-] Error: Archive not found at $BUNDLE_FILE or /sdcard/Download/"
        exit 1
    fi
fi

echo "[*] Extracting portable environment from $BUNDLE_FILE..."
tar -xzf "$BUNDLE_FILE" -C "$HOME"

echo "[*] Installing required binaries to PREFIX..."
mkdir -p "$PREFIX/bin"
cp "$HOME/downloads/archinstall/archinstall/bin/"* "$PREFIX/bin/" 2>/dev/null || true

# Recreate essential stubs if missing
if ! command -v lsblk >/dev/null 2>&1; then
    echo "[*] Initializing mock device handler..."
    set-mock-disk nvme 512
fi

echo "[*] Re-installing editable archinstall Python module..."
cd "$HOME/downloads/archinstall"
pip install --no-deps -e . >/dev/null

echo "[+] Validation suite ready."
arch-val-disk "$HOME/nvme_btrfs_subvols.json"
