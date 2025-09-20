# Multi-Agent Automation Framework - File Structure Documentation

## Directory Structure

```
aisa-agent-framework-v1/
├── app/
│   ├── agents/                    # AI Agent implementations
│   ├── config/                    # Configuration management
│   ├── database/                  # Database layer
│   ├── drivers/                   # Automation drivers
│   ├── tools/                     # Automation tools
│   └── utils/                     # Utility modules
├── generated_code/                # Dynamic output directory
├── docs/                         # Documentation
├── tests/                        # Test suite
└── requirements.txt              # Dependencies
```

## 📁 File Descriptions by Directory

### `/app/` - Main Application Directory

#### **Main Application Files**

##### `updated_main_enhanced.py`
**Purpose**: FastAPI server and main application entry point
**Key Features**:
- RESTful API endpoints for automation requests
- File upload handling (PDF, images)
- System health monitoring
- Orchestrator integration
- CORS configuration for web access

**Main Functions**:
- `POST /automate` - Main automation endpoint
- `GET /health` - System health check
- `GET /status/{task_id}` - Task status monitoring
- Server startup/shutdown handling

**Dependencies**: FastAPI, uvicorn, file handling libraries

---

### `/app/agents/` - AI Agent Implementations

#### **Agent 1: Blueprint Generation**

##### `agent1_blueprint.py`
**Purpose**: Document analysis and workflow blueprint creation
**Key Features**:
- PDF text extraction using PyPDF2
- OCR integration for image processing  
- UI element identification and mapping
- Workflow step generation with confidence scoring
- SQLite database initialization

**Main Classes**:
- `Agent1_BlueprintGenerator`: Core blueprint generation logic
- Document processing methods
- UI element extraction utilities

**Input**: PDF documents, screenshots, instruction text
**Output**: `blueprint.json` with structured automation workflow

##### `enhanced_agent2.py`
**Purpose**: Production-ready automation code generation
**Key Features**:
- Platform-specific script generation (Mobile/Web)
- Dynamic device detection integration
- OCR-enabled automation scripts
- Error handling and retry mechanisms
- Requirements and configuration file generation

**Main Classes**:
- `EnhancedAgent2_CodeGenerator`: Main code generation engine
- `DynamicDeviceManager`: Android device detection
- `ProductionMobileAutomation`: Generated mobile automation class

**Mobile Automation Features**:
- Appium WebDriver integration
- Real device vs emulator preference
- Multi-strategy element finding
- Screenshot + OCR validation
- Dynamic capabilities generation

**Web Automation Features**:
- Playwright integration
- Multi-browser support
- Advanced wait strategies
- Network request handling

**Input**: Blueprint JSON, platform specification
**Output**: Complete automation script + requirements.txt + configurations

##### `enhanced_agent3.py` / `fixed_enhanced_agent3.py`
**Purpose**: Isolated testing environment and script execution
**Key Features**:
- Virtual environment creation and management
- Cross-platform subprocess handling (Windows/Linux/Mac)
- Dependency installation in isolation
- Mobile testing environment setup
- Script execution with timeout handling
- Process cleanup and resource management

**Main Classes**:
- `EnhancedAgent3_IsolatedTesting`: Core testing orchestrator
- Virtual environment management methods
- Mobile environment configuration
- Script execution monitoring

**Testing Process**:
1. Creates isolated virtual environment
2. Installs platform-specific dependencies  
3. Copies automation files to isolated directory
4. Executes script with proper timeout handling
5. Captures all execution logs and results
6. Cleans up processes and resources

**Input**: Generated automation script, requirements
**Output**: Test execution results, logs, environment status

##### `agent4_results.py`
**Purpose**: Comprehensive reporting and result analysis
**Key Features**:
- Multi-format report generation (TXT, JSON, CSV, HTML)
- Execution data analysis and insights
- Agent communication logging
- Interactive dashboard creation
- File organization and packaging

**Main Classes**:
- `Agent4_ResultsGenerator`: Report generation engine
- Data collection and analysis methods
- Dashboard HTML generation

**Report Types**:
- **Text Report**: Detailed execution analysis
- **CSV Export**: Structured data for further analysis  
- **JSON Log**: Complete conversation and execution log
- **HTML Dashboard**: Interactive results visualization

**Input**: Database execution records, agent communications
**Output**: Complete report package with multiple formats

---

### `/app/config/` - Configuration Management

##### `settings.py`
**Purpose**: Application configuration and environment variables
**Key Features**:
- Environment-specific settings (dev/prod/test)
- API key management (Anthropic, OpenAI)
- Database configuration
- Logging configuration
- File path management

