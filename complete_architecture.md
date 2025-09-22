# 🏗️ LANGGRAPH MULTI-AGENT AUTOMATION FRAMEWORK - COMPLETE ARCHITECTURE

## 🎯 **ARCHITECTURE OVERVIEW**

This document defines the complete architecture for a LangGraph-based multi-agent automation framework that transforms document inputs into executable automation scripts through intelligent agent collaboration.

---

## 🔄 **SYSTEM FLOW DIAGRAM**

```
📄 Document Input (PDF/Image/Text)
         |
         ▼
    🤖 SUPERVISOR 
    (Intelligent Routing)
         |
    ┌────┴────┬─────────┬─────────┐
    ▼         ▼         ▼         ▼
Agent1    Agent2    Agent3    Agent4
Blueprint  Code     Testing   Results
    |         ▲         ▲         |
    └─────────┼─────────┼─────────┘
              |         |
              └─────────┘
            Collaboration Loop
            (Agent2 ↔ Agent3)
         |
         ▼
📁 Complete Output Structure
   + Database Tracking
   + State Persistence
```

---

## 🧠 **CORE COMPONENTS**

### **1. LangGraph Workflow Engine**
```python
# State Management
class AutomationWorkflowState(MessagesState):
    task_id: int
    platform: str  # 'web', 'mobile', 'auto'
    blueprint: Optional[Dict]        # Agent1 output
    generated_code: Optional[Dict]   # Agent2 output
    test_results: Optional[Dict]     # Agent3 output
    final_reports: Optional[Dict]    # Agent4 output
    
    # Collaboration & Supervision
    collaboration_history: List[Dict] = []
    supervisor_decisions: List[Dict] = []
    retry_count: int = 0
    current_agent: Optional[str] = None
    workflow_status: str = "initiated"

# Workflow Graph
graph = StateGraph(AutomationWorkflowState)
graph.add_node("supervisor", supervisor_agent)
graph.add_node("agent1", blueprint_agent)
graph.add_node("agent2", code_agent) 
graph.add_node("agent3", testing_agent)
graph.add_node("agent4", results_agent)
```

### **2. Agent Architecture**
```python
# Agent Creation Pattern
agent_X = create_react_agent(
    tools=[tool1, tool2, tool3],
    name="agent_X"
)

# Tool Integration Pattern  
@tool
def agent_tool(
    task_id: Annotated[int, "Task ID for logging"],
    input_data: Annotated[Any, "Tool input"]
) -> Annotated[Any, "Tool output with logging"]:
    """Execute functionality + database logging + output structure management"""
```

### **3. Supervisor Intelligence**
```python
@tool
def supervisor_routing_tool(
    current_state: Annotated[Dict, "Workflow state"],
    last_result: Annotated[Dict, "Last agent result"],
    collaboration_context: Annotated[Dict, "Collaboration context"]
) -> Annotated[str, "Next agent to route to"]:
    """Intelligent routing decisions with collaboration support"""
    
    # Decision Logic:
    # - Route to next agent in sequence
    # - Detect collaboration needs (Agent2 ↔ Agent3)
    # - Handle retries and error recovery
    # - Make final completion decisions
```

---

## 🗄️ **DATABASE ARCHITECTURE**

### **Enhanced Schema (Extends Existing)**
```sql
-- CORE TABLES (Your existing schema)
automation_tasks     -- Main task tracking with ADDED review column
workflow_steps       -- Step-by-step execution tracking
agent_communications -- Agent message tracking with ADDED LangGraph columns
generated_files      -- File output tracking
testing_environments -- Testing setup tracking
test_executions      -- Execution results tracking

-- NEW LANGGRAPH TABLES
langgraph_tool_executions     -- @tool execution logging
langgraph_state_snapshots     -- Workflow state checkpointing
supervisor_decisions          -- Supervisor routing decisions
output_file_structure         -- Exact output structure tracking
```

### **Review System Architecture**
```json
// review column in automation_tasks table
{
  "agent_reviews": {
    "agent1": {
      "confidence": 0.9,
      "ui_elements_detected": 15,
      "workflow_complexity": "medium",
      "recommendations": ["Add error handling for missing elements"]
    },
    "agent2": {
      "code_quality": 0.85,
      "platform_compatibility": "high",
      "generated_files": ["script.py", "requirements.txt", "config.json"],
      "collaboration_responses": 3
    },
    "agent3": {
      "test_success_rate": 0.7,
      "execution_issues": ["Selector timeout", "Element not found"],
      "fix_requests_sent": 2,
      "environment_setup": "successful"
    },
    "agent4": {
      "report_completeness": 0.95,
      "dashboard_generated": true,
      "data_export_quality": "high"
    }
  },
  "supervisor_decisions": [
    {
      "decision_type": "route",
      "from": "agent1",
      "to": "agent2",
      "reasoning": "Blueprint completed successfully",
      "confidence": 0.9,
      "timestamp": "2025-09-22T11:19:00Z"
    },
    {
      "decision_type": "collaboration",
      "from": "agent3", 
      "to": "agent2",
      "reasoning": "Test failed, need code fix",
      "collaboration_attempt": 1,
      "confidence": 0.8,
      "timestamp": "2025-09-22T11:25:00Z"
    }
  ]
}
```

