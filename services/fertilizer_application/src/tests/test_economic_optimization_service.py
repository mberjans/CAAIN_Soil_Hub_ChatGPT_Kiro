"""
Comprehensive tests for Economic Optimization Service.

This module tests all aspects of the economic optimization service including
optimization algorithms, scenario modeling, sensitivity analysis, and investment planning.
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import AsyncMock, patch, MagicMock
from typing import List, Dict, Any

from src.services.economic_optimization_service import (
    EconomicOptimizationService, OptimizationAlgorithm, OptimizationObjective,
    ScenarioType, OptimizationConstraint, OptimizationResult, ScenarioParameters
)
from src.models.application_models import (
    ApplicationMethod, FieldConditions, CropRequirements, 
    FertilizerSpecification, EquipmentSpecification
)


class TestEconomicOptimizationService:
    """Test suite for EconomicOptimizationService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return EconomicOptimizationService()
    
    @pytest.fixture
    def sample_application_methods(self):
        """Sample application methods for testing."""
        return [
            ApplicationMethod(
                method_id="broadcast",
                method_name="Broadcast Application",
                method_type="granular",
                efficiency_score=0.8,
                cost_per_acre=50.0,
                labor_requirements=2.0,
                equipment_requirements=["spreader"],
                environmental_impact_score=0.6
            ),
            ApplicationMethod(
                method_id="banded",
                method_name="Banded Application",
                method_type="granular",
                efficiency_score=0.9,
                cost_per_acre=75.0,
                labor_requirements=3.0,
                equipment_requirements=["planter"],
                environmental_impact_score=0.8
            ),
            ApplicationMethod(
                method_id="liquid",
                method_name="Liquid Application",
                method_type="liquid",
                efficiency_score=0.85,
                cost_per_acre=60.0,
                labor_requirements=2.5,
                equipment_requirements=["sprayer"],
                environmental_impact_score=0.7
            )
        ]
    
    @pytest.fixture
    def sample_field_conditions(self):
        """Sample field conditions for testing."""
        return FieldConditions(
            field_id="test_field",
            field_size_acres=100.0,
            soil_type="clay_loam",
            slope_percent=2.0,
            drainage_class="well_drained",
            organic_matter_percent=3.5,
            ph_level=6.2,
            cec=15.0
        )
    
    @pytest.fixture
    def sample_crop_requirements(self):
        """Sample crop requirements for testing."""
        return CropRequirements(
            crop_type="corn",
            growth_stage="V6",
            target_yield_bu_per_acre=180.0,
            nutrient_requirements={
                "nitrogen": 200.0,
                "phosphorus": 50.0,
                "potassium": 100.0
            },
            application_timing="spring",
            weather_sensitivity="moderate"
        )
    
    @pytest.fixture
    def sample_fertilizer_specification(self):
        """Sample fertilizer specification for testing."""
        return FertilizerSpecification(
            fertilizer_type="NPK",
            npk_ratio="20-10-10",
            cost_per_unit=500.0,
            unit="ton",
            application_rate_lbs_per_acre=200.0,
            availability="high",
            environmental_impact="medium"
        )
    
    @pytest.fixture
    def sample_equipment(self):
        """Sample equipment for testing."""
        return [
            EquipmentSpecification(
                equipment_id="spreader",
                equipment_type="broadcast_spreader",
                capacity_tons=5.0,
                efficiency_score=0.8,
                cost_per_hour=25.0,
                maintenance_cost_per_hour=5.0,
                fuel_consumption_gph=2.0
            ),
            EquipmentSpecification(
                equipment_id="sprayer",
                equipment_type="liquid_sprayer",
                capacity_gallons=1000.0,
                efficiency_score=0.85,
                cost_per_hour=30.0,
                maintenance_cost_per_hour=6.0,
                fuel_consumption_gph=2.5
            )
        ]
    
    @pytest.fixture
    def sample_scenarios(self):
        """Sample scenarios for testing."""
        return [
            ScenarioParameters(
                scenario_type=ScenarioType.PRICE_SCENARIO,
                parameters={
                    "fertilizer_price_variation": 1.1,
                    "fuel_price_variation": 1.05,
                    "labor_price_variation": 1.02,
                    "crop_price_variation": 0.95
                },
                probability=0.3,
                description="Price increase scenario"
            ),
            ScenarioParameters(
                scenario_type=ScenarioType.WEATHER_SCENARIO,
                parameters={
                    "drought_probability": 0.2,
                    "excessive_rain_probability": 0.1,
                    "optimal_weather_probability": 0.7,
                    "weather_impact_on_yield": 0.15
                },
                probability=0.4,
                description="Favorable weather scenario"
            )
        ]


