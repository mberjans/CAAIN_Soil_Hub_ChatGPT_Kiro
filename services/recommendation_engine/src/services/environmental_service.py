"""
Environmental Assessment Service

Comprehensive service for assessing environmental impacts of fertilizer use including:
- Life cycle assessment (LCA)
- Carbon footprint analysis
- Water quality impact
- Soil health impact
- Biodiversity impact
- Mitigation recommendations

Based on scientific research and agricultural best practices.

Agricultural References:
- IPCC (2019): Refinement to the 2006 IPCC Guidelines for National Greenhouse Gas Inventories
- Bouwman et al. (2002): Emissions of N2O and NO from fertilized fields (Global Biogeochem. Cycles)
- Galloway et al. (2008): Transformation of the Nitrogen Cycle (Science)
- Carpenter et al. (2008): Nonpoint pollution of surface waters (Ecological Applications)
- Robertson & Vitousek (2009): Nitrogen in Agriculture (Annual Review of Plant Biology)
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from ..models.environmental_models import (
    EnvironmentalImpactData,
    CarbonFootprint,
    WaterQualityImpact,
    SoilHealthImpact,
    BiodiversityImpact,
    LifecycleAssessment,
    LifecycleImpact,
    EnvironmentalScore,
    MitigationRecommendation,
    EnvironmentalComparisonResult,
    FertilizerCategory,
    ImpactCategory,
    SeverityLevel,
    LifecycleStage,
)

logger = logging.getLogger(__name__)


class EnvironmentalAssessmentService:
    """
    Service for comprehensive environmental impact assessment of fertilizers.

    This service provides:
    - Carbon footprint calculations including N2O emissions
    - Water quality impact assessment (runoff, leaching)
    - Soil health impact evaluation (acidification, organic matter)
    - Biodiversity impact assessment
    - Full lifecycle assessment (LCA)
    - Environmental scoring and ranking
    - Mitigation recommendation generation
    """

    def __init__(self):
        """Initialize the environmental assessment service."""
        self.logger = logging.getLogger(__name__)
        self._initialize_emission_factors()
        self._initialize_impact_parameters()
        self._initialize_regulatory_standards()
        self.logger.info("EnvironmentalAssessmentService initialized")

    def _initialize_emission_factors(self) -> None:
        """
        Initialize GHG emission factors for different fertilizer types.

        Based on IPCC (2019) and life cycle assessment databases (Ecoinvent, GREET).
        Values are kg CO2e per kg of fertilizer product.
        """
        # Production emissions (kg CO2e per kg fertilizer)
        self.production_emissions = {
            "urea": 1.9,  # Haber-Bosch process + urea synthesis
            "ammonium_nitrate": 2.4,  # High energy intensive
            "ammonium_sulfate": 1.2,
            "anhydrous_ammonia": 2.2,
            "uan_solution": 2.0,
            "dap": 1.1,  # Diammonium phosphate
            "map": 1.0,  # Monoammonium phosphate
            "tsp": 0.6,  # Triple superphosphate
            "potash_kcl": 0.5,  # Potassium chloride
            "organic_manure": 0.1,  # Minimal processing
            "compost": 0.2,  # Composting process
            "slow_release_coated": 3.5,  # Coating adds emissions
            "slow_release_polymer": 4.0,  # Polymer synthesis intensive
        }

        # N2O emission factors (IPCC default is 0.01 = 1% of applied N converted to N2O)
        # N2O has 298x global warming potential of CO2
        self.n2o_emission_factor_default = 0.01  # 1% of applied N
        self.n2o_gwp = 298  # Global warming potential of N2O

        # N2O conversion: 1 kg N * 0.01 * (44/28) * 298 = kg CO2e
        # 44/28 converts N to N2O, 298 converts N2O to CO2e
        self.n2o_co2e_factor = 4.67  # kg CO2e per kg N applied (at 1% emission rate)

        # Emission factors by fertilizer type (adjustments to default)
        self.n2o_adjustment_factors = {
            "urea": 1.2,  # Higher volatilization-redeposition
            "ammonium_nitrate": 1.0,  # Standard
            "anhydrous_ammonia": 0.9,  # Injected, less loss
            "uan_solution": 1.0,
            "organic_manure": 0.8,  # Slower release
            "compost": 0.6,  # Much slower release
            "slow_release_coated": 0.5,  # Controlled release reduces N2O
            "slow_release_polymer": 0.5,
        }

    def _initialize_impact_parameters(self) -> None:
        """Initialize parameters for various environmental impact assessments."""

        # Leaching risk by fertilizer solubility (0-1 scale)
        self.leaching_risk_factors = {
            "urea": 0.8,  # Highly soluble
            "ammonium_nitrate": 0.9,  # Very soluble, nitrate mobile
            "anhydrous_ammonia": 0.7,  # Mobile when converted to nitrate
            "uan_solution": 0.85,  # Liquid, highly mobile
            "dap": 0.3,  # P less mobile
            "map": 0.3,
            "potash_kcl": 0.5,  # K moderately mobile
            "organic_manure": 0.4,  # Slow release reduces leaching
            "compost": 0.2,  # Very slow release
            "slow_release_coated": 0.3,  # Controlled release
            "slow_release_polymer": 0.25,
        }

        # Runoff risk by fertilizer type (0-1 scale)
        self.runoff_risk_factors = {
            "urea": 0.6,
            "ammonium_nitrate": 0.7,
            "dap": 0.8,  # P binds to soil particles, moves with erosion
            "map": 0.8,
            "organic_manure": 0.9,  # High P, moves with erosion
            "compost": 0.5,  # Lower nutrient concentration
            "slow_release_coated": 0.4,
            "slow_release_polymer": 0.4,
        }

        # Soil acidification potential (kg CaCO3 equivalent per kg N)
        self.acidification_factors = {
            "urea": -1.8,  # Acidifying (negative values)
            "ammonium_nitrate": -1.8,
            "ammonium_sulfate": -5.3,  # Strongly acidifying
            "anhydrous_ammonia": -1.8,
            "uan_solution": -1.8,
            "dap": -2.5,  # Ammonium component acidifies
            "map": -2.8,
            "lime": 100.0,  # Alkalizing (positive)
            "organic_manure": -0.3,  # Minimal acidification
            "compost": 0.0,  # Neutral
        }

        # Salt index (relative to sodium nitrate = 100)
        self.salt_index = {
            "urea": 75,
            "ammonium_nitrate": 105,
            "ammonium_sulfate": 69,
            "anhydrous_ammonia": 47,
            "potash_kcl": 116,  # High salt index
            "dap": 29,
            "map": 27,
            "organic_manure": 5,
            "compost": 3,
        }

    def _initialize_regulatory_standards(self) -> None:
        """Initialize regulatory standards and thresholds."""

        # EPA water quality standards (mg/L)
        self.water_quality_standards = {
            "nitrate_drinking_water_mcl": 10.0,  # mg/L NO3-N (Maximum Contaminant Level)
            "phosphorus_stream_target": 0.1,  # mg/L total P (eutrophication threshold)
            "phosphorus_lake_target": 0.025,  # mg/L total P
        }

        # Organic certification requirements
        self.organic_certification_criteria = {
            "allowed_inputs": [
                "organic_manure", "compost", "bone_meal", "blood_meal",
                "rock_phosphate", "greensand", "kelp_meal"
            ],
            "prohibited_inputs": [
                "urea", "ammonium_nitrate", "dap", "map",
                "synthetic_nitrogen", "synthetic_phosphorus"
            ]
        }

    async def assess_environmental_impact(
        self,
        fertilizer_data: Dict[str, Any],
        application_data: Dict[str, Any],
        field_conditions: Dict[str, Any]
    ) -> EnvironmentalImpactData:
        """
        Assess overall environmental impact of fertilizer application.

        Args:
            fertilizer_data: Fertilizer product information including type, composition, name
            application_data: Application details including rate, method, timing
            field_conditions: Field characteristics including soil, weather, proximity to water

        Returns:
            Complete environmental impact assessment

        Raises:
            ValueError: If required data is missing or invalid
        """
        try:
            self.logger.info(
                f"Assessing environmental impact for {fertilizer_data.get('name', 'unknown fertilizer')}"
            )

            # Extract and validate inputs
            fertilizer_type = fertilizer_data.get("type", "unknown")
            fertilizer_name = fertilizer_data.get("name", "Unknown Fertilizer")
            application_rate = application_data.get("rate_lbs_per_acre", 0.0)

            if application_rate <= 0:
                raise ValueError("Application rate must be greater than zero")

            # Determine fertilizer category
            fertilizer_category = self._classify_fertilizer_category(fertilizer_type, fertilizer_data)

            # Calculate carbon footprint
            carbon_footprint = await self.calculate_carbon_footprint(
                fertilizer_type=fertilizer_type,
                amount_lbs_per_acre=application_rate,
                production_method=fertilizer_data.get("production_method"),
                transport_distance_km=application_data.get("transport_distance_km", 800.0),
                nitrogen_content_percent=fertilizer_data.get("nitrogen_percent", 0.0)
            )

            # Assess water quality impact
            water_quality_impact = await self.assess_water_quality_impact(
                fertilizer_data=fertilizer_data,
                soil_data=field_conditions.get("soil", {}),
                weather_data=field_conditions.get("weather", {}),
                application_method=application_data.get("method", "broadcast")
            )

            # Assess soil health impact
            soil_health_impact = await self.assess_soil_health_impact(
                fertilizer_type=fertilizer_type,
                application_rate=application_rate,
                soil_conditions=field_conditions.get("soil", {}),
                fertilizer_composition=fertilizer_data.get("composition", {})
            )

            # Assess biodiversity impact
            biodiversity_impact = await self.assess_biodiversity_impact(
                fertilizer_type=fertilizer_type,
                ecosystem_type=field_conditions.get("ecosystem_type", "agricultural"),
                proximity_to_water_m=field_conditions.get("distance_to_water_m", 100.0)
            )

            # Perform lifecycle assessment (if data available)
            lifecycle_assessment = None
            if fertilizer_data.get("lifecycle_data_available", False):
                lifecycle_assessment = await self.perform_lifecycle_assessment(
                    fertilizer_data=fertilizer_data,
                    full_context={"application": application_data, "field": field_conditions}
                )

            # Calculate overall environmental score
            environmental_score = self.calculate_environmental_score(
                carbon_footprint=carbon_footprint,
                water_quality_impact=water_quality_impact,
                soil_health_impact=soil_health_impact,
                biodiversity_impact=biodiversity_impact
            )

            # Generate mitigation recommendations
            mitigation_recommendations = self.generate_mitigation_recommendations(
                carbon_footprint=carbon_footprint,
                water_quality_impact=water_quality_impact,
                soil_health_impact=soil_health_impact,
                biodiversity_impact=biodiversity_impact,
                application_data=application_data,
                field_conditions=field_conditions
            )

            # Check regulatory compliance
            regulatory_compliance = self._assess_regulatory_compliance(
                fertilizer_type=fertilizer_type,
                water_quality_impact=water_quality_impact,
                field_conditions=field_conditions
            )

            # Compile data sources
            data_sources = self._get_data_sources()
            agricultural_sources = self._get_agricultural_sources()

            # Create assessment
            assessment = EnvironmentalImpactData(
                assessment_id=f"env_assess_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                generated_at=datetime.utcnow(),
                fertilizer_name=fertilizer_name,
                fertilizer_type=fertilizer_type,
                fertilizer_category=fertilizer_category,
                application_rate_lbs_per_acre=application_rate,
                farm_acreage=field_conditions.get("farm_size_acres"),
                carbon_footprint=carbon_footprint,
                water_quality_impact=water_quality_impact,
                soil_health_impact=soil_health_impact,
                biodiversity_impact=biodiversity_impact,
                lifecycle_assessment=lifecycle_assessment,
                environmental_score=environmental_score,
                mitigation_recommendations=mitigation_recommendations,
                regulatory_compliance=regulatory_compliance,
                assessment_confidence=0.85,
                data_sources=data_sources,
                agricultural_sources=agricultural_sources,
                limitations=[
                    "Assessment based on typical field conditions",
                    "Actual impacts may vary with local conditions",
                    "Long-term impacts estimated from research data"
                ]
            )

            self.logger.info(
                f"Environmental assessment completed. Overall score: {environmental_score.overall_environmental_score:.1f}"
            )

            return assessment

        except Exception as e:
            self.logger.error(f"Error assessing environmental impact: {str(e)}")
            raise

    async def calculate_carbon_footprint(
        self,
        fertilizer_type: str,
        amount_lbs_per_acre: float,
        production_method: Optional[str] = None,
        transport_distance_km: float = 800.0,
        nitrogen_content_percent: float = 0.0
    ) -> CarbonFootprint:
        """
        Calculate comprehensive carbon footprint including production, transport, and N2O emissions.

        Args:
            fertilizer_type: Type of fertilizer
            amount_lbs_per_acre: Application rate (lbs/acre)
            production_method: Production method (if specified)
            transport_distance_km: Transportation distance (km)
            nitrogen_content_percent: Nitrogen content (%)

        Returns:
            Complete carbon footprint assessment

        Agricultural Basis:
        - Production emissions from LCA databases (Ecoinvent, GREET)
        - N2O emissions based on IPCC Tier 1 methodology (1% default emission factor)
        - Transportation emissions from EPA emission factors
        """
        try:
            self.logger.info(f"Calculating carbon footprint for {fertilizer_type}")

            # Convert to kg
            amount_kg_per_acre = amount_lbs_per_acre * 0.453592

            # Get production emissions (kg CO2e per kg fertilizer)
            fertilizer_key = self._get_fertilizer_key(fertilizer_type)
            production_emission_factor = self.production_emissions.get(fertilizer_key, 1.5)
            production_emissions_total = amount_kg_per_acre * production_emission_factor

            # Calculate transportation emissions
            # Average truck: 0.11 kg CO2e per ton-km
            transport_emission_factor = 0.11  # kg CO2e per ton-km
            transport_emissions_per_kg = (transport_distance_km * transport_emission_factor / 1000.0)
            transport_emissions_total = amount_kg_per_acre * transport_emissions_per_kg

            # Application equipment emissions (typical diesel tractor)
            # ~0.5 gallons diesel per acre, 10.2 kg CO2e per gallon
            application_emissions = 0.5 * 10.2  # kg CO2e per acre

            # Calculate N2O emissions (major contributor for N fertilizers)
            n2o_emissions_total = 0.0
            n2o_factor_used = 0.0

            if nitrogen_content_percent > 0:
                n_applied_kg_per_acre = amount_kg_per_acre * (nitrogen_content_percent / 100.0)

                # Get fertilizer-specific N2O adjustment
                n2o_adjustment = self.n2o_adjustment_factors.get(fertilizer_key, 1.0)
                effective_emission_factor = self.n2o_emission_factor_default * n2o_adjustment
                n2o_factor_used = effective_emission_factor

                # Calculate N2O emissions in CO2e
                # kg N * emission_factor * (44/28) * GWP
                n2o_emissions_per_kg_n = self.n2o_co2e_factor * n2o_adjustment
                n2o_emissions_total = n_applied_kg_per_acre * n2o_emissions_per_kg_n

            # Carbon sequestration (for organic amendments)
            carbon_sequestration = 0.0
            if fertilizer_key in ["organic_manure", "compost"]:
                # Organic amendments can sequester 0.1-0.5 kg CO2e per kg
                carbon_sequestration = -0.3 * amount_kg_per_acre  # Negative = CO2 removal

            # Total lifecycle emissions
            total_emissions_per_kg = (
                production_emission_factor +
                transport_emissions_per_kg +
                (application_emissions / amount_kg_per_acre)
            )

            if nitrogen_content_percent > 0:
                n_kg_per_kg_fertilizer = nitrogen_content_percent / 100.0
                total_emissions_per_kg = total_emissions_per_kg + (
                    n_kg_per_kg_fertilizer * n2o_emissions_per_kg_n
                )

            total_emissions_per_acre = (
                production_emissions_total +
                transport_emissions_total +
                application_emissions +
                n2o_emissions_total +
                carbon_sequestration
            )

            # Calculate impact score (0-100, higher = better)
            # Good: <100 kg CO2e/acre, Poor: >500 kg CO2e/acre
            if total_emissions_per_acre < 100:
                carbon_impact_score = 90.0 + (100 - total_emissions_per_acre) * 0.1
            elif total_emissions_per_acre < 300:
                carbon_impact_score = 50.0 + (300 - total_emissions_per_acre) * 0.2
            elif total_emissions_per_acre < 500:
                carbon_impact_score = 20.0 + (500 - total_emissions_per_acre) * 0.15
            else:
                carbon_impact_score = max(0.0, 20.0 - (total_emissions_per_acre - 500) * 0.04)

            # Determine severity level
            if total_emissions_per_acre < 100:
                severity = SeverityLevel.LOW
            elif total_emissions_per_acre < 250:
                severity = SeverityLevel.MODERATE
            elif total_emissions_per_acre < 400:
                severity = SeverityLevel.HIGH
            else:
                severity = SeverityLevel.VERY_HIGH

            # Identify primary emission sources
            primary_sources = []
            emissions_breakdown = {
                "Production": production_emissions_total,
                "N2O from field": n2o_emissions_total,
                "Transportation": transport_emissions_total,
                "Application": application_emissions
            }

            sorted_sources = sorted(
                emissions_breakdown.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for source, emissions in sorted_sources:
                if emissions > total_emissions_per_acre * 0.15:  # >15% of total
                    primary_sources.append(
                        f"{source}: {emissions:.1f} kg CO2e/acre ({emissions/total_emissions_per_acre*100:.0f}%)"
                    )

            # Estimate mitigation potential
            mitigation_potential = 0.0
            if n2o_emissions_total > total_emissions_per_acre * 0.3:
                mitigation_potential = 40.0  # N2O reduction strategies can reduce by 30-50%
            elif production_emissions_total > total_emissions_per_acre * 0.5:
                mitigation_potential = 25.0  # Some reduction through efficiency
            else:
                mitigation_potential = 20.0

            footprint = CarbonFootprint(
                production_emissions_kg_co2e_per_kg=production_emission_factor,
                transport_emissions_kg_co2e_per_kg=transport_emissions_per_kg,
                transport_distance_km=transport_distance_km,
                application_emissions_kg_co2e_per_acre=application_emissions,
                n2o_emissions_kg_co2e_per_kg_n=n2o_emissions_per_kg_n if nitrogen_content_percent > 0 else 0.0,
                n2o_emission_factor=n2o_factor_used,
                carbon_sequestration_kg_co2e_per_kg=carbon_sequestration / amount_kg_per_acre if amount_kg_per_acre > 0 else 0.0,
                total_emissions_kg_co2e_per_kg=total_emissions_per_kg,
                total_emissions_kg_co2e_per_acre=total_emissions_per_acre,
                carbon_impact_score=carbon_impact_score,
                severity_level=severity,
                primary_emission_sources=primary_sources,
                mitigation_potential_percent=mitigation_potential
            )

            self.logger.info(
                f"Carbon footprint calculated: {total_emissions_per_acre:.1f} kg CO2e/acre, score: {carbon_impact_score:.1f}"
            )

            return footprint

        except Exception as e:
            self.logger.error(f"Error calculating carbon footprint: {str(e)}")
            raise

    async def assess_water_quality_impact(
        self,
        fertilizer_data: Dict[str, Any],
        soil_data: Dict[str, Any],
        weather_data: Dict[str, Any],
        application_method: str
    ) -> WaterQualityImpact:
        """
        Assess water quality impacts including leaching and runoff.

        Args:
            fertilizer_data: Fertilizer product information
            soil_data: Soil characteristics
            weather_data: Weather conditions
            application_method: Application method

        Returns:
            Water quality impact assessment

        Agricultural Basis:
        - Leaching models from Kanwar et al. (1997), Randall & Vetsch (2005)
        - Runoff models from Carpenter et al. (2008)
        - Eutrophication potential based on Galloway et al. (2008)
        """
        try:
            self.logger.info("Assessing water quality impact")

            fertilizer_type = fertilizer_data.get("type", "unknown")
            fertilizer_key = self._get_fertilizer_key(fertilizer_type)
            application_rate = fertilizer_data.get("application_rate", 100.0)

            # Get nutrient content
            n_percent = fertilizer_data.get("nitrogen_percent", 0.0)
            p_percent = fertilizer_data.get("phosphorus_percent", 0.0)

            n_applied = application_rate * (n_percent / 100.0)
            p_applied = application_rate * (p_percent / 100.0)

            # Base leaching risk from fertilizer type
            base_leaching_risk = self.leaching_risk_factors.get(fertilizer_key, 0.5)

            # Soil texture modifier
            soil_texture = soil_data.get("texture", "loam").lower()
            if "sand" in soil_texture:
                soil_leaching_modifier = 1.5
            elif "clay" in soil_texture:
                soil_leaching_modifier = 0.5
            else:
                soil_leaching_modifier = 1.0

            # Drainage modifier
            drainage = soil_data.get("drainage", "moderate").lower()
            if "poor" in drainage:
                drainage_modifier = 0.6
            elif "excess" in drainage or "well" in drainage:
                drainage_modifier = 1.3
            else:
                drainage_modifier = 1.0

            # Rainfall modifier
            rainfall_inches = weather_data.get("rainfall_inches", 1.0)
            if rainfall_inches < 1.0:
                rainfall_modifier = 0.3
            elif rainfall_inches < 2.0:
                rainfall_modifier = 0.7
            elif rainfall_inches < 4.0:
                rainfall_modifier = 1.0
            else:
                rainfall_modifier = 1.5

            # Application method modifier
            method_modifiers = {
                "broadcast": 1.0,
                "incorporated": 0.6,
                "injected": 0.4,
                "banded": 0.7,
                "fertigation": 0.5
            }
            method_modifier = method_modifiers.get(application_method.lower(), 1.0)

            # Calculate nitrate leaching risk
            nitrate_leaching_risk = min(1.0, base_leaching_risk * soil_leaching_modifier *
                                       drainage_modifier * rainfall_modifier * method_modifier)

            nitrate_leaching_potential = n_applied * nitrate_leaching_risk * 0.20  # Assume up to 20% loss

            # Calculate phosphorus runoff risk
            base_runoff_risk = self.runoff_risk_factors.get(fertilizer_key, 0.5)

            # Slope modifier
            slope_percent = soil_data.get("slope_percent", 2.0)
            if slope_percent < 2.0:
                slope_modifier = 0.5
            elif slope_percent < 6.0:
                slope_modifier = 1.0
            elif slope_percent < 12.0:
                slope_modifier = 1.8
            else:
                slope_modifier = 2.5

            # Erosion risk
            erosion_risk = soil_data.get("erosion_risk", "moderate").lower()
            if erosion_risk == "low":
                erosion_modifier = 0.6
            elif erosion_risk == "high":
                erosion_modifier = 1.8
            else:
                erosion_modifier = 1.0

            phosphorus_runoff_risk = min(1.0, base_runoff_risk * slope_modifier *
                                        erosion_modifier * (rainfall_inches / 2.0) * method_modifier)

            phosphorus_runoff_potential = p_applied * phosphorus_runoff_risk * 0.15  # Up to 15% loss

            # Calculate eutrophication potential
            # Both N and P contribute, P is often limiting factor
            n_contribution = nitrate_leaching_potential * 0.5
            p_contribution = phosphorus_runoff_potential * 5.0  # P is 5-10x more potent
            eutrophication_potential = min(10.0, (n_contribution + p_contribution) / 10.0)

            # Assess groundwater contamination risk
            if nitrate_leaching_risk < 0.3 and rainfall_inches < 2.0:
                groundwater_risk = SeverityLevel.LOW
            elif nitrate_leaching_risk < 0.5:
                groundwater_risk = SeverityLevel.MODERATE
            elif nitrate_leaching_risk < 0.7:
                groundwater_risk = SeverityLevel.HIGH
            else:
                groundwater_risk = SeverityLevel.VERY_HIGH

            # Assess surface water pollution risk
            if phosphorus_runoff_risk < 0.3 and slope_percent < 4.0:
                surface_water_risk = SeverityLevel.LOW
            elif phosphorus_runoff_risk < 0.5:
                surface_water_risk = SeverityLevel.MODERATE
            elif phosphorus_runoff_risk < 0.7:
                surface_water_risk = SeverityLevel.HIGH
            else:
                surface_water_risk = SeverityLevel.VERY_HIGH

            # Calculate water quality impact score (0-100, higher = better)
            leaching_score = (1.0 - nitrate_leaching_risk) * 50.0
            runoff_score = (1.0 - phosphorus_runoff_risk) * 50.0
            water_quality_score = leaching_score + runoff_score

            # Identify risk factors
            primary_risk_factors = []
            if nitrate_leaching_risk > 0.6:
                primary_risk_factors.append(
                    f"High nitrate leaching risk ({nitrate_leaching_potential:.1f} lbs N/acre potential loss)"
                )
            if phosphorus_runoff_risk > 0.6:
                primary_risk_factors.append(
                    f"High phosphorus runoff risk ({phosphorus_runoff_potential:.1f} lbs P2O5/acre potential loss)"
                )
            if rainfall_inches > 3.0:
                primary_risk_factors.append(f"Heavy rainfall ({rainfall_inches:.1f} inches)")

            secondary_risk_factors = []
            if "sand" in soil_texture:
                secondary_risk_factors.append("Sandy soil texture increases leaching")
            if slope_percent > 6.0:
                secondary_risk_factors.append(f"Slope ({slope_percent:.0f}%) increases runoff risk")
            if application_method == "broadcast":
                secondary_risk_factors.append("Broadcast application increases loss risk")

            # Check distance to water
            distance_to_water = soil_data.get("distance_to_water_m")
            in_wellhead_area = soil_data.get("in_wellhead_protection", False)

            impact = WaterQualityImpact(
                nitrate_leaching_risk_score=nitrate_leaching_risk,
                nitrate_leaching_potential_lbs_n_per_acre=nitrate_leaching_potential,
                phosphorus_runoff_risk_score=phosphorus_runoff_risk,
                phosphorus_runoff_potential_lbs_p2o5_per_acre=phosphorus_runoff_potential,
                eutrophication_potential_score=eutrophication_potential,
                groundwater_contamination_risk=groundwater_risk,
                surface_water_pollution_risk=surface_water_risk,
                water_quality_impact_score=water_quality_score,
                primary_risk_factors=primary_risk_factors,
                secondary_risk_factors=secondary_risk_factors,
                distance_to_surface_water_m=distance_to_water,
                in_wellhead_protection_area=in_wellhead_area
            )

            self.logger.info(
                f"Water quality impact assessed: score {water_quality_score:.1f}, "
                f"leaching risk {nitrate_leaching_risk:.2f}, runoff risk {phosphorus_runoff_risk:.2f}"
            )

            return impact

        except Exception as e:
            self.logger.error(f"Error assessing water quality impact: {str(e)}")
            raise

    async def assess_soil_health_impact(
        self,
        fertilizer_type: str,
        application_rate: float,
        soil_conditions: Dict[str, Any],
        fertilizer_composition: Dict[str, Any]
    ) -> SoilHealthImpact:
        """
        Assess soil health impacts including acidification, salinity, and organic matter.

        Args:
            fertilizer_type: Type of fertilizer
            application_rate: Application rate (lbs/acre)
            soil_conditions: Current soil conditions
            fertilizer_composition: Fertilizer composition details

        Returns:
            Soil health impact assessment

        Agricultural Basis:
        - Acidification based on Bolan & Hedley (2003)
        - Salt effects from Bernstein (1975)
        - Organic matter effects from Johnston et al. (2009)
        """
        try:
            self.logger.info(f"Assessing soil health impact for {fertilizer_type}")

            fertilizer_key = self._get_fertilizer_key(fertilizer_type)

            # Assess acidification
            acidification_factor = self.acidification_factors.get(fertilizer_key, 0.0)
            n_content = fertilizer_composition.get("nitrogen_percent", 0.0)
            n_applied = application_rate * (n_content / 100.0)

            # Calculate acidification potential
            acidification_potential = acidification_factor * (n_applied / 100.0)  # Normalized

            # Estimate pH change (very rough estimate, depends on buffering capacity)
            current_ph = soil_conditions.get("ph", 6.5)
            buffering_capacity = soil_conditions.get("cec", 15.0)  # CEC indicates buffering

            # Higher CEC = more buffering = less pH change
            ph_change_estimate = acidification_potential / (buffering_capacity / 10.0)
            ph_change_estimate = max(-0.5, min(0.5, ph_change_estimate))  # Cap at ±0.5

            # Calculate lime requirement (if acidifying)
            lime_requirement = 0.0
            if acidification_potential < 0:
                # Rule of thumb: 1 ton lime per 0.5 pH unit change
                lime_requirement = abs(ph_change_estimate) * 2000.0  # lbs/acre

            # Assess salinity
            salt_index_value = self.salt_index.get(fertilizer_key, 50.0)

            # Salinity risk depends on salt index and application rate
            # High risk if salt index > 80 and rate > 200 lbs/acre
            if salt_index_value < 40 or application_rate < 100:
                salinity_risk = SeverityLevel.LOW
            elif salt_index_value < 80 or application_rate < 200:
                salinity_risk = SeverityLevel.MODERATE
            elif salt_index_value < 100 or application_rate < 400:
                salinity_risk = SeverityLevel.HIGH
            else:
                salinity_risk = SeverityLevel.VERY_HIGH

            # Assess organic matter contribution
            organic_matter_contribution = 0.0
            organic_matter_effect = "neutral"

            if fertilizer_key in ["organic_manure", "compost"]:
                # Organic amendments add significant OM
                organic_matter_contribution = application_rate * 0.40  # ~40% becomes stable OM
                organic_matter_effect = "positive"
            elif fertilizer_key in ["slow_release_coated", "slow_release_polymer"]:
                # Some organic coating material
                organic_matter_contribution = application_rate * 0.05
                organic_matter_effect = "neutral"
            else:
                # Synthetic fertilizers don't add OM
                organic_matter_effect = "neutral"

            # Assess microbial activity impact
            if fertilizer_key in ["organic_manure", "compost"]:
                microbial_activity_impact = "beneficial"
                microbial_impact_score = 8.5
            elif fertilizer_key in ["urea", "ammonium_nitrate"]:
                # High salt concentration can temporarily suppress microbes
                if salt_index_value > 80:
                    microbial_activity_impact = "temporarily harmful"
                    microbial_impact_score = 4.0
                else:
                    microbial_activity_impact = "neutral"
                    microbial_impact_score = 6.0
            else:
                microbial_activity_impact = "neutral"
                microbial_impact_score = 6.0

            # Assess soil structure effects
            if fertilizer_key in ["organic_manure", "compost"]:
                soil_structure_effect = "improves"
                aggregation_impact = "Increases soil aggregation and water holding capacity"
            elif salt_index_value > 90:
                soil_structure_effect = "degrades"
                aggregation_impact = "High salinity can disperse soil aggregates"
            else:
                soil_structure_effect = "neutral"
                aggregation_impact = None

            # Assess long-term degradation risk
            degradation_score = 0
            if acidification_potential < -2.0:
                degradation_score = degradation_score + 2  # Significant acidification
            if salinity_risk in [SeverityLevel.HIGH, SeverityLevel.VERY_HIGH]:
                degradation_score = degradation_score + 2  # Salt accumulation
            if organic_matter_effect == "positive":
                degradation_score = degradation_score - 2  # Improves soil health
            if microbial_activity_impact == "harmful":
                degradation_score = degradation_score + 1

            if degradation_score <= -1:
                long_term_degradation_risk = SeverityLevel.VERY_LOW
            elif degradation_score == 0:
                long_term_degradation_risk = SeverityLevel.LOW
            elif degradation_score <= 2:
                long_term_degradation_risk = SeverityLevel.MODERATE
            elif degradation_score <= 4:
                long_term_degradation_risk = SeverityLevel.HIGH
            else:
                long_term_degradation_risk = SeverityLevel.VERY_HIGH

            # Calculate overall soil health score (0-100, higher = better)
            acidification_score = max(0.0, 25.0 - abs(acidification_potential) * 5.0)
            salinity_score = max(0.0, 25.0 - (salt_index_value / 4.0))
            om_score = 25.0 + (organic_matter_contribution / 100.0) * 25.0
            microbial_score = (microbial_impact_score / 10.0) * 25.0

            soil_health_score = acidification_score + salinity_score + om_score + microbial_score
            soil_health_score = min(100.0, max(0.0, soil_health_score))

            # Identify positive and negative impacts
            positive_impacts = []
            if organic_matter_contribution > 50:
                positive_impacts.append(
                    f"Adds {organic_matter_contribution:.0f} lbs/acre organic matter"
                )
            if microbial_activity_impact == "beneficial":
                positive_impacts.append("Enhances soil microbial activity and diversity")
            if soil_structure_effect == "improves":
                positive_impacts.append("Improves soil structure and water holding capacity")

            negative_impacts = []
            if acidification_potential < -1.5:
                negative_impacts.append(
                    f"Acidifying effect requires {lime_requirement:.0f} lbs/acre lime to neutralize"
                )
            if salt_index_value > 80:
                negative_impacts.append(
                    f"High salt index ({salt_index_value:.0f}) may cause salt stress"
                )
            if ph_change_estimate < -0.3:
                negative_impacts.append(
                    f"May decrease soil pH by {abs(ph_change_estimate):.1f} units over time"
                )

            impact = SoilHealthImpact(
                acidification_potential=acidification_potential,
                ph_change_estimate=ph_change_estimate,
                lime_requirement_lbs_per_acre=lime_requirement,
                salt_index=salt_index_value,
                soil_salinity_risk=salinity_risk,
                organic_matter_contribution_lbs_per_acre=organic_matter_contribution,
                organic_matter_effect=organic_matter_effect,
                microbial_activity_impact=microbial_activity_impact,
                microbial_impact_score=microbial_impact_score,
                soil_structure_effect=soil_structure_effect,
                aggregation_impact=aggregation_impact,
                long_term_degradation_risk=long_term_degradation_risk,
                soil_health_impact_score=soil_health_score,
                positive_impacts=positive_impacts,
                negative_impacts=negative_impacts
            )

            self.logger.info(
                f"Soil health impact assessed: score {soil_health_score:.1f}, "
                f"acidification {acidification_potential:.1f}, salt index {salt_index_value:.0f}"
            )

            return impact

        except Exception as e:
            self.logger.error(f"Error assessing soil health impact: {str(e)}")
            raise

    async def assess_biodiversity_impact(
        self,
        fertilizer_type: str,
        ecosystem_type: str,
        proximity_to_water_m: float = 100.0
    ) -> BiodiversityImpact:
        """
        Assess biodiversity impacts on beneficial organisms and ecosystems.

        Args:
            fertilizer_type: Type of fertilizer
            ecosystem_type: Type of ecosystem (agricultural, riparian, etc.)
            proximity_to_water_m: Distance to water bodies (meters)

        Returns:
            Biodiversity impact assessment

        Agricultural Basis:
        - Based on Geiger et al. (2010) on biodiversity in agricultural landscapes
        - Aquatic toxicity from EPA ecotoxicity databases
        """
        try:
            self.logger.info(f"Assessing biodiversity impact for {fertilizer_type}")

            fertilizer_key = self._get_fertilizer_key(fertilizer_type)

            # Assess beneficial insect impact
            if fertilizer_key in ["organic_manure", "compost"]:
                beneficial_insect_impact = "positive"
                pollinator_safety_score = 9.5
            elif fertilizer_key in ["urea", "ammonium_nitrate", "dap"]:
                # Synthetic fertilizers are generally neutral to insects directly
                # but can affect habitat through plant changes
                beneficial_insect_impact = "neutral"
                pollinator_safety_score = 8.0
            else:
                beneficial_insect_impact = "neutral"
                pollinator_safety_score = 8.5

            # Assess soil organism impacts
            if fertilizer_key in ["organic_manure", "compost"]:
                earthworm_impact = "beneficial"
                beneficial_microbe_impact = "beneficial"
                soil_fauna_score = 9.0
            elif fertilizer_key == "ammonium_sulfate":
                # Can be harmful at high concentrations
                earthworm_impact = "neutral"
                beneficial_microbe_impact = "neutral"
                soil_fauna_score = 5.5
            else:
                earthworm_impact = "neutral"
                beneficial_microbe_impact = "neutral"
                soil_fauna_score = 7.0

            # Assess aquatic toxicity
            # Synthetic fertilizers have low direct toxicity but cause eutrophication
            if fertilizer_key in ["organic_manure", "compost"]:
                aquatic_toxicity_score = 7.0  # Can cause BOD issues
                fish_impact = SeverityLevel.LOW
                aquatic_invertebrate_impact = SeverityLevel.LOW
            elif fertilizer_key in ["urea", "ammonium_nitrate"]:
                # Primary impact is eutrophication, not direct toxicity
                aquatic_toxicity_score = 6.0
                if proximity_to_water_m < 30:
                    fish_impact = SeverityLevel.HIGH
                    aquatic_invertebrate_impact = SeverityLevel.MODERATE
                elif proximity_to_water_m < 100:
                    fish_impact = SeverityLevel.MODERATE
                    aquatic_invertebrate_impact = SeverityLevel.LOW
                else:
                    fish_impact = SeverityLevel.LOW
                    aquatic_invertebrate_impact = SeverityLevel.VERY_LOW
            else:
                aquatic_toxicity_score = 7.5
                fish_impact = SeverityLevel.LOW
                aquatic_invertebrate_impact = SeverityLevel.LOW

            # Assess habitat disruption risk
            if proximity_to_water_m < 30 and fertilizer_key not in ["organic_manure", "compost"]:
                habitat_disruption_risk = SeverityLevel.HIGH
            elif proximity_to_water_m < 100:
                habitat_disruption_risk = SeverityLevel.MODERATE
            else:
                habitat_disruption_risk = SeverityLevel.LOW

            # Calculate overall biodiversity score (0-100, higher = better)
            insect_score = pollinator_safety_score * 2.5
            soil_organism_score = soil_fauna_score * 2.5
            aquatic_score = aquatic_toxicity_score * 2.5
            habitat_score = 25.0

            if habitat_disruption_risk == SeverityLevel.HIGH:
                habitat_score = 10.0
            elif habitat_disruption_risk == SeverityLevel.MODERATE:
                habitat_score = 17.0

            biodiversity_score = (insect_score + soil_organism_score + aquatic_score + habitat_score) / 4.0
            biodiversity_score = min(100.0, max(0.0, biodiversity_score))

            # Species of concern
            species_of_concern = []
            if proximity_to_water_m < 50 and fish_impact in [SeverityLevel.HIGH, SeverityLevel.VERY_HIGH]:
                species_of_concern.append("Fish populations in nearby water bodies")
                species_of_concern.append("Aquatic invertebrates sensitive to nutrient enrichment")

            if fertilizer_key in ["urea", "ammonium_nitrate"] and proximity_to_water_m < 100:
                species_of_concern.append("Amphibians in riparian areas")

            # Protective measures
            protective_measures = []
            if proximity_to_water_m < 100:
                protective_measures.append("Maintain vegetated buffer strip (minimum 30m) near water")
                protective_measures.append("Avoid application when heavy rain is forecast")

            if habitat_disruption_risk in [SeverityLevel.HIGH, SeverityLevel.MODERATE]:
                protective_measures.append("Use precision application to minimize overapplication")
                protective_measures.append("Implement integrated pest management to protect beneficial insects")

            impact = BiodiversityImpact(
                beneficial_insect_impact=beneficial_insect_impact,
                pollinator_safety_score=pollinator_safety_score,
                earthworm_impact=earthworm_impact,
                beneficial_microbe_impact=beneficial_microbe_impact,
                soil_fauna_impact_score=soil_fauna_score,
                aquatic_toxicity_score=aquatic_toxicity_score,
                fish_impact=fish_impact,
                aquatic_invertebrate_impact=aquatic_invertebrate_impact,
                habitat_disruption_risk=habitat_disruption_risk,
                biodiversity_impact_score=biodiversity_score,
                species_of_concern=species_of_concern,
                protective_measures_needed=protective_measures
            )

            self.logger.info(
                f"Biodiversity impact assessed: score {biodiversity_score:.1f}"
            )

            return impact

        except Exception as e:
            self.logger.error(f"Error assessing biodiversity impact: {str(e)}")
            raise

    async def perform_lifecycle_assessment(
        self,
        fertilizer_data: Dict[str, Any],
        full_context: Dict[str, Any]
    ) -> LifecycleAssessment:
        """
        Perform comprehensive lifecycle assessment (LCA) from cradle to grave.

        Args:
            fertilizer_data: Complete fertilizer product data
            full_context: Full context including application and field data

        Returns:
            Complete lifecycle assessment

        Note: This is a simplified LCA. Full LCA requires extensive data collection.
        """
        try:
            self.logger.info("Performing lifecycle assessment")

            fertilizer_type = fertilizer_data.get("type", "unknown")
            fertilizer_name = fertilizer_data.get("name", "Unknown")
            fertilizer_key = self._get_fertilizer_key(fertilizer_type)

            # Determine fertilizer category
            fertilizer_category = self._classify_fertilizer_category(fertilizer_type, fertilizer_data)

            # Build lifecycle stages
            lifecycle_impacts = []

            # 1. Raw material extraction
            raw_material_co2e = self.production_emissions.get(fertilizer_key, 1.5) * 0.30
            lifecycle_impacts.append(LifecycleImpact(
                stage=LifecycleStage.RAW_MATERIAL_EXTRACTION,
                stage_name="Raw Material Extraction",
                co2e_emissions_kg=raw_material_co2e,
                energy_use_mj=raw_material_co2e * 20.0,
                non_renewable_resources=["Natural gas", "Phosphate rock", "Potash ore"],
                percent_of_total_impact=15.0,
                key_impact_contributors=["Mining operations", "Natural gas extraction"]
            ))

            # 2. Manufacturing
            manufacturing_co2e = self.production_emissions.get(fertilizer_key, 1.5) * 0.60
            lifecycle_impacts.append(LifecycleImpact(
                stage=LifecycleStage.MANUFACTURING,
                stage_name="Manufacturing & Processing",
                co2e_emissions_kg=manufacturing_co2e,
                energy_use_mj=manufacturing_co2e * 25.0,
                non_renewable_resources=["Natural gas for Haber-Bosch", "Electricity"],
                percent_of_total_impact=35.0,
                key_impact_contributors=["Haber-Bosch synthesis", "Ammonia production", "High pressure/temperature"]
            ))

            # 3. Packaging
            packaging_co2e = 0.05
            lifecycle_impacts.append(LifecycleImpact(
                stage=LifecycleStage.PACKAGING,
                stage_name="Packaging",
                co2e_emissions_kg=packaging_co2e,
                energy_use_mj=packaging_co2e * 15.0,
                non_renewable_resources=["Plastic bags", "Paper bags"],
                percent_of_total_impact=2.0,
                key_impact_contributors=["Bag production"]
            ))

            # 4. Transportation
            transport_co2e = 0.09  # Roughly 800km at 0.11 kg CO2e per ton-km
            lifecycle_impacts.append(LifecycleImpact(
                stage=LifecycleStage.TRANSPORTATION,
                stage_name="Transportation to Farm",
                co2e_emissions_kg=transport_co2e,
                energy_use_mj=transport_co2e * 12.0,
                non_renewable_resources=["Diesel fuel"],
                percent_of_total_impact=4.0,
                key_impact_contributors=["Truck transportation"]
            ))

            # 5. Storage
            storage_co2e = 0.01
            lifecycle_impacts.append(LifecycleImpact(
                stage=LifecycleStage.STORAGE,
                stage_name="On-Farm Storage",
                co2e_emissions_kg=storage_co2e,
                energy_use_mj=storage_co2e * 5.0,
                non_renewable_resources=[],
                percent_of_total_impact=0.5,
                key_impact_contributors=["Storage facility maintenance"]
            ))

            # 6. Application
            application_co2e = 0.05  # Equipment emissions
            lifecycle_impacts.append(LifecycleImpact(
                stage=LifecycleStage.APPLICATION,
                stage_name="Field Application",
                co2e_emissions_kg=application_co2e,
                energy_use_mj=application_co2e * 10.0,
                non_renewable_resources=["Diesel fuel"],
                percent_of_total_impact=2.5,
                key_impact_contributors=["Tractor operation", "Spreader operation"]
            ))

            # 7. In-field transformation (N2O emissions - often largest impact)
            n_percent = fertilizer_data.get("nitrogen_percent", 0.0)
            n2o_co2e = 0.0
            if n_percent > 0:
                n2o_adjustment = self.n2o_adjustment_factors.get(fertilizer_key, 1.0)
                n2o_co2e = (n_percent / 100.0) * self.n2o_co2e_factor * n2o_adjustment

            lifecycle_impacts.append(LifecycleImpact(
                stage=LifecycleStage.IN_FIELD_TRANSFORMATION,
                stage_name="In-Field Transformations",
                co2e_emissions_kg=n2o_co2e,
                energy_use_mj=0.0,  # No direct energy use
                non_renewable_resources=[],
                percent_of_total_impact=40.0 if n2o_co2e > 0.5 else 5.0,
                key_impact_contributors=["N2O emissions from soil", "Microbial denitrification"]
            ))

            # 8. End of life
            eol_co2e = 0.02
            lifecycle_impacts.append(LifecycleImpact(
                stage=LifecycleStage.END_OF_LIFE,
                stage_name="End of Life",
                co2e_emissions_kg=eol_co2e,
                energy_use_mj=eol_co2e * 8.0,
                non_renewable_resources=[],
                percent_of_total_impact=1.0,
                key_impact_contributors=["Packaging disposal"]
            ))

            # Calculate totals
            total_co2e = sum(stage.co2e_emissions_kg for stage in lifecycle_impacts)
            total_energy = sum(stage.energy_use_mj for stage in lifecycle_impacts)

            # Find dominant stage
            dominant_stage = max(lifecycle_impacts, key=lambda x: x.co2e_emissions_kg)
            dominant_stage_percent = (dominant_stage.co2e_emissions_kg / total_co2e * 100.0) if total_co2e > 0 else 0.0

            # Generate improvement opportunities
            improvement_opportunities = []
            if dominant_stage.stage == LifecycleStage.MANUFACTURING:
                improvement_opportunities.append("Use renewable energy in manufacturing")
                improvement_opportunities.append("Improve energy efficiency of Haber-Bosch process")
            if dominant_stage.stage == LifecycleStage.IN_FIELD_TRANSFORMATION:
                improvement_opportunities.append("Use nitrification inhibitors to reduce N2O emissions")
                improvement_opportunities.append("Implement precision agriculture for optimal N rates")
                improvement_opportunities.append("Switch to slow-release or stabilized nitrogen sources")
            if transport_co2e > total_co2e * 0.10:
                improvement_opportunities.append("Source fertilizer from closer suppliers")

            improvement_opportunities.append("Follow 4R Nutrient Stewardship (Right Source, Rate, Time, Place)")

            # Data quality (simplified LCA has moderate quality)
            data_quality_score = 6.5

            lca = LifecycleAssessment(
                fertilizer_name=fertilizer_name,
                fertilizer_category=fertilizer_category,
                functional_unit="per kg of fertilizer applied",
                lifecycle_impacts=lifecycle_impacts,
                total_co2e_kg=total_co2e,
                total_energy_mj=total_energy,
                total_water_liters=None,  # Not tracked in this simplified LCA
                dominant_impact_stage=dominant_stage.stage,
                dominant_stage_percent=dominant_stage_percent,
                improvement_opportunities=improvement_opportunities,
                methodology_standard="Simplified ISO 14040:2006",
                data_quality_score=data_quality_score,
                uncertainty_range_percent=25.0
            )

            self.logger.info(
                f"LCA completed: {total_co2e:.2f} kg CO2e total, "
                f"dominant stage: {dominant_stage.stage.value}"
            )

            return lca

        except Exception as e:
            self.logger.error(f"Error performing lifecycle assessment: {str(e)}")
            raise

    def calculate_environmental_score(
        self,
        carbon_footprint: CarbonFootprint,
        water_quality_impact: WaterQualityImpact,
        soil_health_impact: SoilHealthImpact,
        biodiversity_impact: BiodiversityImpact
    ) -> EnvironmentalScore:
        """
        Calculate aggregated environmental score combining all impact categories.

        Args:
            carbon_footprint: Carbon footprint assessment
            water_quality_impact: Water quality impact
            soil_health_impact: Soil health impact
            biodiversity_impact: Biodiversity impact

        Returns:
            Overall environmental score (0-100 scale, higher = better)
        """
        try:
            self.logger.info("Calculating overall environmental score")

            # Extract individual scores
            carbon_score = carbon_footprint.carbon_impact_score
            water_score = water_quality_impact.water_quality_impact_score
            soil_score = soil_health_impact.soil_health_impact_score
            biodiversity_score = biodiversity_impact.biodiversity_impact_score

            # Define weighting scheme (can be adjusted based on priorities)
            # Default weights emphasize GHG and water quality
            weighting_scheme = {
                "carbon_footprint": 0.35,  # 35% weight
                "water_quality": 0.30,  # 30% weight
                "soil_health": 0.20,  # 20% weight
                "biodiversity": 0.15   # 15% weight
            }

            # Calculate weighted overall score
            overall_score = (
                carbon_score * weighting_scheme["carbon_footprint"] +
                water_score * weighting_scheme["water_quality"] +
                soil_score * weighting_scheme["soil_health"] +
                biodiversity_score * weighting_scheme["biodiversity"]
            )

            # Determine rating category
            if overall_score >= 80.0:
                rating = "Excellent"
            elif overall_score >= 65.0:
                rating = "Good"
            elif overall_score >= 50.0:
                rating = "Fair"
            elif overall_score >= 35.0:
                rating = "Poor"
            else:
                rating = "Very Poor"

            # Identify strongest and weakest areas
            scores_dict = {
                "Carbon Footprint": carbon_score,
                "Water Quality": water_score,
                "Soil Health": soil_score,
                "Biodiversity": biodiversity_score
            }

            strongest_area = max(scores_dict, key=scores_dict.get)
            weakest_area = min(scores_dict, key=scores_dict.get)

            # Check organic certification eligibility (simplified check)
            organic_eligible = (
                carbon_score > 70.0 and
                soil_score > 70.0 and
                water_score > 60.0
            )

            # Sustainability certification potential
            sustainability_certs = []
            if overall_score >= 75.0:
                sustainability_certs.append("USDA Organic (if natural inputs)")
                sustainability_certs.append("4R Nutrient Stewardship Certified")
            if carbon_score >= 80.0:
                sustainability_certs.append("Low Carbon Fertilizer Certification")
            if water_score >= 80.0:
                sustainability_certs.append("Water Quality Friendly")

            score = EnvironmentalScore(
                carbon_footprint_score=carbon_score,
                water_quality_score=water_score,
                soil_health_score=soil_score,
                biodiversity_score=biodiversity_score,
                overall_environmental_score=overall_score,
                weighting_scheme=weighting_scheme,
                environmental_rating=rating,
                strongest_area=strongest_area,
                weakest_area=weakest_area,
                percentile_rank=None,  # Would need database of products for comparison
                organic_certification_eligible=organic_eligible,
                sustainability_certification_potential=sustainability_certs
            )

            self.logger.info(
                f"Environmental score calculated: {overall_score:.1f} ({rating}), "
                f"strongest: {strongest_area}, weakest: {weakest_area}"
            )

            return score

        except Exception as e:
            self.logger.error(f"Error calculating environmental score: {str(e)}")
            raise

    def generate_mitigation_recommendations(
        self,
        carbon_footprint: CarbonFootprint,
        water_quality_impact: WaterQualityImpact,
        soil_health_impact: SoilHealthImpact,
        biodiversity_impact: BiodiversityImpact,
        application_data: Dict[str, Any],
        field_conditions: Dict[str, Any]
    ) -> List[MitigationRecommendation]:
        """
        Generate prioritized mitigation recommendations to reduce environmental impact.

        Args:
            carbon_footprint: Carbon footprint assessment
            water_quality_impact: Water quality impact
            soil_health_impact: Soil health impact
            biodiversity_impact: Biodiversity impact
            application_data: Application details
            field_conditions: Field conditions

        Returns:
            List of mitigation recommendations prioritized by effectiveness
        """
        try:
            self.logger.info("Generating mitigation recommendations")

            recommendations = []
            rec_id = 1

            # High priority GHG mitigation (if carbon footprint is significant)
            if carbon_footprint.carbon_impact_score < 60.0:
                # N2O is usually the biggest contributor
                if "N2O" in str(carbon_footprint.primary_emission_sources):
                    recommendations.append(MitigationRecommendation(
                        recommendation_id=f"MIT-{rec_id:03d}",
                        category=ImpactCategory.GREENHOUSE_GAS,
                        priority="High",
                        recommendation="Use nitrification inhibitors (e.g., Nitrapyrin, DCD) to reduce N2O emissions",
                        rationale="N2O emissions account for major portion of carbon footprint. Inhibitors slow conversion to nitrate, reducing N2O by 30-50%.",
                        impact_reduction_percent=35.0,
                        environmental_benefit="Reduces greenhouse gas emissions while maintaining nitrogen availability",
                        implementation_difficulty="Easy",
                        cost_implication="Additional cost ($5-15/acre)",
                        equipment_needed=["Standard application equipment"],
                        agronomic_trade_offs=["May need to adjust timing slightly"],
                        effectiveness_conditions=["Most effective in fall applications", "Warm, moist soils see greatest benefit"],
                        research_support=["Bouwman et al. (2002)", "IPCC (2019)"]
                    ))
                    rec_id = rec_id + 1

                # Recommend precision application
                recommendations.append(MitigationRecommendation(
                    recommendation_id=f"MIT-{rec_id:03d}",
                    category=ImpactCategory.GREENHOUSE_GAS,
                    priority="High",
                    recommendation="Implement variable rate application based on soil testing and yield goals",
                    rationale="Precision agriculture reduces overapplication, lowering total N input and associated N2O emissions",
                    impact_reduction_percent=20.0,
                    environmental_benefit="Reduces both carbon footprint and cost while maintaining yields",
                    implementation_difficulty="Moderate",
                    cost_implication="Cost savings from reduced fertilizer use",
                    equipment_needed=["VRT-capable spreader", "Soil test data", "Yield maps"],
                    agronomic_trade_offs=[],
                    effectiveness_conditions=["Requires detailed field mapping", "Works best with professional agronomist support"],
                    research_support=["Robertson & Vitousek (2009)"]
                ))
                rec_id = rec_id + 1

            # Water quality mitigation (if significant risk)
            if water_quality_impact.water_quality_impact_score < 60.0:
                # Leaching risk
                if water_quality_impact.nitrate_leaching_risk_score > 0.6:
                    recommendations.append(MitigationRecommendation(
                        recommendation_id=f"MIT-{rec_id:03d}",
                        category=ImpactCategory.WATER_POLLUTION,
                        priority="High",
                        recommendation="Split nitrogen applications into 2-3 applications timed with crop demand",
                        rationale="Reduces soil N concentration at any one time, lowering leaching losses by 30-40%",
                        impact_reduction_percent=35.0,
                        environmental_benefit="Protects groundwater quality while improving N use efficiency",
                        implementation_difficulty="Easy",
                        cost_implication="Neutral to slight cost increase (additional application trip)",
                        equipment_needed=["Standard application equipment"],
                        agronomic_trade_offs=["Requires 2-3 trips instead of 1"],
                        effectiveness_conditions=["Most effective on sandy soils", "High rainfall areas benefit most"],
                        research_support=["Randall & Vetsch (2005)", "Kanwar et al. (1997)"]
                    ))
                    rec_id = rec_id + 1

                # Runoff risk
                if water_quality_impact.phosphorus_runoff_risk_score > 0.6:
                    recommendations.append(MitigationRecommendation(
                        recommendation_id=f"MIT-{rec_id:03d}",
                        category=ImpactCategory.WATER_POLLUTION,
                        priority="High",
                        recommendation="Incorporate fertilizer within 24 hours and maintain cover on slopes >4%",
                        rationale="Incorporation reduces P runoff by 50-70%. Cover crops prevent soil erosion.",
                        impact_reduction_percent=60.0,
                        environmental_benefit="Dramatically reduces P loss to surface water and eutrophication risk",
                        implementation_difficulty="Moderate",
                        cost_implication="Neutral (incorporation is good practice)",
                        equipment_needed=["Tillage equipment or injection system"],
                        agronomic_trade_offs=["May not be compatible with no-till"],
                        effectiveness_conditions=["Most critical near surface water", "Essential on sloping fields"],
                        research_support=["Carpenter et al. (2008)"]
                    ))
                    rec_id = rec_id + 1

                # Buffer strips
                distance_to_water = field_conditions.get("soil", {}).get("distance_to_water_m", 200)
                if distance_to_water < 100:
                    recommendations.append(MitigationRecommendation(
                        recommendation_id=f"MIT-{rec_id:03d}",
                        category=ImpactCategory.WATER_POLLUTION,
                        priority="High",
                        recommendation="Establish 30-50m vegetated buffer strip between field and water body",
                        rationale="Buffer strips filter runoff, removing 40-80% of nutrients before reaching water",
                        impact_reduction_percent=60.0,
                        environmental_benefit="Protects aquatic ecosystems, provides habitat for beneficial organisms",
                        implementation_difficulty="Moderate",
                        cost_implication="Loss of productive area, but may qualify for conservation payments",
                        equipment_needed=["Native grass seed", "Planting equipment"],
                        agronomic_trade_offs=["Removes land from production"],
                        effectiveness_conditions=["Essential for fields <100m from water", "Required in many regulations"],
                        research_support=["USDA NRCS Conservation Practice Standard 393"]
                    ))
                    rec_id = rec_id + 1

            # Soil health mitigation
            if soil_health_impact.soil_health_impact_score < 60.0:
                # Acidification
                if soil_health_impact.acidification_potential < -1.5:
                    recommendations.append(MitigationRecommendation(
                        recommendation_id=f"MIT-{rec_id:03d}",
                        category=ImpactCategory.SOIL_ACIDIFICATION,
                        priority="Medium",
                        recommendation=f"Apply {soil_health_impact.lime_requirement_lbs_per_acre:.0f} lbs/acre lime to neutralize acidification",
                        rationale="Counteracts acidifying effect, maintaining optimal soil pH for nutrient availability",
                        impact_reduction_percent=100.0,
                        environmental_benefit="Maintains soil health and productivity long-term",
                        implementation_difficulty="Easy",
                        cost_implication="Additional cost (~$50-100/acre including lime and application)",
                        equipment_needed=["Lime spreader"],
                        agronomic_trade_offs=[],
                        effectiveness_conditions=["Apply lime 3-6 months before planting for full effect"],
                        research_support=["Bolan & Hedley (2003)"]
                    ))
                    rec_id = rec_id + 1

                # Low organic matter
                if soil_health_impact.organic_matter_contribution_lbs_per_acre < 50:
                    recommendations.append(MitigationRecommendation(
                        recommendation_id=f"MIT-{rec_id:03d}",
                        category=ImpactCategory.SOIL_ACIDIFICATION,
                        priority="Medium",
                        recommendation="Supplement with organic amendments (compost, manure) or use slow-release organic-based fertilizers",
                        rationale="Builds soil organic matter, improves water holding capacity and nutrient cycling",
                        impact_reduction_percent=30.0,
                        environmental_benefit="Enhances soil health, increases carbon sequestration",
                        implementation_difficulty="Moderate",
                        cost_implication="May increase cost depending on amendment source",
                        equipment_needed=["Manure spreader or compost applicator"],
                        agronomic_trade_offs=["Lower nutrient concentration requires higher application rates"],
                        effectiveness_conditions=["Long-term strategy", "Benefits accumulate over years"],
                        research_support=["Johnston et al. (2009)"]
                    ))
                    rec_id = rec_id + 1

            # Biodiversity protection
            if biodiversity_impact.biodiversity_impact_score < 65.0:
                if len(biodiversity_impact.protective_measures_needed) > 0:
                    recommendations.append(MitigationRecommendation(
                        recommendation_id=f"MIT-{rec_id:03d}",
                        category=ImpactCategory.BIODIVERSITY,
                        priority="Medium",
                        recommendation="Follow integrated biodiversity management: buffer strips, pollinator plantings, habitat conservation",
                        rationale="Protects beneficial organisms while maintaining agricultural productivity",
                        impact_reduction_percent=40.0,
                        environmental_benefit="Maintains ecosystem services like pollination and natural pest control",
                        implementation_difficulty="Moderate",
                        cost_implication="Neutral to slight cost increase",
                        equipment_needed=[],
                        agronomic_trade_offs=["May need to coordinate with other practices"],
                        effectiveness_conditions=["Most effective when combined with IPM"],
                        research_support=["Geiger et al. (2010)"]
                    ))
                    rec_id = rec_id + 1

            # Universal 4R recommendation
            recommendations.append(MitigationRecommendation(
                recommendation_id=f"MIT-{rec_id:03d}",
                category=ImpactCategory.GREENHOUSE_GAS,
                priority="High",
                recommendation="Implement 4R Nutrient Stewardship: Right Source, Right Rate, Right Time, Right Place",
                rationale="Comprehensive approach addresses all environmental impacts simultaneously",
                impact_reduction_percent=50.0,
                environmental_benefit="Reduces all environmental impacts while optimizing agronomic performance",
                implementation_difficulty="Moderate",
                cost_implication="Cost savings from improved efficiency",
                equipment_needed=["Soil testing", "Professional agronomist consultation"],
                agronomic_trade_offs=[],
                effectiveness_conditions=["Requires commitment to best management practices"],
                research_support=["International Plant Nutrition Institute 4R Framework"]
            ))

            # Sort by priority and impact reduction
            priority_order = {"High": 3, "Medium": 2, "Low": 1}
            recommendations.sort(
                key=lambda x: (priority_order.get(x.priority, 0), x.impact_reduction_percent),
                reverse=True
            )

            self.logger.info(f"Generated {len(recommendations)} mitigation recommendations")

            return recommendations

        except Exception as e:
            self.logger.error(f"Error generating mitigation recommendations: {str(e)}")
            raise

    async def compare_environmental_impacts(
        self,
        fertilizer_options: List[Dict[str, Any]],
        application_data: Dict[str, Any],
        field_conditions: Dict[str, Any]
    ) -> EnvironmentalComparisonResult:
        """
        Compare environmental impacts across multiple fertilizer options.

        Args:
            fertilizer_options: List of fertilizer products to compare
            application_data: Application details
            field_conditions: Field conditions

        Returns:
            Comparative environmental impact analysis
        """
        try:
            self.logger.info(f"Comparing environmental impacts for {len(fertilizer_options)} fertilizers")

            # Assess each fertilizer
            assessments = []
            for fertilizer in fertilizer_options:
                assessment = await self.assess_environmental_impact(
                    fertilizer_data=fertilizer,
                    application_data=application_data,
                    field_conditions=field_conditions
                )
                assessments.append(assessment)

            # Create rankings
            carbon_ranking = sorted(
                assessments,
                key=lambda x: x.carbon_footprint.carbon_impact_score,
                reverse=True
            )
            carbon_ranking_names = [a.fertilizer_name for a in carbon_ranking]

            water_ranking = sorted(
                assessments,
                key=lambda x: x.water_quality_impact.water_quality_impact_score,
                reverse=True
            )
            water_ranking_names = [a.fertilizer_name for a in water_ranking]

            soil_ranking = sorted(
                assessments,
                key=lambda x: x.soil_health_impact.soil_health_impact_score,
                reverse=True
            )
            soil_ranking_names = [a.fertilizer_name for a in soil_ranking]

            biodiversity_ranking = sorted(
                assessments,
                key=lambda x: x.biodiversity_impact.biodiversity_impact_score,
                reverse=True
            )
            biodiversity_ranking_names = [a.fertilizer_name for a in biodiversity_ranking]

            overall_ranking = sorted(
                assessments,
                key=lambda x: x.environmental_score.overall_environmental_score,
                reverse=True
            )
            overall_ranking_names = [a.fertilizer_name for a in overall_ranking]

            # Best overall choice
            recommended = overall_ranking[0]
            recommendation_rationale = (
                f"{recommended.fertilizer_name} has the best overall environmental score "
                f"({recommended.environmental_score.overall_environmental_score:.1f}) with "
                f"strengths in {recommended.environmental_score.strongest_area}."
            )

            # Identify key differentiators
            key_differentiators = []

            # Carbon footprint differences
            carbon_range = (
                carbon_ranking[0].carbon_footprint.carbon_impact_score -
                carbon_ranking[-1].carbon_footprint.carbon_impact_score
            )
            if carbon_range > 20.0:
                key_differentiators.append(
                    f"Carbon footprint varies significantly ({carbon_range:.0f} points): "
                    f"{carbon_ranking[0].fertilizer_name} is best, {carbon_ranking[-1].fertilizer_name} is worst"
                )

            # Water quality differences
            water_range = (
                water_ranking[0].water_quality_impact.water_quality_impact_score -
                water_ranking[-1].water_quality_impact.water_quality_impact_score
            )
            if water_range > 15.0:
                key_differentiators.append(
                    f"Water quality impact varies ({water_range:.0f} points): "
                    f"{water_ranking[0].fertilizer_name} has lowest impact"
                )

            # Environmental trade-offs
            trade_offs = {}
            for i, assessment in enumerate(assessments):
                trade_off_notes = []

                if assessment.carbon_footprint.carbon_impact_score > 75.0:
                    trade_off_notes.append("Low carbon footprint")
                if assessment.water_quality_impact.water_quality_impact_score > 75.0:
                    trade_off_notes.append("Low water pollution risk")
                if assessment.soil_health_impact.soil_health_impact_score > 75.0:
                    trade_off_notes.append("Positive soil health effects")

                if assessment.carbon_footprint.carbon_impact_score < 50.0:
                    trade_off_notes.append("High carbon footprint")
                if assessment.water_quality_impact.water_quality_impact_score < 50.0:
                    trade_off_notes.append("Higher water pollution risk")

                trade_offs[assessment.fertilizer_name] = ", ".join(trade_off_notes) if trade_off_notes else "Balanced impacts"

            comparison = EnvironmentalComparisonResult(
                comparison_id=f"env_comp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                generated_at=datetime.utcnow(),
                fertilizer_assessments=assessments,
                carbon_footprint_ranking=carbon_ranking_names,
                water_quality_ranking=water_ranking_names,
                soil_health_ranking=soil_ranking_names,
                biodiversity_ranking=biodiversity_ranking_names,
                overall_ranking=overall_ranking_names,
                recommended_fertilizer=recommended.fertilizer_name,
                recommendation_rationale=recommendation_rationale,
                key_differentiators=key_differentiators,
                environmental_trade_offs=trade_offs
            )

            self.logger.info(
                f"Environmental comparison completed. Recommended: {recommended.fertilizer_name}"
            )

            return comparison

        except Exception as e:
            self.logger.error(f"Error comparing environmental impacts: {str(e)}")
            raise

    # Helper methods

    def _classify_fertilizer_category(
        self,
        fertilizer_type: str,
        fertilizer_data: Dict[str, Any]
    ) -> FertilizerCategory:
        """Classify fertilizer into environmental category."""
        type_lower = fertilizer_type.lower()

        if "organic" in type_lower or "manure" in type_lower:
            if "manure" in type_lower:
                return FertilizerCategory.ORGANIC_ANIMAL_MANURE
            elif "compost" in type_lower:
                return FertilizerCategory.ORGANIC_COMPOST
            else:
                return FertilizerCategory.ORGANIC_GREEN_MANURE

        if "slow" in type_lower or "controlled" in type_lower:
            if "coated" in type_lower:
                return FertilizerCategory.SLOW_RELEASE_COATED
            else:
                return FertilizerCategory.SLOW_RELEASE_POLYMER

        if "bio" in type_lower or "inoculant" in type_lower:
            return FertilizerCategory.BIOFERTILIZER

        # Check nutrient content for synthetic classification
        n_percent = fertilizer_data.get("nitrogen_percent", 0.0)
        p_percent = fertilizer_data.get("phosphorus_percent", 0.0)
        k_percent = fertilizer_data.get("potassium_percent", 0.0)

        if n_percent > 10.0:
            return FertilizerCategory.SYNTHETIC_NITROGEN
        elif p_percent > 10.0:
            return FertilizerCategory.SYNTHETIC_PHOSPHORUS
        elif k_percent > 10.0:
            return FertilizerCategory.SYNTHETIC_POTASSIUM

        return FertilizerCategory.SYNTHETIC_NITROGEN  # Default

    def _get_fertilizer_key(self, fertilizer_type: str) -> str:
        """Convert fertilizer type to lookup key."""
        type_map = {
            "urea": "urea",
            "ammonium nitrate": "ammonium_nitrate",
            "ammonium sulfate": "ammonium_sulfate",
            "anhydrous ammonia": "anhydrous_ammonia",
            "uan": "uan_solution",
            "dap": "dap",
            "map": "map",
            "tsp": "tsp",
            "potash": "potash_kcl",
            "manure": "organic_manure",
            "compost": "compost",
            "slow release coated": "slow_release_coated",
            "slow release polymer": "slow_release_polymer",
        }

        type_lower = fertilizer_type.lower()
        for key, value in type_map.items():
            if key in type_lower:
                return value

        return "urea"  # Default fallback

    def _assess_regulatory_compliance(
        self,
        fertilizer_type: str,
        water_quality_impact: WaterQualityImpact,
        field_conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess regulatory compliance status."""
        compliance = {
            "epa_water_quality": "compliant",
            "organic_certification": "not_applicable",
            "state_regulations": "check_local",
            "warnings": []
        }

        # EPA water quality
        if water_quality_impact.groundwater_contamination_risk in [SeverityLevel.HIGH, SeverityLevel.VERY_HIGH]:
            compliance["warnings"].append(
                "High groundwater contamination risk. May require nutrient management plan in some states."
            )

        # Organic certification
        fertilizer_key = self._get_fertilizer_key(fertilizer_type)
        if fertilizer_key in self.organic_certification_criteria["allowed_inputs"]:
            compliance["organic_certification"] = "eligible"
        elif fertilizer_key in self.organic_certification_criteria["prohibited_inputs"]:
            compliance["organic_certification"] = "not_eligible"

        # Proximity to water
        if water_quality_impact.distance_to_surface_water_m and water_quality_impact.distance_to_surface_water_m < 30:
            compliance["warnings"].append(
                "Field is within 30m of surface water. Buffer strips may be required by state law."
            )

        # Wellhead protection area
        if water_quality_impact.in_wellhead_protection_area:
            compliance["warnings"].append(
                "Field is in wellhead protection area. Special restrictions may apply."
            )

        return compliance

    def _get_data_sources(self) -> List[str]:
        """Get list of data sources used."""
        return [
            "IPCC 2019 Guidelines for National Greenhouse Gas Inventories",
            "Ecoinvent LCA Database v3.8",
            "GREET Model (Argonne National Laboratory)",
            "EPA MOVES Emission Model",
            "EPA Ecotoxicity Database",
            "USDA NRCS Soil Health Assessment",
        ]

    def _get_agricultural_sources(self) -> List[str]:
        """Get list of agricultural research sources."""
        return [
            "IPCC (2019): Refinement to the 2006 IPCC Guidelines for National Greenhouse Gas Inventories",
            "Bouwman et al. (2002): Emissions of N2O and NO from fertilized fields (Global Biogeochem. Cycles)",
            "Galloway et al. (2008): Transformation of the Nitrogen Cycle: Recent trends, questions, and potential solutions (Science)",
            "Carpenter et al. (2008): Nonpoint pollution of surface waters with phosphorus and nitrogen (Ecological Applications)",
            "Robertson & Vitousek (2009): Nitrogen in Agriculture: Balancing the cost of an essential resource (Annual Review of Plant Biology)",
            "Kanwar et al. (1997): Nitrate leaching in subsurface drainage as affected by nitrogen fertilizer rate",
            "Randall & Vetsch (2005): Nitrate losses in subsurface drainage from a corn-soybean rotation as affected by time of nitrogen application",
            "Bolan & Hedley (2003): Role of carbon, nitrogen and sulfur cycles in soil acidification",
            "Johnston et al. (2009): Soil organic matter: its importance in sustainable agriculture and carbon dioxide fluxes",
            "Geiger et al. (2010): Persistent negative effects of pesticides on biodiversity and biological control potential",
        ]
