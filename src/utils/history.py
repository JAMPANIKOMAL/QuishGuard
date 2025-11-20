import json
import os
from datetime import datetime

class HistoryManager:
    def __init__(self, filename="scan_history.json"):
        self.filename = filename

    def add_entry(self, file_name, scan_type, content):
        """Saves a new scan to the JSON file"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file": file_name,
            "type": scan_type,
            "content": content
        }
        
        # Load existing history
        history = self.load_history()
        history.insert(0, entry) # Add to top of list
        
        # Save back to file
        try:
            with open(self.filename, "w") as f:
                json.dump(history, f, indent=4)
        except Exception as e:
            print(f"Error saving history: {e}")

    def load_history(self):
        """Returns list of past scans"""
        if not os.path.exists(self.filename):
            return []
        
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except:
            return []