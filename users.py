from contextlib import closing

from db import get_connection


def add_user(username: str, email: str) -> int:
    with get_connection() as con:
        cursor = con.execute(
            "INSERT INTO Users (username, email) VALUES (?, ?)",
            (username, email),
        )
        return cursor.lastrowid


def get_all_users() -> list[tuple]:
    with closing(get_connection()) as con:
        return con.execute("SELECT user_id, username, email FROM Users").fetchall()

def update_user(user_id: int, username: str, email: str) -> None:
    """Update username or email for an existing user."""
    with get_connection() as con:
        cursor = con.execute(
            "UPDATE Users SET username = ?, email = ? WHERE user_id = ?",
            (username, email, user_id),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"No user found with ID {user_id}.")


def delete_user(user_id: int) -> None:
    with get_connection() as con:
        active = con.execute(
            "SELECT COUNT(*) FROM Borrowings WHERE user_id = ? AND return_date IS NULL",
            (user_id,)
        ).fetchone()[0]

        if active > 0:
            raise ValueError("Cannot delete user: They currently have borrowed books.")

        cursor = con.execute("DELETE FROM Users WHERE user_id = ?", (user_id,))
        if cursor.rowcount == 0:
            raise ValueError(f"No user found with ID {user_id}.")


def seed_users() -> None:
    with get_connection() as con:
        if con.execute("SELECT COUNT(*) FROM Users").fetchone()[0] == 0:
            con.execute(
                "INSERT INTO Users (username, email) VALUES (?, ?)",
                ("alice", "alice@example.com"),
            )
