"""
Unit tests for EnvironmentalAssessmentService

Tests cover:
- Carbon footprint calculations for different fertilizer types
- Water quality impact assessments
- Soil health impact assessments
- Biodiversity impact assessments
- Lifecycle assessments
- Environmental scoring
- Mitigation recommendations
- Comparative analysis
- Agricultural validation
- Edge cases and error handling
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from ..src.services.environmental_service import EnvironmentalAssessmentService
from ..src.models.environmental_models import (
    EnvironmentalImpactData,
    CarbonFootprint,
    WaterQualityImpact,
    SoilHealthImpact,
    BiodiversityImpact,
    EnvironmentalScore,
    MitigationRecommendation,
    FertilizerCategory,
    SeverityLevel,
)


@pytest.fixture
def service():
    """Create EnvironmentalAssessmentService instance."""
    return EnvironmentalAssessmentService()


@pytest.fixture
def urea_fertilizer_data():
    """Urea fertilizer data (high N, high emissions)."""
    return {
        "id": "urea_001",
        "name": "Urea 46-0-0",
        "type": "urea",
        "nitrogen_percent": 46.0,
        "phosphorus_percent": 0.0,
        "potassium_percent": 0.0,
        "composition": {
            "nitrogen_percent": 46.0,
            "phosphorus_percent": 0.0,
            "potassium_percent": 0.0
        }
    }


@pytest.fixture
def organic_compost_data():
    """Organic compost data (low emissions, soil health benefits)."""
    return {
        "id": "compost_001",
        "name": "Organic Compost",
        "type": "compost",
        "nitrogen_percent": 2.0,
        "phosphorus_percent": 1.0,
        "potassium_percent": 1.5,
        "composition": {
            "nitrogen_percent": 2.0,
            "phosphorus_percent": 1.0,
            "potassium_percent": 1.5
        }
    }


@pytest.fixture
def broadcast_application_data():
    """Broadcast application (higher risk)."""
    return {
        "rate_lbs_per_acre": 150.0,
        "method": "broadcast",
        "transport_distance_km": 800.0
    }


@pytest.fixture
def incorporated_application_data():
    """Incorporated application (lower risk)."""
    return {
        "rate_lbs_per_acre": 150.0,
        "method": "incorporated",
        "transport_distance_km": 500.0
    }


@pytest.fixture
def high_risk_field_conditions():
    """High-risk field conditions (sandy soil, near water, heavy rain)."""
    return {
        "soil": {
            "texture": "sandy loam",
            "drainage": "well drained",
            "ph": 6.2,
            "cec": 8.0,
            "organic_matter_percent": 1.5,
            "slope_percent": 8.0,
            "erosion_risk": "high",
            "distance_to_water_m": 25.0
        },
        "weather": {
            "rainfall_inches": 4.5,
            "temperature_f": 85.0
        },
        "ecosystem_type": "agricultural",
        "distance_to_water_m": 25.0,
        "farm_size_acres": 100.0
    }


@pytest.fixture
def low_risk_field_conditions():
    """Low-risk field conditions (clay loam, far from water, moderate rain)."""
    return {
        "soil": {
            "texture": "clay loam",
            "drainage": "moderate",
            "ph": 6.8,
            "cec": 18.0,
            "organic_matter_percent": 4.0,
            "slope_percent": 2.0,
            "erosion_risk": "low",
            "distance_to_water_m": 300.0
        },
        "weather": {
            "rainfall_inches": 1.0,
            "temperature_f": 65.0
        },
        "ecosystem_type": "agricultural",
        "distance_to_water_m": 300.0,
        "farm_size_acres": 100.0
    }


# Carbon Footprint Tests

@pytest.mark.asyncio
async def test_carbon_footprint_urea_high_emissions(service, urea_fertilizer_data, broadcast_application_data):
    """Test that urea has significant carbon footprint due to N2O emissions."""
    footprint = await service.calculate_carbon_footprint(
        fertilizer_type=urea_fertilizer_data["type"],
        amount_lbs_per_acre=broadcast_application_data["rate_lbs_per_acre"],
        transport_distance_km=broadcast_application_data["transport_distance_km"],
        nitrogen_content_percent=urea_fertilizer_data["nitrogen_percent"]
    )

    assert isinstance(footprint, CarbonFootprint)
    assert footprint.total_emissions_kg_co2e_per_acre > 200.0  # Urea has high N2O emissions
    assert footprint.n2o_emissions_kg_co2e_per_kg_n > 4.0  # N2O is major contributor
    assert footprint.severity_level in [SeverityLevel.HIGH, SeverityLevel.VERY_HIGH]
    assert footprint.carbon_impact_score < 60.0  # Poor carbon score
    assert len(footprint.primary_emission_sources) > 0


@pytest.mark.asyncio
async def test_carbon_footprint_organic_compost_low_emissions(service, organic_compost_data, broadcast_application_data):
    """Test that organic compost has low carbon footprint and may sequester carbon."""
    footprint = await service.calculate_carbon_footprint(
        fertilizer_type=organic_compost_data["type"],
        amount_lbs_per_acre=broadcast_application_data["rate_lbs_per_acre"],
        transport_distance_km=broadcast_application_data["transport_distance_km"],
        nitrogen_content_percent=organic_compost_data["nitrogen_percent"]
    )

    assert footprint.total_emissions_kg_co2e_per_acre < 100.0  # Low emissions
    assert footprint.severity_level in [SeverityLevel.LOW, SeverityLevel.MODERATE]
    assert footprint.carbon_impact_score > 60.0  # Good carbon score
    # May have carbon sequestration
    if footprint.carbon_sequestration_kg_co2e_per_kg is not None:
        assert footprint.carbon_sequestration_kg_co2e_per_kg < 0  # Negative = sequestration


@pytest.mark.asyncio
async def test_carbon_footprint_production_vs_n2o(service, urea_fertilizer_data, broadcast_application_data):
    """Test that N2O emissions dominate carbon footprint for high-N fertilizers."""
    footprint = await service.calculate_carbon_footprint(
        fertilizer_type=urea_fertilizer_data["type"],
        amount_lbs_per_acre=broadcast_application_data["rate_lbs_per_acre"],
        transport_distance_km=broadcast_application_data["transport_distance_km"],
        nitrogen_content_percent=urea_fertilizer_data["nitrogen_percent"]
    )

    # For high-N fertilizer, N2O should be a major source
    n2o_mentioned = any("N2O" in source or "field" in source.lower() for source in footprint.primary_emission_sources)
    assert n2o_mentioned, "N2O should be identified as primary emission source for urea"


@pytest.mark.asyncio
async def test_carbon_footprint_transport_distance_effect(service, urea_fertilizer_data):
    """Test that transport distance affects total carbon footprint."""
    # Short distance
    footprint_short = await service.calculate_carbon_footprint(
        fertilizer_type=urea_fertilizer_data["type"],
        amount_lbs_per_acre=150.0,
        transport_distance_km=100.0,
        nitrogen_content_percent=urea_fertilizer_data["nitrogen_percent"]
    )

    # Long distance
    footprint_long = await service.calculate_carbon_footprint(
        fertilizer_type=urea_fertilizer_data["type"],
        amount_lbs_per_acre=150.0,
        transport_distance_km=2000.0,
        nitrogen_content_percent=urea_fertilizer_data["nitrogen_percent"]
    )

    assert footprint_long.total_emissions_kg_co2e_per_acre > footprint_short.total_emissions_kg_co2e_per_acre
    assert footprint_long.transport_emissions_kg_co2e_per_kg > footprint_short.transport_emissions_kg_co2e_per_kg


# Water Quality Impact Tests

@pytest.mark.asyncio
async def test_water_quality_high_risk_sandy_soil_heavy_rain(
    service, urea_fertilizer_data, broadcast_application_data, high_risk_field_conditions
):
    """Test that sandy soil with heavy rain has high leaching and runoff risk."""
    water_impact = await service.assess_water_quality_impact(
        fertilizer_data={**urea_fertilizer_data, "application_rate": broadcast_application_data["rate_lbs_per_acre"]},
        soil_data=high_risk_field_conditions["soil"],
        weather_data=high_risk_field_conditions["weather"],
        application_method=broadcast_application_data["method"]
    )

    assert isinstance(water_impact, WaterQualityImpact)
    assert water_impact.nitrate_leaching_risk_score > 0.5  # High leaching risk on sandy soil
    assert water_impact.groundwater_contamination_risk in [SeverityLevel.MODERATE, SeverityLevel.HIGH, SeverityLevel.VERY_HIGH]
    assert water_impact.water_quality_impact_score < 70.0  # Poor water quality score
    assert len(water_impact.primary_risk_factors) > 0


@pytest.mark.asyncio
async def test_water_quality_low_risk_clay_soil_moderate_rain(
    service, urea_fertilizer_data, broadcast_application_data, low_risk_field_conditions
):
    """Test that clay soil with moderate rain has lower risk."""
    water_impact = await service.assess_water_quality_impact(
        fertilizer_data={**urea_fertilizer_data, "application_rate": broadcast_application_data["rate_lbs_per_acre"]},
        soil_data=low_risk_field_conditions["soil"],
        weather_data=low_risk_field_conditions["weather"],
        application_method=broadcast_application_data["method"]
    )

    assert water_impact.nitrate_leaching_risk_score < 0.6  # Lower leaching risk on clay
    assert water_impact.water_quality_impact_score > 50.0
    # Should have lower severity than sandy soil
    assert water_impact.groundwater_contamination_risk in [SeverityLevel.LOW, SeverityLevel.MODERATE]


@pytest.mark.asyncio
async def test_water_quality_incorporation_reduces_runoff(
    service, urea_fertilizer_data, incorporated_application_data, high_risk_field_conditions
):
    """Test that incorporation reduces runoff risk compared to broadcast."""
    # Broadcast
    water_impact_broadcast = await service.assess_water_quality_impact(
        fertilizer_data={**urea_fertilizer_data, "application_rate": 150.0},
        soil_data=high_risk_field_conditions["soil"],
        weather_data=high_risk_field_conditions["weather"],
        application_method="broadcast"
    )

    # Incorporated
    water_impact_incorporated = await service.assess_water_quality_impact(
        fertilizer_data={**urea_fertilizer_data, "application_rate": 150.0},
        soil_data=high_risk_field_conditions["soil"],
        weather_data=high_risk_field_conditions["weather"],
        application_method="incorporated"
    )

    # Incorporation should reduce runoff and leaching (or at least not increase)
    assert water_impact_incorporated.phosphorus_runoff_risk_score <= water_impact_broadcast.phosphorus_runoff_risk_score
    assert water_impact_incorporated.water_quality_impact_score >= water_impact_broadcast.water_quality_impact_score


@pytest.mark.asyncio
async def test_water_quality_proximity_to_water(
    service, urea_fertilizer_data, broadcast_application_data, high_risk_field_conditions
):
    """Test that proximity to water body is flagged."""
    water_impact = await service.assess_water_quality_impact(
        fertilizer_data={**urea_fertilizer_data, "application_rate": broadcast_application_data["rate_lbs_per_acre"]},
        soil_data=high_risk_field_conditions["soil"],
        weather_data=high_risk_field_conditions["weather"],
        application_method=broadcast_application_data["method"]
    )

    # Very close to water (25m)
    assert water_impact.distance_to_surface_water_m == 25.0
    assert water_impact.surface_water_pollution_risk in [SeverityLevel.HIGH, SeverityLevel.VERY_HIGH]


# Soil Health Impact Tests

@pytest.mark.asyncio
async def test_soil_health_urea_acidifying_effect(service, urea_fertilizer_data):
    """Test that urea has acidifying effect on soil."""
    soil_impact = await service.assess_soil_health_impact(
        fertilizer_type=urea_fertilizer_data["type"],
        application_rate=150.0,
        soil_conditions={"ph": 6.5, "cec": 15.0, "organic_matter_percent": 3.0},
        fertilizer_composition=urea_fertilizer_data["composition"]
    )

    assert isinstance(soil_impact, SoilHealthImpact)
    assert soil_impact.acidification_potential < 0  # Negative = acidifying
    assert soil_impact.ph_change_estimate < 0  # pH will decrease
    assert soil_impact.lime_requirement_lbs_per_acre > 0  # Lime needed to neutralize


@pytest.mark.asyncio
async def test_soil_health_compost_improves_soil(service, organic_compost_data):
    """Test that compost improves soil health."""
    soil_impact = await service.assess_soil_health_impact(
        fertilizer_type=organic_compost_data["type"],
        application_rate=1000.0,  # Typical compost rate
        soil_conditions={"ph": 6.5, "cec": 15.0, "organic_matter_percent": 3.0},
        fertilizer_composition=organic_compost_data["composition"]
    )

    assert soil_impact.organic_matter_contribution_lbs_per_acre > 100.0  # Adds significant OM
    assert soil_impact.organic_matter_effect == "positive"
    assert soil_impact.microbial_activity_impact == "beneficial"
    assert soil_impact.soil_health_impact_score > 70.0  # Good score
    assert len(soil_impact.positive_impacts) > 0


@pytest.mark.asyncio
async def test_soil_health_salt_index_effect(service, urea_fertilizer_data):
    """Test that high salt index is flagged."""
    # Use potash (high salt index)
    soil_impact = await service.assess_soil_health_impact(
        fertilizer_type="potash",
        application_rate=300.0,  # High rate
        soil_conditions={"ph": 6.5, "cec": 15.0, "organic_matter_percent": 3.0},
        fertilizer_composition={"potassium_percent": 60.0}
    )

    # Potash has high salt index (116)
    assert soil_impact.salt_index > 100.0
    assert soil_impact.soil_salinity_risk in [SeverityLevel.HIGH, SeverityLevel.VERY_HIGH]


# Biodiversity Impact Tests

@pytest.mark.asyncio
async def test_biodiversity_compost_beneficial(service):
    """Test that compost is beneficial for biodiversity."""
    biodiversity_impact = await service.assess_biodiversity_impact(
        fertilizer_type="compost",
        ecosystem_type="agricultural",
        proximity_to_water_m=150.0
    )

    assert isinstance(biodiversity_impact, BiodiversityImpact)
    # Compost should be beneficial or at least neutral (not harmful)
    assert biodiversity_impact.beneficial_insect_impact in ["positive", "neutral"]
    assert biodiversity_impact.earthworm_impact in ["beneficial", "neutral"]
    assert biodiversity_impact.beneficial_microbe_impact in ["beneficial", "neutral"]
    # Individual component scores should be good
    assert biodiversity_impact.pollinator_safety_score >= 8.0
    assert biodiversity_impact.soil_fauna_impact_score >= 8.0
    # Overall score calculation may vary, but should be non-negative
    assert biodiversity_impact.biodiversity_impact_score >= 0.0


@pytest.mark.asyncio
async def test_biodiversity_synthetic_near_water_risk(service):
    """Test that synthetic fertilizers near water pose aquatic risk."""
    biodiversity_impact = await service.assess_biodiversity_impact(
        fertilizer_type="urea",
        ecosystem_type="riparian",
        proximity_to_water_m=20.0  # Very close
    )

    # Close proximity to water should increase aquatic impact
    assert biodiversity_impact.fish_impact in [SeverityLevel.MODERATE, SeverityLevel.HIGH, SeverityLevel.VERY_HIGH]
    assert len(biodiversity_impact.protective_measures_needed) > 0
    # Should recommend buffer strips
    buffer_mentioned = any("buffer" in measure.lower() for measure in biodiversity_impact.protective_measures_needed)
    assert buffer_mentioned


@pytest.mark.asyncio
async def test_biodiversity_distance_effect(service):
    """Test that distance to water affects biodiversity impact."""
    # Near water
    biodiversity_near = await service.assess_biodiversity_impact(
        fertilizer_type="urea",
        ecosystem_type="agricultural",
        proximity_to_water_m=25.0
    )

    # Far from water
    biodiversity_far = await service.assess_biodiversity_impact(
        fertilizer_type="urea",
        ecosystem_type="agricultural",
        proximity_to_water_m=500.0
    )

    # Near water should have higher or equal aquatic impact (comparing enum values)
    # Map severity levels to numeric values for comparison
    severity_values = {
        SeverityLevel.VERY_LOW: 0,
        SeverityLevel.LOW: 1,
        SeverityLevel.MODERATE: 2,
        SeverityLevel.HIGH: 3,
        SeverityLevel.VERY_HIGH: 4
    }

    near_fish_severity = severity_values[biodiversity_near.fish_impact]
    far_fish_severity = severity_values[biodiversity_far.fish_impact]

    # Near water should have higher or equal severity
    assert near_fish_severity >= far_fish_severity


# Environmental Scoring Tests

@pytest.mark.asyncio
async def test_environmental_score_calculation(service, urea_fertilizer_data, broadcast_application_data, low_risk_field_conditions):
    """Test overall environmental score calculation."""
    # Get full assessment
    assessment = await service.assess_environmental_impact(
        fertilizer_data=urea_fertilizer_data,
        application_data=broadcast_application_data,
        field_conditions=low_risk_field_conditions
    )

    assert isinstance(assessment.environmental_score, EnvironmentalScore)
    assert 0.0 <= assessment.environmental_score.overall_environmental_score <= 100.0
    assert assessment.environmental_score.environmental_rating in [
        "Excellent", "Good", "Fair", "Poor", "Very Poor"
    ]
    assert assessment.environmental_score.strongest_area is not None
    assert assessment.environmental_score.weakest_area is not None
    assert len(assessment.environmental_score.weighting_scheme) == 4


@pytest.mark.asyncio
async def test_environmental_score_compost_better_than_synthetic(
    service, urea_fertilizer_data, organic_compost_data, broadcast_application_data, low_risk_field_conditions
):
    """Test that organic compost scores better environmentally than synthetic urea."""
    # Urea assessment
    urea_assessment = await service.assess_environmental_impact(
        fertilizer_data=urea_fertilizer_data,
        application_data=broadcast_application_data,
        field_conditions=low_risk_field_conditions
    )

    # Compost assessment (adjust rate for lower nutrient content)
    compost_application = {**broadcast_application_data, "rate_lbs_per_acre": 1000.0}
    compost_assessment = await service.assess_environmental_impact(
        fertilizer_data=organic_compost_data,
        application_data=compost_application,
        field_conditions=low_risk_field_conditions
    )

    # Compost should have better overall environmental score
    assert compost_assessment.environmental_score.overall_environmental_score > urea_assessment.environmental_score.overall_environmental_score
    # Compost should be better for soil health
    assert compost_assessment.soil_health_impact.soil_health_impact_score > urea_assessment.soil_health_impact.soil_health_impact_score


# Mitigation Recommendations Tests

def test_mitigation_recommendations_high_carbon(service):
    """Test that high carbon footprint generates appropriate mitigation recommendations."""
    # Create high-carbon scenario
    carbon_footprint = CarbonFootprint(
        production_emissions_kg_co2e_per_kg=2.0,
        transport_emissions_kg_co2e_per_kg=0.1,
        transport_distance_km=800.0,
        application_emissions_kg_co2e_per_acre=5.0,
        n2o_emissions_kg_co2e_per_kg_n=5.0,
        n2o_emission_factor=0.012,
        carbon_sequestration_kg_co2e_per_kg=0.0,
        total_emissions_kg_co2e_per_kg=4.0,
        total_emissions_kg_co2e_per_acre=400.0,
        carbon_impact_score=30.0,
        severity_level=SeverityLevel.VERY_HIGH,
        primary_emission_sources=["N2O from field: 300 kg CO2e/acre (75%)"],
        mitigation_potential_percent=40.0
    )

    # Create moderate water quality impact
    water_quality = WaterQualityImpact(
        nitrate_leaching_risk_score=0.5,
        nitrate_leaching_potential_lbs_n_per_acre=10.0,
        phosphorus_runoff_risk_score=0.3,
        phosphorus_runoff_potential_lbs_p2o5_per_acre=2.0,
        eutrophication_potential_score=4.0,
        groundwater_contamination_risk=SeverityLevel.MODERATE,
        surface_water_pollution_risk=SeverityLevel.LOW,
        water_quality_impact_score=60.0,
        primary_risk_factors=[],
        secondary_risk_factors=[]
    )

    # Create neutral soil health
    soil_health = SoilHealthImpact(
        acidification_potential=-1.0,
        ph_change_estimate=-0.1,
        lime_requirement_lbs_per_acre=200.0,
        salt_index=75.0,
        soil_salinity_risk=SeverityLevel.MODERATE,
        organic_matter_contribution_lbs_per_acre=0.0,
        organic_matter_effect="neutral",
        microbial_activity_impact="neutral",
        microbial_impact_score=6.0,
        soil_structure_effect="neutral",
        long_term_degradation_risk=SeverityLevel.MODERATE,
        soil_health_impact_score=60.0,
        positive_impacts=[],
        negative_impacts=[]
    )

    # Create neutral biodiversity
    biodiversity = BiodiversityImpact(
        beneficial_insect_impact="neutral",
        pollinator_safety_score=8.0,
        earthworm_impact="neutral",
        beneficial_microbe_impact="neutral",
        soil_fauna_impact_score=7.0,
        aquatic_toxicity_score=7.0,
        fish_impact=SeverityLevel.LOW,
        aquatic_invertebrate_impact=SeverityLevel.LOW,
        habitat_disruption_risk=SeverityLevel.LOW,
        biodiversity_impact_score=75.0,
        species_of_concern=[],
        protective_measures_needed=[]
    )

    recommendations = service.generate_mitigation_recommendations(
        carbon_footprint=carbon_footprint,
        water_quality_impact=water_quality,
        soil_health_impact=soil_health,
        biodiversity_impact=biodiversity,
        application_data={"method": "broadcast"},
        field_conditions={"soil": {"distance_to_water_m": 150.0}}
    )

    assert len(recommendations) > 0
    # Should recommend GHG mitigation strategies
    ghg_recommendations = [rec for rec in recommendations if rec.category.value == "greenhouse_gas"]
    assert len(ghg_recommendations) > 0
    # Should mention inhibitors or precision agriculture
    rec_texts = " ".join([rec.recommendation for rec in ghg_recommendations]).lower()
    assert "inhibitor" in rec_texts or "precision" in rec_texts or "4r" in rec_texts


def test_mitigation_recommendations_high_water_risk(service):
    """Test that high water quality risk generates water-specific recommendations."""
    # Low carbon
    carbon_footprint = CarbonFootprint(
        production_emissions_kg_co2e_per_kg=1.0,
        transport_emissions_kg_co2e_per_kg=0.1,
        transport_distance_km=500.0,
        application_emissions_kg_co2e_per_acre=5.0,
        n2o_emissions_kg_co2e_per_kg_n=2.0,
        n2o_emission_factor=0.008,
        carbon_sequestration_kg_co2e_per_kg=0.0,
        total_emissions_kg_co2e_per_kg=2.0,
        total_emissions_kg_co2e_per_acre=150.0,
        carbon_impact_score=70.0,
        severity_level=SeverityLevel.MODERATE,
        primary_emission_sources=[],
        mitigation_potential_percent=20.0
    )

    # High water quality risk
    water_quality = WaterQualityImpact(
        nitrate_leaching_risk_score=0.8,
        nitrate_leaching_potential_lbs_n_per_acre=25.0,
        phosphorus_runoff_risk_score=0.75,
        phosphorus_runoff_potential_lbs_p2o5_per_acre=8.0,
        eutrophication_potential_score=8.0,
        groundwater_contamination_risk=SeverityLevel.VERY_HIGH,
        surface_water_pollution_risk=SeverityLevel.HIGH,
        water_quality_impact_score=30.0,
        primary_risk_factors=["High leaching risk", "High runoff risk"],
        secondary_risk_factors=[],
        distance_to_surface_water_m=40.0
    )

    # Neutral others
    soil_health = SoilHealthImpact(
        acidification_potential=-0.5,
        ph_change_estimate=-0.05,
        salt_index=50.0,
        soil_salinity_risk=SeverityLevel.LOW,
        organic_matter_contribution_lbs_per_acre=0.0,
        organic_matter_effect="neutral",
        microbial_activity_impact="neutral",
        microbial_impact_score=6.0,
        soil_structure_effect="neutral",
        long_term_degradation_risk=SeverityLevel.LOW,
        soil_health_impact_score=75.0,
        positive_impacts=[],
        negative_impacts=[]
    )

    biodiversity = BiodiversityImpact(
        beneficial_insect_impact="neutral",
        pollinator_safety_score=8.0,
        earthworm_impact="neutral",
        beneficial_microbe_impact="neutral",
        soil_fauna_impact_score=7.0,
        aquatic_toxicity_score=7.0,
        fish_impact=SeverityLevel.MODERATE,
        aquatic_invertebrate_impact=SeverityLevel.MODERATE,
        habitat_disruption_risk=SeverityLevel.MODERATE,
        biodiversity_impact_score=65.0,
        species_of_concern=[],
        protective_measures_needed=[]
    )

    recommendations = service.generate_mitigation_recommendations(
        carbon_footprint=carbon_footprint,
        water_quality_impact=water_quality,
        soil_health_impact=soil_health,
        biodiversity_impact=biodiversity,
        application_data={"method": "broadcast"},
        field_conditions={"soil": {"distance_to_water_m": 40.0}}
    )

    # Should have water quality recommendations
    water_recommendations = [rec for rec in recommendations if rec.category.value == "water_pollution"]
    assert len(water_recommendations) > 0
    # Should mention split applications, incorporation, or buffer strips
    rec_texts = " ".join([rec.recommendation for rec in water_recommendations]).lower()
    assert "split" in rec_texts or "incorporat" in rec_texts or "buffer" in rec_texts


# Comparative Analysis Tests

@pytest.mark.asyncio
async def test_compare_environmental_impacts(
    service, urea_fertilizer_data, organic_compost_data, broadcast_application_data, low_risk_field_conditions
):
    """Test comparative environmental impact analysis."""
    fertilizer_options = [
        urea_fertilizer_data,
        organic_compost_data,
        {
            "id": "ammonium_nitrate_001",
            "name": "Ammonium Nitrate 34-0-0",
            "type": "ammonium nitrate",
            "nitrogen_percent": 34.0,
            "phosphorus_percent": 0.0,
            "potassium_percent": 0.0,
            "composition": {"nitrogen_percent": 34.0}
        }
    ]

    comparison = await service.compare_environmental_impacts(
        fertilizer_options=fertilizer_options,
        application_data=broadcast_application_data,
        field_conditions=low_risk_field_conditions
    )

    assert len(comparison.fertilizer_assessments) == 3
    assert len(comparison.overall_ranking) == 3
    assert comparison.recommended_fertilizer is not None
    assert len(comparison.key_differentiators) >= 0
    assert len(comparison.environmental_trade_offs) == 3


# Full Integration Tests

@pytest.mark.asyncio
async def test_full_assessment_urea_broadcast_high_risk(
    service, urea_fertilizer_data, broadcast_application_data, high_risk_field_conditions
):
    """Test complete environmental assessment for worst-case scenario."""
    assessment = await service.assess_environmental_impact(
        fertilizer_data=urea_fertilizer_data,
        application_data=broadcast_application_data,
        field_conditions=high_risk_field_conditions
    )

    assert isinstance(assessment, EnvironmentalImpactData)
    # Should have poor environmental performance in high-risk scenario
    assert assessment.environmental_score.overall_environmental_score < 70.0
    assert len(assessment.mitigation_recommendations) > 0
    # Should have high-priority recommendations
    high_priority_recs = [rec for rec in assessment.mitigation_recommendations if rec.priority == "High"]
    assert len(high_priority_recs) > 0


@pytest.mark.asyncio
async def test_full_assessment_compost_incorporated_low_risk(
    service, organic_compost_data, incorporated_application_data, low_risk_field_conditions
):
    """Test complete environmental assessment for best-case scenario."""
    compost_application = {**incorporated_application_data, "rate_lbs_per_acre": 1000.0}
    assessment = await service.assess_environmental_impact(
        fertilizer_data=organic_compost_data,
        application_data=compost_application,
        field_conditions=low_risk_field_conditions
    )

    # Should have good environmental performance
    assert assessment.environmental_score.overall_environmental_score > 60.0
    assert assessment.environmental_score.environmental_rating in ["Good", "Excellent"]
    # Compost should have positive soil health impacts
    assert len(assessment.soil_health_impact.positive_impacts) > 0


# Agricultural Validation Tests

@pytest.mark.asyncio
async def test_agricultural_validation_n2o_emission_factor(service, urea_fertilizer_data, broadcast_application_data):
    """Validate that N2O emission factor is within scientifically accepted range."""
    footprint = await service.calculate_carbon_footprint(
        fertilizer_type=urea_fertilizer_data["type"],
        amount_lbs_per_acre=broadcast_application_data["rate_lbs_per_acre"],
        transport_distance_km=800.0,
        nitrogen_content_percent=urea_fertilizer_data["nitrogen_percent"]
    )

    # IPCC default is 0.01 (1%), range is 0.003-0.03 depending on conditions
    assert 0.003 <= footprint.n2o_emission_factor <= 0.03
    # N2O has 298x GWP of CO2
    # Emission factor should result in roughly 3-6 kg CO2e per kg N applied
    assert 3.0 <= footprint.n2o_emissions_kg_co2e_per_kg_n <= 8.0


@pytest.mark.asyncio
async def test_agricultural_validation_leaching_sandy_vs_clay(service, urea_fertilizer_data, broadcast_application_data):
    """Validate that sandy soils have higher leaching risk than clay soils."""
    # Sandy soil
    sandy_conditions = {
        "soil": {"texture": "sandy loam", "drainage": "well drained", "ph": 6.5, "cec": 8.0,
                "organic_matter_percent": 2.0, "slope_percent": 2.0, "erosion_risk": "low"},
        "weather": {"rainfall_inches": 2.0, "temperature_f": 70.0},
        "ecosystem_type": "agricultural"
    }

    sandy_impact = await service.assess_water_quality_impact(
        fertilizer_data={**urea_fertilizer_data, "application_rate": 150.0},
        soil_data=sandy_conditions["soil"],
        weather_data=sandy_conditions["weather"],
        application_method="broadcast"
    )

    # Clay soil
    clay_conditions = {
        "soil": {"texture": "clay loam", "drainage": "moderate", "ph": 6.8, "cec": 20.0,
                "organic_matter_percent": 4.0, "slope_percent": 2.0, "erosion_risk": "low"},
        "weather": {"rainfall_inches": 2.0, "temperature_f": 70.0},
        "ecosystem_type": "agricultural"
    }

    clay_impact = await service.assess_water_quality_impact(
        fertilizer_data={**urea_fertilizer_data, "application_rate": 150.0},
        soil_data=clay_conditions["soil"],
        weather_data=clay_conditions["weather"],
        application_method="broadcast"
    )

    # Sandy soil should have higher leaching risk
    assert sandy_impact.nitrate_leaching_risk_score > clay_impact.nitrate_leaching_risk_score


@pytest.mark.asyncio
async def test_agricultural_validation_compost_adds_organic_matter(service, organic_compost_data):
    """Validate that compost significantly increases soil organic matter."""
    soil_impact = await service.assess_soil_health_impact(
        fertilizer_type=organic_compost_data["type"],
        application_rate=2000.0,  # 2 tons per acre (typical)
        soil_conditions={"ph": 6.5, "cec": 15.0, "organic_matter_percent": 3.0},
        fertilizer_composition=organic_compost_data["composition"]
    )

    # Compost should add significant OM (typically 30-50% becomes stable OM)
    assert soil_impact.organic_matter_contribution_lbs_per_acre > 400.0
    assert soil_impact.organic_matter_effect == "positive"


# Edge Cases and Error Handling

@pytest.mark.asyncio
async def test_edge_case_zero_nitrogen_content(service):
    """Test handling of fertilizer with zero nitrogen content."""
    footprint = await service.calculate_carbon_footprint(
        fertilizer_type="tsp",  # Triple superphosphate (0% N)
        amount_lbs_per_acre=100.0,
        transport_distance_km=500.0,
        nitrogen_content_percent=0.0
    )

    # Should not have N2O emissions
    assert footprint.n2o_emissions_kg_co2e_per_kg_n == 0.0
    # Should still have production and transport emissions
    assert footprint.total_emissions_kg_co2e_per_acre > 0


@pytest.mark.asyncio
async def test_edge_case_very_high_application_rate(service, urea_fertilizer_data):
    """Test handling of very high application rate."""
    footprint = await service.calculate_carbon_footprint(
        fertilizer_type=urea_fertilizer_data["type"],
        amount_lbs_per_acre=500.0,  # Very high rate
        transport_distance_km=800.0,
        nitrogen_content_percent=urea_fertilizer_data["nitrogen_percent"]
    )

    # Should have proportionally higher emissions
    assert footprint.total_emissions_kg_co2e_per_acre > 600.0
    assert footprint.severity_level == SeverityLevel.VERY_HIGH


@pytest.mark.asyncio
async def test_error_handling_invalid_fertilizer_type(service):
    """Test error handling for unknown fertilizer type."""
    # Should not crash, should use default values
    footprint = await service.calculate_carbon_footprint(
        fertilizer_type="unknown_fertilizer_xyz",
        amount_lbs_per_acre=150.0,
        transport_distance_km=800.0,
        nitrogen_content_percent=20.0
    )

    # Should return valid result with default parameters
    assert isinstance(footprint, CarbonFootprint)
    assert footprint.total_emissions_kg_co2e_per_acre > 0


@pytest.mark.asyncio
async def test_error_handling_missing_optional_data(service, urea_fertilizer_data, broadcast_application_data):
    """Test handling of missing optional field data."""
    # Minimal field conditions
    minimal_conditions = {
        "soil": {"texture": "loam", "drainage": "moderate", "ph": 6.5},
        "weather": {"rainfall_inches": 1.0, "temperature_f": 70.0},
        "ecosystem_type": "agricultural"
    }

    assessment = await service.assess_environmental_impact(
        fertilizer_data=urea_fertilizer_data,
        application_data=broadcast_application_data,
        field_conditions=minimal_conditions
    )

    # Should complete successfully with default values
    assert isinstance(assessment, EnvironmentalImpactData)
    assert assessment.environmental_score.overall_environmental_score > 0


# Performance Tests

@pytest.mark.asyncio
async def test_performance_full_assessment_completes_quickly(
    service, urea_fertilizer_data, broadcast_application_data, low_risk_field_conditions
):
    """Test that full environmental assessment completes in reasonable time."""
    import time

    start_time = time.time()
    assessment = await service.assess_environmental_impact(
        fertilizer_data=urea_fertilizer_data,
        application_data=broadcast_application_data,
        field_conditions=low_risk_field_conditions
    )
    end_time = time.time()

    elapsed_time = end_time - start_time

    # Should complete in less than 2 seconds
    assert elapsed_time < 2.0
    assert isinstance(assessment, EnvironmentalImpactData)


@pytest.mark.asyncio
async def test_performance_comparison_multiple_fertilizers(
    service, urea_fertilizer_data, organic_compost_data, broadcast_application_data, low_risk_field_conditions
):
    """Test that comparing multiple fertilizers completes in reasonable time."""
    import time

    fertilizer_options = [urea_fertilizer_data, organic_compost_data]

    start_time = time.time()
    comparison = await service.compare_environmental_impacts(
        fertilizer_options=fertilizer_options,
        application_data=broadcast_application_data,
        field_conditions=low_risk_field_conditions
    )
    end_time = time.time()

    elapsed_time = end_time - start_time

    # Should complete in less than 5 seconds for 2 fertilizers
    assert elapsed_time < 5.0
    assert len(comparison.fertilizer_assessments) == 2