class TestOptimizationAlgorithms(TestEconomicOptimizationService):
    """Test optimization algorithms."""
    
    @pytest.mark.asyncio
    async def test_linear_programming_optimization(self, service, sample_application_methods, 
                                                 sample_field_conditions, sample_crop_requirements,
                                                 sample_fertilizer_specification, sample_equipment):
        """Test linear programming optimization."""
        with patch.object(service.cost_service, 'analyze_application_costs') as mock_cost:
            mock_cost.return_value = {
                "method_costs": [
                    {"total_cost_per_acre": 50.0, "estimated_revenue_per_acre": 100.0},
                    {"total_cost_per_acre": 75.0, "estimated_revenue_per_acre": 120.0},
                    {"total_cost_per_acre": 60.0, "estimated_revenue_per_acre": 110.0}
                ]
            }
            
            result = await service.optimize_application_methods(
                application_methods=sample_application_methods,
                field_conditions=sample_field_conditions,
                crop_requirements=sample_crop_requirements,
                fertilizer_specification=sample_fertilizer_specification,
                available_equipment=sample_equipment,
                objective=OptimizationObjective.MINIMIZE_COST,
                algorithm=OptimizationAlgorithm.LINEAR_PROGRAMMING
            )
            
            assert isinstance(result, OptimizationResult)
            assert result.algorithm_used == "linear_programming"
            assert result.optimization_time_ms > 0
            assert len(result.optimal_methods) > 0
    
    @pytest.mark.asyncio
    async def test_dynamic_programming_optimization(self, service, sample_application_methods,
                                                  sample_field_conditions, sample_crop_requirements,
                                                  sample_fertilizer_specification, sample_equipment):
        """Test dynamic programming optimization."""
        with patch.object(service.cost_service, 'analyze_application_costs') as mock_cost:
            mock_cost.return_value = {
                "method_costs": [
                    {"total_cost_per_acre": 50.0, "estimated_revenue_per_acre": 100.0},
                    {"total_cost_per_acre": 75.0, "estimated_revenue_per_acre": 120.0},
                    {"total_cost_per_acre": 60.0, "estimated_revenue_per_acre": 110.0}
                ]
            }
            
            result = await service.optimize_application_methods(
                application_methods=sample_application_methods,
                field_conditions=sample_field_conditions,
                crop_requirements=sample_crop_requirements,
                fertilizer_specification=sample_fertilizer_specification,
                available_equipment=sample_equipment,
                objective=OptimizationObjective.MAXIMIZE_PROFIT,
                algorithm=OptimizationAlgorithm.DYNAMIC_PROGRAMMING
            )
            
            assert isinstance(result, OptimizationResult)
            assert result.algorithm_used == "dynamic_programming"
            assert result.optimization_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_stochastic_optimization(self, service, sample_application_methods,
                                         sample_field_conditions, sample_crop_requirements,
                                         sample_fertilizer_specification, sample_equipment):
        """Test stochastic optimization."""
        with patch.object(service.cost_service, 'analyze_application_costs') as mock_cost:
            mock_cost.return_value = {
                "method_costs": [
                    {"total_cost_per_acre": 50.0, "estimated_revenue_per_acre": 100.0},
                    {"total_cost_per_acre": 75.0, "estimated_revenue_per_acre": 120.0},
                    {"total_cost_per_acre": 60.0, "estimated_revenue_per_acre": 110.0}
                ]
            }
            
            result = await service.optimize_application_methods(
                application_methods=sample_application_methods,
                field_conditions=sample_field_conditions,
                crop_requirements=sample_crop_requirements,
                fertilizer_specification=sample_fertilizer_specification,
                available_equipment=sample_equipment,
                objective=OptimizationObjective.MINIMIZE_RISK,
                algorithm=OptimizationAlgorithm.STOCHASTIC_OPTIMIZATION
            )
            
            assert isinstance(result, OptimizationResult)
            assert result.algorithm_used == "stochastic_optimization"
            assert result.optimization_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_genetic_algorithm_optimization(self, service, sample_application_methods,
                                               sample_field_conditions, sample_crop_requirements,
                                               sample_fertilizer_specification, sample_equipment):
        """Test genetic algorithm optimization."""
        with patch.object(service.cost_service, 'analyze_application_costs') as mock_cost:
            mock_cost.return_value = {
                "method_costs": [
                    {"total_cost_per_acre": 50.0, "estimated_revenue_per_acre": 100.0},
                    {"total_cost_per_acre": 75.0, "estimated_revenue_per_acre": 120.0},
                    {"total_cost_per_acre": 60.0, "estimated_revenue_per_acre": 110.0}
                ]
            }
            
            result = await service.optimize_application_methods(
                application_methods=sample_application_methods,
                field_conditions=sample_field_conditions,
                crop_requirements=sample_crop_requirements,
                fertilizer_specification=sample_fertilizer_specification,
                available_equipment=sample_equipment,
                objective=OptimizationObjective.MAXIMIZE_EFFICIENCY,
                algorithm=OptimizationAlgorithm.GENETIC_ALGORITHM
            )
            
            assert isinstance(result, OptimizationResult)
            assert result.algorithm_used == "genetic_algorithm"
            assert result.optimization_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_simulated_annealing_optimization(self, service, sample_application_methods,
                                                  sample_field_conditions, sample_crop_requirements,
                                                  sample_fertilizer_specification, sample_equipment):
        """Test simulated annealing optimization."""
        with patch.object(service.cost_service, 'analyze_application_costs') as mock_cost:
            mock_cost.return_value = {
                "method_costs": [
                    {"total_cost_per_acre": 50.0, "estimated_revenue_per_acre": 100.0},
                    {"total_cost_per_acre": 75.0, "estimated_revenue_per_acre": 120.0},
                    {"total_cost_per_acre": 60.0, "estimated_revenue_per_acre": 110.0}
                ]
            }
            
            result = await service.optimize_application_methods(
                application_methods=sample_application_methods,
                field_conditions=sample_field_conditions,
                crop_requirements=sample_crop_requirements,
                fertilizer_specification=sample_fertilizer_specification,
                available_equipment=sample_equipment,
                objective=OptimizationObjective.BALANCED_OPTIMIZATION,
                algorithm=OptimizationAlgorithm.SIMULATED_ANNEALING
            )
            
            assert isinstance(result, OptimizationResult)
            assert result.algorithm_used == "simulated_annealing"
            assert result.optimization_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_particle_swarm_optimization(self, service, sample_application_methods,
                                             sample_field_conditions, sample_crop_requirements,
                                             sample_fertilizer_specification, sample_equipment):
        """Test particle swarm optimization."""
        with patch.object(service.cost_service, 'analyze_application_costs') as mock_cost:
            mock_cost.return_value = {
                "method_costs": [
                    {"total_cost_per_acre": 50.0, "estimated_revenue_per_acre": 100.0},
                    {"total_cost_per_acre": 75.0, "estimated_revenue_per_acre": 120.0},
                    {"total_cost_per_acre": 60.0, "estimated_revenue_per_acre": 110.0}
                ]
            }
            
            result = await service.optimize_application_methods(
                application_methods=sample_application_methods,
                field_conditions=sample_field_conditions,
                crop_requirements=sample_crop_requirements,
                fertilizer_specification=sample_fertilizer_specification,
                available_equipment=sample_equipment,
                objective=OptimizationObjective.MAXIMIZE_ROI,
                algorithm=OptimizationAlgorithm.PARTICLE_SWARM
            )
            
            assert isinstance(result, OptimizationResult)
            assert result.algorithm_used == "particle_swarm"
            assert result.optimization_time_ms > 0


