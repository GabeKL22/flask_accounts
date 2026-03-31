from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from app.config import Config
import random
import re

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config["SECRET_KEY"]

MIN_PASSWORD_LENGTH = 8


def get_db_connection():
    return psycopg2.connect(
        host=app.config["DB_HOST"],
        dbname=app.config["DB_NAME"],
        user=app.config["DB_USER"],
        password=app.config["DB_PASSWORD"],
        cursor_factory=RealDictCursor
    )


def generate_verification_code():
    return f"{random.randint(0, 999999):06d}"


def is_valid_password(password):
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."

    if not re.search(r"[A-Z]", password):
        return False, "Password must include at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return False, "Password must include at least one lowercase letter."

    if not re.search(r"[0-9]", password):
        return False, "Password must include at least one number."

    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "Password must include at least one symbol."

    return True, ""


def send_verification_email(to_email, code):
    msg = EmailMessage()
    msg["Subject"] = "Your verification code"
    msg["From"] = app.config["SMTP_FROM_EMAIL"]
    msg["To"] = to_email
    msg.set_content(
        f"Your verification code is: {code}\n\n"
        "It expires in 10 minutes."
    )

    with smtplib.SMTP(app.config["SMTP_HOST"], app.config["SMTP_PORT"]) as server:
        server.starttls()
        server.login(app.config["SMTP_USERNAME"], app.config["SMTP_PASSWORD"])
        server.send_message(msg)


def send_verification_email_test(to_email, code):
    print(f"[DEV] Verification code for {to_email}: {code}")


def deliver_verification_code(to_email, code):
    if app.config["USE_TERMINAL_EMAIL"]:
        send_verification_email_test(to_email, code)
    else:
        send_verification_email(to_email, code)


@app.route("/")
def home():
    return redirect(url_for("show_login"))


@app.route("/register", methods=["GET", "POST"])
def show_register():
    if request.method == "GET":
        return render_template("register.html")

    firstname = request.form.get("firstname", "").strip()
    lastname = request.form.get("lastname", "").strip()
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not firstname or not lastname or not username or not email or not password or not confirm_password:
        flash("All fields are required.", "error")
        return redirect(url_for("show_register"))

    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return redirect(url_for("show_register"))

    password_ok, password_message = is_valid_password(password)
    if not password_ok:
        flash(password_message, "error")
        return redirect(url_for("show_register"))

    verification_code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    password_hash = generate_password_hash(password)

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id
            FROM users
            WHERE username = %s OR email = %s
        """, (username, email))

        existing_user = cur.fetchone()

        if existing_user:
            flash("Username or email already exists.", "error")
            return redirect(url_for("show_register"))

        cur.execute("""
            INSERT INTO users (
                firstname,
                lastname,
                username,
                email,
                password_hash,
                email_verified,
                verification_code,
                verification_expires_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            firstname,
            lastname,
            username,
            email,
            password_hash,
            False,
            verification_code,
            expires_at
        ))

        conn.commit()

        deliver_verification_code(email, verification_code)
        session["pending_verification_email"] = email

        if app.config["USE_TERMINAL_EMAIL"]:
            flash("Account created. Check terminal for verification code.", "success")
        else:
            flash("Account created. Check your email for the verification code.", "success")

        return redirect(url_for("verify_email"))

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Registration error: {e}", "error")
        return redirect(url_for("show_register"))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    email = session.get("pending_verification_email")

    if not email:
        flash("No email awaiting verification. Please register first.", "error")
        return redirect(url_for("show_register"))

    if request.method == "GET":
        return render_template("verify_email.html", email=email)

    code = request.form.get("verification_code", "").strip()

    if not code:
        flash("Verification code is required.", "error")
        return redirect(url_for("verify_email"))

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, verification_code, verification_expires_at, email_verified
            FROM users
            WHERE email = %s
        """, (email,))

        user = cur.fetchone()

        if not user:
            flash("User not found.", "error")
            return redirect(url_for("show_register"))

        if user["email_verified"]:
            flash("Email already verified. Please log in.", "success")
            return redirect(url_for("show_login"))

        if user["verification_code"] != code:
            flash("Invalid verification code.", "error")
            return redirect(url_for("verify_email"))

        expires_at = user["verification_expires_at"]
        now_utc = datetime.utcnow()

        if expires_at is None or now_utc > expires_at:
            flash("Verification code expired. Please request a new one.", "error")
            return redirect(url_for("verify_email"))

        cur.execute("""
            UPDATE users
            SET email_verified = TRUE,
                verification_code = NULL,
                verification_expires_at = NULL
            WHERE email = %s
        """, (email,))

        conn.commit()
        session.pop("pending_verification_email", None)

        flash("Email verified successfully. You can now log in.", "success")
        return redirect(url_for("show_login"))

    except Exception as e:
        flash(f"Verification error: {e}", "error")
        return redirect(url_for("verify_email"))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/login", methods=["GET", "POST"])
def show_login():
    if request.method == "GET":
        return render_template("login.html")

    username_or_email = request.form.get("username_or_email", "").strip()
    password = request.form.get("password", "")

    if not username_or_email or not password:
        flash("Username/email and password are required.", "error")
        return redirect(url_for("show_login"))

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, firstname, lastname, username, email, password_hash, email_verified
            FROM users
            WHERE username = %s OR email = %s
        """, (username_or_email, username_or_email))

        user = cur.fetchone()

        if not user:
            flash("User does not exist.", "error")
            return redirect(url_for("show_login"))

        if not check_password_hash(user["password_hash"], password):
            flash("Invalid password.", "error")
            return redirect(url_for("show_login"))

        if not user["email_verified"]:
            session["pending_verification_email"] = user["email"]
            flash("Please verify your email before logging in.", "error")
            return redirect(url_for("verify_email"))

        return f"Welcome, {user['firstname']} {user['lastname']}!"

    except Exception as e:
        flash(f"Login error: {e}", "error")
        return redirect(url_for("show_login"))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/resend-code", methods=["POST"])
def resend_code():
    email = session.get("pending_verification_email")

    if not email:
        flash("No email awaiting verification.", "error")
        return redirect(url_for("show_register"))

    new_code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE users
            SET verification_code = %s,
                verification_expires_at = %s
            WHERE email = %s
        """, (new_code, expires_at, email))

        conn.commit()
        deliver_verification_code(email, new_code)

        if app.config["USE_TERMINAL_EMAIL"]:
            flash("A new code was generated. Check terminal.", "success")
        else:
            flash("A new code was sent to your email.", "success")

        return redirect(url_for("verify_email"))

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Could not resend code: {e}", "error")
        return redirect(url_for("verify_email"))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)