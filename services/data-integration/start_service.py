#!/usr/bin/env python3
"""
Start Data Integration Service

Simple script to start the data integration service for testing.
"""

import uvicorn
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import app

if __name__ == "__main__":
    port = int(os.getenv("DATA_INTEGRATION_PORT", 8003))
    print(f"🚀 Starting AFAS Data Integration Service on port {port}")
    print(f"📖 API Documentation: http://localhost:{port}/docs")
    print(f"🏥 Health Check: http://localhost:{port}/health")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")