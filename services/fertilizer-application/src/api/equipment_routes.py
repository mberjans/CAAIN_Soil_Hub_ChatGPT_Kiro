"""
API routes for equipment assessment and farm infrastructure evaluation.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
import logging
from uuid import uuid4

from src.models.application_models import (
    EquipmentAssessmentRequest, 
    EquipmentAssessmentResponse,
    EquipmentSpecification,
    EquipmentType
)
from src.models.equipment_models import (
    Equipment, EquipmentCategory, EquipmentStatus, MaintenanceLevel,
    EquipmentInventory, EquipmentCompatibility, EquipmentEfficiency,
    EquipmentUpgrade, EquipmentAssessment, EquipmentMaintenance
)
from src.services.equipment_assessment_service import EquipmentAssessmentService
from src.database.fertilizer_db import get_db_session, EquipmentAssessmentRecord

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/equipment", tags=["equipment-assessment"])


# Dependency injection
async def get_equipment_service() -> EquipmentAssessmentService:
    """Get equipment assessment service instance."""
    return EquipmentAssessmentService()


@router.post("/assess-farm", response_model=EquipmentAssessmentResponse)
async def assess_farm_equipment(
    request: EquipmentAssessmentRequest,
    service: EquipmentAssessmentService = Depends(get_equipment_service)
):
    """
    Perform comprehensive equipment assessment for a farm.
    
    This endpoint provides detailed analysis of farm equipment including:
    - Equipment inventory assessment
    - Capacity analysis and adequacy evaluation
    - Compatibility assessment with farm operations
    - Efficiency analysis and optimization opportunities
    - Upgrade recommendations with cost-benefit analysis
    - Maintenance requirements and scheduling
    
    **Farm Assessment Areas:**
    - Farm size categorization and field analysis
    - Equipment intensity and operational requirements
    - Labor and maintenance capability assessment
    - Budget constraints and upgrade priorities
    
    **Equipment Categories Analyzed:**
    - Spreading equipment (granular fertilizers)
    - Spraying equipment (liquid fertilizers)
    - Injection systems (liquid fertilizers)
    - Irrigation systems (fertigation)
    - Handling and storage equipment
    
    **Assessment Outputs:**
    - Individual equipment suitability scores
    - Capacity adequacy for farm operations
    - Efficiency ratings and optimization opportunities
    - Upgrade recommendations with ROI analysis
    - Maintenance schedules and requirements
    - Overall farm equipment score
    """
    try:
        logger.info(f"Processing farm equipment assessment request")
        
        # Perform comprehensive equipment assessment
        assessment_response = await service.assess_farm_equipment(request)
        
        # Store assessment record in database
        await _store_assessment_record(request, assessment_response)
        
        logger.info(f"Farm equipment assessment completed successfully")
        return assessment_response
        
    except Exception as e:
        logger.error(f"Error in farm equipment assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Equipment assessment failed: {str(e)}")


@router.get("/assessment/{request_id}", response_model=EquipmentAssessmentResponse)
async def get_assessment_result(
    request_id: str,
    service: EquipmentAssessmentService = Depends(get_equipment_service)
):
    """
    Retrieve equipment assessment results by request ID.
    
    This endpoint allows retrieval of previously completed equipment assessments
    for review, comparison, or integration with other farm management systems.
    """
    try:
        # Retrieve assessment from database
        db_session = await get_db_session()
        assessment_record = await db_session.query(EquipmentAssessmentRecord).filter(
            EquipmentAssessmentRecord.request_id == request_id
        ).first()
        
        if not assessment_record:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Reconstruct response from stored data
        response = EquipmentAssessmentResponse(
            request_id=assessment_record.request_id,
            farm_assessment={
                "farm_size_acres": assessment_record.farm_size_acres,
                "field_count": assessment_record.field_count,
                "average_field_size": assessment_record.average_field_size
            },
            equipment_assessments=assessment_record.equipment_inventory or [],
            upgrade_priorities=assessment_record.upgrade_recommendations or [],
            capacity_analysis=assessment_record.capacity_analysis or {},
            cost_benefit_analysis=assessment_record.cost_benefit_analysis,
            processing_time_ms=assessment_record.processing_time_ms
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve assessment: {str(e)}")


@router.get("/categories", response_model=List[Dict[str, Any]])
async def get_equipment_categories():
    """
    Get available equipment categories and their specifications.
    
    This endpoint provides information about all supported equipment categories
    including their typical specifications, capacity ranges, and use cases.
    """
    categories = [
        {
            "category": EquipmentCategory.SPREADING,
            "name": "Spreading Equipment",
            "description": "Equipment for applying granular fertilizers",
            "typical_capacity_range": "100-5000 cubic feet",
            "use_cases": ["Broadcast application", "Band application", "Organic fertilizers"],
            "compatible_fertilizers": ["Granular", "Organic", "Pelleted"],
            "efficiency_factors": ["Spread width", "Application rate accuracy", "Ground speed"]
        },
        {
            "category": EquipmentCategory.SPRAYING,
            "name": "Spraying Equipment",
            "description": "Equipment for applying liquid fertilizers",
            "typical_capacity_range": "50-5000 gallons",
            "use_cases": ["Foliar application", "Broadcast spraying", "Precision application"],
            "compatible_fertilizers": ["Liquid", "Soluble", "Suspension"],
            "efficiency_factors": ["Boom width", "Nozzle efficiency", "Pressure control"]
        },
        {
            "category": EquipmentCategory.INJECTION,
            "name": "Injection Systems",
            "description": "Equipment for injecting liquid fertilizers into soil",
            "typical_capacity_range": "25-1000 gph",
            "use_cases": ["Side-dress application", "Deep injection", "Precision placement"],
            "compatible_fertilizers": ["Liquid", "Soluble", "Anhydrous ammonia"],
            "efficiency_factors": ["Injection depth", "Flow rate", "Pressure control"]
        },
        {
            "category": EquipmentCategory.IRRIGATION,
            "name": "Irrigation Systems",
            "description": "Equipment for fertigation and irrigation",
            "typical_capacity_range": "5-1000 acres",
            "use_cases": ["Fertigation", "Drip irrigation", "Center pivot systems"],
            "compatible_fertilizers": ["Liquid", "Soluble", "Water-soluble"],
            "efficiency_factors": ["System coverage", "Water efficiency", "Fertigation capability"]
        },
        {
            "category": EquipmentCategory.HANDLING,
            "name": "Handling Equipment",
            "description": "Equipment for fertilizer handling and transport",
            "typical_capacity_range": "1-50 tons",
            "use_cases": ["Loading", "Transport", "Storage management"],
            "compatible_fertilizers": ["All types"],
            "efficiency_factors": ["Loading speed", "Transport capacity", "Safety features"]
        },
        {
            "category": EquipmentCategory.STORAGE,
            "name": "Storage Equipment",
            "description": "Equipment for fertilizer storage and management",
            "typical_capacity_range": "10-1000 tons",
            "use_cases": ["Bulk storage", "Conditioning", "Inventory management"],
            "compatible_fertilizers": ["All types"],
            "efficiency_factors": ["Storage capacity", "Conditioning capability", "Access efficiency"]
        }
    ]
    
    return categories


@router.get("/benchmarks", response_model=Dict[str, Any])
async def get_equipment_benchmarks():
    """
    Get comprehensive equipment performance benchmarks and industry standards.
    
    This endpoint provides industry benchmarks for equipment performance,
    capacity requirements, efficiency standards, and operational metrics
    to help farmers evaluate their equipment against industry standards.
    """
    benchmarks = {
        "capacity_benchmarks": {
            EquipmentCategory.SPREADING: {
                "small_farm": {"min": 0, "max": 500, "optimal": 250},
                "medium_farm": {"min": 500, "max": 1500, "optimal": 1000},
                "large_farm": {"min": 1500, "max": 3000, "optimal": 2250},
                "very_large_farm": {"min": 3000, "max": 10000, "optimal": 5000}
            },
            EquipmentCategory.SPRAYING: {
                "small_farm": {"min": 0, "max": 100, "optimal": 50},
                "medium_farm": {"min": 100, "max": 500, "optimal": 300},
                "large_farm": {"min": 500, "max": 1000, "optimal": 750},
                "very_large_farm": {"min": 1000, "max": 5000, "optimal": 2500}
            },
            EquipmentCategory.INJECTION: {
                "small_farm": {"min": 0, "max": 50, "optimal": 25},
                "medium_farm": {"min": 50, "max": 200, "optimal": 125},
                "large_farm": {"min": 200, "max": 500, "optimal": 350},
                "very_large_farm": {"min": 500, "max": 1000, "optimal": 750}
            },
            EquipmentCategory.IRRIGATION: {
                "small_farm": {"min": 0, "max": 10, "optimal": 5},
                "medium_farm": {"min": 10, "max": 50, "optimal": 30},
                "large_farm": {"min": 50, "max": 200, "optimal": 125},
                "very_large_farm": {"min": 200, "max": 1000, "optimal": 500}
            }
        },
        "efficiency_standards": {
            "application_accuracy": {"excellent": 0.95, "good": 0.85, "acceptable": 0.75},
            "fuel_efficiency": {"excellent": 0.9, "good": 0.8, "acceptable": 0.7},
            "labor_efficiency": {"excellent": 0.9, "good": 0.8, "acceptable": 0.7},
            "maintenance_efficiency": {"excellent": 0.9, "good": 0.8, "acceptable": 0.7}
        },
        "farm_size_categories": {
            "small": {"min_acres": 0, "max_acres": 100, "typical_fields": "1-5"},
            "medium": {"min_acres": 100, "max_acres": 500, "typical_fields": "5-15"},
            "large": {"min_acres": 500, "max_acres": 2000, "typical_fields": "15-50"},
            "very_large": {"min_acres": 2000, "max_acres": 10000, "typical_fields": "50+"}
        },
        "maintenance_levels": {
            MaintenanceLevel.BASIC: {
                "description": "Basic maintenance that can be performed by farm operators",
                "typical_tasks": ["Cleaning", "Lubrication", "Basic inspection"],
                "frequency": "Weekly to monthly",
                "skill_required": "Basic mechanical knowledge"
            },
            MaintenanceLevel.INTERMEDIATE: {
                "description": "Intermediate maintenance requiring some mechanical skills",
                "typical_tasks": ["Calibration", "Component replacement", "System adjustment"],
                "frequency": "Monthly to quarterly",
                "skill_required": "Intermediate mechanical skills"
            },
            MaintenanceLevel.ADVANCED: {
                "description": "Advanced maintenance requiring specialized knowledge",
                "typical_tasks": ["Major repairs", "System overhaul", "Precision calibration"],
                "frequency": "Quarterly to annually",
                "skill_required": "Advanced mechanical skills"
            },
            MaintenanceLevel.PROFESSIONAL: {
                "description": "Professional maintenance requiring certified technicians",
                "typical_tasks": ["Major overhauls", "Specialized repairs", "Certification work"],
                "frequency": "Annually or as needed",
                "skill_required": "Professional certification"
            }
        },
        # Enhanced performance benchmarks
        "performance_benchmarks": {
            "operational_efficiency": {
                "excellent": 0.9,
                "good": 0.8,
                "acceptable": 0.7,
                "needs_improvement": 0.6
            },
            "environmental_performance": {
                "excellent": 0.9,
                "good": 0.8,
                "acceptable": 0.7,
                "needs_improvement": 0.6
            },
            "cost_effectiveness": {
                "excellent": 0.9,
                "good": 0.8,
                "acceptable": 0.7,
                "needs_improvement": 0.6
            }
        },
        "industry_standards": {
            "fuel_consumption": {
                "spreading": {"gallons_per_hour": 2.5, "gallons_per_acre": 0.5},
                "spraying": {"gallons_per_hour": 3.0, "gallons_per_acre": 0.6},
                "injection": {"gallons_per_hour": 1.5, "gallons_per_acre": 0.3},
                "irrigation": {"gallons_per_hour": 1.0, "gallons_per_acre": 0.2}
            },
            "application_rates": {
                "spreading": {"lbs_per_acre": 200, "accuracy_percent": 95},
                "spraying": {"gallons_per_acre": 20, "accuracy_percent": 90},
                "injection": {"gallons_per_acre": 10, "accuracy_percent": 95},
                "irrigation": {"gallons_per_acre": 5, "accuracy_percent": 98}
            },
            "maintenance_costs": {
                "annual_percentage": 5.0,
                "preventive_percentage": 60.0,
                "corrective_percentage": 40.0
            }
        },
        "sustainability_metrics": {
            "emissions_standards": {
                "tier_4_final": {"nox_g_per_kwh": 0.4, "pm_g_per_kwh": 0.02},
                "tier_3": {"nox_g_per_kwh": 2.0, "pm_g_per_kwh": 0.1},
                "tier_2": {"nox_g_per_kwh": 4.0, "pm_g_per_kwh": 0.2}
            },
            "noise_standards": {
                "operational": {"db_level": 85, "exposure_hours": 8},
                "residential": {"db_level": 55, "exposure_hours": 24}
            },
            "fuel_efficiency": {
                "excellent": {"gallons_per_hour": 2.0, "gallons_per_acre": 0.4},
                "good": {"gallons_per_hour": 3.0, "gallons_per_acre": 0.6},
                "acceptable": {"gallons_per_hour": 4.0, "gallons_per_acre": 0.8}
            }
        }
    }
    
    return benchmarks


@router.post("/compatibility-check")
async def check_equipment_compatibility(
    equipment_list: List[EquipmentSpecification],
    farm_size_acres: float = Query(..., ge=0.1, le=10000.0),
    field_count: int = Query(..., ge=1),
    service: EquipmentAssessmentService = Depends(get_equipment_service)
):
    """
    Check compatibility of equipment with farm operations.
    
    This endpoint provides quick compatibility assessment for equipment
    without performing a full farm assessment. Useful for evaluating
    specific equipment purchases or upgrades.
    """
    try:
        # Convert EquipmentSpecification to Equipment for compatibility assessment
        equipment_objects = []
        for i, spec in enumerate(equipment_list):
            # Map EquipmentType to EquipmentCategory
            category_mapping = {
                EquipmentType.SPREADER: EquipmentCategory.SPREADING,
                EquipmentType.SPRAYER: EquipmentCategory.SPRAYING,
                EquipmentType.INJECTOR: EquipmentCategory.INJECTION,
                EquipmentType.DRIP_SYSTEM: EquipmentCategory.IRRIGATION,
                EquipmentType.HAND_SPREADER: EquipmentCategory.SPREADING,
                EquipmentType.BROADCASTER: EquipmentCategory.SPREADING
            }
            
            equipment = Equipment(
                equipment_id=f"spec_{i}",
                name=f"{spec.equipment_type} Equipment",
                category=category_mapping.get(spec.equipment_type, EquipmentCategory.SPREADING),
                capacity=spec.capacity,
                status=EquipmentStatus.OPERATIONAL,
                maintenance_level=MaintenanceLevel.BASIC
            )
            equipment_objects.append(equipment)
        
        # Create a minimal request for compatibility checking
        request = EquipmentAssessmentRequest(
            farm_size_acres=farm_size_acres,
            field_count=field_count,
            average_field_size=farm_size_acres / field_count,
            current_equipment=equipment_list
        )
        
        # Perform compatibility assessment
        farm_analysis = await service._analyze_farm_characteristics(request)
        compatibility_assessments = await service._generate_compatibility_assessments(
            equipment_objects, farm_analysis
        )
        
        return {
            "farm_analysis": farm_analysis,
            "compatibility_assessments": compatibility_assessments,
            "overall_compatibility_score": sum(c.compatibility_score for c in compatibility_assessments) / len(compatibility_assessments) if compatibility_assessments else 0
        }
        
    except Exception as e:
        logger.error(f"Error in compatibility check: {e}")
        raise HTTPException(status_code=500, detail=f"Compatibility check failed: {str(e)}")


@router.get("/upgrade-recommendations/{equipment_id}")
async def get_upgrade_recommendations(
    equipment_id: str,
    farm_size_acres: float = Query(..., ge=0.1, le=10000.0),
    budget_constraints: Optional[float] = Query(None, ge=0),
    service: EquipmentAssessmentService = Depends(get_equipment_service)
):
    """
    Get upgrade recommendations for specific equipment.
    
    This endpoint provides targeted upgrade recommendations for individual
    equipment items, including cost estimates, expected benefits, and
    payback period analysis.
    """
    try:
        # This would typically retrieve equipment from database
        # For now, return a placeholder response
        return {
            "equipment_id": equipment_id,
            "upgrade_recommendations": [
                {
                    "priority": "high",
                    "recommendation": "Upgrade to higher capacity model",
                    "estimated_cost": 50000,
                    "expected_benefits": ["Increased efficiency", "Reduced downtime"],
                    "payback_period": 3.5
                }
            ],
            "budget_analysis": {
                "total_cost": 50000,
                "budget_constraints": budget_constraints,
                "affordable": budget_constraints is None or budget_constraints >= 50000
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting upgrade recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get upgrade recommendations: {str(e)}")


@router.post("/performance-comparison")
async def compare_equipment_performance(
    equipment_list: List[EquipmentSpecification],
    service: EquipmentAssessmentService = Depends(get_equipment_service)
):
    """
    Compare equipment performance against industry benchmarks.
    
    This endpoint provides detailed comparison of equipment performance
    against industry standards and benchmarks, helping farmers understand
    how their equipment measures up to industry norms.
    """
    try:
        # Convert equipment specifications to equipment objects
        equipment_objects = []
        for i, spec in enumerate(equipment_list):
            # Map EquipmentType to EquipmentCategory
            category_mapping = {
                EquipmentType.SPREADER: EquipmentCategory.SPREADING,
                EquipmentType.SPRAYER: EquipmentCategory.SPRAYING,
                EquipmentType.INJECTOR: EquipmentCategory.INJECTION,
                EquipmentType.DRIP_SYSTEM: EquipmentCategory.IRRIGATION,
                EquipmentType.HAND_SPREADER: EquipmentCategory.SPREADING,
                EquipmentType.BROADCASTER: EquipmentCategory.SPREADING
            }
            
            equipment = Equipment(
                equipment_id=f"spec_{i}",
                name=f"{spec.equipment_type} Equipment",
                category=category_mapping.get(spec.equipment_type, EquipmentCategory.SPREADING),
                capacity=spec.capacity,
                status=EquipmentStatus.OPERATIONAL,
                maintenance_level=MaintenanceLevel.BASIC
            )
            equipment_objects.append(equipment)
        
        # Perform performance comparison
        comparison_results = []
        for equipment in equipment_objects:
            comparison = {
                "equipment_id": equipment.equipment_id,
                "equipment_category": equipment.category,
                "performance_metrics": {
                    "fuel_efficiency": service._calculate_fuel_efficiency_rating(equipment),
                    "environmental_impact": service._calculate_environmental_impact_score(equipment),
                    "operational_efficiency": service._calculate_efficiency_rating(equipment)
                },
                "benchmark_comparison": service._compare_to_benchmarks(equipment),
                "industry_ranking": service._calculate_industry_ranking(equipment),
                "improvement_opportunities": service._identify_performance_improvements(equipment)
            }
            comparison_results.append(comparison)
        
        return {
            "comparison_results": comparison_results,
            "overall_farm_performance": service._calculate_overall_farm_performance(comparison_results),
            "benchmark_summary": service._generate_benchmark_summary(comparison_results)
        }
        
    except Exception as e:
        logger.error(f"Error in performance comparison: {e}")
        raise HTTPException(status_code=500, detail=f"Performance comparison failed: {str(e)}")


async def _store_assessment_record(
    request: EquipmentAssessmentRequest, 
    response: EquipmentAssessmentResponse
):
    """Store equipment assessment record in database."""
    try:
        db_session = await get_db_session()
        
        assessment_record = EquipmentAssessmentRecord(
            request_id=response.request_id,
            farm_id="current_farm",  # Would be passed from request in real implementation
            assessment_date=str(response.metadata.get("assessment_date", "")),
            farm_size_acres=request.farm_size_acres,
            field_count=request.field_count,
            average_field_size=request.average_field_size,
            equipment_inventory=response.equipment_assessments,
            compatibility_assessments=response.metadata.get("compatibility_assessments", []),
            efficiency_assessments=response.metadata.get("efficiency_assessments", []),
            upgrade_recommendations=response.upgrade_priorities,
            capacity_analysis=response.capacity_analysis,
            cost_benefit_analysis=response.cost_benefit_analysis,
            overall_score=response.metadata.get("overall_score", 0.0),
            processing_time_ms=response.processing_time_ms
        )
        
        db_session.add(assessment_record)
        await db_session.commit()
        
    except Exception as e:
        logger.warning(f"Failed to store assessment record: {e}")
        # Don't raise exception as this is not critical for the main functionality