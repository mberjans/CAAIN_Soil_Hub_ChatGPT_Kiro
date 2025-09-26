"""
Comprehensive benefit quantification and tracking service for cover crops.

This service provides:
1. Benefit prediction and quantification
2. Measurement tracking and validation
3. Performance analytics and insights
4. ROI calculation and economic analysis
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4
import statistics
from dataclasses import dataclass

from models.cover_crop_models import (
    SoilBenefit, BenefitQuantificationEntry, BenefitMeasurementRecord,
    BenefitTrackingField, BenefitValidationProtocol, BenefitTrackingAnalytics,
    BenefitMeasurementMethod, BenefitQuantificationStatus,
    CoverCropSpecies, CoverCropRecommendation
)

logger = logging.getLogger(__name__)


@dataclass
class BenefitPredictionFactors:
    """Factors influencing benefit predictions."""
    species_characteristics: Dict[str, Any]
    soil_conditions: Dict[str, float]
    climate_data: Dict[str, float]
    management_practices: Dict[str, str]
    historical_performance: Optional[Dict[str, float]] = None


class BenefitQuantificationService:
    """Service for quantifying and tracking cover crop benefits."""
    
    def __init__(self):
        """Initialize the benefit quantification service."""
        self.logger = logging.getLogger(__name__)
        self._benefit_coefficients = self._load_benefit_coefficients()
        self._validation_protocols = self._load_validation_protocols()
    
    # === BENEFIT PREDICTION AND QUANTIFICATION ===
    
    async def predict_benefits(
        self,
        cover_crop_species: List[CoverCropSpecies],
        field_conditions: Dict[str, Any],
        implementation_details: Dict[str, Any]
    ) -> Dict[SoilBenefit, BenefitQuantificationEntry]:
        """Predict quantified benefits for cover crop implementation."""
        
        prediction_factors = BenefitPredictionFactors(
            species_characteristics=self._extract_species_characteristics(cover_crop_species),
            soil_conditions=field_conditions.get('soil', {}),
            climate_data=field_conditions.get('climate', {}),
            management_practices=implementation_details
        )
        
        predicted_benefits = {}
        
        for species in cover_crop_species:
            species_benefits = await self._predict_species_benefits(
                species, prediction_factors, field_conditions, implementation_details
            )
            
            # Merge species benefits
            for benefit_type, entry in species_benefits.items():
                if benefit_type in predicted_benefits:
                    # Combine benefits from multiple species
                    predicted_benefits[benefit_type] = self._combine_benefit_entries(
                        predicted_benefits[benefit_type], entry
                    )
                else:
                    predicted_benefits[benefit_type] = entry
        
        return predicted_benefits
    
    async def _predict_species_benefits(
        self,
        species: CoverCropSpecies,
        factors: BenefitPredictionFactors,
        field_conditions: Dict[str, Any],
        implementation_details: Dict[str, Any]
    ) -> Dict[SoilBenefit, BenefitQuantificationEntry]:
        """Predict benefits for a specific species."""
        
        benefits = {}
        field_size = field_conditions.get('field_size_acres', 1.0)
        
        # Nitrogen Fixation (for legumes)
        if hasattr(species, 'cover_crop_type') and 'legume' in str(species.cover_crop_type).lower():
            nitrogen_benefit = await self._predict_nitrogen_fixation(
                species, factors, field_size, implementation_details
            )
            benefits[SoilBenefit.NITROGEN_FIXATION] = nitrogen_benefit
        
        # Erosion Control
        erosion_benefit = await self._predict_erosion_control(
            species, factors, field_size, implementation_details
        )
        benefits[SoilBenefit.EROSION_CONTROL] = erosion_benefit
        
        # Organic Matter
        organic_matter_benefit = await self._predict_organic_matter_improvement(
            species, factors, field_size, implementation_details
        )
        benefits[SoilBenefit.ORGANIC_MATTER] = organic_matter_benefit
        
        # Weed Suppression
        weed_benefit = await self._predict_weed_suppression(
            species, factors, field_size, implementation_details
        )
        benefits[SoilBenefit.WEED_SUPPRESSION] = weed_benefit
        
        # Add other benefit predictions...
        benefits.update(await self._predict_additional_benefits(
            species, factors, field_size, implementation_details
        ))
        
        return benefits
    
    async def _predict_nitrogen_fixation(
        self,
        species: CoverCropSpecies,
        factors: BenefitPredictionFactors,
        field_size: float,
        implementation_details: Dict[str, Any]
    ) -> BenefitQuantificationEntry:
        """Predict nitrogen fixation benefits."""
        
        # Base nitrogen fixation rate (lbs N/acre)
        base_fixation = self._benefit_coefficients['nitrogen_fixation'].get(
            species.species_id, 80.0  # Default for legumes
        )
        
        # Environmental adjustments
        climate_factor = self._calculate_climate_factor(factors.climate_data, 'nitrogen_fixation')
        soil_factor = self._calculate_soil_factor(factors.soil_conditions, 'nitrogen_fixation') 
        management_factor = self._calculate_management_factor(implementation_details, 'nitrogen_fixation')
        
        # Calculate predicted fixation
        predicted_fixation = base_fixation * climate_factor * soil_factor * management_factor
        
        # Economic value ($/lb N)
        nitrogen_price = 0.55  # Average price per lb of N
        economic_value = predicted_fixation * nitrogen_price * field_size
        
        # Confidence based on data quality and species track record
        confidence = self._calculate_prediction_confidence(
            species, factors, 'nitrogen_fixation'
        )
        
        return BenefitQuantificationEntry(
            entry_id=str(uuid4()),
            farm_id=implementation_details.get('farm_id', 'unknown'),
            field_id=implementation_details.get('field_id', 'unknown'),
            cover_crop_implementation_id=implementation_details.get('implementation_id', str(uuid4())),
            benefit_type=SoilBenefit.NITROGEN_FIXATION,
            benefit_category="agronomic_economic",
            predicted_value=predicted_fixation,
            predicted_unit="lbs_N_per_acre",
            predicted_confidence=confidence,
            economic_value_predicted=economic_value
        )
    
    async def _predict_erosion_control(
        self,
        species: CoverCropSpecies,
        factors: BenefitPredictionFactors,
        field_size: float,
        implementation_details: Dict[str, Any]
    ) -> BenefitQuantificationEntry:
        """Predict erosion control benefits."""
        
        # Base erosion control effectiveness (% reduction)
        base_effectiveness = self._benefit_coefficients['erosion_control'].get(
            species.species_id, 0.65  # 65% reduction average
        )
        
        # Adjust for field conditions
        slope_factor = factors.soil_conditions.get('slope_percent', 5.0) / 10.0  # Normalize to 10% slope
        cover_density_factor = getattr(species, 'ground_cover_density', 0.8)
        
        predicted_effectiveness = min(0.95, base_effectiveness * (1 + slope_factor * 0.2) * cover_density_factor)
        
        # Economic value calculation
        # Estimate soil loss prevention value
        baseline_soil_loss = factors.soil_conditions.get('estimated_annual_soil_loss_tons_per_acre', 4.0)
        prevented_soil_loss = baseline_soil_loss * predicted_effectiveness
        soil_replacement_cost = 25.0  # $/ton
        economic_value = prevented_soil_loss * soil_replacement_cost * field_size
        
        confidence = self._calculate_prediction_confidence(
            species, factors, 'erosion_control'
        )
        
        return BenefitQuantificationEntry(
            entry_id=str(uuid4()),
            farm_id=implementation_details.get('farm_id', 'unknown'),
            field_id=implementation_details.get('field_id', 'unknown'),
            cover_crop_implementation_id=implementation_details.get('implementation_id', str(uuid4())),
            benefit_type=SoilBenefit.EROSION_CONTROL,
            benefit_category="environmental_economic",
            predicted_value=predicted_effectiveness,
            predicted_unit="percent_reduction",
            predicted_confidence=confidence,
            economic_value_predicted=economic_value
        )
    
    async def _predict_organic_matter_improvement(
        self,
        species: CoverCropSpecies,
        factors: BenefitPredictionFactors,
        field_size: float,
        implementation_details: Dict[str, Any]
    ) -> BenefitQuantificationEntry:
        """Predict organic matter improvement benefits."""
        
        # Base organic matter contribution (% increase per year)
        base_om_increase = self._benefit_coefficients['organic_matter'].get(
            species.species_id, 0.15  # 0.15% increase average
        )
        
        # Adjust for biomass production potential
        biomass_factor = getattr(species, 'biomass_production_rating', 0.7)
        climate_factor = self._calculate_climate_factor(factors.climate_data, 'organic_matter')
        
        predicted_om_increase = base_om_increase * biomass_factor * climate_factor
        
        # Economic value - improved soil health value
        current_om = factors.soil_conditions.get('organic_matter_percent', 2.5)
        om_improvement_value = 150.0  # $/acre per 1% OM increase
        economic_value = predicted_om_increase * om_improvement_value * field_size
        
        confidence = self._calculate_prediction_confidence(
            species, factors, 'organic_matter'
        )
        
        return BenefitQuantificationEntry(
            entry_id=str(uuid4()),
            farm_id=implementation_details.get('farm_id', 'unknown'),
            field_id=implementation_details.get('field_id', 'unknown'),
            cover_crop_implementation_id=implementation_details.get('implementation_id', str(uuid4())),
            benefit_type=SoilBenefit.ORGANIC_MATTER,
            benefit_category="agronomic_economic",
            predicted_value=predicted_om_increase,
            predicted_unit="percent_increase",
            predicted_confidence=confidence,
            economic_value_predicted=economic_value
        )
    
    async def _predict_weed_suppression(
        self,
        species: CoverCropSpecies,
        factors: BenefitPredictionFactors,
        field_size: float,
        implementation_details: Dict[str, Any]
    ) -> BenefitQuantificationEntry:
        """Predict weed suppression benefits."""
        
        # Base weed suppression effectiveness
        base_suppression = self._benefit_coefficients['weed_suppression'].get(
            species.species_id, 0.55  # 55% suppression average
        )
        
        # Adjust for species characteristics
        competitive_ability = getattr(species, 'competitive_ability_rating', 0.7)
        establishment_speed = getattr(species, 'establishment_speed_rating', 0.7)
        
        predicted_suppression = base_suppression * competitive_ability * establishment_speed
        
        # Economic value - herbicide cost savings
        baseline_herbicide_cost = 35.0  # $/acre average
        herbicide_savings = baseline_herbicide_cost * predicted_suppression
        economic_value = herbicide_savings * field_size
        
        confidence = self._calculate_prediction_confidence(
            species, factors, 'weed_suppression'
        )
        
        return BenefitQuantificationEntry(
            entry_id=str(uuid4()),
            farm_id=implementation_details.get('farm_id', 'unknown'),
            field_id=implementation_details.get('field_id', 'unknown'),
            cover_crop_implementation_id=implementation_details.get('implementation_id', str(uuid4())),
            benefit_type=SoilBenefit.WEED_SUPPRESSION,
            benefit_category="economic",
            predicted_value=predicted_suppression,
            predicted_unit="percent_suppression",
            predicted_confidence=confidence,
            economic_value_predicted=economic_value
        )
    
    async def _predict_additional_benefits(
        self,
        species: CoverCropSpecies,
        factors: BenefitPredictionFactors,
        field_size: float,
        implementation_details: Dict[str, Any]
    ) -> Dict[SoilBenefit, BenefitQuantificationEntry]:
        """Predict additional benefits like pest management, nutrient scavenging, etc."""
        
        benefits = {}
        
        # Nutrient Scavenging
        if hasattr(species, 'primary_benefits') and SoilBenefit.NUTRIENT_SCAVENGING in species.primary_benefits:
            scavenging_effectiveness = 0.70  # 70% nutrient retention
            nitrate_prevention_value = 20.0 * field_size  # $/acre value
            
            benefits[SoilBenefit.NUTRIENT_SCAVENGING] = BenefitQuantificationEntry(
                entry_id=str(uuid4()),
                farm_id=implementation_details.get('farm_id', 'unknown'),
                field_id=implementation_details.get('field_id', 'unknown'),
                cover_crop_implementation_id=implementation_details.get('implementation_id', str(uuid4())),
                benefit_type=SoilBenefit.NUTRIENT_SCAVENGING,
                benefit_category="environmental_economic",
                predicted_value=scavenging_effectiveness,
                predicted_unit="percent_retention",
                predicted_confidence=0.75,
                economic_value_predicted=nitrate_prevention_value
            )
        
        # Compaction Relief
        if hasattr(species, 'root_type') and 'taproot' in str(species.root_type).lower():
            compaction_relief = 0.60  # 60% improvement in compaction
            equipment_efficiency_value = 15.0 * field_size  # $/acre from improved operations
            
            benefits[SoilBenefit.COMPACTION_RELIEF] = BenefitQuantificationEntry(
                entry_id=str(uuid4()),
                farm_id=implementation_details.get('farm_id', 'unknown'),
                field_id=implementation_details.get('field_id', 'unknown'),
                cover_crop_implementation_id=implementation_details.get('implementation_id', str(uuid4())),
                benefit_type=SoilBenefit.COMPACTION_RELIEF,
                benefit_category="agronomic_economic",
                predicted_value=compaction_relief,
                predicted_unit="percent_improvement",
                predicted_confidence=0.70,
                economic_value_predicted=equipment_efficiency_value
            )
        
        # Pollinator Habitat
        if hasattr(species, 'flowering') and species.flowering:
            pollinator_support = 0.80  # High pollinator support
            ecosystem_service_value = 25.0 * field_size  # $/acre ecosystem value
            
            benefits[SoilBenefit.POLLINATOR_HABITAT] = BenefitQuantificationEntry(
                entry_id=str(uuid4()),
                farm_id=implementation_details.get('farm_id', 'unknown'),
                field_id=implementation_details.get('field_id', 'unknown'),
                cover_crop_implementation_id=implementation_details.get('implementation_id', str(uuid4())),
                benefit_type=SoilBenefit.POLLINATOR_HABITAT,
                benefit_category="environmental",
                predicted_value=pollinator_support,
                predicted_unit="habitat_quality_score",
                predicted_confidence=0.65,
                economic_value_predicted=ecosystem_service_value
            )
        
        return benefits
    
    # === MEASUREMENT TRACKING ===
    
    async def record_measurement(
        self,
        benefit_entry_id: str,
        measurement_method: BenefitMeasurementMethod,
        measured_value: float,
        measurement_unit: str,
        measurement_conditions: Dict[str, Any],
        technician_notes: Optional[str] = None
    ) -> BenefitMeasurementRecord:
        """Record a benefit measurement."""
        
        measurement_record = BenefitMeasurementRecord(
            record_id=str(uuid4()),
            measurement_method=measurement_method,
            measured_value=measured_value,
            measurement_unit=measurement_unit,
            measurement_conditions=measurement_conditions,
            technician_notes=technician_notes,
            measurement_accuracy=self._estimate_measurement_accuracy(measurement_method)
        )
        
        # Update benefit entry status
        await self._update_benefit_status(benefit_entry_id, BenefitQuantificationStatus.MEASURING)
        
        self.logger.info(f"Recorded measurement for benefit {benefit_entry_id}: {measured_value} {measurement_unit}")
        
        return measurement_record
    
    async def validate_measurements(
        self,
        benefit_entry: BenefitQuantificationEntry,
        validator_id: str,
        validation_notes: Optional[str] = None
    ) -> BenefitQuantificationEntry:
        """Validate measurements and update benefit entry."""
        
        if not benefit_entry.actual_measurements:
            raise ValueError("No measurements to validate")
        
        # Calculate statistics from measurements
        values = [m.measured_value for m in benefit_entry.actual_measurements]
        validated_value = statistics.mean(values)
        measurement_variance = statistics.variance(values) if len(values) > 1 else 0.0
        
        # Calculate prediction accuracy
        prediction_accuracy = self._calculate_prediction_accuracy(
            benefit_entry.predicted_value,
            validated_value
        )
        
        # Update benefit entry
        benefit_entry.validated_value = validated_value
        benefit_entry.measurement_variance = measurement_variance
        benefit_entry.prediction_accuracy = prediction_accuracy
        benefit_entry.status = BenefitQuantificationStatus.VALIDATED
        benefit_entry.expert_validation_notes = validation_notes
        
        # Mark measurements as validated
        for measurement in benefit_entry.actual_measurements:
            measurement.validated = True
            measurement.validator_id = validator_id
            measurement.validation_notes = validation_notes
        
        self.logger.info(f"Validated benefit {benefit_entry.entry_id} with accuracy {prediction_accuracy:.2%}")
        
        return benefit_entry
    
    # === FIELD-LEVEL TRACKING ===
    
    async def create_field_tracking(
        self,
        farm_id: str,
        field_id: str,
        field_size_acres: float,
        cover_crop_species: List[str],
        implementation_year: int,
        implementation_season: str,
        baseline_measurements: Optional[Dict[str, float]] = None
    ) -> BenefitTrackingField:
        """Create field-level benefit tracking."""
        
        tracking = BenefitTrackingField(
            tracking_id=str(uuid4()),
            farm_id=farm_id,
            field_id=field_id,
            field_size_acres=field_size_acres,
            cover_crop_species=cover_crop_species,
            implementation_year=implementation_year,
            implementation_season=implementation_season,
            baseline_measurements=baseline_measurements or {}
        )
        
        self.logger.info(f"Created field tracking for {field_id}: {field_size_acres} acres")
        
        return tracking
    
    async def update_field_tracking(
        self,
        tracking: BenefitTrackingField,
        new_benefit_entries: List[BenefitQuantificationEntry]
    ) -> BenefitTrackingField:
        """Update field tracking with new benefit data."""
        
        # Add new entries
        tracking.tracked_benefits.extend(new_benefit_entries)
        
        # Recalculate aggregated values
        tracking.total_predicted_value = sum(
            entry.economic_value_predicted or 0.0
            for entry in tracking.tracked_benefits
        )
        
        tracking.total_realized_value = sum(
            entry.economic_value_actual or 0.0
            for entry in tracking.tracked_benefits
            if entry.economic_value_actual is not None
        )
        
        # Calculate overall prediction accuracy
        validated_entries = [
            entry for entry in tracking.tracked_benefits
            if entry.prediction_accuracy is not None
        ]
        
        if validated_entries:
            tracking.overall_prediction_accuracy = statistics.mean(
                entry.prediction_accuracy for entry in validated_entries
            )
        
        # Calculate ROI
        if tracking.total_predicted_value > 0:
            implementation_cost = 75.0 * tracking.field_size_acres  # Estimated cost $/acre
            tracking.roi_predicted = (tracking.total_predicted_value - implementation_cost) / implementation_cost
        
        if tracking.total_realized_value and tracking.total_realized_value > 0:
            implementation_cost = 75.0 * tracking.field_size_acres
            tracking.roi_actual = (tracking.total_realized_value - implementation_cost) / implementation_cost
        
        tracking.last_updated = datetime.utcnow()
        
        return tracking
    
    # === ANALYTICS AND INSIGHTS ===
    
    async def generate_benefit_analytics(
        self,
        farm_ids: List[str],
        analysis_period_start: datetime,
        analysis_period_end: datetime
    ) -> BenefitTrackingAnalytics:
        """Generate comprehensive benefit analytics from tracking data."""
        return await self.generate_analytics(farm_ids, analysis_period_start, analysis_period_end)
    
    async def get_field_tracking_status(
        self,
        field_id: str
    ) -> Optional[BenefitTrackingField]:
        """Get the tracking status for a specific field."""
        # This would typically query a database
        # For testing purposes, return a mock tracking status
        
        if not field_id or field_id.strip() == "":
            return None
            
        # Simulate retrieving field tracking data
        tracking = BenefitTrackingField(
            tracking_id=f"track_{field_id}",
            farm_id=f"farm_{field_id}",
            field_id=field_id,
            field_size_acres=25.0,
            cover_crop_species=["crimson_clover", "winter_rye"],
            implementation_year=2024,
            implementation_season="fall",
            baseline_measurements={
                "soil_nitrogen_ppm": 15.0,
                "organic_matter_percent": 3.2,
                "bulk_density_g_cm3": 1.35
            }
        )
        
        # Add some sample benefits
        sample_benefit = BenefitQuantificationEntry(
            entry_id=str(uuid4()),
            farm_id=tracking.farm_id,
            field_id=field_id,
            cover_crop_implementation_id=str(uuid4()),
            benefit_type=SoilBenefit.NITROGEN_FIXATION,
            benefit_category="nutrient",
            predicted_value=120.0,
            predicted_unit="lbs_N_per_acre",
            predicted_confidence=0.85,
            economic_value_predicted=180.0
        )
        
        tracking.tracked_benefits = [sample_benefit]
        tracking.total_predicted_value = 180.0
        tracking.roi_predicted = 1.4
        
        self.logger.info(f"Retrieved tracking status for field {field_id}")
        
        return tracking
    
    async def generate_analytics(
        self,
        farm_ids: List[str],
        analysis_period_start: datetime,
        analysis_period_end: datetime
    ) -> BenefitTrackingAnalytics:
        """Generate comprehensive analytics from tracking data."""
        
        # This would typically query a database
        # For now, simulate analytics generation
        
        analytics = BenefitTrackingAnalytics(
            analytics_id=str(uuid4()),
            analysis_period_start=analysis_period_start,
            analysis_period_end=analysis_period_end,
            farm_ids=farm_ids,
            field_count=len(farm_ids) * 3,  # Simulate multiple fields per farm
            total_acres_analyzed=len(farm_ids) * 50.0,  # Simulate acreage (50 acres per farm)
            recommendation_summary="Analysis shows strong nitrogen fixation performance from legumes with opportunities to improve erosion control measurement protocols."
        )
        
        # Simulate benefit accuracy by type
        analytics.benefit_accuracy_by_type = {
            SoilBenefit.NITROGEN_FIXATION: 0.85,
            SoilBenefit.EROSION_CONTROL: 0.78,
            SoilBenefit.ORGANIC_MATTER: 0.72,
            SoilBenefit.WEED_SUPPRESSION: 0.81,
            SoilBenefit.NUTRIENT_SCAVENGING: 0.76
        }
        
        # Generate insights and recommendations
        analytics.measurement_protocol_improvements = [
            "Increase measurement frequency for organic matter tracking",
            "Implement standardized soil sampling protocols",
            "Add weather station data integration for better predictions"
        ]
        
        analytics.prediction_model_refinements = [
            "Incorporate historical yield data for better nitrogen fixation predictions",
            "Add regional climate adjustment factors",
            "Improve species-specific benefit coefficients"
        ]
        
        analytics.farmer_recommendations = [
            "Focus on legume species for maximum nitrogen fixation benefits",
            "Consider multi-species mixtures for diverse benefit portfolios",
            "Implement consistent termination timing for optimal benefit realization"
        ]
        
        return analytics
    
    # === HELPER METHODS ===
    
    def _load_benefit_coefficients(self) -> Dict[str, Dict[str, float]]:
        """Load benefit prediction coefficients."""
        return {
            'nitrogen_fixation': {
                'crimson_clover': 120.0,
                'hairy_vetch': 150.0,
                'red_clover': 100.0,
                'winter_peas': 90.0
            },
            'erosion_control': {
                'winter_rye': 0.85,
                'winter_wheat': 0.75,
                'annual_ryegrass': 0.80,
                'crimson_clover': 0.70
            },
            'organic_matter': {
                'winter_rye': 0.20,
                'hairy_vetch': 0.18,
                'oats': 0.15,
                'buckwheat': 0.12
            },
            'weed_suppression': {
                'winter_rye': 0.75,
                'annual_ryegrass': 0.70,
                'winter_wheat': 0.65,
                'oats': 0.60
            }
        }
    
    def _load_validation_protocols(self) -> Dict[SoilBenefit, BenefitValidationProtocol]:
        """Load validation protocols for different benefits."""
        protocols = {}
        
        # Nitrogen fixation protocol
        protocols[SoilBenefit.NITROGEN_FIXATION] = BenefitValidationProtocol(
            protocol_id="nfix_protocol_v1",
            protocol_name="Nitrogen Fixation Validation Protocol",
            benefit_type=SoilBenefit.NITROGEN_FIXATION,
            minimum_measurements=3,
            measurement_frequency="monthly",
            measurement_duration_months=6,
            preferred_methods=[
                BenefitMeasurementMethod.SOIL_SAMPLING,
                BenefitMeasurementMethod.LABORATORY_ANALYSIS,
                BenefitMeasurementMethod.BIOMASS_MEASUREMENT
            ]
        )
        
        # Add other protocols...
        
        return protocols
    
    def _extract_species_characteristics(self, species_list: List[CoverCropSpecies]) -> Dict[str, Any]:
        """Extract relevant characteristics from species list."""
        characteristics = {
            'total_species_count': len(species_list),
            'legume_count': sum(1 for s in species_list if 'legume' in str(getattr(s, 'cover_crop_type', '')).lower()),
            'grass_count': sum(1 for s in species_list if 'grass' in str(getattr(s, 'cover_crop_type', '')).lower()),
            'brassica_count': sum(1 for s in species_list if 'brassica' in str(getattr(s, 'cover_crop_type', '')).lower()),
            'avg_biomass_potential': statistics.mean([getattr(s, 'biomass_production_rating', 0.7) for s in species_list]),
            'winter_hardy_count': sum(1 for s in species_list if getattr(s, 'winter_hardy', False))
        }
        return characteristics
    
    def _calculate_climate_factor(self, climate_data: Dict[str, float], benefit_type: str) -> float:
        """Calculate climate adjustment factor for benefit predictions."""
        # Simplified climate factor calculation
        temp_factor = 1.0
        precip_factor = 1.0
        
        if 'avg_temp_f' in climate_data:
            temp = climate_data['avg_temp_f']
            if benefit_type == 'nitrogen_fixation':
                # Optimal temperature range for N fixation
                if 45 <= temp <= 75:
                    temp_factor = 1.0
                else:
                    temp_factor = max(0.5, 1.0 - abs(temp - 60) / 100.0)
        
        if 'annual_precip_inches' in climate_data:
            precip = climate_data['annual_precip_inches']
            if 25 <= precip <= 45:
                precip_factor = 1.0
            elif precip < 25:
                precip_factor = max(0.6, precip / 25.0)
            else:
                precip_factor = max(0.7, 1.0 - (precip - 45) / 100.0)
        
        return temp_factor * precip_factor
    
    def _calculate_soil_factor(self, soil_conditions: Dict[str, float], benefit_type: str) -> float:
        """Calculate soil adjustment factor for benefit predictions."""
        ph_factor = 1.0
        fertility_factor = 1.0
        
        if 'ph' in soil_conditions:
            ph = soil_conditions['ph']
            if benefit_type == 'nitrogen_fixation':
                # Optimal pH for legume N fixation
                if 6.0 <= ph <= 7.5:
                    ph_factor = 1.0
                else:
                    ph_factor = max(0.5, 1.0 - abs(ph - 6.8) / 3.0)
        
        if 'fertility_index' in soil_conditions:
            fertility = soil_conditions['fertility_index']
            fertility_factor = min(1.2, max(0.7, fertility))
        
        return ph_factor * fertility_factor
    
    def _calculate_management_factor(self, implementation_details: Dict[str, Any], benefit_type: str) -> float:
        """Calculate management practice adjustment factor."""
        # Simplified management factor
        seeding_rate_factor = implementation_details.get('seeding_rate_factor', 1.0)
        planting_timing_factor = implementation_details.get('timing_factor', 1.0)
        
        return min(1.3, max(0.7, seeding_rate_factor * planting_timing_factor))
    
    def _calculate_prediction_confidence(
        self,
        species: CoverCropSpecies,
        factors: BenefitPredictionFactors,
        benefit_type: str
    ) -> float:
        """Calculate confidence level for benefit prediction."""
        
        # Base confidence from species data quality
        base_confidence = 0.75
        
        # Adjust for data availability
        if factors.historical_performance:
            base_confidence += 0.10
        
        # Adjust for environmental data quality
        climate_data_quality = len(factors.climate_data) / 5.0  # Assume 5 key climate variables
        soil_data_quality = len(factors.soil_conditions) / 8.0  # Assume 8 key soil variables
        
        data_adjustment = (climate_data_quality + soil_data_quality) / 2.0 * 0.15
        
        # Species-specific confidence
        species_confidence_bonus = 0.0
        if hasattr(species, 'data_quality_score'):
            species_confidence_bonus = species.data_quality_score * 0.10
        
        final_confidence = min(0.95, base_confidence + data_adjustment + species_confidence_bonus)
        return max(0.40, final_confidence)
    
    def _combine_benefit_entries(
        self,
        entry1: BenefitQuantificationEntry,
        entry2: BenefitQuantificationEntry
    ) -> BenefitQuantificationEntry:
        """Combine benefit entries from multiple species."""
        
        # Combine values based on benefit type
        if entry1.predicted_unit in ["percent_reduction", "percent_suppression", "percent_increase"]:
            # For percentage benefits, use complementary combination: 1 - (1-a)*(1-b)
            # This prevents values from exceeding 100%
            combined_value = 1.0 - (1.0 - entry1.predicted_value) * (1.0 - entry2.predicted_value)
            combined_value = min(0.95, combined_value)  # Cap at 95%
        else:
            # For absolute values (like nitrogen fixation lbs/acre), add them
            combined_value = entry1.predicted_value + entry2.predicted_value
        
        # Create new combined entry
        combined_entry = BenefitQuantificationEntry(
            entry_id=str(uuid4()),
            farm_id=entry1.farm_id,
            field_id=entry1.field_id,
            cover_crop_implementation_id=entry1.cover_crop_implementation_id,
            benefit_type=entry1.benefit_type,
            benefit_category=entry1.benefit_category,
            predicted_value=combined_value,
            predicted_unit=entry1.predicted_unit,
            predicted_confidence=statistics.mean([entry1.predicted_confidence, entry2.predicted_confidence]),
            economic_value_predicted=(entry1.economic_value_predicted or 0.0) + (entry2.economic_value_predicted or 0.0)
        )
        
        return combined_entry
    
    def _estimate_measurement_accuracy(self, method: BenefitMeasurementMethod) -> float:
        """Estimate measurement accuracy based on method."""
        accuracy_map = {
            BenefitMeasurementMethod.LABORATORY_ANALYSIS: 0.95,
            BenefitMeasurementMethod.SOIL_SAMPLING: 0.90,
            BenefitMeasurementMethod.BIOMASS_MEASUREMENT: 0.85,
            BenefitMeasurementMethod.YIELD_COMPARISON: 0.88,
            BenefitMeasurementMethod.WATER_INFILTRATION_TEST: 0.80,
            BenefitMeasurementMethod.FIELD_OBSERVATION: 0.70,
            BenefitMeasurementMethod.SATELLITE_IMAGERY: 0.75,
            BenefitMeasurementMethod.EROSION_MONITORING: 0.82,
            BenefitMeasurementMethod.NITRATE_LEACHING_TEST: 0.92,
            BenefitMeasurementMethod.WEED_DENSITY_COUNT: 0.85,
            BenefitMeasurementMethod.PEST_MONITORING: 0.78,
            BenefitMeasurementMethod.ECONOMIC_ANALYSIS: 0.75
        }
        return accuracy_map.get(method, 0.75)
    
    def _calculate_prediction_accuracy(self, predicted: float, actual: float) -> float:
        """Calculate prediction accuracy."""
        if predicted == 0:
            return 0.0 if actual != 0 else 1.0
        
        error = abs(predicted - actual) / abs(predicted)
        accuracy = max(0.0, 1.0 - error)
        return accuracy
    
    async def _update_benefit_status(self, entry_id: str, status: BenefitQuantificationStatus):
        """Update benefit entry status (would typically update database)."""
        self.logger.info(f"Updated benefit {entry_id} status to {status}")
    
    async def generate_benefit_analytics(self, filters: Dict[str, Any] = None) -> BenefitTrackingAnalytics:
        """Generate comprehensive benefit tracking analytics."""
        logger.info("Generating benefit tracking analytics")
        
        # This would typically query the database with filters
        # For now, return mock analytics data
        analytics = BenefitTrackingAnalytics(
            total_fields_tracked=10,
            active_tracking_sessions=5,
            completed_measurements=25,
            average_roi=2.3,
            top_performing_species=["crimson_clover", "winter_rye"],
            benefit_performance_summary={
                "nitrogen_fixation": {"average_value": 125.0, "confidence": 0.82},
                "organic_matter": {"average_value": 0.35, "confidence": 0.78}
            },
            prediction_accuracy_rates={
                "nitrogen_fixation": 0.85,
                "erosion_control": 0.78,
                "organic_matter": 0.73
            },
            economic_impact_summary={
                "total_value_generated": 15000.0,
                "cost_savings": 8500.0,
                "return_on_investment": 2.3
            }
        )
        
        logger.info("Successfully generated benefit tracking analytics")
        return analytics
    
    async def get_field_tracking_status(self, field_id: str) -> Optional[Dict[str, Any]]:
        """Get current tracking status for a specific field."""
        logger.info(f"Getting tracking status for field: {field_id}")
        
        # This would typically query the database
        # For now, return mock tracking status
        if not field_id or field_id.strip() == "":
            return None
        
        status = {
            "field_id": field_id,
            "tracking_active": True,
            "species_tracked": ["crimson_clover"],
            "measurements_completed": 3,
            "measurements_pending": 2,
            "last_measurement_date": "2024-12-15",
            "next_scheduled_measurement": "2025-01-15",
            "current_roi": 1.8,
            "benefit_realization": {
                "nitrogen_fixation": {"predicted": 120.0, "actual": 115.0, "variance": -4.2},
                "organic_matter": {"predicted": 0.3, "actual": 0.28, "variance": -6.7}
            },
            "recommendations": [
                "Schedule spring soil test for final nitrogen measurement",
                "Consider extending cover crop season for maximum benefit"
            ]
        }
        
        logger.info(f"Successfully retrieved tracking status for field: {field_id}")
        return status
    
    async def create_field_tracking(
        self, 
        field_id: str, 
        species_ids: List[str], 
        predicted_benefits: Dict[str, Any],
        field_size_acres: float,
        planting_date: datetime,
        farmer_id: Optional[str] = None
    ) -> BenefitTrackingField:
        """Create benefit tracking record for a field."""
        logger.info(f"Creating field tracking for field: {field_id}")
        
        # Create tracking record
        tracking = BenefitTrackingField(
            field_id=field_id,
            tracking_id=f"track_{uuid4().hex[:8]}",
            species_tracked=species_ids,
            predicted_benefits=predicted_benefits,
            field_size_acres=field_size_acres,
            planting_date=planting_date,
            farmer_id=farmer_id,
            tracking_status="active",
            measurements_completed=0,
            next_measurement_due=planting_date + timedelta(days=90),
            monitoring_protocols=self._create_monitoring_protocols(species_ids)
        )
        
        logger.info(f"Successfully created field tracking: {tracking.tracking_id}")
        return tracking
    
    def _create_monitoring_protocols(self, species_ids: List[str]) -> List[Dict[str, Any]]:
        """Create monitoring protocols for tracked species."""
        protocols = []
        for species_id in species_ids:
            protocols.append({
                "species_id": species_id,
                "measurement_schedule": ["30_days", "90_days", "termination", "post_harvest"],
                "required_measurements": ["nitrogen_fixation", "organic_matter", "soil_structure"],
                "optional_measurements": ["erosion_control", "weed_suppression"]
            })
        return protocols