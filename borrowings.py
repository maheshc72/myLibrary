import sqlite3
from contextlib import closing
from datetime import date

from config import BORROW_LIMIT_DAYS, FINE_PER_DAY, MAX_BORROWS
from db import get_connection


def borrow_book(book_id: int, user_id: int) -> None:
    with get_connection() as con:
        count = con.execute(
            "SELECT COUNT(*) FROM Borrowings WHERE user_id = ? AND return_date IS NULL",
            (user_id,)
        ).fetchone()[0]
        if count >= MAX_BORROWS:
            raise ValueError(f"Maximum concurrent borrow limit ({MAX_BORROWS}) reached.")

        row = con.execute(
            """SELECT copies - COALESCE(
                   (SELECT COUNT(*) FROM Borrowings WHERE book_id = ? AND return_date IS NULL), 0
               ) FROM Books WHERE book_id = ?""",
            (book_id, book_id)
        ).fetchone()
        if row is None:
            raise ValueError("Book not found.")
        if row[0] <= 0:
            raise ValueError("No copies of this book are currently available.")

        con.execute(
            "INSERT INTO Borrowings (book_id, user_id, borrow_date) VALUES (?, ?, CURRENT_DATE)",
            (book_id, user_id),
        )


def return_book(book_id: int, user_id: int) -> tuple[str, int]:
    """Mark a book returned. Persists the fine. Returns (borrow_date_str, fine_in_rupees)."""
    today = date.today()
    with get_connection() as con:
        row = con.execute("""
            SELECT borrowing_id, borrow_date FROM Borrowings
            WHERE book_id = ? AND user_id = ? AND return_date IS NULL
        """, (book_id, user_id)).fetchone()
        if row is None:
            raise ValueError("No active borrowing found for this book.")
        borrowing_id, borrow_date_str = row
        # Slice to [:10] to extract 'YYYY-MM-DD' even if a full timestamp is present.
        days_borrowed = (today - date.fromisoformat(borrow_date_str[:10])).days
        fine = max(0, (days_borrowed - BORROW_LIMIT_DAYS) * FINE_PER_DAY)
        con.execute(
            "UPDATE Borrowings SET return_date = ?, fine = ? WHERE borrowing_id = ?",
            (today.isoformat(), fine if fine > 0 else None, borrowing_id),
        )
        return borrow_date_str, fine


def get_borrowed_books(user_id: int) -> list[tuple]:
    """Return books currently borrowed by the given user."""
    with closing(get_connection()) as con:
        return con.execute("""
            SELECT b.book_id, b.title, b.author, b.publication_year, br.borrow_date
            FROM Books b
            JOIN Borrowings br ON b.book_id = br.book_id
            WHERE br.user_id = ? AND br.return_date IS NULL
            ORDER BY br.borrow_date DESC
        """, (user_id,)).fetchall()


def get_borrowing_history(user_id: int) -> list[tuple]:
    """Return all past (returned) borrowings for a user, including persisted fines."""
    with closing(get_connection()) as con:
        return con.execute("""
            SELECT b.title, b.author, br.borrow_date, br.return_date, COALESCE(br.fine, 0)
            FROM Books b
            JOIN Borrowings br ON b.book_id = br.book_id
            WHERE br.user_id = ? AND br.return_date IS NOT NULL
            ORDER BY br.return_date DESC
        """, (user_id,)).fetchall()


def get_all_active_borrowings() -> list[tuple]:
    """Admin view: all books currently borrowed by anyone."""
    with closing(get_connection()) as con:
        return con.execute("""
            SELECT u.username, b.title, br.borrow_date
            FROM Borrowings br
            JOIN Users u ON br.user_id = u.user_id
            JOIN Books b ON br.book_id = b.book_id
            WHERE br.return_date IS NULL
            ORDER BY br.borrow_date ASC
        """).fetchall()


def get_overdue_report() -> list[tuple]:
    """List books borrowed longer than BORROW_LIMIT_DAYS."""
    with closing(get_connection()) as con:
        return con.execute("""
            SELECT u.username, b.title, br.borrow_date,
                   CAST(julianday('now') - julianday(br.borrow_date) AS INTEGER) AS days
            FROM Borrowings br
            JOIN Users u ON br.user_id = u.user_id
            JOIN Books b ON br.book_id = b.book_id
            WHERE br.return_date IS NULL
              AND (julianday('now') - julianday(br.borrow_date)) > ?
            ORDER BY days DESC
        """, (BORROW_LIMIT_DAYS,)).fetchall()


# ──────────────────────────── reservations ────────────────────────────

def add_reservation(book_id: int, user_id: int) -> None:
    with get_connection() as con:
        already_borrowed = con.execute(
            "SELECT COUNT(*) FROM Borrowings WHERE book_id = ? AND user_id = ? AND return_date IS NULL",
            (book_id, user_id)
        ).fetchone()[0]
        if already_borrowed > 0:
            raise ValueError("You already have this book borrowed.")
        try:
            con.execute(
                "INSERT INTO Reservations (book_id, user_id) VALUES (?, ?)",
                (book_id, user_id),
            )
        except sqlite3.IntegrityError:
            raise ValueError("You already have a reservation for this book.")


def cancel_reservation(book_id: int, user_id: int) -> None:
    with get_connection() as con:
        cursor = con.execute(
            "DELETE FROM Reservations WHERE book_id = ? AND user_id = ?",
            (book_id, user_id),
        )
        if cursor.rowcount == 0:
            raise ValueError("No reservation found for this book.")


def get_user_reservations(user_id: int) -> list[tuple]:
    with closing(get_connection()) as con:
        return con.execute("""
            SELECT b.book_id, b.title, b.author, r.reserved_at
            FROM Reservations r
            JOIN Books b ON r.book_id = b.book_id
            WHERE r.user_id = ?
            ORDER BY r.reserved_at ASC
        """, (user_id,)).fetchall()


def get_all_reservations() -> list[tuple]:
    """Admin view: all pending reservations."""
    with closing(get_connection()) as con:
        return con.execute("""
            SELECT u.username, b.title, r.reserved_at
            FROM Reservations r
            JOIN Users u ON r.user_id = u.user_id
            JOIN Books b ON r.book_id = b.book_id
            ORDER BY r.reserved_at ASC
        """).fetchall()


def get_book_reservation_count(book_id: int) -> int:
    with closing(get_connection()) as con:
        return con.execute(
            "SELECT COUNT(*) FROM Reservations WHERE book_id = ?", (book_id,)
        ).fetchone()[0]
