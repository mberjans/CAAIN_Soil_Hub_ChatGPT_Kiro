#!/usr/bin/env python3
"""
AFAS Frontend - FastAPI + Jinja2 Startup Script
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Start the FastAPI frontend server"""
    
    # Environment configuration
    host = os.getenv("FRONTEND_HOST", "0.0.0.0")
    port = int(os.getenv("FRONTEND_PORT", 3000))
    reload = os.getenv("FRONTEND_RELOAD", "true").lower() == "true"
    
    print(f"""
🌱 AFAS Frontend (FastAPI + Jinja2) Starting...

Configuration:
- Host: {host}
- Port: {port}
- Reload: {reload}
- Templates: {src_path / 'templates'}
- Static Files: {src_path / 'static'}

Backend Services:
- Question Router: {os.getenv('QUESTION_ROUTER_URL', 'http://localhost:8000')}
- Recommendation Engine: {os.getenv('RECOMMENDATION_ENGINE_URL', 'http://localhost:8001')}
- User Management: {os.getenv('USER_MANAGEMENT_URL', 'http://localhost:8005')}

Access the application at: http://{host}:{port}
    """)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        reload_dirs=[str(src_path)] if reload else None,
        log_level="info"
    )

if __name__ == "__main__":
    main()