# myLibrary v1

A command-line library management system built with Python and SQLite.

## Prerequisites

- **Python 3.10+**
- **SQLite 3** (usually pre-installed with Python)

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

## Implemented Features

### Book Management
- **Add a book** — Add a new book (title, author, optional publication year); existing catalog is shown before prompting
- **Update a book** — Edit title, author, or publication year; leave a field blank to keep the current value
- **Delete a book** — Remove a book; blocked if the book is currently borrowed by anyone
- **Browse available books** — Users see only books not currently checked out

### User Management
- **Create a user** — Register with a unique username and email
- **Login as a user** — Select a user by ID from the full user list to enter the borrowing menu
- **Delete a user** — Remove a user; blocked if they have active borrowings; requires confirmation

### Borrowing System
- **Borrow a book** — Check out an available book; borrow date is recorded automatically
- **View borrowed books** — See all books currently checked out, with borrow dates
- **Return a book** — Mark a book as returned; return date is recorded and any fine is calculated

### Fine Calculation
- Books returned within the **5-day free period** incur no charge
- Returns after 5 days are charged **Rs. 1 per day** for each day over the limit
- Fine amount is displayed at the time of return

### Database & Infrastructure
- SQLite with foreign key enforcement
- Automatic schema migration from the v1 schema (where `Books` held a `user_id` directly) to the current normalized schema
- Configurable constants via `config.py`

## Pending Features

### Book Management
- [ ] Standalone "View all books" menu option (currently the catalog is only shown as part of Add / Update / Delete flows)
- [ ] Search / filter books by title, author, or publication year
- [ ] Add ISBN and genre fields to books
- [ ] Support multiple copies of the same title

### User Management
- [ ] Standalone "View all users" menu option (currently the user list is only shown inside Login and Delete flows)
- [ ] Update user — edit username or email for an existing user

### Borrowing & Fines
- [ ] Borrowing history — view past (returned) borrowings, not just active ones
- [ ] Admin view of all currently active borrowings across all users
- [ ] Overdue report — list books whose borrow date has exceeded the free period
- [ ] Fine tracking — persist fine amounts to the database rather than only displaying them at return time
- [ ] Maximum concurrent borrow limit per user

### General
- [ ] Role-based access — separate admin and member menus
- [ ] Book reservation / hold queue for books that are currently borrowed
- [ ] Pagination for large catalogs or user lists

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

Foreign key constraints are enforced. Deleting a user or book cascades to related borrowing records.

## Configuration

Edit `config.py` to change default behaviour:

```python
DB_NAME = "library.db"      # SQLite database file
BORROW_LIMIT_DAYS = 5       # Days before fines begin
FINE_PER_DAY = 1            # Fine in Rupees per overdue day
```
