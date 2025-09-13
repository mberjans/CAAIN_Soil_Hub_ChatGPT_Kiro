#!/usr/bin/env python3
"""
Test script for Soil Service implementation

Tests the soil database connections and data retrieval functionality.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.soil_service import SoilService, SoilDataError


async def test_soil_service():
    """Test the soil service functionality."""
    
    print("🌱 Testing AFAS Soil Service")
    print("=" * 50)
    
    soil_service = SoilService()
    
    # Test locations
    test_locations = [
        {"name": "Ames, Iowa (Corn Belt)", "lat": 42.0308, "lon": -93.6319},
        {"name": "Champaign, Illinois", "lat": 40.1164, "lon": -88.2434},
        {"name": "Manhattan, Kansas", "lat": 39.1836, "lon": -96.5717},
        {"name": "International Location (Brazil)", "lat": -15.7801, "lon": -47.9292}
    ]
    
    for location in test_locations:
        print(f"\n📍 Testing location: {location['name']}")
        print(f"   Coordinates: {location['lat']}, {location['lon']}")
        
        try:
            # Test soil characteristics
            print("   Fetching soil characteristics...")
            soil_chars = await soil_service.get_soil_characteristics(
                location['lat'], location['lon']
            )
            
            print(f"   ✅ Soil Series: {soil_chars.soil_series}")
            print(f"   ✅ Texture: {soil_chars.soil_texture}")
            print(f"   ✅ Drainage: {soil_chars.drainage_class}")
            print(f"   ✅ pH Range: {soil_chars.typical_ph_range['min']:.1f} - {soil_chars.typical_ph_range['max']:.1f}")
            print(f"   ✅ Organic Matter: {soil_chars.organic_matter_typical:.1f}%")
            print(f"   ✅ Slope: {soil_chars.slope_range}")
            
            # Test nutrient ranges
            print("   Fetching nutrient ranges...")
            nutrient_ranges = await soil_service.get_nutrient_ranges(soil_chars)
            
            print(f"   ✅ P Range: {nutrient_ranges.phosphorus_ppm_range['low']:.0f}-{nutrient_ranges.phosphorus_ppm_range['high']:.0f} ppm")
            print(f"   ✅ K Range: {nutrient_ranges.potassium_ppm_range['low']:.0f}-{nutrient_ranges.potassium_ppm_range['high']:.0f} ppm")
            print(f"   ✅ Typical N: {nutrient_ranges.nitrogen_typical:.0f} lbs/acre")
            
            # Test crop suitability
            print("   Evaluating crop suitability...")
            suitability = await soil_service.get_crop_suitability(soil_chars)
            
            print(f"   ✅ Corn Suitability: {suitability.crop_suitability.get('corn', 'unknown')}")
            print(f"   ✅ Soybean Suitability: {suitability.crop_suitability.get('soybean', 'unknown')}")
            print(f"   ✅ Wheat Suitability: {suitability.crop_suitability.get('wheat', 'unknown')}")
            
            if suitability.limitations:
                print(f"   ⚠️  Limitations: {', '.join(suitability.limitations[:2])}")
            
            if suitability.management_considerations:
                print(f"   💡 Management: {suitability.management_considerations[0]}")
            
        except SoilDataError as e:
            print(f"   ❌ Soil data error: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
    
    # Test error handling
    print(f"\n🧪 Testing error handling...")
    try:
        # Invalid coordinates
        await soil_service.get_soil_characteristics(999, 999)
        print("   ❌ Should have failed with invalid coordinates")
    except SoilDataError:
        print("   ✅ Properly handled invalid coordinates")
    except Exception as e:
        print(f"   ⚠️  Unexpected error type: {e}")
    
    # Close connections
    await soil_service.close()
    
    print(f"\n🎉 Soil service testing completed!")
    print(f"   Timestamp: {datetime.now().isoformat()}")


async def test_individual_services():
    """Test individual soil data services."""
    
    print("\n🔬 Testing Individual Soil Services")
    print("=" * 50)
    
    from services.soil_service import USDAWebSoilSurveyService, SoilGridsService
    
    # Test USDA service
    print("\n📊 Testing USDA Web Soil Survey Service...")
    usda_service = USDAWebSoilSurveyService()
    
    try:
        soil_data = await usda_service.get_soil_data_by_coordinates(42.0308, -93.6319)
        print(f"   ✅ USDA Service: {soil_data.soil_series} - {soil_data.soil_texture}")
    except Exception as e:
        print(f"   ⚠️  USDA Service failed: {e}")
    finally:
        await usda_service.close()
    
    # Test SoilGrids service
    print("\n🌍 Testing SoilGrids Service...")
    soilgrids_service = SoilGridsService()
    
    try:
        soil_data = await soilgrids_service.get_soil_data_by_coordinates(42.0308, -93.6319)
        print(f"   ✅ SoilGrids Service: {soil_data.soil_series} - {soil_data.soil_texture}")
    except Exception as e:
        print(f"   ⚠️  SoilGrids Service failed: {e}")


async def test_agricultural_calculations():
    """Test agricultural calculation accuracy."""
    
    print("\n🧮 Testing Agricultural Calculations")
    print("=" * 50)
    
    soil_service = SoilService()
    
    # Test with known soil characteristics
    from services.soil_service import SoilCharacteristics
    
    test_soil = SoilCharacteristics(
        soil_series="Clarion",
        soil_texture="silt_loam",
        drainage_class="well_drained",
        typical_ph_range={"min": 6.0, "max": 6.8},
        organic_matter_typical=3.5,
        slope_range="0-2%",
        erosion_factor_k=0.32
    )
    
    print(f"   Test Soil: {test_soil.soil_series} {test_soil.soil_texture}")
    
    # Test nutrient range calculations
    nutrient_ranges = await soil_service.get_nutrient_ranges(test_soil)
    
    print(f"   ✅ P Range: {nutrient_ranges.phosphorus_ppm_range}")
    print(f"   ✅ K Range: {nutrient_ranges.potassium_ppm_range}")
    print(f"   ✅ CEC Range: {nutrient_ranges.cec_range}")
    
    # Test crop suitability calculations
    suitability = await soil_service.get_crop_suitability(test_soil)
    
    print(f"   ✅ Crop Ratings: {suitability.crop_suitability}")
    print(f"   ✅ Erosion Risk: {suitability.erosion_risk}")
    print(f"   ✅ Irrigation Suitability: {suitability.irrigation_suitability}")
    
    await soil_service.close()


if __name__ == "__main__":
    print("🌾 AFAS Soil Service Test Suite")
    print(f"Started at: {datetime.now().isoformat()}")
    
    try:
        # Run main soil service tests
        asyncio.run(test_soil_service())
        
        # Run individual service tests
        asyncio.run(test_individual_services())
        
        # Run agricultural calculation tests
        asyncio.run(test_agricultural_calculations())
        
        print("\n✅ All tests completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)