from flask import Flask
from app.config import Config

def create_app():
    app = Flask(__name__, template_folder="../templates")
    app.config.from_object(Config)

    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app