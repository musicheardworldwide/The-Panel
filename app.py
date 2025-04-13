"""
The Panel - A Flask-based server for Open Interpreter integration.

This module provides an API and web interface to interact with LLM models via Open Interpreter.
"""

from flask import Flask, request, jsonify, send_from_directory
from interpreter import interpreter
import json
import os
from typing import Dict, Any, Generator, Union, List
import logging
from config import Config
import providers
from tools import ToolManager, GitHubToolFinder

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static')

# Initialize tool manager
tool_manager = ToolManager()

def configure_interpreter() -> None:
    """Configure Open Interpreter with settings from config."""
    config = Config.get_model_config()
    provider_id = config.get("provider", "openai")
    
    try:
        # Get the appropriate provider
        provider_instance = providers.get_provider(provider_id)
        
        # Use the provider to configure the interpreter
        provider_instance.configure_interpreter(interpreter, config)
        
        logger.info(f"Configured Interpreter with provider: {provider_id}, model: {interpreter.llm.model}")
        
    except Exception as e:
        logger.error(f"Error configuring interpreter: {str(e)}")
        # Fall back to OpenAI if there's an error
        if provider_id != "openai":
            logger.info("Falling back to OpenAI provider")
            providers.get_provider("openai").configure_interpreter(
                interpreter, Config._get_openai_config())

# Configure interpreter on startup
configure_interpreter()

@app.route('/')
def index():
    """Serve the main application page."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/chat', methods=['POST'])
def chat() -> Dict[str, Any]:
    """
    Chat endpoint to interact with the LLM model.
    
    Returns:
        JSON response with the model's answer or error message
    """
    # Get JSON data from request
    data = request.json
    prompt = data.get('prompt')
    
    if not prompt:
        logger.warning("Request received with no prompt")
        return jsonify({"error": "No prompt provided"}), 400

    full_response = ""
    try:
        logger.info(f"Processing prompt: {prompt[:50]}...")
        chunks = process_interpreter_response(interpreter.chat(prompt, stream=True, display=False))
        full_response = "".join(chunks)
    except Exception as e:
        logger.error(f"Error processing prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"response": full_response.strip()})

def process_interpreter_response(response: Generator) -> Generator[str, None, None]:
    """
    Process and yield chunks from the interpreter's streaming response.
    
    Args:
        response: The generator from interpreter.chat()
        
    Yields:
        Text chunks from the response
    """
    for chunk in response:
        if isinstance(chunk, dict):
            if chunk.get("type") == "message":
                yield chunk.get("content", "")
        elif isinstance(chunk, str):
            # Attempt to parse the string as JSON
            try:
                json_chunk = json.loads(chunk)
                yield json_chunk.get("response", "")
            except json.JSONDecodeError:
                # If it's not valid JSON, just yield the string
                yield chunk

@app.route('/health', methods=['GET'])
def health_check() -> Dict[str, Union[str, bool]]:
    """
    Health check endpoint to verify the server is running.
    
    Returns:
        JSON response with status information
    """
    return jsonify({
        "status": "healthy",
        "model": interpreter.llm.model,
        "offline": interpreter.offline,
        "provider": Config.get_model_config().get("provider", "openai")
    })

@app.route('/config', methods=['GET'])
def get_config() -> Dict[str, Any]:
    """
    Get the current interpreter configuration.
    
    Returns:
        JSON response with the current configuration
    """
    return jsonify({
        "model": interpreter.llm.model,
        "offline": interpreter.offline,
        "context_window": interpreter.llm.context_window,
        "max_tokens": interpreter.llm.max_tokens,
        "auto_run": interpreter.auto_run,
        "verbose": interpreter.verbose,
        "provider": Config.get_model_config().get("provider", "openai")
    })

@app.route('/providers', methods=['GET'])
def list_providers() -> Dict[str, List[Dict[str, str]]]:
    """
    Get a list of available providers.
    
    Returns:
        JSON response with provider information
    """
    return jsonify({
        "providers": Config.get_providers()
    })

@app.route('/models', methods=['GET'])
def list_models() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get a list of available models for the current or specified provider.
    
    Returns:
        JSON response with model information
    """
    provider_id = request.args.get('provider', 
                                 Config.get_model_config().get("provider", "openai"))
    
    try:
        provider_instance = providers.get_provider(provider_id)
        models = provider_instance.list_models()
        return jsonify({"models": models})
    except Exception as e:
        logger.error(f"Error listing models for provider {provider_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/tools', methods=['GET'])
def list_tools() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get a list of available tools.
    
    Returns:
        JSON response with tool information
    """
    return jsonify({
        "tools": tool_manager.get_tool_functions(),
        "mcp_servers": tool_manager.get_mcp_server_info()
    })

@app.route('/tools/search', methods=['GET'])
def search_tools() -> Dict[str, List[Dict[str, Any]]]:
    """
    Search for tools on GitHub.
    
    Returns:
        JSON response with search results
    """
    query = request.args.get('query', '')
    tool_type = request.args.get('type', None)
    
    tool_types = [tool_type] if tool_type else None
    
    github_finder = GitHubToolFinder()
    results = github_finder.search_repositories(query, tool_types)
    
    return jsonify({
        "results": results
    })

@app.route('/tools/add', methods=['POST'])
def add_tool() -> Dict[str, Any]:
    """
    Add a tool from GitHub.
    
    Returns:
        JSON response with the result of the operation
    """
    data = request.json
    repo_url = data.get('repo_url')
    
    if not repo_url:
        return jsonify({"error": "No repository URL provided"}), 400
    
    try:
        tool_info = tool_manager.add_tool_from_github(repo_url)
        return jsonify({
            "success": True,
            "tool": {
                "name": tool_info["name"],
                "description": tool_info["description"],
                "version": tool_info["version"],
                "functions": list(tool_info["functions"].keys())
            }
        })
    except Exception as e:
        logger.error(f"Error adding tool from {repo_url}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/update_provider', methods=['POST'])
def update_provider() -> Dict[str, Any]:
    """
    Update the active provider and model.
    
    Returns:
        JSON response with the result of the operation
    """
    data = request.json
    provider_id = data.get('provider')
    model_id = data.get('model')
    
    if not provider_id:
        return jsonify({"error": "No provider specified"}), 400
    
    try:
        # Update environment variables
        os.environ["PROVIDER"] = provider_id
        
        if model_id:
            if provider_id == Config.PROVIDER_OPENAI:
                os.environ["OPENAI_MODEL"] = model_id
            elif provider_id == Config.PROVIDER_OLLAMA:
                os.environ["OLLAMA_MODEL"] = model_id
            elif provider_id == Config.PROVIDER_DEEPSEEK:
                os.environ["DEEPSEEK_MODEL"] = model_id
            elif provider_id == Config.PROVIDER_MHW:
                os.environ["MHW_MODEL"] = model_id
        
        # Reconfigure the interpreter
        configure_interpreter()
        
        return jsonify({
            "success": True,
            "config": {
                "provider": provider_id,
                "model": interpreter.llm.model
            }
        })
    except Exception as e:
        logger.error(f"Error updating provider to {provider_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Get Flask configuration from config
    flask_config = Config.get_flask_config()
    
    # Start the Flask server
    app.run(
        host=flask_config.get("host", "0.0.0.0"),
        port=flask_config.get("port", 5001),
        debug=flask_config.get("debug", False)
    )
    
    logger.info(f"Open Interpreter server is running on http://{flask_config.get('host', '0.0.0.0')}:{flask_config.get('port', 5001')}")