"""
OpenAI provider implementation for The Panel.
"""

import os
import requests
from typing import Dict, Any, List, Optional
import logging

from .base import BaseProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseProvider):
    """Provider implementation for OpenAI."""
    
    def __init__(self):
        """Initialize the OpenAI provider."""
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.api_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
        self._models_cache = None
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available models from OpenAI.
        
        Returns:
            A list of model dictionaries
        """
        if self._models_cache is not None:
            return self._models_cache
        
        # Core models we'll recommend even if the API call fails
        default_models = [
            {"id": "gpt-4o", "name": "GPT-4o", "family": "GPT-4"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "family": "GPT-4"},
            {"id": "gpt-4", "name": "GPT-4", "family": "GPT-4"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "family": "GPT-3.5"},
        ]
        
        try:
            # Try to get models from API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.api_base}/models",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Filter to only GPT models and organize them
                models = []
                for model in data.get("data", []):
                    model_id = model.get("id", "")
                    if "gpt" in model_id.lower():
                        # Determine family
                        if "gpt-4" in model_id:
                            family = "GPT-4"
                        elif "gpt-3.5" in model_id:
                            family = "GPT-3.5"
                        else:
                            family = "Other GPT"
                            
                        # Create user-friendly name
                        name = model_id.replace("gpt-", "GPT-")
                        
                        models.append({
                            "id": model_id,
                            "name": name,
                            "family": family,
                            "details": model
                        })
                
                # Sort by family and then by name
                models.sort(key=lambda x: (0 if x["family"] == "GPT-4" else 
                                          (1 if x["family"] == "GPT-3.5" else 2), 
                                          x["name"]))
                
                self._models_cache = models
                return models
            else:
                logger.warning(f"Failed to fetch OpenAI models: {response.status_code} - {response.text}")
                return default_models
                
        except Exception as e:
            logger.error(f"Error fetching OpenAI models: {str(e)}")
            return default_models
    
    def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific OpenAI model.
        
        Args:
            model_id: The ID of the model to retrieve details for
            
        Returns:
            A dictionary with model details
            
        Raises:
            ValueError: If the model is not found
        """
        models = self.list_models()
        
        for model in models:
            if model["id"] == model_id:
                return model.get("details", {"id": model_id})
        
        raise ValueError(f"Model not found: {model_id}")
    
    def configure_interpreter(self, interpreter, config: Dict[str, Any]) -> None:
        """
        Configure the Open Interpreter instance for OpenAI.
        
        Args:
            interpreter: The interpreter instance to configure
            config: Configuration options from the Config class
        """
        interpreter.offline = False
        interpreter.llm.model = config.get("model", "gpt-4o")
        interpreter.llm.api_key = config.get("api_key", self.api_key)
        
        # Set custom API base if specified
        custom_api_base = config.get("api_base")
        if custom_api_base and custom_api_base != self.api_base:
            interpreter.llm.api_base = custom_api_base
        
        interpreter.llm.context_window = config.get("context_window", 10000)
        interpreter.llm.max_tokens = config.get("max_tokens", 4096)
        interpreter.auto_run = True
        interpreter.verbose = config.get("verbose", False)
    
    def get_default_tools(self) -> List[Dict[str, Any]]:
        """
        Get a list of default tools for OpenAI.
        
        Returns:
            A list of tool definitions compatible with OpenAI
        """
        return []  # OpenAI models come with built-in tools