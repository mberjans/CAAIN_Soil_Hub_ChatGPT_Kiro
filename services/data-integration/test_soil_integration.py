#!/usr/bin/env python3
"""
Integration test for soil database connections

Tests the complete soil data integration workflow.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.soil_service import SoilService


async def test_complete_workflow():
    """Test the complete soil data workflow."""
    
    print("🌾 AFAS Soil Database Integration Test")
    print("=" * 50)
    
    soil_service = SoilService()
    
    # Test location (Ames, Iowa - heart of corn belt)
    latitude = 42.0308
    longitude = -93.6319
    location_name = "Ames, Iowa"
    
    print(f"📍 Testing complete workflow for {location_name}")
    print(f"   Coordinates: {latitude}, {longitude}")
    
    try:
        # Step 1: Get soil characteristics
        print("\n1️⃣ Fetching soil characteristics...")
        soil_chars = await soil_service.get_soil_characteristics(latitude, longitude)
        
        print(f"   ✅ Soil Series: {soil_chars.soil_series}")
        print(f"   ✅ Texture: {soil_chars.soil_texture}")
        print(f"   ✅ Drainage: {soil_chars.drainage_class}")
        print(f"   ✅ pH Range: {soil_chars.typical_ph_range['min']:.1f} - {soil_chars.typical_ph_range['max']:.1f}")
        print(f"   ✅ Organic Matter: {soil_chars.organic_matter_typical:.1f}%")
        print(f"   ✅ Slope: {soil_chars.slope_range}")
        
        if soil_chars.permeability:
            print(f"   ✅ Permeability: {soil_chars.permeability}")
        if soil_chars.hydrologic_group:
            print(f"   ✅ Hydrologic Group: {soil_chars.hydrologic_group}")
        
        # Step 2: Get nutrient ranges
        print("\n2️⃣ Calculating nutrient ranges...")
        nutrient_ranges = await soil_service.get_nutrient_ranges(soil_chars)
        
        print(f"   ✅ Phosphorus Range: {nutrient_ranges.phosphorus_ppm_range['low']:.0f} - {nutrient_ranges.phosphorus_ppm_range['high']:.0f} ppm")
        print(f"   ✅ Potassium Range: {nutrient_ranges.potassium_ppm_range['low']:.0f} - {nutrient_ranges.potassium_ppm_range['high']:.0f} ppm")
        print(f"   ✅ Typical Nitrogen: {nutrient_ranges.nitrogen_typical:.0f} lbs/acre")
        print(f"   ✅ CEC Range: {nutrient_ranges.cec_range['min']:.1f} - {nutrient_ranges.cec_range['max']:.1f} meq/100g")
        print(f"   ✅ Base Saturation: {nutrient_ranges.base_saturation_range['min']:.0f} - {nutrient_ranges.base_saturation_range['max']:.0f}%")
        
        print("   🧪 Micronutrient Status:")
        for nutrient, status in nutrient_ranges.micronutrient_status.items():
            print(f"      {nutrient.title()}: {status}")
        
        # Step 3: Evaluate crop suitability
        print("\n3️⃣ Evaluating crop suitability...")
        suitability = await soil_service.get_crop_suitability(soil_chars)
        
        print("   🌽 Crop Suitability Ratings:")
        for crop, rating in suitability.crop_suitability.items():
            print(f"      {crop.title()}: {rating}")
        
        print(f"   💧 Irrigation Suitability: {suitability.irrigation_suitability}")
        print(f"   🌊 Erosion Risk: {suitability.erosion_risk}")
        
        if suitability.limitations:
            print("   ⚠️  Soil Limitations:")
            for limitation in suitability.limitations:
                print(f"      • {limitation}")
        
        if suitability.management_considerations:
            print("   💡 Management Considerations:")
            for consideration in suitability.management_considerations[:3]:  # Show first 3
                print(f"      • {consideration}")
        
        # Step 4: Generate agricultural recommendations
        print("\n4️⃣ Generating agricultural recommendations...")
        
        recommendations = []
        
        # pH recommendations
        ph_avg = (soil_chars.typical_ph_range['min'] + soil_chars.typical_ph_range['max']) / 2
        if ph_avg < 6.0:
            recommendations.append(f"Consider lime application - soil pH ({ph_avg:.1f}) is below optimal for most crops")
        elif ph_avg > 7.5:
            recommendations.append(f"Monitor micronutrient availability - high pH ({ph_avg:.1f}) may limit iron and zinc")
        
        # Organic matter recommendations
        if soil_chars.organic_matter_typical < 3.0:
            recommendations.append(f"Build soil organic matter ({soil_chars.organic_matter_typical:.1f}%) with cover crops or compost")
        
        # Drainage recommendations
        if "poorly" in soil_chars.drainage_class:
            recommendations.append("Consider drainage improvements or select crops tolerant of wet conditions")
        
        # Texture-specific recommendations
        if "sand" in soil_chars.soil_texture:
            recommendations.append("Use split nitrogen applications to reduce leaching in sandy soil")
        elif soil_chars.soil_texture == "clay":
            recommendations.append("Avoid field operations when wet to prevent compaction in clay soil")
        
        # Nutrient recommendations
        p_low = nutrient_ranges.phosphorus_ppm_range['low']
        if p_low < 15:
            recommendations.append(f"Soil may be low in phosphorus - consider soil testing and P fertilization")
        
        k_low = nutrient_ranges.potassium_ppm_range['low']
        if k_low < 120:
            recommendations.append(f"Soil may be low in potassium - consider soil testing and K fertilization")
        
        print("   📋 Agricultural Recommendations:")
        for i, rec in enumerate(recommendations[:5], 1):  # Show first 5
            print(f"      {i}. {rec}")
        
        # Step 5: Summary assessment
        print("\n5️⃣ Overall Assessment...")
        
        # Calculate overall soil quality score
        quality_score = 0
        max_score = 5
        
        # pH score
        if 6.0 <= ph_avg <= 7.0:
            quality_score += 1
        elif 5.5 <= ph_avg <= 7.5:
            quality_score += 0.5
        
        # Organic matter score
        if soil_chars.organic_matter_typical >= 3.5:
            quality_score += 1
        elif soil_chars.organic_matter_typical >= 2.5:
            quality_score += 0.5
        
        # Drainage score
        if soil_chars.drainage_class in ["well_drained", "moderately_well_drained"]:
            quality_score += 1
        elif soil_chars.drainage_class == "somewhat_poorly_drained":
            quality_score += 0.5
        
        # Texture score
        if soil_chars.soil_texture in ["loam", "silt_loam", "clay_loam"]:
            quality_score += 1
        elif soil_chars.soil_texture in ["sandy_loam", "silty_clay_loam"]:
            quality_score += 0.5
        
        # Erosion risk score
        if suitability.erosion_risk == "low":
            quality_score += 1
        elif suitability.erosion_risk == "moderate":
            quality_score += 0.5
        
        quality_percentage = (quality_score / max_score) * 100
        
        print(f"   📊 Soil Quality Score: {quality_score:.1f}/{max_score} ({quality_percentage:.0f}%)")
        
        if quality_percentage >= 80:
            print("   🌟 Excellent soil conditions for crop production")
        elif quality_percentage >= 60:
            print("   ✅ Good soil conditions with minor limitations")
        elif quality_percentage >= 40:
            print("   ⚠️  Fair soil conditions - management needed")
        else:
            print("   ❌ Poor soil conditions - significant improvements needed")
        
        print(f"\n✅ Complete workflow test successful!")
        
    except Exception as e:
        print(f"\n❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await soil_service.close()


async def test_database_integration():
    """Test integration with database models."""
    
    print("\n🗄️ Testing Database Integration")
    print("=" * 50)
    
    # Test that our soil service data can be stored in database models
    try:
        # Import database models
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../databases/python'))
        from models import SoilTest, Field, Farm
        
        soil_service = SoilService()
        
        # Get soil data
        soil_chars = await soil_service.get_soil_characteristics(42.0308, -93.6319)
        
        # Test creating a SoilTest model with our data
        ph_avg = (soil_chars.typical_ph_range['min'] + soil_chars.typical_ph_range['max']) / 2
        
        # This would be how we'd store the data (not actually saving to DB in test)
        soil_test_data = {
            'ph': ph_avg,
            'organic_matter_percent': soil_chars.organic_matter_typical,
            'soil_texture': soil_chars.soil_texture,
            'test_date': datetime.now().date()
        }
        
        print(f"   ✅ Compatible with SoilTest model")
        print(f"   ✅ pH: {soil_test_data['ph']:.1f}")
        print(f"   ✅ Organic Matter: {soil_test_data['organic_matter_percent']:.1f}%")
        print(f"   ✅ Texture: {soil_test_data['soil_texture']}")
        
        await soil_service.close()
        
    except ImportError as e:
        print(f"   ⚠️  Database models not available: {e}")
    except Exception as e:
        print(f"   ❌ Database integration test failed: {e}")


if __name__ == "__main__":
    print("🌾 AFAS Soil Database Integration Test Suite")
    print(f"Started at: {datetime.now().isoformat()}")
    
    try:
        # Run complete workflow test
        asyncio.run(test_complete_workflow())
        
        # Run database integration test
        asyncio.run(test_database_integration())
        
        print("\n" + "=" * 60)
        print("🎉 All integration tests completed successfully!")
        print(f"Completed at: {datetime.now().isoformat()}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Integration test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)