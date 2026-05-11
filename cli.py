import sqlite3
from datetime import date

from books import (add_book, delete_book, get_all_books, get_available_books,
                   get_unavailable_books, search_books, update_book)
from borrowings import (
    add_reservation, borrow_book, cancel_reservation, get_all_active_borrowings,
    get_all_reservations, get_book_reservation_count, get_borrowed_books,
    get_borrowing_history, get_overdue_report, get_user_reservations, return_book,
)
from config import ADMIN_PASSWORD, BORROW_LIMIT_DAYS, PAGE_SIZE
from db import init_db
from users import add_user, delete_user, get_all_users, update_user


# ──────────────────────────── display helpers ────────────────────────────

def _paginate(items: list, page_size: int = PAGE_SIZE):
    for i in range(0, len(items), page_size):
        yield items[i:i + page_size]


def _paged_display(items: list, header: str, row_fn) -> None:
    pages = list(_paginate(items))
    page = 0
    while True:
        print(header)
        for item in pages[page]:
            print(row_fn(item))
        total = len(pages)
        if total == 1:
            break
        nav = []
        if page > 0:
            nav.append("p=prev")
        if page < total - 1:
            nav.append("n=next")
        nav.append("q=done")
        choice = input(f"\nPage {page + 1}/{total}  [{', '.join(nav)}]: ").strip().lower()
        if choice == "n" and page < total - 1:
            page += 1
        elif choice == "p" and page > 0:
            page -= 1
        else:
            break


def _book_header() -> str:
    return (
        f"\n{'ID':<6} {'Title':<30} {'Author':<20} {'Year':<6} {'Genre':<15} {'ISBN':<15} {'Copies'}\n"
        + "-" * 98
    )


def _book_row(b) -> str:
    book_id, title, author, year, isbn, genre, copies = b
    return f"{book_id:<6} {title:<30} {author:<20} {year or '—':<6} {genre or '—':<15} {isbn or '—':<15} {copies}"


def _avail_header() -> str:
    return (
        f"\n{'ID':<6} {'Title':<30} {'Author':<20} {'Year':<6} {'Genre':<15} {'Avail/Total'}\n"
        + "-" * 85
    )


def _avail_row(b) -> str:
    book_id, title, author, year, isbn, genre, copies, available = b
    return f"{book_id:<6} {title:<30} {author:<20} {year or '—':<6} {genre or '—':<15} {available}/{copies}"


def _user_header() -> str:
    return f"\n{'ID':<5} {'Username':<20} {'Email'}\n" + "-" * 50


def _user_row(u) -> str:
    return f"{u[0]:<5} {u[1]:<20} {u[2]}"


# ──────────────────────────── user menu ────────────────────────────

