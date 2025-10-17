"""
Budget Constraint Optimization API Routes.

This module provides FastAPI routes for comprehensive budget constraint optimization,
including multi-objective optimization, Pareto frontier analysis, and constraint relaxation.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from ..models.roi_models import (
    ROIOptimizationRequest,
    MultiObjectiveOptimizationResult,
    BudgetAllocationResult,
    ParetoFrontierPoint,
    ConstraintRelaxationAnalysis,
    BudgetConstraint,
    OptimizationConstraints
)
from ..services.budget_constraint_optimizer import budget_constraint_optimizer_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/fertilizer", tags=["budget-constraint-optimization"])


@router.post("/optimize-budget-constraints", response_model=MultiObjectiveOptimizationResult)
async def optimize_budget_constraints(
    request: ROIOptimizationRequest,
    background_tasks: BackgroundTasks
):
    """
    Perform comprehensive budget constraint optimization.
    
    This endpoint provides advanced budget constraint optimization including:
    - Multi-objective optimization with Pareto frontier analysis
    - Budget allocation optimization across fields and nutrients
    - Constraint relaxation analysis
    - Trade-off analysis between objectives
    
    **Agricultural Use Cases:**
    - Multi-field budget allocation optimization
    - Constraint-aware fertilizer strategy planning
    - Trade-off analysis between profit, environment, and risk
    - Budget flexibility and reallocation analysis
    
    **Key Features:**
    - Pareto frontier generation for multiple scenarios
    - Budget allocation optimization with field priorities
    - Constraint relaxation impact analysis
    - Comprehensive trade-off analysis
    - Multi-objective optimization (profit, environment, risk)
    
    **Budget Constraint Types:**
    - Total budget limits across all fields
    - Per-field budget limits
    - Per-acre budget limits
    - Nutrient-specific budget allocation
    - Product-specific budget allocation
    - Seasonal budget allocation
    - Priority field budget multipliers
    """
    try:
        logger.info(f"Received budget constraint optimization request for {len(request.fields)} fields")
        
        # Validate budget constraints are present
        if not request.constraints.budget_constraint:
            raise HTTPException(
                status_code=400, 
                detail="Budget constraints are required for budget constraint optimization"
            )
        
        # Perform comprehensive budget constraint optimization
        result = await budget_constraint_optimizer_service.optimize_budget_constraints(request)
        
        # Log optimization completion
        logger.info(f"Budget constraint optimization completed with {len(result.pareto_frontier)} Pareto frontier points")
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in budget constraint optimization: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in budget constraint optimization: {e}")
        raise HTTPException(status_code=500, detail="Budget constraint optimization failed")


@router.post("/budget-allocation-analysis", response_model=List[BudgetAllocationResult])
async def analyze_budget_allocation(
    request: ROIOptimizationRequest,
    scenario_id: str = Query(..., description="Pareto frontier scenario ID to analyze")
):
    """
    Analyze budget allocation for a specific optimization scenario.
    
    This endpoint provides detailed budget allocation analysis for a specific
    scenario from the Pareto frontier, showing how budget is allocated across
    fields, nutrients, and products.
    
    **Analysis Components:**
    - Field-level budget allocation with priority scoring
    - Nutrient-specific budget allocation
    - Product-specific budget allocation
    - Budget utilization percentages
    - Expected ROI for each field
    - Constraint violation detection
    
    **Use Cases:**
    - Detailed budget allocation review
    - Field priority analysis
    - Budget utilization optimization
    - Constraint violation identification
    """
    try:
        logger.info(f"Analyzing budget allocation for scenario {scenario_id}")
        
        # Validate budget constraints are present
        if not request.constraints.budget_constraint:
            raise HTTPException(
                status_code=400, 
                detail="Budget constraints are required for budget allocation analysis"
            )
        
        # Perform full optimization to get Pareto frontier
        optimization_result = await budget_constraint_optimizer_service.optimize_budget_constraints(request)
        
        # Find the specified scenario
        scenario = None
        for point in optimization_result.pareto_frontier:
            if point.scenario_id == scenario_id:
                scenario = point
                break
        
        if not scenario:
            raise HTTPException(
                status_code=404, 
                detail=f"Scenario {scenario_id} not found in Pareto frontier"
            )
        
        # Get budget allocations for this scenario
        budget_allocations = optimization_result.budget_allocations
        
        logger.info(f"Budget allocation analysis completed for scenario {scenario_id}")
        
        return budget_allocations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in budget allocation analysis: {e}")
        raise HTTPException(status_code=500, detail="Budget allocation analysis failed")


@router.post("/constraint-relaxation-analysis", response_model=List[ConstraintRelaxationAnalysis])
async def analyze_constraint_relaxation(
    request: ROIOptimizationRequest,
    scenario_id: str = Query(..., description="Pareto frontier scenario ID to analyze")
):
    """
    Analyze the impact of relaxing various constraints.
    
    This endpoint provides comprehensive constraint relaxation analysis,
    showing the potential benefits and costs of relaxing different types
    of constraints in the optimization problem.
    
    **Constraint Types Analyzed:**
    - Total budget limit relaxation
    - Per-acre cost constraint relaxation
    - Nutrient rate constraint relaxation (N, P, K)
    - Environmental constraint relaxation
    - Risk constraint relaxation
    
    **Analysis Components:**
    - Impact on ROI and profitability
    - Environmental impact assessment
    - Yield improvement potential
    - Cost-benefit analysis
    - Recommendations for constraint relaxation
    
    **Use Cases:**
    - Constraint sensitivity analysis
    - Budget flexibility planning
    - Risk management optimization
    - Investment decision support
    """
    try:
        logger.info(f"Analyzing constraint relaxation for scenario {scenario_id}")
        
        # Validate budget constraints are present
        if not request.constraints.budget_constraint:
            raise HTTPException(
                status_code=400, 
                detail="Budget constraints are required for constraint relaxation analysis"
            )
        
        # Perform full optimization to get Pareto frontier
        optimization_result = await budget_constraint_optimizer_service.optimize_budget_constraints(request)
        
        # Find the specified scenario
        scenario = None
        for point in optimization_result.pareto_frontier:
            if point.scenario_id == scenario_id:
                scenario = point
                break
        
        if not scenario:
            raise HTTPException(
                status_code=404, 
                detail=f"Scenario {scenario_id} not found in Pareto frontier"
            )
        
        # Get constraint relaxation analysis for this scenario
        relaxation_analyses = optimization_result.constraint_relaxation_analysis
        
        logger.info(f"Constraint relaxation analysis completed for scenario {scenario_id}")
        
        return relaxation_analyses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in constraint relaxation analysis: {e}")
        raise HTTPException(status_code=500, detail="Constraint relaxation analysis failed")


@router.post("/pareto-frontier-analysis", response_model=List[ParetoFrontierPoint])
async def analyze_pareto_frontier(
    request: ROIOptimizationRequest
):
    """
    Generate and analyze Pareto frontier for multi-objective optimization.
    
    This endpoint generates the Pareto frontier showing the trade-offs
    between different objectives (profit, environment, risk) and provides
    detailed analysis of each scenario.
    
    **Pareto Frontier Scenarios:**
    - Pure profit maximization
    - Profit with environmental consideration
    - Balanced profit-environment
    - Environment-focused optimization
    - Pure environmental optimization
    - Profit with risk consideration
    - Balanced all objectives
    - Environment-risk focused
    - Pure risk minimization
    - Moderate balance scenarios
    
    **Analysis Components:**
    - Scenario comparison and ranking
    - Trade-off identification
    - Efficiency frontier analysis
    - Objective correlation analysis
    - Recommendation generation
    
    **Use Cases:**
    - Multi-objective decision making
    - Scenario comparison and selection
    - Trade-off analysis
    - Strategic planning support
    """
    try:
        logger.info("Generating Pareto frontier analysis")
        
        # Validate budget constraints are present
        if not request.constraints.budget_constraint:
            raise HTTPException(
                status_code=400, 
                detail="Budget constraints are required for Pareto frontier analysis"
            )
        
        # Perform full optimization to get Pareto frontier
        optimization_result = await budget_constraint_optimizer_service.optimize_budget_constraints(request)
        
        # Get Pareto frontier points
        pareto_frontier = optimization_result.pareto_frontier
        
        logger.info(f"Pareto frontier analysis completed with {len(pareto_frontier)} scenarios")
        
        return pareto_frontier
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Pareto frontier analysis: {e}")
        raise HTTPException(status_code=500, detail="Pareto frontier analysis failed")


@router.post("/trade-off-analysis")
async def analyze_trade_offs(
    request: ROIOptimizationRequest
):
    """
    Perform comprehensive trade-off analysis between optimization objectives.
    
    This endpoint provides detailed trade-off analysis showing the relationships
    between different objectives and their impact on optimization results.
    
    **Trade-off Analysis Components:**
    - Correlation analysis between objectives
    - Trade-off identification and severity assessment
    - Efficiency frontier analysis
    - Scenario recommendation based on goals
    - Objective interaction analysis
    
    **Objectives Analyzed:**
    - Profit maximization vs environmental impact
    - Profit maximization vs risk
    - Environmental impact vs risk
    - Yield target achievement vs cost
    - Budget utilization vs ROI
    
    **Use Cases:**
    - Strategic decision making
    - Objective prioritization
    - Risk management planning
    - Sustainability assessment
    - Investment optimization
    """
    try:
        logger.info("Performing trade-off analysis")
        
        # Validate budget constraints are present
        if not request.constraints.budget_constraint:
            raise HTTPException(
                status_code=400, 
                detail="Budget constraints are required for trade-off analysis"
            )
        
        # Perform full optimization to get trade-off analysis
        optimization_result = await budget_constraint_optimizer_service.optimize_budget_constraints(request)
        
        # Get trade-off analysis
        trade_off_analysis = optimization_result.trade_off_analysis
        
        logger.info("Trade-off analysis completed")
        
        return trade_off_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in trade-off analysis: {e}")
        raise HTTPException(status_code=500, detail="Trade-off analysis failed")


@router.get("/budget-constraint-features")
async def get_budget_constraint_features():
    """
    Get available budget constraint features and their descriptions.
    
    This endpoint provides information about all available budget constraint
    features and their characteristics for fertilizer strategy optimization.
    """
    try:
        features = {
            "budget_constraint_types": [
                {
                    "type": "total_budget_limit",
                    "name": "Total Budget Limit",
                    "description": "Maximum total budget across all fields",
                    "use_case": "Overall farm budget control"
                },
                {
                    "type": "per_field_budget_limit",
                    "name": "Per-Field Budget Limit",
                    "description": "Maximum budget allocation per field",
                    "use_case": "Individual field budget control"
                },
                {
                    "type": "per_acre_budget_limit",
                    "name": "Per-Acre Budget Limit",
                    "description": "Maximum budget per acre",
                    "use_case": "Cost control per unit area"
                },
                {
                    "type": "nutrient_budget_allocation",
                    "name": "Nutrient Budget Allocation",
                    "description": "Budget allocation by nutrient type (N, P, K)",
                    "use_case": "Nutrient-specific budget control"
                },
                {
                    "type": "product_budget_allocation",
                    "name": "Product Budget Allocation",
                    "description": "Budget allocation by fertilizer product",
                    "use_case": "Product-specific budget control"
                },
                {
                    "type": "seasonal_budget_allocation",
                    "name": "Seasonal Budget Allocation",
                    "description": "Budget allocation by season",
                    "use_case": "Seasonal budget planning"
                },
                {
                    "type": "priority_field_budget_multiplier",
                    "name": "Priority Field Budget Multiplier",
                    "description": "Budget multiplier for priority fields",
                    "use_case": "Priority field budget enhancement"
                }
            ],
            "optimization_features": [
                {
                    "feature": "pareto_frontier_analysis",
                    "name": "Pareto Frontier Analysis",
                    "description": "Multi-objective optimization with trade-off analysis",
                    "benefits": ["Scenario comparison", "Trade-off identification", "Objective balancing"]
                },
                {
                    "feature": "budget_allocation_optimization",
                    "name": "Budget Allocation Optimization",
                    "description": "Optimal budget allocation across fields and nutrients",
                    "benefits": ["Field prioritization", "Resource optimization", "ROI maximization"]
                },
                {
                    "feature": "constraint_relaxation_analysis",
                    "name": "Constraint Relaxation Analysis",
                    "description": "Analysis of relaxing various constraints",
                    "benefits": ["Flexibility assessment", "Cost-benefit analysis", "Risk management"]
                },
                {
                    "feature": "trade_off_analysis",
                    "name": "Trade-off Analysis",
                    "description": "Comprehensive analysis of objective trade-offs",
                    "benefits": ["Decision support", "Risk assessment", "Strategic planning"]
                }
            ],
            "multi_objective_optimization": {
                "objectives": ["profit_maximization", "environmental_minimization", "risk_minimization"],
                "methods": ["linear_programming", "quadratic_programming", "genetic_algorithm"],
                "constraints": ["budget_limits", "nutrient_rates", "environmental_limits", "risk_tolerance"]
            }
        }
        
        return features
        
    except Exception as e:
        logger.error(f"Error getting budget constraint features: {e}")
        raise HTTPException(status_code=500, detail="Failed to get budget constraint features")


@router.get("/health")
async def health_check():
    """Health check endpoint for budget constraint optimization service."""
    return {
        "service": "budget-constraint-optimization",
        "status": "healthy",
        "features": [
            "multi_objective_optimization",
            "pareto_frontier_analysis",
            "budget_allocation_optimization",
            "constraint_relaxation_analysis",
            "trade_off_analysis",
            "budget_constraint_handling",
            "field_priority_optimization",
            "nutrient_allocation_optimization",
            "scenario_comparison",
            "efficiency_frontier_analysis"
        ]
    }
