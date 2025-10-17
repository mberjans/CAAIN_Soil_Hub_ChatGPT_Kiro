"""
Sustainability Optimization API Routes.

This module provides REST API endpoints for advanced sustainability optimization,
environmental metrics calculation, multi-objective optimization, and sustainability scoring.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime
import logging

from ..models.environmental_models import (
    EnvironmentalImpactAssessment, SustainabilityMetrics, EnvironmentalImpactLevel
)
from ..services.environmental_optimization_service import (
    SustainabilityOptimizationService, OptimizationObjective, OptimizationConstraint,
    SustainabilityOptimizationResult
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/sustainability", tags=["sustainability-optimization"])

# Dependency injection
async def get_sustainability_service() -> SustainabilityOptimizationService:
    """Get sustainability optimization service instance."""
    return SustainabilityOptimizationService()


@router.post("/optimize", response_model=SustainabilityOptimizationResult)
async def optimize_sustainability(
    field_id: UUID = Body(..., description="Field identifier"),
    field_data: Dict[str, Any] = Body(..., description="Field characteristics and soil data"),
    fertilizer_options: List[Dict[str, Any]] = Body(..., description="Available fertilizer options"),
    optimization_objectives: Optional[List[Dict[str, Any]]] = Body(None, description="Custom optimization objectives"),
    constraints: Optional[List[Dict[str, Any]]] = Body(None, description="Custom optimization constraints"),
    optimization_method: str = Body("genetic_algorithm", description="Optimization algorithm to use"),
    include_trade_off_analysis: bool = Body(True, description="Include trade-off analysis"),
    service: SustainabilityOptimizationService = Depends(get_sustainability_service)
):
    """
    Perform comprehensive sustainability optimization for a field.
    
    This endpoint provides advanced sustainability optimization capabilities including:
    - Multi-objective optimization (environmental, economic, efficiency)
    - Environmental impact assessment
    - Sustainability metrics calculation
    - Trade-off analysis between different objectives
    - Carbon footprint tracking
    - Comprehensive recommendations
    
    Features:
    - Multiple optimization algorithms (genetic algorithm, gradient descent, etc.)
    - Customizable objectives and constraints
    - Environmental impact minimization
    - Economic return optimization
    - Nutrient use efficiency maximization
    - Water quality protection
    - Soil health improvement
    
    Agricultural Use Cases:
    - Sustainable fertilizer strategy development
    - Environmental compliance optimization
    - Multi-objective decision making
    - Sustainability certification support
    - Long-term farm planning
    - Conservation program participation
    """
    try:
        # Convert objectives if provided
        objectives = None
        if optimization_objectives:
            objectives = [
                OptimizationObjective(
                    name=obj['name'],
                    weight=obj['weight'],
                    target_value=obj.get('target_value'),
                    minimize=obj.get('minimize', True)
                )
                for obj in optimization_objectives
            ]
        
        # Convert constraints if provided
        constraints_list = None
        if constraints:
            constraints_list = [
                OptimizationConstraint(
                    name=constraint['name'],
                    constraint_type=constraint['constraint_type'],
                    value=constraint['value'],
                    field=constraint.get('field')
                )
                for constraint in constraints
            ]
        
        result = await service.optimize_sustainability(
            field_id=field_id,
            field_data=field_data,
            fertilizer_options=fertilizer_options,
            optimization_objectives=objectives,
            constraints=constraints_list,
            optimization_method=optimization_method,
            include_trade_off_analysis=include_trade_off_analysis
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error performing sustainability optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-scenarios", response_model=Dict[str, Any])
async def compare_optimization_scenarios(
    field_id: UUID = Body(..., description="Field identifier"),
    scenarios: List[Dict[str, Any]] = Body(..., description="Optimization scenarios to compare"),
    service: SustainabilityOptimizationService = Depends(get_sustainability_service)
):
    """
    Compare different sustainability optimization scenarios.
    
    This endpoint allows comparison of multiple optimization scenarios to help farmers
    make informed decisions about their fertilizer strategies.
    
    Features:
    - Side-by-side scenario comparison
    - Ranking by optimization score
    - Environmental impact comparison
    - Economic analysis comparison
    - Recommendation differences
    - Trade-off analysis
    
    Agricultural Use Cases:
    - Evaluating different farm management approaches
    - Comparing environmental vs economic priorities
    - Decision support for fertilizer strategy selection
    - Scenario planning and risk assessment
    - Stakeholder communication and reporting
    """
    try:
        result = await service.compare_optimization_scenarios(
            field_id=field_id,
            scenarios=scenarios
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error comparing optimization scenarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{field_id}", response_model=List[Dict[str, Any]])
async def get_optimization_history(
    field_id: UUID = Path(..., description="Field identifier"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of optimizations to return"),
    service: SustainabilityOptimizationService = Depends(get_sustainability_service)
):
    """
    Get sustainability optimization history for a field.
    
    Returns historical optimization results with trend analysis and performance tracking
    for continuous improvement of sustainability practices.
    
    Features:
    - Historical optimization results
    - Performance trend analysis
    - Sustainability score tracking
    - Environmental impact trends
    - Recommendation evolution
    - Success rate analysis
    
    Agricultural Use Cases:
    - Performance tracking over time
    - Sustainability improvement monitoring
    - Historical analysis and reporting
    - Learning from past optimizations
    - Continuous improvement planning
    """
    try:
        results = await service.get_optimization_history(field_id, limit)
        
        # Convert results to dict format for JSON response
        return [result.__dict__ for result in results]
        
    except Exception as e:
        logger.error(f"Error getting optimization history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/objectives", response_model=List[Dict[str, Any]])
async def get_default_objectives(
    service: SustainabilityOptimizationService = Depends(get_sustainability_service)
):
    """
    Get default optimization objectives for sustainability optimization.
    
    Returns the standard optimization objectives used in sustainability optimization
    including weights, targets, and descriptions.
    
    Features:
    - Standard optimization objectives
    - Objective weights and priorities
    - Target value ranges
    - Minimization/maximization preferences
    - Agricultural relevance descriptions
    
    Agricultural Use Cases:
    - Understanding optimization parameters
    - Customizing optimization objectives
    - Educational purposes
    - System configuration
    - Objective validation
    """
    try:
        objectives = service.default_objectives
        
        return [
            {
                "name": obj.name,
                "weight": obj.weight,
                "target_value": obj.target_value,
                "minimize": obj.minimize,
                "description": f"Optimize {obj.name.replace('_', ' ')}"
            }
            for obj in objectives
        ]
        
    except Exception as e:
        logger.error(f"Error getting default objectives: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/constraints", response_model=List[Dict[str, Any]])
async def get_default_constraints(
    service: SustainabilityOptimizationService = Depends(get_sustainability_service)
):
    """
    Get default optimization constraints for sustainability optimization.
    
    Returns the standard optimization constraints used in sustainability optimization
    including bounds, limits, and regulatory requirements.
    
    Features:
    - Standard optimization constraints
    - Regulatory compliance limits
    - Safety bounds and limits
    - Field-specific constraints
    - Constraint type definitions
    
    Agricultural Use Cases:
    - Understanding constraint parameters
    - Customizing optimization constraints
    - Regulatory compliance checking
    - Safety limit validation
    - System configuration
    """
    try:
        constraints = service.default_constraints
        
        return [
            {
                "name": constraint.name,
                "constraint_type": constraint.constraint_type,
                "value": constraint.value,
                "field": constraint.field,
                "description": f"Constraint on {constraint.field or 'general'} - {constraint.name.replace('_', ' ')}"
            }
            for constraint in constraints
        ]
        
    except Exception as e:
        logger.error(f"Error getting default constraints: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/methods", response_model=List[Dict[str, Any]])
async def get_optimization_methods(
    service: SustainabilityOptimizationService = Depends(get_sustainability_service)
):
    """
    Get available optimization methods for sustainability optimization.
    
    Returns the available optimization algorithms and their characteristics
    for sustainability optimization problems.
    
    Features:
    - Available optimization algorithms
    - Algorithm characteristics and performance
    - Use case recommendations
    - Convergence properties
    - Computational requirements
    
    Agricultural Use Cases:
    - Selecting appropriate optimization method
    - Understanding algorithm trade-offs
    - Performance optimization
    - Educational purposes
    - System configuration
    """
    try:
        methods = [
            {
                "name": "genetic_algorithm",
                "description": "Genetic algorithm optimization - good for complex multi-objective problems",
                "convergence": "Global optimization",
                "speed": "Medium",
                "recommended_for": "Complex multi-objective problems with multiple local optima"
            },
            {
                "name": "gradient_descent",
                "description": "Gradient descent optimization - fast convergence for smooth problems",
                "convergence": "Local optimization",
                "speed": "Fast",
                "recommended_for": "Smooth objective functions with single optimum"
            },
            {
                "name": "simulated_annealing",
                "description": "Simulated annealing optimization - good for escaping local optima",
                "convergence": "Global optimization",
                "speed": "Slow",
                "recommended_for": "Problems with many local optima"
            },
            {
                "name": "particle_swarm",
                "description": "Particle swarm optimization - good for continuous optimization",
                "convergence": "Global optimization",
                "speed": "Medium",
                "recommended_for": "Continuous optimization problems"
            }
        ]
        
        return methods
        
    except Exception as e:
        logger.error(f"Error getting optimization methods: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/environmental-impact", response_model=EnvironmentalImpactAssessment)
async def calculate_environmental_impact(
    field_id: UUID = Body(..., description="Field identifier"),
    fertilizer_rates: Dict[str, float] = Body(..., description="Fertilizer application rates"),
    field_data: Dict[str, Any] = Body(..., description="Field characteristics"),
    service: SustainabilityOptimizationService = Depends(get_sustainability_service)
):
    """
    Calculate environmental impact for given fertilizer rates.
    
    This endpoint calculates the environmental impact of specific fertilizer
    application rates without performing full optimization.
    
    Features:
    - Environmental impact assessment
    - Nutrient loss estimation
    - Carbon footprint calculation
    - Risk level determination
    - Mitigation recommendations
    - Buffer zone recommendations
    
    Agricultural Use Cases:
    - Quick environmental impact assessment
    - Pre-application impact evaluation
    - Environmental compliance checking
    - Impact comparison between scenarios
    - Risk assessment and mitigation planning
    """
    try:
        # Create mock optimization result for impact calculation
        optimization_result = {
            'optimal_rates': fertilizer_rates,
            'confidence': 0.8
        }
        
        impact = await service._calculate_environmental_impact(
            field_id, optimization_result, field_data
        )
        
        return impact
        
    except Exception as e:
        logger.error(f"Error calculating environmental impact: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sustainability-metrics", response_model=SustainabilityMetrics)
async def calculate_sustainability_metrics(
    field_id: UUID = Body(..., description="Field identifier"),
    fertilizer_rates: Dict[str, float] = Body(..., description="Fertilizer application rates"),
    field_data: Dict[str, Any] = Body(..., description="Field characteristics"),
    service: SustainabilityOptimizationService = Depends(get_sustainability_service)
):
    """
    Calculate sustainability metrics for given fertilizer rates.
    
    This endpoint calculates comprehensive sustainability metrics for specific
    fertilizer application rates without performing full optimization.
    
    Features:
    - Nutrient use efficiency calculation
    - Environmental sustainability metrics
    - Economic sustainability measures
    - Soil health indicators
    - Overall sustainability scoring
    - Performance benchmarking
    
    Agricultural Use Cases:
    - Sustainability performance assessment
    - Benchmarking against standards
    - Sustainability reporting
    - Performance tracking
    - Improvement planning
    - Certification support
    """
    try:
        # Create mock optimization result for metrics calculation
        optimization_result = {
            'optimal_rates': fertilizer_rates,
            'confidence': 0.8
        }
        
        metrics = await service._calculate_sustainability_metrics(
            field_id, optimization_result, field_data
        )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating sustainability metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for sustainability optimization service."""
    return {
        "service": "sustainability-optimization",
        "status": "healthy",
        "features": [
            "multi_objective_optimization",
            "environmental_impact_assessment",
            "sustainability_metrics_calculation",
            "carbon_footprint_tracking",
            "trade_off_analysis",
            "scenario_comparison",
            "optimization_history_tracking",
            "comprehensive_recommendations",
            "genetic_algorithm_optimization",
            "gradient_descent_optimization",
            "simulated_annealing_optimization",
            "particle_swarm_optimization",
            "nutrient_use_efficiency_optimization",
            "water_quality_protection",
            "soil_health_improvement",
            "economic_sustainability_analysis",
            "environmental_compliance_optimization",
            "sustainability_certification_support"
        ]
    }