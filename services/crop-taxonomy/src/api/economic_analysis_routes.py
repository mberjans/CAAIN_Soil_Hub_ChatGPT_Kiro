"""
Economic Analysis API Routes

API endpoints for crop variety economic analysis including:
- Individual variety economic analysis
- Comparative economic analysis
- Economic scoring and ranking
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field
from datetime import datetime

try:
    from ..services.variety_economics import (
        VarietyEconomicAnalysisService,
        EconomicAnalysisResult,
        CostFactors,
        RevenueFactors,
        SophisticatedROIAnalysis,
        ScenarioAnalysis,
        MonteCarloResult,
        InvestmentRecommendation,
        ScenarioType,
        RiskLevel
    )
    from ..models.crop_variety_models import EnhancedCropVariety
    from ..models.service_models import ConfidenceLevel
except ImportError:
    from services.variety_economics import (
        VarietyEconomicAnalysisService,
        EconomicAnalysisResult,
        CostFactors,
        RevenueFactors,
        SophisticatedROIAnalysis,
        ScenarioAnalysis,
        MonteCarloResult,
        InvestmentRecommendation,
        ScenarioType,
        RiskLevel
    )
    from models.crop_variety_models import EnhancedCropVariety
    from models.service_models import ConfidenceLevel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/economic-analysis", tags=["economic-analysis"])


# Request/Response Models
class EconomicAnalysisRequest(BaseModel):
    """Request model for economic analysis."""
    
    variety_id: str = Field(..., description="ID of the variety to analyze")
    regional_context: Dict[str, Any] = Field(..., description="Regional growing conditions and market data")
    farmer_preferences: Optional[Dict[str, Any]] = Field(None, description="Optional farmer-specific preferences")
    analysis_parameters: Optional[Dict[str, Any]] = Field(None, description="Optional analysis parameters override")


class ComparativeAnalysisRequest(BaseModel):
    """Request model for comparative economic analysis."""
    
    variety_ids: List[str] = Field(..., description="List of variety IDs to compare")
    regional_context: Dict[str, Any] = Field(..., description="Regional growing conditions and market data")
    farmer_preferences: Optional[Dict[str, Any]] = Field(None, description="Optional farmer-specific preferences")
    analysis_parameters: Optional[Dict[str, Any]] = Field(None, description="Optional analysis parameters override")


class EconomicAnalysisResponse(BaseModel):
    """Response model for economic analysis."""
    
    variety_id: str
    variety_name: str
    
    # Financial Metrics
    net_present_value: float
    internal_rate_of_return: float
    payback_period_years: float
    break_even_yield: float
    break_even_price: float
    
    # Cost Analysis
    total_seed_cost_per_acre: float
    total_input_costs_per_acre: float
    total_operating_costs_per_acre: float
    
    # Revenue Analysis
    expected_revenue_per_acre: float
    expected_profit_per_acre: float
    profit_margin_percent: float
    
    # Risk Analysis
    risk_adjusted_return: float
    volatility_score: float
    downside_risk: float
    
    # Government Programs
    government_subsidies_per_acre: float
    insurance_coverage_percent: float
    
    # Overall Economic Score
    economic_viability_score: float
    confidence_level: str
    
    # Analysis Metadata
    analysis_date: datetime
    market_data_source: str
    assumptions_used: Dict[str, Any]


class ComparativeAnalysisResponse(BaseModel):
    """Response model for comparative economic analysis."""
    
    analysis_id: str
    analysis_date: datetime
    regional_context: Dict[str, Any]
    farmer_preferences: Optional[Dict[str, Any]]
    
    variety_analyses: List[EconomicAnalysisResponse]
    ranking_summary: Dict[str, Any]
    
    # Comparative metrics
    best_npv_variety: str
    best_irr_variety: str
    lowest_risk_variety: str
    most_profitable_variety: str


class EconomicScoringRequest(BaseModel):
    """Request model for economic scoring only."""
    
    variety_id: str = Field(..., description="ID of the variety to score")
    regional_context: Dict[str, Any] = Field(..., description="Regional growing conditions")
    farmer_preferences: Optional[Dict[str, Any]] = Field(None, description="Optional farmer preferences")


class EconomicScoringResponse(BaseModel):
    """Response model for economic scoring."""
    
    variety_id: str
    variety_name: str
    economic_viability_score: float
    confidence_level: str
    scoring_factors: Dict[str, float]
    analysis_date: datetime


class SophisticatedROIAnalysisRequest(BaseModel):
    """Request model for sophisticated ROI analysis."""
    
    variety_id: str = Field(..., description="ID of the variety to analyze")
    regional_context: Dict[str, Any] = Field(..., description="Regional growing conditions and market data")
    farmer_preferences: Optional[Dict[str, Any]] = Field(None, description="Optional farmer-specific preferences")
    analysis_horizon_years: int = Field(5, ge=1, le=10, description="Number of years for analysis (1-10)")
    monte_carlo_iterations: int = Field(10000, ge=1000, le=50000, description="Number of Monte Carlo iterations")


class ScenarioAnalysisResponse(BaseModel):
    """Response model for scenario analysis."""
    
    scenario_type: str
    net_present_value: float
    internal_rate_of_return: float
    payback_period_years: float
    expected_profit_per_acre: float
    probability_of_profit: float
    confidence_interval_95: List[float]


class MonteCarloAnalysisResponse(BaseModel):
    """Response model for Monte Carlo analysis."""
    
    mean_npv: float
    median_npv: float
    std_deviation_npv: float
    probability_of_positive_npv: float
    value_at_risk_95: float
    expected_shortfall: float
    simulation_iterations: int
    confidence_intervals: Dict[str, List[float]]


class InvestmentRecommendationResponse(BaseModel):
    """Response model for investment recommendation."""
    
    recommendation_type: str
    confidence_score: float
    risk_level: str
    expected_return_percent: float
    payback_period_years: float
    key_factors: List[str]
    risk_factors: List[str]
    mitigation_strategies: List[str]


class SophisticatedROIAnalysisResponse(BaseModel):
    """Response model for sophisticated ROI analysis."""
    
    variety_id: str
    variety_name: str
    
    # Multi-year analysis
    analysis_horizon_years: int
    annual_cash_flows: List[float]
    cumulative_cash_flows: List[float]
    
    # Scenario analysis
    base_case: ScenarioAnalysisResponse
    optimistic: ScenarioAnalysisResponse
    pessimistic: ScenarioAnalysisResponse
    
    # Monte Carlo simulation
    monte_carlo_results: MonteCarloAnalysisResponse
    
    # Risk assessment
    weather_risk_score: float
    market_volatility_risk: float
    yield_volatility_risk: float
    overall_risk_score: float
    
    # Investment recommendation
    investment_recommendation: InvestmentRecommendationResponse
    
    # Financial metrics
    net_present_value: float
    internal_rate_of_return: float
    modified_internal_rate_of_return: float
    profitability_index: float
    discounted_payback_period: float
    
    # Analysis metadata
    analysis_date: datetime
    assumptions_used: Dict[str, Any]
    data_sources: List[str]


# Dependency injection
async def get_economic_analysis_service() -> VarietyEconomicAnalysisService:
    """Get economic analysis service instance."""
    return VarietyEconomicAnalysisService()


@router.post("/analyze", response_model=EconomicAnalysisResponse)
async def analyze_variety_economics(
    request: EconomicAnalysisRequest,
    service: VarietyEconomicAnalysisService = Depends(get_economic_analysis_service)
):
    """
    Perform comprehensive economic analysis for a single crop variety.
    
    This endpoint provides detailed economic analysis including:
    - Net Present Value (NPV) calculations
    - Internal Rate of Return (IRR) analysis
    - Payback period calculations
    - Break-even analysis
    - Risk-adjusted returns
    - Government program integration
    
    Agricultural Use Cases:
    - Variety selection based on economic viability
    - Investment decision support
    - Risk assessment for variety choices
    - Government program optimization
    """
    try:
        # Create mock variety for analysis (in production, would fetch from database)
        variety = EnhancedCropVariety(
            id=request.variety_id,
            variety_name=f"Variety {request.variety_id}",
            crop_name=request.regional_context.get('crop_name', 'corn'),
            yield_potential=None,
            market_attributes=None,
            disease_resistance_profile=None,
            risk_level=None
        )
        
        # Perform economic analysis
        result = await service.analyze_variety_economics(
            variety, 
            request.regional_context, 
            request.farmer_preferences
        )
        
        # Convert to response model
        response = EconomicAnalysisResponse(
            variety_id=result.variety_id,
            variety_name=result.variety_name,
            net_present_value=result.net_present_value,
            internal_rate_of_return=result.internal_rate_of_return,
            payback_period_years=result.payback_period_years,
            break_even_yield=result.break_even_yield,
            break_even_price=result.break_even_price,
            total_seed_cost_per_acre=result.total_seed_cost_per_acre,
            total_input_costs_per_acre=result.total_input_costs_per_acre,
            total_operating_costs_per_acre=result.total_operating_costs_per_acre,
            expected_revenue_per_acre=result.expected_revenue_per_acre,
            expected_profit_per_acre=result.expected_profit_per_acre,
            profit_margin_percent=result.profit_margin_percent,
            risk_adjusted_return=result.risk_adjusted_return,
            volatility_score=result.volatility_score,
            downside_risk=result.downside_risk,
            government_subsidies_per_acre=result.government_subsidies_per_acre,
            insurance_coverage_percent=result.insurance_coverage_percent,
            economic_viability_score=result.economic_viability_score,
            confidence_level=result.confidence_level.value if hasattr(result.confidence_level, 'value') else str(result.confidence_level),
            analysis_date=result.analysis_date,
            market_data_source=result.market_data_source,
            assumptions_used=result.assumptions_used
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in economic analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Economic analysis failed: {str(e)}")


@router.post("/compare", response_model=ComparativeAnalysisResponse)
async def compare_varieties_economics(
    request: ComparativeAnalysisRequest,
    service: VarietyEconomicAnalysisService = Depends(get_economic_analysis_service)
):
    """
    Compare economic viability of multiple crop varieties.
    
    This endpoint provides comparative economic analysis including:
    - Side-by-side economic metrics comparison
    - Ranking by economic viability
    - Best performing varieties by different metrics
    - Risk-adjusted comparison
    
    Agricultural Use Cases:
    - Variety selection from multiple options
    - Portfolio optimization for farm operations
    - Risk diversification analysis
    - Investment prioritization
    """
    try:
        # Create mock varieties for analysis (in production, would fetch from database)
        varieties = []
        for variety_id in request.variety_ids:
            variety = EnhancedCropVariety(
                id=variety_id,
                variety_name=f"Variety {variety_id}",
                crop_name=request.regional_context.get('crop_name', 'corn'),
                yield_potential=None,
                market_attributes=None,
                disease_resistance_profile=None,
                risk_level=None
            )
            varieties.append(variety)
        
        # Perform comparative analysis
        results = await service.compare_varieties_economics(
            varieties, 
            request.regional_context, 
            request.farmer_preferences
        )
        
        # Convert results to response models
        variety_analyses = []
        for variety, result in results:
            analysis_response = EconomicAnalysisResponse(
                variety_id=result.variety_id,
                variety_name=result.variety_name,
                net_present_value=result.net_present_value,
                internal_rate_of_return=result.internal_rate_of_return,
                payback_period_years=result.payback_period_years,
                break_even_yield=result.break_even_yield,
                break_even_price=result.break_even_price,
                total_seed_cost_per_acre=result.total_seed_cost_per_acre,
                total_input_costs_per_acre=result.total_input_costs_per_acre,
                total_operating_costs_per_acre=result.total_operating_costs_per_acre,
                expected_revenue_per_acre=result.expected_revenue_per_acre,
                expected_profit_per_acre=result.expected_profit_per_acre,
                profit_margin_percent=result.profit_margin_percent,
                risk_adjusted_return=result.risk_adjusted_return,
                volatility_score=result.volatility_score,
                downside_risk=result.downside_risk,
                government_subsidies_per_acre=result.government_subsidies_per_acre,
                insurance_coverage_percent=result.insurance_coverage_percent,
                economic_viability_score=result.economic_viability_score,
                confidence_level=result.confidence_level.value if hasattr(result.confidence_level, 'value') else str(result.confidence_level),
                analysis_date=result.analysis_date,
                market_data_source=result.market_data_source,
                assumptions_used=result.assumptions_used
            )
            variety_analyses.append(analysis_response)
        
        # Find best performing varieties
        best_npv = max(variety_analyses, key=lambda x: x.net_present_value)
        best_irr = max(variety_analyses, key=lambda x: x.internal_rate_of_return)
        lowest_risk = min(variety_analyses, key=lambda x: x.downside_risk)
        most_profitable = max(variety_analyses, key=lambda x: x.expected_profit_per_acre)
        
        # Create ranking summary
        ranking_summary = {
            "total_varieties_analyzed": len(variety_analyses),
            "average_economic_score": sum(a.economic_viability_score for a in variety_analyses) / len(variety_analyses),
            "score_range": {
                "min": min(a.economic_viability_score for a in variety_analyses),
                "max": max(a.economic_viability_score for a in variety_analyses)
            },
            "top_3_varieties": [
                {
                    "variety_id": a.variety_id,
                    "variety_name": a.variety_name,
                    "economic_score": a.economic_viability_score
                }
                for a in sorted(variety_analyses, key=lambda x: x.economic_viability_score, reverse=True)[:3]
            ]
        }
        
        response = ComparativeAnalysisResponse(
            analysis_id=f"comparative_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            analysis_date=datetime.utcnow(),
            regional_context=request.regional_context,
            farmer_preferences=request.farmer_preferences,
            variety_analyses=variety_analyses,
            ranking_summary=ranking_summary,
            best_npv_variety=best_npv.variety_id,
            best_irr_variety=best_irr.variety_id,
            lowest_risk_variety=lowest_risk.variety_id,
            most_profitable_variety=most_profitable.variety_id
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in comparative economic analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Comparative analysis failed: {str(e)}")


@router.post("/score", response_model=EconomicScoringResponse)
async def score_variety_economics(
    request: EconomicScoringRequest,
    service: VarietyEconomicAnalysisService = Depends(get_economic_analysis_service)
):
    """
    Get economic viability score for a variety (lightweight endpoint).
    
    This endpoint provides a quick economic viability score without
    detailed analysis, useful for ranking and filtering operations.
    
    Agricultural Use Cases:
    - Quick variety ranking
    - Filtering varieties by economic viability
    - Real-time scoring in recommendation systems
    """
    try:
        # Create mock variety for scoring (in production, would fetch from database)
        variety = EnhancedCropVariety(
            id=request.variety_id,
            variety_name=f"Variety {request.variety_id}",
            crop_name=request.regional_context.get('crop_name', 'corn'),
            yield_potential=None,
            market_attributes=None,
            disease_resistance_profile=None,
            risk_level=None
        )
        
        # Perform economic analysis
        result = await service.analyze_variety_economics(
            variety, 
            request.regional_context, 
            request.farmer_preferences
        )
        
        # Extract scoring factors
        scoring_factors = {
            "npv_score": min(1.0, max(0.0, (result.net_present_value + 1000) / 2000)),
            "irr_score": min(1.0, max(0.0, result.internal_rate_of_return / 30.0)),
            "payback_score": max(0.0, min(1.0, (5.0 - result.payback_period_years) / 5.0)),
            "risk_score": min(1.0, max(0.0, result.risk_adjusted_return / 1000)),
            "volatility_score": result.volatility_score
        }
        
        response = EconomicScoringResponse(
            variety_id=result.variety_id,
            variety_name=result.variety_name,
            economic_viability_score=result.economic_viability_score,
            confidence_level=result.confidence_level.value if hasattr(result.confidence_level, 'value') else str(result.confidence_level),
            scoring_factors=scoring_factors,
            analysis_date=result.analysis_date
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in economic scoring: {e}")
        raise HTTPException(status_code=500, detail=f"Economic scoring failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for economic analysis service."""
    return {
        "status": "healthy", 
        "service": "economic-analysis",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "NPV calculation",
            "IRR analysis", 
            "Payback period",
            "Break-even analysis",
            "Risk assessment",
            "Government program integration",
            "Sophisticated ROI analysis",
            "Multi-year analysis",
            "Scenario modeling",
            "Monte Carlo simulation",
            "Investment recommendations",
            "Advanced financial metrics"
        ]
    }


