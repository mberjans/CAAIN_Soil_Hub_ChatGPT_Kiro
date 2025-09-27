#!/usr/bin/env python3
"""
Agricultural Validation Script
Simple script to validate agricultural soundness of rotation optimization engine.
"""

import os
import sys
import asyncio

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.rotation_models import (
    FieldProfile, RotationGoal, RotationConstraint,
    RotationGoalType, ConstraintType
)
from services.rotation_optimization_engine import RotationOptimizationEngine


def test_crop_compatibility_matrix():
    """Test crop compatibility matrix against agricultural best practices."""
    print("Testing crop compatibility matrix...")
    
    engine = RotationOptimizationEngine()
    matrix = engine.crop_compatibility_matrix
    
    # Test essential crops are present
    essential_crops = ['corn', 'soybean', 'wheat', 'alfalfa', 'oats']
    for crop in essential_crops:
        assert crop in matrix, f"Essential crop {crop} missing from compatibility matrix"
    
    # Test continuous cropping restrictions
    assert 'corn' in matrix['corn']['avoid_next'], "Corn should avoid continuous corn"
    assert 'soybean' in matrix['soybean']['avoid_next'], "Soybean should avoid continuous soybean"
    
    # Test nitrogen fixation values
    soybean_n = matrix['soybean']['nitrogen_fixation']
    alfalfa_n = matrix['alfalfa']['nitrogen_fixation']
    assert 25 <= soybean_n <= 60, f"Soybean N fixation {soybean_n} outside realistic range"
    assert 100 <= alfalfa_n <= 200, f"Alfalfa N fixation {alfalfa_n} outside realistic range"
    assert alfalfa_n > soybean_n, "Alfalfa should fix more nitrogen than soybean"
    
    # Test corn-soybean rotation compatibility
    assert 'corn' in matrix['soybean']['good_next'], "Corn should be good after soybean"
    assert 'soybean' in matrix['corn']['good_next'], "Soybean should be good after corn"
    
    print("✓ Crop compatibility matrix validation passed")


def test_nitrogen_management():
    """Test nitrogen management calculations."""
    print("Testing nitrogen management...")
    
    engine = RotationOptimizationEngine()
    matrix = engine.crop_compatibility_matrix
    
    # Test nitrogen demand classifications
    assert matrix['corn']['nitrogen_demand'] == 'high', "Corn should have high nitrogen demand"
    assert matrix['soybean']['nitrogen_demand'] == 'low', "Soybean should have low nitrogen demand"
    assert matrix['alfalfa']['nitrogen_demand'] == 'low', "Alfalfa should have low nitrogen demand"
    assert matrix['wheat']['nitrogen_demand'] == 'medium', "Wheat should have medium nitrogen demand"
    
    print("✓ Nitrogen management validation passed")


async def test_yield_estimation():
    """Test yield estimation accuracy."""
    print("Testing yield estimation...")
    
    engine = RotationOptimizationEngine()
    
    field_profile = FieldProfile(
        field_id="test_field_yield",
        field_name="Yield Test Field", 
        farm_id="test_farm",
        size_acres=160.0,
        soil_type="silt_loam",
        drainage_class="well_drained",
        climate_zone="5a"
    )
    
    # Test corn yield after soybean (should get nitrogen benefit)
    corn_yield_after_soybean = await engine._estimate_crop_yield(
        'corn', field_profile, 1, ['soybean', 'corn']
    )
    
    # Test base yields are realistic
    assert 140 <= corn_yield_after_soybean <= 220, f"Corn yield {corn_yield_after_soybean} outside realistic range"
    
    # Test nitrogen credit yield boost
    corn_after_alfalfa = await engine._estimate_crop_yield(
        'corn', field_profile, 1, ['alfalfa', 'corn']
    )
    
    corn_base = await engine._estimate_crop_yield(
        'corn', field_profile, 0, ['corn']
    )
    
    assert corn_after_soybean > corn_base, "Corn after soybean should yield more than base"
    assert corn_after_alfalfa > corn_after_soybean, "Corn after alfalfa should yield more than after soybean"
    
    print("✓ Yield estimation validation passed")


