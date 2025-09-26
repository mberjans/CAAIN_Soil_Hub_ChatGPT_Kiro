#!/usr/bin/env python3
"""
Standalone test for timing service functionality
"""

import sys
import os
import asyncio
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.timing_service import CoverCropTimingService
from models.cover_crop_models import TimingRecommendationRequest

async def test_timing_service():
    """Test the timing service directly."""
    print("Testing Cover Crop Timing Service...")
    
    # Create timing service
    timing_service = CoverCropTimingService()
    await timing_service.initialize()
    
    # Test location (Boston area)
    test_location = {
        "latitude": 42.3601,
        "longitude": -71.0589,
        "state": "MA",
        "climate_zone": "6a",
        "elevation_ft": 100
    }
    
    # Test request
    request = TimingRecommendationRequest(
        species_id="crimson_clover",
        location=test_location,
        main_crop_schedule={},
        management_goals=["nitrogen_fixation", "erosion_control"]
    )
    
    try:
        # Generate timing recommendations
        response = await timing_service.generate_comprehensive_timing_recommendation(request)
        
        print(f"✅ Successfully generated timing recommendations for {response.species_id}")
        print(f"📅 Planting window: {response.recommended_planting.optimal_planting_start} to {response.recommended_planting.optimal_planting_end}")
        print(f"🗓️ Termination options: {len(response.recommended_termination)} methods available")
        print(f"📋 Summary: {response.recommendation_summary}")
        print(f"🎯 Confidence: {response.overall_confidence}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing timing service: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_timing_service())
    if success:
        print("\n🎉 Timing system test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Timing system test failed!")
        sys.exit(1)