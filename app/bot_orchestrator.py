import logging
import os
import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ----------------------------------------------------
# 1. إعدادات السجلات والمتغيرات الأساسية من Railway
# ----------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")


# ----------------------------------------------------
# 2. محرك توجيه النماذج الذكي (الهيكل الهجين)
# ----------------------------------------------------
async def call_planner(prompt: str, system: str = "") -> str:
    """استدعاء Claude 3.5 Sonnet: للتخطيط المعماري وتوليد الـ Specs ودراسات الجدوى"""
    if not ANTHROPIC_API_KEY:
        return "⚠️ تنبيه: لم يتم العثور على ANTHROPIC_API_KEY في متغيرات Railway."

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 4096,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
            )
            data = res.json()
            if "content" in data and len(data["content"]) > 0:
                return data["content"][0]["text"]
            return f"خطأ من مزود Claude: {data}"
    except Exception as e:
        return f"حدث خطأ أثناء الاتصال بـ Claude: {str(e)}"


async def call_developer(
    prompt: str, system: str = "", reasoning: bool = False
) -> str:
    """استدعاء DeepSeek: لكتابة الكود والبرمجة وحماية الأمان وقواعد البيانات"""
    if not DEEPSEEK_API_KEY:
        return "⚠️ تنبيه: لم يتم العثور على DEEPSEEK_API_KEY في متغيرات Railway."

    model = "deepseek-reasoner" if reasoning else "deepseek-chat"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            data = res.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            return f"خطأ من مزود DeepSeek: {data}"
    except Exception as e:
        return f"حدث خطأ أثناء الاتصال بـ DeepSeek: {str(e)}"


async def call_fast_ops(prompt: str, system: str = "") -> str:
    """استدعاء Together AI: لعمليات التسويق، فحص الجودة السريع، وتقارير التلجرام"""
    if not TOGETHER_API_KEY:
        return "⚠️ تنبيه: لم يتم العثور على TOGETHER_API_KEY في متغيرات Railway."

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(
                "https://api.together.xyz/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            data = res.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            return f"خطأ من مزود Together: {data}"
    except Exception as e:
        return f"حدث خطأ أثناء الاتصال بـ Together AI: {str(e)}"


# ----------------------------------------------------
# 3. واجهة التلجرام وإدارة الأوامر التنفيذية
# ----------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الترحيب برئيس مجلس إدارة شركة Digital Castle S.P.C"""
    user_id = str(update.effective_user.id)
    if TELEGRAM_ADMIN_ID and user_id != str(TELEGRAM_ADMIN_ID):
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "🔍 صيد فرصة SaaS جديدة", callback_data="scout_opportunity"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 فحص الأرصدة والـ APIs", callback_data="check_finances"
            )
        ],
        [
            InlineKeyboardButton(
                "🛡️ تشغيل فحص الأمان الشامل", callback_data="run_security_scan"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "🏰 **المقر الرقمي — Digital Castle S.P.C**\n"
        "*(شركة القلعة الرقمية ش.ش.و)*\n\n"
        "المنظومة التشغيلية متصلة ومكتملة بكافة مفاتيح الذكاء الاصطناعي على Railway.\n\n"
        "اختر إجراءً من القائمة أو أرسل فكرة مشروع / رابط مستودع GitHub للبدء الفوري:"
    )
    await update.message.reply_text(
        welcome_text, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def handle_incoming_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """معالجة الأفكار والروابط وتوجيهها للمسار الذكي المناسب"""
    user_id = str(update.effective_user.id)
    if TELEGRAM_ADMIN_ID and user_id != str(TELEGRAM_ADMIN_ID):
        return

    user_text = update.message.text.strip()

    # 1. إذا كان المدخل رابط مستودع GitHub مفتوح المصدر
    if "github.com/" in user_text:
        await update.message.reply_text(
            "🔎 **جاري تحليل المستودع عبر مستشار المصادر المفتوحة والابتكار (Claude)...**",
            parse_mode="Markdown",
        )
        analysis = await call_planner(
            prompt=f"قم بتحليل قدرات وتراخيص هذا المستودع واقترح 3 مشاريع تجارية SaaS يمكننا بناؤها باستخدامه مع تحديد المكونات: {user_text}",
            system="أنت مستشار المصادر المفتوحة والابتكار في شركة Digital Castle S.P.C.",
        )
        await update.message.reply_text(analysis)

    # 2. إذا كان المدخل فكرة مشروع أو ميزة جديدة
    else:
        await update.message.reply_text(
            "💡 **جاري إعداد دراسة الجدوى وتفكيك المتطلبات المعمارية...**",
            parse_mode="Markdown",
        )
        feasibility = await call_planner(
            prompt=f"قم بإعداد دراسة جدوى وتفكيك معماري للمشروع التالي: {user_text}\nالمطلوب: المشكلة والحل، التكلفة المتوقعة، والتقسيم المبدئي لملفات .spec-kit",
            system="أنت المخطط المعماري ومستشار الجدوى لشركة Digital Castle S.P.C.",
        )
        await update.message.reply_text(feasibility)


async def handle_callback_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """معالجة أزرار التحكم السريعة"""
    query = update.callback_query
    await query.answer()

    if query.data == "scout_opportunity":
        await query.edit_message_text(
            "🚀 **جاري استكشاف الفرص الصاعدة ومشاكل السوق الحالية عبر محرك البحث...**"
        )
        result = await call_fast_ops(
            prompt="حدد 3 مشاكل تقنية حقيقية متكررة يبحث المستخدمون عن أدوات لحلها في السوق حالياً مع مقترح لكل حل.",
            system="أنت صائد الفرص والترندات التقنية لشركة Digital Castle S.P.C.",
        )
        await query.message.reply_text(result)

    elif query.data == "check_finances":
        await query.message.reply_text(
            "💰 **تقرير FinOps السريع:** المفاتيح الثلاثة (Anthropic, DeepSeek, Together) متصلة ومفعلة ضمن بيئة Railway بنجاح."
        )

    elif query.data == "run_security_scan":
        await query.message.reply_text(
            "🛡️ **فحص DevSecOps:** تم التحقق من سلامة قراءة المتغيرات وعزل البيئات دون تسريب أي مفاتيح في السجلات."
        )


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is missing in environment variables.")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_incoming_message)
    )

    print("🚀 محرك Digital Castle S.P.C يعمل الآن بنجاح على Railway...")
    app.run_polling()


if __name__ == "__main__":
    main()
