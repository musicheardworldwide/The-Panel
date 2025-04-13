"""Providers package for The Panel."""

from .base import BaseProvider
from .openai import OpenAIProvider
from .ollama import OllamaProvider
from .deepseek import DeepseekProvider
from .mhw import MHWProvider

__all__ = [
    'BaseProvider',
    'OpenAIProvider',
    'OllamaProvider',
    'DeepseekProvider',
    'MHWProvider',
    'get_provider'
]

def get_provider(provider_id: str) -> BaseProvider:
    """
    Get a provider instance by ID.
    
    Args:
        provider_id: The provider ID (e.g., 'openai', 'ollama', 'deepseek', 'mhw')
        
    Returns:
        An instance of the appropriate provider class
        
    Raises:
        ValueError: If the provider ID is not recognized
    """
    from config import Config
    
    if provider_id == Config.PROVIDER_OPENAI:
        return OpenAIProvider()
    elif provider_id == Config.PROVIDER_OLLAMA:
        return OllamaProvider()
    elif provider_id == Config.PROVIDER_DEEPSEEK:
        return DeepseekProvider()
    elif provider_id == Config.PROVIDER_MHW:
        return MHWProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_id}")