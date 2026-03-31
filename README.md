# Flask Accounts (Reusable Auth Module)

A modular, reusable Flask authentication system with:

* User registration
* Login / logout
* Email verification (with expiration + resend)
* Password hashing (Werkzeug)
* PostgreSQL backend
* Config-driven email (SMTP or terminal mode)

Designed to be **plug-and-play in future Flask applications** using:

```python
from app.auth import init_auth
init_auth(app)
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/GabeKL22/flask_accounts.git
cd flask_accounts

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

---

## ⚙️ Configuration

Edit:

```
app/config.py
```

Set your values:

```python
SECRET_KEY = "your-secret-key"

# PostgreSQL
DB_HOST = "localhost"
DB_NAME = "accountdb"
DB_USER = "accountuser"
DB_PASSWORD = "yourpassword"

# Email (SMTP)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "youremail@gmail.com"
SMTP_PASSWORD = "your_app_password"
SMTP_FROM_EMAIL = "youremail@gmail.com"

# Other useful configurations (UI)
LOGIN_REDIRECT = "home" # Must have a route defined
REGISTER_REDIRECT = "verify_email" # Must have a route defined
VERIFY_EMAIL_REDIRECT = "login" # Must have a route defined
LOGIN_BANNER = "Welcome Back"
LOGIN_BANNER_MSG = "Login to your account"
REGISTER_BANNER = "Create Account"
REGISTER_BANNER_MSG = "Register to get started"
CSS_STYLE_FILE = ""

# Dev mode
USE_TERMINAL_EMAIL = True
```

### Dev Mode Behavior

| Setting | Behavior                             |
| ------- | ------------------------------------ |
| `True`  | Prints verification code in terminal |
| `False` | Sends real email via SMTP            |

---

## 🗄️ PostgreSQL Database Setup

### 1. Open PostgreSQL

```bash
sudo -u postgres psql
```

---

### 2. Create database

```sql
CREATE DATABASE accountdb;
```

---

### 3. Create user (optional but recommended)

```sql
CREATE USER accountuser WITH PASSWORD 'yourpassword';
ALTER ROLE accountuser SET client_encoding TO 'utf8';
ALTER ROLE accountuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE accountuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE accountdb TO accountuser;
```

---

### 4. Run schema

From your project root:

```bash
psql -U accountuser -d accountdb -f schema.sql
```

---

## ▶️ Run the App

```bash
python run.py
```

Then open:

```
http://<ip>/auth/register
```

---

## 🔐 Authentication Flow

1. Register a new account
2. Receive verification code (terminal or email)
3. Verify email
4. Login
5. Access protected routes

---

## 📁 Project Structure

```
project/
│
├── run.py
├── requirements.txt
├── schema.sql
│
└── app/
    ├── __init__.py
    ├── config.py
    ├── db.py
    │
    └── auth/
        ├── __init__.py        # init_auth(app)
        ├── routes.py
        ├── service.py
        ├── validators.py
        ├── session.py
        │
        └── templates/
            └── auth/
                ├── login.html
                ├── register.html
                └── verify_email.html
```

---

## 🔌 Using This in Another Flask App

### 1. Copy module

Copy:

```
app/auth/
schema.sql
```

into your new project.

---

### 1.1 PIP install module (from top directory)
```
pip install -e .
```

---

### 2. Add required config

Your app must define:

```python
SECRET_KEY
DB_HOST
DB_NAME
DB_USER
DB_PASSWORD
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
SMTP_FROM_EMAIL
USE_TERMINAL_EMAIL
```

---

### 3. Initialize auth

```python
from flask import Flask
from app.auth import init_auth

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_auth(app)

    return app
```

---

### 4. Routes provided

* `/auth/register`
* `/auth/login`
* `/auth/logout`
* `/auth/verify-email`
* `/auth/resend-code`

---

## 🧠 Example Protected Route

```python
from flask import session, redirect, url_for

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.show_login"))
    return "Welcome to your dashboard"
```

---

## ⚠️ Notes

* Uses session-based authentication (no JWT)
* Uses raw SQL via `psycopg2`
* Designed for extension into SaaS applications

---

## 🚀 Future Improvements

* Password reset flow
* JWT / token-based auth
* OAuth (Google, GitHub)
* SQLAlchemy migration
* Packaging for pip install

---

## 🧑‍💻 Author

Gabriel Leffew


## 📜 License

MIT License
