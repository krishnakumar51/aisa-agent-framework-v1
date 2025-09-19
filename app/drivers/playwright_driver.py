"""
Playwright web automation driver with stealth mode optimization
"""
import asyncio
import json
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from app.config.settings import settings

class PlaywrightDriver:
    """Playwright web automation driver with stealth capabilities"""
    
    def __init__(self):
        """Initialize Playwright driver"""
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.screenshots: List[bytes] = []
        self.execution_logs: List[str] = []
    
    async def setup(self, headless: bool = None, stealth_mode: bool = True) -> bool:
        """Setup Playwright browser with optional stealth mode"""
        try:
            if headless is None:
                headless = settings.PLAYWRIGHT_HEADLESS
            
            self.playwright = await async_playwright().start()
            
            # Enhanced browser args for stealth (based on outlook.py patterns)
            browser_args = ['--no-sandbox', '--disable-setuid-sandbox']
            
            if stealth_mode:
                browser_args.extend([
                    '--no-first-run',
                    '--no-service-autorun', 
                    '--no-default-browser-check',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-default-apps',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--disable-hang-monitor',
                    '--disable-prompt-on-repost',
                    '--disable-sync',
                    '--disable-translate',
                    '--metrics-recording-only',
                    '--no-report-upload',
                    '--safebrowsing-disable-auto-update',
                    '--enable-automation=false',
                    '--disable-client-side-phishing-detection'
                ])
            
            # Launch browser
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=browser_args
            )
            
            # Create context with stealth settings
            context_options = {
                'viewport': {'width': 1366, 'height': 768},
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            if stealth_mode:
                context_options.update({
                    'locale': 'en-US',
                    'timezone_id': 'America/New_York',
                    'permissions': ['geolocation', 'notifications'],
                    'extra_http_headers': {
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-User': '?1',
                        'Sec-Fetch-Dest': 'document'
                    }
                })
            
            self.context = await self.browser.new_context(**context_options)
            
            # Create page
            self.page = await self.context.new_page()
            
            # Increase timeout
            self.page.set_default_timeout(60000)
            
            # Apply stealth script if enabled
            if stealth_mode:
                await self.page.add_init_script("""
                    // Remove webdriver property
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                        set: () => {},
                        configurable: true,
                        enumerable: false
                    });

                    // Override chrome property with realistic values
                    window.chrome = {
                        runtime: { onConnect: undefined, onMessage: undefined },
                        loadTimes: function() {
                            return {
                                requestTime: Date.now() / 1000 - Math.random() * 1000,
                                startLoadTime: Date.now() / 1000 - Math.random() * 1000,
                                commitLoadTime: Date.now() / 1000 - Math.random() * 1000,
                                finishDocumentLoadTime: Date.now() / 1000 - Math.random() * 1000,
                                finishLoadTime: Date.now() / 1000 - Math.random() * 1000,
                                firstPaintTime: Date.now() / 1000 - Math.random() * 1000,
                                firstPaintAfterLoadTime: 0,
                                navigationType: 'Other',
                                wasFetchedViaSpdy: false,
                                wasNpnNegotiated: false,
                                npnNegotiatedProtocol: 'unknown',
                                wasAlternateProtocolAvailable: false,
                                connectionInfo: 'unknown'
                            };
                        }
                    };

                    // Mock plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [
                            { 0: { type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", __proto__: MimeType.prototype }, description: "Portable Document Format", filename: "internal-pdf-viewer", length: 1, name: "Chrome PDF Plugin" },
                            { 0: { type: "application/pdf", suffixes: "pdf", description: "", __proto__: MimeType.prototype }, description: "", filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", length: 1, name: "Chrome PDF Viewer" }
                        ],
                        configurable: true,
                        enumerable: false
                    });

                    // Mock languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en'],
                        configurable: true,
                        enumerable: false
                    });

                    // Override permissions query
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );

                    // Add connection info
                    Object.defineProperty(navigator, 'connection', {
                        get: () => ({ effectiveType: '4g', rtt: 50, downlink: 10, saveData: false }),
                        configurable: true,
                        enumerable: false
                    });

                    // Mock hardware
                    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 4, configurable: true, enumerable: false });
                    Object.defineProperty(navigator, 'deviceMemory', { get: () => 8, configurable: true, enumerable: false });

                    // Remove automation traces
                    delete navigator.__proto__.webdriver;
                """)
            
            # Setup page event handlers
            self.page.on("dialog", self._handle_dialog)
            self.page.on("pageerror", self._handle_page_error)
            
            self._log("Playwright browser setup completed" + (" with stealth mode" if stealth_mode else ""))
            return True
        
        except Exception as e:
            self._log(f"Browser setup failed: {str(e)}")
            return False
    
    async def execute_script(self, script: str) -> Dict[str, Any]:
        """Execute automation script"""
        try:
            if not self.page:
                raise Exception("Browser not initialized")
            
            self._log("Starting script execution")
            
            # Parse script commands
            commands = self._parse_script(script)
            results = []
            
            for i, command in enumerate(commands):
                try:
                    result = await self._execute_command(command)
                    results.append({
                        "step": i + 1,
                        "command": command,
                        "success": True,
                        "result": result
                    })
                    
                    # Take screenshot after each step
                    screenshot = await self._take_screenshot()
                    self.screenshots.append(screenshot)
                    
                    # Add small delay between actions
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self._log(f"Command failed: {str(e)}")
                    results.append({
                        "step": i + 1,
                        "command": command,
                        "success": False,
                        "error": str(e)
                    })
                    break
            
            return {
                "success": all(r["success"] for r in results),
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
            
            # Parse different command types
            if line.startswith('navigate'):
                url = line.split('navigate')[1].strip().strip('"\'')
                commands.append({"action": "navigate", "url": url})
            
            elif line.startswith('click'):
                selector = line.split('click')[1].strip().strip('"\'')
                commands.append({"action": "click", "selector": selector})
            
            elif line.startswith('fill'):
                parts = line.split('fill')[1].strip().split(' ', 1)
                selector = parts[0].strip('"\'')
                value = parts[1].strip('"\'') if len(parts) > 1 else ""
                commands.append({"action": "fill", "selector": selector, "value": value})
            
            elif line.startswith('wait'):
                timeout = int(line.split('wait')[1].strip()) if line.split('wait')[1].strip().isdigit() else 3000
                commands.append({"action": "wait", "timeout": timeout})
            
            elif line.startswith('screenshot'):
                commands.append({"action": "screenshot"})
        
        return commands
    
    async def _execute_command(self, command: Dict[str, Any]) -> Any:
        """Execute individual command with enhanced element finding"""
        action = command["action"]
        
        if action == "navigate":
            await self.page.goto(command["url"], wait_until="domcontentloaded")
            self._log(f"Navigated to: {command['url']}")
            return {"url": self.page.url}
        
        elif action == "click":
            element = await self._find_element_robust(command["selector"])
            if element:
                await element.scroll_into_view_if_needed()
                await asyncio.sleep(0.5)  # Wait after scroll
                await element.click()
                self._log(f"Clicked: {command['selector']}")
                return {"clicked": True}
            else:
                raise Exception(f"Element not found: {command['selector']}")
        
        elif action == "fill":
            element = await self._find_element_robust(command["selector"])
            if element:
                await element.scroll_into_view_if_needed()
                await element.click()
                await asyncio.sleep(0.3)
                await element.fill("")
                await asyncio.sleep(0.2)
                await element.type(command["value"], delay=50)  # Type with delay
                self._log(f"Filled {command['selector']} with: {command['value']}")
                return {"filled": True}
            else:
                raise Exception(f"Element not found: {command['selector']}")
        
        elif action == "wait":
            await self.page.wait_for_timeout(command["timeout"])
            self._log(f"Waited: {command['timeout']}ms")
            return {"waited": command["timeout"]}
        
        elif action == "screenshot":
            screenshot = await self._take_screenshot()
            self._log("Screenshot taken")
            return {"screenshot": True}
        
        else:
            raise Exception(f"Unknown action: {action}")
    
    async def _find_element_robust(self, selector: str):
        """Find element with multiple strategies (based on outlook.py patterns)"""
        strategies = [
            selector,  # Original selector
            f"[aria-label*='{selector}' i]",  # Aria label contains
            f"[placeholder*='{selector}' i]",  # Placeholder contains
            f":text('{selector}')",  # Text content
            f"button:has-text('{selector}')",  # Button with text
            f"input[name*='{selector}' i]",  # Input name contains
        ]
        
        for strategy in strategies:
            try:
                element = await self.page.wait_for_selector(strategy, timeout=5000, state="visible")
                if element:
                    return element
            except:
                continue
        
        return None
    
    async def _take_screenshot(self) -> bytes:
        """Take page screenshot"""
        if self.page:
            return await self.page.screenshot(type="png", full_page=True)
        return b""
    
    async def _handle_dialog(self, dialog):
        """Handle browser dialogs"""
        self._log(f"Dialog appeared: {dialog.message}")
        await dialog.accept()
    
    async def _handle_page_error(self, error):
        """Handle page errors"""
        self._log(f"Page error: {str(error)}")
    
    def _log(self, message: str):
        """Add log message"""
        self.execution_logs.append(message)
        print(f"[Playwright] {message}")
    
    async def cleanup(self):
        """Cleanup browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            self._log("Browser cleanup completed")
        except Exception as e:
            self._log(f"Cleanup error: {str(e)}")
    
    async def get_page_info(self) -> Dict[str, Any]:
        """Get current page information"""
        if not self.page:
            return {}
        
        try:
            return {
                "url": self.page.url,
                "title": await self.page.title(),
                "screenshot": await self._take_screenshot()
            }
        except Exception as e:
            self._log(f"Error getting page info: {str(e)}")
            return {}

# Global Playwright driver instance  
playwright_driver = PlaywrightDriver()