import pytest
from ..src.services.micronutrient_service import MicronutrientService

def test_get_recommendations():
    service = MicronutrientService()
    assert service.get_recommendations() == []
