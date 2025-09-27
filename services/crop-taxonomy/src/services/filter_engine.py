"""Filter combination and suggestion engine for crop taxonomy filtering."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from importlib import import_module

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dynamic imports for models and enumerations
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
    raise ImportError('Unable to load crop filtering models for filter engine')

TaxonomyFilterCriteria = getattr(_filter_model_module, 'TaxonomyFilterCriteria')
ClimateFilter = getattr(_filter_model_module, 'ClimateFilter')
SoilFilter = getattr(_filter_model_module, 'SoilFilter')
AgriculturalFilter = getattr(_filter_model_module, 'AgriculturalFilter')
ManagementFilter = getattr(_filter_model_module, 'ManagementFilter')
SustainabilityFilter = getattr(_filter_model_module, 'SustainabilityFilter')
EconomicFilter = getattr(_filter_model_module, 'EconomicFilter')
FilterDirective = getattr(_filter_model_module, 'FilterDirective')
FilterCombinationRequest = getattr(_filter_model_module, 'FilterCombinationRequest')
FilterCombinationResponse = getattr(_filter_model_module, 'FilterCombinationResponse')
FilterSuggestionRequest = getattr(_filter_model_module, 'FilterSuggestionRequest')
FilterSuggestionResponse = getattr(_filter_model_module, 'FilterSuggestionResponse')
FilterSuggestion = getattr(_filter_model_module, 'FilterSuggestion')
FilterPresetSummary = getattr(_filter_model_module, 'FilterPresetSummary')

ManagementComplexity = getattr(_filter_model_module, 'ManagementComplexity')
InputRequirements = getattr(_filter_model_module, 'InputRequirements')
LaborRequirements = getattr(_filter_model_module, 'LaborRequirements')
WaterUseEfficiency = getattr(_filter_model_module, 'WaterUseEfficiency')
DroughtTolerance = getattr(_filter_model_module, 'DroughtTolerance')
BiodiversitySupport = getattr(_filter_model_module, 'BiodiversitySupport')
CarbonSequestrationPotential = getattr(_filter_model_module, 'CarbonSequestrationPotential')
MarketStability = getattr(_filter_model_module, 'MarketStability')
PrimaryUse = getattr(_filter_model_module, 'PrimaryUse', None)

# Optional regional service integration
_regional_service = None
for _candidate in (
    'src.services.regional_adaptation_service',
    '..services.regional_adaptation_service',
    'services.regional_adaptation_service'
):
    try:  # pragma: no cover - optional dependency
        module = import_module(_candidate)
        if hasattr(module, 'regional_adaptation_service'):
            _regional_service = getattr(module, 'regional_adaptation_service')
            break
        if hasattr(module, 'RegionalAdaptationService'):
            RegionalAdaptationService = getattr(module, 'RegionalAdaptationService')
            _regional_service = RegionalAdaptationService()
            break
    except ImportError:
        continue
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.debug('Regional adaptation service unavailable: %s', exc)
        continue


class FilterCombinationEngine:
    """Applies dynamic combinations of crop filtering criteria with guidance."""

    def __init__(self) -> None:
        self._presets = self._build_presets()
        self._dependency_rules = self._build_dependency_rules()
        self._conflict_rules = self._build_conflict_rules()
        self._water_efficiency_rank = self._build_water_efficiency_rank()
        self._drought_rank = self._build_drought_rank()
        self._input_rank = self._build_input_rank()
        self._management_rank = self._build_management_rank()
        self._market_rank = self._build_market_rank()
        self._preset_summaries = self._prepare_preset_summaries()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def combine_filters(self, request: FilterCombinationRequest) -> FilterCombinationResponse:
        """Combine base criteria, directives, and presets into final criteria."""
        logger.debug('Combining filters for request %s', request.request_id)
        base_criteria = self._clone_criteria(request.base_criteria)
        applied_presets: List[str] = []
        dependency_notes: List[str] = []
        conflict_messages: List[str] = []
        warnings: List[str] = []
        suggested_directives: List[FilterDirective] = []

        for preset_key in request.preset_keys:
            preset = self._presets.get(preset_key)
            if preset is None:
                warning_text = f"Unknown preset '{preset_key}' skipped"
                warnings.append(warning_text)
                logger.debug(warning_text)
                continue
            self._apply_preset(base_criteria, preset)
            applied_presets.append(preset_key)

        for directive in request.directives:
            self._apply_directive(base_criteria, directive, warnings)

        for rule in self._dependency_rules:
            rule_notes = rule(base_criteria)
            if len(rule_notes) > 0:
                for note in rule_notes:
                    dependency_notes.append(note)

        for conflict_rule in self._conflict_rules:
            messages = conflict_rule(base_criteria)
            if len(messages) > 0:
                for message in messages:
                    conflict_messages.append(message)

        if request.include_suggestions:
            suggested_directives = self._generate_follow_up_suggestions(base_criteria, conflict_messages)

        metadata: Dict[str, Any] = {}
        if len(request.context) > 0:
            context_copy: Dict[str, Any] = {}
            for key, value in request.context.items():
                context_copy[key] = value
            metadata['context'] = context_copy
        if len(applied_presets) > 0:
            metadata['preset_details'] = self._collect_preset_metadata(applied_presets)

        response = FilterCombinationResponse(
            request_id=request.request_id,
            combined_criteria=base_criteria,
            applied_presets=applied_presets,
            dependency_notes=dependency_notes,
            conflicts=conflict_messages,
            warnings=warnings,
            suggested_directives=suggested_directives,
            metadata=metadata
        )
        return response

    def suggest_filters(self, request: FilterSuggestionRequest) -> FilterSuggestionResponse:
        """Generate intelligent filter suggestions based on context."""
        logger.debug('Generating filter suggestions for %s', request.request_id)
        suggestions: List[FilterSuggestion] = []
        context_summary = self._summarize_context(request)
        relevant_presets = self._determine_relevant_presets(request)

        climate_suggestions = self._suggest_from_climate(request)
        for suggestion in climate_suggestions:
            suggestions.append(suggestion)

        soil_suggestions = self._suggest_from_soil(request)
        for suggestion in soil_suggestions:
            suggestions.append(suggestion)

        market_suggestions = self._suggest_from_market(request)
        for suggestion in market_suggestions:
            suggestions.append(suggestion)

        sustainability_suggestions = self._suggest_from_sustainability(request)
        for suggestion in sustainability_suggestions:
            suggestions.append(suggestion)

        # Trim to requested limit while preserving order
        if request.max_suggestions >= 0 and len(suggestions) > request.max_suggestions:
            limited: List[FilterSuggestion] = []
            index = 0
            while index < len(suggestions) and index < request.max_suggestions:
                limited.append(suggestions[index])
                index += 1
            suggestions = limited

        response = FilterSuggestionResponse(
            request_id=request.request_id,
            suggestions=suggestions,
            preset_summaries=relevant_presets,
            context_summary=context_summary,
            metadata={}
        )
        return response

    # ------------------------------------------------------------------
    # Preset construction
    # ------------------------------------------------------------------

    def _build_presets(self) -> Dict[str, Dict[str, Any]]:
        presets: Dict[str, Dict[str, Any]] = {}

        organic_preset: Dict[str, Any] = {
            'key': 'organic_farming',
            'name': 'Organic Farming Baseline',
            'description': 'Balances certification, biodiversity, and low synthetic inputs.',
            'updates': {
                'management_filter': {
                    'max_management_complexity': ManagementComplexity.MODERATE,
                    'max_input_requirements': InputRequirements.MODERATE,
                    'low_tech_suitable': True
                },
                'sustainability_filter': {
                    'min_biodiversity_support': BiodiversitySupport.HIGH,
                    'min_water_efficiency': WaterUseEfficiency.GOOD,
                    'min_carbon_sequestration': CarbonSequestrationPotential.MODERATE
                },
                'economic_filter': {
                    'premium_market_potential': True,
                    'market_stability_required': MarketStability.MODERATE
                }
            },
            'rationale': [
                'Aligns with organic certification requirements',
                'Emphasizes ecological services and biodiversity',
                'Targets premium markets that value organic production'
            ]
        }
        presets[organic_preset['key']] = organic_preset

        drought_preset: Dict[str, Any] = {
            'key': 'drought_prone_operations',
            'name': 'Drought-Prone Operations',
            'description': 'Focus on drought tolerance, water efficiency, and resilient crops.',
            'updates': {
                'climate_filter': {
                    'drought_tolerance_required': DroughtTolerance.HIGH
                },
                'sustainability_filter': {
                    'min_water_efficiency': WaterUseEfficiency.EXCELLENT
                },
                'agricultural_filter': {
                    'companion_crop_suitable': True
                }
            },
            'rationale': [
                'Prioritizes crops tolerant of limited rainfall',
                'Encourages efficient water use and soil cover',
                'Maintains soil protection through companion cropping'
            ]
        }
        presets[drought_preset['key']] = drought_preset

        high_value_preset: Dict[str, Any] = {
            'key': 'high_value_market_focus',
            'name': 'High-Value Market Focus',
            'description': 'Targets premium markets with quality, certification, and ROI considerations.',
            'updates': {
                'economic_filter': {
                    'premium_market_potential': True,
                    'high_roi_potential': True,
                    'market_stability_required': MarketStability.STABLE
                },
                'agricultural_filter': {
                    'primary_uses': [PrimaryUse.FOOD_HUMAN] if PrimaryUse is not None else []
                },
                'management_filter': {
                    'max_labor_requirements': LaborRequirements.MODERATE
                }
            },
            'rationale': [
                'Aligns with premium and specialty crop markets',
                'Ensures stable demand for high-value crops',
                'Balances labor availability with profitability'
            ]
        }
        presets[high_value_preset['key']] = high_value_preset

        return presets

    def _prepare_preset_summaries(self) -> Dict[str, FilterPresetSummary]:
        summaries: Dict[str, FilterPresetSummary] = {}
        for key, preset in self._presets.items():
            rationale_list: List[str] = []
            if 'rationale' in preset:
                for item in preset['rationale']:
                    rationale_list.append(item)
            summary = FilterPresetSummary(
                key=key,
                name=preset['name'],
                description=preset['description'],
                rationale=rationale_list
            )
            summaries[key] = summary
        return summaries

    # ------------------------------------------------------------------
    # Dependency and conflict rules
    # ------------------------------------------------------------------

    def _build_dependency_rules(self) -> List[Callable[[TaxonomyFilterCriteria], List[str]]]:
        rules: List[Callable[[TaxonomyFilterCriteria], List[str]]] = []

        def enforce_water_efficiency(criteria: TaxonomyFilterCriteria) -> List[str]:
            notes: List[str] = []
            climate_filter = criteria.climate_filter
            sustainability_filter = criteria.sustainability_filter
            if climate_filter is not None and sustainability_filter is not None:
                drought_requirement = climate_filter.drought_tolerance_required
                if drought_requirement is not None:
                    desired_efficiency = WaterUseEfficiency.GOOD
                    if drought_requirement == DroughtTolerance.HIGH:
                        desired_efficiency = WaterUseEfficiency.EXCELLENT
                    current_efficiency = sustainability_filter.min_water_efficiency
                    if current_efficiency is None or self._water_efficiency_rank.get(current_efficiency, 0) < self._water_efficiency_rank.get(desired_efficiency, 0):
                        sustainability_filter.min_water_efficiency = desired_efficiency
                        note_text = 'Adjusted water use efficiency to support drought tolerance requirements'
                        notes.append(note_text)
            return notes

        rules.append(enforce_water_efficiency)

        def enforce_market_stability(criteria: TaxonomyFilterCriteria) -> List[str]:
            notes: List[str] = []
            economic_filter = criteria.economic_filter
            if economic_filter is not None and economic_filter.high_roi_potential:
                current_stability = economic_filter.market_stability_required
                minimum = MarketStability.MODERATE
                if current_stability is None or self._market_rank.get(current_stability, 0) < self._market_rank.get(minimum, 0):
                    economic_filter.market_stability_required = minimum
                    note_text = 'Raised market stability requirement to support high ROI targeting'
                    notes.append(note_text)
            return notes

        rules.append(enforce_market_stability)

        def balance_management_complexity(criteria: TaxonomyFilterCriteria) -> List[str]:
            notes: List[str] = []
            management_filter = criteria.management_filter
            if management_filter is not None:
                complexity = management_filter.max_management_complexity
                input_requirement = management_filter.max_input_requirements
                if complexity is not None and input_requirement is not None:
                    if self._management_rank.get(complexity, 0) < self._input_rank.get(input_requirement, 0):
                        management_filter.max_input_requirements = InputRequirements.MODERATE
                        note_text = 'Normalized input requirements to align with management complexity constraints'
                        notes.append(note_text)
            return notes

        rules.append(balance_management_complexity)

        return rules

    def _build_conflict_rules(self) -> List[Callable[[TaxonomyFilterCriteria], List[str]]]:
        rules: List[Callable[[TaxonomyFilterCriteria], List[str]]] = []

        def drought_vs_water(criteria: TaxonomyFilterCriteria) -> List[str]:
            messages: List[str] = []
            climate_filter = criteria.climate_filter
            sustainability_filter = criteria.sustainability_filter
            if climate_filter is not None and sustainability_filter is not None:
                if climate_filter.drought_tolerance_required == DroughtTolerance.HIGH:
                    efficiency = sustainability_filter.min_water_efficiency
                    if efficiency == WaterUseEfficiency.POOR:
                        messages.append('High drought tolerance conflicts with poor water efficiency')
            return messages

        rules.append(drought_vs_water)

        def management_vs_inputs(criteria: TaxonomyFilterCriteria) -> List[str]:
            messages: List[str] = []
            management_filter = criteria.management_filter
            if management_filter is not None:
                complexity = management_filter.max_management_complexity
                inputs = management_filter.max_input_requirements
                if complexity == ManagementComplexity.LOW and inputs == InputRequirements.INTENSIVE:
                    messages.append('Low management complexity conflicts with intensive input requirements')
            return messages

        rules.append(management_vs_inputs)

        def sustainability_vs_market(criteria: TaxonomyFilterCriteria) -> List[str]:
            messages: List[str] = []
            sustainability_filter = criteria.sustainability_filter
            economic_filter = criteria.economic_filter
            if sustainability_filter is not None and economic_filter is not None:
                carbon = sustainability_filter.min_carbon_sequestration
                high_roi = economic_filter.high_roi_potential
                low_cost = economic_filter.low_establishment_cost
                if carbon == CarbonSequestrationPotential.HIGH and high_roi and low_cost:
                    messages.append('High carbon sequestration with high ROI and low establishment cost may be unrealistic')
            return messages

        rules.append(sustainability_vs_market)

        return rules

    # ------------------------------------------------------------------
    # Suggestion helpers
    # ------------------------------------------------------------------

    def _summarize_context(self, request: FilterSuggestionRequest) -> Dict[str, Any]:
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
        summaries: List[FilterPresetSummary] = []
        if not request.include_presets:
            return summaries

        focus_words: List[str] = []
        for item in request.focus_areas:
            focus_words.append(item.lower())

        for key, preset_summary in self._preset_summaries.items():
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

    def _suggest_from_climate(self, request: FilterSuggestionRequest) -> List[FilterSuggestion]:
        suggestions: List[FilterSuggestion] = []
        climate_zone = request.climate_zone
        if climate_zone is None and request.location_coordinates is not None:
            climate_zone = self._resolve_climate_zone_from_coordinates(request.location_coordinates)
        if climate_zone is None:
            return suggestions

        directive_list: List[FilterDirective] = []
        directive_list.append(
            FilterDirective(
                category='climate',
                attribute='hardiness_zones',
                value=[climate_zone],
                priority=0.7,
                rationale='Align crop selection with detected climate zone'
            )
        )
        suggestion = FilterSuggestion(
            key='climate_zone_alignment',
            title='Align with local climate zone',
            description='Limit crops to those proven in the detected climate zone to reduce establishment risk.',
            directives=directive_list,
            rationale=['Ensures selections are biologically suited to local climate conditions'],
            score=0.78,
            category='climate'
        )
        suggestions.append(suggestion)

        climate_profile = self._lookup_climate_profile(climate_zone)
        if climate_profile is not None:
            if climate_profile.get('frost_risk') == 'high':
                frost_directives: List[FilterDirective] = []
                frost_directives.append(
                    FilterDirective(
                        category='climate',
                        attribute='frost_tolerance_required',
                        value='high',
                        priority=0.8,
                        rationale='High frost risk necessitates frost tolerant crops'
                    )
                )
                frost_suggestion = FilterSuggestion(
                    key='frost_risk_protection',
                    title='Prioritize frost tolerant crops',
                    description='High frost risk in the region suggests selecting crops with strong frost tolerance.',
                    directives=frost_directives,
                    rationale=['Mitigates crop loss from early or late season frost events'],
                    score=0.72,
                    category='climate'
                )
                suggestions.append(frost_suggestion)
        return suggestions

    def _suggest_from_soil(self, request: FilterSuggestionRequest) -> List[FilterSuggestion]:
        suggestions: List[FilterSuggestion] = []
        soil_profile = request.context.get('soil_profile') if request.context else None
        if soil_profile is None:
            return suggestions

        ph_value = soil_profile.get('ph') if isinstance(soil_profile, dict) else None
        if ph_value is not None:
            ph_directives: List[FilterDirective] = []
            ph_directives.append(
                FilterDirective(
                    category='soil',
                    attribute='ph_range',
                    value={'min': max(0.0, ph_value - 0.5), 'max': min(14.0, ph_value + 0.5)},
                    priority=0.6,
                    rationale='Target crops suited to measured soil pH'
                )
            )
            suggestion = FilterSuggestion(
                key='soil_ph_alignment',
                title='Match soil pH requirements',
                description='Filter crops by the measured soil pH range to avoid nutrient uptake issues.',
                directives=ph_directives,
                rationale=['Improves nutrient availability and crop establishment success'],
                score=0.64,
                category='soil'
            )
            suggestions.append(suggestion)

        drainage = soil_profile.get('drainage') if isinstance(soil_profile, dict) else None
        if drainage == 'poor':
            drainage_directives: List[FilterDirective] = []
            drainage_directives.append(
                FilterDirective(
                    category='soil',
                    attribute='drainage_classes',
                    value=['poorly drained', 'somewhat poorly drained'],
                    priority=0.5,
                    rationale='Select crops tolerant of poor drainage conditions'
                )
            )
            suggestion = FilterSuggestion(
                key='poor_drainage_management',
                title='Adapt to poor drainage',
                description='Include crops tolerant of poor drainage and saturated soils to reduce root disease risk.',
                directives=drainage_directives,
                rationale=['Prevents yield loss from waterlogged conditions'],
                score=0.58,
                category='soil'
            )
            suggestions.append(suggestion)
        return suggestions

    def _suggest_from_market(self, request: FilterSuggestionRequest) -> List[FilterSuggestion]:
        suggestions: List[FilterSuggestion] = []
        goals = request.context.get('market_goals') if request.context else None
        if goals is None:
            return suggestions

        if isinstance(goals, list):
            index = 0
            while index < len(goals):
                goal = str(goals[index]).lower()
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

    def _suggest_from_sustainability(self, request: FilterSuggestionRequest) -> List[FilterSuggestion]:
        suggestions: List[FilterSuggestion] = []
        sustainability_focus = request.context.get('sustainability_focus') if request.context else None
        if sustainability_focus is None:
            return suggestions

        focus_lower = str(sustainability_focus).lower()
        if 'carbon' in focus_lower:
            directives: List[FilterDirective] = []
            directives.append(
                FilterDirective(
                    category='sustainability',
                    attribute='min_carbon_sequestration',
                    value='high',
                    priority=0.8,
                    rationale='Emphasize crops that build soil carbon'
                )
            )
            suggestion = FilterSuggestion(
                key='carbon_sequestration_focus',
                title='Maximize carbon sequestration',
                description='Highlight crops known for high carbon sequestration potential.',
                directives=directives,
                rationale=['Supports long-term soil health and climate goals'],
                score=0.62,
                category='sustainability'
            )
            suggestions.append(suggestion)
        return suggestions

    # ------------------------------------------------------------------
    # Directive application helpers
    # ------------------------------------------------------------------

    def _clone_criteria(self, criteria: TaxonomyFilterCriteria) -> TaxonomyFilterCriteria:
        criteria_dict = criteria.dict()
        cloned = TaxonomyFilterCriteria(**criteria_dict)
        return cloned

    def _apply_preset(self, criteria: TaxonomyFilterCriteria, preset: Dict[str, Any]) -> None:
        updates = preset.get('updates', {})
        for category, values in updates.items():
            directive = FilterDirective(
                category=category.replace('_filter', '').replace('filter', ''),
                attribute='',
                value=None
            )
            self._apply_category_updates(criteria, category, values, directive)

    def _apply_category_updates(
        self,
        criteria: TaxonomyFilterCriteria,
        category_key: str,
        values: Dict[str, Any],
        directive_template: FilterDirective
    ) -> None:
        category = category_key
        if category.endswith('_filter'):
            category = category[:-7]
        for attribute, value in values.items():
            directive = FilterDirective(
                category=category,
                attribute=attribute,
                value=value,
                priority=directive_template.priority,
                rationale=directive_template.rationale
            )
            self._apply_directive(criteria, directive, [])

    def _apply_directive(
        self,
        criteria: TaxonomyFilterCriteria,
        directive: FilterDirective,
        warnings: List[str]
    ) -> None:
        category_name, filter_obj = self._resolve_filter(criteria, directive.category)
        if filter_obj is None:
            warning_text = f"Unknown filter category '{directive.category}'"
            warnings.append(warning_text)
            logger.debug(warning_text)
            return

        attribute = directive.attribute
        if attribute == '':
            warning_text = f"Empty attribute provided for category '{directive.category}'"
            warnings.append(warning_text)
            logger.debug(warning_text)
            return

        if not hasattr(filter_obj, attribute):
            warning_text = f"Unknown attribute '{attribute}' for category '{category_name}'"
            warnings.append(warning_text)
            logger.debug(warning_text)
            return

        model_fields = getattr(filter_obj, '__fields__', {})
        field = model_fields.get(attribute)
        coerced_value = self._coerce_value(field, directive.value)
        current_value = getattr(filter_obj, attribute)
        merged_value = self._merge_values(current_value, coerced_value)
        setattr(filter_obj, attribute, merged_value)

    def _merge_values(self, current_value: Any, new_value: Any) -> Any:
        if current_value is None:
            return new_value
        if new_value is None:
            return current_value
        if isinstance(current_value, list):
            result: List[Any] = []
            for item in current_value:
                result.append(item)
            additions: List[Any] = []
            if isinstance(new_value, list):
                for item in new_value:
                    additions.append(item)
            else:
                additions.append(new_value)
            for candidate in additions:
                exists = False
                for existing in result:
                    if existing == candidate:
                        exists = True
                        break
                if not exists:
                    result.append(candidate)
            return result
        return new_value

    def _coerce_value(self, field: Any, value: Any) -> Any:
        if field is None:
            return value
        try:
            if field.shape == 4 and field.sub_fields:
                converted: List[Any] = []
                if isinstance(value, list):
                    iterator = value
                else:
                    iterator = [value]
                index = 0
                while index < len(iterator):
                    item = iterator[index]
                    converted.append(self._coerce_value(field.sub_fields[0], item))
                    index += 1
                return converted
        except AttributeError:
            pass
        target_type = getattr(field, 'type_', None)
        if target_type is None:
            return value
        try:
            if isinstance(value, str) and hasattr(target_type, '__mro__') and issubclass(target_type, Enum):
                return target_type(value)  # type: ignore[call-arg]
        except TypeError:
            pass
        try:
            return target_type(value)
        except Exception:
            return value

    def _resolve_filter(self, criteria: TaxonomyFilterCriteria, category: str) -> Tuple[str, Optional[Any]]:
        normalized = category.lower().strip()
        if normalized.endswith('_filter'):
            normalized = normalized[:-7]
        if normalized == 'climate':
            if criteria.climate_filter is None:
                criteria.climate_filter = ClimateFilter()
            return 'climate_filter', criteria.climate_filter
        if normalized == 'soil':
            if criteria.soil_filter is None:
                criteria.soil_filter = SoilFilter()
            return 'soil_filter', criteria.soil_filter
        if normalized == 'agricultural':
            if criteria.agricultural_filter is None:
                criteria.agricultural_filter = AgriculturalFilter()
            return 'agricultural_filter', criteria.agricultural_filter
        if normalized == 'management':
            if criteria.management_filter is None:
                criteria.management_filter = ManagementFilter()
            return 'management_filter', criteria.management_filter
        if normalized == 'sustainability':
            if criteria.sustainability_filter is None:
                criteria.sustainability_filter = SustainabilityFilter()
            return 'sustainability_filter', criteria.sustainability_filter
        if normalized == 'economic':
            if criteria.economic_filter is None:
                criteria.economic_filter = EconomicFilter()
            return 'economic_filter', criteria.economic_filter
        if normalized in ('geographic', 'geography'):
            if criteria.geographic_filter is None:
                criteria.geographic_filter = getattr(_filter_model_module, 'GeographicFilter')()
            return 'geographic_filter', criteria.geographic_filter
        return normalized, None

    def _collect_preset_metadata(self, preset_keys: List[str]) -> List[Dict[str, Any]]:
        metadata: List[Dict[str, Any]] = []
        for key in preset_keys:
            preset = self._presets.get(key)
            if preset is None:
                continue
            entry: Dict[str, Any] = {
                'key': key,
                'name': preset.get('name'),
                'description': preset.get('description')
            }
            rationale: List[str] = []
            for item in preset.get('rationale', []):
                rationale.append(item)
            if len(rationale) > 0:
                entry['rationale'] = rationale
            metadata.append(entry)
        return metadata

    def _generate_follow_up_suggestions(
        self,
        criteria: TaxonomyFilterCriteria,
        conflicts: List[str]
    ) -> List[FilterDirective]:
        suggestions: List[FilterDirective] = []
        if len(conflicts) > 0:
            return suggestions

        economic_filter = criteria.economic_filter
        if economic_filter is not None and not economic_filter.high_roi_potential:
            suggestions.append(
                FilterDirective(
                    category='economic',
                    attribute='high_roi_potential',
                    value=True,
                    priority=0.4,
                    rationale='Consider identifying crops with strong profitability potential'
                )
            )

        sustainability_filter = criteria.sustainability_filter
        if sustainability_filter is not None and sustainability_filter.min_biodiversity_support is None:
            suggestions.append(
                FilterDirective(
                    category='sustainability',
                    attribute='min_biodiversity_support',
                    value='moderate',
                    priority=0.3,
                    rationale='Promote biodiversity to support integrated pest management'
                )
            )
        return suggestions

    # ------------------------------------------------------------------
    # Climate integration helpers
    # ------------------------------------------------------------------

    def _resolve_climate_zone_from_coordinates(self, coordinates: Dict[str, float]) -> Optional[str]:
        if _regional_service is None:
            return None
        try:
            # The regional service stores recent coordinates; we look up using available methods if present
            if hasattr(_regional_service, 'lookup_climate_zone'):
                return _regional_service.lookup_climate_zone(coordinates)  # type: ignore[attr-defined]
        except Exception as exc:  # pragma: no cover - optional integration
            logger.debug('Climate zone lookup from coordinates failed: %s', exc)
        return None

    def _lookup_climate_profile(self, climate_zone: str) -> Optional[Dict[str, Any]]:
        if _regional_service is not None and hasattr(_regional_service, 'climate_zones'):
            profile = _regional_service.climate_zones.get(climate_zone)
            if profile is not None:
                return profile
        # Fallback simplified profiles
        fallback_profiles: Dict[str, Dict[str, Any]] = {
            '1': {'frost_risk': 'high'},
            '2': {'frost_risk': 'high'},
            '3': {'frost_risk': 'high'},
            '4': {'frost_risk': 'high'},
            '5': {'frost_risk': 'moderate'},
            '6': {'frost_risk': 'moderate'},
            '7': {'frost_risk': 'moderate'},
            '8': {'frost_risk': 'low'},
            '9': {'frost_risk': 'low'}
        }
        zone_prefix = climate_zone[:1]
        return fallback_profiles.get(zone_prefix)

    # ------------------------------------------------------------------
    # Ranking helpers
    # ------------------------------------------------------------------

    def _build_water_efficiency_rank(self) -> Dict[WaterUseEfficiency, int]:
        ranking: Dict[WaterUseEfficiency, int] = {}
        ranking[WaterUseEfficiency.POOR] = 0
        ranking[WaterUseEfficiency.FAIR] = 1
        ranking[WaterUseEfficiency.GOOD] = 2
        ranking[WaterUseEfficiency.EXCELLENT] = 3
        return ranking

    def _build_drought_rank(self) -> Dict[DroughtTolerance, int]:
        ranking: Dict[DroughtTolerance, int] = {}
        ranking[DroughtTolerance.LOW] = 0
        ranking[DroughtTolerance.MODERATE] = 1
        ranking[DroughtTolerance.HIGH] = 2
        if hasattr(DroughtTolerance, 'VERY_HIGH'):
            ranking[getattr(DroughtTolerance, 'VERY_HIGH')] = 3
        return ranking

    def _build_input_rank(self) -> Dict[InputRequirements, int]:
        ranking: Dict[InputRequirements, int] = {}
        ranking[InputRequirements.MINIMAL] = 0
        ranking[InputRequirements.MODERATE] = 1
        ranking[InputRequirements.INTENSIVE] = 2
        return ranking

    def _build_management_rank(self) -> Dict[ManagementComplexity, int]:
        ranking: Dict[ManagementComplexity, int] = {}
        ranking[ManagementComplexity.LOW] = 0
        ranking[ManagementComplexity.MODERATE] = 1
        ranking[ManagementComplexity.HIGH] = 2
        return ranking

    def _build_market_rank(self) -> Dict[MarketStability, int]:
        ranking: Dict[MarketStability, int] = {}
        ranking[MarketStability.VOLATILE] = 0
        ranking[MarketStability.MODERATE] = 1
        ranking[MarketStability.STABLE] = 2
        return ranking


# Expose reusable engine instance
filter_combination_engine = FilterCombinationEngine()

__all__ = ['FilterCombinationEngine', 'filter_combination_engine']
