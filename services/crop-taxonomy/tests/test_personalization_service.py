"""
Tests for Personalization Service

Comprehensive test suite for advanced recommendation personalization and learning features.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from typing import List, Dict, Any

try:
    from src.services.personalization_service import (
        PersonalizationService,
        UserProfile,
        FarmCharacteristics,
        CollaborativeFilteringEngine,
        ContentBasedFilteringEngine,
        HybridRecommendationEngine
    )
    from src.models.crop_variety_models import (
        VarietyRecommendation,
        EnhancedCropVariety,
        VarietyCharacteristics,
        YieldPotential,
        DiseaseResistanceProfile,
        SeasonalTiming,
        AbioticStressTolerances,
        QualityAttributes,
        MarketAttributes
    )
    from src.models.preference_models import (
        RiskTolerance,
        ManagementStyle
    )
except ImportError:
    from services.personalization_service import (
        PersonalizationService,
        UserProfile,
        FarmCharacteristics,
        CollaborativeFilteringEngine,
        ContentBasedFilteringEngine,
        HybridRecommendationEngine
    )
    from models.crop_variety_models import (
        VarietyRecommendation,
        EnhancedCropVariety,
        VarietyCharacteristics,
        YieldPotential,
        DiseaseResistanceProfile,
        SeasonalTiming,
        AbioticStressTolerances,
        QualityAttributes,
        MarketAttributes
    )
    from models.preference_models import (
        RiskTolerance,
        ManagementStyle
    )


class TestCollaborativeFilteringEngine:
    """Test collaborative filtering engine."""
    
    @pytest.fixture
    def engine(self):
        return CollaborativeFilteringEngine()
    
    @pytest.fixture
    def sample_interactions(self):
        return [
            {
                'user_id': 'user1',
                'crop_id': 'crop1',
                'interaction_type': 'select',
                'feedback_value': 4
            },
            {
                'user_id': 'user1',
                'crop_id': 'crop2',
                'interaction_type': 'view',
                'feedback_value': 0
            },
            {
                'user_id': 'user2',
                'crop_id': 'crop1',
                'interaction_type': 'select',
                'feedback_value': 5
            },
            {
                'user_id': 'user2',
                'crop_id': 'crop3',
                'interaction_type': 'reject',
                'feedback_value': 1
            }
        ]
    
    def test_build_user_item_matrix(self, engine, sample_interactions):
        """Test user-item matrix building."""
        matrix = engine.build_user_item_matrix(sample_interactions)
        
        assert 'user1' in matrix
        assert 'user2' in matrix
        assert 'crop1' in matrix['user1']
        assert 'crop2' in matrix['user1']
        assert matrix['user1']['crop1'] > 0  # Positive rating
    
    def test_calculate_user_similarity(self, engine, sample_interactions):
        """Test user similarity calculation."""
        matrix = engine.build_user_item_matrix(sample_interactions)
        similarity = engine.calculate_user_similarity('user1', 'user2', matrix)
        
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
    
    def test_find_similar_users(self, engine, sample_interactions):
        """Test finding similar users."""
        matrix = engine.build_user_item_matrix(sample_interactions)
        similar_users = engine.find_similar_users('user1', matrix)
        
        assert isinstance(similar_users, list)
        for user in similar_users:
            assert hasattr(user, 'entity_id')
            assert hasattr(user, 'similarity')
            assert hasattr(user, 'confidence')


class TestContentBasedFilteringEngine:
    """Test content-based filtering engine."""
    
    @pytest.fixture
    def engine(self):
        return ContentBasedFilteringEngine()
    
    @pytest.fixture
    def sample_variety(self):
        return EnhancedCropVariety(
            id=uuid4(),
            variety_name="Test Variety",
            characteristics=VarietyCharacteristics(
                yield_potential=YieldPotential(expected_yield=0.8),
                disease_resistance=DiseaseResistanceProfile(
                    resistant_diseases=["rust", "blight"]
                ),
                seasonal_timing=SeasonalTiming(maturity_days=120),
                abiotic_stress_tolerances=AbioticStressTolerances(
                    drought_tolerance=0.7
                ),
                quality_attributes=QualityAttributes(
                    protein_content=0.15,
                    oil_content=0.05
                ),
                market_attributes=MarketAttributes(
                    market_stability=0.8
                )
            )
        )
    
    def test_extract_crop_features(self, engine, sample_variety):
        """Test crop feature extraction."""
        features = engine.extract_crop_features(sample_variety)
        
        assert 'yield_potential' in features
        assert 'disease_resistance' in features
        assert 'maturity_days' in features
        assert 'drought_tolerance' in features
        assert 'quality_attributes' in features
        assert 'market_demand' in features
        assert 'input_requirements' in features
        
        # Check feature values are in valid range
        for feature, value in features.items():
            assert 0.0 <= value <= 1.0
    
    def test_calculate_content_similarity(self, engine, sample_variety):
        """Test content similarity calculation."""
        # Create a similar variety
        similar_variety = EnhancedCropVariety(
            id=uuid4(),
            variety_name="Similar Variety",
            characteristics=VarietyCharacteristics(
                yield_potential=YieldPotential(expected_yield=0.75),
                disease_resistance=DiseaseResistanceProfile(
                    resistant_diseases=["rust", "blight", "mildew"]
                ),
                seasonal_timing=SeasonalTiming(maturity_days=115),
                abiotic_stress_tolerances=AbioticStressTolerances(
                    drought_tolerance=0.65
                )
            )
        )
        
        similarity = engine.calculate_content_similarity(sample_variety, similar_variety)
        
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.5  # Should be reasonably similar
    
    def test_find_similar_varieties(self, engine, sample_variety):
        """Test finding similar varieties."""
        candidate_varieties = [
            sample_variety,
            EnhancedCropVariety(
                id=uuid4(),
                variety_name="Different Variety",
                characteristics=VarietyCharacteristics(
                    yield_potential=YieldPotential(expected_yield=0.3),
                    disease_resistance=DiseaseResistanceProfile(
                        resistant_diseases=[]
                    )
                )
            )
        ]
        
        similar_varieties = engine.find_similar_varieties(sample_variety, candidate_varieties)
        
        assert isinstance(similar_varieties, list)
        # Should find the different variety (excluding the target)
        assert len(similar_varieties) == 1


class TestHybridRecommendationEngine:
    """Test hybrid recommendation engine."""
    
    @pytest.fixture
    def engine(self):
        return HybridRecommendationEngine()
    
    @pytest.fixture
    def sample_user_profile(self):
        return UserProfile(
            user_id=uuid4(),
            farm_characteristics=FarmCharacteristics(
                farm_size_acres=100.0,
                soil_type="clay_loam",
                climate_zone="6a",
                irrigation_available=True,
                equipment_level="intermediate",
                labor_availability="moderate",
                market_access="regional",
                organic_certification=False,
                sustainability_focus=0.6,
                technology_adoption=0.7
            ),
            management_style=ManagementStyle.BALANCED,
            risk_tolerance=RiskTolerance.MODERATE,
            economic_goals={"profitability": 0.8, "sustainability": 0.6},
            experience_level="intermediate",
            crop_preferences=["corn", "soybean"],
            sustainability_priorities=["soil_health", "water_conservation"],
            market_preferences=["grain", "organic"]
        )
    
    @pytest.fixture
    def sample_varieties(self):
        return [
            EnhancedCropVariety(
                id=uuid4(),
                variety_name="High Yield Corn",
                crop_id=uuid4(),
                characteristics=VarietyCharacteristics(
                    yield_potential=YieldPotential(expected_yield=0.9),
                    input_requirements={"fertilizer_level": "high"},
                    soil_preferences={"preferred_soil_types": ["clay_loam"]},
                    water_requirements={"irrigation_required": True},
                    sustainability_attributes={"organic_suitable": False}
                )
            ),
            EnhancedCropVariety(
                id=uuid4(),
                variety_name="Sustainable Soybean",
                crop_id=uuid4(),
                characteristics=VarietyCharacteristics(
                    yield_potential=YieldPotential(expected_yield=0.7),
                    input_requirements={"fertilizer_level": "low"},
                    soil_preferences={"preferred_soil_types": ["sandy_loam"]},
                    water_requirements={"irrigation_required": False},
                    sustainability_attributes={"organic_suitable": True}
                )
            )
        ]
    
    def test_score_variety_for_user(self, engine, sample_user_profile, sample_varieties):
        """Test variety scoring for user profile."""
        variety = sample_varieties[0]  # High Yield Corn
        score = engine._score_variety_for_user(variety, sample_user_profile)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        
        # Should score well due to soil type match and irrigation availability
        assert score > 0.0
    
    def test_get_content_based_recommendations(self, engine, sample_user_profile, sample_varieties):
        """Test content-based recommendations."""
        recommendations = engine._get_content_based_recommendations(
            sample_user_profile, sample_varieties
        )
        
        assert isinstance(recommendations, list)
        for rec in recommendations:
            assert isinstance(rec, VarietyRecommendation)
            assert rec.overall_score > 0.0


class TestPersonalizationService:
    """Test personalization service."""
    
    @pytest.fixture
    def service(self):
        return PersonalizationService()
    
    @pytest.fixture
    def sample_user_profile(self):
        return UserProfile(
            user_id=uuid4(),
            farm_characteristics=FarmCharacteristics(
                farm_size_acres=200.0,
                soil_type="sandy_loam",
                climate_zone="5b",
                irrigation_available=False,
                equipment_level="basic",
                labor_availability="limited",
                market_access="local",
                organic_certification=True,
                sustainability_focus=0.8,
                technology_adoption=0.4
            ),
            management_style=ManagementStyle.LOW_INPUT,
            risk_tolerance=RiskTolerance.LOW,
            economic_goals={"profitability": 0.7, "sustainability": 0.9},
            experience_level="beginner",
            crop_preferences=["wheat", "oats"],
            sustainability_priorities=["organic", "biodiversity"],
            market_preferences=["organic", "local"]
        )
    
    @pytest.fixture
    def sample_recommendations(self):
        return [
            VarietyRecommendation(
                variety_id=uuid4(),
                variety_name="Organic Wheat",
                overall_score=0.8,
                suitability_factors={"yield": 0.7, "sustainability": 0.9},
                individual_scores={"yield": 0.7, "sustainability": 0.9},
                weighted_contributions={"yield": 0.35, "sustainability": 0.45}
            ),
            VarietyRecommendation(
                variety_id=uuid4(),
                variety_name="High Input Corn",
                overall_score=0.6,
                suitability_factors={"yield": 0.9, "sustainability": 0.3},
                individual_scores={"yield": 0.9, "sustainability": 0.3},
                weighted_contributions={"yield": 0.45, "sustainability": 0.15}
            )
        ]
    
    @pytest.fixture
    def sample_interactions(self):
        return [
            {
                'user_id': str(uuid4()),
                'crop_id': 'wheat',
                'interaction_type': 'select',
                'feedback_value': 5,
                'timestamp': datetime.now() - timedelta(days=1)
            },
            {
                'user_id': str(uuid4()),
                'crop_id': 'corn',
                'interaction_type': 'reject',
                'feedback_value': 2,
                'timestamp': datetime.now() - timedelta(days=2)
            }
        ]
    
    @pytest.mark.asyncio
    async def test_personalize_recommendations(self, service, sample_user_profile, sample_recommendations):
        """Test recommendation personalization."""
        with patch.object(service, '_get_user_interactions', return_value=[]):
            personalized_recs = await service.personalize_recommendations(
                sample_user_profile, sample_recommendations
            )
        
        assert isinstance(personalized_recs, list)
        assert len(personalized_recs) == len(sample_recommendations)
        
        for rec in personalized_recs:
            assert isinstance(rec, VarietyRecommendation)
            assert rec.metadata.get('personalized') is True
            assert 'personalization_timestamp' in rec.metadata
    
    @pytest.mark.asyncio
    async def test_calculate_personalization_score(self, service, sample_user_profile, sample_recommendations):
        """Test personalization score calculation."""
        recommendation = sample_recommendations[0]
        
        with patch.object(service, '_get_user_interactions', return_value=[]):
            score = await service._calculate_personalization_score(
                recommendation, sample_user_profile, []
            )
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    def test_get_content_based_score(self, service, sample_user_profile, sample_recommendations):
        """Test content-based scoring."""
        recommendation = sample_recommendations[0]
        score = service._get_content_based_score(recommendation, sample_user_profile)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    def test_get_farm_characteristics_score(self, service, sample_user_profile, sample_recommendations):
        """Test farm characteristics scoring."""
        recommendation = sample_recommendations[0]
        score = service._get_farm_characteristics_score(recommendation, sample_user_profile)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    def test_apply_personalization_adjustments(self, service, sample_user_profile, sample_recommendations):
        """Test personalization adjustments."""
        recommendation = sample_recommendations[0]
        personalization_score = 0.7
        
        adjusted_rec = service._apply_personalization_adjustments(
            recommendation, personalization_score, sample_user_profile
        )
        
        assert isinstance(adjusted_rec, VarietyRecommendation)
        assert 'personalization_score' in adjusted_rec.suitability_factors
        assert 'personalization' in adjusted_rec.individual_scores
        assert 'personalization' in adjusted_rec.weighted_contributions
    
    def test_generate_personalization_explanation(self, service, sample_user_profile):
        """Test personalization explanation generation."""
        high_score_explanation = service._generate_personalization_explanation(0.8, sample_user_profile)
        low_score_explanation = service._generate_personalization_explanation(0.3, sample_user_profile)
        
        assert isinstance(high_score_explanation, str)
        assert isinstance(low_score_explanation, str)
        assert len(high_score_explanation) > 0
        assert len(low_score_explanation) > 0
    
    def test_personalize_practices(self, service, sample_user_profile):
        """Test practice personalization."""
        original_practices = ["Plant in spring", "Apply fertilizer", "Monitor growth"]
        
        personalized_practices = service._personalize_practices(
            original_practices, sample_user_profile
        )
        
        assert isinstance(personalized_practices, list)
        assert len(personalized_practices) >= len(original_practices)
        
        # Should include management style specific practices
        assert any("minimal" in practice.lower() for practice in personalized_practices)
    
    @pytest.mark.asyncio
    async def test_learn_from_feedback(self, service):
        """Test learning from feedback."""
        user_id = uuid4()
        recommendation_id = uuid4()
        
        with patch.object(service.preference_learning_service, 'record_feedback', return_value=True):
            success = await service.learn_from_feedback(
                user_id=user_id,
                recommendation_id=recommendation_id,
                feedback_type="rating",
                feedback_value=4,
                feedback_text="Good recommendation"
            )
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_get_personalization_insights(self, service):
        """Test personalization insights."""
        user_id = uuid4()
        
        with patch.object(service.preference_learning_service, 'get_learning_insights', return_value={}):
            with patch.object(service, '_get_user_interactions', return_value=[]):
                insights = await service.get_personalization_insights(user_id)
        
        assert isinstance(insights, dict)
        assert 'user_id' in insights
        assert 'personalization_stats' in insights
        assert 'recommendation_adaptation' in insights
        assert 'generated_at' in insights


class TestPersonalizationIntegration:
    """Integration tests for personalization service."""
    
    @pytest.fixture
    def service(self):
        return PersonalizationService()
    
    @pytest.mark.asyncio
    async def test_end_to_end_personalization(self):
        """Test end-to-end personalization workflow."""
        # Create comprehensive test data
        user_profile = UserProfile(
            user_id=uuid4(),
            farm_characteristics=FarmCharacteristics(
                farm_size_acres=150.0,
                soil_type="loam",
                climate_zone="6a",
                irrigation_available=True,
                equipment_level="advanced",
                labor_availability="abundant",
                market_access="national",
                organic_certification=False,
                sustainability_focus=0.5,
                technology_adoption=0.8
            ),
            management_style=ManagementStyle.HIGH_INTENSITY,
            risk_tolerance=RiskTolerance.HIGH,
            economic_goals={"profitability": 0.9, "sustainability": 0.4},
            experience_level="expert",
            crop_preferences=["corn", "soybean", "wheat"],
            sustainability_priorities=["efficiency"],
            market_preferences=["commodity", "export"]
        )
        
        base_recommendations = [
            VarietyRecommendation(
                variety_id=uuid4(),
                variety_name="High Tech Corn",
                overall_score=0.7,
                suitability_factors={"yield": 0.8, "technology": 0.9},
                individual_scores={"yield": 0.8, "technology": 0.9},
                weighted_contributions={"yield": 0.4, "technology": 0.45}
            )
        ]
        
        user_interactions = [
            {
                'user_id': str(user_profile.user_id),
                'crop_id': 'corn',
                'interaction_type': 'select',
                'feedback_value': 5,
                'timestamp': datetime.now() - timedelta(days=1)
            }
        ]
        
        # Test personalization
        with patch.object(service, '_get_user_interactions', return_value=user_interactions):
            personalized_recs = await service.personalize_recommendations(
                user_profile, base_recommendations, user_interactions
            )
        
        # Verify results
        assert len(personalized_recs) == 1
        personalized_rec = personalized_recs[0]
        
        assert personalized_rec.metadata['personalized'] is True
        assert 'personalization_score' in personalized_rec.suitability_factors
        assert personalized_rec.overall_score >= 0.0
        assert personalized_rec.overall_score <= 1.0


# Agricultural validation tests
class TestAgriculturalValidation:
    """Agricultural validation tests for personalization."""
    
    @pytest.fixture
    def service(self):
        return PersonalizationService()
    
    def test_soil_type_compatibility(self, service):
        """Test soil type compatibility validation."""
        # Test clay soil with clay-loving variety
        farm_chars = FarmCharacteristics(
            farm_size_acres=100.0,
            soil_type="clay",
            climate_zone="6a",
            irrigation_available=True,
            equipment_level="intermediate",
            labor_availability="moderate",
            market_access="regional",
            organic_certification=False,
            sustainability_focus=0.5,
            technology_adoption=0.5
        )
        
        user_profile = UserProfile(
            user_id=uuid4(),
            farm_characteristics=farm_chars,
            management_style=ManagementStyle.BALANCED,
            risk_tolerance=RiskTolerance.MODERATE,
            economic_goals={"profitability": 0.8},
            experience_level="intermediate",
            crop_preferences=["corn"],
            sustainability_priorities=["soil_health"],
            market_preferences=["grain"]
        )
        
        variety = EnhancedCropVariety(
            id=uuid4(),
            variety_name="Clay Adapted Corn",
            characteristics=VarietyCharacteristics(
                soil_preferences={"preferred_soil_types": ["clay", "clay_loam"]}
            )
        )
        
        score = service._get_farm_characteristics_score(
            VarietyRecommendation(variety=variety, variety_id=variety.id, variety_name=variety.variety_name, overall_score=0.5),
            user_profile
        )
        
        # Should score well due to soil compatibility
        assert score > 0.1
    
    def test_irrigation_requirement_matching(self, service):
        """Test irrigation requirement matching."""
        # Test farm without irrigation with drought-tolerant variety
        farm_chars = FarmCharacteristics(
            farm_size_acres=200.0,
            soil_type="sandy_loam",
            climate_zone="5b",
            irrigation_available=False,  # No irrigation
            equipment_level="basic",
            labor_availability="limited",
            market_access="local",
            organic_certification=True,
            sustainability_focus=0.8,
            technology_adoption=0.3
        )
        
        user_profile = UserProfile(
            user_id=uuid4(),
            farm_characteristics=farm_chars,
            management_style=ManagementStyle.LOW_INPUT,
            risk_tolerance=RiskTolerance.LOW,
            economic_goals={"sustainability": 0.9},
            experience_level="beginner",
            crop_preferences=["wheat"],
            sustainability_priorities=["water_conservation"],
            market_preferences=["organic"]
        )
        
        variety = EnhancedCropVariety(
            id=uuid4(),
            variety_name="Drought Tolerant Wheat",
            characteristics=VarietyCharacteristics(
                water_requirements={"irrigation_required": False},
                abiotic_stress_tolerances={"drought_tolerance": 0.8}
            )
        )
        
        score = service._get_farm_characteristics_score(
            VarietyRecommendation(variety=variety, variety_id=variety.id, variety_name=variety.variety_name, overall_score=0.5),
            user_profile
        )
        
        # Should score well due to irrigation compatibility
        assert score > 0.1
    
    def test_management_style_compatibility(self, service):
        """Test management style compatibility."""
        # Test low-input management with low-input variety
        farm_chars = FarmCharacteristics(
            farm_size_acres=50.0,
            soil_type="loam",
            climate_zone="6a",
            irrigation_available=False,
            equipment_level="basic",
            labor_availability="limited",
            market_access="local",
            organic_certification=True,
            sustainability_focus=0.9,
            technology_adoption=0.2
        )
        
        user_profile = UserProfile(
            user_id=uuid4(),
            farm_characteristics=farm_chars,
            management_style=ManagementStyle.LOW_INPUT,
            risk_tolerance=RiskTolerance.LOW,
            economic_goals={"sustainability": 0.9},
            experience_level="beginner",
            crop_preferences=["oats"],
            sustainability_priorities=["organic", "biodiversity"],
            market_preferences=["organic", "local"]
        )
        
        variety = EnhancedCropVariety(
            id=uuid4(),
            variety_name="Low Input Oats",
            characteristics=VarietyCharacteristics(
                input_requirements={"fertilizer_level": "low"},
                sustainability_attributes={"organic_suitable": True}
            )
        )
        
        score = service._get_content_based_score(
            VarietyRecommendation(variety=variety, variety_id=variety.id, variety_name=variety.variety_name, overall_score=0.5),
            user_profile
        )
        
        # Should score well due to management style compatibility
        assert score > 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])