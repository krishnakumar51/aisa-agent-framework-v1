"""
Updated main.py with Testing Environment Integration
FastAPI application with complete 4-agent workflow and sequential task management
"""
import asyncio
import json
import os
import time
import logging
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

# FastAPI imports
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from starlette.background import BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Application imports - Updated to use new orchestrator
from app.main_orchestrator import get_updated_orchestrator
from app.database.database_manager import get_testing_db
from app.langgraph_orchestrator import get_langgraph_orchestrator
# Global variables
task_status_store: Dict[str, Dict[str, Any]] = {}

# Enhanced logging configuration with UTF-8 support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

os.makedirs("logs", exist_ok=True)
os.makedirs("generated_code", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/automation.log', mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enhanced application lifespan handler with SQLite integration"""
    # Startup
    print("🚀 Updated Multi-Agent Automation Framework v2.0.0 starting up...")
    print("🤖 4-Agent System with Testing Environment Integration")
    print("📊 Features: Sequential IDs, Virtual Environments, OCR Validation, Agent Communication")
    print("🗄️ SQLite Database: sqlite_db.sqlite")
    print("📁 Generated Code Directory: generated_code/")
    print("🌐 CORS enabled for all origins")
    
    # Initialize updated orchestrator and database
    try:
        updated_orchestrator = await get_updated_orchestrator()
        db_manager = await get_testing_db()
        print("✅ Updated multi-agent orchestrator system initialized successfully")
        print("✅ SQLite database with testing environment tracking ready")
        print("🤖 All 4 agents initialized:")
        print("   🔵 Agent 1: Blueprint Generation")
        print("   🟢 Agent 2: Code Generation & Requirements")
        print("   🟡 Agent 3: Testing Environment & Execution")
        print("   🔵 Agent 4: Final Reporting & CSV Export")
        print("📋 Sequential task tracking enabled")
        print("💬 Agent-to-agent communication with database persistence")
        print("🧪 Virtual environment setup and management")
        print("🖼️ OCR validation and screenshot capture")
    except Exception as e:
        print(f"⚠️ Orchestrator initialization warning: {str(e)}")
    
    yield
    
    # Shutdown
    print("📝 Saving final task status...")
    await save_task_status_to_file()
    
    # Close database connections
    try:
        db_manager = await get_testing_db()
        # Note: aiosqlite connections are automatically closed
        print("🔒 Database connections closed")
    except:
        pass
        
    print("🛑 Updated Multi-Agent Automation Framework shutting down...")

# FastAPI app with enhanced lifespan
app = FastAPI(
    title="Updated Multi-Agent Automation System with Testing Environment",
    version="2.0.0",
    description="Complete 4-agent system with SQLite database, testing environment setup, and OCR validation",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Enhanced health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check with database and agent status"""
    try:
        db_manager = await get_testing_db()
        orchestrator = await get_updated_orchestrator()
        
        # Get recent tasks count
        recent_tasks = await orchestrator.list_recent_tasks(5)
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "system": "updated_multi_agent_automation",
            "database": {
                "status": "connected",
                "type": "SQLite",
                "file": db_manager.db_path,
                "recent_tasks": len(recent_tasks)
            },
            "agents": {
                "total_agents": 4,
                "agent1": "UpdatedAgent1_BlueprintGenerator",
                "agent2": "UpdatedAgent2_CodeGenerator", 
                "agent3": "UpdatedAgent3_TestingEnvironment",
                "agent4": "UpdatedAgent4_FinalReporter"
            },
            "features": [
                "sequential_task_ids",
                "testing_environment_setup",
                "virtual_environment_management",
                "agent_to_agent_communication",
                "ocr_screenshot_validation",
                "sqlite_workflow_persistence",
                "comprehensive_reporting",
                "csv_data_export"
            ],
            "folder_structure": {
                "base": "generated_code/",
                "pattern": "generated_code/{seq_id}/agent{1-4}/",
                "testing": "generated_code/{seq_id}/agent3/testing/"
            },
            "orchestrator_initialized": orchestrator.initialized,
            "mode": "api_only"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0"
        }

# Updated automation endpoint
@app.post("/automate")
async def updated_automate_endpoint(
    instruction: str = Form(...),
    platform: str = Form("auto-detect"),
    additional_data: str = Form("{}"),
    files: List[UploadFile] = File([]),
    background_tasks: BackgroundTasks = None
):
    """
    Updated automation endpoint with testing environment integration
    
    Args:
        instruction: The automation task description (e.g., "Create an account with name Krishna Kumar and DOB 19 Sep 2000")
        platform: Target platform (web, mobile, or auto-detect)
        additional_data: JSON string with additional user data
        files: List of uploaded files (PDFs, screenshots)
        background_tasks: FastAPI background tasks handler
    
    Returns:
        Enhanced task information with sequential ID and testing environment setup
    """
    start_time = time.time()
    temp_task_id = f"temp_{int(time.time())}"
    
    try:
        logger.info(f"[API] Updated automation request - Temp ID: {temp_task_id}")
        logger.info(f"[API] Instruction: {instruction}")
        logger.info(f"[API] Platform: {platform}")
        logger.info(f"[API] Files: {len(files)}")
        
        # Parse additional data
        try:
            additional_data_dict = json.loads(additional_data) if additional_data != "{}" else {}
        except json.JSONDecodeError:
            additional_data_dict = {}
            logger.warning(f"[API] Invalid additional_data JSON, using empty dict")
        
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
                    
                elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    screenshots.append(file_content)
                    file_info["type"] = "screenshot"
                    
                else:
                    # Try to read as text
                    try:
                        text_content = file_content.decode('utf-8')
                        if document_content:
                            document_content += f"\\n\\n--- {file.filename} ---\\n{text_content}".encode('utf-8')
                        else:
                            document_content = f"--- {file.filename} ---\\n{text_content}".encode('utf-8')
                        file_info["type"] = "text"
                    except UnicodeDecodeError:
                        logger.warning(f"[API] Skipping unsupported file: {file.filename}")
                        continue
                
                processed_files.append(file_info)
                
            except Exception as e:
                logger.error(f"[API] Error processing file {file.filename}: {str(e)}")
                continue
        
        # Create fallback document if needed
        if not document_content and not screenshots:
            fallback_content = f"""
Updated Automation Task Request
==============================

Task: {instruction}
Platform: {platform}
Requested at: {datetime.utcnow().isoformat()}

Additional Data:
{json.dumps(additional_data_dict, indent=2)}

Note: This is a generated document as no files were provided.
The updated 4-agent system will work with the task description above.
"""
            document_content = fallback_content.encode('utf-8')
            logger.info("[API] Created fallback document content")
        
        # Enhanced task categorization and estimation
        task_category = categorize_task(instruction)
        estimated_time = estimate_completion_time(task_category, len(screenshots), len(document_content))
        
        # Initialize comprehensive task status
        task_status_store[temp_task_id] = {
            "temp_task_id": temp_task_id,
            "status": "initializing",
            "current_agent": "orchestrator",
            "progress": {
                "phase": "initialization",
                "phase_progress": 0,
                "overall_progress": 0,
                "current_step": "Starting updated multi-agent workflow...",
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
            "updated_features": {
                "sequential_task_ids": True,
                "testing_environment": True,
                "virtual_environment_setup": True,
                "agent_communication": True,
                "ocr_validation": True,
                "sqlite_persistence": True,
                "csv_export": True
            },
            "folder_structure": {
                "agent1": "blueprint generation",
                "agent2": "code generation + requirements",
                "agent3_testing": "virtual environment + test execution",
                "agent4": "final reports + CSV export"
            },
            "partial_results": {},
            "execution_log": []
        }
        
        # Prepare task configuration
        task_config = {
            "temp_task_id": temp_task_id,
            "instruction": instruction,
            "platform": platform,
            "additional_data": additional_data_dict,
            "document_content": document_content,
            "screenshots": screenshots,
            "processed_files": processed_files,
            "task_category": task_category
        }
        
        # Start updated background workflow
        if background_tasks:
            background_tasks.add_task(
                execute_updated_workflow_background,
                temp_task_id=temp_task_id,
                task_config=task_config
            )
        else:
            # For backwards compatibility
            asyncio.create_task(execute_updated_workflow_background(temp_task_id, task_config))
        
        processing_time = time.time() - start_time
        
        # Return enhanced immediate response
        return JSONResponse(
            content={
                "success": True,
                "temp_task_id": temp_task_id,
                "message": "Updated 4-agent automation workflow started with testing environment integration",
                "status": "initializing",
                "platform": platform,
                "task_category": task_category,
                "confidence": 0.95,
                "confidence_level": "very_high",
                "processing_time": round(processing_time, 3),
                "files_processed": len(processed_files),
                "estimated_completion_time": estimated_time.total_seconds(),
                "system_version": "2.0.0",
                "workflow_type": "updated_multi_agent_testing_environment",
                "agents_count": 4,
                "status_endpoint": f"/status/{temp_task_id}",
                "results_endpoint": f"/results/{temp_task_id}",
                "enhanced_features": [
                    "sequential_task_ids",
                    "testing_environment_setup", 
                    "virtual_environment_management",
                    "real_time_agent_communication",
                    "ocr_screenshot_validation",
                    "sqlite_workflow_persistence",
                    "comprehensive_csv_export",
                    "automated_retry_with_improvements",
                    "folder_structure_management"
                ]
            }
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Failed to start updated automation: {str(e)}"
        logger.error(f"[API] Updated automation endpoint error: {error_msg}")
        
        return JSONResponse(
            content={
                "success": False,
                "error": error_msg,
                "error_type": type(e).__name__,
                "temp_task_id": temp_task_id,
                "processing_time": round(processing_time, 3),
                "message": "Updated automation request failed during initialization",
                "system_version": "2.0.0"
            },
            status_code=500
        )

# Updated background workflow execution
async def execute_updated_workflow_background(temp_task_id: str, task_config: Dict[str, Any]):
    """Execute updated workflow in background with testing environment integration"""
    workflow_start_time = time.time()
    seq_id = None
    
    try:
        logger.info(f"[API] Starting updated background workflow for task: {temp_task_id}")
        logger.info(f"[API] Platform: {task_config.get('platform', 'auto-detect')}")
        logger.info(f"[API] Task category: {task_config.get('task_category', 'automation')}")
        logger.info(f"[API] Instruction: {task_config.get('instruction', 'Unknown')}")
        logger.info(f"[API] Testing environment integration: Enabled")
        
        # Update status to starting
        await update_task_status(temp_task_id, {
            "status": "starting",
            "current_agent": "orchestrator",
            "progress": {
                "phase": "starting",
                "phase_progress": 5,
                "overall_progress": 5,
                "current_step": "Initializing updated 4-agent workflow with testing environment...",
            }
        })
        
        # Small delay for system initialization
        await asyncio.sleep(2)
        
        # Get updated orchestrator and execute
        orchestrator = await get_updated_orchestrator()
        
        result = await orchestrator.execute_complete_workflow(
            document_content=task_config["document_content"],
            screenshots=task_config.get("screenshots", []),
            instruction=task_config["instruction"],
            platform=task_config.get("platform", "auto-detect"),
            additional_data=task_config.get("additional_data", {})
        )
        
        workflow_time = time.time() - workflow_start_time
        
        # Extract results
        success = result.get('success', False)
        seq_id = result.get('seq_id')
        base_path = result.get('base_path', 'N/A')
        final_confidence = result.get('final_confidence', 0.0)
        performance_grade = result.get('performance_grade', 'Unknown')
        final_message = result.get('message', 'Updated workflow completed')
        
        # Update final task status
        await update_task_status(temp_task_id, {
            "status": "completed" if success else "failed",
            "current_agent": "orchestrator_completed",
            "progress": {
                "phase": "completed",
                "phase_progress": 100,
                "overall_progress": 100,
                "current_step": final_message,
            },
            "final_result": {
                "success": success,
                "sequential_task_id": seq_id,
                "base_path": base_path,
                "message": final_message,
                "confidence": final_confidence,
                "performance_grade": performance_grade,
                "execution_time": workflow_time,
                "folder_structure": result.get('workflow_summary', {}).get('folder_structure', {}),
                "key_metrics": result.get('workflow_summary', {}).get('key_metrics', {}),
                "detailed_results": result
            },
            "completed_at": datetime.utcnow().isoformat(),
            "total_execution_time": workflow_time,
            "workflow_summary": result.get('workflow_summary', {}),
            "testing_environment": {
                "enabled": True,
                "sequential_task_id": seq_id,
                "base_path": base_path
            }
        })
        
        status_emoji = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"[API] Updated workflow completed for task {temp_task_id}: {status_emoji}")
        logger.info(f"[API] Sequential task ID: {seq_id}")
        logger.info(f"[API] Base path: {base_path}")
        logger.info(f"[API] Total execution time: {workflow_time:.2f} seconds")
        logger.info(f"[API] Final message: {final_message}")
        logger.info(f"[API] Performance grade: {performance_grade}")
        
    except Exception as e:
        workflow_time = time.time() - workflow_start_time
        error_msg = str(e)
        error_type = type(e).__name__
        
        logger.error(f"[API] Updated workflow failed for task {temp_task_id}: {error_msg}")
        logger.error(f"[API] Error type: {error_type}")
        logger.error(f"[API] Execution time before failure: {workflow_time:.2f} seconds")
        
        # Update task status with error information
        await update_task_status(temp_task_id, {
            "status": "failed",
            "current_agent": "orchestrator_error",
            "progress": {
                "phase": "failed",
                "phase_progress": 0,
                "overall_progress": 0,
                "current_step": f"Updated workflow failed: {error_msg}",
            },
            "error": {
                "message": error_msg,
                "type": error_type,
                "timestamp": datetime.utcnow().isoformat(),
                "system": "updated_multi_agent_workflow"
            },
            "final_result": {
                "success": False,
                "sequential_task_id": seq_id,
                "message": f"Updated workflow failed: {error_msg}",
                "confidence": 0.0,
                "error_details": error_msg
            },
            "failed_at": datetime.utcnow().isoformat(),
            "execution_time_before_failure": workflow_time,
            "testing_environment": {
                "enabled": True,
                "error": "Workflow execution failed"
            }
        })

# Enhanced status endpoint
@app.get("/status/{task_id}")
async def get_updated_task_status(task_id: str):
    """Get enhanced task status with testing environment information"""
    if task_id not in task_status_store:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    status = task_status_store[task_id]
    
    # Add testing environment information if available
    testing_env_info = {}
    if "testing_environment" in status:
        seq_id = status["testing_environment"].get("sequential_task_id")
        if seq_id:
            try:
                orchestrator = await get_updated_orchestrator()
                task_status_result = await orchestrator.get_task_status(seq_id)
                testing_env_info = {
                    "sequential_task_id": seq_id,
                    "task_status": task_status_result
                }
            except Exception as e:
                testing_env_info = {"error": str(e)}
    
    return {
        "temp_task_id": task_id,
        "status": status["status"],
        "current_agent": status.get("current_agent", "unknown"),
        "progress": status.get("progress", {}),
        "task_info": status.get("task_info", {}),
        "partial_results": status.get("partial_results", {}),
        "error": status.get("error"),
        "created_at": status["created_at"],
        "execution_log": status.get("execution_log", [])[-10:],  # Last 10 entries
        "updated_features": status.get("updated_features", {}),
        "folder_structure": status.get("folder_structure", {}),
        "testing_environment": testing_env_info,
        "system_version": "2.0.0"
    }

# Results endpoint
@app.get("/results/{task_id}")
async def get_updated_task_results(task_id: str):
    """Get enhanced final automation results"""
    if task_id not in task_status_store:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    status = task_status_store[task_id]
    
    if status["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=425, detail=f"Task {task_id} is still processing")
    
    return {
        "temp_task_id": task_id,
        "success": status["status"] == "completed",
        "status": status["status"],
        "final_result": status.get("final_result", {}),
        "task_info": status.get("task_info", {}),
        "execution_time": status.get("total_execution_time"),
        "workflow_summary": status.get("workflow_summary", {}),
        "completed_at": status.get("completed_at"),
        "failed_at": status.get("failed_at"),
        "error": status.get("error"),
        "testing_environment": status.get("testing_environment", {}),
        "system_version": "2.0.0"
    }

# Sequential task endpoint
@app.get("/sequential-task/{seq_id}")
async def get_sequential_task_info(seq_id: int):
    """Get detailed information about a sequential task"""
    try:
        orchestrator = await get_updated_orchestrator()
        task_status = await orchestrator.get_task_status(seq_id)
        
        return {
            "sequential_task_id": seq_id,
            "task_status": task_status,
            "system_version": "2.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sequential task info: {str(e)}")

# Recent tasks endpoint
@app.get("/recent-tasks")
async def get_recent_tasks(limit: int = 10):
    """Get list of recent automation tasks"""
    try:
        orchestrator = await get_updated_orchestrator()
        recent_tasks = await orchestrator.list_recent_tasks(limit)
        
        return {
            "recent_tasks": recent_tasks,
            "total_returned": len(recent_tasks),
            "limit": limit,
            "system_version": "2.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent tasks: {str(e)}")

# Download files endpoint
@app.get("/download/{task_id}/{agent}/{filename}")
async def download_task_file(task_id: str, agent: str, filename: str):
    """Download generated files from task folders"""
    try:
        # Find sequential task ID from status
        if task_id in task_status_store:
            status = task_status_store[task_id]
            final_result = status.get("final_result", {})
            base_path = final_result.get("base_path")
            
            if base_path:
                if agent == "agent3" and "testing" not in filename:
                    file_path = Path(base_path) / agent / "testing" / filename
                else:
                    file_path = Path(base_path) / agent / filename
                
                if file_path.exists():
                    return FileResponse(
                        path=str(file_path),
                        filename=filename,
                        media_type='application/octet-stream'
                    )
        
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

# Utility functions
def categorize_task(instruction: str) -> str:
    """Enhanced task categorization"""
    instruction_lower = instruction.lower()
    
    patterns = {
        "account_creation": ["account", "register", "signup", "sign up", "create account"],
        "form_filling": ["form", "fill", "submit", "input", "enter data"],
        "authentication": ["login", "signin", "sign in", "authenticate", "password"],
        "search": ["search", "find", "lookup", "locate", "discover"],
        "navigation": ["navigate", "goto", "visit", "browse", "open"],
        "file_handling": ["download", "upload", "file", "document", "attachment"],
        "interaction": ["click", "tap", "select", "choose", "press"],
        "data_extraction": ["data", "extract", "scrape", "collect", "harvest"],
        "shopping": ["buy", "purchase", "cart", "checkout", "order"],
        "social_media": ["post", "share", "like", "follow", "tweet"],
        "messaging": ["message", "email", "send", "reply", "chat"]
    }
    
    for category, keywords in patterns.items():
        if any(keyword in instruction_lower for keyword in keywords):
            return category
    
    return "automation"

def estimate_completion_time(task_category: str, screenshot_count: int, document_size: int) -> timedelta:
    """Enhanced completion time estimation with testing environment setup"""
    base_times = {
        "account_creation": 300,  # Increased for testing environment
        "form_filling": 250,
        "authentication": 180,
        "search": 150,
        "navigation": 120,
        "file_handling": 280,
        "interaction": 160,
        "data_extraction": 350,
        "shopping": 400,
        "social_media": 200,
        "messaging": 180,
        "automation": 250
    }
    
    base_time = base_times.get(task_category, 250)
    
    # Enhanced complexity factors
    if screenshot_count > 5:
        base_time += 60
    elif screenshot_count > 2:
        base_time += 30
    
    if document_size > 1000000:  # 1MB
        base_time += 80
    elif document_size > 500000:  # 500KB
        base_time += 40
    
    # Add time for testing environment setup
    base_time += 60   # Virtual environment creation
    base_time += 45   # Dependencies installation
    base_time += 30   # Automation tools setup
    base_time += 25   # Agent communications
    
    return timedelta(seconds=base_time)

async def update_task_status(task_id: str, updates: Dict[str, Any]):
    """Enhanced task status update with testing environment logging"""
    if task_id in task_status_store:
        for key, value in updates.items():
            if key == "progress" and isinstance(value, dict):
                if "progress" not in task_status_store[task_id]:
                    task_status_store[task_id]["progress"] = {}
                task_status_store[task_id]["progress"].update(value)
            else:
                task_status_store[task_id][key] = value
        
        if "execution_log" not in task_status_store[task_id]:
            task_status_store[task_id]["execution_log"] = []
        
        task_status_store[task_id]["execution_log"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "updates": updates
        })

async def save_task_status_to_file():
    """Save task status to file with enhanced information"""
    try:
        status_file = Path("logs") / "updated_task_status.json"
        status_file.parent.mkdir(exist_ok=True)
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(task_status_store, f, indent=2, default=str, ensure_ascii=False)
        logger.info(f"Updated task status saved to {status_file}")
    except Exception as e:
        logger.error(f"Failed to save updated task status: {str(e)}")

# Run the updated application
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Updated Multi-Agent Automation System with Testing Environment...")
    print("🤖 4-Agent System: Blueprint → Code → Testing → Reporting")
    print("🧪 Features: Virtual Environments, OCR Validation, Agent Communication")
    print("📋 Sequential Task IDs with SQLite Persistence")
    print("🌐 API Endpoints:")
    print("   📡 Health: http://localhost:8000/health")
    print("   🚀 Automate: POST http://localhost:8000/automate")
    print("   📊 Status: GET http://localhost:8000/status/{task_id}")
    print("   📋 Results: GET http://localhost:8000/results/{task_id}")
    print("   📜 Recent: GET http://localhost:8000/recent-tasks")
    print("   📁 Download: GET http://localhost:8000/download/{task_id}/{agent}/{filename}")
    print("📖 Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )