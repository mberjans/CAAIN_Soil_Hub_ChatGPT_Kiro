"""
Advanced Crop Type and Growth Stage Integration Service for fertilizer application methods.

This service provides comprehensive crop-specific data and growth stage considerations
for fertilizer application method selection and optimization.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CropType(str, Enum):
    """Comprehensive crop type enumeration."""
    # Grains
    CORN = "corn"
    SOYBEAN = "soybean"
    WHEAT = "wheat"
    RICE = "rice"
    BARLEY = "barley"
    OATS = "oats"
    SORGHUM = "sorghum"
    MILLET = "millet"
    
    # Vegetables
    TOMATO = "tomato"
    PEPPER = "pepper"
    LETTUCE = "lettuce"
    CARROT = "carrot"
    ONION = "onion"
    POTATO = "potato"
    SWEET_POTATO = "sweet_potato"
    CABBAGE = "cabbage"
    BROCCOLI = "broccoli"
    CAULIFLOWER = "cauliflower"
    
    # Fruits
    APPLE = "apple"
    PEAR = "pear"
    PEACH = "peach"
    CHERRY = "cherry"
    GRAPE = "grape"
    STRAWBERRY = "strawberry"
    BLUEBERRY = "blueberry"
    
    # Legumes
    BEAN = "bean"
    PEAS = "peas"
    LENTIL = "lentil"
    CHICKPEA = "chickpea"
    
    # Oilseeds
    SUNFLOWER = "sunflower"
    CANOLA = "canola"
    COTTON = "cotton"
    
    # Forage
    ALFALFA = "alfalfa"
    CLOVER = "clover"
    GRASS_HAY = "grass_hay"
    
    # Specialty
    SUGAR_BEET = "sugar_beet"
    SUGAR_CANE = "sugar_cane"
    TOBACCO = "tobacco"


class GrowthStage(str, Enum):
    """Comprehensive growth stage enumeration."""
    # Germination and Early Growth
    GERMINATION = "germination"
    EMERGENCE = "emergence"
    SEEDLING = "seedling"
    
    # Vegetative Growth
    VEGETATIVE_1 = "vegetative_1"  # Early vegetative
    VEGETATIVE_2 = "vegetative_2"  # Mid vegetative
    VEGETATIVE_3 = "vegetative_3"  # Late vegetative
    
    # Reproductive Growth
    FLOWERING = "flowering"
    POLLINATION = "pollination"
    FRUIT_SET = "fruit_set"
    
    # Maturity
    MATURITY = "maturity"
    HARVEST = "harvest"
    
    # Specific crop stages
    # Corn stages
    V1 = "v1"  # First leaf
    V2 = "v2"  # Second leaf
    V3 = "v3"  # Third leaf
    V4 = "v4"  # Fourth leaf
    V5 = "v5"  # Fifth leaf
    V6 = "v6"  # Sixth leaf
    VT = "vt"  # Tasseling
    R1 = "r1"  # Silking
    R2 = "r2"  # Blister
    R3 = "r3"  # Milk
    R4 = "r4"  # Dough
    R5 = "r5"  # Dent
    R6 = "r6"  # Physiological maturity
    
    # Soybean stages
    VE = "ve"  # Emergence
    VC = "vc"  # Cotyledon
    V1_SOY = "v1_soy"  # First trifoliate
    V2_SOY = "v2_soy"  # Second trifoliate
    V3_SOY = "v3_soy"  # Third trifoliate
    V4_SOY = "v4_soy"  # Fourth trifoliate
    V5_SOY = "v5_soy"  # Fifth trifoliate
    V6_SOY = "v6_soy"  # Sixth trifoliate
    R1_SOY = "r1_soy"  # Beginning bloom
    R2_SOY = "r2_soy"  # Full bloom
    R3_SOY = "r3_soy"  # Beginning pod
    R4_SOY = "r4_soy"  # Full pod
    R5_SOY = "r5_soy"  # Beginning seed
    R6_SOY = "r6_soy"  # Full seed
    R7_SOY = "r7_soy"  # Beginning maturity
    R8_SOY = "r8_soy"  # Full maturity
    
    # Wheat stages
    TILLERING = "tillering"
    JOINTING = "jointing"


@dataclass
class CropGrowthStageInfo:
    """Information about a specific growth stage for a crop."""
    stage_name: str
    stage_code: str
    description: str
    days_from_planting: Tuple[int, int]  # Min and max days
    nutrient_demand_level: str  # low, medium, high, critical
    application_sensitivity: str  # low, medium, high
    recommended_methods: List[str]
    avoided_methods: List[str]
    timing_preferences: List[str]


@dataclass
class CropApplicationPreferences:
    """Crop-specific application method preferences."""
    crop_type: CropType
    preferred_methods: List[str]
    avoided_methods: List[str]
    sensitivity_factors: Dict[str, float]
    nutrient_uptake_pattern: Dict[str, List[float]]  # Nutrient: uptake curve over growth stages
    application_timing_critical_stages: List[str]


class CropIntegrationService:
    """Service for advanced crop type and growth stage integration."""
    
    def __init__(self):
        self.crop_database = {}
        self.growth_stage_database = {}
        self.application_preferences = {}
        self._initialize_crop_database()
        self._initialize_growth_stage_database()
        self._initialize_application_preferences()
    
    def _initialize_crop_database(self):
        """Initialize comprehensive crop database with detailed characteristics."""
        self.crop_database = {
            CropType.CORN: {
                "name": "Corn (Maize)",
                "scientific_name": "Zea mays",
                "category": "grain",
                "family": "Poaceae",
                "growing_season": "warm_season",
                "root_system": "fibrous",
                "nutrient_requirements": {
                    "nitrogen": {"high": True, "critical_stages": ["V6", "VT", "R1"]},
                    "phosphorus": {"high": True, "critical_stages": ["V1", "V6"]},
                    "potassium": {"medium": True, "critical_stages": ["V6", "VT"]},
                    "sulfur": {"medium": True, "critical_stages": ["V6"]},
                    "zinc": {"medium": True, "critical_stages": ["V1", "V6"]}
                },
                "application_sensitivity": {
                    "foliar": "high",
                    "broadcast": "low",
                    "band": "medium",
                    "sidedress": "medium",
                    "injection": "low"
                },
                "growth_duration_days": (100, 120),
                "critical_application_windows": {
                    "pre_plant": (0, 7),
                    "at_planting": (0, 3),
                    "early_vegetative": (14, 28),
                    "mid_vegetative": (35, 49),
                    "reproductive": (70, 85)
                }
            },
            
            CropType.SOYBEAN: {
                "name": "Soybean",
                "scientific_name": "Glycine max",
                "category": "legume",
                "family": "Fabaceae",
                "growing_season": "warm_season",
                "root_system": "taproot",
                "nutrient_requirements": {
                    "nitrogen": {"low": True, "fixation": True, "critical_stages": ["R1", "R3"]},
                    "phosphorus": {"high": True, "critical_stages": ["V1", "R1"]},
                    "potassium": {"high": True, "critical_stages": ["R1", "R3"]},
                    "sulfur": {"medium": True, "critical_stages": ["R1"]},
                    "molybdenum": {"high": True, "critical_stages": ["V1"]}
                },
                "application_sensitivity": {
                    "foliar": "high",
                    "broadcast": "low",
                    "band": "medium",
                    "sidedress": "high",
                    "injection": "medium"
                },
                "growth_duration_days": (90, 110),
                "critical_application_windows": {
                    "pre_plant": (0, 7),
                    "at_planting": (0, 3),
                    "early_vegetative": (14, 21),
                    "reproductive": (45, 60)
                }
            },
            
            CropType.WHEAT: {
                "name": "Wheat",
                "scientific_name": "Triticum aestivum",
                "category": "grain",
                "family": "Poaceae",
                "growing_season": "cool_season",
                "root_system": "fibrous",
                "nutrient_requirements": {
                    "nitrogen": {"high": True, "critical_stages": ["tillering", "jointing", "heading"]},
                    "phosphorus": {"high": True, "critical_stages": ["tillering", "jointing"]},
                    "potassium": {"medium": True, "critical_stages": ["tillering", "jointing"]},
                    "sulfur": {"medium": True, "critical_stages": ["jointing"]}
                },
                "application_sensitivity": {
                    "foliar": "medium",
                    "broadcast": "low",
                    "band": "medium",
                    "sidedress": "medium",
                    "injection": "low"
                },
                "growth_duration_days": (120, 150),
                "critical_application_windows": {
                    "fall": (0, 30),
                    "spring": (60, 90),
                    "tillering": (30, 60),
                    "jointing": (60, 90)
                }
            },
            
            CropType.TOMATO: {
                "name": "Tomato",
                "scientific_name": "Solanum lycopersicum",
                "category": "vegetable",
                "family": "Solanaceae",
                "growing_season": "warm_season",
                "root_system": "fibrous",
                "nutrient_requirements": {
                    "nitrogen": {"medium": True, "critical_stages": ["flowering", "fruit_set"]},
                    "phosphorus": {"high": True, "critical_stages": ["flowering"]},
                    "potassium": {"high": True, "critical_stages": ["fruit_set", "maturity"]},
                    "calcium": {"high": True, "critical_stages": ["fruit_set"]},
                    "magnesium": {"medium": True, "critical_stages": ["flowering"]}
                },
                "application_sensitivity": {
                    "foliar": "high",
                    "broadcast": "medium",
                    "band": "high",
                    "sidedress": "high",
                    "injection": "medium"
                },
                "growth_duration_days": (70, 90),
                "critical_application_windows": {
                    "transplant": (0, 3),
                    "flowering": (35, 45),
                    "fruit_set": (45, 55),
                    "fruit_development": (55, 75)
                }
            },
            
            CropType.POTATO: {
                "name": "Potato",
                "scientific_name": "Solanum tuberosum",
                "category": "vegetable",
                "family": "Solanaceae",
                "growing_season": "cool_season",
                "root_system": "tuberous",
                "nutrient_requirements": {
                    "nitrogen": {"medium": True, "critical_stages": ["tuber_initiation", "tuber_bulking"]},
                    "phosphorus": {"high": True, "critical_stages": ["tuber_initiation"]},
                    "potassium": {"high": True, "critical_stages": ["tuber_bulking"]},
                    "calcium": {"medium": True, "critical_stages": ["tuber_bulking"]}
                },
                "application_sensitivity": {
                    "foliar": "medium",
                    "broadcast": "low",
                    "band": "high",
                    "sidedress": "high",
                    "injection": "medium"
                },
                "growth_duration_days": (90, 120),
                "critical_application_windows": {
                    "planting": (0, 7),
                    "tuber_initiation": (35, 45),
                    "tuber_bulking": (45, 75)
                }
            }
        }
    
    def _initialize_growth_stage_database(self):
        """Initialize detailed growth stage database with application considerations."""
        self.growth_stage_database = {
            # Corn growth stages
            "corn": {
                GrowthStage.V1: CropGrowthStageInfo(
                    stage_name="First Leaf",
                    stage_code="V1",
                    description="First leaf fully emerged",
                    days_from_planting=(7, 10),
                    nutrient_demand_level="low",
                    application_sensitivity="low",
                    recommended_methods=["broadcast", "band"],
                    avoided_methods=["foliar"],
                    timing_preferences=["pre_plant", "at_planting"]
                ),
                GrowthStage.V6: CropGrowthStageInfo(
                    stage_name="Sixth Leaf",
                    stage_code="V6",
                    description="Sixth leaf fully emerged - critical N uptake period",
                    days_from_planting=(35, 42),
                    nutrient_demand_level="critical",
                    application_sensitivity="medium",
                    recommended_methods=["sidedress", "band", "injection"],
                    avoided_methods=["foliar"],
                    timing_preferences=["early_vegetative"]
                ),
                GrowthStage.VT: CropGrowthStageInfo(
                    stage_name="Tasseling",
                    stage_code="VT",
                    description="Tassel emergence - peak N demand",
                    days_from_planting=(70, 80),
                    nutrient_demand_level="critical",
                    application_sensitivity="high",
                    recommended_methods=["sidedress", "foliar"],
                    avoided_methods=["broadcast"],
                    timing_preferences=["reproductive"]
                ),
                GrowthStage.R1: CropGrowthStageInfo(
                    stage_name="Silking",
                    stage_code="R1",
                    description="Silk emergence - final N application window",
                    days_from_planting=(75, 85),
                    nutrient_demand_level="high",
                    application_sensitivity="high",
                    recommended_methods=["foliar"],
                    avoided_methods=["broadcast", "sidedress"],
                    timing_preferences=["reproductive"]
                )
            },
            
            # Soybean growth stages
            "soybean": {
                GrowthStage.V1_SOY: CropGrowthStageInfo(
                    stage_name="First Trifoliate",
                    stage_code="V1",
                    description="First trifoliate leaf fully expanded",
                    days_from_planting=(10, 14),
                    nutrient_demand_level="low",
                    application_sensitivity="low",
                    recommended_methods=["broadcast", "band"],
                    avoided_methods=["foliar"],
                    timing_preferences=["pre_plant", "at_planting"]
                ),
                GrowthStage.R1_SOY: CropGrowthStageInfo(
                    stage_name="Beginning Bloom",
                    stage_code="R1",
                    description="First flower open - critical P and K period",
                    days_from_planting=(45, 55),
                    nutrient_demand_level="critical",
                    application_sensitivity="medium",
                    recommended_methods=["band", "foliar"],
                    avoided_methods=["broadcast"],
                    timing_preferences=["reproductive"]
                ),
                GrowthStage.R3_SOY: CropGrowthStageInfo(
                    stage_name="Beginning Pod",
                    stage_code="R3",
                    description="Pod development - peak nutrient demand",
                    days_from_planting=(60, 70),
                    nutrient_demand_level="critical",
                    application_sensitivity="high",
                    recommended_methods=["foliar"],
                    avoided_methods=["broadcast", "sidedress"],
                    timing_preferences=["reproductive"]
                )
            },
            
            # Wheat growth stages
            "wheat": {
                GrowthStage.TILLERING: CropGrowthStageInfo(
                    stage_name="Tillering",
                    stage_code="Tillering",
                    description="Tillering stage - critical N application window",
                    days_from_planting=(30, 60),
                    nutrient_demand_level="critical",
                    application_sensitivity="medium",
                    recommended_methods=["broadcast", "band"],
                    avoided_methods=["foliar"],
                    timing_preferences=["spring"]
                ),
                GrowthStage.JOINTING: CropGrowthStageInfo(
                    stage_name="Jointing",
                    stage_code="Jointing",
                    description="Stem elongation - final N application",
                    days_from_planting=(60, 90),
                    nutrient_demand_level="high",
                    application_sensitivity="high",
                    recommended_methods=["broadcast", "foliar"],
                    avoided_methods=["sidedress"],
                    timing_preferences=["spring"]
                )
            }
        }
    
    def _initialize_application_preferences(self):
        """Initialize crop-specific application method preferences."""
        self.application_preferences = {
            CropType.CORN: CropApplicationPreferences(
                crop_type=CropType.CORN,
                preferred_methods=["band", "sidedress", "injection"],
                avoided_methods=["foliar"],
                sensitivity_factors={
                    "root_damage": 0.8,
                    "foliar_burn": 0.9,
                    "timing_critical": 0.9,
                    "equipment_compatibility": 0.7
                },
                nutrient_uptake_pattern={
                    "nitrogen": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                    "phosphorus": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.8, 0.6],
                    "potassium": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.8]
                },
                application_timing_critical_stages=["V6", "VT", "R1"]
            ),
            
            CropType.SOYBEAN: CropApplicationPreferences(
                crop_type=CropType.SOYBEAN,
                preferred_methods=["band", "broadcast"],
                avoided_methods=["foliar", "sidedress"],
                sensitivity_factors={
                    "root_damage": 0.9,
                    "foliar_burn": 0.8,
                    "timing_critical": 0.7,
                    "equipment_compatibility": 0.8
                },
                nutrient_uptake_pattern={
                    "nitrogen": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # N fixation
                    "phosphorus": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.8],
                    "potassium": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
                },
                application_timing_critical_stages=["R1", "R3"]
            ),
            
            CropType.TOMATO: CropApplicationPreferences(
                crop_type=CropType.TOMATO,
                preferred_methods=["band", "foliar", "injection"],
                avoided_methods=["broadcast"],
                sensitivity_factors={
                    "root_damage": 0.9,
                    "foliar_burn": 0.7,
                    "timing_critical": 0.8,
                    "equipment_compatibility": 0.9
                },
                nutrient_uptake_pattern={
                    "nitrogen": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.8],
                    "phosphorus": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.8, 0.6],
                    "potassium": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
                },
                application_timing_critical_stages=["flowering", "fruit_set"]
            )
        }
    
    def get_crop_info(self, crop_type: CropType) -> Dict[str, Any]:
        """Get comprehensive crop information."""
        return self.crop_database.get(crop_type, {})
    
    def get_growth_stage_info(self, crop_type: CropType, growth_stage: GrowthStage) -> Optional[CropGrowthStageInfo]:
        """Get detailed growth stage information for a specific crop."""
        crop_stages = self.growth_stage_database.get(crop_type.value)
        if crop_stages:
            return crop_stages.get(growth_stage)
        return None
    
    def get_application_preferences(self, crop_type: CropType) -> Optional[CropApplicationPreferences]:
        """Get crop-specific application method preferences."""
        return self.application_preferences.get(crop_type)
    
    def get_recommended_methods_for_stage(self, crop_type: CropType, growth_stage: GrowthStage) -> List[str]:
        """Get recommended application methods for specific crop and growth stage."""
        stage_info = self.get_growth_stage_info(crop_type, growth_stage)
        if stage_info:
            return stage_info.recommended_methods
        return []
    
    def get_avoided_methods_for_stage(self, crop_type: CropType, growth_stage: GrowthStage) -> List[str]:
        """Get avoided application methods for specific crop and growth stage."""
        stage_info = self.get_growth_stage_info(crop_type, growth_stage)
        if stage_info:
            return stage_info.avoided_methods
        return []
    
    def calculate_application_timing_score(self, crop_type: CropType, growth_stage: GrowthStage, 
                                         method_type: str, days_from_planting: int) -> float:
        """Calculate timing score for application method based on crop and growth stage."""
        stage_info = self.get_growth_stage_info(crop_type, growth_stage)
        if not stage_info:
            return 0.5  # Default neutral score
        
        # Base score from growth stage
        base_score = 0.5
        
        # Adjust based on nutrient demand level
        demand_adjustments = {
            "low": 0.0,
            "medium": 0.1,
            "high": 0.2,
            "critical": 0.3
        }
        base_score += demand_adjustments.get(stage_info.nutrient_demand_level, 0.0)
        
        # Adjust based on method sensitivity
        sensitivity_adjustments = {
            "low": 0.1,
            "medium": 0.0,
            "high": -0.1
        }
        base_score += sensitivity_adjustments.get(stage_info.application_sensitivity, 0.0)
        
        # Adjust based on timing window
        if stage_info.days_from_planting[0] <= days_from_planting <= stage_info.days_from_planting[1]:
            base_score += 0.2
        else:
            # Penalty for being outside optimal window
            base_score -= 0.1
        
        # Method-specific adjustments
        if method_type in stage_info.recommended_methods:
            base_score += 0.2
        elif method_type in stage_info.avoided_methods:
            base_score -= 0.3
        
        return max(0.0, min(1.0, base_score))
    
    def get_nutrient_uptake_curve(self, crop_type: CropType, nutrient: str) -> List[float]:
        """Get nutrient uptake curve for a specific crop and nutrient."""
        preferences = self.get_application_preferences(crop_type)
        if preferences and nutrient in preferences.nutrient_uptake_pattern:
            return preferences.nutrient_uptake_pattern[nutrient]
        return [0.1] * 10  # Default low uptake
    
    def assess_crop_method_compatibility(self, crop_type: CropType, method_type: str) -> Dict[str, Any]:
        """Assess compatibility between crop type and application method."""
        crop_info = self.get_crop_info(crop_type)
        preferences = self.get_application_preferences(crop_type)
        
        if not crop_info or not preferences:
            return {"compatibility_score": 0.5, "factors": []}
        
        compatibility_factors = []
        score = 0.5
        
        # Check if method is preferred
        if method_type in preferences.preferred_methods:
            score += 0.3
            compatibility_factors.append("Method is preferred for this crop")
        elif method_type in preferences.avoided_methods:
            score -= 0.3
            compatibility_factors.append("Method is avoided for this crop")
        
        # Check application sensitivity
        sensitivity = crop_info.get("application_sensitivity", {}).get(method_type, "medium")
        if sensitivity == "low":
            score += 0.1
            compatibility_factors.append("Low application sensitivity")
        elif sensitivity == "high":
            score -= 0.1
            compatibility_factors.append("High application sensitivity")
        
        # Check root system compatibility
        root_system = crop_info.get("root_system", "fibrous")
        if root_system == "fibrous" and method_type in ["broadcast", "band"]:
            score += 0.1
            compatibility_factors.append("Compatible with fibrous root system")
        elif root_system == "taproot" and method_type in ["band", "injection"]:
            score += 0.1
            compatibility_factors.append("Compatible with taproot system")
        
        return {
            "compatibility_score": max(0.0, min(1.0, score)),
            "factors": compatibility_factors
        }
    
    def get_critical_application_windows(self, crop_type: CropType) -> Dict[str, Tuple[int, int]]:
        """Get critical application windows for a crop."""
        crop_info = self.get_crop_info(crop_type)
        return crop_info.get("critical_application_windows", {})
    
    def get_supported_crops(self) -> List[CropType]:
        """Get list of all supported crop types."""
        return list(self.crop_database.keys())
    
    def get_supported_growth_stages(self, crop_type: CropType) -> List[GrowthStage]:
        """Get list of supported growth stages for a crop."""
        crop_stages = self.growth_stage_database.get(crop_type.value, {})
        return list(crop_stages.keys())