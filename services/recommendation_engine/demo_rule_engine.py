#!/usr/bin/env python3
"""
Agricultural Rule Engine Demonstration

This script demonstrates the capabilities of the Agricultural Rule Engine
with scikit-learn integration for farm advisory recommendations.
"""

import sys
import os
from datetime import date
import json

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.rule_engine import AgriculturalRuleEngine, RuleType
from models.agricultural_models import (
    RecommendationRequest,
    SoilTestData,
    LocationData,
    CropData,
    FarmProfile
)


def create_sample_farm_data():
    """Create sample farm data for demonstration."""
    
    # Iowa corn/soybean farm
    iowa_farm = {
        "location": LocationData(
            latitude=42.0308,
            longitude=-93.6319,
            address="Ames, Iowa, USA",
            climate_zone="5a",
            state="Iowa",
            county="Story"
        ),
        "soil_data": SoilTestData(
            ph=6.2,
            organic_matter_percent=3.5,
            phosphorus_ppm=25,
            potassium_ppm=180,
            nitrogen_ppm=12,
            cec_meq_per_100g=18.5,
            soil_texture="silt_loam",
            drainage_class="well_drained",
            test_date=date(2024, 3, 15),
            lab_name="Iowa State Soil Testing Lab"
        ),
        "crop_data": CropData(
            crop_name="corn",
            variety="Pioneer P1197AM",
            planting_date=date(2024, 5, 1),
            yield_goal=180,
            previous_crop="soybean"
        ),
        "farm_profile": FarmProfile(
            farm_id="demo_farm_001",
            farm_size_acres=320,
            primary_crops=["corn", "soybean"],
            equipment_available=["planter", "combine", "sprayer"],
            irrigation_available=False,
            organic_certified=False
        )
    }
    
    # Problematic soil farm
    problem_farm = {
        "location": LocationData(
            latitude=40.7128,
            longitude=-74.0060,
            address="New York, NY, USA",
            climate_zone="6b",
            state="New York",
            county="New York"
        ),
        "soil_data": SoilTestData(
            ph=5.2,  # Acidic
            organic_matter_percent=1.8,  # Low
            phosphorus_ppm=8,  # Very low
            potassium_ppm=95,  # Low
            nitrogen_ppm=5,  # Very low
            cec_meq_per_100g=12.0,
            soil_texture="sandy_loam",
            drainage_class="somewhat_poorly_drained",
            test_date=date(2024, 2, 10),
            lab_name="Regional Soil Lab"
        ),
        "crop_data": CropData(
            crop_name="corn",
            yield_goal=120,  # Lower yield goal due to conditions
            previous_crop="corn"  # No legume credit
        ),
        "farm_profile": FarmProfile(
            farm_id="demo_farm_002",
            farm_size_acres=80,
            primary_crops=["corn"],
            equipment_available=["planter"],
            irrigation_available=False,
            organic_certified=False
        )
    }
    
    return iowa_farm, problem_farm


def demonstrate_rule_evaluation(rule_engine, farm_data, farm_name):
    """Demonstrate rule evaluation for a farm."""
    
    print(f"\n{'='*60}")
    print(f"RULE EVALUATION FOR {farm_name.upper()}")
    print(f"{'='*60}")
    
    # Create recommendation request
    request = RecommendationRequest(
        request_id=f"demo_{farm_name.lower().replace(' ', '_')}",
        question_type="crop_selection",
        **farm_data
    )
    
    # Display farm conditions
    print(f"\nFarm Conditions:")
    print(f"  Location: {farm_data['location'].address}")
    print(f"  Farm Size: {farm_data['farm_profile'].farm_size_acres} acres")
    if farm_data['soil_data']:
        print(f"  Soil pH: {farm_data['soil_data'].ph}")
        print(f"  Organic Matter: {farm_data['soil_data'].organic_matter_percent}%")
        print(f"  Phosphorus: {farm_data['soil_data'].phosphorus_ppm} ppm")
        print(f"  Potassium: {farm_data['soil_data'].potassium_ppm} ppm")
    
    # Evaluate different rule types
    rule_types = [
        (RuleType.CROP_SUITABILITY, "Crop Suitability"),
        (RuleType.FERTILIZER_RATE, "Fertilizer Rate"),
        (RuleType.SOIL_MANAGEMENT, "Soil Management"),
        (RuleType.NUTRIENT_DEFICIENCY, "Nutrient Deficiency")
    ]
    
    for rule_type, type_name in rule_types:
        print(f"\n{type_name} Rules:")
        print("-" * 40)
        
        results = rule_engine.evaluate_rules(request, rule_type)
        
        if results:
            for result in results[:3]:  # Show top 3 results
                rule = rule_engine.rules[result.rule_id]
                print(f"  ✓ {rule.name}")
                print(f"    Confidence: {result.confidence:.2f}")
                print(f"    Action: {result.action}")
                print(f"    Source: {rule.agricultural_source}")
                print()
        else:
            print("  No matching rules found")