**Configuration Categories**:
- Database settings (SQLite paths)
- API credentials and endpoints
- Logging levels and formats
- File upload limits and paths
- Automation timeouts and retries

---

### `/app/database/` - Data Persistence Layer

##### `database_manager.py`
**Purpose**: SQLite database operations and schema management
**Key Features**:
- Async SQLite operations using aiosqlite
- Comprehensive schema with 6+ tables
- Task lifecycle management
- Agent communication tracking
- File generation logging
- Test execution results storage

**Database Schema**:
```sql
automation_tasks        # Main task tracking
workflow_steps         # Individual step execution
agent_communications   # Inter-agent messages
generated_files       # File version control
testing_environments  # Environment setup tracking
test_executions       # Execution results and metrics
```

**Main Classes**:
- `TestingDatabaseManager`: Primary database interface
- Async CRUD operations for all entities
- Data export utilities (CSV generation)

---

### `/app/utils/` - Utility Modules

##### `device_manager.py`
**Purpose**: Android device detection and management
**Key Features**:
- ADB integration for device discovery
- Real device vs emulator detection
- Device capability extraction (manufacturer, model, Android version)
- Dynamic device selection algorithms
- Device health monitoring

**Main Classes**:
- `DeviceManager`: Core device management
- Device discovery and filtering methods
- Capability generation for Appium

##### `terminal_manager.py`
**Purpose**: Process and subprocess management across platforms
**Key Features**:
- Cross-platform process handling
- Terminal session management  
- Process cleanup and resource management
- Appium server status monitoring
- Subprocess timeout handling

**Main Classes**:
- `TerminalManager`: Process orchestration
- Platform-specific command execution
- Process lifecycle management

##### `testing_environment_manager.py`
**Purpose**: Virtual environment and dependency management
**Key Features**:
- Python virtual environment creation
- Package installation and version control
- Environment isolation and cleanup
- Cross-platform path handling
- Dependency conflict resolution

**Main Classes**:
- `TestingEnvironmentManager`: Environment orchestration
- Virtual environment lifecycle methods
- Package management utilities

---

### `/app/drivers/` - Automation Drivers

##### `appium_driver.py`
**Purpose**: Mobile automation driver implementation
**Key Features**:
- Appium WebDriver wrapper
- Android-specific automation methods
- Dynamic capability configuration
- Element finding strategies
- Screenshot and interaction utilities

**Main Classes**:
- `AppiumDriver`: Mobile automation interface
- Device-specific method implementations
- Error handling and retry logic

##### `playwright_driver.py`
**Purpose**: Web automation driver implementation  
**Key Features**:
- Playwright browser automation
- Multi-browser support (Chromium, Firefox, Safari)
- Advanced web interaction methods
- Network request interception
- Page performance monitoring

**Main Classes**:
- `PlaywrightDriver`: Web automation interface
- Browser lifecycle management
- Web-specific interaction methods

---

### `/app/tools/` - Automation Tool Libraries

##### `mobile_tools.py`
**Purpose**: Mobile-specific automation utilities
**Key Features**:
- Touch gesture implementations
- Mobile UI element strategies
- App lifecycle management (install/launch/close)
- Device interaction utilities
- Mobile-specific assertions

**Utility Functions**:
- Touch, swipe, and gesture methods
- App state management
- Mobile element finding strategies
- Device orientation handling

##### `web_tools.py`
**Purpose**: Web-specific automation utilities
**Key Features**:
- Advanced web element interactions
- JavaScript execution utilities
- Cookie and session management
- Form handling and validation
- Web performance monitoring

**Utility Functions**:
- DOM interaction methods
- JavaScript injection utilities
- Network request handling
- Browser state management

##### `ocr_utils.py`
**Purpose**: Optical Character Recognition integration
**Key Features**:
- Tesseract OCR integration
- Image preprocessing for better recognition
- Multi-language OCR support
- Text extraction and validation
- Screenshot analysis utilities

**Main Functions**:
- Image-to-text conversion
- OCR accuracy improvement methods
- Text validation and comparison
- Screenshot processing utilities

---

### `/app/orchestration/` - Workflow Orchestration

##### `enhanced_orchestrator.py`
**Purpose**: Main workflow coordination and agent management
**Key Features**:
- 4-phase workflow execution pipeline
- Agent communication and coordination
- Error handling and recovery mechanisms
- Resource management and cleanup
- Execution monitoring and logging

**Orchestration Flow**:
1. **Phase 1**: Blueprint Generation (Agent 1)
2. **Phase 2**: Code Generation (Agent 2)  
3. **Phase 3**: Isolated Testing (Agent 3)
4. **Phase 4**: Results & Reporting (Agent 4)

