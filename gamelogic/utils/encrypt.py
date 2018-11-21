#encrypt.py
import hashlib

def encrypt_sha256(msg: str) -> str:
    sha256 = hashlib.sha256()
    msg_bytes = msg.encode()
    sha256.update(msg_bytes)
    return sha256.hexdigest()
