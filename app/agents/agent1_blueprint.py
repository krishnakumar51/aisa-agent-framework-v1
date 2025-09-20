"""
Updated Agent 1: Blueprint Generation with Proper Folder Structure
Creates blueprint.json in agent1/ folder and initializes SQLite database
"""
import asyncio
import json
import logging
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import PyPDF2
import pytesseract
from PIL import Image
import io

# Import the updated database manager
from app.database.database_manager import get_testing_db

logger = logging.getLogger(__name__)

class UpdatedAgent1_BlueprintGenerator:
    """Agent 1: Blueprint Generation with Testing Environment Structure"""
    
    def __init__(self):
        self.agent_name = "agent1"
        self.db_manager = None
    
    async def initialize(self):
        """Initialize database connection"""
        self.db_manager = await get_testing_db()
        logger.info("🔵 Agent 1: Blueprint generator initialized with updated structure")
    
    async def process_and_generate_blueprint(self, document_content: bytes, screenshots: List[bytes],
                                           instruction: str, platform: str, 
                                           additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process documents and generate blueprint with proper folder structure
        
        Args:
            document_content: PDF or document bytes
            screenshots: List of screenshot bytes  
            instruction: User instruction
            platform: Target platform
            additional_data: Additional user data
            
        Returns:
            Processing results with seq_id and folder structure
        """
        start_time = time.time()
        
        logger.info(f"🔵 [Agent1] Starting blueprint generation")
        logger.info(f"🔵 [Agent1] Document size: {len(document_content)} bytes")
        logger.info(f"🔵 [Agent1] Screenshots: {len(screenshots)} images")
        logger.info(f"🔵 [Agent1] Instruction: {instruction}")
        logger.info(f"🔵 [Agent1] Platform: {platform}")
        
        try:
            # Create task in database and get sequential ID
            seq_id = await self.db_manager.create_task(
                instruction=instruction,
                platform=platform,
                additional_data=additional_data or {}
            )
            
            # Create folder structure
            base_path = Path(f"generated_code/{seq_id}")
            agent1_path = base_path / "agent1"
            agent1_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"🔵 [Agent1] Created task {seq_id}")
            logger.info(f"🔵 [Agent1] Base path: {base_path}")
            
            # Update task status
            await self.db_manager.update_task_status(seq_id, "processing", "agent1")
            
            # Step 1: Extract text content
            text_content = await self._extract_text_content(document_content)
            logger.info(f"🔵 [Agent1] ✅ Extracted {len(text_content)} characters")
            
            # Step 2: Process screenshots
            ui_elements = await self._process_screenshots(screenshots, agent1_path)
            logger.info(f"🔵 [Agent1] ✅ Identified {len(ui_elements)} UI elements")
            
            # Step 3: Generate automation blueprint
            blueprint = await self._generate_automation_blueprint(
                seq_id, instruction, platform, text_content, ui_elements
            )
            
            # Step 4: Save blueprint to agent1/blueprint.json
            blueprint_path = agent1_path / "blueprint.json"
            with open(blueprint_path, 'w', encoding='utf-8') as f:
                json.dump(blueprint, f, indent=2, ensure_ascii=False)
            
            # Save file metadata to database
            await self.db_manager.save_generated_file(
                seq_id=seq_id,
                agent_name=self.agent_name,
                file_name="blueprint.json",
                file_path=str(blueprint_path),
                file_type="blueprint",
                version=1
            )
            
            # Step 5: Create workflow steps in database
            await self._create_workflow_steps_in_db(seq_id, blueprint.get('steps', []))
            
            # Step 6: Initialize SQLite database in task folder
            task_db_path = base_path / "sqlite_db.sqlite"
            await self._initialize_task_database(task_db_path, seq_id)
            
            # Update task progress
            await self.db_manager.update_task_progress(seq_id, blueprint_generated=True)
            await self.db_manager.update_task_status(seq_id, "blueprint_completed", "agent1")
            
            processing_time = time.time() - start_time
            confidence = self._calculate_confidence(text_content, ui_elements, blueprint)
            
            logger.info(f"🔵 [Agent1] ✅ Blueprint saved to: {blueprint_path}")
            logger.info(f"🔵 [Agent1] ✅ Task database initialized: {task_db_path}")
            logger.info(f"🔵 [Agent1] ✅ Blueprint generation completed")
            logger.info(f"🔵 [Agent1] Blueprint confidence: {confidence:.2f}")
            logger.info(f"🔵 [Agent1] Automation steps: {len(blueprint.get('steps', []))}")
            
            return {
                "success": True,
                "seq_id": seq_id,
                "agent": self.agent_name,
                "base_path": str(base_path),
                "agent1_path": str(agent1_path),
                "blueprint_path": str(blueprint_path),
                "sqlite_db_path": str(task_db_path),
                "text_extracted": len(text_content),
                "ui_elements": len(ui_elements),
                "blueprint_confidence": confidence,
                "automation_steps": len(blueprint.get('steps', [])),
                "platform": platform,
                "processing_time": processing_time,
                "blueprint": blueprint,
                "folder_structure": {
                    "base": str(base_path),
                    "agent1": str(agent1_path),
                    "agent2": str(base_path / "agent2"),
                    "agent3_testing": str(base_path / "agent3" / "testing"),
                    "agent4": str(base_path / "agent4")
                }
            }
            
        except Exception as e:
            error_msg = f"Blueprint generation failed: {str(e)}"
            logger.error(f"🔴 [Agent1] {error_msg}")
            
            # Update task status to failed if seq_id exists
            if 'seq_id' in locals():
                await self.db_manager.update_task_status(seq_id, "failed", "agent1")
            
            return {
                "success": False,
                "error": error_msg,
                "agent": self.agent_name,
                "processing_time": time.time() - start_time
            }
    
    async def _extract_text_content(self, document_content: bytes) -> str:
        """Extract text from document content"""
        try:
            # Try PDF extraction first
            if document_content.startswith(b'%PDF'):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(document_content))
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\\n"
                
                if text_content.strip():
                    return text_content.strip()
            
            # Try as image with OCR
            try:
                image = Image.open(io.BytesIO(document_content))
                text_content = pytesseract.image_to_string(image)
                if text_content.strip():
                    return text_content.strip()
            except:
                pass
            
            # Try as text
            try:
                text_content = document_content.decode('utf-8', errors='ignore')
                if text_content.strip():
                    return text_content.strip()
            except:
                pass
            
            return f"Document content for automation task (Size: {len(document_content)} bytes)"
            
        except Exception as e:
            logger.warning(f"🔴 [Agent1] Text extraction failed: {str(e)}")
            return f"Text extraction failed, but document received ({len(document_content)} bytes)"
    
    async def _process_screenshots(self, screenshots: List[bytes], agent1_path: Path) -> List[Dict[str, Any]]:
        """Process screenshots and identify UI elements"""
        ui_elements = []
        
        # Create screenshots folder in agent1
        screenshots_dir = agent1_path / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        
        for i, screenshot_bytes in enumerate(screenshots):
            try:
                # Save screenshot
                screenshot_path = screenshots_dir / f"screenshot_{i+1}.png"
                with open(screenshot_path, 'wb') as f:
                    f.write(screenshot_bytes)
                
                # Perform OCR
                image = Image.open(io.BytesIO(screenshot_bytes))
                ocr_text = pytesseract.image_to_string(image)
                
                if ocr_text.strip():
                    # Identify UI elements from OCR text
                    elements = self._identify_ui_elements(ocr_text, f"screenshot_{i+1}")
                    ui_elements.extend(elements)
                
                logger.info(f"🔵 [Agent1] Processed screenshot {i+1}: {len(ocr_text)} chars OCR text")
                
            except Exception as e:
                logger.warning(f"🔴 [Agent1] Screenshot {i+1} processing failed: {str(e)}")
        
        return ui_elements
    
    def _identify_ui_elements(self, ocr_text: str, source: str) -> List[Dict[str, Any]]:
        """Identify UI elements from OCR text"""
        elements = []
        lines = ocr_text.split('\\n')
        
        # UI element keywords
        ui_keywords = {
            'button': ['button', 'click', 'submit', 'cancel', 'ok', 'yes', 'no', 'save'],
            'input': ['input', 'text', 'field', 'name', 'email', 'password', 'enter'],
            'select': ['dropdown', 'select', 'option', 'choose', 'pick'],
            'checkbox': ['checkbox', 'radio', 'check', 'tick'],
            'navigation': ['menu', 'nav', 'home', 'back', 'next', 'previous'],
            'form': ['form', 'login', 'register', 'signup', 'create', 'account']
        }
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if line_lower and len(line_lower) > 2:
                # Check for UI element type
                element_type = "text"
                for ui_type, keywords in ui_keywords.items():
                    if any(keyword in line_lower for keyword in keywords):
                        element_type = ui_type
                        break
                
                elements.append({
                    "id": f"element_{len(elements)+1}",
                    "type": element_type,
                    "text": line.strip(),
                    "source": source,
                    "line_number": i + 1,
                    "confidence": self._calculate_element_confidence(line_lower, element_type)
                })
        
        return elements
    
    def _calculate_element_confidence(self, text: str, element_type: str) -> float:
        """Calculate confidence for UI element identification"""
        base_confidence = 0.5
        
        # Boost confidence based on specific keywords
        if element_type == "button" and any(word in text for word in ['click', 'submit', 'button']):
            base_confidence += 0.3
        elif element_type == "input" and any(word in text for word in ['input', 'field', 'enter']):
            base_confidence += 0.3
        elif element_type == "form" and any(word in text for word in ['form', 'login', 'register']):
            base_confidence += 0.2
        
        return min(base_confidence, 1.0)
    
    async def _generate_automation_blueprint(self, seq_id: int, instruction: str, platform: str,
                                           text_content: str, ui_elements: List[Dict]) -> Dict[str, Any]:
        """Generate automation blueprint based on analysis"""
        
        # Categorize task
        task_category = self._categorize_task(instruction)
        
        # Generate automation steps
        steps = self._generate_automation_steps(task_category, instruction, ui_elements, platform)
        
        blueprint = {
            "seq_id": seq_id,
            "instruction": instruction,
            "task_category": task_category,
            "platform": platform,
            "document_analysis": {
                "text_length": len(text_content),
                "ui_elements_found": len(ui_elements),
                "text_preview": text_content[:200] + "..." if len(text_content) > 200 else text_content
            },
            "ui_elements": ui_elements,
            "steps": steps,
            "estimated_duration": len(steps) * 15,  # 15 seconds per step
            "complexity": self._assess_complexity(steps),
            "requirements": self._generate_requirements(platform, task_category),
            "generated_at": datetime.utcnow().isoformat(),
            "agent": self.agent_name,
            "folder_structure": {
                "agent2_folder": f"generated_code/{seq_id}/agent2/",
                "agent3_testing": f"generated_code/{seq_id}/agent3/testing/",
                "agent4_folder": f"generated_code/{seq_id}/agent4/"
            }
        }
        
        return blueprint
    
    def _categorize_task(self, instruction: str) -> str:
        """Categorize automation task"""
        instruction_lower = instruction.lower()
        
        if any(keyword in instruction_lower for keyword in ["account", "register", "signup", "sign up"]):
            return "account_creation"
        elif any(keyword in instruction_lower for keyword in ["form", "fill", "submit", "input"]):
            return "form_filling"
        elif any(keyword in instruction_lower for keyword in ["login", "signin", "sign in"]):
            return "authentication"
        elif any(keyword in instruction_lower for keyword in ["search", "find", "lookup"]):
            return "search"
        elif any(keyword in instruction_lower for keyword in ["navigate", "goto", "visit"]):
            return "navigation"
        else:
            return "automation"
    
    def _generate_automation_steps(self, task_category: str, instruction: str, 
                                  ui_elements: List[Dict], platform: str) -> List[Dict[str, Any]]:
        """Generate automation steps based on task analysis"""
        
        steps = []
        
        if task_category == "account_creation":
            steps = [
                {
                    "step_order": 1,
                    "step_name": "Initialize automation environment",
                    "action_type": "setup",
                    "description": f"Setup {platform} automation environment",
                    "expected_result": "Environment ready for automation",
                    "validation_method": "system_check"
                },
                {
                    "step_order": 2,
                    "step_name": "Navigate to registration page",
                    "action_type": "navigate",
                    "description": "Open registration or signup page",
                    "expected_result": "Registration page loaded",
                    "validation_method": "page_title_check"
                },
                {
                    "step_order": 3,
                    "step_name": "Enter user name",
                    "action_type": "input",
                    "description": "Fill in user name or full name field",
                    "expected_result": "Name entered successfully",
                    "validation_method": "field_value_check"
                },
                {
                    "step_order": 4,
                    "step_name": "Enter date of birth",
                    "action_type": "input", 
                    "description": "Fill in date of birth field",
                    "expected_result": "DOB entered successfully",
                    "validation_method": "field_value_check"
                },
                {
                    "step_order": 5,
                    "step_name": "Submit registration form",
                    "action_type": "click",
                    "description": "Click submit or create account button",
                    "expected_result": "Account created successfully",
                    "validation_method": "success_message_check"
                },
                {
                    "step_order": 6,
                    "step_name": "Validate account creation",
                    "action_type": "validate",
                    "description": "Verify account was created successfully",
                    "expected_result": "Account creation confirmed",
                    "validation_method": "ocr_validation"
                }
            ]
        else:
            # Generic automation steps
            steps = [
                {
                    "step_order": 1,
                    "step_name": "Initialize automation",
                    "action_type": "setup",
                    "description": f"Setup {platform} automation environment",
                    "expected_result": "Environment ready",
                    "validation_method": "system_check"
                },
                {
                    "step_order": 2,
                    "step_name": "Navigate to target",
                    "action_type": "navigate",
                    "description": "Navigate to target application/page",
                    "expected_result": "Target loaded",
                    "validation_method": "page_check"
                },
                {
                    "step_order": 3,
                    "step_name": "Perform main action",
                    "action_type": "interact",
                    "description": f"Execute task: {instruction}",
                    "expected_result": "Task completed",
                    "validation_method": "result_check"
                },
                {
                    "step_order": 4,
                    "step_name": "Validate completion",
                    "action_type": "validate",
                    "description": "Verify task completion",
                    "expected_result": "Validation successful",
                    "validation_method": "ocr_validation"
                }
            ]
        
        return steps
    
    def _assess_complexity(self, steps: List[Dict]) -> str:
        """Assess automation complexity"""
        step_count = len(steps)
        if step_count <= 3:
            return "simple"
        elif step_count <= 6:
            return "medium"
        else:
            return "complex"
    
    def _generate_requirements(self, platform: str, task_category: str) -> List[str]:
        """Generate requirements.txt content based on platform and task"""
        base_requirements = [
            "selenium>=4.0.0",
            "requests>=2.25.0",
            "Pillow>=8.0.0",
            "pytesseract>=0.3.8"
        ]
        
        if platform.lower() in ["mobile", "android", "ios"]:
            base_requirements.extend([
                "Appium-Python-Client>=2.0.0",
                "opencv-python>=4.5.0"
            ])
        elif platform.lower() in ["web", "browser"]:
            base_requirements.extend([
                "playwright>=1.20.0",
                "beautifulsoup4>=4.9.0"
            ])
        
        if task_category in ["form_filling", "account_creation"]:
            base_requirements.append("faker>=8.0.0")
        
        return base_requirements
    
    async def _create_workflow_steps_in_db(self, seq_id: int, steps: List[Dict[str, Any]]):
        """Create workflow steps in database"""
        if not steps:
            return
        
        db_steps = []
        for step in steps:
            db_steps.append({
                "step_name": step.get("step_name", step.get("description", f"Step {step.get('step_order', 1)}")),
                "action_type": step.get("action_type", "unknown"),
                "expected_result": step.get("expected_result", "Success")
            })
        
        step_ids = await self.db_manager.create_workflow_steps(
            seq_id=seq_id,
            agent_name=self.agent_name,
            steps=db_steps
        )
        
        logger.info(f"🔵 [Agent1] Created {len(step_ids)} workflow steps in database")
    
    async def _initialize_task_database(self, task_db_path: Path, seq_id: int):
        """Initialize SQLite database file in task folder"""
        # Create a copy of the main database structure in the task folder
        # This allows each task to have its own portable database
        
        task_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy main database to task folder (simplified approach)
        import shutil
        if Path("sqlite_db.sqlite").exists():
            shutil.copy2("sqlite_db.sqlite", str(task_db_path))
            logger.info(f"🔵 [Agent1] ✅ Task database created: {task_db_path}")
        else:
            # Create new database with same schema
            from app.database.database_manager import DATABASE_SCHEMA
            
            async with aiosqlite.connect(str(task_db_path)) as db:
                await db.executescript(DATABASE_SCHEMA)
                await db.commit()
            
            logger.info(f"🔵 [Agent1] ✅ New task database initialized: {task_db_path}")
    
    def _calculate_confidence(self, text_content: str, ui_elements: List[Dict], blueprint: Dict) -> float:
        """Calculate blueprint confidence score"""
        confidence = 0.0
        
        # Text content factor (30%)
        if len(text_content) > 100:
            confidence += 0.3
        elif len(text_content) > 50:
            confidence += 0.15
        
        # UI elements factor (30%)
        if len(ui_elements) > 5:
            confidence += 0.3
        elif len(ui_elements) > 0:
            confidence += 0.15
        
        # Blueprint completeness factor (40%)
        steps = blueprint.get('steps', [])
        if len(steps) > 4:
            confidence += 0.4
        elif len(steps) > 0:
            confidence += 0.2
        
        return min(confidence, 1.0)
