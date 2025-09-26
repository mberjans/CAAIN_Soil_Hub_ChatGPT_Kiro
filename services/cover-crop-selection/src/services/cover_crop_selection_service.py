"""
Cover Crop Selection Service

Core business logic for cover crop selection and recommendations
based on soil conditions, climate data, and farmer objectives.
"""

import logging
import httpx
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    from ..models.cover_crop_models import (
        CoverCropSelectionRequest,
        CoverCropSelectionResponse,
        CoverCropRecommendation,
        CoverCropSpecies,
        CoverCropMixture,
        CoverCropType,
        GrowingSeason,
        SoilBenefit,
        ClimateData
    )
except ImportError:
    from models.cover_crop_models import (
        CoverCropSelectionRequest,
        CoverCropSelectionResponse,
        CoverCropRecommendation,
        CoverCropSpecies,
        CoverCropMixture,
        CoverCropType,
        GrowingSeason,
        SoilBenefit,
        ClimateData
    )

logger = logging.getLogger(__name__)


class CoverCropSelectionService:
    """Service for cover crop selection and recommendations."""
    
    def __init__(self):
        """Initialize the cover crop selection service."""
        self.species_database = {}
        self.mixture_database = {}
        self.climate_service_url = "http://localhost:8003"  # Data integration service
        self.initialized = False
        
    async def initialize(self):
        """Initialize the service with cover crop data."""
        try:
            await self._load_cover_crop_database()
            await self._load_mixture_database()
            self.initialized = True
            logger.info("Cover Crop Selection Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Cover Crop Selection Service: {e}")
            raise
            
    async def cleanup(self):
        """Clean up service resources."""
        self.initialized = False
        logger.info("Cover Crop Selection Service cleaned up")
        
    async def health_check(self) -> bool:
        """Check service health."""
        try:
            # Check if service is initialized and databases are loaded
            if not self.initialized:
                return False
            
            # Check if we have species data
            if not self.species_database:
                return False
                
            # Test climate service connectivity (optional)
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{self.climate_service_url}/health")
                    if response.status_code != 200:
                        logger.warning("Climate service not available")
            except Exception as e:
                logger.warning(f"Climate service health check failed: {e}")
                # Don't fail health check if climate service is down
                
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def select_cover_crops(self, request: CoverCropSelectionRequest) -> CoverCropSelectionResponse:
        """
        Select suitable cover crops based on request parameters.
        
        Args:
            request: Cover crop selection request
            
        Returns:
            Cover crop selection response with recommendations
        """
        try:
            logger.info(f"Processing cover crop selection request: {request.request_id}")
            
            # Enrich request with climate data if needed
            enriched_request = await self._enrich_climate_data(request)
            
            # Analyze field conditions
            field_assessment = await self._analyze_field_conditions(enriched_request)
            
            # Get suitable species
            suitable_species = await self._find_suitable_species(enriched_request)
            
            # Score and rank species
            scored_species = await self._score_species_suitability(
                suitable_species, enriched_request
            )
            
            # Generate single species recommendations
            single_species_recs = await self._generate_species_recommendations(
                scored_species, enriched_request
            )
            
            # Generate mixture recommendations if appropriate
            mixture_recs = await self._generate_mixture_recommendations(
                suitable_species, enriched_request
            )
            
            # Create implementation timeline
            timeline = await self._create_implementation_timeline(enriched_request)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(
                single_species_recs, field_assessment, enriched_request
            )
            
            response = CoverCropSelectionResponse(
                request_id=request.request_id,
                single_species_recommendations=single_species_recs[:5],  # Top 5
                mixture_recommendations=mixture_recs[:3] if mixture_recs else None,
                field_assessment=field_assessment,
                climate_suitability=await self._assess_climate_suitability(enriched_request),
                seasonal_considerations=await self._get_seasonal_considerations(enriched_request),
                implementation_timeline=timeline,
                monitoring_recommendations=await self._get_monitoring_recommendations(enriched_request),
                follow_up_actions=await self._get_follow_up_actions(enriched_request),
                overall_confidence=overall_confidence,
                data_sources=[
                    "USDA NRCS Cover Crop Database",
                    "Regional Extension Services",
                    "SARE Cover Crop Research",
                    "Climate Zone Integration Service"
                ]
            )
            
            logger.info(f"Generated {len(single_species_recs)} cover crop recommendations")
            return response
            
        except Exception as e:
            logger.error(f"Error in cover crop selection: {e}")
            raise
    
    async def lookup_species(self, filters: Dict[str, Any]) -> List[CoverCropSpecies]:
        """
        Lookup cover crop species based on filters.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            List of matching cover crop species
        """
        try:
            filtered_species = []
            
            for species_id, species in self.species_database.items():
                if self._species_matches_filters(species, filters):
                    filtered_species.append(species)
            
            # Sort by common name
            filtered_species.sort(key=lambda x: x.common_name)
            
            return filtered_species
            
        except Exception as e:
            logger.error(f"Error in species lookup: {e}")
            raise
    
    async def _load_cover_crop_database(self):
        """Load cover crop species database."""
        # In a real implementation, this would load from a database or file
        # For now, we'll create sample data
        
        sample_species = [
            {
                "species_id": "cc_001",
                "common_name": "Crimson Clover",
                "scientific_name": "Trifolium incarnatum",
                "cover_crop_type": CoverCropType.LEGUME,
                "hardiness_zones": ["6a", "6b", "7a", "7b", "8a", "8b", "9a"],
                "min_temp_f": 20.0,
                "max_temp_f": 85.0,
                "growing_season": GrowingSeason.WINTER,
                "ph_range": {"min": 5.5, "max": 7.0},
                "drainage_tolerance": ["well_drained", "moderately_well_drained"],
                "salt_tolerance": "low",
                "seeding_rate_lbs_acre": {"broadcast": 20, "drilled": 15},
                "planting_depth_inches": 0.25,
                "days_to_establishment": 14,
                "biomass_production": "moderate",
                "primary_benefits": [SoilBenefit.NITROGEN_FIXATION, SoilBenefit.EROSION_CONTROL],
                "nitrogen_fixation_lbs_acre": 70,
                "root_depth_feet": 2.0,
                "termination_methods": ["herbicide", "mowing", "incorporation"],
                "cash_crop_compatibility": ["corn", "cotton", "soybeans"],
                "seed_cost_per_acre": 45.0,
                "establishment_cost_per_acre": 65.0
            },
            {
                "species_id": "cc_002", 
                "common_name": "Winter Rye",
                "scientific_name": "Secale cereale",
                "cover_crop_type": CoverCropType.GRASS,
                "hardiness_zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"],
                "min_temp_f": -30.0,
                "max_temp_f": 75.0,
                "growing_season": GrowingSeason.WINTER,
                "ph_range": {"min": 5.0, "max": 7.5},
                "drainage_tolerance": ["well_drained", "moderately_well_drained", "somewhat_poorly_drained"],
                "salt_tolerance": "moderate",
                "seeding_rate_lbs_acre": {"broadcast": 90, "drilled": 60},
                "planting_depth_inches": 1.0,
                "days_to_establishment": 7,
                "biomass_production": "high",
                "primary_benefits": [SoilBenefit.EROSION_CONTROL, SoilBenefit.WEED_SUPPRESSION, SoilBenefit.NUTRIENT_SCAVENGING],
                "root_depth_feet": 3.0,
                "termination_methods": ["herbicide", "mowing", "roller_crimper"],
                "cash_crop_compatibility": ["corn", "soybeans", "cotton"],
                "seed_cost_per_acre": 35.0,
                "establishment_cost_per_acre": 50.0
            },
            {
                "species_id": "cc_003",
                "common_name": "Radish (Tillage)",
                "scientific_name": "Raphanus sativus",
                "cover_crop_type": CoverCropType.BRASSICA,
                "hardiness_zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
                "min_temp_f": 25.0,
                "max_temp_f": 80.0,
                "growing_season": GrowingSeason.FALL,
                "ph_range": {"min": 6.0, "max": 7.5},
                "drainage_tolerance": ["well_drained", "moderately_well_drained"],
                "salt_tolerance": "moderate",
                "seeding_rate_lbs_acre": {"broadcast": 12, "drilled": 8},
                "planting_depth_inches": 0.5,
                "days_to_establishment": 5,
                "biomass_production": "moderate",
                "primary_benefits": [SoilBenefit.COMPACTION_RELIEF, SoilBenefit.NUTRIENT_SCAVENGING],
                "root_depth_feet": 4.0,
                "termination_methods": ["winter_kill", "mowing"],
                "cash_crop_compatibility": ["corn", "soybeans"],
                "seed_cost_per_acre": 25.0,
                "establishment_cost_per_acre": 35.0
            }
        ]
        
        for species_data in sample_species:
            species = CoverCropSpecies(**species_data)
            self.species_database[species.species_id] = species
        
        logger.info(f"Loaded {len(self.species_database)} cover crop species")
    
    async def _load_mixture_database(self):
        """Load cover crop mixture database."""
        # Sample mixture data
        sample_mixtures = [
            {
                "mixture_id": "mix_001",
                "mixture_name": "Winter N-Fixer Blend",
                "species_list": [
                    {"species_id": "cc_001", "name": "Crimson Clover", "rate_lbs_acre": 15},
                    {"species_id": "cc_002", "name": "Winter Rye", "rate_lbs_acre": 40}
                ],
                "total_seeding_rate": 55,
                "mixture_benefits": ["Nitrogen fixation", "Erosion control", "Biomass production"],
                "complexity_level": "moderate"
            }
        ]
        
        for mixture_data in sample_mixtures:
            mixture = CoverCropMixture(**mixture_data)
            self.mixture_database[mixture.mixture_id] = mixture
        
        logger.info(f"Loaded {len(self.mixture_database)} cover crop mixtures")
    
    async def _enrich_climate_data(self, request: CoverCropSelectionRequest) -> CoverCropSelectionRequest:
        """Enrich request with climate data if needed."""
        if request.climate_data and request.climate_data.hardiness_zone:
            return request
            
        try:
            # Call climate service to get zone information
            async with httpx.AsyncClient() as client:
                climate_response = await client.post(
                    f"{self.climate_service_url}/api/v1/climate/zone-lookup",
                    json={
                        "latitude": request.location.get("latitude"),
                        "longitude": request.location.get("longitude")
                    }
                )
                
                if climate_response.status_code == 200:
                    climate_data = climate_response.json()
                    # Update request with climate information
                    if not request.climate_data:
                        request.climate_data = ClimateData(
                            hardiness_zone=climate_data.get("zone_id", "7a")
                        )
                    else:
                        request.climate_data.hardiness_zone = climate_data.get("zone_id", "7a")
        
        except Exception as e:
            logger.warning(f"Could not enrich climate data: {e}")
            # Use default if climate service is unavailable
            if not request.climate_data:
                request.climate_data = ClimateData(hardiness_zone="7a")
        
        return request
    
    async def _analyze_field_conditions(self, request: CoverCropSelectionRequest) -> Dict[str, Any]:
        """Analyze field conditions for cover crop suitability."""
        conditions = request.soil_conditions
        
        analysis = {
            "soil_health_score": 0.0,
            "limiting_factors": [],
            "advantages": [],
            "recommendations": []
        }
        
        # pH analysis
        if 6.0 <= conditions.ph <= 7.0:
            analysis["advantages"].append("Optimal pH range for most cover crops")
            ph_score = 1.0
        elif 5.5 <= conditions.ph < 6.0 or 7.0 < conditions.ph <= 7.5:
            analysis["recommendations"].append("pH is slightly outside optimal range")
            ph_score = 0.8
        else:
            analysis["limiting_factors"].append("pH is outside optimal range for most cover crops")
            ph_score = 0.6
        
        # Organic matter analysis
        if conditions.organic_matter_percent >= 3.5:
            analysis["advantages"].append("Good organic matter content")
            om_score = 1.0
        elif conditions.organic_matter_percent >= 2.5:
            analysis["recommendations"].append("Organic matter could be improved")
            om_score = 0.7
        else:
            analysis["limiting_factors"].append("Low organic matter - prioritize organic matter building cover crops")
            om_score = 0.5
        
        # Drainage analysis
        if conditions.drainage_class in ["well_drained", "moderately_well_drained"]:
            drainage_score = 1.0
        elif conditions.drainage_class == "somewhat_poorly_drained":
            analysis["recommendations"].append("Consider drainage-tolerant species")
            drainage_score = 0.7
        else:
            analysis["limiting_factors"].append("Poor drainage limits cover crop options")
            drainage_score = 0.4
        
        # Calculate overall soil health score
        analysis["soil_health_score"] = (ph_score + om_score + drainage_score) / 3
        
        return analysis
    
    async def _find_suitable_species(self, request: CoverCropSelectionRequest) -> List[CoverCropSpecies]:
        """Find cover crop species suitable for the given conditions."""
        suitable_species = []
        
        for species in self.species_database.values():
            if await self._is_species_suitable(species, request):
                suitable_species.append(species)
        
        return suitable_species
    
    async def _is_species_suitable(self, species: CoverCropSpecies, request: CoverCropSelectionRequest) -> bool:
        """Check if a species is suitable for the given conditions."""
        # Check hardiness zone compatibility
        if request.climate_data and request.climate_data.hardiness_zone:
            if request.climate_data.hardiness_zone not in species.hardiness_zones:
                return False
        
        # Check pH tolerance
        soil_ph = request.soil_conditions.ph
        if not (species.ph_range["min"] <= soil_ph <= species.ph_range["max"]):
            return False
        
        # Check drainage compatibility
        if request.soil_conditions.drainage_class not in species.drainage_tolerance:
            return False
        
        # Check planting window compatibility
        planting_start = request.planting_window.get("start")
        planting_end = request.planting_window.get("end")
        
        if planting_start and planting_end:
            # Basic seasonal compatibility check
            plant_month = planting_start.month
            
            if species.growing_season == GrowingSeason.WINTER and plant_month not in [9, 10, 11]:
                return False
            elif species.growing_season == GrowingSeason.SUMMER and plant_month not in [4, 5, 6]:
                return False
            elif species.growing_season == GrowingSeason.FALL and plant_month not in [7, 8, 9]:
                return False
        
        return True
    
    async def _score_species_suitability(self, species_list: List[CoverCropSpecies], request: CoverCropSelectionRequest) -> List[Tuple[CoverCropSpecies, float]]:
        """Score species suitability based on objectives and conditions."""
        scored_species = []
        
        for species in species_list:
            score = await self._calculate_species_score(species, request)
            scored_species.append((species, score))
        
        # Sort by score (highest first)
        scored_species.sort(key=lambda x: x[1], reverse=True)
        
        return scored_species
    
    async def _calculate_species_score(self, species: CoverCropSpecies, request: CoverCropSelectionRequest) -> float:
        """Calculate suitability score for a species."""
        score = 0.0
        
        # Base score for meeting basic requirements
        score += 0.3
        
        # Objective alignment (40% of score)
        objective_score = 0.0
        total_objectives = len(request.objectives.primary_goals)
        
        for goal in request.objectives.primary_goals:
            if goal in species.primary_benefits:
                objective_score += 1.0 / total_objectives
        
        score += objective_score * 0.4
        
        # pH compatibility (10% of score)
        soil_ph = request.soil_conditions.ph
        ph_optimal_range = (species.ph_range["min"] + species.ph_range["max"]) / 2
        ph_distance = abs(soil_ph - ph_optimal_range)
        ph_score = max(0, 1.0 - (ph_distance / 2.0))  # Penalty for pH distance
        score += ph_score * 0.1
        
        # Economic considerations (10% of score)
        if request.objectives.budget_per_acre:
            if species.establishment_cost_per_acre and species.establishment_cost_per_acre <= request.objectives.budget_per_acre:
                score += 0.1
            elif species.establishment_cost_per_acre and species.establishment_cost_per_acre > request.objectives.budget_per_acre * 1.5:
                score -= 0.05  # Penalty for high cost
        
        # Bonus for special benefits
        if request.objectives.nitrogen_needs and SoilBenefit.NITROGEN_FIXATION in species.primary_benefits:
            score += 0.1
        
        if request.soil_conditions.compaction_issues and SoilBenefit.COMPACTION_RELIEF in species.primary_benefits:
            score += 0.1
        
        return min(1.0, max(0.0, score))  # Clamp between 0 and 1
    
    async def _generate_species_recommendations(self, scored_species: List[Tuple[CoverCropSpecies, float]], request: CoverCropSelectionRequest) -> List[CoverCropRecommendation]:
        """Generate detailed recommendations for each species."""
        recommendations = []
        
        for species, score in scored_species:
            # Calculate seeding rate
            seeding_rate = species.seeding_rate_lbs_acre.get("drilled", 
                species.seeding_rate_lbs_acre.get("broadcast", 0))
            
            # Determine planting date
            planting_date = request.planting_window.get("start", date.today())
            
            # Generate expected benefits
            expected_benefits = []
            for benefit in species.primary_benefits:
                if benefit == SoilBenefit.NITROGEN_FIXATION:
                    expected_benefits.append(f"Nitrogen fixation: {species.nitrogen_fixation_lbs_acre or 'Variable'} lbs N/acre")
                elif benefit == SoilBenefit.EROSION_CONTROL:
                    expected_benefits.append("Significant erosion control and soil protection")
                elif benefit == SoilBenefit.ORGANIC_MATTER:
                    expected_benefits.append("Organic matter improvement")
                elif benefit == SoilBenefit.COMPACTION_RELIEF:
                    expected_benefits.append("Soil compaction alleviation through deep rooting")
                else:
                    expected_benefits.append(benefit.value.replace("_", " ").title())
            
            # Generate management notes
            management_notes = [
                f"Plant at {species.planting_depth_inches} inch depth",
                f"Establishment typically occurs in {species.days_to_establishment} days",
                f"Termination options: {', '.join(species.termination_methods)}"
            ]
            
            # Success indicators
            success_indicators = [
                "Uniform emergence and stand establishment",
                f"Good biomass production ({species.biomass_production} level expected)",
                "Healthy plant color and growth"
            ]
            
            if species.nitrogen_fixation_lbs_acre:
                success_indicators.append("Active nodulation visible on roots (for legumes)")
            
            recommendation = CoverCropRecommendation(
                species=species,
                suitability_score=score,
                confidence_level=min(0.95, score + 0.1),  # Slightly higher than suitability
                seeding_rate_recommendation=seeding_rate,
                planting_date_recommendation=planting_date,
                termination_recommendation=species.termination_methods[0],
                expected_benefits=expected_benefits,
                nitrogen_contribution=species.nitrogen_fixation_lbs_acre,
                soil_improvement_score=score * 0.9,  # Based on suitability
                cost_per_acre=species.establishment_cost_per_acre,
                roi_estimate=self._calculate_roi_estimate(species, request),
                management_notes=management_notes,
                potential_challenges=species.potential_issues,
                success_indicators=success_indicators
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_roi_estimate(self, species: CoverCropSpecies, request: CoverCropSelectionRequest) -> Optional[float]:
        """Calculate estimated ROI for cover crop investment."""
        if not species.establishment_cost_per_acre:
            return None
        
        # Simple ROI calculation based on benefits
        estimated_benefits = 0.0
        
        # Nitrogen value
        if species.nitrogen_fixation_lbs_acre:
            nitrogen_value = species.nitrogen_fixation_lbs_acre * 0.50  # $0.50/lb N
            estimated_benefits += nitrogen_value
        
        # Soil erosion prevention value
        if SoilBenefit.EROSION_CONTROL in species.primary_benefits:
            estimated_benefits += 25.0  # Conservative erosion prevention value
        
        # Organic matter value
        if SoilBenefit.ORGANIC_MATTER in species.primary_benefits:
            estimated_benefits += 15.0  # Organic matter improvement value
        
        if estimated_benefits > 0:
            roi = ((estimated_benefits - species.establishment_cost_per_acre) / species.establishment_cost_per_acre) * 100
            return max(0, roi)
        
        return None
    
    async def _generate_mixture_recommendations(self, suitable_species: List[CoverCropSpecies], request: CoverCropSelectionRequest) -> Optional[List[CoverCropMixture]]:
        """Generate cover crop mixture recommendations."""
        # For now, return existing mixtures that match conditions
        # In a full implementation, this would create custom mixtures
        
        suitable_mixtures = []
        
        for mixture in self.mixture_database.values():
            # Check if mixture components are suitable
            mixture_suitable = True
            for component in mixture.species_list:
                species_id = component.get("species_id")
                if species_id and species_id in self.species_database:
                    species = self.species_database[species_id]
                    if species not in suitable_species:
                        mixture_suitable = False
                        break
            
            if mixture_suitable:
                suitable_mixtures.append(mixture)
        
        return suitable_mixtures if suitable_mixtures else None
    
    async def _assess_climate_suitability(self, request: CoverCropSelectionRequest) -> Dict[str, Any]:
        """Assess climate suitability for cover crops."""
        return {
            "hardiness_zone": request.climate_data.hardiness_zone if request.climate_data else "Unknown",
            "suitability": "Good" if request.climate_data else "Unknown",
            "considerations": ["Verify local frost dates", "Monitor weather patterns"]
        }
    
    async def _get_seasonal_considerations(self, request: CoverCropSelectionRequest) -> List[str]:
        """Get seasonal considerations for cover crop establishment."""
        considerations = [
            "Plant within recommended seeding window for best establishment",
            "Monitor soil moisture conditions before and after planting",
            "Consider weather forecast for planting timing"
        ]
        
        planting_start = request.planting_window.get("start")
        if planting_start:
            if planting_start.month in [9, 10, 11]:
                considerations.append("Fall planting - ensure adequate time before first frost")
            elif planting_start.month in [3, 4, 5]:
                considerations.append("Spring planting - wait for soil to warm and dry")
        
        return considerations
    
    async def _create_implementation_timeline(self, request: CoverCropSelectionRequest) -> List[Dict[str, Any]]:
        """Create implementation timeline."""
        planting_date = request.planting_window.get("start", date.today())
        
        timeline = [
            {
                "phase": "Preparation",
                "date_range": f"{planting_date - timedelta(days=14)} to {planting_date - timedelta(days=3)}",
                "tasks": ["Soil preparation", "Seed procurement", "Equipment check"]
            },
            {
                "phase": "Planting",
                "date_range": f"{planting_date} to {planting_date + timedelta(days=7)}",
                "tasks": ["Seeding", "Initial irrigation if needed"]
            },
            {
                "phase": "Establishment",
                "date_range": f"{planting_date + timedelta(days=7)} to {planting_date + timedelta(days=30)}",
                "tasks": ["Monitor emergence", "Assess stand", "Pest monitoring"]
            }
        ]
        
        return timeline
    
    async def _get_monitoring_recommendations(self, request: CoverCropSelectionRequest) -> List[str]:
        """Get monitoring recommendations."""
        return [
            "Monitor emergence within 7-14 days after planting",
            "Assess stand uniformity and density at 3-4 weeks",
            "Check for pest issues throughout growing season",
            "Evaluate biomass production before termination",
            "Document termination effectiveness and timing"
        ]
    
    async def _get_follow_up_actions(self, request: CoverCropSelectionRequest) -> List[str]:
        """Get follow-up action recommendations."""
        return [
            "Plan termination strategy 2-3 weeks before next cash crop planting",
            "Consider soil testing after cover crop termination",
            "Evaluate cover crop performance for next year's planning",
            "Document lessons learned and successful practices"
        ]
    
    def _calculate_overall_confidence(self, recommendations: List[CoverCropRecommendation], field_assessment: Dict[str, Any], request: CoverCropSelectionRequest) -> float:
        """Calculate overall confidence in recommendations."""
        if not recommendations:
            return 0.0
        
        # Base confidence on top recommendation
        top_confidence = recommendations[0].confidence_level
        
        # Adjust based on field conditions
        soil_health_score = field_assessment.get("soil_health_score", 0.5)
        
        # Adjust based on data completeness
        data_completeness = 0.7  # Base completeness
        if request.soil_conditions:
            data_completeness += 0.1
        if request.climate_data:
            data_completeness += 0.1
        if request.objectives:
            data_completeness += 0.1
        
        overall_confidence = (top_confidence + soil_health_score + data_completeness) / 3
        return min(0.95, overall_confidence)
    
    def _species_matches_filters(self, species: CoverCropSpecies, filters: Dict[str, Any]) -> bool:
        """Check if species matches filter criteria."""
        # Species name filter
        if "species_name" in filters and filters["species_name"]:
            name_lower = filters["species_name"].lower()
            if (name_lower not in species.common_name.lower() and 
                name_lower not in species.scientific_name.lower()):
                return False
        
        # Cover crop type filter
        if "cover_crop_type" in filters and filters["cover_crop_type"]:
            if species.cover_crop_type != filters["cover_crop_type"]:
                return False
        
        # Hardiness zone filter
        if "hardiness_zone" in filters and filters["hardiness_zone"]:
            if filters["hardiness_zone"] not in species.hardiness_zones:
                return False
        
        # Growing season filter
        if "growing_season" in filters and filters["growing_season"]:
            if species.growing_season != filters["growing_season"]:
                return False
        
        # Primary benefit filter
        if "primary_benefit" in filters and filters["primary_benefit"]:
            if filters["primary_benefit"] not in species.primary_benefits:
                return False
        
        return True