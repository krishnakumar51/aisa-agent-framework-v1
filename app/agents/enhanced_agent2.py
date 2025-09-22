"""
Agent2 Code Generation
Production Agent2 with integrated @tool decorators and database logging
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# LangGraph tool decorator
try:
    from langchain_core.tools import tool
    from langchain_core.messages import HumanMessage, AIMessage
    LANGGRAPH_AVAILABLE = True
    print("✅ LangGraph @tool decorator available")
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    print(f"⚠️ LangGraph @tool decorator not available: {str(e)}")
    def tool(func):
        func._is_tool = True
        return func

# Framework imports
try:
    from app.database.database_manager import get_database_manager
    from app.utils.output_structure_manager import OutputStructureManager
    from app.utils.model_client import get_model_client
    from app.device_manager import get_device_manager
    from app.tools.code_tools import get_agent2_tools
    from app.tools.shared_tools import agent_communication_tool, error_handling_tool
    FRAMEWORK_AVAILABLE = True
except ImportError as e:
    FRAMEWORK_AVAILABLE = False
    print(f"⚠️ Framework components not available: {str(e)}")

logger = logging.getLogger(__name__)

class Agent2CodeGeneration:
    """
    Production Agent2 with integrated tool system and database logging.
    Uses @tool decorators for LangGraph compatibility while maintaining existing functionality.
    """
    
    def __init__(self):
        self.agent_name = "agent2"
        self.model_client = None
        self.db_manager = None
        self.device_manager = None
        self.output_manager = None
        self.tools = get_agent2_tools() if FRAMEWORK_AVAILABLE else []
        self.initialized = False
        logger.info("🔧 Agent2 Code Generation initialized with tool integration")
    
    async def initialize(self, task_id: int) -> Dict[str, Any]:
        """Initialize Agent2 components"""
        
        if not FRAMEWORK_AVAILABLE:
            return {
                "success": False,
                "error": "Framework components not available"
            }
        
        try:
            # Initialize components
            self.model_client = get_model_client()
            self.db_manager = await get_database_manager()
            self.device_manager = get_device_manager()
            self.output_manager = OutputStructureManager(task_id)
            
            self.initialized = True
            
            result = {
                "success": True,
                "agent": self.agent_name,
                "task_id": task_id,
                "tools_available": len(self.tools),
                "components_initialized": ["model_client", "db_manager", "device_manager", "output_manager"],
                "initialized_at": datetime.now().isoformat()
            }
            
            logger.info("✅ Agent2 components initialized successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Agent2 initialization failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_code_generation(
        self,
        task_id: int,
        blueprint: Dict[str, Any],
        platform: str,
        device_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Main execution method using integrated tools"""
        
        if not self.initialized:
            init_result = await self.initialize(task_id)
            if not init_result["success"]:
                return init_result
        
        try:
            # Log agent execution start
            await self.db_manager.log_agent_execution(
                task_id, self.agent_name, "started",
                {"platform": platform, "blueprint_elements": len(blueprint.get("ui_elements", []))}
            )
            
            # Get device information for mobile
            if platform == "mobile" and not device_info:
                devices = self.device_manager.get_connected_devices()
                device_info = devices[0] if devices else None
            
            # Use the integrated code generation tools
            if self.tools:
                script_generation_tool = None
                code_save_tool = None
                
                # Find tools by name
                for tool in self.tools:
                    if "script_generation" in tool.__name__:
                        script_generation_tool = tool
                    elif "code_save" in tool.__name__:
                        code_save_tool = tool
                
                # Step 1: Script Generation
                if script_generation_tool:
                    generation_result = await script_generation_tool(
                        task_id=task_id,
                        blueprint=blueprint,
                        platform=platform,
                        device_info=device_info
                    )
                    
                    if not generation_result.get("success", False):
                        # Use error handling tool
                        await error_handling_tool(
                            task_id=task_id,
                            agent_name=self.agent_name,
                            error_type="script_generation_failed",
                            error_details=generation_result,
                            recovery_attempted=False,
                            escalate_to_supervisor=True
                        )
                        
                        return {
                            "success": False,
                            "agent": self.agent_name,
                            "error": generation_result.get("error", "Script generation failed"),
                            "execution_failed_at": "script_generation",
                            "collaboration_needed": True
                        }
                    
                    generated_code = generation_result
                    
                    # Step 2: Code Save (if tool available)
                    if code_save_tool:
                        save_result = await code_save_tool(
                            task_id=task_id,
                            generated_code=generated_code,
                            save_ocr_templates=True
                        )
                        
                        if save_result.get("success"):
                            generated_code["saved_files"] = save_result.get("files_saved", {})
                        else:
                            logger.warning(f"Code save failed: {save_result.get('error')}")
                    
                    # Send success communication to next agent
                    await agent_communication_tool(
                        task_id=task_id,
                        from_agent=self.agent_name,
                        to_agent="agent3",
                        message_type="handoff",
                        message_content={
                            "status": "completed",
                            "code_generated": True,
                            "platform": platform,
                            "script_lines": generated_code.get("script_content", "").count('\n') + 1,
                            "requirements_count": len(generated_code.get("requirements_content", "").split('\n')),
                            "device_config_available": bool(generated_code.get("device_config")),
                            "files_saved": len(generated_code.get("saved_files", {}))
                        },
                        priority="medium",
                        requires_response=False
                    )
                    
                    # Log agent execution completion
                    await self.db_manager.log_agent_execution(
                        task_id, self.agent_name, "completed", generated_code
                    )
                    
                    return {
                        "success": True,
                        "agent": self.agent_name,
                        "task_id": task_id,
                        "generated_code": generated_code,
                        "script_content": generated_code.get("script_content", ""),
                        "requirements_content": generated_code.get("requirements_content", ""),
                        "device_config": generated_code.get("device_config", {}),
                        "saved_files": generated_code.get("saved_files", {}),
                        "execution_time": generated_code.get("execution_time", 0.0),
                        "completed_at": datetime.now().isoformat()
                    }
                else:
                    # No script generation tool - use fallback
                    return await self._fallback_code_generation(task_id, blueprint, platform, device_info)
            else:
                # No tools available - use fallback
                return await self._fallback_code_generation(task_id, blueprint, platform, device_info)
                
        except Exception as e:
            logger.error(f"❌ Agent2 execution failed: {str(e)}")
            
            # Log execution error
            if self.db_manager:
                try:
                    await self.db_manager.log_agent_execution(
                        task_id, self.agent_name, "failed", {"error": str(e)}
                    )
                except:
                    pass
            
            # Use error handling tool
            if FRAMEWORK_AVAILABLE:
                try:
                    await error_handling_tool(
                        task_id=task_id,
                        agent_name=self.agent_name,
                        error_type="agent_execution_error",
                        error_details={
                            "error_message": str(e),
                            "context": "agent2_execute_code_generation",
                            "collaboration_needed": True
                        },
                        recovery_attempted=False,
                        escalate_to_supervisor=True
                    )
                except:
                    pass
            
            return {
                "success": False,
                "agent": self.agent_name,
                "error": str(e),
                "execution_failed_at": "agent_execution",
                "collaboration_needed": True
            }
    
    async def _fallback_code_generation(
        self,
        task_id: int,
        blueprint: Dict[str, Any],
        platform: str,
        device_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Fallback code generation when tools are not available"""
        
        try:
            logger.info("🔄 Using fallback code generation")
            
            # Generate script content based on platform and blueprint
            if platform == "web":
                script_content = self._generate_web_script(blueprint)
                requirements_content = "playwright>=1.40.0\nrequests>=2.31.0"
                device_config = {
                    "platform": "web",
                    "browser": "chromium",
                    "headless": False,
                    "viewport": {"width": 1280, "height": 800}
                }
            else:  # mobile
                script_content = self._generate_mobile_script(blueprint)
                requirements_content = "Appium-Python-Client>=3.1.0\nuiautomator2>=3.0.0"
                device_config = {
                    "platform": "mobile",
                    "capabilities": {
                        "platformName": "Android",
                        "deviceName": device_info.get("device_id", "emulator-5554") if device_info else "emulator-5554",
                        "automationName": "UiAutomator2",
                        "noReset": True
                    }
                }
            
            generated_code = {
                "script_content": script_content,
                "requirements_content": requirements_content,
                "device_config": device_config,
                "generation_method": "fallback",
                "platform": platform,
                "blueprint_elements_used": len(blueprint.get("ui_elements", [])),
                "workflow_steps_used": len(blueprint.get("workflow_steps", []))
            }
            
            # Save code using output manager
            try:
                saved_files = self.output_manager.save_agent2_outputs(
                    script_content, requirements_content, device_config
                )
                generated_code["saved_files"] = saved_files
            except Exception as e:
                logger.warning(f"Could not save fallback code: {str(e)}")
                generated_code["saved_files"] = {}
            
            # Save to database
            if self.db_manager:
                try:
                    await self.db_manager.save_agent_output(
                        task_id, self.agent_name, "generated_code_fallback",
                        json.dumps(generated_code)
                    )
                    
                    await self.db_manager.log_agent_execution(
                        task_id, self.agent_name, "completed_fallback", {"method": "fallback"}
                    )
                except Exception as e:
                    logger.warning(f"Could not save fallback code to database: {str(e)}")
            
            return {
                "success": True,
                "agent": self.agent_name,
                "task_id": task_id,
                "generated_code": generated_code,
                "script_content": script_content,
                "requirements_content": requirements_content,
                "device_config": device_config,
                "saved_files": generated_code.get("saved_files", {}),
                "execution_method": "fallback",
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Fallback code generation failed: {str(e)}")
            return {
                "success": False,
                "agent": self.agent_name,
                "error": f"Fallback generation failed: {str(e)}",
                "execution_failed_at": "fallback_generation"
            }
    
    def _generate_web_script(self, blueprint: Dict[str, Any]) -> str:
        """Generate web automation script from blueprint"""
        
        workflow_steps = blueprint.get("workflow_steps", [])
        
        script_lines = [
            "import asyncio",
            "from playwright.async_api import async_playwright",
            "",
            "async def run_automation():",
            "    async with async_playwright() as playwright:",
            "        browser = await playwright.chromium.launch(headless=False)",
            "        context = await browser.new_context()",
            "        page = await context.new_page()",
            "        ",
            "        try:",
            "            # Navigate to target URL",
            "            await page.goto('https://example.com')",
            "            await page.wait_for_load_state('networkidle')",
            "            ",
            "            # Generated automation steps"
        ]
        
        for step in workflow_steps:
            if step.get("action") == "input":
                script_lines.append(f"            await page.fill('{step.get('target', '')}', '{step.get('value', '')}')")
            elif step.get("action") == "click":
                script_lines.append(f"            await page.click('{step.get('target', '')}')")
            elif step.get("action") == "wait":
                script_lines.append(f"            await page.wait_for_timeout({step.get('duration', 1000)})")
        
        script_lines.extend([
            "            ",
            "            print('Automation completed successfully')",
            "        except Exception as e:",
            "            print(f'Automation failed: {e}')",
            "        finally:",
            "            await context.close()",
            "            await browser.close()",
            "",
            "if __name__ == '__main__':",
            "    asyncio.run(run_automation())"
        ])
        
        return "\n".join(script_lines)
    
    def _generate_mobile_script(self, blueprint: Dict[str, Any]) -> str:
        """Generate mobile automation script from blueprint"""
        
        workflow_steps = blueprint.get("workflow_steps", [])
        
        script_lines = [
            "import json",
            "import sys",
            "from appium import webdriver",
            "from appium.webdriver.common.appiumby import AppiumBy",
            "",
            "def run_automation(device_config_path):",
            "    with open(device_config_path, 'r') as f:",
            "        config = json.load(f)",
            "    ",
            "    driver = webdriver.Remote('http://127.0.0.1:4723', config)",
            "    driver.implicitly_wait(10)",
            "    ",
            "    try:",
            "        # Generated automation steps"
        ]
        
        for step in workflow_steps:
            target = step.get("target", "").replace("#", "").replace(".", "")
            if step.get("action") == "input":
                script_lines.extend([
                    f"        element = driver.find_element(AppiumBy.ID, '{target}')",
                    f"        element.send_keys('{step.get('value', '')}')"
                ])
            elif step.get("action") == "click":
                script_lines.extend([
                    f"        element = driver.find_element(AppiumBy.ID, '{target}')",
                    "        element.click()"
                ])
        
        script_lines.extend([
            "        ",
            "        print('Mobile automation completed successfully')",
            "    except Exception as e:",
            "        print(f'Mobile automation failed: {e}')",
            "    finally:",
            "        driver.quit()",
            "",
            "if __name__ == '__main__':",
            "    if len(sys.argv) != 2:",
            "        print('Usage: python script.py <device_config.json>')",
            "        sys.exit(1)",
            "    run_automation(sys.argv[1])"
        ])
        
        return "\n".join(script_lines)
    
    def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get Agent2 capabilities"""
        
        return {
            "agent_name": self.agent_name,
            "framework_available": FRAMEWORK_AVAILABLE,
            "langgraph_available": LANGGRAPH_AVAILABLE,
            "tools_count": len(self.tools),
            "initialized": self.initialized,
            "capabilities": [
                "script_generation",
                "code_save",
                "device_configuration",
                "error_handling",
                "agent_communication",
                "collaboration_support"
            ],
            "supported_platforms": ["web", "mobile"],
            "execution_methods": ["tool_based", "fallback"],
            "output_formats": ["python", "requirements", "device_config"]
        }

# Global Agent2 instance
_agent2_instance = None

def get_agent2() -> Agent2CodeGeneration:
    """Get global Agent2 instance"""
    global _agent2_instance
    if _agent2_instance is None:
        _agent2_instance = Agent2CodeGeneration()
    return _agent2_instance

if __name__ == "__main__":
    # Test Agent2 with tool integration
    async def test_agent2_tools():
        print("🧪 Testing Agent2 with Tool Integration...")
        
        agent2 = Agent2CodeGeneration()
        
        # Test capabilities
        capabilities = agent2.get_agent_capabilities()
        print(f"✅ Agent2 capabilities: {capabilities['tools_count']} tools")
        
        # Test initialization
        init_result = await agent2.initialize(999)
        print(f"✅ Agent2 initialization: {init_result.get('success', False)}")
        
        if init_result.get("success", False):
            # Sample blueprint for testing
            sample_blueprint = {
                "ui_elements": [
                    {"element_type": "input", "selector": "#username", "text": "Username"},
                    {"element_type": "input", "selector": "#password", "text": "Password"},
                    {"element_type": "button", "selector": ".login-button", "text": "Login"}
                ],
                "workflow_steps": [
                    {"step_number": 1, "action": "input", "target": "#username", "value": "test_user"},
                    {"step_number": 2, "action": "input", "target": "#password", "value": "test_pass"},
                    {"step_number": 3, "action": "click", "target": ".login-button"}
                ],
                "platform": "web",
                "confidence": 0.8
            }
            
            # Test code generation
            result = await agent2.execute_code_generation(
                task_id=999,
                blueprint=sample_blueprint,
                platform="web"
            )
            print(f"✅ Code generation: {result.get('success', False)}")
            
            if result.get("success", False):
                generated_code = result.get("generated_code", {})
                print(f"✅ Script lines: {generated_code.get('script_content', '').count(chr(10)) + 1}")
                print(f"✅ Requirements: {len(generated_code.get('requirements_content', '').split())}")
                print(f"✅ Files saved: {len(generated_code.get('saved_files', {}))}")
        
        print("🎉 Agent2 tool integration test completed!")
    
    import asyncio
    asyncio.run(test_agent2_tools())