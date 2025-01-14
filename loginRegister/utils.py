import bcrypt
from Crypto.Cipher import AES
import base64
import os

# Use an environment variable for the SECRET_KEY or raise an error for production
SECRET_KEY = os.getenv('SECRET_KEY', b'some_16_byte_key')

# Ensure the SECRET_KEY meets the required length for AES encryption
SECRET_KEY = (SECRET_KEY[:32] + b'\0' * 32)[:32]

if len(SECRET_KEY) not in [16, 24, 32]:
    raise ValueError("SECRET_KEY must be 16, 24, or 32 bytes long.")

### PASSWORD HASHING ###
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

### DATA ENCRYPTION ###
def encrypt_data(data: str) -> str:
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    return base64.b64encode(nonce + tag + ciphertext).decode('utf-8')

def decrypt_data(encrypted_data: str) -> str:
    try:
        encrypted_bytes = base64.b64decode(encrypted_data)
        nonce = encrypted_bytes[:16]
        tag = encrypted_bytes[16:32]
        ciphertext = encrypted_bytes[32:]
        cipher = AES.new(SECRET_KEY, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")

if __name__ == "__main__":
    plain_password = "securepassword123"
    hashed = hash_password(plain_password)
    print(f"Password: {plain_password}")
    print(f"Hashed: {hashed}")
    print(f"Verified: {verify_password(plain_password, hashed)}")

    test_data = "Sensitive Information"
    encrypted = encrypt_data(test_data)
    print(f"Original: {test_data}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypt_data(encrypted)}")
