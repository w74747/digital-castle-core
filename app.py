from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI(title="Digital Castle")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# مفاتيح الـ APIs
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
TOGETHER_KEY = os.getenv("TOGETHER_API_KEY", "")

# Endpoints أساسية
@app.get("/")
def root():
    return {"message": "🏰 Digital Castle Online"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/status")
def status():
    return {"status": "online", "agents": 22}

@app.get("/api/agents")
def agents_list():
    return {"agents": ["Dev", "DevOps", "QA"], "count": 22}

# Agent endpoints
@app.post("/agents/claude")
async def claude_agent(prompt: str):
    """Claude - التخطيط والتصميم"""
    if not ANTHROPIC_KEY:
        return {"error": "ANTHROPIC_API_KEY not set"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": ANTHROPIC_KEY},
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

@app.post("/agents/deepseek")
async def deepseek_agent(prompt: str):
    """DeepSeek - كتابة الكود"""
    if not DEEPSEEK_KEY:
        return {"error": "DEEPSEEK_API_KEY not set"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"},
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

@app.post("/agents/together")
async def together_agent(prompt: str):
    """Together - العمليات السريعة"""
    if not TOGETHER_KEY:
        return {"error": "TOGETHER_API_KEY not set"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={"Authorization": f"Bearer {TOGETHER_KEY}"},
                json={
                    "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 512
                },
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

@app.post("/agents/orchestrate")
async def orchestrate(task: str):
    """تشغيل الـ 3 agents معاً"""
    
    results = {}
    
    # 1. Claude يخطط
    results["plan"] = await claude_agent(f"Plan this task: {task}")
    
    # 2. DeepSeek يكتب الكود
    results["code"] = await deepseek_agent(f"Write code for: {task}")
    
    # 3. Together يقيّم
    results["review"] = await together_agent(f"Review this implementation: {task}")
    
    return {
        "task": task,
        "results": results
    }
