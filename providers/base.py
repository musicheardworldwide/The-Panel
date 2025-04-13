"""
Base provider interface for The Panel.

This module defines the base interface that all providers must implement.
"""

import abc
from typing import Dict, Any, List, Optional

class BaseProvider(abc.ABC):
    """Base class for LLM providers."""
    
    @abc.abstractmethod
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available models for this provider.
        
        Returns:
            A list of model dictionaries with at least 'id' and 'name' keys
        """
        pass
    
    @abc.abstractmethod
    def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific model.
        
        Args:
            model_id: The ID of the model to retrieve details for
            
        Returns:
            A dictionary with model details
            
        Raises:
            ValueError: If the model is not found
        """
        pass
    
    @abc.abstractmethod
    def configure_interpreter(self, interpreter, config: Dict[str, Any]) -> None:
        """
        Configure the Open Interpreter instance for this provider.
        
        Args:
            interpreter: The interpreter instance to configure
            config: Configuration options from the Config class
        """
        pass
    
    @abc.abstractmethod
    def get_default_tools(self) -> List[Dict[str, Any]]:
        """
        Get a list of default tools for this provider.
        
        Returns:
            A list of tool definitions compatible with the provider
        """
        pass