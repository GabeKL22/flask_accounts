from flask import Blueprint

auth_bp = Blueprint(
    "auth",
    __name__,
    template_folder="templates"
)

def init_auth(app):
    app.register_blueprint(auth_bp, url_prefix="/auth")

# Import routes AFTER blueprint is created
from . import routes