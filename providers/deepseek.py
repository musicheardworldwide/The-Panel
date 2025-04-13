"""
Deepseek provider implementation for The Panel.
"""

import os
import requests
from typing import Dict, Any, List, Optional
import logging

from .base import BaseProvider

logger = logging.getLogger(__name__)

class DeepseekProvider(BaseProvider):
    """Provider implementation for Deepseek."""
    
    def __init__(self):
        """Initialize the Deepseek provider."""
        self.api_key = os.environ.get("DEEPSEEK_API_KEY", "sk-7fd014d945684bf5b00c27c092d8866c")
        self.api_base = os.environ.get("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        self._models_cache = None
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available models from Deepseek.
        
        Returns:
            A list of model dictionaries
        """
        if self._models_cache is not None:
            return self._models_cache
        
        # Default models that we know are available
        default_models = [
            {"id": "deepseek-chat", "name": "Deepseek Chat", "family": "Deepseek Chat"},
            {"id": "deepseek-coder", "name": "Deepseek Coder", "family": "Deepseek Coder"},
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
                
                models = []
                for model in data.get("data", []):
                    model_id = model.get("id", "")
                    
                    # Determine family
                    if "coder" in model_id.lower():
                        family = "Deepseek Coder"
                    else:
                        family = "Deepseek Chat"
                        
                    # Create user-friendly name
                    name = model_id.replace("deepseek-", "Deepseek ").title()
                    
                    models.append({
                        "id": model_id,
                        "name": name,
                        "family": family,
                        "details": model
                    })
                
                # If the API didn't return any models, use our defaults
                if not models:
                    models = default_models
                
                # Sort by family and then by name
                models.sort(key=lambda x: (x["family"], x["name"]))
                
                self._models_cache = models
                return models
            else:
                logger.warning(f"Failed to fetch Deepseek models: {response.status_code} - {response.text}")
                return default_models
                
        except Exception as e:
            logger.error(f"Error fetching Deepseek models: {str(e)}")
            return default_models
    
    def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific Deepseek model.
        
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
        Configure the Open Interpreter instance for Deepseek.
        
        Args:
            interpreter: The interpreter instance to configure
            config: Configuration options from the Config class
        """
        interpreter.offline = False
        interpreter.llm.model = config.get("model", "deepseek-chat")
        interpreter.llm.api_key = config.get("api_key", self.api_key)
        interpreter.llm.api_base = config.get("api_base", self.api_base)
        
        # Set context window and max tokens based on model
        model_id = interpreter.llm.model
        if "coder" in model_id.lower():
            # Coder models typically have larger context
            interpreter.llm.context_window = config.get("context_window", 16000)
            interpreter.llm.max_tokens = config.get("max_tokens", 8000)
        else:
            interpreter.llm.context_window = config.get("context_window", 8192)
            interpreter.llm.max_tokens = config.get("max_tokens", 4096)
        
        interpreter.auto_run = True
        interpreter.verbose = config.get("verbose", False)
    
    def get_default_tools(self) -> List[Dict[str, Any]]:
        """
        Get a list of default tools for Deepseek.
        
        Returns:
            A list of tool definitions compatible with Deepseek
        """
        return []  # No special tools for Deepseek at this time