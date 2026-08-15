"""Code Graph RAG Adapter"""
import os
from typing import Dict, List
from app.logging_config import get_logger

logger = get_logger(__name__)

class CodeAnalyzer:
    def __init__(self):
        self.cache = {}
    
    async def analyze_repository(self, repo_path: str) -> Dict:
        logger.info(f"Analyzing repository: {repo_path}")
        return {"files": await self._scan_files(repo_path), "dependencies": {}}
    
    async def _scan_files(self, path: str) -> List[str]:
        files = []
        for root, dirs, filenames in os.walk(path):
            for file in filenames:
                if file.endswith(('.py', '.js', '.ts')):
                    files.append(os.path.join(root, file))
        return files

class CodeGraphRAG:
    def __init__(self):
        self.analyzer = CodeAnalyzer()
    
    async def analyze(self, repo_path: str) -> Dict:
        return await self.analyzer.analyze_repository(repo_path)

code_graph = CodeGraphRAG()
