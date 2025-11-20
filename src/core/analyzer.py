import requests
from urllib.parse import urlparse
from defang import defang

class URLAnalyzer:
    """
    The 'Blue Team' logic. Analyzes URLs for suspicious traits
    and uncovers redirection chains.
    """
    
    def analyze(self, qr_data):
        # 1. Basic Validation
        if not qr_data:
            return {"status": "error", "message": "Empty Data"}
            
        # Check if it looks like a URL
        if not (qr_data.startswith("http://") or qr_data.startswith("https://")):
            return {
                "status": "info",
                "type": "Text",
                "original": defang(qr_data), # <--- FIX: Added this key
                "safe_url": qr_data, 
                "chain": []
            }

        # 2. Unshortening
        try:
            chain = self.trace_redirects(qr_data)
            final_url = chain[-1] if chain else qr_data
        except Exception as e:
            return {"status": "error", "message": f"Network Error: {str(e)}"}

        # 3. Return Result
        safe_final_url = defang(final_url)
        
        return {
            "status": "success",
            "type": "URL",
            "original": defang(qr_data),
            "final": safe_final_url,
            "chain": chain,
            "domain": urlparse(final_url).netloc
        }

    def trace_redirects(self, url):
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        history = [url]
        current_url = url
        
        for _ in range(10):
            try:
                response = session.head(current_url, headers=headers, allow_redirects=False, timeout=5)
                if 300 <= response.status_code < 400:
                    next_url = response.headers.get('Location')
                    if not next_url: break
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