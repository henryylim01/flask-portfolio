"""
Creates user accounts interactively so passwords are never stored in source
control. Run with: python3 create_users.py
"""
import getpass

from flask_app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    print("Add a user (Ctrl+C to stop)")
    while True:
        try:
            username = input("Username: ").strip()
            if not username:
                continue
            if User.query.filter_by(username=username).first() is not None:
                print(f"'{username}' already exists, skipping.")
                continue

            password = getpass.getpass("Password: ")
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                print("Passwords did not match, try again.")
                continue

            db.session.add(
                User(username=username, password_hash=generate_password_hash(password))
            )
            db.session.commit()
            print(f"User '{username}' created.")
        except (KeyboardInterrupt, EOFError):
            print("\nDone.")
            break
