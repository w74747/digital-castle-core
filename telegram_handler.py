"""
Telegram Handler - معالج تفاعلات Telegram
يدير الاتصال مع المستخدمين عبر Telegram
"""

import logging
from typing import Optional

from telegram import Update, BotCommand, MenuButtonCommands
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

from config import settings
from agent_router import get_agent_router, TaskType

logger = logging.getLogger(__name__)


class TelegramHandler:
    """معالج تفاعلات Telegram"""
    
    def __init__(self):
        """تهيئة معالج Telegram"""
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.admin_id = int(settings.TELEGRAM_ADMIN_ID)
        self.application: Optional[Application] = None
    
    async def initialize(self):
        """تهيئة التطبيق والقائمة"""
        logger.info("🤖 Initializing Telegram Bot...")
        
        self.application = Application.builder().token(self.bot_token).build()
        
        # إضافة المعالجات
        self.application.add_handler(
            CommandHandler("start", self.cmd_start)
        )
        self.application.add_handler(
            CommandHandler("help", self.cmd_help)
        )
        self.application.add_handler(
            CommandHandler("status", self.cmd_status)
        )
        self.application.add_handler(
            CommandHandler("invoice", self.cmd_invoice)
        )
        self.application.add_handler(
            CommandHandler("feasibility", self.cmd_feasibility)
        )
        self.application.add_handler(
            CommandHandler("admin", self.cmd_admin)
        )
        
        # معالج الرسائل النصية العامة
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        # إعدادات قائمة الأوامر
        commands = [
            BotCommand("start", "🚀 Start the bot"),
            BotCommand("help", "❓ Get help"),
            BotCommand("status", "📊 System status"),
            BotCommand("invoice", "📄 Generate invoice"),
            BotCommand("feasibility", "🔍 Feasibility study"),
            BotCommand("admin", "🔐 Admin panel")
        ]
        
        await self.application.bot.set_my_commands(commands)
        await self.application.bot.set_my_default_administrator_rights()
        
        logger.info("✅ Telegram Bot initialized successfully")
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /start"""
        user = update.effective_user
        logger.info(f"👤 User {user.id} started the bot")
        
        message = f"""
╔════════════════════════════════════════╗
║  🏰 Digital Castle S.P.C              ║
║  شركة القلعة الرقمية ش.ش.و            ║
╚════════════════════════════════════════╝

مرحباً بك {user.first_name}! 👋

أنا بوت Digital Castle الذكي، يمكنني مساعدتك في:

📄 توليد الفواتير الرسمية
🔍 دراسات الجدوى والتحليل
🏗️ التصميم المعماري
📊 التقارير المالية
⚡ وأكثر...

اكتب /help لمشاهدة قائمة الأوامر كاملة
        """
        
        await update.message.reply_text(message)
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /help"""
        help_message = """
📋 قائمة الأوامر المتاحة:

🚀 /start - بدء البوت
❓ /help - عرض هذه المساعدة
📊 /status - حالة النظام الحالية
📄 /invoice - توليد فاتورة جديدة
🔍 /feasibility - طلب دراسة جدوى
🔐 /admin - لوحة التحكم (للمسؤولين فقط)

💡 كيفية الاستخدام:
- اكتب الأمر مباشرة (مثل: /invoice)
- أو أرسل سؤال، وسيساعدك البوت

🎯 أمثلة:
- /invoice client:"Acme Corp" amount:1000
- /feasibility "فكرة تطبيق جديد"
        """
        
        await update.message.reply_text(help_message)
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /status"""
        router = await get_agent_router()
        stats = await router.get_router_stats()
        
        status_message = f"""
📊 حالة النظام الحالية:

🟢 Status: {stats['status']}
🏢 Company: Digital Castle S.P.C
🔵 Phase: {settings.PHASE} - {settings.PHASE_NAME}
📈 Version: {settings.APP_VERSION}

🤖 الوكلاء المتاحة:
- Claude: {stats['agents']['claude']}
- DeepSeek: {stats['agents']['deepseek']}
- Together AI: {stats['agents']['together']}

💾 Database: Connected
🌐 API: {settings.SERVER_HOST}:{settings.SERVER_PORT}
        """
        
        await update.message.reply_text(status_message)
    
    async def cmd_invoice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /invoice"""
        message = """
📄 توليد الفاتورة

يرجى توفير التفاصيل التالية:

اسم العميل: 
المبلغ:
نوع الخدمة:

مثال:
/invoice_generate Acme Corp 5000 "SaaS Subscription"
        """
        
        await update.message.reply_text(message)
    
    async def cmd_feasibility(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /feasibility"""
        message = """
🔍 دراسة الجدوى

أخبرني عن فكرتك وسأقوم بـ:
✅ تحليل السوق (TAM/SAM/SOM)
✅ دراسة المنافسين
✅ حساب الاقتصاديات
✅ توصية بالجدوى

أرسل وصفاً لفكرتك...
        """
        
        await update.message.reply_text(message)
    
    async def cmd_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /admin (للمسؤولين فقط)"""
        user_id = update.effective_user.id
        
        if user_id != self.admin_id:
            await update.message.reply_text("❌ ليس لديك صلاحية الوصول إلى لوحة التحكم")
            return
        
        admin_message = """
🔐 لوحة التحكم الإدارية

أوامر إدارية متقدمة:
- /stats - إحصائيات الاستخدام
- /logs - عرض السجلات
- /config - إعدادات النظام
- /agents - حالة الوكلاء
- /reset - إعادة تعيين النظام
        """
        
        await update.message.reply_text(admin_message)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل النصية العامة"""
        user = update.effective_user
        message_text = update.message.text
        
        logger.info(f"📨 Message from {user.id}: {message_text}")
        
        # إرسال رسالة "البوت يكتب..."
        await update.message.chat.send_action("typing")
        
        # معالجة الرسالة بواسطة الوكلاء
        try:
            router = await get_agent_router()
            
            # تحديد نوع المهمة بناءً على المحتوى
            task_type = TaskType.FEASIBILITY
            if any(word in message_text.lower() for word in ["كود", "code", "برنامج"]):
                task_type = TaskType.CODING
            elif any(word in message_text.lower() for word in ["محتوى", "content", "كتابة"]):
                task_type = TaskType.CONTENT
            
            # استدعاء الوكيل المناسب
            response = await router.route_task(
                task_type=task_type,
                prompt=message_text,
                context={"user_id": user.id, "timestamp": str(update.message.date)}
            )
            
            # إرسال الرد
            reply_message = f"""
✅ تم معالجة طلبك

🤖 الوكيل: {response.agent_type.value}
📊 Tokens used: {response.tokens_used}
⏱️ Model: {response.model_used}

📝 الرد:
{response.content}
            """
            
            await update.message.reply_text(reply_message)
        
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
            await update.message.reply_text(
                f"❌ حدث خطأ أثناء معالجة طلبك:\n{str(e)}"
            )
    
    async def start(self):
        """بدء البوت"""
        logger.info("🚀 Starting Telegram Bot polling...")
        
        if self.application is None:
            await self.initialize()
        
        await self.application.run_polling(
            allowed_updates=[Update.ALL_TYPES]
        )
    
    async def stop(self):
        """إيقاف البوت"""
        if self.application:
            await self.application.stop()
            logger.info("🛑 Telegram Bot stopped")


# إنشاء نسخة واحدة من معالج Telegram
_telegram_handler = None

async def get_telegram_handler() -> TelegramHandler:
    """الحصول على نسخة فريدة من معالج Telegram"""
    global _telegram_handler
    if _telegram_handler is None:
        _telegram_handler = TelegramHandler()
    return _telegram_handler