def test_pest_management():
    """Test pest and disease management recommendations."""
    print("Testing pest management...")
    
    engine = RotationOptimizationEngine()
    matrix = engine.crop_compatibility_matrix
    
    # Test pest pressure identification
    corn_pests = matrix['corn']['pest_pressure']
    assert 'corn_borer' in corn_pests, "Corn borer should be listed for corn"
    assert 'rootworm' in corn_pests, "Rootworm should be listed for corn"
    
    soybean_pests = matrix['soybean']['pest_pressure']
    assert 'soybean_aphid' in soybean_pests, "Soybean aphid should be listed"
    
    # Test disease pressure identification
    corn_diseases = matrix['corn']['disease_pressure']
    assert 'gray_leaf_spot' in corn_diseases, "Gray leaf spot should be listed for corn"
    
    wheat_diseases = matrix['wheat']['disease_pressure']
    assert 'fusarium_head_blight' in wheat_diseases, "Fusarium head blight should be listed for wheat"
    
    print("✓ Pest management validation passed")
    

async def test_agricultural_soundness():
    """Test overall agricultural soundness of rotation recommendations."""
    print("Testing agricultural soundness...")
    
    engine = RotationOptimizationEngine()
    
    field_profile = FieldProfile(
        field_id="sustainable_test_field",
        field_name="Sustainability Test Field",
        farm_id="test_farm",
        size_acres=200.0,
        soil_type="silt_loam",
        drainage_class="well_drained",
        climate_zone="5a"
    )
    
    goals = [
        RotationGoal(
            goal_id="soil_health_goal",
            goal_type=RotationGoalType.SOIL_HEALTH,
            priority=9,
            weight=0.7,
            description="Maximize soil health benefits"
        )
    ]
    
    constraints = [
        RotationConstraint(
            constraint_id="diversity_constraint",
            constraint_type=ConstraintType.MAX_CONSECUTIVE,
            description="Limit consecutive same crop",
            parameters={"crop_name": "corn", "max_consecutive": 2},
            is_hard_constraint=True
        )
    ]
    
    rotation_plan = await engine.generate_optimal_rotation(
        field_profile=field_profile,
        goals=goals,
        constraints=constraints,
        planning_horizon=5
    )
    
    crop_sequence = [year.crop_name for year in rotation_plan.rotation_years]
    
    # Test agricultural soundness principles
    
    # 1. Crop diversity - should have at least 3 different crops
    unique_crops = set(crop_sequence)
    assert len(unique_crops) >= 3, f"Rotation should have at least 3 crops, got {len(unique_crops)}: {unique_crops}"
    
    # 2. No excessive continuous cropping
    max_consecutive = calculate_max_consecutive_crops(crop_sequence)
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
    
    print(f"✓ Generated rotation: {crop_sequence}")
    print(f"✓ Overall score: {rotation_plan.overall_score:.1f}")
    print("✓ Agricultural soundness validation passed")


def calculate_max_consecutive_crops(crop_sequence):
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


def test_management_recommendations():
    """Test management notes provide agriculturally accurate recommendations."""
    print("Testing management recommendations...")
    
    engine = RotationOptimizationEngine()
    
    # Test corn after soybean management notes
    corn_after_soybean_notes = engine._get_management_notes('corn', 1, ['soybean', 'corn'])
    
    # Should recommend nitrogen reduction due to soybean nitrogen credit
    nitrogen_note_found = any('nitrogen' in note.lower() and 'reduce' in note.lower() 
                            for note in corn_after_soybean_notes)
    assert nitrogen_note_found, "Should recommend nitrogen reduction after soybean"
    
    # Test planting recommendations seasonal accuracy
    recommendations = engine._get_planting_recommendations('corn')
    planting_window = recommendations.get('planting_window', '')
    
    # Corn planting should be in spring (April-May in most regions)
    assert 'April' in planting_window or 'May' in planting_window, \
        f"Corn planting window should include April or May, got: {planting_window}"
    
    print("✓ Management recommendations validation passed")


async def main():
    """Run all agricultural validation tests."""
    print("=" * 50)
    print("AGRICULTURAL SOUNDNESS VALIDATION")
    print("=" * 50)
    
    try:
        # Run validation tests
        test_crop_compatibility_matrix()
        test_nitrogen_management()
        await test_yield_estimation()
        test_pest_management()
        await test_agricultural_soundness()
        test_management_recommendations()
        
        print("\n" + "=" * 50)
        print("ALL AGRICULTURAL VALIDATION TESTS PASSED! ✓")
        print("The rotation optimization engine demonstrates:")
        print("• Adherence to crop compatibility principles")
        print("• Realistic nitrogen management calculations")
        print("• Appropriate yield estimation models")
        print("• Sound pest and disease management practices")
        print("• Agricultural recommendations aligned with extension guidelines")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)