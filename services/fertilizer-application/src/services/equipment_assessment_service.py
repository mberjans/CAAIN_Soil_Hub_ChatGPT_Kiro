from typing import List, Optional
from uuid import UUID, uuid4
import time

from ..models.equipment_models import (
    EquipmentAssessmentResult,
    EquipmentItem,
    EquipmentSuitability,
    EquipmentUpgradeRecommendation,
    FarmInfrastructure,
)
from ..models.application_models import (
    EquipmentAssessmentRequest,
    EquipmentAssessmentResponse,
    EquipmentSpecification,
    IndividualEquipmentAssessment
)

class EquipmentAssessmentService:
    """Service for assessing farm equipment and infrastructure for fertilizer application."""

    def __init__(self):
        # Placeholder for integration with other services (e.g., Field Management, Cost Analysis)
        pass

    async def assess_farm_equipment_and_infrastructure(
        self, farm_infrastructure: FarmInfrastructure
    ) -> EquipmentAssessmentResult:
        """
        Performs a comprehensive assessment of existing farm equipment and infrastructure.

        Args:
            farm_infrastructure: Data model containing farm infrastructure details.

        Returns:
            An EquipmentAssessmentResult object with assessment scores and recommendations.
        """
        overall_score = self._calculate_overall_score(farm_infrastructure)
        suitability_results = self._assess_existing_equipment_suitability(
            farm_infrastructure.existing_equipment, farm_infrastructure.total_acres
        )
        upgrade_recommendations = self._generate_upgrade_recommendations(
            farm_infrastructure, suitability_results
        )
        identified_gaps = self._identify_gaps(farm_infrastructure, suitability_results)
        efficiency_opportunities = self._identify_efficiency_opportunities(
            farm_infrastructure, suitability_results
        )

        return EquipmentAssessmentResult(
            farm_location_id=farm_infrastructure.farm_location_id,
            overall_assessment_score=overall_score,
            equipment_suitability=suitability_results,
            upgrade_recommendations=upgrade_recommendations,
            identified_gaps=identified_gaps,
            efficiency_opportunities=efficiency_opportunities,
        )

    def _calculate_overall_score(self, farm_infrastructure: FarmInfrastructure) -> float:
        """
        Calculates an overall assessment score based on various farm infrastructure factors.
        This is a simplified calculation for demonstration.
        """
        score = (
            farm_infrastructure.total_acres / 1000  # Scale acres
            + (1 - farm_infrastructure.field_layout_complexity)  # Simpler layout is better
            + farm_infrastructure.access_road_quality
            + (farm_infrastructure.storage_capacity_tons / 500 if farm_infrastructure.storage_capacity_tons else 0)  # Scale storage
            + farm_infrastructure.labor_availability_score
        )
        # Normalize to a 0-1 range (example normalization, adjust as needed)
        normalized_score = min(1.0, score / 5.0)  # Assuming max score around 5 for these factors
        return normalized_score

    def _assess_existing_equipment_suitability(
        self, existing_equipment: List[EquipmentItem], total_acres: float
    ) -> List[EquipmentSuitability]:
        """
        Assesses the suitability of each piece of existing equipment.
        """
        suitability_list = []
        for item in existing_equipment:
            suitability_score = 0.5  # Default suitability
            reasons = []
            compatibility_issues = []

            # Example logic: Spreader capacity vs. farm size
            if item.type == "Spreader":
                if item.capacity_unit == "tons" and item.capacity_value * 10 < total_acres:
                    suitability_score -= 0.2
                    reasons.append("Spreader capacity might be too low for farm size.")
                    compatibility_issues.append("Capacity mismatch.")
                elif item.capacity_unit == "tons" and item.capacity_value * 50 > total_acres:
                    suitability_score += 0.1
                    reasons.append("Spreader capacity is well-suited for farm size.")

            # Example logic: Power requirement
            if item.power_requirement_hp and item.power_requirement_hp < 50:
                suitability_score -= 0.1
                reasons.append("Low horsepower might limit efficiency.")

            suitability_list.append(
                EquipmentSuitability(
                    equipment_id=item.equipment_id,
                    suitability_score=max(0.0, min(1.0, suitability_score)),
                    reasons=reasons,
                    compatibility_issues=compatibility_issues,
                )
            )
        return suitability_list

    def _generate_upgrade_recommendations(
        self, farm_infrastructure: FarmInfrastructure, suitability_results: List[EquipmentSuitability]
    ) -> List[EquipmentUpgradeRecommendation]:
        """
        Generates recommendations for equipment upgrades or new acquisitions.
        This is a simplified example.
        """
        recommendations = []
        # If no spreader is suitable or present, recommend one
        has_suitable_spreader = any(
            s.suitability_score > 0.7 and any(eq.type == "Spreader" for eq in farm_infrastructure.existing_equipment if eq.equipment_id == s.equipment_id)
            for s in suitability_results
        )
        if not has_suitable_spreader:
            recommendations.append(
                EquipmentUpgradeRecommendation(
                    recommendation_id=uuid4(),
                    equipment_name="High-Capacity Broadcast Spreader",
                    type="Spreader",
                    justification="Current spreading equipment is insufficient or unsuitable for farm size/needs.",
                    estimated_cost_usd=25000.0,
                    expected_benefits=["Increased efficiency", "Improved application uniformity"],
                    roi_estimate=0.15,
                )
            )
        return recommendations

    def _identify_gaps(
        self, farm_infrastructure: FarmInfrastructure, suitability_results: List[EquipmentSuitability]
    ) -> List[str]:
        """
        Identifies critical gaps in the farm's equipment or infrastructure.
        """
        gaps = []
        if not any(eq.type == "Spreader" for eq in farm_infrastructure.existing_equipment):
            gaps.append("No fertilizer spreader identified.")
        if farm_infrastructure.total_acres > 500 and not farm_infrastructure.storage_capacity_tons:
            gaps.append("Large farm size but no dedicated fertilizer storage capacity.")
        return gaps

    def _identify_efficiency_opportunities(
        self, farm_infrastructure: FarmInfrastructure, suitability_results: List[EquipmentSuitability]
    ) -> List[str]:
        """
        Identifies opportunities for improving efficiency.
        """
        opportunities = []
        if farm_infrastructure.field_layout_complexity > 0.7:
            opportunities.append("Consider field consolidation or optimizing field access for efficiency.")
        if farm_infrastructure.access_road_quality < 0.5:
            opportunities.append("Improve access road quality to reduce transport time and equipment wear.")
        return opportunities

    async def assess_farm_equipment(self, request: EquipmentAssessmentRequest) -> EquipmentAssessmentResponse:
        """
        Performs comprehensive equipment assessment for a farm based on the API request model.
        
        Args:
            request: EquipmentAssessmentRequest with farm characteristics and equipment inventory
            
        Returns:
            EquipmentAssessmentResponse with assessment results
        """
        start_time = time.time()
        
        # Convert API request model to internal service model
        existing_equipment = self._convert_equipment_specifications(request.current_equipment)
        
        farm_infrastructure = FarmInfrastructure(
            farm_location_id=UUID(int=0),  # Use a default UUID since not in API request
            total_acres=request.farm_size_acres,
            field_layout_complexity=self._calculate_layout_complexity(request),
            access_road_quality=self._determine_access_quality(request),
            storage_capacity_tons=self._extract_storage_capacity(request),
            labor_availability_score=self._determine_labor_availability(request),
            existing_equipment=existing_equipment
        )
        
        # Perform the assessment using the existing internal method
        assessment_result = await self.assess_farm_equipment_and_infrastructure(farm_infrastructure)
        
        # Convert results to API response format
        individual_assessments = self._convert_to_individual_assessments(
            request.current_equipment, assessment_result.equipment_suitability
        )
        
        # Calculate capacity analysis
        capacity_analysis = self._perform_capacity_analysis(request)
        
        # Generate cost-benefit analysis
        cost_benefit_analysis = self._generate_cost_benefit_analysis(assessment_result)
        
        # Determine upgrade priorities
        upgrade_priorities = self._determine_upgrade_priorities(assessment_result)
        
        # Prepare farm assessment data
        farm_assessment = {
            "farm_size_acres": request.farm_size_acres,
            "field_count": request.field_count,
            "average_field_size": request.average_field_size
        }
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Prepare comprehensive metadata
        metadata = {
            "overall_score": assessment_result.overall_assessment_score,
            "assessment_date": time.time(),
            "equipment_count": len(request.current_equipment)
        }
        
        return EquipmentAssessmentResponse(
            request_id=str(uuid4()),
            farm_assessment=farm_assessment,
            equipment_assessments=individual_assessments,
            upgrade_priorities=upgrade_priorities,
            capacity_analysis=capacity_analysis,
            cost_benefit_analysis=cost_benefit_analysis,
            processing_time_ms=processing_time_ms,
            metadata=metadata
        )
    
    def _convert_equipment_specifications(self, equipment_specs: List[EquipmentSpecification]) -> List[EquipmentItem]:
        """
        Convert API EquipmentSpecification to internal EquipmentItem model.
        """
        equipment_items = []
        for spec in equipment_specs:
            equipment_items.append(EquipmentItem(
                equipment_id=uuid4(),  # Generate new ID
                name=spec.equipment_type.value + " Equipment",
                type=spec.equipment_type.value,
                capacity_unit=spec.capacity_unit or "unknown",
                capacity_value=spec.capacity or 0.0,
                working_width_meters=None,  # Not in spec
                power_requirement_hp=None,  # Not in spec
                cost_usd=None,  # Not in spec
                maintenance_cost_annual_usd=spec.maintenance_cost_per_hour,  # Map to maintenance cost
                is_available=True
            ))
        return equipment_items
    
    def _calculate_layout_complexity(self, request: EquipmentAssessmentRequest) -> float:
        """
        Calculate field layout complexity based on field characteristics.
        0 = simple, 1 = complex
        """
        # Complex layout if farm has many small fields
        if request.field_count > 10 and request.average_field_size < 10:
            return 0.8
        elif request.field_count > 5 and request.average_field_size < 20:
            return 0.6
        else:
            return 0.3  # Relatively simple for larger fields
    
    def _determine_access_quality(self, request: EquipmentAssessmentRequest) -> float:
        """
        Determine access road quality based on available information.
        0 = poor, 1 = excellent
        """
        # Default to medium if no specific information
        return 0.5
    
    def _extract_storage_capacity(self, request: EquipmentAssessmentRequest) -> Optional[float]:
        """
        Extract storage capacity if available in request.
        """
        # For now, we'll use a simple estimation based on farm size
        # or we could extract from request if there's storage info
        return request.farm_size_acres * 0.1  # Rough estimate
    
    def _determine_labor_availability(self, request: EquipmentAssessmentRequest) -> float:
        """
        Determine labor availability score from request.
        0 = low, 1 = high
        """
        if request.labor_availability:
            if "high" in request.labor_availability.lower():
                return 0.8
            elif "medium" in request.labor_availability.lower():
                return 0.5
            elif "low" in request.labor_availability.lower():
                return 0.2
        # Default to 0.5 if no specific value provided
        return 0.5
    
    def _convert_to_individual_assessments(
        self, 
        equipment_specs: List[EquipmentSpecification], 
        suitability_results: List[EquipmentSuitability]
    ) -> List[IndividualEquipmentAssessment]:
        """
        Convert equipment suitability results to IndividualEquipmentAssessment.
        """
        assessments = []
        for i, spec in enumerate(equipment_specs):
            # Find corresponding suitability result
            suitability = None
            if i < len(suitability_results):
                suitability = suitability_results[i]
            
            efficiency_score = 0.7  # Default efficiency
            if suitability:
                efficiency_score = suitability.suitability_score
            
            assessment = IndividualEquipmentAssessment(
                equipment_id=uuid4(),  # Generate new ID
                efficiency_score=efficiency_score,
                maintenance_status="good",  # Default
                compatibility_score=efficiency_score,
                notes=f"Assessment for {spec.equipment_type.value} equipment"
            )
            assessments.append(assessment)
        
        return assessments
    
    def _perform_capacity_analysis(self, request: EquipmentAssessmentRequest) -> dict:
        """
        Perform capacity analysis of existing equipment versus farm needs.
        """
        analysis = {
            "total_farm_acres": request.farm_size_acres,
            "equipment_count": len(request.current_equipment),
            "capacity_summary": {},
            "adequacy_assessment": "unknown"
        }
        
        # Simple capacity analysis
        total_acres = request.farm_size_acres
        equipment_count = len(request.current_equipment)
        
        if equipment_count == 0:
            analysis["adequacy_assessment"] = "insufficient"
            analysis["notes"] = "No equipment identified for farm of this size"
        elif total_acres / equipment_count > 200:
            analysis["adequacy_assessment"] = "insufficient"
            analysis["notes"] = "Equipment-to-acre ratio may be too low"
        else:
            analysis["adequacy_assessment"] = "adequate"
            analysis["notes"] = "Equipment-to-acre ratio appears appropriate"
        
        return analysis
    
    def _generate_cost_benefit_analysis(self, assessment_result: EquipmentAssessmentResult) -> dict:
        """
        Generate cost-benefit analysis based on assessment results.
        """
        total_replacement_cost = sum(
            rec.estimated_cost_usd for rec in assessment_result.upgrade_recommendations
        )
        
        return {
            "total_replacement_cost_usd": total_replacement_cost,
            "upgrade_priority_count": len(assessment_result.upgrade_recommendations),
            "estimated_roi_range": {"min": 0.05, "max": 0.20},  # 5-20% range
            "estimated_payback_years": {"min": 2, "max": 5},
            "benefit_summary": [benefit for rec in assessment_result.upgrade_recommendations for benefit in rec.expected_benefits]
        }
    
    def _determine_upgrade_priorities(self, assessment_result: EquipmentAssessmentResult) -> List[str]:
        """
        Determine upgrade priorities based on assessment results.
        """
        priorities = []
        
        # Add priorities based on gaps
        for gap in assessment_result.identified_gaps:
            priorities.append(f"Address gap: {gap}")
        
        # Add priorities based on upgrade recommendations
        for rec in assessment_result.upgrade_recommendations:
            roi_text = f" (est. {rec.roi_estimate*100:.1f}% ROI)" if rec.roi_estimate else ""
            priorities.append(f"Upgrade: {rec.equipment_name} - {rec.justification}{roi_text}")
        
        # Add priorities based on efficiency opportunities
        for opportunity in assessment_result.efficiency_opportunities:
            priorities.append(f"Efficiency opportunity: {opportunity}")
        
        return priorities
    
    async def _analyze_farm_characteristics(self, request: EquipmentAssessmentRequest) -> dict:
        """
        Analyze farm characteristics for compatibility assessment.
        """
        return {
            "farm_size_category": self._categorize_farm_size(request.farm_size_acres),
            "field_complexity_score": self._calculate_layout_complexity(request),
            "total_field_acreage": request.farm_size_acres,
            "average_field_size": request.average_field_size,
            "equipment_intensity": len(request.current_equipment) / max(1, request.farm_size_acres)
        }
    
    def _categorize_farm_size(self, acres: float) -> str:
        """
        Categorize farm size.
        """
        if acres < 100:
            return "small"
        elif acres < 500:
            return "medium"
        elif acres < 2000:
            return "large"
        else:
            return "very_large"
    
    def _generate_compatibility_assessments(self, equipment_list: List, farm_analysis: dict) -> List:
        """
        Generate compatibility assessments for equipment.
        """
        # This is a placeholder method that would be called from the API
        # to return compatibility assessments
        return []
    
    def _calculate_fuel_efficiency_rating(self, equipment) -> float:
        """
        Calculate fuel efficiency rating for equipment.
        """
        return 0.7  # Default rating
    
    def _calculate_environmental_impact_score(self, equipment) -> float:
        """
        Calculate environmental impact score for equipment.
        """
        return 0.7  # Default score
    
    def _calculate_efficiency_rating(self, equipment) -> float:
        """
        Calculate efficiency rating for equipment.
        """
        return 0.7  # Default rating
    
    def _compare_to_benchmarks(self, equipment) -> dict:
        """
        Compare equipment to industry benchmarks.
        """
        return {"rating": "average", "comparison": "meets standards"}
    
    def _calculate_industry_ranking(self, equipment) -> str:
        """
        Calculate industry ranking for equipment.
        """
        return "mid-tier"
    
    def _identify_performance_improvements(self, equipment) -> List[str]:
        """
        Identify performance improvement opportunities.
        """
        return ["regular maintenance", "proper calibration"]
    
    def _calculate_overall_farm_performance(self, comparison_results) -> float:
        """
        Calculate overall farm performance score.
        """
        return 0.7  # Default performance score
    
    def _generate_benchmark_summary(self, comparison_results) -> dict:
        """
        Generate benchmark comparison summary.
        """
        return {"summary": "equipment meets basic industry standards"}