#!/usr/bin/env python3
"""
Test script for Climate Zone Weather Service Integration (TICKET-001_climate-zone-detection-4.1)

Tests the enhanced weather service with climate zone data integration capabilities.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the services directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'data-integration', 'src'))

from services.weather_service import WeatherService, WeatherAPIError


async def test_historical_weather():
    """Test historical weather data retrieval."""
    print("\n🌤️  Testing Historical Weather Data Retrieval")
    print("=" * 50)
    
    weather_service = WeatherService()
    
    # Test coordinates (Ames, Iowa - agricultural region)
    test_coordinates = [
        (42.0308, -93.6319),  # Ames, Iowa
        (40.4406, -86.9292),  # West Lafayette, Indiana  
        (36.1627, -86.7816),  # Nashville, Tennessee
    ]
    
    for lat, lon in test_coordinates:
        try:
            print(f"\n📍 Testing coordinates: {lat}, {lon}")
            
            # Test 1 year of historical data
            historical_data = await weather_service.get_historical_weather(lat, lon, years=1)
            
            print(f"✅ Retrieved {len(historical_data)} days of historical weather data")
            
            if historical_data:
                # Show sample data
                sample_day = historical_data[0]
                print(f"   Sample day ({sample_day.date.strftime('%Y-%m-%d')}):")
                print(f"   - High: {sample_day.temperature_high_f:.1f}°F")
                print(f"   - Low: {sample_day.temperature_low_f:.1f}°F")
                print(f"   - Avg: {sample_day.temperature_avg_f:.1f}°F")
                print(f"   - Precipitation: {sample_day.precipitation_inches:.2f} inches")
                print(f"   - Conditions: {sample_day.conditions}")
            else:
                print("❌ No historical data retrieved")
                
        except Exception as e:
            print(f"❌ Error retrieving historical weather: {str(e)}")
    
    await weather_service.close()


async def test_climate_zone_data():
    """Test climate zone data analysis."""
    print("\n🗺️  Testing Climate Zone Data Analysis")
    print("=" * 50)
    
    weather_service = WeatherService()
    
    # Test coordinates across different climate zones
    test_locations = [
        (42.0308, -93.6319, "Ames, Iowa (Zone 5a)"),
        (30.2672, -97.7431, "Austin, Texas (Zone 8b)"),
        (47.6062, -122.3321, "Seattle, Washington (Zone 9a)"),
        (25.7617, -80.1918, "Miami, Florida (Zone 10b)"),
    ]
    
    for lat, lon, location in test_locations:
        try:
            print(f"\n📍 Testing {location}")
            
            climate_data = await weather_service.get_climate_zone_data(lat, lon)
            
            if climate_data:
                print("✅ Climate zone data retrieved:")
                print(f"   - USDA Zone: {climate_data.usda_zone}")
                print(f"   - Köppen Classification: {climate_data.koppen_classification}")
                print(f"   - Avg Min Temp: {climate_data.average_min_temp_f:.1f}°F")
                print(f"   - Avg Max Temp: {climate_data.average_max_temp_f:.1f}°F")
                print(f"   - Annual Precipitation: {climate_data.annual_precipitation_inches:.1f} inches")
                print(f"   - Growing Season: {climate_data.growing_season_length} days")
                if climate_data.last_frost_date:
                    print(f"   - Last Frost: ~{climate_data.last_frost_date}")
                if climate_data.first_frost_date:
                    print(f"   - First Frost: ~{climate_data.first_frost_date}")
            else:
                print("❌ No climate zone data retrieved")
                
        except Exception as e:
            print(f"❌ Error retrieving climate zone data: {str(e)}")
    
    await weather_service.close()


async def test_enhanced_agricultural_metrics():
    """Test enhanced agricultural metrics with climate zone awareness."""
    print("\n🌾 Testing Enhanced Agricultural Metrics")
    print("=" * 50)
    
    weather_service = WeatherService()
    
    # Test coordinates
    test_coordinates = [
        (42.0308, -93.6319, "Ames, Iowa"),
        (36.1627, -86.7816, "Nashville, Tennessee"),
    ]
    
    for lat, lon, location in test_coordinates:
        try:
            print(f"\n📍 Testing {location}")
            
            # Test with climate zone integration
            metrics_with_climate = await weather_service.get_agricultural_metrics(
                lat, lon, include_climate_zone=True
            )
            
            # Test without climate zone integration
            metrics_without_climate = await weather_service.get_agricultural_metrics(
                lat, lon, include_climate_zone=False
            )
            
            print("✅ Agricultural metrics with climate zone:")
            print(f"   - Growing Degree Days: {metrics_with_climate.growing_degree_days:.1f}")
            print(f"   - Accumulated Precipitation: {metrics_with_climate.accumulated_precipitation:.2f} inches")
            print(f"   - Days Since Rain: {metrics_with_climate.days_since_rain}")
            print(f"   - Soil Temperature: {metrics_with_climate.soil_temperature_f:.1f}°F")
            print(f"   - Evapotranspiration: {metrics_with_climate.evapotranspiration_inches:.3f} inches")
            print(f"   - Climate Zone: {metrics_with_climate.climate_zone}")
            print(f"   - Frost Risk Score: {metrics_with_climate.frost_risk_score:.2f}" if metrics_with_climate.frost_risk_score else "   - Frost Risk Score: N/A")
            
            print("\n📊 Comparison (without climate zone):")
            print(f"   - Soil Temperature: {metrics_without_climate.soil_temperature_f:.1f}°F (vs {metrics_with_climate.soil_temperature_f:.1f}°F)")
            print(f"   - Evapotranspiration: {metrics_without_climate.evapotranspiration_inches:.3f} inches (vs {metrics_with_climate.evapotranspiration_inches:.3f} inches)")
            print(f"   - Climate Zone: {metrics_without_climate.climate_zone} (vs {metrics_with_climate.climate_zone})")
            
        except Exception as e:
            print(f"❌ Error retrieving agricultural metrics: {str(e)}")
    
    await weather_service.close()


async def test_caching_functionality():
    """Test caching functionality."""
    print("\n💾 Testing Caching Functionality")
    print("=" * 50)
    
    weather_service = WeatherService()
    
    test_lat, test_lon = 42.0308, -93.6319  # Ames, Iowa
    
    try:
        print(f"📍 Testing cache with coordinates: {test_lat}, {test_lon}")
        
        # Get initial cache stats
        initial_stats = weather_service.get_cache_stats()
        print(f"Initial cache stats:")
        print(f"   - Climate zone cache entries: {initial_stats['climate_zone_cache']['total_entries']}")
        print(f"   - Historical weather cache entries: {initial_stats['historical_weather_cache']['total_entries']}")
        
        # First call - should populate cache
        print("\n🔄 First call (should populate cache)...")
        start_time = datetime.now()
        climate_data = await weather_service.get_climate_zone_data(test_lat, test_lon)
        first_call_time = (datetime.now() - start_time).total_seconds()
        print(f"   ✅ First call completed in {first_call_time:.2f} seconds")
        
        # Second call - should use cache
        print("\n⚡ Second call (should use cache)...")
        start_time = datetime.now()
        cached_climate_data = await weather_service.get_climate_zone_data(test_lat, test_lon)
        second_call_time = (datetime.now() - start_time).total_seconds()
        print(f"   ✅ Second call completed in {second_call_time:.2f} seconds")
        
        # Verify data is the same
        if climate_data and cached_climate_data:
            if climate_data.usda_zone == cached_climate_data.usda_zone:
                print("   ✅ Cached data matches original data")
            else:
                print("   ⚠️  Cached data differs from original data")
        
        # Show cache improvement
        if second_call_time < first_call_time:
            improvement = ((first_call_time - second_call_time) / first_call_time) * 100
            print(f"   📈 Cache provided {improvement:.1f}% speed improvement")
        
        # Get updated cache stats
        updated_stats = weather_service.get_cache_stats()
        print(f"\nUpdated cache stats:")
        print(f"   - Climate zone cache entries: {updated_stats['climate_zone_cache']['total_entries']}")
        print(f"   - Historical weather cache entries: {updated_stats['historical_weather_cache']['total_entries']}")
        
        # Test cache cleanup
        print("\n🧹 Testing cache cleanup...")
        weather_service.cleanup_expired_cache_entries()
        print("   ✅ Cache cleanup completed")
        
    except Exception as e:
        print(f"❌ Error testing caching: {str(e)}")
    
    await weather_service.close()


async def test_coordinate_climate_detector_integration():
    """Test integration with CoordinateClimateDetector."""
    print("\n🔗 Testing CoordinateClimateDetector Integration")
    print("=" * 50)
    
    try:
        # Import and test the coordinate climate detector
        from services.coordinate_climate_detector import CoordinateClimateDetector
        
        detector = CoordinateClimateDetector()
        test_lat, test_lon = 42.0308, -93.6319  # Ames, Iowa
        
        print(f"📍 Testing coordinate climate detection: {test_lat}, {test_lon}")
        
        # This should now work with the enhanced weather service
        climate_data = await detector.detect_climate_from_coordinates(
            test_lat, test_lon, include_detailed_analysis=True
        )
        
        if climate_data:
            print("✅ CoordinateClimateDetector integration successful:")
            print(f"   - USDA Zone: {climate_data.usda_zone.zone if climate_data.usda_zone else 'N/A'}")
            print(f"   - Confidence: {climate_data.usda_zone.confidence if climate_data.usda_zone else 'N/A'}")
            print(f"   - Köppen Analysis: {'Available' if climate_data.koppen_analysis else 'Not Available'}")
            print(f"   - Elevation: {climate_data.elevation_data.elevation_ft if climate_data.elevation_data else 'N/A'} ft")
            print(f"   - Overall Confidence: {climate_data.confidence_factors.get('overall_confidence', 'N/A')}")
        else:
            print("❌ CoordinateClimateDetector integration failed")
            
    except ImportError as e:
        print(f"⚠️  Could not import CoordinateClimateDetector: {str(e)}")
    except Exception as e:
        print(f"❌ Error testing CoordinateClimateDetector integration: {str(e)}")


async def main():
    """Run all tests."""
    print("🧪 CAAIN Soil Hub - Climate Zone Weather Service Integration Tests")
    print("TICKET-001_climate-zone-detection-4.1")
    print("=" * 70)
    
    tests = [
        test_historical_weather,
        test_climate_zone_data,
        test_enhanced_agricultural_metrics,
        test_caching_functionality,
        test_coordinate_climate_detector_integration,
    ]
    
    for test_func in tests:
        try:
            await test_func()
        except Exception as e:
            print(f"\n❌ Test {test_func.__name__} failed with error: {str(e)}")
        
        print("\n" + "-" * 50)
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())