"""
Unit tests for NutrientModelingService

Tests cover:
- Nutrient uptake curve calculations for different crops
- Leaching loss predictions under various conditions
- Volatilization loss predictions
- Immobilization loss predictions
- Overall nutrient efficiency calculations
- Edge cases and agricultural validation
"""

import pytest
from datetime import date, datetime
from typing import Dict, Any

from ..src.services.nutrient_modeling_service import NutrientModelingService
from ..src.models.nutrient_modeling_models import (
    NutrientUptakeRequest,
    CropNutrientRequirements,
    SoilCharacteristics,
    WeatherConditions,
    ApplicationDetails,
    LeachingModelInputs,
    VolatilizationModelInputs,
    ImmobilizationModelInputs,
    LossPrediction,
    CropType,
    GrowthStage,
    NutrientType,
    LossType,
    SoilTexture,
    DrainageClass,
    FertilizerFormulation,
    ApplicationMethodType,
)


@pytest.fixture
def service():
    """Create NutrientModelingService instance."""
    return NutrientModelingService()


@pytest.fixture
def corn_soil_sandy():
    """Sandy loam soil characteristics."""
    return SoilCharacteristics(
        texture=SoilTexture.SANDY_LOAM,
        drainage_class=DrainageClass.WELL_DRAINED,
        sand_percent=65.0,
        silt_percent=25.0,
        clay_percent=10.0,
        organic_matter_percent=2.5,
        cec_meq_per_100g=8.0,
        ph=6.5,
        bulk_density_g_cm3=1.5,
        field_capacity_percent=22.0,
        wilting_point_percent=10.0,
        current_moisture_percent=18.0
    )


@pytest.fixture
def corn_soil_clay():
    """Clay loam soil characteristics."""
    return SoilCharacteristics(
        texture=SoilTexture.CLAY_LOAM,
        drainage_class=DrainageClass.MODERATELY_WELL_DRAINED,
        sand_percent=30.0,
        silt_percent=35.0,
        clay_percent=35.0,
        organic_matter_percent=4.0,
        cec_meq_per_100g=18.0,
        ph=6.8,
        bulk_density_g_cm3=1.3,
        field_capacity_percent=35.0,
        wilting_point_percent=18.0,
        current_moisture_percent=28.0
    )


@pytest.fixture
def favorable_weather():
    """Favorable weather conditions (cool, humid)."""
    return WeatherConditions(
        temperature_f=65.0,
        relative_humidity_percent=70.0,
        rainfall_inches=0.5,
        rainfall_intensity="light",
        wind_speed_mph=5.0,
        evapotranspiration_inches=0.15,
        days_since_rain=2,
        days_to_next_rain=3
    )


@pytest.fixture
def unfavorable_weather():
    """Unfavorable weather for volatilization (hot, dry, windy)."""
    return WeatherConditions(
        temperature_f=85.0,
        relative_humidity_percent=35.0,
        rainfall_inches=0.0,
        wind_speed_mph=15.0,
        evapotranspiration_inches=0.30,
        days_since_rain=10,
        days_to_next_rain=7
    )


@pytest.fixture
def heavy_rain_weather():
    """Heavy rainfall conditions for leaching."""
    return WeatherConditions(
        temperature_f=70.0,
        relative_humidity_percent=85.0,
        rainfall_inches=4.5,
        rainfall_intensity="heavy",
        wind_speed_mph=8.0,
        evapotranspiration_inches=0.10,
        days_since_rain=0,
        days_to_next_rain=1
    )


@pytest.fixture
def corn_v9_requirements():
    """Corn at V9 growth stage requirements."""
    return CropNutrientRequirements(
        crop_type=CropType.CORN,
        growth_stage=GrowthStage.V9,
        yield_goal_bu_acre=200.0,
        variety="Pioneer P1234",
        total_n_needed_lbs_acre=220.0,
        total_p2o5_needed_lbs_acre=80.0,
        total_k2o_needed_lbs_acre=150.0,
        days_after_planting=49,
        total_growing_days=120
    )


