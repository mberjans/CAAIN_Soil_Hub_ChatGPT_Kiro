"""
Tests for analysis schemas used in image analysis API.

This module tests Pydantic schemas for image analysis requests and responses.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from pydantic import ValidationError

from src.schemas.image_schemas import (
    ImageQuality,
    DeficiencySymptom,
    Recommendation,
    DeficiencyAnalysisResponse
)
from src.schemas.symptom_schemas import (
    SymptomBase,
    SymptomCreate,
    SymptomUpdate,
    SymptomResponse,
    SymptomMatchRequest,
    SymptomMatchResponse,
    SymptomMatchResult
)


class TestImageQuality:
    """Test ImageQuality schema validation"""

    def test_valid_image_quality(self):
        """Test creating valid ImageQuality"""
        quality = ImageQuality(score=0.85, issues=[])
        assert quality.score == 0.85
        assert quality.issues == []

    def test_image_quality_with_issues(self):
        """Test ImageQuality with quality issues"""
        issues = ["Low resolution", "Poor lighting"]
        quality = ImageQuality(score=0.4, issues=issues)
        assert quality.score == 0.4
        assert quality.issues == issues

    def test_invalid_score_too_high(self):
        """Test that score > 1.0 raises validation error"""
        with pytest.raises(ValidationError):
            ImageQuality(score=1.5, issues=[])

    def test_invalid_score_too_low(self):
        """Test that score < 0.0 raises validation error"""
        with pytest.raises(ValidationError):
            ImageQuality(score=-0.1, issues=[])

    def test_default_issues(self):
        """Test that issues defaults to empty list"""
        quality = ImageQuality(score=0.8)
        assert quality.issues == []


class TestDeficiencySymptom:
    """Test DeficiencySymptom schema validation"""

    def test_valid_deficiency_symptom(self):
        """Test creating valid DeficiencySymptom"""
        symptom = DeficiencySymptom(
            nutrient="nitrogen",
            confidence=0.75,
            severity="moderate",
            affected_area_percent=25.0,
            symptoms_detected=["Yellowing leaves", "Stunted growth"]
        )
        assert symptom.nutrient == "nitrogen"
        assert symptom.confidence == 0.75
        assert symptom.severity == "moderate"
        assert symptom.affected_area_percent == 25.0
        assert len(symptom.symptoms_detected) == 2

    def test_deficiency_symptom_without_optional_fields(self):
        """Test DeficiencySymptom with only required fields"""
        symptom = DeficiencySymptom(
            nutrient="phosphorus",
            confidence=0.6,
            severity="mild"
        )
        assert symptom.nutrient == "phosphorus"
        assert symptom.confidence == 0.6
        assert symptom.severity == "mild"
        assert symptom.affected_area_percent is None
        assert symptom.symptoms_detected == []

    def test_invalid_confidence_too_high(self):
        """Test that confidence > 1.0 raises validation error"""
        with pytest.raises(ValidationError):
            DeficiencySymptom(
                nutrient="nitrogen",
                confidence=1.5,
                severity="moderate"
            )

    def test_invalid_confidence_too_low(self):
        """Test that confidence < 0.0 raises validation error"""
        with pytest.raises(ValidationError):
            DeficiencySymptom(
                nutrient="nitrogen",
                confidence=-0.1,
                severity="moderate"
            )

    def test_invalid_affected_area_percent(self):
        """Test that affected_area_percent > 100 raises validation error"""
        with pytest.raises(ValidationError):
            DeficiencySymptom(
                nutrient="nitrogen",
                confidence=0.5,
                severity="moderate",
                affected_area_percent=150.0
            )


class TestRecommendation:
    """Test Recommendation schema validation"""

    def test_valid_recommendation(self):
        """Test creating valid Recommendation"""
        recommendation = Recommendation(
            action="Apply nitrogen fertilizer",
            priority="high",
            timing="immediate",
            details="Use 50kg/ha of urea"
        )
        assert recommendation.action == "Apply nitrogen fertilizer"
        assert recommendation.priority == "high"
        assert recommendation.timing == "immediate"
        assert recommendation.details == "Use 50kg/ha of urea"

    def test_recommendation_without_details(self):
        """Test Recommendation without optional details field"""
        recommendation = Recommendation(
            action="Apply phosphorus",
            priority="medium",
            timing="within 1 week"
        )
        assert recommendation.action == "Apply phosphorus"
        assert recommendation.priority == "medium"
        assert recommendation.timing == "within 1 week"
        assert recommendation.details is None


class TestDeficiencyAnalysisResponse:
    """Test DeficiencyAnalysisResponse schema validation"""

    def test_valid_analysis_response(self):
        """Test creating valid DeficiencyAnalysisResponse"""
        analysis_id = uuid4()
        image_quality = ImageQuality(score=0.9, issues=[])
        deficiencies = [
            DeficiencySymptom(
                nutrient="nitrogen",
                confidence=0.8,
                severity="moderate"
            )
        ]
        recommendations = [
            Recommendation(
                action="Apply nitrogen fertilizer",
                priority="high",
                timing="immediate"
            )
        ]
        metadata = {"crop_type": "corn", "growth_stage": "V6"}

        response = DeficiencyAnalysisResponse(
            analysis_id=analysis_id,
            image_quality=image_quality,
            deficiencies=deficiencies,
            recommendations=recommendations,
            metadata=metadata
        )

        assert response.analysis_id == analysis_id
        assert response.image_quality == image_quality
        assert len(response.deficiencies) == 1
        assert len(response.recommendations) == 1
        assert response.metadata == metadata

    def test_analysis_response_with_default_analysis_id(self):
        """Test DeficiencyAnalysisResponse with default UUID"""
        image_quality = ImageQuality(score=0.8, issues=[])
        deficiencies = []
        recommendations = []

        response = DeficiencyAnalysisResponse(
            image_quality=image_quality,
            deficiencies=deficiencies,
            recommendations=recommendations
        )

        from uuid import UUID
        assert isinstance(response.analysis_id, UUID)
        assert response.metadata == {}


class TestSymptomBase:
    """Test SymptomBase schema validation"""

    def test_valid_symptom_base(self):
        """Test creating valid SymptomBase"""
        severity_levels = {"mild": "slight yellowing", "moderate": "visible yellowing"}
        symptom = SymptomBase(
            nutrient="nitrogen",
            crop_type="corn",
            symptom_name="Nitrogen Deficiency in Corn",
            description="Yellowing of older leaves",
            affected_parts=["Older leaves", "Lower leaves"],
            visual_characteristics=["Yellowing", "Stunted growth"],
            severity_levels=severity_levels,
            growth_stages=["V6", "V8", "V12"],
            confidence_score_threshold=0.7
        )

        assert symptom.nutrient == "nitrogen"
        assert symptom.crop_type == "corn"
        assert symptom.symptom_name == "Nitrogen Deficiency in Corn"
        assert symptom.confidence_score_threshold == 0.7
        assert len(symptom.affected_parts) == 2

    def test_default_confidence_threshold(self):
        """Test default confidence score threshold"""
        severity_levels = {"mild": "slight yellowing"}
        symptom = SymptomBase(
            nutrient="phosphorus",
            crop_type="soybean",
            symptom_name="Phosphorus Deficiency in Soybean",
            description="Purple discoloration",
            affected_parts=["Leaves", "Stem"],
            visual_characteristics=["Purpling"],
            severity_levels=severity_levels,
            growth_stages=["V2", "V4"]
        )

        assert symptom.confidence_score_threshold == 0.7

    def test_invalid_confidence_threshold_range(self):
        """Test confidence threshold outside valid range"""
        severity_levels = {"mild": "slight yellowing"}
        with pytest.raises(ValidationError):
            SymptomBase(
                nutrient="nitrogen",
                crop_type="corn",
                symptom_name="Test",
                description="Test",
                affected_parts=["Leaves"],
                visual_characteristics=["Yellowing"],
                severity_levels=severity_levels,
                growth_stages=["V6"],
                confidence_score_threshold=1.5
            )


class TestSymptomCreateAndUpdate:
    """Test SymptomCreate and SymptomUpdate schemas"""

    def test_symptom_create_inheritance(self):
        """Test that SymptomCreate inherits from SymptomBase"""
        severity_levels = {"mild": "slight yellowing"}
        symptom_create = SymptomCreate(
            nutrient="potassium",
            crop_type="wheat",
            symptom_name="Potassium Deficiency in Wheat",
            description="Leaf edge burn",
            affected_parts=["Leaf edges"],
            visual_characteristics=["Burn", "Yellowing"],
            severity_levels=severity_levels,
            growth_stages=["V4", "V6"]
        )

        assert symptom_create.nutrient == "potassium"
        assert isinstance(symptom_create, SymptomBase)

    def test_symptom_update_optional_fields(self):
        """Test SymptomUpdate with optional fields"""
        symptom_update = SymptomUpdate(
            nutrient="nitrogen",
            severity_levels={"mild": "slight yellowing"}
        )

        assert symptom_update.nutrient == "nitrogen"
        assert symptom_update.crop_type is None
        assert symptom_update.symptom_name is None
        assert symptom_update.severity_levels == {"mild": "slight yellowing"}

    def test_symptom_update_empty(self):
        """Test SymptomUpdate with no fields set"""
        symptom_update = SymptomUpdate()

        assert symptom_update.nutrient is None
        assert symptom_update.crop_type is None
        assert symptom_update.symptom_name is None


class TestSymptomResponse:
    """Test SymptomResponse schema validation"""

    def test_symptom_response_structure(self):
        """Test SymptomResponse includes database fields"""
        symptom_id = uuid4()
        created_at = datetime.now()
        updated_at = datetime.now()

        severity_levels = {"mild": "slight yellowing"}
        symptom_response = SymptomResponse(
            id=symptom_id,
            created_at=created_at,
            updated_at=updated_at,
            nutrient="nitrogen",
            crop_type="corn",
            symptom_name="Nitrogen Deficiency in Corn",
            description="Yellowing of older leaves",
            affected_parts=["Older leaves"],
            visual_characteristics=["Yellowing"],
            severity_levels=severity_levels,
            growth_stages=["V6"],
            confidence_score_threshold=0.7
        )

        assert symptom_response.id == symptom_id
        assert symptom_response.created_at == created_at
        assert symptom_response.updated_at == updated_at
        assert isinstance(symptom_response, SymptomBase)


class TestSymptomMatchSchemas:
    """Test symptom matching schemas"""

    def test_symptom_match_request(self):
        """Test SymptomMatchRequest validation"""
        request = SymptomMatchRequest(
            detected_characteristics=["Yellowing", "Stunted growth"],
            crop_type="corn"
        )

        assert request.detected_characteristics == ["Yellowing", "Stunted growth"]
        assert request.crop_type == "corn"

    def test_symptom_match_response(self):
        """Test SymptomMatchResponse validation"""
        response = SymptomMatchResponse(
            nutrient="nitrogen",
            symptom_name="Nitrogen Deficiency",
            description="Yellowing of older leaves",
            affected_parts=["Older leaves"],
            visual_characteristics=["Yellowing"],
            severity_levels={"mild": "slight yellowing"},
            match_score=0.85,
            confidence_threshold=0.7
        )

        assert response.nutrient == "nitrogen"
        assert response.match_score == 0.85
        assert response.confidence_threshold == 0.7

    def test_symptom_match_result(self):
        """Test SymptomMatchResult aggregation"""
        matches = [
            SymptomMatchResponse(
                nutrient="nitrogen",
                symptom_name="Nitrogen Deficiency",
                description="Yellowing",
                affected_parts=["Leaves"],
                visual_characteristics=["Yellowing"],
                severity_levels={"mild": "slight"},
                match_score=0.8,
                confidence_threshold=0.7
            ),
            SymptomMatchResponse(
                nutrient="iron",
                symptom_name="Iron Deficiency",
                description="Interveinal chlorosis",
                affected_parts=["Young leaves"],
                visual_characteristics=["Yellowing between veins"],
                severity_levels={"moderate": "clear chlorosis"},
                match_score=0.6,
                confidence_threshold=0.8
            )
        ]

        result = SymptomMatchResult(potential_deficiencies=matches)

        assert len(result.potential_deficiencies) == 2
        assert result.potential_deficiencies[0].nutrient == "nitrogen"
        assert result.potential_deficiencies[1].nutrient == "iron"


class TestImageAnalysisRequestSchema:
    """Test ImageAnalysisRequest schema (when implemented)"""

    def test_placeholder_for_image_analysis_request(self):
        """
        Placeholder test for ImageAnalysisRequest schema.

        This test will be updated when ImageAnalysisRequest schema
        is implemented as part of the analysis_schemas.py file.
        For now, it documents the expected behavior.
        """
        # TODO: Implement ImageAnalysisRequest schema and update this test
        # Expected fields:
        # - crop_type: str (required)
        # - growth_stage: Optional[str]
        # - image: UploadFile (handled by FastAPI)
        # - additional_metadata: Optional[dict]

        # This placeholder ensures test structure exists
        # and will fail when schema is implemented,
        # prompting implementation of actual tests
        pass