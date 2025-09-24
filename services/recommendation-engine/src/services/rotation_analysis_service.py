"""
Rotation Analysis Service
Provides comprehensive analysis of crop rotation plans including benefits,
economic impact, sustainability metrics, and risk assessment.
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
from dataclasses import dataclass
import numpy as np

from ..models.rotation_models import (
    CropRotationPlan, FieldProfile, RotationYear
)


@dataclass
class RotationBenefitAnalysis:
    """Comprehensive rotation benefit analysis."""
    nitrogen_fixation_total: float
    nitrogen_fixation_annual_avg: float
    soil_organic_matter_improvement: float
    erosion_reduction_percent: float
    pest_pressure_reduction: float
    weed_suppression_score: float
    biodiversity_index: float
    carbon_sequestration_tons: float
    water_use_efficiency: float
    overall_sustainability_score: float


@dataclass
class EconomicAnalysis:
    """Economic analysis of rotation plan."""
    total_revenue_projection: float
    total_cost_projection: float
    net_profit_projection: float
    roi_percent: float
    payback_period_years: float
    break_even_yield_adjustments: Dict[str, float]
    risk_adjusted_return: float
    cost_per_acre_annual: float
    revenue_per_acre_annual: float
    profit_margin_percent: float


@dataclass
class SustainabilityMetrics:
    """Sustainability metrics for rotation."""
    environmental_impact_score: float
    resource_efficiency_score: float
    soil_health_trajectory: List[float]  # Year-over-year soil health scores
    carbon_footprint_reduction: float
    water_conservation_score: float
    biodiversity_enhancement: float
    long_term_viability_score: float


@dataclass
class RiskAssessment:
    """Risk assessment for rotation plan."""
    weather_risk_score: float
    market_risk_score: float
    pest_disease_risk_score: float
    yield_variability_risk: float
    input_cost_risk: float
    overall_risk_score: float
    risk_mitigation_strategies: List[str]
    confidence_intervals: Dict[str, Tuple[float, float]]


class RotationAnalysisService:
    """Service for analyzing crop rotation plans."""
    
    def __init__(self):
        self.crop_economic_data = self._initialize_crop_economics()
        self.sustainability_factors = self._initialize_sustainability_factors()
        self.risk_factors = self._initialize_risk_factors()
    
    def _initialize_crop_economics(self) -> Dict[str, Dict[str, float]]:
        """Initialize crop economic data."""
        return {
            'corn': {
                'price_per_unit': 4.25,  # $/bushel
                'yield_units': 'bushels',
                'production_cost_per_acre': 450.0,
                'variable_cost_per_acre': 350.0,
                'fixed_cost_per_acre': 100.0,
                'price_volatility': 0.15,
                'yield_volatility': 0.12
            },
            'soybean': {
                'price_per_unit': 12.50,  # $/bushel
                'yield_units': 'bushels',
                'production_cost_per_acre': 380.0,
                'variable_cost_per_acre': 280.0,
                'fixed_cost_per_acre': 100.0,
                'price_volatility': 0.18,
                'yield_volatility': 0.14
            },
            'wheat': {
                'price_per_unit': 6.80,  # $/bushel
                'yield_units': 'bushels',
                'production_cost_per_acre': 320.0,
                'variable_cost_per_acre': 220.0,
                'fixed_cost_per_acre': 100.0,
                'price_volatility': 0.22,
                'yield_volatility': 0.16
            },
            'oats': {
                'price_per_unit': 3.20,  # $/bushel
                'yield_units': 'bushels',
                'production_cost_per_acre': 280.0,
                'variable_cost_per_acre': 180.0,
                'fixed_cost_per_acre': 100.0,
                'price_volatility': 0.25,
                'yield_volatility': 0.18
            },
            'alfalfa': {
                'price_per_unit': 180.0,  # $/ton
                'yield_units': 'tons',
                'production_cost_per_acre': 420.0,
                'variable_cost_per_acre': 320.0,
                'fixed_cost_per_acre': 100.0,
                'price_volatility': 0.12,
                'yield_volatility': 0.10
            },
            'barley': {
                'price_per_unit': 4.50,  # $/bushel
                'yield_units': 'bushels',
                'production_cost_per_acre': 300.0,
                'variable_cost_per_acre': 200.0,
                'fixed_cost_per_acre': 100.0,
                'price_volatility': 0.20,
                'yield_volatility': 0.15
            }
        }
    
    def _initialize_sustainability_factors(self) -> Dict[str, Dict[str, float]]:
        """Initialize sustainability factors for crops."""
        return {
            'corn': {
                'carbon_sequestration': 0.5,  # tons CO2/acre/year
                'water_use_efficiency': 6.0,  # relative score
                'soil_erosion_factor': 0.8,  # higher = more erosion
                'biodiversity_support': 3.0,  # relative score
                'nitrogen_leaching_risk': 0.7
            },
            'soybean': {
                'carbon_sequestration': 0.8,
                'water_use_efficiency': 7.5,
                'soil_erosion_factor': 0.6,
                'biodiversity_support': 5.0,
                'nitrogen_leaching_risk': 0.3
            },
            'wheat': {
                'carbon_sequestration': 0.6,
                'water_use_efficiency': 8.0,
                'soil_erosion_factor': 0.4,
                'biodiversity_support': 6.0,
                'nitrogen_leaching_risk': 0.5
            },
            'oats': {
                'carbon_sequestration': 0.7,
                'water_use_efficiency': 7.8,
                'soil_erosion_factor': 0.3,
                'biodiversity_support': 6.5,
                'nitrogen_leaching_risk': 0.4
            },
            'alfalfa': {
                'carbon_sequestration': 1.2,
                'water_use_efficiency': 6.5,
                'soil_erosion_factor': 0.2,
                'biodiversity_support': 8.0,
                'nitrogen_leaching_risk': 0.1
            },
            'barley': {
                'carbon_sequestration': 0.6,
                'water_use_efficiency': 7.5,
                'soil_erosion_factor': 0.4,
                'biodiversity_support': 5.5,
                'nitrogen_leaching_risk': 0.5
            }
        }
    
    def _initialize_risk_factors(self) -> Dict[str, Dict[str, float]]:
        """Initialize risk factors for crops."""
        return {
            'corn': {
                'weather_sensitivity': 0.7,
                'pest_pressure_risk': 0.6,
                'disease_pressure_risk': 0.5,
                'market_volatility': 0.15
            },
            'soybean': {
                'weather_sensitivity': 0.6,
                'pest_pressure_risk': 0.5,
                'disease_pressure_risk': 0.4,
                'market_volatility': 0.18
            },
            'wheat': {
                'weather_sensitivity': 0.8,
                'pest_pressure_risk': 0.4,
                'disease_pressure_risk': 0.6,
                'market_volatility': 0.22
            },
            'oats': {
                'weather_sensitivity': 0.7,
                'pest_pressure_risk': 0.3,
                'disease_pressure_risk': 0.4,
                'market_volatility': 0.25
            },
            'alfalfa': {
                'weather_sensitivity': 0.5,
                'pest_pressure_risk': 0.3,
                'disease_pressure_risk': 0.3,
                'market_volatility': 0.12
            },
            'barley': {
                'weather_sensitivity': 0.7,
                'pest_pressure_risk': 0.4,
                'disease_pressure_risk': 0.5,
                'market_volatility': 0.20
            }
        }
    
    async def analyze_rotation_benefits(
        self, 
        rotation_plan: CropRotationPlan,
        field_profile: FieldProfile
    ) -> RotationBenefitAnalysis:
        """Analyze comprehensive benefits of rotation plan."""
        
        crop_sequence = rotation_plan.get_crop_sequence()
        
        # Calculate nitrogen fixation benefits
        nitrogen_fixation = self._calculate_nitrogen_fixation(crop_sequence)
        
        # Calculate soil health improvements
        soil_improvement = self._calculate_soil_health_improvement(crop_sequence)
        
        # Calculate pest and disease management benefits
        pest_management = self._calculate_pest_management_benefits(crop_sequence)
        
        # Calculate biodiversity benefits
        biodiversity = self._calculate_biodiversity_index(crop_sequence)
        
        # Calculate carbon sequestration
        carbon_sequestration = self._calculate_carbon_sequestration(
            crop_sequence, field_profile.size_acres
        )
        
        # Calculate water use efficiency
        water_efficiency = self._calculate_water_use_efficiency(crop_sequence)
        
        # Calculate overall sustainability score
        sustainability_score = self._calculate_sustainability_score(
            nitrogen_fixation, soil_improvement, pest_management,
            biodiversity, carbon_sequestration, water_efficiency
        )
        
        return RotationBenefitAnalysis(
            nitrogen_fixation_total=nitrogen_fixation['total'],
            nitrogen_fixation_annual_avg=nitrogen_fixation['annual_average'],
            soil_organic_matter_improvement=soil_improvement['organic_matter'],
            erosion_reduction_percent=soil_improvement['erosion_reduction'],
            pest_pressure_reduction=pest_management['pest_reduction'],
            weed_suppression_score=pest_management['weed_suppression'],
            biodiversity_index=biodiversity,
            carbon_sequestration_tons=carbon_sequestration,
            water_use_efficiency=water_efficiency,
            overall_sustainability_score=sustainability_score
        )
    
    async def analyze_economic_impact(
        self,
        rotation_plan: CropRotationPlan,
        field_profile: FieldProfile,
        market_conditions: Optional[Dict[str, Any]] = None
    ) -> EconomicAnalysis:
        """Analyze economic impact of rotation plan."""
        
        crop_sequence = rotation_plan.get_crop_sequence()
        field_size = field_profile.size_acres
        
        # Calculate revenue projections
        total_revenue = 0
        total_costs = 0
        annual_revenues = []
        annual_costs = []
        
        for i, rotation_year in enumerate(rotation_plan.rotation_years):
            crop = rotation_year.crop_name
            estimated_yield = rotation_year.estimated_yield
            
            crop_economics = self.crop_economic_data.get(crop, {})
            
            # Calculate revenue
            price_per_unit = crop_economics.get('price_per_unit', 0)
            revenue = estimated_yield * price_per_unit * field_size
            annual_revenues.append(revenue)
            total_revenue += revenue
            
            # Calculate costs
            cost_per_acre = crop_economics.get('production_cost_per_acre', 0)
            
            # Apply rotation benefits to reduce costs
            cost_reduction = self._calculate_cost_reduction_from_rotation(
                crop, i, crop_sequence
            )
            adjusted_cost_per_acre = cost_per_acre * (1 - cost_reduction)
            
            costs = adjusted_cost_per_acre * field_size
            annual_costs.append(costs)
            total_costs += costs
        
        # Calculate financial metrics
        net_profit = total_revenue - total_costs
        roi_percent = (net_profit / total_costs * 100) if total_costs > 0 else 0
        
        # Calculate risk-adjusted return
        risk_adjustment = self._calculate_risk_adjustment(crop_sequence)
        risk_adjusted_return = net_profit * (1 - risk_adjustment)
        
        # Calculate break-even adjustments
        break_even_adjustments = self._calculate_break_even_adjustments(
            rotation_plan, field_profile
        )
        
        return EconomicAnalysis(
            total_revenue_projection=total_revenue,
            total_cost_projection=total_costs,
            net_profit_projection=net_profit,
            roi_percent=roi_percent,
            payback_period_years=self._calculate_payback_period(annual_revenues, annual_costs),
            break_even_yield_adjustments=break_even_adjustments,
            risk_adjusted_return=risk_adjusted_return,
            cost_per_acre_annual=total_costs / (field_size * len(crop_sequence)),
            revenue_per_acre_annual=total_revenue / (field_size * len(crop_sequence)),
            profit_margin_percent=(net_profit / total_revenue * 100) if total_revenue > 0 else 0
        )
    
    async def calculate_sustainability_metrics(
        self,
        rotation_plan: CropRotationPlan,
        field_profile: FieldProfile
    ) -> SustainabilityMetrics:
        """Calculate sustainability metrics for rotation."""
        
        crop_sequence = rotation_plan.get_crop_sequence()
        
        # Environmental impact score
        environmental_score = self._calculate_environmental_impact_score(crop_sequence)
        
        # Resource efficiency score
        resource_efficiency = self._calculate_resource_efficiency_score(crop_sequence)
        
        # Soil health trajectory
        soil_health_trajectory = self._calculate_soil_health_trajectory(crop_sequence)
        
        # Carbon footprint reduction
        carbon_reduction = self._calculate_carbon_footprint_reduction(crop_sequence)
        
        # Water conservation score
        water_conservation = self._calculate_water_conservation_score(crop_sequence)
        
        # Biodiversity enhancement
        biodiversity_enhancement = self._calculate_biodiversity_enhancement(crop_sequence)
        
        # Long-term viability
        long_term_viability = self._calculate_long_term_viability(crop_sequence)
        
        return SustainabilityMetrics(
            environmental_impact_score=environmental_score,
            resource_efficiency_score=resource_efficiency,
            soil_health_trajectory=soil_health_trajectory,
            carbon_footprint_reduction=carbon_reduction,
            water_conservation_score=water_conservation,
            biodiversity_enhancement=biodiversity_enhancement,
            long_term_viability_score=long_term_viability
        )
    
    async def assess_rotation_risks(
        self,
        rotation_plan: CropRotationPlan,
        field_profile: FieldProfile,
        historical_data: Optional[Dict[str, Any]] = None
    ) -> RiskAssessment:
        """Assess risks associated with rotation plan."""
        
        crop_sequence = rotation_plan.get_crop_sequence()
        
        # Weather risk assessment
        weather_risk = self._assess_weather_risk(crop_sequence, field_profile)
        
        # Market risk assessment
        market_risk = self._assess_market_risk(crop_sequence)
        
        # Pest and disease risk assessment
        pest_disease_risk = self._assess_pest_disease_risk(crop_sequence)
        
        # Yield variability risk
        yield_risk = self._assess_yield_variability_risk(crop_sequence)
        
        # Input cost risk
        input_cost_risk = self._assess_input_cost_risk(crop_sequence)
        
        # Overall risk score
        overall_risk = self._calculate_overall_risk_score(
            weather_risk, market_risk, pest_disease_risk, yield_risk, input_cost_risk
        )
        
        # Risk mitigation strategies
        mitigation_strategies = self._generate_risk_mitigation_strategies(
            crop_sequence, weather_risk, market_risk, pest_disease_risk
        )
        
        # Confidence intervals
        confidence_intervals = self._calculate_confidence_intervals(rotation_plan)
        
        return RiskAssessment(
            weather_risk_score=weather_risk,
            market_risk_score=market_risk,
            pest_disease_risk_score=pest_disease_risk,
            yield_variability_risk=yield_risk,
            input_cost_risk=input_cost_risk,
            overall_risk_score=overall_risk,
            risk_mitigation_strategies=mitigation_strategies,
            confidence_intervals=confidence_intervals
        )
    
    async def compare_rotation_scenarios(
        self,
        rotation_plans: List[CropRotationPlan],
        field_profile: FieldProfile,
        comparison_criteria: List[str]
    ) -> Dict[str, Any]:
        """Compare multiple rotation scenarios."""
        
        comparison_results = {
            'scenarios': [],
            'rankings': {},
            'trade_offs': {},
            'recommendations': []
        }
        
        # Analyze each scenario
        for i, plan in enumerate(rotation_plans):
            scenario_name = f"Scenario_{i+1}"
            
            # Get analyses for this scenario
            benefits = await self.analyze_rotation_benefits(plan, field_profile)
            economics = await self.analyze_economic_impact(plan, field_profile)
            sustainability = await self.calculate_sustainability_metrics(plan, field_profile)
            risks = await self.assess_rotation_risks(plan, field_profile)
            
            scenario_data = {
                'name': scenario_name,
                'crop_sequence': plan.get_crop_sequence(),
                'benefits': benefits,
                'economics': economics,
                'sustainability': sustainability,
                'risks': risks,
                'overall_score': plan.overall_score
            }
            
            comparison_results['scenarios'].append(scenario_data)
        
        # Rank scenarios by different criteria
        for criterion in comparison_criteria:
            ranking = self._rank_scenarios_by_criterion(
                comparison_results['scenarios'], criterion
            )
            comparison_results['rankings'][criterion] = ranking
        
        # Identify trade-offs
        comparison_results['trade_offs'] = self._identify_trade_offs(
            comparison_results['scenarios']
        )
        
        # Generate recommendations
        comparison_results['recommendations'] = self._generate_scenario_recommendations(
            comparison_results['scenarios'], comparison_results['rankings']
        )
        
        return comparison_results
    
    def _calculate_nitrogen_fixation(self, crop_sequence: List[str]) -> Dict[str, float]:
        """Calculate nitrogen fixation benefits."""
        nitrogen_fixing_crops = {
            'soybean': 40,  # lbs N/acre
            'alfalfa': 150,
            'clover': 100,
            'peas': 60
        }
        
        total_fixation = 0
        for crop in crop_sequence:
            fixation = nitrogen_fixing_crops.get(crop, 0)
            total_fixation += fixation
        
        return {
            'total': total_fixation,
            'annual_average': total_fixation / len(crop_sequence)
        }
    
    def _calculate_soil_health_improvement(self, crop_sequence: List[str]) -> Dict[str, float]:
        """Calculate soil health improvement metrics."""
        
        # Soil organic matter contribution by crop
        om_contribution = {
            'corn': 2.5,
            'soybean': 4.0,
            'wheat': 3.5,
            'oats': 4.5,
            'alfalfa': 8.5,
            'barley': 4.0
        }
        
        # Erosion control rating by crop
        erosion_control = {
            'corn': 3.0,
            'soybean': 2.5,
            'wheat': 6.0,
            'oats': 5.5,
            'alfalfa': 9.0,
            'barley': 5.0
        }
        
        total_om = sum(om_contribution.get(crop, 0) for crop in crop_sequence)
        avg_erosion_control = np.mean([erosion_control.get(crop, 0) for crop in crop_sequence])
        
        # Calculate improvement percentages
        om_improvement = min(50, total_om / len(crop_sequence) * 5)  # Cap at 50%
        erosion_reduction = min(80, avg_erosion_control * 8)  # Cap at 80%
        
        return {
            'organic_matter': om_improvement,
            'erosion_reduction': erosion_reduction
        }
    
    def _calculate_pest_management_benefits(self, crop_sequence: List[str]) -> Dict[str, float]:
        """Calculate pest and disease management benefits."""
        
        # Diversity bonus for pest management
        unique_crops = len(set(crop_sequence))
        diversity_bonus = min(50, unique_crops * 10)
        
        # Weed suppression by crop
        weed_suppression = {
            'corn': 3.5,
            'soybean': 2.0,
            'wheat': 7.0,
            'oats': 6.5,
            'alfalfa': 8.0,
            'barley': 6.0
        }
        
        avg_weed_suppression = np.mean([weed_suppression.get(crop, 0) for crop in crop_sequence])
        
        return {
            'pest_reduction': diversity_bonus,
            'weed_suppression': avg_weed_suppression * 10  # Scale to 0-100
        }
    
    def _calculate_biodiversity_index(self, crop_sequence: List[str]) -> float:
        """Calculate biodiversity index for rotation."""
        
        # Shannon diversity index
        from collections import Counter
        
        crop_counts = Counter(crop_sequence)
        total_crops = len(crop_sequence)
        
        shannon_index = 0
        for count in crop_counts.values():
            proportion = count / total_crops
            if proportion > 0:
                shannon_index -= proportion * np.log(proportion)
        
        # Normalize to 0-100 scale
        max_possible_diversity = np.log(len(set(crop_sequence)))
        if max_possible_diversity > 0:
            normalized_index = (shannon_index / max_possible_diversity) * 100
        else:
            normalized_index = 0
        
        return normalized_index
    
    def _calculate_carbon_sequestration(self, crop_sequence: List[str], field_size: float) -> float:
        """Calculate total carbon sequestration."""
        
        total_sequestration = 0
        for crop in crop_sequence:
            crop_factors = self.sustainability_factors.get(crop, {})
            sequestration_rate = crop_factors.get('carbon_sequestration', 0)
            total_sequestration += sequestration_rate * field_size
        
        return total_sequestration
    
    def _calculate_water_use_efficiency(self, crop_sequence: List[str]) -> float:
        """Calculate water use efficiency score."""
        
        efficiency_scores = []
        for crop in crop_sequence:
            crop_factors = self.sustainability_factors.get(crop, {})
            efficiency = crop_factors.get('water_use_efficiency', 5.0)
            efficiency_scores.append(efficiency)
        
        return np.mean(efficiency_scores) * 10  # Scale to 0-100
    
    def _calculate_sustainability_score(
        self, 
        nitrogen_fixation: Dict[str, float],
        soil_improvement: Dict[str, float],
        pest_management: Dict[str, float],
        biodiversity: float,
        carbon_sequestration: float,
        water_efficiency: float
    ) -> float:
        """Calculate overall sustainability score."""
        
        # Weighted combination of sustainability factors
        score = (
            nitrogen_fixation['annual_average'] * 0.2 +
            soil_improvement['organic_matter'] * 0.2 +
            pest_management['pest_reduction'] * 0.15 +
            biodiversity * 0.15 +
            min(100, carbon_sequestration * 10) * 0.15 +
            water_efficiency * 0.15
        )
        
        return min(100, score)
    
    def _calculate_cost_reduction_from_rotation(
        self, 
        crop: str, 
        position: int, 
        crop_sequence: List[str]
    ) -> float:
        """Calculate cost reduction from rotation benefits."""
        
        cost_reduction = 0
        
        # Nitrogen credit from previous legumes
        if position > 0:
            previous_crop = crop_sequence[position - 1]
            if previous_crop in ['soybean', 'alfalfa', 'clover']:
                if crop == 'corn':
                    # Reduce nitrogen fertilizer costs
                    if previous_crop == 'soybean':
                        cost_reduction += 0.08  # 8% cost reduction
                    elif previous_crop == 'alfalfa':
                        cost_reduction += 0.15  # 15% cost reduction
        
        # Pest management benefits
        unique_crops_before = len(set(crop_sequence[:position+1]))
        if unique_crops_before > 1:
            cost_reduction += 0.02 * (unique_crops_before - 1)  # 2% per additional crop type
        
        return min(0.25, cost_reduction)  # Cap at 25% cost reduction
    
    def _calculate_risk_adjustment(self, crop_sequence: List[str]) -> float:
        """Calculate risk adjustment factor."""
        
        # Diversification reduces risk
        unique_crops = len(set(crop_sequence))
        total_positions = len(crop_sequence)
        
        diversification_ratio = unique_crops / total_positions
        
        # Higher diversification = lower risk adjustment
        risk_adjustment = 0.2 * (1 - diversification_ratio)
        
        return max(0, min(0.2, risk_adjustment))
    
    def _calculate_break_even_adjustments(
        self,
        rotation_plan: CropRotationPlan,
        field_profile: FieldProfile
    ) -> Dict[str, float]:
        """Calculate break-even yield adjustments needed."""
        
        adjustments = {}
        
        for rotation_year in rotation_plan.rotation_years:
            crop = rotation_year.crop_name
            estimated_yield = rotation_year.estimated_yield
            
            crop_economics = self.crop_economic_data.get(crop, {})
            price_per_unit = crop_economics.get('price_per_unit', 0)
            cost_per_acre = crop_economics.get('production_cost_per_acre', 0)
            
            if price_per_unit > 0:
                break_even_yield = cost_per_acre / price_per_unit
                adjustment_needed = (break_even_yield - estimated_yield) / estimated_yield
                adjustments[f"{rotation_year.year}_{crop}"] = adjustment_needed
        
        return adjustments
    
    def _calculate_payback_period(
        self, 
        annual_revenues: List[float], 
        annual_costs: List[float]
    ) -> float:
        """Calculate payback period for rotation investment."""
        
        cumulative_cash_flow = 0
        
        for i, (revenue, cost) in enumerate(zip(annual_revenues, annual_costs)):
            net_cash_flow = revenue - cost
            cumulative_cash_flow += net_cash_flow
            
            if cumulative_cash_flow >= 0:
                return i + 1
        
        return len(annual_revenues)  # Return full period if never breaks even
    
    def _assess_weather_risk(self, crop_sequence: List[str], field_profile: FieldProfile) -> float:
        """Assess weather-related risks."""
        
        weather_sensitivities = []
        for crop in crop_sequence:
            risk_factors = self.risk_factors.get(crop, {})
            sensitivity = risk_factors.get('weather_sensitivity', 0.5)
            weather_sensitivities.append(sensitivity)
        
        avg_sensitivity = np.mean(weather_sensitivities)
        
        # Adjust for field characteristics
        if hasattr(field_profile, 'irrigation_available') and field_profile.irrigation_available:
            avg_sensitivity *= 0.7  # Irrigation reduces weather risk
        
        return avg_sensitivity * 100
    
    def _assess_market_risk(self, crop_sequence: List[str]) -> float:
        """Assess market-related risks."""
        
        market_volatilities = []
        for crop in crop_sequence:
            crop_economics = self.crop_economic_data.get(crop, {})
            volatility = crop_economics.get('price_volatility', 0.2)
            market_volatilities.append(volatility)
        
        # Portfolio effect - diversification reduces risk
        if len(set(crop_sequence)) > 1:
            portfolio_volatility = np.sqrt(np.mean([v**2 for v in market_volatilities]))
        else:
            portfolio_volatility = np.mean(market_volatilities)
        
        return portfolio_volatility * 100
    
    def _assess_pest_disease_risk(self, crop_sequence: List[str]) -> float:
        """Assess pest and disease risks."""
        
        # Continuous cropping increases risk
        risk_score = 0
        
        for i in range(1, len(crop_sequence)):
            if crop_sequence[i] == crop_sequence[i-1]:
                # Same crop consecutive years increases risk
                risk_score += 20
        
        # Diversity reduces risk
        unique_crops = len(set(crop_sequence))
        diversity_reduction = (unique_crops - 1) * 5
        
        final_risk = max(0, risk_score - diversity_reduction)
        return min(100, final_risk)
    
    def _assess_yield_variability_risk(self, crop_sequence: List[str]) -> float:
        """Assess yield variability risks."""
        
        yield_volatilities = []
        for crop in crop_sequence:
            crop_economics = self.crop_economic_data.get(crop, {})
            volatility = crop_economics.get('yield_volatility', 0.15)
            yield_volatilities.append(volatility)
        
        avg_volatility = np.mean(yield_volatilities)
        return avg_volatility * 100
    
    def _assess_input_cost_risk(self, crop_sequence: List[str]) -> float:
        """Assess input cost risks."""
        
        # Crops with higher input requirements have higher cost risk
        input_intensities = {
            'corn': 0.8,
            'soybean': 0.5,
            'wheat': 0.6,
            'oats': 0.4,
            'alfalfa': 0.7,
            'barley': 0.5
        }
        
        intensities = [input_intensities.get(crop, 0.6) for crop in crop_sequence]
        avg_intensity = np.mean(intensities)
        
        return avg_intensity * 100
    
    def _calculate_overall_risk_score(
        self,
        weather_risk: float,
        market_risk: float,
        pest_disease_risk: float,
        yield_risk: float,
        input_cost_risk: float
    ) -> float:
        """Calculate overall risk score."""
        
        # Weighted combination of risk factors
        overall_risk = (
            weather_risk * 0.25 +
            market_risk * 0.25 +
            pest_disease_risk * 0.2 +
            yield_risk * 0.15 +
            input_cost_risk * 0.15
        )
        
        return overall_risk
    
    def _generate_risk_mitigation_strategies(
        self,
        crop_sequence: List[str],
        weather_risk: float,
        market_risk: float,
        pest_disease_risk: float
    ) -> List[str]:
        """Generate risk mitigation strategies."""
        
        strategies = []
        
        if weather_risk > 60:
            strategies.append("Consider crop insurance for weather protection")
            strategies.append("Implement soil moisture monitoring")
            strategies.append("Consider drought-tolerant varieties")
        
        if market_risk > 50:
            strategies.append("Use forward contracts to lock in prices")
            strategies.append("Consider diversifying marketing timing")
            strategies.append("Explore value-added marketing opportunities")
        
        if pest_disease_risk > 40:
            strategies.append("Implement integrated pest management")
            strategies.append("Scout fields regularly during growing season")
            strategies.append("Consider resistant varieties where available")
        
        # Diversification strategies
        unique_crops = len(set(crop_sequence))
        if unique_crops < 3:
            strategies.append("Consider adding more crop diversity to rotation")
        
        return strategies
    
    def _calculate_confidence_intervals(
        self, 
        rotation_plan: CropRotationPlan
    ) -> Dict[str, Tuple[float, float]]:
        """Calculate confidence intervals for key metrics."""
        
        intervals = {}
        
        # Yield confidence intervals (assuming 90% confidence)
        for rotation_year in rotation_plan.rotation_years:
            crop = rotation_year.crop_name
            estimated_yield = rotation_year.estimated_yield
            
            crop_economics = self.crop_economic_data.get(crop, {})
            yield_volatility = crop_economics.get('yield_volatility', 0.15)
            
            # 90% confidence interval
            margin = 1.645 * yield_volatility * estimated_yield
            lower_bound = estimated_yield - margin
            upper_bound = estimated_yield + margin
            
            intervals[f"{rotation_year.year}_{crop}_yield"] = (lower_bound, upper_bound)
        
        return intervals
    
    def _rank_scenarios_by_criterion(
        self, 
        scenarios: List[Dict[str, Any]], 
        criterion: str
    ) -> List[Dict[str, Any]]:
        """Rank scenarios by specific criterion."""
        
        def get_criterion_value(scenario):
            if criterion == 'profitability':
                return scenario['economics'].net_profit_projection
            elif criterion == 'sustainability':
                return scenario['sustainability'].environmental_impact_score
            elif criterion == 'risk':
                return -scenario['risks'].overall_risk_score  # Lower risk is better
            elif criterion == 'overall_score':
                return scenario['overall_score']
            else:
                return 0
        
        ranked = sorted(scenarios, key=get_criterion_value, reverse=True)
        
        # Add ranking information
        for i, scenario in enumerate(ranked):
            scenario[f'{criterion}_rank'] = i + 1
        
        return ranked
    
    def _identify_trade_offs(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify trade-offs between scenarios."""
        
        trade_offs = {
            'profit_vs_sustainability': [],
            'profit_vs_risk': [],
            'sustainability_vs_risk': []
        }
        
        for scenario in scenarios:
            profit = scenario['economics'].net_profit_projection
            sustainability = scenario['sustainability'].environmental_impact_score
            risk = scenario['risks'].overall_risk_score
            
            trade_offs['profit_vs_sustainability'].append({
                'scenario': scenario['name'],
                'profit': profit,
                'sustainability': sustainability
            })
            
            trade_offs['profit_vs_risk'].append({
                'scenario': scenario['name'],
                'profit': profit,
                'risk': risk
            })
            
            trade_offs['sustainability_vs_risk'].append({
                'scenario': scenario['name'],
                'sustainability': sustainability,
                'risk': risk
            })
        
        return trade_offs
    
    def _generate_scenario_recommendations(
        self,
        scenarios: List[Dict[str, Any]],
        rankings: Dict[str, List[Dict[str, Any]]]
    ) -> List[str]:
        """Generate recommendations based on scenario analysis."""
        
        recommendations = []
        
        # Find best overall scenario
        if 'overall_score' in rankings:
            best_overall = rankings['overall_score'][0]
            recommendations.append(
                f"Scenario '{best_overall['name']}' has the highest overall score "
                f"({best_overall['overall_score']:.1f}) and is recommended for balanced performance."
            )
        
        # Find most profitable scenario
        if 'profitability' in rankings:
            most_profitable = rankings['profitability'][0]
            profit = most_profitable['economics'].net_profit_projection
            recommendations.append(
                f"For maximum profitability, consider Scenario '{most_profitable['name']}' "
                f"with projected net profit of ${profit:,.0f}."
            )
        
        # Find most sustainable scenario
        if 'sustainability' in rankings:
            most_sustainable = rankings['sustainability'][0]
            sustainability_score = most_sustainable['sustainability'].environmental_impact_score
            recommendations.append(
                f"For environmental sustainability, Scenario '{most_sustainable['name']}' "
                f"scores highest ({sustainability_score:.1f}) in environmental impact."
            )
        
        # Risk considerations
        if 'risk' in rankings:
            lowest_risk = rankings['risk'][0]
            risk_score = lowest_risk['risks'].overall_risk_score
            recommendations.append(
                f"For risk-averse farmers, Scenario '{lowest_risk['name']}' "
                f"has the lowest risk score ({risk_score:.1f})."
            )
        
        return recommendations
    
    # Additional helper methods for sustainability calculations
    
    def _calculate_environmental_impact_score(self, crop_sequence: List[str]) -> float:
        """Calculate environmental impact score."""
        
        impact_scores = []
        for crop in crop_sequence:
            factors = self.sustainability_factors.get(crop, {})
            
            # Lower erosion factor and nitrogen leaching = better environmental impact
            erosion_factor = factors.get('soil_erosion_factor', 0.5)
            nitrogen_leaching = factors.get('nitrogen_leaching_risk', 0.5)
            
            # Convert to positive impact score (lower is better becomes higher score)
            impact_score = (2 - erosion_factor - nitrogen_leaching) * 50
            impact_scores.append(impact_score)
        
        return np.mean(impact_scores)
    
    def _calculate_resource_efficiency_score(self, crop_sequence: List[str]) -> float:
        """Calculate resource efficiency score."""
        
        efficiency_scores = []
        for crop in crop_sequence:
            factors = self.sustainability_factors.get(crop, {})
            water_efficiency = factors.get('water_use_efficiency', 5.0)
            efficiency_scores.append(water_efficiency)
        
        return np.mean(efficiency_scores) * 10  # Scale to 0-100
    
    def _calculate_soil_health_trajectory(self, crop_sequence: List[str]) -> List[float]:
        """Calculate year-over-year soil health improvement."""
        
        base_score = 50.0  # Starting soil health score
        trajectory = [base_score]
        
        for crop in crop_sequence:
            factors = self.sustainability_factors.get(crop, {})
            
            # Soil improvement factors
            carbon_seq = factors.get('carbon_sequestration', 0.5)
            erosion_factor = factors.get('soil_erosion_factor', 0.5)
            
            # Calculate improvement
            improvement = carbon_seq * 5 - erosion_factor * 3
            new_score = min(100, max(0, trajectory[-1] + improvement))
            trajectory.append(new_score)
        
        return trajectory[1:]  # Return trajectory without starting point
    
    def _calculate_carbon_footprint_reduction(self, crop_sequence: List[str]) -> float:
        """Calculate carbon footprint reduction percentage."""
        
        # Baseline carbon footprint (conventional monoculture)
        baseline_footprint = 100.0
        
        # Calculate actual footprint
        sequestration_total = 0
        for crop in crop_sequence:
            factors = self.sustainability_factors.get(crop, {})
            sequestration = factors.get('carbon_sequestration', 0.5)
            sequestration_total += sequestration
        
        # Convert sequestration to footprint reduction
        avg_sequestration = sequestration_total / len(crop_sequence)
        footprint_reduction = min(50, avg_sequestration * 25)  # Cap at 50% reduction
        
        return footprint_reduction
    
    def _calculate_water_conservation_score(self, crop_sequence: List[str]) -> float:
        """Calculate water conservation score."""
        
        conservation_scores = []
        for crop in crop_sequence:
            factors = self.sustainability_factors.get(crop, {})
            water_efficiency = factors.get('water_use_efficiency', 5.0)
            conservation_scores.append(water_efficiency)
        
        return np.mean(conservation_scores) * 10
    
    def _calculate_biodiversity_enhancement(self, crop_sequence: List[str]) -> float:
        """Calculate biodiversity enhancement score."""
        
        biodiversity_scores = []
        for crop in crop_sequence:
            factors = self.sustainability_factors.get(crop, {})
            biodiversity_support = factors.get('biodiversity_support', 5.0)
            biodiversity_scores.append(biodiversity_support)
        
        avg_support = np.mean(biodiversity_scores)
        
        # Bonus for diversity
        unique_crops = len(set(crop_sequence))
        diversity_bonus = unique_crops * 2
        
        return min(100, (avg_support * 8) + diversity_bonus)
    
    def _calculate_long_term_viability(self, crop_sequence: List[str]) -> float:
        """Calculate long-term viability score."""
        
        # Factors affecting long-term viability
        diversity_score = len(set(crop_sequence)) / len(crop_sequence) * 100
        
        # Soil health contribution
        soil_health_contribution = 0
        for crop in crop_sequence:
            factors = self.sustainability_factors.get(crop, {})
            carbon_seq = factors.get('carbon_sequestration', 0.5)
            soil_health_contribution += carbon_seq
        
        soil_health_score = min(100, soil_health_contribution * 20)
        
        # Economic sustainability (simplified)
        economic_sustainability = 70.0  # Placeholder
        
        # Weighted combination
        viability_score = (
            diversity_score * 0.3 +
            soil_health_score * 0.4 +
            economic_sustainability * 0.3
        )
        
        return viability_score