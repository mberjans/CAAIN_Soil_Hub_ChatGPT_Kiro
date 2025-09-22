#!/usr/bin/env python3
"""
AFAS Knowledge Base Standalone Test
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

This script tests the knowledge base functionality without requiring database connections.
"""

import sys
import os
import logging
from datetime import date, datetime
from unittest.mock import Mock, patch

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_knowledge_base_classes():
    """Test knowledge base classes and data structures."""
    try:
        from services.knowledge_base import (
            KnowledgeCategory, KnowledgeItem, KnowledgeSource, SourceType
        )
        
        print("🧪 Testing Knowledge Base Classes...")
        
        # Test enums
        print("   Testing enums...")
        assert KnowledgeCategory.CROP_MANAGEMENT.value == "crop_management"
        assert SourceType.EXTENSION_SERVICE.value == "extension_service"
        print("   ✅ Enums working correctly")
        
        # Test KnowledgeSource
        print("   Testing KnowledgeSource...")
        source = KnowledgeSource(
            type=SourceType.EXTENSION_SERVICE,
            name="Iowa State University Extension",
            url="https://extension.iastate.edu",
            publication_date=date(2024, 1, 1),
            credibility_score=0.95
        )
        
        assert source.type == SourceType.EXTENSION_SERVICE
        assert source.name == "Iowa State University Extension"
        assert source.credibility_score == 0.95
        print("   ✅ KnowledgeSource working correctly")
        
        # Test KnowledgeItem
        print("   Testing KnowledgeItem...")
        knowledge_item = KnowledgeItem(
            knowledge_id="test_knowledge_001",
            category=KnowledgeCategory.CROP_MANAGEMENT,
            subcategory="variety_selection",
            title="Test Knowledge Item",
            description="This is a test knowledge item",
            guidelines=["Guideline 1", "Guideline 2"],
            source=source,
            tags=["test", "knowledge"],
            expert_validated=True,
            validation_date=date(2024, 1, 15)
        )
        
        assert knowledge_item.knowledge_id == "test_knowledge_001"
        assert knowledge_item.category == KnowledgeCategory.CROP_MANAGEMENT
        assert len(knowledge_item.guidelines) == 2
        assert knowledge_item.expert_validated is True
        print("   ✅ KnowledgeItem working correctly")
        
        print("   ✅ Knowledge base classes test completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Knowledge base classes test failed: {e}")
        return False

def test_soil_interpretation_logic():
    """Test soil test interpretation logic without database."""
    try:
        print("\n🧪 Testing Soil Interpretation Logic...")
        
        # Mock the knowledge base to test interpretation methods
        with patch('services.knowledge_base.get_postgres_session'), \
             patch('services.knowledge_base.get_mongodb_collection'):
            
            from services.knowledge_base import KnowledgeBase
            
            # Create knowledge base instance
            kb = KnowledgeBase()
            
            # Test pH interpretation
            print("   Testing pH interpretation...")
            
            # Test acidic soil
            acidic_interp = kb._interpret_ph(5.2)
            assert acidic_interp["status"] == "very_acidic"
            assert "lime" in acidic_interp["recommendations"][0].lower()
            print("      ✅ Acidic pH interpretation correct")
            
            # Test optimal soil
            optimal_interp = kb._interpret_ph(6.5)
            assert optimal_interp["status"] == "optimal"
            assert len(optimal_interp["recommendations"]) == 0
            print("      ✅ Optimal pH interpretation correct")
            
            # Test alkaline soil
            alkaline_interp = kb._interpret_ph(8.5)
            assert alkaline_interp["status"] == "very_alkaline"
            assert "sulfur" in alkaline_interp["recommendations"][0].lower()
            print("      ✅ Alkaline pH interpretation correct")
            
            # Test organic matter interpretation
            print("   Testing organic matter interpretation...")
            
            low_om = kb._interpret_organic_matter(1.5)
            assert low_om["status"] == "low"
            assert "compost" in low_om["recommendations"][0].lower()
            print("      ✅ Low organic matter interpretation correct")
            
            good_om = kb._interpret_organic_matter(4.0)
            assert good_om["status"] == "good"
            print("      ✅ Good organic matter interpretation correct")
            
            # Test phosphorus interpretation
            print("   Testing phosphorus interpretation...")
            
            low_p = kb._interpret_phosphorus(10)
            assert low_p["status"] == "low"
            assert "phosphorus" in low_p["recommendations"][0].lower()
            print("      ✅ Low phosphorus interpretation correct")
            
            high_p = kb._interpret_phosphorus(50)
            assert high_p["status"] == "high"
            assert "reduce" in high_p["recommendations"][0].lower()
            print("      ✅ High phosphorus interpretation correct")
            
            # Test complete soil interpretation
            print("   Testing complete soil interpretation...")
            
            interpretation = kb.get_soil_test_interpretation(
                ph=5.8, organic_matter=2.1, phosphorus=12, potassium=95
            )
            
            assert "ph_interpretation" in interpretation
            assert "organic_matter_interpretation" in interpretation
            assert "phosphorus_interpretation" in interpretation
            assert "potassium_interpretation" in interpretation
            assert "overall_assessment" in interpretation
            assert "recommendations" in interpretation
            
            # Should identify multiple issues
            assert "ph management needed" in interpretation["overall_assessment"].lower()
            assert len(interpretation["recommendations"]) > 0
            print("      ✅ Complete soil interpretation correct")
        
        print("   ✅ Soil interpretation logic test completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Soil interpretation logic test failed: {e}")
        return False

