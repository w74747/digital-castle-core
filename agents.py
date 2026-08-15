import httpx
import os

class AgentSystem:
    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.together_key = os.getenv("TOGETHER_API_KEY")
    
    async def claude_agent(self, prompt: str):
        """Agent لـ التخطيط والتصميم"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={"x-api-key": self.anthropic_key},
                    json={
                        "model": "claude-3-5-sonnet-20241022",
                        "max_tokens": 1024,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}
    
    async def deepseek_agent(self, prompt: str):
        """Agent لـ كتابة الكود"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.deepseek.com/v1/messages",
                    headers={"Authorization": f"Bearer {self.deepseek_key}"},
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}
    
    async def together_agent(self, prompt: str):
        """Agent لـ العمليات السريعة والتقارير"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.together.xyz/inference",
                    headers={"Authorization": f"Bearer {self.together_key}"},
                    json={
                        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                        "prompt": prompt,
                        "max_tokens": 512
                    }
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}
    
    async def orchestrate(self, task: str):
        """تنسيق الـ 3 agents معاً"""
        
        # 1. Claude يخطط
        plan = await self.claude_agent(f"Plan this task: {task}")
        
        # 2. DeepSeek يكتب الكود
        code = await self.deepseek_agent(f"Write code for: {plan}")
        
        # 3. Together يقيّم
        review = await self.together_agent(f"Review this: {code}")
        
        return {
            "task": task,
            "plan": plan,
            "code": code,
            "review": review
        }

agents = AgentSystem()
