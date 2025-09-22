"""
Terminal Manager with Core Terminal Functionality
Maintains all subprocess and virtual environment functionality while integrating with LangGraph workflow
"""
import asyncio
import subprocess
import logging
import os
import platform
import time
import sys
import shlex
import shutil
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

def open_new_terminal_cmd_windows(command: str = None) -> Dict[str, Any]:
    """
    Open new CMD terminal on Windows with proper command execution
    Based on research: Use 'start "Title" cmd /k "command"' for Windows
    """
    try:
        plat = sys.platform
        if plat.startswith("win"):
            # ALWAYS use CMD on Windows - no PowerShell issues
            if command:
                # Use start with title and /k to keep window open
                # Escape quotes properly for Windows CMD
                escaped_command = command.replace('"', '""')  # Double quotes for CMD
                cmd_string = f'start "Automation Task" cmd /k "{escaped_command}"'
                logger.info(f"🔧 Opening CMD window with command: {cmd_string}")
                process = subprocess.Popen(cmd_string, shell=True)
                return {
                    "success": True,
                    "method": "windows_cmd_start",
                    "terminal_type": "cmd",
                    "pid": process.pid if process else None,
                    "process": process,
                    "command": cmd_string
                }
            else:
                process = subprocess.Popen('start "Terminal" cmd', shell=True)
                return {
                    "success": True,
                    "method": "windows_cmd_blank",
                    "terminal_type": "cmd",
                    "pid": process.pid if process else None,
                    "process": process
                }
        
        # macOS
        elif plat == "darwin":
            if command:
                safe_cmd = command.replace('"', '\\"')
                applescript = f'tell application "Terminal" to do script "{safe_cmd}"'
                process = subprocess.Popen(["osascript", "-e", applescript])
            else:
                process = subprocess.Popen(["open", "-a", "Terminal"])
            return {
                "success": True,
                "method": "macos_terminal",
                "terminal_type": "bash",
                "pid": process.pid,
                "process": process
            }
        
        # Linux
        else:
            terminals = [
                ("gnome-terminal", ["gnome-terminal", "--", "bash", "-c", '{cmd}; exec bash']),
                ("konsole", ["konsole", "-e", "bash", "-c", '{cmd}; exec bash']),
                ("xterm", ["xterm", "-hold", "-e", "{cmd}"]),
            ]
            
            if command:
                for name, template in terminals:
                    if shutil.which(name):
                        cmdline = " ".join(template).format(cmd=shlex.quote(command))
                        process = subprocess.Popen(cmdline, shell=True)
                        return {
                            "success": True,
                            "method": f"linux_{name}",
                            "terminal_type": "bash",
                            "pid": process.pid,
                            "process": process
                        }
            
            # Fallback to first available terminal
            for name, _ in terminals:
                if shutil.which(name):
                    process = subprocess.Popen([name])
                    return {
                        "success": True,
                        "method": f"linux_{name}_blank",
                        "terminal_type": "bash",
                        "pid": process.pid,
                        "process": process
                    }
            
            raise RuntimeError("No terminal emulator found")
            
    except Exception as e:
        logger.error(f"❌ Failed to open terminal: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "method": "failed"
        }


