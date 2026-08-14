from datetime import datetime
from jinja2 import Template
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
