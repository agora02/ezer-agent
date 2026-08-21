#!/bin/bash
# Standalone Native Swift macOS App Binary Compiler

set -e

APP_NAME="Ezer Studio"
APP_DIR="$HOME/Desktop/${APP_NAME}.app"
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🚀 Compiling Native Swift / SwiftUI macOS Binary for ${APP_NAME}..."

rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

swiftc -O \
    -parse-as-library \
    -target arm64-apple-macos12.0 \
    -framework SwiftUI \
    -framework AppKit \
    -framework WebKit \
    "$CURRENT_DIR/mac_app/EzerStudioApp.swift" \
    -o "$APP_DIR/Contents/MacOS/EzerStudio"

# 2. Copy App Icon
if [ -f "$CURRENT_DIR/assets/app_icon.icns" ]; then
    cp "$CURRENT_DIR/assets/app_icon.icns" "$APP_DIR/Contents/Resources/app_icon.icns"
fi

# 3. Create Info.plist
cat << EOF > "$APP_DIR/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>EzerStudio</string>
    <key>CFBundleIconFile</key>
    <string>app_icon</string>
    <key>CFBundleIdentifier</key>
    <string>com.ezer.agent.studio</string>
    <key>CFBundleName</key>
    <string>Ezer Studio</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>12.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
</dict>
</plist>
EOF

echo "🎉 [Ezer Studio.app] 100% Native Swift macOS App Binary built successfully on Desktop!"
