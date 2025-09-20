"""
COMPLETELY FIXED Terminal Manager - Proper Cross-Platform Terminal Handling
Fixes Python path quotes, terminal syntax, and implements two-terminal flow
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

def open_new_terminal(command: str = None, use_cmd_on_windows: bool = True) -> Dict[str, Any]:
    """
    Open a new terminal window with FIXED command syntax.
    For Windows: Always use CMD to avoid PowerShell && syntax issues
    """
    try:
        plat = sys.platform

        # WINDOWS - ALWAYS USE CMD for consistency
        if plat.startswith("win"):
            if use_cmd_on_windows:
                # ALWAYS use CMD on Windows for reliable && syntax
                if command:
                    # Use start to open new CMD window with /k to keep it open
                    escaped_command = command.replace('"', '\\"')
                    process = subprocess.Popen(
                        f'start "Automation Task" cmd /k "{escaped_command}"', 
                        shell=True
                    )
                else:
                    process = subprocess.Popen("start cmd", shell=True)
                
                return {
                    "success": True,
                    "method": "windows_cmd",
                    "terminal_type": "cmd",
                    "pid": process.pid if process else None,
                    "process": process
                }
            
            # Fallback to Windows Terminal if specifically requested
            elif shutil.which("wt"):
                if command:
                    # For wt, use cmd as the profile to avoid PowerShell issues
                    process = subprocess.Popen([
                        "wt", "cmd", "/k", command
                    ])
                else:
                    process = subprocess.Popen(["wt", "cmd"])
                return {
                    "success": True, 
                    "method": "windows_terminal_cmd",
                    "terminal_type": "cmd",
                    "pid": process.pid,
                    "process": process
                }

        # macOS
        elif plat == "darwin":
            if command:
                # Use AppleScript to tell Terminal.app to run the command
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

        # LINUX / Unix
        else:
            # Search for common terminal emulators
            terminals = [
                ("gnome-terminal", ["gnome-terminal", "--", "bash", "-c", '{cmd}; exec bash']),
                ("konsole", ["konsole", "-e", "bash", "-c", '{cmd}; exec bash']),
                ("xfce4-terminal", ["xfce4-terminal", "--command", "bash -c '{cmd}; exec bash'"]),
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

            # If no command given, try to just open any terminal app
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
        logger.error(f"❌ Failed to open new terminal: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "method": "failed"
        }

class TerminalManager:
    """FIXED Terminal Manager with proper command syntax"""
    
    def __init__(self):
        self.active_processes: List[subprocess.Popen] = []
        self.active_terminals: List[Dict[str, Any]] = []
        self.system = platform.system()
        self.appium_process = None
        logger.info(f"🔧 Terminal Manager initialized for {self.system}")

    def fix_python_path(self, python_path: str) -> str:
        """Fix Python path by removing extra quotes"""
        # Remove surrounding quotes if they exist
        if python_path.startswith('"') and python_path.endswith('"'):
            python_path = python_path[1:-1]
        
        # Ensure the path exists
        if not os.path.exists(python_path):
            # Fallback to sys.executable
            logger.warning(f"⚠️ Python path not found: {python_path}, using sys.executable")
            python_path = sys.executable
        
        return python_path

    def build_command_for_terminal(
        self, 
        commands: List[str], 
        terminal_type: str = "cmd"
    ) -> str:
        """Build command string with proper syntax for terminal type"""
        if self.system == "Windows":
            if terminal_type == "cmd":
                # CMD uses && for command chaining
                return " && ".join(commands)
            else:
                # PowerShell uses ; for command chaining
                return "; ".join(commands)
        else:
            # Unix/Linux uses && for command chaining
            return " && ".join(commands)

    def get_activation_command(self, venv_path: Path) -> str:
        """Get virtual environment activation command"""
        if self.system == "Windows":
            activate_script = venv_path / "Scripts" / "activate.bat"
            return f'"{activate_script}"'
        else:
            activate_script = venv_path / "bin" / "activate"
            return f'source "{activate_script}"'

    def execute_command(self, command: str, cwd: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
        """Execute a command with FIXED path handling"""
        try:
            logger.info(f"🔧 Executing command: {command}")
            
            # Handle different shell requirements per platform
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

    def create_virtual_environment(self, venv_path: str, python_executable: Optional[str] = None) -> Dict[str, Any]:
        """Create virtual environment with FIXED path handling"""
        try:
            # Fix Python executable path
            python_exec = python_executable or sys.executable
            python_exec = self.fix_python_path(python_exec)
            
            logger.info(f"🔧 Creating virtual environment: {venv_path}")
            logger.info(f"🔧 Using Python: {python_exec}")
            
            # Create virtual environment command with proper quoting
            if self.system == "Windows":
                venv_command = f'{python_exec} -m venv "{venv_path}" --clear --copies'
            else:
                venv_command = f'"{python_exec}" -m venv "{venv_path}" --clear'
            
            result = self.execute_command(venv_command, timeout=120)
            
            if result["success"]:
                # Determine paths in virtual environment
                venv_path_obj = Path(venv_path)
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
                
                logger.info(f"✅ Virtual environment created: {venv_path}")
                logger.info(f"✅ Python executable: {venv_python}")
                
                return {
                    "success": True,
                    "venv_path": venv_path,
                    "python_executable": str(venv_python),
                    "pip_executable": str(venv_pip),
                    "activate_script": str(venv_activate),
                    "output": result["stdout"]
                }
            else:
                logger.error(f"❌ Virtual environment creation failed: {result.get('stderr', 'Unknown error')}")
                return {
                    "success": False,
                    "error": result.get("stderr", "Virtual environment creation failed"),
                    "command": venv_command
                }
                
        except Exception as e:
            logger.error(f"❌ Virtual environment creation failed: {str(e)}")
            return {"success": False, "error": str(e), "venv_path": venv_path}

    def execute_two_terminal_mobile_flow(
        self,
        venv_path: Path,
        requirements_file: Path,
        script_path: Path,
        working_directory: Path
    ) -> Dict[str, Any]:
        """Execute two-terminal flow for mobile automation"""
        try:
            logger.info("🔧 Starting two-terminal mobile automation flow...")
            
            venv_activate = self.get_activation_command(venv_path)
            
            # TERMINAL 1: Dependencies Installation
            logger.info("🔧 Opening Terminal 1: Dependencies Installation...")
            deps_commands = [
                f'cd /d "{working_directory}"' if self.system == "Windows" else f'cd "{working_directory}"',
                venv_activate,
                "echo Installing dependencies for mobile automation...",
                f'pip install -r "{requirements_file}"',
                "echo Dependencies installation completed!",
                "echo Press any key to continue..." if self.system == "Windows" else "echo Press Enter to continue...",
                "pause" if self.system == "Windows" else "read"
            ]
            
            deps_command = self.build_command_for_terminal(deps_commands)
            deps_result = open_new_terminal(deps_command)
            
            if not deps_result["success"]:
                raise Exception(f"Failed to open dependencies terminal: {deps_result.get('error', 'Unknown error')}")
            
            self.active_terminals.append(deps_result)
            
            # Wait a moment for dependencies terminal to start
            time.sleep(2)
            
            # TERMINAL 2: Appium and Script Execution
            logger.info("🔧 Opening Terminal 2: Appium + Script Execution...")
            script_commands = [
                f'cd /d "{working_directory}"' if self.system == "Windows" else f'cd "{working_directory}"',
                venv_activate,
                "echo Starting Appium server...",
                "start /b appium --port 4723" if self.system == "Windows" else "appium --port 4723 &",
                "timeout /t 5" if self.system == "Windows" else "sleep 5",
                "echo Appium server started, running mobile automation script...",
                f'python "{script_path}"',
                "echo Mobile automation completed!",
                "echo Press any key to continue..." if self.system == "Windows" else "echo Press Enter to continue...",
                "pause" if self.system == "Windows" else "read"
            ]
            
            script_command = self.build_command_for_terminal(script_commands)
            script_result = open_new_terminal(script_command)
            
            if not script_result["success"]:
                raise Exception(f"Failed to open script terminal: {script_result.get('error', 'Unknown error')}")
            
            self.active_terminals.append(script_result)
            
            logger.info("✅ Two-terminal mobile flow started successfully")
            
            return {
                "success": True,
                "terminals_opened": 2,
                "deps_terminal": deps_result,
                "script_terminal": script_result,
                "approach": "two_terminal_mobile"
            }
            
        except Exception as e:
            logger.error(f"❌ Two-terminal mobile flow failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "terminals_opened": len(self.active_terminals),
                "approach": "two_terminal_mobile"
            }

    def execute_two_terminal_web_flow(
        self,
        venv_path: Path,
        requirements_file: Path,
        script_path: Path,
        working_directory: Path
    ) -> Dict[str, Any]:
        """Execute two-terminal flow for web automation"""
        try:
            logger.info("🔧 Starting two-terminal web automation flow...")
            
            venv_activate = self.get_activation_command(venv_path)
            
            # TERMINAL 1: Dependencies + Playwright Installation
            logger.info("🔧 Opening Terminal 1: Dependencies + Playwright Installation...")
            deps_commands = [
                f'cd /d "{working_directory}"' if self.system == "Windows" else f'cd "{working_directory}"',
                venv_activate,
                "echo Installing dependencies for web automation...",
                f'pip install -r "{requirements_file}"',
                "echo Installing Playwright browsers...",
                "playwright install",
                "echo Web automation setup completed!",
                "echo Press any key to continue..." if self.system == "Windows" else "echo Press Enter to continue...",
                "pause" if self.system == "Windows" else "read"
            ]
            
            deps_command = self.build_command_for_terminal(deps_commands)
            deps_result = open_new_terminal(deps_command)
            
            if not deps_result["success"]:
                raise Exception(f"Failed to open dependencies terminal: {deps_result.get('error', 'Unknown error')}")
            
            self.active_terminals.append(deps_result)
            
            # Wait a moment for dependencies terminal to start
            time.sleep(2)
            
            # TERMINAL 2: Script Execution
            logger.info("🔧 Opening Terminal 2: Web Script Execution...")
            script_commands = [
                f'cd /d "{working_directory}"' if self.system == "Windows" else f'cd "{working_directory}"',
                venv_activate,
                "echo Running web automation script...",
                f'python "{script_path}"',
                "echo Web automation completed!",
                "echo Press any key to continue..." if self.system == "Windows" else "echo Press Enter to continue...",
                "pause" if self.system == "Windows" else "read"
            ]
            
            script_command = self.build_command_for_terminal(script_commands)
            script_result = open_new_terminal(script_command)
            
            if not script_result["success"]:
                raise Exception(f"Failed to open script terminal: {script_result.get('error', 'Unknown error')}")
            
            self.active_terminals.append(script_result)
            
            logger.info("✅ Two-terminal web flow started successfully")
            
            return {
                "success": True,
                "terminals_opened": 2,
                "deps_terminal": deps_result,
                "script_terminal": script_result,
                "approach": "two_terminal_web"
            }
            
        except Exception as e:
            logger.error(f"❌ Two-terminal web flow failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "terminals_opened": len(self.active_terminals),
                "approach": "two_terminal_web"
            }

    def execute_script_in_new_terminal(
        self, 
        script_path: str, 
        working_directory: Optional[str] = None,
        python_executable: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a Python script in a new terminal window - SINGLE TERMINAL (fallback)"""
        try:
            logger.info(f"🔧 Executing script in new terminal: {script_path}")
            
            # Fix Python executable path
            python_exec = python_executable or sys.executable
            python_exec = self.fix_python_path(python_exec)
            
            # Build the execution command
            script_path = Path(script_path).resolve()
            if working_directory:
                working_directory = Path(working_directory).resolve()
                commands = [
                    f'cd /d "{working_directory}"' if self.system == "Windows" else f'cd "{working_directory}"',
                    f'"{python_exec}" "{script_path}"',
                    "echo Script execution completed!",
                    "pause" if self.system == "Windows" else "read"
                ]
            else:
                commands = [
                    f'"{python_exec}" "{script_path}"',
                    "echo Script execution completed!",
                    "pause" if self.system == "Windows" else "read"
                ]
            
            command = self.build_command_for_terminal(commands)
            
            # Open new terminal with the command
            terminal_result = open_new_terminal(command)
            
            if terminal_result["success"]:
                self.active_terminals.append(terminal_result)
                logger.info(f"✅ Script started in new terminal: {terminal_result['method']}")
                return {
                    "success": True,
                    "terminal_info": terminal_result,
                    "script_path": str(script_path),
                    "working_directory": str(working_directory) if working_directory else None,
                    "python_executable": python_exec
                }
            else:
                logger.error(f"❌ Failed to open terminal: {terminal_result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "error": terminal_result.get("error", "Terminal creation failed"),
                    "script_path": str(script_path)
                }
                
        except Exception as e:
            logger.error(f"❌ Script execution in new terminal failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "script_path": script_path
            }

    def start_appium_server(self, port: int = 4723) -> Dict[str, Any]:
        """Start Appium server on specified port"""
        try:
            # Check if Appium is already running
            status = self.get_appium_server_status()
            if status.get("running", False):
                logger.info("✅ Appium server is already running")
                return {"success": True, "message": "Appium server already running", "port": port}
            
            logger.info(f"🔧 Starting Appium server on port {port}...")
            
            # Start Appium server
            appium_command = f"appium --port {port} --log-level info"
            result = self.start_process_detached(appium_command)
            
            if result["success"]:
                self.appium_process = result["process"]
                time.sleep(3)  # Wait for server to start
                
                # Verify server is running
                status = self.get_appium_server_status()
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
        """Start a detached process"""
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

    def get_appium_server_status(self) -> Dict[str, Any]:
        """Check Appium server status"""
        try:
            import requests
            resp = requests.get("http://127.0.0.1:4723/status", timeout=5)
            if resp.status_code == 200:
                return {"running": True, "status": "ready", "response": resp.json()}
            else:
                return {"running": False, "status": "not_ready", "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"running": False, "status": "offline", "error": str(e)}

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
                    logger.warning("⚠️ Appium server didn't stop gracefully, force killing...")
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
        """Clean up all active processes"""
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
        """Get status of active processes and terminals"""
        return {
            "active_processes": len(self.active_processes),
            "active_terminals": len(self.active_terminals),
            "appium_running": self.appium_process is not None and self.appium_process.poll() is None,
            "system": self.system,
            "terminal_methods": [t.get("method", "unknown") for t in self.active_terminals]
        }

# Global terminal manager instance
_terminal_manager = None

def get_terminal_manager() -> TerminalManager:
    """Get or create terminal manager instance"""
    global _terminal_manager
    if _terminal_manager is None:
        _terminal_manager = TerminalManager()
    return _terminal_manager

if __name__ == "__main__":
    # Test the fixed terminal manager
    tm = TerminalManager()
    print("🧪 Testing FIXED Terminal Manager...")
    
    # Test Python path fixing
    test_path = '"D:\\SearchLook\\aisa-agent-framework-v1\\venv\\Scripts\\python.exe"'
    fixed_path = tm.fix_python_path(test_path)
    print(f"Fixed Python path: {fixed_path}")
    
    # Test command building
    commands = ["echo Hello", "echo World", "pause"]
    built_command = tm.build_command_for_terminal(commands)
    print(f"Built command: {built_command}")
    
    print("🧪 Fixed Terminal Manager test completed")