import sqlite3
from datetime import date

from books import add_book, delete_book, get_all_books, get_available_books, update_book
from borrowings import borrow_book, get_borrowed_books, return_book
from config import BORROW_LIMIT_DAYS
from users import add_user, delete_user, get_all_users


def user_menu(user_id: int, username: str) -> None:
    while True:
        print(f"\n=== Welcome, {username} ===")
        print("1. Browse & Borrow a Book")
        print("2. My Borrowed Books")
        print("3. Return a Book")
        print("0. Back")
        choice = input("Choice: ").strip()

        if choice == "1":
            books = get_available_books()
            if not books:
                print("No books available to borrow.")
            else:
                print(f"\n{'ID':<6} {'Title':<30} {'Author':<20} {'Year'}")
                print("-" * 70)
                for book_id, title, author, year in books:
                    print(f"{book_id:<6} {title:<30} {author:<20} {year or '—'}")
                try:
                    bid = int(input("\nEnter Book ID to borrow (0 to cancel): ").strip())
                    if bid == 0:
                        continue
                    if any(b[0] == bid for b in books):
                        borrow_book(bid, user_id)
                        print(f"Borrowed successfully. Date: {date.today()}")
                    else:
                        print("Invalid Book ID.")
                except ValueError:
                    print("Please enter a valid numeric ID.")

        elif choice == "2":
            books = get_borrowed_books(user_id)
            if not books:
                print("No books currently borrowed.")
            else:
                print(f"\n{'ID':<6} {'Title':<30} {'Author':<20} {'Year':<6} {'Borrowed On'}")
                print("-" * 80)
                for book_id, title, author, year, borrow_date in books:
                    print(f"{book_id:<6} {title:<30} {author:<20} {year or '—':<6} {borrow_date}")

        elif choice == "3":
            books = get_borrowed_books(user_id)
            if not books:
                print("No books currently borrowed.")
            else:
                print(f"\n{'ID':<6} {'Title':<30} {'Author':<20} {'Year':<6} {'Borrowed On'}")
                print("-" * 80)
                for book_id, title, author, year, borrow_date in books:
                    print(f"{book_id:<6} {title:<30} {author:<20} {year or '—':<6} {borrow_date}")
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
                            print("No fine. Returned within the 5-day free period.")
                    else:
                        print("Invalid Book ID.")
                except ValueError as e:
                    print(f"Error: {e}")

        elif choice == "0":
            break
        else:
            print("Invalid choice, please enter 0, 1, 2, or 3.")


