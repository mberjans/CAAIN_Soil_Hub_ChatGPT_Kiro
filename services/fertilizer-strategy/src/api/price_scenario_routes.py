"""
API routes for comprehensive price scenario modeling system.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
import logging

from ..models.price_scenario_models import (
    PriceScenarioModelingRequest, PriceScenarioModelingResponse,
    ScenarioType, MarketCondition, RiskLevel
)
from ..services.price_scenario_modeling_service import PriceScenarioModelingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/price-scenarios", tags=["price-scenarios"])


# Dependency injection
async def get_scenario_modeling_service() -> PriceScenarioModelingService:
    """Get price scenario modeling service instance."""
    return PriceScenarioModelingService()


@router.post("/comprehensive-modeling", response_model=PriceScenarioModelingResponse)
async def create_comprehensive_scenario_model(
    request: PriceScenarioModelingRequest,
    background_tasks: BackgroundTasks,
    service: PriceScenarioModelingService = Depends(get_scenario_modeling_service)
):
    """
    Create comprehensive price scenario model with advanced forecasting.
    
    This endpoint provides comprehensive price scenario modeling including:
    - Multiple price scenarios (bull market, bear market, volatile market, seasonal patterns, supply disruptions)
    - Monte Carlo simulation for price forecasting
    - Stochastic modeling and sensitivity analysis
    - Decision trees for scenario planning
    - Probability modeling and risk assessment
    
    Agricultural Use Cases:
    - Strategic fertilizer purchasing decisions
    - Risk management and hedging strategies
    - Long-term farm planning and budgeting
    - Market timing optimization
    - Supply chain risk assessment
    """
    try:
        logger.info(f"Creating comprehensive scenario model for analysis {request.analysis_id}")
        
        # Validate request
        if not request.fertilizer_requirements:
            raise HTTPException(status_code=400, detail="Fertilizer requirements are required")
        
        # Create comprehensive scenario model
        response = await service.create_comprehensive_scenario_model(request)
        
        logger.info(f"Scenario modeling completed successfully for analysis {request.analysis_id}")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in scenario modeling: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in comprehensive scenario modeling: {e}")
        raise HTTPException(status_code=500, detail="Failed to create scenario model")


@router.post("/quick-scenario-analysis", response_model=PriceScenarioModelingResponse)
async def create_quick_scenario_analysis(
    request: PriceScenarioModelingRequest,
    service: PriceScenarioModelingService = Depends(get_scenario_modeling_service)
):
    """
    Create quick scenario analysis with essential scenarios only.
    
    This endpoint provides a faster analysis focusing on the most important scenarios:
    - Baseline scenario
    - Optimistic scenario (bull market)
    - Pessimistic scenario (bear market)
    - Volatile market scenario
    
    Use this for quick decision-making when comprehensive analysis is not needed.
    """
    try:
        logger.info(f"Creating quick scenario analysis for analysis {request.analysis_id}")
        
        # Override scenarios for quick analysis
        request.scenarios = [
            ScenarioType.BASELINE,
            ScenarioType.BULL_MARKET,
            ScenarioType.BEAR_MARKET,
            ScenarioType.VOLATILE_MARKET
        ]
        
        # Reduce Monte Carlo iterations for faster processing
        request.monte_carlo_iterations = 5000
        
        # Create scenario model
        response = await service.create_comprehensive_scenario_model(request)
        
        logger.info(f"Quick scenario analysis completed for analysis {request.analysis_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error in quick scenario analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to create quick scenario analysis")


@router.post("/seasonal-scenario-analysis", response_model=PriceScenarioModelingResponse)
async def create_seasonal_scenario_analysis(
    request: PriceScenarioModelingRequest,
    service: PriceScenarioModelingService = Depends(get_scenario_modeling_service)
):
    """
    Create seasonal scenario analysis focusing on seasonal price patterns.
    
    This endpoint provides analysis focused on seasonal variations:
    - Spring planting season scenarios
    - Summer growing season scenarios
    - Fall harvest season scenarios
    - Winter planning season scenarios
    
    Agricultural Use Cases:
    - Seasonal fertilizer purchasing timing
    - Planting season cost planning
    - Harvest season revenue planning
    - Winter planning and budgeting
    """
    try:
        logger.info(f"Creating seasonal scenario analysis for analysis {request.analysis_id}")
        
        # Override scenarios for seasonal analysis
        request.scenarios = [
            ScenarioType.BASELINE,
            ScenarioType.SEASONAL_PATTERNS,
            ScenarioType.VOLATILE_MARKET
        ]
        
        # Create scenario model
        response = await service.create_comprehensive_scenario_model(request)
        
        logger.info(f"Seasonal scenario analysis completed for analysis {request.analysis_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error in seasonal scenario analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to create seasonal scenario analysis")


@router.post("/supply-disruption-analysis", response_model=PriceScenarioModelingResponse)
async def create_supply_disruption_analysis(
    request: PriceScenarioModelingRequest,
    service: PriceScenarioModelingService = Depends(get_scenario_modeling_service)
):
    """
    Create supply disruption scenario analysis for risk assessment.
    
    This endpoint provides analysis focused on supply chain disruptions:
    - Supply disruption scenarios
    - Price spike scenarios
    - Alternative supplier scenarios
    - Contingency planning scenarios
    
    Agricultural Use Cases:
    - Supply chain risk assessment
    - Contingency planning
    - Alternative supplier evaluation
    - Emergency procurement planning
    """
    try:
        logger.info(f"Creating supply disruption analysis for analysis {request.analysis_id}")
        
        # Override scenarios for supply disruption analysis
        request.scenarios = [
            ScenarioType.BASELINE,
            ScenarioType.SUPPLY_DISRUPTION,
            ScenarioType.VOLATILE_MARKET,
            ScenarioType.BEAR_MARKET
        ]
        
        # Create scenario model
        response = await service.create_comprehensive_scenario_model(request)
        
        logger.info(f"Supply disruption analysis completed for analysis {request.analysis_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error in supply disruption analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to create supply disruption analysis")


@router.get("/scenario-types")
async def get_available_scenario_types():
    """
    Get available scenario types for price scenario modeling.
    
    Returns all available scenario types with descriptions and use cases.
    """
    scenario_types = [
        {
            "type": ScenarioType.BULL_MARKET.value,
            "name": "Bull Market Scenario",
            "description": "Strong economic growth with high commodity prices and moderate fertilizer costs",
            "use_cases": ["Strategic planning", "Growth scenarios", "Optimistic planning"],
            "risk_level": RiskLevel.LOW.value
        },
        {
            "type": ScenarioType.BEAR_MARKET.value,
            "name": "Bear Market Scenario",
            "description": "Economic downturn with low commodity prices and reduced fertilizer demand",
            "use_cases": ["Risk assessment", "Conservative planning", "Downturn scenarios"],
            "risk_level": RiskLevel.HIGH.value
        },
        {
            "type": ScenarioType.VOLATILE_MARKET.value,
            "name": "Volatile Market Scenario",
            "description": "High price volatility with uncertain market conditions",
            "use_cases": ["Risk management", "Volatility planning", "Uncertainty scenarios"],
            "risk_level": RiskLevel.HIGH.value
        },
        {
            "type": ScenarioType.SEASONAL_PATTERNS.value,
            "name": "Seasonal Patterns Scenario",
            "description": "Seasonal price variations based on planting and harvest cycles",
            "use_cases": ["Seasonal planning", "Timing optimization", "Cyclical patterns"],
            "risk_level": RiskLevel.MEDIUM.value
        },
        {
            "type": ScenarioType.SUPPLY_DISRUPTION.value,
            "name": "Supply Disruption Scenario",
            "description": "Supply chain disruptions leading to fertilizer shortages and price spikes",
            "use_cases": ["Contingency planning", "Risk mitigation", "Emergency scenarios"],
            "risk_level": RiskLevel.CRITICAL.value
        },
        {
            "type": ScenarioType.BASELINE.value,
            "name": "Baseline Scenario",
            "description": "Current market conditions with moderate price stability",
            "use_cases": ["Baseline planning", "Current conditions", "Reference scenario"],
            "risk_level": RiskLevel.LOW.value
        },
        {
            "type": ScenarioType.CUSTOM.value,
            "name": "Custom Scenario",
            "description": "User-defined scenario with custom parameters",
            "use_cases": ["Custom planning", "Specific conditions", "Tailored scenarios"],
            "risk_level": RiskLevel.MEDIUM.value
        }
    ]
    
    return {
        "scenario_types": scenario_types,
        "total_count": len(scenario_types)
    }


@router.get("/market-conditions")
async def get_available_market_conditions():
    """
    Get available market conditions for price scenario modeling.
    
    Returns all available market conditions with descriptions.
    """
    market_conditions = [
        {
            "condition": MarketCondition.BULL_MARKET.value,
            "name": "Bull Market",
            "description": "Strong upward price trends with high demand"
        },
        {
            "condition": MarketCondition.BEAR_MARKET.value,
            "name": "Bear Market",
            "description": "Downward price trends with low demand"
        },
        {
            "condition": MarketCondition.VOLATILE.value,
            "name": "Volatile Market",
            "description": "High price volatility with uncertain trends"
        },
        {
            "condition": MarketCondition.STABLE.value,
            "name": "Stable Market",
            "description": "Moderate price stability with consistent demand"
        },
        {
            "condition": MarketCondition.SEASONAL.value,
            "name": "Seasonal Market",
            "description": "Seasonal price variations based on agricultural cycles"
        },
        {
            "condition": MarketCondition.SUPPLY_DISRUPTION.value,
            "name": "Supply Disruption",
            "description": "Supply chain disruptions affecting availability and prices"
        },
        {
            "condition": MarketCondition.CUSTOM.value,
            "name": "Custom Condition",
            "description": "User-defined market condition"
        }
    ]
    
    return {
        "market_conditions": market_conditions,
        "total_count": len(market_conditions)
    }


@router.get("/risk-levels")
async def get_available_risk_levels():
    """
    Get available risk levels for price scenario modeling.
    
    Returns all available risk levels with descriptions.
    """
    risk_levels = [
        {
            "level": RiskLevel.LOW.value,
            "name": "Low Risk",
            "description": "Minimal risk with stable conditions",
            "color": "green"
        },
        {
            "level": RiskLevel.MEDIUM.value,
            "name": "Medium Risk",
            "description": "Moderate risk with some uncertainty",
            "color": "yellow"
        },
        {
            "level": RiskLevel.HIGH.value,
            "name": "High Risk",
            "description": "Significant risk with high uncertainty",
            "color": "orange"
        },
        {
            "level": RiskLevel.CRITICAL.value,
            "name": "Critical Risk",
            "description": "Extreme risk requiring immediate attention",
            "color": "red"
        }
    ]
    
    return {
        "risk_levels": risk_levels,
        "total_count": len(risk_levels)
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for price scenario modeling service."""
    return {
        "status": "healthy",
        "service": "price-scenario-modeling",
        "version": "1.0.0",
        "features": [
            "comprehensive_scenario_modeling",
            "monte_carlo_simulation",
            "stochastic_modeling",
            "sensitivity_analysis",
            "decision_trees",
            "risk_assessment"
        ]
    }