import os
import httpx


class AgentRouter:

    def __init__(self):
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")

    async def execute_task(self, prompt: str) -> str:
        if not self.deepseek_key:
            return "⚠️ مفتاح DEEPSEEK_API_KEY غير مفعّل في المتغيرات البيئية."

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
            async with httpx.AsyncClient(timeout=90.0) as client:
                res = await client.post(
                    "https://api.deepseek.com/chat/completions",
                    json=payload,
                    headers=headers,
                )
                if res.status_code == 200:
                    return res.json()["choices"][0]["message"]["content"]
                return f"⚠️ خطأ من مزود الذكاء الاصطناعي: {res.status_code}"
        except Exception as e:
            return f"❌ تعذر الاتصال بالوكيل الذكي: {str(e)}"
