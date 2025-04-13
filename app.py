"""
The Panel - A Flask-based server for Open Interpreter integration.

This module provides an API to interact with LLM models via Open Interpreter.
"""

from flask import Flask, request, jsonify, send_from_directory
from interpreter import interpreter
import json
import os
from typing import Dict, Any, Generator, Union
import logging
from config import Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static')

def configure_interpreter() -> None:
    """Configure Open Interpreter with settings from config."""
    config = Config.get_model_config()
    
    if config.get("offline", False):
        # Local Model
        interpreter.offline = True
        interpreter.llm.model = config.get("model", "ollama/llama3.1")
        interpreter.llm.api_base = config.get("api_base", "http://localhost:11434")
        interpreter.llm.context_window = config.get("context_window", 4000)
        interpreter.llm.max_tokens = config.get("max_tokens", 3000)
    else:
        # Hosted Model
        interpreter.offline = False
        interpreter.llm.model = config.get("model", "gpt-4o")
        interpreter.llm.context_window = config.get("context_window", 10000)
        interpreter.llm.max_tokens = config.get("max_tokens", 4096)
    
    interpreter.auto_run = True
    interpreter.verbose = config.get("verbose", False)
    
    logger.info(f"Configured Interpreter with model: {interpreter.llm.model}, offline: {interpreter.offline}")

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
        "offline": interpreter.offline
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
        "verbose": interpreter.verbose
    })

if __name__ == '__main__':
    # Get Flask configuration from config
    flask_config = Config.get_flask_config()
    
    # Start the Flask server
    app.run(
        host=flask_config.get("host", "0.0.0.0"),
        port=flask_config.get("port", 5001),
        debug=flask_config.get("debug", False)
    )
    
    logger.info(f"Open Interpreter server is running on http://{flask_config.get('host', '0.0.0.0')}:{flask_config.get('port', 5001)}")