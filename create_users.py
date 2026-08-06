from flask_app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    users_to_add = [
        ("admin", "REDACTED"),
        ("bob", "REDACTED"),
        ("caroline", "REDACTED"),
        ("tester", "REDACTED"),
    ]

    for username, password in users_to_add:
        if User.query.filter_by(username=username).first() is None:
            db.session.add(User(username=username, password_hash=generate_password_hash(password)))

    db.session.commit()
    print("Users created successfully!")