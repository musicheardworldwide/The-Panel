#!/bin/bash
# Deployment script for The Panel

# Verify Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Verify pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is required but not installed. Please install pip and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install required packages
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists, if not create from example
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit the .env file with your API keys and configuration before starting the server."
fi

# Run health check
echo "Running server health check..."
python -c "from app import configure_interpreter; configure_interpreter(); print('Interpreter configuration successful!')"

if [ $? -eq 0 ]; then
    echo "Health check passed. Server configuration is valid."
    echo ""
    echo "To start the server, run: python app.py"
    echo "The server will be available at: http://localhost:5001"
    echo ""
    echo "For more information, see the README.md file."
else
    echo "Health check failed. Please check your configuration in .env"
fi

# Deactivate virtual environment
deactivate