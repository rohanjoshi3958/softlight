#!/bin/bash

# Setup script for Agent B

echo "Setting up Agent B..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "Warning: .env file not found!"
    echo "Please create a .env file with your OPENAI_API_KEY:"
    echo "  OPENAI_API_KEY=your_key_here"
    echo ""
    echo "You can copy .env.example to .env and edit it:"
    echo "  cp .env.example .env"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run Agent B, use:"
echo "  python main.py 'How do I create a project in Linear?'"
echo ""

