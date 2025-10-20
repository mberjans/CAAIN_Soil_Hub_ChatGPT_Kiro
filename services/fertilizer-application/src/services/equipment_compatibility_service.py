"""
Equipment Compatibility Service - Multi-factor compatibility matching engine.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
import asyncio

from src.models.equipment_models import (
    Equipment, EquipmentCategory, FertilizerFormulation, ApplicationMethodType,
    CompatibilityLevel, CompatibilityFactor, CompatibilityMatrix,
    EquipmentRecommendation, CostBenefit, FertilizerEquipmentMapping,
    EquipmentRequirements, EquipmentCapabilities
)
from src.database.equipment_compatibility_db import EquipmentCompatibilityDatabase

logger = logging.getLogger(__name__)


class EquipmentCompatibilityService:
    """
    Comprehensive equipment compatibility matching engine with multi-factor scoring.
    """

    def __init__(self):
        self.db = EquipmentCompatibilityDatabase()
        self._initialize_scoring_weights()

    def _initialize_scoring_weights(self):
        """Initialize weights for multi-factor scoring algorithm."""
        self.scoring_weights = {
            "fertilizer_type_compatibility": 0.25,
            "field_size_suitability": 0.20,
            "soil_type_compatibility": 0.10,
            "application_rate_capability": 0.15,
            "weather_resilience": 0.10,
            "cost_effectiveness": 0.10,
            "labor_requirements": 0.05,
            "equipment_availability": 0.05
        }

    async def assess_compatibility(
        self,
        equipment: Equipment,
        fertilizer_type: FertilizerFormulation,
        application_method: ApplicationMethodType,
        field_size_acres: float,
        soil_type: str,
        weather_conditions: Optional[Dict[str, Any]] = None,
        cost_constraints: Optional[float] = None
    ) -> CompatibilityMatrix:
        """
        Assess comprehensive compatibility for specific fertilizer and equipment combination.

        Args:
            equipment: Equipment to assess
            fertilizer_type: Type of fertilizer formulation
            application_method: Desired application method
            field_size_acres: Field size in acres
            soil_type: Soil type classification
            weather_conditions: Current weather conditions
            cost_constraints: Budget constraints

        Returns:
            CompatibilityMatrix with detailed multi-factor assessment
        """
        try:
            logger.info(f"Assessing compatibility for equipment {equipment.equipment_id}")

            # Evaluate individual compatibility factors
            compatibility_factors = await self._evaluate_compatibility_factors(
                equipment, fertilizer_type, application_method, field_size_acres,
                soil_type, weather_conditions, cost_constraints
            )

            # Calculate individual scores
            fertilizer_score = await self._calculate_fertilizer_compatibility_score(
                equipment, fertilizer_type
            )
            field_size_score = await self._calculate_field_size_score(
                equipment, field_size_acres
            )
            soil_type_score = await self._calculate_soil_type_score(
                equipment, soil_type
            )
            weather_score = await self._calculate_weather_score(
                equipment, weather_conditions or {}
            )
            cost_score = await self._calculate_cost_efficiency_score(
                equipment, field_size_acres, cost_constraints
            )
            labor_score = await self._calculate_labor_requirement_score(equipment)

            # Calculate overall weighted score
            overall_score = self._calculate_weighted_score(compatibility_factors)

            # Determine compatibility level
            compatibility_level = self._determine_compatibility_level(overall_score)

            # Identify constraints and warnings
            constraints = await self._identify_constraints(
                equipment, fertilizer_type, application_method, field_size_acres
            )
            warnings = await self._identify_warnings(
                equipment, fertilizer_type, compatibility_level
            )

            compatibility_matrix = CompatibilityMatrix(
                matrix_id=str(uuid4()),
                equipment_id=equipment.equipment_id,
                fertilizer_type=fertilizer_type,
                application_method=application_method,
                compatibility_factors=compatibility_factors,
                overall_compatibility_score=overall_score,
                compatibility_level=compatibility_level,
                field_size_score=field_size_score,
                soil_type_score=soil_type_score,
                weather_score=weather_score,
                cost_efficiency_score=cost_score,
                labor_requirement_score=labor_score,
                constraints=constraints,
                warnings=warnings
            )

            return compatibility_matrix

        except Exception as e:
            logger.error(f"Error in compatibility assessment: {e}")
            raise

    async def recommend_equipment(
        self,
        fertilizer_type: FertilizerFormulation,
        application_method: ApplicationMethodType,
        field_size_acres: float,
        soil_type: str,
        weather_conditions: Optional[Dict[str, Any]] = None,
        cost_constraints: Optional[float] = None,
        available_equipment: Optional[List[Equipment]] = None,
        top_n: int = 5
    ) -> List[EquipmentRecommendation]:
        """
        Get ranked equipment recommendations for fertilizer plan.

        Args:
            fertilizer_type: Type of fertilizer
            application_method: Desired application method
            field_size_acres: Field size in acres
            soil_type: Soil type
            weather_conditions: Weather conditions
            cost_constraints: Budget constraints
            available_equipment: List of available equipment (if None, recommends all)
            top_n: Number of top recommendations to return

        Returns:
            List of ranked equipment recommendations
        """
        try:
            logger.info(f"Generating equipment recommendations for {fertilizer_type}")

            # Get candidate equipment
            if available_equipment:
                candidates = available_equipment
            else:
                candidates = await self._get_candidate_equipment(
                    fertilizer_type, application_method
                )

            # Assess each candidate
            assessments = []
            for equipment in candidates:
                compatibility_matrix = await self.assess_compatibility(
                    equipment, fertilizer_type, application_method,
                    field_size_acres, soil_type, weather_conditions, cost_constraints
                )

                # Only include compatible equipment
                if compatibility_matrix.overall_compatibility_score >= 0.3:
                    assessments.append((equipment, compatibility_matrix))

            # Rank and create recommendations
            recommendations = await self._create_ranked_recommendations(
                assessments, field_size_acres, cost_constraints
            )

            # Return top N recommendations
            return recommendations[:top_n]

        except Exception as e:
            logger.error(f"Error generating equipment recommendations: {e}")
            raise

    async def get_compatibility_matrix_full(
        self,
        fertilizer_types: Optional[List[FertilizerFormulation]] = None,
        equipment_categories: Optional[List[EquipmentCategory]] = None
    ) -> Dict[str, Any]:
        """
        Get full compatibility matrix for all or selected fertilizer-equipment combinations.

        Args:
            fertilizer_types: List of fertilizer types (None for all)
            equipment_categories: List of equipment categories (None for all)

        Returns:
            Complete compatibility matrix data
        """
        try:
            # Use all types if not specified
            if not fertilizer_types:
                fertilizer_types = list(FertilizerFormulation)
            if not equipment_categories:
                equipment_categories = list(EquipmentCategory)

            matrix_data = {}
            for fert_type in fertilizer_types:
                matrix_data[fert_type.value] = {}
                for equip_cat in equipment_categories:
                    compat_data = self.db.get_compatibility(fert_type, equip_cat)
                    matrix_data[fert_type.value][equip_cat.value] = compat_data

            return {
                "compatibility_matrix": matrix_data,
                "fertilizer_types": [ft.value for ft in fertilizer_types],
                "equipment_categories": [ec.value for ec in equipment_categories]
            }

        except Exception as e:
            logger.error(f"Error generating compatibility matrix: {e}")
            raise

    async def optimize_equipment_selection(
        self,
        fields: List[Dict[str, Any]],
        budget_constraint: Optional[float] = None,
        existing_equipment: Optional[List[Equipment]] = None
    ) -> Dict[str, Any]:
        """
        Optimize equipment selection for multiple fields.

        Args:
            fields: List of field specifications with fertilizer requirements
            budget_constraint: Total budget constraint
            existing_equipment: Existing equipment inventory

        Returns:
            Optimized equipment selection plan
        """
        try:
            logger.info(f"Optimizing equipment selection for {len(fields)} fields")

            # Analyze field requirements
            field_requirements = await self._analyze_field_requirements(fields)

            # Determine equipment needs
            equipment_needs = await self._determine_equipment_needs(
                field_requirements, existing_equipment
            )

            # Generate equipment recommendations
            all_recommendations = []
            for need in equipment_needs:
                recommendations = await self.recommend_equipment(
                    fertilizer_type=need["fertilizer_type"],
                    application_method=need["application_method"],
                    field_size_acres=need["total_acres"],
                    soil_type=need["soil_type"],
                    cost_constraints=budget_constraint,
                    top_n=3
                )
                all_recommendations.extend(recommendations)

            # Optimize selection based on budget and coverage
            optimized_selection = await self._optimize_selection(
                all_recommendations, field_requirements, budget_constraint
            )

            # Generate implementation plan
            implementation_plan = await self._generate_implementation_plan(
                optimized_selection, fields
            )

            return {
                "field_requirements": field_requirements,
                "equipment_needs": equipment_needs,
                "recommended_equipment": optimized_selection,
                "implementation_plan": implementation_plan,
                "total_cost": sum(rec.cost_benefit.initial_investment
                                for rec in optimized_selection),
                "budget_constraint": budget_constraint,
                "budget_utilization": self._calculate_budget_utilization(
                    optimized_selection, budget_constraint
                )
            }

        except Exception as e:
            logger.error(f"Error optimizing equipment selection: {e}")
            raise

    async def _evaluate_compatibility_factors(
        self,
        equipment: Equipment,
        fertilizer_type: FertilizerFormulation,
        application_method: ApplicationMethodType,
        field_size_acres: float,
        soil_type: str,
        weather_conditions: Dict[str, Any],
        cost_constraints: Optional[float]
    ) -> List[CompatibilityFactor]:
        """Evaluate all individual compatibility factors."""
        factors = []

        # Factor 1: Fertilizer Type Compatibility
        fert_compat = await self._evaluate_fertilizer_compatibility(
            equipment, fertilizer_type
        )
        factors.append(CompatibilityFactor(
            factor_name="fertilizer_type_compatibility",
            factor_weight=self.scoring_weights["fertilizer_type_compatibility"],
            score=fert_compat["score"],
            justification=fert_compat["justification"],
            improvement_suggestions=fert_compat["suggestions"]
        ))

        # Factor 2: Field Size Suitability
        field_size_compat = await self._evaluate_field_size_suitability(
            equipment, field_size_acres
        )
        factors.append(CompatibilityFactor(
            factor_name="field_size_suitability",
            factor_weight=self.scoring_weights["field_size_suitability"],
            score=field_size_compat["score"],
            justification=field_size_compat["justification"],
            improvement_suggestions=field_size_compat["suggestions"]
        ))

        # Factor 3: Soil Type Compatibility
        soil_compat = await self._evaluate_soil_compatibility(equipment, soil_type)
        factors.append(CompatibilityFactor(
            factor_name="soil_type_compatibility",
            factor_weight=self.scoring_weights["soil_type_compatibility"],
            score=soil_compat["score"],
            justification=soil_compat["justification"],
            improvement_suggestions=soil_compat["suggestions"]
        ))

        # Factor 4: Application Rate Capability
        rate_compat = await self._evaluate_application_rate_capability(
            equipment, field_size_acres
        )
        factors.append(CompatibilityFactor(
            factor_name="application_rate_capability",
            factor_weight=self.scoring_weights["application_rate_capability"],
            score=rate_compat["score"],
            justification=rate_compat["justification"],
            improvement_suggestions=rate_compat["suggestions"]
        ))

        # Factor 5: Weather Resilience
        weather_compat = await self._evaluate_weather_resilience(
            equipment, weather_conditions
        )
        factors.append(CompatibilityFactor(
            factor_name="weather_resilience",
            factor_weight=self.scoring_weights["weather_resilience"],
            score=weather_compat["score"],
            justification=weather_compat["justification"],
            improvement_suggestions=weather_compat["suggestions"]
        ))

        # Factor 6: Cost Effectiveness
        cost_compat = await self._evaluate_cost_effectiveness(
            equipment, field_size_acres, cost_constraints
        )
        factors.append(CompatibilityFactor(
            factor_name="cost_effectiveness",
            factor_weight=self.scoring_weights["cost_effectiveness"],
            score=cost_compat["score"],
            justification=cost_compat["justification"],
            improvement_suggestions=cost_compat["suggestions"]
        ))

        # Factor 7: Labor Requirements
        labor_compat = await self._evaluate_labor_requirements(equipment)
        factors.append(CompatibilityFactor(
            factor_name="labor_requirements",
            factor_weight=self.scoring_weights["labor_requirements"],
            score=labor_compat["score"],
            justification=labor_compat["justification"],
            improvement_suggestions=labor_compat["suggestions"]
        ))

        # Factor 8: Equipment Availability
        availability_compat = await self._evaluate_equipment_availability(equipment)
        factors.append(CompatibilityFactor(
            factor_name="equipment_availability",
            factor_weight=self.scoring_weights["equipment_availability"],
            score=availability_compat["score"],
            justification=availability_compat["justification"],
            improvement_suggestions=availability_compat["suggestions"]
        ))

        return factors

    async def _evaluate_fertilizer_compatibility(
        self, equipment: Equipment, fertilizer_type: FertilizerFormulation
    ) -> Dict[str, Any]:
        """Evaluate fertilizer type compatibility."""
        compat_data = self.db.get_compatibility(fertilizer_type, equipment.category)

        score = compat_data.get("score", 0.0)
        limitations = compat_data.get("limitations", [])
        best_practices = compat_data.get("best_practices", [])

        if score >= 0.9:
            justification = f"Highly compatible - {equipment.category.value} is ideal for {fertilizer_type.value}"
        elif score >= 0.7:
            justification = f"Compatible - {equipment.category.value} works well with {fertilizer_type.value}"
        elif score >= 0.5:
            justification = f"Moderately compatible - Some limitations exist"
        else:
            justification = f"Incompatible - {equipment.category.value} not suitable for {fertilizer_type.value}"

        suggestions = []
        if score < 0.9 and best_practices:
            suggestions.append(f"Follow best practices: {', '.join(best_practices[:2])}")
        if limitations:
            suggestions.append(f"Address limitations: {', '.join(limitations[:2])}")

        return {
            "score": score,
            "justification": justification,
            "suggestions": suggestions
        }

    async def _evaluate_field_size_suitability(
        self, equipment: Equipment, field_size_acres: float
    ) -> Dict[str, Any]:
        """Evaluate field size suitability."""
        # Get equipment specs from database
        equipment_type = self._determine_equipment_type(equipment)
        specs = self.db.get_equipment_specs(equipment_type)

        if not specs:
            return {"score": 0.5, "justification": "Unknown equipment specifications", "suggestions": []}

        field_suitability = specs.get("field_size_suitability", {})
        min_size = field_suitability.get("min", 0)
        max_size = field_suitability.get("max", 10000)
        optimal_size = field_suitability.get("optimal", 100)

        # Calculate score based on field size fit
        if min_size <= field_size_acres <= max_size:
            # Within range - calculate how close to optimal
            deviation = abs(field_size_acres - optimal_size) / optimal_size
            score = max(0.6, 1.0 - (deviation * 0.4))

            if deviation < 0.2:
                justification = f"Field size ({field_size_acres} acres) is optimal for this equipment"
            else:
                justification = f"Field size ({field_size_acres} acres) is suitable but not optimal"
        elif field_size_acres < min_size:
            score = 0.3
            justification = f"Field size ({field_size_acres} acres) is below minimum ({min_size} acres)"
        else:
            score = 0.4
            justification = f"Field size ({field_size_acres} acres) exceeds maximum ({max_size} acres)"

        suggestions = []
        if field_size_acres < min_size:
            suggestions.append(f"Consider smaller equipment suitable for {field_size_acres} acres")
        elif field_size_acres > max_size:
            suggestions.append(f"Consider larger equipment or multiple passes")

        return {
            "score": score,
            "justification": justification,
            "suggestions": suggestions
        }

    async def _evaluate_soil_compatibility(
        self, equipment: Equipment, soil_type: str
    ) -> Dict[str, Any]:
        """Evaluate soil type compatibility."""
        # Most equipment works with all soil types, but some have preferences
        soil_scores = {
            "clay": 0.85,
            "loam": 1.0,
            "sandy": 0.90,
            "silt": 0.95,
            "organic": 0.80
        }

        score = soil_scores.get(soil_type.lower(), 0.75)

        if score >= 0.9:
            justification = f"Excellent compatibility with {soil_type} soil"
        else:
            justification = f"Good compatibility with {soil_type} soil"

        suggestions = []
        if score < 0.9:
            suggestions.append(f"Adjust application rates for {soil_type} soil characteristics")

        return {
            "score": score,
            "justification": justification,
            "suggestions": suggestions
        }

    async def _evaluate_application_rate_capability(
        self, equipment: Equipment, field_size_acres: float
    ) -> Dict[str, Any]:
        """Evaluate application rate capability."""
        # Base score on equipment capacity and field size
        if not equipment.capacity:
            return {"score": 0.5, "justification": "Unknown capacity", "suggestions": []}

        # Calculate if equipment can handle field in reasonable time
        equipment_type = self._determine_equipment_type(equipment)
        specs = self.db.get_equipment_specs(equipment_type)

        if specs:
            coverage_rate = specs.get("coverage_rate", {})
            max_rate = coverage_rate.get("max", 10)

            # Calculate estimated time to cover field
            estimated_hours = field_size_acres / max_rate

            if estimated_hours <= 4:
                score = 1.0
                justification = f"Can cover field in {estimated_hours:.1f} hours - excellent"
            elif estimated_hours <= 8:
                score = 0.85
                justification = f"Can cover field in {estimated_hours:.1f} hours - good"
            elif estimated_hours <= 16:
                score = 0.70
                justification = f"Requires {estimated_hours:.1f} hours - acceptable"
            else:
                score = 0.50
                justification = f"Requires {estimated_hours:.1f} hours - consider larger equipment"
        else:
            score = 0.75
            justification = "Adequate application rate capability"

        suggestions = []
        if score < 0.8:
            suggestions.append("Consider equipment with higher coverage rate")

        return {
            "score": score,
            "justification": justification,
            "suggestions": suggestions
        }

    async def _evaluate_weather_resilience(
        self, equipment: Equipment, weather_conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate weather resilience."""
        wind_speed = weather_conditions.get("wind_speed_mph", 5)
        temperature = weather_conditions.get("temperature_f", 70)
        humidity = weather_conditions.get("humidity_percent", 50)

        # Different equipment types have different weather sensitivities
        if equipment.category == EquipmentCategory.SPRAYING:
            # Sprayers very sensitive to wind
            if wind_speed > 15:
                score = 0.3
                justification = "High wind speeds reduce spray effectiveness"
            elif wind_speed > 10:
                score = 0.6
                justification = "Moderate wind speeds may affect spray pattern"
            else:
                score = 0.9
                justification = "Weather conditions suitable for spraying"
        elif equipment.category == EquipmentCategory.SPREADING:
            # Spreaders moderately sensitive to wind
            if wind_speed > 20:
                score = 0.4
                justification = "High winds may cause drift"
            elif wind_speed > 12:
                score = 0.7
                justification = "Moderate winds acceptable with caution"
            else:
                score = 0.95
                justification = "Good weather conditions for spreading"
        else:
            # Injection and drip systems less weather sensitive
            score = 0.95
            justification = "Weather conditions have minimal impact"

        suggestions = []
        if score < 0.7:
            suggestions.append("Consider delaying application until weather improves")
            suggestions.append("Adjust application parameters for current conditions")

        return {
            "score": score,
            "justification": justification,
            "suggestions": suggestions
        }

    async def _evaluate_cost_effectiveness(
        self, equipment: Equipment, field_size_acres: float,
        cost_constraints: Optional[float]
    ) -> Dict[str, Any]:
        """Evaluate cost effectiveness."""
        equipment_type = self._determine_equipment_type(equipment)
        cost_data = self.db.get_cost_data(equipment_type)

        if not cost_data:
            return {"score": 0.5, "justification": "Unknown cost data", "suggestions": []}

        cost_per_acre = cost_data.get("cost_per_acre", {}).get("typical", 2.0)
        total_cost = cost_per_acre * field_size_acres

        # Evaluate against constraints
        if cost_constraints:
            if total_cost <= cost_constraints * 0.7:
                score = 1.0
                justification = f"Very cost-effective at ${cost_per_acre:.2f}/acre"
            elif total_cost <= cost_constraints:
                score = 0.8
                justification = f"Cost-effective at ${cost_per_acre:.2f}/acre, within budget"
            else:
                score = 0.4
                justification = f"Exceeds budget at ${cost_per_acre:.2f}/acre"
        else:
            # No constraint - evaluate based on typical costs
            if cost_per_acre <= 1.5:
                score = 1.0
                justification = f"Excellent value at ${cost_per_acre:.2f}/acre"
            elif cost_per_acre <= 3.0:
                score = 0.8
                justification = f"Good value at ${cost_per_acre:.2f}/acre"
            else:
                score = 0.6
                justification = f"Moderate cost at ${cost_per_acre:.2f}/acre"

        suggestions = []
        if score < 0.7:
            suggestions.append("Consider alternative equipment to reduce costs")
            suggestions.append("Explore equipment sharing or rental options")

        return {
            "score": score,
            "justification": justification,
            "suggestions": suggestions
        }

    async def _evaluate_labor_requirements(self, equipment: Equipment) -> Dict[str, Any]:
        """Evaluate labor requirements."""
        # Base on equipment automation level and complexity
        equipment_type = self._determine_equipment_type(equipment)
        specs = self.db.get_equipment_specs(equipment_type)

        if specs:
            automation = specs.get("automation_level", "manual")
            if automation == "automatic":
                score = 1.0
                justification = "Fully automatic - minimal labor required"
            elif automation == "semi-automatic":
                score = 0.85
                justification = "Semi-automatic - moderate labor required"
            else:
                score = 0.70
                justification = "Manual operation - higher labor required"
        else:
            score = 0.75
            justification = "Standard labor requirements"

        suggestions = []
        if score < 0.85:
            suggestions.append("Consider equipment with higher automation")

        return {
            "score": score,
            "justification": justification,
            "suggestions": suggestions
        }

    async def _evaluate_equipment_availability(self, equipment: Equipment) -> Dict[str, Any]:
        """Evaluate equipment availability."""
        # Base on equipment status
        if equipment.status.value == "operational":
            score = 1.0
            justification = "Equipment is operational and available"
        elif equipment.status.value == "maintenance_required":
            score = 0.7
            justification = "Equipment requires maintenance before use"
        elif equipment.status.value == "out_of_service":
            score = 0.2
            justification = "Equipment is out of service"
        else:
            score = 0.5
            justification = "Equipment availability uncertain"

        suggestions = []
        if score < 0.8:
            suggestions.append("Schedule equipment maintenance or repair")
            suggestions.append("Consider backup equipment options")

        return {
            "score": score,
            "justification": justification,
            "suggestions": suggestions
        }

    def _calculate_weighted_score(self, factors: List[CompatibilityFactor]) -> float:
        """Calculate overall weighted compatibility score."""
        total_score = 0.0
        total_weight = 0.0

        for factor in factors:
            total_score += factor.score * factor.factor_weight
            total_weight += factor.factor_weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def _determine_compatibility_level(self, score: float) -> CompatibilityLevel:
        """Determine compatibility level from score."""
        if score >= 0.85:
            return CompatibilityLevel.HIGHLY_COMPATIBLE
        elif score >= 0.70:
            return CompatibilityLevel.COMPATIBLE
        elif score >= 0.50:
            return CompatibilityLevel.MODERATELY_COMPATIBLE
        elif score >= 0.30:
            return CompatibilityLevel.POORLY_COMPATIBLE
        else:
            return CompatibilityLevel.INCOMPATIBLE

    async def _identify_constraints(
        self, equipment: Equipment, fertilizer_type: FertilizerFormulation,
        application_method: ApplicationMethodType, field_size_acres: float
    ) -> List[str]:
        """Identify compatibility constraints."""
        constraints = []

        # Get compatibility data
        compat_data = self.db.get_compatibility(fertilizer_type, equipment.category)

        # Add limitations as constraints
        limitations = compat_data.get("limitations", [])
        constraints.extend(limitations)

        # Add special requirements
        special_reqs = compat_data.get("special_requirements", [])
        if special_reqs:
            constraints.append(f"Special requirements: {', '.join(special_reqs)}")

        # Add field size constraints if applicable
        equipment_type = self._determine_equipment_type(equipment)
        specs = self.db.get_equipment_specs(equipment_type)
        if specs:
            field_suitability = specs.get("field_size_suitability", {})
            min_size = field_suitability.get("min", 0)
            max_size = field_suitability.get("max", 10000)

            if field_size_acres < min_size:
                constraints.append(f"Field size below equipment minimum ({min_size} acres)")
            elif field_size_acres > max_size:
                constraints.append(f"Field size exceeds equipment maximum ({max_size} acres)")

        return constraints

    async def _identify_warnings(
        self, equipment: Equipment, fertilizer_type: FertilizerFormulation,
        compatibility_level: CompatibilityLevel
    ) -> List[str]:
        """Identify important warnings."""
        warnings = []

        # Warn on poor compatibility
        if compatibility_level in [CompatibilityLevel.POORLY_COMPATIBLE,
                                   CompatibilityLevel.INCOMPATIBLE]:
            warnings.append("Low compatibility - consider alternative equipment")

        # Get compatibility data for specific warnings
        compat_data = self.db.get_compatibility(fertilizer_type, equipment.category)
        score = compat_data.get("score", 0.0)

        if score < 0.5:
            warnings.append("This combination is not recommended")

        # Equipment status warnings
        if equipment.status.value == "maintenance_required":
            warnings.append("Equipment requires maintenance before use")
        elif equipment.status.value == "out_of_service":
            warnings.append("Equipment is currently out of service")

        return warnings

    async def _calculate_fertilizer_compatibility_score(
        self, equipment: Equipment, fertilizer_type: FertilizerFormulation
    ) -> float:
        """Calculate fertilizer compatibility score."""
        compat_data = self.db.get_compatibility(fertilizer_type, equipment.category)
        return compat_data.get("score", 0.0)

    async def _calculate_field_size_score(
        self, equipment: Equipment, field_size_acres: float
    ) -> float:
        """Calculate field size suitability score."""
        result = await self._evaluate_field_size_suitability(equipment, field_size_acres)
        return result["score"]

    async def _calculate_soil_type_score(
        self, equipment: Equipment, soil_type: str
    ) -> float:
        """Calculate soil type compatibility score."""
        result = await self._evaluate_soil_compatibility(equipment, soil_type)
        return result["score"]

    async def _calculate_weather_score(
        self, equipment: Equipment, weather_conditions: Dict[str, Any]
    ) -> float:
        """Calculate weather resilience score."""
        result = await self._evaluate_weather_resilience(equipment, weather_conditions)
        return result["score"]

    async def _calculate_cost_efficiency_score(
        self, equipment: Equipment, field_size_acres: float,
        cost_constraints: Optional[float]
    ) -> float:
        """Calculate cost efficiency score."""
        result = await self._evaluate_cost_effectiveness(
            equipment, field_size_acres, cost_constraints
        )
        return result["score"]

    async def _calculate_labor_requirement_score(self, equipment: Equipment) -> float:
        """Calculate labor requirement score."""
        result = await self._evaluate_labor_requirements(equipment)
        return result["score"]

    def _determine_equipment_type(self, equipment: Equipment) -> str:
        """Determine equipment type identifier from equipment object."""
        # Map equipment characteristics to database equipment types
        if not equipment.capacity:
            return "unknown"

        category = equipment.category
        capacity = equipment.capacity

        # Determine size category based on capacity
        if category == EquipmentCategory.SPREADING:
            if capacity < 200:
                return "broadcast_spreader_small"
            elif capacity < 800:
                return "broadcast_spreader_medium"
            else:
                return "broadcast_spreader_large"
        elif category == EquipmentCategory.SPRAYING:
            if capacity < 200:
                return "boom_sprayer_small"
            elif capacity < 800:
                return "boom_sprayer_medium"
            else:
                return "boom_sprayer_large"
        elif category == EquipmentCategory.INJECTION:
            if capacity < 50:
                return "injection_system_small"
            elif capacity < 200:
                return "injection_system_medium"
            else:
                return "injection_system_large"
        elif category == EquipmentCategory.IRRIGATION:
            if capacity < 10:
                return "drip_system_small"
            elif capacity < 50:
                return "drip_system_medium"
            else:
                return "drip_system_large"

        return "unknown"

    async def _get_candidate_equipment(
        self, fertilizer_type: FertilizerFormulation,
        application_method: ApplicationMethodType
    ) -> List[Equipment]:
        """Get candidate equipment for fertilizer and application method."""
        # Get compatible equipment types from database
        equipment_types = self.db.get_all_equipment_for_fertilizer(fertilizer_type)

        # Create Equipment objects for candidates
        candidates = []
        for eq_type in equipment_types:
            specs = self.db.get_equipment_specs(eq_type)
            if specs and application_method in specs.get("application_methods", []):
                # Create equipment object from specs
                equipment = Equipment(
                    equipment_id=eq_type,
                    name=specs["name"],
                    category=specs["category"],
                    capacity=specs["capacity"]["max"],
                    capacity_unit=specs["capacity"]["unit"],
                    status="operational"
                )
                candidates.append(equipment)

        return candidates

    async def _create_ranked_recommendations(
        self, assessments: List[Tuple[Equipment, CompatibilityMatrix]],
        field_size_acres: float, cost_constraints: Optional[float]
    ) -> List[EquipmentRecommendation]:
        """Create and rank equipment recommendations."""
        recommendations = []

        for equipment, compat_matrix in assessments:
            # Calculate cost-benefit
            cost_benefit = await self._calculate_cost_benefit(
                equipment, field_size_acres
            )

            # Generate justification
            justification = await self._generate_recommendation_justification(
                compat_matrix, cost_benefit
            )

            # Identify advantages and disadvantages
            advantages, disadvantages = await self._identify_pros_cons(
                equipment, compat_matrix
            )

            # Create recommendation
            recommendation = EquipmentRecommendation(
                recommendation_id=str(uuid4()),
                equipment=equipment,
                compatibility_matrix=compat_matrix,
                overall_score=compat_matrix.overall_compatibility_score,
                ranking=1,  # Will be updated after sorting
                justification=justification,
                advantages=advantages,
                disadvantages=disadvantages,
                cost_benefit=cost_benefit,
                implementation_considerations=await self._get_implementation_considerations(equipment),
                training_requirements=await self._get_training_requirements(equipment),
                maintenance_impact=await self._get_maintenance_impact(equipment),
                confidence_level=compat_matrix.overall_compatibility_score
            )
            recommendations.append(recommendation)

        # Sort by overall score
        recommendations.sort(key=lambda x: x.overall_score, reverse=True)

        # Update rankings
        for i, rec in enumerate(recommendations):
            rec.ranking = i + 1

        return recommendations

    async def _calculate_cost_benefit(
        self, equipment: Equipment, field_size_acres: float
    ) -> CostBenefit:
        """Calculate cost-benefit analysis."""
        equipment_type = self._determine_equipment_type(equipment)
        cost_data = self.db.get_cost_data(equipment_type)

        if not cost_data:
            # Default values if no cost data
            return CostBenefit(
                initial_investment=10000.0,
                annual_operating_cost=1000.0,
                annual_savings=500.0,
                payback_period_years=20.0,
                roi_percentage=5.0,
                break_even_acres=100.0,
                cost_per_acre=2.0
            )

        purchase_price = cost_data.get("purchase_price", {}).get("typical", 10000)
        operating_cost_per_hour = cost_data.get("operating_cost_per_hour", {}).get("typical", 20)
        maintenance_cost_annual = cost_data.get("maintenance_cost_annual", {}).get("typical", 500)
        cost_per_acre = cost_data.get("cost_per_acre", {}).get("typical", 2.0)

        # Estimate annual costs based on field size
        estimated_hours_per_year = field_size_acres / 10  # Assume 10 acres/hour average
        annual_operating_cost = (operating_cost_per_hour * estimated_hours_per_year +
                                maintenance_cost_annual)

        # Estimate savings (assume 15% efficiency improvement)
        annual_savings = annual_operating_cost * 0.15

        # Calculate payback period
        payback_period = purchase_price / annual_savings if annual_savings > 0 else 999

        # Calculate ROI
        roi_percentage = (annual_savings / purchase_price) * 100 if purchase_price > 0 else 0

        # Calculate break-even acres
        break_even_acres = purchase_price / cost_per_acre if cost_per_acre > 0 else 0

        return CostBenefit(
            initial_investment=purchase_price,
            annual_operating_cost=annual_operating_cost,
            annual_savings=annual_savings,
            payback_period_years=payback_period,
            roi_percentage=roi_percentage,
            break_even_acres=break_even_acres,
            cost_per_acre=cost_per_acre
        )

    async def _generate_recommendation_justification(
        self, compat_matrix: CompatibilityMatrix, cost_benefit: CostBenefit
    ) -> str:
        """Generate detailed justification for recommendation."""
        parts = []

        # Compatibility assessment
        if compat_matrix.compatibility_level == CompatibilityLevel.HIGHLY_COMPATIBLE:
            parts.append("Highly compatible with fertilizer and field requirements")
        elif compat_matrix.compatibility_level == CompatibilityLevel.COMPATIBLE:
            parts.append("Compatible with good performance expected")
        else:
            parts.append("Moderate compatibility with some limitations")

        # Cost justification
        if cost_benefit.payback_period_years <= 3:
            parts.append(f"Excellent ROI with {cost_benefit.payback_period_years:.1f} year payback")
        elif cost_benefit.payback_period_years <= 5:
            parts.append(f"Good ROI with {cost_benefit.payback_period_years:.1f} year payback")

        # Performance highlights
        if compat_matrix.field_size_score >= 0.9:
            parts.append("Well-suited for field size")

        return ". ".join(parts) + "."

    async def _identify_pros_cons(
        self, equipment: Equipment, compat_matrix: CompatibilityMatrix
    ) -> Tuple[List[str], List[str]]:
        """Identify advantages and disadvantages."""
        advantages = []
        disadvantages = []

        # Analyze compatibility factors
        for factor in compat_matrix.compatibility_factors:
            if factor.score >= 0.9:
                advantages.append(f"Excellent {factor.factor_name.replace('_', ' ')}")
            elif factor.score < 0.6:
                disadvantages.append(f"Limited {factor.factor_name.replace('_', ' ')}")

        # Add constraint-based disadvantages
        if compat_matrix.constraints:
            disadvantages.extend(compat_matrix.constraints[:2])

        return advantages, disadvantages

    async def _get_implementation_considerations(self, equipment: Equipment) -> List[str]:
        """Get implementation considerations."""
        considerations = []

        equipment_type = self._determine_equipment_type(equipment)
        specs = self.db.get_equipment_specs(equipment_type)

        if specs:
            if specs.get("gps_compatible"):
                considerations.append("GPS integration available for precision application")

            automation = specs.get("automation_level", "manual")
            if automation == "automatic":
                considerations.append("Requires initial setup and calibration")

        considerations.append("Schedule operator training before first use")
        considerations.append("Ensure proper storage and maintenance facilities")

        return considerations

    async def _get_training_requirements(self, equipment: Equipment) -> List[str]:
        """Get training requirements."""
        training = []

        equipment_type = self._determine_equipment_type(equipment)
        specs = self.db.get_equipment_specs(equipment_type)

        if specs:
            automation = specs.get("automation_level", "manual")
            if automation == "automatic":
                training.append("Advanced operator training (2-3 days)")
                training.append("GPS and automation system training")
            elif automation == "semi-automatic":
                training.append("Intermediate operator training (1-2 days)")
            else:
                training.append("Basic operator training (1 day)")

        training.append("Safety procedures and emergency protocols")
        training.append("Maintenance and calibration procedures")

        return training

    async def _get_maintenance_impact(self, equipment: Equipment) -> str:
        """Get maintenance impact assessment."""
        if equipment.maintenance_level.value == "basic":
            return "Low maintenance impact - basic routine maintenance required"
        elif equipment.maintenance_level.value == "intermediate":
            return "Moderate maintenance impact - regular servicing needed"
        elif equipment.maintenance_level.value == "advanced":
            return "Higher maintenance impact - specialized maintenance required"
        else:
            return "Significant maintenance impact - professional servicing needed"

    async def _analyze_field_requirements(
        self, fields: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze requirements across all fields."""
        total_acres = sum(f.get("size_acres", 0) for f in fields)
        fertilizer_types = set()
        application_methods = set()
        soil_types = set()

        for field in fields:
            if "fertilizer_type" in field:
                fertilizer_types.add(field["fertilizer_type"])
            if "application_method" in field:
                application_methods.add(field["application_method"])
            if "soil_type" in field:
                soil_types.add(field["soil_type"])

        return {
            "total_acres": total_acres,
            "field_count": len(fields),
            "fertilizer_types": list(fertilizer_types),
            "application_methods": list(application_methods),
            "soil_types": list(soil_types),
            "average_field_size": total_acres / len(fields) if fields else 0
        }

    async def _determine_equipment_needs(
        self, field_requirements: Dict[str, Any],
        existing_equipment: Optional[List[Equipment]]
    ) -> List[Dict[str, Any]]:
        """Determine equipment needs based on field requirements."""
        needs = []

        for fert_type in field_requirements["fertilizer_types"]:
            for app_method in field_requirements["application_methods"]:
                need = {
                    "fertilizer_type": fert_type,
                    "application_method": app_method,
                    "total_acres": field_requirements["total_acres"],
                    "soil_type": field_requirements["soil_types"][0] if field_requirements["soil_types"] else "loam"
                }
                needs.append(need)

        return needs

    async def _optimize_selection(
        self, all_recommendations: List[EquipmentRecommendation],
        field_requirements: Dict[str, Any], budget_constraint: Optional[float]
    ) -> List[EquipmentRecommendation]:
        """Optimize equipment selection based on constraints."""
        # Sort by overall score
        sorted_recommendations = sorted(
            all_recommendations, key=lambda x: x.overall_score, reverse=True
        )

        # If no budget constraint, return top recommendations
        if not budget_constraint:
            return sorted_recommendations[:5]

        # Select equipment within budget
        selected = []
        total_cost = 0.0

        for rec in sorted_recommendations:
            if total_cost + rec.cost_benefit.initial_investment <= budget_constraint:
                selected.append(rec)
                total_cost += rec.cost_benefit.initial_investment

        return selected

    async def _generate_implementation_plan(
        self, selected_equipment: List[EquipmentRecommendation],
        fields: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate implementation plan."""
        return {
            "phase_1_immediate": [rec.equipment.name for rec in selected_equipment[:2]],
            "phase_2_short_term": [rec.equipment.name for rec in selected_equipment[2:4]],
            "phase_3_long_term": [rec.equipment.name for rec in selected_equipment[4:]],
            "estimated_timeline_months": len(selected_equipment) * 2,
            "training_schedule": "2 weeks before equipment delivery",
            "maintenance_setup": "1 week after delivery"
        }

    def _calculate_budget_utilization(
        self, selected_equipment: List[EquipmentRecommendation],
        budget_constraint: Optional[float]
    ) -> float:
        """Calculate budget utilization percentage."""
        if not budget_constraint:
            return 0.0

        total_cost = sum(rec.cost_benefit.initial_investment for rec in selected_equipment)
        return (total_cost / budget_constraint) * 100 if budget_constraint > 0 else 0.0
