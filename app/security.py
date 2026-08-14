import base64
import hashlib
import os
from io import BytesIO
import qrcode
from PIL import Image

SECRET_KEY = os.getenv("APP_SECRET_KEY", "digital-castle-secure-key-2026")


def generate_document_seal_code(
    doc_number: str, total_amount: float, date_str: str
) -> str:
    """توليد رمز أمان تسلسلي فريد مرتبط بالحسابات والمستند"""
    payload = f"{doc_number}:{total_amount:.2f}:{date_str}:{SECRET_KEY}"
    hash_digest = hashlib.sha256(payload.encode()).hexdigest().upper()
    return f"DC-{hash_digest[:4]}-{hash_digest[4:8]}"


def generate_verification_qr(
    doc_number: str, total_amount: float, date_str: str, security_code: str
) -> str:
    """توليد QR واضح وقابل للقراءة الفورية من كاميرات الهواتف الذكية"""
    # نص قياسي سريع القراءة
    qr_content = (
        f"VERIFIED INVOICE\n"
        f"Issuer: Digital Castle S.P.C\n"
        f"Doc No: {doc_number}\n"
        f"Total: {total_amount:.2f} OMR\n"
        f"Date: {date_str}\n"
        f"Security Ref: {security_code}\n"
        f"Status: OFFICIAL & VALID"
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=2,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0a192f", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def get_asset_base64(file_path: str) -> str:
    """تحويل صور التوقيع والختم إلى Base64 لتضمينها في الـ PDF"""
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""
