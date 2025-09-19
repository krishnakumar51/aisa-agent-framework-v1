"""
Results processing agent - Agent 4
Validates results and formats final output
"""
import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime
from app.models.schemas import WorkflowState, AgentStatus
from app.utils.model_client import model_client

class ResultsAgent:
    """Agent responsible for result validation and formatting"""
    
    def __init__(self):
        self.name = "results_agent"
        self.description = "Validates execution results and formats final output"
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """Main processing function for results agent"""
        try:
            print(f"[{self.name}] Starting result validation...")
            state.current_agent = self.name
            
            # Step 1: Validate execution results
            validation_result = await self._validate_execution_results(state)
            
            # Step 2: Analyze overall success
            success_analysis = await self._analyze_overall_success(state)
            
            # Step 3: Format final output
            final_output = await self._format_final_output(
                state, validation_result, success_analysis
            )
            
            state.final_output = final_output
            state.success = success_analysis.get("overall_success", False)
            
            print(f"[{self.name}] Result validation completed")
            return state
            
        except Exception as e:
            print(f"[{self.name}] Error: {str(e)}")
            state.final_output = {
                "success": False,
                "error": str(e),
                "message": "Result validation failed"
            }
            state.success = False
            return state
    
    async def _validate_execution_results(self, state: WorkflowState) -> Dict[str, Any]:
        """Validate the execution results from Agent 3"""
        execution_result = state.execution_result or {}
        
        validation = {
            "execution_success": execution_result.get("success", False),
            "steps_completed": 0,
            "total_steps": 0,
            "errors_encountered": [],
            "screenshots_count": len(state.screenshots_taken or []),
            "logs_count": len(state.execution_logs or [])
        }
        
        # Analyze execution steps
        results = execution_result.get("results", [])
        if results:
            validation["total_steps"] = len(results)
            validation["steps_completed"] = sum(1 for r in results if r.get("success", False))
            validation["errors_encountered"] = [
                r.get("error", "Unknown error") for r in results if not r.get("success", False)
            ]
        
        # Calculate step success rate
        if validation["total_steps"] > 0:
            validation["step_success_rate"] = validation["steps_completed"] / validation["total_steps"]
        else:
            validation["step_success_rate"] = 0.0
        
        return validation
    
    async def _analyze_overall_success(self, state: WorkflowState) -> Dict[str, Any]:
        """Analyze overall workflow success using LLM intelligence"""
        try:
            # Prepare context for LLM analysis
            context = self._prepare_success_analysis_context(state)
            
            # Generate analysis prompt
            prompt = self._create_success_analysis_prompt(context)
            
            # Get LLM analysis
            response = await model_client.generate(prompt)
            
            # Parse LLM response
            analysis = self._parse_success_analysis(response, context)
            
            return analysis
            
        except Exception as e:
            print(f"[{self.name}] Success analysis failed: {str(e)}")
            return self._create_fallback_success_analysis(state)
    
    def _prepare_success_analysis_context(self, state: WorkflowState) -> Dict[str, Any]:
        """Prepare context for success analysis"""
        blueprint = state.json_blueprint or {}
        execution_result = state.execution_result or {}
        
        return {
            "blueprint_steps": blueprint.get("steps", []),
            "blueprint_confidence": blueprint.get("confidence", 0.0),
            "execution_success": execution_result.get("success", False),
            "execution_results": execution_result.get("results", []),
            "execution_error": execution_result.get("error"),
            "logs": state.execution_logs or [],
            "platform": str(state.platform),
            "screenshots_taken": len(state.screenshots_taken or [])
        }
    
    def _create_success_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for success analysis"""
        return f"""
Analyze the automation workflow execution and determine overall success.

PLANNED STEPS ({len(context['blueprint_steps'])}):
{json.dumps(context['blueprint_steps'][:5], indent=2)}

EXECUTION RESULTS:
Success: {context['execution_success']}
Error: {context['execution_error']}
Platform: {context['platform']}
Screenshots: {context['screenshots_taken']}

DETAILED RESULTS:
{json.dumps(context['execution_results'][-3:], indent=2)}

EXECUTION LOGS (last 5):
{context['logs'][-5:] if context['logs'] else ["No logs"]}

Provide analysis in JSON format:
{{
    "overall_success": true/false,
    "confidence": 0.0-1.0,
    "completion_percentage": 0-100,
    "success_factors": ["factor1", "factor2"],
    "failure_reasons": ["reason1", "reason2"],
    "recommendation": "Next steps or improvements"
}}

