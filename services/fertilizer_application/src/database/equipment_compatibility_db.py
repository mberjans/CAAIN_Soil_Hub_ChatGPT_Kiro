"""
Equipment Compatibility Database - Comprehensive equipment catalog and compatibility data.
"""

from typing import Dict, List, Any
from src.models.equipment_models import (
    FertilizerFormulation, EquipmentCategory, CompatibilityLevel,
    ApplicationMethodType, FertilizerEquipmentMapping, EquipmentCapabilities
)


class EquipmentCompatibilityDatabase:
    """
    Comprehensive database of equipment types, fertilizer compatibility,
    and operational specifications.
    """

    def __init__(self):
        self._initialize_equipment_catalog()
        self._initialize_compatibility_matrix()
        self._initialize_cost_ranges()
        self._initialize_application_requirements()

    def _initialize_equipment_catalog(self):
        """Initialize comprehensive equipment type catalog."""
        self.equipment_catalog = {
            # SPREADERS
            "broadcast_spreader_small": {
                "name": "Small Broadcast Spreader",
                "category": EquipmentCategory.SPREADING,
                "capacity": {"min": 50, "max": 200, "unit": "cubic_feet"},
                "coverage_rate": {"min": 5, "max": 15, "unit": "acres_per_hour"},
                "spread_width": {"min": 10, "max": 30, "unit": "feet"},
                "particle_size": {"min": 1.0, "max": 6.0, "unit": "mm"},
                "application_methods": [ApplicationMethodType.BROADCAST, ApplicationMethodType.BAND],
                "fertilizer_types": [FertilizerFormulation.GRANULAR, FertilizerFormulation.PELLET],
                "field_size_suitability": {"min": 0, "max": 50, "optimal": 25},
                "automation_level": "manual",
                "gps_compatible": False
            },
            "broadcast_spreader_medium": {
                "name": "Medium Broadcast Spreader",
                "category": EquipmentCategory.SPREADING,
                "capacity": {"min": 200, "max": 800, "unit": "cubic_feet"},
                "coverage_rate": {"min": 15, "max": 40, "unit": "acres_per_hour"},
                "spread_width": {"min": 30, "max": 60, "unit": "feet"},
                "particle_size": {"min": 1.0, "max": 8.0, "unit": "mm"},
                "application_methods": [ApplicationMethodType.BROADCAST, ApplicationMethodType.BAND],
                "fertilizer_types": [FertilizerFormulation.GRANULAR, FertilizerFormulation.PELLET, FertilizerFormulation.ORGANIC],
                "field_size_suitability": {"min": 25, "max": 200, "optimal": 100},
                "automation_level": "semi-automatic",
                "gps_compatible": True
            },
            "broadcast_spreader_large": {
                "name": "Large Broadcast Spreader",
                "category": EquipmentCategory.SPREADING,
                "capacity": {"min": 800, "max": 2000, "unit": "cubic_feet"},
                "coverage_rate": {"min": 40, "max": 100, "unit": "acres_per_hour"},
                "spread_width": {"min": 60, "max": 90, "unit": "feet"},
                "particle_size": {"min": 1.0, "max": 10.0, "unit": "mm"},
                "application_methods": [ApplicationMethodType.BROADCAST, ApplicationMethodType.BAND],
                "fertilizer_types": [FertilizerFormulation.GRANULAR, FertilizerFormulation.PELLET, FertilizerFormulation.ORGANIC],
                "field_size_suitability": {"min": 100, "max": 1000, "optimal": 500},
                "automation_level": "automatic",
                "gps_compatible": True
            },

            # SPRAYERS
            "boom_sprayer_small": {
                "name": "Small Boom Sprayer",
                "category": EquipmentCategory.SPRAYING,
                "capacity": {"min": 50, "max": 200, "unit": "gallons"},
                "coverage_rate": {"min": 10, "max": 30, "unit": "acres_per_hour"},
                "boom_width": {"min": 20, "max": 40, "unit": "feet"},
                "flow_rate": {"min": 5, "max": 20, "unit": "gpm"},
                "pressure_range": {"min": 20, "max": 60, "unit": "psi"},
                "application_methods": [ApplicationMethodType.FOLIAR, ApplicationMethodType.BROADCAST],
                "fertilizer_types": [FertilizerFormulation.LIQUID, FertilizerFormulation.SOLUTION],
                "field_size_suitability": {"min": 0, "max": 50, "optimal": 25},
                "automation_level": "manual",
                "gps_compatible": False,
                "chemical_resistance": ["nitrogen", "phosphorus", "potassium", "micronutrients"]
            },
            "boom_sprayer_medium": {
                "name": "Medium Boom Sprayer",
                "category": EquipmentCategory.SPRAYING,
                "capacity": {"min": 200, "max": 800, "unit": "gallons"},
                "coverage_rate": {"min": 30, "max": 80, "unit": "acres_per_hour"},
                "boom_width": {"min": 40, "max": 80, "unit": "feet"},
                "flow_rate": {"min": 20, "max": 50, "unit": "gpm"},
                "pressure_range": {"min": 20, "max": 100, "unit": "psi"},
                "application_methods": [ApplicationMethodType.FOLIAR, ApplicationMethodType.BROADCAST],
                "fertilizer_types": [FertilizerFormulation.LIQUID, FertilizerFormulation.SOLUTION, FertilizerFormulation.SUSPENSION],
                "field_size_suitability": {"min": 25, "max": 300, "optimal": 150},
                "automation_level": "semi-automatic",
                "gps_compatible": True,
                "chemical_resistance": ["nitrogen", "phosphorus", "potassium", "micronutrients", "herbicides"]
            },
            "boom_sprayer_large": {
                "name": "Large Boom Sprayer",
                "category": EquipmentCategory.SPRAYING,
                "capacity": {"min": 800, "max": 2000, "unit": "gallons"},
                "coverage_rate": {"min": 80, "max": 200, "unit": "acres_per_hour"},
                "boom_width": {"min": 80, "max": 120, "unit": "feet"},
                "flow_rate": {"min": 50, "max": 150, "unit": "gpm"},
                "pressure_range": {"min": 20, "max": 120, "unit": "psi"},
                "application_methods": [ApplicationMethodType.FOLIAR, ApplicationMethodType.BROADCAST],
                "fertilizer_types": [FertilizerFormulation.LIQUID, FertilizerFormulation.SOLUTION, FertilizerFormulation.SUSPENSION],
                "field_size_suitability": {"min": 200, "max": 2000, "optimal": 1000},
                "automation_level": "automatic",
                "gps_compatible": True,
                "chemical_resistance": ["nitrogen", "phosphorus", "potassium", "micronutrients", "herbicides", "acidic", "alkaline"]
            },

            # INJECTION SYSTEMS
            "injection_system_small": {
                "name": "Small Injection System",
                "category": EquipmentCategory.INJECTION,
                "capacity": {"min": 10, "max": 50, "unit": "gph"},
                "coverage_rate": {"min": 3, "max": 10, "unit": "acres_per_hour"},
                "injection_depth": {"min": 2, "max": 8, "unit": "inches"},
                "flow_rate": {"min": 0.5, "max": 3, "unit": "gpm"},
                "pressure_range": {"min": 100, "max": 300, "unit": "psi"},
                "application_methods": [ApplicationMethodType.INJECTION, ApplicationMethodType.SIDEDRESS],
                "fertilizer_types": [FertilizerFormulation.LIQUID, FertilizerFormulation.SOLUTION],
                "field_size_suitability": {"min": 0, "max": 40, "optimal": 20},
                "automation_level": "manual",
                "gps_compatible": False,
                "chemical_resistance": ["nitrogen", "anhydrous_ammonia"]
            },
            "injection_system_medium": {
                "name": "Medium Injection System",
                "category": EquipmentCategory.INJECTION,
                "capacity": {"min": 50, "max": 200, "unit": "gph"},
                "coverage_rate": {"min": 10, "max": 30, "unit": "acres_per_hour"},
                "injection_depth": {"min": 2, "max": 12, "unit": "inches"},
                "flow_rate": {"min": 3, "max": 10, "unit": "gpm"},
                "pressure_range": {"min": 100, "max": 400, "unit": "psi"},
                "application_methods": [ApplicationMethodType.INJECTION, ApplicationMethodType.SIDEDRESS],
                "fertilizer_types": [FertilizerFormulation.LIQUID, FertilizerFormulation.SOLUTION],
                "field_size_suitability": {"min": 20, "max": 200, "optimal": 100},
                "automation_level": "semi-automatic",
                "gps_compatible": True,
                "chemical_resistance": ["nitrogen", "anhydrous_ammonia", "phosphorus", "potassium"]
            },
            "injection_system_large": {
                "name": "Large Injection System",
                "category": EquipmentCategory.INJECTION,
                "capacity": {"min": 200, "max": 800, "unit": "gph"},
                "coverage_rate": {"min": 30, "max": 80, "unit": "acres_per_hour"},
                "injection_depth": {"min": 2, "max": 16, "unit": "inches"},
                "flow_rate": {"min": 10, "max": 30, "unit": "gpm"},
                "pressure_range": {"min": 150, "max": 500, "unit": "psi"},
                "application_methods": [ApplicationMethodType.INJECTION, ApplicationMethodType.SIDEDRESS],
                "fertilizer_types": [FertilizerFormulation.LIQUID, FertilizerFormulation.SOLUTION],
                "field_size_suitability": {"min": 100, "max": 1000, "optimal": 500},
                "automation_level": "automatic",
                "gps_compatible": True,
                "chemical_resistance": ["nitrogen", "anhydrous_ammonia", "phosphorus", "potassium", "high_pressure"]
            },

            # DRIP SYSTEMS
            "drip_system_small": {
                "name": "Small Drip System",
                "category": EquipmentCategory.IRRIGATION,
                "capacity": {"min": 1, "max": 10, "unit": "acres"},
                "coverage_rate": {"min": 0.5, "max": 2, "unit": "acres_per_hour"},
                "emitter_spacing": {"min": 6, "max": 24, "unit": "inches"},
                "flow_rate": {"min": 0.5, "max": 3, "unit": "gph_per_emitter"},
                "pressure_range": {"min": 10, "max": 30, "unit": "psi"},
                "application_methods": [ApplicationMethodType.DRIP, ApplicationMethodType.FERTIGATION],
                "fertilizer_types": [FertilizerFormulation.LIQUID, FertilizerFormulation.SOLUTION],
                "field_size_suitability": {"min": 0, "max": 15, "optimal": 5},
                "automation_level": "manual",
                "gps_compatible": False,
                "fertigation_capable": True
            },
            "drip_system_medium": {
                "name": "Medium Drip System",
                "category": EquipmentCategory.IRRIGATION,
                "capacity": {"min": 10, "max": 50, "unit": "acres"},
                "coverage_rate": {"min": 2, "max": 8, "unit": "acres_per_hour"},
                "emitter_spacing": {"min": 6, "max": 36, "unit": "inches"},
                "flow_rate": {"min": 0.5, "max": 5, "unit": "gph_per_emitter"},
                "pressure_range": {"min": 10, "max": 40, "unit": "psi"},
                "application_methods": [ApplicationMethodType.DRIP, ApplicationMethodType.FERTIGATION],
                "fertilizer_types": [FertilizerFormulation.LIQUID, FertilizerFormulation.SOLUTION],
                "field_size_suitability": {"min": 5, "max": 100, "optimal": 30},
                "automation_level": "semi-automatic",
                "gps_compatible": True,
                "fertigation_capable": True
            },
            "drip_system_large": {
                "name": "Large Drip System",
                "category": EquipmentCategory.IRRIGATION,
                "capacity": {"min": 50, "max": 500, "unit": "acres"},
                "coverage_rate": {"min": 8, "max": 30, "unit": "acres_per_hour"},
                "emitter_spacing": {"min": 6, "max": 48, "unit": "inches"},
                "flow_rate": {"min": 0.5, "max": 8, "unit": "gph_per_emitter"},
                "pressure_range": {"min": 10, "max": 50, "unit": "psi"},
                "application_methods": [ApplicationMethodType.DRIP, ApplicationMethodType.FERTIGATION],
                "fertilizer_types": [FertilizerFormulation.LIQUID, FertilizerFormulation.SOLUTION],
                "field_size_suitability": {"min": 30, "max": 1000, "optimal": 250},
                "automation_level": "automatic",
                "gps_compatible": True,
                "fertigation_capable": True
            }
        }

    def _initialize_compatibility_matrix(self):
        """Initialize fertilizer-equipment compatibility matrix."""
        self.compatibility_matrix = {
            # GRANULAR FERTILIZERS
            (FertilizerFormulation.GRANULAR, EquipmentCategory.SPREADING): {
                "compatibility_level": CompatibilityLevel.HIGHLY_COMPATIBLE,
                "score": 0.95,
                "particle_size_range": {"min": 1.0, "max": 8.0, "unit": "mm"},
                "flow_characteristics": "excellent",
                "special_requirements": ["Proper calibration", "Uniform particle size"],
                "limitations": ["Moisture sensitivity", "Wind drift potential"],
                "best_practices": ["Calibrate before use", "Check spread pattern", "Avoid windy conditions"]
            },
            (FertilizerFormulation.GRANULAR, EquipmentCategory.SPRAYING): {
                "compatibility_level": CompatibilityLevel.INCOMPATIBLE,
                "score": 0.0,
                "special_requirements": [],
                "limitations": ["Cannot spray solid particles"],
                "best_practices": []
            },
            (FertilizerFormulation.GRANULAR, EquipmentCategory.INJECTION): {
                "compatibility_level": CompatibilityLevel.INCOMPATIBLE,
                "score": 0.0,
                "special_requirements": [],
                "limitations": ["Solid particles clog injection systems"],
                "best_practices": []
            },
            (FertilizerFormulation.GRANULAR, EquipmentCategory.IRRIGATION): {
                "compatibility_level": CompatibilityLevel.INCOMPATIBLE,
                "score": 0.0,
                "special_requirements": [],
                "limitations": ["Clogs emitters and filters"],
                "best_practices": []
            },

            # LIQUID FERTILIZERS
            (FertilizerFormulation.LIQUID, EquipmentCategory.SPREADING): {
                "compatibility_level": CompatibilityLevel.INCOMPATIBLE,
                "score": 0.0,
                "special_requirements": [],
                "limitations": ["Spreaders designed for solids only"],
                "best_practices": []
            },
            (FertilizerFormulation.LIQUID, EquipmentCategory.SPRAYING): {
                "compatibility_level": CompatibilityLevel.HIGHLY_COMPATIBLE,
                "score": 0.95,
                "flow_rate_range": {"min": 5, "max": 150, "unit": "gpm"},
                "pressure_range": {"min": 20, "max": 120, "unit": "psi"},
                "special_requirements": ["Chemical-resistant materials", "Proper filtration"],
                "limitations": ["Temperature sensitivity", "Tank compatibility"],
                "best_practices": ["Check chemical compatibility", "Maintain proper pressure", "Clean thoroughly after use"]
            },
            (FertilizerFormulation.LIQUID, EquipmentCategory.INJECTION): {
                "compatibility_level": CompatibilityLevel.HIGHLY_COMPATIBLE,
                "score": 0.90,
                "flow_rate_range": {"min": 0.5, "max": 30, "unit": "gpm"},
                "pressure_range": {"min": 100, "max": 500, "unit": "psi"},
                "special_requirements": ["High-pressure capable", "Corrosion-resistant"],
                "limitations": ["Viscosity constraints", "Pressure requirements"],
                "best_practices": ["Monitor injection depth", "Check flow rates", "Regular maintenance"]
            },
            (FertilizerFormulation.LIQUID, EquipmentCategory.IRRIGATION): {
                "compatibility_level": CompatibilityLevel.HIGHLY_COMPATIBLE,
                "score": 0.92,
                "flow_rate_range": {"min": 0.5, "max": 10, "unit": "gph"},
                "pressure_range": {"min": 10, "max": 50, "unit": "psi"},
                "special_requirements": ["Fine filtration", "Fertigation injector"],
                "limitations": ["Emitter clogging risk", "Precipitation potential"],
                "best_practices": ["Use proper filtration", "Monitor EC/pH", "Flush system regularly"]
            },

            # SLOW-RELEASE FERTILIZERS
            (FertilizerFormulation.SLOW_RELEASE, EquipmentCategory.SPREADING): {
                "compatibility_level": CompatibilityLevel.COMPATIBLE,
                "score": 0.85,
                "particle_size_range": {"min": 1.5, "max": 6.0, "unit": "mm"},
                "special_requirements": ["Gentle handling", "Avoid crushing"],
                "limitations": ["Higher cost", "Coating sensitivity"],
                "best_practices": ["Check particle integrity", "Avoid high-impact application", "Store properly"]
            },
            (FertilizerFormulation.SLOW_RELEASE, EquipmentCategory.SPRAYING): {
                "compatibility_level": CompatibilityLevel.INCOMPATIBLE,
                "score": 0.0,
                "special_requirements": [],
                "limitations": ["Cannot spray coated granules"],
                "best_practices": []
            },

            # ORGANIC FERTILIZERS
            (FertilizerFormulation.ORGANIC, EquipmentCategory.SPREADING): {
                "compatibility_level": CompatibilityLevel.COMPATIBLE,
                "score": 0.80,
                "particle_size_range": {"min": 2.0, "max": 10.0, "unit": "mm"},
                "special_requirements": ["Larger spreader openings", "Higher capacity"],
                "limitations": ["Variable particle sizes", "Moisture content issues"],
                "best_practices": ["Check moisture content", "Adjust spreader settings", "Prevent bridging"]
            },
            (FertilizerFormulation.ORGANIC, EquipmentCategory.IRRIGATION): {
                "compatibility_level": CompatibilityLevel.POORLY_COMPATIBLE,
                "score": 0.30,
                "special_requirements": ["Liquid organic only", "Extensive filtration"],
                "limitations": ["High clogging risk", "Organic matter buildup"],
                "best_practices": ["Pre-filter thoroughly", "Frequent cleaning", "Monitor emitters"]
            },

            # SOLUTION FERTILIZERS
            (FertilizerFormulation.SOLUTION, EquipmentCategory.SPRAYING): {
                "compatibility_level": CompatibilityLevel.HIGHLY_COMPATIBLE,
                "score": 0.98,
                "flow_rate_range": {"min": 5, "max": 150, "unit": "gpm"},
                "pressure_range": {"min": 20, "max": 120, "unit": "psi"},
                "special_requirements": ["Basic filtration", "Standard materials"],
                "limitations": ["Temperature sensitivity"],
                "best_practices": ["Maintain solution temperature", "Regular calibration", "Clean nozzles"]
            },
            (FertilizerFormulation.SOLUTION, EquipmentCategory.INJECTION): {
                "compatibility_level": CompatibilityLevel.HIGHLY_COMPATIBLE,
                "score": 0.95,
                "flow_rate_range": {"min": 0.5, "max": 30, "unit": "gpm"},
                "pressure_range": {"min": 100, "max": 500, "unit": "psi"},
                "special_requirements": ["Accurate metering", "Pressure control"],
                "limitations": ["Concentration limits"],
                "best_practices": ["Verify concentration", "Monitor injection rate", "Check depth placement"]
            },
            (FertilizerFormulation.SOLUTION, EquipmentCategory.IRRIGATION): {
                "compatibility_level": CompatibilityLevel.HIGHLY_COMPATIBLE,
                "score": 0.98,
                "flow_rate_range": {"min": 0.5, "max": 10, "unit": "gph"},
                "pressure_range": {"min": 10, "max": 50, "unit": "psi"},
                "special_requirements": ["Basic filtration", "Injection system"],
                "limitations": ["Concentration management"],
                "best_practices": ["Monitor EC", "Maintain pH range", "Regular flushing"]
            }
        }

    def _initialize_cost_ranges(self):
        """Initialize equipment cost ranges."""
        self.cost_ranges = {
            "broadcast_spreader_small": {
                "purchase_price": {"min": 1000, "max": 5000, "typical": 2500},
                "operating_cost_per_hour": {"min": 5, "max": 15, "typical": 10},
                "maintenance_cost_annual": {"min": 200, "max": 500, "typical": 300},
                "cost_per_acre": {"min": 1.0, "max": 3.0, "typical": 2.0}
            },
            "broadcast_spreader_medium": {
                "purchase_price": {"min": 5000, "max": 25000, "typical": 15000},
                "operating_cost_per_hour": {"min": 10, "max": 30, "typical": 20},
                "maintenance_cost_annual": {"min": 500, "max": 1500, "typical": 1000},
                "cost_per_acre": {"min": 0.75, "max": 2.0, "typical": 1.25}
            },
            "broadcast_spreader_large": {
                "purchase_price": {"min": 25000, "max": 75000, "typical": 50000},
                "operating_cost_per_hour": {"min": 25, "max": 60, "typical": 40},
                "maintenance_cost_annual": {"min": 1500, "max": 4000, "typical": 2500},
                "cost_per_acre": {"min": 0.50, "max": 1.5, "typical": 1.0}
            },
            "boom_sprayer_small": {
                "purchase_price": {"min": 2000, "max": 10000, "typical": 5000},
                "operating_cost_per_hour": {"min": 8, "max": 20, "typical": 12},
                "maintenance_cost_annual": {"min": 300, "max": 800, "typical": 500},
                "cost_per_acre": {"min": 2.0, "max": 4.0, "typical": 3.0}
            },
            "boom_sprayer_medium": {
                "purchase_price": {"min": 10000, "max": 40000, "typical": 25000},
                "operating_cost_per_hour": {"min": 15, "max": 40, "typical": 25},
                "maintenance_cost_annual": {"min": 800, "max": 2500, "typical": 1500},
                "cost_per_acre": {"min": 1.5, "max": 3.0, "typical": 2.0}
            },
            "boom_sprayer_large": {
                "purchase_price": {"min": 40000, "max": 150000, "typical": 90000},
                "operating_cost_per_hour": {"min": 35, "max": 80, "typical": 55},
                "maintenance_cost_annual": {"min": 2500, "max": 7000, "typical": 4500},
                "cost_per_acre": {"min": 1.0, "max": 2.0, "typical": 1.5}
            },
            "injection_system_small": {
                "purchase_price": {"min": 3000, "max": 12000, "typical": 7000},
                "operating_cost_per_hour": {"min": 10, "max": 25, "typical": 15},
                "maintenance_cost_annual": {"min": 400, "max": 1000, "typical": 600},
                "cost_per_acre": {"min": 3.0, "max": 6.0, "typical": 4.5}
            },
            "injection_system_medium": {
                "purchase_price": {"min": 12000, "max": 45000, "typical": 28000},
                "operating_cost_per_hour": {"min": 20, "max": 50, "typical": 35},
                "maintenance_cost_annual": {"min": 1000, "max": 3000, "typical": 1800},
                "cost_per_acre": {"min": 2.0, "max": 4.5, "typical": 3.0}
            },
            "injection_system_large": {
                "purchase_price": {"min": 45000, "max": 120000, "typical": 80000},
                "operating_cost_per_hour": {"min": 40, "max": 90, "typical": 65},
                "maintenance_cost_annual": {"min": 3000, "max": 7500, "typical": 5000},
                "cost_per_acre": {"min": 1.5, "max": 3.5, "typical": 2.5}
            },
            "drip_system_small": {
                "purchase_price": {"min": 500, "max": 3000, "typical": 1500},
                "operating_cost_per_hour": {"min": 2, "max": 8, "typical": 5},
                "maintenance_cost_annual": {"min": 100, "max": 400, "typical": 250},
                "cost_per_acre": {"min": 50, "max": 150, "typical": 100}  # Per acre installation
            },
            "drip_system_medium": {
                "purchase_price": {"min": 3000, "max": 15000, "typical": 8000},
                "operating_cost_per_hour": {"min": 5, "max": 20, "typical": 12},
                "maintenance_cost_annual": {"min": 400, "max": 1500, "typical": 900},
                "cost_per_acre": {"min": 40, "max": 120, "typical": 75}
            },
            "drip_system_large": {
                "purchase_price": {"min": 15000, "max": 100000, "typical": 50000},
                "operating_cost_per_hour": {"min": 15, "max": 50, "typical": 30},
                "maintenance_cost_annual": {"min": 1500, "max": 6000, "typical": 3500},
                "cost_per_acre": {"min": 30, "max": 100, "typical": 60}
            }
        }

    def _initialize_application_requirements(self):
        """Initialize application method requirements."""
        self.application_requirements = {
            ApplicationMethodType.BROADCAST: {
                "fertilizer_types": [FertilizerFormulation.GRANULAR, FertilizerFormulation.PELLET,
                                    FertilizerFormulation.ORGANIC, FertilizerFormulation.LIQUID],
                "equipment_categories": [EquipmentCategory.SPREADING, EquipmentCategory.SPRAYING],
                "precision_level": "low_to_medium",
                "coverage_uniformity": 0.80,
                "weather_sensitivity": "high",
                "suitable_soil_types": ["all"],
                "field_shape_preference": "regular"
            },
            ApplicationMethodType.BAND: {
                "fertilizer_types": [FertilizerFormulation.GRANULAR, FertilizerFormulation.PELLET],
                "equipment_categories": [EquipmentCategory.SPREADING],
                "precision_level": "medium",
                "coverage_uniformity": 0.85,
                "weather_sensitivity": "medium",
                "suitable_soil_types": ["all"],
                "field_shape_preference": "row_crops"
            },
            ApplicationMethodType.FOLIAR: {
                "fertilizer_types": [FertilizerFormulation.LIQUID, FertilizerFormulation.SOLUTION],
                "equipment_categories": [EquipmentCategory.SPRAYING],
                "precision_level": "medium_to_high",
                "coverage_uniformity": 0.90,
                "weather_sensitivity": "very_high",
                "suitable_soil_types": ["all"],
                "field_shape_preference": "any"
            },
            ApplicationMethodType.INJECTION: {
                "fertilizer_types": [FertilizerFormulation.LIQUID, FertilizerFormulation.SOLUTION],
                "equipment_categories": [EquipmentCategory.INJECTION],
                "precision_level": "high",
                "coverage_uniformity": 0.92,
                "weather_sensitivity": "low",
                "suitable_soil_types": ["medium_to_light"],
                "field_shape_preference": "row_crops"
            },
            ApplicationMethodType.DRIP: {
                "fertilizer_types": [FertilizerFormulation.LIQUID, FertilizerFormulation.SOLUTION],
                "equipment_categories": [EquipmentCategory.IRRIGATION],
                "precision_level": "very_high",
                "coverage_uniformity": 0.95,
                "weather_sensitivity": "very_low",
                "suitable_soil_types": ["all"],
                "field_shape_preference": "permanent_crops"
            },
            ApplicationMethodType.FERTIGATION: {
                "fertilizer_types": [FertilizerFormulation.LIQUID, FertilizerFormulation.SOLUTION],
                "equipment_categories": [EquipmentCategory.IRRIGATION],
                "precision_level": "very_high",
                "coverage_uniformity": 0.95,
                "weather_sensitivity": "very_low",
                "suitable_soil_types": ["all"],
                "field_shape_preference": "irrigated_fields"
            },
            ApplicationMethodType.SIDEDRESS: {
                "fertilizer_types": [FertilizerFormulation.LIQUID, FertilizerFormulation.GRANULAR],
                "equipment_categories": [EquipmentCategory.INJECTION, EquipmentCategory.SPREADING],
                "precision_level": "medium_to_high",
                "coverage_uniformity": 0.88,
                "weather_sensitivity": "medium",
                "suitable_soil_types": ["all"],
                "field_shape_preference": "row_crops"
            }
        }

    def get_equipment_specs(self, equipment_type: str) -> Dict[str, Any]:
        """Get equipment specifications by type."""
        return self.equipment_catalog.get(equipment_type, {})

    def get_compatibility(self, fertilizer_type: FertilizerFormulation,
                         equipment_category: EquipmentCategory) -> Dict[str, Any]:
        """Get compatibility information for fertilizer-equipment combination."""
        return self.compatibility_matrix.get((fertilizer_type, equipment_category), {
            "compatibility_level": CompatibilityLevel.INCOMPATIBLE,
            "score": 0.0,
            "special_requirements": [],
            "limitations": ["No compatibility data available"],
            "best_practices": []
        })

    def get_cost_data(self, equipment_type: str) -> Dict[str, Any]:
        """Get cost data for equipment type."""
        return self.cost_ranges.get(equipment_type, {})

    def get_application_requirements(self, application_method: ApplicationMethodType) -> Dict[str, Any]:
        """Get requirements for application method."""
        return self.application_requirements.get(application_method, {})

    def get_all_equipment_for_fertilizer(self, fertilizer_type: FertilizerFormulation) -> List[str]:
        """Get all compatible equipment types for a fertilizer type."""
        compatible_equipment = []
        for equipment_type, specs in self.equipment_catalog.items():
            if fertilizer_type in specs.get("fertilizer_types", []):
                compatible_equipment.append(equipment_type)
        return compatible_equipment

    def get_all_fertilizers_for_equipment(self, equipment_category: EquipmentCategory) -> List[FertilizerFormulation]:
        """Get all compatible fertilizers for an equipment category."""
        compatible_fertilizers = set()
        for (fert_type, equip_cat), compat in self.compatibility_matrix.items():
            if equip_cat == equipment_category and compat["score"] > 0.5:
                compatible_fertilizers.add(fert_type)
        return list(compatible_fertilizers)
