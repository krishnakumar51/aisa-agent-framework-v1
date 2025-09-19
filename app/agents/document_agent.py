"""
Document processing agent - Agent 1
Parses PDF content and screenshots to create UI blueprint
"""
import asyncio
import json
from typing import Dict, Any, List
from app.models.schemas import WorkflowState, AutomationBlueprint, PlatformType
from app.utils.ocr_utils import ocr_processor
from app.utils.ui_detection import ui_detector
from app.utils.model_client import model_client

class DocumentAgent:
    """Agent responsible for document processing and UI analysis"""
    
    def __init__(self):
        self.name = "document_agent"
        self.description = "Processes PDF documents and screenshots to extract UI blueprints"
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """Main processing function for document agent"""
        try:
            print(f"[{self.name}] Starting document processing...")
            state.current_agent = self.name
            
            # Step 1: Extract text from PDF
            pdf_text = await self._extract_pdf_text(state.document_content)
            state.extracted_text = pdf_text
            
            # Step 2: Process screenshots with OCR
            screenshot_data = await self._process_screenshots(state.screenshots)
            
            # Step 3: Detect UI elements
            ui_elements = await self._detect_ui_elements(state.screenshots, screenshot_data)
            state.ui_elements = ui_elements
            
            # Step 4: Create automation blueprint using LLM
            blueprint = await self._create_blueprint(pdf_text, ui_elements, screenshot_data)
            state.json_blueprint = blueprint
            
            print(f"[{self.name}] Document processing completed successfully")
            return state
            
        except Exception as e:
            print(f"[{self.name}] Error: {str(e)}")
            state.json_blueprint = {"error": str(e)}
            return state
    
    async def _extract_pdf_text(self, pdf_bytes: bytes) -> str:
        """Extract text content from PDF"""
        if not pdf_bytes:
            return ""
        
        return await asyncio.to_thread(ocr_processor.extract_text_from_pdf, pdf_bytes)
    
    async def _process_screenshots(self, screenshots: List[bytes]) -> List[Dict[str, Any]]:
        """Process screenshots with OCR"""
        screenshot_data = []
        
        for i, screenshot in enumerate(screenshots):
            try:
                # Extract text using OCR
                ocr_text = await asyncio.to_thread(
                    ocr_processor.extract_text_from_image, screenshot
                )
                
                # Get image info
                image_info = await asyncio.to_thread(
                    ocr_processor.get_image_info, screenshot
                )
                
                screenshot_data.append({
                    "index": i,
                    "ocr_text": ocr_text,
                    "image_info": image_info,
                    "size_bytes": len(screenshot)
                })
                
            except Exception as e:
                print(f"[{self.name}] Screenshot {i} processing failed: {str(e)}")
                screenshot_data.append({
                    "index": i,
                    "error": str(e)
                })
        
        return screenshot_data
    
    async def _detect_ui_elements(self, screenshots: List[bytes], 
                                 screenshot_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect UI elements from screenshots"""
        all_elements = []
        
        for i, (screenshot, data) in enumerate(zip(screenshots, screenshot_data)):
            if "error" in data:
                continue
            
            try:
                elements = await asyncio.to_thread(
                    ui_detector.detect_ui_elements,
                    screenshot,
                    data.get("ocr_text", "")
                )
                
                # Add screenshot reference to each element
                for element in elements:
                    element["screenshot_index"] = i
                
                all_elements.extend(elements)
                
            except Exception as e:
                print(f"[{self.name}] UI detection failed for screenshot {i}: {str(e)}")
        
        return all_elements
    
    async def _create_blueprint(self, pdf_text: str, ui_elements: List[Dict[str, Any]], 
                              screenshot_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create automation blueprint using LLM analysis"""
        try:
            # Prepare context for LLM
            context = self._prepare_llm_context(pdf_text, ui_elements, screenshot_data)
            
            # Generate blueprint using LLM
            prompt = self._create_blueprint_prompt(context)
            response = await model_client.generate(prompt)
            
            # Parse LLM response into structured blueprint
            blueprint = self._parse_blueprint_response(response, ui_elements)
            
            return blueprint
            
        except Exception as e:
            print(f"[{self.name}] Blueprint creation failed: {str(e)}")
            return {
                "error": str(e),
                "fallback_blueprint": self._create_fallback_blueprint(ui_elements)
            }
    
    def _prepare_llm_context(self, pdf_text: str, ui_elements: List[Dict[str, Any]], 
                           screenshot_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare context for LLM analysis"""
        return {
            "pdf_text": pdf_text[:2000],  # Truncate for token limits
            "ui_elements_count": len(ui_elements),
            "ui_elements": ui_elements[:10],  # Top 10 elements
            "screenshot_count": len(screenshot_data),
            "ocr_texts": [data.get("ocr_text", "")[:200] for data in screenshot_data]
        }
    
    def _create_blueprint_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for blueprint generation"""
        return f"""
Analyze the following mobile/web automation scenario and create a structured blueprint.

PDF INSTRUCTIONS:
{context['pdf_text']}

DETECTED UI ELEMENTS ({context['ui_elements_count']} total):
{json.dumps(context['ui_elements'], indent=2)}

OCR TEXTS FROM SCREENSHOTS:
{json.dumps(context['ocr_texts'], indent=2)}

Create a JSON blueprint with the following structure:
{{
    "title": "Brief title describing the automation",
    "platform": "mobile" or "web",
    "total_steps": number,
    "steps": [
        {{
            "step_number": 1,
            "action": "click|input|wait|navigate",
            "description": "What to do in this step",
            "target_element": "element selector or description",
            "input_data": "data to input (if applicable)",
            "expected_result": "what should happen"
        }}
    ],
    "confidence": 0.0-1.0
}}

Focus on creating actionable steps that match the PDF instructions with detected UI elements.
"""
    
    def _parse_blueprint_response(self, response: str, ui_elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse LLM response into structured blueprint"""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                blueprint = json.loads(json_str)
                
                # Enhance blueprint with UI element mappings
                blueprint["ui_elements"] = ui_elements
                blueprint["total_elements"] = len(ui_elements)
                
                return blueprint
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            print(f"[{self.name}] Blueprint parsing failed: {str(e)}")
            return self._create_fallback_blueprint(ui_elements)
    
    def _create_fallback_blueprint(self, ui_elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a basic fallback blueprint when LLM fails"""
        steps = []
        
        # Create basic steps from UI elements
        for i, element in enumerate(ui_elements[:5]):  # Max 5 steps
            if element["type"] == "button":
                steps.append({
                    "step_number": i + 1,
                    "action": "click",
                    "description": f"Click {element['text']}",
                    "target_element": element["selector"],
                    "expected_result": "Element clicked"
                })
            elif element["type"] == "input":
                steps.append({
                    "step_number": i + 1,
                    "action": "input",
                    "description": f"Fill {element['text']}",
                    "target_element": element["selector"],
                    "input_data": "test_value",
                    "expected_result": "Field filled"
                })
        
        return {
            "title": "Basic Automation Workflow",
            "platform": "mobile",  # Default assumption
            "total_steps": len(steps),
            "steps": steps,
            "ui_elements": ui_elements,
            "confidence": 0.3,
            "fallback": True
        }

# Global document agent instance
document_agent = DocumentAgent()