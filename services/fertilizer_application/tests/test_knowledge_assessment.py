"""
Tests for Knowledge Assessment and Certification System.

This module provides comprehensive tests for the knowledge assessment and
certification functionality in the fertilizer application service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, List, Any

from src.models.educational_models import (
    AssessmentRequest, AssessmentResponse, AssessmentResult,
    CertificationRequest, CertificationResponse, CertificationType,
    AssessmentDifficulty, ContentCategory, AssessmentQuestionType,
    AssessmentQuestion, UserCertification, CertificationStatus
)
from src.services.knowledge_assessment_service import KnowledgeAssessmentService
from src.services.certification_service import CertificationService


class TestKnowledgeAssessmentService:
    """Test suite for KnowledgeAssessmentService."""

    @pytest.fixture
    def assessment_service(self):
        return KnowledgeAssessmentService()

    @pytest.fixture
    def sample_assessment_request(self):
        return AssessmentRequest(
            user_id="test_user_123",
            assessment_category=ContentCategory.APPLICATION_METHODS,
            difficulty_level=AssessmentDifficulty.INTERMEDIATE,
            question_count=10,
            time_limit_minutes=30
        )

    @pytest.fixture
    def sample_certification_request(self):
        return AssessmentRequest(
            user_id="test_user_123",
            certification_type=CertificationType.APPLICATION_METHOD_SPECIALIST,
            question_count=25,
            time_limit_minutes=45
        )

    @pytest.mark.asyncio
    async def test_create_custom_assessment(self, assessment_service, sample_assessment_request):
        """Test creation of custom assessment."""
        with patch.object(assessment_service, '_store_assessment_attempt', return_value=None):
            response = await assessment_service.create_assessment(sample_assessment_request)
            
            assert isinstance(response, AssessmentResponse)
            assert response.assessment_id is not None
            assert response.attempt_id is not None
            assert len(response.questions) <= sample_assessment_request.question_count
            assert response.time_limit_minutes == sample_assessment_request.time_limit_minutes
            assert response.total_points > 0
            assert response.passing_score == 75.0

    @pytest.mark.asyncio
    async def test_create_certification_assessment(self, assessment_service, sample_certification_request):
        """Test creation of certification assessment."""
        with patch.object(assessment_service, '_store_assessment_attempt', return_value=None):
            response = await assessment_service.create_assessment(sample_certification_request)
            
            assert isinstance(response, AssessmentResponse)
            assert response.assessment_id is not None
            assert response.attempt_id is not None
            assert len(response.questions) <= sample_certification_request.question_count
            assert response.passing_score == 80.0  # Certification assessment passing score

    @pytest.mark.asyncio
    async def test_submit_assessment_success(self, assessment_service):
        """Test successful assessment submission."""
        attempt_id = "test_attempt_123"
        answers = {
            "app_method_001": "Fast coverage of large areas",
            "app_method_002": "Band application",
            "app_method_003": "True"
        }
        
        # Mock assessment attempt and assessment
        mock_attempt = MagicMock()
        mock_attempt.attempt_id = attempt_id
        mock_attempt.user_id = "test_user_123"
        mock_attempt.assessment_id = "test_assessment_123"
        mock_attempt.start_time = datetime.utcnow()
        
        mock_assessment = MagicMock()
        mock_assessment.questions = [
            AssessmentQuestion(
                question_id="app_method_001",
                question_text="What is the primary advantage of broadcast application method?",
                question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
                difficulty=AssessmentDifficulty.BASIC,
                category=ContentCategory.APPLICATION_METHODS,
                options=["Precise nutrient placement", "Fast coverage of large areas", "Minimal equipment requirements"],
                correct_answer="Fast coverage of large areas",
                explanation="Broadcast application allows rapid coverage of large field areas.",
                points=1
            )
        ]
        mock_assessment.total_points = 1
        mock_assessment.passing_score_percentage = 75.0
        mock_assessment.category = ContentCategory.APPLICATION_METHODS
        mock_assessment.certification_eligible = False
        
        with patch.object(assessment_service, '_get_assessment_attempt', return_value=mock_attempt):
            with patch.object(assessment_service, '_get_assessment', return_value=mock_assessment):
                with patch.object(assessment_service, '_update_assessment_attempt', return_value=None):
                    result = await assessment_service.submit_assessment(attempt_id, answers)
                    
                    assert isinstance(result, AssessmentResult)
                    assert result.attempt_id == attempt_id
                    assert result.user_id == "test_user_123"
                    assert result.score >= 0
                    assert result.points_earned >= 0
                    assert result.total_points == 1
                    assert isinstance(result.passed, bool)
                    assert isinstance(result.strengths, list)
                    assert isinstance(result.areas_for_improvement, list)
                    assert isinstance(result.recommendations, list)

    @pytest.mark.asyncio
    async def test_submit_assessment_invalid_attempt(self, assessment_service):
        """Test assessment submission with invalid attempt ID."""
        attempt_id = "invalid_attempt"
        answers = {"question_1": "answer_1"}
        
        with patch.object(assessment_service, '_get_assessment_attempt', return_value=None):
            with pytest.raises(ValueError, match="Assessment attempt.*not found"):
                await assessment_service.submit_assessment(attempt_id, answers)

    def test_evaluate_answer_multiple_choice_correct(self, assessment_service):
        """Test evaluation of correct multiple choice answer."""
        question = AssessmentQuestion(
            question_id="test_001",
            question_text="Test question",
            question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
            difficulty=AssessmentDifficulty.BASIC,
            category=ContentCategory.APPLICATION_METHODS,
            options=["Option A", "Option B"],
            correct_answer="Option A",
            explanation="Correct explanation",
            points=1
        )
        
        is_correct, explanation = assessment_service._evaluate_answer(question, "Option A")
        assert is_correct is True
        assert explanation == "Correct explanation"

    def test_evaluate_answer_multiple_choice_incorrect(self, assessment_service):
        """Test evaluation of incorrect multiple choice answer."""
        question = AssessmentQuestion(
            question_id="test_001",
            question_text="Test question",
            question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
            difficulty=AssessmentDifficulty.BASIC,
            category=ContentCategory.APPLICATION_METHODS,
            options=["Option A", "Option B"],
            correct_answer="Option A",
            explanation="Correct explanation",
            points=1
        )
        
        is_correct, explanation = assessment_service._evaluate_answer(question, "Option B")
        assert is_correct is False
        assert explanation == "Correct explanation"

    def test_evaluate_answer_multiple_select_correct(self, assessment_service):
        """Test evaluation of correct multiple select answer."""
        question = AssessmentQuestion(
            question_id="test_001",
            question_text="Test question",
            question_type=AssessmentQuestionType.MULTIPLE_SELECT,
            difficulty=AssessmentDifficulty.BASIC,
            category=ContentCategory.APPLICATION_METHODS,
            options=["Option A", "Option B", "Option C"],
            correct_answer=["Option A", "Option B"],
            explanation="Correct explanation",
            points=2
        )
        
        is_correct, explanation = assessment_service._evaluate_answer(question, ["Option A", "Option B"])
        assert is_correct is True
        assert explanation == "Correct explanation"

    def test_evaluate_answer_no_answer(self, assessment_service):
        """Test evaluation when no answer is provided."""
        question = AssessmentQuestion(
            question_id="test_001",
            question_text="Test question",
            question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
            difficulty=AssessmentDifficulty.BASIC,
            category=ContentCategory.APPLICATION_METHODS,
            options=["Option A", "Option B"],
            correct_answer="Option A",
            explanation="Correct explanation",
            points=1
        )
        
        is_correct, explanation = assessment_service._evaluate_answer(question, None)
        assert is_correct is False
        assert explanation == "No answer provided"

    @pytest.mark.asyncio
    async def test_get_certification_requirements(self, assessment_service):
        """Test retrieval of certification requirements."""
        requirements = await assessment_service.get_certification_requirements(
            CertificationType.APPLICATION_METHOD_SPECIALIST
        )
        
        assert isinstance(requirements, dict)
        assert "required_assessments" in requirements
        assert "minimum_scores" in requirements
        assert "practical_experience_hours" in requirements
        assert "continuing_education_hours" in requirements
        assert "validity_period_months" in requirements

    @pytest.mark.asyncio
    async def test_check_certification_eligibility(self, assessment_service):
        """Test certification eligibility checking."""
        eligibility = await assessment_service.check_certification_eligibility(
            "test_user_123",
            CertificationType.APPLICATION_METHOD_SPECIALIST
        )
        
        assert isinstance(eligibility, dict)
        assert "eligible" in eligibility
        assert "requirements_met" in eligibility
        assert "missing_requirements" in eligibility
        assert "next_steps" in eligibility


class TestCertificationService:
    """Test suite for CertificationService."""

    @pytest.fixture
    def certification_service(self):
        return CertificationService()

    @pytest.fixture
    def sample_certification_request(self):
        return CertificationRequest(
            user_id="test_user_123",
            certification_type=CertificationType.APPLICATION_METHOD_SPECIALIST,
            assessment_results=["assessment_1", "assessment_2", "assessment_3"],
            practical_experience_hours=40,
            continuing_education_hours=8,
            supporting_documents=["doc1.pdf", "doc2.pdf"]
        )

    @pytest.mark.asyncio
    async def test_issue_certification_success(self, certification_service, sample_certification_request):
        """Test successful certification issuance."""
        with patch.object(certification_service, '_store_certification', return_value=None):
            response = await certification_service.issue_certification(sample_certification_request)
            
            assert isinstance(response, CertificationResponse)
            assert response.certification_record_id is not None
            assert response.user_id == sample_certification_request.user_id
            assert response.certification_type == sample_certification_request.certification_type
            assert response.certification_id is not None
            assert response.issued_date is not None
            assert response.expiry_date is not None
            assert response.verification_code is not None
            assert response.status == CertificationStatus.ACTIVE
            assert len(response.skills_verified) > 0
            assert len(response.renewal_requirements) > 0

    @pytest.mark.asyncio
    async def test_issue_certification_insufficient_hours(self, certification_service):
        """Test certification issuance with insufficient practical experience hours."""
        request = CertificationRequest(
            user_id="test_user_123",
            certification_type=CertificationType.APPLICATION_METHOD_SPECIALIST,
            assessment_results=["assessment_1", "assessment_2", "assessment_3"],
            practical_experience_hours=10,  # Insufficient (requires 40)
            continuing_education_hours=8
        )
        
        with pytest.raises(ValueError, match="Certification requirements not met"):
            await certification_service.issue_certification(request)

    @pytest.mark.asyncio
    async def test_issue_certification_invalid_type(self, certification_service):
        """Test certification issuance with invalid certification type."""
        request = CertificationRequest(
            user_id="test_user_123",
            certification_type="invalid_type",  # Invalid type
            assessment_results=["assessment_1"],
            practical_experience_hours=40,
            continuing_education_hours=8
        )
        
        with pytest.raises(ValueError, match="Certification requirements not met"):
            await certification_service.issue_certification(request)

    def test_generate_certification_id(self, certification_service):
        """Test certification ID generation."""
        cert_id = certification_service._generate_certification_id(
            CertificationType.APPLICATION_METHOD_SPECIALIST
        )
        
        assert isinstance(cert_id, str)
        assert cert_id.startswith("AFAS-APP-")
        assert len(cert_id) > 10

    def test_generate_verification_code(self, certification_service):
        """Test verification code generation."""
        verification_code = certification_service._generate_verification_code(
            "cert_record_123",
            "user_123"
        )
        
        assert isinstance(verification_code, str)
        assert len(verification_code) == 16
        assert verification_code.isupper()

    def test_get_verified_skills(self, certification_service):
        """Test retrieval of verified skills for certification type."""
        skills = certification_service._get_verified_skills(
            CertificationType.APPLICATION_METHOD_SPECIALIST
        )
        
        assert isinstance(skills, list)
        assert len(skills) > 0
        assert all(isinstance(skill, str) for skill in skills)

    @pytest.mark.asyncio
    async def test_get_user_certifications(self, certification_service):
        """Test retrieval of user certifications."""
        certifications = await certification_service.get_user_certifications("test_user_123")
        
        assert isinstance(certifications, list)

    @pytest.mark.asyncio
    async def test_verify_certification(self, certification_service):
        """Test certification verification."""
        certification = await certification_service.verify_certification("test_verification_code")
        
        # Should return None for non-existent verification code
        assert certification is None

    @pytest.mark.asyncio
    async def test_get_expiring_certifications(self, certification_service):
        """Test retrieval of expiring certifications."""
        expiring = await certification_service.get_expiring_certifications(30)
        
        assert isinstance(expiring, list)

    @pytest.mark.asyncio
    async def test_get_certification_statistics(self, certification_service):
        """Test retrieval of certification statistics."""
        stats = await certification_service.get_certification_statistics()
        
        assert isinstance(stats, dict)
        assert "total_certifications" in stats
        assert "active_certifications" in stats
        assert "expired_certifications" in stats
        assert "by_type" in stats


class TestAssessmentModels:
    """Test suite for assessment and certification models."""

    def test_assessment_request_validation(self):
        """Test AssessmentRequest model validation."""
        request = AssessmentRequest(
            user_id="test_user_123",
            assessment_category=ContentCategory.APPLICATION_METHODS,
            difficulty_level=AssessmentDifficulty.INTERMEDIATE,
            question_count=10,
            time_limit_minutes=30
        )
        
        assert request.user_id == "test_user_123"
        assert request.assessment_category == ContentCategory.APPLICATION_METHODS
        assert request.difficulty_level == AssessmentDifficulty.INTERMEDIATE
        assert request.question_count == 10
        assert request.time_limit_minutes == 30

    def test_certification_request_validation(self):
        """Test CertificationRequest model validation."""
        request = CertificationRequest(
            user_id="test_user_123",
            certification_type=CertificationType.APPLICATION_METHOD_SPECIALIST,
            assessment_results=["assessment_1", "assessment_2"],
            practical_experience_hours=40,
            continuing_education_hours=8
        )
        
        assert request.user_id == "test_user_123"
        assert request.certification_type == CertificationType.APPLICATION_METHOD_SPECIALIST
        assert len(request.assessment_results) == 2
        assert request.practical_experience_hours == 40
        assert request.continuing_education_hours == 8

    def test_assessment_question_creation(self):
        """Test AssessmentQuestion model creation."""
        question = AssessmentQuestion(
            question_id="test_001",
            question_text="What is the primary advantage of broadcast application?",
            question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
            difficulty=AssessmentDifficulty.BASIC,
            category=ContentCategory.APPLICATION_METHODS,
            options=["Option A", "Option B", "Option C"],
            correct_answer="Option A",
            explanation="Broadcast application allows rapid coverage.",
            points=1
        )
        
        assert question.question_id == "test_001"
        assert question.question_type == AssessmentQuestionType.MULTIPLE_CHOICE
        assert question.difficulty == AssessmentDifficulty.BASIC
        assert question.category == ContentCategory.APPLICATION_METHODS
        assert len(question.options) == 3
        assert question.correct_answer == "Option A"
        assert question.points == 1


# Integration Tests

class TestKnowledgeAssessmentIntegration:
    """Integration tests for knowledge assessment system."""

    @pytest.mark.asyncio
    async def test_full_assessment_workflow(self):
        """Test complete assessment workflow from creation to submission."""
        assessment_service = KnowledgeAssessmentService()
        
        # Create assessment
        request = AssessmentRequest(
            user_id="integration_test_user",
            assessment_category=ContentCategory.APPLICATION_METHODS,
            difficulty_level=AssessmentDifficulty.BASIC,
            question_count=3,
            time_limit_minutes=15
        )
        
        with patch.object(assessment_service, '_store_assessment_attempt', return_value=None):
            response = await assessment_service.create_assessment(request)
            
            assert response.assessment_id is not None
            assert response.attempt_id is not None
            assert len(response.questions) <= 3
            
            # Submit assessment with answers
            answers = {}
            for question in response.questions:
                if question.question_type == AssessmentQuestionType.MULTIPLE_CHOICE:
                    answers[question.question_id] = question.options[0]
                elif question.question_type == AssessmentQuestionType.TRUE_FALSE:
                    answers[question.question_id] = "True"
            
            # Mock the assessment retrieval for submission
            mock_attempt = MagicMock()
            mock_attempt.attempt_id = response.attempt_id
            mock_attempt.user_id = request.user_id
            mock_attempt.assessment_id = response.assessment_id
            mock_attempt.start_time = datetime.utcnow()
            
            mock_assessment = MagicMock()
            mock_assessment.questions = response.questions
            mock_assessment.total_points = sum(q.points for q in response.questions)
            mock_assessment.passing_score_percentage = 75.0
            mock_assessment.category = ContentCategory.APPLICATION_METHODS
            mock_assessment.certification_eligible = False
            
            with patch.object(assessment_service, '_get_assessment_attempt', return_value=mock_attempt):
                with patch.object(assessment_service, '_get_assessment', return_value=mock_assessment):
                    with patch.object(assessment_service, '_update_assessment_attempt', return_value=None):
                        result = await assessment_service.submit_assessment(response.attempt_id, answers)
                        
                        assert result.attempt_id == response.attempt_id
                        assert result.user_id == request.user_id
                        assert result.score >= 0
                        assert result.total_points == mock_assessment.total_points
                        assert isinstance(result.passed, bool)
                        assert isinstance(result.strengths, list)
                        assert isinstance(result.areas_for_improvement, list)
                        assert isinstance(result.recommendations, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
