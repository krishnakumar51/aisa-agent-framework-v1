"""
Updated SQLite Database Schema for Testing Environment Integration
Enhanced schema with sequential IDs and testing environment tracking
FIXED: Added missing methods that Agent 3 needs, using correct column names
"""

import sqlite3
import asyncio
import aiosqlite
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Updated Database Schema SQL
DATABASE_SCHEMA = """
-- Main tasks table with sequential IDs
CREATE TABLE IF NOT EXISTS automation_tasks (
    seq_id INTEGER PRIMARY KEY AUTOINCREMENT,
    instruction TEXT NOT NULL,
    platform TEXT DEFAULT 'auto-detect',
    additional_data TEXT DEFAULT '{}',
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    blueprint_generated BOOLEAN DEFAULT FALSE,
    code_generated BOOLEAN DEFAULT FALSE,
    testing_completed BOOLEAN DEFAULT FALSE,
    final_report_generated BOOLEAN DEFAULT FALSE,
    base_path TEXT NOT NULL,
    current_agent TEXT DEFAULT 'agent1'
);

-- Workflow steps with testing details
CREATE TABLE IF NOT EXISTS workflow_steps (
    step_id INTEGER PRIMARY KEY AUTOINCREMENT,
    seq_id INTEGER NOT NULL,
    agent_name TEXT NOT NULL,
    step_name TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    expected_result TEXT,
    actual_result TEXT,
    status TEXT DEFAULT 'pending', -- pending, in_progress, completed, failed
    test_attempt INTEGER DEFAULT 0,
    ocr_screenshot_path TEXT,
    ocr_validation_text TEXT,
    error_message TEXT,
    execution_time REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seq_id) REFERENCES automation_tasks(seq_id)
);

-- Agent communications for collaboration
CREATE TABLE IF NOT EXISTS agent_communications (
    comm_id INTEGER PRIMARY KEY AUTOINCREMENT,
    seq_id INTEGER NOT NULL,
    from_agent TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    message_type TEXT NOT NULL, -- code_issue, code_update, test_result, final_report
    message_content TEXT NOT NULL,
    response_content TEXT,
    status TEXT DEFAULT 'pending', -- pending, resolved
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (seq_id) REFERENCES automation_tasks(seq_id)
);

-- Generated files tracking
CREATE TABLE IF NOT EXISTS generated_files (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    seq_id INTEGER NOT NULL,
    agent_name TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL, -- blueprint, script, requirements, report, ocr_log
    version INTEGER DEFAULT 1, -- script.py=1, update_1.py=2, update_2.py=3, etc.
    is_active BOOLEAN DEFAULT TRUE,
    file_size INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seq_id) REFERENCES automation_tasks(seq_id)
);

-- Testing environment tracking
CREATE TABLE IF NOT EXISTS testing_environments (
    env_id INTEGER PRIMARY KEY AUTOINCREMENT,
    seq_id INTEGER NOT NULL,
    environment_type TEXT NOT NULL, -- appium, playwright
    venv_path TEXT NOT NULL,
    requirements_installed BOOLEAN DEFAULT FALSE,
    appium_server_running BOOLEAN DEFAULT FALSE,
    playwright_installed BOOLEAN DEFAULT FALSE,
    setup_status TEXT DEFAULT 'pending', -- pending, setup, ready, failed
    setup_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seq_id) REFERENCES automation_tasks(seq_id)
);

-- Test execution results
CREATE TABLE IF NOT EXISTS test_executions (
    exec_id INTEGER PRIMARY KEY AUTOINCREMENT,
    seq_id INTEGER NOT NULL,
    step_id INTEGER,
    script_version INTEGER NOT NULL, -- 1=script.py, 2=update_1.py, etc.
    execution_attempt INTEGER DEFAULT 1,
    success BOOLEAN DEFAULT FALSE,
    execution_output TEXT,
    error_details TEXT,
    screenshot_before TEXT,
    screenshot_after TEXT,
    ocr_before TEXT,
    ocr_after TEXT,
    execution_duration REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seq_id) REFERENCES automation_tasks(seq_id),
    FOREIGN KEY (step_id) REFERENCES workflow_steps(step_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_tasks_seq_id ON automation_tasks(seq_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON automation_tasks(status);
CREATE INDEX IF NOT EXISTS idx_steps_seq_id ON workflow_steps(seq_id);
CREATE INDEX IF NOT EXISTS idx_steps_status ON workflow_steps(status);
CREATE INDEX IF NOT EXISTS idx_comms_seq_id ON agent_communications(seq_id);
CREATE INDEX IF NOT EXISTS idx_files_seq_id ON generated_files(seq_id);
CREATE INDEX IF NOT EXISTS idx_envs_seq_id ON testing_environments(seq_id);
CREATE INDEX IF NOT EXISTS idx_execs_seq_id ON test_executions(seq_id);
"""


