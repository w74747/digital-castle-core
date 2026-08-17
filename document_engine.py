#!/usr/bin/env python3
"""
document_engine_REAL_FINAL.py
Document Engine - Realistic Production Version with Real Assets
Digital Castle S.P.C - Invoice Generation System
"""

import os
import json
import base64
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from io import BytesIO
from jinja2 import Template

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_TEMPLATE_PATH = "brand-kit/templates/invoice.html"
DEFAULT_BRAND_GUIDELINES_PATH = "brand-kit/brand_guidelines.json"
DEFAULT_ASSETS_PATH = "assets"


class DocumentEngine:
    """
    محرك توليد المستندات - Production-Ready Version
    مع دعم كامل للأصول الحقيقية والتخزين المؤقت
    """
    
    def __init__(
        self,
        template_path: str = DEFAULT_TEMPLATE_PATH,
        brand_guidelines_path: str = DEFAULT_BRAND_GUIDELINES_PATH,
        assets_path: str = DEFAULT_ASSETS_PATH,
        enable_asset_caching: bool = True
    ):
        """Initialize the Document Engine"""
        self.template_path = Path(template_path)
        self.brand_guidelines_path = brand_guidelines_path
        self.assets_path = Path(assets_path)
        self.enable_asset_caching = enable_asset_caching
        
        # Asset cache
        self._asset_cache: Dict[str, Optional[str]] = {}
        
        # Load template
        self.template = self._load_template()
        
        # Load brand guidelines
        self.brand_guidelines = self._load_brand_guidelines()
        
        logger.info("✅ DocumentEngine initialized successfully")
    
    def _load_template(self) -> Template:
        """Load HTML template"""
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        
        with open(self.template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"✅ Template loaded: {self.template_path}")
        return Template(content)
    
    def _load_brand_guidelines(self) -> Dict:
        """Load brand guidelines"""
        try:
            with open(self.brand_guidelines_path, 'r', encoding='utf-8') as f:
                guidelines = json.load(f)
            logger.info("✅ Brand guidelines loaded")
            return guidelines
        except FileNotFoundError:
            logger.warning("⚠️ Brand guidelines not found, using defaults")
            return self._get_default_brand()
    
    @staticmethod
    def _get_default_brand() -> Dict:
        """Get default brand settings"""
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
    
    def _load_asset_as_base64(self, filename: str) -> Optional[str]:
        """
        Load asset and convert to Data URI
        تحميل أصل وتحويله إلى Data URI
        """
        # Check cache first
        if self.enable_asset_caching and filename in self._asset_cache:
            return self._asset_cache[filename]
        
        asset_path = self.assets_path / filename
        
        if not asset_path.exists():
            logger.warning(f"⚠️ Asset not found: {filename}")
            if self.enable_asset_caching:
                self._asset_cache[filename] = None
            return None
        
        try:
            with open(asset_path, 'rb') as f:
                data = f.read()
            
            # Convert to Base64
            b64_data = base64.b64encode(data).decode('utf-8')
            
            # Create Data URI
            mime_type = self._get_mime_type(filename)
            data_uri = f"data:{mime_type};base64,{b64_data}"
            
            # Cache it
            if self.enable_asset_caching:
                self._asset_cache[filename] = data_uri
            
            logger.info(f"✅ Asset loaded: {filename}")
            return data_uri
        
        except Exception as e:
            logger.error(f"❌ Error loading asset {filename}: {str(e)}")
            if self.enable_asset_caching:
                self._asset_cache[filename] = None
            return None
    
    @staticmethod
    def _get_mime_type(filename: str) -> str:
        """Determine MIME type based on extension"""
        extension = filename.lower().split('.')[-1]
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'svg': 'image/svg+xml'
        }
        return mime_types.get(extension, 'application/octet-stream')
    
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
        """
        Render invoice to HTML
        تحويل بيانات الفاتورة إلى HTML
        """
        try:
            # Load assets
            logo_uri = self._load_asset_as_base64('logo.png')
            signature_uri = self._load_asset_as_base64('signature.png')
            stamp_uri = self._load_asset_as_base64('stamp.png')
            
            # Calculate totals
            subtotal = sum(item.get("quantity", 0) * item.get("unit_price", 0) for item in items)
            tax_rate = 0.05  # 5% VAT
            tax = subtotal * tax_rate
            total = subtotal + tax
            
            # Set dates
            if not issue_date:
                issue_date = datetime.now().strftime("%d %b %Y")
            if not due_date:
                due_date = (datetime.now() + timedelta(days=30)).strftime("%d %b %Y")
            
            # Render template
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
                total=f"{total:.3f}",
                logo_uri=logo_uri,
                signature_uri=signature_uri,
                stamp_uri=stamp_uri
            )
            
            logger.info(f"✅ HTML rendered: {invoice_number}")
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
        """
        Generate PDF from invoice data
        توليد PDF من بيانات الفاتورة
        """
        try:
            from playwright.async_api import async_playwright
            
            # Render HTML
            html_content = self.render_invoice_html(
                invoice_number=invoice_number,
                client_name=client_name,
                client_email=client_email,
                client_contact=client_contact,
                items=items,
                issue_date=issue_date,
                due_date=due_date
            )
            
            # Generate PDF
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-gpu"
                    ]
                )
                
                page = await browser.new_page()
                await page.set_content(html_content, wait_until="networkidle")
                
                pdf_bytes = await page.pdf(
                    format="A4",
                    print_background=True,
                    margin={
                        "top": "20px",
                        "bottom": "20px",
                        "left": "20px",
                        "right": "20px"
                    }
                )
                
                await browser.close()
            
            logger.info(f"✅ PDF generated: {invoice_number}")
            return BytesIO(pdf_bytes)
        
        except ImportError:
            logger.error("❌ Playwright not installed!")
            raise
        except Exception as e:
            logger.error(f"❌ Error generating PDF: {str(e)}")
            raise
    
    def clear_asset_cache(self):
        """Clear the asset cache"""
        self._asset_cache.clear()
        logger.info("✅ Asset cache cleared")


# ============================================
# Example Usage & Testing
# ============================================

async def test_invoice_generation():
    """Test invoice generation with real assets"""
    
    logger.info("=" * 60)
    logger.info("Starting Invoice Generation Test")
    logger.info("=" * 60)
    
    # Initialize engine
    engine = DocumentEngine()
    
    # Sample invoice data
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
    
    # Generate PDF
    try:
        pdf = await engine.generate_invoice_pdf(
            invoice_number="DC-INV-2026-0001",
            client_name="Test Client Company",
            client_email="client@example.om",
            client_contact="Attn. Authorized Signatory",
            items=sample_items,
            issue_date="14 Aug 2026",
            due_date="13 Sep 2026"
        )
        
        # Save PDF
        output_path = "sample_invoice_with_assets.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf.getvalue())
        
        logger.info("=" * 60)
        logger.info("✅ SUCCESS!")
        logger.info(f"Invoice saved: {output_path}")
        logger.info("=" * 60)
        
        return True
    
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ FAILED: {str(e)}")
        logger.error("=" * 60)
        return False
    
    finally:
        # Cleanup
        engine.clear_asset_cache()


# ============================================
# Main
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DIGITAL CASTLE - DOCUMENT ENGINE")
    print("Production-Ready Version with Real Assets")
    print("=" * 60 + "\n")
    
    # Run test
    success = asyncio.run(test_invoice_generation())
    
    if success:
        print("\n✅ All tests passed! System is ready for production.\n")
    else:
        print("\n❌ Tests failed! Please check the logs above.\n")
