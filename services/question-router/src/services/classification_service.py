"""
Question Classification Service

Classifies farmer questions into the 20 key question types using advanced NLP with spaCy and NLTK.
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import numpy as np

# NLP imports
try:
    import spacy
    from spacy.matcher import Matcher
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available, falling back to basic classification")

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    from nltk.tag import pos_tag
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available, falling back to basic classification")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available, falling back to basic classification")

try:
    from ..models.question_models import QuestionType, ClassificationResult
except ImportError:
    from models.question_models import QuestionType, ClassificationResult


class QuestionClassificationService:
    """Service for classifying farmer questions using advanced NLP techniques."""
    
    def __init__(self):
        """Initialize the classification service with NLP models and patterns."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize NLP components
        self.nlp = self._load_spacy_model()
        self.matcher = None
        self.lemmatizer = None
        self.stop_words = set()
        self.tfidf_vectorizer = None
        
        # Initialize NLP tools
        self._initialize_nltk()
        self._initialize_spacy_matcher()
        
        # Build classification patterns and training data
        self.question_patterns = self._build_question_patterns()
        self.intent_examples = self._build_intent_examples()
        self.semantic_keywords = self._build_semantic_keywords()
        
        # Initialize TF-IDF for semantic similarity
        self._initialize_tfidf_classifier()
    
    def _load_spacy_model(self):
        """Load spaCy model with fallback options."""
        if not SPACY_AVAILABLE:
            return None
            
        try:
            # Try to load the English model
            nlp = spacy.load("en_core_web_sm")
            self.logger.info("Loaded spaCy en_core_web_sm model")
            return nlp
        except OSError:
            try:
                # Fallback to basic English model
                nlp = spacy.load("en_core_web_md")
                self.logger.info("Loaded spaCy en_core_web_md model")
                return nlp
            except OSError:
                self.logger.warning("No spaCy English model found. Install with: python -m spacy download en_core_web_sm")
                return None
    
    def _initialize_nltk(self):
        """Initialize NLTK components."""
        if not NLTK_AVAILABLE:
            return
            
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
            
            # Add agricultural stop words
            agricultural_stops = {'farm', 'farming', 'farmer', 'field', 'land', 'acre', 'acres'}
            self.stop_words.update(agricultural_stops)
            
            self.logger.info("NLTK components initialized successfully")
        except Exception as e:
            self.logger.warning(f"Error initializing NLTK: {e}")
    
    def _initialize_spacy_matcher(self):
        """Initialize spaCy pattern matcher."""
        if not self.nlp:
            return
            
        self.matcher = Matcher(self.nlp.vocab)
        
        # Define patterns for each question type
        patterns = {
            "CROP_SELECTION": [
                [{"LOWER": {"IN": ["what", "which"]}}, {"LOWER": {"IN": ["crop", "crops", "variety", "varieties"]}}],
                [{"LOWER": "crop"}, {"LOWER": {"IN": ["selection", "choice", "recommendation"]}}],
                [{"LOWER": {"IN": ["plant", "grow"]}}, {"LOWER": {"IN": ["what", "which"]}}]
            ],
            "SOIL_FERTILITY": [
                [{"LOWER": "soil"}, {"LOWER": {"IN": ["fertility", "health", "improvement"]}}],
                [{"LOWER": {"IN": ["improve", "enhance"]}}, {"LOWER": "soil"}],
                [{"LOWER": "over"}, {"LOWER": {"IN": ["applying", "fertilizing"]}}]
            ],
            "NUTRIENT_DEFICIENCY": [
                [{"LOWER": {"IN": ["nitrogen", "phosphorus", "potassium", "npk"]}}, {"LOWER": {"IN": ["deficient", "deficiency", "lacking"]}}],
                [{"LOWER": "soil"}, {"LOWER": {"IN": ["test", "testing"]}}, {"LOWER": {"IN": ["results", "values"]}}],
                [{"LOWER": {"IN": ["nutrient", "nutrients"]}}, {"LOWER": {"IN": ["deficient", "lacking", "low"]}}]
            ],
            "FERTILIZER_TIMING": [
                [{"LOWER": {"IN": ["when", "timing"]}}, {"LOWER": {"IN": ["apply", "fertilize", "fertilizer"]}}],
                [{"LOWER": "best"}, {"LOWER": "time"}, {"LOWER": {"IN": ["fertilizer", "fertilize"]}}],
                [{"LOWER": "fertilizer"}, {"LOWER": {"IN": ["schedule", "timing", "calendar"]}}]
            ]
        }
        
        # Add patterns to matcher
        for intent, pattern_list in patterns.items():
            for i, pattern in enumerate(pattern_list):
                self.matcher.add(f"{intent}_{i}", [pattern])
        
        self.logger.info("spaCy matcher initialized with agricultural patterns")
    
    def _initialize_tfidf_classifier(self):
        """Initialize TF-IDF vectorizer for semantic similarity."""
        if not SKLEARN_AVAILABLE:
            return
            
        try:
            # Prepare training texts for each question type
            training_texts = []
            training_labels = []
            
            for question_type, examples in self.intent_examples.items():
                for example in examples:
                    training_texts.append(self._preprocess_text(example))
                    training_labels.append(question_type)
            
            # Initialize and fit TF-IDF vectorizer
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.8
            )
            
            if training_texts:
                self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(training_texts)
                self.training_labels = training_labels
                self.logger.info("TF-IDF classifier initialized successfully")
            
        except Exception as e:
            self.logger.warning(f"Error initializing TF-IDF classifier: {e}")
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text using NLTK."""
        if not NLTK_AVAILABLE:
            return text.lower()
            
        try:
            # Tokenize and lemmatize
            tokens = word_tokenize(text.lower())
            
            # Remove stop words and non-alphabetic tokens
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                     if token.isalpha() and token not in self.stop_words]
            
            return ' '.join(tokens)
        except Exception:
            return text.lower()
    
    def _build_question_patterns(self) -> Dict[QuestionType, List[str]]:
        """Build enhanced keyword patterns for each question type."""
        return {
            QuestionType.CROP_SELECTION: [
                "crop varieties", "best suited", "soil type", "climate", "what crop",
                "which variety", "plant", "grow", "suitable", "recommend crop",
                "crop choice", "variety selection", "cultivar", "hybrid"
            ],
            QuestionType.SOIL_FERTILITY: [
                "soil fertility", "improve soil", "over-applying", "fertilizer",
                "soil health", "organic matter", "soil improvement", "soil quality",
                "fertility management", "soil enhancement", "soil condition"
            ],
            QuestionType.CROP_ROTATION: [
                "crop rotation", "rotation plan", "rotate crops", "rotation schedule",
                "what to plant next", "rotation system", "cropping sequence",
                "rotation strategy", "crop sequence", "rotational farming"
            ],
            QuestionType.NUTRIENT_DEFICIENCY: [
                "nutrient deficient", "nitrogen", "phosphorus", "potassium", "npk",
                "soil test", "deficiency", "lacking nutrients", "nutrient levels",
                "soil analysis", "nutrient status", "fertilizer needs"
            ],
            QuestionType.FERTILIZER_TYPE: [
                "organic fertilizer", "synthetic fertilizer", "slow-release",
                "fertilizer type", "which fertilizer", "organic vs synthetic",
                "fertilizer choice", "fertilizer selection", "fertilizer options"
            ],
            QuestionType.FERTILIZER_APPLICATION: [
                "liquid fertilizer", "granular fertilizer", "application method",
                "how to apply", "fertilizer application", "broadcast", "banding",
                "foliar application", "side-dress", "incorporation"
            ],
            QuestionType.FERTILIZER_TIMING: [
                "when to apply", "fertilizer timing", "best time", "season",
                "application timing", "fertilizer schedule", "split application",
                "pre-plant", "side-dress timing", "fall application"
            ],
            QuestionType.ENVIRONMENTAL_IMPACT: [
                "fertilizer runoff", "environmental impact", "water quality",
                "reduce runoff", "environmental protection", "leaching",
                "groundwater", "surface water", "nutrient loss"
            ],
            QuestionType.COVER_CROPS: [
                "cover crops", "cover crop", "winter cover", "green manure",
                "soil cover", "nitrogen fixation", "catch crop", "living mulch",
                "companion planting", "intercropping"
            ],
            QuestionType.SOIL_PH: [
                "soil ph", "ph level", "acidic soil", "alkaline soil", "lime",
                "ph management", "soil acidity", "soil alkalinity", "liming",
                "ph adjustment", "soil reaction"
            ],
            QuestionType.MICRONUTRIENTS: [
                "micronutrients", "zinc", "boron", "sulfur", "iron", "manganese",
                "trace elements", "micro nutrients", "copper", "molybdenum",
                "chlorine", "secondary nutrients"
            ],
            QuestionType.PRECISION_AGRICULTURE: [
                "precision agriculture", "drones", "sensors", "mapping", "gps",
                "variable rate", "precision farming", "technology", "grid sampling",
                "yield mapping", "soil sampling", "remote sensing"
            ],
            QuestionType.DROUGHT_MANAGEMENT: [
                "drought", "water conservation", "soil moisture", "irrigation",
                "dry conditions", "water management", "water stress", "drought stress",
                "moisture retention", "water use efficiency"
            ],
            QuestionType.DEFICIENCY_DETECTION: [
                "early signs", "deficiency detection", "crop symptoms", "leaf color",
                "plant health", "visual symptoms", "chlorosis", "necrosis",
                "stunting", "discoloration", "plant diagnosis"
            ],
            QuestionType.TILLAGE_PRACTICES: [
                "no-till", "reduced-till", "tillage", "soil health", "cultivation",
                "minimum tillage", "conservation tillage", "strip-till",
                "conventional tillage", "soil disturbance"
            ],
            QuestionType.COST_EFFECTIVE_STRATEGY: [
                "cost-effective", "fertilizer strategy", "input prices", "budget",
                "economic", "cost", "price", "affordable", "roi", "return on investment",
                "cost analysis", "economic optimization"
            ],
            QuestionType.WEATHER_IMPACT: [
                "weather patterns", "weather impact", "climate", "rainfall",
                "temperature", "weather conditions", "seasonal weather",
                "climate change", "weather forecast", "growing conditions"
            ],
            QuestionType.TESTING_INTEGRATION: [
                "soil testing", "tissue testing", "lab test", "nutrient testing",
                "test results", "soil analysis", "plant analysis", "leaf analysis",
                "soil sampling", "test interpretation"
            ],
            QuestionType.SUSTAINABLE_YIELD: [
                "sustainable yield", "increase yields", "long-term", "soil health",
                "sustainable farming", "productivity", "yield optimization",
                "sustainable intensification", "regenerative agriculture"
            ],
            QuestionType.GOVERNMENT_PROGRAMS: [
                "government programs", "subsidies", "regulations", "compliance",
                "usda", "conservation programs", "farm programs", "cost-share",
                "incentives", "farm bill", "conservation reserve"
            ]
        }
    
    def _build_intent_examples(self) -> Dict[QuestionType, List[str]]:
        """Build example questions for each intent type for training."""
        return {
            QuestionType.CROP_SELECTION: [
                "What crop varieties are best suited to my soil type and climate?",
                "Which corn variety should I plant this year?",
                "What crops grow well in sandy soil?",
                "I need help choosing between different soybean varieties",
                "What's the best crop for my field conditions?"
            ],
            QuestionType.SOIL_FERTILITY: [
                "How can I improve soil fertility without over-applying fertilizer?",
                "My soil health is declining, what should I do?",
                "How do I increase organic matter in my soil?",
                "What's the best way to build soil fertility naturally?",
                "How can I improve my soil without chemicals?"
            ],
            QuestionType.CROP_ROTATION: [
                "What is the optimal crop rotation plan for my land?",
                "Should I rotate corn and soybeans?",
                "What crop should I plant after wheat?",
                "How do I plan a 4-year rotation?",
                "What's a good rotation for soil health?"
            ],
            QuestionType.NUTRIENT_DEFICIENCY: [
                "How do I know if my soil is deficient in nitrogen?",
                "My soil test shows low phosphorus, what should I do?",
                "Are my crops showing signs of potassium deficiency?",
                "How can I tell if my soil needs more nutrients?",
                "What do these soil test results mean?"
            ],
            QuestionType.FERTILIZER_TYPE: [
                "Should I use organic or synthetic fertilizers?",
                "What's better: slow-release or quick-release fertilizer?",
                "Which fertilizer type is best for corn?",
                "Should I invest in organic fertilizers?",
                "What are the pros and cons of different fertilizer types?"
            ],
            QuestionType.FERTILIZER_APPLICATION: [
                "Should I use liquid or granular fertilizer?",
                "What's the best way to apply fertilizer?",
                "How do I decide between broadcast and banded application?",
                "Is foliar feeding worth it?",
                "What application method gives best results?"
            ],
            QuestionType.FERTILIZER_TIMING: [
                "When is the best time to apply fertilizer?",
                "Should I fertilize in spring or fall?",
                "When should I side-dress my corn?",
                "What's the optimal timing for nitrogen application?",
                "How do I time my fertilizer applications?"
            ],
            QuestionType.ENVIRONMENTAL_IMPACT: [
                "How can I reduce fertilizer runoff?",
                "What practices protect water quality?",
                "How do I prevent nutrient leaching?",
                "What's the environmental impact of my fertilizer use?",
                "How can I farm more sustainably?"
            ],
            QuestionType.COVER_CROPS: [
                "Should I use cover crops?",
                "What cover crops work best in my area?",
                "How do cover crops help soil health?",
                "When should I plant cover crops?",
                "What are the benefits of cover cropping?"
            ],
            QuestionType.SOIL_PH: [
                "How do I manage soil pH?",
                "My soil is too acidic, what should I do?",
                "How much lime should I apply?",
                "What's the ideal pH for corn?",
                "How do I raise my soil pH?"
            ]
        }
    
    def _build_semantic_keywords(self) -> Dict[QuestionType, List[str]]:
        """Build semantic keyword groups for better matching."""
        return {
            QuestionType.CROP_SELECTION: [
                "variety", "cultivar", "hybrid", "selection", "choice", "recommendation",
                "suitable", "adapted", "climate", "zone", "growing", "planting"
            ],
            QuestionType.SOIL_FERTILITY: [
                "fertility", "health", "quality", "improvement", "enhancement",
                "organic", "matter", "biology", "microbial", "structure"
            ],
            QuestionType.NUTRIENT_DEFICIENCY: [
                "deficiency", "deficient", "lacking", "low", "insufficient",
                "nitrogen", "phosphorus", "potassium", "test", "analysis"
            ],
            QuestionType.FERTILIZER_TIMING: [
                "timing", "when", "schedule", "application", "split", "season",
                "spring", "fall", "pre-plant", "side-dress", "topdress"
            ]
        }
    
    async def classify_question(self, question_text: str) -> ClassificationResult:
        """
        Classify a farmer's question using advanced NLP techniques.
        
        Uses multiple classification methods:
        1. spaCy pattern matching
        2. TF-IDF semantic similarity
        3. Enhanced keyword matching
        4. NLTK-based linguistic analysis
        
        Args:
            question_text: The farmer's question in natural language
            
        Returns:
            ClassificationResult with the classified type and confidence
        """
        try:
            # Preprocess the question
            processed_text = self._preprocess_text(question_text)
            
            # Get scores from different classification methods
            spacy_scores = self._classify_with_spacy(question_text)
            tfidf_scores = self._classify_with_tfidf(processed_text)
            keyword_scores = self._classify_with_keywords(question_text.lower())
            linguistic_scores = self._classify_with_linguistics(question_text)
            
            # Combine scores with weights
            combined_scores = self._combine_classification_scores(
                spacy_scores, tfidf_scores, keyword_scores, linguistic_scores
            )
            
            if not combined_scores:
                # Default to crop selection if no clear match
                return ClassificationResult(
                    question_type=QuestionType.CROP_SELECTION,
                    confidence_score=0.3,
                    alternative_types=[],
                    reasoning="No clear matches found using any classification method, defaulting to crop selection"
                )
            
            # Sort by combined score and get top matches
            sorted_scores = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
            top_type, top_score = sorted_scores[0]
            
            # Calculate confidence score (normalized)
            confidence = min(top_score, 1.0)
            
            # Get alternative types
            alternatives = [qtype for qtype, score in sorted_scores[1:3] 
                          if score > 0.4 * top_score and score > 0.2]
            
            # Generate reasoning
            reasoning = self._generate_classification_reasoning(
                top_type, spacy_scores, tfidf_scores, keyword_scores, linguistic_scores
            )
            
            return ClassificationResult(
                question_type=top_type,
                confidence_score=confidence,
                alternative_types=alternatives,
                reasoning=reasoning
            )
            
        except Exception as e:
            self.logger.error(f"Error in question classification: {e}")
            # Fallback to basic keyword matching
            return await self._fallback_classification(question_text)
    
    def _classify_with_spacy(self, question_text: str) -> Dict[QuestionType, float]:
        """Classify using spaCy pattern matching."""
        scores = defaultdict(float)
        
        if not self.nlp or not self.matcher:
            return scores
        
        try:
            doc = self.nlp(question_text)
            matches = self.matcher(doc)
            
            for match_id, start, end in matches:
                pattern_name = self.nlp.vocab.strings[match_id]
                question_type_str = pattern_name.split('_')[0]
                
                # Map pattern name to QuestionType
                for qtype in QuestionType:
                    if qtype.name == question_type_str:
                        scores[qtype] += 0.8  # High weight for pattern matches
                        break
            
            # Also use spaCy's similarity if available
            if hasattr(doc, 'vector') and doc.vector.any():
                for question_type, examples in self.intent_examples.items():
                    max_similarity = 0.0
                    for example in examples[:3]:  # Check top 3 examples
                        example_doc = self.nlp(example)
                        if hasattr(example_doc, 'vector') and example_doc.vector.any():
                            similarity = doc.similarity(example_doc)
                            max_similarity = max(max_similarity, similarity)
                    
                    if max_similarity > 0.5:  # Threshold for similarity
                        scores[question_type] += max_similarity * 0.6
            
        except Exception as e:
            self.logger.warning(f"Error in spaCy classification: {e}")
        
        return dict(scores)
    
    def _classify_with_tfidf(self, processed_text: str) -> Dict[QuestionType, float]:
        """Classify using TF-IDF semantic similarity."""
        scores = defaultdict(float)
        
        if not self.tfidf_vectorizer or not hasattr(self, 'tfidf_matrix'):
            return scores
        
        try:
            # Transform the question text
            question_vector = self.tfidf_vectorizer.transform([processed_text])
            
            # Calculate cosine similarity with training examples
            similarities = cosine_similarity(question_vector, self.tfidf_matrix).flatten()
            
            # Aggregate scores by question type
            type_scores = defaultdict(list)
            for i, similarity in enumerate(similarities):
                if similarity > 0.1:  # Threshold for relevance
                    question_type = self.training_labels[i]
                    type_scores[question_type].append(similarity)
            
            # Calculate average similarity for each type
            for question_type, sim_list in type_scores.items():
                scores[question_type] = np.mean(sim_list) * 0.7  # Weight for TF-IDF
            
        except Exception as e:
            self.logger.warning(f"Error in TF-IDF classification: {e}")
        
        return dict(scores)
    
    def _classify_with_keywords(self, question_text: str) -> Dict[QuestionType, float]:
        """Enhanced keyword-based classification."""
        scores = defaultdict(float)
        
        for question_type, keywords in self.question_patterns.items():
            score = self._calculate_enhanced_keyword_score(question_text, keywords)
            if score > 0:
                scores[question_type] = score * 0.5  # Weight for keyword matching
        
        return dict(scores)
    
    def _classify_with_linguistics(self, question_text: str) -> Dict[QuestionType, float]:
        """Classify using linguistic features (NLTK)."""
        scores = defaultdict(float)
        
        if not NLTK_AVAILABLE:
            return scores
        
        try:
            # Tokenize and get POS tags
            tokens = word_tokenize(question_text.lower())
            pos_tags = pos_tag(tokens)
            
            # Extract linguistic features
            question_words = [token for token, pos in pos_tags if pos.startswith('W')]  # WH-words
            nouns = [token for token, pos in pos_tags if pos.startswith('N')]
            verbs = [token for token, pos in pos_tags if pos.startswith('V')]
            
            # Score based on linguistic patterns
            for question_type, semantic_keywords in self.semantic_keywords.items():
                linguistic_score = 0.0
                
                # Check for relevant nouns and verbs
                for noun in nouns:
                    if noun in semantic_keywords:
                        linguistic_score += 0.3
                
                for verb in verbs:
                    if verb in semantic_keywords:
                        linguistic_score += 0.2
                
                # Boost score for question patterns
                if question_words:
                    if question_type in [QuestionType.CROP_SELECTION, QuestionType.FERTILIZER_TYPE]:
                        if any(qw in ['what', 'which'] for qw in question_words):
                            linguistic_score += 0.2
                    elif question_type == QuestionType.FERTILIZER_TIMING:
                        if 'when' in question_words:
                            linguistic_score += 0.3
                    elif question_type in [QuestionType.FERTILIZER_APPLICATION, QuestionType.SOIL_FERTILITY]:
                        if 'how' in question_words:
                            linguistic_score += 0.2
                
                if linguistic_score > 0:
                    scores[question_type] = linguistic_score * 0.4  # Weight for linguistic features
            
        except Exception as e:
            self.logger.warning(f"Error in linguistic classification: {e}")
        
        return dict(scores)
    
    def _combine_classification_scores(self, *score_dicts) -> Dict[QuestionType, float]:
        """Combine scores from different classification methods."""
        combined_scores = defaultdict(float)
        
        for score_dict in score_dicts:
            for question_type, score in score_dict.items():
                combined_scores[question_type] += score
        
        return dict(combined_scores)
    
    def _calculate_enhanced_keyword_score(self, question_text: str, keywords: List[str]) -> float:
        """Enhanced keyword scoring with phrase matching and stemming."""
        score = 0.0
        
        for keyword in keywords:
            # Exact phrase match (highest score)
            if keyword in question_text:
                score += 1.0
            else:
                # Check individual words
                keyword_words = keyword.split()
                matched_words = sum(1 for word in keyword_words if word in question_text)
                
                if matched_words > 0:
                    # Partial match score based on proportion of matched words
                    score += (matched_words / len(keyword_words)) * 0.6
                
                # Stemmed matching if NLTK is available
                if NLTK_AVAILABLE and self.lemmatizer:
                    try:
                        lemmatized_keyword = ' '.join([
                            self.lemmatizer.lemmatize(word) for word in keyword_words
                        ])
                        question_tokens = word_tokenize(question_text)
                        lemmatized_question = ' '.join([
                            self.lemmatizer.lemmatize(token) for token in question_tokens
                        ])
                        
                        if lemmatized_keyword in lemmatized_question:
                            score += 0.4
                    except Exception:
                        pass  # Skip stemmed matching if it fails
        
        return score
    
    def _generate_classification_reasoning(self, top_type: QuestionType, 
                                        spacy_scores: Dict, tfidf_scores: Dict,
                                        keyword_scores: Dict, linguistic_scores: Dict) -> str:
        """Generate human-readable reasoning for the classification."""
        reasons = []
        
        if top_type in spacy_scores and spacy_scores[top_type] > 0:
            reasons.append("matched linguistic patterns")
        
        if top_type in tfidf_scores and tfidf_scores[top_type] > 0:
            reasons.append("semantic similarity to training examples")
        
        if top_type in keyword_scores and keyword_scores[top_type] > 0:
            reasons.append("relevant agricultural keywords")
        
        if top_type in linguistic_scores and linguistic_scores[top_type] > 0:
            reasons.append("question structure and grammar patterns")
        
        if not reasons:
            return f"Classified as {top_type.value} based on general context"
        
        return f"Classified as {top_type.value} based on: {', '.join(reasons)}"
    
    async def _fallback_classification(self, question_text: str) -> ClassificationResult:
        """Fallback classification using basic keyword matching."""
        question_lower = question_text.lower()
        
        # Simple keyword matching as fallback
        scores = {}
        for question_type, keywords in self.question_patterns.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > 0:
                scores[question_type] = score
        
        if not scores:
            return ClassificationResult(
                question_type=QuestionType.CROP_SELECTION,
                confidence_score=0.2,
                alternative_types=[],
                reasoning="Fallback classification - no clear matches found"
            )
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_type, top_score = sorted_scores[0]
        
        confidence = min(top_score / 5.0, 0.8)  # Lower confidence for fallback
        alternatives = [qtype for qtype, score in sorted_scores[1:3] if score > 0]
        
        return ClassificationResult(
            question_type=top_type,
            confidence_score=confidence,
            alternative_types=alternatives,
            reasoning=f"Fallback classification - matched {top_score} keywords for {top_type.value}"
        )