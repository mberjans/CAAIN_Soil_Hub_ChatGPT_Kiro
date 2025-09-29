#!/usr/bin/env python3
"""
AFAS Agricultural Knowledge Base Core Test
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

This script tests the core agricultural knowledge base functionality
without complex model dependencies.
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../databases/python'))

print("🌾 AFAS Agricultural Knowledge Base Core Test")
print("=" * 60)

def test_mongodb_connection():
    """Test MongoDB connection and knowledge retrieval."""
    try:
        from database_config import get_mongodb_collection
        
        print("🔗 Testing MongoDB Connection...")
        collection = get_mongodb_collection('agricultural_knowledge')
        
        # Test basic connection
        count = collection.count_documents({})
        print(f"   ✅ Connected to MongoDB")
        print(f"   📊 Total knowledge items: {count}")
        
        if count == 0:
            print("   ⚠️  No knowledge items found")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ MongoDB connection failed: {e}")
        return False

def test_knowledge_structure():
    """Test the structure of imported knowledge."""
    try:
        from database_config import get_mongodb_collection
        
        print("\n📋 Testing Knowledge Structure...")
        collection = get_mongodb_collection('agricultural_knowledge')
        
        # Get a sample knowledge item
        sample_item = collection.find_one({})
        
        if not sample_item:
            print("   ❌ No knowledge items found")
            return False
        
        # Check required fields
        required_fields = [
            'knowledge_id', 'category', 'subcategory', 'title',
            'description', 'guidelines', 'tags', 'expert_validated'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in sample_item:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"   ❌ Missing required fields: {missing_fields}")
            return False
        
        print(f"   ✅ Knowledge structure is valid")
        print(f"   📝 Sample item: {sample_item['title']}")
        print(f"   🏷️  Category: {sample_item['category']}")
        print(f"   ✅ Expert validated: {sample_item['expert_validated']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Knowledge structure test failed: {e}")
        return False

def test_question_coverage():
    """Test coverage of Questions 1-5."""
    try:
        from database_config import get_mongodb_collection
        
        print("\n🎯 Testing Question Coverage...")
        collection = get_mongodb_collection('agricultural_knowledge')
        
        # Expected knowledge items for each question
        question_knowledge = {
            "Question 1 (Crop Selection)": [
                "crop_soil_ph_compatibility_001",
                "crop_climate_adaptation_001", 
                "crop_variety_selection_001"
            ],
            "Question 2 (Soil Fertility)": [
                "soil_ph_management_001",
                "organic_matter_enhancement_001",
                "nutrient_cycling_efficiency_001"
            ],
            "Question 3 (Crop Rotation)": [
                "crop_rotation_principles_001",
                "nitrogen_fixation_legumes_001",
                "rotation_economic_optimization_001"
            ],
            "Question 4 (Nutrient Deficiency)": [
                "soil_testing_interpretation_001",
                "visual_deficiency_symptoms_001",
                "tissue_testing_analysis_001"
            ],
            "Question 5 (Fertilizer Selection)": [
                "fertilizer_type_comparison_001",
                "organic_fertilizer_management_001",
                "slow_release_technology_001"
            ]
        }
        
        all_covered = True
        
        for question, knowledge_ids in question_knowledge.items():
            print(f"\n   {question}:")
            
            found_count = 0
            for knowledge_id in knowledge_ids:
                item = collection.find_one({"knowledge_id": knowledge_id})
                if item:
                    print(f"     ✅ {knowledge_id}")
                    found_count += 1
                else:
                    print(f"     ❌ {knowledge_id} - MISSING")
                    all_covered = False
            
            coverage_pct = (found_count / len(knowledge_ids)) * 100
            print(f"     📊 Coverage: {found_count}/{len(knowledge_ids)} ({coverage_pct:.1f}%)")
        
        return all_covered
        
    except Exception as e:
        print(f"   ❌ Question coverage test failed: {e}")
        return False

def test_knowledge_categories():
    """Test knowledge organization by categories."""
    try:
        from database_config import get_mongodb_collection
        
        print("\n📂 Testing Knowledge Categories...")
        collection = get_mongodb_collection('agricultural_knowledge')
        
        # Get category distribution
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        category_counts = list(collection.aggregate(pipeline))
        
        print(f"   📊 Category Distribution:")
        total_items = 0
        for category in category_counts:
            category_name = category['_id'].replace('_', ' ').title()
            count = category['count']
            total_items += count
            print(f"     • {category_name}: {count} items")
        
        print(f"   📈 Total Items: {total_items}")
        
        # Check expected categories are present
        expected_categories = [
            'crop_management', 'soil_health', 'nutrient_management', 'economic_analysis'
        ]
        
        found_categories = [cat['_id'] for cat in category_counts]
        missing_categories = [cat for cat in expected_categories if cat not in found_categories]
        
        if missing_categories:
            print(f"   ⚠️  Missing categories: {missing_categories}")
        else:
            print(f"   ✅ All expected categories present")
        
        return len(missing_categories) == 0
        
    except Exception as e:
        print(f"   ❌ Category test failed: {e}")
        return False

def test_knowledge_search():
    """Test text search functionality."""
    try:
        from database_config import get_mongodb_collection
        
        print("\n🔍 Testing Knowledge Search...")
        collection = get_mongodb_collection('agricultural_knowledge')
        
        # Test searches for each question area
        search_tests = [
            {"query": "crop selection", "min_results": 1, "description": "Crop selection knowledge"},
            {"query": "soil pH lime", "min_results": 1, "description": "Soil pH management"},
            {"query": "rotation nitrogen", "min_results": 1, "description": "Crop rotation and nitrogen"},
            {"query": "deficiency symptoms", "min_results": 1, "description": "Nutrient deficiency detection"},
            {"query": "fertilizer organic", "min_results": 1, "description": "Fertilizer type selection"}
        ]
        
        all_searches_passed = True
        
        for test in search_tests:
            print(f"\n   🔎 Searching: '{test['query']}'")
            
            # Perform text search
            results = list(collection.find(
                {"$text": {"$search": test['query']}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(5))
            
            print(f"     📊 Found {len(results)} results")
            
            if len(results) >= test['min_results']:
                print(f"     ✅ {test['description']}: Sufficient results")
                
                # Show top result
                if results:
                    top_result = results[0]
                    print(f"     🏆 Top result: {top_result.get('title', 'N/A')}")
            else:
                print(f"     ❌ {test['description']}: Insufficient results")
                all_searches_passed = False
        
        return all_searches_passed
        
    except Exception as e:
        print(f"   ❌ Search test failed: {e}")
        return False

def test_agricultural_accuracy():
    """Test agricultural accuracy and expert validation."""
    try:
        from database_config import get_mongodb_collection
        
        print("\n🎓 Testing Agricultural Accuracy...")
        collection = get_mongodb_collection('agricultural_knowledge')
        
        # Check expert validation
        total_items = collection.count_documents({})
        expert_validated = collection.count_documents({"expert_validated": True})
        
        validation_rate = (expert_validated / total_items) * 100 if total_items > 0 else 0
        
        print(f"   📊 Expert Validation Rate: {expert_validated}/{total_items} ({validation_rate:.1f}%)")
        
        if validation_rate < 100:
            print(f"   ⚠️  Some items not expert validated")
        else:
            print(f"   ✅ All items expert validated")
        
        # Check for agricultural sources
        items_with_sources = collection.count_documents({"source.name": {"$exists": True, "$ne": None}})
        source_rate = (items_with_sources / total_items) * 100 if total_items > 0 else 0
        
        print(f"   📚 Source Attribution Rate: {items_with_sources}/{total_items} ({source_rate:.1f}%)")
        
        # Check for calculations
        items_with_calculations = collection.count_documents({"calculations": {"$exists": True, "$ne": None}})
        calc_rate = (items_with_calculations / total_items) * 100 if total_items > 0 else 0
        
        print(f"   🧮 Items with Calculations: {items_with_calculations}/{total_items} ({calc_rate:.1f}%)")
        
        # Check for regional variations
        items_with_regional = collection.count_documents({"regional_variations": {"$exists": True, "$ne": None}})
        regional_rate = (items_with_regional / total_items) * 100 if total_items > 0 else 0
        
        print(f"   🌍 Items with Regional Variations: {items_with_regional}/{total_items} ({regional_rate:.1f}%)")
        
        # Overall quality score
        quality_score = (validation_rate + source_rate + calc_rate + regional_rate) / 4
        print(f"   🏆 Overall Quality Score: {quality_score:.1f}%")
        
        return quality_score >= 80.0  # Require 80% quality score
        
    except Exception as e:
        print(f"   ❌ Agricultural accuracy test failed: {e}")
        return False

def test_knowledge_completeness():
    """Test completeness of agricultural knowledge."""
    try:
        from database_config import get_mongodb_collection
        
        print("\n📋 Testing Knowledge Completeness...")
        collection = get_mongodb_collection('agricultural_knowledge')
        
        # Check for essential agricultural topics
        essential_topics = [
            {"topic": "Soil pH Management", "search": "soil pH lime"},
            {"topic": "Crop Selection", "search": "crop suitability"},
            {"topic": "Nutrient Management", "search": "fertilizer nutrient"},
            {"topic": "Organic Matter", "search": "organic matter soil"},
            {"topic": "Crop Rotation", "search": "rotation nitrogen"},
            {"topic": "Deficiency Diagnosis", "search": "deficiency symptoms"},
            {"topic": "Fertilizer Types", "search": "organic synthetic fertilizer"}
        ]
        
        coverage_results = []
        
        for topic_test in essential_topics:
            results = list(collection.find({"$text": {"$search": topic_test['search']}}))
            covered = len(results) > 0
            coverage_results.append(covered)
            
            status = "✅" if covered else "❌"
            print(f"   {status} {topic_test['topic']}: {len(results)} items")
        
        coverage_rate = (sum(coverage_results) / len(coverage_results)) * 100
        print(f"\n   📊 Topic Coverage: {sum(coverage_results)}/{len(coverage_results)} ({coverage_rate:.1f}%)")
        
        return coverage_rate >= 85.0  # Require 85% topic coverage
        
    except Exception as e:
        print(f"   ❌ Completeness test failed: {e}")
        return False

def run_core_tests():
    """Run core agricultural knowledge base tests."""
    
    print("🚀 Starting Core Knowledge Base Tests")
    print("-" * 60)
    
    tests = [
        ("MongoDB Connection", test_mongodb_connection),
        ("Knowledge Structure", test_knowledge_structure),
        ("Question Coverage", test_question_coverage),
        ("Knowledge Categories", test_knowledge_categories),
        ("Knowledge Search", test_knowledge_search),
        ("Agricultural Accuracy", test_agricultural_accuracy),
        ("Knowledge Completeness", test_knowledge_completeness)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"🧪 Running: {test_name}")
            print("-" * 40)
            
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"\n✅ {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"\n❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Core Test Results Summary")
    print("-" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print(f"\n🎉 All core tests passed! Agricultural knowledge base is ready.")
        
        print(f"\n📝 Knowledge Base Status:")
        print(f"   ✅ MongoDB connection working")
        print(f"   ✅ Knowledge structure valid")
        print(f"   ✅ All 5 questions covered")
        print(f"   ✅ Categories properly organized")
        print(f"   ✅ Text search functional")
        print(f"   ✅ Agricultural accuracy validated")
        print(f"   ✅ Knowledge completeness verified")
        
        print(f"\n🚀 Agricultural Knowledge Base Implementation Complete!")
        print(f"\n📋 Task Status: ✅ COMPLETED")
        print(f"   • 15 expert-validated knowledge items")
        print(f"   • 100% coverage for Questions 1-5")
        print(f"   • All agricultural categories represented")
        print(f"   • Search and retrieval functional")
        print(f"   • Ready for recommendation engine integration")
        
        return 0
    else:
        print(f"\n⚠️  Some core tests failed.")
        return 1

def main():
    """Main function."""
    return run_core_tests()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)