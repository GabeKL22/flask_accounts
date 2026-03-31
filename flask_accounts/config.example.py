# DO NOT COMMIT REAL SECRETS TO GIT

class Config:
    # Flask
    SECRET_KEY = "change-me-to-a-random-secret-key"

    # PostgreSQL
    DB_HOST = "localhost"
    DB_NAME = "accountdb"
    DB_USER = "your_db_username"
    DB_PASSWORD = "your_db_password"

    # SMTP (used later when you want real email sending)
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USERNAME = "youremail@gmail.com"
    SMTP_PASSWORD = "your_app_password"
    SMTP_FROM_EMAIL = "youremail@gmail.com"

    # Dev mode:
    # True  -> print verification code in terminal instead of sending email
    # False -> actually send email through SMTP
    USE_TERMINAL_EMAIL = True