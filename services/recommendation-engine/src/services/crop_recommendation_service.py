"""
Crop Recommendation Service

Provides crop selection and variety recommendations based on soil and climate data.
"""

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import numpy as np
try:
    from ..models.agricultural_models import (
        RecommendationRequest,
        RecommendationItem,
        ConfidenceFactors
    )
    # Import filter models for extended functionality
    try:
        from ...crop_taxonomy.src.models.crop_filtering_models import (
            TaxonomyFilterCriteria
        )
    except ImportError:
        from services.crop_taxonomy.src.models.crop_filtering_models import (
            TaxonomyFilterCriteria
        )
except ImportError:
    from models.agricultural_models import (
        RecommendationRequest,
        RecommendationItem,
        ConfidenceFactors
    )
    # Define minimal filter models as fallback
    from pydantic import BaseModel
    class TaxonomyFilterCriteria(BaseModel):
        pass


class CropRecommendationService:
    """Service for crop selection and variety recommendations."""
    
    def __init__(self):
        """Initialize crop recommendation service with crop database."""
        self.crop_database = self._build_crop_database()
        self.suitability_matrix = self._build_suitability_matrix()
        # Import climate service for auto-detection if needed
        try:
            from .climate_integration_service import climate_integration_service
            self.climate_service = climate_integration_service
        except ImportError:
            try:
                from services.climate_integration_service import climate_integration_service
                self.climate_service = climate_integration_service
            except ImportError:
                self.climate_service = None
        
        # Import planting date service for timing calculations
        try:
            from .planting_date_service import planting_date_service
            self.planting_date_service = planting_date_service
        except ImportError:
            try:
                from services.planting_date_service import planting_date_service
                self.planting_date_service = planting_date_service
            except ImportError:
                self.planting_date_service = None

        # Initialize variety intelligence components
        self.variety_database = self._build_variety_database()

        try:
            from .market_price_service import MarketPriceService
            self.market_price_service = MarketPriceService()
        except ImportError:
            try:
                from services.market_price_service import MarketPriceService
                self.market_price_service = MarketPriceService()
            except ImportError:
                self.market_price_service = None
    
    def _build_crop_database(self) -> Dict[str, Dict[str, Any]]:
        """Build crop characteristics database."""
        return {
            "corn": {
                "optimal_ph_range": (6.0, 6.8),
                "minimum_ph": 5.5,
                "maximum_ph": 7.5,
                "optimal_om_range": (3.0, 5.0),
                "phosphorus_requirement": "medium_high",
                "potassium_requirement": "high",
                "nitrogen_requirement": "high",
                "drainage_requirement": "well_drained",
                "climate_zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"],
                "growing_degree_days": 2500,
                "typical_yield_range": (120, 200),  # bu/acre
                "economic_viability_min_acres": 50
            },
            "soybean": {
                "optimal_ph_range": (6.0, 7.0),
                "minimum_ph": 5.8,
                "maximum_ph": 7.5,
                "optimal_om_range": (2.5, 4.5),
                "phosphorus_requirement": "medium",
                "potassium_requirement": "medium_high",
                "nitrogen_requirement": "low",  # Nitrogen fixing
                "drainage_requirement": "well_drained",
                "climate_zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"],
                "growing_degree_days": 2200,
                "typical_yield_range": (40, 70),  # bu/acre
                "economic_viability_min_acres": 30
            },
            "wheat": {
                "optimal_ph_range": (6.0, 7.0),
                "minimum_ph": 5.5,
                "maximum_ph": 8.0,
                "optimal_om_range": (2.0, 4.0),
                "phosphorus_requirement": "medium",
                "potassium_requirement": "medium",
                "nitrogen_requirement": "medium_high",
                "drainage_requirement": "well_drained",
                "climate_zones": ["2a", "2b", "3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b"],
                "growing_degree_days": 2000,
                "typical_yield_range": (50, 80),  # bu/acre
                "economic_viability_min_acres": 40
            }
        }
    
    def _build_suitability_matrix(self) -> Dict[str, Dict[str, float]]:
        """Build suitability scoring matrix for different conditions."""
        return {
            "ph_suitability": {
                "optimal": 1.0,
                "acceptable": 0.8,
                "marginal": 0.6,
                "poor": 0.3
            },
            "nutrient_suitability": {
                "high": 1.0,
                "medium": 0.8,
                "low": 0.5,
                "very_low": 0.2
            },
            "climate_suitability": {
                "optimal": 1.0,
                "good": 0.9,
                "acceptable": 0.7,
                "marginal": 0.5
            }
        }

    def _build_variety_database(self) -> Dict[str, List[Dict[str, Any]]]:
        """Build in-memory database of representative crop varieties."""
        variety_database: Dict[str, List[Dict[str, Any]]] = {}

        corn_varieties: List[Dict[str, Any]] = []

        corn_variety_one = {
            "crop_name": "corn",
            "name": "Pioneer P1197AMXT",
            "company": "Pioneer",
            "relative_maturity": 119,
            "yield_potential_percentile": 95,
            "yield_stability_rating": 8.5,
            "market_acceptance_score": 4.2,
            "standability_rating": 8.0,
            "expected_yield_bu_acre": 205,
            "yield_range_bu_acre": (190, 215),
            "seed_cost_per_unit": 320.0,
            "units_per_acre": 1.0,
            "additional_management_cost_per_acre": 45.0,
            "disease_resistances": {
                "northern_corn_leaf_blight": "resistant",
                "gray_leaf_spot": "moderately_resistant",
                "rust": "resistant",
                "anthracnose": "moderately_resistant"
            },
            "stress_tolerances": ["drought", "heat"],
            "trait_stack": ["Roundup Ready 2", "LibertyLink", "XtendFlex"],
            "adapted_regions": ["Iowa", "Illinois", "Indiana", "Ohio"],
            "recommended_climate_zones": ["4a", "4b", "5a", "5b", "6a"],
            "optimal_ph_range": (6.0, 6.8),
            "minimum_ph": 5.8,
            "maximum_ph": 7.4,
            "seed_availability": "high",
            "release_year": 2020,
            "management_notes": [
                "Responds well to intensive fertility programs",
                "Monitor canopy for gray leaf spot if humidity remains high"
            ]
        }
        corn_varieties.append(corn_variety_one)

        corn_variety_two = {
            "crop_name": "corn",
            "name": "Dekalb DKC62-08",
            "company": "Bayer/Dekalb",
            "relative_maturity": 108,
            "yield_potential_percentile": 88,
            "yield_stability_rating": 7.8,
            "market_acceptance_score": 3.8,
            "standability_rating": 8.0,
            "expected_yield_bu_acre": 192,
            "yield_range_bu_acre": (178, 200),
            "seed_cost_per_unit": 295.0,
            "units_per_acre": 1.0,
            "additional_management_cost_per_acre": 35.0,
            "disease_resistances": {
                "northern_corn_leaf_blight": "moderately_resistant",
                "gray_leaf_spot": "resistant",
                "goss_wilt": "moderately_resistant"
            },
            "stress_tolerances": ["drought"],
            "trait_stack": ["Roundup Ready 2"],
            "adapted_regions": ["Iowa", "Nebraska", "Minnesota"],
            "recommended_climate_zones": ["3b", "4a", "4b", "5a"],
            "optimal_ph_range": (5.8, 7.0),
            "minimum_ph": 5.5,
            "maximum_ph": 7.4,
            "seed_availability": "high",
            "release_year": 2019,
            "management_notes": [
                "Prefers well-drained soils with medium organic matter",
                "Scout for northern corn leaf blight under prolonged humidity"
            ]
        }
        corn_varieties.append(corn_variety_two)

        corn_variety_three = {
            "crop_name": "corn",
            "name": "Syngenta NK603",
            "company": "Syngenta",
            "relative_maturity": 105,
            "yield_potential_percentile": 90,
            "yield_stability_rating": 8.0,
            "market_acceptance_score": 3.9,
            "standability_rating": 7.0,
            "expected_yield_bu_acre": 188,
            "yield_range_bu_acre": (170, 198),
            "seed_cost_per_unit": 285.0,
            "units_per_acre": 1.0,
            "additional_management_cost_per_acre": 30.0,
            "disease_resistances": {
                "northern_corn_leaf_blight": "moderately_resistant",
                "gray_leaf_spot": "moderately_resistant",
                "southern_rust": "susceptible"
            },
            "stress_tolerances": ["drought", "heat"],
            "trait_stack": ["Roundup Ready 2"],
            "adapted_regions": ["Kansas", "Missouri", "Nebraska"],
            "recommended_climate_zones": ["5a", "5b", "6a", "6b"],
            "optimal_ph_range": (5.9, 6.9),
            "minimum_ph": 5.5,
            "maximum_ph": 7.2,
            "seed_availability": "moderate",
            "release_year": 2018,
            "management_notes": [
                "Consider fungicide for rust pressure in hot, humid seasons",
                "Maintain residue management to support standability"
            ]
        }
        corn_varieties.append(corn_variety_three)

        variety_database["corn"] = corn_varieties

        soybean_varieties: List[Dict[str, Any]] = []

        soybean_variety_one = {
            "crop_name": "soybean",
            "name": "Asgrow AG3431",
            "company": "Bayer/Asgrow",
            "relative_maturity": 33,
            "yield_potential_percentile": 92,
            "yield_stability_rating": 8.2,
            "market_acceptance_score": 4.0,
            "standability_rating": 8.0,
            "expected_yield_bu_acre": 66,
            "yield_range_bu_acre": (60, 70),
            "seed_cost_per_unit": 63.0,
            "units_per_acre": 1.0,
            "additional_management_cost_per_acre": 18.0,
            "disease_resistances": {
                "sudden_death_syndrome": "resistant",
                "brown_stem_rot": "moderately_resistant",
                "white_mold": "moderately_resistant"
            },
            "stress_tolerances": ["drought"],
            "trait_stack": ["Roundup Ready 2"],
            "adapted_regions": ["Illinois", "Indiana", "Ohio"],
            "recommended_climate_zones": ["5a", "5b", "6a"],
            "optimal_ph_range": (6.0, 7.2),
            "minimum_ph": 5.8,
            "maximum_ph": 7.5,
            "seed_availability": "high",
            "release_year": 2021,
            "management_notes": [
                "Select fields with strong drainage to protect against white mold",
                "Consider SDS seed treatment if planting early in cool soils"
            ]
        }
        soybean_varieties.append(soybean_variety_one)

        soybean_variety_two = {
            "crop_name": "soybean",
            "name": "Pioneer P39T67R",
            "company": "Pioneer",
            "relative_maturity": 39,
            "yield_potential_percentile": 88,
            "yield_stability_rating": 7.8,
            "market_acceptance_score": 3.7,
            "standability_rating": 7.0,
            "expected_yield_bu_acre": 62,
            "yield_range_bu_acre": (56, 67),
            "seed_cost_per_unit": 61.0,
            "units_per_acre": 1.0,
            "additional_management_cost_per_acre": 15.0,
            "disease_resistances": {
                "sudden_death_syndrome": "moderately_resistant",
                "brown_stem_rot": "resistant",
                "phytophthora": "moderately_resistant"
            },
            "stress_tolerances": ["drought"],
            "trait_stack": ["Roundup Ready 2"],
            "adapted_regions": ["Iowa", "Illinois", "Indiana"],
            "recommended_climate_zones": ["4b", "5a", "5b"],
            "optimal_ph_range": (5.9, 7.0),
            "minimum_ph": 5.5,
            "maximum_ph": 7.4,
            "seed_availability": "high",
            "release_year": 2020,
            "management_notes": [
                "Use resistant seed treatment in phytophthora-prone fields",
                "Adapted to reduced tillage systems with residue cover"
            ]
        }
        soybean_varieties.append(soybean_variety_two)

        soybean_varieties_third = {
            "crop_name": "soybean",
            "name": "Syngenta Soybean 215",
            "company": "Syngenta",
            "relative_maturity": 32,
            "yield_potential_percentile": 85,
            "yield_stability_rating": 7.5,
            "market_acceptance_score": 3.5,
            "standability_rating": 7.0,
            "expected_yield_bu_acre": 58,
            "yield_range_bu_acre": (52, 63),
            "seed_cost_per_unit": 59.0,
            "units_per_acre": 1.0,
            "additional_management_cost_per_acre": 14.0,
            "disease_resistances": {
                "sudden_death_syndrome": "moderately_resistant",
                "brown_stem_rot": "moderately_resistant",
                "white_mold": "susceptible"
            },
            "stress_tolerances": ["drought", "heat"],
            "trait_stack": ["LibertyLink"],
            "adapted_regions": ["Kansas", "Missouri", "Nebraska"],
            "recommended_climate_zones": ["5b", "6a", "6b"],
            "optimal_ph_range": (5.8, 7.1),
            "minimum_ph": 5.4,
            "maximum_ph": 7.3,
            "seed_availability": "moderate",
            "release_year": 2019,
            "management_notes": [
                "Rotate fungicide modes of action for white mold management",
                "Maintain residue cover for heat stress mitigation"
            ]
        }
        soybean_varieties.append(soybean_varieties_third)

        variety_database["soybean"] = soybean_varieties

        wheat_varieties: List[Dict[str, Any]] = []

        wheat_variety_one = {
            "crop_name": "wheat",
            "name": "WestBred WB9653",
            "company": "WestBred",
            "relative_maturity": 95,
            "yield_potential_percentile": 90,
            "yield_stability_rating": 8.3,
            "market_acceptance_score": 4.0,
            "standability_rating": 8.0,
            "expected_yield_bu_acre": 82,
            "yield_range_bu_acre": (75, 90),
            "seed_cost_per_unit": 24.0,
            "units_per_acre": 1.5,
            "additional_management_cost_per_acre": 22.0,
            "disease_resistances": {
                "stripe_rust": "resistant",
                "leaf_rust": "moderately_resistant",
                "fusarium_head_blight": "moderately_resistant"
            },
            "stress_tolerances": ["cold", "heat"],
            "trait_stack": [],
            "adapted_regions": ["Kansas", "Oklahoma", "Colorado"],
            "recommended_climate_zones": ["5a", "5b", "6a"],
            "optimal_ph_range": (6.0, 7.3),
            "minimum_ph": 5.5,
            "maximum_ph": 7.8,
            "seed_availability": "high",
            "release_year": 2019,
            "management_notes": [
                "Achieves highest yields with split nitrogen applications",
                "Scout for fusarium during humid flowering conditions"
            ]
        }
        wheat_varieties.append(wheat_variety_one)

        wheat_variety_two = {
            "crop_name": "wheat",
            "name": "Syngenta SY Monument",
            "company": "Syngenta",
            "relative_maturity": 92,
            "yield_potential_percentile": 87,
            "yield_stability_rating": 7.9,
            "market_acceptance_score": 3.6,
            "standability_rating": 7.0,
            "expected_yield_bu_acre": 78,
            "yield_range_bu_acre": (70, 84),
            "seed_cost_per_unit": 23.0,
            "units_per_acre": 1.5,
            "additional_management_cost_per_acre": 20.0,
            "disease_resistances": {
                "stripe_rust": "moderately_resistant",
                "leaf_rust": "resistant",
                "powdery_mildew": "moderately_resistant"
            },
            "stress_tolerances": ["drought"],
            "trait_stack": [],
            "adapted_regions": ["Nebraska", "South Dakota", "Minnesota"],
            "recommended_climate_zones": ["3b", "4a", "4b", "5a"],
            "optimal_ph_range": (5.8, 7.2),
            "minimum_ph": 5.2,
            "maximum_ph": 7.6,
            "seed_availability": "moderate",
            "release_year": 2018,
            "management_notes": [
                "Responds to timely fungicide at flag leaf for rust suppression",
                "Maintain residue management for snow mold prone areas"
            ]
        }
        wheat_varieties.append(wheat_variety_two)

        wheat_variety_three = {
            "crop_name": "wheat",
            "name": "University Explorer",
            "company": "University Extension",
            "relative_maturity": 98,
            "yield_potential_percentile": 83,
            "yield_stability_rating": 7.4,
            "market_acceptance_score": 3.3,
            "standability_rating": 7.5,
            "expected_yield_bu_acre": 75,
            "yield_range_bu_acre": (68, 82),
            "seed_cost_per_unit": 21.0,
            "units_per_acre": 1.6,
            "additional_management_cost_per_acre": 18.0,
            "disease_resistances": {
                "stripe_rust": "moderately_resistant",
                "leaf_rust": "moderately_resistant",
                "fusarium_head_blight": "susceptible"
            },
            "stress_tolerances": ["cold"],
            "trait_stack": [],
            "adapted_regions": ["Montana", "North Dakota"],
            "recommended_climate_zones": ["3a", "3b", "4a"],
            "optimal_ph_range": (6.2, 7.4),
            "minimum_ph": 5.8,
            "maximum_ph": 7.8,
            "seed_availability": "limited",
            "release_year": 2020,
            "management_notes": [
                "Target well-drained soils to mitigate fusarium pressure",
                "Consider resistant companion crop for snow mold suppression"
            ]
        }
        wheat_varieties.append(wheat_variety_three)

        variety_database["wheat"] = wheat_varieties

        return variety_database

    def _get_variety_records_for_crop(self, crop_name: str) -> List[Dict[str, Any]]:
        """Retrieve stored variety profiles for a given crop."""
        if not crop_name:
            return []

        crop_key = crop_name.lower()
        if crop_key in self.variety_database:
            return self.variety_database[crop_key]

        return []

    def _match_variety_to_location(self, variety: Dict[str, Any], location_data) -> bool:
        """Determine if a variety aligns with the farm location."""
        if not variety:
            return False

        if not location_data:
            return True

        if 'adapted_regions' in variety:
            state = getattr(location_data, 'state', None)
            county = getattr(location_data, 'county', None)
            if state:
                for region in variety['adapted_regions']:
                    if isinstance(region, str) and region.lower() == state.lower():
                        return True
            if county:
                for region in variety['adapted_regions']:
                    if isinstance(region, str) and region.lower() == county.lower():
                        return True

        climate_zone = getattr(location_data, 'climate_zone', None)
        if climate_zone and variety.get('recommended_climate_zones'):
            for zone in variety['recommended_climate_zones']:
                if zone == climate_zone:
                    return True
                compatibility_score = self._calculate_adjacent_zone_compatibility(climate_zone, [zone])
                if compatibility_score >= 0.8:
                    return True
            return False

        return True

    def _calculate_variety_alignment_scores(
        self,
        variety: Dict[str, Any],
        request: RecommendationRequest
    ) -> Dict[str, float]:
        """Calculate climate and soil alignment scores for a variety."""
        results: Dict[str, float] = {}

        climate_alignment = 0.7
        if variety.get('recommended_climate_zones') and request and request.location:
            climate_crop_data = {"climate_zones": variety['recommended_climate_zones']}
            climate_alignment = self._calculate_climate_zone_suitability(
                request.location,
                climate_crop_data
            )
        results['climate_alignment'] = climate_alignment

        soil_alignment = 0.7
        if variety.get('optimal_ph_range') and request and request.soil_data and request.soil_data.ph:
            ph_crop_data = {
                "optimal_ph_range": variety['optimal_ph_range'],
                "minimum_ph": variety.get('minimum_ph', variety['optimal_ph_range'][0]),
                "maximum_ph": variety.get('maximum_ph', variety['optimal_ph_range'][1])
            }
            soil_alignment = self._calculate_ph_suitability(
                request.soil_data.ph,
                ph_crop_data
            )
        results['soil_alignment'] = soil_alignment

        return results

    def _calculate_variety_performance_score(
        self,
        variety: Dict[str, Any],
        request: RecommendationRequest
    ) -> float:
        """Calculate performance score for a variety based on multiple factors."""
        score_total = 0.0
        weight_total = 0.0

        percentile = variety.get('yield_potential_percentile')
        if percentile is not None:
            normalized = float(percentile) / 100.0
            score_total += normalized * 0.45
            weight_total += 0.45

        stability = variety.get('yield_stability_rating')
        if stability is not None:
            capped_stability = float(stability)
            if capped_stability > 10.0:
                capped_stability = 10.0
            normalized_stability = capped_stability / 10.0
            score_total += normalized_stability * 0.25
            weight_total += 0.25

        acceptance = variety.get('market_acceptance_score')
        if acceptance is not None:
            capped_acceptance = float(acceptance)
            if capped_acceptance > 5.0:
                capped_acceptance = 5.0
            normalized_acceptance = capped_acceptance / 5.0
            score_total += normalized_acceptance * 0.15
            weight_total += 0.15

        alignment_scores = self._calculate_variety_alignment_scores(variety, request)
        climate_alignment = alignment_scores.get('climate_alignment', 0.7)
        score_total += climate_alignment * 0.10
        weight_total += 0.10

        soil_alignment = alignment_scores.get('soil_alignment', 0.7)
        score_total += soil_alignment * 0.05
        weight_total += 0.05

        if weight_total == 0.0:
            return 0.6

        calculated_score = score_total / weight_total
        if calculated_score > 1.0:
            return 1.0
        if calculated_score < 0.0:
            return 0.0
        return calculated_score

    def _assess_variety_risk(self, variety: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk profile for a variety based on agronomic indicators."""
        risk_score = 0.0
        risk_factors: List[str] = []

        stability_rating = variety.get('yield_stability_rating')
        if stability_rating is not None and float(stability_rating) < 7.0:
            risk_score += 1.0
            risk_factors.append("Yield stability below 7.0 rating")

        standability_rating = variety.get('standability_rating')
        if standability_rating is not None and float(standability_rating) < 7.0:
            risk_score += 0.5
            risk_factors.append("Standability rating indicates lodging vigilance")

        disease_resistances = variety.get('disease_resistances')
        if isinstance(disease_resistances, dict):
            for disease_name, status in disease_resistances.items():
                if isinstance(status, str):
                    cleaned_status = status.lower()
                    if cleaned_status.startswith('susceptible'):
                        risk_score += 0.7
                        readable_name = disease_name.replace('_', ' ')
                        risk_factors.append(f"Susceptible to {readable_name}")
                    elif cleaned_status.startswith('moderately_susceptible'):
                        risk_score += 0.6
                        readable_name = disease_name.replace('_', ' ')
                        risk_factors.append(f"Moderate susceptibility to {readable_name}")

        stress_tolerances = variety.get('stress_tolerances')
        if isinstance(stress_tolerances, list):
            has_drought = False
            for tolerance in stress_tolerances:
                if isinstance(tolerance, str) and tolerance.lower() == 'drought':
                    has_drought = True
            if not has_drought:
                risk_score += 0.4
                risk_factors.append("Limited drought tolerance")

        if risk_score <= 1.0:
            level = "low"
        elif risk_score <= 2.0:
            level = "moderate"
        else:
            level = "elevated"

        return {
            "risk_level": level,
            "risk_score": risk_score,
            "risk_factors": risk_factors
        }

    def _determine_alignment_label(self, score: float) -> str:
        """Convert numeric alignment score to descriptive label."""
        if score >= 0.9:
            return "optimal"
        if score >= 0.75:
            return "strong"
        if score >= 0.6:
            return "adequate"
        return "limited"

    def _format_variety_summary_step(self, variety_entry: Dict[str, Any]) -> str:
        """Create concise summary string for implementation steps."""
        if not variety_entry:
            return ""

        summary_parts: List[str] = []

        name = variety_entry.get('variety_name')
        company = variety_entry.get('company')
        if name:
            if company:
                summary_parts.append(f"{name} ({company})")
            else:
                summary_parts.append(str(name))

        roi_info = variety_entry.get('roi', {})
        roi_percent = roi_info.get('roi_percent')
        if roi_percent is not None:
            rounded_roi = round(roi_percent)
            summary_parts.append(f"ROI {rounded_roi}%")

        performance_score = variety_entry.get('performance_score')
        if performance_score is not None:
            summary_parts.append(f"performance {round(performance_score * 100)}%")

        risk_info = variety_entry.get('risk', {})
        risk_level = risk_info.get('risk_level')
        if risk_level:
            summary_parts.append(f"risk {risk_level}")

        if not summary_parts:
            return ""

        combined_summary = ", ".join(summary_parts)
        return f"Variety focus: {combined_summary}"

    def _extract_crop_name_from_title(self, title: str) -> str:
        """Extract crop name from recommendation title text."""
        if not title:
            return ""

        lower_title = title.lower()

        for crop_name in self.crop_database.keys():
            if crop_name in lower_title:
                return crop_name

        tokens = lower_title.replace(',', ' ').split()
        for token in tokens:
            if token in self.crop_database:
                return token

        if tokens:
            last_token = tokens[-1]
            if last_token in self.crop_database:
                return last_token
        return ""

    def _get_fallback_crop_price(self, crop_name: str) -> Dict[str, Any]:
        """Provide fallback price data when market service is unavailable."""
        fallback_prices: Dict[str, Dict[str, Any]] = {
            "corn": {
                "price_per_unit": 4.30,
                "unit": "bushel",
                "confidence": 0.45,
                "source": "internal_fallback"
            },
            "soybean": {
                "price_per_unit": 12.60,
                "unit": "bushel",
                "confidence": 0.45,
                "source": "internal_fallback"
            },
            "wheat": {
                "price_per_unit": 6.90,
                "unit": "bushel",
                "confidence": 0.42,
                "source": "internal_fallback"
            }
        }

        crop_key = crop_name.lower() if crop_name else ""
        if crop_key in fallback_prices:
            return fallback_prices[crop_key]

        return {
            "price_per_unit": 8.0,
            "unit": "bushel",
            "confidence": 0.35,
            "source": "internal_fallback"
        }

    async def calculate_variety_roi(
        self,
        variety: Dict[str, Any],
        farm_context: RecommendationRequest
    ) -> Dict[str, Any]:
        """Calculate ROI metrics for a variety using market and cost data."""
        crop_name = variety.get('crop_name', '')
        region = 'US'

        if farm_context and farm_context.location:
            if farm_context.location.state:
                region = farm_context.location.state
            elif farm_context.location.county:
                region = farm_context.location.county

        price_per_unit = None
        price_unit = 'bushel'
        price_source = 'unknown'
        price_confidence = 0.0

        if self.market_price_service and crop_name:
            try:
                market_price = await self.market_price_service.get_current_price(crop_name, region)
            except Exception:
                market_price = None
            if market_price:
                price_per_unit = float(market_price.price_per_unit)
                price_unit = market_price.unit
                price_source = market_price.source
                price_confidence = market_price.confidence

        if price_per_unit is None:
            fallback_price = self._get_fallback_crop_price(crop_name)
            price_per_unit = float(fallback_price['price_per_unit'])
            price_unit = fallback_price['unit']
            price_source = fallback_price['source']
            price_confidence = fallback_price['confidence']

        units_per_acre = variety.get('units_per_acre', 1.0)
        if units_per_acre is None:
            units_per_acre = 1.0

        seed_cost_per_unit = variety.get('seed_cost_per_unit', 0.0)
        seed_cost_per_acre = float(seed_cost_per_unit) * float(units_per_acre)

        management_cost = float(variety.get('additional_management_cost_per_acre', 0.0))

        total_cost = seed_cost_per_acre + management_cost

        expected_yield = variety.get('expected_yield_bu_acre')
        if expected_yield is None:
            yield_range = variety.get('yield_range_bu_acre')
            if isinstance(yield_range, tuple) or isinstance(yield_range, list):
                values: List[float] = []
                for entry in yield_range:
                    try:
                        values.append(float(entry))
                    except (TypeError, ValueError):
                        continue
                total_values = 0.0
                count_values = 0
                for value in values:
                    total_values += value
                    count_values += 1
                if count_values > 0:
                    expected_yield = total_values / count_values
        if expected_yield is None:
            expected_yield = 0.0

        expected_revenue = float(expected_yield) * float(price_per_unit)
        net_return = expected_revenue - total_cost

        if total_cost > 0:
            roi_percent = (net_return / total_cost) * 100.0
        else:
            roi_percent = 0.0

        if price_per_unit > 0:
            break_even_yield = total_cost / price_per_unit
        else:
            break_even_yield = 0.0

        result = {
            "seed_cost_per_acre": seed_cost_per_acre,
            "management_cost_per_acre": management_cost,
            "total_cost_per_acre": total_cost,
            "price_per_unit": price_per_unit,
            "price_unit": price_unit,
            "price_source": price_source,
            "price_confidence": price_confidence,
            "expected_revenue_per_acre": expected_revenue,
            "net_return_per_acre": net_return,
            "roi_percent": roi_percent,
            "break_even_yield_bu_acre": break_even_yield,
            "calculation_timestamp": datetime.utcnow().isoformat()
        }

        return result

    async def get_variety_aware_recommendations(
        self,
        request: RecommendationRequest
    ) -> Dict[str, Any]:
        """Generate crop recommendations enriched with variety intelligence."""
        base_recommendations = await self.get_crop_recommendations(request)

        variety_recommendations: List[Dict[str, Any]] = []
        risk_distribution: Dict[str, int] = {
            "low": 0,
            "moderate": 0,
            "elevated": 0
        }

        for recommendation in base_recommendations:
            crop_name = self._extract_crop_name_from_title(recommendation.title)
            if not crop_name:
                continue

            variety_records = self._get_variety_records_for_crop(crop_name)
            if not variety_records:
                continue

            candidate_varieties: List[Dict[str, Any]] = []

            for variety in variety_records:
                if not self._match_variety_to_location(variety, request.location):
                    continue

                alignment_scores = self._calculate_variety_alignment_scores(variety, request)
                performance_score = self._calculate_variety_performance_score(variety, request)
                risk_info = self._assess_variety_risk(variety)
                roi_info = await self.calculate_variety_roi(variety, request)

                entry: Dict[str, Any] = {}
                entry['crop_name'] = crop_name
                entry['variety_name'] = variety.get('name')
                entry['company'] = variety.get('company')
                entry['performance_score'] = performance_score
                entry['yield_potential_percentile'] = variety.get('yield_potential_percentile')
                entry['expected_yield_bu_acre'] = variety.get('expected_yield_bu_acre')
                entry['risk'] = risk_info
                entry['roi'] = roi_info
                entry['alignment'] = alignment_scores
                entry['management_notes'] = variety.get('management_notes')
                entry['trait_stack'] = variety.get('trait_stack')
                entry['stress_tolerances'] = variety.get('stress_tolerances')
                entry['disease_resistances'] = variety.get('disease_resistances')
                entry['seed_availability'] = variety.get('seed_availability')
                candidate_varieties.append(entry)

            if not candidate_varieties:
                continue

            candidate_varieties.sort(key=lambda item: item['performance_score'], reverse=True)

            top_varieties: List[Dict[str, Any]] = []
            index = 0
            while index < len(candidate_varieties) and index < 3:
                top_varieties.append(candidate_varieties[index])
                risk_level = candidate_varieties[index]['risk'].get('risk_level', 'moderate')
                if risk_level not in risk_distribution:
                    risk_distribution[risk_level] = 0
                risk_distribution[risk_level] += 1
                index += 1

            primary_variety = top_varieties[0]
            summary_step = self._format_variety_summary_step(primary_variety)
            if summary_step:
                recommendation.implementation_steps.insert(0, summary_step)

            risk_label = primary_variety['risk'].get('risk_level', 'moderate')
            risk_note = f"Primary variety risk profile: {risk_label}"
            recommendation.expected_outcomes.append(risk_note)

            alignment_scores = primary_variety['alignment']
            climate_alignment_label = self._determine_alignment_label(
                alignment_scores.get('climate_alignment', 0.7)
            )
            soil_alignment_label = self._determine_alignment_label(
                alignment_scores.get('soil_alignment', 0.7)
            )

            crop_entry = {
                "crop_name": crop_name,
                "variety_candidates": top_varieties,
                "climate_alignment": climate_alignment_label,
                "soil_alignment": soil_alignment_label,
                "recommendation_title": recommendation.title
            }

            variety_recommendations.append(crop_entry)

        analysis_notes: List[str] = []
        for level, count in risk_distribution.items():
            if count > 0:
                analysis_notes.append(f"{level.title()} risk varieties: {count}")

        variety_summary = {
            "request_id": request.request_id,
            "generated_at": datetime.utcnow().isoformat(),
            "crop_recommendations": base_recommendations,
            "variety_recommendations": variety_recommendations,
            "analysis_summary": {
                "risk_distribution": risk_distribution,
                "notes": analysis_notes
            }
        }

        return variety_summary
    
    async def get_crop_recommendations(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """
        Generate crop recommendations based on farm conditions.
        
        Args:
            request: Recommendation request with farm data
            
        Returns:
            List of crop recommendations sorted by suitability
        """
        # Enhance location data with climate zone if missing
        await self._ensure_climate_zone_data(request)
        
        recommendations = []
        
        # Pre-filter crops based on climate zone compatibility
        filtered_crops = self._filter_crops_by_climate_zone(request.location)
        
        for crop_name, crop_data in filtered_crops.items():
            suitability_score = self._calculate_crop_suitability(
                crop_name, crop_data, request
            )
            
            if suitability_score > 0.5:  # Only recommend suitable crops
                recommendation = self._create_crop_recommendation(
                    crop_name, crop_data, suitability_score, request
                )
                recommendations.append(recommendation)
        
        # Add climate zone mismatch warnings for excluded crops
        excluded_crops = self._get_excluded_crops_by_climate(request.location)
        if excluded_crops:
            # Log excluded crops for potential warning generation
            pass  # Warnings will be handled by the main recommendation engine
        
        # Sort by suitability score (descending)
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return recommendations
    
    def _calculate_crop_suitability(
        self, 
        crop_name: str, 
        crop_data: Dict[str, Any], 
        request: RecommendationRequest
    ) -> float:
        """Calculate overall suitability score for a crop."""
        
        scores = []
        
        # pH suitability
        if request.soil_data and request.soil_data.ph:
            ph_score = self._calculate_ph_suitability(
                request.soil_data.ph, crop_data
            )
            scores.append(ph_score)
        
        # Nutrient suitability
        if request.soil_data:
            nutrient_score = self._calculate_nutrient_suitability(
                request.soil_data, crop_data
            )
            scores.append(nutrient_score)
        
        # Farm size suitability
        if request.farm_profile:
            size_score = self._calculate_size_suitability(
                request.farm_profile.farm_size_acres, crop_data
            )
            scores.append(size_score)
        
        # Climate suitability (integrated with climate zone detection)
        climate_score = self._calculate_climate_zone_suitability(
            request.location, crop_data
        )
        scores.append(climate_score)
        
        # Return weighted average
        if scores:
            return sum(scores) / len(scores)
        else:
            return 0.5  # Default moderate suitability
    
    def _calculate_ph_suitability(self, soil_ph: float, crop_data: Dict[str, Any]) -> float:
        """Calculate pH suitability score."""
        optimal_min, optimal_max = crop_data["optimal_ph_range"]
        
        if optimal_min <= soil_ph <= optimal_max:
            return 1.0  # Optimal
        elif crop_data["minimum_ph"] <= soil_ph <= crop_data["maximum_ph"]:
            # Calculate distance from optimal range
            if soil_ph < optimal_min:
                distance = optimal_min - soil_ph
            else:
                distance = soil_ph - optimal_max
            
            # Linear decrease from optimal
            max_distance = max(
                optimal_min - crop_data["minimum_ph"],
                crop_data["maximum_ph"] - optimal_max
            )
            return max(0.6, 1.0 - (distance / max_distance) * 0.4)
        else:
            return 0.3  # Poor suitability
    
    def _calculate_nutrient_suitability(
        self, 
        soil_data, 
        crop_data: Dict[str, Any]
    ) -> float:
        """Calculate nutrient suitability score."""
        scores = []
        
        # Phosphorus suitability
        if soil_data.phosphorus_ppm:
            p_score = self._get_nutrient_score(
                soil_data.phosphorus_ppm, 
                crop_data["phosphorus_requirement"],
                nutrient_type="phosphorus"
            )
            scores.append(p_score)
        
        # Potassium suitability
        if soil_data.potassium_ppm:
            k_score = self._get_nutrient_score(
                soil_data.potassium_ppm,
                crop_data["potassium_requirement"],
                nutrient_type="potassium"
            )
            scores.append(k_score)
        
        return sum(scores) / len(scores) if scores else 0.7
    
    def _get_nutrient_score(
        self, 
        nutrient_level: float, 
        requirement: str, 
        nutrient_type: str
    ) -> float:
        """Get nutrient adequacy score."""
        
        # Define nutrient level thresholds (ppm)
        thresholds = {
            "phosphorus": {"low": 15, "medium": 30, "high": 50},
            "potassium": {"low": 120, "medium": 200, "high": 300}
        }
        
        if nutrient_type not in thresholds:
            return 0.7  # Default score
        
        thresh = thresholds[nutrient_type]
        
        # Determine nutrient level category
        if nutrient_level >= thresh["high"]:
            level_category = "high"
        elif nutrient_level >= thresh["medium"]:
            level_category = "medium"
        else:
            level_category = "low"
        
        # Score based on requirement vs availability
        requirement_scores = {
            ("high", "high"): 1.0,
            ("high", "medium"): 0.7,
            ("high", "low"): 0.4,
            ("medium_high", "high"): 1.0,
            ("medium_high", "medium"): 0.8,
            ("medium_high", "low"): 0.5,
            ("medium", "high"): 1.0,
            ("medium", "medium"): 0.9,
            ("medium", "low"): 0.6,
            ("low", "high"): 1.0,
            ("low", "medium"): 1.0,
            ("low", "low"): 0.8
        }
        
        return requirement_scores.get((requirement, level_category), 0.7)
    
    def _calculate_size_suitability(self, farm_size: float, crop_data: Dict[str, Any]) -> float:
        """Calculate farm size suitability."""
        min_viable_size = crop_data.get("economic_viability_min_acres", 20)
        
        if farm_size >= min_viable_size * 2:
            return 1.0  # Excellent size
        elif farm_size >= min_viable_size:
            return 0.8  # Good size
        elif farm_size >= min_viable_size * 0.5:
            return 0.6  # Marginal size
        else:
            return 0.4  # Small but possible
    
    def _create_crop_recommendation(
        self,
        crop_name: str,
        crop_data: Dict[str, Any],
        suitability_score: float,
        request: RecommendationRequest
    ) -> RecommendationItem:
        """Create a crop recommendation item."""
        
        # Generate description based on suitability factors
        description_parts = [
            f"{crop_name.title()} is {'highly' if suitability_score > 0.8 else 'moderately' if suitability_score > 0.6 else 'marginally'} suitable for your farm conditions."
        ]
        
        # Add climate zone compatibility information
        if request.location:
            climate_compatibility = self._get_climate_compatibility_description(
                request.location, crop_data, crop_name
            )
            if climate_compatibility:
                description_parts.append(climate_compatibility)
        
        if request.soil_data:
            if request.soil_data.ph:
                ph_status = self._get_ph_status(request.soil_data.ph, crop_data)
                description_parts.append(f"Soil pH of {request.soil_data.ph} is {ph_status} for {crop_name}.")
        
        # Implementation steps with planting timing
        implementation_steps = [
            f"Verify soil conditions meet {crop_name} requirements",
            f"Select appropriate {crop_name} variety for your region",
            "Plan planting schedule based on local frost dates",
            "Prepare seedbed and planting equipment",
            "Consider crop insurance options"
        ]
        
        # Add planting timing information if available
        planting_timing = self._get_planting_timing_info(crop_name, request.location)
        if planting_timing:
            implementation_steps.insert(2, planting_timing)
        
        # Expected outcomes
        yield_min, yield_max = crop_data["typical_yield_range"]
        expected_outcomes = [
            f"Expected yield range: {yield_min}-{yield_max} bu/acre",
            "Improved soil health through crop rotation",
            "Diversified income stream",
            "Enhanced farm sustainability"
        ]
        
        return RecommendationItem(
            recommendation_type="crop_selection",
            title=f"Grow {crop_name.title()}",
            description=" ".join(description_parts),
            priority=1 if suitability_score > 0.8 else 2 if suitability_score > 0.6 else 3,
            confidence_score=suitability_score,
            implementation_steps=implementation_steps,
            expected_outcomes=expected_outcomes,
            timing="Plan for next growing season",
            agricultural_sources=[
                "USDA Crop Production Guidelines",
                "State University Extension Services",
                "Regional Crop Variety Trials"
            ]
        )
    
    def _calculate_climate_zone_suitability(self, location_data, crop_data: Dict[str, Any]) -> float:
        """
        Calculate climate zone suitability score for a crop.
        
        Args:
            location_data: Location data with climate zone information
            crop_data: Crop characteristics including compatible climate zones
            
        Returns:
            Suitability score between 0.0 and 1.0
        """
        if not location_data or not crop_data.get("climate_zones"):
            return 0.7  # Default moderate score when no climate data available
        
        # Get the farm's climate zone
        farm_climate_zone = getattr(location_data, 'climate_zone', None)
        
        if not farm_climate_zone:
            return 0.7  # Default moderate score without climate zone
        
        compatible_zones = crop_data["climate_zones"]
        
        # Perfect match - crop is explicitly compatible with this zone
        if farm_climate_zone in compatible_zones:
            return 1.0
        
        # Check for adjacent/similar zones
        adjacent_score = self._calculate_adjacent_zone_compatibility(farm_climate_zone, compatible_zones)
        if adjacent_score > 0:
            return adjacent_score
        
        # No compatibility found
        return 0.3
    
    def _calculate_adjacent_zone_compatibility(self, farm_zone: str, compatible_zones: List[str]) -> float:
        """
        Calculate compatibility score for adjacent climate zones.
        
        Args:
            farm_zone: Farm's USDA climate zone (e.g., "6a")
            compatible_zones: List of crop-compatible zones
            
        Returns:
            Compatibility score (0.0 for incompatible, 0.8 for adjacent)
        """
        if not farm_zone or not compatible_zones:
            return 0.0
        
        try:
            # Extract zone number and subzone from farm zone (e.g., "6a" -> 6, "a")
            farm_num = int(farm_zone[0]) if farm_zone[0].isdigit() else 0
            farm_sub = farm_zone[1:].lower() if len(farm_zone) > 1 else ""
            
            for compatible_zone in compatible_zones:
                if not compatible_zone:
                    continue
                    
                comp_num = int(compatible_zone[0]) if compatible_zone[0].isdigit() else 0
                comp_sub = compatible_zone[1:].lower() if len(compatible_zone) > 1 else ""
                
                # Adjacent zone numbers (within 1 zone)
                if abs(farm_num - comp_num) == 1:
                    return 0.8  # Good compatibility for adjacent zones
                
                # Same zone number but different subzone (e.g., 6a vs 6b)
                if farm_num == comp_num and farm_sub != comp_sub:
                    return 0.9  # Very good compatibility for same zone different subzone
            
            return 0.0  # No adjacent compatibility found
            
        except (ValueError, IndexError):
            return 0.0  # Error parsing zone data
    
    def _filter_crops_by_climate_zone(self, location_data) -> Dict[str, Dict[str, Any]]:
        """
        Filter crop database to include only climate-compatible crops.
        
        Args:
            location_data: Location data with climate zone information
            
        Returns:
            Filtered crop database containing compatible and borderline compatible crops
        """
        if not location_data:
            return self.crop_database  # Return all crops if no location data
        
        farm_climate_zone = getattr(location_data, 'climate_zone', None)
        
        if not farm_climate_zone:
            return self.crop_database  # Return all crops if no climate zone
        
        filtered_crops = {}
        
        for crop_name, crop_data in self.crop_database.items():
            compatibility_score = self._calculate_climate_zone_suitability(location_data, crop_data)
            
            # Include crops with reasonable compatibility (>= 0.5)
            # This includes perfect matches (1.0), adjacent zones (0.8-0.9), and marginal but possible (0.7)
            if compatibility_score >= 0.5:
                filtered_crops[crop_name] = crop_data
        
        return filtered_crops
    
    def _get_excluded_crops_by_climate(self, location_data) -> List[str]:
        """
        Get list of crops excluded due to climate zone incompatibility.
        
        Args:
            location_data: Location data with climate zone information
            
        Returns:
            List of crop names that were excluded
        """
        if not location_data:
            return []
        
        farm_climate_zone = getattr(location_data, 'climate_zone', None)
        
        if not farm_climate_zone:
            return []
        
        excluded_crops = []
        
        for crop_name, crop_data in self.crop_database.items():
            compatibility_score = self._calculate_climate_zone_suitability(location_data, crop_data)
            
            # Crops with very low compatibility are excluded
            if compatibility_score < 0.5:
                excluded_crops.append(crop_name)
        
        return excluded_crops
    
    async def _ensure_climate_zone_data(self, request: RecommendationRequest) -> None:
        """
        Ensure location data includes climate zone information, fetch if missing.
        
        Args:
            request: Recommendation request to enhance with climate data
        """
        if not request.location or not self.climate_service:
            return
        
        # Check if climate zone data is already available
        if hasattr(request.location, 'climate_zone') and request.location.climate_zone:
            return
        
        try:
            # Detect climate zone using coordinates
            climate_data = await self.climate_service.detect_climate_zone(
                latitude=request.location.latitude,
                longitude=request.location.longitude,
                elevation_ft=getattr(request.location, 'elevation_ft', None)
            )
            
            if climate_data:
                # Enhance location data with climate zone information
                enhanced_location_dict = self.climate_service.enhance_location_with_climate(
                    request.location.dict(), climate_data
                )
                
                # Update request location with enhanced data
                for key, value in enhanced_location_dict.items():
                    if hasattr(request.location, key):
                        setattr(request.location, key, value)
                        
        except Exception as e:
            # Log error but continue without climate zone data
            pass  # Fail gracefully, recommendations will use default climate scoring
    
    def _get_climate_compatibility_description(self, location_data, crop_data: Dict[str, Any], crop_name: str) -> str:
        """
        Generate climate compatibility description for recommendation.
        
        Args:
            location_data: Location data with climate zone information
            crop_data: Crop characteristics
            crop_name: Name of the crop
            
        Returns:
            Climate compatibility description string
        """
        farm_climate_zone = getattr(location_data, 'climate_zone', None)
        
        if not farm_climate_zone or not crop_data.get("climate_zones"):
            return ""
        
        compatible_zones = crop_data["climate_zones"]
        compatibility_score = self._calculate_climate_zone_suitability(location_data, crop_data)
        
        if farm_climate_zone in compatible_zones:
            return f"Climate Zone {farm_climate_zone} is optimal for {crop_name} production."
        elif compatibility_score >= 0.8:
            return f"Climate Zone {farm_climate_zone} is well-suited for {crop_name}, being adjacent to optimal zones {', '.join(compatible_zones[:3])}."
        elif compatibility_score >= 0.5:
            return f"Climate Zone {farm_climate_zone} is marginal for {crop_name}. Consider heat/cold tolerant varieties and monitor seasonal conditions."
        else:
            return f"Climate Zone {farm_climate_zone} may present challenges for {crop_name}. Optimal zones are {', '.join(compatible_zones[:3])}."
    
    def _get_ph_status(self, soil_ph: float, crop_data: Dict[str, Any]) -> str:
        """Get pH status description."""
        optimal_min, optimal_max = crop_data["optimal_ph_range"]
        
        if optimal_min <= soil_ph <= optimal_max:
            return "optimal"
        elif crop_data["minimum_ph"] <= soil_ph <= crop_data["maximum_ph"]:
            return "acceptable"
        else:
            return "suboptimal"
    
    def _get_planting_timing_info(self, crop_name: str, location_data) -> Optional[str]:
        """Get planting timing information for a crop."""
        if not self.planting_date_service or not location_data:
            return None
        
        try:
            # Get spring planting window as primary timing recommendation
            from datetime import datetime
            import asyncio
            
            # Use asyncio to run async method
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, schedule the coroutine
                task = asyncio.create_task(
                    self.planting_date_service.calculate_planting_dates(
                        crop_name, location_data, "spring"
                    )
                )
                # This is not ideal but necessary for synchronous context
                return f"Optimal spring planting: mid-April to early May (verify local frost dates)"
            else:
                planting_window = loop.run_until_complete(
                    self.planting_date_service.calculate_planting_dates(
                        crop_name, location_data, "spring"
                    )
                )
                
                optimal_date_str = planting_window.optimal_date.strftime('%B %d')
                return f"Optimal spring planting: {optimal_date_str} (±1-2 weeks based on conditions)"
                
        except Exception as e:
            # Fallback to generic timing advice
            return f"Plan spring planting after last frost date for your area"
