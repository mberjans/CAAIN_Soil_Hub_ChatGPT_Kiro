import pytest
from ..src.services.micronutrient_service import MicronutrientService
from ..src.models.micronutrient_models import SoilTest, Micronutrient, MicronutrientLevel

def test_get_recommendations():
    service = MicronutrientService()
    assert service.get_recommendations() == []

def test_process_soil_test():
    service = MicronutrientService()
    soil_test = SoilTest(
        lab_name="Test Lab",
        report_date="2025-10-20",
        micronutrient_levels=[
            MicronutrientLevel(
                micronutrient=Micronutrient(name="Zinc", symbol="Zn"),
                level=4.0,
                unit="ppm"
            ),
            MicronutrientLevel(
                micronutrient=Micronutrient(name="Iron", symbol="Fe"),
                level=10.0,
                unit="ppm"
            )
        ]
    )
    recommendations = service.process_soil_test(soil_test)
    assert len(recommendations) == 1
    assert recommendations[0].micronutrient.name == "Zinc"