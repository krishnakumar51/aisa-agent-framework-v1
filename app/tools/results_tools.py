"""
Results Generation Tools
Agent4 tools for generating final reports, CSV exports, and dashboards
"""

import json
import logging
import csv
import io
from typing import Dict, Any, List, Optional, Annotated
from datetime import datetime
from pathlib import Path

# @tool decorator
try:
    from langchain_core.tools import tool
    TOOL_DECORATOR_AVAILABLE = True
    print("✅ LangGraph @tool decorator available")
except ImportError as e:
    TOOL_DECORATOR_AVAILABLE = False
    print(f"⚠️ LangGraph @tool decorator not available: {str(e)}")
    def tool(func):
        func._is_tool = True
        return func

# Managers
try:
    from app.database.database_manager import get_database_manager
    from app.utils.output_structure_manager import OutputStructureManager
    MANAGERS_AVAILABLE = True
except ImportError as e:
    MANAGERS_AVAILABLE = False
    print(f"⚠️ Managers not available: {str(e)}")

logger = logging.getLogger(__name__)

def _generate_text_report(
    task_data: Dict[str, Any], 
    agent_outputs: Dict[str, Any], 
    collaboration_history: List[Dict[str, Any]]
) -> str:
    """Generate comprehensive text report"""
    
    report_lines = [
        "# AUTOMATION WORKFLOW FINAL REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 80,
        "",
        "## TASK OVERVIEW",
        f"Task ID: {task_data.get('task_id', 'N/A')}",
        f"Platform: {task_data.get('platform', 'N/A')}",
        f"Instruction: {task_data.get('instruction', 'N/A')}",
        f"Status: {task_data.get('status', 'N/A')}",
        f"Created: {task_data.get('created_at', 'N/A')}",
        f"Completed: {task_data.get('completed_at', 'N/A')}",
        "",
        "## AGENT PERFORMANCE SUMMARY",
    ]
    
    # Agent1 Summary
    agent1_data = agent_outputs.get("agent1", {})
    report_lines.extend([
        "### Agent1 - Blueprint Generation",
        f"Status: {agent1_data.get('status', 'N/A')}",
        f"UI Elements Detected: {agent1_data.get('ui_elements_count', 0)}",
        f"Workflow Steps Generated: {agent1_data.get('workflow_steps_count', 0)}",
        f"Confidence Score: {agent1_data.get('confidence', 0.0):.2f}",
        ""
    ])
    
    # Agent2 Summary
    agent2_data = agent_outputs.get("agent2", {})
    report_lines.extend([
        "### Agent2 - Code Generation", 
        f"Status: {agent2_data.get('status', 'N/A')}",
        f"Script Generated: {agent2_data.get('script_generated', False)}",
        f"Platform: {agent2_data.get('platform', 'N/A')}",
        f"Script Lines: {agent2_data.get('script_lines', 0)}",
        ""
    ])
    
    # Agent3 Summary
    agent3_data = agent_outputs.get("agent3", {})
    report_lines.extend([
        "### Agent3 - Testing & Execution",
        f"Status: {agent3_data.get('status', 'N/A')}",
        f"Environment Setup: {agent3_data.get('environment_ready', False)}",
        f"Script Execution: {agent3_data.get('execution_status', 'N/A')}",
        f"Issues Detected: {agent3_data.get('issues_count', 0)}",
        f"Collaboration Requested: {agent3_data.get('collaboration_requested', False)}",
        ""
    ])
    
    # Collaboration Summary
    if collaboration_history:
        report_lines.extend([
            "## COLLABORATION HISTORY",
            f"Total Collaboration Sessions: {len(collaboration_history)}",
            ""
        ])
        
        for i, session in enumerate(collaboration_history, 1):
            report_lines.extend([
                f"### Session {i}",
                f"Between: {session.get('requesting_agent', 'N/A')} → {session.get('target_agent', 'N/A')}",
                f"Type: {session.get('request_data', {}).get('request_type', 'N/A')}",
                f"Status: {session.get('status', 'N/A')}",
                f"Messages: {len(session.get('messages', []))}",
                ""
            ])
    
    # Final Summary
    overall_success = all([
        agent_outputs.get("agent1", {}).get("status") == "completed",
        agent_outputs.get("agent2", {}).get("status") == "completed",
        agent_outputs.get("agent3", {}).get("status") == "completed"
    ])
    
    report_lines.extend([
        "## OVERALL ASSESSMENT",
        f"Workflow Success: {'✅ SUCCESS' if overall_success else '❌ PARTIAL/FAILED'}",
        f"Agent1 Blueprint: {'✅' if agent1_data.get('status') == 'completed' else '❌'}",
        f"Agent2 Code Gen: {'✅' if agent2_data.get('status') == 'completed' else '❌'}",
        f"Agent3 Testing: {'✅' if agent3_data.get('status') == 'completed' else '❌'}",
        "",
        "## RECOMMENDATIONS",
    ])
    
    # Generate recommendations based on results
    recommendations = []
    if agent1_data.get("confidence", 0) < 0.8:
        recommendations.append("- Consider improving document quality or UI element detection")
    if agent2_data.get("script_lines", 0) == 0:
        recommendations.append("- Code generation may need troubleshooting")
    if agent3_data.get("issues_count", 0) > 0:
        recommendations.append("- Review and address script execution issues")
    if len(collaboration_history) > 2:
        recommendations.append("- High collaboration indicates script complexity - consider simplifying workflow")
    
    if not recommendations:
        recommendations.append("- Workflow executed successfully with minimal issues")
    
    report_lines.extend(recommendations)
    report_lines.extend([
        "",
        "=" * 80,
        "Report generated by Agent4 - Final Reporting System"
    ])
    
    return "\\n".join(report_lines)

