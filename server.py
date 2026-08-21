"""Ezer Agent – Cloud Run & Local entrypoint.

Runs the FastAPI web server on $PORT, and optionally starts the Discord bot
in a background thread if DISCORD_BOT_TOKEN is set.
"""
import os
import sys
import threading
import traceback


def _start_discord_bot_background():
    """Starts the Discord bot in a daemon thread so it runs alongside the web server."""
    token = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    if not token:
        print("ℹ️  [Discord] DISCORD_BOT_TOKEN not set — skipping Discord bot.", flush=True)
        return

    def _run():
        try:
            from gateways.discord_bot import start_discord_bot
            print("🤖 [Discord] Starting Discord bot in background thread...", flush=True)
            start_discord_bot()
        except Exception:
            print("❌ [Discord] Bot crashed:", flush=True)
            traceback.print_exc()

    t = threading.Thread(target=_run, name="discord-bot", daemon=True)
    t.start()
    print("✅ [Discord] Bot thread launched.", flush=True)


def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 [Ezer Agent] Starting server on port {port}...", flush=True)
    print(f"   Python {sys.version}", flush=True)
    print(f"   PYTHONPATH={os.environ.get('PYTHONPATH', '(not set)')}", flush=True)
    print(f"   CWD={os.getcwd()}", flush=True)

    # 1. Import FastAPI app
    try:
        from gateways.web_ui import app
        print("✅ [Ezer Agent] FastAPI app imported successfully.", flush=True)
    except Exception:
        print("❌ [Ezer Agent] FATAL: Failed to import FastAPI app!", flush=True)
        traceback.print_exc()
        sys.exit(1)

    # 2. Start Discord bot in background (if token exists)
    _start_discord_bot_background()

    # 3. Start web server (blocks main thread)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
