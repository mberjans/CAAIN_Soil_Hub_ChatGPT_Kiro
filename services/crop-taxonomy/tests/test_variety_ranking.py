"""Tests for AdvancedVarietyRanking."""

import os
import sys
from typing import Any, Dict

import pytest

_TEST_DIR = os.path.dirname(__file__)
_SRC_PARENT = os.path.abspath(os.path.join(_TEST_DIR, '..'))
_SRC_DIR = os.path.join(_SRC_PARENT, 'src')

if _SRC_PARENT not in sys.path:
    sys.path.insert(0, _SRC_PARENT)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from src.services.advanced_variety_ranking import AdvancedVarietyRanking  # type: ignore


def _build_candidate(identifier: str, scores: Dict[str, float], ranking: AdvancedVarietyRanking) -> Dict[str, Any]:
    candidate: Dict[str, Any] = {}
    candidate["identifier"] = identifier
    candidate["scores"] = scores
    baseline_value = 0.0
    for criterion in scores.keys():
        if criterion in ranking.base_weights:
            baseline_value += scores[criterion] * ranking.base_weights[criterion]
    candidate["baseline_score"] = baseline_value
    return candidate


def test_ranking_prioritizes_climate_under_high_risk() -> None:
    ranking = AdvancedVarietyRanking()
    candidates = []

    scores_a: Dict[str, float] = {}
    scores_a["yield_potential"] = 0.85
    scores_a["climate_adaptation"] = 0.55
    scores_a["disease_resistance"] = 0.65
    scores_a["market_desirability"] = 0.6
    scores_a["management_ease"] = 0.7
    scores_a["risk_tolerance"] = 0.6
    scores_a["quality_attributes"] = 0.5
    candidates.append(_build_candidate("A", scores_a, ranking))

    scores_b: Dict[str, float] = {}
    scores_b["yield_potential"] = 0.78
    scores_b["climate_adaptation"] = 0.9
    scores_b["disease_resistance"] = 0.7
    scores_b["market_desirability"] = 0.58
    scores_b["management_ease"] = 0.68
    scores_b["risk_tolerance"] = 0.65
    scores_b["quality_attributes"] = 0.55
    candidates.append(_build_candidate("B", scores_b, ranking))

    scores_c: Dict[str, float] = {}
    scores_c["yield_potential"] = 0.82
    scores_c["climate_adaptation"] = 0.5
    scores_c["disease_resistance"] = 0.62
    scores_c["market_desirability"] = 0.6
    scores_c["management_ease"] = 0.64
    scores_c["risk_tolerance"] = 0.58
    scores_c["quality_attributes"] = 0.54
    candidates.append(_build_candidate("C", scores_c, ranking))

    regional_context: Dict[str, Any] = {}
    climate_risks: Dict[str, float] = {}
    climate_risks["drought_risk"] = 0.85
    climate_risks["heat_risk"] = 0.75
    regional_context["climate_risks"] = climate_risks

    results = ranking.rank_varieties(candidates, regional_context, None)
    weights = results["weights"]

    assert weights["climate_adaptation"] > ranking.base_weights["climate_adaptation"]

    best_identifier = None
    best_score = -1.0
    for candidate_id, info in results["results"].items():
        score_value = info.get("score", 0.0)
        if score_value > best_score:
            best_score = score_value
            best_identifier = candidate_id

    assert best_identifier == "B"
    assert best_score == pytest.approx(results["results"]["B"]["score"], rel=0.0001)


def test_weight_overrides_shift_priority_to_disease() -> None:
    ranking = AdvancedVarietyRanking()
    candidates = []

    high_yield_scores: Dict[str, float] = {}
    high_yield_scores["yield_potential"] = 0.9
    high_yield_scores["climate_adaptation"] = 0.6
    high_yield_scores["disease_resistance"] = 0.45
    high_yield_scores["market_desirability"] = 0.7
    high_yield_scores["management_ease"] = 0.7
    high_yield_scores["risk_tolerance"] = 0.65
    high_yield_scores["quality_attributes"] = 0.6
    candidates.append(_build_candidate("YieldLeader", high_yield_scores, ranking))

    disease_focus_scores: Dict[str, float] = {}
    disease_focus_scores["yield_potential"] = 0.72
    disease_focus_scores["climate_adaptation"] = 0.7
    disease_focus_scores["disease_resistance"] = 0.92
    disease_focus_scores["market_desirability"] = 0.66
    disease_focus_scores["management_ease"] = 0.68
    disease_focus_scores["risk_tolerance"] = 0.7
    disease_focus_scores["quality_attributes"] = 0.58
    candidates.append(_build_candidate("ShieldPlus", disease_focus_scores, ranking))

    preferences: Dict[str, Any] = {}
    overrides: Dict[str, float] = {}
    overrides["disease_resistance"] = 0.38
    overrides["yield_potential"] = 0.12
    overrides["market_desirability"] = 0.12
    overrides["management_ease"] = 0.1
    overrides["climate_adaptation"] = 0.1
    overrides["risk_tolerance"] = 0.1
    overrides["quality_attributes"] = 0.08
    preferences["weight_overrides"] = overrides

    preferences["primary_focus"] = "disease"

    results = ranking.rank_varieties(candidates, None, preferences)
    weights = results["weights"]

    assert weights["disease_resistance"] >= weights["yield_potential"]

    best_identifier = None
    best_score = -1.0
    for candidate_id, info in results["results"].items():
        score_value = info.get("score", 0.0)
        if score_value > best_score:
            best_score = score_value
            best_identifier = candidate_id

    assert best_identifier == "ShieldPlus"
    assert best_score > results["results"]["YieldLeader"]["score"]
