"""SQLite-backed storage. Designed so the access layer can swap to Postgres later
without touching callers."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    whatsapp_number TEXT UNIQUE NOT NULL,
    name TEXT,
    sex TEXT,
    age INTEGER,
    height_cm INTEGER,
    weight_kg REAL,
    activity_level TEXT,
    goal TEXT,
    target_weight_kg REAL,
    target_date TEXT,
    restrictions TEXT,
    daily_calories INTEGER,
    daily_protein_g INTEGER,
    daily_carbs_g INTEGER,
    daily_fat_g INTEGER,
    photo_consent INTEGER DEFAULT 0,
    onboarding_complete INTEGER DEFAULT 0,
    timezone TEXT DEFAULT 'Europe/Paris',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    photo_path TEXT,
    items_json TEXT NOT NULL,
    total_kcal INTEGER NOT NULL,
    total_protein_g INTEGER NOT NULL,
    total_carbs_g INTEGER NOT NULL,
    total_fat_g INTEGER NOT NULL,
    notes TEXT,
    eaten_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weight_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    weight_kg REAL NOT NULL,
    logged_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS body_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    photo_path TEXT NOT NULL,
    week_number INTEGER,
    analysis TEXT,
    captured_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    role TEXT NOT NULL,
    content_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_meals_user_eaten ON meals(user_id, eaten_at);
CREATE INDEX IF NOT EXISTS idx_messages_user_created ON messages(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_weights_user_logged ON weight_logs(user_id, logged_at);
CREATE INDEX IF NOT EXISTS idx_body_photos_user_captured ON body_photos(user_id, captured_at);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, path: Path):
        self.path = path
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    # ---------- users ----------

    def get_or_create_user(self, whatsapp_number: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE whatsapp_number = ?",
                (whatsapp_number,),
            ).fetchone()
            if row:
                return dict(row)
            ts = now_iso()
            cur = conn.execute(
                "INSERT INTO users (whatsapp_number, created_at, updated_at) VALUES (?, ?, ?)",
                (whatsapp_number, ts, ts),
            )
            return self.get_user_by_id(cur.lastrowid)

    def get_user_by_id(self, user_id: int) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return dict(row) if row else {}

    def update_user(self, user_id: int, **fields: Any) -> None:
        if not fields:
            return
        fields["updated_at"] = now_iso()
        cols = ", ".join(f"{k} = ?" for k in fields)
        with self.connect() as conn:
            conn.execute(
                f"UPDATE users SET {cols} WHERE id = ?",
                (*fields.values(), user_id),
            )

    # ---------- meals ----------

    def add_meal(
        self,
        user_id: int,
        items: list[dict[str, Any]],
        photo_path: str | None,
        notes: str | None = None,
        eaten_at: str | None = None,
    ) -> int:
        total_kcal = sum(int(i.get("kcal", 0)) for i in items)
        total_protein = sum(int(i.get("protein_g", 0)) for i in items)
        total_carbs = sum(int(i.get("carbs_g", 0)) for i in items)
        total_fat = sum(int(i.get("fat_g", 0)) for i in items)
        with self.connect() as conn:
            cur = conn.execute(
                """INSERT INTO meals
                   (user_id, photo_path, items_json, total_kcal, total_protein_g,
                    total_carbs_g, total_fat_g, notes, eaten_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    photo_path,
                    json.dumps(items, ensure_ascii=False),
                    total_kcal,
                    total_protein,
                    total_carbs,
                    total_fat,
                    notes,
                    eaten_at or now_iso(),
                ),
            )
            return cur.lastrowid

    def meals_for_day(self, user_id: int, day_iso: str) -> list[dict[str, Any]]:
        """`day_iso` is the YYYY-MM-DD prefix (UTC). Adequate for phase 1; phase 2
        will switch to user timezone."""
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM meals WHERE user_id = ? AND eaten_at LIKE ? ORDER BY eaten_at",
                (user_id, f"{day_iso}%"),
            ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["items"] = json.loads(d["items_json"])
            out.append(d)
        return out

    # ---------- weight logs ----------

    def add_weight(self, user_id: int, kg: float) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO weight_logs (user_id, weight_kg, logged_at) VALUES (?, ?, ?)",
                (user_id, kg, now_iso()),
            )

    def weights_history(self, user_id: int, limit: int = 30) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM weight_logs WHERE user_id = ? ORDER BY logged_at DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    # ---------- body photos ----------

    def add_body_photo(
        self,
        user_id: int,
        photo_path: str,
        week_number: int | None,
        analysis: str | None,
    ) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """INSERT INTO body_photos
                   (user_id, photo_path, week_number, analysis, captured_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, photo_path, week_number, analysis, now_iso()),
            )
            return cur.lastrowid

    def body_photos(self, user_id: int) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM body_photos WHERE user_id = ? ORDER BY captured_at",
                (user_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    # ---------- conversation history ----------

    def add_message(self, user_id: int, role: str, content: Any) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO messages (user_id, role, content_json, created_at) VALUES (?, ?, ?, ?)",
                (user_id, role, json.dumps(content, ensure_ascii=False), now_iso()),
            )

    def recent_messages(self, user_id: int, limit: int = 40) -> list[dict[str, Any]]:
        """Return up to `limit` most recent messages, oldest first."""
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT role, content_json FROM messages WHERE user_id = ? "
                "ORDER BY id DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        msgs = [
            {"role": r["role"], "content": json.loads(r["content_json"])}
            for r in reversed(rows)
        ]
        return msgs
