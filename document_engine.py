import json
from jinja2 import Template

def load_brand():
    with open("brand_guidelines.json", "r", encoding="utf-8") as f:
        return json.load(f)

def generate_invoice_html(client_name: str, invoice_id: str, items: list, total_amount: float) -> str:
    brand = load_brand()
    template_str = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: {{ brand.typography.ar_font }}; background: {{ brand.brand_colors.background }}; color: {{ brand.brand_colors.primary }}; padding: 30px; }
            .header { border-bottom: 3px solid {{ brand.brand_colors.secondary }}; padding-bottom: 10px; margin-bottom: 20px; }
            .title { font-size: 24px; font-weight: bold; color: {{ brand.brand_colors.secondary }}; }
            .meta { font-size: 14px; color: #64748B; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #CBD5E1; padding: 10px; text-align: right; }
            th { background: {{ brand.brand_colors.primary }}; color: #FFFFFF; }
            .total { font-size: 18px; font-weight: bold; margin-top: 20px; text-align: left; }
            .footer { margin-top: 40px; font-size: 12px; text-align: center; color: #94A3B8; border-top: 1px solid #E2E8F0; padding-top: 10px; }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">{{ brand.company_legal_name_ar }}</div>
            <div class="meta">{{ brand.company_legal_name_en }} | {{ brand.entity_type }}</div>
            <div class="meta">رقم الفاتورة: #{{ invoice_id }}</div>
        </div>
        <p><strong>فاتورة إلى:</strong> {{ client_name }}</p>
        <table>
            <thead>
                <tr>
                    <th>البند / الخدمة</th>
                    <th>السعر</th>
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                <tr>
                    <td>{{ item.description }}</td>
                    <td>${{ item.price }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <div class="total">الإجمالي المستحق: ${{ total_amount }}</div>
        <div class="footer">
            تم إصدار هذه الوثيقة رسمياً من قبل {{ brand.company_legal_name_ar }} — جميع الحقوق محفوظة.
        </div>
    </body>
    </html>
    """
    template = Template(template_str)
    return template.render(brand=brand, client_name=client_name, invoice_id=invoice_id, items=items, total_amount=total_amount)