def user_menu(user_id: int, username: str) -> None:
    while True:
        print(f"\n=== Welcome, {username} ===")
        print("1. Browse & Borrow a Book")
        print("2. My Borrowed Books")
        print("3. Return a Book")
        print("4. My Borrowing History")
        print("5. Reserve a Book")
        print("6. My Reservations")
        print("0. Back")
        choice = input("Choice: ").strip()

        if choice == "1":
            books = get_available_books()
            if not books:
                print("No books available to borrow.")
            else:
                _paged_display(books, _avail_header(), _avail_row)
                try:
                    bid = int(input("\nEnter Book ID to borrow (0 to cancel): ").strip())
                    if bid == 0:
                        continue
                    if any(b[0] == bid for b in books):
                        borrow_book(bid, user_id)
                        print(f"Borrowed successfully. Date: {date.today()}")
                    else:
                        print("Invalid Book ID.")
                except ValueError as e:
                    print(f"Error: {e}")

        elif choice == "2":
            books = get_borrowed_books(user_id)
            if not books:
                print("No books currently borrowed.")
            else:
                header = (f"\n{'ID':<6} {'Title':<30} {'Author':<20} {'Year':<6} {'Borrowed On'}\n"
                          + "-" * 80)
                _paged_display(books, header,
                    lambda b: f"{b[0]:<6} {b[1]:<30} {b[2]:<20} {b[3] or '—':<6} {b[4]}")

        elif choice == "3":
            books = get_borrowed_books(user_id)
            if not books:
                print("No books currently borrowed.")
            else:
                header = (f"\n{'ID':<6} {'Title':<30} {'Author':<20} {'Year':<6} {'Borrowed On'}\n"
                          + "-" * 80)
                _paged_display(books, header,
                    lambda b: f"{b[0]:<6} {b[1]:<30} {b[2]:<20} {b[3] or '—':<6} {b[4]}")
                try:
                    bid = int(input("\nEnter Book ID to return (0 to cancel): ").strip())
                    if bid == 0:
                        continue
                    if any(b[0] == bid for b in books):
                        borrow_date_str, fine = return_book(bid, user_id)
                        print(f"Book returned successfully on {date.today()}.")
                        if fine > 0:
                            print(f"Fine: Rs. {fine} (borrowed for more than {BORROW_LIMIT_DAYS} days)")
                        else:
                            print("No fine. Returned within the free period.")
                        res_count = get_book_reservation_count(bid)
                        if res_count > 0:
                            print(f"Note: {res_count} user(s) have this book reserved.")
                    else:
                        print("Invalid Book ID.")
                except ValueError as e:
                    print(f"Error: {e}")

        elif choice == "4":
            history = get_borrowing_history(user_id)
            if not history:
                print("No borrowing history found.")
            else:
                header = (f"\n{'Title':<30} {'Author':<20} {'Borrowed':<12} {'Returned':<12} {'Fine (Rs.)'}\n"
                          + "-" * 87)
                _paged_display(history, header,
                    lambda h: f"{h[0]:<30} {h[1]:<20} {h[2]:<12} {h[3]:<12} {int(h[4]) if h[4] else 0}")

        elif choice == "5":
            unavail = get_unavailable_books()
            if not unavail:
                print("All books are currently available — no need to reserve.")
            else:
                # Pre-fetch reservation counts to avoid per-row queries inside the display lambda.
                res_counts = {b[0]: get_book_reservation_count(b[0]) for b in unavail}
                header = (f"\n{'ID':<6} {'Title':<30} {'Author':<20} {'Genre':<15} {'In Queue'}\n"
                          + "-" * 80)
                _paged_display(unavail, header,
                    lambda b: f"{b[0]:<6} {b[1]:<30} {b[2]:<20} {b[5] or '—':<15} {res_counts[b[0]]}")
                try:
                    bid = int(input("\nEnter Book ID to reserve (0 to cancel): ").strip())
                    if bid == 0:
                        continue
                    if any(b[0] == bid for b in unavail):
                        add_reservation(bid, user_id)
                        print("Reservation added successfully.")
                    else:
                        print("Invalid Book ID.")
                except ValueError as e:
                    print(f"Error: {e}")

        elif choice == "6":
            reservations = get_user_reservations(user_id)
            if not reservations:
                print("No active reservations.")
            else:
                header = (f"\n{'Book ID':<8} {'Title':<30} {'Author':<20} {'Reserved On'}\n"
                          + "-" * 72)
                _paged_display(reservations, header,
                    lambda r: f"{r[0]:<8} {r[1]:<30} {r[2]:<20} {r[3]}")
                try:
                    bid = int(input("\nEnter Book ID to cancel reservation (0 to skip): ").strip())
                    if bid != 0:
                        cancel_reservation(bid, user_id)
                        print("Reservation cancelled.")
                except ValueError as e:
                    print(f"Error: {e}")

        elif choice == "0":
            break
        else:
            print("Invalid choice.")


# ──────────────────────────── admin menu ────────────────────────────

