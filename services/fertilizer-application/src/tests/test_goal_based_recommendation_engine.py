"""
Comprehensive tests for the Goal-Based Recommendation Engine.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import List, Dict, Any

from ..services.goal_based_recommendation_engine import (
    GoalBasedRecommendationEngine, OptimizationGoal, OptimizationConstraint,
    ConstraintType, GoalWeight, OptimizationResult
)
from ..models.application_models import (
    ApplicationRequest, ApplicationResponse, ApplicationMethod,
    FieldConditions, CropRequirements, FertilizerSpecification,
    ApplicationMethodType, FertilizerForm, EquipmentType, EquipmentSpecification
)


class TestGoalBasedRecommendationEngine:
    """Test suite for the Goal-Based Recommendation Engine."""
    
    @pytest.fixture
    def engine(self):
        """Create a goal-based recommendation engine instance."""
        return GoalBasedRecommendationEngine()
    
    @pytest.fixture
    def sample_request(self):
        """Create a sample application request."""
        return ApplicationRequest(
            field_conditions=FieldConditions(
                field_size_acres=100.0,
                soil_type="loam",
                drainage_class="well_drained",
                slope_percent=2.0,
                irrigation_available=True,
                access_roads=["main_road", "field_road"]
            ),
            crop_requirements=CropRequirements(
                crop_type="corn",
                growth_stage="vegetative",
                target_yield=180.0,
                nutrient_requirements={"nitrogen": 150, "phosphorus": 50, "potassium": 100},
                application_timing_preferences=["early_season", "mid_season"]
            ),
            fertilizer_specification=FertilizerSpecification(
                fertilizer_type="npk",
                form=FertilizerForm.GRANULAR,
                solubility="medium",
                release_rate="medium",
                cost_per_unit=0.5,
                unit="lbs"
            ),
            available_equipment=[
                EquipmentSpecification(
                    equipment_type=EquipmentType.SPREADER,
                    capacity=500,
                    age_years=5,
                    maintenance_status="good"
                ),
                EquipmentSpecification(
                    equipment_type=EquipmentType.BROADCASTER,
                    capacity=1000,
                    age_years=3,
                    maintenance_status="excellent"
                )
            ]
        )
    
    @pytest.fixture
    def sample_methods(self):
        """Create sample application methods."""
        return [
            ApplicationMethod(
                method_id="broadcast_1",
                method_type=ApplicationMethodType.BROADCAST,
                recommended_equipment=EquipmentSpecification(
                    equipment_type=EquipmentType.SPREADER,
                    capacity=500
                ),
                application_rate=150.0,
                rate_unit="lbs/acre",
                application_timing="At planting",
                efficiency_score=0.7,
                cost_per_acre=15.0,
                labor_requirements="medium",
                environmental_impact="moderate",
                pros=["Simple application", "Good for large fields"],
                cons=["Lower efficiency", "Potential runoff"]
            ),
            ApplicationMethod(
                method_id="band_1",
                method_type=ApplicationMethodType.BAND,
                recommended_equipment=EquipmentSpecification(
                    equipment_type=EquipmentType.SPREADER,
                    capacity=500
                ),
                application_rate=120.0,
                rate_unit="lbs/acre",
                application_timing="At planting",
                efficiency_score=0.8,
                cost_per_acre=20.0,
                labor_requirements="medium",
                environmental_impact="low",
                pros=["Higher efficiency", "Reduced fertilizer needs"],
                cons=["More complex setup", "Requires precise equipment"]
            ),
            ApplicationMethod(
                method_id="foliar_1",
                method_type=ApplicationMethodType.FOLIAR,
                recommended_equipment=EquipmentSpecification(
                    equipment_type=EquipmentType.SPRAYER,
                    capacity=200
                ),
                application_rate=45.0,
                rate_unit="lbs/acre",
                application_timing="Mid-season",
                efficiency_score=0.9,
                cost_per_acre=30.0,
                labor_requirements="high",
                environmental_impact="low",
                pros=["Very high efficiency", "Quick response"],
                cons=["Limited amounts", "Weather sensitive"]
            )
        ]
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Test that the engine initializes correctly."""
        assert engine is not None
        assert engine.application_service is not None
        assert len(engine.goal_weights) == 5
        assert len(engine.constraint_handlers) == 6
        assert len(engine.optimization_algorithms) == 4
        
        # Check default goal weights sum to 1.0
        total_weight = sum(weight.weight for weight in engine.goal_weights.values())
        assert abs(total_weight - 1.0) < 0.001
    
    @pytest.mark.asyncio
    async def test_pareto_optimization(self, engine, sample_methods):
        """Test Pareto optimization algorithm."""
        # Create objective matrix
        objective_matrix = await engine._calculate_objective_matrix(sample_methods, None)
        
        # Run Pareto optimization
        result = await engine._pareto_optimization(sample_methods, objective_matrix, [])
        
        assert isinstance(result, OptimizationResult)
        assert len(result.method_scores) > 0
        assert len(result.pareto_front) > 0
        assert result.convergence_info["algorithm"] == "pareto_optimization"
        
        # Check that Pareto front contains non-dominated solutions
        for solution in result.pareto_front:
            assert "method_id" in solution
            assert "objectives" in solution
            assert "crowding_distance" in solution
    
    @pytest.mark.asyncio
    async def test_weighted_sum_optimization(self, engine, sample_methods):
        """Test weighted sum optimization algorithm."""
        # Create objective matrix
        objective_matrix = await engine._calculate_objective_matrix(sample_methods, None)
        
        # Run weighted sum optimization
        result = await engine._weighted_sum_optimization(sample_methods, objective_matrix, [])
        
        assert isinstance(result, OptimizationResult)
        assert len(result.method_scores) > 0
        assert result.convergence_info["algorithm"] == "weighted_sum"
        
        # Check that scores are normalized
        scores = list(result.method_scores.values())
        assert all(0 <= score <= 1 for score in scores)
    
    @pytest.mark.asyncio
    async def test_constraint_satisfaction_optimization(self, engine, sample_methods):
        """Test constraint satisfaction optimization."""
        # Create objective matrix
        objective_matrix = await engine._calculate_objective_matrix(sample_methods, None)
        
        # Create constraints
        constraints = [
            OptimizationConstraint(
                constraint_type=ConstraintType.BUDGET_LIMIT,
                constraint_value=25.0,
                operator="le"
            )
        ]
        
        # Run constraint satisfaction optimization
        result = await engine._constraint_satisfaction_optimization(sample_methods, objective_matrix, constraints)
        
        assert isinstance(result, OptimizationResult)
        assert result.convergence_info["algorithm"] == "constraint_satisfaction"
        
        # Check that feasible solutions are found
        assert result.convergence_info["feasible_solutions"] > 0
    
    @pytest.mark.asyncio
    async def test_objective_calculation(self, engine, sample_methods, sample_request):
        """Test objective function calculations."""
        objective_matrix = await engine._calculate_objective_matrix(sample_methods, sample_request)
        
        assert objective_matrix.shape[0] == len(sample_methods)
        assert objective_matrix.shape[1] == 5  # Five objectives
        
        # Check that objectives are reasonable
        for i, method in enumerate(sample_methods):
            objectives = objective_matrix[i]
            
            # Yield objective should be positive
            assert objectives[0] > 0
            
            # Cost objective should be negative (for minimization)
            assert objectives[1] < 0
            
            # Environmental objective should be positive
            assert objectives[2] > 0
            
            # Labor objective should be positive
            assert objectives[3] > 0
            
            # Nutrient objective should be positive
            assert objectives[4] > 0
    
    @pytest.mark.asyncio
    async def test_yield_objective_calculation(self, engine, sample_methods, sample_request):
        """Test yield maximization objective calculation."""
        method = sample_methods[0]  # Broadcast method
        
        yield_score = await engine._calculate_yield_objective(method, sample_request)
        
        assert isinstance(yield_score, float)
        assert 0 <= yield_score <= 2.0  # Reasonable range
        
        # Test with different crop types
        sample_request.crop_requirements.crop_type = "soybean"
        yield_score_soybean = await engine._calculate_yield_objective(method, sample_request)
        
        assert yield_score_soybean != yield_score  # Should be different for different crops
    
    @pytest.mark.asyncio
    async def test_cost_objective_calculation(self, engine, sample_methods, sample_request):
        """Test cost minimization objective calculation."""
        method = sample_methods[0]  # Broadcast method
        
        cost_score = await engine._calculate_cost_objective(method, sample_request)
        
        assert isinstance(cost_score, float)
        assert cost_score > 0  # Cost should be positive
        
        # Test with different field sizes
        sample_request.field_conditions.field_size_acres = 500.0  # Large field
        cost_score_large = await engine._calculate_cost_objective(method, sample_request)
        
        assert cost_score_large < cost_score  # Large fields should have lower cost per acre
    
    @pytest.mark.asyncio
    async def test_environmental_objective_calculation(self, engine, sample_methods, sample_request):
        """Test environmental protection objective calculation."""
        method = sample_methods[0]  # Broadcast method
        
        env_score = await engine._calculate_environmental_objective(method, sample_request)
        
        assert isinstance(env_score, float)
        assert 0 <= env_score <= 1.0
        
        # Test with different environmental impacts
        method.environmental_impact = "very_low"
        env_score_low = await engine._calculate_environmental_objective(method, sample_request)
        
        method.environmental_impact = "high"
        env_score_high = await engine._calculate_environmental_objective(method, sample_request)
        
        assert env_score_low > env_score_high  # Lower impact should score higher
    
    @pytest.mark.asyncio
    async def test_labor_objective_calculation(self, engine, sample_methods, sample_request):
        """Test labor efficiency objective calculation."""
        method = sample_methods[0]  # Broadcast method
        
        labor_score = await engine._calculate_labor_objective(method, sample_request)
        
        assert isinstance(labor_score, float)
        assert 0 <= labor_score <= 1.5  # Reasonable range
        
        # Test with different labor requirements
        method.labor_requirements = "low"
        labor_score_low = await engine._calculate_labor_objective(method, sample_request)
        
        method.labor_requirements = "high"
        labor_score_high = await engine._calculate_labor_objective(method, sample_request)
        
        assert labor_score_low > labor_score_high  # Lower labor should score higher
    
    @pytest.mark.asyncio
    async def test_nutrient_objective_calculation(self, engine, sample_methods, sample_request):
        """Test nutrient efficiency objective calculation."""
        method = sample_methods[0]  # Broadcast method
        
        nutrient_score = await engine._calculate_nutrient_objective(method, sample_request)
        
        assert isinstance(nutrient_score, float)
        assert nutrient_score > 0
        
        # Test with different fertilizer forms
        sample_request.fertilizer_specification.form = FertilizerForm.LIQUID
        nutrient_score_liquid = await engine._calculate_nutrient_objective(method, sample_request)
        
        sample_request.fertilizer_specification.form = FertilizerForm.ORGANIC
        nutrient_score_organic = await engine._calculate_nutrient_objective(method, sample_request)
        
        assert nutrient_score_liquid != nutrient_score_organic  # Should be different
    
    @pytest.mark.asyncio
    async def test_goal_weight_update(self, engine):
        """Test updating goal weights."""
        # Test with custom farmer goals
        farmer_goals = {
            OptimizationGoal.YIELD_MAXIMIZATION: 0.5,
            OptimizationGoal.COST_MINIMIZATION: 0.3,
            OptimizationGoal.ENVIRONMENTAL_PROTECTION: 0.2,
            OptimizationGoal.LABOR_EFFICIENCY: 0.0,
            OptimizationGoal.NUTRIENT_EFFICIENCY: 0.0
        }
        
        engine._update_goal_weights(farmer_goals)
        
        # Check that weights are updated
        assert engine.goal_weights[OptimizationGoal.YIELD_MAXIMIZATION].weight == 0.5
        assert engine.goal_weights[OptimizationGoal.COST_MINIMIZATION].weight == 0.3
        assert engine.goal_weights[OptimizationGoal.ENVIRONMENTAL_PROTECTION].weight == 0.2
        assert engine.goal_weights[OptimizationGoal.LABOR_EFFICIENCY].weight == 0.0
        assert engine.goal_weights[OptimizationGoal.NUTRIENT_EFFICIENCY].weight == 0.0
    
    @pytest.mark.asyncio
    async def test_constraint_generation(self, engine, sample_request):
        """Test default constraint generation."""
        constraints = engine._generate_default_constraints(sample_request)
        
        assert len(constraints) > 0
        
        # Check that equipment constraint is generated
        equipment_constraints = [c for c in constraints if c.constraint_type == ConstraintType.EQUIPMENT_AVAILABILITY]
        assert len(equipment_constraints) > 0
        
        # Check that field size constraint is generated
        field_size_constraints = [c for c in constraints if c.constraint_type == ConstraintType.FIELD_SIZE]
        assert len(field_size_constraints) > 0
        
        # Check that budget constraint is generated
        budget_constraints = [c for c in constraints if c.constraint_type == ConstraintType.BUDGET_LIMIT]
        assert len(budget_constraints) > 0
    
    @pytest.mark.asyncio
    async def test_constraint_handling(self, engine, sample_methods):
        """Test constraint handling functions."""
        # Test equipment constraint
        method = sample_methods[0]
        constraint = OptimizationConstraint(
            constraint_type=ConstraintType.EQUIPMENT_AVAILABILITY,
            constraint_value=[EquipmentSpecification(equipment_type=EquipmentType.SPREADER)],
            operator="eq"
        )
        
        violation = await engine._handle_equipment_constraint(method, constraint)
        assert violation is None  # Should not violate
        
        # Test budget constraint
        constraint = OptimizationConstraint(
            constraint_type=ConstraintType.BUDGET_LIMIT,
            constraint_value=10.0,  # Low budget
            operator="le"
        )
        
        violation = await engine._handle_budget_constraint(method, constraint)
        assert violation is not None  # Should violate (method costs $15/acre)
        assert violation["constraint_type"] == ConstraintType.BUDGET_LIMIT
    
    @pytest.mark.asyncio
    async def test_pareto_front_calculation(self, engine):
        """Test Pareto front calculation."""
        # Create test objective matrix
        objective_matrix = [
            [1.0, 0.5, 0.8, 0.6, 0.7],  # Solution 1
            [0.8, 0.7, 0.9, 0.5, 0.8],  # Solution 2 (dominates solution 1)
            [0.9, 0.6, 0.7, 0.7, 0.6],  # Solution 3
            [0.7, 0.8, 0.8, 0.8, 0.9],  # Solution 4
        ]
        objective_matrix = np.array(objective_matrix)
        
        pareto_indices = engine._calculate_pareto_front(objective_matrix)
        
        assert len(pareto_indices) > 0
        assert len(pareto_indices) <= len(objective_matrix)
        
        # Check that returned indices are valid
        for idx in pareto_indices:
            assert 0 <= idx < len(objective_matrix)
    
    @pytest.mark.asyncio
    async def test_crowding_distance_calculation(self, engine):
        """Test crowding distance calculation."""
        # Create test Pareto front
        pareto_front = [
            {"method_id": "method1", "objectives": [1.0, 0.5], "crowding_distance": 0.0},
            {"method_id": "method2", "objectives": [0.8, 0.7], "crowding_distance": 0.0},
            {"method_id": "method3", "objectives": [0.9, 0.6], "crowding_distance": 0.0},
        ]
        
        objective_matrix = np.array([
            [1.0, 0.5],
            [0.8, 0.7],
            [0.9, 0.6]
        ])
        
        result = engine._calculate_crowding_distance(pareto_front, objective_matrix)
        
        assert len(result) == len(pareto_front)
        
        # Check that boundary solutions have infinite distance
        assert result[0]["crowding_distance"] == float('inf')
        assert result[-1]["crowding_distance"] == float('inf')
        
        # Check that intermediate solutions have finite distance
        if len(result) > 2:
            assert result[1]["crowding_distance"] != float('inf')
    
    @pytest.mark.asyncio
    async def test_full_optimization_workflow(self, engine, sample_request):
        """Test the complete optimization workflow."""
        # Mock the application service to return sample methods
        with patch.object(engine.application_service, 'select_application_methods') as mock_service:
            mock_response = ApplicationResponse(
                request_id="test",
                recommended_methods=sample_methods,
                primary_recommendation=sample_methods[0],
                alternative_methods=sample_methods[1:],
                cost_comparison={},
                efficiency_analysis={},
                equipment_compatibility={},
                processing_time_ms=100.0,
                metadata={}
            )
            mock_service.return_value = mock_response
            
            # Set up farmer goals
            farmer_goals = {
                OptimizationGoal.YIELD_MAXIMIZATION: 0.4,
                OptimizationGoal.COST_MINIMIZATION: 0.3,
                OptimizationGoal.ENVIRONMENTAL_PROTECTION: 0.2,
                OptimizationGoal.LABOR_EFFICIENCY: 0.1,
                OptimizationGoal.NUTRIENT_EFFICIENCY: 0.0
            }
            
            # Run optimization
            result = await engine.optimize_application_methods(
                sample_request,
                farmer_goals=farmer_goals,
                optimization_method="pareto_optimization"
            )
            
            assert isinstance(result, OptimizationResult)
            assert len(result.method_scores) > 0
            assert result.optimization_time_ms > 0
            assert result.convergence_info["algorithm"] == "pareto_optimization"
    
    @pytest.mark.asyncio
    async def test_optimization_with_constraints(self, engine, sample_request):
        """Test optimization with constraints."""
        # Mock the application service
        with patch.object(engine.application_service, 'select_application_methods') as mock_service:
            mock_response = ApplicationResponse(
                request_id="test",
                recommended_methods=sample_methods,
                primary_recommendation=sample_methods[0],
                alternative_methods=sample_methods[1:],
                cost_comparison={},
                efficiency_analysis={},
                equipment_compatibility={},
                processing_time_ms=100.0,
                metadata={}
            )
            mock_service.return_value = mock_response
            
            # Set up constraints
            constraints = [
                OptimizationConstraint(
                    constraint_type=ConstraintType.BUDGET_LIMIT,
                    constraint_value=25.0,
                    operator="le"
                )
            ]
            
            # Run optimization
            result = await engine.optimize_application_methods(
                sample_request,
                constraints=constraints,
                optimization_method="constraint_satisfaction"
            )
            
            assert isinstance(result, OptimizationResult)
            assert result.convergence_info["algorithm"] == "constraint_satisfaction"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, engine, sample_request):
        """Test error handling in optimization."""
        # Test with invalid optimization method
        with pytest.raises(ValueError):
            await engine.optimize_application_methods(
                sample_request,
                optimization_method="invalid_method"
            )
        
        # Test with empty method list
        with patch.object(engine.application_service, 'select_application_methods') as mock_service:
            mock_response = ApplicationResponse(
                request_id="test",
                recommended_methods=[],
                primary_recommendation=None,
                alternative_methods=[],
                cost_comparison={},
                efficiency_analysis={},
                equipment_compatibility={},
                processing_time_ms=100.0,
                metadata={}
            )
            mock_service.return_value = mock_response
            
            with pytest.raises(ValueError):
                await engine.optimize_application_methods(sample_request)


