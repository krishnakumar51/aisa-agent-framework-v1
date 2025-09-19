"""
LLM supervisor agent - Agent 3
Executes scripts and supervises automation with adaptive retry logic and artifact persistence
"""
import asyncio
import json
import os
from typing import Dict, Any, List
from datetime import datetime
from app.models.schemas import WorkflowState, PlatformType
from app.drivers.playwright_driver import playwright_driver
from app.drivers.appium_driver import appium_driver
from app.utils.model_client import model_client

class LLMSupervisor:
    """Agent responsible for script execution and supervision"""
    
    def __init__(self):
        self.name = "llm_supervisor"
        self.description = "Executes and supervises automation scripts with adaptive logic"
        self.max_retries = 3
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """Main processing function for LLM supervisor"""
        try:
            print(f"[{self.name}] Starting script execution...")
            state.current_agent = self.name
            
            # Step 1: Setup appropriate driver
            driver_ready = await self._setup_driver(state.platform)
            if not driver_ready:
                raise Exception("Failed to setup automation driver")
            
            # Step 2: Execute script with supervision
            execution_result = await self._execute_with_supervision(
                state.generated_script, state.platform, state.json_blueprint, state
            )
            
            state.execution_result = execution_result
            state.execution_logs = execution_result.get("logs", [])
            state.screenshots_taken = execution_result.get("screenshots", [])
            
            print(f"[{self.name}] Script execution completed")
            return state
            
        except Exception as e:
            print(f"[{self.name}] Error: {str(e)}")
            state.execution_result = {
                "success": False,
                "error": str(e),
                "logs": [f"Supervisor error: {str(e)}"]
            }
            return state
        finally:
            # Always cleanup drivers
            await self._cleanup_drivers()
    
    async def _setup_driver(self, platform: PlatformType) -> bool:
        """Setup appropriate automation driver with stealth mode"""
        try:
            if platform == PlatformType.WEB:
                # Enable stealth mode by default for web automation
                return await playwright_driver.setup(stealth_mode=True)
            elif platform == PlatformType.MOBILE:
                return appium_driver.setup_android()
            else:
                print(f"[{self.name}] Unknown platform, defaulting to mobile")
                return appium_driver.setup_android()
                
        except Exception as e:
            print(f"[{self.name}] Driver setup failed: {str(e)}")
            return False
    
    async def _execute_with_supervision(self, script: str, platform: PlatformType, 
                                      blueprint: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute script with LLM supervision and adaptive retries"""
        attempt = 0
        last_error = None
        current_script = script
        
        while attempt < self.max_retries:
            try:
                print(f"[{self.name}] Execution attempt {attempt + 1}")
                
                # Execute the script
                if platform == PlatformType.WEB:
                    result = await playwright_driver.execute_script(current_script)
                else:
                    result = await asyncio.to_thread(appium_driver.execute_script, current_script)
                
                # Persist supervisor artifacts after each attempt
                await self._persist_supervisor_artifacts(state, current_script, result, attempt)
                
                # Check if execution was successful
                if result.get("success", False):
                    return result
                
                # If failed, analyze and adapt
                adapted_script = await self._adapt_script_on_failure(
                    current_script, result, blueprint, attempt
                )
                
                if adapted_script != current_script:
                    current_script = adapted_script
                    print(f"[{self.name}] Script adapted for retry")
                    # Persist adapted script
                    await self._persist_supervisor_artifacts(state, adapted_script, result, attempt, is_adaptation=True)
                else:
                    print(f"[{self.name}] No adaptation possible, retrying original")
                
                last_error = result.get("error", "Unknown error")
                attempt += 1
                
                # Wait before retry
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                last_error = str(e)
                attempt += 1
                print(f"[{self.name}] Execution attempt {attempt} failed: {str(e)}")
                await asyncio.sleep(2 ** attempt)
        
        # All attempts failed
        final_result = {
            "success": False,
            "error": f"All {self.max_retries} attempts failed. Last error: {last_error}",
            "attempts": attempt,
            "logs": [f"Final failure after {attempt} attempts"]
        }
        
        # Persist final failure state
        await self._persist_supervisor_artifacts(state, current_script, final_result, attempt)
        return final_result
    
    async def _persist_supervisor_artifacts(self, state: WorkflowState, script: str, 
                                          result: Dict[str, Any], attempt: int, 
                                          is_adaptation: bool = False):
        """Persist supervisor artifacts: scripts, logs, and screenshots"""
        try:
            if not state.run_dir:
                return
            
            run_dir = state.run_dir
            os.makedirs(run_dir, exist_ok=True)
            
            # Create timestamp
            timestamp = datetime.utcnow().isoformat()
            
            # Version the supervisor script each attempt
            if is_adaptation:
                sup_name = f"agent-llm-supervisor.v{attempt+1}.adapted.py"
            else:
                sup_name = f"agent-llm-supervisor.v{attempt+1}.py"
            
            sup_path = os.path.join(run_dir, sup_name)
            
            # Create script with metadata header
            script_content = f'''"""
Generated/Adapted by Agent 3 - LLM Supervisor
Task ID: {state.task_id}
Attempt: {attempt + 1}
{'Adapted' if is_adaptation else 'Original'} Script
Timestamp: {timestamp}
Success: {result.get('success', False)}
"""

{script}
'''
            
            await self._write_text_file(sup_path, script_content)
            
            # Always update the latest pointer
            latest_path = os.path.join(run_dir, "agent-llm-supervisor.py")
            await self._write_text_file(latest_path, script_content)
            
            # Persist execution logs
            logs_data = {
                "attempt": attempt + 1,
                "timestamp": timestamp,
                "success": result.get("success", False),
                "error": result.get("error"),
                "logs": result.get("logs", []),
                "execution_results": result.get("results", [])
            }
            
            logs_path = os.path.join(run_dir, f"execution_logs.v{attempt+1}.json")
            await self._write_text_file(logs_path, json.dumps(logs_data, ensure_ascii=False, indent=2))
            
            # Latest logs pointer
            latest_logs_path = os.path.join(run_dir, "execution_logs.json")
            await self._write_text_file(latest_logs_path, json.dumps(logs_data, ensure_ascii=False, indent=2))
            
            # Persist screenshots
            screenshots = result.get("screenshots", [])
            if screenshots:
                screens_dir = os.path.join(run_dir, f"screenshots_v{attempt+1}")
                os.makedirs(screens_dir, exist_ok=True)
                
                for idx, img_bytes in enumerate(screenshots):
                    if isinstance(img_bytes, bytes) and len(img_bytes) > 0:
                        img_path = os.path.join(screens_dir, f"screenshot_{idx:03d}.png")
                        await self._write_binary_file(img_path, img_bytes)
                
                # Update state artifacts
                if "screenshot_dirs" not in state.artifacts:
                    state.artifacts["screenshot_dirs"] = []
                state.artifacts["screenshot_dirs"].append(screens_dir)
            
            # Update state artifacts
            if "agent3_script_versions" not in state.artifacts:
                state.artifacts["agent3_script_versions"] = []
            
            state.artifacts.update({
                "agent3_script_latest": latest_path,
                "agent3_logs_latest": latest_logs_path,
                "agent3_last_attempt": attempt + 1
            })
            
            state.artifacts["agent3_script_versions"].append(sup_path)
            
            print(f"[{self.name}] Artifacts persisted to: {run_dir}")
            
        except Exception as e:
            print(f"[{self.name}] Error persisting artifacts: {str(e)}")
    
    async def _write_text_file(self, path: str, content: str):
        """Write text content to file asynchronously"""
        def _write(p: str, c: str):
            with open(p, "w", encoding="utf-8") as f:
                f.write(c)
        await asyncio.to_thread(_write, path, content)
    
    async def _write_binary_file(self, path: str, content: bytes):
        """Write binary content to file asynchronously"""
        def _write(p: str, c: bytes):
            with open(p, "wb") as f:
                f.write(c)
        await asyncio.to_thread(_write, path, content)
    
    async def _adapt_script_on_failure(self, original_script: str, 
                                     execution_result: Dict[str, Any], 
                                     blueprint: Dict[str, Any], 
                                     attempt: int) -> str:
        """Use LLM to adapt script based on execution failure"""
        try:
            # Create adaptation prompt
            prompt = self._create_adaptation_prompt(
                original_script, execution_result, blueprint, attempt
            )
            
            # Get LLM suggestion for script adaptation
            response = await model_client.generate(prompt)
            
            # Extract adapted script
            adapted_script = self._extract_adapted_script(response)
            
            return adapted_script if adapted_script else original_script
            
        except Exception as e:
            print(f"[{self.name}] Script adaptation failed: {str(e)}")
            return original_script
    
    def _create_adaptation_prompt(self, script: str, execution_result: Dict[str, Any], 
                                blueprint: Dict[str, Any], attempt: int) -> str:
        """Create prompt for script adaptation"""
        error_info = execution_result.get("error", "Unknown error")
        logs = execution_result.get("logs", [])
        
        return f"""
The automation script failed during execution. Please analyze and adapt it.

ORIGINAL SCRIPT:
{script}

EXECUTION ERROR:
{error_info}

EXECUTION LOGS:
{logs[-5:] if logs else ["No logs available"]}

BLUEPRINT CONTEXT:
{blueprint.get("steps", [])}

ATTEMPT: {attempt + 1}

Common failure patterns:
1. Element not found - try alternative selectors
2. Timing issues - add more waits
3. UI state changes - adapt to new state

Provide an adapted script that addresses the specific failure.
Return ONLY the adapted script, no explanations.
"""
    
    def _extract_adapted_script(self, response: str) -> str:
        """Extract adapted script from LLM response"""
        try:
            # Look for code blocks
            if "```" in response:
                start = response.find("```")
                if "python" in response[start:start+20]:
                    start = response.find("```python") + len("```python")
                else:
                    start += 3
                
                end = response.find("```", start)
                if end > start:
                    return response[start:end].strip()
            
            # If no code blocks, return cleaned response
            return response.strip()
            
        except Exception as e:
            print(f"[{self.name}] Adapted script extraction failed: {str(e)}")
            return ""
    
    async def _validate_execution_state(self, platform: PlatformType) -> Dict[str, Any]:
        """Validate current execution state"""
        try:
            if platform == PlatformType.WEB:
                return await playwright_driver.get_page_info()
            else:
                return await asyncio.to_thread(appium_driver.get_device_info)
        except Exception as e:
            return {"error": f"State validation failed: {str(e)}"}
    
    async def _cleanup_drivers(self):
        """Cleanup all drivers"""
        try:
            # Cleanup Playwright
            await playwright_driver.cleanup()
            
            # Cleanup Appium
            await asyncio.to_thread(appium_driver.cleanup)
            
        except Exception as e:
            print(f"[{self.name}] Driver cleanup error: {str(e)}")
    
    async def _take_recovery_screenshot(self, platform: PlatformType) -> bytes:
        """Take screenshot for recovery analysis"""
        try:
            if platform == PlatformType.WEB:
                return await playwright_driver._take_screenshot()
            else:
                return await asyncio.to_thread(appium_driver._take_screenshot)
        except Exception as e:
            print(f"[{self.name}] Recovery screenshot failed: {str(e)}")
            return b""
    
    def _analyze_partial_success(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze partial success scenarios"""
        results = execution_result.get("results", [])
        if not results:
            return {"partial_success": False, "progress": 0.0}
        
        successful_steps = sum(1 for r in results if r.get("success", False))
        total_steps = len(results)
        progress = successful_steps / total_steps if total_steps > 0 else 0.0
        
        return {
            "partial_success": progress > 0.0,
            "progress": progress,
            "successful_steps": successful_steps,
            "total_steps": total_steps,
            "last_successful_step": max([r.get("step", 0) for r in results if r.get("success", False)], default=0)
        }

# Global LLM supervisor instance
llm_supervisor = LLMSupervisor()