---

## 🛠️ **TOOL SYSTEM ARCHITECTURE**

### **Agent1: Blueprint Tools**
```python
@tool blueprint_document_analysis_tool()      # PDF/image analysis
@tool blueprint_ui_detection_tool()           # UI element extraction  
@tool blueprint_workflow_generation_tool()    # Workflow step creation
@tool blueprint_save_tool()                   # Save to output structure
```

### **Agent2: Code Generation Tools**
```python
@tool code_script_generation_tool()           # Script generation
@tool code_requirements_generation_tool()     # Dependencies generation
@tool code_config_generation_tool()           # Device/browser config
@tool code_collaboration_response_tool()      # Respond to Agent3 fixes
@tool code_save_artifacts_tool()              # Save to output structure
```

### **Agent3: Testing Tools**
```python
@tool testing_environment_setup_tool()        # Venv + dependency setup
@tool testing_script_execution_tool()         # Script execution with monitoring
@tool testing_result_analysis_tool()          # Result analysis
@tool testing_collaboration_request_tool()    # Request Agent2 fixes
@tool testing_save_logs_tool()                # Save to output structure
```

### **Agent4: Results Tools**  
```python
@tool results_text_report_tool()              # Human-readable report
@tool results_csv_export_tool()               # Structured data export
@tool results_dashboard_generation_tool()     # Interactive HTML dashboard
@tool results_workflow_summary_tool()         # Complete workflow summary
@tool results_save_reports_tool()             # Save to output structure
```

### **Shared Tools**
```python
@tool communication_send_message_tool()       # Inter-agent messaging
@tool database_log_tool_execution_tool()      # Tool execution logging
@tool database_update_review_tool()           # Update agent reviews
@tool output_structure_manager_tool()         # File structure management
```

---

## 📁 **OUTPUT STRUCTURE ARCHITECTURE**

### **Target Directory Structure**
```
generated_code/{task_id}/
├── agent1/
│   └── blueprint.json              # Workflow blueprint with UI elements
├── agent2/
│   ├── script.py                   # Generated automation script
│   ├── requirements.txt            # Platform dependencies
│   ├── device_config.json          # Device/browser configuration
│   └── ocr_logs/                   # OCR analysis templates
├── agent3/
│   └── testing/
│       ├── venv/                   # Isolated virtual environment
│       ├── script.py               # Script copy for testing
│       ├── requirements.txt        # Dependencies copy
│       ├── mobile_config.json      # Mobile-specific config
│       └── execution_logs/         # Runtime execution logs
├── agent4/
│   ├── final_report.txt            # Detailed human-readable report
│   ├── final_report.csv            # Structured data for analysis
│   └── summary_dashboard.html      # Interactive dashboard
├── conversation.json               # Complete agent communication log
├── sqlite_db.sqlite               # Task-specific database export
└── enhanced_workflow_summary.json  # Complete workflow metadata
```

### **Output Management Architecture**
```python
class OutputStructureManager:
    def __init__(self, task_id: int):
        self.task_id = task_id
        self.base_path = Path(f"generated_code/{task_id}")
    
    def get_agent1_path(self) -> Path
    def get_agent2_path(self) -> Path  
    def get_agent3_testing_path(self) -> Path
    def get_agent4_path(self) -> Path
    def create_complete_structure(self) -> Dict[str, Path]
    def generate_conversation_log(self) -> str
    def generate_workflow_summary(self) -> str
    def export_task_database(self) -> str
```

---

## 🔄 **COLLABORATION ARCHITECTURE**

### **Agent2 ↔ Agent3 Bidirectional Communication**
```python
# Agent3 → Agent2: Request Fix
collaboration_request = {
    "type": "fix_request",
    "failed_steps": [
        {"step": 3, "error": "Element not found", "selector": ".login-button"}
    ],
    "suggested_fixes": [
        "Use data-testid instead of class selector",
        "Add explicit wait for element visibility"
    ],
    "execution_context": {
        "platform": "mobile",
        "test_attempt": 2,
        "error_details": "TimeoutException: Element not interactive"
    }
}

# Agent2 → Agent3: Provide Fix  
fix_response = {
    "type": "fix_response",
    "updated_code": "# Updated script with fixes...",
    "fixes_applied": [
        "Changed selector to [data-testid='login-btn']",
        "Added WebDriverWait with 10 second timeout"
    ],
    "confidence": 0.9,
    "version": "update_1.py"
}
```

