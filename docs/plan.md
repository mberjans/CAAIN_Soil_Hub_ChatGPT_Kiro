# Parallel Job 5: Weather Impact Analysis

**TICKET-009: Weather Data Integration System**  
**Estimated Timeline**: 3-4 weeks  
**Priority**: High  
**Can Start**: Immediately (No blocking dependencies)

## Executive Summary

This job implements weather data integration from multiple providers (NOAA, OpenWeatherMap), time series storage using TimescaleDB, and agricultural impact assessment algorithms. This work is **completely independent** of other parallel jobs.

## Related Tickets from Checklist

- **TICKET-009_weather-impact-analysis-1.1**: Implement weather data integration
- **TICKET-009_weather-impact-analysis-1.2**: Create multi-provider weather API client
- **TICKET-009_weather-impact-analysis-1.3**: Build time series data storage
- **TICKET-009_weather-impact-analysis-2.1**: Develop impact assessment algorithms
- **TICKET-009_weather-impact-analysis-2.2**: Create historical pattern analysis
- **TICKET-009_weather-impact-analysis-3.1**: Implement weather-based recommendations

## Technical Stack

```yaml
Languages: Python 3.11+
Framework: FastAPI
Database: PostgreSQL with TimescaleDB extension
ORM: SQLAlchemy 2.0+
Weather APIs: NOAA API, OpenWeatherMap API
Time Series: TimescaleDB
Caching: Redis (optional)
Testing: pytest, pytest-asyncio
Scheduling: APScheduler
```

## Service Architecture

**Service Location**: `services/weather-service/`  
**Port**: 8010 (new service)  
**Reference Pattern**: Follow `services/recommendation-engine/` structure

```
services/weather-service/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── weather_models.py
│   │   └── forecast_models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── weather_fetcher.py
│   │   ├── impact_analyzer.py
│   │   ├── historical_analyzer.py
│   │   └── recommendation_service.py
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── noaa_provider.py
│   │   ├── openweather_provider.py
│   │   └── mock_provider.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── weather_routes.py
│   │   └── forecast_routes.py
│   └── schemas/
│       ├── __init__.py
│       └── weather_schemas.py
├── tests/
│   ├── __init__.py
│   ├── test_weather_fetcher.py
│   ├── test_impact_analyzer.py
│   └── test_api.py
├── requirements.txt
└── README.md
```

## Week 1: Foundation & Data Integration (Days 1-7)

### Day 1: Setup

**requirements.txt**:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
httpx==0.25.1
pandas==2.1.3
numpy==1.26.2
APScheduler==3.10.4
pytest==7.4.3
pytest-asyncio==0.21.1
python-dotenv==1.0.0
```

**Setup Commands**:
```bash
mkdir -p services/weather-service/src/{models,services,providers,api,schemas}
mkdir -p services/weather-service/tests
cd services/weather-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Enable TimescaleDB extension
psql -U postgres -d caain_soil_hub -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
```

### Day 2-3: TimescaleDB Schema

**File**: `services/weather-service/src/models/weather_models.py`

```python
from sqlalchemy import Column, String, Integer, DECIMAL, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class WeatherStation(Base):
    """Weather station reference data"""
    __tablename__ = 'weather_stations'
    
    id = Column(Integer, primary_key=True)
    station_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200))
    latitude = Column(DECIMAL(9, 6), nullable=False)
    longitude = Column(DECIMAL(9, 6), nullable=False)
    elevation_meters = Column(Integer)
    source = Column(String(50), nullable=False)  # NOAA, OpenWeatherMap
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class WeatherObservation(Base):
    """Time series weather observations"""
    __tablename__ = 'weather_observations'
    
    id = Column(Integer, primary_key=True)
    station_id = Column(String(50), ForeignKey('weather_stations.station_id'), nullable=False)
    observation_time = Column(DateTime, nullable=False)
    
    # Temperature (Celsius)
    temperature_c = Column(DECIMAL(5, 2))
    temperature_min_c = Column(DECIMAL(5, 2))
    temperature_max_c = Column(DECIMAL(5, 2))
    
    # Precipitation (mm)
    precipitation_mm = Column(DECIMAL(6, 2))
    
    # Humidity (%)
    humidity_percent = Column(Integer)
    
    # Wind (km/h)
    wind_speed_kmh = Column(DECIMAL(5, 2))
    wind_direction_degrees = Column(Integer)
    
    # Pressure (hPa)
    pressure_hpa = Column(DECIMAL(6, 2))
    
    # Conditions
    conditions = Column(String(100))
    cloud_cover_percent = Column(Integer)
    
    # Solar radiation (W/m²)
    solar_radiation = Column(DECIMAL(7, 2))
    
    source = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_weather_obs_station_time', 'station_id', 'observation_time'),
        Index('idx_weather_obs_time', 'observation_time'),
    )

