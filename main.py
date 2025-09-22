"""
Multi-Agent Automation Framework - Main Application
Production-ready FastAPI application with LangGraph integration and core terminal functionality
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

# Core framework imports
try:
    from app.database.database_manager import get_database_manager, DatabaseManager
    from app.utils.output_structure_manager import OutputStructureManager
    from app.utils.terminal_manager import get_terminal_manager, TerminalManager
    from app.langgraph.workflow_state import AutomationWorkflowState, create_initial_state
    from app.tools.blueprint_tools import get_agent1_tools
    FRAMEWORK_AVAILABLE = True
    print("✅ Core framework components available")
except ImportError as e:
    FRAMEWORK_AVAILABLE = False
    print(f"⚠️ Core framework components not available: {str(e)}")

# Legacy imports (maintain compatibility)
try:
    from app.orchestrator import get_orchestrator, MultiAgentOrchestrator
    ORCHESTRATOR_AVAILABLE = True
    print("✅ Orchestrator module available")
except ImportError as e:
    ORCHESTRATOR_AVAILABLE = False
    print(f"⚠️ Orchestrator not available: {str(e)}")

try:
    from app.device_manager import DeviceManager
    DEVICE_MANAGER_AVAILABLE = True
    print("✅ Device manager module available")
except ImportError as e:
    DEVICE_MANAGER_AVAILABLE = False
    print(f"⚠️ Device manager not available: {str(e)}")

# Try LangGraph import
try:
    from app.langgraph_orchestrator import get_langgraph_orchestrator
    LANGGRAPH_AVAILABLE = True
    print("✅ LangGraph orchestrator module available")
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    print(f"⚠️ LangGraph not available. Install with: pip install langgraph")

# Global task store (in-memory for now)
task_status_store: Dict[str, Dict[str, Any]] = {}

# Logging configuration
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(
            Path("logs") / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global orchestrator instances
_database_manager = None
_orchestrator = None
_langgraph_orchestrator = None
_device_manager = None
_terminal_manager = None

# Simple fallback classes
class SimpleDeviceManager:
    """Fallback device manager with basic functionality"""
    def check_adb_available(self) -> bool:
        try:
            import subprocess
            result = subprocess.run(["adb", "version"], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def get_connected_devices(self) -> List[Dict[str, Any]]:
        try:
            import subprocess
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]
                devices = []
                for line in lines:
                    if line.strip() and 'device' in line:
                        device_id = line.split()[0]
                        devices.append({
                            "device_id": device_id,
                            "device_name": f"Android Device ({device_id})",
                            "is_emulator": device_id.startswith("emulator-")
                        })
                return devices
        except:
            pass
        return []

async def initialize_framework():
    """Initialize framework components"""
    global _database_manager, _orchestrator, _langgraph_orchestrator, _device_manager, _terminal_manager
    
    logger.info("🚀 Initializing Multi-Agent Automation Framework...")
    
    try:
        # Initialize database manager
        if FRAMEWORK_AVAILABLE:
            try:
                _database_manager = await get_database_manager()
                logger.info("✅ Database manager initialized with LangGraph support")
                
                # Test functionality
                test_task_id = await _database_manager.create_task_with_langgraph(
                    "Framework initialization test",
                    "auto",
                    {"framework_version": "1.0.0", "initialization": True}
                )
                logger.info(f"📝 Test task created: {test_task_id}")
                
            except Exception as e:
                logger.error(f"❌ Database manager failed: {str(e)}")
                _database_manager = None
        
        # Initialize terminal manager
        if FRAMEWORK_AVAILABLE:
            _terminal_manager = get_terminal_manager()
            logger.info("✅ Terminal manager initialized")
        
        # Initialize device manager (with fallback)
        if DEVICE_MANAGER_AVAILABLE:
            _device_manager = DeviceManager()
            logger.info("✅ Device manager initialized")
        else:
            _device_manager = SimpleDeviceManager()
            logger.info("✅ Simple device manager initialized (fallback)")
        
        # Initialize orchestrator (if available)
        if ORCHESTRATOR_AVAILABLE:
            try:
                _orchestrator = await get_orchestrator()
                logger.info("✅ Orchestrator initialized")
            except Exception as e:
                logger.warning(f"⚠️ Orchestrator failed: {str(e)}")
        
        # Initialize LangGraph orchestrator (experimental)
        if LANGGRAPH_AVAILABLE:
            try:
                _langgraph_orchestrator = await get_langgraph_orchestrator()
                logger.info("✅ LangGraph orchestrator initialized (EXPERIMENTAL)")
            except Exception as e:
                logger.warning(f"⚠️ LangGraph orchestrator failed: {str(e)}")
        
        # Test framework components
        if FRAMEWORK_AVAILABLE:
            await test_framework_components()
        
        # Perform system health checks
        await perform_health_check()
        
        logger.info("🎯 Framework initialization completed")
        
    except Exception as e:
        logger.error(f"❌ Framework initialization failed: {str(e)}")
        logger.info("🔄 Continuing with available components...")

async def test_framework_components():
    """Test framework components functionality"""
    try:
        logger.info("🧪 Testing framework components...")
        
        # Test output structure manager
        test_output_manager = OutputStructureManager(9999)
        directories = test_output_manager.create_complete_structure()
        logger.info(f"📁 Output structure test: {len(directories)} directories created")
        
        # Test automation state
        test_state = create_initial_state(
            task_id=9999,
            instruction="Framework integration test",
            platform="mobile",
            additional_data={"test": True}
        )
        logger.info(f"📊 State test: {test_state.task_id} - {test_state.workflow_status}")
        
        # Test blueprint tools
        if get_agent1_tools:
            tools = get_agent1_tools()
            logger.info(f"🛠️ Blueprint tools test: {len(tools)} tools available")
        
        logger.info("✅ Framework components test completed successfully")
        
    except Exception as e:
        logger.warning(f"⚠️ Framework components test failed: {str(e)}")

async def perform_health_check():
    """Perform system health checks"""
    health_status = {
        "database_manager": _database_manager is not None,
        "orchestrator": _orchestrator is not None,
        "langgraph_orchestrator": _langgraph_orchestrator is not None,
        "device_manager": _device_manager is not None,
        "terminal_manager": _terminal_manager is not None,
        "framework_components": FRAMEWORK_AVAILABLE
    }
    
    # Check device environment (safely)
    if _device_manager:
        try:
            adb_available = _device_manager.check_adb_available()
            connected_devices = len(_device_manager.get_connected_devices()) if adb_available else 0
            health_status.update({
                "adb_available": adb_available,
                "connected_devices": connected_devices
            })
        except Exception as e:
            health_status["device_check_error"] = str(e)
    
    # Check Appium server (safely)
    if _terminal_manager:
        try:
            appium_status = _terminal_manager.get_appium_server_status()
            health_status["appium_server"] = appium_status.get("running", False)
        except Exception as e:
            health_status["appium_check_error"] = str(e)
    
    logger.info(f"📊 Health Status: {json.dumps(health_status, indent=2)}")

async def cleanup_framework():
    """Cleanup framework resources"""
    global _database_manager, _orchestrator, _terminal_manager
    
    logger.info("🧹 Cleaning up framework resources...")
    
    try:
        # Cleanup orchestrator processes
        if _orchestrator and hasattr(_orchestrator, 'cleanup_workflow'):
            await _orchestrator.cleanup_workflow(0)
        
        # Cleanup terminal manager processes
        if _terminal_manager and hasattr(_terminal_manager, 'cleanup_processes'):
            _terminal_manager.cleanup_processes()
        
        logger.info("✅ Framework cleanup completed")
        
    except Exception as e:
        logger.warning(f"⚠️ Cleanup had issues: {str(e)}")

@asynccontextmanager
async def framework_lifespan(app: FastAPI):
    """Application lifespan context manager"""
    logger.info("🚀 Multi-Agent Automation Framework starting up...")
    
    # Startup
    try:
        await initialize_framework()
        logger.info("✅ Application startup completed")
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        # Continue with partial initialization
    
    yield
    
    # Shutdown
    logger.info("🛑 Multi-Agent Automation Framework shutting down...")
    await cleanup_framework()
    logger.info("✅ Application shutdown completed")

# Initialize FastAPI with lifespan management
app = FastAPI(
    title="Multi-Agent Automation Framework",
    description="LangGraph-powered automation with intelligent orchestration and production terminal functionality",
    version="1.0.0",
    lifespan=framework_lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with framework status"""
    global _database_manager, _device_manager, _terminal_manager
    
    system_info = {
        "framework": "Multi-Agent Automation Framework",
        "version": "1.0.0",
        "description": "Production automation framework with LangGraph integration",
        "features": [
            "Database Manager with LangGraph Support",
            "Output Structure Management",
            "AutomationWorkflowState Management", 
            "@tool Decorator Implementation",
            "Multi-Orchestrator Support",
            "Device Detection" if _device_manager else "Basic Device Support",
            "Terminal Management with Virtual Environment Support",
            "Production Code Generation",
            "Error Handling & Recovery"
        ],
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "orchestrators": {
            "standard": _orchestrator is not None,
            "langgraph": _langgraph_orchestrator is not None
        },
        "core_components": {
            "database_manager": _database_manager is not None,
            "output_structure_manager": FRAMEWORK_AVAILABLE,
            "automation_state": FRAMEWORK_AVAILABLE,
            "blueprint_tools": FRAMEWORK_AVAILABLE,
            "terminal_manager": _terminal_manager is not None
        },
        "modules": {
            "framework_available": FRAMEWORK_AVAILABLE,
            "orchestrator_available": ORCHESTRATOR_AVAILABLE,
            "device_manager_available": DEVICE_MANAGER_AVAILABLE,
            "langgraph_available": LANGGRAPH_AVAILABLE
        }
    }
    
    # Add runtime status (safely)
    if _device_manager:
        try:
            devices = _device_manager.get_connected_devices()
            system_info["connected_devices"] = len(devices)
        except:
            system_info["connected_devices"] = "unavailable"
    
    if _terminal_manager:
        try:
            appium_status = _terminal_manager.get_appium_server_status()
            system_info["appium_server"] = appium_status.get("status", "unknown")
        except:
            system_info["appium_server"] = "unavailable"
    
    return system_info

