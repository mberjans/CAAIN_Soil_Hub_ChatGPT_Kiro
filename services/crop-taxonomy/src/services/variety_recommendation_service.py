"""
Variety Recommendation Service

Service for crop variety selection, comparison, and regional adaptation
recommendations with performance prediction and risk assessment.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, date, timedelta
from uuid import UUID
import statistics

try:
    from ..models.crop_variety_models import (
        EnhancedCropVariety,
        CropRegionalAdaptation,
        VarietyRecommendation,
        VarietyComparisonRequest,
        VarietyComparisonResponse,
        RegionalAdaptationRequest,
        RegionalAdaptationResponse,
        PerformancePrediction,
        RiskAssessment,
        AdaptationStrategy,
        VarietyCharacteristics,
        DiseaseResistanceProfile,
        PestResistanceProfile,
        AbioticStressTolerances,
        RegionalPerformanceData,
        SeasonalTiming,
        YieldPotential,
        QualityAttributes,
        MarketAttributes,
        RiskLevel,
        AdaptationLevel
    )
    from ..models.crop_taxonomy_models import (
        ComprehensiveCropData,
        CropCategory,
        LifeCycle,
        ClimateZone
    )
    from ..models.service_models import (
        ConfidenceLevel,
        ValidationResult
    )
except ImportError:
    from models.crop_variety_models import (
        EnhancedCropVariety,
        CropRegionalAdaptation,
        VarietyRecommendation,
        VarietyComparisonRequest,
        VarietyComparisonResponse,
        RegionalAdaptationRequest,
        RegionalAdaptationResponse,
        PerformancePrediction,
        RiskAssessment,
        AdaptationStrategy,
        VarietyCharacteristics,
        DiseaseResistanceProfile,
        PestResistanceProfile,
        AbioticStressTolerances,
        RegionalPerformanceData,
        SeasonalTiming,
        YieldPotential,
        QualityAttributes,
        MarketAttributes,
        RiskLevel,
        AdaptationLevel
    )
    from models.crop_taxonomy_models import (
        ComprehensiveCropData,
        CropCategory,
        LifeCycle,
        ClimateZone
    )
    from models.service_models import (
        ConfidenceLevel,
        ValidationResult
    )


logger = logging.getLogger(__name__)


class VarietyRecommendationService:
    """
    Service for intelligent crop variety selection with regional adaptation analysis,
    performance prediction, and comparative evaluation.
    """

    def __init__(self, database_url: Optional[str] = None):
        """Initialize the variety recommendation service with database integration."""
        try:
            from ..database.crop_taxonomy_db import CropTaxonomyDatabase
            self.db = CropTaxonomyDatabase(database_url)
            self.database_available = self.db.test_connection()
            logger.info(f"Variety service database connection: {'successful' if self.database_available else 'failed'}")
        except ImportError:
            logger.warning("Database integration not available for variety service")
            self.db = None
            self.database_available = False
        
        # Initialize seed company integration
        try:
            from .seed_company_service import SeedCompanyIntegrationService
            self.seed_company_service = SeedCompanyIntegrationService(database_url)
            logger.info("Seed company integration service initialized")
        except ImportError:
            logger.warning("Seed company integration not available")
            self.seed_company_service = None
            
        self.regional_data = {}
        self.performance_models = {}
        self._initialize_recommendation_algorithms()

    def _initialize_recommendation_algorithms(self):
        """Initialize variety recommendation algorithms and scoring systems."""
        # Scoring weights for variety selection
        self.scoring_weights = {
            "yield_potential": 0.25,
            "disease_resistance": 0.20,
            "climate_adaptation": 0.18,
            "market_desirability": 0.12,
            "management_ease": 0.10,
            "quality_attributes": 0.08,
            "risk_tolerance": 0.07
        }
        
        # Regional adaptation factors
        self.adaptation_factors = {
            "temperature_tolerance": 0.30,
            "precipitation_adaptation": 0.25,
            "soil_compatibility": 0.20,
            "pest_pressure": 0.15,
            "market_access": 0.10
        }

    async def recommend_varieties(
        self, 
        crop_data: ComprehensiveCropData,
        regional_context: Dict[str, Any],
        farmer_preferences: Optional[Dict[str, Any]] = None
    ) -> List[VarietyRecommendation]:
        """
        Generate variety recommendations for a specific crop and region.
        
        Args:
            crop_data: Base crop information
            regional_context: Regional growing conditions and constraints
            farmer_preferences: Optional farmer-specific preferences and priorities
            
        Returns:
            Ranked list of variety recommendations with scoring and rationale
        """
        try:
            # Get available varieties for the crop
            available_varieties = await self._get_available_varieties(crop_data)
            
            if not available_varieties:
                logger.warning(f"No varieties found for crop: {crop_data.id}")
                return []

            # Score each variety for the specific context
            scored_varieties = []
            for variety in available_varieties:
                score_data = await self._score_variety_for_context(
                    variety, regional_context, farmer_preferences
                )
                
                if score_data:
                    recommendation = await self._create_variety_recommendation(
                        variety, score_data, regional_context
                    )
                    scored_varieties.append(recommendation)

            # Sort by overall recommendation score
            scored_varieties.sort(key=lambda x: x.overall_score, reverse=True)
            
            # Apply diversity filtering to ensure variety in recommendations
            final_recommendations = await self._apply_diversity_filtering(scored_varieties)
            
            return final_recommendations

        except Exception as e:
            logger.error(f"Error in variety recommendations: {str(e)}")
            return []

    async def get_variety_availability_info(self, variety_name: str) -> Dict[str, Any]:
        """
        Get comprehensive availability information for a variety from seed companies.
        
        Args:
            variety_name: Name of the variety
            
        Returns:
            Dictionary with availability information from all seed companies
        """
        if not self.seed_company_service:
            logger.warning("Seed company service not available")
            return {"error": "Seed company integration not available"}
        
        try:
            availability = await self.seed_company_service.get_variety_availability(variety_name)
            
            # Process availability data for recommendation context
            availability_info = {
                "variety_name": variety_name,
                "total_companies": len(availability),
                "companies": [],
                "availability_summary": {
                    "in_stock": 0,
                    "limited": 0,
                    "preorder": 0,
                    "discontinued": 0
                },
                "price_range": {
                    "min": None,
                    "max": None,
                    "average": None
                },
                "regional_coverage": set(),
                "last_updated": None
            }
            
            prices = []
            for offering in availability:
                company_info = {
                    "company_name": offering.company_name,
                    "product_code": offering.product_code,
                    "availability_status": offering.availability_status.value,
                    "price_per_unit": offering.price_per_unit,
                    "price_unit": offering.price_unit,
                    "distribution_regions": offering.distribution_regions,
                    "last_updated": offering.last_updated.isoformat() if offering.last_updated else None,
                    "notes": offering.notes
                }
                availability_info["companies"].append(company_info)
                
                # Update summary statistics
                status = offering.availability_status.value
                if status in availability_info["availability_summary"]:
                    availability_info["availability_summary"][status] += 1
                
                # Collect pricing information
                if offering.price_per_unit:
                    prices.append(offering.price_per_unit)
                
                # Collect regional coverage
                availability_info["regional_coverage"].update(offering.distribution_regions)
                
                # Track most recent update
                if offering.last_updated:
                    if not availability_info["last_updated"] or offering.last_updated > datetime.fromisoformat(availability_info["last_updated"]):
                        availability_info["last_updated"] = offering.last_updated.isoformat()
            
            # Calculate price statistics
            if prices:
                availability_info["price_range"]["min"] = min(prices)
                availability_info["price_range"]["max"] = max(prices)
                availability_info["price_range"]["average"] = sum(prices) / len(prices)
            
            # Convert set to list for JSON serialization
            availability_info["regional_coverage"] = list(availability_info["regional_coverage"])
            
            return availability_info
            
        except Exception as e:
            logger.error(f"Error getting variety availability: {e}")
            return {"error": f"Failed to get availability information: {str(e)}"}
    
    async def sync_seed_company_data(self) -> Dict[str, Any]:
        """
        Synchronize data from seed companies to ensure up-to-date variety information.
        
        Returns:
            Dictionary with sync results and status
        """
        if not self.seed_company_service:
            return {"error": "Seed company integration not available"}
        
        try:
            sync_results = await self.seed_company_service.sync_all_companies()
            
            return {
                "sync_completed": True,
                "results": sync_results,
                "timestamp": datetime.now().isoformat(),
                "message": "Seed company data synchronization completed"
            }
            
        except Exception as e:
            logger.error(f"Error syncing seed company data: {e}")
            return {"error": f"Sync failed: {str(e)}"}
    
    async def get_seed_company_sync_status(self) -> Dict[str, Any]:
        """
        Get synchronization status for all seed companies.
        
        Returns:
            Dictionary with sync status information
        """
        if not self.seed_company_service:
            return {"error": "Seed company integration not available"}
        
        try:
            status_info = await self.seed_company_service.get_company_sync_status()
            return status_info
            
        except Exception as e:
            logger.error(f"Error getting seed company sync status: {e}")
            return {"error": f"Status retrieval failed: {str(e)}"}

    async def _get_available_varieties(self, crop_data: ComprehensiveCropData) -> List[EnhancedCropVariety]:
        """Get available varieties for the specified crop."""
        # This would query the actual variety database
        # For now, return sample varieties based on crop type
        return await self._generate_sample_varieties(crop_data)

    async def _generate_sample_varieties(self, crop_data: ComprehensiveCropData) -> List[EnhancedCropVariety]:
        """Generate sample varieties for testing purposes."""
        if not crop_data.agricultural_classification:
            return []

        sample_varieties = []
        
        # Generate varieties based on crop category
        if crop_data.agricultural_classification.primary_category == CropCategory.GRAIN:
            sample_varieties.extend(await self._create_grain_varieties(crop_data))
        elif crop_data.agricultural_classification.primary_category == CropCategory.OILSEED:
            sample_varieties.extend(await self._create_oilseed_varieties(crop_data))
        elif crop_data.agricultural_classification.primary_category == CropCategory.LEGUME:
            sample_varieties.extend(await self._create_legume_varieties(crop_data))
            
        return sample_varieties

    async def _create_grain_varieties(self, crop_data: ComprehensiveCropData) -> List[EnhancedCropVariety]:
        """Create sample grain crop varieties."""
        varieties = []
        
        # Example wheat varieties
        if "wheat" in (crop_data.taxonomic_hierarchy.common_names or []):
            varieties.extend([
                await self._create_wheat_variety("Hard Red Winter", "HRW-2024", "high_yield"),
                await self._create_wheat_variety("Soft White Winter", "SWW-Elite", "quality_focused"),
                await self._create_wheat_variety("Hard Red Spring", "HRS-Premium", "disease_resistant")
            ])
            
        return varieties

    async def _create_wheat_variety(self, variety_name: str, variety_code: str, focus_type: str) -> EnhancedCropVariety:
        """Create a sample wheat variety with realistic characteristics."""
        
        # Customize characteristics based on focus type
        if focus_type == "high_yield":
            yield_potential = YieldPotential(
                average_yield_range=(4.5, 6.8),
                potential_yield_range=(6.0, 8.5),
                yield_stability_rating=4.2,
                factors_affecting_yield=["irrigation", "fertility", "disease_pressure"]
            )
            disease_resistance = DiseaseResistanceProfile(
                rust_resistance={"stripe_rust": 3, "leaf_rust": 4, "stem_rust": 3},
                other_disease_resistance={"powdery_mildew": 3, "septoria": 2}
            )
        elif focus_type == "quality_focused":
            yield_potential = YieldPotential(
                average_yield_range=(3.8, 5.5),
                potential_yield_range=(4.5, 6.8),
                yield_stability_rating=4.5,
                factors_affecting_yield=["protein_content", "test_weight", "falling_number"]
            )
            disease_resistance = DiseaseResistanceProfile(
                rust_resistance={"stripe_rust": 4, "leaf_rust": 4, "stem_rust": 3},
                other_disease_resistance={"powdery_mildew": 4, "septoria": 3}
            )
        else:  # disease_resistant
            yield_potential = YieldPotential(
                average_yield_range=(4.0, 6.0),
                potential_yield_range=(5.2, 7.2),
                yield_stability_rating=4.7,
                factors_affecting_yield=["weather", "fertility"]
            )
            disease_resistance = DiseaseResistanceProfile(
                rust_resistance={"stripe_rust": 5, "leaf_rust": 5, "stem_rust": 4},
                other_disease_resistance={"powdery_mildew": 5, "septoria": 4}
            )

        return EnhancedCropVariety(
            id=UUID('12345678-1234-5678-9abc-' + variety_code.replace('-', '')[:12].ljust(12, '0')),
            variety_name=variety_name,
            variety_code=variety_code,
            parent_crop_id=crop_data.id,
            release_year=2024,
            breeding_institution="University Research Station",
            characteristics=VarietyCharacteristics(
                maturity_class="medium",
                plant_height_range=(75, 95),
                grain_characteristics={
                    "kernel_color": "red" if "Red" in variety_name else "white",
                    "kernel_hardness": "hard" if "Hard" in variety_name else "soft",
                    "protein_content_range": (11.5, 14.2)
                }
            ),
            yield_potential=yield_potential,
            disease_resistance=disease_resistance,
            pest_resistance=PestResistanceProfile(
                insect_resistance={"aphids": 3, "wheat_midge": 2},
                nematode_resistance={}
            ),
            abiotic_stress_tolerances=AbioticStressTolerances(
                drought_tolerance=4 if focus_type == "high_yield" else 3,
                heat_tolerance=3,
                cold_tolerance=4,
                salt_tolerance=2,
                waterlogging_tolerance=2
            ),
            quality_attributes=QualityAttributes(
                protein_content_range=(11.5, 14.2),
                test_weight_range=(76, 82),
                falling_number_range=(250, 400),
                other_quality_metrics={"gluten_strength": "medium-strong"}
            ),
            market_attributes=MarketAttributes(
                market_class=variety_name,
                end_use_suitability=["bread", "general_purpose"],
                premium_potential=4.0 if focus_type == "quality_focused" else 3.2
            )
        )

    async def _create_oilseed_varieties(self, crop_data: ComprehensiveCropData) -> List[EnhancedCropVariety]:
        """Create sample oilseed crop varieties."""
        # Placeholder implementation
        return []

    async def _create_legume_varieties(self, crop_data: ComprehensiveCropData) -> List[EnhancedCropVariety]:
        """Create sample legume crop varieties."""
        # Placeholder implementation  
        return []

    async def _score_variety_for_context(
        self,
        variety: EnhancedCropVariety,
        regional_context: Dict[str, Any],
        farmer_preferences: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Score a variety for specific regional and farmer context."""
        
        scores = {}
        
        # Yield potential scoring
        scores["yield_potential"] = await self._score_yield_potential(variety, regional_context)
        
        # Disease resistance scoring
        scores["disease_resistance"] = await self._score_disease_resistance(variety, regional_context)
        
        # Climate adaptation scoring
        scores["climate_adaptation"] = await self._score_climate_adaptation(variety, regional_context)
        
        # Market desirability scoring
        scores["market_desirability"] = await self._score_market_desirability(variety, regional_context)
        
        # Management ease scoring
        scores["management_ease"] = await self._score_management_ease(variety, regional_context)
        
        # Quality attributes scoring
        scores["quality_attributes"] = await self._score_quality_attributes(variety, farmer_preferences)
        
        # Risk tolerance scoring
        scores["risk_tolerance"] = await self._score_risk_tolerance(variety, regional_context)
        
        # Calculate weighted overall score
        overall_score = sum(
            scores[factor] * self.scoring_weights[factor] 
            for factor in scores.keys() 
            if factor in self.scoring_weights
        )
        
        return {
            "individual_scores": scores,
            "overall_score": overall_score,
            "score_details": await self._generate_score_explanations(variety, scores)
        }

    async def _score_yield_potential(self, variety: EnhancedCropVariety, context: Dict[str, Any]) -> float:
        """Score variety's yield potential in the given context."""
        if not variety.yield_potential:
            return 0.5  # Neutral score if no data
            
        base_score = 0.7  # Base score
        
        # Adjust based on yield stability
        if variety.yield_potential.yield_stability_rating:
            stability_bonus = (variety.yield_potential.yield_stability_rating - 3.0) * 0.1
            base_score += stability_bonus
            
        # Adjust based on regional yield potential
        if "regional_yield_modifier" in context:
            regional_modifier = context["regional_yield_modifier"]
            base_score *= (1.0 + regional_modifier)
            
        return max(0.0, min(1.0, base_score))

    async def _score_disease_resistance(self, variety: EnhancedCropVariety, context: Dict[str, Any]) -> float:
        """Score disease resistance based on regional disease pressure."""
        if not variety.disease_resistance:
            return 0.3  # Low score if no resistance data
            
        total_score = 0.0
        disease_count = 0
        
        # Score rust resistance
        if variety.disease_resistance.rust_resistance:
            rust_scores = list(variety.disease_resistance.rust_resistance.values())
            avg_rust_score = statistics.mean(rust_scores) / 5.0  # Normalize to 0-1
            total_score += avg_rust_score * 0.6  # Rust diseases are critical
            disease_count += 1
            
        # Score other disease resistance
        if variety.disease_resistance.other_disease_resistance:
            other_scores = list(variety.disease_resistance.other_disease_resistance.values())
            avg_other_score = statistics.mean(other_scores) / 5.0  # Normalize to 0-1
            total_score += avg_other_score * 0.4
            disease_count += 1
            
        return total_score / disease_count if disease_count > 0 else 0.3

    async def _score_climate_adaptation(self, variety: EnhancedCropVariety, context: Dict[str, Any]) -> float:
        """Score climate adaptation for regional conditions."""
        if not variety.abiotic_stress_tolerances:
            return 0.5
            
        total_score = 0.0
        factor_count = 0
        
        # Weight stress tolerances based on regional climate risks
        climate_risks = context.get("climate_risks", {})
        
        if "drought_risk" in climate_risks and variety.abiotic_stress_tolerances.drought_tolerance:
            drought_score = variety.abiotic_stress_tolerances.drought_tolerance / 5.0
            drought_weight = climate_risks["drought_risk"]
            total_score += drought_score * drought_weight
            factor_count += drought_weight
            
        if "heat_risk" in climate_risks and variety.abiotic_stress_tolerances.heat_tolerance:
            heat_score = variety.abiotic_stress_tolerances.heat_tolerance / 5.0
            heat_weight = climate_risks["heat_risk"]
            total_score += heat_score * heat_weight
            factor_count += heat_weight
            
        return total_score / factor_count if factor_count > 0 else 0.5

    async def _score_market_desirability(self, variety: EnhancedCropVariety, context: Dict[str, Any]) -> float:
        """Score market desirability and economic potential."""
        if not variety.market_attributes:
            return 0.5
            
        base_score = 0.6
        
        # Adjust based on premium potential
        if variety.market_attributes.premium_potential:
            premium_score = variety.market_attributes.premium_potential / 5.0
            base_score += premium_score * 0.3
            
        # Adjust based on regional market preferences
        if "market_preferences" in context:
            market_prefs = context["market_preferences"]
            if variety.market_attributes.market_class in market_prefs:
                base_score += 0.2
                
        return max(0.0, min(1.0, base_score))

    async def _score_management_ease(self, variety: EnhancedCropVariety, context: Dict[str, Any]) -> float:
        """Score management complexity and input requirements."""
        # Simplified scoring based on disease resistance and stress tolerance
        management_score = 0.6  # Base score
        
        # Better disease resistance = easier management
        disease_score = await self._score_disease_resistance(variety, context)
        management_score += disease_score * 0.2
        
        # Better stress tolerance = easier management
        climate_score = await self._score_climate_adaptation(variety, context)
        management_score += climate_score * 0.2
        
        return max(0.0, min(1.0, management_score))

    async def _score_quality_attributes(self, variety: EnhancedCropVariety, preferences: Optional[Dict[str, Any]]) -> float:
        """Score quality attributes based on farmer preferences."""
        if not variety.quality_attributes:
            return 0.5
            
        base_score = 0.7
        
        # Adjust based on farmer preferences if provided
        if preferences and "quality_priorities" in preferences:
            quality_prefs = preferences["quality_priorities"]
            if "protein_content" in quality_prefs and variety.quality_attributes.protein_content_range:
                # Score based on protein content range
                avg_protein = statistics.mean(variety.quality_attributes.protein_content_range)
                protein_score = min(avg_protein / 15.0, 1.0)  # Normalize to max 15%
                base_score += protein_score * 0.2
                
        return max(0.0, min(1.0, base_score))

    async def _score_risk_tolerance(self, variety: EnhancedCropVariety, context: Dict[str, Any]) -> float:
        """Score variety's risk profile for the region."""
        risk_score = 0.6  # Base risk tolerance
        
        # Lower risk with better yield stability
        if variety.yield_potential and variety.yield_potential.yield_stability_rating:
            stability_factor = variety.yield_potential.yield_stability_rating / 5.0
            risk_score += stability_factor * 0.3
            
        # Lower risk with better disease resistance
        disease_score = await self._score_disease_resistance(variety, context)
        risk_score += disease_score * 0.1
        
        return max(0.0, min(1.0, risk_score))

    async def _generate_score_explanations(
        self, 
        variety: EnhancedCropVariety, 
        scores: Dict[str, float]
    ) -> Dict[str, str]:
        """Generate explanations for variety scores."""
        explanations = {}
        
        for factor, score in scores.items():
            if score >= 0.8:
                explanations[factor] = f"Excellent performance in {factor.replace('_', ' ')}"
            elif score >= 0.6:
                explanations[factor] = f"Good {factor.replace('_', ' ')} characteristics"
            elif score >= 0.4:
                explanations[factor] = f"Moderate {factor.replace('_', ' ')} suitability"
            else:
                explanations[factor] = f"Limited {factor.replace('_', ' ')} performance"
                
        return explanations

    async def _create_variety_recommendation(
        self,
        variety: EnhancedCropVariety,
        score_data: Dict[str, Any],
        regional_context: Dict[str, Any]
    ) -> VarietyRecommendation:
        """Create a complete variety recommendation with all details."""
        
        # Generate performance prediction
        performance_prediction = await self._predict_variety_performance(variety, regional_context)
        
        # Generate risk assessment
        risk_assessment = await self._assess_variety_risks(variety, regional_context)
        
        # Generate adaptation strategies
        adaptation_strategies = await self._generate_adaptation_strategies(variety, regional_context)
        
        return VarietyRecommendation(
            variety_id=variety.id,
            variety_name=variety.variety_name,
            variety_code=variety.variety_code,
            overall_score=score_data["overall_score"],
            individual_scores=score_data["individual_scores"],
            performance_prediction=performance_prediction,
            risk_assessment=risk_assessment,
            adaptation_strategies=adaptation_strategies,
            recommended_practices=await self._generate_recommended_practices(variety),
            economic_analysis=await self._generate_economic_analysis(variety, regional_context),
            confidence_level=self._determine_confidence_level(score_data["overall_score"])
        )

    async def _predict_variety_performance(
        self, 
        variety: EnhancedCropVariety, 
        context: Dict[str, Any]
    ) -> PerformancePrediction:
        """Predict variety performance in the given context."""
        
        # Base yield prediction
        if variety.yield_potential and variety.yield_potential.average_yield_range:
            avg_min, avg_max = variety.yield_potential.average_yield_range
            predicted_yield = statistics.mean([avg_min, avg_max])
            
            # Adjust for regional factors
            regional_modifier = context.get("regional_yield_modifier", 0.0)
            predicted_yield *= (1.0 + regional_modifier)
        else:
            predicted_yield = 4.0  # Default yield estimate
            
        return PerformancePrediction(
            predicted_yield_range=(predicted_yield * 0.8, predicted_yield * 1.2),
            yield_confidence=0.75,
            quality_prediction={
                "protein_content": "medium" if not variety.quality_attributes else "high",
                "test_weight": "good",
                "overall_grade": "no. 1"
            },
            performance_factors=[
                "Weather conditions will significantly impact yield",
                "Disease pressure expected to be moderate",
                "Market conditions favor this variety class"
            ]
        )

    async def _assess_variety_risks(
        self, 
        variety: EnhancedCropVariety, 
        context: Dict[str, Any]
    ) -> RiskAssessment:
        """Assess risks associated with growing this variety."""
        
        risks = []
        
        # Assess disease risks
        if variety.disease_resistance:
            disease_resistance_avg = 0.0
            resistance_count = 0
            
            if variety.disease_resistance.rust_resistance:
                rust_avg = statistics.mean(variety.disease_resistance.rust_resistance.values())
                disease_resistance_avg += rust_avg
                resistance_count += 1
                
            if variety.disease_resistance.other_disease_resistance:
                other_avg = statistics.mean(variety.disease_resistance.other_disease_resistance.values())
                disease_resistance_avg += other_avg
                resistance_count += 1
                
            if resistance_count > 0:
                disease_resistance_avg /= resistance_count
                if disease_resistance_avg < 3.0:
                    risks.append({
                        "category": "disease",
                        "level": RiskLevel.HIGH,
                        "description": "Limited disease resistance may require intensive fungicide program"
                    })
                elif disease_resistance_avg < 4.0:
                    risks.append({
                        "category": "disease", 
                        "level": RiskLevel.MODERATE,
                        "description": "Moderate disease resistance requires monitoring"
                    })
        
        # Assess climate risks
        climate_risks = context.get("climate_risks", {})
        if "drought_risk" in climate_risks and climate_risks["drought_risk"] > 0.6:
            if not variety.abiotic_stress_tolerances or variety.abiotic_stress_tolerances.drought_tolerance < 4:
                risks.append({
                    "category": "climate",
                    "level": RiskLevel.HIGH,
                    "description": "Limited drought tolerance in drought-prone region"
                })
                
        return RiskAssessment(
            overall_risk_level=RiskLevel.MODERATE,  # Default
            specific_risks=risks,
            mitigation_strategies=[
                "Monitor disease development closely",
                "Consider fungicide applications if needed",
                "Ensure adequate soil fertility"
            ]
        )

    async def _generate_adaptation_strategies(
        self, 
        variety: EnhancedCropVariety, 
        context: Dict[str, Any]
    ) -> List[AdaptationStrategy]:
        """Generate adaptation strategies for successful cultivation."""
        
        strategies = []
        
        # Planting strategies
        strategies.append(AdaptationStrategy(
            strategy_type="planting",
            description="Optimize planting date based on variety maturity",
            implementation_details=[
                "Plant during optimal soil temperature window",
                "Adjust seeding rate based on field conditions",
                "Consider seed treatment options"
            ],
            expected_benefit="Improved establishment and yield potential"
        ))
        
        # Fertility management
        strategies.append(AdaptationStrategy(
            strategy_type="fertility",
            description="Tailored fertility program for variety needs",
            implementation_details=[
                "Split nitrogen applications for optimal uptake",
                "Monitor micronutrient requirements",
                "Adjust phosphorus based on soil tests"
            ],
            expected_benefit="Enhanced yield and quality"
        ))
        
        return strategies

    async def _generate_recommended_practices(self, variety: EnhancedCropVariety) -> List[str]:
        """Generate recommended cultivation practices for the variety."""
        practices = [
            f"Use certified seed from {variety.breeding_institution}",
            "Follow recommended seeding rate for field conditions",
            "Monitor growth stages for timely management decisions"
        ]
        
        # Add variety-specific practices
        if variety.disease_resistance:
            practices.append("Implement integrated disease management program")
        if variety.abiotic_stress_tolerances and variety.abiotic_stress_tolerances.drought_tolerance >= 4:
            practices.append("Consider reduced irrigation in drought-tolerant varieties")
            
        return practices

    async def _generate_economic_analysis(
        self, 
        variety: EnhancedCropVariety, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate economic analysis for the variety."""
        
        analysis = {
            "seed_cost_premium": 0.0,
            "expected_revenue": 0.0,
            "input_cost_adjustments": {},
            "roi_factors": []
        }
        
        # Calculate seed cost premium
        if variety.market_attributes and variety.market_attributes.premium_potential:
            analysis["seed_cost_premium"] = variety.market_attributes.premium_potential * 0.1
            
        # Add ROI factors
        analysis["roi_factors"] = [
            "Higher yield potential offsets seed cost premium",
            "Improved disease resistance reduces fungicide costs", 
            "Market class commands premium prices"
        ]
        
        return analysis

    def _determine_confidence_level(self, overall_score: float) -> ConfidenceLevel:
        """Determine confidence level based on overall score."""
        if overall_score >= 0.8:
            return ConfidenceLevel.HIGH
        elif overall_score >= 0.6:
            return ConfidenceLevel.MEDIUM  
        else:
            return ConfidenceLevel.LOW

    async def _apply_diversity_filtering(
        self, 
        recommendations: List[VarietyRecommendation]
    ) -> List[VarietyRecommendation]:
        """Apply diversity filtering to ensure variety in recommendations."""
        # For now, just return top recommendations
        # Could be enhanced to ensure diversity in maturity classes, market classes, etc.
        return recommendations[:10]  # Return top 10 recommendations

    async def compare_varieties(self, request: VarietyComparisonRequest) -> VarietyComparisonResponse:
        """
        Compare multiple varieties side-by-side with detailed analysis.
        
        Args:
            request: Comparison request with variety IDs and comparison criteria
            
        Returns:
            Detailed comparison with strengths, weaknesses, and recommendations
        """
        try:
            # Get variety data for comparison
            varieties_data = []
            for variety_id in request.variety_ids:
                variety = await self._get_variety_by_id(variety_id)
                if variety:
                    varieties_data.append(variety)
                    
            if len(varieties_data) < 2:
                return VarietyComparisonResponse(
                    success=False,
                    message="At least 2 varieties required for comparison",
                    comparisons=[]
                )
                
            # Perform detailed comparisons
            comparisons = await self._perform_variety_comparisons(varieties_data, request)
            
            return VarietyComparisonResponse(
                success=True,
                comparisons=comparisons,
                comparison_summary=await self._generate_comparison_summary(comparisons)
            )
            
        except Exception as e:
            logger.error(f"Error in variety comparison: {str(e)}")
            return VarietyComparisonResponse(
                success=False,
                message=f"Comparison error: {str(e)}",
                comparisons=[]
            )

    async def _get_variety_by_id(self, variety_id: UUID) -> Optional[EnhancedCropVariety]:
        """Get variety data by ID from database."""
        # This would query the actual database
        # For now, return None as placeholder
        return None

    async def _perform_variety_comparisons(
        self, 
        varieties: List[EnhancedCropVariety], 
        request: VarietyComparisonRequest
    ) -> List[Dict[str, Any]]:
        """Perform detailed variety comparisons."""
        comparisons = []
        
        # Compare each variety against the others
        for i, variety1 in enumerate(varieties):
            for j, variety2 in enumerate(varieties[i+1:], i+1):
                comparison = await self._compare_two_varieties(variety1, variety2, request)
                comparisons.append(comparison)
                
        return comparisons

    async def _compare_two_varieties(
        self,
        variety1: EnhancedCropVariety,
        variety2: EnhancedCropVariety,
        request: VarietyComparisonRequest
    ) -> Dict[str, Any]:
        """Compare two specific varieties."""
        comparison = {
            "variety1": variety1.variety_name,
            "variety2": variety2.variety_name,
            "advantages": {
                variety1.variety_name: [],
                variety2.variety_name: []
            },
            "similarities": [],
            "key_differences": []
        }
        
        # Compare yield potential
        if (variety1.yield_potential and variety2.yield_potential and 
            variety1.yield_potential.average_yield_range and variety2.yield_potential.average_yield_range):
            
            avg1 = statistics.mean(variety1.yield_potential.average_yield_range)
            avg2 = statistics.mean(variety2.yield_potential.average_yield_range)
            
            if avg1 > avg2 * 1.1:
                comparison["advantages"][variety1.variety_name].append("Higher yield potential")
            elif avg2 > avg1 * 1.1:
                comparison["advantages"][variety2.variety_name].append("Higher yield potential")
            else:
                comparison["similarities"].append("Similar yield potential")
                
        return comparison

    async def _generate_comparison_summary(self, comparisons: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate overall comparison summary."""
        return {
            "total_comparisons": len(comparisons),
            "key_insights": [
                "Varieties show different strengths for various growing conditions",
                "Disease resistance profiles vary significantly between varieties",
                "Yield potential differences may justify variety selection"
            ],
            "recommendation": "Select variety based on primary production goals and risk tolerance"
        }


# Create service instance with database connection
import os
variety_recommendation_service = VarietyRecommendationService(
    database_url=os.getenv('DATABASE_URL')
)