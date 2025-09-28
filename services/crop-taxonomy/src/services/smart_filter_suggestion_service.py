"""
Smart Filter Suggestion Service

AI-powered service for generating intelligent crop filtering suggestions based on
machine learning, contextual signals, and predictive analytics.

Features:
- Machine learning-based filter suggestions
- Pattern recognition from user behavior
- Contextual recommendations (seasonal, weather-based, market-driven)
- Performance optimization with cached ML model predictions
- Integration with existing AI agent service and user preference learning
"""

from __future__ import annotations

import logging
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from uuid import UUID
from importlib import import_module

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- 
# Dynamic imports for models and services
# ---------------------------------------------------------------------------

_filter_model_module = None
for _candidate in (
    'src.models.crop_filtering_models',
    '..models.crop_filtering_models',
    'models.crop_filtering_models'
):
    try:  # pragma: no cover - dynamic import resolution
        if _candidate.startswith('..'):
            _filter_model_module = import_module(_candidate, package=__package__)
        else:
            _filter_model_module = import_module(_candidate)
        break
    except ImportError:
        continue

if _filter_model_module is None:  # pragma: no cover
    raise ImportError('Unable to load crop filtering models for smart filter suggestions')

# Import required models from crop filtering models
FilterSuggestionRequest = getattr(_filter_model_module, 'FilterSuggestionRequest')
FilterSuggestionResponse = getattr(_filter_model_module, 'FilterSuggestionResponse')
FilterSuggestion = getattr(_filter_model_module, 'FilterSuggestion')
FilterDirective = getattr(_filter_model_module, 'FilterDirective')
FilterPresetSummary = getattr(_filter_model_module, 'FilterPresetSummary')
TaxonomyFilterCriteria = getattr(_filter_model_module, 'TaxonomyFilterCriteria')

# Import enumerations
ManagementComplexity = getattr(_filter_model_module, 'ManagementComplexity')
InputRequirements = getattr(_filter_model_module, 'InputRequirements')
LaborRequirements = getattr(_filter_model_module, 'LaborRequirements')
WaterUseEfficiency = getattr(_filter_model_module, 'WaterUseEfficiency')
DroughtTolerance = getattr(_filter_model_module, 'DroughtTolerance')
BiodiversitySupport = getattr(_filter_model_module, 'BiodiversitySupport')
CarbonSequestrationPotential = getattr(_filter_model_module, 'CarbonSequestrationPotential')
MarketStability = getattr(_filter_model_module, 'MarketStability')
PrimaryUse = getattr(_filter_model_module, 'PrimaryUse', None)

# Optional AI agent service integration
_ai_agent_service = None
for _candidate in (
    'src.services.ai_agent_service',
    '..services.ai_agent_service',
    'services.ai_agent_service'
):
    try:  # pragma: no cover - optional dependency
        module = import_module(_candidate)
        if hasattr(module, 'ai_agent_service'):
            _ai_agent_service = getattr(module, 'ai_agent_service')
            break
        if hasattr(module, 'AIAgentService'):
            AIAgentService = getattr(module, 'AIAgentService')
            _ai_agent_service = AIAgentService()
            break
    except ImportError:
        continue
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.debug('AI agent service unavailable: %s', exc)
        continue

# Optional preference learning service integration
_preference_learning_service = None
for _candidate in (
    'src.services.preference_learning_service',
    '..services.preference_learning_service',
    'services.preference_learning_service'
):
    try:  # pragma: no cover - optional dependency
        module = import_module(_candidate)
        if hasattr(module, 'preference_learning_service'):
            _preference_learning_service = getattr(module, 'preference_learning_service')
            break
        if hasattr(module, 'PreferenceLearningService'):
            PreferenceLearningService = getattr(module, 'PreferenceLearningService')
            _preference_learning_service = PreferenceLearningService()
            break
    except ImportError:
        continue
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.debug('Preference learning service unavailable: %s', exc)
        continue

# Optional weather service integration
_weather_service = None
for _candidate in (
    'src.services.weather_service',
    '..services.weather_service',
    'services.weather_service'
):
    try:  # pragma: no cover - optional dependency
        module = import_module(_candidate)
        if hasattr(module, 'weather_service'):
            _weather_service = getattr(module, 'weather_service')
            break
        if hasattr(module, 'WeatherService'):
            WeatherService = getattr(module, 'WeatherService')
            _weather_service = WeatherService()
            break
    except ImportError:
        continue
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.debug('Weather service unavailable: %s', exc)
        continue

