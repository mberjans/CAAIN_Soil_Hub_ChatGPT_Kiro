from typing import List, Dict
from ..models.micronutrient_models import MicronutrientName
from ..models.soil_test_models import SoilTestResult
from .threshold_service import MicronutrientThresholdService
from .crop_micronutrient_service import CropMicronutrientService

class MicronutrientPrioritizationService:
    def __init__(self, threshold_service: MicronutrientThresholdService, crop_micronutrient_service: CropMicronutrientService):
        self.threshold_service = threshold_service
        self.crop_micronutrient_service = crop_micronutrient_service

    def prioritize_micronutrients(self, soil_test_result: SoilTestResult, crop_name: str) -> List[Dict[str, any]]:
        priorities = []
        for micro_name, micro_result in soil_test_result.micronutrients.items():
            current_concentration = micro_result.concentration_ppm
            
            soil_deficient_threshold = self.threshold_service.get_soil_deficiency_threshold(micro_name)
            soil_toxic_threshold = self.threshold_service.get_soil_toxicity_threshold(micro_name)
            crop_req = self.crop_micronutrient_service.get_specific_micronutrient_requirement(crop_name, micro_name)

            status = "Optimal"
            severity_score = 0.0
            impact_factor = 1.0 # Placeholder, will be refined with yield impact

            if soil_deficient_threshold is not None and current_concentration < soil_deficient_threshold:
                status = "Deficient"
                severity_score = (soil_deficient_threshold - current_concentration) / soil_deficient_threshold
                if crop_req and crop_req.required_amount_per_ton_yield_g:
                    impact_factor = crop_req.required_amount_per_ton_yield_g / 100.0 # Example scaling
            elif soil_toxic_threshold is not None and current_concentration > soil_toxic_threshold:
                status = "Toxic"
                severity_score = (current_concentration - soil_toxic_threshold) / soil_toxic_threshold
                impact_factor = 2.0 # Toxicity generally has higher impact
            
            # Consider pH impact on availability
            optimal_ph_range = self.threshold_service.get_optimal_ph_range(crop_name, micro_name)
            if optimal_ph_range and soil_test_result.ph:
                min_ph, max_ph = optimal_ph_range
                if not (min_ph <= soil_test_result.ph <= max_ph):
                    # Penalize if pH is outside optimal range, increasing priority
                    severity_score += 0.2 # Example penalty
                    impact_factor += 0.5 # Example impact increase

            priority_score = severity_score * impact_factor

            priorities.append({
                "micronutrient": micro_name,
                "status": status,
                "current_concentration_ppm": current_concentration,
                "soil_deficient_threshold_ppm": soil_deficient_threshold,
                "soil_toxic_threshold_ppm": soil_toxic_threshold,
                "priority_score": priority_score,
                "impact_factor": impact_factor
            })
        
        # Sort by priority score in descending order
        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        return priorities
