"""
API Routes for fertilizer application method selection and analysis.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from pydantic import BaseModel, Field

from src.models.application_models import (
    ApplicationRequest, ApplicationResponse, ApplicationMethod,
    FieldConditions, CropRequirements, FertilizerSpecification,
    EquipmentSpecification
)
from src.services.application_method_service import ApplicationMethodService
from src.services.cost_analysis_service import CostAnalysisService
from src.services.goal_based_recommendation_engine import GoalBasedRecommendationEngine

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/application", tags=["application"])

# Global service instances
application_service: ApplicationMethodService = None
cost_service: CostAnalysisService = None
goal_based_engine: GoalBasedRecommendationEngine = None


async def get_application_service() -> ApplicationMethodService:
    """Dependency to get application method service instance."""
    global application_service
    if application_service is None:
        application_service = ApplicationMethodService()
    return application_service


async def get_cost_service() -> CostAnalysisService:
    """Dependency to get cost analysis service instance."""
    global cost_service
    if cost_service is None:
        cost_service = CostAnalysisService()
    return cost_service


async def get_goal_based_engine() -> GoalBasedRecommendationEngine:
    """Dependency to get goal-based recommendation engine instance."""
    global goal_based_engine
    if goal_based_engine is None:
        goal_based_engine = GoalBasedRecommendationEngine()
    return goal_based_engine


@router.post("/select-methods", response_model=ApplicationResponse)
async def select_application_methods(
    request: ApplicationRequest,
    service: ApplicationMethodService = Depends(get_application_service)
):
    """
    Select optimal fertilizer application methods based on field conditions,
    crop requirements, and available equipment.
    
    This endpoint analyzes various factors to recommend the most suitable
    application methods for fertilizer application, considering efficiency,
    cost, equipment compatibility, and environmental impact.
    
    **Agricultural Context:**
    - Considers field size, soil type, and drainage characteristics
    - Evaluates crop growth stage and nutrient requirements
    - Assesses equipment compatibility and capacity
    - Provides efficiency scores and cost estimates
    
    **Response includes:**
    - Primary recommendation with detailed analysis
    - Alternative methods for comparison
    - Cost comparison across methods
    - Equipment compatibility matrix
    - Efficiency analysis and optimization opportunities
    """
    try:
        logger.info(f"Processing application method selection request")
        
        response = await service.select_application_methods(request)
        
        logger.info(f"Application method selection completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error in application method selection: {e}")
        raise HTTPException(status_code=500, detail=f"Application method selection failed: {str(e)}")


@router.post("/analyze-costs")
async def analyze_application_costs(
    request: ApplicationRequest,
    cost_service: CostAnalysisService = Depends(get_cost_service)
):
    """
    Analyze costs for different fertilizer application methods.
    
    This endpoint provides comprehensive cost analysis including fertilizer,
    equipment, labor, fuel, and maintenance costs for different application
    methods, helping farmers make informed economic decisions.
    
    **Cost Analysis includes:**
    - Fertilizer costs with efficiency adjustments
    - Equipment costs (rental vs ownership)
    - Labor costs based on skill requirements
    - Fuel costs based on field conditions
    - Maintenance costs and equipment wear
    - Cost per acre and total field costs
    
    **Economic Analysis:**
    - Comparative cost analysis across methods
    - ROI analysis and payback periods
    - Cost optimization recommendations
    - Sensitivity analysis for cost factors
    """
    try:
        logger.info(f"Processing application cost analysis request")
        
        # First get application methods
        application_service = await get_application_service()
        method_response = await application_service.select_application_methods(request)
        
        # Then analyze costs
        cost_analysis = await cost_service.analyze_application_costs(
            method_response.recommended_methods,
            request.field_conditions,
            request.crop_requirements,
            request.fertilizer_specification,
            request.available_equipment
        )
        
        logger.info(f"Application cost analysis completed successfully")
        return cost_analysis
        
    except Exception as e:
        logger.error(f"Error in application cost analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Cost analysis failed: {str(e)}")


@router.get("/methods", response_model=List[Dict[str, Any]])
async def get_available_methods():
    """
    Get list of available fertilizer application methods.
    
    Returns comprehensive information about all supported application
    methods including their characteristics, suitability factors, and
    equipment requirements.
    
    **Method Information includes:**
    - Method type and description
    - Equipment requirements
    - Fertilizer form compatibility
    - Field size suitability
    - Efficiency ratings
    - Cost estimates
    - Environmental impact
    - Pros and cons
    """
    try:
        logger.info("Retrieving available application methods")
        
        # Get service instance
        service = await get_application_service()
        
        # Extract method information from service database
        methods = []
        for method_type, method_data in service.method_database.items():
            method_info = {
                "method_type": method_type,
                "name": method_data["name"],
                "description": method_data["description"],
                "equipment_types": method_data["equipment_types"],
                "fertilizer_forms": method_data["fertilizer_forms"],
                "field_size_range": method_data["field_size_range"],
                "efficiency_score": method_data["efficiency_score"],
                "cost_per_acre": method_data["cost_per_acre"],
                "labor_intensity": method_data["labor_intensity"],
                "environmental_impact": method_data["environmental_impact"],
                "pros": method_data["pros"],
                "cons": method_data["cons"]
            }
            methods.append(method_info)
        
        logger.info(f"Retrieved {len(methods)} application methods")
        return methods
        
    except Exception as e:
        logger.error(f"Error retrieving application methods: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve application methods: {str(e)}")


@router.post("/validate-request")
async def validate_application_request(request: ApplicationRequest):
    """
    Validate application request parameters and provide feedback.
    
    This endpoint validates the application request parameters and provides
    feedback on potential issues or improvements before processing the
    actual method selection.
    
    **Validation checks:**
    - Field conditions validity
    - Crop requirements completeness
    - Fertilizer specification accuracy
    - Equipment compatibility
    - Parameter ranges and constraints
    """
    try:
        logger.info("Validating application request")
        
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        # Validate field conditions
        if request.field_conditions.field_size_acres < 0.1:
            validation_results["errors"].append("Field size must be at least 0.1 acres")
            validation_results["valid"] = False
        
        if request.field_conditions.field_size_acres > 10000:
            validation_results["warnings"].append("Field size exceeds recommended maximum")
        
        # Validate crop requirements
        if not request.crop_requirements.crop_type:
            validation_results["errors"].append("Crop type is required")
            validation_results["valid"] = False
        
        if not request.crop_requirements.growth_stage:
            validation_results["errors"].append("Growth stage is required")
            validation_results["valid"] = False
        
        # Validate fertilizer specification
        if not request.fertilizer_specification.fertilizer_type:
            validation_results["errors"].append("Fertilizer type is required")
            validation_results["valid"] = False
        
        if not request.fertilizer_specification.npk_ratio:
            validation_results["errors"].append("NPK ratio is required")
            validation_results["valid"] = False
        
        # Validate equipment
        if not request.available_equipment:
            validation_results["warnings"].append("No equipment specified - will use rental costs")
        
        # Provide suggestions
        if request.field_conditions.slope_percent and request.field_conditions.slope_percent > 10:
            validation_results["suggestions"].append("High slope may limit some application methods")
        
        if request.field_conditions.soil_type.lower() == "clay":
            validation_results["suggestions"].append("Clay soils may require specialized equipment")
        
        logger.info(f"Request validation completed: {validation_results['valid']}")
        return validation_results
        
    except Exception as e:
        logger.error(f"Error validating application request: {e}")
        raise HTTPException(status_code=500, detail=f"Request validation failed: {str(e)}")


@router.get("/crops/supported")
async def get_supported_crops(
    service: ApplicationMethodService = Depends(get_application_service)
):
    """
    Get list of supported crop types with detailed information.
    
    Returns comprehensive crop database including:
    - Crop names and scientific names
    - Growth stages and timing windows
    - Nutrient requirements and sensitivities
    - Application method preferences
    """
    try:
        crop_integration_service = service.crop_integration_service
        supported_crops = crop_integration_service.get_supported_crops()
        
        crop_info = {}
        for crop_type in supported_crops:
            crop_data = crop_integration_service.get_crop_info(crop_type)
            preferences = crop_integration_service.get_application_preferences(crop_type)
            growth_stages = crop_integration_service.get_supported_growth_stages(crop_type)
            
            crop_info[crop_type.value] = {
                "name": crop_data.get("name", crop_type.value.title()),
                "scientific_name": crop_data.get("scientific_name", ""),
                "category": crop_data.get("category", ""),
                "family": crop_data.get("family", ""),
                "growing_season": crop_data.get("growing_season", ""),
                "root_system": crop_data.get("root_system", ""),
                "nutrient_requirements": crop_data.get("nutrient_requirements", {}),
                "application_sensitivity": crop_data.get("application_sensitivity", {}),
                "critical_application_windows": crop_data.get("critical_application_windows", {}),
                "preferred_methods": preferences.preferred_methods if preferences else [],
                "avoided_methods": preferences.avoided_methods if preferences else [],
                "supported_growth_stages": [stage.value for stage in growth_stages]
            }
        
        return {
            "supported_crops": crop_info,
            "total_crops": len(supported_crops),
            "categories": list(set(crop_data.get("category", "") for crop_data in crop_info.values()))
        }
        
    except Exception as e:
        logger.error(f"Error getting supported crops: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get supported crops: {str(e)}")


@router.get("/crops/{crop_type}/growth-stages")
async def get_crop_growth_stages(
    crop_type: str,
    service: ApplicationMethodService = Depends(get_application_service)
):
    """
    Get detailed growth stage information for a specific crop.
    
    Args:
        crop_type: Type of crop (e.g., 'corn', 'soybean', 'wheat')
    
    Returns:
        Detailed growth stage information including:
        - Stage names and codes
        - Timing windows
        - Nutrient demand levels
        - Recommended and avoided application methods
    """
    try:
        crop_integration_service = service.crop_integration_service
        parsed_crop_type = service._parse_crop_type(crop_type)
        growth_stages = crop_integration_service.get_supported_growth_stages(parsed_crop_type)
        
        stage_info = {}
        for stage in growth_stages:
            stage_data = crop_integration_service.get_growth_stage_info(parsed_crop_type, stage)
            if stage_data:
                stage_info[stage.value] = {
                    "stage_name": stage_data.stage_name,
                    "stage_code": stage_data.stage_code,
                    "description": stage_data.description,
                    "days_from_planting": {
                        "min": stage_data.days_from_planting[0],
                        "max": stage_data.days_from_planting[1]
                    },
                    "nutrient_demand_level": stage_data.nutrient_demand_level,
                    "application_sensitivity": stage_data.application_sensitivity,
                    "recommended_methods": stage_data.recommended_methods,
                    "avoided_methods": stage_data.avoided_methods,
                    "timing_preferences": stage_data.timing_preferences
                }
        
        return {
            "crop_type": crop_type,
            "growth_stages": stage_info,
            "total_stages": len(stage_info)
        }
        
    except Exception as e:
        logger.error(f"Error getting growth stages for {crop_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get growth stages: {str(e)}")


@router.get("/crops/{crop_type}/nutrient-uptake")
async def get_crop_nutrient_uptake(
    crop_type: str,
    nutrient: str = "nitrogen",
    service: ApplicationMethodService = Depends(get_application_service)
):
    """
    Get nutrient uptake curve for a specific crop and nutrient.
    
    Args:
        crop_type: Type of crop (e.g., 'corn', 'soybean')
        nutrient: Type of nutrient (e.g., 'nitrogen', 'phosphorus', 'potassium')
    
    Returns:
        Nutrient uptake curve showing uptake percentage over growth stages
    """
    try:
        crop_integration_service = service.crop_integration_service
        parsed_crop_type = service._parse_crop_type(crop_type)
        
        uptake_curve = crop_integration_service.get_nutrient_uptake_curve(parsed_crop_type, nutrient)
        
        return {
            "crop_type": crop_type,
            "nutrient": nutrient,
            "uptake_curve": uptake_curve,
            "growth_stages": [f"Stage_{i+1}" for i in range(len(uptake_curve))],
            "peak_uptake": max(uptake_curve),
            "peak_stage": uptake_curve.index(max(uptake_curve)) + 1
        }
        
    except Exception as e:
        logger.error(f"Error getting nutrient uptake for {crop_type}/{nutrient}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get nutrient uptake: {str(e)}")


@router.post("/crops/{crop_type}/method-compatibility")
async def assess_method_compatibility(
    crop_type: str,
    method_types: List[str],
    service: ApplicationMethodService = Depends(get_application_service)
):
    """
    Assess compatibility between crop type and application methods.
    
    Args:
        crop_type: Type of crop (e.g., 'corn', 'soybean')
        method_types: List of application method types to assess
    
    Returns:
        Compatibility assessment for each method including:
        - Compatibility scores
        - Compatibility factors
        - Recommendations
    """
    try:
        crop_integration_service = service.crop_integration_service
        parsed_crop_type = service._parse_crop_type(crop_type)
        
        compatibility_results = {}
        for method_type in method_types:
            compatibility = crop_integration_service.assess_crop_method_compatibility(
                parsed_crop_type, method_type
            )
            compatibility_results[method_type] = {
                "compatibility_score": compatibility["compatibility_score"],
                "compatibility_factors": compatibility["factors"],
                "recommendation": "Recommended" if compatibility["compatibility_score"] > 0.7 
                                else "Neutral" if compatibility["compatibility_score"] > 0.4 
                                else "Not Recommended"
            }
        
        return {
            "crop_type": crop_type,
            "method_compatibility": compatibility_results,
            "overall_assessment": {
                "best_method": max(compatibility_results.keys(), 
                                 key=lambda k: compatibility_results[k]["compatibility_score"]),
                "worst_method": min(compatibility_results.keys(), 
                                  key=lambda k: compatibility_results[k]["compatibility_score"])
            }
        }
        
    except Exception as e:
        logger.error(f"Error assessing method compatibility for {crop_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to assess compatibility: {str(e)}")


@router.post("/crops/{crop_type}/timing-analysis")
async def analyze_application_timing(
    crop_type: str,
    growth_stage: str,
    method_type: str,
    days_from_planting: int,
    service: ApplicationMethodService = Depends(get_application_service)
):
    """
    Analyze optimal application timing for specific crop, growth stage, and method.
    
    Args:
        crop_type: Type of crop (e.g., 'corn', 'soybean')
        growth_stage: Growth stage (e.g., 'v6', 'vt', 'r1')
        method_type: Application method type (e.g., 'sidedress', 'foliar')
        days_from_planting: Days since planting
    
    Returns:
        Timing analysis including:
        - Timing score
        - Optimal timing window
        - Recommendations
    """
    try:
        crop_integration_service = service.crop_integration_service
        parsed_crop_type = service._parse_crop_type(crop_type)
        parsed_growth_stage = service._parse_growth_stage(growth_stage)
        
        # Get timing score
        timing_score = crop_integration_service.calculate_application_timing_score(
            parsed_crop_type, parsed_growth_stage, method_type, days_from_planting
        )
        
        # Get growth stage info
        stage_info = crop_integration_service.get_growth_stage_info(parsed_crop_type, parsed_growth_stage)
        
        # Get critical application windows
        critical_windows = crop_integration_service.get_critical_application_windows(parsed_crop_type)
        
        return {
            "crop_type": crop_type,
            "growth_stage": growth_stage,
            "method_type": method_type,
            "days_from_planting": days_from_planting,
            "timing_score": timing_score,
            "timing_assessment": {
                "optimal": timing_score > 0.8,
                "good": 0.6 <= timing_score <= 0.8,
                "acceptable": 0.4 <= timing_score < 0.6,
                "poor": timing_score < 0.4
            },
            "growth_stage_info": {
                "stage_name": stage_info.stage_name if stage_info else "Unknown",
                "nutrient_demand": stage_info.nutrient_demand_level if stage_info else "Unknown",
                "optimal_window": {
                    "min_days": stage_info.days_from_planting[0] if stage_info else 0,
                    "max_days": stage_info.days_from_planting[1] if stage_info else 0
                }
            },
            "critical_windows": critical_windows,
            "recommendations": {
                "timing": "Apply now" if timing_score > 0.8 
                         else "Consider timing" if timing_score > 0.6
                         else "Delay application" if timing_score < 0.4
                         else "Proceed with caution",
                "method_suitability": "Highly suitable" if timing_score > 0.8
                                     else "Suitable" if timing_score > 0.6
                                     else "Marginally suitable" if timing_score > 0.4
                                     else "Not recommended"
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing timing for {crop_type}/{growth_stage}/{method_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze timing: {str(e)}")


@router.post("/optimize-goals")
async def optimize_with_goals(
    request: ApplicationRequest,
    yield_weight: float = Query(0.35, ge=0.0, le=1.0, description="Weight for yield maximization"),
    cost_weight: float = Query(0.25, ge=0.0, le=1.0, description="Weight for cost minimization"),
    environment_weight: float = Query(0.20, ge=0.0, le=1.0, description="Weight for environmental protection"),
    labor_weight: float = Query(0.15, ge=0.0, le=1.0, description="Weight for labor efficiency"),
    nutrient_weight: float = Query(0.05, ge=0.0, le=1.0, description="Weight for nutrient efficiency"),
    optimization_method: str = Query("pareto_optimization", description="Optimization algorithm"),
    engine: GoalBasedRecommendationEngine = Depends(get_goal_based_engine)
):
    """
    Optimize fertilizer application methods using goal-based multi-objective optimization.
    
    This endpoint integrates the goal-based recommendation engine with the existing
    application method service to provide optimized recommendations based on multiple
    farmer goals and constraints.
    
    Agricultural Use Cases:
    - Multi-objective fertilizer application planning
    - Equipment and resource optimization
    - Environmental compliance optimization
    - Labor and cost efficiency analysis
    """
    try:
        # Normalize weights
        total_weight = yield_weight + cost_weight + environment_weight + labor_weight + nutrient_weight
        if total_weight > 0:
            yield_weight /= total_weight
            cost_weight /= total_weight
            environment_weight /= total_weight
            labor_weight /= total_weight
            nutrient_weight /= total_weight
        
        # Set up farmer goals
        from src.services.goal_based_recommendation_engine import OptimizationGoal
        farmer_goals = {
            OptimizationGoal.YIELD_MAXIMIZATION: yield_weight,
            OptimizationGoal.COST_MINIMIZATION: cost_weight,
            OptimizationGoal.ENVIRONMENTAL_PROTECTION: environment_weight,
            OptimizationGoal.LABOR_EFFICIENCY: labor_weight,
            OptimizationGoal.NUTRIENT_EFFICIENCY: nutrient_weight
        }
        
        # Perform optimization
        result = await engine.optimize_application_methods(
            request,
            farmer_goals=farmer_goals,
            optimization_method=optimization_method
        )
        
        # Get base application response for comparison
        base_response = await get_application_service().select_application_methods(request)
        
        return {
            "request_id": str(uuid4()),
            "optimization_results": {
                "method_scores": result.method_scores,
                "goal_achievements": {goal.value: achievement for goal, achievement in result.goal_achievements.items()},
                "optimization_time_ms": result.optimization_time_ms,
                "convergence_info": result.convergence_info
            },
            "base_recommendations": {
                "primary_method": base_response.primary_recommendation.method_type if base_response.primary_recommendation else None,
                "alternative_methods": [method.method_type for method in base_response.alternative_methods],
                "cost_comparison": base_response.cost_comparison
            },
            "optimization_improvements": {
                "goal_weights": farmer_goals,
                "method": optimization_method,
                "solutions_found": len(result.method_scores)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in goal-based optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Goal-based optimization failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for application service."""
    return {
        "service": "fertilizer-application",
        "status": "healthy",
        "features": [
            "method_selection",
            "cost_analysis",
            "crop_integration",
            "equipment_compatibility",
            "environmental_assessment",
            "goal_based_optimization"
        ],
        "endpoints": [
            "select-methods",
            "analyze-costs",
            "optimize-goals",
            "methods",
            "validate-request",
            "crops/supported",
            "crops/{crop_type}/growth-stages",
            "crops/{crop_type}/nutrient-uptake",
            "crops/{crop_type}/method-compatibility",
            "crops/{crop_type}/timing-analysis"
        ]
    }
