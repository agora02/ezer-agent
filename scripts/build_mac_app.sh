#!/bin/bash
# Self-Bootstrapping Installer for Ezer Studio Native macOS App

APP_NAME="Ezer Studio"
BUILD_DIR="$HOME/Desktop/${APP_NAME}.app"
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🔨 Building Self-Installing Standalone macOS App (${APP_NAME})..."

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/Contents/MacOS"
mkdir -p "$BUILD_DIR/Contents/Resources"

# 1. Info.plist
cat << 'EOF' > "$BUILD_DIR/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch</string>
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
</dict>
</plist>
EOF

# 2. Executable launcher script (Auto setup venv & dependencies on first run)
cat << EOF > "$BUILD_DIR/Contents/MacOS/launch"
#!/bin/bash
TARGET_DIR="${CURRENT_DIR}"

cd "\$TARGET_DIR"

# Auto setup venv & install dependencies if not installed
if [ ! -d "\$TARGET_DIR/venv" ]; then
    python3 -m venv "\$TARGET_DIR/venv"
    source "\$TARGET_DIR/venv/bin/activate"
    pip install -r "\$TARGET_DIR/requirements.txt"
fi

if [ ! -f "\$TARGET_DIR/.env" ]; then
    cp "\$TARGET_DIR/.env.example" "\$TARGET_DIR/.env"
fi

# Ensure backend server is running on 8888
if ! lsof -i:8888 > /dev/null 2>&1; then
    "\$TARGET_DIR/venv/bin/python" -m uvicorn gateways.web_ui:app --host 0.0.0.0 --port 8888 > /dev/null 2>&1 &
    sleep 1.5
fi

# Open Dedicated Standalone Window
if [ -d "/Applications/Google Chrome.app" ]; then
    open -na "Google Chrome" --args --app="http://localhost:8888"
elif [ -d "/Applications/Brave Browser.app" ]; then
    open -na "Brave Browser" --args --app="http://localhost:8888"
else
    open "http://localhost:8888"
fi
EOF

chmod +x "$BUILD_DIR/Contents/MacOS/launch"

echo "✅ [Ezer Studio.app] self-installing macOS package built on Desktop!"
