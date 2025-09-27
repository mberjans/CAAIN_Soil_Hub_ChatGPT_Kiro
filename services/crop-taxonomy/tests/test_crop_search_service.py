"""Tests for the crop search ranking and visualization features."""

import os
import sys
import asyncio
import pytest

_TEST_DIR = os.path.dirname(__file__)
_SRC_PARENT = os.path.abspath(os.path.join(_TEST_DIR, '..'))
_SRC_DIR = os.path.join(_SRC_PARENT, 'src')

if _SRC_PARENT not in sys.path:
    sys.path.insert(0, _SRC_PARENT)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from src.services.crop_search_service import CropSearchService  # type: ignore
from models.crop_filtering_models import (  # type: ignore
    CropSearchRequest,
    SortField,
    SortOrder,
    TaxonomyFilterCriteria,
)


def test_search_provides_ranking_and_visualization_details():
    service = CropSearchService()

    criteria = TaxonomyFilterCriteria(text_search="wheat")
    request = CropSearchRequest(
        request_id="test-ranking-visualization-001",
        filter_criteria=criteria,
        max_results=5,
        sort_by=SortField.SUITABILITY_SCORE,
        sort_order=SortOrder.DESC,
    )

    response = asyncio.run(service.search_crops(request))

    assert response.total_count > 0
    assert len(response.results) > 0

    first_result = response.results[0]
    assert first_result.ranking_details is not None
    assert len(first_result.score_breakdown) > 0

    ranking_details = first_result.ranking_details
    assert ranking_details is not None
    assert ranking_details.active_filters >= 0
    assert ranking_details.coverage >= 0.0
    assert ranking_details.coverage <= 1.0

    has_filter_scores = False
    index = 0
    while index < len(ranking_details.filter_scores):
        filter_entry = ranking_details.filter_scores[index]
        assert filter_entry.name != ""
        assert filter_entry.weight >= 0.0
        assert filter_entry.score >= 0.0
        assert filter_entry.score <= 1.0
        has_filter_scores = True
        index += 1
    assert has_filter_scores is True

    summary = response.visualization_summary
    assert summary is not None
    assert len(summary.score_distribution) == 4

    distribution_total = 0
    bucket_index = 0
    while bucket_index < len(summary.score_distribution):
        bucket = summary.score_distribution[bucket_index]
        assert bucket.minimum >= 0.0
        assert bucket.maximum <= 1.0
        assert bucket.count >= 0
        distribution_total = distribution_total + bucket.count
        bucket_index += 1
    assert distribution_total >= len(response.results)

    contribution_index = 0
    contribution_seen = False
    while contribution_index < len(summary.filter_contributions):
        contribution = summary.filter_contributions[contribution_index]
        assert contribution.name != ""
        assert contribution.weight >= 0.0
        assert contribution.average_score >= 0.0
        assert contribution.average_score <= 1.0
        contribution_seen = True
        contribution_index += 1
    assert contribution_seen is True

    assert 'matched_filters' in summary.match_summary
    assert 'partial_filters' in summary.match_summary
    assert 'missing_filters' in summary.match_summary

    assert len(summary.highlights) > 0

    if response.ranking_overview is not None:
        overview = response.ranking_overview
        assert overview.best_score >= overview.worst_score
        assert overview.median_score >= 0.0
        assert overview.median_score <= 1.0
        assert overview.average_coverage >= 0.0
        assert overview.average_coverage <= 1.0
