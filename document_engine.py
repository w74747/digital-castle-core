import json
import base64
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from io import BytesIO
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# ============================================
# Pydantic Models
# ============================================

class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    
    @property
    def total(self) -> float:
        return self.quantity * self.unit_price


class InvoiceData(BaseModel):
    invoice_number: str
    issue_date: str
    due_date: str
    client_name: str
    client_email: str
    client_address: str
    items: List[InvoiceItem]
    tax_rate: float = 5.0  # نسبة الضريبة الافتراضية
    currency: str = "OMR"
    
    @property
    def subtotal(self) -> float:
        return sum(item.total for item in self.items)
    
    @property
    def tax_amount(self) -> float:
        return self.subtotal * (self.tax_rate / 100)
    
    @property
    def total(self) -> float:
        return self.subtotal + self.tax_amount


# ============================================
# Document Engine
# ============================================

class DocumentEngine:
    """
    محرك توليد المستندات الرسمية عبر Jinja2 و WeasyPrint
    Generates official Digital Castle S.P.C documents
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.templates_path = self.base_path / "brand-kit" / "templates"
        self.assets_path = self.base_path / "assets"
        self.brand_guidelines_path = self.base_path / "brand-kit" / "brand_guidelines.json"
        
        # تحميل معايير الهوية
        self.brand_guidelines = self._load_brand_guidelines()
        
        # إعداد Jinja2
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_path)),
            autoescape=True
        )
        
        logger.info(f"✅ DocumentEngine initialized with base_path: {self.base_path}")
    
    def _load_brand_guidelines(self) -> Dict:
        """تحميل معايير الهوية المؤسسية"""
        try:
            with open(self.brand_guidelines_path, 'r', encoding='utf-8') as f:
                guidelines = json.load(f)
            logger.info("✅ Brand guidelines loaded successfully")
            return guidelines
        except FileNotFoundError:
            logger.error(f"❌ Brand guidelines file not found: {self.brand_guidelines_path}")
            return {}
    
    def _load_asset_as_base64(self, asset_filename: str) -> Optional[str]:
        """تحويل الأصول إلى Base64 للإدراج في HTML"""
        asset_path = self.assets_path / asset_filename
        
        if not asset_path.exists():
            logger.warning(f"⚠️ Asset not found: {asset_filename}")
            return None
        
        try:
            with open(asset_path, 'rb') as f:
                content = f.read()
            base64_content = base64.b64encode(content).decode('utf-8')
            logger.info(f"✅ Asset loaded as Base64: {asset_filename}")
            return base64_content
        except Exception as e:
            logger.error(f"❌ Failed to load asset {asset_filename}: {str(e)}")
            return None
    
    def generate_invoice_pdf(
        self, 
        invoice_data: InvoiceData,
        include_logo: bool = True,
        include_signature: bool = True,
        include_stamp: bool = True
    ) -> BytesIO:
        """
        توليد فاتورة رسمية بصيغة PDF
        
        Args:
            invoice_data: بيانات الفاتورة
            include_logo: إدراج الشعار
            include_signature: إدراج التوقيع
            include_stamp: إدراج الختم الرسمي
        
        Returns:
            BytesIO object containing PDF bytes
        """
        try:
            # تحضير بيانات الأصول
            context = {
                **invoice_data.model_dump(),
                'logo_base64': self._load_asset_as_base64('logo.svg') if include_logo else None,
                'signature_base64': self._load_asset_as_base64('signature.png') if include_signature else None,
                'stamp_base64': self._load_asset_as_base64('stamp.png') if include_stamp else None,
                'brand': self.brand_guidelines,
            }
            
            # تحميل القالب وحقن البيانات
            template = self.jinja_env.get_template('invoice.html')
            html_content = template.render(**context)
            
            # تحويل إلى PDF مع WeasyPrint
            html_doc = HTML(string=html_content)
            
            # إعدادات الطباعة عالية الجودة
            pdf_bytes = html_doc.write_pdf(
                resolution=300,  # DPI عالي للطباعة
                optimize_size=['shapes'],  # تحسين الحجم
            )
            
            pdf_io = BytesIO(pdf_bytes)
            pdf_io.seek(0)
            
            logger.info(f"✅ Invoice PDF generated successfully: {invoice_data.invoice_number}")
            return pdf_io
        
        except Exception as e:
            logger.error(f"❌ Failed to generate invoice PDF: {str(e)}")
            raise
    
    def generate_invoice_html(
        self, 
        invoice_data: InvoiceData,
        include_logo: bool = True,
        include_signature: bool = True,
        include_stamp: bool = True
    ) -> str:
        """
        توليد فاتورة بصيغة HTML (للمعاينة)
        """
        try:
            context = {
                **invoice_data.model_dump(),
                'logo_base64': self._load_asset_as_base64('logo.svg') if include_logo else None,
                'signature_base64': self._load_asset_as_base64('signature.png') if include_signature else None,
                'stamp_base64': self._load_asset_as_base64('stamp.png') if include_stamp else None,
                'brand': self.brand_guidelines,
            }
            
            template = self.jinja_env.get_template('invoice.html')
            html_content = template.render(**context)
            
            logger.info(f"✅ Invoice HTML generated successfully: {invoice_data.invoice_number}")
            return html_content
        
        except Exception as e:
            logger.error(f"❌ Failed to generate invoice HTML: {str(e)}")
            raise


# ============================================
# مثال الاستخدام
# ============================================

def create_sample_invoice() -> InvoiceData:
    """إنشاء فاتورة تجريبية للاختبار"""
    return InvoiceData(
        invoice_number="INV-2025-001",
        issue_date="2025-01-15",
        due_date="2025-02-15",
        client_name="عميل تجريبي",
        client_email="client@example.com",
        client_address="مسقط، سلطنة عمان",
        items=[
            InvoiceItem(
                description="استشارة معمارية - تصميم النظام",
                quantity=10,
                unit_price=50.0
            ),
            InvoiceItem(
                description="تطوير واجهة المستخدم (React)",
                quantity=20,
                unit_price=75.0
            ),
            InvoiceItem(
                description="اختبار الجودة والأداء",
                quantity=8,
                unit_price=60.0
            ),
        ],
        tax_rate=5.0
    )


if __name__ == "__main__":
    # اختبار محرك المستندات
    engine = DocumentEngine()
    sample_invoice = create_sample_invoice()
    
    # توليد PDF
    pdf_io = engine.generate_invoice_pdf(sample_invoice)
    
    # حفظ الـ PDF (للاختبار المحلي فقط)
    with open("sample_invoice.pdf", "wb") as f:
        f.write(pdf_io.getvalue())
    
    print("✅ Sample invoice generated: sample_invoice.pdf")
