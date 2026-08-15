import pytest
from app.auth import hash_password, verify_password, create_access_token, verify_token

def test_hash_password():
    password = "test123"
    hashed = hash_password(password)
    assert verify_password(password, hashed)

def test_token_creation():
    token = create_access_token({"sub": "testuser"})
    assert token is not None
    assert len(token) > 0
