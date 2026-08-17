"""
محرك الأمان والتشفير والعلامات المائية
Security Engine with Encryption & Watermarking
"""

import os
import re
import base64
import hashlib
from io import BytesIO
from typing import Optional, Tuple
import qrcode
from PIL import Image, ImageDraw, ImageFont
from config.brand_settings import BRAND

# مفتاح التشفير الأساسي
SECRET_KEY = os.getenv("APP_SECRET_KEY", "digital-castle-secure-key-2026")

# ============================================
# 1. توليد رموز التحقق
# ============================================

def generate_document_seal_code(
    doc_number: str, 
    total_amount: float, 
    date_str: str
) -> str:
    """
    توليد رمز الختم الأمني للمستند
    Generate unique seal code with SHA-256 hashing
    
    Args:
        doc_number: رقم المستند
        total_amount: الإجمالي المالي
        date_str: تاريخ الإصدار
    
    Returns:
        رمز فريد بصيغة: DC-XXXX-XXXX
    """
    payload = f"{doc_number}:{total_amount:.2f}:{date_str}:{SECRET_KEY}:{BRAND.cr_number}"
    hash_digest = hashlib.sha256(payload.encode()).hexdigest().upper()
    return f"{BRAND.security_seal_prefix}-{hash_digest[:4]}-{hash_digest[4:8]}"


def generate_verification_qr(
    doc_number: str,
    total_amount: float,
    date_str: str,
    security_code: str
) -> str:
    """
    توليد كود QR للتحقق الرسمي
    Generate QR code for official verification
    
    Returns:
        Data URI with base64 encoded PNG
    """
    qr_content = (
        f"═══════════════════════════════\n"
        f"{BRAND.name_ar}\n"
        f"{BRAND.name_en}\n"
        f"═══════════════════════════════\n"
        f"📄 رقم المستند: {doc_number}\n"
        f"💰 الإجمالي: {total_amount:.2f} {BRAND.currency_en}\n"
        f"📅 التاريخ: {date_str}\n"
        f"🔐 رمز التحقق: {security_code}\n"
        f"✅ الحالة: معتمد ورسمي\n"
        f"═══════════════════════════════\n"
        f"التحقق عبر: www.digitalcastle.om"
    )
    
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # أعلى مستوى تصحيح
        box_size=10,
        border=4
    )
    qr.add_data(qr_content)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


# ============================================
# 2. معالجة الأصول (الصور)
# ============================================

def _load_pil_image_from_asset(file_path: str) -> Optional[Image.Image]:
    """
    تحميل صورة من ملف (دعم PNG، JPG، SVG Data URIs، Base64)
    Load image from various formats
    """
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, "rb") as f:
        raw_bytes = f.read()
    
    # محاولة فك ترميز Data URI أو Base64
    try:
        text = raw_bytes.decode("utf-8").strip()
        
        # Data URI regex
        match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', text)
        if match:
            img_data = base64.b64decode(match.group(1))
            return Image.open(BytesIO(img_data)).convert("RGBA")
        
        # Pure Base64
        if len(text) > 100 and re.match(r'^[A-Za-z0-9+/=\s]+$', text):
            img_data = base64.b64decode(re.sub(r'\s+', '', text))
            return Image.open(BytesIO(img_data)).convert("RGBA")
    except Exception:
        pass
    
    # محاولة تحميل الملف الخام
    try:
        return Image.open(BytesIO(raw_bytes)).convert("RGBA")
    except Exception:
        return None


def _get_scalable_font(target_size: int) -> ImageFont.FreeTypeFont:
    """
    الحصول على خط TrueType مع حجم محدد
    Get scalable TrueType font
    """
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=target_size)
            except Exception:
                pass
    
    # الخط الافتراضي كآخر ملجأ
    try:
        return ImageFont.load_default(size=target_size)
    except TypeError:
        return ImageFont.load_default()


# ============================================
# 3. العلامات المائية (Watermarking)
# ============================================

def get_secure_stamped_asset(
    file_path: str,
    security_code: str,
    is_signature: bool = False
) -> str:
    """
    إضافة علامة مائية أمنية على الأصل
    Add secure watermark with rotated text
    
    Args:
        file_path: مسار ملف الصورة
        security_code: رمز الأمان المراد إضافته
        is_signature: ما إذا كانت توقيع (تنسيق مختلف)
    
    Returns:
        Data URI للصورة بها الـ watermark
    """
    img = _load_pil_image_from_asset(file_path)
    if img is None:
        return ""
    
    width, height = img.size
    label_text = f"Ref: {security_code}" if is_signature else security_code
    
    # تحديد حجم الخط واللون بناءً على النوع
    if is_signature:
        font_size = max(12, int(width / (len(label_text) * 1.0)))
        text_color = (20, 60, 180, 180)  # أزرق شفاف
        rotation_angle = 6
    else:
        font_size = max(20, int(height * 0.12))
        text_color = (220, 38, 38, 170)  # أحمر شفاف
        rotation_angle = 8
    
    font = _get_scalable_font(font_size)
    
    # حساب حجم النص
    dummy_img = Image.new("RGBA", (1, 1))
    draw_dummy = ImageDraw.Draw(dummy_img)
    try:
        bbox = draw_dummy.textbbox((0, 0), label_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except Exception:
        text_w = int(len(label_text) * font_size * 0.6)
        text_h = font_size
    
    # رسم النص على طبقة منفصلة
    text_canvas = Image.new("RGBA", (text_w + 30, text_h + 20), (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_canvas)
    text_draw.text((15, 10), label_text, fill=text_color, font=font)
    
    # تدوير النص
    rotated_text = text_canvas.rotate(rotation_angle, resample=Image.BICUBIC, expand=True)
    rot_w, rot_h = rotated_text.size
    
    # حساب موضع النص على الصورة
    pos_x = (width - rot_w) // 2
    pos_y = (height - rot_h) // 2
    
    # دمج طبقة العلامة المائية مع الصورة الأصلية
    watermark_layer = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    watermark_layer.paste(rotated_text, (pos_x, pos_y), rotated_text)
    
    combined = Image.alpha_composite(img, watermark_layer)
    
    # تحويل إلى Base64
    buffer = BytesIO()
    combined.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def get_logo_data_uri(file_path: str) -> str:
    """
    تحويل الشعار إلى Data URI
    Convert logo to Data URI (for HTML embedding)
    """
    if not os.path.exists(file_path):
        return ""
    
    with open(file_path, "rb") as f:
        raw_data = f.read()
    
    # محاولة استخراج مسار الصورة من HTML
    try:
        text = raw_data.decode("utf-8").strip()
        img_src_match = re.search(r'src=["\']([^"\']+)["\']', text)
        if img_src_match:
            return img_src_match.group(1)
        
        # إذا كانت بيانات Base64 مباشرة
        if text.startswith("data:image"):
            return text
        
        # تحويل SVG إلى Base64
        if text.startswith("<svg") or "<?xml" in text:
            b64_svg = base64.b64encode(text.encode("utf-8")).decode("utf-8")
            return f"data:image/svg+xml;base64,{b64_svg}"
    except Exception:
        pass
    
    # معالجة الملف الخام
    b64_raw = base64.b64encode(raw_data).decode("utf-8")
    return f"data:image/png;base64,{b64_raw}"
