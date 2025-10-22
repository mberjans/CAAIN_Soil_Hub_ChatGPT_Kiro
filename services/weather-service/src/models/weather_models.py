from sqlalchemy import Column, String, Integer, DECIMAL, DateTime, Boolean, Index, ForeignKey
from sqlalchemy.orm import declarative_base
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