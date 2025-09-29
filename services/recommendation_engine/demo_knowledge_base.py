#!/usr/bin/env python3
"""
AFAS Knowledge Base Demo
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

This script demonstrates the knowledge base structure and functionality
without requiring database connections.
"""

import sys
import os
from datetime import date, datetime
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

print("🌾 AFAS Knowledge Base Structure Demo")
print("=" * 50)

# ========================================================================
# KNOWLEDGE BASE DATA STRUCTURES
# ========================================================================

class KnowledgeCategory(Enum):
    """Categories for agricultural knowledge."""
    CROP_MANAGEMENT = "crop_management"
    SOIL_HEALTH = "soil_health"
    NUTRIENT_MANAGEMENT = "nutrient_management"
    PEST_MANAGEMENT = "pest_management"
    EQUIPMENT_OPERATION = "equipment_operation"
    ECONOMIC_ANALYSIS = "economic_analysis"
    ENVIRONMENTAL_STEWARDSHIP = "environmental_stewardship"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    BEST_PRACTICES = "best_practices"

class SourceType(Enum):
    """Types of knowledge sources."""
    EXTENSION_SERVICE = "extension_service"
    RESEARCH_PAPER = "research_paper"
    EXPERT_KNOWLEDGE = "expert_knowledge"
    GOVERNMENT_GUIDELINE = "government_guideline"
    INDUSTRY_STANDARD = "industry_standard"

@dataclass
class KnowledgeSource:
    """Represents a source of agricultural knowledge."""
    type: SourceType
    name: str
    url: Optional[str] = None
    publication_date: Optional[date] = None
    credibility_score: float = 0.8

@dataclass
class KnowledgeItem:
    """Represents an item of agricultural knowledge."""
    knowledge_id: str
    category: KnowledgeCategory
    subcategory: str
    title: str
    description: str
    guidelines: List[str]
    calculations: Optional[Dict[str, Any]] = None
    regional_variations: Optional[List[Dict[str, str]]] = None
    source: Optional[KnowledgeSource] = None
    applicability: Optional[Dict[str, Any]] = None
    tags: List[str] = None
    expert_validated: bool = False
    validation_date: Optional[date] = None

# ========================================================================
# SOIL INTERPRETATION FUNCTIONS
# ========================================================================

def interpret_ph(ph: float) -> Dict[str, Any]:
    """Interpret soil pH value."""
    if ph < 5.5:
        status = "very_acidic"
        description = "Very acidic soil may limit nutrient availability"
        recommendations = ["Apply lime to raise pH", "Consider sulfur-tolerant crops"]
    elif ph < 6.0:
        status = "acidic"
        description = "Acidic soil may reduce phosphorus availability"
        recommendations = ["Consider lime application", "Monitor micronutrient levels"]
    elif ph <= 7.0:
        status = "optimal"
        description = "pH is in the optimal range for most crops"
        recommendations = []
    elif ph <= 8.0:
        status = "alkaline"
        description = "Alkaline soil may reduce micronutrient availability"
        recommendations = ["Monitor iron and zinc levels", "Consider acidifying amendments"]
    else:
        status = "very_alkaline"
        description = "Very alkaline soil may cause nutrient deficiencies"
        recommendations = ["Apply sulfur to lower pH", "Use acidifying fertilizers"]
    
    return {
        "value": ph,
        "status": status,
        "description": description,
        "recommendations": recommendations
    }

def interpret_organic_matter(om: float) -> Dict[str, Any]:
    """Interpret organic matter percentage."""
    if om < 2.0:
        status = "low"
        description = "Low organic matter reduces soil health and nutrient retention"
        recommendations = ["Add compost or manure", "Use cover crops", "Reduce tillage"]
    elif om < 3.0:
        status = "moderate"
        description = "Moderate organic matter levels"
        recommendations = ["Continue organic matter building practices"]
    elif om <= 5.0:
        status = "good"
        description = "Good organic matter levels support soil health"
        recommendations = ["Maintain current practices"]
    else:
        status = "high"
        description = "High organic matter levels"
        recommendations = ["Monitor nitrogen mineralization"]
    
    return {
        "value": om,
        "status": status,
        "description": description,
        "recommendations": recommendations
    }

