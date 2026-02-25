#!/bin/bash

set -e

echo "========================================"
echo "  Building Sentinel via Nuitka"
echo "========================================"

ICON_PATH="assets/icon.png"
if [ ! -f "$ICON_PATH" ]; then
    echo "⚠️  Warning: Icon not found at $ICON_PATH."
    echo "The app will build, but it will use the generic OS executable icon."
    ICON_FLAG=""
else
    echo "✅ Icon found."
    ICON_FLAG="--linux-icon=$ICON_PATH"
fi

echo "🚀 Starting Nuitka compilation. This may take a few minutes..."

EXCLUDES="--nofollow-import-to=scipy --nofollow-import-to=pandas --nofollow-import-to=matplotlib --nofollow-import-to=tkinter"

python3 -m nuitka \
    --onefile \
    --lto=no \
    --enable-plugin=pyside6 \
    --enable-plugin=upx \
    --include-package=psutil \
    --include-package=pyqtgraph \
    --include-module=PySide6.QtOpenGL \
    --include-module=PySide6.QtOpenGLWidgets \
    --include-data-dir=assets=assets \
    $EXCLUDES \
    $ICON_FLAG \
    --output-dir=build \
    --output-filename=Sentinel \
    --remove-output \
    main.py

echo "✅ Compilation successful!"

EXECUTABLE_PATH="$(pwd)/build/Sentinel"

if command -v strip &> /dev/null && [ -f "$EXECUTABLE_PATH" ]; then
    echo "🗜️ Stripping debug symbols to reduce size..."
    strip -s "$EXECUTABLE_PATH"
fi

echo "🖥️  Installing Desktop Shortcut..."

APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons"

mkdir -p "$APP_DIR"
mkdir -p "$ICON_DIR"

if [ -f "$ICON_PATH" ]; then
    cp "$ICON_PATH" "$ICON_DIR/sentinel.png"
fi

cat <<EOF > "$APP_DIR/sentinel.desktop"
[Desktop Entry]
Version=1.0
Name=Sentinel
Comment=Adaptive Streaming Multivariate Statistical Monitor
Exec=$EXECUTABLE_PATH
Icon=sentinel
Terminal=false
Type=Application
Categories=System;Monitor;Utility;
EOF

update-desktop-database "$APP_DIR" || true

echo "========================================"
echo "🎉 Build and Installation Complete!"
echo "You can now press your Super/Windows key, type 'Sentinel', and launch the app."
echo "========================================"