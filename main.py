import sys
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

def main():
    parser = argparse.ArgumentParser(description="Ezer Agent - Autonomous Ministry & Project AI OS")
    parser.add_argument("--web", action="store_true", help="Launch Ezer Studio Web Control Center (OpenClaw UI)")
    parser.add_argument("--discord", action="store_true", help="Launch Discord Bot Gateway")
    parser.add_argument("--telegram", action="store_true", help="Launch Telegram Bot Gateway")
    parser.add_argument("--port", type=int, default=8888, help="Port for Web UI (default: 8888)")
    args = parser.parse_args()

    if args.web:
        import uvicorn
        print(f"🖥️ [Ezer Studio] Starting Web UI on http://localhost:{args.port} ...")
        uvicorn.run("gateways.web_ui:app", host="0.0.0.0", port=args.port, reload=False)
    elif args.discord:
        from gateways.discord_bot import start_discord_bot
        print("🤖 [Ezer Agent] Starting Discord Bot Gateway...")
        start_discord_bot()
    elif args.telegram:
        from gateways.telegram_bot import TelegramGateway
        print("📱 [Ezer Agent] Starting Telegram Bot Gateway...")
        gw = TelegramGateway()
        gw.run()
    else:
        # Default: Launch Ezer Studio Web Control Center
        import uvicorn
        print(f"🖥️ [Ezer Studio] Starting Default Web UI on http://localhost:{args.port} ...")
        uvicorn.run("gateways.web_ui:app", host="0.0.0.0", port=args.port, reload=False)

if __name__ == "__main__":
    main()
