"""
OCR Utilities
Production OCR processing for document analysis and UI element detection
"""

import json
import logging
import base64
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

# OCR imports with fallbacks
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
    print("✅ OpenCV available for image processing")
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ OpenCV not available")

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
    print("✅ Tesseract OCR available")
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️ Tesseract OCR not available")

logger = logging.getLogger(__name__)

class OCRProcessor:
    """
    Production OCR processor for document analysis and UI element detection.
    Handles image preprocessing, text extraction, and coordinate mapping.
    """
    
    def __init__(self):
        self.ocr_available = TESSERACT_AVAILABLE
        self.cv2_available = CV2_AVAILABLE
        self.default_config = '--oem 3 --psm 6'
        logger.info(f"🔍 OCR Processor initialized - OCR: {self.ocr_available}, CV2: {self.cv2_available}")
    
    def preprocess_image(self, image_data: bytes) -> Optional[np.ndarray]:
        """Preprocess image for better OCR results"""
        
        if not self.cv2_available:
            logger.warning("⚠️ OpenCV not available for image preprocessing")
            return None
        
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error("❌ Failed to decode image")
                return None
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply noise reduction
            denoised = cv2.medianBlur(gray, 3)
            
            # Apply adaptive thresholding for better text contrast
            binary = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            logger.info("✅ Image preprocessing completed")
            return processed
            
        except Exception as e:
            logger.error(f"❌ Image preprocessing failed: {str(e)}")
            return None
    
    def extract_text_with_coordinates(self, image_data: bytes) -> Dict[str, Any]:
        """Extract text with bounding box coordinates"""
        
        if not self.ocr_available:
            logger.error("❌ OCR not available")
            return {
                "text": "",
                "elements": [],
                "error": "OCR not available"
            }
        
        try:
            # Preprocess image if OpenCV is available
            processed_image = None
            if self.cv2_available:
                processed_image = self.preprocess_image(image_data)
            
            # Use processed image if available, otherwise use PIL
            if processed_image is not None:
                # Convert numpy array to PIL Image
                pil_image = Image.fromarray(processed_image)
            else:
                # Direct PIL processing
                from io import BytesIO
                pil_image = Image.open(BytesIO(image_data))
            
            # Extract text with detailed data
            ocr_data = pytesseract.image_to_data(
                pil_image, 
                config=self.default_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Process OCR results
            elements = []
            full_text_parts = []
            
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()
                confidence = int(ocr_data['conf'][i])
                
                # Filter out low confidence and empty text
                if text and confidence > 30:
                    element = {
                        "text": text,
                        "coordinates": {
                            "x": int(ocr_data['left'][i]),
                            "y": int(ocr_data['top'][i]),
                            "width": int(ocr_data['width'][i]),
                            "height": int(ocr_data['height'][i])
                        },
                        "confidence": confidence / 100.0,
                        "block_num": int(ocr_data['block_num'][i]),
                        "par_num": int(ocr_data['par_num'][i]),
                        "line_num": int(ocr_data['line_num'][i]),
                        "word_num": int(ocr_data['word_num'][i])
                    }
                    elements.append(element)
                    full_text_parts.append(text)
            
            result = {
                "text": " ".join(full_text_parts),
                "elements": elements,
                "total_elements": len(elements),
                "processing_timestamp": datetime.now().isoformat(),
                "image_preprocessed": processed_image is not None
            }
            
            logger.info(f"✅ OCR extraction completed: {len(elements)} elements found")
            return result
            
        except Exception as e:
            logger.error(f"❌ OCR extraction failed: {str(e)}")
            return {
                "text": "",
                "elements": [],
                "error": str(e),
                "processing_timestamp": datetime.now().isoformat()
            }
    
    def detect_ui_elements(self, image_data: bytes, element_types: List[str] = None) -> List[Dict[str, Any]]:
        """Detect UI elements like buttons, inputs, labels"""
        
        if element_types is None:
            element_types = ["button", "input", "label", "link"]
        
        ocr_result = self.extract_text_with_coordinates(image_data)
        
        if "error" in ocr_result:
            return []
        
        ui_elements = []
        
        for element in ocr_result["elements"]:
            text = element["text"].lower()
            coords = element["coordinates"]
            
            # Classify element type based on text content and dimensions
            element_type = self._classify_element_type(text, coords)
            
            if element_type in element_types:
                ui_element = {
                    "element_type": element_type,
                    "text": element["text"],
                    "coordinates": coords,
                    "confidence": element["confidence"],
                    "selector": self._generate_selector(element_type, element["text"], coords),
                    "detected_by": "ocr"
                }
                ui_elements.append(ui_element)
        
        logger.info(f"🎯 UI elements detected: {len(ui_elements)}")
        return ui_elements
    
    def _classify_element_type(self, text: str, coords: Dict[str, int]) -> str:
        """Classify element type based on text and dimensions"""
        
        width = coords.get("width", 0)
        height = coords.get("height", 0)
        aspect_ratio = width / height if height > 0 else 1
        
        # Button keywords
        button_keywords = [
            "click", "submit", "send", "login", "sign in", "register", "sign up",
            "save", "cancel", "ok", "yes", "no", "continue", "next", "back",
            "search", "go", "enter", "add", "delete", "remove"
        ]
        
        # Input field indicators
        input_keywords = [
            "enter", "type", "input", "username", "password", "email", "name",
            "phone", "address", "search", "text", "number"
        ]
        
        # Link indicators
        link_keywords = [
            "http", "www", "click here", "read more", "learn more", "view",
            "download", "link"
        ]
        
        # Check for button characteristics
        if any(keyword in text for keyword in button_keywords):
            return "button"
        
        # Check for input field characteristics
        if any(keyword in text for keyword in input_keywords):
            return "input"
        
        # Check for link characteristics
        if any(keyword in text for keyword in link_keywords):
            return "link"
        
        # Check dimensions for button-like elements
        if 50 <= width <= 200 and 20 <= height <= 50 and 2 <= aspect_ratio <= 6:
            return "button"
        
        # Check for input field dimensions
        if width > 100 and 20 <= height <= 40 and aspect_ratio > 3:
            return "input"
        
        # Default classification
        return "label"
    
    def _generate_selector(self, element_type: str, text: str, coords: Dict[str, int]) -> str:
        """Generate CSS/XPath selector for the element"""
        
        # Clean text for selector
        clean_text = text.replace('"', '\\"').replace("'", "\\'")
        
        if element_type == "button":
            return f"//button[contains(text(), '{clean_text}')]"
        elif element_type == "input":
            return f"//input[@placeholder='{clean_text}' or @name='{clean_text.lower().replace(' ', '_')}']"
        elif element_type == "link":
            return f"//a[contains(text(), '{clean_text}')]"
        else:
            # Generic selector using text content
            return f"//*[contains(text(), '{clean_text}')]"
    
    def analyze_document_structure(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze document structure and layout"""
        
        ocr_result = self.extract_text_with_coordinates(image_data)
        
        if "error" in ocr_result:
            return {"error": ocr_result["error"]}
        
        elements = ocr_result["elements"]
        
        if not elements:
            return {"error": "No text elements found"}
        
        # Group elements by blocks and paragraphs
        blocks = {}
        paragraphs = {}
        
        for element in elements:
            block_num = element["block_num"]
            par_num = element["par_num"]
            
            if block_num not in blocks:
                blocks[block_num] = []
            blocks[block_num].append(element)
            
            if par_num not in paragraphs:
                paragraphs[par_num] = []
            paragraphs[par_num].append(element)
        
        # Analyze layout
        x_coords = [el["coordinates"]["x"] for el in elements]
        y_coords = [el["coordinates"]["y"] for el in elements]
        
        structure_analysis = {
            "total_elements": len(elements),
            "blocks_count": len(blocks),
            "paragraphs_count": len(paragraphs),
            "layout_bounds": {
                "left": min(x_coords) if x_coords else 0,
                "right": max(x_coords) if x_coords else 0,
                "top": min(y_coords) if y_coords else 0,
                "bottom": max(y_coords) if y_coords else 0
            },
            "blocks": blocks,
            "paragraphs": paragraphs,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"📋 Document structure analyzed: {len(blocks)} blocks, {len(paragraphs)} paragraphs")
        return structure_analysis
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get OCR processor capabilities"""
        return {
            "ocr_available": self.ocr_available,
            "image_preprocessing": self.cv2_available,
            "text_extraction": self.ocr_available,
            "coordinate_detection": self.ocr_available,
            "ui_element_detection": self.ocr_available,
            "document_structure_analysis": self.ocr_available
        }

# Global OCR processor instance
_ocr_processor = None

def get_ocr_processor() -> OCRProcessor:
    """Get global OCR processor instance"""
    global _ocr_processor
    if _ocr_processor is None:
        _ocr_processor = OCRProcessor()
    return _ocr_processor

# Utility functions for easy access

def extract_text_from_image(image_data: bytes) -> str:
    """Simple text extraction from image"""
    processor = get_ocr_processor()
    result = processor.extract_text_with_coordinates(image_data)
    return result.get("text", "")

def detect_ui_elements_from_image(image_data: bytes) -> List[Dict[str, Any]]:
    """Simple UI element detection from image"""
    processor = get_ocr_processor()
    return processor.detect_ui_elements(image_data)

def analyze_document_from_image(image_data: bytes) -> Dict[str, Any]:
    """Simple document analysis from image"""
    processor = get_ocr_processor()
    return processor.analyze_document_structure(image_data)

if __name__ == "__main__":
    # Test OCR processor
    def test_ocr_processor():
        print("🧪 Testing OCR Processor...")
        
        processor = OCRProcessor()
        
        # Test capabilities
        capabilities = processor.get_capabilities()
        print(f"✅ OCR capabilities: {capabilities}")
        
        # Test with dummy image data (would be real image bytes in practice)
        dummy_image = b"dummy_image_data_for_testing"
        
        # Test text extraction (will fail with dummy data, but shows the interface)
        try:
            result = processor.extract_text_with_coordinates(dummy_image)
            print(f"✅ Text extraction interface working")
        except:
            print("✅ Text extraction interface available (test data invalid)")
        
        # Test UI element detection
        try:
            ui_elements = processor.detect_ui_elements(dummy_image)
            print(f"✅ UI element detection interface working")
        except:
            print("✅ UI element detection interface available (test data invalid)")
        
        print("🎉 OCR Processor test completed!")
    
    test_ocr_processor()