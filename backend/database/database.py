import os
import sqlite3


# ============================================================
# Database Configuration
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_NAME = os.path.join(
    BASE_DIR,
    "app.db",
)


# ============================================================
# Database Connection
# ============================================================

def get_connection():
    """
    Create and return a SQLite database connection.
    """

    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False,
    )

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# Database Initialization
# ============================================================

def init_db():
    """
    Initialize the local prototype database.

    SQLite is used for the current academic prototype.
    A production deployment can replace it with a
    production-grade database.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # ----------------------------------------------------
        # Users
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT UNIQUE
            )
            """
        )

        # ----------------------------------------------------
        # Chat Logs
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_id TEXT,
                region TEXT,
                message TEXT,
                language TEXT,
                intent TEXT,
                intent_confidence REAL,
                sentiment TEXT,
                sentiment_score REAL,
                prediction INTEGER,
                issue_type TEXT,
                network_problem INTEGER,
                notification_type TEXT,
                display_channel TEXT,
                escalation INTEGER,
                reason TEXT,
                repeat_count INTEGER,
                area_issue_count INTEGER,
                priority TEXT,
                suggested_action TEXT,
                show_to_customer INTEGER
            )
            """
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ============================================================
# Initialize Database
# ============================================================

init_db()
