"""
UI element detection utilities
"""
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import io

class UIDetector:
    """UI element detection and analysis"""
    
    def __init__(self):
        """Initialize UI detector"""
        pass
    
    def detect_ui_elements(self, screenshot_bytes: bytes, ocr_text: str) -> List[Dict[str, Any]]:
        """Detect UI elements from screenshot and OCR text"""
        elements = []
        
        try:
            # Get image dimensions
            image = Image.open(io.BytesIO(screenshot_bytes))
            width, height = image.size
            
            # Parse OCR text for common UI patterns
            ui_patterns = self._extract_ui_patterns(ocr_text)
            
            # Add detected elements with estimated coordinates
            for pattern in ui_patterns:
                element = {
                    "type": pattern["type"],
                    "text": pattern["text"],
                    "coordinates": self._estimate_coordinates(pattern, width, height),
                    "attributes": pattern.get("attributes", {}),
                    "selector": self._generate_selector(pattern)
                }
                elements.append(element)
            
            return elements
        except Exception as e:
            print(f"UI detection error: {str(e)}")
            return []
    
    def _extract_ui_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Extract UI patterns from OCR text"""
        patterns = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Button patterns
            if self._is_button(line):
                patterns.append({
                    "type": "button",
                    "text": line,
                    "line_number": i,
                    "attributes": {"clickable": True}
                })
            
            # Input field patterns
            elif self._is_input_field(line):
                patterns.append({
                    "type": "input",
                    "text": line,
                    "line_number": i,
                    "attributes": {"editable": True}
                })
            
            # Link patterns
            elif self._is_link(line):
                patterns.append({
                    "type": "link",
                    "text": line,
                    "line_number": i,
                    "attributes": {"clickable": True}
                })
            
            # Text patterns
            else:
                patterns.append({
                    "type": "text",
                    "text": line,
                    "line_number": i,
                    "attributes": {}
                })
        
        return patterns
    
    def _is_button(self, text: str) -> bool:
        """Check if text represents a button"""
        button_keywords = [
            "siguiente", "next", "continuar", "continue", "crear", "create",
            "enviar", "send", "submit", "ok", "aceptar", "accept", "confirmar",
            "confirm", "guardar", "save", "cancelar", "cancel", "salir", "exit",
            "login", "register", "sign in", "sign up", "agregar", "add"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in button_keywords)
    
    def _is_input_field(self, text: str) -> bool:
        """Check if text represents an input field"""
        input_patterns = [
            r".*@.*\.(com|org|net)",  # Email patterns
            r"\d{2,4}[/-]\d{2,4}[/-]\d{2,4}",  # Date patterns
            r"password|contraseña",
            r"username|usuario|email|correo",
            r"nombre|name|apellido|surname",
            r"telefono|phone|direccion|address"
        ]
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in input_patterns)
    
    def _is_link(self, text: str) -> bool:
        """Check if text represents a link"""
        link_patterns = [
            r"https?://",
            r"www\.",
            r"\.com|\.org|\.net",
            r"términos|terms|política|policy|ayuda|help"
        ]
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in link_patterns)
    
    def _estimate_coordinates(self, pattern: Dict[str, Any], width: int, height: int) -> Dict[str, int]:
        """Estimate coordinates based on line number and text position"""
        line_number = pattern.get("line_number", 0)
        text_length = len(pattern.get("text", ""))
        
        # Simple estimation based on line position
        y = int(height * (line_number + 1) / 20)  # Rough line height estimation
        x = max(50, int(width / 2 - text_length * 5))  # Center-ish based on text length
        
        return {
            "x": x,
            "y": y,
            "width": min(text_length * 10, width - x - 50),
            "height": 40  # Standard UI element height
        }
    
    def _generate_selector(self, pattern: Dict[str, Any]) -> str:
        """Generate a CSS/XPath selector for the UI element"""
        element_type = pattern["type"]
        text = pattern["text"]
        
        if element_type == "button":
            return f"//button[contains(text(), '{text[:20]}')]"
        elif element_type == "input":
            if "@" in text:
                return "//input[@type='email']"
            elif "password" in text.lower() or "contraseña" in text.lower():
                return "//input[@type='password']"
            else:
                return f"//input[contains(@placeholder, '{text[:10]}')]"
        elif element_type == "link":
            return f"//a[contains(text(), '{text[:20]}')]"
        else:
            return f"//*[contains(text(), '{text[:20]}')]"
    
    def create_blueprint_from_elements(self, elements: List[Dict[str, Any]], 
                                     pdf_text: str) -> Dict[str, Any]:
        """Create automation blueprint from detected elements and PDF instructions"""
        try:
            # Parse PDF text for step instructions
            steps = self._parse_steps_from_text(pdf_text)
            
            # Match elements to steps
            matched_steps = []
            for i, step in enumerate(steps):
                matching_elements = self._find_matching_elements(step, elements)
                matched_steps.append({
                    "step_number": i + 1,
                    "action": step["action"],
                    "target": matching_elements[0] if matching_elements else None,
                    "input_data": step.get("input_data"),
                    "expected_result": step.get("expected_result"),
                    "description": step["description"]
                })
            
            blueprint = {
                "title": "Automated Workflow",
                "platform": "mobile" if self._is_mobile_workflow(elements) else "web",
                "steps": matched_steps,
                "ui_elements": elements,
                "metadata": {
                    "total_steps": len(matched_steps),
                    "total_elements": len(elements),
                    "confidence": self._calculate_confidence(matched_steps)
                }
            }
            
            return blueprint
        except Exception as e:
            print(f"Blueprint creation error: {str(e)}")
            return {"error": str(e)}
    
    def _parse_steps_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse automation steps from PDF text"""
        steps = []
        lines = text.split('\n')
        
        current_step = None
        step_counter = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for step indicators
            if re.match(r'^\d+\.', line) or any(word in line.lower() for word in ['step', 'paso', 'action']):
                if current_step:
                    steps.append(current_step)
                
                current_step = {
                    "step_number": step_counter,
                    "description": line,
                    "action": self._extract_action(line),
                    "input_data": self._extract_input_data(line),
                    "expected_result": None
                }
                step_counter += 1
            elif current_step:
                # Add additional details to current step
                current_step["description"] += " " + line
                if not current_step["action"]:
                    current_step["action"] = self._extract_action(line)
                if not current_step["input_data"]:
                    current_step["input_data"] = self._extract_input_data(line)
        
        if current_step:
            steps.append(current_step)
        
        return steps
    
    def _extract_action(self, text: str) -> str:
        """Extract action type from step text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['click', 'tap', 'press', 'select']):
            return "click"
        elif any(word in text_lower for word in ['enter', 'type', 'input', 'write']):
            return "input"
        elif any(word in text_lower for word in ['wait', 'pause', 'delay']):
            return "wait"
        elif any(word in text_lower for word in ['scroll', 'swipe']):
            return "scroll"
        else:
            return "unknown"
    
    def _extract_input_data(self, text: str) -> Optional[str]:
        """Extract input data from step text"""
        # Look for quoted strings or common input patterns
        import re
        
        # Find quoted text
        quoted = re.findall(r'"([^"]*)"', text)
        if quoted:
            return quoted[0]
        
        # Find email patterns
        email = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email:
            return email[0]
        
        return None
    
    def _find_matching_elements(self, step: Dict[str, Any], 
                              elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find UI elements that match a given step"""
        matches = []
        step_text = step["description"].lower()
        action = step["action"]
        
        for element in elements:
            element_text = element["text"].lower()
            element_type = element["type"]
            
            # Score matching based on text similarity and action compatibility
            score = 0
            
            # Text similarity
            common_words = set(step_text.split()) & set(element_text.split())
            if common_words:
                score += len(common_words) * 10
            
            # Action compatibility
            if action == "click" and element_type in ["button", "link"]:
                score += 20
            elif action == "input" and element_type == "input":
                score += 20
            
            if score > 0:
                matches.append({"element": element, "score": score})
        
        # Sort by score and return elements
        matches.sort(key=lambda x: x["score"], reverse=True)
        return [match["element"] for match in matches]
    
    def _is_mobile_workflow(self, elements: List[Dict[str, Any]]) -> bool:
        """Determine if workflow is for mobile based on UI elements"""
        mobile_indicators = ["tap", "swipe", "scroll", "android", "ios"]
        text_content = " ".join([elem.get("text", "") for elem in elements]).lower()
        
        return any(indicator in text_content for indicator in mobile_indicators)
    
    def _calculate_confidence(self, steps: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for the blueprint"""
        if not steps:
            return 0.0
        
        matched_steps = sum(1 for step in steps if step.get("target"))
        return matched_steps / len(steps)

# Global UI detector instance
ui_detector = UIDetector()