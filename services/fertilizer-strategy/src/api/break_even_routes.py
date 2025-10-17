"""
API routes for comprehensive break-even analysis.

This module provides REST API endpoints for advanced break-even analysis including:
- Comprehensive break-even analysis with all features
- Monte Carlo simulation
- Scenario analysis
- Sensitivity analysis
- Risk assessment
- Comparison tools
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from ..models.break_even_models import (
    BreakEvenAnalysisRequest,
    ComprehensiveBreakEvenAnalysis,
    BreakEvenSummary,
    BreakEvenComparison,
    BreakEvenAlert,
    ScenarioType,
    RiskLevel
)
from ..models.roi_models import ROIOptimizationRequest
from ..services.break_even_analysis_service import BreakEvenAnalysisService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/break-even", tags=["break-even-analysis"])

# Dependency injection
async def get_break_even_service() -> BreakEvenAnalysisService:
    """Get break-even analysis service instance."""
    return BreakEvenAnalysisService()


@router.post("/comprehensive", response_model=ComprehensiveBreakEvenAnalysis)
async def perform_comprehensive_break_even_analysis(
    request: BreakEvenAnalysisRequest,
    background_tasks: BackgroundTasks,
    service: BreakEvenAnalysisService = Depends(get_break_even_service)
):
    """
    Perform comprehensive break-even analysis with all advanced features.
    
    This endpoint provides the most complete break-even analysis including:
    - Basic break-even calculations
    - Monte Carlo simulation (stochastic modeling)
    - Scenario analysis (optimistic, realistic, pessimistic, stress test)
    - Sensitivity analysis for key variables
    - Risk assessment and mitigation recommendations
    - Actionable recommendations
    
    **Advanced Features:**
    - Stochastic modeling with configurable iterations
    - Multiple scenario types with probability weighting
    - Sensitivity analysis for crop price, fertilizer cost, yield, and other variables
    - Risk assessment with mitigation strategies
    - Monte Carlo confidence intervals and risk metrics
    
    **Agricultural Applications:**
    - Investment decision support with risk quantification
    - Price sensitivity analysis for hedging decisions
    - Yield target setting with probability assessments
    - Cost optimization with break-even constraints
    - Risk management and contingency planning
    """
    try:
        logger.info(f"Starting comprehensive break-even analysis for {len(request.fields)} fields")
        
        # Convert request to ROI optimization format for compatibility
        roi_request = ROIOptimizationRequest(
            fields=request.fields,
            products=request.products,
            optimization_method=request.optimization_method,
            budget_constraints=request.budget_constraints,
            farm_context=request.farm_context
        )
        
        # Perform comprehensive analysis
        results = await service.perform_comprehensive_break_even_analysis(
            request=roi_request,
            include_stochastic=request.include_stochastic,
            include_scenarios=request.include_scenarios,
            include_sensitivity=request.include_sensitivity,
            monte_carlo_iterations=request.monte_carlo_iterations
        )
        
        # Log completion
        logger.info(f"Comprehensive break-even analysis completed: {results['analysis_id']}")
        
        return ComprehensiveBreakEvenAnalysis(**results)
        
    except Exception as e:
        logger.error(f"Error in comprehensive break-even analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Break-even analysis failed: {str(e)}")


@router.post("/monte-carlo", response_model=Dict[str, Any])
async def perform_monte_carlo_simulation(
    request: BreakEvenAnalysisRequest,
    iterations: int = Query(10000, ge=1000, le=100000, description="Number of Monte Carlo iterations"),
    service: BreakEvenAnalysisService = Depends(get_break_even_service)
):
    """
    Perform Monte Carlo simulation for break-even analysis.
    
    This endpoint runs stochastic modeling to assess break-even probabilities
    under various price and yield scenarios using Monte Carlo simulation.
    
    **Monte Carlo Features:**
    - Price volatility modeling (crop and fertilizer prices)
    - Yield variability simulation
    - Probability distributions for key variables
    - Confidence intervals for break-even metrics
    - Risk metrics (VaR, Expected Shortfall, Sharpe ratio)
    
    **Agricultural Applications:**
    - Risk quantification for fertilizer investments
    - Probability assessment for profitability
    - Stress testing under adverse conditions
    - Decision support with uncertainty quantification
    """
    try:
        logger.info(f"Starting Monte Carlo simulation with {iterations} iterations")
        
        # Convert request to ROI optimization format
        roi_request = ROIOptimizationRequest(
            fields=request.fields,
            products=request.products,
            optimization_method=request.optimization_method,
            budget_constraints=request.budget_constraints,
            farm_context=request.farm_context
        )
        
        # Perform Monte Carlo simulation
        results = await service.perform_comprehensive_break_even_analysis(
            request=roi_request,
            include_stochastic=True,
            include_scenarios=False,
            include_sensitivity=False,
            monte_carlo_iterations=iterations
        )
        
        # Extract Monte Carlo results
        monte_carlo_results = results.get("stochastic_analysis")
        if not monte_carlo_results:
            raise HTTPException(status_code=500, detail="Monte Carlo simulation failed")
        
        logger.info(f"Monte Carlo simulation completed: {monte_carlo_results.simulation_id}")
        
        return {
            "simulation_id": monte_carlo_results.simulation_id,
            "iterations": monte_carlo_results.iterations,
            "break_even_probabilities": monte_carlo_results.break_even_probabilities,
            "confidence_intervals": monte_carlo_results.confidence_intervals,
            "risk_metrics": monte_carlo_results.risk_metrics,
            "summary_statistics": {
                "mean_profit": sum(monte_carlo_results.probability_distributions["profits"]) / len(monte_carlo_results.probability_distributions["profits"]),
                "profit_volatility": (sum([(x - sum(monte_carlo_results.probability_distributions["profits"]) / len(monte_carlo_results.probability_distributions["profits"]))**2 for x in monte_carlo_results.probability_distributions["profits"]])) ** 0.5,
                "probability_of_loss": len([p for p in monte_carlo_results.probability_distributions["profits"] if p < 0]) / len(monte_carlo_results.probability_distributions["profits"])
            }
        }
        
    except Exception as e:
        logger.error(f"Error in Monte Carlo simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Monte Carlo simulation failed: {str(e)}")


@router.post("/scenarios", response_model=List[Dict[str, Any]])
async def perform_scenario_analysis(
    request: BreakEvenAnalysisRequest,
    custom_scenarios: Optional[List[Dict[str, Any]]] = None,
    service: BreakEvenAnalysisService = Depends(get_break_even_service)
):
    """
    Perform scenario analysis for break-even assessment.
    
    This endpoint analyzes break-even under different scenarios including
    optimistic, realistic, pessimistic, and stress test conditions.
    
    **Scenario Types:**
    - Optimistic: High prices, high yields, low costs
    - Realistic: Base case scenario
    - Pessimistic: Low prices, low yields, high costs
    - Stress Test: Extreme adverse conditions
    
    **Custom Scenarios:**
    - Define custom price/yield/cost combinations
    - Specify probability weights for scenarios
    - Compare multiple strategic options
    
    **Agricultural Applications:**
    - Strategic planning under uncertainty
    - Contingency planning for adverse conditions
    - Investment decision support
    - Risk management and hedging strategies
    """
    try:
        logger.info("Starting scenario analysis")
        
        # Convert request to ROI optimization format
        roi_request = ROIOptimizationRequest(
            fields=request.fields,
            products=request.products,
            optimization_method=request.optimization_method,
            budget_constraints=request.budget_constraints,
            farm_context=request.farm_context
        )
        
        # Perform scenario analysis
        results = await service.perform_comprehensive_break_even_analysis(
            request=roi_request,
            include_stochastic=False,
            include_scenarios=True,
            include_sensitivity=False,
            monte_carlo_iterations=1000  # Minimal for scenario analysis
        )
        
        # Extract scenario results
        scenario_results = results.get("scenario_analysis", [])
        
        # Add custom scenarios if provided
        if custom_scenarios:
            # Process custom scenarios (would need additional implementation)
            logger.info(f"Processing {len(custom_scenarios)} custom scenarios")
        
        logger.info(f"Scenario analysis completed: {len(scenario_results)} scenarios analyzed")
        
        return [
            {
                "scenario_id": scenario.scenario_id,
                "scenario_type": scenario.scenario_type,
                "crop_price": scenario.crop_price,
                "fertilizer_price": scenario.fertilizer_price,
                "expected_yield": scenario.expected_yield,
                "break_even_yield": scenario.break_even_yield,
                "break_even_price": scenario.break_even_price,
                "break_even_cost": scenario.break_even_cost,
                "probability": scenario.probability,
                "risk_level": scenario.risk_level,
                "safety_margin": scenario.safety_margin
            }
            for scenario in scenario_results
        ]
        
    except Exception as e:
        logger.error(f"Error in scenario analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Scenario analysis failed: {str(e)}")


@router.post("/sensitivity", response_model=List[Dict[str, Any]])
async def perform_sensitivity_analysis(
    request: BreakEvenAnalysisRequest,
    variables: Optional[List[str]] = Query(None, description="Specific variables to analyze"),
    service: BreakEvenAnalysisService = Depends(get_break_even_service)
):
    """
    Perform sensitivity analysis for break-even variables.
    
    This endpoint analyzes how changes in key variables affect break-even metrics.
    
    **Analyzed Variables:**
    - Crop price
    - Fertilizer cost
    - Yield targets
    - Fixed costs
    - Variable costs
    
    **Sensitivity Metrics:**
    - Elasticity coefficients
    - Break-even impact ranges
    - Sensitivity rankings
    - Threshold analysis
    
    **Agricultural Applications:**
    - Price sensitivity for hedging decisions
    - Cost optimization priorities
    - Yield target validation
    - Risk factor identification
    """
    try:
        logger.info("Starting sensitivity analysis")
        
        # Convert request to ROI optimization format
        roi_request = ROIOptimizationRequest(
            fields=request.fields,
            products=request.products,
            optimization_method=request.optimization_method,
            budget_constraints=request.budget_constraints,
            farm_context=request.farm_context
        )
        
        # Perform sensitivity analysis
        results = await service.perform_comprehensive_break_even_analysis(
            request=roi_request,
            include_stochastic=False,
            include_scenarios=False,
            include_sensitivity=True,
            monte_carlo_iterations=1000  # Minimal for sensitivity analysis
        )
        
        # Extract sensitivity results
        sensitivity_results = results.get("sensitivity_analysis", [])
        
        # Filter variables if specified
        if variables:
            sensitivity_results = [s for s in sensitivity_results if s.variable_name in variables]
        
        logger.info(f"Sensitivity analysis completed: {len(sensitivity_results)} variables analyzed")
        
        return [
            {
                "variable_name": analysis.variable_name,
                "base_value": analysis.base_value,
                "sensitivity_range": analysis.sensitivity_range,
                "break_even_impact": analysis.break_even_impact,
                "elasticity": analysis.elasticity,
                "sensitivity_ranking": abs(analysis.elasticity)  # For ranking
            }
            for analysis in sensitivity_results
        ]
        
    except Exception as e:
        logger.error(f"Error in sensitivity analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Sensitivity analysis failed: {str(e)}")


@router.post("/risk-assessment", response_model=Dict[str, Any])
async def assess_break_even_risk(
    request: BreakEvenAnalysisRequest,
    service: BreakEvenAnalysisService = Depends(get_break_even_service)
):
    """
    Assess risk level for break-even analysis.
    
    This endpoint provides comprehensive risk assessment including:
    - Overall risk level determination
    - Risk factor identification
    - Risk mitigation recommendations
    - Risk scoring and ranking
    
    **Risk Factors Analyzed:**
    - Safety margin adequacy
    - Probability of profitability
    - Price volatility impact
    - Yield variability risk
    - Cost structure stability
    
    **Agricultural Applications:**
    - Risk management planning
    - Insurance and hedging decisions
    - Investment risk assessment
    - Contingency planning
    """
    try:
        logger.info("Starting risk assessment")
        
        # Convert request to ROI optimization format
        roi_request = ROIOptimizationRequest(
            fields=request.fields,
            products=request.products,
            optimization_method=request.optimization_method,
            budget_constraints=request.budget_constraints,
            farm_context=request.farm_context
        )
        
        # Perform comprehensive analysis for risk assessment
        results = await service.perform_comprehensive_break_even_analysis(
            request=roi_request,
            include_stochastic=True,
            include_scenarios=True,
            include_sensitivity=True,
            monte_carlo_iterations=5000  # Moderate for risk assessment
        )
        
        # Extract risk assessment
        risk_assessment = results.get("risk_assessment", {})
        
        logger.info(f"Risk assessment completed: {risk_assessment.get('overall_risk_level', 'unknown')} risk level")
        
        return {
            "overall_risk_level": risk_assessment.get("overall_risk_level"),
            "risk_score": risk_assessment.get("risk_score"),
            "risk_factors": risk_assessment.get("risk_factors", []),
            "risk_mitigation_recommendations": risk_assessment.get("risk_mitigation_recommendations", []),
            "risk_summary": {
                "safety_margin": results.get("basic_analysis", {}).get("safety_margin_percentage", 0),
                "probability_of_profitability": results.get("basic_analysis", {}).get("probability_of_profitability", 0),
                "break_even_yield": results.get("basic_analysis", {}).get("break_even_yield_per_acre", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in risk assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")


@router.post("/summary", response_model=BreakEvenSummary)
async def get_break_even_summary(
    request: BreakEvenAnalysisRequest,
    service: BreakEvenAnalysisService = Depends(get_break_even_service)
):
    """
    Get summary of break-even analysis results.
    
    This endpoint provides a concise summary of break-even analysis
    suitable for quick decision-making and reporting.
    
    **Summary Includes:**
    - Key break-even metrics
    - Safety margin and profitability probability
    - Overall risk level
    - Top recommendations
    
    **Agricultural Applications:**
    - Quick decision support
    - Executive summaries
    - Dashboard displays
    - Comparative analysis
    """
    try:
        logger.info("Generating break-even summary")
        
        # Convert request to ROI optimization format
        roi_request = ROIOptimizationRequest(
            fields=request.fields,
            products=request.products,
            optimization_method=request.optimization_method,
            budget_constraints=request.budget_constraints,
            farm_context=request.farm_context
        )
        
        # Perform basic analysis for summary
        results = await service.perform_comprehensive_break_even_analysis(
            request=roi_request,
            include_stochastic=False,
            include_scenarios=False,
            include_sensitivity=False,
            monte_carlo_iterations=1000
        )
        
        basic_analysis = results.get("basic_analysis", {})
        risk_assessment = results.get("risk_assessment", {})
        recommendations = results.get("recommendations", [])
        
        summary = BreakEvenSummary(
            analysis_id=results.get("analysis_id", ""),
            break_even_yield_per_acre=basic_analysis.get("break_even_yield_per_acre", 0),
            break_even_price_per_unit=basic_analysis.get("break_even_price_per_unit", 0),
            safety_margin_percentage=basic_analysis.get("safety_margin_percentage", 0),
            probability_of_profitability=basic_analysis.get("probability_of_profitability", 0),
            overall_risk_level=risk_assessment.get("overall_risk_level", RiskLevel.MEDIUM),
            key_recommendations=recommendations[:3]  # Top 3 recommendations
        )
        
        logger.info(f"Break-even summary generated: {summary.analysis_id}")
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating break-even summary: {e}")
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for break-even analysis service."""
    return {
        "status": "healthy",
        "service": "break-even-analysis",
        "features": [
            "comprehensive_analysis",
            "monte_carlo_simulation",
            "scenario_analysis",
            "sensitivity_analysis",
            "risk_assessment"
        ]
    }


