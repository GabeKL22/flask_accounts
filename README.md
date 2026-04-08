# Flask Accounts

> Plug-and-play authentication for Flask with UI, database, and email verification included.

A modular, reusable authentication system for Flask applications.

## ✨ Features

- User registration
- Login / logout
- Email verification (with expiration + resend)
- Password hashing (Werkzeug)
- PostgreSQL backend
- Session-based authentication
- Configurable UI (banners, redirects, custom CSS)
- SMTP email support (or terminal mode for development)

---

## 🚀 Installation

```bash
pip install flask-accounts
```
---



---

## ⚡ Quick Start

### Create run.py:

```python
from flask import Flask
from flask_accounts import init_auth

app = Flask(__name__)

app.config["SECRET_KEY"] = "your-secret-key"

# Database
app.config["DB_HOST"] = "localhost"
app.config["DB_NAME"] = "accountdb"
app.config["DB_USER"] = "accountuser"
app.config["DB_PASSWORD"] = "yourpassword"

# Email
app.config["SMTP_HOST"] = "smtp.email.com"
app.config["SMTP_PORT"] = 587
app.config["SMTP_USERNAME"] = "youremail@email.com"
app.config["SMTP_PASSWORD"] = "your_app_password"
app.config["SMTP_FROM_EMAIL"] = "youremail@email.com"

# Dev mode
app.config["USE_TERMINAL_EMAIL"] = True

init_auth(app)

if __name__ == "__main__":
    app.run(debug=True)
```

### 🛠️ Database Setup

### Recommended (first-time setup):

```flask --app run.py auth-bootstrap-db```

Enter your psql admin username and password - this will create the db.

```python run.py```

That's it, you now hyave a fully working login and register page with PostgreSQL support. Visit the IP link in the terminal given by flask to open the page.

---

## 📸 Screenshots

### 🔐 Login
![Login](https://raw.githubusercontent.com/GabeKL22/flask_accounts/main/docs/login.png)

### 📝 Register
![Register](https://raw.githubusercontent.com/GabeKL22/flask_accounts/main/docs/register.png)

### 📧 Email Verification
![Verify Email](https://raw.githubusercontent.com/GabeKL22/flask_accounts/main/docs/verify.png)

---

## ⚙️ Configuration

### Required

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

---

### Optional

LOGIN_REDIRECT = "home"  
REGISTER_REDIRECT = "verify_email"  
VERIFY_EMAIL_REDIRECT = "login"  

LOGIN_BANNER = "Welcome Back"  
LOGIN_BANNER_MSG = "Login to your account"  

REGISTER_BANNER = "Create Account"  
REGISTER_BANNER_MSG = "Register to get started"  

AUTH_CUSTOM_CSS = "custom.css"

---

## 🎨 Custom Styling

Place CSS in your app:

your_app/static/custom.css

Then:

AUTH_CUSTOM_CSS = "custom.css"

---

## 🗄️ Database Setup

CREATE DATABASE accountdb;

CREATE USER accountuser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE accountdb TO accountuser;

Run schema:

psql -U accountuser -d accountdb -f schema.sql

---

## 🔐 Authentication Flow

1. Register  
2. Verify email  
3. Login  
4. Access app  

---

## 🔌 Routes

/auth/register  
/auth/login  
/auth/logout  
/auth/verify-email  
/auth/resend-code  

---

## 🧠 Protected Route Example

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

- Session-based auth  
- PostgreSQL via psycopg2  

---

## 🚀 Roadmap

- Password reset  
- OAuth  
- JWT  
- SQLAlchemy  

---

## 🧑‍💻 Author

Gabriel Leffew

---

## 📜 License

MIT
