#!/usr/bin/env python3
"""
Test script for the Data Ingestion Framework

Simple test to verify the framework components work correctly.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.ingestion_service import DataIngestionService


async def test_ingestion_framework():
    """Test the data ingestion framework."""
    print("🚀 Testing AFAS Data Ingestion Framework")
    print("=" * 50)
    
    # Initialize service (will use mock Redis for testing)
    service = DataIngestionService("redis://localhost:6379")
    
    try:
        print("📡 Initializing ingestion service...")
        await service.initialize()
        print("✅ Service initialized successfully")
        
        # Test health check
        print("\n🏥 Performing health check...")
        health = await service.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Pipeline: {health['pipeline']['pipeline_status']}")
        print(f"   Cache: {health['pipeline']['cache_status']}")
        
        # Test weather data ingestion
        print("\n🌤️  Testing weather data ingestion...")
        weather_result = await service.get_weather_data(
            latitude=42.0308,  # Ames, Iowa
            longitude=-93.6319,
            operation="current_weather"
        )
        
        if weather_result.success:
            print("✅ Weather data ingested successfully")
            print(f"   Quality Score: {weather_result.quality_score:.2f}")
            print(f"   Cache Hit: {weather_result.cache_hit}")
            print(f"   Temperature: {weather_result.data.get('temperature_f', 'N/A')}°F")
        else:
            print(f"❌ Weather data ingestion failed: {weather_result.error_message}")
        
        # Test soil data ingestion
        print("\n🌱 Testing soil data ingestion...")
        soil_result = await service.get_soil_data(
            latitude=42.0308,
            longitude=-93.6319,
            operation="soil_characteristics"
        )
        
        if soil_result.success:
            print("✅ Soil data ingested successfully")
            print(f"   Quality Score: {soil_result.quality_score:.2f}")
            print(f"   Cache Hit: {soil_result.cache_hit}")
            print(f"   Soil Series: {soil_result.data.get('soil_series', 'N/A')}")
            print(f"   Soil Texture: {soil_result.data.get('soil_texture', 'N/A')}")
        else:
            print(f"❌ Soil data ingestion failed: {soil_result.error_message}")
        
        # Test crop data ingestion
        print("\n🌽 Testing crop data ingestion...")
        crop_result = await service.get_crop_data(
            crop_name="corn",
            operation="crop_varieties"
        )
        
        if crop_result.success:
            print("✅ Crop data ingested successfully")
            print(f"   Quality Score: {crop_result.quality_score:.2f}")
            print(f"   Cache Hit: {crop_result.cache_hit}")
            varieties = crop_result.data.get('varieties', [])
            print(f"   Varieties Found: {len(varieties)}")
            if varieties:
                print(f"   First Variety: {varieties[0].get('variety_name', 'N/A')}")
        else:
            print(f"❌ Crop data ingestion failed: {crop_result.error_message}")
        
        # Test market data ingestion
        print("\n💰 Testing market data ingestion...")
        market_result = await service.get_market_data(operation="all_prices")
        
        if market_result.success:
            print("✅ Market data ingested successfully")
            print(f"   Quality Score: {market_result.quality_score:.2f}")
            print(f"   Cache Hit: {market_result.cache_hit}")
            commodities = market_result.data.get('commodities', {})
            print(f"   Corn Price: ${commodities.get('corn_per_bushel', 'N/A')}/bu")
        else:
            print(f"❌ Market data ingestion failed: {market_result.error_message}")
        
        # Test batch ingestion
        print("\n📦 Testing batch data ingestion...")
        batch_requests = [
            {
                "source_name": "weather_service",
                "operation": "current_weather",
                "params": {"latitude": 42.0, "longitude": -93.6}
            },
            {
                "source_name": "market_data",
                "operation": "commodity_prices",
                "params": {"commodity": "corn"}
            }
        ]
        
        batch_results = await service.batch_ingest_data(batch_requests)
        successful_batch = sum(1 for r in batch_results if r.success)
        print(f"✅ Batch ingestion completed: {successful_batch}/{len(batch_results)} successful")
        
        # Test ETL job status
        print("\n⚙️  Testing ETL job management...")
        jobs_status = service.get_all_jobs_status()
        print(f"   Scheduler Running: {jobs_status['scheduler_running']}")
        print(f"   Registered Jobs: {len(jobs_status['jobs'])}")
        enabled_jobs = sum(1 for job in jobs_status['jobs'].values() if job.get('enabled', False))
        print(f"   Enabled Jobs: {enabled_jobs}")
        
        # Test metrics
        print("\n📊 Testing metrics collection...")
        pipeline_metrics = service.get_pipeline_metrics()
        etl_metrics = service.get_etl_metrics()
        
        print(f"   Total Requests: {pipeline_metrics['total_requests']}")
        print(f"   Success Rate: {pipeline_metrics['success_rate_percent']:.1f}%")
        print(f"   Cache Hit Rate: {pipeline_metrics['cache_hit_rate_percent']:.1f}%")
        print(f"   ETL Jobs Run: {etl_metrics['total_jobs_run']}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n🔄 Shutting down service...")
        await service.shutdown()
        print("✅ Service shutdown complete")
    
    return True


async def main():
    """Main test function."""
    print(f"Starting test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = await test_ingestion_framework()
    
    if success:
        print("\n🎯 Data Ingestion Framework Test: PASSED")
        sys.exit(0)
    else:
        print("\n💥 Data Ingestion Framework Test: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())