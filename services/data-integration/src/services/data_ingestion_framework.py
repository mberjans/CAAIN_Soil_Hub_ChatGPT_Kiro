"""
Data Ingestion Service Framework

Provides a unified framework for ingesting, validating, normalizing, and caching
agricultural data from multiple external sources.
"""

import asyncio
import redis.asyncio as aioredis
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Type, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib
import structlog
from pydantic import BaseModel, ValidationError
import traceback

# Import the enhanced validation pipeline
from .data_validation_pipeline import DataValidationPipeline, ValidationSeverity

logger = structlog.get_logger(__name__)


class DataSourceType(Enum):
    """Types of agricultural data sources."""
    WEATHER = "weather"
    SOIL = "soil"
    CROP = "crop"
    MARKET = "market"
    GOVERNMENT = "government"
    SATELLITE = "satellite"


class DataQuality(Enum):
    """Data quality levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class DataSourceConfig:
    """Configuration for a data source."""
    name: str
    source_type: DataSourceType
    base_url: str
    api_key_env_var: Optional[str] = None
    rate_limit_per_minute: int = 60
    timeout_seconds: int = 30
    retry_attempts: int = 3
    cache_ttl_seconds: int = 3600
    quality_threshold: float = 0.8
    enabled: bool = True


@dataclass
class IngestionResult:
    """Result of a data ingestion operation."""
    source_name: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    quality_score: float = 0.0
    timestamp: datetime = None
    cache_hit: bool = False
    processing_time_ms: float = 0.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    quality_score: float
    normalized_data: Optional[Dict[str, Any]] = None


class DataValidator(ABC):
    """Abstract base class for data validators."""
    
    @abstractmethod
    async def validate(self, data: Dict[str, Any], source_config: DataSourceConfig) -> ValidationResult:
        """Validate and normalize data from a source."""
        pass


class AgriculturalDataValidator(DataValidator):
    """Validator for agricultural data with domain-specific rules."""
    
    async def validate(self, data: Dict[str, Any], source_config: DataSourceConfig) -> ValidationResult:
        """Validate agricultural data with comprehensive checks."""
        errors = []
        warnings = []
        quality_score = 1.0
        normalized_data = data.copy()
        
        try:
            # Source-specific validation
            if source_config.source_type == DataSourceType.WEATHER:
                validation_result = await self._validate_weather_data(normalized_data)
            elif source_config.source_type == DataSourceType.SOIL:
                validation_result = await self._validate_soil_data(normalized_data)
            elif source_config.source_type == DataSourceType.CROP:
                validation_result = await self._validate_crop_data(normalized_data)
            elif source_config.source_type == DataSourceType.MARKET:
                validation_result = await self._validate_market_data(normalized_data)
            else:
                validation_result = await self._validate_generic_data(normalized_data)
            
            errors.extend(validation_result.errors)
            warnings.extend(validation_result.warnings)
            quality_score = min(quality_score, validation_result.quality_score)
            if validation_result.normalized_data:
                normalized_data = validation_result.normalized_data
            
            # General data quality checks
            general_validation = await self._validate_general_quality(normalized_data)
            errors.extend(general_validation.errors)
            warnings.extend(general_validation.warnings)
            quality_score = min(quality_score, general_validation.quality_score)
            
            is_valid = len(errors) == 0 and quality_score >= source_config.quality_threshold
            
            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                quality_score=quality_score,
                normalized_data=normalized_data
            )
            
        except Exception as e:
            logger.error("Validation error", error=str(e), source=source_config.name)
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation exception: {str(e)}"],
                warnings=[],
                quality_score=0.0
            )
    
    async def _validate_weather_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate weather data."""
        errors = []
        warnings = []
        quality_score = 1.0
        
        # Temperature validation
        if "temperature_f" in data:
            temp = data["temperature_f"]
            if not isinstance(temp, (int, float)):
                errors.append("Temperature must be numeric")
            elif temp < -50 or temp > 130:
                errors.append(f"Temperature {temp}°F is outside reasonable range (-50°F to 130°F)")
            elif temp < 0 or temp > 110:
                warnings.append(f"Temperature {temp}°F is unusual for agricultural areas")
                quality_score *= 0.9
        
        # Humidity validation
        if "humidity_percent" in data:
            humidity = data["humidity_percent"]
            if not isinstance(humidity, (int, float)):
                errors.append("Humidity must be numeric")
            elif humidity < 0 or humidity > 100:
                errors.append(f"Humidity {humidity}% is outside valid range (0-100%)")
        
        # Precipitation validation
        if "precipitation_inches" in data:
            precip = data["precipitation_inches"]
            if not isinstance(precip, (int, float)):
                errors.append("Precipitation must be numeric")
            elif precip < 0:
                errors.append("Precipitation cannot be negative")
            elif precip > 10:
                warnings.append(f"Very high precipitation {precip} inches reported")
                quality_score *= 0.95
        
        # Wind speed validation
        if "wind_speed_mph" in data:
            wind = data["wind_speed_mph"]
            if not isinstance(wind, (int, float)):
                errors.append("Wind speed must be numeric")
            elif wind < 0:
                errors.append("Wind speed cannot be negative")
            elif wind > 100:
                warnings.append(f"Very high wind speed {wind} mph reported")
                quality_score *= 0.9
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            quality_score=quality_score,
            normalized_data=data
        )
    
    async def _validate_soil_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate soil data."""
        errors = []
        warnings = []
        quality_score = 1.0
        
        # pH validation
        if "ph" in data or "typical_ph_range" in data:
            ph_value = data.get("ph")
            ph_range = data.get("typical_ph_range", {})
            
            if ph_value is not None:
                if not isinstance(ph_value, (int, float)):
                    errors.append("pH must be numeric")
                elif ph_value < 3.0 or ph_value > 10.0:
                    errors.append(f"pH {ph_value} is outside reasonable range (3.0-10.0)")
                elif ph_value < 4.0 or ph_value > 9.0:
                    warnings.append(f"pH {ph_value} is extreme for agricultural soils")
                    quality_score *= 0.9
            
            if ph_range:
                ph_min = ph_range.get("min")
                ph_max = ph_range.get("max")
                if ph_min is not None and ph_max is not None:
                    if ph_min >= ph_max:
                        errors.append("pH range minimum must be less than maximum")
        
        # Organic matter validation
        if "organic_matter_percent" in data or "organic_matter_typical" in data:
            om = data.get("organic_matter_percent") or data.get("organic_matter_typical")
            if om is not None:
                if not isinstance(om, (int, float)):
                    errors.append("Organic matter must be numeric")
                elif om < 0 or om > 20:
                    errors.append(f"Organic matter {om}% is outside reasonable range (0-20%)")
                elif om > 15:
                    warnings.append(f"Very high organic matter {om}% reported")
                    quality_score *= 0.95
        
        # Nutrient validation
        for nutrient in ["phosphorus_ppm", "potassium_ppm", "nitrogen_typical"]:
            if nutrient in data:
                value = data[nutrient]
                if not isinstance(value, (int, float)):
                    errors.append(f"{nutrient} must be numeric")
                elif value < 0:
                    errors.append(f"{nutrient} cannot be negative")
                elif value > 1000:  # Very high nutrient levels
                    warnings.append(f"Very high {nutrient} value {value} reported")
                    quality_score *= 0.95
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            quality_score=quality_score,
            normalized_data=data
        )
    
    async def _validate_crop_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate crop data."""
        errors = []
        warnings = []
        quality_score = 1.0
        
        # Yield validation
        if "yield_potential" in data:
            yield_val = data["yield_potential"]
            if not isinstance(yield_val, (int, float)):
                errors.append("Yield potential must be numeric")
            elif yield_val <= 0:
                errors.append("Yield potential must be positive")
            elif yield_val > 500:  # Very high yield
                warnings.append(f"Very high yield potential {yield_val} reported")
                quality_score *= 0.95
        
        # Maturity validation
        if "maturity_days" in data:
            maturity = data["maturity_days"]
            if not isinstance(maturity, (int, float)):
                errors.append("Maturity days must be numeric")
            elif maturity <= 0 or maturity > 365:
                errors.append(f"Maturity days {maturity} is outside reasonable range (1-365)")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            quality_score=quality_score,
            normalized_data=data
        )
    
    async def _validate_market_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate market/pricing data."""
        errors = []
        warnings = []
        quality_score = 1.0
        
        # Price validation
        for key, value in data.items():
            if "price" in key.lower() or "cost" in key.lower():
                if not isinstance(value, (int, float)):
                    errors.append(f"{key} must be numeric")
                elif value < 0:
                    errors.append(f"{key} cannot be negative")
                elif value == 0:
                    warnings.append(f"Zero price for {key} may indicate data issue")
                    quality_score *= 0.9
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            quality_score=quality_score,
            normalized_data=data
        )
    
    async def _validate_generic_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate generic data."""
        errors = []
        warnings = []
        quality_score = 1.0
        
        # Basic structure validation
        if not isinstance(data, dict):
            errors.append("Data must be a dictionary")
        elif len(data) == 0:
            warnings.append("Empty data received")
            quality_score *= 0.5
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            quality_score=quality_score,
            normalized_data=data
        )
    
    async def _validate_general_quality(self, data: Dict[str, Any]) -> ValidationResult:
        """General data quality validation."""
        errors = []
        warnings = []
        quality_score = 1.0
        
        # Check for null/missing critical values
        null_count = sum(1 for v in data.values() if v is None)
        if null_count > len(data) * 0.3:  # More than 30% null values
            warnings.append(f"High proportion of null values ({null_count}/{len(data)})")
            quality_score *= 0.8
        
        # Check for timestamp freshness
        if "timestamp" in data:
            try:
                timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
                age_hours = (datetime.utcnow() - timestamp.replace(tzinfo=None)).total_seconds() / 3600
                if age_hours > 24:
                    warnings.append(f"Data is {age_hours:.1f} hours old")
                    quality_score *= max(0.5, 1.0 - (age_hours - 24) / 168)  # Degrade over a week
            except (ValueError, AttributeError):
                warnings.append("Invalid timestamp format")
                quality_score *= 0.9
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            quality_score=quality_score
        )


