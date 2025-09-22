"""
Code Generation Tools
Agent2 tools for generating automation scripts, requirements, and device configurations
"""

import json
import logging
from typing import Dict, Any, List, Optional, Annotated
from datetime import datetime
from pathlib import Path

# @tool decorator
try:
    from langchain_core.tools import tool
    TOOL_DECORATOR_AVAILABLE = True
    print("✅ LangGraph @tool decorator available")
except ImportError as e:
    TOOL_DECORATOR_AVAILABLE = False
    print(f"⚠️ LangGraph @tool decorator not available: {str(e)}")
    def tool(func):
        func._is_tool = True
        return func

# Managers
try:
    from app.database.database_manager import get_database_manager
    from app.utils.output_structure_manager import OutputStructureManager
    MANAGERS_AVAILABLE = True
except ImportError as e:
    MANAGERS_AVAILABLE = False
    print(f"⚠️ Managers not available: {str(e)}")

logger = logging.getLogger(__name__)

def _generate_web_script(workflow_steps: List[Dict[str, Any]], platform_config: Dict[str, Any]) -> str:
    """Generate Playwright web automation script"""
    
    header = [
        "import asyncio",
        "import json",
        "import time",
        "from pathlib import Path",
        "from playwright.async_api import async_playwright, Browser, Page, BrowserContext",
        "",
        "async def run_automation():",
        "    \"\"\"Generated web automation script\"\"\"",
        "    async with async_playwright() as playwright:",
        f"        browser = await playwright.chromium.launch(headless={platform_config.get('headless', False)})",
        "        context = await browser.new_context(",
        f"            viewport={{'width': {platform_config.get('viewport_width', 1280)}, 'height': {platform_config.get('viewport_height', 800)}}}",
        "        )",
        "        page = await context.new_page()",
        "        ",
        "        try:"
    ]
    
    body = []
    for i, step in enumerate(workflow_steps, 1):
        action = step.get("action", "")
        target = step.get("target", "")
        value = step.get("value", "")
        description = step.get("description", "")
        
        body.append(f"            # Step {i}: {description}")
        
        if action == "navigate":
            body.append(f"            await page.goto('{target}', wait_until='domcontentloaded')")
            body.append(f"            await page.wait_for_load_state('networkidle')")
        elif action == "input":
            body.append(f"            await page.wait_for_selector('{target}', timeout=10000)")
            body.append(f"            await page.fill('{target}', '{value}')")
        elif action == "click":
            body.append(f"            await page.wait_for_selector('{target}', timeout=10000)")
            body.append(f"            await page.click('{target}')")
        elif action == "verify":
            body.append("            await page.wait_for_load_state('networkidle')")
            body.append("            await page.screenshot(path='automation_result.png')")
        
        body.append("            await asyncio.sleep(1)  # Wait between actions")
        body.append("")
    
    footer = [
        "            print('✅ Automation completed successfully')",
        "            ",
        "        except Exception as e:",
        "            print(f'❌ Automation failed: {str(e)}')",
        "            await page.screenshot(path='error_screenshot.png')",
        "            raise",
        "        finally:",
        "            await context.close()",
        "            await browser.close()",
        "",
        "if __name__ == '__main__':",
        "    asyncio.run(run_automation())"
    ]
    
    return "\\n".join(header + body + footer)

