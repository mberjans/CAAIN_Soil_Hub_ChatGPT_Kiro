"""
Agricultural Soil Health Assessment Tests

Tests soil health assessment algorithms against established soil science
principles and extension service guidelines. Validates soil health scoring,
improvement recommendations, and management practice effectiveness.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal


class TestSoilHealthScoring:
    """Test soil health scoring algorithms."""
    
    @pytest.mark.agricultural
    def test_soil_health_score_calculation_good_soil(self, iowa_corn_farm_data, agricultural_validator):
        """Test soil health score for good quality soil."""
        
        good_soil_data = iowa_corn_farm_data['soil_data']
        
        result = self._calculate_soil_health_score(good_soil_data)
        
        # Good soil conditions should score 7-8 out of 10
        assert 7.0 <= result['overall_score'] <= 8.5
        assert result['ph_score'] >= 8.0  # pH 6.4 is optimal
        assert result['organic_matter_score'] >= 7.0  # 3.5% OM is good
        assert len(result['improvement_recommendations']) <= 2  # Few improvements needed
        
        # Validate individual component scores
        assert agricultural_validator.validate_confidence_score(result['overall_score'] / 10)
        assert all(0 <= score <= 10 for score in result['component_scores'].values())
    
    @pytest.mark.agricultural
    def test_soil_health_score_calculation_poor_soil(self, problematic_soil_data):
        """Test soil health score for poor quality soil."""
        
        poor_soil_data = problematic_soil_data['soil_data']
        
        result = self._calculate_soil_health_score(poor_soil_data)
        
        # Poor soil should have low score and multiple recommendations
        assert result['overall_score'] <= 5.0
        assert len(result['improvement_recommendations']) >= 3
        
        # Should identify specific problems
        limiting_factors = result['limiting_factors']
        assert 'low_ph' in limiting_factors or 'acidic_soil' in limiting_factors
        assert 'low_organic_matter' in limiting_factors
        assert 'compaction' in limiting_factors or 'poor_structure' in limiting_factors
    
    @pytest.mark.agricultural
    def test_soil_health_component_scoring(self):
        """Test individual soil health component scoring."""
        
        # Test pH scoring
        ph_scores = [
            (6.5, 10.0),  # Optimal
            (6.0, 9.0),   # Good
            (5.5, 6.0),   # Fair
            (5.0, 3.0),   # Poor
            (4.5, 1.0)    # Very poor
        ]
        
        for ph, expected_score in ph_scores:
            score = self._score_soil_ph(ph)
            assert abs(score - expected_score) <= 1.0, f"pH {ph} scored {score}, expected ~{expected_score}"
        
        # Test organic matter scoring
        om_scores = [
            (4.5, 10.0),  # Excellent
            (3.5, 8.0),   # Good
            (2.5, 6.0),   # Fair
            (1.5, 3.0),   # Poor
            (0.5, 1.0)    # Very poor
        ]
        
        for om, expected_score in om_scores:
            score = self._score_organic_matter(om)
            assert abs(score - expected_score) <= 1.0, f"OM {om}% scored {score}, expected ~{expected_score}"
    
    @pytest.mark.agricultural
    def test_soil_health_trend_analysis(self):
        """Test soil health trend analysis over time."""
        
        # Historical soil test data
        soil_tests = [
            {
                'test_date': date(2021, 3, 15),
                'ph': 5.8,
                'organic_matter_percent': 2.8,
                'phosphorus_ppm': 18,
                'potassium_ppm': 140
            },
            {
                'test_date': date(2022, 3, 20),
                'ph': 6.1,
                'organic_matter_percent': 3.1,
                'phosphorus_ppm': 22,
                'potassium_ppm': 155
            },
            {
                'test_date': date(2024, 3, 15),
                'ph': 6.4,
                'organic_matter_percent': 3.5,
                'phosphorus_ppm': 28,
                'potassium_ppm': 165
            }
        ]
        
        trend_analysis = self._analyze_soil_health_trends(soil_tests)
        
        # Should show improving trends
        assert trend_analysis['ph_trend'] == 'improving'
        assert trend_analysis['organic_matter_trend'] == 'improving'
        assert trend_analysis['overall_trend'] == 'improving'
        
        # Should calculate improvement rates
        assert trend_analysis['ph_change_per_year'] > 0
        assert trend_analysis['om_change_per_year'] > 0
        
        # Should provide trend-based recommendations
        assert 'continue current practices' in trend_analysis['recommendations']
    
    def _calculate_soil_health_score(self, soil_data):
        """Simulate soil health score calculation."""
        
        # Individual component scores (0-10 scale)
        ph_score = self._score_soil_ph(soil_data.get('ph', 6.5))
        om_score = self._score_organic_matter(soil_data.get('organic_matter_percent', 3.0))
        
        # Nutrient scores
        p_score = self._score_phosphorus(soil_data.get('phosphorus_ppm', 20))
        k_score = self._score_potassium(soil_data.get('potassium_ppm', 150))
        
        # Physical properties
        bulk_density = soil_data.get('bulk_density', 1.3)
        structure_score = self._score_soil_structure(bulk_density)
        
        drainage_class = soil_data.get('drainage_class', 'well_drained')
        drainage_score = self._score_drainage(drainage_class)
        
        # Component scores
        component_scores = {
            'ph': ph_score,
            'organic_matter': om_score,
            'phosphorus': p_score,
            'potassium': k_score,
            'structure': structure_score,
            'drainage': drainage_score
        }
        
        # Overall score (weighted average)
        weights = {
            'ph': 0.20,
            'organic_matter': 0.25,
            'phosphorus': 0.15,
            'potassium': 0.15,
            'structure': 0.15,
            'drainage': 0.10
        }
        
        overall_score = sum(component_scores[component] * weights[component] 
                          for component in component_scores)
        
        # Identify limiting factors
        limiting_factors = []
        if ph_score < 6.0:
            limiting_factors.append('low_ph' if soil_data.get('ph', 6.5) < 6.0 else 'high_ph')
        if om_score < 6.0:
            limiting_factors.append('low_organic_matter')
        if structure_score < 6.0:
            limiting_factors.append('compaction')
        if drainage_score < 6.0:
            limiting_factors.append('poor_drainage')
        
        # Generate improvement recommendations
        recommendations = self._generate_improvement_recommendations(component_scores, soil_data)
        
        return {
            'overall_score': overall_score,
            'component_scores': component_scores,
            'limiting_factors': limiting_factors,
            'improvement_recommendations': recommendations
        }
    
    def _score_soil_ph(self, ph):
        """Score soil pH (0-10 scale)."""
        if 6.0 <= ph <= 7.0:
            return 10.0
        elif 5.5 <= ph <= 7.5:
            return 8.0
        elif 5.0 <= ph <= 8.0:
            return 6.0
        elif 4.5 <= ph <= 8.5:
            return 3.0
        else:
            return 1.0
    
    def _score_organic_matter(self, om_percent):
        """Score organic matter content (0-10 scale)."""
        if om_percent >= 4.0:
            return 10.0
        elif om_percent >= 3.0:
            return 8.0
        elif om_percent >= 2.0:
            return 6.0
        elif om_percent >= 1.0:
            return 3.0
        else:
            return 1.0
    
    def _score_phosphorus(self, p_ppm):
        """Score phosphorus levels (0-10 scale)."""
        if p_ppm >= 30:
            return 10.0
        elif p_ppm >= 20:
            return 8.0
        elif p_ppm >= 15:
            return 6.0
        elif p_ppm >= 10:
            return 4.0
        else:
            return 2.0
    
    def _score_potassium(self, k_ppm):
        """Score potassium levels (0-10 scale)."""
        if k_ppm >= 200:
            return 10.0
        elif k_ppm >= 150:
            return 8.0
        elif k_ppm >= 120:
            return 6.0
        elif k_ppm >= 90:
            return 4.0
        else:
            return 2.0
    
    def _score_soil_structure(self, bulk_density):
        """Score soil structure based on bulk density (0-10 scale)."""
        if bulk_density <= 1.2:
            return 10.0
        elif bulk_density <= 1.4:
            return 8.0
        elif bulk_density <= 1.6:
            return 5.0
        elif bulk_density <= 1.8:
            return 3.0
        else:
            return 1.0
    
    def _score_drainage(self, drainage_class):
        """Score drainage class (0-10 scale)."""
        drainage_scores = {
            'well_drained': 10.0,
            'moderately_well_drained': 8.0,
            'somewhat_poorly_drained': 5.0,
            'poorly_drained': 2.0,
            'very_poorly_drained': 1.0
        }
        return drainage_scores.get(drainage_class, 5.0)
    
    def _generate_improvement_recommendations(self, component_scores, soil_data):
        """Generate soil improvement recommendations."""
        recommendations = []
        
        # pH recommendations
        ph = soil_data.get('ph', 6.5)
        if component_scores['ph'] < 6.0:
            if ph < 6.0:
                recommendations.append({
                    'practice': 'lime_application',
                    'priority': 'high',
                    'details': {
                        'rate_tons_per_acre': self._calculate_lime_rate(ph),
                        'timing': 'fall_application',
                        'expected_improvement': f'Raise pH to 6.5-7.0'
                    }
                })
            elif ph > 7.5:
                recommendations.append({
                    'practice': 'sulfur_application',
                    'priority': 'medium',
                    'details': {
                        'rate_lbs_per_acre': 200,
                        'timing': 'spring_application'
                    }
                })
        
        # Organic matter recommendations
        if component_scores['organic_matter'] < 6.0:
            recommendations.append({
                'practice': 'organic_matter_improvement',
                'priority': 'high',
                'details': {
                    'strategies': ['cover_crops', 'compost_application', 'reduced_tillage'],
                    'expected_improvement': 'Increase OM by 0.1-0.2% per year'
                }
            })
        
        # Structure/compaction recommendations
        if component_scores['structure'] < 6.0:
            recommendations.append({
                'practice': 'compaction_remediation',
                'priority': 'high',
                'details': {
                    'strategies': ['controlled_traffic', 'deep_tillage', 'cover_crops'],
                    'timing': 'when_soil_is_dry'
                }
            })
        
        # Nutrient recommendations
        if component_scores['phosphorus'] < 6.0:
            recommendations.append({
                'practice': 'phosphorus_buildup',
                'priority': 'medium',
                'details': {
                    'rate_lbs_p2o5_per_acre': 60,
                    'source': 'triple_superphosphate'
                }
            })
        
        if component_scores['potassium'] < 6.0:
            recommendations.append({
                'practice': 'potassium_buildup',
                'priority': 'medium',
                'details': {
                    'rate_lbs_k2o_per_acre': 80,
                    'source': 'muriate_of_potash'
                }
            })
        
        return recommendations
    
    def _calculate_lime_rate(self, current_ph, target_ph=6.5):
        """Calculate lime application rate."""
        ph_change_needed = target_ph - current_ph
        # Rough calculation: 1 ton lime per 0.5 pH unit increase
        return max(ph_change_needed * 2.0, 0.5)
    
    def _analyze_soil_health_trends(self, soil_tests):
        """Analyze soil health trends over time."""
        if len(soil_tests) < 2:
            return {'trend': 'insufficient_data'}
        
        # Sort by date
        sorted_tests = sorted(soil_tests, key=lambda x: x['test_date'])
        
        # Calculate trends
        first_test = sorted_tests[0]
        last_test = sorted_tests[-1]
        
        years_elapsed = (last_test['test_date'] - first_test['test_date']).days / 365.25
        
        # pH trend
        ph_change = last_test['ph'] - first_test['ph']
        ph_change_per_year = ph_change / years_elapsed if years_elapsed > 0 else 0
        
        # Organic matter trend
        om_change = last_test['organic_matter_percent'] - first_test['organic_matter_percent']
        om_change_per_year = om_change / years_elapsed if years_elapsed > 0 else 0
        
        # Determine trend directions
        def get_trend_direction(change_per_year, threshold=0.05):
            if change_per_year > threshold:
                return 'improving'
            elif change_per_year < -threshold:
                return 'declining'
            else:
                return 'stable'
        
        ph_trend = get_trend_direction(ph_change_per_year, 0.1)
        om_trend = get_trend_direction(om_change_per_year, 0.05)
        
        # Overall trend
        if ph_trend == 'improving' and om_trend == 'improving':
            overall_trend = 'improving'
        elif ph_trend == 'declining' or om_trend == 'declining':
            overall_trend = 'declining'
        else:
            overall_trend = 'stable'
        
        # Generate recommendations based on trends
        recommendations = []
        if overall_trend == 'improving':
            recommendations.append('continue current practices')
        elif overall_trend == 'declining':
            recommendations.append('implement soil conservation practices')
            recommendations.append('consider management changes')
        else:
            recommendations.append('maintain current soil health practices')
        
        return {
            'ph_trend': ph_trend,
            'organic_matter_trend': om_trend,
            'overall_trend': overall_trend,
            'ph_change_per_year': ph_change_per_year,
            'om_change_per_year': om_change_per_year,
            'years_analyzed': years_elapsed,
            'recommendations': recommendations
        }


class TestSoilImprovementStrategies:
    """Test soil improvement strategy recommendations."""
    
    @pytest.mark.agricultural
    def test_lime_requirement_calculation(self):
        """Test lime requirement calculation accuracy."""
        
        # Test various pH scenarios
        lime_scenarios = [
            {'current_ph': 5.2, 'target_ph': 6.5, 'expected_rate_range': (2.0, 3.0)},
            {'current_ph': 5.8, 'target_ph': 6.5, 'expected_rate_range': (1.0, 2.0)},
            {'current_ph': 6.2, 'target_ph': 6.5, 'expected_rate_range': (0.5, 1.0)},
            {'current_ph': 6.8, 'target_ph': 6.5, 'expected_rate_range': (0.0, 0.0)}  # No lime needed
        ]
        
        for scenario in lime_scenarios:
            soil_data = {
                'ph': scenario['current_ph'],
                'soil_texture': 'silt_loam',
                'organic_matter_percent': 3.0,
                'target_ph': scenario['target_ph']
            }
            
            result = self._calculate_lime_requirement(soil_data)
            
            expected_min, expected_max = scenario['expected_rate_range']
            actual_rate = result['lime_needed_tons_per_acre']
            
            assert expected_min <= actual_rate <= expected_max, \
                f"pH {scenario['current_ph']} to {scenario['target_ph']}: expected {expected_min}-{expected_max}, got {actual_rate}"
            
            # Should specify lime type and application method
            assert 'lime_type' in result
            assert result['lime_type'] in ['agricultural_limestone', 'dolomitic_limestone']
            assert 'incorporation_required' in result
    
    @pytest.mark.agricultural
    def test_organic_matter_improvement_strategies(self):
        """Test organic matter improvement strategy selection."""
        
        low_om_soil = {
            'organic_matter_percent': 1.8,  # Low OM
            'soil_texture': 'silt_loam',
            'tillage_system': 'conventional',
            'cover_crops_used': False,
            'crop_rotation': ['corn', 'corn']  # Continuous corn
        }
        
        strategies = self._get_organic_matter_improvement_strategies(low_om_soil)
        
        # Should recommend multiple strategies for low OM
        assert len(strategies['strategies']) >= 3
        
        strategy_types = [s['practice'] for s in strategies['strategies']]
        
        # Should recommend key practices
        assert 'cover_crops' in strategy_types
        assert 'reduced_tillage' in strategy_types or 'no_till' in strategy_types
        assert 'crop_rotation_diversification' in strategy_types
        
        # Each strategy should have implementation details
        for strategy in strategies['strategies']:
            assert 'implementation_steps' in strategy
            assert 'expected_improvement' in strategy
            assert strategy['priority'] in ['high', 'medium', 'low']
            
        # Should provide realistic timeline
        assert 'timeline_years' in strategies
        assert 3 <= strategies['timeline_years'] <= 10
    
    @pytest.mark.agricultural
    def test_cover_crop_selection_by_goals(self):
        """Test cover crop selection based on improvement goals."""
        
        # Nitrogen fixation goal
        n_fixation_scenario = {
            'primary_goal': 'nitrogen_fixation',
            'cash_crop': 'corn',
            'planting_window': {'start': date(2024, 9, 15), 'end': date(2024, 10, 15)},
            'termination_date': date(2025, 4, 15),
            'climate_zone': '5a'
        }
        
        n_fixation_covers = self._select_cover_crops(n_fixation_scenario)
        
        # Should recommend legume cover crops
        legume_covers = [cc for cc in n_fixation_covers if cc['type'] == 'legume']
        assert len(legume_covers) > 0
        
        # Should include nitrogen fixation potential
        for cover in legume_covers:
            assert 'nitrogen_fixation_lbs_per_acre' in cover
            assert cover['nitrogen_fixation_lbs_per_acre'] > 0
        
        # Erosion control goal
        erosion_control_scenario = {
            'primary_goal': 'erosion_control',
            'field_slope_percent': 8,  # Sloped field
            'soil_texture': 'sandy_loam',
            'climate_zone': '5a'
        }
        
        erosion_covers = self._select_cover_crops(erosion_control_scenario)
        
        # Should recommend grasses for erosion control
        grass_covers = [cc for cc in erosion_covers if cc['type'] == 'grass']
        assert len(grass_covers) > 0
        
        # Should highlight erosion control benefits
        for cover in grass_covers:
            assert 'erosion_control_rating' in cover
            assert cover['erosion_control_rating'] >= 7  # High rating
    
    @pytest.mark.agricultural
    def test_compaction_remediation_strategies(self):
        """Test compaction remediation strategy recommendations."""
        
        compacted_soil = {
            'bulk_density': 1.7,  # High bulk density
            'soil_texture': 'silt_loam',
            'compaction_depth_inches': 8,
            'traffic_patterns': 'random',
            'equipment_weight': 'heavy'
        }
        
        remediation_plan = self._develop_compaction_remediation_plan(compacted_soil)
        
        # Should include immediate and long-term strategies
        assert 'immediate_actions' in remediation_plan
        assert 'long_term_strategies' in remediation_plan
        
        # Immediate actions should address current compaction
        immediate = remediation_plan['immediate_actions']
        action_types = [action['practice'] for action in immediate]
        assert 'deep_tillage' in action_types or 'subsoiling' in action_types
        
        # Long-term strategies should prevent future compaction
        long_term = remediation_plan['long_term_strategies']
        strategy_types = [strategy['practice'] for strategy in long_term]
        assert 'controlled_traffic' in strategy_types
        assert 'cover_crops' in strategy_types
        
        # Should specify timing constraints
        for action in immediate:
            assert 'timing_requirements' in action
            assert 'soil_moisture_conditions' in action['timing_requirements']
    
    def _calculate_lime_requirement(self, soil_data):
        """Simulate lime requirement calculation."""
        current_ph = soil_data['ph']
        target_ph = soil_data.get('target_ph', 6.5)
        
        if current_ph >= target_ph:
            lime_needed = 0.0
        else:
            ph_change_needed = target_ph - current_ph
            # Buffer capacity varies by soil texture and OM
            texture = soil_data.get('soil_texture', 'loam')
            
            # Base rate calculation (simplified)
            if texture in ['sand', 'sandy_loam']:
                rate_per_ph_unit = 1.5
            elif texture in ['loam', 'silt_loam']:
                rate_per_ph_unit = 2.0
            else:  # Clay soils
                rate_per_ph_unit = 2.5
            
            lime_needed = ph_change_needed * rate_per_ph_unit
        
        # Determine lime type
        mg_level = soil_data.get('magnesium_ppm', 100)
        lime_type = 'dolomitic_limestone' if mg_level < 50 else 'agricultural_limestone'
        
        return {
            'lime_needed_tons_per_acre': max(lime_needed, 0.0),
            'lime_type': lime_type,
            'expected_ph_change': max(target_ph - current_ph, 0.0),
            'incorporation_required': True,
            'application_timing': 'fall_preferred',
            'cost_estimate_per_acre': lime_needed * 45.0  # $45/ton applied
        }
    
    def _get_organic_matter_improvement_strategies(self, soil_data):
        """Simulate organic matter improvement strategy selection."""
        current_om = soil_data['organic_matter_percent']
        target_om = min(current_om + 1.5, 4.5)  # Realistic target
        
        strategies = []
        
        # Cover crops strategy
        if not soil_data.get('cover_crops_used', False):
            strategies.append({
                'practice': 'cover_crops',
                'priority': 'high',
                'implementation_steps': [
                    'Select appropriate cover crop species',
                    'Plant after cash crop harvest',
                    'Terminate before planting'
                ],
                'expected_improvement': '0.1-0.2% OM increase per year',
                'cost_per_acre': 45.0
            })
        
        # Tillage reduction
        if soil_data.get('tillage_system') == 'conventional':
            strategies.append({
                'practice': 'reduced_tillage',
                'priority': 'high',
                'implementation_steps': [
                    'Reduce tillage passes',
                    'Maintain crop residue',
                    'Use strip-till or no-till'
                ],
                'expected_improvement': '0.05-0.1% OM increase per year',
                'cost_per_acre': -15.0  # Cost savings
            })
        
        # Crop rotation diversification
        rotation = soil_data.get('crop_rotation', [])
        if len(set(rotation)) < 2:
            strategies.append({
                'practice': 'crop_rotation_diversification',
                'priority': 'medium',
                'implementation_steps': [
                    'Add legume crops to rotation',
                    'Include small grains',
                    'Consider perennial forages'
                ],
                'expected_improvement': '0.05-0.15% OM increase per year',
                'cost_per_acre': 0.0
            })
        
        # Organic amendments
        strategies.append({
            'practice': 'organic_amendments',
            'priority': 'medium',
            'implementation_steps': [
                'Apply compost or manure',
                'Incorporate properly',
                'Test nutrient content'
            ],
            'expected_improvement': '0.1-0.3% OM increase per year',
            'cost_per_acre': 75.0
        })
        
        # Calculate timeline
        om_increase_needed = target_om - current_om
        annual_increase_rate = 0.15  # Average expected rate
        timeline_years = max(int(om_increase_needed / annual_increase_rate), 3)
        
        return {
            'strategies': strategies,
            'current_om_percent': current_om,
            'target_om_percent': target_om,
            'timeline_years': timeline_years,
            'total_cost_estimate': sum(s['cost_per_acre'] for s in strategies if s['cost_per_acre'] > 0)
        }
    
    def _select_cover_crops(self, scenario):
        """Simulate cover crop selection."""
        goal = scenario['primary_goal']
        climate_zone = scenario.get('climate_zone', '5a')
        
        # Cover crop database (simplified)
        cover_crops = {
            'crimson_clover': {
                'type': 'legume',
                'nitrogen_fixation_lbs_per_acre': 70,
                'erosion_control_rating': 6,
                'cold_tolerance': 'moderate',
                'planting_window': (date(2024, 8, 15), date(2024, 10, 1))
            },
            'winter_rye': {
                'type': 'grass',
                'nitrogen_fixation_lbs_per_acre': 0,
                'erosion_control_rating': 9,
                'cold_tolerance': 'excellent',
                'planting_window': (date(2024, 9, 1), date(2024, 11, 1))
            },
            'red_clover': {
                'type': 'legume',
                'nitrogen_fixation_lbs_per_acre': 90,
                'erosion_control_rating': 7,
                'cold_tolerance': 'good',
                'planting_window': (date(2024, 8, 1), date(2024, 9, 15))
            },
            'annual_ryegrass': {
                'type': 'grass',
                'nitrogen_fixation_lbs_per_acre': 0,
                'erosion_control_rating': 8,
                'cold_tolerance': 'good',
                'planting_window': (date(2024, 8, 15), date(2024, 10, 15))
            }
        }
        
        # Filter by goal
        suitable_covers = []
        for name, properties in cover_crops.items():
            if goal == 'nitrogen_fixation' and properties['type'] == 'legume':
                suitable_covers.append({**properties, 'name': name})
            elif goal == 'erosion_control' and properties['erosion_control_rating'] >= 7:
                suitable_covers.append({**properties, 'name': name})
            elif goal == 'general_soil_health':
                suitable_covers.append({**properties, 'name': name})
        
        # Sort by suitability for goal
        if goal == 'nitrogen_fixation':
            suitable_covers.sort(key=lambda x: x['nitrogen_fixation_lbs_per_acre'], reverse=True)
        elif goal == 'erosion_control':
            suitable_covers.sort(key=lambda x: x['erosion_control_rating'], reverse=True)
        
        return suitable_covers[:3]  # Top 3 recommendations
    
    def _develop_compaction_remediation_plan(self, soil_data):
        """Simulate compaction remediation plan development."""
        
        bulk_density = soil_data['bulk_density']
        compaction_depth = soil_data.get('compaction_depth_inches', 6)
        
        immediate_actions = []
        long_term_strategies = []
        
        # Immediate mechanical remediation
        if bulk_density > 1.6:
            if compaction_depth <= 8:
                immediate_actions.append({
                    'practice': 'deep_tillage',
                    'timing_requirements': {
                        'soil_moisture_conditions': 'dry_to_moderate',
                        'season': 'fall_preferred'
                    },
                    'equipment': 'chisel_plow_or_ripper',
                    'depth_inches': compaction_depth + 2
                })
            else:
                immediate_actions.append({
                    'practice': 'subsoiling',
                    'timing_requirements': {
                        'soil_moisture_conditions': 'dry',
                        'season': 'fall_only'
                    },
                    'equipment': 'subsoiler',
                    'depth_inches': compaction_depth + 4
                })
        
        # Long-term prevention strategies
        long_term_strategies.extend([
            {
                'practice': 'controlled_traffic',
                'implementation': 'designate_permanent_wheel_tracks',
                'expected_benefit': 'reduce_compacted_area_by_80_percent'
            },
            {
                'practice': 'cover_crops',
                'implementation': 'plant_deep_rooted_species',
                'expected_benefit': 'biological_decompaction'
            },
            {
                'practice': 'reduced_axle_loads',
                'implementation': 'limit_equipment_weight_when_possible',
                'expected_benefit': 'prevent_future_compaction'
            }
        ])
        
        return {
            'immediate_actions': immediate_actions,
            'long_term_strategies': long_term_strategies,
            'monitoring_plan': {
                'retest_bulk_density': 'annually',
                'visual_assessment': 'each_season'
            },
            'expected_timeline': '2-3_years_for_full_recovery'
        }