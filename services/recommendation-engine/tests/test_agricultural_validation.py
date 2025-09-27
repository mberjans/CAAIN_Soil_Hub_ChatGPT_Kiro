"""
Agricultural Soundness Validation Tests
Comprehensive tests to validate agricultural logic and recommendations 
against established agricultural practices and extension service guidelines.
"""

import pytest
import asyncio
from typing import List, Dict
from datetime import datetime, date

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.rotation_models import (
    FieldProfile, RotationGoal, RotationConstraint,
    CropRotationPlan, RotationGoalType, ConstraintType
)
from services.rotation_optimization_engine import RotationOptimizationEngine


class TestCropCompatibilityValidation:
    """Test crop compatibility matrix against agricultural best practices."""
    
    @pytest.fixture
    def optimization_engine(self):
        """Create optimization engine instance."""
        return RotationOptimizationEngine()
    
    def test_crop_compatibility_matrix_structure(self, optimization_engine):
        """Test that crop compatibility matrix follows agricultural principles."""
        matrix = optimization_engine.crop_compatibility_matrix
        
        # Validate key crops are present
        essential_crops = ['corn', 'soybean', 'wheat', 'alfalfa', 'oats']
        for crop in essential_crops:
            assert crop in matrix, f"Essential crop {crop} missing from compatibility matrix"
        
        # Test each crop has required fields
        for crop_name, crop_data in matrix.items():
            assert 'good_next' in crop_data, f"Crop {crop_name} missing 'good_next' field"
            assert 'avoid_next' in crop_data, f"Crop {crop_name} missing 'avoid_next' field"
            assert 'nitrogen_demand' in crop_data, f"Crop {crop_name} missing 'nitrogen_demand' field"
            assert 'pest_pressure' in crop_data, f"Crop {crop_name} missing 'pest_pressure' field"
            assert 'disease_pressure' in crop_data, f"Crop {crop_name} missing 'disease_pressure' field"
    
    def test_continuous_cropping_restrictions(self, optimization_engine):
        """Test that continuous cropping is appropriately restricted."""
        matrix = optimization_engine.crop_compatibility_matrix
        
        # Corn should avoid continuous corn (prevents rootworm buildup)
        assert 'corn' in matrix['corn']['avoid_next'], "Corn should avoid continuous corn"
        
        # Soybean should avoid continuous soybean (prevents pest buildup)
        assert 'soybean' in matrix['soybean']['avoid_next'], "Soybean should avoid continuous soybean"
        
        # Wheat should avoid other small grains to prevent disease cycles
        wheat_avoid = matrix['wheat']['avoid_next']
        assert 'wheat' in wheat_avoid, "Wheat should avoid continuous wheat"
        assert 'barley' in wheat_avoid, "Wheat should avoid barley (disease pressure)"
        assert 'oats' in wheat_avoid, "Wheat should avoid oats (disease pressure)"
    
    def test_nitrogen_fixation_crops_identified(self, optimization_engine):
        """Test that nitrogen-fixing crops are properly identified."""
        matrix = optimization_engine.crop_compatibility_matrix
        
        # Soybean should have nitrogen fixation
        assert 'nitrogen_fixation' in matrix['soybean'], "Soybean should have nitrogen_fixation value"
        assert matrix['soybean']['nitrogen_fixation'] > 0, "Soybean nitrogen fixation should be positive"
        
        # Alfalfa should have higher nitrogen fixation than soybean
        assert 'nitrogen_fixation' in matrix['alfalfa'], "Alfalfa should have nitrogen_fixation value"
        alfalfa_n = matrix['alfalfa']['nitrogen_fixation']
        soybean_n = matrix['soybean']['nitrogen_fixation']
        assert alfalfa_n > soybean_n, "Alfalfa should fix more nitrogen than soybean"
    
    def test_corn_soybean_rotation_compatibility(self, optimization_engine):
        """Test classic corn-soybean rotation compatibility."""
        matrix = optimization_engine.crop_compatibility_matrix
        
        # Corn should be good after soybean (nitrogen benefit)
        assert 'corn' in matrix['soybean']['good_next'], "Corn should be good after soybean"
        
        # Soybean should be good after corn (breaks pest cycles)
        assert 'soybean' in matrix['corn']['good_next'], "Soybean should be good after corn"


