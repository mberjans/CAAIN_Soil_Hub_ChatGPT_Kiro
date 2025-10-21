from typing import Dict, List
from ..models.micronutrient_models import Micronutrient, MicronutrientName
from ..models.soil_test_models import SoilTestResult, SoilTestMicronutrientResult

class MicronutrientSoilTestService:
    def __init__(self):
        # This will eventually be loaded from a database or configuration
        self.micronutrient_thresholds: Dict[MicronutrientName, Micronutrient] = self._load_dummy_micronutrient_data()

    def _load_dummy_micronutrient_data(self) -> Dict[MicronutrientName, Micronutrient]:
        # Dummy data for demonstration. Replace with actual data loading.
        return {
            MicronutrientName.BORON: Micronutrient(
                name=MicronutrientName.BORON,
                symbol="B",
                roles=[],
                soil_concentration_deficient_ppm=0.5,
                soil_concentration_toxic_ppm=2.0,
            ),
            MicronutrientName.ZINC: Micronutrient(
                name=MicronutrientName.ZINC,
                symbol="Zn",
                roles=[],
                soil_concentration_deficient_ppm=1.0,
                soil_concentration_toxic_ppm=5.0,
            ),
            MicronutrientName.IRON: Micronutrient(
                name=MicronutrientName.IRON,
                symbol="Fe",
                roles=[],
                soil_concentration_deficient_ppm=2.5,
                soil_concentration_toxic_ppm=20.0,
            ),
            MicronutrientName.MANGANESE: Micronutrient(
                name=MicronutrientName.MANGANESE,
                symbol="Mn",
                roles=[],
                soil_concentration_deficient_ppm=1.0,
                soil_concentration_toxic_ppm=10.0,
            ),
            MicronutrientName.COPPER: Micronutrient(
                name=MicronutrientName.COPPER,
                symbol="Cu",
                roles=[],
                soil_concentration_deficient_ppm=0.2,
                soil_concentration_toxic_ppm=5.0,
            ),
            MicronutrientName.MOLYBDENUM: Micronutrient(
                name=MicronutrientName.MOLYBDENUM,
                symbol="Mo",
                roles=[],
                soil_concentration_deficient_ppm=0.05,
                soil_concentration_toxic_ppm=0.5,
            ),
            MicronutrientName.CHLORINE: Micronutrient(
                name=MicronutrientName.CHLORINE,
                symbol="Cl",
                roles=[],
                soil_concentration_deficient_ppm=10.0,
                soil_concentration_toxic_ppm=100.0,
            ),
            MicronutrientName.NICKEL: Micronutrient(
                name=MicronutrientName.NICKEL,
                symbol="Ni",
                roles=[],
                soil_concentration_deficient_ppm=0.1,
                soil_concentration_toxic_ppm=1.0,
            ),
        }

    def analyze_soil_test_for_micronutrients(self, soil_test_result: SoilTestResult) -> Dict[MicronutrientName, str]:
        analysis_results = {}
        for micro_name, micro_result in soil_test_result.micronutrients.items():
            thresholds = self.micronutrient_thresholds.get(micro_name)
            if not thresholds:
                analysis_results[micro_name] = "No thresholds defined"
                continue

            concentration = micro_result.concentration_ppm

            if thresholds.soil_concentration_deficient_ppm is not None and concentration < thresholds.soil_concentration_deficient_ppm:
                analysis_results[micro_name] = "Deficient"
            elif thresholds.soil_concentration_toxic_ppm is not None and concentration > thresholds.soil_concentration_toxic_ppm:
                analysis_results[micro_name] = "Toxic"
            elif thresholds.soil_concentration_deficient_ppm is not None and thresholds.soil_concentration_toxic_ppm is not None and \
                 thresholds.soil_concentration_deficient_ppm <= concentration <= thresholds.soil_concentration_toxic_ppm:
                analysis_results[micro_name] = "Optimal"
            else:
                analysis_results[micro_name] = "Unknown Status"
        return analysis_results
