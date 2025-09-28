"""
Data Source Adapters

Adapters to integrate existing weather and soil services with the 
data ingestion framework.
"""

from typing import Dict, Any, Optional
import structlog
from datetime import datetime

from .weather_service import WeatherService, WeatherData, ForecastDay, AgriculturalWeatherMetrics, ClimateZoneData
from .soil_service import SoilService, SoilCharacteristics, SoilNutrientRanges, SoilSuitability

logger = structlog.get_logger(__name__)


class WeatherServiceAdapter:
    """Adapter for weather service integration with data ingestion framework."""
    
    def __init__(self):
        self.weather_service = WeatherService()
    
    async def handle_operation(self, operation: str, **params) -> Dict[str, Any]:
        """Handle weather service operations."""
        latitude = params.get("latitude")
        longitude = params.get("longitude")
        
        if not latitude or not longitude:
            raise ValueError("Latitude and longitude are required for weather operations")
        
        try:
            if operation == "current_weather":
                weather_data = await self.weather_service.get_current_weather(latitude, longitude)
                return self._weather_data_to_dict(weather_data)
            
            elif operation == "forecast":
                days = params.get("days", 7)
                forecast_data = await self.weather_service.get_forecast(latitude, longitude, days)
                return {
                    "forecast": [self._forecast_day_to_dict(day) for day in forecast_data],
                    "location": {"latitude": latitude, "longitude": longitude},
                    "forecast_days": len(forecast_data)
                }
            
            elif operation == "agricultural_metrics":
                base_temp_f = params.get("base_temp_f", 50.0)
                metrics = await self.weather_service.get_agricultural_metrics(
                    latitude, longitude, base_temp_f
                )
                return self._agricultural_metrics_to_dict(metrics)
            
            elif operation == "climate_zone_data":
                climate_data = await self.weather_service.get_climate_zone_data(
                    latitude, longitude
                )
                return self._climate_zone_data_to_dict(climate_data)
            
            else:
                raise ValueError(f"Unknown weather operation: {operation}")
                
        except Exception as e:
            logger.error("Weather service adapter error", 
                        operation=operation, error=str(e))
            raise
    
    def _weather_data_to_dict(self, weather_data: WeatherData) -> Dict[str, Any]:
        """Convert WeatherData to dictionary."""
        return {
            "temperature_f": weather_data.temperature_f,
            "humidity_percent": weather_data.humidity_percent,
            "precipitation_inches": weather_data.precipitation_inches,
            "wind_speed_mph": weather_data.wind_speed_mph,
            "wind_direction": weather_data.wind_direction,
            "conditions": weather_data.conditions,
            "pressure_mb": weather_data.pressure_mb,
            "visibility_miles": weather_data.visibility_miles,
            "uv_index": weather_data.uv_index,
            "timestamp": weather_data.timestamp.isoformat() if weather_data.timestamp else None,
            "data_source": "weather_service"
        }
    
    def _forecast_day_to_dict(self, forecast_day: ForecastDay) -> Dict[str, Any]:
        """Convert ForecastDay to dictionary."""
        return {
            "date": forecast_day.date,
            "high_temp_f": forecast_day.high_temp_f,
            "low_temp_f": forecast_day.low_temp_f,
            "precipitation_chance": forecast_day.precipitation_chance,
            "precipitation_amount": forecast_day.precipitation_amount,
            "conditions": forecast_day.conditions,
            "wind_speed_mph": forecast_day.wind_speed_mph,
            "humidity_percent": forecast_day.humidity_percent
        }
    
    def _agricultural_metrics_to_dict(self, metrics: AgriculturalWeatherMetrics) -> Dict[str, Any]:
        """Convert AgriculturalWeatherMetrics to dictionary."""
        return {
            "growing_degree_days": metrics.growing_degree_days,
            "accumulated_precipitation": metrics.accumulated_precipitation,
            "days_since_rain": metrics.days_since_rain,
            "soil_temperature_f": metrics.soil_temperature_f,
            "evapotranspiration_inches": metrics.evapotranspiration_inches,
            "data_source": "weather_service"
        }
    
    def _climate_zone_data_to_dict(self, climate_data) -> Dict[str, Any]:
        """Convert ClimateZoneData to dictionary."""
        if not climate_data:
            return {}
        
        return {
            "usda_zone": climate_data.usda_zone,
            "koppen_classification": climate_data.koppen_classification,
            "average_min_temp_f": climate_data.average_min_temp_f,
            "average_max_temp_f": climate_data.average_max_temp_f,
            "annual_precipitation_inches": climate_data.annual_precipitation_inches,
            "growing_season_length": climate_data.growing_season_length,
            "last_frost_date": climate_data.last_frost_date,
            "first_frost_date": climate_data.first_frost_date,
            "data_source": "weather_service_climate_analysis"
        }
    
    async def close(self):
        """Close weather service connections."""
        await self.weather_service.close()


