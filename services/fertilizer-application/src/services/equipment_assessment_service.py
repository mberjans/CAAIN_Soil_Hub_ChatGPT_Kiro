"""
Equipment Assessment Service for comprehensive farm equipment evaluation and optimization.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from uuid import uuid4

from src.models.application_models import EquipmentAssessmentRequest, EquipmentAssessmentResponse
from src.models.equipment_models import (
    Equipment, EquipmentCategory, EquipmentStatus, MaintenanceLevel,
    SpreaderEquipment, SprayerEquipment, InjectionEquipment, DripSystemEquipment,
    EquipmentInventory, EquipmentCompatibility, EquipmentEfficiency,
    EquipmentUpgrade, IndividualEquipmentAssessment, EquipmentAssessment, EquipmentMaintenance, EquipmentPerformance,
    FieldLayoutAnalysis, StorageFacilityAssessment, LaborAnalysis, 
    EnvironmentalAssessment, ComprehensiveFarmAssessment
)

logger = logging.getLogger(__name__)


class EquipmentAssessmentService:
    """Service for comprehensive equipment assessment and optimization."""
    
    def __init__(self):
        self.equipment_database = {}
        self._initialize_equipment_database()
    
    def _convert_equipment_specs_to_equipment(self, equipment_specs: List[Any]) -> List[Equipment]:
        """Convert EquipmentSpecification objects to Equipment objects."""
        equipment_objects = []
        
        for i, spec in enumerate(equipment_specs):
            # Map EquipmentType to EquipmentCategory
            category_mapping = {
                "spreader": EquipmentCategory.SPREADING,
                "sprayer": EquipmentCategory.SPRAYING,
                "injector": EquipmentCategory.INJECTION,
                "drip_system": EquipmentCategory.IRRIGATION,
                "hand_spreader": EquipmentCategory.SPREADING,
                "broadcaster": EquipmentCategory.SPREADING
            }
            
            # Get equipment type from spec
            equipment_type = getattr(spec, 'equipment_type', 'spreader')
            if hasattr(equipment_type, 'value'):
                equipment_type = equipment_type.value
            
            equipment = Equipment(
                equipment_id=f"spec_{i}",
                name=f"{equipment_type.title()} Equipment",
                category=category_mapping.get(equipment_type, EquipmentCategory.SPREADING),
                capacity=getattr(spec, 'capacity', None),
                capacity_unit=getattr(spec, 'capacity_unit', 'units'),
                status=EquipmentStatus.OPERATIONAL,
                maintenance_level=MaintenanceLevel.BASIC,
                current_value=getattr(spec, 'current_value', None)
            )
            equipment_objects.append(equipment)
        
        return equipment_objects

    def _initialize_equipment_database(self):
        """Initialize equipment database with specifications and benchmarks."""
        self.equipment_database = {
            EquipmentCategory.SPREADING: {
                "capacity_benchmarks": {
                    "small": {"min": 0, "max": 500, "optimal": 250},  # cubic feet
                    "medium": {"min": 500, "max": 1500, "optimal": 1000},
                    "large": {"min": 1500, "max": 3000, "optimal": 2250},
                    "very_large": {"min": 3000, "max": 10000, "optimal": 5000}
                },
                "efficiency_factors": ["spread_width", "application_rate_accuracy", "ground_speed"],
                "maintenance_requirements": {
                    "basic": ["Clean hopper", "Check spread pattern", "Lubricate moving parts"],
                    "intermediate": ["Calibrate spreader", "Check drive system", "Inspect chains"],
                    "advanced": ["Rebuild gearbox", "Replace worn parts", "Precision calibration"]
                }
            },
            EquipmentCategory.SPRAYING: {
                "capacity_benchmarks": {
                    "small": {"min": 0, "max": 100, "optimal": 50},  # gallons
                    "medium": {"min": 100, "max": 500, "optimal": 300},
                    "large": {"min": 500, "max": 1000, "optimal": 750},
                    "very_large": {"min": 1000, "max": 5000, "optimal": 2500}
                },
                "efficiency_factors": ["boom_width", "nozzle_efficiency", "pressure_control"],
                "maintenance_requirements": {
                    "basic": ["Clean tank", "Check nozzles", "Test pressure"],
                    "intermediate": ["Calibrate sprayer", "Check pump", "Inspect hoses"],
                    "advanced": ["Rebuild pump", "Replace boom sections", "Precision calibration"]
                }
            },
            EquipmentCategory.INJECTION: {
                "capacity_benchmarks": {
                    "small": {"min": 0, "max": 50, "optimal": 25},  # gph
                    "medium": {"min": 50, "max": 200, "optimal": 125},
                    "large": {"min": 200, "max": 500, "optimal": 350},
                    "very_large": {"min": 500, "max": 1000, "optimal": 750}
                },
                "efficiency_factors": ["injection_depth", "flow_rate", "pressure_control"],
                "maintenance_requirements": {
                    "basic": ["Clean injection points", "Check flow rates", "Test pressure"],
                    "intermediate": ["Calibrate injector", "Check pump", "Inspect lines"],
                    "advanced": ["Rebuild injection system", "Replace pumps", "Precision calibration"]
                }
            },
            EquipmentCategory.IRRIGATION: {
                "capacity_benchmarks": {
                    "small": {"min": 0, "max": 10, "optimal": 5},  # acres
                    "medium": {"min": 10, "max": 50, "optimal": 30},
                    "large": {"min": 50, "max": 200, "optimal": 125},
                    "very_large": {"min": 200, "max": 1000, "optimal": 500}
                },
                "efficiency_factors": ["system_coverage", "water_efficiency", "fertigation_capability"],
                "maintenance_requirements": {
                    "basic": ["Clean filters", "Check emitters", "Test pressure"],
                    "intermediate": ["Calibrate system", "Check pumps", "Inspect lines"],
                    "advanced": ["Rebuild pumps", "Replace main lines", "System optimization"]
                }
            }
        }
    
    async def assess_farm_equipment(
        self, 
        request: EquipmentAssessmentRequest
    ) -> EquipmentAssessmentResponse:
        """
        Perform comprehensive equipment assessment for a farm.
        
        Args:
            request: Equipment assessment request with farm details and current equipment
            
        Returns:
            EquipmentAssessmentResponse with detailed assessment results
        """
        start_time = time.time()
        request_id = str(uuid4())
        
        try:
            logger.info(f"Processing equipment assessment request {request_id}")
            
            # Convert equipment specifications to equipment objects
            equipment_objects = self._convert_equipment_specs_to_equipment(request.current_equipment)
            
            # Analyze farm characteristics
            farm_analysis = await self._analyze_farm_characteristics(request)
            
            # Assess current equipment inventory
            equipment_inventory = await self._assess_equipment_inventory(equipment_objects)
            
            # Perform individual equipment assessments
            equipment_assessments = await self._assess_individual_equipment(
                equipment_objects, farm_analysis
            )
            
            # Generate compatibility assessments
            compatibility_assessments = await self._generate_compatibility_assessments(
                equipment_objects, farm_analysis
            )
            
            # Generate efficiency assessments
            efficiency_assessments = await self._generate_efficiency_assessments(
                equipment_objects, farm_analysis
            )
            
            # Generate upgrade recommendations
            upgrade_recommendations = await self._generate_upgrade_recommendations(
                equipment_objects, farm_analysis, request.budget_constraints
            )
            
            # Perform capacity analysis
            capacity_analysis = await self._perform_capacity_analysis(
                equipment_objects, farm_analysis
            )
            
            # Perform cost-benefit analysis
            cost_benefit_analysis = await self._perform_cost_benefit_analysis(
                upgrade_recommendations, request.budget_constraints
            )
            
            # Perform comprehensive farm assessment
            comprehensive_assessment = await self._perform_comprehensive_farm_assessment(
                request, equipment_objects, farm_analysis
            )
            
            # Calculate overall assessment score
            overall_score = await self._calculate_overall_score(
                equipment_assessments, efficiency_assessments, compatibility_assessments
            )
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            response = EquipmentAssessmentResponse(
                request_id=request_id,
                farm_assessment=farm_analysis,
                equipment_assessments=equipment_assessments,
                upgrade_priorities=self._prioritize_upgrades(upgrade_recommendations),
                capacity_analysis=capacity_analysis,
                cost_benefit_analysis=cost_benefit_analysis,
                processing_time_ms=processing_time_ms,
                metadata={
                    "assessment_date": str(time.time()),
                    "compatibility_assessments": [c.dict() for c in compatibility_assessments],
                    "efficiency_assessments": [e.dict() for e in efficiency_assessments],
                    "overall_score": await self._calculate_overall_score(
                        equipment_assessments, efficiency_assessments, compatibility_assessments
                    )
                },
                # Enhanced comprehensive assessment fields
                comprehensive_farm_assessment=comprehensive_assessment.get("farm_assessment"),
                field_layout_analysis=comprehensive_assessment.get("field_layout_analysis"),
                storage_facility_assessment=comprehensive_assessment.get("storage_facility_assessment"),
                labor_analysis=comprehensive_assessment.get("labor_analysis"),
                environmental_assessment=comprehensive_assessment.get("environmental_assessment"),
                operational_efficiency_score=comprehensive_assessment.get("operational_efficiency_score"),
                optimization_recommendations=comprehensive_assessment.get("optimization_recommendations"),
                implementation_priorities=comprehensive_assessment.get("implementation_priorities")
            )
            
            logger.info(f"Equipment assessment completed in {processing_time_ms:.2f}ms")
            return response
            
        except Exception as e:
            logger.error(f"Error in equipment assessment: {e}")
            raise
    
    async def _analyze_farm_characteristics(self, request: EquipmentAssessmentRequest) -> Dict[str, Any]:
        """Analyze farm characteristics for equipment suitability."""
        analysis = {
            "farm_size_category": self._categorize_farm_size(request.farm_size_acres),
            "field_count": request.field_count,
            "average_field_size": request.average_field_size,
            "field_size_category": self._categorize_field_size(request.average_field_size),
            "equipment_intensity": self._calculate_equipment_intensity(request),
            "labor_availability": request.labor_availability,
            "maintenance_capability": request.maintenance_capability,
            "budget_constraints": request.budget_constraints,
            "operational_requirements": self._assess_operational_requirements(request)
        }
        return analysis
    
    async def _assess_equipment_inventory(self, equipment_list: List[Equipment]) -> EquipmentInventory:
        """Assess current equipment inventory."""
        total_value = sum(eq.current_value or 0 for eq in equipment_list)
        
        inventory = EquipmentInventory(
            farm_id="current_farm",  # Would be passed from request in real implementation
            equipment_list=equipment_list,
            total_equipment_value=total_value,
            last_updated=str(time.time())
        )
        
        return inventory
    
    async def _assess_individual_equipment(
        self, 
        equipment_list: List[Equipment], 
        farm_analysis: Dict[str, Any]
    ) -> List[IndividualEquipmentAssessment]:
        """Assess individual equipment items."""
        assessments = []
        
        for equipment in equipment_list:
            assessment = IndividualEquipmentAssessment(
                equipment_id=equipment.equipment_id,
                equipment_type=equipment.category,
                suitability_score=self._calculate_suitability_score(equipment, farm_analysis),
                capacity_adequacy=self._assess_capacity_adequacy(equipment, farm_analysis),
                efficiency_rating=self._calculate_efficiency_rating(equipment),
                cost_effectiveness=self._calculate_cost_effectiveness(equipment),
                upgrade_recommendations=self._generate_equipment_upgrade_recommendations(equipment, farm_analysis),
                maintenance_requirements=self._assess_maintenance_requirements(equipment),
                replacement_timeline=self._assess_replacement_timeline(equipment)
            )
            assessments.append(assessment)
        
        return assessments
    
    async def _generate_compatibility_assessments(
        self, 
        equipment_list: List[Equipment], 
        farm_analysis: Dict[str, Any]
    ) -> List[EquipmentCompatibility]:
        """Generate equipment compatibility assessments."""
        compatibilities = []
        
        for equipment in equipment_list:
            compatibility = EquipmentCompatibility(
                equipment_id=equipment.equipment_id,
                fertilizer_types=self._get_compatible_fertilizer_types(equipment),
                application_methods=self._get_compatible_application_methods(equipment),
                field_size_range=self._get_suitable_field_size_range(equipment),
                soil_types=self._get_compatible_soil_types(equipment),
                weather_conditions=self._get_suitable_weather_conditions(equipment),
                compatibility_score=self._calculate_compatibility_score(equipment, farm_analysis)
            )
            compatibilities.append(compatibility)
        
        return compatibilities
    
    async def _generate_efficiency_assessments(
        self, 
        equipment_list: List[Equipment], 
        farm_analysis: Dict[str, Any]
    ) -> List[EquipmentEfficiency]:
        """Generate equipment efficiency assessments."""
        efficiencies = []
        
        for equipment in equipment_list:
            efficiency = EquipmentEfficiency(
                equipment_id=equipment.equipment_id,
                application_efficiency=self._calculate_application_efficiency(equipment),
                fuel_efficiency=self._estimate_fuel_efficiency(equipment),
                labor_efficiency=self._calculate_labor_efficiency(equipment),
                maintenance_efficiency=self._calculate_maintenance_efficiency(equipment),
                overall_efficiency=self._calculate_overall_efficiency(equipment),
                efficiency_factors=self._identify_efficiency_factors(equipment)
            )
            efficiencies.append(efficiency)
        
        return efficiencies
    
    async def _generate_upgrade_recommendations(
        self, 
        equipment_list: List[Equipment], 
        farm_analysis: Dict[str, Any],
        budget_constraints: Optional[float]
    ) -> List[EquipmentUpgrade]:
        """Generate equipment upgrade recommendations."""
        upgrades = []
        
        for equipment in equipment_list:
            if self._needs_upgrade(equipment, farm_analysis):
                upgrade = EquipmentUpgrade(
                    current_equipment_id=equipment.equipment_id,
                    recommended_upgrade=self._recommend_upgrade(equipment, farm_analysis),
                    upgrade_priority=self._determine_upgrade_priority(equipment, farm_analysis),
                    estimated_cost=self._estimate_upgrade_cost(equipment),
                    expected_benefits=self._identify_upgrade_benefits(equipment, farm_analysis),
                    payback_period=self._calculate_payback_period(equipment, farm_analysis),
                    justification=self._generate_upgrade_justification(equipment, farm_analysis)
                )
                upgrades.append(upgrade)
        
        return upgrades
    
    async def _perform_capacity_analysis(
        self, 
        equipment_list: List[Equipment], 
        farm_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform capacity analysis for farm operations."""
        analysis = {
            "total_capacity": self._calculate_total_capacity(equipment_list),
            "capacity_by_category": self._calculate_capacity_by_category(equipment_list),
            "capacity_adequacy": self._assess_capacity_adequacy_overall(equipment_list, farm_analysis),
            "bottlenecks": self._identify_capacity_bottlenecks(equipment_list, farm_analysis),
            "optimization_opportunities": self._identify_optimization_opportunities(equipment_list, farm_analysis)
        }
        return analysis
    
    async def _perform_cost_benefit_analysis(
        self, 
        upgrade_recommendations: List[EquipmentUpgrade],
        budget_constraints: Optional[float]
    ) -> Dict[str, Any]:
        """Perform comprehensive cost-benefit analysis for upgrades."""
        analysis = {
            "total_upgrade_cost": sum(upgrade.estimated_cost or 0 for upgrade in upgrade_recommendations),
            "budget_constraints": budget_constraints,
            "affordable_upgrades": self._filter_affordable_upgrades(upgrade_recommendations, budget_constraints),
            "roi_analysis": self._calculate_roi_analysis(upgrade_recommendations),
            "priority_ranking": self._rank_upgrades_by_priority(upgrade_recommendations),
            "implementation_timeline": self._create_implementation_timeline(upgrade_recommendations),
            # Enhanced cost analysis
            "detailed_cost_breakdown": self._calculate_detailed_cost_breakdown(upgrade_recommendations),
            "operational_cost_analysis": self._calculate_operational_cost_analysis(upgrade_recommendations),
            "maintenance_cost_analysis": self._calculate_maintenance_cost_analysis(upgrade_recommendations),
            "sensitivity_analysis": self._perform_sensitivity_analysis(upgrade_recommendations),
            "break_even_analysis": self._calculate_break_even_analysis(upgrade_recommendations),
            "financing_options": self._analyze_financing_options(upgrade_recommendations, budget_constraints)
        }
        return analysis
    
    def _compare_to_benchmarks(self, equipment: Equipment) -> Dict[str, Any]:
        """Compare equipment performance to industry benchmarks."""
        comparison = {
            "fuel_efficiency": self._compare_fuel_efficiency_to_benchmark(equipment),
            "environmental_performance": self._compare_environmental_to_benchmark(equipment),
            "operational_efficiency": self._compare_operational_to_benchmark(equipment),
            "cost_effectiveness": self._compare_cost_to_benchmark(equipment)
        }
        return comparison
    
    def _compare_fuel_efficiency_to_benchmark(self, equipment: Equipment) -> Dict[str, Any]:
        """Compare fuel efficiency to industry benchmarks."""
        current_efficiency = self._calculate_fuel_efficiency_rating(equipment)
        
        benchmarks = {
            "excellent": 0.9,
            "good": 0.8,
            "acceptable": 0.7,
            "needs_improvement": 0.6
        }
        
        if current_efficiency >= benchmarks["excellent"]:
            rating = "excellent"
        elif current_efficiency >= benchmarks["good"]:
            rating = "good"
        elif current_efficiency >= benchmarks["acceptable"]:
            rating = "acceptable"
        else:
            rating = "needs_improvement"
        
        return {
            "current_score": current_efficiency,
            "benchmark_rating": rating,
            "benchmark_threshold": benchmarks[rating],
            "performance_gap": benchmarks["excellent"] - current_efficiency,
            "improvement_potential": max(0, benchmarks["excellent"] - current_efficiency)
        }
    
    def _compare_environmental_to_benchmark(self, equipment: Equipment) -> Dict[str, Any]:
        """Compare environmental performance to industry benchmarks."""
        current_score = self._calculate_environmental_impact_score(equipment)
        
        benchmarks = {
            "excellent": 0.9,
            "good": 0.8,
            "acceptable": 0.7,
            "needs_improvement": 0.6
        }
        
        if current_score >= benchmarks["excellent"]:
            rating = "excellent"
        elif current_score >= benchmarks["good"]:
            rating = "good"
        elif current_score >= benchmarks["acceptable"]:
            rating = "acceptable"
        else:
            rating = "needs_improvement"
        
        return {
            "current_score": current_score,
            "benchmark_rating": rating,
            "benchmark_threshold": benchmarks[rating],
            "performance_gap": benchmarks["excellent"] - current_score,
            "improvement_potential": max(0, benchmarks["excellent"] - current_score)
        }
    
    def _compare_operational_to_benchmark(self, equipment: Equipment) -> Dict[str, Any]:
        """Compare operational efficiency to industry benchmarks."""
        current_efficiency = self._calculate_efficiency_rating(equipment)
        
        benchmarks = {
            "excellent": 0.9,
            "good": 0.8,
            "acceptable": 0.7,
            "needs_improvement": 0.6
        }
        
        if current_efficiency >= benchmarks["excellent"]:
            rating = "excellent"
        elif current_efficiency >= benchmarks["good"]:
            rating = "good"
        elif current_efficiency >= benchmarks["acceptable"]:
            rating = "acceptable"
        else:
            rating = "needs_improvement"
        
        return {
            "current_score": current_efficiency,
            "benchmark_rating": rating,
            "benchmark_threshold": benchmarks[rating],
            "performance_gap": benchmarks["excellent"] - current_efficiency,
            "improvement_potential": max(0, benchmarks["excellent"] - current_efficiency)
        }
    
    def _compare_cost_to_benchmark(self, equipment: Equipment) -> Dict[str, Any]:
        """Compare cost effectiveness to industry benchmarks."""
        current_cost_effectiveness = self._calculate_cost_effectiveness(equipment)
        
        benchmarks = {
            "excellent": 0.9,
            "good": 0.8,
            "acceptable": 0.7,
            "needs_improvement": 0.6
        }
        
        if current_cost_effectiveness >= benchmarks["excellent"]:
            rating = "excellent"
        elif current_cost_effectiveness >= benchmarks["good"]:
            rating = "good"
        elif current_cost_effectiveness >= benchmarks["acceptable"]:
            rating = "acceptable"
        else:
            rating = "needs_improvement"
        
        return {
            "current_score": current_cost_effectiveness,
            "benchmark_rating": rating,
            "benchmark_threshold": benchmarks[rating],
            "performance_gap": benchmarks["excellent"] - current_cost_effectiveness,
            "improvement_potential": max(0, benchmarks["excellent"] - current_cost_effectiveness)
        }
    
    def _calculate_industry_ranking(self, equipment: Equipment) -> Dict[str, Any]:
        """Calculate industry ranking for equipment."""
        # Calculate overall performance score
        fuel_efficiency = self._calculate_fuel_efficiency_rating(equipment)
        environmental_score = self._calculate_environmental_impact_score(equipment)
        operational_efficiency = self._calculate_efficiency_rating(equipment)
        cost_effectiveness = self._calculate_cost_effectiveness(equipment)
        
        overall_score = (fuel_efficiency * 0.25 + environmental_score * 0.25 + 
                        operational_efficiency * 0.25 + cost_effectiveness * 0.25)
        
        # Determine percentile ranking
        if overall_score >= 0.9:
            percentile = 95
            ranking = "top_5_percent"
        elif overall_score >= 0.8:
            percentile = 80
            ranking = "top_20_percent"
        elif overall_score >= 0.7:
            percentile = 60
            ranking = "above_average"
        elif overall_score >= 0.6:
            percentile = 40
            ranking = "average"
        else:
            percentile = 20
            ranking = "below_average"
        
        return {
            "overall_score": overall_score,
            "percentile_ranking": percentile,
            "industry_ranking": ranking,
            "performance_category": self._get_performance_category(overall_score)
        }
    
    def _get_performance_category(self, score: float) -> str:
        """Get performance category based on score."""
        if score >= 0.9:
            return "Industry Leader"
        elif score >= 0.8:
            return "High Performer"
        elif score >= 0.7:
            return "Good Performer"
        elif score >= 0.6:
            return "Average Performer"
        else:
            return "Needs Improvement"
    
    def _identify_performance_improvements(self, equipment: Equipment) -> List[Dict[str, Any]]:
        """Identify specific performance improvement opportunities."""
        improvements = []
        
        # Fuel efficiency improvements
        fuel_efficiency = self._calculate_fuel_efficiency_rating(equipment)
        if fuel_efficiency < 0.8:
            improvements.append({
                "category": "fuel_efficiency",
                "current_score": fuel_efficiency,
                "target_score": 0.8,
                "improvement_potential": 0.8 - fuel_efficiency,
                "recommendations": [
                    "Regular engine maintenance",
                    "Proper tire inflation",
                    "Optimal operating speeds",
                    "Consider equipment upgrade"
                ]
            })
        
        # Environmental improvements
        environmental_score = self._calculate_environmental_impact_score(equipment)
        if environmental_score < 0.8:
            improvements.append({
                "category": "environmental_performance",
                "current_score": environmental_score,
                "target_score": 0.8,
                "improvement_potential": 0.8 - environmental_score,
                "recommendations": [
                    "Use cleaner fuels",
                    "Regular emissions testing",
                    "Noise reduction measures",
                    "Consider Tier 4 equipment"
                ]
            })
        
        # Operational efficiency improvements
        operational_efficiency = self._calculate_efficiency_rating(equipment)
        if operational_efficiency < 0.8:
            improvements.append({
                "category": "operational_efficiency",
                "current_score": operational_efficiency,
                "target_score": 0.8,
                "improvement_potential": 0.8 - operational_efficiency,
                "recommendations": [
                    "Regular calibration",
                    "Operator training",
                    "Preventive maintenance",
                    "Process optimization"
                ]
            })
        
        return improvements
    
    def _calculate_overall_farm_performance(self, comparison_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall farm performance from equipment comparisons."""
        if not comparison_results:
            return {"overall_score": 0.0, "ranking": "no_data"}
        
        # Calculate average scores across all equipment
        total_fuel_efficiency = sum(result["performance_metrics"]["fuel_efficiency"] for result in comparison_results)
        total_environmental = sum(result["performance_metrics"]["environmental_impact"] for result in comparison_results)
        total_operational = sum(result["performance_metrics"]["operational_efficiency"] for result in comparison_results)
        
        count = len(comparison_results)
        
        overall_score = (total_fuel_efficiency + total_environmental + total_operational) / (count * 3)
        
        # Determine overall ranking
        if overall_score >= 0.9:
            ranking = "Industry Leader"
        elif overall_score >= 0.8:
            ranking = "High Performer"
        elif overall_score >= 0.7:
            ranking = "Good Performer"
        elif overall_score >= 0.6:
            ranking = "Average Performer"
        else:
            ranking = "Needs Improvement"
        
        return {
            "overall_score": overall_score,
            "ranking": ranking,
            "equipment_count": count,
            "average_scores": {
                "fuel_efficiency": total_fuel_efficiency / count,
                "environmental_performance": total_environmental / count,
                "operational_efficiency": total_operational / count
            }
        }
    
    def _generate_benchmark_summary(self, comparison_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate benchmark summary for all equipment."""
        if not comparison_results:
            return {"summary": "No equipment data available"}
        
        # Count equipment by performance level
        performance_counts = {
            "excellent": 0,
            "good": 0,
            "acceptable": 0,
            "needs_improvement": 0
        }
        
        for result in comparison_results:
            fuel_rating = result["benchmark_comparison"]["fuel_efficiency"]["benchmark_rating"]
            performance_counts[fuel_rating] += 1
        
        total_equipment = len(comparison_results)
        
        return {
            "total_equipment_assessed": total_equipment,
            "performance_distribution": performance_counts,
            "performance_percentages": {
                rating: (count / total_equipment) * 100 
                for rating, count in performance_counts.items()
            },
            "key_insights": self._generate_key_insights(comparison_results),
            "recommendations": self._generate_farm_recommendations(comparison_results)
        }
    
    def _generate_key_insights(self, comparison_results: List[Dict[str, Any]]) -> List[str]:
        """Generate key insights from benchmark comparison."""
        insights = []
        
        # Analyze fuel efficiency
        fuel_scores = [result["performance_metrics"]["fuel_efficiency"] for result in comparison_results]
        avg_fuel_efficiency = sum(fuel_scores) / len(fuel_scores)
        
        if avg_fuel_efficiency < 0.7:
            insights.append("Farm equipment fuel efficiency is below industry standards")
        elif avg_fuel_efficiency > 0.8:
            insights.append("Farm equipment fuel efficiency exceeds industry standards")
        
        # Analyze environmental performance
        env_scores = [result["performance_metrics"]["environmental_impact"] for result in comparison_results]
        avg_env_score = sum(env_scores) / len(env_scores)
        
        if avg_env_score < 0.7:
            insights.append("Environmental performance needs improvement")
        elif avg_env_score > 0.8:
            insights.append("Excellent environmental performance")
        
        # Analyze operational efficiency
        op_scores = [result["performance_metrics"]["operational_efficiency"] for result in comparison_results]
        avg_op_score = sum(op_scores) / len(op_scores)
        
        if avg_op_score < 0.7:
            insights.append("Operational efficiency could be improved")
        elif avg_op_score > 0.8:
            insights.append("High operational efficiency achieved")
        
        return insights
    
    def _generate_farm_recommendations(self, comparison_results: List[Dict[str, Any]]) -> List[str]:
        """Generate farm-level recommendations based on benchmark analysis."""
        recommendations = []
        
        # Analyze improvement opportunities
        improvement_count = 0
        for result in comparison_results:
            improvement_count += len(result["improvement_opportunities"])
        
        if improvement_count > len(comparison_results):
            recommendations.append("Multiple equipment improvement opportunities identified")
        
        # Analyze performance distribution
        performance_counts = {}
        for result in comparison_results:
            fuel_rating = result["benchmark_comparison"]["fuel_efficiency"]["benchmark_rating"]
            performance_counts[fuel_rating] = performance_counts.get(fuel_rating, 0) + 1
        
        if performance_counts.get("needs_improvement", 0) > 0:
            recommendations.append("Priority equipment upgrades recommended")
        
        if performance_counts.get("excellent", 0) == len(comparison_results):
            recommendations.append("Farm equipment performance is excellent")
        
        return recommendations
    
    def _categorize_farm_size(self, farm_size_acres: float) -> str:
        """Categorize farm size."""
        if farm_size_acres < 100:
            return "small"
        elif farm_size_acres < 500:
            return "medium"
        elif farm_size_acres < 2000:
            return "large"
        else:
            return "very_large"
    
    def _categorize_field_size(self, field_size_acres: float) -> str:
        """Categorize field size."""
        if field_size_acres < 10:
            return "small"
        elif field_size_acres < 50:
            return "medium"
        elif field_size_acres < 200:
            return "large"
        else:
            return "very_large"
    
    def _calculate_equipment_intensity(self, request: EquipmentAssessmentRequest) -> str:
        """Calculate equipment intensity based on farm characteristics."""
        equipment_per_field = len(request.current_equipment) / request.field_count if request.field_count > 0 else 0
        
        if equipment_per_field < 0.5:
            return "low"
        elif equipment_per_field < 1.0:
            return "medium"
        else:
            return "high"
    
    def _assess_operational_requirements(self, request: EquipmentAssessmentRequest) -> Dict[str, Any]:
        """Assess operational requirements for the farm."""
        return {
            "daily_capacity_requirement": request.farm_size_acres / 30,  # Assume 30-day window
            "seasonal_peak_demand": request.farm_size_acres / 7,  # Assume 7-day peak
            "labor_constraints": request.labor_availability,
            "maintenance_constraints": request.maintenance_capability,
            "budget_constraints": request.budget_constraints
        }
    
    def _calculate_suitability_score(self, equipment: Equipment, farm_analysis: Dict[str, Any]) -> float:
        """Calculate suitability score for equipment."""
        score = 0.5  # Base score
        
        # Capacity suitability
        capacity_score = self._assess_capacity_suitability(equipment, farm_analysis)
        score += capacity_score * 0.3
        
        # Age factor
        age_score = self._assess_age_factor(equipment)
        score += age_score * 0.2
        
        # Maintenance level compatibility
        maintenance_score = self._assess_maintenance_compatibility(equipment, farm_analysis)
        score += maintenance_score * 0.2
        
        # Status factor
        status_score = self._assess_status_factor(equipment)
        score += status_score * 0.1
        
        return min(score, 1.0)
    
    def _assess_capacity_adequacy(self, equipment: Equipment, farm_analysis: Dict[str, Any]) -> str:
        """Assess capacity adequacy for farm operations."""
        if not equipment.capacity:
            return "unknown"
        
        farm_size = farm_analysis.get("farm_size_category", "medium")
        capacity_benchmarks = self.equipment_database.get(equipment.category, {}).get("capacity_benchmarks", {})
        
        if farm_size in capacity_benchmarks:
            benchmark = capacity_benchmarks[farm_size]
            if equipment.capacity < benchmark["min"]:
                return "insufficient"
            elif equipment.capacity > benchmark["max"]:
                return "excessive"
            else:
                return "adequate"
        
        return "unknown"
    
    def _calculate_efficiency_rating(self, equipment: Equipment) -> float:
        """Calculate efficiency rating for equipment."""
        # Base efficiency on age and status
        base_efficiency = 0.7
        
        # Adjust for age
        if equipment.year:
            age = 2024 - equipment.year
            if age < 5:
                base_efficiency += 0.2
            elif age < 10:
                base_efficiency += 0.1
            elif age > 15:
                base_efficiency -= 0.2
        
        # Adjust for status
        if equipment.status == EquipmentStatus.OPERATIONAL:
            base_efficiency += 0.1
        elif equipment.status == EquipmentStatus.MAINTENANCE_REQUIRED:
            base_efficiency -= 0.1
        elif equipment.status == EquipmentStatus.OUT_OF_SERVICE:
            base_efficiency -= 0.3
        
        return max(0.0, min(1.0, base_efficiency))
    
    def _calculate_cost_effectiveness(self, equipment: Equipment) -> float:
        """Calculate cost effectiveness of equipment."""
        if not equipment.current_value or not equipment.capacity:
            return 0.5
        
        # Cost per unit capacity
        cost_per_capacity = equipment.current_value / equipment.capacity
        
        # Normalize based on equipment category
        category_factors = {
            EquipmentCategory.SPREADING: 1.0,
            EquipmentCategory.SPRAYING: 1.2,
            EquipmentCategory.INJECTION: 1.5,
            EquipmentCategory.IRRIGATION: 2.0
        }
        
        factor = category_factors.get(equipment.category, 1.0)
        normalized_cost = cost_per_capacity / factor
        
        # Convert to effectiveness score (lower cost is better)
        if normalized_cost < 100:
            return 1.0
        elif normalized_cost < 500:
            return 0.8
        elif normalized_cost < 1000:
            return 0.6
        else:
            return 0.4
    
    def _generate_equipment_upgrade_recommendations(self, equipment: Equipment, farm_analysis: Dict[str, Any]) -> List[str]:
        """Generate upgrade recommendations for equipment."""
        recommendations = []
        
        # Capacity recommendations
        capacity_adequacy = self._assess_capacity_adequacy(equipment, farm_analysis)
        if capacity_adequacy == "insufficient":
            recommendations.append("Consider upgrading to higher capacity model")
        elif capacity_adequacy == "excessive":
            recommendations.append("Consider downsizing to more appropriate capacity")
        
        # Age recommendations
        if equipment.year and (2024 - equipment.year) > 15:
            recommendations.append("Consider replacement due to age")
        
        # Status recommendations
        if equipment.status == EquipmentStatus.MAINTENANCE_REQUIRED:
            recommendations.append("Schedule maintenance before next season")
        elif equipment.status == EquipmentStatus.OUT_OF_SERVICE:
            recommendations.append("Repair or replace out-of-service equipment")
        
        # Maintenance level recommendations
        if equipment.maintenance_level == MaintenanceLevel.PROFESSIONAL and farm_analysis.get("maintenance_capability") == "basic":
            recommendations.append("Consider equipment with lower maintenance requirements")
        
        return recommendations
    
    def _assess_maintenance_requirements(self, equipment: Equipment) -> List[str]:
        """Assess maintenance requirements for equipment."""
        maintenance_requirements = []
        
        # Base maintenance level requirements
        maintenance_levels = {
            MaintenanceLevel.BASIC: ["Basic cleaning", "Lubrication", "Visual inspection"],
            MaintenanceLevel.INTERMEDIATE: ["Calibration", "Component inspection", "System testing"],
            MaintenanceLevel.ADVANCED: ["Precision calibration", "Component replacement", "System overhaul"],
            MaintenanceLevel.PROFESSIONAL: ["Professional calibration", "Major repairs", "Certification work"]
        }
        
        base_requirements = maintenance_levels.get(equipment.maintenance_level, [])
        maintenance_requirements.extend(base_requirements)
        
        # Add category-specific requirements
        if equipment.category == EquipmentCategory.SPREADING:
            maintenance_requirements.extend(["Check spread pattern", "Clean hopper", "Inspect chains"])
        elif equipment.category == EquipmentCategory.SPRAYING:
            maintenance_requirements.extend(["Clean tank", "Check nozzles", "Test pressure"])
        elif equipment.category == EquipmentCategory.INJECTION:
            maintenance_requirements.extend(["Clean injection points", "Check flow rates", "Test pressure"])
        elif equipment.category == EquipmentCategory.IRRIGATION:
            maintenance_requirements.extend(["Clean filters", "Check emitters", "Test pressure"])
        
        return maintenance_requirements
    
    def _assess_replacement_timeline(self, equipment: Equipment) -> Optional[str]:
        """Assess replacement timeline for equipment."""
        if not equipment.year:
            return "unknown"
        
        age = 2024 - equipment.year
        
        if age < 5:
            return "No replacement needed in next 5 years"
        elif age < 10:
            return "Consider replacement in 2-3 years"
        elif age < 15:
            return "Plan for replacement within 1-2 years"
        else:
            return "Immediate replacement recommended"
    
    def _get_compatible_fertilizer_types(self, equipment: Equipment) -> List[str]:
        """Get compatible fertilizer types for equipment."""
        compatibility_map = {
            EquipmentCategory.SPREADING: ["granular", "organic"],
            EquipmentCategory.SPRAYING: ["liquid"],
            EquipmentCategory.INJECTION: ["liquid"],
            EquipmentCategory.IRRIGATION: ["liquid"]
        }
        return compatibility_map.get(equipment.category, [])
    
    def _get_compatible_application_methods(self, equipment: Equipment) -> List[str]:
        """Get compatible application methods for equipment."""
        method_map = {
            EquipmentCategory.SPREADING: ["broadcast", "band"],
            EquipmentCategory.SPRAYING: ["foliar", "broadcast"],
            EquipmentCategory.INJECTION: ["injection", "sidedress"],
            EquipmentCategory.IRRIGATION: ["drip", "fertigation"]
        }
        return method_map.get(equipment.category, [])
    
    def _get_suitable_field_size_range(self, equipment: Equipment) -> Optional[Dict[str, float]]:
        """Get suitable field size range for equipment."""
        if not equipment.capacity:
            return None
        
        # Estimate based on capacity
        min_size = equipment.capacity * 0.5
        max_size = equipment.capacity * 2.0
        
        return {"min": min_size, "max": max_size}
    
    def _get_compatible_soil_types(self, equipment: Equipment) -> List[str]:
        """Get compatible soil types for equipment."""
        # Most equipment works with all soil types
        return ["clay", "loam", "sandy", "silt"]
    
    def _get_suitable_weather_conditions(self, equipment: Equipment) -> List[str]:
        """Get suitable weather conditions for equipment."""
        return ["dry", "moderate_humidity", "light_wind"]
    
    def _calculate_compatibility_score(self, equipment: Equipment, farm_analysis: Dict[str, Any]) -> float:
        """Calculate overall compatibility score."""
        score = 0.5  # Base score
        
        # Capacity compatibility
        capacity_adequacy = self._assess_capacity_adequacy(equipment, farm_analysis)
        if capacity_adequacy == "adequate":
            score += 0.3
        elif capacity_adequacy == "insufficient" or capacity_adequacy == "excessive":
            score += 0.1
        
        # Maintenance compatibility
        maintenance_capability = farm_analysis.get("maintenance_capability", "basic")
        if equipment.maintenance_level == MaintenanceLevel.BASIC:
            score += 0.2
        elif equipment.maintenance_level == MaintenanceLevel.INTERMEDIATE and maintenance_capability in ["intermediate", "advanced"]:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_application_efficiency(self, equipment: Equipment) -> float:
        """Calculate application efficiency for equipment."""
        return self._calculate_efficiency_rating(equipment)
    
    def _estimate_fuel_efficiency(self, equipment: Equipment) -> Optional[float]:
        """Estimate fuel efficiency for equipment."""
        # Simple estimation based on equipment type and age
        base_efficiency = 0.7
        
        if equipment.year:
            age = 2024 - equipment.year
            if age < 5:
                base_efficiency += 0.2
            elif age > 15:
                base_efficiency -= 0.2
        
        return base_efficiency
    
    def _calculate_labor_efficiency(self, equipment: Equipment) -> Optional[float]:
        """Calculate labor efficiency for equipment."""
        # Estimate based on equipment complexity
        complexity_scores = {
            EquipmentCategory.SPREADING: 0.8,
            EquipmentCategory.SPRAYING: 0.7,
            EquipmentCategory.INJECTION: 0.6,
            EquipmentCategory.IRRIGATION: 0.9
        }
        return complexity_scores.get(equipment.category, 0.7)
    
    def _calculate_maintenance_efficiency(self, equipment: Equipment) -> Optional[float]:
        """Calculate maintenance efficiency for equipment."""
        maintenance_scores = {
            MaintenanceLevel.BASIC: 0.9,
            MaintenanceLevel.INTERMEDIATE: 0.7,
            MaintenanceLevel.ADVANCED: 0.5,
            MaintenanceLevel.PROFESSIONAL: 0.3
        }
        return maintenance_scores.get(equipment.maintenance_level, 0.7)
    
    def _calculate_overall_efficiency(self, equipment: Equipment) -> float:
        """Calculate overall efficiency for equipment."""
        application_eff = self._calculate_application_efficiency(equipment)
        fuel_eff = self._estimate_fuel_efficiency(equipment) or 0.7
        labor_eff = self._calculate_labor_efficiency(equipment) or 0.7
        maintenance_eff = self._calculate_maintenance_efficiency(equipment) or 0.7
        
        return (application_eff * 0.4 + fuel_eff * 0.2 + labor_eff * 0.2 + maintenance_eff * 0.2)
    
    def _identify_efficiency_factors(self, equipment: Equipment) -> Dict[str, Any]:
        """Identify factors affecting equipment efficiency."""
        return {
            "age_factor": equipment.year,
            "status_factor": equipment.status,
            "maintenance_level": equipment.maintenance_level,
            "capacity_factor": equipment.capacity,
            "category_factor": equipment.category
        }
    
    def _needs_upgrade(self, equipment: Equipment, farm_analysis: Dict[str, Any]) -> bool:
        """Determine if equipment needs upgrade."""
        # Check capacity adequacy
        capacity_adequacy = self._assess_capacity_adequacy(equipment, farm_analysis)
        if capacity_adequacy == "insufficient":
            return True
        
        # Check age
        if equipment.year and (2024 - equipment.year) > 15:
            return True
        
        # Check status
        if equipment.status == EquipmentStatus.OUT_OF_SERVICE:
            return True
        
        # Check maintenance compatibility
        maintenance_capability = farm_analysis.get("maintenance_capability", "basic")
        if equipment.maintenance_level == MaintenanceLevel.PROFESSIONAL and maintenance_capability == "basic":
            return True
        
        return False
    
    def _recommend_upgrade(self, equipment: Equipment, farm_analysis: Dict[str, Any]) -> Equipment:
        """Recommend upgrade for equipment."""
        # Create upgraded equipment with improved specifications
        upgraded_equipment = Equipment(
            equipment_id=f"upgrade_{equipment.equipment_id}",
            name=f"Upgraded {equipment.name}",
            category=equipment.category,
            manufacturer=equipment.manufacturer,
            model=f"{equipment.model}_upgraded",
            year=2024,
            capacity=self._calculate_upgraded_capacity(equipment, farm_analysis),
            capacity_unit=equipment.capacity_unit,
            purchase_date=str(time.time()),
            purchase_price=self._estimate_upgrade_cost(equipment),
            current_value=self._estimate_upgrade_cost(equipment),
            status=EquipmentStatus.OPERATIONAL,
            maintenance_level=MaintenanceLevel.BASIC,  # Assume upgraded equipment has lower maintenance
            specifications=equipment.specifications
        )
        
        return upgraded_equipment
    
    def _determine_upgrade_priority(self, equipment: Equipment, farm_analysis: Dict[str, Any]) -> str:
        """Determine upgrade priority."""
        priority_score = 0
        
        # Capacity inadequacy
        capacity_adequacy = self._assess_capacity_adequacy(equipment, farm_analysis)
        if capacity_adequacy == "insufficient":
            priority_score += 3
        
        # Age factor
        if equipment.year and (2024 - equipment.year) > 15:
            priority_score += 2
        
        # Status factor
        if equipment.status == EquipmentStatus.OUT_OF_SERVICE:
            priority_score += 4
        
        # Maintenance compatibility
        maintenance_capability = farm_analysis.get("maintenance_capability", "basic")
        if equipment.maintenance_level == MaintenanceLevel.PROFESSIONAL and maintenance_capability == "basic":
            priority_score += 2
        
        if priority_score >= 4:
            return "high"
        elif priority_score >= 2:
            return "medium"
        else:
            return "low"
    
    def _estimate_upgrade_cost(self, equipment: Equipment) -> Optional[float]:
        """Estimate upgrade cost for equipment."""
        if not equipment.current_value:
            return None
        
        # Estimate upgrade cost as 1.5x current value
        return equipment.current_value * 1.5
    
    def _identify_upgrade_benefits(self, equipment: Equipment, farm_analysis: Dict[str, Any]) -> List[str]:
        """Identify benefits of upgrading equipment."""
        benefits = []
        
        capacity_adequacy = self._assess_capacity_adequacy(equipment, farm_analysis)
        if capacity_adequacy == "insufficient":
            benefits.append("Increased capacity for farm operations")
        
        if equipment.year and (2024 - equipment.year) > 10:
            benefits.append("Improved reliability and reduced downtime")
        
        if equipment.maintenance_level in [MaintenanceLevel.ADVANCED, MaintenanceLevel.PROFESSIONAL]:
            benefits.append("Reduced maintenance requirements")
        
        benefits.extend([
            "Better fuel efficiency",
            "Improved application accuracy",
            "Enhanced safety features"
        ])
        
        return benefits
    
    def _calculate_payback_period(self, equipment: Equipment, farm_analysis: Dict[str, Any]) -> Optional[float]:
        """Calculate payback period for equipment upgrade."""
        upgrade_cost = self._estimate_upgrade_cost(equipment)
        if not upgrade_cost:
            return None
        
        # Estimate annual savings (simplified calculation)
        annual_savings = upgrade_cost * 0.15  # Assume 15% annual savings
        
        if annual_savings > 0:
            return upgrade_cost / annual_savings
        else:
            return None
    
    def _generate_upgrade_justification(self, equipment: Equipment, farm_analysis: Dict[str, Any]) -> str:
        """Generate upgrade justification."""
        justifications = []
        
        capacity_adequacy = self._assess_capacity_adequacy(equipment, farm_analysis)
        if capacity_adequacy == "insufficient":
            justifications.append("Current capacity is insufficient for farm operations")
        
        if equipment.year and (2024 - equipment.year) > 15:
            justifications.append("Equipment age exceeds recommended replacement timeline")
        
        if equipment.status == EquipmentStatus.OUT_OF_SERVICE:
            justifications.append("Equipment is currently out of service")
        
        maintenance_capability = farm_analysis.get("maintenance_capability", "basic")
        if equipment.maintenance_level == MaintenanceLevel.PROFESSIONAL and maintenance_capability == "basic":
            justifications.append("Maintenance requirements exceed farm capabilities")
        
        if not justifications:
            justifications.append("Upgrade would improve operational efficiency")
        
        return "; ".join(justifications)
    
    def _calculate_total_capacity(self, equipment_list: List[Equipment]) -> float:
        """Calculate total capacity of all equipment."""
        return sum(eq.capacity or 0 for eq in equipment_list)
    
    def _calculate_capacity_by_category(self, equipment_list: List[Equipment]) -> Dict[str, float]:
        """Calculate capacity by equipment category."""
        capacity_by_category = {}
        
        for equipment in equipment_list:
            category = equipment.category
            if category not in capacity_by_category:
                capacity_by_category[category] = 0
            capacity_by_category[category] += equipment.capacity or 0
        
        return capacity_by_category
    
    def _assess_capacity_adequacy_overall(self, equipment_list: List[Equipment], farm_analysis: Dict[str, Any]) -> str:
        """Assess overall capacity adequacy."""
        total_capacity = self._calculate_total_capacity(equipment_list)
        farm_size = farm_analysis.get("farm_size_category", "medium")
        
        # Simple capacity assessment
        capacity_thresholds = {
            "small": 100,
            "medium": 500,
            "large": 2000,
            "very_large": 5000
        }
        
        threshold = capacity_thresholds.get(farm_size, 500)
        
        if total_capacity < threshold * 0.5:
            return "insufficient"
        elif total_capacity > threshold * 2:
            return "excessive"
        else:
            return "adequate"
    
    def _identify_capacity_bottlenecks(self, equipment_list: List[Equipment], farm_analysis: Dict[str, Any]) -> List[str]:
        """Identify capacity bottlenecks."""
        bottlenecks = []
        
        capacity_by_category = self._calculate_capacity_by_category(equipment_list)
        farm_size = farm_analysis.get("farm_size_category", "medium")
        
        # Check for missing equipment categories
        required_categories = [EquipmentCategory.SPREADING, EquipmentCategory.SPRAYING]
        for category in required_categories:
            if category not in capacity_by_category or capacity_by_category[category] == 0:
                bottlenecks.append(f"Missing {category} equipment")
        
        return bottlenecks
    
    def _identify_optimization_opportunities(self, equipment_list: List[Equipment], farm_analysis: Dict[str, Any]) -> List[str]:
        """Identify optimization opportunities."""
        opportunities = []
        
        # Check for underutilized equipment
        for equipment in equipment_list:
            if equipment.capacity and equipment.capacity > 1000:  # Large capacity
                opportunities.append(f"Consider optimizing utilization of {equipment.name}")
        
        # Check for maintenance optimization
        high_maintenance_equipment = [eq for eq in equipment_list if eq.maintenance_level in [MaintenanceLevel.ADVANCED, MaintenanceLevel.PROFESSIONAL]]
        if high_maintenance_equipment:
            opportunities.append("Consider maintenance optimization for high-maintenance equipment")
        
        return opportunities
    
    def _filter_affordable_upgrades(self, upgrades: List[EquipmentUpgrade], budget_constraints: Optional[float]) -> List[EquipmentUpgrade]:
        """Filter upgrades that are within budget."""
        if not budget_constraints:
            return upgrades
        
        affordable_upgrades = []
        total_cost = 0
        
        for upgrade in upgrades:
            if upgrade.estimated_cost and total_cost + upgrade.estimated_cost <= budget_constraints:
                affordable_upgrades.append(upgrade)
                total_cost += upgrade.estimated_cost
        
        return affordable_upgrades
    
    def _calculate_roi_analysis(self, upgrades: List[EquipmentUpgrade]) -> Dict[str, Any]:
        """Calculate ROI analysis for upgrades."""
        total_cost = sum(upgrade.estimated_cost or 0 for upgrade in upgrades)
        total_benefits = sum(upgrade.payback_period or 0 for upgrade in upgrades)
        
        return {
            "total_investment": total_cost,
            "expected_benefits": total_benefits,
            "roi_percentage": (total_benefits - total_cost) / total_cost * 100 if total_cost > 0 else 0,
            "payback_period": total_cost / (total_benefits / 10) if total_benefits > 0 else None  # Assume 10-year benefit period
        }
    
    def _rank_upgrades_by_priority(self, upgrades: List[EquipmentUpgrade]) -> List[EquipmentUpgrade]:
        """Rank upgrades by priority."""
        priority_order = {"high": 3, "medium": 2, "low": 1}
        return sorted(upgrades, key=lambda x: priority_order.get(x.upgrade_priority, 0), reverse=True)
    
    def _create_implementation_timeline(self, upgrades: List[EquipmentUpgrade]) -> Dict[str, Any]:
        """Create implementation timeline for upgrades."""
        timeline = {
            "immediate": [upgrade for upgrade in upgrades if upgrade.upgrade_priority == "high"],
            "short_term": [upgrade for upgrade in upgrades if upgrade.upgrade_priority == "medium"],
            "long_term": [upgrade for upgrade in upgrades if upgrade.upgrade_priority == "low"]
        }
        
        return timeline
    
    def _prioritize_upgrades(self, upgrades: List[EquipmentUpgrade]) -> List[str]:
        """Prioritize upgrades for implementation."""
        return [upgrade.current_equipment_id for upgrade in self._rank_upgrades_by_priority(upgrades)]
    
    def _calculate_upgraded_capacity(self, equipment: Equipment, farm_analysis: Dict[str, Any]) -> Optional[float]:
        """Calculate upgraded capacity for equipment."""
        if not equipment.capacity:
            return None
        
        # Increase capacity by 50% for upgrades
        return equipment.capacity * 1.5
    
    def _assess_capacity_suitability(self, equipment: Equipment, farm_analysis: Dict[str, Any]) -> float:
        """Assess capacity suitability for farm."""
        capacity_adequacy = self._assess_capacity_adequacy(equipment, farm_analysis)
        
        if capacity_adequacy == "adequate":
            return 1.0
        elif capacity_adequacy == "insufficient":
            return 0.3
        elif capacity_adequacy == "excessive":
            return 0.7
        else:
            return 0.5
    
    def _assess_age_factor(self, equipment: Equipment) -> float:
        """Assess age factor for equipment."""
        if not equipment.year:
            return 0.5
        
        age = 2024 - equipment.year
        
        if age < 5:
            return 1.0
        elif age < 10:
            return 0.8
        elif age < 15:
            return 0.6
        else:
            return 0.3
    
    def _assess_maintenance_compatibility(self, equipment: Equipment, farm_analysis: Dict[str, Any]) -> float:
        """Assess maintenance compatibility."""
        maintenance_capability = farm_analysis.get("maintenance_capability", "basic")
        
        compatibility_scores = {
            (MaintenanceLevel.BASIC, "basic"): 1.0,
            (MaintenanceLevel.BASIC, "intermediate"): 1.0,
            (MaintenanceLevel.BASIC, "advanced"): 1.0,
            (MaintenanceLevel.INTERMEDIATE, "basic"): 0.7,
            (MaintenanceLevel.INTERMEDIATE, "intermediate"): 1.0,
            (MaintenanceLevel.INTERMEDIATE, "advanced"): 1.0,
            (MaintenanceLevel.ADVANCED, "basic"): 0.4,
            (MaintenanceLevel.ADVANCED, "intermediate"): 0.7,
            (MaintenanceLevel.ADVANCED, "advanced"): 1.0,
            (MaintenanceLevel.PROFESSIONAL, "basic"): 0.2,
            (MaintenanceLevel.PROFESSIONAL, "intermediate"): 0.5,
            (MaintenanceLevel.PROFESSIONAL, "advanced"): 0.8
        }
        
        return compatibility_scores.get((equipment.maintenance_level, maintenance_capability), 0.5)
    
    def _assess_status_factor(self, equipment: Equipment) -> float:
        """Assess status factor for equipment."""
        status_scores = {
            EquipmentStatus.OPERATIONAL: 1.0,
            EquipmentStatus.MAINTENANCE_REQUIRED: 0.7,
            EquipmentStatus.OUT_OF_SERVICE: 0.2,
            EquipmentStatus.RETIRED: 0.0
        }
        return status_scores.get(equipment.status, 0.5)
    
    async def _calculate_overall_score(
        self, 
        equipment_assessments: List[EquipmentAssessment],
        efficiency_assessments: List[EquipmentEfficiency],
        compatibility_assessments: List[EquipmentCompatibility]
    ) -> float:
        """Calculate overall assessment score."""
        if not equipment_assessments:
            return 0.0
        
        # Calculate weighted average of all assessment scores
        total_score = 0.0
        total_weight = 0.0
        
        for assessment in equipment_assessments:
            weight = 1.0
            total_score += assessment.suitability_score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    async def _perform_comprehensive_farm_assessment(
        self, 
        request: EquipmentAssessmentRequest, 
        equipment_objects: List[Equipment], 
        farm_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive farm assessment including all aspects."""
        try:
            # Perform field layout analysis
            field_layout_analysis = await self._analyze_field_layouts(request)
            
            # Perform storage facility assessment
            storage_facility_assessment = await self._assess_storage_facilities(request)
            
            # Perform labor analysis
            labor_analysis = await self._analyze_labor_requirements(request, equipment_objects)
            
            # Perform environmental assessment
            environmental_assessment = await self._assess_environmental_impact(equipment_objects)
            
            # Calculate operational efficiency score
            operational_efficiency_score = await self._calculate_operational_efficiency_score(
                farm_analysis, field_layout_analysis, storage_facility_assessment, 
                labor_analysis, environmental_assessment
            )
            
            # Generate optimization recommendations
            optimization_recommendations = await self._generate_optimization_recommendations(
                farm_analysis, field_layout_analysis, storage_facility_assessment, 
                labor_analysis, environmental_assessment
            )
            
            # Generate implementation priorities
            implementation_priorities = await self._generate_implementation_priorities(
                optimization_recommendations, request.budget_constraints
            )
            
            return {
                "farm_assessment": farm_analysis,
                "field_layout_analysis": [layout.dict() for layout in field_layout_analysis],
                "storage_facility_assessment": [storage.dict() for storage in storage_facility_assessment],
                "labor_analysis": labor_analysis.dict(),
                "environmental_assessment": [env.dict() for env in environmental_assessment],
                "operational_efficiency_score": operational_efficiency_score,
                "optimization_recommendations": optimization_recommendations,
                "implementation_priorities": implementation_priorities
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive farm assessment: {e}")
            return {
                "farm_assessment": farm_analysis,
                "field_layout_analysis": [],
                "storage_facility_assessment": [],
                "labor_analysis": {},
                "environmental_assessment": [],
                "operational_efficiency_score": 0.5,
                "optimization_recommendations": [],
                "implementation_priorities": []
            }
    
    async def _analyze_field_layouts(self, request: EquipmentAssessmentRequest) -> List[FieldLayoutAnalysis]:
        """Analyze field layouts for operational efficiency."""
        field_layouts = []
        
        if request.field_layouts:
            for i, layout_data in enumerate(request.field_layouts):
                field_layout = FieldLayoutAnalysis(
                    field_id=f"field_{i}",
                    field_shape=layout_data.get("shape", "rectangular"),
                    field_size_acres=layout_data.get("size_acres", request.average_field_size),
                    access_points=layout_data.get("access_points", 2),
                    access_road_length=layout_data.get("access_road_length"),
                    field_efficiency_score=self._calculate_field_efficiency_score(layout_data),
                    turning_radius_requirements=layout_data.get("turning_radius"),
                    operational_constraints=self._identify_field_constraints(layout_data),
                    optimization_opportunities=self._identify_field_optimization_opportunities(layout_data)
                )
                field_layouts.append(field_layout)
        else:
            # Create default field layout analysis based on farm characteristics
            for i in range(request.field_count):
                field_layout = FieldLayoutAnalysis(
                    field_id=f"field_{i}",
                    field_shape="rectangular",
                    field_size_acres=request.average_field_size,
                    access_points=2,
                    access_road_length=None,
                    field_efficiency_score=0.7,  # Default efficiency score
                    turning_radius_requirements=None,
                    operational_constraints=[],
                    optimization_opportunities=[]
                )
                field_layouts.append(field_layout)
        
        return field_layouts
    
    async def _assess_storage_facilities(self, request: EquipmentAssessmentRequest) -> List[StorageFacilityAssessment]:
        """Assess storage facilities for farm operations."""
        storage_assessments = []
        
        if request.storage_facilities:
            for i, facility_data in enumerate(request.storage_facilities):
                storage_assessment = StorageFacilityAssessment(
                    facility_id=f"storage_{i}",
                    facility_type=facility_data.get("type", "general"),
                    capacity_tons=facility_data.get("capacity_tons"),
                    location_efficiency=self._calculate_location_efficiency(facility_data),
                    handling_equipment_compatibility=facility_data.get("compatible_equipment", []),
                    access_quality=facility_data.get("access_quality", "good"),
                    environmental_conditions=facility_data.get("environmental_conditions", {}),
                    maintenance_requirements=self._identify_storage_maintenance_requirements(facility_data),
                    upgrade_recommendations=self._generate_storage_upgrade_recommendations(facility_data)
                )
                storage_assessments.append(storage_assessment)
        else:
            # Create default storage assessment
            storage_assessment = StorageFacilityAssessment(
                facility_id="storage_default",
                facility_type="general",
                capacity_tons=100.0,  # Default capacity
                location_efficiency=0.7,
                handling_equipment_compatibility=[],
                access_quality="good",
                environmental_conditions={},
                maintenance_requirements=[],
                upgrade_recommendations=[]
            )
            storage_assessments.append(storage_assessment)
        
        return storage_assessments
    
    async def _analyze_labor_requirements(
        self, 
        request: EquipmentAssessmentRequest, 
        equipment_objects: List[Equipment]
    ) -> LaborAnalysis:
        """Analyze labor requirements for farm operations."""
        # Calculate total labor hours needed
        total_labor_hours = self._calculate_total_labor_hours(equipment_objects, request.farm_size_acres)
        
        # Determine skill requirements
        skill_requirements = self._determine_skill_requirements(equipment_objects)
        
        # Identify training needs
        training_needs = self._identify_training_needs(equipment_objects, request.labor_availability)
        
        # Calculate labor efficiency score
        labor_efficiency_score = self._calculate_labor_efficiency_score(
            request.labor_availability, request.maintenance_capability
        )
        
        labor_analysis = LaborAnalysis(
            farm_id="current_farm",
            total_labor_hours_available=total_labor_hours,
            skilled_labor_percentage=self._estimate_skilled_labor_percentage(request.labor_availability),
            labor_efficiency_score=labor_efficiency_score,
            skill_requirements=skill_requirements,
            training_needs=training_needs,
            labor_cost_per_hour=request.labor_details.get("cost_per_hour") if request.labor_details else None,
            seasonal_availability=request.labor_details.get("seasonal_availability", {}) if request.labor_details else {}
        )
        
        return labor_analysis
    
    async def _assess_environmental_impact(self, equipment_objects: List[Equipment]) -> List[EnvironmentalAssessment]:
        """Assess environmental impact of equipment and operations."""
        environmental_assessments = []
        
        for equipment in equipment_objects:
            environmental_assessment = EnvironmentalAssessment(
                equipment_id=equipment.equipment_id,
                fuel_efficiency_rating=self._calculate_fuel_efficiency_rating(equipment),
                emissions_factor=self._calculate_emissions_factor(equipment),
                noise_level=self._estimate_noise_level(equipment),
                environmental_impact_score=self._calculate_environmental_impact_score(equipment),
                sustainability_metrics=self._calculate_sustainability_metrics(equipment),
                compliance_status=self._check_environmental_compliance(equipment),
                improvement_recommendations=self._generate_environmental_improvements(equipment)
            )
            environmental_assessments.append(environmental_assessment)
        
        return environmental_assessments
    
    async def _calculate_operational_efficiency_score(
        self, 
        farm_analysis: Dict[str, Any], 
        field_layouts: List[FieldLayoutAnalysis], 
        storage_assessments: List[StorageFacilityAssessment], 
        labor_analysis: LaborAnalysis, 
        environmental_assessments: List[EnvironmentalAssessment]
    ) -> float:
        """Calculate overall operational efficiency score."""
        # Weighted average of different efficiency components
        field_efficiency = sum(layout.field_efficiency_score for layout in field_layouts) / len(field_layouts) if field_layouts else 0.7
        storage_efficiency = sum(storage.location_efficiency for storage in storage_assessments) / len(storage_assessments) if storage_assessments else 0.7
        labor_efficiency = labor_analysis.labor_efficiency_score
        environmental_efficiency = sum(env.environmental_impact_score for env in environmental_assessments) / len(environmental_assessments) if environmental_assessments else 0.7
        
        # Weighted average
        overall_efficiency = (
            field_efficiency * 0.3 +
            storage_efficiency * 0.2 +
            labor_efficiency * 0.3 +
            environmental_efficiency * 0.2
        )
        
        return min(overall_efficiency, 1.0)
    
    async def _generate_optimization_recommendations(
        self, 
        farm_analysis: Dict[str, Any], 
        field_layouts: List[FieldLayoutAnalysis], 
        storage_assessments: List[StorageFacilityAssessment], 
        labor_analysis: LaborAnalysis, 
        environmental_assessments: List[EnvironmentalAssessment]
    ) -> List[str]:
        """Generate optimization recommendations based on comprehensive assessment."""
        recommendations = []
        
        # Field layout optimization recommendations
        for layout in field_layouts:
            if layout.field_efficiency_score < 0.7:
                recommendations.append(f"Optimize field {layout.field_id} layout for better operational efficiency")
            if layout.access_points < 2:
                recommendations.append(f"Add access points to field {layout.field_id} for better equipment access")
        
        # Storage facility optimization recommendations
        for storage in storage_assessments:
            if storage.location_efficiency < 0.7:
                recommendations.append(f"Improve storage facility {storage.facility_id} location efficiency")
            if storage.access_quality == "poor":
                recommendations.append(f"Upgrade access roads to storage facility {storage.facility_id}")
        
        # Labor optimization recommendations
        if labor_analysis.labor_efficiency_score < 0.7:
            recommendations.append("Improve labor efficiency through training and better scheduling")
        if labor_analysis.skilled_labor_percentage < 50:
            recommendations.append("Increase skilled labor percentage through training programs")
        
        # Environmental optimization recommendations
        for env in environmental_assessments:
            if env.environmental_impact_score < 0.7:
                recommendations.append(f"Improve environmental performance of equipment {env.equipment_id}")
        
        return recommendations
    
    async def _generate_implementation_priorities(
        self, 
        optimization_recommendations: List[str], 
        budget_constraints: Optional[float]
    ) -> List[str]:
        """Generate implementation priorities based on recommendations and constraints."""
        priorities = []
        
        # High priority items (safety, compliance, critical operations)
        high_priority = [rec for rec in optimization_recommendations if "safety" in rec.lower() or "compliance" in rec.lower()]
        priorities.extend(high_priority)
        
        # Medium priority items (efficiency improvements)
        medium_priority = [rec for rec in optimization_recommendations if "efficiency" in rec.lower() or "optimize" in rec.lower()]
        priorities.extend(medium_priority)
        
        # Low priority items (nice-to-have improvements)
        low_priority = [rec for rec in optimization_recommendations if rec not in high_priority and rec not in medium_priority]
        priorities.extend(low_priority)
        
        return priorities
    
    def _calculate_field_efficiency_score(self, layout_data: Dict[str, Any]) -> float:
        """Calculate field efficiency score based on layout data."""
        score = 0.5  # Base score
        
        # Shape factor
        shape = layout_data.get("shape", "rectangular")
        if shape == "rectangular":
            score += 0.3
        elif shape == "square":
            score += 0.2
        elif shape == "irregular":
            score -= 0.1
        
        # Access points factor
        access_points = layout_data.get("access_points", 2)
        if access_points >= 3:
            score += 0.2
        elif access_points == 2:
            score += 0.1
        else:
            score -= 0.1
        
        # Size factor (optimal size range)
        size_acres = layout_data.get("size_acres", 50)
        if 20 <= size_acres <= 100:
            score += 0.2
        elif 10 <= size_acres <= 200:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _identify_field_constraints(self, layout_data: Dict[str, Any]) -> List[str]:
        """Identify operational constraints for field layout."""
        constraints = []
        
        shape = layout_data.get("shape", "rectangular")
        if shape == "irregular":
            constraints.append("Irregular field shape limits equipment efficiency")
        
        access_points = layout_data.get("access_points", 2)
        if access_points < 2:
            constraints.append("Limited access points restrict equipment movement")
        
        size_acres = layout_data.get("size_acres", 50)
        if size_acres < 10:
            constraints.append("Small field size limits equipment efficiency")
        elif size_acres > 200:
            constraints.append("Large field size may require specialized equipment")
        
        return constraints
    
    def _identify_field_optimization_opportunities(self, layout_data: Dict[str, Any]) -> List[str]:
        """Identify optimization opportunities for field layout."""
        opportunities = []
        
        shape = layout_data.get("shape", "rectangular")
        if shape == "irregular":
            opportunities.append("Consider field consolidation or reshaping")
        
        access_points = layout_data.get("access_points", 2)
        if access_points < 3:
            opportunities.append("Add additional access points for better equipment access")
        
        return opportunities
    
    def _calculate_location_efficiency(self, facility_data: Dict[str, Any]) -> float:
        """Calculate location efficiency for storage facility."""
        score = 0.5  # Base score
        
        # Access quality factor
        access_quality = facility_data.get("access_quality", "good")
        access_scores = {"excellent": 0.3, "good": 0.2, "fair": 0.1, "poor": -0.1}
        score += access_scores.get(access_quality, 0.1)
        
        # Capacity factor
        capacity_tons = facility_data.get("capacity_tons", 100)
        if capacity_tons >= 500:
            score += 0.2
        elif capacity_tons >= 100:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _identify_storage_maintenance_requirements(self, facility_data: Dict[str, Any]) -> List[str]:
        """Identify maintenance requirements for storage facility."""
        requirements = []
        
        facility_type = facility_data.get("type", "general")
        if facility_type == "silo":
            requirements.extend(["Inspect structural integrity", "Check ventilation systems", "Clean interior surfaces"])
        elif facility_type == "bunker":
            requirements.extend(["Check drainage systems", "Inspect walls", "Clean floor"])
        else:
            requirements.extend(["General inspection", "Clean surfaces", "Check access points"])
        
        return requirements
    
    def _generate_storage_upgrade_recommendations(self, facility_data: Dict[str, Any]) -> List[str]:
        """Generate upgrade recommendations for storage facility."""
        recommendations = []
        
        access_quality = facility_data.get("access_quality", "good")
        if access_quality == "poor":
            recommendations.append("Upgrade access roads and loading areas")
        
        capacity_tons = facility_data.get("capacity_tons", 100)
        if capacity_tons < 100:
            recommendations.append("Consider expanding storage capacity")
        
        return recommendations
    
    def _calculate_total_labor_hours(self, equipment_objects: List[Equipment], farm_size_acres: float) -> float:
        """Calculate total labor hours needed for farm operations."""
        # Base labor hours per acre
        base_hours_per_acre = 2.0
        
        # Adjust for equipment complexity
        complexity_factor = 1.0
        for equipment in equipment_objects:
            if equipment.maintenance_level == MaintenanceLevel.ADVANCED:
                complexity_factor += 0.1
            elif equipment.maintenance_level == MaintenanceLevel.PROFESSIONAL:
                complexity_factor += 0.2
        
        total_hours = farm_size_acres * base_hours_per_acre * complexity_factor
        return total_hours
    
    def _determine_skill_requirements(self, equipment_objects: List[Equipment]) -> Dict[str, str]:
        """Determine skill requirements by equipment type."""
        skill_requirements = {}
        
        for equipment in equipment_objects:
            if equipment.maintenance_level == MaintenanceLevel.BASIC:
                skill_requirements[equipment.equipment_id] = "basic"
            elif equipment.maintenance_level == MaintenanceLevel.INTERMEDIATE:
                skill_requirements[equipment.equipment_id] = "intermediate"
            elif equipment.maintenance_level == MaintenanceLevel.ADVANCED:
                skill_requirements[equipment.equipment_id] = "advanced"
            else:
                skill_requirements[equipment.equipment_id] = "professional"
        
        return skill_requirements
    
    def _identify_training_needs(self, equipment_objects: List[Equipment], labor_availability: Optional[str]) -> List[str]:
        """Identify training needs based on equipment and labor availability."""
        training_needs = []
        
        if labor_availability == "low":
            training_needs.append("Basic equipment operation training")
        
        for equipment in equipment_objects:
            if equipment.maintenance_level in [MaintenanceLevel.ADVANCED, MaintenanceLevel.PROFESSIONAL]:
                training_needs.append(f"Advanced maintenance training for {equipment.name}")
        
        return list(set(training_needs))  # Remove duplicates
    
    def _calculate_labor_efficiency_score(self, labor_availability: Optional[str], maintenance_capability: Optional[str]) -> float:
        """Calculate labor efficiency score."""
        score = 0.5  # Base score
        
        # Labor availability factor
        availability_scores = {"high": 0.3, "medium": 0.2, "low": 0.1}
        score += availability_scores.get(labor_availability, 0.1)
        
        # Maintenance capability factor
        capability_scores = {"advanced": 0.2, "intermediate": 0.1, "basic": 0.0}
        score += capability_scores.get(maintenance_capability, 0.0)
        
        return max(0.0, min(1.0, score))
    
    def _estimate_skilled_labor_percentage(self, labor_availability: Optional[str]) -> float:
        """Estimate skilled labor percentage based on labor availability."""
        if labor_availability == "high":
            return 70.0
        elif labor_availability == "medium":
            return 50.0
        else:
            return 30.0
    
    def _calculate_fuel_efficiency_rating(self, equipment: Equipment) -> float:
        """Calculate fuel efficiency rating for equipment."""
        # Base efficiency based on equipment age and type
        base_efficiency = 0.7
        
        if equipment.year:
            age = 2024 - equipment.year
            if age < 5:
                base_efficiency += 0.2
            elif age < 10:
                base_efficiency += 0.1
            elif age > 15:
                base_efficiency -= 0.2
        
        # Equipment type factor
        type_factors = {
            EquipmentCategory.SPREADING: 0.8,
            EquipmentCategory.SPRAYING: 0.7,
            EquipmentCategory.INJECTION: 0.6,
            EquipmentCategory.IRRIGATION: 0.9
        }
        
        type_factor = type_factors.get(equipment.category, 0.7)
        return max(0.0, min(1.0, base_efficiency * type_factor))
    
    def _calculate_emissions_factor(self, equipment: Equipment) -> Optional[float]:
        """Calculate emissions factor for equipment."""
        # Simplified emissions calculation based on equipment age and type
        if not equipment.year:
            return None
        
        age = 2024 - equipment.year
        base_emissions = 1.0
        
        # Newer equipment has lower emissions
        if age < 5:
            base_emissions *= 0.8
        elif age < 10:
            base_emissions *= 0.9
        elif age > 15:
            base_emissions *= 1.2
        
        return base_emissions
    
    def _estimate_noise_level(self, equipment: Equipment) -> Optional[float]:
        """Estimate noise level for equipment."""
        # Simplified noise estimation based on equipment type
        noise_levels = {
            EquipmentCategory.SPREADING: 85.0,
            EquipmentCategory.SPRAYING: 80.0,
            EquipmentCategory.INJECTION: 75.0,
            EquipmentCategory.IRRIGATION: 70.0
        }
        
        return noise_levels.get(equipment.category, 80.0)
    
    def _calculate_environmental_impact_score(self, equipment: Equipment) -> float:
        """Calculate environmental impact score for equipment."""
        fuel_efficiency = self._calculate_fuel_efficiency_rating(equipment)
        emissions_factor = self._calculate_emissions_factor(equipment) or 1.0
        
        # Higher fuel efficiency and lower emissions = better environmental score
        environmental_score = fuel_efficiency * (1.0 / emissions_factor)
        
        return max(0.0, min(1.0, environmental_score))
    
    def _calculate_sustainability_metrics(self, equipment: Equipment) -> Dict[str, Any]:
        """Calculate sustainability metrics for equipment."""
        return {
            "fuel_efficiency": self._calculate_fuel_efficiency_rating(equipment),
            "emissions_factor": self._calculate_emissions_factor(equipment),
            "noise_level": self._estimate_noise_level(equipment),
            "environmental_score": self._calculate_environmental_impact_score(equipment)
        }
    
    def _check_environmental_compliance(self, equipment: Equipment) -> List[str]:
        """Check environmental compliance status for equipment."""
        compliance_status = []
        
        # Check emissions compliance
        emissions_factor = self._calculate_emissions_factor(equipment)
        if emissions_factor and emissions_factor <= 1.0:
            compliance_status.append("Emissions compliant")
        else:
            compliance_status.append("Emissions non-compliant")
        
        # Check noise compliance
        noise_level = self._estimate_noise_level(equipment)
        if noise_level and noise_level <= 85.0:
            compliance_status.append("Noise compliant")
        else:
            compliance_status.append("Noise non-compliant")
        
        return compliance_status
    
    def _generate_environmental_improvements(self, equipment: Equipment) -> List[str]:
        """Generate environmental improvement recommendations for equipment."""
        improvements = []
        
        fuel_efficiency = self._calculate_fuel_efficiency_rating(equipment)
        if fuel_efficiency < 0.8:
            improvements.append("Consider upgrading to more fuel-efficient equipment")
        
        emissions_factor = self._calculate_emissions_factor(equipment)
        if emissions_factor and emissions_factor > 1.0:
            improvements.append("Consider equipment with lower emissions")
        
        noise_level = self._estimate_noise_level(equipment)
        if noise_level and noise_level > 85.0:
            improvements.append("Consider noise reduction measures")
        
        return improvements
    
    def _calculate_detailed_cost_breakdown(self, upgrade_recommendations: List[EquipmentUpgrade]) -> Dict[str, Any]:
        """Calculate detailed cost breakdown for upgrades."""
        breakdown = {
            "equipment_costs": {},
            "installation_costs": {},
            "training_costs": {},
            "infrastructure_costs": {},
            "total_costs": {}
        }
        
        for upgrade in upgrade_recommendations:
            equipment_id = upgrade.current_equipment_id
            estimated_cost = upgrade.estimated_cost or 0
            
            # Equipment cost (70% of total)
            equipment_cost = estimated_cost * 0.7
            breakdown["equipment_costs"][equipment_id] = equipment_cost
            
            # Installation cost (15% of total)
            installation_cost = estimated_cost * 0.15
            breakdown["installation_costs"][equipment_id] = installation_cost
            
            # Training cost (5% of total)
            training_cost = estimated_cost * 0.05
            breakdown["training_costs"][equipment_id] = training_cost
            
            # Infrastructure cost (10% of total)
            infrastructure_cost = estimated_cost * 0.10
            breakdown["infrastructure_costs"][equipment_id] = infrastructure_cost
            
            # Total cost
            breakdown["total_costs"][equipment_id] = estimated_cost
        
        return breakdown
    
    def _calculate_operational_cost_analysis(self, upgrade_recommendations: List[EquipmentUpgrade]) -> Dict[str, Any]:
        """Calculate operational cost analysis for upgrades."""
        analysis = {
            "fuel_savings": {},
            "labor_savings": {},
            "maintenance_savings": {},
            "downtime_reduction": {},
            "total_annual_savings": {}
        }
        
        for upgrade in upgrade_recommendations:
            equipment_id = upgrade.current_equipment_id
            estimated_cost = upgrade.estimated_cost or 0
            
            # Estimate annual savings (15% of equipment cost)
            annual_savings = estimated_cost * 0.15
            
            # Break down savings by category
            analysis["fuel_savings"][equipment_id] = annual_savings * 0.4  # 40% fuel savings
            analysis["labor_savings"][equipment_id] = annual_savings * 0.3  # 30% labor savings
            analysis["maintenance_savings"][equipment_id] = annual_savings * 0.2  # 20% maintenance savings
            analysis["downtime_reduction"][equipment_id] = annual_savings * 0.1  # 10% downtime reduction
            analysis["total_annual_savings"][equipment_id] = annual_savings
        
        return analysis
    
    def _calculate_maintenance_cost_analysis(self, upgrade_recommendations: List[EquipmentUpgrade]) -> Dict[str, Any]:
        """Calculate maintenance cost analysis for upgrades."""
        analysis = {
            "preventive_maintenance": {},
            "corrective_maintenance": {},
            "parts_and_supplies": {},
            "labor_costs": {},
            "total_maintenance_costs": {}
        }
        
        for upgrade in upgrade_recommendations:
            equipment_id = upgrade.current_equipment_id
            estimated_cost = upgrade.estimated_cost or 0
            
            # Annual maintenance cost (5% of equipment cost)
            annual_maintenance = estimated_cost * 0.05
            
            # Break down maintenance costs
            analysis["preventive_maintenance"][equipment_id] = annual_maintenance * 0.6  # 60% preventive
            analysis["corrective_maintenance"][equipment_id] = annual_maintenance * 0.2  # 20% corrective
            analysis["parts_and_supplies"][equipment_id] = annual_maintenance * 0.15  # 15% parts
            analysis["labor_costs"][equipment_id] = annual_maintenance * 0.05  # 5% labor
            analysis["total_maintenance_costs"][equipment_id] = annual_maintenance
        
        return analysis
    
    def _perform_sensitivity_analysis(self, upgrade_recommendations: List[EquipmentUpgrade]) -> Dict[str, Any]:
        """Perform sensitivity analysis for upgrade recommendations."""
        analysis = {
            "cost_sensitivity": {},
            "benefit_sensitivity": {},
            "payback_sensitivity": {},
            "risk_factors": {}
        }
        
        for upgrade in upgrade_recommendations:
            equipment_id = upgrade.current_equipment_id
            estimated_cost = upgrade.estimated_cost or 0
            
            # Cost sensitivity (±20% variation)
            analysis["cost_sensitivity"][equipment_id] = {
                "base_cost": estimated_cost,
                "high_cost": estimated_cost * 1.2,
                "low_cost": estimated_cost * 0.8
            }
            
            # Benefit sensitivity (±15% variation)
            annual_benefit = estimated_cost * 0.15
            analysis["benefit_sensitivity"][equipment_id] = {
                "base_benefit": annual_benefit,
                "high_benefit": annual_benefit * 1.15,
                "low_benefit": annual_benefit * 0.85
            }
            
            # Payback sensitivity
            base_payback = estimated_cost / annual_benefit if annual_benefit > 0 else 0
            analysis["payback_sensitivity"][equipment_id] = {
                "base_payback": base_payback,
                "high_payback": estimated_cost / (annual_benefit * 0.85) if annual_benefit > 0 else 0,
                "low_payback": estimated_cost / (annual_benefit * 1.15) if annual_benefit > 0 else 0
            }
            
            # Risk factors
            analysis["risk_factors"][equipment_id] = [
                "Market price volatility",
                "Technology obsolescence",
                "Regulatory changes",
                "Maintenance cost increases"
            ]
        
        return analysis
    
    def _calculate_break_even_analysis(self, upgrade_recommendations: List[EquipmentUpgrade]) -> Dict[str, Any]:
        """Calculate break-even analysis for upgrades."""
        analysis = {
            "break_even_years": {},
            "break_even_acres": {},
            "break_even_usage_hours": {},
            "break_even_scenarios": {}
        }
        
        for upgrade in upgrade_recommendations:
            equipment_id = upgrade.current_equipment_id
            estimated_cost = upgrade.estimated_cost or 0
            annual_benefit = estimated_cost * 0.15
            
            # Break-even years
            break_even_years = estimated_cost / annual_benefit if annual_benefit > 0 else 0
            analysis["break_even_years"][equipment_id] = break_even_years
            
            # Break-even acres (assuming $50/acre benefit)
            benefit_per_acre = 50.0
            break_even_acres = estimated_cost / benefit_per_acre if benefit_per_acre > 0 else 0
            analysis["break_even_acres"][equipment_id] = break_even_acres
            
            # Break-even usage hours (assuming $25/hour benefit)
            benefit_per_hour = 25.0
            break_even_hours = estimated_cost / benefit_per_hour if benefit_per_hour > 0 else 0
            analysis["break_even_usage_hours"][equipment_id] = break_even_hours
            
            # Break-even scenarios
            analysis["break_even_scenarios"][equipment_id] = {
                "conservative": break_even_years * 1.5,  # 50% longer
                "optimistic": break_even_years * 0.7,   # 30% shorter
                "realistic": break_even_years
            }
        
        return analysis
    
    def _analyze_financing_options(self, upgrade_recommendations: List[EquipmentUpgrade], budget_constraints: Optional[float]) -> Dict[str, Any]:
        """Analyze financing options for upgrades."""
        total_cost = sum(upgrade.estimated_cost or 0 for upgrade in upgrade_recommendations)
        
        analysis = {
            "total_upgrade_cost": total_cost,
            "budget_constraints": budget_constraints,
            "financing_options": {},
            "recommended_financing": {}
        }
        
        # Cash purchase
        analysis["financing_options"]["cash"] = {
            "total_cost": total_cost,
            "down_payment": total_cost,
            "monthly_payment": 0,
            "total_interest": 0,
            "total_cost_with_financing": total_cost,
            "advantages": ["No interest", "Full ownership", "Simplified accounting"],
            "disadvantages": ["Large upfront cost", "Opportunity cost", "Cash flow impact"]
        }
        
        # Equipment loan (5% interest, 5 years)
        loan_rate = 0.05
        loan_years = 5
        monthly_rate = loan_rate / 12
        total_payments = loan_years * 12
        
        monthly_payment = total_cost * (monthly_rate * (1 + monthly_rate)**total_payments) / ((1 + monthly_rate)**total_payments - 1)
        total_interest = (monthly_payment * total_payments) - total_cost
        
        analysis["financing_options"]["equipment_loan"] = {
            "total_cost": total_cost,
            "down_payment": total_cost * 0.1,  # 10% down
            "monthly_payment": monthly_payment,
            "total_interest": total_interest,
            "total_cost_with_financing": total_cost + total_interest,
            "advantages": ["Preserves cash flow", "Tax deductible interest", "Fixed payments"],
            "disadvantages": ["Interest costs", "Longer payback", "Collateral required"]
        }
        
        # Lease option (3% of equipment value per year)
        lease_rate = 0.03
        annual_lease = total_cost * lease_rate
        monthly_lease = annual_lease / 12
        
        analysis["financing_options"]["lease"] = {
            "total_cost": total_cost,
            "down_payment": 0,
            "monthly_payment": monthly_lease,
            "total_interest": annual_lease * 3 - total_cost,  # 3-year lease
            "total_cost_with_financing": annual_lease * 3,
            "advantages": ["Lower monthly payments", "No maintenance responsibility", "Easy upgrade"],
            "disadvantages": ["No ownership", "Higher total cost", "Limited customization"]
        }
        
        # Recommended financing based on budget constraints
        if budget_constraints and budget_constraints >= total_cost:
            analysis["recommended_financing"] = "cash"
        elif budget_constraints and budget_constraints >= total_cost * 0.1:
            analysis["recommended_financing"] = "equipment_loan"
        else:
            analysis["recommended_financing"] = "lease"
        
        return analysis
    # Methods expected by tests
    async def assess_equipment_compatibility(self, equipment: Equipment) -> Dict[str, Any]:
        """Assess equipment compatibility for fertilizer application."""
        return await self._generate_compatibility_assessments([equipment])
    
    async def calculate_application_efficiency(self, equipment: Equipment) -> Dict[str, Any]:
        """Calculate application efficiency for equipment."""
        return await self._generate_efficiency_assessments([equipment])
    
    async def estimate_operational_costs(self, equipment: Equipment, field_size_acres: float = 40.0) -> Dict[str, Any]:
        """Estimate operational costs for equipment."""
        return await self._perform_cost_benefit_analysis([equipment], field_size_acres)