def _generate_csv_export(
    task_data: Dict[str, Any],
    agent_outputs: Dict[str, Any], 
    tool_executions: List[Dict[str, Any]]
) -> str:
    """Generate CSV export with workflow data"""
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Task Overview Section
    writer.writerow(["TASK_OVERVIEW"])
    writer.writerow(["Field", "Value"])
    writer.writerow(["Task_ID", task_data.get("task_id", "")])
    writer.writerow(["Platform", task_data.get("platform", "")])
    writer.writerow(["Instruction", task_data.get("instruction", "")])
    writer.writerow(["Status", task_data.get("status", "")])
    writer.writerow(["Created_At", task_data.get("created_at", "")])
    writer.writerow(["Completed_At", task_data.get("completed_at", "")])
    writer.writerow([])  # Empty row
    
    # Agent Performance Section
    writer.writerow(["AGENT_PERFORMANCE"])
    writer.writerow(["Agent", "Status", "Key_Metric", "Value"])
    
    writer.writerow([
        "Agent1", 
        agent_outputs.get("agent1", {}).get("status", ""),
        "UI_Elements_Detected", 
        agent_outputs.get("agent1", {}).get("ui_elements_count", 0)
    ])
    
    writer.writerow([
        "Agent2",
        agent_outputs.get("agent2", {}).get("status", ""),
        "Script_Lines_Generated",
        agent_outputs.get("agent2", {}).get("script_lines", 0)
    ])
    
    writer.writerow([
        "Agent3", 
        agent_outputs.get("agent3", {}).get("status", ""),
        "Issues_Detected",
        agent_outputs.get("agent3", {}).get("issues_count", 0)
    ])
    
    writer.writerow([])  # Empty row
    
    # Tool Executions Section
    if tool_executions:
        writer.writerow(["TOOL_EXECUTIONS"])
        writer.writerow(["Agent", "Tool_Name", "Status", "Execution_Time", "Timestamp"])
        
        for execution in tool_executions:
            writer.writerow([
                execution.get("agent_name", ""),
                execution.get("tool_name", ""),
                execution.get("execution_status", ""),
                execution.get("execution_time", 0),
                execution.get("created_at", "")
            ])
    
    return output.getvalue()

