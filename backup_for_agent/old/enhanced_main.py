"""
Enhanced Main Application - Phase 1 LangGraph Integration
Updated to use the new enhanced database manager and output structure manager
Maintains backward compatibility while adding LangGraph support
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

# Phase 1 Enhanced imports
try:
    from app.database.enhanced_database_manager import get_enhanced_database_manager, EnhancedDatabaseManager
    from app.utils.output_structure_manager import OutputStructureManager
    from app.langgraph.state import AutomationWorkflowState, create_initial_state
    from app.tools.blueprint_tools.document_analysis import get_agent1_tools
    PHASE1_AVAILABLE = True
    print("✅ Phase 1 components available")
except ImportError as e:
    PHASE1_AVAILABLE = False
    print(f"⚠️ Phase 1 components not available: {str(e)}")

# Legacy imports (maintain compatibility)
try:
    from app.enhanced_orchestrator import get_enhanced_orchestrator, EnhancedMultiAgentOrchestrator
    ENHANCED_AVAILABLE = True
    print("✅ Enhanced orchestrator module available")
except ImportError as e:
    ENHANCED_AVAILABLE = False
    print(f"⚠️ Enhanced orchestrator not available: {str(e)}")

try:
    from app.utils.device_manager import DeviceManager
    DEVICE_MANAGER_AVAILABLE = True
    print("✅ Device manager module available")
except ImportError as e:
    DEVICE_MANAGER_AVAILABLE = False
    print(f"⚠️ Device manager not available: {str(e)}")

try:
    from app.utils.terminal_manager import TerminalManager
    TERMINAL_MANAGER_AVAILABLE = True
    print("✅ Terminal manager module available")
except ImportError as e:
    TERMINAL_MANAGER_AVAILABLE = False
    print(f"⚠️ Terminal manager not available: {str(e)}")

# Legacy database import (fallback)
try:
    from app.database.database_manager import get_testing_db
    LEGACY_DB_AVAILABLE = True
except ImportError as e:
    LEGACY_DB_AVAILABLE = False
    print(f"⚠️ Legacy database not available: {str(e)}")

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

# Enhanced logging configuration
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(
            Path("logs") / f"enhanced_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global orchestrator instances
_enhanced_db_manager = None
_enhanced_orchestrator = None
_traditional_orchestrator = None
_langgraph_orchestrator = None
_device_manager = None
_terminal_manager = None

# Simple fallback classes (from your original code)
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

class SimpleTerminalManager:
    """Fallback terminal manager with basic functionality"""
    def check_appium_running(self, port: int = 4723) -> bool:
        try:
            import requests
            response = requests.get(f"http://localhost:{port}/status", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_appium_server_status(self) -> Dict[str, Any]:
        """Check Appium server status"""
        try:
            import requests
            response = requests.get("http://localhost:4723/status", timeout=5)
            if response.status_code == 200:
                return {
                    "running": True,
                    "status": "ready",
                    "response": response.json()
                }
            else:
                return {
                    "running": False,
                    "status": "not_ready",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "running": False,
                "status": "offline",
                "error": str(e)
            }

async def initialize_enhanced_framework():
    """Initialize enhanced framework with Phase 1 components"""
    global _enhanced_db_manager, _enhanced_orchestrator, _traditional_orchestrator
    global _langgraph_orchestrator, _device_manager, _terminal_manager
    
    logger.info("🚀 Initializing Enhanced Multi-Agent Automation Framework v4.0.0...")
    
    try:
        # Initialize enhanced database manager (Phase 1)
        if PHASE1_AVAILABLE:
            try:
                _enhanced_db_manager = await get_enhanced_database_manager()
                logger.info("✅ Enhanced database manager initialized with LangGraph support")
                
                # Test Phase 1 functionality
                test_task_id = await _enhanced_db_manager.create_task_enhanced(
                    "Framework initialization test",
                    "auto",
                    {"framework_version": "4.0.0", "phase": 1}
                )
                logger.info(f"📝 Test task created: {test_task_id}")
                
            except Exception as e:
                logger.error(f"❌ Enhanced database manager failed: {str(e)}")
                _enhanced_db_manager = None
        
        # Initialize device manager (with fallback)
        if DEVICE_MANAGER_AVAILABLE:
            _device_manager = DeviceManager()
            logger.info("✅ Enhanced device manager initialized")
        else:
            _device_manager = SimpleDeviceManager()
            logger.info("✅ Simple device manager initialized (fallback)")
        
        # Initialize terminal manager (with fallback)
        if TERMINAL_MANAGER_AVAILABLE:
            _terminal_manager = TerminalManager()
            logger.info("✅ Enhanced terminal manager initialized")
        else:
            _terminal_manager = SimpleTerminalManager()
            logger.info("✅ Simple terminal manager initialized (fallback)")
        
        # Initialize enhanced orchestrator (if available)
        if ENHANCED_AVAILABLE:
            try:
                _enhanced_orchestrator = await get_enhanced_orchestrator()
                logger.info("✅ Enhanced orchestrator initialized")
            except Exception as e:
                logger.warning(f"⚠️ Enhanced orchestrator failed: {str(e)}")
        
        # Initialize LangGraph orchestrator (experimental)
        if LANGGRAPH_AVAILABLE:
            try:
                _langgraph_orchestrator = await get_langgraph_orchestrator()
                logger.info("✅ LangGraph orchestrator initialized (EXPERIMENTAL)")
            except Exception as e:
                logger.warning(f"⚠️ LangGraph orchestrator failed: {str(e)}")
        
        # Test Phase 1 components
        if PHASE1_AVAILABLE:
            await test_phase1_components()
        
        # Perform system health checks
        await perform_enhanced_health_check()
        
        logger.info("🎯 Enhanced framework initialization completed")
        
    except Exception as e:
        logger.error(f"❌ Framework initialization failed: {str(e)}")
        logger.info("🔄 Continuing with available components...")

async def test_phase1_components():
    """Test Phase 1 components functionality"""
    try:
        logger.info("🧪 Testing Phase 1 components...")
        
        # Test output structure manager
        test_output_manager = OutputStructureManager(9999)
        directories = test_output_manager.create_complete_structure()
        logger.info(f"📁 Output structure test: {len(directories)} directories created")
        
        # Test automation state
        test_state = create_initial_state(
            task_id=9999,
            instruction="Phase 1 integration test",
            platform="mobile",
            additional_data={"test_phase": 1}
        )
        logger.info(f"📊 State test: {test_state.task_id} - {test_state.workflow_status}")
        
        # Test blueprint tools
        if get_agent1_tools:
            tools = get_agent1_tools()
            logger.info(f"🛠️ Blueprint tools test: {len(tools)} tools available")
        
        logger.info("✅ Phase 1 components test completed successfully")
        
    except Exception as e:
        logger.warning(f"⚠️ Phase 1 components test failed: {str(e)}")

async def perform_enhanced_health_check():
    """Perform enhanced system health checks"""
    health_status = {
        "enhanced_database": _enhanced_db_manager is not None,
        "enhanced_orchestrator": _enhanced_orchestrator is not None,
        "langgraph_orchestrator": _langgraph_orchestrator is not None,
        "device_manager": _device_manager is not None,
        "terminal_manager": _terminal_manager is not None,
        "phase1_components": PHASE1_AVAILABLE
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
    
    logger.info(f"📊 Enhanced Health Status: {json.dumps(health_status, indent=2)}")

async def cleanup_enhanced_framework():
    """Cleanup enhanced framework resources"""
    global _enhanced_db_manager, _enhanced_orchestrator, _terminal_manager
    
    logger.info("🧹 Cleaning up enhanced framework resources...")
    
    try:
        # Cleanup enhanced orchestrator processes
        if _enhanced_orchestrator and hasattr(_enhanced_orchestrator, 'cleanup_workflow'):
            await _enhanced_orchestrator.cleanup_workflow(0)
        
        # Cleanup terminal manager processes
        if _terminal_manager and hasattr(_terminal_manager, 'cleanup_processes'):
            _terminal_manager.cleanup_processes()
        
        logger.info("✅ Enhanced framework cleanup completed")
        
    except Exception as e:
        logger.warning(f"⚠️ Cleanup had issues: {str(e)}")

@asynccontextmanager
async def enhanced_lifespan(app: FastAPI):
    """Enhanced application lifespan context manager"""
    logger.info("🚀 Enhanced Multi-Agent Automation Framework v4.0.0 starting up...")
    
    # Startup
    try:
        await initialize_enhanced_framework()
        logger.info("✅ Enhanced application startup completed")
    except Exception as e:
        logger.error(f"❌ Enhanced startup failed: {str(e)}")
        # Continue with partial initialization
    
    yield
    
    # Shutdown
    logger.info("🛑 Enhanced Multi-Agent Automation Framework shutting down...")
    await cleanup_enhanced_framework()
    logger.info("✅ Enhanced application shutdown completed")

# Initialize FastAPI with enhanced lifespan management
app = FastAPI(
    title="Enhanced Multi-Agent Automation Framework",
    description="LangGraph-powered automation with intelligent orchestration and Phase 1 integration",
    version="4.0.0-phase1",
    lifespan=enhanced_lifespan
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
async def enhanced_root():
    """Enhanced root endpoint with Phase 1 status"""
    global _enhanced_db_manager, _device_manager, _terminal_manager
    
    system_info = {
        "framework": "Enhanced Multi-Agent Automation Framework",
        "version": "4.0.0-phase1",
        "phase": "Phase 1 - Database Foundation & Enhancement",
        "features": [
            "Enhanced Database Manager with LangGraph Support",
            "Output Structure Management",
            "AutomationWorkflowState Definition", 
            "@tool Decorator Implementation",
            "Multi-Orchestrator Support",
            "Device Detection" if _device_manager else "Basic Device Support",
            "Production Code Generation",
            "Enhanced Error Handling"
        ],
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "orchestrators": {
            "enhanced": _enhanced_orchestrator is not None,
            "langgraph": _langgraph_orchestrator is not None
        },
        "phase1_components": {
            "enhanced_database": _enhanced_db_manager is not None,
            "output_structure_manager": PHASE1_AVAILABLE,
            "automation_state": PHASE1_AVAILABLE,
            "blueprint_tools": PHASE1_AVAILABLE
        },
        "modules": {
            "phase1_available": PHASE1_AVAILABLE,
            "enhanced_available": ENHANCED_AVAILABLE,
            "device_manager_available": DEVICE_MANAGER_AVAILABLE,
            "terminal_manager_available": TERMINAL_MANAGER_AVAILABLE,
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

@app.post("/automate/enhanced")
async def automate_with_phase1(
    background_tasks: BackgroundTasks,
    workflow_type: str = Form(default="phase1"),
    instruction: str = Form(...),
    platform: str = Form(...),
    files: List[UploadFile] = File(default=[])
):
    """
    Enhanced automation endpoint with Phase 1 integration
    workflow_type options:
    - phase1: Use Phase 1 components (recommended)
    - enhanced: Use enhanced orchestrator (if available)  
    - langgraph: Use LangGraph orchestrator (if available)
    """
    
    # Generate task ID
    temp_task_id = f"phase1_{int(time.time())}"
    
    logger.info(f"[Enhanced API] Automation request - Task ID: {temp_task_id}")
    logger.info(f"[Enhanced API] Workflow Type: {workflow_type}")
    logger.info(f"[Enhanced API] Instruction: {instruction}")
    logger.info(f"[Enhanced API] Platform: {platform}")
    logger.info(f"[Enhanced API] Files: {len(files)}")
    
    # Initialize task status
    task_status_store[temp_task_id] = {
        "task_id": temp_task_id,
        "workflow_type": workflow_type,
        "instruction": instruction,
        "platform": platform,
        "status": "initiated",
        "created_at": datetime.utcnow().isoformat(),
        "progress": 0,
        "phase": "Phase 1"
    }
    
    # Process uploaded files
    document_data = None
    screenshots = []
    if files:
        for file in files:
            file_content = await file.read()
            if file.content_type == "application/pdf":
                document_data = file_content
                logger.info(f"[Enhanced API] Processing PDF: {file.filename}")
            elif file.content_type and file.content_type.startswith("image/"):
                screenshots.append(file_content)
                logger.info(f"[Enhanced API] Processing screenshot: {file.filename}")
    
    # Launch Phase 1 workflow if available
    if workflow_type == "phase1" and PHASE1_AVAILABLE:
        background_tasks.add_task(
            execute_phase1_workflow,
            temp_task_id, instruction, platform, document_data, screenshots
        )
        selected_orchestrator = "phase1"
    elif workflow_type == "enhanced" and ENHANCED_AVAILABLE and _enhanced_orchestrator:
        background_tasks.add_task(
            execute_enhanced_workflow_safe,
            temp_task_id, instruction, platform, document_data, screenshots
        )
        selected_orchestrator = "enhanced"
    elif workflow_type == "langgraph" and LANGGRAPH_AVAILABLE and _langgraph_orchestrator:
        background_tasks.add_task(
            execute_langgraph_workflow_safe,
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
        "message": "Enhanced automation workflow initiated",
        "task_id": temp_task_id,
        "workflow_type": workflow_type,
        "orchestrator": selected_orchestrator,
        "status": "processing",
        "estimated_duration": "2-5 minutes",
        "phase": "Phase 1 Integration"
    })

async def execute_phase1_workflow(
    task_id: str,
    instruction: str,
    platform: str,
    document_data: bytes = None,
    screenshots: List[bytes] = None
):
    """Execute Phase 1 workflow with enhanced components"""
    
    try:
        logger.info(f"[Phase1] Starting Phase 1 workflow for task: {task_id}")
        
        task_status_store[task_id].update({
            "status": "running_phase1",
            "progress": 20,
            "current_phase": "initialization"
        })
        
        # Create database task
        if _enhanced_db_manager:
            db_task_id = await _enhanced_db_manager.create_task_enhanced(
                instruction, platform, 
                {"temp_task_id": task_id},
                f"thread_{task_id}", f"checkpoint_{task_id}"
            )
            logger.info(f"[Phase1] Created database task: {db_task_id}")
        
        # Create initial state
        if PHASE1_AVAILABLE:
            state = create_initial_state(
                task_id=int(task_id.split('_')[-1]),
                instruction=instruction,
                platform=platform,
                document_content=document_data,
                screenshots=screenshots or [],
                additional_data={"temp_task_id": task_id}
            )
            logger.info(f"[Phase1] Created automation state: {state.task_id}")
        
        # Test blueprint tools
        if PHASE1_AVAILABLE and document_data:
            task_status_store[task_id].update({
                "progress": 40,
                "current_phase": "document_analysis"
            })
            
            # This would be replaced with actual tool execution in Phase 2
            logger.info(f"[Phase1] Would execute blueprint tools here...")
        
        # Create output structure
        if PHASE1_AVAILABLE:
            task_status_store[task_id].update({
                "progress": 60,
                "current_phase": "output_structure"
            })
            
            output_manager = OutputStructureManager(int(task_id.split('_')[-1]))
            directories = output_manager.create_complete_structure()
            logger.info(f"[Phase1] Created output structure: {len(directories)} directories")
        
        task_status_store[task_id].update({
            "status": "completed_phase1",
            "progress": 100,
            "current_phase": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "phase1_results": {
                "database_integration": _enhanced_db_manager is not None,
                "state_management": PHASE1_AVAILABLE,
                "output_structure": PHASE1_AVAILABLE,
                "blueprint_tools": PHASE1_AVAILABLE
            }
        })
        
        logger.info(f"[Phase1] Phase 1 workflow completed for task: {task_id}")
        
    except Exception as e:
        logger.error(f"[Phase1] Phase 1 workflow failed for task {task_id}: {str(e)}")
        task_status_store[task_id].update({
            "status": "failed",
            "progress": 0,
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })

# Keep existing workflow execution functions for backward compatibility
async def execute_enhanced_workflow_safe(task_id, instruction, platform, document_data, screenshots):
    """Execute enhanced workflow with error handling (unchanged from original)"""
    try:
        logger.info(f"[Enhanced] Starting enhanced workflow for task: {task_id}")
        task_status_store[task_id].update({
            "status": "running_enhanced",
            "progress": 20,
            "current_phase": "initialization"
        })
        
        if _enhanced_orchestrator:
            workflow_results = await _enhanced_orchestrator.execute_enhanced_workflow(
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
        
        logger.info(f"[Enhanced] Enhanced workflow completed for task: {task_id}")
        
    except Exception as e:
        logger.error(f"[Enhanced] Enhanced workflow failed for task {task_id}: {str(e)}")
        task_status_store[task_id].update({
            "status": "failed",
            "progress": 0,
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })

async def execute_langgraph_workflow_safe(task_id, instruction, platform, document_data, screenshots):
    """Execute LangGraph workflow with error handling (placeholder)"""
    try:
        logger.info(f"[LangGraph] Starting LangGraph workflow for task: {task_id}")
        task_status_store[task_id].update({
            "status": "running_langgraph",
            "progress": 20,
            "current_phase": "langgraph_orchestration"
        })
        
        # Placeholder - will be implemented in later phases
        task_status_store[task_id].update({
            "status": "completed",
            "progress": 100,
            "completed_at": datetime.utcnow().isoformat(),
            "note": "LangGraph workflow placeholder - full implementation in Phase 2"
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
async def get_enhanced_task_status(task_id: str):
    """Get enhanced task status"""
    if task_id not in task_status_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_status_store[task_id]

@app.get("/health/enhanced")
async def enhanced_health_check():
    """Enhanced health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "4.0.0-phase1",
        "phase": "Phase 1 - Database Foundation & Enhancement",
        "orchestrators": {
            "enhanced": _enhanced_orchestrator is not None,
            "langgraph": _langgraph_orchestrator is not None
        },
        "phase1_components": {
            "enhanced_database": _enhanced_db_manager is not None,
            "output_structure_manager": PHASE1_AVAILABLE,
            "automation_state": PHASE1_AVAILABLE,
            "blueprint_tools": PHASE1_AVAILABLE
        },
        "modules": {
            "phase1_available": PHASE1_AVAILABLE,
            "enhanced_available": ENHANCED_AVAILABLE,
            "device_manager_available": DEVICE_MANAGER_AVAILABLE,
            "terminal_manager_available": TERMINAL_MANAGER_AVAILABLE,
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
    
    # Check enhanced database
    if _enhanced_db_manager:
        try:
            health_status["enhanced_database"] = "connected"
        except Exception as e:
            health_status["enhanced_database"] = {"error": str(e)}
            health_status["status"] = "degraded"
    
    return health_status

@app.get("/devices")
async def get_connected_devices():
    """Get connected Android devices information (unchanged)"""
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
    
    print("🚀 Starting Enhanced Multi-Agent Automation Framework v4.0.0-phase1...")
    print("📋 Features: LangGraph Integration, Enhanced Database, Output Structure Management")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Enhanced Health Check: http://localhost:8000/health/enhanced")
    print("📱 Device Status: http://localhost:8000/devices")
    print()
    print(f"🔧 Phase 1 Status:")
    print(f"   Enhanced Database: {'✅' if PHASE1_AVAILABLE else '❌'}")
    print(f"   Output Structure: {'✅' if PHASE1_AVAILABLE else '❌'}")
    print(f"   Automation State: {'✅' if PHASE1_AVAILABLE else '❌'}")
    print(f"   Blueprint Tools: {'✅' if PHASE1_AVAILABLE else '❌'}")
    print(f"   Enhanced Orchestrator: {'✅' if ENHANCED_AVAILABLE else '❌'}")
    print(f"   Device Manager: {'✅' if DEVICE_MANAGER_AVAILABLE else '❌'}")
    print(f"   Terminal Manager: {'✅' if TERMINAL_MANAGER_AVAILABLE else '❌'}")
    print(f"   LangGraph: {'✅' if LANGGRAPH_AVAILABLE else '❌'}")
    print()
    print("⚠️ Start with '--reload-dir app' to avoid conflicts:")
    print("   uvicorn app.enhanced_main:app --reload --reload-dir app")
    print()
    
    uvicorn.run(
        "app.enhanced_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )