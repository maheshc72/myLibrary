import sqlite3
from pathlib import Path

from config import DB_NAME


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    schema = Path(__file__).with_name("schema.sql").read_text()
    with get_connection() as con:
        columns = [col[1] for col in con.execute("PRAGMA table_info(Books)").fetchall()]

        if columns and "user_id" in columns:
            # Migrate from old schema where Books owned a user_id directly.
            con.execute("PRAGMA foreign_keys = OFF")
            con.execute("ALTER TABLE Books RENAME TO Books_old")
            con.executescript(schema)
            con.execute("""
                INSERT INTO Books (book_id, title, author, publication_year)
                SELECT book_id, title, author, publication_year FROM Books_old
            """)
            old_cols = [col[1] for col in con.execute("PRAGMA table_info(Books_old)").fetchall()]
            date_expr = "date_added" if "date_added" in old_cols else "CURRENT_DATE"
            con.execute(f"""
                INSERT INTO Borrowings (book_id, user_id, borrow_date)
                SELECT book_id, user_id, COALESCE({date_expr}, CURRENT_DATE)
                FROM Books_old
                WHERE user_id IS NOT NULL
            """)
            con.execute("DROP TABLE Books_old")
            con.execute("PRAGMA foreign_keys = ON")
        else:
            con.executescript(schema)
