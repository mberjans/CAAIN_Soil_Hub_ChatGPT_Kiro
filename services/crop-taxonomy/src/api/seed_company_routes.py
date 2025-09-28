"""
Seed Company Integration API Routes

FastAPI routes for seed company integration service, providing endpoints
for data synchronization, status monitoring, and variety availability queries.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..services.seed_company_service import (
    SeedCompanyIntegrationService,
    SyncStatus,
    VarietyUpdateRecord
)
from ..models.crop_variety_models import SeedCompanyOffering

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/seed-companies", tags=["seed-companies"])

# Dependency injection
async def get_seed_company_service() -> SeedCompanyIntegrationService:
    return SeedCompanyIntegrationService()


@router.post("/sync", response_model=Dict[str, str])
async def sync_all_companies(
    background_tasks: BackgroundTasks,
    service: SeedCompanyIntegrationService = Depends(get_seed_company_service)
):
    """
    Synchronize data from all configured seed companies.
    
    This endpoint triggers a full synchronization with all seed companies,
    updating variety data, availability information, and pricing.
    
    **Companies Integrated:**
    - Pioneer/Corteva
    - Bayer/Dekalb  
    - Syngenta
    - BASF (planned)
    - Regional seed companies (planned)
    
    **Data Updated:**
    - Variety characteristics and traits
    - Seed availability and pricing
    - Regional distribution information
    - Technology packages and herbicide tolerances
    
    Returns sync status for each company.
    """
    try:
        # Run sync in background to avoid timeout
        background_tasks.add_task(service.sync_all_companies)
        
        return {
            "message": "Seed company synchronization started",
            "status": "initiated",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error initiating seed company sync: {e}")
        raise HTTPException(status_code=500, detail=f"Sync initiation failed: {str(e)}")


@router.get("/sync-status", response_model=Dict[str, Dict[str, Any]])
async def get_sync_status(
    service: SeedCompanyIntegrationService = Depends(get_seed_company_service)
):
    """
    Get synchronization status for all seed companies.
    
    Returns detailed status information including:
    - Last sync timestamp
    - Current sync status
    - Error counts and retry information
    - Next scheduled sync time
    - Data quality metrics
    """
    try:
        status_info = await service.get_company_sync_status()
        return status_info
        
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")


@router.post("/sync/{company_name}", response_model=Dict[str, str])
async def sync_specific_company(
    company_name: str,
    service: SeedCompanyIntegrationService = Depends(get_seed_company_service)
):
    """
    Synchronize data from a specific seed company.
    
    **Supported Companies:**
    - pioneer (Pioneer/Corteva)
    - bayer (Bayer/Dekalb)
    - syngenta (Syngenta)
    
    Args:
        company_name: Name of the seed company to sync
        
    Returns:
        Sync status and details for the specific company
    """
    try:
        if company_name not in service.providers:
            raise HTTPException(
                status_code=404, 
                detail=f"Company '{company_name}' not found. Available companies: {list(service.providers.keys())}"
            )
        
        provider = service.providers[company_name]
        status = await service._sync_company_data(company_name, provider)
        
        return {
            "company": company_name,
            "status": status.value,
            "timestamp": datetime.now().isoformat(),
            "message": f"Sync completed for {company_name}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing company {company_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Company sync failed: {str(e)}")


@router.get("/varieties/{variety_name}/availability", response_model=List[SeedCompanyOffering])
async def get_variety_availability(
    variety_name: str,
    company_name: Optional[str] = Query(None, description="Filter by specific company"),
    service: SeedCompanyIntegrationService = Depends(get_seed_company_service)
):
    """
    Get availability information for a specific variety across seed companies.
    
    **Information Provided:**
    - Company-specific product codes
    - Current availability status (in stock, limited, preorder, etc.)
    - Regional distribution information
    - Pricing information (when available)
    - Last update timestamps
    
    Args:
        variety_name: Name of the variety to check
        company_name: Optional filter by specific company
        
    Returns:
        List of seed company offerings for the variety
    """
    try:
        availability = await service.get_variety_availability(variety_name, company_name)
        return availability
        
    except Exception as e:
        logger.error(f"Error getting variety availability: {e}")
        raise HTTPException(status_code=500, detail=f"Availability check failed: {str(e)}")


@router.get("/sync-history", response_model=List[Dict[str, Any]])
async def get_sync_history(
    company_name: Optional[str] = Query(None, description="Filter by company name"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: SeedCompanyIntegrationService = Depends(get_seed_company_service)
):
    """
    Get synchronization history for tracking data changes.
    
    **History Information:**
    - Variety update records
    - Data change timestamps
    - Change types (new, updated, discontinued)
    - Data hash for change tracking
    - Company-specific update details
    
    Args:
        company_name: Optional filter by company name
        limit: Maximum number of records to return
        
    Returns:
        List of variety update records
    """
    try:
        history = service.get_sync_history(company_name)
        
        # Convert dataclass to dict for JSON serialization
        history_dicts = []
        for record in history[-limit:]:  # Get most recent records
            history_dicts.append({
                "variety_id": str(record.variety_id),
                "company_name": record.company_name,
                "update_type": record.update_type,
                "changes": record.changes,
                "timestamp": record.timestamp.isoformat(),
                "data_hash": record.data_hash
            })
        
        return history_dicts
        
    except Exception as e:
        logger.error(f"Error getting sync history: {e}")
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")


@router.post("/validate-variety-data", response_model=Dict[str, Any])
async def validate_variety_data(
    variety_data: Dict[str, Any],
    service: SeedCompanyIntegrationService = Depends(get_seed_company_service)
):
    """
    Validate variety data from seed companies.
    
    **Validation Checks:**
    - Required field validation
    - Data type validation
    - Range validation for numeric fields
    - Enum value validation
    - Data quality scoring
    
    Args:
        variety_data: Variety data to validate
        
    Returns:
        Validation result with quality score and issues
    """
    try:
        validation_result = await service.validate_variety_data(variety_data)
        
        return {
            "is_valid": validation_result.is_valid,
            "quality_score": validation_result.quality_score,
            "data_quality": validation_result.data_quality.value,
            "issues": validation_result.issues,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error validating variety data: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/companies", response_model=List[Dict[str, Any]])
async def get_configured_companies(
    service: SeedCompanyIntegrationService = Depends(get_seed_company_service)
):
    """
    Get list of configured seed companies and their integration details.
    
    **Company Information:**
    - Company name and type
    - API endpoint configuration
    - Rate limiting information
    - Update frequency settings
    - Current sync status
    
    Returns:
        List of configured seed companies with their settings
    """
    try:
        companies = []
        for company_name, config in service.company_configs.items():
            companies.append({
                "company_name": config.company_name,
                "company_type": config.company_type.value,
                "api_endpoint": config.api_endpoint,
                "rate_limit_per_minute": config.rate_limit_per_minute,
                "update_frequency_hours": config.update_frequency_hours,
                "sync_status": config.sync_status.value,
                "error_count": config.error_count,
                "max_retries": config.max_retries,
                "last_sync": config.last_sync.isoformat() if config.last_sync else None
            })
        
        return companies
        
    except Exception as e:
        logger.error(f"Error getting configured companies: {e}")
        raise HTTPException(status_code=500, detail=f"Company list retrieval failed: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for seed company integration service.
    
    Returns:
        Service health status and basic information
    """
    return {
        "status": "healthy",
        "service": "seed-company-integration",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# Example usage documentation
@router.get("/docs/examples")
async def get_usage_examples():
    """
    Get usage examples for the seed company integration API.
    
    Returns:
        Example requests and responses for common operations
    """
    return {
        "sync_all_companies": {
            "method": "POST",
            "endpoint": "/api/v1/seed-companies/sync",
            "description": "Trigger synchronization with all seed companies",
            "response": {
                "message": "Seed company synchronization started",
                "status": "initiated",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        },
        "get_sync_status": {
            "method": "GET", 
            "endpoint": "/api/v1/seed-companies/sync-status",
            "description": "Get synchronization status for all companies",
            "response": {
                "pioneer": {
                    "company_name": "Pioneer/Corteva",
                    "last_sync": "2024-01-15T09:00:00Z",
                    "sync_status": "success",
                    "error_count": 0,
                    "next_sync_due": "2024-01-16T09:00:00Z"
                }
            }
        },
        "get_variety_availability": {
            "method": "GET",
            "endpoint": "/api/v1/seed-companies/varieties/{variety_name}/availability",
            "description": "Get availability information for a specific variety",
            "example_url": "/api/v1/seed-companies/varieties/Pioneer%20P1234/availability",
            "response": [
                {
                    "company_name": "Pioneer/Corteva",
                    "product_code": "P1234",
                    "availability_status": "in_stock",
                    "distribution_regions": ["Midwest", "Great Plains"],
                    "price_per_unit": 350.0,
                    "price_unit": "bag",
                    "last_updated": "2024-01-15T10:00:00Z"
                }
            ]
        }
    }