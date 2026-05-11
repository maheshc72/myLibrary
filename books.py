from contextlib import closing

from db import get_connection


def add_book(title: str, author: str, publication_year: int | None = None,
             isbn: str | None = None, genre: str | None = None, copies: int = 1) -> int:
    with get_connection() as con:
        cursor = con.execute(
            "INSERT INTO Books (title, author, publication_year, isbn, genre, copies) VALUES (?, ?, ?, ?, ?, ?)",
            (title, author, publication_year, isbn or None, genre or None, copies),
        )
        return cursor.lastrowid


def get_all_books() -> list[tuple]:
    with closing(get_connection()) as con:
        return con.execute(
            "SELECT book_id, title, author, publication_year, isbn, genre, copies FROM Books ORDER BY book_id"
        ).fetchall()


def get_available_books() -> list[tuple]:
    """Return books with at least one copy not currently borrowed. Includes available count."""
    with closing(get_connection()) as con:
        return con.execute("""
            SELECT b.book_id, b.title, b.author, b.publication_year, b.isbn, b.genre, b.copies,
                   b.copies - COALESCE(
                       (SELECT COUNT(*) FROM Borrowings WHERE book_id = b.book_id AND return_date IS NULL), 0
                   ) AS available
            FROM Books b
            WHERE b.copies > COALESCE(
                (SELECT COUNT(*) FROM Borrowings WHERE book_id = b.book_id AND return_date IS NULL), 0
            )
            ORDER BY b.title
        """).fetchall()


def get_unavailable_books() -> list[tuple]:
    """Return books where all copies are currently borrowed."""
    with closing(get_connection()) as con:
        return con.execute("""
            SELECT b.book_id, b.title, b.author, b.publication_year, b.isbn, b.genre, b.copies
            FROM Books b
            WHERE b.copies <= COALESCE(
                (SELECT COUNT(*) FROM Borrowings WHERE book_id = b.book_id AND return_date IS NULL), 0
            )
            ORDER BY b.title
        """).fetchall()


def search_books(query: str) -> list[tuple]:
    """Search books by title, author, publication year, genre, or ISBN."""
    with closing(get_connection()) as con:
        like = f"%{query}%"
        return con.execute("""
            SELECT book_id, title, author, publication_year, isbn, genre, copies
            FROM Books
            WHERE title LIKE ? OR author LIKE ? OR CAST(publication_year AS TEXT) LIKE ?
               OR genre LIKE ? OR isbn LIKE ?
            ORDER BY title
        """, (like, like, like, like, like)).fetchall()


def delete_book(book_id: int) -> None:
    with get_connection() as con:
        active = con.execute(
            "SELECT COUNT(*) FROM Borrowings WHERE book_id = ? AND return_date IS NULL",
            (book_id,)
        ).fetchone()[0]
        if active > 0:
            raise ValueError("Cannot delete book: It is currently borrowed.")
        cursor = con.execute("DELETE FROM Books WHERE book_id = ?", (book_id,))
        if cursor.rowcount == 0:
            raise ValueError(f"No book found with ID {book_id}.")


def update_book(book_id: int, title: str, author: str, publication_year: int | None = None,
                isbn: str | None = None, genre: str | None = None, copies: int = 1) -> None:
    with get_connection() as con:
        cursor = con.execute(
            "UPDATE Books SET title=?, author=?, publication_year=?, isbn=?, genre=?, copies=? WHERE book_id=?",
            (title, author, publication_year, isbn or None, genre or None, copies, book_id),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"No book found with ID {book_id}.")
