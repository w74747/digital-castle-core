import os
from datetime import datetime
from io import BytesIO
from jinja2 import Template
from playwright.async_api import async_playwright
from app.security import (
    generate_document_seal_code,
    generate_verification_qr,
    get_secure_stamped_asset,
    get_logo_data_uri,
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
    ) -> str:
        subtotal = sum(
            item["quantity"] * item["unit_price"] for item in items
        )
        tax = subtotal * BRAND.tax_rate
        total = subtotal + tax
        date_str = datetime.now().strftime("%Y-%m-%d")

        # توليد كود الأمان المشفر والـ QR
        security_code = generate_document_seal_code(
            invoice_number, total, date_str
        )
        qr_uri = generate_verification_qr(
            invoice_number, total, date_str, security_code
        )

        # قراءة الشعار
        logo_uri = get_logo_data_uri("assets/logo.png")

        # دمج كود الأمان مباشرة داخل بكسلات الختم والتوقيع في وسطهما
        stamp_uri = get_secure_stamped_asset(
            "assets/stamp.png", security_code, is_signature=False
        )
        signature_uri = get_secure_stamped_asset(
            "assets/signature.png", security_code, is_signature=True
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
            qr_uri=qr_uri,
            logo_uri=logo_uri,
            signature_uri=signature_uri,
            stamp_uri=stamp_uri,
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
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-gpu",
                ],
            )
            page = await browser.new_page()
            await page.set_content(html_content, wait_until="networkidle")
            await page.evaluate("document.fonts.ready")

            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "15px", "bottom": "15px"},
            )
            await browser.close()

        return BytesIO(pdf_bytes)
