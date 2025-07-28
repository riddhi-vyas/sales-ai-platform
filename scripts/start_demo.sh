#!/bin/bash

# GTM Opportunity Agent - Quick Start Demo Script

set -e

echo "🎯 Starting GTM Opportunity Agent Demo Setup"
echo "=========================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if Temporal server is running
echo "🔍 Checking Temporal server..."
if ! curl -s http://localhost:8233 > /dev/null 2>&1; then
    echo "⚠️  Temporal server not detected on localhost:8233"
    echo "🚀 Starting Temporal development server..."
    
    # Check if temporal CLI is available
    if command -v temporal &> /dev/null; then
        temporal server start-dev &
        echo "⏳ Waiting for Temporal server to start..."
        sleep 10
    else
        echo "❌ Temporal CLI not found. Please install it:"
        echo "   See: https://docs.temporal.io/cli#installation"
        echo "   Or run: curl -sSf https://temporal.download/cli.sh | sh"
        exit 1
    fi
else
    echo "✅ Temporal server is running"
fi

# Copy environment template if .env doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys for full functionality"
fi

# Show current configuration
echo ""
echo "📊 Current Configuration:"
python3 main.py show-accounts

echo ""
echo "🎉 Setup Complete! You can now:"
echo ""
echo "1. 🚀 Run the full agent:"
echo "   python3 main.py run"
echo ""
echo "2. 🧪 Test Slack integration:"
echo "   python3 main.py test-slack"
echo ""
echo "3. 👀 View high-intent accounts:"
echo "   python3 main.py show-accounts"
echo ""
echo "4. 🔄 Reset demo data:"
echo "   python3 main.py reset-data"
echo ""
echo "For production use, configure your API keys in the .env file:"
echo "- ANTHROPIC_API_KEY (for Claude LLM)"
echo "- ARCADE_API_KEY (for Slack integration)"
echo "- DD_API_KEY (for Datadog monitoring)"
echo "" 