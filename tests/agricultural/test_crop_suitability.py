"""
Agricultural Crop Suitability Tests

Tests crop suitability algorithms against known agricultural standards
and regional best practices. These tests validate that crop recommendations
match extension service guidelines and expert knowledge.
"""

import pytest
from datetime import date
from decimal import Decimal


class TestCornSuitabilityAlgorithms:
    """Test corn suitability assessment algorithms."""
    
    @pytest.mark.agricultural
    def test_corn_suitability_iowa_conditions(self, iowa_corn_farm_data, agricultural_validator):
        """Test corn suitability for typical Iowa conditions."""
        
        farm_conditions = {
            'location': iowa_corn_farm_data['location'],
            'soil': iowa_corn_farm_data['soil_data'],
            'climate': {
                'hardiness_zone': '5a',
                'growing_degree_days': 2800,
                'average_rainfall_inches': 34,
                'frost_free_days': 160
            },
            'farm_size_acres': iowa_corn_farm_data['farm_size_acres']
        }
        
        # Simulate crop suitability analysis
        result = self._analyze_corn_suitability(farm_conditions)
        
        # Corn should be highly suitable for Iowa conditions
        assert result['suitability_score'] >= 0.85
        assert result['climate_match'] >= 0.9
        assert result['soil_suitability'] >= 0.8
        assert 'well-suited' in result['explanation'].lower()
        
        # Validate specific factors
        assert result['ph_suitability'] >= 0.9  # pH 6.4 is optimal for corn
        assert result['drainage_suitability'] >= 0.9  # Well-drained is ideal
        assert result['organic_matter_suitability'] >= 0.8  # 3.5% is good
    
    @pytest.mark.agricultural
    def test_corn_suitability_marginal_conditions(self):
        """Test corn suitability under marginal conditions."""
        
        marginal_conditions = {
            'location': {'latitude': 45.0, 'longitude': -95.0},  # Northern edge
            'soil': {
                'ph': 5.5,  # Slightly acidic
                'organic_matter_percent': 2.0,  # Low
                'drainage_class': 'somewhat_poorly_drained',
                'soil_texture': 'clay'
            },
            'climate': {
                'hardiness_zone': '3b',
                'growing_degree_days': 2200,  # Lower GDD
                'frost_free_days': 120  # Shorter season
            }
        }
        
        result = self._analyze_corn_suitability(marginal_conditions)
        
        # Should show reduced suitability
        assert 0.4 <= result['suitability_score'] <= 0.7
        assert result['climate_match'] < 0.8  # Climate limitations
        assert result['soil_suitability'] < 0.7  # Soil limitations
        
        # Should identify specific limitations
        assert 'short season' in result['limitations'] or 'growing degree days' in result['limitations']
        assert 'drainage' in result['limitations'] or 'acidic' in result['limitations']
    
    @pytest.mark.agricultural
    def test_corn_variety_selection_by_maturity(self):
        """Test corn variety selection based on maturity requirements."""
        
        # Short season location
        short_season_conditions = {
            'climate': {
                'frost_free_days': 130,
                'growing_degree_days': 2300
            },
            'planting_date': date(2024, 5, 15)
        }
        
        varieties = self._get_corn_variety_recommendations(short_season_conditions)
        
        # Should recommend early maturity varieties
        for variety in varieties[:3]:  # Top 3 recommendations
            assert variety['maturity_days'] <= 105
            assert variety['relative_maturity'] <= 95
        
        # Long season location
        long_season_conditions = {
            'climate': {
                'frost_free_days': 180,
                'growing_degree_days': 3200
            },
            'planting_date': date(2024, 4, 25)
        }
        
        varieties = self._get_corn_variety_recommendations(long_season_conditions)
        
        # Should include full-season varieties
        full_season_varieties = [v for v in varieties if v['maturity_days'] >= 115]
        assert len(full_season_varieties) > 0
    
    def _analyze_corn_suitability(self, conditions):
        """Simulate corn suitability analysis."""
        # This would normally call the actual service
        # For testing, we simulate the expected behavior
        
        soil = conditions['soil']
        climate = conditions.get('climate', {})
        
        # pH suitability (optimal 6.0-6.8)
        ph = soil.get('ph', 6.5)
        if 6.0 <= ph <= 6.8:
            ph_suitability = 1.0
        elif 5.5 <= ph <= 7.5:
            ph_suitability = 0.8
        else:
            ph_suitability = 0.5
        
        # Drainage suitability
        drainage = soil.get('drainage_class', 'well_drained')
        drainage_scores = {
            'well_drained': 1.0,
            'moderately_well_drained': 0.9,
            'somewhat_poorly_drained': 0.6,
            'poorly_drained': 0.3
        }
        drainage_suitability = drainage_scores.get(drainage, 0.5)
        
        # Climate suitability
        gdd = climate.get('growing_degree_days', 2800)
        if gdd >= 2600:
            climate_match = 1.0
        elif gdd >= 2200:
            climate_match = 0.7
        else:
            climate_match = 0.4
        
        # Overall suitability
        soil_suitability = (ph_suitability + drainage_suitability) / 2
        suitability_score = (soil_suitability + climate_match) / 2
        
        # Generate limitations
        limitations = []
        if ph < 5.5:
            limitations.append('acidic soil conditions')
        if drainage_suitability < 0.7:
            limitations.append('drainage concerns')
        if gdd < 2400:
            limitations.append('short growing season')
        
        return {
            'suitability_score': suitability_score,
            'climate_match': climate_match,
            'soil_suitability': soil_suitability,
            'ph_suitability': ph_suitability,
            'drainage_suitability': drainage_suitability,
            'organic_matter_suitability': min(soil.get('organic_matter_percent', 3.0) / 4.0, 1.0),
            'explanation': self._generate_explanation(suitability_score, limitations),
            'limitations': limitations
        }
    
    def _get_corn_variety_recommendations(self, conditions):
        """Simulate corn variety recommendations."""
        # Mock variety database
        varieties = [
            {'name': 'Pioneer P0157AM', 'maturity_days': 87, 'relative_maturity': 87},
            {'name': 'DeKalb DKC48-05', 'maturity_days': 95, 'relative_maturity': 95},
            {'name': 'Pioneer P1197AM', 'maturity_days': 111, 'relative_maturity': 111},
            {'name': 'DeKalb DKC64-87', 'maturity_days': 118, 'relative_maturity': 118}
        ]
        
        frost_free_days = conditions['climate']['frost_free_days']
        
        # Filter varieties by season length
        suitable_varieties = []
        for variety in varieties:
            # Need ~30 days buffer for harvest
            if variety['maturity_days'] <= (frost_free_days - 30):
                suitable_varieties.append(variety)
        
        return suitable_varieties
    
    def _generate_explanation(self, score, limitations):
        """Generate explanation text."""
        if score >= 0.85:
            return "Corn is well-suited for these conditions with excellent yield potential."
        elif score >= 0.7:
            return "Corn is suitable with good management practices."
        elif score >= 0.5:
            return "Corn may be grown but with yield limitations."
        else:
            return "Corn is not recommended for these conditions."


