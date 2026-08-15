"""Data Sanitization & Encryption Layer"""
import re
import os
from cryptography.fernet import Fernet
from typing import Any, Dict

class DataSanitizer:
    SENSITIVE_PATTERNS = {
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'phone': r'(\+\d{1,3}[-.\s]?)?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'api_key': r'[a-zA-Z0-9]{32,}',
    }
    FORBIDDEN_FIELDS = {'password', 'token', 'api_key', 'secret', 'ssn', 'credit_card', 'private_key'}
    
    @staticmethod
    def sanitize(data: Any) -> Any:
        if isinstance(data, dict):
            return DataSanitizer._sanitize_dict(data)
        elif isinstance(data, str):
            return DataSanitizer._sanitize_string(data)
        return data
    
    @staticmethod
    def _sanitize_dict(data: Dict) -> Dict:
        cleaned = {}
        for key, value in data.items():
            if key.lower() in DataSanitizer.FORBIDDEN_FIELDS:
                cleaned[key] = "***REDACTED***"
            elif isinstance(value, dict):
                cleaned[key] = DataSanitizer._sanitize_dict(value)
            elif isinstance(value, str):
                cleaned[key] = DataSanitizer._sanitize_string(value)
            else:
                cleaned[key] = value
        return cleaned
    
    @staticmethod
    def _sanitize_string(text: str) -> str:
        for pattern in DataSanitizer.SENSITIVE_PATTERNS.values():
            text = re.sub(pattern, "[REDACTED]", text)
        return text

class DataEncryptor:
    def __init__(self):
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            key = Fernet.generate_key()
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()

sanitizer = DataSanitizer()
encryptor = DataEncryptor()
