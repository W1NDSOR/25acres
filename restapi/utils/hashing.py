from hashlib import sha256
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import GCM
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.backends import default_backend
from os import urandom


def hashDocument(data: str) -> str:
    """
    @desc: hashes the `data` to SHA256
    @param {str} data: data that is to be hashed
    @returns {str} sha256: SHA256 of data (digest)
    """
    hasher = sha256()
    try:
        data = data.encode()
    except:
        pass
    hasher.update(data)
    return hasher.hexdigest()
