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
    SMTP_HOST = "smtp.email.com"
    SMTP_PORT = 587
    SMTP_USERNAME = "youremail@email.com"
    SMTP_PASSWORD = "your_app_password"
    SMTP_FROM_EMAIL = "youremail@email.com"

    # Other useful configurations

    # Route Redirects (For HTML pages these MUST be in dir/templates/*.html - unless auth)
    LOGIN_REDIRECT = "home" # Must have a route defined
    LOGOUT_REDIRECT = "auth/login"
    RESET_PASSWORD_REDIRECT = "auth.show_login"
    REGISTER_REDIRECT = "verify_email" # Must have a route defined
    VERIFY_EMAIL_REDIRECT = "login" # Must have a route defined

    # UI Configuration
    LOGIN_BANNER = "Welcome Back"
    LOGIN_BANNER_MSG = "Login to your account"
    REGISTER_BANNER = "Create Account"
    REGISTER_BANNER_MSG = "Register to get started"
    AUTH_CUSTOM_CSS = "custom.css" # Must live inside of a static folder

    # Auth configuration
    PASSWORD_RESET_TOKEN_EXPIRY = 3600  # seconds
    AUTH_ENABLE_RATE_LIMITS = True
    AUTH_RATE_LIMIT_STORAGE_URI = "memory://"

    AUTH_LOGIN_RATE_LIMIT = "5 per minute"
    AUTH_FORGOT_PASSWORD_RATE_LIMIT = "3 per 10 minutes"
    AUTH_RESEND_CODE_RATE_LIMIT = "3 per 10 minutes"
    AUTH_VERIFY_EMAIL_RATE_LIMIT = "5 per 10 minutes"
    
    # Dev mode:
    # True  -> print verification code & reset link in terminal instead of sending email
    # False -> actually send email through SMTP
    USE_TERMINAL_EMAIL = True