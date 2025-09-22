"""
Testing Tools
Agent3 tools for executing scripts and running tests with collaboration support
"""

import json
import logging
import asyncio
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
    from app.utils.terminal_manager import get_terminal_manager
    MANAGERS_AVAILABLE = True
except ImportError as e:
    MANAGERS_AVAILABLE = False
    print(f"⚠️ Managers not available: {str(e)}")

logger = logging.getLogger(__name__)

def _analyze_script_for_issues(script_content: str, platform: str) -> List[Dict[str, Any]]:
    """Analyze script for potential issues"""
    
    issues = []
    lines = script_content.split('\n')
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        
        # Check for common issues
        if platform == "web":
            if "await page.goto(" in line and "wait_until" not in line:
                issues.append({
                    "type": "potential_issue",
                    "line": i,
                    "message": "Navigation without explicit wait strategy",
                    "suggestion": "Add wait_until parameter",
                    "severity": "medium"
                })
            
            if "await page.click(" in line and "wait_for_selector" not in script_content:
                issues.append({
                    "type": "potential_issue", 
                    "line": i,
                    "message": "Click without element wait",
                    "suggestion": "Add wait_for_selector before click",
                    "severity": "high"
                })
        
        elif platform == "mobile":
            if "find_element(" in line and "WebDriverWait" not in script_content:
                issues.append({
                    "type": "potential_issue",
                    "line": i,
                    "message": "Element location without explicit wait",
                    "suggestion": "Add WebDriverWait for better reliability",
                    "severity": "medium"
                })
    
    return issues

