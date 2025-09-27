"""Tests for FilterCombinationEngine."""

import os
import sys
from typing import Any, Dict, List

_TEST_DIR = os.path.dirname(__file__)
_SRC_PARENT = os.path.abspath(os.path.join(_TEST_DIR, '..'))
_SRC_DIR = os.path.join(_SRC_PARENT, 'src')

if _SRC_PARENT not in sys.path:
    sys.path.insert(0, _SRC_PARENT)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from src.services.filter_engine import filter_combination_engine  # type: ignore
from models.crop_filtering_models import (  # type: ignore
    FilterCombinationRequest,
    FilterDirective,
    FilterSuggestionRequest,
    MarketStability,
    WaterUseEfficiency
)


def test_combine_filters_applies_presets_and_directives():
    directives: List[FilterDirective] = []
    directives.append(
        FilterDirective(
            category='economic',
            attribute='high_roi_potential',
            value=True,
            priority=0.6,
            rationale='Target high ROI opportunities'
        )
    )
    directives.append(
        FilterDirective(
            category='management',
            attribute='max_management_complexity',
            value='moderate',
            priority=0.4,
            rationale='Balance complexity for mid-scale operations'
        )
    )

    request = FilterCombinationRequest(
        request_id='unit-001',
        preset_keys=['drought_prone_operations'],
        directives=directives,
        context={'climate_zone': '4b'}
    )

    response = filter_combination_engine.combine_filters(request)

    assert 'drought_prone_operations' in response.applied_presets
    assert response.combined_criteria.climate_filter is not None
    assert response.combined_criteria.climate_filter.drought_tolerance_required is not None
    assert response.combined_criteria.economic_filter is not None
    assert response.combined_criteria.economic_filter.high_roi_potential is True
    assert len(response.conflicts) == 0


def test_dependency_rules_adjust_values():
    directives: List[FilterDirective] = []
    directives.append(
        FilterDirective(
            category='economic',
            attribute='high_roi_potential',
            value=True,
            priority=0.5
        )
    )

    request = FilterCombinationRequest(
        request_id='unit-002',
        directives=directives
    )

    response = filter_combination_engine.combine_filters(request)

    assert len(response.dependency_notes) > 0
    economic_filter = response.combined_criteria.economic_filter
    assert economic_filter is not None
    assert economic_filter.market_stability_required == MarketStability.MODERATE


def test_water_efficiency_dependency_upgrades_value():
    directives: List[FilterDirective] = []
    directives.append(
        FilterDirective(
            category='sustainability',
            attribute='min_water_efficiency',
            value='poor'
        )
    )

    request = FilterCombinationRequest(
        request_id='unit-003',
        preset_keys=['drought_prone_operations'],
        directives=directives
    )

    response = filter_combination_engine.combine_filters(request)

    note_found = False
    for note in response.dependency_notes:
        if 'water use efficiency' in note.lower():
            note_found = True
            break
    assert note_found is True
    sustainability_filter = response.combined_criteria.sustainability_filter
    assert sustainability_filter is not None
    assert sustainability_filter.min_water_efficiency == WaterUseEfficiency.EXCELLENT
    assert len(response.conflicts) == 0



def test_conflict_detection_flags_unrealistic_profitability():
    directives: List[FilterDirective] = []
    directives.append(
        FilterDirective(
            category='economic',
            attribute='high_roi_potential',
            value=True
        )
    )
    directives.append(
        FilterDirective(
            category='economic',
            attribute='low_establishment_cost',
            value=True
        )
    )
    directives.append(
        FilterDirective(
            category='sustainability',
            attribute='min_carbon_sequestration',
            value='high'
        )
    )

    request = FilterCombinationRequest(
        request_id='unit-003b',
        directives=directives
    )

    response = filter_combination_engine.combine_filters(request)

    assert len(response.conflicts) > 0
    conflict_found = False
    for message in response.conflicts:
        if 'carbon sequestration' in message.lower():
            conflict_found = True
            break
    assert conflict_found is True


def test_suggest_filters_generates_contextual_suggestions():
    request = FilterSuggestionRequest(
        request_id='unit-004',
        climate_zone='5b',
        context={
            'soil_profile': {'ph': 6.4, 'drainage': 'poor'},
            'market_goals': ['premium']
        },
        focus_areas=['organic', 'profit'],
        include_presets=True,
        max_suggestions=6
    )

    response = filter_combination_engine.suggest_filters(request)

    assert len(response.suggestions) > 0
    categories_seen: List[str] = []
    for suggestion in response.suggestions:
        assert suggestion.title != ''
        assert suggestion.description != ''
        if suggestion.category is not None:
            if suggestion.category not in categories_seen:
                categories_seen.append(suggestion.category)
    assert len(categories_seen) > 0


def test_combination_handles_multiple_agricultural_scenarios():
    climate_zones = ['3a', '4b', '5a', '6b', '7a']
    focus_groups = ['organic', 'drought', 'premium', 'cover', 'regenerative']

    scenarios: List[Dict[str, Any]] = []
    for zone in climate_zones:
        for focus in focus_groups:
            scenario: Dict[str, Any] = {}
            scenario['zone'] = zone
            scenario['focus'] = focus
            if focus == 'organic':
                scenario['preset'] = 'organic_farming'
                scenario['directive'] = FilterDirective(
                    category='sustainability',
                    attribute='min_biodiversity_support',
                    value='high'
                )
            elif focus == 'drought':
                scenario['preset'] = 'drought_prone_operations'
                scenario['directive'] = FilterDirective(
                    category='climate',
                    attribute='drought_tolerance_required',
                    value='high'
                )
            elif focus == 'premium':
                scenario['preset'] = 'high_value_market_focus'
                scenario['directive'] = FilterDirective(
                    category='economic',
                    attribute='premium_market_potential',
                    value=True
                )
            elif focus == 'cover':
                scenario['preset'] = 'organic_farming'
                scenario['directive'] = FilterDirective(
                    category='agricultural',
                    attribute='cover_crop_only',
                    value=True
                )
            else:
                scenario['preset'] = 'organic_farming'
                scenario['directive'] = FilterDirective(
                    category='sustainability',
                    attribute='min_carbon_sequestration',
                    value='high'
                )
            scenarios.append(scenario)
            if len(scenarios) >= 20:
                break
        if len(scenarios) >= 20:
            break

    index = 0
    while index < len(scenarios):
        scenario = scenarios[index]
        directives: List[FilterDirective] = []
        directives.append(scenario['directive'])
        request = FilterCombinationRequest(
            request_id=f'scenario-{index}',
            preset_keys=[scenario['preset']],
            directives=directives,
            context={'climate_zone': scenario['zone']}
        )
        response = filter_combination_engine.combine_filters(request)
        assert response is not None
        assert len(response.conflicts) == 0
        index += 1

    assert len(scenarios) >= 20