def _generate_mobile_script(workflow_steps: List[Dict[str, Any]], platform_config: Dict[str, Any]) -> str:
    """Generate Appium mobile automation script"""
    
    header = [
        "import json",
        "import time",
        "import sys",
        "from pathlib import Path",
        "from appium import webdriver",
        "from appium.webdriver.common.appiumby import AppiumBy",
        "",
        "def run_automation(device_config_path):",
        "    \"\"\"Generated mobile automation script\"\"\"",
        "    # Load device configuration",
        "    with open(device_config_path, 'r', encoding='utf-8') as f:",
        "        config = json.load(f)",
        "    ",
        "    device_caps = config.get('selected_device', {}).get('capabilities', config)",
        "    ",
        "    driver = webdriver.Remote('http://127.0.0.1:4723', device_caps)",
        "    driver.implicitly_wait(10)",
        "    ",
        "    try:"
    ]
    
    body = []
    for i, step in enumerate(workflow_steps, 1):
        action = step.get("action", "")
        target = step.get("target", "")
        value = step.get("value", "")
        description = step.get("description", "")
        
        body.append(f"        # Step {i}: {description}")
        
        if action == "input":
            body.append(f"        element = driver.find_element(AppiumBy.XPATH, \"//*[@resource-id='{target}' or @text='{target}' or contains(@content-desc, '{target}')]\")")
            body.append("        element.clear()")
            body.append(f"        element.send_keys('{value}')")
        elif action == "click":
            body.append(f"        element = driver.find_element(AppiumBy.XPATH, \"//*[@resource-id='{target}' or @text='{target}' or contains(@content-desc, '{target}')]\")")
            body.append("        element.click()")
        elif action == "verify":
            body.append("        time.sleep(2)  # Wait for verification")
            body.append("        driver.save_screenshot('automation_result.png')")
        
        body.append("        time.sleep(1)  # Wait between actions")
        body.append("")
    
    footer = [
        "        print('✅ Mobile automation completed successfully')",
        "        ",
        "    except Exception as e:",
        "        print(f'❌ Mobile automation failed: {str(e)}')",
        "        driver.save_screenshot('error_screenshot.png')",
        "        raise",
        "    finally:",
        "        driver.quit()",
        "",
        "if __name__ == '__main__':",
        "    if len(sys.argv) != 2:",
        "        print('Usage: python script.py <device_config.json>')",
        "        sys.exit(1)",
        "    run_automation(sys.argv[1])"
    ]
    
    return "\\n".join(header + body + footer)

def _generate_requirements(platform: str, additional_packages: List[str] = None) -> str:
    """Generate requirements.txt based on platform"""
    
    base_requirements = [
        "# Generated requirements for automation",
        "requests>=2.31.0",
        "aiohttp>=3.9.0"
    ]
    
    if platform == "web":
        base_requirements.extend([
            "# Web automation requirements",
            "playwright>=1.40.0",
            "asyncio-mqtt>=0.13.0"
        ])
    elif platform == "mobile":
        base_requirements.extend([
            "# Mobile automation requirements",
            "Appium-Python-Client>=3.1.0",
            "uiautomator2>=3.0.0"
        ])
    
    if additional_packages:
        base_requirements.extend([
            "# Additional packages",
            *additional_packages
        ])
    
    return "\\n".join(base_requirements)

