#!/bin/bash
# OpenClaw-style macOS launchd daemon installer with Auto-Reloading for Apple MLX AE Agent

PLIST_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$PLIST_DIR"
PLIST_PATH="$PLIST_DIR/com.ae.mlx.agent.plist"
PROJECT_DIR="/Users/jeewonchoi/Documents/antigravity/mlx_agent"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"

echo "[AE MLX Daemon] Creating macOS launchd plist at $PLIST_PATH with Hot-Reloading Watcher..."

cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ae.mlx.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>$VENV_PYTHON</string>
        <string>$PROJECT_DIR/scripts/auto_reloader.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/data/mlx_agent.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/data/mlx_agent.err.log</string>
</dict>
</plist>
EOF

echo "[AE MLX Daemon] Loading launchd service..."
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load -w "$PLIST_PATH"

echo "✅ [AE MLX Daemon] Apple MLX AE Agent is now running 24/7 with Autonomous Hot-Reloading!"
echo "   Status log: $PROJECT_DIR/data/mlx_agent.log"
