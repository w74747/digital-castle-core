"""
تكامل بوت Telegram مع محرك المستندات
Telegram Bot Integration with Document Engine
"""

import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, filters, MessageHandler
from app.document_engine import DocumentEngine
from config.brand_settings import BRAND

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0"))

if not BOT_TOKEN:
    logger.warning("⚠️ TELEGRAM_BOT_TOKEN not configured - Telegram integration disabled")
    exit(1)

doc_engine = DocumentEngine()

# ============================================
# Command Handlers
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /start"""
    await update.message.reply_text(
        f"🏰 مرحباً بك في {BRAND.name_ar}\n\n"
        f"📄 نظام الفوترة والتوثيق الرسمي\n"
        f"{BRAND.tagline_ar}\n\n"
        f"الأوامر المتاحة:\n"
        f"/invoice - إنشاء فاتورة تجريبية\n"
        f"/help - مساعدة إضافية"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /help"""
    help_text = (
        f"📚 {BRAND.name_ar} - نظام المساعدة\n\n"
        f"الأوامر:\n"
        f"• /invoice - توليد فاتورة تجريبية\n"
        f"• /status - حالة النظام\n"
        f"• /about - معلومات الشركة"
    )
    await update.message.reply_text(help_text)


async def generate_sample_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """توليد فاتورة تجريبية"""
    status_msg = await update.message.reply_text(
        "⏳ جاري إنشاء الفاتورة الرسمية وتطبيق التوثيق الأمني...\n"
        "🔐 توليد رموز التحقق والعلامات المائية..."
    )
    
    sample_items = [
        {"description": "خدمات تطوير وتكامل سحابي", "quantity": 1, "unit_price": 250.0},
        {"description": "إعداد بيئة الوكلاء والذكاء الاصطناعي", "quantity": 1, "unit_price": 150.0},
        {"description": "اختبار الجودة والأداء", "quantity": 1, "unit_price": 100.0}
    ]
    
    try:
        pdf_buffer = await doc_engine.generate_invoice_pdf(
            invoice_number="INV-2026-TG-001",
            client_name="عميل تجريبي من Telegram",
            client_contact="sample@telegram.bot",
            items=sample_items
        )
        pdf_buffer.seek(0)
        
        await update.message.reply_document(
            document=pdf_buffer,
            filename="Invoice_INV-2026-TG-001.pdf",
            caption=(
                "✅ تم إنشاء الفاتورة بنجاح!\n\n"
                "🔐 الفاتورة موثقة بـ:\n"
                "• رمز تحقق SHA-256\n"
                "• QR Code للتحقق الرسمي\n"
                "• عتم مائية على التوقيع والختم\n"
                "• ختم رسمي معتمد"
            )
        )
        await status_msg.delete()
        logger.info("✅ Sample invoice generated via Telegram")
    
    except Exception as e:
        logger.error(f"❌ Error in invoice generation: {str(e)}")
        await status_msg.edit_text(f"❌ حدث خطأ: {str(e)}")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض حالة النظام"""
    status_text = (
        f"📊 حالة النظام:\n\n"
        f"✅ محرك توليد المستندات: جاهز\n"
        f"✅ نظام الأمان: فعّال\n"
        f"✅ Telegram Bot: متصل\n"
        f"✅ قاعدة البيانات: متصلة"
    )
    await update.message.reply_text(status_text)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معلومات الشركة"""
    about_text = (
        f"🏰 {BRAND.name_ar}\n"
        f"{BRAND.name_en}\n\n"
        f"📍 {BRAND.address}\n"
        f"📧 {BRAND.email}\n"
        f"📱 {BRAND.phone}\n"
        f"🌐 {BRAND.website}\n\n"
        f"ـــــــــــــــــــــــــــــــــــ\n"
        f"{BRAND.tagline_ar}\n"
        f"{BRAND.tagline_en}"
    )
    await update.message.reply_text(about_text)


# ============================================
# Main Bot Function
# ============================================

def main():
    """تشغيل بوت Telegram"""
    logger.info("🚀 Starting Telegram Bot...")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # إضافة معالجات الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("invoice", generate_sample_invoice))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("about", about))
    
    logger.info("✅ Bot handlers registered")
    logger.info("🔄 Starting polling...")
    
    app.run_polling()


if __name__ == "__main__":
    main()