class TestScenarioModeling(TestEconomicOptimizationService):
    """Test scenario modeling functionality."""
    
    @pytest.mark.asyncio
    async def test_price_scenario_generation(self, service):
        """Test price scenario generation."""
        scenarios = await service._generate_scenarios_for_type(
            ScenarioType.PRICE_SCENARIO, 5
        )
        
        assert len(scenarios) == 5
        for scenario in scenarios:
            assert scenario.scenario_type == ScenarioType.PRICE_SCENARIO
            assert "fertilizer_price_variation" in scenario.parameters
            assert "fuel_price_variation" in scenario.parameters
            assert "labor_price_variation" in scenario.parameters
            assert "crop_price_variation" in scenario.parameters
    
    @pytest.mark.asyncio
    async def test_weather_scenario_generation(self, service):
        """Test weather scenario generation."""
        scenarios = await service._generate_scenarios_for_type(
            ScenarioType.WEATHER_SCENARIO, 3
        )
        
        assert len(scenarios) == 3
        for scenario in scenarios:
            assert scenario.scenario_type == ScenarioType.WEATHER_SCENARIO
            assert "drought_probability" in scenario.parameters
            assert "excessive_rain_probability" in scenario.parameters
            assert "optimal_weather_probability" in scenario.parameters
            assert "weather_impact_on_yield" in scenario.parameters
    
    @pytest.mark.asyncio
    async def test_yield_scenario_generation(self, service):
        """Test yield scenario generation."""
        scenarios = await service._generate_scenarios_for_type(
            ScenarioType.YIELD_SCENARIO, 4
        )
        
        assert len(scenarios) == 4
        for scenario in scenarios:
            assert scenario.scenario_type == ScenarioType.YIELD_SCENARIO
            assert "low_yield_probability" in scenario.parameters
            assert "average_yield_probability" in scenario.parameters
            assert "high_yield_probability" in scenario.parameters
            assert "yield_variation_factor" in scenario.parameters
    
    @pytest.mark.asyncio
    async def test_scenario_summarization(self, service):
        """Test scenario result summarization."""
        mock_optimizations = [
            {
                "optimization_result": {
                    "objective_value": 100.0,
                    "optimal_methods": [{"method": {"method_id": "method1"}}]
                }
            },
            {
                "optimization_result": {
                    "objective_value": 120.0,
                    "optimal_methods": [{"method": {"method_id": "method2"}}]
                }
            },
            {
                "optimization_result": {
                    "objective_value": 110.0,
                    "optimal_methods": [{"method": {"method_id": "method1"}}]
                }
            }
        ]
        
        summary = await service._summarize_scenario_results(mock_optimizations)
        
        assert summary["scenario_count"] == 3
        assert summary["objective_value_stats"]["min"] == 100.0
        assert summary["objective_value_stats"]["max"] == 120.0
        assert summary["objective_value_stats"]["mean"] == 110.0
        assert "method_selection_frequency" in summary
        assert "risk_assessment" in summary
    
    @pytest.mark.asyncio
    async def test_monte_carlo_analysis(self, service, sample_application_methods,
                                      sample_field_conditions, sample_crop_requirements,
                                      sample_fertilizer_specification, sample_equipment):
        """Test Monte Carlo analysis."""
        optimization_request = {
            "application_methods": sample_application_methods,
            "field_conditions": sample_field_conditions,
            "crop_requirements": sample_crop_requirements,
            "fertilizer_specification": sample_fertilizer_specification,
            "available_equipment": sample_equipment,
            "objective": OptimizationObjective.MINIMIZE_COST,
            "algorithm": OptimizationAlgorithm.LINEAR_PROGRAMMING,
            "constraints": None,
            "scenarios": None
        }
        
        with patch.object(service, 'optimize_application_methods') as mock_optimize:
            mock_optimize.return_value = OptimizationResult(
                optimal_methods=[],
                objective_value=100.0,
                constraint_violations=[],
                optimization_time_ms=10.0,
                algorithm_used="linear_programming",
                convergence_info={},
                sensitivity_analysis={}
            )
            
            monte_carlo_results = await service._perform_monte_carlo_analysis(
                optimization_request, 100
            )
            
            assert "iterations_completed" in monte_carlo_results
            assert "objective_value_stats" in monte_carlo_results
            assert "risk_metrics" in monte_carlo_results
            assert monte_carlo_results["iterations_completed"] > 0


