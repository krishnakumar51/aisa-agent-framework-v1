"""
Main Orchestrator - Updated Multi-Agent Workflow with Testing Environment
Coordinates all 4 agents with proper folder structure and sequential IDs
"""
import asyncio
import json
import logging
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import all updated agents
from app.database.database_manager import get_testing_db
from app.agents.agent1_blueprint import UpdatedAgent1_BlueprintGenerator
from app.agents.agent2_code import UpdatedAgent2_CodeGenerator
from app.agents.agent3_testing import UpdatedAgent3_TestingEnvironment
from app.agents.agent4_results import UpdatedAgent4_FinalReporter

logger = logging.getLogger(__name__)

class UpdatedMultiAgentOrchestrator:
    """
    Main orchestrator for the updated 4-agent workflow with testing environment integration
    Manages sequential task IDs and proper folder structure as per requirements
    """
    
    def __init__(self):
        self.orchestrator_version = "2.0.0"
        self.db_manager = None
        
        # Initialize all agents
        self.agent1 = UpdatedAgent1_BlueprintGenerator()
        self.agent2 = UpdatedAgent2_CodeGenerator()
        self.agent3 = UpdatedAgent3_TestingEnvironment()
        self.agent4 = UpdatedAgent4_FinalReporter()
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize database and all agents"""
        if self.initialized:
            return
        
        logger.info("🚀 Initializing Updated Multi-Agent Orchestrator System...")
        logger.info(f"🚀 Version: {self.orchestrator_version}")
        logger.info("🚀 Features: Sequential IDs, Testing Environment, OCR Validation, Agent Communication")
        
        # Initialize database
        self.db_manager = await get_testing_db()
        
        # Initialize all agents
        await self.agent1.initialize()
        await self.agent2.initialize()
        await self.agent3.initialize()
        await self.agent4.initialize()
        
        self.initialized = True
        logger.info("✅ Updated Multi-Agent Orchestrator System initialized")
        logger.info("📋 Ready for automation tasks with testing environment integration")
    
    async def execute_complete_workflow(self, document_content: bytes, screenshots: List[bytes],
                                      instruction: str, platform: str = "auto-detect",
                                      additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute complete 4-agent workflow with testing environment integration
        
        Args:
            document_content: PDF or document content
            screenshots: List of screenshot images
            instruction: User instruction (e.g., "Create an account with name Krishna Kumar and DOB 19 Sep 2000")
            platform: Target platform ("mobile", "web", "auto-detect")
            additional_data: Additional user data
            
        Returns:
            Complete workflow results with all agent outputs
        """
        if not self.initialized:
            await self.initialize()
        
        workflow_start_time = time.time()
        
        logger.info(f"\\n🚀 ========== UPDATED MULTI-AGENT WORKFLOW STARTED ==========")
        logger.info(f"🚀 Version: {self.orchestrator_version}")
        logger.info(f"🚀 Instruction: {instruction}")
        logger.info(f"🚀 Platform: {platform}")
        logger.info(f"🚀 Document Size: {len(document_content)} bytes")
        logger.info(f"🚀 Screenshots: {len(screenshots)}")
        logger.info(f"🚀 =============================================================")
        
        try:
            # PHASE 1: Agent 1 - Blueprint Generation
            logger.info(f"\\n🔵 ========== PHASE 1: BLUEPRINT GENERATION ==========")
            logger.info(f"🔵 Agent 1: Processing document and generating blueprint...")
            
            phase1_start = time.time()
            agent1_result = await self.agent1.process_and_generate_blueprint(
                document_content=document_content,
                screenshots=screenshots,
                instruction=instruction,
                platform=platform,
                additional_data=additional_data
            )
            phase1_time = time.time() - phase1_start
            
            if not agent1_result['success']:
                raise Exception(f"Agent 1 failed: {agent1_result.get('error', 'Unknown error')}")
            
            seq_id = agent1_result['seq_id']
            base_path = agent1_result['base_path']
            
            logger.info(f"🔵 Agent 1 Results:")
            logger.info(f"🔵   Sequential Task ID: {seq_id}")
            logger.info(f"🔵   Base Path: {base_path}")
            logger.info(f"🔵   Blueprint Path: {agent1_result['blueprint_path']}")
            logger.info(f"🔵   Text Extracted: {agent1_result['text_extracted']} chars")
            logger.info(f"🔵   UI Elements: {agent1_result['ui_elements']}")
            logger.info(f"🔵   Automation Steps: {agent1_result['automation_steps']}")
            logger.info(f"🔵   Blueprint Confidence: {agent1_result['blueprint_confidence']:.2f}")
            
            # PHASE 2: Agent 2 - Code Generation & Configuration  
            logger.info(f"\\n🟢 ========== PHASE 2: CODE GENERATION & CONFIGURATION ==========")
            logger.info(f"🟢 Agent 2: Generating automation code and preparing OCR logs...")
            
            phase2_start = time.time()
            agent2_result = await self.agent2.generate_code_and_setup(seq_id)
            phase2_time = time.time() - phase2_start
            
            if not agent2_result['success']:
                raise Exception(f"Agent 2 failed: {agent2_result.get('error', 'Unknown error')}")
            
            logger.info(f"🟢 Agent 2 Results:")
            logger.info(f"🟢   Agent2 Path: {agent2_result['agent2_path']}")
            logger.info(f"🟢   Script Generated: {agent2_result['script_size']} characters")
            logger.info(f"🟢   Requirements: {agent2_result['requirements_path']}")
            logger.info(f"🟢   OCR Logs Prepared: {agent2_result['ocr_logs_path']}")
            logger.info(f"🟢   Workflow Steps: {agent2_result['steps_count']}")
            logger.info(f"🟢   Ready for Testing: {'✅' if agent2_result['ready_for_testing'] else '❌'}")
            
            # PHASE 3: Agent 3 - Testing Environment Setup & Execution
            logger.info(f"\\n🟡 ========== PHASE 3: TESTING ENVIRONMENT & EXECUTION ==========")
            logger.info(f"🟡 Agent 3: Setting up testing environment and executing tests...")
            
            phase3_start = time.time()
            agent3_result = await self.agent3.setup_and_execute_tests(seq_id)
            phase3_time = time.time() - phase3_start
            
            if not agent3_result['success']:
                logger.warning(f"🟡 Agent 3 completed with issues: {agent3_result.get('error', 'Unknown error')}")
            
            logger.info(f"🟡 Agent 3 Results:")
            logger.info(f"🟡   Testing Path: {agent3_result.get('testing_path', 'N/A')}")
            logger.info(f"🟡   Virtual Environment: {'✅' if agent3_result.get('venv_setup', {}).get('success') else '❌'}")
            logger.info(f"🟡   Dependencies Installed: {'✅' if agent3_result.get('dependencies_installed', {}).get('success') else '❌'}")
            logger.info(f"🟡   Test Execution: {'✅' if agent3_result.get('overall_test_success') else '❌'}")
            logger.info(f"🟡   Total Test Attempts: {agent3_result.get('total_attempts', 0)}")
            logger.info(f"🟡   Agent 2 Collaborations: {agent3_result.get('agent2_collaborations', 0)}")
            logger.info(f"🟡   Ready for Reporting: {'✅' if agent3_result.get('ready_for_reporting') else '❌'}")
            
            # PHASE 4: Agent 4 - Final Reporting & CSV Export
            logger.info(f"\\n🔵 ========== PHASE 4: FINAL REPORTING & CSV EXPORT ==========")
            logger.info(f"🔵 Agent 4: Generating final report and exporting data...")
            
            phase4_start = time.time()
            agent4_result = await self.agent4.generate_final_report(seq_id)
            phase4_time = time.time() - phase4_start
            
            if not agent4_result['success']:
                logger.warning(f"🔵 Agent 4 failed: {agent4_result.get('error', 'Unknown error')}")
            
            logger.info(f"🔵 Agent 4 Results:")
            logger.info(f"🔵   Agent4 Path: {agent4_result.get('agent4_path', 'N/A')}")
            logger.info(f"🔵   Final Report: {agent4_result.get('final_report', {}).get('text_report', 'N/A')}")
            logger.info(f"🔵   CSV Export: {agent4_result.get('csv_export', {}).get('csv_path', 'N/A')}")
            logger.info(f"🔵   Conversation Log: {agent4_result.get('conversation_log', {}).get('log_path', 'N/A')}")
            logger.info(f"🔵   Files Generated: {len(agent4_result.get('files_generated', []))}")
            
            # Calculate final results
            total_execution_time = time.time() - workflow_start_time
            overall_success = (
                agent1_result['success'] and 
                agent2_result['success'] and 
                agent3_result.get('success', False) and  # Agent 3 may have warnings but still succeed
                agent4_result.get('success', False)
            )
            
            # Get final confidence from Agent 4's analysis
            final_confidence = 0.0
            performance_grade = "Unknown"
            if agent4_result.get('success') and 'analysis_results' in agent4_result:
                analysis = agent4_result['analysis_results']
                final_confidence = analysis.get('overall_confidence', 0.0)
                performance_grade = analysis.get('performance_grade', 'Unknown')
            
            # Generate comprehensive workflow summary
            workflow_summary = {
                "orchestrator_version": self.orchestrator_version,
                "seq_id": seq_id,
                "instruction": instruction,
                "platform": platform,
                "overall_success": overall_success,
                "final_confidence": final_confidence,
                "performance_grade": performance_grade,
                "total_execution_time": total_execution_time,
                "phase_timings": {
                    "phase1_blueprint": phase1_time,
                    "phase2_code": phase2_time,
                    "phase3_testing": phase3_time,
                    "phase4_reporting": phase4_time
                },
                "agent_results": {
                    "agent1": agent1_result,
                    "agent2": agent2_result,
                    "agent3": agent3_result,
                    "agent4": agent4_result
                },
                "folder_structure": {
                    "base_path": base_path,
                    "agent1_folder": f"{base_path}/agent1",
                    "agent2_folder": f"{base_path}/agent2",
                    "agent3_testing": f"{base_path}/agent3/testing",
                    "agent4_folder": f"{base_path}/agent4"
                },
                "key_metrics": {
                    "agent2_collaborations": agent3_result.get('agent2_collaborations', 0),
                    "test_attempts": agent3_result.get('total_attempts', 0),
                    "automation_steps": agent1_result.get('automation_steps', 0),
                    "files_generated": len(agent4_result.get('files_generated', []))
                }
            }
            
            # Save workflow summary to base folder
            await self._save_workflow_summary(seq_id, base_path, workflow_summary)
            
            # Update final task status in database
            final_status = "completed" if overall_success else "completed_with_issues"
            await self.db_manager.update_task_status(seq_id, final_status, "orchestrator")
            
            logger.info(f"\\n🚀 ========== UPDATED MULTI-AGENT WORKFLOW COMPLETED ==========")
            logger.info(f"🚀 Overall Result: {'✅ SUCCESS' if overall_success else '⚠️ COMPLETED WITH ISSUES'}")
            logger.info(f"🚀 Sequential Task ID: {seq_id}")
            logger.info(f"🚀 Final Confidence: {final_confidence:.3f} ({performance_grade})")
            logger.info(f"🚀 Total Execution Time: {total_execution_time:.1f} seconds")
            logger.info(f"🚀 Agent 2-3 Collaborations: {agent3_result.get('agent2_collaborations', 0)}")
            logger.info(f"🚀 Test Attempts: {agent3_result.get('total_attempts', 0)}")
            logger.info(f"🚀 Base Path: {base_path}")
            logger.info(f"🚀 SQLite Database: {self.db_manager.db_path}")
            logger.info(f"🚀 Testing Environment: {'✅ SET UP' if agent3_result.get('success') else '❌ ISSUES'}")
            logger.info(f"🚀 Final Report: {'✅ GENERATED' if agent4_result.get('success') else '❌ FAILED'}")
            logger.info(f"🚀 ================================================================")
            
            return {
                "success": overall_success,
                "seq_id": seq_id,
                "base_path": base_path,
                "final_confidence": final_confidence,
                "performance_grade": performance_grade,
                "total_execution_time": total_execution_time,
                "workflow_summary": workflow_summary,
                "message": "✅ Updated multi-agent workflow completed successfully" if overall_success else "⚠️ Workflow completed with some issues",
                "orchestrator_version": self.orchestrator_version
            }
            
        except Exception as e:
            error_msg = f"Updated multi-agent workflow failed: {str(e)}"
            logger.error(f"🔴 {error_msg}")
            
            # Update task as failed if we have seq_id
            if 'seq_id' in locals():
                await self.db_manager.update_task_status(seq_id, "failed", "orchestrator")
            
            return {
                "success": False,
                "error": error_msg,
                "seq_id": locals().get('seq_id'),
                "total_execution_time": time.time() - workflow_start_time,
                "message": f"❌ Updated workflow failed: {error_msg}",
                "orchestrator_version": self.orchestrator_version
            }
    
    async def get_task_status(self, seq_id: int) -> Dict[str, Any]:
        """
        Get comprehensive task status including folder structure
        
        Args:
            seq_id: Sequential task ID
            
        Returns:
            Complete task status information
        """
        try:
            # Get task info from database
            task_info = await self.db_manager.get_task_info(seq_id)
            if not task_info:
                return {"error": f"Task {seq_id} not found"}
            
            # Get workflow steps
            workflow_steps = await self.db_manager.get_workflow_steps(seq_id)
            
            # Get agent communications
            communications = []
            async with aiosqlite.connect(self.db_manager.db_path) as db:
                cursor = await db.execute("""
                    SELECT * FROM agent_communications WHERE seq_id = ? ORDER BY created_at DESC LIMIT 10
                """, (seq_id,))
                
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                communications = [dict(zip(columns, row)) for row in rows]
            
            # Check folder structure
            base_path = Path(task_info['base_path'])
            folder_status = {
                "base_exists": base_path.exists(),
                "agent1_exists": (base_path / "agent1").exists(),
                "agent2_exists": (base_path / "agent2").exists(),
                "agent3_testing_exists": (base_path / "agent3" / "testing").exists(),
                "agent4_exists": (base_path / "agent4").exists(),
                "sqlite_db_exists": (base_path / "sqlite_db.sqlite").exists()
            }
            
            return {
                "seq_id": seq_id,
                "task_info": task_info,
                "workflow_steps": len(workflow_steps),
                "recent_communications": len(communications),
                "folder_structure": folder_status,
                "status_check_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Task status check failed: {str(e)}")
            return {"error": f"Status check failed: {str(e)}"}
    
    async def list_recent_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent tasks with basic information
        
        Args:
            limit: Maximum number of tasks to return
            
        Returns:
            List of recent task summaries
        """
        try:
            async with aiosqlite.connect(self.db_manager.db_path) as db:
                cursor = await db.execute("""
                    SELECT seq_id, instruction, platform, status, created_at, updated_at
                    FROM automation_tasks 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
                
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                tasks = [dict(zip(columns, row)) for row in rows]
                
                return tasks
                
        except Exception as e:
            logger.error(f"Recent tasks listing failed: {str(e)}")
            return []
    
    async def _save_workflow_summary(self, seq_id: int, base_path: str, summary: Dict[str, Any]):
        """Save comprehensive workflow summary"""
        try:
            summary_path = Path(base_path) / "workflow_summary.json"
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
            
            # Also save as readable text
            text_summary = self._format_workflow_summary_text(summary)
            text_path = Path(base_path) / "workflow_summary.txt"
            
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text_summary)
            
            logger.info(f"🚀 Workflow summary saved: {summary_path}")
            logger.info(f"🚀 Workflow summary (text): {text_path}")
            
        except Exception as e:
            logger.warning(f"🟡 Failed to save workflow summary: {str(e)}")
    
    def _format_workflow_summary_text(self, summary: Dict[str, Any]) -> str:
        """Format workflow summary as readable text"""
        
        text = f"""
UPDATED MULTI-AGENT WORKFLOW SUMMARY
====================================

Version: {summary['orchestrator_version']}
Task ID: {summary['seq_id']}
Instruction: {summary['instruction']}
Platform: {summary['platform']}
Overall Success: {'✅ YES' if summary['overall_success'] else '❌ NO'}
Final Confidence: {summary['final_confidence']:.3f}
Performance Grade: {summary['performance_grade']}

EXECUTION TIMING
----------------
Total Time: {summary['total_execution_time']:.2f} seconds
Phase 1 (Blueprint): {summary['phase_timings']['phase1_blueprint']:.2f}s
Phase 2 (Code Generation): {summary['phase_timings']['phase2_code']:.2f}s  
Phase 3 (Testing): {summary['phase_timings']['phase3_testing']:.2f}s
Phase 4 (Reporting): {summary['phase_timings']['phase4_reporting']:.2f}s

FOLDER STRUCTURE CREATED
------------------------
Base Path: {summary['folder_structure']['base_path']}
├── agent1/ (Blueprint generation)
├── agent2/ (Code generation & requirements)
├── agent3/testing/ (Virtual environment & test execution)
└── agent4/ (Final reports & CSV export)

KEY METRICS
-----------
Automation Steps: {summary['key_metrics']['automation_steps']}
Test Attempts: {summary['key_metrics']['test_attempts']}
Agent 2-3 Collaborations: {summary['key_metrics']['agent2_collaborations']}
Files Generated: {summary['key_metrics']['files_generated']}

AGENT RESULTS SUMMARY
---------------------
Agent 1 (Blueprint): {'✅' if summary['agent_results']['agent1']['success'] else '❌'}
Agent 2 (Code Gen): {'✅' if summary['agent_results']['agent2']['success'] else '❌'}
Agent 3 (Testing): {'✅' if summary['agent_results']['agent3'].get('success') else '❌'}
Agent 4 (Reporting): {'✅' if summary['agent_results']['agent4'].get('success') else '❌'}

Generated by Updated Multi-Agent Orchestrator v{summary['orchestrator_version']}
"""
        
        return text

# Global orchestrator instance
updated_orchestrator = UpdatedMultiAgentOrchestrator()

async def get_updated_orchestrator() -> UpdatedMultiAgentOrchestrator:
    """Get the global updated orchestrator instance"""
    if not updated_orchestrator.initialized:
        await updated_orchestrator.initialize()
    return updated_orchestrator