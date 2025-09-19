"""
Pydantic models for the automation framework
"""
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum

class PlatformType(str, Enum):
    WEB = "web"
    MOBILE = "mobile"
    UNKNOWN = "unknown"

class AgentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowState(BaseModel):
    """State object passed between agents in the workflow"""
    task_id: str = Field(..., description="Unique task identifier")
    document_content: Optional[bytes] = Field(None, description="PDF document content")
    screenshots: List[bytes] = Field(default_factory=list, description="Screenshot images")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="User parameters")
    
    # Run directory for artifacts
    run_dir: Optional[str] = Field(None, description="Directory for run artifacts")
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Artifact paths and metadata")
    
    # Agent 1 outputs
    json_blueprint: Optional[Dict[str, Any]] = Field(None, description="Parsed UI blueprint")
    extracted_text: Optional[str] = Field(None, description="Extracted text from PDF")
    ui_elements: List[Dict[str, Any]] = Field(default_factory=list, description="Detected UI elements")
    
    # Agent 2 outputs
    platform: Optional[PlatformType] = Field(None, description="Detected platform")
    generated_script: Optional[str] = Field(None, description="Generated automation script")
    script_language: Optional[str] = Field(None, description="Script language (python/javascript)")
    
    # Agent 3 outputs
    execution_result: Optional[Dict[str, Any]] = Field(None, description="Script execution result")
    execution_logs: List[str] = Field(default_factory=list, description="Execution logs")
    screenshots_taken: List[bytes] = Field(default_factory=list, description="Screenshots during execution")
    
    # Agent 4 outputs
    final_output: Optional[Dict[str, Any]] = Field(None, description="Final validated result")
    success: Optional[bool] = Field(None, description="Overall success status")
    
    # Workflow metadata
    current_agent: Optional[str] = Field(None, description="Currently processing agent")
    model_used: Optional[str] = Field("claude-sonnet", description="AI model used")
    created_at: Optional[str] = Field(None, description="Task creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

class AutomationRequest(BaseModel):
    """Request model for automation endpoint"""
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional parameters")
    model: Optional[str] = Field("claude-sonnet", description="AI model to use")
    timeout: Optional[int] = Field(600, description="Timeout in seconds")

class AutomationResponse(BaseModel):
    """Response model for automation endpoint"""
    task_id: str = Field(..., description="Unique task identifier")
    status: AgentStatus = Field(..., description="Current task status")
    message: str = Field(..., description="Status message")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result if completed")

class TaskStatus(BaseModel):
    """Task status response model"""
    task_id: str
    status: AgentStatus
    current_agent: Optional[str] = None
    progress: float = Field(0.0, ge=0.0, le=1.0, description="Progress percentage (0-1)")
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str
    run_dir: Optional[str] = None
    artifacts: Dict[str, Any] = Field(default_factory=dict)

class UIElement(BaseModel):
    """UI element detected from screenshots"""
    type: str = Field(..., description="Element type (button, input, text, etc.)")
    text: Optional[str] = Field(None, description="Element text content")
    coordinates: Dict[str, int] = Field(..., description="Element coordinates")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Element attributes")
    selector: Optional[str] = Field(None, description="CSS/XPath selector")

class BlueprintStep(BaseModel):
    """Individual step in the automation blueprint"""
    step_number: int = Field(..., description="Step sequence number")
    action: str = Field(..., description="Action to perform")
    target: Dict[str, Any] = Field(..., description="Target element or area")
    input_data: Optional[str] = Field(None, description="Data to input")
    expected_result: Optional[str] = Field(None, description="Expected outcome")
    screenshot_reference: Optional[int] = Field(None, description="Reference screenshot index")

class AutomationBlueprint(BaseModel):
    """Complete automation blueprint"""
    title: str = Field(..., description="Blueprint title")
    platform: PlatformType = Field(..., description="Target platform")
    steps: List[BlueprintStep] = Field(..., description="Automation steps")
    ui_elements: List[UIElement] = Field(default_factory=list, description="UI elements")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class ExecutionStep(BaseModel):
    """Individual execution step result"""
    step_number: int
    action: str
    success: bool
    duration: float
    error: Optional[str] = None
    screenshot: Optional[bytes] = None
    details: Dict[str, Any] = Field(default_factory=dict)

class ExecutionResult(BaseModel):
    """Complete execution result"""
    success: bool
    steps: List[ExecutionStep]
    total_duration: float
    final_state: Dict[str, Any] = Field(default_factory=dict)
    screenshots: List[bytes] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)