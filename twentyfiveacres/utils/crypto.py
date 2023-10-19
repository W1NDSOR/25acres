from base64 import b64decode
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.primitives.asymmetric.padding import PSS, MGF1
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import ECB
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature


def verifyWithPortalPublicKey(publicKey, message, signature):
    if not (isinstance(message, bytes) and isinstance(signature, bytes)):
        print("Error: Message and signature should be bytes-like objects.")
        return None
    if not hasattr(publicKey, "verify"):
        print("Error: Invalid public key provided.")
        return None
    try:
        publicKey.verify(
            signature,
            message,
            PSS(mgf=MGF1(SHA256()), salt_length=PSS.MAX_LENGTH),
            SHA256(),
        )
        return message
    except InvalidSignature:
        print("Error: Signature verification failed.")
    except Exception as e:
        print(f"Unexpected error: {e}")


def padData(data):
    """
    @desc: adds `PKCS7` padding to the `data`
    @param {str} data: data that needs to be padded
    @returns {str} paddedData: padded data
    """
    padder = PKCS7(128).padder()
    data = data if isinstance(data, bytes) else str.encode(data)
    paddedData = padder.update(data) + padder.finalize()
    return paddedData


def unpadData(paddedData):
    """
    @desc: removes `PKCS7` from the `data`
    @param {str} paddedData: data from which padding needs to be removed
    @returns {str} data: data
    """
    unpadder = PKCS7(128).unpadder()
    data = unpadder.update(paddedData) + unpadder.finalize()
    return data


# def encryptWithUserSha(userSha, message):
#     """
#     @desc: encrypt the `message` with `userSha`
#     @param {str} userSha: user hash
#     @param {str} message: message that needs to be encrypted
#     @returns {str} encryptedMessage: encrypted message
#     """
#     print(f"before {len(userSha)}")
#     userSha = userSha if isinstance(userSha, bytes) else str.encode(userSha)
#     print(f"after {len(userSha)}")
#     message = message if isinstance(message, bytes) else str.encode(message)
#     cipher = Cipher(AES(userSha), ECB(), backend=default_backend())
#     encryptor = cipher.encryptor()
#     message = padData(message)
#     encryptedMessage = encryptor.update(message) + encryptor.finalize()
#     return encryptedMessage

# old one
def encryptWithUserSha(userSha, message):
    """
    @desc: encrypt the `message` with `userSha`
    @param {str} userSha: user hash
    @param {str} message: message that needs to be encrypted
    @returns {str} encryptedMessage: encrypted message
    """
    cipher = Cipher(AES(userSha), ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    message = padData(message)
    encryptedMessage = encryptor.update(message) + encryptor.finalize()
    return encryptedMessage


# def decryptWithUserSha(userSha, encryptedMessage):
#     """
#     @desc: decrypt the `encryptedMessage` with `userSha`
#     @param {str} userSha: user hash
#     @param {str} encryptedMessage: message that needs to be decrypted
#     @returns {str} decryptedMessage: decrypted message
#     """
#     userSha = userSha if isinstance(userSha, bytes) else str.encode(userSha)
#     encryptedMessage = (
#         encryptedMessage
#         if isinstance(encryptedMessage, bytes)
#         else str.encode(encryptedMessage)
#     )
#     cipher = Cipher(AES(userSha), ECB(), backend=default_backend())
#     decryptor = cipher.decryptor()
#     decryptedMessage = decryptor.update(encryptedMessage) + decryptor.finalize()
#     decryptedMessage = unpadData(decryptedMessage)
#     return decryptedMessage

def decryptWithUserSha(userSha, encryptedMessage):
    """
    @desc: decrypt the `encryptedMessage` with `userSha`
    @param {str} userSha: user hash
    @param {str} encryptedMessage: message that needs to be decrypted
    @returns {str} decryptedMessage: decrypted message
    """
    cipher = Cipher(AES(userSha), ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    decryptedMessage = decryptor.update(encryptedMessage) + decryptor.finalize()
    decryptedMessage = unpadData(decryptedMessage)
    return decryptedMessage


def generatePortalKeys():
    """
    @desc: generates random pair of public and private keys
    @returns {list[str]} (privateKey, publicKey): key pair
    """
    privateKey = generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    publicKey = privateKey.public_key()
    return privateKey, publicKey


def signWithPortalPrivateKey(privateKey, message):
    """
    @desc: signs `message` with `privateKey`
    @param {str} privateKey: private key
    @param {str} message: message that needs to be signed
    @returns {str} signature: generated signature
    """
    message = message if isinstance(message, bytes) else str.encode(message)
    signature = privateKey.sign(
        message,
        PSS(mgf=MGF1(SHA256()), salt_length=PSS.MAX_LENGTH),
        SHA256(),
    )
    return signature


with open("utils/private", "r") as privateKey:
    privateKeyBytes = b64decode(privateKey.read().rstrip())
    PORTAL_PRIVATE_KEY = load_pem_private_key(
        privateKeyBytes,
        password=None,
        backend=default_backend(),
    )



with open("utils/public", "r") as publicKey:
    PORTAL_PUBLIC_ENCODED_KEY = publicKey.read().rstrip()




# with open("utils/private", "r") as privateKey:
#     PORTAL_PRIVATE_KEY = privateKey.read().rstrip()

# with open("utils/public", "r") as publicKey:
#     PORTAL_PUBLIC_ENCODED_KEY = publicKey.read().rstrip()

