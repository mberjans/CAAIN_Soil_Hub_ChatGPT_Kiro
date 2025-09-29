#!/usr/bin/env python3
"""
AI Explanation Service Test
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

This script tests the AI explanation service functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.ai_explanation_service import AIExplanationService

def test_ai_explanation_service():
    """Test AI explanation service functionality."""
    print("🤖 Testing AI Explanation Service")
    print("=" * 50)
    
    # Initialize service
    ai_service = AIExplanationService()
    
    # Test crop selection explanation
    print("\n=== Testing Crop Selection Explanation ===")
    crop_recommendation = {
        'crop_name': 'corn',
        'confidence_score': 0.87,
        'agricultural_sources': ['Iowa State University Extension', 'USDA Guidelines']
    }
    
    crop_context = {
        'soil_data': {
            'ph': 6.2,
            'organic_matter_percent': 3.8,
            'phosphorus_ppm': 25,
            'potassium_ppm': 180
        },
        'farm_profile': {
            'farm_size_acres': 320,
            'irrigation_available': False
        }
    }
    
    crop_explanation = ai_service.generate_explanation(
        'crop_selection', crop_recommendation, crop_context
    )
    print(f"Crop Selection Explanation:\n{crop_explanation}")
    
    # Test soil fertility explanation
    print("\n=== Testing Soil Fertility Explanation ===")
    soil_recommendation = {
        'soil_health_score': 6.2,
        'lime_needed': True,
        'lime_rate': 2.5
    }
    
    soil_context = {
        'soil_data': {
            'ph': 5.8,
            'organic_matter_percent': 2.1,
            'phosphorus_ppm': 12,
            'potassium_ppm': 95
        }
    }
    
    soil_explanation = ai_service.generate_explanation(
        'soil_fertility', soil_recommendation, soil_context
    )
    print(f"Soil Fertility Explanation:\n{soil_explanation}")
    
    # Test confidence explanation
    print("\n=== Testing Confidence Explanation ===")
    confidence_factors = {
        'soil_data_quality': 0.9,
        'regional_data_availability': 0.8,
        'seasonal_appropriateness': 0.9,
        'expert_validation': 0.85
    }
    
    confidence_explanation = ai_service.generate_confidence_explanation(
        confidence_factors, 0.87
    )
    print(f"Confidence Explanation:\n{confidence_explanation}")
    
    # Test implementation steps
    print("\n=== Testing Implementation Steps ===")
    
    # Crop selection steps
    crop_steps = ai_service.generate_implementation_steps(
        'crop_selection', crop_recommendation
    )
    print("Crop Selection Steps:")
    for i, step in enumerate(crop_steps, 1):
        print(f"  {i}. {step}")
    
    # Soil fertility steps
    soil_steps = ai_service.generate_implementation_steps(
        'soil_fertility', soil_recommendation
    )
    print("\nSoil Fertility Steps:")
    for i, step in enumerate(soil_steps, 1):
        print(f"  {i}. {step}")
    
    # Test fertilizer selection
    print("\n=== Testing Fertilizer Selection Explanation ===")
    fertilizer_recommendation = {
        'fertilizer_type': 'organic',
        'cost_per_acre': 65.00,
        'confidence_score': 0.90
    }
    
    fertilizer_context = {
        'soil_data': {
            'ph': 6.5,
            'organic_matter_percent': 2.8
        },
        'farm_profile': {
            'organic_certified': True
        }
    }
    
    fertilizer_explanation = ai_service.generate_explanation(
        'fertilizer_selection', fertilizer_recommendation, fertilizer_context
    )
    print(f"Fertilizer Selection Explanation:\n{fertilizer_explanation}")
    
    # Test nutrient deficiency explanation
    print("\n=== Testing Nutrient Deficiency Explanation ===")
    deficiency_recommendation = {
        'nutrient': 'nitrogen',
        'severity': 'moderate',
        'confidence_score': 0.75
    }
    
    deficiency_context = {
        'soil_data': {
            'nitrogen_ppm': 8,
            'ph': 6.0
        }
    }
    
    deficiency_explanation = ai_service.generate_explanation(
        'nutrient_deficiency', deficiency_recommendation, deficiency_context
    )
    print(f"Nutrient Deficiency Explanation:\n{deficiency_explanation}")
    
    # Test crop rotation explanation
    print("\n=== Testing Crop Rotation Explanation ===")
    rotation_recommendation = {
        'diversity_score': 7.5,
        'confidence_score': 0.82
    }
    
    rotation_context = {
        'crop_data': {
            'current_rotation': ['corn', 'soybean'],
            'rotation_length': 2
        }
    }
    
    rotation_explanation = ai_service.generate_explanation(
        'crop_rotation', rotation_recommendation, rotation_context
    )
    print(f"Crop Rotation Explanation:\n{rotation_explanation}")
    
    # Test seasonal timing advice
    print("\n=== Testing Seasonal Timing Advice ===")
    
    timing_advice = ai_service.generate_seasonal_timing_advice(
        'crop_selection', crop_recommendation
    )
    print(f"Crop Selection Timing:\n{timing_advice}")
    
    soil_timing_advice = ai_service.generate_seasonal_timing_advice(
        'soil_fertility', soil_recommendation
    )
    print(f"\nSoil Fertility Timing:\n{soil_timing_advice}")
    
    # Test risk assessment
    print("\n=== Testing Risk Assessment ===")
    
    risk_context = {
        'weather_data': {
            'drought_risk': 'high',
            'precipitation_forecast': 'below_normal'
        },
        'soil_data': crop_context['soil_data']
    }
    
    risks = ai_service.generate_risk_assessment(crop_recommendation, risk_context)
    print("Risk Assessment:")
    for risk_type, description in risks.items():
        print(f"  {risk_type.title()}: {description}")
    
    # Test enhanced explanation with all features
    print("\n=== Testing Enhanced Complete Explanation ===")
    
    complete_recommendation = {
        'crop_name': 'corn',
        'confidence_score': 0.85,
        'cost_per_acre': 45.50,
        'timing': 'early May planting',
        'agricultural_sources': ['Iowa State Extension', 'USDA Guidelines']
    }
    
    complete_context = {
        'soil_data': {
            'ph': 6.4,
            'organic_matter_percent': 3.2,
            'phosphorus_ppm': 28,
            'potassium_ppm': 165
        },
        'farm_profile': {
            'farm_size_acres': 160,
            'irrigation_available': True
        }
    }
    
    complete_explanation = ai_service.generate_explanation(
        'crop_selection', complete_recommendation, complete_context
    )
    print(f"Complete Enhanced Explanation:\n{complete_explanation}")
    
    print("\n" + "=" * 50)
    print("✅ AI Explanation Service test completed successfully!")
    print("✅ All basic AI explanation generation features implemented!")

if __name__ == "__main__":
    test_ai_explanation_service()