"""
Crop Response and Application Method Optimization Service.

This service implements crop response modeling for different fertilizer application methods,
providing method-specific crop response analysis, efficiency comparisons, and yield impact predictions.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime

from src.models.application_models import ApplicationMethodType, CropRequirements
from src.services.crop_integration_service import CropType, GrowthStage, CropIntegrationService

logger = logging.getLogger(__name__)


class ResponseMetric(str, Enum):
    """Crop response metrics for evaluation."""
    YIELD_RESPONSE = "yield_response"
    NUTRIENT_EFFICIENCY = "nutrient_efficiency"
    GROWTH_RATE = "growth_rate"
    STRESS_TOLERANCE = "stress_tolerance"
    QUALITY_IMPROVEMENT = "quality_improvement"


@dataclass
class CropResponseData:
    """Crop response data for a specific application method."""
    method_type: ApplicationMethodType
    crop_type: CropType
    growth_stage: GrowthStage
    
    # Response metrics (0-1 scale, where 1 is optimal)
    yield_response: float = 0.0
    nutrient_efficiency: float = 0.0
    growth_rate_response: float = 0.0
    stress_tolerance: float = 0.0
    quality_improvement: float = 0.0
    
    # Environmental factors
    weather_conditions: Dict[str, Any] = field(default_factory=dict)
    soil_conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Application parameters
    application_rate: float = 0.0
    application_timing: str = ""
    equipment_efficiency: float = 0.0
    
    # Confidence and validation
    confidence_score: float = 0.0
    data_sources: List[str] = field(default_factory=list)
    validation_status: str = "pending"


@dataclass
class MethodEffectivenessRanking:
    """Ranking of application methods by effectiveness."""
    method_type: ApplicationMethodType
    overall_score: float
    yield_impact: float
    efficiency_score: float
    cost_effectiveness: float
    environmental_score: float
    labor_efficiency: float
    
    # Detailed breakdown
    response_factors: Dict[str, float] = field(default_factory=dict)
    limitations: List[str] = field(default_factory=list)
    advantages: List[str] = field(default_factory=list)
    
    # Recommendations
    optimal_conditions: Dict[str, Any] = field(default_factory=dict)
    application_guidance: List[str] = field(default_factory=list)


@dataclass
class YieldImpactPrediction:
    """Yield impact prediction for application methods."""
    method_type: ApplicationMethodType
    crop_type: CropType
    
    # Yield predictions
    baseline_yield: float
    predicted_yield: float
    yield_increase_percent: float
    yield_range: Tuple[float, float]
    
    # Confidence and factors
    confidence: float
    contributing_factors: Dict[str, float] = field(default_factory=dict)
    risk_factors: List[str] = field(default_factory=list)
    
    # Economic impact
    revenue_impact_per_acre: float = 0.0
    cost_per_unit_yield: float = 0.0


class CropResponseService:
    """Service for crop response modeling and application method optimization."""
    
    def __init__(self):
        self.crop_integration_service = CropIntegrationService()
        self.response_database = {}
        self.effectiveness_models = {}
        self.yield_prediction_models = {}
        self._initialize_response_database()
        self._initialize_effectiveness_models()
        self._initialize_yield_prediction_models()
    
    def _initialize_response_database(self):
        """Initialize crop response database with method-specific data."""
        logger.info("Initializing crop response database")
        
        # Corn response data by application method
        self.response_database[CropType.CORN] = {
            ApplicationMethodType.BROADCAST: CropResponseData(
                method_type=ApplicationMethodType.BROADCAST,
                crop_type=CropType.CORN,
                growth_stage=GrowthStage.V6,
                yield_response=0.75,
                nutrient_efficiency=0.65,
                growth_rate_response=0.70,
                stress_tolerance=0.60,
                quality_improvement=0.55,
                confidence_score=0.85,
                data_sources=["University trials", "Extension data", "Field studies"]
            ),
            ApplicationMethodType.BAND: CropResponseData(
                method_type=ApplicationMethodType.BAND,
                crop_type=CropType.CORN,
                growth_stage=GrowthStage.V6,
                yield_response=0.90,
                nutrient_efficiency=0.85,
                growth_rate_response=0.88,
                stress_tolerance=0.80,
                quality_improvement=0.75,
                confidence_score=0.90,
                data_sources=["Precision agriculture studies", "University trials"]
            ),
            ApplicationMethodType.SIDEDRESS: CropResponseData(
                method_type=ApplicationMethodType.SIDEDRESS,
                crop_type=CropType.CORN,
                growth_stage=GrowthStage.V6,
                yield_response=0.95,
                nutrient_efficiency=0.90,
                growth_rate_response=0.92,
                stress_tolerance=0.85,
                quality_improvement=0.80,
                confidence_score=0.88,
                data_sources=["Extension recommendations", "Farmer trials"]
            ),
            ApplicationMethodType.INJECTION: CropResponseData(
                method_type=ApplicationMethodType.INJECTION,
                crop_type=CropType.CORN,
                growth_stage=GrowthStage.V6,
                yield_response=0.88,
                nutrient_efficiency=0.92,
                growth_rate_response=0.85,
                stress_tolerance=0.90,
                quality_improvement=0.78,
                confidence_score=0.82,
                data_sources=["Research trials", "Equipment studies"]
            ),
            ApplicationMethodType.FOLIAR: CropResponseData(
                method_type=ApplicationMethodType.FOLIAR,
                crop_type=CropType.CORN,
                growth_stage=GrowthStage.V6,
                yield_response=0.60,
                nutrient_efficiency=0.45,
                growth_rate_response=0.55,
                stress_tolerance=0.70,
                quality_improvement=0.65,
                confidence_score=0.75,
                data_sources=["Foliar application studies", "Micronutrient research"]
            )
        }
        
        # Soybean response data
        self.response_database[CropType.SOYBEAN] = {
            ApplicationMethodType.BROADCAST: CropResponseData(
                method_type=ApplicationMethodType.BROADCAST,
                crop_type=CropType.SOYBEAN,
                growth_stage=GrowthStage.R1,
                yield_response=0.80,
                nutrient_efficiency=0.70,
                growth_rate_response=0.75,
                stress_tolerance=0.65,
                quality_improvement=0.60,
                confidence_score=0.85,
                data_sources=["University trials", "Extension data"]
            ),
            ApplicationMethodType.BAND: CropResponseData(
                method_type=ApplicationMethodType.BAND,
                crop_type=CropType.SOYBEAN,
                growth_stage=GrowthStage.R1,
                yield_response=0.85,
                nutrient_efficiency=0.80,
                growth_rate_response=0.82,
                stress_tolerance=0.75,
                quality_improvement=0.70,
                confidence_score=0.88,
                data_sources=["Precision agriculture studies"]
            ),
            ApplicationMethodType.INJECTION: CropResponseData(
                method_type=ApplicationMethodType.INJECTION,
                crop_type=CropType.SOYBEAN,
                growth_stage=GrowthStage.R1,
                yield_response=0.82,
                nutrient_efficiency=0.85,
                growth_rate_response=0.80,
                stress_tolerance=0.85,
                quality_improvement=0.75,
                confidence_score=0.80,
                data_sources=["Research trials"]
            ),
            ApplicationMethodType.FOLIAR: CropResponseData(
                method_type=ApplicationMethodType.FOLIAR,
                crop_type=CropType.SOYBEAN,
                growth_stage=GrowthStage.R1,
                yield_response=0.70,
                nutrient_efficiency=0.50,
                growth_rate_response=0.65,
                stress_tolerance=0.75,
                quality_improvement=0.70,
                confidence_score=0.78,
                data_sources=["Foliar application studies"]
            )
        }
        
        # Wheat response data
        self.response_database[CropType.WHEAT] = {
            ApplicationMethodType.BROADCAST: CropResponseData(
                method_type=ApplicationMethodType.BROADCAST,
                crop_type=CropType.WHEAT,
                growth_stage=GrowthStage.TILLERING,
                yield_response=0.85,
                nutrient_efficiency=0.75,
                growth_rate_response=0.80,
                stress_tolerance=0.70,
                quality_improvement=0.65,
                confidence_score=0.90,
                data_sources=["University trials", "Extension data", "Farmer surveys"]
            ),
            ApplicationMethodType.BAND: CropResponseData(
                method_type=ApplicationMethodType.BAND,
                crop_type=CropType.WHEAT,
                growth_stage=GrowthStage.TILLERING,
                yield_response=0.90,
                nutrient_efficiency=0.85,
                growth_rate_response=0.88,
                stress_tolerance=0.80,
                quality_improvement=0.75,
                confidence_score=0.88,
                data_sources=["Precision agriculture studies"]
            ),
            ApplicationMethodType.INJECTION: CropResponseData(
                method_type=ApplicationMethodType.INJECTION,
                crop_type=CropType.WHEAT,
                growth_stage=GrowthStage.TILLERING,
                yield_response=0.88,
                nutrient_efficiency=0.90,
                growth_rate_response=0.85,
                stress_tolerance=0.85,
                quality_improvement=0.80,
                confidence_score=0.82,
                data_sources=["Research trials"]
            )
        }
    
    def _initialize_effectiveness_models(self):
        """Initialize effectiveness models for different application methods."""
        logger.info("Initializing effectiveness models")
        
        # Effectiveness scoring weights
        self.effectiveness_models = {
            "scoring_weights": {
                "yield_impact": 0.30,
                "nutrient_efficiency": 0.25,
                "cost_effectiveness": 0.20,
                "environmental_impact": 0.15,
                "labor_efficiency": 0.10
            },
            "method_characteristics": {
                ApplicationMethodType.BROADCAST: {
                    "cost_per_acre": 15.0,
                    "labor_hours_per_acre": 0.5,
                    "equipment_complexity": "low",
                    "precision_level": "low",
                    "environmental_risk": "medium"
                },
                ApplicationMethodType.BAND: {
                    "cost_per_acre": 25.0,
                    "labor_hours_per_acre": 0.8,
                    "equipment_complexity": "medium",
                    "precision_level": "high",
                    "environmental_risk": "low"
                },
                ApplicationMethodType.SIDEDRESS: {
                    "cost_per_acre": 30.0,
                    "labor_hours_per_acre": 1.0,
                    "equipment_complexity": "medium",
                    "precision_level": "high",
                    "environmental_risk": "low"
                },
                ApplicationMethodType.INJECTION: {
                    "cost_per_acre": 35.0,
                    "labor_hours_per_acre": 1.2,
                    "equipment_complexity": "high",
                    "precision_level": "very_high",
                    "environmental_risk": "very_low"
                },
                ApplicationMethodType.FOLIAR: {
                    "cost_per_acre": 40.0,
                    "labor_hours_per_acre": 1.5,
                    "equipment_complexity": "medium",
                    "precision_level": "medium",
                    "environmental_risk": "medium"
                }
            }
        }
    
    def _initialize_yield_prediction_models(self):
        """Initialize yield prediction models for application methods."""
        logger.info("Initializing yield prediction models")
        
        # Yield response coefficients by crop and method
        self.yield_prediction_models = {
            CropType.CORN: {
                ApplicationMethodType.BROADCAST: {
                    "base_yield": 180.0,  # bushels per acre
                    "response_coefficient": 0.15,
                    "efficiency_factor": 0.75,
                    "timing_factor": 0.85
                },
                ApplicationMethodType.BAND: {
                    "base_yield": 180.0,
                    "response_coefficient": 0.22,
                    "efficiency_factor": 0.90,
                    "timing_factor": 0.95
                },
                ApplicationMethodType.SIDEDRESS: {
                    "base_yield": 180.0,
                    "response_coefficient": 0.25,
                    "efficiency_factor": 0.95,
                    "timing_factor": 0.90
                },
                ApplicationMethodType.INJECTION: {
                    "base_yield": 180.0,
                    "response_coefficient": 0.20,
                    "efficiency_factor": 0.92,
                    "timing_factor": 0.88
                },
                ApplicationMethodType.FOLIAR: {
                    "base_yield": 180.0,
                    "response_coefficient": 0.08,
                    "efficiency_factor": 0.60,
                    "timing_factor": 0.70
                }
            },
            CropType.SOYBEAN: {
                ApplicationMethodType.BROADCAST: {
                    "base_yield": 55.0,  # bushels per acre
                    "response_coefficient": 0.12,
                    "efficiency_factor": 0.80,
                    "timing_factor": 0.85
                },
                ApplicationMethodType.BAND: {
                    "base_yield": 55.0,
                    "response_coefficient": 0.18,
                    "efficiency_factor": 0.85,
                    "timing_factor": 0.90
                },
                ApplicationMethodType.INJECTION: {
                    "base_yield": 55.0,
                    "response_coefficient": 0.16,
                    "efficiency_factor": 0.88,
                    "timing_factor": 0.85
                },
                ApplicationMethodType.FOLIAR: {
                    "base_yield": 55.0,
                    "response_coefficient": 0.06,
                    "efficiency_factor": 0.70,
                    "timing_factor": 0.75
                }
            },
            CropType.WHEAT: {
                ApplicationMethodType.BROADCAST: {
                    "base_yield": 70.0,  # bushels per acre
                    "response_coefficient": 0.15,
                    "efficiency_factor": 0.85,
                    "timing_factor": 0.90
                },
                ApplicationMethodType.BAND: {
                    "base_yield": 70.0,
                    "response_coefficient": 0.20,
                    "efficiency_factor": 0.90,
                    "timing_factor": 0.95
                },
                ApplicationMethodType.INJECTION: {
                    "base_yield": 70.0,
                    "response_coefficient": 0.18,
                    "efficiency_factor": 0.92,
                    "timing_factor": 0.88
                }
            }
        }
    
    async def analyze_crop_response(
        self,
        crop_type: CropType,
        method_type: ApplicationMethodType,
        growth_stage: GrowthStage,
        application_rate: float,
        field_conditions: Dict[str, Any]
    ) -> CropResponseData:
        """
        Analyze crop response for a specific application method.
        
        Args:
            crop_type: Type of crop
            method_type: Application method type
            growth_stage: Current growth stage
            application_rate: Application rate
            field_conditions: Field and environmental conditions
            
        Returns:
            CropResponseData with response analysis
        """
        try:
            logger.info(f"Analyzing crop response for {crop_type.value} with {method_type.value}")
            
            # Get base response data
            base_response = self._get_base_response_data(crop_type, method_type)
            if not base_response:
                raise ValueError(f"No response data available for {crop_type.value} with {method_type.value}")
            
            # Adjust for growth stage
            stage_adjustment = self._calculate_growth_stage_adjustment(crop_type, method_type, growth_stage)
            
            # Adjust for application rate
            rate_adjustment = self._calculate_rate_adjustment(method_type, application_rate)
            
            # Adjust for field conditions
            field_adjustment = self._calculate_field_condition_adjustment(field_conditions, method_type)
            
            # Calculate final response metrics
            adjusted_response = CropResponseData(
                method_type=method_type,
                crop_type=crop_type,
                growth_stage=growth_stage,
                yield_response=self._adjust_metric(
                    base_response.yield_response, 
                    stage_adjustment["yield"], 
                    rate_adjustment["yield"], 
                    field_adjustment["yield"]
                ),
                nutrient_efficiency=self._adjust_metric(
                    base_response.nutrient_efficiency,
                    stage_adjustment["efficiency"],
                    rate_adjustment["efficiency"],
                    field_adjustment["efficiency"]
                ),
                growth_rate_response=self._adjust_metric(
                    base_response.growth_rate_response,
                    stage_adjustment["growth"],
                    rate_adjustment["growth"],
                    field_adjustment["growth"]
                ),
                stress_tolerance=self._adjust_metric(
                    base_response.stress_tolerance,
                    stage_adjustment["stress"],
                    rate_adjustment["stress"],
                    field_adjustment["stress"]
                ),
                quality_improvement=self._adjust_metric(
                    base_response.quality_improvement,
                    stage_adjustment["quality"],
                    rate_adjustment["quality"],
                    field_adjustment["quality"]
                ),
                application_rate=application_rate,
                weather_conditions=field_conditions.get("weather", {}),
                soil_conditions=field_conditions.get("soil", {}),
                confidence_score=self._calculate_confidence_score(
                    base_response.confidence_score,
                    stage_adjustment["confidence"],
                    field_adjustment["confidence"]
                ),
                data_sources=base_response.data_sources,
                validation_status="analyzed"
            )
            
            return adjusted_response
            
        except Exception as e:
            logger.error(f"Error analyzing crop response: {e}")
            raise
    
    async def rank_method_effectiveness(
        self,
        crop_type: CropType,
        available_methods: List[ApplicationMethodType],
        field_conditions: Dict[str, Any],
        crop_requirements: CropRequirements
    ) -> List[MethodEffectivenessRanking]:
        """
        Rank application methods by effectiveness for specific conditions.
        
        Args:
            crop_type: Type of crop
            available_methods: List of available application methods
            field_conditions: Field and environmental conditions
            crop_requirements: Crop-specific requirements
            
        Returns:
            List of MethodEffectivenessRanking sorted by effectiveness
        """
        try:
            logger.info(f"Ranking method effectiveness for {crop_type.value}")
            
            rankings = []
            
            for method_type in available_methods:
                # Get response data
                # Convert growth stage string to GrowthStage enum if possible, otherwise use the string value directly
                try:
                    growth_stage_enum = GrowthStage(crop_requirements.growth_stage)
                except ValueError:
                    # If the string is not a valid GrowthStage enum, default to V6 for corn or a reasonable default
                    if crop_type == CropType.CORN:
                        growth_stage_enum = GrowthStage.V6
                    elif crop_type == CropType.SOYBEAN:
                        growth_stage_enum = GrowthStage.R1_SOY
                    elif crop_type == CropType.WHEAT:
                        growth_stage_enum = GrowthStage.TILLERING
                    else:
                        growth_stage_enum = GrowthStage.V6  # Default
                
                response_data = await self.analyze_crop_response(
                    crop_type, method_type, 
                    growth_stage_enum,
                    crop_requirements.nutrient_requirements.get("nitrogen", 0),
                    field_conditions
                )
                
                # Calculate effectiveness scores
                yield_impact = response_data.yield_response
                efficiency_score = response_data.nutrient_efficiency
                cost_effectiveness = self._calculate_cost_effectiveness(method_type, response_data)
                environmental_score = self._calculate_environmental_score(method_type, field_conditions)
                labor_efficiency = self._calculate_labor_efficiency(method_type, field_conditions)
                
                # Calculate overall score
                weights = self.effectiveness_models["scoring_weights"]
                overall_score = (
                    yield_impact * weights["yield_impact"] +
                    efficiency_score * weights["nutrient_efficiency"] +
                    cost_effectiveness * weights["cost_effectiveness"] +
                    environmental_score * weights["environmental_impact"] +
                    labor_efficiency * weights["labor_efficiency"]
                )
                
                # Create ranking
                ranking = MethodEffectivenessRanking(
                    method_type=method_type,
                    overall_score=overall_score,
                    yield_impact=yield_impact,
                    efficiency_score=efficiency_score,
                    cost_effectiveness=cost_effectiveness,
                    environmental_score=environmental_score,
                    labor_efficiency=labor_efficiency,
                    response_factors={
                        "yield_response": response_data.yield_response,
                        "nutrient_efficiency": response_data.nutrient_efficiency,
                        "growth_rate": response_data.growth_rate_response,
                        "stress_tolerance": response_data.stress_tolerance,
                        "quality_improvement": response_data.quality_improvement
                    },
                    limitations=self._get_method_limitations(method_type, field_conditions),
                    advantages=self._get_method_advantages(method_type, field_conditions),
                    optimal_conditions=self._get_optimal_conditions(method_type, crop_type),
                    application_guidance=self._get_application_guidance(method_type, crop_type)
                )
                
                rankings.append(ranking)
            
            # Sort by overall score (descending)
            rankings.sort(key=lambda x: x.overall_score, reverse=True)
            
            return rankings
            
        except Exception as e:
            logger.error(f"Error ranking method effectiveness: {e}")
            raise
    
    async def predict_yield_impact(
        self,
        crop_type: CropType,
        method_type: ApplicationMethodType,
        baseline_yield: float,
        application_rate: float,
        field_conditions: Dict[str, Any]
    ) -> YieldImpactPrediction:
        """
        Predict yield impact for a specific application method.
        
        Args:
            crop_type: Type of crop
            method_type: Application method type
            baseline_yield: Baseline yield without fertilizer
            application_rate: Application rate
            field_conditions: Field and environmental conditions
            
        Returns:
            YieldImpactPrediction with yield impact analysis
        """
        try:
            logger.info(f"Predicting yield impact for {crop_type.value} with {method_type.value}")
            
            # Get prediction model
            model = self._get_yield_prediction_model(crop_type, method_type)
            if not model:
                raise ValueError(f"No yield prediction model for {crop_type.value} with {method_type.value}")
            
            # Calculate yield response
            response_coefficient = model["response_coefficient"]
            efficiency_factor = model["efficiency_factor"]
            timing_factor = self._calculate_timing_factor(method_type, field_conditions)
            
            # Adjust for field conditions
            field_factor = self._calculate_field_yield_factor(field_conditions)
            
            # Calculate predicted yield
            yield_increase = baseline_yield * response_coefficient * efficiency_factor * timing_factor * field_factor
            predicted_yield = baseline_yield + yield_increase
            
            # Calculate yield range (confidence interval)
            confidence = 0.85  # Base confidence
            yield_variance = predicted_yield * 0.15  # 15% variance
            yield_range = (
                max(0, predicted_yield - yield_variance),
                predicted_yield + yield_variance
            )
            
            # Calculate economic impact
            revenue_impact_per_acre = yield_increase * self._get_crop_price(crop_type)
            cost_per_unit_yield = self._get_method_cost(method_type) / yield_increase if yield_increase > 0 else 0
            
            # Identify risk factors
            risk_factors = self._identify_yield_risk_factors(method_type, field_conditions)
            
            prediction = YieldImpactPrediction(
                method_type=method_type,
                crop_type=crop_type,
                baseline_yield=baseline_yield,
                predicted_yield=predicted_yield,
                yield_increase_percent=(yield_increase / baseline_yield) * 100 if baseline_yield > 0 else 0,
                yield_range=yield_range,
                confidence=confidence,
                contributing_factors={
                    "response_coefficient": response_coefficient,
                    "efficiency_factor": efficiency_factor,
                    "timing_factor": timing_factor,
                    "field_factor": field_factor
                },
                risk_factors=risk_factors,
                revenue_impact_per_acre=revenue_impact_per_acre,
                cost_per_unit_yield=cost_per_unit_yield
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting yield impact: {e}")
            raise
    
    def _get_base_response_data(self, crop_type: CropType, method_type: ApplicationMethodType) -> Optional[CropResponseData]:
        """Get base response data for crop and method combination."""
        crop_data = self.response_database.get(crop_type)
        if not crop_data:
            return None
        return crop_data.get(method_type)
    
    def _calculate_growth_stage_adjustment(self, crop_type: CropType, method_type: ApplicationMethodType, growth_stage_str: str) -> Dict[str, float]:
        """Calculate adjustment factors based on growth stage."""
        # Get crop preferences
        preferences = self.crop_integration_service.get_application_preferences(crop_type)
        if not preferences:
            return {"yield": 1.0, "efficiency": 1.0, "growth": 1.0, "stress": 1.0, "quality": 1.0, "confidence": 1.0}
        
        # Check if current stage is critical for this method
        is_critical_stage = growth_stage_str in preferences.application_timing_critical_stages
        
        if is_critical_stage:
            return {"yield": 1.1, "efficiency": 1.05, "growth": 1.1, "stress": 1.0, "quality": 1.05, "confidence": 1.05}
        else:
            return {"yield": 0.95, "efficiency": 0.95, "growth": 0.95, "stress": 1.0, "quality": 0.95, "confidence": 0.95}
    
    def _calculate_rate_adjustment(self, method_type: ApplicationMethodType, application_rate: float) -> Dict[str, float]:
        """Calculate adjustment factors based on application rate."""
        # Optimal rates by method (lbs N per acre)
        optimal_rates = {
            ApplicationMethodType.BROADCAST: 150.0,
            ApplicationMethodType.BAND: 120.0,
            ApplicationMethodType.SIDEDRESS: 140.0,
            ApplicationMethodType.INJECTION: 130.0,
            ApplicationMethodType.FOLIAR: 20.0
        }
        
        optimal_rate = optimal_rates.get(method_type, 120.0)
        rate_ratio = application_rate / optimal_rate if optimal_rate > 0 else 1.0
        
        # Calculate adjustment (optimal rate = 1.0, deviations reduce efficiency)
        if rate_ratio < 0.5:
            adjustment = 0.7  # Under-application
        elif rate_ratio > 2.0:
            adjustment = 0.8  # Over-application
        else:
            adjustment = 1.0 - abs(rate_ratio - 1.0) * 0.2  # Linear adjustment around optimal
        
        return {
            "yield": adjustment,
            "efficiency": adjustment,
            "growth": adjustment,
            "stress": 1.0,
            "quality": adjustment,
            "confidence": 1.0
        }
    
    def _calculate_field_condition_adjustment(self, field_conditions: Dict[str, Any], method_type: ApplicationMethodType) -> Dict[str, float]:
        """Calculate adjustment factors based on field conditions."""
        adjustments = {"yield": 1.0, "efficiency": 1.0, "growth": 1.0, "stress": 1.0, "quality": 1.0, "confidence": 1.0}
        
        # Weather conditions
        weather = field_conditions.get("weather", {})
        if weather.get("temperature_celsius", 20) > 30:
            adjustments["stress"] *= 0.9  # Heat stress
        if weather.get("humidity_percent", 50) < 30:
            adjustments["stress"] *= 0.95  # Low humidity stress
        
        # Soil conditions
        soil = field_conditions.get("soil", {})
        if soil.get("ph", 6.5) < 5.5 or soil.get("ph", 6.5) > 8.0:
            adjustments["efficiency"] *= 0.8  # pH stress
        if soil.get("organic_matter_percent", 3.0) < 2.0:
            adjustments["efficiency"] *= 0.9  # Low organic matter
        
        # Method-specific adjustments
        if method_type == ApplicationMethodType.FOLIAR and weather.get("wind_speed_kmh", 0) > 15:
            adjustments["efficiency"] *= 0.7  # Wind reduces foliar efficiency
        
        return adjustments
    
    def _adjust_metric(self, base_value: float, *adjustments: float) -> float:
        """Apply adjustments to a base metric value."""
        result = base_value
        for adjustment in adjustments:
            result *= adjustment
        return max(0.0, min(1.0, result))  # Clamp to [0, 1]
    
    def _calculate_confidence_score(self, base_confidence: float, *adjustments: float) -> float:
        """Calculate final confidence score with adjustments."""
        result = base_confidence
        for adjustment in adjustments:
            result *= adjustment
        return max(0.0, min(1.0, result))
    
    def _calculate_cost_effectiveness(self, method_type: ApplicationMethodType, response_data: CropResponseData) -> float:
        """Calculate cost effectiveness score."""
        method_chars = self.effectiveness_models["method_characteristics"].get(method_type, {})
        cost_per_acre = method_chars.get("cost_per_acre", 25.0)
        
        # Higher yield response and lower cost = better cost effectiveness
        yield_value = response_data.yield_response * 100  # Scale to 0-100
        cost_effectiveness = yield_value / cost_per_acre if cost_per_acre > 0 else 0
        
        # Normalize to 0-1 scale
        return min(1.0, cost_effectiveness / 5.0)
    
    def _calculate_environmental_score(self, method_type: ApplicationMethodType, field_conditions: Dict[str, Any]) -> float:
        """Calculate environmental impact score."""
        method_chars = self.effectiveness_models["method_characteristics"].get(method_type, {})
        risk_level = method_chars.get("environmental_risk", "medium")
        
        risk_scores = {"very_low": 0.9, "low": 0.8, "medium": 0.6, "high": 0.4, "very_high": 0.2}
        base_score = risk_scores.get(risk_level, 0.6)
        
        # Adjust for field conditions
        soil = field_conditions.get("soil", {})
        if soil.get("slope_percent", 0) > 5:
            base_score *= 0.8  # Higher slope increases runoff risk
        
        return base_score
    
    def _calculate_labor_efficiency(self, method_type: ApplicationMethodType, field_conditions: Dict[str, Any]) -> float:
        """Calculate labor efficiency score."""
        method_chars = self.effectiveness_models["method_characteristics"].get(method_type, {})
        labor_hours = method_chars.get("labor_hours_per_acre", 1.0)
        
        # Lower labor hours = higher efficiency
        efficiency = 1.0 / labor_hours if labor_hours > 0 else 1.0
        
        # Normalize to 0-1 scale
        return min(1.0, efficiency)
    
    def _get_method_limitations(self, method_type: ApplicationMethodType, field_conditions: Dict[str, Any]) -> List[str]:
        """Get method limitations for specific conditions."""
        limitations = []
        
        if method_type == ApplicationMethodType.FOLIAR:
            limitations.append("Limited nutrient capacity")
            limitations.append("Weather dependent")
            if field_conditions.get("weather", {}).get("wind_speed_kmh", 0) > 15:
                limitations.append("High wind conditions reduce effectiveness")
        
        elif method_type == ApplicationMethodType.BROADCAST:
            limitations.append("Lower nutrient use efficiency")
            limitations.append("Higher environmental risk")
        
        elif method_type == ApplicationMethodType.INJECTION:
            limitations.append("Requires specialized equipment")
            limitations.append("Higher initial investment")
        
        return limitations
    
    def _get_method_advantages(self, method_type: ApplicationMethodType, field_conditions: Dict[str, Any]) -> List[str]:
        """Get method advantages for specific conditions."""
        advantages = []
        
        if method_type == ApplicationMethodType.BAND:
            advantages.append("High nutrient use efficiency")
            advantages.append("Reduced environmental impact")
        
        elif method_type == ApplicationMethodType.SIDEDRESS:
            advantages.append("Timing flexibility")
            advantages.append("Good nutrient placement")
        
        elif method_type == ApplicationMethodType.INJECTION:
            advantages.append("Precise nutrient placement")
            advantages.append("Minimal environmental impact")
        
        elif method_type == ApplicationMethodType.FOLIAR:
            advantages.append("Quick nutrient uptake")
            advantages.append("Good for micronutrients")
        
        return advantages
    
    def _get_optimal_conditions(self, method_type: ApplicationMethodType, crop_type: CropType) -> Dict[str, Any]:
        """Get optimal conditions for method application."""
        return {
            "soil_ph_range": (6.0, 7.5),
            "soil_moisture": "moderate",
            "temperature_range": (15, 25),
            "wind_speed_max": 15 if method_type == ApplicationMethodType.FOLIAR else 25,
            "application_timing": "early_morning" if method_type == ApplicationMethodType.FOLIAR else "any_time"
        }
    
    def _get_application_guidance(self, method_type: ApplicationMethodType, crop_type: CropType) -> List[str]:
        """Get application guidance for method."""
        guidance = []
        
        if method_type == ApplicationMethodType.BAND:
            guidance.append("Apply 2-3 inches to the side of seed row")
            guidance.append("Maintain consistent application depth")
        
        elif method_type == ApplicationMethodType.SIDEDRESS:
            guidance.append("Apply when crop is 6-12 inches tall")
            guidance.append("Avoid root damage during application")
        
        elif method_type == ApplicationMethodType.FOLIAR:
            guidance.append("Apply during early morning or evening")
            guidance.append("Avoid application during hot, sunny conditions")
        
        return guidance
    
    def _get_yield_prediction_model(self, crop_type: CropType, method_type: ApplicationMethodType) -> Optional[Dict[str, float]]:
        """Get yield prediction model for crop and method."""
        crop_models = self.yield_prediction_models.get(crop_type)
        if not crop_models:
            return None
        return crop_models.get(method_type)
    
    def _calculate_timing_factor(self, method_type: ApplicationMethodType, field_conditions: Dict[str, Any]) -> float:
        """Calculate timing factor for yield prediction."""
        # Base timing factors by method
        timing_factors = {
            ApplicationMethodType.BROADCAST: 0.85,
            ApplicationMethodType.BAND: 0.95,
            ApplicationMethodType.SIDEDRESS: 0.90,
            ApplicationMethodType.INJECTION: 0.88,
            ApplicationMethodType.FOLIAR: 0.70
        }
        
        base_factor = timing_factors.get(method_type, 0.85)
        
        # Adjust for weather conditions
        weather = field_conditions.get("weather", {})
        if weather.get("temperature_celsius", 20) < 10:
            base_factor *= 0.9  # Cold conditions reduce efficiency
        
        return base_factor
    
    def _calculate_field_yield_factor(self, field_conditions: Dict[str, Any]) -> float:
        """Calculate field-specific yield factor."""
        factor = 1.0
        
        # Soil conditions
        soil = field_conditions.get("soil", {})
        if soil.get("ph", 6.5) < 5.5 or soil.get("ph", 6.5) > 8.0:
            factor *= 0.8  # pH stress
        if soil.get("organic_matter_percent", 3.0) < 2.0:
            factor *= 0.9  # Low organic matter
        
        # Weather conditions
        weather = field_conditions.get("weather", {})
        if weather.get("precipitation_mm", 0) > 100:  # Excessive moisture
            factor *= 0.9
        
        return factor
    
    def _get_crop_price(self, crop_type: CropType) -> float:
        """Get crop price per unit yield."""
        prices = {
            CropType.CORN: 5.50,  # $/bushel
            CropType.SOYBEAN: 12.00,  # $/bushel
            CropType.WHEAT: 7.00  # $/bushel
        }
        return prices.get(crop_type, 5.50)
    
    def _get_method_cost(self, method_type: ApplicationMethodType) -> float:
        """Get method cost per acre."""
        method_chars = self.effectiveness_models["method_characteristics"].get(method_type, {})
        return method_chars.get("cost_per_acre", 25.0)
    
    def _identify_yield_risk_factors(self, method_type: ApplicationMethodType, field_conditions: Dict[str, Any]) -> List[str]:
        """Identify risk factors that could affect yield."""
        risks = []
        
        # Weather risks
        weather = field_conditions.get("weather", {})
        if weather.get("temperature_celsius", 20) > 35:
            risks.append("High temperature stress")
        if weather.get("precipitation_mm", 0) > 150:
            risks.append("Excessive moisture")
        
        # Soil risks
        soil = field_conditions.get("soil", {})
        if soil.get("ph", 6.5) < 5.5:
            risks.append("Acidic soil conditions")
        if soil.get("slope_percent", 0) > 8:
            risks.append("High slope increases runoff risk")
        
        # Method-specific risks
        if method_type == ApplicationMethodType.FOLIAR:
            if weather.get("wind_speed_kmh", 0) > 15:
                risks.append("High wind reduces foliar effectiveness")
        
        return risks