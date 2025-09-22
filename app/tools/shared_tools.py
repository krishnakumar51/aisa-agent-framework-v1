"""
Shared Communication Tools
Cross-agent tools for collaboration, error handling, and shared utilities
"""

import json
import logging
from typing import Dict, Any, List, Optional, Annotated
from datetime import datetime

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

# Shared Communication Tools

@tool
async def agent_communication_tool(
    task_id: Annotated[int, "Task ID for database logging"],
    from_agent: Annotated[str, "Source agent name"],
    to_agent: Annotated[str, "Target agent name"],
    message_type: Annotated[str, "Type of message"],
    message_content: Annotated[Dict[str, Any], "Message content"],
    priority: Annotated[str, "Message priority: low, medium, high"] = "medium",
    requires_response: Annotated[bool, "Whether message requires a response"] = False
) -> Annotated[Dict[str, Any], "Communication result"]:
    """
    Send structured communication between agents.
    Handles collaboration requests, status updates, error notifications, and responses.
    """
    
    execution_start = datetime.now()
    tool_input = {
        "task_id": task_id,
        "from_agent": from_agent,
        "to_agent": to_agent,
        "message_type": message_type,
        "priority": priority,
        "requires_response": requires_response
    }
    
    # Log tool execution start
    tool_exec_id = None
    if MANAGERS_AVAILABLE:
        try:
            db_manager = await get_database_manager()
            tool_exec_id = await db_manager.log_tool_execution(
                task_id, from_agent, "agent_communication_tool",
                tool_input, execution_status="running"
            )
        except Exception as e:
            logger.warning(f"Could not log tool execution: {str(e)}")
    
    try:
        # Create structured communication
        communication = {
            "communication_id": f"comm_{task_id}_{int(datetime.now().timestamp())}",
            "from_agent": from_agent,
            "to_agent": to_agent,
            "message_type": message_type,
            "message_content": message_content,
            "priority": priority,
            "requires_response": requires_response,
            "timestamp": datetime.now().isoformat(),
            "communication_metadata": {
                "message_size": len(json.dumps(message_content)),
                "formatted_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        # Save to database
        if MANAGERS_AVAILABLE:
            try:
                comm_id = await db_manager.save_agent_communication_with_langgraph(
                    task_id, from_agent, to_agent, message_type,
                    json.dumps(message_content),
                    review_data={
                        "priority": priority,
                        "requires_response": requires_response,
                        "communication_id": communication["communication_id"]
                    }
                )
                communication["database_id"] = comm_id
            except Exception as e:
                logger.warning(f"Could not save communication to database: {str(e)}")
        
        execution_time = (datetime.now() - execution_start).total_seconds()
        
        # Generate tool review
        tool_review = {
            "communication_sent": True,
            "message_type": message_type,
            "priority": priority,
            "target_agent": to_agent,
            "requires_response": requires_response,
            "quality_assessment": "high"
        }
        
        # Update tool execution in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, communication, "success",
                    execution_time, "", tool_review
                )
            except Exception as e:
                logger.warning(f"Could not update tool execution: {str(e)}")
        
        logger.info(f"📨 Communication sent: {from_agent} → {to_agent} ({message_type})")
        return communication
        
    except Exception as e:
        error_msg = f"Agent communication failed: {str(e)}"
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
            "communication_sent": False,
            "communication_metadata": {
                "communication_failed": True,
                "error_timestamp": datetime.now().isoformat()
            }
        }

