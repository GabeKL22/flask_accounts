# Flask Authentication System

A full-stack authentication system built with Flask, PostgreSQL, and modern frontend UI.
This project demonstrates secure user registration, login, email verification, and strong password validation.

---

## 🚀 Features

* 🔐 User Registration & Login
* 📧 Email Verification (6-digit code system)
* 🔑 Secure Password Hashing (Werkzeug)
* 🛡️ Strong Password Requirements:

  * Minimum length (8+ characters)
  * Uppercase + lowercase letters
  * Numbers
  * Special characters
* 🎨 Modern UI with:

  * Animated gradient background
  * Glassmorphism design
  * Live password validation
  * Show/Hide password toggle
* 🗄️ PostgreSQL database integration
* 🔁 Verification code expiration & resend support

---

## 🧠 How It Works

### Registration Flow

1. User submits registration form
2. Password is validated (frontend + backend)
3. Password is hashed using `werkzeug.security`
4. A 6-digit verification code is generated
5. Code is stored in the database with expiration
6. Code is sent via:

   * Terminal (dev mode)
   * Email (production mode)
7. User is redirected to verification page

---

### Email Verification Flow

1. User enters 6-digit code
2. Backend checks:

   * Code matches
   * Code is not expired
3. If valid:

   * `email_verified = TRUE`
   * Code is cleared
4. User can now log in

---

### Login Flow

1. User submits username/email + password
2. Backend:

   * Finds user
   * Verifies password hash
   * Checks `email_verified`
3. If not verified → redirect to verification
4. If valid → login successful

---

## 🗄️ Database Schema

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    firstname VARCHAR(80) NOT NULL,
    lastname VARCHAR(80) NOT NULL,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    verification_code VARCHAR(6),
    verification_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/GabeKL22/flask_accounts.git
cd flask_accounts
```

---

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure environment

Copy the example config:

```bash
cp app/config.example.py app/config.py
```

Then edit:

```python
DB_HOST = "localhost"
DB_NAME = "accountdb"
DB_USER = "your_user"
DB_PASSWORD = "your_password"
```

---

### 5. Setup PostgreSQL

Create database and user:

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE accountdb;
CREATE USER accountuser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE accountdb TO accountuser;
```

Run schema:

```bash
psql -h localhost -U accountuser -d accountdb -f schema.sql
```

---

### 6. Run the app

```bash
python run.py
```

Visit:

```
http://127.0.0.1:5000
```

---

## 📧 Email Setup

### Development (default)

Uses terminal output:

```python
USE_TERMINAL_EMAIL = True
```

Verification code will print in console.

---

### Production (real email)

Set:

```python
USE_TERMINAL_EMAIL = False
```

Configure SMTP (example Gmail):

```python
SMTP_USERNAME = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"
```

⚠️ Use an **App Password**, not your real password.

---

## 🔒 Security Notes

* Passwords are hashed (never stored in plaintext)
* Email verification prevents fake accounts
* Verification codes expire (10 minutes)
* Sensitive config is excluded via `.gitignore`

---

## 📁 Project Structure

```text
project/
│
├── run.py
├── requirements.txt
├── templates/
│   ├── login.html
│   ├── register.html
│   └── verify_email.html
│
└── app/
    ├── __init__.py
    └── config.py
```

---

## 💡 Future Improvements

* JWT authentication / session management
* Password reset via email
* Rate limiting (prevent brute force)
* OAuth (Google login)
* Docker deployment
* Cloud hosting (AWS / Render)

---

## 👨‍💻 Author

Built as a full-stack authentication system to demonstrate:

* Backend engineering
* Secure auth flows
* Database integration
* Frontend UX

---

## 📜 License

MIT License
