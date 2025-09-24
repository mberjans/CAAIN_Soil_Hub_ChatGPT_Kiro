"""
Comprehensive Test Suite for Nutrient Deficiency Detection
Tests for deficiency analysis, visual symptom processing, and treatment recommendations.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, date
from typing import List, Dict

from ..src.services.nutrient_deficiency_detection_service import (
    NutrientDeficiencyDetectionService, DeficiencyType, DeficiencySeverity,
    DeficiencyAnalysis, VisualSymptomAnalysis, TreatmentRecommendation
)
from ..src.services.visual_symptom_analyzer import VisualSymptomAnalyzer, CropImageAnalyzer
from ..src.models.agricultural_models import SoilTestData


class TestNutrientDeficiencyDetectionService:
    """Test nutrient deficiency detection functionality."""
    
    @pytest.fixture
    def deficiency_service(self):
        """Create deficiency detection service instance."""
        return NutrientDeficiencyDetectionService()
    
    @pytest.fixture
    def sample_soil_test_data(self):
        """Create sample soil test data with deficiencies."""
        return SoilTestData(
            ph=6.2,
            organic_matter_percent=3.1,
            phosphorus_ppm=8.0,  # Low - deficient
            potassium_ppm=95.0,  # Low - deficient
            nitrogen_ppm=5.0,    # Very low - severely deficient
            zinc_ppm=0.4,        # Low - deficient
            iron_ppm=2.5,        # Low - deficient
            manganese_ppm=0.6,   # Low - deficient
            test_date=date(2024, 3, 15),
            lab_name="Test Lab"
        )
    
    @pytest.fixture
    def sample_tissue_test_data(self):
        """Create sample tissue test data."""
        return {
            'nitrogen_percent': 2.2,  # Low for corn
            'phosphorus_percent': 0.18,  # Low for corn
            'potassium_percent': 1.4,  # Low for corn
            'zinc_ppm': 18,  # Low for corn
            'iron_ppm': 35   # Low for corn
        }
    
    @pytest.fixture
    def sample_visual_symptoms(self):
        """Create sample visual symptom descriptions."""
        return [
            'yellowing of older leaves starting from bottom',
            'stunted growth and pale green coloration',
            'leaf margin burn on older leaves',
            'interveinal chlorosis on young leaves'
        ]
    
    @pytest.mark.asyncio
    async def test_comprehensive_deficiency_analysis(
        self, 
        deficiency_service, 
        sample_soil_test_data, 
        sample_tissue_test_data, 
        sample_visual_symptoms
    ):
        """Test comprehensive deficiency analysis with multiple data sources."""
        
        analysis = await deficiency_service.analyze_comprehensive_deficiency(
            crop_type='corn',
            soil_test_data=sample_soil_test_data,
            tissue_test_data=sample_tissue_test_data,
            visual_symptoms=sample_visual_symptoms,
            crop_images=None,
            field_observations={'growth_stage': 'early_vegetative'}
        )
        
        # Verify analysis structure
        assert 'analysis_id' in analysis
        assert 'deficiency_analyses' in analysis
        assert 'treatment_recommendations' in analysis
        assert 'monitoring_plan' in analysis
        assert 'overall_risk_score' in analysis
        
        # Should detect multiple deficiencies
        deficiency_analyses = analysis['deficiency_analyses']
        assert len(deficiency_analyses) > 0
        
        # Should detect nitrogen deficiency (severe in both soil and tissue)
        nitrogen_analysis = next(
            (da for da in deficiency_analyses if da.deficiency_type == DeficiencyType.NITROGEN), 
            None
        )
        assert nitrogen_analysis is not None
        assert nitrogen_analysis.severity in [DeficiencySeverity.SEVERE, DeficiencySeverity.CRITICAL]
        assert nitrogen_analysis.confidence_score > 0.7
        
        # Should have treatment recommendations
        assert len(analysis['treatment_recommendations']) > 0
        
        # Should have monitoring plan
        assert analysis['monitoring_plan'] is not None
    
    def test_soil_test_deficiency_analysis(self, deficiency_service, sample_soil_test_data):
        """Test soil test deficiency analysis."""
        
        # Test nitrogen deficiency detection
        severity, confidence = deficiency_service._analyze_soil_test_deficiency(
            DeficiencyType.NITROGEN, 'corn', sample_soil_test_data
        )
        
        # Should detect severe nitrogen deficiency
        assert severity > 80  # High severity
        assert confidence > 0.8  # High confidence
        
        # Test phosphorus deficiency detection
        severity, confidence = deficiency_service._analyze_soil_test_deficiency(
            DeficiencyType.PHOSPHORUS, 'corn', sample_soil_test_data
        )
        
        # Should detect phosphorus deficiency
        assert severity > 60  # Moderate to severe
        assert confidence > 0.7
    
    def test_tissue_test_deficiency_analysis(self, deficiency_service, sample_tissue_test_data):
        """Test tissue test deficiency analysis."""
        
        # Test nitrogen deficiency in tissue
        severity, confidence = deficiency_service._analyze_tissue_test_deficiency(
            DeficiencyType.NITROGEN, 'corn', sample_tissue_test_data
        )
        
        # Should detect nitrogen deficiency
        assert severity > 60  # Moderate severity
        assert confidence > 0.8  # High confidence for tissue tests
        
        # Test phosphorus deficiency in tissue
        severity, confidence = deficiency_service._analyze_tissue_test_deficiency(
            DeficiencyType.PHOSPHORUS, 'corn', sample_tissue_test_data
        )
        
        # Should detect phosphorus deficiency
        assert severity > 50
        assert confidence > 0.8
    
    def test_visual_symptom_analysis(self, deficiency_service, sample_visual_symptoms):
        """Test visual symptom analysis."""
        
        # Test nitrogen symptom recognition
        severity, confidence = deficiency_service._analyze_visual_symptoms(
            DeficiencyType.NITROGEN, sample_visual_symptoms
        )
        
        # Should recognize nitrogen symptoms
        assert severity > 30  # Should detect some symptoms
        assert confidence > 0.3  # Moderate confidence
        
        # Test potassium symptom recognition
        severity, confidence = deficiency_service._analyze_visual_symptoms(
            DeficiencyType.POTASSIUM, sample_visual_symptoms
        )
        
        # Should recognize potassium symptoms (leaf margin burn)
        assert severity > 20
        assert confidence > 0.3
    
    def test_deficiency_impact_calculation(self, deficiency_service):
        """Test deficiency impact calculation."""
        
        impact = deficiency_service._calculate_deficiency_impact(
            DeficiencyType.NITROGEN, DeficiencySeverity.SEVERE, 'corn'
        )
        
        # Should calculate significant impact for severe nitrogen deficiency
        assert impact['yield_impact_percent'] > 10
        assert impact['economic_impact'] > 50  # Should be substantial
        assert impact['yield_loss_bushels_per_acre'] > 15
        
        # Test mild deficiency impact
        mild_impact = deficiency_service._calculate_deficiency_impact(
            DeficiencyType.ZINC, DeficiencySeverity.MILD, 'corn'
        )
        
        # Should have lower impact
        assert mild_impact['yield_impact_percent'] < impact['yield_impact_percent']
        assert mild_impact['economic_impact'] < impact['economic_impact']
    
    def test_urgency_score_calculation(self, deficiency_service):
        """Test urgency score calculation."""
        
        # Test critical nitrogen deficiency
        urgency = deficiency_service._calculate_urgency_score(
            DeficiencyType.NITROGEN, 
            DeficiencySeverity.CRITICAL, 
            'corn',
            {'growth_stage': 'early_vegetative'}
        )
        
        # Should have very high urgency
        assert urgency > 90
        
        # Test mild zinc deficiency
        mild_urgency = deficiency_service._calculate_urgency_score(
            DeficiencyType.ZINC,
            DeficiencySeverity.MILD,
            'corn',
            {'growth_stage': 'maturity'}
        )
        
        # Should have lower urgency
        assert mild_urgency < urgency
        assert mild_urgency < 50  # Low urgency near maturity


class TestVisualSymptomAnalyzer:
    """Test visual symptom analysis functionality."""
    
    @pytest.fixture
    def symptom_analyzer(self):
        """Create symptom analyzer instance."""
        return VisualSymptomAnalyzer()
    
    @pytest.mark.asyncio
    async def test_symptom_description_analysis(self, symptom_analyzer):
        """Test natural language symptom description analysis."""
        
        nitrogen_description = (
            "The older leaves are turning yellow starting from the bottom of the plant. "
            "The yellowing is uniform and the plants appear stunted with pale green color. "
            "This started about a week ago and is getting worse."
        )
        
        analysis = await symptom_analyzer.analyze_symptom_description(
            symptom_description=nitrogen_description,
            crop_type='corn',
            growth_stage='early_vegetative'
        )
        
        # Verify analysis structure
        assert isinstance(analysis, VisualSymptomAnalysis)
        assert len(analysis.detected_symptoms) > 0
        assert len(analysis.affected_plant_parts) > 0
        assert analysis.confidence_score > 0
        
        # Should detect nitrogen-related symptoms
        assert 'older_leaves' in analysis.affected_plant_parts
        assert any('yellow' in symptom for symptom in analysis.detected_symptoms)
        
        # Should have reasonable confidence for clear nitrogen symptoms
        nitrogen_severity = analysis.symptom_severity.get('nitrogen', 0)
        assert nitrogen_severity > 30
    
    def test_symptom_keyword_matching(self, symptom_analyzer):
        """Test symptom keyword matching."""
        
        # Test iron deficiency symptoms
        iron_description = "young leaves showing interveinal chlorosis with green veins and yellow tissue"
        
        match = symptom_analyzer._match_symptoms_to_deficiency(
            iron_description, DeficiencyType.IRON, 'early_vegetative', None
        )
        
        # Should match iron deficiency well
        assert match.match_confidence > 0.6
        assert match.location_match  # Should match young leaves
        
        # Test potassium deficiency symptoms
        potassium_description = "leaf margins are burning and browning on older leaves"
        
        match = symptom_analyzer._match_symptoms_to_deficiency(
            potassium_description, DeficiencyType.POTASSIUM, 'reproductive', None
        )
        
        # Should match potassium deficiency
        assert match.match_confidence > 0.5
        assert match.location_match  # Should match older leaves and margins
    
    def test_severity_extraction(self, symptom_analyzer):
        """Test severity extraction from descriptions."""
        
        # Test severe symptoms
        severe_description = "severe yellowing affecting 80% of the field with complete leaf burn"
        severity = symptom_analyzer._extract_severity_from_description(severe_description)
        assert severity > 80
        
        # Test mild symptoms
        mild_description = "slight yellowing on a few older leaves, barely noticeable"
        severity = symptom_analyzer._extract_severity_from_description(mild_description)
        assert severity < 40
        
        # Test moderate symptoms
        moderate_description = "noticeable yellowing on many leaves throughout the field"
        severity = symptom_analyzer._extract_severity_from_description(moderate_description)
        assert 40 <= severity <= 70
    
    def test_affected_parts_identification(self, symptom_analyzer):
        """Test identification of affected plant parts."""
        
        description = "older leaves showing margin burn while young leaves have interveinal chlorosis"
        
        affected_parts = symptom_analyzer._identify_affected_parts(description)
        
        # Should identify both older and younger leaves
        assert 'older_leaves' in affected_parts
        assert 'younger_leaves' in affected_parts or 'leaves' in affected_parts
        assert 'leaf_margins' in affected_parts or 'margins' in affected_parts
    
    def test_distribution_pattern_determination(self, symptom_analyzer):
        """Test symptom distribution pattern determination."""
        
        # Test uniform distribution
        uniform_desc = "uniform yellowing throughout the entire field"
        pattern = symptom_analyzer._determine_distribution_pattern(uniform_desc)
        assert pattern == 'uniform'
        
        # Test patchy distribution
        patchy_desc = "scattered patches of yellowing in random spots"
        pattern = symptom_analyzer._determine_distribution_pattern(patchy_desc)
        assert pattern == 'patchy'
        
        # Test localized distribution
        localized_desc = "yellowing confined to one specific area of the field"
        pattern = symptom_analyzer._determine_distribution_pattern(localized_desc)
        assert pattern == 'localized'


class TestCropImageAnalyzer:
    """Test crop image analysis functionality."""
    
    @pytest.fixture
    def image_analyzer(self):
        """Create image analyzer instance."""
        return CropImageAnalyzer()
    
    @pytest.mark.asyncio
    async def test_crop_image_analysis(self, image_analyzer):
        """Test crop image analysis for deficiency detection."""
        
        # Mock base64 encoded image
        mock_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        suspected_deficiencies = [DeficiencyType.NITROGEN, DeficiencyType.IRON]
        
        analysis = await image_analyzer.analyze_crop_image(
            image_data=mock_image,
            crop_type='corn',
            suspected_deficiencies=suspected_deficiencies
        )
        
        # Verify analysis structure
        assert 'image_quality_score' in analysis
        assert 'detected_symptoms' in analysis
        assert 'deficiency_probabilities' in analysis
        assert 'confidence_scores' in analysis
        
        # Should have probabilities for suspected deficiencies
        for deficiency in suspected_deficiencies:
            assert deficiency.value in analysis['deficiency_probabilities']
            assert deficiency.value in analysis['confidence_scores']
    
    def test_image_quality_assessment(self, image_analyzer):
        """Test image quality assessment."""
        
        mock_image = "test_image_data"
        
        quality = image_analyzer.assess_image_quality(mock_image)
        
        # Verify quality assessment structure
        assert 'overall_quality' in quality
        assert 'resolution_adequate' in quality
        assert 'lighting_adequate' in quality
        assert 'focus_adequate' in quality
        assert 'quality_score' in quality
        assert 'improvement_suggestions' in quality
        
        # Quality score should be between 0 and 1
        assert 0 <= quality['quality_score'] <= 1


class TestDeficiencyIntegration:
    """Integration tests for complete deficiency detection workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_deficiency_workflow(self):
        """Test complete workflow from detection to treatment recommendations."""
        
        # Initialize services
        deficiency_service = NutrientDeficiencyDetectionService()
        symptom_analyzer = VisualSymptomAnalyzer()
        
        # Step 1: Analyze symptoms from description
        symptom_description = (
            "Corn plants showing severe yellowing of older leaves starting from the bottom. "
            "Plants are stunted and have pale green color. Also seeing some leaf margin burn "
            "on older leaves and interveinal chlorosis on young leaves."
        )
        
        symptom_analysis = await symptom_analyzer.analyze_symptom_description(
            symptom_description=symptom_description,
            crop_type='corn',
            growth_stage='early_vegetative'
        )
        
        assert symptom_analysis.confidence_score > 0.5
        
        # Step 2: Create deficient soil test data
        soil_test_data = SoilTestData(
            ph=6.0,
            organic_matter_percent=2.8,
            phosphorus_ppm=10.0,  # Low
            potassium_ppm=100.0,  # Low
            nitrogen_ppm=6.0,     # Very low
            zinc_ppm=0.6,         # Low
            test_date=date(2024, 3, 15)
        )
        
        # Step 3: Perform comprehensive deficiency analysis
        comprehensive_analysis = await deficiency_service.analyze_comprehensive_deficiency(
            crop_type='corn',
            soil_test_data=soil_test_data,
            tissue_test_data=None,
            visual_symptoms=[symptom_description],
            crop_images=None,
            field_observations={'growth_stage': 'early_vegetative'}
        )
        
        # Verify comprehensive analysis
        assert comprehensive_analysis is not None
        assert len(comprehensive_analysis['deficiency_analyses']) > 0
        
        # Should detect nitrogen deficiency with high confidence
        nitrogen_deficiency = next(
            (da for da in comprehensive_analysis['deficiency_analyses'] 
             if da.deficiency_type == DeficiencyType.NITROGEN), None
        )
        
        assert nitrogen_deficiency is not None
        assert nitrogen_deficiency.confidence_score > 0.7
        assert nitrogen_deficiency.severity in [DeficiencySeverity.MODERATE, DeficiencySeverity.SEVERE]
        
        # Should have treatment recommendations
        treatments = comprehensive_analysis['treatment_recommendations']
        assert len(treatments) > 0
        
        # Should have monitoring plan
        monitoring = comprehensive_analysis['monitoring_plan']
        assert monitoring is not None
        
        print("Integration test completed successfully!")
        print(f"Detected {len(comprehensive_analysis['deficiency_analyses'])} deficiencies")
        print(f"Generated {len(treatments)} treatment recommendations")
    
    @pytest.mark.asyncio
    async def test_multi_source_deficiency_detection(self):
        """Test deficiency detection using multiple data sources."""
        
        deficiency_service = NutrientDeficiencyDetectionService()
        
        # Create consistent deficiency across all data sources
        soil_data = SoilTestData(
            ph=6.2,
            nitrogen_ppm=4.0,  # Severely deficient
            phosphorus_ppm=25.0,  # Adequate
            potassium_ppm=180.0,  # Adequate
            test_date=date(2024, 3, 15)
        )
        
        tissue_data = {
            'nitrogen_percent': 1.8,  # Severely deficient for corn
            'phosphorus_percent': 0.28,  # Adequate
            'potassium_percent': 2.0   # Adequate
        }
        
        visual_symptoms = [
            'severe yellowing of older leaves',
            'stunted growth throughout field',
            'pale green coloration'
        ]
        
        # Analyze with all data sources
        analysis = await deficiency_service.analyze_comprehensive_deficiency(
            crop_type='corn',
            soil_test_data=soil_data,
            tissue_test_data=tissue_data,
            visual_symptoms=visual_symptoms,
            field_observations={'growth_stage': 'early_vegetative'}
        )
        
        # Should detect nitrogen deficiency with very high confidence
        nitrogen_analysis = next(
            (da for da in analysis['deficiency_analyses'] 
             if da.deficiency_type == DeficiencyType.NITROGEN), None
        )
        
        assert nitrogen_analysis is not None
        assert nitrogen_analysis.confidence_score > 0.85  # High confidence from multiple sources
        assert len(nitrogen_analysis.evidence_sources) >= 3  # Soil, tissue, and visual
        assert nitrogen_analysis.severity == DeficiencySeverity.SEVERE
        
        # Should NOT detect phosphorus or potassium deficiencies strongly
        phosphorus_analysis = next(
            (da for da in analysis['deficiency_analyses'] 
             if da.deficiency_type == DeficiencyType.PHOSPHORUS), None
        )
        
        if phosphorus_analysis:
            assert phosphorus_analysis.confidence_score < 0.5  # Low confidence
        
        print("Multi-source detection test completed successfully!")
        print(f"Nitrogen deficiency confidence: {nitrogen_analysis.confidence_score:.2f}")
        print(f"Evidence sources: {nitrogen_analysis.evidence_sources}")


if __name__ == "__main__":
    # Run specific test for debugging
    import asyncio
    
    async def run_integration_test():
        test_instance = TestDeficiencyIntegration()
        await test_instance.test_complete_deficiency_workflow()
    
    asyncio.run(run_integration_test())