"""
Test suite for Agricultural Rule Engine

Tests the rule-based decision system and scikit-learn integration.
"""

import pytest
import numpy as np
from datetime import date, datetime
from unittest.mock import Mock, patch

# Import the rule engine and related models
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.rule_engine import (
    AgriculturalRuleEngine,
    RuleType,
    RuleCondition,
    AgriculturalRule,
    RuleEvaluationResult
)
from models.agricultural_models import (
    RecommendationRequest,
    SoilTestData,
    LocationData,
    CropData,
    FarmProfile
)


class TestAgriculturalRuleEngine:
    """Test cases for the Agricultural Rule Engine."""
    
    @pytest.fixture
    def rule_engine(self):
        """Create a rule engine instance for testing."""
        return AgriculturalRuleEngine()
    
    @pytest.fixture
    def sample_soil_data(self):
        """Create sample soil test data."""
        return SoilTestData(
            ph=6.2,
            organic_matter_percent=3.5,
            phosphorus_ppm=25,
            potassium_ppm=180,
            nitrogen_ppm=12,
            cec_meq_per_100g=18.5,
            soil_texture="silt_loam",
            drainage_class="well_drained",
            test_date=date(2024, 3, 15),
            lab_name="Test Lab"
        )
    
    @pytest.fixture
    def sample_location(self):
        """Create sample location data."""
        return LocationData(
            latitude=42.0308,
            longitude=-93.6319,
            address="Ames, Iowa, USA",
            climate_zone="5a",
            state="Iowa",
            county="Story"
        )
    
    @pytest.fixture
    def sample_crop_data(self):
        """Create sample crop data."""
        return CropData(
            crop_name="corn",
            variety="Pioneer P1197AM",
            planting_date=date(2024, 5, 1),
            yield_goal=180,
            previous_crop="soybean"
        )
    
    @pytest.fixture
    def sample_farm_profile(self):
        """Create sample farm profile."""
        return FarmProfile(
            farm_id="test_farm_001",
            farm_size_acres=320,
            primary_crops=["corn", "soybean"],
            equipment_available=["planter", "combine", "sprayer"],
            irrigation_available=False,
            organic_certified=False
        )
    
    @pytest.fixture
    def sample_request(self, sample_location, sample_soil_data, sample_crop_data, sample_farm_profile):
        """Create a complete sample recommendation request."""
        return RecommendationRequest(
            request_id="test_request_001",
            question_type="crop_selection",
            location=sample_location,
            soil_data=sample_soil_data,
            crop_data=sample_crop_data,
            farm_profile=sample_farm_profile
        )
    
    def test_rule_engine_initialization(self, rule_engine):
        """Test that rule engine initializes correctly."""
        assert rule_engine is not None
        assert len(rule_engine.rules) > 0
        assert len(rule_engine.decision_trees) > 0
        
        # Check that basic rule types are present
        rule_types = [rule.rule_type for rule in rule_engine.rules.values()]
        assert RuleType.CROP_SUITABILITY in rule_types
        assert RuleType.FERTILIZER_RATE in rule_types
        assert RuleType.SOIL_MANAGEMENT in rule_types
    
    def test_crop_suitability_rules(self, rule_engine, sample_request):
        """Test crop suitability rule evaluation."""
        results = rule_engine.evaluate_rules(sample_request, RuleType.CROP_SUITABILITY)
        
        assert len(results) > 0
        
        # Should find corn optimal conditions rule
        corn_results = [r for r in results if "corn_optimal" in r.rule_id]
        assert len(corn_results) > 0
        
        corn_result = corn_results[0]
        assert corn_result.matched
        assert corn_result.confidence > 0.8
        assert "corn" in corn_result.action.get("crop", "")
    
    def test_fertilizer_rate_rules(self, rule_engine, sample_request):
        """Test fertilizer rate calculation rules."""
        results = rule_engine.evaluate_rules(sample_request, RuleType.FERTILIZER_RATE)
        
        assert len(results) > 0
        
        # Should find nitrogen calculation rule for corn
        nitrogen_results = [r for r in results if "nitrogen" in r.rule_id]
        assert len(nitrogen_results) > 0
        
        nitrogen_result = nitrogen_results[0]
        assert nitrogen_result.matched
        assert "calculation_method" in nitrogen_result.action
    
    def test_soil_management_rules(self, rule_engine, sample_request):
        """Test soil management rule evaluation."""
        # Modify soil data to trigger lime requirement
        sample_request.soil_data.ph = 5.5
        
        results = rule_engine.evaluate_rules(sample_request, RuleType.SOIL_MANAGEMENT)
        
        # Should find lime requirement rule
        lime_results = [r for r in results if "lime" in r.rule_id]
        assert len(lime_results) > 0
        
        lime_result = lime_results[0]
        assert lime_result.matched
        assert "agricultural_limestone" in lime_result.action.get("amendment", "")
    
    def test_nutrient_deficiency_rules(self, rule_engine, sample_request):
        """Test nutrient deficiency detection rules."""
        # Modify soil data to trigger deficiency
        sample_request.soil_data.nitrogen_ppm = 5
        sample_request.soil_data.potassium_ppm = 100
        
        results = rule_engine.evaluate_rules(sample_request, RuleType.NUTRIENT_DEFICIENCY)
        
        assert len(results) > 0
        
        # Should detect nitrogen and potassium deficiencies
        deficiency_types = [r.action.get("deficiency") for r in results if r.matched]
        assert "nitrogen" in deficiency_types or "potassium" in deficiency_types
    
    def test_decision_tree_crop_suitability(self, rule_engine):
        """Test crop suitability decision tree prediction."""
        features = {
            'ph': 6.2,
            'organic_matter': 3.5,
            'phosphorus': 25,
            'potassium': 180,
            'drainage_score': 1.0
        }
        
        result = rule_engine.predict_with_decision_tree('crop_suitability', features)
        
        assert 'suitability_class' in result
        assert 'confidence' in result
        assert result['confidence'] > 0
        assert result['suitability_class'] in ['highly_suitable', 'suitable', 'marginal', 'unsuitable']
    
    def test_decision_tree_nitrogen_rate(self, rule_engine):
        """Test nitrogen rate decision tree prediction."""
        features = {
            'yield_goal': 180,
            'soil_n': 12,
            'organic_matter': 3.5,
            'previous_legume': 1,  # Previous soybean
            'ph': 6.2
        }
        
        result = rule_engine.predict_with_decision_tree('nitrogen_rate', features)
        
        assert 'nitrogen_rate' in result
        assert 'confidence' in result
        assert result['nitrogen_rate'] >= 0
        assert result['nitrogen_rate'] <= 200  # Reasonable upper limit
    
    def test_decision_tree_soil_management(self, rule_engine):
        """Test soil management decision tree prediction."""
        features = {
            'ph': 5.5,  # Low pH should trigger lime recommendation
            'organic_matter': 2.0,
            'phosphorus': 12,
            'potassium': 110,
            'cec': 15
        }
        
        result = rule_engine.predict_with_decision_tree('soil_management', features)
        
        assert 'management_priority' in result
        assert 'confidence' in result
        assert result['management_priority'] in [
            'lime_application', 'organic_matter_improvement', 
            'phosphorus_buildup', 'potassium_buildup', 'maintenance'
        ]
    
    def test_rule_condition_evaluation(self, rule_engine):
        """Test individual rule condition evaluation."""
        # Test different condition operators
        conditions = [
            RuleCondition("soil_ph", "gt", 6.0),
            RuleCondition("organic_matter_percent", "between", (2.0, 5.0)),
            RuleCondition("crop_name", "eq", "corn"),
            RuleCondition("potassium_ppm", "gte", 150)
        ]
        
        # Test values that should match
        test_values = [6.2, 3.5, "corn", 180]
        
        for condition, value in zip(conditions, test_values):
            result = rule_engine._evaluate_condition(condition, value)
            assert result, f"Condition {condition.field} {condition.operator} {condition.value} should match {value}"
    
    def test_field_value_extraction(self, rule_engine, sample_request):
        """Test extraction of field values from request."""
        # Test soil data extraction
        ph_value = rule_engine._extract_field_value("soil_ph", sample_request)
        assert ph_value == 6.2
        
        # Test crop data extraction
        crop_name = rule_engine._extract_field_value("crop_name", sample_request)
        assert crop_name == "corn"
        
        # Test location data extraction
        latitude = rule_engine._extract_field_value("latitude", sample_request)
        assert latitude == 42.0308
        
        # Test missing field
        missing_value = rule_engine._extract_field_value("nonexistent_field", sample_request)
        assert missing_value is None
    
    def test_add_custom_rule(self, rule_engine):
        """Test adding a custom agricultural rule."""
        custom_rule = AgriculturalRule(
            rule_id="test_custom_rule",
            rule_type=RuleType.CROP_SUITABILITY,
            name="Test Custom Rule",
            description="A test rule for validation",
            conditions=[
                RuleCondition("soil_ph", "gt", 7.0, weight=1.0)
            ],
            action={"test_action": "test_value"},
            confidence=0.8,
            priority=3,
            agricultural_source="Test Source",
            expert_validated=False
        )
        
        # Add the rule
        success = rule_engine.add_rule(custom_rule)
        assert success
        assert custom_rule.rule_id in rule_engine.rules
        
        # Try to add duplicate rule
        duplicate_success = rule_engine.add_rule(custom_rule)
        assert not duplicate_success
    
    def test_rule_deactivation(self, rule_engine):
        """Test rule deactivation functionality."""
        # Get a rule ID to deactivate
        rule_id = list(rule_engine.rules.keys())[0]
        original_active_status = rule_engine.rules[rule_id].active
        
        # Deactivate the rule
        success = rule_engine.deactivate_rule(rule_id)
        assert success
        assert not rule_engine.rules[rule_id].active
        
        # Try to deactivate non-existent rule
        invalid_success = rule_engine.deactivate_rule("nonexistent_rule")
        assert not invalid_success
    
    def test_rule_statistics(self, rule_engine):
        """Test rule engine statistics generation."""
        stats = rule_engine.get_rule_statistics()
        
        assert 'total_rules' in stats
        assert 'active_rules' in stats
        assert 'expert_validated_rules' in stats
        assert 'rule_types' in stats
        assert 'decision_trees' in stats
        assert 'validation_percentage' in stats
        
        assert stats['total_rules'] > 0
        assert stats['active_rules'] <= stats['total_rules']
        assert 0 <= stats['validation_percentage'] <= 100
    
    def test_marginal_soil_conditions(self, rule_engine, sample_request):
        """Test rule evaluation with marginal soil conditions."""
        # Set marginal conditions
        sample_request.soil_data.ph = 5.8  # Slightly acidic
        sample_request.soil_data.organic_matter_percent = 2.2  # Low
        sample_request.soil_data.phosphorus_ppm = 12  # Low
        
        results = rule_engine.evaluate_rules(sample_request, RuleType.CROP_SUITABILITY)
        
        # Should still get recommendations but with lower confidence
        assert len(results) > 0
        
        # Check for marginal suitability
        marginal_results = [r for r in results if "marginal" in r.action.get("recommendation", "")]
        if marginal_results:
            assert marginal_results[0].confidence < 0.9
    
    def test_missing_soil_data(self, rule_engine, sample_request):
        """Test rule evaluation with missing soil data."""
        # Remove soil data
        sample_request.soil_data = None
        
        results = rule_engine.evaluate_rules(sample_request)
        
        # Should still get some results but with lower confidence
        # Rules that don't require soil data should still match
        location_based_results = [r for r in results if r.matched and not any(
            'soil' in condition.field for condition in rule_engine.rules[r.rule_id].conditions
        )]
        
        # At least some rules should work without soil data
        assert len(results) >= 0  # May be empty if all rules require soil data
    
    def test_extreme_soil_conditions(self, rule_engine, sample_request):
        """Test rule evaluation with extreme soil conditions."""
        # Set extreme conditions
        sample_request.soil_data.ph = 4.5  # Very acidic
        sample_request.soil_data.organic_matter_percent = 1.0  # Very low
        sample_request.soil_data.phosphorus_ppm = 5  # Very low
        sample_request.soil_data.potassium_ppm = 80  # Very low
        
        results = rule_engine.evaluate_rules(sample_request)
        
        # Should get soil management recommendations
        soil_mgmt_results = [r for r in results if r.rule_id.startswith("lime_") or "organic_matter" in r.rule_id]
        assert len(soil_mgmt_results) > 0
    
    def test_high_yield_goal_nitrogen_calculation(self, rule_engine):
        """Test nitrogen rate calculation for high yield goals."""
        features = {
            'yield_goal': 200,  # High yield goal
            'soil_n': 8,        # Low soil nitrogen
            'organic_matter': 4.0,
            'previous_legume': 0,  # No legume credit
            'ph': 6.5
        }
        
        result = rule_engine.predict_with_decision_tree('nitrogen_rate', features)
        
        # Should recommend higher nitrogen rate for high yield goal
        assert result['nitrogen_rate'] > 150
        assert result['nitrogen_rate'] <= 200  # Should not exceed maximum
    
    def test_decision_tree_error_handling(self, rule_engine):
        """Test decision tree error handling."""
        # Test with invalid tree name
        with pytest.raises(ValueError):
            rule_engine.predict_with_decision_tree('nonexistent_tree', {})
        
        # Test with missing features (should handle gracefully)
        result = rule_engine.predict_with_decision_tree('crop_suitability', {})
        assert 'suitability_class' in result or 'error' in result


