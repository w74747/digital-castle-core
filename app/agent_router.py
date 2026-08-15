"""
Agent Router: Hybrid LLM Strategy with Retry, Fallback, and Monitoring
---
Routes tasks to 3 LLM providers based on task type:
- Claude 3.5 Sonnet (Planning, Architecture, Complex Reasoning)
- DeepSeek (Code Generation, Technical Implementation)
- Together AI (Fast Operations, Reports, QA)
"""

import asyncio
import os
import time
import logging
from typing import Optional, Literal
from datetime import datetime
import httpx
from app.exceptions import (
    APIError,
    ConfigError,
    RateLimitExceeded,
)

logger = logging.getLogger(__name__)

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# Validation
if not all([ANTHROPIC_API_KEY, DEEPSEEK_API_KEY, TOGETHER_API_KEY]):
    raise ConfigError("Missing one or more API keys in environment variables")

# Configuration
MAX_RETRIES = 3
RETRY_DELAY_BASE = 1  # seconds
RETRY_BACKOFF = 2.0  # exponential multiplier
REQUEST_TIMEOUT = 120.0  # seconds
RATE_LIMIT_TRACKING = {}  # {model: {timestamp: count}}


class AgentRouter:
    """
    Main router for managing LLM calls with retry logic, fallback,
    rate limiting, and comprehensive error handling.
    """

    def __init__(self):
        self.planner_model = "claude-3-5-sonnet-20241022"
        self.developer_model = "deepseek-chat"
        self.developer_model_reasoning = "deepseek-reasoner"
        self.ops_model = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"

    async def call_planner(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
    ) -> str:
        """
        Call Claude 3.5 Sonnet for planning and architecture tasks.
        """
        return await self._call_with_retry(
            model_type="planner",
            prompt=prompt,
            system=system,
            max_tokens=max_tokens,
        )

    async def call_developer(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
        reasoning: bool = False,
    ) -> str:
        """
        Call DeepSeek for code generation and technical implementation.
        """
        return await self._call_with_retry(
            model_type="developer",
            prompt=prompt,
            system=system,
            max_tokens=max_tokens,
            reasoning=reasoning,
        )

    async def call_fast_ops(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
    ) -> str:
        """
        Call Together AI for fast operations, reports, and QA.
        """
        return await self._call_with_retry(
            model_type="ops",
            prompt=prompt,
            system=system,
            max_tokens=max_tokens,
        )

    async def _call_with_retry(
        self,
        model_type: Literal["planner", "developer", "ops"],
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
        reasoning: bool = False,
    ) -> str:
        """
        Internal method with retry logic and exponential backoff.
        """
        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(
                    f"Attempt {attempt}/{MAX_RETRIES} for {model_type}",
                    extra={"model_type": model_type, "attempt": attempt},
                )

                if model_type == "planner":
                    return await self._call_anthropic(
                        prompt=prompt,
                        system=system,
                        max_tokens=max_tokens,
                    )
                elif model_type == "developer":
                    return await self._call_deepseek(
                        prompt=prompt,
                        system=system,
                        max_tokens=max_tokens,
                        reasoning=reasoning,
                    )
                elif model_type == "ops":
                    return await self._call_together(
                        prompt=prompt,
                        system=system,
                        max_tokens=max_tokens,
                    )

            except asyncio.TimeoutError:
                last_error = f"Timeout on {model_type} (attempt {attempt})"
                logger.warning(last_error)
                if attempt < MAX_RETRIES:
                    await self._exponential_backoff(attempt)
                continue

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limit - try fallback after waiting
                    last_error = f"Rate limited on {model_type}"
                    logger.warning(last_error)
                    if attempt < MAX_RETRIES:
                        await self._exponential_backoff(attempt * 2)
                    continue
                elif e.response.status_code >= 500:
                    # Server error - retry
                    last_error = f"Server error {e.response.status_code} on {model_type}"
                    logger.warning(last_error)
                    if attempt < MAX_RETRIES:
                        await self._exponential_backoff(attempt)
                    continue
                else:
                    # Client error - don't retry
                    raise APIError(f"API error: {e}")

            except APIError as e:
                last_error = str(e)
                logger.error(f"API Error on {model_type}: {e}")
                if attempt < MAX_RETRIES:
                    await self._exponential_backoff(attempt)
                continue

        # All retries exhausted
        raise APIError(f"Failed after {MAX_RETRIES} retries: {last_error}")

    async def _call_anthropic(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
    ) -> str:
        """
        Direct call to Anthropic (Claude 3.5 Sonnet).
        """
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.planner_model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()

            data = response.json()
            elapsed = time.time() - start_time

            if "content" not in data or len(data["content"]) == 0:
                raise APIError(f"Unexpected response format: {data}")

            result = data["content"][0]["text"]
            logger.info(
                f"Claude call successful",
                extra={
                    "model": self.planner_model,
                    "tokens_used": data.get("usage", {}).get("input_tokens", 0),
                    "elapsed_seconds": elapsed,
                },
            )
            return result

        except httpx.RequestError as e:
            raise APIError(f"Claude API request failed: {str(e)}")

    async def _call_deepseek(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
        reasoning: bool = False,
    ) -> str:
        """
        Direct call to DeepSeek (V3 or R1).
        """
        model = self.developer_model_reasoning if reasoning else self.developer_model

        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system} if system else None,
                {"role": "user", "content": prompt},
            ],
        }
        # Remove None values
        payload["messages"] = [m for m in payload["messages"] if m is not None]

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()

            data = response.json()
            elapsed = time.time() - start_time

            if "choices" not in data or len(data["choices"]) == 0:
                raise APIError(f"Unexpected response format: {data}")

            result = data["choices"][0]["message"]["content"]
            logger.info(
                f"DeepSeek call successful",
                extra={
                    "model": model,
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                    "elapsed_seconds": elapsed,
                },
            )
            return result

        except httpx.RequestError as e:
            raise APIError(f"DeepSeek API request failed: {str(e)}")

    async def _call_together(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
    ) -> str:
        """
        Direct call to Together AI (Llama 3.1 70B).
        """
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.ops_model,
            "messages": [
                {"role": "system", "content": system} if system else None,
                {"role": "user", "content": prompt},
            ],
        }
        # Remove None values
        payload["messages"] = [m for m in payload["messages"] if m is not None]

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(
                    "https://api.together.xyz/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()

            data = response.json()
            elapsed = time.time() - start_time

            if "choices" not in data or len(data["choices"]) == 0:
                raise APIError(f"Unexpected response format: {data}")

            result = data["choices"][0]["message"]["content"]
            logger.info(
                f"Together call successful",
                extra={
                    "model": self.ops_model,
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                    "elapsed_seconds": elapsed,
                },
            )
            return result

        except httpx.RequestError as e:
            raise APIError(f"Together API request failed: {str(e)}")

    @staticmethod
    async def _exponential_backoff(attempt: int) -> None:
        """
        Exponential backoff with jitter.
        """
        delay = RETRY_DELAY_BASE * (RETRY_BACKOFF ** (attempt - 1))
        # Add jitter: ±10%
        import random
        jitter = delay * (0.9 + random.random() * 0.2)
        logger.info(f"Waiting {jitter:.2f}s before retry")
        await asyncio.sleep(jitter)


# Singleton instance
router = AgentRouter()
