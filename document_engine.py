import json
from datetime import datetime
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
from typing import Dict, Any, Optional, List
import logging
from config import (
    COMPANY_NAME, COMPANY_AR_NAME, BRAND_COLORS,
    PROJECT_DIRS
)

logger = logging.getLogger(__name__)

class DocumentEngine:
    """محرك توليد المستندات والفواتير الرسمية بهوية Digital Castle S.P.C"""
    
    def __init__(self):
        self.company_name = COMPANY_NAME
        self.company_ar_name = COMPANY_AR_NAME
        self.brand_colors = BRAND_COLORS
        self.template_dir = PROJECT_DIRS['templates']
        self.docs_dir = PROJECT_DIRS['docs']
        
        # إنشاء مجلدات إذا لم تكن موجودة
        Path(self.template_dir).mkdir(parents=True, exist_ok=True)
        Path(self.docs_dir).mkdir(parents=True, exist_ok=True)
        
        self._load_brand_guidelines()
    
    def _load_brand_guidelines(self):
        """تحميل معايير الهوية البصرية"""
        guidelines_path = Path(self.template_dir).parent / 'brand_guidelines.json'
        
        if guidelines_path.exists():
            with open(guidelines_path, 'r', encoding='utf-8') as f:
                self.guidelines = json.load(f)
        else:
            self.guidelines = {
                'company_name': self.company_name,
                'company_ar': self.company_ar_name,
                'logo': 'assets/logo.svg',
                'signature': 'assets/signature.png',
                'stamp': 'assets/stamp.png',
                'colors': self.brand_colors,
                'fonts': {
                    'heading': 'Segoe UI, Arial',
                    'body': 'Segoe UI, Arial',
                    'mono': 'Courier New, monospace'
                },
                'language': 'ar',
                'direction': 'rtl'
            }

    def generate_invoice(
        self,
        invoice_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        توليد فاتورة رسمية
        
        invoice_data:
        {
            'invoice_number': '001',
            'invoice_date': '2024-01-15',
            'due_date': '2024-02-15',
            'client': {
                'name': 'اسم العميل',
                'address': 'العنوان',
                'tax_id': 'رقم التسجيل',
                'email': 'email@example.com'
            },
            'items': [
                {
                    'description': 'وصف الخدمة',
                    'quantity': 1,
                    'unit_price': 1000,
                    'tax_rate': 0.05
                }
            ],
            'notes': 'ملاحظات إضافية',
            'payment_terms': 'شروط الدفع'
        }
        """
        
        try:
            # حساب الإجماليات
            subtotal = sum(
                item['quantity'] * item['unit_price'] 
                for item in invoice_data['items']
            )
            tax = sum(
                item['quantity'] * item['unit_price'] * item.get('tax_rate', 0)
                for item in invoice_data['items']
            )
            total = subtotal + tax
            
            # بناء بيانات المستند
            doc_data = {
                **invoice_data,
                'subtotal': subtotal,
                'tax': tax,
                'total': total,
                'company_name': self.company_name,
                'company_ar': self.company_ar_name,
                'logo_url': self.guidelines.get('logo'),
                'signature_url': self.guidelines.get('signature'),
                'stamp_url': self.guidelines.get('stamp'),
                'brand_colors': self.brand_colors,
                'current_date': datetime.now().strftime('%Y-%m-%d'),
                'language': 'ar',
                'direction': 'rtl'
            }
            
            # قالب الفاتورة بصيغة HTML
            html_template = """
<!DOCTYPE html>
<html dir="{direction}" lang="ar">
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; direction: {direction}; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 3px solid {primary_color}; padding-bottom: 20px; }}
        .logo {{ width: 120px; height: 120px; }}
        .company-info {{ flex: 1; text-align: center; }}
        .company-info h1 {{ color: {primary_color}; font-size: 28px; margin-bottom: 5px; }}
        .company-info p {{ color: #666; font-size: 12px; }}
        .invoice-title {{ text-align: center; color: {primary_color}; font-size: 22px; font-weight: bold; margin: 20px 0; }}
        .invoice-details {{ display: flex; justify-content: space-between; margin-bottom: 30px; }}
        .detail-box {{ flex: 1; margin: 0 10px; }}
        .detail-box h3 {{ color: {primary_color}; font-size: 14px; margin-bottom: 8px; }}
        .detail-box p {{ font-size: 12px; color: #333; line-height: 1.6; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th {{ background-color: {primary_color}; color: white; padding: 12px; text-align: right; font-weight: bold; }}
        td {{ border-bottom: 1px solid #ddd; padding: 10px; text-align: right; }}
        tr:last-child td {{ border-bottom: none; }}
        .totals {{ text-align: left; margin-bottom: 20px; }}
        .total-row {{ display: flex; justify-content: space-between; margin: 10px 0; font-weight: bold; }}
        .total-amount {{ color: {primary_color}; font-size: 18px; }}
        .footer {{ border-top: 2px solid {primary_color}; padding-top: 20px; margin-top: 30px; text-align: center; color: #666; font-size: 11px; }}
        .stamp {{ position: absolute; bottom: 50px; right: 30px; opacity: 0.3; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <img src="{logo_url}" alt="Logo" style="width: 100%; height: auto;">
            </div>
            <div class="company-info">
                <h1>{company_ar}</h1>
                <p>{company_name}</p>
            </div>
        </div>
        
        <div class="invoice-title">فاتورة رقم #{invoice_number}</div>
        
        <div class="invoice-details">
            <div class="detail-box">
                <h3>بيانات العميل</h3>
                <p><strong>{client_name}</strong></p>
                <p>{client_address}</p>
                <p>رقم التسجيل: {client_tax_id}</p>
                <p>{client_email}</p>
            </div>
            <div class="detail-box">
                <h3>بيانات الفاتورة</h3>
                <p>رقم الفاتورة: #{invoice_number}</p>
                <p>تاريخ الإصدار: {invoice_date}</p>
                <p>تاريخ الاستحقاق: {due_date}</p>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>السعر الإجمالي</th>
                    <th>معدل الضريبة</th>
                    <th>السعر الفردي</th>
                    <th>الكمية</th>
                    <th>الوصف</th>
                </tr>
            </thead>
            <tbody>
                {items_rows}
            </tbody>
        </table>
        
        <div class="totals">
            <div class="total-row">
                <span>المجموع الجزئي:</span>
                <span>{subtotal:.2f} ريال</span>
            </div>
            <div class="total-row">
                <span>الضريبة:</span>
                <span>{tax:.2f} ريال</span>
            </div>
            <div class="total-row total-amount">
                <span>الإجمالي:</span>
                <span>{total:.2f} ريال</span>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>شروط الدفع:</strong> {payment_terms}</p>
            <p><strong>ملاحظات:</strong> {notes}</p>
            <p>تم التوقيع رسمياً من قبل {company_ar}</p>
            <img src="{stamp_url}" alt="Stamp" class="stamp" style="width: 100px; height: auto;">
        </div>
    </div>
</body>
</html>
            """
            
            # إعداد صفوف الجدول
            items_rows = ""
            for item in invoice_data['items']:
                item_total = item['quantity'] * item['unit_price']
                item_tax = item_total * item.get('tax_rate', 0)
                items_rows += f"""
                <tr>
                    <td>{item_total + item_tax:.2f} ريال</td>
                    <td>{item.get('tax_rate', 0) * 100:.0f}%</td>
                    <td>{item['unit_price']:.2f} ريال</td>
                    <td>{item['quantity']}</td>
                    <td>{item['description']}</td>
                </tr>
                """
            
            doc_data['items_rows'] = items_rows
            
            # ملء القالب
            html = html_template.format(
                direction='rtl',
                primary_color=self.brand_colors['primary'],
                **doc_data
            )
            
            # حفظ الملف
            if not output_path:
                output_path = f"{self.docs_dir}/invoice_{invoice_data['invoice_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"Invoice generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating invoice: {str(e)}")
            raise

    def generate_proposal(
        self,
        proposal_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """توليد عرض فني ومالي احترافي"""
        
        try:
            doc_data = {
                **proposal_data,
                'company_name': self.company_name,
                'company_ar': self.company_ar_name,
                'logo_url': self.guidelines.get('logo'),
                'signature_url': self.guidelines.get('signature'),
                'stamp_url': self.guidelines.get('stamp'),
                'brand_colors': self.brand_colors,
                'current_date': datetime.now().strftime('%Y-%m-%d'),
                'direction': 'rtl'
            }
            
            html_template = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; direction: rtl; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ text-align: center; border-bottom: 3px solid {primary_color}; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ color: {primary_color}; font-size: 32px; margin: 10px 0; }}
        .header img {{ width: 150px; height: auto; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: {primary_color}; font-size: 20px; border-left: 5px solid {primary_color}; padding-left: 15px; margin-bottom: 15px; }}
        .section p {{ line-height: 1.8; color: #333; font-size: 14px; }}
        .highlight {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .signature {{ margin-top: 50px; text-align: left; }}
        .signature-line {{ border-top: 2px solid #333; width: 200px; margin-top: 30px; }}
        .footer {{ border-top: 2px solid {primary_color}; padding-top: 20px; margin-top: 40px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{logo_url}" alt="Logo">
            <h1>{company_ar}</h1>
            <p>{company_name}</p>
        </div>
        
        <div class="section">
            <h2>عرض التسعير والخدمات</h2>
            <p><strong>العميل:</strong> {client_name}</p>
            <p><strong>التاريخ:</strong> {current_date}</p>
            <p><strong>موضوع العرض:</strong> {subject}</p>
        </div>
        
        <div class="section">
            <h2>ملخص التكاليف</h2>
            <div class="highlight">
                <p><strong>التكلفة الإجمالية:</strong> {total_cost:.2f} ريال</p>
                <p><strong>مدة التنفيذ:</strong> {duration}</p>
                <p><strong>صلاحية العرض:</strong> {validity_days} يوم</p>
            </div>
        </div>
        
        <div class="section">
            <h2>تفاصيل الخدمات</h2>
            {services_html}
        </div>
        
        <div class="signature">
            <p>وافقاً من:</p>
            <p><strong>{company_ar}</strong></p>
            <div class="signature-line"></div>
            <p>التوقيع والختم</p>
        </div>
        
        <div class="footer">
            <p>© {company_ar} - جميع الحقوق محفوظة</p>
            <p>{current_date}</p>
        </div>
    </div>
</body>
</html>
            """
            
            # بناء قائمة الخدمات
            services_html = ""
            for service in proposal_data.get('services', []):
                services_html += f"""
                <div class="highlight">
                    <p><strong>{service['name']}</strong></p>
                    <p>{service['description']}</p>
                    <p>التكلفة: {service['cost']:.2f} ريال</p>
                </div>
                """
            
            doc_data['services_html'] = services_html
            
            html = html_template.format(
                primary_color=self.brand_colors['primary'],
                **doc_data
            )
            
            if not output_path:
                output_path = f"{self.docs_dir}/proposal_{proposal_data.get('client_name', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"Proposal generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating proposal: {str(e)}")
            raise

    def generate_feasibility_study(
        self,
        study_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """توليد دراسة جدوى اقتصادية احترافية"""
        
        try:
            doc_data = {
                **study_data,
                'company_name': self.company_name,
                'company_ar': self.company_ar_name,
                'brand_colors': self.brand_colors,
                'current_date': datetime.now().strftime('%Y-%m-%d'),
                'direction': 'rtl'
            }
            
            html_template = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; direction: rtl; margin: 0; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .title {{ text-align: center; color: {primary_color}; font-size: 28px; font-weight: bold; margin-bottom: 10px; }}
        .subtitle {{ text-align: center; color: #666; font-size: 14px; margin-bottom: 30px; }}
        .section {{ margin-bottom: 40px; }}
        .section h2 {{ color: {primary_color}; font-size: 20px; border-left: 5px solid {primary_color}; padding-left: 15px; margin-bottom: 15px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th {{ background-color: {primary_color}; color: white; padding: 10px; text-align: right; }}
        td {{ border: 1px solid #ddd; padding: 10px; text-align: right; }}
        .metric {{ display: inline-block; width: 23%; margin: 1%; padding: 15px; background-color: #f9f9f9; border: 1px solid {primary_color}; text-align: center; border-radius: 5px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: {primary_color}; }}
        .metric-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
        .footer {{ border-top: 2px solid {primary_color}; padding-top: 20px; margin-top: 40px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title">{title}</div>
        <div class="subtitle">دراسة جدوى اقتصادية | {current_date}</div>
        
        <div class="section">
            <h2>ملخص تنفيذي</h2>
            <p>{executive_summary}</p>
        </div>
        
        <div class="section">
            <h2>المؤشرات الأساسية</h2>
            <div class="metric">
                <div class="metric-value">{market_size:.0f}</div>
                <div class="metric-label">حجم السوق (مليون ريال)</div>
            </div>
            <div class="metric">
                <div class="metric-value">{expected_revenue:.0f}</div>
                <div class="metric-label">الإيرادات المتوقعة (سنة 1)</div>
            </div>
            <div class="metric">
                <div class="metric-value">{roi_percentage:.0f}%</div>
                <div class="metric-label">العائد على الاستثمار</div>
            </div>
            <div class="metric">
                <div class="metric-value">{payback_months}</div>
                <div class="metric-label">فترة الاسترجاع (شهر)</div>
            </div>
        </div>
        
        <div class="section">
            <h2>تحليل التكاليف</h2>
            <table>
                <thead>
                    <tr>
                        <th>المجموع (ريال)</th>
                        <th>التفاصيل</th>
                        <th>بند التكلفة</th>
                    </tr>
                </thead>
                <tbody>
                    {costs_rows}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>توقعات الإيرادات</h2>
            <table>
                <thead>
                    <tr>
                        <th>الإجمالي السنوي (ريال)</th>
                        <th>السنة</th>
                    </tr>
                </thead>
                <tbody>
                    {revenue_rows}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>المخاطر والتوصيات</h2>
            <p>{risks_recommendations}</p>
        </div>
        
        <div class="footer">
            <p><strong>{company_ar}</strong> | دراسة معتمدة ومختومة رسمياً</p>
            <p>التاريخ: {current_date}</p>
        </div>
    </div>
</body>
</html>
            """
            
            # بناء جداول التكاليف والإيرادات
            costs_rows = ""
            for cost in study_data.get('costs', []):
                costs_rows += f"""
                <tr>
                    <td>{cost['amount']:.2f}</td>
                    <td>{cost['details']}</td>
                    <td>{cost['category']}</td>
                </tr>
                """
            
            revenue_rows = ""
            for revenue in study_data.get('revenue_forecast', []):
                revenue_rows += f"""
                <tr>
                    <td>{revenue['amount']:.2f}</td>
                    <td>السنة {revenue['year']}</td>
                </tr>
                """
            
            doc_data['costs_rows'] = costs_rows
            doc_data['revenue_rows'] = revenue_rows
            
            html = html_template.format(
                primary_color=self.brand_colors['primary'],
                **doc_data
            )
            
            if not output_path:
                output_path = f"{self.docs_dir}/feasibility_{study_data.get('title', 'study')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"Feasibility study generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating feasibility study: {str(e)}")
            raise


# إنشاء instance عام من محرك المستندات
doc_engine = DocumentEngine()
