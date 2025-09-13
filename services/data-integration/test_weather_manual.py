#!/usr/bin/env python3
"""
Manual Weather API Test Script

Simple script to test the weather API integration manually.
Run this to verify the weather service is working correctly.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.weather_service import WeatherService, WeatherAPIError


async def test_weather_service():
    """Test the weather service with real API calls."""
    
    print("🌤️  Testing AFAS Weather API Integration")
    print("=" * 50)
    
    # Test coordinates (Ames, Iowa - agricultural area)
    latitude = 42.0308
    longitude = -93.6319
    location_name = "Ames, Iowa"
    
    weather_service = WeatherService()
    
    try:
        print(f"\n📍 Testing location: {location_name}")
        print(f"   Coordinates: {latitude}, {longitude}")
        
        # Test current weather
        print("\n🌡️  Fetching current weather...")
        try:
            current_weather = await weather_service.get_current_weather(latitude, longitude)
            
            print("✅ Current Weather Retrieved:")
            print(f"   Temperature: {current_weather.temperature_f}°F")
            print(f"   Humidity: {current_weather.humidity_percent}%")
            print(f"   Conditions: {current_weather.conditions}")
            print(f"   Wind: {current_weather.wind_speed_mph} mph {current_weather.wind_direction}")
            print(f"   Pressure: {current_weather.pressure_mb} mb")
            print(f"   Precipitation: {current_weather.precipitation_inches} inches")
            print(f"   Timestamp: {current_weather.timestamp}")
            
        except WeatherAPIError as e:
            print(f"❌ Current weather failed: {e}")
        
        # Test forecast
        print("\n📅 Fetching 5-day forecast...")
        try:
            forecast = await weather_service.get_forecast(latitude, longitude, 5)
            
            print("✅ Forecast Retrieved:")
            for i, day in enumerate(forecast):
                print(f"   Day {i+1} ({day.date}):")
                print(f"     High/Low: {day.high_temp_f}°F / {day.low_temp_f}°F")
                print(f"     Conditions: {day.conditions}")
                print(f"     Precipitation: {day.precipitation_amount} inches ({day.precipitation_chance}% chance)")
                print(f"     Wind: {day.wind_speed_mph} mph")
                
        except WeatherAPIError as e:
            print(f"❌ Forecast failed: {e}")
        
        # Test agricultural metrics
        print("\n🌾 Calculating agricultural weather metrics...")
        try:
            ag_metrics = await weather_service.get_agricultural_metrics(latitude, longitude, 50.0)
            
            print("✅ Agricultural Metrics Calculated:")
            print(f"   Growing Degree Days: {ag_metrics.growing_degree_days}")
            print(f"   Accumulated Precipitation: {ag_metrics.accumulated_precipitation} inches")
            print(f"   Days Since Rain: {ag_metrics.days_since_rain}")
            if ag_metrics.soil_temperature_f:
                print(f"   Estimated Soil Temperature: {ag_metrics.soil_temperature_f}°F")
            if ag_metrics.evapotranspiration_inches:
                print(f"   Estimated ET: {ag_metrics.evapotranspiration_inches} inches")
                
        except Exception as e:
            print(f"❌ Agricultural metrics failed: {e}")
        
        # Test different locations
        print("\n🗺️  Testing multiple locations...")
        
        test_locations = [
            (40.7128, -74.0060, "New York, NY"),
            (39.7392, -104.9903, "Denver, CO"),
            (32.7767, -96.7970, "Dallas, TX"),
            (44.9778, -93.2650, "Minneapolis, MN")
        ]
        
        for lat, lon, name in test_locations:
            try:
                weather = await weather_service.get_current_weather(lat, lon)
                print(f"   ✅ {name}: {weather.temperature_f}°F, {weather.conditions}")
            except Exception as e:
                print(f"   ❌ {name}: Failed - {e}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    finally:
        # Clean up
        await weather_service.close()
        print("\n🔚 Weather service test completed")


async def test_api_keys():
    """Test API key configuration."""
    print("\n🔑 Checking API Key Configuration...")
    
    openweather_key = os.getenv("OPENWEATHER_API_KEY")
    if openweather_key:
        print(f"   ✅ OpenWeatherMap API Key: {'*' * (len(openweather_key) - 4)}{openweather_key[-4:]}")
    else:
        print("   ⚠️  OpenWeatherMap API Key: Not configured (will use NOAA only)")
    
    print("   ℹ️  NOAA API: No key required (public API)")


def main():
    """Main test function."""
    print("Starting Weather API Integration Test...")
    
    # Test API keys first
    asyncio.run(test_api_keys())
    
    # Test weather service
    asyncio.run(test_weather_service())
    
    print("\n✨ Test completed! Check the output above for any issues.")


if __name__ == "__main__":
    main()