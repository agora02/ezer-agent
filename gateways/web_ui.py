import os
import json
from pathlib import Path
from typing import Dict, Any, List
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
MEMORY_FILE = BASE_DIR / "data" / "long_term_memory.json"

load_dotenv(ENV_FILE)

app = FastAPI(title="Ezer Agent (AE Agent Control Center)")

class SettingsUpdate(BaseModel):
    gemini_api_key: str = ""
    discord_bot_token: str = ""
    telegram_bot_token: str = ""
    notion_api_key: str = ""
    notion_default_page_id: str = ""
    email_user: str = ""
    email_pass: str = ""

class MemoryUpdate(BaseModel):
    user_name: str = "User"
    primary_project: str = "Default Project"
    custom_facts: List[str] = []

class TestChatRequest(BaseModel):
    message: str

@app.get("/health")
@app.get("/healthz")
def health_check():
    return {"status": "healthy", "service": "ezer-agent"}

@app.get("/api/status")
def get_status():
    try:
        from tools.system_tools import get_system_status
        sys_status = get_system_status()
    except Exception:
        sys_status = "System status unavailable"

    env_keys = {
        "has_gemini": bool(os.getenv("GEMINI_API_KEY")),
        "has_discord": bool(os.getenv("DISCORD_BOT_TOKEN")),
        "has_telegram": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
        "has_notion": bool(os.getenv("NOTION_API_KEY")),
        "has_email": bool(os.getenv("EMAIL_USER") and os.getenv("EMAIL_PASS")),
    }
    return {
        "system": sys_status,
        "env_status": env_keys,
        "engine": "Google Gemini 3.6 Flash / Pro Hybrid",
        "agent_name": "Ezer Agent (Autonomous AI OS)"
    }

@app.get("/api/settings")
def get_settings():
    load_dotenv(ENV_FILE, override=True)
    return {
        "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
        "discord_bot_token": os.getenv("DISCORD_BOT_TOKEN", ""),
        "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "notion_api_key": os.getenv("NOTION_API_KEY", ""),
        "notion_default_page_id": os.getenv("NOTION_DEFAULT_PAGE_ID", ""),
        "email_user": os.getenv("EMAIL_USER", ""),
        "email_pass": os.getenv("EMAIL_PASS", "")
    }

@app.post("/api/settings")
def save_settings(settings: SettingsUpdate):
    env_content = f"""USE_OLLAMA=false
DISCORD_BOT_TOKEN={settings.discord_bot_token}
TELEGRAM_BOT_TOKEN={settings.telegram_bot_token}
GEMINI_API_KEY={settings.gemini_api_key}

# Gmail IMAP Settings
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
EMAIL_USER={settings.email_user}
EMAIL_PASS={settings.email_pass}

# Notion Integration Settings
NOTION_API_KEY={settings.notion_api_key}
NOTION_DEFAULT_PAGE_ID={settings.notion_default_page_id}
"""
    ENV_FILE.write_text(env_content, encoding="utf-8")
    load_dotenv(ENV_FILE, override=True)
    return {"status": "success", "message": "환경 설정이 성공적으로 저장되었습니다."}

@app.get("/api/memory")
def get_memory():
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"user_name": "User", "primary_project": "", "custom_facts": []}

@app.post("/api/memory")
def save_memory(mem: MemoryUpdate):
    data = {
        "user_name": mem.user_name,
        "primary_project": mem.primary_project,
        "custom_facts": mem.custom_facts
    }
    MEMORY_FILE.parent.mkdir(exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "success", "message": "장기 기억이 업데이트되었습니다."}

@app.get("/api/tools")
def get_tools():
    from core.tool_registry import TOOLS_SCHEMA
    return TOOLS_SCHEMA

@app.post("/api/chat")
def test_chat(req: TestChatRequest):
    try:
        from core.gemini_engine import GeminiAEAgent
        agent = GeminiAEAgent()
        reply = agent.chat(req.message, session_id="web_dashboard")
        return {"status": "success", "reply": reply}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/", response_class=HTMLResponse)
def index_page():
    html_file = Path(__file__).resolve().parent / "index.html"
    return html_file.read_text(encoding="utf-8")

def run_server(port: int = 8888):
    import uvicorn
    uvicorn.run("gateways.web_ui:app", host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    run_server()
