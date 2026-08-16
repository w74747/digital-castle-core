"""
Agent Router - موزع المهام الذكي
يوزع المهام بين Claude و DeepSeek و Together AI بناءً على نوع المهمة
"""

import logging
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

import httpx
from anthropic import Anthropic

from config import settings

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """أنواع الوكلاء المتاحة"""
    CLAUDE = "claude"  # التخطيط والجدوى
    DEEPSEEK = "deepseek"  # البرمجة والأمان
    TOGETHER = "together"  # المهام الخفيفة والمحتوى


class TaskType(str, Enum):
    """أنواع المهام"""
    FEASIBILITY = "feasibility"  # دراسة الجدوى → Claude
    ARCHITECTURE = "architecture"  # التصميم المعماري → Claude
    CODING = "coding"  # البرمجة → DeepSeek
    SECURITY = "security"  # الأمان → DeepSeek
    QA = "qa"  # اختبار الجودة → Together
    CONTENT = "content"  # كتابة المحتوى → Together
    SEO = "seo"  # فحص SEO → Together
    FINOPS = "finops"  # التقارير المالية → Together


@dataclass
class AgentResponse:
    """نموذج الاستجابة من الوكيل"""
    agent_type: AgentType
    task_type: TaskType
    content: str
    tokens_used: int
    timestamp: str
    model_used: str


class AgentRouter:
    """موزع المهام بين الوكلاء المختلفة"""
    
    def __init__(self):
        """تهيئة الاتصالات بـ APIs المختلفة"""
        logger.info("🤖 Initializing Agent Router...")
        
        # Claude (Anthropic)
        self.claude_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        # DeepSeek و Together - يستخدمان OpenAI-compatible API
        self.http_client = httpx.AsyncClient(timeout=60.0)
        
        logger.info("✅ Agent Router initialized successfully")
    
    async def route_task(
        self,
        task_type: TaskType,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1000
    ) -> AgentResponse:
        """
        توجيه المهمة إلى الوكيل المناسب
        
        Args:
            task_type: نوع المهمة
            prompt: نص المهمة
            context: سياق إضافي
            max_tokens: الحد الأقصى للـ tokens
        
        Returns:
            استجابة الوكيل
        """
        
        # تحديد نوع الوكيل بناءً على نوع المهمة
        if task_type in [TaskType.FEASIBILITY, TaskType.ARCHITECTURE]:
            return await self._call_claude(
                prompt, context, max_tokens, task_type
            )
        
        elif task_type in [TaskType.CODING, TaskType.SECURITY]:
            return await self._call_deepseek(
                prompt, context, max_tokens, task_type
            )
        
        elif task_type in [TaskType.QA, TaskType.CONTENT, TaskType.SEO, TaskType.FINOPS]:
            return await self._call_together(
                prompt, context, max_tokens, task_type
            )
        
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _call_claude(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]],
        max_tokens: int,
        task_type: TaskType
    ) -> AgentResponse:
        """استدعاء Claude (Anthropic)"""
        try:
            logger.info(f"📌 Routing to Claude for {task_type.value} task")
            
            # إضافة السياق إلى الـ prompt
            full_prompt = prompt
            if context:
                full_prompt = f"{prompt}\n\nContext: {context}"
            
            # استدعاء Claude
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            )
            
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            return AgentResponse(
                agent_type=AgentType.CLAUDE,
                task_type=task_type,
                content=content,
                tokens_used=tokens_used,
                timestamp=datetime.now().isoformat(),
                model_used="claude-3-5-sonnet-20241022"
            )
        
        except Exception as e:
            logger.error(f"❌ Claude error: {e}")
            raise
    
    async def _call_deepseek(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]],
        max_tokens: int,
        task_type: TaskType
    ) -> AgentResponse:
        """استدعاء DeepSeek عبر OpenAI-compatible API"""
        try:
            logger.info(f"📌 Routing to DeepSeek for {task_type.value} task")
            
            full_prompt = prompt
            if context:
                full_prompt = f"{prompt}\n\nContext: {context}"
            
            # استدعاء DeepSeek
            async with self.http_client as client:
                response = await client.post(
                    f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
                    json={
                        "model": "deepseek-coder",
                        "messages": [
                            {"role": "user", "content": full_prompt}
                        ],
                        "max_tokens": max_tokens,
                        "temperature": 0.7
                    },
                    headers={
                        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    }
                )
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            tokens_used = result.get("usage", {}).get("total_tokens", 0)
            
            return AgentResponse(
                agent_type=AgentType.DEEPSEEK,
                task_type=task_type,
                content=content,
                tokens_used=tokens_used,
                timestamp=datetime.now().isoformat(),
                model_used="deepseek-coder"
            )
        
        except Exception as e:
            logger.error(f"❌ DeepSeek error: {e}")
            raise
    
    async def _call_together(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]],
        max_tokens: int,
        task_type: TaskType
    ) -> AgentResponse:
        """استدعاء Together AI"""
        try:
            logger.info(f"📌 Routing to Together AI for {task_type.value} task")
            
            full_prompt = prompt
            if context:
                full_prompt = f"{prompt}\n\nContext: {context}"
            
            # استدعاء Together
            async with self.http_client as client:
                response = await client.post(
                    f"{settings.TOGETHER_BASE_URL}/chat/completions",
                    json={
                        "model": "meta-llama/Llama-3-8b-chat-hf",
                        "messages": [
                            {"role": "user", "content": full_prompt}
                        ],
                        "max_tokens": max_tokens,
                        "temperature": 0.7
                    },
                    headers={
                        "Authorization": f"Bearer {settings.TOGETHER_API_KEY}",
                        "Content-Type": "application/json"
                    }
                )
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            tokens_used = result.get("usage", {}).get("total_tokens", 0)
            
            return AgentResponse(
                agent_type=AgentType.TOGETHER,
                task_type=task_type,
                content=content,
                tokens_used=tokens_used,
                timestamp=datetime.now().isoformat(),
                model_used="meta-llama/Llama-3-8b-chat-hf"
            )
        
        except Exception as e:
            logger.error(f"❌ Together AI error: {e}")
            raise
    
    async def get_router_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات الموجه"""
        return {
            "status": "active",
            "agents": {
                "claude": "ready",
                "deepseek": "ready",
                "together": "ready"
            },
            "models": {
                "claude": "claude-3-5-sonnet-20241022",
                "deepseek": "deepseek-coder",
                "together": "meta-llama/Llama-3-8b-chat-hf"
            }
        }


# إنشاء نسخة واحدة من الموجه
_router_instance = None

async def get_agent_router() -> AgentRouter:
    """الحصول على نسخة فريدة من موجه الوكلاء"""
    global _router_instance
    if _router_instance is None:
        _router_instance = AgentRouter()
    return _router_instance
