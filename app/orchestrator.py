"""
Multi-Agent Orchestrator - FIXED
Complete orchestrator with proper success key handling
"""
import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import enhanced agents with correct classes
from app.agents.enhanced_agent2 import Agent2CodeGeneration
from app.agents.enhanced_agent3 import Agent3Testing
from app.agents.agent1_blueprint import Agent1Blueprint
from app.agents.agent4_results import Agent4Results

# Import enhanced utilities with error handling
try:
    from app.utils.device_manager import DeviceManager
    from app.utils.terminal_manager import TerminalManager
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    print("⚠️ Enhanced utils not available - using basic functionality")

from app.database.database_manager import get_testing_db

logger = logging.getLogger(__name__)

class MultiAgentOrchestrator:
    """Production Multi-Agent Orchestrator with complete workflow management"""
    
    def __init__(self):
        self.orchestrator_id = f"orchestrator_{int(datetime.now().timestamp())}"
        self.initialized = False
        self.database_manager = None
        self.device_manager = None
        self.terminal_manager = None
        self.model_client = None
        
        logger.info(f"🎯 Multi-Agent Orchestrator initialized: {self.orchestrator_id}")

    async def initialize(self):
        """Initialize orchestrator with all components"""
        try:
            # Initialize database
            self.database_manager = await get_testing_db()
            logger.info("✅ Database manager initialized")
            
            # Initialize terminal manager
            if UTILS_AVAILABLE:
                from app.utils.terminal_manager import get_terminal_manager
                self.terminal_manager = get_terminal_manager()
                logger.info("✅ Terminal manager initialized")
            
            # Initialize device manager  
            if UTILS_AVAILABLE:
                from app.utils.device_manager import get_device_manager
                self.device_manager = get_device_manager()
                logger.info("✅ Device manager initialized")
            
            # Initialize model client
            try:
                from app.utils.model_client import get_model_client
                self.model_client = get_model_client()
                logger.info("✅ Model client initialized")
            except ImportError:
                logger.warning("⚠️ Model client not available")
            
            self.initialized = True
            logger.info("🎯 Orchestrator initialization completed")
            
            return {"success": True, "orchestrator_id": self.orchestrator_id}
            
        except Exception as e:
            logger.error(f"❌ Orchestrator initialization failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def execute_workflow(
        self,
        instruction: str,
        platform: str,
        document_data: bytes = None,
        screenshots: List[bytes] = None,
        additional_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """FIXED: Execute complete workflow with proper success handling"""
        
        if not self.initialized:
            init_result = await self.initialize()
            if not init_result["success"]:
                return init_result
        
        try:
            # Create database task
            task_id = await self.database_manager.create_task(
                instruction, platform, additional_data or {}
            )
            logger.info(f"📝 Created task: {task_id}")
            
            # Execute Agent 1: Blueprint Generation
            logger.info("🔵 Starting Agent 1: Blueprint Generation")
            agent1 = UpdatedAgent1_BlueprintGenerator()
            
            agent1_result = await agent1.generate_blueprint(
                task_id=task_id,
                instruction=instruction,
                platform=platform,
                document_data=document_data,
                screenshot_data=screenshots[0] if screenshots else None
            )
            
            if agent1_result.get("success", False):
                logger.info("✅ Agent 1 completed successfully")
            else:
                logger.error("❌ Agent 1 failed")
                # Continue to finalize workflow even on failure
                
            # Execute Agent 2: Code Generation
            logger.info("🔧 Starting Agent 2: Code Generation")
            agent2 = EnhancedAgent2_CodeGenerator()
            
            agent2_result = await agent2.generate_automation_script(
                task_id=task_id,
                blueprint=agent1_result.get("blueprint", {}),
                platform=platform
            )
            
            if agent2_result.get("success", False):
                logger.info("✅ Agent 2 completed successfully")
            else:
                logger.error("❌ Agent 2 failed")
                
            # Execute Agent 3: Testing & Execution
            logger.info("🧪 Starting Agent 3: Testing & Execution")
            agent3 = EnhancedAgent3_IsolatedTesting()
            
            agent3_result = await agent3.execute_testing_pipeline(
                task_id=task_id,
                script_content=agent2_result.get("script_content", ""),
                requirements_content=agent2_result.get("requirements_content", ""),
                platform=platform
            )
            
            if agent3_result.get("success", False):
                logger.info("✅ Agent 3 completed successfully")
            else:
                logger.error("❌ Agent 3 failed")
                
            # Execute Agent 4: Final Reporting
            logger.info("📊 Starting Agent 4: Final Reporting")
            agent4 = UpdatedAgent4_FinalReporter()
            
            agent4_result = await agent4.generate_final_reports(
                task_id=task_id,
                workflow_data={
                    "agent1_result": agent1_result,
                    "agent2_result": agent2_result,
                    "agent3_result": agent3_result
                }
            )
            
            if agent4_result.get("success", False):
                logger.info("✅ Agent 4 completed successfully")
            else:
                logger.error("❌ Agent 4 failed")
            
            # Finalize workflow
            workflow_id = f"workflow_{task_id}_{int(datetime.now().timestamp())}"
            overall_success = all([
                agent1_result.get("success", False),
                agent2_result.get("success", False),
                agent3_result.get("success", False),
                agent4_result.get("success", False)
            ])
            
            logger.info(f"🎯 Workflow finalized: {workflow_id} - Success: {overall_success}")
            
            # FIXED: Return with both success keys for compatibility
            result = {
                "success": overall_success,  # FIXED: Add this key
                "overall_success": overall_success,  # Keep existing key
                "task_id": task_id,
                "workflow_id": workflow_id,
                "orchestrator_type": "multi_agent",
                "orchestrator_id": self.orchestrator_id,
                "agent_results": {
                    "agent1": agent1_result,
                    "agent2": agent2_result,
                    "agent3": agent3_result,
                    "agent4": agent4_result
                },
                "execution_summary": {
                    "agents_executed": 4,
                    "agents_successful": sum([
                        1 for r in [agent1_result, agent2_result, agent3_result, agent4_result]
                        if r.get("success", False)
                    ]),
                    "workflow_completed": True
                },
                "completed_at": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {str(e)}")
            return {
                "success": False,  # FIXED: Add this key
                "overall_success": False,
                "error": str(e),
                "orchestrator_type": "multi_agent",
                "failed_at": datetime.now().isoformat()
            }

    async def get_workflow_status(self, task_id: int) -> Dict[str, Any]:
        """Get workflow status"""
        if not self.initialized:
            return {"success": False, "error": "Orchestrator not initialized"}
        
        try:
            # Get task info from database
            task_info = await self.database_manager.get_task_info(task_id)
            if not task_info:
                return {"success": False, "error": "Task not found"}
            
            # Get agent executions
            agent_executions = await self.database_manager.get_agent_executions(task_id)
            
            # Get tool executions
            tool_executions = await self.database_manager.get_tool_executions(task_id)
            
            return {
                "success": True,
                "task_id": task_id,
                "task_info": task_info,
                "agent_executions": agent_executions,
                "tool_executions": tool_executions,
                "orchestrator_type": "multi_agent",
                "retrieved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Get workflow status failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_capabilities(self) -> Dict[str, Any]:
        """Get orchestrator capabilities"""
        return {
            "orchestrator_id": self.orchestrator_id,
            "orchestrator_type": "multi_agent",
            "initialized": self.initialized,
            "utils_available": UTILS_AVAILABLE,
            "components": {
                "database_manager": self.database_manager is not None,
                "device_manager": self.device_manager is not None,
                "terminal_manager": self.terminal_manager is not None,
                "model_client": self.model_client is not None
            },
            "agents": [
                "UpdatedAgent1_BlueprintGenerator",
                "EnhancedAgent2_CodeGenerator", 
                "EnhancedAgent3_IsolatedTesting",
                "UpdatedAgent4_FinalReporter"
            ],
            "supported_platforms": ["web", "mobile"],
            "capabilities": [
                "document_analysis",
                "blueprint_generation",
                "code_generation",
                "testing_execution",
                "final_reporting",
                "database_logging",
                "device_management",
                "terminal_management"
            ]
        }


# Global orchestrator instance
_orchestrator = None

async def get_orchestrator() -> MultiAgentOrchestrator:
    """Get global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiAgentOrchestrator()
    return _orchestrator


if __name__ == "__main__":
    # Test orchestrator
    async def test_orchestrator():
        print("🧪 Testing Multi-Agent Orchestrator...")
        
        orchestrator = MultiAgentOrchestrator()
        
        # Test initialization
        init_result = await orchestrator.initialize()
        print(f"🚀 Initialization: {init_result.get('success', False)}")
        
        # Test capabilities
        capabilities = orchestrator.get_capabilities()
        print(f"🔧 Capabilities: {len(capabilities['agents'])} agents available")
        
        if init_result.get("success", False):
            # Test workflow execution
            workflow_result = await orchestrator.execute_workflow(
                instruction="Test automation workflow",
                platform="web",
                document_data=None,
                screenshots=[],
                additional_data={"test": True}
            )
            
            print(f"🔄 Workflow execution: {workflow_result.get('success', False)}")
            if workflow_result.get("success", False):
                print(f"   Task ID: {workflow_result['task_id']}")
                print(f"   Workflow ID: {workflow_result['workflow_id']}")
                print(f"   Agents successful: {workflow_result['execution_summary']['agents_successful']}/4")
        
        print("🎉 Multi-Agent Orchestrator test completed!")
    
    import asyncio
    asyncio.run(test_orchestrator())