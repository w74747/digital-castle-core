import os
from datetime import datetime
from io import BytesIO
from jinja2 import Template
from playwright.sync_api import sync_playwright
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

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = browser.new_page()
            # حقن الـ HTML في المتصفح الافتراضي
            page.set_content(html_content, wait_until="networkidle")

            # تصدير كـ PDF بمقاس A4 وتنسيق كامل
            pdf_bytes = page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "20px", "bottom": "20px"},
            )
            browser.close()

        return BytesIO(pdf_bytes)
