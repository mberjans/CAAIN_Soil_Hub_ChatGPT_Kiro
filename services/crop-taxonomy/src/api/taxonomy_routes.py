"""
Taxonomy API Routes

FastAPI routes for crop taxonomic classification and validation operations.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from uuid import UUID

try:
    from ..services.crop_taxonomy_service import crop_taxonomy_service
    from ..services.crop_attribute_service import crop_attribute_tagging_service
    from ..models.service_models import (
        TaxonomicClassificationRequest,
        TaxonomicClassificationResponse,
        ValidationRequest,
        ValidationResponse,
        AutoTagGenerationRequest,
        AutoTagGenerationResponse,
        TagManagementRequest,
        TagManagementResponse
    )
    from ..models.crop_taxonomy_models import (
        BulkCropImportRequest,
        BulkCropImportResponse,
        ComprehensiveCropData
    )
except ImportError:
    from services.crop_taxonomy_service import crop_taxonomy_service
    from services.crop_attribute_service import crop_attribute_tagging_service
    from models.service_models import (
        TaxonomicClassificationRequest,
        TaxonomicClassificationResponse,
        ValidationRequest,
        ValidationResponse,
        AutoTagGenerationRequest,
        AutoTagGenerationResponse,
        TagManagementRequest,
        TagManagementResponse
    )
    from models.crop_taxonomy_models import (
        BulkCropImportRequest,
        BulkCropImportResponse,
        ComprehensiveCropData
    )


router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])


@router.post("/classify", response_model=TaxonomicClassificationResponse)
async def classify_crop_taxonomically(
    request: TaxonomicClassificationRequest
):
    """
    Classify a crop taxonomically based on common name or botanical characteristics.
    
    - **common_name**: Common name of the crop (e.g., "wheat", "corn")
    - **botanical_characteristics**: Optional botanical characteristics for classification
    - **region**: Optional region for context-specific classification
    
    Returns complete taxonomic hierarchy with confidence scores.
    """
    try:
        result = await crop_taxonomy_service.classify_crop_taxonomically(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")


@router.post("/validate", response_model=ValidationResponse)
async def validate_crop_data(
    request: ValidationRequest
):
    """
    Validate comprehensive crop data for accuracy and completeness.
    
    - **crop_data**: Complete crop data structure to validate
    - **validation_level**: Level of validation rigor (basic, comprehensive, strict)
    - **check_external_sources**: Whether to check against external botanical databases
    
    Returns detailed validation results with specific feedback on each component.
    """
    try:
        result = await crop_taxonomy_service.validate_crop_data(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@router.post("/bulk-process", response_model=BulkCropImportResponse)
async def process_bulk_crop_data(
    request: BulkCropImportRequest
):
    """
    Process multiple crop data entries with batch validation and processing.
    
    - **crop_data_list**: List of crop data structures to process
    - **allow_partial_validation**: Whether to accept partially valid entries
    - **processing_options**: Optional processing configuration
    
    Returns batch processing results with individual validation outcomes.
    Useful for importing large datasets or batch validation operations.
    """
    try:
        result = await crop_taxonomy_service.process_bulk_crop_data(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk processing error: {str(e)}")


@router.post("/tags/auto-generate", response_model=AutoTagGenerationResponse)
async def auto_generate_crop_tags(
    request: AutoTagGenerationRequest
):
    """Automatically generate crop attribute tags."""
    if crop_attribute_tagging_service is None:
        raise HTTPException(status_code=503, detail="Attribute tagging service unavailable")
    try:
        response = await crop_attribute_tagging_service.auto_generate_tags(request)
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Auto-tagging error: {str(exc)}")


@router.put("/tags/manage", response_model=TagManagementResponse)
async def manage_crop_tags(
    request: TagManagementRequest
):
    """Manage crop attribute tags (add, update, remove, validate)."""
    if crop_attribute_tagging_service is None:
        raise HTTPException(status_code=503, detail="Attribute tagging service unavailable")
    try:
        response = await crop_attribute_tagging_service.manage_tags(request)
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Tag management error: {str(exc)}")


@router.get("/crop/{crop_id}", response_model=ComprehensiveCropData)
async def get_crop_data(
    crop_id: UUID,
    include_varieties: bool = False,
    include_regional_data: bool = False
):
    """
    Retrieve comprehensive crop data by crop ID.
    
    - **crop_id**: UUID of the crop to retrieve
    - **include_varieties**: Whether to include variety information
    - **include_regional_data**: Whether to include regional adaptation data
    
    Returns complete crop taxonomy and classification data.
    """
    # This would be implemented with actual database queries
    raise HTTPException(status_code=501, detail="Crop retrieval not yet implemented")


@router.get("/crops", response_model=List[ComprehensiveCropData])
async def list_crops(
    category: Optional[str] = None,
    family: Optional[str] = None,
    region: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List crops with optional filtering.
    
    - **category**: Filter by agricultural category (grain, oilseed, vegetable, etc.)
    - **family**: Filter by botanical family (Poaceae, Fabaceae, etc.)
    - **region**: Filter by regional adaptation
    - **limit**: Maximum number of results to return
    - **offset**: Number of results to skip for pagination
    
    Returns list of crops matching the filter criteria.
    """
    try:
        crops = await crop_taxonomy_service.list_reference_crops(
            category=category,
            family=family,
            region=region,
            limit=limit,
            offset=offset
        )
        return crops
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crop listing error: {str(e)}")


