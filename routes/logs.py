from flask import Blueprint, render_template, session, redirect, url_for, flash

from database.models import SecurityLog

logs = Blueprint("logs", __name__)


# ==========================
# Security Logs
# ==========================

@logs.route("/logs")
def security_logs():

    if "user_id" not in session:

        flash("Please login first.", "warning")

        return redirect(url_for("auth.login"))

    logs_data = SecurityLog.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        SecurityLog.created_at.desc()
    ).all()

    return render_template(
        "logs.html",
        logs=logs_data
    )