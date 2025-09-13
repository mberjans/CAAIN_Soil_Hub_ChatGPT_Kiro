#!/usr/bin/env python3
"""
Demonstration of Data Validation and Cleaning Pipeline

This script demonstrates the enhanced data validation and cleaning
capabilities for agricultural data in the AFAS system.
"""

import asyncio
from datetime import datetime, timedelta
from src.services.data_validation_pipeline import DataValidationPipeline


async def demo_weather_validation():
    """Demonstrate weather data validation and cleaning."""
    print("=" * 60)
    print("WEATHER DATA VALIDATION DEMONSTRATION")
    print("=" * 60)
    
    pipeline = DataValidationPipeline()
    
    # Test case 1: Data with various issues
    print("\n1. Weather data with multiple issues:")
    problematic_weather = {
        "temperature_f": "78.5",  # String that needs conversion
        "humidity_percent": 105.0,  # Invalid > 100%
        "precipitation_inches": -0.2,  # Invalid negative
        "wind_speed_mph": 35.0,  # High wind speed (agricultural concern)
        "conditions": "thunderstorm",
        "timestamp": "2024-12-09T10:30:00Z"
    }
    
    print(f"Original data: {problematic_weather}")
    
    result = await pipeline.validate_and_clean(problematic_weather, "weather")
    
    print(f"Cleaned data: {result.cleaned_data}")
    print(f"Quality score: {result.quality_score:.3f}")
    print(f"Cleaning confidence: {result.cleaning_confidence:.3f}")
    print(f"Issues found: {len(result.issues_found)}")
    
    for issue in result.issues_found:
        print(f"  - {issue.severity.value.upper()}: {issue.message}")
        if issue.agricultural_context:
            print(f"    Agricultural context: {issue.agricultural_context}")
    
    print(f"Actions taken: {result.actions_taken}")
    
    # Test case 2: High-quality data
    print("\n2. High-quality weather data:")
    good_weather = {
        "temperature_f": 72.0,
        "humidity_percent": 68.0,
        "precipitation_inches": 0.0,
        "wind_speed_mph": 8.0,
        "conditions": "partly cloudy",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    print(f"Original data: {good_weather}")
    
    result = await pipeline.validate_and_clean(good_weather, "weather")
    
    print(f"Quality score: {result.quality_score:.3f}")
    print(f"Issues found: {len(result.issues_found)}")
    print(f"Actions taken: {len(result.actions_taken)}")


async def demo_soil_validation():
    """Demonstrate soil data validation and cleaning."""
    print("\n" + "=" * 60)
    print("SOIL DATA VALIDATION DEMONSTRATION")
    print("=" * 60)
    
    pipeline = DataValidationPipeline()
    
    # Test case 1: Soil data with issues
    print("\n1. Soil data with multiple issues:")
    problematic_soil = {
        "ph": "5.2",  # String, acidic pH
        "organic_matter_percent": "1.5%",  # String with %, low value
        "phosphorus_ppm": -3.0,  # Invalid negative
        "potassium_ppm": 85.0,  # Low value
        "soil_texture": "sandy loam",  # Needs normalization
        "drainage_class": "well drained",  # Needs normalization
        "test_date": "2021-01-15",  # Old test date
        "lab_name": "Test Lab <script>alert('test')</script>"  # Security issue
    }
    
    print(f"Original data: {problematic_soil}")
    
    result = await pipeline.validate_and_clean(problematic_soil, "soil")
    
    print(f"Cleaned data: {result.cleaned_data}")
    print(f"Quality score: {result.quality_score:.3f}")
    print(f"Cleaning confidence: {result.cleaning_confidence:.3f}")
    print(f"Issues found: {len(result.issues_found)}")
    
    for issue in result.issues_found:
        print(f"  - {issue.severity.value.upper()}: {issue.message}")
        if issue.agricultural_context:
            print(f"    Agricultural context: {issue.agricultural_context}")
    
    print(f"Actions taken: {result.actions_taken}")
    
    # Test case 2: Good soil data
    print("\n2. High-quality soil data:")
    good_soil = {
        "ph": 6.5,
        "organic_matter_percent": 3.2,
        "phosphorus_ppm": 28.0,
        "potassium_ppm": 185.0,
        "soil_texture": "silt_loam",
        "drainage_class": "well_drained",
        "test_date": "2024-03-15"
    }
    
    print(f"Original data: {good_soil}")
    
    result = await pipeline.validate_and_clean(good_soil, "soil")
    
    print(f"Quality score: {result.quality_score:.3f}")
    print(f"Issues found: {len(result.issues_found)}")
    print(f"Actions taken: {len(result.actions_taken)}")


async def demo_pipeline_metrics():
    """Demonstrate pipeline metrics and monitoring."""
    print("\n" + "=" * 60)
    print("PIPELINE METRICS DEMONSTRATION")
    print("=" * 60)
    
    pipeline = DataValidationPipeline()
    
    # Perform several validations
    test_data = [
        ({"temperature_f": "75.0", "humidity_percent": 65.0}, "weather"),
        ({"ph": "6.5", "organic_matter_percent": 3.0}, "soil"),
        ({"temperature_f": 200.0, "humidity_percent": 150.0}, "weather"),  # Bad data
        ({"ph": 6.2, "phosphorus_ppm": 25.0}, "soil"),
    ]
    
    print("\nProcessing test data...")
    for data, data_type in test_data:
        result = await pipeline.validate_and_clean(data, data_type)
        print(f"  {data_type}: Quality {result.quality_score:.2f}, "
              f"Issues {len(result.issues_found)}, Actions {len(result.actions_taken)}")
    
    # Show metrics
    print("\nPipeline Metrics:")
    metrics = pipeline.get_validation_metrics()
    
    print(f"Total validations: {metrics['total_validations']}")
    print(f"Average quality score: {metrics['average_quality_score']:.3f}")
    
    for data_type, stats in metrics['data_types'].items():
        print(f"\n{data_type.upper()} Data:")
        print(f"  Count: {stats['count']}")
        print(f"  Average quality: {stats['avg_quality']:.3f}")
        print(f"  Average issues per validation: {stats['avg_issues_per_validation']:.1f}")
        print(f"  Average actions per validation: {stats['avg_actions_per_validation']:.1f}")
    
    # Health check
    print("\nHealth Check:")
    health = await pipeline.health_check()
    print(f"Status: {health['status']}")
    print(f"Registered cleaners: {health['registered_cleaners']}")


async def main():
    """Run all demonstrations."""
    print("AFAS Data Validation and Cleaning Pipeline Demonstration")
    print("This demo shows how the pipeline validates and cleans agricultural data")
    
    await demo_weather_validation()
    await demo_soil_validation()
    await demo_pipeline_metrics()
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("✓ Automatic data type conversion")
    print("✓ Range validation with agricultural context")
    print("✓ Data normalization and standardization")
    print("✓ Security sanitization")
    print("✓ Agricultural-specific warnings and advice")
    print("✓ Quality scoring and confidence metrics")
    print("✓ Comprehensive logging and monitoring")


if __name__ == "__main__":
    asyncio.run(main())