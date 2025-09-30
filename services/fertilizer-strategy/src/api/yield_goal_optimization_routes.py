"""
API routes for comprehensive yield goal optimization.

This module provides REST API endpoints for:
- Yield goal optimization with economic constraints
- Goal-oriented fertilizer planning
- Risk-adjusted optimization and scenario analysis
- Multi-criteria optimization (goal programming, robust optimization)
- Integration with yield response curves and economic analysis
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
import logging
from uuid import UUID

from ..models.yield_goal_models import (
    YieldGoalRequest, YieldGoalAnalysis, YieldGoalRecommendation,
    YieldGoalType, YieldRiskLevel, HistoricalYieldData,
    SoilCharacteristic, WeatherPattern, ManagementPractice
)
from ..models.yield_response_models import (
    YieldResponseCurve, NutrientResponseData, ResponseModelType
)
from ..models.price_models import FertilizerPriceData
from ..services.yield_goal_optimization_service import (
    YieldGoalOptimizationService, YieldGoalOptimizationRequest,
    YieldGoalOptimizationResponse, OptimizationObjective, OptimizationMethod,
    OptimizationConstraints, OptimizationScenario, ScenarioType,
    FertilizerStrategy
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/yield-goal-optimization", tags=["yield-goal-optimization"])

# Dependency injection
async def get_yield_goal_optimization_service() -> YieldGoalOptimizationService:
    """Get yield goal optimization service instance."""
    return YieldGoalOptimizationService()


@router.post("/optimize", response_model=YieldGoalOptimizationResponse)
async def optimize_yield_goals(
    request: YieldGoalOptimizationRequest,
    background_tasks: BackgroundTasks,
    service: YieldGoalOptimizationService = Depends(get_yield_goal_optimization_service)
):
    """
    Perform comprehensive yield goal optimization.
    
    This endpoint provides advanced yield goal optimization including:
    - Goal-oriented fertilizer planning with economic constraints
    - Risk-adjusted optimization and scenario analysis
    - Multi-criteria optimization (goal programming, robust optimization)
    - Integration with yield response curves and economic analysis
    - Optimal fertilizer strategies with goal achievement probability
    
    Agricultural Use Cases:
    - Optimize fertilizer rates to achieve specific yield goals
    - Balance yield targets with economic constraints
    - Assess risk-adjusted fertilizer strategies
    - Compare different optimization approaches
    - Generate scenario-based recommendations
    """
    try:
        logger.info(f"Starting yield goal optimization for field {request.field_id}")
        
        # Perform comprehensive optimization
        response = await service.optimize_yield_goals(request)
        
        # Add background task for logging/storage if needed
        background_tasks.add_task(
            _log_optimization_completion,
            request.field_id,
            request.crop_type,
            request.yield_goal,
            len(request.scenarios)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in yield goal optimization: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Yield goal optimization failed: {str(e)}"
        )


@router.post("/quick-optimize", response_model=YieldGoalOptimizationResponse)
async def quick_yield_goal_optimization(
    field_id: UUID = Query(..., description="Field identifier"),
    crop_type: str = Query(..., description="Type of crop"),
    yield_goal: float = Query(..., ge=0.0, description="Target yield goal"),
    crop_price: float = Query(..., ge=0.0, description="Crop price ($/bu)"),
    budget_limit: float = Query(200.0, ge=0.0, description="Budget limit ($/acre)"),
    optimization_objective: OptimizationObjective = Query(OptimizationObjective.BALANCED, description="Optimization objective"),
    optimization_method: OptimizationMethod = Query(OptimizationMethod.MULTI_CRITERIA, description="Optimization method"),
    risk_tolerance: YieldRiskLevel = Query(YieldRiskLevel.MEDIUM, description="Risk tolerance level"),
    service: YieldGoalOptimizationService = Depends(get_yield_goal_optimization_service)
):
    """
    Quick yield goal optimization with minimal input data.
    
    This endpoint provides a simplified optimization using:
    - Default fertilizer prices and response curves
    - Single baseline scenario
    - Standard constraints and parameters
    
    Agricultural Use Cases:
    - Quick fertilizer optimization for new fields
    - Initial strategy assessment
    - Rapid optimization for planning purposes
    """
    try:
        logger.info(f"Starting quick yield goal optimization for field {field_id}")
        
        # Create default constraints
        constraints = OptimizationConstraints(
            max_nitrogen_rate=300.0,
            max_phosphorus_rate=150.0,
            max_potassium_rate=200.0,
            budget_limit=budget_limit
        )
        
        # Create default price scenario
        price_scenario = {
            'nitrogen': 0.80,
            'phosphorus': 0.60,
            'potassium': 0.50
        }
        
        # Create baseline scenario
        baseline_scenario = OptimizationScenario(
            scenario_type=ScenarioType.BASELINE,
            yield_goal=yield_goal,
            price_scenario=price_scenario,
            risk_tolerance=risk_tolerance,
            probability_weight=1.0
        )
        
        # Create default yield response curves
        response_curves = [
            YieldResponseCurve(
                curve_id=UUID("00000000-0000-0000-0000-000000000001"),
                field_id=field_id,
                crop_type=crop_type,
                nutrient_type="nitrogen",
                curve_type=ResponseModelType.QUADRATIC_PLATEAU,
                base_yield=100.0,
                max_yield_response=80.0,
                response_coefficient=0.8,
                diminishing_returns_coefficient=0.001,
                confidence_level=0.8,
                data_points=[],
                model_parameters={}
            ),
            YieldResponseCurve(
                curve_id=UUID("00000000-0000-0000-0000-000000000002"),
                field_id=field_id,
                crop_type=crop_type,
                nutrient_type="phosphorus",
                curve_type=ResponseModelType.QUADRATIC_PLATEAU,
                base_yield=100.0,
                max_yield_response=40.0,
                response_coefficient=0.6,
                diminishing_returns_coefficient=0.002,
                confidence_level=0.7,
                data_points=[],
                model_parameters={}
            ),
            YieldResponseCurve(
                curve_id=UUID("00000000-0000-0000-0000-000000000003"),
                field_id=field_id,
                crop_type=crop_type,
                nutrient_type="potassium",
                curve_type=ResponseModelType.QUADRATIC_PLATEAU,
                base_yield=100.0,
                max_yield_response=30.0,
                response_coefficient=0.4,
                diminishing_returns_coefficient=0.0015,
                confidence_level=0.6,
                data_points=[],
                model_parameters={}
            )
        ]
        
        # Create default fertilizer prices
        fertilizer_prices = [
            FertilizerPriceData(
                fertilizer_type="nitrogen",
                price_per_unit=0.80,
                unit="lb",
                region="default",
                source="default",
                price_date="2024-01-01"
            ),
            FertilizerPriceData(
                fertilizer_type="phosphorus",
                price_per_unit=0.60,
                unit="lb",
                region="default",
                source="default",
                price_date="2024-01-01"
            ),
            FertilizerPriceData(
                fertilizer_type="potassium",
                price_per_unit=0.50,
                unit="lb",
                region="default",
                source="default",
                price_date="2024-01-01"
            )
        ]
        
        # Create optimization request
        optimization_request = YieldGoalOptimizationRequest(
            field_id=field_id,
            crop_type=crop_type,
            yield_goal=yield_goal,
            optimization_objective=optimization_objective,
            optimization_method=optimization_method,
            constraints=constraints,
            scenarios=[baseline_scenario],
            yield_response_curves=response_curves,
            fertilizer_prices=fertilizer_prices,
            crop_price=crop_price
        )
        
        # Perform optimization
        response = await service.optimize_yield_goals(optimization_request)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in quick yield goal optimization: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Quick yield goal optimization failed: {str(e)}"
        )


@router.post("/scenario-analysis", response_model=YieldGoalOptimizationResponse)
async def scenario_analysis_optimization(
    field_id: UUID = Query(..., description="Field identifier"),
    crop_type: str = Query(..., description="Type of crop"),
    yield_goal: float = Query(..., ge=0.0, description="Target yield goal"),
    crop_price: float = Query(..., ge=0.0, description="Crop price ($/bu)"),
    budget_limit: float = Query(200.0, ge=0.0, description="Budget limit ($/acre)"),
    optimization_method: OptimizationMethod = Query(OptimizationMethod.MULTI_CRITERIA, description="Optimization method"),
    service: YieldGoalOptimizationService = Depends(get_yield_goal_optimization_service)
):
    """
    Perform scenario analysis optimization with multiple scenarios.
    
    This endpoint provides comprehensive scenario analysis including:
    - Baseline, optimistic, and pessimistic scenarios
    - Different price and weather conditions
    - Risk-adjusted optimization across scenarios
    - Comparative analysis of strategies
    
    Agricultural Use Cases:
    - Assess strategy robustness across different conditions
    - Evaluate risk-return trade-offs
    - Plan for different market and weather scenarios
    - Make informed decisions under uncertainty
    """
    try:
        logger.info(f"Starting scenario analysis optimization for field {field_id}")
        
        # Create constraints
        constraints = OptimizationConstraints(
            max_nitrogen_rate=300.0,
            max_phosphorus_rate=150.0,
            max_potassium_rate=200.0,
            budget_limit=budget_limit
        )
        
        # Create multiple scenarios
        scenarios = [
            # Baseline scenario
            OptimizationScenario(
                scenario_type=ScenarioType.BASELINE,
                yield_goal=yield_goal,
                price_scenario={
                    'nitrogen': 0.80,
                    'phosphorus': 0.60,
                    'potassium': 0.50
                },
                risk_tolerance=YieldRiskLevel.MEDIUM,
                probability_weight=0.5
            ),
            # Optimistic scenario
            OptimizationScenario(
                scenario_type=ScenarioType.OPTIMISTIC,
                yield_goal=yield_goal * 1.1,  # 10% higher yield goal
                price_scenario={
                    'nitrogen': 0.70,  # Lower fertilizer prices
                    'phosphorus': 0.50,
                    'potassium': 0.40
                },
                risk_tolerance=YieldRiskLevel.LOW,
                probability_weight=0.2
            ),
            # Pessimistic scenario
            OptimizationScenario(
                scenario_type=ScenarioType.PESSIMISTIC,
                yield_goal=yield_goal * 0.9,  # 10% lower yield goal
                price_scenario={
                    'nitrogen': 0.90,  # Higher fertilizer prices
                    'phosphorus': 0.70,
                    'potassium': 0.60
                },
                risk_tolerance=YieldRiskLevel.HIGH,
                probability_weight=0.3
            )
        ]
        
        # Create default yield response curves
        response_curves = [
            YieldResponseCurve(
                curve_id=UUID("00000000-0000-0000-0000-000000000001"),
                field_id=field_id,
                crop_type=crop_type,
                nutrient_type="nitrogen",
                curve_type=ResponseModelType.QUADRATIC_PLATEAU,
                base_yield=100.0,
                max_yield_response=80.0,
                response_coefficient=0.8,
                diminishing_returns_coefficient=0.001,
                confidence_level=0.8,
                data_points=[],
                model_parameters={}
            ),
            YieldResponseCurve(
                curve_id=UUID("00000000-0000-0000-0000-000000000002"),
                field_id=field_id,
                crop_type=crop_type,
                nutrient_type="phosphorus",
                curve_type=ResponseModelType.QUADRATIC_PLATEAU,
                base_yield=100.0,
                max_yield_response=40.0,
                response_coefficient=0.6,
                diminishing_returns_coefficient=0.002,
                confidence_level=0.7,
                data_points=[],
                model_parameters={}
            ),
            YieldResponseCurve(
                curve_id=UUID("00000000-0000-0000-0000-000000000003"),
                field_id=field_id,
                crop_type=crop_type,
                nutrient_type="potassium",
                curve_type=ResponseModelType.QUADRATIC_PLATEAU,
                base_yield=100.0,
                max_yield_response=30.0,
                response_coefficient=0.4,
                diminishing_returns_coefficient=0.0015,
                confidence_level=0.6,
                data_points=[],
                model_parameters={}
            )
        ]
        
        # Create default fertilizer prices
        fertilizer_prices = [
            FertilizerPriceData(
                fertilizer_type="nitrogen",
                price_per_unit=0.80,
                unit="lb",
                region="default",
                source="default",
                price_date="2024-01-01"
            ),
            FertilizerPriceData(
                fertilizer_type="phosphorus",
                price_per_unit=0.60,
                unit="lb",
                region="default",
                source="default",
                price_date="2024-01-01"
            ),
            FertilizerPriceData(
                fertilizer_type="potassium",
                price_per_unit=0.50,
                unit="lb",
                region="default",
                source="default",
                price_date="2024-01-01"
            )
        ]
        
        # Create optimization request
        optimization_request = YieldGoalOptimizationRequest(
            field_id=field_id,
            crop_type=crop_type,
            yield_goal=yield_goal,
            optimization_objective=OptimizationObjective.BALANCED,
            optimization_method=optimization_method,
            constraints=constraints,
            scenarios=scenarios,
            yield_response_curves=response_curves,
            fertilizer_prices=fertilizer_prices,
            crop_price=crop_price
        )
        
        # Perform optimization
        response = await service.optimize_yield_goals(optimization_request)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in scenario analysis optimization: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Scenario analysis optimization failed: {str(e)}"
        )


@router.get("/optimization-methods", response_model=Dict[str, Any])
async def get_optimization_methods():
    """
    Get available optimization methods and their characteristics.
    
    Returns information about different optimization approaches:
    - Goal Programming: Minimize deviations from goals
    - Multi-Criteria: Balance multiple objectives
    - Robust Optimization: Handle uncertainty
    - Stochastic: Monte Carlo simulation
    - Genetic Algorithm: Evolutionary optimization
    """
    return {
        "optimization_methods": {
            "goal_programming": {
                "description": "Minimize deviations from yield and cost goals",
                "best_for": "Specific target achievement",
                "strengths": ["Clear goal focus", "Handles multiple constraints"],
                "limitations": ["May not find global optimum", "Sensitive to goal weights"]
            },
            "multi_criteria": {
                "description": "Balance multiple objectives (yield, profit, cost)",
                "best_for": "Balanced optimization",
                "strengths": ["Flexible objective weighting", "Good for trade-off analysis"],
                "limitations": ["Requires objective prioritization", "May not handle uncertainty well"]
            },
            "robust_optimization": {
                "description": "Optimize under uncertainty and worst-case scenarios",
                "best_for": "Risk-averse farmers",
                "strengths": ["Handles uncertainty", "Conservative approach"],
                "limitations": ["May be overly conservative", "Computationally intensive"]
            },
            "stochastic": {
                "description": "Monte Carlo simulation with random sampling",
                "best_for": "Risk assessment and probability analysis",
                "strengths": ["Comprehensive risk analysis", "Probability distributions"],
                "limitations": ["Computationally intensive", "Requires distribution assumptions"]
            },
            "genetic_algorithm": {
                "description": "Evolutionary optimization inspired by natural selection",
                "best_for": "Complex, non-linear problems",
                "strengths": ["Global optimization", "Handles complex constraints"],
                "limitations": ["Computationally intensive", "May not converge quickly"]
            }
        },
        "optimization_objectives": {
            "maximize_profit": "Focus on profit maximization",
            "minimize_cost": "Focus on cost minimization",
            "maximize_yield": "Focus on yield maximization",
            "minimize_risk": "Focus on risk minimization",
            "balanced": "Balance multiple objectives"
        },
        "scenario_types": {
            "baseline": "Normal conditions scenario",
            "optimistic": "Favorable conditions scenario",
            "pessimistic": "Unfavorable conditions scenario",
            "stress_test": "Extreme conditions scenario"
        }
    }


@router.get("/optimization-parameters", response_model=Dict[str, Any])
async def get_optimization_parameters():
    """
    Get default optimization parameters and constraints.
    
    Returns typical parameter ranges and constraints used in optimization:
    - Fertilizer rate limits
    - Budget constraints
    - Risk parameters
    - Economic assumptions
    """
    return {
        "default_constraints": {
            "max_nitrogen_rate": 300.0,
            "max_phosphorus_rate": 150.0,
            "max_potassium_rate": 200.0,
            "budget_limit": 200.0,
            "description": "Typical fertilizer rate and budget constraints"
        },
        "default_prices": {
            "nitrogen": 0.80,
            "phosphorus": 0.60,
            "potassium": 0.50,
            "unit": "$/lb",
            "description": "Typical fertilizer prices per pound of nutrient"
        },
        "crop_prices": {
            "corn": 5.50,
            "soybean": 13.00,
            "wheat": 7.00,
            "cotton": 0.70,
            "rice": 0.12,
            "unit": "$/bu or $/lb",
            "description": "Typical crop prices"
        },
        "risk_parameters": {
            "yield_volatility": 0.15,
            "price_volatility": 0.20,
            "confidence_levels": [0.5, 0.75, 0.9, 0.95],
            "description": "Default risk and uncertainty parameters"
        },
        "optimization_settings": {
            "max_iterations": 1000,
            "population_size": 50,
            "tolerance": 1e-6,
            "description": "Default optimization algorithm settings"
        }
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for yield goal optimization service."""
    return {
        "service": "yield-goal-optimization",
        "status": "healthy",
        "features": [
            "goal_oriented_fertilizer_planning",
            "economic_constraint_optimization",
            "risk_adjusted_optimization",
            "scenario_analysis",
            "multi_criteria_optimization",
            "goal_programming",
            "robust_optimization",
            "stochastic_optimization",
            "genetic_algorithm_optimization",
            "yield_response_curve_integration",
            "economic_analysis_integration",
            "sensitivity_analysis",
            "risk_assessment",
            "optimal_strategy_recommendations",
            "achievement_probability_calculation",
            "profit_probability_calculation",
            "comprehensive_scenario_modeling"
        ]
    }


# Background task functions
async def _log_optimization_completion(field_id: UUID, crop_type: str, yield_goal: float, scenario_count: int):
    """Log optimization completion for monitoring and analytics."""
    logger.info(f"Yield goal optimization completed for field {field_id}, crop {crop_type}, goal {yield_goal}, scenarios {scenario_count}")
    # In a real implementation, this would:
    # - Store optimization results in database
    # - Update analytics metrics
    # - Send notifications if configured
    # - Trigger downstream processes