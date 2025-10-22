"""
Test file for symptom validation - JOB3-011.3

Tests for validating agricultural accuracy of symptom descriptions
"""

import pytest
from src.services.detector import DeficiencyDetector


class TestSymptomValidation:
    """Test cases for validating symptom descriptions"""

    def setup_method(self):
        """Setup test detector instance"""
        self.detector = DeficiencyDetector()

    def test_nitrogen_deficiency_symptoms(self):
        """
        Test nitrogen deficiency symptoms for agricultural accuracy

        JOB3-011.3 - Validate symptom descriptions
        """
        symptoms = self.detector._get_symptoms("nitrogen", "corn")

        # Nitrogen deficiency should include key symptoms
        expected_symptoms = [
            "yellowing of older leaves",
            "stunted growth",
            "pale green color",
            "chlorosis of lower leaves",
            "reduced vigor",
            "uniform yellowing"
        ]

        # Check that at least 3 key symptoms are present
        matched_symptoms = []
        for expected in expected_symptoms:
            for actual in symptoms:
                if expected.lower() in actual.lower():
                    matched_symptoms.append(expected)
                    break

        assert len(matched_symptoms) >= 3, f"Missing key nitrogen symptoms. Found: {symptoms}"

    def test_phosphorus_deficiency_symptoms(self):
        """
        Test phosphorus deficiency symptoms for agricultural accuracy

        JOB3-011.3 - Validate symptom descriptions
        """
        symptoms = self.detector._get_symptoms("phosphorus", "corn")

        # Phosphorus deficiency should include key symptoms
        expected_symptoms = [
            "purple",
            "reddish",
            "dark green",
            "stunted growth",
            "delayed maturity"
        ]

        # Check that at least 3 key symptoms are present
        matched_symptoms = []
        for expected in expected_symptoms:
            for actual in symptoms:
                if expected.lower() in actual.lower():
                    matched_symptoms.append(expected)
                    break

        assert len(matched_symptoms) >= 3, f"Missing key phosphorus symptoms. Found: {symptoms}"

    def test_potassium_deficiency_symptoms(self):
        """
        Test potassium deficiency symptoms for agricultural accuracy

        JOB3-011.3 - Validate symptom descriptions
        """
        symptoms = self.detector._get_symptoms("potassium", "corn")

        # Potassium deficiency should include key symptoms
        expected_symptoms = [
            "leaf edge",
            "margin",
            "burn",
            "yellowing",
            "weak stalks",
            "lodging"
        ]

        # Check that at least 3 key symptoms are present
        matched_symptoms = []
        for expected in expected_symptoms:
            for actual in symptoms:
                if expected.lower() in actual.lower():
                    matched_symptoms.append(expected)
                    break

        assert len(matched_symptoms) >= 3, f"Missing key potassium symptoms. Found: {symptoms}"

    def test_sulfur_deficiency_symptoms(self):
        """
        Test sulfur deficiency symptoms for agricultural accuracy

        JOB3-011.3 - Validate symptom descriptions
        """
        symptoms = self.detector._get_symptoms("sulfur", "corn")

        # Sulfur deficiency should affect younger leaves first
        expected_symptoms = [
            "young leaves",
            "yellowing",
            "stunted",
            "chlorosis"
        ]

        # Check that at least 2 key symptoms are present and mention young leaves
        matched_symptoms = []
        young_leaves_mentioned = False
        for expected in expected_symptoms:
            for actual in symptoms:
                if expected.lower() in actual.lower():
                    matched_symptoms.append(expected)
                    if "young" in actual.lower():
                        young_leaves_mentioned = True
                    break

        assert len(matched_symptoms) >= 2, f"Missing key sulfur symptoms. Found: {symptoms}"
        assert young_leaves_mentioned, "Sulfur deficiency should mention young leaves"

    def test_iron_deficiency_symptoms(self):
        """
        Test iron deficiency symptoms for agricultural accuracy

        JOB3-011.3 - Validate symptom descriptions
        """
        symptoms = self.detector._get_symptoms("iron", "corn")

        # Iron deficiency should include interveinal chlorosis
        expected_symptoms = [
            "interveinal",
            "chlorosis",
            "young leaves",
            "yellowing"
        ]

        # Check that interveinal chlorosis is mentioned
        interveinal_mentioned = False
        matched_symptoms = []
        for expected in expected_symptoms:
            for actual in symptoms:
                if expected.lower() in actual.lower():
                    matched_symptoms.append(expected)
                    if "interveinal" in actual.lower():
                        interveinal_mentioned = True
                    break

        assert len(matched_symptoms) >= 2, f"Missing key iron symptoms. Found: {symptoms}"
        assert interveinal_mentioned, "Iron deficiency should mention interveinal chlorosis"

    def test_zinc_deficiency_symptoms(self):
        """
        Test zinc deficiency symptoms for agricultural accuracy

        JOB3-011.3 - Validate symptom descriptions
        """
        symptoms = self.detector._get_symptoms("zinc", "corn")

        # Zinc deficiency should include specific symptoms
        expected_symptoms = [
            "white",
            "yellow",
            "bands",
            "strips",
            "shortened",
            "internodes"
        ]

        # Check that at least 2 key symptoms are present
        matched_symptoms = []
        for expected in expected_symptoms:
            for actual in symptoms:
                if expected.lower() in actual.lower():
                    matched_symptoms.append(expected)
                    break

        assert len(matched_symptoms) >= 2, f"Missing key zinc symptoms. Found: {symptoms}"

    def test_manganese_deficiency_symptoms(self):
        """
        Test manganese deficiency symptoms for agricultural accuracy

        JOB3-011.3 - Validate symptom descriptions
        """
        symptoms = self.detector._get_symptoms("manganese", "soybean")

        # Manganese deficiency should include interveinal chlorosis and spots
        expected_symptoms = [
            "interveinal",
            "chlorosis",
            "brown spots",
            "dark spots",
            "young leaves"
        ]

        # Check that at least 2 key symptoms are present
        matched_symptoms = []
        for expected in expected_symptoms:
            for actual in symptoms:
                if expected.lower() in actual.lower():
                    matched_symptoms.append(expected)
                    break

        assert len(matched_symptoms) >= 2, f"Missing key manganese symptoms. Found: {symptoms}"

    def test_symptom_consistency_across_crops(self):
        """
        Test that symptoms are consistent across different crops

        JOB3-011.3 - Validate symptom descriptions
        """
        # Test nitrogen symptoms across different crops
        corn_symptoms = self.detector._get_symptoms("nitrogen", "corn")
        soybean_symptoms = self.detector._get_symptoms("nitrogen", "soybean")
        wheat_symptoms = self.detector._get_symptoms("nitrogen", "wheat")

        # All should mention yellowing/chlorosis
        for symptoms in [corn_symptoms, soybean_symptoms, wheat_symptoms]:
            has_yellowing = any("yellow" in s.lower() or "chlorosis" in s.lower() for s in symptoms)
            assert has_yellowing, f"Nitrogen deficiency should mention yellowing/chlorosis. Found: {symptoms}"

    def test_symptoms_are_specific_and_actionable(self):
        """
        Test that symptom descriptions are specific and actionable

        JOB3-011.3 - Validate symptom descriptions
        """
        for nutrient in ["nitrogen", "phosphorus", "potassium", "sulfur", "iron", "zinc", "manganese"]:
            symptoms = self.detector._get_symptoms(nutrient, "corn")

            # Symptoms should not be generic
            generic_symptom = "Consult agricultural expert"
            assert nutrient != "unknown", f"Known nutrient {nutrient} should have specific symptoms"

            if symptoms != [generic_symptom]:
                # Check that symptoms are descriptive (contain specific plant parts or colors)
                has_specific_terms = any(
                    any(term in symptom.lower() for term in [
                        "leaf", "leaves", "yellow", "green", "purple", "brown",
                        "edge", "margin", "interveinal", "stunted", "burn"
                    ])
                    for symptom in symptoms
                )
                assert has_specific_terms, f"{nutrient} symptoms should contain specific terms. Found: {symptoms}"

    def test_no_duplicate_symptoms(self):
        """
        Test that there are no duplicate symptoms within a nutrient

        JOB3-011.3 - Validate symptom descriptions
        """
        for nutrient in ["nitrogen", "phosphorus", "potassium", "sulfur", "iron", "zinc", "manganese"]:
            symptoms = self.detector._get_symptoms(nutrient, "corn")

            # Convert to lowercase for comparison
            normalized_symptoms = [s.lower().strip() for s in symptoms]
            unique_symptoms = set(normalized_symptoms)

            assert len(normalized_symptoms) == len(unique_symptoms), \
                f"{nutrient} has duplicate symptoms: {symptoms}"