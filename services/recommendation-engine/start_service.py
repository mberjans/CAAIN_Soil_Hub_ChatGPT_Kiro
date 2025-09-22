#!/usr/bin/env python3
"""
Start the Recommendation Engine Service

Simple script to start the recommendation engine FastAPI service.
"""

import os
import sys
import uvicorn

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("RECOMMENDATION_ENGINE_PORT", 8001))
    
    print(f"Starting AFAS Recommendation Engine on port {port}")
    print("=" * 50)
    print("Available endpoints:")
    print("  - Health check: http://localhost:{}/health".format(port))
    print("  - API docs: http://localhost:{}/docs".format(port))
    print("  - Crop selection: POST http://localhost:{}/api/v1/recommendations/crop-selection".format(port))
    print("  - Fertilizer strategy: POST http://localhost:{}/api/v1/recommendations/fertilizer-strategy".format(port))
    print("  - Soil fertility: POST http://localhost:{}/api/v1/recommendations/soil-fertility".format(port))
    print("  - Crop rotation: POST http://localhost:{}/api/v1/recommendations/crop-rotation".format(port))
    print("  - Nutrient deficiency: POST http://localhost:{}/api/v1/recommendations/nutrient-deficiency".format(port))
    print("  - Fertilizer selection: POST http://localhost:{}/api/v1/recommendations/fertilizer-selection".format(port))
    print("  - General recommendations: POST http://localhost:{}/api/v1/recommendations/generate".format(port))
    print("=" * 50)
    
    # Start the service
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )