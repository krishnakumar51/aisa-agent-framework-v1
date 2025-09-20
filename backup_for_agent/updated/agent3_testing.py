"""
Updated Agent 3: Testing Environment Setup and Execution with OCR Validation
Sets up virtual environment, installs dependencies, runs tests, and validates with OCR
"""
import asyncio
import json
import logging
import time
import os
import subprocess
import sys
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import venv
import platform
import signal
import virtualenv
# Import the updated database manager
from app.database.database_manager import get_testing_db

logger = logging.getLogger(__name__)

class UpdatedAgent3_TestingEnvironment:
    """Agent 3: Testing Environment Setup and Execution with OCR Validation"""
    
    def __init__(self):
        self.agent_name = "agent3"
        self.db_manager = None
        self.max_test_attempts = 3
        
    async def initialize(self):
        """Initialize database connection"""
        self.db_manager = await get_testing_db()
        logger.info("🟡 Agent 3: Testing environment manager initialized")
    
    async def setup_and_execute_tests(self, seq_id: int) -> Dict[str, Any]:
        """
        Set up testing environment and execute automation tests
        
        Args:
            seq_id: Sequential task ID from Agent 2
            
        Returns:
            Test execution results with OCR validation
        """
        start_time = time.time()
        
        logger.info(f"🟡 [Agent3] Starting testing environment setup for task {seq_id}")
        
        try:
            # Get task information
            task_info = await self.db_manager.get_task_info(seq_id)
            if not task_info:
                raise Exception(f"Task {seq_id} not found in database")
            
            # Update task status
            await self.db_manager.update_task_status(seq_id, "testing_setup", "agent3")
            
            # Create agent3/testing folder structure
            base_path = Path(task_info['base_path'])
            agent3_path = base_path / "agent3"
            testing_path = agent3_path / "testing"
            testing_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"🟡 [Agent3] Created testing environment: {testing_path}")
            
            # Step 1: Setup virtual environment
            venv_setup_result = await self._setup_virtual_environment(seq_id, testing_path)
            if not venv_setup_result['success']:
                raise Exception(f"Virtual environment setup failed: {venv_setup_result['error']}")
            
            # Step 2: Install dependencies
            deps_result = await self._install_dependencies(seq_id, testing_path, base_path)
            if not deps_result['success']:
                raise Exception(f"Dependencies installation failed: {deps_result['error']}")
            
            # Step 3: Setup automation tools (Appium/Playwright)
            tools_result = await self._setup_automation_tools(seq_id, task_info['platform'], testing_path)
            if not tools_result['success']:
                logger.warning(f"🟡 [Agent3] Automation tools setup had issues: {tools_result.get('warning', 'Unknown')}")
            
            # Step 4: Copy script from agent2
            script_result = await self._copy_script_from_agent2(seq_id, testing_path, base_path)
            if not script_result['success']:
                raise Exception(f"Script copy failed: {script_result['error']}")
            
            # Step 5: Execute tests with OCR validation (up to 3 attempts)
            test_results = await self._execute_tests_with_validation(seq_id, testing_path, task_info['platform'])
            
            # Update task progress
            await self.db_manager.update_task_progress(seq_id, testing_completed=True)
            await self.db_manager.update_task_status(seq_id, "testing_completed", "agent3")
            
            processing_time = time.time() - start_time
            overall_success = test_results.get('overall_success', False)
            
            logger.info(f"🟡 [Agent3] ✅ Testing environment setup completed")
            logger.info(f"🟡 [Agent3] ✅ Test execution: {'SUCCESS' if overall_success else 'FAILED'}")
            logger.info(f"🟡 [Agent3] ✅ Total attempts: {test_results.get('total_attempts', 0)}")
            logger.info(f"🟡 [Agent3] ✅ Agent 2 collaborations: {test_results.get('agent2_collaborations', 0)}")
            
            return {
                "success": True,
                "seq_id": seq_id,
                "agent": self.agent_name,
                "testing_path": str(testing_path),
                "venv_setup": venv_setup_result,
                "dependencies_installed": deps_result,
                "automation_tools": tools_result,
                "script_copied": script_result,
                "test_results": test_results,
                "overall_test_success": overall_success,
                "total_attempts": test_results.get('total_attempts', 0),
                "agent2_collaborations": test_results.get('agent2_collaborations', 0),
                "processing_time": processing_time,
                "ready_for_reporting": True
            }
            
        except Exception as e:
            error_msg = f"Testing environment setup failed: {str(e)}"
            logger.error(f"🔴 [Agent3] {error_msg}")
            
            # Update task status
            await self.db_manager.update_task_status(seq_id, "testing_failed", "agent3")
            
            return {
                "success": False,
                "error": error_msg,
                "seq_id": seq_id,
                "agent": self.agent_name,
                "processing_time": time.time() - start_time
            }
    
    async def _setup_virtual_environment(self, seq_id: int, testing_path: Path) -> Dict[str, Any]:
        """Set up Python virtual environment"""
        logger.info(f"🟡 [Agent3] Setting up virtual environment...")
        
        try:
            venv_path = testing_path / "venv"
            
            # Remove existing venv if present
            if venv_path.exists():
                shutil.rmtree(venv_path)
            
            # Create virtual environment
            logger.info(f"🟡 [Agent3] Creating virtual environment: {venv_path}")
            virtualenv.cli_run([str(venv_path), "--clear"])
            
            # Record in database
            env_id = await self.db_manager.create_testing_environment(
                seq_id=seq_id,
                environment_type="python_venv",
                venv_path=str(venv_path)
            )
            
            await self.db_manager.update_testing_environment(
                seq_id=seq_id,
                setup_status="ready"
            )
            
            logger.info(f"🟡 [Agent3] ✅ Virtual environment created: {venv_path}")
            
            return {
                "success": True,
                "venv_path": str(venv_path),
                "env_id": env_id,
                "python_executable": str(self._get_venv_python(venv_path))
            }
            
        except Exception as e:
            error_msg = f"Virtual environment setup failed: {str(e)}"
            logger.error(f"🔴 [Agent3] {error_msg}")
            
            await self.db_manager.update_testing_environment(
                seq_id=seq_id,
                setup_status="failed",
                setup_error=error_msg
            )
            
            return {
                "success": False,
                "error": error_msg
            }
    
    async def _install_dependencies(self, seq_id: int, testing_path: Path, base_path: Path) -> Dict[str, Any]:
        """Install dependencies from requirements.txt"""
        logger.info(f"🟡 [Agent3] Installing dependencies...")
        
        try:
            venv_path = testing_path / "venv"
            python_exe = self._get_venv_python(venv_path)
            
            # Copy requirements.txt from agent2
            agent2_requirements = base_path / "agent2" / "requirements.txt"
            testing_requirements = testing_path / "requirements.txt"
            
            if not agent2_requirements.exists():
                raise Exception("Requirements.txt not found in agent2 folder")
            
            shutil.copy2(agent2_requirements, testing_requirements)
            logger.info(f"🟡 [Agent3] Copied requirements.txt to testing folder")
            
            # Install dependencies
            logger.info(f"🟡 [Agent3] Installing dependencies with pip...")
            
            install_cmd = [
                str(python_exe), "-m", "pip", "install", 
                "-r", str(testing_requirements),
                "--upgrade"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *install_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(testing_path)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                await self.db_manager.update_testing_environment(
                    seq_id=seq_id,
                    requirements_installed=True
                )
                
                logger.info(f"🟡 [Agent3] ✅ Dependencies installed successfully")
                
                return {
                    "success": True,
                    "requirements_path": str(testing_requirements),
                    "install_output": stdout.decode() if stdout else "",
                    "dependencies_count": len(open(testing_requirements).readlines())
                }
            else:
                error_output = stderr.decode() if stderr else "Unknown error"
                raise Exception(f"pip install failed: {error_output}")
                
        except Exception as e:
            error_msg = f"Dependencies installation failed: {str(e)}"
            logger.error(f"🔴 [Agent3] {error_msg}")
            
            await self.db_manager.update_testing_environment(
                seq_id=seq_id,
                requirements_installed=False,
                setup_error=error_msg
            )
            
            return {
                "success": False,
                "error": error_msg
            }
    
    async def _setup_automation_tools(self, seq_id: int, platform: str, testing_path: Path) -> Dict[str, Any]:
        """Set up platform-specific automation tools"""
        logger.info(f"🟡 [Agent3] Setting up automation tools for platform: {platform}")
        
        try:
            venv_path = testing_path / "venv"
            python_exe = self._get_venv_python(venv_path)
            
            tools_setup = {}
            
            if platform.lower() in ["mobile", "android", "ios"]:
                # Setup Appium
                appium_result = await self._setup_appium(seq_id, python_exe, testing_path)
                tools_setup["appium"] = appium_result
                
                await self.db_manager.update_testing_environment(
                    seq_id=seq_id,
                    appium_server_running=appium_result.get('server_ready', False)
                )
                
            elif platform.lower() in ["web", "browser"]:
                # Setup Playwright
                playwright_result = await self._setup_playwright(seq_id, python_exe, testing_path)
                tools_setup["playwright"] = playwright_result
                
                await self.db_manager.update_testing_environment(
                    seq_id=seq_id,
                    playwright_installed=playwright_result.get('installed', False)
                )
            
            logger.info(f"🟡 [Agent3] ✅ Automation tools setup completed")
            
            return {
                "success": True,
                "platform": platform,
                "tools_setup": tools_setup
            }
            
        except Exception as e:
            warning_msg = f"Automation tools setup had issues: {str(e)}"
            logger.warning(f"🟡 [Agent3] {warning_msg}")
            
            return {
                "success": False,
                "warning": warning_msg,
                "platform": platform
            }
    
    async def _setup_appium(self, seq_id: int, python_exe: Path, testing_path: Path) -> Dict[str, Any]:
        """Set up Appium for mobile automation"""
        logger.info(f"🟡 [Agent3] Setting up Appium...")
        
        try:
            # Check if Appium server is available (basic check)
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 4723))
            sock.close()
            
            if result == 0:
                logger.info(f"🟡 [Agent3] ✅ Appium server detected on localhost:4723")
                return {
                    "installed": True,
                    "server_ready": True,
                    "server_url": "http://localhost:4723"
                }
            else:
                logger.warning(f"🟡 [Agent3] ⚠️ Appium server not running on localhost:4723")
                
                # Create appium server logs directory
                appium_logs_path = testing_path / "appium_server_logs"
                appium_logs_path.mkdir(exist_ok=True)
                
                return {
                    "installed": False,
                    "server_ready": False,
                    "warning": "Appium server not detected - manual start required",
                    "logs_path": str(appium_logs_path)
                }
                
        except Exception as e:
            logger.warning(f"🟡 [Agent3] Appium setup check failed: {str(e)}")
            return {
                "installed": False,
                "server_ready": False,
                "error": str(e)
            }
    
    async def _setup_playwright(self, seq_id: int, python_exe: Path, testing_path: Path) -> Dict[str, Any]:
        """Set up Playwright for web automation"""
        logger.info(f"🟡 [Agent3] Setting up Playwright...")
        
        try:
            # Install Playwright browsers
            install_cmd = [str(python_exe), "-m", "playwright", "install"]
            
            logger.info(f"🟡 [Agent3] Installing Playwright browsers...")
            
            process = await asyncio.create_subprocess_exec(
                *install_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(testing_path)
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)  # 5 minute timeout
            
            if process.returncode == 0:
                logger.info(f"🟡 [Agent3] ✅ Playwright browsers installed")
                return {
                    "installed": True,
                    "browsers_installed": True,
                    "install_output": stdout.decode() if stdout else ""
                }
            else:
                error_output = stderr.decode() if stderr else "Unknown error"
                logger.warning(f"🟡 [Agent3] Playwright browser install warning: {error_output}")
                return {
                    "installed": False,
                    "browsers_installed": False,
                    "warning": error_output
                }
                
        except asyncio.TimeoutError:
            logger.warning(f"🟡 [Agent3] Playwright browser installation timed out")
            return {
                "installed": False,
                "browsers_installed": False,
                "warning": "Installation timed out - may need manual setup"
            }
        except Exception as e:
            logger.warning(f"🟡 [Agent3] Playwright setup failed: {str(e)}")
            return {
                "installed": False,
                "browsers_installed": False,
                "error": str(e)
            }
    
    async def _copy_script_from_agent2(self, seq_id: int, testing_path: Path, base_path: Path) -> Dict[str, Any]:
        """Copy automation script from agent2 to testing environment"""
        logger.info(f"🟡 [Agent3] Copying script from Agent 2...")
        
        try:
            agent2_path = base_path / "agent2"
            
            # Find the latest script version
            latest_version = await self.db_manager.get_latest_script_version(seq_id)
            
            if latest_version == 1:
                script_name = "script.py"
            else:
                script_name = f"update_{latest_version - 1}.py"
            
            source_script = agent2_path / script_name
            target_script = testing_path / "script.py"  # Always copy as script.py for execution
            
            if not source_script.exists():
                raise Exception(f"Script {script_name} not found in agent2 folder")
            
            shutil.copy2(source_script, target_script)
            
            # Also copy OCR logs directory structure
            ocr_source = agent2_path / "ocr_logs"
            ocr_target = testing_path / "ocr_logs"
            
            if ocr_source.exists():
                if ocr_target.exists():
                    shutil.rmtree(ocr_target)
                shutil.copytree(ocr_source, ocr_target)
                logger.info(f"🟡 [Agent3] Copied OCR logs structure")
            
            logger.info(f"🟡 [Agent3] ✅ Copied {script_name} to testing environment")
            
            return {
                "success": True,
                "source_script": str(source_script),
                "target_script": str(target_script),
                "script_version": latest_version,
                "ocr_logs_copied": ocr_source.exists()
            }
            
        except Exception as e:
            error_msg = f"Script copy failed: {str(e)}"
            logger.error(f"🔴 [Agent3] {error_msg}")
            
            return {
                "success": False,
                "error": error_msg
            }
    
    async def _execute_tests_with_validation(self, seq_id: int, testing_path: Path, platform: str) -> Dict[str, Any]:
        """Execute tests with OCR validation and Agent 2 communication"""
        logger.info(f"🟡 [Agent3] Starting test execution with validation...")
        
        test_results = {
            "total_attempts": 0,
            "successful_attempts": 0,
            "failed_attempts": 0,
            "agent2_collaborations": 0,
            "test_executions": [],
            "overall_success": False
        }
        
        venv_path = testing_path / "venv"
        python_exe = self._get_venv_python(venv_path)
        script_path = testing_path / "script.py"
        
        for attempt in range(1, self.max_test_attempts + 1):
            logger.info(f"\\n🟡 [Agent3] ========== TEST ATTEMPT {attempt} ==========")
            
            test_results["total_attempts"] += 1
            
            # Execute the script
            execution_result = await self._execute_single_test(
                seq_id, attempt, python_exe, script_path, testing_path
            )
            
            test_results["test_executions"].append(execution_result)
            
            logger.info(f"🟡 [Agent3] Attempt {attempt} result: {'SUCCESS' if execution_result['success'] else 'FAILED'}")
            logger.info(f"🟡 [Agent3] Duration: {execution_result['duration']:.2f} seconds")
            
            if execution_result['success']:
                test_results["successful_attempts"] += 1
                test_results["overall_success"] = True
                logger.info(f"🟡 [Agent3] ✅ Test execution successful!")
                break
            else:
                test_results["failed_attempts"] += 1
                
                # If not the last attempt, communicate with Agent 2 for improvements
                if attempt < self.max_test_attempts:
                    logger.info(f"🟡 [Agent3] Test failed, requesting improvements from Agent 2...")
                    
                    feedback_result = await self._communicate_with_agent2(
                        seq_id, execution_result, attempt
                    )
                    
                    if feedback_result['success']:
                        test_results["agent2_collaborations"] += 1
                        logger.info(f"🟡 [Agent3] ✅ Received improved script from Agent 2")
                        
                        # Copy the new script for next attempt
                        await self._update_test_script(seq_id, testing_path)
                        
                        # Small delay before retry
                        await asyncio.sleep(3)
                    else:
                        logger.warning(f"🟡 [Agent3] ⚠️ Agent 2 collaboration failed")
        
        if not test_results["overall_success"]:
            logger.info(f"🟡 [Agent3] ❌ ALL {self.max_test_attempts} ATTEMPTS FAILED")
        
        # Save final test results
        await self._save_test_results_summary(seq_id, testing_path, test_results)
        
        return test_results
    
    async def _execute_single_test(self, seq_id: int, attempt: int, python_exe: Path, 
                                  script_path: Path, testing_path: Path) -> Dict[str, Any]:
        """Execute a single test attempt"""
        start_time = time.time()
        
        logger.info(f"🟡 [Agent3] Executing script: {script_path}")
        
        try:
            # Execute the script
            process = await asyncio.create_subprocess_exec(
                str(python_exe), str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(testing_path)
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)  # 2 minute timeout
                duration = time.time() - start_time
                
                success = process.returncode == 0
                
                # Save execution result to database
                exec_id = await self.db_manager.save_test_execution(
                    seq_id=seq_id,
                    script_version=await self.db_manager.get_latest_script_version(seq_id),
                    execution_attempt=attempt,
                    success=success,
                    execution_output=stdout.decode() if stdout else "",
                    error_details=stderr.decode() if stderr else "",
                    execution_duration=duration
                )
                
                # Analyze OCR results if available
                ocr_analysis = await self._analyze_ocr_results(testing_path)
                
                return {
                    "success": success,
                    "attempt": attempt,
                    "duration": duration,
                    "return_code": process.returncode,
                    "stdout": stdout.decode() if stdout else "",
                    "stderr": stderr.decode() if stderr else "",
                    "exec_id": exec_id,
                    "ocr_analysis": ocr_analysis
                }
                
            except asyncio.TimeoutError:
                process.kill()
                duration = time.time() - start_time
                
                await self.db_manager.save_test_execution(
                    seq_id=seq_id,
                    script_version=await self.db_manager.get_latest_script_version(seq_id),
                    execution_attempt=attempt,
                    success=False,
                    error_details="Script execution timed out after 120 seconds",
                    execution_duration=duration
                )
                
                return {
                    "success": False,
                    "attempt": attempt,
                    "duration": duration,
                    "error": "Timeout after 120 seconds",
                    "timeout": True
                }
                
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            await self.db_manager.save_test_execution(
                seq_id=seq_id,
                script_version=await self.db_manager.get_latest_script_version(seq_id),
                execution_attempt=attempt,
                success=False,
                error_details=error_msg,
                execution_duration=duration
            )
            
            return {
                "success": False,
                "attempt": attempt,
                "duration": duration,
                "error": error_msg,
                "exception": True
            }
    
    async def _analyze_ocr_results(self, testing_path: Path) -> Dict[str, Any]:
        """Analyze OCR results from test execution"""
        ocr_logs_path = testing_path / "ocr_logs"
        
        if not ocr_logs_path.exists():
            return {"ocr_available": False}
        
        analysis = {
            "ocr_available": True,
            "screenshot_count": 0,
            "ocr_text_files": 0,
            "validation_results": []
        }
        
        # Count OCR files
        for file_path in ocr_logs_path.iterdir():
            if file_path.suffix == '.png':
                analysis["screenshot_count"] += 1
            elif file_path.suffix == '.txt':
                analysis["ocr_text_files"] += 1
        
        logger.info(f"🟡 [Agent3] OCR Analysis: {analysis['screenshot_count']} screenshots, {analysis['ocr_text_files']} text files")
        
        return analysis
    
    async def _communicate_with_agent2(self, seq_id: int, execution_result: Dict, attempt: int) -> Dict[str, Any]:
        """Communicate with Agent 2 to request script improvements"""
        try:
            # Analyze execution failure
            issues = self._analyze_execution_issues(execution_result)
            suggestions = self._generate_improvement_suggestions(execution_result, attempt)
            
            feedback_data = {
                "attempt": attempt,
                "issues": issues,
                "suggestions": suggestions,
                "execution_details": {
                    "return_code": execution_result.get('return_code'),
                    "duration": execution_result.get('duration'),
                    "timeout": execution_result.get('timeout', False),
                    "exception": execution_result.get('exception', False)
                },
                "error_output": execution_result.get('stderr', ''),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Import Agent 2 to request improvements
            from app.agents.updated_agent2_code import UpdatedAgent2_CodeGenerator
            
            agent2 = UpdatedAgent2_CodeGenerator()
            await agent2.initialize()
            
            # Request improvements
            improvement_result = await agent2.handle_agent3_feedback(seq_id, feedback_data)
            
            return improvement_result
            
        except Exception as e:
            logger.error(f"🟡 [Agent3] Communication with Agent 2 failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _analyze_execution_issues(self, execution_result: Dict) -> List[str]:
        """Analyze execution issues and identify problems"""
        issues = []
        
        stderr = execution_result.get('stderr', '').lower()
        stdout = execution_result.get('stdout', '').lower()
        
        # Common error patterns
        if execution_result.get('timeout'):
            issues.append("Script execution timed out - may need better wait conditions")
        
        if 'modulenotfounderror' in stderr:
            issues.append("Missing required modules - dependencies may not be installed correctly")
        
        if 'connection refused' in stderr or 'connection failed' in stderr:
            issues.append("Connection issues - automation server may not be running")
        
        if 'element not found' in stderr or 'no such element' in stderr:
            issues.append("UI elements not found - selectors may be incorrect")
        
        if 'timeout' in stderr and not execution_result.get('timeout'):
            issues.append("Element wait timeout - need longer wait times or better element detection")
        
        if execution_result.get('return_code', 0) != 0 and not issues:
            issues.append("Script execution failed - check automation logic and error handling")
        
        return issues
    
    def _generate_improvement_suggestions(self, execution_result: Dict, attempt: int) -> List[str]:
        """Generate improvement suggestions for Agent 2"""
        suggestions = [
            "Add explicit wait conditions before interacting with elements",
            "Implement retry logic for failed operations",
            "Add better error handling and logging",
            "Include element availability checks before actions"
        ]
        
        if attempt == 1:
            suggestions.extend([
                "Add longer timeout values for element detection",
                "Include page/app load wait conditions"
            ])
        elif attempt == 2:
            suggestions.extend([
                "Try alternative element selection strategies",
                "Add recovery actions for common failure scenarios"
            ])
        elif attempt == 3:
            suggestions.extend([
                "Implement graceful fallback mechanisms",
                "Add comprehensive debug logging"
            ])
        
        return suggestions
    
    async def _update_test_script(self, seq_id: int, testing_path: Path):
        """Update test script with latest version from Agent 2"""
        try:
            task_info = await self.db_manager.get_task_info(seq_id)
            base_path = Path(task_info['base_path'])
            agent2_path = base_path / "agent2"
            
            # Get latest script version
            latest_version = await self.db_manager.get_latest_script_version(seq_id)
            
            if latest_version > 1:
                source_script = agent2_path / f"update_{latest_version - 1}.py"
                target_script = testing_path / "script.py"
                
                if source_script.exists():
                    shutil.copy2(source_script, target_script)
                    logger.info(f"🟡 [Agent3] Updated test script to version {latest_version}")
                
        except Exception as e:
            logger.warning(f"🟡 [Agent3] Failed to update test script: {str(e)}")
    
    async def _save_test_results_summary(self, seq_id: int, testing_path: Path, test_results: Dict):
        """Save test results summary to file"""
        try:
            results_path = testing_path / "test_results_summary.json"
            
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "seq_id": seq_id,
                    "agent": self.agent_name,
                    "test_summary": test_results,
                    "generated_at": datetime.utcnow().isoformat()
                }, f, indent=2)
            
            logger.info(f"🟡 [Agent3] ✅ Test results summary saved: {results_path}")
            
        except Exception as e:
            logger.warning(f"🟡 [Agent3] Failed to save test results summary: {str(e)}")
    
    def _get_venv_python(self, venv_path: Path) -> Path:
        """Get Python executable path for virtual environment"""
        if platform.system() == "Windows":
            return venv_path / "Scripts" / "python.exe"
        else:
            return venv_path / "bin" / "python"