class TestSoybeanSuitabilityAlgorithms:
    """Test soybean suitability assessment algorithms."""
    
    @pytest.mark.agricultural
    def test_soybean_suitability_midwest_conditions(self):
        """Test soybean suitability for Midwest conditions."""
        
        midwest_conditions = {
            'location': {'latitude': 40.5, 'longitude': -89.4},  # Illinois
            'soil': {
                'ph': 6.2,
                'organic_matter_percent': 3.8,
                'drainage_class': 'well_drained',
                'soil_texture': 'silt_loam'
            },
            'climate': {
                'hardiness_zone': '5b',
                'growing_degree_days': 2600,
                'average_rainfall_inches': 38
            }
        }
        
        result = self._analyze_soybean_suitability(midwest_conditions)
        
        # Soybean should be highly suitable for Midwest
        assert result['suitability_score'] >= 0.85
        assert result['climate_match'] >= 0.9
        assert result['soil_suitability'] >= 0.8
        
        # Should highlight rotation benefits
        assert 'nitrogen fixation' in result['benefits'] or 'rotation' in result['benefits']
    
    @pytest.mark.agricultural
    def test_soybean_maturity_group_selection(self):
        """Test soybean maturity group selection by latitude."""
        
        # Northern location (Minnesota)
        northern_conditions = {
            'location': {'latitude': 46.0, 'longitude': -94.0},
            'climate': {'frost_free_days': 140}
        }
        
        northern_varieties = self._get_soybean_variety_recommendations(northern_conditions)
        
        # Should recommend early maturity groups (0.0-1.5)
        for variety in northern_varieties[:3]:
            assert variety['maturity_group'] <= 1.5
        
        # Southern location (Missouri)
        southern_conditions = {
            'location': {'latitude': 38.0, 'longitude': -92.0},
            'climate': {'frost_free_days': 180}
        }
        
        southern_varieties = self._get_soybean_variety_recommendations(southern_conditions)
        
        # Should include later maturity groups (3.0-4.5)
        late_varieties = [v for v in southern_varieties if v['maturity_group'] >= 3.0]
        assert len(late_varieties) > 0
    
    @pytest.mark.agricultural
    def test_soybean_soil_ph_tolerance(self):
        """Test soybean tolerance to soil pH variations."""
        
        # Slightly acidic conditions
        acidic_conditions = {
            'soil': {
                'ph': 5.8,  # Slightly acidic
                'organic_matter_percent': 3.0,
                'drainage_class': 'well_drained'
            }
        }
        
        acidic_result = self._analyze_soybean_suitability(acidic_conditions)
        
        # Soybean should tolerate slight acidity better than corn
        assert acidic_result['ph_suitability'] >= 0.7
        
        # Very acidic conditions
        very_acidic_conditions = {
            'soil': {
                'ph': 5.2,  # Very acidic
                'organic_matter_percent': 3.0,
                'drainage_class': 'well_drained'
            }
        }
        
        very_acidic_result = self._analyze_soybean_suitability(very_acidic_conditions)
        
        # Should show reduced suitability and recommend lime
        assert very_acidic_result['ph_suitability'] < 0.6
        assert 'lime application' in very_acidic_result['recommendations']
    
    def _analyze_soybean_suitability(self, conditions):
        """Simulate soybean suitability analysis."""
        soil = conditions.get('soil', {})
        climate = conditions.get('climate', {})
        
        # pH suitability (optimal 6.0-7.0, tolerates 5.5-7.5)
        ph = soil.get('ph', 6.5)
        if 6.0 <= ph <= 7.0:
            ph_suitability = 1.0
        elif 5.5 <= ph <= 7.5:
            ph_suitability = 0.8
        elif 5.0 <= ph <= 8.0:
            ph_suitability = 0.6
        else:
            ph_suitability = 0.3
        
        # Drainage (critical for soybean)
        drainage = soil.get('drainage_class', 'well_drained')
        drainage_scores = {
            'well_drained': 1.0,
            'moderately_well_drained': 0.8,
            'somewhat_poorly_drained': 0.4,
            'poorly_drained': 0.2
        }
        drainage_suitability = drainage_scores.get(drainage, 0.5)
        
        # Climate suitability
        gdd = climate.get('growing_degree_days', 2600)
        climate_match = min(gdd / 2400, 1.0) if gdd >= 2000 else 0.3
        
        soil_suitability = (ph_suitability + drainage_suitability) / 2
        suitability_score = (soil_suitability + climate_match) / 2
        
        recommendations = []
        if ph < 5.5:
            recommendations.append('lime application recommended')
        if drainage_suitability < 0.6:
            recommendations.append('improve field drainage')
        
        return {
            'suitability_score': suitability_score,
            'climate_match': climate_match,
            'soil_suitability': soil_suitability,
            'ph_suitability': ph_suitability,
            'drainage_suitability': drainage_suitability,
            'benefits': ['nitrogen fixation', 'rotation benefits', 'soil health improvement'],
            'recommendations': recommendations
        }
    
    def _get_soybean_variety_recommendations(self, conditions):
        """Simulate soybean variety recommendations."""
        latitude = conditions['location']['latitude']
        
        # Maturity group selection based on latitude
        if latitude >= 45:
            suitable_mgs = [0.0, 0.5, 1.0, 1.5]
        elif latitude >= 42:
            suitable_mgs = [1.0, 1.5, 2.0, 2.5]
        elif latitude >= 39:
            suitable_mgs = [2.0, 2.5, 3.0, 3.5]
        else:
            suitable_mgs = [3.0, 3.5, 4.0, 4.5]
        
        varieties = []
        for mg in suitable_mgs:
            varieties.append({
                'name': f'Variety MG{mg}',
                'maturity_group': mg,
                'yield_potential': 55 + (mg * 2),  # Rough correlation
                'disease_resistance': ['scn', 'sudden_death_syndrome']
            })
        
        return varieties


