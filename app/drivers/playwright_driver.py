"""
Web Automation Driver
Production Playwright driver for web automation with robust error handling
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

# Playwright imports with fallback
try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext, ElementHandle
    PLAYWRIGHT_AVAILABLE = True
    print("✅ Playwright available for web automation")
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not available")
    # Create fallback classes
    class Browser: pass
    class Page: pass
    class BrowserContext: pass
    class ElementHandle: pass

logger = logging.getLogger(__name__)

class WebAutomationDriver:
    """
    Production web automation driver using Playwright.
    Handles browser management, page interactions, and error recovery.
    """
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.driver_available = PLAYWRIGHT_AVAILABLE
        self.default_timeout = 30000
        self.retry_attempts = 3
        self.setup_completed = False
        logger.info(f"🌐 Web Automation Driver initialized - Available: {self.driver_available}")
    
    async def initialize_browser(
        self,
        browser_type: str = "chromium",
        headless: bool = False,
        viewport: Dict[str, int] = None
    ) -> Dict[str, Any]:
        """Initialize browser with specified configuration"""
        
        if not self.driver_available:
            return {
                "success": False,
                "error": "Playwright not available"
            }
        
        try:
            self.playwright = await async_playwright().start()
            
            # Browser selection
            if browser_type == "firefox":
                browser_launcher = self.playwright.firefox
            elif browser_type == "webkit":
                browser_launcher = self.playwright.webkit
            else:
                browser_launcher = self.playwright.chromium
            
            # Launch browser
            self.browser = await browser_launcher.launch(
                headless=headless,
                args=['--no-sandbox', '--disable-setuid-sandbox'] if not headless else []
            )
            
            # Create context
            context_options = {}
            if viewport:
                context_options["viewport"] = viewport
            else:
                context_options["viewport"] = {"width": 1280, "height": 800}
            
            self.context = await self.browser.new_context(**context_options)
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set default timeout
            self.page.set_default_timeout(self.default_timeout)
            
            self.setup_completed = True
            
            result = {
                "success": True,
                "browser_type": browser_type,
                "headless": headless,
                "viewport": context_options.get("viewport"),
                "initialized_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Browser initialized: {browser_type} ({'headless' if headless else 'headed'})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Browser initialization failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def navigate_to_url(self, url: str, wait_until: str = "domcontentloaded") -> Dict[str, Any]:
        """Navigate to specified URL"""
        
        if not self.setup_completed:
            return {
                "success": False,
                "error": "Browser not initialized"
            }
        
        try:
            response = await self.page.goto(url, wait_until=wait_until)
            
            result = {
                "success": True,
                "url": url,
                "status_code": response.status if response else None,
                "wait_until": wait_until,
                "navigated_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Navigated to: {url}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Navigation failed to {url}: {str(e)}")
            return {
                "success": False,
                "url": url,
                "error": str(e)
            }
    
    async def wait_for_element(self, selector: str, timeout: int = None) -> Dict[str, Any]:
        """Wait for element to be visible"""
        
        if not self.setup_completed:
            return {
                "success": False,
                "error": "Browser not initialized"
            }
        
        try:
            element = await self.page.wait_for_selector(
                selector,
                timeout=timeout or self.default_timeout
            )
            
            if element:
                # Get element information
                is_visible = await element.is_visible()
                is_enabled = await element.is_enabled()
                
                result = {
                    "success": True,
                    "selector": selector,
                    "element_found": True,
                    "is_visible": is_visible,
                    "is_enabled": is_enabled,
                    "waited_at": datetime.now().isoformat()
                }
                
                logger.info(f"✅ Element found: {selector}")
                return result
            else:
                return {
                    "success": False,
                    "selector": selector,
                    "error": "Element not found within timeout"
                }
                
        except Exception as e:
            logger.error(f"❌ Wait for element failed {selector}: {str(e)}")
            return {
                "success": False,
                "selector": selector,
                "error": str(e)
            }
    
    async def click_element(self, selector: str, wait_first: bool = True) -> Dict[str, Any]:
        """Click on element"""
        
        if not self.setup_completed:
            return {
                "success": False,
                "error": "Browser not initialized"
            }
        
        try:
            # Wait for element if requested
            if wait_first:
                wait_result = await self.wait_for_element(selector)
                if not wait_result["success"]:
                    return wait_result
            
            # Click element
            await self.page.click(selector)
            
            result = {
                "success": True,
                "action": "click",
                "selector": selector,
                "clicked_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Clicked element: {selector}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Click failed on {selector}: {str(e)}")
            return {
                "success": False,
                "action": "click",
                "selector": selector,
                "error": str(e)
            }
    
    async def fill_input(self, selector: str, value: str, clear_first: bool = True) -> Dict[str, Any]:
        """Fill input field with value"""
        
        if not self.setup_completed:
            return {
                "success": False,
                "error": "Browser not initialized"
            }
        
        try:
            # Wait for element
            wait_result = await self.wait_for_element(selector)
            if not wait_result["success"]:
                return wait_result
            
            # Clear field if requested
            if clear_first:
                await self.page.fill(selector, "")
            
            # Fill with value
            await self.page.fill(selector, value)
            
            result = {
                "success": True,
                "action": "fill",
                "selector": selector,
                "value_length": len(value),
                "filled_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Filled input: {selector}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Fill input failed on {selector}: {str(e)}")
            return {
                "success": False,
                "action": "fill",
                "selector": selector,
                "error": str(e)
            }
    
    async def get_element_text(self, selector: str) -> Dict[str, Any]:
        """Get text content of element"""
        
        if not self.setup_completed:
            return {
                "success": False,
                "error": "Browser not initialized"
            }
        
        try:
            # Wait for element
            wait_result = await self.wait_for_element(selector)
            if not wait_result["success"]:
                return wait_result
            
            # Get text
            text = await self.page.text_content(selector)
            
            result = {
                "success": True,
                "action": "get_text",
                "selector": selector,
                "text": text or "",
                "text_length": len(text) if text else 0,
                "retrieved_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Retrieved text from: {selector}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Get text failed on {selector}: {str(e)}")
            return {
                "success": False,
                "action": "get_text",
                "selector": selector,
                "error": str(e)
            }
    
    async def wait_for_page_load(self, state: str = "networkidle") -> Dict[str, Any]:
        """Wait for page to reach specified load state"""
        
        if not self.setup_completed:
            return {
                "success": False,
                "error": "Browser not initialized"
            }
        
        try:
            await self.page.wait_for_load_state(state)
            
            result = {
                "success": True,
                "action": "wait_for_load_state",
                "state": state,
                "completed_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Page load state reached: {state}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Wait for page load failed: {str(e)}")
            return {
                "success": False,
                "action": "wait_for_load_state",
                "state": state,
                "error": str(e)
            }
    
    async def take_screenshot(self, filepath: str = None, full_page: bool = False) -> Dict[str, Any]:
        """Take screenshot of current page"""
        
        if not self.setup_completed:
            return {
                "success": False,
                "error": "Browser not initialized"
            }
        
        try:
            if not filepath:
                filepath = f"screenshot_{int(datetime.now().timestamp())}.png"
            
            screenshot_bytes = await self.page.screenshot(
                path=filepath,
                full_page=full_page
            )
            
            result = {
                "success": True,
                "action": "screenshot",
                "filepath": filepath,
                "full_page": full_page,
                "size_bytes": len(screenshot_bytes),
                "taken_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Screenshot saved: {filepath}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Screenshot failed: {str(e)}")
            return {
                "success": False,
                "action": "screenshot",
                "error": str(e)
            }
    
    async def execute_javascript(self, script: str) -> Dict[str, Any]:
        """Execute JavaScript on the page"""
        
        if not self.setup_completed:
            return {
                "success": False,
                "error": "Browser not initialized"
            }
        
        try:
            result_data = await self.page.evaluate(script)
            
            result = {
                "success": True,
                "action": "javascript",
                "script": script[:100] + "..." if len(script) > 100 else script,
                "result": result_data,
                "executed_at": datetime.now().isoformat()
            }
            
            logger.info("✅ JavaScript executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ JavaScript execution failed: {str(e)}")
            return {
                "success": False,
                "action": "javascript",
                "script": script[:100] + "..." if len(script) > 100 else script,
                "error": str(e)
            }
    
    async def get_page_info(self) -> Dict[str, Any]:
        """Get current page information"""
        
        if not self.setup_completed:
            return {
                "success": False,
                "error": "Browser not initialized"
            }
        
        try:
            url = self.page.url
            title = await self.page.title()
            
            result = {
                "success": True,
                "url": url,
                "title": title,
                "retrieved_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Page info retrieved: {title}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Get page info failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close_browser(self) -> Dict[str, Any]:
        """Close browser and cleanup"""
        
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
            
            result = {
                "success": True,
                "action": "close_browser",
                "closed_at": datetime.now().isoformat()
            }
            
            logger.info("✅ Browser closed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Browser close failed: {str(e)}")
            return {
                "success": False,
                "action": "close_browser",
                "error": str(e)
            }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get driver capabilities"""
        return {
            "driver_available": self.driver_available,
            "setup_completed": self.setup_completed,
            "supported_browsers": ["chromium", "firefox", "webkit"] if self.driver_available else [],
            "supported_actions": [
                "navigate", "click", "fill", "get_text", "wait_for_element",
                "screenshot", "javascript", "page_info"
            ] if self.driver_available else [],
            "default_timeout": self.default_timeout,
            "retry_attempts": self.retry_attempts
        }

