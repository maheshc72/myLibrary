from db import init_db
from users import seed_users
from cli import main_menu

if __name__ == "__main__":
    init_db()
    seed_users()
    main_menu()
