import requests
from urllib.parse import urlparse
from defang import defang

class URLAnalyzer:
    """
    The 'Blue Team' logic. Analyzes URLs for suspicious traits
    and uncovers redirection chains.
    """
    
    def analyze(self, qr_data):
        """
        Main entry point. Returns a dictionary with analysis results.
        """
        # 1. Basic Validation
        if not qr_data:
            return {"status": "error", "message": "Empty Data"}
            
        # Check if it looks like a URL (simple check)
        if not (qr_data.startswith("http://") or qr_data.startswith("https://")):
            return {
                "status": "info",
                "type": "Text",
                "safe_url": qr_data, # No defanging needed for plain text
                "chain": []
            }

        # 2. Unshortening / Redirection Tracing
        try:
            chain = self.trace_redirects(qr_data)
            final_url = chain[-1]
        except Exception as e:
            return {"status": "error", "message": f"Network Error: {str(e)}"}

        # 3. Safety Defanging (Prevent accidental clicks)
        safe_final_url = defang(final_url)
        
        return {
            "status": "success",
            "type": "URL",
            "original": defang(qr_data),
            "final": safe_final_url,
            "chain": chain, # List of all hops
            "domain": urlparse(final_url).netloc
        }

    def trace_redirects(self, url):
        """
        Follows HTTP redirects without downloading the page content (HEAD request).
        """
        session = requests.Session()
        # Pretend to be a regular Chrome browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        history = [url]
        current_url = url
        
        # Max 10 redirects to prevent infinite loops
        for _ in range(10):
            try:
                # allow_redirects=False lets us inspect each hop manually
                response = session.head(current_url, headers=headers, allow_redirects=False, timeout=5)
                
                # If it's a redirect (301, 302, etc.)
                if 300 <= response.status_code < 400:
                    next_url = response.headers.get('Location')
                    if not next_url:
                        break
                    
                    # Handle relative redirects (e.g., "/login")
                    if next_url.startswith('/'):
                        parsed = urlparse(current_url)
                        next_url = f"{parsed.scheme}://{parsed.netloc}{next_url}"
                        
                    history.append(next_url)
                    current_url = next_url
                else:
                    break # End of the chain
                    
            except requests.RequestException:
                break # Network failure, stop tracing
                
        return history