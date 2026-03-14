"""
SecurityAgent - Performs SafeDep-style file scanning and Gearsec URL threat detection
"""
import os
import re
import json
import hashlib
import requests
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import aiohttp
from agents.base_agent import BaseAgent

# Try to import python-magic, fallback to mimetypes
try:
    import magic
    # Test if libmagic is actually available
    magic.from_file(__file__, mime=True)
    MAGIC_AVAILABLE = True
except (ImportError, Exception):
    import mimetypes
    MAGIC_AVAILABLE = False

class SecurityAgent(BaseAgent):
    """
    Security agent that:
    1. Validates file types (SafeDep-style file security)
    2. Scans URLs for threats (Gearsec-style threat detection)
    3. Uses VirusTotal API for URL reputation checks
    """
    
    # Suspicious file extensions
    DANGEROUS_EXTENSIONS = {'.exe', '.dll', '.bat', '.cmd', '.sh', '.php', '.jsp', '.asp'}
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.pdf'}
    
    # Suspicious URL patterns
    SUSPICIOUS_PATTERNS = [
        r'bit\.ly|tinyurl|t\.co|goo\.gl',  # URL shorteners
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP addresses
        r'\.tk|\.ml|\.ga|\.cf|\.gq',  # Free domains often used for phishing
        r'phishing|malware|virus|hack',  # Suspicious keywords
    ]
    
    def __init__(self, event_logger=None):
        super().__init__("SecurityAgent", event_logger)
        self.virustotal_api_key = os.getenv("VIRUSTOTAL_API_KEY")
        self.safedep_api_key = os.getenv("SAFEDEP_API_KEY", "")
        self.gearsec_api_key = os.getenv("GEARSEC_API_KEY", "")
    
    def get_file_type(self, file_path: str) -> str:
        """Detect file type using magic or mimetypes"""
        if MAGIC_AVAILABLE:
            try:
                return magic.from_file(file_path, mime=True)
            except:
                pass
        
        # Fallback to mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "unknown"
    
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """
        SafeDep-style file security scanning
        """
        result = {
            "safe": True,
            "threats": [],
            "file_type": "unknown",
            "file_size": 0,
            "checksums": {}
        }
        
        try:
            if not os.path.exists(file_path):
                return {**result, "safe": False, "threats": ["File not found"]}
            
            # Get file size
            file_size = os.path.getsize(file_path)
            result["file_size"] = file_size
            
            # Check for suspicious size (too large might be an attack)
            if file_size > 50 * 1024 * 1024:  # 50MB
                result["safe"] = False
                result["threats"].append("File exceeds maximum size limit (50MB)")
            
            # Detect file type
            file_type = self.get_file_type(file_path)
            result["file_type"] = file_type
            
            # Validate file extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext in self.DANGEROUS_EXTENSIONS:
                result["safe"] = False
                result["threats"].append(f"Dangerous file extension: {ext}")
            elif ext not in self.ALLOWED_EXTENSIONS:
                result["warnings"] = [f"Unusual file extension: {ext}"]
            
            # Verify content matches extension (basic check)
            if ext in {'.jpg', '.jpeg'} and "image" not in file_type:
                result["safe"] = False
                result["threats"].append("File content does not match JPG extension")
            elif ext == '.png' and "png" not in file_type.lower():
                result["safe"] = False
                result["threats"].append("File content does not match PNG extension")
            
            # Calculate checksums
            with open(file_path, 'rb') as f:
                content = f.read()
                result["checksums"] = {
                    "md5": hashlib.md5(content).hexdigest(),
                    "sha1": hashlib.sha1(content).hexdigest(),
                    "sha256": hashlib.sha256(content).hexdigest()
                }
            
            return result
            
        except Exception as e:
            return {**result, "safe": False, "threats": [f"Scan error: {str(e)}"]}
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        return re.findall(url_pattern, text)
    
    async def check_url_virustotal(self, url: str) -> Dict[str, Any]:
        """
        Gearsec-style URL threat detection using VirusTotal API
        """
        if not self.virustotal_api_key:
            return {
                "safe": True,
                "threat_score": 0,
                "checked": False,
                "reason": "VirusTotal API key not configured"
            }
        
        try:
            headers = {"x-apikey": self.virustotal_api_key}
            
            # Submit URL for scanning
            submit_url = "https://www.virustotal.com/api/v3/urls"
            data = {"url": url}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(submit_url, headers=headers, data=data) as resp:
                    if resp.status == 200:
                        submit_result = await resp.json()
                        analysis_id = submit_result.get("data", {}).get("id")
                        
                        if analysis_id:
                            # Get analysis results
                            analysis_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
                            async with session.get(analysis_url, headers=headers) as analysis_resp:
                                if analysis_resp.status == 200:
                                    analysis = await analysis_resp.json()
                                    stats = analysis.get("data", {}).get("attributes", {}).get("stats", {})
                                    
                                    malicious = stats.get("malicious", 0)
                                    suspicious = stats.get("suspicious", 0)
                                    harmless = stats.get("harmless", 0)
                                    
                                    total_checked = malicious + suspicious + harmless
                                    threat_score = 0
                                    
                                    if total_checked > 0:
                                        threat_score = ((malicious * 2 + suspicious) / (total_checked * 2)) * 100
                                    
                                    return {
                                        "safe": malicious == 0 and suspicious == 0,
                                        "threat_score": round(threat_score, 2),
                                        "malicious": malicious,
                                        "suspicious": suspicious,
                                        "harmless": harmless,
                                        "checked": True,
                                        "url": url
                                    }
            
            return {
                "safe": True,
                "threat_score": 0,
                "checked": False,
                "reason": "Could not complete VirusTotal check"
            }
            
        except Exception as e:
            return {
                "safe": True,
                "threat_score": 0,
                "checked": False,
                "reason": f"Error: {str(e)}"
            }
    
    def check_url_heuristic(self, url: str) -> Dict[str, Any]:
        """Heuristic URL threat detection"""
        result = {
            "suspicious": False,
            "indicators": [],
            "domain_age_concern": False
        }
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check against suspicious patterns
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                result["suspicious"] = True
                result["indicators"].append(f"Matches suspicious pattern: {pattern}")
        
        # Check for suspicious TLDs
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.top', '.xyz']
        for tld in suspicious_tlds:
            if domain.endswith(tld):
                result["suspicious"] = True
                result["indicators"].append(f"Suspicious TLD: {tld}")
        
        # Check for URL encoding obfuscation
        if '%' in url and url.count('%') > 5:
            result["suspicious"] = True
            result["indicators"].append("Heavy URL encoding (possible obfuscation)")
        
        # Check for credential harvest patterns
        credential_keywords = ['login', 'password', 'account', 'verify', 'secure', 'update']
        if any(kw in url.lower() for kw in credential_keywords):
            result["indicators"].append("Contains credential-related keywords")
        
        return result
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute security scanning
        
        Context must contain:
        - file_path: Path to uploaded file
        - claim_reason: Text that may contain URLs
        - claim_id: Unique claim identifier
        """
        file_path = context.get("file_path")
        claim_reason = context.get("claim_reason", "")
        claim_id = context.get("claim_id")
        
        self.start_task(claim_id)
        
        try:
            results = {
                "file_scan": None,
                "url_scans": [],
                "overall_safe": True,
                "security_score": 0,  # 0-100, higher is more dangerous
                "threats_found": []
            }
            
            # File scan
            if file_path and os.path.exists(file_path):
                file_scan = self.scan_file(file_path)
                results["file_scan"] = file_scan
                
                if not file_scan["safe"]:
                    results["overall_safe"] = False
                    results["threats_found"].extend(file_scan.get("threats", []))
                    results["security_score"] += 30
            
            # URL extraction and scanning
            urls = self.extract_urls(claim_reason)
            
            for url in urls:
                # Heuristic check
                heuristic = self.check_url_heuristic(url)
                
                # VirusTotal check
                vt_result = await self.check_url_virustotal(url)
                
                url_result = {
                    "url": url,
                    "heuristic": heuristic,
                    "virustotal": vt_result,
                    "safe": not heuristic["suspicious"] and vt_result.get("safe", True)
                }
                
                results["url_scans"].append(url_result)
                
                if not url_result["safe"]:
                    results["overall_safe"] = False
                    results["threats_found"].append(f"Suspicious URL: {url}")
                    results["security_score"] += 20
            
            # Cap security score at 100
            results["security_score"] = min(results["security_score"], 100)
            
            self.log_event("security_scan_complete", {
                "safe": results["overall_safe"],
                "score": results["security_score"],
                "threats": len(results["threats_found"])
            })
            
            self.complete_task(results)
            return results
            
        except Exception as e:
            error_result = {
                "overall_safe": False,
                "security_score": 50,
                "error": str(e)
            }
            self.fail_task(str(e))
            return error_result
