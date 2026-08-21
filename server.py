"""Ezer Agent – Cloud Run & Local entrypoint.

This file is the single production entrypoint.
It prints diagnostics BEFORE importing the FastAPI app so that any import
crash will at least leave a traceback in Cloud Logging.
"""
import os
import sys
import traceback

def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 [Ezer Agent] Starting server on port {port}...", flush=True)
    print(f"   Python {sys.version}", flush=True)
    print(f"   PYTHONPATH={os.environ.get('PYTHONPATH', '(not set)')}", flush=True)
    print(f"   CWD={os.getcwd()}", flush=True)

    try:
        from gateways.web_ui import app  # noqa: F811
        print("✅ [Ezer Agent] FastAPI app imported successfully.", flush=True)
    except Exception:
        print("❌ [Ezer Agent] FATAL: Failed to import FastAPI app!", flush=True)
        traceback.print_exc()
        sys.exit(1)

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()
