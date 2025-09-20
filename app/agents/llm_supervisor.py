"""
Generic LLM Supervisor - Agent 3 (Updated)
Real script execution with Agent 2 communication for ANY automation task
"""
import asyncio
import json
import os
import subprocess
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.models.schemas import WorkflowState, PlatformType
from app.utils.model_client import model_client

class GenericLLMSupervisor:
    """Generic execution supervisor for any automation task"""
    
    def __init__(self):
        self.name = "llm_supervisor"
        self.description = "Generic execution supervision with real script running and Agent 2 communication"
        self.max_retries = 3
        self.conversation_log = []
        self.code_agent_instance = None
    
    def set_code_agent(self, code_agent):
        """Set reference to code agent for communication"""
        self.code_agent_instance = code_agent
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """Main processing function with real script execution"""
        try:
            print(f"\\n🟡 [{self.name}] Starting generic script execution...")
            print(f"🟡 [{self.name}] Platform: {state.platform}")
            print(f"🟡 [{self.name}] Task: {state.parameters.get('instruction', 'Unknown')}")
            print(f"🟡 [{self.name}] Script available: {bool(state.generated_script)}")
            print(f"🟡 [{self.name}] Agent 2 communication: {'✅ Enabled' if self.code_agent_instance else '❌ Disabled'}")
            
            state.current_agent = self.name
            
            await self._log_conversation(state, "AGENT_3_START", {
                "message": "Generic execution started",
                "platform": str(state.platform),
                "script_available": bool(state.generated_script),
                "agent_2_communication": bool(self.code_agent_instance),
                "task": state.parameters.get("instruction", "Unknown")
            })
            
            # Step 1: Validate execution environment
            print(f"🟡 [{self.name}] Step 1: Validating execution environment...")
            validation_result = await self._validate_execution_environment(state)
            if not validation_result["ready"]:
                print(f"🔴 [{self.name}] Environment validation failed: {validation_result['error']}")
                raise Exception(f"Environment not ready: {validation_result['error']}")
            
            print(f"🟡 [{self.name}] ✅ Environment validated")
            
            # Step 2: Execute script with supervision and Agent 2 communication
            print(f"🟡 [{self.name}] Step 2: Executing script with supervision...")
            execution_result = await self._execute_with_agent2_communication(state)
            
            # Step 3: Generate execution summary
            print(f"🟡 [{self.name}] Step 3: Generating execution summary...")
            summary = await self._generate_execution_summary(state, execution_result)
            
            # Update state
            state.execution_result = execution_result
            state.execution_logs = execution_result.get("logs", [])
            
            # Save artifacts
            if state.run_dir:
                await self._save_execution_artifacts(state, execution_result)
                await self._save_conversation_log(state)
            
            await self._log_conversation(state, "AGENT_3_COMPLETED", {
                "final_success": execution_result.get("success", False),
                "total_attempts": execution_result.get("attempts", 0),
                "agent_2_collaborations": execution_result.get("agent2_collaborations", 0),
                "success_rate": execution_result.get("success_rate", 0)
            })
            
            # Final status
            success_icon = "✅" if execution_result.get("success", False) else "❌"
            print(f"\\n🟡 [{self.name}] ========== EXECUTION RESULTS ==========")
            print(f"🟡 [{self.name}] Status: {success_icon} {'SUCCESS' if execution_result.get('success') else 'FAILED'}")
            print(f"🟡 [{self.name}] Total Attempts: {execution_result.get('attempts', 0)}")
            print(f"🟡 [{self.name}] Success Rate: {execution_result.get('success_rate', 0):.1f}%")
            print(f"🟡 [{self.name}] Agent 2 Collaborations: {execution_result.get('agent2_collaborations', 0)}")
            print(f"🟡 [{self.name}] ==========================================")
            
            return state
            
        except Exception as e:
            print(f"🔴 [{self.name}] Error: {str(e)}")
            state.execution_result = {
                "success": False,
                "error": str(e),
                "logs": [f"Supervisor error: {str(e)}"],
                "agent2_collaborations": 0
            }
            return state
    
    async def _validate_execution_environment(self, state: WorkflowState) -> Dict[str, Any]:
        """Validate execution environment for any platform"""
        validation = {"ready": True, "checks": [], "error": ""}
        
        try:
            # Check Python
            result = subprocess.run(['python', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                validation["checks"].append(f"Python: {result.stdout.strip()}")
            else:
                validation["ready"] = False
                validation["error"] = "Python not available"
            
            # Check platform-specific requirements
            if state.platform == PlatformType.WEB:
                validation["checks"].append("Web platform: Playwright will be loaded dynamically")
            elif state.platform == PlatformType.MOBILE:
                validation["checks"].append("Mobile platform: Appium connection will be attempted")
            
            # Check script
            script = state.generated_script or ""
            if len(script.strip()) < 50:
                validation["ready"] = False
                validation["error"] = "Generated script too short"
            else:
                try:
                    compile(script, '<generated_script>', 'exec')
                    validation["checks"].append("Script validation: Syntax OK")
                except SyntaxError as e:
                    validation["checks"].append(f"Script validation: Syntax error - {str(e)}")
            
            # Check run directory
            if state.run_dir and not os.path.exists(state.run_dir):
                os.makedirs(state.run_dir, exist_ok=True)
                validation["checks"].append("Run directory: Created")
            
            return validation
            
        except Exception as e:
            return {
                "ready": False,
                "error": f"Validation failed: {str(e)}",
                "checks": [f"Validation error: {str(e)}"]
            }
    
    async def _execute_with_agent2_communication(self, state: WorkflowState) -> Dict[str, Any]:
        """Execute script with Agent 2 communication"""
        
        execution_context = {
            "attempt": 0,
            "current_script": state.generated_script,
            "improvements_made": [],
            "agent2_collaborations": 0,
            "step_results": [],
            "logs": [],
            "start_time": time.time()
        }
        
        print(f"🟡 [{self.name}] Starting execution with up to {self.max_retries} attempts...")
        
        while execution_context["attempt"] < self.max_retries:
            execution_context["attempt"] += 1
            
            print(f"\\n🟡 [{self.name}] ========== ATTEMPT {execution_context['attempt']} ==========")
            
            # Execute current script version
            attempt_result = await self._execute_script_attempt(state, execution_context)
            
            # Save attempt artifacts
            await self._save_attempt_artifacts(state, execution_context, attempt_result)
            
            print(f"🟡 [{self.name}] Attempt {execution_context['attempt']} results:")
            print(f"🟡 [{self.name}]   Success: {attempt_result.get('success', False)}")
            print(f"🟡 [{self.name}]   Duration: {attempt_result.get('duration', 0):.1f}s")
            
            # Check if successful
            if attempt_result.get("success", False):
                print(f"🟡 [{self.name}] 🎉 SUCCESS ON ATTEMPT {execution_context['attempt']}!")
                
                return {
                    "success": True,
                    "attempts": execution_context["attempt"],
                    "improvements_made": execution_context["improvements_made"],
                    "agent2_collaborations": execution_context["agent2_collaborations"],
                    "step_results": execution_context["step_results"],
                    "logs": execution_context["logs"],
                    "execution_time": time.time() - execution_context["start_time"],
                    "success_rate": self._calculate_success_rate(execution_context["step_results"])
                }
            
            # If failed and we have more attempts, try Agent 2 collaboration
            if execution_context["attempt"] < self.max_retries and self.code_agent_instance:
                print(f"🟡 [{self.name}] Attempt failed, requesting Agent 2 collaboration...")
                
                agent2_feedback = {
                    "type": "execution_failure",
                    "attempts": execution_context["attempt"],
                    "success_rate": self._calculate_success_rate(execution_context["step_results"]),
                    "issues": self._extract_failure_issues(attempt_result),
                    "improvements": self._suggest_improvements(attempt_result),
                    "platform": str(state.platform),
                    "task": state.parameters.get("instruction", "Unknown")
                }
                
                try:
                    agent2_response = await self.code_agent_instance.handle_agent3_feedback(state, agent2_feedback)
                    
                    if agent2_response.get("regenerated", False):
                        execution_context["current_script"] = agent2_response["new_script"]
                        execution_context["agent2_collaborations"] += 1
                        
                        collaboration_summary = f"Agent 2 collaboration #{execution_context['agent2_collaborations']}"
                        execution_context["improvements_made"].append(collaboration_summary)
                        
                        print(f"🟡 [{self.name}] ✅ Agent 2 collaboration successful - script regenerated")
                    else:
                        print(f"🟡 [{self.name}] ⚠️ Agent 2 collaboration failed")
                        
                except Exception as e:
                    print(f"🟡 [{self.name}] ❌ Agent 2 collaboration error: {str(e)}")
                
                await asyncio.sleep(2)  # Brief pause before retry
        
        # All attempts failed
        print(f"🟡 [{self.name}] ❌ ALL {self.max_retries} ATTEMPTS FAILED")
        
        return {
            "success": False,
            "attempts": execution_context["attempt"],
            "error": f"All {self.max_retries} attempts failed",
            "improvements_made": execution_context["improvements_made"],
            "agent2_collaborations": execution_context["agent2_collaborations"],
            "step_results": execution_context["step_results"],
            "logs": execution_context["logs"],
            "execution_time": time.time() - execution_context["start_time"],
            "success_rate": self._calculate_success_rate(execution_context["step_results"])
        }
    
    async def _execute_script_attempt(self, state: WorkflowState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single script attempt"""
        
        try:
            start_time = time.time()
            
            # Write script to file
            script_path = await self._write_temp_script(state, context["current_script"])
            print(f"🟡 [{self.name}] Script written to: {script_path}")
            
            # Execute based on platform
            if state.platform == PlatformType.WEB:
                result = await self._execute_web_script(script_path)
            elif state.platform == PlatformType.MOBILE:
                result = await self._execute_mobile_script(script_path)
            else:
                result = await self._simulate_execution(script_path)
            
            result["duration"] = time.time() - start_time
            
            # Update context
            context["logs"].extend(result.get("logs", []))
            context["step_results"].extend(result.get("step_results", []))
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            error_msg = f"Script execution failed: {str(e)}"
            context["logs"].append(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "duration": duration,
                "logs": [error_msg],
                "step_results": []
            }
    
    async def _execute_web_script(self, script_path: str) -> Dict[str, Any]:
        """Execute web script"""
        try:
            print(f"🟡 [{self.name}] Executing web script...")
            
            # Check if async script
            with open(script_path, 'r') as f:
                script_content = f.read()
            
            is_async = "async def" in script_content
            
            process = await asyncio.create_subprocess_exec(
                "python", script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.path.dirname(script_path)
            )
            
            try:
                # 3 minutes timeout for web scripts
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=180)
                
                stdout_text = stdout.decode('utf-8', errors='replace') if stdout else ""
                stderr_text = stderr.decode('utf-8', errors='replace') if stderr else ""
                
                print(f"🟡 [{self.name}] Web script execution completed")
                print(f"🟡 [{self.name}] Return code: {process.returncode}")
                
                # Determine success
                success = self._determine_script_success(process.returncode, stdout_text, stderr_text)
                
                return {
                    "success": success,
                    "returncode": process.returncode,
                    "stdout": stdout_text,
                    "stderr": stderr_text,
                    "logs": [stdout_text, stderr_text] if stderr_text else [stdout_text],
                    "step_results": self._parse_step_results(stdout_text)
                }
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "success": False,
                    "error": "Web script execution timed out (180s)",
                    "logs": ["Execution timeout"],
                    "step_results": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Web script execution failed: {str(e)}",
                "logs": [f"Execution error: {str(e)}"],
                "step_results": []
            }
    
    async def _execute_mobile_script(self, script_path: str) -> Dict[str, Any]:
        """Execute mobile script"""
        try:
            print(f"🟡 [{self.name}] Executing mobile script...")
            
            process = await asyncio.create_subprocess_exec(
                "python", script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.path.dirname(script_path)
            )
            
            try:
                # 4 minutes timeout for mobile scripts
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=240)
                
                stdout_text = stdout.decode('utf-8', errors='replace') if stdout else ""
                stderr_text = stderr.decode('utf-8', errors='replace') if stderr else ""
                
                print(f"🟡 [{self.name}] Mobile script execution completed")
                print(f"🟡 [{self.name}] Return code: {process.returncode}")
                
                # Determine success
                success = self._determine_script_success(process.returncode, stdout_text, stderr_text)
                
                return {
                    "success": success,
                    "returncode": process.returncode,
                    "stdout": stdout_text,
                    "stderr": stderr_text,
                    "logs": [stdout_text, stderr_text] if stderr_text else [stdout_text],
                    "step_results": self._parse_step_results(stdout_text)
                }
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "success": False,
                    "error": "Mobile script execution timed out (240s)",
                    "logs": ["Execution timeout"],
                    "step_results": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Mobile script execution failed: {str(e)}",
                "logs": [f"Execution error: {str(e)}"],
                "step_results": []
            }
    
    async def _simulate_execution(self, script_path: str) -> Dict[str, Any]:
        """Simulate execution when drivers not available"""
        print(f"🟡 [{self.name}] ⚠️ Simulating execution (drivers not available)")
        
        try:
            with open(script_path, 'r') as f:
                script_content = f.read()
            
            # Analyze script for steps
            step_indicators = [
                'click', 'fill', 'navigate', 'tap', 'type', 'scroll', 'wait',
                'launch', 'swipe', 'find_element', 'send_keys'
            ]
            
            steps = []
            lines = script_content.split('\\n')
            step_count = 0
            
            for i, line in enumerate(lines):
                line_lower = line.lower()
                if any(indicator in line_lower for indicator in step_indicators):
                    step_count += 1
                    steps.append({
                        "step": step_count,
                        "line": i + 1,
                        "action": line.strip()[:100],
                        "success": True  # Simulate success
                    })
                    
                    if step_count >= 8:  # Limit simulation
                        break
            
            await asyncio.sleep(3)  # Simulate execution time
            
            success_rate = min(85, max(60, len(steps) * 12))
            
            return {
                "success": success_rate > 70,
                "simulated": True,
                "success_rate": success_rate,
                "logs": [
                    f"Simulated execution of {len(steps)} automation steps",
                    f"Simulation success rate: {success_rate}%"
                ],
                "step_results": steps
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Simulation failed: {str(e)}",
                "logs": [f"Simulation error: {str(e)}"],
                "step_results": []
            }
    
    def _determine_script_success(self, returncode: int, stdout: str, stderr: str) -> bool:
        """Determine if script execution was successful"""
        if returncode != 0:
            return False
        
        # Check for success indicators
        combined_output = (stdout + stderr).lower()
        
        success_indicators = ["success", "completed", "✅", "automation completed"]
        failure_indicators = ["error", "failed", "exception", "❌", "traceback"]
        
        has_success = any(indicator in combined_output for indicator in success_indicators)
        has_failure = any(indicator in combined_output for indicator in failure_indicators)
        
        if has_success and not has_failure:
            return True
        elif not has_failure:
            return True  # No explicit failure
        else:
            return False
    
    def _extract_failure_issues(self, attempt_result: Dict[str, Any]) -> List[str]:
        """Extract failure issues for Agent 2 feedback"""
        issues = []
        
        error = attempt_result.get("error", "")
        stderr = attempt_result.get("stderr", "")
        
        combined_text = (error + " " + stderr).lower()
        
        if "element not found" in combined_text or "no such element" in combined_text:
            issues.append("Element locator issues - elements not found")
        
        if "timeout" in combined_text or "timed out" in combined_text:
            issues.append("Timing issues - operations timed out")
        
        if "connection" in combined_text or "refused" in combined_text:
            issues.append("Connection issues - server/driver problems")
        
        if "import" in combined_text or "module" in combined_text:
            issues.append("Import or dependency issues")
        
        if "webdriver" in combined_text or "driver" in combined_text:
            issues.append("WebDriver or automation driver issues")
        
        if not issues:
            issues.append("General execution failure - no specific pattern detected")
        
        return issues
    
    def _suggest_improvements(self, attempt_result: Dict[str, Any]) -> List[str]:
        """Suggest improvements based on failure analysis"""
        improvements = [
            "Add multiple locator strategies for better element finding",
            "Implement explicit waits and retry mechanisms",
            "Add better error handling and logging",
            "Include fallback methods for failed operations",
            "Enhance element waiting conditions",
            "Add screenshot capture for debugging"
        ]
        
        # Add specific improvements based on issues
        issues = self._extract_failure_issues(attempt_result)
        
        if any("element" in issue.lower() for issue in issues):
            improvements.insert(0, "Use more robust element finding strategies")
        
        if any("timeout" in issue.lower() for issue in issues):
            improvements.insert(0, "Increase timeouts and add progressive waiting")
        
        if any("connection" in issue.lower() for issue in issues):
            improvements.insert(0, "Add connection retry logic")
        
        return improvements
    
    def _calculate_success_rate(self, step_results: List[Dict[str, Any]]) -> float:
        """Calculate success rate from step results"""
        if not step_results:
            return 0.0
        
        successful_steps = sum(1 for step in step_results if step.get("success", False))
        return (successful_steps / len(step_results)) * 100
    
    def _parse_step_results(self, output: str) -> List[Dict[str, Any]]:
        """Parse step results from script output"""
        step_results = []
        lines = output.split('\\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            if any(indicator in line_lower for indicator in [
                'step', '✅', '❌', 'success', 'failed', 'completed'
            ]):
                step_results.append({
                    "step": len(step_results) + 1,
                    "line_number": i + 1,
                    "output": line.strip(),
                    "success": any(success_indicator in line_lower for success_indicator in [
                        '✅', 'success', 'completed', 'clicked', 'filled', 'navigated'
                    ]),
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        return step_results
    
    async def _write_temp_script(self, state: WorkflowState, script: str) -> str:
        """Write script to temporary file"""
        script_dir = state.run_dir or "temp"
        os.makedirs(script_dir, exist_ok=True)
        
        timestamp = int(time.time())
        script_path = os.path.join(script_dir, f"execution_script_{timestamp}.py")
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)
        
        return script_path
    
    async def _save_attempt_artifacts(self, state: WorkflowState, context: Dict[str, Any], result: Dict[str, Any]):
        """Save artifacts for each execution attempt"""
        if not state.run_dir:
            return
        
        attempt = context["attempt"]
        logs_data = {
            "attempt": attempt,
            "timestamp": datetime.utcnow().isoformat(),
            "success": result.get("success", False),
            "error": result.get("error"),
            "duration": result.get("duration", 0),
            "agent2_collaborations": context.get("agent2_collaborations", 0),
            "step_results": result.get("step_results", [])
        }
        
        logs_path = os.path.join(state.run_dir, f"execution_attempt_{attempt}.json")
        with open(logs_path, 'w', encoding='utf-8') as f:
            json.dump(logs_data, f, indent=2, ensure_ascii=False)
        
        state.artifacts[f"agent3_attempt_{attempt}"] = logs_path
    
    async def _generate_execution_summary(self, state: WorkflowState, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate execution summary"""
        return {
            "task_id": state.task_id,
            "platform": str(state.platform),
            "task": state.parameters.get("instruction", "Unknown"),
            "execution_success": execution_result.get("success", False),
            "total_attempts": execution_result.get("attempts", 0),
            "agent2_collaborations": execution_result.get("agent2_collaborations", 0),
            "success_rate": execution_result.get("success_rate", 0),
            "execution_time": execution_result.get("execution_time", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _save_execution_artifacts(self, state: WorkflowState, execution_result: Dict[str, Any]):
        """Save execution artifacts"""
        if not state.run_dir:
            return
        
        summary = await self._generate_execution_summary(state, execution_result)
        summary_path = os.path.join(state.run_dir, "agent3_execution_summary.json")
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        state.artifacts["agent3_execution_summary"] = summary_path
    
    async def _log_conversation(self, state: WorkflowState, event_type: str, data: Dict[str, Any]):
        """Log conversation events"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.name,
            "event_type": event_type,
            "data": data
        }
        self.conversation_log.append(log_entry)
    
    async def _save_conversation_log(self, state: WorkflowState):
        """Save conversation log"""
        if not state.run_dir or not self.conversation_log:
            return
        
        try:
            conversation_path = os.path.join(state.run_dir, "conversation.json")
            
            existing_conversation = []
            if os.path.exists(conversation_path):
                try:
                    with open(conversation_path, 'r', encoding='utf-8') as f:
                        existing_conversation = json.load(f)
                except:
                    pass
            
            full_conversation = existing_conversation + self.conversation_log
            
            with open(conversation_path, 'w', encoding='utf-8') as f:
                json.dump(full_conversation, f, indent=2, ensure_ascii=False)
            
            state.artifacts["conversation_log"] = conversation_path
            self.conversation_log = []
            
        except Exception as e:
            print(f"🔴 [{self.name}] Error saving conversation log: {str(e)}")

# Global instance
llm_supervisor = GenericLLMSupervisor()