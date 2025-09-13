#!/usr/bin/env python3
"""
AFAS Frontend - Streamlit Startup Script
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the Streamlit frontend server"""
    
    # Environment configuration
    port = int(os.getenv("STREAMLIT_PORT", 8501))
    
    # Path to the Streamlit app
    src_path = Path(__file__).parent / "src"
    app_path = src_path / "streamlit_app.py"
    
    print(f"""
🌱 AFAS Frontend (Streamlit) Starting...

Configuration:
- Port: {port}
- App Path: {app_path}
- Data Visualization: Plotly enabled
- Interactive Dashboard: Full-featured

Backend Services:
- Question Router: {os.getenv('QUESTION_ROUTER_URL', 'http://localhost:8000')}
- Recommendation Engine: {os.getenv('RECOMMENDATION_ENGINE_URL', 'http://localhost:8001')}
- User Management: {os.getenv('USER_MANAGEMENT_URL', 'http://localhost:8005')}

Access the application at: http://localhost:{port}
    """)
    
    # Streamlit command
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(app_path),
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    # Start Streamlit
    try:
        subprocess.run(cmd, cwd=src_path)
    except KeyboardInterrupt:
        print("\n🛑 Streamlit server stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()