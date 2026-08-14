import os
import requests


class AgentRouter:

    def __init__(self):
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    def execute_task(self, prompt: str, agent_type: str = "deepseek") -> str:
        """توجيه الطلب للنموذج المناسب بناء على نوع المهمة"""
        if agent_type == "deepseek" and self.deepseek_key:
            return self._call_deepseek(prompt)
        return "تم استقبال المهمة، جاري التوجيه للوكيل المتاح."

    def _call_deepseek(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.deepseek_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "أنت المساعد الذكي لشركة Digital Castle S.P.C المتخصصة في الحلول التقنية.",
                },
                {"role": "user", "content": prompt},
            ],
        }
        try:
            res = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=30,
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            return f"خطأ من مزود الذكاء الاصطناعي: {res.status_code}"
        except Exception as e:
            return f"تعذر الاتصال بالوكيل: {str(e)}"
