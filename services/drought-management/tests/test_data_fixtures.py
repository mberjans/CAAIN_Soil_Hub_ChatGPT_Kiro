"""
Test Data Fixtures for Drought Management System

This module provides comprehensive test data fixtures for all drought management tests,
including realistic agricultural scenarios, weather data, soil data, and crop information.

TICKET-014_drought-management-13.1: Test data fixtures
"""

import json
from datetime import datetime, timedelta
from uuid import uuid4
from decimal import Decimal
from typing import Dict, List, Any


class DroughtTestDataFixtures:
    """Comprehensive test data fixtures for drought management tests."""
    
    @staticmethod
    def get_sample_farm_locations() -> List[Dict[str, Any]]:
        """Get sample farm locations for testing."""
        return [
            {
                "id": uuid4(),
                "name": "Midwest Corn Farm",
                "location": {"lat": 40.0, "lng": -95.0},
                "state": "Iowa",
                "climate_zone": "temperate",
                "usda_zone": "5a",
                "total_acres": 500.0,
                "soil_types": ["clay_loam", "silt_loam"],
                "irrigation_available": True
            },
            {
                "id": uuid4(),
                "name": "California Almond Orchard",
                "location": {"lat": 36.0, "lng": -120.0},
                "state": "California",
                "climate_zone": "mediterranean",
                "usda_zone": "9a",
                "total_acres": 200.0,
                "soil_types": ["sandy_loam"],
                "irrigation_available": True
            },
            {
                "id": uuid4(),
                "name": "Texas Cotton Farm",
                "location": {"lat": 32.0, "lng": -97.0},
                "state": "Texas",
                "climate_zone": "subtropical",
                "usda_zone": "8a",
                "total_acres": 1000.0,
                "soil_types": ["clay", "clay_loam"],
                "irrigation_available": False
            }
        ]
    
    @staticmethod
    def get_sample_fields() -> List[Dict[str, Any]]:
        """Get sample field data for testing."""
        return [
            {
                "id": uuid4(),
                "farm_location_id": uuid4(),
                "name": "North Field",
                "acres": 80.0,
                "soil_type": "clay_loam",
                "slope_percent": 3.0,
                "drainage_class": "well_drained",
                "irrigation_available": True,
                "current_crop": "corn",
                "planting_date": datetime.utcnow() - timedelta(days=45),
                "expected_harvest_date": datetime.utcnow() + timedelta(days=90)
            },
            {
                "id": uuid4(),
                "farm_location_id": uuid4(),
                "name": "South Field",
                "acres": 120.0,
                "soil_type": "silt_loam",
                "slope_percent": 1.5,
                "drainage_class": "moderately_well_drained",
                "irrigation_available": False,
                "current_crop": "soybeans",
                "planting_date": datetime.utcnow() - timedelta(days=30),
                "expected_harvest_date": datetime.utcnow() + timedelta(days=105)
            }
        ]
    
    @staticmethod
    def get_sample_weather_data() -> Dict[str, List[Dict[str, Any]]]:
        """Get sample weather data for different scenarios."""
        return {
            "normal_conditions": [
                {
                    "date": datetime.utcnow() - timedelta(days=i),
                    "temperature": 25.0 + (i % 7) * 2.0,  # Daily variation
                    "humidity": 65.0 + (i % 5) * 5.0,
                    "precipitation": 0.2 if i % 3 == 0 else 0.0,
                    "wind_speed": 8.0 + (i % 4) * 2.0,
                    "solar_radiation": 800.0 + (i % 6) * 50.0
                }
                for i in range(30)
            ],
            "drought_conditions": [
                {
                    "date": datetime.utcnow() - timedelta(days=i),
                    "temperature": 30.0 + (i % 7) * 3.0,  # Higher temperatures
                    "humidity": 40.0 + (i % 3) * 5.0,  # Lower humidity
                    "precipitation": 0.0,  # No precipitation
                    "wind_speed": 12.0 + (i % 4) * 3.0,  # Higher winds
                    "solar_radiation": 900.0 + (i % 6) * 60.0  # Higher radiation
                }
                for i in range(30)
            ],
            "severe_drought_conditions": [
                {
                    "date": datetime.utcnow() - timedelta(days=i),
                    "temperature": 35.0 + (i % 7) * 4.0,  # Very high temperatures
                    "humidity": 30.0 + (i % 2) * 5.0,  # Very low humidity
                    "precipitation": 0.0,  # No precipitation
                    "wind_speed": 15.0 + (i % 4) * 4.0,  # Very high winds
                    "solar_radiation": 1000.0 + (i % 6) * 80.0  # Very high radiation
                }
                for i in range(30)
            ]
        }
    
    @staticmethod
    def get_sample_soil_data() -> Dict[str, Dict[str, Any]]:
        """Get sample soil data for different soil types."""
        return {
            "clay_loam": {
                "soil_type": "clay_loam",
                "moisture_content": 0.25,
                "field_capacity": 0.35,
                "wilting_point": 0.15,
                "bulk_density": 1.3,
                "organic_matter": 3.2,
                "ph": 6.5,
                "cec": 25.0,  # Cation exchange capacity
                "infiltration_rate": 0.5,  # inches per hour
                "available_water_capacity": 2.0  # inches per foot
            },
            "sandy_loam": {
                "soil_type": "sandy_loam",
                "moisture_content": 0.18,
                "field_capacity": 0.25,
                "wilting_point": 0.08,
                "bulk_density": 1.5,
                "organic_matter": 2.1,
                "ph": 6.8,
                "cec": 15.0,
                "infiltration_rate": 2.0,
                "available_water_capacity": 1.2
            },
            "silt_loam": {
                "soil_type": "silt_loam",
                "moisture_content": 0.28,
                "field_capacity": 0.38,
                "wilting_point": 0.12,
                "bulk_density": 1.2,
                "organic_matter": 4.1,
                "ph": 6.2,
                "cec": 30.0,
                "infiltration_rate": 1.0,
                "available_water_capacity": 2.2
            }
        }
    
    @staticmethod
    def get_sample_crop_data() -> Dict[str, Dict[str, Any]]:
        """Get sample crop data for different crops."""
        return {
            "corn": {
                "crop_type": "corn",
                "variety": "Pioneer P1234",
                "growth_stage": "V6",
                "planting_date": datetime.utcnow() - timedelta(days=45),
                "expected_harvest_date": datetime.utcnow() + timedelta(days=90),
                "water_requirement": 25.0,  # inches per season
                "drought_tolerance": "moderate",
                "critical_growth_stages": ["VT", "R1", "R2"],  # Tasseling, Silking, Blister
                "yield_potential": 180.0,  # bushels per acre
                "root_depth": 6.0  # feet
            },
            "soybeans": {
                "crop_type": "soybeans",
                "variety": "Asgrow AG1234",
                "growth_stage": "R1",
                "planting_date": datetime.utcnow() - timedelta(days=30),
                "expected_harvest_date": datetime.utcnow() + timedelta(days=105),
                "water_requirement": 20.0,
                "drought_tolerance": "moderate",
                "critical_growth_stages": ["R1", "R2", "R3"],  # Beginning bloom, Full bloom, Beginning pod
                "yield_potential": 55.0,  # bushels per acre
                "root_depth": 4.0
            },
            "wheat": {
                "crop_type": "wheat",
                "variety": "Winter Wheat",
                "growth_stage": "Feekes 6",
                "planting_date": datetime.utcnow() - timedelta(days=120),
                "expected_harvest_date": datetime.utcnow() + timedelta(days=60),
                "water_requirement": 18.0,
                "drought_tolerance": "high",
                "critical_growth_stages": ["Feekes 6", "Feekes 10", "Feekes 10.5"],  # Jointing, Boot, Heading
                "yield_potential": 80.0,  # bushels per acre
                "root_depth": 5.0
            }
        }
    
    @staticmethod
    def get_sample_conservation_practices() -> List[Dict[str, Any]]:
        """Get sample conservation practices for testing."""
        return [
            {
                "practice_type": "cover_crops",
                "name": "Winter Rye Cover Crop",
                "description": "Annual rye grass planted after harvest",
                "water_savings_percent": 15.0,
                "implementation_cost_per_acre": 25.0,
                "maintenance_cost_per_acre": 5.0,
                "soil_health_benefits": ["erosion_control", "organic_matter", "nitrogen_fixation"],
                "implementation_timeline_days": 30,
                "suitable_soil_types": ["clay_loam", "silt_loam"],
                "suitable_crops": ["corn", "soybeans"],
                "seasonal_timing": "fall"
            },
            {
                "practice_type": "mulching",
                "name": "Organic Mulch Application",
                "description": "Application of organic mulch materials",
                "water_savings_percent": 20.0,
                "implementation_cost_per_acre": 40.0,
                "maintenance_cost_per_acre": 10.0,
                "soil_health_benefits": ["moisture_retention", "temperature_regulation", "weed_suppression"],
                "implementation_timeline_days": 7,
                "suitable_soil_types": ["sandy_loam", "silt_loam"],
                "suitable_crops": ["vegetables", "fruits"],
                "seasonal_timing": "spring"
            },
            {
                "practice_type": "tillage_reduction",
                "name": "No-Till Transition",
                "description": "Transition from conventional tillage to no-till",
                "water_savings_percent": 25.0,
                "implementation_cost_per_acre": 100.0,
                "maintenance_cost_per_acre": 0.0,
                "soil_health_benefits": ["structure_improvement", "water_infiltration", "organic_matter"],
                "implementation_timeline_days": 90,
                "suitable_soil_types": ["clay_loam", "silt_loam"],
                "suitable_crops": ["corn", "soybeans", "wheat"],
                "seasonal_timing": "any"
            }
        ]
    
    @staticmethod
    def get_sample_irrigation_systems() -> List[Dict[str, Any]]:
        """Get sample irrigation system data."""
        return [
            {
                "system_type": "center_pivot",
                "efficiency": 0.85,
                "flow_rate": 1000.0,  # gallons per minute
                "coverage_area": 130.0,  # acres
                "energy_cost_per_gallon": 0.05,
                "maintenance_cost_per_year": 5000.0,
                "installation_cost": 150000.0,
                "uniformity_coefficient": 0.85,
                "application_rate": 0.3,  # inches per hour
                "pressure_requirement": 50.0  # PSI
            },
            {
                "system_type": "drip",
                "efficiency": 0.92,
                "flow_rate": 500.0,
                "coverage_area": 50.0,
                "energy_cost_per_gallon": 0.03,
                "maintenance_cost_per_year": 3000.0,
                "installation_cost": 80000.0,
                "uniformity_coefficient": 0.95,
                "application_rate": 0.1,
                "pressure_requirement": 30.0
            },
            {
                "system_type": "flood",
                "efficiency": 0.60,
                "flow_rate": 2000.0,
                "coverage_area": 200.0,
                "energy_cost_per_gallon": 0.02,
                "maintenance_cost_per_year": 2000.0,
                "installation_cost": 50000.0,
                "uniformity_coefficient": 0.70,
                "application_rate": 1.0,
                "pressure_requirement": 10.0
            }
        ]
    
    @staticmethod
    def get_sample_water_sources() -> List[Dict[str, Any]]:
        """Get sample water source data."""
        return [
            {
                "source_type": "groundwater",
                "well_depth": 150.0,  # feet
                "water_quality": "good",
                "sustainability_rating": 0.8,
                "recharge_rate": 0.5,  # inches per month
                "usage_rate": 2.0,  # inches per month
                "cost_per_gallon": 0.02,
                "availability": "reliable",
                "environmental_impact": "low"
            },
            {
                "source_type": "surface_water",
                "stream_flow": 100.0,  # cubic feet per second
                "water_quality": "good",
                "sustainability_rating": 0.7,
                "seasonal_variation": 0.6,
                "usage_rate": 1.5,
                "cost_per_gallon": 0.01,
                "availability": "seasonal",
                "environmental_impact": "medium"
            },
            {
                "source_type": "recycled_water",
                "treatment_level": "tertiary",
                "water_quality": "acceptable",
                "sustainability_rating": 0.9,
                "availability": "reliable",
                "usage_rate": 1.0,
                "cost_per_gallon": 0.05,
                "environmental_impact": "very_low"
            }
        ]
    
    @staticmethod
    def get_historical_drought_scenarios() -> List[Dict[str, Any]]:
        """Get historical drought scenarios for validation."""
        return [
            {
                "scenario_name": "2012_Midwest_Drought",
                "location": {"lat": 40.0, "lng": -95.0},
                "duration_months": 6,
                "precipitation_deficit": -8.5,  # inches below normal
                "temperature_anomaly": 3.2,  # degrees F above normal
                "soil_moisture_deficit": 0.15,
                "yield_loss_percent": 25.0,
                "economic_impact": 30000000000,  # USD
                "affected_area_percent": 60.0,
                "drought_category": "severe"
            },
            {
                "scenario_name": "2017_California_Drought",
                "location": {"lat": 36.0, "lng": -120.0},
                "duration_months": 4,
                "precipitation_deficit": -4.2,
                "temperature_anomaly": 2.1,
                "soil_moisture_deficit": 0.08,
                "yield_loss_percent": 8.0,
                "economic_impact": 5000000000,
                "affected_area_percent": 30.0,
                "drought_category": "moderate"
            },
            {
                "scenario_name": "2019_Texas_Drought",
                "location": {"lat": 32.0, "lng": -97.0},
                "duration_months": 8,
                "precipitation_deficit": -6.8,
                "temperature_anomaly": 2.8,
                "soil_moisture_deficit": 0.12,
                "yield_loss_percent": 18.0,
                "economic_impact": 12000000000,
                "affected_area_percent": 45.0,
                "drought_category": "severe"
            }
        ]
    
    @staticmethod
    def get_agricultural_research_data() -> Dict[str, Any]:
        """Get agricultural research data for validation."""
        return {
            "conservation_practice_effectiveness": {
                "cover_crops": {
                    "water_savings_range": (12.0, 18.0),  # percent
                    "soil_health_improvement": 0.15,
                    "erosion_reduction": 0.40,
                    "implementation_success_rate": 0.85,
                    "cost_per_acre": 25.0,
                    "research_sources": ["USDA-ARS", "University Extension"]
                },
                "no_till": {
                    "water_savings_range": (20.0, 30.0),
                    "soil_health_improvement": 0.25,
                    "organic_matter_increase": 0.5,  # percent per year
                    "implementation_success_rate": 0.75,
                    "cost_per_acre": 100.0,
                    "research_sources": ["USDA-NRCS", "Land Grant Universities"]
                },
                "mulching": {
                    "water_savings_range": (15.0, 25.0),
                    "soil_health_improvement": 0.20,
                    "temperature_regulation": 0.15,  # degrees C reduction
                    "weed_suppression": 0.60,
                    "implementation_success_rate": 0.90,
                    "cost_per_acre": 40.0,
                    "research_sources": ["Organic Farming Research", "Extension Services"]
                }
            },
            "irrigation_efficiency_standards": {
                "center_pivot": {
                    "efficiency_range": (0.75, 0.90),
                    "uniformity_coefficient": 0.85,
                    "energy_efficiency": 0.80,
                    "water_savings_potential": 0.20
                },
                "drip": {
                    "efficiency_range": (0.90, 0.95),
                    "uniformity_coefficient": 0.95,
                    "water_savings_potential": 0.30,
                    "fertilizer_efficiency": 0.25
                },
                "flood": {
                    "efficiency_range": (0.50, 0.70),
                    "uniformity_coefficient": 0.70,
                    "water_savings_potential": 0.10,
                    "energy_efficiency": 0.90
                }
            },
            "crop_drought_response": {
                "corn": {
                    "critical_growth_stages": ["VT", "R1", "R2"],
                    "water_requirement_range": (20.0, 25.0),
                    "drought_tolerance": "moderate",
                    "yield_sensitivity": {
                        "VT": 0.8,  # High sensitivity during tasseling
                        "R1": 0.9,  # Highest sensitivity during silking
                        "R2": 0.7   # High sensitivity during blister stage
                    }
                },
                "soybeans": {
                    "critical_growth_stages": ["R1", "R2", "R3"],
                    "water_requirement_range": (18.0, 22.0),
                    "drought_tolerance": "moderate",
                    "yield_sensitivity": {
                        "R1": 0.6,  # Moderate sensitivity during bloom
                        "R2": 0.8,  # High sensitivity during full bloom
                        "R3": 0.7   # High sensitivity during pod development
                    }
                },
                "wheat": {
                    "critical_growth_stages": ["Feekes 6", "Feekes 10", "Feekes 10.5"],
                    "water_requirement_range": (16.0, 20.0),
                    "drought_tolerance": "high",
                    "yield_sensitivity": {
                        "Feekes 6": 0.5,   # Moderate sensitivity during jointing
                        "Feekes 10": 0.7,  # High sensitivity during boot
                        "Feekes 10.5": 0.8 # High sensitivity during heading
                    }
                }
            }
        }


