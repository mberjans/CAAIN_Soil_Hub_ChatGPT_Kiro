"""
Comprehensive Drought Monitoring and Early Warning Service

Service for monitoring drought conditions, calculating drought indices,
integrating with NOAA data, and providing predictive alerts.
"""

import logging
import asyncio
import math
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta, date
from uuid import UUID
from decimal import Decimal
import numpy as np

from ..models.drought_models import (
    DroughtMonitoringRequest,
    DroughtMonitoringResponse,
    DroughtRiskLevel,
    SoilMoistureLevel
)

logger = logging.getLogger(__name__)

class DroughtMonitoringService:
    """Comprehensive drought monitoring and early warning service."""
    
    def __init__(self):
        self.monitoring_configs = {}
        self.alert_system = None
        self.noaa_provider = None
        self.weather_service = None
        self.soil_service = None
        self.satellite_service = None
        self.drought_indices_calculator = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the comprehensive drought monitoring service."""
        try:
            logger.info("Initializing Comprehensive Drought Monitoring Service...")
            
            # Initialize drought indices calculator
            self.drought_indices_calculator = DroughtIndicesCalculator()
            await self.drought_indices_calculator.initialize()
            
            # Initialize NOAA drought monitor provider
            self.noaa_provider = NOAADroughtProvider()
            await self.noaa_provider.initialize()
            
            # Initialize external service clients
            self.weather_service = WeatherServiceClient()
            self.soil_service = SoilServiceClient()
            self.satellite_service = SatelliteServiceClient()
            
            # Initialize alert system
            self.alert_system = ComprehensiveAlertSystem()
            await self.alert_system.initialize()
            
            self.initialized = True
            logger.info("Comprehensive Drought Monitoring Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Comprehensive Drought Monitoring Service: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up service resources."""
        try:
            logger.info("Cleaning up Drought Monitoring Service...")
            
            if self.alert_system:
                await self.alert_system.cleanup()
            
            self.initialized = False
            logger.info("Drought Monitoring Service cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def setup_monitoring(self, request: DroughtMonitoringRequest) -> DroughtMonitoringResponse:
        """
        Set up drought monitoring for a farm location.
        
        Args:
            request: Drought monitoring setup request
            
        Returns:
            Monitoring configuration and initial status
        """
        try:
            logger.info(f"Setting up drought monitoring for farm: {request.farm_location_id}")
            
            # Create monitoring configuration
            monitoring_config = await self._create_monitoring_config(request)
            
            # Store configuration
            self.monitoring_configs[str(request.farm_location_id)] = monitoring_config
            
            # Set up data collection
            await self._setup_data_collection(request)
            
            # Configure alerts
            await self._configure_alerts(request, monitoring_config)
            
            # Get initial monitoring data
            initial_data = await self._collect_initial_data(request)
            
            # Create response
            response = DroughtMonitoringResponse(
                monitoring_id=UUID(),
                farm_location_id=request.farm_location_id,
                status="active",
                active_alerts=[],
                monitoring_data=initial_data,
                next_check_time=datetime.utcnow() + timedelta(hours=1)
            )
            
            logger.info(f"Drought monitoring setup completed for farm: {request.farm_location_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error setting up drought monitoring: {str(e)}")
            raise
    
    async def get_monitoring_status(self, farm_location_id: UUID) -> DroughtMonitoringResponse:
        """
        Get current drought monitoring status for a farm location.
        
        Args:
            farm_location_id: Farm location identifier
            
        Returns:
            Current monitoring status and data
        """
        try:
            logger.info(f"Getting monitoring status for farm: {farm_location_id}")
            
            # Get monitoring configuration
            config = self.monitoring_configs.get(str(farm_location_id))
            if not config:
                raise ValueError(f"No monitoring configuration found for farm: {farm_location_id}")
            
            # Collect current data
            current_data = await self._collect_current_data(farm_location_id, config)
            
            # Check for alerts
            active_alerts = await self._check_alerts(farm_location_id, current_data, config)
            
            # Determine overall status
            status = await self._determine_monitoring_status(current_data, active_alerts)
            
            # Calculate next check time
            next_check_time = await self._calculate_next_check_time(config)
            
            response = DroughtMonitoringResponse(
                monitoring_id=UUID(),
                farm_location_id=farm_location_id,
                status=status,
                active_alerts=active_alerts,
                monitoring_data=current_data,
                next_check_time=next_check_time
            )
            
            logger.info(f"Monitoring status retrieved for farm: {farm_location_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error getting monitoring status: {str(e)}")
            raise
    
    async def get_drought_alerts(self, farm_location_id: UUID, alert_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get active drought alerts for a farm location.
        
        Args:
            farm_location_id: Farm location identifier
            alert_type: Optional filter by alert type
            
        Returns:
            List of active alerts
        """
        try:
            logger.info(f"Getting drought alerts for farm: {farm_location_id}")
            
            # Get current monitoring data
            status_response = await self.get_monitoring_status(farm_location_id)
            
            # Filter alerts by type if specified
            alerts = status_response.active_alerts
            if alert_type:
                alerts = [alert for alert in alerts if alert.get("type") == alert_type]
            
            logger.info(f"Retrieved {len(alerts)} alerts for farm: {farm_location_id}")
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting drought alerts: {str(e)}")
            raise
    
    async def calculate_drought_indices(self, farm_location_id: UUID, field_id: UUID) -> Dict[str, Any]:
        """
        Calculate comprehensive drought indices for monitoring.
        
        Args:
            farm_location_id: Farm location identifier
            field_id: Field identifier
            
        Returns:
            Dictionary containing drought indices (SPI, PDSI, SPEI)
        """
        try:
            logger.info(f"Calculating drought indices for field: {field_id}")
            
            # Get historical weather data
            weather_data = await self._get_historical_weather_data(farm_location_id, days=365)
            
            # Get soil moisture data
            soil_data = await self._get_soil_moisture_data(field_id, days=90)
            
            # Calculate Standardized Precipitation Index (SPI)
            spi_values = await self.drought_indices_calculator.calculate_spi(
                weather_data["precipitation"], 
                periods=[1, 3, 6, 12]  # 1-month, 3-month, 6-month, 12-month SPI
            )
            
            # Calculate Palmer Drought Severity Index (PDSI)
            pdsi_value = await self.drought_indices_calculator.calculate_pdsi(
                weather_data["precipitation"],
                weather_data["temperature"],
                soil_data["available_water_capacity"]
            )
            
            # Calculate Standardized Precipitation Evapotranspiration Index (SPEI)
            spei_values = await self.drought_indices_calculator.calculate_spei(
                weather_data["precipitation"],
                weather_data["potential_evapotranspiration"],
                periods=[1, 3, 6, 12]
            )
            
            # Calculate Vegetation Health Index (VHI) from satellite data
            vhi_value = await self._calculate_vegetation_health_index(field_id)
            
            # Compile results
            drought_indices = {
                "timestamp": datetime.utcnow(),
                "field_id": field_id,
                "spi": {
                    "1_month": spi_values[0],
                    "3_month": spi_values[1], 
                    "6_month": spi_values[2],
                    "12_month": spi_values[3]
                },
                "pdsi": pdsi_value,
                "spei": {
                    "1_month": spei_values[0],
                    "3_month": spei_values[1],
                    "6_month": spei_values[2], 
                    "12_month": spei_values[3]
                },
                "vegetation_health_index": vhi_value,
                "overall_drought_severity": await self._assess_overall_drought_severity(
                    spi_values, pdsi_value, spei_values, vhi_value
                )
            }
            
            logger.info(f"Drought indices calculated for field: {field_id}")
            return drought_indices
            
        except Exception as e:
            logger.error(f"Error calculating drought indices: {str(e)}")
            raise
    
    async def get_noaa_drought_data(self, farm_location_id: UUID) -> Dict[str, Any]:
        """
        Get NOAA drought monitor data for farm location.
        
        Args:
            farm_location_id: Farm location identifier
            
        Returns:
            NOAA drought monitor data
        """
        try:
            logger.info(f"Getting NOAA drought data for farm: {farm_location_id}")
            
            # Get farm coordinates
            coordinates = await self._get_farm_coordinates(farm_location_id)
            
            # Get NOAA drought monitor data
            noaa_data = await self.noaa_provider.get_drought_monitor_data(
                coordinates["latitude"],
                coordinates["longitude"]
            )
            
            # Process and enhance NOAA data
            enhanced_data = {
                "timestamp": datetime.utcnow(),
                "farm_location_id": farm_location_id,
                "noaa_drought_category": noaa_data.get("drought_category"),
                "drought_intensity": noaa_data.get("drought_intensity"),
                "affected_area_percent": noaa_data.get("affected_area_percent"),
                "drought_start_date": noaa_data.get("drought_start_date"),
                "drought_duration_weeks": noaa_data.get("drought_duration_weeks"),
                "confidence_level": noaa_data.get("confidence_level"),
                "data_source": "NOAA Drought Monitor",
                "last_updated": noaa_data.get("last_updated")
            }
            
            logger.info(f"NOAA drought data retrieved for farm: {farm_location_id}")
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error getting NOAA drought data: {str(e)}")
            raise
    
    async def generate_predictive_alerts(self, farm_location_id: UUID) -> List[Dict[str, Any]]:
        """
        Generate predictive drought alerts based on trends and forecasts.
        
        Args:
            farm_location_id: Farm location identifier
            
        Returns:
            List of predictive alerts
        """
        try:
            logger.info(f"Generating predictive alerts for farm: {farm_location_id}")
            
            alerts = []
            
            # Get current drought indices
            drought_indices = await self.calculate_drought_indices(farm_location_id, None)
            
            # Get weather forecast
            forecast = await self._get_weather_forecast(farm_location_id, days=14)
            
            # Analyze trends and generate alerts
            alerts.extend(await self._analyze_drought_trends(drought_indices, forecast))
            alerts.extend(await self._analyze_weather_patterns(forecast))
            alerts.extend(await self._analyze_soil_moisture_trends(farm_location_id))
            
            # Prioritize and filter alerts
            prioritized_alerts = await self._prioritize_alerts(alerts)
            
            logger.info(f"Generated {len(prioritized_alerts)} predictive alerts for farm: {farm_location_id}")
            return prioritized_alerts
            
        except Exception as e:
            logger.error(f"Error generating predictive alerts: {str(e)}")
            raise
    
    # Helper methods
    async def _create_monitoring_config(self, request: DroughtMonitoringRequest) -> Dict[str, Any]:
        """Create monitoring configuration from request."""
        return {
            "farm_location_id": request.farm_location_id,
            "field_ids": request.field_ids,
            "monitoring_frequency": request.monitoring_frequency,
            "alert_thresholds": request.alert_thresholds,
            "notification_preferences": request.notification_preferences,
            "integration_services": request.integration_services,
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        }
    
    async def _setup_data_collection(self, request: DroughtMonitoringRequest):
        """Set up data collection for monitoring."""
        logger.info(f"Setting up data collection for farm: {request.farm_location_id}")
        
        # In a real implementation, this would:
        # - Connect to soil moisture sensors
        # - Set up weather data feeds
        # - Configure crop monitoring systems
        # - Establish data collection schedules
        
        for field_id in request.field_ids:
            await self._setup_field_monitoring(field_id, request)
    
    async def _setup_field_monitoring(self, field_id: UUID, request: DroughtMonitoringRequest):
        """Set up monitoring for a specific field."""
        logger.info(f"Setting up field monitoring for field: {field_id}")
        
        # Configure field-specific monitoring parameters
        field_config = {
            "field_id": field_id,
            "soil_moisture_sensors": await self._get_soil_moisture_sensors(field_id),
            "weather_station": await self._get_weather_station(field_id),
            "crop_monitoring": await self._get_crop_monitoring_setup(field_id),
            "data_collection_schedule": self._get_collection_schedule(request.monitoring_frequency)
        }
        
        return field_config
    
    async def _configure_alerts(self, request: DroughtMonitoringRequest, config: Dict[str, Any]):
        """Configure alert system for monitoring."""
        logger.info(f"Configuring alerts for farm: {request.farm_location_id}")
        
        # Set up alert thresholds
        default_thresholds = {
            "soil_moisture_low": 30.0,  # Percentage
            "soil_moisture_critical": 20.0,
            "temperature_high": 35.0,  # Celsius
            "precipitation_low": 5.0,  # mm per week
            "drought_risk_high": 0.7,  # Risk score
            "crop_stress": 0.6  # Stress score
        }
        
        # Merge with user-defined thresholds
        alert_thresholds = {**default_thresholds, **request.alert_thresholds}
        
        # Configure alert system
        await self.alert_system.configure_alerts(
            request.farm_location_id,
            alert_thresholds,
            request.notification_preferences
        )
    
    async def _collect_initial_data(self, request: DroughtMonitoringRequest) -> Dict[str, Any]:
        """Collect initial monitoring data."""
        logger.info(f"Collecting initial data for farm: {request.farm_location_id}")
        
        initial_data = {
            "timestamp": datetime.utcnow(),
            "farm_location_id": request.farm_location_id,
            "fields": {}
        }
        
        for field_id in request.field_ids:
            field_data = await self._collect_field_data(field_id)
            initial_data["fields"][str(field_id)] = field_data
        
        # Add farm-level data
        initial_data["farm_level"] = await self._collect_farm_level_data(request.farm_location_id)
        
        return initial_data
    
    async def _collect_current_data(self, farm_location_id: UUID, config: Dict[str, Any]) -> Dict[str, Any]:
        """Collect current monitoring data."""
        logger.info(f"Collecting current data for farm: {farm_location_id}")
        
        current_data = {
            "timestamp": datetime.utcnow(),
            "farm_location_id": farm_location_id,
            "fields": {}
        }
        
        for field_id in config["field_ids"]:
            field_data = await self._collect_field_data(field_id)
            current_data["fields"][str(field_id)] = field_data
        
        # Add farm-level data
        current_data["farm_level"] = await self._collect_farm_level_data(farm_location_id)
        
        return current_data
    
    async def _collect_field_data(self, field_id: UUID) -> Dict[str, Any]:
        """Collect data for a specific field."""
        # In a real implementation, this would query actual sensors and data sources
        return {
            "field_id": field_id,
            "soil_moisture": {
                "surface_percent": 45.0,
                "deep_percent": 60.0,
                "available_water_capacity": 2.5,
                "trend": "decreasing"
            },
            "weather": {
                "temperature": 28.5,
                "humidity": 65.0,
                "precipitation_24h": 0.0,
                "wind_speed": 8.2
            },
            "crop_health": {
                "stress_level": 0.3,
                "growth_stage": "V6",
                "health_score": 7.5
            },
            "drought_indicators": {
                "risk_score": 0.4,
                "risk_level": "moderate",
                "days_until_critical": 7
            }
        }
    
    async def _collect_farm_level_data(self, farm_location_id: UUID) -> Dict[str, Any]:
        """Collect farm-level monitoring data."""
        return {
            "farm_location_id": farm_location_id,
            "overall_drought_risk": {
                "risk_level": "moderate",
                "risk_score": 0.4,
                "trend": "stable"
            },
            "weather_summary": {
                "temperature_avg": 26.8,
                "precipitation_7d": 12.5,
                "humidity_avg": 68.0,
                "wind_avg": 7.5
            },
            "soil_conditions": {
                "avg_moisture": 52.5,
                "moisture_trend": "decreasing",
                "critical_fields": 0
            },
            "crop_conditions": {
                "avg_health_score": 7.2,
                "stress_level": 0.3,
                "fields_at_risk": 1
            }
        }
    
    async def _check_alerts(self, farm_location_id: UUID, current_data: Dict[str, Any], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for active alerts based on current data."""
        alerts = []
        
        # Check soil moisture alerts
        for field_id, field_data in current_data["fields"].items():
            soil_moisture = field_data["soil_moisture"]["surface_percent"]
            
            if soil_moisture < config["alert_thresholds"].get("soil_moisture_critical", 20.0):
                alerts.append({
                    "type": "soil_moisture_critical",
                    "field_id": field_id,
                    "severity": "high",
                    "message": f"Critical soil moisture level: {soil_moisture}%",
                    "recommendation": "Immediate irrigation required",
                    "timestamp": datetime.utcnow()
                })
            elif soil_moisture < config["alert_thresholds"].get("soil_moisture_low", 30.0):
                alerts.append({
                    "type": "soil_moisture_low",
                    "field_id": field_id,
                    "severity": "medium",
                    "message": f"Low soil moisture level: {soil_moisture}%",
                    "recommendation": "Consider irrigation or conservation practices",
                    "timestamp": datetime.utcnow()
                })
        
        # Check weather alerts
        farm_weather = current_data["farm_level"]["weather_summary"]
        if farm_weather["temperature_avg"] > config["alert_thresholds"].get("temperature_high", 35.0):
            alerts.append({
                "type": "temperature_high",
                "severity": "medium",
                "message": f"High temperature: {farm_weather['temperature_avg']}°C",
                "recommendation": "Monitor crop stress and consider irrigation",
                "timestamp": datetime.utcnow()
            })
        
        # Check drought risk alerts
        drought_risk = current_data["farm_level"]["overall_drought_risk"]["risk_score"]
        if drought_risk > config["alert_thresholds"].get("drought_risk_high", 0.7):
            alerts.append({
                "type": "drought_risk_high",
                "severity": "high",
                "message": f"High drought risk: {drought_risk:.1f}",
                "recommendation": "Implement drought mitigation measures",
                "timestamp": datetime.utcnow()
            })
        
        return alerts
    
    async def _determine_monitoring_status(self, current_data: Dict[str, Any], active_alerts: List[Dict[str, Any]]) -> str:
        """Determine overall monitoring status."""
        if not active_alerts:
            return "healthy"
        
        high_severity_alerts = [alert for alert in active_alerts if alert.get("severity") == "high"]
        if high_severity_alerts:
            return "critical"
        
        medium_severity_alerts = [alert for alert in active_alerts if alert.get("severity") == "medium"]
        if medium_severity_alerts:
            return "warning"
        
        return "healthy"
    
    async def _calculate_next_check_time(self, config: Dict[str, Any]) -> datetime:
        """Calculate next monitoring check time."""
        frequency = config["monitoring_frequency"]
        
        if frequency == "continuous":
            return datetime.utcnow() + timedelta(minutes=15)
        elif frequency == "hourly":
            return datetime.utcnow() + timedelta(hours=1)
        elif frequency == "daily":
            return datetime.utcnow() + timedelta(days=1)
        else:
            return datetime.utcnow() + timedelta(hours=6)  # Default
    
    async def _get_soil_moisture_sensors(self, field_id: UUID) -> List[Dict[str, Any]]:
        """Get soil moisture sensors for a field."""
        # In a real implementation, this would query sensor database
        return [
            {
                "sensor_id": f"sensor_{field_id}_surface",
                "depth_cm": 10,
                "status": "active",
                "last_reading": datetime.utcnow()
            },
            {
                "sensor_id": f"sensor_{field_id}_deep",
                "depth_cm": 30,
                "status": "active",
                "last_reading": datetime.utcnow()
            }
        ]
    
    async def _get_weather_station(self, field_id: UUID) -> Dict[str, Any]:
        """Get weather station for a field."""
        # In a real implementation, this would query weather station database
        return {
            "station_id": f"weather_{field_id}",
            "status": "active",
            "last_reading": datetime.utcnow(),
            "capabilities": ["temperature", "humidity", "precipitation", "wind"]
        }
    
    async def _get_crop_monitoring_setup(self, field_id: UUID) -> Dict[str, Any]:
        """Get crop monitoring setup for a field."""
        # In a real implementation, this would query crop monitoring systems
        return {
            "monitoring_type": "satellite_imagery",
            "frequency": "weekly",
            "last_update": datetime.utcnow(),
            "indicators": ["NDVI", "crop_health", "stress_level"]
        }
    
    def _get_collection_schedule(self, frequency: str) -> Dict[str, Any]:
        """Get data collection schedule based on frequency."""
        schedules = {
            "continuous": {"interval_minutes": 15, "retention_days": 7},
            "hourly": {"interval_minutes": 60, "retention_days": 30},
            "daily": {"interval_minutes": 1440, "retention_days": 365},
            "weekly": {"interval_minutes": 10080, "retention_days": 1095}
        }
        return schedules.get(frequency, schedules["daily"])
    
    # Enhanced helper methods for comprehensive monitoring
    async def _get_historical_weather_data(self, farm_location_id: UUID, days: int) -> Dict[str, Any]:
        """Get historical weather data for drought index calculations."""
        # In a real implementation, this would query weather service
        return {
            "precipitation": [10.5, 8.2, 12.1, 5.8, 15.3, 7.9, 9.4, 11.2],  # Mock data
            "temperature": [22.5, 24.1, 26.8, 28.3, 25.9, 23.7, 21.4, 19.8],
            "potential_evapotranspiration": [4.2, 4.8, 5.1, 5.6, 4.9, 4.3, 3.8, 3.2]
        }
    
    async def _get_soil_moisture_data(self, field_id: UUID, days: int) -> Dict[str, Any]:
        """Get soil moisture data for drought assessment."""
        # In a real implementation, this would query soil service
        return {
            "available_water_capacity": 2.5,
            "field_capacity": 0.35,
            "wilting_point": 0.15,
            "current_moisture": 0.25
        }
    
    async def _calculate_vegetation_health_index(self, field_id: UUID) -> float:
        """Calculate vegetation health index from satellite data."""
        # In a real implementation, this would query satellite service
        return 0.75  # Mock VHI value (0-1 scale)
    
    async def _assess_overall_drought_severity(self, spi_values: List[float], pdsi_value: float, 
                                             spei_values: List[float], vhi_value: float) -> str:
        """Assess overall drought severity based on multiple indices."""
        # Weighted assessment of drought severity
        spi_avg = sum(spi_values) / len(spi_values)
        spei_avg = sum(spei_values) / len(spei_values)
        
        # Calculate composite drought score
        drought_score = (spi_avg * 0.3 + pdsi_value * 0.3 + spei_avg * 0.3 + vhi_value * 0.1)
        
        if drought_score < -2.0:
            return "extreme"
        elif drought_score < -1.5:
            return "severe"
        elif drought_score < -1.0:
            return "moderate"
        elif drought_score < -0.5:
            return "mild"
        else:
            return "normal"
    
    async def _get_farm_coordinates(self, farm_location_id: UUID) -> Dict[str, float]:
        """Get farm coordinates for NOAA data lookup."""
        # In a real implementation, this would query location service
        return {"latitude": 40.7128, "longitude": -74.0060}  # Mock coordinates
    
    async def _get_weather_forecast(self, farm_location_id: UUID, days: int) -> Dict[str, Any]:
        """Get weather forecast for predictive analysis."""
        # In a real implementation, this would query weather service
        return {
            "precipitation_forecast": [0.0, 2.5, 0.0, 0.0, 8.2, 0.0, 0.0],
            "temperature_forecast": [28.5, 30.2, 32.1, 29.8, 26.4, 24.7, 22.9],
            "humidity_forecast": [45.0, 52.0, 38.0, 41.0, 68.0, 72.0, 75.0]
        }
    
    async def _analyze_drought_trends(self, drought_indices: Dict[str, Any], forecast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze drought trends and generate alerts."""
        alerts = []
        
        # Check SPI trends
        spi_3m = drought_indices["spi"]["3_month"]
        if spi_3m < -1.5:
            alerts.append({
                "type": "drought_trend_warning",
                "severity": "high",
                "message": f"3-month SPI indicates severe drought conditions: {spi_3m:.2f}",
                "recommendation": "Implement immediate drought mitigation measures",
                "timestamp": datetime.utcnow()
            })
        
        return alerts
    
    async def _analyze_weather_patterns(self, forecast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze weather patterns for drought risk."""
        alerts = []
        
        # Check precipitation forecast
        avg_precip = sum(forecast["precipitation_forecast"]) / len(forecast["precipitation_forecast"])
        if avg_precip < 1.0:  # Less than 1mm average per day
            alerts.append({
                "type": "low_precipitation_forecast",
                "severity": "medium",
                "message": f"Low precipitation forecast: {avg_precip:.1f}mm/day average",
                "recommendation": "Monitor soil moisture closely and prepare irrigation",
                "timestamp": datetime.utcnow()
            })
        
        return alerts
    
    async def _analyze_soil_moisture_trends(self, farm_location_id: UUID) -> List[Dict[str, Any]]:
        """Analyze soil moisture trends."""
        alerts = []
        
        # In a real implementation, this would analyze actual soil moisture trends
        alerts.append({
            "type": "soil_moisture_declining",
            "severity": "medium",
            "message": "Soil moisture levels declining over past week",
            "recommendation": "Consider irrigation or conservation practices",
            "timestamp": datetime.utcnow()
        })
        
        return alerts
    
    async def _prioritize_alerts(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize alerts by severity and urgency."""
        # Sort by severity (high > medium > low)
        severity_order = {"high": 3, "medium": 2, "low": 1}
        return sorted(alerts, key=lambda x: severity_order.get(x.get("severity", "low"), 1), reverse=True)
    
    async def _get_historical_trends(self, farm_location_id: UUID, days_back: int) -> Dict[str, Any]:
        """Get historical trends for dashboard."""
        # In a real implementation, this would query historical data
        return {
            "drought_indices_trend": {
                "spi_3m": [-0.5, -0.8, -1.2, -1.5, -1.3],  # Mock trend data
                "pdsi": [-0.3, -0.7, -1.1, -1.4, -1.2],
                "spei_3m": [-0.4, -0.6, -1.0, -1.3, -1.1]
            },
            "soil_moisture_trend": {
                "surface": [45.0, 42.0, 38.0, 35.0, 32.0],
                "deep": [60.0, 58.0, 55.0, 52.0, 48.0]
            },
            "weather_trend": {
                "precipitation": [5.2, 3.8, 2.1, 1.5, 0.8],
                "temperature": [22.5, 24.1, 26.8, 28.3, 29.1]
            },
            "period_days": days_back,
            "data_points": min(days_back, 30)  # Limit to 30 data points
        }


class DroughtIndicesCalculator:
    """Calculator for drought indices (SPI, PDSI, SPEI)."""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize the drought indices calculator."""
        self.initialized = True
        logger.info("Drought Indices Calculator initialized")
    
    async def calculate_spi(self, precipitation_data: List[float], periods: List[int]) -> List[float]:
        """Calculate Standardized Precipitation Index (SPI)."""
        spi_values = []
        
        for period in periods:
            if len(precipitation_data) >= period:
                # Calculate running sum for the period
                period_sum = sum(precipitation_data[-period:])
                
                # Calculate SPI (simplified calculation)
                # In a real implementation, this would use proper statistical methods
                mean_precip = 100.0  # Historical mean (mock)
                std_precip = 25.0    # Historical std dev (mock)
                
                spi = (period_sum - mean_precip) / std_precip
                spi_values.append(spi)
            else:
                spi_values.append(0.0)
        
        return spi_values
    
    async def calculate_pdsi(self, precipitation: List[float], temperature: List[float], 
                           available_water_capacity: float) -> float:
        """Calculate Palmer Drought Severity Index (PDSI)."""
        # Simplified PDSI calculation
        # In a real implementation, this would use the full Palmer algorithm
        
        avg_precip = sum(precipitation) / len(precipitation)
        avg_temp = sum(temperature) / len(temperature)
        
        # Simplified PDSI calculation
        pdsi = (avg_precip - 100.0) / 25.0 - (avg_temp - 20.0) / 5.0
        return pdsi
    
    async def calculate_spei(self, precipitation: List[float], pet_data: List[float], 
                           periods: List[int]) -> List[float]:
        """Calculate Standardized Precipitation Evapotranspiration Index (SPEI)."""
        spei_values = []
        
        for period in periods:
            if len(precipitation) >= period and len(pet_data) >= period:
                # Calculate water balance (precipitation - PET)
                precip_sum = sum(precipitation[-period:])
                pet_sum = sum(pet_data[-period:])
                water_balance = precip_sum - pet_sum
                
                # Calculate SPEI (simplified)
                mean_balance = 50.0  # Historical mean (mock)
                std_balance = 20.0   # Historical std dev (mock)
                
                spei = (water_balance - mean_balance) / std_balance
                spei_values.append(spei)
            else:
                spei_values.append(0.0)
        
        return spei_values


class NOAADroughtProvider:
    """Provider for NOAA drought monitor data."""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize NOAA provider."""
        self.initialized = True
        logger.info("NOAA Drought Provider initialized")
    
    async def get_drought_monitor_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get NOAA drought monitor data for coordinates."""
        # In a real implementation, this would query NOAA APIs
        return {
            "drought_category": "D1 - Moderate Drought",
            "drought_intensity": 0.3,
            "affected_area_percent": 15.2,
            "drought_start_date": "2024-01-15",
            "drought_duration_weeks": 8,
            "confidence_level": 0.85,
            "last_updated": datetime.utcnow()
        }


class WeatherServiceClient:
    """Client for weather service integration."""
    pass


class SoilServiceClient:
    """Client for soil service integration."""
    pass


class SatelliteServiceClient:
    """Client for satellite data integration."""
    pass


class ComprehensiveAlertSystem:
    """Comprehensive alert system for drought monitoring."""
    
    def __init__(self):
        self.alert_configs = {}
        self.notification_service = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the comprehensive alert system."""
        logger.info("Initializing Comprehensive Alert System...")
        self.notification_service = NotificationService()
        await self.notification_service.initialize()
        self.initialized = True
        logger.info("Comprehensive Alert System initialized successfully")
    
    async def cleanup(self):
        """Clean up alert system resources."""
        if self.notification_service:
            await self.notification_service.cleanup()
        self.initialized = False
    
    async def configure_alerts(self, farm_location_id: UUID, thresholds: Dict[str, float], 
                             notification_preferences: Dict[str, Any]):
        """Configure comprehensive alerts for a farm location."""
        self.alert_configs[str(farm_location_id)] = {
            "thresholds": thresholds,
            "notification_preferences": notification_preferences,
            "created_at": datetime.utcnow(),
            "alert_history": []
        }
    
    async def send_alert(self, farm_location_id: UUID, alert: Dict[str, Any]):
        """Send comprehensive alert notification."""
        config = self.alert_configs.get(str(farm_location_id))
        if config and self.notification_service:
            # Add to alert history
            config["alert_history"].append(alert)
            
            # Send notification
            await self.notification_service.send_notification(
                farm_location_id,
                alert,
                config["notification_preferences"]
            )


class NotificationService:
    """Enhanced notification service for alerts."""
    
    def __init__(self):
        self.initialized = False
        self.email_service = None
        self.sms_service = None
        self.push_service = None
    
    async def initialize(self):
        """Initialize notification service."""
        # In a real implementation, these would connect to actual services
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.push_service = PushNotificationService()
        
        self.initialized = True
        logger.info("Enhanced Notification Service initialized")
    
    async def cleanup(self):
        """Clean up notification service."""
        self.initialized = False
    
    async def send_notification(self, farm_location_id: UUID, alert: Dict[str, Any], 
                              preferences: Dict[str, Any]):
        """Send comprehensive notification for an alert."""
        try:
            # Determine notification channels based on alert severity
            channels = self._determine_notification_channels(alert, preferences)
            
            # Send notifications through appropriate channels
            for channel in channels:
                if channel == "email" and self.email_service:
                    await self.email_service.send_alert_email(farm_location_id, alert)
                elif channel == "sms" and self.sms_service:
                    await self.sms_service.send_alert_sms(farm_location_id, alert)
                elif channel == "push" and self.push_service:
                    await self.push_service.send_push_notification(farm_location_id, alert)
            
            logger.info(f"Alert notification sent for farm {farm_location_id}: {alert['message']}")
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
    
    def _determine_notification_channels(self, alert: Dict[str, Any], preferences: Dict[str, Any]) -> List[str]:
        """Determine which notification channels to use based on alert severity."""
        channels = []
        severity = alert.get("severity", "low")
        
        # High severity alerts use all channels
        if severity == "high":
            channels = ["email", "sms", "push"]
        elif severity == "medium":
            channels = ["email", "push"]
        else:
            channels = ["push"]
        
        # Respect user preferences
        enabled_channels = preferences.get("enabled_channels", channels)
        return [ch for ch in channels if ch in enabled_channels]


class EmailService:
    """Email notification service."""
    async def send_alert_email(self, farm_location_id: UUID, alert: Dict[str, Any]):
        logger.info(f"Sending email alert for farm {farm_location_id}: {alert['message']}")


class SMSService:
    """SMS notification service."""
    async def send_alert_sms(self, farm_location_id: UUID, alert: Dict[str, Any]):
        logger.info(f"Sending SMS alert for farm {farm_location_id}: {alert['message']}")


class PushNotificationService:
    """Push notification service."""
    async def send_push_notification(self, farm_location_id: UUID, alert: Dict[str, Any]):
        logger.info(f"Sending push notification for farm {farm_location_id}: {alert['message']}")


# Legacy AlertSystem class for backward compatibility
class AlertSystem:
    """Legacy alert system for backward compatibility."""
    
    def __init__(self):
        self.alert_configs = {}
        self.notification_service = None
    
    async def initialize(self):
        """Initialize the alert system."""
        logger.info("Initializing Alert System...")
        self.notification_service = NotificationService()
        await self.notification_service.initialize()
    
    async def cleanup(self):
        """Clean up alert system resources."""
        if self.notification_service:
            await self.notification_service.cleanup()
    
    async def configure_alerts(self, farm_location_id: UUID, thresholds: Dict[str, float], 
                             notification_preferences: Dict[str, Any]):
        """Configure alerts for a farm location."""
        self.alert_configs[str(farm_location_id)] = {
            "thresholds": thresholds,
            "notification_preferences": notification_preferences,
            "created_at": datetime.utcnow()
        }
    
    async def send_alert(self, farm_location_id: UUID, alert: Dict[str, Any]):
        """Send alert notification."""
        config = self.alert_configs.get(str(farm_location_id))
        if config and self.notification_service:
            await self.notification_service.send_notification(
                farm_location_id,
                alert,
                config["notification_preferences"]
            )
    