from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_from_directory
)

from werkzeug.utils import secure_filename
from extensions import db
from database.models import UploadedFile
from forms.forms import EmptyForm
from security.logger import log_security_event

import os

upload = Blueprint("upload", __name__)

UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "txt"
}


def allowed_file(filename):

    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ==========================
# Upload File
# ==========================

@upload.route("/upload", methods=["GET", "POST"])
def upload_file():

    if "user_id" not in session:

        flash("Please login first.", "warning")

        return redirect(url_for("auth.login"))

    form = EmptyForm()

    if form.validate_on_submit():

        if "file" not in request.files:

            flash("No file selected.", "danger")

            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":

            flash("Please choose a file.", "warning")

            return redirect(request.url)

        if not allowed_file(file.filename):

            flash("File type not allowed!", "danger")

            return redirect(request.url)

        filename = secure_filename(file.filename)

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        filepath = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        file.save(filepath)

        uploaded = UploadedFile(

            filename=filename,

            filepath=filepath,

            user_id=session["user_id"]

        )

        db.session.add(uploaded)
        db.session.commit()

        # Security Log
        log_security_event(
            session["user_id"],
            f"Uploaded File: {filename}",
            request.remote_addr
        )

        flash("File uploaded successfully!", "success")

        return redirect(url_for("upload.upload_file"))

    files = UploadedFile.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "upload.html",
        files=files,
        form=form
    )


# ==========================
# Download File
# ==========================

@upload.route("/download/<int:file_id>")
def download_file(file_id):

    if "user_id" not in session:

        flash("Please login first.", "warning")

        return redirect(url_for("auth.login"))

    file = UploadedFile.query.filter_by(
        id=file_id,
        user_id=session["user_id"]
    ).first()

    if not file:

        flash("File not found.", "danger")

        return redirect(url_for("upload.upload_file"))

    # Security Log
    log_security_event(
        session["user_id"],
        f"Downloaded File: {file.filename}",
        request.remote_addr
    )

    return send_from_directory(
        UPLOAD_FOLDER,
        file.filename,
        as_attachment=True
    )


# ==========================
# Delete File
# ==========================

@upload.route("/delete-file/<int:file_id>", methods=["POST"])
def delete_file(file_id):

    if "user_id" not in session:

        flash("Please login first.", "warning")

        return redirect(url_for("auth.login"))

    form = EmptyForm()

    if not form.validate_on_submit():

        flash("Invalid CSRF Token.", "danger")

        return redirect(url_for("upload.upload_file"))

    file = UploadedFile.query.filter_by(
        id=file_id,
        user_id=session["user_id"]
    ).first()

    if not file:

        flash("File not found.", "danger")

        return redirect(url_for("upload.upload_file"))

    # Save filename before deleting
    filename = file.filename

    if os.path.exists(file.filepath):

        os.remove(file.filepath)

    db.session.delete(file)
    db.session.commit()

    # Security Log
    log_security_event(
        session["user_id"],
        f"Deleted File: {filename}",
        request.remote_addr
    )

    flash("File deleted successfully.", "info")

    return redirect(url_for("upload.upload_file"))