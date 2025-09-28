#!/usr/bin/env python3
"""
Unit Tests for AI Explanation Service
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

This module contains comprehensive unit tests for the AI explanation service.
"""

import importlib.util
import os
import sys
from datetime import datetime
from unittest.mock import patch

import pytest

# Load AI explanation service directly to avoid heavy package imports
SRC_DIR = os.path.join(os.path.dirname(__file__), '..', 'src')
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

AI_EXPLANATION_PATH = os.path.join(SRC_DIR, 'services', 'ai_explanation_service.py')
AI_SPEC = importlib.util.spec_from_file_location('ai_explanation_service', AI_EXPLANATION_PATH)
AI_MODULE = importlib.util.module_from_spec(AI_SPEC)
if AI_SPEC and AI_SPEC.loader:
    AI_SPEC.loader.exec_module(AI_MODULE)
    sys.modules['ai_explanation_service'] = AI_MODULE

AIExplanationService = AI_MODULE.AIExplanationService
create_ai_explanation_service = AI_MODULE.create_ai_explanation_service


class TestAIExplanationService:
    """Test cases for AI Explanation Service."""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI explanation service instance for testing."""
        return create_ai_explanation_service()
    
    @pytest.fixture
    def sample_crop_recommendation(self):
        """Sample crop recommendation data."""
        return {
            'crop_name': 'corn',
            'confidence_score': 0.87,
            'agricultural_sources': ['Iowa State University Extension', 'USDA Guidelines'],
            'cost_per_acre': 45.50,
            'timing': 'early May planting',
            'variety_suggestions': [
                {
                    'variety_name': 'Pioneer P1197AM',
                    'maturity_days': 111,
                    'yield_potential_bu_per_acre': 185,
                    'drought_tolerance': 'good',
                    'key_advantages': ['consistent yield performance', 'strong standability']
                },
                {
                    'variety_name': 'Dekalb DKC64-35',
                    'maturity_days': 114,
                    'yield_potential_bu_per_acre': 178,
                    'drought_tolerance': 'very good',
                    'key_advantages': ['enhanced stress tolerance']
                }
            ]
        }
    
    @pytest.fixture
    def sample_context(self):
        """Sample farm context data."""
        return {
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
    
    def test_service_initialization(self, ai_service):
        """Test that AI explanation service initializes correctly."""
        assert ai_service is not None
        assert hasattr(ai_service, 'explanation_templates')
        assert len(ai_service.explanation_templates) > 0
    
    def test_generate_crop_selection_explanation(self, ai_service, sample_crop_recommendation, sample_context):
        """Test crop selection explanation generation."""
        explanation = ai_service.generate_explanation(
            'crop_selection', sample_crop_recommendation, sample_context
        )
        
        assert isinstance(explanation, str)
        assert len(explanation) > 50  # Should be substantial explanation
        assert 'corn' in explanation.lower()
        assert 'suitable' in explanation.lower()
        assert 'ph' in explanation.lower()

        # Should highlight top variety details and trade-off insights
        assert 'Pioneer P1197AM' in explanation
        assert 'variety comparison' in explanation.lower()
        assert 'variety trade-offs' in explanation.lower()

        # Should include source attribution
        assert 'Iowa State' in explanation or 'USDA' in explanation
    
    def test_generate_soil_fertility_explanation(self, ai_service):
        """Test soil fertility explanation generation."""
        soil_recommendation = {
            'soil_health_score': 6.2,
            'lime_needed': True,
            'lime_rate': 2.5,
            'confidence_score': 0.75
        }
        
        soil_context = {
            'soil_data': {
                'ph': 5.8,
                'organic_matter_percent': 2.1,
                'phosphorus_ppm': 12,
                'potassium_ppm': 95
            }
        }
        
        explanation = ai_service.generate_explanation(
            'soil_fertility', soil_recommendation, soil_context
        )
        
        assert isinstance(explanation, str)
        assert '6.2/10' in explanation
        assert 'lime' in explanation.lower()
        assert 'organic matter' in explanation.lower()
    
    def test_generate_confidence_explanation(self, ai_service):
        """Test confidence explanation generation."""
        confidence_factors = {
            'soil_data_quality': 0.9,
            'regional_data_availability': 0.8,
            'seasonal_appropriateness': 0.9,
            'expert_validation': 0.85
        }
        
        explanation = ai_service.generate_confidence_explanation(
            confidence_factors, 0.87
        )
        
        assert isinstance(explanation, str)
        assert 'high confidence' in explanation.lower()
        assert '87%' in explanation
        assert 'expert-validated' in explanation.lower()
    
    def test_confidence_explanation_with_low_confidence(self, ai_service):
        """Test confidence explanation with low confidence factors."""
        confidence_factors = {
            'soil_data_quality': 0.5,
            'regional_data_availability': 0.6,
            'expert_validation': 0.4
        }
        
        explanation = ai_service.generate_confidence_explanation(
            confidence_factors, 0.55
        )
        
        assert isinstance(explanation, str)
        assert 'low confidence' in explanation.lower()
        assert 'limited' in explanation.lower() or 'reduced' in explanation.lower()
    
    def test_generate_implementation_steps_crop_selection(self, ai_service, sample_crop_recommendation):
        """Test implementation steps for crop selection."""
        steps = ai_service.generate_implementation_steps(
            'crop_selection', sample_crop_recommendation
        )
        
        assert isinstance(steps, list)
        assert len(steps) >= 5
        assert any('soil' in step.lower() for step in steps)
        assert any('variety' in step.lower() for step in steps)
        assert any('nitrogen' in step.lower() for step in steps)  # Corn-specific

        alignment_step_found = False
        for step in steps:
            if 'align yield goals' in step.lower():
                alignment_step_found = True
        assert alignment_step_found
    
    def test_generate_implementation_steps_soil_fertility(self, ai_service):
        """Test implementation steps for soil fertility."""
        soil_recommendation = {
            'lime_needed': True,
            'lime_rate': 2.5
        }
        
        steps = ai_service.generate_implementation_steps(
            'soil_fertility', soil_recommendation
        )
        
        assert isinstance(steps, list)
        assert len(steps) >= 5
        assert any('soil test' in step.lower() for step in steps)
        assert any('2.5 tons/acre' in step for step in steps)
        assert any('lime' in step.lower() for step in steps)
    
    def test_seasonal_timing_advice(self, ai_service, sample_crop_recommendation):
        """Test seasonal timing advice generation."""
        # Test different seasons by mocking datetime
        with patch('ai_explanation_service.datetime') as mock_datetime:
            # Test spring planting season (May)
            mock_datetime.now.return_value.month = 5
            
            timing_advice = ai_service.generate_seasonal_timing_advice(
                'crop_selection', sample_crop_recommendation
            )
            
            assert isinstance(timing_advice, str)
            assert len(timing_advice) > 20
            assert 'corn' in timing_advice.lower() or 'planting' in timing_advice.lower()
    
    def test_risk_assessment(self, ai_service, sample_crop_recommendation):
        """Test risk assessment generation."""
        risk_context = {
            'weather_data': {
                'drought_risk': 'high',
                'precipitation_forecast': 'below_normal'
            },
            'soil_data': {
                'ph': 6.2,
                'organic_matter_percent': 3.8
            }
        }
        
        risks = ai_service.generate_risk_assessment(sample_crop_recommendation, risk_context)
        
        assert isinstance(risks, dict)
        assert 'weather' in risks
        assert 'drought' in risks['weather'].lower()
    
    def test_risk_assessment_low_confidence(self, ai_service):
        """Test risk assessment with low confidence recommendation."""
        low_confidence_rec = {
            'confidence_score': 0.6,
            'cost_per_acre': 150.0
        }
        
        context = {'soil_data': {'ph': 6.0}}
        
        risks = ai_service.generate_risk_assessment(low_confidence_rec, context)
        
        assert isinstance(risks, dict)
        assert 'recommendation' in risks or 'economic' in risks
    
    def test_fertilizer_selection_explanation(self, ai_service):
        """Test fertilizer selection explanation."""
        fertilizer_rec = {
            'fertilizer_type': 'organic',
            'cost_per_acre': 65.00,
            'confidence_score': 0.90
        }
        
        context = {
            'farm_profile': {
                'organic_certified': True
            },
            'soil_data': {
                'ph': 6.5,
                'organic_matter_percent': 2.8
            }
        }
        
        explanation = ai_service.generate_explanation(
            'fertilizer_selection', fertilizer_rec, context
        )
        
        assert isinstance(explanation, str)
        assert 'organic' in explanation.lower()
        assert '$65.00/acre' in explanation
        assert 'certification' in explanation.lower()
    
    def test_nutrient_deficiency_explanation(self, ai_service):
        """Test nutrient deficiency explanation."""
        deficiency_rec = {
            'nutrient': 'nitrogen',
            'severity': 'moderate',
            'confidence_score': 0.75
        }
        
        context = {
            'soil_data': {
                'nitrogen_ppm': 8,
                'ph': 6.0
            }
        }
        
        explanation = ai_service.generate_explanation(
            'nutrient_deficiency', deficiency_rec, context
        )
        
        assert isinstance(explanation, str)
        assert 'nitrogen' in explanation.lower()
        assert 'moderate' in explanation.lower()
        assert 'fertilizer' in explanation.lower()
    
    def test_crop_rotation_explanation(self, ai_service):
        """Test crop rotation explanation."""
        rotation_rec = {
            'diversity_score': 7.5,
            'confidence_score': 0.82
        }
        
        context = {
            'crop_data': {
                'current_rotation': ['corn', 'soybean'],
                'rotation_length': 2
            }
        }
        
        explanation = ai_service.generate_explanation(
            'crop_rotation', rotation_rec, context
        )
        
        assert isinstance(explanation, str)
        assert '7.5/10' in explanation
        assert 'diversity' in explanation.lower()
        assert 'third crop' in explanation.lower()
    
    def test_error_handling_invalid_recommendation_type(self, ai_service):
        """Test error handling for invalid recommendation type."""
        explanation = ai_service.generate_explanation(
            'invalid_type', {}, {}
        )
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert 'agricultural best practices' in explanation.lower()
    
    def test_error_handling_missing_data(self, ai_service):
        """Test error handling for missing data."""
        # Test with empty recommendation data
        explanation = ai_service.generate_explanation(
            'crop_selection', {}, {}
        )
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
    
    def test_confidence_level_mapping(self, ai_service):
        """Test confidence level mapping."""
        assert ai_service._get_confidence_level(0.9) == "high"
        assert ai_service._get_confidence_level(0.7) == "moderate"
        assert ai_service._get_confidence_level(0.5) == "low"
        assert ai_service._get_confidence_level(0.3) == "very low"
    
    def test_template_variable_generation(self, ai_service):
        """Test template variable generation."""
        recommendation_data = {
            'crop_name': 'corn',
            'confidence_score': 0.85,
            'soil_health_score': 7.2
        }
        
        context = {
            'soil_data': {
                'ph': 6.5,
                'organic_matter_percent': 3.5,
                'phosphorus_ppm': 30,
                'potassium_ppm': 200
            }
        }
        
        variables = ai_service._generate_assessment_variables(recommendation_data, context)
        
        assert isinstance(variables, dict)
        assert 'ph_assessment' in variables
        assert 'suitability_level' in variables
        assert variables['ph_assessment'] == 'optimal'
        assert variables['suitability_level'] == 'highly suitable'
    
    def test_factory_function(self):
        """Test factory function creates service correctly."""
        service = create_ai_explanation_service()
        assert isinstance(service, AIExplanationService)
        assert hasattr(service, 'explanation_templates')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