# Import decision support routes
from src.api.decision_support_routes import router as decision_support_router

# Include decision support routes
router.include_router(decision_support_router)


# Sophisticated Method Selection Endpoints
from src.services.sophisticated_method_selection_service import (
    SophisticatedMethodSelectionService,
    OptimizationObjective,
    OptimizationConstraints,
    UncertaintyLevel
)
from src.services.historical_data_service import (
    HistoricalDataService,
    OutcomeData,
    OutcomeType
)


async def get_sophisticated_service() -> SophisticatedMethodSelectionService:
    """Dependency to get sophisticated method selection service instance."""
    return SophisticatedMethodSelectionService()


async def get_historical_service() -> HistoricalDataService:
    """Dependency to get historical data service instance."""
    return HistoricalDataService()


class SophisticatedMethodRequest(BaseModel):
    """Request model for sophisticated method selection."""
    application_request: ApplicationRequest
    objective: OptimizationObjective = OptimizationObjective.BALANCED_OPTIMIZATION
    constraints: Optional[OptimizationConstraints] = None
    uncertainty_level: UncertaintyLevel = UncertaintyLevel.MEDIUM
    use_ml: bool = True
    use_optimization: bool = True
    use_fuzzy_logic: bool = True


class OutcomeTrackingRequest(BaseModel):
    """Request model for outcome tracking."""
    application_id: str
    method_used: str
    algorithm_used: str
    predicted_efficiency: float
    predicted_cost: float
    actual_efficiency: Optional[float] = None
    actual_cost: Optional[float] = None
    yield_impact: Optional[float] = None
    farmer_satisfaction: Optional[float] = None
    environmental_impact: Optional[str] = None
    outcome_type: OutcomeType = OutcomeType.UNKNOWN
    notes: Optional[str] = None