@pytest.fixture
def broadcast_urea_application():
    """Broadcast urea application details."""
    return ApplicationDetails(
        application_method=ApplicationMethodType.BROADCAST,
        fertilizer_formulation=FertilizerFormulation.UREA,
        application_date=date(2025, 5, 15),
        hours_since_application=24.0,
        incorporation_depth_inches=None,
        hours_until_incorporation=None,
        n_applied_lbs_acre=150.0,
        p2o5_applied_lbs_acre=0.0,
        k2o_applied_lbs_acre=0.0
    )


@pytest.fixture
def injected_anhydrous_application():
    """Injected anhydrous ammonia application."""
    return ApplicationDetails(
        application_method=ApplicationMethodType.INJECTED,
        fertilizer_formulation=FertilizerFormulation.ANHYDROUS_AMMONIA,
        application_date=date(2025, 5, 15),
        hours_since_application=24.0,
        incorporation_depth_inches=6.0,
        hours_until_incorporation=0.0,
        n_applied_lbs_acre=150.0,
        p2o5_applied_lbs_acre=0.0,
        k2o_applied_lbs_acre=0.0
    )


# Uptake Curve Tests

@pytest.mark.asyncio
async def test_corn_nitrogen_uptake_curve(service):
    """Test corn nitrogen uptake curve generation."""
    curve = await service.calculate_nutrient_uptake_curve(
        crop_type=CropType.CORN,
        growth_stage=GrowthStage.V9,
        nutrient_type=NutrientType.NITROGEN,
        total_nutrient_need_lbs_acre=220.0,
        yield_goal=200.0
    )

    assert curve.nutrient_type == NutrientType.NITROGEN
    assert curve.crop_type == CropType.CORN
    assert curve.total_uptake_lbs_acre == 220.0
    assert len(curve.uptake_points) > 0

    # Check that uptake is progressive
    previous_cumulative = 0.0
    for point in curve.uptake_points:
        assert point.cumulative_uptake_percent >= previous_cumulative
        previous_cumulative = point.cumulative_uptake_percent

    # Final uptake should be 100%
    assert curve.uptake_points[-1].cumulative_uptake_percent == 100.0

    # Peak uptake should be during rapid growth (V9-R1)
    assert curve.peak_uptake_stage in [GrowthStage.V9, GrowthStage.V12, GrowthStage.VT, GrowthStage.R1]

    # Peak rate should be reasonable (typically 3-5 lbs N/acre/day for corn)
    assert 2.0 <= curve.peak_uptake_rate_lbs_acre_day <= 8.0


@pytest.mark.asyncio
async def test_corn_phosphorus_uptake_curve(service):
    """Test corn phosphorus uptake curve."""
    curve = await service.calculate_nutrient_uptake_curve(
        crop_type=CropType.CORN,
        growth_stage=GrowthStage.V6,
        nutrient_type=NutrientType.PHOSPHORUS,
        total_nutrient_need_lbs_acre=80.0,
        yield_goal=200.0
    )

    assert curve.nutrient_type == NutrientType.PHOSPHORUS
    assert curve.total_uptake_lbs_acre == 80.0
    assert len(curve.uptake_points) > 0

    # P uptake should be earlier than N (more at early growth stages)
    early_stages_pct = 0.0
    for point in curve.uptake_points:
        if point.growth_stage in [GrowthStage.VE, GrowthStage.V3, GrowthStage.V6]:
            early_stages_pct = point.cumulative_uptake_percent

    # Should have >10% uptake by V6
    assert early_stages_pct > 10.0


@pytest.mark.asyncio
async def test_corn_potassium_uptake_curve(service):
    """Test corn potassium uptake curve."""
    curve = await service.calculate_nutrient_uptake_curve(
        crop_type=CropType.CORN,
        growth_stage=GrowthStage.VT,
        nutrient_type=NutrientType.POTASSIUM,
        total_nutrient_need_lbs_acre=150.0,
        yield_goal=200.0
    )

    assert curve.nutrient_type == NutrientType.POTASSIUM
    assert curve.total_uptake_lbs_acre == 150.0

    # K uptake is heaviest in vegetative stages
    # By VT, should have >80% of K uptake complete
    vt_uptake_pct = 0.0
    for point in curve.uptake_points:
        if point.growth_stage == GrowthStage.VT:
            vt_uptake_pct = point.cumulative_uptake_percent

    assert vt_uptake_pct > 80.0