class WeatherForecast(Base):
    """Weather forecast data"""
    __tablename__ = 'weather_forecasts'
    
    id = Column(Integer, primary_key=True)
    station_id = Column(String(50), ForeignKey('weather_stations.station_id'), nullable=False)
    forecast_time = Column(DateTime, nullable=False)
    forecast_for = Column(DateTime, nullable=False)
    
    temperature_c = Column(DECIMAL(5, 2))
    precipitation_mm = Column(DECIMAL(6, 2))
    precipitation_probability = Column(Integer)
    humidity_percent = Column(Integer)
    wind_speed_kmh = Column(DECIMAL(5, 2))
    conditions = Column(String(100))
    
    source = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_weather_forecast_station_time', 'station_id', 'forecast_for'),
    )
```

**Database Migration SQL**:
```sql
-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create weather_stations table
CREATE TABLE IF NOT EXISTS weather_stations (
    id SERIAL PRIMARY KEY,
    station_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200),
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    elevation_meters INTEGER,
    source VARCHAR(50) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create weather_observations table
CREATE TABLE IF NOT EXISTS weather_observations (
    id SERIAL,
    station_id VARCHAR(50) REFERENCES weather_stations(station_id),
    observation_time TIMESTAMP NOT NULL,
    temperature_c DECIMAL(5,2),
    temperature_min_c DECIMAL(5,2),
    temperature_max_c DECIMAL(5,2),
    precipitation_mm DECIMAL(6,2),
    humidity_percent INTEGER,
    wind_speed_kmh DECIMAL(5,2),
    wind_direction_degrees INTEGER,
    pressure_hpa DECIMAL(6,2),
    conditions VARCHAR(100),
    cloud_cover_percent INTEGER,
    solar_radiation DECIMAL(7,2),
    source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('weather_observations', 'observation_time', if_not_exists => TRUE);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_weather_obs_station_time ON weather_observations(station_id, observation_time DESC);
CREATE INDEX IF NOT EXISTS idx_weather_obs_time ON weather_observations(observation_time DESC);

-- Create weather_forecasts table
CREATE TABLE IF NOT EXISTS weather_forecasts (
    id SERIAL,
    station_id VARCHAR(50) REFERENCES weather_stations(station_id),
    forecast_time TIMESTAMP NOT NULL,
    forecast_for TIMESTAMP NOT NULL,
    temperature_c DECIMAL(5,2),
    precipitation_mm DECIMAL(6,2),
    precipitation_probability INTEGER,
    humidity_percent INTEGER,
    wind_speed_kmh DECIMAL(5,2),
    conditions VARCHAR(100),
    source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('weather_forecasts', 'forecast_for', if_not_exists => TRUE);

-- Create continuous aggregates for daily summaries
CREATE MATERIALIZED VIEW IF NOT EXISTS weather_daily_summary
WITH (timescaledb.continuous) AS
SELECT
    station_id,
    time_bucket('1 day', observation_time) AS day,
    AVG(temperature_c) as avg_temp,
    MIN(temperature_min_c) as min_temp,
    MAX(temperature_max_c) as max_temp,
    SUM(precipitation_mm) as total_precipitation,
    AVG(humidity_percent) as avg_humidity
FROM weather_observations
GROUP BY station_id, day;
```

### Day 4-5: Weather Data Fetcher

**File**: `services/weather-service/src/services/weather_fetcher.py`

```python
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..models.weather_models import WeatherStation, WeatherObservation
from ..providers.noaa_provider import NOAAProvider
from ..providers.openweather_provider import OpenWeatherProvider
from ..providers.mock_provider import MockWeatherProvider
import logging

logger = logging.getLogger(__name__)

class WeatherFetcher:
    """Multi-provider weather data fetcher (TICKET-009_weather-impact-analysis-1.2)"""
    
    def __init__(self, db: Session):
        self.db = db
        self.providers = [
            MockWeatherProvider(),  # Use for development
            # NOAAProvider(),  # Enable for production
            # OpenWeatherProvider(api_key="YOUR_API_KEY"),
        ]
    
    async def fetch_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Fetch current weather from available providers"""
        
        # Find nearest station
        station = self._find_nearest_station(latitude, longitude)
        
        if not station:
            # Create virtual station for this location
            station = self._create_virtual_station(latitude, longitude)
        
        # Try each provider
        for provider in self.providers:
            try:
                weather_data = await provider.get_current_weather(latitude, longitude)
                
                if weather_data:
                    # Store observation
                    self._store_observation(station.station_id, weather_data, provider.name)
                    return weather_data
                    
            except Exception as e:
                logger.error(f"Provider {provider.name} failed: {e}")
                continue
        
        raise Exception("All weather providers failed")
    
    async def fetch_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Fetch weather forecast"""
        
        for provider in self.providers:
            try:
                forecast_data = await provider.get_forecast(latitude, longitude, days)
                if forecast_data:
                    return forecast_data
            except Exception as e:
                logger.error(f"Forecast provider {provider.name} failed: {e}")
                continue
        
        raise Exception("All forecast providers failed")
    
    def _find_nearest_station(self, latitude: float, longitude: float) -> Optional[WeatherStation]:
        """Find nearest weather station"""
        # Simplified: In production, use PostGIS distance query
        stations = self.db.query(WeatherStation).filter(WeatherStation.active == True).all()
        
        if not stations:
            return None
        
        # Simple distance calculation
        min_distance = float('inf')
        nearest = None
        
        for station in stations:
            distance = ((float(station.latitude) - latitude) ** 2 + 
                       (float(station.longitude) - longitude) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest = station
        
        return nearest
    
    def _create_virtual_station(self, latitude: float, longitude: float) -> WeatherStation:
        """Create virtual weather station for location"""
        station_id = f"VIRTUAL_{latitude:.4f}_{longitude:.4f}"
        
        existing = self.db.query(WeatherStation).filter(
            WeatherStation.station_id == station_id
        ).first()
        
        if existing:
            return existing
        
        station = WeatherStation(
            station_id=station_id,
            name=f"Virtual Station {latitude:.4f}, {longitude:.4f}",
            latitude=latitude,
            longitude=longitude,
            source="Virtual",
            active=True
        )
        
        self.db.add(station)
        self.db.commit()
        self.db.refresh(station)
        
        return station
    
    def _store_observation(self, station_id: str, weather_data: Dict, source: str):
        """Store weather observation in database"""
        observation = WeatherObservation(
            station_id=station_id,
            observation_time=datetime.utcnow(),
            temperature_c=weather_data.get('temperature_c'),
            precipitation_mm=weather_data.get('precipitation_mm', 0),
            humidity_percent=weather_data.get('humidity_percent'),
            wind_speed_kmh=weather_data.get('wind_speed_kmh'),
            pressure_hpa=weather_data.get('pressure_hpa'),
            conditions=weather_data.get('conditions'),
            source=source
        )
        
        self.db.add(observation)
        self.db.commit()
```

**File**: `services/weather-service/src/providers/mock_provider.py`

```python
import random
from typing import Dict, Any, List
from datetime import datetime, timedelta

class MockWeatherProvider:
    """Mock weather provider for development"""
    
    def __init__(self):
        self.name = "MockWeather"
    
    async def get_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Generate mock current weather"""
        return {
            "temperature_c": round(random.uniform(15, 30), 1),
            "precipitation_mm": round(random.uniform(0, 10), 1),
            "humidity_percent": random.randint(40, 90),
            "wind_speed_kmh": round(random.uniform(5, 25), 1),
            "pressure_hpa": round(random.uniform(1000, 1020), 1),
            "conditions": random.choice(["Clear", "Partly Cloudy", "Cloudy", "Rain"]),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_forecast(self, latitude: float, longitude: float, days: int) -> List[Dict[str, Any]]:
        """Generate mock forecast"""
        forecast = []
        base_temp = random.uniform(15, 25)
        
        for i in range(days):
            forecast_date = datetime.utcnow() + timedelta(days=i)
            forecast.append({
                "date": forecast_date.date().isoformat(),
                "temperature_c": round(base_temp + random.uniform(-5, 5), 1),
                "precipitation_mm": round(random.uniform(0, 15), 1),
                "precipitation_probability": random.randint(0, 100),
                "conditions": random.choice(["Clear", "Partly Cloudy", "Cloudy", "Rain", "Thunderstorms"])
            })
        
        return forecast
```

## Week 2-3: Impact Analysis & API (Days 8-20)

### Impact Analyzer

**File**: `services/weather-service/src/services/impact_analyzer.py`

```python
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.weather_models import WeatherObservation

class WeatherImpactAnalyzer:
    """Agricultural impact assessment (TICKET-009_weather-impact-analysis-2.1)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def analyze_planting_conditions(
        self,
        station_id: str,
        crop_type: str
    ) -> Dict[str, Any]:
        """Analyze if conditions are suitable for planting"""
        
        # Get recent weather (last 7 days)
        recent_weather = self._get_recent_weather(station_id, days=7)
        
        # Get forecast (next 7 days)
        # forecast = self._get_forecast(station_id, days=7)
        
        # Analyze soil temperature (estimated from air temp)
        avg_temp = sum(w.temperature_c for w in recent_weather) / len(recent_weather) if recent_weather else 0
        soil_temp_estimate = avg_temp * 0.9  # Simplified estimation
        
        # Crop-specific thresholds
        thresholds = {
            "corn": {"min_soil_temp": 10, "min_air_temp": 15},
            "soybean": {"min_soil_temp": 12, "min_air_temp": 18},
            "wheat": {"min_soil_temp": 5, "min_air_temp": 10}
        }
        
        crop_threshold = thresholds.get(crop_type, {"min_soil_temp": 10, "min_air_temp": 15})
        
        # Check precipitation
        total_precip = sum(w.precipitation_mm or 0 for w in recent_weather)
        
        # Determine suitability
        suitable = (
            soil_temp_estimate >= crop_threshold["min_soil_temp"] and
            avg_temp >= crop_threshold["min_air_temp"] and
            total_precip < 50  # Not too wet
        )
        
        return {
            "suitable_for_planting": suitable,
            "soil_temperature_estimate_c": round(soil_temp_estimate, 1),
            "average_air_temperature_c": round(avg_temp, 1),
            "recent_precipitation_mm": round(total_precip, 1),
            "recommendations": self._generate_planting_recommendations(suitable, soil_temp_estimate, total_precip)
        }
    
    def _get_recent_weather(self, station_id: str, days: int) -> List[WeatherObservation]:
        """Get recent weather observations"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        return self.db.query(WeatherObservation).filter(
            WeatherObservation.station_id == station_id,
            WeatherObservation.observation_time >= cutoff
        ).order_by(WeatherObservation.observation_time.desc()).all()
    
    def _generate_planting_recommendations(
        self,
        suitable: bool,
        soil_temp: float,
        precipitation: float
    ) -> List[str]:
        """Generate planting recommendations"""
        recommendations = []
        
        if suitable:
            recommendations.append("Conditions are favorable for planting")
        else:
            if soil_temp < 10:
                recommendations.append("Wait for soil to warm up before planting")
            if precipitation > 50:
                recommendations.append("Wait for fields to dry before planting")
        
        return recommendations
```

## Definition of Done

- [ ] TimescaleDB hypertables created
- [ ] Weather data fetching operational
- [ ] Impact analysis algorithms working
- [ ] API endpoints functional
- [ ] Scheduled updates working

## Integration Points

Integrates with:
- **Location Service** (Job 4): For farm coordinates
- **Recommendation Engine**: For weather-based advice
- **All Services**: Provides weather context

## Next Steps

After completion, integrate with fertilizer optimization (Job 2) for weather-aware application timing.

