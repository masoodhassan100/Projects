"""
SQLite persistence layer for Expense Manager.

Keeps all raw SQL in one place so the rest of the app works with
plain Python objects (see models.py) instead of hand-rolled queries.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB_PATH = Path.home() / ".expense_manager" / "expenses.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    amount      REAL NOT NULL CHECK (amount > 0),
    category    TEXT NOT NULL,
    description TEXT DEFAULT '',
    date        TEXT NOT NULL,          -- ISO format YYYY-MM-DD
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);

CREATE TABLE IF NOT EXISTS budgets (
    category TEXT PRIMARY KEY,
    monthly_limit REAL NOT NULL CHECK (monthly_limit >= 0)
);
"""


class Database:
    """Thin wrapper around a SQLite connection with schema management."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
