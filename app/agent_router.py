import os
import httpx


class AgentRouter:

    def __init__(self):
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    async def execute_task(self, prompt: str, agent_type: str = "deepseek") -> str:
        if agent_type == "deepseek" and self.deepseek_key:
            return await self._call_deepseek(prompt)
        return "⚠️ مفتاح DEEPSEEK_API_KEY غير مفعّل أو غير متوفر."

    async def _call_deepseek(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.deepseek_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "أنت المستشار التقني لشركة Digital Castle S.P.C. أجب بأسلوب احترافي وعملي.",
                },
                {"role": "user", "content": prompt},
            ],
        }
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(
                    "https://api.deepseek.com/chat/completions",
                    json=payload,
                    headers=headers,
                )
                if res.status_code == 200:
                    return res.json()["choices"][0]["message"]["content"]
                return f"⚠️ استجابة غير متوقعة من المزود: {res.status_code} - {res.text}"
        except Exception as e:
            return f"❌ خطأ أثناء الاتصال بالوكيل الذكي: {str(e)}"
