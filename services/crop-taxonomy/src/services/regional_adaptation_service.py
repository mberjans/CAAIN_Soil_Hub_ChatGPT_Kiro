"""
Regional Adaptation Service

Service for analyzing crop and variety adaptation to specific regions,
climate zones, and local growing conditions with seasonal timing optimization.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, date, timedelta
from uuid import UUID
from dataclasses import dataclass

try:
    from ..models.crop_variety_models import (
        CropRegionalAdaptation,
        RegionalAdaptationRequest,
        RegionalAdaptationResponse,
        SeasonalTiming,
        RegionalPerformanceData,
        AdaptationLevel,
        RiskLevel,
        AdaptationStrategy
    )
    from ..models.crop_taxonomy_models import (
        ComprehensiveCropData,
        CropClimateAdaptations,
        ClimateZone,
        SoilType
    )
    from ..models.service_models import ConfidenceLevel
except ImportError:
    from models.crop_variety_models import (
        CropRegionalAdaptation,
        RegionalAdaptationRequest,
        RegionalAdaptationResponse,
        SeasonalTiming,
        RegionalPerformanceData,
        AdaptationLevel,
        RiskLevel,
        AdaptationStrategy
    )
    from models.crop_taxonomy_models import (
        ComprehensiveCropData,
        CropClimateAdaptations,
        ClimateZone,
        SoilType
    )
    from models.service_models import ConfidenceLevel


logger = logging.getLogger(__name__)


@dataclass
class ClimateData:
    """Regional climate data for adaptation analysis."""
    average_temperature: float
    temperature_range: Tuple[float, float]
    annual_precipitation: float
    precipitation_pattern: str
    frost_free_days: int
    growing_degree_days: int
    humidity_levels: Tuple[float, float]
    wind_patterns: Dict[str, Any]


@dataclass
class SoilConditions:
    """Regional soil conditions for adaptation analysis."""
    dominant_soil_types: List[str]
    ph_range: Tuple[float, float]
    organic_matter_levels: Tuple[float, float]
    drainage_characteristics: List[str]
    erosion_risk: str
    fertility_status: Dict[str, Any]


@dataclass
class RegionalConstraints:
    """Regional agricultural constraints and opportunities."""
    water_availability: str
    pest_pressure: Dict[str, int]
    disease_pressure: Dict[str, int]
    market_access: str
    infrastructure_quality: str
    labor_availability: str
    regulatory_constraints: List[str]


class RegionalAdaptationService:
    """
    Service for comprehensive regional adaptation analysis including
    climate matching, soil compatibility, and seasonal timing optimization.
    """

    def __init__(self, database_url: Optional[str] = None):
        """Initialize the regional adaptation service with database integration."""
        try:
            from ..database.crop_taxonomy_db import CropTaxonomyDatabase
            self.db = CropTaxonomyDatabase(database_url)
            self.database_available = self.db.test_connection()
            logger.info(f"Regional service database connection: {'successful' if self.database_available else 'failed'}")
        except ImportError:
            logger.warning("Database integration not available for regional service")
            self.db = None
            self.database_available = False
            
        self.climate_models = {}
        self.adaptation_algorithms = {}
        self._initialize_regional_data()

    def _initialize_regional_data(self):
        """Initialize regional climate and adaptation data."""
        # Regional climate zone mappings
        self.climate_zones = {
            ClimateZone.TEMPERATE_CONTINENTAL: {
                "temperature_range": (-20, 30),
                "precipitation_range": (400, 800),
                "growing_season": (120, 180),
                "frost_risk": "high"
            },
            ClimateZone.TEMPERATE_OCEANIC: {
                "temperature_range": (5, 25),
                "precipitation_range": (600, 1200),
                "growing_season": (150, 220),
                "frost_risk": "moderate"
            },
            ClimateZone.HUMID_SUBTROPICAL: {
                "temperature_range": (10, 35),
                "precipitation_range": (800, 1500),
                "growing_season": (180, 270),
                "frost_risk": "low"
            },
            ClimateZone.SEMI_ARID: {
                "temperature_range": (-5, 40),
                "precipitation_range": (200, 600),
                "growing_season": (100, 200),
                "frost_risk": "variable"
            }
        }

        # Adaptation scoring weights
        self.adaptation_weights = {
            "climate_match": 0.35,
            "soil_compatibility": 0.25,
            "seasonal_timing": 0.20,
            "risk_assessment": 0.10,
            "market_factors": 0.10
        }

    async def analyze_regional_adaptation(
        self, 
        request: RegionalAdaptationRequest
    ) -> RegionalAdaptationResponse:
        """
        Analyze crop/variety adaptation to specific regional conditions.
        
        Args:
            request: Regional adaptation analysis request
            
        Returns:
            Comprehensive adaptation analysis with recommendations
        """
        try:
            # Get regional environmental data
            regional_data = await self._get_regional_data(request.region_id, request.coordinates)
            
            # Analyze climate compatibility
            climate_analysis = await self._analyze_climate_compatibility(
                request.crop_data, regional_data
            )
            
            # Analyze soil compatibility
            soil_analysis = await self._analyze_soil_compatibility(
                request.crop_data, regional_data
            )
            
            # Optimize seasonal timing
            timing_analysis = await self._optimize_seasonal_timing(
                request.crop_data, regional_data, request.target_season
            )
            
            # Assess regional risks
            risk_analysis = await self._assess_regional_risks(
                request.crop_data, regional_data
            )
            
            # Calculate overall adaptation score
            overall_adaptation = await self._calculate_adaptation_score(
                climate_analysis, soil_analysis, timing_analysis, risk_analysis
            )
            
            # Generate adaptation strategies
            adaptation_strategies = await self._generate_regional_strategies(
                request.crop_data, regional_data, overall_adaptation
            )
            
            # Create adaptation recommendation
            regional_adaptation = CropRegionalAdaptation(
                id=UUID('12345678-1234-5678-9abc-123456789abc'),  # Would be generated
                crop_id=request.crop_data.id,
                region_id=request.region_id,
                adaptation_level=self._determine_adaptation_level(overall_adaptation["score"]),
                climate_suitability=climate_analysis["suitability"],
                soil_compatibility=soil_analysis["compatibility"],
                seasonal_timing=timing_analysis["optimal_timing"],
                performance_data=RegionalPerformanceData(
                    historical_yield_data=regional_data.get("historical_yields", {}),
                    success_rate=overall_adaptation["score"] * 100,
                    performance_factors=overall_adaptation["key_factors"],
                    seasonal_variations=timing_analysis.get("seasonal_variations", {})
                ),
                risk_factors=risk_analysis["risk_factors"],
                adaptation_strategies=adaptation_strategies,
                recommended_practices=await self._generate_regional_practices(
                    request.crop_data, regional_data
                ),
                last_updated=datetime.utcnow()
            )
            
            return RegionalAdaptationResponse(
                regional_adaptation=regional_adaptation,
                adaptation_score=overall_adaptation["score"],
                confidence_level=self._determine_confidence_level(overall_adaptation["score"]),
                detailed_analysis={
                    "climate_analysis": climate_analysis,
                    "soil_analysis": soil_analysis,
                    "timing_analysis": timing_analysis,
                    "risk_analysis": risk_analysis
                },
                recommendations=await self._generate_final_recommendations(
                    regional_adaptation, overall_adaptation
                )
            )

        except Exception as e:
            logger.error(f"Error in regional adaptation analysis: {str(e)}")
            return RegionalAdaptationResponse(
                regional_adaptation=None,
                adaptation_score=0.0,
                confidence_level=ConfidenceLevel.LOW,
                error_message=str(e)
            )

    async def _get_regional_data(
        self, 
        region_id: str, 
        coordinates: Optional[Tuple[float, float]]
    ) -> Dict[str, Any]:
        """Get comprehensive regional data for analysis."""
        # This would query actual regional databases
        # For now, return sample data based on coordinates or region
        
        if coordinates:
            latitude, longitude = coordinates
            regional_data = await self._generate_regional_data_from_coordinates(latitude, longitude)
        else:
            regional_data = await self._get_cached_regional_data(region_id)
            
        return regional_data

    async def _generate_regional_data_from_coordinates(
        self, 
        latitude: float, 
        longitude: float
    ) -> Dict[str, Any]:
        """Generate regional data based on geographic coordinates."""
        
        # Determine climate zone from latitude
        if abs(latitude) < 23.5:
            climate_zone = ClimateZone.TROPICAL
        elif abs(latitude) < 40:
            climate_zone = ClimateZone.HUMID_SUBTROPICAL
        elif abs(latitude) < 60:
            climate_zone = ClimateZone.TEMPERATE_CONTINENTAL
        else:
            climate_zone = ClimateZone.SUBARCTIC
            
        zone_data = self.climate_zones.get(climate_zone, self.climate_zones[ClimateZone.TEMPERATE_CONTINENTAL])
        
        return {
            "climate": ClimateData(
                average_temperature=(zone_data["temperature_range"][0] + zone_data["temperature_range"][1]) / 2,
                temperature_range=zone_data["temperature_range"],
                annual_precipitation=(zone_data["precipitation_range"][0] + zone_data["precipitation_range"][1]) / 2,
                precipitation_pattern="seasonal",
                frost_free_days=zone_data["growing_season"][1],
                growing_degree_days=2000,  # Estimated
                humidity_levels=(40, 70),
                wind_patterns={"prevailing": "westerly", "strength": "moderate"}
            ),
            "soil": SoilConditions(
                dominant_soil_types=["loam", "clay_loam"],
                ph_range=(6.0, 7.5),
                organic_matter_levels=(2.5, 4.0),
                drainage_characteristics=["well_drained", "moderately_well_drained"],
                erosion_risk="moderate",
                fertility_status={"nitrogen": "moderate", "phosphorus": "adequate", "potassium": "high"}
            ),
            "constraints": RegionalConstraints(
                water_availability="adequate",
                pest_pressure={"aphids": 3, "cutworms": 2, "wireworms": 2},
                disease_pressure={"rust": 3, "scab": 2, "blight": 2},
                market_access="good",
                infrastructure_quality="adequate",
                labor_availability="seasonal",
                regulatory_constraints=["pesticide_restrictions", "water_use_limits"]
            ),
            "climate_zone": climate_zone,
            "coordinates": (latitude, longitude)
        }

    async def _get_cached_regional_data(self, region_id: str) -> Dict[str, Any]:
        """Get cached regional data by region ID."""
        # This would query cached regional data
        # For now, return default temperate data
        return await self._generate_regional_data_from_coordinates(45.0, -100.0)  # Default to mid-latitude

    async def _analyze_climate_compatibility(
        self, 
        crop_data: ComprehensiveCropData, 
        regional_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze climate compatibility between crop and region."""
        
        analysis = {
            "suitability": 0.0,
            "matching_factors": [],
            "limiting_factors": [],
            "seasonal_considerations": []
        }
        
        if not crop_data.climate_adaptations:
            analysis["limiting_factors"].append("No climate adaptation data available")
            return analysis
            
        climate_data = regional_data["climate"]
        crop_climate = crop_data.climate_adaptations
        
        compatibility_scores = []
        
        # Temperature compatibility
        if crop_climate.temperature_range and climate_data.temperature_range:
            crop_temp_min, crop_temp_max = crop_climate.temperature_range
            region_temp_min, region_temp_max = climate_data.temperature_range
            
            # Check for overlap
            temp_overlap_min = max(crop_temp_min, region_temp_min)
            temp_overlap_max = min(crop_temp_max, region_temp_max)
            
            if temp_overlap_max > temp_overlap_min:
                temp_overlap = temp_overlap_max - temp_overlap_min
                crop_temp_range = crop_temp_max - crop_temp_min
                temp_compatibility = temp_overlap / crop_temp_range
                compatibility_scores.append(temp_compatibility)
                
                if temp_compatibility > 0.8:
                    analysis["matching_factors"].append("Excellent temperature compatibility")
                elif temp_compatibility > 0.6:
                    analysis["matching_factors"].append("Good temperature range overlap")
                else:
                    analysis["limiting_factors"].append("Limited temperature compatibility")
            else:
                analysis["limiting_factors"].append("No temperature range overlap")
                compatibility_scores.append(0.0)
                
        # Precipitation compatibility
        if crop_climate.precipitation_range:
            crop_precip_min, crop_precip_max = crop_climate.precipitation_range
            region_precip = climate_data.annual_precipitation
            
            if crop_precip_min <= region_precip <= crop_precip_max:
                precip_compatibility = 1.0
                analysis["matching_factors"].append("Optimal precipitation levels")
            elif region_precip < crop_precip_min:
                precip_deficit = (crop_precip_min - region_precip) / crop_precip_min
                precip_compatibility = max(0.0, 1.0 - precip_deficit)
                analysis["limiting_factors"].append("Below optimal precipitation")
            else:
                precip_excess = (region_precip - crop_precip_max) / crop_precip_max
                precip_compatibility = max(0.0, 1.0 - precip_excess * 0.5)  # Excess less limiting than deficit
                analysis["seasonal_considerations"].append("Manage excess moisture")
                
            compatibility_scores.append(precip_compatibility)
            
        # Growing season compatibility
        if crop_climate.growing_season_length:
            regional_growing_season = climate_data.frost_free_days
            if regional_growing_season >= crop_climate.growing_season_length:
                season_compatibility = 1.0
                analysis["matching_factors"].append("Adequate growing season length")
            else:
                season_deficit = (crop_climate.growing_season_length - regional_growing_season) / crop_climate.growing_season_length
                season_compatibility = max(0.0, 1.0 - season_deficit)
                analysis["limiting_factors"].append("Short growing season")
                
            compatibility_scores.append(season_compatibility)
            
        # Calculate overall climate suitability
        analysis["suitability"] = sum(compatibility_scores) / len(compatibility_scores) if compatibility_scores else 0.0
        
        return analysis

    async def _analyze_soil_compatibility(
        self, 
        crop_data: ComprehensiveCropData, 
        regional_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze soil compatibility between crop and region."""
        
        analysis = {
            "compatibility": 0.0,
            "suitable_soils": [],
            "soil_limitations": [],
            "management_recommendations": []
        }
        
        if not crop_data.soil_requirements:
            analysis["soil_limitations"].append("No soil requirements data available")
            return analysis
            
        soil_data = regional_data["soil"]
        crop_soil = crop_data.soil_requirements
        
        compatibility_scores = []
        
        # pH compatibility
        if crop_soil.ph_range and soil_data.ph_range:
            crop_ph_min, crop_ph_max = crop_soil.ph_range
            soil_ph_min, soil_ph_max = soil_data.ph_range
            
            # Check for pH overlap
            ph_overlap_min = max(crop_ph_min, soil_ph_min)
            ph_overlap_max = min(crop_ph_max, soil_ph_max)
            
            if ph_overlap_max > ph_overlap_min:
                ph_overlap = ph_overlap_max - ph_overlap_min
                crop_ph_range = crop_ph_max - crop_ph_min
                ph_compatibility = ph_overlap / crop_ph_range
                compatibility_scores.append(ph_compatibility)
                
                if ph_compatibility > 0.8:
                    analysis["suitable_soils"].append("Excellent pH compatibility")
                elif ph_compatibility > 0.6:
                    analysis["suitable_soils"].append("Good pH range")
                else:
                    analysis["soil_limitations"].append("pH adjustment may be needed")
            else:
                analysis["soil_limitations"].append("pH incompatibility")
                analysis["management_recommendations"].append("Soil pH amendment required")
                compatibility_scores.append(0.2)  # Still possible with amendments
                
        # Soil texture compatibility
        if crop_soil.preferred_textures and soil_data.dominant_soil_types:
            texture_matches = set(crop_soil.preferred_textures) & set(soil_data.dominant_soil_types)
            if texture_matches:
                texture_compatibility = len(texture_matches) / len(crop_soil.preferred_textures)
                compatibility_scores.append(texture_compatibility)
                analysis["suitable_soils"].extend(list(texture_matches))
            else:
                compatibility_scores.append(0.3)  # Partial compatibility with management
                analysis["soil_limitations"].append("Suboptimal soil texture")
                analysis["management_recommendations"].append("Consider soil structure improvements")
                
        # Drainage compatibility
        if crop_soil.drainage_requirements and soil_data.drainage_characteristics:
            drainage_matches = set(crop_soil.drainage_requirements) & set(soil_data.drainage_characteristics)
            if drainage_matches:
                drainage_compatibility = len(drainage_matches) / len(crop_soil.drainage_requirements)
                compatibility_scores.append(drainage_compatibility)
            else:
                compatibility_scores.append(0.4)
                analysis["soil_limitations"].append("Drainage concerns")
                analysis["management_recommendations"].append("Drainage management may be required")
                
        # Calculate overall soil compatibility
        analysis["compatibility"] = sum(compatibility_scores) / len(compatibility_scores) if compatibility_scores else 0.0
        
        return analysis

    async def _optimize_seasonal_timing(
        self, 
        crop_data: ComprehensiveCropData, 
        regional_data: Dict[str, Any], 
        target_season: Optional[str]
    ) -> Dict[str, Any]:
        """Optimize seasonal timing for the crop in the region."""
        
        analysis = {
            "optimal_timing": None,
            "planting_window": None,
            "harvest_window": None,
            "seasonal_variations": {},
            "timing_risks": []
        }
        
        climate_data = regional_data["climate"]
        
        # Calculate optimal planting date based on frost risk and temperature
        frost_free_start = date(datetime.now().year, 4, 15)  # Estimated frost-free date
        soil_workable = date(datetime.now().year, 4, 1)  # Estimated soil workable date
        
        # Determine planting window
        if crop_data.agricultural_classification and crop_data.agricultural_classification.maturity_days_range:
            min_maturity, max_maturity = crop_data.agricultural_classification.maturity_days_range
            avg_maturity = (min_maturity + max_maturity) / 2
            
            # Calculate optimal planting date to avoid frost at harvest
            fall_frost = date(datetime.now().year, 10, 15)  # Estimated fall frost
            latest_planting = fall_frost - timedelta(days=int(avg_maturity + 14))  # Safety buffer
            
            # Optimal planting window
            planting_start = max(frost_free_start, soil_workable)
            planting_end = min(latest_planting, date(datetime.now().year, 6, 15))  # Latest reasonable planting
            
            if planting_start <= planting_end:
                analysis["planting_window"] = (planting_start, planting_end)
                
                # Calculate harvest window
                harvest_start = planting_start + timedelta(days=int(min_maturity))
                harvest_end = planting_end + timedelta(days=int(max_maturity))
                analysis["harvest_window"] = (harvest_start, harvest_end)
                
                # Create optimal timing recommendation
                optimal_planting = planting_start + timedelta(days=(planting_end - planting_start).days // 2)
                optimal_harvest = optimal_planting + timedelta(days=int(avg_maturity))
                
                analysis["optimal_timing"] = SeasonalTiming(
                    planting_date_range=(planting_start, planting_end),
                    harvest_date_range=(harvest_start, harvest_end),
                    critical_growth_periods=[
                        {
                            "stage": "emergence", 
                            "date_range": (optimal_planting + timedelta(days=7), optimal_planting + timedelta(days=21)),
                            "risk_factors": ["soil_crusting", "cool_temperatures"]
                        },
                        {
                            "stage": "flowering",
                            "date_range": (optimal_planting + timedelta(days=int(avg_maturity * 0.6)), 
                                         optimal_planting + timedelta(days=int(avg_maturity * 0.8))),
                            "risk_factors": ["heat_stress", "drought_stress"]
                        }
                    ],
                    seasonal_management_calendar=await self._generate_management_calendar(
                        optimal_planting, int(avg_maturity)
                    )
                )
            else:
                analysis["timing_risks"].append("Insufficient growing season length")
                
        return analysis

    async def _generate_management_calendar(
        self, 
        planting_date: date, 
        maturity_days: int
    ) -> Dict[str, List[str]]:
        """Generate seasonal management calendar."""
        
        calendar = {}
        
        # Pre-planting (2-4 weeks before)
        pre_plant_start = planting_date - timedelta(days=28)
        calendar[f"{pre_plant_start.strftime('%B')} (Pre-plant)"] = [
            "Soil testing and fertility planning",
            "Field preparation and cultivation",
            "Seed acquisition and treatment"
        ]
        
        # Planting period
        calendar[f"{planting_date.strftime('%B')} (Planting)"] = [
            "Soil temperature monitoring",
            "Planting operation",
            "Post-planting field monitoring"
        ]
        
        # Mid-season (50% of maturity period)
        mid_season = planting_date + timedelta(days=int(maturity_days * 0.5))
        calendar[f"{mid_season.strftime('%B')} (Mid-season)"] = [
            "Disease and pest monitoring",
            "Nutrient management",
            "Weed control assessment"
        ]
        
        # Pre-harvest (90% of maturity period)
        pre_harvest = planting_date + timedelta(days=int(maturity_days * 0.9))
        calendar[f"{pre_harvest.strftime('%B')} (Pre-harvest)"] = [
            "Maturity monitoring",
            "Harvest equipment preparation",
            "Market timing decisions"
        ]
        
        return calendar

    async def _assess_regional_risks(
        self, 
        crop_data: ComprehensiveCropData, 
        regional_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess regional production risks."""
        
        analysis = {
            "risk_factors": [],
            "overall_risk_level": RiskLevel.MODERATE,
            "mitigation_strategies": []
        }
        
        constraints = regional_data["constraints"]
        
        # Assess pest pressure
        if constraints.pest_pressure:
            high_pressure_pests = [pest for pest, level in constraints.pest_pressure.items() if level >= 4]
            if high_pressure_pests:
                analysis["risk_factors"].append({
                    "category": "pest_pressure",
                    "level": RiskLevel.HIGH,
                    "description": f"High pest pressure from: {', '.join(high_pressure_pests)}"
                })
                analysis["mitigation_strategies"].append("Implement integrated pest management program")
                
        # Assess disease pressure
        if constraints.disease_pressure:
            high_pressure_diseases = [disease for disease, level in constraints.disease_pressure.items() if level >= 4]
            if high_pressure_diseases:
                analysis["risk_factors"].append({
                    "category": "disease_pressure", 
                    "level": RiskLevel.HIGH,
                    "description": f"High disease pressure from: {', '.join(high_pressure_diseases)}"
                })
                analysis["mitigation_strategies"].append("Preventive disease management required")
                
        # Assess water availability
        if constraints.water_availability in ["limited", "scarce"]:
            analysis["risk_factors"].append({
                "category": "water_stress",
                "level": RiskLevel.HIGH if constraints.water_availability == "scarce" else RiskLevel.MODERATE,
                "description": f"Water availability is {constraints.water_availability}"
            })
            analysis["mitigation_strategies"].append("Water conservation and efficient irrigation")
            
        # Assess market access
        if constraints.market_access in ["poor", "limited"]:
            analysis["risk_factors"].append({
                "category": "market_risk",
                "level": RiskLevel.MODERATE,
                "description": "Limited market access may impact profitability"
            })
            analysis["mitigation_strategies"].append("Secure marketing contracts in advance")
            
        # Determine overall risk level
        high_risks = sum(1 for risk in analysis["risk_factors"] if risk["level"] == RiskLevel.HIGH)
        moderate_risks = sum(1 for risk in analysis["risk_factors"] if risk["level"] == RiskLevel.MODERATE)
        
        if high_risks >= 2:
            analysis["overall_risk_level"] = RiskLevel.HIGH
        elif high_risks >= 1 or moderate_risks >= 3:
            analysis["overall_risk_level"] = RiskLevel.MODERATE
        else:
            analysis["overall_risk_level"] = RiskLevel.LOW
            
        return analysis

    async def _calculate_adaptation_score(
        self, 
        climate_analysis: Dict[str, Any], 
        soil_analysis: Dict[str, Any],
        timing_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall regional adaptation score."""
        
        # Individual component scores
        climate_score = climate_analysis.get("suitability", 0.0)
        soil_score = soil_analysis.get("compatibility", 0.0)
        timing_score = 1.0 if timing_analysis.get("optimal_timing") else 0.3
        risk_score = self._convert_risk_to_score(risk_analysis["overall_risk_level"])
        market_score = 0.7  # Default market score (would be calculated from regional data)
        
        # Calculate weighted overall score
        overall_score = (
            climate_score * self.adaptation_weights["climate_match"] +
            soil_score * self.adaptation_weights["soil_compatibility"] +
            timing_score * self.adaptation_weights["seasonal_timing"] +
            risk_score * self.adaptation_weights["risk_assessment"] +
            market_score * self.adaptation_weights["market_factors"]
        )
        
        return {
            "score": overall_score,
            "component_scores": {
                "climate": climate_score,
                "soil": soil_score,
                "timing": timing_score,
                "risk": risk_score,
                "market": market_score
            },
            "key_factors": await self._identify_key_factors(
                climate_analysis, soil_analysis, timing_analysis, risk_analysis
            )
        }

    def _convert_risk_to_score(self, risk_level: RiskLevel) -> float:
        """Convert risk level to adaptation score (higher risk = lower score)."""
        risk_scores = {
            RiskLevel.LOW: 0.9,
            RiskLevel.MODERATE: 0.6,
            RiskLevel.HIGH: 0.3
        }
        return risk_scores.get(risk_level, 0.5)

    async def _identify_key_factors(
        self, 
        climate_analysis: Dict[str, Any],
        soil_analysis: Dict[str, Any], 
        timing_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify key factors affecting adaptation success."""
        
        key_factors = []
        
        # Climate factors
        if climate_analysis.get("suitability", 0) > 0.8:
            key_factors.append("Excellent climate compatibility")
        elif climate_analysis.get("suitability", 0) < 0.4:
            key_factors.append("Climate limitations require management")
            
        # Soil factors
        if soil_analysis.get("compatibility", 0) > 0.8:
            key_factors.append("Highly suitable soils")
        elif soil_analysis.get("compatibility", 0) < 0.4:
            key_factors.append("Soil constraints require amendments")
            
        # Timing factors
        if timing_analysis.get("optimal_timing"):
            key_factors.append("Favorable growing season timing")
        else:
            key_factors.append("Challenging seasonal timing")
            
        # Risk factors
        if risk_analysis["overall_risk_level"] == RiskLevel.LOW:
            key_factors.append("Low production risk environment")
        elif risk_analysis["overall_risk_level"] == RiskLevel.HIGH:
            key_factors.append("High risk requires intensive management")
            
        return key_factors

    async def _generate_regional_strategies(
        self, 
        crop_data: ComprehensiveCropData,
        regional_data: Dict[str, Any],
        adaptation_analysis: Dict[str, Any]
    ) -> List[AdaptationStrategy]:
        """Generate region-specific adaptation strategies."""
        
        strategies = []
        
        # Climate adaptation strategies
        if adaptation_analysis["component_scores"]["climate"] < 0.6:
            strategies.append(AdaptationStrategy(
                strategy_type="climate_adaptation",
                description="Enhance climate resilience through variety selection and timing",
                implementation_details=[
                    "Select climate-adapted varieties",
                    "Optimize planting timing for temperature",
                    "Implement water conservation practices"
                ],
                expected_benefit="Improved crop resilience to climate stress"
            ))
            
        # Soil management strategies
        if adaptation_analysis["component_scores"]["soil"] < 0.6:
            strategies.append(AdaptationStrategy(
                strategy_type="soil_management",
                description="Improve soil conditions for crop success",
                implementation_details=[
                    "Soil pH amendment based on crop requirements",
                    "Organic matter enhancement",
                    "Drainage improvement where needed"
                ],
                expected_benefit="Enhanced soil-crop compatibility"
            ))
            
        # Risk mitigation strategies
        if adaptation_analysis["component_scores"]["risk"] < 0.6:
            strategies.append(AdaptationStrategy(
                strategy_type="risk_mitigation",
                description="Comprehensive risk management program",
                implementation_details=[
                    "Integrated pest and disease management",
                    "Crop insurance evaluation",
                    "Diversification strategies"
                ],
                expected_benefit="Reduced production and financial risks"
            ))
            
        return strategies

    async def _generate_regional_practices(
        self, 
        crop_data: ComprehensiveCropData,
        regional_data: Dict[str, Any]
    ) -> List[str]:
        """Generate region-specific recommended practices."""
        
        practices = []
        
        # Basic regional practices
        practices.extend([
            "Follow local extension recommendations",
            "Adapt planting dates to local frost patterns",
            "Use locally-adapted varieties when available"
        ])
        
        # Climate-specific practices
        climate_zone = regional_data.get("climate_zone")
        if climate_zone == ClimateZone.SEMI_ARID:
            practices.extend([
                "Implement water-efficient irrigation",
                "Use drought-tolerant varieties",
                "Consider moisture conservation tillage"
            ])
        elif climate_zone == ClimateZone.HUMID_SUBTROPICAL:
            practices.extend([
                "Plan for disease pressure management",
                "Ensure adequate drainage",
                "Monitor for heat stress during flowering"
            ])
            
        # Soil-specific practices
        soil_data = regional_data["soil"]
        if "clay" in soil_data.dominant_soil_types:
            practices.append("Avoid field operations on wet clay soils")
        if soil_data.erosion_risk == "high":
            practices.append("Implement erosion control measures")
            
        return practices

    def _determine_adaptation_level(self, score: float) -> AdaptationLevel:
        """Determine adaptation level from score."""
        if score >= 0.8:
            return AdaptationLevel.EXCELLENT
        elif score >= 0.7:
            return AdaptationLevel.GOOD
        elif score >= 0.5:
            return AdaptationLevel.MODERATE
        elif score >= 0.3:
            return AdaptationLevel.CHALLENGING
        else:
            return AdaptationLevel.UNSUITABLE

    def _determine_confidence_level(self, score: float) -> ConfidenceLevel:
        """Determine confidence level from adaptation score."""
        if score >= 0.7:
            return ConfidenceLevel.HIGH
        elif score >= 0.5:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    async def _generate_final_recommendations(
        self, 
        adaptation: CropRegionalAdaptation,
        adaptation_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate final recommendations based on adaptation analysis."""
        
        recommendations = []
        
        # Overall recommendation based on adaptation level
        if adaptation.adaptation_level == AdaptationLevel.EXCELLENT:
            recommendations.append("Highly recommended for commercial production in this region")
        elif adaptation.adaptation_level == AdaptationLevel.GOOD:
            recommendations.append("Well-suited for production with standard management practices")
        elif adaptation.adaptation_level == AdaptationLevel.MODERATE:
            recommendations.append("Suitable with enhanced management and risk mitigation")
        elif adaptation.adaptation_level == AdaptationLevel.CHALLENGING:
            recommendations.append("Consider only with intensive management and risk acceptance")
        else:
            recommendations.append("Not recommended for this region without significant modifications")
            
        # Specific recommendations based on key factors
        key_factors = adaptation_analysis["key_factors"]
        for factor in key_factors:
            if "climate limitations" in factor.lower():
                recommendations.append("Focus on climate adaptation strategies and variety selection")
            elif "soil constraints" in factor.lower():
                recommendations.append("Prioritize soil improvement before crop establishment")
            elif "high risk" in factor.lower():
                recommendations.append("Implement comprehensive risk management program")
                
        return recommendations


# Create service instance with database connection
import os
regional_adaptation_service = RegionalAdaptationService(
    database_url=os.getenv('DATABASE_URL')
)