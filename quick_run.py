#!/usr/bin/env python3
"""
Quick runner for GTM Opportunity Agent Demo
This script runs independently and shows the core functionality.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🎯 GTM Opportunity Agent - Quick Demo")
    print("=" * 50)
    
    # Get project root
    project_root = Path(__file__).parent
    
    # Check if virtual environment exists
    venv_path = project_root / "gtm_agent_env"
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("Please run: python3 -m venv gtm_agent_env")
        return 1
    
    # Get Python executable from virtual environment
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/Mac
        python_exe = venv_path / "bin" / "python3"
    
    if not python_exe.exists():
        print(f"❌ Python executable not found in virtual environment: {python_exe}")
        return 1
    
    print(f"📦 Using Python: {python_exe}")
    
    # Install missing package if needed
    print("🔧 Installing required packages...")
    try:
        subprocess.run([str(python_exe), "-m", "pip", "install", "pydantic-settings"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Could not install pydantic-settings: {e}")
    
    # Run the demo script
    demo_script = project_root / "scripts" / "demo.py"
    if not demo_script.exists():
        print(f"❌ Demo script not found: {demo_script}")
        return 1
    
    print("🚀 Running GTM Agent demo...")
    print("-" * 50)
    
    try:
        # Run the demo with the virtual environment Python
        result = subprocess.run([str(python_exe), str(demo_script)], 
                              cwd=str(project_root))
        return result.returncode
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 