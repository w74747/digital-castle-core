"""
محرك توليد المستندات الرسمية (Playwright + Jinja2)
Official Document Generation Engine
"""

import os
import asyncio
from datetime import datetime
from io import BytesIO
from jinja2 import Template
from playwright.async_api import async_playwright
import logging

from app.security import (
    generate_document_seal_code,
    generate_verification_qr,
    get_secure_stamped_asset,
    get_logo_data_uri
)
from config.brand_settings import BRAND

logger = logging.getLogger(__name__)

class DocumentEngine:
    """محرك توليد الفواتير والمستندات الرسمية"""
    
    def __init__(self, template_path: str = "config/invoice_template.html"):
        """
        تهيئة محرك المستندات
        
        Args:
            template_path: مسار قالب HTML الفاتورة
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, "r", encoding="utf-8") as f:
            self.template = Template(f.read())
        
        logger.info(f"✅ DocumentEngine initialized with template: {template_path}")
    
    def render_invoice_html(
        self,
        invoice_number: str,
        client_name: str,
        client_contact: str,
        items: list[dict]
    ) -> str:
        """
        تحويل بيانات الفاتورة إلى HTML
        Render invoice to HTML with all security elements
        
        Args:
            invoice_number: رقم الفاتورة
            client_name: اسم العميل
            client_contact: بيانات الاتصال
            items: قائمة البنود [{description, quantity, unit_price}, ...]
        
        Returns:
            HTML string ready for PDF conversion
        """
        # حساب المجاميع
        subtotal = sum(item["quantity"] * item["unit_price"] for item in items)
        tax = subtotal * BRAND.tax_rate
        total = subtotal + tax
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # توليد عناصر الأمان
        security_code = generate_document_seal_code(invoice_number, total, date_str)
        qr_uri = generate_verification_qr(invoice_number, total, date_str, security_code)
        
        # معالجة الأصول بالعلامات المائية
        logo_uri = get_logo_data_uri("assets/logo.png")
        stamp_uri = get_secure_stamped_asset("assets/stamp.png", security_code, is_signature=False)
        signature_uri = get_secure_stamped_asset("assets/signature.png", security_code, is_signature=True)
        
        logger.info(f"📄 Rendering invoice: {invoice_number}, Total: {total:.2f} {BRAND.currency}")
        
        # حقن البيانات في القالب
        return self.template.render(
            brand=BRAND,
            invoice_number=invoice_number,
            date=date_str,
            security_code=security_code,
            client_name=client_name,
            client_contact=client_contact,
            items=items,
            subtotal=f"{subtotal:.2f}",
            tax=f"{tax:.2f}",
            total=f"{total:.2f}",
            qr_uri=qr_uri,
            logo_uri=logo_uri,
            signature_uri=signature_uri,
            stamp_uri=stamp_uri
        )
    
    async def generate_invoice_pdf(
        self,
        invoice_number: str,
        client_name: str,
        client_contact: str,
        items: list[dict]
    ) -> BytesIO:
        """
        توليد فاتورة بصيغة PDF مع جودة عالية
        Generate PDF invoice with high quality using Playwright
        
        Returns:
            BytesIO object containing PDF bytes
        """
        try:
            html_content = self.render_invoice_html(
                invoice_number, client_name, client_contact, items
            )
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-gpu",
                        "--disable-dev-shm-usage"  # لتقليل استهلاك الذاكرة
                    ]
                )
                
                page = await browser.new_page()
                
                # تحميل المحتوى مع انتظار تحميل الخطوط
                await page.set_content(html_content, wait_until="networkidle")
                await page.evaluate("document.fonts.ready")
                
                # تحويل إلى PDF بجودة عالية
                pdf_bytes = await page.pdf(
                    format="A4",
                    print_background=True,
                    margin={
                        "top": "15px",
                        "bottom": "15px",
                        "left": "10px",
                        "right": "10px"
                    }
                )
                
                await browser.close()
            
            logger.info(f"✅ PDF generated successfully for {invoice_number}")
            return BytesIO(pdf_bytes)
        
        except Exception as e:
            logger.error(f"❌ Error generating PDF: {str(e)}", exc_info=True)
            raise