@pytest.mark.asyncio
async def test_soybean_nitrogen_uptake_curve(service):
    """Test soybean nitrogen uptake curve."""
    curve = await service.calculate_nutrient_uptake_curve(
        crop_type=CropType.SOYBEAN,
        growth_stage=GrowthStage.VEGETATIVE_MID,
        nutrient_type=NutrientType.NITROGEN,
        total_nutrient_need_lbs_acre=100.0,  # Soybeans fix most N
        yield_goal=60.0
    )

    assert curve.crop_type == CropType.SOYBEAN
    assert curve.total_uptake_lbs_acre == 100.0
    assert len(curve.uptake_points) > 0


# Leaching Loss Tests

@pytest.mark.asyncio
async def test_leaching_sandy_soil_heavy_rain(service, corn_soil_sandy, heavy_rain_weather):
    """Test leaching on sandy soil with heavy rain - should be high risk."""
    inputs = LeachingModelInputs(
        soil_characteristics=corn_soil_sandy,
        weather_conditions=heavy_rain_weather,
        nutrient_type=NutrientType.NITROGEN,
        applied_amount_lbs_acre=150.0,
        days_since_application=3.0
    )

    prediction = await service.predict_leaching_loss(inputs)

    assert prediction.loss_type == LossType.LEACHING
    assert prediction.nutrient_type == NutrientType.NITROGEN

    # Sandy soil + heavy rain = significant leaching
    assert prediction.loss_percent > 8.0
    assert prediction.risk_level in ["moderate", "high", "very_high"]
    assert prediction.loss_amount_lbs_acre > 12.0

    # Should have mitigation recommendations
    assert len(prediction.mitigation_recommendations) > 0


@pytest.mark.asyncio
async def test_leaching_clay_soil_heavy_rain(service, corn_soil_clay, heavy_rain_weather):
    """Test leaching on clay soil with heavy rain - should be lower risk."""
    inputs = LeachingModelInputs(
        soil_characteristics=corn_soil_clay,
        weather_conditions=heavy_rain_weather,
        nutrient_type=NutrientType.NITROGEN,
        applied_amount_lbs_acre=150.0,
        days_since_application=3.0
    )

    prediction = await service.predict_leaching_loss(inputs)

    # Clay soil + heavy rain = moderate leaching (less than sandy)
    assert prediction.loss_percent < 20.0
    assert prediction.risk_level in ["low", "moderate", "high"]


@pytest.mark.asyncio
async def test_leaching_no_rain(service, corn_soil_sandy, favorable_weather):
    """Test leaching with minimal rain - should be low risk."""
    inputs = LeachingModelInputs(
        soil_characteristics=corn_soil_sandy,
        weather_conditions=favorable_weather,
        nutrient_type=NutrientType.NITROGEN,
        applied_amount_lbs_acre=150.0,
        days_since_application=1.0
    )

    prediction = await service.predict_leaching_loss(inputs)

    # Minimal rain = low leaching even on sandy soil
    assert prediction.loss_percent < 10.0
    assert prediction.risk_level in ["low", "moderate"]


@pytest.mark.asyncio
async def test_leaching_phosphorus_vs_nitrogen(service, corn_soil_sandy, heavy_rain_weather):
    """Test that phosphorus leaches much less than nitrogen."""
    n_inputs = LeachingModelInputs(
        soil_characteristics=corn_soil_sandy,
        weather_conditions=heavy_rain_weather,
        nutrient_type=NutrientType.NITROGEN,
        applied_amount_lbs_acre=150.0,
        days_since_application=3.0
    )

    p_inputs = LeachingModelInputs(
        soil_characteristics=corn_soil_sandy,
        weather_conditions=heavy_rain_weather,
        nutrient_type=NutrientType.PHOSPHORUS,
        applied_amount_lbs_acre=80.0,
        days_since_application=3.0
    )

    n_prediction = await service.predict_leaching_loss(n_inputs)
    p_prediction = await service.predict_leaching_loss(p_inputs)

    # P should leach ~10% as much as N (bound to soil particles)
    assert p_prediction.loss_percent < n_prediction.loss_percent * 0.2


# Volatilization Loss Tests