class TestSensitivityAnalysis(TestEconomicOptimizationService):
    """Test sensitivity analysis functionality."""
    
    @pytest.mark.asyncio
    async def test_parameter_sensitivity_analysis(self, service, sample_application_methods,
                                                sample_field_conditions, sample_crop_requirements,
                                                sample_fertilizer_specification, sample_equipment):
        """Test parameter sensitivity analysis."""
        optimization_request = {
            "application_methods": sample_application_methods,
            "field_conditions": sample_field_conditions,
            "crop_requirements": sample_crop_requirements,
            "fertilizer_specification": sample_fertilizer_specification,
            "available_equipment": sample_equipment,
            "objective": OptimizationObjective.MINIMIZE_COST,
            "algorithm": OptimizationAlgorithm.LINEAR_PROGRAMMING,
            "constraints": None,
            "scenarios": None
        }
        
        base_result = OptimizationResult(
            optimal_methods=[],
            objective_value=100.0,
            constraint_violations=[],
            optimization_time_ms=10.0,
            algorithm_used="linear_programming",
            convergence_info={},
            sensitivity_analysis={}
        )
        
        param_range = {"min": 0.8, "max": 1.2}
        
        with patch.object(service, 'optimize_application_methods') as mock_optimize:
            mock_optimize.return_value = OptimizationResult(
                optimal_methods=[],
                objective_value=110.0,
                constraint_violations=[],
                optimization_time_ms=10.0,
                algorithm_used="linear_programming",
                convergence_info={},
                sensitivity_analysis={}
            )
            
            sensitivity_result = await service._analyze_parameter_sensitivity(
                optimization_request, "test_param", param_range, base_result
            )
            
            assert "parameter_name" in sensitivity_result
            assert "parameter_range" in sensitivity_result
            assert "sensitivity_results" in sensitivity_result
            assert "sensitivity_metrics" in sensitivity_result
    
    @pytest.mark.asyncio
    async def test_risk_assessment(self, service):
        """Test risk assessment functionality."""
        sensitivity_results = {
            "param1": {
                "sensitivity_metrics": {
                    "max_change_percent": 15.0,
                    "sensitivity_coefficient": 0.1
                }
            },
            "param2": {
                "sensitivity_metrics": {
                    "max_change_percent": 25.0,
                    "sensitivity_coefficient": 0.2
                }
            },
            "param3": {
                "sensitivity_metrics": {
                    "max_change_percent": 5.0,
                    "sensitivity_coefficient": 0.05
                }
            }
        }
        
        base_result = OptimizationResult(
            optimal_methods=[],
            objective_value=100.0,
            constraint_violations=[],
            optimization_time_ms=10.0,
            algorithm_used="linear_programming",
            convergence_info={},
            sensitivity_analysis={}
        )
        
        risk_assessment = await service._perform_risk_assessment(sensitivity_results, base_result)
        
        assert "overall_risk_level" in risk_assessment
        assert "risk_factors" in risk_assessment
        assert "risk_summary" in risk_assessment
        assert "risk_mitigation" in risk_assessment
        assert len(risk_assessment["risk_factors"]) == 3