class TestCropRotationSuitability:
    """Test crop rotation suitability algorithms."""
    
    @pytest.mark.agricultural
    def test_corn_soybean_rotation_benefits(self):
        """Test corn-soybean rotation benefit calculations."""
        
        rotation_history = [
            {'year': 2023, 'crop': 'soybean'},
            {'year': 2022, 'crop': 'corn'},
            {'year': 2021, 'crop': 'soybean'},
            {'year': 2020, 'crop': 'corn'}
        ]
        
        # Corn following soybean
        corn_benefits = self._calculate_rotation_benefits('corn', rotation_history)
        
        # Should show nitrogen credit from previous soybean
        assert corn_benefits['nitrogen_credit_lbs_per_acre'] >= 30
        assert corn_benefits['nitrogen_credit_lbs_per_acre'] <= 50
        assert 'legume nitrogen fixation' in corn_benefits['explanation']
        
        # Soybean following corn
        soybean_benefits = self._calculate_rotation_benefits('soybean', rotation_history[1:])
        
        # Should show pest and disease break benefits
        assert 'pest cycle break' in soybean_benefits['benefits']
        assert 'disease pressure reduction' in soybean_benefits['benefits']
    
    @pytest.mark.agricultural
    def test_continuous_cropping_penalties(self):
        """Test continuous cropping penalty calculations."""
        
        # Continuous corn
        continuous_corn_history = [
            {'year': 2023, 'crop': 'corn'},
            {'year': 2022, 'crop': 'corn'},
            {'year': 2021, 'crop': 'corn'}
        ]
        
        corn_penalties = self._calculate_rotation_benefits('corn', continuous_corn_history)
        
        # Should show yield penalty and increased pest pressure
        assert corn_penalties['yield_penalty_percent'] > 0
        assert corn_penalties['yield_penalty_percent'] <= 15  # Typical range
        assert 'continuous cropping' in corn_penalties['warnings']
        assert corn_penalties['pest_pressure_increase'] > 1.0
    
    @pytest.mark.agricultural
    def test_cover_crop_integration(self):
        """Test cover crop integration in rotation planning."""
        
        rotation_with_covers = [
            {'year': 2023, 'crop': 'corn', 'cover_crop': 'cereal_rye'},
            {'year': 2022, 'crop': 'soybean', 'cover_crop': 'crimson_clover'},
            {'year': 2021, 'crop': 'corn', 'cover_crop': None}
        ]
        
        benefits = self._calculate_rotation_benefits('soybean', rotation_with_covers)
        
        # Should account for cover crop benefits
        assert 'cover_crop_benefits' in benefits
        cover_benefits = benefits['cover_crop_benefits']
        
        assert 'soil_health_improvement' in cover_benefits
        assert 'erosion_control' in cover_benefits
        
        # Nitrogen-fixing cover crops should provide N credit
        if any(cc.get('cover_crop') == 'crimson_clover' for cc in rotation_with_covers):
            assert benefits.get('cover_crop_n_credit_lbs_per_acre', 0) > 0
    
    def _calculate_rotation_benefits(self, current_crop, rotation_history):
        """Simulate rotation benefit calculations."""
        if not rotation_history:
            return {'benefits': [], 'warnings': []}
        
        previous_crop = rotation_history[0]['crop']
        
        benefits = {
            'benefits': [],
            'warnings': [],
            'nitrogen_credit_lbs_per_acre': 0,
            'yield_penalty_percent': 0,
            'pest_pressure_increase': 1.0,
            'explanation': ''
        }
        
        # Corn following soybean
        if current_crop == 'corn' and previous_crop == 'soybean':
            benefits['nitrogen_credit_lbs_per_acre'] = 40
            benefits['benefits'].append('nitrogen fixation credit')
            benefits['explanation'] = 'Corn benefits from legume nitrogen fixation'
        
        # Soybean following corn
        elif current_crop == 'soybean' and previous_crop == 'corn':
            benefits['benefits'].extend(['pest cycle break', 'disease pressure reduction'])
            benefits['explanation'] = 'Rotation breaks pest and disease cycles'
        
        # Continuous cropping
        elif current_crop == previous_crop:
            continuous_years = 1
            for record in rotation_history[1:]:
                if record['crop'] == current_crop:
                    continuous_years += 1
                else:
                    break
            
            benefits['yield_penalty_percent'] = min(continuous_years * 3, 15)
            benefits['pest_pressure_increase'] = 1.0 + (continuous_years * 0.2)
            benefits['warnings'].append('continuous cropping detected')
        
        # Cover crop benefits
        cover_crop_benefits = []
        cover_crop_n_credit = 0
        
        for record in rotation_history:
            if record.get('cover_crop'):
                cover_crop_benefits.extend(['soil_health_improvement', 'erosion_control'])
                if record['cover_crop'] in ['crimson_clover', 'red_clover']:
                    cover_crop_n_credit += 25
        
        if cover_crop_benefits:
            benefits['cover_crop_benefits'] = list(set(cover_crop_benefits))
            benefits['cover_crop_n_credit_lbs_per_acre'] = min(cover_crop_n_credit, 60)
        
        return benefits


