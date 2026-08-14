import hashlib
import hmac
import os

SECRET_KEY = os.getenv("APP_SECRET_KEY", "digital-castle-secure-key-2026")


def generate_document_seal_code(
    doc_number: str, total_amount: float, date_str: str
) -> str:
    """توليد رمز أمان تسلسلي فريد ومثبت داخل الختم والتوقيع"""
    payload = f"{doc_number}:{total_amount:.2f}:{date_str}:{SECRET_KEY}"
    # توليد بصمة SHA-256 واختصارها لكود أمني واضح
    hash_digest = hashlib.sha256(payload.encode()).hexdigest().upper()
    # كود تسلسلي مثل: DC-A7B2-9F01
    return f"DC-{hash_digest[:4]}-{hash_digest[4:8]}"
