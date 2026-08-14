from datetime import datetime
from io import BytesIO
from jinja2 import Template
from xhtml2pdf import pisa
from config.brand_settings import BRAND


class DocumentEngine:

    def __init__(self, template_path: str = "config/invoice_template.html"):
        with open(template_path, "r", encoding="utf-8") as f:
            self.template = Template(f.read())

    def render_invoice_html(
        self,
        invoice_number: str,
        client_name: str,
        client_contact: str,
        items: list,
    ) -> str:
        subtotal = sum(
            item["quantity"] * item["unit_price"] for item in items
        )
        tax = subtotal * BRAND.tax_rate
        total = subtotal + tax

        return self.template.render(
            brand=BRAND,
            invoice_number=invoice_number,
            date=datetime.now().strftime("%Y-%m-%d"),
            client_name=client_name,
            client_contact=client_contact,
            items=items,
            subtotal=subtotal,
            tax=tax,
            total=total,
        )

    def generate_invoice_pdf(
        self,
        invoice_number: str,
        client_name: str,
        client_contact: str,
        items: list,
    ) -> BytesIO:
        html_content = self.render_invoice_html(
            invoice_number, client_name, client_contact, items
        )
        pdf_buffer = BytesIO()
        pisa.CreatePDF(src=html_content, dest=pdf_buffer, encoding="utf-8")
        pdf_buffer.seek(0)
        return pdf_buffer
