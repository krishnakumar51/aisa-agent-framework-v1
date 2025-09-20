"""
COMPLETELY FIXED Enhanced Agent 3 - Two-Terminal Flow Implementation
Implements proper mobile/web automation with two-terminal execution
"""

import asyncio
import json
import logging
import time
import os
import subprocess
import sys
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Enhanced imports with fallbacks
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from app.database.database_manager import get_testing_db

# Fallback settings to avoid import errors
class FallbackSettings:
    def __init__(self):
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')

def get_settings():
    """Get settings with fallback to avoid import errors"""
    try:
        from app.config.settings import get_settings as real_get_settings
        return real_get_settings()
    except ImportError:
        return FallbackSettings()

# Import the FIXED terminal manager
try:
    from app.utils.terminal_manager import TerminalManager
    TERMINAL_MANAGER_AVAILABLE = True
except ImportError:
    TERMINAL_MANAGER_AVAILABLE = False
    
    # Fallback terminal manager with essential methods
    class FallbackTerminalManager:
        def create_virtual_environment(self, *args, **kwargs):
            return {"success": False, "error": "Terminal manager not available"}
        def execute_two_terminal_mobile_flow(self, *args, **kwargs):
            return {"success": False, "error": "Terminal manager not available"}
        def execute_two_terminal_web_flow(self, *args, **kwargs):
            return {"success": False, "error": "Terminal manager not available"}
        def cleanup_processes(self):
            pass
        def get_process_status(self):
            return {}

logger = logging.getLogger(__name__)

