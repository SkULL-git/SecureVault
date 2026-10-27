"""Promote an existing SecureVault account to administrator.

Run after the account has been registered:
    python create_admin.py
The account must already exist. This script never creates a default admin password.
"""
from getpass import getpass

from app import app
from database.models import User
from extensions import db


def main():
    email = input("Existing account email to promote: ").strip().lower()
    confirmation = input(f"Promote {email} to administrator? Type YES: ").strip()
    if confirmation != "YES":
        print("Cancelled.")
        return

    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print("No account with that email exists. Register normally first.")
            return
        user.role = "admin"
        user.is_active = True
        db.session.commit()
        print(f"{user.email} is now an active administrator.")


if __name__ == "__main__":
    main()
