"""
Advanced Cost Analysis Service for fertilizer application cost optimization and comprehensive economic analysis.
"""

import asyncio
import logging
import time
import statistics
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timedelta
from enum import Enum

from src.models.application_models import ApplicationMethod, FieldConditions, CropRequirements, FertilizerSpecification, ApplicationRequest
from src.models.application_models import EquipmentSpecification
from src.services.fertilizer_type_service import FertilizerTypeService

logger = logging.getLogger(__name__)


class LaborSkillLevel(str, Enum):
    """Labor skill levels for cost analysis."""
    UNSKILLED = "unskilled"
    SEMI_SKILLED = "semi_skilled"
    SKILLED = "skilled"
    HIGHLY_SKILLED = "highly_skilled"


class SeasonalConstraint(str, Enum):
    """Seasonal constraints for labor availability."""
    SPRING_PEAK = "spring_peak"
    SUMMER_PEAK = "summer_peak"
    FALL_PEAK = "fall_peak"
    WINTER_LOW = "winter_low"
    YEAR_ROUND = "year_round"


class EconomicScenario(str, Enum):
    """Economic scenarios for analysis."""
    OPTIMISTIC = "optimistic"
    REALISTIC = "realistic"
    PESSIMISTIC = "pessimistic"
    CRISIS = "crisis"


