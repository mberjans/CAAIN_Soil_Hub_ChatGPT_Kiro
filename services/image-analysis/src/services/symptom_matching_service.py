import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from services.image_analysis.src.models.symptom_models import NutrientDeficiencySymptom

class SymptomMatchingService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def match_symptoms(self, detected_characteristics: List[str], crop_type: str) -> List[Dict[str, Any]]:
        """
        Matches detected visual characteristics against the symptom database for a given crop type.

        Args:
            detected_characteristics: A list of visual characteristics detected from an image.
            crop_type: The type of crop (e.g., 'Corn', 'Soybean').

        Returns:
            A list of potential nutrient deficiencies with match scores.
        """
        potential_deficiencies = []

        # Query for symptoms relevant to the crop type
        symptoms_in_db = self.db_session.query(NutrientDeficiencySymptom).filter_by(crop_type=crop_type).all()

        for symptom_record in symptoms_in_db:
            match_score = self._calculate_match_score(
                detected_characteristics,
                symptom_record.visual_characteristics
            )

            if match_score >= symptom_record.confidence_score_threshold:
                potential_deficiencies.append({
                    "nutrient": symptom_record.nutrient,
                    "symptom_name": symptom_record.symptom_name,
                    "description": symptom_record.description,
                    "affected_parts": symptom_record.affected_parts,
                    "visual_characteristics": symptom_record.visual_characteristics,
                    "severity_levels": symptom_record.severity_levels,
                    "match_score": match_score,
                    "confidence_threshold": symptom_record.confidence_score_threshold
                })
        
        # Sort by match score in descending order
        potential_deficiencies.sort(key=lambda x: x["match_score"], reverse=True)

        return potential_deficiencies

    def _calculate_match_score(self, detected: List[str], reference: List[str]) -> float:
        """
        Calculates a match score between detected characteristics and reference characteristics.
        This is a simple overlap-based scoring. Can be enhanced with NLP techniques.
        """
        if not detected or not reference:
            return 0.0

        detected_set = set(char.lower() for char in detected)
        reference_set = set(char.lower() for char in reference)

        intersection = len(detected_set.intersection(reference_set))
        union = len(detected_set.union(reference_set))

        # Jaccard index for similarity
        if union == 0:
            return 0.0
        return float(intersection) / union