def interpret_phosphorus(p: float) -> Dict[str, Any]:
    """Interpret phosphorus level."""
    if p < 15:
        status = "low"
        description = "Low phosphorus may limit root development and yield"
        recommendations = ["Apply phosphorus fertilizer", "Consider starter fertilizer"]
    elif p < 25:
        status = "moderate"
        description = "Moderate phosphorus levels"
        recommendations = ["Maintenance phosphorus application recommended"]
    elif p <= 40:
        status = "adequate"
        description = "Adequate phosphorus for most crops"
        recommendations = ["Maintenance rates sufficient"]
    else:
        status = "high"
        description = "High phosphorus levels"
        recommendations = ["Reduce or eliminate phosphorus applications"]
    
    return {
        "value": p,
        "status": status,
        "description": description,
        "recommendations": recommendations
    }

def interpret_potassium(k: float) -> Dict[str, Any]:
    """Interpret potassium level."""
    if k < 120:
        status = "low"
        description = "Low potassium may reduce stress tolerance and yield"
        recommendations = ["Apply potassium fertilizer", "Consider fall application"]
    elif k < 160:
        status = "moderate"
        description = "Moderate potassium levels"
        recommendations = ["Maintenance potassium application recommended"]
    elif k <= 200:
        status = "adequate"
        description = "Adequate potassium for most crops"
        recommendations = ["Maintenance rates sufficient"]
    else:
        status = "high"
        description = "High potassium levels"
        recommendations = ["Reduce potassium applications"]
    
    return {
        "value": k,
        "status": status,
        "description": description,
        "recommendations": recommendations
    }

def get_soil_test_interpretation(ph: float, organic_matter: float,
                               phosphorus: float, potassium: float) -> Dict[str, Any]:
    """Get complete soil test interpretation."""
    interpretation = {
        "ph_interpretation": interpret_ph(ph),
        "organic_matter_interpretation": interpret_organic_matter(organic_matter),
        "phosphorus_interpretation": interpret_phosphorus(phosphorus),
        "potassium_interpretation": interpret_potassium(potassium),
        "overall_assessment": "",
        "recommendations": []
    }
    
    # Generate overall assessment
    issues = []
    if interpretation["ph_interpretation"]["status"] != "optimal":
        issues.append("pH management needed")
    if interpretation["organic_matter_interpretation"]["status"] == "low":
        issues.append("organic matter improvement needed")
    if interpretation["phosphorus_interpretation"]["status"] == "low":
        issues.append("phosphorus supplementation needed")
    if interpretation["potassium_interpretation"]["status"] == "low":
        issues.append("potassium supplementation needed")
    
    if not issues:
        interpretation["overall_assessment"] = "Soil fertility levels are generally good"
    else:
        interpretation["overall_assessment"] = f"Priority areas: {', '.join(issues)}"
    
    # Compile recommendations
    for category in ["ph_interpretation", "organic_matter_interpretation", 
                   "phosphorus_interpretation", "potassium_interpretation"]:
        if interpretation[category].get("recommendations"):
            interpretation["recommendations"].extend(interpretation[category]["recommendations"])
    
    return interpretation

# ========================================================================
# CROP SUITABILITY FUNCTIONS
# ========================================================================

def get_crop_suitability(crop_name: str, soil_ph: float, region: str) -> Dict[str, Any]:
    """Get crop suitability based on soil and location."""
    
    # Define crop suitability data
    crop_suitability = {
        "corn": {
            "ph_range": (6.0, 6.8),
            "regions": ["midwest", "southeast"],
            "description": "Well-suited for fertile soils with good drainage",
            "nitrogen_fixing": False,
            "yield_potential": "120-220 bu/acre"
        },
        "soybean": {
            "ph_range": (6.0, 7.0),
            "regions": ["midwest", "southeast"],
            "description": "Nitrogen-fixing legume, good rotation crop",
            "nitrogen_fixing": True,
            "yield_potential": "40-80 bu/acre"
        },
        "wheat": {
            "ph_range": (6.0, 7.0),
            "regions": ["midwest", "northwest", "northeast"],
            "description": "Cool-season grain crop, good for rotation",
            "nitrogen_fixing": False,
            "yield_potential": "40-100 bu/acre"
        },
        "cotton": {
            "ph_range": (5.8, 8.0),
            "regions": ["southeast", "southwest"],
            "description": "Warm-season fiber crop, requires good drainage",
            "nitrogen_fixing": False,
            "yield_potential": "600-1200 lbs/acre"
        }
    }
    
    if crop_name.lower() not in crop_suitability:
        return {"error": f"Crop '{crop_name}' not found in database"}
    
    crop_info = crop_suitability[crop_name.lower()]
    ph_min, ph_max = crop_info["ph_range"]
    suitable_regions = crop_info["regions"]
    
    # Calculate suitability scores
    ph_score = 1.0 if ph_min <= soil_ph <= ph_max else max(0.0, 1.0 - abs(soil_ph - (ph_min + ph_max) / 2) * 0.2)
    region_score = 1.0 if region.lower() in suitable_regions else 0.6
    overall_score = (ph_score + region_score) / 2
    
    return {
        "crop_name": crop_name.title(),
        "suitability_score": overall_score,
        "ph_suitability": ph_score,
        "regional_adaptation": region_score,
        "description": crop_info["description"],
        "nitrogen_fixing": crop_info["nitrogen_fixing"],
        "yield_potential": crop_info["yield_potential"],
        "optimal_ph_range": f"{ph_min}-{ph_max}",
        "suitable_regions": suitable_regions,
        "recommendation": "Highly suitable" if overall_score > 0.8 else 
                         "Suitable" if overall_score > 0.6 else 
                         "Moderately suitable" if overall_score > 0.4 else "Not recommended"
    }