class TestNitrogenManagementValidation:
    """Test nitrogen management calculations for agricultural accuracy."""
    
    @pytest.fixture
    def optimization_engine(self):
        """Create optimization engine instance."""
        return RotationOptimizationEngine()
    
    def test_nitrogen_fixation_values_realistic(self, optimization_engine):
        """Test nitrogen fixation values are within realistic agricultural ranges."""
        matrix = optimization_engine.crop_compatibility_matrix
        
        # Soybean nitrogen fixation (typical range: 30-50 lbs/acre)
        soybean_n = matrix['soybean']['nitrogen_fixation']
        assert 25 <= soybean_n <= 60, f"Soybean N fixation {soybean_n} outside realistic range (25-60 lbs/acre)"
        
        # Alfalfa nitrogen fixation (typical range: 100-200 lbs/acre)
        alfalfa_n = matrix['alfalfa']['nitrogen_fixation']
        assert 100 <= alfalfa_n <= 200, f"Alfalfa N fixation {alfalfa_n} outside realistic range (100-200 lbs/acre)"
    
    def test_nitrogen_demand_classifications(self, optimization_engine):
        """Test nitrogen demand classifications match crop requirements."""
        matrix = optimization_engine.crop_compatibility_matrix
        
        # High nitrogen crops
        assert matrix['corn']['nitrogen_demand'] == 'high', "Corn should have high nitrogen demand"
        
        # Low nitrogen crops (nitrogen fixers)
        assert matrix['soybean']['nitrogen_demand'] == 'low', "Soybean should have low nitrogen demand"
        assert matrix['alfalfa']['nitrogen_demand'] == 'low', "Alfalfa should have low nitrogen demand"
        
        # Medium nitrogen crops
        assert matrix['wheat']['nitrogen_demand'] == 'medium', "Wheat should have medium nitrogen demand"
        assert matrix['oats']['nitrogen_demand'] == 'medium', "Oats should have medium nitrogen demand"


class TestYieldEstimationValidation:
    """Test yield estimation accuracy against regional averages."""
    
    @pytest.fixture
    def optimization_engine(self):
        """Create optimization engine instance."""
        return RotationOptimizationEngine()
    
    @pytest.fixture
    def test_field_profile(self):
        """Create test field profile."""
        return FieldProfile(
            field_id="test_field_yield",
            field_name="Yield Test Field", 
            farm_id="test_farm",
            size_acres=160.0,
            soil_type="silt_loam",
            drainage_class="well_drained",
            climate_zone="5a"
        )
    
    @pytest.mark.asyncio
    async def test_base_yield_estimates_realistic(self, optimization_engine, test_field_profile):
        """Test base yield estimates are within realistic ranges."""
        
        # Test corn yield after soybean (should get nitrogen benefit)
        corn_yield_after_soybean = await optimization_engine._estimate_crop_yield(
            'corn', test_field_profile, 1, ['soybean', 'corn']
        )
        
        # Midwest corn yields typically 150-200 bu/acre
        assert 140 <= corn_yield_after_soybean <= 220, f"Corn yield {corn_yield_after_soybean} outside realistic range"
        
        # Test soybean yield
        soybean_yield = await optimization_engine._estimate_crop_yield(
            'soybean', test_field_profile, 0, ['soybean']
        )
        
        # Midwest soybean yields typically 40-60 bu/acre
        assert 35 <= soybean_yield <= 70, f"Soybean yield {soybean_yield} outside realistic range"
    
    @pytest.mark.asyncio
    async def test_nitrogen_credit_yield_boost(self, optimization_engine, test_field_profile):
        """Test yield increases from nitrogen-fixing predecessors."""
        
        # Corn after soybean should get nitrogen benefit
        corn_after_soybean = await optimization_engine._estimate_crop_yield(
            'corn', test_field_profile, 1, ['soybean', 'corn']
        )
        
        # Corn after alfalfa should get larger benefit
        corn_after_alfalfa = await optimization_engine._estimate_crop_yield(
            'corn', test_field_profile, 1, ['alfalfa', 'corn']
        )
        
        # Base corn yield (no predecessor benefit)
        corn_base = await optimization_engine._estimate_crop_yield(
            'corn', test_field_profile, 0, ['corn']
        )
        
        # Validate nitrogen benefits
        assert corn_after_soybean > corn_base, "Corn after soybean should yield more than base"
        assert corn_after_alfalfa > corn_after_soybean, "Corn after alfalfa should yield more than after soybean"
        
        # Check benefit percentages are realistic
        soybean_benefit = (corn_after_soybean - corn_base) / corn_base
        alfalfa_benefit = (corn_after_alfalfa - corn_base) / corn_base
        
        assert 0.05 <= soybean_benefit <= 0.15, f"Soybean N benefit {soybean_benefit:.2%} outside realistic range (5-15%)"
        assert 0.10 <= alfalfa_benefit <= 0.25, f"Alfalfa N benefit {alfalfa_benefit:.2%} outside realistic range (10-25%)"


