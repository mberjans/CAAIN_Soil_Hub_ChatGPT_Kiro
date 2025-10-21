"""
Comprehensive tests for the Education Service.

This test suite covers all educational content and training system functionality
including content management, personalization, safety training, equipment training,
case studies, expert insights, and integration with other services.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from typing import List, Dict, Any

from src.services.education_service import EducationService
from src.services.personalization_service import PersonalizationService
from src.services.safety_training_service import SafetyTrainingService
from src.services.equipment_training_service import EquipmentTrainingService
from src.services.best_practices_service import BestPracticesService
from src.services.case_studies_service import CaseStudiesService
from src.services.expert_insights_service import ExpertInsightsService
from src.models.educational_models import (
    EducationalRequest, EducationalResponse, EducationalContent, TrainingModule,
    LearningPath, UserProfile, ContentRecommendation, LearningObjective,
    ExpertInsight, CaseStudy, InteractiveSimulation, VirtualRealityTraining,
    LearningProgress, Certification, ContentType, ContentCategory, DifficultyLevel
)
from src.models.application_models import ApplicationMethodType, EquipmentType


class TestEducationService:
    """Test suite for the main Education Service."""
    
    @pytest.fixture
    def education_service(self):
        """Create education service instance for testing."""
        return EducationService()
    
    @pytest.fixture
    def sample_user_profile(self):
        """Create sample user profile for testing."""
        return UserProfile(
            user_id="test_user_001",
            experience_level=DifficultyLevel.INTERMEDIATE,
            primary_crops=["corn", "soybeans"],
            farm_size_acres=500,
            equipment_available=[EquipmentType.SPREADER, EquipmentType.SPRAYER],
            learning_preferences={"preferred_formats": ["video_tutorials", "interactive_simulations"]},
            time_availability="medium",
            learning_style="visual",
            region="Midwest",
            goals=["improve_efficiency", "reduce_costs"],
            interests=["precision_agriculture", "sustainability"],
            constraints=["time_limited", "budget_conscious"]
        )
    
    @pytest.fixture
    def sample_educational_request(self, sample_user_profile):
        """Create sample educational request for testing."""
        return EducationalRequest(
            user_profile=sample_user_profile,
            application_methods=[ApplicationMethodType.BROADCAST, ApplicationMethodType.FOLIAR],
            equipment_types=[EquipmentType.SPREADER, EquipmentType.SPRAYER],
            experience_level=DifficultyLevel.INTERMEDIATE,
            content_preferences={"preferred_formats": ["video_tutorials"]},
            learning_goals=["master_calibration", "improve_safety"],
            farm_characteristics={
                "farm_size_acres": 500,
                "region": "Midwest",
                "soil_type": "clay_loam"
            }
        )
    
    @pytest.mark.asyncio
    async def test_get_educational_content_success(self, education_service, sample_educational_request):
        """Test successful educational content retrieval."""
        # Mock the database and service dependencies
        with patch.object(education_service.db, 'get_content_by_category', return_value=[]):
            with patch.object(education_service.db, 'get_expert_insights', return_value=[]):
                with patch.object(education_service.db, 'get_case_studies', return_value=[]):
                    with patch.object(education_service.db, 'get_interactive_simulations', return_value=[]):
                        with patch.object(education_service.db, 'get_user_progress', return_value=None):
                            response = await education_service.get_educational_content(sample_educational_request)
                            
                            assert isinstance(response, EducationalResponse)
                            assert response.request_id is not None
                            assert response.recommended_content is not None
                            assert response.learning_paths is not None
                            assert response.expert_insights is not None
                            assert response.case_studies is not None
                            assert response.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_get_educational_content_error_handling(self, education_service, sample_educational_request):
        """Test error handling in educational content retrieval."""
        # Mock database to raise an exception
        with patch.object(education_service.db, 'get_content_by_category', side_effect=Exception("Database error")):
            with pytest.raises(Exception):
                await education_service.get_educational_content(sample_educational_request)
    
    @pytest.mark.asyncio
    async def test_track_learning_progress(self, education_service):
        """Test learning progress tracking."""
        user_id = "test_user_001"
        content_id = "test_content_001"
        progress_data = {
            "completed": True,
            "time_spent_minutes": 45,
            "score": 0.85
        }
        
        # Mock database methods
        with patch.object(education_service.db, 'get_user_progress', return_value=None):
            with patch.object(education_service.db, 'save_user_progress', return_value=True):
                progress = await education_service.track_learning_progress(user_id, content_id, progress_data)
                
                assert isinstance(progress, LearningProgress)
                assert progress.user_id == user_id
                assert content_id in progress.completed_content
                assert progress.total_learning_time_minutes == 45
    
    @pytest.mark.asyncio
    async def test_get_certification_requirements(self, education_service):
        """Test certification requirements retrieval."""
        application_method = ApplicationMethodType.BROADCAST
        experience_level = DifficultyLevel.INTERMEDIATE
        
        # Mock database
        with patch.object(education_service.db, 'get_certifications', return_value=[]):
            certifications = await education_service.get_certification_requirements(application_method, experience_level)
            
            assert isinstance(certifications, list)
    
    @pytest.mark.asyncio
    async def test_integrated_educational_content(self, education_service, sample_educational_request):
        """Test integrated educational content with all services."""
        # Mock all service dependencies
        with patch.object(education_service.personalization_service, 'get_personalized_content', return_value=[]):
            with patch.object(education_service.best_practices_service, 'get_best_practices', return_value=[]):
                with patch.object(education_service.case_studies_service, 'get_case_studies_by_method', return_value=[]):
                    with patch.object(education_service.expert_insights_service, 'get_expert_insights', return_value=[]):
                        with patch.object(education_service.safety_training_service, 'get_safety_training_modules', return_value=[]):
                            with patch.object(education_service.equipment_training_service, 'get_operation_training', return_value=[]):
                                response = await education_service.get_integrated_educational_content(sample_educational_request)
                                
                                assert isinstance(response, EducationalResponse)
                                assert response.metadata["integration_complete"] is True
                                assert "integrated_services" in response.metadata


class TestPersonalizationService:
    """Test suite for the Personalization Service."""
    
    @pytest.fixture
    def personalization_service(self):
        """Create personalization service instance for testing."""
        return PersonalizationService()
    
    @pytest.fixture
    def sample_profile_data(self):
        """Create sample profile data for testing."""
        return {
            "experience_level": DifficultyLevel.INTERMEDIATE,
            "primary_crops": ["corn", "soybeans"],
            "farm_size_acres": 500,
            "equipment_available": [EquipmentType.SPREADER, EquipmentType.SPRAYER],
            "learning_preferences": {"preferred_formats": ["video_tutorials"]},
            "time_availability": "medium",
            "learning_style": "visual",
            "region": "Midwest",
            "goals": ["improve_efficiency"],
            "interests": ["precision_agriculture"],
            "constraints": ["time_limited"]
        }
    
    @pytest.mark.asyncio
    async def test_create_user_profile(self, personalization_service, sample_profile_data):
        """Test user profile creation."""
        user_id = "test_user_001"
        
        profile = await personalization_service.create_user_profile(user_id, sample_profile_data)
        
        assert isinstance(profile, UserProfile)
        assert profile.user_id == user_id
        assert profile.experience_level == DifficultyLevel.INTERMEDIATE
        assert profile.farm_size_acres == 500
        assert EquipmentType.SPREADER in profile.equipment_available
    
    @pytest.mark.asyncio
    async def test_get_personalized_content(self, personalization_service, sample_profile_data):
        """Test personalized content recommendations."""
        user_id = "test_user_001"
        
        # Create user profile first
        await personalization_service.create_user_profile(user_id, sample_profile_data)
        
        application_methods = [ApplicationMethodType.BROADCAST]
        
        recommendations = await personalization_service.get_personalized_content(
            user_id, application_methods
        )
        
        assert isinstance(recommendations, list)
        for rec in recommendations:
            assert isinstance(rec, ContentRecommendation)
            assert rec.relevance_score >= 0.0
    
    @pytest.mark.asyncio
    async def test_generate_learning_path(self, personalization_service, sample_profile_data):
        """Test learning path generation."""
        user_id = "test_user_001"
        
        # Create user profile first
        await personalization_service.create_user_profile(user_id, sample_profile_data)
        
        learning_goals = ["master_calibration", "improve_safety"]
        application_methods = [ApplicationMethodType.BROADCAST]
        
        learning_path = await personalization_service.generate_learning_path(
            user_id, learning_goals, application_methods
        )
        
        assert isinstance(learning_path, LearningPath)
        assert learning_path.path_id is not None
        assert len(learning_path.learning_objectives) == len(learning_goals)
        assert learning_path.estimated_duration_minutes > 0
    
    @pytest.mark.asyncio
    async def test_adapt_content_difficulty(self, personalization_service, sample_profile_data):
        """Test content difficulty adaptation."""
        user_id = "test_user_001"
        
        # Create user profile first
        await personalization_service.create_user_profile(user_id, sample_profile_data)
        
        content_id = "test_content_001"
        performance_data = {
            "completion_time_minutes": 25,
            "score": 0.9,
            "attempts": 1
        }
        
        adaptation = await personalization_service.adapt_content_difficulty(
            user_id, content_id, performance_data
        )
        
        assert isinstance(adaptation, dict)
        assert "adapted_difficulty" in adaptation
        assert "adaptation_reason" in adaptation
        assert "recommendations" in adaptation
    
    @pytest.mark.asyncio
    async def test_get_personalized_dashboard(self, personalization_service, sample_profile_data):
        """Test personalized dashboard generation."""
        user_id = "test_user_001"
        
        # Create user profile first
        await personalization_service.create_user_profile(user_id, sample_profile_data)
        
        dashboard = await personalization_service.get_personalized_dashboard(user_id)
        
        assert isinstance(dashboard, dict)
        assert dashboard["user_id"] == user_id
        assert "welcome_message" in dashboard
        assert "quick_actions" in dashboard
        assert "recommended_content" in dashboard
        assert "personalized_insights" in dashboard


class TestSafetyTrainingService:
    """Test suite for the Safety Training Service."""
    
    @pytest.fixture
    def safety_service(self):
        """Create safety training service instance for testing."""
        return SafetyTrainingService()
    
    @pytest.mark.asyncio
    async def test_get_safety_training_modules(self, safety_service):
        """Test safety training modules retrieval."""
        modules = await safety_service.get_safety_training_modules(
            None, DifficultyLevel.INTERMEDIATE
        )
        
        assert isinstance(modules, list)
        for module in modules:
            assert isinstance(module, TrainingModule)
            assert module.category == ContentCategory.SAFETY
    
    @pytest.mark.asyncio
    async def test_get_safety_protocols(self, safety_service):
        """Test safety protocols retrieval."""
        protocols = await safety_service.get_safety_protocols(ApplicationMethodType.BROADCAST)
        
        assert isinstance(protocols, dict)
        assert "pre_operation" in protocols
        assert "during_operation" in protocols
        assert "post_operation" in protocols
    
    @pytest.mark.asyncio
    async def test_get_ppe_requirements(self, safety_service):
        """Test PPE requirements retrieval."""
        requirements = await safety_service.get_ppe_requirements(
            ApplicationMethodType.BROADCAST, "granular"
        )
        
        assert isinstance(requirements, list)
        assert len(requirements) > 0
    
    @pytest.mark.asyncio
    async def test_generate_safety_assessment(self, safety_service):
        """Test safety assessment generation."""
        user_profile = {
            "experience_level": DifficultyLevel.INTERMEDIATE,
            "equipment_available": [EquipmentType.SPREADER],
            "farm_size_acres": 500
        }
        farm_characteristics = {
            "farm_size_acres": 500,
            "region": "Midwest"
        }
        application_method = ApplicationMethodType.BROADCAST
        
        assessment = await safety_service.generate_safety_assessment(
            user_profile, farm_characteristics, application_method
        )
        
        assert isinstance(assessment, dict)
        assert "safety_score" in assessment
        assert "risk_factors" in assessment
        assert "recommendations" in assessment
        assert "required_training" in assessment
        assert "ppe_requirements" in assessment


class TestEquipmentTrainingService:
    """Test suite for the Equipment Training Service."""
    
    @pytest.fixture
    def equipment_service(self):
        """Create equipment training service instance for testing."""
        return EquipmentTrainingService()
    
    @pytest.mark.asyncio
    async def test_get_equipment_information(self, equipment_service):
        """Test equipment information retrieval."""
        equipment_info = await equipment_service.get_equipment_information(EquipmentType.SPREADER)
        
        assert isinstance(equipment_info, dict)
        assert "equipment_id" in equipment_info
        assert "name" in equipment_info
        assert "types" in equipment_info
        assert "applications" in equipment_info
    
    @pytest.mark.asyncio
    async def test_get_operation_training(self, equipment_service):
        """Test operation training retrieval."""
        training = await equipment_service.get_operation_training(
            EquipmentType.SPREADER, DifficultyLevel.INTERMEDIATE
        )
        
        assert isinstance(training, list)
        for module in training:
            assert isinstance(module, TrainingModule)
            assert module.category == ContentCategory.EQUIPMENT_TRAINING
    
    @pytest.mark.asyncio
    async def test_get_maintenance_procedures(self, equipment_service):
        """Test maintenance procedures retrieval."""
        procedures = await equipment_service.get_maintenance_procedures(
            EquipmentType.SPREADER, "daily_maintenance"
        )
        
        assert isinstance(procedures, list)
        assert len(procedures) > 0
    
    @pytest.mark.asyncio
    async def test_get_calibration_procedures(self, equipment_service):
        """Test calibration procedures retrieval."""
        procedures = await equipment_service.get_calibration_procedures(EquipmentType.SPREADER)
        
        assert isinstance(procedures, dict)
        assert "calibration_steps" in procedures
        assert "calibration_formula" in procedures
        assert "tolerance" in procedures
    
    @pytest.mark.asyncio
    async def test_generate_equipment_training_plan(self, equipment_service):
        """Test equipment training plan generation."""
        user_profile = {
            "experience_level": DifficultyLevel.INTERMEDIATE,
            "farm_size_acres": 500
        }
        farm_characteristics = {
            "farm_size_acres": 500,
            "region": "Midwest"
        }
        equipment_available = [EquipmentType.SPREADER, EquipmentType.SPRAYER]
        
        plan = await equipment_service.generate_equipment_training_plan(
            user_profile, farm_characteristics, equipment_available
        )
        
        assert isinstance(plan, dict)
        assert "training_modules" in plan
        assert "estimated_duration" in plan
        assert "priority_order" in plan
        assert "recommendations" in plan


class TestBestPracticesService:
    """Test suite for the Best Practices Service."""
    
    @pytest.fixture
    def best_practices_service(self):
        """Create best practices service instance for testing."""
        return BestPracticesService()
    
    @pytest.mark.asyncio
    async def test_get_best_practices(self, best_practices_service):
        """Test best practices retrieval."""
        practices = await best_practices_service.get_best_practices(
            ApplicationMethodType.BROADCAST, None, DifficultyLevel.INTERMEDIATE
        )
        
        assert isinstance(practices, list)
        for practice in practices:
            assert hasattr(practice, 'practice_id')
            assert hasattr(practice, 'title')
            assert hasattr(practice, 'steps')
    
    @pytest.mark.asyncio
    async def test_get_equipment_guidelines(self, best_practices_service):
        """Test equipment guidelines retrieval."""
        guidelines = await best_practices_service.get_equipment_guidelines(EquipmentType.SPREADER)
        
        assert isinstance(guidelines, dict)
        assert "calibration" in guidelines
        assert "maintenance" in guidelines
        assert "safety" in guidelines
    
    @pytest.mark.asyncio
    async def test_get_timing_recommendations(self, best_practices_service):
        """Test timing recommendations retrieval."""
        recommendations = await best_practices_service.get_timing_recommendations(
            "corn", ApplicationMethodType.BROADCAST
        )
        
        assert isinstance(recommendations, dict)
        assert "soil_conditions" in recommendations
        assert "weather_conditions" in recommendations
        assert "crop_timing" in recommendations


class TestCaseStudiesService:
    """Test suite for the Case Studies Service."""
    
    @pytest.fixture
    def case_studies_service(self):
        """Create case studies service instance for testing."""
        return CaseStudiesService()
    
    @pytest.mark.asyncio
    async def test_get_case_studies_by_method(self, case_studies_service):
        """Test case studies retrieval by application method."""
        studies = await case_studies_service.get_case_studies_by_method(
            ApplicationMethodType.BROADCAST
        )
        
        assert isinstance(studies, list)
        for study in studies:
            assert isinstance(study, CaseStudy)
            assert study.application_method == ApplicationMethodType.BROADCAST
    
    @pytest.mark.asyncio
    async def test_get_case_study_by_id(self, case_studies_service):
        """Test case study retrieval by ID."""
        study = await case_studies_service.get_case_study_by_id("broadcast_success_1")
        
        if study:
            assert isinstance(study, CaseStudy)
            assert study.case_id == "broadcast_success_1"
    
    @pytest.mark.asyncio
    async def test_get_success_stories(self, case_studies_service):
        """Test success stories retrieval."""
        stories = await case_studies_service.get_success_stories(
            farm_size_range=(100, 1000), region="Midwest"
        )
        
        assert isinstance(stories, list)
        for story in stories:
            assert isinstance(story, dict)
            assert "story_id" in story
            assert "title" in story
            assert "results" in story


class TestExpertInsightsService:
    """Test suite for the Expert Insights Service."""
    
    @pytest.fixture
    def expert_insights_service(self):
        """Create expert insights service instance for testing."""
        return ExpertInsightsService()
    
    @pytest.mark.asyncio
    async def test_get_expert_insights(self, expert_insights_service):
        """Test expert insights retrieval."""
        insights = await expert_insights_service.get_expert_insights(
            ApplicationMethodType.BROADCAST
        )
        
        assert isinstance(insights, list)
        for insight in insights:
            assert isinstance(insight, ExpertInsight)
            assert ApplicationMethodType.BROADCAST in insight.application_methods
    
    @pytest.mark.asyncio
    async def test_get_experts_by_specialization(self, expert_insights_service):
        """Test experts retrieval by specialization."""
        experts = await expert_insights_service.get_experts_by_specialization(
            "soil fertility", region="Midwest"
        )
        
        assert isinstance(experts, list)
        for expert in experts:
            assert isinstance(expert, dict)
            assert "expert_id" in expert
            assert "name" in expert
            assert "expertise" in expert
    
    @pytest.mark.asyncio
    async def test_get_research_findings(self, expert_insights_service):
        """Test research findings retrieval."""
        findings = await expert_insights_service.get_research_findings(
            topic="precision agriculture"
        )
        
        assert isinstance(findings, list)
        for finding in findings:
            assert isinstance(finding, dict)
            assert "finding_id" in finding
            assert "title" in finding
            assert "researcher" in finding


class TestIntegration:
    """Integration tests for the complete education system."""
    
    @pytest.fixture
    def education_service(self):
        """Create education service instance for integration testing."""
        return EducationService()
    
    @pytest.mark.asyncio
    async def test_complete_educational_workflow(self, education_service):
        """Test complete educational workflow from user creation to content delivery."""
        # Create user profile
        user_id = "integration_test_user"
        profile_data = {
            "experience_level": DifficultyLevel.INTERMEDIATE,
            "primary_crops": ["corn", "soybeans"],
            "farm_size_acres": 500,
            "equipment_available": [EquipmentType.SPREADER, EquipmentType.SPRAYER],
            "learning_preferences": {"preferred_formats": ["video_tutorials"]},
            "time_availability": "medium",
            "learning_style": "visual",
            "region": "Midwest",
            "goals": ["improve_efficiency"],
            "interests": ["precision_agriculture"],
            "constraints": ["time_limited"]
        }
        
        # Create user profile
        user_profile = await education_service.personalization_service.create_user_profile(
            user_id, profile_data
        )
        
        # Create educational request
        educational_request = EducationalRequest(
            user_profile=user_profile,
            application_methods=[ApplicationMethodType.BROADCAST],
            equipment_types=[EquipmentType.SPREADER],
            experience_level=DifficultyLevel.INTERMEDIATE,
            content_preferences={"preferred_formats": ["video_tutorials"]},
            learning_goals=["master_calibration"],
            farm_characteristics={"farm_size_acres": 500, "region": "Midwest"}
        )
        
        # Get educational content
        response = await education_service.get_educational_content(educational_request)
        
        assert isinstance(response, EducationalResponse)
        assert response.recommended_content is not None
        assert response.learning_paths is not None
        
        # Track learning progress
        progress_data = {
            "completed": True,
            "time_spent_minutes": 30,
            "score": 0.85
        }
        
        progress = await education_service.track_learning_progress(
            user_id, "test_content_001", progress_data
        )
        
        assert isinstance(progress, LearningProgress)
        assert progress.user_id == user_id
        
        # Get comprehensive dashboard
        dashboard = await education_service.get_comprehensive_educational_dashboard(user_id)
        
        assert isinstance(dashboard, dict)
        assert dashboard["user_id"] == user_id
        assert "personalized_dashboard" in dashboard
        assert "safety_assessment" in dashboard
        assert "equipment_training_plan" in dashboard
    
    @pytest.mark.asyncio
    async def test_error_handling_across_services(self, education_service):
        """Test error handling across all integrated services."""
        # Test with invalid user ID
        with pytest.raises(ValueError):
            await education_service.personalization_service.get_personalized_content(
                "invalid_user", [ApplicationMethodType.BROADCAST]
            )
        
        # Test with invalid application method
        with pytest.raises(Exception):
            await education_service.get_educational_content(None)


class TestPerformance:
    """Performance tests for the education system."""
    
    @pytest.fixture
    def education_service(self):
        """Create education service instance for performance testing."""
        return EducationService()
    
    @pytest.mark.asyncio
    async def test_response_time_requirements(self, education_service):
        """Test that response times meet requirements (<3 seconds)."""
        import time
        
        user_id = "perf_test_user"
        profile_data = {
            "experience_level": DifficultyLevel.INTERMEDIATE,
            "primary_crops": ["corn"],
            "farm_size_acres": 1000,
            "equipment_available": [EquipmentType.SPREADER],
            "learning_preferences": {},
            "time_availability": "medium",
            "learning_style": "visual",
            "region": "Midwest",
            "goals": ["efficiency"],
            "interests": ["precision"],
            "constraints": []
        }
        
        # Create user profile
        user_profile = await education_service.personalization_service.create_user_profile(
            user_id, profile_data
        )
        
        # Create educational request
        educational_request = EducationalRequest(
            user_profile=user_profile,
            application_methods=[ApplicationMethodType.BROADCAST],
            equipment_types=[EquipmentType.SPREADER],
            experience_level=DifficultyLevel.INTERMEDIATE,
            content_preferences={},
            learning_goals=["efficiency"],
            farm_characteristics={"farm_size_acres": 1000, "region": "Midwest"}
        )
        
        # Measure response time
        start_time = time.time()
        response = await education_service.get_educational_content(educational_request)
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 3.0, f"Response time {response_time}s exceeds 3s requirement"
        assert response.processing_time_ms < 3000, "Processing time exceeds 3 seconds"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])