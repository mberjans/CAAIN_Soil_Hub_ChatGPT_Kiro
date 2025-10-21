"""
Fertilizer Cost Analysis and Comparison Engine

Comprehensive cost analysis service for fertilizer type selection including:
- Detailed cost breakdown by fertilizer type
- Multi-year cost projections
- Cost comparison across fertilizer options
- Break-even analysis
- ROI calculations
- Scenario-based cost modeling
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class CostCategory(str, Enum):
    """Categories of costs in fertilizer analysis."""
    PRODUCT_COST = "product_cost"
    APPLICATION_COST = "application_cost"
    EQUIPMENT_COST = "equipment_cost"
    LABOR_COST = "labor_cost"
    STORAGE_COST = "storage_cost"
    TRANSPORTATION_COST = "transportation_cost"
    OPPORTUNITY_COST = "opportunity_cost"


@dataclass
class FertilizerCostBreakdown:
    """Detailed cost breakdown for a fertilizer option."""
    fertilizer_id: str
    fertilizer_name: str
    fertilizer_type: str
    
    # Direct costs per acre
    product_cost_per_acre: float
    application_cost_per_acre: float
    equipment_cost_per_acre: float
    labor_cost_per_acre: float
    storage_cost_per_acre: float
    transportation_cost_per_acre: float
    
    # Total costs
    total_cost_per_acre: float
    total_cost_per_unit_nutrient: float  # Cost per unit of NPK
    
    # Cost components breakdown
    cost_components: Dict[str, float]
    cost_percentages: Dict[str, float]
    
    # Efficiency metrics
    nutrient_efficiency_score: float
    cost_efficiency_score: float
    
    # Time period
    analysis_date: datetime
    assumptions_used: Dict[str, Any]


@dataclass
class CostComparison:
    """Comparison of costs between fertilizer options."""
    comparison_id: str
    fertilizers_compared: List[str]
    
    # Cost rankings
    lowest_cost_option: str
    highest_cost_option: str
    cost_range_per_acre: Tuple[float, float]
    
    # Cost differences
    cost_differences: Dict[str, float]  # Fertilizer -> difference from lowest
    percentage_differences: Dict[str, float]
    
    # Detailed comparisons by category
    product_cost_comparison: Dict[str, float]
    application_cost_comparison: Dict[str, float]
    total_cost_comparison: Dict[str, float]
    
    # Value analysis
    best_value_option: str
    value_scores: Dict[str, float]
    
    # Recommendations
    cost_optimization_recommendations: List[str]
    
    analysis_date: datetime


@dataclass
class MultiYearCostProjection:
    """Multi-year cost projection for fertilizer program."""
    fertilizer_id: str
    fertilizer_name: str
    projection_years: int
    
    # Annual costs
    annual_costs: List[float]
    cumulative_costs: List[float]
    
    # Cost trends
    average_annual_cost: float
    cost_growth_rate: float
    total_program_cost: float
    
    # Net present value of costs
    npv_total_costs: float
    discount_rate_used: float
    
    # Inflation adjustments
    inflation_rate_assumed: float
    inflation_adjusted_costs: List[float]
    
    analysis_date: datetime


@dataclass
class BreakEvenAnalysis:
    """Break-even analysis for fertilizer investment."""
    fertilizer_id: str
    fertilizer_name: str
    
    # Break-even metrics
    break_even_yield: float  # Yield needed to break even
    break_even_price: float  # Price needed to break even
    break_even_acres: float  # Acres needed to break even
    
    # Margin analysis
    margin_at_expected_yield: float
    margin_at_low_yield: float
    margin_at_high_yield: float
    
    # Risk assessment
    probability_of_profit: float
    downside_risk: float
    
    # Sensitivity factors
    yield_sensitivity: float
    price_sensitivity: float
    cost_sensitivity: float
    
    analysis_date: datetime


@dataclass
class ROIAnalysis:
    """Return on Investment analysis for fertilizer choice."""
    fertilizer_id: str
    fertilizer_name: str
    
    # ROI metrics
    roi_percent: float
    payback_period_years: float
    internal_rate_of_return: float
    
    # Profit metrics
    expected_profit_per_acre: float
    profit_margin_percent: float
    
    # Risk-adjusted returns
    risk_adjusted_roi: float
    sharpe_ratio: float
    
    # Value creation
    net_present_value: float
    profitability_index: float
    
    # Comparison to alternatives
    roi_rank: int
    roi_percentile: float
    
    analysis_date: datetime


@dataclass
class ScenarioCostAnalysis:
    """Cost analysis under different scenarios."""
    fertilizer_id: str
    fertilizer_name: str
    
    # Base case
    base_case_cost: float
    base_case_roi: float
    
    # Optimistic scenario
    optimistic_cost: float
    optimistic_roi: float
    optimistic_probability: float
    
    # Pessimistic scenario
    pessimistic_cost: float
    pessimistic_roi: float
    pessimistic_probability: float
    
    # Expected value
    expected_cost: float
    expected_roi: float
    
    # Risk metrics
    cost_volatility: float
    worst_case_loss: float
    best_case_gain: float
    
    analysis_date: datetime


class FertilizerCostAnalysisService:
    """
    Comprehensive cost analysis and comparison engine for fertilizer type selection.
    
    Provides detailed cost breakdowns, comparisons, projections, and economic analysis
    to support informed fertilizer purchasing decisions.
    """
    
    def __init__(self):
        """Initialize the cost analysis service."""
        self.logger = logging.getLogger(__name__)
        
        # Economic parameters
        self.discount_rate = 0.08  # 8% discount rate
        self.inflation_rate = 0.03  # 3% inflation rate
        self.risk_free_rate = 0.03  # 3% risk-free rate
        
        # Cost factor databases
        self._initialize_cost_databases()
        
        self.logger.info("FertilizerCostAnalysisService initialized")
    
    def _initialize_cost_databases(self):
        """Initialize cost factor databases."""
        
        # Application cost factors (per acre)
        self.application_costs = {
            'broadcast': {'base_cost': 12.0, 'labor_hours': 0.5, 'equipment_cost': 8.0},
            'banded': {'base_cost': 15.0, 'labor_hours': 0.7, 'equipment_cost': 10.0},
            'foliar': {'base_cost': 18.0, 'labor_hours': 0.8, 'equipment_cost': 12.0},
            'fertigation': {'base_cost': 10.0, 'labor_hours': 0.3, 'equipment_cost': 15.0},
            'injection': {'base_cost': 20.0, 'labor_hours': 0.9, 'equipment_cost': 15.0}
        }
        
        # Storage cost factors (per ton per month)
        self.storage_costs = {
            'granular': 5.0,
            'liquid': 8.0,
            'bulk': 3.0,
            'bagged': 7.0
        }
        
        # Transportation cost factors (per mile per ton)
        self.transportation_costs = {
            'bulk_truck': 0.15,
            'liquid_tanker': 0.20,
            'bagged': 0.25,
            'rail': 0.10
        }
        
        # Labor rates (per hour)
        self.labor_rates = {
            'unskilled': 15.0,
            'semi_skilled': 20.0,
            'skilled': 28.0
        }
    
    async def analyze_fertilizer_costs(
        self,
        fertilizer_data: Dict[str, Any],
        application_data: Dict[str, Any],
        farm_data: Dict[str, Any]
    ) -> FertilizerCostBreakdown:
        """
        Perform comprehensive cost analysis for a fertilizer option.
        
        Args:
            fertilizer_data: Fertilizer product information
            application_data: Application method and rate information
            farm_data: Farm size and logistics information
            
        Returns:
            Detailed cost breakdown
        """
        try:
            # Calculate product cost
            product_cost = self._calculate_product_cost(
                fertilizer_data, application_data, farm_data
            )
            
            # Calculate application cost
            application_cost = self._calculate_application_cost(
                application_data, farm_data
            )
            
            # Calculate equipment cost
            equipment_cost = self._calculate_equipment_cost(
                application_data, farm_data
            )
            
            # Calculate labor cost
            labor_cost = self._calculate_labor_cost(
                application_data, farm_data
            )
            
            # Calculate storage cost
            storage_cost = self._calculate_storage_cost(
                fertilizer_data, farm_data
            )
            
            # Calculate transportation cost
            transportation_cost = self._calculate_transportation_cost(
                fertilizer_data, farm_data
            )
            
            # Calculate total cost per acre
            total_cost_per_acre = (
                product_cost +
                application_cost +
                equipment_cost +
                labor_cost +
                storage_cost +
                transportation_cost
            )
            
            # Calculate cost per unit nutrient
            cost_per_unit_nutrient = self._calculate_cost_per_unit_nutrient(
                total_cost_per_acre, fertilizer_data, application_data
            )
            
            # Build cost components dictionary
            cost_components = {
                'product': product_cost,
                'application': application_cost,
                'equipment': equipment_cost,
                'labor': labor_cost,
                'storage': storage_cost,
                'transportation': transportation_cost
            }
            
            # Calculate percentages
            cost_percentages = {
                category: (cost / total_cost_per_acre * 100) if total_cost_per_acre > 0 else 0
                for category, cost in cost_components.items()
            }
            
            # Calculate efficiency scores
            nutrient_efficiency = self._calculate_nutrient_efficiency(
                fertilizer_data, application_data
            )
            cost_efficiency = self._calculate_cost_efficiency(
                total_cost_per_acre, nutrient_efficiency
            )
            
            return FertilizerCostBreakdown(
                fertilizer_id=fertilizer_data.get('id', 'unknown'),
                fertilizer_name=fertilizer_data.get('name', 'Unknown'),
                fertilizer_type=fertilizer_data.get('type', 'synthetic'),
                product_cost_per_acre=product_cost,
                application_cost_per_acre=application_cost,
                equipment_cost_per_acre=equipment_cost,
                labor_cost_per_acre=labor_cost,
                storage_cost_per_acre=storage_cost,
                transportation_cost_per_acre=transportation_cost,
                total_cost_per_acre=total_cost_per_acre,
                total_cost_per_unit_nutrient=cost_per_unit_nutrient,
                cost_components=cost_components,
                cost_percentages=cost_percentages,
                nutrient_efficiency_score=nutrient_efficiency,
                cost_efficiency_score=cost_efficiency,
                analysis_date=datetime.utcnow(),
                assumptions_used=self._get_cost_assumptions()
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing fertilizer costs: {e}")
            raise
    
    def _calculate_product_cost(
        self,
        fertilizer_data: Dict[str, Any],
        application_data: Dict[str, Any],
        farm_data: Dict[str, Any]
    ) -> float:
        """Calculate product cost per acre."""
        price_per_unit = fertilizer_data.get('price_per_unit', 0.0)
        application_rate = application_data.get('rate_lbs_per_acre', 0.0)
        
        # Convert to per-acre cost
        cost_per_acre = (price_per_unit * application_rate) / 2000  # Convert lbs to tons
        
        return cost_per_acre
    
    def _calculate_application_cost(
        self,
        application_data: Dict[str, Any],
        farm_data: Dict[str, Any]
    ) -> float:
        """Calculate application cost per acre."""
        method = application_data.get('method', 'broadcast')
        
        if method in self.application_costs:
            return self.application_costs[method]['base_cost']
        
        return 12.0  # Default application cost
    
    def _calculate_equipment_cost(
        self,
        application_data: Dict[str, Any],
        farm_data: Dict[str, Any]
    ) -> float:
        """Calculate equipment cost per acre."""
        method = application_data.get('method', 'broadcast')
        
        if method in self.application_costs:
            return self.application_costs[method]['equipment_cost']
        
        return 8.0  # Default equipment cost
    
    def _calculate_labor_cost(
        self,
        application_data: Dict[str, Any],
        farm_data: Dict[str, Any]
    ) -> float:
        """Calculate labor cost per acre."""
        method = application_data.get('method', 'broadcast')
        skill_level = application_data.get('skill_level', 'semi_skilled')
        
        labor_hours = self.application_costs.get(method, {}).get('labor_hours', 0.5)
        labor_rate = self.labor_rates.get(skill_level, 20.0)
        
        return labor_hours * labor_rate
    
    def _calculate_storage_cost(
        self,
        fertilizer_data: Dict[str, Any],
        farm_data: Dict[str, Any]
    ) -> float:
        """Calculate storage cost per acre."""
        physical_form = fertilizer_data.get('physical_form', 'granular')
        storage_months = farm_data.get('storage_months', 3)
        
        # Calculate tons per acre
        application_rate = fertilizer_data.get('application_rate', 200.0)
        tons_per_acre = application_rate / 2000
        
        # Get storage cost per ton per month
        cost_per_ton_month = self.storage_costs.get(physical_form, 5.0)
        
        return tons_per_acre * cost_per_ton_month * storage_months
    
    def _calculate_transportation_cost(
        self,
        fertilizer_data: Dict[str, Any],
        farm_data: Dict[str, Any]
    ) -> float:
        """Calculate transportation cost per acre."""
        transport_method = fertilizer_data.get('transport_method', 'bulk_truck')
        distance_miles = farm_data.get('distance_to_source_miles', 50.0)
        
        # Calculate tons per acre
        application_rate = fertilizer_data.get('application_rate', 200.0)
        tons_per_acre = application_rate / 2000
        
        # Get transportation cost per mile per ton
        cost_per_mile_ton = self.transportation_costs.get(transport_method, 0.15)
        
        return tons_per_acre * distance_miles * cost_per_mile_ton
    
    def _calculate_cost_per_unit_nutrient(
        self,
        total_cost: float,
        fertilizer_data: Dict[str, Any],
        application_data: Dict[str, Any]
    ) -> float:
        """Calculate cost per unit of NPK nutrients."""
        # Get NPK percentages
        n_percent = fertilizer_data.get('nitrogen_percent', 0.0)
        p_percent = fertilizer_data.get('phosphorus_percent', 0.0)
        k_percent = fertilizer_data.get('potassium_percent', 0.0)
        
        # Calculate total nutrients
        total_nutrients = n_percent + p_percent + k_percent
        
        if total_nutrients == 0:
            return 0.0
        
        # Calculate application rate
        application_rate = application_data.get('rate_lbs_per_acre', 200.0)
        
        # Calculate actual nutrient pounds per acre
        nutrient_lbs_per_acre = application_rate * (total_nutrients / 100)
        
        if nutrient_lbs_per_acre == 0:
            return 0.0
        
        return total_cost / nutrient_lbs_per_acre
    
    def _calculate_nutrient_efficiency(
        self,
        fertilizer_data: Dict[str, Any],
        application_data: Dict[str, Any]
    ) -> float:
        """Calculate nutrient efficiency score (0-1)."""
        # Get nutrient content
        n_percent = fertilizer_data.get('nitrogen_percent', 0.0)
        p_percent = fertilizer_data.get('phosphorus_percent', 0.0)
        k_percent = fertilizer_data.get('potassium_percent', 0.0)
        total_nutrients = n_percent + p_percent + k_percent
        
        # Get application efficiency
        method = application_data.get('method', 'broadcast')
        method_efficiency = {
            'broadcast': 0.70,
            'banded': 0.85,
            'foliar': 0.95,
            'fertigation': 0.98,
            'injection': 0.90
        }.get(method, 0.75)
        
        # Calculate overall efficiency
        efficiency = (total_nutrients / 100) * method_efficiency
        
        return min(1.0, efficiency)
    
    def _calculate_cost_efficiency(
        self,
        total_cost: float,
        nutrient_efficiency: float
    ) -> float:
        """Calculate cost efficiency score (0-1)."""
        if nutrient_efficiency == 0:
            return 0.0
        
        # Lower cost per unit efficiency = higher score
        cost_per_efficiency = total_cost / nutrient_efficiency
        
        # Normalize to 0-1 scale (assuming $200/acre as baseline)
        efficiency_score = max(0.0, min(1.0, (200 - cost_per_efficiency) / 200))
        
        return efficiency_score
    
    async def compare_fertilizer_costs(
        self,
        fertilizer_options: List[Dict[str, Any]],
        farm_data: Dict[str, Any]
    ) -> CostComparison:
        """Compare costs across multiple fertilizer options."""
        try:
            # Analyze costs for each option
            cost_breakdowns = []
            for fertilizer in fertilizer_options:
                breakdown = await self.analyze_fertilizer_costs(
                    fertilizer.get('fertilizer_data', {}),
                    fertilizer.get('application_data', {}),
                    farm_data
                )
                cost_breakdowns.append(breakdown)
            
            # Find lowest and highest cost options
            costs = [b.total_cost_per_acre for b in cost_breakdowns]
            min_cost = min(costs)
            max_cost = max(costs)
            
            lowest_idx = costs.index(min_cost)
            highest_idx = costs.index(max_cost)
            
            # Calculate cost differences
            cost_differences = {}
            percentage_differences = {}
            for breakdown in cost_breakdowns:
                diff = breakdown.total_cost_per_acre - min_cost
                cost_differences[breakdown.fertilizer_name] = diff
                percentage_differences[breakdown.fertilizer_name] = (
                    (diff / min_cost * 100) if min_cost > 0 else 0
                )
            
            # Compare by category
            product_costs = {b.fertilizer_name: b.product_cost_per_acre for b in cost_breakdowns}
            application_costs = {b.fertilizer_name: b.application_cost_per_acre for b in cost_breakdowns}
            total_costs = {b.fertilizer_name: b.total_cost_per_acre for b in cost_breakdowns}
            
            # Calculate value scores (considering both cost and efficiency)
            value_scores = {}
            for breakdown in cost_breakdowns:
                # Value = efficiency / cost (normalized)
                if breakdown.total_cost_per_acre > 0:
                    value = breakdown.nutrient_efficiency_score / (breakdown.total_cost_per_acre / 100)
                else:
                    value = 0.0
                value_scores[breakdown.fertilizer_name] = min(1.0, value)
            
            # Find best value option
            best_value = max(value_scores.items(), key=lambda x: x[1])[0]
            
            # Generate recommendations
            recommendations = self._generate_cost_optimization_recommendations(
                cost_breakdowns, cost_differences
            )
            
            return CostComparison(
                comparison_id=f"comp_{datetime.utcnow().timestamp()}",
                fertilizers_compared=[b.fertilizer_name for b in cost_breakdowns],
                lowest_cost_option=cost_breakdowns[lowest_idx].fertilizer_name,
                highest_cost_option=cost_breakdowns[highest_idx].fertilizer_name,
                cost_range_per_acre=(min_cost, max_cost),
                cost_differences=cost_differences,
                percentage_differences=percentage_differences,
                product_cost_comparison=product_costs,
                application_cost_comparison=application_costs,
                total_cost_comparison=total_costs,
                best_value_option=best_value,
                value_scores=value_scores,
                cost_optimization_recommendations=recommendations,
                analysis_date=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Error comparing fertilizer costs: {e}")
            raise
    
    def _generate_cost_optimization_recommendations(
        self,
        cost_breakdowns: List[FertilizerCostBreakdown],
        cost_differences: Dict[str, float]
    ) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        # Find lowest cost option
        lowest_cost = min(cost_breakdowns, key=lambda x: x.total_cost_per_acre)
        recommendations.append(
            f"Consider {lowest_cost.fertilizer_name} for lowest total cost at ${lowest_cost.total_cost_per_acre:.2f}/acre"
        )
        
        # Analyze cost components
        for breakdown in cost_breakdowns:
            # High product cost
            if breakdown.cost_percentages['product'] > 60:
                recommendations.append(
                    f"{breakdown.fertilizer_name}: Product cost represents {breakdown.cost_percentages['product']:.0f}% of total - consider bulk purchasing"
                )
            
            # High application cost
            if breakdown.cost_percentages['application'] > 25:
                recommendations.append(
                    f"{breakdown.fertilizer_name}: High application cost - consider alternative application methods"
                )
            
            # High transportation cost
            if breakdown.cost_percentages['transportation'] > 15:
                recommendations.append(
                    f"{breakdown.fertilizer_name}: High transportation cost - consider local suppliers"
                )
        
        return recommendations
    
    async def project_multi_year_costs(
        self,
        fertilizer_data: Dict[str, Any],
        application_data: Dict[str, Any],
        farm_data: Dict[str, Any],
        projection_years: int = 5
    ) -> MultiYearCostProjection:
        """Project fertilizer costs over multiple years."""
        try:
            # Get base year cost
            base_breakdown = await self.analyze_fertilizer_costs(
                fertilizer_data, application_data, farm_data
            )
            base_cost = base_breakdown.total_cost_per_acre
            
            # Project annual costs with inflation
            annual_costs = []
            inflation_adjusted_costs = []
            
            for year in range(projection_years):
                # Apply inflation
                inflated_cost = base_cost * ((1 + self.inflation_rate) ** year)
                annual_costs.append(inflated_cost)
                
                # Apply additional cost growth (e.g., market factors)
                cost_growth = 0.02  # 2% additional growth
                adjusted_cost = inflated_cost * ((1 + cost_growth) ** year)
                inflation_adjusted_costs.append(adjusted_cost)
            
            # Calculate cumulative costs
            cumulative_costs = []
            running_total = 0.0
            for cost in annual_costs:
                running_total += cost
                cumulative_costs.append(running_total)
            
            # Calculate NPV of costs
            npv_costs = sum(
                cost / ((1 + self.discount_rate) ** (i + 1))
                for i, cost in enumerate(annual_costs)
            )
            
            # Calculate metrics
            average_cost = statistics.mean(annual_costs)
            cost_growth_rate = (
                (annual_costs[-1] - annual_costs[0]) / annual_costs[0]
                if annual_costs[0] > 0 else 0
            )
            total_cost = sum(annual_costs)
            
            return MultiYearCostProjection(
                fertilizer_id=fertilizer_data.get('id', 'unknown'),
                fertilizer_name=fertilizer_data.get('name', 'Unknown'),
                projection_years=projection_years,
                annual_costs=annual_costs,
                cumulative_costs=cumulative_costs,
                average_annual_cost=average_cost,
                cost_growth_rate=cost_growth_rate,
                total_program_cost=total_cost,
                npv_total_costs=npv_costs,
                discount_rate_used=self.discount_rate,
                inflation_rate_assumed=self.inflation_rate,
                inflation_adjusted_costs=inflation_adjusted_costs,
                analysis_date=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Error projecting multi-year costs: {e}")
            raise
    
    def _get_cost_assumptions(self) -> Dict[str, Any]:
        """Get assumptions used in cost analysis."""
        return {
            'discount_rate': self.discount_rate,
            'inflation_rate': self.inflation_rate,
            'labor_rates': self.labor_rates,
            'storage_costs': self.storage_costs,
            'transportation_costs': self.transportation_costs,
            'application_costs': self.application_costs
        }
