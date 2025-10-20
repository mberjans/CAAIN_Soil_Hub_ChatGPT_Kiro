"""
Soil Health Integration Service

Comprehensive service for analyzing the impact of fertilizer choices on soil health,
including organic matter, pH effects, microbial activity, and soil structure.
Implements TICKET-023_fertilizer-type-selection-7.1
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import math

try:
    from ..models.agricultural_models import SoilTestData
    from .soil_ph_management_service import SoilPHManagementService, SoilTexture, PHAnalysis
except ImportError:
    from models.agricultural_models import SoilTestData
    from services.soil_ph_management_service import SoilPHManagementService, SoilTexture, PHAnalysis

logger = logging.getLogger(__name__)


class TimeHorizon(Enum):
    """Time horizons for soil health impact analysis."""
    SHORT_TERM = "short_term"  # 0-1 year
    MEDIUM_TERM = "medium_term"  # 1-5 years
    LONG_TERM = "long_term"  # 5+ years


class SoilHealthRating(Enum):
    """Soil health impact ratings."""
    EXCELLENT = "excellent"  # Major positive impact
    GOOD = "good"  # Moderate positive impact
    NEUTRAL = "neutral"  # Minimal impact
    CONCERNING = "concerning"  # Some negative impact
    POOR = "poor"  # Significant negative impact


@dataclass
class OrganicMatterImpact:
    """Impact assessment for soil organic matter."""
    fertilizer_type: str
    fertilizer_name: str

    # Direct organic matter contribution
    organic_matter_contribution_percent: float  # % OM added per application
    carbon_input_lbs_per_acre: float  # Total carbon added
    decomposition_rate_per_year: float  # % of applied OM that decomposes per year

    # Long-term trends
    short_term_om_change_percent: float  # Change in 0-1 year
    medium_term_om_change_percent: float  # Change in 1-5 years
    long_term_om_change_percent: float  # Change in 5+ years
    equilibrium_om_level_percent: float  # Expected stabilization point

    # Impact ratings
    short_term_rating: SoilHealthRating
    long_term_rating: SoilHealthRating

    # Mechanisms
    impact_mechanisms: List[str]  # How fertilizer affects OM
    carbon_sequestration_potential: str  # low, medium, high

    # Recommendations
    recommendations: List[str]
    monitoring_frequency: str  # How often to test OM


@dataclass
class PHEffectsAnalysis:
    """pH effects analysis for fertilizer application."""
    fertilizer_type: str
    fertilizer_name: str
    application_rate_lbs_per_acre: float

    # pH impact
    immediate_ph_change: float  # pH units, first year
    cumulative_ph_change_5yr: float  # pH units after 5 years
    acidification_potential: str  # none, low, medium, high, very_high
    alkalinization_potential: str  # none, low, medium, high

    # Buffering interactions
    soil_buffer_capacity: float  # meq/100g
    buffering_adequacy: str  # adequate, marginal, inadequate

    # Nutrient availability impact
    nutrient_availability_effects: Dict[str, float]  # Nutrient -> availability change

    # Management strategies
    ph_monitoring_frequency: str
    remediation_strategies: List[str]
    preventive_measures: List[str]

    # Risk assessment
    ph_risk_level: str  # low, medium, high
    requires_ph_management: bool
    ph_adjustment_recommendations: List[str]


@dataclass
class MicrobialActivityAssessment:
    """Assessment of fertilizer impact on soil microbial activity."""
    fertilizer_type: str
    fertilizer_name: str

    # Microbial population effects
    bacterial_population_impact: str  # increase, neutral, decrease
    fungal_population_impact: str  # increase, neutral, decrease
    actinomycete_impact: str  # increase, neutral, decrease

    # Functional impacts
    nitrogen_cycling_impact: float  # -1 to 1 scale (negative to positive)
    phosphorus_solubilization_impact: float
    carbon_cycling_impact: float
    disease_suppression_impact: float

    # Beneficial organisms
    mycorrhizal_impact: str  # positive, neutral, negative
    nitrogen_fixing_bacteria_impact: str
    decomposer_community_impact: str

    # Diversity metrics
    microbial_diversity_score: float  # 0-10 scale
    soil_food_web_health: str  # poor, fair, good, excellent

    # Time-dependent effects
    short_term_microbiome_impact: SoilHealthRating
    long_term_microbiome_impact: SoilHealthRating
    recovery_time_months: int  # Time for microbiome to recover from negative impacts

    # Management recommendations
    microbiome_management_strategies: List[str]
    beneficial_organism_support: List[str]


@dataclass
class SoilStructureEvaluation:
    """Evaluation of fertilizer impact on soil physical structure."""
    fertilizer_type: str
    fertilizer_name: str

    # Aggregation effects
    aggregate_stability_impact: str  # improvement, neutral, degradation
    macro_aggregate_formation: float  # Change in % macro-aggregates
    micro_aggregate_formation: float  # Change in % micro-aggregates

    # Physical properties
    bulk_density_change: float  # g/cm³ change
    porosity_change_percent: float  # Change in total porosity
    infiltration_rate_change: float  # Change in inches/hour
    water_holding_capacity_change: float  # Change in inches/foot

    # Compaction risk
    compaction_risk: str  # low, medium, high
    crusting_tendency: str  # low, medium, high
    structural_stability: str  # poor, fair, good, excellent

    # Erosion impacts
    erosion_resistance_change: str  # increased, neutral, decreased
    aggregate_protection: float  # 0-1 scale

    # Drainage and aeration
    drainage_impact: str  # improved, neutral, impaired
    aeration_impact: str  # improved, neutral, impaired
    root_penetration_impact: str  # improved, neutral, impaired

    # Long-term structure
    long_term_structure_rating: SoilHealthRating

    # Management recommendations
    structure_management_practices: List[str]
    amelioration_strategies: List[str]


@dataclass
class TemporalImpactAnalysis:
    """Time-based analysis of soil health impacts."""
    fertilizer_type: str
    fertilizer_name: str

    # Short-term effects (0-1 year)
    short_term_impacts: Dict[str, Any]
    short_term_overall_rating: SoilHealthRating
    short_term_concerns: List[str]
    short_term_benefits: List[str]

    # Medium-term effects (1-5 years)
    medium_term_impacts: Dict[str, Any]
    medium_term_overall_rating: SoilHealthRating
    medium_term_trajectory: str  # improving, stable, declining

    # Long-term effects (5+ years)
    long_term_impacts: Dict[str, Any]
    long_term_overall_rating: SoilHealthRating
    long_term_sustainability: str  # sustainable, marginal, unsustainable

    # Cumulative effects
    cumulative_impact_score: float  # 0-100 scale
    cumulative_risks: List[str]
    cumulative_benefits: List[str]

    # Reversibility
    impact_reversibility: str  # easily_reversible, partially_reversible, irreversible
    recovery_timeline_years: Optional[float]

    # Recommendations by timeframe
    immediate_actions: List[str]
    medium_term_management: List[str]
    long_term_strategies: List[str]


@dataclass
class RemediationStrategy:
    """Strategy for remediating soil health issues."""
    strategy_id: str
    strategy_name: str
    strategy_type: str  # preventive, corrective, restorative

    # Issue addressed
    target_issue: str
    severity_addressed: str  # minor, moderate, major

    # Implementation details
    implementation_steps: List[str]
    timeline_months: int
    cost_per_acre: float
    labor_requirement: str  # low, medium, high
    equipment_needed: List[str]

    # Effectiveness
    expected_improvement_percent: float
    confidence_level: float  # 0-1
    success_factors: List[str]
    risk_factors: List[str]

    # Monitoring
    monitoring_parameters: List[str]
    evaluation_timeline: str
    success_indicators: List[str]

    # Alternatives
    alternative_approaches: List[str]
    complementary_practices: List[str]


@dataclass
class SoilHealthImpactAssessment:
    """Comprehensive soil health impact assessment."""
    assessment_id: str
    fertilizer_type: str
    fertilizer_name: str
    assessment_date: datetime

    # Component assessments
    organic_matter_impact: OrganicMatterImpact
    ph_effects: PHEffectsAnalysis
    microbial_assessment: MicrobialActivityAssessment
    structure_evaluation: SoilStructureEvaluation
    temporal_analysis: TemporalImpactAnalysis

    # Overall soil health scores
    overall_soil_health_score: float  # 0-100
    soil_health_rating: SoilHealthRating

    # Integrated analysis
    positive_impacts: List[str]
    negative_impacts: List[str]
    neutral_aspects: List[str]

    # Risk assessment
    overall_risk_level: str  # low, medium, high, critical
    critical_concerns: List[str]
    mitigation_priorities: List[str]

    # Remediation strategies
    recommended_remediation: List[RemediationStrategy]
    preventive_practices: List[str]

    # Monitoring plan
    monitoring_frequency: str
    key_indicators_to_monitor: List[str]
    alert_thresholds: Dict[str, float]

    # Comparison with alternatives
    relative_soil_health_rank: Optional[int]  # Rank among alternatives
    better_alternatives: List[str]  # Fertilizers with better soil health profile

    # Confidence and limitations
    assessment_confidence: float  # 0-1
    data_quality_notes: List[str]
    limitations: List[str]


class SoilHealthIntegrationService:
    """
    Comprehensive service for integrating soil health considerations into fertilizer selection.

    This service analyzes the impact of different fertilizer types on various soil health
    factors including organic matter, pH, microbial activity, and soil structure. It provides
    both short-term and long-term impact assessments and generates remediation strategies
    for maintaining optimal soil health.
    """

    def __init__(self):
        """Initialize the soil health integration service."""
        self.logger = logging.getLogger(__name__)
        self.ph_service = SoilPHManagementService()

        # Initialize databases
        self.fertilizer_soil_health_database = self._initialize_fertilizer_soil_health_database()
        self.organic_matter_dynamics = self._initialize_organic_matter_dynamics()
        self.microbial_impact_database = self._initialize_microbial_impact_database()
        self.structure_impact_database = self._initialize_structure_impact_database()

        self.logger.info("SoilHealthIntegrationService initialized successfully")

    def _initialize_fertilizer_soil_health_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize database of fertilizer impacts on soil health.

        Returns:
            Dictionary mapping fertilizer types to their soil health characteristics
        """
        return {
            'organic_compost': {
                'organic_matter_contribution': 0.15,  # % OM per ton per acre
                'carbon_input': 400.0,  # lbs C per ton
                'acidifying_effect': 0.0,  # pH units per ton
                'microbial_stimulation': 'high',
                'structure_improvement': 'excellent',
                'nutrient_release_pattern': 'slow',
                'cec_contribution': 2.5,  # meq/100g per % OM
                'water_retention_improvement': 0.05  # inch/inch OM
            },
            'synthetic_urea': {
                'organic_matter_contribution': 0.0,
                'carbon_input': 0.0,
                'acidifying_effect': -0.15,  # pH units per 100 lbs N
                'microbial_stimulation': 'low',
                'structure_improvement': 'none',
                'nutrient_release_pattern': 'fast',
                'salt_index': 75,
                'volatilization_risk': 'high'
            },
            'synthetic_ammonium_sulfate': {
                'organic_matter_contribution': 0.0,
                'carbon_input': 0.0,
                'acidifying_effect': -0.22,  # pH units per 100 lbs N
                'microbial_stimulation': 'neutral',
                'structure_improvement': 'slight',  # Sulfur benefit
                'nutrient_release_pattern': 'fast',
                'salt_index': 69,
                'sulfur_benefit': True
            },
            'synthetic_anhydrous_ammonia': {
                'organic_matter_contribution': 0.0,
                'carbon_input': 0.0,
                'acidifying_effect': -0.18,  # pH units per 100 lbs N
                'microbial_stimulation': 'low',
                'structure_improvement': 'none',
                'nutrient_release_pattern': 'fast',
                'salt_index': 47,
                'ammonia_toxicity_risk': 'temporary'
            },
            'organic_manure': {
                'organic_matter_contribution': 0.08,  # % OM per ton per acre
                'carbon_input': 250.0,  # lbs C per ton
                'acidifying_effect': 0.02,  # Slight alkalizing
                'microbial_stimulation': 'very_high',
                'structure_improvement': 'excellent',
                'nutrient_release_pattern': 'slow',
                'nutrient_variability': 'high',
                'pathogen_risk': 'moderate'
            },
            'slow_release_coated_urea': {
                'organic_matter_contribution': 0.0,
                'carbon_input': 0.0,
                'acidifying_effect': -0.10,  # pH units per 100 lbs N, reduced
                'microbial_stimulation': 'low',
                'structure_improvement': 'none',
                'nutrient_release_pattern': 'controlled',
                'salt_index': 40,
                'coating_residue': True
            },
            'organic_bone_meal': {
                'organic_matter_contribution': 0.05,
                'carbon_input': 150.0,
                'acidifying_effect': 0.05,  # Slight alkalizing
                'microbial_stimulation': 'moderate',
                'structure_improvement': 'moderate',
                'nutrient_release_pattern': 'slow',
                'phosphorus_source': 'excellent',
                'calcium_benefit': True
            },
            'synthetic_map': {  # Monoammonium phosphate
                'organic_matter_contribution': 0.0,
                'carbon_input': 0.0,
                'acidifying_effect': -0.18,  # pH units per 100 lbs
                'microbial_stimulation': 'low',
                'structure_improvement': 'none',
                'nutrient_release_pattern': 'fast',
                'salt_index': 30,
                'phosphorus_efficiency': 'high'
            },
            'organic_fish_emulsion': {
                'organic_matter_contribution': 0.03,
                'carbon_input': 100.0,
                'acidifying_effect': 0.0,
                'microbial_stimulation': 'high',
                'structure_improvement': 'moderate',
                'nutrient_release_pattern': 'medium',
                'trace_element_benefit': True,
                'odor_concern': True
            },
            'synthetic_potash': {  # Muriate of potash
                'organic_matter_contribution': 0.0,
                'carbon_input': 0.0,
                'acidifying_effect': 0.0,
                'microbial_stimulation': 'neutral',
                'structure_improvement': 'none',
                'nutrient_release_pattern': 'fast',
                'salt_index': 116,
                'chloride_content': 'high'
            }
        }

    def _initialize_organic_matter_dynamics(self) -> Dict[str, Any]:
        """
        Initialize organic matter decomposition and accumulation dynamics.

        Returns:
            Dictionary with OM dynamics parameters
        """
        return {
            'decomposition_rates': {
                'fresh_plant_residue': 0.6,  # 60% decomposition per year
                'animal_manure': 0.5,
                'compost': 0.3,
                'slow_release_organic': 0.25,
                'stabilized_humus': 0.05
            },
            'carbon_to_om_ratio': 1.72,  # OM = C × 1.72
            'cn_ratio_targets': {
                'fast_decomposition': 20,
                'moderate_decomposition': 30,
                'slow_decomposition': 50
            },
            'accumulation_efficiency': {
                'high_clay': 0.25,  # 25% of applied C becomes stable OM
                'medium_texture': 0.20,
                'sandy': 0.15
            },
            'baseline_om_loss': {
                'intensive_tillage': 0.03,  # 3% OM loss per year
                'reduced_tillage': 0.015,
                'no_till': 0.005
            }
        }

    def _initialize_microbial_impact_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize database of fertilizer impacts on soil microbiome.

        Returns:
            Dictionary of microbial impact parameters
        """
        return {
            'organic_compost': {
                'bacterial_growth': 'stimulated',
                'fungal_growth': 'stimulated',
                'diversity_impact': 1.5,  # Multiplier
                'mycorrhizal_impact': 'positive',
                'nitrogen_fixers': 'enhanced',
                'decomposers': 'enhanced',
                'disease_suppressors': 'enhanced'
            },
            'synthetic_urea': {
                'bacterial_growth': 'temporary_boost',
                'fungal_growth': 'suppressed',
                'diversity_impact': 0.8,
                'mycorrhizal_impact': 'negative',
                'nitrogen_fixers': 'suppressed',
                'decomposers': 'neutral',
                'disease_suppressors': 'reduced'
            },
            'synthetic_ammonium_sulfate': {
                'bacterial_growth': 'temporary_boost',
                'fungal_growth': 'suppressed',
                'diversity_impact': 0.75,
                'mycorrhizal_impact': 'negative',
                'nitrogen_fixers': 'suppressed',
                'decomposers': 'neutral',
                'disease_suppressors': 'reduced'
            },
            'organic_manure': {
                'bacterial_growth': 'strongly_stimulated',
                'fungal_growth': 'stimulated',
                'diversity_impact': 1.6,
                'mycorrhizal_impact': 'positive',
                'nitrogen_fixers': 'enhanced',
                'decomposers': 'strongly_enhanced',
                'disease_suppressors': 'enhanced'
            },
            'slow_release_coated_urea': {
                'bacterial_growth': 'moderate_boost',
                'fungal_growth': 'slightly_suppressed',
                'diversity_impact': 0.9,
                'mycorrhizal_impact': 'slight_negative',
                'nitrogen_fixers': 'slightly_suppressed',
                'decomposers': 'neutral',
                'disease_suppressors': 'slightly_reduced'
            }
        }

    def _initialize_structure_impact_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize database of fertilizer impacts on soil structure.

        Returns:
            Dictionary of structure impact parameters
        """
        return {
            'organic_compost': {
                'aggregate_stability': 0.15,  # Improvement factor
                'bulk_density_change': -0.08,  # g/cm³
                'infiltration_improvement': 0.25,  # inches/hour
                'water_holding_increase': 0.15,  # inches/foot
                'compaction_resistance': 'high',
                'crusting_reduction': 'significant'
            },
            'synthetic_urea': {
                'aggregate_stability': -0.02,  # Slight deterioration
                'bulk_density_change': 0.0,
                'infiltration_improvement': 0.0,
                'water_holding_increase': 0.0,
                'compaction_resistance': 'none',
                'crusting_reduction': 'none',
                'salt_damage_risk': 'moderate'
            },
            'synthetic_ammonium_sulfate': {
                'aggregate_stability': 0.02,  # Slight improvement from S
                'bulk_density_change': 0.0,
                'infiltration_improvement': 0.03,
                'water_holding_increase': 0.0,
                'compaction_resistance': 'none',
                'crusting_reduction': 'minimal',
                'calcium_displacement_risk': 'moderate'
            },
            'organic_manure': {
                'aggregate_stability': 0.12,
                'bulk_density_change': -0.06,
                'infiltration_improvement': 0.20,
                'water_holding_increase': 0.12,
                'compaction_resistance': 'high',
                'crusting_reduction': 'significant'
            },
            'slow_release_coated_urea': {
                'aggregate_stability': -0.01,
                'bulk_density_change': 0.0,
                'infiltration_improvement': 0.0,
                'water_holding_increase': 0.0,
                'compaction_resistance': 'none',
                'crusting_reduction': 'none',
                'coating_residue_concern': 'minor'
            }
        }

    async def assess_soil_health_impact(
        self,
        fertilizer_type: str,
        fertilizer_name: str,
        application_rate_lbs_per_acre: float,
        soil_data: SoilTestData,
        application_frequency_per_year: int = 1,
        soil_texture: Optional[SoilTexture] = None,
        field_conditions: Optional[Dict[str, Any]] = None
    ) -> SoilHealthImpactAssessment:
        """
        Assess comprehensive soil health impact of a fertilizer.

        This is the main entry point for soil health impact analysis. It coordinates
        all component analyses and generates an integrated assessment.

        Args:
            fertilizer_type: Type of fertilizer (organic, synthetic, etc.)
            fertilizer_name: Specific fertilizer name
            application_rate_lbs_per_acre: Application rate in lbs/acre
            soil_data: Current soil test data
            application_frequency_per_year: Number of applications per year
            soil_texture: Soil texture classification
            field_conditions: Additional field conditions

        Returns:
            Comprehensive soil health impact assessment

        Performance Target: <0.2s for complete analysis
        """
        start_time = datetime.now()
        self.logger.info(
            f"Starting soil health impact assessment for {fertilizer_name} "
            f"at {application_rate_lbs_per_acre} lbs/acre"
        )

        try:
            # Normalize fertilizer type key
            fert_key = self._normalize_fertilizer_key(fertilizer_type, fertilizer_name)

            # Run component analyses in parallel for performance
            om_impact_task = self._analyze_organic_matter_impact(
                fert_key, fertilizer_name, application_rate_lbs_per_acre,
                soil_data, application_frequency_per_year, soil_texture
            )

            ph_effects_task = self._analyze_ph_effects(
                fert_key, fertilizer_name, application_rate_lbs_per_acre,
                soil_data, application_frequency_per_year, soil_texture
            )

            microbial_assessment_task = self._assess_microbial_activity(
                fert_key, fertilizer_name, application_rate_lbs_per_acre,
                soil_data, application_frequency_per_year
            )

            structure_eval_task = self._evaluate_soil_structure(
                fert_key, fertilizer_name, application_rate_lbs_per_acre,
                soil_data, application_frequency_per_year, soil_texture
            )

            # Await all analyses
            om_impact, ph_effects, microbial_assessment, structure_eval = await asyncio.gather(
                om_impact_task,
                ph_effects_task,
                microbial_assessment_task,
                structure_eval_task
            )

            # Perform temporal analysis
            temporal_analysis = await self._perform_temporal_analysis(
                fert_key, fertilizer_name,
                om_impact, ph_effects, microbial_assessment, structure_eval
            )

            # Calculate overall soil health score
            overall_score = self._calculate_overall_soil_health_score(
                om_impact, ph_effects, microbial_assessment, structure_eval
            )

            # Determine soil health rating
            soil_health_rating = self._determine_soil_health_rating(overall_score)

            # Identify impacts
            positive_impacts = self._identify_positive_impacts(
                om_impact, ph_effects, microbial_assessment, structure_eval
            )
            negative_impacts = self._identify_negative_impacts(
                om_impact, ph_effects, microbial_assessment, structure_eval
            )
            neutral_aspects = self._identify_neutral_aspects(
                om_impact, ph_effects, microbial_assessment, structure_eval
            )

            # Risk assessment
            risk_level, critical_concerns, mitigation_priorities = self._assess_risks(
                om_impact, ph_effects, microbial_assessment, structure_eval, temporal_analysis
            )

            # Generate remediation strategies
            remediation_strategies = await self._generate_remediation_strategies(
                fertilizer_name, negative_impacts, critical_concerns,
                soil_data, soil_texture
            )

            # Preventive practices
            preventive_practices = self._generate_preventive_practices(
                fert_key, fertilizer_name, risk_level
            )

            # Monitoring plan
            monitoring_frequency = self._determine_monitoring_frequency(risk_level, temporal_analysis)
            key_indicators = self._identify_key_monitoring_indicators(
                om_impact, ph_effects, microbial_assessment, structure_eval
            )
            alert_thresholds = self._define_alert_thresholds(soil_data, risk_level)

            # Assessment confidence
            confidence = self._calculate_assessment_confidence(
                fert_key, soil_data, field_conditions
            )

            # Data quality notes and limitations
            data_quality_notes = self._generate_data_quality_notes(soil_data, field_conditions)
            limitations = self._identify_assessment_limitations(fert_key, soil_data)

            # Create assessment ID
            assessment_id = f"soil_health_{fertilizer_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Create comprehensive assessment
            assessment = SoilHealthImpactAssessment(
                assessment_id=assessment_id,
                fertilizer_type=fertilizer_type,
                fertilizer_name=fertilizer_name,
                assessment_date=datetime.now(),
                organic_matter_impact=om_impact,
                ph_effects=ph_effects,
                microbial_assessment=microbial_assessment,
                structure_evaluation=structure_eval,
                temporal_analysis=temporal_analysis,
                overall_soil_health_score=overall_score,
                soil_health_rating=soil_health_rating,
                positive_impacts=positive_impacts,
                negative_impacts=negative_impacts,
                neutral_aspects=neutral_aspects,
                overall_risk_level=risk_level,
                critical_concerns=critical_concerns,
                mitigation_priorities=mitigation_priorities,
                recommended_remediation=remediation_strategies,
                preventive_practices=preventive_practices,
                monitoring_frequency=monitoring_frequency,
                key_indicators_to_monitor=key_indicators,
                alert_thresholds=alert_thresholds,
                relative_soil_health_rank=None,  # Set during comparison
                better_alternatives=[],  # Set during comparison
                assessment_confidence=confidence,
                data_quality_notes=data_quality_notes,
                limitations=limitations
            )

            # Calculate performance
            elapsed_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"Soil health impact assessment completed in {elapsed_time:.3f}s "
                f"(target: <0.2s). Score: {overall_score:.1f}/100, Rating: {soil_health_rating.value}"
            )

            if elapsed_time > 0.2:
                self.logger.warning(
                    f"Assessment exceeded performance target by {elapsed_time - 0.2:.3f}s"
                )

            return assessment

        except Exception as e:
            self.logger.error(f"Error in soil health impact assessment: {str(e)}")
            raise

    async def _analyze_organic_matter_impact(
        self,
        fert_key: str,
        fertilizer_name: str,
        application_rate: float,
        soil_data: SoilTestData,
        application_frequency: int,
        soil_texture: Optional[SoilTexture]
    ) -> OrganicMatterImpact:
        """
        Analyze impact on soil organic matter.

        Args:
            fert_key: Normalized fertilizer key
            fertilizer_name: Fertilizer name
            application_rate: Application rate in lbs/acre
            soil_data: Current soil test data
            application_frequency: Applications per year
            soil_texture: Soil texture

        Returns:
            Organic matter impact analysis
        """
        # Get fertilizer OM characteristics
        fert_data = self.fertilizer_soil_health_database.get(
            fert_key,
            self.fertilizer_soil_health_database['synthetic_urea']  # Default
        )

        # Calculate direct OM contribution
        om_contribution = fert_data['organic_matter_contribution']
        carbon_input = fert_data['carbon_input']

        # Annual OM addition
        annual_om_addition = (om_contribution * application_rate * application_frequency) / 2000.0  # Convert to tons
        annual_carbon = (carbon_input * application_rate * application_frequency) / 2000.0

        # Get decomposition rate
        if 'compost' in fert_key:
            decomp_rate = self.organic_matter_dynamics['decomposition_rates']['compost']
        elif 'manure' in fert_key:
            decomp_rate = self.organic_matter_dynamics['decomposition_rates']['animal_manure']
        else:
            decomp_rate = self.organic_matter_dynamics['decomposition_rates']['fast_decomposition']

        # Calculate time-based OM changes
        current_om = soil_data.organic_matter_percent

        # Short-term (1 year): Net change accounting for decomposition
        short_term_change = annual_om_addition * (1 - decomp_rate * 0.5)  # Half-year decomp

        # Medium-term (1-5 years): Cumulative with ongoing decomposition
        medium_term_change = self._calculate_cumulative_om_change(
            annual_om_addition, decomp_rate, years=5
        )

        # Long-term (5+ years): Approach equilibrium
        long_term_change = self._calculate_equilibrium_om_change(
            annual_om_addition, decomp_rate, years=15
        )

        # Equilibrium OM level
        equilibrium_om = self._calculate_equilibrium_om(
            current_om, annual_om_addition, decomp_rate
        )

        # Impact ratings
        short_term_rating = self._rate_om_impact(short_term_change, TimeHorizon.SHORT_TERM)
        long_term_rating = self._rate_om_impact(long_term_change, TimeHorizon.LONG_TERM)

        # Impact mechanisms
        mechanisms = self._identify_om_impact_mechanisms(fert_key, fert_data)

        # Carbon sequestration potential
        if annual_carbon > 200:
            carbon_seq = 'high'
        elif annual_carbon > 50:
            carbon_seq = 'medium'
        else:
            carbon_seq = 'low'

        # Recommendations
        recommendations = self._generate_om_recommendations(
            fert_key, current_om, short_term_change, long_term_change
        )

        # Monitoring frequency
        if om_contribution > 0.1:
            monitoring_freq = 'annually'
        elif om_contribution > 0:
            monitoring_freq = 'every 2-3 years'
        else:
            monitoring_freq = 'every 3-4 years'

        return OrganicMatterImpact(
            fertilizer_type=fert_key,
            fertilizer_name=fertilizer_name,
            organic_matter_contribution_percent=om_contribution,
            carbon_input_lbs_per_acre=carbon_input,
            decomposition_rate_per_year=decomp_rate,
            short_term_om_change_percent=short_term_change,
            medium_term_om_change_percent=medium_term_change,
            long_term_om_change_percent=long_term_change,
            equilibrium_om_level_percent=equilibrium_om,
            short_term_rating=short_term_rating,
            long_term_rating=long_term_rating,
            impact_mechanisms=mechanisms,
            carbon_sequestration_potential=carbon_seq,
            recommendations=recommendations,
            monitoring_frequency=monitoring_freq
        )

    def _calculate_cumulative_om_change(
        self,
        annual_addition: float,
        decomp_rate: float,
        years: int
    ) -> float:
        """
        Calculate cumulative OM change over multiple years.

        Args:
            annual_addition: Annual OM addition (%)
            decomp_rate: Decomposition rate (fraction per year)
            years: Number of years

        Returns:
            Cumulative OM change (%)
        """
        cumulative = 0.0
        for year in range(years):
            # Add new OM
            cumulative += annual_addition
            # Apply decomposition to all accumulated OM
            cumulative *= (1 - decomp_rate)

        return cumulative

    def _calculate_equilibrium_om_change(
        self,
        annual_addition: float,
        decomp_rate: float,
        years: int = 15
    ) -> float:
        """Calculate OM change approaching equilibrium."""
        return self._calculate_cumulative_om_change(annual_addition, decomp_rate, years)

    def _calculate_equilibrium_om(
        self,
        current_om: float,
        annual_addition: float,
        decomp_rate: float
    ) -> float:
        """
        Calculate equilibrium OM level.

        At equilibrium: annual addition = annual decomposition
        """
        if decomp_rate > 0:
            equilibrium_addition = annual_addition / decomp_rate
            return current_om + equilibrium_addition
        return current_om

    def _rate_om_impact(self, om_change: float, horizon: TimeHorizon) -> SoilHealthRating:
        """
        Rate the organic matter impact.

        Args:
            om_change: Change in OM (%)
            horizon: Time horizon

        Returns:
            Soil health rating
        """
        if horizon == TimeHorizon.SHORT_TERM:
            if om_change > 0.15:
                return SoilHealthRating.EXCELLENT
            elif om_change > 0.08:
                return SoilHealthRating.GOOD
            elif om_change > 0:
                return SoilHealthRating.NEUTRAL
            elif om_change > -0.05:
                return SoilHealthRating.NEUTRAL
            else:
                return SoilHealthRating.CONCERNING
        else:  # LONG_TERM
            if om_change > 0.5:
                return SoilHealthRating.EXCELLENT
            elif om_change > 0.25:
                return SoilHealthRating.GOOD
            elif om_change > 0:
                return SoilHealthRating.NEUTRAL
            elif om_change > -0.2:
                return SoilHealthRating.CONCERNING
            else:
                return SoilHealthRating.POOR

    def _identify_om_impact_mechanisms(
        self,
        fert_key: str,
        fert_data: Dict[str, Any]
    ) -> List[str]:
        """Identify mechanisms by which fertilizer affects OM."""
        mechanisms = []

        if fert_data['organic_matter_contribution'] > 0:
            mechanisms.append("Direct organic matter addition")
            mechanisms.append("Carbon input for microbial food source")

        if fert_data.get('microbial_stimulation') in ['high', 'very_high']:
            mechanisms.append("Enhanced microbial decomposition and transformation")
            mechanisms.append("Improved nutrient cycling through biological activity")

        if fert_data.get('structure_improvement') in ['excellent', 'moderate']:
            mechanisms.append("Physical protection of organic matter in aggregates")

        if fert_data.get('acidifying_effect', 0) < -0.1:
            mechanisms.append("Potential OM mineralization from pH changes")

        if fert_data['organic_matter_contribution'] == 0:
            mechanisms.append("No direct OM contribution - relies on crop residue return")

        return mechanisms

    def _generate_om_recommendations(
        self,
        fert_key: str,
        current_om: float,
        short_term_change: float,
        long_term_change: float
    ) -> List[str]:
        """Generate OM-specific recommendations."""
        recommendations = []

        # Current OM status
        if current_om < 2.0:
            recommendations.append(
                "Current OM is low. Prioritize OM-building fertilizers and practices"
            )

        # Short-term impact
        if short_term_change <= 0:
            recommendations.append(
                "This fertilizer does not add OM. Supplement with cover crops or compost"
            )
        elif short_term_change < 0.05:
            recommendations.append(
                "Modest OM addition. Consider combining with other OM sources"
            )

        # Long-term trajectory
        if long_term_change > 0.5:
            recommendations.append(
                "Excellent long-term OM building potential. Continue consistent application"
            )
        elif long_term_change > 0:
            recommendations.append(
                "Moderate OM building over time. Supplement with conservation tillage"
            )
        else:
            recommendations.append(
                "No OM building. Implement cover crops and residue management"
            )

        # Specific to organic vs synthetic
        if 'organic' in fert_key:
            recommendations.append(
                "Maximize OM benefits by incorporating into soil promptly"
            )
        else:
            recommendations.append(
                "Synthetic fertilizer - combine with organic amendments for soil health"
            )

        return recommendations

    async def _analyze_ph_effects(
        self,
        fert_key: str,
        fertilizer_name: str,
        application_rate: float,
        soil_data: SoilTestData,
        application_frequency: int,
        soil_texture: Optional[SoilTexture]
    ) -> PHEffectsAnalysis:
        """
        Analyze pH effects of fertilizer application.

        Integrates with existing pH management service for comprehensive analysis.
        """
        fert_data = self.fertilizer_soil_health_database.get(
            fert_key,
            self.fertilizer_soil_health_database['synthetic_urea']
        )

        # Get acidifying/alkalizing effect
        acidifying_effect = fert_data.get('acidifying_effect', 0.0)

        # Calculate pH changes
        # Immediate (1 year)
        if 'nitrogen_ppm' in fert_data or 'urea' in fert_key or 'ammonium' in fert_key:
            # Nitrogen fertilizers: effect per 100 lbs N
            n_rate = application_rate * 0.46 if 'urea' in fert_key else application_rate * 0.21
            immediate_ph_change = acidifying_effect * (n_rate / 100.0) * application_frequency
        else:
            # Other fertilizers: effect per ton
            immediate_ph_change = acidifying_effect * (application_rate / 2000.0) * application_frequency

        # Cumulative (5 years)
        cumulative_ph_change = immediate_ph_change * 5 * 0.85  # 85% of annual due to buffering

        # Acidification potential
        if cumulative_ph_change < -0.8:
            acidification_potential = 'very_high'
        elif cumulative_ph_change < -0.5:
            acidification_potential = 'high'
        elif cumulative_ph_change < -0.2:
            acidification_potential = 'medium'
        elif cumulative_ph_change < -0.05:
            acidification_potential = 'low'
        else:
            acidification_potential = 'none'

        # Alkalinization potential
        if cumulative_ph_change > 0.3:
            alkalinization_potential = 'high'
        elif cumulative_ph_change > 0.1:
            alkalinization_potential = 'medium'
        elif cumulative_ph_change > 0.05:
            alkalinization_potential = 'low'
        else:
            alkalinization_potential = 'none'

        # Soil buffering
        if soil_texture:
            buffer_factors = self.ph_service.buffer_capacity_factors.get(
                soil_texture,
                self.ph_service.buffer_capacity_factors[SoilTexture.LOAM]
            )
            buffer_capacity = buffer_factors['base_buffer_capacity']
        else:
            buffer_capacity = 6.0  # Default for loam

        # Adjust pH change based on buffering
        immediate_ph_change *= (6.0 / buffer_capacity)  # Normalize to loam baseline
        cumulative_ph_change *= (6.0 / buffer_capacity)

        # Buffering adequacy
        if buffer_capacity > 8:
            buffering_adequacy = 'adequate'
        elif buffer_capacity > 5:
            buffering_adequacy = 'marginal'
        else:
            buffering_adequacy = 'inadequate'

        # Nutrient availability effects (from pH service)
        projected_ph = soil_data.ph + cumulative_ph_change
        nutrient_availability_before = self.ph_service._assess_nutrient_availability(soil_data.ph)
        nutrient_availability_after = self.ph_service._assess_nutrient_availability(projected_ph)

        nutrient_availability_effects = {
            nutrient: availability_after - nutrient_availability_before[nutrient]
            for nutrient, availability_after in nutrient_availability_after.items()
        }

        # pH monitoring frequency
        if abs(cumulative_ph_change) > 0.5:
            ph_monitoring_freq = 'annually'
        elif abs(cumulative_ph_change) > 0.2:
            ph_monitoring_freq = 'every 2 years'
        else:
            ph_monitoring_freq = 'every 3-4 years'

        # Remediation strategies
        remediation_strategies = []
        if acidification_potential in ['high', 'very_high']:
            remediation_strategies.append(
                f"Apply lime at {abs(cumulative_ph_change) * 2:.1f} tons/acre every 3-4 years"
            )
            remediation_strategies.append("Consider using less acidifying fertilizer alternatives")
            remediation_strategies.append("Increase organic matter to improve buffering capacity")
        elif alkalinization_potential == 'high':
            remediation_strategies.append("Apply elemental sulfur if pH exceeds 7.5")
            remediation_strategies.append("Use acidifying fertilizers to balance pH")

        # Preventive measures
        preventive_measures = []
        if acidification_potential != 'none':
            preventive_measures.append("Test pH annually to catch acidification early")
            preventive_measures.append("Apply maintenance lime based on soil test recommendations")
            preventive_measures.append("Build soil organic matter to increase buffering")

        # Risk assessment
        if acidification_potential in ['high', 'very_high']:
            ph_risk_level = 'high'
            requires_ph_management = True
        elif acidification_potential == 'medium':
            ph_risk_level = 'medium'
            requires_ph_management = True
        else:
            ph_risk_level = 'low'
            requires_ph_management = False

        # pH adjustment recommendations
        ph_adjustment_recs = []
        if requires_ph_management:
            current_ph = soil_data.ph
            if current_ph < 6.0 and acidification_potential != 'none':
                ph_adjustment_recs.append(
                    f"URGENT: Current pH {current_ph:.1f} is already low. "
                    f"Apply lime immediately before using this fertilizer"
                )
            elif current_ph < 6.5 and acidification_potential in ['high', 'very_high']:
                ph_adjustment_recs.append(
                    f"Current pH {current_ph:.1f} requires lime application "
                    f"to prevent future acidification issues"
                )

        return PHEffectsAnalysis(
            fertilizer_type=fert_key,
            fertilizer_name=fertilizer_name,
            application_rate_lbs_per_acre=application_rate,
            immediate_ph_change=immediate_ph_change,
            cumulative_ph_change_5yr=cumulative_ph_change,
            acidification_potential=acidification_potential,
            alkalinization_potential=alkalinization_potential,
            soil_buffer_capacity=buffer_capacity,
            buffering_adequacy=buffering_adequacy,
            nutrient_availability_effects=nutrient_availability_effects,
            ph_monitoring_frequency=ph_monitoring_freq,
            remediation_strategies=remediation_strategies,
            preventive_measures=preventive_measures,
            ph_risk_level=ph_risk_level,
            requires_ph_management=requires_ph_management,
            ph_adjustment_recommendations=ph_adjustment_recs
        )

    async def _assess_microbial_activity(
        self,
        fert_key: str,
        fertilizer_name: str,
        application_rate: float,
        soil_data: SoilTestData,
        application_frequency: int
    ) -> MicrobialActivityAssessment:
        """Assess impact on soil microbial activity."""
        microbe_data = self.microbial_impact_database.get(
            fert_key,
            self.microbial_impact_database['synthetic_urea']
        )

        # Population impacts
        bacterial_impact = microbe_data['bacterial_growth']
        fungal_impact = microbe_data['fungal_growth']
        actinomycete_impact = 'neutral'  # Default

        # Functional impacts (normalized -1 to 1 scale)
        diversity_multiplier = microbe_data['diversity_impact']

        nitrogen_cycling = self._quantify_microbial_impact(bacterial_impact, diversity_multiplier)
        phosphorus_solubilization = self._quantify_microbial_impact(fungal_impact, diversity_multiplier)
        carbon_cycling = (nitrogen_cycling + phosphorus_solubilization) / 2
        disease_suppression = self._quantify_microbial_impact(
            microbe_data['disease_suppressors'], diversity_multiplier
        )

        # Beneficial organisms
        mycorrhizal_impact = microbe_data['mycorrhizal_impact']
        n_fixing_impact = microbe_data['nitrogen_fixers']
        decomposer_impact = microbe_data['decomposers']

        # Diversity score (0-10)
        base_diversity = 6.0
        diversity_score = base_diversity * diversity_multiplier
        diversity_score = max(0, min(10, diversity_score))

        # Soil food web health
        if diversity_score >= 8:
            food_web_health = 'excellent'
        elif diversity_score >= 6:
            food_web_health = 'good'
        elif diversity_score >= 4:
            food_web_health = 'fair'
        else:
            food_web_health = 'poor'

        # Time-dependent effects
        if diversity_multiplier >= 1.3:
            short_term_impact = SoilHealthRating.EXCELLENT
            long_term_impact = SoilHealthRating.EXCELLENT
            recovery_time = 0
        elif diversity_multiplier >= 1.0:
            short_term_impact = SoilHealthRating.GOOD
            long_term_impact = SoilHealthRating.GOOD
            recovery_time = 0
        elif diversity_multiplier >= 0.85:
            short_term_impact = SoilHealthRating.NEUTRAL
            long_term_impact = SoilHealthRating.NEUTRAL
            recovery_time = 3
        elif diversity_multiplier >= 0.7:
            short_term_impact = SoilHealthRating.CONCERNING
            long_term_impact = SoilHealthRating.CONCERNING
            recovery_time = 6
        else:
            short_term_impact = SoilHealthRating.POOR
            long_term_impact = SoilHealthRating.POOR
            recovery_time = 12

        # Management strategies
        strategies = []
        if diversity_multiplier < 1.0:
            strategies.append("Add compost or organic matter to support microbial diversity")
            strategies.append("Reduce fertilizer application rate if possible")
            strategies.append("Consider split applications to reduce shock to microbiome")

        if mycorrhizal_impact == 'negative':
            strategies.append("Avoid excessive fertilization to preserve mycorrhizal associations")
            strategies.append("Use mycorrhizal inoculants if establishing new crops")

        if n_fixing_impact in ['suppressed', 'reduced']:
            strategies.append("Reduce nitrogen rates in legume rotations")
            strategies.append("Allow time between applications for recovery")

        # Beneficial organism support
        beneficial_support = []
        beneficial_support.append("Maintain consistent organic matter inputs")
        beneficial_support.append("Minimize soil disturbance to protect fungal networks")
        beneficial_support.append("Use cover crops to provide food sources for beneficial microbes")

        if diversity_multiplier < 0.9:
            beneficial_support.append("Consider microbial inoculants to restore diversity")

        return MicrobialActivityAssessment(
            fertilizer_type=fert_key,
            fertilizer_name=fertilizer_name,
            bacterial_population_impact=bacterial_impact,
            fungal_population_impact=fungal_impact,
            actinomycete_impact=actinomycete_impact,
            nitrogen_cycling_impact=nitrogen_cycling,
            phosphorus_solubilization_impact=phosphorus_solubilization,
            carbon_cycling_impact=carbon_cycling,
            disease_suppression_impact=disease_suppression,
            mycorrhizal_impact=mycorrhizal_impact,
            nitrogen_fixing_bacteria_impact=n_fixing_impact,
            decomposer_community_impact=decomposer_impact,
            microbial_diversity_score=diversity_score,
            soil_food_web_health=food_web_health,
            short_term_microbiome_impact=short_term_impact,
            long_term_microbiome_impact=long_term_impact,
            recovery_time_months=recovery_time,
            microbiome_management_strategies=strategies,
            beneficial_organism_support=beneficial_support
        )

    def _quantify_microbial_impact(
        self,
        impact_description: str,
        diversity_multiplier: float
    ) -> float:
        """
        Quantify microbial impact from description.

        Args:
            impact_description: Qualitative description
            diversity_multiplier: Diversity impact multiplier

        Returns:
            Quantitative impact (-1 to 1)
        """
        impact_map = {
            'strongly_stimulated': 0.8,
            'stimulated': 0.6,
            'enhanced': 0.5,
            'strongly_enhanced': 0.7,
            'moderate_boost': 0.3,
            'temporary_boost': 0.2,
            'neutral': 0.0,
            'slightly_suppressed': -0.2,
            'suppressed': -0.4,
            'reduced': -0.3,
            'slightly_reduced': -0.2,
            'positive': 0.4,
            'slight_negative': -0.2,
            'negative': -0.4
        }

        base_impact = impact_map.get(impact_description, 0.0)

        # Adjust based on diversity
        adjusted_impact = base_impact * (diversity_multiplier / 1.0)

        return max(-1.0, min(1.0, adjusted_impact))

    async def _evaluate_soil_structure(
        self,
        fert_key: str,
        fertilizer_name: str,
        application_rate: float,
        soil_data: SoilTestData,
        application_frequency: int,
        soil_texture: Optional[SoilTexture]
    ) -> SoilStructureEvaluation:
        """Evaluate impact on soil structure."""
        structure_data = self.structure_impact_database.get(
            fert_key,
            self.structure_impact_database['synthetic_urea']
        )

        # Aggregation effects
        aggregate_improvement = structure_data['aggregate_stability']

        if aggregate_improvement > 0.1:
            aggregate_stability_impact = 'improvement'
            macro_agg_change = aggregate_improvement * 10  # Convert to %
            micro_agg_change = aggregate_improvement * 8
        elif aggregate_improvement < -0.01:
            aggregate_stability_impact = 'degradation'
            macro_agg_change = aggregate_improvement * 10
            micro_agg_change = aggregate_improvement * 8
        else:
            aggregate_stability_impact = 'neutral'
            macro_agg_change = 0.0
            micro_agg_change = 0.0

        # Physical properties
        bulk_density_change = structure_data['bulk_density_change']
        porosity_change = -bulk_density_change * 5  # Inverse relationship, rough estimate
        infiltration_change = structure_data['infiltration_improvement']
        water_holding_change = structure_data['water_holding_increase']

        # Compaction risk
        compaction_resistance = structure_data.get('compaction_resistance', 'none')
        if compaction_resistance in ['high', 'excellent']:
            compaction_risk = 'low'
        elif compaction_resistance == 'moderate':
            compaction_risk = 'medium'
        else:
            compaction_risk = 'medium'  # Default

        # Crusting tendency
        crusting_reduction = structure_data.get('crusting_reduction', 'none')
        if crusting_reduction in ['significant', 'excellent']:
            crusting_tendency = 'low'
        elif crusting_reduction == 'minimal':
            crusting_tendency = 'medium'
        else:
            crusting_tendency = 'medium'

        # Structural stability overall
        if aggregate_stability_impact == 'improvement' and bulk_density_change < -0.05:
            structural_stability = 'excellent'
        elif aggregate_stability_impact == 'improvement':
            structural_stability = 'good'
        elif aggregate_stability_impact == 'degradation':
            structural_stability = 'poor'
        else:
            structural_stability = 'fair'

        # Erosion impacts
        if aggregate_improvement > 0.1:
            erosion_resistance = 'increased'
            aggregate_protection = 0.8
        elif aggregate_improvement > 0.05:
            erosion_resistance = 'increased'
            aggregate_protection = 0.6
        elif aggregate_improvement < -0.02:
            erosion_resistance = 'decreased'
            aggregate_protection = 0.3
        else:
            erosion_resistance = 'neutral'
            aggregate_protection = 0.5

        # Drainage and aeration
        if infiltration_change > 0.1:
            drainage_impact = 'improved'
            aeration_impact = 'improved'
        elif infiltration_change < -0.05:
            drainage_impact = 'impaired'
            aeration_impact = 'impaired'
        else:
            drainage_impact = 'neutral'
            aeration_impact = 'neutral'

        # Root penetration
        if bulk_density_change < -0.05:
            root_penetration = 'improved'
        elif bulk_density_change > 0.03:
            root_penetration = 'impaired'
        else:
            root_penetration = 'neutral'

        # Long-term structure rating
        if structural_stability == 'excellent':
            long_term_rating = SoilHealthRating.EXCELLENT
        elif structural_stability == 'good':
            long_term_rating = SoilHealthRating.GOOD
        elif structural_stability == 'fair':
            long_term_rating = SoilHealthRating.NEUTRAL
        elif structural_stability == 'poor':
            long_term_rating = SoilHealthRating.CONCERNING
        else:
            long_term_rating = SoilHealthRating.POOR

        # Management practices
        management_practices = []
        if aggregate_stability_impact != 'improvement':
            management_practices.append("Add organic matter to improve aggregation")
            management_practices.append("Reduce tillage intensity to preserve structure")

        if compaction_risk == 'high':
            management_practices.append("Avoid field operations when soil is wet")
            management_practices.append("Use controlled traffic patterns")

        if drainage_impact == 'impaired':
            management_practices.append("Consider deep tillage to restore infiltration")
            management_practices.append("Add gypsum to improve soil structure")

        # Amelioration strategies
        amelioration = []
        if structural_stability in ['poor', 'fair']:
            amelioration.append("Apply compost annually at 5-10 tons/acre")
            amelioration.append("Establish deep-rooted cover crops")
            amelioration.append("Implement conservation tillage practices")

        if bulk_density_change > 0:
            amelioration.append("Use biological methods to restore soil aggregation")
            amelioration.append("Avoid heavy equipment on wet soil")

        return SoilStructureEvaluation(
            fertilizer_type=fert_key,
            fertilizer_name=fertilizer_name,
            aggregate_stability_impact=aggregate_stability_impact,
            macro_aggregate_formation=macro_agg_change,
            micro_aggregate_formation=micro_agg_change,
            bulk_density_change=bulk_density_change,
            porosity_change_percent=porosity_change,
            infiltration_rate_change=infiltration_change,
            water_holding_capacity_change=water_holding_change,
            compaction_risk=compaction_risk,
            crusting_tendency=crusting_tendency,
            structural_stability=structural_stability,
            erosion_resistance_change=erosion_resistance,
            aggregate_protection=aggregate_protection,
            drainage_impact=drainage_impact,
            aeration_impact=aeration_impact,
            root_penetration_impact=root_penetration,
            long_term_structure_rating=long_term_rating,
            structure_management_practices=management_practices,
            amelioration_strategies=amelioration
        )

    async def _perform_temporal_analysis(
        self,
        fert_key: str,
        fertilizer_name: str,
        om_impact: OrganicMatterImpact,
        ph_effects: PHEffectsAnalysis,
        microbial_assessment: MicrobialActivityAssessment,
        structure_eval: SoilStructureEvaluation
    ) -> TemporalImpactAnalysis:
        """Perform temporal (time-based) impact analysis."""

        # Short-term impacts (0-1 year)
        short_term_impacts = {
            'organic_matter': om_impact.short_term_om_change_percent,
            'ph_change': ph_effects.immediate_ph_change,
            'microbial_diversity': microbial_assessment.microbial_diversity_score,
            'aggregate_stability': structure_eval.aggregate_stability_impact
        }

        short_term_concerns = []
        short_term_benefits = []

        if ph_effects.immediate_ph_change < -0.2:
            short_term_concerns.append(f"Significant pH drop ({ph_effects.immediate_ph_change:.2f} units)")
        if microbial_assessment.short_term_microbiome_impact in [SoilHealthRating.CONCERNING, SoilHealthRating.POOR]:
            short_term_concerns.append("Negative impact on soil microbiome")
        if om_impact.short_term_om_change_percent > 0.1:
            short_term_benefits.append("Significant organic matter addition")
        if structure_eval.aggregate_stability_impact == 'improvement':
            short_term_benefits.append("Improved soil aggregate stability")

        # Determine short-term overall rating
        short_term_scores = [
            self._rating_to_score(om_impact.short_term_rating),
            self._rating_to_score(microbial_assessment.short_term_microbiome_impact),
            self._rating_to_score(structure_eval.long_term_structure_rating)
        ]
        short_term_avg = sum(short_term_scores) / len(short_term_scores)
        short_term_overall = self._score_to_rating(short_term_avg)

        # Medium-term impacts (1-5 years)
        medium_term_impacts = {
            'organic_matter': om_impact.medium_term_om_change_percent,
            'cumulative_ph_change': ph_effects.cumulative_ph_change_5yr,
            'microbiome_recovery': microbial_assessment.recovery_time_months,
            'structure_stability': structure_eval.structural_stability
        }

        # Determine trajectory
        if om_impact.medium_term_om_change_percent > om_impact.short_term_om_change_percent:
            trajectory = 'improving'
        elif abs(om_impact.medium_term_om_change_percent - om_impact.short_term_om_change_percent) < 0.05:
            trajectory = 'stable'
        else:
            trajectory = 'declining'

        medium_term_overall = short_term_overall  # Similar for now

        # Long-term impacts (5+ years)
        long_term_impacts = {
            'equilibrium_om': om_impact.equilibrium_om_level_percent,
            'cumulative_ph_effect': ph_effects.cumulative_ph_change_5yr * 2,  # Extrapolate
            'microbiome_adaptation': microbial_assessment.long_term_microbiome_impact,
            'structural_stability': structure_eval.long_term_structure_rating
        }

        long_term_scores = [
            self._rating_to_score(om_impact.long_term_rating),
            self._rating_to_score(microbial_assessment.long_term_microbiome_impact),
            self._rating_to_score(structure_eval.long_term_structure_rating)
        ]
        long_term_avg = sum(long_term_scores) / len(long_term_scores)
        long_term_overall = self._score_to_rating(long_term_avg)

        # Sustainability
        if long_term_overall in [SoilHealthRating.EXCELLENT, SoilHealthRating.GOOD]:
            sustainability = 'sustainable'
        elif long_term_overall == SoilHealthRating.NEUTRAL:
            sustainability = 'marginal'
        else:
            sustainability = 'unsustainable'

        # Cumulative effects
        # Calculate average scores for each time horizon (only numeric values)
        short_term_numeric = [v for v in short_term_impacts.values() if isinstance(v, (int, float))]
        medium_term_numeric = [v for v in medium_term_impacts.values() if isinstance(v, (int, float))]
        long_term_numeric = [v for v in long_term_impacts.values() if isinstance(v, (int, float))]
        
        short_term_avg = sum(short_term_numeric) / len(short_term_numeric) if short_term_numeric else 0
        medium_term_avg = sum(medium_term_numeric) / len(medium_term_numeric) if medium_term_numeric else 0
        long_term_avg = sum(long_term_numeric) / len(long_term_numeric) if long_term_numeric else 0
        
        cumulative_score = (short_term_avg + medium_term_avg + long_term_avg) / 3 * 100

        cumulative_risks = []
        cumulative_benefits = []

        if ph_effects.cumulative_ph_change_5yr < -0.5:
            cumulative_risks.append("Severe long-term soil acidification")
        if om_impact.long_term_om_change_percent < 0:
            cumulative_risks.append("Net organic matter depletion over time")
        if microbial_assessment.long_term_microbiome_impact == SoilHealthRating.POOR:
            cumulative_risks.append("Persistent microbiome degradation")

        if om_impact.long_term_om_change_percent > 0.5:
            cumulative_benefits.append("Substantial long-term OM building")
        if structure_eval.long_term_structure_rating == SoilHealthRating.EXCELLENT:
            cumulative_benefits.append("Excellent long-term structure improvement")

        # Reversibility
        if len(cumulative_risks) == 0:
            reversibility = 'easily_reversible'
        elif microbial_assessment.recovery_time_months <= 6:
            reversibility = 'partially_reversible'
        else:
            reversibility = 'partially_reversible'

        recovery_timeline = microbial_assessment.recovery_time_months / 12.0 if cumulative_risks else None

        # Recommendations by timeframe
        immediate_actions = []
        if ph_effects.requires_ph_management:
            immediate_actions.extend(ph_effects.ph_adjustment_recommendations)
        if microbial_assessment.short_term_microbiome_impact == SoilHealthRating.POOR:
            immediate_actions.append("Add microbial inoculants immediately")

        medium_term_management = []
        medium_term_management.append("Monitor key soil health indicators every 1-2 years")
        if trajectory == 'declining':
            medium_term_management.append("Implement corrective practices to reverse decline")

        long_term_strategies = []
        if sustainability == 'unsustainable':
            long_term_strategies.append("Consider alternative fertilizer selection for long-term soil health")
        long_term_strategies.extend(om_impact.recommendations[:2])

        return TemporalImpactAnalysis(
            fertilizer_type=fert_key,
            fertilizer_name=fertilizer_name,
            short_term_impacts=short_term_impacts,
            short_term_overall_rating=short_term_overall,
            short_term_concerns=short_term_concerns,
            short_term_benefits=short_term_benefits,
            medium_term_impacts=medium_term_impacts,
            medium_term_overall_rating=medium_term_overall,
            medium_term_trajectory=trajectory,
            long_term_impacts=long_term_impacts,
            long_term_overall_rating=long_term_overall,
            long_term_sustainability=sustainability,
            cumulative_impact_score=cumulative_score,
            cumulative_risks=cumulative_risks,
            cumulative_benefits=cumulative_benefits,
            impact_reversibility=reversibility,
            recovery_timeline_years=recovery_timeline,
            immediate_actions=immediate_actions,
            medium_term_management=medium_term_management,
            long_term_strategies=long_term_strategies
        )

    def _rating_to_score(self, rating: SoilHealthRating) -> float:
        """Convert rating to numeric score."""
        rating_scores = {
            SoilHealthRating.EXCELLENT: 5.0,
            SoilHealthRating.GOOD: 4.0,
            SoilHealthRating.NEUTRAL: 3.0,
            SoilHealthRating.CONCERNING: 2.0,
            SoilHealthRating.POOR: 1.0
        }
        return rating_scores[rating]

    def _score_to_rating(self, score: float) -> SoilHealthRating:
        """Convert numeric score to rating."""
        if score >= 4.5:
            return SoilHealthRating.EXCELLENT
        elif score >= 3.5:
            return SoilHealthRating.GOOD
        elif score >= 2.5:
            return SoilHealthRating.NEUTRAL
        elif score >= 1.5:
            return SoilHealthRating.CONCERNING
        else:
            return SoilHealthRating.POOR

    def _calculate_overall_soil_health_score(
        self,
        om_impact: OrganicMatterImpact,
        ph_effects: PHEffectsAnalysis,
        microbial_assessment: MicrobialActivityAssessment,
        structure_eval: SoilStructureEvaluation
    ) -> float:
        """
        Calculate overall soil health score (0-100).

        Weights:
        - Organic Matter: 30%
        - pH Effects: 25%
        - Microbial Activity: 25%
        - Soil Structure: 20%
        """
        # Component scores
        om_score = self._rating_to_score(om_impact.long_term_rating) * 20  # 0-100
        ph_score = self._calculate_ph_score(ph_effects) * 20
        microbial_score = microbial_assessment.microbial_diversity_score * 10  # Already 0-10
        structure_score = self._rating_to_score(structure_eval.long_term_structure_rating) * 20

        # Weighted average
        overall = (
            om_score * 0.30 +
            ph_score * 0.25 +
            microbial_score * 0.25 +
            structure_score * 0.20
        )

        return round(overall, 1)

    def _calculate_ph_score(self, ph_effects: PHEffectsAnalysis) -> float:
        """Calculate pH impact score (0-5 scale)."""
        if ph_effects.acidification_potential == 'none' and ph_effects.alkalinization_potential == 'none':
            return 5.0
        elif ph_effects.acidification_potential in ['none', 'low'] and ph_effects.alkalinization_potential in ['none', 'low']:
            return 4.0
        elif ph_effects.acidification_potential == 'medium' or ph_effects.alkalinization_potential == 'medium':
            return 3.0
        elif ph_effects.acidification_potential == 'high' or ph_effects.alkalinization_potential == 'high':
            return 2.0
        else:
            return 1.0

    def _determine_soil_health_rating(self, score: float) -> SoilHealthRating:
        """Determine overall soil health rating from score."""
        if score >= 80:
            return SoilHealthRating.EXCELLENT
        elif score >= 65:
            return SoilHealthRating.GOOD
        elif score >= 50:
            return SoilHealthRating.NEUTRAL
        elif score >= 35:
            return SoilHealthRating.CONCERNING
        else:
            return SoilHealthRating.POOR

    def _identify_positive_impacts(
        self,
        om_impact: OrganicMatterImpact,
        ph_effects: PHEffectsAnalysis,
        microbial_assessment: MicrobialActivityAssessment,
        structure_eval: SoilStructureEvaluation
    ) -> List[str]:
        """Identify positive soil health impacts."""
        positives = []

        if om_impact.long_term_om_change_percent > 0.3:
            positives.append(f"Excellent organic matter building (+{om_impact.long_term_om_change_percent:.2f}% over long term)")
        elif om_impact.long_term_om_change_percent > 0:
            positives.append(f"Positive organic matter contribution (+{om_impact.long_term_om_change_percent:.2f}%)")

        if microbial_assessment.microbial_diversity_score >= 7:
            positives.append("High microbial diversity and activity support")

        if structure_eval.aggregate_stability_impact == 'improvement':
            positives.append("Improved soil aggregate stability and structure")

        if structure_eval.infiltration_rate_change > 0.1:
            positives.append(f"Enhanced water infiltration (+{structure_eval.infiltration_rate_change:.2f} in/hr)")

        if ph_effects.acidification_potential == 'none' and ph_effects.alkalinization_potential == 'none':
            positives.append("Minimal pH impact - maintains soil buffering")

        return positives

    def _identify_negative_impacts(
        self,
        om_impact: OrganicMatterImpact,
        ph_effects: PHEffectsAnalysis,
        microbial_assessment: MicrobialActivityAssessment,
        structure_eval: SoilStructureEvaluation
    ) -> List[str]:
        """Identify negative soil health impacts."""
        negatives = []

        if om_impact.organic_matter_contribution_percent == 0:
            negatives.append("No organic matter contribution - relies entirely on crop residues")

        if ph_effects.acidification_potential in ['high', 'very_high']:
            negatives.append(
                f"Significant soil acidification risk "
                f"({ph_effects.cumulative_ph_change_5yr:.2f} pH units over 5 years)"
            )

        if microbial_assessment.microbial_diversity_score < 5:
            negatives.append("Suppression of soil microbial diversity and activity")

        if microbial_assessment.mycorrhizal_impact == 'negative':
            negatives.append("Negative impact on beneficial mycorrhizal fungi")

        if structure_eval.aggregate_stability_impact == 'degradation':
            negatives.append("Degradation of soil aggregate stability")

        if structure_eval.drainage_impact == 'impaired':
            negatives.append("Impaired soil drainage and aeration")

        return negatives

    def _identify_neutral_aspects(
        self,
        om_impact: OrganicMatterImpact,
        ph_effects: PHEffectsAnalysis,
        microbial_assessment: MicrobialActivityAssessment,
        structure_eval: SoilStructureEvaluation
    ) -> List[str]:
        """Identify neutral soil health aspects."""
        neutrals = []

        if om_impact.short_term_rating == SoilHealthRating.NEUTRAL:
            neutrals.append("Minimal short-term effect on organic matter")

        if ph_effects.acidification_potential == 'low' or ph_effects.alkalinization_potential == 'low':
            neutrals.append("Minor pH effects within manageable range")

        if microbial_assessment.soil_food_web_health == 'fair':
            neutrals.append("Moderate impact on soil food web")

        if structure_eval.aggregate_stability_impact == 'neutral':
            neutrals.append("Neutral effect on soil structure")

        return neutrals

    def _assess_risks(
        self,
        om_impact: OrganicMatterImpact,
        ph_effects: PHEffectsAnalysis,
        microbial_assessment: MicrobialActivityAssessment,
        structure_eval: SoilStructureEvaluation,
        temporal_analysis: TemporalImpactAnalysis
    ) -> Tuple[str, List[str], List[str]]:
        """
        Assess overall risks and priorities.

        Returns:
            Tuple of (risk_level, critical_concerns, mitigation_priorities)
        """
        critical_concerns = []
        mitigation_priorities = []

        # Check for critical concerns
        if ph_effects.acidification_potential == 'very_high':
            critical_concerns.append("CRITICAL: Very high soil acidification risk")
            mitigation_priorities.append("Immediate lime application required")
        elif ph_effects.acidification_potential == 'high':
            critical_concerns.append("High soil acidification potential")
            mitigation_priorities.append("Regular pH monitoring and lime management")

        if microbial_assessment.microbial_diversity_score < 4:
            critical_concerns.append("Severe suppression of soil microbial life")
            mitigation_priorities.append("Add organic amendments to restore microbiome")

        if temporal_analysis.long_term_sustainability == 'unsustainable':
            critical_concerns.append("Unsustainable for long-term soil health")
            mitigation_priorities.append("Consider alternative fertilizer selection")

        if structure_eval.structural_stability == 'poor':
            critical_concerns.append("Poor soil structural stability")
            mitigation_priorities.append("Implement structure-building practices")

        # Determine overall risk level
        if len(critical_concerns) >= 2:
            risk_level = 'critical'
        elif len(critical_concerns) >= 1:
            risk_level = 'high'
        elif temporal_analysis.medium_term_trajectory == 'declining':
            risk_level = 'medium'
        else:
            risk_level = 'low'

        # Additional mitigation priorities
        if om_impact.long_term_om_change_percent < 0.1:
            mitigation_priorities.append("Supplement with organic matter inputs")

        if microbial_assessment.mycorrhizal_impact == 'negative':
            mitigation_priorities.append("Reduce application rates to preserve mycorrhizae")

        return risk_level, critical_concerns, mitigation_priorities

    async def _generate_remediation_strategies(
        self,
        fertilizer_name: str,
        negative_impacts: List[str],
        critical_concerns: List[str],
        soil_data: SoilTestData,
        soil_texture: Optional[SoilTexture]
    ) -> List[RemediationStrategy]:
        """Generate remediation strategies for identified issues."""
        strategies = []

        # Strategy counter for unique IDs
        strategy_counter = 1

        # Acidification remediation
        if any('acidification' in concern.lower() for concern in critical_concerns + negative_impacts):
            strategy_id = f"remediation_{strategy_counter}"
            strategy_counter += 1

            # Calculate lime requirement
            current_ph = soil_data.ph
            target_ph = 6.5
            ph_increase_needed = max(0, target_ph - current_ph)
            lime_rate = ph_increase_needed * 2.0  # Rough estimate: 2 tons/acre per pH unit

            strategies.append(RemediationStrategy(
                strategy_id=strategy_id,
                strategy_name="Soil Acidification Correction",
                strategy_type="corrective",
                target_issue="Excessive soil acidification from fertilizer use",
                severity_addressed="major",
                implementation_steps=[
                    f"Test soil pH to confirm current level",
                    f"Apply {lime_rate:.1f} tons/acre of agricultural limestone",
                    "Incorporate lime into top 6-8 inches of soil",
                    "Retest pH after 6-12 months",
                    "Adjust fertilizer selection or rates to reduce future acidification"
                ],
                timeline_months=12,
                cost_per_acre=lime_rate * 45.0,  # $45/ton lime
                labor_requirement="medium",
                equipment_needed=["lime spreader", "tillage equipment (optional)"],
                expected_improvement_percent=75,
                confidence_level=0.9,
                success_factors=[
                    "Proper lime incorporation",
                    "Adequate time for reaction",
                    "Continued pH monitoring"
                ],
                risk_factors=[
                    "Over-liming can cause nutrient imbalances",
                    "Poor incorporation reduces effectiveness"
                ],
                monitoring_parameters=["soil_ph", "crop_performance", "nutrient_availability"],
                evaluation_timeline="6-12 months post-application",
                success_indicators=[
                    f"pH increase to {target_ph:.1f}",
                    "Improved nutrient availability",
                    "Better crop growth and health"
                ],
                alternative_approaches=[
                    "Use less acidifying fertilizer sources",
                    "Apply dolomitic lime for Mg benefit"
                ],
                complementary_practices=[
                    "Increase organic matter for buffering",
                    "Use split fertilizer applications"
                ]
            ))

        # Organic matter depletion remediation
        if any('organic matter' in impact.lower() and 'no' in impact.lower() for impact in negative_impacts):
            strategy_id = f"remediation_{strategy_counter}"
            strategy_counter += 1

            strategies.append(RemediationStrategy(
                strategy_id=strategy_id,
                strategy_name="Organic Matter Building Program",
                strategy_type="restorative",
                target_issue="Lack of organic matter contribution from fertilizer",
                severity_addressed="moderate",
                implementation_steps=[
                    "Apply 10 tons/acre of quality compost annually",
                    "Establish cover crops in rotation",
                    "Return all crop residues to field",
                    "Reduce tillage intensity",
                    "Consider manure application if available"
                ],
                timeline_months=36,
                cost_per_acre=250.0,  # Compost at $25/ton
                labor_requirement="medium",
                equipment_needed=["compost spreader", "cover crop seeder"],
                expected_improvement_percent=60,
                confidence_level=0.85,
                success_factors=[
                    "Consistent annual applications",
                    "Reduced tillage",
                    "Good cover crop establishment"
                ],
                risk_factors=[
                    "Variable compost quality",
                    "Weather impacts on cover crops"
                ],
                monitoring_parameters=["organic_matter_percent", "soil_structure", "water_holding_capacity"],
                evaluation_timeline="Test soil OM annually for 3 years",
                success_indicators=[
                    "OM increase of 0.1-0.2% per year",
                    "Improved soil structure",
                    "Enhanced water infiltration"
                ],
                alternative_approaches=[
                    "Use organic fertilizers instead",
                    "Implement intensive cover cropping"
                ],
                complementary_practices=[
                    "No-till or strip-till practices",
                    "Diverse crop rotations"
                ]
            ))

        # Microbial suppression remediation
        if any('microb' in impact.lower() and ('suppression' in impact.lower() or 'negative' in impact.lower())
               for impact in negative_impacts):
            strategy_id = f"remediation_{strategy_counter}"
            strategy_counter += 1

            strategies.append(RemediationStrategy(
                strategy_id=strategy_id,
                strategy_name="Microbiome Recovery Program",
                strategy_type="restorative",
                target_issue="Suppression of soil microbial diversity and activity",
                severity_addressed="moderate",
                implementation_steps=[
                    "Reduce synthetic fertilizer application rates by 25%",
                    "Add compost or other organic amendments",
                    "Use microbial inoculants with diverse species",
                    "Establish cover crops to feed soil biology",
                    "Avoid bare fallow periods"
                ],
                timeline_months=12,
                cost_per_acre=100.0,
                labor_requirement="low",
                equipment_needed=["existing fertilizer equipment"],
                expected_improvement_percent=70,
                confidence_level=0.75,
                success_factors=[
                    "Organic matter additions",
                    "Reduced fertilizer shock",
                    "Living roots in soil year-round"
                ],
                risk_factors=[
                    "Continued high synthetic fertilizer rates",
                    "Soil disturbance from tillage"
                ],
                monitoring_parameters=["microbial_biomass", "enzyme_activity", "crop_health"],
                evaluation_timeline="6-12 months",
                success_indicators=[
                    "Increased soil respiration",
                    "Improved crop resilience",
                    "Enhanced nutrient cycling"
                ],
                alternative_approaches=[
                    "Switch to slow-release fertilizers",
                    "Use organic fertilizer sources"
                ],
                complementary_practices=[
                    "Conservation tillage",
                    "Diverse crop rotations",
                    "Livestock integration"
                ]
            ))

        # Soil structure degradation remediation
        if any('structure' in impact.lower() or 'aggregate' in impact.lower()
               for impact in negative_impacts):
            strategy_id = f"remediation_{strategy_counter}"
            strategy_counter += 1

            strategies.append(RemediationStrategy(
                strategy_id=strategy_id,
                strategy_name="Soil Structure Restoration",
                strategy_type="restorative",
                target_issue="Degradation of soil structure and aggregate stability",
                severity_addressed="moderate",
                implementation_steps=[
                    "Apply gypsum at 1-2 tons/acre for immediate improvement",
                    "Add compost at 5-10 tons/acre annually",
                    "Implement controlled traffic farming",
                    "Use deep-rooted cover crops",
                    "Reduce tillage passes and intensity"
                ],
                timeline_months=24,
                cost_per_acre=180.0,
                labor_requirement="high",
                equipment_needed=["spreader", "subsoiler (if needed)"],
                expected_improvement_percent=65,
                confidence_level=0.80,
                success_factors=[
                    "Consistent organic matter additions",
                    "Reduced soil compaction",
                    "Time for structure to develop"
                ],
                risk_factors=[
                    "Continued compaction from traffic",
                    "Excessive tillage"
                ],
                monitoring_parameters=["aggregate_stability", "bulk_density", "infiltration_rate"],
                evaluation_timeline="12-24 months",
                success_indicators=[
                    "Increased aggregate stability",
                    "Reduced bulk density",
                    "Improved infiltration"
                ],
                alternative_approaches=[
                    "Deep tillage to break compaction",
                    "Biological drilling with deep roots"
                ],
                complementary_practices=[
                    "No-till or strip-till",
                    "Cover crops year-round"
                ]
            ))

        return strategies

    def _generate_preventive_practices(
        self,
        fert_key: str,
        fertilizer_name: str,
        risk_level: str
    ) -> List[str]:
        """Generate preventive practices to maintain soil health."""
        practices = []

        # Universal practices
        practices.append("Test soil every 2-3 years to monitor soil health trends")
        practices.append("Return crop residues to maintain organic matter balance")
        practices.append("Use crop rotation to enhance soil biological diversity")

        # Risk-based practices
        if risk_level in ['high', 'critical']:
            practices.append("Monitor soil pH annually to catch acidification early")
            practices.append("Add organic amendments alongside synthetic fertilizers")
            practices.append("Consider reducing application rates or switching to alternatives")

        # Fertilizer-specific practices
        if 'synthetic' in fert_key:
            practices.append("Use split applications to reduce microbiome shock")
            practices.append("Incorporate cover crops to offset lack of OM contribution")

        if 'organic' in fert_key:
            practices.append("Apply consistently to build stable organic matter levels")
            practices.append("Allow adequate decomposition time before planting")

        practices.append("Maintain adequate soil pH for optimal nutrient cycling")
        practices.append("Avoid over-application which increases negative impacts")

        return practices

    def _determine_monitoring_frequency(
        self,
        risk_level: str,
        temporal_analysis: TemporalImpactAnalysis
    ) -> str:
        """Determine appropriate monitoring frequency."""
        if risk_level == 'critical':
            return 'every 6 months'
        elif risk_level == 'high':
            return 'annually'
        elif temporal_analysis.medium_term_trajectory == 'declining':
            return 'annually'
        else:
            return 'every 2-3 years'

    def _identify_key_monitoring_indicators(
        self,
        om_impact: OrganicMatterImpact,
        ph_effects: PHEffectsAnalysis,
        microbial_assessment: MicrobialActivityAssessment,
        structure_eval: SoilStructureEvaluation
    ) -> List[str]:
        """Identify key indicators to monitor."""
        indicators = ['soil_pH', 'organic_matter_percent']

        if om_impact.organic_matter_contribution_percent > 0:
            indicators.append('soil_organic_carbon')

        if ph_effects.acidification_potential in ['high', 'very_high']:
            indicators.append('pH_trend')
            indicators.append('aluminum_saturation')

        if microbial_assessment.microbial_diversity_score < 6:
            indicators.append('microbial_biomass_carbon')
            indicators.append('soil_respiration')

        if structure_eval.aggregate_stability_impact != 'neutral':
            indicators.append('aggregate_stability')
            indicators.append('bulk_density')

        indicators.append('crop_performance')
        indicators.append('nutrient_availability')

        return indicators

    def _define_alert_thresholds(
        self,
        soil_data: SoilTestData,
        risk_level: str
    ) -> Dict[str, float]:
        """Define alert thresholds for monitoring."""
        thresholds = {}

        # pH thresholds
        if risk_level in ['high', 'critical']:
            thresholds['pH_lower_limit'] = max(5.5, soil_data.ph - 0.3)
            thresholds['pH_upper_limit'] = min(7.5, soil_data.ph + 0.3)
        else:
            thresholds['pH_lower_limit'] = 5.5
            thresholds['pH_upper_limit'] = 7.5

        # OM thresholds
        thresholds['organic_matter_minimum'] = max(2.0, soil_data.organic_matter_percent - 0.5)

        # CEC threshold (if available)
        if soil_data.cec_meq_per_100g:
            thresholds['cec_minimum'] = max(5.0, soil_data.cec_meq_per_100g * 0.9)

        return thresholds

    def _calculate_assessment_confidence(
        self,
        fert_key: str,
        soil_data: SoilTestData,
        field_conditions: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate confidence in the assessment."""
        confidence_factors = []

        # Data availability
        if soil_data.cec_meq_per_100g:
            confidence_factors.append(0.95)
        else:
            confidence_factors.append(0.85)

        # Fertilizer database coverage
        if fert_key in self.fertilizer_soil_health_database:
            confidence_factors.append(0.95)
        else:
            confidence_factors.append(0.75)  # Using default

        # Field conditions detail
        if field_conditions:
            confidence_factors.append(0.90)
        else:
            confidence_factors.append(0.80)

        # Recent soil test
        test_age_days = (datetime.now().date() - soil_data.test_date).days
        if test_age_days < 365:
            confidence_factors.append(0.95)
        elif test_age_days < 730:
            confidence_factors.append(0.85)
        else:
            confidence_factors.append(0.75)

        return round(sum(confidence_factors) / len(confidence_factors), 2)

    def _generate_data_quality_notes(
        self,
        soil_data: SoilTestData,
        field_conditions: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate data quality notes."""
        notes = []

        test_age_days = (datetime.now().date() - soil_data.test_date).days
        test_age_years = test_age_days / 365.25

        if test_age_years > 2:
            notes.append(f"Soil test is {test_age_years:.1f} years old - consider retesting")

        if not soil_data.cec_meq_per_100g:
            notes.append("CEC not provided - using texture-based estimates")

        if not field_conditions:
            notes.append("Limited field condition data - using general assumptions")

        if not soil_data.soil_texture:
            notes.append("Soil texture not specified - using default parameters")

        if notes:
            notes.insert(0, "Assessment based on available data with following limitations:")
        else:
            notes.append("High-quality data provided - assessment confidence is high")

        return notes

    def _identify_assessment_limitations(
        self,
        fert_key: str,
        soil_data: SoilTestData
    ) -> List[str]:
        """Identify limitations of the assessment."""
        limitations = []

        limitations.append(
            "Soil health impacts vary by site-specific conditions, climate, and management"
        )

        limitations.append(
            "Long-term projections assume consistent management and environmental conditions"
        )

        if fert_key not in self.fertilizer_soil_health_database:
            limitations.append(
                "Using generalized data for fertilizer type - actual impacts may vary"
            )

        limitations.append(
            "Microbial assessments are based on typical responses - actual microbiome changes vary"
        )

        limitations.append(
            "Assessment does not account for interactions with other farm inputs and practices"
        )

        return limitations

    def _normalize_fertilizer_key(self, fertilizer_type: str, fertilizer_name: str) -> str:
        """
        Normalize fertilizer identifier to match database keys.

        Args:
            fertilizer_type: Fertilizer type (organic, synthetic, etc.)
            fertilizer_name: Specific fertilizer name

        Returns:
            Normalized key for database lookup
        """
        # Convert to lowercase and remove special characters
        name_lower = fertilizer_name.lower().replace('-', '_').replace(' ', '_')
        type_lower = fertilizer_type.lower()

        # Check for direct matches in database
        if name_lower in self.fertilizer_soil_health_database:
            return name_lower

        # Check for type_name combinations
        type_name_key = f"{type_lower}_{name_lower}"
        if type_name_key in self.fertilizer_soil_health_database:
            return type_name_key

        # Pattern matching for common names
        if 'urea' in name_lower and 'coated' not in name_lower:
            return 'synthetic_urea'
        elif 'urea' in name_lower and ('coated' in name_lower or 'slow' in name_lower):
            return 'slow_release_coated_urea'
        elif 'ammonium' in name_lower and 'sulfate' in name_lower:
            return 'synthetic_ammonium_sulfate'
        elif 'anhydrous' in name_lower or 'ammonia' in name_lower:
            return 'synthetic_anhydrous_ammonia'
        elif 'map' in name_lower or 'monoammonium' in name_lower:
            return 'synthetic_map'
        elif 'potash' in name_lower or 'kcl' in name_lower:
            return 'synthetic_potash'
        elif 'compost' in name_lower:
            return 'organic_compost'
        elif 'manure' in name_lower:
            return 'organic_manure'
        elif 'fish' in name_lower:
            return 'organic_fish_emulsion'
        elif 'bone' in name_lower:
            return 'organic_bone_meal'

        # Default based on type
        if 'organic' in type_lower:
            return 'organic_compost'
        else:
            return 'synthetic_urea'

    async def compare_fertilizers_soil_health(
        self,
        fertilizer_options: List[Dict[str, Any]],
        soil_data: SoilTestData,
        soil_texture: Optional[SoilTexture] = None,
        field_conditions: Optional[Dict[str, Any]] = None
    ) -> List[SoilHealthImpactAssessment]:
        """
        Compare soil health impacts of multiple fertilizer options.

        Args:
            fertilizer_options: List of fertilizer option dictionaries with:
                - fertilizer_type: Type of fertilizer
                - fertilizer_name: Name of fertilizer
                - application_rate_lbs_per_acre: Application rate
                - application_frequency_per_year: Application frequency
            soil_data: Current soil test data
            soil_texture: Soil texture classification
            field_conditions: Additional field conditions

        Returns:
            List of soil health impact assessments, ranked by overall score
        """
        self.logger.info(f"Comparing soil health impacts of {len(fertilizer_options)} fertilizer options")

        # Assess each fertilizer
        assessments = []
        for option in fertilizer_options:
            assessment = await self.assess_soil_health_impact(
                fertilizer_type=option['fertilizer_type'],
                fertilizer_name=option['fertilizer_name'],
                application_rate_lbs_per_acre=option['application_rate_lbs_per_acre'],
                soil_data=soil_data,
                application_frequency_per_year=option.get('application_frequency_per_year', 1),
                soil_texture=soil_texture,
                field_conditions=field_conditions
            )
            assessments.append(assessment)

        # Sort by overall soil health score (descending)
        assessments.sort(key=lambda x: x.overall_soil_health_score, reverse=True)

        # Assign relative rankings
        for rank, assessment in enumerate(assessments, start=1):
            assessment.relative_soil_health_rank = rank

            # Identify better alternatives (higher ranked)
            if rank > 1:
                assessment.better_alternatives = [
                    assessments[i].fertilizer_name
                    for i in range(rank - 1)
                ]

        self.logger.info(
            f"Comparison complete. Best option: {assessments[0].fertilizer_name} "
            f"(score: {assessments[0].overall_soil_health_score:.1f}/100)"
        )

        return assessments

    async def generate_soil_health_optimized_recommendation(
        self,
        fertilizer_options: List[Dict[str, Any]],
        soil_data: SoilTestData,
        farmer_priorities: Dict[str, float],
        soil_texture: Optional[SoilTexture] = None,
        field_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate fertilizer recommendations optimized for soil health.

        Integrates soil health considerations into fertilizer selection by
        comparing options and providing soil health-weighted recommendations.

        Args:
            fertilizer_options: List of fertilizer options to evaluate
            soil_data: Current soil test data
            farmer_priorities: Farmer priorities including soil_health weight
            soil_texture: Soil texture classification
            field_conditions: Additional field conditions

        Returns:
            Dictionary with recommendations optimized for soil health
        """
        self.logger.info("Generating soil health-optimized fertilizer recommendations")

        # Get soil health assessments for all options
        assessments = await self.compare_fertilizers_soil_health(
            fertilizer_options, soil_data, soil_texture, field_conditions
        )

        # Extract soil health priority weight (0-1)
        soil_health_weight = farmer_priorities.get('soil_health', 0.5)

        # Calculate combined scores (soil health + other factors)
        # This would integrate with the fertilizer selection service
        # For now, we'll focus on soil health ranking

        # Top recommendation
        top_recommendation = assessments[0]

        # Identify best options by category
        best_om_builder = max(assessments, key=lambda x: x.organic_matter_impact.long_term_om_change_percent)
        best_ph_stability = min(assessments, key=lambda x: abs(x.ph_effects.cumulative_ph_change_5yr))
        best_microbial_support = max(assessments, key=lambda x: x.microbial_assessment.microbial_diversity_score)
        best_structure = max(
            assessments,
            key=lambda x: self._rating_to_score(x.structure_evaluation.long_term_structure_rating)
        )

        # Generate comprehensive recommendation
        recommendation = {
            'recommendation_summary': self._generate_recommendation_summary(
                top_recommendation, soil_health_weight
            ),
            'top_soil_health_option': {
                'name': top_recommendation.fertilizer_name,
                'score': top_recommendation.overall_soil_health_score,
                'rating': top_recommendation.soil_health_rating.value,
                'key_benefits': top_recommendation.positive_impacts,
                'key_concerns': top_recommendation.negative_impacts,
                'management_requirements': top_recommendation.preventive_practices
            },
            'category_best_options': {
                'organic_matter_building': {
                    'name': best_om_builder.fertilizer_name,
                    'om_contribution': best_om_builder.organic_matter_impact.long_term_om_change_percent,
                    'details': f"Adds {best_om_builder.organic_matter_impact.long_term_om_change_percent:.2f}% OM long-term"
                },
                'ph_stability': {
                    'name': best_ph_stability.fertilizer_name,
                    'ph_impact': best_ph_stability.ph_effects.cumulative_ph_change_5yr,
                    'details': f"Minimal pH impact ({best_ph_stability.ph_effects.cumulative_ph_change_5yr:.2f} units over 5 years)"
                },
                'microbial_health': {
                    'name': best_microbial_support.fertilizer_name,
                    'diversity_score': best_microbial_support.microbial_assessment.microbial_diversity_score,
                    'details': f"Supports microbial diversity (score: {best_microbial_support.microbial_assessment.microbial_diversity_score:.1f}/10)"
                },
                'soil_structure': {
                    'name': best_structure.fertilizer_name,
                    'structure_rating': best_structure.structure_evaluation.long_term_structure_rating.value,
                    'details': f"Excellent soil structure improvement ({best_structure.structure_evaluation.long_term_structure_rating.value})"
                }
            },
            'all_options_ranked': [
                {
                    'rank': assessment.relative_soil_health_rank,
                    'name': assessment.fertilizer_name,
                    'score': assessment.overall_soil_health_score,
                    'rating': assessment.soil_health_rating.value,
                    'key_strength': self._identify_key_strength(assessment),
                    'key_weakness': self._identify_key_weakness(assessment)
                }
                for assessment in assessments
            ],
            'soil_health_considerations': {
                'current_soil_status': self._summarize_current_soil_status(soil_data),
                'priority_improvements': self._identify_priority_improvements(assessments, soil_data),
                'risk_factors': self._identify_risk_factors(assessments),
                'monitoring_recommendations': top_recommendation.key_indicators_to_monitor
            },
            'implementation_guidance': {
                'application_strategy': self._generate_application_strategy(top_recommendation),
                'monitoring_plan': {
                    'frequency': top_recommendation.monitoring_frequency,
                    'key_indicators': top_recommendation.key_indicators_to_monitor,
                    'alert_thresholds': top_recommendation.alert_thresholds
                },
                'remediation_if_needed': [
                    {
                        'strategy': strategy.strategy_name,
                        'timeline': f"{strategy.timeline_months} months",
                        'cost': f"${strategy.cost_per_acre:.2f}/acre"
                    }
                    for strategy in top_recommendation.recommended_remediation[:2]
                ]
            },
            'long_term_outlook': {
                'sustainability': top_recommendation.temporal_analysis.long_term_sustainability,
                'trajectory': top_recommendation.temporal_analysis.medium_term_trajectory,
                'equilibrium_om': top_recommendation.organic_matter_impact.equilibrium_om_level_percent,
                'projected_impacts': top_recommendation.temporal_analysis.long_term_impacts
            }
        }

        self.logger.info(
            f"Soil health-optimized recommendation generated. "
            f"Top option: {top_recommendation.fertilizer_name} "
            f"(score: {top_recommendation.overall_soil_health_score:.1f}/100)"
        )

        return recommendation

    def _generate_recommendation_summary(
        self,
        assessment: SoilHealthImpactAssessment,
        soil_health_weight: float
    ) -> str:
        """Generate recommendation summary text."""
        summary = (
            f"Based on comprehensive soil health analysis, {assessment.fertilizer_name} "
            f"receives a soil health score of {assessment.overall_soil_health_score:.1f}/100 "
            f"({assessment.soil_health_rating.value}). "
        )

        if assessment.overall_soil_health_score >= 80:
            summary += "This is an excellent choice for long-term soil health. "
        elif assessment.overall_soil_health_score >= 65:
            summary += "This is a good option for maintaining soil health. "
        elif assessment.overall_soil_health_score >= 50:
            summary += "This option has neutral to moderate soil health impacts. "
        else:
            summary += "This option presents some soil health concerns. "

        if soil_health_weight >= 0.7:
            summary += (
                "Given your high priority on soil health, carefully consider the "
                "recommended management practices to optimize soil health outcomes."
            )

        return summary

    def _summarize_current_soil_status(self, soil_data: SoilTestData) -> str:
        """Summarize current soil health status."""
        om_status = "low" if soil_data.organic_matter_percent < 2.5 else \
                   "moderate" if soil_data.organic_matter_percent < 3.5 else "good"

        ph_status = "acidic" if soil_data.ph < 6.0 else \
                   "optimal" if 6.0 <= soil_data.ph <= 7.0 else "alkaline"

        return (
            f"Current soil has {om_status} organic matter ({soil_data.organic_matter_percent:.1f}%) "
            f"and {ph_status} pH ({soil_data.ph:.1f})"
        )

    def _identify_priority_improvements(
        self,
        assessments: List[SoilHealthImpactAssessment],
        soil_data: SoilTestData
    ) -> List[str]:
        """Identify priority soil health improvements needed."""
        priorities = []

        if soil_data.organic_matter_percent < 2.5:
            priorities.append("Build organic matter to improve soil health foundation")

        if soil_data.ph < 5.8:
            priorities.append("Correct soil acidity with lime application")
        elif soil_data.ph > 7.5:
            priorities.append("Address high pH to improve nutrient availability")

        # Check if all options have negative microbial impacts
        avg_microbial_score = np.mean([
            a.microbial_assessment.microbial_diversity_score for a in assessments
        ])
        if avg_microbial_score < 5:
            priorities.append("Enhance soil microbial diversity with organic amendments")

        return priorities

    def _identify_risk_factors(
        self,
        assessments: List[SoilHealthImpactAssessment]
    ) -> List[str]:
        """Identify common risk factors across options."""
        risks = []

        # Count how many options have high acidification risk
        high_acid_count = sum(
            1 for a in assessments
            if a.ph_effects.acidification_potential in ['high', 'very_high']
        )

        if high_acid_count >= len(assessments) * 0.5:
            risks.append(
                "Multiple options carry soil acidification risk - pH monitoring is critical"
            )

        # Check for OM depletion risk
        no_om_count = sum(
            1 for a in assessments
            if a.organic_matter_impact.organic_matter_contribution_percent == 0
        )

        if no_om_count == len(assessments):
            risks.append(
                "All options lack organic matter contribution - supplement with cover crops or compost"
            )

        return risks

    def _generate_application_strategy(
        self,
        assessment: SoilHealthImpactAssessment
    ) -> str:
        """Generate application strategy for soil health optimization."""
        strategies = []

        if assessment.overall_risk_level in ['high', 'critical']:
            strategies.append("Use split applications to reduce soil health impacts")

        if assessment.ph_effects.acidification_potential != 'none':
            strategies.append("Monitor soil pH regularly and apply lime as needed")

        if assessment.organic_matter_impact.organic_matter_contribution_percent == 0:
            strategies.append("Supplement with organic amendments or cover crops")

        if assessment.microbial_assessment.short_term_microbiome_impact == SoilHealthRating.CONCERNING:
            strategies.append("Add microbial inoculants or compost to support soil biology")

        strategies.extend(assessment.temporal_analysis.immediate_actions)

        return "; ".join(strategies[:3])  # Top 3 strategies

    def _identify_key_strength(self, assessment: SoilHealthImpactAssessment) -> str:
        """Identify key strength of fertilizer option."""
        if assessment.organic_matter_impact.long_term_om_change_percent > 0.5:
            return "Excellent organic matter building"
        elif assessment.microbial_assessment.microbial_diversity_score >= 8:
            return "Strong microbial support"
        elif assessment.structure_evaluation.long_term_structure_rating == SoilHealthRating.EXCELLENT:
            return "Superior structure improvement"
        elif abs(assessment.ph_effects.cumulative_ph_change_5yr) < 0.1:
            return "Excellent pH stability"
        else:
            return "Balanced soil health impact"

    def _identify_key_weakness(self, assessment: SoilHealthImpactAssessment) -> str:
        """Identify key weakness of fertilizer option."""
        if assessment.ph_effects.acidification_potential in ['high', 'very_high']:
            return "High acidification risk"
        elif assessment.organic_matter_impact.organic_matter_contribution_percent == 0:
            return "No organic matter contribution"
        elif assessment.microbial_assessment.microbial_diversity_score < 5:
            return "Suppresses soil microbiome"
        elif assessment.structure_evaluation.aggregate_stability_impact == 'degradation':
            return "Degrades soil structure"
        else:
            return "Minor soil health concerns"
