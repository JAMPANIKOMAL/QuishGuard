import cv2
import numpy as np
from pyzbar.pyzbar import decode
import os
import fitz  # PyMuPDF

class ScannerEngine:
    """
    Handles the processing of images AND PDFs.
    Updated to find MULTIPLE QR codes and report progress.
    """
    
    def extract_qr(self, file_path, progress_callback=None):
        """
        Returns a LIST of found QR strings.
        progress_callback: function(int) that accepts a percentage (0-100).
        """
        if not os.path.exists(file_path):
            return ["[!] Error: File does not exist."]
        
        # Initialize results list
        found_qrs = []
        
        if file_path.lower().endswith(".pdf"):
            found_qrs = self._scan_pdf(file_path, progress_callback)
        else:
            # Image: Simulate 0 -> 100% progress for consistency
            if progress_callback: progress_callback(10)
            res = self._scan_image(file_path)
            if res: found_qrs.append(res)
            if progress_callback: progress_callback(100)

        # Remove duplicates and return
        return list(set(found_qrs))

    def _scan_image(self, file_path):
        img = cv2.imread(file_path)
        if img is None: return None
        return self._decode_frame(img)

    def _scan_pdf(self, file_path, progress_callback):
        results = []
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            for i, page in enumerate(doc):
                # Update Progress Bar
                if progress_callback:
                    percent = int(((i + 1) / total_pages) * 100)
                    progress_callback(percent)

                # Render page (Zoom=2 for quality)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                
                # Convert to format OpenCV can read
                if pix.n < 3:
                    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w)
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                else:
                    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                
                # Scan page
                decoded = self._decode_frame(img)
                if decoded:
                    results.append(decoded)
            
            return results
            
        except Exception as e:
            return [f"[!] PDF Error: {str(e)}"]

    def _decode_frame(self, img):
        try:
            decoded_objects = decode(img)
            if not decoded_objects:
                return None
            # For now, return the first QR found on a single page
            return decoded_objects[0].data.decode("utf-8")
        except:
            return None