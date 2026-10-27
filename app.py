from flask import Flask, redirect, url_for, session, render_template
from werkzeug.exceptions import RequestEntityTooLarge

from config import Config
from extensions import db, bcrypt, jwt, csrf, migrate

from routes.auth import auth
from routes.notes import notes
from routes.upload import upload
from routes.logs import logs
from routes.admin import admin


app = Flask(__name__)
app.config.from_object(Config)


# ==========================
# Initialize Extensions
# ==========================

db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)
csrf.init_app(app)
migrate.init_app(app, db)


# ==========================
# Register Blueprints
# ==========================

app.register_blueprint(auth)
app.register_blueprint(notes)
app.register_blueprint(upload)
app.register_blueprint(logs)
app.register_blueprint(admin)


# ==========================
# Security Headers
# ==========================

@app.after_request
def add_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' https://cdn.jsdelivr.net "
        "https://cdnjs.cloudflare.com 'unsafe-inline'; "
        "script-src 'self' https://cdn.jsdelivr.net "
        "https://cdnjs.cloudflare.com 'unsafe-inline'; "
        "font-src 'self' https://cdnjs.cloudflare.com; "
        "img-src 'self' data:;"
    )

    return response


# ==========================
# Home Route
# ==========================

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("auth.dashboard"))

    return redirect(url_for("auth.login"))


# ==========================
# Error Handlers
# ==========================

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(403)
def forbidden(error):
    return render_template("403.html"), 403


@app.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template("500.html"), 500


@app.errorhandler(RequestEntityTooLarge)
def file_too_large(error):
    return render_template("413.html"), 413


# ==========================
# Database Schema Management
# ==========================
# Database tables and schema changes must be managed explicitly
# through reviewed Flask-Migrate migrations.
# Do not call db.create_all() or alter tables automatically here.


# ==========================
# Run Application
# ==========================

if __name__ == "__main__":
    app.run(debug=True)