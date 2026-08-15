# app/security_scanner.py
"""OpenVuln Security Scanner Adapter"""
import subprocess
import json
from typing import Dict, List
from app.logging_config import get_logger

logger = get_logger(__name__)

class VulnerabilityScanner:
    @staticmethod
    async def scan_dependencies(requirements_file: str) -> Dict:
        logger.info(f"Scanning: {requirements_file}")
        try:
            result = subprocess.run(
                ["safety", "check", "--file", requirements_file, "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout:
                return json.loads(result.stdout)
            return {"vulnerabilities": []}
        except Exception as e:
            logger.error(f"Scan error: {e}")
            return {"vulnerabilities": [], "error": str(e)}
    
    @staticmethod
    async def scan_code(directory: str) -> Dict:
        logger.info(f"Code scan: {directory}")
        try:
            result = subprocess.run(
                ["bandit", "-r", directory, "-f", "json"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.stdout:
                return json.loads(result.stdout)
            return {"results": []}
        except Exception as e:
            logger.error(f"Code scan error: {e}")
            return {"results": [], "error": str(e)}
    
    @staticmethod
    async def generate_report(scan_results: Dict) -> str:
        vulns = scan_results.get("vulnerabilities", [])
        if not vulns:
            return "✅ No vulnerabilities found"
        report = f"⚠️ Found {len(vulns)} vulnerabilities:\n\n"
        for vuln in vulns[:10]:
            report += f"• {vuln.get('package')}: {vuln.get('vulnerability')}\n"
        return report

class SecurityScanner:
    def __init__(self):
        self.scanner = VulnerabilityScanner()
    
    async def full_scan(self, repo_path: str) -> Dict:
        logger.info(f"Full security scan: {repo_path}")
        results = {
            "dependencies": await self.scanner.scan_dependencies(f"{repo_path}/requirements.txt"),
            "code": await self.scanner.scan_code(f"{repo_path}/app"),
        }
        return results
    
    async def get_report(self, results: Dict) -> str:
        report = "🛡️ SECURITY REPORT\n\n"
        dep_vulns = results.get("dependencies", {}).get("vulnerabilities", [])
        report += f"Dependencies: {len(dep_vulns)} vulnerabilities\n"
        code_results = results.get("code", {}).get("results", [])
        report += f"Code: {len(code_results)} issues\n\n"
        report += await self.scanner.generate_report(results.get("dependencies", {}))
        return report

security_scanner = SecurityScanner()
