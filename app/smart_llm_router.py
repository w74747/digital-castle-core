# app/smart_llm_router.py
"""Smart LLM Router - Local First Strategy"""
import asyncio
import os
from typing import Literal
from app.agent_router import router as api_router
from app.logging_config import get_logger

logger = get_logger(__name__)

class SmartLLMRouter:
    def __init__(self):
        self.localai_url = os.getenv("LOCALAI_URL", "http://localhost:8080")
        self.qwen_url = os.getenv("QWEN_URL", "http://localhost:8001")
    
    async def route(self, prompt: str, task_type: Literal["planning", "coding", "operations"], sensitive_data: bool = False, max_tokens: int = 4096) -> str:
        if sensitive_data:
            return await self._local_only(prompt, task_type, max_tokens)
        
        try:
            result = await asyncio.wait_for(self._try_local(prompt, task_type, max_tokens), timeout=15.0)
            logger.info("✅ Local LLM success")
            return result
        except asyncio.TimeoutError:
            logger.warning("⏱️ Local timeout - API fallback")
        except Exception as e:
            logger.warning(f"⚠️ Local error: {e}")
        
        logger.info("☁️ Using API providers")
        return await self._try_apis(prompt, task_type, max_tokens)
    
    async def _local_only(self, prompt: str, task_type: str, max_tokens: int) -> str:
        try:
            return await self._call_qwen(prompt, max_tokens)
        except:
            return await self._call_localai(prompt, max_tokens)
    
    async def _try_local(self, prompt: str, task_type: str, max_tokens: int) -> str:
        tasks = [self._call_qwen(prompt, max_tokens), self._call_localai(prompt, max_tokens)]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        return list(done)[0].result()
    
    async def _try_apis(self, prompt: str, task_type: str, max_tokens: int) -> str:
        if task_type == "planning":
            return await api_router.call_planner(prompt, max_tokens=max_tokens)
        elif task_type == "coding":
            return await api_router.call_developer(prompt, max_tokens=max_tokens)
        else:
            return await api_router.call_fast_ops(prompt, max_tokens=max_tokens)
    
    async def _call_qwen(self, prompt: str, max_tokens: int) -> str:
        import httpx
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(f"{self.qwen_url}/v1/chat/completions", json={"model": "qwen-3.8", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens})
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def _call_localai(self, prompt: str, max_tokens: int) -> str:
        import httpx
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(f"{self.localai_url}/v1/chat/completions", json={"model": "hermes-2-pro", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens})
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

smart_router = SmartLLMRouter()