# ========================================================================
# DEMONSTRATION FUNCTIONS
# ========================================================================

def demo_knowledge_structures():
    """Demonstrate knowledge base data structures."""
    print("\n📚 Knowledge Base Data Structures")
    print("-" * 40)
    
    # Create a knowledge source
    source = KnowledgeSource(
        type=SourceType.EXTENSION_SERVICE,
        name="Iowa State University Extension PM 1688",
        url="https://extension.iastate.edu/corn/nitrogen",
        publication_date=date(2024, 1, 1),
        credibility_score=0.95
    )
    
    print(f"Knowledge Source: {source.name}")
    print(f"  Type: {source.type.value}")
    print(f"  Credibility: {source.credibility_score}")
    
    # Create a knowledge item
    knowledge_item = KnowledgeItem(
        knowledge_id="corn_nitrogen_management_001",
        category=KnowledgeCategory.NUTRIENT_MANAGEMENT,
        subcategory="nitrogen",
        title="Corn Nitrogen Rate Calculation",
        description="Standard method for calculating nitrogen fertilizer rates for corn production",
        guidelines=[
            "Base nitrogen rate on realistic yield goal (1.2 lbs N per bushel expected yield)",
            "Credit nitrogen from previous legume crops (40 lbs/acre for soybean)",
            "Account for soil organic matter mineralization (20 lbs N per 1% OM)",
            "Consider soil test nitrate levels (2 lbs N credit per ppm nitrate-N)"
        ],
        calculations={
            "formula": "N_rate = (Yield_goal * 1.2) - Legume_credit - Soil_N_credit - OM_credit",
            "parameters": {
                "yield_goal_multiplier": 1.2,
                "soybean_credit": 40,
                "om_mineralization_rate": 20,
                "soil_n_credit_multiplier": 2
            }
        },
        source=source,
        applicability={
            "regions": ["midwest", "corn_belt"],
            "crops": ["corn"],
            "soil_types": ["silt_loam", "clay_loam", "sandy_loam"]
        },
        tags=["nitrogen", "corn", "fertilizer", "calculation", "yield"],
        expert_validated=True,
        validation_date=date(2024, 1, 15)
    )
    
    print(f"\nKnowledge Item: {knowledge_item.title}")
    print(f"  Category: {knowledge_item.category.value}")
    print(f"  Expert Validated: {knowledge_item.expert_validated}")
    print(f"  Guidelines: {len(knowledge_item.guidelines)} items")
    print(f"  Tags: {', '.join(knowledge_item.tags)}")
    
    return True

