import pytest
from ..src.services.micronutrient_service import MicronutrientService
from ..src.models.micronutrient_models import SoilTest, Micronutrient, MicronutrientLevel

def test_get_recommendations():
    service = MicronutrientService()
    assert service.get_recommendations() == []

def test_process_soil_test_deficient():
    service = MicronutrientService()
    soil_test = SoilTest(
        lab_name="Test Lab",
        report_date="2025-10-20",
        micronutrient_levels=[
            MicronutrientLevel(
                micronutrient=Micronutrient(name="Zinc", symbol="Zn"),
                level=1.0,
                unit="ppm"
            )
        ]
    )
    recommendations = service.process_soil_test(soil_test, "corn")
    assert len(recommendations) == 1
    assert "Deficient" in recommendations[0].recommendation

def test_process_soil_test_toxic():
    service = MicronutrientService()
    soil_test = SoilTest(
        lab_name="Test Lab",
        report_date="2025-10-20",
        micronutrient_levels=[
            MicronutrientLevel(
                micronutrient=Micronutrient(name="Zinc", symbol="Zn"),
                level=100.0,
                unit="ppm"
            )
        ]
    )
    recommendations = service.process_soil_test(soil_test, "corn")
    assert len(recommendations) == 1
    assert "Toxic" in recommendations[0].recommendation

def test_process_soil_test_sufficient():
    service = MicronutrientService()
    soil_test = SoilTest(
        lab_name="Test Lab",
        report_date="2025-10-20",
        micronutrient_levels=[
            MicronutrientLevel(
                micronutrient=Micronutrient(name="Zinc", symbol="Zn"),
                level=10.0,
                unit="ppm"
            )
        ]
    )
    recommendations = service.process_soil_test(soil_test, "corn")
    assert len(recommendations) == 0
