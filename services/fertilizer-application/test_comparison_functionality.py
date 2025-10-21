#!/usr/bin/env python3
"""
Simple test script to verify the comparison functionality works.
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the service and models we need
from src.services.comparison_service import MethodComparisonService
from src.models.application_models import (
    ApplicationMethod, ApplicationMethodType, FieldConditions, 
    CropRequirements, FertilizerSpecification, EquipmentSpecification, FertilizerForm
)

async def test_comparison_functionality():
    """Test that the comparison service works."""
    print("Testing MethodComparisonService functionality...")
    
    # Create a comparison service instance
    service = MethodComparisonService()
    print("✓ MethodComparisonService initialized successfully")
    
    # Create sample method A
    method_a = ApplicationMethod(
        method_id="method_a",
        method_type=ApplicationMethodType.BROADCAST,
        method_name="Broadcast Application",
        description="Broadcast fertilizer across entire field",
        application_timing="pre_plant",  # Changed from list to string
        recommended_equipment=EquipmentSpecification(
            equipment_type="spreader",
            capacity=10.0,
            maintenance_cost_per_hour=15.0
        ),
        application_rate=150.0,  # Required field
        rate_unit="lbs/acre",  # Required field
        efficiency_score=0.7,
        cost_per_acre=15.0,
        labor_requirements="medium",
        environmental_impact="moderate",
        pros=["Simple application", "Good coverage"],
        cons=["Less precise", "Potential for runoff"],
        crop_compatibility_score=0.8
    )
    
    print("✓ Sample method A created successfully")
    
    # Create sample method B
    method_b = ApplicationMethod(
        method_id="method_b",
        method_type=ApplicationMethodType.BAND,
        method_name="Band Application",
        description="Apply fertilizer in bands near seed row",
        application_timing="at_planting",  # Changed from list to string
        recommended_equipment=EquipmentSpecification(
            equipment_type="spreader",
            capacity=8.0,
            maintenance_cost_per_hour=20.0
        ),
        application_rate=140.0,  # Required field
        rate_unit="lbs/acre",  # Required field
        efficiency_score=0.85,
        cost_per_acre=20.0,
        labor_requirements="high",
        environmental_impact="low",
        pros=["More precise", "Less fertilizer needed"],
        cons=["More complex", "Requires specialized equipment"],
        crop_compatibility_score=0.85
    )
    
    print("✓ Sample method B created successfully")
    
    # Create sample field conditions
    field_conditions = FieldConditions(
        field_size_acres=100.0,
        soil_type="loam",
        drainage_class="well_drained"
    )
    
    print("✓ Sample field conditions created successfully")
    
    # Create sample crop requirements
    crop_requirements = CropRequirements(
        crop_type="corn",
        growth_stage="V6",
        target_yield=200.0,
        nutrient_requirements={"nitrogen": 150.0, "phosphorus": 40.0, "potassium": 80.0},
        application_timing_preferences=["at_planting"],
        growth_stage_deadlines={"V6": "2024-06-15", "R1": "2024-07-20"}
    )
    
    print("✓ Sample crop requirements created successfully")
    
    # Create sample fertilizer specification
    fertilizer_spec = FertilizerSpecification(
        fertilizer_type="nitrogen",
        npk_ratio="46-0-0",  # Required field
        form=FertilizerForm.GRANULAR,  # Required field (FertilizerForm enum)
        solubility=100.0,
        release_rate="immediate",
        cost_per_unit=0.5,
        unit="lbs"
    )
    
    print("✓ Sample fertilizer specification created successfully")
    
    # Create sample equipment
    sample_equipment = EquipmentSpecification(
        equipment_type="spreader",
        capacity=10.0,
        capacity_unit="lbs",
        application_width=60.0,
        application_rate_range={"min": 10.0, "max": 50.0},
        fuel_efficiency=0.8,
        maintenance_cost_per_hour=15.0
    )
    
    print("✓ Sample equipment created successfully")
    
    # Test the comparison method
    try:
        result = await service._compare_cost_effectiveness(method_a, method_b, field_conditions)
        print(f"✓ Cost effectiveness comparison completed: {result}")
    except Exception as e:
        print(f"✗ Cost effectiveness comparison failed: {e}")
        return False
    
    try:
        result = await service._compare_application_efficiency(method_a, method_b)
        print(f"✓ Application efficiency comparison completed: {result.method_a_score}, {result.method_b_score}")
    except Exception as e:
        print(f"✗ Application efficiency comparison failed: {e}")
        return False
    
    try:
        result = await service._compare_environmental_impact(method_a, method_b, field_conditions)
        print(f"✓ Environmental impact comparison completed: {result}")
    except Exception as e:
        print(f"✗ Environmental impact comparison failed: {e}")
        return False
    
    print("✓ All comparison methods working correctly")
    
    # Test multi-criteria analysis
    try:
        from src.services.comparison_service import ComparisonCriteria
        criteria = [ComparisonCriteria.COST_EFFECTIVENESS, ComparisonCriteria.APPLICATION_EFFICIENCY]
        weights = {
            ComparisonCriteria.COST_EFFECTIVENESS: 0.5,
            ComparisonCriteria.APPLICATION_EFFICIENCY: 0.5
        }
        
        multi_result = await service._perform_multi_criteria_analysis(
            method_a, method_b, field_conditions, crop_requirements,
            fertilizer_spec, [sample_equipment], criteria, weights
        )
        print(f"✓ Multi-criteria analysis completed")
        print(f"  Method A weighted score: {multi_result.weighted_scores.get(str(ApplicationMethodType.BROADCAST), 0)}")
        print(f"  Method B weighted score: {multi_result.weighted_scores.get(str(ApplicationMethodType.BAND), 0)}")
        print(f"  Overall winner: {multi_result.overall_winner}")
    except Exception as e:
        print(f"✗ Multi-criteria analysis failed: {e}")
        return False
    
    print("\n✓ All comparison functionality tests passed!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_comparison_functionality())
    if success:
        print("\n🎉 Method comparison engine is working correctly!")
        exit(0)
    else:
        print("\n❌ Method comparison engine has issues!")
        exit(1)