@router.post("/sophisticated-method-selection", response_model=Dict[str, Any])
async def sophisticated_method_selection(
    request: SophisticatedMethodRequest,
    service: SophisticatedMethodSelectionService = Depends(get_sophisticated_service)
):
    """
    Select optimal fertilizer application method using sophisticated algorithms.
    
    This endpoint provides advanced method selection using:
    - Machine learning algorithms (Random Forest, Neural Networks)
    - Multi-criteria optimization algorithms
    - Constraint satisfaction algorithms
    - Fuzzy logic for uncertainty handling
    - Ensemble decision making
    
    Features:
    - Multi-objective optimization (efficiency, cost, environmental impact)
    - Constraint handling (equipment, timing, cost limits)
    - Uncertainty quantification and fuzzy logic
    - Historical data integration for continuous improvement
    - Performance requirements (<2s response time)
    """
    try:
        logger.info(f"Processing sophisticated method selection request")
        
        result = await service.select_optimal_method_sophisticated(
            request.application_request,
            objective=request.objective,
            constraints=request.constraints,
            uncertainty_level=request.uncertainty_level,
            use_ml=request.use_ml,
            use_optimization=request.use_optimization,
            use_fuzzy_logic=request.use_fuzzy_logic
        )
        
        return {
            "optimal_method": result.optimal_method.value,
            "objective_value": result.objective_value,
            "confidence_score": result.confidence_score,
            "alternative_solutions": [
                {"method": method.value, "score": score} 
                for method, score in result.alternative_solutions
            ],
            "optimization_time_ms": result.optimization_time_ms,
            "algorithm_used": result.algorithm_used,
            "convergence_info": result.convergence_info,
            "performance_requirements_met": result.optimization_time_ms < 2000
        }
        
    except Exception as e:
        logger.error(f"Error in sophisticated method selection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record-outcome", response_model=Dict[str, Any])
