from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"


def load_key():

    if not os.path.exists(KEY_FILE):

        key = Fernet.generate_key()

        with open(KEY_FILE, "wb") as f:
            f.write(key)

    with open(KEY_FILE, "rb") as f:
        return f.read()


key = load_key()

cipher = Fernet(key)


def encrypt_text(text):

    return cipher.encrypt(text.encode()).decode()


def decrypt_text(text):

    return cipher.decrypt(text.encode()).decode()