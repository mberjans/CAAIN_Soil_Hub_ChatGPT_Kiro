#!/usr/bin/env python3
"""
Simple test script for Decision Support Service.

This script tests the basic functionality of the decision support system
without requiring the full FastAPI application.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.application_models import (
    FieldConditions, CropRequirements, FertilizerSpecification, EquipmentSpecification
)
from src.services.decision_support_service import (
    DecisionSupportService, DecisionRule
)


async def test_decision_support():
    """Test the decision support service."""
    print("Testing Decision Support Service...")
    
    # Create test data
    field_conditions = FieldConditions(
        field_size_acres=150.0,
        soil_type="clay",
        
        
        slope_percent=2.0,
        drainage_class="well",
        
        
    )
    
    crop_requirements = CropRequirements(
        crop_type="corn",
        growth_stage="vegetative",
        nitrogen_requirement=120.0,
        phosphorus_requirement=40.0,
        potassium_requirement=80.0,
        row_spacing_inches=30.0,
        planting_date="2024-04-15",
        expected_harvest_date="2024-09-15"
    )
    
    fertilizer_specification = FertilizerSpecification(
        fertilizer_type="liquid",
        npk_ratio="28-0-0",
        form="liquid",
        nitrogen_content=28.0,
        phosphorus_content=0.0,
        potassium_content=0.0,
        application_rate_lbs_per_acre=100.0,
        cost_per_unit=0.45,
        availability="readily_available"
    )
    
    equipment = [
        EquipmentSpecification(
            equipment_type="broadcaster",
            capacity=1000.0,
            efficiency=0.85,
            cost_per_hour=25.0,
            availability="available"
        )
    ]
    
    # Initialize service
    service = DecisionSupportService()
    
    try:
        # Test decision tree
        print("\n1. Testing Decision Tree...")
        result = await service.provide_decision_support(
            field_conditions=field_conditions,
            crop_requirements=crop_requirements,
            fertilizer_specification=fertilizer_specification,
            available_equipment=equipment,
            decision_rule=DecisionRule.DECISION_TREE,
            include_scenarios=True,
            include_sensitivity=True
        )
        
        print(f"   Primary Recommendation: {result.primary_recommendation}")
        print(f"   Confidence Level: {result.confidence_level:.2f}")
        print(f"   Alternative Methods: {result.alternative_recommendations}")
        print(f"   Processing Time: {result.processing_time_ms:.2f}ms")
        print(f"   Risk Level: {result.risk_assessment['overall_risk_level']}")
        
        # Test expert system
        print("\n2. Testing Expert System...")
        result = await service.provide_decision_support(
            field_conditions=field_conditions,
            crop_requirements=crop_requirements,
            fertilizer_specification=fertilizer_specification,
            available_equipment=equipment,
            decision_rule=DecisionRule.EXPERT_SYSTEM,
            include_scenarios=False,
            include_sensitivity=False
        )
        
        print(f"   Primary Recommendation: {result.primary_recommendation}")
        print(f"   Expert Rules Applied: {len(result.expert_rules_applied)}")
        print(f"   Confidence Level: {result.confidence_level:.2f}")
        
        # Test weighted sum
        print("\n3. Testing Weighted Sum...")
        result = await service.provide_decision_support(
            field_conditions=field_conditions,
            crop_requirements=crop_requirements,
            fertilizer_specification=fertilizer_specification,
            available_equipment=equipment,
            decision_rule=DecisionRule.WEIGHTED_SUM,
            include_scenarios=True,
            include_sensitivity=True
        )
        
        print(f"   Primary Recommendation: {result.primary_recommendation}")
        print(f"   Decision Matrix Methods: {result.decision_matrix.methods}")
        print(f"   Confidence Level: {result.confidence_level:.2f}")
        
        # Test scenario analysis
        print("\n4. Testing Scenario Analysis...")
        if result.scenario_analysis:
            for scenario in result.scenario_analysis:
                print(f"   {scenario.scenario_type.value}: {scenario.method_rankings[0][0] if scenario.method_rankings else 'N/A'}")
        
        # Test sensitivity analysis
        print("\n5. Testing Sensitivity Analysis...")
        if result.sensitivity_analysis:
            for sensitivity in result.sensitivity_analysis[:3]:  # Show first 3
                print(f"   {sensitivity.parameter}: {sensitivity.recommendation_change}")
        
        print("\n✅ All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_decision_support())
    sys.exit(0 if success else 1)
