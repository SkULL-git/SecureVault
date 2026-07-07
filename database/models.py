from datetime import datetime
from extensions import db


# =========================
# User Model
# =========================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), default="user")

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # =========================
    # Last Login Details
    # =========================

    last_login = db.Column(
        db.DateTime,
        nullable=True
    )

    last_login_ip = db.Column(
        db.String(50),
        nullable=True
    )

    # =========================
    # Login Security
    # =========================

    failed_login_attempts = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    account_locked_until = db.Column(
        db.DateTime,
        nullable=True
    )

    # =========================
    # Relationships
    # =========================

    notes = db.relationship(
        "Note",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    uploaded_files = db.relationship(
        "UploadedFile",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    security_logs = db.relationship(
        "SecurityLog",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"


# =========================
# Secure Notes Model
# =========================

class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    note = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Note {self.title}>"


# =========================
# Uploaded Files Model
# =========================

class UploadedFile(db.Model):
    __tablename__ = "uploaded_files"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    filepath = db.Column(
        db.String(500),
        nullable=False
    )

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<UploadedFile {self.filename}>"


# =========================
# Security Logs Model
# =========================

class SecurityLog(db.Model):
    __tablename__ = "security_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    action = db.Column(
        db.String(255),
        nullable=False
    )

    ip_address = db.Column(
        db.String(50),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<SecurityLog {self.action}>"