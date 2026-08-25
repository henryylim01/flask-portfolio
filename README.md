# Flask Portfolio — My Scratch Page

A small portfolio website built with **Python, Flask, and SQLite**, hosted live on **PythonAnywhere**.

🔗 **Live site:** https://henryyylim01.pythonanywhere.com
🔗 **Portfolio page:** https://henryyylim01.pythonanywhere.com/portfolio/

Built as Mini Project A and B for the Cloud Support & DevOps Bootcamp at Generation Singapore, to practice Flask fundamentals, database-backed apps, authentication, and using Git as source control.

---

## What it does

- Displays a "Scratch Page" with a list of comments stored in a database
- Lets **logged-in users only** add new comments, enforced on both the frontend and backend
- Has a login/logout system with multiple user accounts, each with a securely hashed password
- Has a separate Portfolio/Introduction page linking back to the Scratch Page

---

## Tech stack

| Piece | Tool |
|---|---|
| Backend | Python 3.10, Flask |
| Auth | Flask-Login, Werkzeug password hashing |
| Database | SQLite, accessed via Flask-SQLAlchemy |
| Hosting | PythonAnywhere (free "Beginner" tier) |
| Version control | Git + GitHub |

---

## Mini Project A — Portfolio site + comments

- Built a Flask app with a `Comment` model and two routes: `/` (view comments) and `/add` (post a new comment)
- Used SQLite instead of MySQL, since free PythonAnywhere accounts no longer include MySQL access:
  ```python
  SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(project_dir, "comments.db")
  ```
- Created the database tables via a one-off script (`create_db.py`), rather than the interactive Python shell — more reliable than typing multi-line code directly into the REPL
- Deployed via PythonAnywhere's **Manual configuration**, with a custom WSGI file pointing at `flask_app.py`
- Added name + LinkedIn link to the page (Bonus Task A)

## Mini Project B — Login, security, and a database-backed user system

### Task A — Login page
- Added `/login/` (GET + POST) and a matching `login_page.html` template, styled with Bootstrap
- Integrated **Flask-Login** to manage user sessions:
  - A `User` class (`UserMixin`) representing a logged-in user
  - A `login_manager.user_loader` function so Flask-Login can look up a user from their session
  - `app.secret_key` used internally to sign session cookies (loaded from the `FLASK_SECRET_KEY` environment variable — see **Security** below)
- Added `/logout/`, protected with `@login_required`

### Task B — Real, server-side security
Initially, the comment form was only *hidden* from logged-out users on the frontend — the `/add` route itself had no protection. This was demonstrated by:
1. Logging in, then opening "Log out" in a second tab (logging out there only)
2. Submitting a comment from the original, still-open tab

The comment still got saved, proving that hiding UI elements isn't real security — a request can always be sent directly to the server, bypassing the browser entirely.

**Fix:** added a server-side check as the first line of the `/add` route:
```python
@app.route("/add", methods=["POST"])
def add():
    if not current_user.is_authenticated:
        return redirect(url_for("index"))
    ...
```
This blocks the request at the server regardless of what the frontend does or doesn't show. Retesting the same two-tab scenario confirmed the comment is no longer saved when the request comes from a logged-out session.

### Bonus Task B — Users moved into the database
Originally, users were hardcoded in a Python dictionary (`all_users = {...}`) directly in `flask_app.py` — functional, but not realistic or extensible. This was replaced with:
- A `User` **database model** (`db.Model` + `UserMixin`), storing `username` and a hashed `password_hash`
- `load_user()` and the `login()` view updated to query the database instead of the dictionary
- A seed script (`create_users.py`) to create the `users` table and populate initial accounts, including a `tester` account

Verified directly via the SQLite CLI:
```bash
sqlite3 comments.db
SELECT * FROM users;
```
— confirming passwords are stored as hashes, never in plaintext. (`create_users.py` originally seeded fixed accounts with hardcoded passwords; it's since been rewritten to prompt for each username/password interactively so no plaintext credentials live in the source — see **Security** below.)

### Bonus Task A — Separate Portfolio/Introduction page
Added `/portfolio/` and `portfolio.html`, a standalone introduction page distinct from the comments Scratch Page, with a name, short bio, LinkedIn link, and a project summary. Linked both ways so visitors can move between the Scratch Page and the Portfolio page.

---

## Getting started

```bash
git clone https://github.com/henryylim01/flask-portfolio.git
cd flask-portfolio
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # reference for which vars you need; edit as a reminder
export FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
# ^ the app reads this at runtime — set it in every new terminal session

python3 create_db.py         # creates comments.db
python3 create_users.py      # prompts you to add login accounts

python3 flask_app.py         # runs on http://localhost:5000
```

---

## Project structure

```
flask-portfolio/
├── flask_app.py          # Flask routes, database models, auth logic
├── create_db.py           # One-off script to create the comments table
├── create_users.py         # Interactive script to create the users table + accounts
├── .env.example              # Template for required environment variables
├── requirements.txt          # Python dependencies
├── templates/
│   ├── index.html              # Scratch Page (comments)
│   ├── login_page.html          # Login form
│   └── portfolio.html            # Introduction/Portfolio page
└── .gitignore

Note: comments.db is generated locally (via create_db.py / create_users.py)
and is gitignored — it's never committed to the repo.
```

---

## What I learned

**From Mini Project A:**
- How Flask splits logic (routes) from presentation (Jinja2 templates)
- How Flask-SQLAlchemy maps Python classes to database tables
- Why free-tier constraints sometimes require adapting a tutorial (MySQL → SQLite)
- Git basics: cloning, committing, pushing, authenticating with a Personal Access Token

**From Mini Project B:**
- The difference between **frontend security** (hiding UI elements — makes a site *look* secure) and **backend security** (server-side checks — makes a site *actually* secure)
- How session-based authentication works with Flask-Login, including cookies and the role of `secret_key`
- Why passwords should always be stored as salted hashes (`generate_password_hash` / `check_password_hash`), never in plaintext
- How to migrate application data (users) from hardcoded Python structures into a proper database table
- Practical debugging on PythonAnywhere: reading error logs, diagnosing a `ModuleNotFoundError` for a missing package (`flask-login`), and fixing virtualenv dependency gaps

---

## Security

This repo went through a security review and cleanup after the original bootcamp submission. Fixes applied:

- **Secret key** — no longer hardcoded in source; loaded from the `FLASK_SECRET_KEY` environment variable at startup (the app now fails fast if it's not set, instead of silently using a weak default). Copy `.env.example` to `.env` and fill in a real value generated with `python3 -c "import secrets; print(secrets.token_hex(32))"`.
- **Debug mode** — off by default; only enabled if `FLASK_DEBUG=true` is explicitly set.
- **CSRF protection** — added via Flask-WTF to both the login and comment forms.
- **No committed database or credentials** — `comments.db` and `__pycache__` are gitignored and generated locally instead of checked in. `create_users.py` now prompts for usernames/passwords interactively rather than storing them as plaintext in source.
- **Git history rewritten** — the repo's commit history was rewritten with `git-filter-repo` to permanently remove an old hardcoded secret key and plaintext seed passwords that had been committed early in the project.

If you're setting this up fresh, see **Getting started** below.

---

## Possible next steps

- Style the portfolio page to match the Bootstrap look of the login page
- Store timestamps and the posting user's name on each comment (linking `Comment` to `User`)
- Add basic input validation/error handling around login attempts (e.g. rate limiting)