"""
Music Heard Worldwide provider implementation for The Panel.
"""

import os
import requests
from typing import Dict, Any, List, Optional
import logging

from .base import BaseProvider

logger = logging.getLogger(__name__)

class MHWProvider(BaseProvider):
    """Provider implementation for Music Heard Worldwide."""
    
    def __init__(self):
        """Initialize the Music Heard Worldwide provider."""
        self.api_key = os.environ.get("MHW_API_KEY", "sk-a3180c218e4e45049c2e1345e6a3a09a")
        self.api_base = os.environ.get("MHW_API_BASE", "https://chat.musicheardworldwide.com/api")
        self._models_cache = None
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available models from Music Heard Worldwide.
        
        Returns:
            A list of model dictionaries
        """
        if self._models_cache is not None:
            return self._models_cache
        
        # Default models in case the API call fails
        default_models = [
            {"id": "default", "name": "MHW Default", "family": "MHW"},
            {"id": "mhw-1", "name": "MHW-1", "family": "MHW"},
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
                
                # Process the model data
                models = []
                for model in data.get("data", []):
                    model_id = model.get("id", "")
                    
                    # Create user-friendly name
                    name = model.get("name", model_id)
                    if not name:
                        name = model_id.replace("-", " ").title()
                    
                    # Get the model family if available
                    family = model.get("family", "MHW")
                    if not family:
                        family = "MHW"
                    
                    models.append({
                        "id": model_id,
                        "name": name,
                        "family": family,
                        "details": model
                    })
                
                # If we didn't get any models from the API, use the defaults
                if not models:
                    models = default_models
                
                # Sort by family and then by name
                models.sort(key=lambda x: (x["family"], x["name"]))
                
                self._models_cache = models
                return models
            else:
                logger.warning(f"Failed to fetch MHW models: {response.status_code} - {response.text}")
                return default_models
                
        except Exception as e:
            logger.error(f"Error fetching MHW models: {str(e)}")
            return default_models
    
    def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific Music Heard Worldwide model.
        
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
        Configure the Open Interpreter instance for MHW.
        
        Args:
            interpreter: The interpreter instance to configure
            config: Configuration options from the Config class
        """
        interpreter.offline = False
        interpreter.llm.model = config.get("model", "default")
        interpreter.llm.api_key = config.get("api_key", self.api_key)
        interpreter.llm.api_base = config.get("api_base", self.api_base)
        
        # Configure context window and max tokens
        interpreter.llm.context_window = config.get("context_window", 8192)
        interpreter.llm.max_tokens = config.get("max_tokens", 4096)
        
        # Enable auto run and configure verbosity
        interpreter.auto_run = True
        interpreter.verbose = config.get("verbose", False)
    
    def get_default_tools(self) -> List[Dict[str, Any]]:
        """
        Get a list of default tools for Music Heard Worldwide.
        
        Returns:
            A list of tool definitions compatible with MHW
        """
        return []  # No default tools specified for MHW at this time