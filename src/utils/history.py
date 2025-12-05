import json
import os
from datetime import datetime
from typing import List, Dict, Any

class HistoryManager:
    """
    Manages the persistent storage of scan results using a local JSON file.
    """
    
    def __init__(self, filename: str = "scan_history.json"):
        self.filename = filename

    def add_entry(self, file_name: str, scan_type: str, content: str) -> None:
        """
        Appends a new scan result to the history file.
        
        Args:
            file_name: Name of the scanned file.
            scan_type: Verdict of the scan (e.g., SAFE, HIGH RISK).
            content: The decoded content or URL.
        """
        entry: Dict[str, str] = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file": file_name,
            "type": scan_type,
            "content": content
        }
        
        history = self.load_history()
        history.insert(0, entry) 
        
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4)
        except OSError:
            pass

    def load_history(self) -> List[Dict[str, Any]]:
        """
        Retrieves the complete scan history.
        
        Returns:
            List of dictionary entries representing past scans.
        """
        if not os.path.exists(self.filename):
            return []
        
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return []