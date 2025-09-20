"""
Generic Code Agent - Agent 2 (Updated)
Platform-generic script generation using reusable automation tools
"""
import asyncio
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.models.schemas import WorkflowState, PlatformType
from app.utils.model_client import model_client

class GenericCodeAgent:
    """Generic code generation agent for any automation task"""
    
    def __init__(self):
        self.name = "code_agent"
        self.description = "Generic code generation with reusable automation tools"
        self.conversation_log = []
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """Main processing function for any automation task"""
        try:
            print(f"\\n🟢 [{self.name}] Starting generic code generation...")
            print(f"🟢 [{self.name}] Blueprint available: {bool(state.json_blueprint)}")
            print(f"🟢 [{self.name}] Platform override: {state.parameters.get('platform', 'auto-detect')}")
            print(f"🟢 [{self.name}] Task: {state.parameters.get('instruction', 'Unknown')}")
            
            state.current_agent = self.name
            
            await self._log_conversation(state, "AGENT_2_START", {
                "message": "Generic code generation started",
                "blueprint_available": bool(state.json_blueprint),
                "blueprint_confidence": state.json_blueprint.get("confidence", 0.0) if state.json_blueprint else 0.0,
                "task_instruction": state.parameters.get("instruction", "Unknown")
            })
            
            # Step 1: Detect platform
            print(f"🟢 [{self.name}] Step 1: Platform detection...")
            platform = await self._detect_platform_generic(state)
            state.platform = platform
            print(f"🟢 [{self.name}] ✅ Platform: {platform}")
            
            # Step 2: Generate generic automation script
            print(f"🟢 [{self.name}] Step 2: Generating automation script...")
            script = await self._generate_generic_script(state)
            state.generated_script = script
            state.script_language = "python"
            
            print(f"🟢 [{self.name}] ✅ Script generated: {len(script)} characters")
            
            # Step 3: Save script artifact
            if state.run_dir:
                script_path = await self._save_script_artifact(state, script, 1, "initial_generation")
                state.artifacts["agent2_script_path"] = script_path
                state.artifacts["agent2_script_version"] = 1
                print(f"🟢 [{self.name}] ✅ Script saved to: {script_path}")
            
            await self._log_conversation(state, "AGENT_2_COMPLETED", {
                "script_length": len(script),
                "platform": str(platform),
                "script_type": self._analyze_script_type(script)
            })
            
            await self._save_conversation_log(state)
            print(f"🟢 [{self.name}] ✅ Code generation completed")
            return state
            
        except Exception as e:
            await self._log_conversation(state, "AGENT_2_ERROR", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            
            print(f"🔴 [{self.name}] Error: {str(e)}")
            state.generated_script = f"# Code generation error: {str(e)}"
            state.platform = PlatformType.UNKNOWN
            return state
    
    async def handle_agent3_feedback(self, state: WorkflowState, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Handle feedback from Agent 3 and regenerate script if needed"""
        try:
            print(f"🟢 [{self.name}] 🤝 Received feedback from Agent 3...")
            print(f"🟢 [{self.name}] Feedback type: {feedback.get('type', 'unknown')}")
            print(f"🟢 [{self.name}] Issues: {len(feedback.get('issues', []))}")
            print(f"🟢 [{self.name}] Improvements: {len(feedback.get('improvements', []))}")
            
            await self._log_conversation(state, "AGENT_3_FEEDBACK_RECEIVED", {
                "feedback_type": feedback.get("type", "unknown"),
                "issues_count": len(feedback.get("issues", [])),
                "improvements_count": len(feedback.get("improvements", [])),
                "success_rate": feedback.get("success_rate", 0)
            })
            
            # Generate improved script
            print(f"🟢 [{self.name}] Generating improved script...")
            improved_script = await self._regenerate_script_with_feedback(state, feedback)
            
            if improved_script and improved_script != state.generated_script:
                # Update script
                state.generated_script = improved_script
                
                # Save new version
                if state.run_dir:
                    current_version = state.artifacts.get("agent2_script_version", 1)
                    new_version = current_version + 1
                    
                    script_path = await self._save_script_artifact(
                        state, improved_script, new_version, "agent3_feedback"
                    )
                    state.artifacts[f"agent2_script_v{new_version}"] = script_path
                    state.artifacts["agent2_script_version"] = new_version
                    state.artifacts["agent2_script_latest"] = script_path
                    
                    print(f"🟢 [{self.name}] ✅ Improved script saved as version {new_version}")
                
                await self._log_conversation(state, "SCRIPT_REGENERATED", {
                    "new_version": new_version,
                    "improvements_applied": len(feedback.get("improvements", []))
                })
                
                return {
                    "regenerated": True,
                    "new_script": improved_script,
                    "improvements_applied": len(feedback.get("improvements", [])),
                    "version": new_version
                }
            else:
                return {
                    "regenerated": False,
                    "reason": "No significant improvements possible"
                }
                
        except Exception as e:
            print(f"🔴 [{self.name}] Feedback handling error: {str(e)}")
            return {
                "regenerated": False,
                "error": str(e)
            }
    
    async def _detect_platform_generic(self, state: WorkflowState) -> PlatformType:
        """Generic platform detection"""
        
        # Check for explicit override
        override = state.parameters.get("platform")
        if isinstance(override, str):
            override_clean = override.lower().strip()
            if override_clean == "web":
                print(f"🟢 [{self.name}] Platform override: WEB")
                return PlatformType.WEB
            elif override_clean == "mobile":
                print(f"🟢 [{self.name}] Platform override: MOBILE")
                return PlatformType.MOBILE
        
        # Use blueprint if available
        blueprint = state.json_blueprint or {}
        if "platform" in blueprint:
            bp_platform = blueprint["platform"].lower()
            if bp_platform == "web":
                print(f"🟢 [{self.name}] Platform from blueprint: WEB")
                return PlatformType.WEB
            elif bp_platform == "mobile":
                print(f"🟢 [{self.name}] Platform from blueprint: MOBILE")
                return PlatformType.MOBILE
        
        # Analyze instruction for platform hints
        instruction = state.parameters.get("instruction", "").lower()
        
        web_indicators = ["website", "browser", "url", "web", "page", "link", "http", "www"]
        mobile_indicators = ["app", "mobile", "phone", "device", "android", "ios", "tap", "swipe"]
        
        web_score = sum(1 for indicator in web_indicators if indicator in instruction)
        mobile_score = sum(1 for indicator in mobile_indicators if indicator in instruction)
        
        print(f"🟢 [{self.name}] Platform analysis - Web: {web_score}, Mobile: {mobile_score}")
        
        if mobile_score > web_score:
            print(f"🟢 [{self.name}] Platform from analysis: MOBILE")
            return PlatformType.MOBILE
        elif web_score > mobile_score:
            print(f"🟢 [{self.name}] Platform from analysis: WEB")
            return PlatformType.WEB
        else:
            # Default to web for generic tasks
            print(f"🟢 [{self.name}] Platform unclear, defaulting to: WEB")
            return PlatformType.WEB
    
    async def _generate_generic_script(self, state: WorkflowState) -> str:
        """Generate generic automation script"""
        try:
            if state.platform == PlatformType.MOBILE:
                return await self._generate_generic_mobile_script(state)
            elif state.platform == PlatformType.WEB:
                return await self._generate_generic_web_script(state)
            else:
                return "# Platform not supported for generic automation"
                
        except Exception as e:
            print(f"🔴 [{self.name}] Script generation failed: {str(e)}")
            return f"# Script generation failed: {str(e)}"
    
    async def _generate_generic_mobile_script(self, state: WorkflowState) -> str:
        """Generate generic mobile automation script"""
        
        blueprint = state.json_blueprint or {}
        parameters = state.parameters or {}
        
        workflow_name = blueprint.get("workflow_name", "mobile_automation")
        steps = blueprint.get("steps", [])
        dynamic_inputs = blueprint.get("dynamic_inputs", [])
        user_instruction = parameters.get("instruction", "Mobile automation task")
        user_data = {k: v for k, v in parameters.items() if k not in ["instruction", "platform"]}
        
        script_lines = [
            f'"""',
            f'Generic Mobile Automation Script',
            f'Generated for: {user_instruction}',
            f'Workflow: {workflow_name}',
            f'Platform: Mobile (Appium)',
            f'Steps: {len(steps)}',
            f'Generated at: {datetime.utcnow().isoformat()}',
            f'"""',
            f'',
            f'import asyncio',
            f'import json',
            f'import time',
            f'from typing import Dict, Any',
            f'',
            f'# Import generic mobile automation tools',
            f'from app.tools.mobile_tools import GenericMobileAutomationTools',
            f'',
            f'def execute_mobile_automation():',
            f'    """Execute generic mobile automation"""',
            f'    ',
            f'    # Task configuration',
            f'    task_config = {{',
            f'        "instruction": "{user_instruction}",',
            f'        "workflow": "{workflow_name}",',
            f'        "user_data": {json.dumps(user_data, indent=8)},',
            f'        "dynamic_inputs": {json.dumps(dynamic_inputs, indent=8)}',
            f'    }}',
            f'    ',
            f'    results = []',
            f'    ',
            f'    try:',
            f'        print("🔵 Starting mobile automation...")',
            f'        print("📋 Task:", (task_config.get("instruction", "")[:100]))',
            f'        ',
            f'        # Initialize mobile tools',
            f'        tools = GenericMobileAutomationTools()',
            f'        ',
            f'        # Setup driver',
            f'        print("🔧 Setting up mobile driver...")',
            f'        if not tools.setup_driver():',
            f'            return {{"success": False, "error": "Mobile driver setup failed", "results": results}}',
            f'        ',
            f'        print("✅ Mobile driver ready")',
            f'        results.append({{"step": "setup", "action": "driver_setup", "success": True}})',
            f'        ',
        ]
        
        # Add automation steps from blueprint
        for i, step in enumerate(steps[:10], 1):  # Limit steps for safety
            step_num = i + 1
            action = step.get("action", "unknown")
            target = step.get("target", "element")
            locator = step.get("locator", {})
            value = step.get("value", "")
            
            script_lines.extend([
                f'        # Step {step_num}: {action.title()} - {target}',
                f'        print("\\n🔵 Step {step_num}: {action.title()} - {target}")',
                f'        ',
            ])
            
            if action == "launch":
                package = step.get("package", "com.example.app")
                script_lines.extend([
                    f'        # Launch application',
                    f'        if tools.launch_app("{package}"):',
                    f'            results.append({{"step": {step_num}, "action": "launch", "success": True}})',
                    f'        else:',
                    f'            results.append({{"step": {step_num}, "action": "launch", "success": False}})',
                ])
            
            elif action in ["click", "tap"]:
                locator_strategies = self._create_mobile_locator_strategies(locator, target)
                script_lines.extend([
                    f'        # Tap element: {target}',
                    f'        locator_strategies = {json.dumps(locator_strategies, indent=8)}',
                    f'        if tools.tap_element(locator_strategies, "{target}"):',
                    f'            results.append({{"step": {step_num}, "action": "tap", "target": "{target}", "success": True}})',
                    f'        else:',
                    f'            results.append({{"step": {step_num}, "action": "tap", "target": "{target}", "success": False}})',
                ])
            
            elif action in ["fill", "type"]:
                locator_strategies = self._create_mobile_locator_strategies(locator, target)
                fill_value = self._resolve_dynamic_value(value, user_data)
                
                script_lines.extend([
                    f'        # Fill text field: {target}',
                    f'        locator_strategies = {json.dumps(locator_strategies, indent=8)}',
                    f'        fill_value = "{fill_value}"',
                    f'        if tools.fill_text_field(locator_strategies, fill_value, "{target}"):',
                    f'            results.append({{"step": {step_num}, "action": "fill", "target": "{target}", "success": True, "value": fill_value}})',
                    f'        else:',
                    f'            results.append({{"step": {step_num}, "action": "fill", "target": "{target}", "success": False}})',
                ])
            
            elif action in ["scroll", "swipe"]:
                direction = step.get("direction", "down")
                script_lines.extend([
                    f'        # Swipe screen: {direction}',
                    f'        if tools.swipe_screen("{direction}"):',
                    f'            results.append({{"step": {step_num}, "action": "swipe", "direction": "{direction}", "success": True}})',
                    f'        else:',
                    f'            results.append({{"step": {step_num}, "action": "swipe", "direction": "{direction}", "success": False}})',
                ])
            
            elif action == "wait":
                timeout = step.get("timeout", 5000)
                script_lines.extend([
                    f'        # Wait for element/condition',
                    f'        time.sleep({timeout / 1000})',
                    f'        results.append({{"step": {step_num}, "action": "wait", "success": True}})',
                ])
            
            script_lines.append('')
        
        # Add completion logic
        script_lines.extend([
            f'        # Calculate results',
            f'        success_count = sum(1 for r in results if r.get("success", False))',
            f'        success_rate = (success_count / len(results)) * 100 if results else 0',
            f'        ',
            f'        print(f"\\n🎯 Mobile automation completed!")',
            f'        print(f"📊 Steps: {{len(results)}}, Success: {{success_count}}, Rate: {{success_rate:.1f}}%")',
            f'        ',
            f'        return {{',
            f'            "success": success_rate > 70,',
            f'            "success_rate": success_rate,',
            f'            "message": f"Mobile automation completed with {{success_rate:.1f}}% success rate",',
            f'            "results": results,',
            f'            "task_config": task_config',
            f'        }}',
            f'        ',
            f'    except Exception as e:',
            f'        print(f"❌ Mobile automation failed: {{str(e)}}")',
            f'        return {{',
            f'            "success": False,',
            f'            "error": str(e),',
            f'            "results": results,',
            f'            "task_config": task_config',
            f'        }}',
            f'        ',
            f'    finally:',
            f'        # Cleanup',
            f'        try:',
            f'            tools.close_driver()',
            f'        except:',
            f'            pass',
            f'',
            f'if __name__ == "__main__":',
            f'    result = execute_mobile_automation()',
            f'    print(json.dumps(result, indent=2))'
        ])
        
        return '\\n'.join(script_lines)
    
    async def _generate_generic_web_script(self, state: WorkflowState) -> str:
        """Generate generic web automation script"""
        
        blueprint = state.json_blueprint or {}
        parameters = state.parameters or {}
        
        workflow_name = blueprint.get("workflow_name", "web_automation")
        steps = blueprint.get("steps", [])
        dynamic_inputs = blueprint.get("dynamic_inputs", [])
        user_instruction = parameters.get("instruction", "Web automation task")
        user_data = {k: v for k, v in parameters.items() if k not in ["instruction", "platform"]}
        
        script_lines = [
            f'"""',
            f'Generic Web Automation Script',
            f'Generated for: {user_instruction}',
            f'Workflow: {workflow_name}',
            f'Platform: Web (Playwright)',
            f'Steps: {len(steps)}',
            f'Generated at: {datetime.utcnow().isoformat()}',
            f'"""',
            f'',
            f'import asyncio',
            f'import json',
            f'import time',
            f'from typing import Dict, Any',
            f'',
            f'# Import generic web automation tools',
            f'from app.tools.web_tools import GenericWebAutomationTools',
            f'',
            f'async def execute_web_automation():',
            f'    """Execute generic web automation"""',
            f'    ',
            f'    # Task configuration',
            f'    task_config = {{',
            f'        "instruction": "{user_instruction}",',
            f'        "workflow": "{workflow_name}",',
            f'        "user_data": {json.dumps(user_data, indent=8)},',
            f'        "dynamic_inputs": {json.dumps(dynamic_inputs, indent=8)}',
            f'    }}',
            f'    ',
            f'    results = []',
            f'    ',
            f'    try:',
            f'        print("🔵 Starting web automation...")',
            f'        print("📋 Task:", (task_config.get("instruction", "")[:100]))',
            f'        ',
            f'        # Initialize web tools',
            f'        tools = GenericWebAutomationTools()',
            f'        ',
            f'        # Setup browser',
            f'        print("🔧 Setting up web browser...")',
            f'        if not await tools.setup_browser():',
            f'            return {{"success": False, "error": "Web browser setup failed", "results": results}}',
            f'        ',
            f'        print("✅ Web browser ready")',
            f'        results.append({{"step": "setup", "action": "browser_setup", "success": True}})',
            f'        ',
        ]
        
        # Add automation steps from blueprint
        for i, step in enumerate(steps[:10], 1):  # Limit steps for safety
            step_num = i + 1
            action = step.get("action", "unknown")
            target = step.get("target", "element")
            locator = step.get("locator", {})
            value = step.get("value", "")
            url = step.get("url", "")
            
            script_lines.extend([
                f'        # Step {step_num}: {action.title()} - {target}',
                f'        print("\\n🔵 Step {step_num}: {action.title()} - {target}")',
                f'        await asyncio.sleep(1)',
                f'        ',
            ])
            
            if action == "navigate":
                navigation_url = url or "https://example.com"
                script_lines.extend([
                    f'        # Navigate to URL',
                    f'        if await tools.navigate_to("{navigation_url}"):',
                    f'            results.append({{"step": {step_num}, "action": "navigate", "url": "{navigation_url}", "success": True}})',
                    f'        else:',
                    f'            results.append({{"step": {step_num}, "action": "navigate", "url": "{navigation_url}", "success": False}})',
                ])
            
            elif action == "click":
                locator_strategies = self._create_web_locator_strategies(locator, target)
                script_lines.extend([
                    f'        # Click element: {target}',
                    f'        locator_strategies = {json.dumps(locator_strategies, indent=8)}',
                    f'        if await tools.click_element(locator_strategies, "{target}"):',
                    f'            results.append({{"step": {step_num}, "action": "click", "target": "{target}", "success": True}})',
                    f'        else:',
                    f'            results.append({{"step": {step_num}, "action": "click", "target": "{target}", "success": False}})',
                ])
            
            elif action in ["fill", "type"]:
                locator_strategies = self._create_web_locator_strategies(locator, target)
                fill_value = self._resolve_dynamic_value(value, user_data)
                
                script_lines.extend([
                    f'        # Fill text field: {target}',
                    f'        locator_strategies = {json.dumps(locator_strategies, indent=8)}',
                    f'        fill_value = "{fill_value}"',
                    f'        if await tools.fill_text_field(locator_strategies, fill_value, "{target}"):',
                    f'            results.append({{"step": {step_num}, "action": "fill", "target": "{target}", "success": True, "value": fill_value}})',
                    f'        else:',
                    f'            results.append({{"step": {step_num}, "action": "fill", "target": "{target}", "success": False}})',
                ])
            
            elif action == "scroll":
                direction = step.get("direction", "down")
                script_lines.extend([
                    f'        # Scroll page: {direction}',
                    f'        if await tools.scroll_page("{direction}"):',
                    f'            results.append({{"step": {step_num}, "action": "scroll", "direction": "{direction}", "success": True}})',
                    f'        else:',
                    f'            results.append({{"step": {step_num}, "action": "scroll", "direction": "{direction}", "success": False}})',
                ])
            
            elif action == "wait":
                timeout = step.get("timeout", 5000)
                script_lines.extend([
                    f'        # Wait for element/condition',
                    f'        await asyncio.sleep({timeout / 1000})',
                    f'        results.append({{"step": {step_num}, "action": "wait", "success": True}})',
                ])
            
            script_lines.append('')
        
        # Add completion logic
        script_lines.extend([
            f'        # Calculate results',
            f'        success_count = sum(1 for r in results if r.get("success", False))',
            f'        success_rate = (success_count / len(results)) * 100 if results else 0',
            f'        ',
            f'        print(f"\\n🎯 Web automation completed!")',
            f'        print(f"📊 Steps: {{len(results)}}, Success: {{success_count}}, Rate: {{success_rate:.1f}}%")',
            f'        ',
            f'        return {{',
            f'            "success": success_rate > 70,',
            f'            "success_rate": success_rate,',
            f'            "message": f"Web automation completed with {{success_rate:.1f}}% success rate",',
            f'            "results": results,',
            f'            "task_config": task_config',
            f'        }}',
            f'        ',
            f'    except Exception as e:',
            f'        print(f"❌ Web automation failed: {{str(e)}}")',
            f'        return {{',
            f'            "success": False,',
            f'            "error": str(e),',
            f'            "results": results,',
            f'            "task_config": task_config',
            f'        }}',
            f'        ',
            f'    finally:',
            f'        # Cleanup',
            f'        try:',
            f'            await tools.close_browser()',
            f'        except:',
            f'            pass',
            f'',
            f'async def main():',
            f'    result = await execute_web_automation()',
            f'    print(json.dumps(result, indent=2))',
            f'',
            f'if __name__ == "__main__":',
            f'    asyncio.run(main())'
        ])
        
        return '\\n'.join(script_lines)
    
    def _create_mobile_locator_strategies(self, locator: Dict[str, str], target: str) -> List[Dict[str, str]]:
        """Create mobile locator strategies"""
        strategies = []
        
        if locator and locator.get("value"):
            strategies.append({
                "type": locator.get("type", "xpath"),
                "value": locator["value"]
            })
        
        # Add fallback strategies
        target_lower = target.lower()
        strategies.extend([
            {"type": "xpath", "value": f"//*[contains(@text, '{target}')]"},
            {"type": "xpath", "value": f"//*[contains(@content-desc, '{target}')]"},
            {"type": "android_uiautomator", "value": f'new UiSelector().textContains("{target}")'},
            {"type": "android_uiautomator", "value": f'new UiSelector().descriptionContains("{target}")'}
        ])
        
        return strategies
    
    def _create_web_locator_strategies(self, locator: Dict[str, str], target: str) -> List[Dict[str, str]]:
        """Create web locator strategies"""
        strategies = []
        
        if locator and locator.get("value"):
            strategies.append({
                "type": locator.get("type", "css"),
                "value": locator["value"]
            })
        
        # Add fallback strategies
        target_lower = target.lower().replace(" ", "-")
        strategies.extend([
            {"type": "css", "value": f'button:has-text("{target}")'},
            {"type": "css", "value": f'input[name*="{target_lower}"]'},
            {"type": "css", "value": f'[aria-label*="{target}"]'},
            {"type": "css", "value": f'[placeholder*="{target}"]'},
            {"type": "css", "value": f'#{target_lower}'},
            {"type": "css", "value": f'.{target_lower}'}
        ])
        
        return strategies
    
    def _resolve_dynamic_value(self, value: str, user_data: Dict[str, Any]) -> str:
        """Resolve dynamic template values"""
        if not value or "{{" not in value:
            return value
        
        # Extract variable name
        start = value.find("{{")
        end = value.find("}}", start)
        if start >= 0 and end > start:
            var_name = value[start+2:end].strip()
            if var_name in user_data:
                return str(user_data[var_name])
            else:
                return f"auto_{var_name}"
        
        return value
    
    async def _regenerate_script_with_feedback(self, state: WorkflowState, feedback: Dict[str, Any]) -> str:
        """Regenerate script based on Agent 3's feedback"""
        
        current_script = state.generated_script
        issues = feedback.get("issues", [])
        improvements = feedback.get("improvements", [])
        
        print(f"🟢 [{self.name}] Regenerating script with {len(issues)} issues and {len(improvements)} improvements...")
        
        prompt = f"""
You are an expert automation script improver. Enhance the current script based on execution feedback.

CURRENT SCRIPT:
```python
{current_script[:3000]}...
```

EXECUTION ISSUES:
{json.dumps(issues, indent=2)}

SUGGESTED IMPROVEMENTS:
{json.dumps(improvements, indent=2)}

PLATFORM: {state.platform}
TASK: {state.parameters.get('instruction', 'Unknown')}

IMPROVEMENT REQUIREMENTS:
1. Fix all identified issues specifically
2. Apply all suggested improvements
3. Keep the generic tools integration
4. Enhance error handling and retry logic
5. Add better element finding strategies
6. Improve timing and wait conditions
7. Add more robust fallback methods

Generate the COMPLETE IMPROVED Python script. Keep all existing functionality and generic tools.
Return ONLY the improved script code, no explanations.
"""
        
        try:
            response = await model_client.generate(prompt, max_tokens=4000, temperature=0.1)
            improved_script = self._extract_script_from_response(response)
            
            if improved_script and len(improved_script) > len(current_script) * 0.7:
                return improved_script
            else:
                return current_script
                
        except Exception as e:
            print(f"🔴 [{self.name}] Script regeneration failed: {str(e)}")
            return current_script
    
    def _extract_script_from_response(self, response: str) -> str:
        """Extract script code from LLM response"""
        try:
            if "```python" in response:
                start = response.find("```python") + len("```python")
                end = response.find("```", start)
                if end > start:
                    return response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                if end > start:
                    return response[start:end].strip()
            else:
                return response.strip()
        except:
            return ""
    
    def _analyze_script_type(self, script: str) -> str:
        """Analyze generated script type"""
        script_lower = script.lower()
        
        if "genericwebautomationtools" in script_lower:
            return "generic_web_automation"
        elif "genericmobileautomationtools" in script_lower:
            return "generic_mobile_automation"
        else:
            return "generic_automation_script"
    
    async def _save_script_artifact(self, state: WorkflowState, script: str, version: int, reason: str = "update") -> str:
        """Save script artifact"""
        try:
            os.makedirs(state.run_dir, exist_ok=True)
            
            if version == 1:
                script_name = "agent-code-generator.py"
            else:
                script_name = f"agent-code-generator.v{version}.py"
            
            script_path = os.path.join(state.run_dir, script_name)
            
            metadata_header = f'''"""
Generic Code Agent - Version {version}
Task ID: {state.task_id}
Platform: {state.platform}
Generated at: {datetime.utcnow().isoformat()}
Reason: {reason}
Task: {state.parameters.get('instruction', 'Unknown')}
"""

'''
            
            full_script = metadata_header + script
            
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(full_script)
            
            # Also update latest version pointer
            latest_path = os.path.join(state.run_dir, "agent-code-generator-latest.py")
            with open(latest_path, "w", encoding="utf-8") as f:
                f.write(full_script)
            
            return script_path
            
        except Exception as e:
            print(f"🔴 [{self.name}] Error saving script: {str(e)}")
            return ""
    
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
        """Save conversation log to artifacts"""
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
code_agent = GenericCodeAgent()