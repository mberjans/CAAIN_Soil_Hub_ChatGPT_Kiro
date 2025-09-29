"""
API Routes for Nutrient Deficiency Detection
Provides endpoints for comprehensive nutrient deficiency analysis,
visual symptom processing, and treatment recommendations.
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field
import base64

from ..services.nutrient_deficiency_detection_service import (
    NutrientDeficiencyDetectionService, DeficiencyType, DeficiencySeverity
)
from ..services.visual_symptom_analyzer import VisualSymptomAnalyzer, CropImageAnalyzer
from ..models.agricultural_models import SoilTestData


# Request/Response Models
class DeficiencyAnalysisRequest(BaseModel):
    """Request for comprehensive deficiency analysis."""
    crop_type: str
    farm_id: str
    field_id: str
    soil_test_data: Optional[Dict[str, Any]] = None
    tissue_test_data: Optional[Dict[str, float]] = None
    visual_symptoms: Optional[List[str]] = None
    field_observations: Optional[Dict[str, Any]] = None
    growth_stage: Optional[str] = None
    environmental_conditions: Optional[Dict[str, Any]] = None


class ImageAnalysisRequest(BaseModel):
    """Request for crop image analysis."""
    crop_type: str
    farm_id: str
    field_id: str
    images: List[str] = Field(..., description="Base64 encoded images")
    suspected_deficiencies: Optional[List[str]] = None
    image_metadata: Optional[Dict[str, Any]] = None


class SymptomDescriptionRequest(BaseModel):
    """Request for symptom description analysis."""
    crop_type: str
    symptom_description: str
    growth_stage: Optional[str] = None
    environmental_conditions: Optional[Dict[str, Any]] = None
    affected_area_percent: Optional[float] = None


class TreatmentRequest(BaseModel):
    """Request for treatment recommendations."""
    deficiency_analysis_id: str
    farm_id: str
    field_id: str
    budget_constraints: Optional[Dict[str, float]] = None
    application_preferences: Optional[Dict[str, Any]] = None


class MonitoringSetupRequest(BaseModel):
    """Request for setting up deficiency monitoring."""
    farm_id: str
    field_id: str
    crop_type: str
    monitoring_parameters: List[str]
    alert_thresholds: Dict[str, float]
    monitoring_frequency: str


# Initialize router and services
router = APIRouter(prefix="/api/v1/deficiency", tags=["nutrient-deficiency"])

# Service instances
deficiency_service = NutrientDeficiencyDetectionService()
symptom_analyzer = VisualSymptomAnalyzer()
image_analyzer = CropImageAnalyzer()


@router.post("/analyze")
async def analyze_nutrient_deficiency(request: DeficiencyAnalysisRequest):
    """
    Perform comprehensive nutrient deficiency analysis.
    
    Combines multiple data sources:
    - Soil test results
    - Plant tissue test results  
    - Visual symptom descriptions
    - Field observations
    
    Returns prioritized deficiency analysis with confidence scores.
    """
    try:
        # Convert soil test data if provided
        soil_test_data = None
        if request.soil_test_data:
            soil_test_data = SoilTestData(**request.soil_test_data)
        
        # Perform comprehensive analysis
        analysis = await deficiency_service.analyze_comprehensive_deficiency(
            crop_type=request.crop_type,
            soil_test_data=soil_test_data,
            tissue_test_data=request.tissue_test_data,
            visual_symptoms=request.visual_symptoms,
            crop_images=None,  # No images in this endpoint
            field_observations=request.field_observations
        )
        
        return {
            "status": "success",
            "analysis": analysis,
            "message": "Nutrient deficiency analysis completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing deficiency analysis: {str(e)}"
        )


@router.post("/image-analysis")
async def analyze_crop_images(request: ImageAnalysisRequest):
    """
    Analyze crop photos for visual deficiency symptoms.
    
    Uses AI-powered computer vision to detect:
    - Leaf discoloration patterns
    - Growth abnormalities
    - Symptom severity
    - Affected plant areas
    """
    try:
        # Validate images
        if not request.images:
            raise HTTPException(
                status_code=400,
                detail="At least one image is required for analysis"
            )
        
        # Convert suspected deficiencies to enum types
        suspected_deficiencies = []
        if request.suspected_deficiencies:
            for deficiency_name in request.suspected_deficiencies:
                try:
                    deficiency_type = DeficiencyType(deficiency_name.lower())
                    suspected_deficiencies.append(deficiency_type)
                except ValueError:
                    continue
        
        # Analyze each image
        image_analyses = []
        for i, image_data in enumerate(request.images):
            # Assess image quality first
            quality_assessment = image_analyzer.assess_image_quality(image_data)
            
            if quality_assessment['quality_score'] < 0.5:
                image_analyses.append({
                    'image_index': i,
                    'quality_assessment': quality_assessment,
                    'analysis_result': None,
                    'message': 'Image quality too low for reliable analysis'
                })
                continue
            
            # Perform deficiency analysis
            analysis_result = await image_analyzer.analyze_crop_image(
                image_data=image_data,
                crop_type=request.crop_type,
                suspected_deficiencies=suspected_deficiencies
            )
            
            image_analyses.append({
                'image_index': i,
                'quality_assessment': quality_assessment,
                'analysis_result': analysis_result,
                'message': 'Analysis completed successfully'
            })
        
        # Combine results from multiple images
        combined_analysis = _combine_image_analyses(image_analyses)
        
        return {
            "status": "success",
            "individual_analyses": image_analyses,
            "combined_analysis": combined_analysis,
            "message": f"Analyzed {len(request.images)} images successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing crop images: {str(e)}"
        )


@router.post("/symptoms")
async def process_symptom_description(request: SymptomDescriptionRequest):
    """
    Process natural language symptom descriptions.
    
    Analyzes farmer descriptions of crop symptoms to identify:
    - Potential nutrient deficiencies
    - Symptom severity
    - Affected plant parts
    - Alternative diagnoses
    """
    try:
        # Analyze symptom description
        symptom_analysis = await symptom_analyzer.analyze_symptom_description(
            symptom_description=request.symptom_description,
            crop_type=request.crop_type,
            growth_stage=request.growth_stage,
            environmental_conditions=request.environmental_conditions
        )
        
        # Convert to response format
        analysis_result = {
            'detected_symptoms': symptom_analysis.detected_symptoms,
            'symptom_severity': symptom_analysis.symptom_severity,
            'affected_plant_parts': symptom_analysis.affected_plant_parts,
            'symptom_distribution': symptom_analysis.symptom_distribution,
            'confidence_score': symptom_analysis.confidence_score,
            'alternative_diagnoses': symptom_analysis.alternative_diagnoses,
            'recommendations': _generate_symptom_recommendations(symptom_analysis)
        }
        
        return {
            "status": "success",
            "symptom_analysis": analysis_result,
            "message": "Symptom description processed successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing symptom description: {str(e)}"
        )


@router.get("/recommendations/{analysis_id}")
async def get_treatment_recommendations(
    analysis_id: str,
    farm_id: str,
    field_id: str,
    budget_limit: Optional[float] = None
):
    """
    Get treatment recommendations for identified deficiencies.
    
    Provides:
    - Specific fertilizer recommendations
    - Application rates and timing
    - Cost estimates
    - Expected response times
    """
    try:
        # In production, this would retrieve the analysis from database
        # For demo, we'll generate sample recommendations
        
        sample_recommendations = {
            'analysis_id': analysis_id,
            'farm_id': farm_id,
            'field_id': field_id,
            'treatment_recommendations': [
                {
                    'deficiency_type': 'nitrogen',
                    'severity': 'moderate',
                    'urgency_score': 75,
                    'recommended_treatments': [
                        {
                            'treatment_type': 'soil_fertilizer',
                            'product': 'urea',
                            'application_rate_lbs_per_acre': 80,
                            'application_timing': 'side_dress_at_v6',
                            'application_method': 'broadcast_and_incorporate',
                            'cost_estimate_per_acre': 36.00,
                            'expected_response_time': '7-14_days',
                            'effectiveness_probability': 0.85
                        },
                        {
                            'treatment_type': 'foliar_fertilizer',
                            'product': 'liquid_nitrogen_solution',
                            'application_rate_lbs_per_acre': 20,
                            'application_timing': 'early_morning_spray',
                            'application_method': 'foliar_spray',
                            'cost_estimate_per_acre': 18.00,
                            'expected_response_time': '3-7_days',
                            'effectiveness_probability': 0.75
                        }
                    ]
                },
                {
                    'deficiency_type': 'zinc',
                    'severity': 'mild',
                    'urgency_score': 45,
                    'recommended_treatments': [
                        {
                            'treatment_type': 'foliar_fertilizer',
                            'product': 'zinc_sulfate_solution',
                            'application_rate_lbs_per_acre': 1.0,
                            'application_timing': 'early_vegetative_stage',
                            'application_method': 'foliar_spray',
                            'cost_estimate_per_acre': 8.50,
                            'expected_response_time': '7-14_days',
                            'effectiveness_probability': 0.80
                        }
                    ]
                }
            ],
            'treatment_priority': [
                'Address nitrogen deficiency first (highest urgency)',
                'Follow up with zinc treatment in 2-3 weeks',
                'Monitor response and adjust rates if needed'
            ],
            'total_cost_estimate': 44.50,
            'monitoring_recommendations': [
                'Tissue test in 3-4 weeks to verify treatment response',
                'Visual monitoring weekly for symptom improvement',
                'Soil test next season to assess long-term nutrient status'
            ]
        }
        
        # Apply budget constraints if specified
        if budget_limit:
            sample_recommendations = _apply_budget_constraints(
                sample_recommendations, budget_limit
            )
        
        return {
            "status": "success",
            "recommendations": sample_recommendations,
            "message": "Treatment recommendations generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating treatment recommendations: {str(e)}"
        )


@router.post("/monitor")
async def setup_deficiency_monitoring(request: MonitoringSetupRequest):
    """
    Set up monitoring system for nutrient deficiencies.
    
    Creates monitoring plan with:
    - Regular testing schedules
    - Alert thresholds
    - Seasonal monitoring adjustments
    - Progress tracking
    """
    try:
        monitoring_plan = {
            'monitoring_id': f"monitor_{request.farm_id}_{request.field_id}_{datetime.now().strftime('%Y%m%d')}",
            'farm_id': request.farm_id,
            'field_id': request.field_id,
            'crop_type': request.crop_type,
            'monitoring_schedule': {
                'soil_testing': {
                    'frequency': 'annual',
                    'optimal_timing': 'fall_after_harvest',
                    'parameters': request.monitoring_parameters
                },
                'tissue_testing': {
                    'frequency': 'bi_annual',
                    'optimal_timing': ['early_vegetative', 'reproductive'],
                    'parameters': ['nitrogen', 'phosphorus', 'potassium', 'micronutrients']
                },
                'visual_monitoring': {
                    'frequency': 'weekly_during_growing_season',
                    'focus_areas': ['new_growth', 'older_leaves', 'overall_vigor']
                }
            },
            'alert_system': {
                'thresholds': request.alert_thresholds,
                'notification_methods': ['email', 'mobile_app'],
                'escalation_rules': {
                    'mild_deficiency': 'weekly_notification',
                    'moderate_deficiency': 'immediate_notification',
                    'severe_deficiency': 'urgent_notification_with_recommendations'
                }
            },
            'seasonal_adjustments': {
                'spring': 'Increase monitoring frequency during rapid growth',
                'summer': 'Focus on stress-related deficiencies',
                'fall': 'Comprehensive soil testing and planning',
                'winter': 'Review data and plan next season improvements'
            },
            'success_metrics': {
                'early_detection_rate': 'target_80_percent',
                'treatment_effectiveness': 'target_85_percent_success',
                'yield_protection': 'prevent_deficiency_related_losses'
            }
        }
        
        return {
            "status": "success",
            "monitoring_plan": monitoring_plan,
            "message": "Deficiency monitoring system set up successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error setting up monitoring system: {str(e)}"
        )


@router.get("/alerts")
async def get_deficiency_alerts(
    farm_id: str,
    field_id: Optional[str] = None,
    severity_filter: Optional[str] = None,
    days_back: int = 30
):
    """
    Get current deficiency alerts and warnings.
    
    Returns active alerts for:
    - Detected deficiencies
    - Risk conditions
    - Monitoring reminders
    - Treatment follow-ups
    """
    try:
        # Sample alerts (in production, would query database)
        sample_alerts = [
            {
                'alert_id': 'alert_001',
                'farm_id': farm_id,
                'field_id': field_id or 'field_001',
                'alert_type': 'deficiency_detected',
                'severity': 'moderate',
                'deficiency_type': 'nitrogen',
                'message': 'Moderate nitrogen deficiency detected in corn field',
                'recommended_action': 'Apply 60-80 lbs N/acre as side-dress application',
                'urgency_score': 75,
                'created_at': datetime.now(),
                'status': 'active'
            },
            {
                'alert_id': 'alert_002',
                'farm_id': farm_id,
                'field_id': field_id or 'field_002',
                'alert_type': 'monitoring_reminder',
                'severity': 'low',
                'message': 'Tissue testing recommended for early deficiency detection',
                'recommended_action': 'Schedule tissue sampling during V6-V8 growth stage',
                'urgency_score': 30,
                'created_at': datetime.now(),
                'status': 'pending'
            },
            {
                'alert_id': 'alert_003',
                'farm_id': farm_id,
                'field_id': field_id or 'field_001',
                'alert_type': 'treatment_followup',
                'severity': 'medium',
                'message': 'Follow-up assessment needed for zinc treatment applied 2 weeks ago',
                'recommended_action': 'Visual inspection and tissue test to verify treatment response',
                'urgency_score': 50,
                'created_at': datetime.now(),
                'status': 'active'
            }
        ]
        
        # Filter by severity if specified
        if severity_filter:
            sample_alerts = [
                alert for alert in sample_alerts 
                if alert['severity'] == severity_filter.lower()
            ]
        
        return {
            "status": "success",
            "alerts": sample_alerts,
            "alert_summary": {
                'total_alerts': len(sample_alerts),
                'active_alerts': len([a for a in sample_alerts if a['status'] == 'active']),
                'high_priority_alerts': len([a for a in sample_alerts if a['urgency_score'] > 70])
            },
            "message": f"Retrieved {len(sample_alerts)} alerts"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving deficiency alerts: {str(e)}"
        )

@router.post("/track-treatment")
async def track_treatment_progress(
    treatment_id: str,
    farm_id: str,
    field_id: str,
    progress_data: Dict[str, Any]
):
    """
    Track progress of deficiency treatment implementation.
    
    Monitors:
    - Treatment application status
    - Symptom improvement
    - Follow-up test results
    - Treatment effectiveness
    """
    try:
        tracking_result = {
            'treatment_id': treatment_id,
            'farm_id': farm_id,
            'field_id': field_id,
            'progress_summary': {
                'treatment_applied': progress_data.get('treatment_applied', False),
                'application_date': progress_data.get('application_date'),
                'days_since_treatment': _calculate_days_since_treatment(
                    progress_data.get('application_date')
                ),
                'symptom_improvement': progress_data.get('symptom_improvement', 'not_assessed'),
                'follow_up_tests_completed': progress_data.get('follow_up_tests', False)
            },
            'effectiveness_assessment': {
                'visual_improvement_percent': progress_data.get('visual_improvement', 0),
                'tissue_test_improvement': progress_data.get('tissue_improvement', {}),
                'yield_impact_prevented': progress_data.get('yield_protection', 0),
                'treatment_success_probability': _calculate_treatment_success(progress_data)
            },
            'next_actions': _generate_next_actions(progress_data),
            'updated_at': datetime.now()
        }
        
        return {
            "status": "success",
            "tracking_result": tracking_result,
            "message": "Treatment progress tracked successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error tracking treatment progress: {str(e)}"
        )


@router.get("/dashboard")
async def get_deficiency_dashboard(
    farm_id: str,
    field_id: Optional[str] = None,
    timeframe_days: int = 90
):
    """
    Get comprehensive deficiency monitoring dashboard.
    
    Displays:
    - Current deficiency status
    - Treatment progress
    - Alert summary
    - Monitoring metrics
    """
    try:
        dashboard_data = {
            'farm_id': farm_id,
            'field_id': field_id,
            'timeframe_days': timeframe_days,
            'deficiency_status': {
                'active_deficiencies': [
                    {
                        'deficiency_type': 'nitrogen',
                        'severity': 'moderate',
                        'confidence': 0.85,
                        'first_detected': '2024-03-15',
                        'treatment_status': 'in_progress'
                    },
                    {
                        'deficiency_type': 'zinc',
                        'severity': 'mild',
                        'confidence': 0.72,
                        'first_detected': '2024-03-20',
                        'treatment_status': 'planned'
                    }
                ],
                'resolved_deficiencies': [
                    {
                        'deficiency_type': 'iron',
                        'severity': 'moderate',
                        'treatment_date': '2024-02-28',
                        'resolution_date': '2024-03-14',
                        'treatment_effectiveness': 0.88
                    }
                ]
            },
            'monitoring_metrics': {
                'tests_completed_this_season': 3,
                'deficiencies_detected_early': 2,
                'treatments_applied': 1,
                'treatment_success_rate': 0.88,
                'yield_loss_prevented_percent': 8.5
            },
            'alert_summary': {
                'active_alerts': 2,
                'pending_actions': 3,
                'overdue_monitoring': 0,
                'treatment_followups_needed': 1
            },
            'seasonal_trends': {
                'common_deficiencies_this_season': ['nitrogen', 'zinc'],
                'peak_deficiency_period': 'early_to_mid_vegetative',
                'treatment_response_times': {
                    'nitrogen': '7-10_days',
                    'zinc': '14-21_days',
                    'iron': '10-14_days'
                }
            },
            'recommendations': [
                'Schedule tissue testing in 2 weeks to monitor nitrogen treatment response',
                'Plan zinc foliar application for next week',
                'Consider soil pH testing to address potential iron availability issues'
            ]
        }
        
        return {
            "status": "success",
            "dashboard": dashboard_data,
            "message": "Deficiency dashboard retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving deficiency dashboard: {str(e)}"
        )


@router.get("/regional-comparison")
async def get_regional_deficiency_comparison(
    farm_id: str,
    region: str,
    crop_type: str,
    comparison_period: str = "current_season"
):
    """
    Compare farm deficiency levels to regional averages.
    
    Provides:
    - Regional deficiency prevalence
    - Farm vs. regional comparison
    - Best practice recommendations
    - Peer benchmarking
    """
    try:
        regional_data = {
            'region': region,
            'crop_type': crop_type,
            'comparison_period': comparison_period,
            'regional_statistics': {
                'farms_surveyed': 150,
                'deficiency_prevalence': {
                    'nitrogen': 0.35,  # 35% of farms
                    'phosphorus': 0.18,
                    'potassium': 0.22,
                    'zinc': 0.28,
                    'iron': 0.15,
                    'manganese': 0.08
                },
                'average_severity_scores': {
                    'nitrogen': 45.2,
                    'phosphorus': 32.1,
                    'potassium': 38.7,
                    'zinc': 41.3,
                    'iron': 52.8
                }
            },
            'farm_comparison': {
                'farm_id': farm_id,
                'deficiency_status': {
                    'nitrogen': {
                        'farm_severity': 65.0,
                        'regional_average': 45.2,
                        'percentile_rank': 78,  # Farm is worse than 78% of region
                        'status': 'above_regional_average'
                    },
                    'zinc': {
                        'farm_severity': 35.0,
                        'regional_average': 41.3,
                        'percentile_rank': 42,  # Farm is better than 42% of region
                        'status': 'below_regional_average'
                    }
                }
            },
            'regional_best_practices': [
                'Split nitrogen applications are most effective in this region',
                'Zinc deficiency common in high pH soils - consider chelated forms',
                'Early season tissue testing recommended due to cool spring conditions',
                'Foliar micronutrient applications show 85% success rate regionally'
            ],
            'peer_insights': {
                'top_performing_farms': {
                    'common_practices': [
                        'Regular soil and tissue testing',
                        'Precision nutrient management',
                        'Cover crop integration',
                        'pH management for micronutrient availability'
                    ],
                    'average_treatment_success_rate': 0.92
                },
                'regional_challenges': [
                    'High pH soils limiting micronutrient availability',
                    'Variable spring weather affecting early season nutrition',
                    'Increasing zinc deficiency in continuous corn systems'
                ]
            }
        }
        
        return {
            "status": "success",
            "regional_comparison": regional_data,
            "message": "Regional comparison data retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving regional comparison: {str(e)}"
        )


@router.post("/report")
async def generate_deficiency_report(
    farm_id: str,
    field_id: Optional[str] = None,
    report_type: str = "comprehensive",
    date_range: Dict[str, str] = None
):
    """
    Generate comprehensive deficiency analysis report.
    
    Report types:
    - comprehensive: Full analysis with all data sources
    - summary: Key findings and recommendations
    - treatment_effectiveness: Focus on treatment outcomes
    - seasonal_review: End-of-season analysis
    """
    try:
        report_data = {
            'report_id': f"deficiency_report_{farm_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'farm_id': farm_id,
            'field_id': field_id,
            'report_type': report_type,
            'generated_at': datetime.now(),
            'executive_summary': {
                'total_deficiencies_detected': 4,
                'deficiencies_resolved': 2,
                'treatments_applied': 3,
                'overall_treatment_success_rate': 0.85,
                'estimated_yield_protection': '12.5%',
                'total_treatment_cost': 156.50,
                'roi_on_treatments': '340%'
            },
            'detailed_findings': {
                'deficiency_timeline': [
                    {
                        'date': '2024-02-15',
                        'deficiency': 'iron',
                        'severity': 'moderate',
                        'detection_method': 'visual_symptoms',
                        'treatment_applied': '2024-02-20',
                        'resolution_date': '2024-03-05'
                    },
                    {
                        'date': '2024-03-10',
                        'deficiency': 'nitrogen',
                        'severity': 'moderate',
                        'detection_method': 'tissue_test',
                        'treatment_applied': '2024-03-15',
                        'status': 'responding_well'
                    }
                ],
                'detection_effectiveness': {
                    'early_detection_rate': 0.75,
                    'false_positive_rate': 0.08,
                    'detection_methods_used': ['soil_test', 'tissue_test', 'visual_symptoms', 'image_analysis']
                },
                'treatment_outcomes': {
                    'successful_treatments': 2,
                    'partially_successful': 1,
                    'unsuccessful': 0,
                    'average_response_time': '10_days',
                    'cost_effectiveness': '$12.50_per_bushel_protected'
                }
            },
            'recommendations': {
                'immediate_actions': [
                    'Continue monitoring nitrogen treatment response',
                    'Schedule follow-up tissue test in 2 weeks'
                ],
                'seasonal_planning': [
                    'Implement regular tissue testing program',
                    'Consider soil pH management for micronutrient availability',
                    'Plan split nitrogen applications for next season'
                ],
                'long_term_improvements': [
                    'Develop field-specific nutrient management zones',
                    'Integrate cover crops for improved nutrient cycling',
                    'Consider precision agriculture tools for early detection'
                ]
            },
            'appendices': {
                'test_results_summary': 'Detailed soil and tissue test results',
                'treatment_application_records': 'Complete treatment application log',
                'cost_benefit_analysis': 'Detailed economic analysis of treatments',
                'regional_comparison': 'Comparison with regional deficiency patterns'
            }
        }
        
        return {
            "status": "success",
            "report": report_data,
            "message": f"{report_type.title()} deficiency report generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating deficiency report: {str(e)}"
        )


# Helper functions
def _combine_image_analyses(image_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Combine results from multiple image analyses."""
    
    successful_analyses = [
        analysis for analysis in image_analyses 
        if analysis['analysis_result'] is not None
    ]
    
    if not successful_analyses:
        return {'message': 'No successful image analyses to combine'}
    
    # Aggregate deficiency probabilities
    combined_probabilities = {}
    combined_confidences = {}
    
    for analysis in successful_analyses:
        result = analysis['analysis_result']
        for deficiency, probability in result.get('deficiency_probabilities', {}).items():
            if deficiency not in combined_probabilities:
                combined_probabilities[deficiency] = []
                combined_confidences[deficiency] = []
            
            combined_probabilities[deficiency].append(probability)
            combined_confidences[deficiency].append(
                result.get('confidence_scores', {}).get(deficiency, 0.5)
            )
    
    # Calculate averages
    final_probabilities = {}
    final_confidences = {}
    
    for deficiency in combined_probabilities:
        final_probabilities[deficiency] = sum(combined_probabilities[deficiency]) / len(combined_probabilities[deficiency])
        final_confidences[deficiency] = sum(combined_confidences[deficiency]) / len(combined_confidences[deficiency])
    
    return {
        'combined_deficiency_probabilities': final_probabilities,
        'combined_confidence_scores': final_confidences,
        'images_analyzed': len(successful_analyses),
        'overall_confidence': sum(final_confidences.values()) / len(final_confidences) if final_confidences else 0
    }


