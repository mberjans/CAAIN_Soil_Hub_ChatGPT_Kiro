"""
Advanced Sustainability Optimization Service.

This service provides comprehensive sustainability optimization capabilities including
environmental metrics calculation, multi-objective optimization, carbon footprint tracking,
and sustainability scoring for fertilizer strategy optimization.
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4
import asyncio
from decimal import Decimal
import numpy as np
from scipy.optimize import minimize, differential_evolution
from dataclasses import dataclass

from ..models.environmental_models import (
    EnvironmentalImpactAssessment, SustainabilityMetrics, EnvironmentalImpactLevel
)

logger = logging.getLogger(__name__)


@dataclass
class OptimizationObjective:
    """Represents an optimization objective with weight and target."""
    name: str
    weight: float
    target_value: Optional[float] = None
    minimize: bool = True


@dataclass
class OptimizationConstraint:
    """Represents an optimization constraint."""
    name: str
    constraint_type: str  # 'eq', 'ineq', 'bound'
    value: float
    field: Optional[str] = None


@dataclass
class SustainabilityOptimizationResult:
    """Result of sustainability optimization."""
    optimization_id: UUID
    field_id: UUID
    optimization_objectives: List[OptimizationObjective]
    optimal_fertilizer_rates: Dict[str, float]
    environmental_impact: EnvironmentalImpactAssessment
    sustainability_metrics: SustainabilityMetrics
    optimization_score: float
    trade_off_analysis: Dict[str, Any]
    recommendations: List[str]
    confidence_level: float
    optimization_method: str
    processing_time_ms: float


class SustainabilityOptimizationService:
    """Advanced sustainability optimization service."""
    
    def __init__(self):
        self.optimization_methods = {
            'genetic_algorithm': self._genetic_algorithm_optimization,
            'gradient_descent': self._gradient_descent_optimization,
            'simulated_annealing': self._simulated_annealing_optimization,
            'particle_swarm': self._particle_swarm_optimization
        }
        
        # Default optimization objectives
        self.default_objectives = [
            OptimizationObjective("nitrogen_efficiency", 0.25, minimize=False),
            OptimizationObjective("phosphorus_efficiency", 0.20, minimize=False),
            OptimizationObjective("carbon_footprint", 0.20, minimize=True),
            OptimizationObjective("water_quality_impact", 0.15, minimize=True),
            OptimizationObjective("soil_health_score", 0.10, minimize=False),
            OptimizationObjective("economic_return", 0.10, minimize=False)
        ]
        
        # Default constraints
        self.default_constraints = [
            OptimizationConstraint("max_nitrogen_rate", "bound", 200.0, "nitrogen"),
            OptimizationConstraint("max_phosphorus_rate", "bound", 100.0, "phosphorus"),
            OptimizationConstraint("max_potassium_rate", "bound", 150.0, "potassium"),
            OptimizationConstraint("min_nitrogen_rate", "bound", 50.0, "nitrogen"),
            OptimizationConstraint("min_phosphorus_rate", "bound", 20.0, "phosphorus"),
            OptimizationConstraint("min_potassium_rate", "bound", 30.0, "potassium")
        ]
    
    async def optimize_sustainability(
        self,
        field_id: UUID,
        field_data: Dict[str, Any],
        fertilizer_options: List[Dict[str, Any]],
        optimization_objectives: Optional[List[OptimizationObjective]] = None,
        constraints: Optional[List[OptimizationConstraint]] = None,
        optimization_method: str = "genetic_algorithm",
        include_trade_off_analysis: bool = True
    ) -> SustainabilityOptimizationResult:
        """
        Perform comprehensive sustainability optimization.
        
        Args:
            field_id: Field identifier
            field_data: Field characteristics and soil data
            fertilizer_options: Available fertilizer options
            optimization_objectives: Custom optimization objectives
            constraints: Custom optimization constraints
            optimization_method: Optimization algorithm to use
            include_trade_off_analysis: Whether to include trade-off analysis
            
        Returns:
            Comprehensive sustainability optimization result
        """
        start_time = datetime.utcnow()
        
        try:
            # Use default objectives and constraints if not provided
            objectives = optimization_objectives or self.default_objectives
            constraints = constraints or self.default_constraints
            
            # Validate inputs
            self._validate_optimization_inputs(field_data, fertilizer_options, objectives, constraints)
            
            # Perform optimization
            optimization_result = await self._perform_optimization(
                field_data, fertilizer_options, objectives, constraints, optimization_method
            )
            
            # Calculate environmental impact
            environmental_impact = await self._calculate_environmental_impact(
                field_id, optimization_result, field_data
            )
            
            # Calculate sustainability metrics
            sustainability_metrics = await self._calculate_sustainability_metrics(
                field_id, optimization_result, field_data
            )
            
            # Perform trade-off analysis if requested
            trade_off_analysis = {}
            if include_trade_off_analysis:
                trade_off_analysis = await self._perform_trade_off_analysis(
                    field_data, fertilizer_options, objectives, constraints
                )
            
            # Generate recommendations
            recommendations = await self._generate_sustainability_recommendations(
                optimization_result, environmental_impact, sustainability_metrics, trade_off_analysis
            )
            
            # Calculate overall optimization score
            optimization_score = self._calculate_optimization_score(
                optimization_result, objectives, environmental_impact, sustainability_metrics
            )
            
            # Create result
            result = SustainabilityOptimizationResult(
                optimization_id=uuid4(),
                field_id=field_id,
                optimization_objectives=objectives,
                optimal_fertilizer_rates=optimization_result['optimal_rates'],
                environmental_impact=environmental_impact,
                sustainability_metrics=sustainability_metrics,
                optimization_score=optimization_score,
                trade_off_analysis=trade_off_analysis,
                recommendations=recommendations,
                confidence_level=optimization_result['confidence'],
                optimization_method=optimization_method,
                processing_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error performing sustainability optimization: {e}")
            raise
    
    def _validate_optimization_inputs(
        self,
        field_data: Dict[str, Any],
        fertilizer_options: List[Dict[str, Any]],
        objectives: List[OptimizationObjective],
        constraints: List[OptimizationConstraint]
    ):
        """Validate optimization inputs."""
        if not field_data:
            raise ValueError("Field data is required")
        
        if not fertilizer_options:
            raise ValueError("Fertilizer options are required")
        
        if not objectives:
            raise ValueError("Optimization objectives are required")
        
        if not constraints:
            raise ValueError("Optimization constraints are required")
        
        # Validate objective weights sum to 1.0
        total_weight = sum(obj.weight for obj in objectives)
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Objective weights must sum to 1.0, got {total_weight}")
    
    async def _perform_optimization(
        self,
        field_data: Dict[str, Any],
        fertilizer_options: List[Dict[str, Any]],
        objectives: List[OptimizationObjective],
        constraints: List[OptimizationConstraint],
        method: str
    ) -> Dict[str, Any]:
        """Perform the actual optimization using specified method."""
        try:
            # Get optimization function
            if method not in self.optimization_methods:
                raise ValueError(f"Unknown optimization method: {method}")
            
            optimization_func = self.optimization_methods[method]
            
            # Prepare optimization problem
            problem_data = self._prepare_optimization_problem(
                field_data, fertilizer_options, objectives, constraints
            )
            
            # Run optimization
            result = await optimization_func(problem_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in optimization: {e}")
            raise
    
    def _prepare_optimization_problem(
        self,
        field_data: Dict[str, Any],
        fertilizer_options: List[Dict[str, Any]],
        objectives: List[OptimizationObjective],
        constraints: List[OptimizationConstraint]
    ) -> Dict[str, Any]:
        """Prepare optimization problem data."""
        # Define decision variables (fertilizer rates)
        variables = ['nitrogen_rate', 'phosphorus_rate', 'potassium_rate']
        
        # Set bounds for each variable
        bounds = []
        for var in variables:
            constraint = next((c for c in constraints if c.field == var.split('_')[0]), None)
            if constraint:
                if constraint.name.startswith('max_'):
                    bounds.append((0, constraint.value))
                elif constraint.name.startswith('min_'):
                    bounds.append((constraint.value, float('inf')))
            else:
                bounds.append((0, 300))  # Default bounds
        
        return {
            'variables': variables,
            'bounds': bounds,
            'objectives': objectives,
            'constraints': constraints,
            'field_data': field_data,
            'fertilizer_options': fertilizer_options
        }
    
    async def _genetic_algorithm_optimization(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genetic algorithm optimization."""
        try:
            def objective_function(x):
                """Objective function for genetic algorithm."""
                nitrogen_rate, phosphorus_rate, potassium_rate = x
                
                # Calculate objective values
                objectives = problem_data['objectives']
                total_score = 0.0
                
                for obj in objectives:
                    if obj.name == "nitrogen_efficiency":
                        # Simulate nitrogen efficiency calculation
                        efficiency = min(1.0, nitrogen_rate / 150.0) if nitrogen_rate > 0 else 0.0
                        score = efficiency if not obj.minimize else (1.0 - efficiency)
                    elif obj.name == "phosphorus_efficiency":
                        efficiency = min(1.0, phosphorus_rate / 80.0) if phosphorus_rate > 0 else 0.0
                        score = efficiency if not obj.minimize else (1.0 - efficiency)
                    elif obj.name == "carbon_footprint":
                        # Simulate carbon footprint (higher rates = higher footprint)
                        footprint = (nitrogen_rate * 0.5 + phosphorus_rate * 0.3 + potassium_rate * 0.2) / 100.0
                        score = footprint if obj.minimize else (1.0 - footprint)
                    elif obj.name == "water_quality_impact":
                        # Simulate water quality impact
                        impact = (nitrogen_rate * 0.4 + phosphorus_rate * 0.6) / 200.0
                        score = impact if obj.minimize else (1.0 - impact)
                    elif obj.name == "soil_health_score":
                        # Simulate soil health score
                        health = min(1.0, (nitrogen_rate + phosphorus_rate + potassium_rate) / 300.0)
                        score = health if not obj.minimize else (1.0 - health)
                    elif obj.name == "economic_return":
                        # Simulate economic return
                        return_val = (nitrogen_rate * 2.0 + phosphorus_rate * 1.5 + potassium_rate * 1.0) / 500.0
                        score = return_val if not obj.minimize else (1.0 - return_val)
                    else:
                        score = 0.0
                    
                    total_score += obj.weight * score
                
                return -total_score  # Minimize negative score (maximize positive)
            
            # Run genetic algorithm
            bounds = problem_data['bounds']
            result = differential_evolution(
                objective_function,
                bounds,
                seed=42,
                maxiter=100,
                popsize=15,
                atol=1e-6,
                tol=1e-6
            )
            
            optimal_rates = {
                'nitrogen_rate': result.x[0],
                'phosphorus_rate': result.x[1],
                'potassium_rate': result.x[2]
            }
            
            return {
                'optimal_rates': optimal_rates,
                'objective_value': -result.fun,
                'success': result.success,
                'confidence': 0.85 if result.success else 0.60,
                'iterations': result.nit,
                'method': 'genetic_algorithm'
            }
            
        except Exception as e:
            logger.error(f"Error in genetic algorithm optimization: {e}")
            raise
    
    async def _gradient_descent_optimization(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gradient descent optimization."""
        try:
            def objective_function(x):
                """Objective function for gradient descent."""
                nitrogen_rate, phosphorus_rate, potassium_rate = x
                
                objectives = problem_data['objectives']
                total_score = 0.0
                
                for obj in objectives:
                    if obj.name == "nitrogen_efficiency":
                        efficiency = min(1.0, nitrogen_rate / 150.0) if nitrogen_rate > 0 else 0.0
                        score = efficiency if not obj.minimize else (1.0 - efficiency)
                    elif obj.name == "phosphorus_efficiency":
                        efficiency = min(1.0, phosphorus_rate / 80.0) if phosphorus_rate > 0 else 0.0
                        score = efficiency if not obj.minimize else (1.0 - efficiency)
                    elif obj.name == "carbon_footprint":
                        footprint = (nitrogen_rate * 0.5 + phosphorus_rate * 0.3 + potassium_rate * 0.2) / 100.0
                        score = footprint if obj.minimize else (1.0 - footprint)
                    elif obj.name == "water_quality_impact":
                        impact = (nitrogen_rate * 0.4 + phosphorus_rate * 0.6) / 200.0
                        score = impact if obj.minimize else (1.0 - impact)
                    elif obj.name == "soil_health_score":
                        health = min(1.0, (nitrogen_rate + phosphorus_rate + potassium_rate) / 300.0)
                        score = health if not obj.minimize else (1.0 - health)
                    elif obj.name == "economic_return":
                        return_val = (nitrogen_rate * 2.0 + phosphorus_rate * 1.5 + potassium_rate * 1.0) / 500.0
                        score = return_val if not obj.minimize else (1.0 - return_val)
                    else:
                        score = 0.0
                    
                    total_score += obj.weight * score
                
                return -total_score
            
            # Initial guess
            x0 = [100.0, 50.0, 75.0]  # Initial fertilizer rates
            
            # Run optimization
            result = minimize(
                objective_function,
                x0,
                method='L-BFGS-B',
                bounds=problem_data['bounds'],
                options={'maxiter': 1000}
            )
            
            optimal_rates = {
                'nitrogen_rate': result.x[0],
                'phosphorus_rate': result.x[1],
                'potassium_rate': result.x[2]
            }
            
            return {
                'optimal_rates': optimal_rates,
                'objective_value': -result.fun,
                'success': result.success,
                'confidence': 0.90 if result.success else 0.65,
                'iterations': result.nit,
                'method': 'gradient_descent'
            }
            
        except Exception as e:
            logger.error(f"Error in gradient descent optimization: {e}")
            raise
    
    async def _simulated_annealing_optimization(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulated annealing optimization."""
        # Simplified implementation - in production would use scipy.optimize.dual_annealing
        try:
            # Use gradient descent as fallback for now
            return await self._gradient_descent_optimization(problem_data)
        except Exception as e:
            logger.error(f"Error in simulated annealing optimization: {e}")
            raise
    
    async def _particle_swarm_optimization(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Particle swarm optimization."""
        # Simplified implementation - in production would use pyswarm or similar
        try:
            # Use genetic algorithm as fallback for now
            return await self._genetic_algorithm_optimization(problem_data)
        except Exception as e:
            logger.error(f"Error in particle swarm optimization: {e}")
            raise
    
    async def _calculate_environmental_impact(
        self,
        field_id: UUID,
        optimization_result: Dict[str, Any],
        field_data: Dict[str, Any]
    ) -> EnvironmentalImpactAssessment:
        """Calculate environmental impact based on optimization results."""
        try:
            optimal_rates = optimization_result['optimal_rates']
            
            # Calculate environmental impacts based on fertilizer rates
            nitrogen_rate = optimal_rates['nitrogen_rate']
            phosphorus_rate = optimal_rates['phosphorus_rate']
            potassium_rate = optimal_rates['potassium_rate']
            
            # Simulate environmental impact calculations
            total_nutrient_rate = nitrogen_rate + phosphorus_rate + potassium_rate
            
            # Determine impact levels based on rates
            if total_nutrient_rate > 250:
                runoff_risk = EnvironmentalImpactLevel.HIGH
                groundwater_risk = EnvironmentalImpactLevel.MODERATE
            elif total_nutrient_rate > 150:
                runoff_risk = EnvironmentalImpactLevel.MODERATE
                groundwater_risk = EnvironmentalImpactLevel.LOW
            else:
                runoff_risk = EnvironmentalImpactLevel.LOW
                groundwater_risk = EnvironmentalImpactLevel.LOW
            
            # Air quality impact (generally low for fertilizer application)
            air_quality_impact = EnvironmentalImpactLevel.LOW
            
            # Soil health impact
            if total_nutrient_rate > 200:
                soil_health_impact = EnvironmentalImpactLevel.MODERATE
            else:
                soil_health_impact = EnvironmentalImpactLevel.LOW
            
            # Calculate quantified impacts
            estimated_nitrogen_loss = Decimal(str(nitrogen_rate * 0.15))  # 15% loss rate
            estimated_phosphorus_loss = Decimal(str(phosphorus_rate * 0.05))  # 5% loss rate
            
            # Carbon footprint calculation (simplified)
            carbon_footprint = Decimal(str(
                nitrogen_rate * 0.8 +  # N fertilizer production
                phosphorus_rate * 0.6 +  # P fertilizer production
                potassium_rate * 0.4    # K fertilizer production
            ))
            
            # Generate mitigation recommendations
            recommended_mitigation = []
            if runoff_risk == EnvironmentalImpactLevel.HIGH:
                recommended_mitigation.extend([
                    "Implement cover crops to reduce nutrient loss",
                    "Add buffer strips along field edges",
                    "Use split application timing",
                    "Consider precision application technology"
                ])
            elif runoff_risk == EnvironmentalImpactLevel.MODERATE:
                recommended_mitigation.extend([
                    "Implement cover crops",
                    "Add buffer strips",
                    "Use split application timing"
                ])
            
            # Buffer zone recommendations
            if runoff_risk == EnvironmentalImpactLevel.HIGH:
                buffer_zone_recommendations = Decimal("75")
            elif runoff_risk == EnvironmentalImpactLevel.MODERATE:
                buffer_zone_recommendations = Decimal("50")
            else:
                buffer_zone_recommendations = Decimal("25")
            
            return EnvironmentalImpactAssessment(
                field_id=field_id,
                fertilizer_plan_id=uuid4(),
                nutrient_runoff_risk=runoff_risk,
                groundwater_contamination_risk=groundwater_risk,
                air_quality_impact=air_quality_impact,
                soil_health_impact=soil_health_impact,
                estimated_nitrogen_loss=estimated_nitrogen_loss,
                estimated_phosphorus_loss=estimated_phosphorus_loss,
                carbon_footprint=carbon_footprint,
                recommended_mitigation=recommended_mitigation,
                buffer_zone_recommendations=buffer_zone_recommendations,
                assessment_method="Sustainability Optimization Assessment",
                confidence_level=optimization_result['confidence']
            )
            
        except Exception as e:
            logger.error(f"Error calculating environmental impact: {e}")
            raise
    
    async def _calculate_sustainability_metrics(
        self,
        field_id: UUID,
        optimization_result: Dict[str, Any],
        field_data: Dict[str, Any]
    ) -> SustainabilityMetrics:
        """Calculate sustainability metrics based on optimization results."""
        try:
            optimal_rates = optimization_result['optimal_rates']
            
            # Calculate nutrient use efficiency
            nitrogen_rate = optimal_rates['nitrogen_rate']
            phosphorus_rate = optimal_rates['phosphorus_rate']
            potassium_rate = optimal_rates['potassium_rate']
            
            # Simulate efficiency calculations
            nitrogen_use_efficiency = min(0.95, 0.6 + (nitrogen_rate / 200.0) * 0.3)
            phosphorus_use_efficiency = min(0.90, 0.5 + (phosphorus_rate / 100.0) * 0.4)
            potassium_use_efficiency = min(0.95, 0.7 + (potassium_rate / 150.0) * 0.25)
            
            # Environmental metrics
            total_rate = nitrogen_rate + phosphorus_rate + potassium_rate
            soil_organic_matter_change = Decimal(str(max(0.0, 0.1 + (total_rate / 500.0) * 0.2)))
            erosion_reduction = min(0.3, 0.1 + (total_rate / 400.0) * 0.2)
            
            # Water quality score (inverse relationship with high rates)
            if total_rate > 250:
                water_quality_score = 0.6
            elif total_rate > 150:
                water_quality_score = 0.75
            else:
                water_quality_score = 0.85
            
            # Economic sustainability
            cost_per_unit_yield = Decimal(str(2.0 + (total_rate / 300.0) * 0.5))
            profitability_index = 1.0 + (total_rate / 400.0) * 0.5
            
            # Calculate overall sustainability score
            sustainability_score = (
                nitrogen_use_efficiency * 0.25 +
                phosphorus_use_efficiency * 0.20 +
                potassium_use_efficiency * 0.20 +
                water_quality_score * 0.20 +
                erosion_reduction * 0.15
            )
            
            return SustainabilityMetrics(
                field_id=field_id,
                assessment_period=str(datetime.now().year),
                nitrogen_use_efficiency=nitrogen_use_efficiency,
                phosphorus_use_efficiency=phosphorus_use_efficiency,
                potassium_use_efficiency=potassium_use_efficiency,
                soil_organic_matter_change=soil_organic_matter_change,
                erosion_reduction=erosion_reduction,
                water_quality_score=water_quality_score,
                cost_per_unit_yield=cost_per_unit_yield,
                profitability_index=profitability_index,
                sustainability_score=sustainability_score,
                data_sources=["Optimization results", "Field data", "Environmental models", "Sustainability frameworks"]
            )
            
        except Exception as e:
            logger.error(f"Error calculating sustainability metrics: {e}")
            raise
    
    async def _perform_trade_off_analysis(
        self,
        field_data: Dict[str, Any],
        fertilizer_options: List[Dict[str, Any]],
        objectives: List[OptimizationObjective],
        constraints: List[OptimizationConstraint]
    ) -> Dict[str, Any]:
        """Perform trade-off analysis between different objectives."""
        try:
            # Simulate trade-off analysis by running optimization with different objective weights
            trade_off_scenarios = []
            
            # Scenario 1: Environmental focus
            env_objectives = [
                OptimizationObjective("carbon_footprint", 0.4, minimize=True),
                OptimizationObjective("water_quality_impact", 0.3, minimize=True),
                OptimizationObjective("nitrogen_efficiency", 0.2, minimize=False),
                OptimizationObjective("economic_return", 0.1, minimize=False)
            ]
            
            # Scenario 2: Economic focus
            econ_objectives = [
                OptimizationObjective("economic_return", 0.5, minimize=False),
                OptimizationObjective("nitrogen_efficiency", 0.3, minimize=False),
                OptimizationObjective("carbon_footprint", 0.1, minimize=True),
                OptimizationObjective("water_quality_impact", 0.1, minimize=True)
            ]
            
            # Scenario 3: Balanced approach
            balanced_objectives = [
                OptimizationObjective("nitrogen_efficiency", 0.25, minimize=False),
                OptimizationObjective("economic_return", 0.25, minimize=False),
                OptimizationObjective("carbon_footprint", 0.25, minimize=True),
                OptimizationObjective("water_quality_impact", 0.25, minimize=True)
            ]
            
            scenarios = [
                ("Environmental Focus", env_objectives),
                ("Economic Focus", econ_objectives),
                ("Balanced Approach", balanced_objectives)
            ]
            
            for scenario_name, scenario_objectives in scenarios:
                try:
                    problem_data = self._prepare_optimization_problem(
                        field_data, fertilizer_options, scenario_objectives, constraints
                    )
                    
                    result = await self._genetic_algorithm_optimization(problem_data)
                    
                    trade_off_scenarios.append({
                        "scenario_name": scenario_name,
                        "objectives": scenario_objectives,
                        "optimal_rates": result['optimal_rates'],
                        "objective_value": result['objective_value'],
                        "confidence": result['confidence']
                    })
                    
                except Exception as e:
                    logger.warning(f"Error in trade-off scenario {scenario_name}: {e}")
                    continue
            
            return {
                "scenarios": trade_off_scenarios,
                "analysis_summary": {
                    "total_scenarios": len(trade_off_scenarios),
                    "best_environmental": min(trade_off_scenarios, key=lambda x: x['optimal_rates']['nitrogen_rate'] + x['optimal_rates']['phosphorus_rate']),
                    "best_economic": max(trade_off_scenarios, key=lambda x: x['objective_value']),
                    "most_balanced": next((s for s in trade_off_scenarios if s['scenario_name'] == 'Balanced Approach'), None)
                }
            }
            
        except Exception as e:
            logger.error(f"Error performing trade-off analysis: {e}")
            return {"scenarios": [], "analysis_summary": {}}
    
    async def _generate_sustainability_recommendations(
        self,
        optimization_result: Dict[str, Any],
        environmental_impact: EnvironmentalImpactAssessment,
        sustainability_metrics: SustainabilityMetrics,
        trade_off_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate sustainability recommendations based on optimization results."""
        recommendations = []
        
        optimal_rates = optimization_result['optimal_rates']
        
        # Nitrogen efficiency recommendations
        if sustainability_metrics.nitrogen_use_efficiency < 0.7:
            recommendations.append("Consider split application of nitrogen to improve efficiency")
            recommendations.append("Implement precision application technology for nitrogen")
        
        # Phosphorus efficiency recommendations
        if sustainability_metrics.phosphorus_use_efficiency < 0.6:
            recommendations.append("Use phosphorus-efficient fertilizer formulations")
            recommendations.append("Consider banding phosphorus applications")
        
        # Environmental impact recommendations
        if environmental_impact.nutrient_runoff_risk == EnvironmentalImpactLevel.HIGH:
            recommendations.extend(environmental_impact.recommended_mitigation)
        
        # Water quality recommendations
        if sustainability_metrics.water_quality_score < 0.8:
            recommendations.append("Implement additional water quality protection measures")
            recommendations.append("Consider cover crops to reduce nutrient loss")
        
        # Carbon footprint recommendations
        if environmental_impact.carbon_footprint > 50:
            recommendations.append("Consider organic or slow-release fertilizers to reduce carbon footprint")
            recommendations.append("Optimize application timing to minimize multiple passes")
        
        # Economic sustainability recommendations
        if sustainability_metrics.profitability_index < 1.2:
            recommendations.append("Review fertilizer costs and consider alternative sources")
            recommendations.append("Optimize application rates based on soil test results")
        
        # Trade-off analysis recommendations
        if trade_off_analysis.get("scenarios"):
            scenarios = trade_off_analysis["scenarios"]
            if len(scenarios) > 1:
                recommendations.append("Consider different optimization scenarios based on farm priorities")
                recommendations.append("Evaluate trade-offs between environmental and economic objectives")
        
        # General sustainability recommendations
        recommendations.extend([
            "Regular soil testing to optimize fertilizer rates",
            "Implement precision agriculture technologies",
            "Consider conservation practices for long-term sustainability",
            "Monitor and track sustainability metrics over time"
        ])
        
        return list(set(recommendations))  # Remove duplicates
    
    def _calculate_optimization_score(
        self,
        optimization_result: Dict[str, Any],
        objectives: List[OptimizationObjective],
        environmental_impact: EnvironmentalImpactAssessment,
        sustainability_metrics: SustainabilityMetrics
    ) -> float:
        """Calculate overall optimization score."""
        try:
            # Base score from optimization objective value
            base_score = optimization_result['objective_value']
            
            # Adjust based on environmental impact
            env_adjustment = 1.0
            if environmental_impact.nutrient_runoff_risk == EnvironmentalImpactLevel.HIGH:
                env_adjustment -= 0.2
            elif environmental_impact.nutrient_runoff_risk == EnvironmentalImpactLevel.MODERATE:
                env_adjustment -= 0.1
            
            # Adjust based on sustainability metrics
            sustainability_adjustment = sustainability_metrics.sustainability_score
            
            # Calculate final score
            final_score = base_score * env_adjustment * sustainability_adjustment
            
            return min(1.0, max(0.0, final_score))
            
        except Exception as e:
            logger.error(f"Error calculating optimization score: {e}")
            return 0.5  # Default score
    
    async def get_optimization_history(
        self,
        field_id: UUID,
        limit: int = 10
    ) -> List[SustainabilityOptimizationResult]:
        """Get optimization history for a field."""
        # In a real implementation, this would query a database
        # For now, return empty list
        return []
    
    async def compare_optimization_scenarios(
        self,
        field_id: UUID,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare different optimization scenarios."""
        try:
            comparison_results = []
            
            for scenario in scenarios:
                try:
                    result = await self.optimize_sustainability(
                        field_id=field_id,
                        field_data=scenario.get('field_data', {}),
                        fertilizer_options=scenario.get('fertilizer_options', []),
                        optimization_objectives=scenario.get('objectives'),
                        constraints=scenario.get('constraints'),
                        optimization_method=scenario.get('method', 'genetic_algorithm')
                    )
                    
                    comparison_results.append({
                        "scenario_name": scenario.get('name', 'Unnamed Scenario'),
                        "optimization_score": result.optimization_score,
                        "environmental_impact": result.environmental_impact,
                        "sustainability_metrics": result.sustainability_metrics,
                        "optimal_rates": result.optimal_fertilizer_rates,
                        "recommendations": result.recommendations
                    })
                    
                except Exception as e:
                    logger.warning(f"Error in scenario comparison: {e}")
                    continue
            
            # Rank scenarios by optimization score
            ranked_scenarios = sorted(comparison_results, key=lambda x: x['optimization_score'], reverse=True)
            
            return {
                "scenarios": comparison_results,
                "ranked_scenarios": ranked_scenarios,
                "best_scenario": ranked_scenarios[0] if ranked_scenarios else None,
                "comparison_summary": {
                    "total_scenarios": len(comparison_results),
                    "average_score": sum(s['optimization_score'] for s in comparison_results) / len(comparison_results) if comparison_results else 0.0,
                    "score_range": {
                        "min": min(s['optimization_score'] for s in comparison_results) if comparison_results else 0.0,
                        "max": max(s['optimization_score'] for s in comparison_results) if comparison_results else 0.0
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error comparing optimization scenarios: {e}")
            return {"scenarios": [], "ranked_scenarios": [], "best_scenario": None, "comparison_summary": {}}