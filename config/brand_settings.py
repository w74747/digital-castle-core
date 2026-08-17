"""
هيئة الإعدادات والهوية المؤسسية
Brand Configuration & Legal Metadata
"""

from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class BrandConfig:
    """معايير الهوية المؤسسية - Digital Castle S.P.C"""
    
    # المعلومات الأساسية
    name_ar: str = "شركة القلعة الرقمية ش.ش.و"
    name_en: str = "Digital Castle S.P.C"
    tagline_ar: str = "منصات ذكية، حلول مؤسسية"
    tagline_en: str = "Smart Platforms, Enterprise Solutions"
    
    # البيانات القانونية والضريبية
    cr_number: str = "1197389"  # رقم السجل التجاري
    tax_id: str = "OM-1197389-001"  # رقم التعريف الضريبي
    tax_rate: float = 0.05  # 5% VAT
    
    # الموقع والعملة
    country: str = "سلطنة عُمان"
    country_en: str = "Sultanate of Oman"
    currency: str = "ر.ع."
    currency_en: str = "OMR"
    
    # معلومات الاتصال
    email: str = "info@digitalcastle.om"
    phone: str = "+968-95-XXXX-XXXX"
    website: str = "www.digitalcastle.om"
    address: str = "مسقط، سلطنة عُمان"
    
    # الألوان المؤسسية
    color_primary: str = "#0f172a"      # الأسود الغامق
    color_secondary: str = "#1d4ed8"    # الأزرق الملكي
    color_accent: str = "#0ea5e9"       # الأزرق الفاتح
    color_success: str = "#16a34a"      # الأخضر
    color_danger: str = "#dc2626"       # الأحمر
    
    # إعدادات الأمان
    security_seal_prefix: str = "DC"
    document_version: str = "1.0"

# النسخة الفريدة من البيانات المؤسسية
BRAND = BrandConfig()

# دالة للتحقق من البيانات
def validate_brand_config() -> bool:
    """التحقق من اكتمال بيانات الهوية"""
    required_fields = [
        'name_ar', 'name_en', 'cr_number', 'email', 
        'tax_rate', 'currency', 'country'
    ]
    for field in required_fields:
        if not getattr(BRAND, field, None):
            return False
    return True
