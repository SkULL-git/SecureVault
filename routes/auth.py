from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from extensions import db, bcrypt
from forms.forms import EmptyForm
from security.logger import log_security_event
from database.models import User, Note, UploadedFile, SecurityLog
from datetime import datetime, timedelta

auth = Blueprint("auth", __name__)


# =========================
# Register
# =========================

@auth.route("/register", methods=["GET", "POST"])
def register():

    # If already logged in
    if "user_id" in session:
        return redirect(url_for("auth.dashboard"))

    form = EmptyForm()

    if form.validate_on_submit():

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Validation
        if not name or not email or not password:
            flash("All fields are required.", "warning")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "warning")
            return redirect(url_for("auth.register"))

        # Check existing user
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered!", "danger")
            return redirect(url_for("auth.register"))

        # Hash Password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        # Create User
        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        # Security Log
        log_security_event(
            new_user.id,
            "User Registered",
            request.remote_addr
        )

        flash("Registration Successful! Please Login.", "success")

        return redirect(url_for("auth.login"))

    return render_template(
        "register.html",
        form=form
    )


# =========================
# Login
# =========================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("auth.dashboard"))

    form = EmptyForm()

    if form.validate_on_submit():

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        # =========================
        # Account Lock Check
        # =========================

        if user and user.account_locked_until:

            if datetime.utcnow() < user.account_locked_until:

                remaining = int(
                    (user.account_locked_until - datetime.utcnow()).total_seconds() // 60
                ) + 1

                flash(
                    f"Account is locked. Try again in {remaining} minute(s).",
                    "danger"
                )

                return redirect(url_for("auth.login"))

            else:

                user.failed_login_attempts = 0
                user.account_locked_until = None
                db.session.commit()

                log_security_event(
                    user.id,
                    "Account Unlocked",
                    request.remote_addr
                )

        # =========================
        # Successful Login
        # =========================

        if user and bcrypt.check_password_hash(user.password, password):

            user.failed_login_attempts = 0
            user.account_locked_until = None
            db.session.commit()

            session["user_id"] = user.id
            session["user_name"] = user.name

            log_security_event(
                user.id,
                "User Logged In",
                request.remote_addr
            )

            flash(
                f"Welcome back, {user.name}!",
                "success"
            )

            return redirect(url_for("auth.dashboard"))

        # =========================
        # Failed Login
        # =========================

        if user:

            user.failed_login_attempts += 1

            log_security_event(
                user.id,
                "Failed Login Attempt",
                request.remote_addr
            )

            remaining = 5 - user.failed_login_attempts

            if user.failed_login_attempts >= 5:

                user.account_locked_until = datetime.utcnow() + timedelta(minutes=5)

                log_security_event(
                    user.id,
                    "Account Locked",
                    request.remote_addr
                )

                db.session.commit()

                flash(
                    "Too many failed attempts. Account locked for 5 minutes.",
                    "danger"
                )

                return redirect(url_for("auth.login"))

            db.session.commit()

            flash(
                f"Invalid password. {remaining} attempt(s) remaining.",
                "warning"
            )

            return redirect(url_for("auth.login"))

        flash(
            "Invalid Email or Password!",
            "danger"
        )

        return redirect(url_for("auth.login"))

    return render_template(
        "login.html",
        form=form
    )


# =========================
# Dashboard
# =========================

@auth.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.get(session.get("user_id"))

    # Session exists but user no longer exists
    if not user:

        session.clear()

        flash("Session expired. Please login again.", "warning")

        return redirect(url_for("auth.login"))

    return render_template(
        "dashboard.html",
        user_name=user.name,
        total_notes=Note.query.filter_by(user_id=user.id).count(),
        total_files=UploadedFile.query.filter_by(user_id=user.id).count(),
        total_logs=SecurityLog.query.filter_by(user_id=user.id).count(),
        member_since=user.created_at.strftime("%d %b %Y")
    )


# =========================
# Logout
# =========================

@auth.route("/logout")
def logout():

    if "user_id" in session:

        log_security_event(
            session["user_id"],
            "User Logged Out",
            request.remote_addr
        )

    session.clear()

    flash("Logged out successfully.", "info")

    return redirect(url_for("auth.login"))


# =========================
# Change Password
# =========================

@auth.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "user_id" not in session:

        flash("Please login first.", "warning")

        return redirect(url_for("auth.login"))

    form = EmptyForm()

    if form.validate_on_submit():

        current_password = request.form.get(
            "current_password",
            ""
        )

        new_password = request.form.get(
            "new_password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        user = db.session.get(User, session["user_id"])

        # Verify current password

        if not bcrypt.check_password_hash(
            user.password,
            current_password
        ):

            flash(
                "Current password is incorrect.",
                "danger"
            )

            return redirect(
                url_for("auth.change_password")
            )

        # Password length

        if len(new_password) < 6:

            flash(
                "New password must be at least 6 characters.",
                "warning"
            )

            return redirect(
                url_for("auth.change_password")
            )

        # Confirm Password

        if new_password != confirm_password:

            flash(
                "Passwords do not match.",
                "warning"
            )

            return redirect(
                url_for("auth.change_password")
            )

        # Same Password Check

        if bcrypt.check_password_hash(
            user.password,
            new_password
        ):

            flash(
                "New password cannot be the same as the current password.",
                "warning"
            )

            return redirect(
                url_for("auth.change_password")
            )

        # Update Password

        user.password = bcrypt.generate_password_hash(
            new_password
        ).decode("utf-8")

        db.session.commit()

        # Security Log

        log_security_event(

            user.id,

            "Password Changed",

            request.remote_addr

        )

        flash(
            "Password updated successfully!",
            "success"
        )

        return redirect(
            url_for("auth.dashboard")
        )

    return render_template(

        "change_password.html",

        form=form

    )