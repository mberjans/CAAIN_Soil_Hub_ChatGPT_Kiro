"""
Enhanced Classification Service Tests

Tests for the advanced NLP-based question classification service.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from services.classification_service import QuestionClassificationService
from models.question_models import QuestionType, ClassificationResult


class TestEnhancedClassificationService:
    """Test suite for enhanced question classification."""
    
    @pytest.fixture
    def classification_service(self):
        """Create classification service instance."""
        return QuestionClassificationService()
    
    @pytest.mark.asyncio
    async def test_crop_selection_questions(self, classification_service):
        """Test classification of crop selection questions."""
        test_questions = [
            "What crop varieties are best suited to my soil type and climate?",
            "Which corn variety should I plant this year?",
            "What crops grow well in sandy soil?",
            "I need help choosing between different soybean varieties",
            "What's the best crop for my field conditions?"
        ]
        
        for question in test_questions:
            result = await classification_service.classify_question(question)
            
            assert isinstance(result, ClassificationResult)
            assert result.question_type == QuestionType.CROP_SELECTION
            assert result.confidence_score > 0.3
            assert isinstance(result.reasoning, str)
            assert len(result.reasoning) > 10
    
    @pytest.mark.asyncio
    async def test_soil_fertility_questions(self, classification_service):
        """Test classification of soil fertility questions."""
        test_questions = [
            "How can I improve soil fertility without over-applying fertilizer?",
            "My soil health is declining, what should I do?",
            "How do I increase organic matter in my soil?",
            "What's the best way to build soil fertility naturally?"
        ]
        
        for question in test_questions:
            result = await classification_service.classify_question(question)
            
            assert result.question_type == QuestionType.SOIL_FERTILITY
            assert result.confidence_score > 0.3
    
    @pytest.mark.asyncio
    async def test_nutrient_deficiency_questions(self, classification_service):
        """Test classification of nutrient deficiency questions."""
        test_questions = [
            "How do I know if my soil is deficient in nitrogen?",
            "My soil test shows low phosphorus, what should I do?",
            "Are my crops showing signs of potassium deficiency?",
            "What do these soil test results mean?"
        ]
        
        for question in test_questions:
            result = await classification_service.classify_question(question)
            
            assert result.question_type == QuestionType.NUTRIENT_DEFICIENCY
            assert result.confidence_score > 0.3
    
    @pytest.mark.asyncio
    async def test_fertilizer_timing_questions(self, classification_service):
        """Test classification of fertilizer timing questions."""
        test_questions = [
            "When is the best time to apply fertilizer?",
            "Should I fertilize in spring or fall?",
            "When should I side-dress my corn?",
            "What's the optimal timing for nitrogen application?"
        ]
        
        for question in test_questions:
            result = await classification_service.classify_question(question)
            
            assert result.question_type == QuestionType.FERTILIZER_TIMING
            assert result.confidence_score > 0.3
    
    @pytest.mark.asyncio
    async def test_fertilizer_type_questions(self, classification_service):
        """Test classification of fertilizer type questions."""
        test_questions = [
            "Should I use organic or synthetic fertilizers?",
            "What's better: slow-release or quick-release fertilizer?",
            "Which fertilizer type is best for corn?",
            "Should I invest in organic fertilizers?"
        ]
        
        for question in test_questions:
            result = await classification_service.classify_question(question)
            
            assert result.question_type == QuestionType.FERTILIZER_TYPE
            assert result.confidence_score > 0.3
    
    @pytest.mark.asyncio
    async def test_cover_crops_questions(self, classification_service):
        """Test classification of cover crop questions."""
        test_questions = [
            "Should I use cover crops?",
            "What cover crops work best in my area?",
            "How do cover crops help soil health?",
            "When should I plant cover crops?"
        ]
        
        for question in test_questions:
            result = await classification_service.classify_question(question)
            
            assert result.question_type == QuestionType.COVER_CROPS
            assert result.confidence_score > 0.3
    
    @pytest.mark.asyncio
    async def test_ambiguous_questions(self, classification_service):
        """Test classification of ambiguous questions."""
        ambiguous_questions = [
            "What should I do with my field?",
            "I need help with farming",
            "My crops don't look good",
            "How can I improve my farm?"
        ]
        
        for question in ambiguous_questions:
            result = await classification_service.classify_question(question)
            
            # Should still return a classification, even if confidence is lower
            assert isinstance(result.question_type, QuestionType)
            assert 0.0 <= result.confidence_score <= 1.0
            assert len(result.alternative_types) >= 0
    
    @pytest.mark.asyncio
    async def test_confidence_scores(self, classification_service):
        """Test that confidence scores are reasonable."""
        # High confidence question
        high_conf_question = "What crop varieties are best suited to my soil type and climate?"
        result = await classification_service.classify_question(high_conf_question)
        assert result.confidence_score > 0.5
        
        # Lower confidence question
        low_conf_question = "I have a question about farming"
        result = await classification_service.classify_question(low_conf_question)
        assert result.confidence_score < 0.8  # Should be less confident
    
    @pytest.mark.asyncio
    async def test_alternative_types(self, classification_service):
        """Test that alternative types are provided when appropriate."""
        # Question that could match multiple types
        mixed_question = "How do I improve soil fertility and choose the right fertilizer type?"
        result = await classification_service.classify_question(mixed_question)
        
        # Should have some alternative types
        assert len(result.alternative_types) > 0
        assert all(isinstance(alt, QuestionType) for alt in result.alternative_types)
    
    @pytest.mark.asyncio
    async def test_preprocessing(self, classification_service):
        """Test text preprocessing functionality."""
        # Test with various text formats
        test_cases = [
            "WHAT CROP VARIETIES ARE BEST?",  # All caps
            "what crop varieties are best?",   # All lowercase
            "What crop varieties are best???", # Multiple punctuation
            "  What crop varieties are best?  ", # Extra whitespace
        ]
        
        for question in test_cases:
            result = await classification_service.classify_question(question)
            assert result.question_type == QuestionType.CROP_SELECTION
    
    @pytest.mark.asyncio
    async def test_error_handling(self, classification_service):
        """Test error handling in classification."""
        # Test with empty string
        result = await classification_service.classify_question("")
        assert isinstance(result, ClassificationResult)
        
        # Test with very short string
        result = await classification_service.classify_question("hi")
        assert isinstance(result, ClassificationResult)
        
        # Test with very long string
        long_question = "farming " * 200
        result = await classification_service.classify_question(long_question)
        assert isinstance(result, ClassificationResult)
    
    def test_keyword_scoring(self, classification_service):
        """Test enhanced keyword scoring."""
        # Test exact phrase match
        score1 = classification_service._calculate_enhanced_keyword_score(
            "crop varieties are important", ["crop varieties"]
        )
        assert score1 > 0.5
        
        # Test partial match
        score2 = classification_service._calculate_enhanced_keyword_score(
            "crop selection is important", ["crop varieties"]
        )
        assert 0 < score2 < score1
    
    @pytest.mark.asyncio
    async def test_fallback_classification(self, classification_service):
        """Test fallback classification when NLP components fail."""
        # Mock NLP components to fail
        with patch.object(classification_service, '_classify_with_spacy', side_effect=Exception("Mock error")):
            with patch.object(classification_service, '_classify_with_tfidf', side_effect=Exception("Mock error")):
                result = await classification_service.classify_question("What crop should I plant?")
                
                # Should still return a valid result
                assert isinstance(result, ClassificationResult)
                assert isinstance(result.question_type, QuestionType)
    
    def test_service_initialization(self):
        """Test that service initializes properly even without NLP libraries."""
        # This should not raise an exception even if spaCy/NLTK are not available
        service = QuestionClassificationService()
        assert service is not None
        assert hasattr(service, 'question_patterns')
        assert hasattr(service, 'intent_examples')
    
    @pytest.mark.asyncio
    async def test_all_question_types_covered(self, classification_service):
        """Test that all 20 question types can be classified."""
        # Sample questions for each type
        type_questions = {
            QuestionType.CROP_SELECTION: "What crop varieties should I plant?",
            QuestionType.SOIL_FERTILITY: "How can I improve soil fertility?",
            QuestionType.CROP_ROTATION: "What is the optimal crop rotation?",
            QuestionType.NUTRIENT_DEFICIENCY: "Is my soil deficient in nitrogen?",
            QuestionType.FERTILIZER_TYPE: "Should I use organic fertilizer?",
            QuestionType.FERTILIZER_APPLICATION: "Should I use liquid or granular fertilizer?",
            QuestionType.FERTILIZER_TIMING: "When should I apply fertilizer?",
            QuestionType.ENVIRONMENTAL_IMPACT: "How can I reduce fertilizer runoff?",
            QuestionType.COVER_CROPS: "Should I use cover crops?",
            QuestionType.SOIL_PH: "How do I manage soil pH?",
            QuestionType.MICRONUTRIENTS: "Which micronutrients should I supplement?",
            QuestionType.PRECISION_AGRICULTURE: "Are precision agriculture tools worth it?",
            QuestionType.DROUGHT_MANAGEMENT: "How can I conserve soil moisture?",
            QuestionType.DEFICIENCY_DETECTION: "How can I detect nutrient deficiencies early?",
            QuestionType.TILLAGE_PRACTICES: "Should I adopt no-till practices?",
            QuestionType.COST_EFFECTIVE_STRATEGY: "What's the most cost-effective fertilizer strategy?",
            QuestionType.WEATHER_IMPACT: "How do weather patterns affect my crops?",
            QuestionType.TESTING_INTEGRATION: "How can I use soil testing results?",
            QuestionType.SUSTAINABLE_YIELD: "How can I increase yields sustainably?",
            QuestionType.GOVERNMENT_PROGRAMS: "What government programs are available?"
        }
        
        for expected_type, question in type_questions.items():
            result = await classification_service.classify_question(question)
            
            # The classification should either match exactly or be in alternatives
            assert (result.question_type == expected_type or 
                   expected_type in result.alternative_types), \
                   f"Failed to classify '{question}' as {expected_type}, got {result.question_type}"


@pytest.mark.integration
class TestClassificationIntegration:
    """Integration tests for classification service."""
    
    @pytest.mark.asyncio
    async def test_real_farmer_questions(self):
        """Test with realistic farmer questions."""
        service = QuestionClassificationService()
        
        real_questions = [
            "I'm planning my spring planting and need to know which corn variety would work best for my clay soil in Iowa",
            "My soil test came back showing low phosphorus levels - should I apply DAP or MAP fertilizer?",
            "I've been having issues with nitrogen deficiency in my soybeans - when's the best time to side-dress?",
            "Looking to reduce my fertilizer costs this year while maintaining yields - any suggestions?",
            "Thinking about trying cover crops - do crimson clover and winter rye work well together?",
            "My soil pH is 5.2 - how much lime should I apply per acre?",
            "Considering investing in a drone for crop monitoring - is the ROI worth it for a 500-acre operation?",
            "We've had a dry spring - what practices can help my crops handle drought stress better?",
            "I noticed some yellowing in my corn leaves - could this be a nutrient deficiency?",
            "Been doing conventional tillage for years - is switching to no-till worth the transition costs?"
        ]
        
        for question in real_questions:
            result = await service.classify_question(question)
            
            # All should classify successfully with reasonable confidence
            assert isinstance(result, ClassificationResult)
            assert result.confidence_score > 0.2
            assert len(result.reasoning) > 20
            
            print(f"Question: {question[:50]}...")
            print(f"Classification: {result.question_type.value}")
            print(f"Confidence: {result.confidence_score:.2f}")
            print(f"Reasoning: {result.reasoning}")
            print("---")


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])