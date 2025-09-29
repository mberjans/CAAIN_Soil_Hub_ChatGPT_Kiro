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
        RevenueFactors
    )
    from ..models.crop_variety_models import EnhancedCropVariety
    from ..models.service_models import ConfidenceLevel
except ImportError:
    from services.variety_economics import (
        VarietyEconomicAnalysisService,
        EconomicAnalysisResult,
        CostFactors,
        RevenueFactors
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
            "Government program integration"
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