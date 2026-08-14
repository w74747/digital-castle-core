import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.agent_router import AgentRouter
from app.document_engine import DocumentEngine
from app.sequence_manager import SequenceManager

# إعداد التسجيل وكتم سجلات التوكن الحساسة
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)

router = AgentRouter()
doc_engine = DocumentEngine()
seq_manager = SequenceManager()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🏰 **مرحباً بك في نظام Digital Castle S.P.C**\n\n"
        "النظام الآلي لإدارة المهام وتوليد الوثائق جاهز للعمل.\n"
        "الأوامر المتاحة:\n"
        "/invoice - إنشاء فاتورة جديدة برقم تسلسلي\n"
        "/ask [سؤال] - استشارة وكلاء الذكاء الاصطناعي"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def invoice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. استخراج الرقم التسلسلي التالي غير المتكرر
    invoice_number = seq_manager.generate_next_number(doc_type="INV")

    sample_items = [
        {"description": "خدمات تطوير وبرمجة سحابية", "quantity": 1, "unit_price": 250.0},
        {"description": "إعداد بيئة الوكلاء والذكاء الاصطناعي", "quantity": 1, "unit_price": 150.0},
    ]

    # 2. توليد ملف PDF
    pdf_file = doc_engine.generate_invoice_pdf(
        invoice_number=invoice_number,
        client_name="شركة عُمان للابتكار",
        client_contact="info@client.om",
        items=sample_items,
    )

    # 3. إرسال الملف باسم الرقم التسلسلي (مثال: INV-2026-0001.pdf)
    filename = f"{invoice_number}.pdf"

    await update.message.reply_document(
        document=pdf_file,
        filename=filename,
        caption=f"📄 **فاتورة رسمية صادرة**\nرقم المستند: `{invoice_number}`",
        parse_mode="Markdown",
    )


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("يرجى كتابة الاستفسار بعد الأمر. مثال:\n`/ask خطة العمل للمشروع`", parse_mode="Markdown")
        return
    await update.message.reply_text("⏳ جاري المعالجة عبر وكيل النظام...")
    response = router.execute_task(prompt)
    await update.message.reply_text(response)


if __name__ == "__main__":
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN غير معرف في المتغيرات البيئية!")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("invoice", invoice_command))
    app.add_handler(CommandHandler("ask", ask_command))

    print("🚀 تم تشغيل نظام Digital Castle بنجاح على السيرفر...")
    app.run_polling()
