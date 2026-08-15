"""Agent Memory & Persistence System"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any
from app.logging_config import get_logger

logger = get_logger(__name__)

class MemoryStore:
    def __init__(self, storage_path: str = "data/memory"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    async def save_conversation(self, agent_id: str, messages: List[Dict]) -> str:
        filename = f"{self.storage_path}/{agent_id}_{datetime.now().isoformat()}.json"
        with open(filename, 'w') as f:
            json.dump(messages, f)
        logger.info(f"Saved conversation: {agent_id}")
        return filename

class VectorMemory:
    def __init__(self):
        self.vectors = {}

class CacheManager:
    def __init__(self):
        self.cache = {}
    
    def set(self, key: str, value: Any) -> None:
        self.cache[key] = value
    
    def get(self, key: str) -> Any:
        return self.cache.get(key)

memory_store = MemoryStore()
vector_memory = VectorMemory()
cache_manager = CacheManager()
