# Climate Zone Detection - Design Document

## Overview

This document outlines the technical design for implementing climate zone specification and auto-detection in the Autonomous Farm Advisory System (AFAS). The system will provide both automatic climate zone detection from GPS coordinates and manual climate zone specification, integrating with USDA Plant Hardiness Zones and Köppen climate classifications.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  Climate Zone UI  │  Farm Profile  │  Crop Selection │  Mobile  │
│  - Auto-detect    │  - Zone Display│  - Zone Filter  │  - GPS   │
│  - Manual Select  │  - Validation  │  - Zone Impact  │  - Touch │
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  Climate Zone API │  Location API  │  Weather API   │  Farm API │
│  - Zone Detection │  - Geocoding   │  - Climate Data│  - Profile│
│  - Zone Lookup    │  - Validation  │  - Historical  │  - Update │
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                    Service Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  Climate Zone     │  Location      │  Weather       │  Crop     │
│  Service          │  Service       │  Service       │  Service  │
│  - USDA Zones     │  - Geocoding   │  - Climate     │  - Zone   │
│  - Köppen Types   │  - Validation  │  - History     │  - Filter │
│  - Zone Logic     │  - Coordinates │  - Analysis    │  - Match  │
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                   │
├─────────────────────────────────────────────────────────────────┤
│  Climate Zone DB  │  Location DB   │  Weather Cache │  Farm DB  │
│  - USDA Zones     │  - Coordinates │  - Climate     │  - Zones  │
│  - Köppen Data    │  - Addresses   │  - Historical  │  - Prefs  │
│  - Zone Rules     │  - Boundaries  │  - Forecasts   │  - Override│
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                  External Data Sources                          │
├─────────────────────────────────────────────────────────────────┤
│  USDA Plant       │  Köppen        │  Weather APIs  │  Elevation│
│  Hardiness Zones  │  Climate Data  │  - NOAA        │  Services │
│  - Official Data  │  - Climate     │  - OpenWeather │  - USGS   │
│  - Shapefiles     │  - Types       │  - Historical  │  - SRTM   │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Climate Zone Service

The core service responsible for climate zone detection and management.

```python
class ClimateZoneService:
    """Core climate zone detection and management service."""
    
    async def detect_zone_from_coordinates(
        self, 
        latitude: float, 
        longitude: float,
        elevation: Optional[float] = None
    ) -> ClimateZoneResult:
        """Auto-detect climate zone from GPS coordinates."""
        
    async def detect_zone_from_address(
        self, 
        address: str
    ) -> ClimateZoneResult:
        """Auto-detect climate zone from address."""
        
    async def validate_zone_selection(
        self,
        zone: str,
        latitude: float,
        longitude: float
    ) -> ValidationResult:
        """Validate manual zone selection against location."""
        
    async def get_zone_characteristics(
        self,
        zone: str
    ) -> ZoneCharacteristics:
        """Get detailed characteristics of a climate zone."""
        
    async def calculate_planting_dates(
        self,
        zone: str,
        crop: str
    ) -> PlantingDates:
        """Calculate optimal planting dates for zone and crop."""
```

### Data Models

#### ClimateZoneResult
```python
@dataclass
class ClimateZoneResult:
    """Result of climate zone detection."""
    usda_zone: str                    # e.g., "7a"
    usda_zone_description: str        # e.g., "0°F to 5°F"
    koppen_type: Optional[str]        # e.g., "Dfa"
    koppen_description: Optional[str] # e.g., "Humid continental, hot summer"
    confidence_score: float           # 0.0 to 1.0
    detection_method: str             # "coordinates", "address", "weather"
    alternative_zones: List[str]      # Possible alternative zones
    elevation_adjustment: Optional[float] # Elevation-based adjustment
    microclimate_factors: List[str]   # Factors affecting local climate
    data_sources: List[str]           # Sources used for detection
    last_updated: datetime
```

#### ZoneCharacteristics
```python
@dataclass
class ZoneCharacteristics:
    """Detailed characteristics of a climate zone."""
    zone: str
    min_temperature_f: float
    max_temperature_f: float
    average_frost_dates: FrostDates
    growing_season_days: int
    precipitation_pattern: str
    humidity_characteristics: str
    suitable_crops: List[str]
    challenging_crops: List[str]
    special_considerations: List[str]
```

#### FrostDates
```python
@dataclass
class FrostDates:
    """Frost date information for a climate zone."""
    last_spring_frost: date
    first_fall_frost: date
    frost_free_days: int
    confidence_interval_days: int
    historical_variance: int
```

### USDA Zone Detection Logic

