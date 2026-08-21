import os
import uvicorn
from gateways.web_ui import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 [Cloud Run & Local] Starting Ezer Agent server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