class TestAgriculturalValidation:
    """Agricultural validation tests for the goal-based recommendation engine."""
    
    @pytest.mark.asyncio
    async def test_corn_optimization_scenarios(self):
        """Test optimization scenarios specific to corn production."""
        engine = GoalBasedRecommendationEngine()
        
        # High-yield corn scenario
        request = ApplicationRequest(
            field_conditions=FieldConditions(
                field_size_acres=200.0,
                soil_type="loam",
                drainage_class="well_drained",
                slope_percent=1.0,
                irrigation_available=True
            ),
            crop_requirements=CropRequirements(
                crop_type="corn",
                growth_stage="vegetative",
                target_yield=250.0,  # High yield target
                nutrient_requirements={"nitrogen": 200, "phosphorus": 60, "potassium": 120}
            ),
            fertilizer_specification=FertilizerSpecification(
                fertilizer_type="npk",
                form=FertilizerForm.GRANULAR,
                cost_per_unit=0.6
            ),
            available_equipment=[
                EquipmentSpecification(equipment_type=EquipmentType.SPREADER, capacity=1000),
                EquipmentSpecification(equipment_type=EquipmentType.BROADCASTER, capacity=2000)
            ]
        )
        
        # Optimize for yield maximization
        farmer_goals = {
            OptimizationGoal.YIELD_MAXIMIZATION: 0.6,
            OptimizationGoal.COST_MINIMIZATION: 0.2,
            OptimizationGoal.ENVIRONMENTAL_PROTECTION: 0.1,
            OptimizationGoal.LABOR_EFFICIENCY: 0.1,
            OptimizationGoal.NUTRIENT_EFFICIENCY: 0.0
        }
        
        with patch.object(engine.application_service, 'select_application_methods') as mock_service:
            mock_response = ApplicationResponse(
                request_id="test",
                recommended_methods=[],
                primary_recommendation=None,
                alternative_methods=[],
                cost_comparison={},
                efficiency_analysis={},
                equipment_compatibility={},
                processing_time_ms=100.0,
                metadata={}
            )
            mock_service.return_value = mock_response
            
            result = await engine.optimize_application_methods(
                request,
                farmer_goals=farmer_goals,
                optimization_method="weighted_sum"
            )
            
            # Should prioritize yield maximization
            assert result.goal_achievements[OptimizationGoal.YIELD_MAXIMIZATION] > 0.7
    
    @pytest.mark.asyncio
    async def test_environmental_compliance_scenarios(self):
        """Test optimization scenarios with environmental constraints."""
        engine = GoalBasedRecommendationEngine()
        
        # Environmentally sensitive field
        request = ApplicationRequest(
            field_conditions=FieldConditions(
                field_size_acres=50.0,
                soil_type="sandy",
                drainage_class="poorly_drained",
                slope_percent=8.0,  # High slope
                irrigation_available=False
            ),
            crop_requirements=CropRequirements(
                crop_type="corn",
                growth_stage="vegetative",
                target_yield=150.0,
                nutrient_requirements={"nitrogen": 120, "phosphorus": 40, "potassium": 80}
            ),
            fertilizer_specification=FertilizerSpecification(
                fertilizer_type="npk",
                form=FertilizerForm.LIQUID
            ),
            available_equipment=[
                EquipmentSpecification(equipment_type=EquipmentType.INJECTOR, capacity=500)
            ]
        )
        
        # Optimize for environmental protection
        farmer_goals = {
            OptimizationGoal.YIELD_MAXIMIZATION: 0.2,
            OptimizationGoal.COST_MINIMIZATION: 0.2,
            OptimizationGoal.ENVIRONMENTAL_PROTECTION: 0.5,
            OptimizationGoal.LABOR_EFFICIENCY: 0.1,
            OptimizationGoal.NUTRIENT_EFFICIENCY: 0.0
        }
        
        constraints = [
            OptimizationConstraint(
                constraint_type=ConstraintType.ENVIRONMENTAL_REGULATIONS,
                constraint_value="strict",
                operator="eq"
            )
        ]
        
        with patch.object(engine.application_service, 'select_application_methods') as mock_service:
            mock_response = ApplicationResponse(
                request_id="test",
                recommended_methods=[],
                primary_recommendation=None,
                alternative_methods=[],
                cost_comparison={},
                efficiency_analysis={},
                equipment_compatibility={},
                processing_time_ms=100.0,
                metadata={}
            )
            mock_service.return_value = mock_response
            
            result = await engine.optimize_application_methods(
                request,
                farmer_goals=farmer_goals,
                constraints=constraints,
                optimization_method="constraint_satisfaction"
            )
            
            # Should prioritize environmental protection
            assert result.goal_achievements[OptimizationGoal.ENVIRONMENTAL_PROTECTION] > 0.8


if __name__ == "__main__":
    pytest.main([__file__])