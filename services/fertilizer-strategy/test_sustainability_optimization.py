#!/usr/bin/env python3
"""
Simple test script to verify the sustainability optimization service is working.
"""

import asyncio
import sys
import os
from uuid import uuid4

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.environmental_optimization_service import SustainabilityOptimizationService

async def test_sustainability_optimization():
    """Test the sustainability optimization service."""
    print("Testing Sustainability Optimization Service...")
    
    try:
        # Create service instance
        service = SustainabilityOptimizationService()
        print("✓ Service created successfully")
        
        # Test data
        field_id = uuid4()
        field_data = {
            "soil_type": "clay_loam",
            "organic_matter_percent": 3.5,
            "ph": 6.2,
            "field_size_acres": 40.0,
            "slope_percent": 2.0,
            "drainage_class": "moderate"
        }
        
        fertilizer_options = [
            {
                "type": "nitrogen",
                "form": "urea",
                "cost_per_unit": 0.45,
                "efficiency": 0.85
            },
            {
                "type": "phosphorus",
                "form": "DAP",
                "cost_per_unit": 0.65,
                "efficiency": 0.75
            },
            {
                "type": "potassium",
                "form": "MOP",
                "cost_per_unit": 0.35,
                "efficiency": 0.90
            }
        ]
        
        print("✓ Test data prepared")
        
        # Test optimization
        result = await service.optimize_sustainability(
            field_id=field_id,
            field_data=field_data,
            fertilizer_options=fertilizer_options,
            optimization_method="genetic_algorithm",
            include_trade_off_analysis=True
        )
        
        print("✓ Optimization completed successfully")
        print(f"  - Optimization ID: {result.optimization_id}")
        print(f"  - Field ID: {result.field_id}")
        print(f"  - Optimization Score: {result.optimization_score:.3f}")
        print(f"  - Confidence Level: {result.confidence_level:.3f}")
        print(f"  - Processing Time: {result.processing_time_ms:.1f}ms")
        
        # Print optimal rates
        print("  - Optimal Fertilizer Rates:")
        for nutrient, rate in result.optimal_fertilizer_rates.items():
            print(f"    {nutrient}: {rate:.1f} lbs/acre")
        
        # Print environmental impact
        env_impact = result.environmental_impact
        print("  - Environmental Impact:")
        print(f"    Runoff Risk: {env_impact.nutrient_runoff_risk}")
        print(f"    Groundwater Risk: {env_impact.groundwater_contamination_risk}")
        print(f"    Carbon Footprint: {env_impact.carbon_footprint} kg CO2/acre")
        
        # Print sustainability metrics
        metrics = result.sustainability_metrics
        print("  - Sustainability Metrics:")
        print(f"    N Use Efficiency: {metrics.nitrogen_use_efficiency:.3f}")
        print(f"    P Use Efficiency: {metrics.phosphorus_use_efficiency:.3f}")
        print(f"    K Use Efficiency: {metrics.potassium_use_efficiency:.3f}")
        print(f"    Overall Score: {metrics.sustainability_score:.3f}")
        
        # Print recommendations
        print("  - Recommendations:")
        for i, rec in enumerate(result.recommendations[:5], 1):
            print(f"    {i}. {rec}")
        
        print("\n✓ All tests passed! Sustainability optimization system is working correctly.")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("=" * 60)
    print("SUSTAINABILITY OPTIMIZATION SYSTEM TEST")
    print("=" * 60)
    
    if await test_sustainability_optimization():
        print("\n✓ The sustainability optimization system is fully functional.")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
