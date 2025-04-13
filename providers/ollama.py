"""
Ollama provider implementation for The Panel.
"""

import os
import requests
from typing import Dict, Any, List, Optional
import logging

from .base import BaseProvider

logger = logging.getLogger(__name__)

class OllamaProvider(BaseProvider):
    """Provider implementation for Ollama (local models)."""
    
    def __init__(self):
        """Initialize the Ollama provider."""
        self.api_base = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")
        self._models_cache = None
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available models from Ollama.
        
        Returns:
            A list of model dictionaries
        """
        if self._models_cache is not None:
            return self._models_cache
        
        # Default models in case the API call fails
        default_models = [
            {"id": "llama3", "name": "Llama 3", "family": "Llama"},
            {"id": "llama2", "name": "Llama 2", "family": "Llama"},
            {"id": "mistral", "name": "Mistral", "family": "Mistral"},
            {"id": "mixtral", "name": "Mixtral", "family": "Mistral"},
            {"id": "codellama", "name": "Code Llama", "family": "Llama"},
        ]
        
        try:
            # Try to get models from the Ollama API
            response = requests.get(f"{self.api_base}/api/tags")
            
            if response.status_code == 200:
                data = response.json()
                models = []
                
                for model in data.get("models", []):
                    model_id = model.get("name", "")
                    
                    # Determine family based on name
                    if "llama" in model_id.lower():
                        family = "Llama"
                    elif "mistral" in model_id.lower():
                        family = "Mistral"
                    elif "mixtral" in model_id.lower():
                        family = "Mistral"
                    elif "codellama" in model_id.lower():
                        family = "Llama"
                    elif "gemma" in model_id.lower():
                        family = "Gemma"
                    else:
                        family = "Other"
                    
                    # Create user-friendly name
                    name = model_id.replace("-", " ").title()
                    
                    models.append({
                        "id": model_id,
                        "name": name,
                        "family": family,
                        "details": model
                    })
                
                # Sort by family and then by name
                models.sort(key=lambda x: (x["family"], x["name"]))
                
                self._models_cache = models
                return models
            else:
                logger.warning(f"Failed to fetch Ollama models: {response.status_code} - {response.text}")
                return default_models
                
        except Exception as e:
            logger.error(f"Error fetching Ollama models: {str(e)}")
            return default_models
    
    def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific Ollama model.
        
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
                return model.get("details", {"name": model_id})
        
        raise ValueError(f"Model not found: {model_id}")
    
    def configure_interpreter(self, interpreter, config: Dict[str, Any]) -> None:
        """
        Configure the Open Interpreter instance for Ollama.
        
        Args:
            interpreter: The interpreter instance to configure
            config: Configuration options from the Config class
        """
        interpreter.offline = True
        interpreter.llm.model = config.get("model", "llama3")
        
        # Ensure the model has 'ollama/' prefix if not already present
        if not interpreter.llm.model.startswith('ollama/'):
            interpreter.llm.model = f"ollama/{interpreter.llm.model}"
            
        interpreter.llm.api_base = config.get("api_base", self.api_base)
        interpreter.llm.context_window = config.get("context_window", 4000)
        interpreter.llm.max_tokens = config.get("max_tokens", 3000)
        interpreter.auto_run = True
        interpreter.verbose = config.get("verbose", True)
    
    def get_default_tools(self) -> List[Dict[str, Any]]:
        """
        Get a list of default tools for Ollama.
        
        Returns:
            A list of tool definitions compatible with Ollama
        """
        return []  # Ollama doesn't support custom tools in the same way as OpenAI