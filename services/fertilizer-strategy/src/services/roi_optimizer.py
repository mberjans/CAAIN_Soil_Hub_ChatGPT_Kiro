"""
Fertilizer ROI Optimization Service.

This service implements advanced fertilizer ROI optimization using multiple
optimization methods including linear programming, quadratic programming,
and genetic algorithms.
"""

import asyncio
import logging
import time
import uuid
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
import numpy as np
from scipy.optimize import minimize, linprog
from scipy import stats
import math

from ..models.roi_models import (
    ROIOptimizationRequest,
    ROIOptimizationResponse,
    OptimizationResult,
    NutrientRecommendation,
    SensitivityAnalysis,
    RiskAssessment,
    MarginalReturnAnalysis,
    YieldResponseCurve,
    BreakEvenAnalysis,
    OptimizationSummary,
    OptimizationMethod,
    RiskTolerance,
    NutrientType
)

logger = logging.getLogger(__name__)


class FertilizerROIOptimizer:
    """
    Advanced fertilizer ROI optimization service.
    
    This service provides comprehensive ROI optimization for fertilizer strategies
    using multiple optimization methods and considering various constraints.
    """

    def __init__(self):
        """Initialize the ROI optimizer."""
        self.optimization_methods = {
            OptimizationMethod.LINEAR_PROGRAMMING: self._linear_programming_optimization,
            OptimizationMethod.QUADRATIC_PROGRAMMING: self._quadratic_programming_optimization,
            OptimizationMethod.GENETIC_ALGORITHM: self._genetic_algorithm_optimization,
            OptimizationMethod.GRADIENT_DESCENT: self._gradient_descent_optimization
        }

    async def optimize_fertilizer_roi(
        self,
        request: ROIOptimizationRequest
    ) -> ROIOptimizationResponse:
        """
        Optimize fertilizer ROI for given fields and constraints.
        
        Args:
            request: ROI optimization request with field data and constraints
            
        Returns:
            ROIOptimizationResponse with optimization results
        """
        start_time = time.time()
        optimization_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting ROI optimization {optimization_id}")
            
            # Validate input data
            self._validate_optimization_request(request)
            
            # Perform optimization based on selected method
            optimization_method = self.optimization_methods.get(
                request.optimization_method,
                self._linear_programming_optimization
            )
            
            optimization_result = await optimization_method(request)
            
            # Perform sensitivity analysis if requested
            sensitivity_analysis = None
            if request.include_sensitivity_analysis:
                sensitivity_analysis = await self._perform_sensitivity_analysis(
                    request, optimization_result
                )
            
            # Perform risk assessment if requested
            risk_assessment = None
            if request.include_risk_assessment:
                risk_assessment = await self._perform_risk_assessment(
                    request, optimization_result
                )
            
            # Generate alternative scenarios
            alternative_scenarios = await self._generate_alternative_scenarios(
                request, optimization_result
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                request, optimization_result, risk_assessment
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            response = ROIOptimizationResponse(
                optimization_result=optimization_result,
                sensitivity_analysis=sensitivity_analysis,
                risk_assessment=risk_assessment,
                alternative_scenarios=alternative_scenarios,
                recommendations=recommendations,
                processing_time_ms=processing_time
            )
            
            logger.info(f"Completed ROI optimization {optimization_id} in {processing_time:.2f}ms")
            return response
            
        except Exception as e:
            logger.error(f"Error in ROI optimization {optimization_id}: {e}")
            raise

    async def _linear_programming_optimization(
        self,
        request: ROIOptimizationRequest
    ) -> OptimizationResult:
        """Perform linear programming optimization."""
        logger.info("Performing linear programming optimization")
        
        # Prepare optimization variables
        fields = request.fields
        products = request.fertilizer_products
        constraints = request.constraints
        
        # Calculate objective function coefficients
        objective_coeffs = []
        constraint_matrix = []
        constraint_bounds = []
        
        for field in fields:
            for product in products:
                # Calculate profit per unit of fertilizer
                yield_response = self._calculate_yield_response(field, product)
                revenue_per_unit = yield_response * field.crop_price
                cost_per_unit = product.price_per_unit
                profit_per_unit = revenue_per_unit - cost_per_unit
                
                objective_coeffs.append(profit_per_unit)
        
        # Set up constraints
        # Budget constraint
        if constraints.budget_limit:
            budget_constraint = [product.price_per_unit for product in products for _ in fields]
            constraint_matrix.append(budget_constraint)
            constraint_bounds.append(constraints.budget_limit)
        
        # Per-acre cost constraint
        if constraints.max_per_acre_cost:
            per_acre_constraint = [product.price_per_unit for product in products]
            constraint_matrix.append(per_acre_constraint)
            constraint_bounds.append(constraints.max_per_acre_cost)
        
        # Nutrient rate constraints
        nutrient_mapping = {'N': 'max_nitrogen_rate', 'P': 'max_phosphorus_rate', 'K': 'max_potassium_rate'}
        for nutrient, constraint_name in nutrient_mapping.items():
            constraint_value = getattr(constraints, constraint_name, None)
            if constraint_value:
                nutrient_constraint = [
                    product.nutrient_content.get(nutrient, 0) / 100
                    for product in products for _ in fields
                ]
                constraint_matrix.append(nutrient_constraint)
                constraint_bounds.append(constraint_value)
        
        # Solve linear programming problem
        try:
            result = linprog(
                c=[-coeff for coeff in objective_coeffs],  # Minimize negative profit (maximize profit)
                A_ub=constraint_matrix,
                b_ub=constraint_bounds,
                bounds=(0, None),  # Non-negative variables
                method='highs'
            )
            
            if result.success:
                return await self._create_optimization_result(
                    request, result.x, result.fun
                )
            else:
                raise ValueError(f"Linear programming optimization failed: {result.message}")
                
        except Exception as e:
            logger.error(f"Linear programming optimization error: {e}")
            # Fallback to simplified optimization
            return await self._simplified_optimization(request)

    async def _quadratic_programming_optimization(
        self,
        request: ROIOptimizationRequest
    ) -> OptimizationResult:
        """Perform quadratic programming optimization."""
        logger.info("Performing quadratic programming optimization")
        
        # This is a simplified implementation
        # In production, use a proper QP solver like CVXPY or OSQP
        
        fields = request.fields
        products = request.fertilizer_products
        
        # Define objective function (quadratic)
        def objective(x):
            total_cost = 0
            total_revenue = 0
            
            for i, field in enumerate(fields):
                for j, product in enumerate(products):
                    idx = i * len(products) + j
                    rate = x[idx]
                    
                    # Cost component (linear)
                    cost = rate * product.price_per_unit * field.acres
                    total_cost += cost
                    
                    # Revenue component (quadratic due to diminishing returns)
                    yield_response = self._calculate_yield_response(field, product)
                    revenue = rate * yield_response * field.crop_price * field.acres
                    # Apply diminishing returns
                    revenue *= (1 - 0.1 * rate / 100)  # Simplified diminishing returns
                    total_revenue += revenue
            
            return -(total_revenue - total_cost)  # Minimize negative profit
        
        # Set up constraints
        constraints_list = []
        
        # Budget constraint
        if request.constraints.budget_limit:
            def budget_constraint(x):
                total_cost = 0
                for i, field in enumerate(fields):
                    for j, product in enumerate(products):
                        idx = i * len(products) + j
                        total_cost += x[idx] * product.price_per_unit * field.acres
                return request.constraints.budget_limit - total_cost
            
            constraints_list.append({'type': 'ineq', 'fun': budget_constraint})
        
        # Solve optimization
        try:
            # Initial guess
            x0 = [10.0] * (len(fields) * len(products))  # Start with 10 units per product per field
            
            result = minimize(
                objective,
                x0,
                method='SLSQP',
                constraints=constraints_list,
                bounds=[(0, 200)] * len(x0)  # Reasonable bounds
            )
            
            if result.success:
                return await self._create_optimization_result(
                    request, result.x, result.fun
                )
            else:
                raise ValueError(f"Quadratic programming optimization failed: {result.message}")
                
        except Exception as e:
            logger.error(f"Quadratic programming optimization error: {e}")
            return await self._simplified_optimization(request)

    async def _genetic_algorithm_optimization(
        self,
        request: ROIOptimizationRequest
    ) -> OptimizationResult:
        """Perform genetic algorithm optimization."""
        logger.info("Performing genetic algorithm optimization")
        
        # Simplified genetic algorithm implementation
        # In production, use DEAP or similar library
        
        fields = request.fields
        products = request.fertilizer_products
        population_size = 50
        generations = 100
        
        # Initialize population
        population = []
        for _ in range(population_size):
            individual = []
            for field in fields:
                for product in products:
                    # Random rate between 0 and max rate
                    max_rate = 200  # Default max rate
                    if request.constraints.max_nitrogen_rate and 'N' in product.nutrient_content:
                        max_rate = min(max_rate, request.constraints.max_nitrogen_rate)
                    individual.append(np.random.uniform(0, max_rate))
            population.append(individual)
        
        # Evolution loop
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                fitness = await self._calculate_fitness(individual, request)
                fitness_scores.append(fitness)
            
            # Selection (keep top 50%)
            sorted_indices = np.argsort(fitness_scores)[::-1]
            elite_size = population_size // 2
            elite = [population[i] for i in sorted_indices[:elite_size]]
            
            # Generate new population
            new_population = elite.copy()
            while len(new_population) < population_size:
                # Crossover
                parent1 = np.random.choice(elite)
                parent2 = np.random.choice(elite)
                child = self._crossover(parent1, parent2)
                
                # Mutation
                child = self._mutate(child, request)
                
                new_population.append(child)
            
            population = new_population
        
        # Find best solution
        best_fitness = -float('inf')
        best_individual = None
        
        for individual in population:
            fitness = await self._calculate_fitness(individual, request)
            if fitness > best_fitness:
                best_fitness = fitness
                best_individual = individual
        
        return await self._create_optimization_result(
            request, best_individual, -best_fitness
        )

    async def _gradient_descent_optimization(
        self,
        request: ROIOptimizationRequest
    ) -> OptimizationResult:
        """Perform gradient descent optimization."""
        logger.info("Performing gradient descent optimization")
        
        fields = request.fields
        products = request.fertilizer_products
        
        # Define objective function
        def objective(x):
            total_profit = 0
            for i, field in enumerate(fields):
                for j, product in enumerate(products):
                    idx = i * len(products) + j
                    rate = x[idx]
                    
                    # Calculate profit
                    yield_response = self._calculate_yield_response(field, product)
                    revenue = rate * yield_response * field.crop_price * field.acres
                    cost = rate * product.price_per_unit * field.acres
                    profit = revenue - cost
                    
                    total_profit += profit
            
            return -total_profit  # Minimize negative profit
        
        # Gradient descent
        learning_rate = 0.01
        max_iterations = 1000
        tolerance = 1e-6
        
        # Initial guess
        x = np.array([10.0] * (len(fields) * len(products)))
        
        for iteration in range(max_iterations):
            # Calculate gradient numerically
            gradient = np.zeros_like(x)
            for i in range(len(x)):
                x_plus = x.copy()
                x_plus[i] += 1e-6
                x_minus = x.copy()
                x_minus[i] -= 1e-6
                
                gradient[i] = (objective(x_plus) - objective(x_minus)) / (2e-6)
            
            # Update parameters
            x_new = x - learning_rate * gradient
            
            # Apply constraints
            x_new = np.maximum(x_new, 0)  # Non-negative
            
            # Check convergence
            if np.linalg.norm(x_new - x) < tolerance:
                break
            
            x = x_new
        
        return await self._create_optimization_result(
            request, x, objective(x)
        )

    async def _simplified_optimization(
        self,
        request: ROIOptimizationRequest
    ) -> OptimizationResult:
        """Simplified optimization as fallback."""
        logger.info("Performing simplified optimization")
        
        fields = request.fields
        products = request.fertilizer_products
        
        # Simple greedy optimization
        best_rates = []
        total_profit = 0
        
        for field in fields:
            field_profit = 0
            field_rates = []
            
            for product in products:
                # Calculate optimal rate for this product
                optimal_rate = self._calculate_optimal_rate(field, product, request.constraints)
                field_rates.append(optimal_rate)
                
                # Calculate profit
                yield_response = self._calculate_yield_response(field, product)
                revenue = optimal_rate * yield_response * field.crop_price * field.acres
                cost = optimal_rate * product.price_per_unit * field.acres
                profit = revenue - cost
                field_profit += profit
            
            best_rates.extend(field_rates)
            total_profit += field_profit
        
        return await self._create_optimization_result(
            request, best_rates, -total_profit
        )

    def _calculate_yield_response(
        self,
        field_data: Any,
        product: Any
    ) -> float:
        """Calculate yield response for a fertilizer product."""
        # Simplified yield response calculation
        # In production, use sophisticated yield response models
        
        base_yield = field_data.target_yield
        soil_n = field_data.soil_tests.get('N', 0)
        
        # Calculate nutrient need
        crop_n_requirement = base_yield * 1.2  # Simplified N requirement
        n_deficit = max(0, crop_n_requirement - soil_n)
        
        # Calculate response
        n_content = product.nutrient_content.get('N', 0) / 100
        if n_content > 0:
            response = min(n_deficit * 0.8, 50)  # Cap response at 50 bu/acre
        else:
            response = 0
        
        return response

    def _calculate_optimal_rate(
        self,
        field_data: Any,
        product: Any,
        constraints: Any
    ) -> float:
        """Calculate optimal application rate for a product."""
        # Simplified optimal rate calculation
        base_rate = 100  # Default rate
        
        # Apply constraints
        if constraints.max_nitrogen_rate and 'N' in product.nutrient_content:
            n_content = product.nutrient_content['N'] / 100
            max_rate = constraints.max_nitrogen_rate / n_content if n_content > 0 else 0
            base_rate = min(base_rate, max_rate)
        
        if constraints.max_per_acre_cost:
            max_rate_by_cost = constraints.max_per_acre_cost / product.price_per_unit
            base_rate = min(base_rate, max_rate_by_cost)
        
        return max(0, base_rate)

    async def _calculate_fitness(
        self,
        individual: List[float],
        request: ROIOptimizationRequest
    ) -> float:
        """Calculate fitness for genetic algorithm."""
        total_profit = 0
        
        fields = request.fields
        products = request.fertilizer_products
        
        for i, field in enumerate(fields):
            for j, product in enumerate(products):
                idx = i * len(products) + j
                rate = individual[idx]
                
                # Calculate profit
                yield_response = self._calculate_yield_response(field, product)
                revenue = rate * yield_response * field.crop_price * field.acres
                cost = rate * product.price_per_unit * field.acres
                profit = revenue - cost
                
                total_profit += profit
        
        return total_profit

    def _crossover(self, parent1: List[float], parent2: List[float]) -> List[float]:
        """Crossover operation for genetic algorithm."""
        child = []
        for i in range(len(parent1)):
            if np.random.random() < 0.5:
                child.append(parent1[i])
            else:
                child.append(parent2[i])
        return child

    def _mutate(self, individual: List[float], request: ROIOptimizationRequest) -> List[float]:
        """Mutation operation for genetic algorithm."""
        mutated = individual.copy()
        mutation_rate = 0.1
        
        for i in range(len(mutated)):
            if np.random.random() < mutation_rate:
                # Random mutation
                mutated[i] = max(0, mutated[i] + np.random.normal(0, 10))
        
        return mutated

    async def _create_optimization_result(
        self,
        request: ROIOptimizationRequest,
        rates: List[float],
        objective_value: float
    ) -> OptimizationResult:
        """Create optimization result from rates and objective value."""
        fields = request.fields
        products = request.fertilizer_products
        
        total_revenue = 0
        total_cost = 0
        nutrient_recommendations = []
        
        for i, field in enumerate(fields):
            field_revenue = 0
            field_cost = 0
            
            for j, product in enumerate(products):
                idx = i * len(products) + j
                rate = rates[idx]
                
                # Calculate revenue and cost
                yield_response = self._calculate_yield_response(field, product)
                revenue = rate * yield_response * field.crop_price * field.acres
                cost = rate * product.price_per_unit * field.acres
                
                field_revenue += revenue
                field_cost += cost
                
                # Create nutrient recommendation
                for nutrient, content in product.nutrient_content.items():
                    nutrient_rate = rate * content / 100
                    if nutrient_rate > 0:
                        recommendation = NutrientRecommendation(
                            field_id=field.field_id,
                            nutrient_type=NutrientType(nutrient),
                            recommended_rate=nutrient_rate,
                            unit="lbs/acre",
                            product_recommendations=[{
                                "product_id": product.product_id,
                                "product_name": product.product_name,
                                "rate": rate,
                                "unit": product.unit
                            }],
                            expected_yield_response=yield_response,
                            cost_per_acre=cost / field.acres
                        )
                        nutrient_recommendations.append(recommendation)
            
            total_revenue += field_revenue
            total_cost += field_cost
        
        net_profit = total_revenue - total_cost
        roi_percentage = (net_profit / total_cost * 100) if total_cost > 0 else 0
        
        # Calculate break-even yield
        total_acres = sum(field.acres for field in fields)
        break_even_yield = total_cost / (total_acres * fields[0].crop_price) if fields else 0
        
        return OptimizationResult(
            optimization_id=str(uuid.uuid4()),
            total_expected_revenue=total_revenue,
            total_fertilizer_cost=total_cost,
            net_profit=net_profit,
            roi_percentage=roi_percentage,
            break_even_yield=break_even_yield,
            marginal_return_rate=roi_percentage,  # Simplified
            risk_adjusted_return=roi_percentage * 0.9,  # Simplified risk adjustment
            nutrient_recommendations=nutrient_recommendations,
            optimization_metadata={
                "method": request.optimization_method.value,
                "fields_optimized": len(fields),
                "products_considered": len(products),
                "objective_value": objective_value
            }
        )

    async def _perform_sensitivity_analysis(
        self,
        request: ROIOptimizationRequest,
        result: OptimizationResult
    ) -> List[SensitivityAnalysis]:
        """Perform sensitivity analysis on optimization results."""
        logger.info("Performing sensitivity analysis")
        
        sensitivity_analyses = []
        
        # Analyze sensitivity to crop price
        base_price = request.fields[0].crop_price
        price_range = [base_price * 0.8, base_price * 0.9, base_price, base_price * 1.1, base_price * 1.2]
        
        roi_impacts = []
        for price in price_range:
            # Simplified impact calculation
            if base_price > 0:
                impact = (price - base_price) / base_price * result.roi_percentage
                roi_impacts.append(result.roi_percentage + impact)
            else:
                roi_impacts.append(result.roi_percentage)
        
        sensitivity_analyses.append(SensitivityAnalysis(
            parameter="crop_price",
            base_value=base_price,
            sensitivity_range=price_range,
            roi_impact=roi_impacts,
            critical_threshold=base_price * 0.7,
            risk_level="medium"
        ))
        
        # Analyze sensitivity to fertilizer cost
        base_cost = result.total_fertilizer_cost
        cost_range = [base_cost * 0.8, base_cost * 0.9, base_cost, base_cost * 1.1, base_cost * 1.2]
        
        roi_impacts = []
        for cost in cost_range:
            if base_cost > 0:
                impact = -(cost - base_cost) / base_cost * result.roi_percentage
                roi_impacts.append(result.roi_percentage + impact)
            else:
                roi_impacts.append(result.roi_percentage)
        
        sensitivity_analyses.append(SensitivityAnalysis(
            parameter="fertilizer_cost",
            base_value=base_cost,
            sensitivity_range=cost_range,
            roi_impact=roi_impacts,
            critical_threshold=base_cost * 1.3,
            risk_level="high"
        ))
        
        return sensitivity_analyses

    async def _perform_risk_assessment(
        self,
        request: ROIOptimizationRequest,
        result: OptimizationResult
    ) -> RiskAssessment:
        """Perform risk assessment on optimization results."""
        logger.info("Performing risk assessment")
        
        risk_factors = []
        overall_risk_score = 0.5  # Base risk score
        
        # Price volatility risk
        if request.goals.risk_tolerance == RiskTolerance.CONSERVATIVE:
            price_risk = 0.3
        elif request.goals.risk_tolerance == RiskTolerance.MODERATE:
            price_risk = 0.5
        else:
            price_risk = 0.7
        
        risk_factors.append({
            "factor": "price_volatility",
            "risk_level": price_risk,
            "description": "Crop and fertilizer price volatility"
        })
        
        # Yield variability risk
        yield_risk = 0.4
        risk_factors.append({
            "factor": "yield_variability",
            "risk_level": yield_risk,
            "description": "Weather and yield variability"
        })
        
        # Budget constraint risk
        if request.constraints.budget_limit:
            budget_utilization = result.total_fertilizer_cost / request.constraints.budget_limit
            if budget_utilization > 0.9:
                budget_risk = 0.8
            elif budget_utilization > 0.7:
                budget_risk = 0.5
            else:
                budget_risk = 0.2
            
            risk_factors.append({
                "factor": "budget_constraint",
                "risk_level": budget_risk,
                "description": "Budget constraint utilization"
            })
        
        # Calculate overall risk score
        overall_risk_score = np.mean([factor["risk_level"] for factor in risk_factors])
        
        # Generate mitigation strategies
        mitigation_strategies = []
        if overall_risk_score > 0.7:
            mitigation_strategies.extend([
                "Consider crop insurance",
                "Diversify fertilizer sources",
                "Implement phased application"
            ])
        elif overall_risk_score > 0.5:
            mitigation_strategies.extend([
                "Monitor market prices closely",
                "Consider forward contracts"
            ])
        
        return RiskAssessment(
            overall_risk_score=overall_risk_score,
            risk_factors=risk_factors,
            mitigation_strategies=mitigation_strategies,
            confidence_level=0.8,  # Simplified confidence calculation
            scenario_analysis={
                "best_case_roi": result.roi_percentage * 1.2,
                "worst_case_roi": result.roi_percentage * 0.6,
                "expected_roi": result.roi_percentage
            }
        )

    async def _generate_alternative_scenarios(
        self,
        request: ROIOptimizationRequest,
        result: OptimizationResult
    ) -> List[Dict[str, Any]]:
        """Generate alternative optimization scenarios."""
        logger.info("Generating alternative scenarios")
        
        scenarios = []
        
        # Conservative scenario
        conservative_scenario = {
            "scenario_name": "Conservative",
            "description": "Lower fertilizer rates with reduced risk",
            "fertilizer_cost": result.total_fertilizer_cost * 0.8,
            "expected_revenue": result.total_expected_revenue * 0.9,
            "roi_percentage": result.roi_percentage * 0.8,
            "risk_level": "low"
        }
        scenarios.append(conservative_scenario)
        
        # Aggressive scenario
        aggressive_scenario = {
            "scenario_name": "Aggressive",
            "description": "Higher fertilizer rates with increased potential return",
            "fertilizer_cost": result.total_fertilizer_cost * 1.2,
            "expected_revenue": result.total_expected_revenue * 1.1,
            "roi_percentage": result.roi_percentage * 1.1,
            "risk_level": "high"
        }
        scenarios.append(aggressive_scenario)
        
        return scenarios

    async def _generate_recommendations(
        self,
        request: ROIOptimizationRequest,
        result: OptimizationResult,
        risk_assessment: Optional[RiskAssessment]
    ) -> List[str]:
        """Generate recommendations based on optimization results."""
        recommendations = []
        
        # ROI-based recommendations
        if result.roi_percentage > 200:
            recommendations.append("Excellent ROI - consider expanding fertilizer program")
        elif result.roi_percentage > 100:
            recommendations.append("Good ROI - proceed with recommended fertilizer strategy")
        elif result.roi_percentage > 50:
            recommendations.append("Moderate ROI - consider optimizing fertilizer rates")
        else:
            recommendations.append("Low ROI - review fertilizer strategy and consider alternatives")
        
        # Risk-based recommendations
        if risk_assessment and risk_assessment.overall_risk_score > 0.7:
            recommendations.append("High risk detected - implement risk mitigation strategies")
        
        # Budget recommendations
        if request.constraints.budget_limit:
            budget_utilization = result.total_fertilizer_cost / request.constraints.budget_limit
            if budget_utilization > 0.9:
                recommendations.append("Budget utilization high - consider cost optimization")
        
        return recommendations

    def _validate_optimization_request(self, request: ROIOptimizationRequest) -> None:
        """Validate optimization request."""
        if not request.fields:
            raise ValueError("At least one field is required")
        
        if not request.fertilizer_products:
            raise ValueError("At least one fertilizer product is required")
        
        for field in request.fields:
            if field.acres <= 0:
                raise ValueError(f"Field {field.field_id} must have positive acres")
            
            if field.target_yield <= 0:
                raise ValueError(f"Field {field.field_id} must have positive target yield")
            
            if field.crop_price <= 0:
                raise ValueError(f"Field {field.field_id} must have positive crop price")
        
        for product in request.fertilizer_products:
            if product.price_per_unit <= 0:
                raise ValueError(f"Product {product.product_id} must have positive price")
            
            if not product.nutrient_content:
                raise ValueError(f"Product {product.product_id} must have nutrient content")


# Service instance for dependency injection
roi_optimizer_service = FertilizerROIOptimizer()