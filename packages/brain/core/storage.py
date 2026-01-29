import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Optional
from .logger import setup_logger

logger = setup_logger("brain.core.storage")

DB_PATH = os.getenv("BRAIN_DB_PATH", "/app/data/brain.db")

class StorageManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_db()

    def _ensure_db_dir(self):
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError as e:
                logger.warning(f"Failed to create DB directory {directory}: {e}. Using memory DB.")
                self.db_path = ":memory:"

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        try:
            with self._get_conn() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS articles (
                        url TEXT PRIMARY KEY,
                        title TEXT,
                        source TEXT,
                        published_date TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to init DB: {e}")

    def exists(self, url: str) -> bool:
        """Check if an article URL already exists."""
        try:
            with self._get_conn() as conn:
                cursor = conn.execute("SELECT 1 FROM articles WHERE url = ?", (url,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"DB exists check failed: {e}")
            return False

    def add_article(self, url: str, title: str, source: str, published_date: str = None):
        """Add a new article record."""
        try:
            with self._get_conn() as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO articles (url, title, source, published_date) VALUES (?, ?, ?, ?)",
                    (url, title, source, published_date)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to add article: {e}")

    def prune_old_records(self, days: int = 30):
        """Remove records older than N days."""
        try:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            with self._get_conn() as conn:
                conn.execute("DELETE FROM articles WHERE created_at < ?", (cutoff,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to prune DB: {e}")

# Singleton
storage = StorageManager()
