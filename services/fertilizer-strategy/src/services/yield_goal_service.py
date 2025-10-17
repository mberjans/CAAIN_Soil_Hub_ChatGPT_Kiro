"""
Comprehensive Yield Goal Management Service.

This service provides comprehensive yield goal setting including:
- Historical yield analysis and trend identification
- Potential yield assessment based on multiple factors
- Realistic goal setting with risk assessment
- Integration with soil, weather, and management data
- Goal feasibility analysis and achievement probability
"""

import logging
import statistics
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
from uuid import uuid4
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit

from ..models.yield_goal_models import (
    YieldGoalRequest, YieldGoalAnalysis, YieldGoalRecommendation,
    YieldTrendAnalysis, PotentialYieldAssessment, YieldGoalValidationResult,
    YieldGoalComparison, YieldGoalType, YieldTrendDirection, YieldRiskLevel,
    HistoricalYieldData, SoilCharacteristic, WeatherPattern, ManagementPractice
)

logger = logging.getLogger(__name__)


class YieldGoalManagementService:
    """
    Comprehensive yield goal management service.
    
    Features:
    - Historical yield analysis and trend identification
    - Potential yield assessment based on multiple factors
    - Realistic goal setting with risk assessment
    - Integration with soil, weather, and management data
    - Goal feasibility analysis and achievement probability
    """
    
    def __init__(self):
        """Initialize the yield goal management service."""
        self.logger = logging.getLogger(__name__)
        
        # Yield potential factors and weights
        self.soil_factor_weights = {
            'ph_level': 0.15,
            'organic_matter_percent': 0.20,
            'cation_exchange_capacity': 0.15,
            'drainage_class': 0.15,
            'water_holding_capacity': 0.20,
            'slope_percent': 0.15
        }
        
        self.weather_factor_weights = {
            'growing_season_precipitation': 0.25,
            'growing_degree_days': 0.25,
            'drought_stress_days': 0.20,
            'heat_stress_days': 0.15,
            'optimal_growing_days': 0.15
        }
        
        self.management_factor_weights = {
            'tillage_system': 0.20,
            'irrigation_available': 0.25,
            'precision_agriculture': 0.15,
            'cover_crop_usage': 0.15,
            'crop_rotation': 0.25
        }
        
        # Crop-specific yield potential baselines (bu/acre)
        self.crop_yield_baselines = {
            'corn': 180.0,
            'soybean': 55.0,
            'wheat': 70.0,
            'cotton': 900.0,  # lbs/acre
            'rice': 8000.0,   # lbs/acre
            'sorghum': 100.0,
            'barley': 80.0,
            'oats': 70.0
        }
    
    async def analyze_yield_goals(self, request: YieldGoalRequest) -> YieldGoalAnalysis:
        """
        Perform comprehensive yield goal analysis.
        
        Args:
            request: Yield goal analysis request
            
        Returns:
            Comprehensive yield goal analysis
        """
        try:
            analysis_id = uuid4()
            
            # 1. Analyze historical yield trends
            historical_trend = await self._analyze_historical_trends(request.historical_yields)
            
            # 2. Assess potential yield
            potential_assessment = await self._assess_yield_potential(
                request.soil_characteristics,
                request.weather_patterns,
                request.management_practices,
                request.crop_type,
                request.variety
            )
            
            # 3. Generate goal recommendations
            goal_recommendations = await self._generate_goal_recommendations(
                historical_trend,
                potential_assessment,
                request.goal_preference,
                request.risk_tolerance
            )
            
            # 4. Assess overall risk
            overall_risk_level, risk_factors, mitigation_strategies = await self._assess_overall_risk(
                historical_trend,
                potential_assessment,
                request.weather_patterns,
                request.management_practices
            )
            
            # 5. Calculate analysis confidence and data quality
            analysis_confidence = await self._calculate_analysis_confidence(request)
            data_quality_score = await self._assess_data_quality(request)
            
            # 6. Prepare supporting data
            supporting_data = await self._prepare_supporting_data(
                request, historical_trend, potential_assessment
            )
            
            analysis = YieldGoalAnalysis(
                analysis_id=analysis_id,
                field_id=request.field_id,
                crop_type=request.crop_type,
                historical_trend=historical_trend,
                potential_assessment=potential_assessment,
                goal_recommendations=goal_recommendations,
                overall_risk_level=overall_risk_level,
                risk_factors=risk_factors,
                mitigation_strategies=mitigation_strategies,
                supporting_data=supporting_data,
                analysis_confidence=analysis_confidence,
                data_quality_score=data_quality_score
            )
            
            self.logger.info(f"Yield goal analysis completed for field {request.field_id}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in yield goal analysis: {e}")
            raise
    
    async def _analyze_historical_trends(self, historical_yields: List[HistoricalYieldData]) -> YieldTrendAnalysis:
        """Analyze historical yield trends."""
        if len(historical_yields) < 3:
            # Insufficient data for trend analysis
            if len(historical_yields) == 0:
                return YieldTrendAnalysis(
                    trend_direction=YieldTrendDirection.STABLE,
                    trend_slope=0.0,
                    r_squared=0.0,
                    volatility=0.0,
                    average_yield=0.0,
                    min_yield=0.0,
                    max_yield=0.0,
                    trend_confidence=0.3
                )
            else:
                yields = [y.yield_per_acre for y in historical_yields]
                return YieldTrendAnalysis(
                    trend_direction=YieldTrendDirection.STABLE,
                    trend_slope=0.0,
                    r_squared=0.0,
                    volatility=0.0,
                    average_yield=statistics.mean(yields),
                    min_yield=min(yields),
                    max_yield=max(yields),
                    trend_confidence=0.3
                )
        
        # Sort by year
        sorted_yields = sorted(historical_yields, key=lambda x: x.year)
        years = [y.year for y in sorted_yields]
        yields = [y.yield_per_acre for y in sorted_yields]
        
        # Calculate trend using linear regression
        x = np.array(years)
        y = np.array(yields)
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Calculate volatility (coefficient of variation) first
        volatility = statistics.stdev(yields) / statistics.mean(yields) if statistics.mean(yields) > 0 else 0
        
        # Determine trend direction
        if volatility > 0.2:  # More than 20% coefficient of variation
            trend_direction = YieldTrendDirection.VOLATILE
        elif abs(slope) < 0.5:  # Less than 0.5 bu/acre/year change
            trend_direction = YieldTrendDirection.STABLE
        elif slope > 0:
            trend_direction = YieldTrendDirection.INCREASING
        else:
            trend_direction = YieldTrendDirection.DECREASING
        
        # Calculate trend confidence based on R-squared and data points
        trend_confidence = min(r_value ** 2 * (len(yields) / 10), 1.0)
        
        return YieldTrendAnalysis(
            trend_direction=trend_direction,
            trend_slope=slope,
            r_squared=r_value ** 2,
            volatility=volatility,
            average_yield=statistics.mean(yields),
            min_yield=min(yields),
            max_yield=max(yields),
            trend_confidence=trend_confidence
        )
    
    async def _assess_yield_potential(
        self,
        soil_characteristics: SoilCharacteristic,
        weather_patterns: Optional[WeatherPattern],
        management_practices: ManagementPractice,
        crop_type: str,
        variety: Optional[str]
    ) -> PotentialYieldAssessment:
        """Assess yield potential based on multiple factors."""
        
        # 1. Soil potential assessment
        soil_potential = await self._calculate_soil_potential(soil_characteristics, crop_type)
        
        # 2. Weather potential assessment
        weather_potential = await self._calculate_weather_potential(weather_patterns, crop_type)
        
        # 3. Management potential assessment
        management_potential = await self._calculate_management_potential(management_practices, crop_type)
        
        # 4. Variety potential assessment
        variety_potential = await self._calculate_variety_potential(variety, crop_type)
        
        # 5. Calculate combined potential (weighted average)
        weights = [0.3, 0.25, 0.25, 0.2]  # Soil, weather, management, variety
        potentials = [soil_potential, weather_potential, management_potential, variety_potential]
        
        # Handle missing weather data
        if weather_potential == 0:
            weights = [0.4, 0.0, 0.35, 0.25]  # Adjust weights
            potentials = [soil_potential, 0, management_potential, variety_potential]
        
        combined_potential = sum(w * p for w, p in zip(weights, potentials)) / sum(weights)
        
        # 6. Identify limiting factors and improvement opportunities
        limiting_factors = await self._identify_limiting_factors(
            soil_characteristics, weather_patterns, management_practices, crop_type
        )
        
        improvement_opportunities = await self._identify_improvement_opportunities(
            soil_characteristics, weather_patterns, management_practices, crop_type
        )
        
        return PotentialYieldAssessment(
            soil_potential=soil_potential,
            weather_potential=weather_potential,
            management_potential=management_potential,
            variety_potential=variety_potential,
            combined_potential=combined_potential,
            limiting_factors=limiting_factors,
            improvement_opportunities=improvement_opportunities
        )
    
    async def _calculate_soil_potential(self, soil: SoilCharacteristic, crop_type: str) -> float:
        """Calculate soil-based yield potential."""
        base_yield = self.crop_yield_baselines.get(crop_type, 150.0)
        
        # pH factor (optimal range varies by crop)
        ph_optimal_ranges = {
            'corn': (6.0, 7.0),
            'soybean': (6.0, 7.0),
            'wheat': (6.0, 7.5),
            'cotton': (5.5, 7.0),
            'rice': (5.0, 6.5)
        }
        
        ph_range = ph_optimal_ranges.get(crop_type, (6.0, 7.0))
        ph_factor = 1.0
        if soil.ph_level < ph_range[0] or soil.ph_level > ph_range[1]:
            ph_factor = 0.8  # Reduce potential for suboptimal pH
        
        # Organic matter factor
        om_factor = min(1.0, soil.organic_matter_percent / 4.0)  # Optimal around 4%
        
        # CEC factor
        cec_factor = min(1.0, soil.cation_exchange_capacity / 20.0)  # Optimal around 20
        
        # Drainage factor
        drainage_factors = {
            'excessively_drained': 0.7,
            'well_drained': 1.0,
            'moderately_well_drained': 0.9,
            'somewhat_poorly_drained': 0.8,
            'poorly_drained': 0.6,
            'very_poorly_drained': 0.4
        }
        drainage_factor = drainage_factors.get(soil.drainage_class.lower(), 0.8)
        
        # Slope factor
        slope_factor = max(0.7, 1.0 - (soil.slope_percent * 0.01))  # Reduce potential with slope
        
        # Water holding capacity factor
        whc_factor = min(1.0, soil.water_holding_capacity / 2.0)  # Optimal around 2 inches
        
        # Calculate weighted soil potential
        soil_score = (
            ph_factor * self.soil_factor_weights['ph_level'] +
            om_factor * self.soil_factor_weights['organic_matter_percent'] +
            cec_factor * self.soil_factor_weights['cation_exchange_capacity'] +
            drainage_factor * self.soil_factor_weights['drainage_class'] +
            slope_factor * self.soil_factor_weights['slope_percent'] +
            whc_factor * self.soil_factor_weights['water_holding_capacity']
        )
        
        return base_yield * soil_score
    
    async def _calculate_weather_potential(self, weather: Optional[WeatherPattern], crop_type: str) -> float:
        """Calculate weather-based yield potential."""
        if not weather:
            return 0.0  # No weather data available
        
        base_yield = self.crop_yield_baselines.get(crop_type, 150.0)
        
        # Precipitation factor
        optimal_precipitation = {
            'corn': 25.0,  # inches
            'soybean': 20.0,
            'wheat': 15.0,
            'cotton': 20.0,
            'rice': 30.0
        }
        
        optimal_precip = optimal_precipitation.get(crop_type, 20.0)
        precip_factor = min(1.0, weather.growing_season_precipitation / optimal_precip)
        
        # Growing degree days factor
        optimal_gdd = {
            'corn': 2800,
            'soybean': 2500,
            'wheat': 2000,
            'cotton': 3000,
            'rice': 3500
        }
        
        optimal_gdd_value = optimal_gdd.get(crop_type, 2500)
        gdd_factor = min(1.0, weather.growing_degree_days / optimal_gdd_value)
        
        # Stress factors
        stress_factor = 1.0
        if weather.drought_stress_days > 30:
            stress_factor *= 0.8
        if weather.heat_stress_days > 20:
            stress_factor *= 0.9
        if weather.frost_risk_days > 10:
            stress_factor *= 0.85
        
        # Optimal growing days factor
        optimal_days_factor = min(1.0, weather.optimal_growing_days / 120)  # Optimal around 120 days
        
        # Calculate weighted weather potential
        weather_score = (
            precip_factor * self.weather_factor_weights['growing_season_precipitation'] +
            gdd_factor * self.weather_factor_weights['growing_degree_days'] +
            stress_factor * (self.weather_factor_weights['drought_stress_days'] + 
                           self.weather_factor_weights['heat_stress_days']) +
            optimal_days_factor * self.weather_factor_weights['optimal_growing_days']
        )
        
        return base_yield * weather_score
    
    async def _calculate_management_potential(self, management: ManagementPractice, crop_type: str) -> float:
        """Calculate management-based yield potential."""
        base_yield = self.crop_yield_baselines.get(crop_type, 150.0)
        
        # Tillage system factor
        tillage_factors = {
            'no_till': 0.95,
            'reduced_till': 1.0,
            'conventional_till': 0.9,
            'strip_till': 1.05,
            'ridge_till': 0.95
        }
        tillage_factor = tillage_factors.get(management.tillage_system.lower(), 0.9)
        
        # Irrigation factor
        irrigation_factor = 1.1 if management.irrigation_available else 1.0
        
        # Precision agriculture factor
        precision_factor = 1.05 if management.precision_agriculture else 1.0
        
        # Cover crop factor
        cover_crop_factor = 1.03 if management.cover_crop_usage else 1.0
        
        # Crop rotation factor
        rotation_factors = {
            'continuous_corn': 0.85,
            'corn_soybean': 1.0,
            'corn_soybean_wheat': 1.05,
            'diverse_rotation': 1.1,
            'monoculture': 0.8
        }
        rotation_factor = rotation_factors.get(management.crop_rotation.lower(), 1.0)
        
        # Calculate weighted management potential
        management_score = (
            tillage_factor * self.management_factor_weights['tillage_system'] +
            irrigation_factor * self.management_factor_weights['irrigation_available'] +
            precision_factor * self.management_factor_weights['precision_agriculture'] +
            cover_crop_factor * self.management_factor_weights['cover_crop_usage'] +
            rotation_factor * self.management_factor_weights['crop_rotation']
        )
        
        return base_yield * management_score
    
    async def _calculate_variety_potential(self, variety: Optional[str], crop_type: str) -> float:
        """Calculate variety-based yield potential."""
        base_yield = self.crop_yield_baselines.get(crop_type, 150.0)
        
        if not variety:
            return base_yield * 0.95  # Slight reduction for unknown variety
        
        # In a real implementation, this would query a variety database
        # For now, we'll use a simplified approach
        variety_factors = {
            'high_yield': 1.1,
            'standard': 1.0,
            'drought_tolerant': 0.95,
            'early_maturity': 0.9,
            'late_maturity': 1.05
        }
        
        # Simple keyword matching for variety characteristics
        variety_factor = 0.95  # Default to slightly below baseline for unknown varieties
        variety_lower = variety.lower()
        for factor_type, factor_value in variety_factors.items():
            if factor_type in variety_lower:
                variety_factor = factor_value
                break
        
        return base_yield * variety_factor
    
    async def _identify_limiting_factors(
        self,
        soil: SoilCharacteristic,
        weather: Optional[WeatherPattern],
        management: ManagementPractice,
        crop_type: str
    ) -> List[str]:
        """Identify factors limiting yield potential."""
        limiting_factors = []
        
        # Soil limitations
        if soil.ph_level < 5.5 or soil.ph_level > 8.0:
            limiting_factors.append("Suboptimal soil pH")
        
        if soil.organic_matter_percent < 2.0:
            limiting_factors.append("Low organic matter content")
        
        if soil.cation_exchange_capacity < 10:
            limiting_factors.append("Low cation exchange capacity")
        
        if soil.drainage_class in ['poorly_drained', 'very_poorly_drained']:
            limiting_factors.append("Poor drainage")
        
        if soil.slope_percent > 10:
            limiting_factors.append("Excessive slope")
        
        # Weather limitations
        if weather:
            if weather.drought_stress_days > 30:
                limiting_factors.append("Drought stress")
            
            if weather.heat_stress_days > 20:
                limiting_factors.append("Heat stress")
            
            if weather.frost_risk_days > 10:
                limiting_factors.append("Frost risk")
        
        # Management limitations
        if management.crop_rotation == 'continuous_corn':
            limiting_factors.append("Continuous corn rotation")
        
        if not management.irrigation_available and weather and weather.growing_season_precipitation < 15:
            limiting_factors.append("Insufficient water availability")
        
        return limiting_factors
    
    async def _identify_improvement_opportunities(
        self,
        soil: SoilCharacteristic,
        weather: Optional[WeatherPattern],
        management: ManagementPractice,
        crop_type: str
    ) -> List[str]:
        """Identify opportunities for yield improvement."""
        opportunities = []
        
        # Soil improvements
        if soil.organic_matter_percent < 3.0:
            opportunities.append("Increase organic matter through cover crops or manure")
        
        if soil.ph_level < 6.0 or soil.ph_level > 7.5:
            opportunities.append("Adjust soil pH with lime or sulfur")
        
        # Management improvements
        if not management.precision_agriculture:
            opportunities.append("Adopt precision agriculture technologies")
        
        if not management.cover_crop_usage:
            opportunities.append("Implement cover crop system")
        
        if management.tillage_system == 'conventional_till':
            opportunities.append("Consider reduced tillage or no-till")
        
        if management.crop_rotation == 'continuous_corn':
            opportunities.append("Implement crop rotation")
        
        # Weather-related improvements
        if weather and weather.drought_stress_days > 20 and not management.irrigation_available:
            opportunities.append("Consider irrigation system")
        
        return opportunities
    
    async def _generate_goal_recommendations(
        self,
        historical_trend: YieldTrendAnalysis,
        potential_assessment: PotentialYieldAssessment,
        goal_preference: YieldGoalType,
        risk_tolerance: YieldRiskLevel
    ) -> List[YieldGoalRecommendation]:
        """Generate yield goal recommendations."""
        recommendations = []
        
        # Calculate base goal from historical average and trend
        base_goal = historical_trend.average_yield + (historical_trend.trend_slope * 2)  # 2-year projection
        
        # Adjust based on potential assessment
        potential_adjustment = potential_assessment.combined_potential / historical_trend.average_yield
        adjusted_base = base_goal * min(potential_adjustment, 1.2)  # Cap at 20% increase
        
        # Generate different goal types
        goal_types = [
            (YieldGoalType.CONSERVATIVE, 0.85, YieldRiskLevel.LOW),
            (YieldGoalType.REALISTIC, 1.0, YieldRiskLevel.MEDIUM),
            (YieldGoalType.OPTIMISTIC, 1.1, YieldRiskLevel.HIGH),
            (YieldGoalType.STRETCH, 1.2, YieldRiskLevel.CRITICAL)
        ]
        
        for goal_type, multiplier, risk_level in goal_types:
            recommended_yield = adjusted_base * multiplier
            
            # Calculate confidence and achievement probability
            confidence_level = await self._calculate_goal_confidence(
                historical_trend, potential_assessment, goal_type
            )
            
            achievement_probability = await self._calculate_achievement_probability(
                recommended_yield, historical_trend, potential_assessment, risk_level
            )
            
            # Generate rationale
            rationale = await self._generate_goal_rationale(
                goal_type, recommended_yield, historical_trend, potential_assessment
            )
            
            # Identify supporting and risk factors
            supporting_factors = await self._identify_supporting_factors(
                historical_trend, potential_assessment, goal_type
            )
            
            risk_factors = await self._identify_risk_factors(
                historical_trend, potential_assessment, goal_type
            )
            
            recommendation = YieldGoalRecommendation(
                goal_type=goal_type,
                recommended_yield=recommended_yield,
                confidence_level=confidence_level,
                achievement_probability=achievement_probability,
                risk_level=risk_level,
                rationale=rationale,
                supporting_factors=supporting_factors,
                risk_factors=risk_factors
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _calculate_goal_confidence(
        self,
        historical_trend: YieldTrendAnalysis,
        potential_assessment: PotentialYieldAssessment,
        goal_type: YieldGoalType
    ) -> float:
        """Calculate confidence level for a goal type."""
        base_confidence = historical_trend.trend_confidence
        
        # Adjust based on goal type
        goal_adjustments = {
            YieldGoalType.CONSERVATIVE: 0.1,
            YieldGoalType.REALISTIC: 0.0,
            YieldGoalType.OPTIMISTIC: -0.1,
            YieldGoalType.STRETCH: -0.2
        }
        
        # Adjust based on data quality
        data_quality_factor = min(1.0, len(potential_assessment.limiting_factors) / 5.0)
        
        confidence = base_confidence + goal_adjustments[goal_type] + (data_quality_factor * 0.2)
        return max(0.1, min(1.0, confidence))
    
    async def _calculate_achievement_probability(
        self,
        recommended_yield: float,
        historical_trend: YieldTrendAnalysis,
        potential_assessment: PotentialYieldAssessment,
        risk_level: YieldRiskLevel
    ) -> float:
        """Calculate probability of achieving the recommended yield."""
        # Base probability from historical performance
        historical_prob = 0.5  # Base probability
        
        # Adjust based on how close goal is to historical performance
        if recommended_yield <= historical_trend.average_yield:
            historical_prob = 0.8
        elif recommended_yield <= historical_trend.max_yield:
            historical_prob = 0.6
        else:
            historical_prob = 0.3
        
        # Adjust based on potential assessment
        potential_factor = min(1.0, potential_assessment.combined_potential / recommended_yield)
        
        # Adjust based on risk level
        risk_adjustments = {
            YieldRiskLevel.LOW: 0.1,
            YieldRiskLevel.MEDIUM: 0.0,
            YieldRiskLevel.HIGH: -0.1,
            YieldRiskLevel.CRITICAL: -0.2
        }
        
        probability = historical_prob * potential_factor + risk_adjustments[risk_level]
        return max(0.1, min(0.9, probability))
    
    async def _generate_goal_rationale(
        self,
        goal_type: YieldGoalType,
        recommended_yield: float,
        historical_trend: YieldTrendAnalysis,
        potential_assessment: PotentialYieldAssessment
    ) -> str:
        """Generate rationale for the yield goal recommendation."""
        rationales = {
            YieldGoalType.CONSERVATIVE: f"Conservative goal of {recommended_yield:.1f} bu/acre based on historical average of {historical_trend.average_yield:.1f} bu/acre with low risk tolerance.",
            YieldGoalType.REALISTIC: f"Realistic goal of {recommended_yield:.1f} bu/acre considering historical trends and current field potential of {potential_assessment.combined_potential:.1f} bu/acre.",
            YieldGoalType.OPTIMISTIC: f"Optimistic goal of {recommended_yield:.1f} bu/acre targeting above-average performance with good management and favorable conditions.",
            YieldGoalType.STRETCH: f"Stretch goal of {recommended_yield:.1f} bu/acre requiring excellent management, favorable weather, and optimal conditions."
        }
        
        return rationales[goal_type]
    
    async def _identify_supporting_factors(
        self,
        historical_trend: YieldTrendAnalysis,
        potential_assessment: PotentialYieldAssessment,
        goal_type: YieldGoalType
    ) -> List[str]:
        """Identify factors supporting the yield goal."""
        supporting_factors = []
        
        if historical_trend.trend_direction == YieldTrendDirection.INCREASING:
            supporting_factors.append("Positive historical yield trend")
        
        if potential_assessment.combined_potential > historical_trend.average_yield:
            supporting_factors.append("Field potential exceeds historical average")
        
        if len(potential_assessment.improvement_opportunities) > 0:
            supporting_factors.append("Identified improvement opportunities")
        
        if historical_trend.volatility < 0.15:
            supporting_factors.append("Low yield variability")
        
        return supporting_factors
    
    async def _identify_risk_factors(
        self,
        historical_trend: YieldTrendAnalysis,
        potential_assessment: PotentialYieldAssessment,
        goal_type: YieldGoalType
    ) -> List[str]:
        """Identify risk factors for the yield goal."""
        risk_factors = []
        
        if historical_trend.trend_direction == YieldTrendDirection.DECREASING:
            risk_factors.append("Declining historical yield trend")
        
        if historical_trend.volatility > 0.25:
            risk_factors.append("High yield variability")
        
        if len(potential_assessment.limiting_factors) > 3:
            risk_factors.append("Multiple limiting factors present")
        
        if goal_type in [YieldGoalType.OPTIMISTIC, YieldGoalType.STRETCH]:
            risk_factors.append("Ambitious goal requiring optimal conditions")
        
        return risk_factors
    
    async def _assess_overall_risk(
        self,
        historical_trend: YieldTrendAnalysis,
        potential_assessment: PotentialYieldAssessment,
        weather_patterns: Optional[WeatherPattern],
        management_practices: ManagementPractice
    ) -> Tuple[YieldRiskLevel, List[str], List[str]]:
        """Assess overall risk level and generate mitigation strategies."""
        risk_score = 0
        risk_factors = []
        mitigation_strategies = []
        
        # Historical trend risk
        if historical_trend.trend_direction == YieldTrendDirection.DECREASING:
            risk_score += 2
            risk_factors.append("Declining yield trend")
            mitigation_strategies.append("Review and improve management practices")
        
        if historical_trend.volatility > 0.25:
            risk_score += 1
            risk_factors.append("High yield variability")
            mitigation_strategies.append("Implement risk management strategies")
        
        # Potential assessment risk
        if len(potential_assessment.limiting_factors) > 3:
            risk_score += 2
            risk_factors.append("Multiple limiting factors")
            mitigation_strategies.append("Address limiting factors systematically")
        
        # Weather risk
        if weather_patterns:
            if weather_patterns.drought_stress_days > 30:
                risk_score += 1
                risk_factors.append("Drought risk")
                mitigation_strategies.append("Consider irrigation or drought-tolerant varieties")
            
            if weather_patterns.heat_stress_days > 20:
                risk_score += 1
                risk_factors.append("Heat stress risk")
                mitigation_strategies.append("Select heat-tolerant varieties")
        
        # Management risk
        if management_practices.crop_rotation == 'continuous_corn':
            risk_score += 1
            risk_factors.append("Continuous corn rotation")
            mitigation_strategies.append("Implement crop rotation")
        
        # Determine overall risk level
        if risk_score <= 1:
            overall_risk = YieldRiskLevel.LOW
        elif risk_score <= 3:
            overall_risk = YieldRiskLevel.MEDIUM
        elif risk_score <= 5:
            overall_risk = YieldRiskLevel.HIGH
        else:
            overall_risk = YieldRiskLevel.CRITICAL
        
        return overall_risk, risk_factors, mitigation_strategies
    
    async def _calculate_analysis_confidence(self, request: YieldGoalRequest) -> float:
        """Calculate overall confidence in the analysis."""
        confidence_factors = []
        
        # Historical data quality
        if len(request.historical_yields) >= 5:
            confidence_factors.append(0.3)
        elif len(request.historical_yields) >= 3:
            confidence_factors.append(0.2)
        else:
            confidence_factors.append(0.1)
        
        # Weather data availability
        if request.weather_patterns:
            confidence_factors.append(0.2)
        else:
            confidence_factors.append(0.1)
        
        # Soil data completeness
        soil_completeness = 0
        if request.soil_characteristics.ph_level > 0:
            soil_completeness += 1
        if request.soil_characteristics.organic_matter_percent > 0:
            soil_completeness += 1
        if request.soil_characteristics.cation_exchange_capacity > 0:
            soil_completeness += 1
        if request.soil_characteristics.drainage_class:
            soil_completeness += 1
        
        confidence_factors.append(soil_completeness * 0.1)
        
        # Management data completeness
        management_completeness = 0
        if request.management_practices.tillage_system:
            management_completeness += 1
        if request.management_practices.crop_rotation:
            management_completeness += 1
        if request.management_practices.planting_date:
            management_completeness += 1
        
        confidence_factors.append(management_completeness * 0.1)
        
        return min(1.0, sum(confidence_factors))
    
    async def _assess_data_quality(self, request: YieldGoalRequest) -> float:
        """Assess quality of input data."""
        quality_score = 0.0
        
        # Historical data quality
        if len(request.historical_yields) >= 5:
            quality_score += 0.3
        elif len(request.historical_yields) >= 3:
            quality_score += 0.2
        else:
            quality_score += 0.1
        
        # Data completeness
        completeness_score = 0.0
        
        # Soil data completeness
        soil_fields = 6  # Total soil fields
        soil_complete = sum([
            1 if request.soil_characteristics.ph_level > 0 else 0,
            1 if request.soil_characteristics.organic_matter_percent > 0 else 0,
            1 if request.soil_characteristics.cation_exchange_capacity > 0 else 0,
            1 if request.soil_characteristics.drainage_class else 0,
            1 if request.soil_characteristics.slope_percent >= 0 else 0,
            1 if request.soil_characteristics.water_holding_capacity > 0 else 0
        ])
        completeness_score += (soil_complete / soil_fields) * 0.3
        
        # Weather data completeness
        if request.weather_patterns:
            weather_fields = 6  # Total weather fields
            weather_complete = sum([
                1 if request.weather_patterns.growing_season_precipitation > 0 else 0,
                1 if request.weather_patterns.growing_degree_days > 0 else 0,
                1 if request.weather_patterns.drought_stress_days >= 0 else 0,
                1 if request.weather_patterns.heat_stress_days >= 0 else 0,
                1 if request.weather_patterns.frost_risk_days >= 0 else 0,
                1 if request.weather_patterns.optimal_growing_days > 0 else 0
            ])
            completeness_score += (weather_complete / weather_fields) * 0.2
        else:
            completeness_score += 0.0
        
        # Management data completeness
        management_fields = 5  # Total management fields
        management_complete = sum([
            1 if request.management_practices.tillage_system else 0,
            1 if request.management_practices.crop_rotation else 0,
            1 if request.management_practices.planting_date else 0,
            1 if request.management_practices.harvest_date else 0,
            1  # irrigation_available, precision_agriculture, cover_crop_usage are boolean
        ])
        completeness_score += (management_complete / management_fields) * 0.2
        
        quality_score += completeness_score
        
        return min(1.0, quality_score)
    
    async def _prepare_supporting_data(
        self,
        request: YieldGoalRequest,
        historical_trend: YieldTrendAnalysis,
        potential_assessment: PotentialYieldAssessment
    ) -> Dict[str, Any]:
        """Prepare supporting data for the analysis."""
        return {
            "input_summary": {
                "field_id": str(request.field_id),
                "crop_type": request.crop_type,
                "variety": request.variety,
                "target_year": request.target_year,
                "historical_years": len(request.historical_yields),
                "goal_preference": request.goal_preference,
                "risk_tolerance": request.risk_tolerance
            },
            "analysis_parameters": {
                "soil_factor_weights": self.soil_factor_weights,
                "weather_factor_weights": self.weather_factor_weights,
                "management_factor_weights": self.management_factor_weights,
                "crop_yield_baseline": self.crop_yield_baselines.get(request.crop_type, 150.0)
            },
            "calculated_metrics": {
                "historical_average": historical_trend.average_yield,
                "historical_trend_slope": historical_trend.trend_slope,
                "potential_yield": potential_assessment.combined_potential,
                "limiting_factors_count": len(potential_assessment.limiting_factors),
                "improvement_opportunities_count": len(potential_assessment.improvement_opportunities)
            }
        }
    
    async def validate_yield_goal(self, yield_goal: float, analysis: YieldGoalAnalysis) -> YieldGoalValidationResult:
        """Validate a yield goal against the analysis."""
        issues = []
        warnings = []
        recommendations = []
        
        # Check against historical performance
        if yield_goal > analysis.historical_trend.max_yield * 1.3:
            issues.append(f"Goal exceeds historical maximum by more than 30%")
            recommendations.append("Consider more conservative goal")
        
        elif yield_goal > analysis.historical_trend.max_yield * 1.15:
            warnings.append(f"Goal exceeds historical maximum by more than 15%")
        
        # Check against potential assessment
        if yield_goal > analysis.potential_assessment.combined_potential * 1.2:
            issues.append(f"Goal exceeds field potential by more than 20%")
            recommendations.append("Address limiting factors before setting higher goals")
        
        elif yield_goal > analysis.potential_assessment.combined_potential * 1.1:
            warnings.append(f"Goal exceeds field potential by more than 10%")
        
        # Check risk level
        if analysis.overall_risk_level == YieldRiskLevel.CRITICAL and yield_goal > analysis.historical_trend.average_yield * 1.1:
            issues.append("High-risk goal with critical risk factors present")
            recommendations.append("Consider risk mitigation strategies")
        
        # Calculate validation score
        validation_score = 1.0
        validation_score -= len(issues) * 0.3
        validation_score -= len(warnings) * 0.1
        validation_score = max(0.0, validation_score)
        
        is_valid = len(issues) == 0
        
        return YieldGoalValidationResult(
            is_valid=is_valid,
            validation_score=validation_score,
            issues=issues,
            warnings=warnings,
            recommendations=recommendations
        )
    
    async def compare_yield_goals(self, analysis: YieldGoalAnalysis) -> YieldGoalComparison:
        """Compare different yield goal types."""
        recommendations = {rec.goal_type: rec for rec in analysis.goal_recommendations}
        
        # Calculate goal range
        yields = [rec.recommended_yield for rec in recommendations.values()]
        goal_range = max(yields) - min(yields)
        
        # Create risk progression
        risk_progression = {goal_type: rec.risk_level for goal_type, rec in recommendations.items()}
        
        # Create achievement probabilities
        achievement_probabilities = {goal_type: rec.achievement_probability for goal_type, rec in recommendations.items()}
        
        return YieldGoalComparison(
            conservative_goal=recommendations[YieldGoalType.CONSERVATIVE],
            realistic_goal=recommendations[YieldGoalType.REALISTIC],
            optimistic_goal=recommendations[YieldGoalType.OPTIMISTIC],
            stretch_goal=recommendations[YieldGoalType.STRETCH],
            goal_range=goal_range,
            risk_progression=risk_progression,
            achievement_probabilities=achievement_probabilities
        )