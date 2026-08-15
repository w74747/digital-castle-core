# app/memory_system.py
"""Agent Memory & Persistence System"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from app.logging_config import get_logger

logger = get_logger(__name__)

class MemoryStore:
    def __init__(self, storage_path: str = "data/memory"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.cache = {}
    
    async def save_conversation(self, agent_id: str, messages: List[Dict]) -> str:
        filename = f"{self.storage_path}/{agent_id}_{datetime.now().isoformat()}.json"
        with open(filename, 'w') as f:
            json.dump(messages, f, indent=2)
        logger.info(f"Saved conversation: {agent_id}")
        return filename
    
    async def load_conversation(self, agent_id: str) -> List[Dict]:
        pattern = f"{self.storage_path}/{agent_id}_*.json"
        import glob
        files = sorted(glob.glob(pattern))
        if not files:
            return []
        latest = files[-1]
        with open(latest) as f:
            return json.load(f)
    
    async def save_agent_state(self, agent_id: str, state: Dict) -> None:
        state_file = f"{self.storage_path}/{agent_id}_state.json"
        state["last_updated"] = datetime.now().isoformat()
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        logger.info(f"Saved state: {agent_id}")
    
    async def load_agent_state(self, agent_id: str) -> Dict:
        state_file = f"{self.storage_path}/{agent_id}_state.json"
        if not os.path.exists(state_file):
            return {}
        with open(state_file) as f:
            return json.load(f)
    
    async def save_task_result(self, task_id: str, result: Dict) -> None:
        result_file = f"{self.storage_path}/tasks/{task_id}.json"
        os.makedirs(os.path.dirname(result_file), exist_ok=True)
        result["completed_at"] = datetime.now().isoformat()
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Saved task result: {task_id}")
    
    async def get_task_history(self, limit: int = 10) -> List[Dict]:
        task_dir = f"{self.storage_path}/tasks"
        if not os.path.exists(task_dir):
            return []
        tasks = []
        for filename in os.listdir(task_dir)[-limit:]:
            with open(f"{task_dir}/{filename}") as f:
                tasks.append(json.load(f))
        return tasks

class VectorMemory:
    def __init__(self):
        self.vectors = {}
    
    async def store(self, key: str, embedding: List[float], metadata: Dict) -> None:
        self.vectors[key] = {
            "embedding": embedding,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
    
    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        results = []
        for key, data in self.vectors.items():
            similarity = self._cosine_similarity(query_embedding, data["embedding"])
            results.append({"key": key, "similarity": similarity, "metadata": data["metadata"]})
        return sorted(results, key=lambda x: x["similarity"], reverse=True)[:top_k]
    
    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        import math
        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = math.sqrt(sum(x ** 2 for x in a))
        magnitude_b = math.sqrt(sum(x ** 2 for x in b))
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        return dot_product / (magnitude_a * magnitude_b)

class CacheManager:
    def __init__(self, ttl_hours: int = 24):
        self.cache = {}
        self.ttl_hours = ttl_hours
    
    def set(self, key: str, value: Any) -> None:
        self.cache[key] = {"value": value, "expires_at": datetime.now() + timedelta(hours=self.ttl_hours)}
    
    def get(self, key: str) -> Any:
        if key not in self.cache:
            return None
        entry = self.cache[key]
        if datetime.now() > entry["expires_at"]:
            del self.cache[key]
            return None
        return entry["value"]
    
    def clear_expired(self) -> int:
        now = datetime.now()
        expired = [k for k, v in self.cache.items() if now > v["expires_at"]]
        for key in expired:
            del self.cache[key]
        return len(expired)

memory_store = MemoryStore()
vector_memory = VectorMemory()
cache_manager = CacheManager()
