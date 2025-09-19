"""
Appium mobile automation driver
"""
import time
import json
from typing import Dict, Any, Optional, List, Union
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from app.config.settings import settings

class AppiumDriver:
    """Appium mobile automation driver"""
    
    def __init__(self):
        """Initialize Appium driver"""
        self.driver: Optional[webdriver.Remote] = None
        self.screenshots: List[bytes] = []
        self.execution_logs: List[str] = []
        self.wait: Optional[WebDriverWait] = None
    
    def setup_android(self, device_name: str = "emulator-5554", 
                     app_package: str = None, app_activity: str = None) -> bool:
        """Setup Android driver"""
        try:
            options = UiAutomator2Options()
            options.platform_name = "Android"
            options.device_name = device_name
            options.automation_name = "UiAutomator2"
            options.no_reset = True
            options.full_reset = False
            
            if app_package:
                options.app_package = app_package
            if app_activity:
                options.app_activity = app_activity
            
            # Additional capabilities for stability
            options.set_capability("appium:newCommandTimeout", 300)
            options.set_capability("appium:androidInstallTimeout", 90000)
            options.set_capability("appium:autoGrantPermissions", True)
            options.set_capability("appium:ignoreHiddenApiPolicyError", True)
            
            self.driver = webdriver.Remote(settings.APPIUM_HOST, options=options)
            self.wait = WebDriverWait(self.driver, 30)
            
            self._log("Android driver setup completed")
            return True
            
        except Exception as e:
            self._log(f"Android driver setup failed: {str(e)}")
            return False
    
    def execute_script(self, script: str) -> Dict[str, Any]:
        """Execute automation script"""
        try:
            if not self.driver:
                raise Exception("Driver not initialized")
            
            self._log("Starting script execution")
            
            # Parse script commands
            commands = self._parse_script(script)
            results = []
            
            for i, command in enumerate(commands):
                try:
                    result = self._execute_command(command)
                    results.append({
                        "step": i + 1,
                        "command": command,
                        "success": True,
                        "result": result
                    })
                    
                    # Take screenshot after each step
                    self._take_screenshot()
                    
                except Exception as e:
                    self._log(f"Command failed: {str(e)}")
                    results.append({
                        "step": i + 1,
                        "command": command,
                        "success": False,
                        "error": str(e)
                    })
                    # Continue execution even if one step fails
            
            return {
                "success": any(r["success"] for r in results),  # At least one step succeeded
                "results": results,
                "screenshots": self.screenshots,
                "logs": self.execution_logs
            }
        
        except Exception as e:
            self._log(f"Script execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "logs": self.execution_logs
            }
    
    def _parse_script(self, script: str) -> List[Dict[str, Any]]:
        """Parse automation script into commands"""
        commands = []
        lines = script.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse different command types based on comp.py structure
            if 'find_element' in line and 'click' in line:
                # Extract selector from find_element call
                selector = self._extract_selector(line)
                commands.append({"action": "click", "selector": selector})
            
            elif 'find_element' in line and 'send_keys' in line:
                selector = self._extract_selector(line)
                value = self._extract_send_keys_value(line)
                commands.append({"action": "input", "selector": selector, "value": value})
            
            elif 'wait' in line.lower() or 'sleep' in line.lower():
                timeout = self._extract_timeout(line)
                commands.append({"action": "wait", "timeout": timeout})
            
            elif 'screenshot' in line.lower():
                commands.append({"action": "screenshot"})
            
            elif 'scroll' in line.lower() or 'swipe' in line.lower():
                commands.append({"action": "scroll"})
        
        return commands
    
    def _execute_command(self, command: Dict[str, Any]) -> Any:
        """Execute individual command"""
        action = command["action"]
        
        if action == "click":
            element = self._find_element_safely(command["selector"])
            if element:
                element.click()
                self._log(f"Clicked: {command['selector']}")
                return {"clicked": True}
            else:
                raise Exception(f"Element not found: {command['selector']}")
        
        elif action == "input":
            element = self._find_element_safely(command["selector"])
            if element:
                element.clear()
                element.send_keys(command["value"])
                self._log(f"Input {command['selector']} with: {command['value']}")
                return {"input": True}
            else:
                raise Exception(f"Element not found: {command['selector']}")
        
        elif action == "wait":
            time.sleep(command["timeout"] / 1000.0)  # Convert to seconds
            self._log(f"Waited: {command['timeout']}ms")
            return {"waited": command["timeout"]}
        
        elif action == "screenshot":
            self._take_screenshot()
            self._log("Screenshot taken")
            return {"screenshot": True}
        
        elif action == "scroll":
            self._scroll_down()
            self._log("Scrolled down")
            return {"scrolled": True}
        
        else:
            raise Exception(f"Unknown action: {action}")
    
    def _find_element_safely(self, selector: str, timeout: int = 10) -> Optional[Any]:
        """Find element with multiple strategies"""
        strategies = [
            (AppiumBy.ID, selector),
            (AppiumBy.XPATH, selector),
            (AppiumBy.ACCESSIBILITY_ID, selector),
            (AppiumBy.CLASS_NAME, selector),
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{selector}")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().descriptionContains("{selector}")'),
        ]
        
        for strategy, locator in strategies:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((strategy, locator))
                )
                return element
            except TimeoutException:
                continue
        
        return None
    
    def _extract_selector(self, line: str) -> str:
        """Extract selector from script line"""
        # Simple extraction - look for common patterns
        if 'By.ID' in line:
            return line.split('"')[1] if '"' in line else line.split("'")[1]
        elif 'By.XPATH' in line:
            return line.split('"')[1] if '"' in line else line.split("'")[1]
        elif 'resource-id' in line:
            return line.split('"')[1] if '"' in line else line.split("'")[1]
        else:
            # Default extraction
            parts = line.split('"')
            return parts[1] if len(parts) > 1 else line.strip()
    
    def _extract_send_keys_value(self, line: str) -> str:
        """Extract value from send_keys call"""
        if 'send_keys(' in line:
            start = line.find('send_keys(') + len('send_keys(')
            end = line.rfind(')')
            value = line[start:end].strip().strip('"\'')
            return value
        return ""
    
    def _extract_timeout(self, line: str) -> int:
        """Extract timeout value from wait/sleep call"""
        import re
        numbers = re.findall(r'\d+', line)
        return int(numbers[0]) * 1000 if numbers else 3000  # Default 3 seconds
    
    def _take_screenshot(self) -> bytes:
        """Take device screenshot"""
        try:
            if self.driver:
                screenshot = self.driver.get_screenshot_as_png()
                self.screenshots.append(screenshot)
                return screenshot
        except Exception as e:
            self._log(f"Screenshot failed: {str(e)}")
        return b""
    
    def _scroll_down(self):
        """Scroll down on the screen"""
        try:
            if self.driver:
                size = self.driver.get_window_size()
                start_x = size['width'] // 2
                start_y = size['height'] * 0.8
                end_x = size['width'] // 2
                end_y = size['height'] * 0.2
                
                self.driver.swipe(start_x, start_y, end_x, end_y, 1000)
        except Exception as e:
            self._log(f"Scroll failed: {str(e)}")
    
    def _log(self, message: str):
        """Add log message"""
        self.execution_logs.append(message)
        print(f"[Appium] {message}")
    
    def cleanup(self):
        """Cleanup driver resources"""
        try:
            if self.driver:
                self.driver.quit()
            self._log("Driver cleanup completed")
        except Exception as e:
            self._log(f"Cleanup error: {str(e)}")
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get current device information"""
        if not self.driver:
            return {}
        
        try:
            return {
                "platform": self.driver.capabilities.get('platformName'),
                "device_name": self.driver.capabilities.get('deviceName'),
                "platform_version": self.driver.capabilities.get('platformVersion'),
                "app_package": self.driver.current_package,
                "app_activity": self.driver.current_activity,
                "window_size": self.driver.get_window_size()
            }
        except Exception as e:
            self._log(f"Error getting device info: {str(e)}")
            return {}

# Global Appium driver instance
appium_driver = AppiumDriver()