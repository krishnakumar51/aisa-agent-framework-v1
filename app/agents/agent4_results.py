"""
Updated Agent 4: Final Reporting and CSV Export
Analyzes test results, generates comprehensive reports, and converts SQLite to CSV
"""
import asyncio
import json
import logging
import time
import os
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import shutil
import aiosqlite


# Import the updated database manager
from app.database.database_manager import get_testing_db

logger = logging.getLogger(__name__)

class UpdatedAgent4_FinalReporter:
    """Agent 4: Final Reporting and CSV Export with Conversation Logs"""
    
    def __init__(self):
        self.agent_name = "agent4"
        self.db_manager = None
        
    async def initialize(self):
        """Initialize database connection"""
        self.db_manager = await get_testing_db()
        logger.info("🔵 Agent 4: Final reporter initialized")
    
    async def generate_final_report(self, seq_id: int) -> Dict[str, Any]:
        """
        Generate comprehensive final report with CSV export
        
        Args:
            seq_id: Sequential task ID from Agent 3
            
        Returns:
            Final reporting results with file paths
        """
        start_time = time.time()
        
        logger.info(f"🔵 [Agent4] Starting final report generation for task {seq_id}")
        
        try:
            # Get task information
            task_info = await self.db_manager.get_task_info(seq_id)
            if not task_info:
                raise Exception(f"Task {seq_id} not found in database")
            
            # Update task status
            await self.db_manager.update_task_status(seq_id, "final_reporting", "agent4")
            
            # Create agent4 folder
            base_path = Path(task_info['base_path'])
            agent4_path = base_path / "agent4"
            agent4_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"🔵 [Agent4] Created agent4 folder: {agent4_path}")
            
            # Step 1: Collect all data from database
            comprehensive_data = await self._collect_comprehensive_data(seq_id)
            
            # Step 2: Analyze results and generate insights
            analysis_results = await self._analyze_automation_results(seq_id, comprehensive_data)
            
            # Step 3: Generate final report text
            final_report = await self._generate_final_report_text(seq_id, comprehensive_data, analysis_results)
            
            # Step 4: Export SQLite data to CSV
            csv_export = await self._export_sqlite_to_csv(seq_id, agent4_path)
            
            # Step 5: Generate conversation logs
            conversation_log = await self._generate_conversation_log(seq_id, agent4_path)
            
            # Step 6: Save final report files
            report_files = await self._save_final_report_files(
                seq_id, agent4_path, final_report, comprehensive_data
            )
            
            # Step 7: Create summary dashboard
            dashboard_file = await self._create_summary_dashboard(seq_id, agent4_path, analysis_results)
            
            # Update task progress
            await self.db_manager.update_task_progress(seq_id, final_report_generated=True)
            await self.db_manager.update_task_status(seq_id, "completed", "agent4")
            
            processing_time = time.time() - start_time
            
            logger.info(f"🔵 [Agent4] ✅ Final report generated: {report_files['text_report']}")
            logger.info(f"🔵 [Agent4] ✅ CSV export completed: {csv_export['csv_path']}")
            logger.info(f"🔵 [Agent4] ✅ Conversation log created: {conversation_log['log_path']}")
            logger.info(f"🔵 [Agent4] ✅ Dashboard created: {dashboard_file}")
            logger.info(f"🔵 [Agent4] ✅ Final reporting completed")
            
            return {
                "success": True,
                "seq_id": seq_id,
                "agent": self.agent_name,
                "agent4_path": str(agent4_path),
                "comprehensive_data": comprehensive_data,
                "analysis_results": analysis_results,
                "final_report": report_files,
                "csv_export": csv_export,
                "conversation_log": conversation_log,
                "dashboard_file": dashboard_file,
                "processing_time": processing_time,
                "files_generated": [
                    report_files['text_report'],
                    report_files['json_report'],
                    csv_export['csv_path'],
                    conversation_log['log_path'],
                    dashboard_file
                ]
            }
            
        except Exception as e:
            error_msg = f"Final reporting failed: {str(e)}"
            logger.error(f"🔴 [Agent4] {error_msg}")
            
            # Update task status
            await self.db_manager.update_task_status(seq_id, "reporting_failed", "agent4")
            
            return {
                "success": False,
                "error": error_msg,
                "seq_id": seq_id,
                "agent": self.agent_name,
                "processing_time": time.time() - start_time
            }
    
    async def _collect_comprehensive_data(self, seq_id: int) -> Dict[str, Any]:
        """Collect all data from database for comprehensive analysis"""
        logger.info(f"🔵 [Agent4] Collecting comprehensive data...")
        
        # Get task information
        task_info = await self.db_manager.get_task_info(seq_id)
        
        # Get workflow steps
        workflow_steps = await self.db_manager.get_workflow_steps(seq_id)
        
        # Get agent communications
        communications = []
        async with aiosqlite.connect(self.db_manager.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM agent_communications WHERE seq_id = ? ORDER BY created_at
            """, (seq_id,))
            
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            communications = [dict(zip(columns, row)) for row in rows]
        
        # Get test executions
        test_executions = []
        async with aiosqlite.connect(self.db_manager.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM test_executions WHERE seq_id = ? ORDER BY created_at
            """, (seq_id,))
            
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            test_executions = [dict(zip(columns, row)) for row in rows]
        
        # Get generated files
        generated_files = []
        async with aiosqlite.connect(self.db_manager.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM generated_files WHERE seq_id = ? ORDER BY created_at
            """, (seq_id,))
            
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            generated_files = [dict(zip(columns, row)) for row in rows]
        
        # Get testing environment info
        testing_env = []
        async with aiosqlite.connect(self.db_manager.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM testing_environments WHERE seq_id = ?
            """, (seq_id,))
            
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            testing_env = [dict(zip(columns, row)) for row in rows]
        
        comprehensive_data = {
            "task_info": task_info,
            "workflow_steps": workflow_steps,
            "communications": communications,
            "test_executions": test_executions,
            "generated_files": generated_files,
            "testing_environment": testing_env,
            "collection_timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"🔵 [Agent4] Collected data: {len(workflow_steps)} steps, {len(communications)} communications, {len(test_executions)} executions")
        
        return comprehensive_data
    
    async def _analyze_automation_results(self, seq_id: int, comprehensive_data: Dict) -> Dict[str, Any]:
        """Analyze automation results and generate insights"""
        logger.info(f"🔵 [Agent4] Analyzing automation results...")
        
        task_info = comprehensive_data['task_info']
        workflow_steps = comprehensive_data['workflow_steps']
        communications = comprehensive_data['communications']
        test_executions = comprehensive_data['test_executions']
        
        # Task completion analysis
        total_steps = len(workflow_steps)
        completed_steps = len([step for step in workflow_steps if step['status'] == 'completed'])
        failed_steps = len([step for step in workflow_steps if step['status'] == 'failed'])
        
        # Test execution analysis
        total_test_attempts = len(test_executions)
        successful_tests = len([test for test in test_executions if test['success']])
        failed_tests = total_test_attempts - successful_tests
        
        # Agent collaboration analysis
        total_communications = len(communications)
        resolved_communications = len([comm for comm in communications if comm['status'] == 'resolved'])
        agent2_to_agent3 = len([comm for comm in communications if comm['from_agent'] == 'agent3' and comm['to_agent'] == 'agent2'])
        
        # Success rates
        step_success_rate = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        test_success_rate = (successful_tests / total_test_attempts * 100) if total_test_attempts > 0 else 0
        communication_success_rate = (resolved_communications / total_communications * 100) if total_communications > 0 else 100
        
        # Overall assessment
        overall_success = (
            step_success_rate > 50 and
            test_success_rate > 0 and
            task_info['status'] in ['completed', 'testing_completed']
        )
        
        # Confidence calculation (multi-factor)
        confidence_factors = {
            'step_completion': min(step_success_rate / 100, 1.0),
            'test_execution': min(test_success_rate / 100, 1.0),
            'agent_collaboration': min(communication_success_rate / 100, 1.0),
            'task_complexity': self._assess_task_complexity(workflow_steps)
        }
        
        overall_confidence = (
            confidence_factors['step_completion'] * 0.4 +
            confidence_factors['test_execution'] * 0.3 +
            confidence_factors['agent_collaboration'] * 0.2 +
            confidence_factors['task_complexity'] * 0.1
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            step_success_rate, test_success_rate, communications, overall_success
        )
        
        analysis_results = {
            "overall_success": overall_success,
            "overall_confidence": overall_confidence,
            "step_analysis": {
                "total_steps": total_steps,
                "completed_steps": completed_steps,
                "failed_steps": failed_steps,
                "success_rate": step_success_rate
            },
            "test_analysis": {
                "total_attempts": total_test_attempts,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": test_success_rate
            },
            "collaboration_analysis": {
                "total_communications": total_communications,
                "resolved_communications": resolved_communications,
                "agent2_collaborations": agent2_to_agent3,
                "success_rate": communication_success_rate
            },
            "confidence_factors": confidence_factors,
            "recommendations": recommendations,
            "performance_grade": self._calculate_performance_grade(overall_confidence),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"🔵 [Agent4] Analysis complete - Overall success: {'YES' if overall_success else 'NO'}")
        logger.info(f"🔵 [Agent4] Confidence: {overall_confidence:.3f} ({analysis_results['performance_grade']})")
        
        return analysis_results
    
    def _assess_task_complexity(self, workflow_steps: List[Dict]) -> float:
        """Assess task complexity based on workflow steps"""
        if not workflow_steps:
            return 0.0
        
        step_count = len(workflow_steps)
        action_types = set(step['action_type'] for step in workflow_steps)
        
        # Base complexity on step count and action diversity
        if step_count <= 3:
            complexity = 0.8  # Simple
        elif step_count <= 6:
            complexity = 0.6  # Medium
        else:
            complexity = 0.4  # Complex
        
        # Adjust for action diversity
        if len(action_types) > 3:
            complexity -= 0.1
        
        return max(0.0, min(1.0, complexity))
    
    def _generate_recommendations(self, step_success_rate: float, test_success_rate: float, 
                                communications: List[Dict], overall_success: bool) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if not overall_success:
            recommendations.append("Review automation logic and improve error handling")
            recommendations.append("Consider breaking complex tasks into smaller components")
        
        if step_success_rate < 70:
            recommendations.append("Optimize individual workflow steps for better reliability")
            recommendations.append("Add more robust element detection and wait conditions")
        
        if test_success_rate < 50:
            recommendations.append("Improve script execution with better error recovery")
            recommendations.append("Add validation checkpoints throughout the automation")
        
        if len(communications) > 2:
            recommendations.append("Enhance initial code generation quality to reduce iterations")
            recommendations.append("Implement better error prediction and prevention")
        
        if not recommendations:
            recommendations.extend([
                "Task completed successfully - consider optimizing execution time",
                "Document successful patterns for future automation tasks",
                "Monitor performance over multiple runs for consistency"
            ])
        
        return recommendations
    
    def _calculate_performance_grade(self, confidence: float) -> str:
        """Calculate performance grade based on confidence score"""
        if confidence >= 0.9:
            return "A+ (Excellent)"
        elif confidence >= 0.8:
            return "A (Very Good)"
        elif confidence >= 0.7:
            return "B+ (Good)"
        elif confidence >= 0.6:
            return "B (Satisfactory)"
        elif confidence >= 0.5:
            return "C+ (Acceptable)"
        elif confidence >= 0.4:
            return "C (Needs Improvement)"
        else:
            return "D (Poor)"
    
    async def _generate_final_report_text(self, seq_id: int, comprehensive_data: Dict, 
                                        analysis_results: Dict) -> str:
        """Generate comprehensive final report text"""
        task_info = comprehensive_data['task_info']
        analysis = analysis_results
        
        report_text = f"""
AUTOMATION TASK FINAL REPORT
============================

Report Generated: {datetime.utcnow().isoformat()}
Task ID: {seq_id}
Agent: {self.agent_name}

TASK SUMMARY
------------
Instruction: {task_info['instruction']}
Platform: {task_info['platform']}
Status: {task_info['status']}
Created: {task_info['created_at']}
Completed: {task_info['updated_at']}

OVERALL RESULTS
---------------
Success: {'✅ YES' if analysis['overall_success'] else '❌ NO'}
Confidence: {analysis['overall_confidence']:.3f}
Performance Grade: {analysis['performance_grade']}

DETAILED ANALYSIS
-----------------

Workflow Steps:
  • Total Steps: {analysis['step_analysis']['total_steps']}
  • Completed: {analysis['step_analysis']['completed_steps']}
  • Failed: {analysis['step_analysis']['failed_steps']}
  • Success Rate: {analysis['step_analysis']['success_rate']:.1f}%

Test Execution:
  • Total Attempts: {analysis['test_analysis']['total_attempts']}
  • Successful Tests: {analysis['test_analysis']['successful_tests']}
  • Failed Tests: {analysis['test_analysis']['failed_tests']}
  • Success Rate: {analysis['test_analysis']['success_rate']:.1f}%

Agent Collaboration:
  • Total Communications: {analysis['collaboration_analysis']['total_communications']}
  • Resolved Issues: {analysis['collaboration_analysis']['resolved_communications']}
  • Agent 2-3 Collaborations: {analysis['collaboration_analysis']['agent2_collaborations']}
  • Communication Success: {analysis['collaboration_analysis']['success_rate']:.1f}%

CONFIDENCE FACTORS
------------------
• Step Completion: {analysis['confidence_factors']['step_completion']:.3f}
• Test Execution: {analysis['confidence_factors']['test_execution']:.3f}
• Agent Collaboration: {analysis['confidence_factors']['agent_collaboration']:.3f}
• Task Complexity: {analysis['confidence_factors']['task_complexity']:.3f}

GENERATED FILES
---------------"""

        # List generated files
        for file_info in comprehensive_data['generated_files']:
            report_text += f"\n• {file_info['file_name']} (v{file_info['version']}) - {file_info['file_type']}"

        report_text += f"""

RECOMMENDATIONS
---------------"""
        
        for i, recommendation in enumerate(analysis['recommendations'], 1):
            report_text += f"\n{i}. {recommendation}"
        
        report_text += f"""

TECHNICAL DETAILS
-----------------
Base Path: {task_info['base_path']}
SQLite Database: {self.db_manager.db_path}
Testing Environment: {"✅ SET UP" if comprehensive_data['testing_environment'] else "❌ NOT SET UP"}

FOLDER STRUCTURE
----------------
├── agent1/
│   └── blueprint.json
├── agent2/
│   ├── script.py (and updates)
│   ├── requirements.txt
│   └── ocr_logs/
├── agent3/
│   └── testing/
│       ├── venv/
│       ├── script.py
│       ├── requirements.txt
│       └── ocr_logs/
└── agent4/
    ├── final_report.txt (this file)
    ├── final_report.csv
    └── conversation.json

End of Report - Generated by {self.agent_name}
"""
        
        return report_text
    
    async def _export_sqlite_to_csv(self, seq_id: int, agent4_path: Path) -> Dict[str, Any]:
        """Export SQLite database data to CSV format"""
        logger.info(f"🔵 [Agent4] Exporting SQLite data to CSV...")
        
        csv_path = agent4_path / "final_report.csv"
        
        try:
            await self.db_manager.export_to_csv(seq_id, str(csv_path))
            
            # Get file size
            csv_size = csv_path.stat().st_size if csv_path.exists() else 0
            
            logger.info(f"🔵 [Agent4] ✅ CSV export completed: {csv_path} ({csv_size} bytes)")
            
            return {
                "success": True,
                "csv_path": str(csv_path),
                "file_size": csv_size,
                "export_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"CSV export failed: {str(e)}"
            logger.error(f"🔴 [Agent4] {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "csv_path": str(csv_path)
            }
    
    async def _generate_conversation_log(self, seq_id: int, agent4_path: Path) -> Dict[str, Any]:
        """Generate conversation log between Agent 2 and Agent 3"""
        logger.info(f"🔵 [Agent4] Generating conversation log...")
        
        conversation_path = agent4_path / "conversation.json"
        
        try:
            # Get all communications
            communications = []
            async with aiosqlite.connect(self.db_manager.db_path) as db:
                cursor = await db.execute("""
                    SELECT * FROM agent_communications WHERE seq_id = ? ORDER BY created_at
                """, (seq_id,))
                
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                communications = [dict(zip(columns, row)) for row in rows]
            
            # Format conversation log
            conversation_log = {
                "seq_id": seq_id,
                "agent": self.agent_name,
                "total_communications": len(communications),
                "generated_at": datetime.utcnow().isoformat(),
                "conversation_summary": {
                    "agent2_to_agent3": len([c for c in communications if c['from_agent'] == 'agent2' and c['to_agent'] == 'agent3']),
                    "agent3_to_agent2": len([c for c in communications if c['from_agent'] == 'agent3' and c['to_agent'] == 'agent2']),
                    "resolved_issues": len([c for c in communications if c['status'] == 'resolved']),
                    "pending_issues": len([c for c in communications if c['status'] == 'pending'])
                },
                "detailed_conversations": []
            }
            
            # Add detailed conversation entries
            for comm in communications:
                conversation_entry = {
                    "communication_id": comm['comm_id'],
                    "from_agent": comm['from_agent'],
                    "to_agent": comm['to_agent'],
                    "message_type": comm['message_type'],
                    "timestamp": comm['created_at'],
                    "status": comm['status'],
                    "message_preview": comm['message_content'][:200] + "..." if len(comm['message_content']) > 200 else comm['message_content'],
                    "response_preview": comm['response_content'][:200] + "..." if comm['response_content'] and len(comm['response_content']) > 200 else comm['response_content']
                }
                conversation_log["detailed_conversations"].append(conversation_entry)
            
            # Save conversation log
            with open(conversation_path, 'w', encoding='utf-8') as f:
                json.dump(conversation_log, f, indent=2, ensure_ascii=False)
            
            logger.info(f"🔵 [Agent4] ✅ Conversation log created: {conversation_path}")
            
            return {
                "success": True,
                "log_path": str(conversation_path),
                "total_communications": len(communications),
                "summary": conversation_log["conversation_summary"]
            }
            
        except Exception as e:
            error_msg = f"Conversation log generation failed: {str(e)}"
            logger.error(f"🔴 [Agent4] {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "log_path": str(conversation_path)
            }
    
    async def _save_final_report_files(self, seq_id: int, agent4_path: Path, 
                                     final_report_text: str, comprehensive_data: Dict) -> Dict[str, str]:
        """Save final report in multiple formats"""
        
        # Save text report
        text_report_path = agent4_path / "final_report.txt"
        with open(text_report_path, 'w', encoding='utf-8') as f:
            f.write(final_report_text)
        
        # Save JSON report with full data
        json_report_path = agent4_path / "final_report.json"
        json_data = {
            "seq_id": seq_id,
            "agent": self.agent_name,
            "generated_at": datetime.utcnow().isoformat(),
            "report_text": final_report_text,
            "comprehensive_data": comprehensive_data
        }
        
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"🔵 [Agent4] ✅ Final reports saved: TXT and JSON formats")
        
        return {
            "text_report": str(text_report_path),
            "json_report": str(json_report_path)
        }
    
    async def _create_summary_dashboard(self, seq_id: int, agent4_path: Path, 
                                      analysis_results: Dict) -> str:
        """Create a simple summary dashboard file"""
        dashboard_path = agent4_path / "summary_dashboard.html"
        
        analysis = analysis_results
        
        # Simple HTML dashboard
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Automation Task {seq_id} - Summary Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        .header {{ text-align: center; color: #333; }}
        .success {{ color: #4CAF50; }}
        .failure {{ color: #f44336; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f9f9f9; border-radius: 5px; min-width: 150px; text-align: center; }}
        .grade-a {{ background-color: #e8f5e8; }}
        .grade-b {{ background-color: #fff3cd; }}
        .grade-c {{ background-color: #f8d7da; }}
        .recommendations {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Automation Task Summary</h1>
            <h2>Task ID: {seq_id}</h2>
            <p class="{'success' if analysis['overall_success'] else 'failure'}">
                {'✅ SUCCESS' if analysis['overall_success'] else '❌ FAILED'}
            </p>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <h3>Overall Confidence</h3>
                <p><strong>{analysis['overall_confidence']:.3f}</strong></p>
            </div>
            <div class="metric">
                <h3>Performance Grade</h3>
                <p><strong>{analysis['performance_grade']}</strong></p>
            </div>
            <div class="metric">
                <h3>Steps Success Rate</h3>
                <p><strong>{analysis['step_analysis']['success_rate']:.1f}%</strong></p>
            </div>
            <div class="metric">
                <h3>Test Success Rate</h3>
                <p><strong>{analysis['test_analysis']['success_rate']:.1f}%</strong></p>
            </div>
        </div>
        
        <div class="recommendations">
            <h3>Key Recommendations:</h3>
            <ul>
"""
        
        for rec in analysis['recommendations'][:5]:  # Top 5 recommendations
            html_content += f"                <li>{rec}</li>\n"
        
        html_content += f"""
            </ul>
        </div>
        
        <div class="details">
            <h3>Detailed Metrics:</h3>
            <p><strong>Total Workflow Steps:</strong> {analysis['step_analysis']['total_steps']}</p>
            <p><strong>Test Attempts:</strong> {analysis['test_analysis']['total_attempts']}</p>
            <p><strong>Agent Collaborations:</strong> {analysis['collaboration_analysis']['agent2_collaborations']}</p>
        </div>
        
        <div class="footer">
            <p><em>Generated by Agent 4 on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</em></p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"🔵 [Agent4] ✅ Summary dashboard created: {dashboard_path}")
        
        return str(dashboard_path)