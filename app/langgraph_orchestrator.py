"""
LangGraph Orchestrator - FINAL FIXED VERSION  
FIXES:
- Complete workflow execution coordination
- Proper error handling and recovery
- All original functionality preserved
- Enhanced logging and monitoring
"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Framework imports
try:
    from app.langgraph.workflow_graph import WorkflowGraphManager, get_workflow_graph_manager
    from app.langgraph.workflow_state import create_initial_state
    from app.database.database_manager import get_database_manager
    FRAMEWORK_AVAILABLE = True
except ImportError as e:
    FRAMEWORK_AVAILABLE = False
    print(f"⚠️ Framework components not available: {str(e)}")

logger = logging.getLogger(__name__)

class LangGraphOrchestrator:
    """
    COMPLETELY FIXED LangGraph Orchestrator
    Production orchestrator for complete workflow execution.
    FIXES:
    - All workflow execution flows work correctly
    - Complete error handling and recovery
    - Proper state management
    """

    def __init__(self):
        self.framework_available = FRAMEWORK_AVAILABLE
        logger.info("🎼 FIXED LangGraph Orchestrator initialized")

    async def execute_workflow(
        self,
        task_id: int,
        instruction: str,
        platform: str,
        document_data: Dict[str, Any] = None,
        additional_data: Dict[str, Any] = None,
        screenshots: list = None
    ) -> Dict[str, Any]:
        """Execute complete LangGraph workflow - COMPLETELY FIXED"""
        
        if not self.framework_available:
            logger.warning("⚠️ LangGraph framework not available, using fallback")
            return {
                "success": False,
                "error": "LangGraph framework not available",
                "task_id": task_id,
                "fallback": True
            }

        execution_start = datetime.now()
        
        try:
            logger.info(f"🚀 Starting LangGraph workflow execution for task {task_id}")
            
            # Get workflow graph manager
            workflow_manager = get_workflow_graph_manager(task_id)
            
            # Create initial workflow state - FIXED
            initial_state = await create_initial_state(
                task_id=task_id,
                instruction=instruction,
                platform=platform,
                document_data=document_data or {},
                additional_data=additional_data or {},
                screenshots=screenshots or []
            )
            
            logger.info(f"📊 Initial state created with {len(initial_state)} keys")
            
            # Execute workflow through graph manager - FIXED
            result = await workflow_manager.execute_workflow(initial_state)
            
            execution_time = (datetime.now() - execution_start).total_seconds()
            
            if result.get("success"):
                logger.info(f"🎉 LangGraph workflow completed successfully: {result.get('execution_steps', 0)} steps")
                return {
                    "success": True,
                    "task_id": task_id,
                    "execution_time": execution_time,
                    "workflow_result": result,
                    "final_state": result.get("final_state", {}),
                    "execution_steps": result.get("execution_steps", 0),
                    "completed_at": datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ LangGraph workflow failed: {result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "task_id": task_id,
                    "execution_time": execution_time,
                    "error": result.get("error", "Workflow execution failed"),
                    "workflow_result": result,
                    "failed_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            execution_time = (datetime.now() - execution_start).total_seconds()
            logger.error(f"❌ LangGraph workflow execution failed: {str(e)}")
            
            return {
                "success": False,
                "task_id": task_id,
                "execution_time": execution_time,
                "error": str(e),
                "error_type": type(e).__name__,
                "failed_at": datetime.now().isoformat()
            }

    async def get_workflow_status(self, task_id: int, thread_id: str = None) -> Dict[str, Any]:
        """Get workflow execution status - FIXED"""
        try:
            if not self.framework_available:
                return {
                    "success": False,
                    "error": "LangGraph framework not available",
                    "task_id": task_id
                }
            
            workflow_manager = get_workflow_graph_manager(task_id)
            
            if thread_id:
                state_result = await workflow_manager.get_workflow_state(thread_id)
                return {
                    "success": True,
                    "task_id": task_id,
                    "thread_id": thread_id,
                    "state": state_result,
                    "retrieved_at": datetime.now().isoformat()
                }
            else:
                graph_info = workflow_manager.get_graph_info()
                return {
                    "success": True,
                    "task_id": task_id,
                    "graph_info": graph_info,
                    "retrieved_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get workflow status: {str(e)}")
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }

    async def resume_workflow(self, task_id: int, thread_id: str, checkpoint_id: str = None) -> Dict[str, Any]:
        """Resume workflow from checkpoint - FIXED"""
        try:
            if not self.framework_available:
                return {
                    "success": False,
                    "error": "LangGraph framework not available",
                    "task_id": task_id
                }
            
            workflow_manager = get_workflow_graph_manager(task_id)
            result = await workflow_manager.resume_workflow(thread_id, checkpoint_id)
            
            logger.info(f"🔄 Workflow resume result for task {task_id}: {result.get('success')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to resume workflow: {str(e)}")
            return {
                "success": False,
                "task_id": task_id,
                "thread_id": thread_id,
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "framework_available": self.framework_available,
            "components": {
                "workflow_graph": FRAMEWORK_AVAILABLE,
                "workflow_state": FRAMEWORK_AVAILABLE,
                "database": FRAMEWORK_AVAILABLE
            },
            "status_checked_at": datetime.now().isoformat()
        }

    def cleanup_workflows(self) -> Dict[str, Any]:
        """Cleanup workflow resources"""
        try:
            from app.langgraph.workflow_graph import cleanup_graph_managers
            result = cleanup_graph_managers()
            logger.info(f"🧹 FIXED Workflow cleanup completed: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ Workflow cleanup failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }


# Global orchestrator instance
_orchestrator = None

def get_langgraph_orchestrator() -> LangGraphOrchestrator:
    """Get LangGraph orchestrator (singleton)"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = LangGraphOrchestrator()
    return _orchestrator