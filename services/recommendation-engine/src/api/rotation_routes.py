"""
Crop Rotation Planning API Routes
FastAPI routes for crop rotation planning and field history management.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging
from datetime import datetime, date

from ..models.rotation_models import (
    FieldHistoryRequest, RotationGoalRequest, RotationConstraintRequest,
    RotationPlanRequest, RotationPlanResponse, RotationAnalysisResponse
)
from ..services.field_history_service import field_history_service
from ..services.rotation_optimization_engine import rotation_optimization_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rotations", tags=["crop-rotation"])


# Additional request/response models
class FieldProfileRequest(BaseModel):
    """Request to create field profile."""
    field_name: str
    farm_id: str
    size_acres: float
    soil_type: Optional[str] = None
    drainage_class: Optional[str] = None
    slope_percent: Optional[float] = None
    irrigation_available: bool = False
    coordinates: Optional[tuple] = None
    climate_zone: Optional[str] = None
    elevation_ft: Optional[float] = None


class BulkHistoryImportRequest(BaseModel):
    """Request for bulk history import."""
    field_id: str
    history_records: List[Dict]


class RotationComparisonRequest(BaseModel):
    """Request to compare rotation scenarios."""
    field_id: str
    rotation_scenarios: List[List[str]]
    goals: List[RotationGoalRequest]
    constraints: List[RotationConstraintRequest] = []


# Field History Management Endpoints

@router.post("/fields", status_code=status.HTTP_201_CREATED)
async def create_field_profile(request: FieldProfileRequest):
    """Create a new field profile for rotation planning."""
    try:
        field_id = f"field_{request.farm_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        field_characteristics = {
            'size_acres': request.size_acres,
            'soil_type': request.soil_type,
            'drainage_class': request.drainage_class,
            'slope_percent': request.slope_percent,
            'irrigation_available': request.irrigation_available,
            'coordinates': request.coordinates,
            'climate_zone': request.climate_zone,
            'elevation_ft': request.elevation_ft
        }
        
        field_profile = await field_history_service.create_field_profile(
            field_id=field_id,
            field_name=request.field_name,
            farm_id=request.farm_id,
            field_characteristics=field_characteristics
        )
        
        return {
            "field_id": field_id,
            "field_name": field_profile.field_name,
            "farm_id": field_profile.farm_id,
            "created_date": field_profile.last_updated.isoformat(),
            "message": "Field profile created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating field profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create field profile: {str(e)}")


@router.post("/fields/{field_id}/history", status_code=status.HTTP_201_CREATED)
async def add_field_history(field_id: str, history_data: FieldHistoryRequest):
    """Add field history record."""
    try:
        history_record = await field_history_service.add_field_history_record(
            field_id=field_id,
            history_data=history_data
        )
        
        return {
            "field_id": field_id,
            "year": history_record.year,
            "crop_name": history_record.crop_name,
            "message": "Field history record added successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding field history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add field history: {str(e)}")


@router.get("/fields/{field_id}/history")
async def get_field_history(
    field_id: str,
    start_year: Optional[int] = Query(None, description="Start year for history range"),
    end_year: Optional[int] = Query(None, description="End year for history range")
):
    """Get field history records."""
    try:
        history_records = await field_history_service.get_field_history(
            field_id=field_id,
            start_year=start_year,
            end_year=end_year
        )
        
        # Convert to response format
        history_data = []
        for record in history_records:
            history_data.append({
                "year": record.year,
                "crop_name": record.crop_name,
                "variety": record.variety,
                "planting_date": record.planting_date.isoformat() if record.planting_date else None,
                "harvest_date": record.harvest_date.isoformat() if record.harvest_date else None,
                "yield_amount": record.yield_amount,
                "yield_units": record.yield_units,
                "tillage_type": record.tillage_type,
                "irrigation_used": record.irrigation_used,
                "cover_crop": record.cover_crop,
                "gross_revenue": record.gross_revenue,
                "total_costs": record.total_costs,
                "net_profit": record.net_profit,
                "notes": record.notes
            })
        
        return {
            "field_id": field_id,
            "history_records": history_data,
            "total_records": len(history_data),
            "year_range": {
                "start": min(r["year"] for r in history_data) if history_data else None,
                "end": max(r["year"] for r in history_data) if history_data else None
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting field history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get field history: {str(e)}")


@router.put("/fields/{field_id}/history/{year}")
async def update_field_history(field_id: str, year: int, updates: Dict[str, Any]):
    """Update field history record."""
    try:
        updated_record = await field_history_service.update_field_history_record(
            field_id=field_id,
            year=year,
            updates=updates
        )
        
        return {
            "field_id": field_id,
            "year": year,
            "updated_fields": list(updates.keys()),
            "message": "Field history record updated successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating field history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update field history: {str(e)}")


@router.delete("/fields/{field_id}/history/{year}")
async def delete_field_history(field_id: str, year: int):
    """Delete field history record."""
    try:
        success = await field_history_service.delete_field_history_record(
            field_id=field_id,
            year=year
        )
        
        if success:
            return {
                "field_id": field_id,
                "year": year,
                "message": "Field history record deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="History record not found")
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting field history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete field history: {str(e)}")


@router.post("/fields/{field_id}/bulk-import")
async def bulk_import_history(field_id: str, request: BulkHistoryImportRequest):
    """Bulk import field history records."""
    try:
        results = await field_history_service.bulk_import_history(
            field_id=field_id,
            history_records=request.history_records
        )
        
        return {
            "field_id": field_id,
            "import_results": results,
            "message": f"Bulk import completed: {results['summary']['successful_imports']}/{results['summary']['total_records']} records imported"
        }
        
    except Exception as e:
        logger.error(f"Error in bulk import: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk import failed: {str(e)}")


# Rotation Planning Endpoints

@router.post("/generate", response_model=RotationPlanResponse)
async def generate_rotation_plan(request: RotationPlanRequest):
    """Generate optimal crop rotation plan."""
    try:
        logger.info(f"Generating rotation plan for field {request.field_id}")
        
        # Get field profile (in production, from database)
        field_profile = field_history_service.field_profiles.get(request.field_id)
        if not field_profile:
            raise HTTPException(status_code=404, detail=f"Field {request.field_id} not found")
        
        # Convert request models to domain models
        goals = []
        for goal_req in request.goals:
            goal = RotationGoal(
                goal_id=f"goal_{len(goals)}",
                goal_type=goal_req.goal_type,
                priority=goal_req.priority,
                weight=goal_req.weight,
                target_value=goal_req.target_value,
                target_units=goal_req.target_units,
                target_timeframe=goal_req.target_timeframe,
                description=goal_req.description,
                constraints=goal_req.constraints
            )
            goals.append(goal)
        
        constraints = []
        for constraint_req in request.constraints:
            constraint = RotationConstraint(
                constraint_id=f"constraint_{len(constraints)}",
                constraint_type=constraint_req.constraint_type,
                field_id=constraint_req.field_id,
                description=constraint_req.description,
                is_hard_constraint=constraint_req.is_hard_constraint,
                violation_penalty=constraint_req.violation_penalty,
                parameters=constraint_req.parameters,
                applies_to_years=constraint_req.applies_to_years,
                can_be_relaxed=constraint_req.can_be_relaxed
            )
            constraints.append(constraint)
        
        # Generate rotation plan
        rotation_plan = await rotation_optimization_engine.generate_optimal_rotation(
            field_profile=field_profile,
            goals=goals,
            constraints=constraints,
            planning_horizon=request.planning_horizon
        )
        
        # Convert to response format
        response = RotationPlanResponse(
            plan_id=rotation_plan.plan_id,
            field_id=rotation_plan.field_id,
            plan_name=rotation_plan.plan_name,
            created_date=rotation_plan.created_date,
            rotation_schedule=rotation_plan.rotation_years,
            rotation_details=rotation_plan.rotation_details,
            overall_score=rotation_plan.overall_score or 0.0,
            benefit_scores=rotation_plan.benefit_scores,
            economic_projections=rotation_plan.economic_projections or {},
            key_insights=[
                f"Rotation includes {len(set(rotation_plan.get_crop_sequence()))} different crops",
                f"Overall rotation score: {rotation_plan.overall_score:.1f}/100" if rotation_plan.overall_score else "Score calculated",
                "Plan optimized for specified goals and constraints"
            ],
            recommendations=[
                "Monitor soil health improvements over rotation cycle",
                "Adjust fertilizer programs based on nitrogen-fixing crops",
                "Track pest and disease pressure changes"
            ],
            warnings=[]
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating rotation plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate rotation plan: {str(e)}")


@router.get("/plans/{plan_id}")
async def get_rotation_plan(plan_id: str):
    """Get rotation plan details."""
    try:
        # In production, this would fetch from database
        # For now, return placeholder response
        
        return {
            "plan_id": plan_id,
            "message": "Rotation plan retrieval not yet implemented",
            "status": "placeholder"
        }
        
    except Exception as e:
        logger.error(f"Error getting rotation plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get rotation plan: {str(e)}")


@router.put("/plans/{plan_id}")
async def update_rotation_plan(plan_id: str, updates: Dict[str, Any]):
    """Update rotation plan."""
    try:
        # In production, this would update database
        
        return {
            "plan_id": plan_id,
            "updated_fields": list(updates.keys()),
            "message": "Rotation plan updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating rotation plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update rotation plan: {str(e)}")


@router.post("/compare")
async def compare_rotation_scenarios(request: RotationComparisonRequest):
    """Compare multiple rotation scenarios."""
    try:
        logger.info(f"Comparing {len(request.rotation_scenarios)} rotation scenarios")
        
        # Get field profile
        field_profile = field_history_service.field_profiles.get(request.field_id)
        if not field_profile:
            raise HTTPException(status_code=404, detail=f"Field {request.field_id} not found")
        
        comparison_results = []
        
        for i, scenario in enumerate(request.rotation_scenarios):
            # Prepare context for evaluation
            context = rotation_optimization_engine._prepare_optimization_context(
                field_profile, [], [], len(scenario)
            )
            
            # Evaluate scenario
            fitness_score = await rotation_optimization_engine.evaluate_rotation_fitness(
                scenario, context
            )
            
            benefit_scores = await rotation_optimization_engine._calculate_detailed_benefit_scores(
                scenario, context
            )
            
            comparison_results.append({
                "scenario_id": f"scenario_{i + 1}",
                "rotation_sequence": scenario,
                "overall_score": fitness_score,
                "benefit_scores": benefit_scores,
                "crop_diversity": len(set(scenario)),
                "includes_legumes": any(crop in ['soybean', 'alfalfa', 'clover'] for crop in scenario)
            })
        
        # Rank scenarios
        comparison_results.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Add rankings
        for i, result in enumerate(comparison_results):
            result['rank'] = i + 1
        
        return {
            "field_id": request.field_id,
            "comparison_results": comparison_results,
            "best_scenario": comparison_results[0] if comparison_results else None,
            "analysis_summary": {
                "scenarios_compared": len(comparison_results),
                "best_score": comparison_results[0]['overall_score'] if comparison_results else 0,
                "score_range": {
                    "min": min(r['overall_score'] for r in comparison_results) if comparison_results else 0,
                    "max": max(r['overall_score'] for r in comparison_results) if comparison_results else 0
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing rotation scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to compare scenarios: {str(e)}")


# Rotation Analysis Endpoints

@router.post("/analyze-benefits")
async def analyze_rotation_benefits(
    field_id: str = Query(..., description="Field ID"),
    rotation_sequence: List[str] = Query(..., description="Crop rotation sequence")
):
    """Analyze benefits of a specific rotation sequence."""
    try:
        # Get field profile
        field_profile = field_history_service.field_profiles.get(field_id)
        if not field_profile:
            raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
        
        # Prepare context
        context = rotation_optimization_engine._prepare_optimization_context(
            field_profile, [], [], len(rotation_sequence)
        )
        
        # Calculate detailed benefits
        benefit_scores = await rotation_optimization_engine._calculate_detailed_benefit_scores(
            rotation_sequence, context
        )
        
        # Generate benefit explanations
        benefit_explanations = {
            'soil_health': f"Soil health score: {benefit_scores['soil_health']:.1f}/100. "
                          f"Includes {sum(1 for crop in rotation_sequence if crop in ['soybean', 'alfalfa', 'clover'])} nitrogen-fixing crops.",
            'pest_management': f"Pest management score: {benefit_scores['pest_management']:.1f}/100. "
                              f"Crop diversity helps break pest cycles.",
            'nitrogen_fixation': f"Nitrogen benefit: {benefit_scores['nitrogen_fixation']:.1f}/100. "
                                f"Estimated nitrogen fixation from legumes in rotation.",
            'economic_value': f"Economic score: {benefit_scores['economic_value']:.1f}/100. "
                             f"Based on crop profitability and market values.",
            'sustainability': f"Sustainability score: {benefit_scores['sustainability']:.1f}/100. "
                             f"Considers environmental impact and long-term viability."
        }
        
        return {
            "field_id": field_id,
            "rotation_sequence": rotation_sequence,
            "benefit_scores": benefit_scores,
            "benefit_explanations": benefit_explanations,
            "overall_assessment": "excellent" if max(benefit_scores.values()) > 80 else 
                                 "good" if max(benefit_scores.values()) > 60 else "needs_improvement",
            "key_benefits": [
                f"{len(set(rotation_sequence))} crop diversity",
                f"{sum(1 for crop in rotation_sequence if crop in ['soybean', 'alfalfa', 'clover'])} nitrogen-fixing crops",
                "Pest and disease cycle breaks"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing rotation benefits: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze benefits: {str(e)}")


@router.post("/economic-analysis")
async def get_economic_analysis(
    field_id: str = Query(..., description="Field ID"),
    rotation_sequence: List[str] = Query(..., description="Crop rotation sequence"),
    include_market_prices: bool = Query(True, description="Include current market prices")
):
    """Get economic analysis for rotation sequence."""
    try:
        # Simplified economic analysis
        crop_prices = {
            'corn': 4.50,      # $/bu
            'soybean': 12.00,  # $/bu
            'wheat': 6.50,     # $/bu
            'oats': 3.50,      # $/bu
            'alfalfa': 180.00  # $/ton
        }
        
        crop_costs = {
            'corn': 450,       # $/acre
            'soybean': 350,    # $/acre
            'wheat': 300,      # $/acre
            'oats': 250,       # $/acre
            'alfalfa': 400     # $/acre
        }
        
        economic_projections = {}
        total_profit = 0
        
        for year, crop in enumerate(rotation_sequence):
            year_key = datetime.now().year + year
            
            # Estimate yield (simplified)
            estimated_yield = await rotation_optimization_engine._estimate_crop_yield(
                crop, field_history_service.field_profiles.get(field_id), year, rotation_sequence
            )
            
            # Calculate economics
            price = crop_prices.get(crop, 5.00)
            cost = crop_costs.get(crop, 350)
            revenue = estimated_yield * price
            profit = revenue - cost
            
            economic_projections[year_key] = {
                'crop': crop,
                'estimated_yield': estimated_yield,
                'price_per_unit': price,
                'gross_revenue': revenue,
                'total_costs': cost,
                'net_profit': profit,
                'profit_per_acre': profit
            }
            
            total_profit += profit
        
        avg_annual_profit = total_profit / len(rotation_sequence)
        
        return {
            "field_id": field_id,
            "rotation_sequence": rotation_sequence,
            "economic_projections": economic_projections,
            "summary": {
                "total_profit_projection": total_profit,
                "average_annual_profit": avg_annual_profit,
                "planning_horizon_years": len(rotation_sequence),
                "profit_per_acre_per_year": avg_annual_profit
            },
            "market_assumptions": {
                "crop_prices_used": crop_prices,
                "cost_estimates_used": crop_costs,
                "price_date": datetime.now().isoformat(),
                "note": "Prices are estimates and subject to market volatility"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in economic analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Economic analysis failed: {str(e)}")


@router.get("/fields/{field_id}/data-quality")
async def assess_field_data_quality(field_id: str):
    """Assess quality of field history data."""
    try:
        quality_assessment = await field_history_service.assess_data_quality(field_id)
        
        return {
            "field_id": field_id,
            "data_quality_assessment": quality_assessment,
            "recommendations": quality_assessment.get('recommendations', []),
            "readiness_for_planning": "ready" if quality_assessment['overall_score'] > 0.7 else 
                                    "needs_improvement" if quality_assessment['overall_score'] > 0.4 else 
                                    "insufficient_data"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error assessing data quality: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data quality assessment failed: {str(e)}")


@router.get("/fields/{field_id}/sequence-analysis")
async def get_crop_sequence_analysis(field_id: str, years: int = Query(10, ge=1, le=20)):
    """Analyze crop sequence patterns in field history."""
    try:
        analysis = await field_history_service.get_crop_sequence_analysis(field_id, years)
        
        return {
            "field_id": field_id,
            "sequence_analysis": analysis,
            "planning_recommendations": analysis.get('recommendations', []),
            "potential_issues": analysis.get('potential_issues', [])
        }
        
    except Exception as e:
        logger.error(f"Error analyzing crop sequence: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sequence analysis failed: {str(e)}")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for rotation planning service."""
    return {
        "status": "healthy",
        "service": "crop-rotation-planning",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }