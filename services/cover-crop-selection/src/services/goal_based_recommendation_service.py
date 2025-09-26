"""
Goal-Based Cover Crop Recommendation Service

Provides sophisticated goal-based scoring and recommendation algorithms
for cover crop selection based on farmer objectives and priorities.
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import date
import math

from ..models.cover_crop_models import (
    CoverCropSpecies, GoalBasedObjectives, SpecificGoal, GoalBasedSpeciesRecommendation,
    GoalAchievementMetrics, FarmerGoalCategory, GoalPriority, SoilBenefit,
    SoilConditions, ClimateData
)

logger = logging.getLogger(__name__)


class GoalBasedRecommendationService:
    """Service for generating goal-based cover crop recommendations."""
    
    def __init__(self):
        """Initialize the goal-based recommendation service."""
        self.goal_weight_multipliers = {
            GoalPriority.CRITICAL: 1.0,
            GoalPriority.HIGH: 0.8,
            GoalPriority.MEDIUM: 0.6,
            GoalPriority.LOW: 0.4
        }
        
        self.goal_category_benefits_mapping = {
            FarmerGoalCategory.SOIL_HEALTH: [
                SoilBenefit.ORGANIC_MATTER, SoilBenefit.SOIL_STRUCTURE,
                SoilBenefit.COMPACTION_RELIEF
            ],
            FarmerGoalCategory.NUTRIENT_MANAGEMENT: [
                SoilBenefit.NITROGEN_FIXATION, SoilBenefit.NUTRIENT_SCAVENGING
            ],
            FarmerGoalCategory.EROSION_CONTROL: [
                SoilBenefit.EROSION_CONTROL
            ],
            FarmerGoalCategory.WEED_MANAGEMENT: [
                SoilBenefit.WEED_SUPPRESSION
            ],
            FarmerGoalCategory.PEST_DISEASE_CONTROL: [
                SoilBenefit.PEST_MANAGEMENT
            ]
        }

    def generate_goal_based_recommendations(
        self,
        species_candidates: List[CoverCropSpecies],
        objectives: GoalBasedObjectives,
        soil_conditions: SoilConditions,
        climate_data: Optional[ClimateData] = None,
        planting_window: Optional[Dict[str, date]] = None
    ) -> List[GoalBasedSpeciesRecommendation]:
        """
        Generate goal-optimized cover crop recommendations.
        
        Args:
            species_candidates: Available cover crop species
            objectives: Farmer's goal-based objectives
            soil_conditions: Current soil conditions
            climate_data: Climate information
            planting_window: Preferred planting dates
            
        Returns:
            List of goal-based recommendations sorted by overall alignment
        """
        logger.info(f"Generating goal-based recommendations for {len(species_candidates)} species")
        
        recommendations = []
        
        for species in species_candidates:
            try:
                # Calculate goal achievement scores for this species
                goal_achievements = self._calculate_goal_achievements(
                    species, objectives, soil_conditions, climate_data
                )
                
                # Calculate overall goal alignment
                overall_alignment = self._calculate_overall_goal_alignment(
                    goal_achievements, objectives
                )
                
                # Calculate goal synergy score
                synergy_score = self._calculate_goal_synergy_score(
                    species, objectives, goal_achievements
                )
                
                # Generate optimized recommendations
                optimized_seeding_rate = self._optimize_seeding_rate_for_goals(
                    species, objectives, soil_conditions
                )
                
                optimized_planting_date = self._optimize_planting_date_for_goals(
                    species, objectives, climate_data, planting_window
                )
                
                optimized_termination = self._optimize_termination_for_goals(
                    species, objectives
                )
                
                # Generate goal-specific benefits and strategies
                goal_benefits = self._analyze_goal_specific_benefits(species, objectives)
                trade_offs = self._identify_goal_trade_offs(species, objectives, goal_achievements)
                enhancement_strategies = self._generate_enhancement_strategies(
                    species, objectives, goal_achievements
                )
                
                # Calculate cost-benefit analysis
                cost_benefit = self._calculate_goal_based_cost_benefit(
                    species, objectives, optimized_seeding_rate
                )
                
                # Generate management guidance
                management_notes = self._generate_goal_focused_management_notes(
                    species, objectives, goal_achievements
                )
                monitoring_plan = self._generate_goal_monitoring_plan(objectives, goal_achievements)
                
                # Create recommendation
                recommendation = GoalBasedSpeciesRecommendation(
                    species=species,
                    suitability_score=overall_alignment,
                    goal_achievement_scores=goal_achievements,
                    overall_goal_alignment=overall_alignment,
                    goal_synergy_score=synergy_score,
                    goal_optimized_seeding_rate=optimized_seeding_rate,
                    goal_optimized_planting_date=optimized_planting_date,
                    goal_optimized_termination=optimized_termination,
                    goal_specific_benefits=goal_benefits,
                    potential_goal_trade_offs=trade_offs,
                    goal_enhancement_strategies=enhancement_strategies,
                    goal_based_cost_benefit=cost_benefit,
                    goal_based_roi_estimate=cost_benefit.get('roi_estimate') if cost_benefit else None,
                    goal_focused_management_notes=management_notes,
                    goal_monitoring_plan=monitoring_plan
                )
                
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.error(f"Error generating recommendation for {species.common_name}: {str(e)}")
                continue
        
        # Sort by overall goal alignment
        recommendations.sort(key=lambda x: x.overall_goal_alignment, reverse=True)
        
        logger.info(f"Generated {len(recommendations)} goal-based recommendations")
        return recommendations

    def _calculate_goal_achievements(
        self,
        species: CoverCropSpecies,
        objectives: GoalBasedObjectives,
        soil_conditions: SoilConditions,
        climate_data: Optional[ClimateData]
    ) -> List[GoalAchievementMetrics]:
        """Calculate achievement scores for each specific goal."""
        achievements = []
        
        for goal in objectives.specific_goals:
            # Base score from species benefits alignment
            base_score = self._calculate_base_goal_score(species, goal)
            
            # Adjust for soil conditions
            soil_adjustment = self._calculate_soil_adjustment(species, goal, soil_conditions)
            
            # Adjust for climate suitability
            climate_adjustment = self._calculate_climate_adjustment(species, goal, climate_data)
            
            # Calculate final achievement score
            achievement_score = min(1.0, base_score * soil_adjustment * climate_adjustment)
            
            # Calculate confidence level
            confidence = self._calculate_confidence_level(species, goal, soil_conditions, climate_data)
            
            # Generate contributing and limiting factors
            contributing_factors = self._identify_contributing_factors(species, goal)
            limiting_factors = self._identify_limiting_factors(species, goal, soil_conditions)
            enhancement_opportunities = self._identify_enhancement_opportunities(species, goal)
            
            # Generate monitoring indicators
            monitoring_indicators = self._generate_monitoring_indicators(goal)
            
            # Create achievement metrics
            achievement = GoalAchievementMetrics(
                goal_id=goal.goal_id,
                predicted_achievement_score=achievement_score,
                confidence_level=confidence,
                quantitative_prediction=self._calculate_quantitative_prediction(species, goal),
                prediction_range=self._calculate_prediction_range(species, goal),
                primary_contributing_factors=contributing_factors,
                limiting_factors=limiting_factors,
                enhancement_opportunities=enhancement_opportunities,
                monitoring_indicators=monitoring_indicators,
                measurement_timeline=self._generate_measurement_timeline(goal)
            )
            
            achievements.append(achievement)
        
        return achievements

    def _calculate_base_goal_score(self, species: CoverCropSpecies, goal: SpecificGoal) -> float:
        """Calculate base score for goal achievement based on species characteristics."""
        score = 0.0
        
        # Check if species provides the target benefit
        if goal.target_benefit in species.primary_benefits:
            score += 0.6  # Strong base score for direct benefit match
            
            # Additional scoring for specific benefits
            if goal.target_benefit == SoilBenefit.NITROGEN_FIXATION:
                if species.nitrogen_fixation_lbs_acre:
                    # Score based on nitrogen fixation potential
                    n_fixation = species.nitrogen_fixation_lbs_acre
                    if n_fixation >= 100:
                        score += 0.4
                    elif n_fixation >= 50:
                        score += 0.3
                    else:
                        score += 0.2
                        
            elif goal.target_benefit == SoilBenefit.EROSION_CONTROL:
                # Score based on root depth and biomass production
                if species.root_depth_feet and species.root_depth_feet >= 3:
                    score += 0.2
                if species.biomass_production in ["high", "very high"]:
                    score += 0.2
                    
            elif goal.target_benefit == SoilBenefit.ORGANIC_MATTER:
                # Score based on biomass production
                if species.biomass_production in ["high", "very high"]:
                    score += 0.3
                elif species.biomass_production == "medium":
                    score += 0.2
                else:
                    score += 0.1
        
        # Secondary benefits consideration
        secondary_benefits = self.goal_category_benefits_mapping.get(goal.category, [])
        secondary_matches = [b for b in secondary_benefits if b in species.primary_benefits]
        if secondary_matches:
            score += 0.1 * len(secondary_matches)
        
        return min(1.0, score)

    def _calculate_soil_adjustment(
        self, species: CoverCropSpecies, goal: SpecificGoal, soil_conditions: SoilConditions
    ) -> float:
        """Calculate soil condition adjustment factor."""
        adjustment = 1.0
        
        # pH compatibility
        ph_min = species.ph_range['min']
        ph_max = species.ph_range['max']
        current_ph = soil_conditions.ph
        
        if ph_min <= current_ph <= ph_max:
            adjustment *= 1.0  # Optimal pH
        elif abs(current_ph - ph_min) <= 0.5 or abs(current_ph - ph_max) <= 0.5:
            adjustment *= 0.9  # Close to optimal
        else:
            adjustment *= 0.7  # Sub-optimal pH
        
        # Drainage compatibility
        if soil_conditions.drainage_class in species.drainage_tolerance:
            adjustment *= 1.0
        else:
            adjustment *= 0.8
        
        # Specific goal adjustments
        if goal.target_benefit == SoilBenefit.COMPACTION_RELIEF and soil_conditions.compaction_issues:
            if species.root_depth_feet and species.root_depth_feet >= 2:
                adjustment *= 1.2  # Bonus for deep roots when compaction present
        
        if goal.target_benefit == SoilBenefit.ORGANIC_MATTER:
            if soil_conditions.organic_matter_percent < 3.0:
                adjustment *= 1.1  # Bonus when OM is low
        
        return adjustment

    def _calculate_climate_adjustment(
        self, species: CoverCropSpecies, goal: SpecificGoal, climate_data: Optional[ClimateData]
    ) -> float:
        """Calculate climate suitability adjustment factor."""
        if not climate_data:
            return 1.0
        
        adjustment = 1.0
        
        # Hardiness zone compatibility
        if climate_data.hardiness_zone in species.hardiness_zones:
            adjustment *= 1.0
        else:
            adjustment *= 0.8
        
        # Precipitation considerations
        if climate_data.average_annual_precipitation:
            precipitation = climate_data.average_annual_precipitation
            if species.cover_crop_type.value == "legume" and precipitation < 20:
                adjustment *= 0.9  # Legumes need adequate moisture
            elif species.cover_crop_type.value == "grass" and precipitation > 40:
                adjustment *= 1.1  # Grasses thrive with good moisture
        
        return adjustment

    def _calculate_overall_goal_alignment(
        self, achievements: List[GoalAchievementMetrics], objectives: GoalBasedObjectives
    ) -> float:
        """Calculate overall goal alignment score."""
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for achievement in achievements:
            # Find corresponding goal
            goal = next((g for g in objectives.specific_goals if g.goal_id == achievement.goal_id), None)
            if not goal:
                continue
            
            # Get weight multiplier based on priority
            priority_multiplier = self.goal_weight_multipliers.get(goal.priority, 0.5)
            effective_weight = goal.weight * priority_multiplier
            
            total_weighted_score += achievement.predicted_achievement_score * effective_weight
            total_weight += effective_weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0.0

    def _calculate_goal_synergy_score(
        self,
        species: CoverCropSpecies,
        objectives: GoalBasedObjectives,
        achievements: List[GoalAchievementMetrics]
    ) -> float:
        """Calculate how well goals work together with this species."""
        synergy_score = 0.0
        
        # Check for goal synergies
        if objectives.goal_synergies:
            for primary_goal_id, synergistic_goal_ids in objectives.goal_synergies.items():
                primary_achievement = next(
                    (a for a in achievements if a.goal_id == primary_goal_id), None
                )
                if not primary_achievement:
                    continue
                
                for synergistic_goal_id in synergistic_goal_ids:
                    synergistic_achievement = next(
                        (a for a in achievements if a.goal_id == synergistic_goal_id), None
                    )
                    if synergistic_achievement:
                        # Synergy bonus based on both scores
                        synergy_bonus = (
                            primary_achievement.predicted_achievement_score *
                            synergistic_achievement.predicted_achievement_score * 0.2
                        )
                        synergy_score += synergy_bonus
        
        # Natural synergies based on species characteristics
        high_scoring_goals = [a for a in achievements if a.predicted_achievement_score > 0.7]
        if len(high_scoring_goals) >= 2:
            synergy_score += 0.1 * (len(high_scoring_goals) - 1)
        
        return min(1.0, synergy_score)

    def _optimize_seeding_rate_for_goals(
        self,
        species: CoverCropSpecies,
        objectives: GoalBasedObjectives,
        soil_conditions: SoilConditions
    ) -> float:
        """Optimize seeding rate based on goal priorities."""
        base_rate = species.seeding_rate_lbs_acre.get('broadcast', 0)
        if not base_rate:
            base_rate = list(species.seeding_rate_lbs_acre.values())[0] if species.seeding_rate_lbs_acre else 50
        
        adjustment_factor = 1.0
        
        # Adjust based on primary goals
        for goal in objectives.specific_goals:
            if goal.priority in [GoalPriority.CRITICAL, GoalPriority.HIGH]:
                if goal.target_benefit == SoilBenefit.EROSION_CONTROL:
                    adjustment_factor = max(adjustment_factor, 1.2)  # Higher rate for erosion control
                elif goal.target_benefit == SoilBenefit.WEED_SUPPRESSION:
                    adjustment_factor = max(adjustment_factor, 1.15)  # Higher rate for weed suppression
                elif goal.target_benefit == SoilBenefit.NITROGEN_FIXATION:
                    adjustment_factor = max(adjustment_factor, 1.1)  # Slightly higher for N fixation
        
        # Adjust for soil conditions
        if soil_conditions.compaction_issues:
            adjustment_factor *= 0.9  # Slightly lower rate for compacted soils
        
        return base_rate * adjustment_factor

    def _optimize_planting_date_for_goals(
        self,
        species: CoverCropSpecies,
        objectives: GoalBasedObjectives,
        climate_data: Optional[ClimateData],
        planting_window: Optional[Dict[str, date]]
    ) -> date:
        """Optimize planting date based on goal priorities."""
        # Default to middle of planting window or reasonable default
        if planting_window and 'start' in planting_window and 'end' in planting_window:
            start_date = planting_window['start']
            end_date = planting_window['end']
            days_diff = (end_date - start_date).days
            optimal_date = start_date + (end_date - start_date) / 2
        else:
            # Default planting date based on season
            if species.growing_season.value == "fall":
                optimal_date = date(2024, 9, 15)
            elif species.growing_season.value == "spring":
                optimal_date = date(2024, 4, 15)
            else:
                optimal_date = date(2024, 8, 15)
        
        # Goal-based adjustments would go here
        # For now, return the optimal date
        return optimal_date

    def _optimize_termination_for_goals(
        self, species: CoverCropSpecies, objectives: GoalBasedObjectives
    ) -> str:
        """Optimize termination method based on goal priorities."""
        available_methods = species.termination_methods
        if not available_methods:
            return "mowing"
        
        # Prioritize based on goals
        for goal in objectives.specific_goals:
            if goal.priority in [GoalPriority.CRITICAL, GoalPriority.HIGH]:
                if goal.target_benefit == SoilBenefit.ORGANIC_MATTER:
                    if "incorporation" in available_methods:
                        return "incorporation"
                elif goal.target_benefit == SoilBenefit.WEED_SUPPRESSION:
                    if "roller-crimper" in available_methods:
                        return "roller-crimper"
        
        # Default to first available method
        return available_methods[0]

    def _analyze_goal_specific_benefits(
        self, species: CoverCropSpecies, objectives: GoalBasedObjectives
    ) -> Dict[str, List[str]]:
        """Analyze benefits by goal category."""
        benefits = {}
        
        for goal in objectives.specific_goals:
            category_benefits = []
            
            if goal.target_benefit in species.primary_benefits:
                category_benefits.append(f"Direct {goal.target_benefit.value} benefit")
            
            # Add specific quantified benefits
            if goal.target_benefit == SoilBenefit.NITROGEN_FIXATION and species.nitrogen_fixation_lbs_acre:
                category_benefits.append(f"Fixes ~{species.nitrogen_fixation_lbs_acre} lbs N/acre")
            
            if goal.target_benefit == SoilBenefit.EROSION_CONTROL and species.root_depth_feet:
                category_benefits.append(f"Deep roots to {species.root_depth_feet} feet")
            
            benefits[goal.category.value] = category_benefits
        
        return benefits

    def _identify_goal_trade_offs(
        self,
        species: CoverCropSpecies,
        objectives: GoalBasedObjectives,
        achievements: List[GoalAchievementMetrics]
    ) -> Optional[List[str]]:
        """Identify potential trade-offs between goals."""
        trade_offs = []
        
        # Check for conflicting goals
        if objectives.goal_conflicts:
            for primary_goal_id, conflicting_goal_ids in objectives.goal_conflicts.items():
                primary_achievement = next(
                    (a for a in achievements if a.goal_id == primary_goal_id), None
                )
                if not primary_achievement:
                    continue
                
                for conflicting_goal_id in conflicting_goal_ids:
                    conflicting_achievement = next(
                        (a for a in achievements if a.goal_id == conflicting_goal_id), None
                    )
                    if conflicting_achievement:
                        if (primary_achievement.predicted_achievement_score > 0.7 and
                            conflicting_achievement.predicted_achievement_score < 0.5):
                            trade_offs.append(
                                f"High achievement in {primary_goal_id} may limit {conflicting_goal_id}"
                            )
        
        return trade_offs if trade_offs else None

    def _generate_enhancement_strategies(
        self,
        species: CoverCropSpecies,
        objectives: GoalBasedObjectives,
        achievements: List[GoalAchievementMetrics]
    ) -> List[str]:
        """Generate strategies to enhance goal achievement."""
        strategies = []
        
        for achievement in achievements:
            if achievement.predicted_achievement_score < 0.7:
                goal = next((g for g in objectives.specific_goals if g.goal_id == achievement.goal_id), None)
                if not goal:
                    continue
                
                if goal.target_benefit == SoilBenefit.NITROGEN_FIXATION:
                    strategies.append("Consider inoculation to enhance nitrogen fixation")
                elif goal.target_benefit == SoilBenefit.EROSION_CONTROL:
                    strategies.append("Increase seeding rate for better ground cover")
                elif goal.target_benefit == SoilBenefit.WEED_SUPPRESSION:
                    strategies.append("Plant earlier for competitive advantage over weeds")
        
        return strategies

    def _calculate_goal_based_cost_benefit(
        self,
        species: CoverCropSpecies,
        objectives: GoalBasedObjectives,
        seeding_rate: float
    ) -> Optional[Dict[str, Any]]:
        """Calculate cost-benefit analysis with goal context."""
        if not species.seed_cost_per_acre:
            return None
    
    async def analyze_goal_feasibility(
        self,
        objectives: GoalBasedObjectives,
        soil_conditions: SoilConditions,
        climate_data: Optional[ClimateData] = None,
        available_species: Optional[List[CoverCropSpecies]] = None
    ) -> Dict[str, Any]:
        """
        Analyze the feasibility of achieving farmer goals given current conditions.
        
        Args:
            objectives: Farmer's goal-based objectives
            soil_conditions: Current soil conditions
            climate_data: Climate information
            available_species: Available cover crop species to analyze
            
        Returns:
            Feasibility analysis with scores and recommendations
        """
        logger.info("Analyzing goal feasibility")
        
        feasibility_results = {}
        
        for goal in objectives.specific_goals:
            goal_feasibility = {
                'goal_name': goal.goal_name,
                'goal_category': goal.goal_category,
                'target_value': goal.target_value,
                'priority': goal.priority,
                'feasibility_score': 0.0,
                'limiting_factors': [],
                'enhancement_opportunities': [],
                'recommended_adjustments': [],
                'success_probability': 0.0
            }
            
            # Calculate base feasibility based on soil conditions
            soil_feasibility = self._calculate_soil_feasibility_for_goal(goal, soil_conditions)
            
            # Calculate climate feasibility
            climate_feasibility = self._calculate_climate_feasibility_for_goal(goal, climate_data) if climate_data else 0.7
            
            # Calculate species availability feasibility
            species_feasibility = self._calculate_species_feasibility_for_goal(goal, available_species) if available_species else 0.8
            
            # Overall feasibility score
            overall_feasibility = (soil_feasibility * 0.4 + climate_feasibility * 0.3 + species_feasibility * 0.3)
            goal_feasibility['feasibility_score'] = overall_feasibility
            goal_feasibility['success_probability'] = min(overall_feasibility * goal.weight, 1.0)
            
            # Identify limiting factors
            if soil_feasibility < 0.6:
                goal_feasibility['limiting_factors'].append("Soil conditions may limit achievement")
            if climate_feasibility < 0.6:
                goal_feasibility['limiting_factors'].append("Climate conditions may be challenging")
            if species_feasibility < 0.6:
                goal_feasibility['limiting_factors'].append("Limited suitable species available")
            
            # Enhancement opportunities
            if overall_feasibility > 0.7:
                goal_feasibility['enhancement_opportunities'].append("Strong potential for goal achievement")
            elif overall_feasibility > 0.5:
                goal_feasibility['enhancement_opportunities'].append("Moderate potential with proper management")
                goal_feasibility['recommended_adjustments'].append("Consider adjusting target value or timeline")
            else:
                goal_feasibility['recommended_adjustments'].append("Consider alternative goals or multi-year approach")
            
            feasibility_results[f"{goal.goal_category}_{goal.goal_name}"] = goal_feasibility
        
        # Overall analysis
        avg_feasibility = sum(result['feasibility_score'] for result in feasibility_results.values()) / len(feasibility_results)
        
        return {
            'individual_goal_analysis': feasibility_results,
            'overall_feasibility_score': avg_feasibility,
            'recommendation_strategy': self._determine_recommendation_strategy(avg_feasibility),
            'goal_prioritization_advice': self._generate_goal_prioritization_advice(feasibility_results)
        }
    
    def _calculate_soil_feasibility_for_goal(self, goal: SpecificGoal, soil_conditions: SoilConditions) -> float:
        """Calculate how well soil conditions support a specific goal."""
        if goal.goal_category == FarmerGoalCategory.NUTRIENT_MANAGEMENT:
            if "nitrogen" in goal.goal_name.lower():
                # Better for legume-friendly soils (higher pH, adequate P/K)
                ph_score = 1.0 if 6.0 <= soil_conditions.ph <= 7.5 else max(0.3, 1.0 - abs(soil_conditions.ph - 6.8) * 0.2)
                return min(ph_score, 1.0)
            elif "phosphorus" in goal.goal_name.lower():
                return 0.8 if soil_conditions.phosphorus_ppm < 30 else 0.5  # More benefit if P is low
        elif goal.goal_category == FarmerGoalCategory.SOIL_HEALTH:
            if "organic_matter" in goal.goal_name.lower():
                return 0.9 if soil_conditions.organic_matter_percent < 3.0 else 0.6
        elif goal.goal_category == FarmerGoalCategory.EROSION_CONTROL:
            return 0.9  # Most cover crops provide erosion control
        
        return 0.7  # Default moderate feasibility
    
    def _calculate_climate_feasibility_for_goal(self, goal: SpecificGoal, climate_data: ClimateData) -> float:
        """Calculate how well climate conditions support a specific goal."""
        # Basic climate feasibility - could be enhanced with more detailed climate analysis
        if hasattr(climate_data, 'growing_season_days'):
            if climate_data.growing_season_days > 150:
                return 0.9
            elif climate_data.growing_season_days > 100:
                return 0.7
            else:
                return 0.5
        
        return 0.7  # Default if no detailed climate data
    
    def _calculate_species_feasibility_for_goal(self, goal: SpecificGoal, available_species: List[CoverCropSpecies]) -> float:
        """Calculate species availability for achieving goal."""
        suitable_count = 0
        
        for species in available_species:
            if goal.goal_category == FarmerGoalCategory.NUTRIENT_MANAGEMENT:
                if "nitrogen" in goal.goal_name.lower() and SoilBenefit.NITROGEN_FIXATION in species.primary_benefits:
                    suitable_count += 1
            elif goal.goal_category == FarmerGoalCategory.EROSION_CONTROL:
                if SoilBenefit.EROSION_CONTROL in species.primary_benefits or SoilBenefit.EROSION_CONTROL in species.secondary_benefits:
                    suitable_count += 1
            elif goal.goal_category == FarmerGoalCategory.SOIL_HEALTH:
                if SoilBenefit.ORGANIC_MATTER in species.primary_benefits or SoilBenefit.ORGANIC_MATTER in species.secondary_benefits:
                    suitable_count += 1
        
        if suitable_count >= 3:
            return 0.9
        elif suitable_count >= 1:
            return 0.7
        else:
            return 0.3
    
    def _determine_recommendation_strategy(self, avg_feasibility: float) -> str:
        """Determine overall recommendation strategy based on feasibility."""
        if avg_feasibility >= 0.8:
            return "aggressive_optimization"
        elif avg_feasibility >= 0.6:
            return "balanced_approach"
        else:
            return "conservative_adaptation"
    
    def _generate_goal_prioritization_advice(self, feasibility_results: Dict[str, Any]) -> List[str]:
        """Generate advice on goal prioritization."""
        advice = []
        
        high_feasibility_goals = [goal for goal, data in feasibility_results.items() if data['feasibility_score'] >= 0.7]
        low_feasibility_goals = [goal for goal, data in feasibility_results.items() if data['feasibility_score'] < 0.5]
        
        if high_feasibility_goals:
            advice.append(f"Focus on high-feasibility goals: {', '.join(high_feasibility_goals)}")
        
        if low_feasibility_goals:
            advice.append(f"Consider adjusting or deferring low-feasibility goals: {', '.join(low_feasibility_goals)}")
        
        if len(feasibility_results) > 3:
            advice.append("Consider prioritizing 2-3 primary goals for best results")
        
        return advice
    
    def get_available_goal_categories(self) -> Dict[str, Any]:
        """
        Get available goal categories and their descriptions.
        
        Returns:
            Dictionary of available goal categories with descriptions and examples
        """
        logger.info("Getting available goal categories")
        
        categories = {}
        
        for category in FarmerGoalCategory:
            category_info = {
                'category_id': category.value,
                'display_name': category.value.replace('_', ' ').title(),
                'description': self._get_category_description(category),
                'typical_goals': self._get_typical_goals_for_category(category),
                'related_benefits': self._get_related_benefits(category),
                'measurement_units': self._get_measurement_units(category)
            }
            categories[category.value] = category_info
        
        return {
            'available_categories': categories,
            'category_priorities': self._get_category_priority_guidance(),
            'common_combinations': self._get_common_goal_combinations()
        }
    
    def _get_category_description(self, category: FarmerGoalCategory) -> str:
        """Get description for a goal category."""
        descriptions = {
            FarmerGoalCategory.NUTRIENT_MANAGEMENT: "Improve soil fertility and nutrient availability",
            FarmerGoalCategory.SOIL_HEALTH: "Enhance overall soil biological and physical properties",
            FarmerGoalCategory.EROSION_CONTROL: "Prevent soil loss and protect field integrity",
            FarmerGoalCategory.WEED_MANAGEMENT: "Suppress weeds naturally through cover crop competition",
            FarmerGoalCategory.PEST_DISEASE_CONTROL: "Reduce pest pressure and disease cycles",
            FarmerGoalCategory.WATER_MANAGEMENT: "Improve water infiltration and retention"
        }
        return descriptions.get(category, "Agricultural improvement goal")
    
    def _get_typical_goals_for_category(self, category: FarmerGoalCategory) -> List[str]:
        """Get typical goals for a category."""
        typical_goals = {
            FarmerGoalCategory.NUTRIENT_MANAGEMENT: [
                "maximize_nitrogen_fixation",
                "improve_phosphorus_availability",
                "enhance_potassium_cycling",
                "reduce_fertilizer_dependence"
            ],
            FarmerGoalCategory.SOIL_HEALTH: [
                "increase_organic_matter",
                "improve_soil_structure",
                "enhance_biological_activity",
                "improve_water_holding_capacity"
            ],
            FarmerGoalCategory.EROSION_CONTROL: [
                "prevent_topsoil_loss",
                "reduce_runoff_velocity",
                "stabilize_slopes",
                "protect_waterways"
            ],
            FarmerGoalCategory.WEED_MANAGEMENT: [
                "suppress_annual_weeds",
                "outcompete_problematic_species",
                "reduce_herbicide_use",
                "create_allelopathic_effects"
            ],
            FarmerGoalCategory.PEST_DISEASE_CONTROL: [
                "break_pest_cycles",
                "attract_beneficial_insects",
                "reduce_nematode_pressure",
                "interrupt_disease_cycles"
            ]
        }
        return typical_goals.get(category, [])
    
    def _get_related_benefits(self, category: FarmerGoalCategory) -> List[str]:
        """Get related soil benefits for a category."""
        return [benefit.value for benefit in self.goal_benefit_mapping.get(category, [])]
    
    def _get_measurement_units(self, category: FarmerGoalCategory) -> List[str]:
        """Get common measurement units for goal category."""
        units = {
            FarmerGoalCategory.NUTRIENT_MANAGEMENT: ["lbs/acre", "ppm", "percentage increase"],
            FarmerGoalCategory.SOIL_HEALTH: ["percentage points", "mg/kg", "score (1-10)"],
            FarmerGoalCategory.EROSION_CONTROL: ["tons/acre/year", "percentage reduction", "score (1-10)"],
            FarmerGoalCategory.WEED_MANAGEMENT: ["percentage reduction", "coverage percentage", "score (1-10)"],
            FarmerGoalCategory.PEST_DISEASE_CONTROL: ["percentage reduction", "population count", "incidence rate"]
        }
        return units.get(category, ["score (1-10)", "percentage"])
    
    def _get_category_priority_guidance(self) -> Dict[str, str]:
        """Get guidance on category priorities."""
        return {
            'new_farmers': 'Start with soil_health and erosion_control for foundational benefits',
            'experienced_farmers': 'Focus on nutrient_management and pest_disease_control for optimization',
            'conservation_focused': 'Prioritize erosion_control and water_management',
            'organic_systems': 'Emphasize nutrient_management and weed_management'
        }
    
    def _get_common_goal_combinations(self) -> List[Dict[str, Any]]:
        """Get common combinations of goals that work well together."""
        return [
            {
                'name': 'Soil Building Package',
                'categories': ['nutrient_management', 'soil_health'],
                'description': 'Build soil fertility and health simultaneously'
            },
            {
                'name': 'Conservation Package',
                'categories': ['erosion_control', 'water_management'],
                'description': 'Protect soil and water resources'
            },
            {
                'name': 'Natural Management Package',
                'categories': ['weed_management', 'pest_disease_control'],
                'description': 'Reduce chemical inputs through biological management'
            }
        ]
    
    def get_example_goal_scenarios(self) -> Dict[str, Any]:
        """
        Get example goal scenarios for different farming situations.
        
        Returns:
            Dictionary of example scenarios with complete goal configurations
        """
        logger.info("Getting example goal scenarios")
        
        scenarios = {
            'beginning_farmer': {
                'title': 'Beginning Farmer - Soil Foundation',
                'description': 'Basic soil building goals for new farmers',
                'objectives': GoalBasedObjectives(
                    specific_goals=[
                        SpecificGoal(
                            goal_name="increase_organic_matter",
                            target_value=0.5,  # 0.5% increase
                            priority=GoalPriority.HIGH,
                            goal_category=FarmerGoalCategory.SOIL_HEALTH,
                            weight=0.6
                        ),
                        SpecificGoal(
                            goal_name="prevent_erosion",
                            target_value=90.0,  # 90% erosion reduction
                            priority=GoalPriority.MEDIUM,
                            goal_category=FarmerGoalCategory.EROSION_CONTROL,
                            weight=0.4
                        )
                    ]
                ),
                'expected_outcomes': [
                    'Improved soil structure and water holding capacity',
                    'Reduced soil loss during heavy rains',
                    'Better foundation for future crop production'
                ]
            },
            'nitrogen_focused': {
                'title': 'Nitrogen Self-Sufficiency',
                'description': 'Maximize nitrogen fixation to reduce fertilizer costs',
                'objectives': GoalBasedObjectives(
                    specific_goals=[
                        SpecificGoal(
                            goal_name="maximize_nitrogen_fixation",
                            target_value=150.0,  # 150 lbs N/acre
                            priority=GoalPriority.HIGH,
                            goal_category=FarmerGoalCategory.NUTRIENT_MANAGEMENT,
                            weight=0.8
                        ),
                        SpecificGoal(
                            goal_name="improve_soil_biology",
                            target_value=25.0,  # 25% increase in biological activity
                            priority=GoalPriority.MEDIUM,
                            goal_category=FarmerGoalCategory.SOIL_HEALTH,
                            weight=0.2
                        )
                    ]
                ),
                'expected_outcomes': [
                    'Significant reduction in nitrogen fertilizer needs',
                    'Improved soil biology and mycorrhizal networks',
                    'Enhanced long-term soil fertility'
                ]
            },
            'conservation_focused': {
                'title': 'Conservation and Water Quality',
                'description': 'Protect soil and water resources',
                'objectives': GoalBasedObjectives(
                    specific_goals=[
                        SpecificGoal(
                            goal_name="prevent_topsoil_loss",
                            target_value=95.0,  # 95% reduction in soil loss
                            priority=GoalPriority.HIGH,
                            goal_category=FarmerGoalCategory.EROSION_CONTROL,
                            weight=0.5
                        ),
                        SpecificGoal(
                            goal_name="improve_water_infiltration",
                            target_value=40.0,  # 40% improvement in infiltration
                            priority=GoalPriority.HIGH,
                            goal_category=FarmerGoalCategory.WATER_MANAGEMENT,
                            weight=0.3
                        ),
                        SpecificGoal(
                            goal_name="reduce_nutrient_runoff",
                            target_value=80.0,  # 80% reduction in nutrient loss
                            priority=GoalPriority.MEDIUM,
                            goal_category=FarmerGoalCategory.NUTRIENT_MANAGEMENT,
                            weight=0.2
                        )
                    ]
                ),
                'expected_outcomes': [
                    'Dramatic reduction in soil erosion',
                    'Improved water quality in nearby streams',
                    'Better water retention during dry periods'
                ]
            },
            'integrated_pest_management': {
                'title': 'Natural Pest and Weed Control',
                'description': 'Reduce chemical inputs through biological management',
                'objectives': GoalBasedObjectives(
                    specific_goals=[
                        SpecificGoal(
                            goal_name="suppress_annual_weeds",
                            target_value=70.0,  # 70% weed suppression
                            priority=GoalPriority.HIGH,
                            goal_category=FarmerGoalCategory.WEED_MANAGEMENT,
                            weight=0.4
                        ),
                        SpecificGoal(
                            goal_name="attract_beneficial_insects",
                            target_value=200.0,  # 200% increase in beneficials
                            priority=GoalPriority.MEDIUM,
                            goal_category=FarmerGoalCategory.PEST_DISEASE_CONTROL,
                            weight=0.3
                        ),
                        SpecificGoal(
                            goal_name="break_pest_cycles",
                            target_value=60.0,  # 60% reduction in pest pressure
                            priority=GoalPriority.MEDIUM,
                            goal_category=FarmerGoalCategory.PEST_DISEASE_CONTROL,
                            weight=0.3
                        )
                    ]
                ),
                'expected_outcomes': [
                    'Reduced herbicide and pesticide applications',
                    'Increased beneficial insect populations',
                    'Disrupted pest life cycles and reduced pressure'
                ]
            },
            'high_performance': {
                'title': 'High-Performance Multi-Goal System',
                'description': 'Advanced system targeting multiple objectives',
                'objectives': GoalBasedObjectives(
                    specific_goals=[
                        SpecificGoal(
                            goal_name="maximize_nitrogen_fixation",
                            target_value=180.0,  # 180 lbs N/acre
                            priority=GoalPriority.HIGH,
                            goal_category=FarmerGoalCategory.NUTRIENT_MANAGEMENT,
                            weight=0.25
                        ),
                        SpecificGoal(
                            goal_name="increase_organic_matter",
                            target_value=0.8,  # 0.8% increase
                            priority=GoalPriority.HIGH,
                            goal_category=FarmerGoalCategory.SOIL_HEALTH,
                            weight=0.25
                        ),
                        SpecificGoal(
                            goal_name="prevent_erosion",
                            target_value=95.0,  # 95% erosion control
                            priority=GoalPriority.MEDIUM,
                            goal_category=FarmerGoalCategory.EROSION_CONTROL,
                            weight=0.2
                        ),
                        SpecificGoal(
                            goal_name="suppress_weeds",
                            target_value=75.0,  # 75% weed suppression
                            priority=GoalPriority.MEDIUM,
                            goal_category=FarmerGoalCategory.WEED_MANAGEMENT,
                            weight=0.15
                        ),
                        SpecificGoal(
                            goal_name="improve_water_retention",
                            target_value=50.0,  # 50% improvement
                            priority=GoalPriority.LOW,
                            goal_category=FarmerGoalCategory.WATER_MANAGEMENT,
                            weight=0.15
                        )
                    ]
                ),
                'expected_outcomes': [
                    'Comprehensive soil health improvement',
                    'Significant input cost reductions',
                    'Enhanced resilience to weather extremes',
                    'Optimized multi-functional cover crop system'
                ]
            }
        }
        
        return {
            'scenarios': scenarios,
            'usage_guidance': {
                'selection_tips': [
                    'Choose scenarios that match your primary farming goals',
                    'Consider your experience level and management capacity',
                    'Start with simpler scenarios and build complexity over time'
                ],
                'customization_advice': [
                    'Adjust target values based on your specific field conditions',
                    'Modify goal weights to reflect your priorities',
                    'Add or remove goals based on your farming system needs'
                ]
            }
        }
        
        # Base costs
        seed_cost = species.seed_cost_per_acre * (seeding_rate / 50)  # Adjust for rate
        establishment_cost = species.establishment_cost_per_acre or seed_cost * 1.5
        total_cost = seed_cost + establishment_cost
        
        # Estimate benefits based on goals
        total_benefits = 0.0
        
        for goal in objectives.specific_goals:
            if goal.target_benefit == SoilBenefit.NITROGEN_FIXATION and species.nitrogen_fixation_lbs_acre:
                n_value = species.nitrogen_fixation_lbs_acre * 0.50  # $0.50/lb N
                total_benefits += n_value * goal.weight
            elif goal.target_benefit == SoilBenefit.EROSION_CONTROL:
                erosion_value = 30.0  # Conservative erosion prevention value
                total_benefits += erosion_value * goal.weight
            elif goal.target_benefit == SoilBenefit.ORGANIC_MATTER:
                om_value = 25.0  # Organic matter improvement value
                total_benefits += om_value * goal.weight
        
        roi_estimate = ((total_benefits - total_cost) / total_cost * 100) if total_cost > 0 else 0
        
        return {
            'total_cost': total_cost,
            'estimated_benefits': total_benefits,
            'net_benefit': total_benefits - total_cost,
            'roi_estimate': roi_estimate,
            'cost_per_goal': total_cost / len(objectives.specific_goals)
        }

    def _generate_goal_focused_management_notes(
        self,
        species: CoverCropSpecies,
        objectives: GoalBasedObjectives,
        achievements: List[GoalAchievementMetrics]
    ) -> List[str]:
        """Generate management notes focused on goal achievement."""
        notes = []
        
        # General species management
        notes.append(f"Establish {species.common_name} with optimal seeding rate for goal achievement")
        
        # Goal-specific management
        for goal in objectives.specific_goals:
            if goal.priority in [GoalPriority.CRITICAL, GoalPriority.HIGH]:
                if goal.target_benefit == SoilBenefit.NITROGEN_FIXATION:
                    notes.append("Consider rhizobial inoculation for maximum nitrogen fixation")
                elif goal.target_benefit == SoilBenefit.EROSION_CONTROL:
                    notes.append("Ensure good ground cover establishment before high-risk periods")
                elif goal.target_benefit == SoilBenefit.WEED_SUPPRESSION:
                    notes.append("Time planting for competitive advantage over target weeds")
        
        return notes

    def _generate_goal_monitoring_plan(
        self, objectives: GoalBasedObjectives, achievements: List[GoalAchievementMetrics]
    ) -> List[str]:
        """Generate monitoring plan for goal achievement."""
        monitoring_plan = []
        
        for achievement in achievements:
            goal = next((g for g in objectives.specific_goals if g.goal_id == achievement.goal_id), None)
            if not goal:
                continue
            
            if goal.target_benefit == SoilBenefit.NITROGEN_FIXATION:
                monitoring_plan.append("Monitor nodulation 4-6 weeks after planting")
                monitoring_plan.append("Test soil N levels before termination")
            elif goal.target_benefit == SoilBenefit.EROSION_CONTROL:
                monitoring_plan.append("Assess ground cover percentage monthly")
                monitoring_plan.append("Monitor for erosion after precipitation events")
            elif goal.target_benefit == SoilBenefit.ORGANIC_MATTER:
                monitoring_plan.append("Measure biomass production before termination")
                monitoring_plan.append("Test soil organic matter annually")
        
        return monitoring_plan

    # Helper methods for achievement calculation
    def _calculate_confidence_level(
        self, species: CoverCropSpecies, goal: SpecificGoal,
        soil_conditions: SoilConditions, climate_data: Optional[ClimateData]
    ) -> float:
        """Calculate confidence level in goal achievement prediction."""
        confidence = 0.7  # Base confidence
        
        # Increase confidence for well-documented benefits
        if goal.target_benefit in species.primary_benefits:
            confidence += 0.2
        
        # Adjust for data completeness
        if climate_data:
            confidence += 0.05
        if species.nitrogen_fixation_lbs_acre:
            confidence += 0.05
        
        return min(1.0, confidence)

    def _identify_contributing_factors(self, species: CoverCropSpecies, goal: SpecificGoal) -> List[str]:
        """Identify factors contributing to goal achievement."""
        factors = []
        
        if goal.target_benefit in species.primary_benefits:
            factors.append(f"Species naturally provides {goal.target_benefit.value}")
        
        if goal.target_benefit == SoilBenefit.NITROGEN_FIXATION and species.nitrogen_fixation_lbs_acre:
            factors.append(f"High nitrogen fixation potential ({species.nitrogen_fixation_lbs_acre} lbs/acre)")
        
        if species.biomass_production in ["high", "very high"]:
            factors.append("High biomass production")
        
        return factors

    def _identify_limiting_factors(
        self, species: CoverCropSpecies, goal: SpecificGoal, soil_conditions: SoilConditions
    ) -> Optional[List[str]]:
        """Identify factors that may limit goal achievement."""
        factors = []
        
        # pH limitations
        ph_min, ph_max = species.ph_range['min'], species.ph_range['max']
        if not (ph_min <= soil_conditions.ph <= ph_max):
            factors.append(f"Soil pH ({soil_conditions.ph}) outside optimal range ({ph_min}-{ph_max})")
        
        # Drainage limitations
        if soil_conditions.drainage_class not in species.drainage_tolerance:
            factors.append(f"Drainage class ({soil_conditions.drainage_class}) not optimal")
        
        return factors if factors else None

    def _identify_enhancement_opportunities(self, species: CoverCropSpecies, goal: SpecificGoal) -> Optional[List[str]]:
        """Identify opportunities to enhance goal achievement."""
        opportunities = []
        
        if goal.target_benefit == SoilBenefit.NITROGEN_FIXATION:
            opportunities.append("Rhizobial inoculation can enhance fixation")
        
        if goal.target_benefit == SoilBenefit.WEED_SUPPRESSION:
            opportunities.append("Higher seeding rates improve weed suppression")
        
        return opportunities if opportunities else None

    def _generate_monitoring_indicators(self, goal: SpecificGoal) -> List[str]:
        """Generate monitoring indicators for a specific goal."""
        indicators = []
        
        if goal.target_benefit == SoilBenefit.NITROGEN_FIXATION:
            indicators.extend(["Root nodulation", "Plant tissue N content", "Soil nitrate levels"])
        elif goal.target_benefit == SoilBenefit.EROSION_CONTROL:
            indicators.extend(["Ground cover percentage", "Root density", "Soil loss measurements"])
        elif goal.target_benefit == SoilBenefit.ORGANIC_MATTER:
            indicators.extend(["Biomass production", "C:N ratio", "Soil organic matter tests"])
        elif goal.target_benefit == SoilBenefit.WEED_SUPPRESSION:
            indicators.extend(["Weed density", "Cover crop vigor", "Competitive index"])
        
        return indicators

    def _generate_measurement_timeline(self, goal: SpecificGoal) -> Optional[Dict[str, str]]:
        """Generate measurement timeline for goal monitoring."""
        timeline = {}
        
        if goal.target_benefit == SoilBenefit.NITROGEN_FIXATION:
            timeline = {
                "nodulation_check": "4-6 weeks after planting",
                "tissue_test": "mid-season peak growth",
                "soil_test": "before termination"
            }
        elif goal.target_benefit == SoilBenefit.EROSION_CONTROL:
            timeline = {
                "cover_assessment": "monthly during growing season",
                "root_evaluation": "before termination",
                "erosion_monitoring": "after significant rainfall events"
            }
        
        return timeline if timeline else None

    def _calculate_quantitative_prediction(self, species: CoverCropSpecies, goal: SpecificGoal) -> Optional[float]:
        """Calculate quantitative prediction for goal achievement."""
        if goal.target_benefit == SoilBenefit.NITROGEN_FIXATION and species.nitrogen_fixation_lbs_acre:
            return species.nitrogen_fixation_lbs_acre
        
        return None

    def _calculate_prediction_range(self, species: CoverCropSpecies, goal: SpecificGoal) -> Optional[Dict[str, float]]:
        """Calculate prediction range for quantitative goals."""
        quantitative = self._calculate_quantitative_prediction(species, goal)
        if quantitative:
            return {
                "min": quantitative * 0.7,  # Conservative estimate
                "max": quantitative * 1.2   # Optimistic estimate
            }
        
        return None