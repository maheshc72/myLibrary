# myLibrary v3

A command-line library management system built with Python and SQLite.

## Prerequisites

- **Python 3.10+**
- **SQLite 3** (usually pre-installed with Python)

## Features

### Book Management
- **Add books** — Add new books with title, author, year, ISBN, genre, and copy count
- **View all books** — List every book with all fields including available copies
- **Update books** — Edit any field of an existing book
- **Delete books** — Remove a book; deletion is blocked if any copy is currently borrowed

### User Management
- **Create users** — Register new users with a unique username and email
- **View all users** — List all registered users with their IDs and emails
- **Delete users** — Remove a user; deletion is blocked if they have any active borrowings
- **User login** — Select a user by ID to access their personal borrowing menu

### Borrowing System
- **Browse available books** — Users see books with available copies, showing available/total count
- **Borrow a book** — Check out a book; the borrow date is recorded automatically
- **View borrowed books** — Users can see all books they currently have checked out, with borrow dates
- **Return a book** — Mark a book as returned; fine is calculated and persisted to the database
- **Reserve a book** — Hold a book that is fully borrowed; see queue size per title
- **Cancel reservation** — Remove a pending reservation

### Fine Calculation
- Books returned within the **5-day free period** incur no charge
- Returns after 5 days are charged **Rs. 1 per day** for each day over the limit
- The fine amount is displayed at the time of return

### Access Control
- **Member login** — Select a registered user to access their personal borrowing menu
- **Admin login** — Password-protected admin menu for catalog and user management (default: `admin123`)
- **Pagination** — All catalog and user lists page in groups of 10 (configurable via `PAGE_SIZE`)

## Tech Stack

- **Language:** Python 3.10+
- **Database:** SQLite 3 (via `sqlite3` standard library)
- **Interface:** Interactive CLI (terminal menus)

## Project Structure

| File | Purpose |
|---|---|
| `cli.py` | Entry point; landing, admin, and member menus |
| `books.py` | Book CRUD operations |
| `users.py` | User CRUD operations |
| `borrowings.py` | Borrow, return, fine, and reservation logic |
| `db.py` | Database connection, schema creation, and migrations |
| `config.py` | Configurable constants (`BORROW_LIMIT_DAYS`, `FINE_PER_DAY`, `DB_NAME`, `ADMIN_PASSWORD`, `PAGE_SIZE`, `MAX_BORROWS`) |
| `schema.sql` | SQLite table definitions (`Users`, `Books`, `Borrowings`, `Reservations`) |

## Database Schema

- **Users** — `user_id`, `username` (unique), `email` (unique)
- **Books** — `book_id`, `title`, `author`, `publication_year`, `isbn` (unique), `genre`, `copies`
- **Borrowings** — `borrowing_id`, `book_id`, `user_id`, `borrow_date`, `return_date`, `fine`
- **Reservations** — `reservation_id`, `book_id`, `user_id`, `reserved_at`

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
MAX_BORROWS = 3             # Max books a member can borrow at once
ADMIN_PASSWORD = "admin123" # Password for the admin menu
PAGE_SIZE = 10              # Rows per page in list views
```

## Pending Features

### Book Management
- [x] Standalone "View all books" menu option
- [x] Search / filter books by title, author, or publication year
- [x] Add ISBN and genre fields to books
- [x] Support multiple copies of the same title

### User Management
- [x] Standalone "View all users" menu option
- [x] Update user — edit username or email for an existing user

### Borrowing & Fines
- [x] Borrowing history — view past (returned) borrowings, not just active ones
- [x] Admin view of all currently active borrowings across all users
- [x] Overdue report — list books whose borrow date has exceeded the free period
- [x] Fine tracking — fine amounts persisted to the database and shown in borrowing history
- [x] Maximum concurrent borrow limit per user

### General
- [x] Role-based access — separate admin and member menus with admin password protection
- [x] Book reservation / hold queue for books that are currently borrowed
- [x] Pagination for large catalogs or user lists


#### myLibrary web
This will be a web based implementation of the same CLI application.