def demo_soil_interpretation():
    """Demonstrate soil test interpretation."""
    print("\n🧪 Soil Test Interpretation Demo")
    print("-" * 40)
    
    # Test scenarios
    scenarios = [
        {
            "name": "Good Iowa Soil",
            "ph": 6.4,
            "organic_matter": 3.5,
            "phosphorus": 28,
            "potassium": 165
        },
        {
            "name": "Acidic Low-Fertility Soil",
            "ph": 5.2,
            "organic_matter": 1.8,
            "phosphorus": 8,
            "potassium": 85
        },
        {
            "name": "Alkaline High-Fertility Soil",
            "ph": 8.2,
            "organic_matter": 4.2,
            "phosphorus": 45,
            "potassium": 220
        }
    ]
    
    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")
        print(f"  pH: {scenario['ph']}")
        print(f"  Organic Matter: {scenario['organic_matter']}%")
        print(f"  Phosphorus: {scenario['phosphorus']} ppm")
        print(f"  Potassium: {scenario['potassium']} ppm")
        
        interpretation = get_soil_test_interpretation(
            ph=scenario['ph'],
            organic_matter=scenario['organic_matter'],
            phosphorus=scenario['phosphorus'],
            potassium=scenario['potassium']
        )
        
        print(f"  Assessment: {interpretation['overall_assessment']}")
        print(f"  pH Status: {interpretation['ph_interpretation']['status']}")
        print(f"  OM Status: {interpretation['organic_matter_interpretation']['status']}")
        print(f"  P Status: {interpretation['phosphorus_interpretation']['status']}")
        print(f"  K Status: {interpretation['potassium_interpretation']['status']}")
        
        if interpretation['recommendations']:
            print(f"  Top Recommendations:")
            for i, rec in enumerate(interpretation['recommendations'][:3], 1):
                print(f"    {i}. {rec}")
    
    return True

def demo_crop_suitability():
    """Demonstrate crop suitability analysis."""
    print("\n🌱 Crop Suitability Analysis Demo")
    print("-" * 40)
    
    # Test scenarios
    scenarios = [
        {"location": "Iowa", "region": "midwest", "ph": 6.4},
        {"location": "Georgia", "region": "southeast", "ph": 5.8},
        {"location": "Kansas", "region": "midwest", "ph": 7.2},
        {"location": "California", "region": "southwest", "ph": 7.8}
    ]
    
    crops = ["corn", "soybean", "wheat", "cotton"]
    
    for scenario in scenarios:
        print(f"\nLocation: {scenario['location']} (pH: {scenario['ph']})")
        print("Crop Suitability Analysis:")
        
        suitable_crops = []
        
        for crop in crops:
            suitability = get_crop_suitability(crop, scenario['ph'], scenario['region'])
            
            if 'error' not in suitability:
                score = suitability['suitability_score']
                recommendation = suitability['recommendation']
                
                print(f"  {crop.title()}: {score:.2f} - {recommendation}")
                
                if score > 0.6:
                    suitable_crops.append((crop, score))
        
        # Sort by suitability score
        suitable_crops.sort(key=lambda x: x[1], reverse=True)
        
        if suitable_crops:
            best_crop = suitable_crops[0][0]
            print(f"  → Best choice: {best_crop.title()}")
        else:
            print(f"  → No highly suitable crops found")
    
    return True

def demo_recommendation_scenarios():
    """Demonstrate complete recommendation scenarios."""
    print("\n🎯 Complete Recommendation Scenarios")
    print("-" * 40)
    
    # Scenario 1: New farmer seeking crop advice
    print("\nScenario 1: New Iowa farmer with soil test results")
    print("Question: What crops should I grow on my 160-acre farm?")
    
    farm_data = {
        "location": "Iowa",
        "region": "midwest",
        "farm_size": 160,
        "soil_test": {
            "ph": 6.2,
            "organic_matter": 3.8,
            "phosphorus": 25,
            "potassium": 180
        }
    }
    
    print(f"Farm: {farm_data['farm_size']} acres in {farm_data['location']}")
    
    # Analyze soil
    soil_interp = get_soil_test_interpretation(**farm_data['soil_test'])
    print(f"Soil Assessment: {soil_interp['overall_assessment']}")
    
    # Analyze crop options
    print("Crop Recommendations:")
    for crop in ["corn", "soybean", "wheat"]:
        suitability = get_crop_suitability(crop, farm_data['soil_test']['ph'], farm_data['region'])
        if 'error' not in suitability:
            score = suitability['suitability_score']
            print(f"  {crop.title()}: {score:.2f} - {suitability['recommendation']}")
            if suitability['nitrogen_fixing']:
                print(f"    → Nitrogen-fixing crop, good for rotation")
    
    # Scenario 2: Farmer with soil fertility issues
    print("\nScenario 2: Farmer with acidic, low-fertility soil")
    print("Question: How can I improve my soil fertility?")
    
    problem_soil = {
        "ph": 5.2,
        "organic_matter": 1.8,
        "phosphorus": 8,
        "potassium": 85
    }
    
    soil_interp = get_soil_test_interpretation(**problem_soil)
    print(f"Soil Assessment: {soil_interp['overall_assessment']}")
    print("Priority Recommendations:")
    for i, rec in enumerate(soil_interp['recommendations'][:5], 1):
        print(f"  {i}. {rec}")
    
    # Scenario 3: Crop selection for specific conditions
    print("\nScenario 3: Farmer in alkaline soil region")
    print("Question: What crops work best in alkaline soil?")
    
    alkaline_conditions = {
        "ph": 8.0,
        "region": "southwest"
    }
    
    print("Crop Analysis for Alkaline Soil (pH 8.0):")
    for crop in ["corn", "soybean", "wheat", "cotton"]:
        suitability = get_crop_suitability(crop, alkaline_conditions['ph'], alkaline_conditions['region'])
        if 'error' not in suitability:
            score = suitability['suitability_score']
            ph_score = suitability['ph_suitability']
            print(f"  {crop.title()}: Overall {score:.2f}, pH tolerance {ph_score:.2f}")
    
    return True