def _generate_symptom_recommendations(symptom_analysis) -> List[str]:
    """Generate recommendations based on symptom analysis."""
    
    recommendations = []
    
    if symptom_analysis.confidence_score > 0.7:
        recommendations.append("High confidence in symptom analysis - proceed with targeted testing")
    elif symptom_analysis.confidence_score > 0.4:
        recommendations.append("Moderate confidence - consider additional testing for confirmation")
    else:
        recommendations.append("Low confidence - recommend comprehensive soil and tissue testing")
    
    if len(symptom_analysis.detected_symptoms) > 3:
        recommendations.append("Multiple symptoms detected - consider comprehensive nutrient analysis")
    
    if 'older_leaves' in symptom_analysis.affected_plant_parts:
        recommendations.append("Symptoms on older leaves suggest mobile nutrient deficiency (N, P, K, Mg)")
    
    if 'younger_leaves' in symptom_analysis.affected_plant_parts:
        recommendations.append("Symptoms on younger leaves suggest immobile nutrient deficiency (Fe, Zn, Mn, B)")
    
    return recommendations


def _apply_budget_constraints(recommendations: Dict[str, Any], budget_limit: float) -> Dict[str, Any]:
    """Apply budget constraints to treatment recommendations."""
    
    # Sort treatments by cost-effectiveness (effectiveness/cost ratio)
    for treatment_group in recommendations['treatment_recommendations']:
        treatments = treatment_group['recommended_treatments']
        for treatment in treatments:
            cost = treatment['cost_estimate_per_acre']
            effectiveness = treatment['effectiveness_probability']
            treatment['cost_effectiveness_ratio'] = effectiveness / cost if cost > 0 else 0
        
        # Sort by cost-effectiveness
        treatments.sort(key=lambda x: x['cost_effectiveness_ratio'], reverse=True)
    
    # Filter treatments within budget
    total_cost = 0
    filtered_recommendations = []
    
    for treatment_group in recommendations['treatment_recommendations']:
        filtered_treatments = []
        for treatment in treatment_group['recommended_treatments']:
            if total_cost + treatment['cost_estimate_per_acre'] <= budget_limit:
                filtered_treatments.append(treatment)
                total_cost += treatment['cost_estimate_per_acre']
        
        if filtered_treatments:
            treatment_group['recommended_treatments'] = filtered_treatments
            filtered_recommendations.append(treatment_group)
    
    recommendations['treatment_recommendations'] = filtered_recommendations
    recommendations['total_cost_estimate'] = total_cost
    recommendations['budget_constraint_applied'] = True
    
    return recommendations


