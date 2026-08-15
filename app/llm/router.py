"""
Smart LLM Router - Tries local first, falls back to API.
Minimizes external calls.
"""

import asyncio
from typing import Literal
from app.llm.providers import (
    anthropic, deepseek, together,
    localai, qwen
)

class SmartLLMRouter:
    """Routes requests to optimal provider."""
    
    async def route(
        self,
        prompt: str,
        task_type: Literal["planning", "coding", "operations"],
        sensitive_data: bool = False
    ) -> str:
        """
        Route to appropriate provider.
        
        Strategy:
        1. If sensitive_data=True: use LOCAL ONLY
        2. If task is simple: use Qwen (cheap, local)
        3. If task is complex: try LocalAI first, then API
        """
        
        # ⭐ RULE 1: NEVER send sensitive data to APIs
        if sensitive_data:
            print("🔒 Sensitive data detected - using LOCAL ONLY")
            return await self._local_only(prompt, task_type)
        
        # ⭐ RULE 2: Try local first (cost + privacy)
        try:
            print("🏠 Trying local LLM...")
            result = await asyncio.wait_for(
                self._try_local(prompt, task_type),
                timeout=10.0
            )
            return result
        except (asyncio.TimeoutError, Exception) as e:
            print(f"⏱️ Local timeout/error: {e}")
        
        # ⭐ RULE 3: Fall back to API only if needed
        print("☁️ Falling back to API providers...")
        return await self._try_apis(prompt, task_type)
    
    async def _local_only(self, prompt: str, task_type: str) -> str:
        """Use ONLY local models."""
        # Try Qwen first (fastest)
        try:
            return await qwen.call(prompt)
        except:
            pass
        
        # Try LocalAI
        try:
            return await localai.call(prompt)
        except Exception as e:
            raise Exception(f"All local models failed: {e}")
    
    async def _try_local(self, prompt: str, task_type: str) -> str:
        """Try local models in parallel."""
        tasks = [
            qwen.call(prompt),
            localai.call(prompt),
        ]
        
        # First to succeed wins
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED
        )
        
        for pending_task in pending:
            pending_task.cancel()
        
        return done.pop().result()
    
    async def _try_apis(self, prompt: str, task_type: str) -> str:
        """Fall back to external APIs."""
        if task_type == "planning":
            return await anthropic.call(prompt)
        elif task_type == "coding":
            return await deepseek.call(prompt)
        else:  # operations
            return await together.call(prompt)

# Singleton
smart_router = SmartLLMRouter()
