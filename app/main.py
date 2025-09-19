"""
FastAPI main application - Entry point for the automation framework
"""
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List 
from app.config.settings import settings
from app.models.schemas import (
    AutomationRequest, AutomationResponse, TaskStatus, 
    AgentStatus, WorkflowState
)
from app.workflow.graph import automation_workflow

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Multi-agent document automation framework"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for task states (use Redis in production)
task_storage: Dict[str, WorkflowState] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    print(f"🚀 {settings.API_TITLE} v{settings.API_VERSION} starting up...")
    print(f"📊 Available models: {list(settings.MODELS.keys())}")
    print(f"🔧 Default model: {settings.DEFAULT_MODEL}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Document Automation Framework API",
        "version": settings.API_VERSION,
        "status": "running",
        "workflow_info": automation_workflow.get_workflow_info(),
        "endpoints": {
            "/automate": "POST - Execute automation workflow",
            "/status/{task_id}": "GET - Check task status",
            "/health": "GET - Health check",
            "/models": "GET - Available AI models"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.API_VERSION
    }

@app.get("/models")
async def get_available_models():
    """Get available AI models"""
    from utils.model_client import model_client
    return {
        "available_models": model_client.get_available_models(),
        "default_model": settings.DEFAULT_MODEL,
        "model_configs": {
            name: {
                "model_name": config["model_name"],
                "max_tokens": config["max_tokens"],
                "temperature": config["temperature"]
            }
            for name, config in settings.MODELS.items()
        }
    }


@app.post("/automate", response_model=AutomationResponse)
async def execute_automation(
    background_tasks: BackgroundTasks,
    document: UploadFile = File(..., description="PDF document with instructions"),
    screenshots: Optional[List[UploadFile]] = File(
        None, description="Screenshots of the UI (optional)"
    ),
    parameters: str = Form("{}", description="Additional parameters as JSON string"),
    platform: Literal["web", "mobile"] = Form(..., description="Target platform (web or mobile)"),  # NEW
    model: str = Form(settings.DEFAULT_MODEL, description="AI model to use"),
    timeout: int = Form(settings.WORKFLOW_TIMEOUT, description="Timeout in seconds")
):
    """
    Execute document automation workflow

    - document: PDF file with automation instructions
    - screenshots: Optional screenshots
    - parameters: Additional parameters in JSON format
    - platform: Target platform (web or mobile)
    - model: AI model to use
    - timeout: Maximum execution time in seconds
    """
    try:
        # Validate inputs
        if document.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Document must be a PDF file")

        # Read document content
        document_bytes = await document.read()
        if len(document_bytes) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes"
            )

        # Read screenshots (optional)
        screenshot_bytes: List[bytes] = []
        if screenshots:
            for screenshot in screenshots:
                if not screenshot.content_type or not screenshot.content_type.startswith("image/"):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid screenshot type: {screenshot.content_type}"
                    )
                img_bytes = await screenshot.read()
                screenshot_bytes.append(img_bytes)

        # Parse parameters
        try:
            import json
            params = json.loads(parameters) if parameters else {}
            if not isinstance(params, dict):
                raise ValueError("parameters must be a JSON object")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON in parameters")

        # Inject platform override into parameters so agents can honor it
        params["platform"] = platform  # "web" | "mobile"

        # Generate task ID
        task_id = str(uuid.uuid4())

        # Create initial task state
        initial_state = WorkflowState(
            task_id=task_id,
            document_content=document_bytes,
            screenshots=screenshot_bytes,
            parameters=params,
            model_used=model,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )

        # Store task state
        task_storage[task_id] = initial_state

        # Execute workflow in background
        background_tasks.add_task(
            execute_workflow_background,
            task_id,
            document_bytes,
            screenshot_bytes,
            params
        )

        return AutomationResponse(
            task_id=task_id,
            status=AgentStatus.PROCESSING,
            message="Automation workflow started successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start automation: {str(e)}")

@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """
    Get the status of a specific automation task
    
    - **task_id**: The unique identifier for the task
    """
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    state = task_storage[task_id]
    
    # Determine current status
    if state.final_output:
        status = AgentStatus.COMPLETED
        progress = 1.0
    elif state.execution_result:
        status = AgentStatus.PROCESSING
        progress = 0.75
    elif state.generated_script:
        status = AgentStatus.PROCESSING
        progress = 0.5
    elif state.json_blueprint:
        status = AgentStatus.PROCESSING
        progress = 0.25
    else:
        status = AgentStatus.PROCESSING
        progress = 0.1
    
    # Build steps information
    steps = []
    if state.json_blueprint:
        steps.append({
            "agent": "document_agent",
            "status": "completed" if "error" not in (state.json_blueprint or {}) else "failed",
            "description": "PDF and screenshot analysis"
        })
    
    if state.generated_script:
        steps.append({
            "agent": "code_agent",
            "status": "completed" if not state.generated_script.startswith("# Error") else "failed",
            "description": f"Script generation for {state.platform}"
        })
    
    if state.execution_result:
        steps.append({
            "agent": "llm_supervisor",
            "status": "completed" if state.execution_result.get("success") else "failed",
            "description": "Script execution and supervision"
        })
    
    if state.final_output:
        steps.append({
            "agent": "results_agent",
            "status": "completed",
            "description": "Result validation and formatting"
        })
    
    return TaskStatus(
        task_id=task_id,
        status=status,
        current_agent=state.current_agent,
        progress=progress,
        steps=steps,
        result=state.final_output,
        error=state.final_output.get("error") if state.final_output else None,
        created_at=state.created_at,
        updated_at=state.updated_at
    )

async def execute_workflow_background(task_id: str, document_bytes: bytes, 
                                    screenshots: List[bytes], parameters: Dict[str, Any]):
    """Execute workflow in background"""
    try:
        print(f"[API] Starting background workflow for task: {task_id}")
        
        # Execute the workflow
        final_state = await automation_workflow.execute(
            document_bytes, screenshots, parameters
        )
        
        # Update task storage
        task_storage[task_id] = final_state
        
        print(f"[API] Background workflow completed for task: {task_id}")
        
    except Exception as e:
        print(f"[API] Background workflow failed for task {task_id}: {str(e)}")
        
        # Update with error state
        if task_id in task_storage:
            error_state = task_storage[task_id]
            error_state.final_output = {
                "success": False,
                "error": str(e),
                "message": "Background workflow execution failed"
            }
            error_state.success = False
            error_state.updated_at = datetime.utcnow().isoformat()
            task_storage[task_id] = error_state

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a completed task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del task_storage[task_id]
    return {"message": f"Task {task_id} deleted successfully"}

@app.get("/tasks")
async def list_tasks():
    """List all tasks"""
    return {
        "tasks": [
            {
                "task_id": task_id,
                "status": "completed" if state.final_output else "processing",
                "created_at": state.created_at,
                "updated_at": state.updated_at
            }
            for task_id, state in task_storage.items()
        ],
        "total": len(task_storage)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info"
    )