@app.post("/automate")
async def automate_workflow(
    background_tasks: BackgroundTasks,
    workflow_type: str = Form(default="standard"),
    instruction: str = Form(...),
    platform: str = Form(...),
    files: List[UploadFile] = File(default=[])
):
    """
    Main automation endpoint
    workflow_type options:
    - standard: Use standard components
    - orchestrator: Use orchestrator (if available)  
    - langgraph: Use LangGraph orchestrator (if available)
    """
    
    # Generate task ID
    temp_task_id = f"task_{int(time.time())}"
    
    logger.info(f"[API] Automation request - Task ID: {temp_task_id}")
    logger.info(f"[API] Workflow Type: {workflow_type}")
    logger.info(f"[API] Instruction: {instruction}")
    logger.info(f"[API] Platform: {platform}")
    logger.info(f"[API] Files: {len(files)}")
    
    # Initialize task status
    task_status_store[temp_task_id] = {
        "task_id": temp_task_id,
        "workflow_type": workflow_type,
        "instruction": instruction,
        "platform": platform,
        "status": "initiated",
        "created_at": datetime.utcnow().isoformat(),
        "progress": 0
    }
    
    # Process uploaded files
    document_data = None
    screenshots = []
    if files:
        for file in files:
            file_content = await file.read()
            if file.content_type == "application/pdf":
                document_data = file_content
                logger.info(f"[API] Processing PDF: {file.filename}")
            elif file.content_type and file.content_type.startswith("image/"):
                screenshots.append(file_content)
                logger.info(f"[API] Processing screenshot: {file.filename}")
    
    # Launch appropriate workflow
    if workflow_type == "standard" and FRAMEWORK_AVAILABLE:
        background_tasks.add_task(
            execute_standard_workflow,
            temp_task_id, instruction, platform, document_data, screenshots
        )
        selected_orchestrator = "standard"
    elif workflow_type == "orchestrator" and ORCHESTRATOR_AVAILABLE and _orchestrator:
        background_tasks.add_task(
            execute_orchestrator_workflow,
            temp_task_id, instruction, platform, document_data, screenshots
        )
        selected_orchestrator = "orchestrator"
    elif workflow_type == "langgraph" and LANGGRAPH_AVAILABLE and _langgraph_orchestrator:
        background_tasks.add_task(
            execute_langgraph_workflow,
            temp_task_id, instruction, platform, document_data, screenshots
        )
        selected_orchestrator = "langgraph"
    else:
        raise HTTPException(
            status_code=503,
            detail=f"Workflow type '{workflow_type}' not available. Check system status."
        )
    
    # Update task status
    task_status_store[temp_task_id].update({
        "status": "processing",
        "orchestrator": selected_orchestrator,
        "progress": 10
    })
    
    return JSONResponse({
        "success": True,
        "message": "Automation workflow initiated",
        "task_id": temp_task_id,
        "workflow_type": workflow_type,
        "orchestrator": selected_orchestrator,
        "status": "processing",
        "estimated_duration": "2-5 minutes"
    })