class TestInvestmentPlanning(TestEconomicOptimizationService):
    """Test investment planning functionality."""
    
    @pytest.mark.asyncio
    async def test_investment_analysis(self, service):
        """Test investment analysis."""
        base_result = OptimizationResult(
            optimal_methods=[
                {
                    "method": {"method_id": "method1"},
                    "cost": {"total_cost_per_acre": 50.0}
                },
                {
                    "method": {"method_id": "method2"},
                    "cost": {"total_cost_per_acre": 75.0}
                }
            ],
            objective_value=100.0,
            constraint_violations=[],
            optimization_time_ms=10.0,
            algorithm_used="linear_programming",
            convergence_info={},
            sensitivity_analysis={}
        )
        
        investment_analysis = await service._perform_investment_analysis(
            base_result, 5, 0.08, True, True
        )
        
        assert "investment_horizon_years" in investment_analysis
        assert "discount_rate" in investment_analysis
        assert "investment_components" in investment_analysis
        assert "financial_metrics" in investment_analysis
        assert len(investment_analysis["investment_components"]) == 2
    
    @pytest.mark.asyncio
    async def test_financial_projections(self, service):
        """Test financial projections."""
        investment_analysis = {
            "investment_horizon_years": 5,
            "discount_rate": 0.08,
            "investment_components": {
                "method1": {
                    "cost_per_acre": 50.0,
                    "npv": -200.0,
                    "annual_cash_flow": -50.0
                },
                "method2": {
                    "cost_per_acre": 75.0,
                    "npv": -300.0,
                    "annual_cash_flow": -75.0
                }
            }
        }
        
        projections = await service._generate_financial_projections(investment_analysis, 5)
        
        assert "yearly_projections" in projections
        assert "cumulative_metrics" in projections
        assert len(projections["yearly_projections"]) == 5
        assert "total_npv" in projections["cumulative_metrics"]
        assert "payback_period_years" in projections["cumulative_metrics"]
        assert "irr_estimate" in projections["cumulative_metrics"]
    
    @pytest.mark.asyncio
    async def test_investment_timing_optimization(self, service):
        """Test investment timing optimization."""
        investment_analysis = {
            "investment_horizon_years": 5,
            "discount_rate": 0.08
        }
        
        financial_projections = {
            "cumulative_metrics": {
                "total_npv": 1000.0,
                "payback_period_years": 2.5,
                "irr_estimate": 0.12
            }
        }
        
        timing_optimization = await service._optimize_investment_timing(
            investment_analysis, financial_projections
        )
        
        assert "optimal_investment_timing" in timing_optimization
        assert "investment_recommendations" in timing_optimization
        assert "risk_assessment" in timing_optimization
        assert "decision_factors" in timing_optimization


