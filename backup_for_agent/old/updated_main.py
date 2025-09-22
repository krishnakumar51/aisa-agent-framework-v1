"""
Updated main.py with LangGraph Integration and Testing Environment
Enhanced FastAPI application with both traditional and LangGraph orchestrators
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

# Application imports - Multiple orchestrator support
from app.main_orchestrator import get_updated_orchestrator
from app.langgraph_orchestrator import get_langgraph_orchestrator
from app.database.database_manager import get_testing_db

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
    """Enhanced application lifespan handler with dual orchestrator support"""
    # Startup
    print("🚀 Multi-Agent Automation Framework v3.0.0 starting up...")
    print("🤖 Dual Orchestrator System: Traditional + LangGraph")
    print("📊 Features: Sequential IDs, Virtual Environments, OCR Validation, Agent Communication")
    print("🗄️ SQLite Database: sqlite_db.sqlite")
    print("📁 Generated Code Directory: generated_code/")
    print("🌐 CORS enabled for all origins")
    print("🔄 LangGraph State Management: Available")
    
    # Initialize orchestrators and database
    try:
        # Initialize traditional orchestrator
        traditional_orchestrator = await get_updated_orchestrator()
        print("✅ Traditional multi-agent orchestrator system initialized")
        
        # Initialize LangGraph orchestrator
        try:
            langgraph_orchestrator = await get_langgraph_orchestrator()
            print("✅ LangGraph multi-agent orchestrator system initialized")
            print("🔄 State-driven workflow management enabled")
        except Exception as lg_error:
            print(f"⚠️ LangGraph orchestrator initialization failed: {str(lg_error)}")
            print("📋 Falling back to traditional orchestrator only")
        
        # Initialize database
        db_manager = await get_testing_db()
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
        print(f"⚠️ System initialization warning: {str(e)}")
        print("🔧 Some features may not be available")
    
    yield
    
    # Shutdown
    print("📝 Saving final task status...")
    await save_task_status_to_file()
    
    # Close database connections
    try:
        db_manager = await get_testing_db()
        print("🔒 Database connections closed")
    except:
        pass
        
    print("🛑 Multi-Agent Automation Framework shutting down...")

# FastAPI app with enhanced lifespan
app = FastAPI(
    title="Multi-Agent Automation System with LangGraph Integration",
    version="3.0.0",
    description="Advanced 4-agent system with dual orchestrators: Traditional + LangGraph state management, SQLite database, testing environment setup, and OCR validation",
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
    """Enhanced health check with dual orchestrator status"""
    try:
        db_manager = await get_testing_db()
        
        # Check traditional orchestrator
        traditional_status = "available"
        try:
            traditional_orchestrator = await get_updated_orchestrator()
            recent_tasks = await traditional_orchestrator.list_recent_tasks(5)
        except Exception as e:
            traditional_status = f"error: {str(e)}"
            recent_tasks = []
        
        # Check LangGraph orchestrator
        langgraph_status = "available"
        try:
            langgraph_orchestrator = await get_langgraph_orchestrator()
        except Exception as e:
            langgraph_status = f"error: {str(e)}"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "3.0.0",
            "system": "dual_orchestrator_multi_agent_automation",
            "orchestrators": {
                "traditional": {
                    "status": traditional_status,
                    "description": "Classic workflow orchestration"
                },
                "langgraph": {
                    "status": langgraph_status,
                    "description": "State-driven workflow management"
                }
            },
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
                "dual_orchestrator_support",
                "langgraph_state_management",
                "testing_environment_setup",
                "virtual_environment_management",
                "agent_to_agent_communication",
                "ocr_screenshot_validation",
                "sqlite_workflow_persistence",
                "comprehensive_reporting",
                "csv_data_export",
                "conditional_workflow_routing"
            ],
            "folder_structure": {
                "base": "generated_code/",
                "pattern": "generated_code/{seq_id}/agent{1-4}/",
                "testing": "generated_code/{seq_id}/agent3/testing/"
            },
            "mode": "dual_orchestrator_api"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "3.0.0"
        }

# Enhanced automation endpoint with dual orchestrator support
@app.post("/automate")
async def enhanced_automate_endpoint(
    instruction: str = Form(...),
    platform: str = Form("auto-detect"),
    workflow_type: str = Form("langgraph"),  # "traditional" or "langgraph"
    additional_data: str = Form("{}"),
    files: List[UploadFile] = File([]),
    background_tasks: BackgroundTasks = None
):
    """
    Enhanced automation endpoint with dual orchestrator support
    
    Args:
        instruction: The automation task description
        platform: Target platform (web, mobile, or auto-detect)
        workflow_type: Orchestrator type ("traditional" or "langgraph")
        additional_data: JSON string with additional user data
        files: List of uploaded files (PDFs, screenshots)
        background_tasks: FastAPI background tasks handler
    
    Returns:
        Enhanced task information with orchestrator selection and testing environment setup
    """
    start_time = time.time()
    temp_task_id = f"temp_{int(time.time())}"
    
    try:
        logger.info(f"[API] Enhanced automation request - Temp ID: {temp_task_id}")
        logger.info(f"[API] Workflow Type: {workflow_type}")
        logger.info(f"[API] Instruction: {instruction}")
        logger.info(f"[API] Platform: {platform}")
        logger.info(f"[API] Files: {len(files)}")
        
        # Validate workflow type
        if workflow_type not in ["traditional", "langgraph"]:
            workflow_type = "langgraph"  # Default to LangGraph
            logger.info(f"[API] Invalid workflow_type, defaulting to: {workflow_type}")
        
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
Enhanced Automation Task Request
===============================

Task: {instruction}
Platform: {platform}
Workflow Type: {workflow_type}
Requested at: {datetime.utcnow().isoformat()}

Additional Data:
{json.dumps(additional_data_dict, indent=2)}

Note: This is a generated document as no files were provided.
The enhanced dual-orchestrator system will work with the task description above.
"""
            document_content = fallback_content.encode('utf-8')
            logger.info("[API] Created fallback document content")
        
        # Enhanced task categorization and estimation
        task_category = categorize_task(instruction)
        estimated_time = estimate_completion_time(task_category, len(screenshots), len(document_content), workflow_type)
        
        # Initialize comprehensive task status with orchestrator info
        orchestrator_features = get_orchestrator_features(workflow_type)
        
        task_status_store[temp_task_id] = {
            "temp_task_id": temp_task_id,
            "status": "initializing",
            "workflow_type": workflow_type,
            "current_agent": "orchestrator",
            "progress": {
                "phase": "initialization",
                "phase_progress": 0,
                "overall_progress": 0,
                "current_step": f"Starting {workflow_type} multi-agent workflow...",
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
            "orchestrator_features": orchestrator_features,
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
            "workflow_type": workflow_type,
            "instruction": instruction,
            "platform": platform,
            "additional_data": additional_data_dict,
            "document_content": document_content,
            "screenshots": screenshots,
            "processed_files": processed_files,
            "task_category": task_category
        }
        
        # Start enhanced background workflow
        if background_tasks:
            background_tasks.add_task(
                execute_enhanced_workflow_background,
                temp_task_id=temp_task_id,
                task_config=task_config
            )
        else:
            # For backwards compatibility
            asyncio.create_task(execute_enhanced_workflow_background(temp_task_id, task_config))
        
        processing_time = time.time() - start_time
        
        # Return enhanced immediate response
        return JSONResponse(
            content={
                "success": True,
                "temp_task_id": temp_task_id,
                "message": f"Enhanced {workflow_type} automation workflow started with testing environment integration",
                "status": "initializing",
                "workflow_type": workflow_type,
                "platform": platform,
                "task_category": task_category,
                "confidence": 0.95,
                "confidence_level": "very_high",
                "processing_time": round(processing_time, 3),
                "files_processed": len(processed_files),
                "estimated_completion_time": estimated_time.total_seconds(),
                "system_version": "3.0.0",
                "agents_count": 4,
                "status_endpoint": f"/status/{temp_task_id}",
                "results_endpoint": f"/results/{temp_task_id}",
                "orchestrator_features": orchestrator_features,
                "enhanced_features": [
                    "dual_orchestrator_support",
                    "langgraph_state_management",
                    "sequential_task_ids",
                    "testing_environment_setup", 
                    "virtual_environment_management",
                    "real_time_agent_communication",
                    "ocr_screenshot_validation",
                    "sqlite_workflow_persistence",
                    "comprehensive_csv_export",
                    "automated_retry_with_improvements",
                    "conditional_workflow_routing",
                    "folder_structure_management"
                ]
            }
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Failed to start enhanced automation: {str(e)}"
        logger.error(f"[API] Enhanced automation endpoint error: {error_msg}")
        
        return JSONResponse(
            content={
                "success": False,
                "error": error_msg,
                "error_type": type(e).__name__,
                "temp_task_id": temp_task_id,
                "processing_time": round(processing_time, 3),
                "message": "Enhanced automation request failed during initialization",
                "system_version": "3.0.0"
            },
            status_code=500
        )

# Enhanced background workflow execution with dual orchestrator support
async def execute_enhanced_workflow_background(temp_task_id: str, task_config: Dict[str, Any]):
    """Execute enhanced workflow with orchestrator selection"""
    workflow_start_time = time.time()
    seq_id = None
    workflow_type = task_config.get("workflow_type", "langgraph")
    
    try:
        logger.info(f"[API] Starting {workflow_type} background workflow for task: {temp_task_id}")
        logger.info(f"[API] Platform: {task_config.get('platform', 'auto-detect')}")
        logger.info(f"[API] Task category: {task_config.get('task_category', 'automation')}")
        logger.info(f"[API] Instruction: {task_config.get('instruction', 'Unknown')}")
        
        # Update status to starting
        await update_task_status(temp_task_id, {
            "status": "starting",
            "current_agent": f"{workflow_type}_orchestrator",
            "progress": {
                "phase": "starting",
                "phase_progress": 5,
                "overall_progress": 5,
                "current_step": f"Initializing {workflow_type} 4-agent workflow with testing environment...",
            }
        })
        
        # Small delay for system initialization
        await asyncio.sleep(2)
        
        # Select and execute orchestrator
        try:
            if workflow_type == "langgraph":
                logger.info(f"[API] Using LangGraph orchestrator")
                orchestrator = await get_langgraph_orchestrator()
            else:
                logger.info(f"[API] Using traditional orchestrator")
                orchestrator = await get_updated_orchestrator()
            
            # Execute workflow
            result = await orchestrator.execute_complete_workflow(
                document_content=task_config["document_content"],
                screenshots=task_config.get("screenshots", []),
                instruction=task_config["instruction"],
                platform=task_config.get("platform", "auto-detect"),
                additional_data=task_config.get("additional_data", {})
            )
            
        except Exception as orchestrator_error:
            logger.warning(f"[API] {workflow_type} orchestrator failed: {str(orchestrator_error)}")
            
            # Fallback to traditional orchestrator if LangGraph fails
            if workflow_type == "langgraph":
                logger.info(f"[API] Falling back to traditional orchestrator")
                await update_task_status(temp_task_id, {
                    "status": "fallback_orchestrator",
                    "current_agent": "traditional_orchestrator",
                    "progress": {
                        "current_step": "LangGraph failed, using traditional orchestrator...",
                    }
                })
                
                orchestrator = await get_updated_orchestrator()
                result = await orchestrator.execute_complete_workflow(
                    document_content=task_config["document_content"],
                    screenshots=task_config.get("screenshots", []),
                    instruction=task_config["instruction"],
                    platform=task_config.get("platform", "auto-detect"),
                    additional_data=task_config.get("additional_data", {})
                )
                workflow_type = "traditional_fallback"
            else:
                raise orchestrator_error
        
        workflow_time = time.time() - workflow_start_time
        
        # Extract results
        success = result.get('success', False)
        seq_id = result.get('seq_id')
        base_path = result.get('base_path', 'N/A')
        final_confidence = result.get('final_confidence', 0.0)
        performance_grade = result.get('performance_grade', 'Unknown')
        final_message = result.get('message', f'{workflow_type} workflow completed')
        
        # Extract additional LangGraph-specific results
        langgraph_state = result.get('langgraph_state', {})
        messages = result.get('messages', [])
        testing_env_ready = result.get('testing_env_ready', False)
        automation_tools_status = result.get('automation_tools_status', {})
        
        # Update final task status
        await update_task_status(temp_task_id, {
            "status": "completed" if success else "failed",
            "current_agent": f"{workflow_type}_orchestrator_completed",
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
                "workflow_type_used": workflow_type,
                "folder_structure": result.get('workflow_summary', {}).get('folder_structure', {}),
                "key_metrics": result.get('workflow_summary', {}).get('key_metrics', {}),
                "langgraph_features": {
                    "state_managed": bool(langgraph_state),
                    "messages_count": len(messages),
                    "testing_env_ready": testing_env_ready,
                    "automation_tools_status": automation_tools_status
                },
                "detailed_results": result
            },
            "completed_at": datetime.utcnow().isoformat(),
            "total_execution_time": workflow_time,
            "workflow_summary": result.get('workflow_summary', {}),
            "langgraph_state": langgraph_state,
            "agent_messages": messages,
            "testing_environment": {
                "enabled": True,
                "ready": testing_env_ready,
                "sequential_task_id": seq_id,
                "base_path": base_path,
                "tools_status": automation_tools_status
            }
        })
        
        status_emoji = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"[API] {workflow_type} workflow completed for task {temp_task_id}: {status_emoji}")
        logger.info(f"[API] Sequential task ID: {seq_id}")
        logger.info(f"[API] Base path: {base_path}")
        logger.info(f"[API] Total execution time: {workflow_time:.2f} seconds")
        logger.info(f"[API] Final message: {final_message}")
        logger.info(f"[API] Performance grade: {performance_grade}")
        logger.info(f"[API] LangGraph features used: {bool(langgraph_state)}")
        
    except Exception as e:
        workflow_time = time.time() - workflow_start_time
        error_msg = str(e)
        error_type = type(e).__name__
        
        logger.error(f"[API] {workflow_type} workflow failed for task {temp_task_id}: {error_msg}")
        logger.error(f"[API] Error type: {error_type}")
        logger.error(f"[API] Execution time before failure: {workflow_time:.2f} seconds")
        
        # Update task status with error information
        await update_task_status(temp_task_id, {
            "status": "failed",
            "current_agent": f"{workflow_type}_orchestrator_error",
            "progress": {
                "phase": "failed",
                "phase_progress": 0,
                "overall_progress": 0,
                "current_step": f"{workflow_type} workflow failed: {error_msg}",
            },
            "error": {
                "message": error_msg,
                "type": error_type,
                "timestamp": datetime.utcnow().isoformat(),
                "system": f"{workflow_type}_multi_agent_workflow"
            },
            "final_result": {
                "success": False,
                "sequential_task_id": seq_id,
                "message": f"{workflow_type} workflow failed: {error_msg}",
                "confidence": 0.0,
                "error_details": error_msg,
                "workflow_type_attempted": workflow_type
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
async def get_enhanced_task_status(task_id: str):
    """Get enhanced task status with orchestrator and testing environment information"""
    if task_id not in task_status_store:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    status = task_status_store[task_id]
    
    # Add testing environment information if available
    testing_env_info = {}
    if "testing_environment" in status:
        seq_id = status["testing_environment"].get("sequential_task_id")
        if seq_id:
            try:
                # Use appropriate orchestrator based on workflow type
                workflow_type = status.get("workflow_type", "traditional")
                if workflow_type == "langgraph":
                    orchestrator = await get_langgraph_orchestrator()
                else:
                    orchestrator = await get_updated_orchestrator()
                    
                task_status_result = await orchestrator.get_task_status(seq_id)
                testing_env_info = {
                    "sequential_task_id": seq_id,
                    "orchestrator_used": workflow_type,
                    "task_status": task_status_result
                }
            except Exception as e:
                testing_env_info = {"error": str(e)}
    
    return {
        "temp_task_id": task_id,
        "status": status["status"],
        "workflow_type": status.get("workflow_type", "unknown"),
        "current_agent": status.get("current_agent", "unknown"),
        "progress": status.get("progress", {}),
        "task_info": status.get("task_info", {}),
        "partial_results": status.get("partial_results", {}),
        "error": status.get("error"),
        "created_at": status["created_at"],
        "execution_log": status.get("execution_log", [])[-10:],  # Last 10 entries
        "orchestrator_features": status.get("orchestrator_features", {}),
        "folder_structure": status.get("folder_structure", {}),
        "langgraph_state": status.get("langgraph_state", {}),
        "agent_messages": status.get("agent_messages", []),
        "testing_environment": testing_env_info,
        "system_version": "3.0.0"
    }

# Enhanced results endpoint
@app.get("/results/{task_id}")
async def get_enhanced_task_results(task_id: str):
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
        "workflow_type": status.get("workflow_type", "unknown"),
        "final_result": status.get("final_result", {}),
        "task_info": status.get("task_info", {}),
        "execution_time": status.get("total_execution_time"),
        "workflow_summary": status.get("workflow_summary", {}),
        "completed_at": status.get("completed_at"),
        "failed_at": status.get("failed_at"),
        "error": status.get("error"),
        "langgraph_state": status.get("langgraph_state", {}),
        "agent_messages": status.get("agent_messages", []),
        "testing_environment": status.get("testing_environment", {}),
        "system_version": "3.0.0"
    }

# Sequential task endpoint
@app.get("/sequential-task/{seq_id}")
async def get_sequential_task_info(seq_id: int):
    """Get detailed information about a sequential task"""
    try:
        # Try both orchestrators
        orchestrator = None
        orchestrator_type = "unknown"
        
        try:
            orchestrator = await get_langgraph_orchestrator()
            orchestrator_type = "langgraph"
        except:
            try:
                orchestrator = await get_updated_orchestrator()
                orchestrator_type = "traditional"
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"No orchestrator available: {str(e)}")
        
        task_status = await orchestrator.get_task_status(seq_id)
        
        return {
            "sequential_task_id": seq_id,
            "orchestrator_type": orchestrator_type,
            "task_status": task_status,
            "system_version": "3.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sequential task info: {str(e)}")

# Recent tasks endpoint
@app.get("/recent-tasks")
async def get_recent_tasks(limit: int = 10):
    """Get list of recent automation tasks"""
    try:
        # Try both orchestrators
        recent_tasks = []
        orchestrator_info = []
        
        try:
            langgraph_orchestrator = await get_langgraph_orchestrator()
            lg_tasks = await langgraph_orchestrator.list_recent_tasks(limit)
            recent_tasks.extend(lg_tasks)
            orchestrator_info.append({"type": "langgraph", "tasks": len(lg_tasks)})
        except:
            pass
        
        try:
            traditional_orchestrator = await get_updated_orchestrator()
            trad_tasks = await traditional_orchestrator.list_recent_tasks(limit)
            recent_tasks.extend(trad_tasks)
            orchestrator_info.append({"type": "traditional", "tasks": len(trad_tasks)})
        except:
            pass
        
        # Remove duplicates and sort by date
        unique_tasks = []
        seen_ids = set()
        
        for task in recent_tasks:
            task_id = task.get('seq_id')
            if task_id not in seen_ids:
                unique_tasks.append(task)
                seen_ids.add(task_id)
        
        # Sort by created_at
        unique_tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        unique_tasks = unique_tasks[:limit]
        
        return {
            "recent_tasks": unique_tasks,
            "total_returned": len(unique_tasks),
            "limit": limit,
            "orchestrator_info": orchestrator_info,
            "system_version": "3.0.0"
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

# New: Orchestrator comparison endpoint
@app.get("/orchestrator-comparison")
async def get_orchestrator_comparison():
    """Compare available orchestrators and their features"""
    try:
        orchestrators = {}
        
        # Check traditional orchestrator
        try:
            traditional_orchestrator = await get_updated_orchestrator()
            orchestrators["traditional"] = {
                "available": True,
                "version": traditional_orchestrator.orchestrator_version,
                "features": get_orchestrator_features("traditional"),
                "description": "Classic sequential workflow orchestration"
            }
        except Exception as e:
            orchestrators["traditional"] = {
                "available": False,
                "error": str(e),
                "features": {},
                "description": "Classic sequential workflow orchestration"
            }
        
        # Check LangGraph orchestrator
        try:
            langgraph_orchestrator = await get_langgraph_orchestrator()
            orchestrators["langgraph"] = {
                "available": True,
                "version": langgraph_orchestrator.orchestrator_version,
                "features": get_orchestrator_features("langgraph"),
                "description": "State-driven workflow with advanced agent communication"
            }
        except Exception as e:
            orchestrators["langgraph"] = {
                "available": False,
                "error": str(e),
                "features": {},
                "description": "State-driven workflow with advanced agent communication"
            }
        
        return {
            "orchestrators": orchestrators,
            "recommended": "langgraph" if orchestrators.get("langgraph", {}).get("available") else "traditional",
            "system_version": "3.0.0"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get orchestrator comparison: {str(e)}")

# Utility functions

def get_orchestrator_features(workflow_type: str) -> Dict[str, Any]:
    """Get features for specific orchestrator type"""
    if workflow_type == "langgraph":
        return {
            "state_management": True,
            "message_passing": True,
            "conditional_routing": True,
            "checkpointing": True,
            "visual_workflow": True,
            "error_recovery": True,
            "agent_collaboration": True,
            "testing_environment": True,
            "sequential_task_ids": True,
            "sqlite_persistence": True,
            "csv_export": True
        }
    else:  # traditional
        return {
            "state_management": False,
            "message_passing": False,
            "conditional_routing": False,
            "checkpointing": False,
            "visual_workflow": False,
            "error_recovery": True,
            "agent_collaboration": True,
            "testing_environment": True,
            "sequential_task_ids": True,
            "sqlite_persistence": True,
            "csv_export": True
        }

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

def estimate_completion_time(task_category: str, screenshot_count: int, 
                           document_size: int, workflow_type: str) -> timedelta:
    """Enhanced completion time estimation with orchestrator consideration"""
    base_times = {
        "account_creation": 300,
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
    
    # LangGraph has slight overhead but better recovery
    if workflow_type == "langgraph":
        base_time += 20   # State management overhead
        base_time -= 10   # Better error recovery
    
    return timedelta(seconds=base_time)

async def update_task_status(task_id: str, updates: Dict[str, Any]):
    """Enhanced task status update with orchestrator logging"""
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
    """Save task status to file with enhanced orchestrator information"""
    try:
        status_file = Path("logs") / "enhanced_task_status.json"
        status_file.parent.mkdir(exist_ok=True)
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(task_status_store, f, indent=2, default=str, ensure_ascii=False)
        logger.info(f"Enhanced task status saved to {status_file}")
    except Exception as e:
        logger.error(f"Failed to save enhanced task status: {str(e)}")

# Run the enhanced application
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Enhanced Multi-Agent Automation System...")
    print("🤖 Dual Orchestrator System: Traditional + LangGraph")
    print("🔄 LangGraph Features: State Management, Conditional Routing, Message Passing")
    print("🧪 Enhanced Features: Virtual Environments, OCR Validation, Agent Communication")
    print("📋 Sequential Task IDs with SQLite Persistence")
    print("🌐 Enhanced API Endpoints:")
    print("   📡 Health: http://localhost:8000/health")
    print("   🚀 Automate: POST http://localhost:8000/automate")
    print("   📊 Status: GET http://localhost:8000/status/{task_id}")
    print("   📋 Results: GET http://localhost:8000/results/{task_id}")
    print("   📜 Recent: GET http://localhost:8000/recent-tasks")
    print("   🔄 Comparison: GET http://localhost:8000/orchestrator-comparison")
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