@pytest.mark.asyncio
async def test_volatilization_broadcast_urea_hot_dry(service, corn_soil_sandy, unfavorable_weather):
    """Test volatilization of broadcast urea in hot, dry conditions - should be high risk."""
    inputs = VolatilizationModelInputs(
        fertilizer_formulation=FertilizerFormulation.UREA,
        application_method=ApplicationMethodType.BROADCAST,
        weather_conditions=unfavorable_weather,
        soil_characteristics=corn_soil_sandy,
        applied_n_lbs_acre=150.0,
        hours_since_application=48.0,
        hours_until_incorporation_or_rain=None
    )

    prediction = await service.predict_volatilization_loss(inputs)

    assert prediction.loss_type == LossType.VOLATILIZATION
    assert prediction.nutrient_type == NutrientType.NITROGEN

    # Worst case scenario for volatilization
    assert prediction.loss_percent > 10.0
    assert prediction.risk_level in ["high", "very_high"]

    # Should recommend incorporation
    assert any("incorporat" in rec.lower() for rec in prediction.mitigation_recommendations)


@pytest.mark.asyncio
async def test_volatilization_injected_anhydrous(service, corn_soil_sandy, unfavorable_weather):
    """Test volatilization of injected anhydrous - should be low risk."""
    inputs = VolatilizationModelInputs(
        fertilizer_formulation=FertilizerFormulation.ANHYDROUS_AMMONIA,
        application_method=ApplicationMethodType.INJECTED,
        weather_conditions=unfavorable_weather,
        soil_characteristics=corn_soil_sandy,
        applied_n_lbs_acre=150.0,
        hours_since_application=24.0,
        hours_until_incorporation_or_rain=0.0
    )

    prediction = await service.predict_volatilization_loss(inputs)

    # Injected ammonia has very low volatilization
    assert prediction.loss_percent < 10.0
    assert prediction.risk_level in ["low", "moderate"]


@pytest.mark.asyncio
async def test_volatilization_urea_with_rain(service, corn_soil_sandy, favorable_weather):
    """Test that rain/incorporation within 24h greatly reduces volatilization."""
    # Without rain/incorporation
    inputs_no_rain = VolatilizationModelInputs(
        fertilizer_formulation=FertilizerFormulation.UREA,
        application_method=ApplicationMethodType.BROADCAST,
        weather_conditions=favorable_weather,
        soil_characteristics=corn_soil_sandy,
        applied_n_lbs_acre=150.0,
        hours_since_application=12.0,
        hours_until_incorporation_or_rain=None
    )

    # With rain in 12 hours
    inputs_with_rain = VolatilizationModelInputs(
        fertilizer_formulation=FertilizerFormulation.UREA,
        application_method=ApplicationMethodType.BROADCAST,
        weather_conditions=favorable_weather,
        soil_characteristics=corn_soil_sandy,
        applied_n_lbs_acre=150.0,
        hours_since_application=12.0,
        hours_until_incorporation_or_rain=12.0
    )

    pred_no_rain = await service.predict_volatilization_loss(inputs_no_rain)
    pred_with_rain = await service.predict_volatilization_loss(inputs_with_rain)

    # Rain should reduce loss significantly
    assert pred_with_rain.loss_percent < pred_no_rain.loss_percent * 0.6


@pytest.mark.asyncio
async def test_volatilization_temperature_effect(service, corn_soil_sandy):
    """Test that temperature strongly affects volatilization."""
    # Cool conditions
    cool_weather = WeatherConditions(
        temperature_f=50.0,
        relative_humidity_percent=70.0,
        rainfall_inches=0.0,
        wind_speed_mph=5.0
    )

    # Hot conditions
    hot_weather = WeatherConditions(
        temperature_f=90.0,
        relative_humidity_percent=70.0,
        rainfall_inches=0.0,
        wind_speed_mph=5.0
    )

    inputs_cool = VolatilizationModelInputs(
        fertilizer_formulation=FertilizerFormulation.UREA,
        application_method=ApplicationMethodType.BROADCAST,
        weather_conditions=cool_weather,
        soil_characteristics=corn_soil_sandy,
        applied_n_lbs_acre=150.0,
        hours_since_application=24.0
    )

    inputs_hot = VolatilizationModelInputs(
        fertilizer_formulation=FertilizerFormulation.UREA,
        application_method=ApplicationMethodType.BROADCAST,
        weather_conditions=hot_weather,
        soil_characteristics=corn_soil_sandy,
        applied_n_lbs_acre=150.0,
        hours_since_application=24.0
    )

    pred_cool = await service.predict_volatilization_loss(inputs_cool)
    pred_hot = await service.predict_volatilization_loss(inputs_hot)

    # Hot should have significantly more loss
    assert pred_hot.loss_percent > pred_cool.loss_percent * 1.5


