import os
from dataclasses import dataclass


@dataclass
class BrandIdentity:
    company_name_en: str = "Digital Castle S.P.C"
    company_name_ar: str = "القلعة الرقمية ش.ش.و"
    country: str = "Sultanate of Oman"
    currency_en: str = "OMR"
    currency_ar: str = "ر.ع."
    primary_color: str = "#0F172A"  # Slate 900
    accent_color: str = "#2563EB"  # Royal Blue
    neutral_light: str = "#F8FAFC"  # Light background
    tax_rate: float = 0.05  # 5% ضريبة القيمة المضافة في عُمان


BRAND = BrandIdentity()


def get_environment_config():
    return {
        "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "telegram_admin": os.getenv("TELEGRAM_ADMIN_ID"),
        "anthropic_key": os.getenv("ANTHROPIC_API_KEY"),
        "deepseek_key": os.getenv("DEEPSEEK_API_KEY"),
        "together_key": os.getenv("TOGETHER_API_KEY"),
        "github_token": os.getenv("GITHUB_TOKEN"),
        "debug": os.getenv("DEBUG", "False").lower() == "true",
        "port": int(os.getenv("PORT", 8000)),
    }
