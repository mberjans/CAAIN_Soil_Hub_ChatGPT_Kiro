"""
API routes for goal-based fertilizer application method recommendations.
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from src.services.goal_based_recommendation_engine import (
    GoalBasedRecommendationEngine, OptimizationGoal, OptimizationConstraint,
    ConstraintType, GoalWeight
)
from src.models.application_models import ApplicationRequest, ApplicationResponse
from src.models.application_models import (
    FieldConditions, CropRequirements, FertilizerSpecification, EquipmentSpecification
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/goal-based", tags=["goal-based-recommendations"])


class FarmerGoalsRequest(BaseModel):
    """Request model for farmer goal preferences."""
    yield_maximization: float = Field(0.35, ge=0.0, le=1.0, description="Weight for yield maximization goal")
    cost_minimization: float = Field(0.25, ge=0.0, le=1.0, description="Weight for cost minimization goal")
    environmental_protection: float = Field(0.20, ge=0.0, le=1.0, description="Weight for environmental protection goal")
    labor_efficiency: float = Field(0.15, ge=0.0, le=1.0, description="Weight for labor efficiency goal")
    nutrient_efficiency: float = Field(0.05, ge=0.0, le=1.0, description="Weight for nutrient efficiency goal")


class ConstraintRequest(BaseModel):
    """Request model for optimization constraints."""
    constraint_type: str = Field(..., description="Type of constraint")
    constraint_value: Any = Field(..., description="Constraint value")
    operator: str = Field("le", description="Constraint operator (le, ge, eq)")
    penalty_weight: float = Field(1.0, ge=0.0, le=10.0, description="Penalty weight for constraint violation")


class GoalBasedOptimizationRequest(BaseModel):
    """Request model for goal-based optimization."""
    field_conditions: FieldConditions = Field(..., description="Field conditions and characteristics")
    crop_requirements: CropRequirements = Field(..., description="Crop requirements and preferences")
    fertilizer_specification: FertilizerSpecification = Field(..., description="Fertilizer specification")
    available_equipment: List[EquipmentSpecification] = Field(..., description="Available equipment")
    farmer_goals: Optional[FarmerGoalsRequest] = Field(None, description="Farmer goal preferences")
    constraints: Optional[List[ConstraintRequest]] = Field(None, description="Optimization constraints")
    optimization_method: str = Field("pareto_optimization", description="Optimization algorithm to use")


class OptimizationResultResponse(BaseModel):
    """Response model for optimization results."""
    request_id: str = Field(..., description="Unique request identifier")
    method_scores: Dict[str, float] = Field(..., description="Optimized method scores")
    pareto_front: List[Dict[str, Any]] = Field(..., description="Pareto optimal solutions")
    goal_achievements: Dict[str, float] = Field(..., description="Goal achievement percentages")
    constraint_violations: List[Dict[str, Any]] = Field(..., description="Constraint violations")
    optimization_time_ms: float = Field(..., description="Optimization processing time")
    convergence_info: Dict[str, Any] = Field(..., description="Optimization convergence information")
    recommendations: List[Dict[str, Any]] = Field(..., description="Detailed method recommendations")


# Dependency injection
async def get_goal_based_engine() -> GoalBasedRecommendationEngine:
    """Get goal-based recommendation engine instance."""
    return GoalBasedRecommendationEngine()


@router.post("/optimize", response_model=OptimizationResultResponse)
async def optimize_application_methods(
    request: GoalBasedOptimizationRequest,
    engine: GoalBasedRecommendationEngine = Depends(get_goal_based_engine)
):
    """
    Optimize fertilizer application methods using goal-based multi-objective optimization.
    
    This endpoint provides comprehensive optimization considering multiple farmer goals:
    - Yield maximization
    - Cost minimization  
    - Environmental protection
    - Labor efficiency
    - Nutrient efficiency
    
    The optimization uses advanced algorithms including Pareto optimization,
    constraint satisfaction, and multi-criteria decision analysis.
    
    Agricultural Use Cases:
    - Multi-objective fertilizer application planning
    - Equipment and resource optimization
    - Environmental compliance optimization
    - Labor and cost efficiency analysis
    """
    try:
        # Convert request to internal format
        application_request = ApplicationRequest(
            field_conditions=request.field_conditions,
            crop_requirements=request.crop_requirements,
            fertilizer_specification=request.fertilizer_specification,
            available_equipment=request.available_equipment
        )
        
        # Convert farmer goals
        farmer_goals = None
        if request.farmer_goals:
            farmer_goals = {
                OptimizationGoal.YIELD_MAXIMIZATION: request.farmer_goals.yield_maximization,
                OptimizationGoal.COST_MINIMIZATION: request.farmer_goals.cost_minimization,
                OptimizationGoal.ENVIRONMENTAL_PROTECTION: request.farmer_goals.environmental_protection,
                OptimizationGoal.LABOR_EFFICIENCY: request.farmer_goals.labor_efficiency,
                OptimizationGoal.NUTRIENT_EFFICIENCY: request.farmer_goals.nutrient_efficiency
            }
        
        # Convert constraints
        constraints = None
        if request.constraints:
            constraints = []
            for constraint_req in request.constraints:
                constraint_type = ConstraintType(constraint_req.constraint_type)
                constraint = OptimizationConstraint(
                    constraint_type=constraint_type,
                    constraint_value=constraint_req.constraint_value,
                    operator=constraint_req.operator,
                    penalty_weight=constraint_req.penalty_weight
                )
                constraints.append(constraint)
        
        # Perform optimization
        result = await engine.optimize_application_methods(
            application_request,
            farmer_goals=farmer_goals,
            constraints=constraints,
            optimization_method=request.optimization_method
        )
        
        # Generate detailed recommendations
        recommendations = await _generate_detailed_recommendations(
            result, application_request, engine
        )
        
        # Convert goal achievements to string keys for JSON serialization
        goal_achievements_str = {
            goal.value: achievement for goal, achievement in result.goal_achievements.items()
        }
        
        response = OptimizationResultResponse(
            request_id=str(uuid4()),
            method_scores=result.method_scores,
            pareto_front=result.pareto_front,
            goal_achievements=goal_achievements_str,
            constraint_violations=result.constraint_violations,
            optimization_time_ms=result.optimization_time_ms,
            convergence_info=result.convergence_info,
            recommendations=recommendations
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in goal-based optimization: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in goal-based optimization: {e}")
        raise HTTPException(status_code=500, detail="Goal-based optimization failed")


@router.get("/goals", response_model=Dict[str, Any])
async def get_available_goals():
    """
    Get available optimization goals and their descriptions.
    
    Returns information about all available optimization goals that can be
    used in the goal-based recommendation system.
    """
    goals_info = {
        "yield_maximization": {
            "name": "Yield Maximization",
            "description": "Maximize crop yield potential through optimal fertilizer application",
            "default_weight": 0.35,
            "priority": 1,
            "agricultural_importance": "High - Directly impacts farm profitability"
        },
        "cost_minimization": {
            "name": "Cost Minimization", 
            "description": "Minimize fertilizer application costs while maintaining effectiveness",
            "default_weight": 0.25,
            "priority": 2,
            "agricultural_importance": "High - Affects farm economics and sustainability"
        },
        "environmental_protection": {
            "name": "Environmental Protection",
            "description": "Minimize environmental impact and ensure regulatory compliance",
            "default_weight": 0.20,
            "priority": 3,
            "agricultural_importance": "High - Essential for sustainable farming"
        },
        "labor_efficiency": {
            "name": "Labor Efficiency",
            "description": "Optimize labor requirements and equipment utilization",
            "default_weight": 0.15,
            "priority": 4,
            "agricultural_importance": "Medium - Affects operational efficiency"
        },
        "nutrient_efficiency": {
            "name": "Nutrient Efficiency",
            "description": "Maximize nutrient use efficiency and minimize waste",
            "default_weight": 0.05,
            "priority": 5,
            "agricultural_importance": "Medium - Important for resource conservation"
        }
    }
    
    return {
        "available_goals": goals_info,
        "total_goals": len(goals_info),
        "default_total_weight": sum(goal["default_weight"] for goal in goals_info.values())
    }


@router.get("/constraints", response_model=Dict[str, Any])
async def get_available_constraints():
    """
    Get available constraint types and their descriptions.
    
    Returns information about all available constraint types that can be
    used to limit the optimization search space.
    """
    constraints_info = {
        "equipment_availability": {
            "name": "Equipment Availability",
            "description": "Limit methods to those compatible with available equipment",
            "default_penalty_weight": 2.0,
            "agricultural_importance": "Critical - Equipment compatibility is essential"
        },
        "field_size": {
            "name": "Field Size",
            "description": "Limit methods based on field size constraints",
            "default_penalty_weight": 1.0,
            "agricultural_importance": "High - Affects method feasibility"
        },
        "budget_limit": {
            "name": "Budget Limit",
            "description": "Limit methods based on available budget",
            "default_penalty_weight": 3.0,
            "agricultural_importance": "Critical - Budget constraints are fundamental"
        },
        "labor_capacity": {
            "name": "Labor Capacity",
            "description": "Limit methods based on available labor resources",
            "default_penalty_weight": 1.5,
            "agricultural_importance": "Medium - Labor availability affects feasibility"
        },
        "environmental_regulations": {
            "name": "Environmental Regulations",
            "description": "Ensure compliance with environmental regulations",
            "default_penalty_weight": 5.0,
            "agricultural_importance": "Critical - Regulatory compliance is mandatory"
        },
        "timing_constraints": {
            "name": "Timing Constraints",
            "description": "Limit methods based on application timing requirements",
            "default_penalty_weight": 1.0,
            "agricultural_importance": "Medium - Timing affects method effectiveness"
        }
    }
    
    return {
        "available_constraints": constraints_info,
        "total_constraints": len(constraints_info),
        "constraint_operators": ["le", "ge", "eq"]
    }


@router.get("/optimization-methods", response_model=Dict[str, Any])
async def get_optimization_methods():
    """
    Get available optimization methods and their characteristics.
    
    Returns information about all available optimization algorithms
    that can be used for multi-objective optimization.
    """
    methods_info = {
        "pareto_optimization": {
            "name": "Pareto Optimization",
            "description": "Find Pareto-optimal solutions that balance multiple objectives",
            "best_for": "Multi-objective optimization with conflicting goals",
            "characteristics": ["Non-dominated solutions", "Diversity preservation", "No single best solution"],
            "agricultural_applications": "Ideal for balancing yield, cost, and environmental goals"
        },
        "weighted_sum": {
            "name": "Weighted Sum Optimization",
            "description": "Combine multiple objectives into a single weighted objective function",
            "best_for": "Clear goal priorities and preferences",
            "characteristics": ["Single optimal solution", "Fast computation", "Requires weight specification"],
            "agricultural_applications": "Good when farmer has clear preferences for goal priorities"
        },
        "constraint_satisfaction": {
            "name": "Constraint Satisfaction",
            "description": "Find solutions that satisfy all specified constraints",
            "best_for": "Strict constraint requirements",
            "characteristics": ["Constraint-driven", "Feasible solutions only", "Constraint relaxation"],
            "agricultural_applications": "Essential for regulatory compliance and equipment limitations"
        },
        "genetic_algorithm": {
            "name": "Genetic Algorithm",
            "description": "Evolutionary optimization inspired by natural selection",
            "best_for": "Complex optimization landscapes",
            "characteristics": ["Population-based", "Global search", "Handles non-linear objectives"],
            "agricultural_applications": "Useful for complex multi-variable optimization problems"
        }
    }
    
    return {
        "available_methods": methods_info,
        "total_methods": len(methods_info),
        "default_method": "pareto_optimization",
        "recommendation": "Start with Pareto optimization for most agricultural applications"
    }


@router.post("/compare-methods", response_model=Dict[str, Any])
async def compare_optimization_methods(
    request: GoalBasedOptimizationRequest,
    engine: GoalBasedRecommendationEngine = Depends(get_goal_based_engine)
):
    """
    Compare results from different optimization methods.
    
    This endpoint runs the same optimization problem using multiple
    algorithms and compares their results to help farmers understand
    the trade-offs between different approaches.
    """
    try:
        # Convert request to internal format
        application_request = ApplicationRequest(
            field_conditions=request.field_conditions,
            crop_requirements=request.crop_requirements,
            fertilizer_specification=request.fertilizer_specification,
            available_equipment=request.available_equipment
        )
        
        # Convert farmer goals
        farmer_goals = None
        if request.farmer_goals:
            farmer_goals = {
                OptimizationGoal.YIELD_MAXIMIZATION: request.farmer_goals.yield_maximization,
                OptimizationGoal.COST_MINIMIZATION: request.farmer_goals.cost_minimization,
                OptimizationGoal.ENVIRONMENTAL_PROTECTION: request.farmer_goals.environmental_protection,
                OptimizationGoal.LABOR_EFFICIENCY: request.farmer_goals.labor_efficiency,
                OptimizationGoal.NUTRIENT_EFFICIENCY: request.farmer_goals.nutrient_efficiency
            }
        
        # Convert constraints
        constraints = None
        if request.constraints:
            constraints = []
            for constraint_req in request.constraints:
                constraint_type = ConstraintType(constraint_req.constraint_type)
                constraint = OptimizationConstraint(
                    constraint_type=constraint_type,
                    constraint_value=constraint_req.constraint_value,
                    operator=constraint_req.operator,
                    penalty_weight=constraint_req.penalty_weight
                )
                constraints.append(constraint)
        
        # Run optimization with different methods
        methods_to_compare = ["pareto_optimization", "weighted_sum", "constraint_satisfaction"]
        comparison_results = {}
        
        for method in methods_to_compare:
            try:
                result = await engine.optimize_application_methods(
                    application_request,
                    farmer_goals=farmer_goals,
                    constraints=constraints,
                    optimization_method=method
                )
                
                comparison_results[method] = {
                    "method_scores": result.method_scores,
                    "optimization_time_ms": result.optimization_time_ms,
                    "convergence_info": result.convergence_info,
                    "constraint_violations_count": len(result.constraint_violations)
                }
                
            except Exception as e:
                logger.warning(f"Method {method} failed: {e}")
                comparison_results[method] = {
                    "error": str(e),
                    "status": "failed"
                }
        
        return {
            "request_id": str(uuid4()),
            "comparison_results": comparison_results,
            "methods_compared": methods_to_compare,
            "successful_methods": len([r for r in comparison_results.values() if "error" not in r]),
            "recommendation": _generate_method_recommendation(comparison_results)
        }
        
    except Exception as e:
        logger.error(f"Error in method comparison: {e}")
        raise HTTPException(status_code=500, detail="Method comparison failed")


@router.get("/health")
async def health_check():
    """Health check endpoint for goal-based recommendation service."""
    return {
        "status": "healthy",
        "service": "goal-based-recommendations",
        "version": "1.0.0",
        "features": [
            "multi_objective_optimization",
            "pareto_optimization", 
            "constraint_satisfaction",
            "goal_prioritization"
        ]
    }


# Helper functions
async def _generate_detailed_recommendations(
    result, 
    application_request: ApplicationRequest,
    engine: GoalBasedRecommendationEngine
) -> List[Dict[str, Any]]:
    """Generate detailed recommendations from optimization results."""
    recommendations = []
    
    # Sort methods by score
    sorted_methods = sorted(result.method_scores.items(), key=lambda x: x[1], reverse=True)
    
    for method_type, score in sorted_methods:
        recommendation = {
            "method_type": method_type,
            "optimization_score": score,
            "rank": len(recommendations) + 1,
            "goal_contributions": {
                "yield_maximization": 0.0,
                "cost_minimization": 0.0,
                "environmental_protection": 0.0,
                "labor_efficiency": 0.0,
                "nutrient_efficiency": 0.0
            },
            "constraint_status": "satisfied",
            "implementation_notes": f"Optimized for {method_type} application method"
        }
        recommendations.append(recommendation)
    
    return recommendations


def _generate_method_recommendation(comparison_results: Dict[str, Any]) -> str:
    """Generate recommendation based on comparison results."""
    successful_results = {k: v for k, v in comparison_results.items() if "error" not in v}
    
    if not successful_results:
        return "No optimization methods succeeded. Check input parameters."
    
    # Find method with best balance of speed and solution quality
    best_method = min(successful_results.items(), 
                     key=lambda x: x[1]["optimization_time_ms"])
    
    return f"Recommended method: {best_method[0]} (fastest execution: {best_method[1]['optimization_time_ms']:.2f}ms)"