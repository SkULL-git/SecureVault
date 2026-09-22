from cryptography.fernet import Fernet

import os

KEY_FILE = os.getenv("SECUREVAULT_KEY_FILE", "secret.key")


def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)

        try:
            os.chmod(KEY_FILE, 0o600)
        except OSError:
            pass

    with open(KEY_FILE, "rb") as f:
        key = f.read().strip()

    # Validate the key during startup.
    Fernet(key)
    return key


key = load_key()
cipher = Fernet(key)


def encrypt_text(text):
    return cipher.encrypt(text.encode("utf-8")).decode("utf-8")


def decrypt_text(text):
    return cipher.decrypt(text.encode("utf-8")).decode("utf-8")


def encrypt_bytes(data):
    """Encrypt binary data (images/videos/files) using Fernet."""
    return cipher.encrypt(data)


def decrypt_bytes(data):
    """Decrypt Fernet-encrypted binary data."""
    return cipher.decrypt(data)
