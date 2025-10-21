import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from services.nutrient_deficiency_detection.src.models.sqlalchemy_models import Base, NutrientDeficiencySymptomORM
from services.nutrient_deficiency_detection.src.models.deficiency_models import Nutrient, Severity, PlantPart, Symptom
from services.nutrient_deficiency_detection.src.services.symptom_matching_service import SymptomMatchingService

# Setup for in-memory SQLite database for testing
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def populate_test_data(session):
    # Sample data for testing
    symptoms_to_add = [
        NutrientDeficiencySymptomORM(
            nutrient=Nutrient.NITROGEN,
            crop_type="corn",
            symptom_name="general_chlorosis_older_leaves",
            description="General yellowing of older leaves, starting from the tip and moving along the midrib.",
            affected_parts=[PlantPart.OLDER_LEAVES],
            visual_characteristics=["yellowing", "stunted growth"],
            typical_severity=Severity.MODERATE,
            notes="Nitrogen is mobile in the plant, so symptoms appear on older leaves first."
        ),
        NutrientDeficiencySymptomORM(
            nutrient=Nutrient.PHOSPHORUS,
            crop_type="corn",
            symptom_name="purpling_leaves",
            description="Leaves turn dark green or purplish, especially on the margins, often accompanied by stunted growth.",
            affected_parts=[PlantPart.WHOLE_PLANT, PlantPart.OLDER_LEAVES],
            visual_characteristics=["purpling", "dark green", "stunted growth"],
            typical_severity=Severity.MODERATE,
            notes="Phosphorus deficiency is common in cold, wet soils."
        ),
        NutrientDeficiencySymptomORM(
            nutrient=Nutrient.POTASSIUM,
            crop_type="corn",
            symptom_name="leaf_margin_chlorosis_necrosis",
            description="Yellowing and necrosis (browning/death) of leaf margins, particularly on older leaves.",
            affected_parts=[PlantPart.OLDER_LEAVES, PlantPart.LEAF_MARGINS],
            visual_characteristics=["yellowing", "browning", "necrosis"],
            typical_severity=Severity.SEVERE,
            notes="Potassium is mobile, so symptoms appear on older leaves first. Often called 'firing'."
        ),
        NutrientDeficiencySymptomORM(
            nutrient=Nutrient.IRON,
            crop_type="soybean",
            symptom_name="interveinal_chlorosis_young_leaves",
            description="Yellowing between the veins of young leaves, while veins remain green.",
            affected_parts=[PlantPart.YOUNG_LEAVES, PlantPart.INTERVEINAL_AREAS],
            visual_characteristics=["interveinal yellowing", "green veins"],
            typical_severity=Severity.MILD,
            notes="Iron is immobile, so symptoms appear on new growth first. Common in high pH soils."
        ),
        NutrientDeficiencySymptomORM(
            nutrient=Nutrient.SULFUR,
            crop_type="canola",
            symptom_name="general_chlorosis_young_leaves",
            description="General yellowing of young leaves, often accompanied by purpling of stems and petioles.",
            affected_parts=[PlantPart.YOUNG_LEAVES, PlantPart.STEM],
            visual_characteristics=["yellowing", "purpling"],
            typical_severity=Severity.MODERATE,
            notes="Sulfur is immobile, so symptoms appear on new growth first. Often confused with nitrogen deficiency."
        ),
    ]
    session.add_all(symptoms_to_add)
    session.commit()
    return symptoms_to_add

@pytest.fixture
def symptom_matching_service(session, populate_test_data):
    return SymptomMatchingService(session)

