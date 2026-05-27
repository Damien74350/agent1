"""Conversation history storage (SQLite).

Messages stay local to keep per-turn latency low; everything else (profile,
meals, weights, photos, knowledge, foods) lives in Airtable.
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id, id);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class MessageStore:
    def __init__(self, path: Path):
        self.path = path
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path, isolation_level=None)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def add(self, user_id: str, role: str, content: Any) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO messages (user_id, role, content_json, created_at) "
                "VALUES (?, ?, ?, ?)",
                (user_id, role, json.dumps(content, ensure_ascii=False), now_iso()),
            )

    def recent(self, user_id: str, limit: int = 40) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT role, content_json FROM messages WHERE user_id = ? "
                "ORDER BY id DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        return [
            {"role": r["role"], "content": json.loads(r["content_json"])}
            for r in reversed(rows)
        ]

    def clear(self, user_id: str) -> int:
        with self.connect() as conn:
            cur = conn.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
            return cur.rowcount
