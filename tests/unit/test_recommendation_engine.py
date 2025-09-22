"""
Unit Tests for Recommendation Engine Core Logic

Tests the core recommendation engine functionality including
agricultural calculations, confidence scoring, and decision logic.
"""

import pytest
import sys
import os
from datetime import date, datetime
from unittest.mock import MagicMock, patch, AsyncMock

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'recommendation-engine', 'src'))

from services.recommendation_engine import RecommendationEngine
from services.crop_recommendation_service import CropRecommendationService
from services.fertilizer_recommendation_service import FertilizerRecommendationService
from services.soil_management_service import SoilManagementService
from models.agricultural_models import SoilData, CropRecommendation, FertilizerRecommendation


class TestRecommendationEngine:
    """Test the main recommendation engine orchestration."""
    
    @pytest.fixture
    def recommendation_engine(self):
        """Create recommendation engine instance."""
        return RecommendationEngine()
    
    @pytest.mark.unit
    async def test_generate_crop_recommendations(self, recommendation_engine, iowa_corn_farm_data):
        """Test crop recommendation generation."""
        request_data = {
            'farm_id': iowa_corn_farm_data['farm_id'],
            'location': iowa_corn_farm_data['location'],
            'soil_data': iowa_corn_farm_data['soil_data'],
            'farm_constraints': {
                'farm_size_acres': iowa_corn_farm_data['farm_size_acres'],
                'available_equipment': ['planter', 'combine', 'sprayer'],
                'irrigation_available': False
            }
        }
        
        with patch.object(recommendation_engine, 'crop_service') as mock_crop_service:
            mock_crop_service.get_crop_recommendations.return_value = {
                'recommendations': [
                    {
                        'crop_name': 'corn',
                        'suitability_score': 0.89,
                        'confidence_factors': {
                            'soil_suitability': 0.95,
                            'climate_match': 0.88,
                            'economic_viability': 0.85
                        }
                    }
                ],
                'confidence_score': 0.87
            }
            
            result = await recommendation_engine.generate_crop_recommendations(request_data)
            
            assert result is not None
            assert 'recommendations' in result
            assert result['confidence_score'] >= 0.8
            assert len(result['recommendations']) > 0
            
            # Validate agricultural accuracy
            corn_rec = next((r for r in result['recommendations'] if r['crop_name'] == 'corn'), None)
            assert corn_rec is not None
            assert corn_rec['suitability_score'] > 0.8
    
    @pytest.mark.unit
    async def test_generate_fertilizer_recommendations(self, recommendation_engine, iowa_corn_farm_data):
        """Test fertilizer recommendation generation."""
        request_data = {
            'farm_id': iowa_corn_farm_data['farm_id'],
            'crop_plan': {
                'primary_crop': 'corn',
                'yield_goal_bu_per_acre': 180,
                'planted_acres': 250
            },
            'soil_data': iowa_corn_farm_data['soil_data'],
            'economic_constraints': {
                'fertilizer_budget_total': 18000.00,
                'current_prices': {
                    'urea_per_ton': 420.00,
                    'dap_per_ton': 580.00,
                    'potash_per_ton': 380.00
                }
            }
        }
        
        with patch.object(recommendation_engine, 'fertilizer_service') as mock_fertilizer_service:
            mock_fertilizer_service.calculate_fertilizer_strategy.return_value = {
                'nitrogen_program': {
                    'total_n_rate_lbs_per_acre': 160,
                    'legume_credit_lbs_per_acre': 40,
                    'fertilizer_n_needed_lbs_per_acre': 120
                },
                'economic_analysis': {
                    'expected_roi_percent': 285,
                    'total_cost_per_acre': 93.70
                },
                'confidence_score': 0.85
            }
            
            result = await recommendation_engine.generate_fertilizer_recommendations(request_data)
            
            assert result is not None
            assert 'nitrogen_program' in result
            assert result['confidence_score'] >= 0.8
            
            # Validate agricultural accuracy
            n_program = result['nitrogen_program']
            assert 80 <= n_program['total_n_rate_lbs_per_acre'] <= 220  # Reasonable N rate for corn
            assert n_program['legume_credit_lbs_per_acre'] > 0  # Should have soybean credit
    
    @pytest.mark.unit
    async def test_confidence_score_calculation(self, recommendation_engine):
        """Test confidence score calculation logic."""
        factors = {
            'data_quality': 0.9,
            'regional_applicability': 0.8,
            'agricultural_accuracy': 0.95,
            'economic_viability': 0.75
        }
        
        confidence = recommendation_engine._calculate_confidence_score(factors)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence >= 0.8  # Should be high with good factors
    
    @pytest.mark.unit
    async def test_low_confidence_handling(self, recommendation_engine, problematic_soil_data):
        """Test handling of low confidence scenarios."""
        request_data = {
            'farm_id': problematic_soil_data['farm_id'],
            'soil_data': problematic_soil_data['soil_data']
        }
        
        with patch.object(recommendation_engine, 'crop_service') as mock_crop_service:
            mock_crop_service.get_crop_recommendations.return_value = {
                'recommendations': [],
                'confidence_score': 0.45,  # Low confidence
                'warnings': ['Extreme soil conditions detected']
            }
            
            result = await recommendation_engine.generate_crop_recommendations(request_data)
            
            assert result['confidence_score'] < 0.7
            assert 'warnings' in result
            assert len(result['warnings']) > 0


