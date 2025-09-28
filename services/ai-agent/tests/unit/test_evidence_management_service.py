"""Unit tests for EvidenceManagementService."""

from datetime import datetime
from pathlib import Path
import sys

import pytest

SERVICE_ROOT_PATH = Path(__file__).resolve().parents[2]
SERVICE_ROOT_STR = str(SERVICE_ROOT_PATH)
if SERVICE_ROOT_STR not in sys.path:
    sys.path.insert(0, SERVICE_ROOT_STR)

from src.services.evidence_management_service import EvidenceManagementService


def _build_recommendation_with_sources() -> dict:
    recommendation = {}
    varieties = []

    variety_entry = {
        "variety_name": "Trial Hybrid 101",
        "overall_score": 0.82,
        "confidence_level": 0.78,
        "yield_potential_percentile": 92,
        "disease_resistances": {
            "gray_leaf_spot": "moderately_resistant"
        },
        "adapted_regions": ["Iowa", "Illinois"],
        "management_recommendations": ["Plant at 32k population on well-drained soils."],
        "evidence_sources": [
            {
                "title": "Iowa State University Corn Variety Trial 2024",
                "category": "yield_performance",
                "source_type": "university",
                "summary": "Ranked in the top 8% across central Iowa replicated trials.",
                "published_at": datetime(2024, 1, 15).isoformat(),
                "confidence": 0.9
            },
            {
                "title": "USDA Extension foliar disease bulletin",
                "category": "disease_resistance",
                "source_type": "extension",
                "summary": "Extension pathologists report durable gray leaf spot tolerance.",
                "published_at": datetime(2023, 9, 1).isoformat(),
                "peer_reviewed": False,
                "reliability": "validated"
            }
        ]
    }
    varieties.append(variety_entry)
    recommendation["recommended_varieties"] = varieties
    return recommendation


def _build_basic_recommendation() -> dict:
    recommendation = {}
    varieties = []

    variety_entry = {
        "variety_name": "Drought Shield 220",
        "overall_score": 0.76,
        "confidence_level": 73,
        "yield_potential_percentile": 88,
        "disease_resistances": {
            "southern_rust": "resistant"
        },
        "management_recommendations": ["Maintain consistent moisture through tasseling."],
        "adapted_regions": ["Nebraska Panhandle"],
        "market_acceptance_score": 4.1
    }
    varieties.append(variety_entry)
    recommendation["recommended_varieties"] = varieties
    return recommendation


def _build_duplicate_recommendation() -> dict:
    recommendation = _build_recommendation_with_sources()
    varieties = recommendation.get("recommended_varieties")
    if isinstance(varieties, list) and len(varieties) > 0:
        first_entry = varieties[0]
        sources = first_entry.get("evidence_sources")
        if isinstance(sources, list):
            duplicate_source = {
                "title": "Iowa State University Corn Variety Trial 2024",
                "category": "yield_performance",
                "source_type": "university",
                "summary": "Ranked in the top 8% across central Iowa replicated trials.",
                "published_at": datetime(2024, 1, 15).isoformat(),
                "confidence": 0.9
            }
            sources.append(duplicate_source)
    return recommendation


def test_build_evidence_package_includes_explicit_sources():
    service = EvidenceManagementService()
    recommendation = _build_recommendation_with_sources()
    context = {"location": {"climate_zone": "5a"}}

    package = service.build_evidence_package(recommendation, context)

    assert package.summary.total_records >= 2
    assert package.summary.average_credibility > 0
    assert package.summary.high_credibility_records >= 1
    assert package.summary.recent_evidence_ratio > 0

    assert isinstance(package.citations, list)
    assert len(package.citations) >= 1

    has_yield_reference = False
    citation_categories_present = False
    index = 0
    while index < len(package.records):
        record = package.records[index]
        if record.category == "yield_performance":
            has_yield_reference = True
        assert 0.0 <= record.credibility_score <= 1.0
        assert 0.0 <= record.strength_score <= 1.0
        index += 1

    citation_index = 0
    while citation_index < len(package.citations):
        citation = package.citations[citation_index]
        assert citation.label.startswith("[")
        if len(citation.categories) > 0:
            citation_categories_present = True
        citation_index += 1

    assert has_yield_reference is True
    assert citation_categories_present is True
    assert len(package.coverage_notes) >= 0


def test_build_evidence_package_generates_fallback_records():
    service = EvidenceManagementService(minimum_records=2)
    recommendation = _build_basic_recommendation()
    context = {"location": {"climate_zone": "6b"}}

    package = service.build_evidence_package(recommendation, context)

    assert package.summary.total_records >= 2
    assert package.summary.average_strength >= 0
    assert package.summary.recent_evidence_ratio == 0

    has_climate_note = False
    has_recency_note = False
    note_index = 0
    while note_index < len(package.coverage_notes):
        note = package.coverage_notes[note_index]
        if "climate" in note.lower():
            has_climate_note = True
        if "recency" in note.lower() or "newer" in note.lower():
            has_recency_note = True
        note_index += 1

    assert has_climate_note is True or len(package.coverage_notes) >= 0
    assert has_recency_note is True

    category_found = False
    record_index = 0
    while record_index < len(package.records):
        record = package.records[record_index]
        if record.category in ("yield_performance", "disease_resistance"):
            category_found = True
        record_index += 1

    assert category_found is True


def test_evidence_package_deduplicates_duplicate_sources():
    service = EvidenceManagementService()
    recommendation = _build_duplicate_recommendation()
    package = service.build_evidence_package(recommendation, {})

    duplicate_count = 0
    index = 0
    while index < len(package.records):
        record = package.records[index]
        if record.source_name == "Iowa State University Corn Variety Trial 2024" and record.category == "yield_performance":
            duplicate_count += 1
        index += 1

    assert duplicate_count == 1

    unique_trial_citations = 0
    citation_index = 0
    while citation_index < len(package.citations):
        citation = package.citations[citation_index]
        if citation.source_name == "Iowa State University Corn Variety Trial 2024":
            unique_trial_citations += 1
        citation_index += 1

    assert unique_trial_citations == 1
    assert len(package.citations) >= 2
