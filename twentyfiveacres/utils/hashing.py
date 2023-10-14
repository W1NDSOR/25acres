from hashlib import sha256

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
