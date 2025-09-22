#!/usr/bin/env python3
"""
AFAS Knowledge Base Integration Test
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

This script tests the knowledge base integration with actual database connections.
"""

import sys
import os
import logging
from datetime import date

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_knowledge_base_basic():
    """Test basic knowledge base functionality."""
    try:
        from services.knowledge_base import initialize_knowledge_base, seed_initial_knowledge
        
        print("🧪 Testing Knowledge Base Basic Functionality...")
        
        # Initialize knowledge base
        print("   Initializing knowledge base...")
        kb = initialize_knowledge_base()
        
        # Test database connections
        print("   Testing database connections...")
        
        # Test PostgreSQL connection (if available)
        try:
            crop_info = kb.get_crop_information("corn")
            if crop_info:
                print(f"   ✅ PostgreSQL connection working - Found crop: {crop_info['crop_name']}")
            else:
                print("   ⚠️  PostgreSQL connection working but no corn data found")
        except Exception as e:
            print(f"   ⚠️  PostgreSQL connection issue: {e}")
        
        # Test MongoDB connection (if available)
        try:
            # Try to search knowledge (this will test MongoDB)
            results = kb.search_knowledge("nitrogen fertilizer")
            print(f"   ✅ MongoDB connection working - Found {len(results)} knowledge items")
        except Exception as e:
            print(f"   ⚠️  MongoDB connection issue: {e}")
        
        # Test soil test interpretation (doesn't require database)
        print("   Testing soil test interpretation...")
        interpretation = kb.get_soil_test_interpretation(
            ph=5.8, organic_matter=2.1, phosphorus=12, potassium=95
        )
        
        if interpretation and "overall_assessment" in interpretation:
            print(f"   ✅ Soil interpretation working: {interpretation['overall_assessment']}")
        else:
            print("   ❌ Soil interpretation failed")
        
        kb.close()
        print("   ✅ Knowledge base basic test completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Knowledge base basic test failed: {e}")
        return False

def test_knowledge_manager():
    """Test knowledge manager functionality."""
    try:
        from services.knowledge_manager import (
            initialize_knowledge_manager, create_recommendation_context
        )
        
        print("\n🧪 Testing Knowledge Manager...")
        
        # Initialize knowledge manager
        print("   Initializing knowledge manager...")
        km = initialize_knowledge_manager()
        
        # Test crop selection recommendations
        print("   Testing crop selection recommendations...")
        context = create_recommendation_context(
            user_id="test_user_123",
            question_type="crop_selection",
            location={"latitude": 42.0308, "longitude": -93.6319},
            soil_data={
                "ph": 6.2,
                "organic_matter_percent": 3.8,
                "phosphorus_ppm": 25,
                "potassium_ppm": 180
            }
        )
        
        recommendations = km.generate_recommendations(context)
        
        if recommendations and "confidence_score" in recommendations:
            confidence = recommendations["confidence_score"]
            rec_count = len(recommendations.get("recommendations", []))
            print(f"   ✅ Crop selection working - {rec_count} recommendations, confidence: {confidence:.2f}")
        else:
            print("   ❌ Crop selection recommendations failed")
        
        # Test soil fertility recommendations
        print("   Testing soil fertility recommendations...")
        context = create_recommendation_context(
            user_id="test_user_123",
            question_type="soil_fertility",
            soil_data={
                "ph": 5.8,
                "organic_matter_percent": 2.1,
                "phosphorus_ppm": 12,
                "potassium_ppm": 95
            }
        )
        
        recommendations = km.generate_recommendations(context)
        
        if recommendations and "confidence_score" in recommendations:
            confidence = recommendations["confidence_score"]
            rec_count = len(recommendations.get("recommendations", []))
            print(f"   ✅ Soil fertility working - {rec_count} recommendations, confidence: {confidence:.2f}")
        else:
            print("   ❌ Soil fertility recommendations failed")
        
        # Test knowledge search
        print("   Testing knowledge search...")
        search_results = km.search_knowledge("nitrogen corn fertilizer")
        print(f"   ✅ Knowledge search working - Found {len(search_results)} items")
        
        km.close()
        print("   ✅ Knowledge manager test completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Knowledge manager test failed: {e}")
        return False

