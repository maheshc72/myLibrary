from contextlib import closing

from db import get_connection


def add_book(title: str, author: str, publication_year: int | None = None) -> int:
    with get_connection() as con:
        cursor = con.execute(
            "INSERT INTO Books (title, author, publication_year) VALUES (?, ?, ?)",
            (title, author, publication_year),
        )
        return cursor.lastrowid


def get_all_books() -> list[tuple]:
    with closing(get_connection()) as con:
        return con.execute(
            "SELECT book_id, title, author, publication_year FROM Books ORDER BY book_id"
        ).fetchall()


def get_available_books() -> list[tuple]:
    """Return books not currently borrowed by anyone."""
    with closing(get_connection()) as con:
        return con.execute("""
            SELECT b.book_id, b.title, b.author, b.publication_year
            FROM Books b
            WHERE b.book_id NOT IN (
                SELECT book_id FROM Borrowings WHERE return_date IS NULL
            )
            ORDER BY b.title
        """).fetchall()


def delete_book(book_id: int) -> None:
    with get_connection() as con:
        # Check if the book is currently borrowed
        active = con.execute(
            "SELECT COUNT(*) FROM Borrowings WHERE book_id = ? AND return_date IS NULL",
            (book_id,)
        ).fetchone()[0]

        if active > 0:
            raise ValueError("Cannot delete book: It is currently borrowed.")

        cursor = con.execute("DELETE FROM Books WHERE book_id = ?", (book_id,))
        if cursor.rowcount == 0:
            raise ValueError(f"No book found with ID {book_id}.")


def update_book(book_id: int, title: str, author: str, publication_year: int | None = None) -> None:
    with get_connection() as con:
        cursor = con.execute(
            "UPDATE Books SET title = ?, author = ?, publication_year = ? WHERE book_id = ?",
            (title, author, publication_year, book_id),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"No book found with ID {book_id}.")