class TestCropRecommendationService:
    """Test crop recommendation service logic."""
    
    @pytest.fixture
    def crop_service(self):
        """Create crop recommendation service."""
        return CropRecommendationService()
    
    @pytest.mark.unit
    @pytest.mark.agricultural
    def test_corn_suitability_iowa_conditions(self, crop_service, iowa_corn_farm_data):
        """Test corn suitability for Iowa conditions."""
        farm_conditions = {
            'location': iowa_corn_farm_data['location'],
            'soil': iowa_corn_farm_data['soil_data'],
            'farm_size_acres': iowa_corn_farm_data['farm_size_acres']
        }
        
        result = crop_service.analyze_crop_suitability('corn', farm_conditions)
        
        # Corn should be highly suitable for Iowa conditions
        assert result['suitability_score'] >= 0.85
        assert result['climate_match'] >= 0.9
        assert result['soil_suitability'] >= 0.8
        assert 'well-suited' in result['explanation'].lower()
    
    @pytest.mark.unit
    @pytest.mark.agricultural
    def test_crop_selection_ranking(self, crop_service):
        """Test crop selection ranking logic."""
        farm_conditions = {
            'location': {'latitude': 40.5, 'longitude': -89.4},  # Illinois
            'soil': {
                'ph': 6.2,
                'organic_matter_percent': 3.8,
                'phosphorus_ppm': 25,
                'potassium_ppm': 180
            },
            'preferences': {
                'crop_types': ['grain_crops'],
                'risk_tolerance': 'moderate'
            }
        }
        
        recommendations = crop_service.get_crop_recommendations(farm_conditions)
        
        # Should recommend corn and soybean for Illinois
        crop_names = [rec['crop_name'] for rec in recommendations[:3]]
        assert 'corn' in crop_names
        assert 'soybean' in crop_names
        
        # Recommendations should be sorted by suitability score
        scores = [rec['suitability_score'] for rec in recommendations]
        assert scores == sorted(scores, reverse=True)
        
        # Each recommendation should have required fields
        for rec in recommendations:
            assert 'explanation' in rec
            assert 'confidence_factors' in rec
            assert rec['suitability_score'] >= 0.0
    
    @pytest.mark.unit
    @pytest.mark.agricultural
    def test_unsuitable_crop_filtering(self, crop_service, problematic_soil_data):
        """Test filtering of unsuitable crops."""
        farm_conditions = {
            'soil': problematic_soil_data['soil_data'],
            'location': {'latitude': 42.0, 'longitude': -93.6}
        }
        
        recommendations = crop_service.get_crop_recommendations(farm_conditions)
        
        # Should filter out crops unsuitable for poor soil conditions
        for rec in recommendations:
            assert rec['suitability_score'] >= 0.3  # Minimum threshold
            assert 'soil_limitations' in rec.get('warnings', []) or rec['suitability_score'] >= 0.6


