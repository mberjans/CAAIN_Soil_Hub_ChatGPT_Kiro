"""
Economic Optimization API Routes for Fertilizer Strategy Optimization Service.

This module provides comprehensive API endpoints for economic optimization and scenario modeling,
including multi-objective optimization, risk assessment, sensitivity analysis, and Monte Carlo simulation.
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
import time

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from pydantic import BaseModel, Field

from ..models.economic_optimization_models import (
    EconomicOptimizationRequest,
    EconomicOptimizationResponse,
    EconomicScenario,
    ScenarioType,
    MarketCondition,
    OptimizationResult,
    MultiObjectiveOptimization,
    RiskAssessment,
    SensitivityAnalysis,
    MonteCarloSimulation,
    ScenarioModeling,
    BudgetAllocation,
    InvestmentPrioritization,
    ROIAnalysis,
    BreakEvenAnalysis,
    PaybackPeriod,
    OpportunityCost,
    EconomicImpact,
    ConstraintRelaxation,
    ParetoFrontier,
    TradeOffAnalysis
)
from ..services.economic_optimizer import EconomicOptimizer
from ..exceptions import EconomicOptimizationError, ProviderError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/economic-optimization", tags=["economic-optimization"])

# Dependency injection
async def get_economic_optimizer() -> EconomicOptimizer:
    """Get economic optimizer service instance."""
    return EconomicOptimizer()


@router.post("/optimize-strategy", response_model=EconomicOptimizationResponse)
async def optimize_fertilizer_strategy(
    request: EconomicOptimizationRequest = Body(...),
    service: EconomicOptimizer = Depends(get_economic_optimizer)
):
    """
    Optimize fertilizer strategy using multi-objective economic optimization.
    
    This endpoint provides comprehensive economic optimization for fertilizer strategies
    considering cost, yield, environmental impact, and risk management.
    
    Agricultural Use Cases:
    - Multi-objective optimization (cost, yield, environment)
    - Risk assessment and mitigation planning
    - Sensitivity analysis for key variables
    - Monte Carlo simulation for uncertainty modeling
    - Investment prioritization and budget allocation
    
    Features:
    - Multi-objective optimization with weighted goals
    - Risk assessment with mitigation strategies
    - Sensitivity analysis for parameter variations
    - Monte Carlo simulation for uncertainty modeling
    - Budget allocation and investment prioritization
    - Scenario modeling with multiple market conditions
    - Economic impact assessment and constraint relaxation
    - Pareto frontier analysis for trade-off visualization
    - Trade-off analysis between competing objectives
    
    Request Body:
    {
        "analysis_id": "uuid",
        "farm_context": {
            "farm_id": "uuid",
            "field_id": "uuid",
            "field_size_acres": 40.0,
            "region": "US-Midwest"
        },
        "crop_context": {
            "crop_type": "corn",
            "expected_yield_bu_per_acre": 180.0,
            "crop_price_per_bu": 5.50
        },
        "fertilizer_requirements": [
            {
                "product": "urea",
                "type": "nitrogen",
                "rate_lbs_per_acre": 150.0,
                "application_method": "broadcast"
            }
        ],
        "optimization_goals": {
            "primary_goal": "profit_maximization",
            "yield_priority": 0.8,
            "cost_priority": 0.7,
            "environmental_priority": 0.6
        },
        "constraints": {
            "budget_limit": 12000.0,
            "risk_tolerance": "moderate",
            "environmental_constraints": {
                "max_n_rate": 200.0,
                "buffer_zones": true
            }
        },
        "scenarios_to_analyze": ["bull_market", "bear_market", "volatile_market"],
        "custom_scenarios": [
            {
                "name": "High Input Cost Scenario",
                "fertilizer_multipliers": {"urea": 1.5, "dap": 1.4},
                "crop_multiplier": 0.9,
                "probability": 0.15,
                "risk_level": "high"
            }
        ],
        "include_sensitivity_analysis": true,
        "include_monte_carlo_simulation": true,
        "include_risk_assessment": true
    }
    
    Response:
    {
        "analysis_id": "uuid",
        "scenarios": [...],
        "optimization_results": [...],
        "risk_assessments": [...],
        "sensitivity_analysis": {...},
        "monte_carlo_simulation": {...},
        "budget_allocations": [...],
        "investment_priorities": [...],
        "recommendations": [...],
        "processing_time_ms": 1250.5
    }
    """
    try:
        logger.info(f"Starting economic optimization for analysis {request.analysis_id}")
        start_time = time.time()
        
        # Validate request
        if not request.farm_context or not request.crop_context:
            raise HTTPException(status_code=400, detail="Farm context and crop context are required")
        
        if not request.fertilizer_requirements:
            raise HTTPException(status_code=400, detail="Fertilizer requirements are required")
        
        # Perform optimization
        result = await service.optimize_fertilizer_strategy(request)
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Economic optimization completed in {processing_time:.2f}ms")
        
        return result
        
    except EconomicOptimizationError as e:
        logger.error(f"Economic optimization error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ProviderError as e:
        logger.error(f"Provider error in economic optimization: {e}")
        raise HTTPException(status_code=500, detail=f"External provider error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in economic optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Economic optimization failed: {str(e)}")


@router.post("/multi-objective-optimization", response_model=List[MultiObjectiveOptimization])
async def perform_multi_objective_optimization(
    request: EconomicOptimizationRequest = Body(...),
    service: EconomicOptimizer = Depends(get_economic_optimizer)
):
    """
    Perform multi-objective optimization for economic scenarios.
    
    This endpoint provides multi-objective optimization considering:
    - Profit maximization
    - Cost minimization
    - Environmental impact minimization
    - Risk management
    
    Request Body:
    {
        "analysis_id": "uuid",
        "farm_context": {
            "farm_id": "uuid",
            "field_id": "uuid",
            "field_size_acres": 40.0,
            "region": "US-Midwest"
        },
        "crop_context": {
            "crop_type": "corn",
            "expected_yield_bu_per_acre": 180.0,
            "crop_price_per_bu": 5.50
        },
        "fertilizer_requirements": [
            {
                "product": "urea",
                "type": "nitrogen",
                "rate_lbs_per_acre": 150.0,
                "application_method": "broadcast"
            }
        ],
        "optimization_goals": {
            "primary_goal": "profit_maximization",
            "yield_priority": 0.8,
            "cost_priority": 0.7,
            "environmental_priority": 0.6
        },
        "constraints": {
            "budget_limit": 12000.0,
            "risk_tolerance": "moderate",
            "environmental_constraints": {
                "max_n_rate": 200.0,
                "buffer_zones": true
            }
        }
    }
    
    Response:
    [
        {
            "optimization_id": "uuid",
            "scenario_id": "uuid",
            "base_optimization": {...},
            "weighted_optimization": {...},
            "constraint_optimization": {...},
            "risk_adjusted_optimization": {...},
            "objectives": {...},
            "constraints": {...},
            "optimization_methods": [...],
            "created_at": "datetime"
        }
    ]
    """
    try:
        logger.info(f"Starting multi-objective optimization for analysis {request.analysis_id}")
        start_time = time.time()
        
        # Validate request
        if not request.farm_context or not request.crop_context:
            raise HTTPException(status_code=400, detail="Farm context and crop context are required")
        
        if not request.fertilizer_requirements:
            raise HTTPException(status_code=400, detail="Fertilizer requirements are required")
        
        # Get market data
        market_data = await service._get_market_data(request)
        
        # Generate scenarios
        scenarios = await service._generate_scenarios(request, market_data)
        
        # Perform multi-objective optimization
        optimization_results = await service._perform_multi_objective_optimization(
            request, market_data, scenarios
        )
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Multi-objective optimization completed in {processing_time:.2f}ms")
        
        return optimization_results
        
    except EconomicOptimizationError as e:
        logger.error(f"Multi-objective optimization error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ProviderError as e:
        logger.error(f"Provider error in multi-objective optimization: {e}")
        raise HTTPException(status_code=500, detail=f"External provider error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in multi-objective optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Multi-objective optimization failed: {str(e)}")


@router.post("/risk-assessment", response_model=List[RiskAssessment])
async def perform_risk_assessment(
    request: EconomicOptimizationRequest = Body(...),
    service: EconomicOptimizer = Depends(get_economic_optimizer)
):
    """
    Perform comprehensive risk assessment for economic scenarios.
    
    This endpoint provides risk assessment considering:
    - Price volatility risk
    - Yield variability risk
    - Weather impact risk
    - Market conditions risk
    - Input availability risk
    - Equipment failure risk
    - Regulatory changes risk
    - Pest pressure risk
    - Disease outbreak risk
    
    Request Body:
    {
        "analysis_id": "uuid",
        "farm_context": {
            "farm_id": "uuid",
            "field_id": "uuid",
            "field_size_acres": 40.0,
            "region": "US-Midwest"
        },
        "crop_context": {
            "crop_type": "corn",
            "expected_yield_bu_per_acre": 180.0,
            "crop_price_per_bu": 5.50
        },
        "fertilizer_requirements": [
            {
                "product": "urea",
                "type": "nitrogen",
                "rate_lbs_per_acre": 150.0,
                "application_method": "broadcast"
            }
        ],
        "scenarios_to_analyze": ["bull_market", "bear_market", "volatile_market"]
    }
    
    Response:
    [
        {
            "assessment_id": "uuid",
            "scenario_id": "uuid",
            "overall_risk_score": 0.65,
            "risk_level": "medium",
            "individual_risks": {
                "price_volatility": 0.7,
                "yield_variability": 0.5,
                "weather_impact": 0.6
            },
            "mitigation_strategies": [...],
            "confidence_intervals": {...},
            "created_at": "datetime"
        }
    ]
    """
    try:
        logger.info(f"Starting risk assessment for analysis {request.analysis_id}")
        start_time = time.time()
        
        # Validate request
        if not request.farm_context or not request.crop_context:
            raise HTTPException(status_code=400, detail="Farm context and crop context are required")
        
        if not request.fertilizer_requirements:
            raise HTTPException(status_code=400, detail="Fertilizer requirements are required")
        
        # Get market data
        market_data = await service._get_market_data(request)
        
        # Generate scenarios
        scenarios = await service._generate_scenarios(request, market_data)
        
        # Perform risk assessment
        risk_assessments = await service._perform_risk_assessment(
            request, scenarios, []
        )
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Risk assessment completed in {processing_time:.2f}ms")
        
        return risk_assessments
        
    except EconomicOptimizationError as e:
        logger.error(f"Risk assessment error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ProviderError as e:
        logger.error(f"Provider error in risk assessment: {e}")
        raise HTTPException(status_code=500, detail=f"External provider error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in risk assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")


@router.post("/sensitivity-analysis", response_model=SensitivityAnalysis)
async def perform_sensitivity_analysis(
    request: EconomicOptimizationRequest = Body(...),
    service: EconomicOptimizer = Depends(get_economic_optimizer)
):
    """
    Perform sensitivity analysis for economic optimization.
    
    This endpoint provides sensitivity analysis for:
    - Fertilizer price variations
    - Crop price variations
    - Yield expectation variations
    - Field size variations
    
    Request Body:
    {
        "analysis_id": "uuid",
        "farm_context": {
            "farm_id": "uuid",
            "field_id": "uuid",
            "field_size_acres": 40.0,
            "region": "US-Midwest"
        },
        "crop_context": {
            "crop_type": "corn",
            "expected_yield_bu_per_acre": 180.0,
            "crop_price_per_bu": 5.50
        },
        "fertilizer_requirements": [
            {
                "product": "urea",
                "type": "nitrogen",
                "rate_lbs_per_acre": 150.0,
                "application_method": "broadcast"
            }
        ]
    }
    
    Response:
    {
        "analysis_id": "uuid",
        "parameter_variations": {...},
        "sensitivity_results": {...},
        "critical_parameters": [...],
        "recommendations": [...],
        "created_at": "datetime"
    }
    """
    try:
        logger.info(f"Starting sensitivity analysis for analysis {request.analysis_id}")
        start_time = time.time()
        
        # Validate request
        if not request.farm_context or not request.crop_context:
            raise HTTPException(status_code=400, detail="Farm context and crop context are required")
        
        if not request.fertilizer_requirements:
            raise HTTPException(status_code=400, detail="Fertilizer requirements are required")
        
        # Get market data
        market_data = await service._get_market_data(request)
        
        # Generate scenarios
        scenarios = await service._generate_scenarios(request, market_data)
        
        # Perform multi-objective optimization
        optimization_results = await service._perform_multi_objective_optimization(
            request, market_data, scenarios
        )
        
        # Perform sensitivity analysis
        sensitivity_analysis = await service._perform_sensitivity_analysis(
            request, optimization_results
        )
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Sensitivity analysis completed in {processing_time:.2f}ms")
        
        return sensitivity_analysis
        
    except EconomicOptimizationError as e:
        logger.error(f"Sensitivity analysis error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ProviderError as e:
        logger.error(f"Provider error in sensitivity analysis: {e}")
        raise HTTPException(status_code=500, detail=f"External provider error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in sensitivity analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Sensitivity analysis failed: {str(e)}")


@router.post("/monte-carlo-simulation", response_model=MonteCarloSimulation)
async def perform_monte_carlo_simulation(
    request: EconomicOptimizationRequest = Body(...),
    service: EconomicOptimizer = Depends(get_economic_optimizer)
):
    """
    Perform Monte Carlo simulation for economic forecasting.
    
    This endpoint provides Monte Carlo simulation with:
    - Random price variations
    - Statistical analysis of outcomes
    - Confidence intervals
    - Probability distributions
    
    Request Body:
    {
        "analysis_id": "uuid",
        "farm_context": {
            "farm_id": "uuid",
            "field_id": "uuid",
            "field_size_acres": 40.0,
            "region": "US-Midwest"
        },
        "crop_context": {
            "crop_type": "corn",
            "expected_yield_bu_per_acre": 180.0,
            "crop_price_per_bu": 5.50
        },
        "fertilizer_requirements": [
            {
                "product": "urea",
                "type": "nitrogen",
                "rate_lbs_per_acre": 150.0,
                "application_method": "broadcast"
            }
        ],
        "monte_carlo_iterations": 10000
    }
    
    Response:
    {
        "simulation_id": "uuid",
        "iterations": 10000,
        "confidence_levels": [...],
        "scenario_results": [...],
        "overall_statistics": {...},
        "created_at": "datetime"
    }
    """
    try:
        logger.info(f"Starting Monte Carlo simulation for analysis {request.analysis_id}")
        start_time = time.time()
        
        # Validate request
        if not request.farm_context or not request.crop_context:
            raise HTTPException(status_code=400, detail="Farm context and crop context are required")
        
        if not request.fertilizer_requirements:
            raise HTTPException(status_code=400, detail="Fertilizer requirements are required")
        
        # Get market data
        market_data = await service._get_market_data(request)
        
        # Generate scenarios
        scenarios = await service._generate_scenarios(request, market_data)
        
        # Perform Monte Carlo simulation
        monte_carlo_results = await service._perform_monte_carlo_simulation(
            request, scenarios
        )
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Monte Carlo simulation completed in {processing_time:.2f}ms")
        
        return monte_carlo_results
        
    except EconomicOptimizationError as e:
        logger.error(f"Monte Carlo simulation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ProviderError as e:
        logger.error(f"Provider error in Monte Carlo simulation: {e}")
        raise HTTPException(status_code=500, detail=f"External provider error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in Monte Carlo simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Monte Carlo simulation failed: {str(e)}")


@router.post("/budget-allocation", response_model=List[BudgetAllocation])
async def generate_budget_allocations(
    request: EconomicOptimizationRequest = Body(...),
    service: EconomicOptimizer = Depends(get_economic_optimizer)
):
    """
    Generate budget allocations for economic optimization.
    
    This endpoint provides budget allocation recommendations considering:
    - Yield potential optimization
    - Cost efficiency maximization
    - Environmental impact minimization
    - Risk management
    - Sustainability goals
    
    Request Body:
    {
        "analysis_id": "uuid",
        "farm_context": {
            "farm_id": "uuid",
            "field_id": "uuid",
            "field_size_acres": 40.0,
            "region": "US-Midwest"
        },
        "crop_context": {
            "crop_type": "corn",
            "expected_yield_bu_per_acre": 180.0,
            "crop_price_per_bu": 5.50
        },
        "fertilizer_requirements": [
            {
                "product": "urea",
                "type": "nitrogen",
                "rate_lbs_per_acre": 150.0,
                "application_method": "broadcast"
            }
        ],
        "budget_limit": 12000.0
    }
    
    Response:
    [
        {
            "allocation_id": "uuid",
            "optimization_id": "uuid",
            "total_budget": 12000.0,
            "field_size_acres": 40.0,
            "allocation_breakdown": {...},
            "per_acre_allocation": 300.0,
            "budget_utilization": 0.85,
            "remaining_budget": 1800.0,
            "created_at": "datetime"
        }
    ]
    """
    try:
        logger.info(f"Starting budget allocation generation for analysis {request.analysis_id}")
        start_time = time.time()
        
        # Validate request
        if not request.farm_context or not request.crop_context:
            raise HTTPException(status_code=400, detail="Farm context and crop context are required")
        
        if not request.fertilizer_requirements:
            raise HTTPException(status_code=400, detail="Fertilizer requirements are required")
        
        # Get market data
        market_data = await service._get_market_data(request)
        
        # Generate scenarios
        scenarios = await service._generate_scenarios(request, market_data)
        
        # Perform multi-objective optimization
        optimization_results = await service._perform_multi_objective_optimization(
            request, market_data, scenarios
        )
        
        # Generate budget allocations
        budget_allocations = await service._generate_budget_allocations(
            request, optimization_results
        )
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Budget allocation generation completed in {processing_time:.2f}ms")
        
        return budget_allocations
        
    except EconomicOptimizationError as e:
        logger.error(f"Budget allocation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ProviderError as e:
        logger.error(f"Provider error in budget allocation: {e}")
        raise HTTPException(status_code=500, detail=f"External provider error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in budget allocation: {e}")
        raise HTTPException(status_code=500, detail=f"Budget allocation failed: {str(e)}")


@router.post("/investment-priorities", response_model=List[InvestmentPrioritization])
async def prioritize_investments(
    request: EconomicOptimizationRequest = Body(...),
    service: EconomicOptimizer = Depends(get_economic_optimizer)
):
    """
    Prioritize investments based on economic optimization.
    
    This endpoint provides investment prioritization considering:
    - ROI optimization
    - Risk-adjusted returns
    - Payback periods
    - Opportunity costs
    - Budget constraints
    
    Request Body:
    {
        "analysis_id": "uuid",
        "farm_context": {
            "farm_id": "uuid",
            "field_id": "uuid",
            "field_size_acres": 40.0,
            "region": "US-Midwest"
        },
        "crop_context": {
            "crop_type": "corn",
            "expected_yield_bu_per_acre": 180.0,
            "crop_price_per_bu": 5.50
        },
        "fertilizer_requirements": [
            {
                "product": "urea",
                "type": "nitrogen",
                "rate_lbs_per_acre": 150.0,
                "application_method": "broadcast"
            }
        ],
        "budget_limit": 12000.0,
        "risk_tolerance": "moderate"
    }
    
    Response:
    [
        {
            "priority_id": "uuid",
            "optimization_id": "uuid",
            "priority_score": 0.85,
            "priority_level": "high",
            "investment_recommendations": [...],
            "risk_adjusted_return": 15.5,
            "payback_period": {...},
            "opportunity_cost": {...},
            "created_at": "datetime"
        }
    ]
    """
    try:
        logger.info(f"Starting investment prioritization for analysis {request.analysis_id}")
        start_time = time.time()
        
        # Validate request
        if not request.farm_context or not request.crop_context:
            raise HTTPException(status_code=400, detail="Farm context and crop context are required")
        
        if not request.fertilizer_requirements:
            raise HTTPException(status_code=400, detail="Fertilizer requirements are required")
        
        # Get market data
        market_data = await service._get_market_data(request)
        
        # Generate scenarios
        scenarios = await service._generate_scenarios(request, market_data)
        
        # Perform multi-objective optimization
        optimization_results = await service._perform_multi_objective_optimization(
            request, market_data, scenarios
        )
        
        # Perform risk assessment
        risk_assessments = await service._perform_risk_assessment(
            request, scenarios, optimization_results
        )
        
        # Prioritize investments
        investment_priorities = await service._prioritize_investments(
            request, optimization_results, risk_assessments
        )
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Investment prioritization completed in {processing_time:.2f}ms")
        
        return investment_priorities
        
    except EconomicOptimizationError as e:
        logger.error(f"Investment prioritization error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ProviderError as e:
        logger.error(f"Provider error in investment prioritization: {e}")
        raise HTTPException(status_code=500, detail=f"External provider error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in investment prioritization: {e}")
        raise HTTPException(status_code=500, detail=f"Investment prioritization failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for economic optimization service monitoring."""
    return {"status": "healthy", "service": "economic-optimization", "timestamp": datetime.utcnow()}


@router.get("/metrics")
async def get_service_metrics():
    """Get service performance and usage metrics."""
    # In a real implementation, this would return actual metrics
    return {
        "service": "economic-optimization",
        "uptime": "99.5%",
        "response_time_avg_ms": 1200,
        "requests_per_minute": 45,
        "error_rate": "0.2%",
        "cache_hit_rate": "75%"
    }