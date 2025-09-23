#!/usr/bin/env python3
"""
Demo script for soil test functionality.

This script demonstrates the soil test processing capabilities including
manual data entry, validation, interpretation, and recommendations.
"""

import asyncio
import sys
import os
from datetime import date

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.ingestion_service import DataIngestionService

async def demo_soil_test_processing():
    """Demonstrate soil test processing functionality."""
    print("🌱 AFAS Soil Test Processing Demo")
    print("=" * 50)
    
    # Initialize the ingestion service
    service = DataIngestionService()
    await service.initialize()
    
    try:
        # Demo 1: Good soil conditions
        print("\n📊 Demo 1: Processing Good Soil Test Results")
        print("-" * 40)
        
        good_soil_data = {
            "ph": 6.5,
            "organic_matter_percent": 4.2,
            "phosphorus_ppm": 28,
            "potassium_ppm": 185,
            "nitrogen_ppm": 15,
            "soil_texture": "silt_loam",
            "cec_meq_per_100g": 19.5,
            "test_date": date.today().isoformat(),
            "lab_name": "Iowa State Soil Testing Lab"
        }
        
        result = await service.process_soil_test_data(good_soil_data)
        
        if result.success:
            print("✅ Processing successful!")
            print(f"   Test ID: {result.data['test_id']}")
            print(f"   Confidence Score: {result.data['confidence_score']:.2f}")
            print(f"   Overall Rating: {result.data['interpretation']['overall_rating']}")
            print("   Recommendations:")
            for i, rec in enumerate(result.data['recommendations'][:3], 1):
                print(f"     {i}. {rec}")
        else:
            print(f"❌ Processing failed: {result.error_message}")
        
        # Demo 2: Problematic soil conditions
        print("\n📊 Demo 2: Processing Problematic Soil Test Results")
        print("-" * 40)
        
        problem_soil_data = {
            "ph": 5.1,  # Too acidic
            "organic_matter_percent": 1.5,  # Too low
            "phosphorus_ppm": 8,  # Deficient
            "potassium_ppm": 75,  # Low
            "soil_texture": "clay",
            "test_date": date.today().isoformat()
        }
        
        result = await service.process_soil_test_data(problem_soil_data)
        
        if result.success:
            print("✅ Processing successful!")
            print(f"   Confidence Score: {result.data['confidence_score']:.2f}")
            print(f"   Overall Rating: {result.data['interpretation']['overall_rating']}")
            print("   Key Recommendations:")
            for i, rec in enumerate(result.data['recommendations'][:4], 1):
                print(f"     {i}. {rec}")
        else:
            print(f"❌ Processing failed: {result.error_message}")
        
        # Demo 3: Detailed interpretation
        print("\n📊 Demo 3: Detailed Soil Test Interpretation")
        print("-" * 40)
        
        interpretation_data = {
            "ph": 6.8,
            "organic_matter_percent": 3.0,
            "phosphorus_ppm": 18,
            "potassium_ppm": 140,
            "soil_texture": "loam",
            "crop_type": "corn"
        }
        
        result = await service.interpret_soil_test(interpretation_data)
        
        if result.success:
            data = result.data
            print("✅ Interpretation successful!")
            print(f"   Overall Rating: {data['overall_rating']}")
            print(f"   Confidence Score: {data['confidence_score']:.2f}")
            print("   Nutrient Status:")
            for nutrient, status in data['nutrient_status'].items():
                print(f"     {nutrient.replace('_', ' ').title()}: {status}")
            print("   Limiting Factors:")
            for factor in data['limiting_factors']:
                print(f"     • {factor}")
            print("   Detailed Recommendations:")
            for rec in data['recommendations'][:3]:
                print(f"     • {rec['practice']} ({rec['priority']} priority)")
                print(f"       {rec['description']}")
                print(f"       Cost: {rec['cost_per_acre']}")
        else:
            print(f"❌ Interpretation failed: {result.error_message}")
        
        # Demo 4: Text parsing simulation
        print("\n📊 Demo 4: Soil Test Report Text Parsing")
        print("-" * 40)
        
        sample_report_text = """
        SOIL TEST REPORT
        Laboratory: Iowa State University Soil Testing Lab
        Date: 12/09/2024
        Sample ID: ST-2024-001
        
        RESULTS:
        pH: 6.3
        Organic Matter: 3.7%
        Phosphorus: 22 ppm
        Potassium: 165 ppm
        CEC: 17.5 meq/100g
        
        Soil Texture: Silt Loam
        """
        
        result = await service.parse_soil_test_report(
            sample_report_text, 
            filename="sample_report.txt"
        )
        
        if result.success:
            print("✅ Text parsing successful!")
            print(f"   Confidence Score: {result.data['confidence_score']:.2f}")
            print("   Extracted Values:")
            interpretation = result.data['interpretation']
            print(f"     Overall Rating: {interpretation['overall_rating']}")
            print("   Sample Recommendations:")
            for i, rec in enumerate(result.data['recommendations'][:2], 1):
                print(f"     {i}. {rec}")
        else:
            print(f"❌ Text parsing failed: {result.error_message}")
        
        # Demo 5: Validation testing
        print("\n📊 Demo 5: Data Validation Testing")
        print("-" * 40)
        
        invalid_data = {
            "ph": 15.0,  # Invalid pH
            "organic_matter_percent": -2.0,  # Invalid negative
            "phosphorus_ppm": 300,  # Too high
            "test_date": date.today().isoformat()
        }
        
        result = await service.process_soil_test_data(invalid_data)
        
        if not result.success:
            print("✅ Validation working correctly!")
            print(f"   Error: {result.error_message}")
        else:
            print("❌ Validation should have failed for invalid data")
        
    finally:
        await service.shutdown()
    
    print("\n🎉 Demo completed successfully!")
    print("\nKey Features Demonstrated:")
    print("• Manual soil test data processing")
    print("• Agricultural interpretation and scoring")
    print("• Intelligent recommendations based on soil conditions")
    print("• Text parsing from laboratory reports")
    print("• Data validation and error handling")
    print("• Confidence scoring based on data completeness")

if __name__ == "__main__":
    asyncio.run(demo_soil_test_processing())