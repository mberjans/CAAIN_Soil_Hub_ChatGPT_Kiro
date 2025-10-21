from ..models.micronutrient_models import Micronutrient, MicronutrientRecommendation, SoilTest, CropMicronutrientRequirement

class MicronutrientService:

    def __init__(self):
        self.crop_requirements: list[CropMicronutrientRequirement] = [
            CropMicronutrientRequirement(
                crop_name="corn",
                micronutrient=Micronutrient(name="Zinc", symbol="Zn"),
                sufficient_range=(2.0, 70.0),
                unit="ppm"
            )
        ]

    def get_recommendations(self) -> list[MicronutrientRecommendation]:
        # Placeholder
        return []

    def get_crop_requirement(self, crop_name: str, micronutrient_symbol: str) -> Optional[CropMicronutrientRequirement]:
        for req in self.crop_requirements:
            if req.crop_name == crop_name and req.micronutrient.symbol == micronutrient_symbol:
                return req
        return None

    def process_soil_test(self, soil_test: SoilTest, crop_name: str) -> list[MicronutrientRecommendation]:
        recommendations = []
        for level in soil_test.micronutrient_levels:
            requirement = self.get_crop_requirement(crop_name, level.micronutrient.symbol)
            if requirement:
                if level.level < requirement.sufficient_range[0]:
                    recommendations.append(
                        MicronutrientRecommendation(
                            micronutrient=level.micronutrient,
                            recommendation=f"Deficient in {level.micronutrient.name}. Consider applying fertilizer."
                        )
                    )
                elif level.level > requirement.sufficient_range[1]:
                    recommendations.append(
                        MicronutrientRecommendation(
                            micronutrient=level.micronutrient,
                            recommendation=f"Toxic level of {level.micronutrient.name}. Avoid application."
                        )
                    )
        return recommendations
