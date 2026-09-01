import json
import re
from pathlib import Path
from typing import Dict, Any, List
from core.sqlite_store import db_store

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
LONG_TERM_MEMORY_FILE = DATA_DIR / "long_term_memory.json"

DEFAULT_LONG_TERM_MEMORY = {
    "user_name": "User",
    "primary_project": "Default Project",
    "preferences": {
        "language": "Korean (한국어)",
        "tone": "Warm, smart, capable, concise",
        "file_safety": "Move to Trash (~/.Trash) instead of permanent deletion"
    },
    "custom_facts": [
        "자율 AI 에이전트 Ezer Agent가 시스템을 관리함."
    ]
}

def mask_sensitive_credentials(text: str) -> str:
    """OpenClaw 2.0 Credential Shielding: Masks API keys, tokens, and secrets from prompt & logging."""
    if not isinstance(text, str):
        return text
    # Mask OpenAI / Gemini / Discord / Notion keys
    text = re.sub(r'(AIzaSy[A-Za-z0-9_-]{33})', r'AIzaSy***[MASKED]***', text)
    text = re.sub(r'(secret_[A-Za-z0-9]{32,})', r'secret_***[MASKED]***', text)
    text = re.sub(r'(ghp_[A-Za-z0-9]{36})', r'ghp_***[MASKED]***', text)
    text = re.sub(r'([A-Za-z0-9_-]{24}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27,})', r'***[DISCORD_TOKEN_MASKED]***', text)
    return text

class MemoryManager:
    """Manages SQLite-backed fast sliding context and persistent long-term knowledge."""

    def __init__(self, max_history_turns: int = 8):
        self.max_history_turns = max_history_turns
        self.db = db_store
        self.long_term_memory = self._load_long_term_memory()

    def _load_long_term_memory(self) -> Dict[str, Any]:
        if not LONG_TERM_MEMORY_FILE.exists():
            self._save_long_term_memory(DEFAULT_LONG_TERM_MEMORY)
            return DEFAULT_LONG_TERM_MEMORY
        try:
            return json.loads(LONG_TERM_MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return DEFAULT_LONG_TERM_MEMORY

    def _save_long_term_memory(self, data: Dict[str, Any]):
        try:
            LONG_TERM_MEMORY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[MemoryManager] Failed to save long-term memory: {e}")

    def add_fact(self, fact: str):
        fact_clean = mask_sensitive_credentials(fact)
        if fact_clean not in self.long_term_memory.get("custom_facts", []):
            self.long_term_memory.setdefault("custom_facts", []).append(fact_clean)
            self._save_long_term_memory(self.long_term_memory)
        # Also persist to SQLite
        self.db.add_insight(fact_clean, category="user_preference")

    def add_turn(self, session_id: str, role: str, content: str):
        content_clean = mask_sensitive_credentials(content)
        self.db.add_message(session_id, role, content_clean)

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self.db.get_messages(session_id, limit=self.max_history_turns * 2)

    def get_memory_context_prompt(self) -> str:
        """Formats long-term memory facts for injection into system prompt."""
        facts = self.long_term_memory.get("custom_facts", [])
        sqlite_insights = self.db.get_insights(limit=10)
        
        all_unique_facts = list(dict.fromkeys(facts + sqlite_insights))
        facts_text = "\n".join([f"- {f}" for f in all_unique_facts])
        return f"""### Persistent User & Project Memory:
- User Name: {self.long_term_memory.get('user_name', 'User')}
- Primary Project: {self.long_term_memory.get('primary_project', 'Default Project')}
- Memory Facts & Self-Learned Insights:
{facts_text}
"""
