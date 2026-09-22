from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file
)

from werkzeug.utils import secure_filename

from extensions import db
from database.models import UploadedFile
from forms.forms import EmptyForm
from security.logger import log_security_event
from security.encryption import encrypt_bytes, decrypt_bytes

import os
import io
import uuid


upload = Blueprint("upload", __name__)

UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "txt",
    "mp4",
    "mov",
    "avi",
    "mkv",
    "webm"
}


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def encrypted_disk_path(original_filename):
    extension = original_filename.rsplit(".", 1)[1].lower()
    return os.path.join(
        UPLOAD_FOLDER,
        f"{uuid.uuid4().hex}.{extension}.enc"
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

        original_filename = secure_filename(file.filename)

        if not original_filename or not allowed_file(original_filename):
            flash("File type not allowed!", "danger")
            return redirect(request.url)

        # MAX_CONTENT_LENGTH in config.py limits the request to 10 MB.
        # The plaintext is held in memory and only ciphertext is written to disk.
        plaintext = file.read()

        if not plaintext:
            flash("The selected file is empty.", "warning")
            return redirect(request.url)

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        encrypted_path = encrypted_disk_path(original_filename)

        try:
            ciphertext = encrypt_bytes(plaintext)

            with open(encrypted_path, "wb") as encrypted_file:
                encrypted_file.write(ciphertext)

        except OSError:
            if os.path.exists(encrypted_path):
                os.remove(encrypted_path)

            flash("Could not securely store the file.", "danger")
            return redirect(request.url)

        uploaded = UploadedFile(
            filename=original_filename,
            filepath=encrypted_path,
            user_id=session["user_id"],
            encrypted=True
        )

        db.session.add(uploaded)
        db.session.commit()

        log_security_event(
            session["user_id"],
            f"Uploaded & Encrypted File: {original_filename}",
            request.remote_addr
        )

        flash(
            "File uploaded and encrypted successfully!",
            "success"
        )

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
# Download / Decrypt File
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

    if not os.path.exists(file.filepath):
        flash("Stored file is missing.", "danger")
        return redirect(url_for("upload.upload_file"))

    try:
        with open(file.filepath, "rb") as encrypted_file:
            stored_data = encrypted_file.read()

        # Legacy files from the old version are plaintext.
        # New files are always Fernet encrypted.
        plaintext = (
            decrypt_bytes(stored_data)
            if file.encrypted
            else stored_data
        )

    except Exception:
        flash(
            "File could not be decrypted. Check the SecureVault encryption key.",
            "danger"
        )
        return redirect(url_for("upload.upload_file"))

    log_security_event(
        session["user_id"],
        f"Downloaded & Decrypted File: {file.filename}",
        request.remote_addr
    )

    return send_file(
        io.BytesIO(plaintext),
        as_attachment=True,
        download_name=file.filename,
        mimetype="application/octet-stream"
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

    filename = file.filename

    if os.path.exists(file.filepath):
        os.remove(file.filepath)

    db.session.delete(file)
    db.session.commit()

    log_security_event(
        session["user_id"],
        f"Deleted File: {filename}",
        request.remote_addr
    )

    flash("File deleted successfully.", "info")

    return redirect(url_for("upload.upload_file"))
