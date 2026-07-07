# 🛡️ SecureVault

A secure web application built with **Flask** that demonstrates modern web security practices including authentication, encrypted note storage, secure file upload, audit logging, brute-force protection, CSRF protection, and OWASP-inspired secure coding.

---

## 📸 Project Preview

- Register Page
- Login Page
- Dashboard
- Secure Notes
- File Upload
- Security Logs

---

# ✨ Features

## 🔐 Authentication

- User Registration
- Secure Login
- Logout
- Password Change
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

B.Tech CS-IT

---

# ⭐ If you like this project

Give it a ⭐ on GitHub.