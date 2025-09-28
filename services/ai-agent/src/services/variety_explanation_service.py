"""Variety Explanation Service.

Creates context-aware, farmer-friendly explanation payloads for crop variety
recommendations with multilingual and audience-specific support.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple


class VarietyExplanationService:
    """Build structured explanation payloads for crop variety recommendations."""

    def __init__(self) -> None:
        self.supported_languages = {
            "en": {
                "identifier": "en",
                "label": "english",
                "summary_heading": "Summary",
                "fit_heading": "Why this fits your farm",
                "management_heading": "Management guidance",
                "risk_heading": "Risks to monitor",
                "economics_heading": "Economics",
                "actions_heading": "Next actions"
            },
            "es": {
                "identifier": "es",
                "label": "spanish",
                "summary_heading": "Resumen",
                "fit_heading": "Por qué encaja en su finca",
                "management_heading": "Guía de manejo",
                "risk_heading": "Riesgos a vigilar",
                "economics_heading": "Economía",
                "actions_heading": "Próximos pasos"
            },
            "fr": {
                "identifier": "fr",
                "label": "french",
                "summary_heading": "Résumé",
                "fit_heading": "Pourquoi cela convient à votre ferme",
                "management_heading": "Conseils de gestion",
                "risk_heading": "Risques à surveiller",
                "economics_heading": "Économie",
                "actions_heading": "Actions suivantes"
            }
        }
        self.default_language = "en"

    def is_variety_recommendation(self, recommendation: Dict[str, Any]) -> bool:
        """Determine if the payload represents a variety recommendation."""
        if not isinstance(recommendation, dict):
            return False

        if "recommended_varieties" in recommendation:
            varieties = recommendation.get("recommended_varieties")
            if isinstance(varieties, list) and len(varieties) > 0:
                return True

        keys_to_check: List[str] = []
        keys_to_check.append("variety_recommendations")
        keys_to_check.append("variety_suggestions")
        for key in keys_to_check:
            if key in recommendation:
                content = recommendation.get(key)
                if isinstance(content, list) and len(content) > 0:
                    return True

        return False

    def build_explanation_payload(
        self,
        recommendation: Dict[str, Any],
        context: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build structured payload for downstream explanation generation."""
        preferences: Dict[str, Any] = {}
        if isinstance(user_preferences, dict):
            preferences = user_preferences.copy()

        language = self._determine_language(context, preferences)
        audience_level = self._determine_audience_level(context, preferences)

        varieties: List[Dict[str, Any]] = self._collect_variety_entries(recommendation)
        primary_variety = self._select_primary_variety(varieties)

        context_overview = self._build_context_overview(context)
        agronomic_considerations = self._build_agronomic_considerations(varieties, context)
        economic_summary = self._build_economic_summary(varieties)
        risk_notes = self._collect_risk_notes(varieties)
        management_actions = self._collect_management_actions(varieties)
        confidence_summary = self._summarize_confidence(varieties)
        yield_insights = self._build_yield_insights(varieties, context)
        disease_highlights = self._build_disease_highlights(varieties)
        climate_adaptation = self._build_climate_adaptation_notes(varieties, context)

        payload: Dict[str, Any] = {}
        payload["language"] = language
        payload["audience_level"] = audience_level
        payload["preferences"] = preferences
        payload["context_overview"] = context_overview
        payload["primary_variety"] = primary_variety
        payload["variety_summaries"] = varieties
        payload["agronomic_considerations"] = agronomic_considerations
        payload["economic_summary"] = economic_summary
        payload["risk_notes"] = risk_notes
        payload["management_actions"] = management_actions
        payload["confidence_summary"] = confidence_summary
        payload["yield_insights"] = yield_insights
        payload["disease_highlights"] = disease_highlights
        payload["climate_adaptation"] = climate_adaptation
        payload["raw_recommendation"] = recommendation

        structured_key_points: List[str] = []
        self._populate_key_points(structured_key_points, primary_variety, agronomic_considerations, economic_summary)
        payload["key_points"] = structured_key_points

        quality_metrics = self._evaluate_quality_metrics(
            payload,
            varieties,
            audience_level
        )
        payload["quality_metrics"] = quality_metrics

        return payload

    def build_fallback_text(self, payload: Dict[str, Any]) -> str:
        """Create deterministic explanation text when LLM is unavailable."""
        language_key = payload.get("language", self.default_language)
        templates = self.supported_languages.get(language_key)
        if templates is None:
            templates = self.supported_languages[self.default_language]

        lines: List[str] = []
        lines.append(self._capitalize_language_label(templates.get("summary_heading", "Summary"), language_key))
        primary = payload.get("primary_variety")
        if isinstance(primary, dict):
            name = primary.get("name")
            score = primary.get("overall_score")
            if name:
                summary_line = f"{name}"
                if isinstance(score, (int, float)):
                    summary_line = f"{summary_line} ({round(score * 100)}% score)"
                lines.append(summary_line)
            fit_detail = primary.get("fit_summary")
            if fit_detail:
                lines.append(str(fit_detail))

        lines.append(templates.get("fit_heading", "Why this fits your farm"))
        agronomic = payload.get("agronomic_considerations")
        if isinstance(agronomic, list):
            for item in agronomic:
                lines.append(f"- {item}")

        yield_items = payload.get("yield_insights")
        if isinstance(yield_items, list) and len(yield_items) > 0:
            lines.append("Yield outlook")
            for insight in yield_items:
                lines.append(f"- {insight}")

        disease_items = payload.get("disease_highlights")
        if isinstance(disease_items, list) and len(disease_items) > 0:
            lines.append("Disease and pest notes")
            for highlight in disease_items:
                lines.append(f"- {highlight}")

        climate_items = payload.get("climate_adaptation")
        if isinstance(climate_items, list) and len(climate_items) > 0:
            lines.append("Climate adaptation")
            for adaptation in climate_items:
                lines.append(f"- {adaptation}")

        lines.append(templates.get("management_heading", "Management guidance"))
        management_entries = payload.get("management_actions")
        if isinstance(management_entries, list):
            for entry in management_entries:
                lines.append(f"- {entry}")

        lines.append(templates.get("risk_heading", "Risks to monitor"))
        risks = payload.get("risk_notes")
        if isinstance(risks, list) and len(risks) > 0:
            for risk in risks:
                lines.append(f"- {risk}")
        else:
            lines.append("- None identified from current data")

        lines.append(templates.get("economics_heading", "Economics"))
        economics = payload.get("economic_summary")
        if isinstance(economics, list) and len(economics) > 0:
            for point in economics:
                lines.append(f"- {point}")

        lines.append(templates.get("actions_heading", "Next actions"))
        key_points = payload.get("key_points")
        if isinstance(key_points, list):
            for point in key_points:
                lines.append(f"- {point}")

        metrics = payload.get("quality_metrics")
        if isinstance(metrics, dict):
            coherence = metrics.get("coherence_score")
            coverage = metrics.get("coverage_score")
            comprehension = metrics.get("comprehension_notes")
            lines.append("Quality metrics")
            if isinstance(coherence, (int, float)):
                lines.append(f"- Coherence score: {round(float(coherence) * 100)}%")
            if isinstance(coverage, (int, float)):
                lines.append(f"- Coverage score: {round(float(coverage) * 100)}%")
            if isinstance(comprehension, list):
                index = 0
                while index < len(comprehension):
                    note = comprehension[index]
                    if isinstance(note, str) and len(note) > 0:
                        lines.append(f"- {note}")
                    index += 1

        return "\n".join(lines)

    def _determine_language(self, context: Dict[str, Any], preferences: Dict[str, Any]) -> str:
        language = self.default_language

        if preferences and "language" in preferences:
            preferred = preferences.get("language")
            if isinstance(preferred, str) and preferred in self.supported_languages:
                language = preferred
                return language

        if context:
            profile = context.get("user_profile")
            if isinstance(profile, dict):
                profile_language = profile.get("preferred_language")
                if isinstance(profile_language, str) and profile_language in self.supported_languages:
                    language = profile_language
                    return language

            direct_preference = context.get("preferred_language")
            if isinstance(direct_preference, str) and direct_preference in self.supported_languages:
                language = direct_preference
                return language

        return language

    def _determine_audience_level(self, context: Dict[str, Any], preferences: Dict[str, Any]) -> str:
        default_level = "farmer_friendly"

        if preferences and "expertise_level" in preferences:
            pref_level = preferences.get("expertise_level")
            if isinstance(pref_level, str) and len(pref_level) > 0:
                return pref_level

        if context:
            profile = context.get("user_profile")
            if isinstance(profile, dict):
                profile_level = profile.get("expertise_level")
                if isinstance(profile_level, str) and len(profile_level) > 0:
                    return profile_level

        return default_level

    def _collect_variety_entries(self, recommendation: Dict[str, Any]) -> List[Dict[str, Any]]:
        varieties: List[Dict[str, Any]] = []
        variety_sources: List[Tuple[str, Any]] = []

        candidates = recommendation.get("recommended_varieties")
        variety_sources.append(("recommended_varieties", candidates))
        candidates = recommendation.get("variety_recommendations")
        variety_sources.append(("variety_recommendations", candidates))
        candidates = recommendation.get("variety_suggestions")
        variety_sources.append(("variety_suggestions", candidates))

        for source_name, source_items in variety_sources:
            if isinstance(source_items, list):
                for entry in source_items:
                    normalized = self._normalize_variety_entry(entry, source_name)
                    if normalized:
                        varieties.append(normalized)

        return varieties

    def _normalize_variety_entry(self, entry: Any, source: str) -> Optional[Dict[str, Any]]:
        variety_data: Dict[str, Any] = {}

        if entry is None:
            return None

        if isinstance(entry, dict):
            for key, value in entry.items():
                variety_data[key] = value
        else:
            attributes = [
                "variety_name",
                "variety",
                "overall_score",
                "suitability_factors",
                "key_advantages",
                "potential_challenges",
                "recommended_practices",
                "economic_analysis",
                "confidence_level",
                "performance_prediction",
                "management_recommendations",
                "risk_assessment",
                "variety_id"
            ]
            for attribute in attributes:
                if hasattr(entry, attribute):
                    value = getattr(entry, attribute)
                    variety_data[attribute] = value

        normalized: Dict[str, Any] = {}
        normalized["source"] = source
        normalized["name"] = self._extract_variety_name(variety_data)
        normalized["overall_score"] = self._extract_numeric(variety_data.get("overall_score"))
        normalized["confidence"] = self._extract_numeric(variety_data.get("confidence_level"))
        normalized["key_advantages"] = self._coerce_string_list(variety_data.get("key_advantages"))
        normalized["potential_challenges"] = self._coerce_string_list(variety_data.get("potential_challenges"))
        normalized["recommended_practices"] = self._coerce_string_list(variety_data.get("recommended_practices"))
        normalized["management_recommendations"] = self._coerce_string_list(variety_data.get("management_recommendations"))
        normalized["fit_summary"] = self._compose_fit_summary(variety_data)
        normalized["economic_points"] = self._extract_economic_points(variety_data)
        normalized["risk_points"] = self._extract_risk_points(variety_data)
        normalized["raw"] = variety_data

        return normalized

    def _extract_variety_name(self, data: Dict[str, Any]) -> Optional[str]:
        candidate_fields = ["variety_name", "name", "variety_code"]
        index = 0
        while index < len(candidate_fields):
            field = candidate_fields[index]
            value = data.get(field)
            if isinstance(value, str) and len(value.strip()) > 0:
                return value
            index += 1

        variety_object = data.get("variety")
        if isinstance(variety_object, dict):
            nested_names = ["variety_name", "name", "display_name"]
            index = 0
            while index < len(nested_names):
                nested_key = nested_names[index]
                nested_value = variety_object.get(nested_key)
                if isinstance(nested_value, str) and len(nested_value.strip()) > 0:
                    return nested_value
                index += 1

        return None

    def _extract_numeric(self, value: Any) -> Optional[float]:
        if isinstance(value, (int, float)):
            return float(value)
        return None

    def _coerce_string_list(self, value: Any) -> List[str]:
        results: List[str] = []
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and len(item.strip()) > 0:
                    results.append(item.strip())
        elif isinstance(value, str) and len(value.strip()) > 0:
            results.append(value.strip())
        return results

    def _compose_fit_summary(self, data: Dict[str, Any]) -> Optional[str]:
        soil_notes = self._coerce_string_list(data.get("soil_fit"))
        climate_notes = self._coerce_string_list(data.get("climate_fit"))
        sentences: List[str] = []

        if len(soil_notes) > 0:
            sentences.append("Soil fit: " + soil_notes[0])

        if len(climate_notes) > 0:
            sentences.append("Climate fit: " + climate_notes[0])

        if len(sentences) == 0:
            return None

        return " ".join(sentences)

    def _extract_economic_points(self, data: Dict[str, Any]) -> List[str]:
        economics: List[str] = []
        economic_data = data.get("economic_analysis")
        if isinstance(economic_data, dict):
            for key, value in economic_data.items():
                formatted = self._format_key_value(key, value)
                if formatted:
                    economics.append(formatted)
        return economics

    def _extract_risk_points(self, data: Dict[str, Any]) -> List[str]:
        risks: List[str] = []
        risk_data = data.get("potential_challenges")
        if isinstance(risk_data, list):
            for entry in risk_data:
                if isinstance(entry, str) and len(entry.strip()) > 0:
                    risks.append(entry.strip())
        return risks

    def _format_key_value(self, key: Any, value: Any) -> Optional[str]:
        if not isinstance(key, str):
            return None

        if isinstance(value, (int, float)):
            return f"{key.replace('_', ' ')}: {round(float(value), 2)}"

        if isinstance(value, str) and len(value.strip()) > 0:
            return f"{key.replace('_', ' ')}: {value.strip()}"

        return None

    def _select_primary_variety(self, varieties: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(varieties) == 0:
            return None

        best_entry = varieties[0]
        best_score = best_entry.get("overall_score")
        index = 1
        while index < len(varieties):
            candidate = varieties[index]
            candidate_score = candidate.get("overall_score")
            if isinstance(candidate_score, (int, float)):
                if not isinstance(best_score, (int, float)) or candidate_score > best_score:
                    best_entry = candidate
                    best_score = candidate_score
            index += 1

        return best_entry

    def _build_context_overview(self, context: Dict[str, Any]) -> Dict[str, Any]:
        overview: Dict[str, Any] = {}

        if context is None:
            return overview

        soil_data = context.get("soil_data")
        if isinstance(soil_data, dict):
            overview["soil"] = soil_data

        climate_data = context.get("climate")
        if isinstance(climate_data, dict):
            overview["climate"] = climate_data

        farm_profile = context.get("farm_profile")
        if isinstance(farm_profile, dict):
            overview["farm_profile"] = farm_profile

        region = context.get("region")
        if isinstance(region, str):
            overview["region"] = region

        return overview

    def _build_agronomic_considerations(
        self,
        varieties: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[str]:
        considerations: List[str] = []

        index = 0
        while index < len(varieties):
            variety = varieties[index]
            fit_summary = variety.get("fit_summary")
            if fit_summary:
                considerations.append(fit_summary)

            advantages = variety.get("key_advantages")
            if isinstance(advantages, list):
                for advantage in advantages:
                    considerations.append(advantage)

            index += 1

        soil_data = None
        if context:
            soil_data = context.get("soil_data")
        if isinstance(soil_data, dict):
            ph = soil_data.get("ph")
            if isinstance(ph, (int, float)):
                considerations.append(f"Matches soil pH around {ph}")
            texture = soil_data.get("texture")
            if isinstance(texture, str) and len(texture) > 0:
                considerations.append(f"Suited for {texture} soils")

        return considerations

    def _build_economic_summary(self, varieties: List[Dict[str, Any]]) -> List[str]:
        economic_points: List[str] = []

        index = 0
        while index < len(varieties):
            variety = varieties[index]
            variety_economics = variety.get("economic_points")
            if isinstance(variety_economics, list):
                for entry in variety_economics:
                    economic_points.append(entry)
            index += 1

        if len(economic_points) == 0:
            economic_points.append("Monitor seed cost and market demand before purchase")

        return economic_points

    def _collect_risk_notes(self, varieties: List[Dict[str, Any]]) -> List[str]:
        risks: List[str] = []
        index = 0
        while index < len(varieties):
            variety = varieties[index]
            variety_risks = variety.get("risk_points")
            if isinstance(variety_risks, list):
                for risk in variety_risks:
                    risks.append(risk)
            index += 1
        return risks

    def _collect_management_actions(self, varieties: List[Dict[str, Any]]) -> List[str]:
        actions: List[str] = []
        index = 0
        while index < len(varieties):
            variety = varieties[index]
            recommended = variety.get("recommended_practices")
            if isinstance(recommended, list):
                for practice in recommended:
                    actions.append(practice)

            management_recs = variety.get("management_recommendations")
            if isinstance(management_recs, list):
                for recommendation in management_recs:
                    actions.append(recommendation)

            index += 1

        if len(actions) == 0:
            actions.append("Confirm seed availability with suppliers")

        return actions

    def _summarize_confidence(self, varieties: List[Dict[str, Any]]) -> Dict[str, Any]:
        summary: Dict[str, Any] = {}

        if len(varieties) == 0:
            summary["average_confidence"] = None
            summary["notes"] = "No confidence data available"
            return summary

        total_confidence = 0.0
        count = 0
        index = 0
        while index < len(varieties):
            value = varieties[index].get("confidence")
            if isinstance(value, (int, float)):
                total_confidence += float(value)
                count += 1
            index += 1

        if count > 0:
            average = total_confidence / count
            summary["average_confidence"] = round(average, 3)
            if average >= 0.8:
                summary["notes"] = "High confidence based on available trial data"
            elif average >= 0.6:
                summary["notes"] = "Moderate confidence; verify with local trials"
            else:
                summary["notes"] = "Limited confidence; gather more local data"
        else:
            summary["average_confidence"] = None
            summary["notes"] = "Confidence indicators not provided"

        return summary

    def _populate_key_points(
        self,
        key_points: List[str],
        primary_variety: Optional[Dict[str, Any]],
        agronomic_considerations: List[str],
        economic_summary: List[str]
    ) -> None:
        if isinstance(primary_variety, dict):
            name = primary_variety.get("name")
            if name:
                key_points.append(f"Primary focus: {name}")
            score = primary_variety.get("overall_score")
            if isinstance(score, (int, float)):
                key_points.append(f"Suitability score around {round(score * 100)}%")

        index = 0
        while index < len(agronomic_considerations):
            consideration = agronomic_considerations[index]
            if len(key_points) < 5:
                key_points.append(consideration)
            index += 1

        index = 0
        while index < len(economic_summary):
            economic_point = economic_summary[index]
            if len(key_points) < 7:
                key_points.append(economic_point)
            index += 1

    def prepare_prompt_payload(self, payload: Dict[str, Any]) -> str:
        """Prepare JSON payload string for LLM prompt inclusion."""
        return json.dumps(payload, indent=2, default=str)

    def _capitalize_language_label(self, label: str, language: str) -> str:
        if not isinstance(label, str) or len(label) == 0:
            return "Summary"
        if language == "en":
            return label
        return label

    def _evaluate_quality_metrics(
        self,
        payload: Dict[str, Any],
        varieties: List[Dict[str, Any]],
        audience_level: str
    ) -> Dict[str, Any]:
        metrics: Dict[str, Any] = {}

        sections = [
            payload.get("agronomic_considerations"),
            payload.get("yield_insights"),
            payload.get("disease_highlights"),
            payload.get("climate_adaptation"),
            payload.get("economic_summary"),
            payload.get("risk_notes"),
            payload.get("management_actions")
        ]

        non_empty_sections = 0
        total_sections = 0
        index = 0
        while index < len(sections):
            section = sections[index]
            if section is not None:
                total_sections += 1
                if isinstance(section, list) and len(section) > 0:
                    non_empty_sections += 1
            index += 1

        coverage_score = 0.0
        if total_sections > 0:
            coverage_score = non_empty_sections / float(total_sections)
        metrics["coverage_score"] = min(1.0, max(0.0, coverage_score))

        confidence_summary = payload.get("confidence_summary")
        confidence_value = None
        if isinstance(confidence_summary, dict):
            confidence_value = confidence_summary.get("average_confidence")

        coherence_score = coverage_score
        if isinstance(confidence_value, (int, float)):
            confidence_adjusted = (coverage_score + float(confidence_value)) / 2.0
            coherence_score = min(1.0, max(0.0, confidence_adjusted))
        metrics["coherence_score"] = coherence_score

        accuracy_flags: List[str] = []
        if not isinstance(confidence_value, (int, float)):
            accuracy_flags.append("Confidence indicators unavailable; verify with extension agronomist")

        disease_list = payload.get("disease_highlights")
        if isinstance(disease_list, list) and len(disease_list) == 1:
            entry = disease_list[0]
            if isinstance(entry, str) and "no specific resistance" in entry.lower():
                accuracy_flags.append("Disease resistance data limited; plan proactive scouting")

        risk_entries = payload.get("risk_notes")
        if isinstance(risk_entries, list) and len(risk_entries) == 0:
            accuracy_flags.append("Risk notes not provided; review management plan for gaps")

        metrics["accuracy_flags"] = accuracy_flags

        comprehension_notes: List[str] = []
        if coherence_score < 0.7:
            comprehension_notes.append("Schedule discussion with advisor to clarify variety trade-offs")

        if audience_level in ("beginner", "farmer_friendly"):
            comprehension_notes.append("Use plain language summary when sharing with field crew")
        else:
            comprehension_notes.append("Include technical appendices for advanced audience as needed")

        metrics["comprehension_notes"] = comprehension_notes

        reliability_observations = self._summarize_reliability(varieties)
        if isinstance(reliability_observations, list) and len(reliability_observations) > 0:
            metrics["reliability_observations"] = reliability_observations

        return metrics

    def _summarize_reliability(self, varieties: List[Dict[str, Any]]) -> List[str]:
        notes: List[str] = []

        index = 0
        while index < len(varieties):
            variety = varieties[index]
            raw = variety.get("raw")
            confidence = None
            if isinstance(variety, dict):
                confidence = variety.get("confidence")

            variety_details = None
            if isinstance(raw, dict):
                variety_details = raw.get("variety")

            variety_name = variety.get("name")

            if isinstance(confidence, (int, float)) and confidence < 0.6:
                if isinstance(variety_name, str):
                    notes.append(f"Confidence for {variety_name} below typical threshold; gather local trial data")

            if isinstance(variety_details, dict):
                regional_data = variety_details.get("regional_performance_data")
                if isinstance(regional_data, list) and len(regional_data) < 2:
                    if isinstance(variety_name, str):
                        notes.append(f"Limited regional trial coverage for {variety_name}")

            index += 1

        return notes

    def _build_yield_insights(
        self,
        varieties: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[str]:
        insights: List[str] = []

        index = 0
        while index < len(varieties):
            variety = varieties[index]
            raw = variety.get("raw")
            insight = self._compose_yield_message(raw)
            if insight:
                insights.append(insight)
            index += 1

        if len(insights) == 0:
            yield_context = self._extract_yield_context(context)
            if yield_context:
                insights.append(yield_context)
            else:
                insights.append("Yield potential expected to match regional benchmarks; verify with local trial data")

        return insights

    def _compose_yield_message(self, raw: Any) -> Optional[str]:
        if not isinstance(raw, dict):
            return None

        performance_prediction = raw.get("performance_prediction")
        if isinstance(performance_prediction, dict):
            predicted = performance_prediction.get("predicted_yield_range")
            if isinstance(predicted, (list, tuple)) and len(predicted) == 2:
                low_value = predicted[0]
                high_value = predicted[1]
                if isinstance(low_value, (int, float)) and isinstance(high_value, (int, float)):
                    low_text = round(float(low_value), 2)
                    high_text = round(float(high_value), 2)
                    return f"Projected yield range of {low_text}-{high_text} based on current season outlook"
            yield_confidence = performance_prediction.get("yield_confidence")
            if isinstance(yield_confidence, (int, float)):
                confidence_percent = round(float(yield_confidence) * 100)
                return f"Yield forecast supported by {confidence_percent}% confidence from integrated models"

        expectation = raw.get("yield_expectation")
        if isinstance(expectation, str) and len(expectation) > 0:
            return expectation

        variety_details = raw.get("variety")
        if isinstance(variety_details, dict):
            percentile = variety_details.get("yield_potential_percentile")
            if isinstance(percentile, (int, float)):
                return f"Yield potential ranked near the top {percentile}% of evaluated varieties"
            stability_rating = variety_details.get("yield_stability_rating")
            if isinstance(stability_rating, (int, float)):
                normalized = round(float(stability_rating), 1)
                return f"Yield stability rating of {normalized} on the 0-10 extension scale"

        return None

    def _extract_yield_context(self, context: Dict[str, Any]) -> Optional[str]:
        if not isinstance(context, dict):
            return None

        production_goals = context.get("production_goals")
        if isinstance(production_goals, dict):
            goal_value = production_goals.get("target_yield")
            if isinstance(goal_value, (int, float)):
                rounded = round(float(goal_value), 1)
                return f"Aim for approximately {rounded} unit yield; adjust fertility plan as needed"

        historical_data = context.get("historical_yield")
        if isinstance(historical_data, (int, float)):
            baseline = round(float(historical_data), 1)
            return f"Historical field average around {baseline}; monitor trial blocks for improvement"

        return None

    def _build_disease_highlights(self, varieties: List[Dict[str, Any]]) -> List[str]:
        highlights: List[str] = []

        index = 0
        while index < len(varieties):
            variety = varieties[index]
            raw = variety.get("raw")
            disease_notes = self._collect_disease_notes(raw)
            note_index = 0
            while note_index < len(disease_notes):
                highlights.append(disease_notes[note_index])
                note_index += 1
            index += 1

        if len(highlights) == 0:
            highlights.append("Review disease scouting plans; no specific resistance data provided")

        return highlights

    def _collect_disease_notes(self, raw: Any) -> List[str]:
        notes: List[str] = []
        if not isinstance(raw, dict):
            return notes

        variety_details = raw.get("variety")
        if isinstance(variety_details, dict):
            resistances = variety_details.get("disease_resistances")
            if isinstance(resistances, list):
                index = 0
                entries_added = 0
                while index < len(resistances) and entries_added < 3:
                    entry = resistances[index]
                    message = self._format_disease_entry(entry)
                    if message:
                        notes.append(message)
                        entries_added += 1
                    index += 1

        potential_challenges = raw.get("potential_challenges")
        if isinstance(potential_challenges, list):
            index = 0
            while index < len(potential_challenges):
                challenge = potential_challenges[index]
                if isinstance(challenge, str) and len(challenge) > 0:
                    notes.append(f"Management note: {challenge}")
                index += 1

        recommended_practices = raw.get("recommended_practices")
        if isinstance(recommended_practices, list):
            index = 0
            while index < len(recommended_practices):
                practice = recommended_practices[index]
                if isinstance(practice, str) and "scout" in practice.lower():
                    notes.append(practice)
                index += 1

        return notes

    def _format_disease_entry(self, entry: Any) -> Optional[str]:
        if isinstance(entry, dict):
            name = entry.get("disease_name")
            level = entry.get("resistance_level")
            if isinstance(name, str) and len(name) > 0 and isinstance(level, str) and len(level) > 0:
                formatted_level = level.replace("_", " ")
                return f"Shows {formatted_level} response to {name}"

        if hasattr(entry, "disease_name") and hasattr(entry, "resistance_level"):
            disease_name = getattr(entry, "disease_name")
            resistance_level = getattr(entry, "resistance_level")
            if isinstance(disease_name, str) and isinstance(resistance_level, str):
                formatted_level = resistance_level.replace("_", " ")
                return f"Shows {formatted_level} response to {disease_name}"

        return None

    def _build_climate_adaptation_notes(
        self,
        varieties: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[str]:
        notes: List[str] = []

        climate_context = self._extract_climate_context(context)
        if climate_context:
            notes.append(climate_context)

        index = 0
        while index < len(varieties):
            variety = varieties[index]
            raw = variety.get("raw")
            adaptation_messages = self._collect_adaptation_messages(raw)
            message_index = 0
            while message_index < len(adaptation_messages):
                notes.append(adaptation_messages[message_index])
                message_index += 1
            index += 1

        if len(notes) == 0:
            notes.append("Confirm local climate fit with regional agronomist; dataset did not include adaptation details")

        return notes

    def _extract_climate_context(self, context: Dict[str, Any]) -> Optional[str]:
        if not isinstance(context, dict):
            return None

        climate_data = context.get("climate")
        if isinstance(climate_data, dict):
            zone = climate_data.get("zone")
            if isinstance(zone, str) and len(zone) > 0:
                return f"Targeting climate zone {zone} conditions"
            hardiness = climate_data.get("hardiness_zone")
            if isinstance(hardiness, str) and len(hardiness) > 0:
                return f"Aligned with USDA hardiness zone {hardiness}"

        location_data = context.get("location")
        if isinstance(location_data, dict):
            state = location_data.get("state")
            if isinstance(state, str) and len(state) > 0:
                return f"Recommendations tuned for {state}"

        return None

    def _collect_adaptation_messages(self, raw: Any) -> List[str]:
        messages: List[str] = []
        if not isinstance(raw, dict):
            return messages

        adaptation_strategies = raw.get("adaptation_strategies")
        if isinstance(adaptation_strategies, list):
            index = 0
            while index < len(adaptation_strategies):
                entry = adaptation_strategies[index]
                if isinstance(entry, dict):
                    summary = entry.get("summary")
                    if isinstance(summary, str) and len(summary) > 0:
                        messages.append(summary)
                    detail = entry.get("detail")
                    if isinstance(detail, str) and len(detail) > 0:
                        messages.append(detail)
                index += 1

        variety_details = raw.get("variety")
        if isinstance(variety_details, dict):
            stress_tolerances = variety_details.get("stress_tolerances")
            if isinstance(stress_tolerances, list):
                index = 0
                while index < len(stress_tolerances):
                    tolerance = stress_tolerances[index]
                    if isinstance(tolerance, str) and len(tolerance) > 0:
                        messages.append(f"Includes stress tolerance for {tolerance}")
                    index += 1

        return messages