class TestConstraintHandling(TestEconomicOptimizationService):
    """Test constraint handling functionality."""
    
    @pytest.mark.asyncio
    async def test_optimization_constraints(self, service, sample_application_methods,
                                          sample_field_conditions, sample_crop_requirements,
                                          sample_fertilizer_specification, sample_equipment):
        """Test optimization with constraints."""
        constraints = [
            OptimizationConstraint(
                constraint_type="selection",
                variable="total_methods",
                operator="<=",
                value=2.0,
                description="Maximum 2 methods can be selected"
            )
        ]
        
        with patch.object(service.cost_service, 'analyze_application_costs') as mock_cost:
            mock_cost.return_value = {
                "method_costs": [
                    {"total_cost_per_acre": 50.0, "estimated_revenue_per_acre": 100.0},
                    {"total_cost_per_acre": 75.0, "estimated_revenue_per_acre": 120.0},
                    {"total_cost_per_acre": 60.0, "estimated_revenue_per_acre": 110.0}
                ]
            }
            
            result = await service.optimize_application_methods(
                application_methods=sample_application_methods,
                field_conditions=sample_field_conditions,
                crop_requirements=sample_crop_requirements,
                fertilizer_specification=sample_fertilizer_specification,
                available_equipment=sample_equipment,
                objective=OptimizationObjective.MINIMIZE_COST,
                algorithm=OptimizationAlgorithm.LINEAR_PROGRAMMING,
                constraints=constraints
            )
            
            assert isinstance(result, OptimizationResult)
            assert len(result.optimal_methods) <= 2


