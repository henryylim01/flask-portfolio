from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, login_user, LoginManager, logout_user, UserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import os

app = Flask(__name__)

# --- Database config (SQLite) ---
project_dir = os.path.dirname(os.path.abspath(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(project_dir, "comments.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

app.secret_key = "REDACTED"
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.username


all_users = {
    "admin": User("admin", generate_password_hash("REDACTED")),
    "bob": User("bob", generate_password_hash("REDACTED")),
    "caroline": User("caroline", generate_password_hash("REDACTED")),
}


@login_manager.user_loader
def load_user(user_id):
    return all_users.get(user_id)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))


@app.route("/")
def index():
    comments = Comment.query.all()
    return render_template("index.html", comments=comments)


@app.route("/add", methods=["POST"])
def add():
    if not current_user.is_authenticated:
        return redirect(url_for("index"))

    content = request.form["contents"].strip()
    if content:
        comment = Comment(content=content)
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for("index"))


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login_page.html", error=False)

    username = request.form["username"]
    if username not in all_users:
        return render_template("login_page.html", error=True)
    user = all_users[username]

    if not user.check_password(request.form["password"]):
        return render_template("login_page.html", error=True)

    login_user(user)
    return redirect(url_for("index"))


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)