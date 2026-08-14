import json
from jinja2 import Template

def load_brand():
    with open("brand_guidelines.json", "r", encoding="utf-8") as f:
        return json.load(f)

BASE_CSS = """
:root {
    --dc-ink: #0B1020; --dc-keep: #071033; --dc-steel: #2F4368;
    --dc-blue: #0025FF; --dc-cyan: #08F9F2; --dc-azure: #0A7BF4;
    --dc-canvas: #F6F8FB; --dc-mesa: #EDF1F7; --dc-paper: #FFFFFF;
    --dc-frost: #DCE2EC; --dc-mist: #6B7688;
    --dc-display: 'Spectral', Georgia, serif;
    --dc-text: 'Plus Jakarta Sans', Arial, sans-serif;
    --dc-display-ar: 'Almarai', sans-serif;
    --dc-text-ar: 'IBM Plex Sans Arabic', Tahoma, sans-serif;
    --dc-mono: 'IBM Plex Mono', Consolas, monospace;
}
@page {
    size: A4 portrait;
    margin: 18mm 20mm 20mm 20mm;
}
body {
    font: 400 9.5pt/1.62 var(--dc-text);
    color: var(--dc-ink);
    background: var(--dc-paper);
    margin: 0;
}
body[dir="rtl"] {
    font-family: var(--dc-text-ar);
    line-height: 1.90;
}
.dc-header {
    height: 14mm;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    border-bottom: 0.5pt solid var(--dc-blue);
    padding-bottom: 3mm;
    margin-bottom: 6mm;
}
.dc-eyebrow {
    font: 600 7.5pt/1.2 var(--dc-text);
    letter-spacing: .22em;
    text-transform: uppercase;
    color: var(--dc-mist);
}
[dir="rtl"] .dc-eyebrow {
    font-family: var(--dc-text-ar);
    letter-spacing: 0;
    text-transform: none;
}
h1 {
    font: 400 21pt/1.18 var(--dc-display);
    letter-spacing: -.01em;
    margin: 0 0 4mm;
    color: var(--dc-ink);
}
[dir="rtl"] h1 {
    font-family: var(--dc-display-ar);
    line-height: 1.45;
}
.dc-statutory-block {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 5mm;
    background: var(--dc-canvas);
    border: 0.5pt solid var(--dc-frost);
    padding: 4mm 5mm;
    margin-bottom: 6mm;
    font-size: 8.5pt;
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 8.5pt;
    margin-top: 5mm;
}
th {
    font: 600 7.5pt/1.4 var(--dc-text);
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--dc-mist);
    text-align: right;
    padding: 0 3mm 2mm 0;
    border-bottom: 0.75pt solid var(--dc-ink);
}
td {
    padding: 2.5mm 3mm 2.5mm 0;
    border-bottom: 0.5pt solid var(--dc-frost);
    vertical-align: top;
}
td.num, th.num {
    text-align: left;
    font-family: var(--dc-mono);
    font-variant-numeric: tabular-nums;
}
.dc-total-rule {
    border-top: 1.5pt solid var(--dc-blue);
    font-size: 11pt;
    font-weight: 600;
    padding-top: 3mm;
}
.dc-callout {
    background: var(--dc-mesa);
    border-right: 1.5pt solid var(--dc-blue);
    padding: 5mm 6mm;
    margin: 6mm 0;
}
.dc-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 10mm;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 0.5pt solid var(--dc-frost);
    font: 400 7.5pt/1.4 var(--dc-text);
    color: var(--dc-mist);
}
"""

def generate_invoice_document(client_name: str, invoice_no: str, date: str, items: list, subtotal: float, vat: float, total: float) -> str:
    brand = load_brand()
    html_template = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>{{ brand.documents.invoice.code }} · {{ invoice_no }}</title>
        <style>{{ base_css }}</style>
    </head>
    <body>
        <header class="dc-header">
            <div>
                <div class="dc-eyebrow">{{ brand.entity.legal_name_en }}</div>
                <div style="font-family: var(--dc-display-ar); font-size: 14pt; font-weight: 700; color: var(--dc-ink);">
                    {{ brand.entity.legal_name_ar }}
                </div>
            </div>
            <div style="text-align: left;">
                <div class="dc-eyebrow">OFFICIAL INVOICE · فاتورة معتمدة</div>
                <div style="font-family: var(--dc-mono); font-size: 10pt; color: var(--dc-blue); font-weight: 600;">#{{ invoice_no }}</div>
            </div>
        </header>

        <div class="dc-statutory-block">
            <div>
                <strong>الجهة المفوترة:</strong> {{ brand.entity.legal_name_ar }}<br>
                <strong>السجل التجاري (C.R.):</strong> {{ brand.entity.commercial_registration }}<br>
                <strong>البريد:</strong> {{ brand.entity.email }} | <strong>هاتف:</strong> {{ brand.entity.phone }}
            </div>
            <div>
                <strong>فاتورة إلى العميل:</strong> {{ client_name }}<br>
                <strong>تاريخ الإصدار:</strong> {{ date }}<br>
                <strong>العملة المعتمدة:</strong> {{ brand.documents.invoice.currency }} (ريال عماني)
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th style="width: 60%;">الوصف والخدمة التقنية</th>
                    <th class="num">الكمية</th>
                    <th class="num">السعر الفردي</th>
                    <th class="num">الإجمالي</th>
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                <tr>
                    <td><strong>{{ item.name }}</strong><br><span style="color: var(--dc-mist);">{{ item.description }}</span></td>
                    <td class="num">{{ item.qty }}</td>
                    <td class="num">{{ item.unit_price }}</td>
                    <td class="num">{{ item.total }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <div style="width: 45%; margin-right: auto; margin-top: 6mm;">
            <div style="display: flex; justify-content: space-between; padding: 1.5mm 0;">
                <span>المجموع الفرعي:</span>
                <span class="num" style="font-family: var(--dc-mono);">{{ subtotal }} {{ brand.documents.invoice.currency }}</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 1.5mm 0; border-bottom: 0.5pt solid var(--dc-frost);">
                <span>ضريبة القيمة المضافة (VAT):</span>
                <span class="num" style="font-family: var(--dc-mono);">{{ vat }} {{ brand.documents.invoice.currency }}</span>
            </div>
            <div class="dc-total-rule" style="display: flex; justify-content: space-between;">
                <span>الإجمالي المستحق:</span>
                <span style="font-family: var(--dc-mono); color: var(--dc-blue);">{{ total }} {{ brand.documents.invoice.currency }}</span>
            </div>
        </div>

        <div class="dc-callout">
            <div class="dc-eyebrow" style="color: var(--dc-ink);">تعليمات الدفع والتحويل البنكي</div>
            يرجى تحويل المبلغ لحساب شركة القلعة الرقمية ش.ش.و المعتمد في بنك مسقط، مع إرفاق رقم الفاتورة في خانة المرجع.
        </div>

        <footer class="dc-footer">
            <span>{{ brand.entity.legal_name_en }} · C.R. {{ brand.entity.commercial_registration }} · Muscat, Oman</span>
            <span>{{ brand.entity.website }} · {{ brand.entity.email }}</span>
            <span>وثيقة رسمية معتمدة</span>
        </footer>
    </body>
    </html>
    """
    return Template(html_template).render(
        brand=brand,
        base_css=BASE_CSS,
        client_name=client_name,
        invoice_no=invoice_no,
        date=date,
        items=items,
        subtotal=subtotal,
        vat=vat,
        total=total
    )
