import httpx
import json
import logging
from typing import Optional, Dict, Any
from config import (
    ANTHROPIC_API_KEY, DEEPSEEK_API_KEY, TOGETHER_API_KEY,
    MODELS, TOKEN_LIMITS, TELEGRAM_ADMIN_ID
)

logger = logging.getLogger(__name__)

class HybridAgentRouter:
    """موزع ذكي للمهام بين Claude و DeepSeek و Together AI"""
    
    def __init__(self):
        self.token_usage = {
            'anthropic': 0,
            'deepseek': 0,
            'together': 0
        }
        self.monthly_limits = TOKEN_LIMITS
        
    async def route_task(
        self,
        task_type: str,
        prompt: str,
        context: Optional[Dict] = None,
        admin_callback=None
    ) -> Dict[str, Any]:
        """
        توجيه المهمة للنموذج المناسب
        
        task_type:
        - 'planning': Claude (التخطيط والجدوى والمواصفات)
        - 'development': DeepSeek (الكود والبرمجة والأمان)
        - 'fast_tasks': Together AI (المهام السريعة والمراقبة)
        """
        
        if task_type == 'planning':
            return await self._call_claude(prompt, context, admin_callback)
        elif task_type == 'development':
            return await self._call_deepseek(prompt, context, admin_callback)
        elif task_type == 'fast_tasks':
            return await self._call_together(prompt, context, admin_callback)
        else:
            return {
                'success': False,
                'error': 'نوع المهمة غير معروف',
                'status': 'unknown_task_type'
            }

    async def _call_claude(self, prompt: str, context: Optional[Dict], admin_callback) -> Dict[str, Any]:
        """استدعاء Claude 3.5 Sonnet للتخطيط والجدوى"""
        try:
            model_config = MODELS['planning']
            
            headers = {
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
                'x-api-key': ANTHROPIC_API_KEY
            }
            
            system_prompt = """أنت العقل المعماري والمخطط الرئيسي (System Architect) لشركة Digital Castle S.P.C.
تتخصص في:
- دراسة الجدوى الاقتصادية
- صياغة المواصفات الفنية والمعمارية
- تحليل مستودعات GitHub والأدوات المتاحة
- التخطيط الاستراتيجي للمشاريع
- إرشادات العمل والبروتوكولات

كن دقيقاً وشاملاً واحرص على الالتزام بمعايير Spec-Driven Development."""
            
            payload = {
                'model': model_config['model'],
                'max_tokens': model_config['max_tokens'],
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'system': system_prompt
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    'https://api.anthropic.com/v1/messages',
                    headers=headers,
                    json=payload
                )
            
            result = response.json()
            
            if response.status_code == 200:
                usage = result.get('usage', {})
                tokens_used = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
                self.token_usage['anthropic'] += tokens_used
                
                content = result['content'][0]['text'] if result.get('content') else ''
                
                # تنبيه الأدمن إذا اقتربنا من الحد
                await self._check_token_limit('anthropic', admin_callback)
                
                return {
                    'success': True,
                    'provider': 'anthropic',
                    'model': model_config['model'],
                    'response': content,
                    'tokens_used': tokens_used,
                    'stop_reason': result.get('stop_reason', 'end_turn')
                }
            else:
                error_msg = result.get('error', {}).get('message', 'خطأ غير معروف')
                logger.error(f"Claude API Error: {error_msg}")
                return {
                    'success': False,
                    'provider': 'anthropic',
                    'error': error_msg,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Claude Call Error: {str(e)}")
            return {
                'success': False,
                'provider': 'anthropic',
                'error': str(e)
            }

    async def _call_deepseek(self, prompt: str, context: Optional[Dict], admin_callback) -> Dict[str, Any]:
        """استدعاء DeepSeek للبرمجة والأمان والـ Migrations"""
        try:
            model_config = MODELS['development']
            
            headers = {
                'content-type': 'application/json',
                'authorization': f'Bearer {DEEPSEEK_API_KEY}'
            }
            
            system_prompt = """أنت المبرمج الرئيسي والخبير الأمني (Core Developer & DevSecOps) لشركة Digital Castle S.P.C.
تتخصص في:
- كتابة الكود النظيف والآمن والمحسّن
- إدارة الـ Database Migrations بدون فقدان البيانات
- فحص الثغرات الأمنية وسد ثغرات OWASP
- اتباع معايير Spec-Driven Development بدقة تامة
- العمل داخل فروع Git المستقلة فقط

تحذير: لا تعدل ملفات غير مذكورة في جدول المهام المعتمد. ركز على المهام المحددة فقط."""
            
            payload = {
                'model': model_config['model'],
                'max_tokens': model_config['max_tokens'],
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'system': system_prompt,
                'temperature': 0.3
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    'https://api.deepseek.com/v1/chat/completions',
                    headers=headers,
                    json=payload
                )
            
            result = response.json()
            
            if response.status_code == 200:
                usage = result.get('usage', {})
                tokens_used = usage.get('prompt_tokens', 0) + usage.get('completion_tokens', 0)
                self.token_usage['deepseek'] += tokens_used
                
                content = result['choices'][0]['message']['content'] if result.get('choices') else ''
                
                await self._check_token_limit('deepseek', admin_callback)
                
                return {
                    'success': True,
                    'provider': 'deepseek',
                    'model': model_config['model'],
                    'response': content,
                    'tokens_used': tokens_used,
                    'finish_reason': result['choices'][0].get('finish_reason', 'stop')
                }
            else:
                error_msg = result.get('error', {}).get('message', 'خطأ غير معروف')
                logger.error(f"DeepSeek API Error: {error_msg}")
                return {
                    'success': False,
                    'provider': 'deepseek',
                    'error': error_msg,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"DeepSeek Call Error: {str(e)}")
            return {
                'success': False,
                'provider': 'deepseek',
                'error': str(e)
            }

    async def _call_together(self, prompt: str, context: Optional[Dict], admin_callback) -> Dict[str, Any]:
        """استدعاء Together AI للمهام السريعة والمراقبة والمحتوى"""
        try:
            model_config = MODELS['fast_tasks']
            
            headers = {
                'content-type': 'application/json',
                'authorization': f'Bearer {TOGETHER_API_KEY}'
            }
            
            system_prompt = """أنت فريق المهام السريعة والمراقبة (QA, Monitoring, Content) لشركة Digital Castle S.P.C.
تتخصص في:
- اختبارات الجودة والأداء (QA)
- المراقبة والتنبيهات المبكرة
- كتابة المحتوى التسويقي والمقالات
- تحليل بيانات السوق والترندات
- التقارير المالية والإحصائيات

كن سريعاً وفعالاً واحرص على الدقة في الأرقام والبيانات."""
            
            payload = {
                'model': model_config['model'],
                'max_tokens': model_config['max_tokens'],
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    'https://api.together.xyz/v1/chat/completions',
                    headers=headers,
                    json=payload
                )
            
            result = response.json()
            
            if response.status_code == 200:
                usage = result.get('usage', {})
                tokens_used = usage.get('prompt_tokens', 0) + usage.get('completion_tokens', 0)
                self.token_usage['together'] += tokens_used
                
                content = result['choices'][0]['message']['content'] if result.get('choices') else ''
                
                await self._check_token_limit('together', admin_callback)
                
                return {
                    'success': True,
                    'provider': 'together',
                    'model': model_config['model'],
                    'response': content,
                    'tokens_used': tokens_used,
                    'finish_reason': result['choices'][0].get('finish_reason', 'stop')
                }
            else:
                error_msg = result.get('error', {}).get('message', 'خطأ غير معروف')
                logger.error(f"Together AI Error: {error_msg}")
                return {
                    'success': False,
                    'provider': 'together',
                    'error': error_msg,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Together Call Error: {str(e)}")
            return {
                'success': False,
                'provider': 'together',
                'error': str(e)
            }

    async def _check_token_limit(self, provider: str, admin_callback):
        """التحقق من استهلاك التوكنز وإرسال تنبيهات"""
        current_usage = self.token_usage.get(provider, 0)
        limit = self.monthly_limits.get(f'{provider}_monthly', 0)
        
        if limit > 0:
            usage_percentage = current_usage / limit
            
            if usage_percentage > self.monthly_limits['warning_threshold']:
                warning_msg = f"⚠️ تنبيه استهلاك التوكنز:\n{provider.upper()}\nالاستهلاك: {usage_percentage:.0%} من الحد الشهري"
                if admin_callback:
                    await admin_callback(warning_msg)
                logger.warning(warning_msg)

    def get_token_summary(self) -> Dict[str, Any]:
        """ملخص استهلاك التوكنز"""
        summary = {}
        for provider, usage in self.token_usage.items():
            limit = self.monthly_limits.get(f'{provider}_monthly', 0)
            summary[provider] = {
                'used': usage,
                'limit': limit,
                'remaining': max(0, limit - usage),
                'percentage': (usage / limit * 100) if limit > 0 else 0
            }
        return summary


# إنشاء instance عام من الموزع
router = HybridAgentRouter()
