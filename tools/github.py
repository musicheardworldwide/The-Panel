"""
GitHub tool finder for The Panel.

This module provides functionality to search and discover tools on GitHub
for use with Open Interpreter.
"""

import os
import requests
import logging
import re
import json
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class GitHubToolFinder:
    """
    Find and discover tools on GitHub for use with Open Interpreter.
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize the GitHub tool finder.
        
        Args:
            github_token: Optional GitHub personal access token for API access
        """
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN", "")
        self.api_base = "https://api.github.com"
        
    def search_repositories(self, query: str, tool_types: Optional[List[str]] = None, 
                           max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for repositories that might contain tools.
        
        Args:
            query: Search query
            tool_types: Optional list of tool types to filter by (e.g., ["mcp", "interpreter"])
            max_results: Maximum number of results to return
            
        Returns:
            List of repository information dictionaries
        """
        # Build the search query
        search_terms = [query]
        
        # Add language filter for Python
        search_terms.append("language:python")
        
        # Add tool type filters
        if tool_types:
            for tool_type in tool_types:
                search_terms.append(f"topic:{tool_type}")
        
        # Construct the full query
        full_query = "+".join(search_terms)
        
        # Set up the API request
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        # Make the request
        try:
            response = requests.get(
                f"{self.api_base}/search/repositories",
                params={"q": full_query, "sort": "stars", "order": "desc", "per_page": max_results},
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"GitHub API error: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            results = []
            
            for repo in data.get("items", []):
                # Extract relevant information
                repo_info = {
                    "name": repo.get("name", ""),
                    "full_name": repo.get("full_name", ""),
                    "description": repo.get("description", ""),
                    "url": repo.get("html_url", ""),
                    "clone_url": repo.get("clone_url", ""),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "updated_at": repo.get("updated_at", ""),
                    "topics": repo.get("topics", [])
                }
                
                # Check for tool-related files
                repo_info["has_manifest"] = self._check_for_file(repo["full_name"], "tool-manifest.json")
                
                results.append(repo_info)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching GitHub repositories: {str(e)}")
            return []
    
    def search_mcp_servers(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search specifically for MCP server repositories.
        
        Args:
            max_results: Maximum number of results to return
            
        Returns:
            List of repository information dictionaries
        """
        return self.search_repositories("mcp server", tool_types=["mcp", "server"], max_results=max_results)
    
    def get_tool_manifest(self, repo_full_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the tool manifest for a repository if it exists.
        
        Args:
            repo_full_name: Full name of the repository (e.g., "username/repo")
            
        Returns:
            Tool manifest dictionary or None if not found
        """
        # Set up the API request
        headers = {"Accept": "application/vnd.github.v3.raw"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        # Try to get the manifest file
        try:
            manifest_path = "tool-manifest.json"
            response = requests.get(
                f"{self.api_base}/repos/{repo_full_name}/contents/{manifest_path}",
                headers=headers
            )
            
            if response.status_code == 200:
                try:
                    return json.loads(response.text)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in tool manifest for {repo_full_name}")
                    return None
            else:
                logger.warning(f"No tool manifest found for {repo_full_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching tool manifest for {repo_full_name}: {str(e)}")
            return None
    
    def _check_for_file(self, repo_full_name: str, file_path: str) -> bool:
        """
        Check if a file exists in a repository.
        
        Args:
            repo_full_name: Full name of the repository (e.g., "username/repo")
            file_path: Path to the file to check for
            
        Returns:
            True if the file exists, False otherwise
        """
        # Set up the API request
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        # Make the request
        try:
            response = requests.get(
                f"{self.api_base}/repos/{repo_full_name}/contents/{file_path}",
                headers=headers
            )
            
            return response.status_code == 200
                
        except Exception:
            return False