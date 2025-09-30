"""
Comprehensive Regulatory Compliance Service.

This service provides automated regulatory compliance monitoring, assessment,
and reporting for fertilizer applications and agricultural practices.
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
import asyncio
from decimal import Decimal

from ..models.environmental_models import (
    RegulatoryRule, ComplianceAssessment, EnvironmentalImpactAssessment,
    SustainabilityMetrics, ComplianceReport, RegulatoryUpdate,
    RegulationType, ComplianceStatus, EnvironmentalImpactLevel,
    ComplianceRequest, ComplianceResponse, ComplianceValidator
)
from ..database.regulatory_compliance_db import RegulatoryComplianceDB

logger = logging.getLogger(__name__)


class RegulatoryComplianceService:
    """Comprehensive regulatory compliance service."""
    
    def __init__(self, db_path: str = "regulatory_compliance.db"):
        self.db = RegulatoryComplianceDB(db_path)
        self.validator = ComplianceValidator()
        
        # Initialize with common regulatory rules
        asyncio.create_task(self._initialize_regulatory_rules())
    
    async def _initialize_regulatory_rules(self):
        """Initialize common regulatory rules."""
        try:
            # Check if rules already exist
            existing_rules = await self.db.get_regulatory_rules()
            if existing_rules:
                logger.info(f"Found {len(existing_rules)} existing regulatory rules")
                return
            
            # Create common federal regulations
            federal_rules = [
                RegulatoryRule(
                    rule_id="EPA_CWA_NPDES",
                    regulation_type=RegulationType.FEDERAL,
                    jurisdiction="Federal",
                    title="Clean Water Act - NPDES Permits",
                    description="National Pollutant Discharge Elimination System permits for agricultural operations",
                    max_application_rate=Decimal("200"),  # lbs N/acre/year
                    application_timing_restrictions=["winter_application_prohibited"],
                    buffer_zone_requirements=Decimal("100"),  # feet from water bodies
                    water_body_protection=True,
                    record_keeping_required=True,
                    reporting_requirements=["annual_nutrient_management_plan"],
                    effective_date=date(1972, 10, 18),
                    source_url="https://www.epa.gov/npdes"
                ),
                RegulatoryRule(
                    rule_id="EPA_CAFO_RULE",
                    regulation_type=RegulationType.FEDERAL,
                    jurisdiction="Federal",
                    title="Concentrated Animal Feeding Operations Rule",
                    description="Regulations for large animal feeding operations",
                    max_application_rate=Decimal("150"),  # lbs N/acre/year
                    application_timing_restrictions=["frozen_ground_prohibited"],
                    buffer_zone_requirements=Decimal("150"),
                    water_body_protection=True,
                    record_keeping_required=True,
                    reporting_requirements=["nutrient_management_plan", "annual_reporting"],
                    effective_date=date(2003, 2, 12),
                    source_url="https://www.epa.gov/agriculture/animal-feeding-operations-afos"
                ),
                RegulatoryRule(
                    rule_id="USDA_NRCS_590",
                    regulation_type=RegulationType.CONSERVATION_PROGRAM,
                    jurisdiction="Federal",
                    title="USDA NRCS Standard 590 - Nutrient Management",
                    description="Nutrient management standard for conservation programs",
                    max_application_rate=Decimal("180"),  # lbs N/acre/year
                    application_timing_restrictions=["wet_soil_conditions"],
                    buffer_zone_requirements=Decimal("50"),
                    water_body_protection=True,
                    record_keeping_required=True,
                    reporting_requirements=["nutrient_management_plan"],
                    effective_date=date(2017, 1, 1),
                    source_url="https://www.nrcs.usda.gov/wps/portal/nrcs/detail/national/technical/cp/nc/"
                )
            ]
            
            # Create state-level regulations (example for Iowa)
            state_rules = [
                RegulatoryRule(
                    rule_id="IOWA_NUTRIENT_REDUCTION",
                    regulation_type=RegulationType.STATE,
                    jurisdiction="Iowa",
                    title="Iowa Nutrient Reduction Strategy",
                    description="Voluntary nutrient reduction strategy for Iowa agriculture",
                    max_application_rate=Decimal("160"),  # lbs N/acre/year
                    application_timing_restrictions=["fall_application_restricted"],
                    buffer_zone_requirements=Decimal("30"),
                    water_body_protection=True,
                    record_keeping_required=True,
                    reporting_requirements=["annual_nutrient_plan"],
                    effective_date=date(2013, 1, 1),
                    source_url="https://www.nutrientstrategy.iastate.edu/"
                ),
                RegulatoryRule(
                    rule_id="IOWA_WATER_QUALITY",
                    regulation_type=RegulationType.STATE,
                    jurisdiction="Iowa",
                    title="Iowa Water Quality Initiative",
                    description="State water quality improvement initiative",
                    max_application_rate=Decimal("140"),  # lbs N/acre/year
                    application_timing_restrictions=["winter_application_prohibited"],
                    buffer_zone_requirements=Decimal("25"),
                    water_body_protection=True,
                    record_keeping_required=True,
                    reporting_requirements=["water_quality_reporting"],
                    effective_date=date(2013, 1, 1),
                    source_url="https://www.iowaagriculture.gov/waterquality/"
                )
            ]
            
            # Create local regulations (example)
            local_rules = [
                RegulatoryRule(
                    rule_id="LOCAL_WATERSHED_PROTECTION",
                    regulation_type=RegulationType.LOCAL,
                    jurisdiction="Local Watershed District",
                    title="Local Watershed Protection Ordinance",
                    description="Local watershed protection requirements",
                    max_application_rate=Decimal("120"),  # lbs N/acre/year
                    application_timing_restrictions=["spring_application_preferred"],
                    buffer_zone_requirements=Decimal("75"),
                    water_body_protection=True,
                    record_keeping_required=True,
                    reporting_requirements=["quarterly_reporting"],
                    effective_date=date(2020, 1, 1),
                    source_url="https://example-watershed-district.org/"
                )
            ]
            
            # Insert all rules
            all_rules = federal_rules + state_rules + local_rules
            for rule in all_rules:
                await self.db.create_regulatory_rule(rule)
            
            logger.info(f"Initialized {len(all_rules)} regulatory rules")
            
        except Exception as e:
            logger.error(f"Error initializing regulatory rules: {e}")
    
    async def assess_compliance(
        self,
        request: ComplianceRequest
    ) -> ComplianceResponse:
        """
        Perform comprehensive compliance assessment for a field.
        
        Args:
            request: Compliance assessment request
            
        Returns:
            Comprehensive compliance assessment response
        """
        start_time = datetime.utcnow()
        
        try:
            # Get applicable regulatory rules
            applicable_rules = await self._get_applicable_rules(
                request.field_id,
                request.regulation_types,
                request.jurisdiction
            )
            
            # Perform compliance assessment
            compliance_assessment = await self._perform_compliance_assessment(
                request.field_id,
                request.user_id,
                applicable_rules
            )
            
            # Perform environmental impact assessment if requested
            environmental_assessment = None
            if request.include_environmental_assessment:
                environmental_assessment = await self._perform_environmental_assessment(
                    request.field_id
                )
            
            # Calculate sustainability metrics if requested
            sustainability_metrics = None
            if request.include_sustainability_metrics:
                sustainability_metrics = await self._calculate_sustainability_metrics(
                    request.field_id
                )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                compliance_assessment,
                environmental_assessment,
                sustainability_metrics
            )
            
            # Identify critical issues
            critical_issues = await self._identify_critical_issues(
                compliance_assessment,
                environmental_assessment
            )
            
            # Create response
            response = ComplianceResponse(
                assessment_id=compliance_assessment.assessment_id,
                field_id=request.field_id,
                compliance_assessment=compliance_assessment,
                environmental_assessment=environmental_assessment,
                sustainability_metrics=sustainability_metrics,
                overall_compliance_status=compliance_assessment.overall_status,
                critical_issues=critical_issues,
                recommendations=recommendations,
                processing_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
            # Store assessment in database
            await self.db.create_compliance_assessment(compliance_assessment)
            if environmental_assessment:
                await self.db.create_environmental_assessment(environmental_assessment)
            if sustainability_metrics:
                await self.db.create_sustainability_metrics(sustainability_metrics)
            
            return response
            
        except Exception as e:
            logger.error(f"Error performing compliance assessment: {e}")
            raise
    
    async def _get_applicable_rules(
        self,
        field_id: UUID,
        regulation_types: Optional[List[RegulationType]] = None,
        jurisdiction: Optional[str] = None
    ) -> List[RegulatoryRule]:
        """Get regulatory rules applicable to a field."""
        try:
            # In a real implementation, this would consider:
            # - Field location (state, county, watershed)
            # - Field characteristics (soil type, slope, proximity to water)
            # - Farm size and type
            # - Current practices
            
            rules = await self.db.get_regulatory_rules(
                regulation_type=None,  # Get all types for now
                jurisdiction=jurisdiction,
                active_only=True
            )
            
            # Filter by regulation types if specified
            if regulation_types:
                rules = [rule for rule in rules if rule.regulation_type in regulation_types]
            
            # In production, add field-specific filtering logic here
            return rules
            
        except Exception as e:
            logger.error(f"Error getting applicable rules: {e}")
            return []
    
    async def _perform_compliance_assessment(
        self,
        field_id: UUID,
        user_id: UUID,
        applicable_rules: List[RegulatoryRule]
    ) -> ComplianceAssessment:
        """Perform compliance assessment against applicable rules."""
        try:
            # In a real implementation, this would:
            # - Get field data (soil tests, application history, etc.)
            # - Get current fertilizer plan
            # - Check against each applicable rule
            # - Calculate compliance score
            
            violations = []
            compliance_score = 1.0
            risk_factors = []
            
            # Simulate compliance checking
            for rule in applicable_rules:
                # Check application rates
                if rule.max_application_rate:
                    # Simulate checking against planned application rate
                    planned_rate = Decimal("150")  # This would come from fertilizer plan
                    if not self.validator.validate_application_rate(planned_rate, rule):
                        violations.append({
                            "rule_id": rule.rule_id,
                            "violation_type": "exceeds_max_application_rate",
                            "description": f"Planned rate {planned_rate} exceeds maximum {rule.max_application_rate}",
                            "severity": "high"
                        })
                        compliance_score -= 0.2
                        risk_factors.append("High application rate")
                
                # Check buffer zones
                if rule.buffer_zone_requirements:
                    # Simulate checking buffer zone distance
                    buffer_distance = Decimal("50")  # This would come from field data
                    if not self.validator.validate_buffer_zone(buffer_distance, rule):
                        violations.append({
                            "rule_id": rule.rule_id,
                            "violation_type": "insufficient_buffer_zone",
                            "description": f"Buffer zone {buffer_distance} feet is less than required {rule.buffer_zone_requirements}",
                            "severity": "medium"
                        })
                        compliance_score -= 0.15
                        risk_factors.append("Insufficient buffer zone")
                
                # Check timing restrictions
                if rule.application_timing_restrictions:
                    # Simulate checking application timing
                    application_date = date.today()  # This would come from fertilizer plan
                    if not self.validator.validate_timing_restrictions(application_date, rule):
                        violations.append({
                            "rule_id": rule.rule_id,
                            "violation_type": "timing_restriction_violation",
                            "description": f"Application timing violates restrictions: {rule.application_timing_restrictions}",
                            "severity": "medium"
                        })
                        compliance_score -= 0.1
                        risk_factors.append("Timing restriction violation")
            
            # Determine overall status
            if compliance_score >= 0.9:
                overall_status = ComplianceStatus.COMPLIANT
            elif compliance_score >= 0.7:
                overall_status = ComplianceStatus.AT_RISK
            elif compliance_score >= 0.5:
                overall_status = ComplianceStatus.REQUIRES_REVIEW
            else:
                overall_status = ComplianceStatus.NON_COMPLIANT
            
            # Determine risk level
            if any(v.get("severity") == "high" for v in violations):
                risk_level = EnvironmentalImpactLevel.HIGH
            elif any(v.get("severity") == "medium" for v in violations):
                risk_level = EnvironmentalImpactLevel.MODERATE
            else:
                risk_level = EnvironmentalImpactLevel.LOW
            
            return ComplianceAssessment(
                field_id=field_id,
                user_id=user_id,
                regulation_type=RegulationType.FEDERAL,  # Default for now
                jurisdiction="Federal",
                overall_status=overall_status,
                compliance_score=max(0.0, compliance_score),
                applicable_rules=applicable_rules,
                violations=violations,
                recommendations=await self._generate_compliance_recommendations(violations),
                risk_level=risk_level,
                risk_factors=risk_factors,
                notes="Automated compliance assessment"
            )
            
        except Exception as e:
            logger.error(f"Error performing compliance assessment: {e}")
            raise
    
    async def _perform_environmental_assessment(
        self,
        field_id: UUID
    ) -> EnvironmentalImpactAssessment:
        """Perform environmental impact assessment."""
        try:
            # In a real implementation, this would:
            # - Analyze soil characteristics
            # - Consider weather patterns
            # - Assess proximity to water bodies
            # - Calculate nutrient loss potential
            # - Use environmental models (SWAT, APEX, etc.)
            
            # Simulate environmental assessment
            nutrient_runoff_risk = EnvironmentalImpactLevel.MODERATE
            groundwater_contamination_risk = EnvironmentalImpactLevel.LOW
            air_quality_impact = EnvironmentalImpactLevel.LOW
            soil_health_impact = EnvironmentalImpactLevel.MODERATE
            
            # Simulate quantified impacts
            estimated_nitrogen_loss = Decimal("25.5")  # lbs/acre
            estimated_phosphorus_loss = Decimal("2.1")  # lbs/acre
            carbon_footprint = Decimal("45.2")  # kg CO2/acre
            
            # Generate mitigation recommendations
            recommended_mitigation = [
                "Implement cover crops to reduce nutrient loss",
                "Add buffer strips along field edges",
                "Use split application timing",
                "Consider precision application technology"
            ]
            
            buffer_zone_recommendations = Decimal("50")  # feet
            
            return EnvironmentalImpactAssessment(
                field_id=field_id,
                fertilizer_plan_id=UUID(),  # Would come from actual plan
                nutrient_runoff_risk=nutrient_runoff_risk,
                groundwater_contamination_risk=groundwater_contamination_risk,
                air_quality_impact=air_quality_impact,
                soil_health_impact=soil_health_impact,
                estimated_nitrogen_loss=estimated_nitrogen_loss,
                estimated_phosphorus_loss=estimated_phosphorus_loss,
                carbon_footprint=carbon_footprint,
                recommended_mitigation=recommended_mitigation,
                buffer_zone_recommendations=buffer_zone_recommendations,
                assessment_method="Automated Environmental Assessment",
                confidence_level=0.85
            )
            
        except Exception as e:
            logger.error(f"Error performing environmental assessment: {e}")
            raise
    
    async def _calculate_sustainability_metrics(
        self,
        field_id: UUID
    ) -> SustainabilityMetrics:
        """Calculate sustainability metrics for a field."""
        try:
            # In a real implementation, this would:
            # - Analyze nutrient use efficiency
            # - Calculate soil health indicators
            # - Assess economic sustainability
            # - Consider long-term environmental impact
            
            # Simulate sustainability calculations
            nitrogen_use_efficiency = 0.75
            phosphorus_use_efficiency = 0.68
            potassium_use_efficiency = 0.82
            
            soil_organic_matter_change = Decimal("0.2")  # % increase
            erosion_reduction = 0.15
            water_quality_score = 0.78
            
            cost_per_unit_yield = Decimal("2.45")  # $/bushel
            profitability_index = 1.25
            
            # Calculate overall sustainability score
            sustainability_score = (
                nitrogen_use_efficiency * 0.25 +
                phosphorus_use_efficiency * 0.20 +
                potassium_use_efficiency * 0.20 +
                water_quality_score * 0.20 +
                erosion_reduction * 0.15
            )
            
            return SustainabilityMetrics(
                field_id=field_id,
                assessment_period=f"{datetime.now().year}",
                nitrogen_use_efficiency=nitrogen_use_efficiency,
                phosphorus_use_efficiency=phosphorus_use_efficiency,
                potassium_use_efficiency=potassium_use_efficiency,
                soil_organic_matter_change=soil_organic_matter_change,
                erosion_reduction=erosion_reduction,
                water_quality_score=water_quality_score,
                cost_per_unit_yield=cost_per_unit_yield,
                profitability_index=profitability_index,
                sustainability_score=sustainability_score,
                data_sources=["Soil tests", "Yield data", "Application records", "Weather data"]
            )
            
        except Exception as e:
            logger.error(f"Error calculating sustainability metrics: {e}")
            raise
    
    async def _generate_compliance_recommendations(
        self,
        violations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate compliance recommendations based on violations."""
        recommendations = []
        
        for violation in violations:
            violation_type = violation.get("violation_type")
            
            if violation_type == "exceeds_max_application_rate":
                recommendations.append("Reduce fertilizer application rate to comply with regulations")
            elif violation_type == "insufficient_buffer_zone":
                recommendations.append("Increase buffer zone distance or relocate application area")
            elif violation_type == "timing_restriction_violation":
                recommendations.append("Adjust application timing to comply with seasonal restrictions")
            else:
                recommendations.append("Review and adjust practices to ensure compliance")
        
        # Add general recommendations
        if not recommendations:
            recommendations.extend([
                "Maintain detailed application records",
                "Regular soil testing for nutrient management",
                "Consider precision application technologies",
                "Implement conservation practices"
            ])
        
        return recommendations
    
    async def _generate_recommendations(
        self,
        compliance_assessment: ComplianceAssessment,
        environmental_assessment: Optional[EnvironmentalImpactAssessment],
        sustainability_metrics: Optional[SustainabilityMetrics]
    ) -> List[str]:
        """Generate comprehensive recommendations."""
        recommendations = []
        
        # Add compliance recommendations
        recommendations.extend(compliance_assessment.recommendations)
        
        # Add environmental recommendations
        if environmental_assessment:
            recommendations.extend(environmental_assessment.recommended_mitigation)
        
        # Add sustainability recommendations
        if sustainability_metrics:
            if sustainability_metrics.nitrogen_use_efficiency < 0.7:
                recommendations.append("Improve nitrogen use efficiency through precision application")
            if sustainability_metrics.water_quality_score < 0.8:
                recommendations.append("Implement additional water quality protection measures")
            if sustainability_metrics.sustainability_score < 0.75:
                recommendations.append("Consider adopting additional sustainable practices")
        
        # Remove duplicates and return
        return list(set(recommendations))
    
    async def _identify_critical_issues(
        self,
        compliance_assessment: ComplianceAssessment,
        environmental_assessment: Optional[EnvironmentalImpactAssessment]
    ) -> List[str]:
        """Identify critical compliance and environmental issues."""
        critical_issues = []
        
        # Check for high-severity violations
        for violation in compliance_assessment.violations:
            if violation.get("severity") == "high":
                critical_issues.append(f"High-severity violation: {violation.get('description')}")
        
        # Check for high environmental risk
        if environmental_assessment:
            if environmental_assessment.nutrient_runoff_risk == EnvironmentalImpactLevel.HIGH:
                critical_issues.append("High nutrient runoff risk detected")
            if environmental_assessment.groundwater_contamination_risk == EnvironmentalImpactLevel.HIGH:
                critical_issues.append("High groundwater contamination risk detected")
        
        return critical_issues
    
    async def get_compliance_history(
        self,
        field_id: UUID,
        limit: int = 10
    ) -> List[ComplianceAssessment]:
        """Get compliance assessment history for a field."""
        try:
            return await self.db.get_compliance_assessments(
                field_id=field_id,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Error getting compliance history: {e}")
            return []
    
    async def generate_compliance_report(
        self,
        farm_id: UUID,
        report_period: str,
        generated_by: str = "system"
    ) -> ComplianceReport:
        """Generate comprehensive compliance report for a farm."""
        try:
            # Get all assessments for the farm
            assessments = await self.db.get_compliance_assessments()
            
            # Filter by farm (in real implementation, would join with farm data)
            farm_assessments = assessments  # Simplified for now
            
            # Calculate summary statistics
            compliance_summary = {}
            environmental_summary = {}
            
            for assessment in farm_assessments:
                status = assessment.overall_status.value
                compliance_summary[status] = compliance_summary.get(status, 0) + 1
            
            # Get environmental assessments
            env_assessments = []
            for assessment in farm_assessments:
                # In real implementation, would get environmental assessments
                pass
            
            # Generate report
            report = ComplianceReport(
                farm_id=farm_id,
                report_period=report_period,
                total_fields_assessed=len(farm_assessments),
                compliance_summary=compliance_summary,
                environmental_summary=environmental_summary,
                critical_violations=await self._identify_critical_violations(farm_assessments),
                improvement_areas=await self._identify_improvement_areas(farm_assessments),
                best_practices=await self._identify_best_practices(farm_assessments),
                priority_actions=await self._generate_priority_actions(farm_assessments),
                long_term_goals=await self._generate_long_term_goals(farm_assessments),
                generated_by=generated_by
            )
            
            # Store report
            await self.db.create_compliance_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            raise
    
    async def _identify_critical_violations(
        self,
        assessments: List[ComplianceAssessment]
    ) -> List[Dict[str, Any]]:
        """Identify critical violations across assessments."""
        critical_violations = []
        
        for assessment in assessments:
            for violation in assessment.violations:
                if violation.get("severity") == "high":
                    critical_violations.append({
                        "field_id": str(assessment.field_id),
                        "violation": violation,
                        "assessment_date": assessment.assessment_date
                    })
        
        return critical_violations
    
    async def _identify_improvement_areas(
        self,
        assessments: List[ComplianceAssessment]
    ) -> List[str]:
        """Identify areas needing improvement."""
        improvement_areas = []
        
        # Analyze common issues
        common_violations = {}
        for assessment in assessments:
            for violation in assessment.violations:
                violation_type = violation.get("violation_type")
                common_violations[violation_type] = common_violations.get(violation_type, 0) + 1
        
        # Generate improvement recommendations
        for violation_type, count in common_violations.items():
            if count > len(assessments) * 0.3:  # If >30% of assessments have this issue
                if violation_type == "exceeds_max_application_rate":
                    improvement_areas.append("Application rate management")
                elif violation_type == "insufficient_buffer_zone":
                    improvement_areas.append("Buffer zone implementation")
                elif violation_type == "timing_restriction_violation":
                    improvement_areas.append("Application timing optimization")
        
        return improvement_areas
    
    async def _identify_best_practices(
        self,
        assessments: List[ComplianceAssessment]
    ) -> List[str]:
        """Identify best practices from compliant assessments."""
        best_practices = []
        
        compliant_assessments = [
            a for a in assessments 
            if a.overall_status == ComplianceStatus.COMPLIANT
        ]
        
        if compliant_assessments:
            best_practices.extend([
                "Maintaining detailed application records",
                "Regular soil testing and analysis",
                "Proper buffer zone implementation",
                "Timing applications according to regulations"
            ])
        
        return best_practices
    
    async def _generate_priority_actions(
        self,
        assessments: List[ComplianceAssessment]
    ) -> List[str]:
        """Generate priority actions based on assessments."""
        priority_actions = []
        
        # Check for non-compliant assessments
        non_compliant = [
            a for a in assessments 
            if a.overall_status == ComplianceStatus.NON_COMPLIANT
        ]
        
        if non_compliant:
            priority_actions.append("Address non-compliance issues immediately")
        
        # Check for high-risk assessments
        high_risk = [
            a for a in assessments 
            if a.risk_level == EnvironmentalImpactLevel.HIGH
        ]
        
        if high_risk:
            priority_actions.append("Implement additional environmental protection measures")
        
        return priority_actions
    
    async def _generate_long_term_goals(
        self,
        assessments: List[ComplianceAssessment]
    ) -> List[str]:
        """Generate long-term sustainability goals."""
        return [
            "Achieve 100% compliance across all fields",
            "Improve nutrient use efficiency by 15%",
            "Reduce environmental impact by 20%",
            "Implement precision agriculture technologies",
            "Develop comprehensive conservation plan"
        ]
    
    async def check_regulatory_updates(self) -> List[RegulatoryUpdate]:
        """Check for new regulatory updates."""
        try:
            # In a real implementation, this would:
            # - Monitor regulatory agency websites
            # - Subscribe to regulatory update feeds
            # - Check for new regulations and changes
            
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error checking regulatory updates: {e}")
            return []
    
    async def get_compliance_statistics(
        self,
        farm_id: Optional[UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get compliance statistics for reporting."""
        try:
            return await self.db.get_compliance_statistics(
                farm_id=farm_id,
                date_from=date_from,
                date_to=date_to
            )
        except Exception as e:
            logger.error(f"Error getting compliance statistics: {e}")
            return {}