class TerminalManager:
    """Production Terminal Manager with subprocess virtual environment and terminal functionality"""
    
    def __init__(self):
        self.active_processes: List[subprocess.Popen] = []
        self.active_terminals: List[Dict[str, Any]] = []
        self.system = platform.system()
        self.appium_process = None
        logger.info(f"🔧 Terminal Manager initialized for {self.system}")

    def create_absolute_path(self, path: str) -> str:
        """Create absolute path and ensure it's properly formatted"""
        abs_path = os.path.abspath(path)
        # Convert forward slashes to backslashes on Windows
        if self.system == "Windows":
            abs_path = abs_path.replace('/', '\\')
        return abs_path

    def fix_python_executable_path(self, python_path: str) -> str:
        """
        Remove extra quotes and ensure valid Python executable path
        Based on research: Windows path issues with nested quotes
        """
        # Remove surrounding quotes if they exist
        while python_path.startswith('"') and python_path.endswith('"'):
            python_path = python_path[1:-1]
        
        # Make absolute path
        python_path = self.create_absolute_path(python_path)
        
        # Verify the path exists
        if not os.path.exists(python_path):
            logger.warning(f"⚠️ Python path not found: {python_path}, using sys.executable")
            python_path = sys.executable
        
        logger.info(f"🔧 Fixed Python path: {python_path}")
        return python_path

    def build_cmd_command_chain(self, commands: List[str]) -> str:
        """
        Build command chain for Windows CMD with proper && syntax
        Based on research: CMD uses &&, PowerShell uses ;
        """
        if self.system == "Windows":
            # Windows CMD uses && for command chaining
            return " && ".join(commands)
        else:
            # Unix/Linux uses && for command chaining
            return " && ".join(commands)

    def get_venv_activation_command(self, venv_path: Path) -> str:
        """
        Get proper virtual environment activation command
        Based on research: activate.bat for CMD, Activate.ps1 for PowerShell
        """
        if self.system == "Windows":
            # Use activate.bat for CMD (not Activate.ps1 for PowerShell)
            activate_script = venv_path / "Scripts" / "activate.bat"
            return f'"{activate_script}"'
        else:
            activate_script = venv_path / "bin" / "activate"
            return f'source "{activate_script}"'

    def create_virtual_environment(self, venv_path: str, python_executable: Optional[str] = None) -> Dict[str, Any]:
        """
        FIXED: Create virtual environment with proper Windows execution
        Uses direct subprocess.run instead of CMD string parsing
        """
        try:
            # Fix Python executable path
            python_exec = python_executable or sys.executable
            python_exec = self.fix_python_executable_path(python_exec)
            
            # Create absolute venv path
            venv_abs_path = self.create_absolute_path(venv_path)
            
            logger.info(f"🔧 Creating virtual environment: {venv_abs_path}")
            logger.info(f"🔧 Using Python: {python_exec}")
            
            # FIXED: Use direct argument list instead of CMD string
            cmd_args = [python_exec, "-m", "venv", venv_abs_path, "--clear", "--copies"]
            
            logger.info(f"🔧 Executing venv command: {' '.join(cmd_args)}")
            
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                # Determine paths in virtual environment
                venv_path_obj = Path(venv_abs_path)
                if self.system == "Windows":
                    venv_python = venv_path_obj / "Scripts" / "python.exe"
                    venv_pip = venv_path_obj / "Scripts" / "pip.exe"
                    venv_activate = venv_path_obj / "Scripts" / "activate.bat"
                else:
                    venv_python = venv_path_obj / "bin" / "python"
                    venv_pip = venv_path_obj / "bin" / "pip"
                    venv_activate = venv_path_obj / "bin" / "activate"
                
                # Verify the executables exist
                if not venv_python.exists():
                    raise Exception(f"Virtual environment Python not found: {venv_python}")
                
                logger.info(f"✅ Virtual environment created: {venv_abs_path}")
                logger.info(f"✅ Python executable: {venv_python}")
                
                return {
                    "success": True,
                    "venv_path": venv_abs_path,
                    "python_executable": str(venv_python),
                    "pip_executable": str(venv_pip),
                    "activate_script": str(venv_activate),
                    "output": result.stdout
                }
            else:
                logger.error(f"❌ Virtual environment creation failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr or "Virtual environment creation failed",
                    "command": " ".join(cmd_args)
                }
                
        except Exception as e:
            logger.error(f"❌ Virtual environment creation failed: {str(e)}")
            return {"success": False, "error": str(e), "venv_path": venv_path}

    def execute_command_sync(self, command: str, cwd: Optional[str] = None, timeout: int = 60) -> Dict[str, Any]:
        """
        Execute command with proper shell handling
        Always uses CMD on Windows to avoid PowerShell issues
        """
        try:
            logger.info(f"🔧 Executing command: {command}")
            
            if cwd:
                cwd = self.create_absolute_path(cwd)
                logger.info(f"🔧 Working directory: {cwd}")
            
            # Always use CMD on Windows
            if self.system == "Windows":
                shell_command = ["cmd", "/c", command]
            else:
                shell_command = ["bash", "-c", command]
            
            result = subprocess.run(
                shell_command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Command timed out: {command}")
            return {"success": False, "error": "Command timed out", "command": command}
        except Exception as e:
            logger.error(f"❌ Command execution failed: {str(e)}")
            return {"success": False, "error": str(e), "command": command}

    def execute_mobile_two_terminal_flow_fixed(
        self,
        working_directory: Path,
        venv_path: Path,
        requirements_file: Path,
        script_path: Path
    ) -> Dict[str, Any]:
        """
        FIXED: Execute mobile automation with two CMD terminals
        Based on research: Terminal 1 for deps, Terminal 2 for Appium + script
        """
        try:
            logger.info("🔧 Starting mobile two-terminal flow...")
            
            # Convert all paths to absolute paths
            working_dir_abs = self.create_absolute_path(str(working_directory))
            venv_path_abs = self.create_absolute_path(str(venv_path))
            requirements_abs = self.create_absolute_path(str(requirements_file))
            script_abs = self.create_absolute_path(str(script_path))
            
            # Get activation command
            venv_activate = self.get_venv_activation_command(Path(venv_path_abs))
            
            # TERMINAL 1: Dependencies Installation
            logger.info("🔧 Opening Terminal 1: Mobile Dependencies...")
            
            deps_commands = [
                f'cd /d "{working_dir_abs}"' if self.system == "Windows" else f'cd "{working_dir_abs}"',
                venv_activate,
                "echo [MOBILE-DEPS] Installing mobile automation dependencies...",
                f'pip install -r "{requirements_abs}"',
                "echo [MOBILE-DEPS] Dependencies installation completed!",
                "echo [MOBILE-DEPS] Press any key to continue...",
                "pause" if self.system == "Windows" else "read -p 'Press Enter to continue...'"
            ]
            
            deps_command = self.build_cmd_command_chain(deps_commands)
            deps_result = open_new_terminal_cmd_windows(deps_command)
            
            if not deps_result["success"]:
                raise Exception(f"Failed to open dependencies terminal: {deps_result.get('error', 'Unknown error')}")
            
            self.active_terminals.append(deps_result)
            logger.info("✅ Mobile dependencies terminal opened successfully")
            
            # Wait for dependencies terminal to start
            time.sleep(3)
            
            # TERMINAL 2: Appium + Script Execution
            logger.info("🔧 Opening Terminal 2: Appium + Mobile Script...")
            
            appium_commands = [
                f'cd /d "{working_dir_abs}"' if self.system == "Windows" else f'cd "{working_dir_abs}"',
                venv_activate,
                "echo [MOBILE-APPIUM] Starting Appium server...",
                "start /b appium --port 4723 --log-level info" if self.system == "Windows" else "appium --port 4723 --log-level info &",
                "timeout /t 8" if self.system == "Windows" else "sleep 8",
                "echo [MOBILE-APPIUM] Appium server started, running mobile automation script...",
                f'python "{script_abs}"',
                "echo [MOBILE-APPIUM] Mobile automation completed!",
                "echo [MOBILE-APPIUM] Press any key to continue...",
                "pause" if self.system == "Windows" else "read -p 'Press Enter to continue...'"
            ]
            
            appium_command = self.build_cmd_command_chain(appium_commands)
            appium_result = open_new_terminal_cmd_windows(appium_command)
            
            if not appium_result["success"]:
                raise Exception(f"Failed to open Appium terminal: {appium_result.get('error', 'Unknown error')}")
            
            self.active_terminals.append(appium_result)
            logger.info("✅ Mobile Appium + script terminal opened successfully")
            
            return {
                "success": True,
                "environment_ready": True,  # FIXED: Add this key
                "terminals_opened": 2,
                "platform_type": "mobile",
                "deps_terminal": deps_result,
                "appium_terminal": appium_result,
                "working_directory": working_dir_abs,
                "venv_path": venv_path_abs,
                "approach": "mobile_two_terminal"
            }
            
        except Exception as e:
            logger.error(f"❌ Mobile two-terminal flow failed: {str(e)}")
            return {
                "success": False,
                "environment_ready": False,  # FIXED: Add this key
                "error": str(e),
                "terminals_opened": len(self.active_terminals),
                "platform_type": "mobile",
                "approach": "mobile_two_terminal"
            }

    def execute_web_two_terminal_flow(
        self,
        working_directory: Path,
        venv_path: Path,
        requirements_file: Path,
        script_path: Path
    ) -> Dict[str, Any]:
        """
        Execute web automation with two CMD terminals
        Based on research: Terminal 1 for deps + Playwright, Terminal 2 for script
        """
        try:
            logger.info("🔧 Starting web two-terminal flow...")
            
            # Convert all paths to absolute paths
            working_dir_abs = self.create_absolute_path(str(working_directory))
            venv_path_abs = self.create_absolute_path(str(venv_path))
            requirements_abs = self.create_absolute_path(str(requirements_file))
            script_abs = self.create_absolute_path(str(script_path))
            
            # Get activation command
            venv_activate = self.get_venv_activation_command(Path(venv_path_abs))
            
            # TERMINAL 1: Dependencies + Playwright Installation
            logger.info("🔧 Opening Terminal 1: Web Dependencies + Playwright...")
            
            deps_commands = [
                f'cd /d "{working_dir_abs}"' if self.system == "Windows" else f'cd "{working_dir_abs}"',
                venv_activate,
                "echo [WEB-DEPS] Installing web automation dependencies...",
                f'pip install -r "{requirements_abs}"',
                "echo [WEB-DEPS] Installing Playwright browsers...",
                "playwright install",
                "echo [WEB-DEPS] Web automation setup completed!",
                "echo [WEB-DEPS] Press any key to continue...",
                "pause" if self.system == "Windows" else "read -p 'Press Enter to continue...'"
            ]
            
            deps_command = self.build_cmd_command_chain(deps_commands)
            deps_result = open_new_terminal_cmd_windows(deps_command)
            
            if not deps_result["success"]:
                raise Exception(f"Failed to open dependencies terminal: {deps_result.get('error', 'Unknown error')}")
            
            self.active_terminals.append(deps_result)
            logger.info("✅ Web dependencies + Playwright terminal opened successfully")
            
            # Wait for dependencies terminal to start
            time.sleep(3)
            
            # TERMINAL 2: Script Execution
            logger.info("🔧 Opening Terminal 2: Web Script Execution...")
            
            script_commands = [
                f'cd /d "{working_dir_abs}"' if self.system == "Windows" else f'cd "{working_dir_abs}"',
                venv_activate,
                "echo [WEB-SCRIPT] Running web automation script...",
                f'python "{script_abs}"',
                "echo [WEB-SCRIPT] Web automation completed!",
                "echo [WEB-SCRIPT] Press any key to continue...",
                "pause" if self.system == "Windows" else "read -p 'Press Enter to continue...'"
            ]
            
            script_command = self.build_cmd_command_chain(script_commands)
            script_result = open_new_terminal_cmd_windows(script_command)
            
            if not script_result["success"]:
                raise Exception(f"Failed to open script terminal: {script_result.get('error', 'Unknown error')}")
            
            self.active_terminals.append(script_result)
            logger.info("✅ Web script execution terminal opened successfully")
            
            return {
                "success": True,
                "environment_ready": True,
                "terminals_opened": 2,
                "platform_type": "web",
                "deps_terminal": deps_result,
                "script_terminal": script_result,
                "working_directory": working_dir_abs,
                "venv_path": venv_path_abs,
                "approach": "web_two_terminal"
            }
            
        except Exception as e:
            logger.error(f"❌ Web two-terminal flow failed: {str(e)}")
            return {
                "success": False,
                "environment_ready": False,
                "error": str(e),
                "terminals_opened": len(self.active_terminals),
                "platform_type": "web",
                "approach": "web_two_terminal"
            }

    def execute_single_terminal_fallback(
        self,
        script_path: str,
        working_directory: Optional[str] = None,
        python_executable: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Single terminal execution as fallback
        Uses proper CMD window with absolute paths
        """
        try:
            logger.info(f"🔧 Executing script in single terminal: {script_path}")
            
            # Fix paths
            python_exec = python_executable or sys.executable
            python_exec = self.fix_python_executable_path(python_exec)
            script_abs = self.create_absolute_path(script_path)
            
            if working_directory:
                working_dir_abs = self.create_absolute_path(working_directory)
                commands = [
                    f'cd /d "{working_dir_abs}"' if self.system == "Windows" else f'cd "{working_dir_abs}"',
                    f'"{python_exec}" "{script_abs}"',
                    "echo [SINGLE] Script execution completed!",
                    "pause" if self.system == "Windows" else "read -p 'Press Enter to continue...'"
                ]
            else:
                commands = [
                    f'"{python_exec}" "{script_abs}"',
                    "echo [SINGLE] Script execution completed!",
                    "pause" if self.system == "Windows" else "read -p 'Press Enter to continue...'"
                ]
            
            command = self.build_cmd_command_chain(commands)
            terminal_result = open_new_terminal_cmd_windows(command)
            
            if terminal_result["success"]:
                self.active_terminals.append(terminal_result)
                logger.info(f"✅ Single terminal script started: {terminal_result['method']}")
                return {
                    "success": True,
                    "terminal_info": terminal_result,
                    "script_path": script_abs,
                    "working_directory": working_directory,
                    "python_executable": python_exec,
                    "terminals_opened": 1
                }
            else:
                logger.error(f"❌ Failed to open terminal: {terminal_result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "error": terminal_result.get("error", "Terminal creation failed"),
                    "script_path": script_abs,
                    "terminals_opened": 0
                }
                
        except Exception as e:
            logger.error(f"❌ Single terminal execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "script_path": script_path,
                "terminals_opened": 0
            }

    def start_appium_server_background(self, port: int = 4723) -> Dict[str, Any]:
        """Start Appium server in background (if needed separately)"""
        try:
            status = self.get_appium_server_status(port)
            if status.get("running", False):
                logger.info(f"✅ Appium server already running on port {port}")
                return {"success": True, "message": f"Appium server already running on port {port}", "port": port}
            
            logger.info(f"🔧 Starting Appium server on port {port}...")
            
            if self.system == "Windows":
                appium_command = f"start /b appium --port {port} --log-level info"
            else:
                appium_command = f"appium --port {port} --log-level info &"
            
            result = self.start_process_detached(appium_command)
            
            if result["success"]:
                self.appium_process = result["process"]
                time.sleep(5)  # Wait for server to start
                
                # Verify server is running
                status = self.get_appium_server_status(port)
                if status.get("running", False):
                    logger.info(f"✅ Appium server started successfully on port {port}")
                    return {"success": True, "pid": result["pid"], "port": port, "status": status}
                else:
                    logger.error("❌ Appium server failed to start properly")
                    return {"success": False, "error": "Server failed to start", "port": port}
            else:
                logger.error(f"❌ Failed to start Appium server: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Appium server startup failed: {str(e)}")
            return {"success": False, "error": str(e), "port": port}

    def start_process_detached(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """Start a detached background process"""
        try:
            logger.info(f"🔧 Starting detached process: {command}")
            
            if self.system == "Windows":
                process = subprocess.Popen(
                    command, shell=True, cwd=cwd,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                process = subprocess.Popen(
                    command, shell=True, cwd=cwd,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    start_new_session=True
                )
            
            self.active_processes.append(process)
            logger.info(f"✅ Process started with PID: {process.pid}")
            
            return {"success": True, "pid": process.pid, "process": process, "command": command}
            
        except Exception as e:
            logger.error(f"❌ Failed to start detached process: {str(e)}")
            return {"success": False, "error": str(e), "command": command}

    def get_appium_server_status(self, port: int = 4723) -> Dict[str, Any]:
        """Check if Appium server is running"""
        try:
            import requests
            resp = requests.get(f"http://127.0.0.1:{port}/status", timeout=5)
            if resp.status_code == 200:
                return {"running": True, "status": "ready", "port": port, "response": resp.json()}
            else:
                return {"running": False, "status": "not_ready", "port": port, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"running": False, "status": "offline", "port": port, "error": str(e)}

    def stop_appium_server(self) -> Dict[str, Any]:
        """Stop the Appium server"""
        try:
            if self.appium_process and self.appium_process.poll() is None:
                logger.info("🔧 Stopping Appium server...")
                self.appium_process.terminate()
                try:
                    self.appium_process.wait(timeout=10)
                    logger.info("✅ Appium server stopped gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning("⚠️ Force killing Appium server...")
                    self.appium_process.kill()
                    self.appium_process.wait()
                    logger.info("✅ Appium server force stopped")
                
                self.appium_process = None
                return {"success": True, "message": "Appium server stopped"}
            else:
                logger.info("ℹ️ Appium server was not running")
                return {"success": True, "message": "Appium server was not running"}
                
        except Exception as e:
            logger.error(f"❌ Failed to stop Appium server: {str(e)}")
            return {"success": False, "error": str(e)}

    def cleanup_processes(self):
        """Clean up all active processes and terminals"""
        logger.info("🔧 Cleaning up terminal processes...")
        
        try:
            # Stop Appium server if running
            if self.appium_process:
                self.stop_appium_server()
            
            # Terminate all active processes
            for process in self.active_processes:
                try:
                    if process.poll() is None:
                        logger.info(f"🔧 Terminating process PID: {process.pid}")
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            logger.warning(f"⚠️ Force killing process PID: {process.pid}")
                            process.kill()
                            process.wait()
                except Exception as e:
                    logger.error(f"❌ Error terminating process {process.pid}: {str(e)}")
            
            self.active_processes.clear()
            self.active_terminals.clear()
            
            logger.info("✅ Process cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Process cleanup failed: {str(e)}")

    def get_process_status(self) -> Dict[str, Any]:
        """Get status of all active processes and terminals"""
        return {
            "active_processes": len(self.active_processes),
            "active_terminals": len(self.active_terminals),
            "appium_running": self.appium_process is not None and self.appium_process.poll() is None,
            "system": self.system,
            "terminal_methods": [t.get("method", "unknown") for t in self.active_terminals],
            "approach": "production_cmd_based"
        }

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "system": self.system,
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0],
            "machine": platform.machine(),
            "active_processes": len(self.active_processes),
            "active_terminals": len(self.active_terminals),
            "appium_running": self.appium_process is not None and self.appium_process.poll() is None,
            "terminal_manager": "production_cmd_based"
        }


# Global instance
_terminal_manager = None

def get_terminal_manager() -> TerminalManager:
    """Get global terminal manager instance"""
    global _terminal_manager
    if _terminal_manager is None:
        _terminal_manager = TerminalManager()
    return _terminal_manager

# Alias for backward compatibility
open_new_terminal = open_new_terminal_cmd_windows

if __name__ == "__main__":
    # Test the terminal manager
    tm = TerminalManager()
    print("🧪 Testing Terminal Manager...")
    
    # Test path fixing
    test_path = '"D:\\SearchLook\\aisa-agent-framework-v1\\venv\\Scripts\\python.exe"'
    fixed_path = tm.fix_python_executable_path(test_path)
    print(f"Fixed Python path: {fixed_path}")
    
    # Test command building
    commands = ["echo [TEST] Hello", "echo [TEST] World", "pause"]
    built_command = tm.build_cmd_command_chain(commands)
    print(f"Built command: {built_command}")
    
    # Test venv creation
    test_venv = "test_venv_temp"
    venv_result = tm.create_virtual_environment(test_venv)
    print(f"Venv creation result: {venv_result['success']}")
    
    # Clean up test venv
    if venv_result["success"] and os.path.exists(test_venv):
        import shutil
        shutil.rmtree(test_venv)
    
    print("🧪 Terminal Manager test completed")