@tool
async def error_handling_tool(
    task_id: Annotated[int, "Task ID for database logging"],
    agent_name: Annotated[str, "Agent reporting the error"],
    error_type: Annotated[str, "Type of error"],
    error_details: Annotated[Dict[str, Any], "Detailed error information"],
    recovery_attempted: Annotated[bool, "Whether recovery was attempted"] = False,
    escalate_to_supervisor: Annotated[bool, "Whether to escalate to supervisor"] = True
) -> Annotated[Dict[str, Any], "Error handling result"]:
    """
    Handle errors across agents with structured logging and recovery recommendations.
    Provides error categorization, recovery suggestions, and escalation.
    """
    
    execution_start = datetime.now()
    tool_input = {
        "task_id": task_id,
        "agent_name": agent_name,
        "error_type": error_type,
        "recovery_attempted": recovery_attempted,
        "escalate_to_supervisor": escalate_to_supervisor
    }
    
    # Log tool execution start
    tool_exec_id = None
    if MANAGERS_AVAILABLE:
        try:
            db_manager = await get_database_manager()
            tool_exec_id = await db_manager.log_tool_execution(
                task_id, agent_name, "error_handling_tool",
                tool_input, execution_status="running"
            )
        except Exception as e:
            logger.warning(f"Could not log tool execution: {str(e)}")
    
    try:
        # Categorize error severity
        severity = _categorize_error_severity(error_type, error_details)
        
        # Generate recovery recommendations
        recovery_recommendations = _generate_recovery_recommendations(error_type, error_details, agent_name)
        
        error_report = {
            "error_id": f"error_{task_id}_{int(datetime.now().timestamp())}",
            "task_id": task_id,
            "reporting_agent": agent_name,
            "error_type": error_type,
            "severity": severity,
            "error_details": error_details,
            "recovery_attempted": recovery_attempted,
            "recovery_recommendations": recovery_recommendations,
            "escalate_to_supervisor": escalate_to_supervisor,
            "timestamp": datetime.now().isoformat(),
            "error_metadata": {
                "error_context": error_details.get("context", ""),
                "affected_components": error_details.get("affected_components", []),
                "can_continue_workflow": severity != "critical"
            }
        }
        
        # Log error to database
        if MANAGERS_AVAILABLE:
            try:
                # Save as agent communication for error tracking
                await db_manager.save_agent_communication_with_langgraph(
                    task_id, agent_name, "supervisor", "error_report",
                    json.dumps(error_report),
                    review_data={
                        "severity": severity,
                        "escalated": escalate_to_supervisor,
                        "error_id": error_report["error_id"]
                    }
                )
            except Exception as e:
                logger.warning(f"Could not save error report to database: {str(e)}")
        
        # Send supervisor notification if escalation requested
        if escalate_to_supervisor:
            supervisor_notification = {
                "notification_type": "error_escalation",
                "error_id": error_report["error_id"],
                "severity": severity,
                "reporting_agent": agent_name,
                "requires_intervention": severity in ["high", "critical"],
                "recovery_recommendations": recovery_recommendations
            }
            
            if MANAGERS_AVAILABLE:
                try:
                    await db_manager.log_supervisor_decision(
                        task_id, "error_escalation", agent_name, "supervisor",
                        f"Error escalated from {agent_name}: {error_type}",
                        confidence=0.0,  # Error escalation doesn't have confidence
                        decision_data=supervisor_notification
                    )
                except Exception as e:
                    logger.warning(f"Could not log supervisor escalation: {str(e)}")
        
        execution_time = (datetime.now() - execution_start).total_seconds()
        
        # Generate tool review
        tool_review = {
            "error_processed": True,
            "severity": severity,
            "escalated": escalate_to_supervisor,
            "recovery_recommendations_count": len(recovery_recommendations),
            "workflow_can_continue": error_report["error_metadata"]["can_continue_workflow"],
            "quality_assessment": "high"
        }
        
        # Update tool execution in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, error_report, "success",
                    execution_time, "", tool_review
                )
            except Exception as e:
                logger.warning(f"Could not update tool execution: {str(e)}")
        
        logger.error(f"🚨 Error handled: {agent_name} - {error_type} ({severity})")
        return error_report
        
    except Exception as e:
        error_msg = f"Error handling failed: {str(e)}"
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
            "error_processed": False,
            "error_metadata": {
                "error_handling_failed": True,
                "error_timestamp": datetime.now().isoformat()
            }
        }

