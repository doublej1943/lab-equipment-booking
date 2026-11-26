"""Password policy shared by preset-account initialization and login."""

from werkzeug.security import check_password_hash, generate_password_hash

SCRYPT_METHOD = "scrypt:32768:8:3"
SALT_LENGTH = 24


def hash_password(password: str) -> str:
    return generate_password_hash(password, method=SCRYPT_METHOD, salt_length=SALT_LENGTH)


def verify_password(stored_hash: str, password: str) -> bool:
    return check_password_hash(stored_hash, password)