**Main Classes**:
- `EnhancedOrchestrator`: Workflow coordinator
- Agent lifecycle management
- Inter-phase communication handling
- Error recovery and cleanup procedures

**Error Handling**:
- Agent-level error recovery
- Resource cleanup on failures
- Alternative execution paths
- Comprehensive error logging

---

### `/generated_code/` - Dynamic Output Directory

**Purpose**: Task-specific output organization
**Structure**: Each task gets a unique directory by task ID

```
generated_code/{task_id}/
├── agent1/
│   └── blueprint.json           # Workflow blueprint
├── agent2/  
│   ├── script.py               # Generated automation script
│   ├── requirements.txt        # Dependencies
│   ├── device_config.json      # Device configuration
│   └── ocr_logs/              # OCR templates
├── agent3/
│   └── testing/
│       ├── venv/              # Isolated virtual environment
│       ├── script.py          # Copy of automation script
│       ├── requirements.txt   # Copy of dependencies
│       ├── mobile_config.json # Mobile-specific config
│       └── execution_logs/    # Runtime logs
├── agent4/
│   ├── final_report.txt       # Detailed text report
│   ├── final_report.csv       # Structured data export
│   ├── conversation.json      # Complete execution log
│   └── summary_dashboard.html # Interactive dashboard
├── sqlite_db.sqlite           # Task-specific database
└── enhanced_workflow_summary.json # Complete workflow summary
```

---

## 🔧 Specialized Components

### Legacy Components (Backward Compatibility)

##### `langgraph_orchestrator.py`
**Purpose**: Alternative orchestration using LangGraph framework
**Status**: Legacy - maintained for compatibility
**Features**: Graph-based agent coordination, alternative to enhanced orchestrator

##### `code_agent.py`, `results_agent.py`
**Purpose**: Original agent implementations
**Status**: Legacy - replaced by enhanced versions
**Features**: Basic code generation and results processing

### External Integration Files

##### `outlook.py`, `comp.py`
**Purpose**: Outlook-specific automation components
**Features**: Outlook API integration, email automation utilities
**Usage**: Referenced by generated scripts for email automation tasks

---

## 🚀 Execution Flow File Interaction

### Typical Request Flow
1. **`updated_main_enhanced.py`** receives API request
2. **`enhanced_orchestrator.py`** coordinates workflow
3. **`agent1_blueprint.py`** processes document → blueprint
4. **`enhanced_agent2.py`** generates automation code
5. **`enhanced_agent3.py`** executes in isolated environment
6. **`agent4_results.py`** generates comprehensive reports
7. **`database_manager.py`** persists all data throughout

### File Dependencies
- All agents depend on `database_manager.py` for persistence
- Agent 2 uses `device_manager.py` for mobile automation
- Agent 3 uses `terminal_manager.py` and `testing_environment_manager.py`
- Drivers (`appium_driver.py`, `playwright_driver.py`) used by generated scripts
- Tools (`mobile_tools.py`, `web_tools.py`, `ocr_utils.py`) imported by automation scripts

### Configuration Flow
- `settings.py` provides environment variables to all components
- `database_manager.py` uses settings for database configuration
- Agents use settings for AI API keys and operational parameters

## 📊 File Size and Complexity Metrics

| Component | Lines of Code | Complexity | Purpose |
|-----------|---------------|------------|---------|
| `enhanced_agent2.py` | 1000+ | High | Complete script generation |
| `enhanced_orchestrator.py` | 500+ | High | Workflow coordination |
| `enhanced_agent3.py` | 600+ | High | Testing environment |
| `agent1_blueprint.py` | 500+ | Medium | Document processing |
| `agent4_results.py` | 600+ | Medium | Report generation |
| `database_manager.py` | 400+ | Medium | Data persistence |
| `updated_main_enhanced.py` | 300+ | Medium | API server |
| Utility files | 200-300 each | Low-Medium | Specialized functions |

## 🔄 Inter-File Communication Patterns

### Database-Centric Communication
- All agents communicate through shared SQLite database
- `database_manager.py` provides unified interface
- Async operations prevent blocking

### Direct File Passing  
- Generated files passed between agents via filesystem
- Structured directory organization prevents conflicts
- Version control through database tracking

### Process Isolation
- Agent 3 creates completely isolated execution environment
- Virtual environments prevent dependency conflicts
- Process cleanup ensures resource management

This comprehensive file structure enables enterprise-grade automation generation with complete traceability, isolated execution, and extensive error handling across both mobile and web platforms.