import base64
import hashlib
from io import BytesIO
import os
import re
from PIL import Image, ImageDraw, ImageFont
import qrcode

SECRET_KEY = os.getenv("APP_SECRET_KEY", "digital-castle-secure-key-2026")


def generate_document_seal_code(
    doc_number: str, total_amount: float, date_str: str
) -> str:
    """توليد كود أمان تسلسلي مشفر وفريد للفاتورة"""
    payload = f"{doc_number}:{total_amount:.2f}:{date_str}:{SECRET_KEY}"
    hash_digest = hashlib.sha256(payload.encode()).hexdigest().upper()
    return f"DC-{hash_digest[:4]}-{hash_digest[4:8]}"


def generate_verification_qr(
    doc_number: str, total_amount: float, date_str: str, security_code: str
) -> str:
    """توليد رمز QR سريع القراءة لبيانات التحقق الرسمية"""
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
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def _load_pil_image_from_asset(file_path: str) -> Image.Image:
    """تحميل الصورة بمرونة سواء كانت ملفاً ثنائياً أو نصاً مشفراً تم لصقه"""
    if not os.path.exists(file_path):
        return None

    with open(file_path, "rb") as f:
        raw_bytes = f.read()

    try:
        text = raw_bytes.decode("utf-8").strip()
        # إذا كان كود data:image أو HTML <img>
        match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', text)
        if match:
            img_data = base64.b64decode(match.group(1))
            return Image.open(BytesIO(img_data)).convert("RGBA")
        elif len(text) > 100 and re.match(r"^[A-Za-z0-9+/=\s]+$", text):
            img_data = base64.b64decode(re.sub(r"\s+", "", text))
            return Image.open(BytesIO(img_data)).convert("RGBA")
    except Exception:
        pass

    try:
        return Image.open(BytesIO(raw_bytes)).convert("RGBA")
    except Exception:
        return None


def get_secure_stamped_asset(
    file_path: str, security_code: str, is_signature: bool = False
) -> str:
    """طباعة البصمة الأمنية المشفرة داخل بكسلات الصورة مباشرة في الوسط"""
    img = _load_pil_image_from_asset(file_path)
    if img is None:
        return ""

    width, height = img.size
    draw = ImageDraw.Draw(img)

    # تجهيز نص البصمة
    label_text = f"Ref: {security_code}" if is_signature else security_code

    try:
        # حساب أبعاد النص وموضعه في المنتصف
        bbox = draw.textbbox((0, 0), label_text)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except Exception:
        text_w, text_h = (len(label_text) * 8, 14)

    center_x = (width - text_w) // 2
    center_y = (height - text_h) // 2

    # رسم خلفية حماية مصغرة مدمجة مع الصورة لمنع قصها
    padding_x, padding_y = 6, 3
    box_rect = [
        center_x - padding_x,
        center_y - padding_y,
        center_x + text_w + padding_x,
        center_y + text_h + padding_y,
    ]

    if is_signature:
        # شريط أمان مدمج مع خطوط التوقيع
        draw.rectangle(box_rect, fill=(241, 245, 249, 210), outline=(71, 85, 105, 240), width=1)
        draw.text((center_x, center_y), label_text, fill=(15, 23, 42, 255))
    else:
        # شريط أمان مدمج في قلب الختم الرسمي
        draw.rectangle(box_rect, fill=(255, 255, 255, 220), outline=(185, 28, 28, 230), width=1)
        draw.text((center_x, center_y), label_text, fill=(185, 28, 28, 255))

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def get_logo_data_uri(file_path: str) -> str:
    """قراءة شعار الشركة بدقة متناهية"""
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        raw_data = f.read()

    try:
        text = raw_data.decode("utf-8").strip()
        img_src_match = re.search(r'src=["\']([^"\']+)["\']', text)
        if img_src_match:
            return img_src_match.group(1)
        if text.startswith("data:image"):
            return text
        if text.startswith("<svg") or "<?xml" in text:
            b64_svg = base64.b64encode(text.encode("utf-8")).decode("utf-8")
            return f"data:image/svg+xml;base64,{b64_svg}"
    except Exception:
        pass

    b64_raw = base64.b64encode(raw_data).decode("utf-8")
    return f"data:image/png;base64,{b64_raw}"
