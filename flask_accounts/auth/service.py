import random
import smtplib
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(to_email, code):
    if current_app.config["USE_TERMINAL_EMAIL"]:
        print(f"[DEV] Verification code for {to_email}: {code}")
        return

    subject = "Your Verification Code"
    body = f"Your verification code is: {code}"

    send_email(to_email, subject, body)

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = current_app.config["SMTP_FROM_EMAIL"]
    msg["To"] = to_email

    server = smtplib.SMTP(
        current_app.config["SMTP_HOST"],
        current_app.config["SMTP_PORT"]
    )
    server.starttls()
    server.login(
        current_app.config["SMTP_USERNAME"],
        current_app.config["SMTP_PASSWORD"]
    )
    server.send_message(msg)
    server.quit()

def send_password_reset_email_message(to_email, subject, body):
    if current_app.config.get("USE_TERMINAL_EMAIL", False):
        print("\n=== EMAIL (DEV MODE) ===")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print("========================\n")
        return
    send_email(to_email, subject, body)
    

def get_reset_serializer():
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
        salt="password-reset"
    )

def generate_password_reset_token(user_id: int, email: str) -> str:
    serializer = get_reset_serializer()
    return serializer.dumps({
        "user_id": user_id,
        "email": email,
        "purpose": "password-reset",
    })

def verify_password_reset_token(token: str):
    serializer = get_reset_serializer()
    max_age = current_app.config.get("PASSWORD_RESET_TOKEN_EXPIRY", 3600)

    try:
        data = serializer.loads(token, max_age=max_age)
    except SignatureExpired:
        return None, "expired"
    except BadSignature:
        return None, "invalid"

    if data.get("purpose") != "password-reset":
        return None, "invalid"

    return data, None