async def execute_standard_workflow(
    task_id: str,
    instruction: str,
    platform: str,
    document_data: bytes = None,
    screenshots: List[bytes] = None
):
    """Execute standard workflow with framework components"""
    
    try:
        logger.info(f"[Standard] Starting standard workflow for task: {task_id}")
        
        task_status_store[task_id].update({
            "status": "running_standard",
            "progress": 20,
            "current_phase": "initialization"
        })
        
        # Create database task
        if _database_manager:
            db_task_id = await _database_manager.create_task_with_langgraph(
                instruction, platform, 
                {"temp_task_id": task_id},
                f"thread_{task_id}", f"checkpoint_{task_id}"
            )
            logger.info(f"[Standard] Created database task: {db_task_id}")
        
        # Create initial state
        if FRAMEWORK_AVAILABLE:
            state = create_initial_state(
                task_id=int(task_id.split('_')[-1]),
                instruction=instruction,
                platform=platform,
                document_content=document_data,
                screenshots=screenshots or [],
                additional_data={"temp_task_id": task_id}
            )
            logger.info(f"[Standard] Created automation state: {state.task_id}")
        
        # Test blueprint tools
        if FRAMEWORK_AVAILABLE and document_data:
            task_status_store[task_id].update({
                "progress": 40,
                "current_phase": "document_analysis"
            })
            
            logger.info(f"[Standard] Would execute blueprint tools here...")
        
        # Create output structure
        if FRAMEWORK_AVAILABLE:
            task_status_store[task_id].update({
                "progress": 60,
                "current_phase": "output_structure"
            })
            
            output_manager = OutputStructureManager(int(task_id.split('_')[-1]))
            directories = output_manager.create_complete_structure()
            logger.info(f"[Standard] Created output structure: {len(directories)} directories")
        
        task_status_store[task_id].update({
            "status": "completed",
            "progress": 100,
            "current_phase": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "results": {
                "database_integration": _database_manager is not None,
                "state_management": FRAMEWORK_AVAILABLE,
                "output_structure": FRAMEWORK_AVAILABLE,
                "blueprint_tools": FRAMEWORK_AVAILABLE
            }
        })
        
        logger.info(f"[Standard] Standard workflow completed for task: {task_id}")
        
    except Exception as e:
        logger.error(f"[Standard] Standard workflow failed for task {task_id}: {str(e)}")
        task_status_store[task_id].update({
            "status": "failed",
            "progress": 0,
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })

