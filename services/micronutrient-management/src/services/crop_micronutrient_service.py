from typing import Dict, List, Optional
from ..models.micronutrient_models import MicronutrientName, MicronutrientRequirement

class CropMicronutrientService:
    def __init__(self):
        self._crop_requirements: Dict[str, Dict[MicronutrientName, MicronutrientRequirement]] = self._load_dummy_crop_requirements()

    def _load_dummy_crop_requirements(self) -> Dict[str, Dict[MicronutrientName, MicronutrientRequirement]]:
        # Dummy data for demonstration. In a real application, this would come from a database.
        return {
            "Corn": {
                MicronutrientName.ZINC: MicronutrientRequirement(
                    crop_name="Corn",
                    micronutrient=MicronutrientName.ZINC,
                    required_amount_per_ton_yield_g=40.0,
                    critical_leaf_concentration_ppm=20.0,
                    optimal_ph_range_min=6.0,
                    optimal_ph_range_max=7.5,
                    notes="Corn is highly sensitive to Zinc deficiency."
                ),
                MicronutrientName.BORON: MicronutrientRequirement(
                    crop_name="Corn",
                    micronutrient=MicronutrientName.BORON,
                    required_amount_per_ton_yield_g=10.0,
                    critical_leaf_concentration_ppm=5.0,
                    optimal_ph_range_min=5.5,
                    optimal_ph_range_max=7.0,
                    notes="Boron is important for pollination and kernel set."
                ),
            },
            "Soybean": {
                MicronutrientName.IRON: MicronutrientRequirement(
                    crop_name="Soybean",
                    micronutrient=MicronutrientName.IRON,
                    required_amount_per_ton_yield_g=100.0,
                    critical_leaf_concentration_ppm=50.0,
                    optimal_ph_range_min=6.0,
                    optimal_ph_range_max=7.0,
                    notes="Soybeans are susceptible to Iron Chlorosis in high pH soils."
                ),
                MicronutrientName.MANGANESE: MicronutrientRequirement(
                    crop_name="Soybean",
                    micronutrient=MicronutrientName.MANGANESE,
                    required_amount_per_ton_yield_g=30.0,
                    critical_leaf_concentration_ppm=20.0,
                    optimal_ph_range_min=5.5,
                    optimal_ph_range_max=6.5,
                    notes="Manganese deficiency is common in high organic matter soils."
                ),
            },
            "Wheat": {
                MicronutrientName.COPPER: MicronutrientRequirement(
                    crop_name="Wheat",
                    micronutrient=MicronutrientName.COPPER,
                    required_amount_per_ton_yield_g=5.0,
                    critical_leaf_concentration_ppm=3.0,
                    optimal_ph_range_min=6.0,
                    optimal_ph_range_max=7.5,
                    notes="Copper deficiency can lead to poor grain filling."
                ),
                MicronutrientName.ZINC: MicronutrientRequirement(
                    crop_name="Wheat",
                    micronutrient=MicronutrientName.ZINC,
                    required_amount_per_ton_yield_g=20.0,
                    critical_leaf_concentration_ppm=15.0,
                    optimal_ph_range_min=6.0,
                    optimal_ph_range_max=7.5,
                    notes="Zinc is important for early growth and tillering."
                ),
            },
        }

    def get_crop_micronutrient_requirements(self, crop_name: str) -> Dict[MicronutrientName, MicronutrientRequirement]:
        """Retrieves all micronutrient requirements for a given crop."""
        return self._crop_requirements.get(crop_name, {})

    def get_specific_micronutrient_requirement(self, crop_name: str, micronutrient_name: MicronutrientName) -> Optional[MicronutrientRequirement]:
        """Retrieves a specific micronutrient requirement for a given crop."""
        return self._crop_requirements.get(crop_name, {}).get(micronutrient_name)
