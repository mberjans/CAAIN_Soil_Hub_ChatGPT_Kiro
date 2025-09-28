import logging
from typing import List, Dict, Any, Optional
import statistics

logger = logging.getLogger(__name__)

class FilterResultProcessor:
    """
    Processes and enhances filter results with ranking, clustering, and visualizations.
    """

    def __init__(self, scoring_weights: Optional[Dict[str, float]] = None):
        if scoring_weights:
            self.scoring_weights = scoring_weights
        else:
            self.scoring_weights = {
                "yield_potential": 0.25,
                "disease_resistance": 0.20,
                "climate_adaptation": 0.18,
                "market_desirability": 0.12,
                "management_ease": 0.10,
                "quality_attributes": 0.08,
                "risk_tolerance": 0.07
            }

    def process_results(self, results: List[Dict[str, Any]], regional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processes a list of crop filter results.

        Args:
            results: A list of crop results from the filtering engine.
            regional_context: Regional context for scoring.

        Returns:
            A dictionary containing ranked, clustered, and other processed results.
        """
        if not results:
            return {
                "ranked_results": [],
                "clustered_results": {},
                "alternative_suggestions": self.suggest_alternatives(),
                "visualization_data": {},
                "summary": "No results found. Consider broadening your filter criteria.",
            }

        ranked_results = self.rank_results(results, regional_context or {})
        clustered_results = self.cluster_results(ranked_results)
        visualization_data = self.prepare_visualization_data(ranked_results)

        return {
            "ranked_results": ranked_results,
            "clustered_results": clustered_results,
            "alternative_suggestions": [],
            "visualization_data": visualization_data,
            "summary": f"Found {len(ranked_results)} results.",
        }

    def rank_results(self, results: List[Dict[str, Any]], regional_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Ranks results based on agricultural suitability, economic potential, and risk factors.
        """
        for result in results:
            result["suitability_score"] = self._calculate_score(result, regional_context)
        return sorted(results, key=lambda x: x.get("suitability_score", 0), reverse=True)

    def _calculate_score(self, result: Dict[str, Any], regional_context: Dict[str, Any]) -> float:
        """
        Calculates a score for a single filter result.
        """
        scores = {
            "yield_potential": self._score_yield_potential(result, regional_context),
            "disease_resistance": self._score_disease_resistance(result, regional_context),
            "climate_adaptation": self._score_climate_adaptation(result, regional_context),
            "market_desirability": self._score_market_desirability(result, regional_context),
            "management_ease": self._score_management_ease(result, regional_context),
            "quality_attributes": self._score_quality_attributes(result, {}), # No farmer preferences for now
            "risk_tolerance": self._score_risk_tolerance(result, regional_context),
        }

        overall_score = sum(
            scores[factor] * self.scoring_weights[factor]
            for factor in scores
            if factor in self.scoring_weights
        )
        return overall_score

    def _score_yield_potential(self, result: Dict[str, Any], context: Dict[str, Any]) -> float:
        yield_potential = result.get("yield_potential", {})
        if not yield_potential:
            return 0.5
        
        base_score = 0.7
        
        stability_rating = yield_potential.get("yield_stability_rating")
        if stability_rating:
            stability_bonus = (stability_rating - 3.0) * 0.1
            base_score += stability_bonus
            
        regional_modifier = context.get("regional_yield_modifier", 0.0)
        base_score *= (1.0 + regional_modifier)
            
        return max(0.0, min(1.0, base_score))

    def _score_disease_resistance(self, result: Dict[str, Any], context: Dict[str, Any]) -> float:
        disease_resistance = result.get("disease_resistance", {})
        if not disease_resistance:
            return 0.3
            
        total_score = 0.0
        disease_count = 0
        
        rust_resistance = disease_resistance.get("rust_resistance", {})
        if rust_resistance:
            rust_scores = list(rust_resistance.values())
            avg_rust_score = statistics.mean(rust_scores) / 5.0
            total_score += avg_rust_score * 0.6
            disease_count += 1
            
        other_resistance = disease_resistance.get("other_disease_resistance", {})
        if other_resistance:
            other_scores = list(other_resistance.values())
            avg_other_score = statistics.mean(other_scores) / 5.0
            total_score += avg_other_score * 0.4
            disease_count += 1
            
        return total_score / disease_count if disease_count > 0 else 0.3

    def _score_climate_adaptation(self, result: Dict[str, Any], context: Dict[str, Any]) -> float:
        tolerances = result.get("abiotic_stress_tolerances", {})
        if not tolerances:
            return 0.5
            
        total_score = 0.0
        factor_count = 0
        
        climate_risks = context.get("climate_risks", {})
        
        drought_tolerance = tolerances.get("drought_tolerance")
        if "drought_risk" in climate_risks and drought_tolerance:
            drought_score = drought_tolerance / 5.0
            drought_weight = climate_risks["drought_risk"]
            total_score += drought_score * drought_weight
            factor_count += drought_weight
            
        heat_tolerance = tolerances.get("heat_tolerance")
        if "heat_risk" in climate_risks and heat_tolerance:
            heat_score = heat_tolerance / 5.0
            heat_weight = climate_risks["heat_risk"]
            total_score += heat_score * heat_weight
            factor_count += heat_weight
            
        return total_score / factor_count if factor_count > 0 else 0.5

    def _score_market_desirability(self, result: Dict[str, Any], context: Dict[str, Any]) -> float:
        market_attributes = result.get("market_attributes", {})
        if not market_attributes:
            return 0.5
            
        base_score = 0.6
        
        premium_potential = market_attributes.get("premium_potential")
        if premium_potential:
            premium_score = premium_potential / 5.0
            base_score += premium_score * 0.3
            
        market_prefs = context.get("market_preferences", [])
        if market_attributes.get("market_class") in market_prefs:
            base_score += 0.2
                
        return max(0.0, min(1.0, base_score))

    def _score_management_ease(self, result: Dict[str, Any], context: Dict[str, Any]) -> float:
        management_score = 0.6
        
        disease_score = self._score_disease_resistance(result, context)
        management_score += disease_score * 0.2
        
        climate_score = self._score_climate_adaptation(result, context)
        management_score += climate_score * 0.2
        
        return max(0.0, min(1.0, management_score))

    def _score_quality_attributes(self, result: Dict[str, Any], preferences: Dict[str, Any]) -> float:
        quality_attributes = result.get("quality_attributes", {})
        if not quality_attributes:
            return 0.5
            
        base_score = 0.7
        
        quality_prefs = preferences.get("quality_priorities", [])
        protein_range = quality_attributes.get("protein_content_range")
        if "protein_content" in quality_prefs and protein_range:
            avg_protein = statistics.mean(protein_range)
            protein_score = min(avg_protein / 15.0, 1.0)
            base_score += protein_score * 0.2
                
        return max(0.0, min(1.0, base_score))

    def _score_risk_tolerance(self, result: Dict[str, Any], context: Dict[str, Any]) -> float:
        risk_score = 0.6
        
        yield_potential = result.get("yield_potential", {})
        stability_rating = yield_potential.get("yield_stability_rating")
        if stability_rating:
            stability_factor = stability_rating / 5.0
            risk_score += stability_factor * 0.3
            
        disease_score = self._score_disease_resistance(result, context)
        risk_score += disease_score * 0.1
        
        return max(0.0, min(1.0, risk_score))

    def cluster_results(self, results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Clusters results by similarity (e.g., crop type, family).
        """
        clusters = {}
        for result in results:
            cluster_key = result.get("family", "Uncategorized")
            if cluster_key not in clusters:
                clusters[cluster_key] = []
            clusters[cluster_key].append(result)
        return clusters

    def suggest_alternatives(self) -> List[Dict[str, Any]]:
        """
        Suggests alternative crops or filter adjustments when there are no results.
        """
        # Placeholder for alternative suggestions
        return [
            {"suggestion": "Try broadening the maturity days range."},
            {"suggestion": "Consider removing a pest resistance filter."},
        ]

    def prepare_visualization_data(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Prepares data structures for frontend charts and comparison tables.
        """
        # Placeholder for visualization data
        return {
            "yield_potential": {
                "labels": [result.get("variety_name", "N/A") for result in results[:10]],
                "data": [result.get("yield_potential", {}).get("potential_yield_range", [0,0])[1] for result in results[:10]],
            },
            "suitability_scores": {
                "labels": [result.get("variety_name", "N/A") for result in results[:10]],
                "data": [result.get("suitability_score", 0) for result in results[:10]],
            }
        }