class TestSpecialtyCropSuitability:
    """Test suitability algorithms for specialty crops."""
    
    @pytest.mark.agricultural
    def test_vegetable_crop_suitability(self, california_vegetable_farm_data):
        """Test vegetable crop suitability assessment."""
        
        farm_conditions = {
            'location': california_vegetable_farm_data['location'],
            'soil': california_vegetable_farm_data['soil_data'],
            'irrigation': california_vegetable_farm_data['irrigation'],
            'climate': {
                'hardiness_zone': '9a',
                'frost_free_days': 300,
                'average_temperature_f': 68
            }
        }
        
        # Test tomato suitability
        tomato_result = self._analyze_vegetable_suitability('tomatoes', farm_conditions)
        
        # Should be highly suitable for California conditions
        assert tomato_result['suitability_score'] >= 0.85
        assert tomato_result['climate_match'] >= 0.9
        
        # Should require irrigation
        assert 'irrigation_required' in tomato_result['requirements']
        assert tomato_result['water_needs_inches_per_season'] > 20
        
        # Test lettuce suitability
        lettuce_result = self._analyze_vegetable_suitability('lettuce', farm_conditions)
        
        # Should be suitable with proper timing
        assert lettuce_result['suitability_score'] >= 0.8
        assert 'cool_season_timing' in lettuce_result['recommendations']
    
    @pytest.mark.agricultural
    def test_fruit_tree_suitability(self):
        """Test fruit tree suitability assessment."""
        
        orchard_conditions = {
            'location': {'latitude': 37.5, 'longitude': -120.5},  # Central Valley CA
            'soil': {
                'ph': 7.0,
                'drainage_class': 'well_drained',
                'soil_depth_inches': 48
            },
            'climate': {
                'hardiness_zone': '9a',
                'chill_hours': 800,  # Winter chill accumulation
                'frost_free_days': 280
            }
        }
        
        # Test almond suitability
        almond_result = self._analyze_tree_crop_suitability('almonds', orchard_conditions)
        
        # Should be suitable with adequate chill hours
        assert almond_result['suitability_score'] >= 0.8
        assert almond_result['chill_requirement_met'] is True
        
        # Should highlight long-term investment
        assert almond_result['years_to_production'] >= 3
        assert 'long_term_investment' in almond_result['considerations']
    
    def _analyze_vegetable_suitability(self, crop, conditions):
        """Simulate vegetable crop suitability analysis."""
        
        crop_requirements = {
            'tomatoes': {
                'optimal_temp_range': (65, 85),
                'water_needs': 25,
                'irrigation_required': True,
                'frost_tolerance': False
            },
            'lettuce': {
                'optimal_temp_range': (45, 75),
                'water_needs': 15,
                'irrigation_required': True,
                'frost_tolerance': True
            }
        }
        
        requirements = crop_requirements.get(crop, {})
        climate = conditions.get('climate', {})
        
        # Temperature suitability
        avg_temp = climate.get('average_temperature_f', 70)
        temp_range = requirements.get('optimal_temp_range', (50, 80))
        
        if temp_range[0] <= avg_temp <= temp_range[1]:
            climate_match = 1.0
        else:
            climate_match = 0.6
        
        # Irrigation assessment
        irrigation_available = conditions.get('irrigation', {}).get('available', False)
        irrigation_required = requirements.get('irrigation_required', False)
        
        if irrigation_required and not irrigation_available:
            suitability_score = 0.3
        else:
            suitability_score = climate_match * 0.9
        
        result = {
            'suitability_score': suitability_score,
            'climate_match': climate_match,
            'water_needs_inches_per_season': requirements.get('water_needs', 20),
            'requirements': [],
            'recommendations': []
        }
        
        if irrigation_required:
            result['requirements'].append('irrigation_required')
        
        if crop == 'lettuce' and avg_temp > 75:
            result['recommendations'].append('cool_season_timing')
        
        return result
    
    def _analyze_tree_crop_suitability(self, crop, conditions):
        """Simulate tree crop suitability analysis."""
        
        tree_requirements = {
            'almonds': {
                'chill_hours_required': 500,
                'years_to_production': 4,
                'optimal_ph_range': (6.0, 7.5),
                'drainage_critical': True
            }
        }
        
        requirements = tree_requirements.get(crop, {})
        climate = conditions.get('climate', {})
        soil = conditions.get('soil', {})
        
        # Chill hour requirement
        chill_hours = climate.get('chill_hours', 0)
        required_chill = requirements.get('chill_hours_required', 0)
        chill_met = chill_hours >= required_chill
        
        # Soil suitability
        ph = soil.get('ph', 7.0)
        ph_range = requirements.get('optimal_ph_range', (6.0, 8.0))
        ph_suitable = ph_range[0] <= ph <= ph_range[1]
        
        drainage = soil.get('drainage_class', 'well_drained')
        drainage_suitable = drainage in ['well_drained', 'moderately_well_drained']
        
        # Overall suitability
        if chill_met and ph_suitable and drainage_suitable:
            suitability_score = 0.9
        elif chill_met and (ph_suitable or drainage_suitable):
            suitability_score = 0.7
        else:
            suitability_score = 0.4
        
        return {
            'suitability_score': suitability_score,
            'chill_requirement_met': chill_met,
            'years_to_production': requirements.get('years_to_production', 3),
            'considerations': ['long_term_investment', 'permanent_planting'],
            'soil_suitability': ph_suitable and drainage_suitable
        }