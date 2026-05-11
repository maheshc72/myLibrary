CREATE TABLE IF NOT EXISTS Users (
    user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT    NOT NULL UNIQUE,
    email     TEXT    NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Books (
    book_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT    NOT NULL,
    author           TEXT    NOT NULL,
    publication_year INTEGER,
    isbn             TEXT    UNIQUE,
    genre            TEXT,
    copies           INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS Borrowings (
    borrowing_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id       INTEGER NOT NULL,
    user_id       INTEGER NOT NULL,
    borrow_date   DATE    NOT NULL DEFAULT CURRENT_DATE,
    return_date   DATE,
    fine          REAL,
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Reservations (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id        INTEGER NOT NULL,
    user_id        INTEGER NOT NULL,
    reserved_at    DATE    NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    UNIQUE (book_id, user_id)
);
