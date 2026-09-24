import sqlite3

DATABASE_NAME = "daksh.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT UNIQUE NOT NULL,
            document_type TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_case(case_id, document_type, status, result):
    connection = get_connection()

    connection.execute("""
        INSERT OR REPLACE INTO cases
        (case_id, document_type, status, result)
        VALUES (?, ?, ?, ?)
    """, (
        case_id,
        document_type,
        status,
        result
    ))

    connection.commit()
    connection.close()


def get_case(case_id):
    connection = get_connection()

    case = connection.execute("""
        SELECT * FROM cases
        WHERE case_id = ?
    """, (case_id,)).fetchone()

    connection.close()

    return case
    