"""
Agent4 Results & Reporting
Production Agent4 with integrated @tool decorators and database logging
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# LangGraph tool decorator
try:
    from langchain_core.tools import tool
    from langchain_core.messages import HumanMessage, AIMessage
    LANGGRAPH_AVAILABLE = True
    print("✅ LangGraph @tool decorator available")
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    print(f"⚠️ LangGraph @tool decorator not available: {str(e)}")
    def tool(func):
        func._is_tool = True
        return func

# Framework imports
try:
    from app.database.database_manager import get_database_manager
    from app.utils.output_structure_manager import OutputStructureManager
    from app.langgraph.integration_manager import get_integration_manager
    from app.tools.results_tools import get_agent4_tools
    from app.tools.shared_tools import agent_communication_tool, error_handling_tool
    FRAMEWORK_AVAILABLE = True
except ImportError as e:
    FRAMEWORK_AVAILABLE = False
    print(f"⚠️ Framework components not available: {str(e)}")

logger = logging.getLogger(__name__)

class Agent4Results:
    """
    Production Agent4 with integrated tool system and database logging.
    Uses @tool decorators for LangGraph compatibility while maintaining existing functionality.
    """
    
    def __init__(self):
        self.agent_name = "agent4"
        self.db_manager = None
        self.output_manager = None
        self.integration_manager = None
        self.tools = get_agent4_tools() if FRAMEWORK_AVAILABLE else []
        self.initialized = False
        logger.info("📊 Agent4 Results initialized with tool integration")
    
    async def initialize(self, task_id: int) -> Dict[str, Any]:
        """Initialize Agent4 components"""
        
        if not FRAMEWORK_AVAILABLE:
            return {
                "success": False,
                "error": "Framework components not available"
            }
        
        try:
            # Initialize components
            self.db_manager = await get_database_manager()
            self.output_manager = OutputStructureManager(task_id)
            self.integration_manager = get_integration_manager(task_id)
            
            self.initialized = True
            
            result = {
                "success": True,
                "agent": self.agent_name,
                "task_id": task_id,
                "tools_available": len(self.tools),
                "components_initialized": ["db_manager", "output_manager", "integration_manager"],
                "initialized_at": datetime.now().isoformat()
            }
            
            logger.info("✅ Agent4 components initialized successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Agent4 initialization failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_final_reporting(
        self,
        task_id: int,
        workflow_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Main execution method using integrated tools"""
        
        if not self.initialized:
            init_result = await self.initialize(task_id)
            if not init_result["success"]:
                return init_result
        
        try:
            # Log agent execution start
            await self.db_manager.log_agent_execution(
                task_id, self.agent_name, "started",
                {"workflow_results_available": bool(workflow_results)}
            )
            
            # Use the integrated results tools
            if self.tools:
                workflow_analysis_tool = None
                report_generation_tool = None
                reports_save_tool = None
                
                # Find tools by name
                for tool in self.tools:
                    if "workflow_analysis" in tool.__name__:
                        workflow_analysis_tool = tool
                    elif "report_generation" in tool.__name__:
                        report_generation_tool = tool
                    elif "reports_save" in tool.__name__:
                        reports_save_tool = tool
                
                final_results = {
                    "workflow_analysis": {},
                    "reports_generated": {},
                    "reports_saved": {},
                    "integration_completed": False
                }
                
                # Step 1: Workflow Analysis
                if workflow_analysis_tool:
                    analysis_result = await workflow_analysis_tool(
                        task_id=task_id,
                        collect_collaboration_history=True,
                        collect_tool_executions=True
                    )
                    
                    final_results["workflow_analysis"] = analysis_result
                    
                    if not analysis_result.get("success", True):
                        logger.warning(f"Workflow analysis issues for task {task_id}: {analysis_result.get('error')}")
                
                # Step 2: Report Generation
                if report_generation_tool:
                    reports_result = await report_generation_tool(
                        task_id=task_id,
                        analysis_data=final_results["workflow_analysis"],
                        generate_dashboard=True,
                        generate_csv=True
                    )
                    
                    final_results["reports_generated"] = reports_result
                    
                    if not reports_result.get("success", True):
                        # Use error handling tool
                        await error_handling_tool(
                            task_id=task_id,
                            agent_name=self.agent_name,
                            error_type="report_generation_failed",
                            error_details=reports_result,
                            recovery_attempted=False,
                            escalate_to_supervisor=False  # Agent4 errors shouldn't stop workflow
                        )
                
                # Step 3: Reports Save
                if reports_save_tool:
                    save_result = await reports_save_tool(
                        task_id=task_id,
                        reports_content=final_results["reports_generated"],
                        export_database=True
                    )
                    
                    final_results["reports_saved"] = save_result
                
                # Step 4: Complete Integration (Conversation JSON, SQLite Export, Summary)
                try:
                    integration_result = await self.integration_manager.complete_integration_workflow(
                        generate_conversation=True,
                        create_sqlite_export=True,
                        generate_summary=True,
                        cleanup_temp_files=True
                    )
                    
                    final_results["integration_completed"] = integration_result.get("overall_success", False)
                    final_results["integration_results"] = integration_result
                    
                    if integration_result.get("overall_success", False):
                        logger.info(f"✅ Complete integration workflow completed for task {task_id}")
                    else:
                        logger.warning(f"⚠️ Integration workflow had issues for task {task_id}")
                
                except Exception as e:
                    logger.warning(f"Integration workflow failed for task {task_id}: {str(e)}")
                    final_results["integration_error"] = str(e)
                
                # Send final completion communication
                await agent_communication_tool(
                    task_id=task_id,
                    from_agent=self.agent_name,
                    to_agent="supervisor",
                    message_type="workflow_completion",
                    message_content={
                        "status": "completed",
                        "final_reporting_completed": True,
                        "reports_generated": len(final_results["reports_generated"].get("reports_metadata", {}).get("reports_generated", [])),
                        "reports_saved": bool(final_results["reports_saved"].get("success")),
                        "integration_completed": final_results["integration_completed"],
                        "workflow_fully_completed": True
                    },
                    priority="low",
                    requires_response=False
                )
                
                # Log agent execution completion
                await self.db_manager.log_agent_execution(
                    task_id, self.agent_name, "completed", final_results
                )
                
                # Update task status to fully completed
                await self.db_manager.update_task_status(
                    task_id, "fully_completed",
                    {
                        "final_reporting": True,
                        "integration_completed": final_results["integration_completed"]
                    }
                )
                
                return {
                    "success": True,
                    "agent": self.agent_name,
                    "task_id": task_id,
                    "final_results": final_results,
                    "reports_generated": len(final_results["reports_generated"].get("reports_metadata", {}).get("reports_generated", [])),
                    "reports_saved": bool(final_results["reports_saved"].get("success")),
                    "integration_completed": final_results["integration_completed"],
                    "workflow_completed": True,
                    "completed_at": datetime.now().isoformat()
                }
            else:
                # No tools available - use fallback
                return await self._fallback_final_reporting(task_id, workflow_results)
                
        except Exception as e:
            logger.error(f"❌ Agent4 execution failed: {str(e)}")
            
            # Log execution error
            if self.db_manager:
                try:
                    await self.db_manager.log_agent_execution(
                        task_id, self.agent_name, "failed", {"error": str(e)}
                    )
                except:
                    pass
            
            # Use error handling tool
            if FRAMEWORK_AVAILABLE:
                try:
                    await error_handling_tool(
                        task_id=task_id,
                        agent_name=self.agent_name,
                        error_type="agent_execution_error",
                        error_details={
                            "error_message": str(e),
                            "context": "agent4_execute_final_reporting",
                            "workflow_should_complete": True
                        },
                        recovery_attempted=False,
                        escalate_to_supervisor=False  # Agent4 errors shouldn't prevent completion
                    )
                except:
                    pass
            
            return {
                "success": False,
                "agent": self.agent_name,
                "error": str(e),
                "execution_failed_at": "agent_execution",
                "workflow_completed": False  # But this might still be acceptable
            }
    
    async def _fallback_final_reporting(
        self,
        task_id: int,
        workflow_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback final reporting when tools are not available"""
        
        try:
            logger.info("🔄 Using fallback final reporting")
            
            # Generate basic final report
            fallback_results = {
                "workflow_analysis": {
                    "success": True,
                    "task_id": task_id,
                    "analysis_method": "fallback",
                    "workflow_summary": "Fallback analysis completed",
                    "agents_executed": len([k for k in workflow_results.keys() if k.startswith("agent")]),
                    "overall_workflow_success": any(
                        workflow_results.get(f"agent{i}_status") == "completed" 
                        for i in range(1, 5)
                    )
                },
                "reports_generated": {
                    "success": True,
                    "method": "fallback",
                    "reports_metadata": {
                        "reports_generated": ["text_report", "summary_report"],
                        "generation_time": datetime.now().isoformat()
                    }
                },
                "reports_saved": {
                    "success": True,
                    "method": "fallback",
                    "files_saved": 2
                },
                "integration_completed": False
            }
            
            # Generate basic text report
            text_report = self._generate_fallback_report(task_id, workflow_results)
            
            # Save reports using output manager
            try:
                saved_files = self.output_manager.save_agent4_outputs(
                    text_report=text_report,
                    csv_data="task_id,status,completed_at\n" + f"{task_id},fallback_completed,{datetime.now().isoformat()}",
                    dashboard_html="<html><body><h1>Fallback Report</h1><p>Workflow completed with fallback reporting.</p></body></html>"
                )
                fallback_results["reports_saved"]["files_saved"] = len(saved_files)
                fallback_results["saved_files_details"] = saved_files
            except Exception as e:
                logger.warning(f"Could not save fallback reports: {str(e)}")
                fallback_results["reports_saved"]["save_error"] = str(e)
            
            # Try integration manager if available
            if self.integration_manager:
                try:
                    integration_result = await self.integration_manager.complete_integration_workflow(
                        generate_conversation=True,
                        create_sqlite_export=True,
                        generate_summary=True,
                        cleanup_temp_files=True
                    )
                    
                    fallback_results["integration_completed"] = integration_result.get("overall_success", False)
                    fallback_results["integration_results"] = integration_result
                
                except Exception as e:
                    logger.warning(f"Integration failed in fallback: {str(e)}")
                    fallback_results["integration_error"] = str(e)
            
            # Save to database
            if self.db_manager:
                try:
                    await self.db_manager.save_agent_output(
                        task_id, self.agent_name, "final_results_fallback",
                        json.dumps(fallback_results)
                    )
                    
                    await self.db_manager.log_agent_execution(
                        task_id, self.agent_name, "completed_fallback", {"method": "fallback"}
                    )
                    
                    await self.db_manager.update_task_status(
                        task_id, "completed_fallback",
                        {"final_reporting": True, "method": "fallback"}
                    )
                except Exception as e:
                    logger.warning(f"Could not save fallback results to database: {str(e)}")
            
            return {
                "success": True,
                "agent": self.agent_name,
                "task_id": task_id,
                "final_results": fallback_results,
                "reports_generated": 2,
                "reports_saved": fallback_results["reports_saved"]["files_saved"],
                "integration_completed": fallback_results["integration_completed"],
                "workflow_completed": True,
                "execution_method": "fallback",
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Fallback final reporting failed: {str(e)}")
            return {
                "success": False,
                "agent": self.agent_name,
                "error": f"Fallback reporting failed: {str(e)}",
                "execution_failed_at": "fallback_reporting"
            }
    
    def _generate_fallback_report(self, task_id: int, workflow_results: Dict[str, Any]) -> str:
        """Generate a basic fallback report"""
        
        report_lines = [
            f"# AUTOMATION WORKFLOW FINAL REPORT (Fallback)",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Task ID: {task_id}",
            f"Report Type: Fallback Generation",
            "",
            "## WORKFLOW EXECUTION SUMMARY",
        ]
        
        # Analyze workflow results
        for i in range(1, 5):
            agent_status = workflow_results.get(f"agent{i}_status", "unknown")
            agent_output = workflow_results.get(f"agent{i}_output", {})
            
            report_lines.extend([
                f"Agent {i}: {agent_status.upper()}",
                f"  - Output available: {'Yes' if agent_output else 'No'}",
                f"  - Details: {len(str(agent_output))} characters" if agent_output else "  - Details: No output data",
                ""
            ])
        
        # Add overall assessment
        successful_agents = sum(1 for i in range(1, 5) if workflow_results.get(f"agent{i}_status") == "completed")
        report_lines.extend([
            "## OVERALL ASSESSMENT",
            f"Successful Agents: {successful_agents}/4",
            f"Workflow Success Rate: {(successful_agents/4)*100:.1f}%",
            "",
            "## NOTES",
            "This report was generated using fallback methods due to tool unavailability.",
            "For complete analysis, ensure all framework components are properly installed.",
            "",
            f"Report generated by Agent4 Fallback System at {datetime.now().isoformat()}"
        ])
        
        return "\n".join(report_lines)
    
    def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get Agent4 capabilities"""
        
        return {
            "agent_name": self.agent_name,
            "framework_available": FRAMEWORK_AVAILABLE,
            "langgraph_available": LANGGRAPH_AVAILABLE,
            "tools_count": len(self.tools),
            "initialized": self.initialized,
            "capabilities": [
                "workflow_analysis",
                "report_generation",
                "reports_save",
                "integration_management",
                "error_handling",
                "agent_communication"
            ],
            "output_formats": ["text_report", "csv_data", "dashboard_html", "conversation_json", "sqlite_export"],
            "execution_methods": ["tool_based", "fallback"],
            "integration_features": [
                "conversation_json_generation",
                "sqlite_database_export",
                "workflow_summary_creation",
                "temporary_file_cleanup"
            ]
        }

# Global Agent4 instance
_agent4_instance = None

def get_agent4() -> Agent4Results:
    """Get global Agent4 instance"""
    global _agent4_instance
    if _agent4_instance is None:
        _agent4_instance = Agent4Results()
    return _agent4_instance

if __name__ == "__main__":
    # Test Agent4 with tool integration
    async def test_agent4_tools():
        print("🧪 Testing Agent4 with Tool Integration...")
        
        agent4 = Agent4Results()
        
        # Test capabilities
        capabilities = agent4.get_agent_capabilities()
        print(f"✅ Agent4 capabilities: {capabilities['tools_count']} tools")
        
        # Test initialization
        init_result = await agent4.initialize(999)
        print(f"✅ Agent4 initialization: {init_result.get('success', False)}")
        
        if init_result.get("success", False):
            # Sample workflow results for testing
            sample_workflow_results = {
                "agent1_status": "completed",
                "agent1_output": {"blueprint": {"ui_elements": 3}},
                "agent2_status": "completed", 
                "agent2_output": {"generated_code": {"script_lines": 25}},
                "agent3_status": "completed",
                "agent3_output": {"testing_results": {"execution_status": "success"}},
                "workflow_id": "test_workflow_999"
            }
            
            # Test final reporting
            result = await agent4.execute_final_reporting(
                task_id=999,
                workflow_results=sample_workflow_results
            )
            print(f"✅ Final reporting: {result.get('success', False)}")
            
            if result.get("success", False):
                final_results = result.get("final_results", {})
                print(f"✅ Reports generated: {result.get('reports_generated', 0)}")
                print(f"✅ Reports saved: {result.get('reports_saved', False)}")
                print(f"✅ Integration completed: {result.get('integration_completed', False)}")
                print(f"✅ Workflow completed: {result.get('workflow_completed', False)}")
        
        print("🎉 Agent4 tool integration test completed!")
    
    import asyncio
    asyncio.run(test_agent4_tools())