async def record_application_outcome(
    request: OutcomeTrackingRequest,
    background_tasks: BackgroundTasks,
    historical_service: HistoricalDataService = Depends(get_historical_service)
):
    """
    Record the outcome of a fertilizer application for continuous learning.
    
    This endpoint tracks:
    - Predicted vs actual efficiency and cost
    - Yield impact and farmer satisfaction
    - Environmental impact assessment
    - Outcome classification (success, partial success, failure)
    
    The data is used for:
    - Algorithm performance analysis
    - Model retraining and improvement
    - Historical trend analysis
    - Performance benchmarking
    """
    try:
        logger.info(f"Recording outcome for application {request.application_id}")
        
        # Convert string method to enum
        method_enum = ApplicationMethodType(request.method_used)
        
        outcome_data = OutcomeData(
            application_id=request.application_id,
            method_used=method_enum,
            algorithm_used=request.algorithm_used,
            predicted_efficiency=request.predicted_efficiency,
            predicted_cost=request.predicted_cost,
            actual_efficiency=request.actual_efficiency,
            actual_cost=request.actual_cost,
            yield_impact=request.yield_impact,
            farmer_satisfaction=request.farmer_satisfaction,
            environmental_impact=request.environmental_impact,
            outcome_type=request.outcome_type,
            notes=request.notes,
            timestamp=datetime.utcnow()
        )
        
        # Record outcome in background
        background_tasks.add_task(
            historical_service.record_application_outcome,
            outcome_data
        )
        
        return {
            "status": "success",
            "message": "Outcome recorded successfully",
            "application_id": request.application_id,
            "outcome_type": request.outcome_type.value
        }
        
    except Exception as e:
        logger.error(f"Error recording application outcome: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/algorithm-performance/{algorithm_name}", response_model=Dict[str, Any])
