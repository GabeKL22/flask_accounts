from flask import Flask, redirect, session, url_for
from app.config import Config
from app.auth import init_auth

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_auth(app)

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return redirect(url_for("auth.show_login"))

    @app.route("/dashboard")
    def dashboard():
        if "user_id" not in session:
            return redirect(url_for("auth.show_login"))
        return "Logged in successfully. Welcome to your dashboard."

    return app