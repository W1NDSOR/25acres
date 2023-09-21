import hashlib


def hashDocument(data: str) -> str:
    """
    @desc: hashes image present at path `imagePath` to SHA256
    @param {string} imagePath: path to image
    @returns {string} sha256: SHA256 of image (digest)
    """
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()