async def get_algorithm_performance(
    algorithm_name: str,
    days_back: int = Query(90, ge=1, le=365, description="Number of days to look back"),
    historical_service: HistoricalDataService = Depends(get_historical_service)
):
    """
    Get performance analysis for a specific algorithm.
    
    Returns:
    - Success rate and performance metrics
    - Average efficiency, cost, and satisfaction scores
    - Performance trend analysis
    - Confidence score based on data volume
    - Recommendations for improvement
    """
    try:
        logger.info(f"Analyzing performance for algorithm: {algorithm_name}")
        
        analysis = await historical_service.analyze_algorithm_performance(
            algorithm_name, days_back
        )
        
        return {
            "algorithm_name": analysis.algorithm_name,
            "total_applications": analysis.total_applications,
            "success_rate": analysis.success_rate,
            "average_efficiency": analysis.average_efficiency,
            "average_cost": analysis.average_cost,
            "average_satisfaction": analysis.average_satisfaction,
            "performance_trend": analysis.performance_trend,
            "confidence_score": analysis.confidence_score,
            "recommendations": analysis.recommendations,
            "analysis_period_days": days_back
        }
        
    except Exception as e:
        logger.error(f"Error analyzing algorithm performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/method-comparison", response_model=Dict[str, Any])
async def compare_methods(
    methods: List[str] = Query(..., description="List of methods to compare"),
    days_back: int = Query(90, ge=1, le=365, description="Number of days to look back"),
    historical_service: HistoricalDataService = Depends(get_historical_service)
):
    """
    Compare performance of multiple application methods.
    
    Returns comparison data including:
    - Total applications and success rates
    - Average efficiency, cost, and satisfaction
    - Algorithms used for each method
    - Performance rankings
    """
    try:
        logger.info(f"Comparing methods: {methods}")
        
        # Convert string methods to enums
        method_enums = [ApplicationMethodType(method) for method in methods]
        
        comparison_data = await historical_service.get_method_comparison_data(
            method_enums, days_back
        )
        
        return {
            "comparison_data": comparison_data,
            "comparison_period_days": days_back,
            "methods_compared": methods
        }
        
    except Exception as e:
        logger.error(f"Error comparing methods: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train-models", response_model=Dict[str, Any])
