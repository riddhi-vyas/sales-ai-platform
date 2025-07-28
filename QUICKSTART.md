# 🚀 GTM Opportunity Agent - Quick Start

## Option 1: Web Interface (Recommended for Demos) 🌐

```bash
# Make sure you're in the project directory
cd /home/riddhi/Downloads/GTM_project

# Run the web interface
python3 run_streamlit.py
```

**Then open your browser to: http://localhost:8501**

## Option 2: Terminal Demo

```bash
# Make sure you're in the project directory
cd /home/riddhi/Downloads/GTM_project

# Run the terminal demo
python3 quick_run.py
```

## Option 2: Manual Steps

```bash
# 1. Navigate to project directory
cd /home/riddhi/Downloads/GTM_project

# 2. Activate virtual environment
source gtm_agent_env/bin/activate

# 3. Verify activation (should show the venv path)
which python3

# 4. Install any missing packages
pip install pydantic-settings

# 5. Run the demo
python3 scripts/demo.py
```

## Troubleshooting

### If you get "ModuleNotFoundError"
```bash
# Make sure virtual environment is activated
source gtm_agent_env/bin/activate

# Install missing dependencies
pip install pydantic-settings

# Try again
python3 scripts/demo.py
```

### If virtual environment doesn't exist
```bash
# Create it again
python3 -m venv gtm_agent_env
source gtm_agent_env/bin/activate
pip install -r requirements.txt
pip install pydantic-settings
```

## Other Commands

```bash
# Show high-intent accounts (requires venv)
source gtm_agent_env/bin/activate
python3 -c "
import sys
sys.path.append('.')
from utils.data_loader import data_loader
accounts = data_loader.get_high_intent_accounts()
for acc in accounts:
    print(f'{acc[\"company_name\"]}: {acc[\"intent_score\"]}/100')
"

# Reset demo data
python3 -c "
import sys, json
sys.path.append('.')
from config.settings import settings
with open(settings.mock_data_path, 'r') as f:
    accounts = json.load(f)
for account in accounts:
    account['processed'] = False
with open(settings.mock_data_path, 'w') as f:
    json.dump(accounts, f, indent=2)
print('✅ Demo data reset')
"
```

## Expected Output

When working correctly, you should see:
- 🎯 Beautiful terminal interface
- 📊 Table of high-intent accounts  
- 🤖 AI analysis with opportunity brief
- 📝 Mock Slack integration
- 💰 Business impact summary

**Note**: The demo works in mock mode without requiring external APIs! 