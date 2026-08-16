import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import json
from datetime import datetime
from typing import Optional, Dict, Any

from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_ID, PORT, WEBHOOK_URL,
    ANTHROPIC_API_KEY, DEEPSEEK_API_KEY, TOGETHER_API_KEY
)
from agent_router import HybridAgentRouter, router
from document_engine import DocumentEngine, doc_engine

# ================ LOGGING ================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/digital_castle.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================ TELEGRAM UTILITIES ================
async def send_telegram_message(chat_id: int, text: str, parse_mode: str = "HTML"):
    """إرسال رسالة عبر Telegram Bot"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.error(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        logger.error(f"Telegram send error: {str(e)}")

async def send_admin_notification(message: str):
    """إرسال تنبيه للأدمن"""
    await send_telegram_message(TELEGRAM_ADMIN_ID, message)

# ================ AGENTS ORCHESTRATOR ================
class AgentOrchestrator:
    """منسق الوكلاء - يدير تفاعل الوكلاء المختلفين"""
    
    def __init__(self, router: HybridAgentRouter):
        self.router = router
        self.doc_engine = doc_engine
        
    async def handle_feasibility_request(
        self,
        market_problem: str,
        target_audience: str,
        chat_id: int
    ) -> Dict[str, Any]:
        """معالج طلب دراسة الجدوى"""
        
        # الخطوة 1: صائد الفرص - اكتشاف الفرصة
        await send_telegram_message(chat_id, "🔍 جاري البحث عن الفرصة والسوق...")
        
        market_scout_prompt = f"""
        كمستكشف أسواق (Market Scout)، حلل الفرصة التالية:
        
        المشكلة: {market_problem}
        الجمهور المستهدف: {target_audience}
        
        قدم تحليلاً للترندات الحالية والفرص المتاحة والمنافسين الرئيسيين.
        """
        
        scout_result = await self.router.route_task(
            'planning',
            market_scout_prompt,
            admin_callback=send_admin_notification
        )
        
        if not scout_result['success']:
            return {'success': False, 'error': scout_result['error']}
        
        await send_telegram_message(chat_id, f"✅ تحليل السوق:\n\n{scout_result['response'][:500]}...")
        
        # الخطوة 2: استشاري الجدوى - تحليل التفاصيل
        await send_telegram_message(chat_id, "📊 جاري تحليل الجدوى الاقتصادية...")
        
        feasibility_prompt = f"""
        كمستشار جدوى (Feasibility Consultant)، حلل:
        
        الفرصة السابقة من المستكشف:
        {scout_result['response']}
        
        قدم:
        1. حجم السوق المقدر
        2. تكاليف التشغيل والتطوير
        3. الإيرادات المتوقعة
        4. هامش الربح المقدر
        5. فترة الاسترجاع
        6. مؤشرات الخطر
        
        قدم أرقاماً واقعية وقابلة للتحقق.
        """
        
        feasibility_result = await self.router.route_task(
            'planning',
            feasibility_prompt,
            admin_callback=send_admin_notification
        )
        
        if not feasibility_result['success']:
            return {'success': False, 'error': feasibility_result['error']}
        
        await send_telegram_message(chat_id, f"📈 الجدوى الاقتصادية:\n\n{feasibility_result['response'][:500]}...")
        
        return {
            'success': True,
            'market_analysis': scout_result['response'],
            'feasibility_analysis': feasibility_result['response'],
            'tokens_used': {
                'anthropic': scout_result.get('tokens_used', 0) + feasibility_result.get('tokens_used', 0)
            }
        }
    
    async def handle_specification_request(
        self,
        project_name: str,
        requirements: str,
        chat_id: int
    ) -> Dict[str, Any]:
        """معالج طلب صياغة المواصفات الفنية"""
        
        await send_telegram_message(chat_id, "🏗️ جاري صياغة المواصفات الفنية...")
        
        spec_prompt = f"""
        كمهندس معماري (System Architect)، صغ المواصفات الفنية للمشروع:
        
        اسم المشروع: {project_name}
        المتطلبات: {requirements}
        
        أنتج:
        1. ملف spec.md يتضمن:
           - نظرة عامة
           - متطلبات النظام
           - معمارية النظام
           - واجهات API
           - قواعد البيانات
           - أمان وحماية
        
        2. جدول مهام مفصل (tasks.md) يتضمن:
           - كل مهمة بصيغة منفصلة
           - المتطلبات المسبقة
           - معايير القبول
           - الموارد المطلوبة
        
        اتبع منهجية Spec-Driven Development بدقة تامة.
        """
        
        spec_result = await self.router.route_task(
            'planning',
            spec_prompt,
            admin_callback=send_admin_notification
        )
        
        if not spec_result['success']:
            return {'success': False, 'error': spec_result['error']}
        
        await send_telegram_message(chat_id, f"✅ تم صياغة المواصفات:\n\n{spec_result['response'][:300]}...")
        
        return {
            'success': True,
            'specifications': spec_result['response'],
            'tokens_used': {'anthropic': spec_result.get('tokens_used', 0)}
        }
    
    async def handle_code_task(
        self,
        specification: str,
        task_details: str,
        chat_id: int
    ) -> Dict[str, Any]:
        """معالج طلب كتابة الكود"""
        
        await send_telegram_message(chat_id, "💻 جاري كتابة الكود...")
        
        code_prompt = f"""
        كمبرمج رئيسي (Core Developer)، اكتب الكود بناءً على:
        
        المواصفات:
        {specification}
        
        تفاصيل المهمة:
        {task_details}
        
        متطلبات:
        - اتبع أفضل الممارسات البرمجية (PEP 8, Clean Code)
        - أضف تعليقات واضحة
        - أضف معالجة الأخطاء
        - أضف وحدات اختبار (Unit Tests)
        - تأكد من الأمان
        
        قدم الكود جاهزاً للنشر على Railway.
        """
        
        code_result = await self.router.route_task(
            'development',
            code_prompt,
            admin_callback=send_admin_notification
        )
        
        if not code_result['success']:
            return {'success': False, 'error': code_result['error']}
        
        await send_telegram_message(chat_id, f"✅ تم كتابة الكود:\n\n{code_result['response'][:300]}...")
        
        return {
            'success': True,
            'code': code_result['response'],
            'tokens_used': {'deepseek': code_result.get('tokens_used', 0)}
        }
    
    async def handle_qa_task(
        self,
        code: str,
        requirements: str,
        chat_id: int
    ) -> Dict[str, Any]:
        """معالج طلب فحص الجودة والاختبارات"""
        
        await send_telegram_message(chat_id, "🧪 جاري فحص الجودة والأداء...")
        
        qa_prompt = f"""
        كفريق جودة واختبارات (QA & Fixes Agent)، افحص:
        
        الكود:
        {code}
        
        المتطلبات:
        {requirements}
        
        قيّم:
        - كفاية الاختبارات
        - الأداء والسرعة
        - الأمان
        - الأخطاء المحتملة
        - الثغرات
        
        قدم قائمة بالإصلاحات المطلوبة بالأولوية.
        """
        
        qa_result = await self.router.route_task(
            'fast_tasks',
            qa_prompt,
            admin_callback=send_admin_notification
        )
        
        return qa_result

# ================ LIFESPAN ================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """إدارة دورة حياة التطبيق"""
    
    # STARTUP
    logger.info("🚀 Digital Castle S.P.C - Starting Up")
    
    # التحقق من المفاتيح API
    if not ANTHROPIC_API_KEY:
        logger.warning("⚠️ ANTHROPIC_API_KEY not set")
    if not DEEPSEEK_API_KEY:
        logger.warning("⚠️ DEEPSEEK_API_KEY not set")
    if not TOGETHER_API_KEY:
        logger.warning("⚠️ TOGETHER_API_KEY not set")
    
    # إنشاء منسق الوكلاء
    app.state.orchestrator = AgentOrchestrator(router)
    
    logger.info("✅ All Systems Ready")
    logger.info(f"Token Usage Summary: {router.get_token_summary()}")
    
    # إرسال إشعار بدء التشغيل
    try:
        await send_admin_notification("🟢 <b>Digital Castle S.P.C</b> - تم بدء التشغيل بنجاح ✅")
    except:
        pass
    
    yield
    
    # SHUTDOWN
    logger.info("🛑 Digital Castle S.P.C - Shutting Down")
    await send_admin_notification("🔴 <b>Digital Castle S.P.C</b> - تم إيقاف الخدمة")

# ================ FASTAPI APP ================
app = FastAPI(
    title="Digital Castle S.P.C",
    description="شركة القلعة الرقمية - نظام حاضنة مشاريع ذاتية التشغيل",
    version="1.0.0",
    lifespan=lifespan
)

# ================ ROUTES ================

@app.get("/")
async def root():
    """صحة التطبيق"""
    return {
        "status": "online",
        "company": "Digital Castle S.P.C",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """نقطة استقبال أحداث Telegram"""
    
    try:
        data = await request.json()
        
        if 'message' not in data:
            return JSONResponse({'ok': True})
        
        message = data['message']
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        text = message.get('text', '')
        
        # التحقق من تفويض المستخدم
        if user_id != TELEGRAM_ADMIN_ID:
            await send_telegram_message(chat_id, "❌ غير مفوض للوصول إلى هذا النظام")
            return JSONResponse({'ok': True})
        
        logger.info(f"Message from {user_id}: {text[:50]}")
        
        # معالجة الأوامر
        if text.startswith('/start'):
            await send_telegram_message(
                chat_id,
                """🏰 <b>أهلاً في Digital Castle S.P.C</b>
                
