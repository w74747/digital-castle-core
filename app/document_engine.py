import os
from datetime import datetime
from io import BytesIO
from jinja2 import Template
from playwright.async_api import async_playwright
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

    async def generate_invoice_pdf(
        self,
        invoice_number: str,
        client_name: str,
        client_contact: str,
        items: list,
    ) -> BytesIO:
        html_content = self.render_invoice_html(
            invoice_number, client_name, client_contact, items
        )

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"],
            )
            page = await browser.new_page()
            await page.set_content(html_content, wait_until="networkidle")

            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "20px", "bottom": "20px"},
            )
            await browser.close()

        return BytesIO(pdf_bytes)
