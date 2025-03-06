#!/bin/bash

# Pastikan skrip dijalankan sebagai superuser
if [[ $EUID -ne 0 ]]; then
   echo "❌ Skrip ini harus dijalankan sebagai root! Gunakan: sudo ./uninstaller.sh"
   exit 1
fi

# Nama aplikasi dan path yang digunakan
APP_NAME="YogzspWineLauncher"
INSTALL_PATH="/usr/local/bin"
DESKTOP_FILE="/usr/share/applications/$APP_NAME.desktop"
ICON_PATH="/usr/local/share/icons/$APP_NAME.png"

echo "🗑️ Menghapus aplikasi $APP_NAME..."

# Hapus script utama
if [[ -f "$INSTALL_PATH/$APP_NAME" ]]; then
    rm "$INSTALL_PATH/$APP_NAME"
    echo "✅ File utama ($INSTALL_PATH/$APP_NAME) dihapus."
else
    echo "⚠️ File utama tidak ditemukan."
fi

# Hapus script Bash
if [[ -f "$INSTALL_PATH/run_wine.sh" ]]; then
    rm "$INSTALL_PATH/run_wine.sh"
    echo "✅ File Bash ($INSTALL_PATH/run_wine.sh) dihapus."
else
    echo "⚠️ File Bash tidak ditemukan."
fi

# Hapus shortcut aplikasi
if [[ -f "$DESKTOP_FILE" ]]; then
    rm "$DESKTOP_FILE"
    echo "✅ Shortcut aplikasi ($DESKTOP_FILE) dihapus."
else
    echo "⚠️ Shortcut aplikasi tidak ditemukan."
fi

# Hapus ikon aplikasi
if [[ -f "$ICON_PATH" ]]; then
    rm "$ICON_PATH"
    echo "✅ Ikon aplikasi ($ICON_PATH) dihapus."
else
    echo "⚠️ Ikon aplikasi tidak ditemukan."
fi

echo "🚀 Uninstall selesai!"
