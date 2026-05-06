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
    user_id          INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);
