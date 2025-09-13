"""
Data Integration API Routes

FastAPI routes for external agricultural data integration using the
unified data ingestion framework.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import structlog

from ..services.ingestion_service import get_ingestion_service, DataIngestionService
from ..services.data_ingestion_framework import IngestionResult

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["data-integration"])


class LocationRequest(BaseModel):
    """Request model for location-based data."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")


class WeatherResponse(BaseModel):
    """Enhanced weather data response model."""
    temperature_f: float
    humidity_percent: float
    precipitation_inches: float
    wind_speed_mph: float
    wind_direction: str
    conditions: str
    pressure_mb: float
    visibility_miles: float
    uv_index: Optional[float] = None
    timestamp: datetime
    source: str = "NOAA/OpenWeatherMap"


class ForecastResponse(BaseModel):
    """Weather forecast response model."""
    date: str
    high_temp_f: float
    low_temp_f: float
    precipitation_chance: float
    precipitation_amount: float
    conditions: str
    wind_speed_mph: float
    humidity_percent: float


class AgriculturalWeatherResponse(BaseModel):
    """Agricultural weather metrics response."""
    growing_degree_days: float
    accumulated_precipitation: float
    days_since_rain: int
    soil_temperature_f: Optional[float] = None
    evapotranspiration_inches: Optional[float] = None
    recommendations: List[str] = []


class SoilCharacteristicsResponse(BaseModel):
    """Soil characteristics response model."""
    soil_series: str
    soil_texture: str
    drainage_class: str
    typical_ph_range: Dict[str, float]
    organic_matter_typical: float
    slope_range: str
    parent_material: Optional[str] = None
    depth_to_bedrock: Optional[str] = None
    flooding_frequency: Optional[str] = None
    ponding_frequency: Optional[str] = None
    hydrologic_group: Optional[str] = None
    available_water_capacity: Optional[float] = None
    permeability: Optional[str] = None
    erosion_factor_k: Optional[float] = None
    data_source: str = "USDA/SoilGrids"


class SoilNutrientRangesResponse(BaseModel):
    """Soil nutrient ranges response model."""
    phosphorus_ppm_range: Dict[str, float]
    potassium_ppm_range: Dict[str, float]
    nitrogen_typical: float
    cec_range: Dict[str, float]
    base_saturation_range: Dict[str, float]
    micronutrient_status: Dict[str, str]


class SoilSuitabilityResponse(BaseModel):
    """Soil suitability response model."""
    crop_suitability: Dict[str, str]
    limitations: List[str]
    management_considerations: List[str]
    irrigation_suitability: str
    erosion_risk: str


