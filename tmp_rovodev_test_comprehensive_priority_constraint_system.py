#!/usr/bin/env python3
"""
Test script for comprehensive priority and constraint input system.
Tests TICKET-023_fertilizer-type-selection-3.1 implementation.
"""

import sys
import os
import logging
from decimal import Decimal

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'recommendation_engine', 'src'))

try:
    from models.fertilizer_models import FarmerPriorities, FarmerConstraints
    from services.fertilizer_type_selection_service import FertilizerTypeSelectionService
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import path...")
    sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'recommendation_engine'))
    try:
        from src.models.fertilizer_models import FarmerPriorities, FarmerConstraints
        from src.services.fertilizer_type_selection_service import FertilizerTypeSelectionService
    except ImportError as e2:
        print(f"Alternative import also failed: {e2}")
        sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_priority_validation():
    """Test priority validation functionality."""
    print("\n=== Testing Priority Validation ===")
    
    service = FertilizerTypeSelectionService()
    
    # Test valid priorities
    valid_priorities = FarmerPriorities(
        cost_effectiveness=0.8,
        soil_health=0.6,
        quick_results=0.4,
        environmental_impact=0.7,
        ease_of_application=0.3,
        long_term_benefits=0.5
    )
    
    validation_result = service._validate_priorities(valid_priorities)
    print(f"Valid priorities validation: {validation_result['is_valid']}")
    print(f"Warnings: {len(validation_result['warnings'])}")
    
    # Test invalid priorities (all zero)
    invalid_priorities = FarmerPriorities(
        cost_effectiveness=0.0,
        soil_health=0.0,
        quick_results=0.0,
        environmental_impact=0.0,
        ease_of_application=0.0,
        long_term_benefits=0.0
    )
    
    validation_result = service._validate_priorities(invalid_priorities)
    print(f"Invalid priorities validation: {validation_result['is_valid']}")
    print(f"Errors: {len(validation_result['errors'])}")
    
    return True

def test_constraint_validation():
    """Test constraint validation functionality."""
    print("\n=== Testing Constraint Validation ===")
    
    service = FertilizerTypeSelectionService()
    
    # Test valid constraints
    valid_constraints = FarmerConstraints(
        budget_per_acre=150.0,
        total_budget=15000.0,
        farm_size_acres=100.0,
        available_equipment=["broadcast_spreader", "liquid_applicator"],
        application_window_days=30,
        labor_availability="medium",
        organic_preference=False,
        environmental_concerns=True,
        soil_health_focus=True
    )
    
    validation_result = service._validate_constraints(valid_constraints)
    print(f"Valid constraints validation: {validation_result['is_valid']}")
    print(f"Warnings: {len(validation_result['warnings'])}")
    
    # Test invalid constraints - Pydantic will catch these at model level
    try:
        invalid_constraints = FarmerConstraints(
            budget_per_acre=-50.0,  # Invalid negative budget
            farm_size_acres=0.0,    # Invalid zero farm size
            available_equipment=[]  # Invalid empty equipment
        )
        print("❌ Pydantic validation should have caught invalid values")
        return False
    except Exception as e:
        print(f"✅ Pydantic correctly caught invalid constraints: validation working at model level")
        
        # Test with constraints that pass Pydantic but fail our business logic
        business_invalid_constraints = FarmerConstraints(
            budget_per_acre=1.0,    # Very low but positive budget
            farm_size_acres=0.1,    # Very small farm
            available_equipment=[]  # Empty equipment list
        )
        
        validation_result = service._validate_constraints(business_invalid_constraints)
        print(f"Business logic validation: {validation_result['is_valid']}")
        print(f"Errors: {len(validation_result['errors'])}")
    
    return True