def test_knowledge_manager_logic():
    """Test knowledge manager logic without database connections."""
    try:
        print("\n🧪 Testing Knowledge Manager Logic...")
        
        # Mock database dependencies
        with patch('services.knowledge_manager.initialize_knowledge_base') as mock_init:
            
            # Create mock knowledge base
            mock_kb = Mock()
            mock_init.return_value = mock_kb
            
            from services.knowledge_manager import (
                KnowledgeManager, RecommendationContext, create_recommendation_context
            )
            
            # Test knowledge manager initialization
            print("   Testing knowledge manager initialization...")
            km = KnowledgeManager()
            
            assert km.knowledge_base is not None
            assert len(km._question_type_mapping) > 0
            assert "crop_selection" in km._question_type_mapping
            print("      ✅ Knowledge manager initialized correctly")
            
            # Test recommendation context creation
            print("   Testing recommendation context creation...")
            context = create_recommendation_context(
                user_id="test_user_123",
                question_type="crop_selection",
                location={"latitude": 42.0, "longitude": -93.6},
                soil_data={"ph": 6.2, "organic_matter_percent": 3.8}
            )
            
            assert context.user_id == "test_user_123"
            assert context.question_type == "crop_selection"
            assert context.location["latitude"] == 42.0
            assert context.soil_data["ph"] == 6.2
            print("      ✅ Recommendation context created correctly")
            
            # Test context completeness assessment
            print("   Testing context completeness assessment...")
            
            # Complete context for crop selection
            complete_context = RecommendationContext(
                user_id="user_123",
                question_type="crop_selection",
                location={"latitude": 42.0, "longitude": -93.6},
                soil_data={"ph": 6.2, "organic_matter_percent": 3.8}
            )
            
            completeness = km._assess_context_completeness(complete_context)
            assert completeness > 0.5
            print(f"      ✅ Complete context assessment: {completeness:.2f}")
            
            # Incomplete context
            incomplete_context = RecommendationContext(
                user_id="user_123",
                question_type="crop_selection"
            )
            
            completeness = km._assess_context_completeness(incomplete_context)
            assert completeness < 0.5
            print(f"      ✅ Incomplete context assessment: {completeness:.2f}")
            
            # Test soil data analysis
            print("   Testing soil data analysis...")
            
            good_soil = {
                "ph": 6.5,
                "organic_matter_percent": 4.0,
                "phosphorus_ppm": 25,
                "potassium_ppm": 180,
                "test_date": "2024-01-15"
            }
            
            analysis = km._analyze_soil_data(good_soil)
            assert analysis["quality_score"] == 1.0  # All required fields present
            assert len(analysis["strengths"]) > 0
            print(f"      ✅ Good soil analysis: quality={analysis['quality_score']:.2f}")
            
            poor_soil = {
                "ph": 4.2,  # Very acidic
                "organic_matter_percent": 1.5  # Low OM
            }
            
            analysis = km._analyze_soil_data(poor_soil)
            assert analysis["quality_score"] == 0.5  # Only 2 of 4 required fields
            assert len(analysis["issues"]) > 0
            print(f"      ✅ Poor soil analysis: quality={analysis['quality_score']:.2f}")
            
            # Test location analysis
            print("   Testing location analysis...")
            
            iowa_location = {"latitude": 42.0308, "longitude": -93.6319}
            location_analysis = km._analyze_location_data(iowa_location)
            
            assert location_analysis["specificity_score"] == 1.0
            assert location_analysis["region"] == "midwest"
            print(f"      ✅ Iowa location analysis: region={location_analysis['region']}")
            
            # Test search terms generation
            print("   Testing search terms generation...")
            
            search_terms = km._get_search_terms_for_question("crop_selection")
            assert "crop" in search_terms
            assert "variety" in search_terms
            print(f"      ✅ Search terms for crop_selection: '{search_terms}'")
            
            search_terms = km._get_search_terms_for_question("soil_fertility")
            assert "soil" in search_terms
            assert "fertility" in search_terms
            print(f"      ✅ Search terms for soil_fertility: '{search_terms}'")
        
        print("   ✅ Knowledge manager logic test completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Knowledge manager logic test failed: {e}")
        return False

