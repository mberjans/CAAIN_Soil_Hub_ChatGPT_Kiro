"""
Cost Analysis Service for fertilizer application cost optimization and economic analysis.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from uuid import uuid4
from decimal import Decimal

from ..models.application_models import ApplicationMethod, FieldConditions, CropRequirements, FertilizerSpecification
from ..models.application_models import EquipmentSpecification

logger = logging.getLogger(__name__)


class CostAnalysisService:
    """Service for comprehensive cost analysis and optimization."""
    
    def __init__(self):
        self.cost_database = {}
        self._initialize_cost_database()
    
    def _initialize_cost_database(self):
        """Initialize cost database with market rates and benchmarks."""
        self.cost_database = {
            "labor_rates": {
                "skilled": 25.0,  # USD per hour
                "semi_skilled": 18.0,
                "unskilled": 12.0
            },
            "fuel_costs": {
                "diesel": 3.50,  # USD per gallon
                "gasoline": 3.20,
                "electric": 0.12  # USD per kWh
            },
            "equipment_costs": {
                "spreader": {
                    "rental_per_day": 150.0,
                    "maintenance_per_hour": 5.0,
                    "depreciation_per_hour": 8.0
                },
                "sprayer": {
                    "rental_per_day": 200.0,
                    "maintenance_per_hour": 7.0,
                    "depreciation_per_hour": 12.0
                },
                "injector": {
                    "rental_per_day": 180.0,
                    "maintenance_per_hour": 6.0,
                    "depreciation_per_hour": 10.0
                },
                "drip_system": {
                    "rental_per_day": 100.0,
                    "maintenance_per_hour": 3.0,
                    "depreciation_per_hour": 5.0
                }
            },
            "fertilizer_costs": {
                "nitrogen": 0.80,  # USD per lb
                "phosphorus": 0.60,
                "potassium": 0.50,
                "organic": 0.40,
                "liquid": 0.90
            },
            "application_efficiency": {
                "broadcast": 0.70,
                "band": 0.85,
                "sidedress": 0.90,
                "foliar": 0.95,
                "injection": 0.85,
                "drip": 0.98
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
            method, fertilizer_specification, crop_requirements
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
        crop_requirements: CropRequirements
    ) -> Dict[str, Any]:
        """Calculate fertilizer costs for the application method."""
        
        # Get base fertilizer cost
        fertilizer_type = fertilizer_specification.fertilizer_type.lower()
        base_cost_per_unit = self.cost_database["fertilizer_costs"].get(fertilizer_type, 0.50)
        
        # Calculate fertilizer amount needed
        application_rate = method.application_rate
        efficiency_factor = self.cost_database["application_efficiency"].get(method.method_type, 0.8)
        
        # Adjust for efficiency (less efficient methods need more fertilizer)
        adjusted_rate = application_rate / efficiency_factor
        
        # Calculate total fertilizer cost
        fertilizer_cost_per_acre = adjusted_rate * base_cost_per_unit
        total_fertilizer_cost = fertilizer_cost_per_acre * crop_requirements.target_yield or 1.0
        
        return {
            "base_cost_per_unit": base_cost_per_unit,
            "application_rate": application_rate,
            "efficiency_factor": efficiency_factor,
            "adjusted_rate": adjusted_rate,
            "cost_per_acre": fertilizer_cost_per_acre,
            "total_cost": total_fertilizer_cost,
            "fertilizer_type": fertilizer_type,
            "cost_components": {
                "base_fertilizer_cost": adjusted_rate * base_cost_per_unit,
                "efficiency_adjustment": (adjusted_rate - application_rate) * base_cost_per_unit
            }
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