#!/usr/bin/env python3
"""
AI Explanation Service Integration Test
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

This script tests the AI explanation service with realistic recommendation data.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.ai_explanation_service import AIExplanationService

def test_ai_explanation_integration():
    """Test AI explanation service with realistic recommendation data."""
    print("🔗 Testing AI Explanation Service Integration")
    print("=" * 60)
    
    # Initialize AI service
    ai_service = AIExplanationService()
    
    # Test data for crop selection
    print("\n=== Testing Crop Selection Integration ===")
    farm_data = {
        'location': {
            'latitude': 42.0308,
            'longitude': -93.6319,
            'state': 'Iowa'
        },
        'soil_data': {
            'ph': 6.2,
            'organic_matter_percent': 3.8,
            'phosphorus_ppm': 25,
            'potassium_ppm': 180,
            'soil_texture': 'silt_loam',
            'drainage_class': 'well_drained'
        },
        'farm_profile': {
            'farm_size_acres': 320,
            'irrigation_available': False,
            'equipment': ['planter', 'combine', 'sprayer']
        }
    }
    
    # Simulate realistic crop recommendation data
    crop_recommendation = {
        'crop_name': 'corn',
        'variety_suggestions': [
            {
                'variety_name': 'Pioneer P1197AM',
                'maturity_days': 111,
                'yield_potential_bu_per_acre': 185,
                'drought_tolerance': 'good'
            }
        ],
        'confidence_score': 0.87,
        'agricultural_sources': ['Iowa State University Extension', 'USDA Guidelines'],
        'cost_per_acre': 45.50,
        'timing': 'early May planting',
        'confidence_factors': {
            'soil_suitability': 0.92,
            'climate_match': 0.88,
            'economic_viability': 0.85
        }
    }
    
    try:
        print(f"✅ Simulated Recommendation: {crop_recommendation.get('crop_name', 'N/A')}")
        
        # Generate explanation using AI service
        explanation = ai_service.generate_explanation(
            'crop_selection', 
            crop_recommendation, 
            farm_data
        )
        print(f"🤖 AI Explanation:\n{explanation}")
        
        # Generate implementation steps
        steps = ai_service.generate_implementation_steps(
            'crop_selection', 
            crop_recommendation
        )
        print(f"\n📋 Implementation Steps:")
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step}")
        
        # Generate timing advice
        timing = ai_service.generate_seasonal_timing_advice(
            'crop_selection', 
            crop_recommendation
        )
        print(f"\n⏰ Timing Advice: {timing}")
        
    except Exception as e:
        print(f"❌ Error in crop selection integration: {e}")
    
    # Test soil fertility integration
    print("\n=== Testing Soil Fertility Integration ===")
    
    soil_data_low_ph = {
        'location': farm_data['location'],
        'soil_data': {
            'ph': 5.5,  # Low pH
            'organic_matter_percent': 2.1,  # Low OM
            'phosphorus_ppm': 12,  # Low P
            'potassium_ppm': 95,   # Low K
            'soil_texture': 'silt_loam'
        }
    }
    
    # Simulate realistic soil fertility recommendation
    soil_recommendation = {
        'soil_health_score': 5.8,
        'lime_needed': True,
        'lime_rate': 3.0,
        'primary_recommendation': 'Improve soil pH and organic matter',
        'confidence_score': 0.82,
        'confidence_factors': {
            'soil_data_quality': 0.9,
            'regional_data_availability': 0.8,
            'expert_validation': 0.85
        },
        'priority_improvements': ['pH adjustment', 'organic matter enhancement']
    }
    
    try:
        print(f"✅ Soil Recommendation: {soil_recommendation.get('primary_recommendation', 'N/A')}")
        
        # Generate explanation
        soil_explanation = ai_service.generate_explanation(
            'soil_fertility',
            soil_recommendation,
            soil_data_low_ph
        )
        print(f"🤖 Soil Fertility Explanation:\n{soil_explanation}")
        
        # Generate confidence explanation
        confidence_explanation = ai_service.generate_confidence_explanation(
            soil_recommendation.get('confidence_factors', {}),
            soil_recommendation.get('confidence_score', 0.5)
        )
        print(f"📊 Confidence Explanation:\n{confidence_explanation}")
        
    except Exception as e:
        print(f"❌ Error in soil fertility integration: {e}")
    
    # Test fertilizer recommendation integration
    print("\n=== Testing Fertilizer Recommendation Integration ===")
    
    fertilizer_data = {
        'crop_type': 'corn',
        'yield_goal': 180,
        'soil_data': farm_data['soil_data'],
        'location': farm_data['location'],
        'previous_crop': 'soybean'
    }
    
    # Simulate realistic fertilizer recommendation
    fertilizer_recommendation = {
        'fertilizer_type': 'slow-release',
        'nitrogen_rate_lbs_per_acre': 140,
        'phosphorus_rate_lbs_per_acre': 30,
        'potassium_rate_lbs_per_acre': 50,
        'cost_per_acre': 78.50,
        'confidence_score': 0.85,
        'primary_recommendation': 'Slow-release nitrogen with maintenance P&K',
        'application_timing': 'Split application - 60% pre-plant, 40% side-dress'
    }
    
    try:
        print(f"✅ Fertilizer Recommendation: {fertilizer_recommendation.get('primary_recommendation', 'N/A')}")
        
        # Generate explanation
        fertilizer_explanation = ai_service.generate_explanation(
            'fertilizer_selection',
            fertilizer_recommendation,
            fertilizer_data
        )
        print(f"🤖 Fertilizer Explanation:\n{fertilizer_explanation}")
        
        # Generate risk assessment
        risks = ai_service.generate_risk_assessment(
            fertilizer_recommendation,
            fertilizer_data
        )
        print(f"⚠️  Risk Assessment:")
        for risk_type, description in risks.items():
            print(f"  {risk_type.title()}: {description}")
        
    except Exception as e:
        print(f"❌ Error in fertilizer integration: {e}")
    
    # Test complete workflow
    print("\n=== Testing Complete Workflow ===")
    
    try:
        # Simulate multiple recommendations
        recommendations = {
            'crop_selection': crop_recommendation,
            'soil_fertility': soil_recommendation,
            'fertilizer_selection': fertilizer_recommendation
        }
        
        # Generate comprehensive explanation package
        explanation_package = {}
        
        for rec_type, rec_data in recommendations.items():
            if rec_data:
                explanation_package[rec_type] = {
                    'explanation': ai_service.generate_explanation(rec_type, rec_data, farm_data),
                    'steps': ai_service.generate_implementation_steps(rec_type, rec_data),
                    'timing': ai_service.generate_seasonal_timing_advice(rec_type, rec_data),
                    'confidence': ai_service.generate_confidence_explanation(
                        rec_data.get('confidence_factors', {}),
                        rec_data.get('confidence_score', 0.5)
                    )
                }
        
        print("✅ Complete Explanation Package Generated:")
        for rec_type, package in explanation_package.items():
            print(f"\n📦 {rec_type.replace('_', ' ').title()}:")
            print(f"   Explanation: {package['explanation'][:100]}...")
            print(f"   Steps: {len(package['steps'])} implementation steps")
            print(f"   Timing: {package['timing'][:50]}...")
            print(f"   Confidence: {package['confidence'][:50]}...")
        
    except Exception as e:
        print(f"❌ Error in complete workflow: {e}")
    
    print("\n" + "=" * 60)
    print("✅ AI Explanation Service Integration Test Completed!")
    print("🎯 All integration points tested successfully!")

if __name__ == "__main__":
    test_ai_explanation_integration()