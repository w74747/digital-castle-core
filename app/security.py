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
    """توليد رمز QR عالي الدقة وسهل القراءة فورياً من أي هاتف"""
    qr_content = (
        f"القلعة الرقمية ش.ش.و | Digital Castle S.P.C\n"
        f"رقم الفاتورة: {doc_number}\n"
        f"الإجمالي: {total_amount:.2f} OMR\n"
        f"التاريخ: {date_str}\n"
        f"رمز التحقق: {security_code}\n"
        f"الحالة: معتمد ورسمي"
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
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


def _get_scalable_font(target_size: int):
    """تحميل خط واضح بالحجم المطلوب مع دعم أنظمة Linux / Docker"""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size=target_size)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size=target_size)
    except TypeError:
        return ImageFont.load_default()


def get_secure_stamped_asset(
    file_path: str, security_code: str, is_signature: bool = False
) -> str:
    """طباعة البصمة الأمنية المشفرة بحجم واضح وبارز في منتصف الصورة مباشرة"""
    img = _load_pil_image_from_asset(file_path)
    if img is None:
        return ""

    width, height = img.size
    draw = ImageDraw.Draw(img)

    font_size = max(24, int(height * 0.12))
    font = _get_scalable_font(font_size)

    label_text = f"Ref: {security_code}" if is_signature else security_code

    try:
        bbox = draw.textbbox((0, 0), label_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except Exception:
        text_w, text_h = (len(label_text) * (font_size * 0.6), font_size)

    center_x = (width - text_w) // 2
    center_y = (height - text_h) // 2

    padding_x, padding_y = int(font_size * 0.4), int(font_size * 0.25)
    box_rect = [
        center_x - padding_x,
        center_y - padding_y,
        center_x + text_w + padding_x,
        center_y + text_h + padding_y,
    ]

    if is_signature:
        draw.rectangle(
            box_rect,
            fill=(241, 245, 249, 235),
            outline=(15, 23, 42, 255),
            width=2,
        )
        draw.text(
            (center_x, center_y),
            label_text,
            fill=(15, 23, 42, 255),
            font=font,
        )
    else:
        draw.rectangle(
            box_rect,
            fill=(255, 255, 255, 245),
            outline=(185, 28, 28, 255),
            width=2,
        )
        draw.text(
            (center_x, center_y),
            label_text,
            fill=(185, 28, 28, 255),
            font=font,
        )

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
