# The Panel

A Flask-based server for Open Interpreter integration, providing an API and web interface to interact with various LLM models.

![The Panel Screenshot](https://via.placeholder.com/800x450.png?text=The+Panel+Web+Interface)

## Features

- Simple REST API to send prompts to LLM models via Open Interpreter
- Web-based chat interface for easy interaction
- Support for both local and hosted LLM models
- Streaming responses
- Configurable model parameters
- Chat history persistence
- Markdown and code syntax highlighting support

## Installation

Clone the repository:

```bash
git clone https://github.com/musicheardworldwide/The-Panel.git
cd The-Panel
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or use the deployment script:

```bash
chmod +x deploy.sh
./deploy.sh
```

## Configuration

The application can be configured to use either a local or hosted LLM model using environment variables. Copy the `.env.example` file to `.env` and customize the settings:

```bash
cp .env.example .env
```

### Local Model Configuration

To use a local model like Ollama, set the following in your `.env` file:

```
USE_LOCAL_MODEL=true
LOCAL_MODEL_NAME=ollama/llama3.1
LOCAL_API_BASE=http://localhost:11434
LOCAL_CONTEXT_WINDOW=4000
LOCAL_MAX_TOKENS=3000
VERBOSE=true
```

### Hosted Model Configuration

To use a hosted model like GPT-4o (default), use the following configuration:

```
USE_LOCAL_MODEL=false
MODEL_NAME=gpt-4o
CONTEXT_WINDOW=10000
MAX_TOKENS=4096
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

Start the server:

```bash
python app.py
```

The server will run on `http://0.0.0.0:5001`.

### Web Interface

Access the web interface by opening a browser and navigating to:
- `http://localhost:5001`

### API Endpoints

#### `/chat` (POST)

Send a prompt to the LLM model.

**Request:**

```json
{
  "prompt": "Your message or question"
}
```

**Response:**

```json
{
  "response": "The model's response"
}
```

#### `/health` (GET)

Check the server health and model configuration.

**Response:**

```json
{
  "status": "healthy",
  "model": "gpt-4o",
  "offline": false
}
```

#### `/config` (GET)

Get the current model configuration.

**Response:**

```json
{
  "model": "gpt-4o",
  "offline": false,
  "context_window": 10000,
  "max_tokens": 4096,
  "auto_run": true,
  "verbose": false
}
```

### Example with curl

```bash
curl -X POST http://localhost:5001/chat \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello, how are you?"}'
```

## Project Structure

```
The-Panel/
├── app.py                # Main application file
├── config.py             # Configuration utilities
├── .env                  # Environment variables (not tracked in git)
├── .env.example          # Example environment file
├── deploy.sh             # Deployment script
├── requirements.txt      # Project dependencies
├── static/               # Web UI static files
│   ├── index.html        # Main HTML page
│   ├── css/              # CSS styles
│   ├── js/               # JavaScript files
│   └── favicon.ico       # Favicon
├── tests/                # Test scripts
│   └── test_server.py    # Server test utility
└── README.md             # Project documentation
```

## Testing

The repository includes a simple test script to verify the server is working correctly:

```bash
python -m tests.test_server --url http://localhost:5001 --prompt "Hello, how are you?"
```

To only check server health:

```bash
python -m tests.test_server --url http://localhost:5001 --health-only
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.