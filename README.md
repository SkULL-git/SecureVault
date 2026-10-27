# 🛡️ SecureVault

A secure web application built with **Flask** that demonstrates modern web security practices including authentication, encrypted note storage, secure file upload, audit logging, brute-force protection, CSRF protection, and OWASP-inspired secure coding.

---

## 📸 Project Preview

- Register Page

  <img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/4caadd95-e1ce-4ed5-b94f-7432f3a4aa60" />

- Login Page
  <img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/ece41545-e6a3-41a2-b67a-4ffd5457b54d" />

- Dashboard
  <img width="1892" height="1079" alt="image" src="https://github.com/user-attachments/assets/75603b91-8ee6-41ec-b07e-6252908b9c93" />

- Secure Notes
  <img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/a840b78f-fbe3-4343-9e10-0a9d14c572ef" />

- File Upload
  <img width="1919" height="1077" alt="image" src="https://github.com/user-attachments/assets/9d8f5f5d-13e0-4a0c-aca6-e17694a3df1e" />

- Security Logs
  <img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/a39efd2b-484c-4a79-8436-968b45b7f7d8" />



---

# ✨ Features

## 🔐 Authentication

- User Registration
- Secure Login
- Logout
- Password Change
- Recovery Key Password Reset
- Password Strength Meter
- Session Management
- Brute Force Protection

---

## 📝 Secure Notes

- Create Notes
- Delete Notes
- Encrypted Storage
- User-specific Notes

---

## 📁 Secure File Upload

- Upload Files
- Download Files
- Delete Files
- File Type Validation
- File Size Limit (10 MB)
- Fernet-encrypted storage for uploaded files, including photos and videos
- Secure Filename Handling

---

## 🛡️ Security Features

- Password Hashing using Bcrypt
- CSRF Protection
- Security Headers
- Content Security Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options
- Referrer Policy
- Secure Session Handling
- Custom Error Pages
- Security Audit Logs

---

## 📊 Dashboard

- Total Notes
- Uploaded Files
- Security Logs
- Member Since

---

## ⚠️ Custom Error Pages

- 404 Not Found
- 413 File Too Large
- 500 Internal Server Error

---

# 🛠️ Tech Stack

- Python
- Flask
- Flask-WTF
- SQLAlchemy
- SQLite
- Flask-Bcrypt
- Bootstrap 5
- HTML
- CSS
- JavaScript
- Font Awesome

---

# 📂 Project Structure

```
SecureVault/
│
├── app.py
├── config.py
├── extensions.py
├── requirements.txt
│
├── database/
│   └── models.py
│
├── routes/
│   ├── auth.py
│   ├── notes.py
│   ├── upload.py
│   └── logs.py
│
├── security/
│   ├── encryption.py
│   └── logger.py
│
├── forms/
│   └── forms.py
├── create_admin.py
├── .env.example
│
├── templates/
│
├── static/
│   ├── css/
│   └── js/
│
├── uploads/
│
└── instance/
```

---

# 🚀 Installation

```bash
git clone https://github.com/YOUR_USERNAME/SecureVault.git

cd SecureVault

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python app.py
```

---

# 🔒 Security Controls

- ✅ Authentication
- ✅ Authorization
- ✅ Password Hashing
- ✅ CSRF Protection
- ✅ Brute Force Protection
- ✅ Secure File Upload
- ✅ File Validation
- ✅ Security Headers
- ✅ Content Security Policy
- ✅ Encrypted Notes
- ✅ Audit Logging

---

# 🧰 PostgreSQL + Admin Dashboard Upgrade

## New features
- PostgreSQL support through `DATABASE_URL` (SQLite remains the local default).
- Flask-Migrate/Alembic support for schema migrations.
- Admin overview cards for user counts, notes, uploaded files and audit events.
- User search, account enable/disable, and role promotion/demotion.
- Cross-account security audit view (metadata only; never decrypts private notes).
- Admin routes re-check the current user's database role on each request.
- Protections against disabling/demoting the current admin or removing the last active admin.

## Local setup
1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and set strong, unique `SECRET_KEY` and `JWT_SECRET_KEY` values.
4. For PostgreSQL, create a database and set `DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/securevault`.
5. Run the app once with `python app.py`. The app creates missing tables and applies a small compatibility update for the `role`, `is_active`, `recovery_key_hash`, and `encrypted` columns on existing SQLite/PostgreSQL databases.
6. Register your normal account in SecureVault, then run `python create_admin.py` and confirm that account's email. Do not hardcode admin credentials in source code.
7. For future schema changes, initialize Flask-Migrate once (`flask --app app db init`) and then use `flask --app app db migrate -m "Describe schema change"` followed by `flask --app app db upgrade`. Review generated migrations before applying them. Do not run `db init` again if `migrations/` already exists.

`db.create_all()` creates missing tables but does not modify existing tables; the compatibility code above only covers the listed legacy columns. Use reviewed migrations for future schema changes.

## Production notes
- Configure HTTPS and set `SESSION_COOKIE_SECURE=true`.
- Use a managed PostgreSQL database, backups, and a tested migration/rollback plan.
- Set strong secrets in the hosting provider's environment settings; never commit `.env`.
- Admin access should use a unique account and a strong password. Add MFA before exposing the app publicly.
- The audit view exposes IP addresses and account activity to administrators; set an appropriate retention policy.
- Uploaded encrypted files currently live on local disk. For multi-instance hosting, configure durable private storage and backups; a PostgreSQL migration does not migrate the file bytes themselves.

---

# 📚 Future Enhancements

- Email Verification
- Two-Factor Authentication (2FA)
- Role-Based Access Control (RBAC)
- Cloud Storage Integration
- Docker Support
- PostgreSQL Support

---

# 👨‍💻 Author

**Shivam Kumar**

B.Tech CS-IT(3rd Year)


---

# ⭐ If you like this project


Give it a ⭐ on GitHub.
