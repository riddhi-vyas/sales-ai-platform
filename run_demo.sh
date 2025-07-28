#!/bin/bash

# GTM Opportunity Agent - Demo Runner
echo "🎯 Starting GTM Opportunity Agent Demo"
echo "======================================"

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "gtm_agent_env" ]; then
    echo "📦 Activating virtual environment..."
    source gtm_agent_env/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Install missing package if needed
echo "🔧 Checking dependencies..."
python3 -c "import pydantic_settings" 2>/dev/null || pip install pydantic-settings

# Run the demo
echo "🚀 Running GTM Agent demo..."
python3 scripts/demo.py 