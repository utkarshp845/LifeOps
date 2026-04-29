import os
import sys
from getpass import getpass
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import select

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(BACKEND_ROOT.parent / ".env")

from auth import get_password_hash
from database import SessionLocal
from models.user import User


def main() -> None:
    username = os.getenv("LIFEOS_USERNAME") or input("Username: ").strip()
    password = os.getenv("LIFEOS_PASSWORD") or getpass("Password: ")

    if not username or not password:
        raise SystemExit("Username and password are required")

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == username))
        if user is None:
            user = User(username=username, password_hash=get_password_hash(password))
            db.add(user)
            action = "Created"
        else:
            user.password_hash = get_password_hash(password)
            action = "Updated"
        db.commit()
        print(f"{action} single user: {username}")


if __name__ == "__main__":
    main()