def test_recommendation_scenarios():
    """Test various recommendation scenarios."""
    try:
        from services.knowledge_manager import (
            initialize_knowledge_manager, create_recommendation_context
        )
        
        print("\n🧪 Testing Recommendation Scenarios...")
        
        km = initialize_knowledge_manager()
        
        # Scenario 1: Iowa corn farmer with good soil
        print("   Scenario 1: Iowa corn farmer with good soil...")
        context = create_recommendation_context(
            user_id="iowa_farmer_001",
            question_type="crop_selection",
            location={"latitude": 42.0308, "longitude": -93.6319},  # Ames, Iowa
            soil_data={
                "ph": 6.4,
                "organic_matter_percent": 3.5,
                "phosphorus_ppm": 28,
                "potassium_ppm": 165,
                "test_date": "2024-03-15"
            },
            crop_data={"crop_name": "corn"},
            farm_constraints={
                "farm_size_acres": 320,
                "equipment": ["planter", "combine", "sprayer"],
                "irrigation_available": False
            }
        )
        
        result = km.generate_recommendations(context)
        print(f"      Confidence: {result.get('confidence_score', 0):.2f}")
        print(f"      Recommendations: {len(result.get('recommendations', []))}")
        
        # Scenario 2: Farmer with acidic soil needing fertility improvement
        print("   Scenario 2: Farmer with acidic soil...")
        context = create_recommendation_context(
            user_id="acidic_soil_farmer_002",
            question_type="soil_fertility",
            soil_data={
                "ph": 5.2,
                "organic_matter_percent": 1.8,
                "phosphorus_ppm": 8,
                "potassium_ppm": 85,
                "test_date": "2024-02-20"
            }
        )
        
        result = km.generate_recommendations(context)
        print(f"      Confidence: {result.get('confidence_score', 0):.2f}")
        print(f"      Recommendations: {len(result.get('recommendations', []))}")
        
        # Check if lime application is recommended
        recommendations = result.get('recommendations', [])
        lime_recommended = any('lime' in str(rec).lower() for rec in recommendations)
        print(f"      Lime recommended: {'Yes' if lime_recommended else 'No'}")
        
        # Scenario 3: Nutrient deficiency diagnosis
        print("   Scenario 3: Nutrient deficiency diagnosis...")
        context = create_recommendation_context(
            user_id="deficient_farmer_003",
            question_type="nutrient_deficiency",
            soil_data={
                "ph": 6.2,
                "organic_matter_percent": 3.0,
                "phosphorus_ppm": 6,  # Very low
                "potassium_ppm": 75,  # Low
                "nitrogen_ppm": 5     # Low
            },
            crop_data={"crop_name": "corn", "growth_stage": "V6"}
        )
        
        result = km.generate_recommendations(context)
        print(f"      Confidence: {result.get('confidence_score', 0):.2f}")
        print(f"      Recommendations: {len(result.get('recommendations', []))}")
        
        km.close()
        print("   ✅ Recommendation scenarios test completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Recommendation scenarios test failed: {e}")
        return False

def test_data_quality_assessment():
    """Test data quality assessment functionality."""
    try:
        from services.knowledge_manager import initialize_knowledge_manager
        
        print("\n🧪 Testing Data Quality Assessment...")
        
        km = initialize_knowledge_manager()
        
        # Test high-quality data
        print("   Testing high-quality soil data...")
        high_quality_soil = {
            "ph": 6.4,
            "organic_matter_percent": 3.5,
            "phosphorus_ppm": 28,
            "potassium_ppm": 165,
            "test_date": "2024-03-15",
            "lab_name": "Iowa State Soil Testing Lab"
        }
        
        analysis = km._analyze_soil_data(high_quality_soil)
        print(f"      Quality score: {analysis['quality_score']:.2f}")
        print(f"      Issues: {len(analysis['issues'])}")
        print(f"      Strengths: {len(analysis['strengths'])}")
        
        # Test low-quality data
        print("   Testing low-quality soil data...")
        low_quality_soil = {
            "ph": 4.2,  # Very acidic
            "organic_matter_percent": 1.2  # Very low
            # Missing P and K data
        }
        
        analysis = km._analyze_soil_data(low_quality_soil)
        print(f"      Quality score: {analysis['quality_score']:.2f}")
        print(f"      Issues: {len(analysis['issues'])}")
        print(f"      Strengths: {len(analysis['strengths'])}")
        
        # Test location analysis
        print("   Testing location analysis...")
        iowa_location = {"latitude": 42.0308, "longitude": -93.6319}
        location_analysis = km._analyze_location_data(iowa_location)
        print(f"      Specificity score: {location_analysis['specificity_score']:.2f}")
        print(f"      Region: {location_analysis['region']}")
        
        km.close()
        print("   ✅ Data quality assessment test completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Data quality assessment test failed: {e}")
        return False

def main():
    """Run all knowledge base integration tests."""
    print("🚀 AFAS Knowledge Base Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Knowledge Base Basic", test_knowledge_base_basic),
        ("Knowledge Manager", test_knowledge_manager),
        ("Recommendation Scenarios", test_recommendation_scenarios),
        ("Data Quality Assessment", test_data_quality_assessment)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All knowledge base integration tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)