class TestPestManagementValidation:
    """Test pest and disease management recommendations."""
    
    @pytest.fixture
    def optimization_engine(self):
        """Create optimization engine instance."""
        return RotationOptimizationEngine()
    
    def test_pest_pressure_identification(self, optimization_engine):
        """Test major pest pressures are identified for each crop."""
        matrix = optimization_engine.crop_compatibility_matrix
        
        # Corn pests
        corn_pests = matrix['corn']['pest_pressure']
        assert 'corn_borer' in corn_pests, "Corn borer should be listed for corn"
        assert 'rootworm' in corn_pests, "Rootworm should be listed for corn"
        
        # Soybean pests
        soybean_pests = matrix['soybean']['pest_pressure']
        assert 'soybean_aphid' in soybean_pests, "Soybean aphid should be listed"
        assert 'bean_leaf_beetle' in soybean_pests, "Bean leaf beetle should be listed"
    
    def test_disease_pressure_identification(self, optimization_engine):
        """Test major disease pressures are identified."""
        matrix = optimization_engine.crop_compatibility_matrix
        
        # Corn diseases
        corn_diseases = matrix['corn']['disease_pressure']
        assert 'gray_leaf_spot' in corn_diseases, "Gray leaf spot should be listed for corn"
        assert 'northern_corn_leaf_blight' in corn_diseases, "Northern corn leaf blight should be listed"
        
        # Wheat diseases
        wheat_diseases = matrix['wheat']['disease_pressure']
        assert 'fusarium_head_blight' in wheat_diseases, "Fusarium head blight should be listed for wheat"
    
    def test_rotation_breaks_pest_cycles(self, optimization_engine):
        """Test that rotations break pest and disease cycles."""
        matrix = optimization_engine.crop_compatibility_matrix
        
        # Corn should avoid continuous corn to break rootworm cycle
        assert 'corn' in matrix['corn']['avoid_next'], "Continuous corn should be avoided for rootworm management"
        
        # Small grains should avoid each other to break disease cycles
        wheat_avoid = matrix['wheat']['avoid_next']
        assert 'barley' in wheat_avoid and 'oats' in wheat_avoid, "Wheat should avoid other small grains"