# Immobilization Loss Tests

@pytest.mark.asyncio
async def test_immobilization_high_cn_ratio(service, corn_soil_sandy, favorable_weather):
    """Test immobilization with high C:N ratio residue - should have significant immobilization."""
    inputs = ImmobilizationModelInputs(
        soil_characteristics=corn_soil_sandy,
        weather_conditions=favorable_weather,
        residue_cn_ratio=50.0,  # High C:N (e.g., corn stover)
        residue_amount_tons_acre=4.0,
        applied_n_lbs_acre=150.0,
        microbial_activity_level="high"
    )

    prediction = await service.predict_immobilization_loss(inputs)

    assert prediction.loss_type == LossType.IMMOBILIZATION
    assert prediction.nutrient_type == NutrientType.NITROGEN

    # High C:N should cause significant immobilization
    assert prediction.loss_percent > 10.0
    assert prediction.risk_level in ["moderate", "high", "very_high"]

    # Should recommend additional N or delay
    assert len(prediction.mitigation_recommendations) > 0


@pytest.mark.asyncio
async def test_immobilization_low_cn_ratio(service, corn_soil_sandy, favorable_weather):
    """Test immobilization with low C:N ratio - should have minimal immobilization."""
    inputs = ImmobilizationModelInputs(
        soil_characteristics=corn_soil_sandy,
        weather_conditions=favorable_weather,
        residue_cn_ratio=15.0,  # Low C:N (e.g., legume residue)
        residue_amount_tons_acre=2.0,
        applied_n_lbs_acre=150.0,
        microbial_activity_level="medium"
    )

    prediction = await service.predict_immobilization_loss(inputs)

    # Low C:N should have minimal or no immobilization
    assert prediction.loss_percent < 5.0
    assert prediction.risk_level in ["low", "moderate"]


@pytest.mark.asyncio
async def test_immobilization_temperature_effect(service, corn_soil_sandy):
    """Test that warm temperatures increase immobilization."""
    # Cool weather (low microbial activity)
    cool_weather = WeatherConditions(
        temperature_f=50.0,
        relative_humidity_percent=60.0,
        rainfall_inches=0.5
    )

    # Warm weather (high microbial activity)
    warm_weather = WeatherConditions(
        temperature_f=75.0,
        relative_humidity_percent=60.0,
        rainfall_inches=0.5
    )

    inputs_cool = ImmobilizationModelInputs(
        soil_characteristics=corn_soil_sandy,
        weather_conditions=cool_weather,
        residue_cn_ratio=40.0,
        applied_n_lbs_acre=150.0,
        microbial_activity_level="medium"
    )

    inputs_warm = ImmobilizationModelInputs(
        soil_characteristics=corn_soil_sandy,
        weather_conditions=warm_weather,
        residue_cn_ratio=40.0,
        applied_n_lbs_acre=150.0,
        microbial_activity_level="medium"
    )

    pred_cool = await service.predict_immobilization_loss(inputs_cool)
    pred_warm = await service.predict_immobilization_loss(inputs_warm)

    # Warm should have more immobilization (more microbial activity)
    assert pred_warm.loss_percent >= pred_cool.loss_percent


# Nutrient Efficiency Tests