class SoilServiceAdapter:
    """Adapter for soil service integration with data ingestion framework."""
    
    def __init__(self):
        self.soil_service = SoilService()
    
    async def handle_operation(self, operation: str, **params) -> Dict[str, Any]:
        """Handle soil service operations."""
        latitude = params.get("latitude")
        longitude = params.get("longitude")
        
        if not latitude or not longitude:
            raise ValueError("Latitude and longitude are required for soil operations")
        
        try:
            if operation == "soil_characteristics":
                soil_chars = await self.soil_service.get_soil_characteristics(latitude, longitude)
                return self._soil_characteristics_to_dict(soil_chars)
            
            elif operation == "nutrient_ranges":
                # First get soil characteristics
                soil_chars = await self.soil_service.get_soil_characteristics(latitude, longitude)
                # Then get nutrient ranges
                nutrient_ranges = await self.soil_service.get_nutrient_ranges(soil_chars)
                return self._nutrient_ranges_to_dict(nutrient_ranges, soil_chars)
            
            elif operation == "crop_suitability":
                # First get soil characteristics
                soil_chars = await self.soil_service.get_soil_characteristics(latitude, longitude)
                # Then get crop suitability
                suitability = await self.soil_service.get_crop_suitability(soil_chars)
                return self._crop_suitability_to_dict(suitability, soil_chars)
            
            else:
                raise ValueError(f"Unknown soil operation: {operation}")
                
        except Exception as e:
            logger.error("Soil service adapter error", 
                        operation=operation, error=str(e))
            raise
    
    def _soil_characteristics_to_dict(self, soil_chars: SoilCharacteristics) -> Dict[str, Any]:
        """Convert SoilCharacteristics to dictionary."""
        return {
            "soil_series": soil_chars.soil_series,
            "soil_texture": soil_chars.soil_texture,
            "drainage_class": soil_chars.drainage_class,
            "typical_ph_range": soil_chars.typical_ph_range,
            "organic_matter_typical": soil_chars.organic_matter_typical,
            "slope_range": soil_chars.slope_range,
            "parent_material": soil_chars.parent_material,
            "depth_to_bedrock": soil_chars.depth_to_bedrock,
            "flooding_frequency": soil_chars.flooding_frequency,
            "ponding_frequency": soil_chars.ponding_frequency,
            "hydrologic_group": soil_chars.hydrologic_group,
            "available_water_capacity": soil_chars.available_water_capacity,
            "permeability": soil_chars.permeability,
            "erosion_factor_k": soil_chars.erosion_factor_k,
            "data_source": "soil_service"
        }
    
    def _nutrient_ranges_to_dict(self, nutrient_ranges: SoilNutrientRanges, 
                                soil_chars: SoilCharacteristics) -> Dict[str, Any]:
        """Convert SoilNutrientRanges to dictionary."""
        return {
            "phosphorus_ppm_range": nutrient_ranges.phosphorus_ppm_range,
            "potassium_ppm_range": nutrient_ranges.potassium_ppm_range,
            "nitrogen_typical": nutrient_ranges.nitrogen_typical,
            "cec_range": nutrient_ranges.cec_range,
            "base_saturation_range": nutrient_ranges.base_saturation_range,
            "micronutrient_status": nutrient_ranges.micronutrient_status,
            "soil_series": soil_chars.soil_series,
            "soil_texture": soil_chars.soil_texture,
            "data_source": "soil_service"
        }
    
    def _crop_suitability_to_dict(self, suitability: SoilSuitability, 
                                 soil_chars: SoilCharacteristics) -> Dict[str, Any]:
        """Convert SoilSuitability to dictionary."""
        return {
            "crop_suitability": suitability.crop_suitability,
            "limitations": suitability.limitations,
            "management_considerations": suitability.management_considerations,
            "irrigation_suitability": suitability.irrigation_suitability,
            "erosion_risk": suitability.erosion_risk,
            "soil_series": soil_chars.soil_series,
            "soil_texture": soil_chars.soil_texture,
            "drainage_class": soil_chars.drainage_class,
            "data_source": "soil_service"
        }