Consider:
- Partial completion can still be valuable
- Some failures might be acceptable if main goal achieved
- Evidence from screenshots and logs
"""
    
    def _parse_success_analysis(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM success analysis response"""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                analysis = json.loads(json_str)
                
                # Validate and enhance analysis
                analysis["overall_success"] = bool(analysis.get("overall_success", False))
                analysis["confidence"] = max(0.0, min(1.0, float(analysis.get("confidence", 0.0))))
                analysis["completion_percentage"] = max(0, min(100, int(analysis.get("completion_percentage", 0))))
                
                return analysis
            else:
                raise ValueError("No valid JSON in response")
                
        except Exception as e:
            print(f"[{self.name}] Analysis parsing failed: {str(e)}")
            return self._create_fallback_success_analysis_from_context(context)
    
    def _create_fallback_success_analysis(self, state: WorkflowState) -> Dict[str, Any]:
        """Create fallback success analysis when LLM fails"""
        execution_result = state.execution_result or {}
        execution_success = execution_result.get("success", False)
        
        # Basic success determination
        if execution_success:
            return {
                "overall_success": True,
                "confidence": 0.7,
                "completion_percentage": 90,
                "success_factors": ["Script executed successfully", "No major errors"],
                "failure_reasons": [],
                "recommendation": "Workflow completed successfully"
            }
        else:
            return {
                "overall_success": False,
                "confidence": 0.3,
                "completion_percentage": 20,
                "success_factors": [],
                "failure_reasons": ["Script execution failed", execution_result.get("error", "Unknown error")],
                "recommendation": "Review errors and retry with corrections"
            }
    
    def _create_fallback_success_analysis_from_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback analysis from context"""
        execution_success = context.get("execution_success", False)
        results = context.get("execution_results", [])
        
        if results:
            successful_steps = sum(1 for r in results if r.get("success", False))
            total_steps = len(results)
            completion_percentage = int((successful_steps / total_steps) * 100) if total_steps > 0 else 0
            
            return {
                "overall_success": completion_percentage >= 50,  # 50% threshold
                "confidence": 0.6,
                "completion_percentage": completion_percentage,
                "success_factors": [f"Completed {successful_steps}/{total_steps} steps"],
                "failure_reasons": ["Some steps failed"] if completion_percentage < 100 else [],
                "recommendation": "Partial completion achieved" if completion_percentage > 0 else "Workflow failed"
            }
        else:
            return self._create_fallback_success_analysis({"execution_result": context})
    
    async def _format_final_output(self, state: WorkflowState, 
                                 validation_result: Dict[str, Any],
                                 success_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Format the final output JSON"""
        
        # Create comprehensive final output
        final_output = {
            "task_id": state.task_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed" if success_analysis.get("overall_success", False) else "failed",
            "platform": str(state.platform),
            
            # Success metrics
            "success": success_analysis.get("overall_success", False),
            "confidence": success_analysis.get("confidence", 0.0),
            "completion_percentage": success_analysis.get("completion_percentage", 0),
            
            # Execution details
            "steps_completed": validation_result.get("steps_completed", 0),
            "total_steps": validation_result.get("total_steps", 0),
            "step_success_rate": validation_result.get("step_success_rate", 0.0),
            
            # Agent processing summary
            "agents_processed": [
                {
                    "name": "document_agent",
                    "success": state.json_blueprint is not None and "error" not in (state.json_blueprint or {}),
                    "output": "Blueprint created" if state.json_blueprint else "Failed"
                },
                {
                    "name": "code_agent", 
                    "success": bool(state.generated_script and not state.generated_script.startswith("# Error")),
                    "output": f"Script generated for {state.platform}" if state.generated_script else "Failed"
                },
                {
                    "name": "llm_supervisor",
                    "success": validation_result.get("execution_success", False),
                    "output": f"{validation_result.get('steps_completed', 0)} steps completed"
                },
                {
                    "name": "results_agent",
                    "success": True,  # Always succeeds if we reach here
                    "output": "Results validated and formatted"
                }
            ],
            
            # Detailed results
            "execution_summary": {
                "success_factors": success_analysis.get("success_factors", []),
                "failure_reasons": success_analysis.get("failure_reasons", []),
                "recommendation": success_analysis.get("recommendation", ""),
                "screenshots_captured": len(state.screenshots_taken or []),
                "logs_generated": len(state.execution_logs or [])
            },
            
            # Blueprint information
            "blueprint_info": {
                "steps_planned": len((state.json_blueprint or {}).get("steps", [])),
                "ui_elements_detected": len(state.ui_elements or []),
                "confidence": (state.json_blueprint or {}).get("confidence", 0.0)
            },
            
            # Timing (estimated)
            "estimated_duration": "6.5 minutes",
            "actual_processing_time": "Processing completed",
            
            # Error details (if any)
            "errors": validation_result.get("errors_encountered", [])
        }
        
        return final_output

# Global results agent instance
results_agent = ResultsAgent()