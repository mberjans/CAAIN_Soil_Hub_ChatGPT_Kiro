#!/usr/bin/env python3
"""
Test Climate Zone Integration with Location Validation Service
TICKET-001_climate-zone-detection-4.2

This test verifies the integration between the location validation service
and the enhanced weather service for climate zone detection.
"""

import asyncio
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/services'))

from location_validation_service import LocationValidationService


async def test_enhanced_climate_integration():
    """Test the enhanced climate zone integration."""
    print("Testing Enhanced Climate Zone Integration")
    print("=" * 50)
    
    # Initialize service
    service = LocationValidationService()
    
    # Test coordinates (Ames, Iowa - known agricultural area)
    test_coords = [
        (42.0308, -93.6319),  # Ames, Iowa
        (40.4173, -86.8751),  # Lafayette, Indiana (Purdue area)
        (32.0835, -81.0998),  # Savannah, Georgia
    ]
    
    for lat, lon in test_coords:
        print(f"\nTesting coordinates: {lat}, {lon}")
        print("-" * 30)
        
        try:
            # Test basic climate zone detection
            climate_zone = await service._get_climate_zone(lat, lon)
            print(f"Basic Climate Zone: {climate_zone}")
            
            # Test comprehensive climate analysis
            if service.validation_config.get('use_enhanced_climate_detection'):
                analysis = await service.get_comprehensive_climate_analysis(lat, lon)
                if analysis.get('error'):
                    print(f"Enhanced Analysis Error: {analysis['error']}")
                    print(f"Fallback Zone: {analysis.get('basic_zone')}")
                else:
                    print(f"USDA Zone: {analysis.get('usda_zone')}")
                    print(f"Köppen Classification: {analysis.get('koppen_classification')}")
                    print(f"Growing Season: {analysis.get('growing_season', {}).get('length_days')} days")
                    
                    # Agricultural assessment
                    ag_assessment = analysis.get('agricultural_assessment', {})
                    print(f"Agricultural Suitability: {ag_assessment.get('category')} ({ag_assessment.get('suitability_score')})")
            else:
                print("Enhanced climate detection not available")
            
            # Test comprehensive validation
            validation_result = await service.validate_agricultural_location(lat, lon)
            print(f"Validation Status: {'✅ Valid' if validation_result.valid else '❌ Invalid'}")
            
            if validation_result.geographic_info:
                geo_info = validation_result.geographic_info
                print(f"Geographic Info: {geo_info.state}, Zone: {geo_info.climate_zone}")
                if hasattr(geo_info, 'climate_analysis') and geo_info.climate_analysis:
                    print("✅ Climate analysis integrated into geographic info")
                else:
                    print("⚠️ Climate analysis not integrated")
            
            if validation_result.warnings:
                print(f"Warnings: {len(validation_result.warnings)}")
                for warning in validation_result.warnings[:2]:  # Show first 2 warnings
                    print(f"  - {warning}")
                    
        except Exception as e:
            print(f"❌ Error testing coordinates {lat}, {lon}: {e}")
    
    print(f"\n{'=' * 50}")
    print("Climate Integration Test Complete")


if __name__ == "__main__":
    asyncio.run(test_enhanced_climate_integration())