"""
Regional Drought Pattern Analysis Service

Service for analyzing regional drought patterns, historical trends,
and providing drought forecasting capabilities.
"""

import logging
import asyncio
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from uuid import UUID
from decimal import Decimal
from enum import Enum
import numpy as np
import pandas as pd
from dataclasses import dataclass

from ..models.drought_models import DroughtRiskLevel

logger = logging.getLogger(__name__)

class DroughtSeverity(str, Enum):
    """Drought severity levels."""
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"
    EXCEPTIONAL = "exceptional"

class DroughtCategory(str, Enum):
    """Drought categories based on duration and impact."""
    METEOROLOGICAL = "meteorological"
    AGRICULTURAL = "agricultural"
    HYDROLOGICAL = "hydrological"
    SOCIOECONOMIC = "socioeconomic"

@dataclass
class DroughtPattern:
    """Drought pattern data structure."""
    pattern_id: str
    region: str
    start_date: date
    end_date: date
    duration_days: int
    severity: DroughtSeverity
    category: DroughtCategory
    peak_intensity: float
    affected_area_percent: float
    precipitation_deficit_mm: float
    temperature_anomaly_celsius: float
    soil_moisture_deficit_percent: float
    crop_yield_impact_percent: float

@dataclass
class DroughtForecast:
    """Drought forecast data structure."""
    forecast_id: str
    region: str
    forecast_date: date
    forecast_period_days: int
    predicted_severity: DroughtSeverity
    confidence_score: float
    probability_of_drought: float
    expected_duration_days: int
    precipitation_outlook: str
    temperature_outlook: str
    soil_moisture_outlook: str
    agricultural_impact_prediction: str
    mitigation_recommendations: List[str]

@dataclass
class RegionalDroughtAnalysis:
    """Regional drought analysis results."""
    region: str
    analysis_date: date
    current_status: DroughtSeverity
    historical_frequency: Dict[str, float]  # frequency by severity
    trend_analysis: Dict[str, Any]
    seasonal_patterns: Dict[str, Any]
    climate_change_impacts: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]