class TestDataGenerator:
    """Generate test data for specific test scenarios."""
    
    @staticmethod
    def generate_weather_forecast(days: int = 7, scenario: str = "normal") -> List[Dict[str, Any]]:
        """Generate weather forecast data."""
        base_temperature = 25.0 if scenario == "normal" else 30.0 if scenario == "drought" else 35.0
        base_humidity = 65.0 if scenario == "normal" else 40.0 if scenario == "drought" else 30.0
        base_precipitation = 0.2 if scenario == "normal" else 0.0
        
        forecast = []
        for i in range(days):
            forecast.append({
                "date": datetime.utcnow() + timedelta(days=i),
                "temperature": base_temperature + (i % 3) * 2.0,
                "humidity": base_humidity + (i % 2) * 5.0,
                "precipitation": base_precipitation if i % 3 == 0 else 0.0,
                "wind_speed": 8.0 + (i % 4) * 2.0,
                "solar_radiation": 800.0 + (i % 5) * 50.0
            })
        
        return forecast
    
    @staticmethod
    def generate_soil_moisture_data(days: int = 30, initial_moisture: float = 0.25) -> List[Dict[str, Any]]:
        """Generate soil moisture data over time."""
        moisture_data = []
        current_moisture = initial_moisture
        
        for i in range(days):
            # Simulate moisture changes based on weather and crop uptake
            weather_effect = 0.01 if i % 3 == 0 else -0.005  # Precipitation vs evaporation
            crop_uptake = -0.002  # Daily crop water use
            
            current_moisture += weather_effect + crop_uptake
            current_moisture = max(0.05, min(0.40, current_moisture))  # Keep within realistic bounds
            
            moisture_data.append({
                "date": datetime.utcnow() - timedelta(days=days-i),
                "moisture_content": round(current_moisture, 3),
                "field_capacity": 0.35,
                "wilting_point": 0.15,
                "available_water": round((current_moisture - 0.15) * 12, 2)  # inches per foot
            })
        
        return moisture_data
    
    @staticmethod
    def generate_drought_indices_data(months: int = 12) -> Dict[str, Any]:
        """Generate drought indices data."""
        import random
        
        # Generate realistic drought index values
        spi_values = [round(random.uniform(-2.0, 2.0), 2) for _ in range(months)]
        pdsi_value = round(random.uniform(-3.0, 3.0), 2)
        spei_values = [round(random.uniform(-2.5, 2.5), 2) for _ in range(months)]
        
        return {
            "spi": {
                "1_month": spi_values[-1],
                "3_month": round(sum(spi_values[-3:]) / 3, 2),
                "6_month": round(sum(spi_values[-6:]) / 6, 2),
                "12_month": round(sum(spi_values) / len(spi_values), 2)
            },
            "pdsi": pdsi_value,
            "spei": {
                "1_month": spei_values[-1],
                "3_month": round(sum(spei_values[-3:]) / 3, 2),
                "6_month": round(sum(spei_values[-6:]) / 6, 2),
                "12_month": round(sum(spei_values) / len(spei_values), 2)
            },
            "vegetation_health_index": round(random.uniform(0.6, 1.0), 2),
            "overall_drought_severity": "moderate" if pdsi_value < -1.0 else "mild"
        }


# Export fixtures for use in tests
__all__ = [
    "DroughtTestDataFixtures",
    "TestDataGenerator"
]