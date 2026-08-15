"""
Encryption Layer - Encrypt sensitive data before API calls.
"""

from cryptography.fernet import Fernet
import os
import base64

class DataEncryptor:
    """Encrypts/decrypts sensitive data."""
    
    def __init__(self):
        # Generate key from environment or create
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            key = Fernet.generate_key()
            print(f"⚠️ New encryption key: {key.decode()}")
        
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def encrypt_dict(self, data: dict, keys_to_encrypt: list) -> dict:
        """Encrypt specific dict keys."""
        encrypted = data.copy()
        for key in keys_to_encrypt:
            if key in encrypted:
                encrypted[key] = self.encrypt(str(encrypted[key]))
        return encrypted

# Usage
encryptor = DataEncryptor()
encrypted_payload = encryptor.encrypt_dict(
    user_data,
    keys_to_encrypt=['email', 'phone', 'address']
)
