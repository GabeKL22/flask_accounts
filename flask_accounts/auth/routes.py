from datetime import datetime, timedelta

from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash

from flask_accounts.auth import auth_bp
from flask_accounts.auth.service import generate_verification_code, send_verification_email, verify_password_reset_token, generate_password_reset_token, send_password_reset_email_message
from flask_accounts.auth.session import login_user, logout_user
from flask_accounts.auth.validators import is_valid_password
from flask_accounts.db import get_db_connection

def css_style():
    custom_css = current_app.config.get("AUTH_CUSTOM_CSS")
    auth_custom_css = None

    if custom_css:
        auth_custom_css = url_for("static", filename=custom_css)
    return auth_custom_css

@auth_bp.route("/")
def home():
    return redirect(url_for("auth.show_login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def show_register():
    if request.method == "GET":
        return render_template("auth/register.html", register_banner=current_app.config.get("REGISTER_BANNER", "Create Account"), register_banner_msg=current_app.config.get("REGISTER_BANNER_MSG", "Register to get started"), auth_custom_css=css_style())

    firstname = request.form.get("firstname", "").strip()
    lastname = request.form.get("lastname", "").strip()
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not firstname or not lastname or not username or not email or not password or not confirm_password:
        flash("All fields are required.", "error")
        return redirect(url_for("auth.show_register"))

    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return redirect(url_for("auth.show_register"))

    password_ok, password_message = is_valid_password(password)
    if not password_ok:
        flash(password_message, "error")
        return redirect(url_for("auth.show_register"))

    verification_code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    password_hash = generate_password_hash(password)

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            SELECT id
            FROM users
            WHERE username = %s OR email = %s
            """,
            (username, email),
        )

        existing_user = cur.fetchone()

        if existing_user:
            flash("Username or email already exists.", "error")
            return redirect(url_for("auth.show_register"))

        cur.execute(
            """
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
            """,
            (
                firstname,
                lastname,
                username,
                email,
                password_hash,
                False,
                verification_code,
                expires_at,
            ),
        )

        conn.commit()

        send_verification_email(email, verification_code)
        session["pending_verification_email"] = email

        if current_app.config["USE_TERMINAL_EMAIL"]:
            flash("Account created. Check terminal for verification code.", "success")
        else:
            flash("Account created. Check your email for the verification code.", "success")

        return redirect(url_for("auth.verify_email"))

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Registration error: {e}", "error")
        return redirect(url_for("auth.show_register"))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@auth_bp.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    email = session.get("pending_verification_email")

    if not email:
        flash("No email awaiting verification. Please register first.", "error")
        return redirect(url_for("auth.show_register"))

    if request.method == "GET":
        return render_template("auth/verify_email.html", email=email, auth_custom_css=css_style())

    code = request.form.get("verification_code", "").strip()

    if not code:
        flash("Verification code is required.", "error")
        return redirect(url_for("auth.verify_email"))

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            SELECT id, verification_code, verification_expires_at, email_verified
            FROM users
            WHERE email = %s
            """,
            (email,),
        )

        user = cur.fetchone()

        if not user:
            flash("User not found.", "error")
            return redirect(url_for("auth.show_register"))

        if user["email_verified"]:
            flash("Email already verified. Please log in.", "success")
            session.pop("pending_verification_email", None)
            return redirect(url_for("auth.show_login"))

        if user["verification_code"] != code:
            flash("Invalid verification code.", "error")
            return redirect(url_for("auth.verify_email"))

        expires_at = user["verification_expires_at"]
        now_utc = datetime.utcnow()

        if expires_at is None or now_utc > expires_at:
            flash("Verification code expired. Please request a new one.", "error")
            return redirect(url_for("auth.verify_email"))

        cur.execute(
            """
            UPDATE users
            SET email_verified = TRUE,
                verification_code = NULL,
                verification_expires_at = NULL
            WHERE email = %s
            """,
            (email,),
        )

        conn.commit()
        session.pop("pending_verification_email", None)

        flash("Email verified successfully. You can now log in.", "success")
        return redirect(url_for("auth.show_login"))

    except Exception as e:
        flash(f"Verification error: {e}", "error")
        return redirect(url_for("auth.verify_email"))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@auth_bp.route("/login", methods=["GET", "POST"])
def show_login():
    if request.method == "GET":
        return render_template("auth/login.html", login_banner=current_app.config.get("LOGIN_BANNER", "Welcome Back"), login_banner_msg=current_app.config.get("LOGIN_BANNER_MSG", "Login to your account"), auth_custom_css=css_style())

    username_or_email = request.form.get("username_or_email", "").strip()
    password = request.form.get("password", "")

    if not username_or_email or not password:
        flash("Username/email and password are required.", "error")
        return redirect(url_for("auth.show_login"))

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            SELECT id, firstname, lastname, username, email, password_hash, email_verified
            FROM users
            WHERE username = %s OR email = %s
            """,
            (username_or_email, username_or_email),
        )

        user = cur.fetchone()

        if not user:
            flash("User does not exist.", "error")
            return redirect(url_for("auth.show_login"))

        if not check_password_hash(user["password_hash"], password):
            flash("Invalid password.", "error")
            return redirect(url_for("auth.show_login"))

        if not user["email_verified"]:
            session["pending_verification_email"] = user["email"]
            flash("Please verify your email before logging in.", "error")
            return redirect(url_for("auth.verify_email"))

        login_user(user)

        flash("Logged in successfully.", "success")
        redirect_target = current_app.config.get("LOGIN_REDIRECT", "/")

        if redirect_target.startswith("/"):
            return redirect(redirect_target)

        return redirect(url_for(redirect_target))

    except Exception as e:
        flash(f"Login error: {e}", "error")
        return redirect(url_for("auth.show_login"))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@auth_bp.app_context_processor
def inject_auth_helpers():
    return {
        "logout_url": lambda: url_for("auth.logout")
    }

@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()

    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.show_login"))


@auth_bp.route("/resend-code", methods=["POST"])
def resend_code():
    email = session.get("pending_verification_email")

    if not email:
        flash("No email awaiting verification.", "error")
        return redirect(url_for("auth.show_register"))

    new_code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            UPDATE users
            SET verification_code = %s,
                verification_expires_at = %s
            WHERE email = %s
            """,
            (new_code, expires_at, email),
        )

        conn.commit()
        send_verification_email(email, new_code)

        if current_app.config["USE_TERMINAL_EMAIL"]:
            flash("A new code was generated. Check terminal.", "success")
        else:
            flash("A new code was sent to your email.", "success")

        return redirect(url_for("auth.verify_email"))

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Could not resend code: {e}", "error")
        return redirect(url_for("auth.verify_email"))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, email FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        # Always return the same message to avoid email enumeration
        flash("If an account with that email exists, a reset link has been sent.", "info")

        if user:
            user_id, user_email = user
            token = generate_password_reset_token(user_id, user_email)
            reset_url = url_for("auth.reset_password", token=token, _external=True)

            send_password_reset_email_message(
                to_email=user_email,
                subject="Reset your password",
                body=f"Click this link to reset your password:\n\n{reset_url}\n\n"
                     f"This link will expire in "
                     f"{current_app.config.get('PASSWORD_RESET_TOKEN_EXPIRY', 3600) // 60} minutes."
            )

        return redirect(url_for("auth.forgot_password"))

    return render_template("auth/forgot_password.html")

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    data, error = verify_password_reset_token(token)

    if error == "expired":
        flash("This password reset link has expired.", "error")
        return redirect(url_for("auth.forgot_password"))

    if error == "invalid":
        flash("This password reset link is invalid.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        valid, error = is_valid_password(password)
        if not valid:
            flash(error, "error")
            return render_template("auth/reset_password.html", token=token)

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("auth/reset_password.html", token=token)

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, email FROM users WHERE id = %s",
            (data["user_id"],)
        )
        user = cur.fetchone()

        if not user or user[1].lower() != data["email"].lower():
            cur.close()
            conn.close()
            flash("This password reset link is invalid.", "error")
            return redirect(url_for("auth.forgot_password"))

        new_hash = generate_password_hash(password)

        cur.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (new_hash, data["user_id"])
        )
        conn.commit()

        cur.close()
        conn.close()

        flash("Your password has been reset. You can now log in.", "success")
        return redirect(url_for(current_app.config.get("RESET_PASSWORD_REDIRECT", "auth.show_login")))

    return render_template("auth/reset_password.html", token=token)