async def train_ml_models(
    background_tasks: BackgroundTasks,
    service: SophisticatedMethodSelectionService = Depends(get_sophisticated_service),
    historical_service: HistoricalDataService = Depends(get_historical_service)
):
    """
    Train machine learning models with historical data.
    
    This endpoint:
    - Retrieves historical training data
    - Trains ML models (Random Forest, Neural Networks)
    - Records training metrics and performance
    - Updates model performance tracking
    
    Training is performed in the background to avoid blocking the API.
    """
    try:
        logger.info("Starting ML model training")
        
        # Get historical data for training
        training_data = await historical_service.get_historical_data_for_training()
        
        if not training_data:
            return {
                "status": "no_data",
                "message": "No historical data available for training",
                "training_samples": 0
            }
        
        # Train models in background
        background_tasks.add_task(
            _train_models_background,
            service,
            historical_service,
            training_data
        )
        
        return {
            "status": "training_started",
            "message": "Model training started in background",
            "training_samples": len(training_data)
        }
        
    except Exception as e:
        logger.error(f"Error starting model training: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _train_models_background(
    service: SophisticatedMethodSelectionService,
    historical_service: HistoricalDataService,
    training_data: List[Dict[str, Any]]
):
    """Background task for training ML models."""
    try:
        start_time = time.time()
        
        # Train models
        training_result = await service.train_ml_models(training_data)
        
        training_time_ms = (time.time() - start_time) * 1000
        
        # Record training session
        await historical_service.record_algorithm_training(
            algorithm_name="sophisticated_method_selection",
            training_data_size=len(training_data),
            model_metrics=training_result,
            training_time_ms=training_time_ms
        )
        
        logger.info(f"ML model training completed in {training_time_ms:.2f}ms")
        
    except Exception as e:
        logger.error(f"Error in background model training: {e}")


