"""
Drought-Resilient Crop Recommendation Service

Service for recommending drought-tolerant crop varieties and alternative crops
with comprehensive drought resilience analysis and water use efficiency optimization.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, date, timedelta
from uuid import UUID
import statistics
from decimal import Decimal

from .variety_recommendation_service import VarietyRecommendationService
from .confidence_calculation_service import ConfidenceCalculationService

try:
    from ..models.crop_variety_models import (
        EnhancedCropVariety,
        VarietyRecommendation,
        VarietyComparisonRequest,
        VarietyComparisonResponse,
        RegionalPerformanceEntry,
        QualityCharacteristic,
        RiskLevel
    )
    from ..models.crop_taxonomy_models import (
        ComprehensiveCropData,
        CropCategory,
    )
    from ..models.service_models import (
        ConfidenceLevel,
    )
    from ..models.drought_resilient_models import (
        DroughtToleranceProfile,
        WaterUseEfficiencyProfile,
        DroughtResilienceScore,
        DroughtRecommendationRequest,
        DroughtRecommendationResponse,
        AlternativeCropRecommendation,
        DiversificationStrategy,
        DroughtRiskAssessment,
        WaterConservationPotential
    )
except ImportError:
    from models.crop_variety_models import (
        EnhancedCropVariety,
        VarietyRecommendation,
        VarietyComparisonRequest,
        VarietyComparisonResponse,
        RegionalPerformanceEntry,
        QualityCharacteristic,
        RiskLevel
    )
    from models.crop_taxonomy_models import (
        ComprehensiveCropData,
        CropCategory,
    )
    from models.service_models import (
        ConfidenceLevel,
    )
    from models.drought_resilient_models import (
        DroughtToleranceProfile,
        WaterUseEfficiencyProfile,
        DroughtResilienceScore,
        DroughtRecommendationRequest,
        DroughtRecommendationResponse,
        AlternativeCropRecommendation,
        DiversificationStrategy,
        DroughtRiskAssessment,
        WaterConservationPotential
    )

logger = logging.getLogger(__name__)


class DroughtResilientCropService:
    """
    Service for drought-resilient crop variety selection with comprehensive
    drought tolerance analysis, water use efficiency optimization, and
    alternative crop recommendations.
    """

    def __init__(self, database_url: Optional[str] = None):
        """Initialize the drought-resilient crop service."""
        try:
            from ..database.crop_taxonomy_db import CropTaxonomyDatabase
            self.db = CropTaxonomyDatabase(database_url)
            self.database_available = self.db.test_connection()
            logger.info(f"Drought service database connection: {'successful' if self.database_available else 'failed'}")
        except ImportError:
            logger.warning("Database integration not available for drought service")
            self.db = None
            self.database_available = False
        
        # Initialize base variety recommendation service
        self.variety_service = VarietyRecommendationService(database_url)
        
        # Initialize confidence calculation service
        self.confidence_service = ConfidenceCalculationService()
        
        # Initialize drought-specific scoring weights
        self._initialize_drought_scoring_weights()
        
        # Drought tolerance thresholds
        self.drought_tolerance_thresholds = {
            "high": 0.8,      # Excellent drought tolerance
            "moderate": 0.6,   # Good drought tolerance
            "low": 0.4,       # Limited drought tolerance
            "poor": 0.2        # Poor drought tolerance
        }
        
        # Water use efficiency categories
        self.water_efficiency_categories = {
            "very_high": 0.9,   # Very water efficient
            "high": 0.7,        # Water efficient
            "moderate": 0.5,    # Moderate water use
            "low": 0.3,         # High water use
            "very_low": 0.1     # Very high water use
        }

    def _initialize_drought_scoring_weights(self):
        """Initialize drought-specific scoring weights."""
        self.drought_scoring_weights = {
            "drought_tolerance": 0.25,        # Primary drought tolerance
            "water_use_efficiency": 0.20,    # Water efficiency
            "root_depth_adaptation": 0.15,   # Root system adaptation
            "stress_recovery": 0.15,         # Stress recovery ability
            "yield_stability": 0.10,         # Yield stability under stress
            "disease_resistance": 0.08,      # Disease resistance under stress
            "economic_viability": 0.07       # Economic viability in drought
        }

    async def get_drought_resilient_recommendations(
        self,
        request: DroughtRecommendationRequest
    ) -> DroughtRecommendationResponse:
        """
        Get comprehensive drought-resilient crop recommendations.
        
        Args:
            request: Drought recommendation request with location, risk level, and preferences
            
        Returns:
            Comprehensive drought-resilient recommendations with alternatives and strategies
        """
        try:
            logger.info(f"Generating drought-resilient recommendations for location: {request.location}")
            
            # Assess drought risk for the location
            drought_risk = await self._assess_drought_risk(request.location, request.drought_risk_level)
            
            # Get base crop recommendations with drought focus
            base_recommendations = await self._get_base_drought_recommendations(request, drought_risk)
            
            # Get alternative crop recommendations
            alternative_crops = await self._get_alternative_crop_recommendations(request, drought_risk)
            
            # Generate diversification strategies
            diversification_strategies = await self._generate_diversification_strategies(request, drought_risk)
            
            # Calculate water conservation potential
            water_conservation = await self._calculate_water_conservation_potential(
                base_recommendations, alternative_crops, request
            )
            
            # Generate comprehensive response
            response = DroughtRecommendationResponse(
                request_id=request.request_id,
                location=request.location,
                drought_risk_assessment=drought_risk,
                recommended_varieties=base_recommendations,
                alternative_crops=alternative_crops,
                diversification_strategies=diversification_strategies,
                water_conservation_potential=water_conservation,
                confidence_score=self._calculate_overall_confidence(
                    base_recommendations, alternative_crops, drought_risk
                ),
                generated_at=datetime.utcnow()
            )
            
            logger.info(f"Generated {len(base_recommendations)} drought-resilient recommendations")
            return response
            
        except Exception as e:
            logger.error(f"Error generating drought-resilient recommendations: {str(e)}")
            return DroughtRecommendationResponse(
                request_id=request.request_id,
                location=request.location,
                error_message=f"Failed to generate recommendations: {str(e)}",
                generated_at=datetime.utcnow()
            )

    async def _assess_drought_risk(
        self,
        location: Dict[str, Any],
        provided_risk_level: Optional[str] = None
    ) -> DroughtRiskAssessment:
        """Assess drought risk for the given location."""
        
        # If risk level is provided, use it as base
        if provided_risk_level:
            base_risk = provided_risk_level.lower()
        else:
            # Default to moderate risk if not specified
            base_risk = "moderate"
        
        # Calculate risk factors based on location
        risk_factors = await self._calculate_location_risk_factors(location)
        
        # Determine overall risk level
        overall_risk = self._determine_overall_risk_level(base_risk, risk_factors)
        
        return DroughtRiskAssessment(
            location=location,
            overall_risk_level=overall_risk,
            risk_factors=risk_factors,
            confidence_score=0.8,  # Base confidence
            assessment_date=datetime.utcnow()
        )

    async def _calculate_location_risk_factors(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate drought risk factors based on location data."""
        risk_factors = {
            "historical_drought_frequency": 0.5,  # Default moderate
            "soil_water_holding_capacity": 0.5,   # Default moderate
            "irrigation_availability": 0.3,       # Default limited
            "climate_zone_drought_tendency": 0.5,  # Default moderate
            "elevation_water_stress": 0.4,        # Default moderate-high
            "seasonal_precipitation_pattern": 0.5  # Default moderate
        }
        
        # Adjust based on location data if available
        if "climate_zone" in location:
            climate_zone = location["climate_zone"]
            if "arid" in climate_zone.lower() or "desert" in climate_zone.lower():
                risk_factors["climate_zone_drought_tendency"] = 0.8
            elif "semi-arid" in climate_zone.lower():
                risk_factors["climate_zone_drought_tendency"] = 0.7
            elif "humid" in climate_zone.lower():
                risk_factors["climate_zone_drought_tendency"] = 0.3
        
        if "irrigation_available" in location:
            risk_factors["irrigation_availability"] = 0.8 if location["irrigation_available"] else 0.2
        
        if "soil_type" in location:
            soil_type = location["soil_type"].lower()
            if "sand" in soil_type:
                risk_factors["soil_water_holding_capacity"] = 0.2  # Poor water holding
            elif "clay" in soil_type:
                risk_factors["soil_water_holding_capacity"] = 0.8  # Good water holding
            elif "loam" in soil_type:
                risk_factors["soil_water_holding_capacity"] = 0.7  # Good water holding
        
        return risk_factors

    def _determine_overall_risk_level(self, base_risk: str, risk_factors: Dict[str, Any]) -> str:
        """Determine overall drought risk level based on factors."""
        # Calculate weighted average of risk factors
        risk_values = list(risk_factors.values())
        avg_risk = statistics.mean(risk_values)
        
        # Adjust base risk based on calculated factors
        if avg_risk >= 0.7:
            return "high"
        elif avg_risk >= 0.5:
            return "moderate"
        elif avg_risk >= 0.3:
            return "low"
        else:
            return "very_low"

    async def _get_base_drought_recommendations(
        self,
        request: DroughtRecommendationRequest,
        drought_risk: DroughtRiskAssessment
    ) -> List[VarietyRecommendation]:
        """Get base crop variety recommendations with drought focus."""
        
        # Create crop data for the request
        crop_data = await self._create_crop_data_from_request(request)
        
        # Create regional context with drought focus
        regional_context = await self._create_drought_focused_context(request, drought_risk)
        
        # Get base recommendations from variety service
        base_recommendations = await self.variety_service.recommend_varieties(
            crop_data, regional_context, request.farmer_preferences
        )
        
        # Enhance recommendations with drought-specific scoring
        drought_enhanced_recommendations = []
        for recommendation in base_recommendations:
            enhanced_recommendation = await self._enhance_with_drought_scoring(
                recommendation, drought_risk, request
            )
            drought_enhanced_recommendations.append(enhanced_recommendation)
        
        # Sort by drought resilience score
        drought_enhanced_recommendations.sort(
            key=lambda x: x.suitability_factors.get("drought_resilience_score", 0),
            reverse=True
        )
        
        return drought_enhanced_recommendations

    async def _create_crop_data_from_request(self, request: DroughtRecommendationRequest) -> ComprehensiveCropData:
        """Create crop data from recommendation request."""
        # This would typically query the database for crop information
        # For now, create a basic crop data structure
        return ComprehensiveCropData(
            id=UUID('12345678-1234-5678-9abc-123456789012'),
            name=request.crop_type or "corn",
            scientific_name="Zea mays",
            agricultural_classification={
                "primary_category": CropCategory.GRAIN,
                "secondary_categories": [CropCategory.CEREAL]
            }
        )

    async def _create_drought_focused_context(
        self,
        request: DroughtRecommendationRequest,
        drought_risk: DroughtRiskAssessment
    ) -> Dict[str, Any]:
        """Create regional context focused on drought conditions."""
        context = {
            "location": request.location,
            "drought_risk_level": drought_risk.overall_risk_level,
            "climate_risks": {
                "drought_risk": self._risk_level_to_numeric(drought_risk.overall_risk_level),
                "heat_risk": 0.6,  # Default moderate heat risk
                "water_stress": 0.7  # Default high water stress
            },
            "soil_conditions": {
                "water_holding_capacity": drought_risk.risk_factors.get("soil_water_holding_capacity", 0.5),
                "irrigation_available": drought_risk.risk_factors.get("irrigation_availability", 0.3) > 0.5
            },
            "management_constraints": {
                "water_limitations": True,
                "drought_tolerance_priority": True,
                "water_efficiency_priority": True
            },
            "drought_focus": True
        }
        
        return context

    def _risk_level_to_numeric(self, risk_level: str) -> float:
        """Convert risk level string to numeric value."""
        risk_mapping = {
            "very_low": 0.1,
            "low": 0.3,
            "moderate": 0.5,
            "high": 0.7,
            "severe": 0.9
        }
        return risk_mapping.get(risk_level.lower(), 0.5)

    async def _enhance_with_drought_scoring(
        self,
        recommendation: VarietyRecommendation,
        drought_risk: DroughtRiskAssessment,
        request: DroughtRecommendationRequest
    ) -> VarietyRecommendation:
        """Enhance variety recommendation with drought-specific scoring."""
        
        variety = recommendation.variety
        if not variety:
            return recommendation
        
        # Calculate drought resilience score
        drought_resilience_score = await self._calculate_drought_resilience_score(
            variety, drought_risk, request
        )
        
        # Calculate water use efficiency score
        water_efficiency_score = await self._calculate_water_efficiency_score(
            variety, drought_risk, request
        )
        
        # Calculate stress recovery score
        stress_recovery_score = await self._calculate_stress_recovery_score(
            variety, drought_risk, request
        )
        
        # Update suitability factors with drought-specific scores
        recommendation.suitability_factors.update({
            "drought_resilience_score": drought_resilience_score,
            "water_efficiency_score": water_efficiency_score,
            "stress_recovery_score": stress_recovery_score,
            "drought_tolerance_level": self._determine_drought_tolerance_level(drought_resilience_score)
        })
        
        # Update individual scores
        recommendation.individual_scores.update({
            "drought_tolerance": drought_resilience_score,
            "water_use_efficiency": water_efficiency_score,
            "stress_recovery": stress_recovery_score
        })
        
        # Add drought-specific recommendations
        drought_practices = await self._generate_drought_management_practices(
            variety, drought_risk, request
        )
        recommendation.recommended_practices.extend(drought_practices)
        
        # Update economic analysis with drought considerations
        drought_economics = await self._calculate_drought_economics(
            variety, drought_risk, request
        )
        recommendation.economic_analysis.update(drought_economics)
        
        return recommendation

    async def _calculate_drought_resilience_score(
        self,
        variety: EnhancedCropVariety,
        drought_risk: DroughtRiskAssessment,
        request: DroughtRecommendationRequest
    ) -> float:
        """Calculate comprehensive drought resilience score."""
        
        base_score = 0.5  # Default moderate score
        
        # Factor 1: Stress tolerances from variety data
        if variety.stress_tolerances:
            drought_tolerance_keywords = ["drought", "water", "stress", "arid"]
            drought_traits = [trait for trait in variety.stress_tolerances 
                            if any(keyword in trait.lower() for keyword in drought_tolerance_keywords)]
            if drought_traits:
                base_score += 0.2 * len(drought_traits) / len(variety.stress_tolerances)
        
        # Factor 2: Yield stability under stress
        if variety.yield_stability_rating:
            stability_bonus = (variety.yield_stability_rating - 5.0) * 0.05
            base_score += stability_bonus
        
        # Factor 3: Disease resistance under stress conditions
        if variety.disease_resistances:
            disease_score = len(variety.disease_resistances) * 0.05
            base_score += min(disease_score, 0.15)
        
        # Factor 4: Regional adaptation
        if variety.adapted_regions:
            # Check if variety is adapted to drought-prone regions
            drought_regions = ["southwest", "great plains", "california", "texas", "arizona"]
            adapted_drought_regions = [region for region in variety.adapted_regions 
                                    if any(drought_region in region.lower() for drought_region in drought_regions)]
            if adapted_drought_regions:
                base_score += 0.1
        
        # Factor 5: Risk level adjustment
        risk_adjustment = self._risk_level_to_numeric(drought_risk.overall_risk_level) * 0.2
        base_score += risk_adjustment
        
        return max(0.0, min(1.0, base_score))

    async def _calculate_water_efficiency_score(
        self,
        variety: EnhancedCropVariety,
        drought_risk: DroughtRiskAssessment,
        request: DroughtRecommendationRequest
    ) -> float:
        """Calculate water use efficiency score."""
        
        base_score = 0.5  # Default moderate efficiency
        
        # Factor 1: Maturity timing affects water use
        if variety.relative_maturity:
            # Earlier maturing varieties typically use less water
            if variety.relative_maturity < 100:  # Early maturity
                base_score += 0.2
            elif variety.relative_maturity > 120:  # Late maturity
                base_score -= 0.1
        
        # Factor 2: Yield potential vs water use
        if variety.yield_potential_percentile:
            # Higher yield potential with same water use = better efficiency
            efficiency_bonus = (variety.yield_potential_percentile - 50) * 0.002
            base_score += efficiency_bonus
        
        # Factor 3: Stress tolerance indicates water efficiency
        if variety.stress_tolerances:
            water_efficiency_traits = ["drought", "water", "efficient", "conservation"]
            efficient_traits = [trait for trait in variety.stress_tolerances 
                              if any(keyword in trait.lower() for keyword in water_efficiency_traits)]
            if efficient_traits:
                base_score += 0.15
        
        # Factor 4: Regional performance in water-limited conditions
        if variety.regional_performance_data:
            # Look for performance data in drought-prone regions
            drought_performance = [perf for perf in variety.regional_performance_data 
                                 if perf.performance_index and perf.performance_index > 0.7]
            if drought_performance:
                base_score += 0.1
        
        return max(0.0, min(1.0, base_score))

    async def _calculate_stress_recovery_score(
        self,
        variety: EnhancedCropVariety,
        drought_risk: DroughtRiskAssessment,
        request: DroughtRecommendationRequest
    ) -> float:
        """Calculate stress recovery ability score."""
        
        base_score = 0.5  # Default moderate recovery
        
        # Factor 1: Yield stability indicates recovery ability
        if variety.yield_stability_rating:
            stability_factor = variety.yield_stability_rating / 10.0
            base_score += stability_factor * 0.3
        
        # Factor 2: Disease resistance helps recovery
        if variety.disease_resistances:
            disease_count = len(variety.disease_resistances)
            disease_bonus = min(disease_count * 0.05, 0.2)
            base_score += disease_bonus
        
        # Factor 3: Stress tolerance traits
        if variety.stress_tolerances:
            recovery_traits = ["recovery", "resilience", "tolerance", "adaptation"]
            recovery_count = sum(1 for trait in variety.stress_tolerances 
                              if any(keyword in trait.lower() for keyword in recovery_traits))
            if recovery_count > 0:
                base_score += 0.15
        
        # Factor 4: Regional performance under stress
        if variety.regional_performance_data:
            # Look for consistent performance across regions
            performance_scores = [perf.performance_index for perf in variety.regional_performance_data 
                               if perf.performance_index is not None]
            if performance_scores:
                avg_performance = statistics.mean(performance_scores)
                consistency_bonus = (avg_performance - 0.5) * 0.2
                base_score += consistency_bonus
        
        return max(0.0, min(1.0, base_score))

    def _determine_drought_tolerance_level(self, drought_resilience_score: float) -> str:
        """Determine drought tolerance level from score."""
        if drought_resilience_score >= self.drought_tolerance_thresholds["high"]:
            return "high"
        elif drought_resilience_score >= self.drought_tolerance_thresholds["moderate"]:
            return "moderate"
        elif drought_resilience_score >= self.drought_tolerance_thresholds["low"]:
            return "low"
        else:
            return "poor"

    async def _generate_drought_management_practices(
        self,
        variety: EnhancedCropVariety,
        drought_risk: DroughtRiskAssessment,
        request: DroughtRecommendationRequest
    ) -> List[str]:
        """Generate drought-specific management practices."""
        
        practices = []
        
        # General drought management practices
        practices.extend([
            "Implement conservation tillage to reduce soil moisture loss",
            "Use mulch or residue to conserve soil moisture",
            "Monitor soil moisture levels regularly",
            "Consider deficit irrigation strategies"
        ])
        
        # Variety-specific practices
        if variety.relative_maturity and variety.relative_maturity < 100:
            practices.append("Early maturity allows for earlier planting and harvest")
        
        if variety.stress_tolerances:
            drought_traits = [trait for trait in variety.stress_tolerances 
                            if "drought" in trait.lower()]
            if drought_traits:
                practices.append("Variety has drought tolerance traits - reduce irrigation frequency")
        
        # Risk-specific practices
        if drought_risk.overall_risk_level in ["high", "severe"]:
            practices.extend([
                "Consider drought insurance options",
                "Implement water-saving irrigation technologies",
                "Plan for alternative water sources"
            ])
        
        return practices

    async def _calculate_drought_economics(
        self,
        variety: EnhancedCropVariety,
        drought_risk: DroughtRiskAssessment,
        request: DroughtRecommendationRequest
    ) -> Dict[str, Any]:
        """Calculate economic considerations for drought conditions."""
        
        economics = {
            "drought_premium": 0.0,
            "water_cost_savings": 0.0,
            "risk_adjustment": 0.0,
            "insurance_considerations": []
        }
        
        # Calculate drought premium (additional cost for drought-tolerant varieties)
        drought_resilience_score = await self._calculate_drought_resilience_score(
            variety, drought_risk, request
        )
        economics["drought_premium"] = drought_resilience_score * 0.1  # Up to 10% premium
        
        # Calculate water cost savings
        water_efficiency_score = await self._calculate_water_efficiency_score(
            variety, drought_risk, request
        )
        economics["water_cost_savings"] = water_efficiency_score * 50  # Up to $50/acre savings
        
        # Risk adjustment for drought conditions
        risk_level = drought_risk.overall_risk_level
        if risk_level in ["high", "severe"]:
            economics["risk_adjustment"] = -0.15  # 15% risk discount
        elif risk_level == "moderate":
            economics["risk_adjustment"] = -0.05  # 5% risk discount
        
        # Insurance considerations
        if risk_level in ["high", "severe"]:
            economics["insurance_considerations"].extend([
                "Consider drought insurance coverage",
                "Evaluate crop insurance options",
                "Assess revenue protection programs"
            ])
        
        return economics

    async def _get_alternative_crop_recommendations(
        self,
        request: DroughtRecommendationRequest,
        drought_risk: DroughtRiskAssessment
    ) -> List[AlternativeCropRecommendation]:
        """Get alternative crop recommendations for drought conditions."""
        
        alternative_crops = []
        
        # Define drought-tolerant alternative crops
        drought_tolerant_crops = [
            {
                "crop_name": "Sorghum",
                "scientific_name": "Sorghum bicolor",
                "drought_tolerance": "high",
                "water_use_efficiency": "very_high",
                "yield_potential": "moderate",
                "market_demand": "moderate",
                "management_complexity": "low"
            },
            {
                "crop_name": "Millet",
                "scientific_name": "Pennisetum glaucum",
                "drought_tolerance": "very_high",
                "water_use_efficiency": "very_high",
                "yield_potential": "moderate",
                "market_demand": "low",
                "management_complexity": "low"
            },
            {
                "crop_name": "Sunflower",
                "scientific_name": "Helianthus annuus",
                "drought_tolerance": "high",
                "water_use_efficiency": "high",
                "yield_potential": "moderate",
                "market_demand": "moderate",
                "management_complexity": "moderate"
            },
            {
                "crop_name": "Cotton",
                "scientific_name": "Gossypium hirsutum",
                "drought_tolerance": "moderate",
                "water_use_efficiency": "moderate",
                "yield_potential": "moderate",
                "market_demand": "high",
                "management_complexity": "high"
            }
        ]
        
        # Generate recommendations for each alternative crop
        for crop_data in drought_tolerant_crops:
            recommendation = AlternativeCropRecommendation(
                crop_name=crop_data["crop_name"],
                scientific_name=crop_data["scientific_name"],
                drought_tolerance_level=crop_data["drought_tolerance"],
                water_use_efficiency=crop_data["water_use_efficiency"],
                yield_potential=crop_data["yield_potential"],
                market_demand=crop_data["market_demand"],
                management_complexity=crop_data["management_complexity"],
                suitability_score=self._calculate_alternative_crop_suitability(
                    crop_data, drought_risk, request
                ),
                advantages=self._get_alternative_crop_advantages(crop_data),
                considerations=self._get_alternative_crop_considerations(crop_data),
                transition_requirements=self._get_transition_requirements(crop_data)
            )
            alternative_crops.append(recommendation)
        
        # Sort by suitability score
        alternative_crops.sort(key=lambda x: x.suitability_score, reverse=True)
        
        return alternative_crops

    def _calculate_alternative_crop_suitability(
        self,
        crop_data: Dict[str, str],
        drought_risk: DroughtRiskAssessment,
        request: DroughtRecommendationRequest
    ) -> float:
        """Calculate suitability score for alternative crop."""
        
        base_score = 0.5
        
        # Factor 1: Drought tolerance
        tolerance_mapping = {"very_high": 0.9, "high": 0.7, "moderate": 0.5, "low": 0.3}
        tolerance_score = tolerance_mapping.get(crop_data["drought_tolerance"], 0.5)
        base_score += tolerance_score * 0.3
        
        # Factor 2: Water use efficiency
        efficiency_mapping = {"very_high": 0.9, "high": 0.7, "moderate": 0.5, "low": 0.3}
        efficiency_score = efficiency_mapping.get(crop_data["water_use_efficiency"], 0.5)
        base_score += efficiency_score * 0.25
        
        # Factor 3: Market demand
        demand_mapping = {"high": 0.8, "moderate": 0.6, "low": 0.4}
        demand_score = demand_mapping.get(crop_data["market_demand"], 0.5)
        base_score += demand_score * 0.2
        
        # Factor 4: Management complexity
        complexity_mapping = {"low": 0.8, "moderate": 0.6, "high": 0.4}
        complexity_score = complexity_mapping.get(crop_data["management_complexity"], 0.5)
        base_score += complexity_score * 0.15
        
        # Factor 5: Risk level adjustment
        risk_adjustment = self._risk_level_to_numeric(drought_risk.overall_risk_level) * 0.1
        base_score += risk_adjustment
        
        return max(0.0, min(1.0, base_score))

    def _get_alternative_crop_advantages(self, crop_data: Dict[str, str]) -> List[str]:
        """Get advantages for alternative crop."""
        advantages = []
        
        if crop_data["drought_tolerance"] in ["high", "very_high"]:
            advantages.append("Excellent drought tolerance")
        
        if crop_data["water_use_efficiency"] in ["high", "very_high"]:
            advantages.append("High water use efficiency")
        
        if crop_data["management_complexity"] == "low":
            advantages.append("Low management complexity")
        
        if crop_data["market_demand"] == "high":
            advantages.append("Strong market demand")
        
        return advantages

    def _get_alternative_crop_considerations(self, crop_data: Dict[str, str]) -> List[str]:
        """Get considerations for alternative crop."""
        considerations = []
        
        if crop_data["yield_potential"] == "low":
            considerations.append("Lower yield potential compared to traditional crops")
        
        if crop_data["market_demand"] == "low":
            considerations.append("Limited market outlets")
        
        if crop_data["management_complexity"] == "high":
            considerations.append("Requires specialized management")
        
        return considerations

    def _get_transition_requirements(self, crop_data: Dict[str, str]) -> List[str]:
        """Get transition requirements for alternative crop."""
        requirements = []
        
        requirements.extend([
            "Evaluate equipment compatibility",
            "Assess market access and contracts",
            "Plan crop rotation integration",
            "Consider seed availability and cost"
        ])
        
        if crop_data["management_complexity"] == "high":
            requirements.append("Develop specialized management expertise")
        
        return requirements

    async def _generate_diversification_strategies(
        self,
        request: DroughtRecommendationRequest,
        drought_risk: DroughtRiskAssessment
    ) -> List[DiversificationStrategy]:
        """Generate diversification strategies for drought risk management."""
        
        strategies = []
        
        # Strategy 1: Crop rotation diversification
        strategies.append(DiversificationStrategy(
            strategy_type="crop_rotation",
            description="Implement diverse crop rotation to spread drought risk",
            implementation_steps=[
                "Include drought-tolerant crops in rotation",
                "Vary planting dates to spread risk",
                "Use different root depths to access soil moisture"
            ],
            expected_benefits=[
                "Reduced overall drought risk",
                "Improved soil health",
                "Better water use efficiency"
            ],
            risk_reduction_potential=0.3,
            implementation_difficulty="moderate"
        ))
        
        # Strategy 2: Variety diversification
        strategies.append(DiversificationStrategy(
            strategy_type="variety_diversification",
            description="Plant multiple varieties with different drought tolerances",
            implementation_steps=[
                "Select varieties with different maturity dates",
                "Include both drought-tolerant and high-yield varieties",
                "Distribute varieties across fields based on soil conditions"
            ],
            expected_benefits=[
                "Reduced yield variability",
                "Better adaptation to varying conditions",
                "Maintained overall farm productivity"
            ],
            risk_reduction_potential=0.2,
            implementation_difficulty="low"
        ))
        
        # Strategy 3: Water source diversification
        if drought_risk.risk_factors.get("irrigation_availability", 0.3) < 0.5:
            strategies.append(DiversificationStrategy(
                strategy_type="water_source_diversification",
                description="Develop multiple water sources for irrigation",
                implementation_steps=[
                    "Evaluate groundwater potential",
                    "Consider rainwater harvesting",
                    "Explore water storage options"
                ],
                expected_benefits=[
                    "Reduced water supply risk",
                    "Improved irrigation reliability",
                    "Better drought preparedness"
                ],
                risk_reduction_potential=0.4,
                implementation_difficulty="high"
            ))
        
        return strategies

    async def _calculate_water_conservation_potential(
        self,
        recommendations: List[VarietyRecommendation],
        alternative_crops: List[AlternativeCropRecommendation],
        request: DroughtRecommendationRequest
    ) -> WaterConservationPotential:
        """Calculate water conservation potential from recommendations."""
        
        # Calculate potential water savings from recommended varieties
        variety_savings = 0.0
        if recommendations:
            avg_efficiency = statistics.mean([
                rec.suitability_factors.get("water_efficiency_score", 0.5)
                for rec in recommendations
            ])
            variety_savings = avg_efficiency * 100  # Up to 100 gallons per acre
        
        # Calculate potential water savings from alternative crops
        alternative_savings = 0.0
        if alternative_crops:
            avg_alternative_efficiency = statistics.mean([
                self._efficiency_to_numeric(crop.water_use_efficiency)
                for crop in alternative_crops
            ])
            alternative_savings = avg_alternative_efficiency * 150  # Up to 150 gallons per acre
        
        # Calculate total potential savings
        total_savings = variety_savings + alternative_savings
        
        return WaterConservationPotential(
            variety_based_savings=variety_savings,
            alternative_crop_savings=alternative_savings,
            total_potential_savings=total_savings,
            savings_percentage=self._calculate_savings_percentage(total_savings),
            implementation_timeline="1-3 years",
            cost_benefit_ratio=self._calculate_cost_benefit_ratio(total_savings)
        )

    def _efficiency_to_numeric(self, efficiency: str) -> float:
        """Convert efficiency string to numeric value."""
        efficiency_mapping = {
            "very_high": 0.9,
            "high": 0.7,
            "moderate": 0.5,
            "low": 0.3,
            "very_low": 0.1
        }
        return efficiency_mapping.get(efficiency, 0.5)

    def _calculate_savings_percentage(self, total_savings: float) -> float:
        """Calculate percentage of water savings."""
        # Assume baseline water use of 500 gallons per acre
        baseline_use = 500.0
        return min((total_savings / baseline_use) * 100, 50.0)  # Cap at 50%

    def _calculate_cost_benefit_ratio(self, total_savings: float) -> float:
        """Calculate cost-benefit ratio for water conservation."""
        # Assume water cost of $0.50 per gallon
        water_cost = 0.50
        annual_savings = total_savings * water_cost
        
        # Assume implementation cost of $100 per acre
        implementation_cost = 100.0
        
        if implementation_cost > 0:
            return annual_savings / implementation_cost
        return 0.0

    def _calculate_overall_confidence(
        self,
        recommendations: List[VarietyRecommendation],
        alternative_crops: List[AlternativeCropRecommendation],
        drought_risk: DroughtRiskAssessment
    ) -> float:
        """Calculate overall confidence score for recommendations."""
        
        # Base confidence from drought risk assessment
        base_confidence = drought_risk.confidence_score
        
        # Adjust based on number of recommendations
        if len(recommendations) >= 3:
            base_confidence += 0.1
        elif len(recommendations) >= 1:
            base_confidence += 0.05
        
        # Adjust based on alternative crop options
        if len(alternative_crops) >= 2:
            base_confidence += 0.05
        
        return max(0.0, min(1.0, base_confidence))


# Create service instance
import os
drought_resilient_crop_service = DroughtResilientCropService(
    database_url=os.getenv('DATABASE_URL')
)