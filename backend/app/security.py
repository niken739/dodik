import os
import hashlib
import binascii

def generate_salt(length: int = 16) -> str:
    return binascii.hexlify(os.urandom(length)).decode()

def hash_password(password: str, salt: str) -> str:
    h = hashlib.sha256()
    h.update((password + salt).encode())
    return h.hexdigest()