def demo_knowledge_categories():
    """Demonstrate knowledge categories and organization."""
    print("\n📂 Knowledge Base Organization")
    print("-" * 40)
    
    print("Knowledge Categories:")
    for category in KnowledgeCategory:
        print(f"  • {category.value.replace('_', ' ').title()}")
    
    print("\nSource Types:")
    for source_type in SourceType:
        print(f"  • {source_type.value.replace('_', ' ').title()}")
    
    # Example knowledge mapping
    print("\nExample Knowledge Mapping:")
    question_mapping = {
        "crop_selection": {
            "categories": ["crop_management"],
            "required_data": ["location", "soil_data"],
            "example_knowledge": [
                "Crop pH requirements",
                "Regional variety recommendations", 
                "Climate adaptation guidelines"
            ]
        },
        "soil_fertility": {
            "categories": ["soil_health", "nutrient_management"],
            "required_data": ["soil_data"],
            "example_knowledge": [
                "pH management practices",
                "Organic matter improvement",
                "Nutrient deficiency correction"
            ]
        },
        "fertilizer_timing": {
            "categories": ["nutrient_management"],
            "required_data": ["crop_type", "growth_stage"],
            "example_knowledge": [
                "Split application strategies",
                "Growth stage requirements",
                "Weather timing considerations"
            ]
        }
    }
    
    for question, info in question_mapping.items():
        print(f"\n{question.replace('_', ' ').title()}:")
        print(f"  Categories: {', '.join(info['categories'])}")
        print(f"  Required Data: {', '.join(info['required_data'])}")
        print(f"  Knowledge Examples:")
        for example in info['example_knowledge']:
            print(f"    - {example}")
    
    return True

def main():
    """Run the knowledge base demonstration."""
    
    demos = [
        ("Knowledge Base Data Structures", demo_knowledge_structures),
        ("Soil Test Interpretation", demo_soil_interpretation),
        ("Crop Suitability Analysis", demo_crop_suitability),
        ("Complete Recommendation Scenarios", demo_recommendation_scenarios),
        ("Knowledge Base Organization", demo_knowledge_categories)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n{'='*60}")
            result = demo_func()
            results.append((demo_name, result))
        except Exception as e:
            print(f"\n❌ {demo_name} demo failed: {e}")
            results.append((demo_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Demo Results Summary:")
    
    passed = 0
    total = len(results)
    
    for demo_name, result in results:
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"   {demo_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} demos completed successfully")
    
    if passed == total:
        print("\n🎉 Knowledge base structure demonstration completed!")
        print("\n📝 Key Features Demonstrated:")
        print("   • Structured agricultural knowledge representation")
        print("   • Soil test interpretation with agricultural accuracy")
        print("   • Crop suitability analysis based on soil and climate")
        print("   • Complete recommendation generation workflows")
        print("   • Extensible knowledge categorization system")
        print("\n🔗 Integration Points:")
        print("   • PostgreSQL: Structured crop, soil, and farm data")
        print("   • MongoDB: Flexible knowledge documents and recommendations")
        print("   • Redis: Caching and session management")
        print("   • AI Services: Natural language explanation generation")
        return 0
    else:
        print("⚠️  Some demonstrations failed.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)