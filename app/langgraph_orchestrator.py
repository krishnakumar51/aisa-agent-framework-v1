"""
LangGraph-Based Multi-Agent Orchestrator
State-driven workflow with proper agent communication and testing environment
"""
import asyncio
import json
import logging
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from typing_extensions import Literal

# LangGraph imports for state management and workflow
try:
    from langgraph.graph import StateGraph, START, END
    from langgraph.graph.message import add_messages
    from langgraph.prebuilt import ToolExecutor, tools_condition
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("⚠️  LangGraph not available. Install with: pip install langgraph")


try:
    from langgraph_checkpoint_sqlite import SqliteSaver
except ImportError:
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
    except ImportError:
        print("⚠️ SqliteSaver not available")
        SqliteSaver = None


# Import database and agents
from app.database.database_manager import get_testing_db
from app.agents.agent1_blueprint import UpdatedAgent1_BlueprintGenerator
from app.agents.agent2_code import UpdatedAgent2_CodeGenerator
from app.agents.agent3_testing import UpdatedAgent3_TestingEnvironment
from app.agents.agent4_results import UpdatedAgent4_FinalReporter

# Import existing automation tools
from app.drivers.playwright_driver import playwright_driver
from app.drivers.appium_driver import appium_driver
from app.tools.web_tools import web_tools
from app.tools.mobile_tools import mobile_tools
from app.utils.ocr_utils import ocr_processor

logger = logging.getLogger(__name__)

# LangGraph State Schema
class AutomationState(TypedDict):
    """State schema for the automation workflow"""
    # Task metadata
    seq_id: Optional[int]
    instruction: str
    platform: str
    base_path: Optional[str]
    
    # Document and media inputs
    document_content: bytes
    screenshots: List[bytes]
    additional_data: Optional[Dict[str, Any]]
    
    # Agent results and communication
    agent1_result: Optional[Dict[str, Any]]
    agent2_result: Optional[Dict[str, Any]]
    agent3_result: Optional[Dict[str, Any]]
    agent4_result: Optional[Dict[str, Any]]
    
    # Inter-agent messages for communication
    messages: Annotated[List[Dict[str, Any]], add_messages]
    
    # Workflow status and control
    current_phase: str
    overall_success: bool
    error_messages: List[str]
    
    # Performance metrics
    start_time: float
    phase_timings: Dict[str, float]
    final_confidence: float
    performance_grade: str
    
    # Testing environment status
    testing_env_ready: bool
    virtual_env_path: Optional[str]
    automation_tools_status: Dict[str, bool]

