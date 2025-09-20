"""
Settings Configuration for Claude 4 Sonnet Automation System
Simple configuration management
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with Claude 4 Sonnet configuration"""
    
    # API Configuration
    api_title: str = "Generic Multi-Agent Automation System"
    api_version: str = "1.1.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug_mode: bool = False
    enable_cors: bool = True
    
    # Model Configuration - Updated for Claude 4 Sonnet
    default_model: str = "claude-sonnet-4-20250514"  # Claude 4 Sonnet production ID
    max_retries: int = 3
    workflow_timeout: int = 600  # 10 minutes
    
    # Directory Configuration
    generated_root: str = "generated_code"
    logs_directory: str = "logs"
    
    # Security Configuration
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # Performance Configuration
    enable_screenshots: bool = True
    log_level: str = "INFO"
    max_concurrent_tasks: int = 5
    
    # Feature Flags
    enable_websockets: bool = True
    enable_file_downloads: bool = True
    enable_task_persistence: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow" 
        # Override environment variable names
        fields = {
            "anthropic_api_key": {"env": "ANTHROPIC_API_KEY"},
            "openai_api_key": {"env": "OPENAI_API_KEY"}
        }

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
        
        # Validate critical settings
        if not _settings.anthropic_api_key and not os.getenv("ANTHROPIC_API_KEY"):
            print("⚠️ WARNING: ANTHROPIC_API_KEY not set. Claude 4 Sonnet will use fallback responses.")
            print("   Set your API key: export ANTHROPIC_API_KEY=sk-ant-xxxxx")
    
    return _settings