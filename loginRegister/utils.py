from Crypto.Cipher import AES
import base64

SECRET_KEY = b'some_16_byte_key'  # Ensure this is 16, 24, or 32 bytes

import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# # Route: Login
def encrypt_data(data):
    if len(SECRET_KEY) not in [16, 24, 32]:
        raise ValueError("SECRET_KEY must be 16, 24, or 32 bytes long.")
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    return {'nonce': nonce, 'ciphertext': ciphertext, 'tag': tag}

def decrypt_data(encrypted_data):
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX, nonce=encrypted_data['nonce'])
    plaintext = cipher.decrypt_and_verify(encrypted_data['ciphertext'], encrypted_data['tag'])
    return plaintext.decode('utf-8')