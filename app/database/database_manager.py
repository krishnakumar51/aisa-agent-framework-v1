"""
Database Manager - TABLE ALTER FIX VERSION
CRITICAL FIX: Adds document_data column to existing automation_tasks table
+ Method signature matches main_production.py calls
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

# CRITICAL FIX: Schema update to add missing document_data column
DATABASE_SCHEMA_UPDATE = """
-- Add document_data column to automation_tasks if it doesn't exist
ALTER TABLE automation_tasks ADD COLUMN document_data TEXT DEFAULT '{}';
"""

# Complete Database Schema - WITH DOCUMENT_DATA COLUMN
DATABASE_SCHEMA = """
-- Main tasks table with sequential IDs and document_data
CREATE TABLE IF NOT EXISTS automation_tasks (
seq_id INTEGER PRIMARY KEY AUTOINCREMENT,
instruction TEXT NOT NULL,
platform TEXT DEFAULT 'auto-detect',
additional_data TEXT DEFAULT '{}',
document_data TEXT DEFAULT '{}',
status TEXT DEFAULT 'pending',
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
blueprint_generated BOOLEAN DEFAULT FALSE,
code_generated BOOLEAN DEFAULT FALSE,
testing_completed BOOLEAN DEFAULT FALSE,
final_report_generated BOOLEAN DEFAULT FALSE,
base_path TEXT NOT NULL,
current_agent TEXT DEFAULT 'agent1',
review TEXT DEFAULT '{}',
langgraph_thread_id TEXT,
langgraph_checkpoint_id TEXT
);

-- Tasks table for compatibility with document_data
CREATE TABLE IF NOT EXISTS tasks (
task_id INTEGER PRIMARY KEY AUTOINCREMENT,
instruction TEXT NOT NULL,
platform TEXT NOT NULL,
document_data TEXT DEFAULT '{}',
additional_data TEXT,
status TEXT DEFAULT 'pending',
metadata TEXT,
created_at TEXT NOT NULL,
updated_at TEXT NOT NULL
);

-- All other tables remain the same...
CREATE TABLE IF NOT EXISTS workflow_steps (
step_id INTEGER PRIMARY KEY AUTOINCREMENT,
seq_id INTEGER NOT NULL,
agent_name TEXT NOT NULL,
step_name TEXT NOT NULL,
step_order INTEGER NOT NULL,
action_type TEXT NOT NULL,
expected_result TEXT,
actual_result TEXT,
status TEXT DEFAULT 'pending',
test_attempt INTEGER DEFAULT 0,
ocr_screenshot_path TEXT,
ocr_validation_text TEXT,
error_message TEXT,
execution_time REAL DEFAULT 0.0,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (seq_id) REFERENCES automation_tasks(seq_id)
);

CREATE TABLE IF NOT EXISTS agent_communications (
comm_id INTEGER PRIMARY KEY AUTOINCREMENT,
seq_id INTEGER NOT NULL,
from_agent TEXT NOT NULL,
to_agent TEXT NOT NULL,
message_type TEXT NOT NULL,
message_content TEXT NOT NULL,
response_content TEXT,
status TEXT DEFAULT 'pending',
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
resolved_at TIMESTAMP,
langgraph_message_id TEXT,
thread_id TEXT,
checkpoint_id TEXT,
review_data TEXT DEFAULT '{}',
FOREIGN KEY (seq_id) REFERENCES automation_tasks(seq_id)
);

CREATE TABLE IF NOT EXISTS agent_executions (
id INTEGER PRIMARY KEY AUTOINCREMENT,
task_id INTEGER NOT NULL,
agent_name TEXT NOT NULL,
status TEXT NOT NULL,
metadata TEXT,
timestamp TEXT NOT NULL,
FOREIGN KEY (task_id) REFERENCES tasks (task_id)
);

CREATE TABLE IF NOT EXISTS workflow_executions (
id INTEGER PRIMARY KEY AUTOINCREMENT,
task_id INTEGER NOT NULL,
thread_id TEXT NOT NULL,
status TEXT NOT NULL,
steps INTEGER DEFAULT 0,
final_state TEXT,
timestamp TEXT NOT NULL,
FOREIGN KEY (task_id) REFERENCES tasks (task_id)
);

