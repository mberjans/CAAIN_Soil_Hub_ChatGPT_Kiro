# Service Patterns - Crop Variety Recommendations

## Overview

This document outlines the architectural patterns, design principles, and implementation guidelines used in the crop variety recommendations system. These patterns ensure consistency, maintainability, and scalability across all services.

## Architectural Patterns

### 1. Microservices Architecture

The system follows a microservices architecture with clear service boundaries and responsibilities.

```
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway                                  │
│                 (Load Balancer)                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Variety Recommendations                       │
│                         Service                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Crop      │  │   Climate   │  │    Soil     │  │ Market  │ │
│  │ Taxonomy    │  │    Zone     │  │   Data      │  │ Price   │ │
│  │  Service    │  │  Service    │  │  Service    │  │Service  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- Independent deployment and scaling
- Technology diversity
- Fault isolation
- Team autonomy

**Implementation Guidelines:**
- Each service has a single responsibility
- Services communicate via well-defined APIs
- No direct database sharing between services
- Each service manages its own data

### 2. Domain-Driven Design (DDD)

The system is organized around agricultural domains and business capabilities.

**Core Domains:**
- **Crop Management**: Variety selection, crop characteristics
- **Climate Analysis**: Weather data, climate zones
- **Soil Science**: Soil properties, fertility analysis
- **Market Intelligence**: Pricing, economic analysis
- **Recommendation Engine**: Decision logic, ranking algorithms

**Domain Boundaries:**
```python
# Domain Service Example
class CropVarietyDomainService:
    """Handles crop variety business logic."""
    
    def __init__(self, variety_repository: VarietyRepository):
        self.variety_repository = variety_repository
    
    async def find_suitable_varieties(
        self, 
        crop_type: CropType, 
        conditions: GrowingConditions
    ) -> List[VarietyRecommendation]:
        """Find varieties suitable for given conditions."""
        # Domain logic here
        pass
```

### 3. Repository Pattern

Data access is abstracted through repository interfaces.

```python
from abc import ABC, abstractmethod
from typing import List, Optional

class VarietyRepository(ABC):
    """Abstract repository for variety data access."""
    
    @abstractmethod
    async def find_by_crop(self, crop_id: str) -> List[Variety]:
        """Find varieties by crop type."""
        pass
    
    @abstractmethod
    async def find_by_criteria(self, criteria: SearchCriteria) -> List[Variety]:
        """Find varieties by search criteria."""
        pass
    
    @abstractmethod
    async def save(self, variety: Variety) -> Variety:
        """Save variety to repository."""
        pass