def admin_menu() -> None:
    while True:
        print("\n=== Admin Menu ===")
        print("1.  Add a Book")
        print("2.  Update Book")
        print("3.  Delete Book")
        print("4.  View Catalog (with Search)")
        print("5.  Create User")
        print("6.  Update User")
        print("7.  Delete User")
        print("8.  View All Users")
        print("9.  Active Borrowings")
        print("10. Overdue Report")
        print("11. All Reservations")
        print("0.  Back")
        choice = input("Choice: ").strip()

        if choice == "1":
            books = get_all_books()
            if books:
                _paged_display(books, _book_header(), _book_row)
            else:
                print("\nNo books in catalog yet.")
            print()
            title = input("New book title (or leave blank to cancel): ").strip()
            if not title:
                continue
            author = input("Author: ").strip()
            year_raw = input("Publication year (leave blank if unknown): ").strip()
            year = int(year_raw) if year_raw.isdigit() else None
            isbn = input("ISBN (leave blank if unknown): ").strip() or None
            genre = input("Genre (leave blank if unknown): ").strip() or None
            copies_raw = input("Number of copies [1]: ").strip()
            copies = int(copies_raw) if copies_raw.isdigit() and int(copies_raw) > 0 else 1
            try:
                book_id = add_book(title, author, year, isbn, genre, copies)
                print(f"Book added with ID={book_id}")
            except sqlite3.IntegrityError as e:
                print(f"Error: {e}")

        elif choice == "2":
            books = get_all_books()
            if not books:
                print("No books in catalog.")
                continue
            _paged_display(books, _book_header(), _book_row)
            try:
                bid_input = input("\nEnter Book ID to update (0 to cancel): ").strip()
                if not bid_input or bid_input == "0":
                    continue
                bid = int(bid_input)
                matched = next((b for b in books if b[0] == bid), None)
                if not matched:
                    print("Invalid Book ID.")
                    continue
                _, old_title, old_author, old_year, old_isbn, old_genre, old_copies = matched
                print(f"Updating '{old_title}'. Leave blank to keep current value.")
                new_title = input(f"Title [{old_title}]: ").strip() or old_title
                new_author = input(f"Author [{old_author}]: ").strip() or old_author
                new_year_raw = input(f"Year [{old_year or '—'}]: ").strip()
                new_year = int(new_year_raw) if new_year_raw.isdigit() else old_year
                new_isbn = input(f"ISBN [{old_isbn or '—'}]: ").strip() or old_isbn
                new_genre = input(f"Genre [{old_genre or '—'}]: ").strip() or old_genre
                new_copies_raw = input(f"Copies [{old_copies}]: ").strip()
                new_copies = (int(new_copies_raw)
                              if new_copies_raw.isdigit() and int(new_copies_raw) > 0
                              else old_copies)
                update_book(bid, new_title, new_author, new_year, new_isbn, new_genre, new_copies)
                print("Book updated successfully.")
            except (ValueError, sqlite3.Error) as e:
                print(f"Error: {e}")

        elif choice == "3":
            books = get_all_books()
            if not books:
                print("No books in catalog.")
                continue
            _paged_display(books, _book_header(), _book_row)
            try:
                bid_input = input("\nEnter Book ID to delete (0 to cancel): ").strip()
                if not bid_input or bid_input == "0":
                    continue
                bid = int(bid_input)
                matched = next((b for b in books if b[0] == bid), None)
                if matched:
                    confirm = input(f"Delete '{matched[1]}'? (y/N): ").strip().lower()
                    if confirm == "y":
                        delete_book(bid)
                        print("Book deleted successfully.")
                    else:
                        print("Deletion cancelled.")
                else:
                    print("Invalid Book ID.")
            except (ValueError, sqlite3.Error) as e:
                print(f"Error: {e}")

        elif choice == "4":
            query = input("Search term (or leave blank for all): ").strip()
            books = search_books(query) if query else get_all_books()
            if not books:
                print("No books found.")
            else:
                _paged_display(books, _book_header(), _book_row)

        elif choice == "5":
            username = input("Username: ").strip()
            email = input("Email: ").strip()
            try:
                new_id = add_user(username, email)
                print(f"User created with ID: {new_id}")
            except sqlite3.IntegrityError:
                print("Error: Username or email already exists.")

        elif choice == "6":
            users = get_all_users()
            if not users:
                print("No users found.")
                continue
            _paged_display(users, _user_header(), _user_row)
            try:
                uid_input = input("\nEnter User ID to update (0 to cancel): ").strip()
                if not uid_input or uid_input == "0":
                    continue
                uid = int(uid_input)
                matched = next((u for u in users if u[0] == uid), None)
                if not matched:
                    print("Invalid User ID.")
                    continue
                _, old_name, old_email = matched
                print(f"Updating '{old_name}'. Leave blank to keep current value.")
                new_name = input(f"Username [{old_name}]: ").strip() or old_name
                new_email = input(f"Email [{old_email}]: ").strip() or old_email
                try:
                    update_user(uid, new_name, new_email)
                    print("User updated successfully.")
                except sqlite3.IntegrityError:
                    print("Error: Username or email already exists.")
            except (ValueError, sqlite3.Error) as e:
                print(f"Error: {e}")

        elif choice == "7":
            users = get_all_users()
            if not users:
                print("No users found.")
                continue
            _paged_display(users, _user_header(), _user_row)
            try:
                uid_input = input("\nEnter User ID to delete (0 to cancel): ").strip()
                if not uid_input or uid_input == "0":
                    continue
                uid = int(uid_input)
                matched = next((u for u in users if u[0] == uid), None)
                if matched:
                    confirm = input(f"Delete user '{matched[1]}'? (y/N): ").strip().lower()
                    if confirm == "y":
                        delete_user(uid)
                        print("User deleted successfully.")
                    else:
                        print("Deletion cancelled.")
                else:
                    print("Invalid User ID.")
            except (ValueError, sqlite3.Error) as e:
                print(f"Error: {e}")

        elif choice == "8":
            users = get_all_users()
            if not users:
                print("No users found.")
            else:
                _paged_display(users, _user_header(), _user_row)

        elif choice == "9":
            active = get_all_active_borrowings()
            if not active:
                print("No active borrowings.")
            else:
                header = f"\n{'User':<15} {'Book Title':<30} {'Borrowed On'}\n" + "-" * 60
                _paged_display(active, header, lambda r: f"{r[0]:<15} {r[1]:<30} {r[2]}")

        elif choice == "10":
            overdue = get_overdue_report()
            if not overdue:
                print("No overdue books.")
            else:
                header = (f"\n{'User':<15} {'Book Title':<30} {'Borrowed On':<12} {'Days Out'}\n"
                          + "-" * 65)
                _paged_display(overdue, header,
                    lambda r: f"{r[0]:<15} {r[1]:<30} {r[2]:<12} {r[3]}")

        elif choice == "11":
            reservations = get_all_reservations()
            if not reservations:
                print("No pending reservations.")
            else:
                header = f"\n{'User':<15} {'Book Title':<30} {'Reserved On'}\n" + "-" * 60
                _paged_display(reservations, header, lambda r: f"{r[0]:<15} {r[1]:<30} {r[2]}")

        elif choice == "0":
            break
        else:
            print("Invalid choice.")


