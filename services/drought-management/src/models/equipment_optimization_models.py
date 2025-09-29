"""
Equipment Optimization and Investment Planning Models

Data models for equipment optimization, investment analysis, and planning
for drought management systems.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from enum import Enum


class InvestmentType(str, Enum):
    """Types of equipment investments."""
    PURCHASE = "purchase"
    LEASE = "lease"
    RENTAL = "rental"
    UPGRADE = "upgrade"
    MAINTENANCE = "maintenance"
    REPLACEMENT = "replacement"


class InvestmentPriority(str, Enum):
    """Investment priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FinancingOption(str, Enum):
    """Financing options for equipment investments."""
    CASH = "cash"
    BANK_LOAN = "bank_loan"
    EQUIPMENT_LEASE = "equipment_lease"
    GOVERNMENT_PROGRAM = "government_program"
    VENDOR_FINANCING = "vendor_financing"
    EQUIPMENT_SHARING = "equipment_sharing"


class OptimizationObjective(str, Enum):
    """Equipment optimization objectives."""
    COST_MINIMIZATION = "cost_minimization"
    EFFICIENCY_MAXIMIZATION = "efficiency_maximization"
    CAPACITY_MAXIMIZATION = "capacity_maximization"
    RELIABILITY_MAXIMIZATION = "reliability_maximization"
    WATER_CONSERVATION = "water_conservation"
    DROUGHT_RESILIENCE = "drought_resilience"


