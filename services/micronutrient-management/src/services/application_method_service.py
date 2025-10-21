"""
Application Method Service for Micronutrient Management

This service provides logic for choosing optimal application methods (soil application, 
foliar application, seed treatment, fertigation, broadcast, banded) based on crop type,
growth stage, deficiency severity, equipment availability, and field conditions.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.micronutrient_schemas import (
    ApplicationMethodRequest,
    ApplicationMethodRecommendation,
    ApplicationMethod,
    RecommendationPriority,
    EquipmentAvailability,
    FieldCondition,
    TimingRecommendationType
)


class ApplicationMethodService:
    """
    Service class for determining optimal application methods for micronutrients.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def get_optimal_application_method(
        self, 
        request: ApplicationMethodRequest
    ) -> ApplicationMethodRecommendation:
        """
        Determine the optimal application method based on various factors.
        
        Args:
            request: ApplicationMethodRequest containing crop type, growth stage, 
                    deficiency severity, equipment, and field conditions
            
        Returns:
            ApplicationMethodRecommendation with the recommended method and details
        """
        try:
            # Determine the most appropriate application method
            recommended_method = self._determine_application_method(request)
            
            # Calculate confidence score based on how well factors align
            confidence_score = self._calculate_confidence_score(recommended_method, request)
            
            # Determine timing recommendation based on the method chosen
            timing_recommendation = self._determine_timing_recommendation(request)
            
            # Generate reason for the recommendation
            reason = self._generate_reason(recommended_method, request)
            
            # Get equipment requirements for the method
            equipment_required = self._get_equipment_required(recommended_method)
            
            # Check if field conditions are suitable
            field_conditions_suitable = self._check_field_conditions_suitability(
                recommended_method, request.field_conditions
            )
            
            # Get alternative methods
            alternative_methods = self._get_alternative_methods(recommended_method, request)
            
            recommendation = ApplicationMethodRecommendation(
                method=recommended_method,
                confidence_score=confidence_score,
                timing_recommendation=timing_recommendation,
                reason=reason,
                equipment_required=equipment_required,
                field_conditions_suitable=field_conditions_suitable,
                alternative_methods=alternative_methods
            )
            
            self.logger.info(f"Generated application method recommendation: {recommended_method}")
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Error generating application method recommendation: {str(e)}")
            raise

    def _determine_application_method(self, request: ApplicationMethodRequest) -> ApplicationMethod:
        """
        Main logic to determine the optimal application method based on input factors.
        """
        # Priority factor: equipment availability
        available_equipment = self._get_available_equipment(request.equipment_availability)
        
        # Priority factor: growth stage
        growth_stage = request.growth_stage.lower() if request.growth_stage else ""
        
        # Priority factor: deficiency severity
        severity = request.deficiency_severity
        
        # Priority factor: nutrient type properties
        nutrient_type = request.nutrient_type
        
        # Special cases for specific nutrients that have absorption preferences
        if nutrient_type in ["IRON", "MANGANESE", "ZINC"] and severity in [RecommendationPriority.CRITICAL, RecommendationPriority.HIGH]:
            # These nutrients are often more effectively applied foliarly when deficiency is critical
            if "sprayer" in available_equipment:
                return ApplicationMethod.FOLIAR_APPLICATION
        
        # Special case for seed treatment - only applicable during early growth stages
        if "seeding_equipment" in available_equipment and growth_stage in ["seedling", "germination", "early"]:
            return ApplicationMethod.SEED_TREATMENT
            
        # For critical deficiencies, foliar is often preferred for quick uptake
        if severity == RecommendationPriority.CRITICAL and "sprayer" in available_equipment:
            return ApplicationMethod.FOLIAR_APPLICATION
            
        # For fertigation, check if irrigation system is available
        if "irrigation_system" in available_equipment:
            return ApplicationMethod.FERTIGATION
            
        # For foliar application during critical periods or for mobile nutrients
        if ("sprayer" in available_equipment and 
            (severity in [RecommendationPriority.CRITICAL, RecommendationPriority.HIGH] or 
             growth_stage in ["vegetative", "vegetative growth"])):
            return ApplicationMethod.FOLIAR_APPLICATION
            
        # For banded application only during planting/early growth
        if growth_stage in ["seedling", "germination", "early"] and "fertilizer_applicator" in available_equipment:
            return ApplicationMethod.BANDED
            
        # For broadcast applications when specifically needed (e.g. pre-plant, top-dress)
        elif growth_stage in ["pre-plant", "top-dress"] and "fertilizer_applicator" in available_equipment:
            return ApplicationMethod.BROADCAST
            
        # If fertilizer applicator is available, prefer soil application as the general method
        elif "fertilizer_applicator" in available_equipment:
            return ApplicationMethod.SOIL_APPLICATION
            
        # Fallback to soil application if no specific equipment constraints
        return ApplicationMethod.SOIL_APPLICATION

    def _get_available_equipment(self, equipment: EquipmentAvailability) -> List[str]:
        """
        Convert equipment availability to a list of available equipment.
        """
        available = []
        if equipment.sprayer:
            available.append("sprayer")
        if equipment.fertilizer_applicator:
            available.append("fertilizer_applicator")
        if equipment.irrigation_system:
            available.append("irrigation_system")
        if equipment.seeding_equipment:
            available.append("seeding_equipment")
        return available

    def _calculate_confidence_score(self, method: ApplicationMethod, request: ApplicationMethodRequest) -> float:
        """
        Calculate confidence score based on how well the method matches input factors.
        """
        score = 0.5  # Base score
        
        # Equipment availability factor
        equipment_matches = {
            ApplicationMethod.FOLIAR_APPLICATION: "sprayer",
            ApplicationMethod.FERTIGATION: "irrigation_system", 
            ApplicationMethod.SEED_TREATMENT: "seeding_equipment",
            ApplicationMethod.BROADCAST: "fertilizer_applicator",
            ApplicationMethod.BANDED: "fertilizer_applicator",
            ApplicationMethod.SOIL_APPLICATION: "fertilizer_applicator"
        }
        
        if equipment_matches[method] in self._get_available_equipment(request.equipment_availability):
            score += 0.2  # Equipment available
            
        # Growth stage factor
        if method == ApplicationMethod.SEED_TREATMENT and request.growth_stage and "seed" in request.growth_stage.lower():
            score += 0.15  # Perfect timing match
        elif method == ApplicationMethod.FOLIAR_APPLICATION and request.deficiency_severity in [RecommendationPriority.CRITICAL, RecommendationPriority.HIGH]:
            score += 0.15  # Perfect need match
        elif method == ApplicationMethod.FERTIGATION and request.equipment_availability.irrigation_system:
            score += 0.15  # Perfect equipment match
            
        # Nutrient type factor
        if method == ApplicationMethod.FOLIAR_APPLICATION and request.nutrient_type in ["IRON", "MANGANESE", "ZINC"]:
            score += 0.1  # Mobile nutrients benefit from foliar
            
        # Cap the score at 1.0
        return min(1.0, score)

    def _determine_timing_recommendation(self, request: ApplicationMethodRequest) -> TimingRecommendationType:
        """
        Determine appropriate timing based on application method and conditions.
        """
        severity = request.deficiency_severity
        growth_stage = request.growth_stage.lower() if request.growth_stage else ""
        
        if severity == RecommendationPriority.CRITICAL:
            return TimingRecommendationType.IMMEDIATE
        elif growth_stage in ["vegetative", "vegetative growth", "critical uptake"]:
            return TimingRecommendationType.SHORT_TERM
        elif growth_stage in ["floring", "flowering", "fruiting"]:
            return TimingRecommendationType.MEDIUM_TERM
        else:
            return TimingRecommendationType.LONG_TERM

    def _generate_reason(self, method: ApplicationMethod, request: ApplicationMethodRequest) -> str:
        """
        Generate a human-readable reason for the application method recommendation.
        """
        reasons = []
        
        # Reason based on deficiency severity
        if request.deficiency_severity == RecommendationPriority.CRITICAL:
            reasons.append("critical deficiency requiring rapid correction")
        elif request.deficiency_severity == RecommendationPriority.HIGH:
            reasons.append("high priority deficiency requiring attention")
        
        # Reason based on growth stage
        if request.growth_stage:
            reasons.append(f"crop in {request.growth_stage} growth stage")
            
        # Reason based on equipment availability
        available_equipment = self._get_available_equipment(request.equipment_availability)
        if method == ApplicationMethod.FOLIAR_APPLICATION and "sprayer" in available_equipment:
            reasons.append("sprayer equipment available for foliar application")
        elif method == ApplicationMethod.FERTIGATION and "irrigation_system" in available_equipment:
            reasons.append("irrigation system available for fertigation")
        elif method == ApplicationMethod.SEED_TREATMENT and "seeding_equipment" in available_equipment:
            reasons.append("seeding equipment available for seed treatment")
            
        # Reason based on nutrient type
        if method == ApplicationMethod.FOLIAR_APPLICATION and request.nutrient_type in ["IRON", "MANGANESE", "ZINC"]:
            reasons.append(f"{request.nutrient_type.value} absorption is more efficient via foliar application")
            
        return f"{method.value} recommended because: {', '.join(reasons)}."

    def _get_equipment_required(self, method: ApplicationMethod) -> List[str]:
        """
        Get list of equipment required for specific application method.
        """
        equipment_map = {
            ApplicationMethod.FOLIAR_APPLICATION: ["sprayer"],
            ApplicationMethod.FERTIGATION: ["irrigation_system"],
            ApplicationMethod.SEED_TREATMENT: ["seeding_equipment"],
            ApplicationMethod.SOIL_APPLICATION: ["fertilizer_applicator"],
            ApplicationMethod.BROADCAST: ["fertilizer_applicator"],
            ApplicationMethod.BANDED: ["fertilizer_applicator"]
        }
        return equipment_map.get(method, [])

    def _check_field_conditions_suitability(self, method: ApplicationMethod, field_conditions: FieldCondition) -> bool:
        """
        Check if field conditions are suitable for the recommended method.
        """
        # For foliar applications, avoid wet conditions which reduce effectiveness
        if method == ApplicationMethod.FOLIAR_APPLICATION:
            if field_conditions.moisture in ["wet", "saturated"] or field_conditions.temperature < 40:
                return False  # Too cold or wet for foliar application
            return True  # Otherwise suitable
            
        # For soil applications, avoid waterlogged conditions
        if method in [ApplicationMethod.SOIL_APPLICATION, ApplicationMethod.BROADCAST, ApplicationMethod.BANDED]:
            if field_conditions.moisture == "saturated":
                return False  # Too wet for soil application
            if field_conditions.soil_compaction and method in [ApplicationMethod.BROADCAST, ApplicationMethod.BANDED]:
                return False  # Compacted soil may not allow proper incorporation
            return True
            
        # For fertigation, ensure adequate moisture
        if method == ApplicationMethod.FERTIGATION:
            if field_conditions.moisture == "dry":
                return False  # Need moisture for fertigation effectiveness
            return True
            
        return True  # Default to suitable

    def _get_alternative_methods(self, primary_method: ApplicationMethod, request: ApplicationMethodRequest) -> List[ApplicationMethod]:
        """
        Get alternative application methods based on available equipment and conditions.
        """
        alternatives = []
        available_equipment = self._get_available_equipment(request.equipment_availability)
        
        # Add alternatives based on available equipment
        if "sprayer" in available_equipment and primary_method != ApplicationMethod.FOLIAR_APPLICATION:
            alternatives.append(ApplicationMethod.FOLIAR_APPLICATION)
        if "irrigation_system" in available_equipment and primary_method != ApplicationMethod.FERTIGATION:
            alternatives.append(ApplicationMethod.FERTIGATION)
        if "seeding_equipment" in available_equipment and primary_method != ApplicationMethod.SEED_TREATMENT:
            alternatives.append(ApplicationMethod.SEED_TREATMENT)
        if "fertilizer_applicator" in available_equipment:
            if primary_method != ApplicationMethod.SOIL_APPLICATION:
                alternatives.append(ApplicationMethod.SOIL_APPLICATION)
            if primary_method != ApplicationMethod.BROADCAST:
                alternatives.append(ApplicationMethod.BROADCAST)
            if primary_method != ApplicationMethod.BANDED:
                alternatives.append(ApplicationMethod.BANDED)
                
        # Limit to top 3 alternatives
        return alternatives[:3]