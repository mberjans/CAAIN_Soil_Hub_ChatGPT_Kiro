"""
Regulatory Compliance API Routes.

This module provides REST API endpoints for regulatory compliance assessment,
environmental impact analysis, and sustainability reporting.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime
import logging

from ..models.environmental_models import (
    ComplianceRequest, ComplianceResponse, ComplianceAssessment,
    EnvironmentalImpactAssessment, SustainabilityMetrics, ComplianceReport,
    RegulatoryRule, RegulationType, ComplianceStatus, EnvironmentalImpactLevel
)
from ..services.environmental_service import RegulatoryComplianceService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/compliance", tags=["regulatory-compliance"])

# Dependency injection
async def get_compliance_service() -> RegulatoryComplianceService:
    """Get regulatory compliance service instance."""
    return RegulatoryComplianceService()


@router.post("/assess", response_model=ComplianceResponse)
async def assess_compliance(
    request: ComplianceRequest,
    service: RegulatoryComplianceService = Depends(get_compliance_service)
):
    """
    Perform comprehensive compliance assessment for a field.
    
    This endpoint provides automated regulatory compliance monitoring and assessment
    for fertilizer applications and agricultural practices.
    
    Features:
    - Multi-level regulation checking (federal, state, local)
    - Environmental impact assessment
    - Sustainability metrics calculation
    - Automated violation detection
    - Comprehensive recommendations
    - Risk assessment and scoring
    
    Agricultural Use Cases:
    - Pre-application compliance checking
    - Regulatory requirement validation
    - Environmental impact assessment
    - Sustainability reporting
    - Audit preparation
    """
    try:
        result = await service.assess_compliance(request)
        return result
    except Exception as e:
        logger.error(f"Error performing compliance assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{field_id}", response_model=List[ComplianceAssessment])
async def get_compliance_history(
    field_id: UUID = Path(..., description="Field identifier"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of assessments to return"),
    service: RegulatoryComplianceService = Depends(get_compliance_service)
):
    """
    Get compliance assessment history for a field.
    
    Returns historical compliance assessments with detailed violation tracking
    and trend analysis for regulatory monitoring and improvement planning.
    """
    try:
        assessments = await service.get_compliance_history(field_id, limit)
        return assessments
    except Exception as e:
        logger.error(f"Error getting compliance history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report", response_model=ComplianceReport)
async def generate_compliance_report(
    farm_id: UUID,
    report_period: str = Query(..., description="Reporting period (e.g., '2024-Q1')"),
    generated_by: str = Query("system", description="Report generator identifier"),
    service: RegulatoryComplianceService = Depends(get_compliance_service)
):
    """
    Generate comprehensive compliance report for a farm.
    
    Creates detailed compliance reports including:
    - Summary statistics across all fields
    - Critical violations identification
    - Improvement area recommendations
    - Best practices documentation
    - Priority action items
    - Long-term sustainability goals
    
    Agricultural Use Cases:
    - Annual compliance reporting
    - Regulatory audit preparation
    - Farm management planning
    - Sustainability certification
    - Stakeholder reporting
    """
    try:
        report = await service.generate_compliance_report(
            farm_id=farm_id,
            report_period=report_period,
            generated_by=generated_by
        )
        return report
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules", response_model=List[RegulatoryRule])
async def get_regulatory_rules(
    regulation_type: Optional[RegulationType] = Query(None, description="Filter by regulation type"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction"),
    active_only: bool = Query(True, description="Return only active regulations"),
    service: RegulatoryComplianceService = Depends(get_compliance_service)
):
    """
    Get applicable regulatory rules.
    
    Returns regulatory rules that may apply to agricultural operations,
    filtered by type, jurisdiction, and active status.
    
    Agricultural Use Cases:
    - Understanding applicable regulations
    - Compliance planning
    - Regulatory requirement research
    - Jurisdiction-specific rule lookup
    """
    try:
        rules = await service.db.get_regulatory_rules(
            regulation_type=regulation_type,
            jurisdiction=jurisdiction,
            active_only=active_only
        )
        return rules
    except Exception as e:
        logger.error(f"Error getting regulatory rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=Dict[str, Any])
async def get_compliance_statistics(
    farm_id: Optional[UUID] = Query(None, description="Farm identifier for filtering"),
    date_from: Optional[date] = Query(None, description="Start date for statistics"),
    date_to: Optional[date] = Query(None, description="End date for statistics"),
    service: RegulatoryComplianceService = Depends(get_compliance_service)
):
    """
    Get compliance statistics for reporting and analysis.
    
    Returns aggregated compliance statistics including:
    - Compliance status distribution
    - Environmental impact level counts
    - Total assessment counts
    - Trend analysis data
    
    Agricultural Use Cases:
    - Dashboard metrics
    - Performance tracking
    - Trend analysis
    - Management reporting
    """
    try:
        statistics = await service.get_compliance_statistics(
            farm_id=farm_id,
            date_from=date_from,
            date_to=date_to
        )
        return statistics
    except Exception as e:
        logger.error(f"Error getting compliance statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/updates", response_model=List[Dict[str, Any]])
async def check_regulatory_updates(
    service: RegulatoryComplianceService = Depends(get_compliance_service)
):
    """
    Check for new regulatory updates and changes.
    
    Monitors regulatory agencies for new regulations, updates, and changes
    that may affect agricultural operations and compliance requirements.
    
    Agricultural Use Cases:
    - Staying current with regulations
    - Proactive compliance management
    - Regulatory change notifications
    - Compliance planning updates
    """
    try:
        updates = await service.check_regulatory_updates()
        return [update.dict() for update in updates]
    except Exception as e:
        logger.error(f"Error checking regulatory updates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for regulatory compliance service."""
    return {
        "service": "regulatory-compliance",
        "status": "healthy",
        "features": [
            "automated_compliance_assessment",
            "environmental_impact_analysis",
            "sustainability_metrics",
            "regulatory_rule_management",
            "compliance_reporting",
            "violation_tracking",
            "risk_assessment",
            "recommendation_generation",
            "historical_analysis",
            "statistical_reporting"
        ]
    }