class CropDatabaseAdapter:
    """Adapter for crop database integration (placeholder implementation)."""
    
    def __init__(self):
        # Placeholder crop database
        self.crop_database = {
            "corn": {
                "varieties": [
                    {
                        "variety_name": "Pioneer P1197AM",
                        "maturity_days": 111,
                        "yield_potential_bu_per_acre": 185,
                        "drought_tolerance": "good",
                        "disease_resistance": ["gray_leaf_spot", "northern_corn_leaf_blight"],
                        "recommended_regions": ["midwest", "great_plains"],
                        "planting_depth_inches": 2.0,
                        "seeding_rate_seeds_per_acre": 32000
                    },
                    {
                        "variety_name": "DeKalb DKC64-87RIB",
                        "maturity_days": 114,
                        "yield_potential_bu_per_acre": 190,
                        "drought_tolerance": "excellent",
                        "disease_resistance": ["gray_leaf_spot", "stalk_rot"],
                        "recommended_regions": ["midwest"],
                        "planting_depth_inches": 2.0,
                        "seeding_rate_seeds_per_acre": 30000
                    }
                ],
                "general_requirements": {
                    "optimal_ph_range": {"min": 6.0, "max": 6.8},
                    "minimum_growing_season_days": 100,
                    "water_requirements_inches": 20,
                    "soil_temperature_germination_f": 50
                }
            },
            "soybean": {
                "varieties": [
                    {
                        "variety_name": "Asgrow AG2433",
                        "maturity_group": "2.4",
                        "yield_potential_bu_per_acre": 65,
                        "disease_resistance": ["scn", "phytophthora", "white_mold"],
                        "recommended_regions": ["midwest"],
                        "planting_depth_inches": 1.5,
                        "seeding_rate_seeds_per_acre": 140000
                    },
                    {
                        "variety_name": "Pioneer P22T41R",
                        "maturity_group": "2.2",
                        "yield_potential_bu_per_acre": 62,
                        "disease_resistance": ["scn", "sudden_death_syndrome"],
                        "recommended_regions": ["midwest", "great_plains"],
                        "planting_depth_inches": 1.5,
                        "seeding_rate_seeds_per_acre": 145000
                    }
                ],
                "general_requirements": {
                    "optimal_ph_range": {"min": 6.0, "max": 7.0},
                    "minimum_growing_season_days": 90,
                    "water_requirements_inches": 18,
                    "soil_temperature_germination_f": 50
                }
            },
            "wheat": {
                "varieties": [
                    {
                        "variety_name": "WB-Grainfield",
                        "type": "hard_red_winter",
                        "yield_potential_bu_per_acre": 75,
                        "disease_resistance": ["stripe_rust", "leaf_rust"],
                        "recommended_regions": ["great_plains", "midwest"],
                        "planting_depth_inches": 1.5,
                        "seeding_rate_lbs_per_acre": 90
                    }
                ],
                "general_requirements": {
                    "optimal_ph_range": {"min": 6.0, "max": 7.5},
                    "minimum_growing_season_days": 120,
                    "water_requirements_inches": 15,
                    "soil_temperature_germination_f": 40
                }
            }
        }
    
    async def handle_operation(self, operation: str, **params) -> Dict[str, Any]:
        """Handle crop database operations."""
        try:
            if operation == "crop_varieties":
                crop_name = params.get("crop_name", "").lower()
                region = params.get("region", "").lower()
                
                if not crop_name:
                    raise ValueError("crop_name parameter is required")
                
                if crop_name not in self.crop_database:
                    return {
                        "crop_name": crop_name,
                        "varieties": [],
                        "message": f"No varieties found for crop: {crop_name}",
                        "data_source": "crop_database"
                    }
                
                crop_data = self.crop_database[crop_name]
                varieties = crop_data["varieties"]
                
                # Filter by region if specified
                if region:
                    varieties = [
                        variety for variety in varieties
                        if region in variety.get("recommended_regions", [])
                    ]
                
                return {
                    "crop_name": crop_name,
                    "varieties": varieties,
                    "general_requirements": crop_data["general_requirements"],
                    "region_filter": region if region else None,
                    "data_source": "crop_database"
                }
            
            elif operation == "crop_requirements":
                crop_name = params.get("crop_name", "").lower()
                
                if not crop_name:
                    raise ValueError("crop_name parameter is required")
                
                if crop_name not in self.crop_database:
                    return {
                        "crop_name": crop_name,
                        "requirements": {},
                        "message": f"No requirements found for crop: {crop_name}",
                        "data_source": "crop_database"
                    }
                
                return {
                    "crop_name": crop_name,
                    "requirements": self.crop_database[crop_name]["general_requirements"],
                    "data_source": "crop_database"
                }
            
            else:
                raise ValueError(f"Unknown crop database operation: {operation}")
                
        except Exception as e:
            logger.error("Crop database adapter error", 
                        operation=operation, error=str(e))
            raise