class TestErrorHandling(TestEconomicOptimizationService):
    """Test error handling functionality."""
    
    @pytest.mark.asyncio
    async def test_invalid_algorithm(self, service, sample_application_methods,
                                   sample_field_conditions, sample_crop_requirements,
                                   sample_fertilizer_specification, sample_equipment):
        """Test handling of invalid optimization algorithm."""
        with patch.object(service.cost_service, 'analyze_application_costs') as mock_cost:
            mock_cost.return_value = {
                "method_costs": [
                    {"total_cost_per_acre": 50.0, "estimated_revenue_per_acre": 100.0}
                ]
            }
            
            with pytest.raises(ValueError):
                await service.optimize_application_methods(
                    application_methods=sample_application_methods,
                    field_conditions=sample_field_conditions,
                    crop_requirements=sample_crop_requirements,
                    fertilizer_specification=sample_fertilizer_specification,
                    available_equipment=sample_equipment,
                    objective=OptimizationObjective.MINIMIZE_COST,
                    algorithm="invalid_algorithm"
                )
    
    @pytest.mark.asyncio
    async def test_empty_application_methods(self, service, sample_field_conditions,
                                          sample_crop_requirements, sample_fertilizer_specification,
                                          sample_equipment):
        """Test handling of empty application methods list."""
        with pytest.raises(Exception):
            await service.optimize_application_methods(
                application_methods=[],
                field_conditions=sample_field_conditions,
                crop_requirements=sample_crop_requirements,
                fertilizer_specification=sample_fertilizer_specification,
                available_equipment=sample_equipment,
                objective=OptimizationObjective.MINIMIZE_COST,
                algorithm=OptimizationAlgorithm.LINEAR_PROGRAMMING
            )
    
    @pytest.mark.asyncio
    async def test_cost_service_failure(self, service, sample_application_methods,
                                      sample_field_conditions, sample_crop_requirements,
                                      sample_fertilizer_specification, sample_equipment):
        """Test handling of cost service failure."""
        with patch.object(service.cost_service, 'analyze_application_costs') as mock_cost:
            mock_cost.side_effect = Exception("Cost service failure")
            
            with pytest.raises(Exception):
                await service.optimize_application_methods(
                    application_methods=sample_application_methods,
                    field_conditions=sample_field_conditions,
                    crop_requirements=sample_crop_requirements,
                    fertilizer_specification=sample_fertilizer_specification,
                    available_equipment=sample_equipment,
                    objective=OptimizationObjective.MINIMIZE_COST,
                    algorithm=OptimizationAlgorithm.LINEAR_PROGRAMMING
                )


class TestPerformanceRequirements(TestEconomicOptimizationService):
    """Test performance requirements."""
    
    @pytest.mark.asyncio
    async def test_optimization_performance(self, service, sample_application_methods,
                                          sample_field_conditions, sample_crop_requirements,
                                          sample_fertilizer_specification, sample_equipment):
        """Test that optimization completes within performance requirements."""
        with patch.object(service.cost_service, 'analyze_application_costs') as mock_cost:
            mock_cost.return_value = {
                "method_costs": [
                    {"total_cost_per_acre": 50.0, "estimated_revenue_per_acre": 100.0},
                    {"total_cost_per_acre": 75.0, "estimated_revenue_per_acre": 120.0},
                    {"total_cost_per_acre": 60.0, "estimated_revenue_per_acre": 110.0}
                ]
            }
            
            result = await service.optimize_application_methods(
                application_methods=sample_application_methods,
                field_conditions=sample_field_conditions,
                crop_requirements=sample_crop_requirements,
                fertilizer_specification=sample_fertilizer_specification,
                available_equipment=sample_equipment,
                objective=OptimizationObjective.MINIMIZE_COST,
                algorithm=OptimizationAlgorithm.LINEAR_PROGRAMMING
            )
            
            # Performance requirement: optimization should complete within 5 seconds
            assert result.optimization_time_ms < 5000
    
    @pytest.mark.asyncio
    async def test_scenario_analysis_performance(self, service):
        """Test scenario analysis performance."""
        scenarios = await service._generate_scenarios_for_type(
            ScenarioType.PRICE_SCENARIO, 10
        )
        
        # Performance requirement: scenario generation should be fast
        assert len(scenarios) == 10
        
        # Test that scenario generation completes quickly
        import time
        start_time = time.time()
        await service._generate_scenarios_for_type(ScenarioType.PRICE_SCENARIO, 100)
        elapsed_time = time.time() - start_time
        
        # Should complete within 1 second for 100 scenarios
        assert elapsed_time < 1.0


