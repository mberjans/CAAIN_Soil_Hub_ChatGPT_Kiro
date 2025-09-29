"""
Tests for Comprehensive Explanation Service
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch

from src.services.comprehensive_explanation_service import (
    ComprehensiveExplanationService,
    ExplanationType,
    ConfidenceLevel,
    EvidenceItem,
    ExplanationSection,
    ComprehensiveExplanation
)

class TestComprehensiveExplanationService:
    """Test suite for comprehensive explanation service."""

    @pytest.fixture
    def explanation_service(self):
        """Create explanation service instance."""
        return ComprehensiveExplanationService()

    @pytest.fixture
    def sample_variety_data(self):
        """Sample variety data for testing."""
        return {
            "variety_id": "test-variety-1",
            "variety_name": "Test Corn Variety",
            "request_id": "test_request_123",
            "overall_score": 0.85,
            "scores": {
                "yield_potential": 0.88,
                "disease_resistance": 0.92,
                "soil_compatibility": 0.85,
                "market_acceptance": 0.80
            },
            "data_completeness": 0.9,
            "testing_years": 4,
            "trial_yield": 185,
            "trial_years": 3,
            "farmer_satisfaction": 87,
            "resistant_diseases": ["Northern Corn Leaf Blight", "Gray Leaf Spot"],
            "disease_cost_savings": 35,
            "strengths": ["High yield potential", "Strong disease resistance"],
            "considerations": ["Higher seed cost", "Requires careful management"],
            "risk_level": "low",
            "risk_factors": [
                {"factor": "Weather Sensitivity", "level": "Low", "description": "Good stability"},
                {"factor": "Management Risk", "level": "Medium", "description": "Requires attention"}
            ],
            "mitigation_strategies": ["Precision nitrogen management", "Regular monitoring"],
            "estimated_roi": 1.35,
            "break_even_yield": 165.5,
            "premium_potential": 0.15,
            "cost_analysis": {
                "seed_cost_per_acre": 145.00,
                "additional_inputs": 25.00,
                "total_investment": 170.00
            },
            "planting_recommendations": [
                "Plant when soil temperature reaches 50°F",
                "Optimal planting depth: 1.5-2 inches"
            ],
            "fertilizer_recommendations": [
                "Apply nitrogen in split applications",
                "Monitor soil phosphorus levels"
            ],
            "pest_recommendations": [
                "Monitor for early season insects",
                "Scout regularly for disease symptoms"
            ]
        }

    @pytest.fixture
    def sample_context(self):
        """Sample context data for testing."""
        return {
            "location": {"latitude": 41.8781, "longitude": -87.6298},
            "soil_data": {"ph": 6.5, "organic_matter": 3.2, "texture": "loam"},
            "climate_zone": "5b",
            "region": "Midwest",
            "soil_type": "loam",
            "regional_data_quality": 0.8
        }

    @pytest.fixture
    def sample_explanation_options(self):
        """Sample explanation options for testing."""
        return {
            "include_detailed_reasoning": True,
            "include_evidence": True,
            "include_trade_offs": True,
            "include_risk_analysis": True,
            "include_economic_analysis": True,
            "include_management_guidance": True,
            "explanation_style": "comprehensive",
            "max_sections": 7
        }

    @pytest.mark.asyncio
    async def test_generate_comprehensive_explanation(
        self, 
        explanation_service, 
        sample_variety_data, 
        sample_context, 
        sample_explanation_options
    ):
        """Test comprehensive explanation generation."""
        explanation = await explanation_service.generate_comprehensive_explanation(
            variety_data=sample_variety_data,
            context=sample_context,
            explanation_options=sample_explanation_options
        )

        assert isinstance(explanation, ComprehensiveExplanation)
        assert explanation.variety_id == "test-variety-1"
        assert explanation.variety_name == "Test Corn Variety"
        assert explanation.request_id == "test_request_123"
        assert 0 <= explanation.overall_confidence <= 1
        assert len(explanation.sections) > 0
        assert len(explanation.key_insights) > 0
        assert len(explanation.recommendations) > 0
        assert len(explanation.educational_resources) > 0
        assert "aria_labels" in explanation.accessibility_features

    def test_calculate_overall_confidence(self, explanation_service, sample_variety_data, sample_context):
        """Test overall confidence calculation."""
        confidence = explanation_service._calculate_overall_confidence(sample_variety_data, sample_context)
        
        assert 0 <= confidence <= 1
        assert confidence > 0.5  # Should be reasonably high for good data

    def test_create_summary_section(self, explanation_service, sample_variety_data, sample_context):
        """Test summary section creation."""
        section = explanation_service._create_summary_section(sample_variety_data, sample_context)
        
        assert isinstance(section, ExplanationSection)
        assert section.section_id == "summary"
        assert section.title == "Recommendation Summary"
        assert section.explanation_type == ExplanationType.SUMMARY
        assert len(section.evidence_items) > 0
        assert not section.expandable  # Summary should not be expandable

    def test_create_detailed_reasoning_section(self, explanation_service, sample_variety_data, sample_context):
        """Test detailed reasoning section creation."""
        section = explanation_service._create_detailed_reasoning_section(sample_variety_data, sample_context)
        
        assert isinstance(section, ExplanationSection)
        assert section.section_id == "detailed_reasoning"
        assert section.title == "Detailed Reasoning"
        assert section.explanation_type == ExplanationType.DETAILED_REASONING
        assert section.expandable
        assert len(section.evidence_items) > 0

    def test_create_evidence_section(self, explanation_service, sample_variety_data, sample_context):
        """Test evidence section creation."""
        section = explanation_service._create_evidence_section(sample_variety_data, sample_context)
        
        assert isinstance(section, ExplanationSection)
        assert section.section_id == "evidence"
        assert section.title == "Supporting Evidence"
        assert section.explanation_type == ExplanationType.EVIDENCE_BASED
        assert section.expandable
        assert len(section.evidence_items) > 0
        assert len(section.interactive_elements) > 0

    def test_create_trade_off_section(self, explanation_service, sample_variety_data, sample_context):
        """Test trade-off analysis section creation."""
        section = explanation_service._create_trade_off_section(sample_variety_data, sample_context)
        
        assert isinstance(section, ExplanationSection)
        assert section.section_id == "trade_offs"
        assert section.title == "Trade-off Analysis"
        assert section.explanation_type == ExplanationType.TRADE_OFF_ANALYSIS
        assert section.expandable
        assert len(section.interactive_elements) > 0

    def test_create_risk_assessment_section(self, explanation_service, sample_variety_data, sample_context):
        """Test risk assessment section creation."""
        section = explanation_service._create_risk_assessment_section(sample_variety_data, sample_context)
        
        assert isinstance(section, ExplanationSection)
        assert section.section_id == "risk_assessment"
        assert section.title == "Risk Assessment"
        assert section.explanation_type == ExplanationType.RISK_ASSESSMENT
        assert section.expandable
        assert len(section.evidence_items) > 0

    def test_create_economic_analysis_section(self, explanation_service, sample_variety_data, sample_context):
        """Test economic analysis section creation."""
        section = explanation_service._create_economic_analysis_section(sample_variety_data, sample_context)
        
        assert isinstance(section, ExplanationSection)
        assert section.section_id == "economic_analysis"
        assert section.title == "Economic Analysis"
        assert section.explanation_type == ExplanationType.ECONOMIC_ANALYSIS
        assert section.expandable
        assert len(section.interactive_elements) > 0

    def test_create_management_guidance_section(self, explanation_service, sample_variety_data, sample_context):
        """Test management guidance section creation."""
        section = explanation_service._create_management_guidance_section(sample_variety_data, sample_context)
        
        assert isinstance(section, ExplanationSection)
        assert section.section_id == "management_guidance"
        assert section.title == "Management Guidance"
        assert section.explanation_type == ExplanationType.MANAGEMENT_GUIDANCE
        assert section.expandable
        assert len(section.evidence_items) > 0

    def test_identify_primary_recommendation_factor(self, explanation_service, sample_variety_data):
        """Test primary recommendation factor identification."""
        factor = explanation_service._identify_primary_recommendation_factor(sample_variety_data)
        
        assert isinstance(factor, str)
        assert len(factor) > 0
        # Should identify yield potential as primary factor based on high score
        assert "yield" in factor.lower() or "disease" in factor.lower()

    def test_get_confidence_level(self, explanation_service):
        """Test confidence level conversion."""
        assert explanation_service._get_confidence_level(0.9) == ConfidenceLevel.HIGH
        assert explanation_service._get_confidence_level(0.7) == ConfidenceLevel.MEDIUM
        assert explanation_service._get_confidence_level(0.5) == ConfidenceLevel.LOW
        assert explanation_service._get_confidence_level(0.3) == ConfidenceLevel.VERY_LOW

    def test_generate_summary(self, explanation_service, sample_variety_data, sample_context):
        """Test summary generation."""
        summary = explanation_service._generate_summary(sample_variety_data, sample_context)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "Test Corn Variety" in summary

    def test_generate_key_insights(self, explanation_service, sample_variety_data, sample_context):
        """Test key insights generation."""
        insights = explanation_service._generate_key_insights(sample_variety_data, sample_context)
        
        assert isinstance(insights, list)
        assert len(insights) > 0
        for insight in insights:
            assert isinstance(insight, str)
            assert len(insight) > 0

    def test_generate_recommendations(self, explanation_service, sample_variety_data, sample_context):
        """Test recommendations generation."""
        recommendations = explanation_service._generate_recommendations(sample_variety_data, sample_context)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        for recommendation in recommendations:
            assert isinstance(recommendation, str)
            assert len(recommendation) > 0

    def test_get_educational_resources(self, explanation_service, sample_variety_data, sample_context):
        """Test educational resources generation."""
        resources = explanation_service._get_educational_resources(sample_variety_data, sample_context)
        
        assert isinstance(resources, list)
        assert len(resources) > 0
        for resource in resources:
            assert "title" in resource
            assert "url" in resource
            assert "type" in resource

    def test_prepare_accessibility_features(self, explanation_service):
        """Test accessibility features preparation."""
        sections = [
            ExplanationSection(
                section_id="test1",
                title="Test Section 1",
                content="Test content",
                explanation_type=ExplanationType.SUMMARY,
                confidence_level=ConfidenceLevel.HIGH,
                evidence_items=[],
                expandable=True
            ),
            ExplanationSection(
                section_id="test2",
                title="Test Section 2",
                content="Test content",
                explanation_type=ExplanationType.DETAILED_REASONING,
                confidence_level=ConfidenceLevel.MEDIUM,
                evidence_items=[],
                expandable=False
            )
        ]
        
        features = explanation_service._prepare_accessibility_features(sections)
        
        assert "aria_labels" in features
        assert "keyboard_navigation" in features
        assert "screen_reader_support" in features
        assert "high_contrast_mode" in features
        assert len(features["aria_labels"]) >= 2
        assert len(features["keyboard_navigation"]["sections"]) == 2

    def test_explanation_templates_loaded(self, explanation_service):
        """Test that explanation templates are loaded."""
        assert hasattr(explanation_service, 'explanation_templates')
        assert len(explanation_service.explanation_templates) > 0
        assert "high_yield_variety" in explanation_service.explanation_templates
        assert "disease_resistant_variety" in explanation_service.explanation_templates
        assert "premium_quality_variety" in explanation_service.explanation_templates

    def test_educational_content_loaded(self, explanation_service):
        """Test that educational content is loaded."""
        assert hasattr(explanation_service, 'educational_content')
        assert len(explanation_service.educational_content) > 0
        assert "yield_potential" in explanation_service.educational_content
        assert "disease_resistance" in explanation_service.educational_content
        assert "soil_compatibility" in explanation_service.educational_content

    def test_evidence_sources_initialized(self, explanation_service):
        """Test that evidence sources are initialized."""
        assert hasattr(explanation_service, 'evidence_sources')
        assert len(explanation_service.evidence_sources) > 0
        assert "university_trials" in explanation_service.evidence_sources
        assert "seed_company_data" in explanation_service.evidence_sources
        assert "farmer_reports" in explanation_service.evidence_sources
        assert "research_studies" in explanation_service.evidence_sources

    @pytest.mark.asyncio
    async def test_generate_explanation_with_minimal_options(
        self, 
        explanation_service, 
        sample_variety_data, 
        sample_context
    ):
        """Test explanation generation with minimal options."""
        minimal_options = {
            "include_detailed_reasoning": False,
            "include_evidence": False,
            "include_trade_offs": False,
            "include_risk_analysis": False,
            "include_economic_analysis": False,
            "include_management_guidance": False
        }
        
        explanation = await explanation_service.generate_comprehensive_explanation(
            variety_data=sample_variety_data,
            context=sample_context,
            explanation_options=minimal_options
        )
        
        assert isinstance(explanation, ComprehensiveExplanation)
        # Should only have summary section
        assert len(explanation.sections) == 1
        assert explanation.sections[0].section_id == "summary"

    @pytest.mark.asyncio
    async def test_generate_explanation_with_all_options(
        self, 
        explanation_service, 
        sample_variety_data, 
        sample_context
    ):
        """Test explanation generation with all options enabled."""
        all_options = {
            "include_detailed_reasoning": True,
            "include_evidence": True,
            "include_trade_offs": True,
            "include_risk_analysis": True,
            "include_economic_analysis": True,
            "include_management_guidance": True
        }
        
        explanation = await explanation_service.generate_comprehensive_explanation(
            variety_data=sample_variety_data,
            context=sample_context,
            explanation_options=all_options
        )
        
        assert isinstance(explanation, ComprehensiveExplanation)
        # Should have all sections
        assert len(explanation.sections) == 7
        section_ids = [section.section_id for section in explanation.sections]
        assert "summary" in section_ids
        assert "detailed_reasoning" in section_ids
        assert "evidence" in section_ids
        assert "trade_offs" in section_ids
        assert "risk_assessment" in section_ids
        assert "economic_analysis" in section_ids
        assert "management_guidance" in section_ids

class TestEvidenceItem:
    """Test suite for EvidenceItem dataclass."""

    def test_evidence_item_creation(self):
        """Test EvidenceItem creation."""
        evidence = EvidenceItem(
            title="Test Evidence",
            description="Test description",
            source="Test Source",
            confidence=0.85,
            data_type="research",
            relevance_score=0.9,
            supporting_data={"key": "value"}
        )
        
        assert evidence.title == "Test Evidence"
        assert evidence.description == "Test description"
        assert evidence.source == "Test Source"
        assert evidence.confidence == 0.85
        assert evidence.data_type == "research"
        assert evidence.relevance_score == 0.9
        assert evidence.supporting_data == {"key": "value"}

class TestExplanationSection:
    """Test suite for ExplanationSection dataclass."""

    def test_explanation_section_creation(self):
        """Test ExplanationSection creation."""
        evidence_items = [
            EvidenceItem(
                title="Test Evidence",
                description="Test description",
                source="Test Source",
                confidence=0.85,
                data_type="research",
                relevance_score=0.9
            )
        ]
        
        section = ExplanationSection(
            section_id="test_section",
            title="Test Section",
            content="Test content",
            explanation_type=ExplanationType.SUMMARY,
            confidence_level=ConfidenceLevel.HIGH,
            evidence_items=evidence_items,
            expandable=True,
            educational_content="Educational content",
            interactive_elements=[{"type": "test", "title": "Test Element"}]
        )
        
        assert section.section_id == "test_section"
        assert section.title == "Test Section"
        assert section.content == "Test content"
        assert section.explanation_type == ExplanationType.SUMMARY
        assert section.confidence_level == ConfidenceLevel.HIGH
        assert len(section.evidence_items) == 1
        assert section.expandable
        assert section.educational_content == "Educational content"
        assert len(section.interactive_elements) == 1

class TestComprehensiveExplanation:
    """Test suite for ComprehensiveExplanation dataclass."""

    def test_comprehensive_explanation_creation(self):
        """Test ComprehensiveExplanation creation."""
        sections = [
            ExplanationSection(
                section_id="test_section",
                title="Test Section",
                content="Test content",
                explanation_type=ExplanationType.SUMMARY,
                confidence_level=ConfidenceLevel.HIGH,
                evidence_items=[]
            )
        ]
        
        explanation = ComprehensiveExplanation(
            request_id="test_request",
            variety_id="test_variety",
            variety_name="Test Variety",
            generated_at=datetime.now(),
            overall_confidence=0.85,
            sections=sections,
            summary="Test summary",
            key_insights=["Test insight"],
            recommendations=["Test recommendation"],
            educational_resources=[{"title": "Test Resource", "url": "/test", "type": "article"}],
            accessibility_features={"test": "feature"}
        )
        
        assert explanation.request_id == "test_request"
        assert explanation.variety_id == "test_variety"
        assert explanation.variety_name == "Test Variety"
        assert explanation.overall_confidence == 0.85
        assert len(explanation.sections) == 1
        assert explanation.summary == "Test summary"
        assert len(explanation.key_insights) == 1
        assert len(explanation.recommendations) == 1
        assert len(explanation.educational_resources) == 1
        assert "test" in explanation.accessibility_features