class TestSymptomMatchingService:

    def test_exact_match_nitrogen_deficiency(self, symptom_matching_service):
        observed_symptoms = [
            Symptom(name="yellowing", location="older leaves", description="Older leaves are yellowing from the tip.")
        ]
        crop_type = "corn"
        detected_deficiencies = symptom_matching_service.match_symptoms(observed_symptoms, crop_type)

        assert len(detected_deficiencies) == 1
        assert detected_deficiencies[0].nutrient == Nutrient.NITROGEN
        assert detected_deficiencies[0].confidence > 0.5
        assert detected_deficiencies[0].severity == Severity.MODERATE

    def test_partial_match_phosphorus_deficiency(self, symptom_matching_service):
        observed_symptoms = [
            Symptom(name="stunted growth", location="whole plant", description="Plant is small and leaves have a dark green color.")
        ]
        crop_type = "corn"
        detected_deficiencies = symptom_matching_service.match_symptoms(observed_symptoms, crop_type)

        assert len(detected_deficiencies) == 1
        assert detected_deficiencies[0].nutrient == Nutrient.PHOSPHORUS
        assert detected_deficiencies[0].confidence > 0.3
        assert detected_deficiencies[0].severity == Severity.MODERATE

    def test_no_match(self, symptom_matching_service):
        observed_symptoms = [
            Symptom(name="unusual spots", location="anywhere", description="Strange spots on leaves.")
        ]
        crop_type = "corn"
        detected_deficiencies = symptom_matching_service.match_symptoms(observed_symptoms, crop_type)

        assert len(detected_deficiencies) == 0

    def test_multiple_deficiencies_detected(self, symptom_matching_service):
        observed_symptoms = [
            Symptom(name="yellowing", location="older leaves", description="Older leaves are yellowing from the tip."),
            Symptom(name="purpling", location="whole plant", description="Plant is small and leaves have a purplish tint.")
        ]
        crop_type = "corn"
        detected_deficiencies = symptom_matching_service.match_symptoms(observed_symptoms, crop_type)

        assert len(detected_deficiencies) == 2
        assert {d.nutrient for d in detected_deficiencies} == {Nutrient.NITROGEN, Nutrient.PHOSPHORUS}
        # Check order by confidence (Nitrogen might have higher score due to more specific match)
        assert detected_deficiencies[0].confidence >= detected_deficiencies[1].confidence

    def test_different_crop_type(self, symptom_matching_service):
        observed_symptoms = [
            Symptom(name="interveinal yellowing", location="young leaves", description="Young leaves show yellowing between veins.")
        ]
        crop_type = "soybean"
        detected_deficiencies = symptom_matching_service.match_symptoms(observed_symptoms, crop_type)

        assert len(detected_deficiencies) == 1
        assert detected_deficiencies[0].nutrient == Nutrient.IRON

    def test_no_symptoms_observed(self, symptom_matching_service):
        observed_symptoms = []
        crop_type = "corn"
        detected_deficiencies = symptom_matching_service.match_symptoms(observed_symptoms, crop_type)
        assert len(detected_deficiencies) == 0

    def test_min_confidence_threshold(self, symptom_matching_service):
        observed_symptoms = [
            Symptom(name="yellowing", location="older leaves", description="Older leaves are yellowing from the tip.")
        ]
        crop_type = "corn"
        # Set a high min_confidence that the single symptom might not meet
        detected_deficiencies = symptom_matching_service.match_symptoms(observed_symptoms, crop_type, min_confidence=0.9)
        # Depending on scoring, this might return 0 or 1. For now, expect 0 if score is low.
        # The current scoring is simple, so it might not reach 0.9 with one symptom.
        assert len(detected_deficiencies) == 0 or detected_deficiencies[0].confidence >= 0.9

    def test_sulfur_deficiency_canola(self, symptom_matching_service):
        observed_symptoms = [
            Symptom(name="yellowing", location="young leaves", description="Young leaves are generally yellow, and stems have a purplish tint.")
        ]
        crop_type = "canola"
        detected_deficiencies = symptom_matching_service.match_symptoms(observed_symptoms, crop_type)

        assert len(detected_deficiencies) == 1
        assert detected_deficiencies[0].nutrient == Nutrient.SULFUR
        assert detected_deficiencies[0].confidence > 0.5
        assert detected_deficiencies[0].severity == Severity.MODERATE

    def test_potassium_deficiency_corn(self, symptom_matching_service):
        observed_symptoms = [
            Symptom(name="leaf margin burn", location="older leaves", description="Older leaves show yellowing and browning along the edges.")
        ]
        crop_type = "corn"
        detected_deficiencies = symptom_matching_service.match_symptoms(observed_symptoms, crop_type)

        assert len(detected_deficiencies) == 1
        assert detected_deficiencies[0].nutrient == Nutrient.POTASSIUM
        assert detected_deficiencies[0].confidence > 0.5
        assert detected_deficiencies[0].severity == Severity.SEVERE
