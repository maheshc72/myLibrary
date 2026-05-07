import sqlite3
from pathlib import Path


def init_db() -> None:
    """Create tables from schema.sql if they don't exist yet."""
    schema = Path(__file__).with_name("schema.sql").read_text()
    with sqlite3.connect("library.db") as con:
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript(schema)


def seed_users() -> None:
    """Insert a default user if the Users table is empty. Runs once at startup."""
    with sqlite3.connect("library.db") as con:
        con.execute("PRAGMA foreign_keys = ON")
        row = con.execute("SELECT COUNT(*) FROM Users").fetchone()
        if row[0] == 0:
            con.execute(
                "INSERT INTO Users (username, email) VALUES (?, ?)",
                ("alice", "alice@example.com"),
            )


def add_user(username: str, email: str) -> int:
    """Insert a new user and return their user_id."""
    with sqlite3.connect("library.db") as con:
        con.execute("PRAGMA foreign_keys = ON")
        cursor = con.execute(
            "INSERT INTO Users (username, email) VALUES (?, ?)",
            (username, email),
        )
        return cursor.lastrowid


def get_all_users() -> list[tuple]:
    """Return all registered users."""
    with sqlite3.connect("library.db") as con:
        return con.execute("SELECT user_id, username, email FROM Users").fetchall()


def add_book(title: str, author: str, user_id: int, publication_year: int | None = None) -> int:
    """Insert a book and return its generated book_id."""
    with sqlite3.connect("library.db") as con:
        con.execute("PRAGMA foreign_keys = ON")
        cursor = con.execute(
            "INSERT INTO Books (title, author, publication_year, user_id) VALUES (?, ?, ?, ?)",
            (title, author, publication_year, user_id),
        )
        return cursor.lastrowid


def get_books_for_user(user_id: int) -> list[tuple]:
    """Return all books tracked by the given user via a JOIN query."""
    with sqlite3.connect("library.db") as con:
        con.execute("PRAGMA foreign_keys = ON")
        return con.execute(
            """
            SELECT b.book_id, b.title, b.author, b.publication_year
            FROM Books b
            JOIN Users u ON b.user_id = u.user_id
            WHERE u.user_id = ?
            """,
            (user_id,),
        ).fetchall()


def menu(user_id: int) -> None:
    while True:
        print("\n1. Add a book")
        print("2. Display my books")
        print("0. Exit")
        choice = input("Choice: ").strip()

        if choice == "1":
            title = input("Title: ").strip()
            author = input("Author: ").strip()
            year_raw = input("Publication year (leave blank if unknown): ").strip()
            year = int(year_raw) if year_raw.isdigit() else None
            try:
                book_id = add_book(title, author, user_id, year)
                print(f"Added book with book_id={book_id}")
            except sqlite3.IntegrityError as e:
                print(f"Error: {e}")

        elif choice == "2":
            books = get_books_for_user(user_id)
            if not books:
                print("No books tracked yet.")
            else:
                print(f"\n{'ID':<6} {'Title':<35} {'Author':<25} {'Year'}")
                print("-" * 75)
                for book_id, title, author, year in books:
                    print(f"{book_id:<6} {title:<35} {author:<25} {year or '—'}")

        elif choice == "0":
            break
        else:
            print("Invalid choice, please enter 0, 1, or 2.")


def main_menu() -> None:
    """Top-level menu to manage or select users."""
    while True:
        print("\n=== Library System ===")
        print("1. Select User (Login)")
        print("2. Create New User")
        print("0. Exit")
        choice = input("Choice: ").strip()

        if choice == "1":
            users = get_all_users()
            if not users:
                print("No users found. Please create one first.")
                continue
            
            print(f"\n{'ID':<5} {'Username':<20} {'Email'}")
            print("-" * 45)
            for uid, name, email in users:
                print(f"{uid:<5} {name:<20} {email}")
            
            try:
                user_id = int(input("\nEnter User ID to manage books: ").strip())
                # Basic validation check
                if any(u[0] == user_id for u in users):
                    menu(user_id)
                else:
                    print("Invalid User ID.")
            except ValueError:
                print("Please enter a valid numeric ID.")

        elif choice == "2":
            username = input("Enter username: ").strip()
            email = input("Enter email: ").strip()
            try:
                new_id = add_user(username, email)
                print(f"User created successfully with ID: {new_id}")
            except sqlite3.IntegrityError:
                print("Error: Username or Email already exists.")

        elif choice == "0":
            break

if __name__ == "__main__":
    init_db()
    seed_users()
    main_menu()
