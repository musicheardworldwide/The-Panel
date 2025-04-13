"""
Configuration utilities for The Panel.

This module handles loading environment variables and configuring
the application settings.
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for The Panel application."""
    
    # Provider constants
    PROVIDER_OPENAI = "openai"
    PROVIDER_OLLAMA = "ollama"
    PROVIDER_DEEPSEEK = "deepseek"
    PROVIDER_MHW = "mhw"  # Music Heard Worldwide
    
    @staticmethod
    def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get an environment variable value.
        
        Args:
            key: The environment variable key
            default: Default value if the environment variable is not found
            
        Returns:
            The environment variable value or the default value
        """
        return os.environ.get(key, default)
    
    @staticmethod
    def get_model_config() -> Dict[str, Any]:
        """
        Get model configuration from environment variables.
        
        Returns:
            A dictionary with model configuration parameters
        """
        # Get the selected provider
        provider = os.environ.get("PROVIDER", "openai").lower()
        
        # Check if we're using a local model (Ollama)
        if provider == Config.PROVIDER_OLLAMA:
            return Config._get_ollama_config()
        elif provider == Config.PROVIDER_DEEPSEEK:
            return Config._get_deepseek_config()
        elif provider == Config.PROVIDER_MHW:
            return Config._get_mhw_config()
        else:
            # Default to OpenAI
            return Config._get_openai_config()
    
    @staticmethod
    def _get_openai_config() -> Dict[str, Any]:
        """Get OpenAI configuration"""
        return {
            "provider": Config.PROVIDER_OPENAI,
            "offline": False,
            "model": os.environ.get("OPENAI_MODEL", "gpt-4o"),
            "api_key": os.environ.get("OPENAI_API_KEY", ""),
            "context_window": int(os.environ.get("CONTEXT_WINDOW", "10000")),
            "max_tokens": int(os.environ.get("MAX_TOKENS", "4096")),
            "auto_run": True,
            "verbose": os.environ.get("VERBOSE", "false").lower() == "true",
        }
    
    @staticmethod
    def _get_ollama_config() -> Dict[str, Any]:
        """Get Ollama configuration"""
        return {
            "provider": Config.PROVIDER_OLLAMA,
            "offline": True,
            "model": os.environ.get("OLLAMA_MODEL", "llama3.1"),
            "api_base": os.environ.get("OLLAMA_API_BASE", "http://localhost:11434"),
            "context_window": int(os.environ.get("OLLAMA_CONTEXT_WINDOW", "4000")),
            "max_tokens": int(os.environ.get("OLLAMA_MAX_TOKENS", "3000")),
            "auto_run": True,
            "verbose": os.environ.get("VERBOSE", "true").lower() == "true",
        }
    
    @staticmethod
    def _get_deepseek_config() -> Dict[str, Any]:
        """Get Deepseek configuration"""
        return {
            "provider": Config.PROVIDER_DEEPSEEK,
            "offline": False,
            "model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
            "api_key": os.environ.get("DEEPSEEK_API_KEY", "sk-7fd014d945684bf5b00c27c092d8866c"),
            "api_base": os.environ.get("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
            "context_window": int(os.environ.get("DEEPSEEK_CONTEXT_WINDOW", "8192")),
            "max_tokens": int(os.environ.get("DEEPSEEK_MAX_TOKENS", "4096")),
            "auto_run": True,
            "verbose": os.environ.get("VERBOSE", "false").lower() == "true",
        }
    
    @staticmethod
    def _get_mhw_config() -> Dict[str, Any]:
        """Get Music Heard Worldwide configuration"""
        return {
            "provider": Config.PROVIDER_MHW,
            "offline": False,
            "model": os.environ.get("MHW_MODEL", "default"),
            "api_key": os.environ.get("MHW_API_KEY", "sk-a3180c218e4e45049c2e1345e6a3a09a"),
            "api_base": os.environ.get("MHW_API_BASE", "https://chat.musicheardworldwide.com/api"),
            "context_window": int(os.environ.get("MHW_CONTEXT_WINDOW", "8192")),
            "max_tokens": int(os.environ.get("MHW_MAX_TOKENS", "4096")),
            "auto_run": True,
            "verbose": os.environ.get("VERBOSE", "false").lower() == "true",
        }
    
    @staticmethod
    def get_flask_config() -> Dict[str, Any]:
        """
        Get Flask application configuration.
        
        Returns:
            A dictionary with Flask configuration parameters
        """
        return {
            "debug": os.environ.get("FLASK_DEBUG", "false").lower() == "true",
            "host": os.environ.get("FLASK_HOST", "0.0.0.0"),
            "port": int(os.environ.get("FLASK_PORT", "5001")),
        }
    
    @staticmethod
    def get_providers() -> List[Dict[str, str]]:
        """
        Get list of available providers.
        
        Returns:
            A list of provider dictionaries with id and name
        """
        return [
            {"id": Config.PROVIDER_OPENAI, "name": "OpenAI"},
            {"id": Config.PROVIDER_OLLAMA, "name": "Ollama (Local)"},
            {"id": Config.PROVIDER_DEEPSEEK, "name": "Deepseek"},
            {"id": Config.PROVIDER_MHW, "name": "Music Heard Worldwide"},
        ]