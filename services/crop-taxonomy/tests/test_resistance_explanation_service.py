"""
Comprehensive Tests for Resistance Explanation Service

Tests for the resistance recommendation explanations and educational content service.
Covers resistance mechanism explanations, educational content, stewardship guidelines,
and integration with the AI explanation service.

TICKET-005_crop-variety-recommendations-10.3: Add comprehensive resistance recommendation explanations and education
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import Dict, List, Any

from services.resistance_explanation_service import (
    ResistanceExplanationService,
    ResistanceType,
    ResistanceMechanism,
    StewardshipLevel
)


class TestResistanceExplanationService:
    """Test suite for the resistance explanation service."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return ResistanceExplanationService()
    
    @pytest.fixture
    def sample_variety_data(self):
        """Sample variety data with resistance traits."""
        return {
            "variety_id": "test_variety_001",
            "variety_name": "Test Corn Variety",
            "bt_traits": [
                {
                    "name": "Cry1Ab",
                    "target_pests": ["corn_borer", "corn_rootworm"],
                    "mechanism": "Protein inhibition",
                    "efficacy": "High"
                }
            ],
            "herbicide_tolerance": [
                {
                    "name": "Roundup Ready",
                    "target_herbicides": ["glyphosate"],
                    "mechanism": "Metabolic detoxification",
                    "efficacy": "High"
                }
            ],
            "disease_resistance": [
                {
                    "name": "Rust Resistance",
                    "target_diseases": ["rust", "blight"],
                    "mechanism": "Structural modification",
                    "efficacy": "Medium"
                }
            ]
        }
    
    @pytest.fixture
    def sample_pest_resistance_data(self):
        """Sample pest resistance analysis data."""
        return {
            "regional_pressure": {
                "current_pressure": "Medium",
                "historical_trends": ["Stable", "Increasing"],
                "resistance_development": "Not detected"
            },
            "data_quality_score": 0.8,
            "confidence_level": 0.85
        }
    
    @pytest.fixture
    def sample_context(self):
        """Sample farm and environmental context."""
        return {
            "location": {
                "latitude": 40.0,
                "longitude": -95.0,
                "state": "Iowa",
                "region": "Midwest"
            },
            "climate": {
                "zone": "5a",
                "hardiness_zone": "5a"
            },
            "farm_size": 100,
            "soil_type": "clay_loam"
        }
    
    def test_service_initialization(self, service):
        """Test service initialization and knowledge base setup."""
        assert service is not None
        assert hasattr(service, 'resistance_knowledge_base')
        assert hasattr(service, 'educational_content')
        assert hasattr(service, 'stewardship_guidelines')
        assert hasattr(service, 'regulatory_requirements')
        
        # Test knowledge base content
        assert 'bt_toxin' in service.resistance_knowledge_base
        assert 'herbicide_tolerance' in service.resistance_knowledge_base
        assert 'disease_resistance' in service.resistance_knowledge_base
        
        # Test educational content
        assert 'resistance_management_principles' in service.educational_content
        assert 'stewardship_best_practices' in service.educational_content
        assert 'durability_factors' in service.educational_content
    
    @pytest.mark.asyncio
    async def test_generate_resistance_explanation_success(
        self, 
        service, 
        sample_variety_data, 
        sample_pest_resistance_data, 
        sample_context
    ):
        """Test successful resistance explanation generation."""
        explanation = await service.generate_resistance_explanation(
            variety_data=sample_variety_data,
            pest_resistance_data=sample_pest_resistance_data,
            context=sample_context
        )
        
        # Test response structure
        assert 'explanation_id' in explanation
        assert 'variety_id' in explanation
        assert 'variety_name' in explanation
        assert 'resistance_traits' in explanation
        assert 'explanation_sections' in explanation
        assert 'educational_content' in explanation
        assert 'stewardship_guidelines' in explanation
        assert 'management_recommendations' in explanation
        assert 'durability_assessment' in explanation
        assert 'compliance_requirements' in explanation
        assert 'generated_at' in explanation
        assert 'confidence_score' in explanation
        
        # Test resistance traits extraction
        resistance_traits = explanation['resistance_traits']
        assert len(resistance_traits) == 3  # Bt, herbicide, disease traits
        
        # Test explanation sections
        explanation_sections = explanation['explanation_sections']
        assert 'mechanism_explanations' in explanation_sections
        assert 'pest_pressure_analysis' in explanation_sections
        assert 'resistance_effectiveness' in explanation_sections
        assert 'risk_assessment' in explanation_sections
    
    def test_extract_resistance_traits(self, service, sample_variety_data):
        """Test resistance traits extraction from variety data."""
        traits = service._extract_resistance_traits(sample_variety_data)
        
        assert len(traits) == 3
        
        # Test Bt trait extraction
        bt_traits = [t for t in traits if t['type'] == ResistanceType.BT_TOXIN]
        assert len(bt_traits) == 1
        assert bt_traits[0]['trait_name'] == 'Cry1Ab'
        assert bt_traits[0]['target_pests'] == ['corn_borer', 'corn_rootworm']
        
        # Test herbicide tolerance extraction
        herbicide_traits = [t for t in traits if t['type'] == ResistanceType.HERBICIDE_TOLERANCE]
        assert len(herbicide_traits) == 1
        assert herbicide_traits[0]['trait_name'] == 'Roundup Ready'
        assert herbicide_traits[0]['target_herbicides'] == ['glyphosate']
        
        # Test disease resistance extraction
        disease_traits = [t for t in traits if t['type'] == ResistanceType.DISEASE_RESISTANCE]
        assert len(disease_traits) == 1
        assert disease_traits[0]['trait_name'] == 'Rust Resistance'
        assert disease_traits[0]['target_diseases'] == ['rust', 'blight']
    
    def test_explain_resistance_mechanisms(self, service):
        """Test resistance mechanism explanations."""
        resistance_traits = [
            {
                "type": ResistanceType.BT_TOXIN,
                "trait_name": "Cry1Ab"
            },
            {
                "type": ResistanceType.HERBICIDE_TOLERANCE,
                "trait_name": "Roundup Ready"
            }
        ]
        
        explanations = service._explain_resistance_mechanisms(resistance_traits)
        
        assert 'Cry1Ab' in explanations
        assert 'Roundup Ready' in explanations
        
        # Test Bt mechanism explanation
        bt_explanation = explanations['Cry1Ab']
        assert bt_explanation['mechanism'] == 'Protein inhibition'
        assert 'corn_borer' in bt_explanation['target_organisms']
        assert bt_explanation['durability'] == 'High when properly managed with refuge requirements'
        
        # Test herbicide mechanism explanation
        herbicide_explanation = explanations['Roundup Ready']
        assert herbicide_explanation['mechanism'] == 'Metabolic detoxification'
        assert herbicide_explanation['durability'] == 'Variable - depends on herbicide and management'
    
    def test_analyze_pest_pressure(self, service, sample_pest_resistance_data, sample_context):
        """Test pest pressure analysis."""
        analysis = service._analyze_pest_pressure(sample_pest_resistance_data, sample_context)
        
        assert 'current_pest_pressure' in analysis
        assert 'historical_trends' in analysis
        assert 'resistance_development' in analysis
        assert 'management_implications' in analysis
        assert 'monitoring_recommendations' in analysis
        
        assert analysis['current_pest_pressure'] == 'Medium'
        assert analysis['historical_trends'] == ['Stable', 'Increasing']
        assert analysis['resistance_development'] == 'Not detected'
    
    def test_assess_resistance_effectiveness(self, service, sample_pest_resistance_data):
        """Test resistance effectiveness assessment."""
        resistance_traits = [
            {
                "type": ResistanceType.BT_TOXIN,
                "trait_name": "Cry1Ab",
                "efficacy": "High"
            }
        ]
        
        effectiveness = service._assess_resistance_effectiveness(resistance_traits, sample_pest_resistance_data)
        
        assert 'Cry1Ab' in effectiveness
        cry_effectiveness = effectiveness['Cry1Ab']
        assert cry_effectiveness['overall_effectiveness'] == 'High'
        assert 'target_pest_coverage' in cry_effectiveness
        assert 'resistance_durability' in cry_effectiveness
        assert 'management_requirements' in cry_effectiveness
    
    def test_assess_resistance_risks(self, service, sample_context):
        """Test resistance risk assessment."""
        resistance_traits = [
            {
                "type": ResistanceType.BT_TOXIN,
                "trait_name": "Cry1Ab"
            },
            {
                "type": ResistanceType.HERBICIDE_TOLERANCE,
                "trait_name": "Roundup Ready"
            }
        ]
        
        risks = service._assess_resistance_risks(resistance_traits, sample_context)
        
        assert 'resistance_development_risk' in risks
        assert 'environmental_risks' in risks
        assert 'economic_risks' in risks
        assert 'regulatory_risks' in risks
        assert 'mitigation_strategies' in risks
        
        assert risks['resistance_development_risk'] in ['Low', 'Medium', 'High']
        assert isinstance(risks['environmental_risks'], list)
        assert isinstance(risks['mitigation_strategies'], list)
    
    def test_generate_educational_content(self, service, sample_context):
        """Test educational content generation."""
        resistance_traits = [
            {
                "type": ResistanceType.BT_TOXIN,
                "trait_name": "Cry1Ab"
            }
        ]
        
        content = service._generate_educational_content(resistance_traits, sample_context)
        
        assert 'resistance_management_principles' in content
        assert 'stewardship_best_practices' in content
        assert 'durability_factors' in content
        assert 'trait_specific_education' in content
        
        # Test trait-specific education
        trait_education = content['trait_specific_education']
        assert 'Cry1Ab' in trait_education
        cry_education = trait_education['Cry1Ab']
        assert 'mechanism_explanation' in cry_education
        assert 'management_guidance' in cry_education
        assert 'monitoring_requirements' in cry_education
        assert 'compliance_requirements' in cry_education
    
    def test_generate_stewardship_guidelines(self, service, sample_context):
        """Test stewardship guidelines generation."""
        resistance_traits = [
            {
                "type": ResistanceType.BT_TOXIN,
                "trait_name": "Cry1Ab"
            }
        ]
        
        guidelines = service._generate_stewardship_guidelines(resistance_traits, sample_context)
        
        assert 'refuge_requirements' in guidelines
        assert 'monitoring_requirements' in guidelines
        assert 'documentation_requirements' in guidelines
        assert 'compliance_checklist' in guidelines
        
        # Test refuge requirements for Bt crops
        refuge_reqs = guidelines['refuge_requirements']
        assert 'corn' in refuge_reqs
        assert 'structured_refuge' in refuge_reqs['corn']
        assert 'in_field_refuge' in refuge_reqs['corn']
    
    def test_generate_management_recommendations(self, service, sample_pest_resistance_data, sample_context):
        """Test management recommendations generation."""
        resistance_traits = [
            {
                "type": ResistanceType.BT_TOXIN,
                "trait_name": "Cry1Ab"
            }
        ]
        
        recommendations = service._generate_management_recommendations(
            resistance_traits, sample_pest_resistance_data, sample_context
        )
        
        assert 'immediate_actions' in recommendations
        assert 'seasonal_management' in recommendations
        assert 'long_term_strategy' in recommendations
        assert 'monitoring_schedule' in recommendations
        assert 'record_keeping' in recommendations
        
        assert isinstance(recommendations['immediate_actions'], list)
        assert isinstance(recommendations['seasonal_management'], list)
        assert isinstance(recommendations['long_term_strategy'], list)
    
    def test_generate_durability_assessment(self, service, sample_context):
        """Test durability assessment generation."""
        resistance_traits = [
            {
                "type": ResistanceType.BT_TOXIN,
                "trait_name": "Cry1Ab"
            }
        ]
        
        assessment = service._generate_durability_assessment(resistance_traits, sample_context)
        
        assert 'overall_durability' in assessment
        assert 'durability_factors' in assessment
        assert 'durability_timeline' in assessment
        assert 'sustainability_score' in assessment
        
        assert assessment['overall_durability'] in ['Low', 'Medium', 'High']
        assert isinstance(assessment['durability_timeline'], dict)
        assert isinstance(assessment['sustainability_score'], float)
        assert 0.0 <= assessment['sustainability_score'] <= 1.0
    
    def test_generate_compliance_requirements(self, service, sample_context):
        """Test compliance requirements generation."""
        resistance_traits = [
            {
                "type": ResistanceType.BT_TOXIN,
                "trait_name": "Cry1Ab"
            }
        ]
        
        requirements = service._generate_compliance_requirements(resistance_traits, sample_context)
        
        assert 'usda_requirements' in requirements
        assert 'epa_requirements' in requirements
        assert 'state_requirements' in requirements
        assert 'label_requirements' in requirements
        assert 'documentation_requirements' in requirements
        
        assert isinstance(requirements['usda_requirements'], list)
        assert isinstance(requirements['epa_requirements'], list)
        assert isinstance(requirements['state_requirements'], list)
    
    def test_calculate_confidence_score(self, service, sample_pest_resistance_data):
        """Test confidence score calculation."""
        resistance_traits = [
            {
                "type": ResistanceType.BT_TOXIN,
                "trait_name": "Cry1Ab"
            }
        ]
        
        confidence = service._calculate_confidence_score(resistance_traits, sample_pest_resistance_data)
        
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
        
        # Test with high-quality data
        high_quality_data = sample_pest_resistance_data.copy()
        high_quality_data['data_quality_score'] = 0.9
        
        high_confidence = service._calculate_confidence_score(resistance_traits, high_quality_data)
        assert high_confidence > confidence
    
    def test_helper_methods(self, service):
        """Test helper methods."""
        # Test durability scoring
        assert service._score_durability("High") == 0.9
        assert service._score_durability("Medium") == 0.6
        assert service._score_durability("Low") == 0.3
        assert service._score_durability("Unknown") == 0.5
        
        # Test overall durability calculation
        scores = [0.9, 0.8, 0.7]
        overall = service._calculate_overall_durability(scores)
        assert overall == "High"
        
        scores = [0.5, 0.6, 0.4]
        overall = service._calculate_overall_durability(scores)
        assert overall == "Low"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling in explanation generation."""
        # Test with invalid variety data
        invalid_variety_data = None
        
        with pytest.raises(Exception):
            await service.generate_resistance_explanation(
                variety_data=invalid_variety_data,
                pest_resistance_data={},
                context={}
            )
    
    def test_resistance_knowledge_base_content(self, service):
        """Test resistance knowledge base content quality."""
        knowledge_base = service.resistance_knowledge_base
        
        for trait_type, knowledge in knowledge_base.items():
            assert 'mechanism' in knowledge
            assert 'description' in knowledge
            assert 'durability' in knowledge
            assert 'resistance_risk' in knowledge
            assert 'management_strategy' in knowledge
            
            # Test that descriptions are informative
            assert len(knowledge['description']) > 20
            assert len(knowledge['management_strategy']) > 10
    
    def test_educational_content_quality(self, service):
        """Test educational content quality."""
        educational_content = service.educational_content
        
        for content_type, content in educational_content.items():
            assert 'title' in content
            assert 'content' in content
            assert isinstance(content['content'], list)
            assert len(content['content']) > 0
            
            # Test that content items are informative
            for item in content['content']:
                assert len(item) > 10
    
    def test_stewardship_guidelines_quality(self, service):
        """Test stewardship guidelines quality."""
        guidelines = service.stewardship_guidelines
        
        assert 'bt_crops' in guidelines
        assert 'herbicide_tolerant_crops' in guidelines
        
        # Test Bt crop guidelines
        bt_guidelines = guidelines['bt_crops']
        assert 'refuge_requirements' in bt_guidelines
        assert 'compliance_monitoring' in bt_guidelines
        
        # Test herbicide guidelines
        herbicide_guidelines = guidelines['herbicide_tolerant_crops']
        assert 'resistance_management' in herbicide_guidelines
        assert 'compliance_requirements' in herbicide_guidelines
    
    def test_regulatory_requirements_quality(self, service):
        """Test regulatory requirements quality."""
        requirements = service.regulatory_requirements
        
        assert 'usda_requirements' in requirements
        assert 'epa_requirements' in requirements
        assert 'state_requirements' in requirements
        
        # Test USDA requirements
        usda_reqs = requirements['usda_requirements']
        assert 'bt_crops' in usda_reqs
        assert 'herbicide_tolerant_crops' in usda_reqs
        
        # Test EPA requirements
        epa_reqs = requirements['epa_requirements']
        assert 'pesticide_resistance' in epa_reqs


class TestResistanceExplanationIntegration:
    """Test integration with AI explanation service."""
    
    @pytest.fixture
    def variety_explanation_service(self):
        """Create variety explanation service with resistance integration."""
        from services.variety_explanation_service import VarietyExplanationService
        return VarietyExplanationService()
    
    def test_resistance_explanation_integration(self, variety_explanation_service):
        """Test integration of resistance explanations in variety explanation service."""
        # Test that resistance explanation service is initialized
        assert hasattr(variety_explanation_service, 'resistance_explanation_service')
        
        # Test that resistance heading is added to supported languages
        assert 'resistance_heading' in variety_explanation_service.supported_languages['en']
        assert 'resistance_heading' in variety_explanation_service.supported_languages['es']
        assert 'resistance_heading' in variety_explanation_service.supported_languages['fr']
    
    def test_build_resistance_explanations_method(self, variety_explanation_service):
        """Test the _build_resistance_explanations method."""
        # Test with varieties containing resistance traits
        varieties = [
            {
                "raw": {
                    "variety_id": "test_001",
                    "variety_name": "Test Variety",
                    "bt_traits": [
                        {
                            "name": "Cry1Ab",
                            "target_pests": ["corn_borer"],
                            "mechanism": "Protein inhibition"
                        }
                    ]
                }
            }
        ]
        
        context = {"location": {"state": "Iowa"}}
        
        resistance_explanations = variety_explanation_service._build_resistance_explanations(
            varieties, context
        )
        
        assert 'has_resistance_traits' in resistance_explanations
        assert 'resistance_summary' in resistance_explanations
        assert 'educational_content' in resistance_explanations
        assert 'stewardship_guidelines' in resistance_explanations
        assert 'management_recommendations' in resistance_explanations
        
        # Test that resistance traits are detected
        if variety_explanation_service.resistance_explanation_service:
            assert resistance_explanations['has_resistance_traits'] == True
            assert len(resistance_explanations['resistance_summary']) > 0
        else:
            # Service not available, should handle gracefully
            assert "not available" in resistance_explanations['resistance_summary'][0]


class TestResistanceExplanationAPI:
    """Test API endpoints for resistance explanations."""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        from fastapi.testclient import TestClient
        from api.resistance_explanation_routes import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/resistance-explanations/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "resistance-explanations"
        assert "version" in data
        assert "features" in data
    
    def test_mechanism_explanations_endpoint(self, client):
        """Test mechanism explanations endpoint."""
        response = client.get(
            "/api/v1/resistance-explanations/mechanism-explanations",
            params={"resistance_type": "bt_toxin", "include_details": True}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["resistance_type"] == "bt_toxin"
        assert "mechanism" in data
        assert "description" in data
        assert "durability" in data
        assert "resistance_risk" in data
        assert "management_strategy" in data
        
        # Test with invalid resistance type
        response = client.get(
            "/api/v1/resistance-explanations/mechanism-explanations",
            params={"resistance_type": "invalid_type"}
        )
        assert response.status_code == 404
    
    def test_compliance_requirements_endpoint(self, client):
        """Test compliance requirements endpoint."""
        response = client.get(
            "/api/v1/resistance-explanations/compliance-requirements",
            params={"resistance_traits": ["bt_toxin"], "region": "US"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "resistance_traits" in data
        assert "region" in data
        assert "compliance_requirements" in data
        assert "generated_at" in data
    
    def test_durability_assessment_endpoint(self, client):
        """Test durability assessment endpoint."""
        response = client.get(
            "/api/v1/resistance-explanations/durability-assessment",
            params={"resistance_traits": ["bt_toxin"], "context": {}}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "resistance_traits" in data
        assert "durability_assessment" in data
        assert "generated_at" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])