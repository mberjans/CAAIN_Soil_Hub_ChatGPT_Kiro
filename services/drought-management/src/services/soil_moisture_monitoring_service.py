"""
Soil Moisture Monitoring Service

Service for monitoring soil moisture levels, predicting moisture deficits,
and providing irrigation recommendations based on weather data, soil characteristics,
and crop water requirements.
"""

import logging
import math
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from uuid import UUID
from decimal import Decimal

from ..models.drought_models import (
    SoilMoistureStatus,
    SoilMoistureLevel,
    DroughtRiskLevel
)

logger = logging.getLogger(__name__)

class SoilMoistureMonitoringService:
    """Service for soil moisture monitoring and prediction."""
    
    def __init__(self):
        self.weather_service = None
        self.crop_service = None
        self.field_service = None
        self.initialized = False
        
        # Soil moisture monitoring configurations
        self.monitoring_configs = {}
        self.prediction_models = {}
        
        # Water balance model parameters
        self.water_balance_params = {
            "field_capacity": 0.35,  # Default field capacity (35% moisture)
            "wilting_point": 0.15,   # Default wilting point (15% moisture)
            "saturation_point": 0.45, # Default saturation point (45% moisture)
            "soil_depth_cm": 100,    # Default soil depth (100 cm)
            "bulk_density": 1.3      # Default bulk density (g/cm³)
        }
    
    async def initialize(self):
        """Initialize the soil moisture monitoring service."""
        try:
            logger.info("Initializing Soil Moisture Monitoring Service...")
            
            # Initialize external service connections
            await self._initialize_external_services()
            
            # Load prediction models
            await self._load_prediction_models()
            
            # Initialize monitoring configurations
            await self._initialize_monitoring_configs()
            
            self.initialized = True
            logger.info("Soil Moisture Monitoring Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Soil Moisture Monitoring Service: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up service resources."""
        try:
            logger.info("Cleaning up Soil Moisture Monitoring Service...")
            
            # Clean up external service connections
            await self._cleanup_external_services()
            
            self.initialized = False
            logger.info("Soil Moisture Monitoring Service cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def setup_field_monitoring(self, field_id: UUID, soil_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set up soil moisture monitoring for a specific field.
        
        Args:
            field_id: Field identifier
            soil_characteristics: Soil properties and characteristics
            
        Returns:
            Monitoring configuration for the field
        """
        try:
            logger.info(f"Setting up soil moisture monitoring for field: {field_id}")
            
            # Create field-specific monitoring configuration
            config = await self._create_field_config(field_id, soil_characteristics)
            
            # Store configuration
            self.monitoring_configs[str(field_id)] = config
            
            # Initialize prediction models for this field
            await self._initialize_field_models(field_id, soil_characteristics)
            
            logger.info(f"Soil moisture monitoring setup completed for field: {field_id}")
            return config
            
        except Exception as e:
            logger.error(f"Error setting up field monitoring: {str(e)}")
            raise
    
    async def get_current_moisture_status(self, field_id: UUID) -> SoilMoistureStatus:
        """
        Get current soil moisture status for a field.
        
        Args:
            field_id: Field identifier
            
        Returns:
            Current soil moisture status
        """
        try:
            logger.info(f"Getting current moisture status for field: {field_id}")
            
            # Get field configuration
            config = self.monitoring_configs.get(str(field_id))
            if not config:
                raise ValueError(f"No monitoring configuration found for field: {field_id}")
            
            # Collect current moisture data
            moisture_data = await self._collect_current_moisture_data(field_id, config)
            
            # Calculate moisture levels
            surface_moisture = moisture_data["surface_moisture_percent"]
            deep_moisture = moisture_data["deep_moisture_percent"]
            available_water = moisture_data["available_water_capacity"]
            
            # Determine overall moisture level
            moisture_level = self._determine_moisture_level(surface_moisture, deep_moisture)
            
            # Generate irrigation recommendation
            irrigation_recommendation = await self._generate_irrigation_recommendation(
                field_id, moisture_data, config
            )
            
            # Calculate days until critical moisture level
            days_until_critical = await self._calculate_days_until_critical(
                field_id, moisture_data, config
            )
            
            status = SoilMoistureStatus(
                field_id=field_id,
                assessment_date=datetime.utcnow(),
                surface_moisture_percent=surface_moisture,
                deep_moisture_percent=deep_moisture,
                available_water_capacity=available_water,
                moisture_level=moisture_level,
                irrigation_recommendation=irrigation_recommendation,
                days_until_critical=days_until_critical
            )
            
            logger.info(f"Moisture status retrieved for field: {field_id}")
            return status
            
        except Exception as e:
            logger.error(f"Error getting moisture status: {str(e)}")
            raise
    
    async def predict_moisture_deficit(self, field_id: UUID, forecast_days: int = 7) -> Dict[str, Any]:
        """
        Predict soil moisture deficit over the forecast period.
        
        Args:
            field_id: Field identifier
            forecast_days: Number of days to forecast
            
        Returns:
            Moisture deficit prediction
        """
        try:
            logger.info(f"Predicting moisture deficit for field: {field_id}, days: {forecast_days}")
            
            # Get field configuration
            config = self.monitoring_configs.get(str(field_id))
            if not config:
                raise ValueError(f"No monitoring configuration found for field: {field_id}")
            
            # Get current moisture status
            current_status = await self.get_current_moisture_status(field_id)
            
            # Get weather forecast
            weather_forecast = await self._get_weather_forecast(field_id, forecast_days)
            
            # Get crop water requirements
            crop_requirements = await self._get_crop_water_requirements(field_id, forecast_days)
            
            # Run water balance model
            moisture_prediction = await self._run_water_balance_model(
                field_id, current_status, weather_forecast, crop_requirements, config
            )
            
            # Calculate deficit predictions
            deficit_prediction = await self._calculate_deficit_prediction(
                moisture_prediction, config
            )
            
            logger.info(f"Moisture deficit prediction completed for field: {field_id}")
            return deficit_prediction
            
        except Exception as e:
            logger.error(f"Error predicting moisture deficit: {str(e)}")
            raise
    
    async def calculate_evapotranspiration(self, field_id: UUID, date: datetime) -> Dict[str, Any]:
        """
        Calculate evapotranspiration for a field on a specific date.
        
        Args:
            field_id: Field identifier
            date: Date for calculation
            
        Returns:
            Evapotranspiration calculation results
        """
        try:
            logger.info(f"Calculating evapotranspiration for field: {field_id}, date: {date}")
            
            # Get field configuration
            config = self.monitoring_configs.get(str(field_id))
            if not config:
                raise ValueError(f"No monitoring configuration found for field: {field_id}")
            
            # Get weather data for the date
            weather_data = await self._get_weather_data(field_id, date)
            
            # Get crop data
            crop_data = await self._get_crop_data(field_id, date)
            
            # Calculate reference evapotranspiration (ET₀) using Penman-Monteith equation
            et0 = await self._calculate_reference_et(weather_data)
            
            # Calculate crop coefficient (Kc)
            kc = await self._calculate_crop_coefficient(crop_data, date)
            
            # Calculate actual evapotranspiration (ETc)
            etc = et0 * kc
            
            # Calculate soil evaporation component
            soil_evaporation = await self._calculate_soil_evaporation(
                weather_data, config["soil_characteristics"]
            )
            
            result = {
                "field_id": field_id,
                "date": date,
                "reference_et_mm": et0,
                "crop_coefficient": kc,
                "crop_et_mm": etc,
                "soil_evaporation_mm": soil_evaporation,
                "total_et_mm": etc + soil_evaporation,
                "weather_data": weather_data,
                "crop_data": crop_data
            }
            
            logger.info(f"Evapotranspiration calculation completed for field: {field_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating evapotranspiration: {str(e)}")
            raise
    
    async def get_irrigation_recommendations(self, field_id: UUID) -> Dict[str, Any]:
        """
        Get irrigation recommendations for a field.
        
        Args:
            field_id: Field identifier
            
        Returns:
            Irrigation recommendations
        """
        try:
            logger.info(f"Getting irrigation recommendations for field: {field_id}")
            
            # Get current moisture status
            current_status = await self.get_current_moisture_status(field_id)
            
            # Get field configuration
            config = self.monitoring_configs.get(str(field_id))
            
            # Get weather forecast
            weather_forecast = await self._get_weather_forecast(field_id, 7)
            
            # Get crop data
            crop_data = await self._get_crop_data(field_id, datetime.utcnow())
            
            # Calculate irrigation needs
            irrigation_needs = await self._calculate_irrigation_needs(
                current_status, weather_forecast, crop_data, config
            )
            
            # Generate recommendations
            recommendations = await self._generate_irrigation_recommendations(
                irrigation_needs, config
            )
            
            logger.info(f"Irrigation recommendations generated for field: {field_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting irrigation recommendations: {str(e)}")
            raise
    
    async def get_moisture_alerts(self, field_id: UUID) -> List[Dict[str, Any]]:
        """
        Get moisture-related alerts for a field.
        
        Args:
            field_id: Field identifier
            
        Returns:
            List of moisture alerts
        """
        try:
            logger.info(f"Getting moisture alerts for field: {field_id}")
            
            # Initialize alert service if not already done
            if not hasattr(self, 'alert_service'):
                from .soil_moisture_alert_service import SoilMoistureAlertService
                self.alert_service = SoilMoistureAlertService()
                await self.alert_service.initialize()
            
            # Get current moisture status
            current_status = await self.get_current_moisture_status(field_id)
            
            # Get field configuration
            config = self.monitoring_configs.get(str(field_id))
            
            # Prepare moisture data for alert evaluation
            moisture_data = {
                "surface_moisture_percent": current_status.surface_moisture_percent,
                "deep_moisture_percent": current_status.deep_moisture_percent,
                "available_water_capacity": current_status.available_water_capacity,
                "trend": "stable",  # Would be calculated from historical data
                "timestamp": datetime.utcnow()
            }
            
            # Evaluate alerts using the advanced alert service
            alerts = await self.alert_service.evaluate_moisture_alerts(
                field_id, moisture_data, config
            )
            
            # Convert alerts to dictionary format for API response
            alert_dicts = [alert.to_dict() for alert in alerts]
            
            logger.info(f"Retrieved {len(alert_dicts)} moisture alerts for field: {field_id}")
            return alert_dicts
            
        except Exception as e:
            logger.error(f"Error getting moisture alerts: {str(e)}")
            raise
    
    # Helper methods
    async def _initialize_external_services(self):
        """Initialize connections to external services."""
        logger.info("Initializing external service connections...")
        
        # Initialize real external service integrations
        from .external_service_integration import ExternalServiceManager
        self.external_services = ExternalServiceManager()
        await self.external_services.initialize()
        
        # Set up service references for backward compatibility
        self.weather_service = self.external_services.weather_service
        self.crop_service = self.external_services.crop_service
        self.field_service = self.external_services.field_service
    
    async def _cleanup_external_services(self):
        """Clean up external service connections."""
        logger.info("Cleaning up external service connections...")
        if hasattr(self, 'external_services'):
            await self.external_services.cleanup()
    
    async def _load_prediction_models(self):
        """Load prediction models for soil moisture forecasting."""
        logger.info("Loading prediction models...")
        
        # Initialize water balance model
        self.prediction_models["water_balance"] = WaterBalanceModel()
        
        # Initialize evapotranspiration model
        self.prediction_models["evapotranspiration"] = EvapotranspirationModel()
        
        # Initialize crop coefficient model
        self.prediction_models["crop_coefficient"] = CropCoefficientModel()
    
    async def _initialize_monitoring_configs(self):
        """Initialize default monitoring configurations."""
        logger.info("Initializing monitoring configurations...")
        # Set up default configurations
    
    async def _create_field_config(self, field_id: UUID, soil_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Create monitoring configuration for a field."""
        return {
            "field_id": field_id,
            "soil_characteristics": soil_characteristics,
            "alert_thresholds": {
                "low_moisture": 30.0,      # 30% moisture
                "critical_moisture": 20.0,  # 20% moisture
                "high_moisture": 80.0       # 80% moisture
            },
            "monitoring_depth_cm": soil_characteristics.get("monitoring_depth", 100),
            "field_capacity": soil_characteristics.get("field_capacity", 0.35),
            "wilting_point": soil_characteristics.get("wilting_point", 0.15),
            "bulk_density": soil_characteristics.get("bulk_density", 1.3),
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        }
    
    async def _initialize_field_models(self, field_id: UUID, soil_characteristics: Dict[str, Any]):
        """Initialize prediction models for a specific field."""
        logger.info(f"Initializing prediction models for field: {field_id}")
        
        # Initialize field-specific model parameters
        field_models = {
            "water_balance": WaterBalanceModel(soil_characteristics),
            "evapotranspiration": EvapotranspirationModel(soil_characteristics),
            "crop_coefficient": CropCoefficientModel(soil_characteristics)
        }
        
        self.prediction_models[str(field_id)] = field_models
    
    async def _collect_current_moisture_data(self, field_id: UUID, config: Dict[str, Any]) -> Dict[str, Any]:
        """Collect current soil moisture data for a field."""
        # In a real implementation, this would query soil moisture sensors
        # For now, return mock data based on field characteristics
        
        soil_chars = config["soil_characteristics"]
        
        # Simulate moisture data based on soil type and recent weather
        base_moisture = soil_chars.get("field_capacity", 0.35) * 0.7  # 70% of field capacity
        
        return {
            "surface_moisture_percent": base_moisture * 100,
            "deep_moisture_percent": base_moisture * 100 * 1.2,  # Deeper soil typically wetter
            "available_water_capacity": self._calculate_available_water_capacity(
                base_moisture, soil_chars
            ),
            "soil_temperature": 22.5,  # Mock soil temperature
            "timestamp": datetime.utcnow()
        }
    
    def _calculate_available_water_capacity(self, moisture_content: float, soil_chars: Dict[str, Any]) -> float:
        """Calculate available water capacity in inches."""
        soil_depth = soil_chars.get("monitoring_depth", 100)  # cm
        bulk_density = soil_chars.get("bulk_density", 1.3)  # g/cm³
        
        # Convert to inches
        soil_depth_inches = soil_depth / 2.54
        
        # Calculate available water capacity
        # AWC = (moisture_content - wilting_point) * soil_depth * bulk_density
        wilting_point = soil_chars.get("wilting_point", 0.15)
        awc = (moisture_content - wilting_point) * soil_depth_inches * bulk_density
        
        return max(0, awc)
    
    def _determine_moisture_level(self, surface_moisture: float, deep_moisture: float) -> SoilMoistureLevel:
        """Determine overall soil moisture level."""
        avg_moisture = (surface_moisture + deep_moisture) / 2
        
        if avg_moisture < 15:
            return SoilMoistureLevel.VERY_DRY
        elif avg_moisture < 25:
            return SoilMoistureLevel.DRY
        elif avg_moisture < 35:
            return SoilMoistureLevel.ADEQUATE
        elif avg_moisture < 45:
            return SoilMoistureLevel.MOIST
        else:
            return SoilMoistureLevel.SATURATED
    
    async def _generate_irrigation_recommendation(self, field_id: UUID, moisture_data: Dict[str, Any], 
                                                config: Dict[str, Any]) -> str:
        """Generate irrigation recommendation based on moisture data."""
        surface_moisture = moisture_data["surface_moisture_percent"]
        
        if surface_moisture < config["alert_thresholds"]["critical_moisture"]:
            return "Immediate irrigation required - critical moisture level"
        elif surface_moisture < config["alert_thresholds"]["low_moisture"]:
            return "Consider irrigation - low moisture level"
        else:
            return "No irrigation needed - adequate moisture level"
    
    async def _calculate_days_until_critical(self, field_id: UUID, moisture_data: Dict[str, Any], 
                                           config: Dict[str, Any]) -> Optional[int]:
        """Calculate days until critical moisture level."""
        # This would use weather forecast and evapotranspiration models
        # For now, return a simple estimate
        
        current_moisture = moisture_data["surface_moisture_percent"]
        critical_threshold = config["alert_thresholds"]["critical_moisture"]
        
        if current_moisture <= critical_threshold:
            return 0
        
        # Simple linear estimate (would be more sophisticated in real implementation)
        moisture_deficit = current_moisture - critical_threshold
        daily_decline_rate = 2.0  # Assume 2% moisture decline per day
        
        days_until_critical = int(moisture_deficit / daily_decline_rate)
        return max(0, days_until_critical)
    
    async def _get_weather_forecast(self, field_id: UUID, days: int) -> Dict[str, Any]:
        """Get weather forecast for a field."""
        try:
            # Get field location
            field_location = await self.external_services.field_service.get_field_location(field_id)
            coordinates = field_location.get("coordinates", field_location)
            
            # Get weather forecast
            forecast = await self.external_services.weather_service.get_weather_forecast(
                coordinates["latitude"], coordinates["longitude"], days
            )
            
            return forecast
        except Exception as e:
            logger.error(f"Error getting weather forecast: {str(e)}")
            # Return fallback forecast
            return {
                "forecast": [
                    {
                        "date": datetime.utcnow() + timedelta(days=i),
                        "temperature": 25.0 + i,
                        "humidity": 60.0 - i,
                        "precipitation": 0.0 if i % 3 == 0 else 2.0,
                        "wind_speed": 2.0,
                        "solar_radiation": 20.0,
                        "conditions": "clear"
                    }
                    for i in range(days)
                ]
            }
    
    async def _get_crop_water_requirements(self, field_id: UUID, days: int) -> Dict[str, Any]:
        """Get crop water requirements for a field."""
        try:
            # Get field characteristics to determine crop type
            field_chars = await self.external_services.field_service.get_field_characteristics(field_id)
            crop_type = field_chars.get("crop_type", "corn")  # Default to corn
            
            # Get crop water requirements
            crop_data = await self.external_services.crop_service.get_crop_data(field_id, crop_type)
            
            return {
                "crop_type": crop_type,
                "daily_water_requirement_mm": crop_data.get("water_requirements", {}).get("daily_mm", 5.0),
                "total_requirement_mm": crop_data.get("water_requirements", {}).get("daily_mm", 5.0) * days
            }
        except Exception as e:
            logger.error(f"Error getting crop water requirements: {str(e)}")
            # Return fallback requirements
            return {
                "crop_type": "corn",
                "daily_water_requirement_mm": 5.0,
                "total_requirement_mm": 5.0 * days
            }
    
    async def _run_water_balance_model(self, field_id: UUID, current_status: SoilMoistureStatus,
                                     weather_forecast: Dict[str, Any], crop_requirements: Dict[str, Any],
                                     config: Dict[str, Any]) -> Dict[str, Any]:
        """Run water balance model for moisture prediction."""
        # Get the water balance model for this field
        model = self.prediction_models.get(str(field_id), {}).get("water_balance")
        if not model:
            model = self.prediction_models["water_balance"]
        
        # Run the model
        prediction = await model.predict(
            current_status, weather_forecast, crop_requirements, config
        )
        
        return prediction
    
    async def _calculate_deficit_prediction(self, moisture_prediction: Dict[str, Any], 
                                         config: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate moisture deficit predictions."""
        critical_threshold = config["alert_thresholds"]["critical_moisture"]
        
        deficits = []
        for day_prediction in moisture_prediction.get("daily_predictions", []):
            moisture_level = day_prediction["predicted_moisture"]
            deficit = max(0, critical_threshold - moisture_level)
            deficits.append({
                "date": day_prediction["date"],
                "predicted_moisture": moisture_level,
                "deficit": deficit,
                "risk_level": "high" if deficit > 0 else "low"
            })
        
        return {
            "field_id": moisture_prediction["field_id"],
            "prediction_period": moisture_prediction["prediction_period"],
            "deficit_predictions": deficits,
            "overall_risk": "high" if any(d["deficit"] > 0 for d in deficits) else "low"
        }
    
    async def _get_weather_data(self, field_id: UUID, date: datetime) -> Dict[str, Any]:
        """Get weather data for a field on a specific date."""
        try:
            weather_data = await self.external_services.get_weather_data_for_field(field_id, date)
            return weather_data
        except Exception as e:
            logger.error(f"Error getting weather data: {str(e)}")
            # Return fallback weather data
            return {
                "temperature": 25.0,
                "humidity": 60.0,
                "precipitation": 0.0,
                "wind_speed": 2.0,
                "solar_radiation": 20.0
            }
    
    async def _get_crop_data(self, field_id: UUID, date: datetime) -> Dict[str, Any]:
        """Get crop data for a field on a specific date."""
        try:
            # Get field characteristics to determine crop type
            field_chars = await self.external_services.field_service.get_field_characteristics(field_id)
            crop_type = field_chars.get("crop_type", "corn")  # Default to corn
            
            # Get crop data
            crop_data = await self.external_services.crop_service.get_crop_data(field_id, crop_type)
            
            return crop_data
        except Exception as e:
            logger.error(f"Error getting crop data: {str(e)}")
            # Return fallback crop data
            return {
                "crop_type": "corn",
                "growth_stage": "vegetative",
                "planting_date": date - timedelta(days=30),
                "expected_harvest": date + timedelta(days=90)
            }
    
    async def _calculate_reference_et(self, weather_data: Dict[str, Any]) -> float:
        """Calculate reference evapotranspiration using Penman-Monteith equation."""
        # Simplified Penman-Monteith calculation
        # In a real implementation, this would use the full FAO-56 equation
        
        temperature = weather_data.get("temperature", 25.0)
        humidity = weather_data.get("humidity", 60.0)
        wind_speed = weather_data.get("wind_speed", 2.0)
        solar_radiation = weather_data.get("solar_radiation", 20.0)
        
        # Simplified ET₀ calculation (mm/day) with safety check
        temp_diff = temperature - 17.8
        if temp_diff <= 0:
            temp_diff = 0.1  # Minimum value to avoid math domain error
        
        et0 = 0.0023 * (temperature + 17.8) * math.sqrt(temp_diff) * solar_radiation
        
        return max(0, et0)
    
    async def _calculate_crop_coefficient(self, crop_data: Dict[str, Any], date: datetime) -> float:
        """Calculate crop coefficient based on growth stage."""
        growth_stage = crop_data.get("growth_stage", "vegetative")
        
        # Crop coefficient values by growth stage
        kc_values = {
            "initial": 0.4,
            "development": 0.7,
            "mid_season": 1.0,
            "late_season": 0.8,
            "harvest": 0.3
        }
        
        return kc_values.get(growth_stage, 0.7)
    
    async def _calculate_soil_evaporation(self, weather_data: Dict[str, Any], 
                                        soil_characteristics: Dict[str, Any]) -> float:
        """Calculate soil evaporation component."""
        # Simplified soil evaporation calculation
        temperature = weather_data.get("temperature", 25.0)
        humidity = weather_data.get("humidity", 60.0)
        
        # Soil evaporation is typically 10-20% of total ET
        base_et = 0.0023 * (temperature + 17.8) * math.sqrt(temperature - 17.8)
        soil_evaporation = base_et * 0.15  # 15% of base ET
        
        return max(0, soil_evaporation)
    
    async def _calculate_irrigation_needs(self, current_status: SoilMoistureStatus,
                                       weather_forecast: Dict[str, Any], crop_data: Dict[str, Any],
                                       config: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate irrigation needs for a field."""
        # Calculate water deficit
        field_capacity = config["field_capacity"]
        current_moisture = current_status.surface_moisture_percent / 100
        
        water_deficit = field_capacity - current_moisture
        
        # Calculate crop water requirements
        crop_et = await self._calculate_crop_et(crop_data, weather_forecast)
        
        # Calculate irrigation requirement
        irrigation_needed = max(0, water_deficit + crop_et)
        
        return {
            "water_deficit": water_deficit,
            "crop_et": crop_et,
            "irrigation_needed": irrigation_needed,
            "irrigation_depth_mm": irrigation_needed * 25.4  # Convert to mm
        }
    
    async def _calculate_crop_et(self, crop_data: Dict[str, Any], weather_forecast: Dict[str, Any]) -> float:
        """Calculate crop evapotranspiration."""
        # Simplified crop ET calculation
        growth_stage = crop_data.get("growth_stage", "vegetative")
        kc = await self._calculate_crop_coefficient(crop_data, datetime.utcnow())
        
        # Use average weather conditions
        daily_forecast = weather_forecast.get("daily_forecast", [])
        if not daily_forecast:
            daily_forecast = weather_forecast.get("forecast", [])
        
        if daily_forecast:
            avg_temp = sum(day["temperature"] for day in daily_forecast) / len(daily_forecast)
            avg_solar = sum(day["solar_radiation"] for day in daily_forecast) / len(daily_forecast)
        else:
            avg_temp = 25.0
            avg_solar = 20.0
        
        # Safety check for temperature difference
        temp_diff = avg_temp - 17.8
        if temp_diff <= 0:
            temp_diff = 0.1
        
        et0 = 0.0023 * (avg_temp + 17.8) * math.sqrt(temp_diff) * avg_solar
        etc = et0 * kc
        
        return etc
    
    async def _generate_irrigation_recommendations(self, irrigation_needs: Dict[str, Any], 
                                                 config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate irrigation recommendations."""
        irrigation_depth = irrigation_needs["irrigation_depth_mm"]
        
        if irrigation_depth < 5:
            recommendation = "No irrigation needed"
            priority = "low"
        elif irrigation_depth < 15:
            recommendation = "Light irrigation recommended"
            priority = "medium"
        else:
            recommendation = "Heavy irrigation required"
            priority = "high"
        
        return {
            "recommendation": recommendation,
            "priority": priority,
            "irrigation_depth_mm": irrigation_depth,
            "irrigation_depth_inches": irrigation_depth / 25.4,
            "timing": "Early morning or evening",
            "frequency": "As needed based on soil moisture monitoring"
        }


# Mock services for external integrations
class MockWeatherService:
    """Mock weather service for testing."""
    
    async def get_forecast(self, field_id: UUID, days: int) -> Dict[str, Any]:
        """Get mock weather forecast."""
        return {
            "field_id": field_id,
            "forecast_days": days,
            "daily_forecast": [
                {
                    "date": datetime.utcnow() + timedelta(days=i),
                    "temperature": 25.0 + i,
                    "humidity": 60.0 - i,
                    "precipitation": 0.0,
                    "wind_speed": 2.0,
                    "solar_radiation": 20.0
                }
                for i in range(days)
            ]
        }
    
    async def get_weather_data(self, field_id: UUID, date: datetime) -> Dict[str, Any]:
        """Get mock weather data."""
        return {
            "field_id": field_id,
            "date": date,
            "temperature": 25.0,
            "humidity": 60.0,
            "precipitation": 0.0,
            "wind_speed": 2.0,
            "solar_radiation": 20.0
        }


class MockCropService:
    """Mock crop service for testing."""
    
    async def get_water_requirements(self, field_id: UUID, days: int) -> Dict[str, Any]:
        """Get mock crop water requirements."""
        return {
            "field_id": field_id,
            "crop_type": "corn",
            "growth_stage": "vegetative",
            "daily_water_requirement_mm": 5.0,
            "total_requirement_mm": 5.0 * days
        }
    
    async def get_crop_data(self, field_id: UUID, date: datetime) -> Dict[str, Any]:
        """Get mock crop data."""
        return {
            "field_id": field_id,
            "crop_type": "corn",
            "growth_stage": "vegetative",
            "planting_date": date - timedelta(days=30),
            "expected_harvest": date + timedelta(days=90)
        }


class MockFieldService:
    """Mock field service for testing."""
    
    async def get_field_characteristics(self, field_id: UUID) -> Dict[str, Any]:
        """Get mock field characteristics."""
        return {
            "field_id": field_id,
            "soil_type": "clay_loam",
            "field_capacity": 0.35,
            "wilting_point": 0.15,
            "bulk_density": 1.3,
            "monitoring_depth": 100
        }


# Prediction models
class WaterBalanceModel:
    """Water balance model for soil moisture prediction."""
    
    def __init__(self, soil_characteristics: Optional[Dict[str, Any]] = None):
        self.soil_characteristics = soil_characteristics or {}
    
    async def predict(self, current_status: SoilMoistureStatus, weather_forecast: Dict[str, Any],
                     crop_requirements: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Predict soil moisture over time."""
        daily_predictions = []
        current_moisture = current_status.surface_moisture_percent
        
        for day_data in weather_forecast.get("daily_forecast", []):
            # Simple moisture prediction based on weather and crop needs
            precipitation = day_data.get("precipitation", 0.0)
            temperature = day_data.get("temperature", 25.0)
            
            # Calculate moisture change
            crop_et = crop_requirements.get("daily_water_requirement_mm", 5.0)
            moisture_change = precipitation - crop_et
            
            # Update moisture level
            current_moisture += moisture_change / 10  # Simplified conversion
            
            daily_predictions.append({
                "date": day_data["date"],
                "predicted_moisture": max(0, min(100, current_moisture)),
                "precipitation": precipitation,
                "crop_et": crop_et,
                "moisture_change": moisture_change
            })
        
        return {
            "field_id": current_status.field_id,
            "prediction_period": len(daily_predictions),
            "daily_predictions": daily_predictions
        }


class EvapotranspirationModel:
    """Evapotranspiration model for water loss prediction."""
    
    def __init__(self, soil_characteristics: Optional[Dict[str, Any]] = None):
        self.soil_characteristics = soil_characteristics or {}
    
    async def calculate_et(self, weather_data: Dict[str, Any], crop_data: Dict[str, Any]) -> float:
        """Calculate evapotranspiration."""
        # Simplified ET calculation
        temperature = weather_data.get("temperature", 25.0)
        solar_radiation = weather_data.get("solar_radiation", 20.0)
        
        # Safety check for temperature difference
        temp_diff = temperature - 17.8
        if temp_diff <= 0:
            temp_diff = 0.1
        
        et0 = 0.0023 * (temperature + 17.8) * math.sqrt(temp_diff) * solar_radiation
        kc = 0.7  # Default crop coefficient
        
        return et0 * kc


class CropCoefficientModel:
    """Crop coefficient model for water requirement calculations."""
    
    def __init__(self, soil_characteristics: Optional[Dict[str, Any]] = None):
        self.soil_characteristics = soil_characteristics or {}
    
    async def get_crop_coefficient(self, crop_type: str, growth_stage: str) -> float:
        """Get crop coefficient for specific crop and growth stage."""
        # Crop coefficient lookup table
        kc_table = {
            "corn": {
                "initial": 0.4,
                "development": 0.7,
                "mid_season": 1.0,
                "late_season": 0.8,
                "harvest": 0.3
            },
            "soybean": {
                "initial": 0.4,
                "development": 0.7,
                "mid_season": 1.0,
                "late_season": 0.8,
                "harvest": 0.3
            },
            "wheat": {
                "initial": 0.4,
                "development": 0.7,
                "mid_season": 1.0,
                "late_season": 0.8,
                "harvest": 0.3
            }
        }
        
        return kc_table.get(crop_type, {}).get(growth_stage, 0.7)