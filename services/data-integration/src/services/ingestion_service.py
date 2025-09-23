"""
Data Ingestion Service

Main service that orchestrates the data ingestion framework, ETL jobs,
and provides a unified interface for agricultural data ingestion.
"""

import asyncio
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from .data_ingestion_framework import (
    DataIngestionPipeline, 
    CacheManager, 
    AgriculturalDataValidator,
    DataSourceConfig,
    DataSourceType,
    IngestionResult
)
from .etl_orchestrator import ETLOrchestrator, ETLJobConfig, JobPriority
from .data_source_adapters import (
    WeatherServiceAdapter,
    SoilServiceAdapter,
    CropDatabaseAdapter,
    MarketDataAdapter
)

logger = structlog.get_logger(__name__)


class DataIngestionService:
    """Main data ingestion service for AFAS."""
    
    def __init__(self, redis_url: str = None):
        # Initialize components
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.cache_manager = CacheManager(self.redis_url)
        self.validator = AgriculturalDataValidator()
        self.pipeline = DataIngestionPipeline(self.cache_manager, self.validator)
        self.orchestrator = ETLOrchestrator(self.pipeline)
        
        # Initialize adapters
        self.weather_adapter = WeatherServiceAdapter()
        self.soil_adapter = SoilServiceAdapter()
        self.crop_adapter = CropDatabaseAdapter()
        self.market_adapter = MarketDataAdapter()
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize the data ingestion service."""
        if self.initialized:
            return
        
        try:
            # Connect to cache
            await self.cache_manager.connect()
            
            # Register data sources
            await self._register_data_sources()
            
            # Register ETL jobs
            await self._register_etl_jobs()
            
            # Start ETL scheduler
            await self.orchestrator.start_scheduler()
            
            self.initialized = True
            logger.info("Data ingestion service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize data ingestion service", error=str(e))
            raise
    
    async def _register_data_sources(self):
        """Register all data sources with the ingestion pipeline."""
        
        # Weather service
        weather_config = DataSourceConfig(
            name="weather_service",
            source_type=DataSourceType.WEATHER,
            base_url="https://api.weather.gov",
            rate_limit_per_minute=60,
            timeout_seconds=30,
            retry_attempts=3,
            cache_ttl_seconds=1800,  # 30 minutes for weather data
            quality_threshold=0.7,
            enabled=True
        )
        self.pipeline.register_data_source(weather_config, self.weather_adapter.handle_operation)
        
        # Soil service
        soil_config = DataSourceConfig(
            name="soil_service",
            source_type=DataSourceType.SOIL,
            base_url="https://sdmdataaccess.sc.egov.usda.gov",
            rate_limit_per_minute=30,
            timeout_seconds=45,
            retry_attempts=3,
            cache_ttl_seconds=86400,  # 24 hours for soil data
            quality_threshold=0.8,
            enabled=True
        )
        self.pipeline.register_data_source(soil_config, self.soil_adapter.handle_operation)
        
        # Crop database
        crop_config = DataSourceConfig(
            name="crop_database",
            source_type=DataSourceType.CROP,
            base_url="internal",
            rate_limit_per_minute=120,
            timeout_seconds=15,
            retry_attempts=2,
            cache_ttl_seconds=43200,  # 12 hours for crop data
            quality_threshold=0.9,
            enabled=True
        )
        self.pipeline.register_data_source(crop_config, self.crop_adapter.handle_operation)
        
        # Market data
        market_config = DataSourceConfig(
            name="market_data",
            source_type=DataSourceType.MARKET,
            base_url="internal",
            rate_limit_per_minute=60,
            timeout_seconds=20,
            retry_attempts=2,
            cache_ttl_seconds=3600,  # 1 hour for market data
            quality_threshold=0.8,
            enabled=True
        )
        self.pipeline.register_data_source(market_config, self.market_adapter.handle_operation)
        
        logger.info("Registered all data sources")
    
    async def _register_etl_jobs(self):
        """Register ETL jobs for scheduled data updates."""
        
        # Weather data refresh job - every 30 minutes
        weather_job = ETLJobConfig(
            job_id="weather_refresh",
            name="Weather Data Refresh",
            description="Refresh weather data for key agricultural regions",
            source_name="weather_service",
            operation="current_weather",
            parameters={
                "latitude": 42.0308,  # Ames, Iowa as default
                "longitude": -93.6319
            },
            schedule_interval_minutes=30,
            priority=JobPriority.HIGH,
            timeout_minutes=5,
            retry_attempts=3,
            enabled=True
        )
        self.orchestrator.register_job(weather_job)
        
        # Market data refresh job - every hour
        market_job = ETLJobConfig(
            job_id="market_data_refresh",
            name="Market Data Refresh",
            description="Refresh commodity and fertilizer prices",
            source_name="market_data",
            operation="all_prices",
            parameters={},
            schedule_interval_minutes=60,
            priority=JobPriority.MEDIUM,
            timeout_minutes=3,
            retry_attempts=2,
            enabled=True
        )
        self.orchestrator.register_job(market_job)
        
        # Soil data validation job - daily at 2 AM
        soil_validation_job = ETLJobConfig(
            job_id="soil_data_validation",
            name="Soil Data Validation",
            description="Validate and refresh soil database connections",
            source_name="soil_service",
            operation="soil_characteristics",
            parameters={
                "latitude": 42.0308,  # Test location
                "longitude": -93.6319
            },
            schedule_cron="0 2 * * *",  # Daily at 2 AM
            priority=JobPriority.LOW,
            timeout_minutes=10,
            retry_attempts=2,
            enabled=True
        )
        self.orchestrator.register_job(soil_validation_job)
        
        logger.info("Registered ETL jobs")
    
    async def get_weather_data(self, latitude: float, longitude: float, 
                              operation: str = "current_weather", **kwargs) -> IngestionResult:
        """Get weather data through the ingestion pipeline."""
        params = {"latitude": latitude, "longitude": longitude, **kwargs}
        return await self.pipeline.ingest_data("weather_service", operation, **params)
    
    async def get_soil_data(self, latitude: float, longitude: float, 
                           operation: str = "soil_characteristics", **kwargs) -> IngestionResult:
        """Get soil data through the ingestion pipeline."""
        params = {"latitude": latitude, "longitude": longitude, **kwargs}
        return await self.pipeline.ingest_data("soil_service", operation, **params)
    
    async def get_crop_data(self, crop_name: str, operation: str = "crop_varieties", 
                           **kwargs) -> IngestionResult:
        """Get crop data through the ingestion pipeline."""
        params = {"crop_name": crop_name, **kwargs}
        return await self.pipeline.ingest_data("crop_database", operation, **params)
    
    async def get_market_data(self, operation: str = "all_prices", **kwargs) -> IngestionResult:
        """Get market data through the ingestion pipeline."""
        return await self.pipeline.ingest_data("market_data", operation, **kwargs)
    
    async def batch_ingest_data(self, requests: List[Dict[str, Any]]) -> List[IngestionResult]:
        """Perform batch data ingestion."""
        return await self.pipeline.batch_ingest(requests)
    
    async def refresh_cache(self, source_name: Optional[str] = None):
        """Refresh cached data."""
        await self.pipeline.refresh_cache(source_name)
    
    async def run_etl_job(self, job_id: str):
        """Manually trigger an ETL job."""
        return await self.orchestrator.run_job_now(job_id)
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get ETL job status."""
        return self.orchestrator.get_job_status(job_id)
    
    def get_all_jobs_status(self) -> Dict[str, Any]:
        """Get status for all ETL jobs."""
        return self.orchestrator.get_all_jobs_status()
    
    def enable_etl_job(self, job_id: str):
        """Enable an ETL job."""
        self.orchestrator.enable_job(job_id)
    
    def disable_etl_job(self, job_id: str):
        """Disable an ETL job."""
        self.orchestrator.disable_job(job_id)
    
    def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get ingestion pipeline metrics."""
        return self.pipeline.get_metrics()
    
    def get_etl_metrics(self) -> Dict[str, Any]:
        """Get ETL orchestrator metrics."""
        return self.orchestrator.get_metrics()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        if not self.initialized:
            return {
                "status": "unhealthy",
                "message": "Service not initialized"
            }
        
        try:
            # Check pipeline health
            pipeline_health = await self.pipeline.health_check()
            
            # Check ETL scheduler
            etl_health = {
                "scheduler_running": self.orchestrator.scheduler.running,
                "registered_jobs": len(self.orchestrator.jobs),
                "enabled_jobs": len([j for j in self.orchestrator.jobs.values() if j.enabled])
            }
            
            # Overall status
            overall_status = "healthy"
            if pipeline_health["pipeline_status"] != "healthy":
                overall_status = "degraded"
            if not etl_health["scheduler_running"]:
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "pipeline": pipeline_health,
                "etl": etl_health,
                "metrics": {
                    "pipeline": self.get_pipeline_metrics(),
                    "etl": self.get_etl_metrics()
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def process_soil_test_data(self, soil_test_data: Dict[str, Any]) -> IngestionResult:
        """
        Process manual soil test data entry.
        
        Validates soil test data, interprets results, and provides recommendations
        based on agricultural standards and regional guidelines.
        
        Args:
            soil_test_data: Dictionary containing soil test parameters
            
        Returns:
            IngestionResult with processed soil test data and recommendations
        """
        try:
            logger.info("Processing soil test data", ph=soil_test_data.get("ph"))
            
            # Generate unique test ID
            import uuid
            test_id = str(uuid.uuid4())
            
            # Validate soil test data
            validation_result = self.validator.validate_soil_test_data(soil_test_data)
            if not validation_result.is_valid:
                return IngestionResult(
                    source_name="soil_test_processor",
                    success=False,
                    error_message=f"Validation failed: {', '.join(validation_result.errors)}",
                    quality_score=0.0
                )
            
            # Interpret soil test results
            interpretation = await self._interpret_soil_test_results(soil_test_data)
            
            # Generate recommendations
            recommendations = await self._generate_soil_recommendations(soil_test_data, interpretation)
            
            # Calculate confidence score based on data completeness
            confidence_score = self._calculate_soil_test_confidence(soil_test_data)
            
            processed_data = {
                "test_id": test_id,
                "interpretation": interpretation,
                "recommendations": recommendations,
                "confidence_score": confidence_score,
                "validation_warnings": validation_result.warnings
            }
            
            return IngestionResult(
                source_name="soil_test_processor",
                success=True,
                data=processed_data,
                quality_score=confidence_score,
                processing_time_ms=0,  # Will be set by pipeline
                cache_hit=False
            )
            
        except Exception as e:
            logger.error("Error processing soil test data", error=str(e))
            return IngestionResult(
                source_name="soil_test_processor",
                success=False,
                error_message=str(e),
                quality_score=0.0
            )
    
    async def parse_soil_test_report(self, extracted_text: str, filename: str = None, 
                                   field_id: str = None) -> IngestionResult:
        """
        Parse soil test report from extracted text.
        
        Uses text parsing and pattern matching to extract soil test data
        from laboratory reports.
        
        Args:
            extracted_text: Text extracted from uploaded report
            filename: Original filename for reference
            field_id: Optional field ID to associate with test
            
        Returns:
            IngestionResult with parsed soil test data
        """
        try:
            logger.info("Parsing soil test report", filename=filename)
            
            # Parse soil test data from text
            parsed_data = await self._parse_soil_test_text(extracted_text)
            
            if not parsed_data:
                return IngestionResult(
                    source_name="soil_test_parser",
                    success=False,
                    error_message="Could not extract soil test data from the provided text",
                    quality_score=0.0
                )
            
            # Add metadata
            parsed_data["field_id"] = field_id
            parsed_data["source_filename"] = filename
            parsed_data["extraction_method"] = "text_parsing"
            
            # Process the parsed data through normal soil test processing
            return await self.process_soil_test_data(parsed_data)
            
        except Exception as e:
            logger.error("Error parsing soil test report", filename=filename, error=str(e))
            return IngestionResult(
                source_name="soil_test_parser",
                success=False,
                error_message=str(e),
                quality_score=0.0
            )
    
    async def interpret_soil_test(self, soil_data: Dict[str, Any]) -> IngestionResult:
        """
        Interpret soil test results and provide recommendations.
        
        Provides comprehensive interpretation of soil test results including
        nutrient status, limiting factors, and management recommendations.
        
        Args:
            soil_data: Dictionary containing soil test parameters
            
        Returns:
            IngestionResult with interpretation and recommendations
        """
        try:
            logger.info("Interpreting soil test", ph=soil_data.get("ph"))
            
            # Interpret results
            interpretation = await self._interpret_soil_test_results(soil_data)
            
            # Assess nutrient status
            nutrient_status = self._assess_nutrient_status(soil_data)
            
            # Identify limiting factors
            limiting_factors = self._identify_limiting_factors(soil_data, nutrient_status)
            
            # Generate recommendations
            recommendations = await self._generate_detailed_recommendations(
                soil_data, nutrient_status, limiting_factors
            )
            
            # Calculate confidence
            confidence_score = self._calculate_soil_test_confidence(soil_data)
            
            # Agricultural sources
            agricultural_sources = [
                "Iowa State University Extension PM 1688",
                "USDA-NRCS Soil Survey",
                "Tri-State Fertilizer Recommendations"
            ]
            
            interpretation_data = {
                "overall_rating": interpretation["overall_rating"],
                "limiting_factors": limiting_factors,
                "nutrient_status": nutrient_status,
                "recommendations": recommendations,
                "confidence_score": confidence_score,
                "agricultural_sources": agricultural_sources
            }
            
            return IngestionResult(
                source_name="soil_test_interpreter",
                success=True,
                data=interpretation_data,
                quality_score=confidence_score,
                processing_time_ms=0,
                cache_hit=False
            )
            
        except Exception as e:
            logger.error("Error interpreting soil test", error=str(e))
            return IngestionResult(
                source_name="soil_test_interpreter",
                success=False,
                error_message=str(e),
                quality_score=0.0
            )
    
    async def _interpret_soil_test_results(self, soil_data: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret soil test results and provide overall assessment."""
        ph = soil_data.get("ph", 7.0)
        om = soil_data.get("organic_matter_percent", 0)
        p = soil_data.get("phosphorus_ppm", 0)
        k = soil_data.get("potassium_ppm", 0)
        
        # Calculate overall rating
        score = 0
        factors = 0
        
        # pH scoring
        if 6.0 <= ph <= 7.0:
            score += 4
        elif 5.5 <= ph <= 7.5:
            score += 3
        elif 5.0 <= ph <= 8.0:
            score += 2
        else:
            score += 1
        factors += 1
        
        # Organic matter scoring
        if om >= 4.0:
            score += 4
        elif om >= 3.0:
            score += 3
        elif om >= 2.0:
            score += 2
        else:
            score += 1
        factors += 1
        
        # Phosphorus scoring
        if p and 20 <= p <= 40:
            score += 4
        elif p and 15 <= p <= 50:
            score += 3
        elif p and 10 <= p <= 60:
            score += 2
        else:
            score += 1
        factors += 1
        
        # Potassium scoring
        if k and 150 <= k <= 250:
            score += 4
        elif k and 100 <= k <= 300:
            score += 3
        elif k and 75 <= k <= 350:
            score += 2
        else:
            score += 1
        factors += 1
        
        avg_score = score / factors if factors > 0 else 2.5
        
        if avg_score >= 3.5:
            overall_rating = "excellent"
        elif avg_score >= 2.5:
            overall_rating = "good"
        elif avg_score >= 1.5:
            overall_rating = "fair"
        else:
            overall_rating = "poor"
        
        return {
            "overall_rating": overall_rating,
            "score": avg_score,
            "factors_assessed": factors
        }
    
    def _assess_nutrient_status(self, soil_data: Dict[str, Any]) -> Dict[str, str]:
        """Assess the status of individual nutrients."""
        status = {}
        
        # pH status
        ph = soil_data.get("ph")
        if ph:
            if ph < 5.5:
                status["ph"] = "low"
            elif ph > 7.5:
                status["ph"] = "high"
            else:
                status["ph"] = "adequate"
        
        # Organic matter status
        om = soil_data.get("organic_matter_percent")
        if om:
            if om < 2.0:
                status["organic_matter"] = "low"
            elif om < 3.0:
                status["organic_matter"] = "moderate"
            else:
                status["organic_matter"] = "adequate"
        
        # Phosphorus status
        p = soil_data.get("phosphorus_ppm")
        if p:
            if p < 15:
                status["phosphorus"] = "deficient"
            elif p < 20:
                status["phosphorus"] = "low"
            elif p <= 40:
                status["phosphorus"] = "adequate"
            else:
                status["phosphorus"] = "high"
        
        # Potassium status
        k = soil_data.get("potassium_ppm")
        if k:
            if k < 100:
                status["potassium"] = "deficient"
            elif k < 150:
                status["potassium"] = "low"
            elif k <= 250:
                status["potassium"] = "adequate"
            else:
                status["potassium"] = "high"
        
        return status
    
    def _identify_limiting_factors(self, soil_data: Dict[str, Any], 
                                 nutrient_status: Dict[str, str]) -> List[str]:
        """Identify factors limiting crop production."""
        limiting_factors = []
        
        # Check pH
        if nutrient_status.get("ph") == "low":
            limiting_factors.append("Acidic soil (pH too low)")
        elif nutrient_status.get("ph") == "high":
            limiting_factors.append("Alkaline soil (pH too high)")
        
        # Check organic matter
        if nutrient_status.get("organic_matter") == "low":
            limiting_factors.append("Low organic matter")
        
        # Check nutrients
        if nutrient_status.get("phosphorus") in ["deficient", "low"]:
            limiting_factors.append("Low phosphorus levels")
        
        if nutrient_status.get("potassium") in ["deficient", "low"]:
            limiting_factors.append("Low potassium levels")
        
        # Check soil texture issues
        soil_texture = soil_data.get("soil_texture")
        if soil_texture == "sand":
            limiting_factors.append("Sandy soil - low water and nutrient retention")
        elif soil_texture == "clay":
            limiting_factors.append("Heavy clay soil - potential drainage issues")
        
        return limiting_factors
    
    async def _generate_soil_recommendations(self, soil_data: Dict[str, Any], 
                                           interpretation: Dict[str, Any]) -> List[str]:
        """Generate basic soil management recommendations."""
        recommendations = []
        
        ph = soil_data.get("ph", 7.0)
        om = soil_data.get("organic_matter_percent", 0)
        p = soil_data.get("phosphorus_ppm", 0)
        k = soil_data.get("potassium_ppm", 0)
        
        # pH recommendations
        if ph < 6.0:
            lime_rate = round((6.5 - ph) * 2, 1)
            recommendations.append(f"Apply {lime_rate} tons/acre of agricultural limestone to raise pH")
        elif ph > 7.5:
            recommendations.append("Consider sulfur application to lower pH if needed for specific crops")
        
        # Organic matter recommendations
        if om < 3.0:
            recommendations.append("Increase organic matter through cover crops, compost, or manure application")
        
        # Phosphorus recommendations
        if p and p < 15:
            recommendations.append("Apply 40-60 lbs P2O5/acre to build phosphorus levels")
        elif p and p < 20:
            recommendations.append("Apply 25-40 lbs P2O5/acre for phosphorus maintenance")
        
        # Potassium recommendations
        if k and k < 100:
            recommendations.append("Apply 80-120 lbs K2O/acre to build potassium levels")
        elif k and k < 150:
            recommendations.append("Apply 40-80 lbs K2O/acre for potassium maintenance")
        
        # General recommendations
        recommendations.append("Conduct soil tests every 2-3 years to monitor nutrient levels")
        
        return recommendations
    
    async def _generate_detailed_recommendations(self, soil_data: Dict[str, Any],
                                               nutrient_status: Dict[str, str],
                                               limiting_factors: List[str]) -> List[Dict[str, Any]]:
        """Generate detailed recommendations with priorities and costs."""
        recommendations = []
        
        ph = soil_data.get("ph", 7.0)
        om = soil_data.get("organic_matter_percent", 0)
        p = soil_data.get("phosphorus_ppm", 0)
        k = soil_data.get("potassium_ppm", 0)
        
        # pH correction (high priority)
        if ph < 6.0:
            lime_rate = round((6.5 - ph) * 2, 1)
            recommendations.append({
                "practice": "Lime Application",
                "priority": "high",
                "description": f"Apply {lime_rate} tons/acre of agricultural limestone",
                "timing": "Fall application preferred",
                "cost_per_acre": "$45-65",
                "expected_benefit": "Improved nutrient availability and pH balance"
            })
        
        # Organic matter improvement (high priority if low)
        if om < 3.0:
            recommendations.append({
                "practice": "Organic Matter Enhancement",
                "priority": "high" if om < 2.0 else "medium",
                "description": "Use cover crops, compost, or manure to increase organic matter",
                "timing": "Fall seeding for cover crops",
                "cost_per_acre": "$25-50",
                "expected_benefit": "Improved soil structure and water retention"
            })
        
        # Phosphorus management
        if p and p < 15:
            recommendations.append({
                "practice": "Phosphorus Application",
                "priority": "medium",
                "description": "Apply 40-60 lbs P2O5/acre to build soil P levels",
                "timing": "Fall or spring application",
                "cost_per_acre": "$30-45",
                "expected_benefit": "Enhanced root development and energy transfer"
            })
        
        # Potassium management
        if k and k < 100:
            recommendations.append({
                "practice": "Potassium Application",
                "priority": "medium",
                "description": "Apply 80-120 lbs K2O/acre to build soil K levels",
                "timing": "Fall application preferred",
                "cost_per_acre": "$35-55",
                "expected_benefit": "Improved disease resistance and water use efficiency"
            })
        
        # Soil testing (always recommend)
        recommendations.append({
            "practice": "Regular Soil Testing",
            "priority": "low",
            "description": "Test soil every 2-3 years to monitor changes",
            "timing": "Every 2-3 years",
            "cost_per_acre": "$15-25",
            "expected_benefit": "Data-driven nutrient management decisions"
        })
        
        return recommendations
    
    async def _parse_soil_test_text(self, text: str) -> Dict[str, Any]:
        """Parse soil test data from extracted text using pattern matching."""
        import re
        
        parsed_data = {}
        
        # Common patterns for soil test reports
        patterns = {
            "ph": [
                r"pH[:\s]+(\d+\.?\d*)",
                r"Soil pH[:\s]+(\d+\.?\d*)",
                r"pH\s*=\s*(\d+\.?\d*)"
            ],
            "organic_matter_percent": [
                r"Organic Matter[:\s]+(\d+\.?\d*)%?",
                r"O\.?M\.?[:\s]+(\d+\.?\d*)%?",
                r"OM[:\s]+(\d+\.?\d*)%?"
            ],
            "phosphorus_ppm": [
                r"Phosphorus[:\s]+(\d+\.?\d*)\s*ppm",
                r"P[:\s]+(\d+\.?\d*)\s*ppm",
                r"P2O5[:\s]+(\d+\.?\d*)"
            ],
            "potassium_ppm": [
                r"Potassium[:\s]+(\d+\.?\d*)\s*ppm",
                r"K[:\s]+(\d+\.?\d*)\s*ppm",
                r"K2O[:\s]+(\d+\.?\d*)"
            ],
            "cec_meq_per_100g": [
                r"CEC[:\s]+(\d+\.?\d*)",
                r"Cation Exchange Capacity[:\s]+(\d+\.?\d*)"
            ]
        }
        
        # Extract values using patterns
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        parsed_data[field] = float(match.group(1))
                        break
                    except ValueError:
                        continue
        
        # Extract test date
        date_patterns = [
            r"Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"Test Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    from datetime import datetime
                    date_str = match.group(1)
                    # Try different date formats
                    for fmt in ["%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y"]:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt).date()
                            parsed_data["test_date"] = parsed_date.isoformat()
                            break
                        except ValueError:
                            continue
                    break
                except:
                    continue
        
        # Extract lab name
        lab_patterns = [
            r"Laboratory[:\s]+([^\n\r]+)",
            r"Lab[:\s]+([^\n\r]+)",
            r"Tested by[:\s]+([^\n\r]+)"
        ]
        
        for pattern in lab_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parsed_data["lab_name"] = match.group(1).strip()
                break
        
        return parsed_data if parsed_data else None
    
    def _calculate_soil_test_confidence(self, soil_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data completeness and quality."""
        confidence = 0.5  # Base confidence
        
        # Required parameters
        if soil_data.get("ph"):
            confidence += 0.2
        
        # Important parameters
        if soil_data.get("organic_matter_percent"):
            confidence += 0.1
        if soil_data.get("phosphorus_ppm"):
            confidence += 0.1
        if soil_data.get("potassium_ppm"):
            confidence += 0.1
        
        # Additional parameters
        if soil_data.get("cec_meq_per_100g"):
            confidence += 0.05
        if soil_data.get("soil_texture"):
            confidence += 0.05
        
        # Test recency (if test_date provided)
        test_date = soil_data.get("test_date")
        if test_date:
            try:
                from datetime import datetime, date
                if isinstance(test_date, str):
                    test_date = datetime.fromisoformat(test_date).date()
                
                days_old = (date.today() - test_date).days
                if days_old <= 365:  # Less than 1 year
                    confidence += 0.05
                elif days_old <= 730:  # Less than 2 years
                    confidence += 0.03
                elif days_old > 1095:  # More than 3 years
                    confidence -= 0.05
            except:
                pass
        
        return min(confidence, 1.0)

    async def shutdown(self):
        """Shutdown the data ingestion service."""
        try:
            # Stop ETL scheduler
            await self.orchestrator.stop_scheduler()
            
            # Close adapters
            await self.weather_adapter.close()
            
            # Close cache connection
            await self.cache_manager.close()
            
            self.initialized = False
            logger.info("Data ingestion service shutdown complete")
            
        except Exception as e:
            logger.error("Error during shutdown", error=str(e))
            raise


# Global service instance
_ingestion_service: Optional[DataIngestionService] = None


async def get_ingestion_service() -> DataIngestionService:
    """Get or create the global ingestion service instance."""
    global _ingestion_service
    
    if _ingestion_service is None:
        _ingestion_service = DataIngestionService()
        await _ingestion_service.initialize()
    
    return _ingestion_service


async def shutdown_ingestion_service():
    """Shutdown the global ingestion service instance."""
    global _ingestion_service
    
    if _ingestion_service:
        await _ingestion_service.shutdown()
        _ingestion_service = None