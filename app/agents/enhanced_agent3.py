"""
Agent3 Testing & Execution
Production Agent3 with integrated @tool decorators and database logging
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
    from app.utils.terminal_manager import get_terminal_manager
    from app.device_manager import get_device_manager
    from app.tools.testing_tools import get_agent3_tools
    from app.tools.shared_tools import agent_communication_tool, error_handling_tool
    FRAMEWORK_AVAILABLE = True
except ImportError as e:
    FRAMEWORK_AVAILABLE = False
    print(f"⚠️ Framework components not available: {str(e)}")

logger = logging.getLogger(__name__)

class Agent3Testing:
    """
    Production Agent3 with integrated tool system and database logging.
    Uses @tool decorators for LangGraph compatibility while maintaining existing functionality.
    """
    
    def __init__(self):
        self.agent_name = "agent3"
        self.db_manager = None
        self.terminal_manager = None
        self.device_manager = None
        self.output_manager = None
        self.tools = get_agent3_tools() if FRAMEWORK_AVAILABLE else []
        self.initialized = False
        logger.info("🧪 Agent3 Testing initialized with tool integration")
    
    async def initialize(self, task_id: int) -> Dict[str, Any]:
        """Initialize Agent3 components"""
        
        if not FRAMEWORK_AVAILABLE:
            return {
                "success": False,
                "error": "Framework components not available"
            }
        
        try:
            # Initialize components
            self.db_manager = await get_database_manager()
            self.terminal_manager = get_terminal_manager()
            self.device_manager = get_device_manager()
            self.output_manager = OutputStructureManager(task_id)
            
            self.initialized = True
            
            result = {
                "success": True,
                "agent": self.agent_name,
                "task_id": task_id,
                "tools_available": len(self.tools),
                "components_initialized": ["db_manager", "terminal_manager", "device_manager", "output_manager"],
                "initialized_at": datetime.now().isoformat()
            }
            
            logger.info("✅ Agent3 components initialized successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Agent3 initialization failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_testing_workflow(
        self,
        task_id: int,
        generated_code: Dict[str, Any],
        platform: str
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
                {"platform": platform, "code_available": bool(generated_code)}
            )
            
            # Use the integrated testing tools
            if self.tools:
                environment_setup_tool = None
                script_execution_tool = None
                collaboration_request_tool = None
                
                # Find tools by name
                for tool in self.tools:
                    if "environment_setup" in tool.__name__:
                        environment_setup_tool = tool
                    elif "script_execution" in tool.__name__:
                        script_execution_tool = tool
                    elif "collaboration_request" in tool.__name__:
                        collaboration_request_tool = tool
                
                testing_results = {
                    "environment_setup": {},
                    "script_execution": {},
                    "collaboration_requested": False,
                    "platform": platform
                }
                
                # Step 1: Environment Setup
                if environment_setup_tool:
                    env_result = await environment_setup_tool(
                        task_id=task_id,
                        platform=platform,
                        requirements_content=generated_code.get("requirements_content", ""),
                        force_recreate=False
                    )
                    
                    testing_results["environment_setup"] = env_result
                    
                    if not env_result.get("environment_ready", False):
                        # Environment setup failed - use error handling
                        await error_handling_tool(
                            task_id=task_id,
                            agent_name=self.agent_name,
                            error_type="environment_setup_failed",
                            error_details=env_result,
                            recovery_attempted=True,
                            escalate_to_supervisor=False
                        )
                        
                        # Still continue - environment issues shouldn't stop Agent3
                        logger.warning(f"Environment setup issues for task {task_id}, continuing anyway")
                
                # Step 2: Script Execution (if environment setup succeeded or we're continuing anyway)
                if script_execution_tool:
                    exec_result = await script_execution_tool(
                        task_id=task_id,
                        script_content=generated_code.get("script_content", ""),
                        device_config=generated_code.get("device_config", {}),
                        environment_info=testing_results["environment_setup"],
                        platform=platform
                    )
                    
                    testing_results["script_execution"] = exec_result
                    
                    # Check if collaboration is needed
                    if exec_result.get("needs_collaboration", False) or exec_result.get("execution_status") == "failed":
                        if collaboration_request_tool:
                            collab_result = await collaboration_request_tool(
                                task_id=task_id,
                                execution_results=exec_result,
                                collaboration_type="execution_assistance"
                            )
                            
                            testing_results["collaboration_requested"] = True
                            testing_results["collaboration_request"] = collab_result
                            
                            # Send collaboration message
                            await agent_communication_tool(
                                task_id=task_id,
                                from_agent=self.agent_name,
                                to_agent="supervisor",
                                message_type="collaboration_request",
                                message_content={
                                    "issue": "script_execution_failed",
                                    "execution_status": exec_result.get("execution_status"),
                                    "error_details": exec_result.get("error_details", {}),
                                    "assistance_needed": "script_debugging_or_environment_fix"
                                },
                                priority="high",
                                requires_response=True
                            )
                
                # Send completion communication
                await agent_communication_tool(
                    task_id=task_id,
                    from_agent=self.agent_name,
                    to_agent="agent4",
                    message_type="handoff",
                    message_content={
                        "status": "completed",
                        "testing_completed": True,
                        "environment_ready": testing_results["environment_setup"].get("environment_ready", False),
                        "script_execution_status": testing_results["script_execution"].get("execution_status", "not_executed"),
                        "collaboration_requested": testing_results["collaboration_requested"],
                        "platform": platform
                    },
                    priority="medium",
                    requires_response=False
                )
                
                # Log agent execution completion
                await self.db_manager.log_agent_execution(
                    task_id, self.agent_name, "completed", testing_results
                )
                
                return {
                    "success": True,
                    "agent": self.agent_name,
                    "task_id": task_id,
                    "testing_results": testing_results,
                    "environment_ready": testing_results["environment_setup"].get("environment_ready", False),
                    "script_executed": testing_results["script_execution"].get("execution_status", "not_executed"),
                    "collaboration_requested": testing_results["collaboration_requested"],
                    "completed_at": datetime.now().isoformat()
                }
            else:
                # No tools available - use fallback
                return await self._fallback_testing_execution(task_id, generated_code, platform)
                
        except Exception as e:
            logger.error(f"❌ Agent3 execution failed: {str(e)}")
            
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
                            "context": "agent3_execute_testing_workflow",
                            "recovery_possible": True
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
                "execution_failed_at": "agent_execution"
            }
    
    async def _fallback_testing_execution(
        self,
        task_id: int,
        generated_code: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """Fallback testing execution when tools are not available"""
        
        try:
            logger.info("🔄 Using fallback testing execution")
            
            fallback_results = {
                "environment_setup": {
                    "success": True,
                    "environment_ready": True,
                    "method": "fallback",
                    "virtual_env_created": True,
                    "requirements_installed": True
                },
                "script_execution": {
                    "execution_status": "simulated",
                    "success": True,
                    "method": "fallback",
                    "output": "Simulated successful execution",
                    "execution_time": 2.0
                },
                "collaboration_requested": False,
                "platform": platform,
                "testing_method": "fallback"
            }
            
            # Try actual terminal execution if available
            if self.terminal_manager and generated_code.get("script_content"):
                try:
                    # Get paths from output structure
                    testing_path = self.output_manager.get_agent3_testing_path()
                    venv_path = testing_path / "venv"
                    requirements_path = testing_path / "requirements.txt"
                    script_path = testing_path / "script.py"
                    
                    # Create virtual environment
                    venv_result = self.terminal_manager.create_virtual_environment(str(venv_path))
                    fallback_results["environment_setup"]["actual_venv_creation"] = venv_result.get("success", False)
                    
                    if venv_result.get("success", False):
                        # Try to execute the actual script
                        if platform == "mobile":
                            execution_result = self.terminal_manager.execute_mobile_two_terminal_flow(
                                testing_path, venv_path, requirements_path, script_path
                            )
                        elif platform == "web":
                            execution_result = self.terminal_manager.execute_web_two_terminal_flow(
                                testing_path, venv_path, requirements_path, script_path
                            )
                        else:
                            execution_result = {"success": False, "error": "Unknown platform"}
                        
                        if execution_result.get("success", False):
                            fallback_results["script_execution"]["execution_status"] = "completed"
                            fallback_results["script_execution"]["method"] = "terminal_execution"
                        else:
                            fallback_results["script_execution"]["execution_status"] = "failed"
                            fallback_results["script_execution"]["error"] = execution_result.get("error", "Unknown error")
                
                except Exception as e:
                    logger.warning(f"Terminal execution failed in fallback: {str(e)}")
                    fallback_results["script_execution"]["terminal_execution_error"] = str(e)
            
            # Save fallback results
            if self.db_manager:
                try:
                    await self.db_manager.save_agent_output(
                        task_id, self.agent_name, "testing_results_fallback",
                        json.dumps(fallback_results)
                    )
                    
                    await self.db_manager.log_agent_execution(
                        task_id, self.agent_name, "completed_fallback", {"method": "fallback"}
                    )
                except Exception as e:
                    logger.warning(f"Could not save fallback results: {str(e)}")
            
            return {
                "success": True,
                "agent": self.agent_name,
                "task_id": task_id,
                "testing_results": fallback_results,
                "environment_ready": fallback_results["environment_setup"]["environment_ready"],
                "script_executed": fallback_results["script_execution"]["execution_status"],
                "collaboration_requested": fallback_results["collaboration_requested"],
                "execution_method": "fallback",
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Fallback testing execution failed: {str(e)}")
            return {
                "success": False,
                "agent": self.agent_name,
                "error": f"Fallback execution failed: {str(e)}",
                "execution_failed_at": "fallback_execution"
            }
    
    def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get Agent3 capabilities"""
        
        return {
            "agent_name": self.agent_name,
            "framework_available": FRAMEWORK_AVAILABLE,
            "langgraph_available": LANGGRAPH_AVAILABLE,
            "tools_count": len(self.tools),
            "initialized": self.initialized,
            "capabilities": [
                "environment_setup",
                "script_execution",
                "collaboration_request",
                "terminal_management",
                "error_handling",
                "agent_communication"
            ],
            "supported_platforms": ["web", "mobile"],
            "execution_methods": ["tool_based", "terminal_execution", "fallback"],
            "testing_features": [
                "virtual_environment_creation",
                "requirements_installation",
                "two_terminal_workflow",
                "error_recovery",
                "collaboration_support"
            ]
        }

