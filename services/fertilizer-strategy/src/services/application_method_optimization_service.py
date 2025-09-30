"""
Application Method Optimization Service

This service provides comprehensive fertilizer application method optimization with method selection,
efficiency optimization, and cost-benefit analysis for optimal fertilizer application strategies.
"""

import asyncio
import logging
import time
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any, Tuple
import statistics
import math

from ..models.application_method_optimization_models import (
    ApplicationMethodOptimizationRequest,
    ApplicationMethodOptimizationResult,
    ApplicationMethodRecommendation,
    ApplicationMethodComparisonRequest,
    ApplicationMethodComparisonResult,
    ApplicationMethodEfficiencyAnalysis,
    ApplicationMethodCostAnalysis,
    ApplicationMethodSummary,
    ApplicationMethod,
    FertilizerForm,
    EquipmentType,
    SoilCondition,
    ApplicationEfficiency,
    ApplicationCosts,
    ApplicationConstraints
)

logger = logging.getLogger(__name__)


class ApplicationMethodOptimizer:
    """
    Comprehensive application method optimization service.
    
    Features:
    - Method selection optimization based on field conditions
    - Efficiency optimization for nutrient use and application uniformity
    - Cost-benefit analysis including equipment, labor, and fertilizer costs
    - Environmental impact assessment and risk analysis
    - Multi-objective optimization (yield, cost, efficiency, environment)
    - Constraint handling for equipment, labor, and field conditions
    - Sensitivity analysis and scenario modeling
    """
    
    def __init__(self):
        self.efficiency_database = self._initialize_efficiency_database()
        self.cost_database = self._initialize_cost_database()
        self.equipment_compatibility = self._initialize_equipment_compatibility()
        self.soil_method_compatibility = self._initialize_soil_method_compatibility()
    
    def _initialize_efficiency_database(self) -> Dict[str, Dict[str, float]]:
        """Initialize efficiency database for different application methods."""
        return {
            "broadcast": {
                "nutrient_use_efficiency": 0.75,
                "application_uniformity": 0.85,
                "volatilization_loss": 0.15,
                "leaching_loss": 0.20,
                "runoff_loss": 0.10,
                "denitrification_loss": 0.05,
                "overall_efficiency": 0.70
            },
            "broadcast_incorporated": {
                "nutrient_use_efficiency": 0.85,
                "application_uniformity": 0.90,
                "volatilization_loss": 0.05,
                "leaching_loss": 0.15,
                "runoff_loss": 0.05,
                "denitrification_loss": 0.03,
                "overall_efficiency": 0.82
            },
            "banded": {
                "nutrient_use_efficiency": 0.90,
                "application_uniformity": 0.95,
                "volatilization_loss": 0.03,
                "leaching_loss": 0.10,
                "runoff_loss": 0.02,
                "denitrification_loss": 0.02,
                "overall_efficiency": 0.88
            },
            "side_dress": {
                "nutrient_use_efficiency": 0.88,
                "application_uniformity": 0.92,
                "volatilization_loss": 0.05,
                "leaching_loss": 0.12,
                "runoff_loss": 0.03,
                "denitrification_loss": 0.02,
                "overall_efficiency": 0.85
            },
            "foliar": {
                "nutrient_use_efficiency": 0.95,
                "application_uniformity": 0.88,
                "volatilization_loss": 0.02,
                "leaching_loss": 0.01,
                "runoff_loss": 0.01,
                "denitrification_loss": 0.01,
                "overall_efficiency": 0.92
            },
            "fertigation": {
                "nutrient_use_efficiency": 0.92,
                "application_uniformity": 0.90,
                "volatilization_loss": 0.03,
                "leaching_loss": 0.08,
                "runoff_loss": 0.02,
                "denitrification_loss": 0.02,
                "overall_efficiency": 0.89
            },
            "injection": {
                "nutrient_use_efficiency": 0.93,
                "application_uniformity": 0.94,
                "volatilization_loss": 0.02,
                "leaching_loss": 0.05,
                "runoff_loss": 0.01,
                "denitrification_loss": 0.01,
                "overall_efficiency": 0.91
            },
            "strip_till": {
                "nutrient_use_efficiency": 0.87,
                "application_uniformity": 0.93,
                "volatilization_loss": 0.04,
                "leaching_loss": 0.08,
                "runoff_loss": 0.02,
                "denitrification_loss": 0.02,
                "overall_efficiency": 0.86
            },
            "no_till": {
                "nutrient_use_efficiency": 0.80,
                "application_uniformity": 0.88,
                "volatilization_loss": 0.08,
                "leaching_loss": 0.12,
                "runoff_loss": 0.05,
                "denitrification_loss": 0.03,
                "overall_efficiency": 0.78
            },
            "conventional_till": {
                "nutrient_use_efficiency": 0.82,
                "application_uniformity": 0.90,
                "volatilization_loss": 0.06,
                "leaching_loss": 0.15,
                "runoff_loss": 0.08,
                "denitrification_loss": 0.04,
                "overall_efficiency": 0.79
            }
        }
    
    def _initialize_cost_database(self) -> Dict[str, Dict[str, float]]:
        """Initialize cost database for different application methods."""
        return {
            "broadcast": {
                "fertilizer_cost_per_acre": 0.0,  # Will be calculated based on fertilizer type
                "application_cost_per_acre": 8.50,
                "equipment_cost_per_acre": 5.20,
                "labor_cost_per_acre": 3.80,
                "fuel_cost_per_acre": 2.10,
                "total_cost_per_acre": 19.60
            },
            "broadcast_incorporated": {
                "fertilizer_cost_per_acre": 0.0,
                "application_cost_per_acre": 12.30,
                "equipment_cost_per_acre": 8.50,
                "labor_cost_per_acre": 5.20,
                "fuel_cost_per_acre": 4.80,
                "total_cost_per_acre": 30.80
            },
            "banded": {
                "fertilizer_cost_per_acre": 0.0,
                "application_cost_per_acre": 15.60,
                "equipment_cost_per_acre": 12.30,
                "labor_cost_per_acre": 6.80,
                "fuel_cost_per_acre": 3.20,
                "total_cost_per_acre": 37.90
            },
            "side_dress": {
                "fertilizer_cost_per_acre": 0.0,
                "application_cost_per_acre": 18.20,
                "equipment_cost_per_acre": 15.60,
                "labor_cost_per_acre": 8.50,
                "fuel_cost_per_acre": 4.20,
                "total_cost_per_acre": 46.50
            },
            "foliar": {
                "fertilizer_cost_per_acre": 0.0,
                "application_cost_per_acre": 22.80,
                "equipment_cost_per_acre": 18.20,
                "labor_cost_per_acre": 12.30,
                "fuel_cost_per_acre": 6.50,
                "total_cost_per_acre": 59.80
            },
            "fertigation": {
                "fertilizer_cost_per_acre": 0.0,
                "application_cost_per_acre": 8.50,
                "equipment_cost_per_acre": 5.20,
                "labor_cost_per_acre": 2.10,
                "fuel_cost_per_acre": 1.50,
                "total_cost_per_acre": 17.30
            },
            "injection": {
                "fertilizer_cost_per_acre": 0.0,
                "application_cost_per_acre": 25.60,
                "equipment_cost_per_acre": 22.80,
                "labor_cost_per_acre": 15.60,
                "fuel_cost_per_acre": 8.20,
                "total_cost_per_acre": 72.20
            },
            "strip_till": {
                "fertilizer_cost_per_acre": 0.0,
                "application_cost_per_acre": 28.50,
                "equipment_cost_per_acre": 25.60,
                "labor_cost_per_acre": 18.20,
                "fuel_cost_per_acre": 12.30,
                "total_cost_per_acre": 84.60
            },
            "no_till": {
                "fertilizer_cost_per_acre": 0.0,
                "application_cost_per_acre": 6.80,
                "equipment_cost_per_acre": 4.20,
                "labor_cost_per_acre": 2.50,
                "fuel_cost_per_acre": 1.80,
                "total_cost_per_acre": 15.30
            },
            "conventional_till": {
                "fertilizer_cost_per_acre": 0.0,
                "application_cost_per_acre": 15.60,
                "equipment_cost_per_acre": 12.30,
                "labor_cost_per_acre": 8.50,
                "fuel_cost_per_acre": 6.20,
                "total_cost_per_acre": 42.60
            }
        }
    
    def _initialize_equipment_compatibility(self) -> Dict[str, List[str]]:
        """Initialize equipment compatibility matrix."""
        return {
            "broadcast": ["broadcaster"],
            "broadcast_incorporated": ["broadcaster", "conventional_tillage"],
            "banded": ["planter_mounted", "side_dress_bar"],
            "side_dress": ["side_dress_bar"],
            "foliar": ["sprayer"],
            "fertigation": ["irrigation_system"],
            "injection": ["injection_system"],
            "strip_till": ["strip_till_toolbar"],
            "no_till": ["planter_mounted"],
            "conventional_till": ["conventional_tillage"]
        }
    
    def _initialize_soil_method_compatibility(self) -> Dict[str, List[str]]:
        """Initialize soil condition and method compatibility."""
        return {
            "dry": ["broadcast", "banded", "side_dress", "foliar", "fertigation", "injection"],
            "moist": ["broadcast", "broadcast_incorporated", "banded", "side_dress", "foliar", "fertigation", "injection", "strip_till"],
            "wet": ["foliar", "fertigation", "injection"],
            "frozen": ["foliar"],
            "compacted": ["broadcast_incorporated", "strip_till", "conventional_till"],
            "loose": ["broadcast", "banded", "side_dress", "foliar", "fertigation", "injection", "no_till"]
        }
    
    async def optimize_application_methods(
        self,
        request: ApplicationMethodOptimizationRequest
    ) -> ApplicationMethodOptimizationResult:
        """
        Optimize application methods based on field conditions and objectives.
        
        Args:
            request: Application method optimization request
            
        Returns:
            ApplicationMethodOptimizationResult with recommendations
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting application method optimization for field {request.field_id}")
            
            # Get all possible methods
            all_methods = list(ApplicationMethod)
            
            # Filter methods based on constraints and preferences
            feasible_methods = self._filter_feasible_methods(request, all_methods)
            
            # Evaluate each feasible method
            recommendations = []
            for method in feasible_methods:
                recommendation = await self._evaluate_application_method(request, method)
                recommendations.append(recommendation)
            
            # Sort recommendations by overall score
            recommendations.sort(key=lambda x: x.overall_score, reverse=True)
            
            # Assign rankings
            for i, rec in enumerate(recommendations):
                rec.ranking = i + 1
            
            # Calculate performance metrics
            best_yield_impact = max(rec.expected_yield_impact for rec in recommendations) if recommendations else 0.0
            lowest_cost_per_acre = min(rec.costs.total_cost_per_acre for rec in recommendations) if recommendations else 0.0
            highest_efficiency = max(rec.efficiency.overall_efficiency for rec in recommendations) if recommendations else 0.0
            best_environmental_score = max(rec.environmental_score for rec in recommendations) if recommendations else 0.0
            
            # Generate method comparison
            method_comparison = self._generate_method_comparison(recommendations)
            
            # Generate key insights
            key_insights = self._generate_key_insights(recommendations, request)
            
            # Generate implementation notes
            implementation_notes = self._generate_implementation_notes(recommendations[0] if recommendations else None, request)
            
            processing_time = (time.time() - start_time) * 1000
            
            result = ApplicationMethodOptimizationResult(
                request_id=request.request_id,
                recommendations=recommendations,
                best_method=recommendations[0] if recommendations else None,
                optimization_objectives={
                    "optimize_for_yield": request.optimize_for_yield,
                    "optimize_for_cost": request.optimize_for_cost,
                    "optimize_for_efficiency": request.optimize_for_efficiency,
                    "optimize_for_environment": request.optimize_for_environment
                },
                total_methods_evaluated=len(all_methods),
                feasible_methods=len(feasible_methods),
                best_yield_impact=best_yield_impact,
                lowest_cost_per_acre=lowest_cost_per_acre,
                highest_efficiency=highest_efficiency,
                best_environmental_score=best_environmental_score,
                method_comparison=method_comparison,
                key_insights=key_insights,
                implementation_notes=implementation_notes,
                processing_time_ms=processing_time
            )
            
            logger.info(f"Application method optimization completed in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Error in application method optimization: {e}")
            raise
    
    def _filter_feasible_methods(
        self,
        request: ApplicationMethodOptimizationRequest,
        all_methods: List[ApplicationMethod]
    ) -> List[ApplicationMethod]:
        """Filter methods based on constraints and preferences."""
        feasible_methods = []
        
        for method in all_methods:
            # Check if method is in avoid list
            if method in request.avoid_methods:
                continue
            
            # Check equipment availability
            required_equipment = self.equipment_compatibility.get(method.value, [])
            if not any(EquipmentType(eq) in request.constraints.available_equipment for eq in required_equipment):
                continue
            
            # Check soil condition compatibility
            compatible_methods = self.soil_method_compatibility.get(request.constraints.soil_conditions.value, [])
            if method.value not in compatible_methods:
                continue
            
            # Check field accessibility
            if request.constraints.field_accessibility < 0.5 and method in [ApplicationMethod.INJECTION, ApplicationMethod.STRIP_TILL]:
                continue
            
            feasible_methods.append(method)
        
        # If preferred methods are specified, prioritize them
        if request.preferred_methods:
            preferred_feasible = [m for m in request.preferred_methods if m in feasible_methods]
            if preferred_feasible:
                feasible_methods = preferred_feasible + [m for m in feasible_methods if m not in preferred_feasible]
        
        return feasible_methods
    
    async def _evaluate_application_method(
        self,
        request: ApplicationMethodOptimizationRequest,
        method: ApplicationMethod
    ) -> ApplicationMethodRecommendation:
        """Evaluate a specific application method."""
        
        # Get efficiency metrics
        efficiency_data = self.efficiency_database.get(method.value, {})
        efficiency = ApplicationEfficiency(**efficiency_data)
        
        # Calculate costs
        cost_data = self.cost_database.get(method.value, {}).copy()
        cost_data["fertilizer_cost_per_acre"] = self._calculate_fertilizer_cost(request)
        cost_data["total_cost_per_acre"] = sum([
            cost_data["application_cost_per_acre"],
            cost_data["equipment_cost_per_acre"],
            cost_data["labor_cost_per_acre"],
            cost_data["fuel_cost_per_acre"],
            cost_data["fertilizer_cost_per_acre"]
        ])
        costs = ApplicationCosts(**cost_data)
        
        # Calculate yield impact
        yield_impact = self._calculate_yield_impact(request, method, efficiency)
        
        # Calculate nutrient availability
        nutrient_availability = efficiency.nutrient_use_efficiency
        
        # Determine optimal timing
        application_timing = self._determine_application_timing(request, method)
        
        # Calculate environmental impact
        environmental_score = self._calculate_environmental_score(method, efficiency)
        runoff_risk = efficiency.runoff_loss
        volatilization_risk = efficiency.volatilization_loss
        
        # Calculate feasibility score
        feasibility_score = self._calculate_feasibility_score(request, method)
        
        # Check constraint violations
        constraint_violations = self._check_constraint_violations(request, method)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            request, method, efficiency, costs, yield_impact, environmental_score, feasibility_score
        )
        
        # Determine fertilizer form and equipment
        fertilizer_form = self._determine_fertilizer_form(request, method)
        equipment_type = self._determine_equipment_type(method)
        
        return ApplicationMethodRecommendation(
            method=method,
            fertilizer_form=fertilizer_form,
            equipment_type=equipment_type,
            efficiency=efficiency,
            costs=costs,
            expected_yield_impact=yield_impact,
            nutrient_availability=nutrient_availability,
            application_timing=application_timing,
            environmental_score=environmental_score,
            runoff_risk=runoff_risk,
            volatilization_risk=volatilization_risk,
            feasibility_score=feasibility_score,
            constraint_violations=constraint_violations,
            overall_score=overall_score,
            ranking=0  # Will be set later
        )
    
    def _calculate_fertilizer_cost(self, request: ApplicationMethodOptimizationRequest) -> float:
        """Calculate fertilizer cost per acre."""
        # Base fertilizer costs (simplified - in production, would use real-time pricing)
        fertilizer_costs = {
            "nitrogen": 0.65,  # $/lb
            "phosphorus": 0.85,  # $/lb
            "potassium": 0.45,  # $/lb
            "complete": 0.60,  # $/lb
            "micronutrients": 2.50,  # $/lb
            "organic": 0.40,  # $/lb
        }
        
        total_cost = 0.0
        for nutrient, amount in request.fertilizer_requirements.items():
            cost_per_lb = fertilizer_costs.get(nutrient.lower(), 0.60)
            total_cost += amount * cost_per_lb
        
        return total_cost
    
    def _calculate_yield_impact(
        self,
        request: ApplicationMethodOptimizationRequest,
        method: ApplicationMethod,
        efficiency: ApplicationEfficiency
    ) -> float:
        """Calculate expected yield impact."""
        # Base yield impact by crop type (bu/acre)
        base_yield_impact = {
            "corn": 15.0,
            "soybean": 8.0,
            "wheat": 12.0,
            "cotton": 0.5,  # bales/acre
            "rice": 20.0
        }
        
        base_impact = base_yield_impact.get(request.crop_type.lower(), 10.0)
        
        # Adjust based on efficiency
        efficiency_factor = efficiency.overall_efficiency
        
        # Adjust based on soil conditions
        soil_factor = 1.0
        if request.soil_ph < 6.0 or request.soil_ph > 7.5:
            soil_factor = 0.9
        if request.organic_matter_percent < 2.0:
            soil_factor = 0.95
        
        # Adjust based on method-specific factors
        method_factor = 1.0
        if method in [ApplicationMethod.BANDED, ApplicationMethod.INJECTION]:
            method_factor = 1.05  # Better placement
        elif method == ApplicationMethod.FOLIAR:
            method_factor = 0.8  # Limited nutrient capacity
        
        return base_impact * efficiency_factor * soil_factor * method_factor
    
    def _determine_application_timing(
        self,
        request: ApplicationMethodOptimizationRequest,
        method: ApplicationMethod
    ) -> str:
        """Determine optimal application timing."""
        timing_by_method = {
            ApplicationMethod.BROADCAST: "Pre-plant or early season",
            ApplicationMethod.BROADCAST_INCORPORATED: "Pre-plant",
            ApplicationMethod.BANDED: "At planting",
            ApplicationMethod.SIDE_DRESS: "Early to mid-season",
            ApplicationMethod.FOLIAR: "Mid to late season",
            ApplicationMethod.FERTIGATION: "Throughout growing season",
            ApplicationMethod.INJECTION: "Pre-plant or early season",
            ApplicationMethod.STRIP_TILL: "Pre-plant",
            ApplicationMethod.NO_TILL: "At planting or early season",
            ApplicationMethod.CONVENTIONAL_TILL: "Pre-plant"
        }
        
        return timing_by_method.get(method, "Seasonal application")
    
    def _calculate_environmental_score(
        self,
        method: ApplicationMethod,
        efficiency: ApplicationEfficiency
    ) -> float:
        """Calculate environmental impact score."""
        # Base environmental scores
        base_scores = {
            ApplicationMethod.BROADCAST: 0.6,
            ApplicationMethod.BROADCAST_INCORPORATED: 0.7,
            ApplicationMethod.BANDED: 0.8,
            ApplicationMethod.SIDE_DRESS: 0.75,
            ApplicationMethod.FOLIAR: 0.9,
            ApplicationMethod.FERTIGATION: 0.85,
            ApplicationMethod.INJECTION: 0.9,
            ApplicationMethod.STRIP_TILL: 0.7,
            ApplicationMethod.NO_TILL: 0.95,
            ApplicationMethod.CONVENTIONAL_TILL: 0.5
        }
        
        base_score = base_scores.get(method, 0.7)
        
        # Adjust based on efficiency losses
        loss_penalty = (
            efficiency.volatilization_loss * 0.3 +
            efficiency.leaching_loss * 0.4 +
            efficiency.runoff_loss * 0.3
        )
        
        return max(0.0, base_score - loss_penalty)
    
    def _calculate_feasibility_score(
        self,
        request: ApplicationMethodOptimizationRequest,
        method: ApplicationMethod
    ) -> float:
        """Calculate feasibility score based on constraints."""
        score = 1.0
        
        # Labor availability
        if request.constraints.labor_availability < 0.5:
            if method in [ApplicationMethod.SIDE_DRESS, ApplicationMethod.INJECTION]:
                score -= 0.3
        
        # Field accessibility
        if request.constraints.field_accessibility < 0.5:
            if method in [ApplicationMethod.INJECTION, ApplicationMethod.STRIP_TILL]:
                score -= 0.4
        
        # Budget constraints
        method_cost = self.cost_database.get(method.value, {}).get("total_cost_per_acre", 0)
        if method_cost > request.constraints.budget_constraints:
            score -= 0.5
        
        return max(0.0, score)
    
    def _check_constraint_violations(
        self,
        request: ApplicationMethodOptimizationRequest,
        method: ApplicationMethod
    ) -> List[str]:
        """Check for constraint violations."""
        violations = []
        
        # Budget constraint
        method_cost = self.cost_database.get(method.value, {}).get("total_cost_per_acre", 0)
        if method_cost > request.constraints.budget_constraints:
            violations.append(f"Exceeds budget constraint (${method_cost:.2f} > ${request.constraints.budget_constraints:.2f})")
        
        # Labor constraint
        if request.constraints.labor_availability < 0.3:
            if method in [ApplicationMethod.SIDE_DRESS, ApplicationMethod.INJECTION]:
                violations.append("Requires high labor availability")
        
        # Equipment constraint
        required_equipment = self.equipment_compatibility.get(method.value, [])
        if not any(EquipmentType(eq) in request.constraints.available_equipment for eq in required_equipment):
            violations.append(f"Required equipment not available: {required_equipment}")
        
        return violations
    
    def _calculate_overall_score(
        self,
        request: ApplicationMethodOptimizationRequest,
        method: ApplicationMethod,
        efficiency: ApplicationEfficiency,
        costs: ApplicationCosts,
        yield_impact: float,
        environmental_score: float,
        feasibility_score: float
    ) -> float:
        """Calculate overall recommendation score."""
        score = 0.0
        total_weight = 0.0
        
        # Yield optimization weight
        if request.optimize_for_yield:
            yield_weight = 0.3
            # Normalize yield impact (assuming max 20 bu/acre)
            normalized_yield = min(yield_impact / 20.0, 1.0)
            score += normalized_yield * yield_weight
            total_weight += yield_weight
        
        # Cost optimization weight
        if request.optimize_for_cost:
            cost_weight = 0.25
            # Normalize cost (assuming max $100/acre)
            normalized_cost = max(0.0, 1.0 - (costs.total_cost_per_acre / 100.0))
            score += normalized_cost * cost_weight
            total_weight += cost_weight
        
        # Efficiency optimization weight
        if request.optimize_for_efficiency:
            efficiency_weight = 0.25
            score += efficiency.overall_efficiency * efficiency_weight
            total_weight += efficiency_weight
        
        # Environmental optimization weight
        if request.optimize_for_environment:
            env_weight = 0.2
            score += environmental_score * env_weight
            total_weight += env_weight
        
        # Feasibility weight (always included)
        feasibility_weight = 0.1
        score += feasibility_score * feasibility_weight
        total_weight += feasibility_weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _determine_fertilizer_form(
        self,
        request: ApplicationMethodOptimizationRequest,
        method: ApplicationMethod
    ) -> FertilizerForm:
        """Determine optimal fertilizer form for method."""
        form_by_method = {
            ApplicationMethod.BROADCAST: FertilizerForm.GRANULAR,
            ApplicationMethod.BROADCAST_INCORPORATED: FertilizerForm.GRANULAR,
            ApplicationMethod.BANDED: FertilizerForm.GRANULAR,
            ApplicationMethod.SIDE_DRESS: FertilizerForm.GRANULAR,
            ApplicationMethod.FOLIAR: FertilizerForm.LIQUID,
            ApplicationMethod.FERTIGATION: FertilizerForm.LIQUID,
            ApplicationMethod.INJECTION: FertilizerForm.LIQUID,
            ApplicationMethod.STRIP_TILL: FertilizerForm.GRANULAR,
            ApplicationMethod.NO_TILL: FertilizerForm.GRANULAR,
            ApplicationMethod.CONVENTIONAL_TILL: FertilizerForm.GRANULAR
        }
        
        return form_by_method.get(method, FertilizerForm.GRANULAR)
    
    def _determine_equipment_type(self, method: ApplicationMethod) -> EquipmentType:
        """Determine required equipment type for method."""
        equipment_by_method = {
            ApplicationMethod.BROADCAST: EquipmentType.BROADCASTER,
            ApplicationMethod.BROADCAST_INCORPORATED: EquipmentType.BROADCASTER,
            ApplicationMethod.BANDED: EquipmentType.PLANTER_MOUNTED,
            ApplicationMethod.SIDE_DRESS: EquipmentType.SIDE_DRESS_BAR,
            ApplicationMethod.FOLIAR: EquipmentType.SPRAYER,
            ApplicationMethod.FERTIGATION: EquipmentType.IRRIGATION_SYSTEM,
            ApplicationMethod.INJECTION: EquipmentType.INJECTION_SYSTEM,
            ApplicationMethod.STRIP_TILL: EquipmentType.STRIP_TILL_TOOLBAR,
            ApplicationMethod.NO_TILL: EquipmentType.PLANTER_MOUNTED,
            ApplicationMethod.CONVENTIONAL_TILL: EquipmentType.CONVENTIONAL_TILLAGE
        }
        
        return equipment_by_method.get(method, EquipmentType.BROADCASTER)
    
    def _generate_method_comparison(self, recommendations: List[ApplicationMethodRecommendation]) -> Dict[str, Dict[str, Any]]:
        """Generate detailed method comparison."""
        comparison = {}
        
        for rec in recommendations:
            comparison[rec.method.value] = {
                "overall_score": rec.overall_score,
                "yield_impact": rec.expected_yield_impact,
                "total_cost": rec.costs.total_cost_per_acre,
                "efficiency": rec.efficiency.overall_efficiency,
                "environmental_score": rec.environmental_score,
                "feasibility_score": rec.feasibility_score,
                "constraint_violations": rec.constraint_violations
            }
        
        return comparison
    
    def _generate_key_insights(
        self,
        recommendations: List[ApplicationMethodRecommendation],
        request: ApplicationMethodOptimizationRequest
    ) -> List[str]:
        """Generate key insights from optimization results."""
        insights = []
        
        if not recommendations:
            return ["No feasible application methods found for current constraints"]
        
        best_method = recommendations[0]
        
        # Best method insights
        insights.append(f"Best method: {best_method.method.value} with {best_method.overall_score:.2f} overall score")
        
        # Cost insights
        cost_range = max(rec.costs.total_cost_per_acre for rec in recommendations) - min(rec.costs.total_cost_per_acre for rec in recommendations)
        insights.append(f"Cost range: ${cost_range:.2f}/acre across all methods")
        
        # Efficiency insights
        efficiency_range = max(rec.efficiency.overall_efficiency for rec in recommendations) - min(rec.efficiency.overall_efficiency for rec in recommendations)
        insights.append(f"Efficiency range: {efficiency_range:.2f} across all methods")
        
        # Environmental insights
        env_range = max(rec.environmental_score for rec in recommendations) - min(rec.environmental_score for rec in recommendations)
        insights.append(f"Environmental impact range: {env_range:.2f} across all methods")
        
        # Constraint insights
        constrained_methods = [rec for rec in recommendations if rec.constraint_violations]
        if constrained_methods:
            insights.append(f"{len(constrained_methods)} methods have constraint violations")
        
        return insights
    
    def _generate_implementation_notes(
        self,
        best_method: Optional[ApplicationMethodRecommendation],
        request: ApplicationMethodOptimizationRequest
    ) -> List[str]:
        """Generate implementation notes."""
        notes = []
        
        if not best_method:
            return ["No implementation possible with current constraints"]
        
        # Equipment notes
        notes.append(f"Required equipment: {best_method.equipment_type.value}")
        
        # Timing notes
        notes.append(f"Optimal timing: {best_method.application_timing}")
        
        # Cost notes
        notes.append(f"Total cost: ${best_method.costs.total_cost_per_acre:.2f}/acre")
        
        # Efficiency notes
        notes.append(f"Expected efficiency: {best_method.efficiency.overall_efficiency:.2f}")
        
        # Constraint notes
        if best_method.constraint_violations:
            notes.append("Constraint violations to address:")
            notes.extend(best_method.constraint_violations)
        
        return notes
    
    async def compare_application_methods(
        self,
        request: ApplicationMethodComparisonRequest
    ) -> ApplicationMethodComparisonResult:
        """
        Compare specific application methods.
        
        Args:
            request: Application method comparison request
            
        Returns:
            ApplicationMethodComparisonResult with detailed comparison
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting application method comparison for {len(request.methods_to_compare)} methods")
            
            # Create optimization request from comparison request
            opt_request = ApplicationMethodOptimizationRequest(
                field_id=request.field_id,
                crop_type=request.crop_type,
                field_size_acres=request.field_size_acres,
                fertilizer_requirements=request.fertilizer_requirements,
                fertilizer_forms=[FertilizerForm.GRANULAR, FertilizerForm.LIQUID],
                soil_type=request.soil_type,
                soil_ph=request.soil_ph,
                constraints=request.constraints,
                preferred_methods=request.methods_to_compare
            )
            
            # Get optimization results
            opt_result = await self.optimize_application_methods(opt_request)
            
            # Filter to only requested methods
            method_comparisons = [rec for rec in opt_result.recommendations if rec.method in request.methods_to_compare]
            
            # Generate comparisons
            yield_comparison = {rec.method.value: rec.expected_yield_impact for rec in method_comparisons}
            cost_comparison = {rec.method.value: rec.costs.total_cost_per_acre for rec in method_comparisons}
            efficiency_comparison = {rec.method.value: rec.efficiency.overall_efficiency for rec in method_comparisons}
            environmental_comparison = {rec.method.value: rec.environmental_score for rec in method_comparisons}
            
            # Generate rankings
            method_rankings = {rec.method.value: rec.ranking for rec in method_comparisons}
            best_method_overall = min(method_comparisons, key=lambda x: x.ranking).method if method_comparisons else None
            
            # Generate key differences
            key_differences = self._generate_comparison_differences(method_comparisons)
            
            # Generate trade-off analysis
            trade_off_analysis = self._generate_trade_off_analysis(method_comparisons)
            
            processing_time = (time.time() - start_time) * 1000
            
            result = ApplicationMethodComparisonResult(
                request_id=request.request_id,
                method_comparisons=method_comparisons,
                yield_comparison=yield_comparison,
                cost_comparison=cost_comparison,
                efficiency_comparison=efficiency_comparison,
                environmental_comparison=environmental_comparison,
                method_rankings=method_rankings,
                best_method_overall=best_method_overall,
                key_differences=key_differences,
                trade_off_analysis=trade_off_analysis,
                processing_time_ms=processing_time
            )
            
            logger.info(f"Application method comparison completed in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Error in application method comparison: {e}")
            raise
    
    def _generate_comparison_differences(self, comparisons: List[ApplicationMethodRecommendation]) -> List[str]:
        """Generate key differences between methods."""
        differences = []
        
        if len(comparisons) < 2:
            return differences
        
        # Cost differences
        costs = [rec.costs.total_cost_per_acre for rec in comparisons]
        max_cost = max(costs)
        min_cost = min(costs)
        if max_cost - min_cost > 10.0:  # Significant cost difference
            differences.append(f"Cost difference: ${max_cost - min_cost:.2f}/acre between methods")
        
        # Efficiency differences
        efficiencies = [rec.efficiency.overall_efficiency for rec in comparisons]
        max_eff = max(efficiencies)
        min_eff = min(efficiencies)
        if max_eff - min_eff > 0.1:  # Significant efficiency difference
            differences.append(f"Efficiency difference: {max_eff - min_eff:.2f} between methods")
        
        # Yield differences
        yields = [rec.expected_yield_impact for rec in comparisons]
        max_yield = max(yields)
        min_yield = min(yields)
        if max_yield - min_yield > 2.0:  # Significant yield difference
            differences.append(f"Yield difference: {max_yield - min_yield:.1f} bu/acre between methods")
        
        return differences
    
    def _generate_trade_off_analysis(self, comparisons: List[ApplicationMethodRecommendation]) -> Dict[str, Any]:
        """Generate trade-off analysis."""
        if len(comparisons) < 2:
            return {}
        
        # Find best and worst for each metric
        best_cost = min(comparisons, key=lambda x: x.costs.total_cost_per_acre)
        best_efficiency = max(comparisons, key=lambda x: x.efficiency.overall_efficiency)
        best_yield = max(comparisons, key=lambda x: x.expected_yield_impact)
        best_environmental = max(comparisons, key=lambda x: x.environmental_score)
        
        return {
            "cost_efficiency_trade_off": {
                "best_cost_method": best_cost.method.value,
                "best_efficiency_method": best_efficiency.method.value,
                "cost_difference": best_efficiency.costs.total_cost_per_acre - best_cost.costs.total_cost_per_acre,
                "efficiency_difference": best_efficiency.efficiency.overall_efficiency - best_cost.efficiency.overall_efficiency
            },
            "yield_cost_trade_off": {
                "best_yield_method": best_yield.method.value,
                "best_cost_method": best_cost.method.value,
                "yield_difference": best_yield.expected_yield_impact - best_cost.expected_yield_impact,
                "cost_difference": best_yield.costs.total_cost_per_acre - best_cost.costs.total_cost_per_acre
            },
            "environmental_cost_trade_off": {
                "best_environmental_method": best_environmental.method.value,
                "best_cost_method": best_cost.method.value,
                "environmental_difference": best_environmental.environmental_score - best_cost.environmental_score,
                "cost_difference": best_environmental.costs.total_cost_per_acre - best_cost.costs.total_cost_per_acre
            }
        }
    
    async def get_application_method_summary(
        self,
        optimization_id: str,
        field_id: str,
        crop_type: str
    ) -> ApplicationMethodSummary:
        """
        Get summary of application method optimization results.
        
        Args:
            optimization_id: Optimization identifier
            field_id: Field identifier
            crop_type: Crop type
            
        Returns:
            ApplicationMethodSummary with key insights
        """
        # This would typically retrieve from database in production
        # For now, return a placeholder summary
        return ApplicationMethodSummary(
            optimization_id=optimization_id,
            field_id=field_id,
            crop_type=crop_type,
            best_method=ApplicationMethod.BANDED,
            best_method_score=0.85,
            expected_yield_impact=12.5,
            total_cost_per_acre=45.20,
            efficiency_score=0.88,
            environmental_score=0.80,
            primary_recommendation="Use banded application for optimal efficiency and yield",
            alternative_methods=[ApplicationMethod.SIDE_DRESS, ApplicationMethod.INJECTION],
            implementation_priority="High",
            key_benefits=["High efficiency", "Good yield impact", "Moderate cost"],
            key_risks=["Requires specialized equipment", "Timing critical"],
            optimization_notes=["Consider soil conditions", "Monitor weather forecast"]
        )