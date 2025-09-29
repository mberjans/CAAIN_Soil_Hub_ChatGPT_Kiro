"""
Trial Data API Routes
TICKET-005_crop-variety-recommendations-11.1

FastAPI routes for university trial data access and management.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from uuid import uuid4
import logging

from ..services.trial_data_service import (
    UniversityTrialDataService,
    TrialDataSource,
    TrialDataQuality,
    TrialSummary
)
from ..models.trial_data_models import (
    TrialDataRequest,
    TrialDataResponse,
    VarietyPerformanceRequest,
    VarietyPerformanceResponse,
    RegionalTrialRequest,
    RegionalTrialResponse,
    TrialIngestionRequest,
    TrialIngestionResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/trial-data", tags=["trial-data"])

# Dependency injection
async def get_trial_data_service() -> UniversityTrialDataService:
    """Get trial data service instance."""
    return UniversityTrialDataService()

@router.get("/sources", response_model=Dict[str, Any])
async def get_available_sources():
    """
    Get list of available university trial data sources.
    
    Returns information about all configured university trial data sources
    including their names, URLs, supported crop types, and update frequencies.
    """
    try:
        async with UniversityTrialDataService() as service:
            sources_info = {}
            for source_name, config in service.data_sources.items():
                sources_info[source_name] = {
                    "name": config["name"],
                    "url": config["url"],
                    "crop_types": config["crop_types"],
                    "states": config["states"],
                    "data_format": config["data_format"],
                    "update_frequency": config["update_frequency"]
                }
            return {"sources": sources_info}
    except Exception as e:
        logger.error(f"Error getting trial data sources: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trial data sources")

@router.post("/ingest", response_model=TrialIngestionResponse)
async def ingest_trial_data(
    request: TrialIngestionRequest,
    background_tasks: BackgroundTasks,
    service: UniversityTrialDataService = Depends(get_trial_data_service)
):
    """
    Ingest trial data from specified university sources.
    
    This endpoint triggers the ingestion of variety trial data from university
    sources. The ingestion can be run in the background for large datasets.
    
    Agricultural Use Cases:
    - Update variety performance data from latest university trials
    - Integrate multi-year trial data for trend analysis
    - Refresh regional adaptation data from extension services
    """
    try:
        if request.run_in_background:
            # Run ingestion in background
            background_tasks.add_task(
                _run_background_ingestion,
                request.source_names,
                request.year,
                request.crop_type
            )
            return TrialIngestionResponse(
                status="started",
                message="Trial data ingestion started in background",
                ingestion_id=str(uuid4())
            )
        else:
            # Run ingestion synchronously
            results = await _run_ingestion(request.source_names, request.year, request.crop_type)
            return TrialIngestionResponse(
                status="completed",
                message=f"Successfully ingested {results['total_trials']} trials",
                ingestion_id=str(uuid4()),
                results=results
            )
    except Exception as e:
        logger.error(f"Error ingesting trial data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest trial data: {str(e)}")

@router.get("/trials", response_model=TrialDataResponse)
async def get_trial_data(
    source: Optional[str] = Query(None, description="Filter by data source"),
    crop_type: Optional[str] = Query(None, description="Filter by crop type"),
    year: Optional[int] = Query(None, description="Filter by trial year"),
    state: Optional[str] = Query(None, description="Filter by state"),
    quality: Optional[TrialDataQuality] = Query(None, description="Filter by data quality"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of trials to return"),
    offset: int = Query(0, ge=0, description="Number of trials to skip"),
    service: UniversityTrialDataService = Depends(get_trial_data_service)
):
    """
    Get trial data with optional filtering.
    
    Retrieve variety trial data from university sources with various filtering
    options. Supports pagination for large result sets.
    
    Agricultural Use Cases:
    - Find trials for specific crops and regions
    - Analyze trial data quality and reliability
    - Access historical trial data for trend analysis
    """
    try:
        async with service:
            # Get trials from specified source or all sources
            if source:
                trials = await service.ingest_trial_data(source, year, crop_type)
            else:
                trials = []
                for source_name in service.data_sources.keys():
                    source_trials = await service.ingest_trial_data(source_name, year, crop_type)
                    trials.extend(source_trials)
            
            # Apply filters
            filtered_trials = trials
            
            if crop_type:
                filtered_trials = [t for t in filtered_trials if t.crop_type.lower() == crop_type.lower()]
            
            if year:
                filtered_trials = [t for t in filtered_trials if t.trial_year == year]
            
            if state:
                filtered_trials = [t for t in filtered_trials if t.location.state.lower() == state.lower()]
            
            if quality:
                filtered_trials = [t for t in filtered_trials if t.data_quality == quality]
            
            # Apply pagination
            total_count = len(filtered_trials)
            paginated_trials = filtered_trials[offset:offset + limit]
            
            # Convert to response format
            trial_data = []
            for trial in paginated_trials:
                trial_data.append({
                    "trial_id": trial.trial_id,
                    "trial_name": trial.trial_name,
                    "crop_type": trial.crop_type,
                    "trial_year": trial.trial_year,
                    "location": {
                        "location_name": trial.location.location_name,
                        "state": trial.location.state,
                        "county": trial.location.county,
                        "climate_zone": trial.location.climate_zone,
                        "soil_type": trial.location.soil_type
                    },
                    "design": {
                        "design_type": trial.design.design_type,
                        "replications": trial.design.replications,
                        "plot_size_sq_meters": trial.design.plot_size_sq_meters,
                        "growing_season_days": trial.design.growing_season_days
                    },
                    "statistics": {
                        "varieties_tested": trial.varieties_tested,
                        "mean_yield": trial.mean_yield,
                        "std_dev_yield": trial.std_dev_yield,
                        "cv_percent": trial.cv_percent
                    },
                    "quality": {
                        "data_quality": trial.data_quality.value,
                        "outliers_detected": trial.outliers_detected,
                        "validation_notes": trial.validation_notes
                    },
                    "metadata": {
                        "data_source": trial.data_source.value,
                        "source_url": trial.source_url,
                        "last_updated": trial.last_updated.isoformat() if trial.last_updated else None
                    }
                })
            
            return TrialDataResponse(
                trials=trial_data,
                total_count=total_count,
                limit=limit,
                offset=offset,
                filters_applied={
                    "source": source,
                    "crop_type": crop_type,
                    "year": year,
                    "state": state,
                    "quality": quality.value if quality else None
                }
            )
            
    except Exception as e:
        logger.error(f"Error getting trial data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trial data: {str(e)}")

@router.get("/trials/{trial_id}", response_model=Dict[str, Any])
async def get_trial_details(
    trial_id: str,
    service: UniversityTrialDataService = Depends(get_trial_data_service)
):
    """
    Get detailed information for a specific trial.
    
    Retrieve comprehensive details about a specific variety trial including
    all varieties tested, statistical analysis, and quality metrics.
    """
    try:
        async with service:
            # Search for trial across all sources
            trial = None
            for source_name in service.data_sources.keys():
                trials = await service.ingest_trial_data(source_name)
                trial = next((t for t in trials if t.trial_id == trial_id), None)
                if trial:
                    break
            
            if not trial:
                raise HTTPException(status_code=404, detail=f"Trial {trial_id} not found")
            
            # Return detailed trial information
            return {
                "trial_id": trial.trial_id,
                "trial_name": trial.trial_name,
                "crop_type": trial.crop_type,
                "trial_year": trial.trial_year,
                "location": {
                    "location_id": trial.location.location_id,
                    "location_name": trial.location.location_name,
                    "latitude": trial.location.latitude,
                    "longitude": trial.location.longitude,
                    "state": trial.location.state,
                    "county": trial.location.county,
                    "climate_zone": trial.location.climate_zone,
                    "soil_type": trial.location.soil_type,
                    "elevation_meters": trial.location.elevation_meters,
                    "irrigation_available": trial.location.irrigation_available
                },
                "design": {
                    "design_type": trial.design.design_type,
                    "replications": trial.design.replications,
                    "plot_size_sq_meters": trial.design.plot_size_sq_meters,
                    "planting_date": trial.design.planting_date.isoformat() if trial.design.planting_date else None,
                    "harvest_date": trial.design.harvest_date.isoformat() if trial.design.harvest_date else None,
                    "growing_season_days": trial.design.growing_season_days,
                    "management_practices": trial.design.management_practices
                },
                "statistics": {
                    "varieties_tested": trial.varieties_tested,
                    "check_variety": trial.check_variety,
                    "mean_yield": trial.mean_yield,
                    "std_dev_yield": trial.std_dev_yield,
                    "cv_percent": trial.cv_percent,
                    "lsd_05": trial.lsd_05,
                    "f_statistic": trial.f_statistic,
                    "p_value": trial.p_value
                },
                "quality": {
                    "data_quality": trial.data_quality.value,
                    "outliers_detected": trial.outliers_detected,
                    "missing_data_percent": trial.missing_data_percent,
                    "validation_notes": trial.validation_notes
                },
                "metadata": {
                    "data_source": trial.data_source.value,
                    "source_url": trial.source_url,
                    "last_updated": trial.last_updated.isoformat() if trial.last_updated else None
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trial details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trial details: {str(e)}")

@router.post("/variety-performance", response_model=VarietyPerformanceResponse)
async def get_variety_performance(
    request: VarietyPerformanceRequest,
    service: UniversityTrialDataService = Depends(get_trial_data_service)
):
    """
    Get performance summary for a specific variety across multiple trials.
    
    Analyze variety performance across multiple trials and years to provide
    comprehensive performance metrics including yield stability and adaptation.
    
    Agricultural Use Cases:
    - Compare variety performance across different regions
    - Assess yield stability and consistency
    - Identify optimal growing regions for varieties
    - Support variety selection decisions
    """
    try:
        async with service:
            performance = await service.get_variety_performance_summary(
                request.variety_name,
                request.crop_type,
                request.years
            )
            
            return VarietyPerformanceResponse(
                variety_name=performance["variety_name"],
                crop_type=performance["crop_type"],
                trials_found=performance["trials_found"],
                years_covered=performance["years_covered"],
                states_covered=performance["states_covered"],
                performance_metrics={
                    "average_yield": performance["average_yield"],
                    "yield_stability": performance["yield_stability"],
                    "adaptation_regions": performance["adaptation_regions"]
                },
                data_quality_summary=performance["data_quality_summary"]
            )
            
    except Exception as e:
        logger.error(f"Error getting variety performance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve variety performance: {str(e)}")

@router.post("/regional-trials", response_model=RegionalTrialResponse)
async def get_regional_trials(
    request: RegionalTrialRequest,
    service: UniversityTrialDataService = Depends(get_trial_data_service)
):
    """
    Get trial data filtered by region.
    
    Retrieve variety trial data for specific regions with optional filtering
    by crop type and year.
    
    Agricultural Use Cases:
    - Find trials relevant to specific growing regions
    - Compare variety performance across different states
    - Access regional adaptation data
    """
    try:
        async with service:
            trials = await service.get_trial_data_by_region(
                request.state,
                request.crop_type,
                request.year
            )
            
            # Convert to response format
            trial_data = []
            for trial in trials:
                trial_data.append({
                    "trial_id": trial.trial_id,
                    "trial_name": trial.trial_name,
                    "crop_type": trial.crop_type,
                    "trial_year": trial.trial_year,
                    "location": {
                        "location_name": trial.location.location_name,
                        "state": trial.location.state,
                        "county": trial.location.county,
                        "climate_zone": trial.location.climate_zone
                    },
                    "statistics": {
                        "varieties_tested": trial.varieties_tested,
                        "mean_yield": trial.mean_yield,
                        "cv_percent": trial.cv_percent
                    },
                    "data_quality": trial.data_quality.value
                })
            
            return RegionalTrialResponse(
                state=request.state,
                crop_type=request.crop_type,
                year=request.year,
                trials=trial_data,
                total_count=len(trial_data)
            )
            
    except Exception as e:
        logger.error(f"Error getting regional trials: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve regional trials: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint for trial data service."""
    return {
        "status": "healthy",
        "service": "trial-data",
        "timestamp": datetime.now().isoformat(),
        "available_sources": len(UniversityTrialDataService().data_sources)
    }

