#!/usr/bin/env python3
"""
Test script for Variety Economic Analysis Service

This script tests the core functionality of the economic analysis service
without requiring the full API infrastructure.
"""

import sys
import os
import asyncio
from datetime import datetime
from decimal import Decimal

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.variety_economics import (
    VarietyEconomicAnalysisService,
    EconomicAnalysisResult,
    CostFactors,
    RevenueFactors
)

# Import models with fallback
try:
    from src.models.crop_variety_models import (
        EnhancedCropVariety,
        MarketAttributes,
        YieldPotential
    )
    from src.models.service_models import ConfidenceLevel
except ImportError:
    # Create minimal mock classes for testing
    class EnhancedCropVariety:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class MarketAttributes:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class YieldPotential:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class ConfidenceLevel:
        HIGH = "HIGH"
        MEDIUM = "MEDIUM"
        LOW = "LOW"


def create_test_variety():
    """Create a test variety for economic analysis."""
    return EnhancedCropVariety(
        variety_id="test_corn_001",
        variety_name="Test Corn Variety",
        crop_name="Corn",
        scientific_name="Zea mays",
        maturity_days=110,
        yield_potential_percentile=75.0,
        market_acceptance_score=4.2,
        disease_resistances={
            "rust": "moderate",
            "blight": "high"
        },
        yield_stability_rating=3.8,
        seed_cost_per_unit=2.50,
        seeding_rate_per_acre=32000,
        market_attributes=MarketAttributes(
            premium_pricing_potential=0.15,
            market_demand_level="high",
            export_potential=True
        ),
        yield_potential=YieldPotential(
            expected_yield_bu_per_acre=180.0,
            yield_variability_percent=12.0,
            drought_tolerance_rating=3.5
        )
    )


def create_test_regional_context():
    """Create test regional context for analysis."""
    return {
        "region": "Midwest",
        "climate_zone": "5a",
        "soil_type": "clay_loam",
        "crop_name": "corn",
        "market_data_source": "test",
        "current_market_price_per_bu": 5.25,
        "regional_yield_average": 165.0,
        "input_cost_multiplier": 1.0,
        "government_programs": ["ARC", "PLC"],
        "insurance_coverage": 0.85
    }


async def test_economic_analysis():
    """Test the economic analysis functionality."""
    print("Testing Variety Economic Analysis Service...")
    
    # Initialize service
    service = VarietyEconomicAnalysisService()
    print("✓ Service initialized successfully")
    
    # Create test data
    variety = create_test_variety()
    regional_context = create_test_regional_context()
    print("✓ Test data created successfully")
    
    # Perform economic analysis
    try:
        result = await service.analyze_variety_economics(
            variety, regional_context
        )
        print("✓ Economic analysis completed successfully")
        
        # Display results
        print("\n=== ECONOMIC ANALYSIS RESULTS ===")
        print(f"Variety: {result.variety_name}")
        print(f"Net Present Value: ${result.net_present_value:,.2f}")
        print(f"Internal Rate of Return: {result.internal_rate_of_return:.1%}")
        print(f"Payback Period: {result.payback_period_years:.1f} years")
        print(f"Break-even Yield: {result.break_even_yield:.1f} bu/acre")
        print(f"Break-even Price: ${result.break_even_price:.2f}/bu")
        print(f"Expected Revenue: ${result.expected_revenue_per_acre:,.2f}/acre")
        print(f"Expected Profit: ${result.expected_profit_per_acre:,.2f}/acre")
        print(f"Profit Margin: {result.profit_margin_percent:.1f}%")
        print(f"Risk-adjusted Return: {result.risk_adjusted_return:.1%}")
        print(f"Economic Viability Score: {result.economic_viability_score:.2f}")
        print(f"Confidence Level: {result.confidence_level}")
        print(f"Government Subsidies: ${result.government_subsidies_per_acre:.2f}/acre")
        print(f"Insurance Coverage: {result.insurance_coverage_percent:.1%}")
        
        return True
        
    except Exception as e:
        print(f"✗ Economic analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_comparative_analysis():
    """Test comparative analysis of multiple varieties."""
    print("\nTesting Comparative Analysis...")
    
    service = VarietyEconomicAnalysisService()
    
    # Create multiple test varieties
    varieties = [
        create_test_variety(),
        EnhancedCropVariety(
            variety_id="test_corn_002",
            variety_name="Test Corn Variety 2",
            crop_name="Corn",
            scientific_name="Zea mays",
            maturity_days=105,
            yield_potential_percentile=80.0,
            market_acceptance_score=4.5,
            disease_resistances={"rust": "high", "blight": "moderate"},
            yield_stability_rating=4.0,
            seed_cost_per_unit=3.00,
            seeding_rate_per_acre=30000,
            market_attributes=MarketAttributes(
                premium_pricing_potential=0.20,
                market_demand_level="high",
                export_potential=True
            ),
            yield_potential=YieldPotential(
                expected_yield_bu_per_acre=190.0,
                yield_variability_percent=10.0,
                drought_tolerance_rating=4.0
            )
        )
    ]
    
    regional_context = create_test_regional_context()
    
    try:
        results = await service.compare_varieties_economics(
            varieties, regional_context
        )
        print("✓ Comparative analysis completed successfully")
        
        print("\n=== COMPARATIVE ANALYSIS RESULTS ===")
        for i, (variety, analysis) in enumerate(results, 1):
            print(f"\n{i}. {variety.variety_name}")
            print(f"   Economic Score: {analysis.economic_viability_score:.2f}")
            print(f"   NPV: ${analysis.net_present_value:,.2f}")
            print(f"   IRR: {analysis.internal_rate_of_return:.1%}")
            print(f"   Profit/Acre: ${analysis.expected_profit_per_acre:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Comparative analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("VARIETY ECONOMIC ANALYSIS SERVICE TEST")
    print("=" * 60)
    
    # Test individual analysis
    test1_passed = await test_economic_analysis()
    
    # Test comparative analysis
    test2_passed = await test_comparative_analysis()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Individual Analysis: {'PASS' if test1_passed else 'FAIL'}")
    print(f"Comparative Analysis: {'PASS' if test2_passed else 'FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! Economic analysis service is working correctly.")
        return True
    else:
        print("\n❌ SOME TESTS FAILED. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)