#### Coordinate-Based Detection
```python
class USDAZoneDetector:
    """USDA Plant Hardiness Zone detection from coordinates."""
    
    def __init__(self):
        self.zone_shapefile = self._load_usda_shapefile()
        self.zone_lookup_cache = {}
    
    async def detect_zone(
        self, 
        latitude: float, 
        longitude: float,
        elevation: Optional[float] = None
    ) -> USDAZoneResult:
        """Detect USDA zone from coordinates."""
        
        # 1. Point-in-polygon lookup using USDA shapefiles
        base_zone = self._point_in_polygon_lookup(latitude, longitude)
        
        # 2. Apply elevation adjustments if available
        adjusted_zone = self._apply_elevation_adjustment(
            base_zone, elevation, latitude, longitude
        )
        
        # 3. Handle zone boundaries and transitions
        confidence = self._calculate_confidence(
            latitude, longitude, adjusted_zone
        )
        
        # 4. Identify alternative zones for boundary areas
        alternatives = self._find_alternative_zones(
            latitude, longitude, adjusted_zone
        )
        
        return USDAZoneResult(
            zone=adjusted_zone,
            confidence=confidence,
            alternatives=alternatives,
            elevation_adjusted=elevation is not None
        )
    
    def _apply_elevation_adjustment(
        self, 
        base_zone: str, 
        elevation: float,
        latitude: float,
        longitude: float
    ) -> str:
        """Apply elevation-based climate zone adjustments."""
        if not elevation:
            return base_zone
        
        # Rule: ~300 feet elevation = 1°F temperature drop
        # Each USDA zone = ~10°F range
        elevation_adjustment = elevation / 3000  # Zones to adjust
        
        if elevation_adjustment >= 0.5:
            return self._shift_zone_colder(base_zone, int(elevation_adjustment))
        
        return base_zone
```

### Köppen Climate Classification

#### Köppen Type Detection
```python
class KoppenClassifier:
    """Köppen climate classification implementation."""
    
    async def classify_climate(
        self,
        latitude: float,
        longitude: float,
        weather_data: Optional[WeatherHistory] = None
    ) -> KoppenResult:
        """Classify climate using Köppen system."""
        
        if weather_data:
            return await self._classify_from_weather_data(weather_data)
        else:
            return await self._classify_from_coordinates(latitude, longitude)
    
    async def _classify_from_weather_data(
        self, 
        weather_data: WeatherHistory
    ) -> KoppenResult:
        """Classify climate from historical weather data."""
        
        # Calculate annual temperature and precipitation patterns
        annual_temp = weather_data.annual_average_temperature
        monthly_temps = weather_data.monthly_temperatures
        annual_precip = weather_data.annual_precipitation
        monthly_precip = weather_data.monthly_precipitation
        
        # Apply Köppen classification rules
        climate_type = self._apply_koppen_rules(
            annual_temp, monthly_temps, annual_precip, monthly_precip
        )
        
        return KoppenResult(
            type=climate_type,
            description=self._get_koppen_description(climate_type),
            confidence=self._calculate_koppen_confidence(weather_data)
        )
    
    def _apply_koppen_rules(
        self,
        annual_temp: float,
        monthly_temps: List[float],
        annual_precip: float,
        monthly_precip: List[float]
    ) -> str:
        """Apply Köppen classification rules."""
        
        # Main climate groups
        if annual_temp >= 18:  # 64.4°F
            return self._classify_tropical(monthly_precip)
        elif self._is_arid(annual_temp, annual_precip):
            return self._classify_arid(annual_temp, annual_precip)
        elif min(monthly_temps) >= -3:  # 26.6°F
            return self._classify_temperate(monthly_temps, monthly_precip)
        elif max(monthly_temps) >= 10:  # 50°F
            return self._classify_continental(monthly_temps, monthly_precip)
        else:
            return self._classify_polar(monthly_temps)
```

### Climate Zone Validation

#### Validation Logic
```python
class ClimateZoneValidator:
    """Validates climate zone selections against location data."""
    
    async def validate_zone_selection(
        self,
        selected_zone: str,
        latitude: float,
        longitude: float,
        elevation: Optional[float] = None
    ) -> ValidationResult:
        """Validate user's climate zone selection."""
        
        # Auto-detect expected zone
        expected_result = await self.climate_service.detect_zone_from_coordinates(
            latitude, longitude, elevation
        )
        
        # Compare selected vs expected
        validation_issues = []
        
        if selected_zone != expected_result.usda_zone:
            severity = self._determine_validation_severity(
                selected_zone, expected_result.usda_zone
            )
            
            validation_issues.append(ValidationIssue(
                severity=severity,
                message=f"Selected zone {selected_zone} differs from detected zone {expected_result.usda_zone}",
                suggested_actions=self._get_validation_suggestions(
                    selected_zone, expected_result
                )
            ))
        
        return ValidationResult(
            is_valid=len([i for i in validation_issues if i.severity == "error"]) == 0,
            issues=validation_issues,
            confidence_score=self._calculate_validation_confidence(
                selected_zone, expected_result
            )
        )
    
    def _determine_validation_severity(
        self, 
        selected: str, 
        expected: str
    ) -> str:
        """Determine severity of zone mismatch."""
        
        selected_num = self._extract_zone_number(selected)
        expected_num = self._extract_zone_number(expected)
        
        zone_diff = abs(selected_num - expected_num)
        
        if zone_diff >= 3:
            return "error"  # Major mismatch
        elif zone_diff >= 2:
            return "warning"  # Significant mismatch
        elif zone_diff >= 1:
            return "info"  # Minor mismatch
        else:
            return "info"  # Subzone difference only
```