def _generate_device_config(platform: str, device_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate device configuration"""
    
    if platform == "web":
        return {
            "platform": "web",
            "browser_config": {
                "browser_type": "chromium",
                "headless": False,
                "viewport": {
                    "width": 1280,
                    "height": 800
                },
                "timeout": 30000
            },
            "automation_settings": {
                "wait_strategy": "explicit",
                "retry_attempts": 3,
                "screenshot_on_error": True
            }
        }
    elif platform == "mobile":
        return {
            "platform": "mobile",
            "selected_device": {
                "device_name": device_info.get("device_name", "Android Device") if device_info else "Android Device",
                "capabilities": {
                    "platformName": "Android",
                    "platformVersion": device_info.get("platform_version", "11") if device_info else "11",
                    "deviceName": device_info.get("device_id", "emulator-5554") if device_info else "emulator-5554",
                    "automationName": "UiAutomator2",
                    "newCommandTimeout": 300,
                    "noReset": True
                }
            },
            "automation_settings": {
                "implicit_wait": 10,
                "retry_attempts": 3,
                "screenshot_on_error": True
            }
        }
    
    return {"platform": platform, "config": "auto-detect"}

# Agent2 Code Tools

@tool
async def script_generation_tool(
    task_id: Annotated[int, "Task ID for database logging"],
    blueprint: Annotated[Dict[str, Any], "Workflow blueprint from Agent1"],
    platform: Annotated[str, "Target platform"],
    device_info: Annotated[Optional[Dict[str, Any]], "Device information if available"] = None
) -> Annotated[Dict[str, Any], "Generated script and configuration"]:
    """
    Generate automation script from blueprint.
    Creates platform-specific automation code with proper error handling.
    """
    
    execution_start = datetime.now()
    tool_input = {
        "task_id": task_id,
        "platform": platform,
        "workflow_steps": len(blueprint.get("workflow_steps", [])),
        "device_info": device_info
    }
    
    # Log tool execution start
    tool_exec_id = None
    if MANAGERS_AVAILABLE:
        try:
            db_manager = await get_database_manager()
            tool_exec_id = await db_manager.log_tool_execution(
                task_id, "agent2", "script_generation_tool",
                tool_input, execution_status="running"
            )
        except Exception as e:
            logger.warning(f"Could not log tool execution: {str(e)}")
    
    try:
        workflow_steps = blueprint.get("workflow_steps", [])
        platform_config = blueprint.get("automation_config", {})
        
        # Generate script based on platform
        if platform == "web":
            script_content = _generate_web_script(workflow_steps, platform_config)
        elif platform == "mobile":
            script_content = _generate_mobile_script(workflow_steps, platform_config)
        else:
            script_content = _generate_web_script(workflow_steps, platform_config)  # Default to web
        
        # Generate requirements
        requirements_content = _generate_requirements(platform)
        
        # Generate device configuration
        device_config = _generate_device_config(platform, device_info)
        
        # Create OCR templates if UI elements are present
        ocr_templates = []
        ui_elements = blueprint.get("ui_elements", [])
        for element in ui_elements:
            ocr_template = {
                "element_type": element.get("element_type"),
                "selector": element.get("selector"),
                "coordinates": element.get("coordinates", {}),
                "confidence": element.get("confidence", 0.8),
                "template_id": f"template_{len(ocr_templates) + 1}",
                "platform": platform
            }
            ocr_templates.append(ocr_template)
        
        generation_result = {
            "script_content": script_content,
            "requirements_content": requirements_content,
            "device_config": device_config,
            "ocr_templates": ocr_templates,
            "generation_metadata": {
                "platform": platform,
                "steps_generated": len(workflow_steps),
                "script_lines": len(script_content.split("\\n")),
                "ocr_templates_count": len(ocr_templates),
                "generated_at": datetime.now().isoformat()
            }
        }
        
        execution_time = (datetime.now() - execution_start).total_seconds()
        
        # Generate tool review
        tool_review = {
            "script_generated": True,
            "platform": platform,
            "steps_processed": len(workflow_steps),
            "script_complexity": "simple" if len(workflow_steps) <= 3 else "medium" if len(workflow_steps) <= 6 else "complex",
            "quality_assessment": "high",
            "recommendations": [
                "Test script in target environment",
                "Adjust timeouts based on application performance"
            ]
        }
        
        # Update tool execution in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, generation_result, "success",
                    execution_time, "", tool_review
                )
            except Exception as e:
                logger.warning(f"Could not update tool execution: {str(e)}")
        
        logger.info(f"🔧 Script generated: {platform} - {len(workflow_steps)} steps")
        return generation_result
        
    except Exception as e:
        error_msg = f"Script generation failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # Log error in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, None, "failed",
                    (datetime.now() - execution_start).total_seconds(), error_msg, {}
                )
            except Exception as db_error:
                logger.warning(f"Could not log tool error: {str(db_error)}")
        
        return {
            "error": error_msg,
            "generation_metadata": {
                "platform": platform,
                "steps_generated": 0,
                "generation_failed": True
            }
        }

@tool
async def code_save_tool(
    task_id: Annotated[int, "Task ID for database logging and output structure"],
    generated_code: Annotated[Dict[str, Any], "Generated code from script_generation_tool"],
    save_ocr_templates: Annotated[bool, "Whether to save OCR templates"] = True
) -> Annotated[Dict[str, str], "Paths where code files were saved"]:
    """
    Save generated code to exact output structure: generated_code/{task_id}/agent2/
    Saves script.py, requirements.txt, device_config.json, and OCR templates.
    """
    
    execution_start = datetime.now()
    tool_input = {
        "task_id": task_id,
        "has_script": "script_content" in generated_code,
        "has_requirements": "requirements_content" in generated_code,
        "has_device_config": "device_config" in generated_code,
        "ocr_templates_count": len(generated_code.get("ocr_templates", [])),
        "save_ocr_templates": save_ocr_templates
    }
    
    # Log tool execution start
    tool_exec_id = None
    if MANAGERS_AVAILABLE:
        try:
            db_manager = await get_database_manager()
            tool_exec_id = await db_manager.log_tool_execution(
                task_id, "agent2", "code_save_tool",
                tool_input, execution_status="running"
            )
        except Exception as e:
            logger.warning(f"Could not log tool execution: {str(e)}")
    
    try:
        # Initialize output structure manager
        output_manager = OutputStructureManager(task_id)
        
        # Create directory structure
        directories = output_manager.create_complete_structure()
        
        # Save Agent2 outputs
        saved_files = output_manager.save_agent2_outputs(
            script_content=generated_code.get("script_content", "# No script generated"),
            requirements_content=generated_code.get("requirements_content", "# No requirements generated"),
            device_config=generated_code.get("device_config", {}),
            ocr_templates=generated_code.get("ocr_templates", []) if save_ocr_templates else None
        )
        
        execution_time = (datetime.now() - execution_start).total_seconds()
        
        # Log output files to database
        if MANAGERS_AVAILABLE:
            try:
                for file_category, file_path in saved_files.items():
                    if file_category == "ocr_logs":
                        # OCR logs is a list of files
                        for ocr_file in file_path:
                            file_name = Path(ocr_file).name
                            file_size = Path(ocr_file).stat().st_size
                            await db_manager.log_output_file(
                                task_id, "agent2", file_name, ocr_file,
                                "ocr_template", file_size, "",
                                {"saved_by": "code_save_tool", "category": "ocr_logs"}
                            )
                    else:
                        file_name = Path(file_path).name
                        file_size = Path(file_path).stat().st_size
                        
                        # Get content preview for text files
                        content_preview = ""
                        if file_name.endswith(('.py', '.txt', '.json')):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                content_preview = content[:500] + "..." if len(content) > 500 else content
                        
                        await db_manager.log_output_file(
                            task_id, "agent2", file_name, file_path,
                            file_category, file_size, content_preview,
                            {"saved_by": "code_save_tool", "category": file_category}
                        )
            except Exception as e:
                logger.warning(f"Could not log output files: {str(e)}")
        
        # Generate tool review
        tool_review = {
            "files_saved": len([f for f in saved_files.values() if isinstance(f, str)]) + len(saved_files.get("ocr_logs", [])),
            "script_saved": "script" in saved_files,
            "requirements_saved": "requirements" in saved_files,
            "config_saved": "device_config" in saved_files,
            "ocr_templates_saved": len(saved_files.get("ocr_logs", [])),
            "save_success": True
        }
        
        # Update tool execution in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, saved_files, "success",
                    execution_time, "", tool_review
                )
            except Exception as e:
                logger.warning(f"Could not update tool execution: {str(e)}")
        
        logger.info(f"💾 Code files saved successfully: {len(saved_files)} categories")
        return saved_files
        
    except Exception as e:
        error_msg = f"Code save failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # Log error in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, None, "failed",
                    (datetime.now() - execution_start).total_seconds(), error_msg, {}
                )
            except Exception as db_error:
                logger.warning(f"Could not log tool error: {str(db_error)}")
        
        return {"error": error_msg}

# Tool collection for Agent2

AGENT2_CODE_TOOLS = [
    script_generation_tool,
    code_save_tool
]

def get_agent2_tools():
    """Get all Agent2 code generation tools"""
    return AGENT2_CODE_TOOLS

if __name__ == "__main__":
    # Test code generation tools
    async def test_code_tools():
        print("🧪 Testing Code Generation Tools...")
        
        # Test blueprint
        test_blueprint = {
            "workflow_steps": [
                {"action": "navigate", "target": "https://example.com", "description": "Navigate to example"},
                {"action": "input", "target": "#username", "value": "test_user", "description": "Enter username"},
                {"action": "click", "target": ".login-button", "description": "Click login"}
            ],
            "ui_elements": [
                {"element_type": "input", "selector": "#username", "confidence": 0.9},
                {"element_type": "button", "selector": ".login-button", "confidence": 0.95}
            ],
            "automation_config": {"platform": "web", "headless": False}
        }
        
        # Test script generation
        generation_result = await script_generation_tool(
            999, test_blueprint, "web"
        )
        print(f"✅ Script generation: {generation_result['generation_metadata']['steps_generated']} steps")
        
        # Test code save
        save_result = await code_save_tool(
            999, generation_result, True
        )
        print(f"✅ Code save: {len(save_result)} files saved")
        
        print("🎉 Code generation tools test completed!")
    
    import asyncio
    asyncio.run(test_code_tools())