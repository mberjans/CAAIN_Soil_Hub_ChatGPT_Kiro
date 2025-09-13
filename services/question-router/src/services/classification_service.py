"""
Question Classification Service

Classifies farmer questions into the 20 key question types using NLP.
"""

import re
from typing import List, Dict, Tuple
try:
    from ..models.question_models import QuestionType, ClassificationResult
except ImportError:
    from models.question_models import QuestionType, ClassificationResult


class QuestionClassificationService:
    """Service for classifying farmer questions using keyword matching and NLP."""
    
    def __init__(self):
        """Initialize the classification service with keyword patterns."""
        self.question_patterns = self._build_question_patterns()
    
    def _build_question_patterns(self) -> Dict[QuestionType, List[str]]:
        """Build keyword patterns for each question type."""
        return {
            QuestionType.CROP_SELECTION: [
                "crop varieties", "best suited", "soil type", "climate", "what crop",
                "which variety", "plant", "grow", "suitable", "recommend crop"
            ],
            QuestionType.SOIL_FERTILITY: [
                "soil fertility", "improve soil", "over-applying", "fertilizer",
                "soil health", "organic matter", "soil improvement"
            ],
            QuestionType.CROP_ROTATION: [
                "crop rotation", "rotation plan", "rotate crops", "rotation schedule",
                "what to plant next", "rotation system"
            ],
            QuestionType.NUTRIENT_DEFICIENCY: [
                "nutrient deficient", "nitrogen", "phosphorus", "potassium", "npk",
                "soil test", "deficiency", "lacking nutrients"
            ],
            QuestionType.FERTILIZER_TYPE: [
                "organic fertilizer", "synthetic fertilizer", "slow-release",
                "fertilizer type", "which fertilizer", "organic vs synthetic"
            ],
            QuestionType.FERTILIZER_APPLICATION: [
                "liquid fertilizer", "granular fertilizer", "application method",
                "how to apply", "fertilizer application"
            ],
            QuestionType.FERTILIZER_TIMING: [
                "when to apply", "fertilizer timing", "best time", "season",
                "application timing", "fertilizer schedule"
            ],
            QuestionType.ENVIRONMENTAL_IMPACT: [
                "fertilizer runoff", "environmental impact", "water quality",
                "reduce runoff", "environmental protection"
            ],
            QuestionType.COVER_CROPS: [
                "cover crops", "cover crop", "winter cover", "green manure",
                "soil cover", "nitrogen fixation"
            ],
            QuestionType.SOIL_PH: [
                "soil ph", "ph level", "acidic soil", "alkaline soil", "lime",
                "ph management", "soil acidity"
            ],
            QuestionType.MICRONUTRIENTS: [
                "micronutrients", "zinc", "boron", "sulfur", "iron", "manganese",
                "trace elements", "micro nutrients"
            ],
            QuestionType.PRECISION_AGRICULTURE: [
                "precision agriculture", "drones", "sensors", "mapping", "gps",
                "variable rate", "precision farming", "technology"
            ],
            QuestionType.DROUGHT_MANAGEMENT: [
                "drought", "water conservation", "soil moisture", "irrigation",
                "dry conditions", "water management"
            ],
            QuestionType.DEFICIENCY_DETECTION: [
                "early signs", "deficiency detection", "crop symptoms", "leaf color",
                "plant health", "visual symptoms"
            ],
            QuestionType.TILLAGE_PRACTICES: [
                "no-till", "reduced-till", "tillage", "soil health", "cultivation",
                "minimum tillage", "conservation tillage"
            ],
            QuestionType.COST_EFFECTIVE_STRATEGY: [
                "cost-effective", "fertilizer strategy", "input prices", "budget",
                "economic", "cost", "price", "affordable"
            ],
            QuestionType.WEATHER_IMPACT: [
                "weather patterns", "weather impact", "climate", "rainfall",
                "temperature", "weather conditions"
            ],
            QuestionType.TESTING_INTEGRATION: [
                "soil testing", "tissue testing", "lab test", "nutrient testing",
                "test results", "soil analysis"
            ],
            QuestionType.SUSTAINABLE_YIELD: [
                "sustainable yield", "increase yields", "long-term", "soil health",
                "sustainable farming", "productivity"
            ],
            QuestionType.GOVERNMENT_PROGRAMS: [
                "government programs", "subsidies", "regulations", "compliance",
                "usda", "conservation programs", "farm programs"
            ]
        }
    
    async def classify_question(self, question_text: str) -> ClassificationResult:
        """
        Classify a farmer's question into one of the 20 key question types.
        
        Args:
            question_text: The farmer's question in natural language
            
        Returns:
            ClassificationResult with the classified type and confidence
        """
        question_lower = question_text.lower()
        
        # Score each question type based on keyword matches
        scores = {}
        for question_type, keywords in self.question_patterns.items():
            score = self._calculate_keyword_score(question_lower, keywords)
            if score > 0:
                scores[question_type] = score
        
        if not scores:
            # Default to crop selection if no clear match
            return ClassificationResult(
                question_type=QuestionType.CROP_SELECTION,
                confidence_score=0.3,
                alternative_types=[],
                reasoning="No clear keyword matches found, defaulting to crop selection"
            )
        
        # Sort by score and get top matches
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_type, top_score = sorted_scores[0]
        
        # Normalize confidence score
        max_possible_score = len(self.question_patterns[top_type])
        confidence = min(top_score / max_possible_score, 1.0)
        
        # Get alternative types
        alternatives = [qtype for qtype, score in sorted_scores[1:3] if score > 0.3 * top_score]
        
        return ClassificationResult(
            question_type=top_type,
            confidence_score=confidence,
            alternative_types=alternatives,
            reasoning=f"Matched {int(top_score)} keywords for {top_type.value}"
        )
    
    def _calculate_keyword_score(self, question_text: str, keywords: List[str]) -> float:
        """Calculate score based on keyword matches."""
        score = 0.0
        for keyword in keywords:
            if keyword in question_text:
                # Exact phrase match gets higher score
                score += 1.0
            elif any(word in question_text for word in keyword.split()):
                # Partial word match gets lower score
                score += 0.5
        return score