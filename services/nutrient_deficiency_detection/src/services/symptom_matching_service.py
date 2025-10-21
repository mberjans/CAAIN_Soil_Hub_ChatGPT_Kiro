from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..models.deficiency_models import Nutrient, Severity, PlantPart, Symptom, DetectedDeficiency
from ..models.sqlalchemy_models import NutrientDeficiencySymptomORM

class SymptomMatchingService:
    def __init__(self, db: Session):
        self.db = db

    def match_symptoms(
        self,
        observed_symptoms: List[Symptom],
        crop_type: str,
        min_confidence: float = 0.3
    ) -> List[DetectedDeficiency]:
        """
        Matches observed symptoms against the symptom database to identify potential nutrient deficiencies.

        Args:
            observed_symptoms: A list of observed Symptom objects.
            crop_type: The type of crop being analyzed (e.g., 'corn', 'soybean').
            min_confidence: Minimum confidence score for a deficiency to be returned.

        Returns:
            A list of DetectedDeficiency objects, sorted by confidence.
        """
        potential_deficiencies: Dict[Nutrient, Dict[str, Any]] = {}

        # Query all known symptoms for the given crop type
        known_symptoms_orms = self.db.query(NutrientDeficiencySymptomORM).filter_by(crop_type=crop_type).all()

        for observed_symptom in observed_symptoms:
            for known_symptom_orm in known_symptoms_orms:
                # Calculate a match score for each known symptom against the observed symptom
                score = self._calculate_match_score(observed_symptom, known_symptom_orm)

                if score > 0:
                    nutrient = known_symptom_orm.nutrient
                    if nutrient not in potential_deficiencies:
                        potential_deficiencies[nutrient] = {
                            "total_score": 0.0,
                            "matched_symptoms": [],
                            "max_severity": Severity.MILD
                        }
                    
                    potential_deficiencies[nutrient]["total_score"] += score
                    potential_deficiencies[nutrient]["matched_symptoms"].append(known_symptom_orm.symptom_name)
                    
                    # Update max severity if current known symptom is more severe
                    if known_symptom_orm.typical_severity.value > potential_deficiencies[nutrient]["max_severity"].value:
                        potential_deficiencies[nutrient]["max_severity"] = known_symptom_orm.typical_severity

        detected_deficiencies: List[DetectedDeficiency] = []
        for nutrient, data in potential_deficiencies.items():
            # Normalize score to a confidence level (0-1)
            # This is a simple normalization; more complex logic might be needed
            confidence = min(data["total_score"] / len(observed_symptoms), 1.0) # Simple: score per observed symptom
            
            if confidence >= min_confidence:
                detected_deficiencies.append(
                    DetectedDeficiency(
                        nutrient=nutrient,
                        confidence=confidence,
                        severity=data["max_severity"],
                        affected_area_percent=0.0, # This would typically come from image analysis
                        symptoms=[Symptom(name=s_name, location="", description="") for s_name in data["matched_symptoms"]], # Placeholder
                        source="symptom_matching_service"
                    )
                )
        
        # Sort by confidence in descending order
        detected_deficiencies.sort(key=lambda d: d.confidence, reverse=True)
        return detected_deficiencies

    def _calculate_match_score(self, observed: Symptom, known: NutrientDeficiencySymptomORM) -> float:
        """
        Calculates a match score between an observed symptom and a known symptom.
        A higher score indicates a better match.
        """
        score = 0.0

        # Match symptom name (exact match gives highest score)
        if self._pattern_match(observed.name, known.symptom_name):
            score += 1.0
        
        # Match visual characteristics (partial matches)
        for obs_char in observed.description.lower().split() if observed.description else []:
            for known_char in known.visual_characteristics:
                if obs_char in known_char.lower() or known_char.lower() in obs_char:
                    score += 0.2 # Partial match bonus

        # Match affected plant parts (partial matches)
        if observed.location:
            for known_part in known.affected_parts:
                if self._pattern_match(observed.location, known_part.value):
                    score += 0.5 # Direct match on location/part

        # Consider description similarity (simple keyword matching for now)
        if observed.description and known.description:
            obs_desc_words = set(observed.description.lower().split())
            known_desc_words = set(known.description.lower().split())
            common_words = len(obs_desc_words.intersection(known_desc_words))
            score += common_words * 0.1 # Small bonus for common words

        return score

    def _pattern_match(self, text: str, pattern: str) -> bool:
        """
        Custom pattern matching function to avoid regex.
        Checks if pattern is a substring of text (case-insensitive).
        """
        return pattern.lower() in text.lower()
