from typing import Optional
from ..models.micronutrient_models import MicronutrientName, Micronutrient
from .soil_test_service import MicronutrientSoilTestService
from .crop_micronutrient_service import CropMicronutrientService

class MicronutrientThresholdService:
    def __init__(self, soil_test_service: MicronutrientSoilTestService, crop_micronutrient_service: CropMicronutrientService):
        self.soil_test_service = soil_test_service
        self.crop_micronutrient_service = crop_micronutrient_service

    def get_soil_deficiency_threshold(self, micronutrient_name: MicronutrientName) -> Optional[float]:
        micronutrient_data = self.soil_test_service.micronutrient_thresholds.get(micronutrient_name)
        return micronutrient_data.soil_concentration_deficient_ppm if micronutrient_data else None

    def get_soil_toxicity_threshold(self, micronutrient_name: MicronutrientName) -> Optional[float]:
        micronutrient_data = self.soil_test_service.micronutrient_thresholds.get(micronutrient_name)
        return micronutrient_data.soil_concentration_toxic_ppm if micronutrient_data else None

    def get_critical_leaf_concentration(self, crop_name: str, micronutrient_name: MicronutrientName) -> Optional[float]:
        crop_req = self.crop_micronutrient_service.get_specific_micronutrient_requirement(crop_name, micronutrient_name)
        return crop_req.critical_leaf_concentration_ppm if crop_req else None

    def get_optimal_ph_range(self, crop_name: str, micronutrient_name: MicronutrientName) -> Optional[tuple[float, float]]:
        crop_req = self.crop_micronutrient_service.get_specific_micronutrient_requirement(crop_name, micronutrient_name)
        if crop_req and crop_req.optimal_ph_range_min is not None and crop_req.optimal_ph_range_max is not None:
            return (crop_req.optimal_ph_range_min, crop_req.optimal_ph_range_max)
        return None
