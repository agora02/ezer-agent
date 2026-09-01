import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "ezer_store.db"

class SQLiteStore:
    """OpenClaw 2.0-inspired high-speed SQLite storage for sessions, memories, and transactions."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # 1. Sessions & Messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_messages(session_id)")

            # 2. Long Term Memory & Insights (Hermes Evolution)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    insight TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 3. Accounting Transactions (OpenAccountant)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounting_transactions (
                    id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    type TEXT NOT NULL,
                    account TEXT DEFAULT '주계좌',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 4. Settings Key-Value Store
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            conn.commit()

    # --- Chat Messages ---
    def add_message(self, session_id: str, role: str, content: str):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content)
            )
            conn.commit()

    def get_messages(self, session_id: str, limit: int = 12) -> List[Dict[str, str]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

    def list_sessions(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, count(*) as msg_count, max(timestamp) as last_active
                FROM chat_messages
                GROUP BY session_id
                ORDER BY last_active DESC
            """)
            return [dict(r) for r in cursor.fetchall()]

    # --- Memory & Insights ---
    def add_insight(self, insight: str, session_id: str = "default", category: str = "learned_fact"):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO memory_insights (session_id, insight, category) VALUES (?, ?, ?)",
                (session_id, insight, category)
            )
            conn.commit()

    def get_insights(self, limit: int = 20) -> List[str]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT insight FROM memory_insights ORDER BY id DESC LIMIT ?", (limit,))
            return [r["insight"] for r in cursor.fetchall()]

    # --- Accounting Transactions ---
    def add_transaction(self, tx_id: str, date: str, description: str, amount: float, category: str, t_type: str, account: str = "주계좌"):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO accounting_transactions (id, date, description, amount, category, type, account)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tx_id, date, description, amount, category, t_type.lower(), account))
            conn.commit()

    def get_transactions(self, start_date: Optional[str] = None, end_date: Optional[str] = None, category: Optional[str] = None, t_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        query = "SELECT * FROM accounting_transactions WHERE 1=1"
        params = []
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if category:
            query += " AND category LIKE ?"
            params.append(f"%{category}%")
        if t_type:
            query += " AND type = ?"
            params.append(t_type.lower())
        query += " ORDER BY date DESC, id DESC LIMIT ?"
        params.append(limit)

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]

# Global Singleton Store
db_store = SQLiteStore()
