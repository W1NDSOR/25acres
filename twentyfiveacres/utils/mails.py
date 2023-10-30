import ssl
from django.core.mail import send_mail
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import GCM
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.backends import default_backend
from os import urandom


ssl._create_default_https_context = ssl._create_unverified_context
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


def generateGcmOtp(key, data):
    """
    @desc: generates the `OTP` using AESGCM
    @param {str} key: secret key
    @param {str} data: using which the OTP should be generated
    @returns {str} otp: otp
    """
    nonce = urandom(12)
    cipher = Cipher(AES(key), GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    intValue = int.from_bytes(ciphertext[:3], "big")
    otp = f"{intValue % 10**6:06}"
    return otp


def sendMail(
    subject: str,
    message: str,
    recipientEmails: list[str],
    failSilently: bool = False,
    senderEmail: str = "settings.EMAIL_HOST_USER",
):
    """
    @desc: wrapper from `django.core.mail.send_mail` method
    @param {str} subject: subject
    @param {str} message: message
    @param {str} senderEmail: sender email
    @param {list[str]} recipientEmails: list of recipient emails
    @param {bool} failSilently: fail silently
    @returns {int} result: result
    """
    return send_mail(subject, message, senderEmail, recipientEmails, failSilently)
