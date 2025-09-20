"""
Updated Agent 2: Code Generation with Testing Environment Setup
Generates Python scripts, creates requirements.txt, and prepares OCR logs
"""
import asyncio
import json
import logging
import time
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import anthropic

# Import the updated database manager
from app.database.database_manager import get_testing_db

logger = logging.getLogger(__name__)

class UpdatedAgent2_CodeGenerator:
    """Agent 2: Code Generation with Testing Environment Preparation"""
    
    def __init__(self):
        self.agent_name = "agent2"
        self.db_manager = None
        self.anthropic_client = None
        
    async def initialize(self):
        """Initialize database and AI client"""
        self.db_manager = await get_testing_db()
        
        # Initialize Anthropic client
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.anthropic_client = anthropic.AsyncAnthropic(api_key=api_key)
                logger.info("🟢 Agent 2: Claude AI client initialized")
            else:
                logger.warning("🟡 Agent 2: No Claude API key, using template generation")
        except Exception as e:
            logger.warning(f"🟡 Agent 2: Claude initialization failed: {str(e)}")
            
        logger.info("🟢 Agent 2: Code generator initialized with testing environment setup")
    
    async def generate_code_and_setup(self, seq_id: int) -> Dict[str, Any]:
        """
        Generate automation code and setup testing environment
        
        Args:
            seq_id: Sequential task ID from Agent 1
            
        Returns:
            Code generation results with testing setup
        """
        start_time = time.time()
        
        logger.info(f"🟢 [Agent2] Starting code generation for task {seq_id}")
        
        try:
            # Get task information from database
            task_info = await self.db_manager.get_task_info(seq_id)
            if not task_info:
                raise Exception(f"Task {seq_id} not found in database")
            
            # Update task status
            await self.db_manager.update_task_status(seq_id, "code_generation", "agent2")
            
            # Create agent2 folder structure
            base_path = Path(task_info['base_path'])
            agent2_path = base_path / "agent2"
            agent2_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"🟢 [Agent2] Created agent2 folder: {agent2_path}")
            
            # Load blueprint from agent1
            blueprint_path = base_path / "agent1" / "blueprint.json"
            if not blueprint_path.exists():
                raise Exception("Blueprint not found from Agent 1")
            
            with open(blueprint_path, 'r', encoding='utf-8') as f:
                blueprint = json.load(f)
            
            logger.info(f"🟢 [Agent2] Loaded blueprint with {len(blueprint.get('steps', []))} steps")
            
            # Get workflow steps from database
            workflow_steps = await self.db_manager.get_workflow_steps(seq_id)
            
            # Generate initial script
            script_content = await self._generate_automation_script(
                seq_id, task_info['instruction'], task_info['platform'], 
                blueprint, workflow_steps
            )
            
            # Save script.py (version 1)
            script_path = agent2_path / "script.py"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Save to database
            await self.db_manager.save_generated_file(
                seq_id=seq_id,
                agent_name=self.agent_name,
                file_name="script.py",
                file_path=str(script_path),
                file_type="script",
                version=1
            )
            
            # Generate requirements.txt
            requirements_content = self._generate_requirements_txt(
                task_info['platform'], blueprint.get('task_category', 'automation')
            )
            
            requirements_path = agent2_path / "requirements.txt"
            with open(requirements_path, 'w', encoding='utf-8') as f:
                f.write(requirements_content)
            
            # Save requirements to database
            await self.db_manager.save_generated_file(
                seq_id=seq_id,
                agent_name=self.agent_name,
                file_name="requirements.txt",
                file_path=str(requirements_path),
                file_type="requirements",
                version=1
            )
            
            # Create OCR logs folder structure
            ocr_logs_path = agent2_path / "ocr_logs"
            ocr_logs_path.mkdir(exist_ok=True)
            
            # Generate OCR log template for each step
            await self._generate_ocr_log_templates(seq_id, workflow_steps, ocr_logs_path)
            
            # Update task progress
            await self.db_manager.update_task_progress(seq_id, code_generated=True)
            await self.db_manager.update_task_status(seq_id, "code_completed", "agent2")
            
            processing_time = time.time() - start_time
            
            logger.info(f"🟢 [Agent2] ✅ Script generated: {len(script_content)} characters")
            logger.info(f"🟢 [Agent2] ✅ Requirements created: {requirements_path}")
            logger.info(f"🟢 [Agent2] ✅ OCR log templates prepared: {ocr_logs_path}")
            logger.info(f"🟢 [Agent2] ✅ Code generation completed")
            
            return {
                "success": True,
                "seq_id": seq_id,
                "agent": self.agent_name,
                "agent2_path": str(agent2_path),
                "script_path": str(script_path),
                "requirements_path": str(requirements_path),
                "ocr_logs_path": str(ocr_logs_path),
                "script_size": len(script_content),
                "platform": task_info['platform'],
                "steps_count": len(workflow_steps),
                "processing_time": processing_time,
                "ready_for_testing": True
            }
            
        except Exception as e:
            error_msg = f"Code generation failed: {str(e)}"
            logger.error(f"🔴 [Agent2] {error_msg}")
            
            # Update task status
            await self.db_manager.update_task_status(seq_id, "failed", "agent2")
            
            return {
                "success": False,
                "error": error_msg,
                "seq_id": seq_id,
                "agent": self.agent_name,
                "processing_time": time.time() - start_time
            }
    
    async def handle_agent3_feedback(self, seq_id: int, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle feedback from Agent 3 and generate improved script
        
        Args:
            seq_id: Task sequential ID
            feedback_data: Feedback from Agent 3 with issues and suggestions
            
        Returns:
            Script update results
        """
        logger.info(f"🟢 [Agent2] 🤝 Received feedback from Agent 3 for task {seq_id}")
        logger.info(f"🟢 [Agent2] Issues reported: {len(feedback_data.get('issues', []))}")
        logger.info(f"🟢 [Agent2] Suggestions: {len(feedback_data.get('suggestions', []))}")
        
        try:
            # Record communication in database
            comm_id = await self.db_manager.create_agent_communication(
                seq_id=seq_id,
                from_agent="agent3",
                to_agent=self.agent_name,
                message_type="test_feedback",
                message_content=json.dumps(feedback_data)
            )
            
            # Get current script version
            current_version = await self.db_manager.get_latest_script_version(seq_id)
            new_version = current_version + 1
            
            # Generate improved script
            task_info = await self.db_manager.get_task_info(seq_id)
            base_path = Path(task_info['base_path'])
            agent2_path = base_path / "agent2"
            
            # Load blueprint
            blueprint_path = base_path / "agent1" / "blueprint.json"
            with open(blueprint_path, 'r', encoding='utf-8') as f:
                blueprint = json.load(f)
            
            # Get workflow steps
            workflow_steps = await self.db_manager.get_workflow_steps(seq_id)
            
            # Generate improved script
            improved_script = await self._generate_improved_script(
                seq_id, task_info['instruction'], task_info['platform'],
                blueprint, workflow_steps, feedback_data, current_version
            )
            
            # Save updated script
            update_filename = f"update_{new_version - 1}.py"  # update_1.py, update_2.py, etc.
            update_path = agent2_path / update_filename
            
            with open(update_path, 'w', encoding='utf-8') as f:
                f.write(improved_script)
            
            # Save to database
            await self.db_manager.save_generated_file(
                seq_id=seq_id,
                agent_name=self.agent_name,
                file_name=update_filename,
                file_path=str(update_path),
                file_type="script",
                version=new_version
            )
            
            # Update communication with response
            response_content = f"Generated improved script {update_filename} with {len(feedback_data.get('suggestions', []))} improvements applied"
            await self.db_manager.update_communication_response(comm_id, response_content)
            
            logger.info(f"🟢 [Agent2] ✅ Generated improved script: {update_filename}")
            logger.info(f"🟢 [Agent2] ✅ Script version: {new_version}")
            
            return {
                "success": True,
                "seq_id": seq_id,
                "script_updated": True,
                "new_version": new_version,
                "update_filename": update_filename,
                "update_path": str(update_path),
                "improvements_applied": len(feedback_data.get('suggestions', [])),
                "issues_addressed": len(feedback_data.get('issues', []))
            }
            
        except Exception as e:
            error_msg = f"Script update failed: {str(e)}"
            logger.error(f"🔴 [Agent2] {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "seq_id": seq_id
            }
    
    async def _generate_automation_script(self, seq_id: int, instruction: str, platform: str,
                                         blueprint: Dict, workflow_steps: List[Dict]) -> str:
        """Generate automation script based on blueprint and steps"""
        
        if self.anthropic_client:
            return await self._generate_ai_script(seq_id, instruction, platform, blueprint, workflow_steps)
        else:
            return self._generate_template_script(seq_id, instruction, platform, blueprint, workflow_steps)
    
    async def _generate_ai_script(self, seq_id: int, instruction: str, platform: str,
                                 blueprint: Dict, workflow_steps: List[Dict]) -> str:
        """Generate script using Claude AI"""
        
        steps_context = []
        for step in workflow_steps:
            steps_context.append({
                "step_order": step['step_order'],
                "step_name": step['step_name'],
                "action_type": step['action_type'],
                "expected_result": step['expected_result']
            })
        
        prompt = f"""
Generate a comprehensive Python automation script for the following task:

Task: {instruction}
Platform: {platform}
Task ID: {seq_id}
Task Category: {blueprint.get('task_category', 'automation')}

Blueprint Steps:
{json.dumps(steps_context, indent=2)}

Requirements:
1. Use appropriate automation library (Playwright for web, Appium for mobile)
2. Include OCR screenshot capture after each step for validation
3. Save OCR results to ocr_logs/ folder with step names
4. Add proper error handling and logging
5. Include detailed comments for each step
6. Make script executable and production-ready
7. Add wait conditions and element verification
8. Include setup and cleanup methods

Platform-specific requirements:
- For web: Use Playwright with proper selectors and wait conditions
- For mobile: Use Appium with proper capabilities and element finding
- For both: Include screenshot and OCR validation after each action

The script should create OCR log files in the format:
- step_1_screenshot.png
- step_1_ocr.txt
- step_2_screenshot.png
- step_2_ocr.txt
etc.

Generate a complete, executable Python script that implements all workflow steps with OCR validation.
"""
        
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            if response.content and response.content[0].text:
                generated_code = response.content[0].text
                
                # Clean up code (remove markdown formatting if present)
                if "```python" in generated_code:
                    generated_code = generated_code.split("```python")[1]
                    if "```" in generated_code:
                        generated_code = generated_code.split("```")[0]
                elif "```" in generated_code:
                    parts = generated_code.split("```")
                    if len(parts) >= 2:
                        generated_code = parts[1]
                
                return generated_code.strip()
            else:
                raise Exception("Empty response from Claude AI")
                
        except Exception as e:
            logger.error(f"🔴 [Agent2] AI script generation failed: {str(e)}")
            # Fallback to template generation
            return self._generate_template_script(seq_id, instruction, platform, blueprint, workflow_steps)
    
    def _generate_template_script(self, seq_id: int, instruction: str, platform: str,
                                 blueprint: Dict, workflow_steps: List[Dict]) -> str:
        """Generate script using templates when AI is not available"""
        
        if platform.lower() in ["mobile", "android", "ios"]:
            return self._generate_mobile_template(seq_id, instruction, workflow_steps)
        else:
            return self._generate_web_template(seq_id, instruction, workflow_steps)
    
    def _generate_mobile_template(self, seq_id: int, instruction: str, workflow_steps: List[Dict]) -> str:
        """Generate mobile automation template with OCR integration"""
        
        steps_code = ""
        for i, step in enumerate(workflow_steps, 1):
            steps_code += f"""
        # Step {i}: {step['step_name']}
        logger.info(f"Executing Step {i}: {step['step_name']}")
        try:
            # Take screenshot before action
            screenshot_before = self.take_screenshot_with_ocr(f"step_{i}_before")
            
            # TODO: Implement {step['action_type']} action for: {step['step_name']}
            # Expected result: {step['expected_result']}
            time.sleep(2)  # Placeholder for actual automation
            
            # Take screenshot after action
            screenshot_after = self.take_screenshot_with_ocr(f"step_{i}_after")
            
            logger.info(f"Step {i} completed successfully")
            step_results.append({{
                "step": {i},
                "name": "{step['step_name']}",
                "status": "completed",
                "screenshot_before": screenshot_before[0],
                "ocr_before": screenshot_before[1],
                "screenshot_after": screenshot_after[0],
                "ocr_after": screenshot_after[1]
            }})
            
        except Exception as e:
            logger.error(f"Step {i} failed: {{e}}")
            step_results.append({{
                "step": {i},
                "name": "{step['step_name']}",
                "status": "failed",
                "error": str(e)
            }})
            raise
"""
        
        return f'''
"""
Mobile Automation Script - Task {seq_id}
Generated by Agent 2
Task: {instruction}
"""
import logging
import time
import json
from datetime import datetime
from pathlib import Path
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytesseract
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MobileAutomationRunner:
    def __init__(self):
        self.driver = None
        self.ocr_logs_dir = Path("ocr_logs")
        self.ocr_logs_dir.mkdir(exist_ok=True)
        
    def setup_driver(self):
        """Setup Appium driver"""
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = "emulator-5554"  # Adjust as needed
        options.automation_name = "UiAutomator2"
        options.app_wait_timeout = 30000
        
        self.driver = webdriver.Remote("http://localhost:4723", options=options)
        self.driver.implicitly_wait(10)
        logger.info("✅ Mobile driver initialized")
        
    def take_screenshot_with_ocr(self, step_name: str):
        """Take screenshot and perform OCR"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = self.ocr_logs_dir / f"{{step_name}}_{{timestamp}}.png"
        ocr_path = self.ocr_logs_dir / f"{{step_name}}_{{timestamp}}.txt"
        
        if self.driver:
            # Take screenshot
            self.driver.save_screenshot(str(screenshot_path))
            
            # Perform OCR
            image = Image.open(screenshot_path)
            ocr_text = pytesseract.image_to_string(image)
            
            # Save OCR result
            with open(ocr_path, 'w', encoding='utf-8') as f:
                f.write(f"OCR Result for {{step_name}}\\n")
                f.write(f"Timestamp: {{timestamp}}\\n")
                f.write(f"Screenshot: {{screenshot_path}}\\n")
                f.write(f"\\nOCR Text:\\n{{ocr_text}}")
            
            logger.info(f"Screenshot and OCR saved: {{screenshot_path}}, {{ocr_path}}")
            return str(screenshot_path), ocr_text
        
        return "", ""
    
    def run_automation(self):
        """Execute the automation workflow with OCR validation"""
        step_results = []
        
        try:
            logger.info("🚀 Starting mobile automation...")
            logger.info(f"Task: {instruction}")
            
            # Setup driver
            self.setup_driver()
            
            # Execute workflow steps with OCR
{steps_code}
            
            # Save results summary
            results_path = self.ocr_logs_dir / "automation_results.json"
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump({{
                    "task_id": {seq_id},
                    "instruction": "{instruction}",
                    "execution_time": datetime.utcnow().isoformat(),
                    "total_steps": len(step_results),
                    "completed_steps": len([r for r in step_results if r["status"] == "completed"]),
                    "failed_steps": len([r for r in step_results if r["status"] == "failed"]),
                    "results": step_results
                }}, f, indent=2)
            
            logger.info("✅ Mobile automation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Mobile automation failed: {{e}}")
            return False
            
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    runner = MobileAutomationRunner()
    success = runner.run_automation()
    exit(0 if success else 1)
'''
    
    def _generate_web_template(self, seq_id: int, instruction: str, workflow_steps: List[Dict]) -> str:
        """Generate web automation template with OCR integration"""
        
        steps_code = ""
        for i, step in enumerate(workflow_steps, 1):
            steps_code += f"""
        # Step {i}: {step['step_name']}
        logger.info(f"Executing Step {i}: {step['step_name']}")
        try:
            # Take screenshot before action
            screenshot_before = await self.take_screenshot_with_ocr(f"step_{i}_before")
            
            # TODO: Implement {step['action_type']} action for: {step['step_name']}
            # Expected result: {step['expected_result']}
            await asyncio.sleep(2)  # Placeholder for actual automation
            
            # Take screenshot after action
            screenshot_after = await self.take_screenshot_with_ocr(f"step_{i}_after")
            
            logger.info(f"Step {i} completed successfully")
            step_results.append({{
                "step": {i},
                "name": "{step['step_name']}",
                "status": "completed",
                "screenshot_before": screenshot_before[0],
                "ocr_before": screenshot_before[1],
                "screenshot_after": screenshot_after[0],
                "ocr_after": screenshot_after[1]
            }})
            
        except Exception as e:
            logger.error(f"Step {i} failed: {{e}}")
            step_results.append({{
                "step": {i},
                "name": "{step['step_name']}",
                "status": "failed",
                "error": str(e)
            }})
            raise
"""
        
        return f'''
"""
Web Automation Script - Task {seq_id}
Generated by Agent 2
Task: {instruction}
"""
import asyncio
import logging
import time
import json
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page
import pytesseract
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebAutomationRunner:
    def __init__(self):
        self.browser: Browser = None
        self.page: Page = None
        self.ocr_logs_dir = Path("ocr_logs")
        self.ocr_logs_dir.mkdir(exist_ok=True)
        
    async def setup_browser(self):
        """Setup Playwright browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        
        # Set viewport
        await self.page.set_viewport_size({{"width": 1280, "height": 720}})
        logger.info("✅ Web browser initialized")
        
    async def take_screenshot_with_ocr(self, step_name: str):
        """Take screenshot and perform OCR"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = self.ocr_logs_dir / f"{{step_name}}_{{timestamp}}.png"
        ocr_path = self.ocr_logs_dir / f"{{step_name}}_{{timestamp}}.txt"
        
        if self.page:
            # Take screenshot
            await self.page.screenshot(path=str(screenshot_path))
            
            # Perform OCR
            image = Image.open(screenshot_path)
            ocr_text = pytesseract.image_to_string(image)
            
            # Save OCR result
            with open(ocr_path, 'w', encoding='utf-8') as f:
                f.write(f"OCR Result for {{step_name}}\\n")
                f.write(f"Timestamp: {{timestamp}}\\n")
                f.write(f"Screenshot: {{screenshot_path}}\\n")
                f.write(f"\\nOCR Text:\\n{{ocr_text}}")
            
            logger.info(f"Screenshot and OCR saved: {{screenshot_path}}, {{ocr_path}}")
            return str(screenshot_path), ocr_text
        
        return "", ""
    
    async def run_automation(self):
        """Execute the automation workflow with OCR validation"""
        step_results = []
        
        try:
            logger.info("🚀 Starting web automation...")
            logger.info(f"Task: {instruction}")
            
            # Setup browser
            await self.setup_browser()
            
            # Execute workflow steps with OCR
{steps_code}
            
            # Save results summary
            results_path = self.ocr_logs_dir / "automation_results.json"
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump({{
                    "task_id": {seq_id},
                    "instruction": "{instruction}",
                    "execution_time": datetime.utcnow().isoformat(),
                    "total_steps": len(step_results),
                    "completed_steps": len([r for r in step_results if r["status"] == "completed"]),
                    "failed_steps": len([r for r in step_results if r["status"] == "failed"]),
                    "results": step_results
                }}, f, indent=2)
            
            logger.info("✅ Web automation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Web automation failed: {{e}}")
            return False
            
        finally:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

async def main():
    runner = WebAutomationRunner()
    success = await runner.run_automation()
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
'''
    
    def _generate_requirements_txt(self, platform: str, task_category: str) -> str:
        """Generate requirements.txt content"""
        requirements = [
            "# Automation Testing Requirements",
            "# Generated by Agent 2",
            "",
            "# Core automation libraries",
            "selenium>=4.0.0",
            "requests>=2.25.0",
            "Pillow>=8.0.0",
            "pytesseract>=0.3.8",
            "opencv-python>=4.5.0",
            ""
        ]
        
        if platform.lower() in ["mobile", "android", "ios"]:
            requirements.extend([
                "# Mobile automation",
                "Appium-Python-Client>=2.0.0",
                ""
            ])
        
        if platform.lower() in ["web", "browser"]:
            requirements.extend([
                "# Web automation", 
                "playwright>=1.20.0",
                "beautifulsoup4>=4.9.0",
                ""
            ])
        
        if task_category in ["form_filling", "account_creation"]:
            requirements.extend([
                "# Data generation",
                "faker>=8.0.0",
                ""
            ])
        
        requirements.extend([
            "# Utilities",
            "python-dateutil>=2.8.0",
            "colorlog>=6.0.0"
        ])
        
        return "\\n".join(requirements)
    
    async def _generate_ocr_log_templates(self, seq_id: int, workflow_steps: List[Dict], ocr_logs_path: Path):
        """Generate OCR log templates for each workflow step"""
        
        for i, step in enumerate(workflow_steps, 1):
            # Create template OCR log file
            template_path = ocr_logs_path / f"step_{i}_{step['step_name'].replace(' ', '_').lower()}_template.txt"
            
            template_content = f"""OCR Log Template - Step {i}
Step Name: {step['step_name']}
Action Type: {step['action_type']}
Expected Result: {step['expected_result']}

This file will be populated with actual OCR results during testing.

Template created by Agent 2 at: {datetime.utcnow().isoformat()}
Task ID: {seq_id}
"""
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
        
        logger.info(f"🟢 [Agent2] Created {len(workflow_steps)} OCR log templates")
    
    async def _generate_improved_script(self, seq_id: int, instruction: str, platform: str,
                                       blueprint: Dict, workflow_steps: List[Dict],
                                       feedback_data: Dict, current_version: int) -> str:
        """Generate improved script based on Agent 3 feedback"""
        
        # Extract issues and suggestions from feedback
        issues = feedback_data.get('issues', [])
        suggestions = feedback_data.get('suggestions', [])
        
        if self.anthropic_client:
            return await self._generate_ai_improved_script(
                seq_id, instruction, platform, blueprint, workflow_steps, 
                issues, suggestions, current_version
            )
        else:
            # For template-based approach, apply basic improvements
            base_script = await self._generate_automation_script(
                seq_id, instruction, platform, blueprint, workflow_steps
            )
            
            # Add improvement comments
            improvements_header = f"""
'''
IMPROVED SCRIPT - Version {current_version + 1}
Previous issues addressed:
{chr(10).join(f"- {issue}" for issue in issues)}

Improvements applied:
{chr(10).join(f"- {suggestion}" for suggestion in suggestions)}
'''

"""
            return improvements_header + base_script
    
    async def _generate_ai_improved_script(self, seq_id: int, instruction: str, platform: str,
                                          blueprint: Dict, workflow_steps: List[Dict],
                                          issues: List[str], suggestions: List[str], 
                                          current_version: int) -> str:
        """Generate improved script using AI based on feedback"""
        
        prompt = f"""
Improve the automation script based on testing feedback:

Original Task: {instruction}
Platform: {platform}  
Task ID: {seq_id}
Current Version: {current_version}

Issues from testing:
{json.dumps(issues, indent=2)}

Improvement suggestions:
{json.dumps(suggestions, indent=2)}

Workflow Steps:
{json.dumps([{
    "step_order": step['step_order'],
    "step_name": step['step_name'], 
    "action_type": step['action_type'],
    "expected_result": step['expected_result']
} for step in workflow_steps], indent=2)}

Please generate an improved version that:
1. Addresses all identified issues
2. Implements suggested improvements
3. Includes better error handling and recovery
4. Adds more robust element detection and waiting
5. Improves OCR validation and screenshot capture
6. Adds retry mechanisms for failed operations
7. Includes better logging and debugging information

Generate a complete, improved Python automation script.
"""
        
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            if response.content and response.content[0].text:
                improved_code = response.content[0].text
                
                # Clean up code
                if "```python" in improved_code:
                    improved_code = improved_code.split("```python")[1]
                    if "```" in improved_code:
                        improved_code = improved_code.split("```")[0]
                elif "```" in improved_code:
                    parts = improved_code.split("```")
                    if len(parts) >= 2:
                        improved_code = parts[1]
                
                return improved_code.strip()
            else:
                raise Exception("Empty response from Claude AI")
                
        except Exception as e:
            logger.error(f"🔴 [Agent2] AI script improvement failed: {str(e)}")
            raise
