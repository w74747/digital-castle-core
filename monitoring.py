import asyncio
import httpx
from datetime import datetime

async def health_check():
    endpoints = [
        "http://localhost:8001/health",
        "http://localhost:8001/api/status",
        "http://localhost:8001/api/agents"
    ]
    
    print(f"[{datetime.now()}] Health Check Started")
    
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            try:
                response = await client.get(endpoint, timeout=5)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"{status} {endpoint} - {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} - {e}")
    
    print()

async def monitor():
    while True:
        await health_check()
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(monitor())
