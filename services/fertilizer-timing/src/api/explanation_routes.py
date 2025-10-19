"""
API routes for fertilizer timing reasoning and explanation generation.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from models import (
    ProgramAnalysisContext,
    TimingExplanation,
    TimingExplanationRequest,
    TimingOptimizationRequest,
    TimingOptimizationResult,
)
from services.timing_explanation_service import TimingExplanationService
from timing_services import TimingResultRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fertilizer-timing", tags=["fertilizer-timing-explanations"])


def get_explanation_service() -> TimingExplanationService:
    return TimingExplanationService()


def get_repository() -> TimingResultRepository:
    return TimingResultRepository()


def _build_context_from_request(
    optimization_request: TimingOptimizationRequest,
) -> Optional[ProgramAnalysisContext]:
    """
    Convert an optimization request into a program analysis context when possible.
    """
    try:
        context = ProgramAnalysisContext(
            field_id=optimization_request.field_id,
            crop_name=optimization_request.crop_type,
            planting_date=optimization_request.planting_date,
            expected_harvest_date=optimization_request.expected_harvest_date,
            fertilizer_requirements=optimization_request.fertilizer_requirements,
            soil_type=optimization_request.soil_type,
            soil_moisture_capacity=optimization_request.soil_moisture_capacity,
            drainage_class=optimization_request.drainage_class,
            slope_percent=optimization_request.slope_percent,
            location=optimization_request.location,
        )
        return context
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("Failed to derive context from optimization request: %s", exc)
        return None


@router.post(
    "/explanations",
    response_model=TimingExplanation,
    status_code=status.HTTP_200_OK,
)
async def generate_timing_explanation(
    payload: TimingExplanationRequest,
    explanation_service: TimingExplanationService = Depends(get_explanation_service),
    repository: TimingResultRepository = Depends(get_repository),
) -> TimingExplanation:
    """
    Generate a comprehensive explanation for fertilizer timing recommendations.
    """
    try:
        optimization_result = payload.optimization_result
        derived_context: Optional[ProgramAnalysisContext] = None

        if optimization_result is None:
            if payload.request_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="optimization_result or request_id must be supplied.",
                )

            stored_payload = await repository.load_result(payload.request_id)
            if stored_payload is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No optimization result found for the provided request_id.",
                )

            if "result" not in stored_payload:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Optimization result payload is unavailable for the provided request_id.",
                )

            stored_result = stored_payload.get("result")
            if not isinstance(stored_result, TimingOptimizationResult):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Stored optimization result is invalid.",
                )
            optimization_result = stored_result

            stored_request = stored_payload.get("request")
            if isinstance(stored_request, TimingOptimizationRequest):
                derived_context = _build_context_from_request(stored_request)

        context = payload.context
        if context is None and derived_context is not None:
            context = derived_context

        explanation = explanation_service.build_explanation(
            optimization_result,
            context,
            payload.timing_assessment,
        )
        return explanation
    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to generate timing explanation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate timing explanation: {exc}",
        ) from exc


@router.get(
    "/explanations/{request_id}",
    response_model=TimingExplanation,
    status_code=status.HTTP_200_OK,
)
async def get_explanation_for_request(
    request_id: str,
    explanation_service: TimingExplanationService = Depends(get_explanation_service),
    repository: TimingResultRepository = Depends(get_repository),
) -> TimingExplanation:
    """
    Retrieve a stored optimization result and generate an explanation on demand.
    """
    try:
        stored_payload = await repository.load_result(request_id)
        if stored_payload is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No optimization result found for the provided request_id.",
            )

        stored_result = stored_payload.get("result")
        if not isinstance(stored_result, TimingOptimizationResult):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Optimization result unavailable for the provided request_id.",
            )

        derived_context = None
        stored_request = stored_payload.get("request")
        if isinstance(stored_request, TimingOptimizationRequest):
            derived_context = _build_context_from_request(stored_request)

        explanation = explanation_service.build_explanation(
            stored_result,
            derived_context,
            None,
        )
        return explanation
    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to retrieve timing explanation for request_id %s", request_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve timing explanation: {exc}",
        ) from exc


__all__ = ["router"]