@router.get("/training-history", response_model=Dict[str, Any])
async def get_training_history(
    algorithm_name: Optional[str] = Query(None, description="Filter by algorithm name"),
    days_back: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    historical_service: HistoricalDataService = Depends(get_historical_service)
):
    """
    Get training history for ML models.
    
    Returns:
    - Training sessions and timestamps
    - Model metrics and performance scores
    - Training data sizes and durations
    - Training trends and improvements
    """
    try:
        logger.info(f"Retrieving training history for {algorithm_name or 'all algorithms'}")
        
        training_history = await historical_service.get_training_history(
            algorithm_name, days_back
        )
        
        return {
            "training_history": training_history,
            "algorithm_filter": algorithm_name,
            "period_days": days_back,
            "total_sessions": len(training_history)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving training history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cleanup-old-data", response_model=Dict[str, Any])
async def cleanup_old_data(
    days_to_keep: int = Query(365, ge=30, le=1095, description="Days of data to keep"),
    historical_service: HistoricalDataService = Depends(get_historical_service)
):
    """
    Clean up old historical data to manage storage.
    
    Removes data older than specified days while preserving:
    - Recent performance metrics
    - Training history
    - Critical outcome records
    """
    try:
        logger.info(f"Cleaning up data older than {days_to_keep} days")
        
        deleted_count = await historical_service.cleanup_old_data(days_to_keep)
        
        return {
            "status": "success",
            "message": f"Cleaned up {deleted_count} old records",
            "days_kept": days_to_keep,
            "records_deleted": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
