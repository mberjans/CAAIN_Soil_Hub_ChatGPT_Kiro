"""
API Routes for Economic Optimization Service.

This module provides REST API endpoints for economic optimization and scenario modeling,
including linear programming, dynamic programming, stochastic optimization, and comprehensive
scenario analysis for fertilizer application method optimization.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from enum import Enum

from src.models.application_models import (
    ApplicationMethod, FieldConditions, CropRequirements, 
    FertilizerSpecification, EquipmentSpecification
)
from src.services.economic_optimization_service import (
    EconomicOptimizationService, OptimizationAlgorithm, OptimizationObjective,
    ScenarioType, OptimizationConstraint, OptimizationResult, ScenarioParameters
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/economic-optimization", tags=["economic-optimization"])


class OptimizationRequest(BaseModel):
    """Request model for economic optimization."""
    application_methods: List[ApplicationMethod] = Field(..., description="Available application methods")
    field_conditions: FieldConditions = Field(..., description="Field conditions and characteristics")
    crop_requirements: CropRequirements = Field(..., description="Crop requirements and constraints")
    fertilizer_specification: FertilizerSpecification = Field(..., description="Fertilizer specifications")
    available_equipment: List[EquipmentSpecification] = Field(default_factory=list, description="Available equipment inventory")
    objective: OptimizationObjective = Field(OptimizationObjective.BALANCED_OPTIMIZATION, description="Optimization objective")
    algorithm: OptimizationAlgorithm = Field(OptimizationAlgorithm.LINEAR_PROGRAMMING, description="Optimization algorithm")
    constraints: Optional[List[OptimizationConstraint]] = Field(None, description="Optimization constraints")
    scenarios: Optional[List[ScenarioParameters]] = Field(None, description="Economic scenarios to consider")


class ScenarioAnalysisRequest(BaseModel):
    """Request model for scenario analysis."""
    base_optimization_request: OptimizationRequest = Field(..., description="Base optimization request")
    scenario_types: List[ScenarioType] = Field(..., description="Types of scenarios to analyze")
    scenario_count: int = Field(5, ge=1, le=20, description="Number of scenarios to generate per type")
    include_monte_carlo: bool = Field(True, description="Include Monte Carlo simulation")
    monte_carlo_iterations: int = Field(1000, ge=100, le=10000, description="Number of Monte Carlo iterations")


class SensitivityAnalysisRequest(BaseModel):
    """Request model for sensitivity analysis."""
    optimization_request: OptimizationRequest = Field(..., description="Base optimization request")
    parameter_ranges: Dict[str, Dict[str, float]] = Field(..., description="Parameter ranges for sensitivity analysis")
    analysis_type: str = Field("cost_sensitivity", description="Type of sensitivity analysis")
    include_risk_assessment: bool = Field(True, description="Include risk assessment")


class InvestmentPlanningRequest(BaseModel):
    """Request model for investment planning analysis."""
    optimization_request: OptimizationRequest = Field(..., description="Base optimization request")
    investment_horizon_years: int = Field(5, ge=1, le=20, description="Investment planning horizon")
    discount_rate: float = Field(0.08, ge=0.0, le=0.5, description="Discount rate for NPV calculation")
    include_equipment_investment: bool = Field(True, description="Include equipment investment analysis")
    include_maintenance_costs: bool = Field(True, description="Include maintenance cost projections")


# Dependency injection
async def get_economic_optimization_service() -> EconomicOptimizationService:
    return EconomicOptimizationService()


@router.post("/optimize", response_model=OptimizationResult)
async def optimize_application_methods(
    request: OptimizationRequest,
    service: EconomicOptimizationService = Depends(get_economic_optimization_service)
):
    """
    Optimize fertilizer application methods using advanced economic optimization.
    
    This endpoint implements sophisticated optimization algorithms including linear programming,
    dynamic programming, stochastic optimization, genetic algorithms, simulated annealing,
    and particle swarm optimization to provide optimal economic solutions for fertilizer
    application methods under various scenarios and constraints.
    
    **Optimization Algorithms Available:**
    - Linear Programming: Fast optimization for linear objective functions and constraints
    - Dynamic Programming: Optimal substructure problems with overlapping subproblems
    - Stochastic Optimization: Monte Carlo simulation for uncertain conditions
    - Genetic Algorithm: Evolutionary optimization for complex non-linear problems
    - Simulated Annealing: Probabilistic optimization for global optimum search
    - Particle Swarm: Swarm intelligence optimization for multi-objective problems
    
    **Optimization Objectives:**
    - Minimize Cost: Find the most cost-effective application method
    - Maximize Profit: Optimize for maximum profit considering revenue and costs
    - Maximize ROI: Optimize return on investment ratio
    - Minimize Risk: Reduce economic and operational risks
    - Maximize Efficiency: Optimize for application efficiency and effectiveness
    - Balanced Optimization: Multi-objective optimization balancing multiple criteria
    
    **Economic Scenarios:**
    - Price Scenarios: Fertilizer, fuel, labor, and equipment price variations
    - Weather Scenarios: Drought, excessive rain, and optimal weather conditions
    - Yield Scenarios: Low, average, and high yield potential scenarios
    - Cost Scenarios: Low, average, and high cost scenarios
    - Market Scenarios: Bull, bear, and stable market conditions
    - Comprehensive Scenarios: Combined analysis with correlation matrices
    
    **Features:**
    - Multi-objective optimization with customizable weights
    - Constraint handling for equipment, labor, and field limitations
    - Sensitivity analysis for parameter variations
    - Risk assessment and mitigation strategies
    - Investment planning and ROI analysis
    - Scenario modeling with probability distributions
    - Monte Carlo simulation for uncertainty quantification
    """
    try:
        logger.info("Processing economic optimization request")
        
        result = await service.optimize_application_methods(
            application_methods=request.application_methods,
            field_conditions=request.field_conditions,
            crop_requirements=request.crop_requirements,
            fertilizer_specification=request.fertilizer_specification,
            available_equipment=request.available_equipment,
            objective=request.objective,
            algorithm=request.algorithm,
            constraints=request.constraints,
            scenarios=request.scenarios
        )
        
        logger.info(f"Economic optimization completed in {result.optimization_time_ms:.2f}ms")
        return result
        
    except Exception as e:
        logger.error(f"Error in economic optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Economic optimization failed: {str(e)}")


@router.post("/scenario-analysis")
async def perform_scenario_analysis(
    request: ScenarioAnalysisRequest,
    service: EconomicOptimizationService = Depends(get_economic_optimization_service)
):
    """
    Perform comprehensive scenario analysis for fertilizer application methods.
    
    This endpoint analyzes multiple economic scenarios to understand how different
    conditions affect optimal method selection and economic outcomes.
    
    **Scenario Types:**
    - Price Scenarios: Analyze impact of fertilizer, fuel, labor, and equipment price changes
    - Weather Scenarios: Evaluate performance under different weather conditions
    - Yield Scenarios: Assess impact of yield variations on method selection
    - Cost Scenarios: Analyze cost structure variations and their effects
    - Market Scenarios: Evaluate market condition impacts on profitability
    - Comprehensive Scenarios: Combined analysis with correlation between factors
    
    **Analysis Features:**
    - Monte Carlo simulation for probabilistic analysis
    - Risk quantification and probability distributions
    - Sensitivity analysis across scenario parameters
    - Optimal method ranking under different conditions
    - Economic impact assessment for each scenario
    - Risk mitigation recommendations
    
    **Use Cases:**
    - Planning for different economic conditions
    - Risk assessment and contingency planning
    - Investment decision support
    - Market volatility preparation
    - Weather risk management
    - Long-term strategic planning
    """
    try:
        logger.info("Processing scenario analysis request")
        
        scenario_results = []
        
        # Analyze each scenario type
        for scenario_type in request.scenario_types:
            # Generate scenarios for this type
            scenarios = await service._generate_scenarios_for_type(
                scenario_type, request.scenario_count
            )
            
            # Run optimization for each scenario
            scenario_optimizations = []
            for scenario in scenarios:
                optimization_result = await service.optimize_application_methods(
                    application_methods=request.base_optimization_request.application_methods,
                    field_conditions=request.base_optimization_request.field_conditions,
                    crop_requirements=request.base_optimization_request.crop_requirements,
                    fertilizer_specification=request.base_optimization_request.fertilizer_specification,
                    available_equipment=request.base_optimization_request.available_equipment,
                    objective=request.base_optimization_request.objective,
                    algorithm=request.base_optimization_request.algorithm,
                    constraints=request.base_optimization_request.constraints,
                    scenarios=[scenario]
                )
                
                scenario_optimizations.append({
                    "scenario": scenario,
                    "optimization_result": optimization_result
                })
            
            scenario_results.append({
                "scenario_type": scenario_type.value,
                "scenario_count": len(scenarios),
                "optimizations": scenario_optimizations,
                "summary": await service._summarize_scenario_results(scenario_optimizations)
            })
        
        # Perform Monte Carlo analysis if requested
        monte_carlo_results = None
        if request.include_monte_carlo:
            monte_carlo_results = await service._perform_monte_carlo_analysis(
                request.base_optimization_request, request.monte_carlo_iterations
            )
        
        analysis_result = {
            "scenario_analysis": scenario_results,
            "monte_carlo_analysis": monte_carlo_results,
            "summary": {
                "total_scenarios_analyzed": sum(len(result["optimizations"]) for result in scenario_results),
                "scenario_types": [result["scenario_type"] for result in scenario_results],
                "monte_carlo_included": request.include_monte_carlo,
                "analysis_timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
            }
        }
        
        logger.info("Scenario analysis completed")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error in scenario analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Scenario analysis failed: {str(e)}")


@router.post("/sensitivity-analysis")
async def perform_sensitivity_analysis(
    request: SensitivityAnalysisRequest,
    service: EconomicOptimizationService = Depends(get_economic_optimization_service)
):
    """
    Perform sensitivity analysis on optimization parameters.
    
    This endpoint analyzes how changes in key parameters affect optimization results,
    helping farmers understand which factors most influence their decisions.
    
    **Sensitivity Analysis Types:**
    - Cost Sensitivity: Analyze impact of cost parameter variations
    - Yield Sensitivity: Evaluate yield parameter impact on optimization
    - Price Sensitivity: Assess price parameter sensitivity
    - Equipment Sensitivity: Analyze equipment parameter variations
    - Field Condition Sensitivity: Evaluate field parameter impact
    
    **Analysis Features:**
    - Parameter range analysis with confidence intervals
    - Critical threshold identification
    - Risk assessment for parameter variations
    - Optimal parameter value recommendations
    - Sensitivity ranking and prioritization
    - Robustness analysis for decision stability
    
    **Risk Assessment:**
    - Parameter uncertainty quantification
    - Risk mitigation strategies
    - Confidence level analysis
    - Decision robustness evaluation
    - Contingency planning recommendations
    """
    try:
        logger.info("Processing sensitivity analysis request")
        
        # Perform base optimization
        base_result = await service.optimize_application_methods(
            application_methods=request.optimization_request.application_methods,
            field_conditions=request.optimization_request.field_conditions,
            crop_requirements=request.optimization_request.crop_requirements,
            fertilizer_specification=request.optimization_request.fertilizer_specification,
            available_equipment=request.optimization_request.available_equipment,
            objective=request.optimization_request.objective,
            algorithm=request.optimization_request.algorithm,
            constraints=request.optimization_request.constraints,
            scenarios=request.optimization_request.scenarios
        )
        
        # Perform sensitivity analysis for each parameter
        sensitivity_results = {}
        
        for param_name, param_range in request.parameter_ranges.items():
            param_sensitivity = await service._analyze_parameter_sensitivity(
                request.optimization_request, param_name, param_range, base_result
            )
            sensitivity_results[param_name] = param_sensitivity
        
        # Perform risk assessment if requested
        risk_assessment = None
        if request.include_risk_assessment:
            risk_assessment = await service._perform_risk_assessment(
                sensitivity_results, base_result
            )
        
        analysis_result = {
            "base_optimization": base_result,
            "sensitivity_analysis": sensitivity_results,
            "risk_assessment": risk_assessment,
            "summary": {
                "parameters_analyzed": list(request.parameter_ranges.keys()),
                "analysis_type": request.analysis_type,
                "risk_assessment_included": request.include_risk_assessment
            }
        }
        
        logger.info("Sensitivity analysis completed")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error in sensitivity analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Sensitivity analysis failed: {str(e)}")


@router.post("/investment-planning")
async def perform_investment_planning(
    request: InvestmentPlanningRequest,
    service: EconomicOptimizationService = Depends(get_economic_optimization_service)
):
    """
    Perform investment planning analysis for fertilizer application methods.
    
    This endpoint provides comprehensive investment analysis including NPV calculations,
    payback periods, ROI analysis, and long-term financial planning for fertilizer
    application method investments.
    
    **Investment Analysis Features:**
    - Net Present Value (NPV) calculations with discount rates
    - Payback period analysis for equipment investments
    - Return on Investment (ROI) calculations over time
    - Internal Rate of Return (IRR) analysis
    - Break-even analysis for different scenarios
    - Cash flow projections and financial modeling
    
    **Investment Components:**
    - Equipment purchase and financing costs
    - Maintenance and operational costs over time
    - Labor cost projections and inflation adjustments
    - Fuel cost projections and volatility analysis
    - Fertilizer cost projections and market trends
    - Revenue projections based on yield improvements
    
    **Financial Planning:**
    - Multi-year financial projections
    - Risk-adjusted return calculations
    - Sensitivity analysis for financial parameters
    - Scenario analysis for different economic conditions
    - Investment timing optimization
    - Financing option analysis
    
    **Decision Support:**
    - Investment recommendation ranking
    - Risk-return trade-off analysis
    - Optimal investment timing recommendations
    - Financing strategy recommendations
    - Portfolio optimization for multiple investments
    """
    try:
        logger.info("Processing investment planning request")
        
        # Perform base optimization
        base_result = await service.optimize_application_methods(
            application_methods=request.optimization_request.application_methods,
            field_conditions=request.optimization_request.field_conditions,
            crop_requirements=request.optimization_request.crop_requirements,
            fertilizer_specification=request.optimization_request.fertilizer_specification,
            available_equipment=request.optimization_request.available_equipment,
            objective=OptimizationObjective.MAXIMIZE_ROI,  # Use ROI for investment planning
            algorithm=request.optimization_request.algorithm,
            constraints=request.optimization_request.constraints,
            scenarios=request.optimization_request.scenarios
        )
        
        # Perform investment analysis
        investment_analysis = await service._perform_investment_analysis(
            base_result, request.investment_horizon_years, request.discount_rate,
            request.include_equipment_investment, request.include_maintenance_costs
        )
        
        # Generate financial projections
        financial_projections = await service._generate_financial_projections(
            investment_analysis, request.investment_horizon_years
        )
        
        # Perform investment optimization
        investment_optimization = await service._optimize_investment_timing(
            investment_analysis, financial_projections
        )
        
        planning_result = {
            "base_optimization": base_result,
            "investment_analysis": investment_analysis,
            "financial_projections": financial_projections,
            "investment_optimization": investment_optimization,
            "summary": {
                "investment_horizon_years": request.investment_horizon_years,
                "discount_rate": request.discount_rate,
                "equipment_investment_included": request.include_equipment_investment,
                "maintenance_costs_included": request.include_maintenance_costs
            }
        }
        
        logger.info("Investment planning completed")
        return planning_result
        
    except Exception as e:
        logger.error(f"Error in investment planning: {e}")
        raise HTTPException(status_code=500, detail=f"Investment planning failed: {str(e)}")


@router.get("/optimization-algorithms")
async def get_optimization_algorithms():
    """
    Get list of available optimization algorithms and their characteristics.
    
    Returns information about all available optimization algorithms that can be used
    for fertilizer application method optimization, including their characteristics,
    performance characteristics, and when to use each algorithm.
    """
    algorithms = [
        {
            "algorithm": OptimizationAlgorithm.LINEAR_PROGRAMMING,
            "name": "Linear Programming",
            "description": "Fast optimization for linear objective functions and constraints",
            "best_for": "Linear optimization problems with clear constraints",
            "characteristics": ["Fast", "Deterministic", "Linear", "Scalable"],
            "performance": "Excellent for small to medium problems",
            "limitations": "Requires linear objective and constraints"
        },
        {
            "algorithm": OptimizationAlgorithm.DYNAMIC_PROGRAMMING,
            "name": "Dynamic Programming",
            "description": "Optimal substructure problems with overlapping subproblems",
            "best_for": "Sequential decision problems with optimal substructure",
            "characteristics": ["Optimal", "Sequential", "Substructure", "Overlapping"],
            "performance": "Excellent for problems with optimal substructure",
            "limitations": "Requires optimal substructure property"
        },
        {
            "algorithm": OptimizationAlgorithm.STOCHASTIC_OPTIMIZATION,
            "name": "Stochastic Optimization",
            "description": "Monte Carlo simulation for uncertain conditions",
            "best_for": "Problems with uncertainty and random variables",
            "characteristics": ["Probabilistic", "Uncertainty", "Monte Carlo", "Robust"],
            "performance": "Good for uncertain environments",
            "limitations": "Computationally intensive"
        },
        {
            "algorithm": OptimizationAlgorithm.GENETIC_ALGORITHM,
            "name": "Genetic Algorithm",
            "description": "Evolutionary optimization for complex non-linear problems",
            "best_for": "Complex non-linear optimization problems",
            "characteristics": ["Evolutionary", "Non-linear", "Global search", "Robust"],
            "performance": "Good for complex problems",
            "limitations": "May not find global optimum"
        },
        {
            "algorithm": OptimizationAlgorithm.SIMULATED_ANNEALING,
            "name": "Simulated Annealing",
            "description": "Probabilistic optimization for global optimum search",
            "best_for": "Global optimization with local optima",
            "characteristics": ["Probabilistic", "Global search", "Annealing", "Robust"],
            "performance": "Good for avoiding local optima",
            "limitations": "Requires careful parameter tuning"
        },
        {
            "algorithm": OptimizationAlgorithm.PARTICLE_SWARM,
            "name": "Particle Swarm Optimization",
            "description": "Swarm intelligence optimization for multi-objective problems",
            "best_for": "Multi-objective optimization problems",
            "characteristics": ["Swarm intelligence", "Multi-objective", "Social", "Adaptive"],
            "performance": "Good for multi-objective problems",
            "limitations": "May converge slowly"
        }
    ]
    
    return {
        "available_algorithms": algorithms,
        "default_algorithm": OptimizationAlgorithm.LINEAR_PROGRAMMING,
        "recommendation": "Use Linear Programming for most scenarios, Genetic Algorithm for complex problems, Stochastic Optimization for uncertain conditions"
    }


@router.get("/optimization-objectives")
async def get_optimization_objectives():
    """
    Get list of available optimization objectives and their descriptions.
    
    Returns information about all available optimization objectives that can be used
    for fertilizer application method optimization, including their characteristics
    and when to use each objective.
    """
    objectives = [
        {
            "objective": OptimizationObjective.MINIMIZE_COST,
            "name": "Minimize Cost",
            "description": "Find the most cost-effective application method",
            "best_for": "Cost-sensitive operations and budget constraints",
            "characteristics": ["Cost-focused", "Budget-oriented", "Efficient"]
        },
        {
            "objective": OptimizationObjective.MAXIMIZE_PROFIT,
            "name": "Maximize Profit",
            "description": "Optimize for maximum profit considering revenue and costs",
            "best_for": "Profit-maximizing operations",
            "characteristics": ["Profit-focused", "Revenue-oriented", "Economic"]
        },
        {
            "objective": OptimizationObjective.MAXIMIZE_ROI,
            "name": "Maximize ROI",
            "description": "Optimize return on investment ratio",
            "best_for": "Investment-focused decision making",
            "characteristics": ["ROI-focused", "Investment-oriented", "Efficient"]
        },
        {
            "objective": OptimizationObjective.MINIMIZE_RISK,
            "name": "Minimize Risk",
            "description": "Reduce economic and operational risks",
            "best_for": "Risk-averse operations and uncertain conditions",
            "characteristics": ["Risk-focused", "Conservative", "Stable"]
        },
        {
            "objective": OptimizationObjective.MAXIMIZE_EFFICIENCY,
            "name": "Maximize Efficiency",
            "description": "Optimize for application efficiency and effectiveness",
            "best_for": "Efficiency-focused operations",
            "characteristics": ["Efficiency-focused", "Performance-oriented", "Optimal"]
        },
        {
            "objective": OptimizationObjective.BALANCED_OPTIMIZATION,
            "name": "Balanced Optimization",
            "description": "Multi-objective optimization balancing multiple criteria",
            "best_for": "Comprehensive decision making with multiple priorities",
            "characteristics": ["Balanced", "Multi-objective", "Comprehensive"]
        }
    ]
    
    return {
        "available_objectives": objectives,
        "default_objective": OptimizationObjective.BALANCED_OPTIMIZATION,
        "recommendation": "Use Balanced Optimization for most scenarios, specific objectives for focused optimization"
    }


@router.get("/scenario-types")
async def get_scenario_types():
    """
    Get list of available scenario types for economic analysis.
    
    Returns information about different scenario types that can be used
    for economic analysis, including their characteristics and use cases.
    """
    scenario_types = [
        {
            "type": ScenarioType.PRICE_SCENARIO,
            "name": "Price Scenario",
            "description": "Analyze impact of price variations for inputs and outputs",
            "use_case": "Market volatility analysis and price risk assessment",
            "characteristics": ["Fertilizer prices", "Fuel prices", "Labor costs", "Equipment costs", "Crop prices"]
        },
        {
            "type": ScenarioType.WEATHER_SCENARIO,
            "name": "Weather Scenario",
            "description": "Evaluate performance under different weather conditions",
            "use_case": "Weather risk management and climate adaptation",
            "characteristics": ["Drought conditions", "Excessive rain", "Optimal weather", "Weather impact on yield"]
        },
        {
            "type": ScenarioType.YIELD_SCENARIO,
            "name": "Yield Scenario",
            "description": "Assess impact of yield variations on method selection",
            "use_case": "Yield risk assessment and production planning",
            "characteristics": ["Low yield", "Average yield", "High yield", "Yield variability"]
        },
        {
            "type": ScenarioType.COST_SCENARIO,
            "name": "Cost Scenario",
            "description": "Analyze cost structure variations and their effects",
            "use_case": "Cost structure analysis and budget planning",
            "characteristics": ["Low costs", "Average costs", "High costs", "Cost variability"]
        },
        {
            "type": ScenarioType.MARKET_SCENARIO,
            "name": "Market Scenario",
            "description": "Evaluate market condition impacts on profitability",
            "use_case": "Market condition analysis and strategic planning",
            "characteristics": ["Bull market", "Bear market", "Stable market", "Market volatility"]
        },
        {
            "type": ScenarioType.COMPREHENSIVE_SCENARIO,
            "name": "Comprehensive Scenario",
            "description": "Combined analysis with correlation between factors",
            "use_case": "Comprehensive risk analysis and strategic planning",
            "characteristics": ["Multiple factors", "Correlation analysis", "Monte Carlo", "Risk assessment"]
        }
    ]
    
    return {
        "scenario_types": scenario_types,
        "default_scenarios": [ScenarioType.PRICE_SCENARIO, ScenarioType.WEATHER_SCENARIO, ScenarioType.YIELD_SCENARIO],
        "recommendation": "Use comprehensive scenarios for thorough analysis, specific scenarios for focused analysis"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for economic optimization service."""
    return {
        "service": "fertilizer-application-economic-optimization",
        "status": "healthy",
        "endpoints": [
            "optimize_application_methods",
            "perform_scenario_analysis",
            "perform_sensitivity_analysis",
            "perform_investment_planning",
            "get_optimization_algorithms",
            "get_optimization_objectives",
            "get_scenario_types"
        ],
        "features": [
            "linear_programming",
            "dynamic_programming",
            "stochastic_optimization",
            "genetic_algorithms",
            "simulated_annealing",
            "particle_swarm_optimization",
            "scenario_modeling",
            "sensitivity_analysis",
            "investment_planning",
            "risk_assessment",
            "monte_carlo_simulation",
            "economic_optimization"
        ]
    }