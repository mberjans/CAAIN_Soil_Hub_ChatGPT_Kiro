"""
Main Crop Integration Service

Service for analyzing compatibility between cover crops and main crops,
integrating with crop rotation data, and providing timing analysis.
"""

import logging
import httpx
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    from ..models.cover_crop_models import (
        CoverCropSpecies,
        MainCropRotationPlan,
        CoverCropRotationIntegration,
        CropTimingWindow,
        RotationBenefitAnalysis,
        SoilBenefit,
        CoverCropType
    )
except ImportError:
    from models.cover_crop_models import (
        CoverCropSpecies,
        MainCropRotationPlan,
        CoverCropRotationIntegration,
        CropTimingWindow,
        RotationBenefitAnalysis,
        SoilBenefit,
        CoverCropType
    )

logger = logging.getLogger(__name__)


class MainCropIntegrationService:
    """Service for main crop and cover crop integration analysis."""
    
    def __init__(self):
        """Initialize the main crop integration service."""
        self.rotation_service_url = "http://localhost:8001"  # Recommendation engine service
        self.rotation_database = {}
        self.compatibility_matrix = {}
        self.timing_windows = {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize the service with rotation data."""
        try:
            await self._load_rotation_database()
            await self._build_compatibility_matrix()
            await self._load_timing_windows()
            self.initialized = True
            logger.info("Main Crop Integration Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Main Crop Integration Service: {e}")
            raise
            
    async def cleanup(self):
        """Clean up service resources."""
        self.initialized = False
        logger.info("Main Crop Integration Service cleaned up")
        
    async def health_check(self) -> bool:
        """Check service health."""
        try:
            if not self.initialized:
                return False
                
            # Test rotation service connectivity
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{self.rotation_service_url}/health")
                    if response.status_code != 200:
                        logger.warning("Rotation service not available")
            except Exception as e:
                logger.warning(f"Rotation service health check failed: {e}")
                
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def analyze_main_crop_compatibility(
        self, 
        cover_crop: CoverCropSpecies, 
        main_crop: str,
        position: str = "before"  # "before", "after", "between"
    ) -> Dict[str, Any]:
        """
        Analyze compatibility between a cover crop and main crop.
        
        Args:
            cover_crop: Cover crop species to analyze
            main_crop: Main crop name
            position: Position in rotation (before/after/between main crop)
            
        Returns:
            Compatibility analysis results
        """
        try:
            logger.info(f"Analyzing compatibility: {cover_crop.common_name} {position} {main_crop}")
            
            compatibility_score = await self._calculate_compatibility_score(
                cover_crop, main_crop, position
            )
            
            benefits = await self._analyze_integration_benefits(
                cover_crop, main_crop, position
            )
            
            risks = await self._identify_integration_risks(
                cover_crop, main_crop, position
            )
            
            timing_analysis = await self._analyze_timing_compatibility(
                cover_crop, main_crop, position
            )
            
            return {
                "compatibility_score": compatibility_score,
                "overall_rating": self._get_compatibility_rating(compatibility_score),
                "benefits": benefits,
                "risks": risks,
                "timing_analysis": timing_analysis,
                "recommendations": await self._generate_integration_recommendations(
                    cover_crop, main_crop, position, compatibility_score
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing compatibility: {e}")
            raise
    
    async def get_rotation_integration_plan(
        self, 
        rotation_name: str,
        available_cover_crops: List[CoverCropSpecies],
        objectives: List[str] = None
    ) -> CoverCropRotationIntegration:
        """
        Create a cover crop integration plan for a specific rotation.
        
        Args:
            rotation_name: Name of the rotation system
            available_cover_crops: List of available cover crop species
            objectives: Specific integration objectives
            
        Returns:
            Complete rotation integration plan
        """
        try:
            logger.info(f"Creating integration plan for rotation: {rotation_name}")
            
            # Get rotation plan
            rotation_plan = await self._get_rotation_plan(rotation_name)
            if not rotation_plan:
                raise ValueError(f"Rotation plan '{rotation_name}' not found")
                
            # Identify integration positions
            integration_positions = await self._identify_integration_positions(rotation_plan)
            
            # Select optimal cover crops for each position
            cover_crop_positions = []
            compatibility_scores = {}
            
            for position in integration_positions:
                optimal_species = await self._select_optimal_cover_crop(
                    position, available_cover_crops, objectives
                )
                
                if optimal_species:
                    position_data = {
                        "position_id": position["id"],
                        "position_description": position["description"],
                        "preceding_crop": position.get("preceding_crop"),
                        "following_crop": position.get("following_crop"),
                        "recommended_species": optimal_species["species"].species_id,
                        "species_name": optimal_species["species"].common_name,
                        "timing_window": optimal_species["timing"],
                        "management_notes": optimal_species["management_notes"]
                    }
                    cover_crop_positions.append(position_data)
                    compatibility_scores[position["id"]] = optimal_species["compatibility_score"]
            
            # Analyze overall benefits
            nitrogen_benefits = await self._calculate_nitrogen_cycling_benefits(
                rotation_plan, cover_crop_positions
            )
            
            pest_benefits = await self._analyze_pest_management_benefits(
                rotation_plan, cover_crop_positions
            )
            
            soil_benefits = await self._analyze_soil_health_improvements(
                rotation_plan, cover_crop_positions
            )
            
            # Calculate economic impact
            cost_impact, benefit_value = await self._calculate_economic_impact(
                rotation_plan, cover_crop_positions
            )
            
            integration = CoverCropRotationIntegration(
                integration_id=f"integration_{rotation_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                rotation_plan=rotation_plan,
                cover_crop_positions=cover_crop_positions,
                nitrogen_cycling_benefits=nitrogen_benefits,
                pest_management_benefits=pest_benefits,
                soil_health_improvements=soil_benefits,
                compatibility_scores=compatibility_scores,
                risk_factors=await self._identify_integration_risks_overall(rotation_plan, cover_crop_positions),
                estimated_cost_impact=cost_impact,
                estimated_benefit_value=benefit_value
            )
            
            return integration
            
        except Exception as e:
            logger.error(f"Error creating rotation integration plan: {e}")
            raise
    
    async def analyze_timing_windows(
        self,
        rotation_plan: MainCropRotationPlan,
        region: str = None,
        climate_zone: str = None
    ) -> List[CropTimingWindow]:
        """
        Analyze timing windows for cover crop integration in rotation.
        
        Args:
            rotation_plan: Rotation plan to analyze
            region: Geographic region
            climate_zone: Climate zone identifier
            
        Returns:
            List of timing windows for cover crop integration
        """
        try:
            logger.info(f"Analyzing timing windows for rotation: {rotation_plan.rotation_name}")
            
            timing_windows = []
            
            for i, crop in enumerate(rotation_plan.sequence):
                # Analyze gaps between main crops
                if i < len(rotation_plan.sequence) - 1:
                    next_crop = rotation_plan.sequence[i + 1]
                    
                    # Get typical timing for current and next crop
                    current_harvest = rotation_plan.harvest_windows.get(crop, {})
                    next_planting = rotation_plan.typical_planting_dates.get(next_crop, {})
                    
                    if current_harvest and next_planting:
                        window_id = f"{rotation_plan.rotation_id}_gap_{i}_{i+1}"
                        
                        # Calculate cover crop window
                        harvest_end = self._parse_date_range(current_harvest.get("end", ""))
                        planting_start = self._parse_date_range(next_planting.get("start", ""))
                        
                        if harvest_end and planting_start:
                            # Allow 2 weeks after harvest and 2 weeks before next planting
                            cover_crop_start = harvest_end + timedelta(days=14)
                            cover_crop_end = planting_start - timedelta(days=14)
                            
                            if cover_crop_end > cover_crop_start:
                                timing_window = CropTimingWindow(
                                    window_id=window_id,
                                    crop_name=f"Cover crop between {crop} and {next_crop}",
                                    window_type="cover_crop_window",
                                    optimal_start=cover_crop_start,
                                    optimal_end=cover_crop_end,
                                    region=region,
                                    climate_zone=climate_zone,
                                    flexibility_days=7,
                                    critical_factors=[
                                        f"Allow time after {crop} harvest",
                                        f"Terminate before {next_crop} planting"
                                    ],
                                    weather_dependencies=[
                                        "Soil moisture for establishment",
                                        "Temperature for growth",
                                        "Frost dates for termination"
                                    ]
                                )
                                timing_windows.append(timing_window)
            
            return timing_windows
            
        except Exception as e:
            logger.error(f"Error analyzing timing windows: {e}")
            raise
    
    async def generate_benefit_analysis(
        self,
        integration_plan: CoverCropRotationIntegration,
        field_conditions: Dict[str, Any] = None
    ) -> RotationBenefitAnalysis:
        """
        Generate comprehensive benefit analysis for rotation integration.
        
        Args:
            integration_plan: Cover crop rotation integration plan
            field_conditions: Specific field conditions
            
        Returns:
            Detailed benefit analysis
        """
        try:
            logger.info(f"Generating benefit analysis for integration: {integration_plan.integration_id}")
            
            # Calculate quantified benefits
            nitrogen_value = await self._calculate_nitrogen_fixation_value(integration_plan)
            erosion_value = await self._calculate_erosion_prevention_value(integration_plan)
            organic_matter_improvement = await self._calculate_organic_matter_improvement(integration_plan)
            weed_suppression_value = await self._calculate_weed_suppression_value(integration_plan)
            
            # Analyze pest and disease management
            pest_reduction = await self._analyze_pest_pressure_reduction(integration_plan)
            disease_effectiveness = await self._analyze_disease_break_effectiveness(integration_plan)
            beneficial_insect_score = await self._calculate_beneficial_insect_support(integration_plan)
            
            # Long-term impact projections
            soil_health_trajectory = await self._project_soil_health_trajectory(integration_plan)
            yield_impacts = await self._project_yield_impacts(integration_plan)
            sustainability_improvements = await self._identify_sustainability_improvements(integration_plan)
            
            # Economic analysis
            total_benefit_value = (
                nitrogen_value + erosion_value + 
                organic_matter_improvement + weed_suppression_value
            )
            
            cost_benefit_ratio = (
                total_benefit_value / integration_plan.estimated_cost_impact 
                if integration_plan.estimated_cost_impact > 0 else float('inf')
            )
            
            payback_period = (
                integration_plan.estimated_cost_impact / total_benefit_value 
                if total_benefit_value > 0 else None
            )
            
            # Risk assessment
            implementation_risks = await self._assess_implementation_risks(integration_plan)
            mitigation_strategies = await self._develop_mitigation_strategies(implementation_risks)
            
            confidence_level = await self._calculate_analysis_confidence(
                integration_plan, field_conditions
            )
            
            analysis = RotationBenefitAnalysis(
                analysis_id=f"analysis_{integration_plan.integration_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                rotation_plan=integration_plan.rotation_plan,
                cover_crop_integration=integration_plan,
                nitrogen_fixation_value=nitrogen_value,
                erosion_prevention_value=erosion_value,
                organic_matter_improvement=organic_matter_improvement,
                weed_suppression_value=weed_suppression_value,
                pest_pressure_reduction=pest_reduction,
                disease_break_effectiveness=disease_effectiveness,
                beneficial_insect_support=beneficial_insect_score,
                soil_health_trajectory=soil_health_trajectory,
                yield_impact_projections=yield_impacts,
                sustainability_improvements=sustainability_improvements,
                total_benefit_value=total_benefit_value,
                cost_benefit_ratio=cost_benefit_ratio,
                payback_period_years=payback_period,
                implementation_risks=implementation_risks,
                mitigation_strategies=mitigation_strategies,
                confidence_level=confidence_level
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating benefit analysis: {e}")
            raise
    
    # Private helper methods
    
    async def _load_rotation_database(self):
        """Load rotation system database."""
        # Sample rotation data based on existing CropRotationService patterns
        sample_rotations = {
            "corn_soybean": MainCropRotationPlan(
                rotation_id="rot_cs_001",
                rotation_name="Corn-Soybean",
                sequence=["corn", "soybean"],
                duration_years=2,
                region_suitability=["midwest", "great_plains"],
                primary_benefits=[
                    "nitrogen_fixation_benefit",
                    "pest_cycle_disruption", 
                    "herbicide_resistance_management"
                ],
                sustainability_rating=7.5,
                complexity_level="simple",
                economic_performance="excellent",
                risk_level="low",
                typical_planting_dates={
                    "corn": {"start": "April 15", "end": "May 31"},
                    "soybean": {"start": "May 1", "end": "June 15"}
                },
                harvest_windows={
                    "corn": {"start": "September 15", "end": "November 15"},
                    "soybean": {"start": "September 1", "end": "October 31"}
                }
            ),
            "corn_soybean_wheat": MainCropRotationPlan(
                rotation_id="rot_csw_001",
                rotation_name="Corn-Soybean-Wheat",
                sequence=["corn", "soybean", "wheat"],
                duration_years=3,
                region_suitability=["midwest", "eastern_corn_belt"],
                primary_benefits=[
                    "increased_diversity",
                    "extended_harvest_window",
                    "soil_erosion_control"
                ],
                sustainability_rating=8.5,
                complexity_level="moderate",
                economic_performance="good",
                risk_level="moderate",
                typical_planting_dates={
                    "corn": {"start": "April 15", "end": "May 31"},
                    "soybean": {"start": "May 1", "end": "June 15"},
                    "wheat": {"start": "September 15", "end": "October 31"}
                },
                harvest_windows={
                    "corn": {"start": "September 15", "end": "November 15"},
                    "soybean": {"start": "September 1", "end": "October 31"},
                    "wheat": {"start": "June 15", "end": "July 31"}
                }
            )
        }
        
        self.rotation_database = sample_rotations
        logger.info(f"Loaded {len(self.rotation_database)} rotation systems")
    
    async def _build_compatibility_matrix(self):
        """Build crop compatibility matrix."""
        self.compatibility_matrix = {
            "corn": {
                "before": {
                    "legume": 0.9,  # Excellent - nitrogen benefit
                    "grass": 0.7,   # Good - residue management
                    "brassica": 0.8, # Good - pest break
                    "forb": 0.6     # Moderate
                },
                "after": {
                    "legume": 0.8,  # Good - utilize residual N
                    "grass": 0.9,   # Excellent - scavenge N
                    "brassica": 0.7, # Good
                    "forb": 0.6     # Moderate
                }
            },
            "soybean": {
                "before": {
                    "legume": 0.6,  # Moderate - same family
                    "grass": 0.9,   # Excellent - different family
                    "brassica": 0.8, # Good - pest break
                    "forb": 0.7     # Good
                },
                "after": {
                    "legume": 0.5,  # Poor - same family issues
                    "grass": 0.8,   # Good - utilize N
                    "brassica": 0.7, # Good
                    "forb": 0.6     # Moderate
                }
            },
            "wheat": {
                "before": {
                    "legume": 0.9,  # Excellent - N benefit
                    "grass": 0.6,   # Moderate - same family
                    "brassica": 0.8, # Good - pest break
                    "forb": 0.7     # Good
                },
                "after": {
                    "legume": 0.7,  # Good
                    "grass": 0.5,   # Poor - disease carryover
                    "brassica": 0.8, # Good - different family
                    "forb": 0.7     # Good
                }
            }
        }
        logger.info("Built crop compatibility matrix")
    
    async def _load_timing_windows(self):
        """Load timing windows database."""
        # This would typically load from database or external service
        self.timing_windows = {}
        logger.info("Loaded timing windows database")
    
    async def _calculate_compatibility_score(
        self, 
        cover_crop: CoverCropSpecies, 
        main_crop: str, 
        position: str
    ) -> float:
        """Calculate compatibility score between cover crop and main crop."""
        base_score = 0.7
        
        # Get compatibility from matrix
        crop_compatibility = self.compatibility_matrix.get(main_crop.lower(), {})
        position_compatibility = crop_compatibility.get(position, {})
        type_score = position_compatibility.get(cover_crop.cover_crop_type.value, 0.6)
        
        # Adjust for specific benefits
        if main_crop.lower() == "corn" and SoilBenefit.NITROGEN_FIXATION in cover_crop.primary_benefits:
            type_score += 0.1
        
        if SoilBenefit.PEST_MANAGEMENT in cover_crop.primary_benefits:
            type_score += 0.05
            
        return min(1.0, type_score)
    
    async def _analyze_integration_benefits(
        self, 
        cover_crop: CoverCropSpecies, 
        main_crop: str, 
        position: str
    ) -> List[str]:
        """Analyze integration benefits."""
        benefits = []
        
        # Nitrogen benefits
        if SoilBenefit.NITROGEN_FIXATION in cover_crop.primary_benefits:
            if main_crop.lower() in ["corn", "wheat"] and position == "before":
                benefits.append(f"Nitrogen fixation benefit for following {main_crop}")
        
        # Pest management benefits
        if SoilBenefit.PEST_MANAGEMENT in cover_crop.primary_benefits:
            benefits.append(f"Pest cycle disruption for {main_crop}")
        
        # Soil health benefits
        if SoilBenefit.EROSION_CONTROL in cover_crop.primary_benefits:
            benefits.append("Soil erosion protection between crops")
            
        if SoilBenefit.ORGANIC_MATTER in cover_crop.primary_benefits:
            benefits.append("Organic matter improvement")
        
        return benefits
    
    async def _identify_integration_risks(
        self, 
        cover_crop: CoverCropSpecies, 
        main_crop: str, 
        position: str
    ) -> List[str]:
        """Identify integration risks."""
        risks = []
        
        # Timing risks
        if position == "before":
            risks.append("Risk of delayed main crop planting if termination issues occur")
        
        # Allelopathy risks
        if cover_crop.cover_crop_type == CoverCropType.GRASS and main_crop.lower() == "soybean":
            risks.append("Potential allelopathic effects on soybean emergence")
        
        # Management complexity
        if cover_crop.cover_crop_type == CoverCropType.MIXTURE:
            risks.append("Increased management complexity with mixture")
            
        return risks
    
    async def _analyze_timing_compatibility(
        self, 
        cover_crop: CoverCropSpecies, 
        main_crop: str, 
        position: str
    ) -> Dict[str, Any]:
        """Analyze timing compatibility."""
        return {
            "establishment_window": f"{cover_crop.days_to_establishment} days to establishment",
            "termination_flexibility": len(cover_crop.termination_methods),
            "seasonal_constraints": cover_crop.growing_season.value,
            "timing_risk": "low" if len(cover_crop.termination_methods) > 2 else "moderate"
        }
    
    async def _generate_integration_recommendations(
        self, 
        cover_crop: CoverCropSpecies, 
        main_crop: str, 
        position: str, 
        compatibility_score: float
    ) -> List[str]:
        """Generate integration recommendations."""
        recommendations = []
        
        if compatibility_score > 0.8:
            recommendations.append(f"Excellent compatibility - proceed with confidence")
        elif compatibility_score > 0.6:
            recommendations.append(f"Good compatibility - monitor for specific challenges")
        else:
            recommendations.append(f"Moderate compatibility - consider alternatives")
        
        # Specific management recommendations
        if position == "before":
            recommendations.append(f"Plan termination 2-3 weeks before {main_crop} planting")
        
        if SoilBenefit.NITROGEN_FIXATION in cover_crop.primary_benefits:
            recommendations.append("Reduce nitrogen fertilizer rate for following crop")
            
        return recommendations
    
    def _get_compatibility_rating(self, score: float) -> str:
        """Convert compatibility score to rating."""
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Moderate"
        else:
            return "Poor"
    
    async def _get_rotation_plan(self, rotation_name: str) -> Optional[MainCropRotationPlan]:
        """Get rotation plan by name."""
        return self.rotation_database.get(rotation_name.lower().replace("-", "_"))
    
    async def _identify_integration_positions(self, rotation_plan: MainCropRotationPlan) -> List[Dict[str, Any]]:
        """Identify potential cover crop integration positions in rotation."""
        positions = []
        
        for i in range(len(rotation_plan.sequence)):
            current_crop = rotation_plan.sequence[i]
            next_crop = rotation_plan.sequence[(i + 1) % len(rotation_plan.sequence)]
            
            position = {
                "id": f"position_{i}_{i+1}",
                "description": f"Between {current_crop} and {next_crop}",
                "preceding_crop": current_crop,
                "following_crop": next_crop,
                "timing_constraints": {
                    "after_harvest": rotation_plan.harvest_windows.get(current_crop),
                    "before_planting": rotation_plan.typical_planting_dates.get(next_crop)
                }
            }
            positions.append(position)
        
        return positions
    
    async def _select_optimal_cover_crop(
        self, 
        position: Dict[str, Any], 
        available_cover_crops: List[CoverCropSpecies],
        objectives: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Select optimal cover crop for a specific position."""
        best_species = None
        best_score = 0.0
        
        for species in available_cover_crops:
            # Calculate compatibility with both preceding and following crop
            preceding_score = await self._calculate_compatibility_score(
                species, position["preceding_crop"], "after"
            )
            following_score = await self._calculate_compatibility_score(
                species, position["following_crop"], "before"
            )
            
            # Combined score
            combined_score = (preceding_score + following_score) / 2
            
            # Bonus for meeting objectives
            if objectives:
                objective_bonus = 0.0
                for objective in objectives:
                    if objective in [benefit.value for benefit in species.primary_benefits]:
                        objective_bonus += 0.1
                combined_score += objective_bonus
            
            if combined_score > best_score:
                best_score = combined_score
                best_species = species
        
        if best_species:
            return {
                "species": best_species,
                "compatibility_score": best_score,
                "timing": await self._calculate_optimal_timing(position, best_species),
                "management_notes": await self._generate_position_management_notes(position, best_species)
            }
        
        return None
    
    async def _calculate_optimal_timing(
        self, 
        position: Dict[str, Any], 
        species: CoverCropSpecies
    ) -> Dict[str, Any]:
        """Calculate optimal timing for cover crop in position."""
        return {
            "planting_window": "2-3 weeks after preceding crop harvest",
            "termination_window": "2-3 weeks before following crop planting",
            "growth_period_days": 90,  # Default growth period
            "critical_timing_factors": [
                "Allow time for establishment",
                "Ensure adequate termination time"
            ]
        }
    
    async def _generate_position_management_notes(
        self, 
        position: Dict[str, Any], 
        species: CoverCropSpecies
    ) -> List[str]:
        """Generate management notes for specific position."""
        notes = [
            f"Plant after {position['preceding_crop']} harvest",
            f"Terminate before {position['following_crop']} planting",
            f"Use {species.termination_methods[0]} for termination"
        ]
        
        if SoilBenefit.NITROGEN_FIXATION in species.primary_benefits:
            notes.append(f"Reduce N fertilizer for {position['following_crop']}")
            
        return notes
    
    # Additional helper methods for benefit calculations
    
    async def _calculate_nitrogen_cycling_benefits(
        self, 
        rotation_plan: MainCropRotationPlan, 
        cover_crop_positions: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate nitrogen cycling benefits by position."""
        nitrogen_benefits = {}
        
        for position in cover_crop_positions:
            # This would look up actual species data
            # For now, using default values
            nitrogen_benefits[position["position_id"]] = 50.0  # lbs N per acre
            
        return nitrogen_benefits
    
    async def _analyze_pest_management_benefits(
        self, 
        rotation_plan: MainCropRotationPlan, 
        cover_crop_positions: List[Dict[str, Any]]
    ) -> List[str]:
        """Analyze pest management benefits."""
        return [
            "Pest cycle disruption",
            "Beneficial insect habitat",
            "Reduced pest pressure on main crops"
        ]
    
    async def _analyze_soil_health_improvements(
        self, 
        rotation_plan: MainCropRotationPlan, 
        cover_crop_positions: List[Dict[str, Any]]
    ) -> List[str]:
        """Analyze soil health improvements."""
        return [
            "Increased organic matter",
            "Improved soil structure",
            "Enhanced nutrient cycling",
            "Reduced erosion"
        ]
    
    async def _calculate_economic_impact(
        self, 
        rotation_plan: MainCropRotationPlan, 
        cover_crop_positions: List[Dict[str, Any]]
    ) -> Tuple[float, float]:
        """Calculate economic impact (cost, benefit value)."""
        cost_per_position = 50.0  # Average cost per acre
        benefit_per_position = 75.0  # Average benefit per acre
        
        total_cost = len(cover_crop_positions) * cost_per_position
        total_benefit = len(cover_crop_positions) * benefit_per_position
        
        return total_cost, total_benefit
    
    async def _identify_integration_risks_overall(
        self, 
        rotation_plan: MainCropRotationPlan, 
        cover_crop_positions: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify overall integration risks."""
        risks = []
        
        if len(cover_crop_positions) > 2:
            risks.append("Complex management with multiple cover crop positions")
        
        if rotation_plan.complexity_level == "complex":
            risks.append("Additional complexity on already complex rotation")
            
        return risks
    
    # Additional benefit analysis methods
    
    async def _calculate_nitrogen_fixation_value(self, integration_plan: CoverCropRotationIntegration) -> float:
        """Calculate nitrogen fixation value."""
        total_value = 0.0
        nitrogen_price = 0.50  # $ per lb N
        
        for position_id, n_value in integration_plan.nitrogen_cycling_benefits.items():
            total_value += n_value * nitrogen_price
            
        return total_value
    
    async def _calculate_erosion_prevention_value(self, integration_plan: CoverCropRotationIntegration) -> float:
        """Calculate erosion prevention value."""
        return 25.0 * len(integration_plan.cover_crop_positions)  # $25 per position
    
    async def _calculate_organic_matter_improvement(self, integration_plan: CoverCropRotationIntegration) -> float:
        """Calculate organic matter improvement percentage."""
        return 0.1 * len(integration_plan.cover_crop_positions)  # 0.1% per position
    
    async def _calculate_weed_suppression_value(self, integration_plan: CoverCropRotationIntegration) -> float:
        """Calculate weed suppression value."""
        return 15.0 * len(integration_plan.cover_crop_positions)  # $15 per position
    
    async def _analyze_pest_pressure_reduction(self, integration_plan: CoverCropRotationIntegration) -> Dict[str, float]:
        """Analyze pest pressure reduction."""
        return {
            "corn_rootworm": 0.3,  # 30% reduction
            "soybean_cyst_nematode": 0.25,  # 25% reduction
            "general_pest_pressure": 0.2  # 20% general reduction
        }
    
    async def _analyze_disease_break_effectiveness(self, integration_plan: CoverCropRotationIntegration) -> Dict[str, float]:
        """Analyze disease break effectiveness."""
        return {
            "soilborne_diseases": 0.4,  # 40% effectiveness
            "residue_borne_diseases": 0.3,  # 30% effectiveness
            "foliar_diseases": 0.2  # 20% effectiveness
        }
    
    async def _calculate_beneficial_insect_support(self, integration_plan: CoverCropRotationIntegration) -> float:
        """Calculate beneficial insect support score."""
        return 0.7  # 70% support score
    
    async def _project_soil_health_trajectory(self, integration_plan: CoverCropRotationIntegration) -> Dict[str, float]:
        """Project soil health trajectory."""
        return {
            "year_1": 0.05,  # 5% improvement
            "year_3": 0.15,  # 15% improvement
            "year_5": 0.25   # 25% improvement
        }
    
    async def _project_yield_impacts(self, integration_plan: CoverCropRotationIntegration) -> Dict[str, float]:
        """Project yield impacts by crop."""
        yield_impacts = {}
        
        for crop in integration_plan.rotation_plan.sequence:
            yield_impacts[crop] = 0.03  # 3% yield increase
            
        return yield_impacts
    
    async def _identify_sustainability_improvements(self, integration_plan: CoverCropRotationIntegration) -> List[str]:
        """Identify sustainability improvements."""
        return [
            "Reduced synthetic fertilizer dependence",
            "Improved soil carbon sequestration", 
            "Enhanced biodiversity",
            "Reduced environmental impact"
        ]
    
    async def _assess_implementation_risks(self, integration_plan: CoverCropRotationIntegration) -> List[str]:
        """Assess implementation risks."""
        return [
            "Weather-dependent establishment",
            "Timing coordination challenges",
            "Additional management complexity"
        ]
    
    async def _develop_mitigation_strategies(self, risks: List[str]) -> List[str]:
        """Develop risk mitigation strategies."""
        strategies = []
        
        for risk in risks:
            if "weather" in risk.lower():
                strategies.append("Have backup planting dates and methods")
            elif "timing" in risk.lower():
                strategies.append("Plan detailed timing calendar with buffer periods")
            elif "management" in risk.lower():
                strategies.append("Start with simple integration and add complexity gradually")
        
        return strategies
    
    async def _calculate_analysis_confidence(
        self, 
        integration_plan: CoverCropRotationIntegration, 
        field_conditions: Dict[str, Any] = None
    ) -> float:
        """Calculate analysis confidence level."""
        base_confidence = 0.7
        
        # Increase confidence with more data
        if field_conditions:
            base_confidence += 0.1
            
        # Increase confidence with simpler rotations
        if integration_plan.rotation_plan.complexity_level == "simple":
            base_confidence += 0.1
        
        return min(0.95, base_confidence)
    
    def _parse_date_range(self, date_string: str) -> Optional[date]:
        """Parse date string to date object."""
        # Simple parser for "Month Day" format
        try:
            if not date_string:
                return None
                
            parts = date_string.split()
            if len(parts) == 2:
                month_name, day = parts
                month_map = {
                    "January": 1, "February": 2, "March": 3, "April": 4,
                    "May": 5, "June": 6, "July": 7, "August": 8,
                    "September": 9, "October": 10, "November": 11, "December": 12
                }
                
                month = month_map.get(month_name)
                if month:
                    return date(2024, month, int(day))  # Use current year or appropriate year
                    
        except Exception:
            pass
            
        return None