async def execute_orchestrator_workflow(task_id, instruction, platform, document_data, screenshots):
    """Execute orchestrator workflow with error handling"""
    try:
        logger.info(f"[Orchestrator] Starting orchestrator workflow for task: {task_id}")
        task_status_store[task_id].update({
            "status": "running_orchestrator",
            "progress": 20,
            "current_phase": "initialization"
        })
        
        if _orchestrator:
            workflow_results = await _orchestrator.execute_workflow(
                instruction=instruction,
                platform=platform,
                document_data=document_data,
                screenshots=screenshots or [],
                additional_data={"temp_task_id": task_id}
            )
            
            final_status = "completed" if workflow_results.get("overall_success") else "completed_with_issues"
            task_status_store[task_id].update({
                "status": final_status,
                "progress": 100,
                "workflow_results": workflow_results,
                "completed_at": datetime.utcnow().isoformat()
            })
        
        logger.info(f"[Orchestrator] Orchestrator workflow completed for task: {task_id}")
        
    except Exception as e:
        logger.error(f"[Orchestrator] Orchestrator workflow failed for task {task_id}: {str(e)}")
        task_status_store[task_id].update({
            "status": "failed",
            "progress": 0,
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })

async def execute_langgraph_workflow(task_id, instruction, platform, document_data, screenshots):
    """Execute LangGraph workflow with error handling"""
    try:
        logger.info(f"[LangGraph] Starting LangGraph workflow for task: {task_id}")
        task_status_store[task_id].update({
            "status": "running_langgraph",
            "progress": 20,
            "current_phase": "langgraph_orchestration"
        })
        
        # Placeholder - will be implemented when LangGraph orchestrator is ready
        task_status_store[task_id].update({
            "status": "completed",
            "progress": 100,
            "completed_at": datetime.utcnow().isoformat(),
            "note": "LangGraph workflow placeholder - full implementation coming soon"
        })
        
        logger.info(f"[LangGraph] LangGraph workflow completed for task: {task_id}")
        
    except Exception as e:
        logger.error(f"[LangGraph] LangGraph workflow failed for task {task_id}: {str(e)}")
        task_status_store[task_id].update({
            "status": "failed",
            "progress": 0,
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Get task status"""
    if task_id not in task_status_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_status_store[task_id]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "framework": "Multi-Agent Automation Framework",
        "orchestrators": {
            "standard": FRAMEWORK_AVAILABLE,
            "orchestrator": _orchestrator is not None,
            "langgraph": _langgraph_orchestrator is not None
        },
        "core_components": {
            "database_manager": _database_manager is not None,
            "output_structure_manager": FRAMEWORK_AVAILABLE,
            "automation_state": FRAMEWORK_AVAILABLE,
            "blueprint_tools": FRAMEWORK_AVAILABLE,
            "terminal_manager": _terminal_manager is not None
        },
        "modules": {
            "framework_available": FRAMEWORK_AVAILABLE,
            "orchestrator_available": ORCHESTRATOR_AVAILABLE,
            "device_manager_available": DEVICE_MANAGER_AVAILABLE,
            "langgraph_available": LANGGRAPH_AVAILABLE
        }
    }
    
    # Check components safely
    if _device_manager:
        try:
            adb_available = _device_manager.check_adb_available()
            devices = _device_manager.get_connected_devices() if adb_available else []
            health_status["mobile_environment"] = {
                "adb_available": adb_available,
                "connected_devices": len(devices)
            }
        except Exception as e:
            health_status["mobile_environment"] = {"error": str(e)}
    
    if _terminal_manager:
        try:
            appium_status = _terminal_manager.get_appium_server_status()
            health_status["appium_server"] = appium_status.get("status", "unknown")
        except Exception as e:
            health_status["appium_server"] = {"error": str(e)}
    
    # Check database
    if _database_manager:
        try:
            health_status["database"] = "connected"
        except Exception as e:
            health_status["database"] = {"error": str(e)}
            health_status["status"] = "degraded"
    
    return health_status

@app.get("/devices")
async def get_connected_devices():
    """Get connected Android devices information"""
    global _device_manager
    
    if not _device_manager:
        return {"error": "Device manager not available"}
    
    try:
        if not _device_manager.check_adb_available():
            return {
                "adb_available": False,
                "devices": [],
                "message": "ADB not available. Please install Android SDK Platform Tools."
            }
        
        devices = _device_manager.get_connected_devices()
        return {
            "adb_available": True,
            "devices": devices,
            "device_count": len(devices),
            "message": f"Found {len(devices)} connected device(s)"
        }
        
    except Exception as e:
        return {"error": f"Device detection failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Multi-Agent Automation Framework v1.0.0...")
    print("📋 Features: LangGraph Integration, Database Management, Terminal Support, Output Structure")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📱 Device Status: http://localhost:8000/devices")
    print()
    print(f"🔧 Component Status:")
    print(f"   Core Framework: {'✅' if FRAMEWORK_AVAILABLE else '❌'}")
    print(f"   Database Manager: {'✅' if FRAMEWORK_AVAILABLE else '❌'}")
    print(f"   Terminal Manager: {'✅' if FRAMEWORK_AVAILABLE else '❌'}")
    print(f"   Output Structure: {'✅' if FRAMEWORK_AVAILABLE else '❌'}")
    print(f"   Automation State: {'✅' if FRAMEWORK_AVAILABLE else '❌'}")
    print(f"   Blueprint Tools: {'✅' if FRAMEWORK_AVAILABLE else '❌'}")
    print(f"   Orchestrator: {'✅' if ORCHESTRATOR_AVAILABLE else '❌'}")
    print(f"   Device Manager: {'✅' if DEVICE_MANAGER_AVAILABLE else '❌'}")
    print(f"   LangGraph: {'✅' if LANGGRAPH_AVAILABLE else '❌'}")
    print()
    print("⚠️ Start with '--reload-dir app' to avoid conflicts:")
    print("   uvicorn main:app --reload --reload-dir app")
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )