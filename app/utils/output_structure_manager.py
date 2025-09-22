"""
Output Structure Manager - COMPLETE FIXED VERSION
FIXES:
- Added missing get_agent4_output_path() and sibling methods
- All output path getters ensure directories exist
- Complete folder structure management
- All original functionality preserved
"""
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

logger = logging.getLogger(__name__)

class OutputStructureManager:
    """
    COMPLETELY FIXED Output Structure Manager
    Manages complete output directory structure for automation workflows.
    FIXES:
    - Added missing get_agentX_output_path() methods
    - Directory creation guarantees
    - Complete integration with IntegrationManager
    """

    def __init__(self, task_id: int, base_path: str = "generated_code"):
        self.task_id = task_id
        self.base_path = Path(base_path)
        self.task_path = self.base_path / str(task_id)
        
        # Define exact structure paths
        self.agent1_path = self.task_path / "agent1"
        self.agent2_path = self.task_path / "agent2"
        self.agent3_path = self.task_path / "agent3"
        self.agent3_testing_path = self.agent3_path / "testing"
        self.agent4_path = self.task_path / "agent4"
        
        logger.info(f"📁 FIXED Output structure manager initialized for task {task_id}")

    def create_complete_structure(self) -> Dict[str, Any]:
        """Create the complete directory structure for a task"""
        try:
            # Create base task directory
            self.task_path.mkdir(parents=True, exist_ok=True)
            
            # Create agent directories
            self.agent1_path.mkdir(exist_ok=True)
            self.agent2_path.mkdir(exist_ok=True)
            self.agent3_path.mkdir(exist_ok=True)
            self.agent3_testing_path.mkdir(exist_ok=True)
            self.agent4_path.mkdir(exist_ok=True)
            
            # Create README files for each agent
            self._create_readme_files()
            
            structure = {
                "success": True,
                "task_id": self.task_id,
                "base_path": str(self.base_path),
                "task_path": str(self.task_path),
                "directories": {
                    "agent1": str(self.agent1_path),
                    "agent2": str(self.agent2_path),
                    "agent3": str(self.agent3_path),
                    "agent3_testing": str(self.agent3_testing_path),
                    "agent4": str(self.agent4_path)
                },
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Complete directory structure created for task {self.task_id}")
            return structure
            
        except Exception as e:
            logger.error(f"❌ Failed to create directory structure: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "task_id": self.task_id
            }

    def _create_readme_files(self):
        """Create README files for each agent directory"""
        readme_contents = {
            "agent1": f"# Agent 1 - Blueprint Generation\n\nTask ID: {self.task_id}\nGenerated: {datetime.now().isoformat()}\n\nThis directory contains blueprint generation outputs:\n- UI element analysis\n- Workflow step definitions\n- Platform-specific configurations\n",
            "agent2": f"# Agent 2 - Code Generation\n\nTask ID: {self.task_id}\nGenerated: {datetime.now().isoformat()}\n\nThis directory contains code generation outputs:\n- Generated automation scripts\n- Requirements and dependencies\n- Platform-specific implementations\n",
            "agent3": f"# Agent 3 - Testing & Execution\n\nTask ID: {self.task_id}\nGenerated: {datetime.now().isoformat()}\n\nThis directory contains testing outputs:\n- Environment setup results\n- Test execution logs\n- Validation reports\n",
            "agent4": f"# Agent 4 - Final Results\n\nTask ID: {self.task_id}\nGenerated: {datetime.now().isoformat()}\n\nThis directory contains final outputs:\n- Comprehensive reports\n- Integration summaries\n- Conversation logs\n- SQLite exports\n"
        }
        
        for agent, content in readme_contents.items():
            readme_path = getattr(self, f"{agent}_path") / "README.md"
            try:
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                logger.warning(f"Could not create README for {agent}: {str(e)}")

    # CRITICAL FIX: Added missing output path getters used by IntegrationManager
    def get_output_root_path(self) -> Path:
        """Return the task's root output directory and ensure it exists."""
        self.task_path.mkdir(parents=True, exist_ok=True)
        return self.task_path

    def get_agent1_output_path(self) -> Path:
        """Return Agent1 output directory and ensure it exists."""
        self.agent1_path.mkdir(parents=True, exist_ok=True)
        return self.agent1_path

    def get_agent2_output_path(self) -> Path:
        """Return Agent2 output directory and ensure it exists."""
        self.agent2_path.mkdir(parents=True, exist_ok=True)
        return self.agent2_path

    def get_agent3_output_path(self) -> Path:
        """Return Agent3 base directory and ensure it exists."""
        self.agent3_path.mkdir(parents=True, exist_ok=True)
        return self.agent3_path

    def get_agent3_testing_output_path(self) -> Path:
        """Return Agent3 testing directory and ensure it exists."""
        self.agent3_testing_path.mkdir(parents=True, exist_ok=True)
        return self.agent3_testing_path

    def get_agent4_output_path(self) -> Path:
        """Return Agent4 output directory and ensure it exists."""
        self.agent4_path.mkdir(parents=True, exist_ok=True)
        return self.agent4_path

    # Original methods preserved
    def get_agent1_path(self) -> Path:
        """Get Agent1 directory path"""
        return self.agent1_path
    
    def get_agent2_path(self) -> Path:
        """Get Agent2 directory path"""
        return self.agent2_path
    
    def get_agent3_path(self) -> Path:
        """Get Agent3 directory path"""
        return self.agent3_path
    
    def get_agent3_testing_path(self) -> Path:
        """Get Agent3 testing directory path"""
        return self.agent3_testing_path
    
    def get_agent4_path(self) -> Path:
        """Get Agent4 directory path"""
        return self.agent4_path

    def save_agent1_blueprint(self, blueprint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save Agent1 blueprint data"""
        try:
            self.agent1_path.mkdir(parents=True, exist_ok=True)
            
            # Save blueprint as JSON
            blueprint_file = self.agent1_path / "blueprint.json"
            with open(blueprint_file, 'w', encoding='utf-8') as f:
                json.dump(blueprint_data, f, indent=2, ensure_ascii=False)
            
            # Save UI elements if present
            if 'ui_elements' in blueprint_data:
                ui_elements_file = self.agent1_path / "ui_elements.json"
                with open(ui_elements_file, 'w', encoding='utf-8') as f:
                    json.dump(blueprint_data['ui_elements'], f, indent=2, ensure_ascii=False)
            
            # Save workflow steps if present
            if 'workflow_steps' in blueprint_data:
                workflow_file = self.agent1_path / "workflow_steps.json"
                with open(workflow_file, 'w', encoding='utf-8') as f:
                    json.dump(blueprint_data['workflow_steps'], f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "files_saved": [str(blueprint_file)] + 
                              ([str(self.agent1_path / "ui_elements.json")] if 'ui_elements' in blueprint_data else []) +
                              ([str(self.agent1_path / "workflow_steps.json")] if 'workflow_steps' in blueprint_data else []),
                "saved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to save Agent1 blueprint: {str(e)}")
            return {"success": False, "error": str(e)}

    def save_agent2_code(self, code_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save Agent2 generated code"""
        try:
            self.agent2_path.mkdir(parents=True, exist_ok=True)
            saved_files = []
            
            # Save main script
            if 'script_content' in code_data:
                script_file = self.agent2_path / "automation_script.py"
                with open(script_file, 'w', encoding='utf-8') as f:
                    f.write(code_data['script_content'])
                saved_files.append(str(script_file))
            
            # Save requirements
            if 'requirements_content' in code_data:
                req_file = self.agent2_path / "requirements.txt"
                with open(req_file, 'w', encoding='utf-8') as f:
                    f.write(code_data['requirements_content'])
                saved_files.append(str(req_file))
            
            # Save code metadata
            metadata = {
                k: v for k, v in code_data.items() 
                if k not in ['script_content', 'requirements_content']
            }
            metadata_file = self.agent2_path / "code_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            saved_files.append(str(metadata_file))
            
            return {
                "success": True,
                "files_saved": saved_files,
                "saved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to save Agent2 code: {str(e)}")
            return {"success": False, "error": str(e)}

    def save_agent3_testing(self, testing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save Agent3 testing results"""
        try:
            self.agent3_path.mkdir(parents=True, exist_ok=True)
            self.agent3_testing_path.mkdir(parents=True, exist_ok=True)
            saved_files = []
            
            # Save testing results
            results_file = self.agent3_testing_path / "testing_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(testing_data, f, indent=2, ensure_ascii=False)
            saved_files.append(str(results_file))
            
            # Save environment config if present
            if 'device_config' in testing_data:
                config_file = self.agent3_path / "device_config.json"
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(testing_data['device_config'], f, indent=2, ensure_ascii=False)
                saved_files.append(str(config_file))
            
            # Save test logs if present
            if 'test_logs' in testing_data:
                log_file = self.agent3_testing_path / "test_logs.txt"
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(testing_data['test_logs'])
                saved_files.append(str(log_file))
            
            return {
                "success": True,
                "files_saved": saved_files,
                "saved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to save Agent3 testing: {str(e)}")
            return {"success": False, "error": str(e)}

    def save_agent4_results(self, results_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save Agent4 final results"""
        try:
            self.agent4_path.mkdir(parents=True, exist_ok=True)
            saved_files = []
            
            # Save final results
            results_file = self.agent4_path / "final_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            saved_files.append(str(results_file))
            
            # Save comprehensive report if present
            if 'comprehensive_report' in results_data:
                report_file = self.agent4_path / "comprehensive_report.md"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(results_data['comprehensive_report'])
                saved_files.append(str(report_file))
            
            # Save success metrics if present
            if 'success_metrics' in results_data:
                metrics_file = self.agent4_path / "success_metrics.json"
                with open(metrics_file, 'w', encoding='utf-8') as f:
                    json.dump(results_data['success_metrics'], f, indent=2, ensure_ascii=False)
                saved_files.append(str(metrics_file))
            
            return {
                "success": True,
                "files_saved": saved_files,
                "saved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to save Agent4 results: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_task_summary(self) -> Dict[str, Any]:
        """Get complete task summary"""
        try:
            summary = {
                "task_id": self.task_id,
                "base_path": str(self.base_path),
                "task_path": str(self.task_path),
                "structure_exists": self.task_path.exists(),
                "agents": {}
            }
            
            # Check each agent directory
            for agent in ["agent1", "agent2", "agent3", "agent4"]:
                agent_path = getattr(self, f"{agent}_path")
                agent_info = {
                    "path": str(agent_path),
                    "exists": agent_path.exists(),
                    "files": []
                }
                
                if agent_path.exists():
                    try:
                        agent_info["files"] = [f.name for f in agent_path.iterdir() if f.is_file()]
                    except Exception:
                        agent_info["files"] = []
                
                summary["agents"][agent] = agent_info
            
            # Special handling for agent3 testing
            summary["agents"]["agent3"]["testing"] = {
                "path": str(self.agent3_testing_path),
                "exists": self.agent3_testing_path.exists(),
                "files": []
            }
            
            if self.agent3_testing_path.exists():
                try:
                    summary["agents"]["agent3"]["testing"]["files"] = [
                        f.name for f in self.agent3_testing_path.iterdir() if f.is_file()
                    ]
                except Exception:
                    pass
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to get task summary: {str(e)}")
            return {"error": str(e), "task_id": self.task_id}

    def cleanup_task(self) -> Dict[str, Any]:
        """Clean up task directory"""
        try:
            if self.task_path.exists():
                shutil.rmtree(self.task_path)
                logger.info(f"🧹 Cleaned up task {self.task_id} directory")
                return {
                    "success": True,
                    "task_id": self.task_id,
                    "cleaned_path": str(self.task_path),
                    "cleaned_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": True,
                    "task_id": self.task_id,
                    "message": "Task directory did not exist",
                    "path": str(self.task_path)
                }
        except Exception as e:
            logger.error(f"❌ Failed to cleanup task {self.task_id}: {str(e)}")
            return {"success": False, "error": str(e), "task_id": self.task_id}

    def archive_task(self, archive_path: Optional[str] = None) -> Dict[str, Any]:
        """Archive task directory"""
        try:
            if not self.task_path.exists():
                return {"success": False, "error": "Task directory does not exist"}
            
            if not archive_path:
                archive_path = f"archives/task_{self.task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            archive_path = Path(archive_path)
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copytree(self.task_path, archive_path)
            
            logger.info(f"📦 Archived task {self.task_id} to {archive_path}")
            return {
                "success": True,
                "task_id": self.task_id,
                "source_path": str(self.task_path),
                "archive_path": str(archive_path),
                "archived_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to archive task {self.task_id}: {str(e)}")
            return {"success": False, "error": str(e), "task_id": self.task_id}