"""
API endpoints for crop type and growth stage integration system.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from enum import Enum

from src.services.crop_integration_service import (
    CropIntegrationService, CropType, GrowthStage,
    CropGrowthStageInfo, CropApplicationPreferences
)

router = APIRouter(prefix="/api/v1/crop-integration", tags=["crop-integration"])

# Initialize service
service = CropIntegrationService()

# Create Pydantic-compatible enums
class CropTypeEnum(str, Enum):
    corn = "corn"
    soybean = "soybean"
    wheat = "wheat"
    rice = "rice"
    barley = "barley"
    oats = "oats"
    sorghum = "sorghum"
    millet = "millet"
    tomato = "tomato"
    pepper = "pepper"
    lettuce = "lettuce"
    carrot = "carrot"
    onion = "onion"
    potato = "potato"
    sweet_potato = "sweet_potato"
    cabbage = "cabbage"
    broccoli = "broccoli"
    cauliflower = "cauliflower"
    apple = "apple"
    pear = "pear"
    peach = "peach"
    cherry = "cherry"
    grape = "grape"
    strawberry = "strawberry"
    blueberry = "blueberry"
    bean = "bean"
    peas = "peas"
    lentil = "lentil"
    chickpea = "chickpea"
    sunflower = "sunflower"
    canola = "canola"
    cotton = "cotton"
    alfalfa = "alfalfa"
    clover = "clover"
    grass_hay = "grass_hay"
    sugar_beet = "sugar_beet"
    sugar_cane = "sugar_cane"
    tobacco = "tobacco"

class GrowthStageEnum(str, Enum):
    germination = "germination"
    emergence = "emergence"
    seedling = "seedling"
    vegetative_1 = "vegetative_1"
    vegetative_2 = "vegetative_2"
    vegetative_3 = "vegetative_3"
    flowering = "flowering"
    pollination = "pollination"
    fruit_set = "fruit_set"
    maturity = "maturity"
    harvest = "harvest"
    v1 = "v1"
    v2 = "v2"
    v3 = "v3"
    v4 = "v4"
    v5 = "v5"
    v6 = "v6"
    vt = "vt"
    r1 = "r1"
    r2 = "r2"
    r3 = "r3"
    r4 = "r4"
    r5 = "r5"
    r6 = "r6"
    ve = "ve"
    vc = "vc"
    v1_soy = "v1_soy"
    v2_soy = "v2_soy"
    v3_soy = "v3_soy"
    v4_soy = "v4_soy"
    v5_soy = "v5_soy"
    v6_soy = "v6_soy"
    r1_soy = "r1_soy"
    r2_soy = "r2_soy"
    r3_soy = "r3_soy"
    r4_soy = "r4_soy"
    r5_soy = "r5_soy"
    r6_soy = "r6_soy"
    r7_soy = "r7_soy"
    r8_soy = "r8_soy"
    tillering = "tillering"
    jointing = "jointing"

# Response models as dictionaries to avoid complex Pydantic model dependencies
@router.get("/supported-crops", 
            summary="Get all supported crop types",
            description="Returns a list of all crop types supported by the crop integration system.")
async def get_supported_crops() -> List[str]:
    """
    Get a list of all supported crop types in the system.
    """
    try:
        crops = service.get_supported_crops()
        return [crop.value for crop in crops]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving supported crops: {str(e)}")

@router.get("/crop-info/{crop_type}", 
            summary="Get detailed crop information",
            description="Returns comprehensive information about a specific crop type.")
async def get_crop_info(crop_type: CropTypeEnum) -> Dict[str, Any]:
    """
    Get detailed information about a specific crop type.
    """
    try:
        parsed_crop_type = CropType(crop_type.value)
        crop_info = service.get_crop_info(parsed_crop_type)
        
        if not crop_info:
            raise HTTPException(status_code=404, detail=f"Crop type '{crop_type.value}' not found")
        
        return crop_info
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid crop type: {crop_type.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving crop info: {str(e)}")

@router.get("/supported-growth-stages/{crop_type}", 
            summary="Get supported growth stages for a crop",
            description="Returns a list of all supported growth stages for a specific crop type.")
async def get_supported_growth_stages(crop_type: CropTypeEnum) -> List[str]:
    """
    Get supported growth stages for a specific crop type.
    """
    try:
        parsed_crop_type = CropType(crop_type.value)
        stages = service.get_supported_growth_stages(parsed_crop_type)
        return [stage.value for stage in stages]
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid crop type: {crop_type.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving growth stages: {str(e)}")

@router.get("/growth-stage-info/{crop_type}/{growth_stage}", 
            summary="Get detailed growth stage information",
            description="Returns detailed information about a specific growth stage for a crop.")
async def get_growth_stage_info(crop_type: CropTypeEnum, growth_stage: GrowthStageEnum) -> Dict[str, Any]:
    """
    Get detailed information about a specific growth stage for a crop.
    """
    try:
        parsed_crop_type = CropType(crop_type.value)
        parsed_growth_stage = GrowthStage(growth_stage.value)
        
        stage_info = service.get_growth_stage_info(parsed_crop_type, parsed_growth_stage)
        
        if not stage_info:
            raise HTTPException(
                status_code=404, 
                detail=f"Growth stage '{growth_stage.value}' for crop '{crop_type.value}' not found"
            )
        
        # Convert the CropGrowthStageInfo object to a dictionary
        return {
            "stage_name": stage_info.stage_name,
            "stage_code": stage_info.stage_code,
            "description": stage_info.description,
            "days_from_planting": list(stage_info.days_from_planting),
            "nutrient_demand_level": stage_info.nutrient_demand_level,
            "application_sensitivity": stage_info.application_sensitivity,
            "recommended_methods": stage_info.recommended_methods,
            "avoided_methods": stage_info.avoided_methods,
            "timing_preferences": stage_info.timing_preferences
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid crop type or growth stage: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving growth stage info: {str(e)}")

@router.get("/application-preferences/{crop_type}", 
            summary="Get crop-specific application preferences",
            description="Returns application method preferences for a specific crop type.")
async def get_application_preferences(crop_type: CropTypeEnum) -> Dict[str, Any]:
    """
    Get crop-specific application method preferences.
    """
    try:
        parsed_crop_type = CropType(crop_type.value)
        preferences = service.get_application_preferences(parsed_crop_type)
        
        if not preferences:
            raise HTTPException(status_code=404, detail=f"Application preferences for crop '{crop_type.value}' not found")
        
        # Convert the CropApplicationPreferences object to a dictionary
        return {
            "crop_type": preferences.crop_type.value,
            "preferred_methods": preferences.preferred_methods,
            "avoided_methods": preferences.avoided_methods,
            "sensitivity_factors": preferences.sensitivity_factors,
            "nutrient_uptake_pattern": preferences.nutrient_uptake_pattern,
            "application_timing_critical_stages": preferences.application_timing_critical_stages
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid crop type: {crop_type.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving application preferences: {str(e)}")

@router.get("/recommended-methods/{crop_type}/{growth_stage}", 
            summary="Get recommended application methods for crop and growth stage",
            description="Returns recommended application methods for a specific crop and growth stage combination.")
async def get_recommended_methods(crop_type: CropTypeEnum, growth_stage: GrowthStageEnum) -> List[str]:
    """
    Get recommended application methods for a specific crop and growth stage.
    """
    try:
        parsed_crop_type = CropType(crop_type.value)
        parsed_growth_stage = GrowthStage(growth_stage.value)
        
        recommended_methods = service.get_recommended_methods_for_stage(parsed_crop_type, parsed_growth_stage)
        return recommended_methods
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid crop type or growth stage: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving recommended methods: {str(e)}")

@router.get("/avoided-methods/{crop_type}/{growth_stage}", 
            summary="Get avoided application methods for crop and growth stage",
            description="Returns application methods to avoid for a specific crop and growth stage combination.")
async def get_avoided_methods(crop_type: CropTypeEnum, growth_stage: GrowthStageEnum) -> List[str]:
    """
    Get application methods to avoid for a specific crop and growth stage.
    """
    try:
        parsed_crop_type = CropType(crop_type.value)
        parsed_growth_stage = GrowthStage(growth_stage.value)
        
        avoided_methods = service.get_avoided_methods_for_stage(parsed_crop_type, parsed_growth_stage)
        return avoided_methods
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid crop type or growth stage: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving avoided methods: {str(e)}")

@router.get("/critical-application-windows/{crop_type}", 
            summary="Get critical application windows for a crop",
            description="Returns critical application windows for a specific crop type.")
async def get_critical_application_windows(crop_type: CropTypeEnum) -> Dict[str, List[int]]:
    """
    Get critical application windows for a specific crop type.
    """
    try:
        parsed_crop_type = CropType(crop_type.value)
        windows = service.get_critical_application_windows(parsed_crop_type)
        # Convert tuples to lists for JSON serialization
        return {key: list(value) for key, value in windows.items()}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid crop type: {crop_type.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving critical application windows: {str(e)}")

@router.post("/calculate-timing-score", 
            summary="Calculate application timing score",
            description="Calculates a timing score for a specific crop, growth stage, method, and timing.")
async def calculate_timing_score(
    crop_type: CropTypeEnum = Query(..., description="Crop type"),
    growth_stage: GrowthStageEnum = Query(..., description="Growth stage"),
    method_type: str = Query(..., description="Application method type"),
    days_from_planting: int = Query(..., ge=0, le=365, description="Days from planting")
) -> float:
    """
    Calculate timing score for application method based on crop and growth stage.
    Returns a score between 0.0 and 1.0, where higher scores indicate better timing.
    """
    try:
        parsed_crop_type = CropType(crop_type.value)
        parsed_growth_stage = GrowthStage(growth_stage.value)
        
        score = service.calculate_application_timing_score(
            parsed_crop_type, parsed_growth_stage, method_type, days_from_planting
        )
        return score
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid crop type or growth stage: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating timing score: {str(e)}")

@router.get("/nutrient-uptake-curve/{crop_type}/{nutrient}", 
            summary="Get nutrient uptake curve for a crop",
            description="Returns the nutrient uptake curve for a specific crop and nutrient.")
async def get_nutrient_uptake_curve(crop_type: CropTypeEnum, nutrient: str) -> List[float]:
    """
    Get nutrient uptake curve for a specific crop and nutrient.
    Returns a list of 10 values representing uptake from early to late season.
    """
    try:
        parsed_crop_type = CropType(crop_type.value)
        uptake_curve = service.get_nutrient_uptake_curve(parsed_crop_type, nutrient)
        return uptake_curve
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid crop type: {crop_type.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving nutrient uptake curve: {str(e)}")

@router.get("/method-compatibility/{crop_type}/{method_type}", 
            summary="Assess crop-method compatibility",
            description="Assesses compatibility between a crop type and an application method.")
async def assess_crop_method_compatibility(crop_type: CropTypeEnum, method_type: str) -> Dict[str, Any]:
    """
    Assess compatibility between crop type and application method.
    """
    try:
        parsed_crop_type = CropType(crop_type.value)
        compatibility = service.assess_crop_method_compatibility(parsed_crop_type, method_type)
        return compatibility
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid crop type: {crop_type.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assessing compatibility: {str(e)}")

@router.get("/health", 
            summary="Health check for crop integration service",
            description="Health check endpoint for the crop integration service.")
async def health_check():
    """
    Health check for the crop integration service.
    """
    try:
        # Test basic functionality
        supported_crops = service.get_supported_crops()
        if len(supported_crops) > 0:
            return {"status": "healthy", "service": "crop-integration", "supported_crops": len(supported_crops)}
        else:
            raise HTTPException(status_code=500, detail="Service is not healthy: no crops available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")