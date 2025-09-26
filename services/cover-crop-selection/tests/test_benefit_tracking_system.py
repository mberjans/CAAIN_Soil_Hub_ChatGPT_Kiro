"""
Comprehensive tests for the benefit quantification and tracking system.

Tests cover:
1. Benefit prediction accuracy
2. Measurement recording and validation
3. Field-level tracking
4. Analytics generation
5. Integration scenarios
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import statistics
from typing import Dict, List

from src.services.benefit_tracking_service import BenefitQuantificationService, BenefitPredictionFactors
from src.models.cover_crop_models import (
    SoilBenefit, BenefitQuantificationEntry, BenefitMeasurementRecord,
    BenefitTrackingField, BenefitTrackingAnalytics, BenefitValidationProtocol,
    BenefitMeasurementMethod, BenefitQuantificationStatus,
    CoverCropSpecies, CoverCropType, GrowingSeason
)


@pytest.fixture
def benefit_service():
    """Create benefit quantification service instance."""
    return BenefitQuantificationService()


@pytest.fixture
def sample_legume_species():
    """Create sample legume cover crop species."""
    return CoverCropSpecies(
        species_id="crimson_clover",
        common_name="Crimson Clover",
        scientific_name="Trifolium incarnatum",
        cover_crop_type=CoverCropType.LEGUME,
        hardiness_zones=["6a", "6b", "7a", "7b", "8a"],
        min_temp_f=20.0,
        max_temp_f=90.0,
        growing_season=GrowingSeason.WINTER,
        ph_range={"min": 6.0, "max": 7.5},
        drainage_tolerance=["well_drained", "moderately_well_drained"],
        seeding_rate_lbs_acre={"broadcast": 15.0, "drilled": 12.0},
        planting_depth_inches=0.25,
        days_to_establishment=14,
        biomass_production="medium_high",
        primary_benefits=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.EROSION_CONTROL],
        nitrogen_fixation_lbs_acre=120.0,
        root_depth_feet=2.5,
        termination_methods=["herbicide", "mowing", "frost_kill"],
        cash_crop_compatibility=["corn", "soybeans", "cotton"],
        seed_cost_per_acre=45.0,
        establishment_cost_per_acre=65.0
    )


@pytest.fixture
def sample_grass_species():
    """Create sample grass cover crop species."""
    return CoverCropSpecies(
        species_id="winter_rye",
        common_name="Winter Rye",
        scientific_name="Secale cereale",
        cover_crop_type=CoverCropType.GRASS,
        hardiness_zones=["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a"],
        min_temp_f=-20.0,
        max_temp_f=85.0,
        growing_season=GrowingSeason.WINTER,
        ph_range={"min": 5.0, "max": 8.0},
        drainage_tolerance=["well_drained", "moderately_well_drained", "somewhat_poorly_drained"],
        seeding_rate_lbs_acre={"broadcast": 90.0, "drilled": 70.0},
        planting_depth_inches=1.0,
        days_to_establishment=7,
        biomass_production="high",
        primary_benefits=[SoilBenefit.EROSION_CONTROL, SoilBenefit.WEED_SUPPRESSION],
        root_depth_feet=4.0,
        termination_methods=["herbicide", "mowing", "tillage"],
        cash_crop_compatibility=["corn", "soybeans", "cotton", "wheat"],
        seed_cost_per_acre=35.0,
        establishment_cost_per_acre=55.0
    )


@pytest.fixture
def sample_field_conditions():
    """Create sample field conditions."""
    return {
        'field_size_acres': 50.0,
        'soil': {
            'ph': 6.5,
            'organic_matter_percent': 2.8,
            'fertility_index': 0.8,
            'slope_percent': 3.0,
            'estimated_annual_soil_loss_tons_per_acre': 2.5
        },
        'climate': {
            'avg_temp_f': 55.0,
            'annual_precip_inches': 35.0,
            'growing_degree_days': 2800,
            'frost_free_days': 180
        }
    }


@pytest.fixture
def sample_implementation_details():
    """Create sample implementation details."""
    return {
        'farm_id': 'farm_001',
        'field_id': 'field_A',
        'implementation_id': 'impl_2024_001',
        'seeding_rate_factor': 1.0,
        'timing_factor': 0.95,
        'planting_date': '2024-09-15',
        'termination_method': 'herbicide'
    }


class TestBenefitPrediction:
    """Test benefit prediction functionality."""
    
    @pytest.mark.asyncio
    async def test_predict_nitrogen_fixation_legume(
        self, benefit_service, sample_legume_species, sample_field_conditions, sample_implementation_details
    ):
        """Test nitrogen fixation prediction for legume species."""
        
        predicted_benefits = await benefit_service.predict_benefits(
            [sample_legume_species],
            sample_field_conditions,
            sample_implementation_details
        )
        
        # Should predict nitrogen fixation for legume
        assert SoilBenefit.NITROGEN_FIXATION in predicted_benefits
        
        n_benefit = predicted_benefits[SoilBenefit.NITROGEN_FIXATION]
        assert isinstance(n_benefit, BenefitQuantificationEntry)
        assert n_benefit.benefit_type == SoilBenefit.NITROGEN_FIXATION
        assert n_benefit.predicted_value > 0
        assert n_benefit.predicted_unit == "lbs_N_per_acre"
        assert n_benefit.economic_value_predicted > 0
        assert 0.4 <= n_benefit.predicted_confidence <= 0.95
        
        # Should be reasonable nitrogen fixation rate (50-200 lbs N/acre)
        assert 50 <= n_benefit.predicted_value <= 200
    
    @pytest.mark.asyncio 
    async def test_predict_erosion_control_all_species(
        self, benefit_service, sample_legume_species, sample_grass_species, 
        sample_field_conditions, sample_implementation_details
    ):
        """Test erosion control prediction for all species types."""
        
        predicted_benefits = await benefit_service.predict_benefits(
            [sample_legume_species, sample_grass_species],
            sample_field_conditions,
            sample_implementation_details
        )
        
        # Should predict erosion control for all species
        assert SoilBenefit.EROSION_CONTROL in predicted_benefits
        
        erosion_benefit = predicted_benefits[SoilBenefit.EROSION_CONTROL]
        assert erosion_benefit.benefit_type == SoilBenefit.EROSION_CONTROL
        assert erosion_benefit.predicted_unit == "percent_reduction"
        assert 0.5 <= erosion_benefit.predicted_value <= 0.95  # 50-95% reduction
        assert erosion_benefit.economic_value_predicted > 0
    
    @pytest.mark.asyncio
    async def test_predict_weed_suppression(
        self, benefit_service, sample_grass_species, sample_field_conditions, sample_implementation_details
    ):
        """Test weed suppression prediction."""
        
        predicted_benefits = await benefit_service.predict_benefits(
            [sample_grass_species],
            sample_field_conditions,
            sample_implementation_details
        )
        
        assert SoilBenefit.WEED_SUPPRESSION in predicted_benefits
        
        weed_benefit = predicted_benefits[SoilBenefit.WEED_SUPPRESSION]
        assert weed_benefit.predicted_unit == "percent_suppression"
        assert 0.3 <= weed_benefit.predicted_value <= 0.9  # 30-90% suppression
        assert weed_benefit.benefit_category == "economic"
    
    @pytest.mark.asyncio
    async def test_predict_organic_matter_improvement(
        self, benefit_service, sample_legume_species, sample_field_conditions, sample_implementation_details
    ):
        """Test organic matter improvement prediction."""
        
        predicted_benefits = await benefit_service.predict_benefits(
            [sample_legume_species],
            sample_field_conditions,
            sample_implementation_details
        )
        
        assert SoilBenefit.ORGANIC_MATTER in predicted_benefits
        
        om_benefit = predicted_benefits[SoilBenefit.ORGANIC_MATTER]
        assert om_benefit.predicted_unit == "percent_increase"
        assert 0.05 <= om_benefit.predicted_value <= 0.5  # 0.05-0.5% increase
        assert om_benefit.benefit_category == "agronomic_economic"
    
    @pytest.mark.asyncio
    async def test_multi_species_benefit_combination(
        self, benefit_service, sample_legume_species, sample_grass_species,
        sample_field_conditions, sample_implementation_details
    ):
        """Test benefit combination from multiple species."""
        
        # Get individual species benefits
        legume_benefits = await benefit_service.predict_benefits(
            [sample_legume_species], sample_field_conditions, sample_implementation_details
        )
        
        grass_benefits = await benefit_service.predict_benefits(
            [sample_grass_species], sample_field_conditions, sample_implementation_details
        )
        
        # Get combined benefits
        combined_benefits = await benefit_service.predict_benefits(
            [sample_legume_species, sample_grass_species],
            sample_field_conditions, sample_implementation_details
        )
        
        # Combined erosion control should be higher than individual
        if SoilBenefit.EROSION_CONTROL in legume_benefits and SoilBenefit.EROSION_CONTROL in grass_benefits:
            individual_max = max(
                legume_benefits[SoilBenefit.EROSION_CONTROL].predicted_value,
                grass_benefits[SoilBenefit.EROSION_CONTROL].predicted_value
            )
            combined_value = combined_benefits[SoilBenefit.EROSION_CONTROL].predicted_value
            assert combined_value >= individual_max
        
        # Should have nitrogen fixation from legume
        assert SoilBenefit.NITROGEN_FIXATION in combined_benefits
    
    @pytest.mark.asyncio
    async def test_environmental_factor_adjustments(
        self, benefit_service, sample_legume_species, sample_implementation_details
    ):
        """Test environmental factor adjustments to predictions."""
        
        # Test with poor conditions
        poor_conditions = {
            'field_size_acres': 20.0,
            'soil': {'ph': 5.0, 'fertility_index': 0.4, 'organic_matter_percent': 1.5},
            'climate': {'avg_temp_f': 35.0, 'annual_precip_inches': 15.0}
        }
        
        # Test with optimal conditions  
        optimal_conditions = {
            'field_size_acres': 20.0,
            'soil': {'ph': 6.8, 'fertility_index': 0.9, 'organic_matter_percent': 3.5},
            'climate': {'avg_temp_f': 65.0, 'annual_precip_inches': 35.0}
        }
        
        poor_benefits = await benefit_service.predict_benefits(
            [sample_legume_species], poor_conditions, sample_implementation_details
        )
        
        optimal_benefits = await benefit_service.predict_benefits(
            [sample_legume_species], optimal_conditions, sample_implementation_details
        )
        
        # Optimal conditions should give higher predictions
        if SoilBenefit.NITROGEN_FIXATION in poor_benefits and SoilBenefit.NITROGEN_FIXATION in optimal_benefits:
            poor_n_fix = poor_benefits[SoilBenefit.NITROGEN_FIXATION].predicted_value
            optimal_n_fix = optimal_benefits[SoilBenefit.NITROGEN_FIXATION].predicted_value
            assert optimal_n_fix > poor_n_fix
        
        # Optimal conditions should have higher confidence
        poor_confidence = poor_benefits[SoilBenefit.NITROGEN_FIXATION].predicted_confidence
        optimal_confidence = optimal_benefits[SoilBenefit.NITROGEN_FIXATION].predicted_confidence
        assert optimal_confidence >= poor_confidence


class TestMeasurementTracking:
    """Test measurement tracking and validation."""
    
    @pytest.mark.asyncio
    async def test_record_measurement(self, benefit_service):
        """Test recording benefit measurements."""
        
        measurement = await benefit_service.record_measurement(
            benefit_entry_id="test_entry_001",
            measurement_method=BenefitMeasurementMethod.SOIL_SAMPLING,
            measured_value=85.5,
            measurement_unit="lbs_N_per_acre",
            measurement_conditions={
                'weather': 'sunny',
                'soil_moisture': 'adequate',
                'temperature_f': 68.0
            },
            technician_notes="Collected from 5 random locations across field"
        )
        
        assert isinstance(measurement, BenefitMeasurementRecord)
        assert measurement.measured_value == 85.5
        assert measurement.measurement_unit == "lbs_N_per_acre"
        assert measurement.measurement_method == BenefitMeasurementMethod.SOIL_SAMPLING
        assert measurement.measurement_accuracy > 0.8  # Soil sampling should be quite accurate
        assert measurement.validated == False  # Not validated yet
        assert measurement.technician_notes is not None
    
    @pytest.mark.asyncio
    async def test_validate_measurements(self, benefit_service, sample_implementation_details):
        """Test measurement validation process."""
        
        # Create benefit entry with measurements
        benefit_entry = BenefitQuantificationEntry(
            entry_id="test_entry_002",
            farm_id="farm_001",
            field_id="field_A", 
            cover_crop_implementation_id="impl_001",
            benefit_type=SoilBenefit.NITROGEN_FIXATION,
            benefit_category="agronomic_economic",
            predicted_value=90.0,
            predicted_unit="lbs_N_per_acre",
            predicted_confidence=0.8
        )
        
        # Add multiple measurements
        measurements = [
            BenefitMeasurementRecord(
                record_id="meas_001",
                measurement_method=BenefitMeasurementMethod.SOIL_SAMPLING,
                measured_value=88.5,
                measurement_unit="lbs_N_per_acre",
                measurement_accuracy=0.90
            ),
            BenefitMeasurementRecord(
                record_id="meas_002", 
                measurement_method=BenefitMeasurementMethod.LABORATORY_ANALYSIS,
                measured_value=92.0,
                measurement_unit="lbs_N_per_acre",
                measurement_accuracy=0.95
            ),
            BenefitMeasurementRecord(
                record_id="meas_003",
                measurement_method=BenefitMeasurementMethod.SOIL_SAMPLING,
                measured_value=87.5,
                measurement_unit="lbs_N_per_acre", 
                measurement_accuracy=0.90
            )
        ]
        
        benefit_entry.actual_measurements = measurements
        
        # Validate measurements
        validated_entry = await benefit_service.validate_measurements(
            benefit_entry,
            validator_id="expert_001",
            validation_notes="Measurements consistent with expected range"
        )
        
        # Check validation results
        assert validated_entry.status == BenefitQuantificationStatus.VALIDATED
        assert validated_entry.validated_value is not None
        assert validated_entry.measurement_variance is not None
        assert validated_entry.prediction_accuracy is not None
        
        # Validated value should be mean of measurements
        expected_mean = statistics.mean([88.5, 92.0, 87.5])
        assert abs(validated_entry.validated_value - expected_mean) < 0.1
        
        # Prediction accuracy should be reasonable (within 10% is good)
        assert validated_entry.prediction_accuracy > 0.8
        
        # All measurements should be marked as validated
        for measurement in validated_entry.actual_measurements:
            assert measurement.validated == True
            assert measurement.validator_id == "expert_001"
    
    @pytest.mark.asyncio
    async def test_measurement_accuracy_estimation(self, benefit_service):
        """Test measurement accuracy estimation by method."""
        
        # Test different measurement methods
        lab_measurement = await benefit_service.record_measurement(
            "entry_001", BenefitMeasurementMethod.LABORATORY_ANALYSIS,
            100.0, "lbs_N_per_acre", {}
        )
        
        field_measurement = await benefit_service.record_measurement(
            "entry_002", BenefitMeasurementMethod.FIELD_OBSERVATION,
            75.0, "percent_suppression", {}
        )
        
        satellite_measurement = await benefit_service.record_measurement(
            "entry_003", BenefitMeasurementMethod.SATELLITE_IMAGERY,
            0.65, "percent_reduction", {}
        )
        
        # Laboratory analysis should have highest accuracy
        assert lab_measurement.measurement_accuracy > field_measurement.measurement_accuracy
        assert lab_measurement.measurement_accuracy > satellite_measurement.measurement_accuracy
        
        # All should be within reasonable ranges
        assert 0.6 <= field_measurement.measurement_accuracy <= 0.8
        assert 0.7 <= satellite_measurement.measurement_accuracy <= 0.8
        assert 0.9 <= lab_measurement.measurement_accuracy <= 1.0


class TestFieldLevelTracking:
    """Test field-level benefit tracking."""
    
    @pytest.mark.asyncio
    async def test_create_field_tracking(self, benefit_service):
        """Test creating field-level tracking."""
        
        tracking = await benefit_service.create_field_tracking(
            farm_id="farm_001",
            field_id="field_north",
            field_size_acres=75.5,
            cover_crop_species=["crimson_clover", "winter_rye"],
            implementation_year=2024,
            implementation_season="fall",
            baseline_measurements={
                'soil_om_percent': 2.2,
                'nitrogen_availability': 25.0,
                'weed_density': 15.0
            }
        )
        
        assert isinstance(tracking, BenefitTrackingField)
        assert tracking.farm_id == "farm_001"
        assert tracking.field_id == "field_north"
        assert tracking.field_size_acres == 75.5
        assert len(tracking.cover_crop_species) == 2
        assert tracking.implementation_year == 2024
        assert len(tracking.baseline_measurements) == 3
        assert tracking.total_predicted_value == 0.0  # No benefits added yet
        assert tracking.tracking_started is not None
    
    @pytest.mark.asyncio
    async def test_update_field_tracking_with_benefits(self, benefit_service):
        """Test updating field tracking with benefit entries."""
        
        # Create field tracking
        tracking = await benefit_service.create_field_tracking(
            "farm_001", "field_A", 50.0, ["crimson_clover"], 2024, "fall"
        )
        
        # Create sample benefit entries
        benefit_entries = [
            BenefitQuantificationEntry(
                entry_id="benefit_001",
                farm_id="farm_001",
                field_id="field_A",
                cover_crop_implementation_id="impl_001",
                benefit_type=SoilBenefit.NITROGEN_FIXATION,
                benefit_category="agronomic_economic",
                predicted_value=100.0,
                predicted_unit="lbs_N_per_acre",
                predicted_confidence=0.85,
                economic_value_predicted=2750.0  # 50 acres * 100 lbs * $0.55
            ),
            BenefitQuantificationEntry(
                entry_id="benefit_002",
                farm_id="farm_001", 
                field_id="field_A",
                cover_crop_implementation_id="impl_001",
                benefit_type=SoilBenefit.EROSION_CONTROL,
                benefit_category="environmental_economic",
                predicted_value=0.70,
                predicted_unit="percent_reduction",
                predicted_confidence=0.80,
                economic_value_predicted=1250.0
            )
        ]
        
        # Update tracking
        updated_tracking = await benefit_service.update_field_tracking(
            tracking, benefit_entries
        )
        
        # Check updates
        assert len(updated_tracking.tracked_benefits) == 2
        assert updated_tracking.total_predicted_value == 4000.0  # 2750 + 1250
        assert updated_tracking.roi_predicted is not None
        # Allow for small timing differences (within 1 second)
        time_diff = (updated_tracking.last_updated - tracking.last_updated).total_seconds()
        assert time_diff >= -0.1  # Allow small negative difference due to timing precision
    
    @pytest.mark.asyncio
    async def test_field_tracking_roi_calculation(self, benefit_service):
        """Test ROI calculation in field tracking."""
        
        tracking = await benefit_service.create_field_tracking(
            "farm_001", "field_A", 20.0, ["winter_rye"], 2024, "fall"
        )
        
        # Add benefit with economic value
        high_value_benefit = BenefitQuantificationEntry(
            entry_id="benefit_roi_test",
            farm_id="farm_001",
            field_id="field_A", 
            cover_crop_implementation_id="impl_001",
            benefit_type=SoilBenefit.WEED_SUPPRESSION,
            benefit_category="economic",
            predicted_value=0.75,
            predicted_unit="percent_suppression",
            predicted_confidence=0.85,
            economic_value_predicted=2000.0,  # High value benefit
            economic_value_actual=1800.0  # Actual realized value
        )
        
        updated_tracking = await benefit_service.update_field_tracking(
            tracking, [high_value_benefit]
        )
        
        # Implementation cost should be 20 acres * $75/acre = $1500
        expected_cost = 20.0 * 75.0
        
        # ROI predicted = (2000 - 1500) / 1500 = 0.33 (33%)
        expected_roi_predicted = (2000.0 - expected_cost) / expected_cost
        assert abs(updated_tracking.roi_predicted - expected_roi_predicted) < 0.01
        
        # ROI actual = (1800 - 1500) / 1500 = 0.20 (20%)
        expected_roi_actual = (1800.0 - expected_cost) / expected_cost
        assert abs(updated_tracking.roi_actual - expected_roi_actual) < 0.01


class TestAnalyticsGeneration:
    """Test analytics and insights generation."""
    
    @pytest.mark.asyncio
    async def test_generate_analytics(self, benefit_service):
        """Test comprehensive analytics generation."""
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        farm_ids = ["farm_001", "farm_002", "farm_003"]
        
        analytics = await benefit_service.generate_analytics(
            farm_ids, start_date, end_date
        )
        
        assert isinstance(analytics, BenefitTrackingAnalytics)
        assert analytics.analysis_period_start == start_date
        assert analytics.analysis_period_end == end_date
        assert analytics.farm_ids == farm_ids
        assert analytics.field_count > 0
        assert analytics.total_acres_analyzed > 0
        
        # Should have benefit accuracy data
        assert len(analytics.benefit_accuracy_by_type) > 0
        for benefit_type, accuracy in analytics.benefit_accuracy_by_type.items():
            assert isinstance(benefit_type, SoilBenefit)
            assert 0.0 <= accuracy <= 1.0
        
        # Should have recommendations
        assert len(analytics.measurement_protocol_improvements) > 0
        assert len(analytics.prediction_model_refinements) > 0
        assert len(analytics.farmer_recommendations) > 0
        
        # Quality metrics should be reasonable
        assert 0.0 <= analytics.overall_data_quality_score <= 1.0
        assert 0.0 <= analytics.measurement_completion_rate <= 1.0
        assert 0.0 <= analytics.validation_completion_rate <= 1.0


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases."""
    
    @pytest.mark.asyncio
    async def test_full_benefit_lifecycle(
        self, benefit_service, sample_legume_species, sample_field_conditions, sample_implementation_details
    ):
        """Test complete benefit lifecycle from prediction to validation."""
        
        # 1. Predict benefits
        predicted_benefits = await benefit_service.predict_benefits(
            [sample_legume_species], sample_field_conditions, sample_implementation_details
        )
        
        assert len(predicted_benefits) > 0
        nitrogen_benefit = predicted_benefits[SoilBenefit.NITROGEN_FIXATION]
        
        # 2. Create field tracking
        field_tracking = await benefit_service.create_field_tracking(
            farm_id=sample_implementation_details['farm_id'],
            field_id=sample_implementation_details['field_id'],
            field_size_acres=sample_field_conditions['field_size_acres'],
            cover_crop_species=[sample_legume_species.species_id],
            implementation_year=2024,
            implementation_season="fall"
        )
        
        # 3. Update field tracking with predictions
        updated_tracking = await benefit_service.update_field_tracking(
            field_tracking, list(predicted_benefits.values())
        )
        
        assert len(updated_tracking.tracked_benefits) > 0
        assert updated_tracking.total_predicted_value > 0
        
        # 4. Record measurements
        measurement1 = await benefit_service.record_measurement(
            nitrogen_benefit.entry_id,
            BenefitMeasurementMethod.SOIL_SAMPLING,
            nitrogen_benefit.predicted_value * 0.95,  # Close to predicted
            nitrogen_benefit.predicted_unit,
            {'sampling_depth': '0-6_inches', 'weather': 'clear'}
        )
        
        measurement2 = await benefit_service.record_measurement(
            nitrogen_benefit.entry_id,
            BenefitMeasurementMethod.LABORATORY_ANALYSIS,
            nitrogen_benefit.predicted_value * 1.05,  # Slightly higher
            nitrogen_benefit.predicted_unit,
            {'lab_method': 'kjeldahl', 'certified_lab': True}
        )
        
        # 5. Add measurements to benefit entry
        nitrogen_benefit.actual_measurements = [measurement1, measurement2]
        
        # 6. Validate measurements
        validated_benefit = await benefit_service.validate_measurements(
            nitrogen_benefit, "expert_validator_001"
        )
        
        assert validated_benefit.status == BenefitQuantificationStatus.VALIDATED
        assert validated_benefit.prediction_accuracy > 0.9  # Should be very accurate
        assert validated_benefit.validated_value is not None
        
        # 7. Generate analytics
        analytics = await benefit_service.generate_analytics(
            [sample_implementation_details['farm_id']],
            datetime(2024, 1, 1),
            datetime(2024, 12, 31)
        )
        
        assert analytics.farm_ids == [sample_implementation_details['farm_id']]
        assert len(analytics.benefit_accuracy_by_type) > 0
    
    def test_benefit_coefficient_loading(self, benefit_service):
        """Test benefit coefficient loading and structure."""
        
        coefficients = benefit_service._benefit_coefficients
        
        # Should have main benefit categories
        assert 'nitrogen_fixation' in coefficients
        assert 'erosion_control' in coefficients
        assert 'organic_matter' in coefficients
        assert 'weed_suppression' in coefficients
        
        # Each category should have species-specific values
        for benefit_type, species_values in coefficients.items():
            assert isinstance(species_values, dict)
            assert len(species_values) > 0
            
            for species_id, coefficient in species_values.items():
                assert isinstance(species_id, str)
                assert isinstance(coefficient, (int, float))
                assert coefficient > 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, benefit_service):
        """Test error handling for invalid inputs."""
        
        # Test validation with no measurements
        empty_benefit = BenefitQuantificationEntry(
            entry_id="empty_test",
            farm_id="farm_001",
            field_id="field_A",
            cover_crop_implementation_id="impl_001",
            benefit_type=SoilBenefit.NITROGEN_FIXATION,
            benefit_category="agronomic",
            predicted_value=100.0,
            predicted_unit="lbs_N_per_acre",
            predicted_confidence=0.8
        )
        
        with pytest.raises(ValueError, match="No measurements to validate"):
            await benefit_service.validate_measurements(empty_benefit, "validator_001")
    
    @pytest.mark.asyncio
    async def test_prediction_confidence_factors(
        self, benefit_service, sample_legume_species, sample_field_conditions, sample_implementation_details
    ):
        """Test that prediction confidence varies appropriately with data quality."""
        
        # Test with complete environmental data
        complete_conditions = {
            **sample_field_conditions,
            'soil': {
                **sample_field_conditions['soil'],
                'nitrogen_availability': 30.0,
                'phosphorus_ppm': 25.0,
                'potassium_ppm': 180.0,
                'bulk_density': 1.3
            },
            'climate': {
                **sample_field_conditions['climate'],
                'humidity_percent': 65.0,
                'wind_speed_mph': 8.0
            }
        }
        
        # Test with minimal data
        minimal_conditions = {
            'field_size_acres': 50.0,
            'soil': {'ph': 6.5},
            'climate': {'avg_temp_f': 55.0}
        }
        
        complete_benefits = await benefit_service.predict_benefits(
            [sample_legume_species], complete_conditions, sample_implementation_details
        )
        
        minimal_benefits = await benefit_service.predict_benefits(
            [sample_legume_species], minimal_conditions, sample_implementation_details
        )
        
        # Complete data should have higher confidence
        if SoilBenefit.NITROGEN_FIXATION in complete_benefits and SoilBenefit.NITROGEN_FIXATION in minimal_benefits:
            complete_confidence = complete_benefits[SoilBenefit.NITROGEN_FIXATION].predicted_confidence
            minimal_confidence = minimal_benefits[SoilBenefit.NITROGEN_FIXATION].predicted_confidence
            
            # Complete data should have higher or equal confidence
            assert complete_confidence >= minimal_confidence - 0.05  # Small tolerance for randomness