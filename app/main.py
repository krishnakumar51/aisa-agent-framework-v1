"""
Complete Main.py - Generic Multi-Agent Automation System
Updated with Claude 4 Sonnet - API Only Version (No Static Frontend)
Modified for external frontend with defined backend APIs
"""
import asyncio
import json
import os
import uuid
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

# FastAPI imports
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask
from contextlib import asynccontextmanager

# System imports
from pathlib import Path
import logging
import sys

# Application imports
from app.workflow.graph import workflow
from app.config.settings import get_settings

# Global variables
task_status_store: Dict[str, Dict[str, Any]] = {}
settings = get_settings()

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add this at the VERY TOP, before logging.basicConfig
os.makedirs("logs", exist_ok=True)
# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/automation.log', mode='a', encoding='utf-8')  # Add UTF-8 encoding
    ]
)
logger = logging.getLogger(__name__)

# Create logs directory
os.makedirs("logs", exist_ok=True)
os.makedirs(settings.generated_root, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    print("🚀 Document Automation Framework v1.1.0 starting up...")
    print(f"📊 Available models: ['claude-4-sonnet', 'claude-sonnet-4', 'openai-gpt4', 'gemini-flash']")
    print(f"🔧 Default model: {settings.default_model}")
    print(f"📁 Artifacts directory: {settings.generated_root}")
    print(f"🌐 CORS enabled: {settings.enable_cors}")
    print("✨ Enhanced agents with Claude 4 Sonnet loaded")
    print("🎯 API Only Mode - No built-in frontend")
    
    yield
    
    # Shutdown
    print("📝 Saving task status...")
    await save_task_status_to_file()
    print("🛑 Document Automation Framework shutting down...")

# FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Generic Multi-Agent Automation System with Claude 4 Sonnet - API Only",
    lifespan=lifespan
)

# CORS middleware - Configure for your specific frontend domains
if settings.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Replace with your frontend domains: ["https://your-frontend.com"]
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.api_version,
        "default_model": settings.default_model,
        "active_tasks": len(task_status_store),
        "mode": "api_only"
    }

