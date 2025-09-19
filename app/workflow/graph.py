"""
LangGraph workflow definition - orchestrates the multi-agent pipeline
"""
import uuid
import os
from datetime import datetime
from typing import Dict, Any
from langgraph.graph import StateGraph, END, START
from app.models.schemas import WorkflowState, PlatformType
from app.agents.document_agent import document_agent
from app.agents.code_agent import code_agent
from app.agents.llm_supervisor import llm_supervisor
from app.agents.results_agent import results_agent
from app.config.settings import settings

class AutomationWorkflow:
    """Multi-agent automation workflow using LangGraph"""
    
    def __init__(self):
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        # Create state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes (agents)
        workflow.add_node("document_agent", self._document_agent_node)
        workflow.add_node("code_agent", self._code_agent_node)
        workflow.add_node("llm_supervisor", self._llm_supervisor_node)
        workflow.add_node("results_agent", self._results_agent_node)
        
        # Define edges (workflow flow)
        workflow.add_edge(START, "document_agent")
        workflow.add_edge("document_agent", "code_agent")
        workflow.add_edge("code_agent", "llm_supervisor")
        workflow.add_edge("llm_supervisor", "results_agent")
        workflow.add_edge("results_agent", END)
        
       
        
        # Compile the graph
        self.graph = workflow.compile()
        print("[Workflow] LangGraph workflow compiled successfully")
    
    async def _document_agent_node(self, state: WorkflowState) -> WorkflowState:
        """Document processing agent node"""
        print("[Workflow] Executing document_agent...")
        try:
            updated_state = await document_agent.process(state)
            updated_state.updated_at = datetime.utcnow().isoformat()
            return updated_state
        except Exception as e:
            print(f"[Workflow] Document agent failed: {str(e)}")
            state.json_blueprint = {"error": str(e)}
            return state
    
    async def _code_agent_node(self, state: WorkflowState) -> WorkflowState:
        """Code generation agent node"""
        print("[Workflow] Executing code_agent...")
        try:
            updated_state = await code_agent.process(state)
            updated_state.updated_at = datetime.utcnow().isoformat()
            return updated_state
        except Exception as e:
            print(f"[Workflow] Code agent failed: {str(e)}")
            state.generated_script = f"# Error: {str(e)}"
            state.platform = PlatformType.UNKNOWN
            return state
    
    async def _llm_supervisor_node(self, state: WorkflowState) -> WorkflowState:
        """LLM supervisor agent node"""
        print("[Workflow] Executing llm_supervisor...")
        try:
            updated_state = await llm_supervisor.process(state)
            updated_state.updated_at = datetime.utcnow().isoformat()
            return updated_state
        except Exception as e:
            print(f"[Workflow] LLM supervisor failed: {str(e)}")
            state.execution_result = {
                "success": False,
                "error": str(e),
                "logs": [f"Supervisor error: {str(e)}"]
            }
            return state
    
    async def _results_agent_node(self, state: WorkflowState) -> WorkflowState:
        """Results processing agent node"""
        print("[Workflow] Executing results_agent...")
        try:
            updated_state = await results_agent.process(state)
            updated_state.updated_at = datetime.utcnow().isoformat()
            return updated_state
        except Exception as e:
            print(f"[Workflow] Results agent failed: {str(e)}")
            state.final_output = {
                "success": False,
                "error": str(e),
                "message": "Result processing failed"
            }
            state.success = False
            return state
    
    async def execute(self, document_bytes: bytes, screenshots: list, 
                     parameters: Dict[str, Any]) -> WorkflowState:
        """Execute the complete workflow"""
        try:
            # Initialize workflow state with run directory
            task_id = str(uuid.uuid4())
            current_time = datetime.utcnow().isoformat()
            
            # Create run directory for artifacts
            run_dir = os.path.join(settings.GENERATED_ROOT, task_id)
            os.makedirs(run_dir, exist_ok=True)
            
            initial_state = WorkflowState(
                task_id=task_id,
                document_content=document_bytes,
                screenshots=screenshots,
                parameters=parameters,
                run_dir=run_dir,
                artifacts={},
                created_at=current_time,
                updated_at=current_time
            )
            
            print(f"[Workflow] Starting execution for task: {task_id}")
            print(f"[Workflow] Run directory: {run_dir}")
            
            # Execute the workflow
            final_state = await self.graph.ainvoke(initial_state)
            
            print(f"[Workflow] Workflow completed for task: {task_id}")
            return final_state
            
        except Exception as e:
            print(f"[Workflow] Workflow execution failed: {str(e)}")
            # Return error state
            return WorkflowState(
                task_id=task_id if 'task_id' in locals() else str(uuid.uuid4()),
                document_content=document_bytes,
                screenshots=screenshots,
                parameters=parameters,
                run_dir=run_dir if 'run_dir' in locals() else None,
                artifacts={},
                final_output={
                    "success": False,
                    "error": str(e),
                    "message": "Workflow execution failed"
                },
                success=False,
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat()
            )
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Get information about the workflow"""
        return {
            "name": "Document Automation Workflow",
            "agents": [
                "document_agent",
                "code_agent", 
                "llm_supervisor",
                "results_agent"
            ],
            "flow": "document_agent -> code_agent -> llm_supervisor -> results_agent",
            "estimated_duration": "6.5 minutes",
            "supported_platforms": ["web", "mobile"],
            "artifacts_root": settings.GENERATED_ROOT
        }

# Global workflow instance
automation_workflow = AutomationWorkflow()