"""
API routes for sophisticated fertilizer application method selection.

This module provides REST API endpoints for advanced method selection using:
- Machine learning algorithms
- Multi-criteria optimization
- Constraint satisfaction
- Fuzzy logic for uncertainty handling
- Ensemble decision making
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from src.services.sophisticated_method_selection_service import (
    SophisticatedMethodSelectionService, 
    OptimizationObjective, 
    OptimizationConstraints,
    UncertaintyLevel
)
from src.models.application_models import (
    ApplicationRequest, ApplicationResponse, ApplicationMethod,
    FieldConditions, CropRequirements, FertilizerSpecification, EquipmentSpecification
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/sophisticated-methods", tags=["sophisticated-method-selection"])

# Global service instance
sophisticated_service: SophisticatedMethodSelectionService = None


async def get_sophisticated_service() -> SophisticatedMethodSelectionService:
    """Dependency to get sophisticated method selection service instance."""
    global sophisticated_service
    if sophisticated_service is None:
        sophisticated_service = SophisticatedMethodSelectionService()
    return sophisticated_service


class SophisticatedSelectionRequest(BaseModel):
    """Request model for sophisticated method selection."""
    application_request: ApplicationRequest = Field(..., description="Base application request")
    optimization_objective: str = Field(
        default="balanced_optimization", 
        description="Optimization objective (maximize_efficiency, minimize_cost, minimize_environmental_impact, maximize_yield_potential, balanced_optimization)"
    )
    uncertainty_level: str = Field(
        default="medium",
        description="Uncertainty level (low, medium, high, very_high)"
    )
    use_ml_algorithms: bool = Field(default=True, description="Use machine learning algorithms")
    use_optimization_algorithms: bool = Field(default=True, description="Use optimization algorithms")
    use_fuzzy_logic: bool = Field(default=True, description="Use fuzzy logic for uncertainty handling")
    max_cost_per_acre: Optional[float] = Field(None, description="Maximum cost per acre constraint")
    min_efficiency_score: Optional[float] = Field(None, description="Minimum efficiency score constraint")
    max_environmental_impact: Optional[str] = Field(None, description="Maximum environmental impact constraint")


class SophisticatedSelectionResponse(BaseModel):
    """Response model for sophisticated method selection."""
    request_id: str = Field(..., description="Unique request identifier")
    optimal_method: str = Field(..., description="Optimal method selected")
    confidence_score: float = Field(..., description="Confidence in selection (0-1)")
    objective_value: float = Field(..., description="Objective function value")
    alternative_solutions: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative solutions")
    algorithm_used: str = Field(..., description="Algorithm used for selection")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    convergence_info: Dict[str, Any] = Field(default_factory=dict, description="Convergence information")
    method_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed method information")


class AlgorithmComparisonRequest(BaseModel):
    """Request model for algorithm comparison."""
    application_request: ApplicationRequest = Field(..., description="Base application request")
    algorithms_to_compare: List[str] = Field(
        default=["ml", "optimization", "constraint_satisfaction", "fuzzy_logic"],
        description="Algorithms to compare"
    )


class AlgorithmComparisonResponse(BaseModel):
    """Response model for algorithm comparison."""
    request_id: str = Field(..., description="Unique request identifier")
    algorithm_results: Dict[str, Dict[str, Any]] = Field(..., description="Results for each algorithm")
    comparison_summary: Dict[str, Any] = Field(..., description="Comparison summary")
    best_algorithm: str = Field(..., description="Best performing algorithm")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")


@router.post("/select-method", response_model=SophisticatedSelectionResponse)
async def select_sophisticated_method(
    request: SophisticatedSelectionRequest,
    service: SophisticatedMethodSelectionService = Depends(get_sophisticated_service)
):
    """
    Select optimal fertilizer application method using sophisticated algorithms.
    
    This endpoint combines multiple advanced algorithms including:
    - Machine learning models (Random Forest, Neural Networks)
    - Multi-criteria optimization (Scipy SLSQP)
    - Constraint satisfaction algorithms
    - Fuzzy logic for uncertainty handling
    - Ensemble decision making
    
    **Advanced Features:**
    - Multi-algorithm ensemble approach
    - Uncertainty handling with fuzzy logic
    - Constraint satisfaction with penalty methods
    - Historical data integration for continuous learning
    - Real-time performance optimization
    
    **Optimization Objectives:**
    - Maximize efficiency
    - Minimize cost
    - Minimize environmental impact
    - Maximize yield potential
    - Balanced optimization (default)
    
    **Uncertainty Levels:**
    - Low: High confidence in data and conditions
    - Medium: Normal uncertainty (default)
    - High: Significant uncertainty in conditions
    - Very High: Extreme uncertainty in data
    
    **Agricultural Context:**
    - Field conditions analysis
    - Crop growth stage considerations
    - Equipment compatibility
    - Environmental constraints
    - Economic constraints
    """
    try:
        start_time = time.time()
        request_id = str(uuid4())
        
        logger.info(f"Processing sophisticated method selection request {request_id}")
        
        # Parse optimization objective
        try:
            objective = OptimizationObjective(request.optimization_objective)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid optimization objective: {request.optimization_objective}"
            )
        
        # Parse uncertainty level
        try:
            uncertainty_level = UncertaintyLevel(request.uncertainty_level)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid uncertainty level: {request.uncertainty_level}"
            )
        
        # Create constraints
        constraints = OptimizationConstraints(
            max_cost_per_acre=request.max_cost_per_acre,
            min_efficiency_score=request.min_efficiency_score,
            max_environmental_impact=request.max_environmental_impact
        )
        
        # Perform sophisticated method selection
        result = await service.select_optimal_method_sophisticated(
            request.application_request,
            objective=objective,
            constraints=constraints,
            uncertainty_level=uncertainty_level,
            use_ml=request.use_ml_algorithms,
            use_optimization=request.use_optimization_algorithms,
            use_fuzzy_logic=request.use_fuzzy_logic
        )
        
        # Convert result to response format
        alternative_solutions = [
            {
                "method": str(method),
                "score": score,
                "confidence": 0.8  # Placeholder confidence
            }
            for method, score in result.alternative_solutions
        ]
        
        response = SophisticatedSelectionResponse(
            request_id=request_id,
            optimal_method=str(result.optimal_method),
            confidence_score=result.confidence_score,
            objective_value=result.objective_value,
            alternative_solutions=alternative_solutions,
            algorithm_used=result.algorithm_used,
            processing_time_ms=(time.time() - start_time) * 1000,
            convergence_info=result.convergence_info,
            method_details={
                "efficiency_score": 0.85,  # Placeholder
                "cost_per_acre": 25.0,      # Placeholder
                "environmental_impact": "low"  # Placeholder
            }
        )
        
        logger.info(f"Sophisticated method selection completed in {response.processing_time_ms:.2f}ms")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in sophisticated method selection: {e}")
        raise HTTPException(status_code=500, detail=f"Sophisticated method selection failed: {str(e)}")


@router.post("/compare-algorithms", response_model=AlgorithmComparisonResponse)
async def compare_sophisticated_algorithms(
    request: AlgorithmComparisonRequest,
    service: SophisticatedMethodSelectionService = Depends(get_sophisticated_service)
):
    """
    Compare different sophisticated algorithms for method selection.
    
    This endpoint runs the same selection problem using different algorithms
    and compares their performance, results, and recommendations.
    
    **Comparison Algorithms:**
    - Machine Learning (Random Forest + Neural Networks)
    - Multi-criteria Optimization (Scipy SLSQP)
    - Constraint Satisfaction
    - Fuzzy Logic
    
    **Performance Metrics:**
    - Processing time
    - Solution quality
    - Confidence scores
    - Convergence characteristics
    
    **Agricultural Insights:**
    - Algorithm suitability for different conditions
    - Performance trade-offs
    - Recommendation consistency
    - Uncertainty handling effectiveness
    """
    try:
        start_time = time.time()
        request_id = str(uuid4())
        
        logger.info(f"Comparing sophisticated algorithms for request {request_id}")
        
        # Initialize results dictionary
        algorithm_results = {}
        
        # Compare different algorithm combinations
        algorithm_configs = {
            "ml_only": {"use_ml": True, "use_optimization": False, "use_fuzzy_logic": False},
            "optimization_only": {"use_ml": False, "use_optimization": True, "use_fuzzy_logic": False},
            "constraint_satisfaction": {"use_ml": False, "use_optimization": False, "use_fuzzy_logic": False},
            "fuzzy_logic": {"use_ml": False, "use_optimization": False, "use_fuzzy_logic": True},
            "full_ensemble": {"use_ml": True, "use_optimization": True, "use_fuzzy_logic": True}
        }
        
        # Run each algorithm configuration
        for config_name, config in algorithm_configs.items():
            try:
                result = await service.select_optimal_method_sophisticated(
                    request.application_request,
                    objective=OptimizationObjective.BALANCED_OPTIMIZATION,
                    use_ml=config["use_ml"],
                    use_optimization=config["use_optimization"],
                    use_fuzzy_logic=config["use_fuzzy_logic"]
                )
                
                algorithm_results[config_name] = {
                    "optimal_method": str(result.optimal_method),
                    "confidence_score": result.confidence_score,
                    "objective_value": result.objective_value,
                    "processing_time_ms": result.optimization_time_ms,
                    "algorithm_used": result.algorithm_used,
                    "alternative_solutions_count": len(result.alternative_solutions),
                    "status": "success"
                }
                
            except Exception as e:
                logger.warning(f"Algorithm {config_name} failed: {e}")
                algorithm_results[config_name] = {
                    "error": str(e),
                    "status": "failed"
                }
        
        # Determine best algorithm based on confidence and processing time
        successful_results = {
            name: result for name, result in algorithm_results.items() 
            if result["status"] == "success"
        }
        
        if successful_results:
            best_algorithm = max(
                successful_results.keys(),
                key=lambda k: successful_results[k]["confidence_score"] / (1 + successful_results[k]["processing_time_ms"] / 1000)
            )
        else:
            best_algorithm = "none_successful"
        
        # Create comparison summary
        comparison_summary = {
            "total_algorithms_tested": len(algorithm_configs),
            "successful_algorithms": len(successful_results),
            "failed_algorithms": len(algorithm_configs) - len(successful_results),
            "best_algorithm": best_algorithm,
            "average_processing_time_ms": sum(
                result["processing_time_ms"] for result in successful_results.values()
            ) / len(successful_results) if successful_results else 0,
            "confidence_range": {
                "min": min(result["confidence_score"] for result in successful_results.values()) if successful_results else 0,
                "max": max(result["confidence_score"] for result in successful_results.values()) if successful_results else 0,
                "average": sum(result["confidence_score"] for result in successful_results.values()) / len(successful_results) if successful_results else 0
            }
        }
        
        response = AlgorithmComparisonResponse(
            request_id=request_id,
            algorithm_results=algorithm_results,
            comparison_summary=comparison_summary,
            best_algorithm=best_algorithm,
            processing_time_ms=(time.time() - start_time) * 1000
        )
        
        logger.info(f"Algorithm comparison completed in {response.processing_time_ms:.2f}ms")
        return response
        
    except Exception as e:
        logger.error(f"Error in algorithm comparison: {e}")
        raise HTTPException(status_code=500, detail=f"Algorithm comparison failed: {str(e)}")


@router.post("/train-models")
async def train_sophisticated_models(
    training_data: List[Dict[str, Any]],
    service: SophisticatedMethodSelectionService = Depends(get_sophisticated_service)
):
    """
    Train machine learning models with historical data.
    
    This endpoint trains the internal machine learning models with
    provided historical data to improve future recommendations.
    
    **Training Data Format:**
    ```json
    [
      {
        "field_size_acres": 100.0,
        "soil_type_encoded": 1,
        "drainage_class_encoded": 1,
        "slope_percent": 2.0,
        "irrigation_available": 1,
        "crop_type_encoded": 1,
        "growth_stage_encoded": 1,
        "target_yield": 180.0,
        "fertilizer_type_encoded": 1,
        "fertilizer_form_encoded": 1,
        "equipment_count": 1,
        "equipment_types_encoded": 1,
        "weather_conditions_encoded": 0,
        "historical_success_rate": 0.8,
        "efficiency_score": 0.8,
        "cost_per_acre": 25.0,
        "method_type_encoded": 1
      }
    ]
    ```
    
    **Model Training Features:**
    - Cross-validation scores
    - Performance metrics
    - Model improvement tracking
    - Continuous learning integration
    """
    try:
        logger.info(f"Training sophisticated models with {len(training_data)} samples")
        
        # Train models
        training_results = await service.train_ml_models(training_data)
        
        response = {
            "status": "success",
            "training_results": training_results,
            "samples_processed": len(training_data),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Model training completed: {training_results}")
        return response
        
    except Exception as e:
        logger.error(f"Error in model training: {e}")
        raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")


@router.post("/update-historical-data")
async def update_historical_data(
    outcome_data: Dict[str, Any],
    service: SophisticatedMethodSelectionService = Depends(get_sophisticated_service)
):
    """
    Update historical data with new outcomes for continuous improvement.
    
    This endpoint adds new outcome data to the historical database
    to enable continuous learning and model improvement.
    
    **Outcome Data Format:**
    ```json
    {
      "application_id": "app_123",
      "method_used": "broadcast",
      "algorithm_used": "ml_algorithm",
      "predicted_efficiency": 0.8,
      "predicted_cost": 25.0,
      "actual_efficiency": 0.75,
      "actual_cost": 27.0,
      "farmer_satisfaction": 0.8
    }
    ```
    """
    try:
        logger.info("Updating historical data for continuous improvement")
        
        # Update historical data
        await service.update_historical_data(outcome_data)
        
        response = {
            "status": "success",
            "message": "Historical data updated successfully",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("Historical data update completed")
        return response
        
    except Exception as e:
        logger.error(f"Error updating historical data: {e}")
        raise HTTPException(status_code=500, detail=f"Historical data update failed: {str(e)}")


@router.get("/algorithms")
async def get_available_algorithms():
    """
    Get information about available sophisticated algorithms.
    
    Returns detailed information about all available algorithms
    including their characteristics, strengths, and use cases.
    """
    algorithms_info = {
        "machine_learning": {
            "name": "Machine Learning Algorithms",
            "description": "Random Forest and Neural Network models trained on historical data",
            "strengths": ["High accuracy with sufficient data", "Handles complex patterns", "Adapts to new data"],
            "weaknesses": ["Requires large training datasets", "Black box decisions", "Computational overhead"],
            "best_for": ["Data-rich environments", "Pattern recognition", "Predictive modeling"],
            "algorithms": ["Random Forest Regressor", "Neural Network Regressor", "Random Forest Classifier"]
        },
        "optimization": {
            "name": "Multi-criteria Optimization",
            "description": "Scipy SLSQP optimization for multi-objective problems",
            "strengths": ["Mathematically rigorous", "Handles constraints well", "Proven convergence"],
            "weaknesses": ["Requires good initial guess", "Can be computationally expensive", "Sensitive to constraints"],
            "best_for": ["Resource allocation", "Multi-objective problems", "Constraint-heavy scenarios"],
            "algorithms": ["Sequential Least Squares Programming (SLSQP)"]
        },
        "constraint_satisfaction": {
            "name": "Constraint Satisfaction",
            "description": "Rule-based constraint satisfaction for feasibility checking",
            "strengths": ["Fast execution", "Clear logic", "Easy to debug"],
            "weaknesses": ["Limited optimization capability", "Rigid rules", "No uncertainty handling"],
            "best_for": ["Initial screening", "Constraint validation", "Quick feasibility checks"],
            "algorithms": ["Rule-based constraint checking", "Heuristic satisfaction"]
        },
        "fuzzy_logic": {
            "name": "Fuzzy Logic",
            "description": "Uncertainty handling with fuzzy membership functions",
            "strengths": ["Handles uncertainty well", "Intuitive reasoning", "Flexible boundaries"],
            "weaknesses": ["Subjective membership functions", "Parameter tuning needed", "Limited learning"],
            "best_for": ["Uncertain conditions", "Expert knowledge integration", "Qualitative reasoning"],
            "algorithms": ["Fuzzy membership functions", "Defuzzification methods"]
        },
        "ensemble": {
            "name": "Ensemble Decision Making",
            "description": "Combines multiple algorithms for robust decisions",
            "strengths": ["Robust to algorithm failures", "Balanced performance", "Confidence aggregation"],
            "weaknesses": ["Complex implementation", "Computational overhead", "Harder to interpret"],
            "best_for": ["Critical decisions", "High-stakes scenarios", "When robustness is paramount"],
            "algorithms": ["Weighted voting", "Confidence-based selection", "Performance-based weighting"]
        }
    }
    
    return {
        "available_algorithms": algorithms_info,
        "total_algorithms": len(algorithms_info),
        "default_algorithm": "ensemble",
        "recommendation": "Use ensemble for most agricultural applications"
    }


@router.get("/optimization-objectives")
async def get_optimization_objectives():
    """
    Get available optimization objectives.
    
    Returns information about all available optimization objectives
    that can be used in sophisticated method selection.
    """
    objectives_info = {
        "maximize_efficiency": {
            "name": "Maximize Efficiency",
            "description": "Prioritize application efficiency and nutrient use effectiveness",
            "weight_distribution": {"efficiency": 1.0, "cost": 0.0, "environmental": 0.0},
            "best_for": ["High-value crops", "Limited fertilizer budgets", "Precision agriculture"]
        },
        "minimize_cost": {
            "name": "Minimize Cost",
            "description": "Prioritize cost minimization while maintaining acceptable performance",
            "weight_distribution": {"efficiency": 0.0, "cost": 1.0, "environmental": 0.0},
            "best_for": ["Budget-constrained operations", "Commodity crops", "Large-scale farming"]
        },
        "minimize_environmental_impact": {
            "name": "Minimize Environmental Impact",
            "description": "Prioritize environmental protection and sustainability",
            "weight_distribution": {"efficiency": 0.0, "cost": 0.0, "environmental": 1.0},
            "best_for": ["Organic farming", "Environmentally sensitive areas", "Regulated operations"]
        },
        "maximize_yield_potential": {
            "name": "Maximize Yield Potential",
            "description": "Prioritize maximum yield potential and crop performance",
            "weight_distribution": {"efficiency": 0.8, "cost": 0.2, "environmental": 0.0},
            "best_for": ["High-value specialty crops", "Premium markets", "Yield-focused operations"]
        },
        "balanced_optimization": {
            "name": "Balanced Optimization",
            "description": "Balance efficiency, cost, and environmental considerations",
            "weight_distribution": {"efficiency": 0.4, "cost": 0.3, "environmental": 0.3},
            "best_for": ["Most agricultural applications", "Sustainable farming", "General use"]
        }
    }
    
    return {
        "available_objectives": objectives_info,
        "default_objective": "balanced_optimization",
        "recommendation": "Use balanced optimization for most scenarios"
    }


@router.get("/uncertainty-levels")
async def get_uncertainty_levels():
    """
    Get available uncertainty levels.
    
    Returns information about different uncertainty levels and
    their impact on decision making.
    """
    uncertainty_info = {
        "low": {
            "name": "Low Uncertainty",
            "description": "High confidence in data and conditions",
            "factor": 1.0,
            "use_case": "Well-documented fields with stable conditions",
            "confidence_adjustment": 1.0,
            "recommendations": ["Use precise algorithms", "Minimize conservative adjustments"]
        },
        "medium": {
            "name": "Medium Uncertainty",
            "description": "Normal uncertainty in agricultural conditions",
            "factor": 0.8,
            "use_case": "Typical field conditions with some variability",
            "confidence_adjustment": 0.85,
            "recommendations": ["Apply standard safety margins", "Use ensemble methods"]
        },
        "high": {
            "name": "High Uncertainty",
            "description": "Significant uncertainty in conditions or data",
            "factor": 0.6,
            "use_case": "New fields, variable weather, uncertain data",
            "confidence_adjustment": 0.7,
            "recommendations": ["Increase safety margins", "Prioritize robust methods", "Consider alternatives"]
        },
        "very_high": {
            "name": "Very High Uncertainty",
            "description": "Extreme uncertainty in critical conditions",
            "factor": 0.4,
            "use_case": "Experimental fields, extreme weather, poor data quality",
            "confidence_adjustment": 0.5,
            "recommendations": ["Prioritize conservative approaches", "Multiple contingency plans", "Expert consultation"]
        }
    }
    
    return {
        "uncertainty_levels": uncertainty_info,
        "default_level": "medium",
        "recommendation": "Start with medium uncertainty for most agricultural scenarios"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for sophisticated method selection service."""
    return {
        "service": "sophisticated-method-selection",
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "machine_learning_algorithms",
            "multi_criteria_optimization",
            "constraint_satisfaction",
            "fuzzy_logic",
            "ensemble_decision_making",
            "historical_data_integration",
            "continuous_learning"
        ],
        "endpoints": [
            "POST /select-method",
            "POST /compare-algorithms",
            "POST /train-models",
            "POST /update-historical-data",
            "GET /algorithms",
            "GET /optimization-objectives",
            "GET /uncertainty-levels"
        ]
    }