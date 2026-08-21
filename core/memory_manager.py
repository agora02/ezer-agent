import json
from pathlib import Path
from typing import Dict, Any, List

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
LONG_TERM_MEMORY_FILE = DATA_DIR / "long_term_memory.json"

DEFAULT_LONG_TERM_MEMORY = {
    "user_name": "최지원",
    "primary_church_app": "lign-app (/Users/jeewonchoi/Documents/antigravity/lign-app)",
    "preferences": {
        "language": "Korean (한국어)",
        "tone": "Warm, smart, capable, concise",
        "file_safety": "Move to Trash (~/.Trash) instead of permanent deletion"
    },
    "custom_facts": [
        "이룸교회 청년부 웹/앱 프로젝트(lign-app)를 주로 개발하고 있음.",
        "카메라 소니 RAW 파일 확장자는 .ARW 이며, JPG는 보존 대상임."
    ]
}

class MemoryManager:
    """Manages short-term conversation context per channel and persistent long-term knowledge."""

    def __init__(self, max_history_turns: int = 8):
        self.max_history_turns = max_history_turns
        self.short_term_sessions: Dict[str, List[Dict[str, str]]] = {}
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
        if fact not in self.long_term_memory.get("custom_facts", []):
            self.long_term_memory.setdefault("custom_facts", []).append(fact)
            self._save_long_term_memory(self.long_term_memory)

    def add_turn(self, session_id: str, role: str, content: str):
        if session_id not in self.short_term_sessions:
            self.short_term_sessions[session_id] = []
        
        self.short_term_sessions[session_id].append({"role": role, "content": content})
        
        # Keep within max sliding window
        if len(self.short_term_sessions[session_id]) > self.max_history_turns * 2:
            self.short_term_sessions[session_id] = self.short_term_sessions[session_id][-self.max_history_turns * 2:]

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self.short_term_sessions.get(session_id, [])

    def get_memory_context_prompt(self) -> str:
        """Formats long-term memory facts for injection into system prompt."""
        facts = self.long_term_memory.get("custom_facts", [])
        facts_text = "\n".join([f"- {f}" for f in facts])
        return f"""### Persistent User & Project Memory:
- User Name: {self.long_term_memory.get('user_name', '최지원')}
- Primary Project: {self.long_term_memory.get('primary_church_app')}
- Memory Facts:
{facts_text}
"""