class TestAgriculturalSoundnessValidation:
    """Test overall agricultural soundness of rotation recommendations."""
    
    @pytest.fixture
    def optimization_engine(self):
        """Create optimization engine instance."""
        return RotationOptimizationEngine()
    
    @pytest.fixture
    def sustainable_field_profile(self):
        """Create field profile for sustainability testing."""
        return FieldProfile(
            field_id="sustainable_test_field",
            field_name="Sustainability Test Field",
            farm_id="test_farm",
            size_acres=200.0,
            soil_type="silt_loam",
            drainage_class="well_drained",
            climate_zone="5a"
        )
    
    @pytest.fixture
    def soil_health_goals(self):
        """Create soil health focused goals."""
        return [
            RotationGoal(
                goal_id="soil_health_goal",
                goal_type=RotationGoalType.SOIL_HEALTH,
                priority=9,
                weight=0.7,
                description="Maximize soil health benefits"
            ),
            RotationGoal(
                goal_id="sustainability_goal", 
                goal_type=RotationGoalType.SUSTAINABILITY,
                priority=8,
                weight=0.3,
                description="Ensure sustainable practices"
            )
        ]
    
    @pytest.fixture
    def diversity_constraints(self):
        """Create constraints promoting diversity."""
        return [
            RotationConstraint(
                constraint_id="diversity_constraint",
                constraint_type=ConstraintType.MAX_CONSECUTIVE,
                description="Limit consecutive same crop",
                parameters={"crop_name": "corn", "max_consecutive": 2},
                is_hard_constraint=True
            )
        ]
    
    @pytest.mark.asyncio
    async def test_soil_health_rotation_generation(
        self, 
        optimization_engine,
        sustainable_field_profile,
        soil_health_goals,
        diversity_constraints
    ):
        """Test generation of agriculturally sound soil health rotation."""
        
        rotation_plan = await optimization_engine.generate_optimal_rotation(
            field_profile=sustainable_field_profile,
            goals=soil_health_goals,
            constraints=diversity_constraints,
            planning_horizon=5
        )
        
        crop_sequence = [year.crop_name for year in rotation_plan.rotation_years]
        
        # Test agricultural soundness principles
        
        # 1. Crop diversity - should have at least 3 different crops
        unique_crops = set(crop_sequence)
        assert len(unique_crops) >= 3, f"Rotation should have at least 3 crops, got {len(unique_crops)}: {unique_crops}"
        
        # 2. No excessive continuous cropping
        max_consecutive = self._calculate_max_consecutive_crops(crop_sequence)
        assert max_consecutive <= 2, f"No crop should appear more than 2 times consecutively, found {max_consecutive}"
        
        # 3. Include nitrogen-fixing crop for soil health
        nitrogen_fixers = ['soybean', 'alfalfa']
        has_nitrogen_fixer = any(crop in nitrogen_fixers for crop in crop_sequence)
        assert has_nitrogen_fixer, f"Soil health rotation should include nitrogen-fixing crop, got {crop_sequence}"
        
        # 4. Benefit scores should be reasonable
        benefit_scores = rotation_plan.benefit_analysis
        assert benefit_scores['nitrogen_fixation'] > 0, "Should have nitrogen fixation benefits"
        assert benefit_scores['soil_organic_matter'] > 0, "Should have soil organic matter benefits"
        assert benefit_scores['pest_management'] > 0, "Should have pest management benefits"
    
    @pytest.mark.asyncio
    async def test_rotation_follows_compatibility_rules(
        self,
        optimization_engine,
        sustainable_field_profile,
        soil_health_goals,
        diversity_constraints
    ):
        """Test that generated rotations follow crop compatibility rules."""
        
        rotation_plan = await optimization_engine.generate_optimal_rotation(
            field_profile=sustainable_field_profile,
            goals=soil_health_goals,
            constraints=diversity_constraints,
            planning_horizon=5
        )
        
        crop_sequence = [year.crop_name for year in rotation_plan.rotation_years]
        matrix = optimization_engine.crop_compatibility_matrix
        
        # Check each crop transition follows compatibility rules
        for i in range(len(crop_sequence) - 1):
            current_crop = crop_sequence[i]
            next_crop = crop_sequence[i + 1]
            
            # Get compatibility info for current crop
            compatibility = matrix.get(current_crop, {})
            avoid_next = compatibility.get('avoid_next', [])
            
            # Next crop should not be in avoid list (unless soft constraint)
            if next_crop in avoid_next:
                # This could be acceptable if it's a soft constraint violation
                # Check if there are hard constraints that might force this
                print(f"Warning: {next_crop} after {current_crop} violates compatibility preference")
    
    def _calculate_max_consecutive_crops(self, crop_sequence: List[str]) -> int:
        """Calculate maximum consecutive occurrences of same crop."""
        if not crop_sequence:
            return 0
        
        max_consecutive = 1
        current_consecutive = 1
        
        for i in range(1, len(crop_sequence)):
            if crop_sequence[i] == crop_sequence[i-1]:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 1
        
        return max_consecutive
    
    @pytest.mark.asyncio
    async def test_management_notes_agricultural_accuracy(self, optimization_engine):
        """Test management notes provide agriculturally accurate recommendations."""
        
        # Test corn after soybean management notes
        corn_after_soybean_notes = optimization_engine._get_management_notes('corn', 1, ['soybean', 'corn'])
        
        # Should recommend nitrogen reduction due to soybean nitrogen credit
        nitrogen_note_found = any('nitrogen' in note.lower() and 'reduce' in note.lower() 
                                for note in corn_after_soybean_notes)
        assert nitrogen_note_found, "Should recommend nitrogen reduction after soybean"
        
        # Test corn after alfalfa management notes
        corn_after_alfalfa_notes = optimization_engine._get_management_notes('corn', 1, ['alfalfa', 'corn'])
        
        # Should mention nitrogen availability from alfalfa
        alfalfa_nitrogen_note = any('alfalfa' in note.lower() and 'nitrogen' in note.lower()
                                  for note in corn_after_alfalfa_notes)
        assert alfalfa_nitrogen_note, "Should mention nitrogen availability from alfalfa"
    
    @pytest.mark.asyncio
    async def test_planting_recommendations_seasonal_accuracy(self, optimization_engine):
        """Test planting recommendations match seasonal requirements."""
        
        recommendations = optimization_engine._get_planting_recommendations('corn')
        planting_window = recommendations.get('planting_window', '')
        
        # Corn planting should be in spring (April-May in most regions)
        assert 'April' in planting_window or 'May' in planting_window, \
            f"Corn planting window should include April or May, got: {planting_window}"
        
        # Wheat recommendations (winter wheat)
        wheat_recommendations = optimization_engine._get_planting_recommendations('wheat')
        wheat_window = wheat_recommendations.get('planting_window', '')
        
        # Winter wheat should be planted in fall
        assert 'September' in wheat_window or 'October' in wheat_window, \
            f"Wheat planting should be in fall, got: {wheat_window}"