class TestFertilizerRecommendationService:
    """Test fertilizer recommendation service logic."""
    
    @pytest.fixture
    def fertilizer_service(self):
        """Create fertilizer recommendation service."""
        return FertilizerRecommendationService()
    
    @pytest.mark.unit
    @pytest.mark.agricultural
    def test_nitrogen_rate_calculation_iowa_corn(self, fertilizer_service, iowa_corn_farm_data, agricultural_validator):
        """Test nitrogen rate calculation for Iowa corn."""
        crop_data = {
            'crop_type': 'corn',
            'yield_goal': 180,
            'soil_data': iowa_corn_farm_data['soil_data'],
            'management_history': iowa_corn_farm_data['management_history']
        }
        
        result = fertilizer_service.calculate_nitrogen_rate(crop_data)
        
        # Validate agricultural accuracy
        assert agricultural_validator.validate_nutrient_rate(
            result['total_n_rate_lbs_per_acre'], 'nitrogen', 'corn'
        )
        assert result['legume_credit_lbs_per_acre'] > 0  # Should have soybean credit
        assert result['confidence_score'] >= 0.8
        assert 'legume credit' in result['reasoning'].lower()
    
    @pytest.mark.unit
    @pytest.mark.agricultural
    def test_phosphorus_buildup_vs_maintenance(self, fertilizer_service):
        """Test phosphorus buildup vs maintenance recommendations."""
        # Low P scenario - should recommend buildup
        low_p_data = {
            'crop_type': 'corn',
            'yield_goal': 175,
            'soil_data': {
                'phosphorus_ppm': 8,  # Low P
                'soil_texture': 'silt_loam'
            }
        }
        
        low_p_result = fertilizer_service.calculate_phosphorus_rate(low_p_data)
        assert low_p_result['recommendation_type'] == 'buildup'
        assert low_p_result['rate_lbs_p2o5_per_acre'] > 40
        
        # Adequate P scenario - should recommend maintenance
        adequate_p_data = {
            'crop_type': 'corn',
            'yield_goal': 175,
            'soil_data': {
                'phosphorus_ppm': 25,  # Adequate P
                'soil_texture': 'silt_loam'
            }
        }
        
        adequate_p_result = fertilizer_service.calculate_phosphorus_rate(adequate_p_data)
        assert adequate_p_result['recommendation_type'] == 'maintenance'
        assert 20 <= adequate_p_result['rate_lbs_p2o5_per_acre'] <= 40
    
    @pytest.mark.unit
    @pytest.mark.agricultural
    def test_economic_optimization(self, fertilizer_service):
        """Test economic optimization in fertilizer recommendations."""
        scenario = {
            'crop_type': 'corn',
            'yield_goal': 180,
            'planted_acres': 250,
            'soil_data': {'ph': 6.2, 'organic_matter_percent': 3.5},
            'economic_constraints': {
                'fertilizer_budget_total': 15000.00,
                'current_prices': {
                    'urea_per_ton': 420.00,
                    'dap_per_ton': 580.00,
                    'potash_per_ton': 380.00
                }
            },
            'market_conditions': {
                'corn_price_per_bushel': 4.25
            }
        }
        
        result = fertilizer_service.calculate_fertilizer_strategy(scenario)
        
        # Should optimize for economic return
        assert result['economic_analysis']['expected_roi_percent'] > 200
        assert result['fertilizer_strategy']['total_cost'] <= scenario['economic_constraints']['fertilizer_budget_total']
        assert 'economic_optimization' in result['reasoning'].lower()
    
    @pytest.mark.unit
    @pytest.mark.agricultural
    def test_manure_credit_calculation(self, fertilizer_service):
        """Test manure nitrogen credit calculation."""
        scenario = {
            'crop_type': 'corn',
            'yield_goal': 170,
            'soil_data': {'organic_matter_percent': 4.2},
            'manure_application': {
                'type': 'dairy_manure',
                'rate_tons_per_acre': 20,
                'application_date': date(2024, 3, 15),
                'analysis': {
                    'total_nitrogen_percent': 0.5,
                    'available_nitrogen_percent': 0.25
                }
            }
        }
        
        result = fertilizer_service.calculate_nitrogen_rate(scenario)
        
        # Expected manure N credit: 20 tons * 0.25% available N * 20 lbs/ton = 100 lbs N/acre
        expected_credit = 100
        assert abs(result['manure_n_credit_lbs_per_acre'] - expected_credit) <= 10
        assert 'manure nitrogen credit' in result['reasoning'].lower()


