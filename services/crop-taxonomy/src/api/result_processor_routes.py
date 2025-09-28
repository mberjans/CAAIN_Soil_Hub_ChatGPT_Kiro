from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import logging

from ..services.result_processor import FilterResultProcessor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/filter-results", tags=["filter-results"])

async def get_result_processor() -> FilterResultProcessor:
    return FilterResultProcessor()

@router.post("/process", response_model=Dict[str, Any])
async def process_filtered_crops(
    filtered_crops: List[Dict[str, Any]],
    filtering_criteria: Dict[str, Any],
    processor: FilterResultProcessor = Depends(get_result_processor)
):
    """
    Processes a list of filtered crops to apply ranking, clustering, and prepare visualization data.

    This endpoint takes the raw output from a filtering operation and enhances it
    with intelligent ranking based on relevance, groups similar crops through clustering,
    and formats the data for easy consumption by frontend visualization components.

    Args:
        filtered_crops: A list of crop dictionaries that passed the initial filtering.
        filtering_criteria: The criteria used for filtering, to inform ranking.

    Returns:
        A dictionary containing:
        - ranked_results: Crops sorted by relevance score.
        - clustered_results: Crops grouped by similarity.
        - visualization_data: Data structured for charts and comparison tables.
        - alternatives: Suggestions if no crops matched the criteria.
    """
    try:
        result = await processor.process_results(filtered_crops, filtering_criteria)
        return result
    except Exception as e:
        logger.error(f"Error processing filtered crops: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process results: {str(e)}")
