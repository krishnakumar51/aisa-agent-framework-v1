"""
Fixed Main Application - Resolves all critical issues
Complete patch to fix multiple framework issues
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

# Global flags (must be at module level for proper scope)
ENHANCED_AVAILABLE = False
DEVICE_MANAGER_AVAILABLE = False
TERMINAL_MANAGER_AVAILABLE = False
LANGGRAPH_AVAILABLE = False

# Try enhanced imports with fallbacks
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

# Legacy orchestrator imports (should work)
from app.database.database_manager import get_testing_db
from app.main_orchestrator import get_updated_orchestrator

# Try LangGraph import
try:
    from app.langgraph_orchestrator import get_langgraph_orchestrator
    LANGGRAPH_AVAILABLE = True
    print("✅ LangGraph orchestrator module available")
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    print(f"⚠️ LangGraph not available. Install with: pip install langgraph")

# Configure Tesseract path for Windows
if sys.platform == "win32":
    # Common Tesseract installation paths on Windows
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv("USERNAME", ""))
    ]
    
    for path in tesseract_paths:
        if os.path.exists(path):
            os.environ["TESSERACT_PATH"] = path
            print(f"✅ Tesseract found: {path}")
            break
    else:
        print("⚠️ Tesseract not found. Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Or set TESSERACT_PATH environment variable manually")

# Configure OCR and image processing
try:
    import pytesseract
    from PIL import Image
    print("🔧 Generic Web Automation Tools initialized")
except ImportError:
    print("⚠️ OCR tools not available - install Pillow and pytesseract")

try:
    from appium import webdriver
    from appium.options.android import UiAutomator2Options
    print("📱 Generic Mobile Automation Tools initialized")
except ImportError:
    print("⚠️ Mobile automation tools not available - install Appium-Python-Client")

# Global variables
task_status_store: Dict[str, Dict[str, Any]] = {}

# Enhanced logging configuration
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
_enhanced_orchestrator = None
_traditional_orchestrator = None
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
    
    def get_process_status(self) -> Dict[str, Any]:
        return {}
    
    def cleanup_processes(self):
        pass

async def initialize_orchestrators():
    """Initialize orchestrator systems with fallbacks"""
    global _enhanced_orchestrator, _traditional_orchestrator, _langgraph_orchestrator
    global _device_manager, _terminal_manager
    
    logger.info("🚀 Initializing Multi-Agent Automation Framework...")
    
    try:
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
                logger.info("✅ Enhanced orchestrator initialized (PRIMARY)")
            except Exception as e:
                logger.warning(f"⚠️ Enhanced orchestrator failed: {str(e)}")
        
        # Initialize traditional orchestrator (fallback)
        try:
            _traditional_orchestrator = await get_updated_orchestrator()
            logger.info("✅ Traditional orchestrator initialized")
        except Exception as e:
            logger.error(f"❌ Traditional orchestrator failed: {str(e)}")
        
        # Initialize LangGraph orchestrator (experimental)  
        if LANGGRAPH_AVAILABLE:
            try:
                _langgraph_orchestrator = await get_langgraph_orchestrator()
                logger.info("✅ LangGraph orchestrator initialized (EXPERIMENTAL)")
            except Exception as e:
                logger.warning(f"⚠️ LangGraph orchestrator failed: LangGraph is required but not installed")
        
        # Perform system health checks (simplified)
        await perform_system_health_check()
        logger.info("🎯 Orchestrator systems ready")
        
    except Exception as e:
        logger.error(f"❌ Orchestrator initialization failed: {str(e)}")
        # Don't raise - continue with partial initialization
        logger.info("🔄 Continuing with partial initialization...")

async def perform_system_health_check():
    """Perform simplified system health checks"""
    health_status = {
        "enhanced_orchestrator": _enhanced_orchestrator is not None,
        "traditional_orchestrator": _traditional_orchestrator is not None,
        "langgraph_orchestrator": _langgraph_orchestrator is not None,
        "device_manager": _device_manager is not None,
        "terminal_manager": _terminal_manager is not None
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
    
    logger.info(f"📊 System Health Status: {json.dumps(health_status, indent=2)}")

async def cleanup_orchestrators():
    """Cleanup orchestrator resources (safely)"""
    global _enhanced_orchestrator, _terminal_manager
    
    logger.info("🧹 Cleaning up orchestrator resources...")
    try:
        # Cleanup enhanced orchestrator processes
        if _enhanced_orchestrator and hasattr(_enhanced_orchestrator, 'cleanup_workflow'):
            await _enhanced_orchestrator.cleanup_workflow(0)
        
        # Cleanup terminal manager processes
        if _terminal_manager and hasattr(_terminal_manager, 'cleanup_processes'):
            _terminal_manager.cleanup_processes()
        
        logger.info("✅ Orchestrator cleanup completed")
    except Exception as e:
        logger.warning(f"⚠️ Cleanup had issues: {str(e)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    logger.info("🚀 Multi-Agent Automation Framework starting up...")
    
    # Startup
    try:
        await initialize_orchestrators()
        logger.info("✅ Application startup completed")
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        # Continue with partial initialization
    
    yield
    
    # Shutdown
    logger.info("🛑 Multi-Agent Automation Framework shutting down...")
    await cleanup_orchestrators()
    logger.info("✅ Application shutdown completed")

# Initialize FastAPI with lifespan management
app = FastAPI(
    title="Multi-Agent Automation Framework",
    description="Production-ready automation with intelligent orchestration and device support",
    version="3.0.0-fully-fixed",
    lifespan=lifespan
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
    """Root endpoint with system status"""
    global _enhanced_orchestrator, _device_manager, _terminal_manager
    
    system_info = {
        "framework": "Multi-Agent Automation Framework",
        "version": "3.0.0-fully-fixed",
        "features": [
            "Multi-Orchestrator Support",
            "Device Detection" if _device_manager else "Basic Device Support",
            "Production Code Generation",  
            "Enhanced Error Handling"
        ],
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "orchestrators": {
            "enhanced": _enhanced_orchestrator is not None,
            "traditional": _traditional_orchestrator is not None,
            "langgraph": _langgraph_orchestrator is not None
        },
        "modules": {
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

@app.post("/automate")
async def automate_with_fallback(
    background_tasks: BackgroundTasks,
    workflow_type: str = Form(default="auto"),
    instruction: str = Form(...),
    platform: str = Form(...),
    files: List[UploadFile] = File(default=[])
):
    """
    Automation endpoint with intelligent fallbacks
    
    workflow_type options:
    - auto: Use best available orchestrator (recommended)
    - enhanced: Use enhanced orchestrator (if available)
    - traditional: Use traditional orchestrator
    - langgraph: Use LangGraph orchestrator (if available)
    """
    # Generate temp task ID
    temp_task_id = f"temp_{int(time.time())}"
    logger.info(f"[API] Automation request - Temp ID: {temp_task_id}")
    logger.info(f"[API] Workflow Type: {workflow_type}")
    logger.info(f"[API] Instruction: {instruction}")
    logger.info(f"[API] Platform: {platform}")
    logger.info(f"[API] Files: {len(files)}")
    
    # Initialize task status
    task_status_store[temp_task_id] = {
        "temp_id": temp_task_id,
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
                logger.info(f"[API] Processing file: {file.filename} ({file.content_type})")
            elif file.content_type and file.content_type.startswith("image/"):
                screenshots.append(file_content)
                logger.info(f"[API] Processing screenshot: {file.filename}")
    
    # Determine best orchestrator
    selected_orchestrator = None
    selected_type = workflow_type
    
    if workflow_type == "auto":
        # Auto-select best available
        if ENHANCED_AVAILABLE and _enhanced_orchestrator:
            selected_orchestrator = "enhanced"
            selected_type = "enhanced"
        elif _traditional_orchestrator:
            selected_orchestrator = "traditional"  
            selected_type = "traditional"
        elif LANGGRAPH_AVAILABLE and _langgraph_orchestrator:
            selected_orchestrator = "langgraph"
            selected_type = "langgraph"
    elif workflow_type == "enhanced" and ENHANCED_AVAILABLE and _enhanced_orchestrator:
        selected_orchestrator = "enhanced"
    elif workflow_type == "traditional" and _traditional_orchestrator:
        selected_orchestrator = "traditional"
    elif workflow_type == "langgraph" and LANGGRAPH_AVAILABLE and _langgraph_orchestrator:
        selected_orchestrator = "langgraph"
    
    # Default to traditional if nothing else available
    if not selected_orchestrator and _traditional_orchestrator:
        selected_orchestrator = "traditional"
        selected_type = "traditional"
    
    # Launch workflow
    if selected_orchestrator == "enhanced":
        background_tasks.add_task(
            execute_enhanced_workflow_safe,
            temp_task_id, instruction, platform, document_data, screenshots
        )
    elif selected_orchestrator == "traditional":
        background_tasks.add_task(
            execute_traditional_workflow_safe,
            temp_task_id, instruction, platform, document_data, screenshots
        )
    elif selected_orchestrator == "langgraph":
        background_tasks.add_task(
            execute_langgraph_workflow_safe,
            temp_task_id, instruction, platform, document_data, screenshots
        )
    else:
        raise HTTPException(
            status_code=503,
            detail="No orchestrator available. Please check system status."
        )
    
    # Update task status
    task_status_store[temp_task_id].update({
        "status": "processing",
        "workflow_type": selected_type,
        "orchestrator": selected_orchestrator,
        "progress": 10
    })
    
    return JSONResponse({
        "success": True,
        "message": "Automation workflow initiated",
        "temp_task_id": temp_task_id,
        "workflow_type": selected_type,
        "orchestrator": selected_orchestrator,
        "status": "processing",
        "estimated_duration": "2-5 minutes"
    })

async def execute_enhanced_workflow_safe(
    temp_task_id: str,
    instruction: str,
    platform: str,
    document_data: bytes = None,
    screenshots: List[bytes] = None
):
    """Execute enhanced workflow with error handling"""
    try:
        logger.info(f"[API] Starting enhanced workflow for task: {temp_task_id}")
        
        task_status_store[temp_task_id].update({
            "status": "running_enhanced",
            "progress": 20,
            "current_phase": "initialization"
        })
        
        workflow_results = await _enhanced_orchestrator.execute_enhanced_workflow(
            instruction=instruction,
            platform=platform,
            document_data=document_data,
            screenshots=screenshots or [],
            additional_data={"temp_task_id": temp_task_id}
        )
        
        final_status = "completed" if workflow_results.get("overall_success") else "completed_with_issues"
        
        task_status_store[temp_task_id].update({
            "status": final_status,
            "progress": 100,
            "workflow_results": workflow_results,
            "completed_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"[API] Enhanced workflow completed for task: {temp_task_id}")
        
    except Exception as e:
        logger.error(f"[API] Enhanced workflow failed for task {temp_task_id}: {str(e)}")
        task_status_store[temp_task_id].update({
            "status": "failed",
            "progress": 0,
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })

async def execute_traditional_workflow_safe(
    temp_task_id: str,
    instruction: str,
    platform: str,
    document_data: bytes = None,
    screenshots: List[bytes] = None
):
    """Execute traditional workflow with error handling"""
    try:
        logger.info(f"[API] Starting traditional workflow for task: {temp_task_id}")
        
        task_status_store[temp_task_id].update({
            "status": "running_traditional",
            "progress": 20,
            "current_phase": "traditional_orchestration"
        })
        
        workflow_results = await _traditional_orchestrator.execute_workflow(
            instruction=instruction,
            platform=platform,
            document_data=document_data,
            screenshots=screenshots or []
        )
        
        final_status = "completed" if workflow_results.get("overall_success") else "completed_with_issues"
        
        task_status_store[temp_task_id].update({
            "status": final_status,
            "progress": 100,
            "workflow_results": workflow_results,
            "completed_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"[API] Traditional workflow completed for task: {temp_task_id}")
        
    except Exception as e:
        logger.error(f"[API] Traditional workflow failed for task {temp_task_id}: {str(e)}")
        task_status_store[temp_task_id].update({
            "status": "failed",
            "progress": 0,
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })

async def execute_langgraph_workflow_safe(
    temp_task_id: str,
    instruction: str,
    platform: str,
    document_data: bytes = None,
    screenshots: List[bytes] = None
):
    """Execute LangGraph workflow with error handling"""
    try:
        logger.info(f"[API] Starting LangGraph workflow for task: {temp_task_id}")
        
        task_status_store[temp_task_id].update({
            "status": "running_langgraph",
            "progress": 20,
            "current_phase": "langgraph_orchestration"
        })
        
        workflow_results = await _langgraph_orchestrator.execute_workflow(
            instruction=instruction,
            platform=platform,
            document_data=document_data,
            screenshots=screenshots or []
        )
        
        final_status = "completed" if workflow_results.get("overall_success") else "completed_with_issues"
        
        task_status_store[temp_task_id].update({
            "status": final_status,
            "progress": 100,
            "workflow_results": workflow_results,
            "completed_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"[API] LangGraph workflow completed for task: {temp_task_id}")
        
    except Exception as e:
        logger.error(f"[API] LangGraph workflow failed for task {temp_task_id}: {str(e)}")
        task_status_store[temp_task_id].update({
            "status": "failed",
            "progress": 0,
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })

@app.get("/status/{temp_task_id}")
async def get_task_status(temp_task_id: str):
    """Get task status"""
    if temp_task_id not in task_status_store:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_status_store[temp_task_id]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0-fully-fixed",
        "orchestrators": {
            "enhanced": _enhanced_orchestrator is not None,
            "traditional": _traditional_orchestrator is not None,
            "langgraph": _langgraph_orchestrator is not None
        },
        "modules": {
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
    
    # Check database
    try:
        db = await get_testing_db()
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
    
    print("🚀 Starting Multi-Agent Automation Framework v3.0.0-fully-fixed...")
    print("📋 Features: Intelligent Orchestration, Device Support, Production Code Generation")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📱 Device Status: http://localhost:8000/devices")
    print()
    print(f"🔧 Module Status:")
    print(f"   Enhanced Orchestrator: {'✅' if ENHANCED_AVAILABLE else '❌'}")
    print(f"   Device Manager: {'✅' if DEVICE_MANAGER_AVAILABLE else '❌'}")
    print(f"   Terminal Manager: {'✅' if TERMINAL_MANAGER_AVAILABLE else '❌'}")
    print(f"   LangGraph: {'✅' if LANGGRAPH_AVAILABLE else '❌'}")
    
    if "TESSERACT_PATH" in os.environ:
        print(f"✅ Tesseract configured: {os.environ['TESSERACT_PATH']}")
    else:
        print("⚠️ Tesseract not configured - OCR may not work")
    
    print("⚠️ Start with '--reload-dir app' to avoid conflicts:")
    print("   uvicorn app.updated_main_enhanced:app --reload --reload-dir app")
    print()
    
    uvicorn.run(
        "app.updated_main_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )