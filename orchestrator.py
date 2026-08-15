import httpx
import os
import json
from datetime import datetime

class DigitalCastleOrchestrator:
    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.together_key = os.getenv("TOGETHER_API_KEY")
        self.tasks_completed = []
    
    async def claude_plan(self, task: str):
        """Claude يخطط"""
        print(f"📋 Claude التخطيط: {task}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={"x-api-key": self.anthropic_key},
                    json={
                        "model": "claude-3-5-sonnet-20241022",
                        "max_tokens": 2048,
                        "messages": [{"role": "user", "content": f"Plan this task: {task}"}]
                    },
                    timeout=60
                )
                result = response.json()
                print(f"✅ Claude: تم التخطيط")
                return result
            except Exception as e:
                print(f"❌ Claude Error: {e}")
                return {"error": str(e)}
    
    async def deepseek_code(self, task: str, plan: str):
        """DeepSeek يكتب الكود"""
        print(f"💻 DeepSeek يكتب: {task}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.deepseek_key}"},
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": f"Write complete code for: {task}\nBased on plan: {plan}"}]
                    },
                    timeout=60
                )
                result = response.json()
                print(f"✅ DeepSeek: الكود جاهز")
                return result
            except Exception as e:
                print(f"❌ DeepSeek Error: {e}")
                return {"error": str(e)}
    
    async def together_review(self, task: str, code: str):
        """Together يقيّم"""
        print(f"🔍 Together يقيّم: {task}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.together.xyz/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.together_key}"},
                    json={
                        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                        "messages": [{"role": "user", "content": f"Review this code:\n{code}\n\nIs it production-ready?"}],
                        "max_tokens": 1024
                    },
                    timeout=60
                )
                result = response.json()
                print(f"✅ Together: التقييم اكتمل")
                return result
            except Exception as e:
                print(f"❌ Together Error: {e}")
                return {"error": str(e)}
    
    async def execute_task(self, task_name: str, description: str):
        """تنفيذ مهمة كاملة"""
        print(f"\n{'='*60}")
        print(f"🚀 مهمة: {task_name}")
        print(f"{'='*60}\n")
        
        plan = await self.claude_plan(description)
        code = await self.deepseek_code(task_name, str(plan))
        review = await self.together_review(task_name, str(code))
        
        result = {
            "task": task_name,
            "timestamp": datetime.now().isoformat(),
            "plan": plan,
            "code": code,
            "review": review
        }
        
        self.tasks_completed.append(result)
        print(f"\n✨ اكتملت: {task_name}\n")
        return result
    
    async def build_project(self):
        """بناء المشروع بالكامل"""
        
        tasks = [
            {
                "name": "Telegram Bot Orchestrator",
                "description": "Create bot_orchestrator.py with Telegram bot and commands"
            },
            {
                "name": "Agent Router",
                "description": "Create agent_router.py - routes tasks to 3 APIs"
            },
            {
                "name": "Document Engine",
                "description": "Create app/document_engine.py - PDF generation"
            },
            {
                "name": "Security Module",
                "description": "Create app/security.py - encryption and watermarking"
            }
        ]
        
        print("\n🏰 Digital Castle - Build Starting\n")
        
        for task in tasks:
            await self.execute_task(task["name"], task["description"])
        
        print("\n✅ كل المهام اكتملت!\n")
        return self.tasks_completed

if __name__ == "__main__":
    import asyncio
    orchestrator = DigitalCastleOrchestrator()
    results = asyncio.run(orchestrator.build_project())
    
    with open("build_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("📁 النتائج في: build_results.json")