@router.post("/weather/current", response_model=WeatherResponse)
async def get_current_weather(
    location: LocationRequest,
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get current weather data for a location.
    
    Uses the unified data ingestion framework with caching, validation,
    and fallback mechanisms for reliable weather data delivery.
    
    Args:
        location: GPS coordinates (latitude, longitude)
        
    Returns:
        Current weather conditions with agricultural relevance
    """
    try:
        logger.info("Fetching current weather via ingestion framework", 
                   latitude=location.latitude, longitude=location.longitude)
        
        result = await ingestion_service.get_weather_data(
            location.latitude, location.longitude, "current_weather"
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Weather data ingestion failed: {result.error_message}"
            )
        
        weather_data = result.data
        
        return WeatherResponse(
            temperature_f=weather_data["temperature_f"],
            humidity_percent=weather_data["humidity_percent"],
            precipitation_inches=weather_data["precipitation_inches"],
            wind_speed_mph=weather_data["wind_speed_mph"],
            wind_direction=weather_data["wind_direction"],
            conditions=weather_data["conditions"],
            pressure_mb=weather_data["pressure_mb"],
            visibility_miles=weather_data["visibility_miles"],
            uv_index=weather_data.get("uv_index"),
            timestamp=datetime.fromisoformat(weather_data["timestamp"].replace("Z", "+00:00")) if weather_data.get("timestamp") else datetime.utcnow(),
            source=f"{weather_data.get('data_source', 'weather_service')} (quality: {result.quality_score:.2f})"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching current weather", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching weather data: {str(e)}"
        )


@router.post("/weather/forecast", response_model=List[ForecastResponse])
async def get_weather_forecast(
    location: LocationRequest, 
    days: int = 7,
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get weather forecast for a location.
    
    Uses the unified data ingestion framework for reliable forecast data
    with caching and validation.
    
    Args:
        location: GPS coordinates (latitude, longitude)
        days: Number of forecast days (1-14, default 7)
        
    Returns:
        Daily weather forecast for agricultural planning
    """
    # Validate days parameter
    if not 1 <= days <= 14:
        raise HTTPException(
            status_code=422,
            detail="Days parameter must be between 1 and 14"
        )
    
    try:
        logger.info("Fetching weather forecast via ingestion framework", 
                   latitude=location.latitude, longitude=location.longitude, days=days)
        
        result = await ingestion_service.get_weather_data(
            location.latitude, location.longitude, "forecast", days=days
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Weather forecast ingestion failed: {result.error_message}"
            )
        
        forecast_data = result.data["forecast"]
        
        return [
            ForecastResponse(
                date=day["date"],
                high_temp_f=day["high_temp_f"],
                low_temp_f=day["low_temp_f"],
                precipitation_chance=day["precipitation_chance"],
                precipitation_amount=day["precipitation_amount"],
                conditions=day["conditions"],
                wind_speed_mph=day["wind_speed_mph"],
                humidity_percent=day["humidity_percent"]
            )
            for day in forecast_data
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching weather forecast", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching weather forecast: {str(e)}"
        )


@router.post("/weather/agricultural-metrics", response_model=AgriculturalWeatherResponse)
async def get_agricultural_weather_metrics(
    location: LocationRequest, 
    base_temp_f: float = 50.0,
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get agricultural-specific weather metrics.
    
    Uses the unified data ingestion framework to calculate growing degree days,
    precipitation accumulation, and other agricultural weather metrics.
    
    Args:
        location: GPS coordinates (latitude, longitude)
        base_temp_f: Base temperature for growing degree days calculation
        
    Returns:
        Agricultural weather metrics and recommendations
    """
    # Validate base temperature parameter
    if not 32.0 <= base_temp_f <= 80.0:
        raise HTTPException(
            status_code=422,
            detail="Base temperature must be between 32°F and 80°F"
        )
    
    try:
        logger.info("Calculating agricultural weather metrics via ingestion framework", 
                   latitude=location.latitude, longitude=location.longitude, base_temp=base_temp_f)
        
        result = await ingestion_service.get_weather_data(
            location.latitude, location.longitude, "agricultural_metrics", base_temp_f=base_temp_f
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Agricultural weather metrics ingestion failed: {result.error_message}"
            )
        
        metrics_data = result.data
        
        # Generate agricultural recommendations based on metrics
        recommendations = []
        
        if metrics_data.get("days_since_rain", 0) > 7:
            recommendations.append("Consider irrigation - extended dry period detected")
        
        if metrics_data.get("growing_degree_days", 0) > 30:
            recommendations.append("High GDD accumulation - monitor crop development closely")
        
        if metrics_data.get("accumulated_precipitation", 0) > 3.0:
            recommendations.append("High precipitation - monitor for disease pressure and field access")
        
        if metrics_data.get("soil_temperature_f") and metrics_data["soil_temperature_f"] < 50:
            recommendations.append("Soil temperature may limit nutrient uptake and root growth")
        
        return AgriculturalWeatherResponse(
            growing_degree_days=metrics_data.get("growing_degree_days", 0.0),
            accumulated_precipitation=metrics_data.get("accumulated_precipitation", 0.0),
            days_since_rain=metrics_data.get("days_since_rain", 0),
            soil_temperature_f=metrics_data.get("soil_temperature_f"),
            evapotranspiration_inches=metrics_data.get("evapotranspiration_inches"),
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error calculating agricultural weather metrics", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating agricultural weather metrics: {str(e)}"
        )


@router.post("/soil/characteristics", response_model=SoilCharacteristicsResponse)
async def get_soil_characteristics(
    location: LocationRequest,
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get comprehensive soil characteristics for a location.
    
    Uses the unified data ingestion framework with USDA Web Soil Survey
    and SoilGrids integration for reliable soil data delivery.
    
    Args:
        location: GPS coordinates (latitude, longitude)
        
    Returns:
        Detailed soil characteristics including texture, drainage, pH, and more
    """
    try:
        logger.info("Fetching soil characteristics via ingestion framework", 
                   latitude=location.latitude, longitude=location.longitude)
        
        result = await ingestion_service.get_soil_data(
            location.latitude, location.longitude, "soil_characteristics"
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Soil characteristics ingestion failed: {result.error_message}"
            )
        
        soil_data = result.data
        
        return SoilCharacteristicsResponse(
            soil_series=soil_data["soil_series"],
            soil_texture=soil_data["soil_texture"],
            drainage_class=soil_data["drainage_class"],
            typical_ph_range=soil_data["typical_ph_range"],
            organic_matter_typical=soil_data["organic_matter_typical"],
            slope_range=soil_data["slope_range"],
            parent_material=soil_data.get("parent_material"),
            depth_to_bedrock=soil_data.get("depth_to_bedrock"),
            flooding_frequency=soil_data.get("flooding_frequency"),
            ponding_frequency=soil_data.get("ponding_frequency"),
            hydrologic_group=soil_data.get("hydrologic_group"),
            available_water_capacity=soil_data.get("available_water_capacity"),
            permeability=soil_data.get("permeability"),
            erosion_factor_k=soil_data.get("erosion_factor_k"),
            data_source=f"{soil_data.get('data_source', 'soil_service')} (quality: {result.quality_score:.2f})"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching soil characteristics", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching soil characteristics: {str(e)}"
        )


@router.post("/soil/nutrient-ranges", response_model=SoilNutrientRangesResponse)
async def get_soil_nutrient_ranges(
    location: LocationRequest,
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get typical nutrient ranges for soil at a location.
    
    Uses the unified data ingestion framework to provide expected nutrient
    levels and ranges based on soil type and characteristics.
    
    Args:
        location: GPS coordinates (latitude, longitude)
        
    Returns:
        Typical nutrient ranges and micronutrient status for the soil type
    """
    try:
        logger.info("Fetching soil nutrient ranges via ingestion framework", 
                   latitude=location.latitude, longitude=location.longitude)
        
        result = await ingestion_service.get_soil_data(
            location.latitude, location.longitude, "nutrient_ranges"
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Soil nutrient ranges ingestion failed: {result.error_message}"
            )
        
        nutrient_data = result.data
        
        return SoilNutrientRangesResponse(
            phosphorus_ppm_range=nutrient_data["phosphorus_ppm_range"],
            potassium_ppm_range=nutrient_data["potassium_ppm_range"],
            nitrogen_typical=nutrient_data["nitrogen_typical"],
            cec_range=nutrient_data["cec_range"],
            base_saturation_range=nutrient_data["base_saturation_range"],
            micronutrient_status=nutrient_data["micronutrient_status"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching soil nutrient ranges", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching soil nutrient ranges: {str(e)}"
        )


@router.post("/soil/crop-suitability", response_model=SoilSuitabilityResponse)
async def get_soil_crop_suitability(
    location: LocationRequest,
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get crop suitability ratings for soil at a location.
    
    Uses the unified data ingestion framework to evaluate crop suitability,
    identify limitations, and provide management considerations.
    
    Args:
        location: GPS coordinates (latitude, longitude)
        
    Returns:
        Crop suitability ratings, limitations, and management recommendations
    """
    try:
        logger.info("Evaluating soil crop suitability via ingestion framework", 
                   latitude=location.latitude, longitude=location.longitude)
        
        result = await ingestion_service.get_soil_data(
            location.latitude, longitude.longitude, "crop_suitability"
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Soil crop suitability ingestion failed: {result.error_message}"
            )
        
        suitability_data = result.data
        
        return SoilSuitabilityResponse(
            crop_suitability=suitability_data["crop_suitability"],
            limitations=suitability_data["limitations"],
            management_considerations=suitability_data["management_considerations"],
            irrigation_suitability=suitability_data["irrigation_suitability"],
            erosion_risk=suitability_data["erosion_risk"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error evaluating soil crop suitability", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error evaluating soil crop suitability: {str(e)}"
        )


@router.get("/crops/varieties/{crop_name}")
async def get_crop_varieties(
    crop_name: str, 
    region: Optional[str] = None,
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get crop variety information.
    
    Uses the unified data ingestion framework to retrieve crop variety
    data from agricultural databases.
    """
    try:
        result = await ingestion_service.get_crop_data(
            crop_name, "crop_varieties", region=region
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Crop variety data ingestion failed: {result.error_message}"
            )
        
        return result.data.get("varieties", [])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching crop variety data: {str(e)}"
        )


@router.get("/market/prices")
async def get_market_prices(
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get current agricultural commodity and input prices.
    
    Uses the unified data ingestion framework for market data with caching.
    """
    try:
        result = await ingestion_service.get_market_data("all_prices")
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Market data ingestion failed: {result.error_message}"
            )
        
        return result.data["market_data"]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching market prices: {str(e)}"
        )


# New endpoints for ingestion framework management

@router.get("/ingestion/health")
async def get_ingestion_health(
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get health status of the data ingestion framework.
    
    Returns comprehensive health information including pipeline status,
    ETL jobs, cache connectivity, and metrics.
    """
    try:
        return await ingestion_service.health_check()
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/ingestion/metrics")
async def get_ingestion_metrics(
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get metrics for the data ingestion framework.
    
    Returns pipeline and ETL metrics including success rates,
    cache hit rates, and performance statistics.
    """
    try:
        return {
            "pipeline_metrics": ingestion_service.get_pipeline_metrics(),
            "etl_metrics": ingestion_service.get_etl_metrics(),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metrics: {str(e)}"
        )


@router.get("/ingestion/jobs")
async def get_etl_jobs_status(
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get status of all ETL jobs.
    
    Returns information about scheduled jobs, their status,
    recent runs, and next scheduled execution times.
    """
    try:
        return ingestion_service.get_all_jobs_status()
    except Exception as e:
        logger.error("Failed to get job status", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.get("/ingestion/jobs/{job_id}")
async def get_etl_job_status(
    job_id: str,
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get status of a specific ETL job.
    
    Returns detailed information about the job including
    recent runs, configuration, and next execution time.
    """
    try:
        status = ingestion_service.get_job_status(job_id)
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get job status", job_id=job_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.post("/ingestion/jobs/{job_id}/run")
async def run_etl_job(
    job_id: str,
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Manually trigger an ETL job to run immediately.
    
    Executes the specified job outside of its normal schedule.
    Returns the job run result.
    """
    try:
        job_run = await ingestion_service.run_etl_job(job_id)
        return {
            "job_id": job_id,
            "run_id": job_run.run_id,
            "status": job_run.status.value,
            "start_time": job_run.start_time.isoformat(),
            "end_time": job_run.end_time.isoformat() if job_run.end_time else None,
            "duration_seconds": job_run.duration_seconds,
            "error_message": job_run.error_message,
            "success": job_run.status.value == "success"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error("Failed to run job", job_id=job_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run job: {str(e)}"
        )


@router.post("/ingestion/jobs/{job_id}/enable")
async def enable_etl_job(
    job_id: str,
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Enable an ETL job for scheduled execution.
    
    Enables the job and adds it to the scheduler if it has
    a valid schedule configuration.
    """
    try:
        ingestion_service.enable_etl_job(job_id)
        return {"job_id": job_id, "enabled": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to enable job", job_id=job_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enable job: {str(e)}"
        )


@router.post("/ingestion/jobs/{job_id}/disable")
async def disable_etl_job(
    job_id: str,
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Disable an ETL job from scheduled execution.
    
    Disables the job and removes it from the scheduler.
    Currently running instances will complete normally.
    """
    try:
        ingestion_service.disable_etl_job(job_id)
        return {"job_id": job_id, "enabled": False}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to disable job", job_id=job_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to disable job: {str(e)}"
        )


@router.post("/ingestion/cache/refresh")
async def refresh_cache(
    source_name: Optional[str] = None,
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Refresh cached data for a specific source or all sources.
    
    Clears cached data to force fresh data retrieval on next request.
    Use with caution as this may impact performance temporarily.
    """
    try:
        await ingestion_service.refresh_cache(source_name)
        return {
            "cache_refreshed": True,
            "source": source_name or "all_sources",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Failed to refresh cache", source=source_name, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh cache: {str(e)}"
        )


class BatchIngestionRequest(BaseModel):
    """Request model for batch data ingestion."""
    requests: List[Dict[str, Any]] = Field(
        ..., 
        description="List of ingestion requests with source_name, operation, and params"
    )


@router.post("/ingestion/batch")
async def batch_ingest_data(
    request: BatchIngestionRequest,
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Perform batch data ingestion from multiple sources.
    
    Executes multiple data ingestion requests in parallel for improved
    performance when fetching data from multiple sources.
    """
    try:
        results = await ingestion_service.batch_ingest_data(request.requests)
        
        return {
            "batch_results": [
                {
                    "source_name": result.source_name,
                    "success": result.success,
                    "quality_score": result.quality_score,
                    "cache_hit": result.cache_hit,
                    "processing_time_ms": result.processing_time_ms,
                    "error_message": result.error_message,
                    "data_available": result.data is not None
                }
                for result in results
            ],
            "total_requests": len(results),
            "successful_requests": sum(1 for r in results if r.success),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Batch ingestion failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Batch ingestion failed: {str(e)}"
        )