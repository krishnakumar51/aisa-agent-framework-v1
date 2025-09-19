"""
Multi-model AI client for handling different LLM providers
"""
import asyncio
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

import anthropic
import openai
import google.generativeai as genai

from app.config.settings import settings

class ModelClient(ABC):
    """Abstract base class for model clients"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from the model"""
        pass

class ClaudeClient(ModelClient):
    """Anthropic Claude client"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Claude"""
        try:
            message = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.3),
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

class OpenAIClient(ModelClient):
    """OpenAI GPT client"""
    
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.3)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

class GeminiClient(ModelClient):
    """Google Gemini client"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Gemini"""
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, 
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=kwargs.get("max_tokens", 4096),
                    temperature=kwargs.get("temperature", 0.3)
                )
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

class MultiModelClient:
    """Client that manages multiple AI models"""
    
    def __init__(self):
        self.clients: Dict[str, ModelClient] = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize all available model clients"""
        config = settings.MODELS
        
        # Initialize Claude
        if config["claude-sonnet"]["api_key"]:
            self.clients["claude-sonnet"] = ClaudeClient(
                config["claude-sonnet"]["api_key"]
            )
        
        # Initialize OpenAI
        if config["openai-gpt4"]["api_key"]:
            self.clients["openai-gpt4"] = OpenAIClient(
                config["openai-gpt4"]["api_key"]
            )
        
        # Initialize Gemini
        if config["gemini-flash"]["api_key"]:
            self.clients["gemini-flash"] = GeminiClient(
                config["gemini-flash"]["api_key"]
            )
    
    async def generate(self, prompt: str, model_name: Optional[str] = None, **kwargs) -> str:
        """Generate response using specified model or default"""
        if model_name is None:
            model_name = settings.DEFAULT_MODEL
        
        if model_name not in self.clients:
            available_models = list(self.clients.keys())
            if not available_models:
                raise Exception("No AI models configured")
            model_name = available_models[0]
        
        client = self.clients[model_name]
        return await client.generate(prompt, **kwargs)
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return list(self.clients.keys())
    
    async def generate_with_fallback(self, prompt: str, **kwargs) -> tuple[str, str]:
        """Generate with fallback to other models if primary fails"""
        models_to_try = [settings.DEFAULT_MODEL] + [
            model for model in self.clients.keys() 
            if model != settings.DEFAULT_MODEL
        ]
        
        last_error = None
        for model_name in models_to_try:
            if model_name in self.clients:
                try:
                    response = await self.generate(prompt, model_name, **kwargs)
                    return response, model_name
                except Exception as e:
                    last_error = e
                    continue
        
        raise Exception(f"All models failed. Last error: {str(last_error)}")

# Global multi-model client instance
model_client = MultiModelClient()