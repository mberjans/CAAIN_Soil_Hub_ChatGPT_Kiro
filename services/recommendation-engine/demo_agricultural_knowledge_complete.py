#!/usr/bin/env python3
"""
AFAS Agricultural Knowledge Base Demo - Complete Implementation
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

This script demonstrates the complete agricultural knowledge base
implementation for Questions 1-5 with real database integration.
"""

import sys
import os
from typing import Dict, List, Any

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../databases/python'))

print("🌾 AFAS Agricultural Knowledge Base - Complete Implementation Demo")
print("=" * 70)

def demo_question_1_crop_selection():
    """Demonstrate Question 1: Crop Selection knowledge."""
    try:
        from database_config import get_mongodb_collection
        
        print("\n🌱 Question 1: Crop Selection Knowledge")
        print("-" * 50)
        
        collection = get_mongodb_collection('agricultural_knowledge')
        
        # Get crop selection knowledge
        crop_knowledge = list(collection.find({
            "$or": [
                {"subcategory": "crop_selection"},
                {"subcategory": "climate_adaptation"},
                {"subcategory": "variety_selection"}
            ]
        }))
        
        print(f"📚 Found {len(crop_knowledge)} knowledge items for crop selection")
        
        for item in crop_knowledge:
            print(f"\n📖 {item['title']}")
            print(f"   Category: {item['category']} > {item['subcategory']}")
            print(f"   Guidelines: {len(item['guidelines'])} items")
            print(f"   Expert Validated: {'✅' if item['expert_validated'] else '❌'}")
            
            # Show first guideline as example
            if item['guidelines']:
                print(f"   Example: {item['guidelines'][0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def demo_question_2_soil_fertility():
    """Demonstrate Question 2: Soil Fertility knowledge."""
    try:
        from database_config import get_mongodb_collection
        
        print("\n🧪 Question 2: Soil Fertility Knowledge")
        print("-" * 50)
        
        collection = get_mongodb_collection('agricultural_knowledge')
        
        # Search for soil fertility knowledge
        soil_knowledge = list(collection.find({
            "$text": {"$search": "soil fertility pH organic matter"}
        }))
        
        print(f"📚 Found {len(soil_knowledge)} knowledge items for soil fertility")
        
        # Demonstrate soil pH interpretation
        ph_item = collection.find_one({"knowledge_id": "soil_ph_management_001"})
        if ph_item:
            print(f"\n📖 Featured: {ph_item['title']}")
            print(f"   Description: {ph_item['description']}")
            print(f"   Key Guidelines:")
            for i, guideline in enumerate(ph_item['guidelines'][:3], 1):
                print(f"     {i}. {guideline}")
            
            # Show calculation example
            if ph_item.get('calculations'):
                print(f"   🧮 Includes agricultural calculations for lime requirements")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def demo_question_3_crop_rotation():
    """Demonstrate Question 3: Crop Rotation knowledge."""
    try:
        from database_config import get_mongodb_collection
        
        print("\n🔄 Question 3: Crop Rotation Knowledge")
        print("-" * 50)
        
        collection = get_mongodb_collection('agricultural_knowledge')
        
        # Get rotation knowledge
        rotation_knowledge = list(collection.find({
            "$or": [
                {"subcategory": "rotation_planning"},
                {"subcategory": "nitrogen_fixation"},
                {"subcategory": "rotation_economics"}
            ]
        }))
        
        print(f"📚 Found {len(rotation_knowledge)} knowledge items for crop rotation")
        
        # Demonstrate nitrogen fixation knowledge
        nitrogen_item = collection.find_one({"knowledge_id": "nitrogen_fixation_legumes_001"})
        if nitrogen_item:
            print(f"\n📖 Featured: {nitrogen_item['title']}")
            print(f"   Key Benefits:")
            for i, guideline in enumerate(nitrogen_item['guidelines'][:3], 1):
                print(f"     {i}. {guideline}")
            
            # Show nitrogen credit calculations
            if nitrogen_item.get('calculations', {}).get('nitrogen_credit'):
                calc = nitrogen_item['calculations']['nitrogen_credit']
                print(f"   🧮 Nitrogen Credits (lbs/acre):")
                for crop, credit in calc.get('base_fixation_lbs_per_acre', {}).items():
                    print(f"     • {crop.title()}: {credit} lbs N/acre")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def demo_question_4_nutrient_deficiency():
    """Demonstrate Question 4: Nutrient Deficiency knowledge."""
    try:
        from database_config import get_mongodb_collection
        
        print("\n🔍 Question 4: Nutrient Deficiency Detection Knowledge")
        print("-" * 50)
        
        collection = get_mongodb_collection('agricultural_knowledge')
        
        # Get deficiency detection knowledge
        deficiency_knowledge = list(collection.find({
            "$text": {"$search": "deficiency symptoms testing"}
        }))
        
        print(f"📚 Found {len(deficiency_knowledge)} knowledge items for deficiency detection")
        
        # Demonstrate visual symptoms knowledge
        symptoms_item = collection.find_one({"knowledge_id": "visual_deficiency_symptoms_001"})
        if symptoms_item:
            print(f"\n📖 Featured: {symptoms_item['title']}")
            print(f"   Visual Symptoms Guide:")
            for i, guideline in enumerate(symptoms_item['guidelines'][:4], 1):
                print(f"     {i}. {guideline}")
        
        # Demonstrate soil testing knowledge
        testing_item = collection.find_one({"knowledge_id": "soil_testing_interpretation_001"})
        if testing_item:
            print(f"\n📖 Featured: {testing_item['title']}")
            if testing_item.get('calculations', {}).get('nutrient_sufficiency_levels'):
                levels = testing_item['calculations']['nutrient_sufficiency_levels']
                print(f"   🧮 Phosphorus Sufficiency Levels (ppm):")
                for level, range_val in levels.get('phosphorus_ppm', {}).items():
                    print(f"     • {level.replace('_', ' ').title()}: {range_val}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def demo_question_5_fertilizer_selection():
    """Demonstrate Question 5: Fertilizer Selection knowledge."""
    try:
        from database_config import get_mongodb_collection
        
        print("\n🌾 Question 5: Fertilizer Selection Knowledge")
        print("-" * 50)
        
        collection = get_mongodb_collection('agricultural_knowledge')
        
        # Get fertilizer selection knowledge
        fertilizer_knowledge = list(collection.find({
            "$or": [
                {"subcategory": "fertilizer_selection"},
                {"subcategory": "organic_fertilizers"},
                {"subcategory": "slow_release_fertilizers"}
            ]
        }))
        
        print(f"📚 Found {len(fertilizer_knowledge)} knowledge items for fertilizer selection")
        
        # Demonstrate fertilizer comparison
        comparison_item = collection.find_one({"knowledge_id": "fertilizer_type_comparison_001"})
        if comparison_item:
            print(f"\n📖 Featured: {comparison_item['title']}")
            print(f"   Key Considerations:")
            for i, guideline in enumerate(comparison_item['guidelines'][:3], 1):
                print(f"     {i}. {guideline}")
            
            # Show cost comparison
            if comparison_item.get('calculations', {}).get('fertilizer_comparison_matrix'):
                matrix = comparison_item['calculations']['fertilizer_comparison_matrix']
                print(f"   💰 Cost Comparison (per lb N):")
                for fert_type, cost in matrix.get('cost_per_lb_nutrient', {}).items():
                    print(f"     • {fert_type.replace('_', ' ').title()}: {cost}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def demo_search_capabilities():
    """Demonstrate search capabilities across all knowledge."""
    try:
        from database_config import get_mongodb_collection
        
        print("\n🔍 Agricultural Knowledge Search Capabilities")
        print("-" * 50)
        
        collection = get_mongodb_collection('agricultural_knowledge')
        
        # Demonstrate various search queries
        search_queries = [
            "corn soybean rotation",
            "soil pH lime application",
            "nitrogen deficiency symptoms",
            "organic fertilizer management",
            "crop variety selection"
        ]
        
        for query in search_queries:
            results = list(collection.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(3))
            
            print(f"\n🔎 Search: '{query}'")
            print(f"   📊 Found {len(results)} relevant results")
            
            if results:
                top_result = results[0]
                print(f"   🏆 Top result: {top_result['title']}")
                print(f"   📂 Category: {top_result['category']} > {top_result['subcategory']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def demo_knowledge_statistics():
    """Show comprehensive knowledge base statistics."""
    try:
        from database_config import get_mongodb_collection
        
        print("\n📊 Agricultural Knowledge Base Statistics")
        print("-" * 50)
        
        collection = get_mongodb_collection('agricultural_knowledge')
        
        # Overall statistics
        total_items = collection.count_documents({})
        expert_validated = collection.count_documents({"expert_validated": True})
        with_calculations = collection.count_documents({"calculations": {"$exists": True, "$ne": None}})
        with_regional = collection.count_documents({"regional_variations": {"$exists": True, "$ne": None}})
        
        print(f"📈 Overall Statistics:")
        print(f"   Total Knowledge Items: {total_items}")
        print(f"   Expert Validated: {expert_validated}/{total_items} ({expert_validated/total_items*100:.1f}%)")
        print(f"   With Calculations: {with_calculations}/{total_items} ({with_calculations/total_items*100:.1f}%)")
        print(f"   With Regional Variations: {with_regional}/{total_items} ({with_regional/total_items*100:.1f}%)")
        
        # Category breakdown
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        categories = list(collection.aggregate(pipeline))
        
        print(f"\n📂 Knowledge by Category:")
        for category in categories:
            category_name = category['_id'].replace('_', ' ').title()
            count = category['count']
            print(f"   • {category_name}: {count} items")
        
        # Question coverage
        question_coverage = {
            "Question 1": collection.count_documents({"$text": {"$search": "crop selection"}}),
            "Question 2": collection.count_documents({"$text": {"$search": "soil fertility"}}),
            "Question 3": collection.count_documents({"$text": {"$search": "crop rotation"}}),
            "Question 4": collection.count_documents({"$text": {"$search": "deficiency"}}),
            "Question 5": collection.count_documents({"$text": {"$search": "fertilizer"}})
        }
        
        print(f"\n🎯 Question Coverage:")
        for question, count in question_coverage.items():
            print(f"   • {question}: {count} relevant items")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def main():
    """Run the complete agricultural knowledge base demo."""
    
    print("🚀 Starting Complete Agricultural Knowledge Base Demo")
    print("-" * 70)
    
    demos = [
        ("Question 1: Crop Selection", demo_question_1_crop_selection),
        ("Question 2: Soil Fertility", demo_question_2_soil_fertility),
        ("Question 3: Crop Rotation", demo_question_3_crop_rotation),
        ("Question 4: Nutrient Deficiency", demo_question_4_nutrient_deficiency),
        ("Question 5: Fertilizer Selection", demo_question_5_fertilizer_selection),
        ("Search Capabilities", demo_search_capabilities),
        ("Knowledge Statistics", demo_knowledge_statistics)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n{'='*70}")
            result = demo_func()
            results.append((demo_name, result))
        except Exception as e:
            print(f"\n❌ {demo_name} demo failed: {e}")
            results.append((demo_name, False))
    
    # Summary
    print(f"\n{'='*70}")
    print("🎉 Agricultural Knowledge Base Demo Complete!")
    print("-" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"📊 Demo Results: {passed}/{total} successful ({passed/total*100:.1f}%)")
    
    if passed == total:
        print(f"\n✅ All demonstrations successful!")
        print(f"\n🌾 Agricultural Knowledge Base Features Demonstrated:")
        print(f"   • Complete coverage of Questions 1-5")
        print(f"   • Expert-validated agricultural content")
        print(f"   • Comprehensive search capabilities")
        print(f"   • Detailed agricultural calculations")
        print(f"   • Regional adaptation guidelines")
        print(f"   • Source attribution and traceability")
        
        print(f"\n🚀 Ready for Production Use:")
        print(f"   • Recommendation engine integration")
        print(f"   • API endpoint integration")
        print(f"   • Farmer-facing applications")
        print(f"   • Expert validation workflows")
        
        return 0
    else:
        print(f"\n⚠️  Some demonstrations failed.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)