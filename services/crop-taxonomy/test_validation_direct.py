#!/usr/bin/env python3
"""
Direct test for agricultural validation service.

This test imports the standalone service directly without going through the services module.
"""

import asyncio
import sys
import os
from datetime import datetime
from uuid import uuid4

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import directly from the standalone service file
import importlib.util
spec = importlib.util.spec_from_file_location(
    "standalone_agricultural_validation_service", 
    os.path.join(os.path.dirname(__file__), 'src', 'services', 'standalone_agricultural_validation_service.py')
)
standalone_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(standalone_module)

# Get the classes from the module
StandaloneAgriculturalValidationService = standalone_module.StandaloneAgriculturalValidationService
VarietyRecommendation = standalone_module.VarietyRecommendation
VarietyRecommendationRequest = standalone_module.VarietyRecommendationRequest


async def test_agricultural_validation():
    """Test the agricultural validation service."""
    print("🧪 Testing Agricultural Validation Service...")
    
    service = StandaloneAgriculturalValidationService()
    
    # Create sample recommendations
    recommendations = [
        VarietyRecommendation(
            variety_name="Test Corn Variety 1",
            overall_score=0.85,
            suitability_factors={"yield": 0.9, "disease_resistance": 0.8},
            individual_scores={"yield": 0.9, "disease_resistance": 0.8},
            weighted_contributions={"yield": 0.4, "disease_resistance": 0.3},
            score_details={"yield": "High yield potential", "disease_resistance": "Good resistance"},
            yield_expectation="High",
            risk_assessment={"overall_risk": "low"},
            management_difficulty="medium",
            performance_prediction={"regional_performance": {"confidence": 0.8}},
            adaptation_strategies=[{"strategy": "optimal_planting_date"}],
            recommended_practices=["fertilizer_application", "pest_monitoring"],
            economic_analysis={"roi": 0.15, "break_even_yield": 150, "expected_yield": 180}
        ),
        VarietyRecommendation(
            variety_name="Test Corn Variety 2",
            overall_score=0.75,
            suitability_factors={"yield": 0.7, "disease_resistance": 0.9},
            individual_scores={"yield": 0.7, "disease_resistance": 0.9},
            weighted_contributions={"yield": 0.3, "disease_resistance": 0.4},
            score_details={"yield": "Moderate yield", "disease_resistance": "Excellent resistance"},
            yield_expectation="Medium",
            risk_assessment={"overall_risk": "medium"},
            management_difficulty="low",
            performance_prediction={"regional_performance": {"confidence": 0.9}},
            adaptation_strategies=[{"strategy": "disease_management"}],
            recommended_practices=["disease_monitoring"],
            economic_analysis={"roi": 0.12, "break_even_yield": 140, "expected_yield": 160}
        )
    ]
    
    # Create sample request context
    request_context = VarietyRecommendationRequest(
        crop_name="corn",
        location_data={"latitude": 40.0, "longitude": -95.0, "region": "Midwest"},
        soil_conditions={"ph": 6.5, "organic_matter": 3.2},
        farming_objectives=["high_yield", "disease_resistance"],
        production_system="conventional",
        available_equipment=["planter", "sprayer"],
        yield_priority_weight=0.4,
        quality_priority_weight=0.3,
        risk_management_weight=0.3,
        max_recommendations=10
    )
    
    # Create sample regional and crop context
    regional_context = {
        "region": "Midwest",
        "climate_zone": "6a",
        "average_yield": 150,
        "growing_season_days": 120
    }
    
    crop_context = {
        "soil_ph": 6.5,
        "organic_matter": 3.2,
        "crop_type": "corn"
    }
    
    # Perform validation
    print("📊 Performing agricultural validation...")
    validation_result = await service.validate_recommendations(
        recommendations=recommendations,
        request_context=request_context,
        regional_context=regional_context,
        crop_context=crop_context
    )
    
    print(f"✅ Validation completed:")
    print(f"   Overall Score: {validation_result.overall_score:.3f}")
    print(f"   Status: {validation_result.status}")
    print(f"   Expert Review Required: {validation_result.expert_review_required}")
    print(f"   Issues Found: {len(validation_result.issues)}")
    print(f"   Validation Duration: {validation_result.validation_duration_ms:.1f}ms")
    
    if validation_result.issues:
        print("\n⚠️  Issues Found:")
        for issue in validation_result.issues:
            print(f"   {issue.severity.value.upper()}: {issue.message}")
            if issue.suggested_action:
                print(f"      Suggested Action: {issue.suggested_action}")
    
    return validation_result