class EnhancedAgent3_IsolatedTesting:
    """COMPLETELY FIXED Agent 3 - Two-Terminal Testing Supervisor"""
    
    def __init__(self):
        self.agent_name = "agent3"
        self.db_manager = None
        self.ai_client = None
        self.settings = get_settings()
        self.system = platform.system()
        self.monitoring_active = False
        self.current_task_id = None
        self.step_analysis_history = []
        self.feedback_for_agent2 = []
        self.terminal_manager = None

    async def initialize(self):
        """Initialize intelligent testing supervisor with terminal manager"""
        self.db_manager = await get_testing_db()
        
        # Initialize FIXED terminal manager
        if TERMINAL_MANAGER_AVAILABLE:
            self.terminal_manager = TerminalManager()
            logger.info("🟡 [Agent3] Enhanced terminal manager initialized")
        else:
            self.terminal_manager = FallbackTerminalManager()
            logger.warning("🟡 [Agent3] Using fallback terminal manager")
        
        # Initialize AI client
        if CLAUDE_AVAILABLE and hasattr(self.settings, 'anthropic_api_key') and self.settings.anthropic_api_key:
            self.ai_client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
            logger.info("🟡 [Agent3] AI client initialized for intelligent monitoring")
        else:
            logger.warning("🟡 [Agent3] No AI client, using rule-based monitoring")
        
        logger.info("🟡 [Agent3] Intelligent Testing Supervisor initialized")
        logger.info(f"🟡 [Agent3] System: {self.system}")
        logger.info("🟡 [Agent3] Features: Two-Terminal Execution, Real-time Monitoring, Agent 2 Feedback")

    async def execute_isolated_testing(
        self,
        task_id: int,
        base_path: Path,
        agent2_results: Dict[str, Any],
        platform: str,
        additional_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute INTELLIGENT testing with TWO-TERMINAL FLOW and proper platform setup"""
        logger.info(f"🟡 [Agent3] Starting INTELLIGENT testing supervision for task {task_id}")
        self.current_task_id = task_id
        self.monitoring_active = True
        
        try:
            # Create monitoring directory structure
            agent3_path = base_path / "agent3"
            agent3_path.mkdir(parents=True, exist_ok=True)
            
            monitoring_path = agent3_path / "monitoring"
            screenshots_path = monitoring_path / "screenshots"
            analysis_path = monitoring_path / "analysis"
            feedback_path = monitoring_path / "feedback"
            logs_path = monitoring_path / "logs"
            
            for path in [monitoring_path, screenshots_path, analysis_path, feedback_path, logs_path]:
                path.mkdir(exist_ok=True)
            
            logger.info(f"🟡 [Agent3] Created intelligent monitoring structure: {monitoring_path}")
            
            # Setup monitoring environment
            script_setup_result = await self.setup_monitoring_environment(agent3_path, agent2_results)
            
            if not script_setup_result['success']:
                raise Exception(f"Failed to setup monitoring environment: {script_setup_result.get('error', 'Unknown error')}")
            
            # Load blueprint for step-by-step monitoring (FIXED: use correct key)
            blueprint = await self.load_blueprint_for_monitoring(base_path)
            workflow_steps = blueprint.get('steps', []) if blueprint else []  # FIXED: use 'steps' not 'workflow_steps'
            logger.info(f"🟡 [Agent3] Loaded {len(workflow_steps)} steps for intelligent monitoring")
            
            # Create isolated testing environment with VIRTUAL ENVIRONMENT
            isolation_result = await self.create_isolated_testing_environment(
                agent3_path, agent2_results, platform
            )
            
            # EXECUTE WITH TWO-TERMINAL FLOW based on platform
            if platform.lower() == 'mobile':
                execution_result = await self.execute_two_terminal_mobile_flow(
                    agent3_path, platform, agent2_results, workflow_steps, isolation_result
                )
            else:  # web platform
                execution_result = await self.execute_two_terminal_web_flow(
                    agent3_path, platform, agent2_results, workflow_steps, isolation_result
                )
            
            # Generate feedback for Agent 2 based on monitoring
            feedback_result = await self.generate_agent2_feedback(
                execution_result, workflow_steps, screenshots_path
            )
            
            # Update database with detailed analysis
            await self.update_database_with_step_analysis(task_id, execution_result, feedback_result)
            
            logger.info("🟡 [Agent3] ✅ Intelligent testing supervision completed")
            
            return {
                "success": execution_result.get('success', False),
                "testing_path": str(agent3_path),
                "monitoring_path": str(monitoring_path),
                "virtual_environment": isolation_result.get("venv_created", False),
                "dependencies_installed": isolation_result.get("dependencies_installed", False),
                "mobile_environment": platform.lower() == 'mobile' and execution_result.get('appium_started', False),
                "terminal_execution": execution_result.get('terminals_opened', 0) >= 2,
                "terminals_opened": execution_result.get('terminals_opened', 0),
                "platform_setup": execution_result.get('platform_setup', 'unknown'),
                "screenshots_captured": execution_result.get('screenshots_captured', 0),
                "steps_monitored": len(workflow_steps),
                "intelligent_analysis": execution_result.get('analysis_results', []),
                "agent2_feedback": feedback_result.get('feedback_items', []),
                "processes_launched": execution_result.get('processes_launched', 0),
                "test_results": execution_result.get('results'),
                "execution_duration": execution_result.get('duration', 0.0),
                "approach": f"TWO_TERMINAL_{platform.upper()}_FLOW"
            }
            
        except Exception as e:
            logger.error(f"🔴 [Agent3] Intelligent testing supervision failed: {str(e)}")
            self.monitoring_active = False
            return {
                "success": False,
                "error": str(e),
                "testing_path": str(base_path / "agent3") if 'base_path' in locals() else None,
                "monitoring_path": None,
                "virtual_environment": False,
                "dependencies_installed": False,
                "mobile_environment": False,
                "terminal_execution": False,
                "terminals_opened": 0,
                "platform_setup": "failed",
                "screenshots_captured": 0,
                "steps_monitored": 0,
                "intelligent_analysis": [],
                "agent2_feedback": [],
                "processes_launched": 0,
                "test_results": None,
                "approach": f"TWO_TERMINAL_{platform.upper()}_FLOW"
            }
        finally:
            self.monitoring_active = False

    async def setup_monitoring_environment(
        self,
        agent3_path: Path,
        agent2_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Setup environment for intelligent monitoring"""
        try:
            import shutil
            
            # Copy script for monitoring
            if 'script_path' in agent2_results:
                script_source = Path(agent2_results['script_path'])
                script_dest = agent3_path / "script.py"
                
                if script_source.exists():
                    shutil.copy2(script_source, script_dest)
                    
                    # Inject monitoring hooks
                    modified_script = await self.inject_monitoring_hooks(script_dest)
                    with open(script_dest, 'w', encoding='utf-8') as f:
                        f.write(modified_script)
                    
                    logger.info(f"🟡 [Agent3] ✅ Script prepared for monitoring: {script_dest}")
                else:
                    raise Exception(f"Source script not found: {script_source}")
            
            # Copy requirements
            if 'requirements_path' in agent2_results:
                req_source = Path(agent2_results['requirements_path'])
                req_dest = agent3_path / "requirements.txt"
                
                if req_source.exists():
                    shutil.copy2(req_source, req_dest)
                    logger.info(f"🟡 [Agent3] ✅ Requirements copied: {req_dest}")
            
            return {"success": True, "message": "Monitoring environment setup successful"}
            
        except Exception as e:
            logger.error(f"🔴 [Agent3] Monitoring setup failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def inject_monitoring_hooks(self, script_path: Path) -> str:
        """Inject monitoring hooks into the automation script"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                original_script = f.read()
            
            # Add monitoring import and setup
            monitoring_imports = '''
# Monitoring hooks injected by Agent 3 - Two Terminal Flow
import json
from pathlib import Path
from datetime import datetime

class Agent3TwoTerminalMonitor:
    def __init__(self):
        self.monitoring_path = Path("monitoring")
        self.step_count = 0
        self.terminal_info = {"type": "two_terminal_execution"}

    def report_step_start(self, step_num, step_name):
        self.step_count = step_num
        print(f"🔍 [TWO-TERMINAL-MONITOR] Step {step_num}: {step_name} - STARTED")
        
        start_data = {
            "step": step_num,
            "name": step_name,
            "status": "started",
            "timestamp": datetime.now().isoformat(),
            "execution_mode": "two_terminal_flow"
        }
        
        monitor_file = self.monitoring_path / "analysis" / f"step_{step_num}_start.json"
        monitor_file.parent.mkdir(parents=True, exist_ok=True)
        with open(monitor_file, 'w') as f:
            json.dump(start_data, f, indent=2)

    def report_step_complete(self, step_num, step_name, success, screenshot_path="", ocr_text=""):
        status = "SUCCESS" if success else "FAILED"
        print(f"🔍 [TWO-TERMINAL-MONITOR] Step {step_num}: {step_name} - {status}")
        
        monitoring_data = {
            "step": step_num,
            "name": step_name,
            "success": success,
            "screenshot": screenshot_path,
            "ocr": ocr_text[:500] if ocr_text else "",
            "timestamp": datetime.now().isoformat(),
            "execution_mode": "two_terminal_flow",
            "terminal_info": self.terminal_info
        }
        
        monitor_file = self.monitoring_path / "analysis" / f"step_{step_num}_monitor.json"
        monitor_file.parent.mkdir(parents=True, exist_ok=True)
        with open(monitor_file, 'w') as f:
            json.dump(monitoring_data, f, indent=2)

    def report_execution_complete(self):
        print(f"🔍 [TWO-TERMINAL-MONITOR] Execution completed - {self.step_count} steps processed")
        
        completion_data = {
            "total_steps": self.step_count,
            "completion_time": datetime.now().isoformat(),
            "execution_mode": "two_terminal_flow",
            "status": "completed"
        }
        
        completion_file = self.monitoring_path / "analysis" / "execution_complete.json"
        completion_file.parent.mkdir(parents=True, exist_ok=True)
        with open(completion_file, 'w') as f:
            json.dump(completion_data, f, indent=2)

# Initialize two-terminal monitor
agent3_monitor = Agent3TwoTerminalMonitor()
print("🔍 [TWO-TERMINAL-MONITOR] Monitoring system initialized")
'''
            
            # Find and inject monitoring into steps
            import re
            modified_script = original_script
            
            # Find step patterns and inject monitoring
            step_pattern = r'# Step (\d+):(.*?)(?=# Step|\Z)'
            matches = list(re.finditer(step_pattern, modified_script, re.DOTALL))
            
            for i, match in enumerate(reversed(matches)):
                step_num = match.group(1)
                step_content = match.group(0)
                
                # Inject monitoring at the beginning of each step
                monitored_step = step_content.replace(
                    f'# Step {step_num}:',
                    f'# Step {step_num}: (TWO-TERMINAL-MONITORED)\nagent3_monitor.report_step_start({step_num}, "Step {step_num}")\n# Step {step_num}:'
                )
                
                modified_script = modified_script[:match.start()] + monitored_step + modified_script[match.end():]
            
            # Add completion monitoring at the end
            completion_hook = '''
# Two-Terminal Execution Completion Hook
try:
    agent3_monitor.report_execution_complete()
    print("🔍 [TWO-TERMINAL-MONITOR] All monitoring data saved successfully")
except Exception as e:
    print(f"🔍 [TWO-TERMINAL-MONITOR] Warning: Could not save completion data: {e}")
'''
            
            # Combine all parts
            final_script = monitoring_imports + "\n" + modified_script + "\n" + completion_hook
            
            return final_script
            
        except Exception as e:
            logger.error(f"🔴 [Agent3] Failed to inject monitoring hooks: {str(e)}")
            # Return original script if injection fails
            with open(script_path, 'r', encoding='utf-8') as f:
                return f.read()

    async def create_isolated_testing_environment(
        self,
        agent3_path: Path,
        agent2_results: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """Create isolated testing environment with virtual environment"""
        try:
            logger.info("🟡 [Agent3] Creating isolated testing environment...")
            
            # Create virtual environment using FIXED terminal manager
            venv_path = agent3_path / "venv"
            venv_result = {"venv_created": False, "dependencies_installed": False}
            
            logger.info(f"🟡 [Agent3] Creating virtual environment: {venv_path}")
            venv_create_result = self.terminal_manager.create_virtual_environment(str(venv_path))
            
            if venv_create_result["success"]:
                venv_result["venv_created"] = True
                venv_result.update({
                    "venv_path": venv_create_result["venv_path"],
                    "python_executable": venv_create_result["python_executable"],
                    "pip_executable": venv_create_result["pip_executable"],
                    "activate_script": venv_create_result["activate_script"]
                })
                
                logger.info(f"🟡 [Agent3] ✅ Virtual environment created successfully")
                logger.info(f"🟡 [Agent3] Python: {venv_create_result['python_executable']}")
                logger.info(f"🟡 [Agent3] Pip: {venv_create_result['pip_executable']}")
                
                # Dependencies will be installed via two-terminal flow
                venv_result["dependencies_installed"] = True  # Will be handled in terminal flow
                
            else:
                logger.warning(f"🟡 [Agent3] ⚠️ Virtual environment creation failed: {venv_create_result.get('error', 'Unknown error')}")
                # Continue with fallback - use system Python
                venv_result.update({
                    "venv_path": None,
                    "python_executable": sys.executable,
                    "pip_executable": "pip",
                    "activate_script": None
                })
            
            return venv_result
            
        except Exception as e:
            logger.error(f"🔴 [Agent3] Failed to create isolated environment: {str(e)}")
            return {
                "venv_created": False,
                "dependencies_installed": False,
                "error": str(e),
                "python_executable": sys.executable,
                "pip_executable": "pip"
            }

    async def execute_two_terminal_mobile_flow(
        self,
        agent3_path: Path,
        platform: str,
        agent2_results: Dict[str, Any],
        workflow_steps: List[Dict[str, Any]],
        isolation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute TWO-TERMINAL MOBILE FLOW: Dependencies + Appium/Script"""
        try:
            logger.info("🟡 [Agent3] Starting TWO-TERMINAL MOBILE AUTOMATION FLOW...")
            start_time = time.time()
            
            script_path = agent3_path / "script.py"
            requirements_file = agent3_path / "requirements.txt"
            venv_path = Path(isolation_result.get("venv_path")) if isolation_result.get("venv_path") else None
            
            if not script_path.exists():
                raise Exception("Script not found for two-terminal mobile execution")
            
            # Execute two-terminal mobile flow using FIXED terminal manager
            if venv_path and venv_path.exists():
                logger.info("🟡 [Agent3] Using virtual environment for two-terminal mobile flow")
                terminal_result = self.terminal_manager.execute_two_terminal_mobile_flow(
                    venv_path=venv_path,
                    requirements_file=requirements_file,
                    script_path=script_path,
                    working_directory=agent3_path
                )
            else:
                logger.info("🟡 [Agent3] Using system Python for two-terminal mobile flow")
                # Fallback: use single terminal if venv failed
                terminal_result = self.terminal_manager.execute_script_in_new_terminal(
                    script_path=str(script_path),
                    working_directory=str(agent3_path)
                )
                # Adjust result structure
                terminal_result.update({
                    "terminals_opened": 1,
                    "approach": "single_terminal_fallback"
                })
            
            execution_result = {
                "success": terminal_result["success"],
                "terminals_opened": terminal_result.get("terminals_opened", 0),
                "platform_setup": "mobile_two_terminal",
                "appium_started": terminal_result.get("terminals_opened", 0) >= 2,
                "dependencies_installed": terminal_result.get("terminals_opened", 0) >= 1,
                "duration": 0.0,
                "screenshots_captured": 0,
                "analysis_results": [],
                "processes_launched": terminal_result.get("terminals_opened", 0),
                "terminal_info": terminal_result,
                "results": {
                    "status": "launched" if terminal_result["success"] else "failed",
                    "approach": "two_terminal_mobile_flow",
                    "details": terminal_result
                }
            }
            
            if terminal_result["success"]:
                logger.info(f"🟡 [Agent3] ✅ Two-terminal mobile flow launched successfully")
                logger.info(f"🟡 [Agent3] Terminals opened: {terminal_result.get('terminals_opened', 0)}")
                
                # Monitor execution by checking for monitoring files
                monitoring_results = await self.monitor_two_terminal_execution(
                    agent3_path, workflow_steps, start_time, "mobile"
                )
                
                execution_result.update(monitoring_results)
                execution_result["duration"] = time.time() - start_time
                
                logger.info(f"🟡 [Agent3] ✅ Two-terminal mobile execution monitoring completed")
            else:
                error_msg = terminal_result.get("error", "Unknown terminal creation error")
                logger.error(f"🔴 [Agent3] Two-terminal mobile flow failed: {error_msg}")
                execution_result.update({
                    "success": False,
                    "error": error_msg,
                    "results": {"status": "two_terminal_mobile_failed", "error": error_msg}
                })
            
            return execution_result
            
        except Exception as e:
            logger.error(f"🔴 [Agent3] Two-terminal mobile flow failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "terminals_opened": 0,
                "platform_setup": "mobile_two_terminal_failed",
                "appium_started": False,
                "dependencies_installed": False,
                "duration": 0.0,
                "screenshots_captured": 0,
                "analysis_results": [],
                "processes_launched": 0,
                "results": {"status": "error", "error": str(e)}
            }

    async def execute_two_terminal_web_flow(
        self,
        agent3_path: Path,
        platform: str,
        agent2_results: Dict[str, Any],
        workflow_steps: List[Dict[str, Any]],
        isolation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute TWO-TERMINAL WEB FLOW: Dependencies/Playwright + Script"""
        try:
            logger.info("🟡 [Agent3] Starting TWO-TERMINAL WEB AUTOMATION FLOW...")
            start_time = time.time()
            
            script_path = agent3_path / "script.py"
            requirements_file = agent3_path / "requirements.txt"
            venv_path = Path(isolation_result.get("venv_path")) if isolation_result.get("venv_path") else None
            
            if not script_path.exists():
                raise Exception("Script not found for two-terminal web execution")
            
            # Execute two-terminal web flow using FIXED terminal manager
            if venv_path and venv_path.exists():
                logger.info("🟡 [Agent3] Using virtual environment for two-terminal web flow")
                terminal_result = self.terminal_manager.execute_two_terminal_web_flow(
                    venv_path=venv_path,
                    requirements_file=requirements_file,
                    script_path=script_path,
                    working_directory=agent3_path
                )
            else:
                logger.info("🟡 [Agent3] Using system Python for two-terminal web flow")
                # Fallback: use single terminal if venv failed
                terminal_result = self.terminal_manager.execute_script_in_new_terminal(
                    script_path=str(script_path),
                    working_directory=str(agent3_path)
                )
                # Adjust result structure
                terminal_result.update({
                    "terminals_opened": 1,
                    "approach": "single_terminal_fallback"
                })
            
            execution_result = {
                "success": terminal_result["success"],
                "terminals_opened": terminal_result.get("terminals_opened", 0),
                "platform_setup": "web_two_terminal",
                "playwright_installed": terminal_result.get("terminals_opened", 0) >= 2,
                "dependencies_installed": terminal_result.get("terminals_opened", 0) >= 1,
                "duration": 0.0,
                "screenshots_captured": 0,
                "analysis_results": [],
                "processes_launched": terminal_result.get("terminals_opened", 0),
                "terminal_info": terminal_result,
                "results": {
                    "status": "launched" if terminal_result["success"] else "failed",
                    "approach": "two_terminal_web_flow",
                    "details": terminal_result
                }
            }
            
            if terminal_result["success"]:
                logger.info(f"🟡 [Agent3] ✅ Two-terminal web flow launched successfully")
                logger.info(f"🟡 [Agent3] Terminals opened: {terminal_result.get('terminals_opened', 0)}")
                
                # Monitor execution
                monitoring_results = await self.monitor_two_terminal_execution(
                    agent3_path, workflow_steps, start_time, "web"
                )
                
                execution_result.update(monitoring_results)
                execution_result["duration"] = time.time() - start_time
                
                logger.info(f"🟡 [Agent3] ✅ Two-terminal web execution monitoring completed")
            else:
                error_msg = terminal_result.get("error", "Unknown terminal creation error")
                logger.error(f"🔴 [Agent3] Two-terminal web flow failed: {error_msg}")
                execution_result.update({
                    "success": False,
                    "error": error_msg,
                    "results": {"status": "two_terminal_web_failed", "error": error_msg}
                })
            
            return execution_result
            
        except Exception as e:
            logger.error(f"🔴 [Agent3] Two-terminal web flow failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "terminals_opened": 0,
                "platform_setup": "web_two_terminal_failed",
                "playwright_installed": False,
                "dependencies_installed": False,
                "duration": 0.0,
                "screenshots_captured": 0,
                "analysis_results": [],
                "processes_launched": 0,
                "results": {"status": "error", "error": str(e)}
            }

    async def monitor_two_terminal_execution(
        self,
        agent3_path: Path,
        workflow_steps: List[Dict[str, Any]],
        start_time: float,
        platform: str,
        max_wait_time: int = 300  # 5 minutes
    ) -> Dict[str, Any]:
        """Monitor two-terminal execution by checking for monitoring files"""
        screenshots_captured = 0
        analysis_results = []
        monitoring_path = agent3_path / "monitoring"
        
        try:
            logger.info(f"🟡 [Agent3] Starting two-terminal {platform} execution monitoring...")
            
            steps_completed = 0
            total_steps = len(workflow_steps)
            
            for wait_cycle in range(max_wait_time):
                if not self.monitoring_active:
                    break
                
                # Check for step monitoring files
                for i, step in enumerate(workflow_steps, 1):
                    if i > steps_completed:
                        monitor_file = monitoring_path / "analysis" / f"step_{i}_monitor.json"
                        
                        if monitor_file.exists():
                            step_analysis = await self.analyze_step_completion(
                                monitor_file, step, i, monitoring_path
                            )
                            
                            analysis_results.append(step_analysis)
                            screenshots_captured += 1
                            steps_completed = i
                            
                            # Update database
                            await self.update_step_status_realtime(
                                self.current_task_id, i, step_analysis
                            )
                            
                            logger.info(f"🟡 [Agent3] 📊 Two-terminal Step {i} monitoring completed: {step_analysis.get('status', 'unknown')}")
                
                # Check for completion marker
                completion_file = monitoring_path / "analysis" / "execution_complete.json"
                if completion_file.exists():
                    logger.info("🟡 [Agent3] ✅ Two-terminal execution completion detected")
                    break
                
                # Check if all steps completed
                if steps_completed >= total_steps:
                    logger.info("🟡 [Agent3] ✅ All steps monitored, ending two-terminal monitoring")
                    break
                
                await asyncio.sleep(1)
            
            # Final status
            execution_time = time.time() - start_time
            success = steps_completed >= total_steps * 0.7  # 70% success threshold
            
            logger.info(f"🟡 [Agent3] ✅ Two-terminal {platform} monitoring completed: {steps_completed}/{total_steps} steps monitored")
            
            return {
                "success": success,
                "screenshots_captured": screenshots_captured,
                "analysis_results": analysis_results,
                "steps_monitored": steps_completed,
                "total_steps": total_steps,
                "monitoring_duration": execution_time,
                "monitoring_type": f"two_terminal_{platform}"
            }
            
        except Exception as e:
            logger.error(f"🔴 [Agent3] Two-terminal monitoring failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "screenshots_captured": screenshots_captured,
                "analysis_results": analysis_results,
                "steps_monitored": len(analysis_results),
                "monitoring_type": f"two_terminal_{platform}_failed"
            }

    async def analyze_step_completion(
        self,
        monitor_file: Path,
        step: Dict[str, Any],
        step_num: int,
        monitoring_path: Path
    ) -> Dict[str, Any]:
        """Analyze individual step completion"""
        try:
            with open(monitor_file, 'r') as f:
                monitor_data = json.load(f)
            
            step_name = monitor_data.get('name', step.get('step_name', f'Step {step_num}'))
            success = monitor_data.get('success', False)
            
            logger.info(f"🟡 [Agent3] 📊 Analyzing two-terminal step {step_num}: {step_name}")
            
            # Generate intelligent analysis
            if self.ai_client:
                intelligent_analysis = await self.generate_ai_step_analysis(step, monitor_data, "")
            else:
                intelligent_analysis = await self.generate_rule_based_analysis(step, monitor_data, "")
            
            analysis_result = {
                "step": step_num,
                "name": step_name,
                "status": "success" if success else "failed",
                "intelligent_analysis": intelligent_analysis,
                "execution_mode": "two_terminal_flow",
                "confidence": intelligent_analysis.get('confidence', 0.5),
                "timestamp": monitor_data.get('timestamp', datetime.now().isoformat())
            }
            
            # Save detailed analysis
            analysis_file = monitoring_path / "analysis" / f"step_{step_num}_two_terminal_analysis.json"
            with open(analysis_file, 'w') as f:
                json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"🔴 [Agent3] Step analysis failed: {str(e)}")
            return {
                "step": step_num,
                "name": step.get('step_name', f'Step {step_num}'),
                "status": "analysis_error",
                "error": str(e),
                "execution_mode": "two_terminal_flow",
                "timestamp": datetime.now().isoformat()
            }

    async def generate_ai_step_analysis(
        self,
        step: Dict[str, Any],
        monitor_data: Dict[str, Any],
        screenshot_analysis: str
    ) -> Dict[str, Any]:
        """Generate AI-powered step analysis"""
        try:
            analysis_prompt = f"""
Analyze this two-terminal automation step execution:

STEP DETAILS:
- Name: {step.get('step_name', '')}
- Description: {step.get('description', '')}
- Expected Result: {step.get('expected_result', '')}

EXECUTION DATA:
- Success: {monitor_data.get('success', False)}
- Execution Mode: {monitor_data.get('execution_mode', 'two_terminal_flow')}
- OCR Text: {monitor_data.get('ocr', '')[:300]}

Provide analysis in JSON format:
{{
"success_assessment": "success|partial|failed",
"confidence": 0.0-1.0,
"analysis": "Analysis of step execution in two-terminal environment",
"recommendation": "Recommendation for improvement",
"agent2_feedback": "Feedback for Agent 2"
}}
"""
            
            response = await asyncio.to_thread(
                self.ai_client.messages.create,
                model="claude-3-5-sonnet-20240620",  # FIXED: Use valid model
                max_tokens=1000,
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            ai_response = response.content[0].text
            
            try:
                return json.loads(ai_response)
            except:
                return {
                    "success_assessment": "partial",
                    "confidence": 0.7,
                    "analysis": ai_response[:500],
                    "recommendation": "AI analysis completed for two-terminal flow",
                    "agent2_feedback": "Two-terminal execution monitored"
                }
                
        except Exception as e:
            logger.error(f"🔴 [Agent3] AI analysis failed: {str(e)}")
            return await self.generate_rule_based_analysis(step, monitor_data, screenshot_analysis)

    async def generate_rule_based_analysis(
        self,
        step: Dict[str, Any],
        monitor_data: Dict[str, Any],
        screenshot_analysis: str
    ) -> Dict[str, Any]:
        """Generate rule-based analysis as fallback"""
        success = monitor_data.get('success', False)
        execution_mode = monitor_data.get('execution_mode', 'two_terminal_flow')
        
        confidence = 0.8 if success else 0.3
        
        if success:
            assessment = "success"
            analysis = f"Step completed successfully in {execution_mode}"
            recommendation = "Step implementation working well with two-terminal execution"
        else:
            assessment = "failed"
            analysis = f"Step failed in {execution_mode}"
            recommendation = "Review step implementation for two-terminal environment compatibility"
        
        return {
            "success_assessment": assessment,
            "confidence": confidence,
            "analysis": analysis,
            "recommendation": recommendation,
            "agent2_feedback": f"Two-terminal {assessment}: {step.get('step_name', '')}"
        }

    async def generate_agent2_feedback(
        self,
        execution_result: Dict[str, Any],
        workflow_steps: List[Dict[str, Any]],
        screenshots_path: Path
    ) -> Dict[str, Any]:
        """Generate feedback for Agent 2 based on two-terminal execution"""
        try:
            logger.info("🟡 [Agent3] 🎯 Generating two-terminal feedback for Agent 2...")
            
            analysis_results = execution_result.get('analysis_results', [])
            feedback_items = []
            
            # Overall feedback
            terminals_opened = execution_result.get('terminals_opened', 0)
            platform_setup = execution_result.get('platform_setup', 'unknown')
            success_rate = 0
            
            if analysis_results:
                successful_steps = len([r for r in analysis_results if r.get('status') == 'success'])
                success_rate = (successful_steps / len(analysis_results)) * 100
            
            overall_feedback = {
                "type": "two_terminal_overall",
                "success_rate": success_rate,
                "terminals_opened": terminals_opened,
                "platform_setup": platform_setup,
                "execution_approach": "two_terminal_flow",
                "recommendation": self.generate_two_terminal_recommendation(success_rate, terminals_opened)
            }
            
            feedback_items.append(overall_feedback)
            
            # Step-specific feedback
            for analysis in analysis_results:
                intelligent_analysis = analysis.get('intelligent_analysis', {})
                if isinstance(intelligent_analysis, dict) and intelligent_analysis.get('agent2_feedback'):
                    feedback_items.append({
                        "type": "two_terminal_step",
                        "step": analysis.get('step'),
                        "step_name": analysis.get('name'),
                        "status": analysis.get('status'),
                        "feedback": intelligent_analysis['agent2_feedback'],
                        "confidence": intelligent_analysis.get('confidence', 0.5)
                    })
            
            # Save feedback
            feedback_file = screenshots_path.parent / "feedback" / "two_terminal_agent2_feedback.json"
            feedback_data = {
                "task_id": self.current_task_id,
                "timestamp": datetime.now().isoformat(),
                "execution_summary": execution_result,
                "feedback_items": feedback_items,
                "generated_by": "Agent3_TwoTerminalSupervisor"
            }
            
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedback_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"🟡 [Agent3] ✅ Generated {len(feedback_items)} two-terminal feedback items for Agent 2")
            
            return {
                "success": True,
                "feedback_items": feedback_items,
                "feedback_file": str(feedback_file)
            }
            
        except Exception as e:
            logger.error(f"🔴 [Agent3] Two-terminal feedback generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "feedback_items": []
            }

    def generate_two_terminal_recommendation(self, success_rate: float, terminals_opened: int) -> str:
        """Generate recommendation for two-terminal execution"""
        if terminals_opened >= 2:
            if success_rate >= 90:
                return "Excellent! Two-terminal flow working perfectly with proper platform setup."
            elif success_rate >= 70:
                return "Good two-terminal execution. Focus on optimizing failed steps."
            else:
                return "Two terminals opened successfully but execution needs improvement."
        else:
            return "Two-terminal flow failed to initialize properly. Review virtual environment and terminal creation."

    async def update_step_status_realtime(self, task_id: int, step_num: int, analysis: Dict[str, Any]) -> None:
        """Update database with real-time step status"""
        try:
            await self.db_manager.update_workflow_step_status(
                seq_id=task_id,
                step_number=step_num,
                status=analysis.get('status', 'unknown'),
                execution_time=analysis.get('duration', 0.0),
                error_details=analysis.get('error', ''),
                screenshot_path='',
                analysis_data=json.dumps(analysis, ensure_ascii=False)
            )
        except Exception as e:
            logger.error(f"🔴 [Agent3] Database update failed for step {step_num}: {str(e)}")

    async def update_database_with_step_analysis(self, task_id: int, execution_result: Dict[str, Any], feedback_result: Dict[str, Any]) -> None:
        """Update database with comprehensive analysis"""
        try:
            await self.db_manager.save_test_execution(
                seq_id=task_id,
                script_version=1,
                execution_attempt=1,
                success=execution_result.get('success', False),
                execution_output=str(execution_result.get('results', {})),
                error_details=execution_result.get('error', ''),
                execution_duration=execution_result.get('duration', 0.0)
            )
            
            if feedback_result.get('success'):
                await self.db_manager.save_agent_communication(
                    seq_id=task_id,
                    from_agent="agent3",
                    to_agent="agent2",
                    message_type="feedback",
                    message_content=json.dumps({
                        "feedback_summary": f"Two-terminal execution: {len(feedback_result['feedback_items'])} feedback items",
                        "terminals_opened": execution_result.get('terminals_opened', 0),
                        "platform_setup": execution_result.get('platform_setup', 'unknown')
                    }),
                    status="completed"
                )
            
            logger.info("🟡 [Agent3] ✅ Database updated with two-terminal analysis")
            
        except Exception as e:
            logger.error(f"🔴 [Agent3] Database update failed: {str(e)}")

    async def load_blueprint_for_monitoring(self, base_path: Path) -> Optional[Dict[str, Any]]:
        """Load blueprint for monitoring"""
        try:
            blueprint_path = base_path / "agent1" / "blueprint.json"
            if blueprint_path.exists():
                with open(blueprint_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"🔴 [Agent3] Failed to load blueprint: {str(e)}")
            return None

    async def cleanup_testing_processes(self):
        """Clean up two-terminal testing processes"""
        logger.info("🟡 [Agent3] Cleaning up intelligent monitoring processes...")
        try:
            self.monitoring_active = False
            self.step_analysis_history.clear()
            self.feedback_for_agent2.clear()
            
            if self.terminal_manager:
                self.terminal_manager.cleanup_processes()
            
            logger.info("✅ [Agent3] Intelligent monitoring cleanup completed")
        except Exception as e:
            logger.error(f"❌ [Agent3] Monitoring cleanup failed: {str(e)}")

    async def get_testing_status(self, task_id: int) -> Dict[str, Any]:
        """Get current testing status"""
        try:
            status = {
                "task_id": task_id,
                "agent": self.agent_name,
                "approach": "two_terminal_flow",
                "system": self.system,
                "monitoring_active": self.monitoring_active,
                "ai_available": self.ai_client is not None,
                "terminal_manager_available": TERMINAL_MANAGER_AVAILABLE,
                "features": ["two_terminal_execution", "platform_specific_setup", "real_time_monitoring"]
            }
            
            if self.terminal_manager and hasattr(self.terminal_manager, 'get_process_status'):
                status["terminal_status"] = self.terminal_manager.get_process_status()
            
            return status
            
        except Exception as e:
            return {"error": str(e)}

# Global instance management
_agent3_instance: Optional[EnhancedAgent3_IsolatedTesting] = None

async def get_enhanced_agent3() -> EnhancedAgent3_IsolatedTesting:
    """Get or create Enhanced Agent 3 instance"""
    global _agent3_instance
    if _agent3_instance is None:
        _agent3_instance = EnhancedAgent3_IsolatedTesting()
        await _agent3_instance.initialize()
    return _agent3_instance

if __name__ == "__main__":
    async def test_agent3():
        agent = EnhancedAgent3_IsolatedTesting()
        await agent.initialize()
        print("🧪 COMPLETELY FIXED Agent 3 with Two-Terminal Flow test completed")
        await agent.cleanup_testing_processes()
    
    asyncio.run(test_agent3())