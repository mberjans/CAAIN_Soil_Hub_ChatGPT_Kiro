"""
Equipment Assessment Service for comprehensive farm equipment evaluation and optimization.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from uuid import uuid4

from ..models.application_models import EquipmentAssessmentRequest, EquipmentAssessmentResponse
from ..models.equipment_models import (
    Equipment, EquipmentCategory, EquipmentStatus, MaintenanceLevel,
    SpreaderEquipment, SprayerEquipment, InjectionEquipment, DripSystemEquipment,
    EquipmentInventory, EquipmentCompatibility, EquipmentEfficiency,
    EquipmentUpgrade, EquipmentAssessment, EquipmentMaintenance, EquipmentPerformance
)

logger = logging.getLogger(__name__)


class EquipmentAssessmentService:
    """Service for comprehensive equipment assessment and optimization."""
    
    def __init__(self):
        self.equipment_database = {}
        self._initialize_equipment_database()
    
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
            
            # Analyze farm characteristics
            farm_analysis = await self._analyze_farm_characteristics(request)
            
            # Assess current equipment inventory
            equipment_inventory = await self._assess_equipment_inventory(request.current_equipment)
            
            # Perform individual equipment assessments
            equipment_assessments = await self._assess_individual_equipment(
                request.current_equipment, farm_analysis
            )
            
            # Generate compatibility assessments
            compatibility_assessments = await self._generate_compatibility_assessments(
                request.current_equipment, farm_analysis
            )
            
            # Generate efficiency assessments
            efficiency_assessments = await self._generate_efficiency_assessments(
                request.current_equipment, farm_analysis
            )
            
            # Generate upgrade recommendations
            upgrade_recommendations = await self._generate_upgrade_recommendations(
                request.current_equipment, farm_analysis, request.budget_constraints
            )
            
            # Perform capacity analysis
            capacity_analysis = await self._perform_capacity_analysis(
                request.current_equipment, farm_analysis
            )
            
            # Perform cost-benefit analysis
            cost_benefit_analysis = await self._perform_cost_benefit_analysis(
                upgrade_recommendations, request.budget_constraints
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
                processing_time_ms=processing_time_ms
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
    ) -> List[EquipmentAssessment]:
        """Assess individual equipment items."""
        assessments = []
        
        for equipment in equipment_list:
            assessment = EquipmentAssessment(
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
        """Perform cost-benefit analysis for upgrades."""
        analysis = {
            "total_upgrade_cost": sum(upgrade.estimated_cost or 0 for upgrade in upgrade_recommendations),
            "budget_constraints": budget_constraints,
            "affordable_upgrades": self._filter_affordable_upgrades(upgrade_recommendations, budget_constraints),
            "roi_analysis": self._calculate_roi_analysis(upgrade_recommendations),
            "priority_ranking": self._rank_upgrades_by_priority(upgrade_recommendations),
            "implementation_timeline": self._create_implementation_timeline(upgrade_recommendations)
        }
        return analysis
    
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
    
    def _assess_maintenance_requirements(self, equipment: Equipment) -> Optional[str]:
        """Assess maintenance requirements for equipment."""
        maintenance_levels = {
            MaintenanceLevel.BASIC: "Basic maintenance required",
            MaintenanceLevel.INTERMEDIATE: "Intermediate maintenance required",
            MaintenanceLevel.ADVANCED: "Advanced maintenance required",
            MaintenanceLevel.PROFESSIONAL: "Professional maintenance required"
        }
        return maintenance_levels.get(equipment.maintenance_level)
    
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