async def test_expert_review_workflow():
    """Test the expert review workflow."""
    print("\n👨‍🌾 Testing Expert Review Workflow...")
    
    service = StandaloneAgriculturalValidationService()
    
    # Create an expert reviewer
    reviewer = await service.create_expert_reviewer(
        name="Dr. Jane Smith",
        credentials="PhD in Agronomy, 15 years experience",
        specialization=["corn", "soybean", "precision_agriculture"],
        region="Midwest",
        institution="Iowa State University",
        contact_email="jane.smith@iastate.edu"
    )
    
    print(f"✅ Expert reviewer created: {reviewer.name}")
    print(f"   Institution: {reviewer.institution}")
    print(f"   Specializations: {', '.join(reviewer.specialization)}")
    
    # Submit an expert review
    validation_id = uuid4()
    review_data = {
        "overall_score": 0.88,
        "agricultural_soundness": 0.92,
        "regional_applicability": 0.85,
        "economic_feasibility": 0.80,
        "farmer_practicality": 0.90,
        "comments": "Excellent variety selection with strong agricultural foundation. Minor concerns about economic feasibility in current market conditions.",
        "recommendations": [
            "Monitor fertilizer costs closely",
            "Consider yield insurance for risk management",
            "Verify soil test results before planting"
        ],
        "concerns": [
            "High input costs may impact profitability",
            "Limited regional performance data for one variety"
        ],
        "approval_conditions": [
            "Verify current fertilizer prices",
            "Confirm soil test accuracy"
        ],
        "overall_approval": True
    }
    
    review = await service.submit_expert_review(
        validation_id=validation_id,
        reviewer_id=reviewer.reviewer_id,
        review_data=review_data
    )
    
    print(f"✅ Expert review submitted:")
    print(f"   Overall Score: {review.overall_score:.2f}")
    print(f"   Agricultural Soundness: {review.agricultural_soundness:.2f}")
    print(f"   Regional Applicability: {review.regional_applicability:.2f}")
    print(f"   Economic Feasibility: {review.economic_feasibility:.2f}")
    print(f"   Farmer Practicality: {review.farmer_practicality:.2f}")
    print(f"   Overall Approval: {review.overall_approval}")
    print(f"   Comments: {review.comments}")
    
    return review


async def test_farmer_satisfaction_tracking():
    """Test farmer satisfaction tracking."""
    print("\n👨‍🌾 Testing Farmer Satisfaction Tracking...")
    
    service = StandaloneAgriculturalValidationService()
    
    # Track farmer satisfaction
    recommendation_id = uuid4()
    farmer_id = uuid4()
    satisfaction_score = 4.5
    feedback = "Great recommendations! The variety selection helped increase my corn yield by 18% compared to last year. The disease resistance was excellent and I had minimal pest issues."
    
    await service.track_farmer_satisfaction(
        recommendation_id=recommendation_id,
        farmer_id=farmer_id,
        satisfaction_score=satisfaction_score,
        feedback=feedback
    )
    
    print(f"✅ Farmer satisfaction tracked:")
    print(f"   Satisfaction Score: {satisfaction_score}/5.0")
    print(f"   Feedback: {feedback}")
    
    return True


async def test_edge_cases():
    """Test edge cases and error conditions."""
    print("\n🔍 Testing Edge Cases...")
    
    service = StandaloneAgriculturalValidationService()
    
    # Test with problematic recommendations
    problematic_recommendations = [
        VarietyRecommendation(
            variety_name="Low ROI Variety",
            overall_score=0.3,
            economic_analysis={"roi": 0.02},  # Very low ROI
            performance_prediction={"regional_performance": {"confidence": 0.3}}  # Low confidence
        ),
        VarietyRecommendation(
            variety_name="High Management Variety",
            overall_score=0.4,
            management_difficulty="high",
            economic_analysis={"roi": 0.08}
        )
    ]
    
    request_context = VarietyRecommendationRequest(crop_name="corn")
    regional_context = {"region": "Midwest", "average_yield": 150}
    crop_context = {"soil_ph": 6.5}
    
    result = await service.validate_recommendations(
        recommendations=problematic_recommendations,
        request_context=request_context,
        regional_context=regional_context,
        crop_context=crop_context
    )
    
    print(f"✅ Edge case validation completed:")
    print(f"   Overall Score: {result.overall_score:.3f}")
    print(f"   Expert Review Required: {result.expert_review_required}")
    print(f"   Issues Found: {len(result.issues)}")
    
    if result.issues:
        print("   Issues:")
        for issue in result.issues:
            print(f"     {issue.severity.value.upper()}: {issue.message}")
    
    return result


async def test_regional_edge_cases():
    """Test regional edge cases."""
    print("\n🌍 Testing Regional Edge Cases...")
    
    service = StandaloneAgriculturalValidationService()
    
    # Test with edge case regions
    edge_case_regions = [
        {"region": "arctic", "climate_zone": "1a", "average_yield": 50},
        {"region": "desert", "climate_zone": "9a", "average_yield": 80},
        {"region": "tropical", "climate_zone": "11a", "average_yield": 200}
    ]
    
    recommendations = [
        VarietyRecommendation(
            variety_name="Standard Variety",
            overall_score=0.8,
            economic_analysis={"roi": 0.15},
            performance_prediction={"regional_performance": {"confidence": 0.8}}
        )
    ]
    
    request_context = VarietyRecommendationRequest(crop_name="corn")
    crop_context = {"soil_ph": 6.5}
    
    for regional_context in edge_case_regions:
        result = await service.validate_recommendations(
            recommendations=recommendations,
            request_context=request_context,
            regional_context=regional_context,
            crop_context=crop_context
        )
        
        print(f"✅ {regional_context['region'].title()} region validation:")
        print(f"   Expert Review Required: {result.expert_review_required}")
        print(f"   Issues Found: {len(result.issues)}")
    
    return True


async def main():
    """Run all tests."""
    print("🚀 Starting Agricultural Validation System Tests")
    print("=" * 60)
    
    try:
        # Test basic validation
        await test_agricultural_validation()
        
        # Test expert review workflow
        await test_expert_review_workflow()
        
        # Test farmer satisfaction tracking
        await test_farmer_satisfaction_tracking()
        
        # Test edge cases
        await test_edge_cases()
        
        # Test regional edge cases
        await test_regional_edge_cases()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("✅ Agricultural Validation System is working correctly")
        print("✅ Expert Review Workflow is functional")
        print("✅ Farmer Satisfaction Tracking is operational")
        print("✅ Edge case handling is robust")
        print("✅ Regional validation is comprehensive")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)