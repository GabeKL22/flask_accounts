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

    # Other useful configurations
    LOGIN_REDIRECT = "home" # Must have a route defined
    REGISTER_REDIRECT = "verify_email" # Must have a route defined
    VERIFY_EMAIL_REDIRECT = "login" # Must have a route defined
    LOGIN_BANNER = "Welcome Back"
    LOGIN_BANNER_MSG = "Login to your account"
    REGISTER_BANNER = "Create Account"
    REGISTER_BANNER_MSG = "Register to get started"
    AUTH_CUSTOM_CSS = "custom.css" # Must live inside of a static folder

    # Dev mode:
    # True  -> print verification code in terminal instead of sending email
    # False -> actually send email through SMTP
    USE_TERMINAL_EMAIL = True