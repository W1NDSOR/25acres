import hashlib


def hashImage(imagePath: str) -> str:
    """
    @desc: hashes image present at path `imagePath` to SHA256
    @param {string} imagePath: path to image
    @returns {string} sha256: SHA256 of image (digest)
    """
    try:
        with open(imagePath, "rb") as file:
            imageData = file.read()
            hasher = hashlib.sha256()
            hasher.update(imageData)
            return hasher.hexdigest()
    except:
        pass
