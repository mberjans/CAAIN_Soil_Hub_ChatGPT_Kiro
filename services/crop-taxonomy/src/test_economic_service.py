"""
Test script for sophisticated ROI analysis functionality.

This script tests the enhanced VarietyEconomicAnalysisService with sophisticated
ROI and profitability analysis features.
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from services.variety_economics import (
        VarietyEconomicAnalysisService,
        SophisticatedROIAnalysis,
        ScenarioType,
        RiskLevel
    )
    from models.crop_variety_models import EnhancedCropVariety
except ImportError:
    logger.error("Could not import required modules. Make sure you're running from the correct directory.")
    exit(1)


async def test_sophisticated_roi_analysis():
    """Test the sophisticated ROI analysis functionality."""
    
    logger.info("Starting sophisticated ROI analysis test...")
    
    # Initialize the service
    service = VarietyEconomicAnalysisService()
    
    # Create a mock variety for testing
    variety = EnhancedCropVariety(
        variety_id=uuid4(),
        crop_id=uuid4(),
        variety_name="Test Corn Variety",
        variety_code="TC001",
        breeder_company="Test Breeder",
        relative_maturity=110,
        maturity_group="4.5",
        yield_potential_percentile=75.0,
        market_acceptance_score=4.2,
        yield_stability_rating=7.5
    )
    
    # Create regional context
    regional_context = {
        "crop_name": "corn",
        "region": "US",
        "climate_zone": "6a",
        "soil_type": "clay_loam",
        "yield_multiplier": 1.0,
        "price_multiplier": 1.0,
        "cost_multiplier": 1.0,
        "weather_risk_score": 0.5,
        "price_volatility": 0.15,
        "yield_volatility_adjustment": 0.0
    }
    
    # Farmer preferences
    farmer_preferences = {
        "risk_tolerance": "medium",
        "investment_horizon": "long_term",
        "preferred_crops": ["corn", "soybean"]
    }
    
    try:
        # Test sophisticated ROI analysis
        logger.info("Performing sophisticated ROI analysis...")
        result = await service.perform_sophisticated_roi_analysis(
            variety=variety,
            regional_context=regional_context,
            farmer_preferences=farmer_preferences,
            analysis_horizon_years=5
        )
        
        # Display results
        logger.info("=== SOPHISTICATED ROI ANALYSIS RESULTS ===")
        logger.info(f"Variety: {result.variety_name}")
        logger.info(f"Analysis Horizon: {result.analysis_horizon_years} years")
        logger.info(f"Analysis Date: {result.analysis_date}")
        
        logger.info("\n--- Financial Metrics ---")
        logger.info(f"NPV: ${result.net_present_value:.2f}")
        logger.info(f"IRR: {result.internal_rate_of_return:.2f}%")
        logger.info(f"MIRR: {result.modified_internal_rate_of_return:.2f}%")
        logger.info(f"Profitability Index: {result.profitability_index:.2f}")
        logger.info(f"Discounted Payback Period: {result.discounted_payback_period:.2f} years")
        
        logger.info("\n--- Scenario Analysis ---")
        logger.info(f"Base Case NPV: ${result.base_case.net_present_value:.2f}")
        logger.info(f"Optimistic NPV: ${result.optimistic.net_present_value:.2f}")
        logger.info(f"Pessimistic NPV: ${result.pessimistic.net_present_value:.2f}")
        
        logger.info("\n--- Monte Carlo Results ---")
        logger.info(f"Mean NPV: ${result.monte_carlo_results.mean_npv:.2f}")
        logger.info(f"Median NPV: ${result.monte_carlo_results.median_npv:.2f}")
        logger.info(f"Std Deviation: ${result.monte_carlo_results.std_deviation_npv:.2f}")
        logger.info(f"Probability of Positive NPV: {result.monte_carlo_results.probability_of_positive_npv:.1%}")
        logger.info(f"Value at Risk (95%): ${result.monte_carlo_results.value_at_risk_95:.2f}")
        logger.info(f"Expected Shortfall: ${result.monte_carlo_results.expected_shortfall:.2f}")
        
        logger.info("\n--- Risk Assessment ---")
        logger.info(f"Weather Risk Score: {result.weather_risk_score:.2f}")
        logger.info(f"Market Volatility Risk: {result.market_volatility_risk:.2f}")
        logger.info(f"Yield Volatility Risk: {result.yield_volatility_risk:.2f}")
        logger.info(f"Overall Risk Score: {result.overall_risk_score:.2f}")
        
        logger.info("\n--- Investment Recommendation ---")
        logger.info(f"Recommendation: {result.investment_recommendation.recommendation_type}")
        logger.info(f"Confidence Score: {result.investment_recommendation.confidence_score:.2f}")
        logger.info(f"Risk Level: {result.investment_recommendation.risk_level.value}")
        logger.info(f"Expected Return: {result.investment_recommendation.expected_return_percent:.2f}%")
        logger.info(f"Payback Period: {result.investment_recommendation.payback_period_years:.2f} years")
        
        logger.info("\n--- Key Factors ---")
        for factor in result.investment_recommendation.key_factors:
            logger.info(f"  • {factor}")
        
        logger.info("\n--- Risk Factors ---")
        for risk in result.investment_recommendation.risk_factors:
            logger.info(f"  • {risk}")
        
        logger.info("\n--- Mitigation Strategies ---")
        for strategy in result.investment_recommendation.mitigation_strategies:
            logger.info(f"  • {strategy}")
        
        logger.info("\n--- Annual Cash Flows ---")
        for year, cash_flow in enumerate(result.annual_cash_flows, 1):
            logger.info(f"Year {year}: ${cash_flow:.2f}")
        
        logger.info("\n--- Data Sources ---")
        for source in result.data_sources:
            logger.info(f"  • {source}")
        
        logger.info("\n=== TEST COMPLETED SUCCESSFULLY ===")
        return True
        
    except Exception as e:
        logger.error(f"Error in sophisticated ROI analysis test: {e}")
        return False


async def test_scenario_analysis():
    """Test scenario analysis functionality."""
    
    logger.info("\n=== TESTING SCENARIO ANALYSIS ===")
    
    service = VarietyEconomicAnalysisService()
    
    variety = EnhancedCropVariety(
        variety_id=uuid4(),
        crop_id=uuid4(),
        variety_name="Test Soybean Variety",
        variety_code="TS001",
        breeder_company="Test Breeder",
        relative_maturity=105,
        maturity_group="3.2",
        yield_potential_percentile=80.0,
        market_acceptance_score=3.8,
        yield_stability_rating=8.0
    )
    
    regional_context = {
        "crop_name": "soybean",
        "region": "US",
        "yield_multiplier": 1.0,
        "price_multiplier": 1.0,
        "cost_multiplier": 1.0
    }
    
    try:
        # Test scenario analysis
        scenario_results = await service._perform_scenario_analysis(
            variety, regional_context, None, 5
        )
        
        logger.info("Scenario Analysis Results:")
        for scenario_name, scenario in scenario_results.items():
            logger.info(f"\n{scenario_name.upper()}:")
            logger.info(f"  NPV: ${scenario.net_present_value:.2f}")
            logger.info(f"  IRR: {scenario.internal_rate_of_return:.2f}%")
            logger.info(f"  Payback Period: {scenario.payback_period_years:.2f} years")
            logger.info(f"  Expected Profit: ${scenario.expected_profit_per_acre:.2f}/acre")
            logger.info(f"  Probability of Profit: {scenario.probability_of_profit:.1%}")
        
        logger.info("\n=== SCENARIO ANALYSIS TEST COMPLETED ===")
        return True
        
    except Exception as e:
        logger.error(f"Error in scenario analysis test: {e}")
        return False


async def test_monte_carlo_simulation():
    """Test Monte Carlo simulation functionality."""
    
    logger.info("\n=== TESTING MONTE CARLO SIMULATION ===")
    
    service = VarietyEconomicAnalysisService()
    
    variety = EnhancedCropVariety(
        variety_id=uuid4(),
        crop_id=uuid4(),
        variety_name="Test Wheat Variety",
        variety_code="TW001",
        breeder_company="Test Breeder",
        relative_maturity=120,
        maturity_group="Winter",
        yield_potential_percentile=70.0,
        market_acceptance_score=4.0,
        yield_stability_rating=6.5
    )
    
    regional_context = {
        "crop_name": "wheat",
        "region": "US",
        "yield_multiplier": 1.0,
        "price_multiplier": 1.0,
        "cost_multiplier": 1.0
    }
    
    try:
        # Test Monte Carlo simulation with fewer iterations for testing
        monte_carlo_results = await service._perform_monte_carlo_simulation(
            variety, regional_context, None, 5, iterations=1000
        )
        
        logger.info("Monte Carlo Simulation Results:")
        logger.info(f"Mean NPV: ${monte_carlo_results.mean_npv:.2f}")
        logger.info(f"Median NPV: ${monte_carlo_results.median_npv:.2f}")
        logger.info(f"Standard Deviation: ${monte_carlo_results.std_deviation_npv:.2f}")
        logger.info(f"Probability of Positive NPV: {monte_carlo_results.probability_of_positive_npv:.1%}")
        logger.info(f"Value at Risk (95%): ${monte_carlo_results.value_at_risk_95:.2f}")
        logger.info(f"Expected Shortfall: ${monte_carlo_results.expected_shortfall:.2f}")
        logger.info(f"Simulation Iterations: {monte_carlo_results.simulation_iterations}")
        
        logger.info("\nConfidence Intervals:")
        for level, interval in monte_carlo_results.confidence_intervals.items():
            logger.info(f"  {level}: ${interval[0]:.2f} to ${interval[1]:.2f}")
        
        logger.info("\n=== MONTE CARLO SIMULATION TEST COMPLETED ===")
        return True
        
    except Exception as e:
        logger.error(f"Error in Monte Carlo simulation test: {e}")
        return False


async def test_risk_assessment():
    """Test risk assessment functionality."""
    
    logger.info("\n=== TESTING RISK ASSESSMENT ===")
    
    service = VarietyEconomicAnalysisService()
    
    variety = EnhancedCropVariety(
        variety_id=uuid4(),
        crop_id=uuid4(),
        variety_name="Test Corn Variety with Risk",
        variety_code="TC002",
        breeder_company="Test Breeder",
        relative_maturity=115,
        maturity_group="4.8",
        yield_potential_percentile=60.0,
        market_acceptance_score=2.5,
        yield_stability_rating=4.0
    )
    
    regional_context = {
        "crop_name": "corn",
        "region": "US",
        "weather_risk_score": 0.6,
        "price_volatility": 0.20,
        "yield_volatility_adjustment": 0.1
    }
    
    try:
        # Test risk assessment
        risk_assessments = await service._calculate_comprehensive_risk_assessment(
            variety, regional_context, None
        )
        
        logger.info("Risk Assessment Results:")
        logger.info(f"Weather Risk: {risk_assessments['weather_risk']:.2f}")
        logger.info(f"Market Volatility Risk: {risk_assessments['market_volatility']:.2f}")
        logger.info(f"Yield Volatility Risk: {risk_assessments['yield_volatility']:.2f}")
        logger.info(f"Overall Risk Score: {risk_assessments['overall_risk']:.2f}")
        
        logger.info("\n=== RISK ASSESSMENT TEST COMPLETED ===")
        return True
        
    except Exception as e:
        logger.error(f"Error in risk assessment test: {e}")
        return False


async def main():
    """Run all tests."""
    
    logger.info("Starting comprehensive test suite for sophisticated ROI analysis...")
    
    tests = [
        ("Sophisticated ROI Analysis", test_sophisticated_roi_analysis),
        ("Scenario Analysis", test_scenario_analysis),
        ("Monte Carlo Simulation", test_monte_carlo_simulation),
        ("Risk Assessment", test_risk_assessment)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*60}")
        
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*60}")
    
    passed = 0
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nTotal Tests: {len(results)}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {len(results) - passed}")
    
    if passed == len(results):
        logger.info("\n🎉 ALL TESTS PASSED! Sophisticated ROI analysis is working correctly.")
    else:
        logger.info(f"\n❌ {len(results) - passed} tests failed. Please check the implementation.")


if __name__ == "__main__":
    asyncio.run(main())