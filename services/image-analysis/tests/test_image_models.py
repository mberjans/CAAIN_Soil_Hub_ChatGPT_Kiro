"""
Test file for image models - JOB3-003.1.test

Tests for ImageAnalysis and DeficiencyDetection models
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Import the models (these will be created in JOB3-003.3.impl)
try:
    from src.models.image_models import ImageAnalysis, DeficiencyDetection
except ImportError:
    # Models don't exist yet - this is expected for TDD
    pytest.skip("Models not implemented yet", allow_module_level=True)


class TestImageAnalysis:
    """Test cases for ImageAnalysis model"""

    def setup_method(self):
        """Setup test database session"""
        # Use in-memory SQLite for testing
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        # Import Base from models and create tables
        from src.models.image_models import Base
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self):
        """Cleanup test database session"""
        self.session.close()

    def test_image_analysis_creation(self):
        """
        Test creating an ImageAnalysis record

        JOB3-003.2.test - Write test for ImageAnalysis model
        """
        # Create test data
        image_analysis = ImageAnalysis(
            image_path="/path/to/test/image.jpg",
            crop_type="corn",
            growth_stage="V6",
            image_size_mb=2.5,
            upload_timestamp=datetime.utcnow(),
            processing_status="pending",
            quality_score=0.85
        )

        # Add to session and commit
        self.session.add(image_analysis)
        self.session.commit()

        # Verify the record was created
        retrieved = self.session.query(ImageAnalysis).filter_by(image_path="/path/to/test/image.jpg").first()

        assert retrieved is not None
        assert retrieved.crop_type == "corn"
        assert retrieved.growth_stage == "V6"
        assert retrieved.image_size_mb == 2.5
        assert retrieved.processing_status == "pending"
        assert retrieved.quality_score == 0.85
        assert retrieved.upload_timestamp is not None
        assert retrieved.id is not None  # Primary key should be assigned

    def test_image_analysis_required_fields(self):
        """Test that required fields cannot be null"""
        # Test missing image_path
        with pytest.raises(IntegrityError):
            image_analysis = ImageAnalysis(
                crop_type="corn",
                growth_stage="V6"
            )
            self.session.add(image_analysis)
            self.session.commit()

    def test_image_analysis_default_values(self):
        """Test default values are set correctly"""
        image_analysis = ImageAnalysis(
            image_path="/path/to/test/image2.jpg",
            crop_type="soybean",
            growth_stage="R2"
        )

        self.session.add(image_analysis)
        self.session.commit()

        # Check default values
        retrieved = self.session.query(ImageAnalysis).filter_by(image_path="/path/to/test/image2.jpg").first()
        assert retrieved.processing_status == "pending"  # Default status
        assert retrieved.quality_score is None  # Should be None until processed

    def test_image_analysis_relationships(self):
        """Test relationship with DeficiencyDetection"""
        # Create image analysis
        image_analysis = ImageAnalysis(
            image_path="/path/to/test/image3.jpg",
            crop_type="wheat",
            growth_stage="boot"
        )

        # Create deficiency detection
        deficiency = DeficiencyDetection(
            image_analysis=image_analysis,
            nutrient="nitrogen",
            confidence_score=0.75,
            severity="moderate",
            affected_area_percent=30.0
        )

        self.session.add(image_analysis)
        self.session.add(deficiency)
        self.session.commit()

        # Verify relationship
        retrieved_image = self.session.query(ImageAnalysis).filter_by(image_path="/path/to/test/image3.jpg").first()
        assert len(retrieved_image.deficiency_detections) == 1
        assert retrieved_image.deficiency_detections[0].nutrient == "nitrogen"
        assert retrieved_image.deficiency_detections[0].confidence_score == 0.75


class TestDeficiencyDetection:
    """Test cases for DeficiencyDetection model"""

    def setup_method(self):
        """Setup test database session"""
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        from src.models.image_models import Base
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self):
        """Cleanup test database session"""
        self.session.close()

    def test_deficiency_detection_creation(self):
        """Test creating a DeficiencyDetection record"""
        # First create an ImageAnalysis to reference
        image_analysis = ImageAnalysis(
            image_path="/path/to/test/image4.jpg",
            crop_type="corn",
            growth_stage="V6"
        )
        self.session.add(image_analysis)
        self.session.commit()

        # Create deficiency detection
        deficiency = DeficiencyDetection(
            image_analysis_id=image_analysis.id,
            nutrient="phosphorus",
            confidence_score=0.82,
            severity="severe",
            affected_area_percent=45.5,
            symptoms_detected=["Purple leaves", "Stunted growth"],
            model_version="v1.0"
        )

        self.session.add(deficiency)
        self.session.commit()

        # Verify the record was created
        retrieved = self.session.query(DeficiencyDetection).filter_by(nutrient="phosphorus").first()

        assert retrieved is not None
        assert retrieved.image_analysis_id == image_analysis.id
        assert retrieved.nutrient == "phosphorus"
        assert retrieved.confidence_score == 0.82
        assert retrieved.severity == "severe"
        assert retrieved.affected_area_percent == 45.5
        assert retrieved.symptoms_detected == ["Purple leaves", "Stunted growth"]
        assert retrieved.model_version == "v1.0"
        assert retrieved.id is not None

    def test_deficiency_detection_required_fields(self):
        """Test that required fields cannot be null"""
        # Test missing nutrient
        with pytest.raises(IntegrityError):
            deficiency = DeficiencyDetection(
                confidence_score=0.75
            )
            self.session.add(deficiency)
            self.session.commit()

    def test_multiple_deficiencies_per_image(self):
        """Test that one image can have multiple deficiency detections"""
        # Create image analysis
        image_analysis = ImageAnalysis(
            image_path="/path/to/test/image5.jpg",
            crop_type="corn",
            growth_stage="V6"
        )
        self.session.add(image_analysis)
        self.session.commit()

        # Create multiple deficiencies
        deficiency1 = DeficiencyDetection(
            image_analysis_id=image_analysis.id,
            nutrient="nitrogen",
            confidence_score=0.75,
            severity="moderate",
            affected_area_percent=25.0
        )

        deficiency2 = DeficiencyDetection(
            image_analysis_id=image_analysis.id,
            nutrient="potassium",
            confidence_score=0.60,
            severity="mild",
            affected_area_percent=15.0
        )

        self.session.add(deficiency1)
        self.session.add(deficiency2)
        self.session.commit()

        # Verify both deficiencies are associated with the image
        retrieved_image = self.session.query(ImageAnalysis).filter_by(image_path="/path/to/test/image5.jpg").first()
        assert len(retrieved_image.deficiency_detections) == 2

        nutrients = [d.nutrient for d in retrieved_image.deficiency_detections]
        assert "nitrogen" in nutrients
        assert "potassium" in nutrients

    def test_deficiency_severity_validation(self):
        """Test that severity values are within expected range"""
        image_analysis = ImageAnalysis(
            image_path="/path/to/test/image6.jpg",
            crop_type="soybean",
            growth_stage="R2"
        )
        self.session.add(image_analysis)
        self.session.commit()

        # Valid severity values
        valid_severities = ["mild", "moderate", "severe"]

        for severity in valid_severities:
            deficiency = DeficiencyDetection(
                image_analysis_id=image_analysis.id,
                nutrient="nitrogen",
                confidence_score=0.5,
                severity=severity,
                affected_area_percent=20.0
            )
            self.session.add(deficiency)
            self.session.commit()

            retrieved = self.session.query(DeficiencyDetection).filter_by(severity=severity).first()
            assert retrieved.severity == severity

            # Clean up for next iteration
            self.session.delete(retrieved)
            self.session.commit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])