class LangGraphMultiAgentOrchestrator:
    """
    LangGraph-based Multi-Agent Orchestrator with proper state management
    Uses nodes and edges for agent coordination with testing environment integration
    """
    
    def __init__(self):
        self.orchestrator_version = "3.0.0-langgraph"
        self.db_manager = None
        self.graph = None
        self.checkpointer = None
        
        # Initialize all agents
        self.agent1 = UpdatedAgent1_BlueprintGenerator()
        self.agent2 = UpdatedAgent2_CodeGenerator() 
        self.agent3 = UpdatedAgent3_TestingEnvironment()
        self.agent4 = UpdatedAgent4_FinalReporter()
        
        # Initialize automation tools
        self.playwright_driver = playwright_driver
        self.appium_driver = appium_driver
        self.web_tools = web_tools
        self.mobile_tools = mobile_tools
        self.ocr_processor = ocr_processor
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize database, agents, and LangGraph workflow"""
        if self.initialized:
            return
        
        logger.info("🚀 Initializing LangGraph Multi-Agent Orchestrator System...")
        logger.info(f"🚀 Version: {self.orchestrator_version}")
        logger.info("🚀 Features: LangGraph State Management, Agent Communication, Testing Environment")
        
        if not LANGGRAPH_AVAILABLE:
            raise RuntimeError("LangGraph is required but not installed")
        
        # Initialize database
        self.db_manager = await get_testing_db()
        
        # Initialize all agents
        await self.agent1.initialize()
        await self.agent2.initialize()
        await self.agent3.initialize()
        await self.agent4.initialize()
        
        # Create LangGraph workflow
        self.graph = self._build_langgraph_workflow()
        
        # Set up checkpointer for state persistence
        if SqliteSaver:
            with SqliteSaver.from_conn_string("checkpoints.sqlite") as checkpointer:
                self.checkpointer = checkpointer
        else:
            self.checkpointer = None
            logger.warning("Using in-memory checkpointing")
        
        self.initialized = True
        logger.info("✅ LangGraph Multi-Agent Orchestrator System initialized")
        logger.info("📋 Ready for automation tasks with stateful workflow management")
    
    def _build_langgraph_workflow(self) -> StateGraph:
        """Build the LangGraph workflow with nodes and edges"""
        logger.info("🔧 Building LangGraph workflow...")
        
        # Create state graph
        workflow = StateGraph(AutomationState)
        
        # Add agent nodes
        workflow.add_node("blueprint_agent", self._blueprint_node)
        workflow.add_node("code_agent", self._code_generation_node)
        workflow.add_node("testing_agent", self._testing_environment_node)
        workflow.add_node("results_agent", self._final_reporting_node)
        
        # Add utility nodes
        workflow.add_node("initialize_task", self._initialize_task_node)
        workflow.add_node("finalize_workflow", self._finalize_workflow_node)
        
        # Define edges and control flow
        workflow.add_edge(START, "initialize_task")
        workflow.add_edge("initialize_task", "blueprint_agent")
        workflow.add_edge("blueprint_agent", "code_agent")
        
        # Conditional edge for testing - may need Agent 2 collaboration
        workflow.add_conditional_edges(
            "code_agent",
            self._should_proceed_to_testing,
            {
                "testing": "testing_agent",
                "retry_code": "code_agent",  # Loop back for improvements
                "error": END
            }
        )
        
        # Conditional edge after testing - may need Agent 2 collaboration
        workflow.add_conditional_edges(
            "testing_agent", 
            self._should_proceed_to_results,
            {
                "results": "results_agent",
                "retry_code": "code_agent",  # Agent 3 -> Agent 2 collaboration
                "retry_testing": "testing_agent",  # Retry testing
                "error": END
            }
        )
        
        workflow.add_edge("results_agent", "finalize_workflow")
        workflow.add_edge("finalize_workflow", END)
        
        logger.info("🔧 ✅ LangGraph workflow built successfully")
        return workflow
    
    # LangGraph Node Functions
    
    async def _initialize_task_node(self, state: AutomationState) -> AutomationState:
        """Initialize the automation task"""
        logger.info("🔵 [LangGraph] Initializing automation task...")
        
        state["current_phase"] = "initialization"
        state["start_time"] = time.time()
        state["phase_timings"] = {}
        state["error_messages"] = []
        state["overall_success"] = False
        state["testing_env_ready"] = False
        state["automation_tools_status"] = {
            "playwright": False,
            "appium": False,
            "ocr": False
        }
        
        # Add initial message
        state["messages"].append({
            "role": "system",
            "content": f"Starting automation workflow for: {state['instruction']}",
            "agent": "orchestrator",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info("🔵 [LangGraph] ✅ Task initialized successfully")
        return state
    
    async def _blueprint_node(self, state: AutomationState) -> AutomationState:
        """Agent 1: Blueprint Generation Node"""
        logger.info("🔵 [LangGraph] Executing Blueprint Agent...")
        
        phase_start = time.time()
        state["current_phase"] = "blueprint_generation"
        
        try:
            # Call Agent 1
            agent1_result = await self.agent1.process_and_generate_blueprint(
                document_content=state["document_content"],
                screenshots=state["screenshots"],
                instruction=state["instruction"],
                platform=state["platform"],
                additional_data=state.get("additional_data")
            )
            
            if agent1_result["success"]:
                state["agent1_result"] = agent1_result
                state["seq_id"] = agent1_result["seq_id"]
                state["base_path"] = agent1_result["base_path"]
                
                # Add success message
                state["messages"].append({
                    "role": "agent",
                    "content": f"Blueprint generated successfully. Sequential ID: {agent1_result['seq_id']}",
                    "agent": "agent1",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        "ui_elements": agent1_result.get("ui_elements", 0),
                        "automation_steps": agent1_result.get("automation_steps", 0),
                        "confidence": agent1_result.get("blueprint_confidence", 0.0)
                    }
                })
                
                logger.info(f"🔵 [LangGraph] ✅ Blueprint Agent completed - Task ID: {agent1_result['seq_id']}")
            else:
                raise Exception(f"Agent 1 failed: {agent1_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            error_msg = f"Blueprint generation failed: {str(e)}"
            logger.error(f"🔴 [LangGraph] {error_msg}")
            
            state["error_messages"].append(error_msg)
            state["messages"].append({
                "role": "error",
                "content": error_msg,
                "agent": "agent1",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        state["phase_timings"]["blueprint"] = time.time() - phase_start
        return state
    
    async def _code_generation_node(self, state: AutomationState) -> AutomationState:
        """Agent 2: Code Generation Node with automation tools integration"""
        logger.info("🟢 [LangGraph] Executing Code Generation Agent...")
        
        phase_start = time.time()
        state["current_phase"] = "code_generation"
        
        try:
            if not state.get("seq_id"):
                raise Exception("No sequential task ID available from blueprint agent")
            
            # Call Agent 2 with existing automation tools
            agent2_result = await self.agent2.generate_code_and_setup(
                seq_id=state["seq_id"],
                automation_tools={
                    "playwright_driver": self.playwright_driver,
                    "appium_driver": self.appium_driver,
                    "web_tools": self.web_tools,
                    "mobile_tools": self.mobile_tools,
                    "ocr_processor": self.ocr_processor
                }
            )
            
            if agent2_result["success"]:
                state["agent2_result"] = agent2_result
                
                # Add success message with tool integration status
                state["messages"].append({
                    "role": "agent",
                    "content": f"Code generated with automation tools integration. Script size: {agent2_result.get('script_size', 0)} chars",
                    "agent": "agent2", 
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        "ready_for_testing": agent2_result.get("ready_for_testing", False),
                        "tools_integrated": True,
                        "requirements_generated": agent2_result.get("requirements_path") is not None
                    }
                })
                
                logger.info("🟢 [LangGraph] ✅ Code Generation Agent completed with tool integration")
            else:
                raise Exception(f"Agent 2 failed: {agent2_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            error_msg = f"Code generation failed: {str(e)}"
            logger.error(f"🔴 [LangGraph] {error_msg}")
            
            state["error_messages"].append(error_msg)
            state["messages"].append({
                "role": "error",
                "content": error_msg,
                "agent": "agent2",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        state["phase_timings"]["code_generation"] = time.time() - phase_start
        return state
    
    async def _testing_environment_node(self, state: AutomationState) -> AutomationState:
        """Agent 3: Testing Environment Node with Agent 2 collaboration"""
        logger.info("🟡 [LangGraph] Executing Testing Environment Agent...")
        
        phase_start = time.time()
        state["current_phase"] = "testing_environment"
        
        try:
            if not state.get("seq_id"):
                raise Exception("No sequential task ID available")
            
            # Call Agent 3 with platform tools status
            agent3_result = await self.agent3.setup_and_execute_tests(
                seq_id=state["seq_id"],
                platform_tools={
                    "web": {"playwright": True, "tools": True},
                    "mobile": {"appium": True, "tools": True},
                    "ocr": {"available": True}
                }
            )
            
            state["agent3_result"] = agent3_result
            
            # Update testing environment status
            if agent3_result.get("success"):
                state["testing_env_ready"] = True
                state["virtual_env_path"] = agent3_result.get("testing_path")
                state["automation_tools_status"] = {
                    "playwright": agent3_result.get("venv_setup", {}).get("success", False),
                    "appium": agent3_result.get("dependencies_installed", {}).get("success", False),
                    "ocr": True  # OCR is always available
                }
            
            # Add collaboration message
            collaborations = agent3_result.get("agent2_collaborations", 0)
            state["messages"].append({
                "role": "agent",
                "content": f"Testing completed. Collaborations with Agent 2: {collaborations}. Success: {agent3_result.get('overall_test_success', False)}",
                "agent": "agent3",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "test_attempts": agent3_result.get("total_attempts", 0),
                    "agent2_collaborations": collaborations,
                    "testing_environment_ready": state["testing_env_ready"]
                }
            })
            
            logger.info(f"🟡 [LangGraph] ✅ Testing Environment Agent completed - Collaborations: {collaborations}")
                
        except Exception as e:
            error_msg = f"Testing environment setup failed: {str(e)}"
            logger.error(f"🔴 [LangGraph] {error_msg}")
            
            state["error_messages"].append(error_msg)
            state["messages"].append({
                "role": "error",
                "content": error_msg,
                "agent": "agent3",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        state["phase_timings"]["testing"] = time.time() - phase_start
        return state
    
    async def _final_reporting_node(self, state: AutomationState) -> AutomationState:
        """Agent 4: Final Reporting Node"""
        logger.info("🔵 [LangGraph] Executing Final Reporting Agent...")
        
        phase_start = time.time()
        state["current_phase"] = "final_reporting"
        
        try:
            if not state.get("seq_id"):
                raise Exception("No sequential task ID available")
            
            # Call Agent 4
            agent4_result = await self.agent4.generate_final_report(state["seq_id"])
            
            if agent4_result.get("success"):
                state["agent4_result"] = agent4_result
                
                # Extract performance metrics
                if "analysis_results" in agent4_result:
                    analysis = agent4_result["analysis_results"]
                    state["final_confidence"] = analysis.get("overall_confidence", 0.0)
                    state["performance_grade"] = analysis.get("performance_grade", "Unknown")
                
                # Add final message
                state["messages"].append({
                    "role": "agent",
                    "content": f"Final report generated. Performance: {state.get('performance_grade', 'Unknown')}",
                    "agent": "agent4",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        "confidence": state.get("final_confidence", 0.0),
                        "files_generated": len(agent4_result.get("files_generated", []))
                    }
                })
                
                logger.info("🔵 [LangGraph] ✅ Final Reporting Agent completed")
            else:
                logger.warning(f"🟡 [LangGraph] Final reporting completed with issues: {agent4_result.get('error', 'Unknown')}")
                
        except Exception as e:
            error_msg = f"Final reporting failed: {str(e)}"
            logger.error(f"🔴 [LangGraph] {error_msg}")
            
            state["error_messages"].append(error_msg)
            state["messages"].append({
                "role": "error",
                "content": error_msg,
                "agent": "agent4", 
                "timestamp": datetime.utcnow().isoformat()
            })
        
        state["phase_timings"]["final_reporting"] = time.time() - phase_start
        return state
    
    async def _finalize_workflow_node(self, state: AutomationState) -> AutomationState:
        """Finalize the entire workflow"""
        logger.info("🚀 [LangGraph] Finalizing workflow...")
        
        state["current_phase"] = "completed"
        
        # Calculate overall success
        state["overall_success"] = (
            state.get("agent1_result", {}).get("success", False) and
            state.get("agent2_result", {}).get("success", False) and
            state.get("agent3_result", {}).get("success", False) and
            state.get("agent4_result", {}).get("success", False) and
            len(state.get("error_messages", [])) == 0
        )
        
        # Calculate total execution time
        total_time = time.time() - state["start_time"]
        
        # Add final summary message
        state["messages"].append({
            "role": "system",
            "content": f"Workflow completed. Success: {state['overall_success']}. Total time: {total_time:.1f}s",
            "agent": "orchestrator",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "total_execution_time": total_time,
                "final_confidence": state.get("final_confidence", 0.0),
                "performance_grade": state.get("performance_grade", "Unknown"),
                "testing_env_ready": state.get("testing_env_ready", False)
            }
        })
        
        logger.info(f"🚀 [LangGraph] ✅ Workflow finalized - Success: {state['overall_success']}")
        return state
    
    # Conditional Edge Functions
    
    def _should_proceed_to_testing(self, state: AutomationState) -> Literal["testing", "retry_code", "error"]:
        """Determine if we should proceed to testing or retry code generation"""
        
        if state.get("error_messages"):
            return "error"
        
        agent2_result = state.get("agent2_result", {})
        
        if not agent2_result.get("success", False):
            return "retry_code" if len(state.get("messages", [])) < 10 else "error"  # Max retry limit
        
        if not agent2_result.get("ready_for_testing", False):
            return "retry_code"
        
        return "testing"
    
    def _should_proceed_to_results(self, state: AutomationState) -> Literal["results", "retry_code", "retry_testing", "error"]:
        """Determine next step after testing - enables Agent 2-3 collaboration"""
        
        if state.get("error_messages"):
            return "error"
        
        agent3_result = state.get("agent3_result", {})
        
        if not agent3_result.get("success", False):
            # Check if Agent 3 needs to collaborate with Agent 2
            collaborations = agent3_result.get("agent2_collaborations", 0)
            
            if collaborations < 3:  # Max 3 collaboration attempts
                return "retry_code"  # Agent 3 requests Agent 2 improvements
            else:
                return "retry_testing"  # Try testing again without more code changes
        
        # If testing was successful, proceed to results
        if agent3_result.get("overall_test_success", False):
            return "results"
        
        # If testing failed but we haven't reached collaboration limit
        collaborations = agent3_result.get("agent2_collaborations", 0)
        if collaborations < 3:
            return "retry_code"
        
        # Last resort - proceed to results even with testing issues
        return "results"
    
    # Main Execution Method
    
    async def execute_complete_workflow(self, 
                                      document_content: bytes, 
                                      screenshots: List[bytes],
                                      instruction: str, 
                                      platform: str = "auto-detect",
                                      additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute complete LangGraph-based workflow"""
        
        if not self.initialized:
            await self.initialize()
        
        workflow_start_time = time.time()
        
        logger.info(f"\\n🚀 ========== LANGGRAPH MULTI-AGENT WORKFLOW STARTED ==========")
        logger.info(f"🚀 Version: {self.orchestrator_version}")
        logger.info(f"🚀 Instruction: {instruction}")
        logger.info(f"🚀 Platform: {platform}")
        logger.info(f"🚀 LangGraph State Management: ✅ ENABLED")
        logger.info(f"🚀 Automation Tools Integration: ✅ ENABLED")
        logger.info(f"🚀 =============================================================")
        
        try:
            # Compile the graph with checkpointing
            compiled_graph = self.graph.compile(checkpointer=self.checkpointer)
            
            # Initial state
            initial_state: AutomationState = {
                "seq_id": None,
                "instruction": instruction,
                "platform": platform,
                "base_path": None,
                "document_content": document_content,
                "screenshots": screenshots,
                "additional_data": additional_data or {},
                "agent1_result": None,
                "agent2_result": None, 
                "agent3_result": None,
                "agent4_result": None,
                "messages": [],
                "current_phase": "starting",
                "overall_success": False,
                "error_messages": [],
                "start_time": workflow_start_time,
                "phase_timings": {},
                "final_confidence": 0.0,
                "performance_grade": "Unknown",
                "testing_env_ready": False,
                "virtual_env_path": None,
                "automation_tools_status": {}
            }
            
            # Execute the graph
            config = {"configurable": {"thread_id": f"automation_{int(time.time())}"}}
            
            final_state = None
            async for state_update in compiled_graph.astream(initial_state, config=config):
                final_state = state_update
                
                # Log progress
                current_phase = state_update.get("current_phase", "unknown")
                logger.info(f"🔄 [LangGraph] Phase: {current_phase}")
            
            if not final_state:
                raise Exception("LangGraph execution failed - no final state")
            
            # Extract final results
            total_execution_time = time.time() - workflow_start_time
            
            # Update final task status in database if we have a seq_id
            if final_state.get("seq_id"):
                final_status = "completed" if final_state.get("overall_success") else "completed_with_issues"
                await self.db_manager.update_task_status(final_state["seq_id"], final_status, "langgraph_orchestrator")
            
            logger.info(f"\\n🚀 ========== LANGGRAPH MULTI-AGENT WORKFLOW COMPLETED ==========")
            logger.info(f"🚀 Overall Result: {'✅ SUCCESS' if final_state.get('overall_success') else '⚠️ COMPLETED WITH ISSUES'}")
            logger.info(f"🚀 Sequential Task ID: {final_state.get('seq_id', 'N/A')}")
            logger.info(f"🚀 Final Confidence: {final_state.get('final_confidence', 0.0):.3f}")
            logger.info(f"🚀 Performance Grade: {final_state.get('performance_grade', 'Unknown')}")
            logger.info(f"🚀 Total Execution Time: {total_execution_time:.1f} seconds")
            logger.info(f"🚀 Testing Environment: {'✅ READY' if final_state.get('testing_env_ready') else '❌ NOT READY'}")
            logger.info(f"🚀 Agent Communications: {len(final_state.get('messages', []))}")
            logger.info(f"🚀 LangGraph State Transitions: ✅ MANAGED")
            logger.info(f"🚀 ================================================================")
            
            return {
                "success": final_state.get("overall_success", False),
                "seq_id": final_state.get("seq_id"),
                "base_path": final_state.get("base_path"),
                "final_confidence": final_state.get("final_confidence", 0.0),
                "performance_grade": final_state.get("performance_grade", "Unknown"),
                "total_execution_time": total_execution_time,
                "langgraph_state": final_state,
                "messages": final_state.get("messages", []),
                "testing_env_ready": final_state.get("testing_env_ready", False),
                "automation_tools_status": final_state.get("automation_tools_status", {}),
                "message": "✅ LangGraph multi-agent workflow completed successfully" if final_state.get("overall_success") else "⚠️ LangGraph workflow completed with some issues",
                "orchestrator_version": self.orchestrator_version
            }
            
        except Exception as e:
            error_msg = f"LangGraph multi-agent workflow failed: {str(e)}"
            logger.error(f"🔴 {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "total_execution_time": time.time() - workflow_start_time,
                "message": f"❌ LangGraph workflow failed: {error_msg}",
                "orchestrator_version": self.orchestrator_version
            }
    
    async def get_task_status(self, seq_id: int) -> Dict[str, Any]:
        """Get comprehensive task status including LangGraph state"""
        try:
            # Get task info from database
            task_info = await self.db_manager.get_task_info(seq_id)
            if not task_info:
                return {"error": f"Task {seq_id} not found"}
            
            # Get workflow steps
            workflow_steps = await self.db_manager.get_workflow_steps(seq_id)
            
            return {
                "seq_id": seq_id,
                "task_info": task_info,
                "workflow_steps": len(workflow_steps),
                "langgraph_enabled": True,
                "orchestrator_version": self.orchestrator_version,
                "status_check_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"LangGraph task status check failed: {str(e)}")
            return {"error": f"Status check failed: {str(e)}"}
    
    async def list_recent_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent tasks managed by LangGraph orchestrator"""
        try:
            return await self.db_manager.list_recent_tasks(limit)
        except Exception as e:
            logger.error(f"Recent tasks listing failed: {str(e)}")
            return []

# Global LangGraph orchestrator instance
langgraph_orchestrator = LangGraphMultiAgentOrchestrator()

async def get_langgraph_orchestrator() -> LangGraphMultiAgentOrchestrator:
    """Get the global LangGraph orchestrator instance"""
    if not langgraph_orchestrator.initialized:
        await langgraph_orchestrator.initialize()
    return langgraph_orchestrator