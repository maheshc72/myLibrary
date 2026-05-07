from contextlib import closing
from datetime import date

from config import BORROW_LIMIT_DAYS, FINE_PER_DAY
from db import get_connection


def borrow_book(book_id: int, user_id: int) -> None:
    with get_connection() as con:
        con.execute(
            "INSERT INTO Borrowings (book_id, user_id, borrow_date) VALUES (?, ?, CURRENT_DATE)",
            (book_id, user_id),
        )


def return_book(book_id: int, user_id: int) -> tuple[str, int]:
    """Mark a book returned. Returns (borrow_date_str, fine_in_rupees)."""
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
            "UPDATE Borrowings SET return_date = ? WHERE borrowing_id = ?",
            (today.isoformat(), borrowing_id),
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
