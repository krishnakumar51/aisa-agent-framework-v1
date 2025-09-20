"""
Generic Multi-Agent Workflow (graph.py)
Complete orchestration for ANY automation task
"""
import asyncio
import json
import os
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from app.models.schemas import WorkflowState, PlatformType
from app.agents.document_agent import document_agent
from app.agents.code_agent import code_agent  
from app.agents.llm_supervisor import llm_supervisor
from app.agents.results_agent import results_agent

class GenericMultiAgentWorkflow:
    """Generic multi-agent workflow for any automation task"""
    
    def __init__(self):
        self.name = "generic_multi_agent_workflow"
        self.version = "3.0"
        self.agents = {
            "document": document_agent,
            "code": code_agent,
            "supervisor": llm_supervisor,
            "results": results_agent
        }
        
        # Set up agent communication
        llm_supervisor.set_code_agent(code_agent)
        
        print(f"🚀 Generic Multi-Agent Workflow v{self.version} initialized")
        print(f"🤝 Agent 2-3 communication: ✅ Enabled")
        print(f"🔧 Generic automation tools: ✅ Integrated")
        print(f"📝 Conversation logging: ✅ Enabled")
        print(f"🌐 Platform support: Web & Mobile (Generic)")
    
    async def execute(self, 
                     document_content: bytes,
                     screenshots: list = None,
                     parameters: Dict[str, Any] = None,
                     run_dir: str = None) -> Dict[str, Any]:
        """Execute complete generic workflow for any automation task"""
        
        # Generate unique task ID
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        
        # Setup run directory
        if not run_dir:
            run_dir = f"generated_code/{task_id}"
        
        os.makedirs(run_dir, exist_ok=True)
        
        print(f"\\n🚀 ========== GENERIC MULTI-AGENT WORKFLOW STARTED ==========")
        print(f"🚀 Task ID: {task_id}")
        print(f"🚀 Version: {self.version}")
        print(f"🚀 Run Directory: {run_dir}")
        print(f"🚀 Document Size: {len(document_content)} bytes")
        print(f"🚀 Screenshots: {len(screenshots or [])}")
        print(f"🚀 User Task: {(parameters or {}).get('instruction', 'Unknown automation task')}")
        print(f"🚀 Platform Preference: {(parameters or {}).get('platform', 'auto-detect')}")
        print(f"🚀 =============================================================")
        
        # Initialize workflow state
        state = WorkflowState(
            task_id=task_id,
            document_content=document_content,
            screenshots=screenshots or [],
            parameters=parameters or {},
            run_dir=run_dir,
            artifacts={}
        )
        
        # Initialize conversation log
        conversation_start = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "WORKFLOW_START",
            "data": {
                "task_id": task_id,
                "workflow_version": self.version,
                "user_task": state.parameters.get("instruction", "Unknown"),
                "platform_preference": state.parameters.get("platform", "auto-detect"),
                "document_size": len(document_content),
                "screenshots_count": len(screenshots or []),
                "run_directory": run_dir,
                "workflow_type": "generic_automation"
            }
        }
        
        await self._save_initial_conversation(state, conversation_start)
        
        workflow_start_time = datetime.utcnow()
        
        try:
            # PHASE 1: Generic Document Processing (Agent 1)
            print(f"\\n🔵 ========== PHASE 1: GENERIC DOCUMENT PROCESSING ==========")
            print(f"🔵 Agent 1: Processing document for any automation task...")
            
            state = await document_agent.process(state)
            
            if not state.json_blueprint:
                raise Exception("Document processing failed - no automation blueprint generated")
            
            blueprint_confidence = state.json_blueprint.get("confidence", 0.0)
            blueprint_steps = len(state.json_blueprint.get("steps", []))
            detected_platform = state.json_blueprint.get("platform", "unknown")
            task_category = state.json_blueprint.get("task_category", "automation")
            
            print(f"🔵 Agent 1 Results:")
            print(f"🔵   Text Extracted: {len(state.extracted_text or '')} chars")
            print(f"🔵   UI Elements: {len(state.ui_elements or [])}")
            print(f"🔵   Blueprint Confidence: {blueprint_confidence:.2f}")
            print(f"🔵   Automation Steps: {blueprint_steps}")
            print(f"🔵   Platform: {detected_platform}")
            print(f"🔵   Task Category: {task_category}")
            
            # PHASE 2: Generic Code Generation (Agent 2)
            print(f"\\n🟢 ========== PHASE 2: GENERIC CODE GENERATION ==========")
            print(f"🟢 Agent 2: Generating automation script using generic tools...")
            
            state = await code_agent.process(state)
            
            if not state.generated_script:
                raise Exception("Code generation failed - no automation script generated")
            
            script_length = len(state.generated_script)
            script_type = self._analyze_script_type(state.generated_script)
            final_platform = state.platform
            
            print(f"🟢 Agent 2 Results:")
            print(f"🟢   Platform Detected: {final_platform}")
            print(f"🟢   Script Generated: {script_length} characters")
            print(f"🟢   Script Type: {script_type}")
            print(f"🟢   Generic Tools: ✅ Integrated")
            
            # PHASE 3: Generic Execution Supervision (Agent 3)
            print(f"\\n🟡 ========== PHASE 3: GENERIC EXECUTION SUPERVISION ==========")
            print(f"🟡 Agent 3: Executing automation with Agent 2 communication...")
            
            state = await llm_supervisor.process(state)
            
            execution_result = state.execution_result or {}
            execution_success = execution_result.get("success", False)
            total_attempts = execution_result.get("attempts", 0)
            agent2_collaborations = execution_result.get("agent2_collaborations", 0)
            success_rate = execution_result.get("success_rate", 0)
            
            print(f"🟡 Agent 3 Results:")
            print(f"🟡   Execution Success: {'✅' if execution_success else '❌'}")
            print(f"🟡   Total Attempts: {total_attempts}")
            print(f"🟡   Agent 2 Collaborations: {agent2_collaborations}")
            print(f"🟡   Success Rate: {success_rate:.1f}%")
            print(f"🟡   Improvements Made: {len(execution_result.get('improvements_made', []))}")
            
            # PHASE 4: Generic Results Validation (Agent 4)
            print(f"\\n🔵 ========== PHASE 4: GENERIC RESULTS VALIDATION ==========")
            print(f"🔵 Agent 4: Validating automation results...")
            
            state = await results_agent.process(state)
            
            final_output = state.final_output or {}
            overall_success = final_output.get("success", False)
            confidence = final_output.get("confidence", 0.0)
            confidence_level = final_output.get("confidence_level", "unknown")
            
            print(f"🔵 Agent 4 Results:")
            print(f"🔵   Overall Success: {'✅' if overall_success else '❌'}")
            print(f"🔵   Confidence: {confidence:.3f} ({confidence_level})")
            print(f"🔵   Success Factors: {len(final_output.get('achievements', []))}")
            print(f"🔵   Improvement Areas: {len(final_output.get('areas_for_improvement', []))}")
            
            # WORKFLOW COMPLETION
            workflow_end_time = datetime.utcnow()
            total_workflow_time = (workflow_end_time - workflow_start_time).total_seconds()
            
            # Final conversation log
            await self._save_final_conversation(state, {
                "workflow_success": overall_success,
                "total_time": total_workflow_time,
                "agent_results": {
                    "agent1_blueprint_confidence": blueprint_confidence,
                    "agent1_task_category": task_category,
                    "agent2_script_length": script_length,
                    "agent2_platform": str(final_platform),
                    "agent3_execution_success": execution_success,
                    "agent3_collaborations": agent2_collaborations,
                    "agent4_final_confidence": confidence
                }
            })
            
            # Create comprehensive summary
            workflow_summary = {
                "task_id": task_id,
                "workflow_version": self.version,
                "workflow_type": "generic_automation",
                "overall_success": overall_success,
                "total_execution_time": total_workflow_time,
                "user_task": state.parameters.get("instruction", "Unknown"),
                "platform_detected": str(final_platform),
                "task_category": task_category,
                
                "phase_results": {
                    "phase1_document_processing": {
                        "success": bool(state.json_blueprint),
                        "blueprint_confidence": blueprint_confidence,
                        "blueprint_steps": blueprint_steps,
                        "text_extracted": len(state.extracted_text or ""),
                        "ui_elements": len(state.ui_elements or []),
                        "task_category": task_category,
                        "platform_detected": detected_platform
                    },
                    "phase2_code_generation": {
                        "success": bool(state.generated_script),
                        "script_length": script_length,
                        "script_type": script_type,
                        "platform_confirmed": str(final_platform),
                        "generic_tools_integrated": True
                    },
                    "phase3_execution_supervision": {
                        "success": execution_success,
                        "total_attempts": total_attempts,
                        "agent2_collaborations": agent2_collaborations,
                        "success_rate": success_rate,
                        "execution_time": execution_result.get("execution_time", 0),
                        "improvements_made": len(execution_result.get("improvements_made", []))
                    },
                    "phase4_results_validation": {
                        "success": overall_success,
                        "confidence": confidence,
                        "confidence_level": confidence_level,
                        "task_completed": final_output.get("summary", {}).get("task_completed", False)
                    }
                },
                
                "automation_metrics": {
                    "blueprint_steps": blueprint_steps,
                    "execution_attempts": total_attempts,
                    "success_rate": success_rate,
                    "agent_collaborations": agent2_collaborations,
                    "overall_confidence": confidence,
                    "quality_assessment": final_output.get("quality_assessment", {}).get("overall_quality", "unknown")
                },
                
                "artifacts_generated": {
                    "total_artifacts": len(state.artifacts),
                    "conversation_log": "conversation.json",
                    "blueprint": "agent1_blueprint.json",
                    "generated_scripts": [k for k in state.artifacts.keys() if "agent2_script" in k],
                    "execution_logs": [k for k in state.artifacts.keys() if "agent3" in k],
                    "final_reports": [k for k in state.artifacts.keys() if "agent4" in k]
                },
                
                "multi_agent_communication": {
                    "agent2_agent3_collaborations": agent2_collaborations,
                    "communication_successful": agent2_collaborations > 0 and execution_success,
                    "conversation_log_entries": self._count_conversation_entries(state)
                },
                
                "timestamp": datetime.utcnow().isoformat(),
                "run_directory": run_dir
            }
            
            # Save workflow summary
            await self._save_workflow_summary(state, workflow_summary)
            
            print(f"\\n🚀 ========== GENERIC MULTI-AGENT WORKFLOW COMPLETED ==========")
            print(f"🚀 Overall Result: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
            print(f"🚀 Task Category: {task_category}")
            print(f"🚀 Platform: {final_platform}")
            print(f"🚀 Total Time: {total_workflow_time:.1f} seconds")
            print(f"🚀 Agent 2-3 Collaborations: {agent2_collaborations}")
            print(f"🚀 Final Confidence: {confidence:.3f} ({confidence_level})")
            print(f"🚀 Artifacts Generated: {len(state.artifacts)}")
            print(f"🚀 Conversation Entries: {self._count_conversation_entries(state)}")
            print(f"🚀 Message: {final_output.get('message', 'Generic automation workflow completed')}")
            print(f"🚀 Run Directory: {run_dir}")
            print(f"🚀 ================================================================")
            
            return {
                "success": overall_success,
                "task_id": task_id,
                "message": final_output.get("message", "Generic multi-agent automation completed"),
                "confidence": confidence,
                "confidence_level": confidence_level,
                "task_category": task_category,
                "platform": str(final_platform),
                "execution_time": total_workflow_time,
                "agent_collaborations": agent2_collaborations,
                "artifacts_count": len(state.artifacts),
                "run_directory": run_dir,
                "workflow_summary": workflow_summary,
                "detailed_results": {
                    "blueprint": state.json_blueprint,
                    "execution_result": state.execution_result,
                    "final_output": state.final_output,
                    "artifacts": state.artifacts
                }
            }
            
        except Exception as e:
            workflow_end_time = datetime.utcnow()
            total_workflow_time = (workflow_end_time - workflow_start_time).total_seconds()
            
            error_summary = {
                "success": False,
                "task_id": task_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time": total_workflow_time,
                "current_agent": getattr(state, "current_agent", "unknown"),
                "artifacts_generated": len(state.artifacts) if hasattr(state, "artifacts") else 0,
                "run_directory": run_dir,
                "workflow_type": "generic_automation"
            }
            
            print(f"\\n🚀 ========== WORKFLOW FAILED ==========")
            print(f"🚀 Error: {str(e)}")
            print(f"🚀 Current Agent: {error_summary['current_agent']}")
            print(f"🚀 Total Time: {total_workflow_time:.1f} seconds")
            print(f"🚀 Artifacts Generated: {error_summary['artifacts_generated']}")
            print(f"🚀 ========================================")
            
            # Save error conversation
            await self._save_error_conversation(state, error_summary)
            
            return error_summary
    
    def _analyze_script_type(self, script: str) -> str:
        """Analyze generated script type"""
        script_lower = script.lower()
        
        if "genericwebautomationtools" in script_lower:
            return "generic_web_automation"
        elif "genericmobileautomationtools" in script_lower:
            return "generic_mobile_automation"
        elif "async def" in script_lower:
            return "async_automation_script"
        elif "execute_" in script_lower and "_automation" in script_lower:
            return "generic_automation_script"
        else:
            return "automation_script"
    
    def _count_conversation_entries(self, state: WorkflowState) -> int:
        """Count conversation log entries"""
        conversation_path = state.artifacts.get("conversation_log")
        if not conversation_path or not os.path.exists(conversation_path):
            return 0
        
        try:
            with open(conversation_path, 'r', encoding='utf-8') as f:
                conversation = json.load(f)
                return len(conversation) if isinstance(conversation, list) else 0
        except:
            return 0
    
    async def _save_initial_conversation(self, state: WorkflowState, start_entry: Dict[str, Any]):
        """Save initial conversation entry"""
        conversation_path = os.path.join(state.run_dir, "conversation.json")
        
        try:
            with open(conversation_path, 'w', encoding='utf-8') as f:
                json.dump([start_entry], f, indent=2, ensure_ascii=False)
            
            state.artifacts["conversation_log"] = conversation_path
            
        except Exception as e:
            print(f"🔴 Error saving initial conversation: {str(e)}")
    
    async def _save_final_conversation(self, state: WorkflowState, final_data: Dict[str, Any]):
        """Save final conversation entry"""
        conversation_path = state.artifacts.get("conversation_log")
        if not conversation_path:
            return
        
        try:
            with open(conversation_path, 'r', encoding='utf-8') as f:
                conversation = json.load(f)
            
            final_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "WORKFLOW_COMPLETED",
                "data": final_data
            }
            
            conversation.append(final_entry)
            
            with open(conversation_path, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"🔴 Error saving final conversation: {str(e)}")
    
    async def _save_error_conversation(self, state: WorkflowState, error_data: Dict[str, Any]):
        """Save error conversation entry"""
        conversation_path = state.artifacts.get("conversation_log")
        if not conversation_path:
            return
        
        try:
            conversation = []
            if os.path.exists(conversation_path):
                with open(conversation_path, 'r', encoding='utf-8') as f:
                    conversation = json.load(f)
            
            error_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "WORKFLOW_ERROR",
                "data": error_data
            }
            
            conversation.append(error_entry)
            
            with open(conversation_path, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"🔴 Error saving error conversation: {str(e)}")
    
    async def _save_workflow_summary(self, state: WorkflowState, summary: Dict[str, Any]):
        """Save comprehensive workflow summary"""
        try:
            summary_path = os.path.join(state.run_dir, "workflow_summary.json")
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            state.artifacts["workflow_summary"] = summary_path
            
            # Also save human-readable summary
            await self._save_human_readable_summary(state, summary)
            
        except Exception as e:
            print(f"🔴 Error saving workflow summary: {str(e)}")
    
    async def _save_human_readable_summary(self, state: WorkflowState, summary: Dict[str, Any]):
        """Save human-readable workflow summary"""
        try:
            summary_txt_path = os.path.join(state.run_dir, "workflow_summary.txt")
            
            with open(summary_txt_path, 'w', encoding='utf-8') as f:
                f.write("GENERIC MULTI-AGENT AUTOMATION WORKFLOW - SUMMARY\\n")
                f.write("=" * 60 + "\\n\\n")
                
                f.write(f"Task ID: {summary['task_id']}\\n")
                f.write(f"Workflow Version: {summary['workflow_version']}\\n")
                f.write(f"Workflow Type: {summary['workflow_type']}\\n")
                f.write(f"User Task: {summary['user_task']}\\n")
                f.write(f"Task Category: {summary['task_category']}\\n")
                f.write(f"Platform: {summary['platform_detected']}\\n")
                f.write(f"Overall Success: {'✅' if summary['overall_success'] else '❌'}\\n")
                f.write(f"Total Time: {summary['total_execution_time']:.1f} seconds\\n\\n")
                
                f.write("AUTOMATION METRICS:\\n")
                f.write("-" * 20 + "\\n")
                metrics = summary['automation_metrics']
                f.write(f"Blueprint Steps: {metrics['blueprint_steps']}\\n")
                f.write(f"Execution Attempts: {metrics['execution_attempts']}\\n")
                f.write(f"Success Rate: {metrics['success_rate']:.1f}%\\n")
                f.write(f"Agent Collaborations: {metrics['agent_collaborations']}\\n")
                f.write(f"Overall Confidence: {metrics['overall_confidence']:.3f}\\n")
                f.write(f"Quality Assessment: {metrics['quality_assessment'].title()}\\n\\n")
                
                f.write("PHASE RESULTS:\\n")
                f.write("-" * 15 + "\\n")
                phases = summary['phase_results']
                
                f.write(f"Phase 1 - Document Processing: {'✅' if phases['phase1_document_processing']['success'] else '❌'}\\n")
                f.write(f"  Blueprint Confidence: {phases['phase1_document_processing']['blueprint_confidence']:.2f}\\n")
                f.write(f"  Task Category: {phases['phase1_document_processing']['task_category']}\\n\\n")
                
                f.write(f"Phase 2 - Code Generation: {'✅' if phases['phase2_code_generation']['success'] else '❌'}\\n")
                f.write(f"  Script Length: {phases['phase2_code_generation']['script_length']} chars\\n")
                f.write(f"  Script Type: {phases['phase2_code_generation']['script_type']}\\n\\n")
                
                f.write(f"Phase 3 - Execution: {'✅' if phases['phase3_execution_supervision']['success'] else '❌'}\\n")
                f.write(f"  Success Rate: {phases['phase3_execution_supervision']['success_rate']:.1f}%\\n")
                f.write(f"  Agent 2-3 Collaborations: {phases['phase3_execution_supervision']['agent2_collaborations']}\\n\\n")
                
                f.write(f"Phase 4 - Results Validation: {'✅' if phases['phase4_results_validation']['success'] else '❌'}\\n")
                f.write(f"  Final Confidence: {phases['phase4_results_validation']['confidence']:.3f}\\n\\n")
                
                f.write("MULTI-AGENT COMMUNICATION:\\n")
                f.write("-" * 30 + "\\n")
                comm = summary['multi_agent_communication']
                f.write(f"Agent 2-3 Collaborations: {comm['agent2_agent3_collaborations']}\\n")
                f.write(f"Communication Successful: {'✅' if comm['communication_successful'] else '❌'}\\n\\n")
                
                f.write(f"Generated at: {summary['timestamp']}\\n")
                f.write(f"Generic Multi-Agent Automation System v{summary['workflow_version']}\\n")
            
            state.artifacts["workflow_summary_txt"] = summary_txt_path
            
        except Exception as e:
            print(f"🔴 Error saving human-readable summary: {str(e)}")

# Global generic workflow instance
workflow = GenericMultiAgentWorkflow()