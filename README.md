# myLibrary v1

A command-line library management system built with Python and SQLite.

## Prerequisites

- **Python 3.10+**
- **SQLite 3** (usually pre-installed with Python)

## Features

### Book Management
- **Add books** — Add new books to the catalog with title, author, and optional publication year
- **View all books** — List every book in the catalog with ID, title, author, and year
- **Update books** — Edit any field of an existing book (title, author, publication year)
- **Delete books** — Remove a book from the catalog; deletion is blocked if the book is currently borrowed

### User Management
- **Create users** — Register new users with a unique username and email
- **View all users** — List all registered users with their IDs and emails
- **Delete users** — Remove a user; deletion is blocked if they have any active borrowings
- **User login** — Select a user by ID to access their personal borrowing menu

### Borrowing System
- **Browse available books** — Users see only books that are not currently borrowed by anyone
- **Borrow a book** — Check out a book; the borrow date is recorded automatically
- **View borrowed books** — Users can see all books they currently have checked out, with borrow dates
- **Return a book** — Mark a book as returned and record the return date

### Fine Calculation
- Books returned within the **5-day free period** incur no charge
- Returns after 5 days are charged **Rs. 1 per day** for each day over the limit
- The fine amount is displayed at the time of return

## Tech Stack

- **Language:** Python 3.10+
- **Database:** SQLite 3 (via `sqlite3` standard library)
- **Interface:** Interactive CLI (terminal menus)

## Project Structure

| File | Purpose |
|---|---|
| `cli.py` | Entry point; all interactive menus |
| `books.py` | Book CRUD operations |
| `users.py` | User CRUD operations |
| `borrowings.py` | Borrow, return, and fine logic |
| `db.py` | Database connection and schema migration |
| `config.py` | Configurable constants (`BORROW_LIMIT_DAYS`, `FINE_PER_DAY`, `DB_NAME`) |
| `schema.sql` | SQLite table definitions (`Users`, `Books`, `Borrowings`) |

## Database Schema

- **Users** — `user_id`, `username` (unique), `email` (unique)
- **Books** — `book_id`, `title`, `author`, `publication_year`
- **Borrowings** — `borrowing_id`, `book_id`, `user_id`, `borrow_date`, `return_date`

Foreign key constraints are enforced; deleting a user or book cascades to related borrowing records.

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd myLibrary_v1
   ```
2. **Run the application:**
```bash
python cli.py
```

## Configuration

Edit `config.py` to change default behaviour:

```python
DB_NAME = "library.db"      # SQLite database file
BORROW_LIMIT_DAYS = 5       # Days before fines begin
FINE_PER_DAY = 1            # Fine in Rupees per overdue day
```
