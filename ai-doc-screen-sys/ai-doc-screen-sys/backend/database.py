import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "daksh.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Initializes SQLite database table schema if it does not exist."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS screenings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_name TEXT NOT NULL,
                document_type TEXT NOT NULL,
                screening_date TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                ocr_score INTEGER NOT NULL,
                consistency_score INTEGER NOT NULL,
                image_quality INTEGER NOT NULL,
                tamper_signal INTEGER NOT NULL,
                status TEXT NOT NULL,
                document_id TEXT NOT NULL
            )
        """)
        connection.commit()


def save_screening(result, document_name):
    """Saves screening execution results into SQLite table."""
    with get_connection() as connection:
        status_raw = result.get("status", "review")
        status_label = status_raw.replace("_", " ").title()
        doc_id = result.get("document_id", "DEMO-000123")
        doc_type = result.get("document_type", "Synthetic Visitor Permit")
        scores = result.get("scores", {})
        tamper_flag = int(result.get("tamper_analysis", {}).get("signal_detected", False))

        connection.execute(
            """INSERT INTO screenings
            (document_name, document_type, screening_date, risk_level, ocr_score,
             consistency_score, image_quality, tamper_signal, status, document_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                document_name,
                doc_type,
                datetime.now().isoformat(timespec="seconds"),
                status_raw,
                scores.get("ocr", 90),
                scores.get("consistency", 85),
                scores.get("image_quality", 88),
                tamper_flag,
                status_label,
                doc_id
            ),
        )
        connection.commit()


def list_screenings():
    """Returns past screening runs ordered by timestamp descending."""
    with get_connection() as connection:
        cursor = connection.execute("SELECT * FROM screenings ORDER BY id DESC LIMIT 50")
        return [dict(row) for row in cursor.fetchall()]
