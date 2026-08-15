# app/code_graph_adapter.py
"""Code Graph RAG Adapter"""
import os
import asyncio
from typing import List, Dict
from app.logging_config import get_logger

logger = get_logger(__name__)

class CodeAnalyzer:
    def __init__(self):
        self.cache = {}
    
    async def analyze_repository(self, repo_path: str) -> Dict:
        logger.info(f"Analyzing repository: {repo_path}")
        structure = {
            "files": await self._scan_files(repo_path),
            "dependencies": await self._extract_dependencies(repo_path),
            "structure": await self._build_graph(repo_path),
        }
        return structure
    
    async def _scan_files(self, path: str) -> List[str]:
        files = []
        for root, dirs, filenames in os.walk(path):
            for file in filenames:
                if file.endswith(('.py', '.js', '.ts', '.java', '.go')):
                    files.append(os.path.join(root, file))
        return files
    
    async def _extract_dependencies(self, path: str) -> Dict:
        deps = {"external": [], "internal": []}
        req_file = os.path.join(path, "requirements.txt")
        if os.path.exists(req_file):
            with open(req_file) as f:
                deps["external"] = [line.strip() for line in f if line.strip()]
        return deps
    
    async def _build_graph(self, path: str) -> Dict:
        return {"nodes": await self._scan_files(path), "edges": []}
    
    async def extract_context(self, file_path: str, focus_area: str = None) -> str:
        logger.info(f"Extracting context: {file_path}")
        if not os.path.exists(file_path):
            return ""
        with open(file_path, 'r') as f:
            content = f.read()
        if focus_area:
            lines = content.split('\n')
            relevant = [l for l in lines if focus_area.lower() in l.lower()]
            return '\n'.join(relevant[:50])
        return content[:5000]

class CodeGraphRAG:
    def __init__(self):
        self.analyzer = CodeAnalyzer()
    
    async def analyze(self, repo_path: str) -> Dict:
        return await self.analyzer.analyze_repository(repo_path)
    
    async def get_context_for_task(self, task: Dict) -> str:
        file_path = task.get("file")
        focus = task.get("focus")
        if not file_path:
            return ""
        return await self.analyzer.extract_context(file_path, focus)

code_graph = CodeGraphRAG()