class CacheManager:
    """Redis-based cache manager for agricultural data."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = aioredis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache."""
        if not self.redis_client:
            return None
        
        try:
            cached_data = await self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning("Cache get error", key=key, error=str(e))
        
        return None
    
    async def set(self, key: str, data: Dict[str, Any], ttl_seconds: int = 3600):
        """Set data in cache."""
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.setex(key, ttl_seconds, json.dumps(data, default=str))
            return True
        except Exception as e:
            logger.warning("Cache set error", key=key, error=str(e))
            return False
    
    async def delete(self, key: str):
        """Delete data from cache."""
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning("Cache delete error", key=key, error=str(e))
            return False
    
    async def clear_pattern(self, pattern: str):
        """Clear cache entries matching pattern."""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning("Cache clear pattern error", pattern=pattern, error=str(e))
            return 0
    
    def generate_cache_key(self, source_name: str, operation: str, **params) -> str:
        """Generate a consistent cache key."""
        # Create a hash of the parameters for consistent key generation
        param_str = json.dumps(params, sort_keys=True, default=str)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
        return f"afas:data:{source_name}:{operation}:{param_hash}"
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()


class DataIngestionPipeline:
    """Main data ingestion pipeline orchestrator."""
    
    def __init__(self, cache_manager: Union[CacheManager, 'EnhancedCacheManager'], validator: DataValidator, 
                 enhanced_validator: DataValidationPipeline = None):
        self.cache_manager = cache_manager
        self.validator = validator
        self.enhanced_validator = enhanced_validator or DataValidationPipeline()
        self.data_sources: Dict[str, DataSourceConfig] = {}
        self.ingestion_handlers: Dict[str, Callable] = {}
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "cache_hits": 0,
            "validation_failures": 0,
            "cleaning_actions": 0,
            "source_failures": {}
        }
        
        # Check if we're using enhanced cache manager
        self.use_enhanced_cache = hasattr(cache_manager, 'get_comprehensive_stats')
    
    def register_data_source(self, config: DataSourceConfig, handler: Callable):
        """Register a data source with its ingestion handler."""
        self.data_sources[config.name] = config
        self.ingestion_handlers[config.name] = handler
        logger.info("Registered data source", source=config.name, type=config.source_type.value)
    
    async def ingest_data(self, source_name: str, operation: str, **params) -> IngestionResult:
        """Ingest data from a specific source with caching and validation."""
        start_time = datetime.utcnow()
        self.metrics["total_requests"] += 1
        
        # Check if source is registered and enabled
        if source_name not in self.data_sources:
            return IngestionResult(
                source_name=source_name,
                success=False,
                error_message=f"Data source '{source_name}' not registered"
            )
        
        source_config = self.data_sources[source_name]
        if not source_config.enabled:
            return IngestionResult(
                source_name=source_name,
                success=False,
                error_message=f"Data source '{source_name}' is disabled"
            )
        
        # Generate cache key
        if self.use_enhanced_cache:
            cache_key = self.cache_manager.generate_cache_key(source_name, operation, **params)
            # Determine data type for enhanced cache
            data_type = self._get_data_type_for_source(source_config.source_type)
        else:
            cache_key = self.cache_manager.generate_cache_key(source_name, operation, **params)
        
        # Try to get from cache first
        if self.use_enhanced_cache:
            cached_data = await self.cache_manager.get(cache_key, data_type)
        else:
            cached_data = await self.cache_manager.get(cache_key)
            
        if cached_data:
            self.metrics["cache_hits"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return IngestionResult(
                source_name=source_name,
                success=True,
                data=cached_data,
                quality_score=cached_data.get("_quality_score", 1.0),
                cache_hit=True,
                processing_time_ms=processing_time
            )
        
        # Get handler and execute ingestion
        handler = self.ingestion_handlers.get(source_name)
        if not handler:
            return IngestionResult(
                source_name=source_name,
                success=False,
                error_message=f"No handler registered for source '{source_name}'"
            )
        
        try:
            # Execute the ingestion handler
            raw_data = await handler(operation, **params)
            
            if raw_data is None:
                raise Exception("Handler returned no data")
            
            # First pass: Basic validation
            validation_result = await self.validator.validate(raw_data, source_config)
            
            if not validation_result.is_valid:
                self.metrics["validation_failures"] += 1
                return IngestionResult(
                    source_name=source_name,
                    success=False,
                    error_message=f"Basic validation failed: {'; '.join(validation_result.errors)}",
                    quality_score=validation_result.quality_score
                )
            
            # Second pass: Enhanced cleaning and validation
            data_type = self._determine_data_type(source_config.source_type)
            if data_type:
                try:
                    cleaning_result = await self.enhanced_validator.validate_and_clean(
                        validation_result.normalized_data, 
                        data_type,
                        context={"source_name": source_name, "operation": operation, **params}
                    )
                    
                    # Update metrics
                    if cleaning_result.actions_taken:
                        self.metrics["cleaning_actions"] += len(cleaning_result.actions_taken)
                    
                    # Use cleaned data and update quality score
                    final_data = cleaning_result.cleaned_data.copy()
                    final_quality_score = min(validation_result.quality_score, cleaning_result.quality_score)
                    
                    # Log cleaning actions if any
                    if cleaning_result.actions_taken:
                        logger.info("Data cleaning performed", 
                                  source=source_name, 
                                  actions=cleaning_result.actions_taken,
                                  issues_found=len(cleaning_result.issues_found))
                    
                    # Log critical issues
                    critical_issues = [issue for issue in cleaning_result.issues_found 
                                     if issue.severity == ValidationSeverity.CRITICAL]
                    if critical_issues:
                        logger.warning("Critical data quality issues found",
                                     source=source_name,
                                     critical_issues=[issue.message for issue in critical_issues])
                    
                except Exception as e:
                    logger.warning("Enhanced validation failed, using basic validation", 
                                 source=source_name, error=str(e))
                    final_data = validation_result.normalized_data.copy()
                    final_quality_score = validation_result.quality_score
            else:
                final_data = validation_result.normalized_data.copy()
                final_quality_score = validation_result.quality_score
            
            # Add metadata to data for caching
            final_data["_quality_score"] = final_quality_score
            final_data["_ingestion_timestamp"] = datetime.utcnow().isoformat()
            final_data["_validation_metadata"] = {
                "basic_validation": True,
                "enhanced_cleaning": data_type is not None,
                "source_type": source_config.source_type.value
            }
            
            # Cache the validated data
            if self.use_enhanced_cache:
                await self.cache_manager.set(cache_key, final_data, data_type)
            else:
                await self.cache_manager.set(cache_key, final_data, source_config.cache_ttl_seconds)
            
            # Update metrics
            self.metrics["successful_requests"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Log warnings if any
            if validation_result.warnings:
                logger.warning("Data validation warnings", 
                             source=source_name, warnings=validation_result.warnings)
            
            return IngestionResult(
                source_name=source_name,
                success=True,
                data=final_data,
                quality_score=final_quality_score,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            # Update failure metrics
            if source_name not in self.metrics["source_failures"]:
                self.metrics["source_failures"][source_name] = 0
            self.metrics["source_failures"][source_name] += 1
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            error_msg = f"Ingestion failed: {str(e)}"
            
            logger.error("Data ingestion error", 
                        source=source_name, operation=operation, 
                        error=str(e), traceback=traceback.format_exc())
            
            return IngestionResult(
                source_name=source_name,
                success=False,
                error_message=error_msg,
                processing_time_ms=processing_time
            )
    
    async def batch_ingest(self, requests: List[Dict[str, Any]]) -> List[IngestionResult]:
        """Ingest data from multiple sources in parallel."""
        tasks = []
        
        for request in requests:
            source_name = request.get("source_name")
            operation = request.get("operation")
            params = request.get("params", {})
            
            if source_name and operation:
                task = self.ingest_data(source_name, operation, **params)
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert exceptions to error results
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    final_results.append(IngestionResult(
                        source_name=requests[i].get("source_name", "unknown"),
                        success=False,
                        error_message=f"Batch ingestion error: {str(result)}"
                    ))
                else:
                    final_results.append(result)
            
            return final_results
        
        return []
    
    def _determine_data_type(self, source_type: DataSourceType) -> Optional[str]:
        """Determine data type for enhanced validation."""
        type_mapping = {
            DataSourceType.WEATHER: "weather",
            DataSourceType.SOIL: "soil",
            DataSourceType.CROP: "crop",
            DataSourceType.MARKET: "market"
        }
        return type_mapping.get(source_type)
    
    def _get_data_type_for_source(self, source_type: DataSourceType):
        """Get DataType enum for enhanced cache manager."""
        try:
            from .enhanced_cache_manager import DataType
            type_mapping = {
                DataSourceType.WEATHER: DataType.WEATHER,
                DataSourceType.SOIL: DataType.SOIL,
                DataSourceType.CROP: DataType.CROP,
                DataSourceType.MARKET: DataType.MARKET,
                DataSourceType.GOVERNMENT: DataType.MARKET,  # Fallback
                DataSourceType.SATELLITE: DataType.CROP     # Fallback
            }
            return type_mapping.get(source_type, DataType.WEATHER)
        except ImportError:
            # Fallback if enhanced cache manager not available
            return None
    
    async def refresh_cache(self, source_name: Optional[str] = None):
        """Refresh cached data for a source or all sources."""
        if source_name:
            pattern = f"afas:data:{source_name}:*"
            cleared = await self.cache_manager.clear_pattern(pattern)
            logger.info("Cleared cache for source", source=source_name, keys_cleared=cleared)
        else:
            pattern = "afas:data:*"
            cleared = await self.cache_manager.clear_pattern(pattern)
            logger.info("Cleared all data cache", keys_cleared=cleared)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get ingestion pipeline metrics."""
        total = self.metrics["total_requests"]
        success_rate = (self.metrics["successful_requests"] / total * 100) if total > 0 else 0
        cache_hit_rate = (self.metrics["cache_hits"] / total * 100) if total > 0 else 0
        
        return {
            "total_requests": total,
            "successful_requests": self.metrics["successful_requests"],
            "success_rate_percent": round(success_rate, 2),
            "cache_hits": self.metrics["cache_hits"],
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "validation_failures": self.metrics["validation_failures"],
            "cleaning_actions": self.metrics["cleaning_actions"],
            "source_failures": self.metrics["source_failures"].copy(),
            "registered_sources": list(self.data_sources.keys()),
            "enabled_sources": [name for name, config in self.data_sources.items() if config.enabled],
            "enhanced_validation_metrics": self.enhanced_validator.get_validation_metrics() if self.enhanced_validator else {}
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the ingestion pipeline."""
        health_status = {
            "pipeline_status": "healthy",
            "cache_status": "unknown",
            "sources": {}
        }
        
        # Check cache connectivity
        try:
            await self.cache_manager.redis_client.ping()
            health_status["cache_status"] = "healthy"
        except Exception as e:
            health_status["cache_status"] = f"unhealthy: {str(e)}"
            health_status["pipeline_status"] = "degraded"
        
        # Check each data source
        for source_name, config in self.data_sources.items():
            source_health = {
                "enabled": config.enabled,
                "recent_failures": self.metrics["source_failures"].get(source_name, 0)
            }
            
            # Consider source unhealthy if it has many recent failures
            if source_health["recent_failures"] > 10:
                source_health["status"] = "unhealthy"
                if health_status["pipeline_status"] == "healthy":
                    health_status["pipeline_status"] = "degraded"
            else:
                source_health["status"] = "healthy"
            
            health_status["sources"][source_name] = source_health
        
        return health_status