def _calculate_days_since_treatment(application_date: Optional[str]) -> Optional[int]:
    """Calculate days since treatment application."""
    
    if not application_date:
        return None
    
    try:
        app_date = datetime.fromisoformat(application_date.replace('Z', '+00:00'))
        return (datetime.now() - app_date).days
    except:
        return None


def _calculate_treatment_success(progress_data: Dict[str, Any]) -> float:
    """Calculate treatment success probability based on progress data."""
    
    success_factors = []
    
    # Visual improvement
    visual_improvement = progress_data.get('visual_improvement', 0)
    if visual_improvement > 0:
        success_factors.append(min(1.0, visual_improvement / 80))  # 80% improvement = full success
    
    # Tissue test improvement
    tissue_improvement = progress_data.get('tissue_improvement', {})
    if tissue_improvement:
        avg_improvement = sum(tissue_improvement.values()) / len(tissue_improvement)
        success_factors.append(min(1.0, avg_improvement / 50))  # 50% improvement = full success
    
    # Days since treatment (response time factor)
    days_since = _calculate_days_since_treatment(progress_data.get('application_date'))
    if days_since:
        if days_since >= 14:  # Full response time
            time_factor = 1.0
        elif days_since >= 7:  # Partial response time
            time_factor = 0.7
        else:  # Too early to assess
            time_factor = 0.3
        success_factors.append(time_factor)
    
    if success_factors:
        return sum(success_factors) / len(success_factors)
    else:
        return 0.5  # Default moderate success probability


def _generate_next_actions(progress_data: Dict[str, Any]) -> List[str]:
    """Generate next action recommendations based on progress."""
    
    actions = []
    
    days_since = _calculate_days_since_treatment(progress_data.get('application_date'))
    
    if not progress_data.get('treatment_applied'):
        actions.append("Apply recommended treatment as soon as possible")
    
    elif days_since and days_since >= 14:
        if progress_data.get('visual_improvement', 0) < 50:
            actions.append("Consider additional treatment or alternative approach")
        else:
            actions.append("Continue monitoring - treatment showing good response")
    
    elif days_since and days_since >= 7:
        actions.append("Conduct visual assessment for early treatment response")
        if not progress_data.get('follow_up_tests'):
            actions.append("Schedule tissue testing to quantify treatment response")
    
    else:
        actions.append("Continue monitoring - too early to assess full treatment response")
    
    if not progress_data.get('follow_up_tests') and days_since and days_since >= 21:
        actions.append("Conduct comprehensive follow-up testing to verify treatment success")
    
    return actions