class TestingDatabaseManager:
    """Enhanced database manager for testing environment workflow - FIXED VERSION"""
    
    def __init__(self, db_path: str = "sqlite_db.sqlite"):
        self.db_path = db_path
        self.initialized = False
    
    async def initialize(self):
        """Initialize database with testing schema"""
        if self.initialized:
            return
            
        logger.info(f"🗄️ Initializing testing database: {self.db_path}")
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(DATABASE_SCHEMA)
            await db.commit()
        
        self.initialized = True
        logger.info("✅ Testing database initialized")
    
    async def create_task(self, instruction: str, platform: str = "auto-detect", 
                         additional_data: Dict = None) -> int:
        """Create new automation task and return sequential ID"""
        await self.initialize()
        
        base_path = "generated_code"
        additional_data_str = json.dumps(additional_data or {})
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO automation_tasks (instruction, platform, additional_data, base_path)
                VALUES (?, ?, ?, ?)
                """,
                (instruction, platform, additional_data_str, base_path)
            )
            seq_id = cursor.lastrowid
            await db.commit()
            
            # Update base_path with seq_id
            await db.execute(
                "UPDATE automation_tasks SET base_path = ? WHERE seq_id = ?",
                (f"generated_code/{seq_id}", seq_id)
            )
            await db.commit()
        
        logger.info(f"📝 Created task {seq_id}: {instruction[:50]}...")
        return seq_id
    
    async def update_task_status(self, seq_id: int, status: str, current_agent: str = None):
        """Update task status and current agent"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            if current_agent:
                await db.execute(
                    """
                    UPDATE automation_tasks 
                    SET status = ?, current_agent = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE seq_id = ?
                    """,
                    (status, current_agent, seq_id)
                )
            else:
                await db.execute(
                    """
                    UPDATE automation_tasks 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE seq_id = ?
                    """,
                    (status, seq_id)
                )
            await db.commit()
    
    async def update_task_progress(self, seq_id: int, **kwargs):
        """Update task progress flags"""
        await self.initialize()
        
        updates = []
        params = []
        
        for key, value in kwargs.items():
            if key in ['blueprint_generated', 'code_generated', 'testing_completed', 'final_report_generated']:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if updates:
            params.append(seq_id)
            sql = f"UPDATE automation_tasks SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE seq_id = ?"
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(sql, params)
                await db.commit()
    
    async def create_workflow_steps(self, seq_id: int, agent_name: str, steps: List[Dict]) -> List[int]:
        """Create workflow steps for task"""
        await self.initialize()
        
        step_ids = []
        
        async with aiosqlite.connect(self.db_path) as db:
            for i, step_data in enumerate(steps):
                cursor = await db.execute(
                    """
                    INSERT INTO workflow_steps 
                    (seq_id, agent_name, step_name, step_order, action_type, expected_result)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        seq_id, agent_name,
                        step_data.get('step_name', f"Step {i+1}"),
                        i+1,
                        step_data.get('action_type', 'action'),
                        step_data.get('expected_result', 'Success')
                    )
                )
                step_ids.append(cursor.lastrowid)
            await db.commit()
        
        logger.info(f"📋 Created {len(step_ids)} workflow steps for task {seq_id}")
        return step_ids
    
    async def update_step_status(self, step_id: int, status: str, **kwargs):
        """Update workflow step status and details"""
        await self.initialize()
        
        updates = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
        params = [status]
        
        for key, value in kwargs.items():
            if key in ['actual_result', 'test_attempt', 'ocr_screenshot_path', 
                      'ocr_validation_text', 'error_message', 'execution_time']:
                updates.append(f"{key} = ?")
                params.append(value)
        
        params.append(step_id)
        sql = f"UPDATE workflow_steps SET {', '.join(updates)} WHERE step_id = ?"
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(sql, params)
            await db.commit()
    
    # NEW FIXED METHOD - Uses step_order instead of step_number
    async def update_workflow_step_status(
        self,
        seq_id: int,
        step_number: int,  # This is the step position (1, 2, 3, etc.)
        status: str,
        execution_time: float = 0.0,
        error_details: str = "",
        screenshot_path: str = "",
        analysis_data: str = ""
    ) -> bool:
        """Update workflow step status - FIXED to use step_order column instead of step_number"""
        
        try:
            await self.initialize()
            
            # Use step_order column (which exists) instead of step_number (which doesn't exist)
            update_query = """
            UPDATE workflow_steps 
            SET 
                status = ?,
                execution_time = ?,
                error_message = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE seq_id = ? AND step_order = ?
            """
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    update_query,
                    (status, execution_time, error_details, seq_id, step_number)
                )
                await db.commit()
            
            logger.info(f"📊 Updated workflow step {step_number} status: {status}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update workflow step status: {str(e)}")
            return False
    
    # NEW FIXED METHOD - Uses existing create_agent_communication
    async def save_agent_communication(
        self,
        seq_id: int,
        from_agent: str,
        to_agent: str,
        message_type: str,
        message_content: str,
        status: str = "sent"
    ) -> Optional[int]:
        """Save agent-to-agent communication - COMPATIBLE VERSION"""
        
        try:
            await self.initialize()
            
            # Use the existing create_agent_communication method
            comm_id = await self.create_agent_communication(
                seq_id, from_agent, to_agent, message_type, message_content
            )
            
            logger.info(f"💬 Saved agent communication: {from_agent} -> {to_agent}")
            return comm_id
            
        except Exception as e:
            logger.error(f"❌ Failed to save agent communication: {str(e)}")
            return None
    
    async def create_agent_communication(self, seq_id: int, from_agent: str, to_agent: str,
                                       message_type: str, message_content: str) -> int:
        """Create agent communication record"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO agent_communications 
                (seq_id, from_agent, to_agent, message_type, message_content)
                VALUES (?, ?, ?, ?, ?)
                """,
                (seq_id, from_agent, to_agent, message_type, message_content)
            )
            comm_id = cursor.lastrowid
            await db.commit()
        
        logger.info(f"💬 Agent {from_agent} -> {to_agent}: {message_type}")
        return comm_id
    
    async def update_communication_response(self, comm_id: int, response_content: str):
        """Update agent communication with response"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE agent_communications 
                SET response_content = ?, status = 'resolved', resolved_at = CURRENT_TIMESTAMP 
                WHERE comm_id = ?
                """,
                (response_content, comm_id)
            )
            await db.commit()
    
    async def save_generated_file(
        self, seq_id: int, agent_name: str, file_name: str, 
        file_path: str, file_type: str, version: int = 1
    ) -> int:
        """Save generated file metadata"""
        await self.initialize()
        
        file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO generated_files 
                (seq_id, agent_name, file_name, file_path, file_type, version, file_size)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (seq_id, agent_name, file_name, file_path, file_type, version, file_size)
            )
            file_id = cursor.lastrowid
            await db.commit()
        
        logger.info(f"💾 Saved file {file_name} (v{version}) for task {seq_id}")
        return file_id
    
    async def create_testing_environment(self, seq_id: int, environment_type: str, venv_path: str) -> int:
        """Create testing environment record"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO testing_environments 
                (seq_id, environment_type, venv_path)
                VALUES (?, ?, ?)
                """,
                (seq_id, environment_type, venv_path)
            )
            env_id = cursor.lastrowid
            await db.commit()
        
        logger.info(f"🧪 Created testing environment {environment_type} for task {seq_id}")
        return env_id
    
    async def update_testing_environment(self, seq_id: int, **kwargs):
        """Update testing environment status"""
        await self.initialize()
        
        updates = []
        params = []
        
        for key, value in kwargs.items():
            if key in [
                'requirements_installed', 'appium_server_running', 
                'playwright_installed', 'setup_status', 'setup_error'
            ]:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if updates:
            params.append(seq_id)
            sql = f"UPDATE testing_environments SET {', '.join(updates)} WHERE seq_id = ?"
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(sql, params)
                await db.commit()
    
    async def save_test_execution(
        self, seq_id: int, script_version: int, execution_attempt: int, 
        success: bool, **kwargs
    ) -> int:
        """Save test execution result"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO test_executions 
                (seq_id, script_version, execution_attempt, success,
                 execution_output, error_details, 
                 screenshot_before, screenshot_after, 
                 ocr_before, ocr_after, execution_duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    seq_id, script_version, execution_attempt, success,
                    kwargs.get('execution_output', ''),
                    kwargs.get('error_details', ''),
                    kwargs.get('screenshot_before', ''),
                    kwargs.get('screenshot_after', ''),
                    kwargs.get('ocr_before', ''),
                    kwargs.get('ocr_after', ''),
                    kwargs.get('execution_duration', 0.0)
                )
            )
            exec_id = cursor.lastrowid
            await db.commit()
        
        status_emoji = "✅" if success else "❌"
        logger.info(f"🎯 Test execution {status_emoji} - Task {seq_id}, Script v{script_version}, Attempt {execution_attempt}")
        return exec_id
    
    async def get_task_info(self, seq_id: int) -> Optional[Dict]:
        """Get complete task information"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM automation_tasks WHERE seq_id = ?", (seq_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    
    async def get_workflow_steps(self, seq_id: int, status: str = None) -> List[Dict]:
        """Get workflow steps for task"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            if status:
                cursor = await db.execute(
                    "SELECT * FROM workflow_steps WHERE seq_id = ? AND status = ? ORDER BY step_order",
                    (seq_id, status)
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM workflow_steps WHERE seq_id = ? ORDER BY step_order",
                    (seq_id,)
                )
            
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def get_latest_script_version(self, seq_id: int) -> int:
        """Get latest script version number"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT MAX(version) FROM generated_files 
                WHERE seq_id = ? AND file_type = 'script' AND is_active = TRUE
                """,
                (seq_id,)
            )
            result = await cursor.fetchone()
            return result[0] if result and result[0] else 1
    
    async def export_to_csv(self, seq_id: int, export_path: str):
        """Export task data to CSV for Agent 4"""
        await self.initialize()
        import csv
        
        # Get comprehensive data
        task_info = await self.get_task_info(seq_id)
        workflow_steps = await self.get_workflow_steps(seq_id)
        
        async with aiosqlite.connect(self.db_path) as db:
            # Get communications
            comm_cursor = await db.execute(
                "SELECT * FROM agent_communications WHERE seq_id = ? ORDER BY created_at",
                (seq_id,)
            )
            communications = await comm_cursor.fetchall()
            
            # Get executions
            exec_cursor = await db.execute(
                "SELECT * FROM test_executions WHERE seq_id = ? ORDER BY created_at",
                (seq_id,)
            )
            executions = await exec_cursor.fetchall()
        
        # Write to CSV
        with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Task summary
            writer.writerow(['=== TASK SUMMARY ==='])
            writer.writerow(['seq_id','instruction','platform','status','created_at'])
            writer.writerow([
                task_info['seq_id'], task_info['instruction'], 
                task_info['platform'], task_info['status'], task_info['created_at']
            ])
            writer.writerow([])
            
            # Workflow steps  
            writer.writerow(['=== WORKFLOW STEPS ==='])
            writer.writerow(['step_id','step_name','action_type','status','test_attempt','execution_time'])
            for step in workflow_steps:
                writer.writerow([
                    step['step_id'], step['step_name'], step['action_type'],
                    step['status'], step['test_attempt'], step['execution_time']
                ])
            writer.writerow([])
            
            # Agent communications
            writer.writerow(['=== AGENT COMMUNICATIONS ==='])
            writer.writerow(['from_agent','to_agent','message_type','status','created_at'])
            for comm in communications:
                writer.writerow([comm[2],comm[3],comm[4],comm[7],comm[8]])
            writer.writerow([])
            
            # Test executions
            writer.writerow(['=== TEST EXECUTIONS ==='])
            writer.writerow(['script_version','execution_attempt','success','execution_duration','created_at'])
            for ex in executions:
                writer.writerow([ex[2],ex[3],ex[4],ex[9],ex[10]])
        
        logger.info(f"📊 Exported task {seq_id} data to {export_path}")


# Global database manager instance
testing_db = TestingDatabaseManager()

async def get_testing_db() -> TestingDatabaseManager:
    """Get the global testing database manager"""
    if not testing_db.initialized:
        await testing_db.initialize()
    return testing_db


if __name__ == "__main__":
    # Test database functionality
    async def test_db():
        db = await get_testing_db()
        print("🧪 Database test completed")
    
    asyncio.run(test_db())