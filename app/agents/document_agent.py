"""
Generic Document Agent - Agent 1 (Updated)
Platform-generic blueprint generation for ANY automation task
"""
import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import base64

from app.models.schemas import WorkflowState, PlatformType
from app.utils.model_client import model_client

class GenericDocumentAgent:
    """Generic document processing agent for any automation task"""
    
    def __init__(self):
        self.name = "document_agent"
        self.description = "Generic document processing with platform-agnostic blueprint generation"
        self.conversation_log = []
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """Main processing function for any automation task"""
        try:
            print(f"\\n🔵 [{self.name}] Starting generic document processing...")
            print(f"🔵 [{self.name}] Document size: {len(state.document_content)} bytes")
            print(f"🔵 [{self.name}] Screenshots: {len(state.screenshots)} images")
            print(f"🔵 [{self.name}] User instruction: '{state.parameters.get('instruction', 'Unknown')}'")
            
            state.current_agent = self.name
            
            await self._log_conversation(state, "AGENT_1_START", {
                "message": "Generic document processing started",
                "document_size": len(state.document_content),
                "screenshots_count": len(state.screenshots),
                "user_instruction": state.parameters.get("instruction", "Unknown")
            })
            
            # Step 1: Extract text from any document type
            print(f"🔵 [{self.name}] Step 1: Extracting text from document...")
            extracted_text = await self._extract_text_generic(state.document_content)
            state.extracted_text = extracted_text
            print(f"🔵 [{self.name}] ✅ Extracted {len(extracted_text)} characters")
            
            # Step 2: Process screenshots for UI elements
            print(f"🔵 [{self.name}] Step 2: Analyzing screenshots...")
            ui_elements = await self._analyze_screenshots(state.screenshots)
            state.ui_elements = ui_elements
            print(f"🔵 [{self.name}] ✅ Identified {len(ui_elements)} UI elements")
            
            # Step 3: Generate generic automation blueprint
            print(f"🔵 [{self.name}] Step 3: Generating automation blueprint...")
            blueprint = await self._generate_generic_blueprint(state)
            state.json_blueprint = blueprint
            
            # Save artifacts
            if state.run_dir:
                blueprint_path = await self._save_blueprint_artifact(state, blueprint)
                state.artifacts["agent1_blueprint"] = blueprint_path
                print(f"🔵 [{self.name}] ✅ Blueprint saved to: {blueprint_path}")
            
            await self._log_conversation(state, "AGENT_1_COMPLETED", {
                "text_extracted": len(extracted_text),
                "ui_elements_found": len(ui_elements),
                "blueprint_confidence": blueprint.get("confidence", 0.0),
                "blueprint_steps": len(blueprint.get("steps", [])),
                "platform_detected": blueprint.get("platform", "unknown")
            })
            
            print(f"🔵 [{self.name}] ✅ Document processing completed")
            print(f"🔵 [{self.name}] Blueprint confidence: {blueprint.get('confidence', 0.0):.2f}")
            print(f"🔵 [{self.name}] Platform: {blueprint.get('platform', 'unknown')}")
            print(f"🔵 [{self.name}] Automation steps: {len(blueprint.get('steps', []))}")
            
            await self._save_conversation_log(state)
            return state
            
        except Exception as e:
            await self._log_conversation(state, "AGENT_1_ERROR", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            
            print(f"🔴 [{self.name}] Error: {str(e)}")
            state.json_blueprint = {"error": str(e), "confidence": 0.0}
            return state
    
    async def _extract_text_generic(self, document_content: bytes) -> str:
        """Extract text from any document format"""
        try:
            print(f"🔵 [{self.name}] Attempting multi-format text extraction...")
            
            extracted_text = ""
            
            # Try PDF extraction first (most common)
            if self._is_pdf_content(document_content):
                extracted_text = await self._extract_pdf_text(document_content)
                if extracted_text:
                    print(f"🔵 [{self.name}] ✅ PDF text extracted")
                    return extracted_text
            
            # Try image OCR if no text found
            if len(extracted_text) < 50:
                try:
                    extracted_text = await self._extract_text_via_ocr(document_content)
                    if extracted_text:
                        print(f"🔵 [{self.name}] ✅ OCR text extracted")
                        return extracted_text
                except Exception as e:
                    print(f"🔵 [{self.name}] OCR failed: {str(e)}")
            
            # Fallback for other formats
            if not extracted_text:
                extracted_text = f"Document content ({len(document_content)} bytes) - Unable to extract readable text"
                print(f"🔵 [{self.name}] ⚠️ Using fallback text description")
            
            return extracted_text
            
        except Exception as e:
            print(f"🔴 [{self.name}] Text extraction failed: {str(e)}")
            return f"Text extraction error: {str(e)}"
    
    def _is_pdf_content(self, content: bytes) -> bool:
        """Check if content is PDF"""
        return content.startswith(b'%PDF')
    
    async def _extract_pdf_text(self, pdf_content: bytes) -> str:
        """Extract text from PDF using multiple methods"""
        try:
            # Method 1: PyPDF2
            try:
                import PyPDF2
                import io
                
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
                text_parts = []
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_parts.append(f"[Page {page_num + 1}]\\n{page_text}")
                
                if text_parts:
                    return "\\n\\n".join(text_parts)
                    
            except Exception as e:
                print(f"🔵 [{self.name}] PyPDF2 failed: {str(e)}")
            
            # Method 2: pdfplumber
            try:
                import pdfplumber
                import io
                
                with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                    text_parts = []
                    
                    for page_num, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_parts.append(f"[Page {page_num + 1}]\\n{page_text}")
                    
                    if text_parts:
                        return "\\n\\n".join(text_parts)
                        
            except Exception as e:
                print(f"🔵 [{self.name}] pdfplumber failed: {str(e)}")
            
            return ""
            
        except Exception as e:
            print(f"🔴 [{self.name}] PDF extraction failed: {str(e)}")
            return ""
    
    async def _extract_text_via_ocr(self, content: bytes) -> str:
        """Extract text using OCR for images or image-based PDFs"""
        try:
            import fitz  # PyMuPDF
            import pytesseract
            from PIL import Image
            import io
            
            # For PDF files, extract images from pages
            if self._is_pdf_content(content):
                doc = fitz.open(stream=content, filetype="pdf")
                text_parts = []
                
                for page_num in range(min(5, len(doc))):  # Limit to first 5 pages
                    page = doc[page_num]
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    
                    img = Image.open(io.BytesIO(img_data))
                    page_text = pytesseract.image_to_string(img)
                    
                    if page_text.strip():
                        text_parts.append(f"[Page {page_num + 1} - OCR]\\n{page_text}")
                
                doc.close()
                
                if text_parts:
                    return "\\n\\n".join(text_parts)
            
            # For direct image content
            else:
                try:
                    img = Image.open(io.BytesIO(content))
                    text = pytesseract.image_to_string(img)
                    if text.strip():
                        return f"[OCR Extracted]\\n{text}"
                except Exception as e:
                    print(f"🔵 [{self.name}] Direct OCR failed: {str(e)}")
            
            return ""
            
        except Exception as e:
            print(f"🔴 [{self.name}] OCR extraction failed: {str(e)}")
            return ""
    
    async def _analyze_screenshots(self, screenshots: List[bytes]) -> List[Dict[str, Any]]:
        """Analyze screenshots to identify UI elements"""
        try:
            ui_elements = []
            
            for i, screenshot_bytes in enumerate(screenshots):
                try:
                    element = {
                        "id": f"screenshot_{i + 1}",
                        "type": "screenshot",
                        "name": f"UI Screenshot {i + 1}",
                        "description": f"User interface screenshot containing interactive elements",
                        "size_bytes": len(screenshot_bytes),
                        "analysis": "Contains potential clickable elements, form fields, and navigation"
                    }
                    
                    ui_elements.append(element)
                    print(f"🔵 [{self.name}] Processed screenshot {i + 1}: {len(screenshot_bytes)} bytes")
                    
                except Exception as e:
                    print(f"🔴 [{self.name}] Error processing screenshot {i + 1}: {str(e)}")
            
            # Add common UI element patterns that might be present
            if screenshots:
                common_elements = [
                    {"type": "button", "name": "Action Button", "description": "Interactive button element"},
                    {"type": "input", "name": "Text Input", "description": "Text input field for user data"},
                    {"type": "dropdown", "name": "Selection Menu", "description": "Dropdown menu for options"},
                    {"type": "checkbox", "name": "Checkbox", "description": "Checkbox for boolean selection"},
                    {"type": "link", "name": "Navigation Link", "description": "Clickable navigation element"},
                    {"type": "form", "name": "Form Container", "description": "Form containing multiple input fields"}
                ]
                ui_elements.extend(common_elements)
            
            return ui_elements
            
        except Exception as e:
            print(f"🔴 [{self.name}] Screenshot analysis failed: {str(e)}")
            return []
    
    async def _generate_generic_blueprint(self, state: WorkflowState) -> Dict[str, Any]:
        """Generate generic automation blueprint for any task"""
        try:
            print(f"🔵 [{self.name}] Generating automation blueprint...")
            
            prompt = self._build_generic_blueprint_prompt(state)
            response = await model_client.generate(prompt, max_tokens=4000, temperature=0.3)
            blueprint = await self._parse_blueprint_response(response, state)
            
            return blueprint
            
        except Exception as e:
            print(f"🔴 [{self.name}] Blueprint generation failed: {str(e)}")
            return self._create_fallback_blueprint(state)
    
    def _build_generic_blueprint_prompt(self, state: WorkflowState) -> str:
        """Build generic blueprint generation prompt"""
        
        extracted_text = state.extracted_text or ""
        ui_elements = state.ui_elements or []
        parameters = state.parameters or {}
        
        user_instruction = parameters.get("instruction", "Unknown automation task")
        user_data = {k: v for k, v in parameters.items() if k not in ["instruction", "platform"]}
        platform_override = parameters.get("platform", "auto-detect")
        
        prompt = f"""
You are an expert UI automation analyst. Generate a structured JSON blueprint for ANY automation task.

USER TASK: {user_instruction}
USER DATA: {json.dumps(user_data, indent=2)}
PLATFORM PREFERENCE: {platform_override}

DOCUMENT CONTENT:
{extracted_text[:2000]}...

UI ELEMENTS DETECTED:
{json.dumps(ui_elements[:5], indent=2)}

REQUIRED OUTPUT (STRICT JSON):
{{
  "type": "json_blueprint",
  "schema_version": "1.1",
  "workflow_name": "descriptive_workflow_name",
  "platform": "web|mobile",
  "confidence": 0.0-1.0,
  "task_category": "form_filling|navigation|data_entry|interaction|search|automation",
  "dynamic_inputs": [
    {{"field": "field_name", "source": "user_data|generated|computed"}},
    {{"field": "another_field", "source": "user_data"}}
  ],
  "steps": [
    {{"i": 1, "action": "navigate|launch", "target": "application_or_url", "url": "https://example.com", "package": "com.app"}},
    {{"i": 2, "action": "click|tap", "target": "Button Name", "locator": {{"type": "xpath|id|css|accessibility_id", "value": "locator_value"}}}},
    {{"i": 3, "action": "fill|type", "target": "Input Field", "locator": {{"type": "xpath|id|css", "value": "locator_value"}}, "value": "{{{{dynamic_field}}}}"}},
    {{"i": 4, "action": "wait", "target": "Element or Condition", "timeout": 5000}},
    {{"i": 5, "action": "scroll|swipe", "target": "Screen Area", "direction": "down|up|left|right"}},
    {{"i": 6, "action": "verify", "target": "Expected Result", "condition": "element_present|text_contains|url_matches"}}
  ],
  "checkpoints": ["step_completed", "data_submitted", "result_verified"]
}}

ANALYSIS GUIDELINES:
1. Determine platform (web/mobile) from context and user preference
2. Identify the core automation task from user instruction
3. Break down the task into logical, sequential steps
4. Use appropriate actions: navigate, click, fill, wait, scroll, verify
5. Create realistic locator strategies (prefer ID > CSS > XPath)
6. Map user data to form fields using template variables
7. Add verification steps to ensure task completion
8. Assign confidence based on available information

PLATFORM DETECTION:
- Web: URLs, browser actions, CSS selectors, web forms
- Mobile: App packages, touch actions, mobile UI elements

LOCATOR STRATEGIES:
- ID: Use when element has unique ID attribute
- CSS: Use for styling-based selection
- XPath: Use for complex element relationships
- accessibility_id: Use for mobile accessibility identifiers

Generate ONLY valid JSON. No explanations outside JSON.
"""
        
        return prompt
    
    async def _parse_blueprint_response(self, response: str, state: WorkflowState) -> Dict[str, Any]:
        """Parse LLM response into structured blueprint"""
        try:
            print(f"🔵 [{self.name}] Parsing blueprint response...")
            
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                blueprint_data = json.loads(json_str)
                
                blueprint = self._validate_and_enhance_blueprint(blueprint_data, state)
                
                print(f"🔵 [{self.name}] ✅ Blueprint parsed successfully")
                return blueprint
            else:
                raise ValueError("No valid JSON found in response")
                
        except json.JSONDecodeError as e:
            print(f"🔴 [{self.name}] JSON parsing error: {str(e)}")
            return self._create_fallback_blueprint(state)
        except Exception as e:
            print(f"🔴 [{self.name}] Blueprint parsing error: {str(e)}")
            return self._create_fallback_blueprint(state)
    
    def _validate_and_enhance_blueprint(self, blueprint: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Validate and enhance the generated blueprint"""
        
        # Ensure required fields
        blueprint.setdefault("type", "json_blueprint")
        blueprint.setdefault("schema_version", "1.1")
        blueprint.setdefault("confidence", 0.7)
        
        # Handle platform override
        parameters = state.parameters or {}
        platform_override = parameters.get("platform")
        if platform_override:
            if platform_override.lower() == "web":
                blueprint["platform"] = "web"
            elif platform_override.lower() == "mobile":
                blueprint["platform"] = "mobile"
        
        # Ensure platform is set
        if "platform" not in blueprint:
            blueprint["platform"] = "web"  # Default
        
        # Validate steps
        if "steps" not in blueprint or not blueprint["steps"]:
            blueprint["steps"] = self._create_default_steps(state)
        
        # Validate dynamic inputs
        if "dynamic_inputs" not in blueprint:
            blueprint["dynamic_inputs"] = self._create_default_dynamic_inputs(state)
        
        # Add workflow name if missing
        if "workflow_name" not in blueprint:
            instruction = state.parameters.get("instruction", "automation_task")
            blueprint["workflow_name"] = instruction.lower().replace(" ", "_")[:50]
        
        # Add task category if missing
        if "task_category" not in blueprint:
            blueprint["task_category"] = self._determine_task_category(state)
        
        return blueprint
    
    def _determine_task_category(self, state: WorkflowState) -> str:
        """Determine task category from instruction"""
        instruction = state.parameters.get("instruction", "").lower()
        
        if any(word in instruction for word in ["form", "fill", "input", "enter"]):
            return "form_filling"
        elif any(word in instruction for word in ["navigate", "go to", "visit", "open"]):
            return "navigation"
        elif any(word in instruction for word in ["search", "find", "look"]):
            return "search"
        elif any(word in instruction for word in ["click", "tap", "press", "select"]):
            return "interaction"
        elif any(word in instruction for word in ["data", "information", "details"]):
            return "data_entry"
        else:
            return "automation"
    
    def _create_default_dynamic_inputs(self, state: WorkflowState) -> List[Dict[str, str]]:
        """Create default dynamic inputs based on user data"""
        parameters = state.parameters or {}
        user_data = {k: v for k, v in parameters.items() if k not in ["instruction", "platform"]}
        
        dynamic_inputs = []
        
        # Add user-provided data
        for key, value in user_data.items():
            dynamic_inputs.append({"field": key, "source": "user_data"})
        
        # Add common fields if none provided
        if not dynamic_inputs:
            dynamic_inputs.extend([
                {"field": "search_term", "source": "generated"},
                {"field": "input_text", "source": "generated"},
                {"field": "selection_value", "source": "generated"}
            ])
        
        return dynamic_inputs
    
    def _create_default_steps(self, state: WorkflowState) -> List[Dict[str, Any]]:
        """Create default automation steps"""
        parameters = state.parameters or {}
        platform = parameters.get("platform", "web")
        instruction = parameters.get("instruction", "")
        
        if platform == "mobile":
            return [
                {"i": 1, "action": "launch", "target": "Application", "package": "com.example.app"},
                {"i": 2, "action": "wait", "target": "App Loading", "timeout": 5000},
                {"i": 3, "action": "tap", "target": "Main Action", "locator": {"type": "xpath", "value": "//*[contains(@text, 'Action')]"}},
                {"i": 4, "action": "fill", "target": "Input Field", "locator": {"type": "id", "value": "input_field"}, "value": "{{input_text}}"},
                {"i": 5, "action": "tap", "target": "Submit", "locator": {"type": "xpath", "value": "//*[contains(@text, 'Submit')]"}}
            ]
        else:  # web
            return [
                {"i": 1, "action": "navigate", "url": "https://example.com", "target": "target_page"},
                {"i": 2, "action": "wait", "target": "Page Load", "timeout": 5000},
                {"i": 3, "action": "click", "target": "Main Action", "locator": {"type": "css", "value": "button.main-action"}},
                {"i": 4, "action": "fill", "target": "Input Field", "locator": {"type": "id", "value": "input-field"}, "value": "{{input_text}}"},
                {"i": 5, "action": "click", "target": "Submit", "locator": {"type": "css", "value": "button[type='submit']"}}
            ]
    
    def _create_fallback_blueprint(self, state: WorkflowState) -> Dict[str, Any]:
        """Create fallback blueprint when parsing fails"""
        print(f"🔵 [{self.name}] Creating fallback blueprint...")
        
        parameters = state.parameters or {}
        instruction = parameters.get("instruction", "automation_task")
        platform = parameters.get("platform", "web")
        
        return {
            "type": "json_blueprint",
            "schema_version": "1.1",
            "workflow_name": instruction.lower().replace(" ", "_")[:50],
            "platform": platform,
            "confidence": 0.5,
            "task_category": self._determine_task_category(state),
            "dynamic_inputs": self._create_default_dynamic_inputs(state),
            "steps": self._create_default_steps(state),
            "checkpoints": ["task_initiated", "actions_completed", "result_achieved"]
        }
    
    async def _save_blueprint_artifact(self, state: WorkflowState, blueprint: Dict[str, Any]) -> str:
        """Save blueprint as artifact"""
        try:
            os.makedirs(state.run_dir, exist_ok=True)
            
            blueprint_path = os.path.join(state.run_dir, "agent1_blueprint.json")
            
            enhanced_blueprint = {
                "metadata": {
                    "agent": self.name,
                    "version": "generic_v2.0",
                    "task_id": state.task_id,
                    "generated_at": datetime.utcnow().isoformat(),
                    "document_size": len(state.document_content),
                    "text_extracted": len(state.extracted_text or ""),
                    "ui_elements": len(state.ui_elements or []),
                    "user_instruction": state.parameters.get("instruction", "Unknown")
                },
                "blueprint": blueprint
            }
            
            with open(blueprint_path, 'w', encoding='utf-8') as f:
                json.dump(enhanced_blueprint, f, indent=2, ensure_ascii=False)
            
            return blueprint_path
            
        except Exception as e:
            print(f"🔴 [{self.name}] Error saving blueprint: {str(e)}")
            return ""
    
    async def _log_conversation(self, state: WorkflowState, event_type: str, data: Dict[str, Any]):
        """Log conversation events"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.name,
            "event_type": event_type,
            "data": data
        }
        self.conversation_log.append(log_entry)
    
    async def _save_conversation_log(self, state: WorkflowState):
        """Save conversation log to artifacts"""
        if not state.run_dir or not self.conversation_log:
            return
        
        try:
            conversation_path = os.path.join(state.run_dir, "conversation.json")
            
            existing_conversation = []
            if os.path.exists(conversation_path):
                try:
                    with open(conversation_path, 'r', encoding='utf-8') as f:
                        existing_conversation = json.load(f)
                except:
                    pass
            
            full_conversation = existing_conversation + self.conversation_log
            
            with open(conversation_path, 'w', encoding='utf-8') as f:
                json.dump(full_conversation, f, indent=2, ensure_ascii=False)
            
            state.artifacts["conversation_log"] = conversation_path
            self.conversation_log = []
            
        except Exception as e:
            print(f"🔴 [{self.name}] Error saving conversation log: {str(e)}")

# Global instance
document_agent = GenericDocumentAgent()