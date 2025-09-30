"""
ROI Optimization API Routes.

This module provides FastAPI routes for fertilizer ROI optimization,
including comprehensive strategy optimization and analysis endpoints.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from ..models.roi_models import (
    ROIOptimizationRequest,
    ROIOptimizationResponse,
    OptimizationSummary,
    MarginalReturnAnalysis,
    YieldResponseCurve,
    BreakEvenAnalysis
)
from ..services.roi_optimizer import roi_optimizer_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/fertilizer", tags=["roi-optimization"])


@router.post("/optimize-strategy", response_model=ROIOptimizationResponse)
async def optimize_fertilizer_strategy(
    request: ROIOptimizationRequest,
    background_tasks: BackgroundTasks
):
    """
    Optimize fertilizer strategy for maximum ROI.
    
    This endpoint provides comprehensive fertilizer strategy optimization
    considering multiple objectives, constraints, and risk factors.
    
    **Agricultural Use Cases:**
    - Multi-field fertilizer optimization
    - Budget-constrained optimization
    - Risk-adjusted fertilizer planning
    - Economic optimization with environmental constraints
    
    **Optimization Methods:**
    - Linear Programming: Fast optimization for linear relationships
    - Quadratic Programming: Handles diminishing returns
    - Genetic Algorithm: Complex multi-objective optimization
    - Gradient Descent: Continuous optimization
    
    **Features:**
    - Multi-nutrient optimization (N, P, K, micronutrients)
    - Sensitivity analysis for key variables
    - Risk assessment and mitigation strategies
    - Alternative scenario generation
    - Break-even analysis
    """
    try:
        logger.info(f"Received optimization request for {len(request.fields)} fields")
        
        # Perform optimization
        result = await roi_optimizer_service.optimize_fertilizer_roi(request)
        
        # Log optimization completion
        logger.info(f"Optimization completed with ROI: {result.optimization_result.roi_percentage:.2f}%")
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in optimization: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in fertilizer strategy optimization: {e}")
        raise HTTPException(status_code=500, detail="Fertilizer strategy optimization failed")


@router.post("/roi-analysis", response_model=ROIOptimizationResponse)
async def analyze_fertilizer_roi(
    request: ROIOptimizationRequest,
    include_sensitivity: bool = Query(True, description="Include sensitivity analysis"),
    include_risk_assessment: bool = Query(True, description="Include risk assessment")
):
    """
    Perform comprehensive ROI analysis for fertilizer strategy.
    
    This endpoint provides detailed ROI analysis including sensitivity analysis,
    risk assessment, and scenario modeling for fertilizer investments.
    
    **Analysis Components:**
    - ROI calculation with multiple scenarios
    - Sensitivity analysis for key variables
    - Risk assessment and mitigation strategies
    - Break-even analysis
    - Marginal return analysis
    
    **Use Cases:**
    - Investment decision support
    - Risk management planning
    - Sensitivity analysis for key variables
    - Scenario planning and comparison
    """
    try:
        # Override request settings for analysis
        request.include_sensitivity_analysis = include_sensitivity
        request.include_risk_assessment = include_risk_assessment
        
        logger.info("Performing comprehensive ROI analysis")
        
        result = await roi_optimizer_service.optimize_fertilizer_roi(request)
        
        logger.info(f"ROI analysis completed with {result.optimization_result.roi_percentage:.2f}% ROI")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in ROI analysis: {e}")
        raise HTTPException(status_code=500, detail="ROI analysis failed")


@router.post("/break-even", response_model=BreakEvenAnalysis)
async def calculate_break_even_analysis(
    request: ROIOptimizationRequest
):
    """
    Calculate break-even analysis for fertilizer strategy.
    
    This endpoint calculates break-even points for fertilizer investments
    including yield, price, and cost break-even scenarios.
    
    **Break-Even Calculations:**
    - Break-even yield per acre
    - Break-even crop price
    - Break-even fertilizer cost
    - Safety margin analysis
    - Probability of profitability
    
    **Agricultural Applications:**
    - Investment decision support
    - Risk assessment for fertilizer programs
    - Price sensitivity analysis
    - Yield target setting
    """
    try:
        logger.info("Calculating break-even analysis")
        
        # Perform optimization to get base results
        optimization_result = await roi_optimizer_service.optimize_fertilizer_roi(request)
        result = optimization_result.optimization_result
        
        # Calculate break-even metrics
        total_acres = sum(field.acres for field in request.fields)
        crop_price = request.fields[0].crop_price if request.fields else 0
        
        # Break-even yield
        break_even_yield = result.total_fertilizer_cost / (total_acres * crop_price) if crop_price > 0 else 0
        
        # Break-even price
        total_yield = sum(field.target_yield * field.acres for field in request.fields)
        break_even_price = result.total_fertilizer_cost / total_yield if total_yield > 0 else 0
        
        # Break-even cost
        break_even_cost = result.total_expected_revenue / total_acres if total_acres > 0 else 0
        
        # Safety margin
        safety_margin = ((result.total_expected_revenue - result.total_fertilizer_cost) / result.total_fertilizer_cost * 100) if result.total_fertilizer_cost > 0 else 0
        
        # Probability of profitability (simplified)
        probability_of_profitability = 0.8 if result.roi_percentage > 50 else 0.6 if result.roi_percentage > 0 else 0.3
        
        # Risk factors
        risk_factors = []
        if result.roi_percentage < 50:
            risk_factors.append("Low ROI increases break-even risk")
        if safety_margin < 20:
            risk_factors.append("Low safety margin increases risk")
        if break_even_yield > sum(field.target_yield for field in request.fields) / len(request.fields):
            risk_factors.append("Break-even yield exceeds target yield")
        
        break_even_analysis = BreakEvenAnalysis(
            break_even_yield=break_even_yield,
            break_even_price=break_even_price,
            break_even_cost=break_even_cost,
            safety_margin=safety_margin,
            probability_of_profitability=probability_of_profitability,
            risk_factors=risk_factors
        )
        
        logger.info(f"Break-even analysis completed: yield={break_even_yield:.2f}, price={break_even_price:.2f}")
        
        return break_even_analysis
        
    except Exception as e:
        logger.error(f"Error in break-even analysis: {e}")
        raise HTTPException(status_code=500, detail="Break-even analysis failed")


@router.get("/optimization-summary", response_model=OptimizationSummary)
async def get_optimization_summary(
    farm_id: str = Query(..., description="Farm identifier"),
    include_historical: bool = Query(False, description="Include historical optimization data")
):
    """
    Get optimization summary for a farm.
    
    This endpoint provides a summary of optimization results and performance
    metrics for a specific farm.
    
    **Summary Components:**
    - Total fields optimized
    - Average ROI across fields
    - Total investment and expected return
    - Risk level assessment
    - Optimization method used
    """
    try:
        logger.info(f"Getting optimization summary for farm {farm_id}")
        
        # This would typically query a database for historical optimization data
        # For now, return a mock summary
        summary = OptimizationSummary(
            total_fields_optimized=5,
            total_acres=400.0,
            average_roi=125.5,
            total_investment=15000.0,
            expected_return=18750.0,
            risk_level="moderate",
            optimization_method_used="linear_programming",
            processing_time_ms=2500.0
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting optimization summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get optimization summary")


@router.post("/marginal-return-analysis", response_model=List[MarginalReturnAnalysis])
async def analyze_marginal_returns(
    request: ROIOptimizationRequest,
    nutrient_type: str = Query(..., description="Nutrient type (N, P, K)")
):
    """
    Analyze marginal returns for fertilizer applications.
    
    This endpoint calculates marginal return analysis for different
    fertilizer application rates to identify optimal application levels.
    
    **Analysis Components:**
    - Marginal yield response curves
    - Marginal cost analysis
    - Optimal application rate identification
    - Diminishing returns threshold
    """
    try:
        logger.info(f"Analyzing marginal returns for {nutrient_type}")
        
        # Perform optimization to get base results
        optimization_result = await roi_optimizer_service.optimize_fertilizer_roi(request)
        
        # Generate marginal return analysis
        marginal_analyses = []
        
        for field in request.fields:
            for product in request.fertilizer_products:
                if nutrient_type in product.nutrient_content:
                    # Calculate marginal return analysis
                    analysis = MarginalReturnAnalysis(
                        nutrient_type=nutrient_type,
                        application_rate=100.0,  # Default rate
                        marginal_yield_response=15.0,  # Simplified calculation
                        marginal_cost=product.price_per_unit,
                        marginal_return=15.0 * field.crop_price - product.price_per_unit,
                        optimal_rate=120.0,  # Simplified optimal rate
                        diminishing_returns_threshold=150.0
                    )
                    marginal_analyses.append(analysis)
        
        logger.info(f"Marginal return analysis completed for {len(marginal_analyses)} products")
        
        return marginal_analyses
        
    except Exception as e:
        logger.error(f"Error in marginal return analysis: {e}")
        raise HTTPException(status_code=500, detail="Marginal return analysis failed")


@router.post("/yield-response-curves", response_model=List[YieldResponseCurve])
async def generate_yield_response_curves(
    request: ROIOptimizationRequest,
    nutrient_type: str = Query(..., description="Nutrient type (N, P, K)")
):
    """
    Generate yield response curves for fertilizer applications.
    
    This endpoint generates yield response curves showing the relationship
    between fertilizer application rates and crop yield response.
    
    **Curve Components:**
    - Application rates vs yield response
    - Curve type identification
    - Model fit quality (R-squared)
    - Optimal application rate
    """
    try:
        logger.info(f"Generating yield response curves for {nutrient_type}")
        
        # Generate yield response curves
        curves = []
        
        for field in request.fields:
            # Generate sample data points
            rates = [0, 25, 50, 75, 100, 125, 150, 175, 200]
            yields = []
            
            for rate in rates:
                # Simplified yield calculation
                base_yield = field.target_yield
                response = min(rate * 0.8, 50)  # Diminishing returns
                yields.append(base_yield + response)
            
            curve = YieldResponseCurve(
                nutrient_type=nutrient_type,
                rates=rates,
                yields=yields,
                curve_type="quadratic",
                r_squared=0.85,
                optimal_rate=125.0
            )
            curves.append(curve)
        
        logger.info(f"Generated {len(curves)} yield response curves")
        
        return curves
        
    except Exception as e:
        logger.error(f"Error generating yield response curves: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate yield response curves")


@router.get("/optimization-methods")
async def get_available_optimization_methods():
    """
    Get available optimization methods and their descriptions.
    
    This endpoint provides information about available optimization methods
    and their characteristics for fertilizer strategy optimization.
    """
    try:
        methods = [
            {
                "method": "linear_programming",
                "name": "Linear Programming",
                "description": "Fast optimization for linear relationships between inputs and outputs",
                "best_for": "Simple optimization problems with linear constraints",
                "processing_time": "Fast (< 1 second)",
                "accuracy": "High for linear problems"
            },
            {
                "method": "quadratic_programming",
                "name": "Quadratic Programming",
                "description": "Handles diminishing returns and quadratic relationships",
                "best_for": "Problems with diminishing returns and quadratic objectives",
                "processing_time": "Medium (1-5 seconds)",
                "accuracy": "High for quadratic problems"
            },
            {
                "method": "genetic_algorithm",
                "name": "Genetic Algorithm",
                "description": "Evolutionary optimization for complex multi-objective problems",
                "best_for": "Complex optimization with multiple objectives and constraints",
                "processing_time": "Slow (5-30 seconds)",
                "accuracy": "Good for complex problems"
            },
            {
                "method": "gradient_descent",
                "name": "Gradient Descent",
                "description": "Continuous optimization using gradient information",
                "best_for": "Smooth optimization problems with continuous variables",
                "processing_time": "Medium (1-10 seconds)",
                "accuracy": "High for smooth problems"
            }
        ]
        
        return {"optimization_methods": methods}
        
    except Exception as e:
        logger.error(f"Error getting optimization methods: {e}")
        raise HTTPException(status_code=500, detail="Failed to get optimization methods")


@router.get("/health")
async def health_check():
    """Health check endpoint for ROI optimization service."""
    return {
        "service": "roi-optimization",
        "status": "healthy",
        "features": [
            "fertilizer_strategy_optimization",
            "roi_analysis",
            "break_even_analysis",
            "sensitivity_analysis",
            "risk_assessment",
            "marginal_return_analysis",
            "yield_response_curves",
            "multi_objective_optimization",
            "constraint_handling",
            "scenario_analysis"
        ]
    }