@router.get("/cost-factors/{crop_name}")
async def get_cost_factors(
    crop_name: str,
    service: VarietyEconomicAnalysisService = Depends(get_economic_analysis_service)
):
    """
    Get default cost factors for a crop type.
    
    This endpoint provides default cost factors used in economic analysis,
    useful for understanding the cost structure assumptions.
    """
    try:
        crop_name_lower = crop_name.lower()
        
        if crop_name_lower not in service.default_cost_factors:
            raise HTTPException(
                status_code=404, 
                detail=f"Cost factors not available for crop: {crop_name}"
            )
        
        cost_factors = service.default_cost_factors[crop_name_lower]
        
        return {
            "crop_name": crop_name,
            "cost_factors": {
                "seed_cost_per_unit": cost_factors.seed_cost_per_unit,
                "seeding_rate_per_acre": cost_factors.seeding_rate_per_acre,
                "fertilizer_cost_per_acre": cost_factors.fertilizer_cost_per_acre,
                "pesticide_cost_per_acre": cost_factors.pesticide_cost_per_acre,
                "fuel_cost_per_acre": cost_factors.fuel_cost_per_acre,
                "labor_cost_per_acre": cost_factors.labor_cost_per_acre,
                "equipment_cost_per_acre": cost_factors.equipment_cost_per_acre,
                "insurance_cost_per_acre": cost_factors.insurance_cost_per_acre,
                "other_inputs_cost_per_acre": cost_factors.other_inputs_cost_per_acre,
                "total_cost_per_acre": cost_factors.total_cost_per_acre()
            },
            "last_updated": datetime.utcnow().isoformat(),
            "source": "default_regional_averages"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cost factors: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cost factors: {str(e)}")


@router.get("/government-programs/{crop_name}")
async def get_government_programs(
    crop_name: str,
    service: VarietyEconomicAnalysisService = Depends(get_economic_analysis_service)
):
    """
    Get government program information for a crop type.
    
    This endpoint provides information about government programs
    and subsidies available for specific crops.
    """
    try:
        crop_name_lower = crop_name.lower()
        
        if crop_name_lower not in service.government_programs:
            raise HTTPException(
                status_code=404, 
                detail=f"Government programs not available for crop: {crop_name}"
            )
        
        programs = service.government_programs[crop_name_lower]
        
        return {
            "crop_name": crop_name,
            "government_programs": programs,
            "last_updated": datetime.utcnow().isoformat(),
            "source": "simplified_program_data",
            "note": "This is simplified data. In production, would integrate with real government databases."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting government programs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get government programs: {str(e)}")


@router.post("/sophisticated-roi", response_model=SophisticatedROIAnalysisResponse)
async def perform_sophisticated_roi_analysis(
    request: SophisticatedROIAnalysisRequest,
    service: VarietyEconomicAnalysisService = Depends(get_economic_analysis_service)
):
    """
    Perform sophisticated ROI and profitability analysis with advanced financial modeling.
    
    This endpoint provides comprehensive ROI analysis including:
    - Multi-year ROI analysis with annual cash flows
    - Scenario modeling (base case, optimistic, pessimistic)
    - Monte Carlo simulation for uncertainty quantification
    - Risk assessment with weather and market volatility
    - Investment recommendations with mitigation strategies
    - Advanced financial metrics (MIRR, PI, discounted payback)
    
    Agricultural Use Cases:
    - Investment decision support for variety selection
    - Risk assessment and portfolio optimization
    - Scenario planning for different market conditions
    - Uncertainty quantification for financial planning
    - Investment recommendation with risk mitigation
    """
    try:
        logger.info(f"Starting sophisticated ROI analysis for variety {request.variety_id}")
        
        # Create mock variety for analysis (in production, would fetch from database)
        variety = EnhancedCropVariety(
            id=request.variety_id,
            variety_name=f"Variety {request.variety_id}",
            crop_name=request.regional_context.get('crop_name', 'corn'),
            yield_potential=None,
            market_attributes=None,
            disease_resistance_profile=None,
            risk_level=None
        )
        
        # Perform sophisticated ROI analysis
        result = await service.perform_sophisticated_roi_analysis(
            variety,
            request.regional_context,
            request.farmer_preferences,
            request.analysis_horizon_years
        )
        
        # Convert scenario analyses to response models
        def convert_scenario_analysis(scenario: ScenarioAnalysis) -> ScenarioAnalysisResponse:
            return ScenarioAnalysisResponse(
                scenario_type=scenario.scenario_type.value,
                net_present_value=scenario.net_present_value,
                internal_rate_of_return=scenario.internal_rate_of_return,
                payback_period_years=scenario.payback_period_years,
                expected_profit_per_acre=scenario.expected_profit_per_acre,
                probability_of_profit=scenario.probability_of_profit,
                confidence_interval_95=list(scenario.confidence_interval_95)
            )
        
        # Convert Monte Carlo results to response model
        monte_carlo_response = MonteCarloAnalysisResponse(
            mean_npv=result.monte_carlo_results.mean_npv,
            median_npv=result.monte_carlo_results.median_npv,
            std_deviation_npv=result.monte_carlo_results.std_deviation_npv,
            probability_of_positive_npv=result.monte_carlo_results.probability_of_positive_npv,
            value_at_risk_95=result.monte_carlo_results.value_at_risk_95,
            expected_shortfall=result.monte_carlo_results.expected_shortfall,
            simulation_iterations=result.monte_carlo_results.simulation_iterations,
            confidence_intervals={
                k: list(v) for k, v in result.monte_carlo_results.confidence_intervals.items()
            }
        )
        
        # Convert investment recommendation to response model
        investment_response = InvestmentRecommendationResponse(
            recommendation_type=result.investment_recommendation.recommendation_type,
            confidence_score=result.investment_recommendation.confidence_score,
            risk_level=result.investment_recommendation.risk_level.value,
            expected_return_percent=result.investment_recommendation.expected_return_percent,
            payback_period_years=result.investment_recommendation.payback_period_years,
            key_factors=result.investment_recommendation.key_factors,
            risk_factors=result.investment_recommendation.risk_factors,
            mitigation_strategies=result.investment_recommendation.mitigation_strategies
        )
        
        # Create comprehensive response
        response = SophisticatedROIAnalysisResponse(
            variety_id=result.variety_id,
            variety_name=result.variety_name,
            analysis_horizon_years=result.analysis_horizon_years,
            annual_cash_flows=result.annual_cash_flows,
            cumulative_cash_flows=result.cumulative_cash_flows,
            base_case=convert_scenario_analysis(result.base_case),
            optimistic=convert_scenario_analysis(result.optimistic),
            pessimistic=convert_scenario_analysis(result.pessimistic),
            monte_carlo_results=monte_carlo_response,
            weather_risk_score=result.weather_risk_score,
            market_volatility_risk=result.market_volatility_risk,
            yield_volatility_risk=result.yield_volatility_risk,
            overall_risk_score=result.overall_risk_score,
            investment_recommendation=investment_response,
            net_present_value=result.net_present_value,
            internal_rate_of_return=result.internal_rate_of_return,
            modified_internal_rate_of_return=result.modified_internal_rate_of_return,
            profitability_index=result.profitability_index,
            discounted_payback_period=result.discounted_payback_period,
            analysis_date=result.analysis_date,
            assumptions_used=result.assumptions_used,
            data_sources=result.data_sources
        )
        
        logger.info(f"Completed sophisticated ROI analysis for variety {request.variety_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error in sophisticated ROI analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Sophisticated ROI analysis failed: {str(e)}")


@router.get("/roi-scenarios/{variety_id}")
async def get_roi_scenarios(
    variety_id: str,
    analysis_horizon_years: int = Query(5, ge=1, le=10, description="Analysis horizon in years"),
    service: VarietyEconomicAnalysisService = Depends(get_economic_analysis_service)
):
    """
    Get ROI scenario analysis for a variety.
    
    This endpoint provides scenario analysis (base case, optimistic, pessimistic)
    for a specific variety without the full sophisticated analysis.
    
    Agricultural Use Cases:
    - Quick scenario comparison
    - Risk assessment overview
    - Investment decision support
    """
    try:
        # Create mock variety for analysis (in production, would fetch from database)
        variety = EnhancedCropVariety(
            id=variety_id,
            variety_name=f"Variety {variety_id}",
            crop_name="corn",  # Default crop
            yield_potential=None,
            market_attributes=None,
            disease_resistance_profile=None,
            risk_level=None
        )
        
        # Default regional context
        regional_context = {
            "crop_name": "corn",
            "region": "US",
            "yield_multiplier": 1.0,
            "price_multiplier": 1.0,
            "cost_multiplier": 1.0
        }
        
        # Perform scenario analysis only
        scenario_results = await service._perform_scenario_analysis(
            variety, regional_context, None, analysis_horizon_years
        )
        
        # Convert to response format
        scenarios = {}
        for scenario_name, scenario in scenario_results.items():
            scenarios[scenario_name] = {
                "scenario_type": scenario.scenario_type.value,
                "net_present_value": scenario.net_present_value,
                "internal_rate_of_return": scenario.internal_rate_of_return,
                "payback_period_years": scenario.payback_period_years,
                "expected_profit_per_acre": scenario.expected_profit_per_acre,
                "probability_of_profit": scenario.probability_of_profit,
                "confidence_interval_95": list(scenario.confidence_interval_95)
            }
        
        return {
            "variety_id": variety_id,
            "analysis_horizon_years": analysis_horizon_years,
            "scenarios": scenarios,
            "analysis_date": datetime.utcnow().isoformat(),
            "summary": {
                "best_scenario": max(scenarios.keys(), key=lambda k: scenarios[k]["net_present_value"]),
                "worst_scenario": min(scenarios.keys(), key=lambda k: scenarios[k]["net_present_value"]),
                "scenario_range": {
                    "min_npv": min(s["net_present_value"] for s in scenarios.values()),
                    "max_npv": max(s["net_present_value"] for s in scenarios.values())
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error in ROI scenarios analysis: {e}")
        raise HTTPException(status_code=500, detail=f"ROI scenarios analysis failed: {str(e)}")


@router.get("/risk-assessment/{variety_id}")
async def get_risk_assessment(
    variety_id: str,
    service: VarietyEconomicAnalysisService = Depends(get_economic_analysis_service)
):
    """
    Get comprehensive risk assessment for a variety.
    
    This endpoint provides detailed risk assessment including weather,
    market volatility, and yield volatility risks.
    
    Agricultural Use Cases:
    - Risk evaluation for variety selection
    - Portfolio risk management
    - Insurance and hedging decisions
    """
    try:
        # Create mock variety for analysis (in production, would fetch from database)
        variety = EnhancedCropVariety(
            id=variety_id,
            variety_name=f"Variety {variety_id}",
            crop_name="corn",  # Default crop
            yield_potential=None,
            market_attributes=None,
            disease_resistance_profile=None,
            risk_level=None
        )
        
        # Default regional context
        regional_context = {
            "crop_name": "corn",
            "region": "US",
            "weather_risk_score": 0.5,
            "price_volatility": 0.15,
            "yield_volatility_adjustment": 0.0
        }
        
        # Perform risk assessment
        risk_assessments = await service._calculate_comprehensive_risk_assessment(
            variety, regional_context, None
        )
        
        return {
            "variety_id": variety_id,
            "risk_assessment": {
                "weather_risk_score": risk_assessments["weather_risk"],
                "market_volatility_risk": risk_assessments["market_volatility"],
                "yield_volatility_risk": risk_assessments["yield_volatility"],
                "overall_risk_score": risk_assessments["overall_risk"]
            },
            "risk_level": "high" if risk_assessments["overall_risk"] > 0.7 else 
                         "medium" if risk_assessments["overall_risk"] > 0.4 else "low",
            "analysis_date": datetime.utcnow().isoformat(),
            "risk_factors": await service._generate_risk_factors(risk_assessments, {}),
            "mitigation_strategies": await service._generate_mitigation_strategies(
                [], 
                RiskLevel.HIGH if risk_assessments["overall_risk"] > 0.7 else RiskLevel.MEDIUM
            )
        }
        
    except Exception as e:
        logger.error(f"Error in risk assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")