# Background task functions
async def _run_background_ingestion(source_names: List[str], year: Optional[int], crop_type: Optional[str]):
    """Run trial data ingestion in background."""
    try:
        async with UniversityTrialDataService() as service:
            results = await _run_ingestion(source_names, year, crop_type)
            logger.info(f"Background ingestion completed: {results}")
    except Exception as e:
        logger.error(f"Background ingestion failed: {e}")

async def _run_ingestion(source_names: List[str], year: Optional[int], crop_type: Optional[str]) -> Dict[str, Any]:
    """Run trial data ingestion and return results."""
    async with UniversityTrialDataService() as service:
        all_trials = []
        source_results = {}
        
        for source_name in source_names:
            try:
                trials = await service.ingest_trial_data(source_name, year, crop_type)
                all_trials.extend(trials)
                source_results[source_name] = {
                    "trials_ingested": len(trials),
                    "status": "success"
                }
            except Exception as e:
                logger.error(f"Error ingesting from {source_name}: {e}")
                source_results[source_name] = {
                    "trials_ingested": 0,
                    "status": "error",
                    "error": str(e)
                }
        
        # Save trials to database
        save_results = await service.save_trial_data(all_trials)
        
        return {
            "total_trials": len(all_trials),
            "source_results": source_results,
            "save_results": save_results
        }