الأوامر المتاحة:
/status - حالة النظام
/tokens - ملخص استهلاك التوكنز
/feasibility - دراسة جدوى جديدة
/spec - صياغة مواصفات تقنية
/code - كتابة كود
/qa - فحص جودة
/help - المساعدة الكاملة
                """,
                "HTML"
            )
        
        elif text.startswith('/status'):
            token_summary = router.get_token_summary()
            status_msg = "📊 <b>حالة النظام</b>\n\n"
            for provider, stats in token_summary.items():
                status_msg += f"<b>{provider.upper()}</b>\n"
                status_msg += f"  المستخدم: {stats['used']:,}\n"
                status_msg += f"  المتبقي: {stats['remaining']:,}\n"
                status_msg += f"  النسبة: {stats['percentage']:.1f}%\n\n"
            await send_telegram_message(chat_id, status_msg, "HTML")
        
        elif text.startswith('/tokens'):
            token_summary = router.get_token_summary()
            await send_telegram_message(
                chat_id,
                f"<pre>{json.dumps(token_summary, indent=2, ensure_ascii=False)}</pre>",
                "HTML"
            )
        
        elif text.startswith('/feasibility'):
            await send_telegram_message(
                chat_id,
                "📝 أرسل: /start_feasibility [المشكلة] | [الجمهور]\n\nمثال:\n/start_feasibility تطبيق توصيل طعام | سكان المدينة"
            )
        
        elif text.startswith('/spec'):
            await send_telegram_message(
                chat_id,
                "📝 أرسل: /start_spec [اسم المشروع] | [المتطلبات]\n\nمثال:\n/start_spec متجر إلكتروني | نظام دفع وإدارة مخزون"
            )
        
        elif text.startswith('/help'):
            await send_telegram_message(
                chat_id,
                """🆘 <b>المساعدة الكاملة</b>

