from flask import Blueprint
from .limiter import limiter, register_rate_limit_handler

auth_bp = Blueprint(
    "auth",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/auth/static"
)

def init_auth(app):
    app.register_blueprint(auth_bp, url_prefix="/auth")
    limiter.init_app(app)
    register_rate_limit_handler(app)
    register_cli_commands(app)

# Import routes AFTER blueprint is created
from . import routes
from .cli import register_cli_commands