# The Panel

A Flask-based server for Open Interpreter integration, providing an API to interact with various LLM models.

## Features

- Simple REST API to send prompts to LLM models via Open Interpreter
- Support for both local and hosted LLM models
- Streaming responses
- Configurable model parameters

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

## Configuration

The application can be configured to use either a local or hosted LLM model:

### Local Model Configuration

To use a local model like Ollama, uncomment and adjust the local model configuration in `app.py`:

```python
# Local Model
interpreter.offline = True
interpreter.llm.model = "ollama/llama3.1"
interpreter.llm.api_base = "http://localhost:11434"
interpreter.llm.context_window = 4000
interpreter.llm.max_tokens = 3000
interpreter.auto_run = True
interpreter.verbose = True
```

### Hosted Model Configuration

To use a hosted model like GPT-4o (default), use the following configuration:

```python
# Hosted Model
interpreter.llm.model = "gpt-4o"
interpreter.llm.context_window = 10000
interpreter.llm.max_tokens = 4096
interpreter.auto_run = True
```

## Usage

Start the server:

```bash
python app.py
```

The server will run on `http://0.0.0.0:5001`.

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

### Example with curl

```bash
curl -X POST http://localhost:5001/chat \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello, how are you?"}'
```

## Environment Variables

For security, API keys and other sensitive information should be stored in a `.env` file:

```
OPENAI_API_KEY=your-api-key-here
```

## Project Structure

```
The-Panel/
├── app.py               # Main application file
├── config.py            # Configuration utilities
├── .env                 # Environment variables (not tracked in git)
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.