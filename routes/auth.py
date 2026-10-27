from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from extensions import db, bcrypt
from forms.forms import EmptyForm
from security.logger import log_security_event
from database.models import User, Note, UploadedFile, SecurityLog

from datetime import datetime, timedelta
import secrets


auth = Blueprint("auth", __name__)


def generate_recovery_key():
    """Generate a high-entropy recovery key."""
    return "SV-" + secrets.token_urlsafe(24)


def set_new_password(user, new_password):
    user.password = bcrypt.generate_password_hash(
        new_password
    ).decode("utf-8")

    user.failed_login_attempts = 0
    user.account_locked_until = None


# =========================
# Register
# =========================

@auth.route("/register", methods=["GET", "POST"])
def register():

    if "user_id" in session:
        return redirect(url_for("auth.dashboard"))

    form = EmptyForm()

    if form.validate_on_submit():

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "warning")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash(
                "Password must be at least 6 characters long.",
                "warning"
            )
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            flash(
                "Email already registered!",
                "danger"
            )
            return redirect(url_for("auth.register"))

        recovery_key = generate_recovery_key()

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        recovery_key_hash = bcrypt.generate_password_hash(
            recovery_key
        ).decode("utf-8")

        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            recovery_key_hash=recovery_key_hash
        )

        db.session.add(new_user)
        db.session.commit()

        log_security_event(
            new_user.id,
            "User Registered",
            request.remote_addr
        )

        # The plaintext recovery key is shown once.
        return render_template(
            "recovery_key.html",
            recovery_key=recovery_key,
            email=email,
            regenerated=False
        )

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

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if user and not user.is_active:
            flash("This account has been disabled. Contact an administrator.", "danger")
            return redirect(url_for("auth.login"))

        if user and user.account_locked_until:

            if datetime.utcnow() < user.account_locked_until:

                remaining = int(
                    (
                        user.account_locked_until
                        - datetime.utcnow()
                    ).total_seconds() // 60
                ) + 1

                flash(
                    f"Account is locked. Try again in {remaining} minute(s).",
                    "danger"
                )

                return redirect(url_for("auth.login"))

            user.failed_login_attempts = 0
            user.account_locked_until = None
            db.session.commit()

            log_security_event(
                user.id,
                "Account Unlocked",
                request.remote_addr
            )

        if user and bcrypt.check_password_hash(
            user.password,
            password
        ):

            user.failed_login_attempts = 0
            user.account_locked_until = None
            user.last_login = datetime.utcnow()
            user.last_login_ip = request.remote_addr

            db.session.commit()

            session.clear()
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["role"] = user.role

            log_security_event(
                user.id,
                "User Logged In",
                request.remote_addr
            )

            flash(
                f"Welcome back, {user.name}!",
                "success"
            )

            return redirect(
                url_for("auth.dashboard")
            )

        if user:

            user.failed_login_attempts += 1

            log_security_event(
                user.id,
                "Failed Login Attempt",
                request.remote_addr
            )

            remaining = 5 - user.failed_login_attempts

            if user.failed_login_attempts >= 5:

                user.account_locked_until = (
                    datetime.utcnow()
                    + timedelta(minutes=5)
                )

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

                return redirect(
                    url_for("auth.login")
                )

            db.session.commit()

            flash(
                f"Invalid password. {remaining} attempt(s) remaining.",
                "warning"
            )

            return redirect(
                url_for("auth.login")
            )

        flash(
            "Invalid Email or Password!",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "login.html",
        form=form
    )


# =========================
# Forgot Password
# =========================

@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if "user_id" in session:
        return redirect(url_for("auth.dashboard"))

    form = EmptyForm()

    if form.validate_on_submit():

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        recovery_key = request.form.get(
            "recovery_key",
            ""
        ).strip()

        user = User.query.filter_by(
            email=email
        ).first()

        if (
            not user
            or not user.recovery_key_hash
        ):
            flash(
                "Invalid recovery details.",
                "danger"
            )

            return redirect(
                url_for("auth.forgot_password")
            )

        if not bcrypt.check_password_hash(
            user.recovery_key_hash,
            recovery_key
        ):

            log_security_event(
                user.id,
                "Failed Recovery Attempt",
                request.remote_addr
            )

            flash(
                "Invalid recovery details.",
                "danger"
            )

            return redirect(
                url_for("auth.forgot_password")
            )

        # Store only the user ID in the temporary recovery session.
        session["recovery_user_id"] = user.id

        return redirect(
            url_for("auth.reset_password")
        )

    return render_template(
        "forgot_password.html",
        form=form
    )


