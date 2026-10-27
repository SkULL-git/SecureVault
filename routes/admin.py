from datetime import datetime, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from sqlalchemy import or_

from database.models import Note, SecurityLog, UploadedFile, User
from extensions import db
from forms.forms import EmptyForm
from security.logger import log_security_event

admin = Blueprint("admin", __name__, url_prefix="/admin")


def require_admin():
    """Resolve the current account from the database on every admin request."""
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login first.", "warning")
        return None
    user = db.session.get(User, user_id)
    if not user or not user.is_active:
        session.clear()
        flash("Your session is no longer valid.", "warning")
        return None
    if user.role != "admin":
        abort(403)
    return user


@admin.route("/")
def dashboard():
    current_admin = require_admin()
    if current_admin is None:
        return redirect(url_for("auth.login"))

    since_7_days = datetime.utcnow() - timedelta(days=7)
    recent_logs = SecurityLog.query.order_by(SecurityLog.created_at.desc()).limit(12).all()
    return render_template(
        "admin/dashboard.html",
        admin_user=current_admin,
        total_users=User.query.count(),
        active_users=User.query.filter_by(is_active=True).count(),
        disabled_users=User.query.filter_by(is_active=False).count(),
        total_notes=Note.query.count(),
        total_files=UploadedFile.query.count(),
        total_events=SecurityLog.query.count(),
        recent_logins=SecurityLog.query.filter(
            SecurityLog.action == "User Logged In",
            SecurityLog.created_at >= since_7_days
        ).count(),
        recent_logs=recent_logs,
    )


@admin.route("/users")
def users():
    current_admin = require_admin()
    if current_admin is None:
        return redirect(url_for("auth.login"))

    query = request.args.get("q", "").strip()
    users_query = User.query
    if query:
        like = f"%{query}%"
        users_query = users_query.filter(or_(User.name.ilike(like), User.email.ilike(like)))
    user_rows = users_query.order_by(User.created_at.desc()).limit(200).all()
    form = EmptyForm()
    return render_template(
        "admin/users.html",
        admin_user=current_admin,
        users=user_rows,
        query=query,
        form=form,
    )


@admin.route("/users/<int:user_id>/toggle-active", methods=["POST"])
def toggle_active(user_id):
    current_admin = require_admin()
    if current_admin is None:
        return redirect(url_for("auth.login"))
    form = EmptyForm()
    if not form.validate_on_submit():
        abort(400)

    target = db.session.get(User, user_id)
    if not target:
        abort(404)
    if target.id == current_admin.id:
        flash("You cannot disable your own account.", "warning")
        return redirect(url_for("admin.users"))

    if target.is_active and target.role == "admin":
        active_admins = User.query.filter_by(role="admin", is_active=True).count()
        if active_admins <= 1:
            flash("The last active administrator cannot be disabled.", "danger")
            return redirect(url_for("admin.users"))

    target.is_active = not target.is_active
    db.session.commit()
    log_security_event(
        current_admin.id,
        f"Admin {'enabled' if target.is_active else 'disabled'} account for user ID {target.id}",
        request.remote_addr or "unknown",
    )
    flash(f"Account for {target.email} is now {'active' if target.is_active else 'disabled'}.", "success")
    return redirect(url_for("admin.users", q=request.args.get("q", "")))


@admin.route("/users/<int:user_id>/toggle-role", methods=["POST"])
def toggle_role(user_id):
    current_admin = require_admin()
    if current_admin is None:
        return redirect(url_for("auth.login"))
    form = EmptyForm()
    if not form.validate_on_submit():
        abort(400)

    target = db.session.get(User, user_id)
    if not target:
        abort(404)
    if target.id == current_admin.id:
        flash("You cannot change your own administrator role.", "warning")
        return redirect(url_for("admin.users"))

    if target.role == "admin":
        active_admins = User.query.filter_by(role="admin", is_active=True).count()
        if target.is_active and active_admins <= 1:
            flash("The last active administrator cannot be demoted.", "danger")
            return redirect(url_for("admin.users"))
        target.role = "user"
        action = "demoted"
    else:
        target.role = "admin"
        action = "promoted"

    db.session.commit()
    log_security_event(
        current_admin.id,
        f"Admin {action} user ID {target.id} {'to administrator' if action == 'promoted' else 'to standard user'}",
        request.remote_addr or "unknown",
    )
    flash(f"Role updated for {target.email}.", "success")
    return redirect(url_for("admin.users", q=request.args.get("q", "")))


@admin.route("/security")
def security():
    current_admin = require_admin()
    if current_admin is None:
        return redirect(url_for("auth.login"))
    logs = SecurityLog.query.order_by(SecurityLog.created_at.desc()).limit(250).all()
    return render_template("admin/security.html", admin_user=current_admin, logs=logs)