class CostAnalysisService:
    """Service for comprehensive cost analysis and optimization."""
    
    def __init__(self):
        self.cost_database = {}
        self.fertilizer_type_service = FertilizerTypeService()
        self._initialize_cost_database()
    
    def _initialize_cost_database(self):
        """Initialize comprehensive cost database with market rates, benchmarks, and economic factors."""
        self.cost_database = {
            "labor_rates": {
                "unskilled": 12.0,  # USD per hour
                "semi_skilled": 18.0,
                "skilled": 25.0,
                "highly_skilled": 35.0
            },
            "labor_availability": {
                "spring_peak": 0.8,  # Availability factor (0-1)
                "summer_peak": 0.9,
                "fall_peak": 0.85,
                "winter_low": 0.6,
                "year_round": 1.0
            },
            "labor_skill_requirements": {
                "broadcast": "semi_skilled",
                "band": "skilled",
                "sidedress": "skilled",
                "foliar": "highly_skilled",
                "injection": "skilled",
                "drip": "semi_skilled"
            },
            "fuel_costs": {
                "diesel": 3.50,  # USD per gallon
                "gasoline": 3.20,
                "electric": 0.12,  # USD per kWh
                "propane": 2.80
            },
            "fuel_price_volatility": {
                "diesel": 0.15,  # Volatility factor (15% standard deviation)
                "gasoline": 0.18,
                "electric": 0.05,
                "propane": 0.20
            },
            "equipment_costs": {
                "spreader": {
                    "rental_per_day": 150.0,
                    "maintenance_per_hour": 5.0,
                    "depreciation_per_hour": 8.0,
                    "insurance_per_hour": 1.5,
                    "storage_per_month": 50.0
                },
                "sprayer": {
                    "rental_per_day": 200.0,
                    "maintenance_per_hour": 7.0,
                    "depreciation_per_hour": 12.0,
                    "insurance_per_hour": 2.0,
                    "storage_per_month": 75.0
                },
                "injector": {
                    "rental_per_day": 180.0,
                    "maintenance_per_hour": 6.0,
                    "depreciation_per_hour": 10.0,
                    "insurance_per_hour": 1.8,
                    "storage_per_month": 60.0
                },
                "drip_system": {
                    "rental_per_day": 100.0,
                    "maintenance_per_hour": 3.0,
                    "depreciation_per_hour": 5.0,
                    "insurance_per_hour": 1.0,
                    "storage_per_month": 30.0
                }
            },
            "fertilizer_costs": {
                "nitrogen": 0.80,  # USD per lb
                "phosphorus": 0.60,
                "potassium": 0.50,
                "organic": 0.40,
                "liquid": 0.90,
                "slow_release": 1.20,
                "micronutrients": 2.50
            },
            "fertilizer_price_volatility": {
                "nitrogen": 0.25,  # High volatility
                "phosphorus": 0.20,
                "potassium": 0.18,
                "organic": 0.15,
                "liquid": 0.22,
                "slow_release": 0.12,
                "micronutrients": 0.30
            },
            "application_efficiency": {
                "broadcast": 0.70,
                "band": 0.85,
                "sidedress": 0.90,
                "foliar": 0.95,
                "injection": 0.85,
                "drip": 0.98
            },
            "economic_scenarios": {
                "optimistic": {
                    "fertilizer_multiplier": 0.9,  # 10% lower costs
                    "fuel_multiplier": 0.85,
                    "labor_multiplier": 0.95,
                    "equipment_multiplier": 0.9
                },
                "realistic": {
                    "fertilizer_multiplier": 1.0,
                    "fuel_multiplier": 1.0,
                    "labor_multiplier": 1.0,
                    "equipment_multiplier": 1.0
                },
                "pessimistic": {
                    "fertilizer_multiplier": 1.2,  # 20% higher costs
                    "fuel_multiplier": 1.3,
                    "labor_multiplier": 1.15,
                    "equipment_multiplier": 1.1
                },
                "crisis": {
                    "fertilizer_multiplier": 1.5,  # 50% higher costs
                    "fuel_multiplier": 1.8,
                    "labor_multiplier": 1.4,
                    "equipment_multiplier": 1.3
                }
            },
            "opportunity_costs": {
                "land_rental_per_acre": 150.0,  # Annual land rental
                "alternative_crop_revenue": 800.0,  # Revenue per acre
                "equipment_utilization_rate": 0.7  # Equipment utilization factor
            },
            "risk_factors": {
                "weather_risk": 0.15,  # 15% weather-related cost variance
                "market_risk": 0.20,   # 20% market-related cost variance
                "equipment_failure_risk": 0.05,  # 5% equipment failure risk
                "labor_shortage_risk": 0.10  # 10% labor shortage risk
            }
        }
    
    async def analyze_application_costs(
        self,
        application_methods: List[ApplicationMethod],
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> Dict[str, Any]:
        """
        Analyze costs for different application methods.
        
        Args:
            application_methods: List of application methods to analyze
            field_conditions: Field conditions affecting costs
            crop_requirements: Crop requirements affecting fertilizer needs
            fertilizer_specification: Fertilizer specification for cost calculation
            available_equipment: Available equipment for cost estimation
            
        Returns:
            Comprehensive cost analysis results
        """
        start_time = time.time()
        
        try:
            logger.info("Starting application cost analysis")
            
            # Calculate costs for each method
            method_costs = []
            for method in application_methods:
                cost_analysis = await self._calculate_method_costs(
                    method, field_conditions, crop_requirements, 
                    fertilizer_specification, available_equipment
                )
                method_costs.append(cost_analysis)
            
            # Perform comparative analysis
            comparative_analysis = await self._perform_comparative_analysis(method_costs)
            
            # Generate cost optimization recommendations
            optimization_recommendations = await self._generate_optimization_recommendations(
                method_costs, field_conditions, crop_requirements
            )
            
            # Calculate ROI analysis
            roi_analysis = await self._calculate_roi_analysis(
                method_costs, crop_requirements, fertilizer_specification
            )
            
            # Generate cost sensitivity analysis
            sensitivity_analysis = await self._generate_sensitivity_analysis(
                method_costs, field_conditions, crop_requirements
            )
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            analysis_results = {
                "method_costs": method_costs,
                "comparative_analysis": comparative_analysis,
                "optimization_recommendations": optimization_recommendations,
                "roi_analysis": roi_analysis,
                "sensitivity_analysis": sensitivity_analysis,
                "processing_time_ms": processing_time_ms,
                "analysis_timestamp": time.time()
            }
            
            logger.info(f"Cost analysis completed in {processing_time_ms:.2f}ms")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in cost analysis: {e}")
            raise
    
    async def _calculate_method_costs(
        self,
        method: ApplicationMethod,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> Dict[str, Any]:
        """Calculate comprehensive costs for a specific application method."""
        
        # Calculate fertilizer costs
        fertilizer_costs = await self._calculate_fertilizer_costs(
            method, fertilizer_specification, crop_requirements, field_conditions.field_size_acres
        )
        
        # Calculate equipment costs
        equipment_costs = await self._calculate_equipment_costs(
            method, field_conditions, available_equipment
        )
        
        # Calculate labor costs
        labor_costs = await self._calculate_labor_costs(
            method, field_conditions, crop_requirements
        )
        
        # Calculate fuel costs
        fuel_costs = await self._calculate_fuel_costs(
            method, field_conditions, available_equipment
        )
        
        # Calculate maintenance costs
        maintenance_costs = await self._calculate_maintenance_costs(
            method, field_conditions, available_equipment
        )
        
        # Calculate total costs
        total_costs = {
            "fertilizer": fertilizer_costs["total_cost"],
            "equipment": equipment_costs["total_cost"],
            "labor": labor_costs["total_cost"],
            "fuel": fuel_costs["total_cost"],
            "maintenance": maintenance_costs["total_cost"]
        }
        
        total_cost_per_acre = sum(total_costs.values()) / field_conditions.field_size_acres
        total_cost_per_field = sum(total_costs.values())
        
        return {
            "method_id": method.method_id,
            "method_type": method.method_type,
            "fertilizer_costs": fertilizer_costs,
            "equipment_costs": equipment_costs,
            "labor_costs": labor_costs,
            "fuel_costs": fuel_costs,
            "maintenance_costs": maintenance_costs,
            "total_costs": total_costs,
            "cost_per_acre": total_cost_per_acre,
            "cost_per_field": total_cost_per_field,
            "cost_breakdown": self._create_cost_breakdown(total_costs),
            "efficiency_adjustment": self._calculate_efficiency_adjustment(method)
        }
    
    async def _calculate_fertilizer_costs(
        self,
        method: ApplicationMethod,
        fertilizer_specification: FertilizerSpecification,
        crop_requirements: CropRequirements,
        field_size_acres: float
    ) -> Dict[str, Any]:
        """Calculate fertilizer costs for the application method using detailed fertilizer type info."""

        # Get detailed fertilizer type information
        detailed_fertilizer_type = self.fertilizer_type_service.get_fertilizer_type_by_id(
            fertilizer_specification.fertilizer_type
        )

        if not detailed_fertilizer_type:
            logger.warning(f"Detailed info for fertilizer type {fertilizer_specification.fertilizer_type} not found. Using generic cost.")
            # Fallback to generic cost if detailed info is not available
            fertilizer_type_key = fertilizer_specification.fertilizer_type.lower()
            base_cost_per_unit = self.cost_database["fertilizer_costs"].get(fertilizer_type_key, 0.50)
            # Simplified calculation for fallback
            application_rate = method.application_rate
            efficiency_factor = self.cost_database["application_efficiency"].get(method.method_type, 0.8)
            adjusted_rate = application_rate / efficiency_factor
            fertilizer_cost_per_acre = adjusted_rate * base_cost_per_unit
            total_fertilizer_cost = fertilizer_cost_per_acre * field_size_acres
            return {
                "base_cost_per_unit": base_cost_per_unit,
                "application_rate": application_rate,
                "efficiency_factor": efficiency_factor,
                "adjusted_rate": adjusted_rate,
                "cost_per_acre": fertilizer_cost_per_acre,
                "total_cost": total_fertilizer_cost,
                "fertilizer_type": fertilizer_type_key,
                "cost_components": {
                    "base_fertilizer_cost": adjusted_rate * base_cost_per_unit,
                    "efficiency_adjustment": (adjusted_rate - application_rate) * base_cost_per_unit
                }
            }

        # Use detailed cost factors from FertilizerTypeDetails
        cost_factors = detailed_fertilizer_type.cost_factors
        application_rate = method.application_rate # This is typically in lbs/acre of product
        efficiency_factor = self.cost_database["application_efficiency"].get(method.method_type, 0.8)
        adjusted_rate = application_rate / efficiency_factor

        fertilizer_cost_per_acre = Decimal('0.0')
        cost_components = {}

        # Example: if cost is per ton of product
        if "per_ton_usd" in cost_factors:
            cost_per_ton = cost_factors["per_ton_usd"]
            # Convert adjusted_rate (lbs/acre) to tons/acre
            adjusted_rate_tons = adjusted_rate / 2000 # 2000 lbs per ton
            fertilizer_cost_per_acre = adjusted_rate_tons * cost_per_ton
            cost_components["product_cost_per_ton"] = float(cost_per_ton)
            cost_components["adjusted_rate_tons_per_acre"] = float(adjusted_rate_tons)

        # Example: if cost is per lb of Nitrogen (N)
        elif "per_lb_N_usd" in cost_factors and detailed_fertilizer_type.nutrient_composition.get(NutrientType.NITROGEN, Decimal('0.0')) > 0:
            cost_per_lb_N = cost_factors["per_lb_N_usd"]
            nitrogen_content_percent = detailed_fertilizer_type.nutrient_composition[NutrientType.NITROGEN]
            # Calculate lbs of N in adjusted_rate (lbs of product)
            lbs_N_per_acre = adjusted_rate * (float(nitrogen_content_percent) / 100)
            fertilizer_cost_per_acre = lbs_N_per_acre * cost_per_lb_N
            cost_components["product_cost_per_lb_N"] = float(cost_per_lb_N)
            cost_components["lbs_N_per_acre"] = float(lbs_N_per_acre)

        # Add other cost factor types as needed (e.g., per_gallon, per_lb_P, per_lb_K)
        # For simplicity, if no specific cost factor is matched, use a default or raise error
        if fertilizer_cost_per_acre == Decimal('0.0') and cost_factors:
            logger.warning(f"No matching cost factor found for {detailed_fertilizer_type.id}. Using first available cost factor.")
            # Fallback to using the first cost factor found, assuming it's per unit of product
            first_cost_key = list(cost_factors.keys())[0]
            cost_per_unit_product = cost_factors[first_cost_key]
            fertilizer_cost_per_acre = adjusted_rate * cost_per_unit_product
            cost_components["generic_product_cost_per_unit"] = float(cost_per_unit_product)

        total_fertilizer_cost = fertilizer_cost_per_acre * Decimal(str(field_size_acres))

        return {
            "base_cost_per_unit": float(fertilizer_cost_per_acre / adjusted_rate) if adjusted_rate > 0 else 0.0, # Re-derive effective base cost
            "application_rate": float(application_rate),
            "efficiency_factor": efficiency_factor,
            "adjusted_rate": float(adjusted_rate),
            "cost_per_acre": float(fertilizer_cost_per_acre),
            "total_cost": float(total_fertilizer_cost),
            "fertilizer_type": detailed_fertilizer_type.id,
            "cost_components": cost_components
        }
    
    async def _calculate_equipment_costs(
        self,
        method: ApplicationMethod,
        field_conditions: FieldConditions,
        available_equipment: List[EquipmentSpecification]
    ) -> Dict[str, Any]:
        """Calculate equipment costs for the application method."""
        
        # Find compatible equipment
        compatible_equipment = self._find_compatible_equipment(
            method.recommended_equipment.equipment_type, available_equipment
        )
        
        if not compatible_equipment:
            # Use rental costs if no compatible equipment available
            equipment_type = method.recommended_equipment.equipment_type.lower()
            rental_cost_per_day = self.cost_database["equipment_costs"].get(equipment_type, {}).get("rental_per_day", 150.0)
            
            # Estimate days needed based on field size
            days_needed = self._estimate_days_needed(field_conditions.field_size_acres, method)
            
            return {
                "equipment_type": equipment_type,
                "rental_cost_per_day": rental_cost_per_day,
                "days_needed": days_needed,
                "total_cost": rental_cost_per_day * days_needed,
                "cost_type": "rental",
                "cost_per_acre": (rental_cost_per_day * days_needed) / field_conditions.field_size_acres
            }
        
        # Calculate ownership costs
        equipment_type = compatible_equipment.equipment_type.lower()
        maintenance_per_hour = self.cost_database["equipment_costs"].get(equipment_type, {}).get("maintenance_per_hour", 5.0)
        depreciation_per_hour = self.cost_database["equipment_costs"].get(equipment_type, {}).get("depreciation_per_hour", 8.0)
        
        # Estimate hours needed
        hours_needed = self._estimate_hours_needed(field_conditions.field_size_acres, method, compatible_equipment)
        
        maintenance_cost = maintenance_per_hour * hours_needed
        depreciation_cost = depreciation_per_hour * hours_needed
        
        return {
            "equipment_type": equipment_type,
            "equipment_id": compatible_equipment.equipment_type,
            "hours_needed": hours_needed,
            "maintenance_cost": maintenance_cost,
            "depreciation_cost": depreciation_cost,
            "total_cost": maintenance_cost + depreciation_cost,
            "cost_type": "ownership",
            "cost_per_acre": (maintenance_cost + depreciation_cost) / field_conditions.field_size_acres,
            "cost_components": {
                "maintenance": maintenance_cost,
                "depreciation": depreciation_cost
            }
        }
    
    async def _calculate_labor_costs(
        self,
        method: ApplicationMethod,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements
    ) -> Dict[str, Any]:
        """Calculate labor costs for the application method."""
        
        # Determine labor skill level based on method complexity
        skill_level = self._determine_labor_skill_level(method.method_type)
        labor_rate = self.cost_database["labor_rates"][skill_level]
        
        # Estimate labor hours needed
        labor_hours = self._estimate_labor_hours(
            field_conditions.field_size_acres, method.method_type, crop_requirements
        )
        
        # Calculate total labor cost
        total_labor_cost = labor_rate * labor_hours
        
        return {
            "skill_level": skill_level,
            "labor_rate": labor_rate,
            "labor_hours": labor_hours,
            "total_cost": total_labor_cost,
            "cost_per_acre": total_labor_cost / field_conditions.field_size_acres,
            "cost_components": {
                "base_labor": labor_rate * labor_hours,
                "skill_premium": 0  # Could add skill premium calculations
            }
        }
    
    async def _calculate_fuel_costs(
        self,
        method: ApplicationMethod,
        field_conditions: FieldConditions,
        available_equipment: List[EquipmentSpecification]
    ) -> Dict[str, Any]:
        """Calculate fuel costs for the application method."""
        
        # Determine fuel type based on equipment
        fuel_type = self._determine_fuel_type(method.recommended_equipment.equipment_type)
        fuel_cost_per_unit = self.cost_database["fuel_costs"][fuel_type]
        
        # Estimate fuel consumption
        fuel_consumption = self._estimate_fuel_consumption(
            field_conditions.field_size_acres, method.method_type, field_conditions.soil_type
        )
        
        # Calculate total fuel cost
        total_fuel_cost = fuel_consumption * fuel_cost_per_unit
        
        return {
            "fuel_type": fuel_type,
            "fuel_cost_per_unit": fuel_cost_per_unit,
            "fuel_consumption": fuel_consumption,
            "total_cost": total_fuel_cost,
            "cost_per_acre": total_fuel_cost / field_conditions.field_size_acres,
            "cost_components": {
                "base_fuel_cost": fuel_consumption * fuel_cost_per_unit
            }
        }
    
    async def _calculate_maintenance_costs(
        self,
        method: ApplicationMethod,
        field_conditions: FieldConditions,
        available_equipment: List[EquipmentSpecification]
    ) -> Dict[str, Any]:
        """Calculate maintenance costs for the application method."""
        
        # Find compatible equipment
        compatible_equipment = self._find_compatible_equipment(
            method.recommended_equipment.equipment_type, available_equipment
        )
        
        if not compatible_equipment:
            return {
                "total_cost": 0,
                "cost_per_acre": 0,
                "cost_type": "none"
            }
        
        # Estimate maintenance hours
        maintenance_hours = self._estimate_maintenance_hours(
            field_conditions.field_size_acres, method.method_type, compatible_equipment
        )
        
        # Calculate maintenance cost
        maintenance_rate = 15.0  # USD per hour for maintenance
        total_maintenance_cost = maintenance_hours * maintenance_rate
        
        return {
            "maintenance_hours": maintenance_hours,
            "maintenance_rate": maintenance_rate,
            "total_cost": total_maintenance_cost,
            "cost_per_acre": total_maintenance_cost / field_conditions.field_size_acres,
            "cost_components": {
                "routine_maintenance": maintenance_hours * maintenance_rate
            }
        }
    
    async def _perform_comparative_analysis(self, method_costs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comparative analysis of method costs."""
        
        if not method_costs:
            return {}
        
        # Sort methods by total cost per acre
        sorted_methods = sorted(method_costs, key=lambda x: x["cost_per_acre"])
        
        # Calculate cost differences
        cost_differences = []
        for i, method in enumerate(sorted_methods):
            if i == 0:
                cost_differences.append(0)  # Lowest cost method
            else:
                difference = method["cost_per_acre"] - sorted_methods[0]["cost_per_acre"]
                cost_differences.append(difference)
        
        # Calculate cost ranges
        costs_per_acre = [method["cost_per_acre"] for method in method_costs]
        min_cost = min(costs_per_acre)
        max_cost = max(costs_per_acre)
        cost_range = max_cost - min_cost
        
        # Identify cost leaders
        cost_leaders = {
            "lowest_cost": sorted_methods[0]["method_type"],
            "highest_cost": sorted_methods[-1]["method_type"],
            "cost_range": cost_range,
            "average_cost": sum(costs_per_acre) / len(costs_per_acre)
        }
        
        return {
            "sorted_methods": sorted_methods,
            "cost_differences": cost_differences,
            "cost_leaders": cost_leaders,
            "cost_analysis": {
                "min_cost": min_cost,
                "max_cost": max_cost,
                "cost_range": cost_range,
                "average_cost": sum(costs_per_acre) / len(costs_per_acre),
                "cost_variance": self._calculate_variance(costs_per_acre)
            }
        }
    
    async def _generate_optimization_recommendations(
        self,
        method_costs: List[Dict[str, Any]],
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements
    ) -> List[Dict[str, Any]]:
        """Generate cost optimization recommendations."""
        
        recommendations = []
        
        # Find the most cost-effective method
        most_cost_effective = min(method_costs, key=lambda x: x["cost_per_acre"])
        
        recommendations.append({
            "type": "method_selection",
            "recommendation": f"Consider {most_cost_effective['method_type']} for lowest cost per acre",
            "potential_savings": self._calculate_potential_savings(method_costs, most_cost_effective),
            "priority": "high"
        })
        
        # Analyze cost components for optimization opportunities
        for method_cost in method_costs:
            cost_components = method_cost["total_costs"]
            
            # Identify highest cost component
            highest_component = max(cost_components.items(), key=lambda x: x[1])
            
            if highest_component[0] == "fertilizer":
                recommendations.append({
                    "type": "fertilizer_optimization",
                    "method": method_cost["method_type"],
                    "recommendation": "Consider optimizing fertilizer application rate or type",
                    "potential_savings": highest_component[1] * 0.1,  # Assume 10% savings
                    "priority": "medium"
                })
            
            elif highest_component[0] == "labor":
                recommendations.append({
                    "type": "labor_optimization",
                    "method": method_cost["method_type"],
                    "recommendation": "Consider automation or equipment upgrades to reduce labor",
                    "potential_savings": highest_component[1] * 0.2,  # Assume 20% savings
                    "priority": "medium"
                })
            
            elif highest_component[0] == "equipment":
                recommendations.append({
                    "type": "equipment_optimization",
                    "method": method_cost["method_type"],
                    "recommendation": "Consider equipment sharing or rental options",
                    "potential_savings": highest_component[1] * 0.15,  # Assume 15% savings
                    "priority": "low"
                })
        
        return recommendations
    
    async def _calculate_roi_analysis(
        self,
        method_costs: List[Dict[str, Any]],
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification
    ) -> Dict[str, Any]:
        """Calculate ROI analysis for different methods."""
        
        roi_analysis = {}
        
        for method_cost in method_costs:
            method_type = method_cost["method_type"]
            total_cost = method_cost["cost_per_field"]
            
            # Estimate yield improvement (simplified)
            efficiency_factor = self.cost_database["application_efficiency"].get(method_type, 0.8)
            yield_improvement = efficiency_factor * 0.1  # Assume 10% base improvement
            
            # Calculate revenue increase (simplified)
            crop_price = 5.0  # USD per bushel (example)
            yield_increase = yield_improvement * (crop_requirements.target_yield or 150)  # bushels per acre
            revenue_increase = yield_increase * crop_price
            
            # Calculate ROI
            roi = (revenue_increase - total_cost) / total_cost * 100 if total_cost > 0 else 0
            
            roi_analysis[method_type] = {
                "total_cost": total_cost,
                "yield_improvement": yield_improvement,
                "revenue_increase": revenue_increase,
                "roi_percentage": roi,
                "payback_period": total_cost / revenue_increase if revenue_increase > 0 else None
            }
        
        return roi_analysis
    
    async def _generate_sensitivity_analysis(
        self,
        method_costs: List[Dict[str, Any]],
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements
    ) -> Dict[str, Any]:
        """Generate sensitivity analysis for cost factors."""
        
        sensitivity_analysis = {}
        
        # Analyze sensitivity to fertilizer price changes
        fertilizer_sensitivity = {}
        for method_cost in method_costs:
            method_type = method_cost["method_type"]
            base_fertilizer_cost = method_cost["fertilizer_costs"]["total_cost"]
            
            # Calculate cost change for 10% fertilizer price increase
            price_increase_10 = base_fertilizer_cost * 0.1
            cost_per_acre_change = price_increase_10 / field_conditions.field_size_acres
            
            fertilizer_sensitivity[method_type] = {
                "base_cost_per_acre": method_cost["cost_per_acre"],
                "cost_change_10_percent": cost_per_acre_change,
                "sensitivity_ratio": cost_per_acre_change / method_cost["cost_per_acre"]
            }
        
        # Analyze sensitivity to field size changes
        field_size_sensitivity = {}
        for method_cost in method_costs:
            method_type = method_cost["method_type"]
            
            # Calculate cost per acre for different field sizes
            field_size_scenarios = [field_conditions.field_size_acres * 0.5, field_conditions.field_size_acres * 1.5]
            cost_scenarios = []
            
            for size in field_size_scenarios:
                # Simplified calculation - assume fixed costs don't scale linearly
                fixed_costs = method_cost["equipment_costs"]["total_cost"] + method_cost["labor_costs"]["total_cost"]
                variable_costs = method_cost["fertilizer_costs"]["total_cost"] + method_cost["fuel_costs"]["total_cost"]
                
                # Fixed costs don't scale, variable costs do
                scaled_cost = fixed_costs + (variable_costs * size / field_conditions.field_size_acres)
                cost_per_acre = scaled_cost / size
                cost_scenarios.append(cost_per_acre)
            
            field_size_sensitivity[method_type] = {
                "base_cost_per_acre": method_cost["cost_per_acre"],
                "cost_scenarios": cost_scenarios,
                "field_size_scenarios": field_size_scenarios
            }
        
        sensitivity_analysis = {
            "fertilizer_price_sensitivity": fertilizer_sensitivity,
            "field_size_sensitivity": field_size_sensitivity,
            "sensitivity_summary": self._create_sensitivity_summary(fertilizer_sensitivity, field_size_sensitivity)
        }
        
        return sensitivity_analysis
    
    def _find_compatible_equipment(self, equipment_type: str, available_equipment: List[EquipmentSpecification]) -> Optional[EquipmentSpecification]:
        """Find compatible equipment for the method."""
        for equipment in available_equipment:
            if equipment.equipment_type.lower() == equipment_type.lower():
                return equipment
        return None
    
    def _estimate_days_needed(self, field_size_acres: float, method: ApplicationMethod) -> float:
        """Estimate days needed for application."""
        # Simplified calculation based on field size and method efficiency
        base_days = field_size_acres / 100  # Assume 100 acres per day base rate
        
        # Adjust based on method efficiency
        efficiency_adjustments = {
            "broadcast": 1.0,
            "band": 1.2,
            "sidedress": 1.5,
            "foliar": 2.0,
            "injection": 1.3,
            "drip": 0.5
        }
        
        adjustment = efficiency_adjustments.get(method.method_type, 1.0)
        return base_days * adjustment
    
    def _estimate_hours_needed(self, field_size_acres: float, method: ApplicationMethod, equipment: EquipmentSpecification) -> float:
        """Estimate hours needed for application."""
        # Simplified calculation
        base_hours = field_size_acres / 50  # Assume 50 acres per hour base rate
        
        # Adjust based on equipment capacity
        if equipment.capacity:
            capacity_factor = min(equipment.capacity / 1000, 2.0)  # Cap at 2x
            base_hours = base_hours / capacity_factor
        
        return max(base_hours, 1.0)  # Minimum 1 hour
    
    def _determine_labor_skill_level(self, method_type: str) -> str:
        """Determine required labor skill level."""
        skill_levels = {
            "broadcast": "semi_skilled",
            "band": "skilled",
            "sidedress": "skilled",
            "foliar": "skilled",
            "injection": "skilled",
            "drip": "semi_skilled"
        }
        return skill_levels.get(method_type, "semi_skilled")
    
    def _estimate_labor_hours(self, field_size_acres: float, method_type: str, crop_requirements: CropRequirements) -> float:
        """Estimate labor hours needed."""
        # Base hours per acre
        base_hours_per_acre = 0.5
        
        # Adjust based on method complexity
        complexity_adjustments = {
            "broadcast": 0.3,
            "band": 0.5,
            "sidedress": 0.8,
            "foliar": 1.0,
            "injection": 0.6,
            "drip": 0.2
        }
        
        adjustment = complexity_adjustments.get(method_type, 0.5)
        return field_size_acres * base_hours_per_acre * adjustment
    
    def _determine_fuel_type(self, equipment_type: str) -> str:
        """Determine fuel type for equipment."""
        fuel_types = {
            "spreader": "diesel",
            "sprayer": "diesel",
            "injector": "diesel",
            "drip_system": "electric"
        }
        return fuel_types.get(equipment_type.lower(), "diesel")
    
    def _estimate_fuel_consumption(self, field_size_acres: float, method_type: str, soil_type: str) -> float:
        """Estimate fuel consumption."""
        # Base consumption per acre
        base_consumption_per_acre = 0.5  # gallons per acre
        
        # Adjust based on soil type
        soil_adjustments = {
            "clay": 1.2,
            "loam": 1.0,
            "sandy": 0.8,
            "silt": 1.1
        }
        
        soil_factor = soil_adjustments.get(soil_type.lower(), 1.0)
        
        # Adjust based on method
        method_adjustments = {
            "broadcast": 1.0,
            "band": 1.1,
            "sidedress": 1.3,
            "foliar": 1.5,
            "injection": 1.2,
            "drip": 0.1
        }
        
        method_factor = method_adjustments.get(method_type, 1.0)
        
        return field_size_acres * base_consumption_per_acre * soil_factor * method_factor
    
    def _estimate_maintenance_hours(self, field_size_acres: float, method_type: str, equipment: EquipmentSpecification) -> float:
        """Estimate maintenance hours needed."""
        # Base maintenance hours
        base_hours = 2.0
        
        # Adjust based on field size
        size_factor = min(field_size_acres / 100, 3.0)  # Cap at 3x
        
        # Adjust based on method complexity
        complexity_adjustments = {
            "broadcast": 1.0,
            "band": 1.2,
            "sidedress": 1.5,
            "foliar": 2.0,
            "injection": 1.3,
            "drip": 0.8
        }
        
        complexity_factor = complexity_adjustments.get(method_type, 1.0)
        
        return base_hours * size_factor * complexity_factor
    
    def _create_cost_breakdown(self, total_costs: Dict[str, float]) -> Dict[str, float]:
        """Create cost breakdown with percentages."""
        total = sum(total_costs.values())
        if total == 0:
            return {}
        
        breakdown = {}
        for cost_type, cost in total_costs.items():
            breakdown[cost_type] = {
                "amount": cost,
                "percentage": (cost / total) * 100
            }
        
        return breakdown
    
    def _calculate_efficiency_adjustment(self, method: ApplicationMethod) -> float:
        """Calculate efficiency adjustment factor."""
        return method.efficiency_score
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _calculate_potential_savings(self, method_costs: List[Dict[str, Any]], most_cost_effective: Dict[str, Any]) -> float:
        """Calculate potential savings from using most cost-effective method."""
        if not method_costs:
            return 0.0
        
        total_cost_current = sum(method["cost_per_field"] for method in method_costs)
        total_cost_optimal = most_cost_effective["cost_per_field"] * len(method_costs)
        
        return total_cost_current - total_cost_optimal
    
    def _create_sensitivity_summary(self, fertilizer_sensitivity: Dict[str, Any], field_size_sensitivity: Dict[str, Any]) -> Dict[str, Any]:
        """Create sensitivity analysis summary."""
        return {
            "most_sensitive_to_fertilizer_prices": max(
                fertilizer_sensitivity.items(), 
                key=lambda x: x[1]["sensitivity_ratio"]
            )[0] if fertilizer_sensitivity else None,
            "least_sensitive_to_fertilizer_prices": min(
                fertilizer_sensitivity.items(), 
                key=lambda x: x[1]["sensitivity_ratio"]
            )[0] if fertilizer_sensitivity else None,
            "field_size_impact_summary": "Field size changes affect fixed costs more than variable costs"
        }
    
    async def analyze_comprehensive_labor_requirements(
        self,
        application_methods: List[ApplicationMethod],
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        seasonal_constraint: Optional[SeasonalConstraint] = None
    ) -> Dict[str, Any]:
        """
        Analyze comprehensive labor requirements including skill levels, availability, and constraints.
        
        Args:
            application_methods: List of application methods to analyze
            field_conditions: Field conditions affecting labor needs
            crop_requirements: Crop requirements affecting timing
            seasonal_constraint: Seasonal constraint for labor availability
            
        Returns:
            Comprehensive labor analysis results
        """
        start_time = time.time()
        
        try:
            logger.info("Starting comprehensive labor analysis")
            
            labor_analyses = []
            for method in application_methods:
                labor_analysis = await self._analyze_method_labor_requirements(
                    method, field_conditions, crop_requirements, seasonal_constraint
                )
                labor_analyses.append(labor_analysis)
            
            # Perform comparative labor analysis
            comparative_labor = await self._perform_comparative_labor_analysis(labor_analyses)
            
            # Generate labor optimization recommendations
            labor_optimization = await self._generate_labor_optimization_recommendations(
                labor_analyses, field_conditions, seasonal_constraint
            )
            
            # Calculate labor cost sensitivity
            labor_sensitivity = await self._calculate_labor_cost_sensitivity(
                labor_analyses, field_conditions
            )
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            return {
                "method_labor_analyses": labor_analyses,
                "comparative_labor_analysis": comparative_labor,
                "labor_optimization_recommendations": labor_optimization,
                "labor_cost_sensitivity": labor_sensitivity,
                "processing_time_ms": processing_time_ms,
                "analysis_timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive labor analysis: {e}")
            raise
    
    async def perform_economic_scenario_analysis(
        self,
        application_methods: List[ApplicationMethod],
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification],
        scenarios: Optional[List[EconomicScenario]] = None
    ) -> Dict[str, Any]:
        """
        Perform economic scenario analysis across different market conditions.
        
        Args:
            application_methods: List of application methods to analyze
            field_conditions: Field conditions
            crop_requirements: Crop requirements
            fertilizer_specification: Fertilizer specification
            available_equipment: Available equipment
            scenarios: Economic scenarios to analyze
            
        Returns:
            Economic scenario analysis results
        """
        start_time = time.time()
        
        try:
            logger.info("Starting economic scenario analysis")
            
            if scenarios is None:
                scenarios = [EconomicScenario.OPTIMISTIC, EconomicScenario.REALISTIC, 
                           EconomicScenario.PESSIMISTIC, EconomicScenario.CRISIS]
            
            scenario_results = {}
            
            for scenario in scenarios:
                logger.info(f"Analyzing {scenario.value} scenario")
                
                # Apply scenario multipliers to cost database
                original_costs = self._backup_cost_database()
                self._apply_scenario_multipliers(scenario)
                
                try:
                    # Perform cost analysis with scenario-adjusted costs
                    scenario_analysis = await self.analyze_application_costs(
                        application_methods, field_conditions, crop_requirements,
                        fertilizer_specification, available_equipment
                    )
                    
                    # Add scenario-specific analysis
                    scenario_analysis["scenario"] = scenario.value
                    scenario_analysis["scenario_multipliers"] = self.cost_database["economic_scenarios"][scenario.value]
                    
                    scenario_results[scenario.value] = scenario_analysis
                    
                finally:
                    # Restore original costs
                    self._restore_cost_database(original_costs)
            
            # Perform cross-scenario analysis
            cross_scenario_analysis = await self._perform_cross_scenario_analysis(scenario_results)
            
            # Generate risk assessment
            risk_assessment = await self._generate_risk_assessment(scenario_results, field_conditions)
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            return {
                "scenario_results": scenario_results,
                "cross_scenario_analysis": cross_scenario_analysis,
                "risk_assessment": risk_assessment,
                "processing_time_ms": processing_time_ms,
                "analysis_timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error in economic scenario analysis: {e}")
            raise
    
    async def calculate_break_even_analysis(
        self,
        application_methods: List[ApplicationMethod],
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification],
        crop_price_per_unit: float = 5.0,
        yield_units: str = "bushels"
    ) -> Dict[str, Any]:
        """
        Calculate break-even analysis for different application methods.
        
        Args:
            application_methods: List of application methods to analyze
            field_conditions: Field conditions
            crop_requirements: Crop requirements
            fertilizer_specification: Fertilizer specification
            available_equipment: Available equipment
            crop_price_per_unit: Price per unit of crop yield
            yield_units: Units for yield measurement
            
        Returns:
            Break-even analysis results
        """
        start_time = time.time()
        
        try:
            logger.info("Starting break-even analysis")
            
            # Get cost analysis for all methods
            cost_analysis = await self.analyze_application_costs(
                application_methods, field_conditions, crop_requirements,
                fertilizer_specification, available_equipment
            )
            
            break_even_results = {}
            
            for method_cost in cost_analysis["method_costs"]:
                method_type = method_cost["method_type"]
                total_cost_per_acre = method_cost["cost_per_acre"]
                
                # Calculate break-even yield
                break_even_yield = total_cost_per_acre / crop_price_per_unit
                
                # Calculate break-even price
                target_yield = crop_requirements.target_yield or 150  # Default yield
                break_even_price = total_cost_per_acre / target_yield
                
                # Calculate profit margin at different yield levels
                yield_scenarios = [target_yield * 0.8, target_yield, target_yield * 1.2]
                profit_scenarios = []
                
                for yield_level in yield_scenarios:
                    revenue = yield_level * crop_price_per_unit
                    profit = revenue - total_cost_per_acre
                    profit_margin = (profit / revenue) * 100 if revenue > 0 else 0
                    
                    profit_scenarios.append({
                        "yield_level": yield_level,
                        "revenue_per_acre": revenue,
                        "profit_per_acre": profit,
                        "profit_margin_percent": profit_margin
                    })
                
                break_even_results[method_type] = {
                    "break_even_yield": break_even_yield,
                    "break_even_price": break_even_price,
                    "target_yield": target_yield,
                    "crop_price_per_unit": crop_price_per_unit,
                    "total_cost_per_acre": total_cost_per_acre,
                    "profit_scenarios": profit_scenarios,
                    "risk_level": self._assess_break_even_risk(break_even_yield, target_yield)
                }
            
            # Perform comparative break-even analysis
            comparative_break_even = await self._perform_comparative_break_even_analysis(break_even_results)
            
            # Generate break-even optimization recommendations
            optimization_recommendations = await self._generate_break_even_optimization_recommendations(
                break_even_results, field_conditions, crop_requirements
            )
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            return {
                "break_even_results": break_even_results,
                "comparative_break_even_analysis": comparative_break_even,
                "optimization_recommendations": optimization_recommendations,
                "processing_time_ms": processing_time_ms,
                "analysis_timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error in break-even analysis: {e}")
            raise
    
    async def calculate_opportunity_cost_analysis(
        self,
        application_methods: List[ApplicationMethod],
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification],
        alternative_uses: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calculate opportunity cost analysis for different application methods.
        
        Args:
            application_methods: List of application methods to analyze
            field_conditions: Field conditions
            crop_requirements: Crop requirements
            fertilizer_specification: Fertilizer specification
            available_equipment: Available equipment
            alternative_uses: Alternative uses for resources
            
        Returns:
            Opportunity cost analysis results
        """
        start_time = time.time()
        
        try:
            logger.info("Starting opportunity cost analysis")
            
            if alternative_uses is None:
                alternative_uses = [
                    {"type": "land_rental", "revenue_per_acre": 150.0},
                    {"type": "alternative_crop", "revenue_per_acre": 800.0},
                    {"type": "equipment_rental", "revenue_per_hour": 25.0}
                ]
            
            # Get cost analysis for all methods
            cost_analysis = await self.analyze_application_costs(
                application_methods, field_conditions, crop_requirements,
                fertilizer_specification, available_equipment
            )
            
            opportunity_cost_results = {}
            
            for method_cost in cost_analysis["method_costs"]:
                method_type = method_cost["method_type"]
                
                # Calculate opportunity costs for different resources
                land_opportunity_cost = self._calculate_land_opportunity_cost(
                    field_conditions.field_size_acres, alternative_uses
                )
                
                equipment_opportunity_cost = self._calculate_equipment_opportunity_cost(
                    method_cost["equipment_costs"], alternative_uses
                )
                
                labor_opportunity_cost = self._calculate_labor_opportunity_cost(
                    method_cost["labor_costs"], alternative_uses
                )
                
                total_opportunity_cost = (
                    land_opportunity_cost + equipment_opportunity_cost + labor_opportunity_cost
                )
                
                # Calculate economic profit (accounting for opportunity costs)
                total_cost_with_opportunity = method_cost["cost_per_field"] + total_opportunity_cost
                
                opportunity_cost_results[method_type] = {
                    "land_opportunity_cost": land_opportunity_cost,
                    "equipment_opportunity_cost": equipment_opportunity_cost,
                    "labor_opportunity_cost": labor_opportunity_cost,
                    "total_opportunity_cost": total_opportunity_cost,
                    "total_cost_with_opportunity": total_cost_with_opportunity,
                    "opportunity_cost_per_acre": total_opportunity_cost / field_conditions.field_size_acres,
                    "economic_profit": self._calculate_economic_profit(
                        method_cost, total_opportunity_cost, field_conditions, crop_requirements
                    )
                }
            
            # Perform comparative opportunity cost analysis
            comparative_opportunity_cost = await self._perform_comparative_opportunity_cost_analysis(
                opportunity_cost_results
            )
            
            # Generate opportunity cost optimization recommendations
            optimization_recommendations = await self._generate_opportunity_cost_optimization_recommendations(
                opportunity_cost_results, field_conditions
            )
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            return {
                "opportunity_cost_results": opportunity_cost_results,
                "comparative_opportunity_cost_analysis": comparative_opportunity_cost,
                "optimization_recommendations": optimization_recommendations,
                "processing_time_ms": processing_time_ms,
                "analysis_timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error in opportunity cost analysis: {e}")
            raise
    
    # Helper methods for advanced analysis features
    
    async def _analyze_method_labor_requirements(
        self,
        method: ApplicationMethod,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        seasonal_constraint: Optional[SeasonalConstraint] = None
    ) -> Dict[str, Any]:
        """Analyze comprehensive labor requirements for a specific method."""
        
        # Determine skill level required
        skill_level = self.cost_database["labor_skill_requirements"].get(method.method_type, "semi_skilled")
        labor_rate = self.cost_database["labor_rates"][skill_level]
        
        # Estimate labor hours
        labor_hours = self._estimate_labor_hours(
            field_conditions.field_size_acres, method.method_type, crop_requirements
        )
        
        # Apply seasonal constraints
        availability_factor = 1.0
        if seasonal_constraint:
            availability_factor = self.cost_database["labor_availability"].get(seasonal_constraint.value, 1.0)
        
        # Calculate adjusted labor hours and costs
        adjusted_labor_hours = labor_hours / availability_factor
        total_labor_cost = labor_rate * adjusted_labor_hours
        
        # Calculate labor intensity metrics
        labor_intensity_score = self._calculate_labor_intensity_score(method.method_type)
        
        return {
            "method_type": method.method_type,
            "skill_level": skill_level,
            "labor_rate": labor_rate,
            "base_labor_hours": labor_hours,
            "availability_factor": availability_factor,
            "adjusted_labor_hours": adjusted_labor_hours,
            "total_labor_cost": total_labor_cost,
            "labor_cost_per_acre": total_labor_cost / field_conditions.field_size_acres,
            "labor_intensity_score": labor_intensity_score,
            "seasonal_constraint": seasonal_constraint.value if seasonal_constraint else None,
            "skill_requirements": self._get_skill_requirements(skill_level),
            "training_requirements": self._get_training_requirements(skill_level)
        }
    
    async def _perform_comparative_labor_analysis(self, labor_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comparative analysis of labor requirements."""
        
        if not labor_analyses:
            return {}
        
        # Sort by labor cost per acre
        sorted_by_cost = sorted(labor_analyses, key=lambda x: x["labor_cost_per_acre"])
        
        # Calculate labor efficiency metrics
        labor_efficiency_scores = []
        for analysis in labor_analyses:
            efficiency_score = 1.0 / (analysis["labor_cost_per_acre"] / analysis["labor_intensity_score"])
            labor_efficiency_scores.append(efficiency_score)
        
        # Find most and least labor-intensive methods
        most_labor_intensive = max(labor_analyses, key=lambda x: x["labor_intensity_score"])
        least_labor_intensive = min(labor_analyses, key=lambda x: x["labor_intensity_score"])
        
        return {
            "sorted_by_cost": sorted_by_cost,
            "labor_efficiency_scores": labor_efficiency_scores,
            "most_labor_intensive": most_labor_intensive["method_type"],
            "least_labor_intensive": least_labor_intensive["method_type"],
            "labor_cost_range": {
                "min_cost_per_acre": sorted_by_cost[0]["labor_cost_per_acre"],
                "max_cost_per_acre": sorted_by_cost[-1]["labor_cost_per_acre"],
                "cost_difference": sorted_by_cost[-1]["labor_cost_per_acre"] - sorted_by_cost[0]["labor_cost_per_acre"]
            }
        }
    
    async def _generate_labor_optimization_recommendations(
        self,
        labor_analyses: List[Dict[str, Any]],
        field_conditions: FieldConditions,
        seasonal_constraint: Optional[SeasonalConstraint] = None
    ) -> List[Dict[str, Any]]:
        """Generate labor optimization recommendations."""
        
        recommendations = []
        
        # Find most labor-efficient method
        most_efficient = min(labor_analyses, key=lambda x: x["labor_cost_per_acre"])
        
        recommendations.append({
            "type": "labor_efficiency",
            "recommendation": f"Consider {most_efficient['method_type']} for lowest labor costs",
            "potential_savings": self._calculate_labor_savings(labor_analyses, most_efficient),
            "priority": "high"
        })
        
        # Analyze skill level optimization
        skill_levels = [analysis["skill_level"] for analysis in labor_analyses]
        if "highly_skilled" in skill_levels:
            recommendations.append({
                "type": "skill_optimization",
                "recommendation": "Consider training existing labor to reduce skill level requirements",
                "potential_savings": self._calculate_skill_optimization_savings(labor_analyses),
                "priority": "medium"
            })
        
        # Seasonal optimization
        if seasonal_constraint and seasonal_constraint != SeasonalConstraint.YEAR_ROUND:
            recommendations.append({
                "type": "seasonal_optimization",
                "recommendation": f"Consider timing applications during {seasonal_constraint.value} for better labor availability",
                "potential_savings": self._calculate_seasonal_optimization_savings(labor_analyses, seasonal_constraint),
                "priority": "medium"
            })
        
        return recommendations
    
    async def _calculate_labor_cost_sensitivity(
        self,
        labor_analyses: List[Dict[str, Any]],
        field_conditions: FieldConditions
    ) -> Dict[str, Any]:
        """Calculate labor cost sensitivity analysis."""
        
        sensitivity_analysis = {}
        
        for analysis in labor_analyses:
            method_type = analysis["method_type"]
            base_cost = analysis["labor_cost_per_acre"]
            
            # Calculate sensitivity to labor rate changes
            rate_sensitivity = base_cost * 0.1  # 10% rate increase
            
            # Calculate sensitivity to availability changes
            availability_sensitivity = base_cost * 0.2  # 20% availability decrease
            
            sensitivity_analysis[method_type] = {
                "base_labor_cost_per_acre": base_cost,
                "rate_sensitivity": rate_sensitivity,
                "availability_sensitivity": availability_sensitivity,
                "total_sensitivity": rate_sensitivity + availability_sensitivity
            }
        
        return sensitivity_analysis
    
    def _backup_cost_database(self) -> Dict[str, Any]:
        """Backup current cost database for scenario analysis."""
        return {
            "labor_rates": self.cost_database["labor_rates"].copy(),
            "fuel_costs": self.cost_database["fuel_costs"].copy(),
            "fertilizer_costs": self.cost_database["fertilizer_costs"].copy(),
            "equipment_costs": self.cost_database["equipment_costs"].copy()
        }
    
    def _apply_scenario_multipliers(self, scenario: EconomicScenario):
        """Apply scenario multipliers to cost database."""
        multipliers = self.cost_database["economic_scenarios"][scenario.value]
        
        # Apply multipliers to labor rates
        for skill_level in self.cost_database["labor_rates"]:
            self.cost_database["labor_rates"][skill_level] *= multipliers["labor_multiplier"]
        
        # Apply multipliers to fuel costs
        for fuel_type in self.cost_database["fuel_costs"]:
            self.cost_database["fuel_costs"][fuel_type] *= multipliers["fuel_multiplier"]
        
        # Apply multipliers to fertilizer costs
        for fertilizer_type in self.cost_database["fertilizer_costs"]:
            self.cost_database["fertilizer_costs"][fertilizer_type] *= multipliers["fertilizer_multiplier"]
        
        # Apply multipliers to equipment costs
        for equipment_type in self.cost_database["equipment_costs"]:
            for cost_type in self.cost_database["equipment_costs"][equipment_type]:
                self.cost_database["equipment_costs"][equipment_type][cost_type] *= multipliers["equipment_multiplier"]
    
    def _restore_cost_database(self, backup: Dict[str, Any]):
        """Restore cost database from backup."""
        self.cost_database["labor_rates"] = backup["labor_rates"]
        self.cost_database["fuel_costs"] = backup["fuel_costs"]
        self.cost_database["fertilizer_costs"] = backup["fertilizer_costs"]
        self.cost_database["equipment_costs"] = backup["equipment_costs"]
    
    async def _perform_cross_scenario_analysis(self, scenario_results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform cross-scenario analysis."""
        
        # Extract cost per acre for each scenario
        scenario_costs = {}
        for scenario_name, results in scenario_results.items():
            method_costs = results.get("method_costs", [])
            if method_costs:
                avg_cost = sum(method["cost_per_acre"] for method in method_costs) / len(method_costs)
                scenario_costs[scenario_name] = avg_cost
        
        # Calculate cost volatility
        if len(scenario_costs) > 1:
            costs = list(scenario_costs.values())
            cost_volatility = statistics.stdev(costs) / statistics.mean(costs) if statistics.mean(costs) > 0 else 0
        else:
            cost_volatility = 0
        
        return {
            "scenario_costs": scenario_costs,
            "cost_volatility": cost_volatility,
            "most_volatile_scenario": max(scenario_costs.items(), key=lambda x: x[1])[0] if scenario_costs else None,
            "least_volatile_scenario": min(scenario_costs.items(), key=lambda x: x[1])[0] if scenario_costs else None
        }
    
    async def _generate_risk_assessment(
        self,
        scenario_results: Dict[str, Any],
        field_conditions: FieldConditions
    ) -> Dict[str, Any]:
        """Generate risk assessment based on scenario analysis."""
        
        risk_factors = self.cost_database["risk_factors"]
        
        # Calculate overall risk score
        overall_risk_score = (
            risk_factors["weather_risk"] +
            risk_factors["market_risk"] +
            risk_factors["equipment_failure_risk"] +
            risk_factors["labor_shortage_risk"]
        ) / 4
        
        # Assess field-specific risks
        field_risks = []
        if field_conditions.slope_percent and field_conditions.slope_percent > 10:
            field_risks.append("High slope increases equipment and labor costs")
        
        if field_conditions.field_size_acres < 50:
            field_risks.append("Small field size reduces economies of scale")
        
        return {
            "overall_risk_score": overall_risk_score,
            "risk_level": self._assess_risk_level(overall_risk_score),
            "field_specific_risks": field_risks,
            "risk_mitigation_recommendations": self._generate_risk_mitigation_recommendations(overall_risk_score)
        }
    
    def _assess_break_even_risk(self, break_even_yield: float, target_yield: float) -> str:
        """Assess break-even risk level."""
        if break_even_yield > target_yield * 0.9:
            return "high"
        elif break_even_yield > target_yield * 0.8:
            return "medium"
        else:
            return "low"
    
    async def _perform_comparative_break_even_analysis(self, break_even_results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comparative break-even analysis."""
        
        if not break_even_results:
            return {}
        
        # Sort by break-even yield
        sorted_by_yield = sorted(break_even_results.items(), key=lambda x: x[1]["break_even_yield"])
        
        # Calculate break-even ranges
        yields = [result["break_even_yield"] for result in break_even_results.values()]
        min_yield = min(yields)
        max_yield = max(yields)
        
        return {
            "sorted_by_break_even_yield": sorted_by_yield,
            "break_even_yield_range": {
                "min_yield": min_yield,
                "max_yield": max_yield,
                "yield_difference": max_yield - min_yield
            },
            "most_risky_method": max(break_even_results.items(), key=lambda x: x[1]["break_even_yield"])[0],
            "least_risky_method": min(break_even_results.items(), key=lambda x: x[1]["break_even_yield"])[0]
        }
    
    async def _generate_break_even_optimization_recommendations(
        self,
        break_even_results: Dict[str, Any],
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements
    ) -> List[Dict[str, Any]]:
        """Generate break-even optimization recommendations."""
        
        recommendations = []
        
        # Find method with lowest break-even yield
        lowest_break_even = min(break_even_results.items(), key=lambda x: x[1]["break_even_yield"])
        
        recommendations.append({
            "type": "break_even_optimization",
            "recommendation": f"Consider {lowest_break_even[0]} for lowest break-even yield",
            "break_even_yield": lowest_break_even[1]["break_even_yield"],
            "priority": "high"
        })
        
        # Analyze risk levels
        high_risk_methods = [
            method for method, result in break_even_results.items()
            if result["risk_level"] == "high"
        ]
        
        if high_risk_methods:
            recommendations.append({
                "type": "risk_mitigation",
                "recommendation": f"High-risk methods detected: {', '.join(high_risk_methods)}. Consider risk mitigation strategies.",
                "high_risk_methods": high_risk_methods,
                "priority": "high"
            })
        
        return recommendations
    
    def _calculate_land_opportunity_cost(self, field_size_acres: float, alternative_uses: List[Dict[str, Any]]) -> float:
        """Calculate land opportunity cost."""
        land_rental_rate = next(
            (alt["revenue_per_acre"] for alt in alternative_uses if alt["type"] == "land_rental"),
            150.0
        )
        return field_size_acres * land_rental_rate
    
    def _calculate_equipment_opportunity_cost(self, equipment_costs: Dict[str, Any], alternative_uses: List[Dict[str, Any]]) -> float:
        """Calculate equipment opportunity cost."""
        equipment_rental_rate = next(
            (alt["revenue_per_hour"] for alt in alternative_uses if alt["type"] == "equipment_rental"),
            25.0
        )
        
        # Estimate equipment hours based on total cost
        estimated_hours = equipment_costs["total_cost"] / 50.0  # Rough estimate
        return estimated_hours * equipment_rental_rate
    
    def _calculate_labor_opportunity_cost(self, labor_costs: Dict[str, Any], alternative_uses: List[Dict[str, Any]]) -> float:
        """Calculate labor opportunity cost."""
        # Assume labor could be used for alternative activities
        alternative_labor_rate = 20.0  # USD per hour
        labor_hours = labor_costs["labor_hours"]
        return labor_hours * alternative_labor_rate
    
    def _calculate_economic_profit(
        self,
        method_cost: Dict[str, Any],
        opportunity_cost: float,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements
    ) -> Dict[str, Any]:
        """Calculate economic profit accounting for opportunity costs."""
        
        # Simplified economic profit calculation
        total_cost = method_cost["cost_per_field"] + opportunity_cost
        
        # Estimate revenue (simplified)
        target_yield = crop_requirements.target_yield or 150
        crop_price = 5.0  # USD per unit
        estimated_revenue = target_yield * field_conditions.field_size_acres * crop_price
        
        economic_profit = estimated_revenue - total_cost
        
        return {
            "estimated_revenue": estimated_revenue,
            "total_economic_cost": total_cost,
            "economic_profit": economic_profit,
            "economic_profit_per_acre": economic_profit / field_conditions.field_size_acres,
            "economic_profit_margin": (economic_profit / estimated_revenue) * 100 if estimated_revenue > 0 else 0
        }
    
    async def _perform_comparative_opportunity_cost_analysis(self, opportunity_cost_results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comparative opportunity cost analysis."""
        
        if not opportunity_cost_results:
            return {}
        
        # Sort by economic profit
        sorted_by_profit = sorted(
            opportunity_cost_results.items(),
            key=lambda x: x[1]["economic_profit"]["economic_profit"],
            reverse=True
        )
        
        return {
            "sorted_by_economic_profit": sorted_by_profit,
            "most_profitable_method": sorted_by_profit[0][0] if sorted_by_profit else None,
            "least_profitable_method": sorted_by_profit[-1][0] if sorted_by_profit else None
        }
    
    async def _generate_opportunity_cost_optimization_recommendations(
        self,
        opportunity_cost_results: Dict[str, Any],
        field_conditions: FieldConditions
    ) -> List[Dict[str, Any]]:
        """Generate opportunity cost optimization recommendations."""
        
        recommendations = []
        
        # Find most economically profitable method
        most_profitable = max(
            opportunity_cost_results.items(),
            key=lambda x: x[1]["economic_profit"]["economic_profit"]
        )
        
        recommendations.append({
            "type": "economic_profit_optimization",
            "recommendation": f"Consider {most_profitable[0]} for highest economic profit",
            "economic_profit": most_profitable[1]["economic_profit"]["economic_profit"],
            "priority": "high"
        })
        
        return recommendations
    
    # Additional helper methods
    
    def _calculate_labor_intensity_score(self, method_type: str) -> float:
        """Calculate labor intensity score for a method."""
        intensity_scores = {
            "broadcast": 0.3,
            "band": 0.5,
            "sidedress": 0.7,
            "foliar": 0.9,
            "injection": 0.6,
            "drip": 0.2
        }
        return intensity_scores.get(method_type, 0.5)
    
    def _get_skill_requirements(self, skill_level: str) -> List[str]:
        """Get skill requirements for a skill level."""
        skill_requirements = {
            "unskilled": ["Basic equipment operation", "Following instructions"],
            "semi_skilled": ["Equipment calibration", "Basic troubleshooting", "Safety protocols"],
            "skilled": ["Advanced equipment operation", "Problem solving", "Quality control"],
            "highly_skilled": ["Complex equipment setup", "Advanced troubleshooting", "Training others"]
        }
        return skill_requirements.get(skill_level, [])
    
    def _get_training_requirements(self, skill_level: str) -> List[str]:
        """Get training requirements for a skill level."""
        training_requirements = {
            "unskilled": ["Basic safety training", "Equipment orientation"],
            "semi_skilled": ["Equipment operation training", "Safety certification"],
            "skilled": ["Advanced equipment training", "Quality control training"],
            "highly_skilled": ["Specialized training", "Leadership training", "Continuous education"]
        }
        return training_requirements.get(skill_level, [])
    
    def _calculate_labor_savings(self, labor_analyses: List[Dict[str, Any]], most_efficient: Dict[str, Any]) -> float:
        """Calculate potential labor savings."""
        if not labor_analyses:
            return 0.0
        
        total_current_cost = sum(analysis["total_labor_cost"] for analysis in labor_analyses)
        total_optimal_cost = most_efficient["total_labor_cost"] * len(labor_analyses)
        
        return total_current_cost - total_optimal_cost
    
    def _calculate_skill_optimization_savings(self, labor_analyses: List[Dict[str, Any]]) -> float:
        """Calculate potential savings from skill optimization."""
        # Simplified calculation
        return sum(analysis["total_labor_cost"] for analysis in labor_analyses) * 0.1
    
    def _calculate_seasonal_optimization_savings(
        self,
        labor_analyses: List[Dict[str, Any]],
        seasonal_constraint: SeasonalConstraint
    ) -> float:
        """Calculate potential savings from seasonal optimization."""
        # Simplified calculation
        return sum(analysis["total_labor_cost"] for analysis in labor_analyses) * 0.05
    
    def _assess_risk_level(self, risk_score: float) -> str:
        """Assess risk level based on risk score."""
        if risk_score > 0.3:
            return "high"
        elif risk_score > 0.15:
            return "medium"
        else:
            return "low"
    
    def _generate_risk_mitigation_recommendations(self, risk_score: float) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []
        
        if risk_score > 0.2:
            recommendations.append("Consider diversifying application methods to reduce risk")
            recommendations.append("Implement contingency plans for equipment failures")
        
        if risk_score > 0.15:
            recommendations.append("Monitor market conditions closely")
            recommendations.append("Maintain equipment maintenance schedules")
        
        return recommendations
    # Methods expected by tests
    async def calculate_total_cost(self, request: ApplicationRequest) -> Dict[str, Any]:
        """Calculate total cost for fertilizer application."""
        return await self.analyze_application_costs(request)
    
    async def calculate_cost_per_acre(self, request: ApplicationRequest) -> Dict[str, Any]:
        """Calculate cost per acre for fertilizer application."""
        result = await self.analyze_application_costs(request)
        field_size = request.field_conditions.field_size_acres
        total_cost = result.get("total_cost", 0)
        return {"cost_per_acre": total_cost / field_size if field_size > 0 else 0}
    
    async def compare_method_costs(self, request: ApplicationRequest) -> Dict[str, Any]:
        """Compare costs between different application methods."""
        return await self.analyze_application_costs(request)
