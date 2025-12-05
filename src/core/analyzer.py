import requests
import re
from urllib.parse import urlparse
from defang import defang
from typing import Dict, List, Tuple, Any

class URLAnalyzer:
    """
    Core intelligence engine for QuishGuard.
    Analyzes URLs for malicious indicators, redirection chains, and obfuscation.
    """

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        }
        self.sus_keywords = [
            "login", "verify", "update", "secure", "account", "banking", 
            "free", "bonus", "prize", "confirm", "wallet", "crypto", "auth"
        ]

    def analyze(self, qr_data: str) -> Dict[str, Any]:
        """
        Orchestrates the analysis process for a single QR data string.
        """
        if not qr_data:
            return {"status": "error", "message": "Empty Data"}
            
        # Regex to validate if the data is a URL
        if not re.match(r'^https?://', qr_data):
            return {
                "status": "info",
                "type": "Text",
                "original": defang(qr_data),
                "final": defang(qr_data),
                "chain": [],
                "domain": "N/A",
                "verdict": "SAFE",
                "score": 0,
                "flags": ["Plain Text Content"]
            }

        # Network Analysis (Tracing Redirects)
        try:
            chain = self._trace_redirects(qr_data)
            final_url = chain[-1] if chain else qr_data
        except Exception:
            # If network fails, proceed with static analysis of the original URL
            chain = [qr_data]
            final_url = qr_data
        
        # Heuristic Analysis
        verdict, score, flags = self._calculate_threat_score(final_url, chain)

        return {
            "status": "success",
            "type": "URL",
            "original": defang(qr_data),
            "final": defang(final_url),
            "chain": [defang(u) for u in chain],
            "domain": urlparse(final_url).netloc,
            "verdict": verdict,
            "score": score,
            "flags": flags
        }

    def _trace_redirects(self, url: str) -> List[str]:
        """
        Follows HTTP redirects to determine the final destination.
        Limits recursion to 8 hops to prevent infinite loops.
        """
        history = [url]
        current_url = url
        session = requests.Session()
        
        for _ in range(8):
            try:
                response = session.head(
                    current_url, 
                    headers=self.headers, 
                    allow_redirects=False, 
                    timeout=5
                )
                
                if 300 <= response.status_code < 400:
                    next_url = response.headers.get('Location')
                    if not next_url:
                        break
                        
                    # Handle relative redirects
                    if next_url.startswith('/'):
                        parsed = urlparse(current_url)
                        next_url = f"{parsed.scheme}://{parsed.netloc}{next_url}"
                        
                    history.append(next_url)
                    current_url = next_url
                else:
                    break
            except requests.RequestException:
                break
                
        return history

    def _calculate_threat_score(self, url: str, chain: List[str]) -> Tuple[str, int, List[str]]:
        """
        Calculates risk score based on static heuristics.
        Returns: (Verdict, Score, Flags)
        """
        score = 0
        flags = []
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Heuristic 1: Redirection Depth
        if len(chain) > 3:
            score += 2
            flags.append(f"Deep Redirection Chain ({len(chain)} hops)")
            
        # Heuristic 2: Raw IP Address usage
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
            score += 5
            flags.append("Destination is a Raw IP Address")

        # Heuristic 3: Suspicious Keywords in URL
        for word in self.sus_keywords:
            if word in url.lower():
                score += 1
                flags.append(f"Suspicious Keyword: '{word}'")

        # Heuristic 4: Dangerous File Extensions
        if url.lower().endswith(('.exe', '.zip', '.scr', '.apk', '.bat', '.ps1', '.vbs')):
            score += 5
            flags.append("Direct Executable/Archive Download")

        # Heuristic 5: Non-Standard Ports
        if parsed.port and parsed.port not in [80, 443, 8080]:
            score += 2
            flags.append(f"Non-Standard Port ({parsed.port})")

        # Final Verdict Logic
        if score >= 5:
            return "HIGH RISK", score, flags
        elif score >= 2:
            return "SUSPICIOUS", score, flags
        else:
            return "SAFE", score, ["Clean URL Structure"]