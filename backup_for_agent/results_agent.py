"""
Generic Results Agent - Agent 4 (Updated)  
Comprehensive validation for ANY automation task
"""
import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.models.schemas import WorkflowState
from app.utils.model_client import model_client

class GenericResultsAgent:
    """Generic results validation agent for any automation task"""
    
    def __init__(self):
        self.name = "results_agent"
        self.description = "Generic results validation with comprehensive analysis"
        self.conversation_log = []
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """Main processing function for any automation task"""
        try:
            print(f"\\n🔵 [{self.name}] Starting generic results validation...")
            print(f"🔵 [{self.name}] Task: {state.parameters.get('instruction', 'Unknown')}")
            print(f"🔵 [{self.name}] Platform: {state.platform}")
            print(f"🔵 [{self.name}] Execution result available: {bool(state.execution_result)}")
            
            state.current_agent = self.name
            
            await self._log_conversation(state, "AGENT_4_START", {
                "message": "Generic results validation started",
                "task": state.parameters.get("instruction", "Unknown"),
                "platform": str(state.platform),
                "execution_available": bool(state.execution_result)
            })
            
            # Step 1: Analyze execution results
            print(f"🔵 [{self.name}] Step 1: Analyzing execution results...")
            execution_analysis = await self._analyze_execution_results(state)
            
            # Step 2: Validate task completion
            print(f"🔵 [{self.name}] Step 2: Validating task completion...")
            task_analysis = await self._validate_task_completion(state)
            
            # Step 3: Calculate confidence score
            print(f"🔵 [{self.name}] Step 3: Calculating confidence score...")
            confidence_analysis = await self._calculate_confidence_score(state, execution_analysis, task_analysis)
            
            # Step 4: Generate final report
            print(f"🔵 [{self.name}] Step 4: Generating final report...")
            final_report = await self._generate_final_report(state, execution_analysis, task_analysis, confidence_analysis)
            
            # Update state
            state.final_output = final_report
            state.success = final_report.get("success", False)
            
            # Save artifacts
            if state.run_dir:
                await self._save_results_artifacts(state, final_report)
                await self._save_conversation_log(state)
            
            await self._log_conversation(state, "AGENT_4_COMPLETED", {
                "final_success": final_report.get("success", False),
                "confidence": final_report.get("confidence", 0.0),
                "execution_score": execution_analysis.get("score", 0.0),
                "task_completion": task_analysis.get("completed", False)
            })
            
            # Final status
            success_icon = "✅" if final_report.get("success") else "❌"
            print(f"\\n🔵 [{self.name}] ========== FINAL RESULTS ==========")
            print(f"🔵 [{self.name}] Status: {success_icon} {'SUCCESS' if final_report.get('success') else 'FAILED'}")
            print(f"🔵 [{self.name}] Confidence: {final_report.get('confidence', 0.0):.3f}")
            print(f"🔵 [{self.name}] Task Completion: {'✅' if task_analysis.get('completed') else '❌'}")
            print(f"🔵 [{self.name}] Execution Score: {execution_analysis.get('score', 0.0):.1f}/100")
            print(f"🔵 [{self.name}] Agent Collaborations: {state.execution_result.get('agent2_collaborations', 0)}")
            print(f"🔵 [{self.name}] =====================================")
            
            return state
            
        except Exception as e:
            print(f"🔴 [{self.name}] Error: {str(e)}")
            state.final_output = {
                "success": False,
                "error": str(e),
                "confidence": 0.0,
                "message": "Results validation failed"
            }
            state.success = False
            return state
    
    async def _analyze_execution_results(self, state: WorkflowState) -> Dict[str, Any]:
        """Analyze execution results"""
        
        execution_result = state.execution_result or {}
        
        analysis = {
            "execution_success": execution_result.get("success", False),
            "attempts_made": execution_result.get("attempts", 0),
            "success_rate": execution_result.get("success_rate", 0),
            "execution_time": execution_result.get("execution_time", 0),
            "agent2_collaborations": execution_result.get("agent2_collaborations", 0),
            "improvements_made": len(execution_result.get("improvements_made", [])),
            "steps_executed": len(execution_result.get("step_results", [])),
            "step_success_rate": 0.0,
            "quality_indicators": [],
            "technical_achievements": []
        }
        
        # Analyze step results
        step_results = execution_result.get("step_results", [])
        if step_results:
            successful_steps = sum(1 for step in step_results if step.get("success", False))
            analysis["step_success_rate"] = (successful_steps / len(step_results)) * 100
            
            if analysis["step_success_rate"] > 90:
                analysis["quality_indicators"].append("Excellent step execution rate")
            elif analysis["step_success_rate"] > 70:
                analysis["quality_indicators"].append("Good step execution rate")
            else:
                analysis["quality_indicators"].append("Step execution needs improvement")
        
        # Technical achievements
        if analysis["execution_success"]:
            analysis["technical_achievements"].append("Script execution completed successfully")
            
        if analysis["attempts_made"] == 1 and analysis["execution_success"]:
            analysis["technical_achievements"].append("Success on first attempt")
        elif analysis["execution_success"]:
            analysis["technical_achievements"].append("Success after multiple attempts")
            
        if analysis["agent2_collaborations"] > 0:
            analysis["technical_achievements"].append(f"Multi-agent collaboration succeeded ({analysis['agent2_collaborations']} rounds)")
        
        # Calculate execution score
        score = 0
        if analysis["execution_success"]:
            score += 60  # Base success points
        
        score += min(25, analysis["step_success_rate"] / 4)  # Step quality points
        
        # Efficiency points
        if analysis["attempts_made"] == 1:
            score += 15
        elif analysis["attempts_made"] <= 2:
            score += 10
        elif analysis["attempts_made"] <= 3:
            score += 5
        
        analysis["score"] = score
        
        print(f"🔵 [{self.name}] Execution analysis:")
        print(f"🔵 [{self.name}]   Success: {'✅' if analysis['execution_success'] else '❌'}")
        print(f"🔵 [{self.name}]   Score: {analysis['score']:.1f}/100")
        print(f"🔵 [{self.name}]   Step Success Rate: {analysis['step_success_rate']:.1f}%")
        print(f"🔵 [{self.name}]   Agent Collaborations: {analysis['agent2_collaborations']}")
        
        return analysis
    
    async def _validate_task_completion(self, state: WorkflowState) -> Dict[str, Any]:
        """Validate task completion based on user instruction"""
        
        user_instruction = state.parameters.get("instruction", "")
        execution_result = state.execution_result or {}
        blueprint = state.json_blueprint or {}
        
        analysis = {
            "user_instruction": user_instruction,
            "task_clarity": "high" if len(user_instruction) > 30 else "medium" if len(user_instruction) > 10 else "low",
            "blueprint_alignment": 0.0,
            "execution_alignment": 0.0,
            "completed": False,
            "completion_indicators": [],
            "missing_elements": []
        }
        
        # Analyze blueprint alignment
        blueprint_steps = blueprint.get("steps", [])
        if blueprint_steps and user_instruction:
            instruction_words = set(user_instruction.lower().split())
            alignment_count = 0
            
            for step in blueprint_steps:
                step_action = step.get("action", "").lower()
                step_target = step.get("target", "").lower()
                step_words = set((step_action + " " + step_target).split())
                
                if instruction_words.intersection(step_words):
                    alignment_count += 1
            
            analysis["blueprint_alignment"] = alignment_count / len(blueprint_steps) if blueprint_steps else 0
        
        # Analyze execution alignment
        if execution_result.get("success", False):
            analysis["execution_alignment"] = 0.8  # High alignment if execution succeeded
        else:
            step_success_rate = execution_result.get("success_rate", 0)
            analysis["execution_alignment"] = step_success_rate / 100
        
        # Determine completion
        execution_success = execution_result.get("success", False)
        good_alignment = analysis["blueprint_alignment"] > 0.6 or analysis["execution_alignment"] > 0.7
        
        if execution_success and good_alignment:
            analysis["completed"] = True
            analysis["completion_indicators"].extend([
                "Script executed successfully",
                "Good alignment between task and execution",
                "Automation objectives achieved"
            ])
        elif execution_success:
            analysis["completed"] = True
            analysis["completion_indicators"].extend([
                "Script executed successfully",
                "Basic automation completed"
            ])
            analysis["missing_elements"].append("Limited evidence of specific task completion")
        else:
            analysis["completed"] = False
            analysis["missing_elements"].extend([
                "Script execution failed",
                "Primary automation task not completed"
            ])
        
        # Additional indicators
        if execution_result.get("agent2_collaborations", 0) > 0:
            analysis["completion_indicators"].append("Multi-agent collaboration enhanced results")
        
        if execution_result.get("success_rate", 0) > 80:
            analysis["completion_indicators"].append("High automation success rate achieved")
        
        print(f"🔵 [{self.name}] Task completion analysis:")
        print(f"🔵 [{self.name}]   Completed: {'✅' if analysis['completed'] else '❌'}")
        print(f"🔵 [{self.name}]   Blueprint Alignment: {analysis['blueprint_alignment']:.2f}")
        print(f"🔵 [{self.name}]   Execution Alignment: {analysis['execution_alignment']:.2f}")
        
        return analysis
    
    async def _calculate_confidence_score(self, state: WorkflowState, execution_analysis: Dict[str, Any], task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall confidence score"""
        
        confidence_factors = {
            "blueprint_quality": 0.0,
            "execution_success": 0.0,
            "task_alignment": 0.0,
            "technical_quality": 0.0
        }
        
        weights = {
            "blueprint_quality": 0.2,
            "execution_success": 0.4,
            "task_alignment": 0.3,
            "technical_quality": 0.1
        }
        
        # Blueprint quality
        blueprint = state.json_blueprint or {}
        blueprint_confidence = blueprint.get("confidence", 0.0)
        blueprint_steps = len(blueprint.get("steps", []))
        
        if blueprint_confidence > 0.8 and blueprint_steps >= 5:
            confidence_factors["blueprint_quality"] = 0.9
        elif blueprint_confidence > 0.6 and blueprint_steps >= 3:
            confidence_factors["blueprint_quality"] = 0.7
        elif blueprint_steps > 0:
            confidence_factors["blueprint_quality"] = 0.5
        
        # Execution success
        if execution_analysis["execution_success"]:
            if execution_analysis["attempts_made"] == 1:
                confidence_factors["execution_success"] = 1.0
            elif execution_analysis["attempts_made"] <= 2:
                confidence_factors["execution_success"] = 0.8
            else:
                confidence_factors["execution_success"] = 0.6
        else:
            confidence_factors["execution_success"] = max(0.1, execution_analysis["step_success_rate"] / 100)
        
        # Task alignment
        confidence_factors["task_alignment"] = (task_analysis["blueprint_alignment"] + task_analysis["execution_alignment"]) / 2
        if task_analysis["completed"]:
            confidence_factors["task_alignment"] = min(1.0, confidence_factors["task_alignment"] + 0.2)
        
        # Technical quality
        confidence_factors["technical_quality"] = min(1.0, execution_analysis["score"] / 100)
        
        # Calculate weighted confidence
        overall_confidence = sum(
            confidence_factors[factor] * weights[factor]
            for factor in confidence_factors
        )
        
        confidence_level = "high" if overall_confidence > 0.8 else "medium" if overall_confidence > 0.6 else "low"
        
        analysis = {
            "overall_confidence": overall_confidence,
            "confidence_factors": confidence_factors,
            "confidence_level": confidence_level,
            "reasoning": []
        }
        
        # Add reasoning
        if execution_analysis["execution_success"]:
            analysis["reasoning"].append("Script execution succeeded")
        if task_analysis["completed"]:
            analysis["reasoning"].append("Task completion achieved")
        if blueprint.get("confidence", 0) > 0.7:
            analysis["reasoning"].append("High-quality blueprint generated")
        if execution_analysis["agent2_collaborations"] > 0:
            analysis["reasoning"].append("Multi-agent collaboration succeeded")
        
        print(f"🔵 [{self.name}] Confidence analysis:")
        print(f"🔵 [{self.name}]   Overall: {overall_confidence:.3f} ({confidence_level})")
        print(f"🔵 [{self.name}]   Blueprint: {confidence_factors['blueprint_quality']:.2f}")
        print(f"🔵 [{self.name}]   Execution: {confidence_factors['execution_success']:.2f}")
        print(f"🔵 [{self.name}]   Task Alignment: {confidence_factors['task_alignment']:.2f}")
        
        return analysis
    
    async def _generate_final_report(self, state: WorkflowState, execution_analysis: Dict[str, Any], 
                                    task_analysis: Dict[str, Any], confidence_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        
        execution_result = state.execution_result or {}
        blueprint = state.json_blueprint or {}
        
        overall_success = (
            execution_analysis["execution_success"] and 
            task_analysis["completed"] and
            confidence_analysis["overall_confidence"] > 0.5
        )
        
        report = {
            "success": overall_success,
            "confidence": confidence_analysis["overall_confidence"],
            "confidence_level": confidence_analysis["confidence_level"],
            
            # Summary
            "summary": {
                "task": state.parameters.get("instruction", "Unknown"),
                "platform": str(state.platform),
                "execution_success": execution_analysis["execution_success"],
                "task_completed": task_analysis["completed"],
                "total_attempts": execution_analysis["attempts_made"],
                "agent_collaborations": execution_analysis["agent2_collaborations"],
                "execution_time": execution_analysis["execution_time"],
                "overall_score": execution_analysis["score"]
            },
            
            # Detailed metrics
            "metrics": {
                "execution_score": execution_analysis["score"],
                "step_success_rate": execution_analysis["step_success_rate"],
                "steps_executed": execution_analysis["steps_executed"],
                "blueprint_alignment": task_analysis["blueprint_alignment"],
                "execution_alignment": task_analysis["execution_alignment"],
                "confidence_factors": confidence_analysis["confidence_factors"]
            },
            
            # Achievements and improvements
            "achievements": execution_analysis["technical_achievements"] + task_analysis["completion_indicators"],
            "areas_for_improvement": task_analysis["missing_elements"],
            
            # Quality assessment
            "quality_assessment": {
                "overall_quality": "excellent" if overall_success and confidence_analysis["overall_confidence"] > 0.8 else
                                  "good" if overall_success and confidence_analysis["overall_confidence"] > 0.6 else
                                  "fair" if execution_analysis["execution_success"] else "poor",
                "blueprint_quality": execution_analysis["quality_indicators"],
                "execution_quality": "high" if execution_analysis["step_success_rate"] > 80 else
                                    "medium" if execution_analysis["step_success_rate"] > 60 else "low"
            },
            
            # Metadata
            "metadata": {
                "task_id": state.task_id,
                "timestamp": datetime.utcnow().isoformat(),
                "processing_agents": ["document_agent", "code_agent", "llm_supervisor", "results_agent"],
                "multi_agent_communication": execution_analysis["agent2_collaborations"] > 0,
                "artifacts_generated": len(state.artifacts),
                "confidence_reasoning": confidence_analysis["reasoning"]
            }
        }
        
        # Generate final message
        if overall_success:
            if confidence_analysis["overall_confidence"] > 0.8:
                report["message"] = "✅ Excellent! Automation completed successfully with high confidence."
            else:
                report["message"] = "✅ Success! Automation completed with good confidence."
        else:
            if execution_analysis["execution_success"]:
                report["message"] = "⚠️ Partial Success. Script executed but task completion unclear."
            else:
                report["message"] = "❌ Failed. Automation did not complete successfully."
        
        return report
    
    async def _save_results_artifacts(self, state: WorkflowState, final_report: Dict[str, Any]):
        """Save results artifacts"""
        if not state.run_dir:
            return
        
        # Save JSON report
        report_json_path = os.path.join(state.run_dir, "agent4_final_report.json")
        with open(report_json_path, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        state.artifacts["agent4_final_report"] = report_json_path
        
        # Save human-readable report
        report_txt_path = os.path.join(state.run_dir, "agent4_final_report.txt")
        await self._save_human_readable_report(final_report, report_txt_path)
        
        state.artifacts["agent4_final_report_txt"] = report_txt_path
        
        print(f"🔵 [{self.name}] ✅ Results artifacts saved")
    
    async def _save_human_readable_report(self, final_report: Dict[str, Any], report_path: str):
        """Save human-readable final report"""
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("GENERIC MULTI-AGENT AUTOMATION - FINAL REPORT\\n")
                f.write("=" * 55 + "\\n\\n")
                
                f.write("SUMMARY\\n")
                f.write("-" * 10 + "\\n")
                f.write(f"Task: {final_report['summary']['task']}\\n")
                f.write(f"Platform: {final_report['summary']['platform']}\\n")
                f.write(f"Result: {'✅ SUCCESS' if final_report['success'] else '❌ FAILED'}\\n")
                f.write(f"Confidence: {final_report['confidence']:.3f} ({final_report['confidence_level']})\\n")
                f.write(f"Message: {final_report['message']}\\n\\n")
                
                f.write("EXECUTION METRICS\\n")
                f.write("-" * 20 + "\\n")
                f.write(f"Overall Score: {final_report['metrics']['execution_score']:.1f}/100\\n")
                f.write(f"Steps Executed: {final_report['metrics']['steps_executed']}\\n")
                f.write(f"Step Success Rate: {final_report['metrics']['step_success_rate']:.1f}%\\n")
                f.write(f"Total Attempts: {final_report['summary']['total_attempts']}\\n")
                f.write(f"Agent Collaborations: {final_report['summary']['agent_collaborations']}\\n")
                f.write(f"Execution Time: {final_report['summary']['execution_time']:.1f}s\\n\\n")
                
                if final_report['achievements']:
                    f.write("ACHIEVEMENTS\\n")
                    f.write("-" * 15 + "\\n")
                    for achievement in final_report['achievements']:
                        f.write(f"  ✅ {achievement}\\n")
                    f.write("\\n")
                
                if final_report['areas_for_improvement']:
                    f.write("AREAS FOR IMPROVEMENT\\n")
                    f.write("-" * 25 + "\\n")
                    for area in final_report['areas_for_improvement']:
                        f.write(f"  🔧 {area}\\n")
                    f.write("\\n")
                
                f.write(f"Quality Assessment: {final_report['quality_assessment']['overall_quality'].title()}\\n")
                f.write(f"Generated at: {final_report['metadata']['timestamp']}\\n")
                f.write(f"Generic Multi-Agent Automation System\\n")
        except Exception as e:
            print(f"🔴 [{self.name}] Error saving readable report: {str(e)}")
    
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
results_agent = GenericResultsAgent()