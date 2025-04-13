"""
Configuration utilities for The Panel.

This module handles loading environment variables and configuring
the application settings.
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for The Panel application."""
    
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
        # Default to GPT-4o as the hosted model
        model_name = os.environ.get("MODEL_NAME", "gpt-4o")
        
        # Check if we're using a local model (Ollama)
        use_local = os.environ.get("USE_LOCAL_MODEL", "false").lower() == "true"
        
        if use_local:
            # Local model configuration
            return {
                "offline": True,
                "model": os.environ.get("LOCAL_MODEL_NAME", "ollama/llama3.1"),
                "api_base": os.environ.get("LOCAL_API_BASE", "http://localhost:11434"),
                "context_window": int(os.environ.get("LOCAL_CONTEXT_WINDOW", "4000")),
                "max_tokens": int(os.environ.get("LOCAL_MAX_TOKENS", "3000")),
                "auto_run": True,
                "verbose": os.environ.get("VERBOSE", "true").lower() == "true",
            }
        else:
            # Hosted model configuration
            return {
                "offline": False,
                "model": model_name,
                "context_window": int(os.environ.get("CONTEXT_WINDOW", "10000")),
                "max_tokens": int(os.environ.get("MAX_TOKENS", "4096")),
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