import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

from ..services.variety_recommendation_service import VarietyRecommendationService
from ..services.crop_search_service import CropSearchService
from ..models.crop_taxonomy_models import ComprehensiveCropData, CropCategory, LifeCycle
from ..models.crop_variety_models import (
    EnhancedCropVariety, YieldPotential, DiseaseResistanceProfile, AbioticStressTolerances,
    MarketAttributes, QualityAttributes, PestResistanceProfile, VarietyCharacteristics
)
from ..models.crop_filtering_models import CropFilteringAttributes

logger = logging.getLogger(__name__)

class FilterResultProcessor:
    """
    Processes filtered crop results for ranking, clustering, and visualization.
    """

    def __init__(self):
        logger.info("FilterResultProcessor initialized.")
        self.variety_recommendation_service = VarietyRecommendationService()
        self.crop_search_service = CropSearchService()

    async def process_results(
        self,
        filtered_crops: List[Dict[str, Any]],
        filtering_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main method to process filtered crop results.

        Args:
            filtered_crops: A list of crop dictionaries that passed the initial filtering.
            filtering_criteria: The criteria used for filtering.

        Returns:
            A dictionary containing ranked results, clustered results, and visualization data.
        """
        if not filtered_crops:
            logger.info("No crops found after filtering. Suggesting alternatives.")
            alternatives = await self._suggest_alternatives(filtering_criteria)
            return {
                "ranked_results": [],
                "clustered_results": {},
                "visualization_data": {},
                "alternatives": alternatives,
                "message": "No crops matched the criteria. Here are some alternatives."
            }

        # 1. Relevance Scoring
        ranked_crops = await self._apply_relevance_scoring(filtered_crops, filtering_criteria)

        # 2. Result Clustering
        clustered_results = await self._cluster_results(ranked_crops)

        # 3. Prepare Visualization Data
        visualization_data = await self._prepare_visualization_data(ranked_crops)

        return {
            "ranked_results": ranked_crops,
            "clustered_results": clustered_results,
            "visualization_data": visualization_data,
            "alternatives": [],
            "message": f"{len(ranked_crops)} crops found matching criteria."
        }

    async def _apply_relevance_scoring(
        self,
        crops: List[Dict[str, Any]],
        filtering_criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Applies a relevance score to each crop based on filtering criteria and agricultural context.
        """
        scored_crops = []
        for crop in crops:
            score = await self._calculate_relevance_score(crop, filtering_criteria)
            scored_crops.append({**crop, "relevance_score": score})

        # Sort by relevance score in descending order
        scored_crops.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return scored_crops

    async def _calculate_relevance_score(
        self,
        crop: Dict[str, Any],
        filtering_criteria: Dict[str, Any]
    ) -> float:
        """
        Calculates a relevance score for a single crop using VarietyRecommendationService.
        """
        try:
            # Convert crop dictionary to EnhancedCropVariety object
            # This assumes the crop dictionary has the necessary fields to construct EnhancedCropVariety
            # If not, a more robust mapping or fetching from DB would be needed.
            # For now, we'll try to construct it directly.
            # Need to handle UUID conversion if 'id' is a string
            crop_id = crop.get("id")
            if isinstance(crop_id, str):
                from uuid import UUID
                try:
                    crop["id"] = UUID(crop_id)
                except ValueError:
                    logger.warning(f"Invalid UUID format for crop ID: {crop_id}. Skipping scoring.")
                    return 0.0

            # Create a dummy ComprehensiveCropData for the parent_crop_id if needed by EnhancedCropVariety
            # This is a simplification; in a real scenario, you'd fetch the actual parent crop.
            parent_crop_id = crop.get("parent_crop_id")
            if isinstance(parent_crop_id, str):
                from uuid import UUID
                try:
                    crop["parent_crop_id"] = UUID(parent_crop_id)
                except ValueError:
                    logger.warning(f"Invalid UUID format for parent_crop_id: {parent_crop_id}. Skipping scoring.")
                    return 0.0

            # Ensure nested Pydantic models are correctly instantiated if they are dicts
            if isinstance(crop.get("yield_potential"), dict):
                from ..models.crop_variety_models import YieldPotential
                crop["yield_potential"] = YieldPotential(**crop["yield_potential"])
            if isinstance(crop.get("disease_resistance"), dict):
                from ..models.crop_variety_models import DiseaseResistanceProfile
                crop["disease_resistance"] = DiseaseResistanceProfile(**crop["disease_resistance"])
            if isinstance(crop.get("abiotic_stress_tolerances"), dict):
                from ..models.crop_variety_models import AbioticStressTolerances
                crop["abiotic_stress_tolerances"] = AbioticStressTolerances(**crop["abiotic_stress_tolerances"])
            if isinstance(crop.get("market_attributes"), dict):
                from ..models.crop_variety_models import MarketAttributes
                crop["market_attributes"] = MarketAttributes(**crop["market_attributes"])
            if isinstance(crop.get("quality_attributes"), dict):
                from ..models.crop_variety_models import QualityAttributes
                crop["quality_attributes"] = QualityAttributes(**crop["quality_attributes"])
            if isinstance(crop.get("pest_resistance"), dict):
                from ..models.crop_variety_models import PestResistanceProfile
                crop["pest_resistance"] = PestResistanceProfile(**crop["pest_resistance"])
            if isinstance(crop.get("characteristics"), dict):
                from ..models.crop_variety_models import VarietyCharacteristics
                crop["characteristics"] = VarietyCharacteristics(**crop["characteristics"])

            enhanced_crop_variety = EnhancedCropVariety(**crop)

            # Extract regional_context and farmer_preferences from filtering_criteria
            regional_context = filtering_criteria.get("location", {})
            regional_context["climate_risks"] = filtering_criteria.get("climate_risks", {})
            regional_context["market_preferences"] = filtering_criteria.get("market_class", [])

            farmer_preferences = filtering_criteria.get("user_preferences", {})
            farmer_preferences["quality_priorities"] = filtering_criteria.get("quality_priorities", {})

            score_data = await self.variety_recommendation_service._score_variety_for_context(
                enhanced_crop_variety, regional_context, farmer_preferences
            )

            if score_data and "overall_score" in score_data:
                return score_data["overall_score"]
            else:
                logger.warning(f"VarietyRecommendationService returned no overall_score for crop {crop.get('name')}")
                return 0.0
        except Exception as e:
            logger.error(f"Error calculating relevance score for crop {crop.get('name')}: {e}")
            return 0.0
    async def _cluster_results(
        self,
        crops: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Clusters crops based on similarity (e.g., crop type, family, primary use).
        """
        clustered_data = {}
        for crop in crops:
            # Prioritize clustering by primary category, then life cycle, then primary use
            cluster_key_parts = []
            if crop.get("agricultural_classification") and crop["agricultural_classification"].get("primary_category"):
                cluster_key_parts.append(crop["agricultural_classification"]["primary_category"].value)
            if crop.get("life_cycle"):
                cluster_key_parts.append(crop["life_cycle"].value)
            if crop.get("primary_use"):
                cluster_key_parts.append(crop["primary_use"])

            cluster_key = " - ".join(cluster_key_parts) if cluster_key_parts else "Miscellaneous"

            if cluster_key not in clustered_data:
                clustered_data[cluster_key] = []
            clustered_data[cluster_key].append(crop)
        return clustered_data

    async def _suggest_alternatives(
        self,
        filtering_criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Suggests alternative crops by relaxing some filtering criteria.
        """
        alternatives = []
        original_filters = CropFilteringAttributes(**filtering_criteria.get("filters", {}))

        # Strategy 1: Relax climate zones
        if original_filters.climate_zones:
            relaxed_filters = original_filters.copy(update={
                "climate_zones": [] # Remove climate zone filter
            })
            relaxed_search_results = await self.crop_search_service.search_crops(
                filters=relaxed_filters,
                location=filtering_criteria.get("location"),
                user_preferences=filtering_criteria.get("user_preferences"),
                limit=3
            )
            for crop in relaxed_search_results:
                alternatives.append({
                    "name": crop.get("name"),
                    "category": crop.get("agricultural_classification", {}).get("primary_category"),
                    "reason": "Relaxed climate zone filter"
                })
            if alternatives: return alternatives # Return first set of alternatives

        # Strategy 2: Relax soil pH range
        if original_filters.soil_ph_range:
            relaxed_filters = original_filters.copy(update={
                "soil_ph_range": None # Remove soil pH filter
            })
            relaxed_search_results = await self.crop_search_service.search_crops(
                filters=relaxed_filters,
                location=filtering_criteria.get("location"),
                user_preferences=filtering_criteria.get("user_preferences"),
                limit=3
            )
            for crop in relaxed_search_results:
                alternatives.append({
                    "name": crop.get("name"),
                    "category": crop.get("agricultural_classification", {}).get("primary_category"),
                    "reason": "Relaxed soil pH range filter"
                })
            if alternatives: return alternatives

        # Strategy 3: Relax maturity days range
        if original_filters.maturity_days_range:
            relaxed_filters = original_filters.copy(update={
                "maturity_days_range": None # Remove maturity days filter
            })
            relaxed_search_results = await self.crop_search_service.search_crops(
                filters=relaxed_filters,
                location=filtering_criteria.get("location"),
                user_preferences=filtering_criteria.get("user_preferences"),
                limit=3
            )
            for crop in relaxed_search_results:
                alternatives.append({
                    "name": crop.get("name"),
                    "category": crop.get("agricultural_classification", {}).get("primary_category"),
                    "reason": "Relaxed maturity days range filter"
                })
            if alternatives: return alternatives

        logger.info("No meaningful alternatives found after relaxing filters.")
        return [
            {"name": "General Purpose Crop A", "category": "Grain", "reason": "No specific alternatives found"},
            {"name": "General Purpose Crop B", "category": "Legume", "reason": "No specific alternatives found"}
        ]
    async def _prepare_visualization_data(
        self,
        crops: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Prepares data structures suitable for frontend charts and comparison tables.
        """
        visualization_data = {
            "chart_data": {
                "category_distribution": {},
                "relevance_score_distribution": {},
                "yield_potential_distribution": {},
                "climate_adaptation_distribution": {},
                "disease_resistance_distribution": {},
                "market_desirability_distribution": {}
            },
            "comparison_table_data": []
        }

        relevance_scores = []
        yield_potentials = []
        climate_adaptations = []
        disease_resistances = []
        market_desirabilities = []

        for crop in crops:
            # Category Distribution
            category = crop.get("agricultural_classification", {}).get("primary_category", "Other")
            if isinstance(category, CropCategory):
                category = category.value
            visualization_data["chart_data"]["category_distribution"][category] = \
                visualization_data["chart_data"]["category_distribution"].get(category, 0) + 1

            # Relevance Score Distribution
            if "relevance_score" in crop:
                relevance_scores.append(crop["relevance_score"])

            # Yield Potential Distribution
            if crop.get("yield_potential") and crop["yield_potential"].get("average_yield_range"):
                avg_yield = sum(crop["yield_potential"]["average_yield_range"]) / 2
                yield_potentials.append(avg_yield)

            # Climate Adaptation Distribution (simplified for now)
            if crop.get("abiotic_stress_tolerances") and crop["abiotic_stress_tolerances"].get("drought_tolerance"):
                climate_adaptations.append(crop["abiotic_stress_tolerances"]["drought_tolerance"])

            # Disease Resistance Distribution (simplified for now)
            if crop.get("disease_resistance") and crop["disease_resistance"].get("rust_resistance"):
                avg_rust_resistance = sum(crop["disease_resistance"]["rust_resistance"].values()) / len(crop["disease_resistance"]["rust_resistance"])
                disease_resistances.append(avg_rust_resistance)

            # Market Desirability Distribution (simplified for now)
            if crop.get("market_attributes") and crop["market_attributes"].get("premium_potential"):
                market_desirabilities.append(crop["market_attributes"]["premium_potential"])

            # Comparison Table Data
            comparison_entry = {
                "id": str(crop.get("id")),
                "name": crop.get("variety_name") or crop.get("name"),
                "relevance_score": round(crop.get("relevance_score", 0.0), 2),
                "category": category,
                "climate_adaptation": crop.get("abiotic_stress_tolerances", {}).get("drought_tolerance", "N/A"),
                "disease_resistance": crop.get("disease_resistance", {}).get("overall_rating", "N/A"), # Assuming an overall rating
                "market_desirability": crop.get("market_attributes", {}).get("premium_potential", "N/A"),
                "yield_potential": f"{crop.get('yield_potential', {}).get('average_yield_range', ['N/A', 'N/A'])[0]}-" \
                                   f"{crop.get('yield_potential', {}).get('average_yield_range', ['N/A', 'N/A'])[1]} " \
                                   f"{crop.get('yield_potential', {}).get('yield_unit', '')}",
                "soil_ph_range": f"{crop.get('soil_ph_min', 'N/A')}-{crop.get('soil_ph_max', 'N/A')}"
            }
            visualization_data["comparison_table_data"].append(comparison_entry)

        # Process distributions for charts
        if relevance_scores:
            bins = [i * 0.1 for i in range(11)] # 0.0 to 1.0 in 0.1 increments
            for score in relevance_scores:
                bin_index = int(score * 10)
                bin_label = f"{bins[bin_index]:.1f}-{(bins[bin_index] + 0.1):.1f}"
                visualization_data["chart_data"]["relevance_score_distribution"][bin_label] = \
                    visualization_data["chart_data"]["relevance_score_distribution"].get(bin_label, 0) + 1

        # Simple average for other distributions for now
        if yield_potentials: visualization_data["chart_data"]["yield_potential_distribution"]["average"] = sum(yield_potentials) / len(yield_potentials)
        if climate_adaptations: visualization_data["chart_data"]["climate_adaptation_distribution"]["average"] = sum(climate_adaptations) / len(climate_adaptations)
        if disease_resistances: visualization_data["chart_data"]["disease_resistance_distribution"]["average"] = sum(disease_resistances) / len(disease_resistances)
        if market_desirabilities: visualization_data["chart_data"]["market_desirability_distribution"]["average"] = sum(market_desirabilities) / len(market_desirabilities)

        return visualization_data