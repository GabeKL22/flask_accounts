import random
import smtplib
from email.mime.text import MIMEText
from flask import current_app

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(to_email, code):
    if current_app.config["USE_TERMINAL_EMAIL"]:
        print(f"[DEV] Verification code for {to_email}: {code}")
        return

    subject = "Your Verification Code"
    body = f"Your verification code is: {code}"

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