def _generate_collaboration_request(
    error_details: Dict[str, Any], 
    script_analysis: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate collaboration request for Agent2"""
    
    return {
        "request_type": "fix_request",
        "error_summary": error_details.get("error_message", "Script execution failed"),
        "error_details": error_details,
        "script_issues": script_analysis,
        "suggested_fixes": [
            {
                "issue_type": issue["type"],
                "line": issue["line"],
                "current_code": issue.get("current_code", ""),
                "suggested_fix": issue["suggestion"],
                "priority": issue["severity"]
            }
            for issue in script_analysis
        ],
        "collaboration_metadata": {
            "requesting_agent": "agent3",
            "target_agent": "agent2",
            "request_timestamp": datetime.now().isoformat(),
            "collaboration_type": "code_fix"
        }
    }

# Agent3 Testing Tools

@tool
async def environment_setup_tool(
    task_id: Annotated[int, "Task ID for database logging"],
    platform: Annotated[str, "Target platform for testing"],
    requirements_content: Annotated[str, "Requirements.txt content"],
    force_recreate: Annotated[bool, "Force recreate virtual environment"] = False
) -> Annotated[Dict[str, Any], "Environment setup results"]:
    """
    Set up testing environment with virtual environment and dependencies.
    Uses the terminal manager's subprocess functionality to create venv.
    """
    
    execution_start = datetime.now()
    tool_input = {
        "task_id": task_id,
        "platform": platform,
        "requirements_size": len(requirements_content.split('\n')),
        "force_recreate": force_recreate
    }
    
    # Log tool execution start
    tool_exec_id = None
    if MANAGERS_AVAILABLE:
        try:
            db_manager = await get_database_manager()
            tool_exec_id = await db_manager.log_tool_execution(
                task_id, "agent3", "environment_setup_tool",
                tool_input, execution_status="running"
            )
        except Exception as e:
            logger.warning(f"Could not log tool execution: {str(e)}")
    
    try:
        # Get output structure manager
        output_manager = OutputStructureManager(task_id)
        testing_path = output_manager.get_agent3_testing_path()
        venv_path = testing_path / "venv"
        requirements_path = testing_path / "requirements.txt"
        
        # Create testing directory structure
        directories = output_manager.create_complete_structure()
        
        # Save requirements to testing directory
        with open(requirements_path, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        # Get terminal manager for venv creation
        if MANAGERS_AVAILABLE:
            terminal_manager = get_terminal_manager()
            
            # Remove existing venv if force_recreate
            if force_recreate and venv_path.exists():
                import shutil
                shutil.rmtree(venv_path)
                logger.info(f"🔄 Removed existing virtual environment: {venv_path}")
            
            # Create virtual environment using terminal manager's subprocess functionality
            venv_result = terminal_manager.create_virtual_environment(str(venv_path))
            
            if not venv_result["success"]:
                raise Exception(f"Virtual environment creation failed: {venv_result.get('error', 'Unknown error')}")
            
            # Install requirements using subprocess
            pip_install_command = f'"{venv_result["pip_executable"]}" install -r "{requirements_path}"'
            install_result = terminal_manager.execute_command_sync(pip_install_command, timeout=300)
            
            if not install_result["success"]:
                logger.warning(f"Requirements installation had issues: {install_result.get('stderr', 'Unknown error')}")
        else:
            # Fallback without terminal manager
            venv_result = {"success": True, "venv_path": str(venv_path)}
            install_result = {"success": True}
        
        setup_result = {
            "environment_ready": venv_result["success"] and install_result["success"],
            "venv_path": str(venv_path),
            "requirements_path": str(requirements_path),
            "python_executable": venv_result.get("python_executable", ""),
            "pip_executable": venv_result.get("pip_executable", ""),
            "platform": platform,
            "setup_metadata": {
                "venv_created": venv_result["success"],
                "requirements_installed": install_result["success"],
                "testing_directory": str(testing_path),
                "setup_timestamp": datetime.now().isoformat()
            }
        }
        
        execution_time = (datetime.now() - execution_start).total_seconds()
        
        # Generate tool review
        tool_review = {
            "environment_setup": setup_result["environment_ready"],
            "venv_creation": venv_result["success"],
            "dependencies_installed": install_result["success"],
            "quality_assessment": "high" if setup_result["environment_ready"] else "medium",
            "recommendations": [
                "Verify all dependencies installed correctly",
                "Test script execution in this environment"
            ]
        }
        
        # Update tool execution in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, setup_result, "success",
                    execution_time, "", tool_review
                )
            except Exception as e:
                logger.warning(f"Could not update tool execution: {str(e)}")
        
        logger.info(f"🔧 Testing environment setup completed: {setup_result['environment_ready']}")
        return setup_result
        
    except Exception as e:
        error_msg = f"Environment setup failed: {str(e)}"
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
            "environment_ready": False,
            "setup_metadata": {
                "setup_failed": True,
                "error_timestamp": datetime.now().isoformat()
            }
        }

@tool
async def script_execution_tool(
    task_id: Annotated[int, "Task ID for database logging"],
    script_content: Annotated[str, "Script content to execute"],
    device_config: Annotated[Dict[str, Any], "Device configuration"],
    environment_info: Annotated[Dict[str, Any], "Environment setup information"],
    platform: Annotated[str, "Target platform"]
) -> Annotated[Dict[str, Any], "Script execution results"]:
    """
    Execute automation script in the testing environment.
    Uses terminal manager's two-terminal flow functionality.
    """
    
    execution_start = datetime.now()
    tool_input = {
        "task_id": task_id,
        "platform": platform,
        "script_size": len(script_content.split('\n')),
        "environment_ready": environment_info.get("environment_ready", False)
    }
    
    # Log tool execution start
    tool_exec_id = None
    if MANAGERS_AVAILABLE:
        try:
            db_manager = await get_database_manager()
            tool_exec_id = await db_manager.log_tool_execution(
                task_id, "agent3", "script_execution_tool",
                tool_input, execution_status="running"
            )
        except Exception as e:
            logger.warning(f"Could not log tool execution: {str(e)}")
    
    try:
        # Get output structure manager
        output_manager = OutputStructureManager(task_id)
        testing_path = output_manager.get_agent3_testing_path()
        script_path = testing_path / "script.py"
        device_config_path = testing_path / "device_config.json"
        requirements_path = testing_path / "requirements.txt"
        venv_path = Path(environment_info.get("venv_path", testing_path / "venv"))
        
        # Save script and device config to testing directory
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        with open(device_config_path, 'w', encoding='utf-8') as f:
            json.dump(device_config, f, indent=2)
        
        # Analyze script for potential issues
        script_issues = _analyze_script_for_issues(script_content, platform)
        
        execution_result = {
            "execution_attempted": True,
            "script_path": str(script_path),
            "device_config_path": str(device_config_path),
            "platform": platform,
            "script_analysis": script_issues,
            "execution_metadata": {
                "script_lines": len(script_content.split('\n')),
                "issues_detected": len(script_issues),
                "execution_timestamp": datetime.now().isoformat()
            }
        }
        
        # Execute script using terminal manager's two-terminal functionality
        if MANAGERS_AVAILABLE:
            terminal_manager = get_terminal_manager()
            
            if platform == "mobile":
                # Use mobile two-terminal flow
                execution_flow_result = terminal_manager.execute_mobile_two_terminal_flow(
                    working_directory=testing_path,
                    venv_path=venv_path,
                    requirements_file=requirements_path,
                    script_path=script_path
                )
            elif platform == "web":
                # Use web two-terminal flow
                execution_flow_result = terminal_manager.execute_web_two_terminal_flow(
                    working_directory=testing_path,
                    venv_path=venv_path,
                    requirements_file=requirements_path,
                    script_path=script_path
                )
            else:
                # Use single terminal fallback
                execution_flow_result = terminal_manager.execute_single_terminal_fallback(
                    str(script_path),
                    str(testing_path),
                    environment_info.get("python_executable")
                )
            
            execution_result.update({
                "terminals_opened": execution_flow_result.get("terminals_opened", 0),
                "execution_method": execution_flow_result.get("approach", "unknown"),
                "terminal_success": execution_flow_result.get("success", False)
            })
            
            # If terminal execution failed, it might be a script issue
            if not execution_flow_result.get("success", False):
                execution_result["execution_status"] = "failed"
                execution_result["needs_collaboration"] = len(script_issues) > 0
            else:
                execution_result["execution_status"] = "launched"
                execution_result["needs_collaboration"] = False
        else:
            # Fallback without terminal manager
            execution_result.update({
                "execution_status": "simulated",
                "terminals_opened": 0,
                "needs_collaboration": len(script_issues) > 0
            })
        
        execution_time = (datetime.now() - execution_start).total_seconds()
        
        # Generate tool review
        tool_review = {
            "script_analyzed": True,
            "issues_found": len(script_issues),
            "execution_attempted": execution_result["execution_attempted"],
            "terminals_launched": execution_result.get("terminals_opened", 0),
            "collaboration_needed": execution_result.get("needs_collaboration", False),
            "quality_assessment": "low" if len(script_issues) > 2 else "medium" if len(script_issues) > 0 else "high"
        }
        
        # Update tool execution in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, execution_result, "success",
                    execution_time, "", tool_review
                )
            except Exception as e:
                logger.warning(f"Could not update tool execution: {str(e)}")
        
        logger.info(f"🧪 Script execution completed: {execution_result['execution_status']}")
        return execution_result
        
    except Exception as e:
        error_msg = f"Script execution failed: {str(e)}"
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
            "execution_status": "error",
            "needs_collaboration": True,
            "execution_metadata": {
                "execution_failed": True,
                "error_timestamp": datetime.now().isoformat()
            }
        }

@tool
async def collaboration_request_tool(
    task_id: Annotated[int, "Task ID for database logging"],
    execution_results: Annotated[Dict[str, Any], "Results from script execution"],
    collaboration_type: Annotated[str, "Type of collaboration needed"] = "fix_request"
) -> Annotated[Dict[str, Any], "Collaboration request details"]:
    """
    Generate collaboration request to Agent2 for script fixes.
    Creates structured request for Agent2 ↔ Agent3 collaboration.
    """
    
    execution_start = datetime.now()
    tool_input = {
        "task_id": task_id,
        "collaboration_type": collaboration_type,
        "issues_count": len(execution_results.get("script_analysis", [])),
        "execution_status": execution_results.get("execution_status", "unknown")
    }
    
    # Log tool execution start
    tool_exec_id = None
    if MANAGERS_AVAILABLE:
        try:
            db_manager = await get_database_manager()
            tool_exec_id = await db_manager.log_tool_execution(
                task_id, "agent3", "collaboration_request_tool",
                tool_input, execution_status="running"
            )
        except Exception as e:
            logger.warning(f"Could not log tool execution: {str(e)}")
    
    try:
        # Generate collaboration request
        collaboration_request = _generate_collaboration_request(
            error_details={
                "execution_status": execution_results.get("execution_status", "failed"),
                "error_message": execution_results.get("error", "Script execution issues detected"),
                "platform": execution_results.get("platform", "unknown")
            },
            script_analysis=execution_results.get("script_analysis", [])
        )
        
        # Save collaboration request to database
        if MANAGERS_AVAILABLE:
            try:
                await db_manager.save_agent_communication_with_langgraph(
                    task_id, "agent3", "agent2", "collaboration_request",
                    json.dumps(collaboration_request),
                    review_data={"collaboration_type": collaboration_type, "issues_count": len(execution_results.get("script_analysis", []))}
                )
            except Exception as e:
                logger.warning(f"Could not save collaboration request: {str(e)}")
        
        execution_time = (datetime.now() - execution_start).total_seconds()
        
        # Generate tool review
        tool_review = {
            "collaboration_initiated": True,
            "request_type": collaboration_type,
            "issues_identified": len(execution_results.get("script_analysis", [])),
            "target_agent": "agent2",
            "quality_assessment": "high"
        }
        
        # Update tool execution in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, collaboration_request, "success",
                    execution_time, "", tool_review
                )
            except Exception as e:
                logger.warning(f"Could not update tool execution: {str(e)}")
        
        logger.info(f"🤝 Collaboration request created: {collaboration_type}")
        return collaboration_request
        
    except Exception as e:
        error_msg = f"Collaboration request failed: {str(e)}"
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
            "collaboration_initiated": False,
            "collaboration_metadata": {
                "request_failed": True,
                "error_timestamp": datetime.now().isoformat()
            }
        }

# Tool collection for Agent3

AGENT3_TESTING_TOOLS = [
    environment_setup_tool,
    script_execution_tool,
    collaboration_request_tool
]

def get_agent3_tools():
    """Get all Agent3 testing tools"""
    return AGENT3_TESTING_TOOLS

if __name__ == "__main__":
    # Test testing tools
    async def test_testing_tools():
        print("🧪 Testing Agent3 Testing Tools...")
        
        # Test environment setup
        requirements_content = "playwright>=1.40.0\nrequests>=2.31.0"
        env_result = await environment_setup_tool(
            999, "web", requirements_content, False
        )
        print(f"✅ Environment setup: {env_result['environment_ready']}")
        
        # Test script execution
        test_script = """
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
        """
        
        test_device_config = {"platform": "web", "browser": "chromium"}
        
        exec_result = await script_execution_tool(
            999, test_script, test_device_config, env_result, "web"
        )
        print(f"✅ Script execution: {exec_result['execution_status']}")
        
        # Test collaboration request if needed
        if exec_result.get("needs_collaboration", False):
            collab_result = await collaboration_request_tool(
                999, exec_result, "fix_request"
            )
            print(f"✅ Collaboration request: {collab_result['collaboration_metadata']['request_timestamp']}")
        
        print("🎉 Agent3 testing tools test completed!")
    
    import asyncio
    asyncio.run(test_testing_tools())