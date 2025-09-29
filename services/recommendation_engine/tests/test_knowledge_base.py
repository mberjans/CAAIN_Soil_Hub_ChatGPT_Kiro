"""
Test suite for AFAS Knowledge Base
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024
"""

import pytest
import sys
import os
from datetime import date, datetime
from unittest.mock import Mock, patch, MagicMock

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.knowledge_base import (
    KnowledgeBase, KnowledgeCategory, KnowledgeItem, 
    KnowledgeSource, SourceType, initialize_knowledge_base, seed_initial_knowledge
)
from services.knowledge_manager import (
    KnowledgeManager, RecommendationContext, 
    create_recommendation_context, initialize_knowledge_manager
)

class TestKnowledgeBase:
    """Test cases for the KnowledgeBase class."""
    
    @pytest.fixture
    def mock_knowledge_base(self):
        """Create a mock knowledge base for testing."""
        with patch('services.knowledge_base.get_postgres_session') as mock_pg, \
             patch('services.knowledge_base.get_mongodb_collection') as mock_mongo:
            
            # Mock PostgreSQL session
            mock_session = Mock()
            mock_pg.return_value = mock_session
            
            # Mock MongoDB collections
            mock_collections = {
                'agricultural_knowledge': Mock(),
                'question_responses': Mock(),
                'external_data_cache': Mock(),
                'image_analysis': Mock(),
                'conversation_history': Mock()
            }
            mock_mongo.side_effect = lambda name: mock_collections[name]
            
            kb = KnowledgeBase()
            kb.mock_session = mock_session
            kb.mock_collections = mock_collections
            
            return kb
    
    def test_knowledge_base_initialization(self, mock_knowledge_base):
        """Test knowledge base initialization."""
        kb = mock_knowledge_base
        
        assert kb.postgres_session is not None
        assert len(kb.mongodb_collections) == 5
        assert 'agricultural_knowledge' in kb.mongodb_collections
    
    def test_add_knowledge_item(self, mock_knowledge_base):
        """Test adding a knowledge item."""
        kb = mock_knowledge_base
        
        # Mock successful insertion
        kb.mock_collections['agricultural_knowledge'].insert_one.return_value = Mock(inserted_id="test_id")
        
        knowledge_item = KnowledgeItem(
            knowledge_id="test_knowledge_001",
            category=KnowledgeCategory.CROP_MANAGEMENT,
            subcategory="test_subcategory",
            title="Test Knowledge",
            description="Test description",
            guidelines=["Test guideline 1", "Test guideline 2"],
            source=KnowledgeSource(
                type=SourceType.EXTENSION_SERVICE,
                name="Test Extension Service"
            ),
            tags=["test", "knowledge"],
            expert_validated=True
        )
        
        result = kb.add_knowledge_item(knowledge_item)
        
        assert result is True
        kb.mock_collections['agricultural_knowledge'].insert_one.assert_called_once()
    
    def test_get_knowledge_by_category(self, mock_knowledge_base):
        """Test retrieving knowledge by category."""
        kb = mock_knowledge_base
        
        # Mock MongoDB query result
        mock_results = [
            {
                "knowledge_id": "test_001",
                "category": "crop_management",
                "title": "Test Knowledge 1"
            },
            {
                "knowledge_id": "test_002", 
                "category": "crop_management",
                "title": "Test Knowledge 2"
            }
        ]
        
        mock_cursor = Mock()
        mock_cursor.sort.return_value = mock_results
        kb.mock_collections['agricultural_knowledge'].find.return_value = mock_cursor
        
        results = kb.get_knowledge_by_category(KnowledgeCategory.CROP_MANAGEMENT)
        
        assert len(results) == 2
        assert results[0]["knowledge_id"] == "test_001"
        kb.mock_collections['agricultural_knowledge'].find.assert_called_once()
    
    def test_search_knowledge(self, mock_knowledge_base):
        """Test knowledge search functionality."""
        kb = mock_knowledge_base
        
        # Mock search results
        mock_results = [
            {
                "knowledge_id": "search_001",
                "content": {"title": "Corn Nitrogen Management"},
                "score": 0.95
            }
        ]
        
        mock_cursor = Mock()
        mock_cursor.sort.return_value.limit.return_value = mock_results
        kb.mock_collections['agricultural_knowledge'].find.return_value = mock_cursor
        
        results = kb.search_knowledge("nitrogen corn fertilizer")
        
        assert len(results) == 1
        assert results[0]["knowledge_id"] == "search_001"
        kb.mock_collections['agricultural_knowledge'].find.assert_called_once()
    
    def test_get_crop_information(self, mock_knowledge_base):
        """Test retrieving crop information from PostgreSQL."""
        kb = mock_knowledge_base
        
        # Mock crop object
        mock_crop = Mock()
        mock_crop.crop_id = "crop_123"
        mock_crop.crop_name = "Corn"
        mock_crop.scientific_name = "Zea mays"
        mock_crop.crop_category = "grain"
        mock_crop.crop_family = "Poaceae"
        mock_crop.nitrogen_fixing = False
        mock_crop.typical_yield_range_min = 120
        mock_crop.typical_yield_range_max = 220
        mock_crop.yield_units = "bu/acre"
        mock_crop.growing_degree_days = 2700
        mock_crop.maturity_days_min = 90
        mock_crop.maturity_days_max = 120
        mock_crop.optimal_ph_min = 6.0
        mock_crop.optimal_ph_max = 6.8
        mock_crop.drought_tolerance = "moderate"
        mock_crop.cold_tolerance = "low"
        
        kb.mock_session.query.return_value.filter.return_value.first.return_value = mock_crop
        
        result = kb.get_crop_information("corn")
        
        assert result is not None
        assert result["crop_name"] == "Corn"
        assert result["category"] == "grain"
        assert result["nitrogen_fixing"] is False
    
    def test_soil_test_interpretation(self, mock_knowledge_base):
        """Test soil test interpretation."""
        kb = mock_knowledge_base
        
        interpretation = kb.get_soil_test_interpretation(
            ph=5.8, organic_matter=2.1, phosphorus=12, potassium=95
        )
        
        assert "ph_interpretation" in interpretation
        assert "organic_matter_interpretation" in interpretation
        assert "phosphorus_interpretation" in interpretation
        assert "potassium_interpretation" in interpretation
        assert "overall_assessment" in interpretation
        assert "recommendations" in interpretation
        
        # Check that low values trigger appropriate recommendations
        ph_interp = interpretation["ph_interpretation"]
        assert ph_interp["status"] == "acidic"
        assert "lime" in ph_interp["recommendations"][0].lower()
    
    def test_store_recommendation(self, mock_knowledge_base):
        """Test storing recommendations."""
        kb = mock_knowledge_base
        
        # Mock successful insertion
        kb.mock_collections['question_responses'].insert_one.return_value = Mock(inserted_id="rec_id")
        
        rec_id = kb.store_recommendation(
            user_id="user_123",
            question_type="crop_selection",
            request_data={"location": {"lat": 42.0, "lon": -93.6}},
            response_data={"recommendations": [{"crop": "corn"}]}
        )
        
        assert rec_id != ""
        kb.mock_collections['question_responses'].insert_one.assert_called_once()
    
    def test_cache_external_data(self, mock_knowledge_base):
        """Test caching external data."""
        kb = mock_knowledge_base
        
        # Mock successful cache operation
        kb.mock_collections['external_data_cache'].replace_one.return_value = Mock()
        
        result = kb.cache_external_data(
            cache_key="weather_42.0_-93.6",
            data_source="weather_api",
            data={"temperature": 75, "humidity": 60},
            ttl_seconds=3600
        )
        
        assert result is True
        kb.mock_collections['external_data_cache'].replace_one.assert_called_once()


