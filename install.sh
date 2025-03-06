#!/bin/bash

# Pastikan skrip dijalankan sebagai superuser
if [[ $EUID -ne 0 ]]; then
   echo "❌ Skrip ini harus dijalankan sebagai root! Gunakan: sudo ./installer.sh"
   exit 1
fi

# Nama file utama
SRC_DIR="./src"
SCRIPT_NAME="index.py"
BASH_SCRIPT="run_wine.sh"
ICON_FILE="icon.png"
APP_NAME="YogzspWineLauncher"

INSTALL_PATH="/usr/local/bin"
DESKTOP_FILE="/usr/share/applications/$APP_NAME.desktop"
ICON_PATH="/usr/local/share/icons/$APP_NAME.png"

echo "🔧 Memeriksa dependencies..."

# Cek dan install Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 tidak ditemukan, menginstal..."
    apt update && apt install -y python3 python3-pip
else
    echo "✅ Python3 sudah terinstal."
fi

# Cek dan install PyQt6
if ! python3 -c "import PyQt6" &> /dev/null; then
    echo "❌ PyQt6 tidak ditemukan, menginstal..."
    python3 -m pip install PyQt6 --break-system-packages
else
    echo "✅ PyQt6 sudah terinstal."
fi

# Cek dan install Wine
if ! command -v wine &> /dev/null; then
    echo "❌ Wine tidak ditemukan, menginstal..."
    dpkg --add-architecture i386 && apt update
    apt install -y wine wine32:i386
else
    echo "✅ Wine sudah terinstal."
fi

# Pastikan direktori instalasi ada
mkdir -p "$INSTALL_PATH"

# Pindahkan script Python
if [[ -f "$SRC_DIR/$SCRIPT_NAME" ]]; then
    echo "🔧 Memindahkan $SCRIPT_NAME ke $INSTALL_PATH/$APP_NAME..."
    cp "$SRC_DIR/$SCRIPT_NAME" "$INSTALL_PATH/$APP_NAME"
    chmod +x "$INSTALL_PATH/$APP_NAME"
else
    echo "❌ File $SCRIPT_NAME tidak ditemukan di $SRC_DIR!"
    exit 1
fi

# Pindahkan script Bash untuk menjalankan Wine
if [[ -f "$SRC_DIR/$BASH_SCRIPT" ]]; then
    echo "🔧 Memindahkan $BASH_SCRIPT ke $INSTALL_PATH/$BASH_SCRIPT..."
    cp "$SRC_DIR/$BASH_SCRIPT" "$INSTALL_PATH/$BASH_SCRIPT"
    chmod +x "$INSTALL_PATH/$BASH_SCRIPT"
else
    echo "❌ File $BASH_SCRIPT tidak ditemukan di $SRC_DIR!"
    exit 1
fi

# Salin ikon jika ada
if [[ -f "$SRC_DIR/$ICON_FILE" ]]; then
    echo "🖼️ Menyalin ikon..."
    mkdir -p /usr/local/share/icons/
    cp "$SRC_DIR/$ICON_FILE" "$ICON_PATH"
else
    echo "⚠️ Ikon tidak ditemukan, menggunakan default."
fi

# Buat file .desktop agar muncul di menu aplikasi
echo "📝 Membuat shortcut aplikasi..."
cat > "$DESKTOP_FILE" <<EOL
[Desktop Entry]
Version=1.0
Name=$APP_NAME
Comment=A simple game launcher using Wine
Exec=$INSTALL_PATH/$APP_NAME
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Game;
EOL

# Beri izin eksekusi pada file .desktop
chmod +x "$DESKTOP_FILE"

echo "✅ Instalasi selesai! Anda dapat menjalankan aplikasi dari menu atau dengan perintah '$APP_NAME'."