def main_menu() -> None:
    while True:
        print("\n=== Library System ===")
        print("1. Add a Book to Catalog")
        print("2. Select User (Login)")
        print("3. Create New User")
        print("4. Delete User")
        print("5. Delete Book")
        print("6. Update Book")
        print("0. Exit")

        choice = input("Choice: ").strip()

        if choice == "1":
            books = get_all_books()
            if books:
                print(f"\n{'ID':<6} {'Title':<30} {'Author':<20} {'Year'}")
                print("-" * 70)
                for book_id, title, author, year in books:
                    print(f"{book_id:<6} {title:<30} {author:<20} {year or '—'}")
            else:
                print("\nNo books in catalog yet.")
            print()
            title = input("New book title (or leave blank to cancel): ").strip()
            if not title:
                continue
            author = input("Author: ").strip()
            year_raw = input("Publication year (leave blank if unknown): ").strip()
            year = int(year_raw) if year_raw.isdigit() else None
            try:
                book_id = add_book(title, author, year)
                print(f"Book added to catalog with ID={book_id}")
            except sqlite3.IntegrityError as e:
                print(f"Error: {e}")

        elif choice == "2":
            users = get_all_users()
            if not users:
                print("No users found. Please create one first.")
                continue
            print(f"\n{'ID':<5} {'Username':<20} {'Email'}")
            print("-" * 45)
            for uid, name, email in users:
                print(f"{uid:<5} {name:<20} {email}")
            try:
                user_id = int(input("\nEnter User ID: ").strip())
                matched = next((u for u in users if u[0] == user_id), None)
                if matched:
                    user_menu(user_id, matched[1])
                else:
                    print("Invalid User ID.")
            except ValueError:
                print("Please enter a valid numeric ID.")

        elif choice == "3":
            username = input("Enter username: ").strip()
            email = input("Enter email: ").strip()
            try:
                new_id = add_user(username, email)
                print(f"User created with ID: {new_id}")
            except sqlite3.IntegrityError:
                print("Error: Username or email already exists.")

        elif choice == "4":
            users = get_all_users()
            if not users:
                print("No users found.")
                continue
            print(f"\n{'ID':<5} {'Username':<20} {'Email'}")
            print("-" * 45)
            for uid, name, email in users:
                print(f"{uid:<5} {name:<20} {email}")
            try:
                uid_input = input("\nEnter User ID to delete (0 to cancel): ").strip()
                if not uid_input or uid_input == "0":
                    continue
                uid = int(uid_input)
                matched = next((u for u in users if u[0] == uid), None)
                if matched:
                    confirm = input(f"Are you sure you want to delete user '{matched[1]}'? (y/N): ").strip().lower()
                    if confirm == 'y':
                        delete_user(uid)
                        print("User deleted successfully.")
                    else:
                        print("Deletion cancelled.")
            except (ValueError, sqlite3.Error) as e:
                print(f"Error: {e}")

        elif choice == "5":
            books = get_all_books()
            if not books:
                print("No books in catalog.")
                continue
            print(f"\n{'ID':<6} {'Title':<30} {'Author':<20} {'Year'}")
            print("-" * 70)
            for book_id, title, author, year in books:
                print(f"{book_id:<6} {title:<30} {author:<20} {year or '—'}")
            try:
                bid_input = input("\nEnter Book ID to delete (0 to cancel): ").strip()
                if not bid_input or bid_input == "0":
                    continue
                bid = int(bid_input)
                matched = next((b for b in books if b[0] == bid), None)
                if matched:
                    confirm = input(f"Are you sure you want to delete '{matched[1]}'? (y/N): ").strip().lower()
                    if confirm == 'y':
                        delete_book(bid)
                        print("Book deleted successfully.")
                    else:
                        print("Deletion cancelled.")
                else:
                    print("Invalid Book ID.")
            except (ValueError, sqlite3.Error) as e:
                print(f"Error: {e}")

        elif choice == "6":
            books = get_all_books()
            if not books:
                print("No books in catalog.")
                continue
            print(f"\n{'ID':<6} {'Title':<30} {'Author':<20} {'Year'}")
            print("-" * 70)
            for book_id, title, author, year in books:
                print(f"{book_id:<6} {title:<30} {author:<20} {year or '—'}")
            try:
                bid_input = input("\nEnter Book ID to update (0 to cancel): ").strip()
                if not bid_input or bid_input == "0":
                    continue
                bid = int(bid_input)
                matched = next((b for b in books if b[0] == bid), None)
                if matched:
                    _, old_title, old_author, old_year = matched
                    print(f"Updating '{old_title}'. Leave blank to keep current value.")
                    new_title = input(f"New Title [{old_title}]: ").strip() or old_title
                    new_author = input(f"New Author [{old_author}]: ").strip() or old_author
                    new_year_raw = input(f"New Year [{old_year or '—'}]: ").strip()
                    new_year = int(new_year_raw) if new_year_raw.isdigit() else old_year
                    update_book(bid, new_title, new_author, new_year)
                    print("Book updated successfully.")
                else:
                    print("Invalid Book ID.")
            except (ValueError, sqlite3.Error) as e:
                print(f"Error: {e}")

        elif choice == "0":
            break


if __name__ == "__main__":
    main_menu()