class MarketDataAdapter:
    """Adapter for market data integration (placeholder implementation)."""
    
    def __init__(self):
        # Placeholder market data
        self.market_data = {
            "commodities": {
                "corn_per_bushel": 4.25,
                "soybean_per_bushel": 12.80,
                "wheat_per_bushel": 6.15,
                "last_updated": "2024-12-09T10:00:00Z"
            },
            "fertilizers": {
                "urea_per_ton": 420.00,
                "dap_per_ton": 580.00,
                "potash_per_ton": 380.00,
                "anhydrous_ammonia_per_ton": 520.00,
                "last_updated": "2024-12-09T10:00:00Z"
            },
            "fuel": {
                "diesel_per_gallon": 3.45,
                "gasoline_per_gallon": 3.25,
                "last_updated": "2024-12-09T10:00:00Z"
            }
        }
    
    async def handle_operation(self, operation: str, **params) -> Dict[str, Any]:
        """Handle market data operations."""
        try:
            if operation == "commodity_prices":
                commodity = params.get("commodity", "").lower()
                
                if commodity and commodity in self.market_data["commodities"]:
                    return {
                        "commodity": commodity,
                        "price": self.market_data["commodities"][commodity],
                        "last_updated": self.market_data["commodities"]["last_updated"],
                        "data_source": "market_data"
                    }
                else:
                    return {
                        "commodities": self.market_data["commodities"],
                        "data_source": "market_data"
                    }
            
            elif operation == "fertilizer_prices":
                fertilizer = params.get("fertilizer", "").lower()
                
                if fertilizer and fertilizer in self.market_data["fertilizers"]:
                    return {
                        "fertilizer": fertilizer,
                        "price": self.market_data["fertilizers"][fertilizer],
                        "last_updated": self.market_data["fertilizers"]["last_updated"],
                        "data_source": "market_data"
                    }
                else:
                    return {
                        "fertilizers": self.market_data["fertilizers"],
                        "data_source": "market_data"
                    }
            
            elif operation == "fuel_prices":
                return {
                    "fuel_prices": self.market_data["fuel"],
                    "data_source": "market_data"
                }
            
            elif operation == "all_prices":
                return {
                    "market_data": self.market_data,
                    "data_source": "market_data"
                }
            
            else:
                raise ValueError(f"Unknown market data operation: {operation}")
                
        except Exception as e:
            logger.error("Market data adapter error", 
                        operation=operation, error=str(e))
            raise