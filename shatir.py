from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from base64 import b64encode, b64decode
import os

# Generate portal's private and public keys
def generate_portal_keys():
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

# Sign the message using portal's private key
def sign_with_portal_private_key(private_key, message):
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

# Verify the signature using portal's public key
def verify_with_portal_public_key(public_key, message, signature):
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return message  # If verification succeeds, return the original message
    except:
        return None

# Encrypt using user's SHA identifier
def encrypt_with_user_sha(user_sha, message):
    cipher = Cipher(algorithms.AES(user_sha), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(message) + encryptor.finalize()

# Decrypt using user's SHA identifier
def decrypt_with_user_sha(user_sha, encrypted_message):
    cipher = Cipher(algorithms.AES(user_sha), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_message) + decryptor.finalize()


def main():

    portal_private_key, portal_public_key = generate_portal_keys()
    # once these are generated they should be kept really really private and extremely secure 
    # one way of doing this is to save them as environment variables and then use them in the code
    
    contract = b"This is the description of the contract created betweeen the user and the portal!"
    contract_sha = hashes.Hash(hashes.SHA256(), backend=default_backend())
    contract_sha.update(contract)
    contract_sha_digest = contract_sha.finalize()
    print(f"Original Contract SHA: {b64encode(contract_sha_digest).decode('utf-8')}")
    # NOw this contract sha is to be saved in the sha databse of the portal

    user = "This is the description oo the user!"
    user_sha = hashes.Hash(hashes.SHA256(), backend=default_backend())
    user_sha.update(user.encode('utf-8'))
    user_sha = user_sha.finalize()
    print(f"User SHA: {b64encode(user_sha).decode('utf-8')}")
    
    # step1: sign the contract sha with the portal's private key
    signature = sign_with_portal_private_key(portal_private_key, contract_sha_digest)
    print(f"Signature: {b64encode(signature).decode('utf-8')}")

    # step2: encrypt the signature with the user's sha
    encrypted_signature = encrypt_with_user_sha(user_sha, signature)
    print(f"Encrypted Signature: {b64encode(encrypted_signature).decode('utf-8')}")
    # this string of characters is to be displayed to the user and asked to keep safe and secure and will be used for verification later on that the contract is issued by the portal

    # this is the logic that will be used by the portal to verify the contract and will be there in the profile of the user on the portal
    # step1: decrypt the encrypted signature with the user's sha first
    decrypted_signature = decrypt_with_user_sha(user_sha, encrypted_signature)
    print(f"Decrypted Signature: {b64encode(decrypted_signature).decode('utf-8')}")

    # step2: verify the decrypted signature with the portal's public key
    verified_contract_sha = verify_with_portal_public_key(portal_public_key, contract_sha_digest, decrypted_signature)
    print(f"Verified Contract SHA: {b64encode(verified_contract_sha).decode('utf-8')}" if verified_contract_sha else "Verification failed!")

    # this should be checking that whether the verified contract sha is stored in the portal's database or not
    if verified_contract_sha == contract_sha_digest:
        print("The contract is verified!")
    else:
        print("The contract is not verified!")

if __name__ == "__main__":
    main()
