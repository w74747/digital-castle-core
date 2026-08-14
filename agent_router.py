import httpx
from config import ANTHROPIC_API_KEY, DEEPSEEK_API_KEY, TOGETHER_API_KEY

async def call_claude(prompt: str, system: str = "") -> str:
    """للتخطيط المعماري، دراسات الجدوى، وتصميم واجهات الـ UI"""
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 4096,
        "system": system,
        "messages": [{"role": "user", "content": prompt}]
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        res = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
        data = res.json()
        return data["content"][0]["text"]

async def call_deepseek(prompt: str, system: str = "", reasoning: bool = False) -> str:
    """لكتابة الكود السريع، الأمان والحماية، وإدارة قواعد البيانات"""
    model = "deepseek-reasoner" if reasoning else "deepseek-chat"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        res = await client.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload)
        data = res.json()
        return data["choices"][0]["message"]["content"]

async def call_together(prompt: str, system: str = "") -> str:
    """لصيد الترندات، التسويق، التقارير السريعة، وفحص الأرصدة"""
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        res = await client.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=payload)
        data = res.json()
        return data["choices"][0]["message"]["content"]
