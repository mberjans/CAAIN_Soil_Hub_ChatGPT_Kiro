#!/usr/bin/env python3
"""
Cover Crop Selection Service Startup Script

Simple script to start the cover crop selection service.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Start the cover crop selection service."""
    # Set default port
    port = int(os.getenv("COVER_CROP_SERVICE_PORT", 8006))
    
    print(f"Starting Cover Crop Selection Service on port {port}")
    print("Service endpoints will be available at:")
    print(f"  - Health check: http://localhost:{port}/health")
    print(f"  - API docs: http://localhost:{port}/docs")
    print(f"  - Cover crop selection: http://localhost:{port}/api/v1/cover-crops/select")
    print(f"  - Species lookup: http://localhost:{port}/api/v1/cover-crops/species")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nShutting down Cover Crop Selection Service...")
    except Exception as e:
        print(f"Error starting service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()