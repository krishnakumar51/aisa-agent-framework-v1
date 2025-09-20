"""
Testing Environment Manager Utility
Handles virtual environment creation, dependency management, and automation tool setup
"""
import asyncio
import logging
import os
import subprocess
import sys
import venv
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class TestingEnvironmentManager:
    """Utility class for managing testing environments across different platforms"""
    
    def __init__(self):
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.platform = platform.system().lower()
        
    async def create_isolated_environment(self, env_path: Path, requirements_file: Path) -> Dict[str, Any]:
        """
        Create a completely isolated testing environment
        
        Args:
            env_path: Path where environment should be created
            requirements_file: Path to requirements.txt
            
        Returns:
            Environment creation results
        """
        logger.info(f"🔧 Creating isolated environment: {env_path}")
        
        try:
            # Step 1: Remove existing environment
            if env_path.exists():
                shutil.rmtree(env_path)
                logger.info(f"🔧 Removed existing environment")
            
            # Step 2: Create virtual environment
            venv_result = await self._create_venv(env_path)
            if not venv_result['success']:
                return venv_result
            
            # Step 3: Upgrade pip
            pip_result = await self._upgrade_pip(env_path)
            if not pip_result['success']:
                logger.warning(f"🟡 Pip upgrade failed: {pip_result['error']}")
            
            # Step 4: Install requirements
            if requirements_file.exists():
                install_result = await self._install_requirements(env_path, requirements_file)
                if not install_result['success']:
                    return install_result
            else:
                logger.warning(f"🟡 Requirements file not found: {requirements_file}")
                install_result = {"success": True, "packages_installed": 0}
            
            # Step 5: Verify environment
            verify_result = await self._verify_environment(env_path)
            
            logger.info(f"🔧 ✅ Isolated environment created successfully")
            
            return {
                "success": True,
                "env_path": str(env_path),
                "python_executable": str(self._get_python_executable(env_path)),
                "python_version": self.python_version,
                "platform": self.platform,
                "venv_creation": venv_result,
                "pip_upgrade": pip_result,
                "requirements_install": install_result,
                "environment_verification": verify_result
            }
            
        except Exception as e:
            error_msg = f"Environment creation failed: {str(e)}"
            logger.error(f"🔴 {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "env_path": str(env_path)
            }
    
    async def setup_automation_tools(self, env_path: Path, platform_type: str) -> Dict[str, Any]:
        """
        Set up platform-specific automation tools
        
        Args:
            env_path: Virtual environment path
            platform_type: 'web', 'mobile', or 'both'
            
        Returns:
            Tool setup results
        """
        logger.info(f"🔧 Setting up automation tools for: {platform_type}")
        
        results = {
            "platform_type": platform_type,
            "tools_setup": {},
            "overall_success": True
        }
        
        python_exe = self._get_python_executable(env_path)
        
        try:
            if platform_type.lower() in ["web", "browser", "both"]:
                # Setup Playwright
                playwright_result = await self._setup_playwright_tools(python_exe, env_path)
                results["tools_setup"]["playwright"] = playwright_result
                if not playwright_result["success"]:
                    results["overall_success"] = False
            
            if platform_type.lower() in ["mobile", "android", "ios", "both"]:
                # Setup Appium tools
                appium_result = await self._setup_appium_tools(python_exe, env_path)
                results["tools_setup"]["appium"] = appium_result
                if not appium_result["success"]:
                    results["overall_success"] = False
            
            # Setup common OCR tools
            ocr_result = await self._setup_ocr_tools(python_exe, env_path)
            results["tools_setup"]["ocr"] = ocr_result
            if not ocr_result["success"]:
                logger.warning(f"🟡 OCR setup failed: {ocr_result.get('error', 'Unknown error')}")
            
            logger.info(f"🔧 Automation tools setup completed: {'✅' if results['overall_success'] else '⚠️'}")
            
            return results
            
        except Exception as e:
            error_msg = f"Automation tools setup failed: {str(e)}"
            logger.error(f"🔴 {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "platform_type": platform_type
            }
    
    async def validate_automation_readiness(self, env_path: Path, platform_type: str) -> Dict[str, Any]:
        """
        Validate that the environment is ready for automation
        
        Args:
            env_path: Virtual environment path
            platform_type: Target platform type
            
        Returns:
            Validation results
        """
        logger.info(f"🔧 Validating automation readiness for: {platform_type}")
        
        python_exe = self._get_python_executable(env_path)
        validations = {}
        overall_ready = True
        
        try:
            # Basic Python validation
            python_check = await self._validate_python(python_exe)
            validations["python"] = python_check
            if not python_check["valid"]:
                overall_ready = False
            
            # Platform-specific validations
            if platform_type.lower() in ["web", "browser", "both"]:
                playwright_check = await self._validate_playwright(python_exe)
                validations["playwright"] = playwright_check
                if not playwright_check["valid"]:
                    overall_ready = False
            
            if platform_type.lower() in ["mobile", "android", "ios", "both"]:
                appium_check = await self._validate_appium(python_exe)
                validations["appium"] = appium_check
                if not appium_check["valid"]:
                    overall_ready = False
            
            # OCR validation
            ocr_check = await self._validate_ocr(python_exe)
            validations["ocr"] = ocr_check
            if not ocr_check["valid"]:
                logger.warning(f"🟡 OCR validation failed - screenshots may not work")
            
            logger.info(f"🔧 Validation complete: {'✅ READY' if overall_ready else '⚠️ ISSUES FOUND'}")
            
            return {
                "ready": overall_ready,
                "platform_type": platform_type,
                "env_path": str(env_path),
                "validations": validations,
                "recommendations": self._generate_setup_recommendations(validations)
            }
            
        except Exception as e:
            error_msg = f"Validation failed: {str(e)}"
            logger.error(f"🔴 {error_msg}")
            
            return {
                "ready": False,
                "error": error_msg,
                "platform_type": platform_type,
                "env_path": str(env_path)
            }
    
    # Private helper methods
    
    async def _create_venv(self, env_path: Path) -> Dict[str, Any]:
        """Create Python virtual environment"""
        try:
            logger.info(f"🔧 Creating virtual environment: {env_path}")
            venv.create(env_path, with_pip=True)
            
            return {
                "success": True,
                "env_path": str(env_path),
                "python_executable": str(self._get_python_executable(env_path))
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"venv creation failed: {str(e)}"
            }
    
    async def _upgrade_pip(self, env_path: Path) -> Dict[str, Any]:
        """Upgrade pip in virtual environment"""
        try:
            python_exe = self._get_python_executable(env_path)
            
            process = await asyncio.create_subprocess_exec(
                str(python_exe), "-m", "pip", "install", "--upgrade", "pip",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "output": stdout.decode() if stdout else ""
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode() if stderr else "Unknown pip upgrade error"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"pip upgrade failed: {str(e)}"
            }
    
    async def _install_requirements(self, env_path: Path, requirements_file: Path) -> Dict[str, Any]:
        """Install requirements in virtual environment"""
        try:
            python_exe = self._get_python_executable(env_path)
            
            logger.info(f"🔧 Installing requirements from: {requirements_file}")
            
            process = await asyncio.create_subprocess_exec(
                str(python_exe), "-m", "pip", "install", "-r", str(requirements_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)  # 5 minute timeout
            
            if process.returncode == 0:
                # Count installed packages
                packages_count = len([line for line in open(requirements_file).readlines() if line.strip() and not line.startswith('#')])
                
                return {
                    "success": True,
                    "packages_installed": packages_count,
                    "output": stdout.decode() if stdout else ""
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode() if stderr else "Unknown installation error",
                    "output": stdout.decode() if stdout else ""
                }
                
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Requirements installation timed out after 5 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Requirements installation failed: {str(e)}"
            }
    
    async def _verify_environment(self, env_path: Path) -> Dict[str, Any]:
        """Verify virtual environment is working"""
        try:
            python_exe = self._get_python_executable(env_path)
            
            # Test basic Python execution
            process = await asyncio.create_subprocess_exec(
                str(python_exe), "-c", "import sys; print(sys.version)",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "python_version": stdout.decode().strip(),
                    "executable": str(python_exe)
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode() if stderr else "Python execution failed"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Environment verification failed: {str(e)}"
            }
    
    async def _setup_playwright_tools(self, python_exe: Path, env_path: Path) -> Dict[str, Any]:
        """Setup Playwright for web automation"""
        try:
            logger.info(f"🔧 Setting up Playwright...")
            
            # Install Playwright browsers
            process = await asyncio.create_subprocess_exec(
                str(python_exe), "-m", "playwright", "install",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)  # 5 minute timeout
            
            if process.returncode == 0:
                logger.info(f"🔧 ✅ Playwright browsers installed")
                
                return {
                    "success": True,
                    "tool": "playwright",
                    "browsers_installed": True,
                    "output": stdout.decode() if stdout else ""
                }
            else:
                logger.warning(f"🟡 Playwright browser installation failed")
                
                return {
                    "success": False,
                    "tool": "playwright",
                    "browsers_installed": False,
                    "error": stderr.decode() if stderr else "Browser installation failed"
                }
                
        except asyncio.TimeoutError:
            return {
                "success": False,
                "tool": "playwright",
                "error": "Playwright browser installation timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "tool": "playwright",
                "error": f"Playwright setup failed: {str(e)}"
            }
    
    async def _setup_appium_tools(self, python_exe: Path, env_path: Path) -> Dict[str, Any]:
        """Setup Appium for mobile automation"""
        try:
            logger.info(f"🔧 Setting up Appium tools...")
            
            # Check if Appium server is available
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 4723))
            sock.close()
            
            server_available = (result == 0)
            
            if server_available:
                logger.info(f"🔧 ✅ Appium server detected on localhost:4723")
            else:
                logger.warning(f"🟡 Appium server not running on localhost:4723")
            
            return {
                "success": True,
                "tool": "appium",
                "server_available": server_available,
                "server_url": "http://localhost:4723" if server_available else None,
                "warning": "Appium server not detected - manual start required" if not server_available else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "tool": "appium",
                "error": f"Appium setup check failed: {str(e)}"
            }
    
    async def _setup_ocr_tools(self, python_exe: Path, env_path: Path) -> Dict[str, Any]:
        """Setup OCR tools for screenshot validation"""
        try:
            logger.info(f"🔧 Setting up OCR tools...")
            
            # Test pytesseract import
            process = await asyncio.create_subprocess_exec(
                str(python_exe), "-c", "import pytesseract; from PIL import Image; print('OCR tools available')",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"🔧 ✅ OCR tools available")
                
                return {
                    "success": True,
                    "tool": "ocr",
                    "libraries_available": True,
                    "output": stdout.decode() if stdout else ""
                }
            else:
                logger.warning(f"🟡 OCR tools not available")
                
                return {
                    "success": False,
                    "tool": "ocr",
                    "libraries_available": False,
                    "error": stderr.decode() if stderr else "OCR libraries not found"
                }
                
        except Exception as e:
            return {
                "success": False,
                "tool": "ocr",
                "error": f"OCR setup failed: {str(e)}"
            }
    
    async def _validate_python(self, python_exe: Path) -> Dict[str, Any]:
        """Validate Python executable"""
        try:
            process = await asyncio.create_subprocess_exec(
                str(python_exe), "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                version = stdout.decode().strip()
                return {
                    "valid": True,
                    "version": version,
                    "executable": str(python_exe)
                }
            else:
                return {
                    "valid": False,
                    "error": stderr.decode() if stderr else "Python validation failed"
                }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Python validation exception: {str(e)}"
            }
    
    async def _validate_playwright(self, python_exe: Path) -> Dict[str, Any]:
        """Validate Playwright installation"""
        try:
            process = await asyncio.create_subprocess_exec(
                str(python_exe), "-c", "from playwright.async_api import async_playwright; print('Playwright available')",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "valid": True,
                    "tool": "playwright",
                    "available": True
                }
            else:
                return {
                    "valid": False,
                    "tool": "playwright",
                    "available": False,
                    "error": stderr.decode() if stderr else "Playwright not available"
                }
        except Exception as e:
            return {
                "valid": False,
                "tool": "playwright",
                "error": f"Playwright validation failed: {str(e)}"
            }
    
    async def _validate_appium(self, python_exe: Path) -> Dict[str, Any]:
        """Validate Appium installation"""
        try:
            process = await asyncio.create_subprocess_exec(
                str(python_exe), "-c", "from appium import webdriver; print('Appium client available')",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "valid": True,
                    "tool": "appium",
                    "client_available": True
                }
            else:
                return {
                    "valid": False,
                    "tool": "appium",
                    "client_available": False,
                    "error": stderr.decode() if stderr else "Appium client not available"
                }
        except Exception as e:
            return {
                "valid": False,
                "tool": "appium",
                "error": f"Appium validation failed: {str(e)}"
            }
    
    async def _validate_ocr(self, python_exe: Path) -> Dict[str, Any]:
        """Validate OCR tools"""
        try:
            process = await asyncio.create_subprocess_exec(
                str(python_exe), "-c", "import pytesseract; from PIL import Image; print('OCR available')",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "valid": True,
                    "tool": "ocr",
                    "libraries_available": True
                }
            else:
                return {
                    "valid": False,
                    "tool": "ocr",
                    "libraries_available": False,
                    "error": stderr.decode() if stderr else "OCR libraries not available"
                }
        except Exception as e:
            return {
                "valid": False,
                "tool": "ocr",
                "error": f"OCR validation failed: {str(e)}"
            }
    
    def _generate_setup_recommendations(self, validations: Dict[str, Any]) -> List[str]:
        """Generate setup recommendations based on validation results"""
        recommendations = []
        
        for tool, validation in validations.items():
            if not validation.get("valid", False):
                if tool == "python":
                    recommendations.append("Fix Python installation in virtual environment")
                elif tool == "playwright":
                    recommendations.append("Install Playwright browsers: python -m playwright install")
                elif tool == "appium":
                    recommendations.append("Start Appium server: appium (requires Node.js and Appium installed)")
                elif tool == "ocr":
                    recommendations.append("Install OCR dependencies: apt-get install tesseract-ocr (Linux) or brew install tesseract (Mac)")
        
        if not recommendations:
            recommendations.append("Environment is ready for automation testing")
        
        return recommendations
    
    def _get_python_executable(self, env_path: Path) -> Path:
        """Get Python executable path for virtual environment"""
        if platform.system() == "Windows":
            return env_path / "Scripts" / "python.exe"
        else:
            return env_path / "bin" / "python"