@router.get("/families", response_model=List[str])
async def get_botanical_families():
    """
    Get list of available botanical families in the taxonomy system.
    
    Returns sorted list of botanical family names with crop counts.
    Useful for building filter interfaces and taxonomy browsing.
    """
    try:
        families = await crop_taxonomy_service.get_reference_families()
        return families
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving families: {str(e)}")


@router.get("/crops/search", response_model=List[Dict[str, Any]])
async def search_crops(
    query: str = Query(..., description="Search query for crop names or characteristics"),
    limit: int = Query(10, description="Maximum number of results to return")
):
    """
    Search crops by name or characteristics.
    
    This endpoint provides crop search functionality for the frontend variety selection interface.
    It searches through crop names, scientific names, and common characteristics.
    
    Args:
        query: Search term (crop name, scientific name, or characteristic)
        limit: Maximum number of results to return
        
    Returns:
        List of matching crops with basic information
    """
    try:
        # For now, return demo data since database integration is not yet implemented
        # This matches the structure expected by the frontend JavaScript
        
        # Sample crop data that matches frontend expectations
        sample_crops = [
            {
                "id": "corn",
                "name": "Corn",
                "scientific_name": "Zea mays",
                "category": "Grain",
                "family": "Poaceae",
                "description": "Major cereal crop grown worldwide for grain and silage"
            },
            {
                "id": "soybean", 
                "name": "Soybean",
                "scientific_name": "Glycine max",
                "category": "Legume",
                "family": "Fabaceae",
                "description": "Important legume crop for protein and oil production"
            },
            {
                "id": "wheat",
                "name": "Wheat", 
                "scientific_name": "Triticum aestivum",
                "category": "Grain",
                "family": "Poaceae",
                "description": "Major cereal crop for bread and flour production"
            },
            {
                "id": "cotton",
                "name": "Cotton",
                "scientific_name": "Gossypium hirsutum", 
                "category": "Fiber",
                "family": "Malvaceae",
                "description": "Fiber crop grown for cotton production"
            },
            {
                "id": "rice",
                "name": "Rice",
                "scientific_name": "Oryza sativa",
                "category": "Grain", 
                "family": "Poaceae",
                "description": "Staple cereal crop in many regions"
            },
            {
                "id": "barley",
                "name": "Barley",
                "scientific_name": "Hordeum vulgare",
                "category": "Grain",
                "family": "Poaceae", 
                "description": "Cereal crop used for feed, malting, and food"
            },
            {
                "id": "oats",
                "name": "Oats",
                "scientific_name": "Avena sativa",
                "category": "Grain",
                "family": "Poaceae",
                "description": "Cereal crop for feed and human consumption"
            },
            {
                "id": "canola",
                "name": "Canola",
                "scientific_name": "Brassica napus",
                "category": "Oilseed",
                "family": "Brassicaceae",
                "description": "Oilseed crop for edible oil production"
            },
            {
                "id": "sunflower",
                "name": "Sunflower", 
                "scientific_name": "Helianthus annuus",
                "category": "Oilseed",
                "family": "Asteraceae",
                "description": "Oilseed crop for oil and confectionery markets"
            },
            {
                "id": "alfalfa",
                "name": "Alfalfa",
                "scientific_name": "Medicago sativa",
                "category": "Forage",
                "family": "Fabaceae",
                "description": "Perennial forage legume for livestock feed"
            }
        ]
        
        # Filter crops based on query
        query_lower = query.lower()
        matching_crops = [
            crop for crop in sample_crops
            if (query_lower in crop["name"].lower() or 
                query_lower in crop["scientific_name"].lower() or
                query_lower in crop["category"].lower() or
                query_lower in crop["description"].lower())
        ]
        
        # Return limited results
        return matching_crops[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crop search error: {str(e)}")


@router.get("/categories", response_model=List[str])
async def get_agricultural_categories():
    """
    Get list of available agricultural categories.
    
    Returns list of agricultural crop categories used in classification.
    """
    try:
        categories = [
            "grain", "oilseed", "forage", "vegetable", "fruit", "specialty",
            "legume", "cereal", "root_crop", "leafy_green", "herb_spice", 
            "fiber", "sugar_crop", "cover_crop", "ornamental", "medicinal"
        ]
        return sorted(categories)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving categories: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the taxonomy service.
    
    Returns service status and basic system information.
    """
    return {
        "status": "healthy",
        "service": "crop-taxonomy",
        "version": "1.0.0",
        "components": {
            "classification": "operational",
            "validation": "operational", 
            "bulk_processing": "operational"
        }
    }