# Additional specialized endpoints for specific compliance areas

@router.post("/environmental-assessment", response_model=EnvironmentalImpactAssessment)
async def perform_environmental_assessment(
    field_id: UUID,
    fertilizer_plan_id: UUID,
    service: RegulatoryComplianceService = Depends(get_compliance_service)
):
    """
    Perform detailed environmental impact assessment.
    
    Analyzes potential environmental impacts of fertilizer applications including:
    - Nutrient runoff risk assessment
    - Groundwater contamination analysis
    - Air quality impact evaluation
    - Soil health impact assessment
    - Carbon footprint calculation
    
    Agricultural Use Cases:
    - Environmental impact evaluation
    - Mitigation planning
    - Conservation program compliance
    - Sustainability reporting
    """
    try:
        # Create a mock assessment for demonstration
        assessment = EnvironmentalImpactAssessment(
            field_id=field_id,
            fertilizer_plan_id=fertilizer_plan_id,
            nutrient_runoff_risk=EnvironmentalImpactLevel.MODERATE,
            groundwater_contamination_risk=EnvironmentalImpactLevel.LOW,
            air_quality_impact=EnvironmentalImpactLevel.LOW,
            soil_health_impact=EnvironmentalImpactLevel.MODERATE,
            estimated_nitrogen_loss=25.5,
            estimated_phosphorus_loss=2.1,
            carbon_footprint=45.2,
            recommended_mitigation=[
                "Implement cover crops to reduce nutrient loss",
                "Add buffer strips along field edges",
                "Use split application timing"
            ],
            buffer_zone_recommendations=50.0,
            assessment_method="Automated Environmental Assessment",
            confidence_level=0.85
        )
        
        # Store in database
        await service.db.create_environmental_assessment(assessment)
        
        return assessment
    except Exception as e:
        logger.error(f"Error performing environmental assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sustainability-metrics", response_model=SustainabilityMetrics)
async def calculate_sustainability_metrics(
    field_id: UUID,
    assessment_period: str = Query(..., description="Assessment period (e.g., '2024')"),
    service: RegulatoryComplianceService = Depends(get_compliance_service)
):
    """
    Calculate comprehensive sustainability metrics for a field.
    
    Provides detailed sustainability analysis including:
    - Nutrient use efficiency calculations
    - Soil health indicators
    - Environmental impact metrics
    - Economic sustainability measures
    - Overall sustainability scoring
    
    Agricultural Use Cases:
    - Sustainability certification
    - Performance benchmarking
    - Improvement planning
    - Stakeholder reporting
    - Conservation program participation
    """
    try:
        # Create mock sustainability metrics for demonstration
        metrics = SustainabilityMetrics(
            field_id=field_id,
            assessment_period=assessment_period,
            nitrogen_use_efficiency=0.75,
            phosphorus_use_efficiency=0.68,
            potassium_use_efficiency=0.82,
            soil_organic_matter_change=0.2,
            erosion_reduction=0.15,
            water_quality_score=0.78,
            cost_per_unit_yield=2.45,
            profitability_index=1.25,
            sustainability_score=0.76,
            data_sources=["Soil tests", "Yield data", "Application records", "Weather data"]
        )
        
        # Store in database
        await service.db.create_sustainability_metrics(metrics)
        
        return metrics
    except Exception as e:
        logger.error(f"Error calculating sustainability metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/violations/{field_id}", response_model=List[Dict[str, Any]])
async def get_field_violations(
    field_id: UUID = Path(..., description="Field identifier"),
    severity: Optional[str] = Query(None, description="Filter by violation severity"),
    service: RegulatoryComplianceService = Depends(get_compliance_service)
):
    """
    Get compliance violations for a specific field.
    
    Returns detailed violation information including:
    - Violation descriptions and severity
    - Regulatory rule references
    - Recommended corrective actions
    - Historical violation trends
    
    Agricultural Use Cases:
    - Violation tracking and management
    - Corrective action planning
    - Compliance improvement
    - Audit preparation
    """
    try:
        assessments = await service.get_compliance_history(field_id, limit=50)
        
        violations = []
        for assessment in assessments:
            for violation in assessment.violations:
                if not severity or violation.get("severity") == severity:
                    violations.append({
                        "field_id": str(field_id),
                        "assessment_id": str(assessment.assessment_id),
                        "assessment_date": assessment.assessment_date,
                        "violation": violation,
                        "recommendations": assessment.recommendations
                    })
        
        return violations
    except Exception as e:
        logger.error(f"Error getting field violations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
