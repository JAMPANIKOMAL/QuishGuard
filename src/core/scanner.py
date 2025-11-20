import cv2
import numpy as np
from pyzbar.pyzbar import decode
import os
import fitz  # PyMuPDF

class ScannerEngine:
    """
    Handles the processing of images AND PDFs to extract QR code data.
    """
    
    def extract_qr(self, file_path):
        """
        Detects file type and routes to the correct scanner.
        Returns the decoded string or None.
        """
        if not os.path.exists(file_path):
            return "[!] Error: File does not exist."
        
        # Check if it's a PDF
        if file_path.lower().endswith(".pdf"):
            return self._scan_pdf(file_path)
        else:
            return self._scan_image(file_path)

    def _scan_image(self, file_path):
        """Standard Image Scanning (OpenCV)"""
        img = cv2.imread(file_path)
        
        if img is None:
            return "[!] Error: OpenCV could not read the file. Is it a valid image?"

        return self._decode_frame(img)

    def _scan_pdf(self, file_path):
        """
        PDF Scanning: Renders pages to images in memory.
        """
        try:
            doc = fitz.open(file_path)
            
            # Iterate through every page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Render page to an image (Zoom=2 for better QR resolution)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                
                # Convert PyMuPDF Pixmap to Numpy Array (for OpenCV/pyzbar)
                # pix.samples is the raw byte data
                if pix.n < 3:
                    # Grayscale
                    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w)
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                else:
                    # RGB
                    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                    # PyMuPDF gives RGB, OpenCV expects BGR usually, but pyzbar handles RGB fine.
                    # We convert just to be safe and standard.
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                
                # Scan this page
                result = self._decode_frame(img)
                
                if result:
                    return result # Return immediately if found
            
            return None # No QR found in entire PDF
            
        except Exception as e:
            return f"[!] PDF Error: {str(e)}"

    def _decode_frame(self, img):
        """Helper: Decodes a single numpy image array"""
        try:
            decoded_objects = decode(img)
            if not decoded_objects:
                return None
            return decoded_objects[0].data.decode("utf-8")
        except Exception as e:
            return f"[!] Decode Error: {str(e)}"