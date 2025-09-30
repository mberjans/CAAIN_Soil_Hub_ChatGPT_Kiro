"""
Application Method Service for fertilizer application method selection and optimization.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from uuid import uuid4

from ..models.application_models import (
    ApplicationRequest, ApplicationResponse, ApplicationMethod,
    FieldConditions, CropRequirements, FertilizerSpecification,
    ApplicationMethodType, FertilizerForm, EquipmentType
)
from ..models.application_models import EquipmentSpecification
from ..models.method_models import ApplicationMethod as MethodModel
from ..database.fertilizer_db import get_application_methods_by_type
from .crop_integration_service import CropIntegrationService, CropType, GrowthStage

logger = logging.getLogger(__name__)


class ApplicationMethodService:
    """Service for fertilizer application method selection and optimization."""
    
    def __init__(self):
        self.method_database = {}
        self.crop_integration_service = CropIntegrationService()
        self._initialize_method_database()
    
    def _initialize_method_database(self):
        """Initialize the application method database with predefined methods."""
        self.method_database = {
            ApplicationMethodType.BROADCAST: {
                "name": "Broadcast Application",
                "description": "Uniform distribution of fertilizer across the entire field surface",
                "equipment_types": [EquipmentType.SPREADER, EquipmentType.BROADCASTER],
                "fertilizer_forms": [FertilizerForm.GRANULAR, FertilizerForm.ORGANIC],
                "field_size_range": (1, 10000),  # acres
                "efficiency_score": 0.7,
                "cost_per_acre": 15.0,
                "labor_intensity": "medium",
                "environmental_impact": "moderate",
                "pros": [
                    "Simple and fast application",
                    "Good for large fields",
                    "Low equipment requirements",
                    "Suitable for most fertilizer types"
                ],
                "cons": [
                    "Lower nutrient use efficiency",
                    "Potential for runoff",
                    "Less precise application",
                    "May require higher application rates"
                ]
            },
            ApplicationMethodType.BAND: {
                "name": "Band Application",
                "description": "Placement of fertilizer in bands near the seed or plant row",
                "equipment_types": [EquipmentType.SPREADER],
                "fertilizer_forms": [FertilizerForm.GRANULAR, FertilizerForm.LIQUID],
                "field_size_range": (1, 5000),
                "efficiency_score": 0.8,
                "cost_per_acre": 20.0,
                "labor_intensity": "medium",
                "environmental_impact": "low",
                "pros": [
                    "Higher nutrient use efficiency",
                    "Reduced fertilizer requirements",
                    "Better root access to nutrients",
                    "Reduced environmental impact"
                ],
                "cons": [
                    "More complex setup",
                    "Requires precise equipment",
                    "May need specialized equipment",
                    "Higher initial cost"
                ]
            },
            ApplicationMethodType.SIDEDRESS: {
                "name": "Sidedress Application",
                "description": "Application of fertilizer to the side of growing plants",
                "equipment_types": [EquipmentType.SPREADER, EquipmentType.INJECTOR],
                "fertilizer_forms": [FertilizerForm.GRANULAR, FertilizerForm.LIQUID],
                "field_size_range": (1, 3000),
                "efficiency_score": 0.85,
                "cost_per_acre": 25.0,
                "labor_intensity": "high",
                "environmental_impact": "low",
                "pros": [
                    "Excellent nutrient timing",
                    "High efficiency",
                    "Reduced early season losses",
                    "Flexible application timing"
                ],
                "cons": [
                    "Requires crop growth stage timing",
                    "Higher labor requirements",
                    "Equipment must avoid crop damage",
                    "Weather dependent"
                ]
            },
            ApplicationMethodType.FOLIAR: {
                "name": "Foliar Application",
                "description": "Application of fertilizer directly to plant leaves",
                "equipment_types": [EquipmentType.SPRAYER],
                "fertilizer_forms": [FertilizerForm.LIQUID],
                "field_size_range": (1, 2000),
                "efficiency_score": 0.9,
                "cost_per_acre": 30.0,
                "labor_intensity": "high",
                "environmental_impact": "low",
                "pros": [
                    "Very high efficiency",
                    "Quick plant response",
                    "Precise nutrient delivery",
                    "Minimal soil disturbance"
                ],
                "cons": [
                    "Limited nutrient amounts",
                    "Weather sensitive",
                    "Requires specialized equipment",
                    "Higher cost per unit"
                ]
            },
            ApplicationMethodType.INJECTION: {
                "name": "Injection Application",
                "description": "Injection of liquid fertilizer into the soil",
                "equipment_types": [EquipmentType.INJECTOR],
                "fertilizer_forms": [FertilizerForm.LIQUID],
                "field_size_range": (1, 4000),
                "efficiency_score": 0.8,
                "cost_per_acre": 22.0,
                "labor_intensity": "medium",
                "environmental_impact": "low",
                "pros": [
                    "Direct soil placement",
                    "Reduced volatilization",
                    "Good nutrient distribution",
                    "Weather independent"
                ],
                "cons": [
                    "Requires specialized equipment",
                    "Higher equipment cost",
                    "Soil compaction concerns",
                    "Limited to liquid fertilizers"
                ]
            },
            ApplicationMethodType.DRIP: {
                "name": "Drip Irrigation Application",
                "description": "Application through drip irrigation system",
                "equipment_types": [EquipmentType.DRIP_SYSTEM],
                "fertilizer_forms": [FertilizerForm.LIQUID],
                "field_size_range": (1, 1000),
                "efficiency_score": 0.95,
                "cost_per_acre": 35.0,
                "labor_intensity": "low",
                "environmental_impact": "very_low",
                "pros": [
                    "Highest efficiency",
                    "Precise nutrient delivery",
                    "Water and fertilizer savings",
                    "Automated application"
                ],
                "cons": [
                    "High initial investment",
                    "Requires irrigation system",
                    "Limited to liquid fertilizers",
                    "Maintenance intensive"
                ]
            }
        }
    
    async def select_application_methods(
        self, 
        request: ApplicationRequest
    ) -> ApplicationResponse:
        """
        Select optimal fertilizer application methods based on field conditions,
        crop requirements, and available equipment.
        
        Args:
            request: Application request with field conditions, crop requirements,
                    fertilizer specification, and available equipment
            
        Returns:
            ApplicationResponse with recommended methods and analysis
        """
        start_time = time.time()
        request_id = str(uuid4())
        
        try:
            logger.info(f"Processing application method selection request {request_id}")
            
            # Analyze field conditions and crop requirements
            field_analysis = await self._analyze_field_conditions(request.field_conditions)
            crop_analysis = await self._analyze_crop_requirements(request.crop_requirements)
            fertilizer_analysis = await self._analyze_fertilizer_specification(request.fertilizer_specification)
            equipment_analysis = await self._analyze_available_equipment(request.available_equipment)
            
            # Score and rank application methods
            method_scores = await self._score_application_methods(
                field_analysis, crop_analysis, fertilizer_analysis, equipment_analysis
            )
            
            # Generate recommendations
            recommended_methods = await self._generate_recommendations(
                method_scores, request.field_conditions, request.crop_requirements,
                request.fertilizer_specification, request.available_equipment
            )
            
            # Select primary recommendation
            primary_recommendation = recommended_methods[0] if recommended_methods else None
            
            # Generate alternative methods
            alternative_methods = recommended_methods[1:3] if len(recommended_methods) > 1 else []
            
            # Perform cost comparison
            cost_comparison = await self._perform_cost_comparison(recommended_methods)
            
            # Generate efficiency analysis
            efficiency_analysis = await self._generate_efficiency_analysis(recommended_methods)
            
            # Generate equipment compatibility matrix
            equipment_compatibility = await self._generate_equipment_compatibility(
                recommended_methods, request.available_equipment
            )
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            response = ApplicationResponse(
                request_id=request_id,
                recommended_methods=recommended_methods,
                primary_recommendation=primary_recommendation,
                alternative_methods=alternative_methods,
                cost_comparison=cost_comparison,
                efficiency_analysis=efficiency_analysis,
                equipment_compatibility=equipment_compatibility,
                processing_time_ms=processing_time_ms,
                metadata={
                    "field_analysis": field_analysis,
                    "crop_analysis": crop_analysis,
                    "fertilizer_analysis": fertilizer_analysis,
                    "equipment_analysis": equipment_analysis,
                    "method_scores": method_scores
                }
            )
            
            logger.info(f"Application method selection completed in {processing_time_ms:.2f}ms")
            return response
            
        except Exception as e:
            logger.error(f"Error in application method selection: {e}")
            raise
    
    async def _analyze_field_conditions(self, field_conditions: FieldConditions) -> Dict[str, Any]:
        """Analyze field conditions for method suitability."""
        analysis = {
            "field_size_category": self._categorize_field_size(field_conditions.field_size_acres),
            "soil_suitability": self._assess_soil_suitability(field_conditions.soil_type),
            "drainage_impact": self._assess_drainage_impact(field_conditions.drainage_class),
            "slope_considerations": self._assess_slope_impact(field_conditions.slope_percent),
            "irrigation_availability": field_conditions.irrigation_available,
            "access_constraints": self._assess_access_constraints(field_conditions.access_roads)
        }
        return analysis
    
    async def _analyze_crop_requirements(self, crop_requirements: CropRequirements) -> Dict[str, Any]:
        """Analyze crop requirements for method suitability."""
        analysis = {
            "crop_type": crop_requirements.crop_type,
            "growth_stage": crop_requirements.growth_stage,
            "nutrient_timing": self._assess_nutrient_timing(crop_requirements.growth_stage),
            "yield_target": crop_requirements.target_yield,
            "nutrient_demand": crop_requirements.nutrient_requirements,
            "application_timing_preferences": crop_requirements.application_timing_preferences
        }
        return analysis
    
    async def _analyze_fertilizer_specification(self, fertilizer_spec: FertilizerSpecification) -> Dict[str, Any]:
        """Analyze fertilizer specification for method compatibility."""
        analysis = {
            "fertilizer_type": fertilizer_spec.fertilizer_type,
            "form": fertilizer_spec.form,
            "solubility": fertilizer_spec.solubility,
            "release_rate": fertilizer_spec.release_rate,
            "cost_per_unit": fertilizer_spec.cost_per_unit,
            "method_compatibility": self._assess_method_compatibility(fertilizer_spec.form)
        }
        return analysis
    
    async def _analyze_available_equipment(self, equipment_list: List[EquipmentSpecification]) -> Dict[str, Any]:
        """Analyze available equipment for method compatibility."""
        analysis = {
            "equipment_count": len(equipment_list),
            "equipment_types": [eq.equipment_type for eq in equipment_list],
            "capacity_analysis": self._analyze_equipment_capacity(equipment_list),
            "compatibility_matrix": self._generate_equipment_compatibility_matrix(equipment_list),
            "upgrade_recommendations": self._generate_upgrade_recommendations(equipment_list)
        }
        return analysis
    
    async def _score_application_methods(
        self, 
        field_analysis: Dict[str, Any],
        crop_analysis: Dict[str, Any],
        fertilizer_analysis: Dict[str, Any],
        equipment_analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Score application methods based on analysis results."""
        scores = {}
        
        for method_type, method_data in self.method_database.items():
            score = 0.0
            
            # Field size compatibility (25% weight)
            field_size_score = self._calculate_field_size_score(
                field_analysis["field_size_category"], method_data["field_size_range"]
            )
            score += field_size_score * 0.25
            
            # Equipment compatibility (25% weight)
            equipment_score = self._calculate_equipment_compatibility_score(
                method_data["equipment_types"], equipment_analysis["equipment_types"]
            )
            score += equipment_score * 0.25
            
            # Fertilizer form compatibility (20% weight)
            fertilizer_score = self._calculate_fertilizer_compatibility_score(
                method_data["fertilizer_forms"], fertilizer_analysis["form"]
            )
            score += fertilizer_score * 0.20
            
            # Efficiency score (15% weight)
            efficiency_score = method_data["efficiency_score"]
            score += efficiency_score * 0.15
            
            # Environmental impact (10% weight)
            environmental_score = self._calculate_environmental_score(method_data["environmental_impact"])
            score += environmental_score * 0.10
            
            # Cost effectiveness (5% weight)
            cost_score = self._calculate_cost_score(method_data["cost_per_acre"])
            score += cost_score * 0.05
            
            scores[method_type] = score
        
        return scores
    
    async def _generate_recommendations(
        self,
        method_scores: Dict[str, float],
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_spec: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> List[ApplicationMethod]:
        """Generate application method recommendations with advanced crop integration."""
        recommendations = []
        
        # Get crop type and growth stage for advanced analysis
        crop_type = self._parse_crop_type(crop_requirements.crop_type)
        growth_stage = self._parse_growth_stage(crop_requirements.growth_stage)
        
        # Sort methods by score
        sorted_methods = sorted(method_scores.items(), key=lambda x: x[1], reverse=True)
        
        for method_type, score in sorted_methods:
            if score > 0.3:  # Minimum threshold for recommendation
                method_data = self.method_database[method_type]
                
                # Enhanced crop-specific scoring
                crop_compatibility = self.crop_integration_service.assess_crop_method_compatibility(
                    crop_type, method_type
                )
                
                # Check if method is recommended for this crop and growth stage
                recommended_methods = self.crop_integration_service.get_recommended_methods_for_stage(
                    crop_type, growth_stage
                )
                avoided_methods = self.crop_integration_service.get_avoided_methods_for_stage(
                    crop_type, growth_stage
                )
                
                # Adjust score based on crop compatibility
                adjusted_score = score * crop_compatibility["compatibility_score"]
                
                # Apply penalties for avoided methods
                if method_type in avoided_methods:
                    adjusted_score *= 0.3
                
                # Apply bonuses for recommended methods
                if method_type in recommended_methods:
                    adjusted_score *= 1.2
                
                if adjusted_score > 0.3:  # Re-check threshold with adjusted score
                    # Find compatible equipment
                    compatible_equipment = self._find_compatible_equipment(
                        method_data["equipment_types"], available_equipment
                    )
                    
                    if compatible_equipment:
                        # Get enhanced application timing
                        application_timing = self._get_enhanced_application_timing(
                            crop_type, growth_stage, method_type, crop_requirements.growth_stage
                        )
                        
                        # Get crop-specific application rate
                        application_rate = self._calculate_enhanced_application_rate(
                            fertilizer_spec, crop_requirements, method_type, crop_type, growth_stage
                        )
                        
                        recommendation = ApplicationMethod(
                            method_id=f"{method_type}_{uuid4().hex[:8]}",
                            method_type=method_type,
                            recommended_equipment=compatible_equipment,
                            application_rate=application_rate,
                            rate_unit=fertilizer_spec.unit or "lbs/acre",
                            application_timing=application_timing,
                            efficiency_score=method_data["efficiency_score"],
                            cost_per_acre=method_data["cost_per_acre"],
                            labor_requirements=method_data["labor_intensity"],
                            environmental_impact=method_data["environmental_impact"],
                            pros=method_data["pros"],
                            cons=method_data["cons"],
                            crop_compatibility_score=crop_compatibility["compatibility_score"],
                            crop_compatibility_factors=crop_compatibility["factors"]
                        )
                        recommendations.append(recommendation)
        
        return recommendations
    
    def _categorize_field_size(self, field_size_acres: float) -> str:
        """Categorize field size."""
        if field_size_acres < 10:
            return "small"
        elif field_size_acres < 100:
            return "medium"
        elif field_size_acres < 1000:
            return "large"
        else:
            return "very_large"
    
    def _assess_soil_suitability(self, soil_type: str) -> Dict[str, Any]:
        """Assess soil suitability for different application methods."""
        soil_suitability = {
            "clay": {"broadcast": 0.8, "band": 0.9, "injection": 0.7, "drip": 0.6},
            "loam": {"broadcast": 0.9, "band": 0.9, "injection": 0.8, "drip": 0.8},
            "sandy": {"broadcast": 0.7, "band": 0.8, "injection": 0.9, "drip": 0.9},
            "silt": {"broadcast": 0.8, "band": 0.9, "injection": 0.8, "drip": 0.7}
        }
        return soil_suitability.get(soil_type.lower(), {"broadcast": 0.8, "band": 0.8, "injection": 0.8, "drip": 0.8})
    
    def _assess_drainage_impact(self, drainage_class: Optional[str]) -> Dict[str, Any]:
        """Assess drainage impact on application methods."""
        if not drainage_class:
            return {"impact": "unknown", "recommendations": []}
        
        drainage_impacts = {
            "well_drained": {"impact": "low", "recommendations": ["All methods suitable"]},
            "moderately_drained": {"impact": "medium", "recommendations": ["Avoid broadcast in wet conditions"]},
            "poorly_drained": {"impact": "high", "recommendations": ["Prefer band or injection methods"]}
        }
        return drainage_impacts.get(drainage_class.lower(), {"impact": "medium", "recommendations": []})
    
    def _assess_slope_impact(self, slope_percent: Optional[float]) -> Dict[str, Any]:
        """Assess slope impact on application methods."""
        if not slope_percent:
            return {"impact": "unknown", "recommendations": []}
        
        if slope_percent < 2:
            return {"impact": "low", "recommendations": ["All methods suitable"]}
        elif slope_percent < 5:
            return {"impact": "medium", "recommendations": ["Consider band application"]}
        else:
            return {"impact": "high", "recommendations": ["Avoid broadcast, prefer band or injection"]}
    
    def _assess_access_constraints(self, access_roads: Optional[List[str]]) -> Dict[str, Any]:
        """Assess access constraints for equipment."""
        if not access_roads:
            return {"constraints": "unknown", "impact": "medium"}
        
        # Simple assessment based on road availability
        if len(access_roads) > 2:
            return {"constraints": "low", "impact": "low"}
        elif len(access_roads) == 1:
            return {"constraints": "medium", "impact": "medium"}
        else:
            return {"constraints": "high", "impact": "high"}
    
    def _assess_nutrient_timing(self, growth_stage: str) -> Dict[str, Any]:
        """Assess nutrient timing requirements based on growth stage."""
        timing_requirements = {
            "emergence": {"timing": "early", "methods": ["broadcast", "band"]},
            "vegetative": {"timing": "mid", "methods": ["sidedress", "foliar"]},
            "reproductive": {"timing": "late", "methods": ["foliar", "injection"]},
            "maturity": {"timing": "very_late", "methods": ["foliar"]}
        }
        return timing_requirements.get(growth_stage.lower(), {"timing": "flexible", "methods": ["broadcast", "band"]})
    
    def _assess_method_compatibility(self, fertilizer_form: FertilizerForm) -> Dict[str, bool]:
        """Assess method compatibility with fertilizer form."""
        compatibility = {
            FertilizerForm.GRANULAR: {
                "broadcast": True, "band": True, "sidedress": True,
                "foliar": False, "injection": False, "drip": False
            },
            FertilizerForm.LIQUID: {
                "broadcast": False, "band": True, "sidedress": True,
                "foliar": True, "injection": True, "drip": True
            },
            FertilizerForm.ORGANIC: {
                "broadcast": True, "band": True, "sidedress": True,
                "foliar": False, "injection": False, "drip": False
            }
        }
        return compatibility.get(fertilizer_form, {})
    
    def _analyze_equipment_capacity(self, equipment_list: List[EquipmentSpecification]) -> Dict[str, Any]:
        """Analyze equipment capacity for field operations."""
        capacity_analysis = {
            "total_capacity": sum(eq.capacity or 0 for eq in equipment_list),
            "capacity_by_type": {},
            "adequacy_assessment": "unknown"
        }
        
        for equipment in equipment_list:
            if equipment.equipment_type not in capacity_analysis["capacity_by_type"]:
                capacity_analysis["capacity_by_type"][equipment.equipment_type] = 0
            capacity_analysis["capacity_by_type"][equipment.equipment_type] += equipment.capacity or 0
        
        return capacity_analysis
    
    def _generate_equipment_compatibility_matrix(self, equipment_list: List[EquipmentSpecification]) -> Dict[str, List[str]]:
        """Generate equipment compatibility matrix."""
        compatibility_matrix = {}
        
        for equipment in equipment_list:
            compatible_methods = []
            for method_type, method_data in self.method_database.items():
                if equipment.equipment_type in method_data["equipment_types"]:
                    compatible_methods.append(method_type)
            compatibility_matrix[equipment.equipment_type] = compatible_methods
        
        return compatibility_matrix
    
    def _generate_upgrade_recommendations(self, equipment_list: List[EquipmentSpecification]) -> List[str]:
        """Generate equipment upgrade recommendations."""
        recommendations = []
        
        # Simple upgrade recommendations based on equipment age and capacity
        for equipment in equipment_list:
            if equipment.capacity and equipment.capacity < 100:  # Low capacity
                recommendations.append(f"Consider upgrading {equipment.equipment_type} for better capacity")
        
        return recommendations
    
    def _calculate_field_size_score(self, field_size_category: str, method_range: tuple) -> float:
        """Calculate field size compatibility score."""
        size_scores = {"small": 1, "medium": 2, "large": 3, "very_large": 4}
        field_score = size_scores.get(field_size_category, 2)
        
        min_size, max_size = method_range
        if min_size <= field_score <= max_size:
            return 1.0
        else:
            return 0.5  # Partial compatibility
    
    def _calculate_equipment_compatibility_score(self, method_equipment: List[str], available_equipment: List[str]) -> float:
        """Calculate equipment compatibility score."""
        if not available_equipment:
            return 0.0
        
        compatible_count = sum(1 for eq_type in method_equipment if eq_type in available_equipment)
        return compatible_count / len(method_equipment)
    
    def _calculate_fertilizer_compatibility_score(self, method_forms: List[FertilizerForm], fertilizer_form: FertilizerForm) -> float:
        """Calculate fertilizer form compatibility score."""
        return 1.0 if fertilizer_form in method_forms else 0.0
    
    def _calculate_environmental_score(self, environmental_impact: str) -> float:
        """Calculate environmental impact score (higher is better)."""
        impact_scores = {
            "very_low": 1.0,
            "low": 0.8,
            "moderate": 0.6,
            "high": 0.4,
            "very_high": 0.2
        }
        return impact_scores.get(environmental_impact, 0.6)
    
    def _calculate_cost_score(self, cost_per_acre: float) -> float:
        """Calculate cost effectiveness score (lower cost is better)."""
        if cost_per_acre <= 15:
            return 1.0
        elif cost_per_acre <= 25:
            return 0.8
        elif cost_per_acre <= 35:
            return 0.6
        else:
            return 0.4
    
    def _find_compatible_equipment(self, method_equipment_types: List[str], available_equipment: List[EquipmentSpecification]) -> Optional[EquipmentSpecification]:
        """Find compatible equipment for the method."""
        for equipment in available_equipment:
            if equipment.equipment_type in method_equipment_types:
                return equipment
        return None
    
    def _calculate_application_rate(self, fertilizer_spec: FertilizerSpecification, crop_requirements: CropRequirements, method_type: str) -> float:
        """Calculate recommended application rate."""
        # Base rate from crop requirements
        base_rate = crop_requirements.nutrient_requirements.get("nitrogen", 100)
        
        # Adjust based on method efficiency
        efficiency_adjustments = {
            "broadcast": 1.0,
            "band": 0.8,
            "sidedress": 0.7,
            "foliar": 0.3,
            "injection": 0.8,
            "drip": 0.6
        }
        
        adjustment = efficiency_adjustments.get(method_type, 1.0)
        return base_rate * adjustment
    
    def _determine_application_timing(self, growth_stage: str, method_type: str) -> str:
        """Determine optimal application timing."""
        timing_mapping = {
            "emergence": "At planting or pre-plant",
            "vegetative": "Early to mid-season",
            "reproductive": "Mid to late season",
            "maturity": "Late season"
        }
        
        base_timing = timing_mapping.get(growth_stage.lower(), "Flexible timing")
        
        # Add method-specific timing
        if method_type == "foliar":
            return f"{base_timing} (foliar application)"
        elif method_type == "sidedress":
            return f"{base_timing} (sidedress application)"
        else:
            return base_timing
    
    async def _perform_cost_comparison(self, methods: List[ApplicationMethod]) -> Dict[str, float]:
        """Perform cost comparison across methods."""
        cost_comparison = {}
        for method in methods:
            cost_comparison[method.method_type] = method.cost_per_acre or 0.0
        return cost_comparison
    
    async def _generate_efficiency_analysis(self, methods: List[ApplicationMethod]) -> Dict[str, Any]:
        """Generate efficiency analysis."""
        efficiency_analysis = {
            "method_efficiencies": {method.method_type: method.efficiency_score for method in methods},
            "average_efficiency": sum(method.efficiency_score for method in methods) / len(methods) if methods else 0,
            "efficiency_ranking": sorted(methods, key=lambda x: x.efficiency_score, reverse=True)
        }
        return efficiency_analysis
    
    async def _generate_equipment_compatibility(self, methods: List[ApplicationMethod], available_equipment: List[EquipmentSpecification]) -> Dict[str, bool]:
        """Generate equipment compatibility matrix."""
        compatibility = {}
        for method in methods:
            equipment_type = method.recommended_equipment.equipment_type
            compatibility[method.method_type] = any(
                eq.equipment_type == equipment_type for eq in available_equipment
            )
        return compatibility
    
    def _parse_crop_type(self, crop_type_str: str) -> CropType:
        """Parse crop type string to CropType enum."""
        crop_mapping = {
            "corn": CropType.CORN,
            "maize": CropType.CORN,
            "soybean": CropType.SOYBEAN,
            "soy": CropType.SOYBEAN,
            "wheat": CropType.WHEAT,
            "tomato": CropType.TOMATO,
            "potato": CropType.POTATO,
            "rice": CropType.RICE,
            "barley": CropType.BARLEY,
            "oats": CropType.OATS,
            "sorghum": CropType.SORGHUM,
            "millet": CropType.MILLET,
            "pepper": CropType.PEPPER,
            "lettuce": CropType.LETTUCE,
            "carrot": CropType.CARROT,
            "onion": CropType.ONION,
            "sweet_potato": CropType.SWEET_POTATO,
            "cabbage": CropType.CABBAGE,
            "broccoli": CropType.BROCCOLI,
            "cauliflower": CropType.CAULIFLOWER,
            "apple": CropType.APPLE,
            "pear": CropType.PEAR,
            "peach": CropType.PEACH,
            "cherry": CropType.CHERRY,
            "grape": CropType.GRAPE,
            "strawberry": CropType.STRAWBERRY,
            "blueberry": CropType.BLUEBERRY,
            "bean": CropType.BEAN,
            "peas": CropType.PEAS,
            "lentil": CropType.LENTIL,
            "chickpea": CropType.CHICKPEA,
            "sunflower": CropType.SUNFLOWER,
            "canola": CropType.CANOLA,
            "cotton": CropType.COTTON,
            "alfalfa": CropType.ALFALFA,
            "clover": CropType.CLOVER,
            "grass_hay": CropType.GRASS_HAY,
            "sugar_beet": CropType.SUGAR_BEET,
            "sugar_cane": CropType.SUGAR_CANE,
            "tobacco": CropType.TOBACCO
        }
        return crop_mapping.get(crop_type_str.lower(), CropType.CORN)
    
    def _parse_growth_stage(self, growth_stage_str: str) -> GrowthStage:
        """Parse growth stage string to GrowthStage enum."""
        stage_mapping = {
            # General stages
            "germination": GrowthStage.GERMINATION,
            "emergence": GrowthStage.EMERGENCE,
            "seedling": GrowthStage.SEEDLING,
            "vegetative": GrowthStage.VEGETATIVE_2,
            "vegetative_1": GrowthStage.VEGETATIVE_1,
            "vegetative_2": GrowthStage.VEGETATIVE_2,
            "vegetative_3": GrowthStage.VEGETATIVE_3,
            "flowering": GrowthStage.FLOWERING,
            "pollination": GrowthStage.POLLINATION,
            "fruit_set": GrowthStage.FRUIT_SET,
            "maturity": GrowthStage.MATURITY,
            "harvest": GrowthStage.HARVEST,
            
            # Corn stages
            "v1": GrowthStage.V1,
            "v2": GrowthStage.V2,
            "v3": GrowthStage.V3,
            "v4": GrowthStage.V4,
            "v5": GrowthStage.V5,
            "v6": GrowthStage.V6,
            "vt": GrowthStage.VT,
            "r1": GrowthStage.R1,
            "r2": GrowthStage.R2,
            "r3": GrowthStage.R3,
            "r4": GrowthStage.R4,
            "r5": GrowthStage.R5,
            "r6": GrowthStage.R6,
            
            # Soybean stages
            "ve": GrowthStage.VE,
            "vc": GrowthStage.VC,
            "v1_soy": GrowthStage.V1_SOY,
            "v2_soy": GrowthStage.V2_SOY,
            "v3_soy": GrowthStage.V3_SOY,
            "v4_soy": GrowthStage.V4_SOY,
            "v5_soy": GrowthStage.V5_SOY,
            "v6_soy": GrowthStage.V6_SOY,
            "r1_soy": GrowthStage.R1_SOY,
            "r2_soy": GrowthStage.R2_SOY,
            "r3_soy": GrowthStage.R3_SOY,
            "r4_soy": GrowthStage.R4_SOY,
            "r5_soy": GrowthStage.R5_SOY,
            "r6_soy": GrowthStage.R6_SOY,
            "r7_soy": GrowthStage.R7_SOY,
            "r8_soy": GrowthStage.R8_SOY,
            
            # Wheat stages
            "tillering": GrowthStage.TILLERING,
            "jointing": GrowthStage.JOINTING
        }
        return stage_mapping.get(growth_stage_str.lower(), GrowthStage.VEGETATIVE_2)
    
    def _get_enhanced_application_timing(self, crop_type: CropType, growth_stage: GrowthStage, 
                                        method_type: str, growth_stage_str: str) -> str:
        """Get enhanced application timing based on crop and growth stage."""
        # Get crop-specific timing information
        stage_info = self.crop_integration_service.get_growth_stage_info(crop_type, growth_stage)
        
        if stage_info:
            # Use crop-specific timing preferences
            if stage_info.timing_preferences:
                base_timing = stage_info.timing_preferences[0]
            else:
                base_timing = "Flexible timing"
        else:
            # Fallback to original logic
            base_timing = self._determine_application_timing(growth_stage_str, method_type)
        
        # Add method-specific enhancements
        method_enhancements = {
            "foliar": " (foliar application - avoid during flowering)",
            "sidedress": " (sidedress application - avoid root damage)",
            "broadcast": " (broadcast application - weather dependent)",
            "band": " (band application - precise placement)",
            "injection": " (injection application - soil moisture dependent)"
        }
        
        enhancement = method_enhancements.get(method_type, "")
        return f"{base_timing}{enhancement}"
    
    def _calculate_enhanced_application_rate(self, fertilizer_spec: FertilizerSpecification, 
                                           crop_requirements: CropRequirements, method_type: str,
                                           crop_type: CropType, growth_stage: GrowthStage) -> float:
        """Calculate enhanced application rate based on crop and growth stage."""
        # Base rate from crop requirements
        base_rate = crop_requirements.nutrient_requirements.get("nitrogen", 100)
        
        # Get crop-specific nutrient uptake pattern
        nutrient_uptake = self.crop_integration_service.get_nutrient_uptake_curve(
            crop_type, "nitrogen"
        )
        
        # Adjust based on growth stage nutrient demand
        stage_info = self.crop_integration_service.get_growth_stage_info(crop_type, growth_stage)
        if stage_info:
            demand_adjustments = {
                "low": 0.8,
                "medium": 1.0,
                "high": 1.2,
                "critical": 1.3
            }
            demand_multiplier = demand_adjustments.get(stage_info.nutrient_demand_level, 1.0)
            base_rate *= demand_multiplier
        
        # Adjust based on method efficiency
        efficiency_adjustments = {
            "broadcast": 1.0,
            "band": 0.8,
            "sidedress": 0.7,
            "foliar": 0.3,
            "injection": 0.8,
            "drip": 0.6
        }
        
        adjustment = efficiency_adjustments.get(method_type, 1.0)
        return base_rate * adjustment