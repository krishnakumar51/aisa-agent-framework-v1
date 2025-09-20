"""
Enhanced Generic Web Automation Tools
Robust Playwright-based automation with advanced strategies
"""
import asyncio
import time
import json
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext, ElementHandle
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    async_playwright = None

class GenericWebAutomationTools:
    """Enhanced generic web automation tools with robust strategies"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.default_timeout = 30000  # 30 seconds
        self.retry_attempts = 3
        self.setup_completed = False
        
        print("🔧 Generic Web Automation Tools initialized")
    
    async def setup_browser(self, 
                           headless: bool = True, 
                           browser_type: str = "chromium",
                           viewport: Dict[str, int] = None) -> bool:
        """Setup browser with robust configuration"""
        try:
            if not PLAYWRIGHT_AVAILABLE:
                print("❌ Playwright not available. Install with: pip install playwright")
                return False
            
            print(f"🔧 Setting up {browser_type} browser...")
            
            self.playwright = await async_playwright().start()
            
            # Browser options for stability
            browser_options = {
                "headless": headless,
                "args": [
                    "--no-sandbox",
                    "--disable-setuid-sandbox", 
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-default-apps"
                ]
            }
            
            # Launch browser
            if browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(**browser_options)
            elif browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(**browser_options)
            else:
                self.browser = await self.playwright.chromium.launch(**browser_options)
            
            # Create context with realistic settings
            context_options = {
                "viewport": viewport or {"width": 1920, "height": 1080},
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "ignore_https_errors": True,
                "java_script_enabled": True,
                "accept_downloads": True
            }
            
            self.context = await self.browser.new_context(**context_options)
            
            # Create page with timeouts
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.default_timeout)
            self.page.set_default_navigation_timeout(self.default_timeout)
            
            self.setup_completed = True
            print("✅ Web browser setup completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Browser setup failed: {str(e)}")
            await self._cleanup_browser()
            return False
    
    async def navigate_to(self, url: str, wait_until: str = "domcontentloaded") -> bool:
        """Navigate to URL with robust error handling"""
        if not self.setup_completed:
            print("❌ Browser not setup. Call setup_browser() first.")
            return False
        
        for attempt in range(self.retry_attempts):
            try:
                print(f"🔗 Navigating to: {url} (attempt {attempt + 1})")
                
                # Add small delay for stability
                await asyncio.sleep(1)
                
                response = await self.page.goto(
                    url,
                    wait_until=wait_until,
                    timeout=self.default_timeout
                )
                
                if response and response.status < 400:
                    print(f"✅ Navigation successful (status: {response.status})")
                    
                    # Wait for page to be fully interactive
                    await self.page.wait_for_load_state("networkidle", timeout=10000)
                    return True
                else:
                    print(f"⚠️ Navigation returned status: {response.status if response else 'None'}")
                    
            except Exception as e:
                print(f"❌ Navigation attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(2 * (attempt + 1))  # Progressive delay
                
        return False
    
    async def click_element(self, 
                           locator_strategies: List[Dict[str, str]], 
                           element_name: str = "element",
                           timeout: int = None) -> bool:
        """Click element using multiple locator strategies"""
        if not self.setup_completed:
            return False
        
        timeout = timeout or self.default_timeout
        
        for strategy in locator_strategies:
            locator_type = strategy.get("type", "css")
            locator_value = strategy.get("value", "")
            
            if not locator_value:
                continue
            
            try:
                print(f"🔍 Trying to click {element_name} with {locator_type}: {locator_value}")
                
                # Create locator based on type
                locator = self._create_playwright_locator(locator_type, locator_value)
                
                if locator:
                    # Wait for element and check if it's actionable
                    await locator.wait_for(state="visible", timeout=timeout)
                    
                    # Scroll element into view if needed
                    try:
                        await locator.scroll_into_view_if_needed(timeout=5000)
                    except:
                        pass  # Continue even if scroll fails
                    
                    # Wait a bit more for stability
                    await asyncio.sleep(0.5)
                    
                    # Try to click
                    await locator.click(timeout=timeout)
                    
                    print(f"✅ Successfully clicked {element_name}")
                    return True
                    
            except Exception as e:
                print(f"⚠️ Click failed with {locator_type}: {str(e)}")
                continue
        
        print(f"❌ Failed to click {element_name} with all strategies")
        return False
    
    async def fill_text_field(self, 
                             locator_strategies: List[Dict[str, str]], 
                             text_value: str,
                             field_name: str = "field",
                             clear_first: bool = True,
                             timeout: int = None) -> bool:
        """Fill text field using multiple locator strategies"""
        if not self.setup_completed:
            return False
        
        timeout = timeout or self.default_timeout
        
        for strategy in locator_strategies:
            locator_type = strategy.get("type", "css")
            locator_value = strategy.get("value", "")
            
            if not locator_value:
                continue
            
            try:
                print(f"🔍 Trying to fill {field_name} with {locator_type}: {locator_value}")
                
                # Create locator
                locator = self._create_playwright_locator(locator_type, locator_value)
                
                if locator:
                    # Wait for element
                    await locator.wait_for(state="visible", timeout=timeout)
                    
                    # Scroll into view if needed
                    try:
                        await locator.scroll_into_view_if_needed(timeout=5000)
                    except:
                        pass
                    
                    # Focus the element
                    await locator.focus()
                    await asyncio.sleep(0.3)
                    
                    # Clear field if requested
                    if clear_first:
                        await locator.clear()
                        await asyncio.sleep(0.2)
                    
                    # Type text with realistic typing speed
                    await locator.fill(text_value)
                    
                    # Verify the text was entered
                    actual_value = await locator.input_value()
                    if actual_value == text_value:
                        print(f"✅ Successfully filled {field_name} with: {text_value}")
                        return True
                    else:
                        print(f"⚠️ Text verification failed. Expected: {text_value}, Got: {actual_value}")
                        # Try alternative method
                        await locator.clear()
                        await locator.type(text_value, delay=50)  # Slower typing
                        
                        actual_value = await locator.input_value()
                        if actual_value == text_value:
                            print(f"✅ Successfully filled {field_name} with alternative method")
                            return True
                    
            except Exception as e:
                print(f"⚠️ Fill failed with {locator_type}: {str(e)}")
                continue
        
        print(f"❌ Failed to fill {field_name} with all strategies")
        return False
    
    async def wait_for_element(self, 
                              locator_strategies: List[Dict[str, str]], 
                              element_name: str = "element",
                              state: str = "visible",
                              timeout: int = None) -> bool:
        """Wait for element using multiple strategies"""
        if not self.setup_completed:
            return False
        
        timeout = timeout or self.default_timeout
        
        for strategy in locator_strategies:
            locator_type = strategy.get("type", "css")
            locator_value = strategy.get("value", "")
            
            if not locator_value:
                continue
            
            try:
                print(f"⏳ Waiting for {element_name} with {locator_type}: {locator_value}")
                
                locator = self._create_playwright_locator(locator_type, locator_value)
                
                if locator:
                    await locator.wait_for(state=state, timeout=timeout)
                    print(f"✅ Element {element_name} is {state}")
                    return True
                    
            except Exception as e:
                print(f"⚠️ Wait failed with {locator_type}: {str(e)}")
                continue
        
        print(f"❌ Element {element_name} not found in {state} state")
        return False
    
    async def scroll_page(self, direction: str = "down", pixels: int = 500) -> bool:
        """Scroll page in specified direction"""
        if not self.setup_completed:
            return False
        
        try:
            print(f"📜 Scrolling {direction} by {pixels} pixels")
            
            if direction.lower() == "down":
                await self.page.mouse.wheel(0, pixels)
            elif direction.lower() == "up":
                await self.page.mouse.wheel(0, -pixels)
            elif direction.lower() == "left":
                await self.page.mouse.wheel(-pixels, 0)
            elif direction.lower() == "right":
                await self.page.mouse.wheel(pixels, 0)
            
            await asyncio.sleep(0.5)  # Wait for scroll to complete
            print(f"✅ Scrolled {direction} successfully")
            return True
            
        except Exception as e:
            print(f"❌ Scroll failed: {str(e)}")
            return False
    
    async def take_screenshot(self, filename: str = None) -> bool:
        """Take screenshot for debugging"""
        if not self.setup_completed:
            return False
        
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            await self.page.screenshot(path=filename, full_page=True)
            print(f"📸 Screenshot saved: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Screenshot failed: {str(e)}")
            return False
    
    async def get_page_title(self) -> str:
        """Get current page title"""
        if not self.setup_completed:
            return ""
        
        try:
            title = await self.page.title()
            print(f"📄 Page title: {title}")
            return title
        except Exception as e:
            print(f"❌ Failed to get page title: {str(e)}")
            return ""
    
    async def wait_for_navigation(self, timeout: int = None) -> bool:
        """Wait for page navigation to complete"""
        if not self.setup_completed:
            return False
        
        timeout = timeout or self.default_timeout
        
        try:
            print("⏳ Waiting for navigation...")
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
            print("✅ Navigation completed")
            return True
        except Exception as e:
            print(f"❌ Navigation wait failed: {str(e)}")
            return False
    
    def _create_playwright_locator(self, locator_type: str, locator_value: str):
        """Create Playwright locator based on type"""
        try:
            if locator_type == "css":
                return self.page.locator(locator_value)
            elif locator_type == "xpath":
                return self.page.locator(f"xpath={locator_value}")
            elif locator_type == "text":
                return self.page.locator(f"text={locator_value}")
            elif locator_type == "id":
                return self.page.locator(f"#{locator_value}")
            elif locator_type == "name":
                return self.page.locator(f"[name='{locator_value}']")
            elif locator_type == "placeholder":
                return self.page.locator(f"[placeholder*='{locator_value}']")
            elif locator_type == "role":
                # Handle role-based locators
                if "[" in locator_value:
                    return self.page.locator(f"role={locator_value}")
                else:
                    return self.page.get_by_role(locator_value)
            else:
                # Default to CSS selector
                return self.page.locator(locator_value)
                
        except Exception as e:
            print(f"❌ Failed to create locator: {str(e)}")
            return None
    
    async def close_browser(self):
        """Clean browser shutdown"""
        await self._cleanup_browser()
    
    async def _cleanup_browser(self):
        """Internal cleanup method"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            self.setup_completed = False
            print("🧹 Browser cleanup completed")
            
        except Exception as e:
            print(f"⚠️ Cleanup warning: {str(e)}")

# Global instance
web_tools = GenericWebAutomationTools()