def test_recommendation_generation_logic():
    """Test recommendation generation logic."""
    try:
        print("\n🧪 Testing Recommendation Generation Logic...")
        
        with patch('services.knowledge_manager.initialize_knowledge_base') as mock_init:
            
            # Create comprehensive mock knowledge base
            mock_kb = Mock()
            
            # Mock knowledge retrieval methods
            mock_kb.get_knowledge_by_category.return_value = [
                {
                    "knowledge_id": "crop_001",
                    "category": "crop_management",
                    "content": {
                        "title": "Crop Selection Guide",
                        "description": "Guidelines for selecting appropriate crops",
                        "guidelines": ["Consider soil pH", "Match climate zone"]
                    },
                    "expert_validated": True,
                    "source": {"name": "Extension Service", "type": "extension_service"}
                }
            ]
            
            mock_kb.get_knowledge_for_crop.return_value = []
            mock_kb.search_knowledge.return_value = []
            mock_kb.get_crop_varieties.return_value = [
                {
                    "variety_name": "Pioneer P1197AM",
                    "company": "Pioneer",
                    "maturity_days": 111,
                    "yield_potential": 185
                }
            ]
            
            # Mock soil test interpretation
            mock_kb.get_soil_test_interpretation.return_value = {
                "ph_interpretation": {
                    "status": "acidic",
                    "recommendations": ["Apply lime to raise pH"],
                    "value": 5.8,
                    "description": "Acidic soil may reduce phosphorus availability"
                },
                "organic_matter_interpretation": {
                    "status": "low",
                    "recommendations": ["Add compost or manure"],
                    "value": 2.1,
                    "description": "Low organic matter reduces soil health"
                },
                "phosphorus_interpretation": {
                    "status": "low",
                    "recommendations": ["Apply phosphorus fertilizer"],
                    "value": 12,
                    "description": "Low phosphorus may limit root development"
                },
                "potassium_interpretation": {
                    "status": "low",
                    "recommendations": ["Apply potassium fertilizer"],
                    "value": 95,
                    "description": "Low potassium may reduce stress tolerance"
                },
                "overall_assessment": "Priority areas: pH management needed, organic matter improvement needed",
                "recommendations": ["Apply lime to raise pH", "Add compost or manure"]
            }
            
            mock_kb.store_recommendation.return_value = "rec_123"
            mock_init.return_value = mock_kb
            
            from services.knowledge_manager import (
                KnowledgeManager, create_recommendation_context
            )
            
            km = KnowledgeManager()
            
            # Test crop selection recommendations
            print("   Testing crop selection recommendations...")
            
            context = create_recommendation_context(
                user_id="test_user",
                question_type="crop_selection",
                location={"latitude": 42.0308, "longitude": -93.6319},
                soil_data={"ph": 6.2, "organic_matter_percent": 3.8}
            )
            
            result = km.generate_recommendations(context)
            
            assert "recommendations" in result
            assert "confidence_score" in result
            assert "generated_at" in result
            assert 0.0 <= result["confidence_score"] <= 1.0
            print(f"      ✅ Crop selection: {len(result['recommendations'])} recommendations, confidence: {result['confidence_score']:.2f}")
            
            # Test soil fertility recommendations
            print("   Testing soil fertility recommendations...")
            
            context = create_recommendation_context(
                user_id="test_user",
                question_type="soil_fertility",
                soil_data={
                    "ph": 5.8,
                    "organic_matter_percent": 2.1,
                    "phosphorus_ppm": 12,
                    "potassium_ppm": 95
                }
            )
            
            result = km.generate_recommendations(context)
            
            assert "recommendations" in result
            assert len(result["recommendations"]) > 0
            
            # Check that lime application is recommended for acidic soil
            recommendations = result["recommendations"]
            lime_recommended = any("lime" in rec.get("action", "").lower() for rec in recommendations)
            assert lime_recommended, "Lime should be recommended for acidic soil"
            print(f"      ✅ Soil fertility: {len(recommendations)} recommendations, lime recommended: {lime_recommended}")
            
            # Test confidence score calculation
            print("   Testing confidence score calculation...")
            
            # High-quality context should have higher confidence
            high_quality_context = create_recommendation_context(
                user_id="test_user",
                question_type="crop_selection",
                location={"latitude": 42.0, "longitude": -93.6},
                soil_data={
                    "ph": 6.2,
                    "organic_matter_percent": 3.8,
                    "phosphorus_ppm": 25,
                    "potassium_ppm": 180,
                    "test_date": "2024-01-15"
                },
                crop_data={"crop_name": "corn"},
                farm_constraints={"farm_size_acres": 320}
            )
            
            high_quality_result = km.generate_recommendations(high_quality_context)
            
            # Low-quality context should have lower confidence
            low_quality_context = create_recommendation_context(
                user_id="test_user",
                question_type="crop_selection"
            )
            
            low_quality_result = km.generate_recommendations(low_quality_context)
            
            assert high_quality_result["confidence_score"] > low_quality_result["confidence_score"]
            print(f"      ✅ Confidence scores: high-quality={high_quality_result['confidence_score']:.2f}, low-quality={low_quality_result['confidence_score']:.2f}")
        
        print("   ✅ Recommendation generation logic test completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Recommendation generation logic test failed: {e}")
        return False