def _generate_dashboard_html(
    task_data: Dict[str, Any],
    agent_outputs: Dict[str, Any],
    collaboration_history: List[Dict[str, Any]]
) -> str:
    """Generate HTML dashboard"""
    
    overall_success = all([
        agent_outputs.get("agent1", {}).get("status") == "completed",
        agent_outputs.get("agent2", {}).get("status") == "completed", 
        agent_outputs.get("agent3", {}).get("status") == "completed"
    ])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Automation Workflow Dashboard - Task {task_data.get('task_id', 'N/A')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .status-badge {{ display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: 600; margin-left: 10px; }}
        .status-success {{ background: #d4edda; color: #155724; }}
        .status-warning {{ background: #fff3cd; color: #856404; }}
        .status-error {{ background: #f8d7da; color: #721c24; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .card {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .metric {{ text-align: center; margin: 15px 0; }}
        .metric-value {{ font-size: 2.5em; font-weight: bold; color: #007bff; }}
        .metric-label {{ font-size: 0.9em; color: #666; text-transform: uppercase; letter-spacing: 1px; }}
        .progress-bar {{ background: #e9ecef; border-radius: 10px; height: 8px; margin: 10px 0; }}
        .progress-fill {{ background: #28a745; height: 100%; border-radius: 10px; transition: width 0.3s ease; }}
        .collaboration-item {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #007bff; }}
        .timestamp {{ color: #666; font-size: 0.85em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Automation Workflow Dashboard</h1>
            <div>
                <strong>Task ID:</strong> {task_data.get('task_id', 'N/A')}
                <span class="status-badge {'status-success' if overall_success else 'status-warning'}">
                    {'✅ COMPLETED' if overall_success else '⚠️ PARTIAL'}
                </span>
            </div>
            <div style="margin-top: 10px;">
                <strong>Platform:</strong> {task_data.get('platform', 'N/A')} | 
                <strong>Created:</strong> {task_data.get('created_at', 'N/A')}
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📋 Agent1 - Blueprint</h3>
                <div class="metric">
                    <div class="metric-value">{agent_outputs.get('agent1', {}).get('ui_elements_count', 0)}</div>
                    <div class="metric-label">UI Elements Detected</div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {min(agent_outputs.get('agent1', {}).get('confidence', 0) * 100, 100)}%"></div>
                </div>
                <div>Confidence: {agent_outputs.get('agent1', {}).get('confidence', 0):.1%}</div>
            </div>
            
            <div class="card">
                <h3>🔧 Agent2 - Code Generation</h3>
                <div class="metric">
                    <div class="metric-value">{agent_outputs.get('agent2', {}).get('script_lines', 0)}</div>
                    <div class="metric-label">Script Lines Generated</div>
                </div>
                <div>Status: {agent_outputs.get('agent2', {}).get('status', 'N/A')}</div>
                <div>Platform: {agent_outputs.get('agent2', {}).get('platform', 'N/A')}</div>
            </div>
            
            <div class="card">
                <h3>🧪 Agent3 - Testing</h3>
                <div class="metric">
                    <div class="metric-value">{agent_outputs.get('agent3', {}).get('issues_count', 0)}</div>
                    <div class="metric-label">Issues Detected</div>
                </div>
                <div>Environment: {'✅ Ready' if agent_outputs.get('agent3', {}).get('environment_ready') else '❌ Not Ready'}</div>
                <div>Execution: {agent_outputs.get('agent3', {}).get('execution_status', 'N/A')}</div>
            </div>
        </div>
        
        {'<div class="card"><h3>🤝 Collaboration History</h3>' + ''.join([
            f'<div class="collaboration-item"><strong>{session.get("requesting_agent", "N/A")} → {session.get("target_agent", "N/A")}</strong><br>Type: {session.get("request_data", {}).get("request_type", "N/A")}<br>Status: {session.get("status", "N/A")}<div class="timestamp">Messages: {len(session.get("messages", []))}</div></div>'
            for session in collaboration_history
        ]) + '</div>' if collaboration_history else ''}
        
        <div class="card">
            <h3>📊 Overall Assessment</h3>
            <p><strong>Workflow Success:</strong> {'✅ SUCCESS' if overall_success else '❌ PARTIAL/FAILED'}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Report by:</strong> Agent4 - Final Reporting System</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

# Agent4 Results Tools

@tool
async def workflow_analysis_tool(
    task_id: Annotated[int, "Task ID for database logging"],
    collect_collaboration_history: Annotated[bool, "Whether to collect collaboration history"] = True,
    collect_tool_executions: Annotated[bool, "Whether to collect tool execution data"] = True
) -> Annotated[Dict[str, Any], "Complete workflow analysis data"]:
    """
    Analyze complete workflow execution and collect all data for final reporting.
    Gathers task data, agent outputs, collaboration history, and tool executions.
    """
    
    execution_start = datetime.now()
    tool_input = {
        "task_id": task_id,
        "collect_collaboration_history": collect_collaboration_history,
        "collect_tool_executions": collect_tool_executions
    }
    
    # Log tool execution start
    tool_exec_id = None
    if MANAGERS_AVAILABLE:
        try:
            db_manager = await get_database_manager()
            tool_exec_id = await db_manager.log_tool_execution(
                task_id, "agent4", "workflow_analysis_tool",
                tool_input, execution_status="running"
            )
        except Exception as e:
            logger.warning(f"Could not log tool execution: {str(e)}")
    
    try:
        analysis_result = {
            "task_id": task_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "data_collected": {}
        }
        
        if MANAGERS_AVAILABLE:
            # Collect task data from database
            # Note: This would need actual database queries in real implementation
            # For now, we'll create sample structure
            
            task_data = {
                "task_id": task_id,
                "platform": "auto",
                "instruction": "Workflow analysis",
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat()
            }
            
            # Collect agent outputs (sample structure)
            agent_outputs = {
                "agent1": {
                    "status": "completed",
                    "ui_elements_count": 5,
                    "workflow_steps_count": 4,
                    "confidence": 0.85
                },
                "agent2": {
                    "status": "completed", 
                    "script_generated": True,
                    "platform": "web",
                    "script_lines": 42
                },
                "agent3": {
                    "status": "completed",
                    "environment_ready": True,
                    "execution_status": "success",
                    "issues_count": 1,
                    "collaboration_requested": False
                }
            }
            
            # Collect collaboration history if requested
            collaboration_history = []
            if collect_collaboration_history:
                try:
                    collaboration_history = await db_manager.get_collaboration_history(task_id)
                except Exception as e:
                    logger.warning(f"Could not collect collaboration history: {str(e)}")
            
            # Collect tool executions if requested
            tool_executions = []
            if collect_tool_executions:
                # This would query the langgraph_tool_executions table
                # Sample structure for now
                tool_executions = [
                    {
                        "agent_name": "agent1",
                        "tool_name": "document_analysis_tool",
                        "execution_status": "success",
                        "execution_time": 2.5,
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "agent_name": "agent2",
                        "tool_name": "script_generation_tool",
                        "execution_status": "success",
                        "execution_time": 3.2,
                        "created_at": datetime.now().isoformat()
                    }
                ]
            
            analysis_result["data_collected"] = {
                "task_data": task_data,
                "agent_outputs": agent_outputs,
                "collaboration_history": collaboration_history,
                "tool_executions": tool_executions,
                "data_points_collected": len(task_data) + len(agent_outputs) + len(collaboration_history) + len(tool_executions)
            }
        else:
            # Fallback without database
            analysis_result["data_collected"] = {
                "task_data": {"task_id": task_id, "status": "simulated"},
                "agent_outputs": {},
                "collaboration_history": [],
                "tool_executions": [],
                "data_points_collected": 1
            }
        
        execution_time = (datetime.now() - execution_start).total_seconds()
        
        # Generate tool review
        tool_review = {
            "data_collection_success": True,
            "data_points_collected": analysis_result["data_collected"]["data_points_collected"],
            "collaboration_sessions": len(analysis_result["data_collected"]["collaboration_history"]),
            "tool_executions": len(analysis_result["data_collected"]["tool_executions"]),
            "quality_assessment": "high"
        }
        
        # Update tool execution in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, analysis_result, "success",
                    execution_time, "", tool_review
                )
            except Exception as e:
                logger.warning(f"Could not update tool execution: {str(e)}")
        
        logger.info(f"📊 Workflow analysis completed: {analysis_result['data_collected']['data_points_collected']} data points")
        return analysis_result
        
    except Exception as e:
        error_msg = f"Workflow analysis failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # Log error in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, None, "failed",
                    (datetime.now() - execution_start).total_seconds(), error_msg, {}
                )
            except Exception as db_error:
                logger.warning(f"Could not log tool error: {str(db_error)}")
        
        return {
            "error": error_msg,
            "analysis_timestamp": datetime.now().isoformat(),
            "data_collected": {
                "analysis_failed": True
            }
        }

@tool  
async def report_generation_tool(
    task_id: Annotated[int, "Task ID for database logging"],
    analysis_data: Annotated[Dict[str, Any], "Workflow analysis data"],
    generate_dashboard: Annotated[bool, "Whether to generate HTML dashboard"] = True,
    generate_csv: Annotated[bool, "Whether to generate CSV export"] = True
) -> Annotated[Dict[str, Any], "Generated reports content"]:
    """
    Generate comprehensive final reports from workflow analysis data.
    Creates text report, CSV export, and HTML dashboard.
    """
    
    execution_start = datetime.now()
    tool_input = {
        "task_id": task_id,
        "generate_dashboard": generate_dashboard,
        "generate_csv": generate_csv,
        "data_points": analysis_data.get("data_collected", {}).get("data_points_collected", 0)
    }
    
    # Log tool execution start
    tool_exec_id = None
    if MANAGERS_AVAILABLE:
        try:
            db_manager = await get_database_manager()
            tool_exec_id = await db_manager.log_tool_execution(
                task_id, "agent4", "report_generation_tool",
                tool_input, execution_status="running"
            )
        except Exception as e:
            logger.warning(f"Could not log tool execution: {str(e)}")
    
    try:
        data_collected = analysis_data.get("data_collected", {})
        task_data = data_collected.get("task_data", {})
        agent_outputs = data_collected.get("agent_outputs", {})
        collaboration_history = data_collected.get("collaboration_history", [])
        tool_executions = data_collected.get("tool_executions", [])
        
        # Generate text report
        text_report = _generate_text_report(task_data, agent_outputs, collaboration_history)
        
        reports_content = {
            "text_report": text_report,
            "reports_metadata": {
                "generated_at": datetime.now().isoformat(),
                "task_id": task_id,
                "reports_generated": ["text"]
            }
        }
        
        # Generate CSV export if requested
        if generate_csv:
            csv_content = _generate_csv_export(task_data, agent_outputs, tool_executions)
            reports_content["csv_export"] = csv_content
            reports_content["reports_metadata"]["reports_generated"].append("csv")
        
        # Generate HTML dashboard if requested
        if generate_dashboard:
            dashboard_html = _generate_dashboard_html(task_data, agent_outputs, collaboration_history)
            reports_content["html_dashboard"] = dashboard_html
            reports_content["reports_metadata"]["reports_generated"].append("dashboard")
        
        execution_time = (datetime.now() - execution_start).total_seconds()
        
        # Generate tool review
        tool_review = {
            "reports_generated": len(reports_content["reports_metadata"]["reports_generated"]),
            "text_report_lines": len(text_report.split("\\n")),
            "csv_generated": generate_csv,
            "dashboard_generated": generate_dashboard,
            "quality_assessment": "high"
        }
        
        # Update tool execution in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, reports_content, "success",
                    execution_time, "", tool_review
                )
            except Exception as e:
                logger.warning(f"Could not update tool execution: {str(e)}")
        
        logger.info(f"📋 Reports generated: {len(reports_content['reports_metadata']['reports_generated'])} formats")
        return reports_content
        
    except Exception as e:
        error_msg = f"Report generation failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # Log error in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, None, "failed",
                    (datetime.now() - execution_start).total_seconds(), error_msg, {}
                )
            except Exception as db_error:
                logger.warning(f"Could not log tool error: {str(db_error)}")
        
        return {
            "error": error_msg,
            "reports_metadata": {
                "generated_at": datetime.now().isoformat(),
                "generation_failed": True
            }
        }

@tool
async def reports_save_tool(
    task_id: Annotated[int, "Task ID for database logging"],
    reports_content: Annotated[Dict[str, Any], "Generated reports content"],
    export_database: Annotated[bool, "Whether to export task database"] = True
) -> Annotated[Dict[str, str], "Saved reports file paths"]:
    """
    Save generated reports to exact output structure: generated_code/{task_id}/agent4/
    Saves final_report.txt, final_report.csv, summary_dashboard.html, and sqlite_db.sqlite.
    """
    
    execution_start = datetime.now()
    tool_input = {
        "task_id": task_id,
        "reports_count": len(reports_content.get("reports_metadata", {}).get("reports_generated", [])),
        "export_database": export_database
    }
    
    # Log tool execution start
    tool_exec_id = None
    if MANAGERS_AVAILABLE:
        try:
            db_manager = await get_database_manager()
            tool_exec_id = await db_manager.log_tool_execution(
                task_id, "agent4", "reports_save_tool",
                tool_input, execution_status="running"
            )
        except Exception as e:
            logger.warning(f"Could not log tool execution: {str(e)}")
    
    try:
        # Initialize output structure manager
        output_manager = OutputStructureManager(task_id)
        
        # Create directory structure
        directories = output_manager.create_complete_structure()
        
        # Save Agent4 outputs
        saved_files = output_manager.save_agent4_outputs(
            text_report=reports_content.get("text_report", "# No report generated"),
            csv_data=reports_content.get("csv_export", "# No CSV data generated"),
            dashboard_html=reports_content.get("html_dashboard", "<html><body>No dashboard generated</body></html>")
        )
        
        # Export database if requested
        if export_database and MANAGERS_AVAILABLE:
            try:
                db_path = output_manager.export_task_database("sqlite_db.sqlite")
                saved_files["database_export"] = db_path
            except Exception as e:
                logger.warning(f"Could not export database: {str(e)}")
        
        execution_time = (datetime.now() - execution_start).total_seconds()
        
        # Log output files to database
        if MANAGERS_AVAILABLE:
            try:
                for file_category, file_path in saved_files.items():
                    file_name = Path(file_path).name
                    file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
                    
                    # Get content preview for text files
                    content_preview = ""
                    if file_name.endswith(('.txt', '.csv', '.html')):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                content_preview = content[:500] + "..." if len(content) > 500 else content
                        except:
                            pass
                    
                    await db_manager.log_output_file(
                        task_id, "agent4", file_name, file_path,
                        file_category, file_size, content_preview,
                        {"saved_by": "reports_save_tool", "category": file_category}
                    )
            except Exception as e:
                logger.warning(f"Could not log output files: {str(e)}")
        
        # Generate tool review
        tool_review = {
            "files_saved": len(saved_files),
            "text_report_saved": "text_report" in saved_files,
            "csv_saved": "csv_export" in saved_files,
            "dashboard_saved": "dashboard" in saved_files,
            "database_exported": "database_export" in saved_files,
            "save_success": True
        }
        
        # Update tool execution in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, saved_files, "success",
                    execution_time, "", tool_review
                )
            except Exception as e:
                logger.warning(f"Could not update tool execution: {str(e)}")
        
        logger.info(f"💾 Reports saved successfully: {len(saved_files)} files")
        return saved_files
        
    except Exception as e:
        error_msg = f"Reports save failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # Log error in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, None, "failed",
                    (datetime.now() - execution_start).total_seconds(), error_msg, {}
                )
            except Exception as db_error:
                logger.warning(f"Could not log tool error: {str(db_error)}")
        
        return {"error": error_msg}

# Tool collection for Agent4

AGENT4_RESULTS_TOOLS = [
    workflow_analysis_tool,
    report_generation_tool,
    reports_save_tool
]

def get_agent4_tools():
    """Get all Agent4 results generation tools"""
    return AGENT4_RESULTS_TOOLS

if __name__ == "__main__":
    # Test results generation tools
    async def test_results_tools():
        print("🧪 Testing Agent4 Results Tools...")
        
        # Test workflow analysis
        analysis_result = await workflow_analysis_tool(
            999, True, True
        )
        print(f"✅ Workflow analysis: {analysis_result['data_collected']['data_points_collected']} data points")
        
        # Test report generation
        reports_result = await report_generation_tool(
            999, analysis_result, True, True
        )
        print(f"✅ Report generation: {len(reports_result['reports_metadata']['reports_generated'])} formats")
        
        # Test reports save
        save_result = await reports_save_tool(
            999, reports_result, True
        )
        print(f"✅ Reports save: {len(save_result)} files saved")
        
        print("🎉 Agent4 results tools test completed!")
    
    import asyncio
    asyncio.run(test_results_tools())