# Main automation endpoint
@app.post("/automate")
async def automate_endpoint(
    instruction: str = Form(...),
    platform: str = Form("auto-detect"),
    additional_data: str = Form("{}"),
    files: List[UploadFile] = File(...)
):
    """
    Enhanced automation endpoint with Claude 4 Sonnet
    
    Args:
        instruction: The automation task description
        platform: Target platform (web, mobile, or auto-detect)
        additional_data: JSON string with additional user data
        files: List of uploaded files (PDFs, screenshots)
    
    Returns:
        Task information and status
    """
    start_time = time.time()
    task_id = f"{uuid.uuid4().hex[:12]}"
    
    try:
        logger.info(f"[API] New automation request - Task ID: {task_id}")
        logger.info(f"[API] Instruction: {instruction}")
        logger.info(f"[API] Platform: {platform}")
        logger.info(f"[API] Files: {len(files)}")
        
        # Parse additional data with enhanced error handling
        try:
            additional_data_dict = json.loads(additional_data) if additional_data != "{}" else {}
        except json.JSONDecodeError as e:
            additional_data_dict = {}
            logger.warning(f"[API] Invalid additional_data JSON: {str(e)}, using empty dict")
        
        # Enhanced file processing
        document_content = b""
        screenshots = []
        processed_files = []
        
        for file in files:
            if not file.filename:
                continue
                
            logger.info(f"[API] Processing file: {file.filename} ({file.content_type})")
            
            try:
                file_content = await file.read()
                file_info = {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size": len(file_content)
                }
                
                if file.filename.lower().endswith('.pdf'):
                    document_content = file_content
                    file_info["type"] = "document"
                    logger.info(f"[API] PDF document: {len(file_content)} bytes")
                    
                elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    screenshots.append(file_content)
                    file_info["type"] = "screenshot"
                    logger.info(f"[API] Screenshot: {len(file_content)} bytes")
                    
                else:
                    # Try to read as text for other file types
                    try:
                        text_content = file_content.decode('utf-8')
                        if document_content:
                            document_content += f"\\n\\n--- {file.filename} ---\\n{text_content}".encode('utf-8')
                        else:
                            document_content = f"--- {file.filename} ---\\n{text_content}".encode('utf-8')
                        file_info["type"] = "text"
                        logger.info(f"[API] Text file: {len(file_content)} bytes")
                    except UnicodeDecodeError:
                        logger.warning(f"[API] Skipping unsupported file: {file.filename}")
                        continue
                
                processed_files.append(file_info)
                
            except Exception as e:
                logger.error(f"[API] Error processing file {file.filename}: {str(e)}")
                continue
        
        # Create fallback document if no content
        if not document_content and not screenshots:
            fallback_content = f"""
Automation Task Request
=====================

Task: {instruction}
Platform: {platform}
Requested at: {datetime.utcnow().isoformat()}

Additional Data:
{json.dumps(additional_data_dict, indent=2)}

Note: This is a generated document as no files were provided.
The automation system will work with the task description above.
"""
            document_content = fallback_content.encode('utf-8')
            logger.info("[API] Created fallback document content")
        
        # Enhanced task categorization
        task_category = categorize_task(instruction)
        estimated_time = estimate_completion_time(task_category, len(screenshots), len(document_content))
        
        # Initialize comprehensive task status
        task_status_store[task_id] = {
            "task_id": task_id,
            "status": "processing",
            "current_agent": "initializing",
            "progress": {
                "phase": "initialization",
                "phase_progress": 0,
                "overall_progress": 0,
                "current_step": "Preparing automation workflow...",
                "estimated_completion": (datetime.utcnow().replace(tzinfo=timezone.utc) + 
                                       estimated_time).isoformat()
            },
            "task_info": {
                "instruction": instruction,
                "platform": platform,
                "task_category": task_category,
                "files_processed": processed_files,
                "document_size": len(document_content),
                "screenshots_count": len(screenshots),
                "additional_data_keys": list(additional_data_dict.keys())
            },
            "created_at": datetime.utcnow().isoformat(),
            "model_used": settings.default_model,
            "partial_results": {},
            "execution_log": []
        }
        
        # Prepare comprehensive task configuration
        task_config = {
            "task_id": task_id,
            "instruction": instruction,
            "platform": platform,
            "additional_data": additional_data_dict,
            "document_content": document_content,
            "screenshots": screenshots,
            "processed_files": processed_files,
            "task_category": task_category,
            "model_config": {
                "default_model": settings.default_model,
                "max_retries": settings.max_retries,
                "workflow_timeout": settings.workflow_timeout
            }
        }
        
        # Start enhanced background workflow
        background_task = BackgroundTask(
            execute_enhanced_workflow_background,
            task_id=task_id,
            task_config=task_config
        )
        
        processing_time = time.time() - start_time
        
        # Return enhanced immediate response
        return JSONResponse(
            content={
                "success": True,
                "task_id": task_id,
                "message": "Generic multi-agent automation workflow started with Claude 4 Sonnet",
                "status": "processing",
                "platform": platform,
                "task_category": task_category,
                "confidence": 0.85,
                "confidence_level": "high",
                "processing_time": round(processing_time, 3),
                "files_processed": len(processed_files),
                "estimated_completion_time": estimated_time.total_seconds(),
                "model_used": settings.default_model,
                "run_directory": f"{settings.generated_root}/{task_id}",
                "status_endpoint": f"/status/{task_id}",
                "results_endpoint": f"/results/{task_id}",
                "artifacts_endpoint": f"/artifacts/{task_id}",
                "features": [
                    "claude_4_sonnet_integration",
                    "multi_agent_collaboration",
                    "real_script_execution",
                    "comprehensive_logging",
                    "agent_2_3_communication",
                    "progressive_retry_logic",
                    "artifact_generation"
                ]
            },
            background=background_task
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Failed to start automation: {str(e)}"
        logger.error(f"[API] Automation endpoint error: {error_msg}")
        
        return JSONResponse(
            content={
                "success": False,
                "error": error_msg,
                "error_type": type(e).__name__,
                "task_id": task_id,
                "processing_time": round(processing_time, 3),
                "message": "Automation request failed during initialization",
                "support_info": {
                    "check_logs": "logs/automation.log",
                    "health_endpoint": "/health",
                    "documentation": "/docs"
                }
            },
            status_code=500
        )

# Enhanced background workflow execution
async def execute_enhanced_workflow_background(task_id: str, task_config: Dict[str, Any]):
    """Execute enhanced workflow in background with comprehensive error handling"""
    workflow_start_time = time.time()
    
    try:
        logger.info(f"[API] Starting enhanced background workflow for task: {task_id}")
        logger.info(f"[API] Platform: {task_config.get('platform', 'auto-detect')}")
        logger.info(f"[API] Task category: {task_config.get('task_category', 'automation')}")
        logger.info(f"[API] Instruction: {task_config.get('instruction', 'Unknown')}")
        logger.info(f"[API] Model: {task_config.get('model_config', {}).get('default_model', 'unknown')}")
        
        # Update status to starting
        await update_task_status(task_id, {
            "status": "processing",
            "current_agent": "workflow_orchestrator",
            "progress": {
                "phase": "starting",
                "phase_progress": 5,
                "overall_progress": 5,
                "current_step": "Initializing multi-agent workflow with Claude 4 Sonnet...",
            }
        })
        
        # Add thoughtful delay for Claude 4 Sonnet processing
        await asyncio.sleep(3)
        
        # Execute the enhanced workflow
        result = await workflow.execute(
            document_content=task_config["document_content"],
            screenshots=task_config.get("screenshots", []),
            parameters={
                "instruction": task_config["instruction"],
                "platform": task_config.get("platform", "auto-detect"),
                "additional_data": task_config.get("additional_data", {}),
                "task_category": task_config.get("task_category", "automation"),
                "model_config": task_config.get("model_config", {})
            },
            run_dir=f"{settings.generated_root}/{task_id}"
        )
        
        workflow_time = time.time() - workflow_start_time
        
        # Handle different result types
        if isinstance(result, dict):
            # Convert dict result to proper state object
            final_state = create_state_object_from_dict(result, task_id)
        else:
            # Assume it's already a proper state object
            final_state = result
        
        # Determine final success status
        success_status = " SUCCESS" if final_state.success else " FAILED"
        final_message = "Workflow completed successfully" if final_state.success else "Workflow execution failed"
        
        if hasattr(final_state, 'final_output') and final_state.final_output:
            final_message = final_state.final_output.get('message', final_message)
        
        # Update final task status
        await update_task_status(task_id, {
            "status": "completed" if final_state.success else "failed",
            "current_agent": "workflow_completed",
            "progress": {
                "phase": "completed",
                "phase_progress": 100,
                "overall_progress": 100,
                "current_step": final_message,
            },
            "final_result": final_state.final_output if hasattr(final_state, 'final_output') and final_state.final_output else {
                "success": final_state.success,
                "message": final_message
            },
            "completed_at": datetime.utcnow().isoformat(),
            "total_execution_time": workflow_time,
            "workflow_summary": getattr(final_state, 'workflow_summary', {})
        })
        
        logger.info(f"[API] Enhanced workflow completed for task {task_id}: {success_status}")
        logger.info(f"[API] Total execution time: {workflow_time:.2f} seconds")
        logger.info(f"[API] Final message: {final_message}")
        
    except Exception as e:
        workflow_time = time.time() - workflow_start_time
        error_msg = str(e)
        error_type = type(e).__name__
        
        logger.error(f"[API] Enhanced workflow failed for task {task_id}: {error_msg}")
        logger.error(f"[API] Error type: {error_type}")
        logger.error(f"[API] Execution time before failure: {workflow_time:.2f} seconds")
        
        # Create comprehensive error state
        error_state = create_error_state_object(task_id, error_msg, error_type)
        
        # Update task status with detailed error information
        await update_task_status(task_id, {
            "status": "failed",
            "current_agent": "error_handler",
            "progress": {
                "phase": "failed",
                "phase_progress": 0,
                "overall_progress": 0,
                "current_step": f"Workflow failed: {error_msg}",
            },
            "error": {
                "message": error_msg,
                "type": error_type,
                "timestamp": datetime.utcnow().isoformat()
            },
            "final_result": error_state.final_output,
            "failed_at": datetime.utcnow().isoformat(),
            "execution_time_before_failure": workflow_time
        })

# Task status endpoint
@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Get real-time task status and progress"""
    if task_id not in task_status_store:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    status = task_status_store[task_id]
    
    # Calculate dynamic progress if still processing
    if status["status"] == "processing":
        elapsed_time = (datetime.utcnow() - datetime.fromisoformat(status["created_at"])).total_seconds()
        estimated_total = status.get("progress", {}).get("estimated_completion")
        
        if estimated_total:
            try:
                estimated_datetime = datetime.fromisoformat(estimated_total.replace('Z', '+00:00'))
                total_estimated_seconds = (estimated_datetime - datetime.fromisoformat(status["created_at"])).total_seconds()
                dynamic_progress = min(95, (elapsed_time / total_estimated_seconds) * 100)
                status["progress"]["dynamic_progress"] = round(dynamic_progress, 1)
            except:
                pass
    
    return {
        "task_id": task_id,
        "status": status["status"],
        "current_agent": status.get("current_agent", "unknown"),
        "progress": status.get("progress", {}),
        "task_info": status.get("task_info", {}),
        "partial_results": status.get("partial_results", {}),
        "error": status.get("error"),
        "created_at": status["created_at"],
        "model_used": status.get("model_used", settings.default_model),
        "execution_log": status.get("execution_log", [])[-10:]  # Last 10 entries
    }

# Results endpoint
@app.get("/results/{task_id}")
async def get_task_results(task_id: str):
    """Get final automation results"""
    if task_id not in task_status_store:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    status = task_status_store[task_id]
    
    if status["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=425, detail=f"Task {task_id} is still processing")
    
    return {
        "task_id": task_id,
        "success": status["status"] == "completed",
        "status": status["status"],
        "final_result": status.get("final_result", {}),
        "task_info": status.get("task_info", {}),
        "execution_time": status.get("total_execution_time"),
        "model_used": status.get("model_used", settings.default_model),
        "workflow_summary": status.get("workflow_summary", {}),
        "completed_at": status.get("completed_at"),
        "failed_at": status.get("failed_at"),
        "error": status.get("error"),
        "artifacts_available": f"/artifacts/{task_id}"
    }

# Task history endpoint
@app.get("/tasks")
async def list_tasks(page: int = 1, per_page: int = 20, status: Optional[str] = None):
    """List automation tasks with pagination"""
    tasks = []
    
    for task_id, task_data in task_status_store.items():
        if status and task_data["status"] != status:
            continue
            
        task_summary = {
            "task_id": task_id,
            "instruction": task_data.get("task_info", {}).get("instruction", "Unknown"),
            "status": task_data["status"],
            "platform": task_data.get("task_info", {}).get("platform", "unknown"),
            "task_category": task_data.get("task_info", {}).get("task_category", "automation"),
            "created_at": task_data["created_at"],
            "completed_at": task_data.get("completed_at"),
            "failed_at": task_data.get("failed_at"),
            "success": task_data["status"] == "completed",
            "execution_time": task_data.get("total_execution_time"),
            "model_used": task_data.get("model_used", settings.default_model),
            "confidence": task_data.get("final_result", {}).get("confidence", 0.0) if task_data.get("final_result") else 0.0
        }
        tasks.append(task_summary)
    
    # Sort by created_at descending
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Pagination
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_tasks = tasks[start_idx:end_idx]
    
    return {
        "tasks": paginated_tasks,
        "total": len(tasks),
        "page": page,
        "per_page": per_page,
        "total_pages": (len(tasks) + per_page - 1) // per_page,
        "has_next": end_idx < len(tasks),
        "has_prev": page > 1
    }

# Artifacts endpoint
@app.get("/artifacts/{task_id}")
async def get_task_artifacts(task_id: str):
    """Get generated artifacts (scripts, logs, reports)"""
    if task_id not in task_status_store:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    artifacts_dir = Path(settings.generated_root) / task_id
    
    if not artifacts_dir.exists():
        raise HTTPException(status_code=404, detail=f"Artifacts for task {task_id} not found")
    
    artifacts = {}
    
    # Common artifact files
    artifact_files = {
        "blueprint": "agent1_blueprint.json",
        "generated_script": "agent-code-generator-latest.py",
        "execution_logs": "agent3_execution_summary.json",
        "final_report": "agent4_final_report.txt",
        "final_report_json": "agent4_final_report.json",
        "conversation_log": "conversation.json",
        "workflow_summary": "workflow_summary.txt",
        "workflow_summary_json": "workflow_summary.json"
    }
    
    for name, filename in artifact_files.items():
        file_path = artifacts_dir / filename
        if file_path.exists():
            artifacts[name] = f"/download/{task_id}/{filename}"
    
    return {
        "task_id": task_id,
        "artifacts": artifacts,
        "download_urls": {
            "all_artifacts": f"/download/{task_id}/artifacts.zip"
        },
        "artifacts_directory": str(artifacts_dir)
    }

# File download endpoint
@app.get("/download/{task_id}/{filename}")
async def download_file(task_id: str, filename: str):
    """Download specific artifact file"""
    if task_id not in task_status_store:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    file_path = Path(settings.generated_root) / task_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File {filename} not found for task {task_id}")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='application/octet-stream'
    )

# Utility functions
def categorize_task(instruction: str) -> str:
    """Categorize automation task based on instruction"""
    instruction_lower = instruction.lower()
    
    if any(keyword in instruction_lower for keyword in ["account", "register", "signup", "sign up"]):
        return "account_creation"
    elif any(keyword in instruction_lower for keyword in ["form", "fill", "submit", "input"]):
        return "form_filling"
    elif any(keyword in instruction_lower for keyword in ["login", "signin", "sign in", "authenticate"]):
        return "authentication"
    elif any(keyword in instruction_lower for keyword in ["search", "find", "lookup"]):
        return "search"
    elif any(keyword in instruction_lower for keyword in ["navigate", "goto", "visit", "browse"]):
        return "navigation"
    elif any(keyword in instruction_lower for keyword in ["download", "upload", "file", "document"]):
        return "file_handling"
    elif any(keyword in instruction_lower for keyword in ["click", "tap", "select", "choose"]):
        return "interaction"
    elif any(keyword in instruction_lower for keyword in ["data", "extract", "scrape", "collect"]):
        return "data_extraction"
    else:
        return "automation"

def estimate_completion_time(task_category: str, screenshot_count: int, document_size: int) ->timedelta:
    """Estimate task completion time"""
    base_times = {
        "account_creation": 180,  # 3 minutes
        "form_filling": 120,      # 2 minutes  
        "authentication": 90,     # 1.5 minutes
        "search": 60,             # 1 minute
        "navigation": 45,         # 45 seconds
        "file_handling": 150,     # 2.5 minutes
        "interaction": 75,        # 1.25 minutes
        "data_extraction": 200,   # 3.3 minutes
        "automation": 120         # 2 minutes default
    }
    
    base_time = base_times.get(task_category, 120)
    
    # Add time for complexity factors
    if screenshot_count > 3:
        base_time += 30
    if document_size > 500000:  # 500KB
        base_time += 45
    
    return timedelta(seconds=base_time)

def create_state_object_from_dict(result_dict: Dict[str, Any], task_id: str):
    """Create state object from dictionary result"""
    class WorkflowState:
        def __init__(self):
            self.task_id = task_id
            self.success = result_dict.get('success', False)
            self.final_output = result_dict.get('final_output', {
                'success': result_dict.get('success', False),
                'message': result_dict.get('message', 'Workflow completed'),
                'confidence': result_dict.get('confidence', 0.0),
                'task_category': result_dict.get('task_category', 'automation'),
                'platform': result_dict.get('platform', 'unknown'),
                'execution_time': result_dict.get('execution_time', 0),
                'agent_collaborations': result_dict.get('agent_collaborations', 0),
                'detailed_results': result_dict.get('detailed_results', {})
            })
            self.workflow_summary = result_dict.get('workflow_summary', {})
    
    return WorkflowState()

def create_error_state_object(task_id: str, error_msg: str, error_type: str):
    """Create error state object"""
    class ErrorState:
        def __init__(self):
            self.task_id = task_id
            self.success = False
            self.final_output = {
                "success": False,
                "error": error_msg,
                "error_type": error_type,
                "message": f"❌ Workflow failed: {error_msg}",
                "confidence": 0.0,
                "task_category": "automation",
                "platform": "unknown",
                "execution_time": 0,
                "agent_collaborations": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.workflow_summary = {
                "overall_success": False,
                "error_summary": error_msg,
                "error_type": error_type
            }
    
    return ErrorState()

async def update_task_status(task_id: str, updates: Dict[str, Any]):
    """Update task status"""
    if task_id in task_status_store:
        # Update existing status
        for key, value in updates.items():
            if key == "progress" and isinstance(value, dict):
                # Merge progress updates
                if "progress" not in task_status_store[task_id]:
                    task_status_store[task_id]["progress"] = {}
                task_status_store[task_id]["progress"].update(value)
            else:
                task_status_store[task_id][key] = value
        
        # Add to execution log
        if "execution_log" not in task_status_store[task_id]:
            task_status_store[task_id]["execution_log"] = []
        
        task_status_store[task_id]["execution_log"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "updates": updates
        })

async def save_task_status_to_file():
    """Save task status to file for persistence"""
    try:
        status_file = Path("logs") / "task_status.json"
        with open(status_file, 'w') as f:
            json.dump(task_status_store, f, indent=2, default=str)
        logger.info(f"Task status saved to {status_file}")
    except Exception as e:
        logger.error(f"Failed to save task status: {str(e)}")

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Generic Multi-Agent Automation System...")
    print(f"🤖 Powered by Claude 4 Sonnet")
    print(f"🎯 API Only Mode - No Built-in Frontend")
    print(f"🌐 API: http://{settings.api_host}:{settings.api_port}")
    print(f"📖 Docs: http://{settings.api_host}:{settings.api_port}/docs")
    print(f"📊 Health: http://{settings.api_host}:{settings.api_port}/health")
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug_mode,
        log_level=settings.log_level.lower(),
        access_log=True
    )