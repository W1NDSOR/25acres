from utils.hashing import hashDocument


def generateUserHash(username, rollNumber, email):
    """
    @desc: generates `userHash`
    @param {str} username: username
    @param {int} rollNumber: rollNumber
    @param {str} email: email
    @returns {str} userHash: userHash
    """
    return hashDocument(f"{username}.{rollNumber}.{email}")


def verifyUserDocument(user, document):
    documentHash = hashDocument(document)
    return documentHash == user.documentHash