@tool
async def state_synchronization_tool(
    task_id: Annotated[int, "Task ID for database logging"],
    agent_name: Annotated[str, "Agent performing synchronization"],
    state_updates: Annotated[Dict[str, Any], "State updates to synchronize"],
    sync_target: Annotated[str, "Sync target: database, workflow_state, both"] = "both",
    validate_consistency: Annotated[bool, "Whether to validate state consistency"] = True
) -> Annotated[Dict[str, Any], "State synchronization result"]:
    """
    Synchronize agent state across database and workflow state.
    Ensures consistency between local agent state and global workflow state.
    """
    
    execution_start = datetime.now()
    tool_input = {
        "task_id": task_id,
        "agent_name": agent_name,
        "sync_target": sync_target,
        "validate_consistency": validate_consistency,
        "updates_count": len(state_updates)
    }
    
    # Log tool execution start
    tool_exec_id = None
    if MANAGERS_AVAILABLE:
        try:
            db_manager = await get_database_manager()
            tool_exec_id = await db_manager.log_tool_execution(
                task_id, agent_name, "state_synchronization_tool",
                tool_input, execution_status="running"
            )
        except Exception as e:
            logger.warning(f"Could not log tool execution: {str(e)}")
    
    try:
        sync_result = {
            "sync_id": f"sync_{task_id}_{int(datetime.now().timestamp())}",
            "task_id": task_id,
            "agent_name": agent_name,
            "state_updates": state_updates,
            "sync_target": sync_target,
            "sync_timestamp": datetime.now().isoformat(),
            "sync_results": {}
        }
        
        # Synchronize to database
        if sync_target in ["database", "both"] and MANAGERS_AVAILABLE:
            try:
                # Update task review with agent state
                success = await db_manager.update_task_review(
                    task_id, f"{agent_name}_sync", state_updates
                )
                sync_result["sync_results"]["database"] = {
                    "success": success,
                    "updates_applied": len(state_updates) if success else 0
                }
            except Exception as e:
                logger.warning(f"Database sync failed: {str(e)}")
                sync_result["sync_results"]["database"] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Synchronize to workflow state (placeholder for actual implementation)
        if sync_target in ["workflow_state", "both"]:
            # In real implementation, this would update the AutomationWorkflowState
            sync_result["sync_results"]["workflow_state"] = {
                "success": True,
                "updates_applied": len(state_updates)
            }
        
        # Validate consistency if requested
        consistency_check = {"consistent": True, "issues": []}
        if validate_consistency:
            consistency_check = _validate_state_consistency(state_updates, agent_name)
        
        sync_result["consistency_check"] = consistency_check
        
        execution_time = (datetime.now() - execution_start).total_seconds()
        
        # Generate tool review
        tool_review = {
            "sync_completed": True,
            "sync_target": sync_target,
            "database_sync": sync_result["sync_results"].get("database", {}).get("success", False),
            "workflow_state_sync": sync_result["sync_results"].get("workflow_state", {}).get("success", False),
            "state_consistent": consistency_check["consistent"],
            "quality_assessment": "high" if consistency_check["consistent"] else "medium"
        }
        
        # Update tool execution in database
        if MANAGERS_AVAILABLE and tool_exec_id:
            try:
                await db_manager.update_tool_execution(
                    tool_exec_id, sync_result, "success",
                    execution_time, "", tool_review
                )
            except Exception as e:
                logger.warning(f"Could not update tool execution: {str(e)}")
        
        logger.info(f"🔄 State synchronized: {agent_name} - {sync_target}")
        return sync_result
        
    except Exception as e:
        error_msg = f"State synchronization failed: {str(e)}"
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
            "sync_completed": False,
            "sync_metadata": {
                "sync_failed": True,
                "error_timestamp": datetime.now().isoformat()
            }
        }

# Utility functions

def _categorize_error_severity(error_type: str, error_details: Dict[str, Any]) -> str:
    """Categorize error severity based on type and details"""
    
    critical_errors = ["database_connection_failed", "system_crash", "security_breach"]
    high_errors = ["script_execution_failed", "dependency_missing", "authentication_failed"]
    medium_errors = ["element_not_found", "timeout", "validation_failed"]
    low_errors = ["warning", "performance_issue", "deprecation_notice"]
    
    if error_type in critical_errors:
        return "critical"
    elif error_type in high_errors:
        return "high"
    elif error_type in medium_errors:
        return "medium"
    elif error_type in low_errors:
        return "low"
    else:
        # Default based on error details
        if error_details.get("blocks_workflow", False):
            return "high"
        elif error_details.get("requires_intervention", False):
            return "medium"
        else:
            return "low"

