"""
Data Sanitization Layer - Remove sensitive information
before any external API call.
"""

import re
import hashlib
from typing import Any, Dict

class DataSanitizer:
    """Removes/hashes sensitive data."""
    
    SENSITIVE_PATTERNS = {
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'phone': r'(\+\d{1,3}[-.\s]?)?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'api_key': r'[a-zA-Z0-9]{32,}',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'ssn': r'\d{3}-\d{2}-\d{4}',
    }
    
    @staticmethod
    def hash_identifier(value: str) -> str:
        """Hash sensitive identifiers."""
        return f"HASH_{hashlib.sha256(value.encode()).hexdigest()[:12]}"
    
    @staticmethod
    def remove_sensitive_data(data: Dict) -> Dict:
        """Remove sensitive fields."""
        forbidden_fields = {
            'password', 'token', 'api_key', 'secret',
            'ssn', 'credit_card', 'private_key',
            'auth', 'credential'
        }
        
        cleaned = {}
        for key, value in data.items():
            if key.lower() in forbidden_fields:
                cleaned[key] = "***REDACTED***"
            elif isinstance(value, dict):
                cleaned[key] = DataSanitizer.remove_sensitive_data(value)
            elif isinstance(value, str):
                cleaned[key] = DataSanitizer._sanitize_string(value)
            else:
                cleaned[key] = value
        
        return cleaned
    
    @staticmethod
    def _sanitize_string(text: str) -> str:
        """Replace sensitive patterns."""
        for pattern_name, pattern in DataSanitizer.SENSITIVE_PATTERNS.items():
            text = re.sub(pattern, f"[{pattern_name.upper()}]", text)
        return text

# Usage
sanitizer = DataSanitizer()
clean_data = sanitizer.remove_sensitive_data(user_input)