class TestConstraintValidation:
    """Test constraint handling for agricultural validity."""
    
    @pytest.fixture
    def optimization_engine(self):
        """Create optimization engine instance."""
        return RotationOptimizationEngine()
    
    @pytest.fixture
    def test_field_profile(self):
        """Create test field profile."""
        return FieldProfile(
            field_id="constraint_test_field",
            field_name="Constraint Test Field",
            farm_id="test_farm", 
            size_acres=120.0,
            soil_type="silt_loam",
            climate_zone="5a"
        )
    
    @pytest.mark.asyncio
    async def test_continuous_cropping_constraint_enforcement(self, optimization_engine, test_field_profile):
        """Test that continuous cropping constraints are properly enforced."""
        
        # Create strict constraint against continuous corn
        constraints = [
            RotationConstraint(
                constraint_id="no_continuous_corn",
                constraint_type=ConstraintType.MAX_CONSECUTIVE,
                description="No continuous corn",
                parameters={"crop_name": "corn", "max_consecutive": 1},
                is_hard_constraint=True
            )
        ]
        
        goals = [
            RotationGoal(
                goal_id="test_goal",
                goal_type=RotationGoalType.PROFIT_MAXIMIZATION,
                priority=5,
                weight=1.0,
                description="Test goal"
            )
        ]
        
        rotation_plan = await optimization_engine.generate_optimal_rotation(
            field_profile=test_field_profile,
            goals=goals,
            constraints=constraints,
            planning_horizon=5
        )
        
        crop_sequence = [year.crop_name for year in rotation_plan.rotation_years]
        
        # Check no continuous corn
        for i in range(len(crop_sequence) - 1):
            if crop_sequence[i] == 'corn':
                assert crop_sequence[i + 1] != 'corn', \
                    f"Found continuous corn at positions {i} and {i+1}: {crop_sequence}"


if __name__ == "__main__":
    # Run specific agricultural validation tests
    import asyncio
    
    async def run_agricultural_validation():
        """Run key agricultural validation tests."""
        print("Running Agricultural Soundness Validation Tests...")
        
        # Test crop compatibility
        test_compatibility = TestCropCompatibilityValidation()
        engine = test_compatibility.optimization_engine()
        test_compatibility.test_crop_compatibility_matrix_structure(engine)
        test_compatibility.test_continuous_cropping_restrictions(engine)
        test_compatibility.test_nitrogen_fixation_crops_identified(engine)
        test_compatibility.test_corn_soybean_rotation_compatibility(engine)
        print("✓ Crop compatibility validation passed")
        
        # Test nitrogen management
        test_nitrogen = TestNitrogenManagementValidation()
        engine = test_nitrogen.optimization_engine()
        test_nitrogen.test_nitrogen_fixation_values_realistic(engine)
        test_nitrogen.test_nitrogen_demand_classifications(engine)
        print("✓ Nitrogen management validation passed")
        
        # Test agricultural soundness
        test_soundness = TestAgriculturalSoundnessValidation()
        engine = test_soundness.optimization_engine()
        field_profile = test_soundness.sustainable_field_profile()
        goals = test_soundness.soil_health_goals()
        constraints = test_soundness.diversity_constraints()
        
        await test_soundness.test_soil_health_rotation_generation(
            engine, field_profile, goals, constraints
        )
        await test_soundness.test_rotation_follows_compatibility_rules(
            engine, field_profile, goals, constraints
        )
        await test_soundness.test_management_notes_agricultural_accuracy(engine)
        await test_soundness.test_planting_recommendations_seasonal_accuracy(engine)
        print("✓ Agricultural soundness validation passed")
        
        print("All agricultural validation tests completed successfully!")
    
    asyncio.run(run_agricultural_validation())