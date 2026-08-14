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
    """تحميل خط عريض وواضح بالحجم المطلوب"""
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
    """دمج كود الأمان كعلامة مائية متناسقة مع أبعاد الصورة دون أي قطع"""
    img = _load_pil_image_from_asset(file_path)
    if img is None:
        return ""

    width, height = img.size
    label_text = f"Ref: {security_code}" if is_signature else security_code

    # 1. ضبط حجم الخط وزاوية الميلان واللون لكل عنصر بدقة
    if is_signature:
        # حساب حجم الخط ليكون عرض النص دائماً متناسباً داخل مساحة التوقيع
        font_size = max(14, int(width / (len(label_text) * 0.95)))
        font = _get_scalable_font(font_size)
        text_color = (
            20,
            60,
            180,
            195,
        )  # أزرق كحلي شبه شفاف متقاطع مع خطوط التوقيع
        rotation_angle = 6  # زاوية ميلان خفيفة
    else:
        font_size = max(22, int(height * 0.13))
        font = _get_scalable_font(font_size)
        text_color = (220, 38, 38, 185)  # أحمر قرمزي رسمي للختم
        rotation_angle = 8

    # 2. قياس أبعاد النص بدقة
    dummy_img = Image.new("RGBA", (1, 1))
    draw_dummy = ImageDraw.Draw(dummy_img)
    try:
        bbox = draw_dummy.textbbox((0, 0), label_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except Exception:
        text_w, text_h = (int(len(label_text) * font_size * 0.6), font_size)

    # 3. رسم النص في طبقة مستقلة شفافة وتدويره
    text_canvas = Image.new(
        "RGBA", (text_w + 30, text_h + 20), (255, 255, 255, 0)
    )
    text_draw = ImageDraw.Draw(text_canvas)
    text_draw.text((15, 10), label_text, fill=text_color, font=font)

    rotated_text = text_canvas.rotate(
        rotation_angle, resample=Image.BICUBIC, expand=True
    )
    rot_w, rot_h = rotated_text.size

    # 4. التمركز الدقيق في المنتصف
    pos_x = (width - rot_w) // 2
    pos_y = (height - rot_h) // 2

    watermark_layer = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    watermark_layer.paste(rotated_text, (pos_x, pos_y), rotated_text)

    # دمج الطبقتين لإنتاج الصورة المائية النهائية
    combined = Image.alpha_composite(img, watermark_layer)

    buffer = BytesIO()
    combined.save(buffer, format="PNG")
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