def demonstrate_decision_trees(rule_engine, farm_data, farm_name):
    """Demonstrate decision tree predictions."""
    
    print(f"\n{'='*60}")
    print(f"DECISION TREE PREDICTIONS FOR {farm_name.upper()}")
    print(f"{'='*60}")
    
    # Crop Suitability Decision Tree
    print("\nCrop Suitability Analysis:")
    print("-" * 30)
    
    crop_features = {
        'ph': farm_data['soil_data'].ph,
        'organic_matter': farm_data['soil_data'].organic_matter_percent,
        'phosphorus': farm_data['soil_data'].phosphorus_ppm,
        'potassium': farm_data['soil_data'].potassium_ppm,
        'drainage_score': 1.0 if farm_data['soil_data'].drainage_class == "well_drained" else 0.5
    }
    
    try:
        crop_result = rule_engine.predict_with_decision_tree('crop_suitability', crop_features)
        print(f"  Suitability Class: {crop_result.get('suitability_class', 'Unknown')}")
        print(f"  Confidence: {crop_result.get('confidence', 0):.2f}")
        if 'probabilities' in crop_result:
            print("  Class Probabilities:")
            for class_name, prob in crop_result['probabilities'].items():
                print(f"    {class_name}: {prob:.3f}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Nitrogen Rate Decision Tree
    print("\nNitrogen Rate Calculation:")
    print("-" * 30)
    
    nitrogen_features = {
        'yield_goal': farm_data['crop_data'].yield_goal or 150,
        'soil_n': farm_data['soil_data'].nitrogen_ppm or 10,
        'organic_matter': farm_data['soil_data'].organic_matter_percent,
        'previous_legume': 1 if farm_data['crop_data'].previous_crop == "soybean" else 0,
        'ph': farm_data['soil_data'].ph
    }
    
    try:
        nitrogen_result = rule_engine.predict_with_decision_tree('nitrogen_rate', nitrogen_features)
        print(f"  Recommended N Rate: {nitrogen_result.get('nitrogen_rate', 0):.0f} lbs/acre")
        print(f"  Confidence: {nitrogen_result.get('confidence', 0):.2f}")
        print(f"  Method: {nitrogen_result.get('method', 'Unknown')}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Soil Management Decision Tree
    print("\nSoil Management Priority:")
    print("-" * 30)
    
    soil_features = {
        'ph': farm_data['soil_data'].ph,
        'organic_matter': farm_data['soil_data'].organic_matter_percent,
        'phosphorus': farm_data['soil_data'].phosphorus_ppm,
        'potassium': farm_data['soil_data'].potassium_ppm,
        'cec': farm_data['soil_data'].cec_meq_per_100g or 15
    }
    
    try:
        soil_result = rule_engine.predict_with_decision_tree('soil_management', soil_features)
        print(f"  Management Priority: {soil_result.get('management_priority', 'Unknown')}")
        print(f"  Confidence: {soil_result.get('confidence', 0):.2f}")
        if 'probabilities' in soil_result:
            print("  Priority Probabilities:")
            for priority, prob in soil_result['probabilities'].items():
                if prob > 0.1:  # Only show significant probabilities
                    print(f"    {priority}: {prob:.3f}")
    except Exception as e:
        print(f"  Error: {e}")


def demonstrate_rule_statistics(rule_engine):
    """Demonstrate rule engine statistics."""
    
    print(f"\n{'='*60}")
    print("RULE ENGINE STATISTICS")
    print(f"{'='*60}")
    
    stats = rule_engine.get_rule_statistics()
    
    print(f"\nOverall Statistics:")
    print(f"  Total Rules: {stats['total_rules']}")
    print(f"  Active Rules: {stats['active_rules']}")
    print(f"  Expert Validated: {stats['expert_validated_rules']}")
    print(f"  Validation Percentage: {stats['validation_percentage']:.1f}%")
    
    print(f"\nRule Types:")
    for rule_type, count in stats['rule_types'].items():
        print(f"  {rule_type.replace('_', ' ').title()}: {count}")
    
    print(f"\nDecision Trees:")
    for tree_name in stats['decision_trees']:
        print(f"  {tree_name.replace('_', ' ').title()}")


def demonstrate_custom_rule_addition(rule_engine):
    """Demonstrate adding custom rules."""
    
    print(f"\n{'='*60}")
    print("CUSTOM RULE ADDITION DEMONSTRATION")
    print(f"{'='*60}")
    
    from services.rule_engine import AgriculturalRule, RuleCondition
    
    # Create a custom rule for organic farming
    organic_rule = AgriculturalRule(
        rule_id="organic_farming_suitability",
        rule_type=RuleType.CROP_SUITABILITY,
        name="Organic Farming Suitability Assessment",
        description="Assess farm suitability for organic crop production",
        conditions=[
            RuleCondition("organic_matter_percent", "gte", 3.0, weight=0.4),
            RuleCondition("soil_ph", "between", (6.0, 7.0), weight=0.3),
            RuleCondition("drainage_class", "eq", "well_drained", weight=0.3)
        ],
        action={
            "farming_system": "organic",
            "suitability_score": 0.85,
            "certification_potential": "high",
            "transition_period": "3_years"
        },
        confidence=0.82,
        priority=2,
        agricultural_source="Organic Farming Guidelines",
        expert_validated=False  # Custom rule, not yet validated
    )
    
    # Add the custom rule
    success = rule_engine.add_rule(organic_rule)
    print(f"Custom rule addition: {'Success' if success else 'Failed'}")
    
    if success:
        print(f"Added rule: {organic_rule.name}")
        print(f"Rule ID: {organic_rule.rule_id}")
        print(f"Conditions: {len(organic_rule.conditions)}")
        
        # Test the custom rule with sample data
        iowa_farm, _ = create_sample_farm_data()
        request = RecommendationRequest(
            request_id="custom_rule_test",
            question_type="crop_selection",
            **iowa_farm
        )
        
        # Evaluate only the custom rule
        all_results = rule_engine.evaluate_rules(request)
        custom_results = [r for r in all_results if r.rule_id == organic_rule.rule_id]
        
        if custom_results:
            result = custom_results[0]
            print(f"\nCustom Rule Evaluation:")
            print(f"  Matched: {result.matched}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Action: {result.action}")


def main():
    """Main demonstration function."""
    
    print("Agricultural Rule Engine Demonstration")
    print("=====================================")
    print("This demo showcases the rule-based decision system with scikit-learn integration")
    
    # Initialize the rule engine
    print("\nInitializing Agricultural Rule Engine...")
    rule_engine = AgriculturalRuleEngine()
    print("✓ Rule engine initialized successfully")
    
    # Create sample farm data
    iowa_farm, problem_farm = create_sample_farm_data()
    
    # Demonstrate rule evaluation for different farms
    demonstrate_rule_evaluation(rule_engine, iowa_farm, "Iowa Corn Farm")
    demonstrate_rule_evaluation(rule_engine, problem_farm, "Problem Soil Farm")
    
    # Demonstrate decision tree predictions
    demonstrate_decision_trees(rule_engine, iowa_farm, "Iowa Corn Farm")
    demonstrate_decision_trees(rule_engine, problem_farm, "Problem Soil Farm")
    
    # Show rule engine statistics
    demonstrate_rule_statistics(rule_engine)
    
    # Demonstrate custom rule addition
    demonstrate_custom_rule_addition(rule_engine)
    
    print(f"\n{'='*60}")
    print("DEMONSTRATION COMPLETE")
    print(f"{'='*60}")
    print("\nThe Agricultural Rule Engine provides:")
    print("• Expert-validated agricultural rules")
    print("• Scikit-learn decision tree integration")
    print("• Traceable recommendation logic")
    print("• Customizable rule management")
    print("• Agricultural domain-specific insights")
    print("\nReady for integration with the AFAS recommendation system!")


if __name__ == "__main__":
    main()