CREATE TABLE IF NOT EXISTS tool_executions (
id INTEGER PRIMARY KEY AUTOINCREMENT,
task_id INTEGER NOT NULL,
tool_name TEXT NOT NULL,
status TEXT NOT NULL,
input_data TEXT,
output_data TEXT,
execution_time REAL,
timestamp TEXT NOT NULL,
FOREIGN KEY (task_id) REFERENCES tasks (task_id)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_tasks_seq_id ON automation_tasks(seq_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON automation_tasks(status);
CREATE INDEX IF NOT EXISTS idx_steps_seq_id ON workflow_steps(seq_id);
"""

class DatabaseManager:
    """Database manager with TABLE ALTER support for document_data column"""

    def __init__(self, db_path: str = "automation_workflow.db"):
        self.db_path = db_path
        self.initialized = False
        self._conn = None

    async def initialize(self):
        """Initialize database with schema and ALTER existing tables - FIXED"""
        if self.initialized:
            return

        logger.info(f"🗄️ TABLE-ALTER-FIXED Database initializing: {self.db_path}")
        
        # Ensure database directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            # First, create all tables with new schema
            await db.executescript(DATABASE_SCHEMA)
            
            # CRITICAL FIX: Check if document_data column exists, if not add it
            cursor = await db.execute("PRAGMA table_info(automation_tasks)")
            columns = await cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if 'document_data' not in column_names:
                logger.info("🔧 Adding missing document_data column to automation_tasks")
                await db.execute("ALTER TABLE automation_tasks ADD COLUMN document_data TEXT DEFAULT '{}'")
                await db.commit()
                logger.info("✅ document_data column added successfully")
            else:
                logger.info("✅ document_data column already exists")
            
            # Also check tasks table
            cursor = await db.execute("PRAGMA table_info(tasks)")
            columns = await cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if 'document_data' not in column_names:
                logger.info("🔧 Adding missing document_data column to tasks")
                await db.execute("ALTER TABLE tasks ADD COLUMN document_data TEXT DEFAULT '{}'")
                await db.commit()
                logger.info("✅ document_data column added to tasks table")
            
            await db.commit()
        
        self.initialized = True
        logger.info("✅ TABLE-ALTER-FIXED Database initialized with all columns")

    # CRITICAL FIX: create_task() method signature now matches main_production.py
    async def create_task(
        self, 
        instruction: str, 
        platform: str = "auto-detect", 
        document_data: Dict = None,  # ✅ NOW ACCEPTS document_data
        additional_data: Dict = None
    ) -> int:
        """Create new automation task - SIGNATURE FIXED to match main_production.py calls"""
        await self.initialize()
        
        base_path = "generated_code"
        additional_data_str = json.dumps(additional_data or {})
        document_data_str = json.dumps(document_data or {})  # ✅ FIXED: Handle document_data
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO automation_tasks (instruction, platform, additional_data, document_data, base_path)
                VALUES (?, ?, ?, ?, ?)
                """,
                (instruction, platform, additional_data_str, document_data_str, base_path)
            )
            
            seq_id = cursor.lastrowid
            await db.commit()
            
            # Update base_path with seq_id
            await db.execute(
                "UPDATE automation_tasks SET base_path = ? WHERE seq_id = ?",
                (f"generated_code/{seq_id}", seq_id)
            )
            await db.commit()
            
            # ✅ FIXED: Also create in tasks table for compatibility with SAME signature
            await db.execute(
                """
                INSERT INTO tasks (instruction, platform, document_data, additional_data, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (instruction, platform, document_data_str, additional_data_str, "pending",
                 datetime.now().isoformat(), datetime.now().isoformat())
            )
            await db.commit()
            
            logger.info(f"📝 TABLE-ALTER-FIXED Task created {seq_id}: {instruction[:50]}...")
            return seq_id

    async def update_task_status(self, task_id: int, status: str, metadata: Optional[Dict[str, Any]] = None):
        """Update task status and metadata"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE automation_tasks
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE seq_id = ?
                """,
                (status, task_id)
            )
            await db.commit()
            
            # Also update tasks table if it exists
            if metadata:
                await db.execute(
                    "UPDATE tasks SET status = ?, metadata = ?, updated_at = ? WHERE task_id = ?",
                    (status, json.dumps(metadata), datetime.now().isoformat(), task_id)
                )
            else:
                await db.execute(
                    "UPDATE tasks SET status = ?, updated_at = ? WHERE task_id = ?",
                    (status, datetime.now().isoformat(), task_id)
                )
            await db.commit()

    async def get_task_info(self, task_id: int) -> Optional[Dict]:
        """Get complete task information"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            # Try automation_tasks first (primary)
            cursor = await db.execute(
                "SELECT * FROM automation_tasks WHERE seq_id = ?", (task_id,)
            )
            row = await cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            
            # Fallback to tasks table
            cursor = await db.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
            )
            row = await cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
        
        return None

    async def get_task(self, task_id: int) -> Optional[Dict]:
        """Get task information (alias for get_task_info for compatibility)"""
        return await self.get_task_info(task_id)

    # AGENT EXECUTION LOGGING
    async def log_agent_execution(self, task_id: int, agent_name: str, status: str, metadata: Dict[str, Any]):
        """Log agent execution status and metadata"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO agent_executions (task_id, agent_name, status, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (task_id, agent_name, status, json.dumps(metadata), datetime.now().isoformat())
            )
            await db.commit()

    async def get_agent_executions(self, task_id: int) -> List[Dict[str, Any]]:
        """Get all agent executions for a task"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM agent_executions WHERE task_id = ? ORDER BY timestamp",
                (task_id,)
            )
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    # WORKFLOW EXECUTION LOGGING
    async def log_workflow_execution(self, task_id: int, thread_id: str, status: str, steps: int, final_state: str):
        """Log workflow execution details"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO workflow_executions (task_id, thread_id, status, steps, final_state, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (task_id, thread_id, status, steps, final_state, datetime.now().isoformat())
            )
            await db.commit()

    async def get_workflow_executions(self, task_id: int) -> List[Dict[str, Any]]:
        """Get all workflow executions for a task"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM workflow_executions WHERE task_id = ? ORDER BY timestamp",
                (task_id,)
            )
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    # TOOL EXECUTION LOGGING
    async def log_tool_execution(
        self, task_id: int, tool_name: str, status: str, input_data: str,
        output_data: str = "", execution_time: float = 0.0
    ) -> int:
        """Log tool execution"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO tool_executions (task_id, tool_name, status, input_data, output_data, execution_time, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (task_id, tool_name, status, input_data, output_data, execution_time, datetime.now().isoformat())
            )
            tool_exec_id = cursor.lastrowid
            await db.commit()
            
            return tool_exec_id

    async def get_tool_executions(self, task_id: int) -> List[Dict[str, Any]]:
        """Get all tool executions for a task"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM tool_executions WHERE task_id = ? ORDER BY timestamp",
                (task_id,)
            )
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    # AGENT OUTPUT STORAGE
    async def save_agent_output(self, task_id: int, agent_name: str, output_type: str, output_data: str):
        """Save agent output data"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO agent_outputs (task_id, agent_name, output_type, output_data, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (task_id, agent_name, output_type, output_data, datetime.now().isoformat())
            )
            await db.commit()

    async def get_agent_outputs(self, task_id: int, agent_name: str = None) -> List[Dict[str, Any]]:
        """Get agent outputs for a task"""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            if agent_name:
                cursor = await db.execute(
                    "SELECT * FROM agent_outputs WHERE task_id = ? AND agent_name = ? ORDER BY timestamp",
                    (task_id, agent_name)
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM agent_outputs WHERE task_id = ? ORDER BY timestamp",
                    (task_id,)
                )
            
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    async def cleanup_database(self):
        """Cleanup database connections on shutdown"""
        if self._conn:
            await self._conn.close()
            self._conn = None
        logger.info("✅ TABLE-ALTER-FIXED Database connections closed")


# SINGLETON INSTANCE MANAGEMENT - FIXED
_database_manager_instance: Optional[DatabaseManager] = None

async def get_database_manager() -> DatabaseManager:
    """Get singleton database manager instance - FIXED"""
    global _database_manager_instance
    if _database_manager_instance is None:
        _database_manager_instance = DatabaseManager()
        await _database_manager_instance.initialize()
        logger.info("✅ TABLE-ALTER-FIXED Database manager singleton initialized")
    
    return _database_manager_instance

async def initialize_database() -> Dict[str, Any]:
    """Initialize database tables on application startup"""
    try:
        manager = await get_database_manager()
        await manager.initialize()  # This will handle the ALTER TABLE
        
        logger.info("✅ TABLE-ALTER-FIXED Database initialized successfully with document_data column")
        return {
            "success": True,
            "message": "Database initialized successfully with document_data column",
            "database_path": manager.db_path
        }
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# CLEANUP FUNCTION
async def cleanup_database():
    """Cleanup database connections on shutdown"""
    global _database_manager_instance
    if _database_manager_instance:
        await _database_manager_instance.cleanup_database()
        _database_manager_instance = None
        logger.info("✅ TABLE-ALTER-FIXED Database connections closed")

if __name__ == "__main__":
    # Test database initialization with ALTER TABLE
    import asyncio

    async def test_database():
        print("🧪 Testing TABLE-ALTER-FIXED database initialization...")
        
        # Initialize database (will run ALTER TABLE if needed)
        result = await initialize_database()
        print(f"✅ Database init result: {result['success']}")
        
        if result['success']:
            # Test basic operations with document_data
            db = await get_database_manager()
            
            # ✅ CRITICAL TEST: Create task with document_data parameter
            task_id = await db.create_task(
                instruction="Test complete automation",
                platform="web",
                document_data={"filename": "test.pdf", "size": 1234},  # ✅ NOW WORKS WITH ALTER
                additional_data={"test": True}
            )
            print(f"✅ Created test task with document_data: {task_id}")
            
            # Get task info to verify document_data was stored
            task_info = await db.get_task_info(task_id)
            document_data = json.loads(task_info.get('document_data', '{}'))
            print(f"✅ Retrieved document_data: {document_data}")
            
            # Cleanup
            await cleanup_database()
            print("🎉 TABLE-ALTER-FIXED Complete database test completed!")

    asyncio.run(test_database())