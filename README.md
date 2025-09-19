# Document Automation Framework

A complete multi-agent automation framework that processes PDF instructions and screenshots to generate and execute automation scripts for web and mobile applications.

## 🚀 Features

- **Multi-Agent Pipeline**: 4 specialized agents working in sequence
- **Multi-Model Support**: Anthropic Claude Sonnet (default), OpenAI GPT-4, Google Gemini Flash 2.5
- **Dual Platform**: Web automation (Playwright) and Mobile automation (Appium)
- **LangGraph Orchestration**: Robust workflow management with state persistence
- **FastAPI Backend**: High-performance async API with automatic documentation
- **Production Ready**: Docker support, error handling, logging, and monitoring

## 🏗️ Architecture

```
User → Agent1 (Document Processing) → Agent2 (Code Generation) → Agent3 (LLM Supervision) → Agent4 (Result Validation) → User
```

### Agent Flow
1. **Document Agent**: Parses PDF + screenshots → UI blueprint (3 minutes)
2. **Code Agent**: Detects platform → generates Playwright/Appium script (1 minute)  
3. **LLM Supervisor**: Executes script with adaptive retries (2.5 minutes)
4. **Results Agent**: Validates results → formatted JSON output (10 seconds)

**Total Execution Time**: ~6.5 minutes

## 📁 Project Structure

```
automation_framework/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── agents/                 # Multi-agent implementations
│   │   ├── document_agent.py   # PDF/screenshot processing
│   │   ├── code_agent.py       # Script generation
│   │   ├── llm_supervisor.py   # Execution supervision
│   │   └── results_agent.py    # Result validation
│   ├── drivers/                # Automation drivers
│   │   ├── playwright_driver.py # Web automation
│   │   └── appium_driver.py     # Mobile automation
│   ├── workflow/
│   │   └── graph.py            # LangGraph workflow definition
│   ├── models/
│   │   └── schemas.py          # Pydantic data models
│   └── utils/                  # Utility functions
│       ├── ocr_utils.py        # OCR and PDF processing
│       ├── ui_detection.py     # UI element detection
│       └── model_client.py     # Multi-model AI client
├── config/
│   └── settings.py             # Configuration settings
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker configuration
└── README.md                   # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js (for Playwright)
- Java 8+ (for Appium)
- Android SDK (for mobile automation)
- Docker & Docker Compose (recommended)

### Environment Variables
Create a `.env` file in the root directory:

```bash
# AI Model API Keys
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key  
GOOGLE_API_KEY=your_google_key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEFAULT_MODEL=claude-sonnet

# Driver Settings
PLAYWRIGHT_HEADLESS=true
APPIUM_HOST=http://localhost:4723

# OCR Settings
TESSERACT_CMD=/usr/bin/tesseract

# Workflow Settings
WORKFLOW_TIMEOUT=600
RETRY_ATTEMPTS=3
```

### Quick Start with Docker

1. **Clone and setup**:
```bash
git clone <repository>
cd automation_framework
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start services**:
```bash
docker-compose up -d
```

4. **Access the API**:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- VNC (Android): http://localhost:6080

### Manual Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Install Playwright browsers**:
```bash
playwright install chromium
playwright install-deps
```

3. **Install Appium drivers**:
```bash
npm install -g appium
appium driver install uiautomator2
```

4. **Start Appium server**:
```bash
appium server --address 0.0.0.0 --port 4723
```

5. **Run the application**:
```bash
cd app
python main.py
```

## 🔧 Usage

### API Endpoints

#### Start Automation
```bash
curl -X POST "http://localhost:8000/automate" \
  -F "document=@instructions.pdf" \
  -F "screenshots=@screenshot1.png" \
  -F "screenshots=@screenshot2.png" \
  -F "parameters={\"timeout\": 600}" \
  -F "model=claude-sonnet"
```

#### Check Status
```bash
curl "http://localhost:8000/status/{task_id}"
```

### Python Client Example

```python
import requests
import json

# Upload files and start automation
files = {
    'document': open('instructions.pdf', 'rb'),
    'screenshots': [
        open('screen1.png', 'rb'),
        open('screen2.png', 'rb')
    ]
}

data = {
    'parameters': json.dumps({"timeout": 600}),
    'model': 'claude-sonnet'
}

response = requests.post('http://localhost:8000/automate', 
                        files=files, data=data)
task_id = response.json()['task_id']

# Check status
status_response = requests.get(f'http://localhost:8000/status/{task_id}')
print(status_response.json())
```

### Expected Input/Output

**Input**:
- PDF document with step-by-step instructions
- Screenshots showing the UI to automate
- Optional parameters (timeouts, retries, etc.)

**Output**:
```json
{
  "task_id": "uuid",
  "success": true,
  "platform": "mobile",
  "completion_percentage": 95,
  "steps_completed": 4,
  "total_steps": 5,
  "agents_processed": [
    {"name": "document_agent", "success": true},
    {"name": "code_agent", "success": true},
    {"name": "llm_supervisor", "success": true},
    {"name": "results_agent", "success": true}
  ],
  "execution_summary": {
    "success_factors": ["Script executed successfully"],
    "screenshots_captured": 8,
    "recommendation": "Workflow completed successfully"
  }
}
```

## 🧪 Testing

Run the example from the attached files:

1. Use `AI_Agent_Outlook_v1.1_20250702.pdf` as the document
2. Extract screenshots from the PDF  
3. Expected output should generate similar automation as `comp.py`

## 🔄 Development Workflow

1. **Modify agents** in `app/agents/`
2. **Update workflow** in `app/workflow/graph.py`
3. **Add new drivers** in `app/drivers/`
4. **Test changes** using the `/automate` endpoint
5. **Monitor logs** in console output

## 📊 Monitoring & Debugging

- **Logs**: Check console output for detailed agent execution logs
- **Screenshots**: Captured automatically during execution
- **State**: Full workflow state available via `/status/{task_id}`
- **Health**: Use `/health` endpoint for system status

## 🚀 Production Considerations

- Replace in-memory task storage with Redis
- Add authentication and rate limiting
- Implement proper logging with structured formats
- Use environment-specific configurations
- Add monitoring and alerting
- Scale agents independently using container orchestration

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the `/docs` endpoint for API documentation
- Review logs in console output
- Ensure all environment variables are set correctly
- Verify Appium/Playwright drivers are properly installedmm