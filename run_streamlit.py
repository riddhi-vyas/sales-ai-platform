#!/usr/bin/env python3
"""
Streamlit App Runner for GTM Opportunity Agent
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🎯 Starting GTM Opportunity Agent Web Interface")
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
    
    # Install required packages
    print("🔧 Installing/checking required packages...")
    required_packages = ["streamlit", "plotly", "pydantic-settings"]
    
    for package in required_packages:
        try:
            subprocess.run([str(python_exe), "-m", "pip", "install", package], 
                          check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Could not install {package}: {e}")
    
    print("✅ Dependencies ready")
    
    # Run Streamlit
    streamlit_app = project_root / "streamlit_app.py"
    if not streamlit_app.exists():
        print(f"❌ Streamlit app not found: {streamlit_app}")
        return 1
    
    print("🚀 Starting Streamlit web interface...")
    print("📱 Opening in your default browser...")
    print("🔗 URL: http://localhost:8501")
    print("-" * 50)
    
    try:
        # Run streamlit with the virtual environment Python
        result = subprocess.run([
            str(python_exe), "-m", "streamlit", "run", str(streamlit_app),
            "--server.port", "8501",
            "--server.address", "localhost"
        ], cwd=str(project_root))
        return result.returncode
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 