@pytest.mark.asyncio
async def test_nutrient_efficiency_calculation(service):
    """Test nutrient use efficiency calculation."""
    # Create mock loss predictions
    loss_predictions = [
        LossPrediction(
            loss_type=LossType.LEACHING,
            nutrient_type=NutrientType.NITROGEN,
            loss_amount_lbs_acre=20.0,
            loss_percent=13.3,
            risk_level="moderate",
            confidence_score=0.8,
            primary_factors=["Moderate rainfall"],
            mitigation_recommendations=[]
        ),
        LossPrediction(
            loss_type=LossType.VOLATILIZATION,
            nutrient_type=NutrientType.NITROGEN,
            loss_amount_lbs_acre=15.0,
            loss_percent=10.0,
            risk_level="moderate",
            confidence_score=0.75,
            primary_factors=["Surface application"],
            mitigation_recommendations=[]
        )
    ]

    efficiency = await service.calculate_nutrient_efficiency(
        nutrient_type=NutrientType.NITROGEN,
        applied_lbs_acre=150.0,
        crop_uptake_lbs_acre=100.0,
        loss_predictions=loss_predictions,
        yield_goal=200.0
    )

    assert efficiency.nutrient_type == NutrientType.NITROGEN
    assert efficiency.applied_lbs_acre == 150.0
    assert efficiency.crop_uptake_lbs_acre == 100.0
    assert efficiency.total_losses_lbs_acre == 35.0  # 20 + 15
    assert efficiency.remaining_in_soil_lbs_acre == 15.0  # 150 - 100 - 35

    # Uptake efficiency = 100/150 = 66.7%
    assert 66.0 <= efficiency.uptake_efficiency_percent <= 67.0

    # Recovery efficiency = (100 + 15)/150 = 76.7%
    assert 76.0 <= efficiency.recovery_efficiency_percent <= 77.0

    # Loss breakdown should sum to total losses
    breakdown_sum = sum(efficiency.loss_breakdown.values())
    assert abs(breakdown_sum - 35.0) < 0.01


# Full Integration Tests

@pytest.mark.asyncio
async def test_predict_nutrient_fate_corn_v9(
    service,
    corn_v9_requirements,
    corn_soil_sandy,
    favorable_weather,
    broadcast_urea_application
):
    """Test complete nutrient fate prediction for corn at V9."""
    request = NutrientUptakeRequest(
        request_id="test_001",
        crop_requirements=corn_v9_requirements,
        soil_characteristics=corn_soil_sandy,
        weather_conditions=favorable_weather,
        application_details=broadcast_urea_application,
        residue_cn_ratio=35.0,
        microbial_activity_level="medium"
    )

    prediction = await service.predict_nutrient_fate(request)

    # Basic structure checks
    assert prediction.request_id == "test_001"
    assert len(prediction.uptake_curves) > 0
    assert len(prediction.loss_predictions) > 0
    assert len(prediction.efficiency_analyses) > 0

    # Should have N uptake curve
    n_curve = None
    for curve in prediction.uptake_curves:
        if curve.nutrient_type == NutrientType.NITROGEN:
            n_curve = curve
    assert n_curve is not None

    # Should have predictions for multiple loss pathways
    loss_types = set()
    for loss_pred in prediction.loss_predictions:
        loss_types.add(loss_pred.loss_type)
    assert LossType.LEACHING in loss_types
    assert LossType.VOLATILIZATION in loss_types
    assert LossType.IMMOBILIZATION in loss_types

    # Should have optimization recommendations
    assert len(prediction.optimization_recommendations) > 0

    # Confidence should be reasonable
    assert 0.5 <= prediction.overall_confidence <= 1.0

    # Should have agricultural sources
    assert len(prediction.agricultural_sources) > 0


@pytest.mark.asyncio
async def test_predict_nutrient_fate_worst_case(
    service,
    corn_v9_requirements,
    corn_soil_sandy,
    unfavorable_weather,
    broadcast_urea_application
):
    """Test worst-case scenario: broadcast urea, hot/dry weather, sandy soil."""
    # Modify weather to have heavy rain too
    bad_weather = WeatherConditions(
        temperature_f=85.0,
        relative_humidity_percent=30.0,
        rainfall_inches=4.0,  # Heavy rain after hot period
        wind_speed_mph=15.0
    )

    request = NutrientUptakeRequest(
        request_id="test_worst",
        crop_requirements=corn_v9_requirements,
        soil_characteristics=corn_soil_sandy,
        weather_conditions=bad_weather,
        application_details=broadcast_urea_application,
        residue_cn_ratio=45.0,  # High C:N
        microbial_activity_level="high"
    )

    prediction = await service.predict_nutrient_fate(request)

    # Should identify high loss risk
    assert prediction.total_loss_risk in ["high", "very_high"]

    # Should have multiple high-risk loss pathways
    high_risk_count = 0
    for loss_pred in prediction.loss_predictions:
        if loss_pred.risk_level in ["high", "very_high"]:
            high_risk_count = high_risk_count + 1
    assert high_risk_count >= 2

    # Efficiency should be low
    for efficiency in prediction.efficiency_analyses:
        if efficiency.nutrient_type == NutrientType.NITROGEN:
            # In worst case, uptake efficiency < 60%
            assert efficiency.uptake_efficiency_percent < 70.0