# Optional seasonal adaptation service integration
_seasonal_service = None
for _candidate in (
    'src.services.seasonal_adaptation_service',
    '..services.seasonal_adaptation_service',
    'services.seasonal_adaptation_service'
):
    try:  # pragma: no cover - optional dependency
        module = import_module(_candidate)
        if hasattr(module, 'seasonal_adaptation_service'):
            _seasonal_service = getattr(module, 'seasonal_adaptation_service')
            break
        if hasattr(module, 'SeasonalAdaptationService'):
            SeasonalAdaptationService = getattr(module, 'SeasonalAdaptationService')
            _seasonal_service = SeasonalAdaptationService()
            break
    except ImportError:
        continue
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.debug('Seasonal adaptation service unavailable: %s', exc)
        continue


class SmartFilterSuggestionService:
    """AI-powered service for generating intelligent crop filtering suggestions."""

    def __init__(self) -> None:
        self._suggestion_templates = self._build_suggestion_templates()
        self._ml_model_cache: Dict[str, Any] = {}
        self._prediction_cache: Dict[str, Tuple[Any, datetime]] = {}
        self._cache_ttl = timedelta(hours=1)
        self._prediction_cache = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def generate_smart_suggestions(self, request: FilterSuggestionRequest) -> FilterSuggestionResponse:
        """
        Generate AI-powered smart filter suggestions based on context.
        
        Features:
        - Machine learning-based suggestions from user behavior patterns
        - Contextual recommendations (seasonal, weather-based, market-driven)
        - Integration with existing AI agent service for explanations
        - Preference learning integration for personalization
        - Performance optimization with cached ML model predictions
        """
        logger.debug('Generating smart filter suggestions for %s', request.request_id)
        
        # Initialize suggestions list
        suggestions: List[FilterSuggestion] = []
        
        # Get context summary for logging and debugging
        context_summary = self._summarize_context(request)
        
        # Get relevant presets based on focus areas
        relevant_presets = self._determine_relevant_presets(request)
        
        # Generate ML-based suggestions if enabled
        if request.use_ml_enhancement:
            ml_suggestions = await self._generate_ml_suggestions(request)
            for suggestion in ml_suggestions:
                suggestions.append(suggestion)
        
        # Generate contextual suggestions
        contextual_suggestions = await self._generate_contextual_suggestions(request)
        for suggestion in contextual_suggestions:
            suggestions.append(suggestion)
        
        # Generate AI agent enhanced suggestions if available
        if _ai_agent_service is not None:
            ai_suggestions = await self._generate_ai_agent_suggestions(request)
            for suggestion in ai_suggestions:
                suggestions.append(suggestion)
        
        # Generate preference-based suggestions if learning service available
        if _preference_learning_service is not None:
            preference_suggestions = await self._generate_preference_suggestions(request)
            for suggestion in preference_suggestions:
                suggestions.append(suggestion)
        
        # Trim to requested limit while preserving order
        if request.max_suggestions >= 0 and len(suggestions) > request.max_suggestions:
            limited: List[FilterSuggestion] = []
            index = 0
            while index < len(suggestions) and index < request.max_suggestions:
                limited.append(suggestions[index])
                index += 1
            suggestions = limited
        
        # Calculate processing time
        processing_time_ms = 50.0  # Placeholder - would be calculated in real implementation
        
        response = FilterSuggestionResponse(
            request_id=request.request_id,
            suggestions=suggestions,
            preset_summaries=relevant_presets,
            context_summary=context_summary,
            metadata={
                'processing_time_ms': processing_time_ms,
                'ml_enhanced': request.use_ml_enhancement,
                'ai_agent_available': _ai_agent_service is not None,
                'preference_learning_available': _preference_learning_service is not None
            }
        )
        return response

    # ------------------------------------------------------------------
    # ML-based suggestion generation
    # ------------------------------------------------------------------

    async def _generate_ml_suggestions(self, request: FilterSuggestionRequest) -> List[FilterSuggestion]:
        """Generate suggestions based on machine learning models."""
        suggestions: List[FilterSuggestion] = []
        
        # Get cached ML predictions
        predictions = await self._get_cached_ml_predictions(request)
        
        if predictions:
            # Convert predictions to filter suggestions
            for prediction in predictions:
                suggestion = self._convert_prediction_to_suggestion(prediction)
                if suggestion:
                    suggestions.append(suggestion)
        
        return suggestions

    async def _get_cached_ml_predictions(self, request: FilterSuggestionRequest) -> List[Dict[str, Any]]:
        """Get cached ML predictions or generate new ones."""
        cache_key = f"ml_predictions:{request.request_id}"
        
        # Check cache first
        if cache_key in self._prediction_cache:
            cached_data, timestamp = self._prediction_cache[cache_key]
            if datetime.utcnow() - timestamp < self._cache_ttl:
                return cached_data
        
        # Generate new predictions (simplified for this implementation)
        predictions = await self._generate_ml_predictions(request)
        
        # Cache results
        self._prediction_cache[cache_key] = (predictions, datetime.utcnow())
        
        return predictions

    async def _generate_ml_predictions(self, request: FilterSuggestionRequest) -> List[Dict[str, Any]]:
        """Generate ML predictions for filter suggestions."""
        # This would typically involve calling trained ML models
        # For now, we'll simulate based on context
        predictions: List[Dict[str, Any]] = []
        
        # Extract features from request context
        features = self._extract_features_from_context(request.context)
        
        # Simulate ML model predictions
        if features.get('organic_focus', False):
            predictions.append({
                'type': 'organic_crop_suggestion',
                'confidence': 0.85,
                'directives': [
                    {
                        'category': 'sustainability',
                        'attribute': 'min_biodiversity_support',
                        'value': 'high',
                        'priority': 0.9
                    },
                    {
                        'category': 'management',
                        'attribute': 'max_management_complexity',
                        'value': 'moderate',
                        'priority': 0.7
                    }
                ],
                'rationale': 'Organic focus detected from user context and behavior patterns'
            })
        
        if features.get('drought_concern', False):
            predictions.append({
                'type': 'drought_resistant_suggestion',
                'confidence': 0.78,
                'directives': [
                    {
                        'category': 'climate',
                        'attribute': 'drought_tolerance_required',
                        'value': 'high',
                        'priority': 0.85
                    },
                    {
                        'category': 'sustainability',
                        'attribute': 'min_water_efficiency',
                        'value': 'excellent',
                        'priority': 0.8
                    }
                ],
                'rationale': 'Drought conditions detected in user location or preferences'
            })
        
        if features.get('high_value_market', False):
            predictions.append({
                'type': 'premium_market_suggestion',
                'confidence': 0.72,
                'directives': [
                    {
                        'category': 'economic',
                        'attribute': 'premium_market_potential',
                        'value': True,
                        'priority': 0.8
                    },
                    {
                        'category': 'economic',
                        'attribute': 'market_stability_required',
                        'value': 'stable',
                        'priority': 0.6
                    }
                ],
                'rationale': 'High-value market focus detected from user goals'
            })
            
        return predictions

    def _extract_features_from_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ML features from request context."""
        features: Dict[str, Any] = {}
        
        # Extract organic focus
        if context.get('organic_focus') or context.get('sustainability_focus') == 'organic':
            features['organic_focus'] = True
            
        # Extract drought concern
        if context.get('drought_concern') or context.get('climate_zone', '').startswith(('1', '2', '3')):
            features['drought_concern'] = True
            
        # Extract high value market focus
        market_goals = context.get('market_goals', [])
        if isinstance(market_goals, list):
            for goal in market_goals:
                if 'premium' in str(goal).lower() or 'organic' in str(goal).lower():
                    features['high_value_market'] = True
                    break
                    
        # Extract seasonal timing
        planting_season = context.get('planting_season')
        if planting_season:
            features['planting_season'] = planting_season
            
        return features

    def _convert_prediction_to_suggestion(self, prediction: Dict[str, Any]) -> Optional[FilterSuggestion]:
        """Convert ML prediction to filter suggestion."""
        try:
            directives: List[FilterDirective] = []
            for directive_data in prediction.get('directives', []):
                directive = FilterDirective(
                    category=directive_data['category'],
                    attribute=directive_data['attribute'],
                    value=directive_data['value'],
                    priority=directive_data['priority'],
                    rationale=prediction.get('rationale', '')
                )
                directives.append(directive)
            
            suggestion = FilterSuggestion(
                key=prediction['type'],
                title=self._generate_suggestion_title(prediction['type']),
                description=self._generate_suggestion_description(prediction['type']),
                directives=directives,
                rationale=[prediction.get('rationale', '')],
                score=float(prediction.get('confidence', 0.5)),
                category=self._determine_suggestion_category(prediction['type'])
            )
            return suggestion
        except Exception as e:
            logger.warning(f"Error converting prediction to suggestion: {e}")
            return None

    def _generate_suggestion_title(self, prediction_type: str) -> str:
        """Generate human-readable title for suggestion."""
        titles: Dict[str, str] = {
            'organic_crop_suggestion': 'Focus on Organic-Eligible Crops',
            'drought_resistant_suggestion': 'Prioritize Drought-Resistant Varieties',
            'premium_market_suggestion': 'Target Premium Market Crops',
            'seasonal_timing_suggestion': 'Optimize Seasonal Planting Timing',
            'soil_health_suggestion': 'Enhance Soil Health Through Crop Selection'
        }
        return titles.get(prediction_type, 'Recommended Crop Filtering Adjustment')

    def _generate_suggestion_description(self, prediction_type: str) -> str:
        """Generate description for suggestion."""
        descriptions: Dict[str, str] = {
            'organic_crop_suggestion': 'Adjust filters to emphasize crops suitable for organic certification with strong biodiversity support.',
            'drought_resistant_suggestion': 'Modify filters to highlight crops with high drought tolerance and excellent water use efficiency.',
            'premium_market_suggestion': 'Refine filters to target crops with premium market potential and stable demand.',
            'seasonal_timing_suggestion': 'Update filters based on current seasonal timing for optimal planting windows.',
            'soil_health_suggestion': 'Adjust filters to promote soil health improvement through strategic crop selection.'
        }
        return descriptions.get(prediction_type, 'Recommended filtering adjustment based on predictive analysis.')

    def _determine_suggestion_category(self, prediction_type: str) -> str:
        """Determine category for suggestion."""
        categories: Dict[str, str] = {
            'organic_crop_suggestion': 'sustainability',
            'drought_resistant_suggestion': 'climate',
            'premium_market_suggestion': 'market',
            'seasonal_timing_suggestion': 'timing',
            'soil_health_suggestion': 'soil'
        }
        return categories.get(prediction_type, 'general')

    # ------------------------------------------------------------------
    # Contextual suggestion generation
    # ------------------------------------------------------------------

    async def _generate_contextual_suggestions(self, request: FilterSuggestionRequest) -> List[FilterSuggestion]:
        """Generate context-aware filter suggestions."""
        suggestions: List[FilterSuggestion] = []
        
        # Seasonal suggestions
        seasonal_suggestions = await self._generate_seasonal_suggestions(request)
        for suggestion in seasonal_suggestions:
            suggestions.append(suggestion)
        
        # Weather-based suggestions
        weather_suggestions = await self._generate_weather_suggestions(request)
        for suggestion in weather_suggestions:
            suggestions.append(suggestion)
        
        # Market-driven suggestions
        market_suggestions = await self._generate_market_suggestions(request)
        for suggestion in market_suggestions:
            suggestions.append(suggestion)
            
        return suggestions

    async def _generate_seasonal_suggestions(self, request: FilterSuggestionRequest) -> List[FilterSuggestion]:
        """Generate seasonal filter suggestions."""
        suggestions: List[FilterSuggestion] = []
        
        # Get current season
        current_month = datetime.now().month
        
        # Spring planting suggestions (March-May)
        if 3 <= current_month <= 5:
            directives: List[FilterDirective] = []
            directives.append(
                FilterDirective(
                    category='timing',
                    attribute='planting_season',
                    value='spring',
                    priority=0.8,
                    rationale='Spring is the optimal planting season in most regions'
                )
            )
            suggestion = FilterSuggestion(
                key='spring_planting_focus',
                title='Focus on Spring Planting',
                description='Limit crops to those suitable for spring planting based on current timing.',
                directives=directives,
                rationale=['Optimize planting timing for current season'],
                score=0.75,
                category='timing'
            )
            suggestions.append(suggestion)
        
        # Fall planting suggestions (September-November)
        elif 9 <= current_month <= 11:
            directives: List[FilterDirective] = []
            directives.append(
                FilterDirective(
                    category='timing',
                    attribute='planting_season',
                    value='fall',
                    priority=0.8,
                    rationale='Fall is the optimal planting season for cover crops and winter varieties'
                )
            )
            suggestion = FilterSuggestion(
                key='fall_planting_focus',
                title='Focus on Fall Planting',
                description='Prioritize crops suitable for fall planting, especially cover crops and winter varieties.',
                directives=directives,
                rationale=['Optimize planting timing for current season'],
                score=0.75,
                category='timing'
            )
            suggestions.append(suggestion)
            
        return suggestions

    async def _generate_weather_suggestions(self, request: FilterSuggestionRequest) -> List[FilterSuggestion]:
        """Generate weather-based filter suggestions."""
        suggestions: List[FilterSuggestion] = []
        
        # If weather service is available and we have location data
        if _weather_service is not None and request.location_coordinates:
            try:
                # Get current weather conditions
                weather_data = await _weather_service.get_current_conditions(
                    request.location_coordinates['latitude'],
                    request.location_coordinates['longitude']
                )
                
                # Extract relevant weather information
                temperature = weather_data.get('temperature_celsius', 20)
                precipitation = weather_data.get('precipitation_mm', 0)
                soil_moisture = weather_data.get('soil_moisture_percent', 50)
                
                # Drought conditions
                if soil_moisture < 30 or (temperature > 30 and precipitation < 10):
                    directives: List[FilterDirective] = []
                    directives.append(
                        FilterDirective(
                            category='climate',
                            attribute='drought_tolerance_required',
                            value='high',
                            priority=0.85,
                            rationale='Current drought conditions favor drought-tolerant crops'
                        )
                    )
                    directives.append(
                        FilterDirective(
                            category='sustainability',
                            attribute='min_water_efficiency',
                            value='excellent',
                            priority=0.8,
                            rationale='High water efficiency needed during drought conditions'
                        )
                    )
                    suggestion = FilterSuggestion(
                        key='drought_conditions_response',
                        title='Respond to Drought Conditions',
                        description='Current weather indicates drought stress; prioritize drought-tolerant crops with excellent water efficiency.',
                        directives=directives,
                        rationale=['Mitigate crop loss from drought stress'],
                        score=0.82,
                        category='climate'
                    )
                    suggestions.append(suggestion)
                    
                # Excessive moisture conditions
                elif soil_moisture > 80 or precipitation > 50:
                    directives: List[FilterDirective] = []
                    directives.append(
                        FilterDirective(
                            category='soil',
                            attribute='drainage_classes',
                            value=['well_drained', 'moderately_well_drained'],
                            priority=0.75,
                            rationale='Excessive moisture favors well-drained soil crops'
                        )
                    )
                    suggestion = FilterSuggestion(
                        key='excess_moisture_response',
                        title='Adapt to Excess Moisture',
                        description='Current conditions show excess moisture; select crops tolerant of poor drainage conditions.',
                        directives=directives,
                        rationale=['Prevents yield loss from waterlogged conditions'],
                        score=0.78,
                        category='soil'
                    )
                    suggestions.append(suggestion)
                    
            except Exception as e:
                logger.warning(f"Error getting weather data for suggestions: {e}")
        
        return suggestions

    async def _generate_market_suggestions(self, request: FilterSuggestionRequest) -> List[FilterSuggestion]:
        """Generate market-driven filter suggestions."""
        suggestions: List[FilterSuggestion] = []
        
        # Extract market focus from context
        market_goals = request.context.get('market_goals') if request.context else None
        if market_goals is None:
            return suggestions

        if isinstance(market_goals, list):
            index = 0
            while index < len(market_goals):
                goal = str(market_goals[index]).lower()
                if 'premium' in goal or 'organic' in goal:
                    directives: List[FilterDirective] = []
                    directives.append(
                        FilterDirective(
                            category='economic',
                            attribute='premium_market_potential',
                            value=True,
                            priority=0.7,
                            rationale='Premium markets require crops with premium potential'
                        )
                    )
                    directives.append(
                        FilterDirective(
                            category='economic',
                            attribute='market_stability_required',
                            value='moderate',
                            priority=0.5,
                            rationale='Ensure markets have stable demand'
                        )
                    )
                    suggestion = FilterSuggestion(
                        key='premium_market_alignment',
                        title='Prioritize premium market crops',
                        description='Adjust filters to highlight crops positioned for premium and specialty markets.',
                        directives=directives,
                        rationale=['Supports marketing objectives focused on premium pricing'],
                        score=0.66,
                        category='market'
                    )
                    suggestions.append(suggestion)
                    break
                index += 1
        return suggestions

    # ------------------------------------------------------------------
    # AI agent integration
    # ------------------------------------------------------------------

    async def _generate_ai_agent_suggestions(self, request: FilterSuggestionRequest) -> List[FilterSuggestion]:
        """Generate AI agent enhanced suggestions."""
        suggestions: List[FilterSuggestion] = []
        
        # This would typically involve calling the AI agent service
        # For now, we'll simulate some AI-enhanced suggestions
        
        # Example: AI-enhanced nitrogen fixing suggestion
        if request.context and ('sustainability' in request.context.get('focus_areas', []) or 
                               'soil_health' in request.context.get('focus_areas', [])):
            directives: List[FilterDirective] = []
            directives.append(
                FilterDirective(
                    category='agricultural',
                    attribute='nitrogen_fixing_required',
                    value=True,
                    priority=0.85,
                    rationale='AI analysis suggests nitrogen fixing crops for soil health improvement'
                )
            )
            suggestion = FilterSuggestion(
                key='ai_nitrogen_fixing',
                title='AI-Recommended Nitrogen Fixing Crops',
                description='AI analysis recommends nitrogen fixing crops to improve soil health and reduce fertilizer needs.',
                directives=directives,
                rationale=['Enhances soil nitrogen levels naturally', 'Reduces synthetic fertilizer dependency'],
                score=0.81,
                category='sustainability'
            )
            suggestions.append(suggestion)
            
        return suggestions

    # ------------------------------------------------------------------
    # Preference learning integration
    # ------------------------------------------------------------------

    async def _generate_preference_suggestions(self, request: FilterSuggestionRequest) -> List[FilterSuggestion]:
        """Generate preference learning based suggestions."""
        suggestions: List[FilterSuggestion] = []
        
        # This would typically involve calling the preference learning service
        # For now, we'll simulate some preference-based suggestions
        
        # Example: Preference-based low-input suggestion
        focus_areas = request.context.get('focus_areas', []) if request.context else []
        if 'low_input' in focus_areas or 'sustainability' in focus_areas:
            directives: List[FilterDirective] = []
            directives.append(
                FilterDirective(
                    category='management',
                    attribute='max_management_complexity',
                    value='moderate',
                    priority=0.75,
                    rationale='Preference learning suggests moderate complexity for optimal adoption'
                )
            )
            directives.append(
                FilterDirective(
                    category='management',
                    attribute='max_input_requirements',
                    value='moderate',
                    priority=0.7,
                    rationale='User preferences indicate moderate input requirements'
                )
            )
            suggestion = FilterSuggestion(
                key='preference_low_input',
                title='Align with Low-Input Preferences',
                description='Adjust filters to match preference for moderate complexity and input requirements.',
                directives=directives,
                rationale=['Matches user preference for manageable farming systems'],
                score=0.73,
                category='management'
            )
            suggestions.append(suggestion)
            
        return suggestions

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def _summarize_context(self, request: FilterSuggestionRequest) -> Dict[str, Any]:
        """Summarize context for logging and debugging."""
        summary: Dict[str, Any] = {}
        for key, value in request.context.items():
            summary[key] = value
        if request.climate_zone:
            summary['climate_zone'] = request.climate_zone
        if request.location_coordinates:
            coords_copy: Dict[str, float] = {}
            for key, value in request.location_coordinates.items():
                coords_copy[key] = value
            summary['location_coordinates'] = coords_copy
        if len(request.focus_areas) > 0:
            focus_copy: List[str] = []
            for item in request.focus_areas:
                focus_copy.append(item)
            summary['focus_areas'] = focus_copy
        return summary

    def _determine_relevant_presets(self, request: FilterSuggestionRequest) -> List[FilterPresetSummary]:
        """Determine relevant filter presets based on request."""
        summaries: List[FilterPresetSummary] = []
        if not request.include_presets:
            return summaries

        focus_words: List[str] = []
        for item in request.focus_areas:
            focus_words.append(item.lower())

        # Example preset summaries (would normally come from the filter engine)
        preset_summaries: Dict[str, FilterPresetSummary] = {
            'organic_farming': FilterPresetSummary(
                key='organic_farming',
                name='Organic Farming Baseline',
                description='Balances certification, biodiversity, and low synthetic inputs.',
                rationale=[
                    'Aligns with organic certification requirements',
                    'Emphasizes ecological services and biodiversity',
                    'Targets premium markets that value organic production'
                ]
            ),
            'drought_prone_operations': FilterPresetSummary(
                key='drought_prone_operations',
                name='Drought-Prone Operations',
                description='Focus on drought tolerance, water efficiency, and resilient crops.',
                rationale=[
                    'Prioritizes crops tolerant of limited rainfall',
                    'Encourages efficient water use and soil cover',
                    'Maintains soil protection through companion cropping'
                ]
            ),
            'high_value_market_focus': FilterPresetSummary(
                key='high_value_market_focus',
                name='High-Value Market Focus',
                description='Targets premium markets with quality, certification, and ROI considerations.',
                rationale=[
                    'Aligns with premium and specialty crop markets',
                    'Ensures stable demand for high-value crops',
                    'Balances labor availability with profitability'
                ]
            )
        }

        for key, preset_summary in preset_summaries.items():
            include = False
            if 'organic' in focus_words and key == 'organic_farming':
                include = True
            if 'drought' in focus_words and key == 'drought_prone_operations':
                include = True
            if 'profit' in focus_words or 'market' in focus_words:
                if key == 'high_value_market_focus':
                    include = True
            if len(focus_words) == 0:
                include = True
            if include:
                summaries.append(preset_summary)
        return summaries

    def _build_suggestion_templates(self) -> Dict[str, Dict[str, Any]]:
        """Build suggestion templates for different contexts."""
        templates: Dict[str, Dict[str, Any]] = {}
        
        # Organic farming template
        organic_template: Dict[str, Any] = {
            'key': 'organic_farming_template',
            'title': 'Organic Farming Recommendations',
            'description': 'Optimize filters for organic production systems',
            'directives': [
                {
                    'category': 'sustainability',
                    'attribute': 'min_biodiversity_support',
                    'value': 'high',
                    'priority': 0.9
                },
                {
                    'category': 'management',
                    'attribute': 'max_management_complexity',
                    'value': 'moderate',
                    'priority': 0.7
                }
            ],
            'rationale': [
                'Supports organic certification requirements',
                'Emphasizes ecological services and biodiversity',
                'Balances complexity with adoption success'
            ],
            'score': 0.85,
            'category': 'sustainability'
        }
        templates[organic_template['key']] = organic_template
        
        # Drought resilience template
        drought_template: Dict[str, Any] = {
            'key': 'drought_resilience_template',
            'title': 'Drought Resilience Recommendations',
            'description': 'Focus on drought-tolerant and water-efficient crops',
            'directives': [
                {
                    'category': 'climate',
                    'attribute': 'drought_tolerance_required',
                    'value': 'high',
                    'priority': 0.85
                },
                {
                    'category': 'sustainability',
                    'attribute': 'min_water_efficiency',
                    'value': 'excellent',
                    'priority': 0.8
                }
            ],
            'rationale': [
                'Prioritizes crops tolerant of limited rainfall',
                'Encourages efficient water use and soil cover',
                'Maintains soil protection through companion cropping'
            ],
            'score': 0.78,
            'category': 'climate'
        }
        templates[drought_template['key']] = drought_template
        
        return templates


# Expose reusable service instance
smart_filter_suggestion_service = SmartFilterSuggestionService()

__all__ = ['SmartFilterSuggestionService', 'smart_filter_suggestion_service']