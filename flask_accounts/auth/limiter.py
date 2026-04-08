from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request, redirect, url_for, flash # flashing and redirect on limits
from werkzeug.exceptions import TooManyRequests

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="memory://",  # good for local dev
)

def register_rate_limit_handler(app):

    @app.errorhandler(429)
    def handle_rate_limit(e: TooManyRequests):
        if request.path.endswith("/login"):
            flash("Too many login attempts. Try again shortly.", "error")
        elif request.path.endswith("/forgot-password"):
            flash("Too many reset attempts. Please wait before trying again.", "error")
        elif request.path.endswith("/verify-email"):
            flash("Too many verification attempts. Please wait before trying again.", "error")
        elif request.path.endswith("/resend-code"):
            flash("Too many code request attempts. Please wait before trying again.", "error")

        # Send user back to where they came from
        return redirect(request.referrer or url_for("auth.show_login"))