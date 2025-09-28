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
    RotationPlanRequest, RotationPlanResponse, RotationAnalysisResponse,
    RotationPlanUpdateRequest
)
from ..services.field_history_service import field_history_service
from ..services.rotation_optimization_engine import RotationOptimizationEngine
from ..services.rotation_storage_service import rotation_storage_service
from ..services.rotation_goal_service import RotationGoalService
from ..services.rotation_analysis_service import RotationAnalysisService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rotations", tags=["crop-rotation"])
fields_router = APIRouter(prefix="/fields", tags=["fields"])

# Initialize services
goal_service = RotationGoalService()
rotation_optimization_engine = RotationOptimizationEngine()
rotation_analysis_service = RotationAnalysisService()


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


class GoalPrioritizationRequest(BaseModel):
    """Request for goal prioritization."""
    goals: List[Dict[str, Any]]
    strategy: str = "weighted_average"
    farmer_preferences: Optional[Dict[str, float]] = None


class GoalTemplateResponse(BaseModel):
    """Response for goal templates."""
    templates: Dict[str, Dict[str, Any]]
    compatibility_matrix: Dict[str, Dict[str, float]]


class GoalConflictAnalysisRequest(BaseModel):
    """Request for goal conflict analysis."""
    goals: List[Dict[str, Any]]


# Field History Management Endpoints

@fields_router.post("", status_code=status.HTTP_201_CREATED)
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


@fields_router.post("/{field_id}/history", status_code=status.HTTP_201_CREATED)
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


@fields_router.get("/{field_id}/history")
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


@fields_router.put("/{field_id}/history/{year}")
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


@fields_router.delete("/{field_id}/history/{year}")
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


@fields_router.post("/{field_id}/bulk-import")
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


@router.put("/plans/{plan_id}", response_model=RotationPlanResponse)
async def update_rotation_plan(plan_id: str, updates: RotationPlanUpdateRequest):
    """Update rotation plan with partial updates support."""
    try:
        # Validate plan_id format
        if not plan_id or len(plan_id.strip()) == 0:
            raise HTTPException(
                status_code=400, 
                detail="Plan ID cannot be empty"
            )
        
        # Check if plan exists and update it
        updated_plan = await rotation_storage_service.update_plan(plan_id, updates)
        
        if not updated_plan:
            raise HTTPException(
                status_code=404, 
                detail=f"Rotation plan with ID {plan_id} not found"
            )
        
        # Convert to response model
        response = RotationPlanResponse(
            plan_id=updated_plan.plan_id,
            field_id=updated_plan.field_id,
            plan_name=updated_plan.plan_name,
            created_date=updated_plan.created_date,
            rotation_schedule=updated_plan.rotation_years,
            rotation_details=updated_plan.rotation_details,
            overall_score=updated_plan.overall_score or 0.0,
            benefit_scores=updated_plan.benefit_scores,
            economic_projections=updated_plan.economic_projections or {},
            key_insights=[],  # These would be populated by analysis service
            recommendations=[],
            warnings=[]
        )
        
        logger.info(f"Successfully updated rotation plan: {plan_id}")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        logger.error(f"Validation error updating rotation plan {plan_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating rotation plan {plan_id}: {str(e)}")
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