def _generate_recovery_recommendations(error_type: str, error_details: Dict[str, Any], agent_name: str) -> List[str]:
    """Generate recovery recommendations based on error type"""
    
    recommendations = []
    
    if error_type == "script_execution_failed":
        recommendations.extend([
            "Check script syntax and dependencies",
            "Verify target environment is accessible",
            "Review element selectors for accuracy",
            "Consider requesting Agent2 collaboration for script fixes"
        ])
    elif error_type == "element_not_found":
        recommendations.extend([
            "Update element selectors",
            "Add explicit waits before element interaction",
            "Verify page load state",
            "Check for dynamic content changes"
        ])
    elif error_type == "database_connection_failed":
        recommendations.extend([
            "Check database connection parameters",
            "Verify database service is running",
            "Review network connectivity",
            "Implement connection retry logic"
        ])
    elif error_type == "timeout":
        recommendations.extend([
            "Increase timeout values",
            "Optimize wait strategies",
            "Check for network latency issues",
            "Consider breaking down long operations"
        ])
    else:
        recommendations.extend([
            f"Review {agent_name} configuration",
            "Check system resources and dependencies",
            "Consult error logs for additional details",
            "Consider workflow restart if issue persists"
        ])
    
    return recommendations

def _validate_state_consistency(state_updates: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
    """Validate state consistency"""
    
    consistency_check = {
        "consistent": True,
        "issues": [],
        "validated_fields": list(state_updates.keys()),
        "validation_timestamp": datetime.now().isoformat()
    }
    
    # Basic validation rules
    for field, value in state_updates.items():
        if field.endswith("_count") and not isinstance(value, int):
            consistency_check["issues"].append(f"Field {field} should be integer, got {type(value)}")
            consistency_check["consistent"] = False
        
        if field.endswith("_timestamp") and not isinstance(value, str):
            consistency_check["issues"].append(f"Field {field} should be string timestamp, got {type(value)}")
            consistency_check["consistent"] = False
        
        if field == "status" and value not in ["pending", "running", "completed", "failed", "error"]:
            consistency_check["issues"].append(f"Invalid status value: {value}")
            consistency_check["consistent"] = False
    
    return consistency_check

# Tool collection for shared tools

SHARED_COMMUNICATION_TOOLS = [
    agent_communication_tool,
    error_handling_tool,
    state_synchronization_tool
]

def get_shared_tools():
    """Get all shared communication tools"""
    return SHARED_COMMUNICATION_TOOLS

if __name__ == "__main__":
    # Test shared communication tools
    async def test_shared_tools():
        print("🧪 Testing Shared Communication Tools...")
        
        # Test agent communication
        message_content = {
            "request_type": "status_update",
            "status": "completed",
            "details": "Blueprint generation finished successfully"
        }
        
        comm_result = await agent_communication_tool(
            999, "agent1", "supervisor", "status_update",
            message_content, "medium", False
        )
        print(f"✅ Agent communication: {comm_result['communication_id']}")
        
        # Test error handling
        error_details = {
            "error_message": "Element not found on page",
            "context": "Trying to click login button",
            "affected_components": ["ui_interaction"],
            "blocks_workflow": False
        }
        
        error_result = await error_handling_tool(
            999, "agent3", "element_not_found", error_details,
            False, True
        )
        print(f"✅ Error handling: {error_result['severity']} severity")
        
        # Test state synchronization
        state_updates = {
            "agent1_status": "completed",
            "ui_elements_count": 5,
            "confidence": 0.85,
            "last_updated": datetime.now().isoformat()
        }
        
        sync_result = await state_synchronization_tool(
            999, "agent1", state_updates, "both", True
        )
        print(f"✅ State sync: {sync_result['consistency_check']['consistent']}")
        
        print("🎉 Shared communication tools test completed!")
    
    import asyncio
    asyncio.run(test_shared_tools())