"""
Budget Constraint Optimization Service.

This service implements comprehensive budget constraint optimization with
multi-objective optimization, Pareto frontier analysis, and constraint relaxation.
"""

import asyncio
import logging
import time
import uuid
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
import numpy as np
from scipy.optimize import minimize, differential_evolution
from scipy import stats
import math
from itertools import combinations

from ..models.roi_models import (
    ROIOptimizationRequest,
    BudgetConstraint,
    TimingConstraint,
    OptimizationConstraints,
    BudgetAllocationResult,
    ParetoFrontierPoint,
    ConstraintRelaxationAnalysis,
    MultiObjectiveOptimizationResult,
    FieldData,
    FertilizerProduct,
    OptimizationGoals,
    RiskTolerance
)

logger = logging.getLogger(__name__)


class BudgetConstraintOptimizer:
    """
    Comprehensive budget constraint optimization service.
    
    This service provides advanced budget constraint optimization including:
    - Multi-objective optimization with Pareto frontier analysis
    - Budget allocation optimization across fields and nutrients
    - Constraint relaxation analysis
    - Trade-off analysis between objectives
    - Timing and resource constraint integration
    """

    def __init__(self):
        """Initialize the budget constraint optimizer."""
        self.optimization_methods = {
            'pareto_frontier': self._generate_pareto_frontier,
            'budget_allocation': self._optimize_budget_allocation,
            'constraint_relaxation': self._analyze_constraint_relaxation
        }

    async def optimize_budget_constraints(
        self,
        request: ROIOptimizationRequest
    ) -> MultiObjectiveOptimizationResult:
        """
        Perform comprehensive budget constraint optimization.
        
        Args:
            request: ROI optimization request with budget constraints
            
        Returns:
            MultiObjectiveOptimizationResult with comprehensive analysis
        """
        start_time = time.time()
        optimization_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting budget constraint optimization {optimization_id}")
            
            # Validate budget constraints
            self._validate_budget_constraints(request)
            
            # Generate Pareto frontier
            pareto_frontier = await self._generate_pareto_frontier(request)
            
            # Select recommended scenario
            recommended_scenario = await self._select_recommended_scenario(
                pareto_frontier, request.goals
            )
            
            # Optimize budget allocation
            budget_allocations = await self._optimize_budget_allocation(
                request, recommended_scenario
            )
            
            # Perform constraint relaxation analysis
            constraint_relaxation_analysis = await self._analyze_constraint_relaxation(
                request, recommended_scenario
            )
            
            # Generate trade-off analysis
            trade_off_analysis = await self._generate_trade_off_analysis(
                pareto_frontier, request.goals
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            result = MultiObjectiveOptimizationResult(
                optimization_id=optimization_id,
                pareto_frontier=pareto_frontier,
                recommended_scenario=recommended_scenario,
                budget_allocations=budget_allocations,
                constraint_relaxation_analysis=constraint_relaxation_analysis,
                trade_off_analysis=trade_off_analysis,
                optimization_metadata={
                    "method": "budget_constraint_optimization",
                    "fields_optimized": len(request.fields),
                    "products_considered": len(request.fertilizer_products),
                    "processing_time_ms": processing_time,
                    "pareto_frontier_size": len(pareto_frontier)
                }
            )
            
            logger.info(f"Completed budget constraint optimization {optimization_id} in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Error in budget constraint optimization {optimization_id}: {e}")
            raise

    async def _generate_pareto_frontier(
        self,
        request: ROIOptimizationRequest
    ) -> List[ParetoFrontierPoint]:
        """Generate Pareto frontier for multi-objective optimization."""
        logger.info("Generating Pareto frontier")
        
        pareto_points = []
        
        # Define objective weights for different scenarios
        objective_scenarios = [
            {"profit": 1.0, "environment": 0.0, "risk": 0.0},  # Pure profit maximization
            {"profit": 0.8, "environment": 0.2, "risk": 0.0},   # Profit with environmental consideration
            {"profit": 0.6, "environment": 0.4, "risk": 0.0},   # Balanced profit-environment
            {"profit": 0.4, "environment": 0.6, "risk": 0.0}, # Environment-focused
            {"profit": 0.0, "environment": 1.0, "risk": 0.0}, # Pure environmental optimization
            {"profit": 0.7, "environment": 0.0, "risk": 0.3},  # Profit with risk consideration
            {"profit": 0.5, "environment": 0.3, "risk": 0.2},  # Balanced all objectives
            {"profit": 0.3, "environment": 0.5, "risk": 0.2},  # Environment-risk focused
            {"profit": 0.0, "environment": 0.0, "risk": 1.0},  # Pure risk minimization
            {"profit": 0.6, "environment": 0.2, "risk": 0.2},  # Moderate balance
        ]
        
        for i, weights in enumerate(objective_scenarios):
            scenario_id = f"scenario_{i+1}"
            
            # Optimize for this scenario
            scenario_result = await self._optimize_scenario(request, weights)
            
            # Calculate objectives
            total_cost = scenario_result["total_cost"]
            total_revenue = scenario_result["total_revenue"]
            roi_percentage = scenario_result["roi_percentage"]
            environmental_score = scenario_result["environmental_score"]
            risk_score = scenario_result["risk_score"]
            yield_target_achievement = scenario_result["yield_target_achievement"]
            budget_utilization = scenario_result["budget_utilization"]
            
            # Generate trade-off description
            trade_off_description = self._generate_trade_off_description(weights)
            
            pareto_point = ParetoFrontierPoint(
                scenario_id=scenario_id,
                total_cost=total_cost,
                total_revenue=total_revenue,
                roi_percentage=roi_percentage,
                environmental_score=environmental_score,
                risk_score=risk_score,
                yield_target_achievement=yield_target_achievement,
                budget_utilization=budget_utilization,
                trade_off_description=trade_off_description
            )
            
            pareto_points.append(pareto_point)
        
        # Filter to true Pareto frontier (remove dominated solutions)
        pareto_frontier = self._filter_pareto_frontier(pareto_points)
        
        logger.info(f"Generated Pareto frontier with {len(pareto_frontier)} points")
        return pareto_frontier

    async def _optimize_scenario(
        self,
        request: ROIOptimizationRequest,
        objective_weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Optimize a single scenario with given objective weights."""
        
        fields = request.fields
        products = request.fertilizer_products
        constraints = request.constraints
        
        # Define multi-objective function
        def objective(x):
            total_cost = 0
            total_revenue = 0
            environmental_impact = 0
            risk_factors = 0
            
            for i, field in enumerate(fields):
                for j, product in enumerate(products):
                    idx = i * len(products) + j
                    rate = x[idx]
                    
                    # Cost calculation
                    cost = rate * product.price_per_unit * field.acres
                    total_cost += cost
                    
                    # Revenue calculation
                    yield_response = self._calculate_yield_response(field, product)
                    revenue = rate * yield_response * field.crop_price * field.acres
                    total_revenue += revenue
                    
                    # Environmental impact calculation
                    env_impact = self._calculate_environmental_impact(product, rate, field)
                    environmental_impact += env_impact
                    
                    # Risk calculation
                    risk = self._calculate_risk_factor(product, rate, field)
                    risk_factors += risk
            
            # Calculate objectives
            profit = total_revenue - total_cost
            roi = (profit / total_cost * 100) if total_cost > 0 else 0
            
            # Normalize objectives (0-1 scale)
            normalized_profit = min(profit / 100000, 1.0)  # Cap at $100k profit
            normalized_environment = max(0, 1 - environmental_impact / 1000)  # Lower impact is better
            normalized_risk = max(0, 1 - risk_factors / 100)  # Lower risk is better
            
            # Weighted objective
            weighted_objective = (
                objective_weights["profit"] * normalized_profit +
                objective_weights["environment"] * normalized_environment +
                objective_weights["risk"] * normalized_risk
            )
            
            return -weighted_objective  # Minimize negative (maximize positive)
        
        # Set up constraints
        constraints_list = []
        
        # Budget constraints
        if constraints.budget_constraint:
            budget_constraint = constraints.budget_constraint
            if budget_constraint.total_budget_limit:
                def total_budget_constraint(x):
                    total_cost = 0
                    for i, field in enumerate(fields):
                        for j, product in enumerate(products):
                            idx = i * len(products) + j
                            total_cost += x[idx] * product.price_per_unit * field.acres
                    return budget_constraint.total_budget_limit - total_cost
                
                constraints_list.append({'type': 'ineq', 'fun': total_budget_constraint})
        
        # Per-acre budget constraints
        if constraints.budget_constraint and constraints.budget_constraint.per_acre_budget_limit:
            def per_acre_budget_constraint(x):
                violations = 0
                for i, field in enumerate(fields):
                    field_cost = 0
                    for j, product in enumerate(products):
                        idx = i * len(products) + j
                        field_cost += x[idx] * product.price_per_unit
                    if field_cost > constraints.budget_constraint.per_acre_budget_limit:
                        violations += field_cost - constraints.budget_constraint.per_acre_budget_limit
                return -violations  # Negative violations (constraint satisfied)
            
            constraints_list.append({'type': 'ineq', 'fun': per_acre_budget_constraint})
        
        # Nutrient rate constraints
        nutrient_constraints = {
            'N': constraints.max_nitrogen_rate,
            'P': constraints.max_phosphorus_rate,
            'K': constraints.max_potassium_rate
        }
        
        for nutrient, max_rate in nutrient_constraints.items():
            if max_rate:
                def nutrient_constraint(x, nutrient=nutrient, max_rate=max_rate):
                    violations = 0
                    for i, field in enumerate(fields):
                        field_nutrient_rate = 0
                        for j, product in enumerate(products):
                            idx = i * len(products) + j
                            nutrient_content = product.nutrient_content.get(nutrient, 0) / 100
                            field_nutrient_rate += x[idx] * nutrient_content
                        if field_nutrient_rate > max_rate:
                            violations += field_nutrient_rate - max_rate
                    return -violations
                
                constraints_list.append({'type': 'ineq', 'fun': nutrient_constraint})
        
        # Solve optimization
        try:
            # Initial guess
            x0 = [10.0] * (len(fields) * len(products))
            
            # Bounds
            bounds = [(0, 200)] * len(x0)
            
            result = minimize(
                objective,
                x0,
                method='SLSQP',
                constraints=constraints_list,
                bounds=bounds,
                options={'maxiter': 1000}
            )
            
            if result.success:
                # Calculate final metrics
                total_cost = 0
                total_revenue = 0
                environmental_impact = 0
                risk_factors = 0
                
                for i, field in enumerate(fields):
                    for j, product in enumerate(products):
                        idx = i * len(products) + j
                        rate = result.x[idx]
                        
                        cost = rate * product.price_per_unit * field.acres
                        total_cost += cost
                        
                        yield_response = self._calculate_yield_response(field, product)
                        revenue = rate * yield_response * field.crop_price * field.acres
                        total_revenue += revenue
                        
                        env_impact = self._calculate_environmental_impact(product, rate, field)
                        environmental_impact += env_impact
                        
                        risk = self._calculate_risk_factor(product, rate, field)
                        risk_factors += risk
                
                profit = total_revenue - total_cost
                roi_percentage = (profit / total_cost * 100) if total_cost > 0 else 0
                
                # Calculate yield target achievement
                total_target_yield = sum(field.target_yield * field.acres for field in fields)
                total_actual_yield = sum(
                    field.target_yield * field.acres + 
                    sum(result.x[i * len(products) + j] * self._calculate_yield_response(field, products[j]) * field.acres
                        for j in range(len(products)))
                    for i, field in enumerate(fields)
                )
                yield_target_achievement = (total_actual_yield / total_target_yield * 100) if total_target_yield > 0 else 0
                
                # Calculate budget utilization
                budget_limit = constraints.budget_constraint.total_budget_limit if constraints.budget_constraint else None
                budget_utilization = (total_cost / budget_limit * 100) if budget_limit and budget_limit > 0 else 100
                
                return {
                    "total_cost": total_cost,
                    "total_revenue": total_revenue,
                    "roi_percentage": roi_percentage,
                    "environmental_score": max(0, 100 - environmental_impact),  # Convert to score (higher is better)
                    "risk_score": max(0, 100 - risk_factors),  # Convert to score (higher is better)
                    "yield_target_achievement": yield_target_achievement,
                    "budget_utilization": budget_utilization,
                    "rates": result.x
                }
            else:
                raise ValueError(f"Optimization failed: {result.message}")
                
        except Exception as e:
            logger.error(f"Scenario optimization error: {e}")
            # Return default values
            return {
                "total_cost": 0,
                "total_revenue": 0,
                "roi_percentage": 0,
                "environmental_score": 50,
                "risk_score": 50,
                "yield_target_achievement": 0,
                "budget_utilization": 0,
                "rates": [0] * (len(fields) * len(products))
            }

    async def _select_recommended_scenario(
        self,
        pareto_frontier: List[ParetoFrontierPoint],
        goals: OptimizationGoals
    ) -> ParetoFrontierPoint:
        """Select recommended scenario based on optimization goals."""
        
        if not pareto_frontier:
            raise ValueError("No Pareto frontier points available")
        
        # Score each scenario based on goals
        best_scenario = None
        best_score = -float('inf')
        
        for scenario in pareto_frontier:
            score = 0
            
            # ROI scoring
            if goals.primary_goal == "profit_maximization":
                score += scenario.roi_percentage * goals.yield_priority
            
            # Environmental scoring
            score += scenario.environmental_score * goals.environmental_priority
            
            # Risk scoring (lower risk is better)
            risk_score = (100 - scenario.risk_score) * (1 - goals.risk_tolerance.value.count('conservative') / 3)
            score += risk_score
            
            # Yield target achievement
            score += scenario.yield_target_achievement * goals.yield_priority
            
            if score > best_score:
                best_score = score
                best_scenario = scenario
        
        return best_scenario or pareto_frontier[0]

    async def _optimize_budget_allocation(
        self,
        request: ROIOptimizationRequest,
        scenario: ParetoFrontierPoint
    ) -> List[BudgetAllocationResult]:
        """Optimize budget allocation across fields."""
        
        budget_allocations = []
        fields = request.fields
        products = request.fertilizer_products
        
        # Calculate field priorities based on various factors
        field_priorities = self._calculate_field_priorities(fields, request.goals)
        
        # Allocate budget based on priorities and constraints
        total_budget = request.constraints.budget_constraint.total_budget_limit if request.constraints.budget_constraint else scenario.total_cost
        
        for i, field in enumerate(fields):
            priority_score = field_priorities[i]
            
            # Calculate field budget allocation
            if request.constraints.budget_constraint and request.constraints.budget_constraint.allow_budget_reallocation:
                # Proportional allocation based on priority
                total_priority = sum(field_priorities)
                allocated_budget = total_budget * (priority_score / total_priority) if total_priority > 0 else total_budget / len(fields)
            else:
                # Equal allocation
                allocated_budget = total_budget / len(fields)
            
            # Apply per-field budget limit
            if request.constraints.budget_constraint and request.constraints.budget_constraint.per_field_budget_limit:
                allocated_budget = min(allocated_budget, request.constraints.budget_constraint.per_field_budget_limit)
            
            # Calculate nutrient and product allocation
            nutrient_allocation = {}
            product_allocation = {}
            
            for product in products:
                product_cost = 0
                for nutrient, content in product.nutrient_content.items():
                    nutrient_cost = allocated_budget * (content / 100) * 0.3  # Simplified allocation
                    nutrient_allocation[nutrient] = nutrient_allocation.get(nutrient, 0) + nutrient_cost
                    product_cost += nutrient_cost
                product_allocation[product.product_id] = product_cost
            
            # Calculate expected ROI for this field
            expected_roi = self._calculate_field_roi(field, allocated_budget, products)
            
            # Check for constraint violations
            constraint_violations = self._check_field_constraint_violations(
                field, allocated_budget, request.constraints
            )
            
            budget_allocation = BudgetAllocationResult(
                field_id=field.field_id,
                allocated_budget=allocated_budget,
                budget_utilization_percentage=(allocated_budget / (total_budget / len(fields)) * 100) if total_budget > 0 else 100,
                nutrient_allocation=nutrient_allocation,
                product_allocation=product_allocation,
                expected_roi=expected_roi,
                priority_score=priority_score,
                constraint_violations=constraint_violations
            )
            
            budget_allocations.append(budget_allocation)
        
        return budget_allocations

    async def _analyze_constraint_relaxation(
        self,
        request: ROIOptimizationRequest,
        scenario: ParetoFrontierPoint
    ) -> List[ConstraintRelaxationAnalysis]:
        """Analyze the impact of relaxing various constraints."""
        
        relaxation_analyses = []
        constraints = request.constraints
        
        # Budget constraint relaxation
        if constraints.budget_constraint and constraints.budget_constraint.total_budget_limit:
            relaxation_analysis = await self._analyze_budget_relaxation(request, scenario)
            relaxation_analyses.append(relaxation_analysis)
        
        # Nutrient rate constraint relaxation
        for nutrient, max_rate in [
            ('N', constraints.max_nitrogen_rate),
            ('P', constraints.max_phosphorus_rate),
            ('K', constraints.max_potassium_rate)
        ]:
            if max_rate:
                relaxation_analysis = await self._analyze_nutrient_relaxation(
                    request, scenario, nutrient, max_rate
                )
                relaxation_analyses.append(relaxation_analysis)
        
        # Per-acre cost constraint relaxation
        if constraints.max_per_acre_cost:
            relaxation_analysis = await self._analyze_per_acre_cost_relaxation(request, scenario)
            relaxation_analyses.append(relaxation_analysis)
        
        return relaxation_analyses

    async def _analyze_budget_relaxation(
        self,
        request: ROIOptimizationRequest,
        scenario: ParetoFrontierPoint
    ) -> ConstraintRelaxationAnalysis:
        """Analyze budget constraint relaxation impact."""
        
        original_budget = request.constraints.budget_constraint.total_budget_limit
        relaxed_budget = original_budget * 1.2  # 20% increase
        
        # Simulate optimization with relaxed budget
        relaxed_request = request.model_copy()
        relaxed_request.constraints.budget_constraint.total_budget_limit = relaxed_budget
        
        relaxed_scenario = await self._optimize_scenario(relaxed_request, {"profit": 1.0, "environment": 0.0, "risk": 0.0})
        
        # Calculate impact
        roi_improvement = relaxed_scenario["roi_percentage"] - scenario.roi_percentage
        cost_increase = relaxed_budget - original_budget
        
        # Generate recommendation
        if roi_improvement > 10 and cost_increase < original_budget * 0.3:
            recommendation = "Consider relaxing budget constraint - significant ROI improvement with moderate cost increase"
        elif roi_improvement > 5:
            recommendation = "Budget relaxation may be beneficial - evaluate cost-benefit trade-off"
        else:
            recommendation = "Budget constraint relaxation not recommended - minimal ROI improvement"
        
        return ConstraintRelaxationAnalysis(
            constraint_type="total_budget_limit",
            original_value=original_budget,
            relaxed_value=relaxed_budget,
            relaxation_impact={
                "roi_improvement": roi_improvement,
                "cost_increase": cost_increase,
                "yield_improvement": relaxed_scenario["yield_target_achievement"] - scenario.yield_target_achievement
            },
            cost_of_relaxation=cost_increase,
            benefit_of_relaxation=roi_improvement * original_budget / 100,  # Simplified benefit calculation
            recommendation=recommendation
        )

    async def _analyze_nutrient_relaxation(
        self,
        request: ROIOptimizationRequest,
        scenario: ParetoFrontierPoint,
        nutrient: str,
        max_rate: float
    ) -> ConstraintRelaxationAnalysis:
        """Analyze nutrient rate constraint relaxation impact."""
        
        relaxed_rate = max_rate * 1.25  # 25% increase
        
        # Simulate optimization with relaxed nutrient rate
        relaxed_request = request.model_copy()
        if nutrient == "N":
            relaxed_request.constraints.max_nitrogen_rate = relaxed_rate
        elif nutrient == "P":
            relaxed_request.constraints.max_phosphorus_rate = relaxed_rate
        elif nutrient == "K":
            relaxed_request.constraints.max_potassium_rate = relaxed_rate
        
        relaxed_scenario = await self._optimize_scenario(relaxed_request, {"profit": 1.0, "environment": 0.0, "risk": 0.0})
        
        # Calculate impact
        roi_improvement = relaxed_scenario["roi_percentage"] - scenario.roi_percentage
        environmental_impact = scenario.environmental_score - relaxed_scenario["environmental_score"]
        
        # Generate recommendation
        if roi_improvement > 15 and environmental_impact < 10:
            recommendation = f"Consider relaxing {nutrient} rate constraint - significant ROI improvement with minimal environmental impact"
        elif roi_improvement > 5:
            recommendation = f"{nutrient} rate relaxation may be beneficial - evaluate environmental trade-off"
        else:
            recommendation = f"{nutrient} rate constraint relaxation not recommended - minimal benefit"
        
        return ConstraintRelaxationAnalysis(
            constraint_type=f"max_{nutrient.lower()}_rate",
            original_value=max_rate,
            relaxed_value=relaxed_rate,
            relaxation_impact={
                "roi_improvement": roi_improvement,
                "environmental_impact": environmental_impact,
                "yield_improvement": relaxed_scenario["yield_target_achievement"] - scenario.yield_target_achievement
            },
            cost_of_relaxation=environmental_impact,
            benefit_of_relaxation=roi_improvement,
            recommendation=recommendation
        )

    async def _analyze_per_acre_cost_relaxation(
        self,
        request: ROIOptimizationRequest,
        scenario: ParetoFrontierPoint
    ) -> ConstraintRelaxationAnalysis:
        """Analyze per-acre cost constraint relaxation impact."""
        
        original_cost = request.constraints.max_per_acre_cost
        relaxed_cost = original_cost * 1.3  # 30% increase
        
        # Simulate optimization with relaxed per-acre cost
        relaxed_request = request.model_copy()
        relaxed_request.constraints.max_per_acre_cost = relaxed_cost
        
        relaxed_scenario = await self._optimize_scenario(relaxed_request, {"profit": 1.0, "environment": 0.0, "risk": 0.0})
        
        # Calculate impact
        roi_improvement = relaxed_scenario["roi_percentage"] - scenario.roi_percentage
        cost_per_acre_increase = relaxed_cost - original_cost
        
        # Generate recommendation
        if roi_improvement > 12:
            recommendation = "Consider relaxing per-acre cost constraint - significant ROI improvement"
        elif roi_improvement > 5:
            recommendation = "Per-acre cost relaxation may be beneficial - evaluate cost-benefit"
        else:
            recommendation = "Per-acre cost constraint relaxation not recommended - minimal benefit"
        
        return ConstraintRelaxationAnalysis(
            constraint_type="max_per_acre_cost",
            original_value=original_cost,
            relaxed_value=relaxed_cost,
            relaxation_impact={
                "roi_improvement": roi_improvement,
                "cost_per_acre_increase": cost_per_acre_increase,
                "yield_improvement": relaxed_scenario["yield_target_achievement"] - scenario.yield_target_achievement
            },
            cost_of_relaxation=cost_per_acre_increase,
            benefit_of_relaxation=roi_improvement,
            recommendation=recommendation
        )

    async def _generate_trade_off_analysis(
        self,
        pareto_frontier: List[ParetoFrontierPoint],
        goals: OptimizationGoals
    ) -> Dict[str, Any]:
        """Generate comprehensive trade-off analysis."""
        
        if len(pareto_frontier) < 2:
            return {"message": "Insufficient data for trade-off analysis"}
        
        # Calculate correlation between objectives
        roi_values = [point.roi_percentage for point in pareto_frontier]
        environmental_values = [point.environmental_score for point in pareto_frontier]
        risk_values = [point.risk_score for point in pareto_frontier]
        
        roi_env_correlation = np.corrcoef(roi_values, environmental_values)[0, 1]
        roi_risk_correlation = np.corrcoef(roi_values, risk_values)[0, 1]
        env_risk_correlation = np.corrcoef(environmental_values, risk_values)[0, 1]
        
        # Identify trade-offs
        trade_offs = []
        
        if roi_env_correlation < -0.3:
            trade_offs.append({
                "type": "profit_environment",
                "description": "Higher profits typically come with higher environmental impact",
                "correlation": roi_env_correlation,
                "severity": "moderate" if abs(roi_env_correlation) < 0.6 else "high"
            })
        
        if roi_risk_correlation > 0.3:
            trade_offs.append({
                "type": "profit_risk",
                "description": "Higher profits typically come with higher risk",
                "correlation": roi_risk_correlation,
                "severity": "moderate" if roi_risk_correlation < 0.6 else "high"
            })
        
        if env_risk_correlation < -0.3:
            trade_offs.append({
                "type": "environment_risk",
                "description": "Lower environmental impact typically comes with higher risk",
                "correlation": env_risk_correlation,
                "severity": "moderate" if abs(env_risk_correlation) < 0.6 else "high"
            })
        
        # Calculate efficiency frontier
        efficiency_scores = []
        for point in pareto_frontier:
            # Composite efficiency score
            efficiency = (
                point.roi_percentage * goals.yield_priority +
                point.environmental_score * goals.environmental_priority +
                (100 - point.risk_score) * (1 - goals.cost_priority)
            ) / 3
            efficiency_scores.append(efficiency)
        
        max_efficiency_idx = np.argmax(efficiency_scores)
        most_efficient_scenario = pareto_frontier[max_efficiency_idx]
        
        return {
            "correlations": {
                "profit_environment": roi_env_correlation,
                "profit_risk": roi_risk_correlation,
                "environment_risk": env_risk_correlation
            },
            "trade_offs": trade_offs,
            "efficiency_analysis": {
                "most_efficient_scenario": most_efficient_scenario.scenario_id,
                "efficiency_score": efficiency_scores[max_efficiency_idx],
                "description": "Scenario with best balance of all objectives"
            },
            "recommendations": self._generate_trade_off_recommendations(trade_offs, goals)
        }

    def _generate_trade_off_recommendations(
        self,
        trade_offs: List[Dict[str, Any]],
        goals: OptimizationGoals
    ) -> List[str]:
        """Generate recommendations based on trade-off analysis."""
        
        recommendations = []
        
        for trade_off in trade_offs:
            if trade_off["type"] == "profit_environment":
                if goals.environmental_priority > 0.7:
                    recommendations.append("Consider accepting lower profits for better environmental outcomes")
                elif goals.yield_priority > 0.8:
                    recommendations.append("Consider accepting higher environmental impact for better profits")
                else:
                    recommendations.append("Balance profit and environmental objectives based on farm priorities")
            
            elif trade_off["type"] == "profit_risk":
                if goals.risk_tolerance == RiskTolerance.CONSERVATIVE:
                    recommendations.append("Consider accepting lower profits for reduced risk")
                elif goals.risk_tolerance == RiskTolerance.AGGRESSIVE:
                    recommendations.append("Consider accepting higher risk for better profits")
                else:
                    recommendations.append("Balance profit and risk objectives based on risk tolerance")
        
        return recommendations

    def _filter_pareto_frontier(
        self,
        points: List[ParetoFrontierPoint]
    ) -> List[ParetoFrontierPoint]:
        """Filter points to true Pareto frontier (remove dominated solutions)."""
        
        pareto_frontier = []
        
        for point in points:
            is_dominated = False
            
            for other_point in points:
                if point == other_point:
                    continue
                
                # Check if other_point dominates point
                if (other_point.roi_percentage >= point.roi_percentage and
                    other_point.environmental_score >= point.environmental_score and
                    other_point.risk_score <= point.risk_score and
                    (other_point.roi_percentage > point.roi_percentage or
                     other_point.environmental_score > point.environmental_score or
                     other_point.risk_score < point.risk_score)):
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_frontier.append(point)
        
        return pareto_frontier

    def _generate_trade_off_description(self, weights: Dict[str, float]) -> str:
        """Generate description of trade-offs for a scenario."""
        
        descriptions = []
        
        if weights["profit"] > 0.7:
            descriptions.append("Profit-focused")
        elif weights["environment"] > 0.7:
            descriptions.append("Environment-focused")
        elif weights["risk"] > 0.7:
            descriptions.append("Risk-minimizing")
        else:
            descriptions.append("Balanced")
        
        if weights["profit"] > 0.5 and weights["environment"] > 0.3:
            descriptions.append("with environmental consideration")
        elif weights["profit"] > 0.5 and weights["risk"] > 0.3:
            descriptions.append("with risk consideration")
        elif weights["environment"] > 0.5 and weights["risk"] > 0.3:
            descriptions.append("with risk consideration")
        
        return " ".join(descriptions)

    def _calculate_field_priorities(
        self,
        fields: List[FieldData],
        goals: OptimizationGoals
    ) -> List[float]:
        """Calculate field priorities based on various factors."""
        
        priorities = []
        
        for field in fields:
            priority = 0
            
            # Yield potential priority
            priority += field.target_yield * goals.yield_priority * 0.4
            
            # Crop price priority
            priority += field.crop_price * goals.yield_priority * 0.3
            
            # Field size priority (larger fields get higher priority)
            priority += field.acres * 0.2
            
            # Historical yield priority
            if field.historical_yield:
                priority += field.historical_yield * 0.1
            
            priorities.append(priority)
        
        # Normalize priorities
        max_priority = max(priorities) if priorities else 1
        priorities = [p / max_priority for p in priorities]
        
        return priorities

    def _calculate_field_roi(
        self,
        field: FieldData,
        budget: float,
        products: List[FertilizerProduct]
    ) -> float:
        """Calculate expected ROI for a field with given budget."""
        
        # Simplified ROI calculation
        total_cost = budget
        total_revenue = 0
        
        for product in products:
            # Simplified rate calculation
            rate = budget / (len(products) * product.price_per_unit * field.acres)
            yield_response = self._calculate_yield_response(field, product)
            revenue = rate * yield_response * field.crop_price * field.acres
            total_revenue += revenue
        
        profit = total_revenue - total_cost
        roi = (profit / total_cost * 100) if total_cost > 0 else 0
        
        return max(0.0, float(roi))  # Ensure non-negative ROI

    def _check_field_constraint_violations(
        self,
        field: FieldData,
        budget: float,
        constraints: OptimizationConstraints
    ) -> List[str]:
        """Check for constraint violations for a field."""
        
        violations = []
        
        # Check per-acre cost constraint
        if constraints.max_per_acre_cost:
            cost_per_acre = budget / field.acres
            if cost_per_acre > constraints.max_per_acre_cost:
                violations.append(f"Per-acre cost exceeds limit: ${cost_per_acre:.2f} > ${constraints.max_per_acre_cost:.2f}")
        
        # Check per-field budget constraint
        if constraints.budget_constraint and constraints.budget_constraint.per_field_budget_limit:
            if budget > constraints.budget_constraint.per_field_budget_limit:
                violations.append(f"Field budget exceeds limit: ${budget:.2f} > ${constraints.budget_constraint.per_field_budget_limit:.2f}")
        
        return violations

    def _calculate_yield_response(
        self,
        field_data: FieldData,
        product: FertilizerProduct
    ) -> float:
        """Calculate yield response for a fertilizer product."""
        # Simplified yield response calculation
        base_yield = field_data.target_yield
        soil_n = field_data.soil_tests.get('N', 0)
        
        # Calculate nutrient need
        crop_n_requirement = base_yield * 1.2  # Simplified N requirement
        n_deficit = max(0, crop_n_requirement - soil_n)
        
        # Calculate response
        n_content = product.nutrient_content.get('N', 0) / 100
        if n_content > 0:
            response = min(n_deficit * 0.8, 50.0)  # Cap response at 50 bu/acre
        else:
            response = 0.0
        
        return float(response)

    def _calculate_environmental_impact(
        self,
        product: FertilizerProduct,
        rate: float,
        field: FieldData
    ) -> float:
        """Calculate environmental impact score."""
        # Simplified environmental impact calculation
        impact = 0
        
        # Nitrogen impact
        n_content = product.nutrient_content.get('N', 0) / 100
        impact += rate * n_content * 0.5  # Nitrogen leaching potential
        
        # Phosphorus impact
        p_content = product.nutrient_content.get('P', 0) / 100
        impact += rate * p_content * 0.3  # Phosphorus runoff potential
        
        # Application method impact
        if product.application_method == "broadcast":
            impact += rate * 0.1  # Higher impact for broadcast
        elif product.application_method == "injected":
            impact += rate * 0.05  # Lower impact for injection
        
        return impact

    def _calculate_risk_factor(
        self,
        product: FertilizerProduct,
        rate: float,
        field: FieldData
    ) -> float:
        """Calculate risk factor for fertilizer application."""
        # Simplified risk calculation
        risk = 0
        
        # Price volatility risk
        risk += 0.2  # Base price risk
        
        # Application timing risk
        risk += 0.1  # Base timing risk
        
        # Product availability risk
        if not product.availability:
            risk += 0.3
        
        # Rate-based risk
        if rate > 150:
            risk += 0.2  # High rate risk
        
        return risk

    def _validate_budget_constraints(self, request: ROIOptimizationRequest) -> None:
        """Validate budget constraints."""
        constraints = request.constraints
        
        if not constraints.budget_constraint:
            raise ValueError("Budget constraints are required for budget constraint optimization")
        
        budget_constraint = constraints.budget_constraint
        
        if budget_constraint.total_budget_limit and budget_constraint.total_budget_limit <= 0:
            raise ValueError("Total budget limit must be positive")
        
        if budget_constraint.per_field_budget_limit and budget_constraint.per_field_budget_limit <= 0:
            raise ValueError("Per-field budget limit must be positive")
        
        if budget_constraint.per_acre_budget_limit and budget_constraint.per_acre_budget_limit <= 0:
            raise ValueError("Per-acre budget limit must be positive")
        
        if budget_constraint.budget_flexibility_percentage < 0 or budget_constraint.budget_flexibility_percentage > 50:
            raise ValueError("Budget flexibility percentage must be between 0 and 50")
        
        if budget_constraint.budget_utilization_target < 80 or budget_constraint.budget_utilization_target > 100:
            raise ValueError("Budget utilization target must be between 80 and 100")


# Service instance for dependency injection
budget_constraint_optimizer_service = BudgetConstraintOptimizer()