@pytest.mark.asyncio
async def test_predict_nutrient_fate_best_case(
    service,
    corn_v9_requirements,
    corn_soil_clay,
    favorable_weather,
    injected_anhydrous_application
):
    """Test best-case scenario: injected anhydrous, clay soil, favorable weather."""
    request = NutrientUptakeRequest(
        request_id="test_best",
        crop_requirements=corn_v9_requirements,
        soil_characteristics=corn_soil_clay,
        weather_conditions=favorable_weather,
        application_details=injected_anhydrous_application,
        residue_cn_ratio=18.0,  # Low C:N (legume residue)
        microbial_activity_level="low"
    )

    prediction = await service.predict_nutrient_fate(request)

    # Should identify low to moderate loss risk
    assert prediction.total_loss_risk in ["low", "moderate"]

    # Most loss pathways should be low risk
    low_risk_count = 0
    for loss_pred in prediction.loss_predictions:
        if loss_pred.risk_level in ["low", "moderate"]:
            low_risk_count = low_risk_count + 1
    assert low_risk_count >= 2

    # Overall efficiency should be reasonable (best practices reduce losses)
    # Note: Even in best case, ~30-40% efficiency is typical due to timing
    assert prediction.overall_efficiency_score > 0.3


# Agricultural Validation Tests

@pytest.mark.asyncio
async def test_corn_n_uptake_realistic_values(service):
    """Validate that corn N uptake values are agriculturally realistic."""
    curve = await service.calculate_nutrient_uptake_curve(
        crop_type=CropType.CORN,
        growth_stage=GrowthStage.V12,
        nutrient_type=NutrientType.NITROGEN,
        total_nutrient_need_lbs_acre=220.0,
        yield_goal=200.0
    )

    # Check V9-R1 period has highest uptake (this is critical period)
    peak_found = False
    for point in curve.uptake_points:
        if point.growth_stage in [GrowthStage.V9, GrowthStage.V12, GrowthStage.VT, GrowthStage.R1]:
            # Daily rates during rapid growth should be 3-5 lbs/acre/day
            if point.daily_uptake_rate_lbs_acre > 2.5:
                peak_found = True

    assert peak_found, "Peak N uptake not found during critical V9-R1 period"


@pytest.mark.asyncio
async def test_leaching_loss_realistic_range(service, corn_soil_sandy, heavy_rain_weather):
    """Validate leaching losses are in realistic range."""
    inputs = LeachingModelInputs(
        soil_characteristics=corn_soil_sandy,
        weather_conditions=heavy_rain_weather,
        nutrient_type=NutrientType.NITROGEN,
        applied_amount_lbs_acre=150.0,
        days_since_application=5.0
    )

    prediction = await service.predict_leaching_loss(inputs)

    # Leaching losses should be < 50% even in worst case
    # Literature shows 15-40% for sandy soils with heavy rain
    assert prediction.loss_percent <= 50.0
    assert prediction.loss_percent >= 0.0


@pytest.mark.asyncio
async def test_volatilization_loss_realistic_range(service, corn_soil_sandy, unfavorable_weather):
    """Validate volatilization losses match agricultural research."""
    inputs = VolatilizationModelInputs(
        fertilizer_formulation=FertilizerFormulation.UREA,
        application_method=ApplicationMethodType.BROADCAST,
        weather_conditions=unfavorable_weather,
        soil_characteristics=corn_soil_sandy,
        applied_n_lbs_acre=150.0,
        hours_since_application=72.0
    )

    prediction = await service.predict_volatilization_loss(inputs)

    # Literature shows broadcast urea can lose 15-30% in unfavorable conditions
    # Should not exceed 50%
    assert prediction.loss_percent <= 50.0
    assert prediction.loss_percent >= 0.0


