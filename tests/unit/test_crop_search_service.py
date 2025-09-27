"""Unit tests for the crop search service advanced filtering."""

import asyncio
import importlib.util
import pathlib
import sys

import pytest


def _ensure_service_path() -> None:
    current_file = pathlib.Path(__file__).resolve()
    service_src = current_file.parents[2] / "services" / "crop-taxonomy" / "src"
    service_path = str(service_src)
    if service_path not in sys.path:
        sys.path.insert(0, service_path)


_ensure_service_path()


def _load_crop_search_service() -> type:
    current_file = pathlib.Path(__file__).resolve()
    module_path = current_file.parents[2] / "services" / "crop-taxonomy" / "src" / "services" / "crop_search_service.py"
    spec = importlib.util.spec_from_file_location("crop_search_service_module", module_path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load crop_search_service module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module.CropSearchService


CropSearchService = _load_crop_search_service()
from models.crop_filtering_models import (  # type: ignore  # noqa: E402
    AgriculturalFilter,
    CropSearchRequest,
    SortField,
    SortOrder,
    TaxonomyFilterCriteria,
)


def _create_search_service() -> CropSearchService:
    service = CropSearchService(database_url="postgresql://invalid-host")
    service.database_available = False
    service.db = None
    return service


def test_crop_search_text_filter_returns_expected_crop() -> None:
    service = _create_search_service()
    criteria = TaxonomyFilterCriteria(text_search="wheat")
    request = CropSearchRequest(
        request_id="text-search",
        filter_criteria=criteria,
        max_results=5,
        offset=0,
        sort_by=SortField.NAME,
        sort_order=SortOrder.ASC,
    )

    response = asyncio.run(service.search_crops(request))

    found_wheat = False
    index = 0
    while index < len(response.results):
        crop_name = response.results[index].crop.crop_name.lower()
        if crop_name == "wheat":
            found_wheat = True
            break
        index += 1

    assert found_wheat, "Expected to find wheat in text search results"


def test_crop_search_agricultural_filter_returns_nitrogen_fixers() -> None:
    service = _create_search_service()
    agricultural_filter = AgriculturalFilter(nitrogen_fixing_required=True)
    criteria = TaxonomyFilterCriteria(agricultural_filter=agricultural_filter)
    request = CropSearchRequest(
        request_id="ag-filter",
        filter_criteria=criteria,
        max_results=10,
        offset=0,
        sort_by=SortField.SUITABILITY_SCORE,
        sort_order=SortOrder.DESC,
    )

    response = asyncio.run(service.search_crops(request))

    assert response.total_count > 0, "Expected at least one nitrogen fixing crop"

    index = 0
    while index < len(response.results):
        classification = response.results[index].crop.agricultural_classification
        nitrogen_fixing = False
        if classification is not None and classification.nitrogen_fixing:
            nitrogen_fixing = True
        assert nitrogen_fixing, "All returned crops should fix nitrogen"
        index += 1
