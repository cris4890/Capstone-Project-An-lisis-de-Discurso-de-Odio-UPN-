"""Historial local de inferencias; independiente del corpus y las anotaciones."""
from contextlib import closing, contextmanager
from datetime import datetime, timezone
import math
import os
from pathlib import Path
import sqlite3
import uuid

import pandas as pd
from data_pipeline import clean_and_anonymize


def history_path():
    return Path(os.environ.get("CAPSTONE_HISTORY_DB", str(Path(__file__).resolve().parent / "private" / "history.sqlite3")))


class HistoryStore:
    def __init__(self, path):
        self.path = Path(path)

    @contextmanager
    def connect(self):
        with closing(sqlite3.connect(self.path)) as conn:
            with conn:
                yield conn

    def add(self, text, prediction, model_name, run_id, latency_ms, confidence=None):
        text = clean_and_anonymize(text)
        if not text or prediction not in {"Odio", "Ofensivo", "Neutro"}:
            raise ValueError("Texto o categoría inválidos.")
        if not model_name or not run_id or not math.isfinite(latency_ms) or latency_ms < 0:
            raise ValueError("Metadatos inválidos.")
        if confidence is not None and (not math.isfinite(confidence) or not 0 <= confidence <= 1):
            raise ValueError("Probabilidad inválida.")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        record_id = str(uuid.uuid4())
        with self.connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS classifications (
                id TEXT PRIMARY KEY, created_at TEXT NOT NULL, text TEXT NOT NULL,
                prediction TEXT NOT NULL, model_name TEXT NOT NULL, run_id TEXT NOT NULL,
                latency_ms REAL NOT NULL, confidence REAL)""")
            conn.execute("INSERT INTO classifications VALUES (?,?,?,?,?,?,?,?)", (
                record_id, datetime.now(timezone.utc).isoformat(), text, prediction,
                model_name, run_id, float(latency_ms), confidence))
        return record_id

    def read(self):
        if not self.path.exists():
            return pd.DataFrame()
        with self.connect() as conn:
            exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='classifications'").fetchone()
            if not exists:
                return pd.DataFrame()
            return pd.read_sql_query("SELECT * FROM classifications ORDER BY created_at DESC, id DESC",conn)
