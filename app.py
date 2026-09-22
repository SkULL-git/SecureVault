from flask import Flask, redirect, url_for, session, render_template

from config import Config
from extensions import db, bcrypt, jwt, csrf

from routes.auth import auth
from routes.notes import notes
from routes.upload import upload
from routes.logs import logs
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
app.config.from_object(Config)

# ==========================
# Initialize Extensions
# ==========================

db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)
csrf.init_app(app)

# ==========================
# Register Blueprints
# ==========================

app.register_blueprint(auth)
app.register_blueprint(notes)
app.register_blueprint(upload)
app.register_blueprint(logs)

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
        "style-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com 'unsafe-inline'; "
        "script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com 'unsafe-inline'; "
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

    return render_template(
        "404.html"
    ), 404


@app.errorhandler(403)
def forbidden(error):

    return render_template(
        "403.html"
    ), 403


@app.errorhandler(500)
def internal_server_error(error):

    db.session.rollback()

    return render_template(
        "500.html"
    ), 500

@app.errorhandler(RequestEntityTooLarge)
def file_too_large(error):

    return (
        render_template(
            "413.html"
        ),
        413
    )


# ==========================
# Create Database Tables
# ==========================

with app.app_context():

    from database.models import (
        User,
        Note,
        UploadedFile,
        SecurityLog
    )

    db.create_all()

    # SQLite migration for databases created by the previous SecureVault version.
    # SQLAlchemy create_all() does not add columns to existing tables.
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):

        from sqlalchemy import inspect, text

        inspector = inspect(db.engine)

        user_columns = {
            column["name"]
            for column in inspector.get_columns("users")
        }

        file_columns = {
            column["name"]
            for column in inspector.get_columns("uploaded_files")
        }

        with db.engine.begin() as connection:

            if "recovery_key_hash" not in user_columns:

                connection.execute(
                    text(
                        "ALTER TABLE users "
                        "ADD COLUMN recovery_key_hash VARCHAR(255)"
                    )
                )

            if "encrypted" not in file_columns:

                connection.execute(
                    text(
                        "ALTER TABLE uploaded_files "
                        "ADD COLUMN encrypted BOOLEAN NOT NULL DEFAULT 0"
                    )
                )


# ==========================
# Run Application
# ==========================

if __name__ == "__main__":

    app.run(debug=True)

