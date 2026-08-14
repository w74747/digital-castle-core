import os
import httpx

# قراءة المفاتيح المعرفة في متغيرات بيئة Railway
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")


async def call_planner(prompt: str, system: str = "") -> str:
    """استدعاء Claude 3.5 Sonnet: للتخطيط المعماري وتوليد الـ Specs"""
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
    async with httpx.AsyncClient(timeout=120.0) as client:
        res = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
        )
        data = res.json()
        return data["content"][0]["text"]


async def call_developer(
    prompt: str, system: str = "", reasoning: bool = False
) -> str:
    """استدعاء DeepSeek: لكتابة الكود وفحص الأمان وقواعد البيانات"""
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
    async with httpx.AsyncClient(timeout=120.0) as client:
        res = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        data = res.json()
        return data["choices"][0]["message"]["content"]


async def call_fast_ops(prompt: str, system: str = "") -> str:
    """استدعاء Together AI: للتسويق، تقارير التلجرام، الفحص السريع ومراقبة الموارد"""
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
    async with httpx.AsyncClient(timeout=60.0) as client:
        res = await client.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        data = res.json()
        return data["choices"][0]["message"]["content"]
