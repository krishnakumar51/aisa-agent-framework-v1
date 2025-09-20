"""
Enhanced Generic Mobile Automation Tools
Robust Appium-based automation with advanced strategies
"""
import time
import json
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

try:
    from appium import webdriver
    from appium.options.android import UiAutomator2Options
    from appium.options.ios import XCUITestOptions
    from appium.webdriver.common.appiumby import AppiumBy
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    APPIUM_AVAILABLE = True
except ImportError:
    APPIUM_AVAILABLE = False
    webdriver = None

class GenericMobileAutomationTools:
    """Enhanced generic mobile automation tools with robust strategies"""
    
    def __init__(self):
        self.driver = None
        self.platform = None
        self.device_name = None
        self.default_timeout = 30
        self.retry_attempts = 3
        self.setup_completed = False
        self.appium_server_url = "http://127.0.0.1:4723"
        
        print("📱 Generic Mobile Automation Tools initialized")
    
    def setup_driver(self, 
                    platform: str = "Android",
                    device_name: str = "emulator-5554",
                    app_package: str = None,
                    app_activity: str = None,
                    app_path: str = None,
                    automation_name: str = None) -> bool:
        """Setup mobile driver with robust configuration"""
        try:
            if not APPIUM_AVAILABLE:
                print("❌ Appium not available. Install with: pip install Appium-Python-Client")
                return False
            
            print(f"📱 Setting up {platform} driver for device: {device_name}")
            
            self.platform = platform.lower()
            self.device_name = device_name
            
            # Configure capabilities based on platform
            if self.platform == "android":
                options = UiAutomator2Options()
                options.platform_name = "Android"
                options.device_name = device_name
                options.automation_name = automation_name or "UiAutomator2"
                
                # Add app details if provided
                if app_package:
                    options.app_package = app_package
                if app_activity:
                    options.app_activity = app_activity
                if app_path:
                    options.app = app_path
                
                # Additional Android options for stability
                options.no_reset = True
                options.full_reset = False
                options.new_command_timeout = 300
                options.implicit_wait = 10
                
            elif self.platform == "ios":
                options = XCUITestOptions()
                options.platform_name = "iOS"
                options.device_name = device_name
                options.automation_name = automation_name or "XCUITest"
                
                if app_path:
                    options.app = app_path
                
                # Additional iOS options
                options.new_command_timeout = 300
                options.implicit_wait = 10
            else:
                print(f"❌ Unsupported platform: {platform}")
                return False
            
            # Create driver with retries
            for attempt in range(self.retry_attempts):
                try:
                    print(f"🔗 Connecting to Appium server (attempt {attempt + 1})...")
                    
                    self.driver = webdriver.Remote(
                        command_executor=self.appium_server_url,
                        options=options
                    )
                    
                    # Set implicit wait
                    self.driver.implicitly_wait(self.default_timeout)
                    
                    self.setup_completed = True
                    print("✅ Mobile driver setup completed successfully")
                    return True
                    
                except Exception as e:
                    print(f"❌ Driver setup attempt {attempt + 1} failed: {str(e)}")
                    if attempt < self.retry_attempts - 1:
                        time.sleep(3 * (attempt + 1))  # Progressive delay
                    
            print(f"❌ Failed to setup mobile driver after {self.retry_attempts} attempts")
            return False
            
        except Exception as e:
            print(f"❌ Mobile driver setup failed: {str(e)}")
            return False
    
    def launch_app(self, package_name: str = None) -> bool:
        """Launch app with robust error handling"""
        if not self.setup_completed:
            print("❌ Driver not setup. Call setup_driver() first.")
            return False
        
        try:
            print(f"🚀 Launching app: {package_name or 'Current app'}")
            
            if package_name and self.platform == "android":
                # Android-specific app launch
                self.driver.activate_app(package_name)
            else:
                # Generic app launch
                self.driver.launch_app()
            
            # Wait for app to be ready
            time.sleep(3)
            
            print("✅ App launched successfully")
            return True
            
        except Exception as e:
            print(f"❌ App launch failed: {str(e)}")
            return False
    
    def tap_element(self, 
                   locator_strategies: List[Dict[str, str]], 
                   element_name: str = "element",
                   timeout: int = None) -> bool:
        """Tap element using multiple locator strategies"""
        if not self.setup_completed:
            return False
        
        timeout = timeout or self.default_timeout
        wait = WebDriverWait(self.driver, timeout)
        
        for strategy in locator_strategies:
            locator_type = strategy.get("type", "xpath")
            locator_value = strategy.get("value", "")
            
            if not locator_value:
                continue
            
            try:
                print(f"🔍 Trying to tap {element_name} with {locator_type}: {locator_value}")
                
                # Create locator based on type
                by_locator = self._create_appium_locator(locator_type, locator_value)
                
                if by_locator:
                    # Wait for element to be present and clickable
                    element = wait.until(EC.element_to_be_clickable(by_locator))
                    
                    # Scroll element into view if needed
                    try:
                        self.driver.execute_script("mobile: scrollToElement", {"element": element})
                    except:
                        pass  # Continue even if scroll fails
                    
                    # Tap the element
                    element.click()
                    
                    print(f"✅ Successfully tapped {element_name}")
                    return True
                    
            except TimeoutException:
                print(f"⚠️ Timeout waiting for element with {locator_type}")
                continue
            except Exception as e:
                print(f"⚠️ Tap failed with {locator_type}: {str(e)}")
                continue
        
        print(f"❌ Failed to tap {element_name} with all strategies")
        return False
    
    def fill_text_field(self, 
                       locator_strategies: List[Dict[str, str]], 
                       text_value: str,
                       field_name: str = "field",
                       clear_first: bool = True,
                       timeout: int = None) -> bool:
        """Fill text field using multiple locator strategies"""
        if not self.setup_completed:
            return False
        
        timeout = timeout or self.default_timeout
        wait = WebDriverWait(self.driver, timeout)
        
        for strategy in locator_strategies:
            locator_type = strategy.get("type", "xpath")
            locator_value = strategy.get("value", "")
            
            if not locator_value:
                continue
            
            try:
                print(f"🔍 Trying to fill {field_name} with {locator_type}: {locator_value}")
                
                # Create locator
                by_locator = self._create_appium_locator(locator_type, locator_value)
                
                if by_locator:
                    # Wait for element
                    element = wait.until(EC.element_to_be_clickable(by_locator))
                    
                    # Scroll into view if needed
                    try:
                        self.driver.execute_script("mobile: scrollToElement", {"element": element})
                    except:
                        pass
                    
                    # Focus the element
                    element.click()
                    time.sleep(0.5)
                    
                    # Clear field if requested
                    if clear_first:
                        element.clear()
                        time.sleep(0.3)
                    
                    # Send text
                    element.send_keys(text_value)
                    
                    # Verify text was entered (if possible)
                    try:
                        actual_value = element.get_attribute("text") or element.get_attribute("value")
                        if actual_value and text_value in actual_value:
                            print(f"✅ Successfully filled {field_name} with: {text_value}")
                            return True
                    except:
                        # If verification fails, assume success if no exception was thrown
                        print(f"✅ Text entered in {field_name} (verification skipped)")
                        return True
                    
            except TimeoutException:
                print(f"⚠️ Timeout waiting for field with {locator_type}")
                continue
            except Exception as e:
                print(f"⚠️ Fill failed with {locator_type}: {str(e)}")
                continue
        
        print(f"❌ Failed to fill {field_name} with all strategies")
        return False
    
    def swipe_screen(self, direction: str = "down", distance: int = 500) -> bool:
        """Swipe screen in specified direction"""
        if not self.setup_completed:
            return False
        
        try:
            print(f"👆 Swiping {direction} by {distance} pixels")
            
            # Get screen size
            screen_size = self.driver.get_window_size()
            width = screen_size["width"]
            height = screen_size["height"]
            
            # Calculate swipe coordinates
            start_x = width // 2
            start_y = height // 2
            
            if direction.lower() == "down":
                end_x = start_x
                end_y = start_y + distance
            elif direction.lower() == "up":
                end_x = start_x
                end_y = start_y - distance
            elif direction.lower() == "left":
                end_x = start_x - distance
                end_y = start_y
            elif direction.lower() == "right":
                end_x = start_x + distance
                end_y = start_y
            else:
                print(f"❌ Unsupported swipe direction: {direction}")
                return False
            
            # Ensure coordinates are within screen bounds
            end_x = max(0, min(width, end_x))
            end_y = max(0, min(height, end_y))
            
            # Perform swipe
            self.driver.swipe(start_x, start_y, end_x, end_y, duration=800)
            
            time.sleep(1)  # Wait for swipe to complete
            print(f"✅ Swiped {direction} successfully")
            return True
            
        except Exception as e:
            print(f"❌ Swipe failed: {str(e)}")
            return False
    
    def wait_for_element(self, 
                        locator_strategies: List[Dict[str, str]], 
                        element_name: str = "element",
                        timeout: int = None) -> bool:
        """Wait for element using multiple strategies"""
        if not self.setup_completed:
            return False
        
        timeout = timeout or self.default_timeout
        wait = WebDriverWait(self.driver, timeout)
        
        for strategy in locator_strategies:
            locator_type = strategy.get("type", "xpath")
            locator_value = strategy.get("value", "")
            
            if not locator_value:
                continue
            
            try:
                print(f"⏳ Waiting for {element_name} with {locator_type}: {locator_value}")
                
                by_locator = self._create_appium_locator(locator_type, locator_value)
                
                if by_locator:
                    element = wait.until(EC.presence_of_element_located(by_locator))
                    print(f"✅ Element {element_name} found")
                    return True
                    
            except TimeoutException:
                print(f"⚠️ Timeout waiting for element with {locator_type}")
                continue
            except Exception as e:
                print(f"⚠️ Wait failed with {locator_type}: {str(e)}")
                continue
        
        print(f"❌ Element {element_name} not found")
        return False
    
    def take_screenshot(self, filename: str = None) -> bool:
        """Take screenshot for debugging"""
        if not self.setup_completed:
            return False
        
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"mobile_screenshot_{timestamp}.png"
            
            self.driver.save_screenshot(filename)
            print(f"📸 Screenshot saved: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Screenshot failed: {str(e)}")
            return False
    
    def get_current_activity(self) -> str:
        """Get current activity (Android only)"""
        if not self.setup_completed or self.platform != "android":
            return ""
        
        try:
            activity = self.driver.current_activity
            print(f"📱 Current activity: {activity}")
            return activity
        except Exception as e:
            print(f"❌ Failed to get current activity: {str(e)}")
            return ""
    
    def press_back_button(self) -> bool:
        """Press device back button"""
        if not self.setup_completed:
            return False
        
        try:
            print("⬅️ Pressing back button")
            self.driver.back()
            time.sleep(1)
            print("✅ Back button pressed")
            return True
        except Exception as e:
            print(f"❌ Back button press failed: {str(e)}")
            return False
    
    def hide_keyboard(self) -> bool:
        """Hide keyboard if visible"""
        if not self.setup_completed:
            return False
        
        try:
            if self.driver.is_keyboard_shown():
                print("⌨️ Hiding keyboard")
                self.driver.hide_keyboard()
                print("✅ Keyboard hidden")
            return True
        except Exception as e:
            print(f"❌ Hide keyboard failed: {str(e)}")
            return True  # Return True even if failed, as it's not critical
    
    def _create_appium_locator(self, locator_type: str, locator_value: str):
        """Create Appium locator based on type"""
        try:
            if locator_type == "id":
                return (AppiumBy.ID, locator_value)
            elif locator_type == "xpath":
                return (AppiumBy.XPATH, locator_value)
            elif locator_type == "class_name":
                return (AppiumBy.CLASS_NAME, locator_value)
            elif locator_type == "accessibility_id":
                return (AppiumBy.ACCESSIBILITY_ID, locator_value)
            elif locator_type == "android_uiautomator":
                if self.platform == "android":
                    return (AppiumBy.ANDROID_UIAUTOMATOR, locator_value)
            elif locator_type == "ios_predicate":
                if self.platform == "ios":
                    return (AppiumBy.IOS_PREDICATE, locator_value)
            elif locator_type == "ios_class_chain":
                if self.platform == "ios":
                    return (AppiumBy.IOS_CLASS_CHAIN, locator_value)
            elif locator_type == "name":
                return (AppiumBy.NAME, locator_value)
            elif locator_type == "tag_name":
                return (AppiumBy.TAG_NAME, locator_value)
            else:
                # Default to XPath
                return (AppiumBy.XPATH, locator_value)
                
        except Exception as e:
            print(f"❌ Failed to create locator: {str(e)}")
            return None
    
    def close_driver(self):
        """Clean driver shutdown"""
        try:
            if self.driver:
                print("🧹 Closing mobile driver...")
                self.driver.quit()
                self.driver = None
                self.setup_completed = False
                print("✅ Mobile driver closed successfully")
        except Exception as e:
            print(f"⚠️ Driver close warning: {str(e)}")

# Global instance
mobile_tools = GenericMobileAutomationTools()