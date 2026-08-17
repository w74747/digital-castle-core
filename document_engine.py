"""
Document Engine - Simple & Realistic Version
Digital Castle S.P.C - Invoice Generation
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from io import BytesIO
from jinja2 import Template

logger = logging.getLogger(__name__)

class DocumentEngine:
    """محرك توليد المستندات - نسخة بسيطة وواقعية"""
    
    def __init__(
        self,
        template_path: str = "brand-kit/templates/invoice.html",
        brand_guidelines_path: str = "brand-kit/brand_guidelines.json"
    ):
        self.template_path = Path(template_path)
        self.brand_guidelines_path = brand_guidelines_path
        self.template = self._load_template()
        self.brand_guidelines = self._load_brand_guidelines()
        logger.info("✅ DocumentEngine initialized")
    
    def _load_template(self) -> Template:
        """تحميل قالب HTML"""
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        
        with open(self.template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"✅ Template loaded from {self.template_path}")
        return Template(content)
    
    def _load_brand_guidelines(self) -> Dict:
        """تحميل معايير الهوية"""
        try:
            with open(self.brand_guidelines_path, 'r', encoding='utf-8') as f:
                guidelines = json.load(f)
            logger.info("✅ Brand guidelines loaded")
            return guidelines
        except FileNotFoundError:
            logger.warning(f"⚠️ Brand guidelines not found, using defaults")
            return self._get_default_brand()
    
    @staticmethod
    def _get_default_brand() -> Dict:
        """إعدادات افتراضية"""
        return {
            "company": {
                "name_ar": "شركة القلعة الرقمية ش.ش.و",
                "name_en": "Digital Castle S.P.C",
                "registration_number": "1197389"
            },
            "colors": {
                "primary": "#071033",
                "secondary": "#0025FF",
                "accent": "#08F9F2"
            }
        }
    
    def render_invoice_html(
        self,
        invoice_number: str,
        client_name: str,
        client_email: str,
        client_contact: str,
        items: List[Dict],
        issue_date: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> str:
        """تحويل بيانات الفاتورة إلى HTML"""
        try:
            # حساب المجاميع
            subtotal = sum(item.get("quantity", 0) * item.get("unit_price", 0) for item in items)
            tax = subtotal * 0.05
            total = subtotal + tax
            
            # التواريخ
            if not issue_date:
                issue_date = datetime.now().strftime("%d %b %Y")
            if not due_date:
                due_date = (datetime.now() + __import__('datetime').timedelta(days=30)).strftime("%d %b %Y")
            
            # حقن البيانات
            html = self.template.render(
                invoice_number=invoice_number,
                issue_date=issue_date,
                due_date=due_date,
                client_name=client_name,
                client_email=client_email,
                client_contact=client_contact,
                items=items,
                subtotal=f"{subtotal:.3f}",
                tax=f"{tax:.3f}",
                total=f"{total:.3f}"
            )
            
            logger.info(f"✅ HTML rendered for invoice {invoice_number}")
            return html
        
        except Exception as e:
            logger.error(f"❌ Error rendering HTML: {str(e)}")
            raise
    
    async def generate_invoice_pdf(
        self,
        invoice_number: str,
        client_name: str,
        client_email: str,
        client_contact: str,
        items: List[Dict],
        issue_date: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> BytesIO:
        """توليد فاتورة بصيغة PDF باستخدام Playwright"""
        try:
            from playwright.async_api import async_playwright
            
            html_content = self.render_invoice_html(
                invoice_number=invoice_number,
                client_name=client_name,
                client_email=client_email,
                client_contact=client_contact,
                items=items,
                issue_date=issue_date,
                due_date=due_date
            )
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox"]
                )
                
                page = await browser.new_page()
                await page.set_content(html_content, wait_until="networkidle")
                
                pdf_bytes = await page.pdf(
                    format="A4",
                    print_background=True,
                    margin={"top": "20px", "bottom": "20px", "left": "20px", "right": "20px"}
                )
                
                await browser.close()
            
            logger.info(f"✅ PDF generated for {invoice_number}")
            return BytesIO(pdf_bytes)
        
        except ImportError:
            logger.error("❌ Playwright not installed. Install with: pip install playwright")
            raise
        except Exception as e:
            logger.error(f"❌ Error generating PDF: {str(e)}")
            raise


# مثال الاستخدام
async def example_usage():
    """مثال بسيط"""
    engine = DocumentEngine()
    
    sample_items = [
        {
            "description": "Platform architecture & technical design authority",
            "quantity": 1,
            "unit_price": 4500.0
        },
        {
            "description": "Autonomous engineering team - retained capacity",
            "quantity": 4,
            "unit_price": 1250.0
        },
        {
            "description": "Infrastructure & third-party licenses",
            "quantity": 1,
            "unit_price": 640.50
        }
    ]
    
    pdf = await engine.generate_invoice_pdf(
        invoice_number="DC-INV-2026-0114",
        client_name="Client Legal Entity Name",
        client_email="contact@client.om",
        client_contact="Attn. Authorised Signatory",
        items=sample_items,
        issue_date="14 Aug 2026",
        due_date="13 Sep 2026"
    )
    
    with open("sample_invoice.pdf", "wb") as f:
        f.write(pdf.getvalue())
    
    print("✅ Sample invoice generated: sample_invoice.pdf")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example_usage())
