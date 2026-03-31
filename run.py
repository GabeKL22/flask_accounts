from flask import Flask, redirect, session, url_for
from flask_accounts import init_auth

class Config:
    # Flask
    SECRET_KEY = "change-me-to-a-random-secret-key"

    # PostgreSQL
    DB_HOST = "localhost"
    DB_NAME = "accountdb"
    DB_USER = "accountuser"
    DB_PASSWORD = "mypassword"

    # SMTP (used later when you want real email sending)
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USERNAME = "youremail@gmail.com"
    SMTP_PASSWORD = "your_app_password"
    SMTP_FROM_EMAIL = "youremail@gmail.com"

    # Other useful configurations
    LOGIN_REDIRECT = "search" # Must have a route defined
    LOGIN_BANNER = "Welcome Back"
    LOGIN_BANNER_MSG = "Login to your account"
    REGISTER_BANNER = "Create Account"
    REGISTER_BANNER_MSG = "Register to get started"
    CSS_STYLE_FILE = ""

    # Dev mode:
    # True  -> print verification code in terminal instead of sending email
    # False -> actually send email through SMTP
    USE_TERMINAL_EMAIL = True


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_auth(app)

    @app.route("/")
    def index():
        if "user_id" not in session:
            return redirect(url_for("auth.show_login"))
        return redirect(url_for("search"))

    @app.route("/search")
    def search():
        if "user_id" not in session:
            return redirect(url_for("auth.show_login"))
        return "Search page works"

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
