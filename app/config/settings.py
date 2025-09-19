"""
Configuration settings for the automation framework
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_TITLE: str = "Document Automation Framework"
    API_VERSION: str = "1.0.0"
    
    # Model Configuration
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "claude-sonnet")
    
    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Model Configurations
    MODELS: Dict[str, Dict[str, Any]] = {
        "claude-sonnet": {
            "model_name": "claude-3-5-sonnet-20241022",
            "api_key": ANTHROPIC_API_KEY,
            "max_tokens": 4096,
            "temperature": 0.3
        },
        "openai-gpt4": {
            "model_name": "gpt-4-1106-preview",
            "api_key": OPENAI_API_KEY,
            "max_tokens": 4096,
            "temperature": 0.3
        },
        "gemini-flash": {
            "model_name": "gemini-2.5-flash",
            "api_key": GOOGLE_API_KEY,
            "max_tokens": 4096,
            "temperature": 0.3
        }
    }
    
    # Driver Configuration
    PLAYWRIGHT_HEADLESS: bool = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
    PLAYWRIGHT_STEALTH: bool = os.getenv("PLAYWRIGHT_STEALTH", "true").lower() == "true"
    APPIUM_HOST: str = os.getenv("APPIUM_HOST", "http://localhost:4723")
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50")) * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: list = [".pdf", ".png", ".jpg", ".jpeg"]
    
    # OCR Configuration
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")
    
    # Workflow Configuration
    WORKFLOW_TIMEOUT: int = int(os.getenv("WORKFLOW_TIMEOUT", "600"))  # 10 minutes
    RETRY_ATTEMPTS: int = int(os.getenv("RETRY_ATTEMPTS", "3"))
    
    # Artifacts Configuration
    GENERATED_ROOT: str = os.getenv("GENERATED_ROOT", "generated_code")
    
    @classmethod
    def get_model_config(cls, model_name: str) -> Dict[str, Any]:
        """Get configuration for a specific model"""
        return cls.MODELS.get(model_name, cls.MODELS[cls.DEFAULT_MODEL])

# Global settings instance
settings = Settings()