class PostgreSQLVarietyRepository(VarietyRepository):
    """PostgreSQL implementation of variety repository."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def find_by_crop(self, crop_id: str) -> List[Variety]:
        """Find varieties by crop type."""
        query = select(VarietyDB).where(VarietyDB.crop_id == crop_id)
        result = await self.db_session.execute(query)
        return [self._to_domain_model(v) for v in result.scalars().all()]
    
    def _to_domain_model(self, db_model: VarietyDB) -> Variety:
        """Convert database model to domain model."""
        return Variety(
            id=db_model.id,
            name=db_model.variety_name,
            crop_id=db_model.crop_id,
            company=db_model.company,
            maturity_days=db_model.maturity_days,
            yield_potential=YieldPotential(
                min=db_model.yield_potential_min,
                max=db_model.yield_potential_max,
                unit=db_model.yield_unit
            )
        )
```

### 4. Service Layer Pattern

Business logic is encapsulated in service classes.

```python
class VarietyRecommendationService:
    """Service for variety recommendation business logic."""
    
    def __init__(
        self,
        variety_repository: VarietyRepository,
        climate_service: ClimateService,
        soil_service: SoilService,
        ranking_algorithm: RankingAlgorithm
    ):
        self.variety_repository = variety_repository
        self.climate_service = climate_service
        self.soil_service = soil_service
        self.ranking_algorithm = ranking_algorithm
    
    async def get_recommendations(
        self, 
        request: VarietyRecommendationRequest
    ) -> List[VarietyRecommendation]:
        """Get variety recommendations for given conditions."""
        # 1. Validate input
        self._validate_request(request)
        
        # 2. Gather context data
        context = await self._gather_context(request.farm_data)
        
        # 3. Find candidate varieties
        candidates = await self._find_candidates(request.crop_id, context)
        
        # 4. Rank varieties
        ranked_varieties = await self._rank_varieties(candidates, context, request.user_preferences)
        
        # 5. Generate explanations
        recommendations = await self._generate_recommendations(ranked_varieties, context)
        
        return recommendations[:request.max_recommendations]
    
    async def _gather_context(self, farm_data: FarmData) -> RecommendationContext:
        """Gather context data from various services."""
        climate_data = await self.climate_service.get_climate_data(
            farm_data.location.latitude,
            farm_data.location.longitude
        )
        
        soil_data = await self.soil_service.get_soil_analysis(
            farm_data.soil_data
        )
        
        return RecommendationContext(
            climate=climate_data,
            soil=soil_data,
            farm=farm_data
        )
```

## Design Patterns

### 1. Strategy Pattern

Used for different ranking algorithms and recommendation strategies.

```python
from abc import ABC, abstractmethod

class RankingStrategy(ABC):
    """Abstract ranking strategy."""
    
    @abstractmethod
    async def rank_varieties(
        self,
        varieties: List[Variety],
        context: RecommendationContext,
        preferences: UserPreferences
    ) -> List[RankedVariety]:
        """Rank varieties based on strategy."""
        pass

class YieldOptimizedRanking(RankingStrategy):
    """Ranking strategy optimized for yield."""
    
    async def rank_varieties(
        self,
        varieties: List[Variety],
        context: RecommendationContext,
        preferences: UserPreferences
    ) -> List[RankedVariety]:
        """Rank varieties by yield potential."""
        ranked = []
        for variety in varieties:
            score = self._calculate_yield_score(variety, context)
            ranked.append(RankedVariety(variety=variety, score=score))
        
        return sorted(ranked, key=lambda x: x.score, reverse=True)
    
    def _calculate_yield_score(self, variety: Variety, context: RecommendationContext) -> float:
        """Calculate yield-based score."""
        # Implementation details
        pass

class DiseaseResistanceRanking(RankingStrategy):
    """Ranking strategy optimized for disease resistance."""
    
    async def rank_varieties(
        self,
        varieties: List[Variety],
        context: RecommendationContext,
        preferences: UserPreferences
    ) -> List[RankedVariety]:
        """Rank varieties by disease resistance."""
        # Implementation details
        pass

class RankingStrategyFactory:
    """Factory for creating ranking strategies."""
    
    @staticmethod
    def create_strategy(preference: str) -> RankingStrategy:
        """Create ranking strategy based on preference."""
        strategies = {
            "yield": YieldOptimizedRanking(),
            "disease_resistance": DiseaseResistanceRanking(),
            "balanced": BalancedRanking()
        }
        return strategies.get(preference, BalancedRanking())
```

### 2. Observer Pattern

Used for recommendation events and notifications.

```python
from abc import ABC, abstractmethod
from typing import List

class RecommendationObserver(ABC):
    """Observer interface for recommendation events."""
    
    @abstractmethod
    async def on_recommendation_generated(self, event: RecommendationEvent):
        """Handle recommendation generated event."""
        pass
    
    @abstractmethod
    async def on_recommendation_viewed(self, event: RecommendationViewedEvent):
        """Handle recommendation viewed event."""
        pass

class RecommendationEventPublisher:
    """Publishes recommendation events to observers."""
    
    def __init__(self):
        self._observers: List[RecommendationObserver] = []
    
    def subscribe(self, observer: RecommendationObserver):
        """Subscribe observer to events."""
        self._observers.append(observer)
    
    def unsubscribe(self, observer: RecommendationObserver):
        """Unsubscribe observer from events."""
        self._observers.remove(observer)
    
    async def publish_recommendation_generated(self, event: RecommendationEvent):
        """Publish recommendation generated event."""
        for observer in self._observers:
            await observer.on_recommendation_generated(event)
    
    async def publish_recommendation_viewed(self, event: RecommendationViewedEvent):
        """Publish recommendation viewed event."""
        for observer in self._observers:
            await observer.on_recommendation_viewed(event)

class AnalyticsObserver(RecommendationObserver):
    """Observer for analytics tracking."""
    
    async def on_recommendation_generated(self, event: RecommendationEvent):
        """Track recommendation generation."""
        await self._track_event("recommendation_generated", event.data)
    
    async def on_recommendation_viewed(self, event: RecommendationViewedEvent):
        """Track recommendation views."""
        await self._track_event("recommendation_viewed", event.data)
    
    async def _track_event(self, event_type: str, data: dict):
        """Track event in analytics system."""
        # Implementation details
        pass
```

### 3. Factory Pattern

Used for creating domain objects and services.

```python
class VarietyFactory:
    """Factory for creating variety objects."""
    
    @staticmethod
    def create_variety_from_db(db_model: VarietyDB) -> Variety:
        """Create variety from database model."""
        return Variety(
            id=db_model.id,
            name=db_model.variety_name,
            crop_id=db_model.crop_id,
            company=db_model.company,
            maturity_days=db_model.maturity_days,
            yield_potential=YieldPotential(
                min=db_model.yield_potential_min,
                max=db_model.yield_potential_max,
                unit=db_model.yield_unit
            ),
            disease_resistance=DiseaseResistance.from_dict(db_model.disease_resistance),
            traits=[Trait.from_dict(t) for t in db_model.traits]
        )
    
    @staticmethod
    def create_variety_from_api(api_data: dict) -> Variety:
        """Create variety from API data."""
        return Variety(
            id=api_data["id"],
            name=api_data["name"],
            crop_id=api_data["crop_id"],
            company=api_data["company"],
            maturity_days=api_data["maturity_days"],
            yield_potential=YieldPotential.from_dict(api_data["yield_potential"]),
            disease_resistance=DiseaseResistance.from_dict(api_data["disease_resistance"]),
            traits=[Trait.from_dict(t) for t in api_data["traits"]]
        )

class ServiceFactory:
    """Factory for creating service instances."""
    
    @staticmethod
    def create_variety_service(
        db_session: AsyncSession,
        cache_client: Redis,
        external_services: ExternalServices
    ) -> VarietyRecommendationService:
        """Create variety recommendation service."""
        variety_repository = PostgreSQLVarietyRepository(db_session)
        climate_service = ClimateServiceClient(external_services.climate_url)
        soil_service = SoilServiceClient(external_services.soil_url)
        ranking_algorithm = RankingAlgorithmFactory.create_default()
        
        return VarietyRecommendationService(
            variety_repository=variety_repository,
            climate_service=climate_service,
            soil_service=soil_service,
            ranking_algorithm=ranking_algorithm
        )
```

### 4. Command Pattern

Used for handling user actions and system operations.

```python
from abc import ABC, abstractmethod
from typing import Any

class Command(ABC):
    """Abstract command interface."""
    
    @abstractmethod
    async def execute(self) -> Any:
        """Execute the command."""
        pass
    
    @abstractmethod
    async def undo(self) -> Any:
        """Undo the command."""
        pass

class GenerateRecommendationCommand(Command):
    """Command for generating variety recommendations."""
    
    def __init__(
        self,
        service: VarietyRecommendationService,
        request: VarietyRecommendationRequest
    ):
        self.service = service
        self.request = request
        self.result = None
    
    async def execute(self) -> List[VarietyRecommendation]:
        """Execute recommendation generation."""
        self.result = await self.service.get_recommendations(self.request)
        return self.result
    
    async def undo(self) -> None:
        """Undo is not applicable for read operations."""
        pass

class CommandInvoker:
    """Invokes commands and manages command history."""
    
    def __init__(self):
        self._history: List[Command] = []
        self._max_history = 100
    
    async def execute_command(self, command: Command) -> Any:
        """Execute command and add to history."""
        result = await command.execute()
        
        # Add to history
        self._history.append(command)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        
        return result
    
    async def undo_last_command(self) -> Any:
        """Undo the last command."""
        if not self._history:
            raise ValueError("No commands to undo")
        
        command = self._history.pop()
        return await command.undo()
```

## Data Patterns

### 1. Data Transfer Object (DTO) Pattern

Used for data transfer between layers and services.

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class VarietyRecommendationDTO(BaseModel):
    """DTO for variety recommendation data transfer."""
    
    id: str = Field(..., description="Variety ID")
    name: str = Field(..., description="Variety name")
    company: str = Field(..., description="Seed company")
    yield_potential: str = Field(..., description="Yield potential")
    maturity_days: int = Field(..., description="Days to maturity")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Recommendation confidence")
    suitability: str = Field(..., description="Suitability rating")
    disease_resistance: str = Field(..., description="Disease resistance level")
    traits: List[TraitDTO] = Field(default_factory=list, description="Variety traits")
    regional_performance: RegionalPerformanceDTO = Field(..., description="Regional performance data")
    economic_analysis: EconomicAnalysisDTO = Field(..., description="Economic analysis")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TraitDTO(BaseModel):
    """DTO for variety trait data."""
    
    name: str = Field(..., description="Trait name")
    category: str = Field(..., description="Trait category")
    description: Optional[str] = Field(None, description="Trait description")
    value: Optional[str] = Field(None, description="Trait value")

class RegionalPerformanceDTO(BaseModel):
    """DTO for regional performance data."""
    
    yield_advantage: str = Field(..., description="Yield advantage percentage")
    disease_rating: str = Field(..., description="Disease resistance rating")
    stress_tolerance: str = Field(..., description="Stress tolerance level")

class EconomicAnalysisDTO(BaseModel):
    """DTO for economic analysis data."""
    
    seed_cost_per_acre: float = Field(..., description="Seed cost per acre")
    expected_roi: float = Field(..., description="Expected return on investment")
    break_even_yield: float = Field(..., description="Break-even yield")
    market_premium: Optional[float] = Field(None, description="Market premium")
```

### 2. Value Object Pattern

Used for immutable objects that represent concepts.

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class YieldPotential:
    """Value object for yield potential."""
    
    min: float
    max: float
    unit: str
    
    def __post_init__(self):
        if self.min < 0 or self.max < 0:
            raise ValueError("Yield values must be positive")
        if self.min > self.max:
            raise ValueError("Minimum yield cannot be greater than maximum")
    
    @property
    def average(self) -> float:
        """Calculate average yield."""
        return (self.min + self.max) / 2
    
    def is_within_range(self, value: float) -> bool:
        """Check if value is within yield range."""
        return self.min <= value <= self.max

@dataclass(frozen=True)
class Coordinates:
    """Value object for geographic coordinates."""
    
    latitude: float
    longitude: float
    
    def __post_init__(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")
    
    def distance_to(self, other: 'Coordinates') -> float:
        """Calculate distance to another coordinate."""
        # Haversine formula implementation
        import math
        
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(self.latitude)
        lat2_rad = math.radians(other.latitude)
        delta_lat = math.radians(other.latitude - self.latitude)
        delta_lon = math.radians(other.longitude - self.longitude)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

@dataclass(frozen=True)
class SoilPH:
    """Value object for soil pH."""
    
    value: float
    
    def __post_init__(self):
        if not (0 <= self.value <= 14):
            raise ValueError("pH must be between 0 and 14")
    
    @property
    def acidity_level(self) -> str:
        """Get acidity level description."""
        if self.value < 6.5:
            return "acidic"
        elif self.value > 7.5:
            return "alkaline"
        else:
            return "neutral"
    
    def is_suitable_for_crop(self, crop_ph_range: tuple) -> bool:
        """Check if pH is suitable for crop."""
        min_ph, max_ph = crop_ph_range
        return min_ph <= self.value <= max_ph
```

## Error Handling Patterns

### 1. Result Pattern

Used for handling operations that can succeed or fail.

```python
from typing import Generic, TypeVar, Union, Optional
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E')

@dataclass
class Result(Generic[T, E]):
    """Result pattern for handling success/failure."""
    
    value: Optional[T] = None
    error: Optional[E] = None
    is_success: bool = True
    
    @classmethod
    def success(cls, value: T) -> 'Result[T, E]':
        """Create successful result."""
        return cls(value=value, is_success=True)
    
    @classmethod
    def failure(cls, error: E) -> 'Result[T, E]':
        """Create failed result."""
        return cls(error=error, is_success=False)
    
    def map(self, func) -> 'Result[T, E]':
        """Map function over successful result."""
        if self.is_success:
            try:
                return Result.success(func(self.value))
            except Exception as e:
                return Result.failure(e)
        return self
    
    def flat_map(self, func) -> 'Result[T, E]':
        """Flat map function over successful result."""
        if self.is_success:
            return func(self.value)
        return self

# Usage example
async def get_variety_recommendations(request: VarietyRecommendationRequest) -> Result[List[VarietyRecommendation], str]:
    """Get variety recommendations with error handling."""
    try:
        # Validate request
        validation_result = validate_request(request)
        if not validation_result.is_success:
            return validation_result
        
        # Get recommendations
        recommendations = await variety_service.get_recommendations(request)
        return Result.success(recommendations)
    
    except DatabaseError as e:
        return Result.failure(f"Database error: {str(e)}")
    except ExternalServiceError as e:
        return Result.failure(f"External service error: {str(e)}")
    except Exception as e:
        return Result.failure(f"Unexpected error: {str(e)}")
```

### 2. Circuit Breaker Pattern

Used for handling external service failures.

```python
import asyncio
import time
from enum import Enum
from typing import Callable, Any

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker for external service calls."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            return result
        
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
            
            raise e

class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass

# Usage example
climate_service_breaker = CircuitBreaker(
    failure_threshold=3,
    timeout=30,
    expected_exception=httpx.RequestError
)

async def get_climate_data_with_breaker(latitude: float, longitude: float):
    """Get climate data with circuit breaker protection."""
    try:
        return await climate_service_breaker.call(
            climate_service.get_climate_data,
            latitude,
            longitude
        )
    except CircuitBreakerOpenError:
        # Return fallback data
        return get_fallback_climate_data(latitude, longitude)
```

## Caching Patterns

### 1. Cache-Aside Pattern

Used for managing cache in application code.

```python
import json
import hashlib
from typing import Optional, Any
import redis.asyncio as redis

class CacheManager:
    """Cache manager using cache-aside pattern."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.default_ttl = 3600  # 1 hour
    
    def _generate_cache_key(self, prefix: str, *args) -> str:
        """Generate cache key from arguments."""
        key_data = json.dumps(args, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            cached_data = await self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            # Log error but don't fail the request
            logger.warning(f"Cache get error: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        try:
            ttl = ttl or self.default_ttl
            await self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
        except Exception as e:
            # Log error but don't fail the request
            logger.warning(f"Cache set error: {e}")
    
    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
    
    async def get_or_set(
        self,
        key: str,
        fetch_func: Callable,
        ttl: Optional[int] = None
    ) -> Any:
        """Get from cache or fetch and set."""
        # Try to get from cache
        cached_value = await self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Fetch from source
        value = await fetch_func()
        
        # Set in cache
        await self.set(key, value, ttl)
        
        return value

# Usage example
cache_manager = CacheManager(redis_client)

async def get_variety_recommendations_cached(
    request: VarietyRecommendationRequest
) -> List[VarietyRecommendation]:
    """Get variety recommendations with caching."""
    cache_key = cache_manager._generate_cache_key(
        "variety_recommendations",
        request.crop_id,
        request.farm_data.location.latitude,
        request.farm_data.location.longitude,
        request.farm_data.soil_data.ph
    )
    
    async def fetch_recommendations():
        return await variety_service.get_recommendations(request)
    
    return await cache_manager.get_or_set(
        cache_key,
        fetch_recommendations,
        ttl=1800  # 30 minutes
    )
```

### 2. Write-Through Pattern

Used for maintaining cache consistency.

```python
class WriteThroughCache:
    """Write-through cache implementation."""
    
    def __init__(self, cache_manager: CacheManager, repository: VarietyRepository):
        self.cache_manager = cache_manager
        self.repository = repository
    
    async def save_variety(self, variety: Variety) -> Variety:
        """Save variety with write-through caching."""
        # Save to database
        saved_variety = await self.repository.save(variety)
        
        # Update cache
        cache_key = f"variety:{saved_variety.id}"
        await self.cache_manager.set(cache_key, saved_variety)
        
        return saved_variety
    
    async def get_variety(self, variety_id: str) -> Optional[Variety]:
        """Get variety with cache check."""
        cache_key = f"variety:{variety_id}"
        
        # Try cache first
        cached_variety = await self.cache_manager.get(cache_key)
        if cached_variety:
            return cached_variety
        
        # Fetch from database
        variety = await self.repository.find_by_id(variety_id)
        if variety:
            # Update cache
            await self.cache_manager.set(cache_key, variety)
        
        return variety
```

## Security Patterns

### 1. Input Validation Pattern

Used for validating and sanitizing input data.

```python
from pydantic import BaseModel, validator, Field
from typing import Optional, List
import re

class VarietyRecommendationRequest(BaseModel):
    """Request model with validation."""
    
    crop_id: str = Field(..., min_length=1, max_length=50)
    farm_data: FarmData
    user_preferences: Optional[UserPreferences] = None
    max_recommendations: int = Field(default=20, ge=1, le=100)
    
    @validator('crop_id')
    def validate_crop_id(cls, v):
        """Validate crop ID format."""
        if not re.match(r'^[a-z_]+$', v):
            raise ValueError('Crop ID must contain only lowercase letters and underscores')
        return v
    
    @validator('max_recommendations')
    def validate_max_recommendations(cls, v):
        """Validate max recommendations."""
        if v > 100:
            raise ValueError('Maximum recommendations cannot exceed 100')
        return v

class FarmData(BaseModel):
    """Farm data with validation."""
    
    location: Location
    soil_data: SoilData
    field_size_acres: float = Field(..., gt=0, le=10000)
    irrigation_available: bool = False
    
    @validator('field_size_acres')
    def validate_field_size(cls, v):
        """Validate field size."""
        if v <= 0:
            raise ValueError('Field size must be positive')
        if v > 10000:
            raise ValueError('Field size cannot exceed 10,000 acres')
        return v

class Location(BaseModel):
    """Location with validation."""
    
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    climate_zone: Optional[str] = None
    
    @validator('latitude', 'longitude')
    def validate_coordinates(cls, v):
        """Validate coordinate precision."""
        if len(str(v).split('.')[-1]) > 7:
            raise ValueError('Coordinates cannot have more than 7 decimal places')
        return v
```

### 2. Rate Limiting Pattern

Used for controlling request rates.

```python
import time
from collections import defaultdict
from typing import Dict, Optional

class RateLimiter:
    """Rate limiter implementation."""
    
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client."""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) < self.requests_per_minute:
            self.requests[client_id].append(now)
            return True
        
        return False
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        now = time.time()
        minute_ago = now - 60
        
        recent_requests = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        return max(0, self.requests_per_minute - len(recent_requests))

# Usage in FastAPI
from fastapi import Request, HTTPException

rate_limiter = RateLimiter(requests_per_minute=100)

async def check_rate_limit(request: Request):
    """Check rate limit for request."""
    client_id = request.client.host
    
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )
```

## Performance Patterns

### 1. Async/Await Pattern

Used for non-blocking operations.

```python
import asyncio
import httpx
from typing import List, Dict, Any

class AsyncServiceClient:
    """Async service client for external API calls."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if not self._client:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout
            )
        return self._client
    
    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def get_climate_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get climate data asynchronously."""
        client = await self.get_client()
        response = await client.get(
            "/api/v1/climate-zones/by-coordinates",
            params={"latitude": latitude, "longitude": longitude}
        )
        response.raise_for_status()
        return response.json()
    
    async def get_soil_data(self, field_id: str) -> Dict[str, Any]:
        """Get soil data asynchronously."""
        client = await self.get_client()
        response = await client.get(f"/api/v1/soil-data/{field_id}")
        response.raise_for_status()
        return response.json()

class ParallelDataGatherer:
    """Gather data from multiple services in parallel."""
    
    def __init__(self, services: Dict[str, AsyncServiceClient]):
        self.services = services
    
    async def gather_all_data(
        self,
        latitude: float,
        longitude: float,
        field_id: str
    ) -> Dict[str, Any]:
        """Gather data from all services in parallel."""
        tasks = [
            self.services["climate"].get_climate_data(latitude, longitude),
            self.services["soil"].get_soil_data(field_id),
            self.services["market"].get_market_prices("corn")
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "climate_data": results[0] if not isinstance(results[0], Exception) else None,
            "soil_data": results[1] if not isinstance(results[1], Exception) else None,
            "market_data": results[2] if not isinstance(results[2], Exception) else None
        }
```

### 2. Connection Pooling Pattern

Used for managing database connections efficiently.

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

class DatabaseConnectionPool:
    """Database connection pool manager."""
    
    def __init__(self, database_url: str, pool_size: int = 20, max_overflow: int = 30):
        self.engine = create_async_engine(
            database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session from pool."""
        session = self.SessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def close(self):
        """Close all connections in pool."""
        await self.engine.dispose()

# Usage example
db_pool = DatabaseConnectionPool(
    database_url="postgresql+asyncpg://user:password@localhost/db",
    pool_size=20,
    max_overflow=30
)

async def get_varieties_with_pool(crop_id: str) -> List[Variety]:
    """Get varieties using connection pool."""
    async with db_pool.get_session() as session:
        query = select(VarietyDB).where(VarietyDB.crop_id == crop_id)
        result = await session.execute(query)
        return [Variety.from_db_model(v) for v in result.scalars().all()]
```

## Testing Patterns

### 1. Test Doubles Pattern

Used for testing with mock objects.

```python
from unittest.mock import AsyncMock, Mock
import pytest

class MockVarietyRepository:
    """Mock variety repository for testing."""
    
    def __init__(self):
        self.varieties = []
        self.find_by_crop_calls = []
        self.save_calls = []
    
    async def find_by_crop(self, crop_id: str) -> List[Variety]:
        """Mock find by crop method."""
        self.find_by_crop_calls.append(crop_id)
        return [v for v in self.varieties if v.crop_id == crop_id]
    
    async def save(self, variety: Variety) -> Variety:
        """Mock save method."""
        self.save_calls.append(variety)
        variety.id = f"mock_{len(self.varieties)}"
        self.varieties.append(variety)
        return variety
    
    def add_test_variety(self, variety: Variety):
        """Add test variety to mock repository."""
        self.varieties.append(variety)

class MockExternalService:
    """Mock external service for testing."""
    
    def __init__(self):
        self.responses = {}
        self.call_count = 0
    
    def set_response(self, endpoint: str, response: Any):
        """Set mock response for endpoint."""
        self.responses[endpoint] = response
    
    async def get_climate_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Mock climate data method."""
        self.call_count += 1
        return self.responses.get("climate_data", {
            "zone": "6a",
            "confidence": 0.9,
            "source": "mock"
        })

# Test example
@pytest.mark.asyncio
async def test_variety_recommendations_with_mocks():
    """Test variety recommendations with mock dependencies."""
    # Setup mocks
    mock_repository = MockVarietyRepository()
    mock_climate_service = MockExternalService()
    mock_soil_service = MockExternalService()
    
    # Add test data
    test_variety = Variety(
        id="test-1",
        name="Test Variety",
        crop_id="corn",
        company="Test Company",
        maturity_days=105,
        yield_potential=YieldPotential(min=180, max=200, unit="bu/acre")
    )
    mock_repository.add_test_variety(test_variety)
    
    # Setup mock responses
    mock_climate_service.set_response("climate_data", {
        "zone": "6a",
        "confidence": 0.9
    })
    mock_soil_service.set_response("soil_data", {
        "ph": 6.5,
        "organic_matter_percent": 3.2
    })
    
    # Create service with mocks
    service = VarietyRecommendationService(
        variety_repository=mock_repository,
        climate_service=mock_climate_service,
        soil_service=mock_soil_service,
        ranking_algorithm=MockRankingAlgorithm()
    )
    
    # Test
    request = VarietyRecommendationRequest(
        crop_id="corn",
        farm_data=FarmData(
            location=Location(latitude=40.7128, longitude=-74.0060),
            soil_data=SoilData(ph=6.5, organic_matter_percent=3.2),
            field_size_acres=100
        )
    )
    
    recommendations = await service.get_recommendations(request)
    
    # Assertions
    assert len(recommendations) == 1
    assert recommendations[0].name == "Test Variety"
    assert mock_repository.find_by_crop_calls == ["corn"]
    assert mock_climate_service.call_count == 1
```

This comprehensive service patterns document provides the architectural foundation and implementation guidelines for building robust, scalable, and maintainable services in the crop variety recommendations system.