# Edge Case Tests

@pytest.mark.asyncio
async def test_zero_nutrient_application(service, corn_v9_requirements, corn_soil_sandy, favorable_weather):
    """Test handling of zero nutrient application."""
    zero_application = ApplicationDetails(
        application_method=ApplicationMethodType.BROADCAST,
        fertilizer_formulation=FertilizerFormulation.UREA,
        hours_since_application=24.0,
        n_applied_lbs_acre=0.0,  # Zero application
        p2o5_applied_lbs_acre=0.0,
        k2o_applied_lbs_acre=0.0
    )

    request = NutrientUptakeRequest(
        request_id="test_zero",
        crop_requirements=corn_v9_requirements,
        soil_characteristics=corn_soil_sandy,
        weather_conditions=favorable_weather,
        application_details=zero_application
    )

    prediction = await service.predict_nutrient_fate(request)

    # Should handle gracefully - no losses if nothing applied
    for loss_pred in prediction.loss_predictions:
        assert loss_pred.loss_amount_lbs_acre == 0.0


@pytest.mark.asyncio
async def test_extreme_temperature_cold(service, corn_soil_sandy):
    """Test handling of extreme cold temperature."""
    cold_weather = WeatherConditions(
        temperature_f=25.0,  # Very cold
        relative_humidity_percent=70.0,
        rainfall_inches=0.5
    )

    inputs = VolatilizationModelInputs(
        fertilizer_formulation=FertilizerFormulation.UREA,
        application_method=ApplicationMethodType.BROADCAST,
        weather_conditions=cold_weather,
        soil_characteristics=corn_soil_sandy,
        applied_n_lbs_acre=150.0,
        hours_since_application=24.0
    )

    prediction = await service.predict_volatilization_loss(inputs)

    # Cold weather should greatly reduce volatilization
    assert prediction.loss_percent < 5.0


@pytest.mark.asyncio
async def test_extreme_temperature_hot(service, corn_soil_sandy):
    """Test handling of extreme hot temperature."""
    hot_weather = WeatherConditions(
        temperature_f=105.0,  # Very hot
        relative_humidity_percent=20.0,
        rainfall_inches=0.0,
        wind_speed_mph=20.0
    )

    inputs = VolatilizationModelInputs(
        fertilizer_formulation=FertilizerFormulation.UREA,
        application_method=ApplicationMethodType.BROADCAST,
        weather_conditions=hot_weather,
        soil_characteristics=corn_soil_sandy,
        applied_n_lbs_acre=150.0,
        hours_since_application=48.0
    )

    prediction = await service.predict_volatilization_loss(inputs)

    # Very hot, dry, windy should cause high volatilization
    assert prediction.loss_percent > 15.0
    assert prediction.risk_level in ["high", "very_high"]


@pytest.mark.asyncio
async def test_early_growth_stage(service):
    """Test uptake curve at very early growth stage."""
    curve = await service.calculate_nutrient_uptake_curve(
        crop_type=CropType.CORN,
        growth_stage=GrowthStage.VE,
        nutrient_type=NutrientType.NITROGEN,
        total_nutrient_need_lbs_acre=220.0,
        yield_goal=200.0
    )

    # At emergence, uptake should be very low
    ve_point = None
    for point in curve.uptake_points:
        if point.growth_stage == GrowthStage.VE:
            ve_point = point

    assert ve_point is not None
    assert ve_point.cumulative_uptake_percent < 2.0  # Less than 2% by VE


@pytest.mark.asyncio
async def test_late_growth_stage(service):
    """Test uptake curve at late growth stage."""
    curve = await service.calculate_nutrient_uptake_curve(
        crop_type=CropType.CORN,
        growth_stage=GrowthStage.R6,
        nutrient_type=NutrientType.NITROGEN,
        total_nutrient_need_lbs_acre=220.0,
        yield_goal=200.0
    )

    # At maturity, uptake should be complete
    r6_point = None
    for point in curve.uptake_points:
        if point.growth_stage == GrowthStage.R6:
            r6_point = point

    assert r6_point is not None
    assert r6_point.cumulative_uptake_percent == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
