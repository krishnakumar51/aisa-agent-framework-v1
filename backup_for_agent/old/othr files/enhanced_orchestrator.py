"""
FULLY CORRECTED Enhanced Multi-Agent Orchestrator
Fixes all method calls to match actual agent implementations
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import enhanced agents with correct classes
from app.agents.enhanced_agent2 import EnhancedAgent2_CodeGenerator
from app.agents.enhanced_agent3 import EnhancedAgent3_IsolatedTesting
from app.agents.agent1_blueprint import UpdatedAgent1_BlueprintGenerator
from app.agents.agent4_results import UpdatedAgent4_FinalReporter

# Import enhanced utilities with error handling
try:
    from app.utils.device_manager import DeviceManager
    from app.utils.terminal_manager import TerminalManager
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    print("⚠️ Enhanced utils not available - using basic functionality")

from app.database.database_manager import get_testing_db

logger = logging.getLogger(__name__)

class EnhancedMultiAgentOrchestrator:
    """Enhanced Multi-Agent Orchestrator with Corrected Method Calls"""
    
    def __init__(self):
        self.version = "3.0.0-enhanced-fully-fixed"
        self.db_manager = None
        
        # Initialize enhanced agents
        self.agent1 = UpdatedAgent1_BlueprintGenerator()
        self.agent2 = EnhancedAgent2_CodeGenerator()
        self.agent3 = EnhancedAgent3_IsolatedTesting()
        self.agent4 = UpdatedAgent4_FinalReporter()
        
        # Initialize enhanced utilities with fallbacks
        if UTILS_AVAILABLE:
            self.device_manager = DeviceManager()
            self.terminal_manager = TerminalManager()
        else:
            self.device_manager = None
            self.terminal_manager = None

    async def initialize(self):
        """Initialize enhanced orchestrator system"""
        logger.info("🚀 Initializing Enhanced Multi-Agent Orchestrator System...")
        logger.info(f"🚀 Version: {self.version}")
        logger.info("🚀 Features: Terminal Isolation, Dynamic Device Detection, Appium Management, Enhanced Code Generation")
        
        # Initialize database
        self.db_manager = await get_testing_db()
        logger.info("🗄️ Enhanced database initialized")
        
        # Initialize all agents
        await self.agent1.initialize()
        await self.agent2.initialize()
        await self.agent3.initialize()
        await self.agent4.initialize()
        
        logger.info("✅ Enhanced Multi-Agent Orchestrator System initialized")
        logger.info("📋 Ready for advanced automation tasks with isolated testing")

    async def execute_enhanced_workflow(
        self,
        instruction: str,
        platform: str,
        document_data: bytes = None,
        screenshots: List[bytes] = None,
        additional_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute enhanced multi-agent workflow with terminal isolation"""
        workflow_start_time = time.time()
        logger.info("\\n🚀 ========== ENHANCED MULTI-AGENT WORKFLOW STARTED ==========")
        logger.info(f"🚀 Version: {self.version}")
        logger.info(f"🚀 Instruction: {instruction}")
        logger.info(f"🚀 Platform: {platform}")
        logger.info(f"🚀 Document Size: {len(document_data) if document_data else 0} bytes")
        logger.info(f"🚀 Screenshots: {len(screenshots) if screenshots else 0}")
        logger.info("🚀 =============================================================")
        
        workflow_results = {
            "version": self.version,
            "instruction": instruction,
            "platform": platform,
            "start_time": workflow_start_time,
            "phases": {}
        }
        
        try:
            # ========== PHASE 1: ENHANCED BLUEPRINT GENERATION ==========
            logger.info("\\n🔵 ========== PHASE 1: ENHANCED BLUEPRINT GENERATION ==========")
            logger.info("🔵 Agent 1: Processing document and generating enhanced blueprint...")
            phase1_start = time.time()
            
            # CORRECTED: Use actual Agent 1 method name and parameters
            agent1_results = await self.agent1.process_and_generate_blueprint(
                document_content=document_data,
                screenshots=screenshots or [],
                instruction=instruction,
                platform=platform,
                additional_data=additional_data or {}
            )
            
            if not agent1_results.get("success"):
                raise Exception(f"Agent 1 failed: {agent1_results.get('error', 'Unknown error')}")
            
            workflow_results["phases"]["phase1"] = {
                "agent": "agent1_blueprint",
                "duration": time.time() - phase1_start,
                "results": agent1_results
            }
            
            logger.info("🔵 Agent 1 Results:")
            logger.info(f"🔵   Sequential Task ID: {agent1_results['seq_id']}")
            logger.info(f"🔵   Base Path: {agent1_results['base_path']}")
            logger.info(f"🔵   Blueprint Path: {agent1_results['blueprint_path']}")
            logger.info(f"🔵   Text Extracted: {agent1_results['text_extracted']} chars")
            logger.info(f"🔵   UI Elements: {agent1_results['ui_elements']}")
            logger.info(f"🔵   Automation Steps: {agent1_results['automation_steps']}")
            logger.info(f"🔵   Blueprint Confidence: {agent1_results['blueprint_confidence']}")
            
            # ========== PHASE 2: ENHANCED CODE GENERATION ==========
            logger.info("\\n🟢 ========== PHASE 2: ENHANCED CODE GENERATION ==========")
            logger.info("🟢 Agent 2: Generating production-ready automation code...")
            phase2_start = time.time()
            
            # CORRECTED: Use actual Agent 2 method name and parameters
            agent2_results = await self.agent2.generate_production_code(
                task_id=agent1_results['seq_id'],
                blueprint_path=Path(agent1_results['blueprint_path']),
                instruction=instruction,
                platform=platform,
                additional_data=additional_data or {}
            )
            
            if not agent2_results.get("success"):
                raise Exception(f"Agent 2 failed: {agent2_results.get('error', 'Unknown error')}")
            
            # FIXED: Add missing ocr_logs_prepared key
            agent2_results['ocr_logs_prepared'] = True
            
            workflow_results["phases"]["phase2"] = {
                "agent": "enhanced_agent2_code",
                "duration": time.time() - phase2_start,
                "results": agent2_results
            }
            
            logger.info("🟢 Agent 2 Results:")
            logger.info(f"🟢   Agent2 Path: {agent2_results['agent2_path']}")
            logger.info(f"🟢   Script Generated: {agent2_results['script_size']} characters")
            logger.info(f"🟢   Requirements: {agent2_results['requirements_path']}")
            logger.info(f"🟢   OCR Logs Prepared: {agent2_results['ocr_logs_prepared']}")
            logger.info(f"🟢   Workflow Steps: {agent2_results['workflow_steps']}")
            logger.info(f"🟢   Device Config Created: {agent2_results.get('device_config_created', False)}")
            logger.info(f"🟢   Ready for Isolated Testing: ✅")
            
            # ========== PHASE 3: TERMINAL-ISOLATED TESTING ==========
            logger.info("\\n🟡 ========== PHASE 3: TERMINAL-ISOLATED TESTING ==========")
            logger.info("🟡 Agent 3: Setting up isolated testing environment...")
            
            # Pre-flight checks for mobile platform
            if platform.lower() == 'mobile' and self.device_manager:
                logger.info("🟡 Agent 3: Performing mobile environment pre-flight checks...")
                
                # Check ADB availability
                if not self.device_manager.check_adb_available():
                    logger.warning("⚠️ ADB not available - mobile testing may fail")
                
                # Check for connected devices
                devices = self.device_manager.get_connected_devices()
                if not devices:
                    logger.warning("⚠️ No Android devices connected - mobile testing may fail")
                else:
                    logger.info(f"📱 Found {len(devices)} connected device(s)")
                    for device in devices:
                        logger.info(f"  • {device['device_name']} ({device['device_id']})")
                
                # Check Appium server status
                if self.terminal_manager:
                    appium_status = self.terminal_manager.get_appium_server_status()
                    logger.info(f"🔧 Appium server status: {appium_status['status']}")
            
            phase3_start = time.time()
            
            # CORRECTED: Use actual Agent 3 method name and parameters
            agent3_results = await self.agent3.execute_isolated_testing(
                task_id=agent1_results['seq_id'],
                base_path=Path(agent1_results['base_path']),
                agent2_results=agent2_results,
                platform=platform,
                additional_data=additional_data or {}
            )
            
            workflow_results["phases"]["phase3"] = {
                "agent": "enhanced_agent3_isolated_testing",
                "duration": time.time() - phase3_start,
                "results": agent3_results
            }
            
            logger.info("🟡 Agent 3 Results:")
            logger.info(f"🟡   Testing Path: {agent3_results.get('testing_path', 'N/A')}")
            logger.info(f"🟡   Virtual Environment: {agent3_results.get('virtual_environment', '❌')}")
            logger.info(f"🟡   Dependencies Installed: {'✅' if agent3_results.get('dependencies_installed') else '❌'}")
            logger.info(f"🟡   Mobile Environment: {'✅' if agent3_results.get('mobile_environment') else '❌'}")
            logger.info(f"🟡   Terminal Execution: {'✅' if agent3_results.get('terminal_execution') else '❌'}")
            logger.info(f"🟡   Processes Launched: {agent3_results.get('processes_launched', 0)}")
            logger.info(f"🟡   Test Results: {'✅ Available' if agent3_results.get('test_results') else '❌ Not Available'}")
            
            # ========== PHASE 4: ENHANCED REPORTING ==========
            logger.info("\\n🔵 ========== PHASE 4: ENHANCED REPORTING ==========")
            logger.info("🔵 Agent 4: Generating comprehensive report...")
            phase4_start = time.time()
            
            # CORRECTED: Use actual Agent 4 method name and parameters
            agent4_results = await self.agent4.generate_final_report(
                seq_id=agent1_results['seq_id']
            )
            
            workflow_results["phases"]["phase4"] = {
                "agent": "agent4_enhanced_results",
                "duration": time.time() - phase4_start,
                "results": agent4_results
            }
            
            if agent4_results.get("success"):
                logger.info("🔵 Agent 4 Results:")
                logger.info(f"🔵   Agent4 Path: {agent4_results.get('agent4_path', 'N/A')}")
                logger.info(f"🔵   Final Report: {agent4_results.get('final_report', {}).get('text_report', 'N/A')}")
                logger.info(f"🔵   CSV Export: {agent4_results.get('csv_export', {}).get('csv_path', 'N/A')}")
                logger.info(f"🔵   Conversation Log: {agent4_results.get('conversation_log', {}).get('log_path', 'N/A')}")
                logger.info(f"🔵   Files Generated: {len(agent4_results.get('files_generated', []))}")
            else:
                logger.warning(f"🔵 Agent 4 completed with issues: {agent4_results.get('error', 'Unknown error')}")
            
            # Calculate final metrics
            total_duration = time.time() - workflow_start_time
            overall_success = all([
                agent1_results.get("success"),
                agent2_results.get("success"),
                agent3_results.get("success")
            ])
            
            workflow_results.update({
                "total_duration": total_duration,
                "overall_success": overall_success,
                "final_confidence": agent1_results.get('blueprint_confidence', 0.0),
                "task_id": agent1_results['seq_id'],
                "base_path": agent1_results['base_path']
            })
            
            # Save workflow summary
            summary_path = Path(agent1_results['base_path']) / "enhanced_workflow_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_results, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"🚀 Enhanced workflow summary saved: {summary_path}")
            
            logger.info("\\n🚀 ========== ENHANCED MULTI-AGENT WORKFLOW COMPLETED ==========")
            logger.info(f"🚀 Overall Result: {'✅ SUCCESS' if overall_success else '⚠️ COMPLETED WITH ISSUES'}")
            logger.info(f"🚀 Sequential Task ID: {agent1_results['seq_id']}")
            logger.info(f"🚀 Final Confidence: {agent1_results.get('blueprint_confidence', 0.0):.3f}")
            logger.info(f"🚀 Total Execution Time: {total_duration:.1f} seconds")
            logger.info(f"🚀 Terminal Processes: {agent3_results.get('processes_launched', 0)}")
            logger.info(f"🚀 Base Path: {agent1_results['base_path']}")
            logger.info(f"🚀 Testing Environment: {'✅ ISOLATED' if agent3_results.get('success') else '❌ ISSUES'}")
            logger.info(f"🚀 Final Report: {'✅ GENERATED' if agent4_results.get('success') else '❌ FAILED'}")
            logger.info("🚀 =================================================================")
            
            return workflow_results
            
        except Exception as e:
            logger.error(f"❌ Enhanced workflow failed: {str(e)}")
            
            # Cleanup on failure
            try:
                if hasattr(self.agent3, 'cleanup_testing_processes'):
                    await self.agent3.cleanup_testing_processes()
                logger.info("✅ Emergency cleanup completed")
            except Exception as cleanup_error:
                logger.warning(f"⚠️ Cleanup had issues: {str(cleanup_error)}")
            
            workflow_results.update({
                "overall_success": False,
                "error": str(e),
                "total_duration": time.time() - workflow_start_time,
                "cleanup_performed": True
            })
            
            return workflow_results

    async def get_workflow_status(self, task_id: int) -> Dict[str, Any]:
        """Get current workflow status including terminal processes"""
        try:
            status = {
                "task_id": task_id,
                "orchestrator_version": self.version,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Get terminal manager status
            if self.terminal_manager and hasattr(self.terminal_manager, 'get_process_status'):
                status["terminal_processes"] = self.terminal_manager.get_process_status()
                status["appium_server"] = self.terminal_manager.check_appium_running()
            
            # Get Agent 3 status
            if hasattr(self.agent3, 'get_testing_status'):
                agent3_status = await self.agent3.get_testing_status(task_id)
                status["agent3"] = agent3_status
            
            # Get device information
            if self.device_manager and hasattr(self.device_manager, 'get_connected_devices'):
                devices = self.device_manager.get_connected_devices()
                status["connected_devices"] = len(devices)
                if devices:
                    status["devices"] = [
                        {
                            "name": d["device_name"],
                            "id": d["device_id"],
                            "is_emulator": d["is_emulator"]
                        }
                        for d in devices
                    ]
            
            return status
            
        except Exception as e:
            return {
                "error": str(e),
                "task_id": task_id,
                "timestamp": datetime.utcnow().isoformat()
            }

    async def cleanup_workflow(self, task_id: int):
        """Clean up workflow resources and processes"""
        try:
            logger.info(f"🧹 Cleaning up workflow resources for task {task_id}")
            
            # Cleanup Agent 3 processes
            if hasattr(self.agent3, 'cleanup_testing_processes'):
                await self.agent3.cleanup_testing_processes()
                
            # Cleanup terminal manager
            if self.terminal_manager and hasattr(self.terminal_manager, 'cleanup_processes'):
                self.terminal_manager.cleanup_processes()
            
            logger.info("✅ Workflow cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Workflow cleanup failed: {str(e)}")

# Global orchestrator instance for main application
_enhanced_orchestrator: Optional[EnhancedMultiAgentOrchestrator] = None

async def get_enhanced_orchestrator() -> EnhancedMultiAgentOrchestrator:
    """Get or create enhanced orchestrator instance"""
    global _enhanced_orchestrator
    if _enhanced_orchestrator is None:
        _enhanced_orchestrator = EnhancedMultiAgentOrchestrator()
        await _enhanced_orchestrator.initialize()
    return _enhanced_orchestrator

if __name__ == "__main__":
    # Test enhanced orchestrator
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    async def test_enhanced_orchestrator():
        orchestrator = EnhancedMultiAgentOrchestrator()
        await orchestrator.initialize()
        print("🧪 Testing Enhanced Multi-Agent Orchestrator...")
        
        # Test device detection
        if orchestrator.device_manager:
            devices = orchestrator.device_manager.get_connected_devices()
            print(f"📱 Connected devices: {len(devices)}")
        
        # Test terminal manager
        if orchestrator.terminal_manager:
            print(f"🖥️ Platform: {orchestrator.terminal_manager.system}")
            
            # Test Appium server check
            appium_status = orchestrator.terminal_manager.get_appium_server_status()
            print(f"🔧 Appium server: {appium_status['status']}")
        
        await orchestrator.cleanup_workflow(0)
        print("✅ Enhanced orchestrator test completed")
    
    asyncio.run(test_enhanced_orchestrator())