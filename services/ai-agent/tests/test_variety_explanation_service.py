"""Tests for variety explanation service."""

from pathlib import Path
import sys

import pytest

SERVICE_ROOT_PATH = Path(__file__).resolve().parents[1]
SERVICE_ROOT_STR = str(SERVICE_ROOT_PATH)
if SERVICE_ROOT_STR not in sys.path:
    sys.path.insert(0, SERVICE_ROOT_STR)

from src.services.variety_explanation_service import VarietyExplanationService


def _build_sample_recommendation() -> dict:
    recommendation = {}
    recommended_varieties = []

    variety_entry = {
        "variety_name": "Hybrid A",
        "overall_score": 0.87,
        "key_advantages": ["Strong drought tolerance"],
        "potential_challenges": ["Monitor for gray leaf spot"],
        "recommended_practices": ["Plant between April 25 and May 10"],
        "economic_analysis": {
            "gross_margin": 325.45,
            "seed_cost_per_acre": 115.0
        }
    }
    recommended_varieties.append(variety_entry)
    recommendation["recommended_varieties"] = recommended_varieties

    return recommendation


def test_is_variety_recommendation_true():
    service = VarietyExplanationService()
    recommendation = _build_sample_recommendation()

    result = service.is_variety_recommendation(recommendation)

    assert result is True


def test_build_explanation_payload_language_preference():
    service = VarietyExplanationService()
    recommendation = _build_sample_recommendation()
    context = {
        "user_profile": {
            "preferred_language": "es",
            "expertise_level": "advanced"
        }
    }

    payload = service.build_explanation_payload(recommendation, context)

    assert payload["language"] == "es"
    assert payload["audience_level"] == "advanced"
    assert len(payload["variety_summaries"]) > 0
    assert "yield_insights" in payload
    assert isinstance(payload["yield_insights"], list)
    assert len(payload["yield_insights"]) > 0
    assert "disease_highlights" in payload
    assert isinstance(payload["disease_highlights"], list)
    assert len(payload["disease_highlights"]) > 0
    assert "climate_adaptation" in payload
    assert isinstance(payload["climate_adaptation"], list)
    assert len(payload["climate_adaptation"]) > 0
    assert "quality_metrics" in payload
    metrics = payload["quality_metrics"]
    assert isinstance(metrics, dict)
    assert "coherence_score" in metrics
    assert "coverage_score" in metrics
    assert "accuracy_flags" in metrics
    assert "comprehension_notes" in metrics

    assert "supporting_evidence" in payload
    evidence_records = payload["supporting_evidence"]
    assert isinstance(evidence_records, list)
    assert len(evidence_records) > 0

    evidence_summary = payload.get("evidence_summary")
    assert isinstance(evidence_summary, dict)
    assert evidence_summary.get("total_records", 0) >= len(evidence_records)
    assert "high_credibility_records" in evidence_summary
    assert "recent_evidence_ratio" in evidence_summary

    evidence_notes = payload.get("evidence_notes")
    assert isinstance(evidence_notes, list)

    evidence_citations = payload.get("evidence_citations")
    assert isinstance(evidence_citations, list)
    assert len(evidence_citations) > 0
    first_citation = evidence_citations[0]
    assert "label" in first_citation
    assert "categories" in first_citation


def test_build_fallback_text_spanish_heading():
    service = VarietyExplanationService()
    recommendation = _build_sample_recommendation()
    context = {
        "user_profile": {
            "preferred_language": "es"
        }
    }

    payload = service.build_explanation_payload(recommendation, context)
    fallback_text = service.build_fallback_text(payload)

    assert "Resumen" in fallback_text
    assert "Hybrid A" in fallback_text
    assert "Yield outlook" in fallback_text
    assert "Disease and pest notes" in fallback_text
    assert "Climate adaptation" in fallback_text
    assert "Quality metrics" in fallback_text
    assert "Supporting evidence" in fallback_text
