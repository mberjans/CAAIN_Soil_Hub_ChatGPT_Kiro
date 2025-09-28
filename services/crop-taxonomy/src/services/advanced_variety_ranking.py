"""Advanced MCDA ranking engine for crop varieties."""

from typing import Any, Dict, List, Optional
import math


class AdvancedVarietyRanking:
    """Advanced ranking engine using MCDA with AHP-derived weights and TOPSIS."""

    def __init__(self, base_weights: Optional[Dict[str, float]] = None) -> None:
        self.base_weights: Dict[str, float] = {}
        self.criteria_order: List[str] = []
        self._initialize_base_weights(base_weights)

    def _initialize_base_weights(self, base_weights: Optional[Dict[str, float]]) -> None:
        """Set up base weights and criteria ordering."""
        if base_weights is None or len(base_weights) == 0:
            self.base_weights["yield_potential"] = 0.25
            self.base_weights["climate_adaptation"] = 0.20
            self.base_weights["disease_resistance"] = 0.15
            self.base_weights["market_desirability"] = 0.15
            self.base_weights["management_ease"] = 0.10
            self.base_weights["risk_tolerance"] = 0.10
            self.base_weights["quality_attributes"] = 0.05
        else:
            for key, value in base_weights.items():
                self.base_weights[key] = float(value)

        self.criteria_order = []
        for key in self.base_weights.keys():
            self.criteria_order.append(key)

    def update_base_weights(self, new_weights: Dict[str, float]) -> None:
        """Refresh base weights when the parent service updates its configuration."""
        if new_weights:
            self.base_weights = {}
            for key, value in new_weights.items():
                self.base_weights[key] = float(value)
        self.criteria_order = []
        for key in self.base_weights.keys():
            self.criteria_order.append(key)

    def rank_varieties(
        self,
        candidates: List[Dict[str, Any]],
        regional_context: Optional[Dict[str, Any]] = None,
        farmer_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compute advanced ranking scores for candidate varieties."""
        results: Dict[str, Any] = {}
        results["results"] = {}
        criteria_copy: List[str] = []
        for criterion in self.criteria_order:
            criteria_copy.append(criterion)
        results["criteria"] = criteria_copy

        normalized_weights = self._build_contextual_weight_map(regional_context, farmer_preferences)
        weight_vector = self._compute_weight_vector(normalized_weights)
        mapped_weights = self._map_weights(weight_vector)
        results["weights"] = mapped_weights
        results["normalized_weights"] = normalized_weights

        if not candidates:
            results["ideal_best"] = {}
            results["ideal_worst"] = {}
            return results

        if len(candidates) == 1:
            single_candidate = candidates[0]
            candidate_id = str(single_candidate.get("identifier"))
            baseline = single_candidate.get("baseline_score")
            baseline_score = 1.0
            if isinstance(baseline, (int, float)):
                baseline_score = max(0.0, min(1.0, float(baseline)))

            weighted_scores = {}
            scores_dict = single_candidate.get("scores", {})
            for criterion in criteria_copy:
                criterion_score = 0.0
                if isinstance(scores_dict, dict) and criterion in scores_dict:
                    raw_value = scores_dict[criterion]
                    if isinstance(raw_value, (int, float)):
                        criterion_score = float(raw_value)
                weight_component = mapped_weights.get(criterion, 0.0)
                weighted_scores[criterion] = criterion_score * weight_component

            single_entry: Dict[str, Any] = {}
            single_entry["score"] = baseline_score
            single_entry["rank"] = 1
            single_entry["weighted_scores"] = weighted_scores
            single_entry["baseline_score"] = baseline_score
            results["results"][candidate_id] = single_entry
            results["ideal_best"] = {}
            results["ideal_worst"] = {}
            return results

        score_matrix = self._build_score_matrix(candidates)
        topsis_results = self._apply_topsis(score_matrix, weight_vector)

        closeness_scores: Dict[str, float] = {}
        weighted_details: Dict[str, Dict[str, float]] = {}
        index = 0
        while index < len(candidates):
            candidate = candidates[index]
            candidate_id = str(candidate.get("identifier"))
            closeness = 0.0
            if index < len(topsis_results["scores"]):
                closeness = topsis_results["scores"][index]
            closeness_scores[candidate_id] = closeness

            weighted_row: Dict[str, float] = {}
            row_values: List[float] = []
            if index < len(topsis_results["weighted_matrix"]):
                row_values = topsis_results["weighted_matrix"][index]

            criterion_index = 0
            while criterion_index < len(self.criteria_order):
                criterion_name = self.criteria_order[criterion_index]
                weighted_value = 0.0
                if criterion_index < len(row_values):
                    weighted_value = row_values[criterion_index]
                weighted_row[criterion_name] = weighted_value
                criterion_index += 1

            weighted_details[candidate_id] = weighted_row
            index += 1

        ranks = self._assign_ranks(closeness_scores)

        ideal_best_map: Dict[str, float] = {}
        ideal_worst_map: Dict[str, float] = {}
        criterion_index = 0
        while criterion_index < len(self.criteria_order):
            criterion_name = self.criteria_order[criterion_index]
            best_value = 0.0
            worst_value = 0.0
            if criterion_index < len(topsis_results["ideal_best"]):
                best_value = topsis_results["ideal_best"][criterion_index]
            if criterion_index < len(topsis_results["ideal_worst"]):
                worst_value = topsis_results["ideal_worst"][criterion_index]
            ideal_best_map[criterion_name] = best_value
            ideal_worst_map[criterion_name] = worst_value
            criterion_index += 1

        results["ideal_best"] = ideal_best_map
        results["ideal_worst"] = ideal_worst_map

        index = 0
        while index < len(candidates):
            candidate = candidates[index]
            candidate_id = str(candidate.get("identifier"))
            entry: Dict[str, Any] = {}
            entry["score"] = closeness_scores.get(candidate_id, 0.0)
            entry["rank"] = ranks.get(candidate_id, index + 1)
            entry["weighted_scores"] = weighted_details.get(candidate_id, {})
            baseline_value = candidate.get("baseline_score")
            if isinstance(baseline_value, (int, float)):
                entry["baseline_score"] = float(baseline_value)
            scores_snapshot: Dict[str, float] = {}
            scores_dict = candidate.get("scores", {})
            if isinstance(scores_dict, dict):
                for key, value in scores_dict.items():
                    if isinstance(value, (int, float)):
                        scores_snapshot[key] = float(value)
            entry["criteria_scores"] = scores_snapshot
            results["results"][candidate_id] = entry
            index += 1

        return results

    def _copy_base_weights(self) -> Dict[str, float]:
        """Create a mutable copy of the base weight mapping."""
        weight_map: Dict[str, float] = {}
        for key, value in self.base_weights.items():
            weight_map[key] = float(value)
        return weight_map

    def _build_contextual_weight_map(
        self,
        regional_context: Optional[Dict[str, Any]],
        farmer_preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Adjust base weights using contextual signals."""
        weight_map = self._copy_base_weights()

        if regional_context:
            climate_risks = regional_context.get("climate_risks")
            if isinstance(climate_risks, dict):
                risk_total = 0.0
                risk_count = 0
                for risk_value in climate_risks.values():
                    if isinstance(risk_value, (int, float)):
                        risk_total += float(risk_value)
                        risk_count += 1
                if risk_count > 0 and "climate_adaptation" in weight_map:
                    average_risk = risk_total / float(risk_count)
                    weight_map["climate_adaptation"] += average_risk * 0.1
                    if "risk_tolerance" in weight_map:
                        weight_map["risk_tolerance"] += average_risk * 0.05

            regional_priorities = regional_context.get("regional_priorities")
            if isinstance(regional_priorities, dict):
                feed_value = regional_priorities.get("market_focus")
                if isinstance(feed_value, (int, float)) and "market_desirability" in weight_map:
                    weight_map["market_desirability"] += float(feed_value) * 0.05

            soil_constraints = regional_context.get("soil_constraints")
            if isinstance(soil_constraints, dict) and "management_ease" in weight_map:
                constraint_level = soil_constraints.get("management_pressure")
                if isinstance(constraint_level, (int, float)):
                    weight_map["management_ease"] += float(constraint_level) * 0.05

        if farmer_preferences:
            overrides = farmer_preferences.get("weight_overrides")
            if isinstance(overrides, dict):
                for key, value in overrides.items():
                    if key in weight_map and isinstance(value, (int, float)):
                        weight_map[key] = float(value)

            primary_focus = farmer_preferences.get("primary_focus")
            if isinstance(primary_focus, str):
                lowered = primary_focus.lower()
                if lowered == "yield" and "yield_potential" in weight_map:
                    weight_map["yield_potential"] += 0.1
                elif lowered == "quality" and "quality_attributes" in weight_map:
                    weight_map["quality_attributes"] += 0.1
                elif lowered == "disease" and "disease_resistance" in weight_map:
                    weight_map["disease_resistance"] += 0.1
                elif lowered == "risk" and "risk_tolerance" in weight_map:
                    weight_map["risk_tolerance"] += 0.1

            risk_attitude = farmer_preferences.get("risk_attitude")
            if isinstance(risk_attitude, str):
                lowered_attitude = risk_attitude.lower()
                if lowered_attitude == "conservative" and "risk_tolerance" in weight_map:
                    weight_map["risk_tolerance"] += 0.05
                elif lowered_attitude == "aggressive" and "yield_potential" in weight_map:
                    weight_map["yield_potential"] += 0.05

            sustainability_focus = farmer_preferences.get("sustainability_priority")
            if isinstance(sustainability_focus, (int, float)) and "management_ease" in weight_map:
                weight_value = float(sustainability_focus)
                weight_map["management_ease"] += weight_value * 0.05

        normalized_map = self._normalize_weight_map(weight_map)
        return normalized_map

    def _normalize_weight_map(self, weight_map: Dict[str, float]) -> Dict[str, float]:
        """Normalize weight values so they sum to one."""
        total_weight = 0.0
        for key in weight_map.keys():
            value = weight_map[key]
            if value < 0.0:
                value = 0.0
            weight_map[key] = value
            total_weight += value

        normalized: Dict[str, float] = {}
        if total_weight <= 0.0 and len(weight_map) > 0:
            equal_weight = 1.0 / float(len(weight_map))
            for key in weight_map.keys():
                normalized[key] = equal_weight
        else:
            for key in weight_map.keys():
                if total_weight > 0.0:
                    normalized[key] = weight_map[key] / total_weight
                else:
                    normalized[key] = 0.0
        return normalized

    def _compute_weight_vector(self, normalized_weights: Dict[str, float]) -> List[float]:
        """Compute AHP weight vector from normalized weights."""
        comparison_matrix = self._build_pairwise_matrix(normalized_weights)
        eigenvector = self._principal_eigenvector(comparison_matrix)
        return eigenvector

    def _build_pairwise_matrix(self, normalized_weights: Dict[str, float]) -> List[List[float]]:
        """Construct pairwise comparison matrix for AHP."""
        matrix: List[List[float]] = []
        outer_index = 0
        criteria_count = len(self.criteria_order)
        while outer_index < criteria_count:
            row: List[float] = []
            criterion_i = self.criteria_order[outer_index]
            weight_i = normalized_weights.get(criterion_i, 0.0)
            if weight_i <= 0.0:
                weight_i = 0.0001
            inner_index = 0
            while inner_index < criteria_count:
                criterion_j = self.criteria_order[inner_index]
                weight_j = normalized_weights.get(criterion_j, 0.0)
                if weight_j <= 0.0:
                    weight_j = 0.0001
                ratio = weight_i / weight_j
                row.append(ratio)
                inner_index += 1
            matrix.append(row)
            outer_index += 1
        return matrix

    def _principal_eigenvector(self, matrix: List[List[float]]) -> List[float]:
        """Approximate the principal eigenvector using the geometric mean method."""
        eigenvector: List[float] = []
        matrix_length = len(matrix)
        if matrix_length == 0:
            return eigenvector

        geometric_means: List[float] = []
        total = 0.0
        row_index = 0
        while row_index < matrix_length:
            row = matrix[row_index]
            product = 1.0
            element_index = 0
            row_length = len(row)
            while element_index < row_length:
                product *= row[element_index]
                element_index += 1
            geometric_value = 0.0
            if row_length > 0:
                geometric_value = product ** (1.0 / float(row_length))
            geometric_means.append(geometric_value)
            total += geometric_value
            row_index += 1

        index = 0
        while index < len(geometric_means):
            normalized_value = 0.0
            if total > 0.0:
                normalized_value = geometric_means[index] / total
            eigenvector.append(normalized_value)
            index += 1
        return eigenvector

    def _map_weights(self, weight_vector: List[float]) -> Dict[str, float]:
        """Map weight vector back onto criteria keys."""
        mapped: Dict[str, float] = {}
        index = 0
        while index < len(self.criteria_order):
            criterion = self.criteria_order[index]
            value = 0.0
            if index < len(weight_vector):
                value = weight_vector[index]
            mapped[criterion] = value
            index += 1
        return mapped

    def _build_score_matrix(self, candidates: List[Dict[str, Any]]) -> List[List[float]]:
        """Create score matrix for TOPSIS processing."""
        matrix: List[List[float]] = []
        candidate_index = 0
        while candidate_index < len(candidates):
            candidate = candidates[candidate_index]
            row: List[float] = []
            candidate_scores = candidate.get("scores", {})
            criterion_index = 0
            while criterion_index < len(self.criteria_order):
                criterion_name = self.criteria_order[criterion_index]
                score_value = 0.0
                if isinstance(candidate_scores, dict) and criterion_name in candidate_scores:
                    raw_value = candidate_scores[criterion_name]
                    if isinstance(raw_value, (int, float)):
                        score_value = float(raw_value)
                row.append(score_value)
                criterion_index += 1
            matrix.append(row)
            candidate_index += 1
        return matrix

    def _apply_topsis(self, matrix: List[List[float]], weight_vector: List[float]) -> Dict[str, Any]:
        """Apply TOPSIS algorithm to the score matrix."""
        results: Dict[str, Any] = {}
        results["scores"] = []
        results["ideal_best"] = []
        results["ideal_worst"] = []
        results["weighted_matrix"] = []

        if not matrix:
            return results

        num_candidates = len(matrix)
        num_criteria = len(self.criteria_order)

        denominators: List[float] = []
        index = 0
        while index < num_criteria:
            denominators.append(0.0)
            index += 1

        row_index = 0
        while row_index < num_candidates:
            row = matrix[row_index]
            criterion_index = 0
            while criterion_index < num_criteria:
                value = 0.0
                if criterion_index < len(row):
                    value = row[criterion_index]
                denominators[criterion_index] += value * value
                criterion_index += 1
            row_index += 1

        criterion_index = 0
        while criterion_index < num_criteria:
            denominators[criterion_index] = math.sqrt(denominators[criterion_index])
            if denominators[criterion_index] <= 0.0:
                denominators[criterion_index] = 1.0
            criterion_index += 1

        weighted_matrix: List[List[float]] = []
        row_index = 0
        while row_index < num_candidates:
            row = matrix[row_index]
            weighted_row: List[float] = []
            criterion_index = 0
            while criterion_index < num_criteria:
                raw_value = 0.0
                if criterion_index < len(row):
                    raw_value = row[criterion_index]
                normalized_value = raw_value / denominators[criterion_index]
                weight_value = 0.0
                if criterion_index < len(weight_vector):
                    weight_value = weight_vector[criterion_index]
                weighted_value = normalized_value * weight_value
                weighted_row.append(weighted_value)
                criterion_index += 1
            weighted_matrix.append(weighted_row)
            row_index += 1

        ideal_best: List[float] = []
        ideal_worst: List[float] = []
        criterion_index = 0
        while criterion_index < num_criteria:
            best = None
            worst = None
            row_index = 0
            while row_index < len(weighted_matrix):
                value = weighted_matrix[row_index][criterion_index]
                if best is None or value > best:
                    best = value
                if worst is None or value < worst:
                    worst = value
                row_index += 1
            if best is None:
                best = 0.0
            if worst is None:
                worst = 0.0
            ideal_best.append(best)
            ideal_worst.append(worst)
            criterion_index += 1

        distance_positive: List[float] = []
        distance_negative: List[float] = []
        row_index = 0
        while row_index < len(weighted_matrix):
            weighted_row = weighted_matrix[row_index]
            sum_positive = 0.0
            sum_negative = 0.0
            criterion_index = 0
            while criterion_index < num_criteria:
                diff_positive = weighted_row[criterion_index] - ideal_best[criterion_index]
                diff_negative = weighted_row[criterion_index] - ideal_worst[criterion_index]
                sum_positive += diff_positive * diff_positive
                sum_negative += diff_negative * diff_negative
                criterion_index += 1
            distance_positive.append(math.sqrt(sum_positive))
            distance_negative.append(math.sqrt(sum_negative))
            row_index += 1

        scores: List[float] = []
        index = 0
        while index < len(distance_positive):
            denominator = distance_positive[index] + distance_negative[index]
            closeness = 0.0
            if denominator > 0.0:
                closeness = distance_negative[index] / denominator
            scores.append(closeness)
            index += 1

        results["scores"] = scores
        results["ideal_best"] = ideal_best
        results["ideal_worst"] = ideal_worst
        results["weighted_matrix"] = weighted_matrix
        return results

    def _assign_ranks(self, score_map: Dict[str, float]) -> Dict[str, int]:
        """Assign ranks based on descending score order."""
        sorted_items = sorted(score_map.items(), key=lambda item: item[1], reverse=True)
        ranks: Dict[str, int] = {}
        current_rank = 1
        last_score = None
        index = 0
        while index < len(sorted_items):
            key, value = sorted_items[index]
            if last_score is None or value < last_score:
                current_rank = index + 1
            ranks[key] = current_rank
            last_score = value
            index += 1
        return ranks