### **Supervisor Collaboration Logic**
```python
def collaboration_decision_logic(state: AutomationWorkflowState) -> str:
    """Decide if collaboration is needed between Agent2 and Agent3"""
    
    # Test failed and retry count < max_retries
    if (state.test_results and 
        not state.test_results.get("success") and 
        state.retry_count < 3):
        
        if state.current_agent == "agent3":
            # Agent3 just failed, send fix request to Agent2
            return "agent2"  
        elif state.current_agent == "agent2":
            # Agent2 just provided fix, test again with Agent3
            return "agent3"
    
    # Collaboration successful or max retries reached
    return "agent4"  # Generate final report
```

---

## 🔍 **MONITORING & OBSERVABILITY ARCHITECTURE**

### **Real-time State Tracking**
```python
# LangGraph state checkpointing
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
workflow = graph.compile(checkpointer=checkpointer)

# State snapshot on every node transition
await save_state_snapshot(
    task_id, checkpoint_id, thread_id, 
    current_node, complete_state_json
)
```

### **Tool Execution Monitoring**
```python
# Every @tool execution logged
await log_tool_execution(
    task_id=task_id,
    agent_name="agent2", 
    tool_name="code_generation_tool",
    tool_input={"blueprint": {...}, "platform": "mobile"},
    tool_output={"script": "...", "requirements": "..."},
    execution_status="success",
    execution_time=2.3,
    review={"code_quality": 0.85, "recommendations": [...]}
)
```

### **Communication Tracking**
```python
# All agent messages logged with LangGraph integration
await log_agent_message(
    task_id=task_id,
    from_agent="agent3",
    to_agent="agent2", 
    message_type="collaboration_request",
    message_content=collaboration_request,
    langgraph_message_id=msg.id,
    thread_id=state.thread_id,
    checkpoint_id=state.checkpoint_id
)
```

---

## 🎯 **QUALITY ASSURANCE ARCHITECTURE**

### **Agent Self-Assessment**
```python
# Each agent provides self-assessment
def generate_agent_review(execution_result: Dict) -> Dict:
    return {
        "confidence": calculate_confidence(execution_result),
        "quality_metrics": extract_quality_metrics(execution_result),
        "recommendations": generate_recommendations(execution_result),
        "next_steps": suggest_next_steps(execution_result)
    }
```

### **Supervisor Quality Gates**
```python
def supervisor_quality_check(agent_result: Dict, agent_review: Dict) -> bool:
    """Quality gate before proceeding to next agent"""
    
    confidence_threshold = 0.7
    quality_threshold = 0.8
    
    return (
        agent_review.get("confidence", 0) >= confidence_threshold and
        agent_result.get("success", False) and
        meets_quality_standards(agent_result, quality_threshold)
    )
```

---

## 🚀 **SCALABILITY ARCHITECTURE**

### **Modular Tool System**
- Each tool is independently deployable
- Tools can be shared across agents  
- New tools can be added without workflow changes
- Tool versioning and rollback support

### **Agent Extensibility**
- New agents can be added to the workflow graph
- Agent capabilities defined by assigned tools
- Agent communication patterns are standardized
- Agent performance metrics are tracked

### **Database Scalability**
- Horizontal scaling with task-specific databases
- Efficient indexing for real-time queries
- Configurable retention policies
- Export capabilities for external analysis

---

## 🔐 **ERROR HANDLING & RECOVERY ARCHITECTURE**

### **Hierarchical Error Recovery**
```
1. Tool Level: Individual tool error handling and retry
2. Agent Level: Agent fallback strategies and alternative approaches  
3. Collaboration Level: Agent-to-agent error resolution
4. Supervisor Level: Workflow-level error recovery and routing decisions
5. System Level: Complete workflow restart with state recovery
```

### **State Recovery**
```python
# Checkpoint recovery on failure
async def recover_workflow_state(task_id: int, checkpoint_id: str):
    """Recover workflow from last successful checkpoint"""
    
    state = await load_state_snapshot(task_id, checkpoint_id)
    workflow = create_enhanced_workflow()
    
    # Resume from checkpoint
    result = await workflow.ainvoke(
        state, 
        config={"thread_id": state.thread_id, "checkpoint_id": checkpoint_id}
    )
```

This architecture provides a robust, scalable, and maintainable foundation for the multi-agent automation framework with complete observability, error recovery, and quality assurance capabilities.