class TestAgriculturalValidation(TestEconomicOptimizationService):
    """Test agricultural validation and domain-specific logic."""
    
    @pytest.mark.asyncio
    async def test_agricultural_scenario_validation(self, service):
        """Test that scenarios are agriculturally valid."""
        scenarios = await service._generate_scenarios_for_type(
            ScenarioType.WEATHER_SCENARIO, 5
        )
        
        for scenario in scenarios:
            params = scenario.parameters
            
            # Agricultural validation: probabilities should sum to reasonable values
            drought_prob = params["drought_probability"]
            rain_prob = params["excessive_rain_probability"]
            optimal_prob = params["optimal_weather_probability"]
            
            assert 0 <= drought_prob <= 1
            assert 0 <= rain_prob <= 1
            assert 0 <= optimal_prob <= 1
            
            # Total probability should be reasonable (not necessarily 1.0 as these are independent events)
            total_prob = drought_prob + rain_prob + optimal_prob
            assert 0.5 <= total_prob <= 2.0  # Reasonable range for agricultural scenarios
    
    @pytest.mark.asyncio
    async def test_cost_optimization_agricultural_validity(self, service, sample_application_methods,
                                                         sample_field_conditions, sample_crop_requirements,
                                                         sample_fertilizer_specification, sample_equipment):
        """Test that cost optimization produces agriculturally valid results."""
        with patch.object(service.cost_service, 'analyze_application_costs') as mock_cost:
            mock_cost.return_value = {
                "method_costs": [
                    {"total_cost_per_acre": 50.0, "estimated_revenue_per_acre": 100.0, "efficiency_score": 0.8},
                    {"total_cost_per_acre": 75.0, "estimated_revenue_per_acre": 120.0, "efficiency_score": 0.9},
                    {"total_cost_per_acre": 60.0, "estimated_revenue_per_acre": 110.0, "efficiency_score": 0.85}
                ]
            }
            
            result = await service.optimize_application_methods(
                application_methods=sample_application_methods,
                field_conditions=sample_field_conditions,
                crop_requirements=sample_crop_requirements,
                fertilizer_specification=sample_fertilizer_specification,
                available_equipment=sample_equipment,
                objective=OptimizationObjective.MINIMIZE_COST,
                algorithm=OptimizationAlgorithm.LINEAR_PROGRAMMING
            )
            
            # Agricultural validation: should select at least one method
            assert len(result.optimal_methods) > 0
            
            # Agricultural validation: objective value should be positive and reasonable
            assert result.objective_value > 0
            assert result.objective_value < 1000  # Reasonable upper bound for cost per acre
    
    @pytest.mark.asyncio
    async def test_yield_scenario_agricultural_validity(self, service):
        """Test that yield scenarios are agriculturally valid."""
        scenarios = await service._generate_scenarios_for_type(
            ScenarioType.YIELD_SCENARIO, 5
        )
        
        for scenario in scenarios:
            params = scenario.parameters
            
            # Agricultural validation: yield probabilities should be reasonable
            low_yield_prob = params["low_yield_probability"]
            avg_yield_prob = params["average_yield_probability"]
            high_yield_prob = params["high_yield_probability"]
            
            assert 0 <= low_yield_prob <= 1
            assert 0 <= avg_yield_prob <= 1
            assert 0 <= high_yield_prob <= 1
            
            # Agricultural validation: average yield should be most likely
            assert avg_yield_prob >= low_yield_prob
            assert avg_yield_prob >= high_yield_prob
            
            # Agricultural validation: yield variation factor should be reasonable
            yield_variation = params["yield_variation_factor"]
            assert 0.1 <= yield_variation <= 0.5  # 10-50% variation is agriculturally reasonable


if __name__ == "__main__":
    pytest.main([__file__, "-v"])