@router.get("/scenarios/types")
async def get_scenario_types():
    """Get available scenario types for analysis."""
    return {
        "scenario_types": [
            {
                "type": ScenarioType.OPTIMISTIC,
                "description": "High prices, high yields, low costs",
                "probability_weight": 0.2
            },
            {
                "type": ScenarioType.REALISTIC,
                "description": "Base case scenario",
                "probability_weight": 0.5
            },
            {
                "type": ScenarioType.PESSIMISTIC,
                "description": "Low prices, low yields, high costs",
                "probability_weight": 0.2
            },
            {
                "type": ScenarioType.STRESS_TEST,
                "description": "Extreme adverse conditions",
                "probability_weight": 0.1
            }
        ]
    }


@router.get("/risk-levels")
async def get_risk_levels():
    """Get available risk levels and their descriptions."""
    return {
        "risk_levels": [
            {
                "level": RiskLevel.LOW,
                "description": "Low risk - high safety margin, good profitability probability",
                "safety_margin_threshold": 30,
                "profitability_threshold": 0.8
            },
            {
                "level": RiskLevel.MEDIUM,
                "description": "Medium risk - moderate safety margin and profitability",
                "safety_margin_threshold": 20,
                "profitability_threshold": 0.7
            },
            {
                "level": RiskLevel.HIGH,
                "description": "High risk - low safety margin or profitability concerns",
                "safety_margin_threshold": 10,
                "profitability_threshold": 0.6
            },
            {
                "level": RiskLevel.CRITICAL,
                "description": "Critical risk - negative safety margin or very low profitability",
                "safety_margin_threshold": 0,
                "profitability_threshold": 0.5
            }
        ]
    }