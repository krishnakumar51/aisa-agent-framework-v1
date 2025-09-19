"""
OCR utilities for processing screenshots and documents
"""
import io
import base64
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from app.config.settings import settings

class OCRProcessor:
    """OCR processing utilities"""
    
    def __init__(self):
        """Initialize OCR processor"""
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
    
    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Perform OCR
            text = pytesseract.image_to_string(image, config='--psm 6')
            return text.strip()
        except Exception as e:
            print(f"OCR error: {str(e)}")
            return ""
    
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF document"""
        try:
            # Open PDF from bytes
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            extracted_text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                extracted_text += page.get_text() + "\n"
            
            pdf_document.close()
            return extracted_text.strip()
        except Exception as e:
            print(f"PDF extraction error: {str(e)}")
            return ""
    
    def extract_images_from_pdf(self, pdf_bytes: bytes) -> List[bytes]:
        """Extract images from PDF document"""
        images = []
        try:
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    pix = fitz.Pixmap(pdf_document, xref)
                    
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_bytes = pix.tobytes("png")
                        images.append(img_bytes)
                    
                    pix = None
            
            pdf_document.close()
            return images
        except Exception as e:
            print(f"PDF image extraction error: {str(e)}")
            return []
    
    def get_image_info(self, image_bytes: bytes) -> Dict[str, Any]:
        """Get basic information about an image"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "size_bytes": len(image_bytes)
            }
        except Exception as e:
            print(f"Image info error: {str(e)}")
            return {}
    
    def resize_image(self, image_bytes: bytes, max_width: int = 1024, max_height: int = 768) -> bytes:
        """Resize image while maintaining aspect ratio"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Calculate new size maintaining aspect ratio
            ratio = min(max_width / image.width, max_height / image.height)
            if ratio < 1:
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert back to bytes
            output = io.BytesIO()
            image.save(output, format='PNG')
            return output.getvalue()
        except Exception as e:
            print(f"Image resize error: {str(e)}")
            return image_bytes
    
    def image_to_base64(self, image_bytes: bytes) -> str:
        """Convert image bytes to base64 string"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def base64_to_image(self, base64_string: str) -> bytes:
        """Convert base64 string to image bytes"""
        return base64.b64decode(base64_string)

# Global OCR processor instance
ocr_processor = OCRProcessor()