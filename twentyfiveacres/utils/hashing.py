import hashlib


def hashDocument(data: str) -> str:
    """
    @desc: hashes the `data` to SHA256
    @param {string} data: data that is to be hashed
    @returns {string} sha256: SHA256 of data (digest)
    """
    hasher = hashlib.sha256()
    data = data.encode()
    hasher.update(data)
    return hasher.hexdigest()