### Integration with Crop Recommendations

#### Climate-Aware Crop Filtering
```python
class ClimateAwareCropService:
    """Crop recommendation service with climate zone integration."""
    
    async def get_suitable_crops(
        self,
        climate_zone: str,
        soil_data: SoilData,
        farm_constraints: FarmConstraints
    ) -> List[CropRecommendation]:
        """Get crops suitable for the climate zone."""
        
        # Filter crops by climate zone compatibility
        climate_suitable_crops = await self._filter_crops_by_climate(
            climate_zone
        )
        
        # Apply additional filters (soil, constraints)
        filtered_crops = await self._apply_additional_filters(
            climate_suitable_crops, soil_data, farm_constraints
        )
        
        # Calculate climate suitability scores
        recommendations = []
        for crop in filtered_crops:
            climate_score = await self._calculate_climate_suitability(
                crop, climate_zone
            )
            
            recommendation = CropRecommendation(
                crop=crop,
                climate_suitability=climate_score,
                climate_considerations=await self._get_climate_considerations(
                    crop, climate_zone
                ),
                planting_dates=await self._calculate_planting_dates(
                    crop, climate_zone
                )
            )
            recommendations.append(recommendation)
        
        return sorted(recommendations, key=lambda x: x.climate_suitability, reverse=True)
    
    async def _calculate_climate_suitability(
        self,
        crop: Crop,
        climate_zone: str
    ) -> float:
        """Calculate how suitable a crop is for the climate zone."""
        
        zone_characteristics = await self.climate_service.get_zone_characteristics(
            climate_zone
        )
        
        # Temperature suitability
        temp_score = self._score_temperature_suitability(
            crop.temperature_requirements,
            zone_characteristics.min_temperature_f,
            zone_characteristics.max_temperature_f
        )
        
        # Growing season suitability
        season_score = self._score_growing_season_suitability(
            crop.days_to_maturity,
            zone_characteristics.growing_season_days
        )
        
        # Frost tolerance suitability
        frost_score = self._score_frost_tolerance(
            crop.frost_tolerance,
            zone_characteristics.average_frost_dates
        )
        
        # Weighted average
        return (temp_score * 0.4 + season_score * 0.4 + frost_score * 0.2)
```

## Error Handling

### Climate Zone Detection Errors
```python
class ClimateZoneError(Exception):
    """Base exception for climate zone operations."""
    pass

class ZoneDetectionError(ClimateZoneError):
    """Error during climate zone detection."""
    pass

class ZoneValidationError(ClimateZoneError):
    """Error during climate zone validation."""
    pass

class DataSourceError(ClimateZoneError):
    """Error accessing climate zone data sources."""
    pass

# Error handling strategy
async def detect_zone_with_fallback(
    latitude: float, 
    longitude: float
) -> ClimateZoneResult:
    """Detect climate zone with multiple fallback strategies."""
    
    try:
        # Primary: USDA shapefile lookup
        return await usda_detector.detect_zone(latitude, longitude)
    except DataSourceError:
        try:
            # Fallback 1: Weather-based inference
            return await weather_based_detector.detect_zone(latitude, longitude)
        except DataSourceError:
            try:
                # Fallback 2: Geographic approximation
                return await geographic_approximator.detect_zone(latitude, longitude)
            except DataSourceError:
                # Final fallback: Default zone with low confidence
                return ClimateZoneResult(
                    usda_zone="7a",  # Conservative default
                    confidence_score=0.1,
                    detection_method="default_fallback",
                    data_sources=["fallback"]
                )
```

## Testing Strategy

### Unit Tests
- Climate zone detection algorithms
- Köppen classification logic
- Validation rules and scoring
- Data model serialization/deserialization

### Integration Tests
- End-to-end climate zone detection workflow
- API endpoint functionality
- Database operations
- External data source integration

### Agricultural Validation Tests
- Climate zone accuracy against known locations
- Crop suitability calculations
- Planting date calculations
- Zone boundary handling

### Performance Tests
- Climate zone detection response times
- Concurrent request handling
- Cache effectiveness
- Database query optimization

## Deployment Considerations

### Data Requirements
- USDA Plant Hardiness Zone shapefiles (~50MB)
- Köppen climate classification data (~10MB)
- Climate zone lookup tables (~5MB)
- Historical weather data for validation

### Caching Strategy
- Climate zone results cached for 24 hours
- USDA zone lookups cached for 7 days
- Köppen classifications cached for 30 days
- Validation results cached for 1 hour

### Performance Optimization
- Spatial indexing for coordinate lookups
- Pre-computed zone boundaries
- Efficient shapefile queries
- Connection pooling for external APIs

### Monitoring and Alerting
- Climate zone detection success rates
- API response times
- Data source availability
- Cache hit rates
- User validation override rates

This design provides a comprehensive, scalable, and accurate climate zone detection system that integrates seamlessly with the existing AFAS architecture while providing farmers with reliable climate information for agricultural decision-making.