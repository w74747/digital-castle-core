import os
from datetime import datetime
from io import BytesIO
from jinja2 import Template
from playwright.async_api import async_playwright
from app.security import (
    generate_document_seal_code,
    generate_verification_qr,
)
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
        include_stamp: bool = True,
        include_signature: bool = True,
    ) -> str:
        subtotal = sum(
            item["quantity"] * item["unit_price"] for item in items
        )
        tax = subtotal * BRAND.tax_rate
        total = subtotal + tax
        date_str = datetime.now().strftime("%Y-%m-%d")

        # 1. توليد كود الأمان المشفر
        security_code = generate_document_seal_code(
            invoice_number, total, date_str
        )

        # 2. توليد صورة الـ QR Code
        qr_base64 = generate_verification_qr(
            invoice_number, total, date_str, security_code
        )

        return self.template.render(
            brand=BRAND,
            invoice_number=invoice_number,
            date=date_str,
            client_name=client_name,
            client_contact=client_contact,
            items=items,
            subtotal=subtotal,
            tax=tax,
            total=total,
            include_stamp=include_stamp,
            include_signature=include_signature,
            security_code=security_code,
            qr_code_base64=qr_base64,
        )

    async def generate_invoice_pdf(
        self,
        invoice_number: str,
        client_name: str,
        client_contact: str,
        items: list,
        include_stamp: bool = True,
        include_signature: bool = True,
    ) -> BytesIO:
        html_content = self.render_invoice_html(
            invoice_number,
            client_name,
            client_contact,
            items,
            include_stamp,
            include_signature,
        )

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-gpu",
                ],
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