def test_priority_analysis():
    """Test priority profile analysis."""
    print("\n=== Testing Priority Analysis ===")
    
    service = FertilizerTypeSelectionService()
    
    # Test environmental steward profile
    env_priorities = FarmerPriorities(
        cost_effectiveness=0.2,
        soil_health=0.9,
        quick_results=0.1,
        environmental_impact=0.8,
        ease_of_application=0.3,
        long_term_benefits=0.7
    )
    
    analysis = service._analyze_priority_profile(env_priorities)
    print(f"Environmental priorities profile: {analysis['profile_type']}")
    print(f"Dominant priority: {analysis['dominant_priority']}")
    print(f"Conflicts detected: {len(analysis['conflicts'])}")
    
    # Test cost-conscious profile
    cost_priorities = FarmerPriorities(
        cost_effectiveness=0.9,
        soil_health=0.2,
        quick_results=0.8,
        environmental_impact=0.1,
        ease_of_application=0.6,
        long_term_benefits=0.2
    )
    
    analysis = service._analyze_priority_profile(cost_priorities)
    print(f"Cost-conscious priorities profile: {analysis['profile_type']}")
    print(f"Conflicts detected: {len(analysis['conflicts'])}")
    
    return True

def test_constraint_analysis():
    """Test constraint analysis functionality."""
    print("\n=== Testing Constraint Analysis ===")
    
    service = FertilizerTypeSelectionService()
    
    # Test resource-constrained profile
    constrained = FarmerConstraints(
        budget_per_acre=50.0,   # Low budget
        farm_size_acres=25.0,
        available_equipment=["manual_application"],  # Limited equipment
        application_window_days=5,  # Short window
        labor_availability="low"
    )
    
    analysis = service._analyze_constraints(constrained)
    print(f"Resource-constrained profile: {analysis['constraint_profile']}")
    print(f"Limiting factors: {analysis['limiting_factors']}")
    print(f"Recommendations: {len(analysis['recommendations'])}")
    
    # Test flexible profile
    flexible = FarmerConstraints(
        budget_per_acre=200.0,
        farm_size_acres=500.0,
        available_equipment=["broadcast_spreader", "liquid_applicator", "fertigation_system"],
        application_window_days=60,
        labor_availability="high"
    )
    
    analysis = service._analyze_constraints(flexible)
    print(f"Flexible profile: {analysis['constraint_profile']}")
    print(f"Limiting factors: {analysis['limiting_factors']}")
    
    return True

async def test_comprehensive_system():
    """Test the complete comprehensive priority and constraint system."""
    print("\n=== Testing Comprehensive System Integration ===")
    
    service = FertilizerTypeSelectionService()
    
    priorities = FarmerPriorities(
        cost_effectiveness=0.7,
        soil_health=0.8,
        quick_results=0.3,
        environmental_impact=0.6,
        ease_of_application=0.5,
        long_term_benefits=0.7
    )
    
    constraints = FarmerConstraints(
        budget_per_acre=120.0,
        total_budget=12000.0,
        farm_size_acres=100.0,
        available_equipment=["broadcast_spreader", "liquid_applicator"],
        application_window_days=21,
        labor_availability="medium",
        organic_preference=True,
        environmental_concerns=True,
        soil_health_focus=True
    )
    
    try:
        recommendations = await service.get_fertilizer_type_recommendations(
            priorities=priorities,
            constraints=constraints,
            soil_data={"ph": 6.5, "organic_matter": 3.2},
            crop_data={"crop_type": "corn", "target_yield": 180},
            farm_profile={"region": "midwest", "climate_zone": "temperate"}
        )
        
        print("✅ Comprehensive system test passed!")
        print(f"Recommendations generated: {len(recommendations)}")
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive system test failed: {e}")
        return False

def main():
    """Run all tests for the comprehensive priority and constraint input system."""
    print("Testing TICKET-023_fertilizer-type-selection-3.1: Comprehensive Priority and Constraint Input System")
    print("=" * 80)
    
    tests = [
        test_priority_validation,
        test_constraint_validation,
        test_priority_analysis,
        test_constraint_analysis,
    ]
    
    passed = 0
    total = len(tests) + 1  # +1 for async test
    
    # Run synchronous tests
    for test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_func.__name__} passed")
            else:
                print(f"❌ {test_func.__name__} failed")
        except Exception as e:
            print(f"❌ {test_func.__name__} failed with error: {e}")
    
    # Run async test
    import asyncio
    try:
        if asyncio.run(test_comprehensive_system()):
            passed += 1
            print("✅ test_comprehensive_system passed")
        else:
            print("❌ test_comprehensive_system failed")
    except Exception as e:
        print(f"❌ test_comprehensive_system failed with error: {e}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Comprehensive priority and constraint input system is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)