@router.post("/sustainability-score")
async def calculate_sustainability_score(
    field_id: str = Query(..., description="Field ID"),
    rotation_sequence: List[str] = Query(..., description="Crop rotation sequence")
):
    """Calculate comprehensive sustainability metrics for a rotation sequence."""
    try:
        logger.info(f"Calculating sustainability score for field {field_id} with sequence: {rotation_sequence}")
        
        # Get field profile
        field_profile = field_history_service.field_profiles.get(field_id)
        if not field_profile:
            raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
        
        # Validate rotation sequence
        if not rotation_sequence or len(rotation_sequence) == 0:
            raise HTTPException(status_code=400, detail="Rotation sequence cannot be empty")
        
        # Create a temporary rotation plan for analysis
        from ..models.rotation_models import CropRotationPlan
        from datetime import datetime
        
        # Create rotation years dictionary from sequence
        base_year = datetime.now().year
        rotation_years_dict = {}
        rotation_details_dict = {}
        
        for i, crop in enumerate(rotation_sequence):
            year = base_year + i
            rotation_years_dict[year] = crop
            
            # Estimate yield using optimization engine (with error handling)
            try:
                estimated_yield = await rotation_optimization_engine._estimate_crop_yield(
                    crop, field_profile, i, rotation_sequence
                )
            except:
                # Fallback yield estimates if optimization engine method fails
                default_yields = {
                    'corn': 180.0,     # bushels/acre
                    'soybean': 50.0,   # bushels/acre
                    'wheat': 60.0,     # bushels/acre
                    'oats': 80.0,      # bushels/acre
                    'alfalfa': 4.0,    # tons/acre
                    'barley': 70.0     # bushels/acre
                }
                estimated_yield = default_yields.get(crop.lower(), 50.0)
            
            rotation_details_dict[year] = {
                'crop_name': crop,
                'estimated_yield': estimated_yield,
                'yield_units': 'bushels' if crop.lower() != 'alfalfa' else 'tons'
            }
        
        # Create temporary rotation plan
        temp_plan = CropRotationPlan(
            plan_id=f"temp_sustainability_{field_id}_{int(datetime.now().timestamp())}",
            field_id=field_id,
            farm_id=getattr(field_profile, 'farm_id', 'unknown'),
            plan_name="Sustainability Analysis",
            created_date=datetime.now(),
            rotation_years=rotation_years_dict,
            rotation_details=rotation_details_dict,
            planning_horizon=len(rotation_sequence),
            start_year=base_year,
            overall_score=0.0,
            benefit_scores={},
            economic_projections={}
        )
        
        # Calculate comprehensive sustainability metrics
        sustainability_metrics = await rotation_analysis_service.calculate_sustainability_metrics(
            rotation_plan=temp_plan,
            field_profile=field_profile
        )
        
        # Calculate rotation benefits for additional sustainability insights
        benefit_analysis = await rotation_analysis_service.analyze_rotation_benefits(
            rotation_plan=temp_plan,
            field_profile=field_profile
        )
        
        # Calculate detailed sustainability scores (0-100 scale)
        sustainability_scores = {
            "environmental_impact": sustainability_metrics.environmental_impact_score,
            "soil_health": min(100, benefit_analysis.soil_organic_matter_improvement * 2),  # Scale to 0-100
            "carbon_sequestration": min(100, benefit_analysis.carbon_sequestration_tons * 20),  # Scale to 0-100
            "water_efficiency": sustainability_metrics.water_conservation_score,
            "biodiversity": min(100, benefit_analysis.biodiversity_index),
            "long_term_viability": sustainability_metrics.long_term_viability_score
        }
        
        # Calculate overall sustainability score
        overall_score = sum(sustainability_scores.values()) / len(sustainability_scores)
        
        # Determine sustainability grade
        def get_sustainability_grade(score: float) -> str:
            if score >= 90:
                return "A"
            elif score >= 80:
                return "B"
            elif score >= 70:
                return "C"
            elif score >= 60:
                return "D"
            else:
                return "F"
        
        sustainability_grade = get_sustainability_grade(overall_score)
        
        # Generate improvement recommendations
        recommendations = []
        
        if sustainability_scores["environmental_impact"] < 70:
            recommendations.append("Consider adding more legumes to reduce nitrogen fertilizer needs")
            
        if sustainability_scores["soil_health"] < 70:
            recommendations.append("Include cover crops or perennial forages to improve soil organic matter")
            
        if sustainability_scores["carbon_sequestration"] < 60:
            recommendations.append("Add deep-rooted crops like alfalfa to increase carbon sequestration")
            
        if sustainability_scores["water_efficiency"] < 70:
            recommendations.append("Consider drought-tolerant crops or improve water management practices")
            
        if sustainability_scores["biodiversity"] < 70:
            recommendations.append("Increase crop diversity by adding different plant families to the rotation")
            
        if sustainability_scores["long_term_viability"] < 75:
            recommendations.append("Balance economic returns with environmental benefits for long-term sustainability")
        
        # Add diversity-specific recommendations
        unique_crops = len(set(rotation_sequence))
        if unique_crops < 3:
            recommendations.append("Add more crop diversity to improve pest management and soil health")
        
        # Check for nitrogen-fixing crops
        nitrogen_fixers = ['soybean', 'alfalfa', 'clover', 'peas', 'beans']
        has_nitrogen_fixer = any(crop.lower() in nitrogen_fixers for crop in rotation_sequence)
        if not has_nitrogen_fixer:
            recommendations.append("Include nitrogen-fixing legumes to reduce fertilizer requirements")
        
        # Add general sustainability recommendations if score is good
        if overall_score >= 80 and not recommendations:
            recommendations.extend([
                "Excellent sustainability profile - maintain current rotation practices",
                "Monitor soil health indicators annually to track improvements",
                "Consider precision agriculture technologies to optimize resource use"
            ])
        elif overall_score >= 70 and len(recommendations) < 2:
            recommendations.append("Good sustainability foundation - minor improvements can enhance performance")
        
        return {
            "field_id": field_id,
            "rotation_sequence": rotation_sequence,
            "sustainability_scores": sustainability_scores,
            "overall_sustainability_score": round(overall_score, 2),
            "sustainability_grade": sustainability_grade,
            "recommendations": recommendations,
            "analysis_details": {
                "crop_diversity_index": benefit_analysis.biodiversity_index,
                "nitrogen_fixation_lbs_per_acre": benefit_analysis.nitrogen_fixation_annual_avg,
                "carbon_sequestration_tons": benefit_analysis.carbon_sequestration_tons,
                "erosion_reduction_percent": benefit_analysis.erosion_reduction_percent,
                "water_use_efficiency_score": benefit_analysis.water_use_efficiency,
                "soil_health_trajectory": sustainability_metrics.soil_health_trajectory,
                "unique_crops_count": unique_crops,
                "rotation_length_years": len(rotation_sequence),
                "has_nitrogen_fixing_crops": has_nitrogen_fixer
            },
            "sustainability_insights": [
                f"Rotation includes {unique_crops} different crop types",
                f"Average annual nitrogen fixation: {benefit_analysis.nitrogen_fixation_annual_avg:.1f} lbs/acre",
                f"Carbon sequestration potential: {benefit_analysis.carbon_sequestration_tons:.2f} tons",
                f"Biodiversity index: {benefit_analysis.biodiversity_index:.1f}/100",
                f"Soil erosion reduction: {benefit_analysis.erosion_reduction_percent:.1f}%"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating sustainability score: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sustainability analysis failed: {str(e)}")


@fields_router.get("/{field_id}/data-quality")
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


@fields_router.get("/{field_id}/sequence-analysis")
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


# Goal Prioritization Endpoints

@router.get("/goal-templates", response_model=GoalTemplateResponse)
async def get_goal_templates():
    """Get available goal templates and compatibility matrix."""
    try:
        templates = goal_service.goal_templates
        compatibility_matrix = goal_service.goal_compatibility_matrix
        
        return GoalTemplateResponse(
            templates=templates,
            compatibility_matrix=compatibility_matrix
        )
    except Exception as e:
        logger.error(f"Error retrieving goal templates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve goal templates: {str(e)}")


@router.post("/prioritize-goals")
async def prioritize_goals(request: GoalPrioritizationRequest):
    """Prioritize rotation goals using specified strategy."""
    try:
        # Convert dict goals to RotationGoal objects
        from ..models.rotation_models import RotationGoal, RotationGoalType
        
        rotation_goals = []
        for goal_dict in request.goals:
            goal = RotationGoal(
                goal_id=goal_dict.get('goal_id', goal_dict.get('type', 'unknown')),
                goal_type=RotationGoalType(goal_dict.get('type', 'SOIL_HEALTH')),
                description=goal_dict.get('description', ''),
                priority=goal_dict.get('priority', 1.0),
                weight=goal_dict.get('weight', 0.5),
                target_value=goal_dict.get('target_value', 0.0),
                measurement_criteria=goal_dict.get('measurement_criteria', [])
            )
            rotation_goals.append(goal)
        
        # Import strategy enum
        from ..services.rotation_goal_service import GoalPriorityStrategy
        strategy_enum = GoalPriorityStrategy(request.strategy)
        
        # Prioritize goals
        prioritized_goals = await goal_service.prioritize_goals(
            goals=rotation_goals,
            strategy=strategy_enum,
            farmer_preferences=request.farmer_preferences
        )
        
        # Convert back to dict format
        result = []
        for goal in prioritized_goals:
            goal_dict = {
                'goal_id': goal.goal_id,
                'type': goal.goal_type.value,
                'description': goal.description,
                'priority': goal.priority,
                'weight': goal.weight,
                'target_value': goal.target_value,
                'measurement_criteria': goal.measurement_criteria,
                'composite_score': getattr(goal, 'composite_score', None)
            }
            result.append(goal_dict)
        
        return {
            "prioritized_goals": result,
            "strategy_used": request.strategy,
            "total_goals": len(result)
        }
        
    except Exception as e:
        logger.error(f"Error prioritizing goals: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to prioritize goals: {str(e)}")


@router.post("/analyze-goal-conflicts")
async def analyze_goal_conflicts(request: GoalConflictAnalysisRequest):
    """Analyze conflicts between rotation goals."""
    try:
        # Convert dict goals to RotationGoal objects
        from ..models.rotation_models import RotationGoal, RotationGoalType
        
        rotation_goals = []
        for goal_dict in request.goals:
            goal = RotationGoal(
                goal_id=goal_dict.get('goal_id', goal_dict.get('type', 'unknown')),
                goal_type=RotationGoalType(goal_dict.get('type', 'SOIL_HEALTH')),
                description=goal_dict.get('description', ''),
                priority=goal_dict.get('priority', 1.0),
                weight=goal_dict.get('weight', 0.5),
                target_value=goal_dict.get('target_value', 0.0),
                measurement_criteria=goal_dict.get('measurement_criteria', [])
            )
            rotation_goals.append(goal)
        
        # Analyze conflicts
        conflicts = await goal_service.analyze_goal_conflicts(rotation_goals)
        
        # Convert conflicts to dict format
        result = []
        for conflict in conflicts:
            conflict_dict = {
                'conflicting_goals': conflict.conflicting_goals,
                'resolution_strategy': conflict.resolution_strategy,
                'weight_adjustments': conflict.weight_adjustments,
                'explanation': conflict.explanation
            }
            result.append(conflict_dict)
        
        return {
            "conflicts": result,
            "total_conflicts": len(result),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing goal conflicts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze goal conflicts: {str(e)}")


@router.post("/validate-constraints")
async def validate_constraints(field_id: str, constraints: List[Dict[str, Any]]):
    """Validate rotation constraints for feasibility."""
    try:
        # Convert dict constraints to RotationConstraint objects
        from ..models.rotation_models import RotationConstraint, ConstraintType
        
        rotation_constraints = []
        for constraint_dict in constraints:
            constraint = RotationConstraint(
                constraint_id=constraint_dict.get('constraint_id', constraint_dict.get('type', 'unknown')),
                constraint_type=ConstraintType(constraint_dict.get('type', 'REQUIRED_CROP')),
                description=constraint_dict.get('description', ''),
                parameters=constraint_dict.get('parameters', {}),
                is_hard_constraint=constraint_dict.get('is_hard_constraint', True)
            )
            rotation_constraints.append(constraint)
        
        # Get field profile for validation
        field_profile = field_history_service.field_profiles.get(field_id)
        if not field_profile:
            raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
        
        # Available crops (simplified list for validation)
        available_crops = ['corn', 'soybean', 'wheat', 'oats', 'alfalfa', 'barley', 'canola', 'sunflower']
        
        # Validate constraints
        validation_results = await goal_service.validate_constraints(rotation_constraints, field_profile, available_crops)
        
        # Convert validation results to dict format
        result = []
        for validation in validation_results:
            validation_dict = {
                'constraint_id': validation.constraint_id,
                'is_feasible': validation.is_feasible,
                'conflicts': validation.conflicts,
                'suggestions': validation.suggestions,
                'impact_assessment': validation.impact_assessment
            }
            result.append(validation_dict)
        
        return {
            "validation_results": result,
            "field_id": field_id,
            "total_constraints": len(result),
            "feasible_constraints": sum(1 for r in result if r['is_feasible']),
            "validation_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error validating constraints: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate constraints: {str(e)}")


@router.post("/risk-assessment")
async def assess_rotation_risks(
    field_id: str = Query(..., description="Field ID"),
    rotation_sequence: List[str] = Query(..., description="Crop rotation sequence")
):
    """Assess comprehensive risks for a specific rotation sequence."""
    try:
        logger.info(f"Assessing rotation risks for field {field_id} with sequence: {rotation_sequence}")
        
        # Validate input parameters
        if not rotation_sequence or len(rotation_sequence) == 0:
            raise HTTPException(status_code=400, detail="Rotation sequence cannot be empty")
        
        if len(rotation_sequence) > 20:
            raise HTTPException(status_code=400, detail="Rotation sequence too long (maximum 20 years)")
        
        # Get field profile
        field_profile = field_history_service.field_profiles.get(field_id)
        if not field_profile:
            raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
        
        # Create a temporary rotation plan for risk assessment
        from ..models.rotation_models import CropRotationPlan, RotationYear
        
        base_year = datetime.now().year
        rotation_years_list = []
        rotation_years_dict = {}
        rotation_details_dict = {}
        
        for i, crop in enumerate(rotation_sequence):
            year = base_year + i
            
            # Estimate yield using optimization engine (with fallback)
            try:
                estimated_yield = await rotation_optimization_engine._estimate_crop_yield(
                    crop, field_profile, i, rotation_sequence
                )
            except:
                # Fallback yield estimates
                default_yields = {
                    'corn': 180.0,     # bushels/acre
                    'soybean': 50.0,   # bushels/acre
                    'wheat': 60.0,     # bushels/acre
                    'oats': 80.0,      # bushels/acre
                    'alfalfa': 4.0,    # tons/acre
                    'barley': 70.0,    # bushels/acre
                    'canola': 40.0,    # bushels/acre
                    'sunflower': 2500.0 # lbs/acre
                }
                estimated_yield = default_yields.get(crop.lower(), 50.0)
            
            rotation_year = RotationYear(
                year=year,
                crop_name=crop,
                estimated_yield=estimated_yield,
                confidence_score=0.8
            )
            
            rotation_years_list.append(rotation_year)
            rotation_years_dict[year] = crop
            rotation_details_dict[year] = {
                'crop_name': crop,
                'estimated_yield': estimated_yield,
                'yield_units': 'bushels' if crop.lower() != 'alfalfa' else 'tons'
            }
        
        # Create temporary rotation plan for analysis
        temp_plan = CropRotationPlan(
            plan_id=f"temp_risk_assessment_{field_id}_{int(datetime.now().timestamp())}",
            field_id=field_id,
            farm_id=getattr(field_profile, 'farm_id', 'unknown'),
            plan_name="Risk Assessment Analysis",
            created_date=datetime.now(),
            rotation_years=rotation_years_dict,
            rotation_details=rotation_details_dict,
            planning_horizon=len(rotation_sequence),
            start_year=base_year,
            overall_score=0.0,
            benefit_scores={},
            economic_projections={}
        )
        
        # Perform comprehensive risk assessment using rotation analysis service
        risk_assessment = await rotation_analysis_service.assess_rotation_risks(
            rotation_plan=temp_plan,
            field_profile=field_profile
        )
        
        # Calculate individual risk scores (0-100 scale, higher = more risk)
        risk_scores = {
            "weather_climate": round(risk_assessment.weather_risk_score, 2),
            "market_volatility": round(risk_assessment.market_risk_score, 2),
            "pest_disease": round(risk_assessment.pest_disease_risk_score, 2),
            "soil_health": _calculate_soil_health_risk(rotation_sequence, field_profile),
            "yield_variability": round(risk_assessment.yield_variability_risk, 2),
            "economic": round(risk_assessment.input_cost_risk, 2)
        }
        
        # Calculate overall risk score
        overall_risk_score = round(risk_assessment.overall_risk_score, 2)
        
        # Determine risk level
        def get_risk_level(score: float) -> str:
            if score >= 80:
                return "CRITICAL"
            elif score >= 60:
                return "HIGH"
            elif score >= 35:
                return "MEDIUM" 
            else:
                return "LOW"
        
        risk_level = get_risk_level(overall_risk_score)
        
        # Identify specific risk factors
        risk_factors = []
        
        if risk_scores["weather_climate"] > 60:
            risk_factors.append("High weather/climate sensitivity")
        if risk_scores["market_volatility"] > 50:
            risk_factors.append("Significant market price volatility")
        if risk_scores["pest_disease"] > 40:
            risk_factors.append("Pest and disease pressure concerns")
        if risk_scores["soil_health"] > 50:
            risk_factors.append("Soil health degradation risk")
        if risk_scores["yield_variability"] > 45:
            risk_factors.append("High yield variability")
        if risk_scores["economic"] > 55:
            risk_factors.append("Input cost volatility risk")
        
        # Check for monoculture or low diversity risks
        unique_crops = len(set(rotation_sequence))
        if unique_crops == 1:
            risk_factors.append("Monoculture system - high risk")
        elif unique_crops < 3:
            risk_factors.append("Limited crop diversity")
        
        # Check for continuous cropping
        for i in range(1, len(rotation_sequence)):
            if rotation_sequence[i] == rotation_sequence[i-1]:
                risk_factors.append("Continuous cropping detected")
                break
        
        # Generate mitigation strategies
        mitigation_strategies = list(risk_assessment.risk_mitigation_strategies)
        
        # Add specific strategies based on risk analysis
        if risk_scores["weather_climate"] > 60:
            mitigation_strategies.extend([
                "Implement precision irrigation systems",
                "Plant climate-adapted crop varieties",
                "Consider adjusting planting dates for climate resilience"
            ])
        
        if risk_scores["market_volatility"] > 50:
            mitigation_strategies.extend([
                "Diversify marketing channels and timing",
                "Consider commodity price hedging strategies",
                "Explore value-added processing opportunities"
            ])
        
        if unique_crops < 3:
            mitigation_strategies.append("Increase crop diversity in rotation to reduce risks")
        
        if "nitrogen-fixing" not in [crop.lower() for crop in rotation_sequence if crop.lower() in ['soybean', 'alfalfa', 'clover', 'peas']]:
            mitigation_strategies.append("Add nitrogen-fixing legumes to reduce fertilizer costs and risks")
        
        # Remove duplicates from mitigation strategies
        mitigation_strategies = list(dict.fromkeys(mitigation_strategies))
        
        # Calculate risk timeline (year-by-year risk evolution)
        risk_timeline = {}
        base_risk = overall_risk_score
        
        for i, crop in enumerate(rotation_sequence):
            year = base_year + i
            
            # Adjust risk based on position in rotation
            position_adjustment = 0
            
            # First year establishment risk
            if i == 0:
                position_adjustment += 5
            
            # Continuous cropping penalty
            if i > 0 and rotation_sequence[i] == rotation_sequence[i-1]:
                position_adjustment += 15
            
            # Diversity benefit (cumulative)
            crops_so_far = len(set(rotation_sequence[:i+1]))
            diversity_benefit = min(10, (crops_so_far - 1) * 3)
            
            year_risk = max(0, min(100, base_risk + position_adjustment - diversity_benefit))
            risk_timeline[str(year)] = round(year_risk, 2)
        
        return {
            "field_id": field_id,
            "rotation_sequence": rotation_sequence,
            "risk_scores": risk_scores,
            "overall_risk_score": overall_risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "mitigation_strategies": mitigation_strategies,
            "risk_timeline": risk_timeline,
            "assessment_details": {
                "crops_analyzed": len(rotation_sequence),
                "unique_crops": unique_crops,
                "rotation_length_years": len(rotation_sequence),
                "assessment_date": datetime.now().isoformat(),
                "confidence_level": "high" if len(rotation_sequence) >= 3 else "medium",
                "field_size_acres": getattr(field_profile, 'size_acres', 'unknown'),
                "climate_zone": getattr(field_profile, 'climate_zone', 'unknown')
            },
            "recommendations_summary": {
                "primary_concern": _get_primary_risk_concern(risk_scores),
                "top_mitigation": mitigation_strategies[0] if mitigation_strategies else "Increase crop diversity",
                "risk_trend": "improving" if overall_risk_score < 50 else "concerning" if overall_risk_score > 70 else "moderate"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing rotation risks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")


def _calculate_soil_health_risk(rotation_sequence: List[str], field_profile) -> float:
    """Calculate soil health risk based on rotation sequence."""
    
    # Soil health risk factors
    soil_building_crops = {'alfalfa': -15, 'clover': -10, 'soybean': -5, 'oats': -3}
    soil_depleting_crops = {'corn': 8, 'wheat': 3, 'barley': 2}
    
    risk_score = 50.0  # Baseline risk
    
    for crop in rotation_sequence:
        crop_lower = crop.lower()
        if crop_lower in soil_building_crops:
            risk_score += soil_building_crops[crop_lower]
        elif crop_lower in soil_depleting_crops:
            risk_score += soil_depleting_crops[crop_lower]
    
    # Check for continuous row crops (higher erosion risk)
    row_crops = ['corn', 'soybean']
    continuous_row_crop_years = 0
    for i in range(len(rotation_sequence)):
        if rotation_sequence[i].lower() in row_crops:
            continuous_row_crop_years += 1
        else:
            continuous_row_crop_years = 0
        
        if continuous_row_crop_years >= 3:
            risk_score += 20  # Significant soil health risk
            break
    
    # Adjust for field characteristics
    if hasattr(field_profile, 'slope_percent') and field_profile.slope_percent:
        if field_profile.slope_percent > 8:
            risk_score += 15  # Higher erosion risk on steep slopes
        elif field_profile.slope_percent > 4:
            risk_score += 8
    
    # Drainage impact
    if hasattr(field_profile, 'drainage_class') and field_profile.drainage_class:
        if field_profile.drainage_class.lower() in ['poorly drained', 'very poorly drained']:
            risk_score += 10  # Compaction and waterlogging risks
    
    return max(0, min(100, risk_score))


def _get_primary_risk_concern(risk_scores: Dict[str, float]) -> str:
    """Identify the primary risk concern."""
    max_risk = max(risk_scores.values())
    for risk_type, score in risk_scores.items():
        if score == max_risk:
            risk_descriptions = {
                "weather_climate": "Weather and climate variability",
                "market_volatility": "Market price volatility",
                "pest_disease": "Pest and disease pressure",
                "soil_health": "Soil health degradation",
                "yield_variability": "Yield inconsistency",
                "economic": "Input cost volatility"
            }
            return risk_descriptions.get(risk_type, "Multiple risk factors")
    
    return "Balanced risk profile"


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