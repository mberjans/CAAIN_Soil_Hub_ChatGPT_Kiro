"""
Sophisticated Timing-Based Variety Filtering Service

This service implements advanced timing-based filtering for crop varieties,
including season length compatibility, planting window flexibility,
harvest timing optimization, and succession planting coordination.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import date, datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field

from models.crop_variety_models import EnhancedCropVariety, VarietyRecommendationCriteria


# Simple location data model for timing filter
class LocationData(BaseModel):
    """Location data for timing-based filtering."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    climate_zone: Optional[str] = Field(None, description="Climate zone identifier")
    elevation_meters: Optional[int] = Field(None, description="Elevation in meters")

logger = logging.getLogger(__name__)


class TimingFilterType(str, Enum):
    """Types of timing-based filters."""
    SEASON_LENGTH = "season_length"
    PLANTING_WINDOW = "planting_window"
    HARVEST_TIMING = "harvest_timing"
    SUCCESSION_PLANTING = "succession_planting"
    GROWING_DEGREE_DAYS = "growing_degree_days"
    PHOTOPERIOD_RESPONSE = "photoperiod_response"


class SeasonLengthCompatibility(str, Enum):
    """Season length compatibility levels."""
    EXCELLENT = "excellent"  # Perfect fit with buffer
    GOOD = "good"           # Good fit with minimal risk
    MARGINAL = "marginal"   # Possible but risky
    POOR = "poor"          # Not recommended
    INCOMPATIBLE = "incompatible"  # Impossible


class PlantingWindowFlexibility(str, Enum):
    """Planting window flexibility levels."""
    VERY_FLEXIBLE = "very_flexible"  # 4+ weeks window
    FLEXIBLE = "flexible"           # 2-4 weeks window
    MODERATE = "moderate"           # 1-2 weeks window
    NARROW = "narrow"               # <1 week window
    CRITICAL = "critical"           # Very narrow window


@dataclass
class TimingFilterCriteria:
    """Criteria for timing-based variety filtering."""
    
    # Season length requirements
    available_growing_days: int
    min_growing_days_required: Optional[int] = None
    max_growing_days_tolerated: Optional[int] = None
    
    # Planting window constraints
    preferred_planting_start: Optional[date] = None
    preferred_planting_end: Optional[date] = None
    planting_window_flexibility: Optional[PlantingWindowFlexibility] = None
    
    # Harvest timing preferences
    preferred_harvest_start: Optional[date] = None
    preferred_harvest_end: Optional[date] = None
    harvest_timing_constraints: Optional[List[str]] = None  # e.g., ["before_frost", "market_timing"]
    
    # Succession planting requirements
    succession_planting_needed: bool = False
    succession_interval_days: Optional[int] = None
    multiple_plantings_per_season: bool = False
    
    # Growing degree day requirements
    target_growing_degree_days: Optional[int] = None
    gdd_tolerance_percent: float = 10.0  # ±10% tolerance
    
    # Photoperiod sensitivity
    photoperiod_sensitive: Optional[bool] = None
    day_length_requirements: Optional[Tuple[int, int]] = None  # (min_hours, max_hours)


class TimingCompatibilityScore(BaseModel):
    """Timing compatibility scoring for a variety."""
    
    variety_id: str
    variety_name: str
    
    # Overall compatibility
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall compatibility score")
    compatibility_level: SeasonLengthCompatibility
    
    # Individual component scores
    season_length_score: float = Field(..., ge=0.0, le=1.0, description="Season length compatibility score")
    planting_window_score: float = Field(..., ge=0.0, le=1.0, description="Planting window compatibility score")
    harvest_timing_score: float = Field(..., ge=0.0, le=1.0, description="Harvest timing compatibility score")
    succession_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Succession planting compatibility score")
    gdd_compatibility_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="GDD compatibility score")
    photoperiod_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Photoperiod compatibility score")
    
    # Detailed analysis
    season_length_analysis: Dict[str, Any] = Field(..., description="Season length analysis details")
    planting_window_analysis: Dict[str, Any] = Field(..., description="Planting window analysis details")
    harvest_timing_analysis: Dict[str, Any] = Field(..., description="Harvest timing analysis details")
    succession_analysis: Optional[Dict[str, Any]] = Field(None, description="Succession planting analysis details")
    gdd_analysis: Optional[Dict[str, Any]] = Field(None, description="GDD analysis details")
    photoperiod_analysis: Optional[Dict[str, Any]] = Field(None, description="Photoperiod analysis details")
    
    # Recommendations
    timing_recommendations: List[str] = Field(default_factory=list, description="Timing recommendations")
    risk_factors: List[str] = Field(default_factory=list, description="Risk factors")
    optimization_suggestions: List[str] = Field(default_factory=list, description="Optimization suggestions")


class TimingBasedVarietyFilter:
    """
    Sophisticated timing-based variety filtering service.
    
    Provides advanced filtering capabilities for crop varieties based on:
    - Season length compatibility and growing degree day requirements
    - Planting window flexibility and timing constraints
    - Harvest timing optimization and market coordination
    - Succession planting coordination and multiple planting scenarios
    - Photoperiod response and day length requirements
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize the timing-based variety filter."""
        try:
            from database.crop_taxonomy_db import CropTaxonomyDatabase
            self.db = CropTaxonomyDatabase(database_url)
            self.database_available = self.db.test_connection()
            logger.info(f"Timing filter database connection: {'successful' if self.database_available else 'failed'}")
        except ImportError:
            logger.warning("Database integration not available for timing filter")
            self.db = None
            self.database_available = False
        
        # Initialize supporting services (simplified for now)
        self.growing_season_service = None
        self.regional_adaptation_service = None
        
        # Initialize timing calculation engines
        self._initialize_timing_calculators()
        
        logger.info("Timing-based variety filter initialized successfully")
    
    def _initialize_timing_calculators(self):
        """Initialize timing calculation engines and algorithms."""
        self.season_length_calculator = SeasonLengthCalculator()
        self.planting_window_analyzer = PlantingWindowAnalyzer()
        self.harvest_timing_optimizer = HarvestTimingOptimizer()
        self.succession_coordinator = SuccessionPlantingCoordinator()
        self.gdd_calculator = GrowingDegreeDayCalculator()
        self.photoperiod_analyzer = PhotoperiodResponseAnalyzer()
    
    async def filter_varieties_by_timing(
        self,
        varieties: List[EnhancedCropVariety],
        timing_criteria: TimingFilterCriteria,
        location: LocationData,
        crop_name: str
    ) -> List[TimingCompatibilityScore]:
        """
        Filter varieties based on sophisticated timing criteria.
        
        Args:
            varieties: List of crop varieties to evaluate
            timing_criteria: Timing-based filtering criteria
            location: Geographic location data
            crop_name: Name of the crop being evaluated
            
        Returns:
            List of timing compatibility scores for each variety
        """
        logger.info(f"Filtering {len(varieties)} varieties by timing criteria for {crop_name}")
        
        compatibility_scores = []
        
        for variety in varieties:
            try:
                score = await self._evaluate_variety_timing_compatibility(
                    variety, timing_criteria, location, crop_name
                )
                compatibility_scores.append(score)
            except Exception as e:
                logger.error(f"Error evaluating timing for variety {variety.variety_name}: {e}")
                continue
        
        # Sort by overall compatibility score (descending)
        compatibility_scores.sort(key=lambda x: x.overall_score, reverse=True)
        
        logger.info(f"Completed timing evaluation for {len(compatibility_scores)} varieties")
        return compatibility_scores
    
    async def _evaluate_variety_timing_compatibility(
        self,
        variety: EnhancedCropVariety,
        timing_criteria: TimingFilterCriteria,
        location: LocationData,
        crop_name: str
    ) -> TimingCompatibilityScore:
        """Evaluate timing compatibility for a single variety."""
        
        # Calculate individual component scores
        season_length_score, season_analysis = await self._evaluate_season_length_compatibility(
            variety, timing_criteria, location
        )
        
        planting_window_score, planting_analysis = await self._evaluate_planting_window_compatibility(
            variety, timing_criteria, location
        )
        
        harvest_timing_score, harvest_analysis = await self._evaluate_harvest_timing_compatibility(
            variety, timing_criteria, location
        )
        
        # Optional evaluations
        succession_score = None
        succession_analysis = None
        if timing_criteria.succession_planting_needed:
            succession_score, succession_analysis = await self._evaluate_succession_compatibility(
                variety, timing_criteria, location
            )
        
        gdd_score = None
        gdd_analysis = None
        if timing_criteria.target_growing_degree_days:
            gdd_score, gdd_analysis = await self._evaluate_gdd_compatibility(
                variety, timing_criteria, location
            )
        
        photoperiod_score = None
        photoperiod_analysis = None
        if timing_criteria.photoperiod_sensitive is not None:
            photoperiod_score, photoperiod_analysis = await self._evaluate_photoperiod_compatibility(
                variety, timing_criteria, location
            )
        
        # Calculate overall score
        overall_score = self._calculate_overall_timing_score(
            season_length_score, planting_window_score, harvest_timing_score,
            succession_score, gdd_score, photoperiod_score
        )
        
        # Determine compatibility level
        compatibility_level = self._determine_compatibility_level(overall_score)
        
        # Generate recommendations and risk factors
        recommendations, risk_factors, optimizations = self._generate_timing_recommendations(
            variety, timing_criteria, season_analysis, planting_analysis, harvest_analysis,
            succession_analysis, gdd_analysis, photoperiod_analysis
        )
        
        return TimingCompatibilityScore(
            variety_id=str(variety.id),
            variety_name=variety.variety_name,
            overall_score=overall_score,
            compatibility_level=compatibility_level,
            season_length_score=season_length_score,
            planting_window_score=planting_window_score,
            harvest_timing_score=harvest_timing_score,
            succession_score=succession_score,
            gdd_compatibility_score=gdd_score,
            photoperiod_score=photoperiod_score,
            season_length_analysis=season_analysis,
            planting_window_analysis=planting_analysis,
            harvest_timing_analysis=harvest_analysis,
            succession_analysis=succession_analysis,
            gdd_analysis=gdd_analysis,
            photoperiod_analysis=photoperiod_analysis,
            timing_recommendations=recommendations,
            risk_factors=risk_factors,
            optimization_suggestions=optimizations
        )
    
    async def _evaluate_season_length_compatibility(
        self,
        variety: EnhancedCropVariety,
        timing_criteria: TimingFilterCriteria,
        location: LocationData
    ) -> Tuple[float, Dict[str, Any]]:
        """Evaluate season length compatibility for a variety."""
        
        # Get variety's maturity requirements
        variety_maturity_days = variety.days_to_physiological_maturity or variety.relative_maturity
        if not variety_maturity_days:
            return 0.0, {"error": "No maturity data available for variety"}
        
        # Calculate available growing season
        available_days = timing_criteria.available_growing_days
        
        # Calculate compatibility score
        if timing_criteria.min_growing_days_required:
            min_required = timing_criteria.min_growing_days_required
            if variety_maturity_days < min_required:
                score = 0.0
                compatibility = "insufficient_maturity"
            else:
                # Score based on how well variety fits within available season
                excess_days = available_days - variety_maturity_days
                if excess_days >= 14:  # 2+ weeks buffer
                    score = 1.0
                    compatibility = "excellent_fit"
                elif excess_days >= 7:  # 1+ week buffer
                    score = 0.8
                    compatibility = "good_fit"
                elif excess_days >= 0:  # Fits exactly
                    score = 0.6
                    compatibility = "tight_fit"
                else:  # Doesn't fit
                    score = 0.0
                    compatibility = "insufficient_season"
        else:
            # Score based on optimal fit
            optimal_range = (available_days * 0.8, available_days * 1.2)
            if optimal_range[0] <= variety_maturity_days <= optimal_range[1]:
                score = 1.0
                compatibility = "optimal_fit"
            elif variety_maturity_days < optimal_range[0]:
                score = 0.7
                compatibility = "early_maturity"
            else:
                score = 0.3
                compatibility = "late_maturity"
        
        analysis = {
            "variety_maturity_days": variety_maturity_days,
            "available_growing_days": available_days,
            "compatibility": compatibility,
            "score": score,
            "buffer_days": available_days - variety_maturity_days if variety_maturity_days else None
        }
        
        return score, analysis
    
    async def _evaluate_planting_window_compatibility(
        self,
        variety: EnhancedCropVariety,
        timing_criteria: TimingFilterCriteria,
        location: LocationData
    ) -> Tuple[float, Dict[str, Any]]:
        """Evaluate planting window compatibility for a variety."""
        
        # Get variety's planting window requirements
        planting_populations = variety.recommended_planting_populations
        if not planting_populations:
            return 0.5, {"warning": "No planting population data available"}
        
        # Calculate planting window flexibility
        window_flexibility = self._calculate_planting_window_flexibility(variety, location)
        
        # Score based on farmer's flexibility requirements
        farmer_flexibility = timing_criteria.planting_window_flexibility
        
        if farmer_flexibility:
            flexibility_scores = {
                PlantingWindowFlexibility.VERY_FLEXIBLE: 1.0,
                PlantingWindowFlexibility.FLEXIBLE: 0.8,
                PlantingWindowFlexibility.MODERATE: 0.6,
                PlantingWindowFlexibility.NARROW: 0.4,
                PlantingWindowFlexibility.CRITICAL: 0.2
            }
            
            # Match variety flexibility to farmer requirements
            if window_flexibility == farmer_flexibility:
                score = 1.0
            elif self._flexibility_compatible(window_flexibility, farmer_flexibility):
                score = 0.8
            else:
                score = 0.4
        else:
            # Score based on general flexibility preference
            score = flexibility_scores.get(window_flexibility, 0.5)
        
        analysis = {
            "variety_flexibility": window_flexibility,
            "farmer_requirements": farmer_flexibility,
            "score": score,
            "planting_populations": len(planting_populations)
        }
        
        return score, analysis
    
    async def _evaluate_harvest_timing_compatibility(
        self,
        variety: EnhancedCropVariety,
        timing_criteria: TimingFilterCriteria,
        location: LocationData
    ) -> Tuple[float, Dict[str, Any]]:
        """Evaluate harvest timing compatibility for a variety."""
        
        # Calculate expected harvest dates
        harvest_dates = await self._calculate_harvest_dates(variety, location)
        
        if not harvest_dates:
            return 0.5, {"warning": "Could not calculate harvest dates"}
        
        # Check against farmer's harvest preferences
        score = 1.0
        constraints_met = []
        constraints_failed = []
        
        if timing_criteria.preferred_harvest_start:
            if harvest_dates["earliest"] <= timing_criteria.preferred_harvest_start:
                constraints_met.append("early_harvest_available")
            else:
                score *= 0.7
                constraints_failed.append("too_late_for_preferred_start")
        
        if timing_criteria.preferred_harvest_end:
            if harvest_dates["latest"] <= timing_criteria.preferred_harvest_end:
                constraints_met.append("harvest_before_preferred_end")
            else:
                score *= 0.5
                constraints_failed.append("harvest_extends_beyond_preferred_end")
        
        # Check harvest timing constraints
        if timing_criteria.harvest_timing_constraints:
            for constraint in timing_criteria.harvest_timing_constraints:
                if constraint == "before_frost":
                    # Check if harvest completes before first frost
                    first_frost = await self._get_first_frost_date(location)
                    if first_frost and harvest_dates["latest"] <= first_frost:
                        constraints_met.append("harvest_before_frost")
                    else:
                        score *= 0.3
                        constraints_failed.append("harvest_after_frost_risk")
        
        analysis = {
            "harvest_dates": harvest_dates,
            "constraints_met": constraints_met,
            "constraints_failed": constraints_failed,
            "score": score
        }
        
        return score, analysis
    
    async def _evaluate_succession_compatibility(
        self,
        variety: EnhancedCropVariety,
        timing_criteria: TimingFilterCriteria,
        location: LocationData
    ) -> Tuple[float, Dict[str, Any]]:
        """Evaluate succession planting compatibility for a variety."""
        
        # Check if variety supports succession planting
        variety_maturity = variety.days_to_physiological_maturity or variety.relative_maturity
        if not variety_maturity:
            return 0.0, {"error": "No maturity data for succession evaluation"}
        
        # Calculate if variety fits in succession schedule
        if timing_criteria.succession_interval_days:
            if variety_maturity <= timing_criteria.succession_interval_days:
                score = 1.0
                compatibility = "excellent_succession_fit"
            elif variety_maturity <= timing_criteria.succession_interval_days * 1.2:
                score = 0.8
                compatibility = "good_succession_fit"
            else:
                score = 0.3
                compatibility = "poor_succession_fit"
        else:
            # General succession suitability
            if variety_maturity <= 90:  # Short season varieties
                score = 1.0
                compatibility = "excellent_succession_fit"
            elif variety_maturity <= 120:  # Medium season varieties
                score = 0.7
                compatibility = "moderate_succession_fit"
            else:
                score = 0.3
                compatibility = "poor_succession_fit"
        
        analysis = {
            "variety_maturity_days": variety_maturity,
            "succession_interval": timing_criteria.succession_interval_days,
            "compatibility": compatibility,
            "score": score
        }
        
        return score, analysis
    
    async def _evaluate_gdd_compatibility(
        self,
        variety: EnhancedCropVariety,
        timing_criteria: TimingFilterCriteria,
        location: LocationData
    ) -> Tuple[float, Dict[str, Any]]:
        """Evaluate growing degree day compatibility for a variety."""
        
        # Calculate variety's GDD requirements
        variety_gdd = await self._calculate_variety_gdd_requirements(variety, location)
        
        if not variety_gdd:
            return 0.5, {"warning": "Could not calculate variety GDD requirements"}
        
        target_gdd = timing_criteria.target_growing_degree_days
        tolerance = timing_criteria.gdd_tolerance_percent / 100.0
        
        # Calculate compatibility
        gdd_difference = abs(variety_gdd - target_gdd)
        max_tolerance = target_gdd * tolerance
        
        if gdd_difference <= max_tolerance:
            score = 1.0 - (gdd_difference / max_tolerance) * 0.5
            compatibility = "excellent_gdd_match"
        else:
            score = 0.3
            compatibility = "poor_gdd_match"
        
        analysis = {
            "variety_gdd_requirements": variety_gdd,
            "target_gdd": target_gdd,
            "gdd_difference": gdd_difference,
            "tolerance_percent": timing_criteria.gdd_tolerance_percent,
            "compatibility": compatibility,
            "score": score
        }
        
        return score, analysis
    
    async def _evaluate_photoperiod_compatibility(
        self,
        variety: EnhancedCropVariety,
        timing_criteria: TimingFilterCriteria,
        location: LocationData
    ) -> Tuple[float, Dict[str, Any]]:
        """Evaluate photoperiod response compatibility for a variety."""
        
        # Get variety's photoperiod sensitivity
        variety_photoperiod = await self._get_variety_photoperiod_response(variety)
        
        if not variety_photoperiod:
            return 0.5, {"warning": "No photoperiod data available"}
        
        # Calculate location's day length patterns
        location_day_lengths = await self._calculate_location_day_lengths(location)
        
        # Evaluate compatibility
        if timing_criteria.photoperiod_sensitive:
            if variety_photoperiod["sensitive"]:
                # Check if day length requirements are met
                min_hours, max_hours = timing_criteria.day_length_requirements or (12, 16)
                if min_hours <= location_day_lengths["average"] <= max_hours:
                    score = 1.0
                    compatibility = "photoperiod_requirements_met"
                else:
                    score = 0.4
                    compatibility = "photoperiod_requirements_not_met"
            else:
                score = 0.7
                compatibility = "variety_not_photoperiod_sensitive"
        else:
            if not variety_photoperiod["sensitive"]:
                score = 1.0
                compatibility = "both_not_photoperiod_sensitive"
            else:
                score = 0.6
                compatibility = "variety_photoperiod_sensitive_but_not_required"
        
        analysis = {
            "variety_photoperiod": variety_photoperiod,
            "location_day_lengths": location_day_lengths,
            "farmer_requirements": {
                "photoperiod_sensitive": timing_criteria.photoperiod_sensitive,
                "day_length_requirements": timing_criteria.day_length_requirements
            },
            "compatibility": compatibility,
            "score": score
        }
        
        return score, analysis
    
    def _calculate_overall_timing_score(
        self,
        season_length_score: float,
        planting_window_score: float,
        harvest_timing_score: float,
        succession_score: Optional[float] = None,
        gdd_score: Optional[float] = None,
        photoperiod_score: Optional[float] = None
    ) -> float:
        """Calculate overall timing compatibility score."""
        
        # Weight the scores based on importance
        weights = {
            "season_length": 0.35,
            "planting_window": 0.25,
            "harvest_timing": 0.25,
            "succession": 0.10,
            "gdd": 0.05,
            "photoperiod": 0.05
        }
        
        total_score = (
            season_length_score * weights["season_length"] +
            planting_window_score * weights["planting_window"] +
            harvest_timing_score * weights["harvest_timing"]
        )
        
        if succession_score is not None:
            total_score += succession_score * weights["succession"]
        
        if gdd_score is not None:
            total_score += gdd_score * weights["gdd"]
        
        if photoperiod_score is not None:
            total_score += photoperiod_score * weights["photoperiod"]
        
        return min(max(total_score, 0.0), 1.0)
    
    def _determine_compatibility_level(self, overall_score: float) -> SeasonLengthCompatibility:
        """Determine overall compatibility level based on score."""
        if overall_score >= 0.9:
            return SeasonLengthCompatibility.EXCELLENT
        elif overall_score >= 0.7:
            return SeasonLengthCompatibility.GOOD
        elif overall_score >= 0.5:
            return SeasonLengthCompatibility.MARGINAL
        elif overall_score >= 0.3:
            return SeasonLengthCompatibility.POOR
        else:
            return SeasonLengthCompatibility.INCOMPATIBLE
    
    def _generate_timing_recommendations(
        self,
        variety: EnhancedCropVariety,
        timing_criteria: TimingFilterCriteria,
        season_analysis: Dict[str, Any],
        planting_analysis: Dict[str, Any],
        harvest_analysis: Dict[str, Any],
        succession_analysis: Optional[Dict[str, Any]],
        gdd_analysis: Optional[Dict[str, Any]],
        photoperiod_analysis: Optional[Dict[str, Any]]
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate timing recommendations, risk factors, and optimizations."""
        
        recommendations = []
        risk_factors = []
        optimizations = []
        
        # Season length recommendations
        if season_analysis.get("score", 0) < 0.7:
            if season_analysis.get("compatibility") == "insufficient_season":
                risk_factors.append("Variety may not reach maturity before season ends")
                optimizations.append("Consider earlier planting or shorter-season variety")
            elif season_analysis.get("compatibility") == "tight_fit":
                risk_factors.append("Minimal buffer for weather delays")
                recommendations.append("Monitor weather closely and plant as early as possible")
        
        # Planting window recommendations
        if planting_analysis.get("score", 0) < 0.7:
            recommendations.append("Ensure precise planting timing for optimal results")
            if planting_analysis.get("variety_flexibility") == PlantingWindowFlexibility.CRITICAL:
                risk_factors.append("Very narrow planting window requires careful timing")
        
        # Harvest timing recommendations
        if harvest_analysis.get("score", 0) < 0.7:
            if "harvest_after_frost_risk" in harvest_analysis.get("constraints_failed", []):
                risk_factors.append("Harvest may extend into frost risk period")
                optimizations.append("Consider earlier maturing variety or earlier planting")
        
        # Succession recommendations
        if succession_analysis and succession_analysis.get("score", 0) < 0.7:
            recommendations.append("Variety may not be optimal for succession planting")
            optimizations.append("Consider shorter-season variety for succession")
        
        return recommendations, risk_factors, optimizations
    
    # Helper methods for timing calculations
    def _calculate_planting_window_flexibility(self, variety: EnhancedCropVariety, location: LocationData) -> PlantingWindowFlexibility:
        """Calculate planting window flexibility for a variety."""
        # This would integrate with the planting date service
        # For now, return a default based on variety characteristics
        maturity_days = variety.days_to_physiological_maturity or variety.relative_maturity
        
        if maturity_days and maturity_days <= 90:
            return PlantingWindowFlexibility.VERY_FLEXIBLE
        elif maturity_days and maturity_days <= 120:
            return PlantingWindowFlexibility.FLEXIBLE
        elif maturity_days and maturity_days <= 150:
            return PlantingWindowFlexibility.MODERATE
        else:
            return PlantingWindowFlexibility.NARROW
    
    def _flexibility_compatible(self, variety_flexibility: PlantingWindowFlexibility, farmer_flexibility: PlantingWindowFlexibility) -> bool:
        """Check if variety flexibility is compatible with farmer requirements."""
        flexibility_order = [
            PlantingWindowFlexibility.VERY_FLEXIBLE,
            PlantingWindowFlexibility.FLEXIBLE,
            PlantingWindowFlexibility.MODERATE,
            PlantingWindowFlexibility.NARROW,
            PlantingWindowFlexibility.CRITICAL
        ]
        
        variety_index = flexibility_order.index(variety_flexibility)
        farmer_index = flexibility_order.index(farmer_flexibility)
        
        # Variety can be more flexible than required, but not less
        return variety_index <= farmer_index
    
    async def _calculate_harvest_dates(self, variety: EnhancedCropVariety, location: LocationData) -> Optional[Dict[str, date]]:
        """Calculate expected harvest dates for a variety."""
        # This would integrate with the growing season service
        # For now, return a placeholder
        return {
            "earliest": date.today() + timedelta(days=90),
            "typical": date.today() + timedelta(days=105),
            "latest": date.today() + timedelta(days=120)
        }
    
    async def _get_first_frost_date(self, location: LocationData) -> Optional[date]:
        """Get first frost date for location."""
        # This would integrate with weather/climate services
        # For now, return a placeholder
        return date.today() + timedelta(days=150)
    
    async def _calculate_variety_gdd_requirements(self, variety: EnhancedCropVariety, location: LocationData) -> Optional[int]:
        """Calculate GDD requirements for a variety."""
        # This would integrate with the growing season service
        maturity_days = variety.days_to_physiological_maturity or variety.relative_maturity
        if maturity_days:
            # Rough estimate: 15 GDD per day
            return maturity_days * 15
        return None
    
    async def _get_variety_photoperiod_response(self, variety: EnhancedCropVariety) -> Optional[Dict[str, Any]]:
        """Get photoperiod response data for a variety."""
        # This would integrate with variety characteristics database
        # For now, return a placeholder
        return {
            "sensitive": False,
            "critical_day_length": None,
            "response_type": "day_neutral"
        }
    
    async def _calculate_location_day_lengths(self, location: LocationData) -> Dict[str, float]:
        """Calculate day length patterns for location."""
        # This would integrate with astronomical calculations
        # For now, return a placeholder
        return {
            "average": 14.5,
            "summer_max": 16.0,
            "winter_min": 9.0
        }


# Supporting calculation classes
class SeasonLengthCalculator:
    """Calculator for season length compatibility."""
    pass


class PlantingWindowAnalyzer:
    """Analyzer for planting window flexibility."""
    pass


class HarvestTimingOptimizer:
    """Optimizer for harvest timing coordination."""
    pass


class SuccessionPlantingCoordinator:
    """Coordinator for succession planting scenarios."""
    pass


class GrowingDegreeDayCalculator:
    """Calculator for growing degree day requirements."""
    pass


class PhotoperiodResponseAnalyzer:
    """Analyzer for photoperiod response compatibility."""
    pass