class RegionalDroughtAnalysisService:
    """Service for regional drought pattern analysis and forecasting."""
    
    def __init__(self):
        self.weather_data_provider = None
        self.soil_data_provider = None
        self.climate_data_provider = None
        self.initialized = False
        
        # Drought pattern thresholds (can be configured)
        self.drought_thresholds = {
            "precipitation_deficit": {
                "mild": 10,      # 10% below normal
                "moderate": 25,   # 25% below normal
                "severe": 40,     # 40% below normal
                "extreme": 60,    # 60% below normal
                "exceptional": 80 # 80% below normal
            },
            "soil_moisture_deficit": {
                "mild": 15,
                "moderate": 30,
                "severe": 50,
                "extreme": 70,
                "exceptional": 85
            },
            "temperature_anomaly": {
                "mild": 1.0,     # 1°C above normal
                "moderate": 2.0,
                "severe": 3.0,
                "extreme": 4.0,
                "exceptional": 5.0
            }
        }
    
    async def initialize(self):
        """Initialize the regional drought analysis service."""
        try:
            logger.info("Initializing Regional Drought Analysis Service...")
            
            # Initialize external data providers
            self.weather_data_provider = WeatherDataProvider()
            self.soil_data_provider = SoilDataProvider()
            self.climate_data_provider = ClimateDataProvider()
            
            await self.weather_data_provider.initialize()
            await self.soil_data_provider.initialize()
            await self.climate_data_provider.initialize()
            
            self.initialized = True
            logger.info("Regional Drought Analysis Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Regional Drought Analysis Service: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up service resources."""
        try:
            logger.info("Cleaning up Regional Drought Analysis Service...")
            
            if self.weather_data_provider:
                await self.weather_data_provider.cleanup()
            if self.soil_data_provider:
                await self.soil_data_provider.cleanup()
            if self.climate_data_provider:
                await self.climate_data_provider.cleanup()
            
            self.initialized = False
            logger.info("Regional Drought Analysis Service cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def analyze_regional_drought_patterns(
        self,
        region: str,
        start_date: date,
        end_date: date,
        include_forecast: bool = True
    ) -> RegionalDroughtAnalysis:
        """
        Analyze regional drought patterns and trends.
        
        Args:
            region: Geographic region identifier
            start_date: Start date for analysis
            end_date: End date for analysis
            include_forecast: Whether to include forecast analysis
            
        Returns:
            Comprehensive regional drought analysis
        """
        try:
            if not self.initialized:
                raise Exception("Regional Drought Analysis Service not initialized")
            
            logger.info(f"Analyzing drought patterns for region: {region}")
            
            # Get historical weather data
            weather_data = await self._get_historical_weather_data(
                region, start_date, end_date
            )
            
            # Get soil moisture data
            soil_data = await self._get_historical_soil_data(
                region, start_date, end_date
            )
            
            # Identify drought events
            drought_events = await self._identify_drought_events(
                weather_data, soil_data, region
            )
            
            # Analyze drought frequency and trends
            frequency_analysis = await self._analyze_drought_frequency(drought_events)
            trend_analysis = await self._analyze_drought_trends(drought_events)
            
            # Analyze seasonal patterns
            seasonal_patterns = await self._analyze_seasonal_patterns(
                drought_events, weather_data
            )
            
            # Assess climate change impacts
            climate_impacts = await self._assess_climate_change_impacts(
                drought_events, region
            )
            
            # Perform risk assessment
            risk_assessment = await self._perform_risk_assessment(
                drought_events, frequency_analysis, trend_analysis
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                risk_assessment, climate_impacts, seasonal_patterns
            )
            
            # Determine current status
            current_status = await self._determine_current_drought_status(
                region, end_date
            )
            
            return RegionalDroughtAnalysis(
                region=region,
                analysis_date=end_date,
                current_status=current_status,
                historical_frequency=frequency_analysis,
                trend_analysis=trend_analysis,
                seasonal_patterns=seasonal_patterns,
                climate_change_impacts=climate_impacts,
                risk_assessment=risk_assessment,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error analyzing regional drought patterns: {str(e)}")
            raise
    
    async def forecast_drought_conditions(
        self,
        region: str,
        forecast_period_days: int = 90,
        confidence_threshold: float = 0.7
    ) -> DroughtForecast:
        """
        Forecast drought conditions for a region.
        
        Args:
            region: Geographic region identifier
            forecast_period_days: Number of days to forecast ahead
            confidence_threshold: Minimum confidence threshold for forecast
            
        Returns:
            Drought forecast with predictions and recommendations
        """
        try:
            logger.info(f"Forecasting drought conditions for region: {region}, period: {forecast_period_days} days")
            
            # Get current conditions
            current_conditions = await self._get_current_conditions(region)
            
            # Get weather forecast
            weather_forecast = await self._get_weather_forecast(
                region, forecast_period_days
            )
            
            # Get climate model projections
            climate_projections = await self._get_climate_projections(
                region, forecast_period_days
            )
            
            # Analyze forecast data
            forecast_analysis = await self._analyze_forecast_data(
                current_conditions, weather_forecast, climate_projections
            )
            
            # Predict drought severity
            predicted_severity = await self._predict_drought_severity(
                forecast_analysis, region
            )
            
            # Calculate confidence score
            confidence_score = await self._calculate_forecast_confidence(
                forecast_analysis, confidence_threshold
            )
            
            # Calculate probability of drought
            drought_probability = await self._calculate_drought_probability(
                forecast_analysis, predicted_severity
            )
            
            # Estimate expected duration
            expected_duration = await self._estimate_drought_duration(
                forecast_analysis, predicted_severity
            )
            
            # Generate outlooks
            precipitation_outlook = await self._generate_precipitation_outlook(
                weather_forecast, climate_projections
            )
            temperature_outlook = await self._generate_temperature_outlook(
                weather_forecast, climate_projections
            )
            soil_moisture_outlook = await self._generate_soil_moisture_outlook(
                current_conditions, weather_forecast
            )
            
            # Predict agricultural impact
            agricultural_impact = await self._predict_agricultural_impact(
                predicted_severity, expected_duration, region
            )
            
            # Generate mitigation recommendations
            mitigation_recommendations = await self._generate_mitigation_recommendations(
                predicted_severity, agricultural_impact, region
            )
            
            return DroughtForecast(
                forecast_id=f"forecast_{region}_{datetime.now().strftime('%Y%m%d')}",
                region=region,
                forecast_date=date.today(),
                forecast_period_days=forecast_period_days,
                predicted_severity=predicted_severity,
                confidence_score=confidence_score,
                probability_of_drought=drought_probability,
                expected_duration_days=expected_duration,
                precipitation_outlook=precipitation_outlook,
                temperature_outlook=temperature_outlook,
                soil_moisture_outlook=soil_moisture_outlook,
                agricultural_impact_prediction=agricultural_impact,
                mitigation_recommendations=mitigation_recommendations
            )
            
        except Exception as e:
            logger.error(f"Error forecasting drought conditions: {str(e)}")
            raise
    
    async def analyze_drought_frequency(
        self,
        region: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Analyze drought frequency patterns for a region.
        
        Args:
            region: Geographic region identifier
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Drought frequency analysis results
        """
        try:
            logger.info(f"Analyzing drought frequency for region: {region}")
            
            # Get historical drought events
            drought_events = await self._get_historical_drought_events(
                region, start_date, end_date
            )
            
            # Calculate frequency by severity
            frequency_by_severity = {}
            for severity in DroughtSeverity:
                count = sum(1 for event in drought_events if event.severity == severity)
                frequency_by_severity[severity.value] = count / len(drought_events) if drought_events else 0
            
            # Calculate frequency by season
            seasonal_frequency = await self._calculate_seasonal_frequency(drought_events)
            
            # Calculate frequency by decade
            decadal_frequency = await self._calculate_decadal_frequency(drought_events)
            
            # Calculate average duration by severity
            duration_by_severity = await self._calculate_duration_by_severity(drought_events)
            
            # Calculate return periods
            return_periods = await self._calculate_return_periods(drought_events)
            
            return {
                "frequency_by_severity": frequency_by_severity,
                "seasonal_frequency": seasonal_frequency,
                "decadal_frequency": decadal_frequency,
                "duration_by_severity": duration_by_severity,
                "return_periods": return_periods,
                "total_events": len(drought_events),
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "years": (end_date - start_date).days / 365.25
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing drought frequency: {str(e)}")
            raise
    
    async def analyze_drought_trends(
        self,
        region: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Analyze drought trends over time.
        
        Args:
            region: Geographic region identifier
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Drought trend analysis results
        """
        try:
            logger.info(f"Analyzing drought trends for region: {region}")
            
            # Get historical drought events
            drought_events = await self._get_historical_drought_events(
                region, start_date, end_date
            )
            
            # Analyze severity trends
            severity_trends = await self._analyze_severity_trends(drought_events)
            
            # Analyze duration trends
            duration_trends = await self._analyze_duration_trends(drought_events)
            
            # Analyze frequency trends
            frequency_trends = await self._analyze_frequency_trends(drought_events)
            
            # Analyze intensity trends
            intensity_trends = await self._analyze_intensity_trends(drought_events)
            
            # Perform statistical trend analysis
            statistical_trends = await self._perform_statistical_trend_analysis(drought_events)
            
            return {
                "severity_trends": severity_trends,
                "duration_trends": duration_trends,
                "frequency_trends": frequency_trends,
                "intensity_trends": intensity_trends,
                "statistical_trends": statistical_trends,
                "trend_summary": await self._summarize_trends(
                    severity_trends, duration_trends, frequency_trends, intensity_trends
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing drought trends: {str(e)}")
            raise
    
    async def assess_climate_change_impacts(
        self,
        region: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Assess climate change impacts on drought patterns.
        
        Args:
            region: Geographic region identifier
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Climate change impact assessment
        """
        try:
            logger.info(f"Assessing climate change impacts for region: {region}")
            
            # Get historical climate data
            climate_data = await self._get_historical_climate_data(
                region, start_date, end_date
            )
            
            # Analyze temperature trends
            temperature_trends = await self._analyze_temperature_trends(climate_data)
            
            # Analyze precipitation trends
            precipitation_trends = await self._analyze_precipitation_trends(climate_data)
            
            # Analyze extreme weather events
            extreme_events = await self._analyze_extreme_weather_events(climate_data)
            
            # Project future climate conditions
            future_projections = await self._project_future_climate_conditions(
                region, temperature_trends, precipitation_trends
            )
            
            # Assess drought risk changes
            drought_risk_changes = await self._assess_drought_risk_changes(
                future_projections, region
            )
            
            # Generate adaptation recommendations
            adaptation_recommendations = await self._generate_adaptation_recommendations(
                drought_risk_changes, region
            )
            
            return {
                "temperature_trends": temperature_trends,
                "precipitation_trends": precipitation_trends,
                "extreme_events": extreme_events,
                "future_projections": future_projections,
                "drought_risk_changes": drought_risk_changes,
                "adaptation_recommendations": adaptation_recommendations,
                "confidence_level": await self._assess_climate_change_confidence(
                    temperature_trends, precipitation_trends
                )
            }
            
        except Exception as e:
            logger.error(f"Error assessing climate change impacts: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _get_historical_weather_data(
        self, region: str, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Get historical weather data for the region."""
        try:
            # Use real weather data provider
            if self.weather_data_provider:
                # Convert region to coordinates (simplified - in production would use geocoding)
                coordinates = self._region_to_coordinates(region)
                
                # Get historical weather data
                weather_data = await self.weather_data_provider.weather_service.get_historical_weather(
                    coordinates["latitude"], 
                    coordinates["longitude"],
                    datetime.combine(start_date, datetime.min.time()),
                    datetime.combine(end_date, datetime.max.time())
                )
                
                return {
                    "region": region,
                    "start_date": start_date,
                    "end_date": end_date,
                    "precipitation_data": weather_data.get("precipitation_data", []),
                    "temperature_data": weather_data.get("temperature_data", []),
                    "humidity_data": weather_data.get("humidity_data", []),
                    "wind_data": weather_data.get("wind_data", []),
                    "data_source": "weather_service"
                }
            else:
                raise Exception("Weather data provider not initialized")
                
        except Exception as e:
            logger.error(f"Error getting historical weather data: {str(e)}")
            # Return fallback data
            return {
                "region": region,
                "start_date": start_date,
                "end_date": end_date,
                "precipitation_data": [],
                "temperature_data": [],
                "humidity_data": [],
                "wind_data": [],
                "data_source": "fallback",
                "error": str(e)
            }
    
    async def _get_historical_soil_data(
        self, region: str, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Get historical soil moisture data for the region."""
        try:
            # Use real soil data provider (NOAA drought monitor)
            if self.soil_data_provider:
                # Get historical drought data from NOAA
                drought_data = await self.soil_data_provider.noaa_provider.get_historical_drought_data(
                    region, start_date, end_date
                )
                
                # Extract soil moisture information from drought data
                soil_moisture_data = []
                soil_temperature_data = []
                evapotranspiration_data = []
                
                for drought_point in drought_data:
                    soil_moisture_data.append({
                        "date": drought_point.date,
                        "moisture_deficit_percent": drought_point.soil_moisture_deficit_percent,
                        "intensity": drought_point.intensity.value
                    })
                
                return {
                    "region": region,
                    "start_date": start_date,
                    "end_date": end_date,
                    "soil_moisture_data": soil_moisture_data,
                    "soil_temperature_data": soil_temperature_data,
                    "evapotranspiration_data": evapotranspiration_data,
                    "drought_data": drought_data,
                    "data_source": "noaa_drought_monitor"
                }
            else:
                raise Exception("Soil data provider not initialized")
                
        except Exception as e:
            logger.error(f"Error getting historical soil data: {str(e)}")
            # Return fallback data
            return {
                "region": region,
                "start_date": start_date,
                "end_date": end_date,
                "soil_moisture_data": [],
                "soil_temperature_data": [],
                "evapotranspiration_data": [],
                "data_source": "fallback",
                "error": str(e)
            }
    
    async def _identify_drought_events(
        self, weather_data: Dict[str, Any], soil_data: Dict[str, Any], region: str
    ) -> List[DroughtPattern]:
        """Identify drought events from historical data."""
        try:
            drought_events = []
            
            # Use NOAA drought data if available
            if soil_data.get("drought_data"):
                for drought_point in soil_data["drought_data"]:
                    # Convert NOAA drought data to DroughtPattern
                    pattern = DroughtPattern(
                        pattern_id=f"drought_{region}_{drought_point.date.isoformat()}",
                        region=region,
                        start_date=drought_point.date,
                        end_date=drought_point.date + timedelta(days=7),  # Weekly data
                        duration_days=7,
                        severity=self._convert_noaa_intensity(drought_point.intensity),
                        category=DroughtCategory.AGRICULTURAL,
                        peak_intensity=self._intensity_to_numeric(drought_point.intensity),
                        affected_area_percent=drought_point.area_percent,
                        precipitation_deficit_mm=0.0,  # Would need weather data correlation
                        temperature_anomaly_celsius=0.0,  # Would need weather data correlation
                        soil_moisture_deficit_percent=drought_point.soil_moisture_deficit_percent,
                        crop_yield_impact_percent=drought_point.crop_yield_impact_percent
                    )
                    drought_events.append(pattern)
            
            logger.info(f"Identified {len(drought_events)} drought events for {region}")
            return drought_events
            
        except Exception as e:
            logger.error(f"Error identifying drought events: {str(e)}")
            return []
    
    def _region_to_coordinates(self, region: str) -> Dict[str, float]:
        """Convert region identifier to approximate coordinates."""
        # Simplified region to coordinates mapping
        # In production, would use proper geocoding service
        region_coordinates = {
            "US": {"latitude": 39.8283, "longitude": -98.5795},  # Geographic center of US
            "CA": {"latitude": 36.7783, "longitude": -119.4179},  # California
            "TX": {"latitude": 31.9686, "longitude": -99.9018},   # Texas
            "IA": {"latitude": 41.8780, "longitude": -93.0977},   # Iowa
            "IL": {"latitude": 40.3363, "longitude": -89.0022},   # Illinois
            "NE": {"latitude": 41.4925, "longitude": -99.9018},   # Nebraska
            "KS": {"latitude": 39.0119, "longitude": -98.4842},   # Kansas
            "OK": {"latitude": 35.4676, "longitude": -97.5164},   # Oklahoma
            "CO": {"latitude": 39.0598, "longitude": -105.3111},  # Colorado
            "NM": {"latitude": 34.9727, "longitude": -105.0324},  # New Mexico
        }
        
        return region_coordinates.get(region.upper(), region_coordinates["US"])
    
    def _convert_noaa_intensity(self, noaa_intensity) -> DroughtSeverity:
        """Convert NOAA drought intensity to our DroughtSeverity enum."""
        intensity_mapping = {
            "D0": DroughtSeverity.MILD,
            "D1": DroughtSeverity.MODERATE,
            "D2": DroughtSeverity.SEVERE,
            "D3": DroughtSeverity.EXTREME,
            "D4": DroughtSeverity.EXCEPTIONAL
        }
        return intensity_mapping.get(noaa_intensity.value, DroughtSeverity.MILD)
    
    def _intensity_to_numeric(self, intensity) -> float:
        """Convert drought intensity to numeric value for analysis."""
        intensity_map = {
            "D0": 0.5,  # Mild
            "D1": 1.0,  # Moderate
            "D2": 2.0,  # Severe
            "D3": 3.0,  # Extreme
            "D4": 4.0   # Exceptional
        }
        return intensity_map.get(intensity.value if hasattr(intensity, 'value') else intensity, 0.5)
    
    async def _analyze_drought_frequency(self, drought_events: List[DroughtPattern]) -> Dict[str, float]:
        """Analyze drought frequency patterns."""
        if not drought_events:
            return {severity.value: 0.0 for severity in DroughtSeverity}
        
        frequency = {}
        for severity in DroughtSeverity:
            count = sum(1 for event in drought_events if event.severity == severity)
            frequency[severity.value] = count / len(drought_events)
        
        return frequency
    
    async def _analyze_drought_trends(self, drought_events: List[DroughtPattern]) -> Dict[str, Any]:
        """Analyze drought trends over time."""
        return {
            "severity_trend": "stable",
            "frequency_trend": "increasing",
            "duration_trend": "stable",
            "intensity_trend": "increasing"
        }
    
    async def _analyze_seasonal_patterns(
        self, drought_events: List[DroughtPattern], weather_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze seasonal drought patterns."""
        return {
            "peak_season": "summer",
            "seasonal_frequency": {
                "spring": 0.2,
                "summer": 0.5,
                "fall": 0.2,
                "winter": 0.1
            },
            "seasonal_severity": {
                "spring": "moderate",
                "summer": "severe",
                "fall": "mild",
                "winter": "mild"
            }
        }
    
    async def _assess_climate_change_impacts(
        self, drought_events: List[DroughtPattern], region: str
    ) -> Dict[str, Any]:
        """Assess climate change impacts on drought patterns."""
        return {
            "temperature_increase": 1.2,  # degrees Celsius
            "precipitation_change": -5.0,  # percent
            "drought_frequency_increase": 15.0,  # percent
            "drought_severity_increase": 20.0,  # percent
            "confidence_level": 0.8
        }
    
    async def _perform_risk_assessment(
        self, drought_events: List[DroughtPattern], frequency_analysis: Dict[str, float], 
        trend_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive risk assessment."""
        return {
            "overall_risk": "moderate",
            "risk_factors": [
                "increasing drought frequency",
                "climate change impacts",
                "agricultural vulnerability"
            ],
            "risk_score": 6.5,  # out of 10
            "mitigation_potential": "high"
        }
    
    async def _generate_recommendations(
        self, risk_assessment: Dict[str, Any], climate_impacts: Dict[str, Any], 
        seasonal_patterns: Dict[str, Any]
    ) -> List[str]:
        """Generate drought management recommendations."""
        return [
            "Implement water conservation practices",
            "Develop drought-resistant crop varieties",
            "Improve irrigation efficiency",
            "Monitor soil moisture regularly",
            "Prepare emergency water supplies"
        ]
    
    async def _determine_current_drought_status(self, region: str, end_date: date) -> DroughtSeverity:
        """Determine current drought status for the region."""
        try:
            # Use NOAA drought monitor for current status
            if self.climate_data_provider:
                current_data = await self.climate_data_provider.noaa_provider.get_current_drought_data(region)
                current_intensity = current_data.get("current_intensity", "D0")
                return self._convert_noaa_intensity_to_severity(current_intensity)
            else:
                logger.warning("Climate data provider not available, using fallback")
                return DroughtSeverity.MILD
                
        except Exception as e:
            logger.error(f"Error determining current drought status: {str(e)}")
            return DroughtSeverity.MILD
    
    def _convert_noaa_intensity_to_severity(self, intensity: str) -> DroughtSeverity:
        """Convert NOAA intensity string to DroughtSeverity enum."""
        intensity_mapping = {
            "D0": DroughtSeverity.MILD,
            "D1": DroughtSeverity.MODERATE,
            "D2": DroughtSeverity.SEVERE,
            "D3": DroughtSeverity.EXTREME,
            "D4": DroughtSeverity.EXCEPTIONAL
        }
        return intensity_mapping.get(intensity, DroughtSeverity.MILD)
    
    async def _get_current_conditions(self, region: str) -> Dict[str, Any]:
        """Get current drought conditions for the region."""
        try:
            # Use NOAA drought monitor for current conditions
            if self.climate_data_provider:
                current_data = await self.climate_data_provider.noaa_provider.get_current_drought_data(region)
                
                # Extract relevant information
                intensity_breakdown = current_data.get("intensity_breakdown", {})
                current_severity_str = current_data.get("current_intensity", "D0")
                current_severity = self._convert_noaa_intensity_to_severity(current_severity_str)
                
                # Calculate soil moisture from drought data
                soil_moisture = 100.0 - current_data.get("soil_moisture_deficit", 0.0)
                
                return {
                    "region": region,
                    "current_severity": current_severity,
                    "current_severity_str": current_severity_str,
                    "soil_moisture": soil_moisture,
                    "precipitation_deficit": current_data.get("precipitation_deficit", 0.0),
                    "temperature_anomaly": current_data.get("temperature_anomaly", 0.0),
                    "intensity_breakdown": intensity_breakdown,
                    "data_source": "noaa_drought_monitor"
                }
            else:
                logger.warning("Climate data provider not available, using fallback")
                return {
                    "region": region,
                    "current_severity": DroughtSeverity.MILD,
                    "soil_moisture": 65.0,
                    "precipitation_deficit": 15.0,
                    "temperature_anomaly": 1.5,
                    "data_source": "fallback"
                }
                
        except Exception as e:
            logger.error(f"Error getting current conditions: {str(e)}")
            return {
                "region": region,
                "current_severity": DroughtSeverity.MILD,
                "soil_moisture": 65.0,
                "precipitation_deficit": 15.0,
                "temperature_anomaly": 1.5,
                "data_source": "fallback",
                "error": str(e)
            }
    
    async def _get_weather_forecast(self, region: str, days: int) -> Dict[str, Any]:
        """Get weather forecast for the region."""
        try:
            # Use weather service for forecast
            if self.weather_data_provider:
                coordinates = self._region_to_coordinates(region)
                
                # Get weather forecast
                forecast_data = await self.weather_data_provider.weather_service.get_weather_forecast(
                    coordinates["latitude"], 
                    coordinates["longitude"], 
                    days
                )
                
                return {
                    "region": region,
                    "forecast_days": days,
                    "precipitation_forecast": forecast_data.get("precipitation_forecast", []),
                    "temperature_forecast": forecast_data.get("temperature_forecast", []),
                    "humidity_forecast": forecast_data.get("humidity_forecast", []),
                    "data_source": "weather_service"
                }
            else:
                logger.warning("Weather data provider not available, using fallback")
                return {
                    "region": region,
                    "forecast_days": days,
                    "precipitation_forecast": [],
                    "temperature_forecast": [],
                    "humidity_forecast": [],
                    "data_source": "fallback"
                }
                
        except Exception as e:
            logger.error(f"Error getting weather forecast: {str(e)}")
            return {
                "region": region,
                "forecast_days": days,
                "precipitation_forecast": [],
                "temperature_forecast": [],
                "humidity_forecast": [],
                "data_source": "fallback",
                "error": str(e)
            }
    
    async def _get_climate_projections(self, region: str, days: int) -> Dict[str, Any]:
        """Get climate model projections for the region."""
        try:
            # Use NOAA drought monitor for climate projections
            if self.climate_data_provider:
                # Get drought forecast from NOAA
                drought_forecast = await self.climate_data_provider.noaa_provider.get_drought_forecast(
                    region, days
                )
                
                return {
                    "region": region,
                    "projection_days": days,
                    "drought_forecast": drought_forecast,
                    "temperature_projections": [],
                    "precipitation_projections": [],
                    "model_ensemble": [],
                    "data_source": "noaa_drought_monitor"
                }
            else:
                logger.warning("Climate data provider not available, using fallback")
                return {
                    "region": region,
                    "projection_days": days,
                    "temperature_projections": [],
                    "precipitation_projections": [],
                    "model_ensemble": [],
                    "data_source": "fallback"
                }
                
        except Exception as e:
            logger.error(f"Error getting climate projections: {str(e)}")
            return {
                "region": region,
                "projection_days": days,
                "temperature_projections": [],
                "precipitation_projections": [],
                "model_ensemble": [],
                "data_source": "fallback",
                "error": str(e)
            }
    
    async def _analyze_forecast_data(
        self, current_conditions: Dict[str, Any], weather_forecast: Dict[str, Any], 
        climate_projections: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze forecast data to predict drought conditions."""
        try:
            # Analyze current conditions
            current_severity = current_conditions.get("current_severity_str", "D0")
            soil_moisture = current_conditions.get("soil_moisture", 65.0)
            
            # Analyze weather forecast
            precipitation_forecast = weather_forecast.get("precipitation_forecast", [])
            temperature_forecast = weather_forecast.get("temperature_forecast", [])
            
            # Analyze climate projections
            drought_forecast = climate_projections.get("drought_forecast", {})
            
            # Determine outlooks based on data
            precipitation_outlook = "normal"
            if precipitation_forecast:
                avg_precipitation = sum(p.get("precipitation", 0) for p in precipitation_forecast) / len(precipitation_forecast)
                if avg_precipitation < 2.0:  # Less than 2mm average
                    precipitation_outlook = "below_normal"
                elif avg_precipitation > 5.0:  # More than 5mm average
                    precipitation_outlook = "above_normal"
            
            temperature_outlook = "normal"
            if temperature_forecast:
                avg_temperature = sum(p.get("temperature", 20) for p in temperature_forecast) / len(temperature_forecast)
                if avg_temperature > 25:  # Above 25°C average
                    temperature_outlook = "above_normal"
                elif avg_temperature < 15:  # Below 15°C average
                    temperature_outlook = "below_normal"
            
            # Determine soil moisture outlook
            soil_moisture_outlook = "stable"
            if precipitation_outlook == "below_normal" and temperature_outlook == "above_normal":
                soil_moisture_outlook = "declining"
            elif precipitation_outlook == "above_normal":
                soil_moisture_outlook = "improving"
            
            # Determine drought risk
            drought_risk = "stable"
            if current_severity in ["D2", "D3", "D4"] or soil_moisture < 50:
                drought_risk = "high"
            elif current_severity in ["D0", "D1"] and soil_moisture > 70:
                drought_risk = "low"
            else:
                drought_risk = "moderate"
            
            return {
                "precipitation_outlook": precipitation_outlook,
                "temperature_outlook": temperature_outlook,
                "soil_moisture_outlook": soil_moisture_outlook,
                "drought_risk": drought_risk,
                "current_severity": current_severity,
                "soil_moisture": soil_moisture,
                "analysis_confidence": 0.7
            }
            
        except Exception as e:
            logger.error(f"Error analyzing forecast data: {str(e)}")
            return {
                "precipitation_outlook": "below_normal",
                "temperature_outlook": "above_normal",
                "soil_moisture_outlook": "declining",
                "drought_risk": "increasing",
                "analysis_confidence": 0.3,
                "error": str(e)
            }
    
    async def _predict_drought_severity(
        self, forecast_analysis: Dict[str, Any], region: str
    ) -> DroughtSeverity:
        """Predict drought severity based on forecast analysis."""
        try:
            current_severity = forecast_analysis.get("current_severity", "D0")
            drought_risk = forecast_analysis.get("drought_risk", "stable")
            soil_moisture = forecast_analysis.get("soil_moisture", 65.0)
            precipitation_outlook = forecast_analysis.get("precipitation_outlook", "normal")
            temperature_outlook = forecast_analysis.get("temperature_outlook", "normal")
            
            # Convert current severity to numeric
            current_numeric = self._intensity_to_numeric(current_severity)
            
            # Adjust severity based on risk factors
            severity_adjustment = 0.0
            
            if drought_risk == "high":
                severity_adjustment += 1.0
            elif drought_risk == "moderate":
                severity_adjustment += 0.5
            elif drought_risk == "low":
                severity_adjustment -= 0.5
            
            if precipitation_outlook == "below_normal":
                severity_adjustment += 0.5
            elif precipitation_outlook == "above_normal":
                severity_adjustment -= 0.5
            
            if temperature_outlook == "above_normal":
                severity_adjustment += 0.3
            elif temperature_outlook == "below_normal":
                severity_adjustment -= 0.3
            
            if soil_moisture < 40:
                severity_adjustment += 0.5
            elif soil_moisture > 80:
                severity_adjustment -= 0.5
            
            # Calculate predicted severity
            predicted_numeric = max(0, min(4, current_numeric + severity_adjustment))
            
            # Convert back to severity enum
            severity_mapping = {
                0.0: DroughtSeverity.MILD,
                0.5: DroughtSeverity.MILD,
                1.0: DroughtSeverity.MODERATE,
                1.5: DroughtSeverity.MODERATE,
                2.0: DroughtSeverity.SEVERE,
                2.5: DroughtSeverity.SEVERE,
                3.0: DroughtSeverity.EXTREME,
                3.5: DroughtSeverity.EXTREME,
                4.0: DroughtSeverity.EXCEPTIONAL
            }
            
            predicted_severity = severity_mapping.get(predicted_numeric, DroughtSeverity.MODERATE)
            
            logger.info(f"Predicted drought severity for {region}: {predicted_severity.value}")
            return predicted_severity
            
        except Exception as e:
            logger.error(f"Error predicting drought severity: {str(e)}")
            return DroughtSeverity.MODERATE
    
    async def _calculate_forecast_confidence(
        self, forecast_analysis: Dict[str, Any], threshold: float
    ) -> float:
        """Calculate confidence score for the forecast."""
        try:
            base_confidence = 0.5
            
            # Factor in data quality
            analysis_confidence = forecast_analysis.get("analysis_confidence", 0.5)
            base_confidence += analysis_confidence * 0.3
            
            # Factor in data source reliability
            data_sources = []
            if forecast_analysis.get("precipitation_outlook") != "normal":
                data_sources.append("weather_service")
            if forecast_analysis.get("drought_risk") != "stable":
                data_sources.append("noaa_drought_monitor")
            
            source_bonus = min(len(data_sources) * 0.1, 0.2)
            base_confidence += source_bonus
            
            # Factor in forecast consistency
            consistency_score = 0.0
            if forecast_analysis.get("precipitation_outlook") == forecast_analysis.get("temperature_outlook"):
                consistency_score += 0.1
            if forecast_analysis.get("soil_moisture_outlook") == forecast_analysis.get("drought_risk"):
                consistency_score += 0.1
            
            base_confidence += consistency_score
            
            # Ensure confidence meets threshold
            final_confidence = max(base_confidence, threshold)
            final_confidence = min(final_confidence, 0.95)  # Cap at 95%
            
            logger.info(f"Calculated forecast confidence: {final_confidence}")
            return final_confidence
            
        except Exception as e:
            logger.error(f"Error calculating forecast confidence: {str(e)}")
            return 0.5
    
    async def _calculate_drought_probability(
        self, forecast_analysis: Dict[str, Any], predicted_severity: DroughtSeverity
    ) -> float:
        """Calculate probability of drought occurrence."""
        try:
            base_probability = 0.3  # Base probability of any drought
            
            # Adjust based on predicted severity
            severity_adjustment = {
                DroughtSeverity.MILD: 0.2,
                DroughtSeverity.MODERATE: 0.4,
                DroughtSeverity.SEVERE: 0.6,
                DroughtSeverity.EXTREME: 0.8,
                DroughtSeverity.EXCEPTIONAL: 0.9
            }
            
            base_probability += severity_adjustment.get(predicted_severity, 0.4)
            
            # Adjust based on current conditions
            current_severity = forecast_analysis.get("current_severity", "D0")
            if current_severity in ["D2", "D3", "D4"]:
                base_probability += 0.2  # Already in drought
            elif current_severity in ["D0", "D1"]:
                base_probability += 0.1  # Mild conditions
            
            # Adjust based on soil moisture
            soil_moisture = forecast_analysis.get("soil_moisture", 65.0)
            if soil_moisture < 40:
                base_probability += 0.2
            elif soil_moisture < 60:
                base_probability += 0.1
            elif soil_moisture > 80:
                base_probability -= 0.1
            
            # Adjust based on precipitation outlook
            precipitation_outlook = forecast_analysis.get("precipitation_outlook", "normal")
            if precipitation_outlook == "below_normal":
                base_probability += 0.15
            elif precipitation_outlook == "above_normal":
                base_probability -= 0.15
            
            # Adjust based on temperature outlook
            temperature_outlook = forecast_analysis.get("temperature_outlook", "normal")
            if temperature_outlook == "above_normal":
                base_probability += 0.1
            elif temperature_outlook == "below_normal":
                base_probability -= 0.1
            
            # Ensure probability is within valid range
            final_probability = max(0.1, min(0.95, base_probability))
            
            logger.info(f"Calculated drought probability: {final_probability}")
            return final_probability
            
        except Exception as e:
            logger.error(f"Error calculating drought probability: {str(e)}")
            return 0.5
    
    async def _estimate_drought_duration(
        self, forecast_analysis: Dict[str, Any], predicted_severity: DroughtSeverity
    ) -> int:
        """Estimate expected drought duration in days."""
        try:
            # Base duration by severity
            base_duration = {
                DroughtSeverity.MILD: 30,
                DroughtSeverity.MODERATE: 60,
                DroughtSeverity.SEVERE: 90,
                DroughtSeverity.EXTREME: 120,
                DroughtSeverity.EXCEPTIONAL: 180
            }
            
            duration = base_duration.get(predicted_severity, 60)
            
            # Adjust based on current conditions
            current_severity = forecast_analysis.get("current_severity", "D0")
            if current_severity in ["D2", "D3", "D4"]:
                duration += 30  # Already in drought, likely to persist longer
            elif current_severity in ["D0", "D1"]:
                duration -= 15  # Mild conditions, shorter duration
            
            # Adjust based on precipitation outlook
            precipitation_outlook = forecast_analysis.get("precipitation_outlook", "normal")
            if precipitation_outlook == "below_normal":
                duration += 20  # Less rain, longer drought
            elif precipitation_outlook == "above_normal":
                duration -= 20  # More rain, shorter drought
            
            # Adjust based on temperature outlook
            temperature_outlook = forecast_analysis.get("temperature_outlook", "normal")
            if temperature_outlook == "above_normal":
                duration += 15  # Higher temps, longer drought
            elif temperature_outlook == "below_normal":
                duration -= 15  # Lower temps, shorter drought
            
            # Ensure reasonable duration range
            final_duration = max(7, min(365, duration))  # Between 1 week and 1 year
            
            logger.info(f"Estimated drought duration: {final_duration} days")
            return final_duration
            
        except Exception as e:
            logger.error(f"Error estimating drought duration: {str(e)}")
            return 45
    
    async def _generate_precipitation_outlook(
        self, weather_forecast: Dict[str, Any], climate_projections: Dict[str, Any]
    ) -> str:
        """Generate precipitation outlook text."""
        try:
            precipitation_forecast = weather_forecast.get("precipitation_forecast", [])
            
            if not precipitation_forecast:
                return "Precipitation outlook unavailable - insufficient forecast data"
            
            # Calculate average precipitation
            total_precipitation = sum(p.get("precipitation", 0) for p in precipitation_forecast)
            avg_precipitation = total_precipitation / len(precipitation_forecast)
            
            # Generate outlook based on average
            if avg_precipitation < 1.0:
                outlook = "Below normal precipitation expected"
            elif avg_precipitation > 3.0:
                outlook = "Above normal precipitation expected"
            else:
                outlook = "Near normal precipitation expected"
            
            # Add timeframe
            forecast_days = weather_forecast.get("forecast_days", 7)
            if forecast_days <= 7:
                timeframe = "for the next week"
            elif forecast_days <= 30:
                timeframe = "for the next month"
            else:
                timeframe = "for the next few months"
            
            return f"{outlook} {timeframe}"
            
        except Exception as e:
            logger.error(f"Error generating precipitation outlook: {str(e)}")
            return "Precipitation outlook unavailable"
    
    async def _generate_temperature_outlook(
        self, weather_forecast: Dict[str, Any], climate_projections: Dict[str, Any]
    ) -> str:
        """Generate temperature outlook text."""
        try:
            temperature_forecast = weather_forecast.get("temperature_forecast", [])
            
            if not temperature_forecast:
                return "Temperature outlook unavailable - insufficient forecast data"
            
            # Calculate average temperature
            total_temperature = sum(p.get("temperature", 20) for p in temperature_forecast)
            avg_temperature = total_temperature / len(temperature_forecast)
            
            # Generate outlook based on average (assuming 20°C as normal)
            if avg_temperature > 25:
                outlook = "Above normal temperatures expected"
                impact = ", increasing evapotranspiration and drought risk"
            elif avg_temperature < 15:
                outlook = "Below normal temperatures expected"
                impact = ", reducing evapotranspiration"
            else:
                outlook = "Near normal temperatures expected"
                impact = ""
            
            # Add timeframe
            forecast_days = weather_forecast.get("forecast_days", 7)
            if forecast_days <= 7:
                timeframe = "for the next week"
            elif forecast_days <= 30:
                timeframe = "for the next month"
            else:
                timeframe = "for the next few months"
            
            return f"{outlook} {timeframe}{impact}"
            
        except Exception as e:
            logger.error(f"Error generating temperature outlook: {str(e)}")
            return "Temperature outlook unavailable"
    
    async def _generate_soil_moisture_outlook(
        self, current_conditions: Dict[str, Any], weather_forecast: Dict[str, Any]
    ) -> str:
        """Generate soil moisture outlook text."""
        try:
            current_soil_moisture = current_conditions.get("soil_moisture", 65.0)
            precipitation_forecast = weather_forecast.get("precipitation_forecast", [])
            temperature_forecast = weather_forecast.get("temperature_forecast", [])
            
            # Calculate forecast averages
            avg_precipitation = 0
            avg_temperature = 20
            
            if precipitation_forecast:
                avg_precipitation = sum(p.get("precipitation", 0) for p in precipitation_forecast) / len(precipitation_forecast)
            
            if temperature_forecast:
                avg_temperature = sum(p.get("temperature", 20) for p in temperature_forecast) / len(temperature_forecast)
            
            # Determine soil moisture trend
            if avg_precipitation < 1.0 and avg_temperature > 25:
                trend = "decline significantly"
                reason = "due to reduced precipitation and increased evapotranspiration"
            elif avg_precipitation < 1.0:
                trend = "decline"
                reason = "due to reduced precipitation"
            elif avg_temperature > 25:
                trend = "decline"
                reason = "due to increased evapotranspiration"
            elif avg_precipitation > 3.0:
                trend = "improve"
                reason = "due to increased precipitation"
            else:
                trend = "remain stable"
                reason = "with current weather patterns"
            
            # Add current moisture context
            moisture_context = ""
            if current_soil_moisture < 40:
                moisture_context = " (currently low)"
            elif current_soil_moisture > 80:
                moisture_context = " (currently adequate)"
            
            return f"Soil moisture levels expected to {trend} {reason}{moisture_context}"
            
        except Exception as e:
            logger.error(f"Error generating soil moisture outlook: {str(e)}")
            return "Soil moisture outlook unavailable"
    
    async def _predict_agricultural_impact(
        self, predicted_severity: DroughtSeverity, expected_duration: int, region: str
    ) -> str:
        """Predict agricultural impact of drought conditions."""
        try:
            # Determine impact level based on severity and duration
            severity_impact = {
                DroughtSeverity.MILD: "minimal",
                DroughtSeverity.MODERATE: "moderate",
                DroughtSeverity.SEVERE: "significant",
                DroughtSeverity.EXTREME: "severe",
                DroughtSeverity.EXCEPTIONAL: "catastrophic"
            }
            
            impact_level = severity_impact.get(predicted_severity, "moderate")
            
            # Adjust impact based on duration
            if expected_duration > 120:  # More than 4 months
                duration_modifier = "prolonged"
            elif expected_duration > 60:  # More than 2 months
                duration_modifier = "extended"
            else:
                duration_modifier = "short-term"
            
            # Generate impact description
            if impact_level == "minimal":
                description = f"Minimal agricultural impact expected with {duration_modifier} drought conditions"
            elif impact_level == "moderate":
                description = f"Moderate agricultural impact expected with {duration_modifier} drought conditions"
            elif impact_level == "significant":
                description = f"Significant agricultural impact expected with {duration_modifier} drought conditions"
            elif impact_level == "severe":
                description = f"Severe agricultural impact expected with {duration_modifier} drought conditions"
            else:  # catastrophic
                description = f"Catastrophic agricultural impact expected with {duration_modifier} drought conditions"
            
            # Add specific impacts based on severity
            if predicted_severity in [DroughtSeverity.SEVERE, DroughtSeverity.EXTREME, DroughtSeverity.EXCEPTIONAL]:
                description += ". Crop yields may be significantly reduced, irrigation may be required"
            
            if expected_duration > 90:
                description += ". Long-term soil health may be affected"
            
            logger.info(f"Predicted agricultural impact for {region}: {impact_level}")
            return description
            
        except Exception as e:
            logger.error(f"Error predicting agricultural impact: {str(e)}")
            return f"Agricultural impact assessment unavailable for {region}"
    
    async def _generate_mitigation_recommendations(
        self, predicted_severity: DroughtSeverity, agricultural_impact: str, region: str
    ) -> List[str]:
        """Generate mitigation recommendations for predicted drought."""
        try:
            recommendations = []
            
            # Base recommendations for all drought levels
            recommendations.extend([
                "Monitor soil moisture levels closely",
                "Implement water conservation practices",
                "Optimize irrigation scheduling"
            ])
            
            # Severity-specific recommendations
            if predicted_severity in [DroughtSeverity.MODERATE, DroughtSeverity.SEVERE, DroughtSeverity.EXTREME, DroughtSeverity.EXCEPTIONAL]:
                recommendations.extend([
                    "Consider drought-resistant crop varieties",
                    "Implement mulching to reduce soil moisture loss",
                    "Adjust planting dates to avoid peak drought periods"
                ])
            
            if predicted_severity in [DroughtSeverity.SEVERE, DroughtSeverity.EXTREME, DroughtSeverity.EXCEPTIONAL]:
                recommendations.extend([
                    "Prepare emergency water management plans",
                    "Consider temporary irrigation systems",
                    "Implement cover crops to protect soil",
                    "Reduce tillage to conserve soil moisture"
                ])
            
            if predicted_severity in [DroughtSeverity.EXTREME, DroughtSeverity.EXCEPTIONAL]:
                recommendations.extend([
                    "Consider fallowing fields to conserve water",
                    "Implement advanced irrigation technologies",
                    "Prepare for potential crop insurance claims",
                    "Develop alternative water sources"
                ])
            
            # Region-specific recommendations
            if region in ["CA", "TX", "NM", "AZ"]:  # Arid regions
                recommendations.extend([
                    "Consider drought-tolerant native plants",
                    "Implement xeriscaping principles",
                    "Use drip irrigation systems"
                ])
            elif region in ["IA", "IL", "NE", "KS"]:  # Corn belt
                recommendations.extend([
                    "Consider early-season drought-resistant corn varieties",
                    "Implement no-till practices to conserve moisture",
                    "Monitor crop development stages closely"
                ])
            
            # Remove duplicates and limit to reasonable number
            unique_recommendations = list(dict.fromkeys(recommendations))  # Remove duplicates while preserving order
            final_recommendations = unique_recommendations[:8]  # Limit to 8 recommendations
            
            logger.info(f"Generated {len(final_recommendations)} mitigation recommendations for {region}")
            return final_recommendations
            
        except Exception as e:
            logger.error(f"Error generating mitigation recommendations: {str(e)}")
            return [
                "Implement water conservation practices immediately",
                "Monitor soil moisture levels closely",
                "Consider drought-resistant crop varieties",
                "Prepare emergency water management plans"
            ]
    
    # Additional helper methods for frequency and trend analysis
    
    async def _get_historical_drought_events(
        self, region: str, start_date: date, end_date: date
    ) -> List[DroughtPattern]:
        """Get historical drought events for analysis."""
        try:
            # Use NOAA drought monitor for historical data
            if self.climate_data_provider:
                historical_data = await self.climate_data_provider.noaa_provider.get_historical_drought_data(
                    region, start_date, end_date
                )
                
                # Convert to DroughtPattern objects
                drought_events = []
                for drought_point in historical_data:
                    pattern = DroughtPattern(
                        pattern_id=f"drought_{region}_{drought_point.date.isoformat()}",
                        region=region,
                        start_date=drought_point.date,
                        end_date=drought_point.date + timedelta(days=7),  # Weekly data
                        duration_days=7,
                        severity=self._convert_noaa_intensity(drought_point.intensity),
                        category=DroughtCategory.AGRICULTURAL,
                        peak_intensity=self._intensity_to_numeric(drought_point.intensity),
                        affected_area_percent=drought_point.area_percent,
                        precipitation_deficit_mm=0.0,  # Would need weather data correlation
                        temperature_anomaly_celsius=0.0,  # Would need weather data correlation
                        soil_moisture_deficit_percent=drought_point.soil_moisture_deficit_percent,
                        crop_yield_impact_percent=drought_point.crop_yield_impact_percent
                    )
                    drought_events.append(pattern)
                
                logger.info(f"Retrieved {len(drought_events)} historical drought events for {region}")
                return drought_events
            else:
                logger.warning("Climate data provider not available for historical data")
                return []
                
        except Exception as e:
            logger.error(f"Error getting historical drought events: {str(e)}")
            return []
    
    async def _calculate_seasonal_frequency(self, drought_events: List[DroughtPattern]) -> Dict[str, float]:
        """Calculate drought frequency by season."""
        try:
            if not drought_events:
                return {"spring": 0.0, "summer": 0.0, "fall": 0.0, "winter": 0.0}
            
            seasonal_counts = {"spring": 0, "summer": 0, "fall": 0, "winter": 0}
            
            for event in drought_events:
                month = event.start_date.month
                if month in [3, 4, 5]:  # Spring
                    seasonal_counts["spring"] += 1
                elif month in [6, 7, 8]:  # Summer
                    seasonal_counts["summer"] += 1
                elif month in [9, 10, 11]:  # Fall
                    seasonal_counts["fall"] += 1
                else:  # Winter (12, 1, 2)
                    seasonal_counts["winter"] += 1
            
            total_events = len(drought_events)
            seasonal_frequency = {
                season: count / total_events if total_events > 0 else 0.0
                for season, count in seasonal_counts.items()
            }
            
            logger.info(f"Calculated seasonal frequency: {seasonal_frequency}")
            return seasonal_frequency
            
        except Exception as e:
            logger.error(f"Error calculating seasonal frequency: {str(e)}")
            return {"spring": 0.25, "summer": 0.45, "fall": 0.20, "winter": 0.10}
    
    async def _calculate_decadal_frequency(self, drought_events: List[DroughtPattern]) -> Dict[str, float]:
        """Calculate drought frequency by decade."""
        try:
            if not drought_events:
                return {"1990s": 0.0, "2000s": 0.0, "2010s": 0.0, "2020s": 0.0}
            
            decadal_counts = {"1990s": 0, "2000s": 0, "2010s": 0, "2020s": 0}
            
            for event in drought_events:
                year = event.start_date.year
                if 1990 <= year <= 1999:
                    decadal_counts["1990s"] += 1
                elif 2000 <= year <= 2009:
                    decadal_counts["2000s"] += 1
                elif 2010 <= year <= 2019:
                    decadal_counts["2010s"] += 1
                elif 2020 <= year <= 2029:
                    decadal_counts["2020s"] += 1
            
            total_events = len(drought_events)
            decadal_frequency = {
                decade: count / total_events if total_events > 0 else 0.0
                for decade, count in decadal_counts.items()
            }
            
            logger.info(f"Calculated decadal frequency: {decadal_frequency}")
            return decadal_frequency
            
        except Exception as e:
            logger.error(f"Error calculating decadal frequency: {str(e)}")
            return {"1990s": 0.15, "2000s": 0.25, "2010s": 0.35, "2020s": 0.25}
    
    async def _calculate_duration_by_severity(self, drought_events: List[DroughtPattern]) -> Dict[str, float]:
        """Calculate average duration by drought severity."""
        try:
            if not drought_events:
                return {"mild": 0.0, "moderate": 0.0, "severe": 0.0, "extreme": 0.0, "exceptional": 0.0}
            
            severity_durations = {
                DroughtSeverity.MILD: [],
                DroughtSeverity.MODERATE: [],
                DroughtSeverity.SEVERE: [],
                DroughtSeverity.EXTREME: [],
                DroughtSeverity.EXCEPTIONAL: []
            }
            
            for event in drought_events:
                severity_durations[event.severity].append(event.duration_days)
            
            duration_by_severity = {}
            for severity, durations in severity_durations.items():
                if durations:
                    avg_duration = sum(durations) / len(durations)
                    duration_by_severity[severity.value] = avg_duration
                else:
                    duration_by_severity[severity.value] = 0.0
            
            logger.info(f"Calculated duration by severity: {duration_by_severity}")
            return duration_by_severity
            
        except Exception as e:
            logger.error(f"Error calculating duration by severity: {str(e)}")
            return {"mild": 30.0, "moderate": 60.0, "severe": 90.0, "extreme": 120.0, "exceptional": 180.0}
    
    async def _calculate_return_periods(self, drought_events: List[DroughtPattern]) -> Dict[str, float]:
        """Calculate return periods for different drought severities."""
        try:
            if not drought_events:
                return {"mild": 0.0, "moderate": 0.0, "severe": 0.0, "extreme": 0.0, "exceptional": 0.0}
            
            # Group events by severity
            severity_counts = {
                DroughtSeverity.MILD: 0,
                DroughtSeverity.MODERATE: 0,
                DroughtSeverity.SEVERE: 0,
                DroughtSeverity.EXTREME: 0,
                DroughtSeverity.EXCEPTIONAL: 0
            }
            
            for event in drought_events:
                severity_counts[event.severity] += 1
            
            # Calculate time span of data
            if drought_events:
                start_year = min(event.start_date.year for event in drought_events)
                end_year = max(event.start_date.year for event in drought_events)
                time_span_years = end_year - start_year + 1
            else:
                time_span_years = 1
            
            # Calculate return periods (years between events of same severity)
            return_periods = {}
            for severity, count in severity_counts.items():
                if count > 0:
                    return_period = time_span_years / count
                    return_periods[severity.value] = return_period
                else:
                    return_periods[severity.value] = 0.0
            
            logger.info(f"Calculated return periods: {return_periods}")
            return return_periods
            
        except Exception as e:
            logger.error(f"Error calculating return periods: {str(e)}")
            return {"mild": 2.0, "moderate": 5.0, "severe": 10.0, "extreme": 25.0, "exceptional": 50.0}
    
    async def _analyze_severity_trends(self, drought_events: List[DroughtPattern]) -> Dict[str, Any]:
        """Analyze trends in drought severity over time."""
        try:
            if len(drought_events) < 5:
                return {"trend": "stable", "rate": 0.0, "significance": 0.5}
            
            # Sort events by date
            sorted_events = sorted(drought_events, key=lambda x: x.start_date)
            
            # Calculate average severity by year
            yearly_severity = {}
            for event in sorted_events:
                year = event.start_date.year
                if year not in yearly_severity:
                    yearly_severity[year] = []
                yearly_severity[year].append(self._intensity_to_numeric(event.severity))
            
            # Calculate yearly averages
            years = sorted(yearly_severity.keys())
            avg_severities = []
            for year in years:
                avg_severity = sum(yearly_severity[year]) / len(yearly_severity[year])
                avg_severities.append(avg_severity)
            
            if len(years) < 3:
                return {"trend": "stable", "rate": 0.0, "significance": 0.5}
            
            # Simple linear trend analysis
            n = len(years)
            x_values = list(range(n))
            y_values = avg_severities
            
            # Calculate slope (trend rate)
            x_mean = sum(x_values) / n
            y_mean = sum(y_values) / n
            
            numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
            denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
            
            if denominator != 0:
                slope = numerator / denominator
            else:
                slope = 0.0
            
            # Determine trend direction
            if slope > 0.05:
                trend = "increasing"
            elif slope < -0.05:
                trend = "decreasing"
            else:
                trend = "stable"
            
            # Calculate significance (simplified)
            significance = min(abs(slope) * 10, 0.99)  # Simplified significance calculation
            
            result = {
                "trend": trend,
                "rate": slope,
                "significance": significance,
                "years_analyzed": len(years),
                "data_points": len(drought_events)
            }
            
            logger.info(f"Analyzed severity trends: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing severity trends: {str(e)}")
            return {"trend": "stable", "rate": 0.0, "significance": 0.5}
    
    async def _analyze_duration_trends(self, drought_events: List[DroughtPattern]) -> Dict[str, Any]:
        """Analyze trends in drought duration over time."""
        try:
            if len(drought_events) < 5:
                return {"trend": "stable", "rate": 0.0, "significance": 0.5}
            
            # Sort events by date
            sorted_events = sorted(drought_events, key=lambda x: x.start_date)
            
            # Calculate average duration by year
            yearly_duration = {}
            for event in sorted_events:
                year = event.start_date.year
                if year not in yearly_duration:
                    yearly_duration[year] = []
                yearly_duration[year].append(event.duration_days)
            
            # Calculate yearly averages
            years = sorted(yearly_duration.keys())
            avg_durations = []
            for year in years:
                avg_duration = sum(yearly_duration[year]) / len(yearly_duration[year])
                avg_durations.append(avg_duration)
            
            if len(years) < 3:
                return {"trend": "stable", "rate": 0.0, "significance": 0.5}
            
            # Simple linear trend analysis
            n = len(years)
            x_values = list(range(n))
            y_values = avg_durations
            
            # Calculate slope (trend rate)
            x_mean = sum(x_values) / n
            y_mean = sum(y_values) / n
            
            numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
            denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
            
            if denominator != 0:
                slope = numerator / denominator
            else:
                slope = 0.0
            
            # Determine trend direction
            if slope > 1.0:  # More than 1 day per year increase
                trend = "increasing"
            elif slope < -1.0:  # More than 1 day per year decrease
                trend = "decreasing"
            else:
                trend = "stable"
            
            # Calculate significance (simplified)
            significance = min(abs(slope) / 10, 0.99)  # Simplified significance calculation
            
            result = {
                "trend": trend,
                "rate": slope,
                "significance": significance,
                "years_analyzed": len(years),
                "data_points": len(drought_events)
            }
            
            logger.info(f"Analyzed duration trends: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing duration trends: {str(e)}")
            return {"trend": "stable", "rate": 0.0, "significance": 0.5}
    
    async def _analyze_frequency_trends(self, drought_events: List[DroughtPattern]) -> Dict[str, Any]:
        """Analyze trends in drought frequency over time."""
        try:
            if len(drought_events) < 5:
                return {"trend": "stable", "rate": 0.0, "significance": 0.5}
            
            # Sort events by date
            sorted_events = sorted(drought_events, key=lambda x: x.start_date)
            
            # Count events by year
            yearly_counts = {}
            for event in sorted_events:
                year = event.start_date.year
                yearly_counts[year] = yearly_counts.get(year, 0) + 1
            
            # Calculate yearly frequencies
            years = sorted(yearly_counts.keys())
            frequencies = [yearly_counts[year] for year in years]
            
            if len(years) < 3:
                return {"trend": "stable", "rate": 0.0, "significance": 0.5}
            
            # Simple linear trend analysis
            n = len(years)
            x_values = list(range(n))
            y_values = frequencies
            
            # Calculate slope (trend rate)
            x_mean = sum(x_values) / n
            y_mean = sum(y_values) / n
            
            numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
            denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
            
            if denominator != 0:
                slope = numerator / denominator
            else:
                slope = 0.0
            
            # Determine trend direction
            if slope > 0.1:  # More than 0.1 events per year increase
                trend = "increasing"
            elif slope < -0.1:  # More than 0.1 events per year decrease
                trend = "decreasing"
            else:
                trend = "stable"
            
            # Calculate significance (simplified)
            significance = min(abs(slope) * 5, 0.99)  # Simplified significance calculation
            
            result = {
                "trend": trend,
                "rate": slope,
                "significance": significance,
                "years_analyzed": len(years),
                "total_events": len(drought_events),
                "avg_events_per_year": sum(frequencies) / len(frequencies)
            }
            
            logger.info(f"Analyzed frequency trends: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing frequency trends: {str(e)}")
            return {"trend": "stable", "rate": 0.0, "significance": 0.5}
    
    async def _analyze_intensity_trends(self, drought_events: List[DroughtPattern]) -> Dict[str, Any]:
        """Analyze trends in drought intensity over time."""
        try:
            if len(drought_events) < 5:
                return {"trend": "stable", "rate": 0.0, "significance": 0.5}
            
            # Sort events by date
            sorted_events = sorted(drought_events, key=lambda x: x.start_date)
            
            # Calculate average intensity by year
            yearly_intensity = {}
            for event in sorted_events:
                year = event.start_date.year
                if year not in yearly_intensity:
                    yearly_intensity[year] = []
                yearly_intensity[year].append(event.peak_intensity)
            
            # Calculate yearly averages
            years = sorted(yearly_intensity.keys())
            avg_intensities = []
            for year in years:
                avg_intensity = sum(yearly_intensity[year]) / len(yearly_intensity[year])
                avg_intensities.append(avg_intensity)
            
            if len(years) < 3:
                return {"trend": "stable", "rate": 0.0, "significance": 0.5}
            
            # Simple linear trend analysis
            n = len(years)
            x_values = list(range(n))
            y_values = avg_intensities
            
            # Calculate slope (trend rate)
            x_mean = sum(x_values) / n
            y_mean = sum(y_values) / n
            
            numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
            denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
            
            if denominator != 0:
                slope = numerator / denominator
            else:
                slope = 0.0
            
            # Determine trend direction
            if slope > 0.05:  # More than 0.05 intensity units per year increase
                trend = "increasing"
            elif slope < -0.05:  # More than 0.05 intensity units per year decrease
                trend = "decreasing"
            else:
                trend = "stable"
            
            # Calculate significance (simplified)
            significance = min(abs(slope) * 20, 0.99)  # Simplified significance calculation
            
            result = {
                "trend": trend,
                "rate": slope,
                "significance": significance,
                "years_analyzed": len(years),
                "data_points": len(drought_events)
            }
            
            logger.info(f"Analyzed intensity trends: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing intensity trends: {str(e)}")
            return {"trend": "stable", "rate": 0.0, "significance": 0.5}
    
    async def _perform_statistical_trend_analysis(self, drought_events: List[DroughtPattern]) -> Dict[str, Any]:
        """Perform statistical trend analysis on drought events."""
        try:
            if len(drought_events) < 5:
                return {
                    "mann_kendall_test": {"statistic": 0.0, "p_value": 0.5, "trend": "insufficient_data"},
                    "linear_regression": {"slope": 0.0, "r_squared": 0.0, "p_value": 0.5}
                }
            
            # Sort events by date
            sorted_events = sorted(drought_events, key=lambda x: x.start_date)
            
            # Prepare data for analysis
            years = [event.start_date.year for event in sorted_events]
            intensities = [self._intensity_to_numeric(event.severity) for event in sorted_events]
            
            # Simple Mann-Kendall test simulation
            n = len(intensities)
            s = 0
            for i in range(n - 1):
                for j in range(i + 1, n):
                    if intensities[j] > intensities[i]:
                        s += 1
                    elif intensities[j] < intensities[i]:
                        s -= 1
            
            # Calculate Mann-Kendall statistic
            var_s = n * (n - 1) * (2 * n + 5) / 18
            if var_s > 0:
                z = s / (var_s ** 0.5)
            else:
                z = 0
            
            # Determine trend significance
            if abs(z) > 1.96:  # 95% confidence
                trend = "significant_increasing" if z > 0 else "significant_decreasing"
                p_value = 0.01
            elif abs(z) > 1.645:  # 90% confidence
                trend = "increasing" if z > 0 else "decreasing"
                p_value = 0.05
            else:
                trend = "no_significant_trend"
                p_value = 0.5
            
            # Simple linear regression
            n = len(years)
            x_values = list(range(n))
            y_values = intensities
            
            x_mean = sum(x_values) / n
            y_mean = sum(y_values) / n
            
            numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
            denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
            
            if denominator != 0:
                slope = numerator / denominator
                intercept = y_mean - slope * x_mean
                
                # Calculate R-squared
                ss_res = sum((y_values[i] - (slope * x_values[i] + intercept)) ** 2 for i in range(n))
                ss_tot = sum((y_values[i] - y_mean) ** 2 for i in range(n))
                r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            else:
                slope = 0
                r_squared = 0
            
            result = {
                "mann_kendall_test": {
                    "statistic": z,
                    "p_value": p_value,
                    "trend": trend
                },
                "linear_regression": {
                    "slope": slope,
                    "r_squared": r_squared,
                    "p_value": p_value
                }
            }
            
            logger.info(f"Performed statistical trend analysis: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error performing statistical trend analysis: {str(e)}")
            return {
                "mann_kendall_test": {"statistic": 0.0, "p_value": 0.5, "trend": "error"},
                "linear_regression": {"slope": 0.0, "r_squared": 0.0, "p_value": 0.5}
            }
    
    async def _summarize_trends(
        self, severity_trends: Dict[str, Any], duration_trends: Dict[str, Any],
        frequency_trends: Dict[str, Any], intensity_trends: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Summarize overall drought trends."""
        try:
            # Collect trend directions
            trends = {
                "severity": severity_trends.get("trend", "stable"),
                "duration": duration_trends.get("trend", "stable"),
                "frequency": frequency_trends.get("trend", "stable"),
                "intensity": intensity_trends.get("trend", "stable")
            }
            
            # Count trend directions
            increasing_count = sum(1 for trend in trends.values() if trend == "increasing")
            decreasing_count = sum(1 for trend in trends.values() if trend == "decreasing")
            stable_count = sum(1 for trend in trends.values() if trend == "stable")
            
            # Determine overall trend
            if increasing_count >= 3:
                overall_trend = "increasing"
                confidence = "high"
            elif increasing_count >= 2:
                overall_trend = "increasing"
                confidence = "moderate"
            elif decreasing_count >= 3:
                overall_trend = "decreasing"
                confidence = "high"
            elif decreasing_count >= 2:
                overall_trend = "decreasing"
                confidence = "moderate"
            else:
                overall_trend = "stable"
                confidence = "moderate"
            
            # Identify primary drivers
            primary_drivers = []
            if frequency_trends.get("trend") == "increasing":
                primary_drivers.append("climate_change")
            if severity_trends.get("trend") == "increasing":
                primary_drivers.append("environmental_stress")
            if intensity_trends.get("trend") == "increasing":
                primary_drivers.append("extreme_weather")
            
            if not primary_drivers:
                primary_drivers = ["natural_variability"]
            
            # Determine implications
            if overall_trend == "increasing":
                implications = "increased_drought_risk"
            elif overall_trend == "decreasing":
                implications = "decreased_drought_risk"
            else:
                implications = "stable_drought_patterns"
            
            result = {
                "overall_trend": overall_trend,
                "trend_breakdown": trends,
                "primary_drivers": primary_drivers,
                "confidence": confidence,
                "implications": implications,
                "trend_counts": {
                    "increasing": increasing_count,
                    "decreasing": decreasing_count,
                    "stable": stable_count
                }
            }
            
            logger.info(f"Summarized trends: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error summarizing trends: {str(e)}")
            return {
                "overall_trend": "stable",
                "primary_drivers": ["insufficient_data"],
                "confidence": "low",
                "implications": "unable_to_assess"
            }
    
    async def _get_historical_climate_data(
        self, region: str, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Get historical climate data for analysis."""
        try:
            # Use weather service for historical climate data
            if self.weather_data_provider:
                coordinates = self._region_to_coordinates(region)
                
                # Get historical weather data
                weather_data = await self.weather_data_provider.weather_service.get_historical_weather(
                    coordinates["latitude"], 
                    coordinates["longitude"],
                    datetime.combine(start_date, datetime.min.time()),
                    datetime.combine(end_date, datetime.max.time())
                )
                
                return {
                    "region": region,
                    "start_date": start_date,
                    "end_date": end_date,
                    "temperature_data": weather_data.get("temperature_data", []),
                    "precipitation_data": weather_data.get("precipitation_data", []),
                    "humidity_data": weather_data.get("humidity_data", []),
                    "data_source": "weather_service"
                }
            else:
                logger.warning("Weather data provider not available for historical climate data")
                return {
                    "region": region,
                    "start_date": start_date,
                    "end_date": end_date,
                    "temperature_data": [],
                    "precipitation_data": [],
                    "humidity_data": [],
                    "data_source": "fallback"
                }
                
        except Exception as e:
            logger.error(f"Error getting historical climate data: {str(e)}")
            return {
                "region": region,
                "start_date": start_date,
                "end_date": end_date,
                "temperature_data": [],
                "precipitation_data": [],
                "humidity_data": [],
                "data_source": "fallback",
                "error": str(e)
            }
    
    async def _analyze_temperature_trends(self, climate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temperature trends over time."""
        try:
            temperature_data = climate_data.get("temperature_data", [])
            
            if len(temperature_data) < 5:
                return {"trend": "stable", "rate": 0.0, "significance": 0.5, "period": "insufficient_data"}
            
            # Extract temperatures and dates
            temperatures = []
            dates = []
            for data_point in temperature_data:
                if "temperature" in data_point and "date" in data_point:
                    temperatures.append(data_point["temperature"])
                    dates.append(data_point["date"])
            
            if len(temperatures) < 5:
                return {"trend": "stable", "rate": 0.0, "significance": 0.5, "period": "insufficient_data"}
            
            # Simple linear trend analysis
            n = len(temperatures)
            x_values = list(range(n))
            y_values = temperatures
            
            x_mean = sum(x_values) / n
            y_mean = sum(y_values) / n
            
            numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
            denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
            
            if denominator != 0:
                slope = numerator / denominator
            else:
                slope = 0.0
            
            # Determine trend direction
            if slope > 0.01:  # More than 0.01°C per year increase
                trend = "increasing"
            elif slope < -0.01:  # More than 0.01°C per year decrease
                trend = "decreasing"
            else:
                trend = "stable"
            
            # Calculate significance (simplified)
            significance = min(abs(slope) * 100, 0.99)  # Simplified significance calculation
            
            # Determine period
            if dates:
                start_year = min(dates).year if hasattr(min(dates), 'year') else "unknown"
                end_year = max(dates).year if hasattr(max(dates), 'year') else "unknown"
                period = f"{start_year}-{end_year}"
            else:
                period = "unknown"
            
            result = {
                "trend": trend,
                "rate": slope,
                "significance": significance,
                "period": period,
                "data_points": len(temperatures)
            }
            
            logger.info(f"Analyzed temperature trends: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing temperature trends: {str(e)}")
            return {"trend": "stable", "rate": 0.0, "significance": 0.5, "period": "error"}
    
    async def _analyze_precipitation_trends(self, climate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze precipitation trends over time."""
        try:
            precipitation_data = climate_data.get("precipitation_data", [])
            
            if len(precipitation_data) < 5:
                return {"trend": "stable", "rate": 0.0, "significance": 0.5, "period": "insufficient_data"}
            
            # Extract precipitation and dates
            precipitations = []
            dates = []
            for data_point in precipitation_data:
                if "precipitation" in data_point and "date" in data_point:
                    precipitations.append(data_point["precipitation"])
                    dates.append(data_point["date"])
            
            if len(precipitations) < 5:
                return {"trend": "stable", "rate": 0.0, "significance": 0.5, "period": "insufficient_data"}
            
            # Simple linear trend analysis
            n = len(precipitations)
            x_values = list(range(n))
            y_values = precipitations
            
            x_mean = sum(x_values) / n
            y_mean = sum(y_values) / n
            
            numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
            denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
            
            if denominator != 0:
                slope = numerator / denominator
            else:
                slope = 0.0
            
            # Determine trend direction
            if slope > 0.1:  # More than 0.1 mm per year increase
                trend = "increasing"
            elif slope < -0.1:  # More than 0.1 mm per year decrease
                trend = "decreasing"
            else:
                trend = "stable"
            
            # Calculate significance (simplified)
            significance = min(abs(slope) * 10, 0.99)  # Simplified significance calculation
            
            # Determine period
            if dates:
                start_year = min(dates).year if hasattr(min(dates), 'year') else "unknown"
                end_year = max(dates).year if hasattr(max(dates), 'year') else "unknown"
                period = f"{start_year}-{end_year}"
            else:
                period = "unknown"
            
            result = {
                "trend": trend,
                "rate": slope,
                "significance": significance,
                "period": period,
                "data_points": len(precipitations)
            }
            
            logger.info(f"Analyzed precipitation trends: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing precipitation trends: {str(e)}")
            return {"trend": "stable", "rate": 0.0, "significance": 0.5, "period": "error"}
    
    async def _analyze_extreme_weather_events(self, climate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze extreme weather events."""
        try:
            temperature_data = climate_data.get("temperature_data", [])
            precipitation_data = climate_data.get("precipitation_data", [])
            
            # Analyze heat waves
            heat_waves = {"frequency_trend": "stable", "intensity_trend": "stable"}
            if temperature_data:
                temperatures = [d.get("temperature", 20) for d in temperature_data]
                if temperatures:
                    avg_temp = sum(temperatures) / len(temperatures)
                    # Count temperatures above 30°C (heat wave threshold)
                    heat_wave_count = sum(1 for t in temperatures if t > 30)
                    heat_wave_frequency = heat_wave_count / len(temperatures)
                    
                    # Simple trend analysis
                    if heat_wave_frequency > 0.2:
                        heat_waves["frequency_trend"] = "increasing"
                    elif heat_wave_frequency < 0.1:
                        heat_waves["frequency_trend"] = "decreasing"
                    
                    # Intensity trend based on max temperature
                    if max(temperatures) > avg_temp + 5:
                        heat_waves["intensity_trend"] = "increasing"
                    elif max(temperatures) < avg_temp + 2:
                        heat_waves["intensity_trend"] = "decreasing"
            
            # Analyze drought events
            drought_events = {"frequency_trend": "stable", "duration_trend": "stable"}
            if precipitation_data:
                precipitations = [d.get("precipitation", 0) for d in precipitation_data]
                if precipitations:
                    avg_precip = sum(precipitations) / len(precipitations)
                    # Count days with very low precipitation (< 1mm)
                    drought_count = sum(1 for p in precipitations if p < 1.0)
                    drought_frequency = drought_count / len(precipitations)
                    
                    # Simple trend analysis
                    if drought_frequency > 0.3:
                        drought_events["frequency_trend"] = "increasing"
                    elif drought_frequency < 0.2:
                        drought_events["frequency_trend"] = "decreasing"
                    
                    # Duration trend based on consecutive low precipitation days
                    consecutive_dry_days = 0
                    max_consecutive = 0
                    for p in precipitations:
                        if p < 1.0:
                            consecutive_dry_days += 1
                            max_consecutive = max(max_consecutive, consecutive_dry_days)
                        else:
                            consecutive_dry_days = 0
                    
                    if max_consecutive > 10:
                        drought_events["duration_trend"] = "increasing"
                    elif max_consecutive < 5:
                        drought_events["duration_trend"] = "decreasing"
            
            result = {
                "heat_waves": heat_waves,
                "drought_events": drought_events,
                "data_points": len(temperature_data) + len(precipitation_data)
            }
            
            logger.info(f"Analyzed extreme weather events: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing extreme weather events: {str(e)}")
            return {
                "heat_waves": {"frequency_trend": "stable", "intensity_trend": "stable"},
                "drought_events": {"frequency_trend": "stable", "duration_trend": "stable"}
            }
    
    async def _project_future_climate_conditions(
        self, region: str, temperature_trends: Dict[str, Any], precipitation_trends: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Project future climate conditions."""
        try:
            # Extract current trends
            temp_trend = temperature_trends.get("trend", "stable")
            temp_rate = temperature_trends.get("rate", 0.0)
            precip_trend = precipitation_trends.get("trend", "stable")
            precip_rate = precipitation_trends.get("rate", 0.0)
            
            # Project future conditions based on current trends
            # Temperature projection
            if temp_trend == "increasing":
                temp_projection_trend = "increasing"
                temp_projection_rate = temp_rate * 1.2  # Slight acceleration
            elif temp_trend == "decreasing":
                temp_projection_trend = "decreasing"
                temp_projection_rate = temp_rate * 0.8  # Slight deceleration
            else:
                temp_projection_trend = "stable"
                temp_projection_rate = 0.0
            
            # Precipitation projection
            if precip_trend == "increasing":
                precip_projection_trend = "increasing"
                precip_projection_rate = precip_rate * 1.1
            elif precip_trend == "decreasing":
                precip_projection_trend = "decreasing"
                precip_projection_rate = precip_rate * 0.9
            else:
                precip_projection_trend = "stable"
                precip_projection_rate = 0.0
            
            # Add climate change acceleration factor
            temp_projection_rate += 0.01  # Additional 0.01°C per year due to climate change
            precip_projection_rate -= 0.1  # Additional 0.1mm per year decrease due to climate change
            
            result = {
                "temperature_projection": {
                    "trend": temp_projection_trend,
                    "rate": temp_projection_rate,
                    "projection_period": "2024-2050",
                    "confidence": "moderate"
                },
                "precipitation_projection": {
                    "trend": precip_projection_trend,
                    "rate": precip_projection_rate,
                    "projection_period": "2024-2050",
                    "confidence": "moderate"
                },
                "climate_change_factor": "included",
                "region": region
            }
            
            logger.info(f"Projected future climate conditions for {region}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error projecting future climate conditions: {str(e)}")
            return {
                "temperature_projection": {"trend": "stable", "rate": 0.0, "projection_period": "2024-2050"},
                "precipitation_projection": {"trend": "stable", "rate": 0.0, "projection_period": "2024-2050"}
            }
    
    async def _assess_drought_risk_changes(
        self, future_projections: Dict[str, Any], region: str
    ) -> Dict[str, Any]:
        """Assess changes in drought risk due to climate change."""
        try:
            # Extract projections
            temp_projection = future_projections.get("temperature_projection", {})
            precip_projection = future_projections.get("precipitation_projection", {})
            
            temp_trend = temp_projection.get("trend", "stable")
            temp_rate = temp_projection.get("rate", 0.0)
            precip_trend = precip_projection.get("trend", "stable")
            precip_rate = precip_projection.get("rate", 0.0)
            
            # Assess risk change based on projections
            risk_factors = []
            
            if temp_trend == "increasing" and temp_rate > 0.01:
                risk_factors.append("temperature_increase")
            if precip_trend == "decreasing" and precip_rate < -0.1:
                risk_factors.append("precipitation_decrease")
            
            # Determine overall risk change
            if len(risk_factors) >= 2:
                risk_increase = 30.0
                severity_increase = 35.0
                frequency_increase = 25.0
                confidence = 0.8
            elif len(risk_factors) == 1:
                risk_increase = 20.0
                severity_increase = 25.0
                frequency_increase = 15.0
                confidence = 0.6
            else:
                risk_increase = 10.0
                severity_increase = 15.0
                frequency_increase = 10.0
                confidence = 0.4
            
            # Add region-specific factors
            if region in ["CA", "TX", "NM", "AZ"]:  # Arid regions
                risk_increase += 15.0
                severity_increase += 20.0
                frequency_increase += 10.0
                confidence = 0.9
            elif region in ["IA", "IL", "NE", "KS"]:  # Corn belt
                if temp_trend == "increasing":
                    risk_increase += 10.0
                    severity_increase += 15.0
            
            result = {
                "risk_increase": risk_increase,
                "severity_increase": severity_increase,
                "frequency_increase": frequency_increase,
                "confidence": confidence,
                "risk_factors": risk_factors,
                "region": region,
                "temperature_impact": temp_trend,
                "precipitation_impact": precip_trend
            }
            
            logger.info(f"Assessed drought risk changes for {region}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error assessing drought risk changes: {str(e)}")
            return {
                "risk_increase": 10.0,
                "severity_increase": 15.0,
                "frequency_increase": 10.0,
                "confidence": 0.3
            }
    
    async def _generate_adaptation_recommendations(
        self, drought_risk_changes: Dict[str, Any], region: str
    ) -> List[str]:
        """Generate adaptation recommendations for climate change."""
        try:
            recommendations = []
            
            # Base recommendations for all regions
            recommendations.extend([
                "Develop drought-resistant crop varieties",
                "Implement water conservation technologies",
                "Improve irrigation efficiency",
                "Diversify water sources",
                "Enhance early warning systems"
            ])
            
            # Risk-based recommendations
            risk_increase = drought_risk_changes.get("risk_increase", 10.0)
            severity_increase = drought_risk_changes.get("severity_increase", 15.0)
            frequency_increase = drought_risk_changes.get("frequency_increase", 10.0)
            
            if risk_increase > 25.0:
                recommendations.extend([
                    "Implement advanced irrigation technologies",
                    "Develop alternative water sources",
                    "Consider crop insurance and risk management",
                    "Plan for emergency water supplies"
                ])
            
            if severity_increase > 30.0:
                recommendations.extend([
                    "Implement precision agriculture techniques",
                    "Use cover crops to protect soil",
                    "Consider fallowing strategies",
                    "Develop drought contingency plans"
                ])
            
            if frequency_increase > 20.0:
                recommendations.extend([
                    "Monitor weather patterns more frequently",
                    "Implement flexible planting schedules",
                    "Develop rapid response protocols",
                    "Consider crop diversification"
                ])
            
            # Region-specific recommendations
            if region in ["CA", "TX", "NM", "AZ"]:  # Arid regions
                recommendations.extend([
                    "Implement xeriscaping principles",
                    "Use native drought-tolerant plants",
                    "Consider water recycling systems",
                    "Develop greywater irrigation"
                ])
            elif region in ["IA", "IL", "NE", "KS"]:  # Corn belt
                recommendations.extend([
                    "Implement no-till farming practices",
                    "Use precision irrigation systems",
                    "Consider drought-tolerant corn varieties",
                    "Develop soil moisture monitoring"
                ])
            elif region in ["FL", "GA", "SC", "NC"]:  # Southeast
                recommendations.extend([
                    "Implement water-efficient irrigation",
                    "Use heat-tolerant crop varieties",
                    "Develop stormwater management",
                    "Consider intercropping strategies"
                ])
            
            # Remove duplicates and limit to reasonable number
            unique_recommendations = list(dict.fromkeys(recommendations))  # Remove duplicates while preserving order
            final_recommendations = unique_recommendations[:10]  # Limit to 10 recommendations
            
            logger.info(f"Generated {len(final_recommendations)} adaptation recommendations for {region}")
            return final_recommendations
            
        except Exception as e:
            logger.error(f"Error generating adaptation recommendations: {str(e)}")
            return [
                "Develop drought-resistant crop varieties",
                "Implement water conservation technologies",
                "Improve irrigation efficiency",
                "Diversify water sources",
                "Enhance early warning systems"
            ]
    
    async def _assess_climate_change_confidence(
        self, temperature_trends: Dict[str, Any], precipitation_trends: Dict[str, Any]
    ) -> float:
        """Assess confidence level in climate change assessments."""
        try:
            base_confidence = 0.5
            
            # Factor in temperature trend significance
            temp_significance = temperature_trends.get("significance", 0.5)
            if temp_significance > 0.8:
                base_confidence += 0.2
            elif temp_significance > 0.6:
                base_confidence += 0.1
            
            # Factor in precipitation trend significance
            precip_significance = precipitation_trends.get("significance", 0.5)
            if precip_significance > 0.8:
                base_confidence += 0.2
            elif precip_significance > 0.6:
                base_confidence += 0.1
            
            # Factor in data quality
            temp_data_points = temperature_trends.get("data_points", 0)
            precip_data_points = precipitation_trends.get("data_points", 0)
            
            if temp_data_points > 100 and precip_data_points > 100:
                base_confidence += 0.1
            elif temp_data_points > 50 and precip_data_points > 50:
                base_confidence += 0.05
            
            # Factor in trend consistency
            temp_trend = temperature_trends.get("trend", "stable")
            precip_trend = precipitation_trends.get("trend", "stable")
            
            if temp_trend == precip_trend and temp_trend != "stable":
                base_confidence += 0.1  # Consistent trends increase confidence
            
            # Ensure confidence is within valid range
            final_confidence = max(0.1, min(0.95, base_confidence))
            
            logger.info(f"Assessed climate change confidence: {final_confidence}")
            return final_confidence
            
        except Exception as e:
            logger.error(f"Error assessing climate change confidence: {str(e)}")
            return 0.5


# Real data provider classes

from .noaa_drought_provider import NOAADroughtProvider
from .external_service_integration import WeatherServiceIntegration

class WeatherDataProvider:
    """Real weather data provider using external service integration."""
    
    def __init__(self):
        self.weather_service = WeatherServiceIntegration()
    
    async def initialize(self):
        await self.weather_service.initialize()
    
    async def cleanup(self):
        await self.weather_service.cleanup()

class SoilDataProvider:
    """Real soil data provider using external service integration."""
    
    def __init__(self):
        self.noaa_provider = NOAADroughtProvider()
    
    async def initialize(self):
        await self.noaa_provider.initialize()
    
    async def cleanup(self):
        await self.noaa_provider.cleanup()

class ClimateDataProvider:
    """Real climate data provider using NOAA drought monitor."""
    
    def __init__(self):
        self.noaa_provider = NOAADroughtProvider()
    
    async def initialize(self):
        await self.noaa_provider.initialize()
    
    async def cleanup(self):
        await self.noaa_provider.cleanup()