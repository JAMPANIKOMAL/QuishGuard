import cv2
import numpy as np
from pyzbar.pyzbar import decode
import os
import fitz 
from typing import List, Optional, Callable

class ScannerEngine:
    """
    Handles the optical recognition and extraction of QR codes from 
    static images and multi-page PDF documents.
    """
    
    def extract_qr(self, file_path: str, progress_callback: Optional[Callable[[int], None]] = None) -> List[str]:
        """
        Scans a file for QR codes.
        
        Args:
            file_path: Path to the input file.
            progress_callback: Optional function to report progress (0-100).

        Returns:
            List of unique QR data strings found in the file.
        """
        if not os.path.exists(file_path):
            return ["[ERROR] File does not exist."]
        
        found_qrs = []
        
        if file_path.lower().endswith(".pdf"):
            found_qrs = self._scan_pdf(file_path, progress_callback)
        else:
            if progress_callback: progress_callback(10)
            res = self._scan_image(file_path)
            if res: found_qrs.append(res)
            if progress_callback: progress_callback(100)

        return list(set(found_qrs))

    def _scan_image(self, file_path: str) -> Optional[str]:
        img = cv2.imread(file_path)
        if img is None: return None
        return self._decode_frame(img)

    def _scan_pdf(self, file_path: str, progress_callback: Optional[Callable[[int], None]]) -> List[str]:
        results = []
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            for i, page in enumerate(doc):
                if progress_callback:
                    percent = int(((i + 1) / total_pages) * 100)
                    progress_callback(percent)

                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                
                # Convert PyMuPDF pixmap to OpenCV format
                if pix.n < 3:
                    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w)
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                else:
                    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                
                decoded = self._decode_frame(img)
                if decoded:
                    results.append(decoded)
            
            return results
            
        except Exception as e:
            return [f"[ERROR] PDF Processing Failed: {str(e)}"]

    def _decode_frame(self, img: np.ndarray) -> Optional[str]:
        try:
            decoded_objects = decode(img)
            if not decoded_objects:
                return None
            return decoded_objects[0].data.decode("utf-8")
        except Exception:
            return None