# =========================
# Reset Password
# =========================

@auth.route("/reset-password", methods=["GET", "POST"])
def reset_password():

    user_id = session.get(
        "recovery_user_id"
    )

    if not user_id:
        flash(
            "Start the recovery process first.",
            "warning"
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        session.pop(
            "recovery_user_id",
            None
        )

        flash(
            "Invalid recovery session.",
            "danger"
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    form = EmptyForm()

    if form.validate_on_submit():

        new_password = request.form.get(
            "new_password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if len(new_password) < 6:
            flash(
                "New password must be at least 6 characters.",
                "warning"
            )

            return redirect(
                url_for("auth.reset_password")
            )

        if new_password != confirm_password:
            flash(
                "Passwords do not match.",
                "warning"
            )

            return redirect(
                url_for("auth.reset_password")
            )

        if bcrypt.check_password_hash(
            user.password,
            new_password
        ):

            flash(
                "New password cannot be the same as the current password.",
                "warning"
            )

            return redirect(
                url_for("auth.reset_password")
            )

        set_new_password(
            user,
            new_password
        )

        db.session.commit()

        session.pop(
            "recovery_user_id",
            None
        )

        log_security_event(
            user.id,
            "Password Recovered Using Recovery Key",
            request.remote_addr
        )

        flash(
            "Password reset successfully. Please login.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "reset_password.html",
        form=form
    )


# =========================
# Recovery Key Management
# =========================

@auth.route("/recovery-key", methods=["GET", "POST"])
def recovery_key():

    if "user_id" not in session:
        flash(
            "Please login first.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )

    form = EmptyForm()

    if form.validate_on_submit():

        current_password = request.form.get(
            "current_password",
            ""
        )

        user = db.session.get(
            User,
            session["user_id"]
        )

        if (
            not user
            or not bcrypt.check_password_hash(
                user.password,
                current_password
            )
        ):
            flash(
                "Current password is incorrect.",
                "danger"
            )

            return redirect(
                url_for("auth.recovery_key")
            )

        new_recovery_key = generate_recovery_key()

        user.recovery_key_hash = (
            bcrypt.generate_password_hash(
                new_recovery_key
            ).decode("utf-8")
        )

        db.session.commit()

        log_security_event(
            user.id,
            "Recovery Key Generated",
            request.remote_addr
        )

        return render_template(
            "recovery_key.html",
            recovery_key=new_recovery_key,
            email=user.email,
            regenerated=True
        )

    return render_template(
        "recovery_key.html",
        recovery_key=None,
        form=form,
        regenerated=False
    )


# =========================
# Dashboard
# =========================

@auth.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        flash(
            "Please login first.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )

    user = User.query.get(
        session.get("user_id")
    )

    if not user:
        session.clear()

        flash(
            "Session expired. Please login again.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "dashboard.html",
        user_name=user.name,
        total_notes=Note.query.filter_by(
            user_id=user.id
        ).count(),
        total_files=UploadedFile.query.filter_by(
            user_id=user.id
        ).count(),
        total_logs=SecurityLog.query.filter_by(
            user_id=user.id
        ).count(),
        member_since=user.created_at.strftime(
            "%d %b %Y"
        )
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

    flash(
        "Logged out successfully.",
        "info"
    )

    return redirect(
        url_for("auth.login")
    )


# =========================
# Change Password
# =========================

@auth.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "user_id" not in session:
        flash(
            "Please login first.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )

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

        user = db.session.get(
            User,
            session["user_id"]
        )

        if (
            not user
            or not bcrypt.check_password_hash(
                user.password,
                current_password
            )
        ):

            flash(
                "Current password is incorrect.",
                "danger"
            )

            return redirect(
                url_for("auth.change_password")
            )

        if len(new_password) < 6:

            flash(
                "New password must be at least 6 characters.",
                "warning"
            )

            return redirect(
                url_for("auth.change_password")
            )

        if new_password != confirm_password:

            flash(
                "Passwords do not match.",
                "warning"
            )

            return redirect(
                url_for("auth.change_password")
            )

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

        set_new_password(
            user,
            new_password
        )

        db.session.commit()

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
