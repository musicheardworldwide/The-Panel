"""
Tool manager for The Panel.

This module provides functionality to dynamically load, configure, and manage
tools for use with Open Interpreter.
"""

import os
import sys
import importlib
import importlib.util
import json
import logging
import tempfile
import shutil
from typing import Dict, Any, List, Optional, Callable
import subprocess
import uuid

logger = logging.getLogger(__name__)

class ToolManager:
    """
    Manager for loading, configuring, and running tools for Open Interpreter.
    """
    
    def __init__(self, tools_dir: Optional[str] = None):
        """
        Initialize the tool manager.
        
        Args:
            tools_dir: Optional directory to store downloaded tools
        """
        # Set up tools directory
        if tools_dir is None:
            self.tools_dir = os.path.join(os.path.expanduser("~"), ".the_panel", "tools")
        else:
            self.tools_dir = tools_dir
            
        # Create directory if it doesn't exist
        os.makedirs(self.tools_dir, exist_ok=True)
        
        # Keep track of loaded tools
        self.loaded_tools: Dict[str, Dict[str, Any]] = {}
        
        # MCP server modules
        self.mcp_servers: Dict[str, Any] = {}
        
    def add_tool_from_path(self, path: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a tool from a local path.
        
        Args:
            path: Path to the tool directory or file
            name: Optional name for the tool (defaults to directory/file name)
            
        Returns:
            Tool information dictionary
            
        Raises:
            ValueError: If the tool cannot be loaded
        """
        if name is None:
            name = os.path.basename(path)
            
        # Determine if it's a directory or file
        if os.path.isdir(path):
            # Check for __init__.py or main module
            init_path = os.path.join(path, "__init__.py")
            main_path = os.path.join(path, "main.py")
            tool_path = init_path if os.path.exists(init_path) else main_path
            
            if not os.path.exists(tool_path):
                raise ValueError(f"Could not find __init__.py or main.py in {path}")
                
            module_name = name
        elif os.path.isfile(path) and path.endswith(".py"):
            tool_path = path
            module_name = os.path.splitext(os.path.basename(path))[0]
        else:
            raise ValueError(f"Path must be a Python file or directory containing Python files: {path}")
        
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, tool_path)
            if spec is None or spec.loader is None:
                raise ValueError(f"Could not load module from {tool_path}")
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Extract tool info
            tool_info = {
                "name": getattr(module, "NAME", name),
                "description": getattr(module, "DESCRIPTION", ""),
                "version": getattr(module, "VERSION", "0.1.0"),
                "module": module,
                "path": path,
                "functions": {}
            }
            
            # Find tool functions
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr) and hasattr(attr, "__tool_metadata__"):
                    metadata = getattr(attr, "__tool_metadata__")
                    tool_info["functions"][attr_name] = {
                        "function": attr,
                        "metadata": metadata
                    }
            
            # Store the loaded tool
            self.loaded_tools[name] = tool_info
            logger.info(f"Added tool: {name} from {path}")
            
            return tool_info
            
        except Exception as e:
            logger.error(f"Error loading tool from {path}: {str(e)}")
            raise ValueError(f"Failed to load tool: {str(e)}")
    
    def add_tool_from_github(self, repo_url: str, branch: str = "main") -> Dict[str, Any]:
        """
        Add a tool by cloning a GitHub repository.
        
        Args:
            repo_url: GitHub repository URL
            branch: Branch to clone (default: main)
            
        Returns:
            Tool information dictionary
            
        Raises:
            ValueError: If the repository cannot be cloned or the tool cannot be loaded
        """
        # Extract the repo name from the URL
        repo_name = repo_url.split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
            
        # Create a unique directory for this repo
        tool_dir = os.path.join(self.tools_dir, f"{repo_name}_{uuid.uuid4().hex[:8]}")
        
        try:
            # Clone the repository
            logger.info(f"Cloning {repo_url} to {tool_dir}...")
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", branch, repo_url, tool_dir],
                check=True,
                capture_output=True,
                text=True
            )
            
            # Load the tool
            return self.add_tool_from_path(tool_dir, repo_name)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error cloning repository {repo_url}: {e.stderr}")
            if os.path.exists(tool_dir):
                shutil.rmtree(tool_dir)
            raise ValueError(f"Failed to clone repository: {e.stderr}")
            
        except Exception as e:
            logger.error(f"Error adding tool from GitHub {repo_url}: {str(e)}")
            if os.path.exists(tool_dir):
                shutil.rmtree(tool_dir)
            raise ValueError(f"Failed to add tool from GitHub: {str(e)}")
    
    def get_tool_functions(self) -> List[Dict[str, Any]]:
        """
        Get a list of all tool functions in a format compatible with Open Interpreter.
        
        Returns:
            List of tool function schemas
        """
        functions = []
        
        for tool_name, tool_info in self.loaded_tools.items():
            for func_name, func_info in tool_info["functions"].items():
                metadata = func_info["metadata"]
                
                # Convert to Open Interpreter function schema
                function_schema = {
                    "name": f"{tool_name}_{func_name}",
                    "description": metadata.get("description", ""),
                    "parameters": metadata.get("parameters", {"type": "object", "properties": {}, "required": []}),
                }
                
                functions.append(function_schema)
        
        return functions
    
    def register_mcp_server(self, name: str, server_module: Any) -> None:
        """
        Register an MCP server module.
        
        Args:
            name: Name of the server
            server_module: Module with server implementation
        """
        self.mcp_servers[name] = server_module
        logger.info(f"Registered MCP server: {name}")
        
        # Try to start the server if it has a start method
        if hasattr(server_module, "start") and callable(server_module.start):
            try:
                server_module.start()
                logger.info(f"Started MCP server: {name}")
            except Exception as e:
                logger.error(f"Error starting MCP server {name}: {str(e)}")
    
    def start_all_mcp_servers(self) -> None:
        """Start all registered MCP servers."""
        for name, server in self.mcp_servers.items():
            if hasattr(server, "start") and callable(server.start):
                try:
                    server.start()
                    logger.info(f"Started MCP server: {name}")
                except Exception as e:
                    logger.error(f"Error starting MCP server {name}: {str(e)}")
    
    def stop_all_mcp_servers(self) -> None:
        """Stop all registered MCP servers."""
        for name, server in self.mcp_servers.items():
            if hasattr(server, "stop") and callable(server.stop):
                try:
                    server.stop()
                    logger.info(f"Stopped MCP server: {name}")
                except Exception as e:
                    logger.error(f"Error stopping MCP server {name}: {str(e)}")
    
    def get_mcp_server_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered MCP servers.
        
        Returns:
            List of server information dictionaries
        """
        info = []
        
        for name, server in self.mcp_servers.items():
            server_info = {
                "name": name,
                "status": "unknown",
                "description": getattr(server, "DESCRIPTION", ""),
                "version": getattr(server, "VERSION", "0.1.0"),
                "endpoints": []
            }
            
            # Get status if available
            if hasattr(server, "get_status") and callable(server.get_status):
                try:
                    server_info["status"] = server.get_status()
                except Exception:
                    server_info["status"] = "error"
            
            # Get endpoints if available
            if hasattr(server, "get_endpoints") and callable(server.get_endpoints):
                try:
                    server_info["endpoints"] = server.get_endpoints()
                except Exception as e:
                    logger.error(f"Error getting endpoints for server {name}: {str(e)}")
                    server_info["endpoints"] = []
            
            info.append(server_info)
        
        return info