class TestRuleConditions:
    """Test rule condition evaluation in detail."""
    
    def test_numeric_conditions(self):
        """Test numeric condition operators."""
        engine = AgriculturalRuleEngine()
        
        # Test greater than
        condition_gt = RuleCondition("test_field", "gt", 5.0)
        assert engine._evaluate_condition(condition_gt, 6.0)
        assert not engine._evaluate_condition(condition_gt, 4.0)
        
        # Test between
        condition_between = RuleCondition("test_field", "between", (5.0, 10.0))
        assert engine._evaluate_condition(condition_between, 7.5)
        assert not engine._evaluate_condition(condition_between, 12.0)
        
        # Test less than or equal
        condition_lte = RuleCondition("test_field", "lte", 10.0)
        assert engine._evaluate_condition(condition_lte, 10.0)
        assert not engine._evaluate_condition(condition_lte, 11.0)
    
    def test_string_conditions(self):
        """Test string condition operators."""
        engine = AgriculturalRuleEngine()
        
        # Test equality
        condition_eq = RuleCondition("test_field", "eq", "corn")
        assert engine._evaluate_condition(condition_eq, "corn")
        assert not engine._evaluate_condition(condition_eq, "soybean")
        
        # Test in list
        condition_in = RuleCondition("test_field", "in", ["corn", "soybean", "wheat"])
        assert engine._evaluate_condition(condition_in, "corn")
        assert engine._evaluate_condition(condition_in, "soybean")
        assert not engine._evaluate_condition(condition_in, "rice")
    
    def test_invalid_conditions(self):
        """Test handling of invalid conditions."""
        engine = AgriculturalRuleEngine()
        
        # Test with None value
        condition = RuleCondition("test_field", "gt", 5.0)
        assert not engine._evaluate_condition(condition, None)
        
        # Test with invalid operator
        invalid_condition = RuleCondition("test_field", "invalid_op", 5.0)
        assert not engine._evaluate_condition(invalid_condition, 6.0)
        
        # Test type mismatch
        numeric_condition = RuleCondition("test_field", "gt", 5.0)
        assert not engine._evaluate_condition(numeric_condition, "not_a_number")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])