class TestKnowledgeManager:
    """Test cases for the KnowledgeManager class."""
    
    @pytest.fixture
    def mock_knowledge_manager(self):
        """Create a mock knowledge manager for testing."""
        with patch('services.knowledge_manager.initialize_knowledge_base') as mock_init:
            mock_kb = Mock()
            mock_init.return_value = mock_kb
            
            km = KnowledgeManager()
            km.mock_kb = mock_kb
            
            return km
    
    def test_knowledge_manager_initialization(self, mock_knowledge_manager):
        """Test knowledge manager initialization."""
        km = mock_knowledge_manager
        
        assert km.knowledge_base is not None
        assert len(km._question_type_mapping) > 0
        assert "crop_selection" in km._question_type_mapping
    
    def test_create_recommendation_context(self):
        """Test creating recommendation context."""
        context = create_recommendation_context(
            user_id="user_123",
            question_type="crop_selection",
            location={"latitude": 42.0, "longitude": -93.6},
            soil_data={"ph": 6.2, "organic_matter_percent": 3.8}
        )
        
        assert context.user_id == "user_123"
        assert context.question_type == "crop_selection"
        assert context.location["latitude"] == 42.0
        assert context.soil_data["ph"] == 6.2
    
    def test_generate_recommendations_crop_selection(self, mock_knowledge_manager):
        """Test generating crop selection recommendations."""
        km = mock_knowledge_manager
        
        # Mock knowledge base responses
        km.mock_kb.get_knowledge_by_category.return_value = [
            {
                "knowledge_id": "crop_001",
                "category": "crop_management",
                "content": {"title": "Crop Selection Guide"},
                "expert_validated": True
            }
        ]
        km.mock_kb.get_knowledge_for_crop.return_value = []
        km.mock_kb.search_knowledge.return_value = []
        km.mock_kb.get_crop_varieties.return_value = [
            {
                "variety_name": "Pioneer P1197AM",
                "company": "Pioneer",
                "maturity_days": 111
            }
        ]
        km.mock_kb.store_recommendation.return_value = "rec_123"
        
        context = RecommendationContext(
            user_id="user_123",
            question_type="crop_selection",
            location={"latitude": 42.0308, "longitude": -93.6319},
            soil_data={"ph": 6.2, "organic_matter_percent": 3.8}
        )
        
        result = km.generate_recommendations(context)
        
        assert "recommendations" in result
        assert "confidence_score" in result
        assert "recommendation_id" in result
        assert result["confidence_score"] >= 0.0
        assert result["confidence_score"] <= 1.0
    
    def test_generate_recommendations_soil_fertility(self, mock_knowledge_manager):
        """Test generating soil fertility recommendations."""
        km = mock_knowledge_manager
        
        # Mock knowledge base responses
        km.mock_kb.get_knowledge_by_category.return_value = []
        km.mock_kb.get_knowledge_for_crop.return_value = []
        km.mock_kb.search_knowledge.return_value = []
        km.mock_kb.get_soil_test_interpretation.return_value = {
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
            "overall_assessment": "Priority areas: pH management needed, organic matter improvement needed"
        }
        km.mock_kb.store_recommendation.return_value = "rec_124"
        
        context = RecommendationContext(
            user_id="user_123",
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
        assert any("lime" in rec.get("action", "").lower() for rec in result["recommendations"])
    
    def test_assess_context_completeness(self, mock_knowledge_manager):
        """Test context completeness assessment."""
        km = mock_knowledge_manager
        
        # Test complete context
        complete_context = RecommendationContext(
            user_id="user_123",
            question_type="crop_selection",
            location={"latitude": 42.0, "longitude": -93.6},
            soil_data={"ph": 6.2},
            crop_data={"crop_name": "corn"}
        )
        
        completeness = km._assess_context_completeness(complete_context)
        assert completeness > 0.5
        
        # Test incomplete context
        incomplete_context = RecommendationContext(
            user_id="user_123",
            question_type="crop_selection"
        )
        
        completeness = km._assess_context_completeness(incomplete_context)
        assert completeness < 0.5
    
    def test_analyze_soil_data(self, mock_knowledge_manager):
        """Test soil data analysis."""
        km = mock_knowledge_manager
        
        # Test good soil data
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
        
        # Test poor soil data
        poor_soil = {
            "ph": 4.2,  # Very acidic
            "organic_matter_percent": 1.5  # Low OM
        }
        
        analysis = km._analyze_soil_data(poor_soil)
        
        assert analysis["quality_score"] == 0.5  # Only 2 of 4 required fields
        assert len(analysis["issues"]) > 0
        assert any("acidic" in issue.lower() for issue in analysis["issues"])
    
    def test_search_knowledge(self, mock_knowledge_manager):
        """Test knowledge search through manager."""
        km = mock_knowledge_manager
        
        # Mock search results
        km.mock_kb.search_knowledge.return_value = [
            {
                "knowledge_id": "search_001",
                "content": {"title": "Nitrogen Management"},
                "category": "nutrient_management"
            }
        ]
        
        results = km.search_knowledge("nitrogen fertilizer", categories=["nutrient_management"])
        
        assert len(results) == 1
        assert results[0]["knowledge_id"] == "search_001"
        km.mock_kb.search_knowledge.assert_called_once()


class TestKnowledgeIntegration:
    """Integration tests for knowledge base components."""
    
    @pytest.mark.integration
    def test_knowledge_base_seeding(self):
        """Test seeding the knowledge base with initial data."""
        with patch('services.knowledge_base.get_postgres_session') as mock_pg, \
             patch('services.knowledge_base.get_mongodb_collection') as mock_mongo:
            
            # Mock database connections
            mock_session = Mock()
            mock_pg.return_value = mock_session
            
            mock_collection = Mock()
            mock_collection.insert_one.return_value = Mock(inserted_id="test_id")
            mock_collection.list_indexes.return_value = []
            mock_collection.create_index.return_value = None
            mock_mongo.return_value = mock_collection
            
            # Test seeding
            kb = KnowledgeBase()
            seed_initial_knowledge(kb)
            
            # Verify that knowledge items were added
            assert mock_collection.insert_one.call_count >= 3  # At least 3 initial items
    
    @pytest.mark.integration
    def test_end_to_end_recommendation_flow(self):
        """Test complete recommendation generation flow."""
        with patch('services.knowledge_manager.initialize_knowledge_base') as mock_init:
            # Mock knowledge base
            mock_kb = Mock()
            mock_kb.get_knowledge_by_category.return_value = []
            mock_kb.get_knowledge_for_crop.return_value = []
            mock_kb.search_knowledge.return_value = []
            mock_kb.get_crop_information.return_value = {
                "crop_name": "Corn",
                "category": "grain",
                "nitrogen_fixing": False
            }
            mock_kb.get_crop_varieties.return_value = []
            mock_kb.store_recommendation.return_value = "rec_123"
            mock_init.return_value = mock_kb
            
            # Create knowledge manager and generate recommendations
            km = KnowledgeManager()
            
            context = create_recommendation_context(
                user_id="test_user",
                question_type="crop_selection",
                location={"latitude": 42.0, "longitude": -93.6},
                soil_data={"ph": 6.2, "organic_matter_percent": 3.8}
            )
            
            result = km.generate_recommendations(context)
            
            # Verify result structure
            assert "recommendations" in result
            assert "confidence_score" in result
            assert "generated_at" in result
            assert "recommendation_id" in result
            
            # Verify confidence score is valid
            assert 0.0 <= result["confidence_score"] <= 1.0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])