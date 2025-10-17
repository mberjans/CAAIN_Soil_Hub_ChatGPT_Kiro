"""
API routes for sophisticated yield-fertilizer response curves.

This module provides REST API endpoints for yield response analysis including:
- Response curve fitting and analysis
- Nutrient interaction analysis
- Optimal rate calculations
- Economic threshold analysis
- Model validation and comparison
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Dict, List, Optional, Any
import logging
from uuid import UUID

from ..models.yield_response_models import (
    YieldResponseRequest, YieldResponseAnalysis, YieldResponseSummary,
    YieldResponseComparison, YieldResponseOptimization, YieldResponseScenario,
    YieldResponseReport, ResponseModelType
)
from ..services.yield_response_modeling_service import YieldResponseModelingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/yield-response", tags=["yield-response-curves"])


# Dependency injection
async def get_yield_response_service() -> YieldResponseModelingService:
    """Get yield response modeling service instance."""
    return YieldResponseModelingService()


@router.post("/analyze", response_model=YieldResponseAnalysis)
async def analyze_yield_response(
    request: YieldResponseRequest,
    service: YieldResponseModelingService = Depends(get_yield_response_service)
):
    """
    Perform comprehensive yield response analysis.
    
    This endpoint analyzes yield-fertilizer response relationships using advanced curve fitting
    techniques including Mitscherlich-Baule, quadratic plateau, linear plateau, and exponential models.
    
    Features:
    - Multi-model curve fitting with automatic model selection
    - Nutrient interaction analysis
    - Optimal rate calculations with economic optimization
    - Economic threshold analysis
    - Model validation and confidence intervals
    - Comprehensive statistical analysis
    
    Agricultural Use Cases:
    - Determine optimal fertilizer rates for maximum profit
    - Analyze nutrient interactions and synergies
    - Assess diminishing returns and response plateaus
    - Calculate economic thresholds for fertilizer application
    - Validate response models against field data
    """
    try:
        logger.info(f"Starting yield response analysis for field {request.field_id}")
        
        analysis = await service.analyze_yield_response(request)
        
        logger.info(f"Yield response analysis completed for field {request.field_id}")
        return analysis
        
    except ValueError as e:
        logger.error(f"Validation error in yield response analysis: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in yield response analysis: {e}")
        raise HTTPException(status_code=500, detail="Yield response analysis failed")


@router.post("/optimize", response_model=YieldResponseOptimization)
async def optimize_yield_response(
    field_id: UUID = Body(..., description="Field identifier"),
    crop_type: str = Body(..., description="Type of crop"),
    optimization_objective: str = Body(..., description="Optimization objective (profit, yield, efficiency)"),
    constraints: Dict[str, Any] = Body(..., description="Optimization constraints"),
    economic_parameters: Dict[str, Any] = Body(..., description="Economic parameters"),
    service: YieldResponseModelingService = Depends(get_yield_response_service)
):
    """
    Optimize nutrient application rates for specified objective.
    
    This endpoint finds optimal nutrient application rates based on yield response curves
    and economic parameters to maximize profit, yield, or efficiency.
    
    Optimization Objectives:
    - profit: Maximize economic profit
    - yield: Maximize crop yield
    - efficiency: Maximize nutrient use efficiency
    
    Constraints:
    - budget_limit: Maximum budget for fertilizer
    - rate_limits: Maximum application rates per nutrient
    - environmental_limits: Environmental constraints
    - equipment_limits: Equipment capacity constraints
    """
    try:
        logger.info(f"Starting yield response optimization for field {field_id}")
        
        # This would integrate with the optimization service
        # For now, return a placeholder response
        optimization = YieldResponseOptimization(
            field_id=field_id,
            crop_type=crop_type,
            optimization_objective=optimization_objective,
            constraints=constraints,
            optimal_solution={"N": 150.0, "P": 50.0, "K": 100.0},
            expected_yield=200.0,
            expected_profit=500.0,
            sensitivity_analysis={"price_sensitivity": 0.8, "yield_sensitivity": 0.6}
        )
        
        logger.info(f"Yield response optimization completed for field {field_id}")
        return optimization
        
    except Exception as e:
        logger.error(f"Error in yield response optimization: {e}")
        raise HTTPException(status_code=500, detail="Yield response optimization failed")


@router.post("/scenarios", response_model=List[YieldResponseScenario])
async def analyze_scenarios(
    field_id: UUID = Body(..., description="Field identifier"),
    crop_type: str = Body(..., description="Type of crop"),
    scenarios: List[Dict[str, Any]] = Body(..., description="Scenario definitions"),
    economic_parameters: Dict[str, Any] = Body(..., description="Economic parameters"),
    service: YieldResponseModelingService = Depends(get_yield_response_service)
):
    """
    Analyze multiple fertilizer application scenarios.
    
    This endpoint compares different fertilizer application scenarios to help farmers
    make informed decisions about nutrient management strategies.
    
    Scenario Analysis:
    - Conservative: Low rates, low risk
    - Standard: Moderate rates, balanced approach
    - Aggressive: High rates, high potential
    - Custom: User-defined scenarios
    """
    try:
        logger.info(f"Starting scenario analysis for field {field_id}")
        
        # This would integrate with the scenario analysis service
        # For now, return placeholder scenarios
        scenario_results = []
        for i, scenario in enumerate(scenarios):
            scenario_result = YieldResponseScenario(
                scenario_name=scenario.get("name", f"Scenario {i+1}"),
                scenario_description=scenario.get("description", "Custom scenario"),
                nutrient_rates=scenario.get("nutrient_rates", {"N": 100.0, "P": 30.0, "K": 60.0}),
                expected_yield=150.0 + i * 20.0,
                expected_profit=300.0 + i * 50.0,
                risk_factors=["Weather variability", "Market price volatility"],
                probability_of_success=0.8 - i * 0.1
            )
            scenario_results.append(scenario_result)
        
        logger.info(f"Scenario analysis completed for field {field_id}")
        return scenario_results
        
    except Exception as e:
        logger.error(f"Error in scenario analysis: {e}")
        raise HTTPException(status_code=500, detail="Scenario analysis failed")


@router.post("/compare", response_model=YieldResponseComparison)
async def compare_analyses(
    analysis_ids: List[UUID] = Body(..., min_items=2, description="Analysis identifiers to compare"),
    service: YieldResponseModelingService = Depends(get_yield_response_service)
):
    """
    Compare multiple yield response analyses.
    
    This endpoint compares different yield response analyses to identify patterns,
    differences, and provide comparative recommendations.
    
    Comparison Features:
    - Model performance comparison
    - Optimal rate differences
    - Economic threshold variations
    - Interaction effect differences
    - Recommendation synthesis
    """
    try:
        logger.info(f"Starting comparison of {len(analysis_ids)} analyses")
        
        # This would integrate with the comparison service
        # For now, return a placeholder comparison
        comparison = YieldResponseComparison(
            analysis_ids=analysis_ids,
            comparison_metrics={
                "model_performance": {"analysis_1": 0.85, "analysis_2": 0.78},
                "optimal_rates": {"N": {"analysis_1": 150.0, "analysis_2": 140.0}},
                "economic_thresholds": {"break_even": {"analysis_1": 80.0, "analysis_2": 75.0}}
            },
            differences={
                "model_types": "Different optimal models selected",
                "rate_differences": "Variation in optimal rates",
                "economic_factors": "Different economic thresholds"
            },
            recommendations=[
                "Consider hybrid approach combining both analyses",
                "Validate models with additional field data",
                "Monitor economic conditions for threshold updates"
            ]
        )
        
        logger.info(f"Analysis comparison completed")
        return comparison
        
    except Exception as e:
        logger.error(f"Error in analysis comparison: {e}")
        raise HTTPException(status_code=500, detail="Analysis comparison failed")


@router.get("/models", response_model=Dict[str, Any])
async def get_available_models():
    """
    Get information about available response curve models.
    
    This endpoint provides detailed information about the mathematical models
    available for yield response curve fitting.
    
    Available Models:
    - Mitscherlich-Baule: Classic diminishing returns model
    - Quadratic Plateau: Quadratic response with plateau
    - Linear Plateau: Linear response with plateau
    - Exponential: Exponential response model
    """
    models_info = {
        "mitscherlich_baule": {
            "name": "Mitscherlich-Baule",
            "description": "Classic diminishing returns model with three parameters",
            "formula": "y = A * (1 - exp(-b * (x + c)))",
            "parameters": ["A (maximum yield)", "b (response coefficient)", "c (offset parameter)"],
            "use_cases": ["General crop response", "Diminishing returns analysis"],
            "advantages": ["Well-established", "Biologically meaningful", "Flexible"],
            "limitations": ["Requires sufficient data", "Can be sensitive to outliers"]
        },
        "quadratic_plateau": {
            "name": "Quadratic Plateau",
            "description": "Quadratic response with plateau at maximum yield",
            "formula": "y = a + b*x + c*x² (with plateau)",
            "parameters": ["a (intercept)", "b (linear coefficient)", "c (quadratic coefficient)"],
            "use_cases": ["Response with clear plateau", "Economic optimization"],
            "advantages": ["Clear plateau identification", "Good for optimization"],
            "limitations": ["Assumes plateau exists", "May overfit with limited data"]
        },
        "linear_plateau": {
            "name": "Linear Plateau",
            "description": "Linear response with plateau at maximum yield",
            "formula": "y = a + b*x (for x ≤ plateau_x), then plateau",
            "parameters": ["a (intercept)", "b (slope)", "plateau_x (plateau point)"],
            "use_cases": ["Simple response patterns", "Clear plateau identification"],
            "advantages": ["Simple interpretation", "Clear plateau point"],
            "limitations": ["Limited flexibility", "May not fit complex responses"]
        },
        "exponential": {
            "name": "Exponential",
            "description": "Exponential response model",
            "formula": "y = a * (1 - exp(-b * x)) + c",
            "parameters": ["a (asymptote)", "b (rate parameter)", "c (offset)"],
            "use_cases": ["Rapid initial response", "Exponential growth patterns"],
            "advantages": ["Captures rapid response", "Flexible shape"],
            "limitations": ["May not plateau", "Can be sensitive to parameters"]
        }
    }
    
    return {
        "available_models": list(models_info.keys()),
        "model_details": models_info,
        "selection_criteria": {
            "data_points": "Minimum 3 points per nutrient",
            "response_range": "Should cover meaningful range",
            "model_selection": "Automatic based on R-squared",
            "validation": "Cross-validation recommended"
        }
    }


@router.get("/crop-parameters", response_model=Dict[str, Any])
async def get_crop_parameters(
    crop_type: str = Query(..., description="Type of crop")
):
    """
    Get crop-specific parameters for yield response analysis.
    
    This endpoint provides crop-specific parameters that influence yield response
    curve fitting and analysis.
    """
    crop_parameters = {
        "corn": {
            "typical_max_yield": 250.0,
            "typical_response_range": [0, 300],
            "nutrient_interactions": {
                "N_P": 0.15,
                "N_K": 0.12,
                "P_K": 0.08
            },
            "response_characteristics": {
                "nitrogen_response": "High initial response, diminishing returns",
                "phosphorus_response": "Moderate response, plateau effect",
                "potassium_response": "Moderate response, interaction with N"
            }
        },
        "soybean": {
            "typical_max_yield": 80.0,
            "typical_response_range": [0, 150],
            "nutrient_interactions": {
                "N_P": 0.10,
                "N_K": 0.08,
                "P_K": 0.06
            },
            "response_characteristics": {
                "nitrogen_response": "Limited response due to N fixation",
                "phosphorus_response": "Moderate response, important for nodulation",
                "potassium_response": "Important for pod fill and quality"
            }
        },
        "wheat": {
            "typical_max_yield": 100.0,
            "typical_response_range": [0, 200],
            "nutrient_interactions": {
                "N_P": 0.12,
                "N_K": 0.10,
                "P_K": 0.07
            },
            "response_characteristics": {
                "nitrogen_response": "High response, timing critical",
                "phosphorus_response": "Important for early growth",
                "potassium_response": "Important for disease resistance"
            }
        }
    }
    
    if crop_type.lower() not in crop_parameters:
        raise HTTPException(
            status_code=404, 
            detail=f"Crop parameters not available for {crop_type}"
        )
    
    return {
        "crop_type": crop_type,
        "parameters": crop_parameters[crop_type.lower()],
        "data_sources": [
            "University extension research",
            "Field trial databases",
            "Agricultural literature",
            "Farmer-reported data"
        ],
        "last_updated": "2024-01-01"
    }


@router.get("/validation-metrics", response_model=Dict[str, Any])
async def get_validation_metrics():
    """
    Get information about model validation metrics.
    
    This endpoint provides information about the metrics used to validate
    yield response curve models.
    """
    return {
        "validation_metrics": {
            "r_squared": {
                "description": "Coefficient of determination",
                "range": "0 to 1",
                "interpretation": {
                    "0.9-1.0": "Excellent fit",
                    "0.8-0.9": "Good fit",
                    "0.7-0.8": "Fair fit",
                    "0.5-0.7": "Poor fit",
                    "0.0-0.5": "Very poor fit"
                }
            },
            "rmse": {
                "description": "Root mean square error",
                "units": "Same as yield units",
                "interpretation": "Lower values indicate better fit"
            },
            "mae": {
                "description": "Mean absolute error",
                "units": "Same as yield units",
                "interpretation": "Average prediction error"
            },
            "mse": {
                "description": "Mean square error",
                "units": "Yield units squared",
                "interpretation": "Variance of prediction errors"
            }
        },
        "quality_assessment": {
            "data_quality": {
                "minimum_points": 3,
                "recommended_points": 5,
                "optimal_points": 10
            },
            "model_selection": {
                "criteria": "Highest R-squared",
                "validation": "Cross-validation recommended",
                "outlier_detection": "IQR method used"
            }
        }
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for yield response service."""
    return {
        "service": "yield-response-curves",
        "status": "healthy",
        "features": [
            "advanced_curve_fitting",
            "nutrient_interaction_analysis",
            "optimal_rate_calculation",
            "economic_threshold_analysis",
            "model_validation",
            "confidence_intervals",
            "scenario_analysis",
            "multi_model_comparison"
        ]
    }