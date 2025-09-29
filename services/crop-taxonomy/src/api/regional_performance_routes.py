"""
Regional Performance Scoring API Routes
TICKET-005_crop-variety-recommendations-11.2

FastAPI routes for regional performance scoring and analysis.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from uuid import uuid4
import logging

from ..services.regional_performance_scoring_service import (
    RegionalPerformanceScoringService,
    PerformanceMetric,
    StabilityMeasure,
    AdaptationType
)
from ..models.regional_performance_models import (
    RegionalPerformanceRequest,
    RegionalPerformanceResponse,
    VarietyPerformanceSummaryRequest,
    VarietyPerformanceSummaryResponse,
    StabilityAnalysisRequest,
    StabilityAnalysisResponse,
    AMMIAnalysisRequest,
    AMMIAnalysisResponse,
    GGEBiplotRequest,
    GGEBiplotResponse,
    RegionalRankingRequest,
    RegionalRankingResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/regional-performance", tags=["regional-performance"])

# Dependency injection
async def get_regional_performance_service() -> RegionalPerformanceScoringService:
    """Get regional performance scoring service instance."""
    return RegionalPerformanceScoringService()

@router.post("/analyze", response_model=RegionalPerformanceResponse)
async def analyze_regional_performance(
    request: RegionalPerformanceRequest,
    service: RegionalPerformanceScoringService = Depends(get_regional_performance_service)
):
    """
    Perform comprehensive regional performance analysis.
    
    This endpoint provides sophisticated regional performance scoring including:
    - Multi-location performance analysis
    - Genotype-by-environment interaction modeling
    - AMMI analysis
    - GGE biplot analysis
    - Stability analysis and adaptability assessment
    - Regional performance rankings
    - Environmental data integration
    """
    try:
        logger.info(f"Starting regional performance analysis for {request.crop_type}")
        
        # Perform the analysis
        analysis_results = await service.analyze_regional_performance(
            crop_type=request.crop_type,
            varieties=request.varieties,
            locations=request.locations,
            years=request.years,
            performance_metrics=request.performance_metrics
        )
        
        if "error" in analysis_results:
            raise HTTPException(status_code=400, detail=analysis_results["error"])
        
        return RegionalPerformanceResponse(
            analysis_id=analysis_results["analysis_id"],
            crop_type=analysis_results["crop_type"],
            varieties_analyzed=analysis_results["varieties_analyzed"],
            locations_analyzed=analysis_results["locations_analyzed"],
            years_analyzed=analysis_results["years_analyzed"],
            multi_location_analysis=analysis_results["multi_location_analysis"],
            gxe_analysis=analysis_results["gxe_analysis"],
            ammi_analysis=analysis_results["ammi_analysis"],
            gge_analysis=analysis_results["gge_analysis"],
            stability_analysis=analysis_results["stability_analysis"],
            regional_rankings=analysis_results["regional_rankings"],
            environmental_integration=analysis_results["environmental_integration"],
            analysis_timestamp=analysis_results["analysis_timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Error in regional performance analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/variety-summary", response_model=VarietyPerformanceSummaryResponse)
async def get_variety_performance_summary(
    request: VarietyPerformanceSummaryRequest,
    service: RegionalPerformanceScoringService = Depends(get_regional_performance_service)
):
    """
    Get comprehensive performance summary for a specific variety.
    
    Provides detailed performance metrics, stability analysis, and regional
    adaptation recommendations for a single variety.
    """
    try:
        logger.info(f"Getting performance summary for {request.variety_name}")
        
        summary = await service.get_variety_performance_summary(
            variety_name=request.variety_name,
            crop_type=request.crop_type,
            years=request.years
        )
        
        return VarietyPerformanceSummaryResponse(
            variety_name=summary["variety_name"],
            crop_type=summary["crop_type"],
            years_analyzed=summary["years_analyzed"],
            overall_performance=summary["overall_performance"],
            stability_metrics=summary["stability_metrics"],
            recommendations=summary["recommendations"]
        )
        
    except Exception as e:
        logger.error(f"Error getting variety performance summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stability-analysis", response_model=StabilityAnalysisResponse)
async def perform_stability_analysis(
    request: StabilityAnalysisRequest,
    service: RegionalPerformanceScoringService = Depends(get_regional_performance_service)
):
    """
    Perform detailed stability analysis for varieties.
    
    Analyzes variety stability across environments using multiple
    stability measures including CV, regression coefficient, and
    deviation from regression.
    """
    try:
        logger.info(f"Performing stability analysis for {len(request.varieties)} varieties")
        
        # Get trial data
        trial_data = await service._get_trial_data(
            request.crop_type,
            request.varieties,
            request.locations,
            request.years
        )
        
        # Perform stability analysis
        stability_results = await service._perform_stability_analysis(trial_data)
        
        return StabilityAnalysisResponse(
            crop_type=request.crop_type,
            varieties_analyzed=request.varieties,
            stability_measures=stability_results.variety_stability,
            adaptation_types=stability_results.adaptation_types,
            stability_rankings=stability_results.stability_rankings,
            recommendations=stability_results.adaptation_recommendations
        )
        
    except Exception as e:
        logger.error(f"Error in stability analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ammi-analysis", response_model=AMMIAnalysisResponse)
async def perform_ammi_analysis(
    request: AMMIAnalysisRequest,
    service: RegionalPerformanceScoringService = Depends(get_regional_performance_service)
):
    """
    Perform AMMI (Additive Main Effects and Multiplicative Interaction) analysis.
    
    Analyzes genotype and environment main effects along with their
    multiplicative interactions using principal component analysis.
    """
    try:
        logger.info(f"Performing AMMI analysis for {len(request.varieties)} varieties")
        
        # Get trial data
        trial_data = await service._get_trial_data(
            request.crop_type,
            request.varieties,
            request.locations,
            request.years
        )
        
        # Perform AMMI analysis
        ammi_results = await service._perform_ammi_analysis(trial_data)
        
        return AMMIAnalysisResponse(
            crop_type=request.crop_type,
            varieties_analyzed=request.varieties,
            locations_analyzed=request.locations,
            genotype_effects=ammi_results.genotype_effects,
            environment_effects=ammi_results.environment_effects,
            interaction_effects=ammi_results.interaction_effects,
            explained_variance=ammi_results.explained_variance,
            ipca_scores=ammi_results.ipca_scores,
            stability_values=ammi_results.stability_values
        )
        
    except Exception as e:
        logger.error(f"Error in AMMI analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/gge-biplot", response_model=GGEBiplotResponse)
async def perform_gge_biplot_analysis(
    request: GGEBiplotRequest,
    service: RegionalPerformanceScoringService = Depends(get_regional_performance_service)
):
    """
    Perform GGE (Genotype + Genotype-by-Environment) biplot analysis.
    
    Creates biplots for visualizing genotype and environment relationships,
    including "which won where" and "mean vs stability" analyses.
    """
    try:
        logger.info(f"Performing GGE biplot analysis for {len(request.varieties)} varieties")
        
        # Get trial data
        trial_data = await service._get_trial_data(
            request.crop_type,
            request.varieties,
            request.locations,
            request.years
        )
        
        # Perform GGE analysis
        gge_results = await service._perform_gge_analysis(trial_data)
        
        return GGEBiplotResponse(
            crop_type=request.crop_type,
            varieties_analyzed=request.varieties,
            locations_analyzed=request.locations,
            genotype_scores=gge_results.genotype_scores,
            environment_scores=gge_results.environment_scores,
            explained_variance=gge_results.explained_variance,
            which_won_where=gge_results.which_won_where,
            mean_vs_stability=gge_results.mean_vs_stability
        )
        
    except Exception as e:
        logger.error(f"Error in GGE biplot analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/regional-rankings", response_model=RegionalRankingResponse)
async def generate_regional_rankings(
    request: RegionalRankingRequest,
    service: RegionalPerformanceScoringService = Depends(get_regional_performance_service)
):
    """
    Generate regional performance rankings for varieties.
    
    Provides comprehensive rankings across different regions,
    performance trends, and adaptation zone recommendations.
    """
    try:
        logger.info(f"Generating regional rankings for {len(request.varieties)} varieties")
        
        # Get trial data
        trial_data = await service._get_trial_data(
            request.crop_type,
            request.varieties,
            request.locations,
            request.years
        )
        
        # Perform multi-location analysis
        multi_location_analysis = await service._perform_multi_location_analysis(trial_data)
        
        # Perform stability analysis
        stability_analysis = await service._perform_stability_analysis(trial_data)
        
        # Generate regional rankings
        ranking_results = await service._generate_regional_rankings(
            trial_data, multi_location_analysis, stability_analysis
        )
        
        return RegionalRankingResponse(
            crop_type=request.crop_type,
            varieties_analyzed=request.varieties,
            locations_analyzed=request.locations,
            variety_rankings=ranking_results.variety_rankings,
            regional_winners=ranking_results.regional_winners,
            performance_trends=ranking_results.performance_trends,
            adaptation_zones=ranking_results.adaptation_zones
        )
        
    except Exception as e:
        logger.error(f"Error generating regional rankings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance-metrics")
async def get_available_performance_metrics():
    """Get list of available performance metrics."""
    return {
        "performance_metrics": [metric.value for metric in PerformanceMetric],
        "stability_measures": [measure.value for measure in StabilityMeasure],
        "adaptation_types": [adaptation.value for adaptation in AdaptationType]
    }

@router.get("/health")
async def health_check():
    """Health check endpoint for service monitoring."""
    return {"status": "healthy", "service": "regional-performance-scoring"}

# Example usage endpoints for testing
@router.get("/example-analysis")
async def get_example_analysis():
    """Get example analysis results for testing purposes."""
    return {
        "example_request": {
            "crop_type": "corn",
            "varieties": ["Pioneer P1197AMXT", "DeKalb DKC61-69", "Syngenta NK603"],
            "locations": ["Iowa_1", "Illinois_1", "Nebraska_1", "Minnesota_1"],
            "years": [2022, 2023, 2024],
            "performance_metrics": ["yield", "quality", "stability"]
        },
        "example_response": {
            "analysis_id": "12345678-1234-5678-9abc-123456789abc",
            "crop_type": "corn",
            "varieties_analyzed": ["Pioneer P1197AMXT", "DeKalb DKC61-69", "Syngenta NK603"],
            "locations_analyzed": ["Iowa_1", "Illinois_1", "Nebraska_1", "Minnesota_1"],
            "years_analyzed": [2022, 2023, 2024],
            "analysis_timestamp": "2024-01-15T10:30:00Z"
        }
    }