# ──────────────────────────── landing menu ────────────────────────────

def landing_menu() -> None:
    while True:
        print("\n=== myLibrary ===")
        print("1. Login as Member")
        print("2. Register New Member")
        print("3. Admin Login")
        print("0. Exit")
        choice = input("Choice: ").strip()

        if choice == "1":
            users = get_all_users()
            if not users:
                print("No members registered yet. Please register first.")
                continue
            _paged_display(users, _user_header(), _user_row)
            try:
                user_id = int(input("\nEnter User ID: ").strip())
                matched = next((u for u in users if u[0] == user_id), None)
                if matched:
                    user_menu(user_id, matched[1])
                else:
                    print("Invalid User ID.")
            except ValueError:
                print("Please enter a valid numeric ID.")

        elif choice == "2":
            username = input("Username: ").strip()
            email = input("Email: ").strip()
            try:
                new_id = add_user(username, email)
                print(f"Registered successfully. Your member ID: {new_id}")
            except sqlite3.IntegrityError:
                print("Error: Username or email already exists.")

        elif choice == "3":
            password = input("Admin password: ").strip()
            if password == ADMIN_PASSWORD:
                print("Access granted.")
                admin_menu()
            else:
                print("Incorrect password.")

        elif choice == "0":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    init_db()
    landing_menu()