def test_agricultural_calculations():
    """Test agricultural calculation accuracy."""
    try:
        print("\n🧪 Testing Agricultural Calculations...")
        
        # Test pH interpretation ranges
        print("   Testing pH interpretation ranges...")
        
        with patch('services.knowledge_base.get_postgres_session'), \
             patch('services.knowledge_base.get_mongodb_collection'):
            
            from services.knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            
            # Test pH boundary conditions
            test_cases = [
                (4.0, "very_acidic"),
                (5.0, "very_acidic"),
                (5.5, "acidic"),
                (6.0, "optimal"),
                (6.5, "optimal"),
                (7.0, "optimal"),
                (7.5, "alkaline"),
                (8.0, "alkaline"),
                (8.5, "very_alkaline"),
                (9.0, "very_alkaline")
            ]
            
            for ph_value, expected_status in test_cases:
                result = kb._interpret_ph(ph_value)
                assert result["status"] == expected_status, f"pH {ph_value} should be {expected_status}, got {result['status']}"
            
            print("      ✅ pH interpretation ranges correct")
            
            # Test nutrient level interpretations
            print("   Testing nutrient level interpretations...")
            
            # Phosphorus levels
            p_test_cases = [
                (10, "low"),
                (15, "moderate"),
                (25, "adequate"),
                (45, "high")
            ]
            
            for p_value, expected_status in p_test_cases:
                result = kb._interpret_phosphorus(p_value)
                assert result["status"] == expected_status, f"P {p_value} should be {expected_status}, got {result['status']}"
            
            # Potassium levels
            k_test_cases = [
                (100, "low"),
                (130, "moderate"),
                (170, "adequate"),
                (250, "high")
            ]
            
            for k_value, expected_status in k_test_cases:
                result = kb._interpret_potassium(k_value)
                assert result["status"] == expected_status, f"K {k_value} should be {expected_status}, got {result['status']}"
            
            print("      ✅ Nutrient level interpretations correct")
            
            # Test organic matter levels
            print("   Testing organic matter interpretations...")
            
            om_test_cases = [
                (1.5, "low"),
                (2.5, "moderate"),
                (4.0, "good"),
                (6.0, "high")
            ]
            
            for om_value, expected_status in om_test_cases:
                result = kb._interpret_organic_matter(om_value)
                assert result["status"] == expected_status, f"OM {om_value} should be {expected_status}, got {result['status']}"
            
            print("      ✅ Organic matter interpretations correct")
        
        print("   ✅ Agricultural calculations test completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Agricultural calculations test failed: {e}")
        return False

def main():
    """Run all standalone knowledge base tests."""
    print("🚀 AFAS Knowledge Base Standalone Tests")
    print("=" * 50)
    
    tests = [
        ("Knowledge Base Classes", test_knowledge_base_classes),
        ("Soil Interpretation Logic", test_soil_interpretation_logic),
        ("Knowledge Manager Logic", test_knowledge_manager_logic),
        ("Recommendation Generation Logic", test_recommendation_generation_logic),
        ("Agricultural Calculations", test_agricultural_calculations)
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
        print("🎉 All knowledge base standalone tests passed!")
        print("\n📝 Note: These tests verify the knowledge base logic without requiring")
        print("   actual database connections. For full integration testing, ensure")
        print("   PostgreSQL, MongoDB, and Redis are properly configured.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)