class TestSoilManagementService:
    """Test soil management service logic."""
    
    @pytest.fixture
    def soil_service(self):
        """Create soil management service."""
        return SoilManagementService()
    
    @pytest.mark.unit
    @pytest.mark.agricultural
    def test_soil_health_score_calculation(self, soil_service, iowa_corn_farm_data):
        """Test soil health score calculation."""
        soil_data = iowa_corn_farm_data['soil_data']
        
        result = soil_service.calculate_soil_health_score(soil_data)
        
        # Good soil conditions should score 7-8 out of 10
        assert 7.0 <= result['overall_score'] <= 8.5
        assert result['ph_score'] >= 8.0  # Optimal pH
        assert result['organic_matter_score'] >= 7.0  # Good OM level
        assert len(result['improvement_recommendations']) <= 2
    
    @pytest.mark.unit
    @pytest.mark.agricultural
    def test_soil_health_improvement_recommendations(self, soil_service, problematic_soil_data):
        """Test soil health improvement recommendations."""
        soil_data = problematic_soil_data['soil_data']
        
        result = soil_service.calculate_soil_health_score(soil_data)
        
        # Poor soil should have low score and multiple recommendations
        assert result['overall_score'] <= 5.0
        assert len(result['improvement_recommendations']) >= 3
        
        # Should recommend lime for pH
        lime_rec = next((rec for rec in result['improvement_recommendations'] 
                        if rec['practice'] == 'lime_application'), None)
        assert lime_rec is not None
        assert lime_rec['priority'] == 'high'
    
    @pytest.mark.unit
    @pytest.mark.agricultural
    def test_lime_requirement_calculation(self, soil_service):
        """Test lime requirement calculation."""
        soil_data = {
            'ph': 5.2,  # Acidic
            'soil_texture': 'silt_loam',
            'organic_matter_percent': 3.0,
            'target_ph': 6.5
        }
        
        result = soil_service.calculate_lime_requirement(soil_data)
        
        # Should recommend lime for acidic soil
        assert result['lime_needed_tons_per_acre'] > 0
        assert result['lime_needed_tons_per_acre'] <= 5.0  # Reasonable range
        assert result['expected_ph_change'] > 0
        assert 'agricultural_limestone' in result['lime_type'].lower()
    
    @pytest.mark.unit
    @pytest.mark.agricultural
    def test_organic_matter_improvement_strategies(self, soil_service):
        """Test organic matter improvement strategies."""
        soil_data = {
            'organic_matter_percent': 1.8,  # Low OM
            'soil_texture': 'silt_loam',
            'tillage_system': 'conventional'
        }
        
        result = soil_service.get_organic_matter_improvement_strategies(soil_data)
        
        # Should recommend multiple strategies for low OM
        assert len(result['strategies']) >= 2
        
        strategy_types = [s['practice'] for s in result['strategies']]
        assert 'cover_crops' in strategy_types
        assert 'reduced_tillage' in strategy_types or 'no_till' in strategy_types
        
        # Each strategy should have implementation details
        for strategy in result['strategies']:
            assert 'implementation_steps' in strategy
            assert 'expected_improvement' in strategy
            assert strategy['priority'] in ['high', 'medium', 'low']