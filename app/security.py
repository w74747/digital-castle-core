import base64
import hashlib
from io import BytesIO
import os
import qrcode

SECRET_KEY = os.getenv("APP_SECRET_KEY", "digital-castle-secure-key-2026")


def generate_document_seal_code(
    doc_number: str, total_amount: float, date_str: str
) -> str:
    """توليد رمز أمان تسلسلي فريد ومثبت داخل الختم والتوقيع"""
    payload = f"{doc_number}:{total_amount:.2f}:{date_str}:{SECRET_KEY}"
    hash_digest = hashlib.sha256(payload.encode()).hexdigest().upper()
    return f"DC-{hash_digest[:4]}-{hash_digest[4:8]}"


def generate_verification_qr(
    doc_number: str, total_amount: float, date_str: str, security_code: str
) -> str:
    """توليد رمز QR يحتوي على بيانات التحقق الرسمية بصيغة Base64"""
    verification_data = (
        f"🏰 القلعة الرقمية ش.ش.و | Digital Castle S.P.C\n"
        f"📄 رقم المستند: {doc_number}\n"
        f"💰 الإجمالي: {total_amount:.2f} ر.ع.\n"
        f"📅 التاريخ: {date_str}\n"
        f"🔒 رمز التحقق الأمني: {security_code}\n"
        f"✓ الحالة: وثيقة رسمية معتمدة وموثقة"
    )

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=1,
    )
    qr.add_data(verification_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0a192f", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