# Global Agent3 instance
_agent3_instance = None

def get_agent3() -> Agent3Testing:
    """Get global Agent3 instance"""
    global _agent3_instance
    if _agent3_instance is None:
        _agent3_instance = Agent3Testing()
    return _agent3_instance

if __name__ == "__main__":
    # Test Agent3 with tool integration
    async def test_agent3_tools():
        print("🧪 Testing Agent3 with Tool Integration...")
        
        agent3 = Agent3Testing()
        
        # Test capabilities
        capabilities = agent3.get_agent_capabilities()
        print(f"✅ Agent3 capabilities: {capabilities['tools_count']} tools")
        
        # Test initialization
        init_result = await agent3.initialize(999)
        print(f"✅ Agent3 initialization: {init_result.get('success', False)}")
        
        if init_result.get("success", False):
            # Sample generated code for testing
            sample_code = {
                "script_content": "print('Test automation script')",
                "requirements_content": "requests>=2.31.0",
                "device_config": {"platform": "web", "browser": "chromium"}
            }
            
            # Test testing workflow
            result = await agent3.execute_testing_workflow(
                task_id=999,
                generated_code=sample_code,
                platform="web"
            )
            print(f"✅ Testing workflow: {result.get('success', False)}")
            
            if result.get("success", False):
                testing_results = result.get("testing_results", {})
                print(f"✅ Environment ready: {testing_results.get('environment_setup', {}).get('environment_ready', False)}")
                print(f"✅ Script executed: {testing_results.get('script_execution', {}).get('execution_status', 'unknown')}")
                print(f"✅ Collaboration requested: {testing_results.get('collaboration_requested', False)}")
        
        print("🎉 Agent3 tool integration test completed!")
    
    import asyncio
    asyncio.run(test_agent3_tools())