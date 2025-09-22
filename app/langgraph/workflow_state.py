"""
Automation Workflow State - COMPLETELY FIXED  
LangGraph state management for multi-agent automation workflows
"""
import json
import logging
from typing import Dict, List, Optional, Any, Annotated
from datetime import datetime

# Try importing LangGraph components
try:
    from langgraph.graph.message import MessagesState, add_messages
    LANGGRAPH_AVAILABLE = True
    print("✅ LangGraph components available")
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    print(f"⚠️ LangGraph not available: {str(e)}")
    
    # Create fallback MessagesState
    class MessagesState:
        messages: List[Dict] = []

# Import managers
try:
    from app.database.database_manager import get_database_manager
    from app.utils.output_structure_manager import OutputStructureManager
    MANAGERS_AVAILABLE = True
    print("✅ Managers available")
except ImportError as e:
    MANAGERS_AVAILABLE = False
    print(f"⚠️ Managers not available: {str(e)}")

logger = logging.getLogger(__name__)

class AutomationWorkflowState(MessagesState):
    """
    LangGraph state for multi-agent automation workflow.
    Extends MessagesState with workflow orchestration capabilities.
    COMPLETELY FIXED: No reserved names, dict-compatible
    """
    
    # Core workflow identification
    task_id: int
    platform: str  # 'web', 'mobile', 'auto'
    instruction: str
    document_data: Optional[bytes] = None
    screenshots: List[bytes] = []
    
    # LangGraph integration - FIXED: Renamed checkpoint_id to avoid reserved name
    thread_id: Optional[str] = None
    workflow_checkpoint_id: Optional[str] = None  # FIXED: Renamed from checkpoint_id
    current_node: Optional[str] = None  # 'supervisor', 'agent1', 'agent2', 'agent3', 'agent4'
    
    # Agent status tracking - FIXED: Added missing status fields
    agent1_status: str = "pending"  # 'pending', 'running', 'completed', 'failed'
    agent2_status: str = "pending"
    agent3_status: str = "pending"
    agent4_status: str = "pending"
    
    # Agent outputs
    blueprint: Optional[Dict[str, Any]] = None  # Agent1 output
    generated_code: Optional[Dict[str, Any]] = None  # Agent2 output
    testing_results: Optional[Dict[str, Any]] = None  # Agent3 output
    final_results: Optional[Dict[str, Any]] = None  # Agent4 output
    
    # Workflow execution state
    ui_elements: List[Dict[str, Any]] = []
    workflow_steps: List[Dict[str, Any]] = []
    script_content: str = ""
    requirements_content: str = ""
    device_config: Dict[str, Any] = {}
    environment_ready: bool = False
    script_executed: str = "not_started"  # 'not_started', 'running', 'completed', 'failed'
    
    # Collaboration tracking
    collaboration_requested: bool = False
    collaboration_history: List[Dict[str, Any]] = []
    collaboration_active: bool = False
    collaboration_count: int = 0
    
    # Agent2 ↔ Agent3 specific collaboration
    pending_fix_requests: List[Dict[str, Any]] = []
    pending_fix_responses: List[Dict[str, Any]] = []
    
    # Supervisor decisions
    supervisor_decisions: List[Dict[str, Any]] = []
    supervisor_decision: Optional[Dict[str, Any]] = None  # Current decision
    routing_history: List[str] = []  # Track agent sequence
    
    # Execution tracking
    retry_count: int = 0
    max_retries: int = 3
    current_agent: Optional[str] = None
    previous_agent: Optional[str] = None
    workflow_status: str = "initiated"  # 'initiated', 'running', 'completed', 'failed', 'collaboration'
    workflow_completed: bool = False
    
    # Execution timing
    workflow_started_at: Optional[str] = None
    workflow_completed_at: Optional[str] = None
    current_phase_started_at: Optional[str] = None
    
    # Agent reviews & assessments
    agent_reviews: Dict[str, Dict[str, Any]] = {}
    quality_assessments: Dict[str, float] = {}  # agent -> confidence score
    
    # Error handling
    error_messages: List[str] = []
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    last_error: Optional[str] = None
    
    # Quality metrics
    confidence: float = 0.0
    
    # Tool execution tracking
    tool_executions: List[Dict[str, Any]] = []
    active_tools: Dict[str, Any] = {}  # Currently executing tools
    
    # Database & output integration
    db_manager: Optional[Any] = None
    output_manager: Optional[Any] = None
    
    # File paths for generated outputs
    output_files: Dict[str, str] = {}  # category -> file_path
    
    # Configuration & metadata
    additional_data: Dict[str, Any] = {}
    workflow_config: Dict[str, Any] = {}
    
    # Platform-specific settings
    mobile_config: Optional[Dict[str, Any]] = None
    web_config: Optional[Dict[str, Any]] = None
    
    # Workflow creation timestamp
    created_at: Optional[str] = None

    def __post_init__(self):
        """Initialize state after creation"""
        if not self.workflow_started_at:
            self.workflow_started_at = datetime.now().isoformat()
        if not self.thread_id:
            self.thread_id = f"thread_{self.task_id}_{int(datetime.now().timestamp())}"
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    # State management methods
    def update_current_agent(self, agent_name: str):
        """Update current and previous agent tracking"""
        self.previous_agent = self.current_agent
        self.current_agent = agent_name
        self.current_phase_started_at = datetime.now().isoformat()
        
        # Add to routing history
        if agent_name not in ["supervisor"]:  # Don't track supervisor in routing
            self.routing_history.append(agent_name)
        
        logger.info(f"🔄 State updated: {self.previous_agent} → {agent_name}")

    def add_supervisor_decision(
        self,
        decision_type: str,
        from_node: str,
        to_node: str,
        reasoning: str,
        confidence: float = 0.0,
        decision_data: Optional[Dict[str, Any]] = None
    ):
        """Add supervisor decision to state"""
        decision = {
            "decision_id": len(self.supervisor_decisions) + 1,
            "decision_type": decision_type,
            "from_node": from_node,
            "to_node": to_node,
            "reasoning": reasoning,
            "confidence": confidence,
            "decision_data": decision_data or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.supervisor_decisions.append(decision)
        self.supervisor_decision = decision  # Set current decision
        logger.info(f"🎯 Supervisor decision added: {from_node} → {to_node} ({decision_type})")

    def start_collaboration(self, requesting_agent: str, target_agent: str, request_data: Dict[str, Any]):
        """Start collaboration between agents"""
        collaboration_session = {
            "session_id": f"collab_{len(self.collaboration_history) + 1}",
            "requesting_agent": requesting_agent,
            "target_agent": target_agent,
            "request_data": request_data,
            "status": "active",
            "started_at": datetime.now().isoformat(),
            "messages": []
        }
        
        self.collaboration_history.append(collaboration_session)
        self.collaboration_active = True
        self.collaboration_count += 1
        self.collaboration_requested = True
        
        logger.info(f"🤝 Collaboration started: {requesting_agent} ↔ {target_agent}")

    def add_collaboration_message(self, from_agent: str, to_agent: str, message_type: str, content: Dict[str, Any]):
        """Add message to active collaboration session"""
        if self.collaboration_active and self.collaboration_history:
            current_session = self.collaboration_history[-1]
            message = {
                "from_agent": from_agent,
                "to_agent": to_agent,
                "message_type": message_type,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            
            current_session["messages"].append(message)
            logger.info(f"💬 Collaboration message: {from_agent} → {to_agent} ({message_type})")

    def end_collaboration(self, success: bool = True, resolution: Optional[str] = None):
        """End current collaboration session"""
        if self.collaboration_active and self.collaboration_history:
            current_session = self.collaboration_history[-1]
            current_session["status"] = "completed" if success else "failed"
            current_session["ended_at"] = datetime.now().isoformat()
            current_session["resolution"] = resolution or ("Success" if success else "Failed")
            
            self.collaboration_active = False
            logger.info(f"✅ Collaboration ended: {current_session['status']}")

    def add_agent_review(self, agent_name: str, review_data: Dict[str, Any]):
        """Add agent self-assessment review"""
        self.agent_reviews[agent_name] = {
            **review_data,
            "reviewed_at": datetime.now().isoformat()
        }
        
        # Extract confidence score
        if "confidence" in review_data:
            self.quality_assessments[agent_name] = review_data["confidence"]
        
        logger.info(f"📝 Agent review added: {agent_name}")

    def log_tool_execution(
        self,
        agent_name: str,
        tool_name: str,
        tool_input: Dict[str, Any],
        execution_status: str = "started"
    ):
        """Log tool execution in state"""
        execution = {
            "execution_id": f"tool_{len(self.tool_executions) + 1}",
            "agent_name": agent_name,
            "tool_name": tool_name,
            "tool_input": tool_input,
            "execution_status": execution_status,
            "started_at": datetime.now().isoformat()
        }
        
        self.tool_executions.append(execution)
        
        if execution_status == "started":
            self.active_tools[execution["execution_id"]] = execution
        
        logger.info(f"🛠️ Tool execution logged: {agent_name}.{tool_name} ({execution_status})")

    def update_tool_execution(self, execution_id: str, tool_output: Any, execution_status: str = "completed"):
        """Update tool execution with results"""
        # Update in tool_executions list
        for execution in self.tool_executions:
            if execution["execution_id"] == execution_id:
                execution["tool_output"] = tool_output
                execution["execution_status"] = execution_status
                execution["completed_at"] = datetime.now().isoformat()
                break
        
        # Remove from active tools if completed
        if execution_status in ["completed", "failed"] and execution_id in self.active_tools:
            del self.active_tools[execution_id]
        
        logger.info(f"🔧 Tool execution updated: {execution_id} ({execution_status})")

    def add_error(self, error_type: str, error_message: str, agent_name: Optional[str] = None):
        """Add error to state"""
        error = {
            "error_id": len(self.errors) + 1,
            "error_type": error_type,
            "error_message": error_message,
            "agent_name": agent_name,
            "timestamp": datetime.now().isoformat()
        }
        
        self.errors.append(error)
        self.error_messages.append(error_message)
        self.last_error = error_message
        
        logger.error(f"❌ Error added to state: {error_type} - {error_message}")

    def add_warning(self, warning_type: str, warning_message: str, agent_name: Optional[str] = None):
        """Add warning to state"""
        warning = {
            "warning_id": len(self.warnings) + 1,
            "warning_type": warning_type,
            "warning_message": warning_message,
            "agent_name": agent_name,
            "timestamp": datetime.now().isoformat()
        }
        
        self.warnings.append(warning)
        logger.warning(f"⚠️ Warning added to state: {warning_type} - {warning_message}")

    # State utilities
    def get_current_phase_duration(self) -> float:
        """Get duration of current phase in seconds"""
        if self.current_phase_started_at:
            start_time = datetime.fromisoformat(self.current_phase_started_at)
            return (datetime.now() - start_time).total_seconds()
        return 0.0

    def get_total_workflow_duration(self) -> float:
        """Get total workflow duration in seconds"""
        if self.workflow_started_at:
            start_time = datetime.fromisoformat(self.workflow_started_at)
            return (datetime.now() - start_time).total_seconds()
        return 0.0

    def should_retry(self) -> bool:
        """Check if workflow should retry based on retry count"""
        return self.retry_count < self.max_retries

    def increment_retry(self):
        """Increment retry count"""
        self.retry_count += 1
        logger.info(f"🔁 Retry count incremented: {self.retry_count}/{self.max_retries}")

    def is_collaboration_needed(self) -> bool:
        """Check if Agent2 ↔ Agent3 collaboration is needed"""
        return (
            self.testing_results is not None and
            not self.testing_results.get("success", False) and
            self.should_retry()
        )

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of current state"""
        return {
            "task_id": self.task_id,
            "platform": self.platform,
            "workflow_status": self.workflow_status,
            "current_agent": self.current_agent,
            "current_node": self.current_node,
            "retry_count": self.retry_count,
            "collaboration_active": self.collaboration_active,
            "collaboration_count": self.collaboration_count,
            "routing_history": self.routing_history,
            "total_duration": self.get_total_workflow_duration(),
            "phase_duration": self.get_current_phase_duration(),
            "agent_outputs": {
                "blueprint": self.blueprint is not None,
                "generated_code": self.generated_code is not None,
                "testing_results": self.testing_results is not None,
                "final_results": self.final_results is not None
            },
            "agent_statuses": {
                "agent1": self.agent1_status,
                "agent2": self.agent2_status,
                "agent3": self.agent3_status,
                "agent4": self.agent4_status
            },
            "quality_scores": self.quality_assessments,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "tool_executions_count": len(self.tool_executions),
            "active_tools_count": len(self.active_tools)
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization - FIXED for LangGraph compatibility"""
        state_dict = {}
        
        # Convert all attributes to serializable format
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            
            if isinstance(value, bytes):
                # Convert bytes to base64 string
                import base64
                state_dict[key] = base64.b64encode(value).decode('utf-8')
            elif hasattr(value, '__dict__'):
                # Skip complex objects that can't be serialized
                continue
            else:
                state_dict[key] = value
        
        return state_dict

    def __repr__(self):
        return (
            f"AutomationWorkflowState("
            f"task_id={self.task_id}, "
            f"platform={self.platform}, "
            f"status={self.workflow_status}, "
            f"current_agent={self.current_agent}, "
            f"retry_count={self.retry_count})"
        )


def create_initial_state(
    task_id: int,
    instruction: str,
    platform: str,
    document_data: Optional[bytes] = None,
    screenshots: Optional[List[bytes]] = None,
    additional_data: Optional[Dict[str, Any]] = None
) -> AutomationWorkflowState:
    """Create initial automation workflow state"""
    
    state = AutomationWorkflowState(
        task_id=task_id,
        platform=platform,
        instruction=instruction,
        document_data=document_data,
        screenshots=screenshots or [],
        additional_data=additional_data or {},
        messages=[],  # Initialize empty messages list
        workflow_status="initiated"
    )
    
    # Initialize managers if available
    if MANAGERS_AVAILABLE:
        try:
            state.output_manager = OutputStructureManager(task_id)
            logger.info(f"✅ Output manager initialized for task {task_id}")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize output manager: {str(e)}")
    
    logger.info(f"🚀 Initial workflow state created for task {task_id}")
    return state


if __name__ == "__main__":
    # Test state functionality
    def test_automation_state():
        print("🧪 Testing AutomationWorkflowState...")
        
        # Create initial state
        state = create_initial_state(
            task_id=123,
            instruction="Test mobile automation",
            platform="mobile",
            additional_data={"test": True}
        )
        
        print(f"✅ Initial state created: {state}")
        
        # Test agent tracking
        state.update_current_agent("agent1")
        print(f"✅ Updated to agent1: {state.current_agent}")
        
        # Test supervisor decision
        state.add_supervisor_decision(
            "route", "supervisor", "agent1",
            "Starting with blueprint generation", 0.95
        )
        print(f"✅ Added supervisor decision: {len(state.supervisor_decisions)}")
        
        # Test collaboration
        state.start_collaboration(
            "agent3", "agent2",
            {"error": "Element not found", "suggested_fix": "Update selector"}
        )
        
        state.add_collaboration_message(
            "agent3", "agent2", "fix_request",
            {"error_details": "Timeout on element selection"}
        )
        
        state.end_collaboration(True, "Code fixed successfully")
        print(f"✅ Collaboration session completed: {len(state.collaboration_history)}")
        
        # Test agent review
        state.add_agent_review("agent1", {
            "confidence": 0.9,
            "ui_elements_detected": 5,
            "quality": "high"
        })
        print(f"✅ Added agent review: {len(state.agent_reviews)}")
        
        # Test state summary
        summary = state.get_state_summary()
        print(f"✅ State summary: {summary['workflow_status']}")
        
        # Test dict conversion
        state_dict = state.to_dict()
        print(f"✅ Dict conversion: {len(state_dict)} fields")
        
        print("🎉 AutomationWorkflowState test completed!")
    
    test_automation_state()