# Global web driver instance
_web_driver = None

async def get_web_driver() -> WebAutomationDriver:
    """Get global web driver instance"""
    global _web_driver
    if _web_driver is None:
        _web_driver = WebAutomationDriver()
    return _web_driver

if __name__ == "__main__":
    # Test web automation driver
    async def test_web_driver():
        print("🧪 Testing Web Automation Driver...")
        
        driver = WebAutomationDriver()
        
        # Test capabilities
        capabilities = driver.get_capabilities()
        print(f"✅ Driver capabilities: {capabilities['driver_available']}")
        
        if capabilities["driver_available"]:
            # Test browser initialization
            init_result = await driver.initialize_browser("chromium", True)
            print(f"✅ Browser initialization: {init_result['success']}")
            
            if init_result["success"]:
                # Test navigation
                nav_result = await driver.navigate_to_url("https://example.com")
                print(f"✅ Navigation: {nav_result['success']}")
                
                # Test page info
                info_result = await driver.get_page_info()
                print(f"✅ Page info: {info_result.get('title', 'No title')}")
                
                # Test screenshot
                screenshot_result = await driver.take_screenshot("test_screenshot.png")
                print(f"✅ Screenshot: {screenshot_result['success']}")
                
                # Close browser
                close_result = await driver.close_browser()
                print(f"✅ Browser close: {close_result['success']}")
        
        print("🎉 Web Automation Driver test completed!")
    
    import asyncio
    asyncio.run(test_web_driver())