<b>قطاع الجدوى والمشاريع:</b>
• صائد الفرص (Market Scout) - اكتشاف الفرص
• مستشار الجدوى (Feasibility) - تحليل اقتصادي

<b>قطاع الهندسة والتطوير:</b>
• مهندس معماري (Architect) - صياغة المواصفات
• مبرمج رئيسي (Developer) - كتابة الكود
• فريق جودة (QA) - الاختبارات

<b>قطاع التسويق:</b>
• مدير تسويق (CMO) - خطط الإطلاق
• كاتب محتوى (Copywriter) - محتوى تسويقي

<b>قطاع المالية:</b>
• مدير مالي (CFO) - التقارير المالية

اكتب /status لعرض حالة النظام
                """,
                "HTML"
            )
        
        else:
            # معالجة الرسائل العادية كاستفسارات عامة
            analysis_result = await app.state.orchestrator.router.route_task(
                'planning',
                f"الاستفسار: {text}\n\nقدم إجابة مختصرة وإجرائية.",
                admin_callback=send_admin_notification
            )
            
            if analysis_result['success']:
                response_text = analysis_result['response'][:1000]
                await send_telegram_message(chat_id, response_text)
            else:
                await send_telegram_message(chat_id, f"❌ حدث خطأ: {analysis_result['error']}")
        
        return JSONResponse({'ok': True})
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JSONResponse({'ok': False, 'error': str(e)})

@app.post("/api/feasibility")
async def create_feasibility(request: Request):
    """API endpoint لإنشاء دراسة جدوى"""
    
    try:
        payload = await request.json()
        
        result = await app.state.orchestrator.handle_feasibility_request(
            market_problem=payload.get('market_problem'),
            target_audience=payload.get('target_audience'),
            chat_id=TELEGRAM_ADMIN_ID
        )
        
        return JSONResponse(result)
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return JSONResponse({'success': False, 'error': str(e)})

@app.post("/api/specification")
async def create_specification(request: Request):
    """API endpoint لإنشاء مواصفات تقنية"""
    
    try:
        payload = await request.json()
        
        result = await app.state.orchestrator.handle_specification_request(
            project_name=payload.get('project_name'),
            requirements=payload.get('requirements'),
            chat_id=TELEGRAM_ADMIN_ID
        )
        
        return JSONResponse(result)
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return JSONResponse({'success': False, 'error': str(e)})

@app.get("/api/tokens")
async def get_token_summary():
    """الحصول على ملخص استهلاك التوكنز"""
    return router.get_token_summary()

# ================ MAIN ================
if __name__ == "__main__":
    import uvicorn
    
    os.makedirs('logs', exist_ok=True)
    
    logger.info(f"Starting Digital Castle S.P.C on port {PORT}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
