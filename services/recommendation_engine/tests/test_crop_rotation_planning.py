"""
Comprehensive Test Suite for Crop Rotation Planning
Tests for field history management, rotation optimization, and analysis.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, date
from typing import List, Dict

from ..src.models.rotation_models import (
    FieldHistoryRecord, FieldProfile, RotationGoal, RotationConstraint,
    CropRotationPlan, RotationGoalType, ConstraintType, FieldHistoryRequest
)
from ..src.services.field_history_service import FieldHistoryService
from ..src.services.rotation_optimization_engine import RotationOptimizationEngine


class TestFieldHistoryService:
    """Test field history management functionality."""
    
    @pytest.fixture
    def field_history_service(self):
        """Create field history service instance."""
        return FieldHistoryService()
    
    @pytest.fixture
    def sample_field_profile(self, field_history_service):
        """Create sample field profile for testing."""
        return asyncio.run(field_history_service.create_field_profile(
            field_id="test_field_001",
            field_name="North Field",
            farm_id="farm_001",
            field_characteristics={
                'size_acres': 160.0,
                'soil_type': 'silt_loam',
                'drainage_class': 'well_drained',
                'slope_percent': 2.5,
                'irrigation_available': True,
                'climate_zone': '5a'
            }
        ))
    
    @pytest.mark.asyncio
    async def test_create_field_profile(self, field_history_service):
        """Test field profile creation."""
        field_profile = await field_history_service.create_field_profile(
            field_id="test_field_002",
            field_name="South Field",
            farm_id="farm_001",
            field_characteristics={
                'size_acres': 80.0,
                'soil_type': 'clay_loam',
                'irrigation_available': False
            }
        )
        
        assert field_profile.field_id == "test_field_002"
        assert field_profile.field_name == "South Field"
        assert field_profile.farm_id == "farm_001"
        assert field_profile.size_acres == 80.0
        assert field_profile.soil_type == "clay_loam"
        assert field_profile.irrigation_available is False
        assert len(field_profile.history) == 0
    
    @pytest.mark.asyncio
    async def test_add_field_history_record(self, field_history_service, sample_field_profile):
        """Test adding field history record."""
        history_data = FieldHistoryRequest(
            year=2023,
            crop_name="corn",
            variety="Pioneer 1234",
            planting_date=date(2023, 5, 1),
            harvest_date=date(2023, 10, 15),
            yield_amount=180.5,
            yield_units="bu/acre",
            tillage_type="no_till",
            irrigation_used=True,
            gross_revenue=900.0,
            total_costs=450.0,
            net_profit=450.0
        )
        
        record = await field_history_service.add_field_history_record(
            field_id="test_field_001",
            history_data=history_data
        )
        
        assert record.year == 2023
        assert record.crop_name == "corn"
        assert record.variety == "Pioneer 1234"
        assert record.yield_amount == 180.5
        assert record.net_profit == 450.0
        
        # Verify it was added to field profile
        field_profile = field_history_service.field_profiles["test_field_001"]
        assert len(field_profile.history) == 1
        assert field_profile.history[0].year == 2023


class TestRotationOptimizationEngine:
    """Test rotation optimization functionality."""
    
    @pytest.fixture
    def optimization_engine(self):
        """Create optimization engine instance."""
        return RotationOptimizationEngine()
    
    @pytest.fixture
    def sample_field_profile(self):
        """Create sample field profile for optimization testing."""
        field_profile = FieldProfile(
            field_id="opt_test_field",
            field_name="Optimization Test Field",
            farm_id="farm_001",
            size_acres=160.0,
            soil_type="silt_loam",
            climate_zone="5a"
        )
        
        # Add some history
        field_profile.history = [
            FieldHistoryRecord(year=2020, crop_name="corn", yield_amount=175.0),
            FieldHistoryRecord(year=2021, crop_name="soybean", yield_amount=55.0),
            FieldHistoryRecord(year=2022, crop_name="corn", yield_amount=180.0)
        ]
        
        return field_profile
    
    @pytest.fixture
    def sample_goals(self):
        """Create sample rotation goals."""
        return [
            RotationGoal(
                goal_id="goal_1",
                goal_type=RotationGoalType.SOIL_HEALTH,
                priority=8,
                weight=0.4,
                description="Improve soil health through diverse rotation"
            ),
            RotationGoal(
                goal_id="goal_2",
                goal_type=RotationGoalType.PROFIT_MAXIMIZATION,
                priority=7,
                weight=0.6,
                description="Maximize economic returns"
            )
        ]
    
    @pytest.fixture
    def sample_constraints(self):
        """Create sample rotation constraints."""
        return [
            RotationConstraint(
                constraint_id="constraint_1",
                constraint_type=ConstraintType.REQUIRED_CROP,
                description="Must include corn in rotation",
                parameters={"crop_name": "corn"}
            ),
            RotationConstraint(
                constraint_id="constraint_2",
                constraint_type=ConstraintType.EXCLUDED_CROP,
                description="Avoid continuous corn",
                parameters={"crop_name": "corn"},
                is_hard_constraint=False
            )
        ]
    
    @pytest.mark.asyncio
    async def test_generate_optimal_rotation(
        self, 
        optimization_engine, 
        sample_field_profile, 
        sample_goals, 
        sample_constraints
    ):
        """Test optimal rotation generation."""
        
        rotation_plan = await optimization_engine.generate_optimal_rotation(
            field_profile=sample_field_profile,
            goals=sample_goals,
            constraints=sample_constraints,
            planning_horizon=5
        )
        
        assert rotation_plan.field_id == "opt_test_field"
        assert rotation_plan.planning_horizon == 5
        assert len(rotation_plan.rotation_years) == 5
        assert rotation_plan.overall_score is not None
        assert rotation_plan.overall_score >= 0
        
        # Check that required crop (corn) is included
        crop_sequence = rotation_plan.get_crop_sequence()
        assert "corn" in crop_sequence
        
        # Check that rotation details are provided
        assert len(rotation_plan.rotation_details) == 5
        for year, details in rotation_plan.rotation_details.items():
            assert 'crop_name' in details
            assert 'estimated_yield' in details
            assert 'planting_recommendations' in details


class TestRotationIntegration:
    """Integration tests for complete rotation planning workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_rotation_planning_workflow(self):
        """Test complete workflow from field creation to rotation plan."""
        
        # Initialize services
        field_service = FieldHistoryService()
        optimization_engine = RotationOptimizationEngine()
        
        # Step 1: Create field profile
        field_profile = await field_service.create_field_profile(
            field_id="integration_test_field",
            field_name="Integration Test Field",
            farm_id="test_farm",
            field_characteristics={
                'size_acres': 120.0,
                'soil_type': 'silt_loam',
                'climate_zone': '5a',
                'irrigation_available': True
            }
        )
        
        # Step 2: Add field history
        history_records = [
            {"year": 2020, "crop_name": "corn", "yield_amount": 170.0},
            {"year": 2021, "crop_name": "soybean", "yield_amount": 52.0},
            {"year": 2022, "crop_name": "wheat", "yield_amount": 62.0},
            {"year": 2023, "crop_name": "corn", "yield_amount": 175.0}
        ]
        
        import_results = await field_service.bulk_import_history(
            field_id="integration_test_field",
            history_records=history_records
        )
        
        assert import_results['summary']['successful_imports'] == 4
        
        # Step 3: Define goals and constraints
        goals = [
            RotationGoal(
                goal_id="integration_goal_1",
                goal_type=RotationGoalType.SOIL_HEALTH,
                priority=8,
                weight=0.5,
                description="Improve soil health"
            ),
            RotationGoal(
                goal_id="integration_goal_2",
                goal_type=RotationGoalType.PROFIT_MAXIMIZATION,
                priority=7,
                weight=0.5,
                description="Maximize profit"
            )
        ]
        
        constraints = [
            RotationConstraint(
                constraint_id="integration_constraint_1",
                constraint_type=ConstraintType.REQUIRED_CROP,
                description="Include corn in rotation",
                parameters={"crop_name": "corn"}
            )
        ]
        
        # Step 4: Generate optimal rotation
        rotation_plan = await optimization_engine.generate_optimal_rotation(
            field_profile=field_profile,
            goals=goals,
            constraints=constraints,
            planning_horizon=5
        )
        
        # Verify rotation plan
        assert rotation_plan.field_id == "integration_test_field"
        assert rotation_plan.planning_horizon == 5
        assert len(rotation_plan.rotation_years) == 5
        assert "corn" in rotation_plan.get_crop_sequence()  # Constraint satisfied
        assert rotation_plan.overall_score > 0
        
        print(f"Integration test completed successfully!")
        print(f"Rotation plan: {rotation_plan.get_crop_sequence()}")
        print(f"Overall score: {rotation_plan.overall_score}")


if __name__ == "__main__":
    # Run specific test for debugging
    import asyncio
    
    async def run_integration_test():
        test_instance = TestRotationIntegration()
        await test_instance.test_complete_rotation_planning_workflow()
    
    asyncio.run(run_integration_test())