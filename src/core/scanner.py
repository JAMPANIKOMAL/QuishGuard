import cv2
import numpy as np
from pyzbar.pyzbar import decode
import os

class ScannerEngine:
    """
    Handles the processing of images to extract QR code data.
    """
    
    def extract_qr(self, file_path):
        """
        Reads an image file and returns the decoded string.
        Returns None if no QR is found.
        """
        # 1. Validation
        if not os.path.exists(file_path):
            return "[!] Error: File does not exist."
        
        # 2. Load Image (Grayscale for better detection)
        # cv2.imread loads the image into a numpy array
        img = cv2.imread(file_path)
        
        if img is None:
            return "[!] Error: OpenCV could not read the file. Is it a valid image?"

        # 3. Pre-processing (Optional: simple thresholding if needed later)
        # For now, pyzbar is smart enough to handle raw color images
        
        # 4. Decode
        try:
            decoded_objects = decode(img)
            
            if not decoded_objects:
                return None # No QR found
            
            # Return the data from the first QR code found
            # .decode('utf-8') converts bytes to string
            return decoded_objects[0].data.decode("utf-8")
            
        except Exception as e:
            return f"[!] Critical Error during decoding: {str(e)}"