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
        ClimateData,
        MainCropRotationPlan,
        CoverCropRotationIntegration,
        CropTimingWindow,
        RotationBenefitAnalysis,
        GoalBasedObjectives,
        GoalBasedRecommendation
    )
    from .main_crop_integration_service import MainCropIntegrationService
    from .goal_based_recommendation_service import GoalBasedRecommendationService
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
        ClimateData,
        MainCropRotationPlan,
        CoverCropRotationIntegration,
        CropTimingWindow,
        RotationBenefitAnalysis,
        GoalBasedObjectives,
        GoalBasedRecommendation
    )
    from services.main_crop_integration_service import MainCropIntegrationService
    from services.goal_based_recommendation_service import GoalBasedRecommendationService

logger = logging.getLogger(__name__)


class CoverCropSelectionService:
    """Service for cover crop selection and recommendations."""
    
    def __init__(self):
        """Initialize the cover crop selection service."""
        self.species_database = {}
        self.mixture_database = {}
        self.climate_service_url = "http://localhost:8003"  # Data integration service
        self.main_crop_integration_service = MainCropIntegrationService()
        self.goal_based_service = GoalBasedRecommendationService()
        self.initialized = False
        
    async def initialize(self):
        """Initialize the service with cover crop data."""
        try:
            await self._load_cover_crop_database()
            await self._load_mixture_database()
            await self.main_crop_integration_service.initialize()
            self.initialized = True
            logger.info("Cover Crop Selection Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Cover Crop Selection Service: {e}")
            raise
            
    async def cleanup(self):
        """Clean up service resources."""
        await self.main_crop_integration_service.cleanup()
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
    async def _generate_rotation_specific_recommendations(
        self, 
        integration_plan: Any, 
        request: CoverCropSelectionRequest
    ) -> List[CoverCropRecommendation]:
        """Generate cover crop recommendations optimized for rotation integration."""
        try:
            recommendations = []
            
            # Get suitable species from integration plan - handle both dict and Pydantic model
            if hasattr(integration_plan, 'cover_crop_positions'):
                # Pydantic model
                positions = integration_plan.cover_crop_positions
            else:
                # Dictionary fallback
                positions = integration_plan.get("integrations", [])
            
            for integration in positions:
                if isinstance(integration, dict):
                    # Try both field names for compatibility
                    species_id = integration.get("cover_crop_species_id") or integration.get("recommended_species")
                else:
                    species_id = getattr(integration, 'cover_crop_species_id', None) or getattr(integration, 'recommended_species', None)
                
                species = self.species_database.get(species_id) if species_id else None
                
                if species:
                    # Calculate rotation-specific score
                    score = await self._calculate_rotation_specific_score(species, integration_plan, request)
                    
                    # Create recommendation with rotation context
                    recommendation = await self._create_rotation_recommendation(
                        species, score, integration, request
                    )
                    recommendations.append(recommendation)
            
            # Sort by suitability score
            recommendations.sort(key=lambda x: x.suitability_score, reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating rotation-specific recommendations: {e}")
            # Fallback to standard recommendations
            suitable_species = await self._find_suitable_species(request)
            scored_species = await self._score_species_suitability(suitable_species, request)
            return await self._generate_species_recommendations(scored_species, request)
    
    async def _analyze_field_conditions_with_rotation(
        self, 
        request: CoverCropSelectionRequest, 
        integration_plan: 'CoverCropRotationIntegration'
    ) -> Dict[str, Any]:
        """Analyze field conditions with rotation context."""
        # Start with base field analysis
        base_analysis = await self._analyze_field_conditions(request)
        
        # Add rotation-specific considerations
        rotation_considerations = {
            "rotation_benefits": [],
            "rotation_challenges": [],
            "rotation_recommendations": []
        }
        
        # Analyze rotation system impact - access Pydantic model attributes correctly
        rotation_name = integration_plan.rotation_plan.rotation_name if integration_plan.rotation_plan else "Unknown"
        main_crops = integration_plan.rotation_plan.sequence if integration_plan.rotation_plan else []
        
        if main_crops:
            rotation_considerations["rotation_benefits"].append(
                f"Integration with {', '.join(main_crops)} rotation system"
            )
            
            # Check for complementary relationships
            for crop in main_crops:
                if crop.lower() in ["corn", "soybean", "wheat"]:
                    rotation_considerations["rotation_benefits"].append(
                        f"Complementary relationship with {crop} for nutrient cycling"
                    )
        
        # Add timing considerations based on cover crop positions
        if integration_plan.cover_crop_positions:
            rotation_considerations["rotation_recommendations"].append(
                "Timing windows optimized for rotation sequence"
            )
        
        # Merge with base analysis
        base_analysis.update(rotation_considerations)
        
        return base_analysis
    
    async def _create_rotation_integration_timeline(
        self, 
        request: CoverCropSelectionRequest, 
        integration_plan: Any
    ) -> List[Dict[str, Any]]:
        """Create timeline with rotation integration context."""
        base_timeline = await self._create_implementation_timeline(request)
        
        # Add rotation-specific phases
        rotation_phases = []
        
        # Pre-integration planning
        rotation_phases.append({
            "phase": "Rotation Planning",
            "date_range": "2-4 weeks before planting",
            "tasks": [
                "Review rotation schedule and main crop plans",
                "Coordinate with main crop planting timeline",
                "Verify termination timing for next main crop"
            ]
        })
        
        # Integration monitoring
        rotation_phases.append({
            "phase": "Integration Monitoring",
            "date_range": "Throughout growing season",
            "tasks": [
                "Monitor cover crop performance within rotation context",
                "Assess impact on subsequent main crop preparation",
                "Document rotation benefits and challenges"
            ]
        })
        
        # Transition planning
        rotation_phases.append({
            "phase": "Transition Planning",
            "date_range": "4-6 weeks before termination",
            "tasks": [
                "Plan termination timing for optimal main crop planting",
                "Coordinate with main crop seeding schedule",
                "Prepare equipment for rotation transition"
            ]
        })
        
        # Combine timelines
        combined_timeline = base_timeline + rotation_phases
        
        return combined_timeline
    
    async def _generate_rotation_mixtures(self, integration_plan: Any) -> List[CoverCropMixture]:
        """Generate cover crop mixtures optimized for rotation integration."""
        mixtures = []
        
        try:
            # Get species from integration plan - handle both dict and Pydantic model
            recommended_species = []
            if hasattr(integration_plan, 'cover_crop_positions'):
                # Pydantic model
                positions = integration_plan.cover_crop_positions
            else:
                # Dictionary fallback
                positions = integration_plan.get("integrations", [])
            
            for integration in positions:
                if isinstance(integration, dict):
                    # Try both field names for compatibility
                    species_id = integration.get("cover_crop_species_id") or integration.get("recommended_species")
                else:
                    species_id = getattr(integration, 'cover_crop_species_id', None) or getattr(integration, 'recommended_species', None)
                
                species = self.species_database.get(species_id) if species_id else None
                if species:
                    recommended_species.append(species)
            
            # Create rotation-optimized mixtures
            if len(recommended_species) >= 2:
                # Create complementary mixtures
                legume_species = [s for s in recommended_species if s.cover_crop_type == CoverCropType.LEGUME]
                grass_species = [s for s in recommended_species if s.cover_crop_type == CoverCropType.GRASS]
                brassica_species = [s for s in recommended_species if s.cover_crop_type == CoverCropType.BRASSICA]
                
                # Legume-Grass mixture
                if legume_species and grass_species:
                    mixture = await self._create_rotation_mixture(
                        "Rotation N-Fixer Blend",
                        [legume_species[0], grass_species[0]],
                        integration_plan
                    )
                    mixtures.append(mixture)
                
                # Three-way mixture if brassica available
                if legume_species and grass_species and brassica_species:
                    mixture = await self._create_rotation_mixture(
                        "Complete Rotation Blend",
                        [legume_species[0], grass_species[0], brassica_species[0]],
                        integration_plan
                    )
                    mixtures.append(mixture)
            
            return mixtures[:3]  # Return top 3 mixtures
            
        except Exception as e:
            logger.error(f"Error generating rotation mixtures: {e}")
            return []
    
    async def _get_rotation_seasonal_considerations(
        self, 
        request: CoverCropSelectionRequest, 
        integration_plan: 'CoverCropRotationIntegration'
    ) -> List[str]:
        """Get seasonal considerations with rotation context."""
        base_considerations = await self._get_seasonal_considerations(request)
        
        rotation_considerations = [
            "Coordinate planting timing with main crop harvest schedule",
            "Plan termination timing to optimize main crop planting window",
            "Consider rotation sequence impacts on soil conditions"
        ]
        
        # Add main crop specific considerations - access Pydantic model correctly
        main_crops = integration_plan.rotation_plan.sequence if integration_plan.rotation_plan else []
        for crop in main_crops:
            if crop.lower() == "corn":
                rotation_considerations.append(
                    "Ensure adequate nitrogen fixation for corn nitrogen needs"
                )
            elif crop.lower() == "soybean":
                rotation_considerations.append(
                    "Focus on soil structure improvement for soybean root development"
                )
        
        return base_considerations + rotation_considerations
    
    async def _get_rotation_monitoring_recommendations(self, integration_plan: Any) -> List[str]:
        """Get monitoring recommendations specific to rotation integration."""
        return [
            "Monitor cover crop establishment within rotation timeline",
            "Assess cover crop termination effectiveness for main crop planting",
            "Evaluate rotation system benefits (yield, soil health, economics)",
            "Document cover crop impact on subsequent main crop performance",
            "Track rotation sequence success metrics over time"
        ]
    
    async def _get_rotation_follow_up_actions(self, integration_plan: Any) -> List[str]:
        """Get follow-up actions specific to rotation integration."""
        return [
            "Evaluate rotation integration success after main crop harvest",
            "Adjust rotation timing based on cover crop performance",
            "Plan next rotation cycle improvements",
            "Document lessons learned for rotation optimization",
            "Consider economic analysis of rotation system benefits"
        ]
    
    async def _calculate_rotation_confidence(
        self, 
        recommendations: List[CoverCropRecommendation], 
        integration_plan: 'CoverCropRotationIntegration'
    ) -> float:
        """Calculate confidence specific to rotation integration."""
        if not recommendations:
            return 0.5
        
        # Base confidence on top recommendation
        base_confidence = recommendations[0].confidence_level
        
        # Adjust for rotation integration factors - handle both dict and Pydantic model
        # Calculate integration quality based on compatibility scores
        if isinstance(integration_plan, dict):
            # Dictionary input (from tests)
            compatibility_scores = integration_plan.get("compatibility_scores", {})
            rotation_plan_exists = integration_plan.get("rotation_plan") is not None
        else:
            # Pydantic model input
            compatibility_scores = getattr(integration_plan, 'compatibility_scores', {})
            rotation_plan_exists = getattr(integration_plan, 'rotation_plan', None) is not None
        
        if compatibility_scores:
            integration_quality = sum(compatibility_scores.values()) / len(compatibility_scores)
        else:
            integration_quality = 0.7
            
        # Estimate timing compatibility based on rotation structure
        timing_compatibility = 0.9 if rotation_plan_exists else 0.7
        
        # Calculate weighted confidence
        rotation_confidence = (base_confidence * 0.5 + 
                             integration_quality * 0.3 + 
                             timing_compatibility * 0.2)
        
        return min(0.95, max(0.5, rotation_confidence))
    
    async def _generate_species_specific_recommendations(
        self, 
        species: CoverCropSpecies, 
        main_crop: str, 
        position: str
    ) -> List[str]:
        """Generate species-specific recommendations for main crop compatibility."""
        recommendations = []
        
        # Position-specific recommendations
        if position == "before":
            recommendations.append(
                f"Plant {species.common_name} after {main_crop} harvest with adequate termination timing"
            )
        elif position == "after":
            recommendations.append(
                f"Use {species.common_name} to prepare soil conditions for {main_crop}"
            )
        
        # Species-specific benefits
        if species.cover_crop_type == CoverCropType.LEGUME:
            recommendations.append(f"Nitrogen fixation will benefit subsequent {main_crop} nitrogen needs")
        
        if SoilBenefit.COMPACTION_RELIEF in species.primary_benefits:
            recommendations.append(f"Deep rooting will improve soil structure for {main_crop} root development")
        
        # Main crop specific recommendations
        if main_crop.lower() == "corn":
            recommendations.append("Ensure adequate nitrogen contribution for corn production")
        elif main_crop.lower() == "soybean":
            recommendations.append("Focus on soil structure and water infiltration improvements")
        
        return recommendations
    
    async def _analyze_compatibility_economics(
        self, 
        species: CoverCropSpecies, 
        main_crop: str, 
        position: str
    ) -> Dict[str, Any]:
        """Analyze economic aspects of cover crop-main crop compatibility."""
        economic_analysis = {
            "establishment_cost": species.establishment_cost_per_acre or 0,
            "expected_benefits": {},
            "roi_estimate": None,
            "payback_period": None
        }
        
        # Calculate main crop specific benefits
        if main_crop.lower() == "corn" and species.nitrogen_fixation_lbs_acre:
            nitrogen_value = species.nitrogen_fixation_lbs_acre * 0.50  # $0.50/lb N
            economic_analysis["expected_benefits"]["nitrogen_value"] = nitrogen_value
        
        # Soil improvement benefits
        if SoilBenefit.EROSION_CONTROL in species.primary_benefits:
            economic_analysis["expected_benefits"]["erosion_prevention"] = 25.0
        
        # Calculate ROI
        total_benefits = sum(economic_analysis["expected_benefits"].values())
        if total_benefits > 0 and economic_analysis["establishment_cost"] > 0:
            roi = ((total_benefits - economic_analysis["establishment_cost"]) / 
                   economic_analysis["establishment_cost"]) * 100
            economic_analysis["roi_estimate"] = max(0, roi)
            
            if roi > 0:
                economic_analysis["payback_period"] = "1-2 years"
        
        return economic_analysis
    
    async def _filter_recommendations_by_position(
        self, 
        integration_plan: Any, 
        position_id: str, 
        request: CoverCropSelectionRequest
    ) -> List[CoverCropRecommendation]:
        """Filter recommendations for specific rotation position."""
        try:
            # Find position-specific integrations - handle both dict and Pydantic model
            position_integrations = []
            if hasattr(integration_plan, 'cover_crop_positions'):
                # Pydantic model
                positions = integration_plan.cover_crop_positions
            else:
                # Dictionary fallback
                positions = integration_plan.get("integrations", [])
            
            for integration in positions:
                position_matches = False
                
                if isinstance(integration, dict):
                    # Check direct position ID/name match
                    if integration.get("position_id") == position_id or integration.get("position") == position_id:
                        position_matches = True
                    # Check semantic matching (e.g., "before_corn" matches following_crop="corn")
                    elif position_id.startswith("before_") and integration.get("following_crop"):
                        target_crop = position_id.replace("before_", "")
                        if integration.get("following_crop").lower() == target_crop.lower():
                            position_matches = True
                    # Check semantic matching (e.g., "after_corn" matches preceding_crop="corn")
                    elif position_id.startswith("after_") and integration.get("preceding_crop"):
                        target_crop = position_id.replace("after_", "")
                        if integration.get("preceding_crop").lower() == target_crop.lower():
                            position_matches = True
                else:
                    # For Pydantic models, check both attribute names
                    if (getattr(integration, 'position_id', None) == position_id or 
                        getattr(integration, 'position', None) == position_id):
                        position_matches = True
                    # Check semantic matching for Pydantic models
                    elif position_id.startswith("before_") and hasattr(integration, 'following_crop'):
                        target_crop = position_id.replace("before_", "")
                        if getattr(integration, 'following_crop', '').lower() == target_crop.lower():
                            position_matches = True
                    elif position_id.startswith("after_") and hasattr(integration, 'preceding_crop'):
                        target_crop = position_id.replace("after_", "")
                        if getattr(integration, 'preceding_crop', '').lower() == target_crop.lower():
                            position_matches = True
                
                if position_matches:
                    position_integrations.append(integration)
            
            # Generate recommendations for position
            recommendations = []
            for integration in position_integrations:
                if isinstance(integration, dict):
                    # Try both field names for compatibility
                    species_id = integration.get("cover_crop_species_id") or integration.get("recommended_species")
                else:
                    species_id = getattr(integration, 'cover_crop_species_id', None) or getattr(integration, 'recommended_species', None)
                
                species = self.species_database.get(species_id) if species_id else None
                
                if species:
                    score = await self._calculate_position_specific_score(
                        species, integration, request
                    )
                    
                    recommendation = await self._create_position_recommendation(
                        species, score, integration, request
                    )
                    recommendations.append(recommendation)
            
            # Sort by score
            recommendations.sort(key=lambda x: x.suitability_score, reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error filtering recommendations by position: {e}")
            # Fallback to general recommendations
            suitable_species = await self._find_suitable_species(request)
            scored_species = await self._score_species_suitability(suitable_species, request)
            return await self._generate_species_recommendations(scored_species, request)
    
    async def _analyze_specific_position(
        self, 
        integration_plan: 'CoverCropRotationIntegration', 
        position_id: str
    ) -> Dict[str, Any]:
        """Analyze specific position in rotation for cover crop suitability."""
        position_analysis = {
            "position_id": position_id,
            "position_characteristics": {},
            "suitability_factors": [],
            "challenges": [],
            "opportunities": []
        }
        
        # Find position details in integration plan - access Pydantic model correctly
        if hasattr(integration_plan, 'cover_crop_positions'):
            positions = integration_plan.cover_crop_positions
        elif isinstance(integration_plan, dict):
            positions = integration_plan.get("cover_crop_positions", [])
        else:
            positions = []
            
        for position in positions:
            position_match = False
            if isinstance(position, dict):
                position_match = position.get("position") == position_id
                if position_match:
                    position_analysis["position_characteristics"] = {
                        "position": position.get("position"),
                        "cover_crop_species_id": position.get("cover_crop_species_id") or position.get("recommended_species"),
                        "expected_benefits": position.get("expected_benefits", [])
                    }
            else:
                position_match = getattr(position, 'position', None) == position_id
                if position_match:
                    position_analysis["position_characteristics"] = {
                        "position": getattr(position, 'position', position_id),
                        "cover_crop_species_id": getattr(position, 'cover_crop_species_id', None) or getattr(position, 'recommended_species', None),
                        "expected_benefits": getattr(position, 'expected_benefits', [])
                    }
            
            if position_match:
                break
        
        # Analyze position characteristics based on rotation sequence
        if integration_plan.rotation_plan and integration_plan.rotation_plan.sequence:
            sequence = integration_plan.rotation_plan.sequence
            position_analysis["suitability_factors"].append(
                f"Integrated with {' -> '.join(sequence)} rotation sequence"
            )
            
            # Add crop-specific opportunities
            for crop in sequence:
                if crop.lower() in ["corn", "soybean", "wheat"]:
                    position_analysis["opportunities"].append(
                        f"Can enhance soil conditions for {crop} production"
                    )
        
        return position_analysis
    
    async def _generate_position_mixtures(
        self, 
        integration_plan: Any, 
        position_id: str
    ) -> List[CoverCropMixture]:
        """Generate mixtures optimized for specific rotation position."""
        try:
            # Get position-specific species - handle both dict and Pydantic model
            position_species = []
            if hasattr(integration_plan, 'cover_crop_positions'):
                # Pydantic model
                positions = integration_plan.cover_crop_positions
            else:
                # Dictionary fallback
                positions = integration_plan.get("integrations", [])
            
            for integration in positions:
                position_matches = False
                species_id = None
                
                if isinstance(integration, dict):
                    if integration.get("position_id") == position_id:
                        position_matches = True
                        # Try both field names for compatibility
                        species_id = integration.get("cover_crop_species_id") or integration.get("recommended_species")
                else:
                    if getattr(integration, 'position_id', None) == position_id:
                        position_matches = True
                        species_id = getattr(integration, 'cover_crop_species_id', None) or getattr(integration, 'recommended_species', None)
                
                if position_matches and species_id:
                    species = self.species_database.get(species_id)
                    if species:
                        position_species.append(species)
            
            # Create position-optimized mixtures
            mixtures = []
            if len(position_species) >= 2:
                mixture = await self._create_position_mixture(
                    f"Position {position_id} Blend",
                    position_species[:3],  # Up to 3 species
                    integration_plan,
                    position_id
                )
                mixtures.append(mixture)
            
            return mixtures
            
        except Exception as e:
            logger.error(f"Error generating position mixtures: {e}")
            return []
    
    async def _get_position_seasonal_considerations(
        self, 
        integration_plan: 'CoverCropRotationIntegration', 
        position_id: str
    ) -> List[str]:
        """Get seasonal considerations for specific rotation position."""
        considerations = [
            f"Position {position_id} timing within rotation sequence",
            "Coordinate with preceding and following crop schedules",
            "Optimize termination timing for next rotation phase"
        ]
        
        # Add position-specific timing considerations - access Pydantic model correctly
        for position in integration_plan.cover_crop_positions:
            position_match = False
            if isinstance(position, dict):
                position_match = position.get("position") == position_id
            else:
                position_match = getattr(position, 'position', None) == position_id
            
            if position_match:
                # Add timing recommendations based on position
                considerations.append(
                    f"Timing optimized for {position_id} position in rotation"
                )
                if position.get("expected_benefits"):
                    benefits = ", ".join(position.get("expected_benefits", []))
                    considerations.append(f"Focus on {benefits} for optimal timing")
                break
        
        return considerations
    
    async def _create_position_timeline(
        self, 
        integration_plan: 'CoverCropRotationIntegration', 
        position_id: str
    ) -> List[Dict[str, Any]]:
        """Create timeline for specific rotation position."""
        timeline = []
        
        # Find position timing - access Pydantic model correctly
        position_found = False
        for position in integration_plan.cover_crop_positions:
            position_match = False
            if isinstance(position, dict):
                position_match = position.get("position") == position_id
            else:
                position_match = getattr(position, 'position', None) == position_id
            
            if position_match:
                position_found = True
                break
        
        if position_found:
            # Use default dates based on rotation plan or current date
            planting_date = date.today()
            termination_date = date.today() + timedelta(days=120)
            
            # Try to get better dates from rotation plan if available
            if integration_plan.rotation_plan and integration_plan.rotation_plan.typical_planting_dates:
                # Use first crop's planting as reference
                first_crop = next(iter(integration_plan.rotation_plan.typical_planting_dates.keys()), None)
                if first_crop:
                    planting_info = integration_plan.rotation_plan.typical_planting_dates[first_crop]
                    try:
                        if isinstance(planting_info, dict):
                            start_date = planting_info.get("start", date.today().isoformat())
                        else:
                            start_date = getattr(planting_info, 'start', date.today().isoformat())
                        planting_date = date.fromisoformat(start_date)
                    except (ValueError, AttributeError):
                        pass
            
            timeline = [
                {
                    "phase": f"Position {position_id} Preparation",
                    "date_range": f"{planting_date - timedelta(days=14)} to {planting_date}",
                    "tasks": ["Position-specific soil preparation", "Rotation sequence coordination"]
                },
                {
                    "phase": f"Position {position_id} Management",
                    "date_range": f"{planting_date} to {termination_date - timedelta(days=14)}",
                    "tasks": ["Monitor position-specific objectives", "Assess rotation benefits"]
                },
                {
                    "phase": f"Position {position_id} Transition",
                    "date_range": f"{termination_date - timedelta(days=14)} to {termination_date}",
                    "tasks": ["Plan termination for next rotation phase", "Prepare for rotation transition"]
                }
            ]
        
        return timeline
    
    async def _get_position_monitoring_recommendations(
        self, 
        integration_plan: Any, 
        position_id: str
    ) -> List[str]:
        """Get monitoring recommendations for specific rotation position."""
        return [
            f"Monitor position {position_id} specific objectives",
            "Track rotation sequence performance metrics",
            "Assess position impact on overall rotation success",
            "Document position-specific lessons learned"
        ]
    
    async def _get_position_follow_up_actions(
        self, 
        integration_plan: Any, 
        position_id: str
    ) -> List[str]:
        """Get follow-up actions for specific rotation position."""
        return [
            f"Evaluate position {position_id} performance in rotation context",
            "Plan adjustments for next rotation cycle",
            "Document position-specific best practices",
            "Consider position optimization opportunities"
        ]
    
    # Additional helper methods for rotation integration
    async def _calculate_rotation_specific_score(
        self, 
        species: CoverCropSpecies, 
        integration_plan: Any, 
        request: CoverCropSelectionRequest
    ) -> float:
        """Calculate species score specific to rotation integration."""
        base_score = await self._calculate_species_score(species, request)
        
        # Add rotation-specific scoring
        rotation_bonus = 0.0
        
        # Check rotation compatibility
        # Handle both dict and Pydantic model
        if hasattr(integration_plan, 'main_crops'):
            main_crops = integration_plan.main_crops if integration_plan.main_crops else []
        elif isinstance(integration_plan, dict):
            main_crops = integration_plan.get("main_crops", [])
        else:
            main_crops = []
        
        for crop in main_crops:
            if crop.lower() in [c.lower() for c in species.cash_crop_compatibility]:
                rotation_bonus += 0.1
        
        # Timing compatibility bonus
        if hasattr(integration_plan, 'timing_compatibility'):
            timing_compatibility = getattr(integration_plan, 'timing_compatibility', 0)
        elif isinstance(integration_plan, dict):
            timing_compatibility = integration_plan.get("timing_compatibility", 0)
        else:
            timing_compatibility = 0
        
        if timing_compatibility > 0.8:
            rotation_bonus += 0.05
        
        return min(1.0, base_score + rotation_bonus)
    
    async def _create_rotation_recommendation(
        self, 
        species: CoverCropSpecies, 
        score: float, 
        integration: Any, 
        request: CoverCropSelectionRequest
    ) -> CoverCropRecommendation:
        """Create recommendation with rotation integration context."""
        # Get base recommendation
        base_recs = await self._generate_species_recommendations([(species, score)], request)
        
        if base_recs:
            recommendation = base_recs[0]
            
            # Add rotation-specific context
            # Handle both dict and Pydantic model
            if isinstance(integration, dict):
                rotation_benefits = integration.get("expected_benefits", [])
                rotation_name = integration.get('rotation_name', 'rotation')
                position = integration.get('position', 'rotation')
            else:
                rotation_benefits = getattr(integration, "expected_benefits", [])
                rotation_name = getattr(integration, 'rotation_name', 'rotation')
                position = getattr(integration, 'position', 'rotation')
            
            recommendation.expected_benefits.extend(rotation_benefits)
            
            # Add rotation-specific management notes
            rotation_notes = [
                f"Integrated with {rotation_name} system",
                f"Optimized for {position} position timing"
            ]
            recommendation.management_notes.extend(rotation_notes)
            
            return recommendation
        
        # Fallback recommendation
        # Handle seeding rate safely
        drilled_rate = 0
        if hasattr(species.seeding_rate_lbs_acre, 'get'):
            drilled_rate = species.seeding_rate_lbs_acre.get("drilled", 0)
        elif isinstance(species.seeding_rate_lbs_acre, dict):
            drilled_rate = species.seeding_rate_lbs_acre.get("drilled", 0)
        
        # Handle planting date safely
        planting_date = date.today()
        if hasattr(request.planting_window, 'get'):
            planting_date = request.planting_window.get("start", date.today())
        elif isinstance(request.planting_window, dict):
            planting_date = request.planting_window.get("start", date.today())
        elif hasattr(request.planting_window, 'start'):
            planting_date = request.planting_window.start
        
        return CoverCropRecommendation(
            species=species,
            suitability_score=score,
            confidence_level=score * 0.9,
            seeding_rate_recommendation=drilled_rate,
            planting_date_recommendation=planting_date,
            termination_recommendation=species.termination_methods[0] if species.termination_methods else "herbicide",
            expected_benefits=["Rotation integration with system"],
            management_notes=["Rotation-optimized management"],
            success_indicators=["Integration success with rotation system"]
        )
    
    async def _calculate_position_specific_score(
        self, 
        species: CoverCropSpecies, 
        integration: Any, 
        request: CoverCropSelectionRequest
    ) -> float:
        """Calculate score for specific rotation position."""
        base_score = await self._calculate_species_score(species, request)
        
        # Position-specific adjustments
        position_score = base_score
        
        # Check position suitability - handle both dict and Pydantic model
        if isinstance(integration, dict):
            position_details = integration.get("position_details", {})
            soil_conditions_match = position_details.get("soil_conditions_match", True)
            timing_optimal = position_details.get("timing_optimal", True)
        else:
            position_details = getattr(integration, "position_details", {})
            soil_conditions_match = position_details.get("soil_conditions_match", True) if isinstance(position_details, dict) else True
            timing_optimal = position_details.get("timing_optimal", True) if isinstance(position_details, dict) else True
        
        if soil_conditions_match:
            position_score += 0.05
        
        if timing_optimal:
            position_score += 0.05
        
        return min(1.0, position_score)
    
    async def _create_position_recommendation(
        self, 
        species: CoverCropSpecies, 
        score: float, 
        integration: Any, 
        request: CoverCropSelectionRequest
    ) -> CoverCropRecommendation:
        """Create recommendation for specific rotation position."""
        # Create base recommendation
        recommendation = await self._create_rotation_recommendation(
            species, score, integration, request
        )
        
        # Add position-specific details - handle both dict and Pydantic model
        if isinstance(integration, dict):
            position_id = integration.get("position_id", "unknown")
        else:
            position_id = getattr(integration, "position_id", "unknown")
        position_notes = [
            f"Optimized for rotation position {position_id}",
            f"Position-specific timing and management"
        ]
        
        recommendation.management_notes.extend(position_notes)
        
        return recommendation
    
    async def _create_rotation_mixture(
        self, 
        mixture_name: str, 
        species_list: List[CoverCropSpecies], 
        integration_plan: Any
    ) -> CoverCropMixture:
        """Create cover crop mixture optimized for rotation."""
        # Calculate seeding rates for mixture
        mixture_species = []
        total_rate = 0
        
        for species in species_list:
            # Adjust rate for mixture (typically 60-70% of single species rate)
            single_rate = species.seeding_rate_lbs_acre.get("drilled", 
                species.seeding_rate_lbs_acre.get("broadcast", 0))
            mixture_rate = single_rate * 0.65  # 65% of single species rate
            
            mixture_species.append({
                "species_id": species.species_id,
                "name": species.common_name,
                "rate_lbs_acre": mixture_rate
            })
            total_rate += mixture_rate
        
        # Create mixture benefits
        mixture_benefits = []
        for species in species_list:
            for benefit in species.primary_benefits:
                benefit_text = benefit.value.replace("_", " ").title()
                if benefit_text not in mixture_benefits:
                    mixture_benefits.append(benefit_text)
        
        # Add rotation-specific benefits - handle both dict and Pydantic model
        if isinstance(integration_plan, dict):
            rotation_name = integration_plan.get("rotation_name", "rotation")
        else:
            rotation_name = getattr(integration_plan, "rotation_name", "rotation")
        mixture_benefits.append(f"Optimized for {rotation_name} system integration")
        
        return CoverCropMixture(
            mixture_id=f"rot_{mixture_name.lower().replace(' ', '_')}",
            mixture_name=mixture_name,
            species_list=mixture_species,
            total_seeding_rate=total_rate,
            mixture_benefits=mixture_benefits,
            complexity_level="moderate"
        )
    
    async def _create_position_mixture(
        self, 
        mixture_name: str, 
        species_list: List[CoverCropSpecies], 
        integration_plan: Any,
        position_id: str
    ) -> CoverCropMixture:
        """Create mixture optimized for specific rotation position."""
        # Create base rotation mixture
        mixture = await self._create_rotation_mixture(
            mixture_name, species_list, integration_plan
        )
        
        # Add position-specific adjustments
        mixture.mixture_id = f"pos_{position_id}_{mixture.mixture_id}"
        mixture.mixture_name = f"{mixture_name} (Position {position_id})"
        mixture.mixture_benefits.append(f"Position {position_id} optimization")
        
        return mixture
    
    async def get_rotation_integration_recommendations(
        self,
        rotation_name: str,
        request: CoverCropSelectionRequest,
        objectives: List[str] = None
    ) -> CoverCropSelectionResponse:
        """
        Get cover crop recommendations for specific rotation integration.
        
        Args:
            rotation_name: Name of the rotation system
            request: Cover crop selection request
            objectives: Specific integration objectives
            
        Returns:
            Cover crop selection response optimized for rotation integration
        """
        try:
            logger.info(f"Processing rotation integration request for: {rotation_name}")
            
            # Get suitable species first
            suitable_species = await self._find_suitable_species(request)
            
            # Create rotation integration plan
            integration_plan = await self.main_crop_integration_service.get_rotation_integration_plan(
                rotation_name, suitable_species, objectives
            )
            
            # Generate rotation-optimized recommendations
            rotation_recs = await self._generate_rotation_specific_recommendations(
                integration_plan, request
            )
            
            # Analyze field conditions with rotation context
            field_assessment = await self._analyze_field_conditions_with_rotation(
                request, integration_plan
            )
            
            # Generate benefit analysis
            benefit_analysis = await self.main_crop_integration_service.generate_benefit_analysis(
                integration_plan
            )
            
            # Create enhanced timeline with rotation integration
            timeline = await self._create_rotation_integration_timeline(
                request, integration_plan
            )
            
            response = CoverCropSelectionResponse(
                request_id=request.request_id,
                single_species_recommendations=rotation_recs[:5],
                mixture_recommendations=await self._generate_rotation_mixtures(integration_plan),
                field_assessment=field_assessment,
                climate_suitability=await self._assess_climate_suitability(request),
                seasonal_considerations=await self._get_rotation_seasonal_considerations(
                    request, integration_plan
                ),
                implementation_timeline=timeline,
                monitoring_recommendations=await self._get_rotation_monitoring_recommendations(
                    integration_plan
                ),
                follow_up_actions=await self._get_rotation_follow_up_actions(integration_plan),
                overall_confidence=await self._calculate_rotation_confidence(
                    rotation_recs, integration_plan
                ),
                data_sources=[
                    "USDA NRCS Cover Crop Database",
                    "Crop Rotation Integration Service",
                    "Regional Extension Services",
                    "SARE Cover Crop Research"
                ]
            )
            
            logger.info(f"Generated rotation integration recommendations for {rotation_name}")
            return response
            
        except Exception as e:
            logger.error(f"Error in rotation integration recommendations: {e}")
            # Fallback to standard recommendations for empty rotation names or other errors
            if not rotation_name or rotation_name.strip() == "":
                logger.info("Falling back to standard recommendations for empty rotation name")
                return await self.select_cover_crops(request)
            raise
    
    async def get_main_crop_compatibility_analysis(
        self,
        cover_crop_species_id: str,
        main_crop: str,
        position: str = "before"
    ) -> Dict[str, Any]:
        """
        Analyze compatibility between specific cover crop and main crop.
        
        Args:
            cover_crop_species_id: Cover crop species identifier
            main_crop: Main crop name
            position: Position relative to main crop (before/after/between)
            
        Returns:
            Detailed compatibility analysis
        """
        try:
            logger.info(f"Analyzing compatibility: {cover_crop_species_id} {position} {main_crop}")
            
            # Get cover crop species
            species = self.species_database.get(cover_crop_species_id)
            if not species:
                raise ValueError(f"Cover crop species '{cover_crop_species_id}' not found")
            
            # Perform compatibility analysis
            compatibility_analysis = await self.main_crop_integration_service.analyze_main_crop_compatibility(
                species, main_crop, position
            )
            
            # Add species-specific recommendations
            compatibility_analysis["species_recommendations"] = await self._generate_species_specific_recommendations(
                species, main_crop, position
            )
            
            # Add economic considerations
            compatibility_analysis["economic_analysis"] = await self._analyze_compatibility_economics(
                species, main_crop, position
            )
            
            return compatibility_analysis
            
        except Exception as e:
            logger.error(f"Error in compatibility analysis: {e}")
            raise
    
    async def get_rotation_position_recommendations(
        self,
        rotation_name: str,
        position_id: str,
        request: CoverCropSelectionRequest
    ) -> CoverCropSelectionResponse:
        """
        Get cover crop recommendations for specific position in rotation.
        
        Args:
            rotation_name: Name of the rotation system
            position_id: Specific position identifier in rotation
            request: Cover crop selection request
            
        Returns:
            Cover crop recommendations optimized for specific rotation position
        """
        try:
            logger.info(f"Processing position-specific request: {rotation_name} position {position_id}")
            
            # Get suitable species
            suitable_species = await self._find_suitable_species(request)
            
            # Create integration plan
            integration_plan = await self.main_crop_integration_service.get_rotation_integration_plan(
                rotation_name, suitable_species
            )
            
            # Filter recommendations for specific position
            position_recs = await self._filter_recommendations_by_position(
                integration_plan, position_id, request
            )
            
            # Generate position-specific analysis
            position_analysis = await self._analyze_specific_position(
                integration_plan, position_id
            )
            
            response = CoverCropSelectionResponse(
                request_id=request.request_id,
                single_species_recommendations=position_recs[:5],
                mixture_recommendations=await self._generate_position_mixtures(
                    integration_plan, position_id
                ),
                field_assessment=position_analysis,
                climate_suitability=await self._assess_climate_suitability(request),
                seasonal_considerations=await self._get_position_seasonal_considerations(
                    integration_plan, position_id
                ),
                implementation_timeline=await self._create_position_timeline(
                    integration_plan, position_id
                ),
                monitoring_recommendations=await self._get_position_monitoring_recommendations(
                    integration_plan, position_id
                ),
                follow_up_actions=await self._get_position_follow_up_actions(
                    integration_plan, position_id
                ),
                overall_confidence=0.85,  # Position-specific confidence
                data_sources=[
                    "Crop Rotation Integration Service",
                    "Position-Specific Analysis",
                    "USDA NRCS Cover Crop Database"
                ]
            )
            
            logger.info(f"Generated position-specific recommendations for {position_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error in position-specific recommendations: {e}")
            raise
    
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
            # LEGUMES - Nitrogen Fixers
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
                "species_id": "cc_004",
                "common_name": "Red Clover",
                "scientific_name": "Trifolium pratense",
                "cover_crop_type": CoverCropType.LEGUME,
                "hardiness_zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"],
                "min_temp_f": -20.0,
                "max_temp_f": 80.0,
                "growing_season": GrowingSeason.SPRING,
                "ph_range": {"min": 6.0, "max": 7.5},
                "drainage_tolerance": ["well_drained", "moderately_well_drained"],
                "salt_tolerance": "low",
                "seeding_rate_lbs_acre": {"broadcast": 12, "drilled": 8},
                "planting_depth_inches": 0.25,
                "days_to_establishment": 10,
                "biomass_production": "high",
                "primary_benefits": [SoilBenefit.NITROGEN_FIXATION, SoilBenefit.ORGANIC_MATTER, SoilBenefit.EROSION_CONTROL],
                "nitrogen_fixation_lbs_acre": 120,
                "root_depth_feet": 3.0,
                "termination_methods": ["herbicide", "mowing", "incorporation"],
                "cash_crop_compatibility": ["corn", "small_grains", "pasture"],
                "seed_cost_per_acre": 55.0,
                "establishment_cost_per_acre": 75.0
            },
            {
                "species_id": "cc_005",
                "common_name": "White Clover",
                "scientific_name": "Trifolium repens",
                "cover_crop_type": CoverCropType.LEGUME,
                "hardiness_zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
                "min_temp_f": -15.0,
                "max_temp_f": 85.0,
                "growing_season": GrowingSeason.SPRING,
                "ph_range": {"min": 5.5, "max": 7.5},
                "drainage_tolerance": ["well_drained", "moderately_well_drained", "somewhat_poorly_drained"],
                "salt_tolerance": "low",
                "seeding_rate_lbs_acre": {"broadcast": 6, "drilled": 4},
                "planting_depth_inches": 0.125,
                "days_to_establishment": 12,
                "biomass_production": "moderate",
                "primary_benefits": [SoilBenefit.NITROGEN_FIXATION, SoilBenefit.WEED_SUPPRESSION],
                "nitrogen_fixation_lbs_acre": 80,
                "root_depth_feet": 1.5,
                "termination_methods": ["herbicide", "mowing"],
                "cash_crop_compatibility": ["corn", "orchards", "pasture"],
                "seed_cost_per_acre": 30.0,
                "establishment_cost_per_acre": 45.0
            },
            {
                "species_id": "cc_006",
                "common_name": "Austrian Winter Pea",
                "scientific_name": "Pisum sativum",
                "cover_crop_type": CoverCropType.LEGUME,
                "hardiness_zones": ["6a", "6b", "7a", "7b", "8a", "8b"],
                "min_temp_f": 15.0,
                "max_temp_f": 75.0,
                "growing_season": GrowingSeason.WINTER,
                "ph_range": {"min": 6.0, "max": 7.5},
                "drainage_tolerance": ["well_drained", "moderately_well_drained"],
                "salt_tolerance": "low",
                "seeding_rate_lbs_acre": {"broadcast": 60, "drilled": 40},
                "planting_depth_inches": 1.0,
                "days_to_establishment": 14,
                "biomass_production": "high",
                "primary_benefits": [SoilBenefit.NITROGEN_FIXATION, SoilBenefit.BIOMASS_PRODUCTION, SoilBenefit.WEED_SUPPRESSION],
                "nitrogen_fixation_lbs_acre": 100,
                "root_depth_feet": 2.5,
                "termination_methods": ["herbicide", "mowing", "roller_crimper"],
                "cash_crop_compatibility": ["corn", "soybeans", "cotton"],
                "seed_cost_per_acre": 80.0,
                "establishment_cost_per_acre": 100.0
            },
            {
                "species_id": "cc_007",
                "common_name": "Hairy Vetch",
                "scientific_name": "Vicia villosa",
                "cover_crop_type": CoverCropType.LEGUME,
                "hardiness_zones": ["4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
                "min_temp_f": -10.0,
                "max_temp_f": 80.0,
                "growing_season": GrowingSeason.WINTER,
                "ph_range": {"min": 5.5, "max": 7.5},
                "drainage_tolerance": ["well_drained", "moderately_well_drained"],
                "salt_tolerance": "low",
                "seeding_rate_lbs_acre": {"broadcast": 30, "drilled": 20},
                "planting_depth_inches": 0.5,
                "days_to_establishment": 21,
                "biomass_production": "high",
                "primary_benefits": [SoilBenefit.NITROGEN_FIXATION, SoilBenefit.WEED_SUPPRESSION, SoilBenefit.EROSION_CONTROL],
                "nitrogen_fixation_lbs_acre": 150,
                "root_depth_feet": 3.0,
                "termination_methods": ["herbicide", "mowing", "roller_crimper"],
                "cash_crop_compatibility": ["corn", "soybeans"],
                "seed_cost_per_acre": 90.0,
                "establishment_cost_per_acre": 115.0
            },

            # GRASSES - Carbon Builders & Erosion Control
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
                "species_id": "cc_008",
                "common_name": "Winter Wheat",
                "scientific_name": "Triticum aestivum",
                "cover_crop_type": CoverCropType.GRASS,
                "hardiness_zones": ["4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"],
                "min_temp_f": -15.0,
                "max_temp_f": 75.0,
                "growing_season": GrowingSeason.WINTER,
                "ph_range": {"min": 6.0, "max": 7.5},
                "drainage_tolerance": ["well_drained", "moderately_well_drained"],
                "salt_tolerance": "moderate",
                "seeding_rate_lbs_acre": {"broadcast": 120, "drilled": 90},
                "planting_depth_inches": 1.0,
                "days_to_establishment": 10,
                "biomass_production": "high",
                "primary_benefits": [SoilBenefit.EROSION_CONTROL, SoilBenefit.NUTRIENT_SCAVENGING, SoilBenefit.ORGANIC_MATTER],
                "root_depth_feet": 2.5,
                "termination_methods": ["herbicide", "mowing", "incorporation"],
                "cash_crop_compatibility": ["corn", "soybeans"],
                "seed_cost_per_acre": 40.0,
                "establishment_cost_per_acre": 55.0
            },
            {
                "species_id": "cc_009",
                "common_name": "Oats",
                "scientific_name": "Avena sativa",
                "cover_crop_type": CoverCropType.GRASS,
                "hardiness_zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a"],
                "min_temp_f": 25.0,
                "max_temp_f": 70.0,
                "growing_season": GrowingSeason.FALL,
                "ph_range": {"min": 5.5, "max": 7.0},
                "drainage_tolerance": ["well_drained", "moderately_well_drained"],
                "salt_tolerance": "low",
                "seeding_rate_lbs_acre": {"broadcast": 80, "drilled": 60},
                "planting_depth_inches": 1.0,
                "days_to_establishment": 7,
                "biomass_production": "moderate",
                "primary_benefits": [SoilBenefit.EROSION_CONTROL, SoilBenefit.WEED_SUPPRESSION],
                "root_depth_feet": 2.0,
                "termination_methods": ["winter_kill", "mowing"],
                "cash_crop_compatibility": ["corn", "soybeans", "vegetables"],
                "seed_cost_per_acre": 30.0,
                "establishment_cost_per_acre": 45.0
            },
            {
                "species_id": "cc_010",
                "common_name": "Annual Ryegrass",
                "scientific_name": "Lolium annuum",
                "cover_crop_type": CoverCropType.GRASS,
                "hardiness_zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b", "9a"],
                "min_temp_f": 20.0,
                "max_temp_f": 85.0,
                "growing_season": GrowingSeason.WINTER,
                "ph_range": {"min": 5.5, "max": 7.5},
                "drainage_tolerance": ["well_drained", "moderately_well_drained", "somewhat_poorly_drained"],
                "salt_tolerance": "moderate",
                "seeding_rate_lbs_acre": {"broadcast": 30, "drilled": 20},
                "planting_depth_inches": 0.25,
                "days_to_establishment": 10,
                "biomass_production": "moderate",
                "primary_benefits": [SoilBenefit.EROSION_CONTROL, SoilBenefit.NUTRIENT_SCAVENGING],
                "root_depth_feet": 1.5,
                "termination_methods": ["herbicide", "mowing"],
                "cash_crop_compatibility": ["corn", "soybeans", "vegetables"],
                "seed_cost_per_acre": 25.0,
                "establishment_cost_per_acre": 40.0
            },
            {
                "species_id": "cc_011",
                "common_name": "Sorghum Sudan",
                "scientific_name": "Sorghum bicolor x S. sudanense",
                "cover_crop_type": CoverCropType.GRASS,
                "hardiness_zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b", "9a", "9b"],
                "min_temp_f": 50.0,
                "max_temp_f": 100.0,
                "growing_season": GrowingSeason.SUMMER,
                "ph_range": {"min": 5.5, "max": 8.0},
                "drainage_tolerance": ["well_drained", "moderately_well_drained", "somewhat_poorly_drained"],
                "salt_tolerance": "moderate",
                "seeding_rate_lbs_acre": {"broadcast": 30, "drilled": 20},
                "planting_depth_inches": 0.5,
                "days_to_establishment": 7,
                "biomass_production": "very_high",
                "primary_benefits": [SoilBenefit.BIOMASS_PRODUCTION, SoilBenefit.WEED_SUPPRESSION, SoilBenefit.COMPACTION_RELIEF],
                "root_depth_feet": 4.0,
                "termination_methods": ["herbicide", "mowing", "frost_kill"],
                "cash_crop_compatibility": ["corn", "soybeans", "wheat"],
                "seed_cost_per_acre": 20.0,
                "establishment_cost_per_acre": 35.0
            },

            # BRASSICAS - Biofumigants & Deep Taproot
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
            },
            {
                "species_id": "cc_012",
                "common_name": "Turnip",
                "scientific_name": "Brassica rapa",
                "cover_crop_type": CoverCropType.BRASSICA,
                "hardiness_zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"],
                "min_temp_f": 20.0,
                "max_temp_f": 75.0,
                "growing_season": GrowingSeason.FALL,
                "ph_range": {"min": 5.5, "max": 7.0},
                "drainage_tolerance": ["well_drained", "moderately_well_drained"],
                "salt_tolerance": "moderate",
                "seeding_rate_lbs_acre": {"broadcast": 5, "drilled": 3},
                "planting_depth_inches": 0.25,
                "days_to_establishment": 7,
                "biomass_production": "moderate",
                "primary_benefits": [SoilBenefit.NUTRIENT_SCAVENGING, SoilBenefit.PEST_SUPPRESSION, SoilBenefit.COMPACTION_RELIEF],
                "root_depth_feet": 3.0,
                "termination_methods": ["winter_kill", "mowing", "grazing"],
                "cash_crop_compatibility": ["corn", "soybeans", "vegetables"],
                "seed_cost_per_acre": 15.0,
                "establishment_cost_per_acre": 25.0
            },
            {
                "species_id": "cc_013",
                "common_name": "Mustard",
                "scientific_name": "Brassica juncea",
                "cover_crop_type": CoverCropType.BRASSICA,
                "hardiness_zones": ["4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
                "min_temp_f": 25.0,
                "max_temp_f": 85.0,
                "growing_season": GrowingSeason.FALL,
                "ph_range": {"min": 6.0, "max": 7.5},
                "drainage_tolerance": ["well_drained", "moderately_well_drained"],
                "salt_tolerance": "moderate",
                "seeding_rate_lbs_acre": {"broadcast": 8, "drilled": 5},
                "planting_depth_inches": 0.25,
                "days_to_establishment": 5,
                "biomass_production": "moderate",
                "primary_benefits": [SoilBenefit.PEST_SUPPRESSION, SoilBenefit.NUTRIENT_SCAVENGING, SoilBenefit.WEED_SUPPRESSION],
                "root_depth_feet": 2.0,
                "termination_methods": ["winter_kill", "mowing", "herbicide"],
                "cash_crop_compatibility": ["corn", "soybeans", "potatoes"],
                "seed_cost_per_acre": 18.0,
                "establishment_cost_per_acre": 28.0
            },

            # FORBS/BROADLEAVES - Diverse Benefits
            {
                "species_id": "cc_014",
                "common_name": "Sunflower",
                "scientific_name": "Helianthus annuus",
                "cover_crop_type": CoverCropType.FORB,
                "hardiness_zones": ["4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b"],
                "min_temp_f": 35.0,
                "max_temp_f": 95.0,
                "growing_season": GrowingSeason.SUMMER,
                "ph_range": {"min": 6.0, "max": 7.5},
                "drainage_tolerance": ["well_drained", "moderately_well_drained"],
                "salt_tolerance": "moderate",
                "seeding_rate_lbs_acre": {"broadcast": 25, "drilled": 15},
                "planting_depth_inches": 1.0,
                "days_to_establishment": 10,
                "biomass_production": "high",
                "primary_benefits": [SoilBenefit.COMPACTION_RELIEF, SoilBenefit.NUTRIENT_SCAVENGING, SoilBenefit.POLLINATOR_HABITAT],
                "root_depth_feet": 6.0,
                "termination_methods": ["herbicide", "mowing", "frost_kill"],
                "cash_crop_compatibility": ["corn", "soybeans", "small_grains"],
                "seed_cost_per_acre": 35.0,
                "establishment_cost_per_acre": 50.0
            },
            {
                "species_id": "cc_015",
                "common_name": "Buckwheat",
                "scientific_name": "Fagopyrum esculentum",
                "cover_crop_type": CoverCropType.FORB,
                "hardiness_zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"],
                "min_temp_f": 35.0,
                "max_temp_f": 80.0,
                "growing_season": GrowingSeason.SUMMER,
                "ph_range": {"min": 5.0, "max": 7.0},
                "drainage_tolerance": ["well_drained", "moderately_well_drained"],
                "salt_tolerance": "low",
                "seeding_rate_lbs_acre": {"broadcast": 70, "drilled": 50},
                "planting_depth_inches": 0.75,
                "days_to_establishment": 7,
                "biomass_production": "moderate",
                "primary_benefits": [SoilBenefit.PHOSPHORUS_MOBILIZATION, SoilBenefit.POLLINATOR_HABITAT, SoilBenefit.WEED_SUPPRESSION],
                "root_depth_feet": 1.5,
                "termination_methods": ["frost_kill", "mowing", "herbicide"],
                "cash_crop_compatibility": ["corn", "soybeans", "vegetables"],
                "seed_cost_per_acre": 40.0,
                "establishment_cost_per_acre": 55.0
            },
            {
                "species_id": "cc_016",
                "common_name": "Phacelia",
                "scientific_name": "Phacelia tanacetifolia",
                "cover_crop_type": CoverCropType.FORB,
                "hardiness_zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b"],
                "min_temp_f": 30.0,
                "max_temp_f": 85.0,
                "growing_season": GrowingSeason.SPRING,
                "ph_range": {"min": 6.0, "max": 7.5},
                "drainage_tolerance": ["well_drained", "moderately_well_drained"],
                "salt_tolerance": "low",
                "seeding_rate_lbs_acre": {"broadcast": 8, "drilled": 5},
                "planting_depth_inches": 0.25,
                "days_to_establishment": 10,
                "biomass_production": "moderate",
                "primary_benefits": [SoilBenefit.POLLINATOR_HABITAT, SoilBenefit.PEST_SUPPRESSION, SoilBenefit.ORGANIC_MATTER],
                "root_depth_feet": 2.0,
                "termination_methods": ["mowing", "herbicide", "incorporation"],
                "cash_crop_compatibility": ["corn", "vegetables", "orchards"],
                "seed_cost_per_acre": 65.0,
                "establishment_cost_per_acre": 85.0
            },

            # SPECIALTY LEGUMES
            {
                "species_id": "cc_017",
                "common_name": "Cowpea",
                "scientific_name": "Vigna unguiculata",
                "cover_crop_type": CoverCropType.LEGUME,
                "hardiness_zones": ["6a", "6b", "7a", "7b", "8a", "8b", "9a", "9b"],
                "min_temp_f": 50.0,
                "max_temp_f": 95.0,
                "growing_season": GrowingSeason.SUMMER,
                "ph_range": {"min": 5.5, "max": 7.5},
                "drainage_tolerance": ["well_drained", "moderately_well_drained", "somewhat_poorly_drained"],
                "salt_tolerance": "moderate",
                "seeding_rate_lbs_acre": {"broadcast": 40, "drilled": 30},
                "planting_depth_inches": 1.0,
                "days_to_establishment": 14,
                "biomass_production": "moderate",
                "primary_benefits": [SoilBenefit.NITROGEN_FIXATION, SoilBenefit.HEAT_TOLERANCE, SoilBenefit.WEED_SUPPRESSION],
                "nitrogen_fixation_lbs_acre": 90,
                "root_depth_feet": 2.5,
                "termination_methods": ["herbicide", "mowing", "frost_kill"],
                "cash_crop_compatibility": ["corn", "cotton", "vegetables"],
                "seed_cost_per_acre": 60.0,
                "establishment_cost_per_acre": 80.0
            },
            {
                "species_id": "cc_018",
                "common_name": "Berseem Clover",
                "scientific_name": "Trifolium alexandrinum",
                "cover_crop_type": CoverCropType.LEGUME,
                "hardiness_zones": ["7a", "7b", "8a", "8b", "9a", "9b"],
                "min_temp_f": 25.0,
                "max_temp_f": 90.0,
                "growing_season": GrowingSeason.WINTER,
                "ph_range": {"min": 6.5, "max": 8.0},
                "drainage_tolerance": ["well_drained", "moderately_well_drained"],
                "salt_tolerance": "moderate",
                "seeding_rate_lbs_acre": {"broadcast": 20, "drilled": 15},
                "planting_depth_inches": 0.25,
                "days_to_establishment": 14,
                "biomass_production": "high",
                "primary_benefits": [SoilBenefit.NITROGEN_FIXATION, SoilBenefit.SALT_TOLERANCE, SoilBenefit.BIOMASS_PRODUCTION],
                "nitrogen_fixation_lbs_acre": 100,
                "root_depth_feet": 2.0,
                "termination_methods": ["herbicide", "mowing", "incorporation"],
                "cash_crop_compatibility": ["cotton", "corn", "vegetables"],
                "seed_cost_per_acre": 70.0,
                "establishment_cost_per_acre": 90.0
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
                    f"{self.climate_service_url}/api/v1/climate/detect-zone",
                    json={
                        "latitude": request.location.get("latitude"),
                        "longitude": request.location.get("longitude"),
                        "elevation_ft": request.location.get("elevation_ft") if request.location else None
                    }
                )
                
                if climate_response.status_code == 200:
                    climate_data = climate_response.json()
                    # Extract zone information from the response
                    primary_zone = climate_data.get("primary_zone", {})
                    zone_id = primary_zone.get("zone_id", "7a")
                    
                    # Update request with enhanced climate information
                    if not request.climate_data:
                        request.climate_data = ClimateData(
                            hardiness_zone=zone_id,
                            min_temp_f=primary_zone.get("min_temp_f"),
                            max_temp_f=primary_zone.get("max_temp_f"),
                            growing_season_length=primary_zone.get("growing_season_days"),
                            average_annual_precipitation=climate_data.get("precipitation_inches")
                        )
                    else:
                        request.climate_data.hardiness_zone = zone_id
                        if not request.climate_data.min_temp_f:
                            request.climate_data.min_temp_f = primary_zone.get("min_temp_f")
                        if not request.climate_data.max_temp_f:
                            request.climate_data.max_temp_f = primary_zone.get("max_temp_f")
                        if not request.climate_data.growing_season_length:
                            request.climate_data.growing_season_length = primary_zone.get("growing_season_days")
                        if not request.climate_data.average_annual_precipitation:
                            request.climate_data.average_annual_precipitation = climate_data.get("precipitation_inches")
        
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
        """Check if a species is suitable for the given conditions with enhanced climate and soil matching."""
        # Enhanced hardiness zone compatibility
        if request.climate_data and request.climate_data.hardiness_zone:
            if request.climate_data.hardiness_zone not in species.hardiness_zones:
                return False
        
        # Enhanced temperature tolerance check
        if request.climate_data:
            # Check minimum temperature tolerance
            if (request.climate_data.min_temp_f is not None and 
                species.min_temp_f is not None and
                request.climate_data.min_temp_f < species.min_temp_f):
                return False
            
            # Check maximum temperature tolerance  
            if (request.climate_data.max_temp_f is not None and
                species.max_temp_f is not None and
                request.climate_data.max_temp_f > species.max_temp_f):
                return False
        
        # Enhanced soil pH compatibility with tolerance buffer
        soil_ph = request.soil_conditions.ph
        ph_buffer = 0.2  # Allow slight pH tolerance beyond stated range
        if not (species.ph_range["min"] - ph_buffer <= soil_ph <= species.ph_range["max"] + ph_buffer):
            return False
        
        # Enhanced drainage compatibility
        if request.soil_conditions.drainage_class not in species.drainage_tolerance:
            return False
        
        # Enhanced salt tolerance check
        if (hasattr(request.soil_conditions, 'salinity_level') and 
            request.soil_conditions.salinity_level and
            species.salt_tolerance):
            salinity_level = request.soil_conditions.salinity_level.lower()
            species_tolerance = species.salt_tolerance.lower()
            
            # Basic salinity compatibility mapping
            salinity_order = ['low', 'moderate', 'high']
            if (salinity_level in salinity_order and 
                species_tolerance in salinity_order and
                salinity_order.index(salinity_level) > salinity_order.index(species_tolerance)):
                return False
        
        # Enhanced planting window compatibility
        planting_start = request.planting_window.get("start")
        planting_end = request.planting_window.get("end")
        
        if planting_start and planting_end:
            plant_month = planting_start.month
            
            # More flexible seasonal compatibility
            winter_months = [9, 10, 11, 12, 1, 2]
            summer_months = [3, 4, 5, 6, 7, 8]
            fall_months = [7, 8, 9, 10]
            spring_months = [3, 4, 5, 6]
            
            if species.growing_season == GrowingSeason.WINTER and plant_month not in winter_months:
                return False
            elif species.growing_season == GrowingSeason.SUMMER and plant_month not in summer_months:
                return False
            elif species.growing_season == GrowingSeason.FALL and plant_month not in fall_months:
                return False
            elif species.growing_season == GrowingSeason.SPRING and plant_month not in spring_months:
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
        """Calculate comprehensive suitability score for a species."""
        # Get climate and soil compatibility score (50% of total score)
        climate_soil_score = await self._calculate_climate_soil_compatibility_score(species, request)
        total_score = climate_soil_score * 0.5
        
        # Objective alignment score (30% of total score)
        objective_score = 0.0
        if request.objectives and request.objectives.primary_goals:
            total_objectives = len(request.objectives.primary_goals)
            for goal in request.objectives.primary_goals:
                if goal in species.primary_benefits:
                    objective_score += 1.0 / total_objectives
        else:
            # Default objective score if no specific objectives
            objective_score = 0.7
        
        total_score += objective_score * 0.3
        
        # Economic feasibility score (10% of total score)
        economic_score = 1.0  # Default to good economic feasibility
        if request.objectives and request.objectives.budget_per_acre:
            if species.establishment_cost_per_acre:
                cost_ratio = species.establishment_cost_per_acre / request.objectives.budget_per_acre
                if cost_ratio <= 1.0:
                    economic_score = 1.0
                elif cost_ratio <= 1.5:
                    economic_score = 0.8
                else:
                    economic_score = 0.4  # Expensive but potentially viable
        
        total_score += economic_score * 0.1
        
        # Management complexity adjustment (5% of total score)
        management_score = self._calculate_management_score(species, request)
        total_score += management_score * 0.05
        
        # Special benefits bonus (5% of total score)
        bonus_score = self._calculate_special_benefits_bonus(species, request)
        total_score += bonus_score * 0.05
        
        return min(1.0, total_score)  # Cap at 1.0
    
    def _calculate_management_score(self, species: CoverCropSpecies, request: CoverCropSelectionRequest) -> float:
        """Calculate management complexity score."""
        score = 1.0
        
        # Simple termination methods are preferred
        easy_termination = ['winter_kill', 'herbicide', 'mowing']
        if any(method in species.termination_methods for method in easy_termination):
            score = 1.0
        elif 'mechanical' in species.termination_methods:
            score = 0.8
        else:
            score = 0.6
        
        # Quick establishment is preferred
        if species.days_to_establishment <= 10:
            score += 0.2
        elif species.days_to_establishment <= 20:
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_special_benefits_bonus(self, species: CoverCropSpecies, request: CoverCropSelectionRequest) -> float:
        """Calculate bonus score for special benefits."""
        bonus = 0.0
        
        # Nitrogen fixation bonus
        if (request.objectives and request.objectives.nitrogen_needs and 
            SoilBenefit.NITROGEN_FIXATION in species.primary_benefits):
            bonus += 0.3
        
        # Soil health bonus
        soil_health_benefits = [
            SoilBenefit.ORGANIC_MATTER,
            SoilBenefit.SOIL_STRUCTURE,
            SoilBenefit.EROSION_CONTROL
        ]
        
        matching_benefits = sum(1 for benefit in soil_health_benefits 
                              if benefit in species.primary_benefits)
        bonus += matching_benefits * 0.1
        
        # Pest/disease management bonus
        if SoilBenefit.PEST_SUPPRESSION in species.primary_benefits:
            bonus += 0.2
        
        return min(1.0, bonus)
    
    async def _calculate_management_complexity_score(self, species: CoverCropSpecies, request: CoverCropSelectionRequest) -> float:
        """Calculate score based on management complexity."""
        score = 0.5  # Base score
        
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
    
    async def _calculate_climate_soil_compatibility_score(self, species: CoverCropSpecies, request: CoverCropSelectionRequest) -> float:
        """Calculate comprehensive climate and soil compatibility score for a species."""
        total_score = 0.0
        weight_sum = 0.0
        
        # Hardiness zone compatibility (weight: 25%)
        zone_weight = 0.25
        if request.climate_data and request.climate_data.hardiness_zone:
            if request.climate_data.hardiness_zone in species.hardiness_zones:
                zone_score = 1.0
            else:
                # Calculate proximity score for nearby zones
                zone_score = self._calculate_zone_proximity_score(
                    request.climate_data.hardiness_zone, 
                    species.hardiness_zones
                )
            total_score += zone_score * zone_weight
            weight_sum += zone_weight
        
        # Temperature tolerance (weight: 20%)
        temp_weight = 0.20
        if request.climate_data and species.min_temp_f is not None and species.max_temp_f is not None:
            temp_score = 1.0
            
            # Check minimum temperature tolerance
            if (request.climate_data.min_temp_f is not None and 
                request.climate_data.min_temp_f < species.min_temp_f):
                temp_deficit = species.min_temp_f - request.climate_data.min_temp_f
                temp_score *= max(0.0, 1.0 - (temp_deficit / 20.0))  # Gradual penalty
            
            # Check maximum temperature tolerance
            if (request.climate_data.max_temp_f is not None and
                request.climate_data.max_temp_f > species.max_temp_f):
                temp_excess = request.climate_data.max_temp_f - species.max_temp_f
                temp_score *= max(0.0, 1.0 - (temp_excess / 15.0))  # Gradual penalty
            
            total_score += temp_score * temp_weight
            weight_sum += temp_weight
        
        # Soil pH compatibility (weight: 20%)
        ph_weight = 0.20
        soil_ph = request.soil_conditions.ph
        ph_min, ph_max = species.ph_range["min"], species.ph_range["max"]
        
        if ph_min <= soil_ph <= ph_max:
            ph_score = 1.0
        else:
            # Calculate distance from acceptable range
            if soil_ph < ph_min:
                ph_distance = ph_min - soil_ph
            else:
                ph_distance = soil_ph - ph_max
            
            # Gradual penalty based on pH distance
            ph_score = max(0.0, 1.0 - (ph_distance / 1.5))
        
        total_score += ph_score * ph_weight
        weight_sum += ph_weight
        
        # Drainage compatibility (weight: 15%)
        drainage_weight = 0.15
        if request.soil_conditions.drainage_class in species.drainage_tolerance:
            drainage_score = 1.0
        else:
            # Partial score for compatible drainage types
            drainage_score = self._calculate_drainage_compatibility_score(
                request.soil_conditions.drainage_class,
                species.drainage_tolerance
            )
        
        total_score += drainage_score * drainage_weight
        weight_sum += drainage_weight
        
        # Growing season compatibility (weight: 15%)
        season_weight = 0.15
        planting_start = request.planting_window.get("start")
        if planting_start:
            season_score = self._calculate_seasonal_compatibility_score(
                planting_start.month, species.growing_season
            )
            total_score += season_score * season_weight
            weight_sum += season_weight
        
        # Salt tolerance (weight: 5%) - if applicable
        salt_weight = 0.05
        if (hasattr(request.soil_conditions, 'salinity_level') and 
            request.soil_conditions.salinity_level and
            species.salt_tolerance):
            salt_score = self._calculate_salt_tolerance_score(
                request.soil_conditions.salinity_level,
                species.salt_tolerance
            )
            total_score += salt_score * salt_weight
            weight_sum += salt_weight
        
        # Return normalized score
        return total_score / weight_sum if weight_sum > 0 else 0.0
    
    def _calculate_zone_proximity_score(self, target_zone: str, species_zones: List[str]) -> float:
        """Calculate proximity score for hardiness zones."""
        # Extract numeric part of target zone (e.g., "7a" -> 7)
        try:
            target_num = int(target_zone[0])
        except (ValueError, IndexError):
            return 0.0
        
        # Find closest zone match
        min_distance = float('inf')
        for zone in species_zones:
            try:
                zone_num = int(zone[0])
                distance = abs(target_num - zone_num)
                min_distance = min(min_distance, distance)
            except (ValueError, IndexError):
                continue
        
        # Convert distance to score (1 zone difference = 0.8, 2 zones = 0.6, etc.)
        if min_distance == 0:
            return 1.0
        elif min_distance == 1:
            return 0.8
        elif min_distance == 2:
            return 0.6
        elif min_distance == 3:
            return 0.4
        else:
            return 0.2
    
    def _calculate_drainage_compatibility_score(self, soil_drainage: str, species_tolerance: List[str]) -> float:
        """Calculate drainage compatibility score."""
        # Define drainage compatibility matrix
        drainage_order = [
            "very_poorly_drained",
            "poorly_drained", 
            "somewhat_poorly_drained",
            "moderately_well_drained",
            "well_drained",
            "somewhat_excessively_drained",
            "excessively_drained"
        ]
        
        try:
            soil_index = drainage_order.index(soil_drainage)
        except ValueError:
            return 0.0
        
        # Calculate compatibility based on proximity to acceptable drainage types
        best_score = 0.0
        for acceptable_drainage in species_tolerance:
            try:
                acceptable_index = drainage_order.index(acceptable_drainage)
                distance = abs(soil_index - acceptable_index)
                
                if distance == 0:
                    score = 1.0
                elif distance == 1:
                    score = 0.8
                elif distance == 2:
                    score = 0.6
                else:
                    score = 0.3
                
                best_score = max(best_score, score)
            except ValueError:
                continue
        
        return best_score
    
    def _calculate_seasonal_compatibility_score(self, planting_month: int, growing_season: GrowingSeason) -> float:
        """Calculate seasonal compatibility score."""
        # Define optimal planting months for each season
        season_months = {
            GrowingSeason.WINTER: [9, 10, 11],
            GrowingSeason.SUMMER: [4, 5, 6],
            GrowingSeason.FALL: [7, 8, 9],
            GrowingSeason.SPRING: [3, 4, 5]
        }
        
        optimal_months = season_months.get(growing_season, [])
        
        if planting_month in optimal_months:
            return 1.0
        
        # Calculate proximity to optimal months
        min_distance = min(
            min(abs(planting_month - opt_month), 12 - abs(planting_month - opt_month))
            for opt_month in optimal_months
        ) if optimal_months else 6
        
        if min_distance <= 1:
            return 0.8
        elif min_distance <= 2:
            return 0.6
        elif min_distance <= 3:
            return 0.4
        else:
            return 0.2
    
    def _calculate_salt_tolerance_score(self, soil_salinity: str, species_tolerance: str) -> float:
        """Calculate salt tolerance compatibility score."""
        salinity_levels = {'low': 0, 'moderate': 1, 'high': 2}
        
        try:
            soil_level = salinity_levels[soil_salinity.lower()]
            species_level = salinity_levels[species_tolerance.lower()]
            
            if species_level >= soil_level:
                return 1.0
            else:
                # Penalty for insufficient salt tolerance
                difference = soil_level - species_level
                return max(0.0, 1.0 - (difference * 0.4))
        except KeyError:
            return 0.5  # Default score for unknown salinity levels

    async def _assess_climate_suitability(self, request: CoverCropSelectionRequest) -> Dict[str, Any]:
        """Assess climate suitability for cover crops with enhanced analysis."""
        suitability_data = {
            "hardiness_zone": request.climate_data.hardiness_zone if request.climate_data else "Unknown",
            "suitability": "Unknown",
            "considerations": []
        }
        
        if request.climate_data:
            zone = request.climate_data.hardiness_zone
            considerations = ["Verify local frost dates", "Monitor weather patterns"]
            
            # Enhanced climate analysis
            if request.climate_data.min_temp_f is not None:
                if request.climate_data.min_temp_f < -10:
                    considerations.append("Extremely cold temperatures - select cold-hardy species")
                    suitability_data["suitability"] = "Challenging"
                elif request.climate_data.min_temp_f > 25:
                    considerations.append("Mild winters - good for cool-season species")
                    suitability_data["suitability"] = "Good"
            
            if request.climate_data.max_temp_f is not None:
                if request.climate_data.max_temp_f > 90:
                    considerations.append("High summer temperatures - ensure heat tolerance")
                elif request.climate_data.max_temp_f < 70:
                    considerations.append("Cool summers - excellent for cool-season crops")
            
            if request.climate_data.growing_season_length:
                if request.climate_data.growing_season_length > 200:
                    considerations.append("Long growing season - multiple planting options")
                    suitability_data["suitability"] = "Excellent"
                elif request.climate_data.growing_season_length < 120:
                    considerations.append("Short growing season - select quick-establishing species")
            
            if request.climate_data.average_annual_precipitation:
                if request.climate_data.average_annual_precipitation < 20:
                    considerations.append("Low precipitation - prioritize drought-tolerant species")
                elif request.climate_data.average_annual_precipitation > 50:
                    considerations.append("High precipitation - ensure good drainage tolerance")
            
            suitability_data["considerations"] = considerations
            
            # Set default suitability if not already determined
            if suitability_data["suitability"] == "Unknown":
                suitability_data["suitability"] = "Good"
        else:
            suitability_data["considerations"] = [
                "Climate data unavailable - verify local conditions",
                "Consult local extension services for planting guidance"
            ]
        
        return suitability_data
    
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
    
    async def get_goal_based_recommendations(
        self,
        request: CoverCropSelectionRequest,
        objectives: GoalBasedObjectives
    ) -> GoalBasedRecommendation:
        """
        Get goal-based cover crop recommendations.
        
        Args:
            request: Cover crop selection request with location and conditions
            objectives: Goal-based objectives with farmer priorities
            
        Returns:
            Goal-based recommendation with optimized species and management
        """
        try:
            logger.info(f"Processing goal-based recommendation request: {request.request_id}")
            
            # Get suitable species first
            suitable_species = await self._find_suitable_species(request)
            
            if not suitable_species:
                logger.warning("No suitable species found for goal-based recommendations")
                # Return empty recommendation
                return GoalBasedRecommendation(
                    request_id=request.request_id,
                    farmer_goals=objectives,
                    recommended_species=[],
                    goal_achievement_scores={},
                    optimized_seeding_rates={},
                    goal_focused_management={},
                    cost_benefit_analysis={},
                    goal_synergy_analysis={},
                    confidence_score=0.0
                )
            
            # Use goal-based service to generate recommendations
            individual_recommendations = await self.goal_based_service.generate_goal_based_recommendations(
                species_candidates=suitable_species,
                objectives=objectives,
                soil_conditions=request.soil_conditions,
                climate_data=request.climate_data if hasattr(request, 'climate_data') else None,
                planting_window=request.planting_window if hasattr(request, 'planting_window') else None
            )
            
            # Convert individual recommendations to response format
            if individual_recommendations:
                # Create response with all recommended species
                recommended_species = [rec.species for rec in individual_recommendations]
                
                # Calculate aggregate scores and analysis
                avg_alignment = sum(rec.overall_goal_alignment for rec in individual_recommendations) / len(individual_recommendations)
                
                # Combine goal achievements from all recommendations
                combined_goal_achievements = {}
                for rec in individual_recommendations:
                    for goal_achievement in rec.goal_achievement_scores:
                        goal_key = f"{goal_achievement.goal_name}_{goal_achievement.goal_category}"
                        if goal_key not in combined_goal_achievements:
                            combined_goal_achievements[goal_key] = []
                        combined_goal_achievements[goal_key].append(goal_achievement.achievement_score)
                
                # Average the achievement scores by goal
                avg_goal_achievements = {
                    goal: sum(scores) / len(scores) for goal, scores in combined_goal_achievements.items()
                }
                
                # Create optimized seeding rates mapping
                optimized_seeding_rates = {
                    rec.species.species_id: rec.goal_optimized_seeding_rate 
                    for rec in individual_recommendations
                }
                
                # Create goal-focused management guidance
                goal_focused_management = {}
                for rec in individual_recommendations:
                    for goal_category, benefits in rec.goal_specific_benefits.items():
                        if goal_category not in goal_focused_management:
                            goal_focused_management[goal_category] = {
                                'planting_practices': [],
                                'maintenance_practices': [],
                                'termination_practices': []
                            }
                        
                        # Add management notes from this recommendation
                        for note in rec.goal_focused_management_notes:
                            if 'planting' in note.lower():
                                goal_focused_management[goal_category]['planting_practices'].append(note)
                            elif 'maintenance' in note.lower() or 'monitoring' in note.lower():
                                goal_focused_management[goal_category]['maintenance_practices'].append(note)
                            elif 'termination' in note.lower():
                                goal_focused_management[goal_category]['termination_practices'].append(note)
                
                # Calculate cost-benefit analysis
                total_cost = sum(
                    rec.goal_based_cost_benefit.get('establishment_cost', 0) if rec.goal_based_cost_benefit else 0
                    for rec in individual_recommendations
                )
                total_benefits = sum(
                    rec.goal_based_cost_benefit.get('expected_benefits', 0) if rec.goal_based_cost_benefit else 0
                    for rec in individual_recommendations
                )
                
                cost_benefit_analysis = {
                    'total_establishment_cost': total_cost,
                    'expected_benefits': total_benefits,
                    'roi_estimate': (total_benefits / total_cost) if total_cost > 0 else 0.0
                }
                
                # Create goal synergy analysis
                goal_synergy_analysis = {
                    'synergy_score': sum(rec.goal_synergy_score for rec in individual_recommendations) / len(individual_recommendations),
                    'potential_conflicts': [],
                    'enhancement_opportunities': []
                }
                
                # Add potential conflicts from recommendations
                for rec in individual_recommendations:
                    if rec.potential_goal_trade_offs:
                        goal_synergy_analysis['potential_conflicts'].extend(rec.potential_goal_trade_offs)
                    goal_synergy_analysis['enhancement_opportunities'].extend(rec.goal_enhancement_strategies)
                
                # Create the response
                goal_recommendation = GoalBasedRecommendation(
                    request_id=request.request_id,
                    farmer_goals=objectives,
                    recommended_species=recommended_species,
                    goal_achievement_scores=avg_goal_achievements,
                    optimized_seeding_rates=optimized_seeding_rates,
                    goal_focused_management=goal_focused_management,
                    cost_benefit_analysis=cost_benefit_analysis,
                    goal_synergy_analysis=goal_synergy_analysis,
                    confidence_score=avg_alignment,
                    individual_recommendations=individual_recommendations
                )
                
                logger.info(f"Generated goal-based recommendations with {len(recommended_species)} species")
                return goal_recommendation
            else:
                logger.warning("No goal-based recommendations generated")
                return GoalBasedRecommendation(
                    request_id=request.request_id,
                    farmer_goals=objectives,
                    recommended_species=[],
                    goal_achievement_scores={},
                    optimized_seeding_rates={},
                    goal_focused_management={},
                    cost_benefit_analysis={},
                    goal_synergy_analysis={},
                    confidence_score=0.0
                )
            
        except Exception as e:
            logger.error(f"Error in goal-based recommendations: {e}")
            raise
    
    async def analyze_goal_feasibility(
        self,
        request: CoverCropSelectionRequest,
        objectives: GoalBasedObjectives
    ) -> Dict[str, Any]:
        """
        Analyze feasibility of achieving specified goals.
        
        Args:
            request: Cover crop selection request with location and conditions
            objectives: Goal-based objectives to analyze
            
        Returns:
            Detailed feasibility analysis with recommendations
        """
        try:
            logger.info(f"Analyzing goal feasibility for request: {request.request_id}")
            
            # Get suitable species for analysis
            suitable_species = await self._find_suitable_species(request)
            
            # Use goal-based service for feasibility analysis
            feasibility_analysis = await self.goal_based_service.analyze_goal_feasibility(
                suitable_species, request, objectives
            )
            
            return feasibility_analysis
            
        except Exception as e:
            logger.error(f"Error in goal feasibility analysis: {e}")
            raise
    
    async def get_goal_categories_and_options(self) -> Dict[str, Any]:
        """
        Get available goal categories and specific goal options.
        
        Returns:
            Dictionary of available goals and options for goal-based planning
        """
        try:
            return self.goal_based_service.get_available_goal_categories()
            
        except Exception as e:
            logger.error(f"Error getting goal categories: {e}")
            raise