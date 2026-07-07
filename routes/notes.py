from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from extensions import db
from database.models import Note
from security.encryption import encrypt_text, decrypt_text
from forms.forms import EmptyForm
from security.logger import log_security_event

notes = Blueprint("notes", __name__)


# ==========================
# Secure Notes
# ==========================

@notes.route("/notes", methods=["GET", "POST"])
def notes_page():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    form = EmptyForm()

    if form.validate_on_submit():

        title = request.form.get("title", "").strip()
        note = request.form.get("note", "").strip()

        if not title or not note:

            flash("Title and Note cannot be empty.", "warning")
            return redirect(url_for("notes.notes_page"))

        encrypted_note = encrypt_text(note)

        new_note = Note(
            title=title,
            note=encrypted_note,
            user_id=session["user_id"]
        )

        db.session.add(new_note)
        db.session.commit()

        # Security Log
        log_security_event(
            session["user_id"],
            f"Created Note: {title}",
            request.remote_addr
        )

        flash("Note saved securely!", "success")

        return redirect(url_for("notes.notes_page"))

    all_notes = Note.query.filter_by(
        user_id=session["user_id"]
    ).all()

    decrypted_notes = []

    for note in all_notes:

        decrypted_notes.append({
            "id": note.id,
            "title": note.title,
            "note": decrypt_text(note.note)
        })

    return render_template(
        "notes.html",
        notes=decrypted_notes,
        form=form
    )


# ==========================
# Delete Note
# ==========================

@notes.route("/delete-note/<int:note_id>", methods=["POST"])
def delete_note(note_id):

    if "user_id" not in session:

        flash("Please login first.", "warning")

        return redirect(url_for("auth.login"))

    note = Note.query.filter_by(
        id=note_id,
        user_id=session["user_id"]
    ).first()

    if note:

        note_title = note.title

        db.session.delete(note)
        db.session.commit()

        # Security Log
        log_security_event(
            session["user_id"],
            f"Deleted Note: {note_title}",
            request.remote_addr
        )

        flash("Note deleted successfully.", "info")

    else:

        flash("Note not found.", "danger")

    return redirect(url_for("notes.notes_page"))