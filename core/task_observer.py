import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from core.sqlite_store import db_store

OBSERVER_DIR = Path(__file__).resolve().parent.parent / "data" / "observer"
OBSERVER_DIR.mkdir(parents=True, exist_ok=True)

class TaskObserver:
    """Task Observer Engine (inspired by rebelytics/one-skill-to-rule-them-all, Pattern B).
    Passively observes user corrections and repetitive task patterns in the background.
    Triggers a polite, single-line skill creation/improvement suggestion only when a pattern reaches threshold (e.g. 3 times).
    """

    def __init__(self, threshold: int = 3):
        self.threshold = threshold
        self._init_observer_table()

    def _init_observer_table(self):
        with db_store._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_key TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL, -- 'correction', 'new_skill_candidate', 'preference'
                    summary TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    suggested_action TEXT NOT NULL,
                    is_resolved INTEGER DEFAULT 0,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def record_observation(self, pattern_key: str, category: str, summary: str, suggested_action: str) -> Optional[str]:
        """Records an observation. If frequency reaches threshold and is not resolved, returns a suggestion prompt to append."""
        with db_store._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT frequency, is_resolved FROM task_observations WHERE pattern_key = ?", (pattern_key,))
            row = cursor.fetchone()

            if row:
                freq = row["frequency"] + 1
                is_resolved = row["is_resolved"]
                conn.execute("""
                    UPDATE task_observations
                    SET frequency = ?, summary = ?, suggested_action = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE pattern_key = ?
                """, (freq, summary, suggested_action, pattern_key))
                conn.commit()

                # Trigger suggestion when hitting the threshold
                if freq == self.threshold and not is_resolved:
                    return f"\n\n💡 **[Ezer 스킬 자율 진화 제안]** 최근 유사한 피드백/패턴이 {freq}회 감지되었습니다.\n👉 *{summary}*\n이 규칙을 기본 스킬 동작으로 영구 반영하거나 자동화 스킬로 등록할까요? ('응 해줘'라고 답하시면 즉시 적용됩니다)"
            else:
                conn.execute("""
                    INSERT INTO task_observations (pattern_key, category, summary, frequency, suggested_action)
                    VALUES (?, ?, ?, 1, ?)
                """, (pattern_key, category, summary, suggested_action))
                conn.commit()

        return None

    def mark_resolved(self, pattern_key: str):
        with db_store._get_conn() as conn:
            conn.execute("UPDATE task_observations SET is_resolved = 1 WHERE pattern_key = ?", (pattern_key,))
            conn.commit()

    def get_pending_suggestions(self) -> List[Dict[str, Any]]:
        with db_store._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pattern_key, category, summary, frequency, suggested_action
                FROM task_observations
                WHERE frequency >= ? AND is_resolved = 0
                ORDER BY frequency DESC
            """, (self.threshold,))
            return [dict(r) for r in cursor.fetchall()]

# Global Singleton
task_observer = TaskObserver(threshold=3)
