"""
Document Engine - محرك توليد المستندات الرسمية والفواتير
يستخدم Jinja2 و WeasyPrint لتحويل القوالب إلى ملفات PDF عالية الجودة
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from decimal import Decimal

import jinja2
from weasyprint import HTML, CSS
from PIL import Image
import io


class DocumentEngine:
    """محرك توليد المستندات الرسمية بهوية Digital Castle S.P.C"""

    def __init__(self, base_path: str = "."):
        """
        تهيئة محرك المستندات
        
        Args:
            base_path: المسار الأساسي للمشروع
        """
        self.base_path = Path(base_path)
        self.brand_path = self.base_path / "brand-kit"
        self.assets_path = self.base_path / "assets"
        self.templates_path = self.brand_path / "templates"
        
        # تحميل إرشادات الهوية
        self.brand_guidelines = self._load_brand_guidelines()
        
        # إعداد Jinja2
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_path)),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            enable_async=False,
        )
        
        # إضافة مرشحات مخصصة
        self.jinja_env.filters['format_currency'] = self._format_currency
        self.jinja_env.filters['format_date'] = self._format_date
        self.jinja_env.globals['now'] = datetime.now
    
    def _load_brand_guidelines(self) -> Dict[str, Any]:
        """تحميل ملف معايير الهوية"""
        guidelines_path = self.brand_path / "brand_guidelines.json"
        try:
            with open(guidelines_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Brand guidelines not found at {guidelines_path}. "
                "Please ensure brand-kit/brand_guidelines.json exists."
            )
    
    @staticmethod
    def _format_currency(value: float, currency: str = "OMR") -> str:
        """تنسيق القيم النقدية"""
        if isinstance(value, Decimal):
            value = float(value)
        return f"{value:,.2f} {currency}"
    
    @staticmethod
    def _format_date(date_obj, date_format: str = "%Y-%m-%d") -> str:
        """تنسيق التواريخ"""
        if isinstance(date_obj, str):
            return date_obj
        return date_obj.strftime(date_format)
    
    def _get_asset_path(self, asset_name: str) -> str:
        """الحصول على المسار الكامل للأصل"""
        asset_path = self.assets_path / asset_name
        if not asset_path.exists():
            raise FileNotFoundError(f"Asset '{asset_name}' not found at {asset_path}")
        return str(asset_path)
    
    def validate_invoice_data(self, invoice_data: Dict[str, Any]) -> bool:
        """التحقق من سلامة بيانات الفاتورة"""
        required_fields = [
            'invoice_number', 'date', 'due_date', 'currency',
            'client_name', 'client_email', 'client_phone', 'client_address',
            'items'
        ]
        
        for field in required_fields:
            if field not in invoice_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(invoice_data['items'], list) or len(invoice_data['items']) == 0:
            raise ValueError("Invoice must contain at least one item")
        
        for idx, item in enumerate(invoice_data['items']):
            item_fields = ['description', 'quantity', 'unit_price', 'amount']
            for field in item_fields:
                if field not in item:
                    raise ValueError(f"Item {idx} missing field: {field}")
        
        return True
    
    def calculate_totals(self, invoice_data: Dict[str, Any]) -> Dict[str, float]:
        """حساب الإجماليات (مبلغ جزئي، ضريبة، إجمالي)"""
        subtotal = sum(
            float(item['amount']) for item in invoice_data['items']
        )
        
        tax_rate = float(invoice_data.get('tax_rate', 0))
        tax = (subtotal * tax_rate) / 100
        
        discount = float(invoice_data.get('discount', 0))
        
        total = subtotal + tax - discount
        
        return {
            'subtotal': round(subtotal, 2),
            'tax': round(tax, 2),
            'discount': round(discount, 2),
            'total': round(total, 2),
            'tax_rate': tax_rate
        }
    
    def generate_invoice_pdf(
        self,
        invoice_data: Dict[str, Any],
        output_path: Optional[str] = None,
        template_name: str = "invoice.html"
    ) -> bytes:
        """
        توليد فاتورة PDF رسمية
        
        Args:
            invoice_data: بيانات الفاتورة
            output_path: مسار الحفظ (اختياري، إذا لم يُحدد سيتم إرجاع البايتات)
            template_name: اسم القالب المراد استخدامه
        
        Returns:
            بيانات PDF كـ bytes
        """
        # التحقق من البيانات
        self.validate_invoice_data(invoice_data)
        
        # حساب الإجماليات
        totals = self.calculate_totals(invoice_data)
        invoice_data.update(totals)
        
        # إضافة بيانات الشركة والأصول
        context = {
            'company': self.brand_guidelines['company'],
            'invoice': invoice_data,
            'logo_path': self._get_asset_path('logo.svg'),
            'signature_path': self._get_asset_path('signature.png'),
            'stamp_path': self._get_asset_path('stamp.png'),
            'brand_guidelines': self.brand_guidelines
        }
        
        # تحميل وتصيير القالب
        template = self.jinja_env.get_template(template_name)
        html_content = template.render(**context)
        
        # تحويل HTML إلى PDF باستخدام WeasyPrint
        html_doc = HTML(string=html_content)
        
        # تطبيق إعدادات CSS
        css_styles = self._get_css_styles()
        
        pdf_bytes = html_doc.write_pdf(stylesheets=[css_styles])
        
        # حفظ الملف إذا تم تحديد مسار الحفظ
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)
            print(f"✅ Invoice generated successfully: {output_path}")
        
        return pdf_bytes
    
    def _get_css_styles(self) -> CSS:
        """إرجاع أنماط CSS إضافية للـ PDF"""
        brand = self.brand_guidelines
        colors = brand['color_palette']
        
        css_string = f"""
        @page {{
            size: A4;
            margin: {brand['document_standards']['margin_top']} 
                    {brand['document_standards']['margin_right']} 
                    {brand['document_standards']['margin_bottom']} 
                    {brand['document_standards']['margin_left']};
        }}
        
        body {{
            font-family: 'Cairo', 'Inter', sans-serif;
            color: {colors['primary']['hex']};
            line-height: {brand['document_standards']['line_height']};
        }}
        """
        
        return CSS(string=css_string)
    
    def generate_sample_invoice(self) -> bytes:
        """توليد فاتورة تجريبية للاختبار"""
        sample_invoice = {
            'invoice_number': 'DC-2024-000001',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'due_date': '2024-02-15',
            'currency': 'OMR',
            'client_name': 'Acme Corporation Limited',
            'client_email': 'billing@acme.example.com',
            'client_phone': '+968 9123 4567',
            'client_address': 'Muscat, Sultanate of Oman',
            'items': [
                {
                    'description': 'SaaS Platform - Monthly Subscription',
                    'quantity': 1,
                    'unit_price': 299.99,
                    'amount': 299.99
                },
                {
                    'description': 'API Integration Support',
                    'quantity': 5,
                    'unit_price': 50.00,
                    'amount': 250.00
                },
                {
                    'description': 'Custom Feature Development',
                    'quantity': 10,
                    'unit_price': 150.00,
                    'amount': 1500.00
                }
            ],
            'tax_rate': 5,
            'discount': 0,
            'notes': 'Payment terms: Net 30 days. Thank you for your business!'
        }
        
        return self.generate_invoice_pdf(sample_invoice)


# متغير عام للمحرك (Singleton)
_engine_instance = None

def get_document_engine() -> DocumentEngine:
    """الحصول على نسخة فريدة من محرك المستندات"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = DocumentEngine()
    return _engine_instance