class EquipmentOptimizationScenario(BaseModel):
    """Equipment optimization scenario."""
    scenario_id: UUID = Field(..., description="Unique scenario identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    scenario_name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    
    # Optimization parameters
    optimization_objectives: List[OptimizationObjective] = Field(..., description="Optimization objectives")
    budget_constraints: Optional[Decimal] = Field(None, ge=0, description="Budget constraints")
    timeline_months: int = Field(..., ge=1, le=60, description="Implementation timeline in months")
    risk_tolerance: str = Field("medium", description="Risk tolerance level")
    
    # Equipment requirements
    required_equipment_categories: List[str] = Field(..., description="Required equipment categories")
    field_characteristics: Dict[str, Any] = Field(..., description="Field characteristics")
    operational_requirements: Dict[str, Any] = Field(..., description="Operational requirements")
    
    # Constraints
    financing_preferences: List[FinancingOption] = Field(default_factory=list, description="Financing preferences")
    vendor_preferences: List[str] = Field(default_factory=list, description="Preferred vendors")
    maintenance_capabilities: Dict[str, Any] = Field(default_factory=dict, description="Maintenance capabilities")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EquipmentInvestmentOption(BaseModel):
    """Equipment investment option."""
    option_id: UUID = Field(..., description="Unique option identifier")
    scenario_id: UUID = Field(..., description="Scenario identifier")
    equipment_category: str = Field(..., description="Equipment category")
    equipment_name: str = Field(..., description="Equipment name")
    manufacturer: str = Field(..., description="Equipment manufacturer")
    model: str = Field(..., description="Equipment model")
    
    # Investment details
    investment_type: InvestmentType = Field(..., description="Type of investment")
    investment_cost: Decimal = Field(..., ge=0, description="Total investment cost")
    financing_option: FinancingOption = Field(..., description="Financing option")
    down_payment: Optional[Decimal] = Field(None, ge=0, description="Down payment amount")
    monthly_payment: Optional[Decimal] = Field(None, ge=0, description="Monthly payment amount")
    loan_term_months: Optional[int] = Field(None, ge=1, description="Loan term in months")
    interest_rate: Optional[float] = Field(None, ge=0, le=100, description="Interest rate percentage")
    
    # Equipment specifications
    capacity_specifications: Dict[str, Any] = Field(..., description="Capacity specifications")
    efficiency_ratings: Dict[str, float] = Field(..., description="Efficiency ratings")
    water_conservation_features: List[str] = Field(default_factory=list, description="Water conservation features")
    drought_resilience_features: List[str] = Field(default_factory=list, description="Drought resilience features")
    
    # Financial analysis
    annual_operating_cost: Decimal = Field(..., ge=0, description="Annual operating cost")
    annual_maintenance_cost: Decimal = Field(..., ge=0, description="Annual maintenance cost")
    expected_lifespan_years: int = Field(..., ge=1, description="Expected lifespan in years")
    residual_value: Optional[Decimal] = Field(None, ge=0, description="Expected residual value")
    
    # Performance metrics
    water_savings_percent: Optional[float] = Field(None, ge=0, le=100, description="Water savings percentage")
    efficiency_improvement_percent: Optional[float] = Field(None, ge=0, le=100, description="Efficiency improvement percentage")
    capacity_increase_percent: Optional[float] = Field(None, ge=0, le=100, description="Capacity increase percentage")
    
    # Risk factors
    implementation_risks: List[str] = Field(default_factory=list, description="Implementation risks")
    operational_risks: List[str] = Field(default_factory=list, description="Operational risks")
    financial_risks: List[str] = Field(default_factory=list, description="Financial risks")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InvestmentAnalysis(BaseModel):
    """Investment analysis for equipment option."""
    analysis_id: UUID = Field(..., description="Unique analysis identifier")
    option_id: UUID = Field(..., description="Investment option identifier")
    
    # Financial metrics
    net_present_value: Decimal = Field(..., description="Net present value")
    internal_rate_of_return: float = Field(..., ge=0, le=100, description="Internal rate of return percentage")
    payback_period_years: float = Field(..., ge=0, description="Payback period in years")
    return_on_investment: float = Field(..., ge=0, le=100, description="Return on investment percentage")
    
    # Cost analysis
    total_cost_of_ownership: Decimal = Field(..., ge=0, description="Total cost of ownership")
    annual_cost_savings: Decimal = Field(..., ge=0, description="Annual cost savings")
    cumulative_savings_5yr: Decimal = Field(..., ge=0, description="Cumulative savings over 5 years")
    break_even_point_years: float = Field(..., ge=0, description="Break-even point in years")
    
    # Sensitivity analysis
    sensitivity_scenarios: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Sensitivity analysis scenarios")
    risk_adjusted_return: float = Field(..., description="Risk-adjusted return")
    probability_of_success: float = Field(..., ge=0, le=1, description="Probability of success")
    
    # Performance analysis
    water_savings_value: Optional[Decimal] = Field(None, ge=0, description="Monetary value of water savings")
    efficiency_gains_value: Optional[Decimal] = Field(None, ge=0, description="Monetary value of efficiency gains")
    capacity_gains_value: Optional[Decimal] = Field(None, ge=0, description="Monetary value of capacity gains")
    
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class EquipmentOptimizationPlan(BaseModel):
    """Equipment optimization plan."""
    plan_id: UUID = Field(..., description="Unique plan identifier")
    scenario_id: UUID = Field(..., description="Scenario identifier")
    plan_name: str = Field(..., description="Plan name")
    description: str = Field(..., description="Plan description")
    
    # Plan details
    optimization_objectives: List[OptimizationObjective] = Field(..., description="Optimization objectives")
    implementation_timeline_months: int = Field(..., ge=1, le=60, description="Implementation timeline")
    total_investment_required: Decimal = Field(..., ge=0, description="Total investment required")
    total_annual_savings: Decimal = Field(..., ge=0, description="Total annual savings")
    
    # Investment options
    recommended_investments: List[EquipmentInvestmentOption] = Field(..., description="Recommended investments")
    investment_analyses: List[InvestmentAnalysis] = Field(..., description="Investment analyses")
    
    # Financial summary
    net_present_value: Decimal = Field(..., description="Overall net present value")
    internal_rate_of_return: float = Field(..., ge=0, le=100, description="Overall IRR percentage")
    payback_period_years: float = Field(..., ge=0, description="Overall payback period")
    return_on_investment: float = Field(..., ge=0, le=100, description="Overall ROI percentage")
    
    # Performance improvements
    water_savings_percent: Optional[float] = Field(None, ge=0, le=100, description="Overall water savings percentage")
    efficiency_improvement_percent: Optional[float] = Field(None, ge=0, le=100, description="Overall efficiency improvement")
    capacity_increase_percent: Optional[float] = Field(None, ge=0, le=100, description="Overall capacity increase")
    
    # Risk assessment
    overall_risk_score: float = Field(..., ge=0, le=1, description="Overall risk score")
    risk_factors: List[str] = Field(default_factory=list, description="Key risk factors")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Risk mitigation strategies")
    
    # Implementation details
    implementation_phases: List[Dict[str, Any]] = Field(default_factory=list, description="Implementation phases")
    required_resources: List[str] = Field(default_factory=list, description="Required resources")
    dependencies: List[str] = Field(default_factory=list, description="Implementation dependencies")
    
    # Monitoring and evaluation
    success_metrics: List[str] = Field(default_factory=list, description="Success metrics")
    monitoring_schedule: Dict[str, Any] = Field(default_factory=dict, description="Monitoring schedule")
    evaluation_criteria: List[str] = Field(default_factory=list, description="Evaluation criteria")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EquipmentSharingOpportunity(BaseModel):
    """Equipment sharing opportunity."""
    opportunity_id: UUID = Field(..., description="Unique opportunity identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    equipment_category: str = Field(..., description="Equipment category")
    equipment_name: str = Field(..., description="Equipment name")
    
    # Sharing details
    sharing_type: str = Field(..., description="Type of sharing arrangement")
    partner_farm_id: Optional[UUID] = Field(None, description="Partner farm identifier")
    partner_farm_name: Optional[str] = Field(None, description="Partner farm name")
    sharing_terms: Dict[str, Any] = Field(..., description="Sharing terms and conditions")
    
    # Financial benefits
    cost_sharing_percent: float = Field(..., ge=0, le=100, description="Cost sharing percentage")
    annual_cost_savings: Decimal = Field(..., ge=0, description="Annual cost savings")
    shared_maintenance_cost: Decimal = Field(..., ge=0, description="Shared maintenance cost")
    
    # Operational benefits
    increased_utilization: float = Field(..., ge=0, le=100, description="Increased utilization percentage")
    reduced_downtime: float = Field(..., ge=0, le=100, description="Reduced downtime percentage")
    improved_efficiency: float = Field(..., ge=0, le=100, description="Improved efficiency percentage")
    
    # Risk factors
    coordination_challenges: List[str] = Field(default_factory=list, description="Coordination challenges")
    scheduling_conflicts: List[str] = Field(default_factory=list, description="Scheduling conflicts")
    maintenance_responsibilities: List[str] = Field(default_factory=list, description="Maintenance responsibilities")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MultiYearInvestmentPlan(BaseModel):
    """Multi-year investment plan."""
    plan_id: UUID = Field(..., description="Unique plan identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    plan_name: str = Field(..., description="Plan name")
    planning_horizon_years: int = Field(..., ge=1, le=10, description="Planning horizon in years")
    
    # Investment phases
    investment_phases: List[Dict[str, Any]] = Field(..., description="Investment phases")
    phase_timelines: Dict[str, int] = Field(..., description="Phase timelines in months")
    phase_budgets: Dict[str, Decimal] = Field(..., description="Phase budgets")
    
    # Financial projections
    annual_investments: Dict[int, Decimal] = Field(..., description="Annual investment amounts")
    annual_savings: Dict[int, Decimal] = Field(..., description="Annual savings projections")
    cumulative_cash_flow: Dict[int, Decimal] = Field(..., description="Cumulative cash flow")
    
    # Performance projections
    water_savings_progression: Dict[int, float] = Field(..., description="Water savings progression")
    efficiency_improvements: Dict[int, float] = Field(..., description="Efficiency improvements")
    capacity_increases: Dict[int, float] = Field(..., description="Capacity increases")
    
    # Risk management
    contingency_budgets: Dict[str, Decimal] = Field(default_factory=dict, description="Contingency budgets")
    risk_scenarios: List[Dict[str, Any]] = Field(default_factory=list, description="Risk scenarios")
    mitigation_plans: List[Dict[str, Any]] = Field(default_factory=list, description="Mitigation plans")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Request Models
class EquipmentOptimizationRequest(BaseModel):
    """Request model for equipment optimization."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    optimization_objectives: List[OptimizationObjective] = Field(..., description="Optimization objectives")
    budget_constraints: Optional[Decimal] = Field(None, ge=0, description="Budget constraints")
    timeline_months: int = Field(12, ge=1, le=60, description="Implementation timeline")
    risk_tolerance: str = Field("medium", description="Risk tolerance")
    equipment_categories: List[str] = Field(..., description="Equipment categories to optimize")
    field_characteristics: Dict[str, Any] = Field(..., description="Field characteristics")
    financing_preferences: List[FinancingOption] = Field(default_factory=list, description="Financing preferences")


class InvestmentAnalysisRequest(BaseModel):
    """Request model for investment analysis."""
    scenario_id: UUID = Field(..., description="Scenario identifier")
    investment_options: List[EquipmentInvestmentOption] = Field(..., description="Investment options to analyze")
    analysis_depth: str = Field("comprehensive", description="Analysis depth (basic, standard, comprehensive)")
    include_sensitivity_analysis: bool = Field(True, description="Include sensitivity analysis")
    include_risk_assessment: bool = Field(True, description="Include risk assessment")
    discount_rate: float = Field(8.0, ge=0, le=20, description="Discount rate for NPV calculation")


class EquipmentSharingRequest(BaseModel):
    """Request model for equipment sharing analysis."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    equipment_categories: List[str] = Field(..., description="Equipment categories for sharing")
    sharing_radius_miles: float = Field(25.0, ge=1, le=100, description="Sharing radius in miles")
    include_cost_benefit_analysis: bool = Field(True, description="Include cost-benefit analysis")
    include_operational_analysis: bool = Field(True, description="Include operational analysis")


# Response Models
class EquipmentOptimizationResponse(BaseModel):
    """Response model for equipment optimization."""
    request_id: UUID = Field(..., description="Unique request identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    optimization_plan: EquipmentOptimizationPlan = Field(..., description="Optimization plan")
    investment_analyses: List[InvestmentAnalysis] = Field(..., description="Investment analyses")
    sharing_opportunities: List[EquipmentSharingOpportunity] = Field(default_factory=list, description="Sharing opportunities")
    multi_year_plan: Optional[MultiYearInvestmentPlan] = Field(None, description="Multi-year investment plan")
    executive_summary: Dict[str, Any] = Field(..., description="Executive summary")
    key_recommendations: List[str] = Field(..., description="Key recommendations")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class InvestmentAnalysisResponse(BaseModel):
    """Response model for investment analysis."""
    request_id: UUID = Field(..., description="Unique request identifier")
    scenario_id: UUID = Field(..., description="Scenario identifier")
    investment_analyses: List[InvestmentAnalysis] = Field(..., description="Investment analyses")
    comparison_summary: Dict[str, Any] = Field(..., description="Comparison summary")
    ranking_recommendations: List[Dict[str, Any]] = Field(..., description="Ranking recommendations")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class EquipmentSharingResponse(BaseModel):
    """Response model for equipment sharing analysis."""
    request_id: UUID = Field(..., description="Unique request identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    sharing_opportunities: List[EquipmentSharingOpportunity] = Field(..., description="Sharing opportunities")
    cost_benefit_analysis: Dict[str, Any] = Field(..., description="Cost-benefit analysis")
    operational_benefits: Dict[str, Any] = Field(..., description="Operational benefits")
    implementation_recommendations: List[str] = Field(..., description="Implementation recommendations")
    generated_at: datetime = Field(default_factory=datetime.utcnow)