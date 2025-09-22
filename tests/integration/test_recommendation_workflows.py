"""
Integration Tests for Recommendation Workflows

Tests complete end-to-end workflows for the AFAS system including
crop selection, fertilizer recommendations, and soil management.
"""

import pytest
import asyncio
import sys
import os
from datetime import date, datetime
from unittest.mock import patch, AsyncMock, MagicMock
import json

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services'))


class TestCropSelectionWorkflow:
    """Test complete crop selection workflow."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_crop_selection_workflow(self, iowa_corn_farm_data, mock_http_client):
        """Test end-to-end crop selection process."""
        
        # Mock external API responses
        mock_weather_response = {
            'current': {
                'temperature_f': 72.5,
                'humidity_percent': 65,
                'precipitation_inches': 0.0
            },
            'forecast': [
                {
                    'date': (date.today()).isoformat(),
                    'high_f': 75,
                    'low_f': 55,
                    'precipitation_chance': 20
                }
            ]
        }
        
        mock_soil_response = {
            'soil_series': 'Clarion',
            'drainage_class': 'well_drained',
            'typical_ph_range': {'min': 6.0, 'max': 7.5}
        }
        
        # Simulate complete workflow
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock()
            
            # Configure different responses for different APIs
            def side_effect(*args, **kwargs):
                url = args[0] if args else kwargs.get('url', '')
                if 'weather' in url:
                    mock_response.json.return_value = mock_weather_response
                elif 'soil' in url:
                    mock_response.json.return_value = mock_soil_response
                return mock_response
            
            mock_get.return_value.__aenter__.return_value = mock_response
            mock_response.json.side_effect = side_effect
            
            # Import and test the workflow
            from recommendation_engine.src.api.routes import generate_crop_recommendations
            
            request_data = {
                'farm_id': iowa_corn_farm_data['farm_id'],
                'location': iowa_corn_farm_data['location'],
                'soil_data': iowa_corn_farm_data['soil_data'],
                'climate_preferences': {
                    'drought_tolerance': 'medium',
                    'season_length': 'full_season'
                },
                'farm_constraints': {
                    'farm_size_acres': iowa_corn_farm_data['farm_size_acres'],
                    'available_equipment': ['planter', 'combine', 'sprayer'],
                    'irrigation_available': False
                }
            }
            
            # Execute workflow
            result = await generate_crop_recommendations(request_data)
            
            # Validate workflow results
            assert result is not None
            assert 'recommendations' in result
            assert result['confidence_score'] >= 0.7
            assert len(result['recommendations']) >= 2
            
            # Should recommend corn and soybean for Iowa
            crop_names = [rec['crop_name'] for rec in result['recommendations']]
            assert 'corn' in crop_names
            assert 'soybean' in crop_names
            
            # Each recommendation should have agricultural reasoning
            for rec in result['recommendations']:
                assert len(rec['explanation']) > 50
                assert 'soil' in rec['explanation'].lower()
                assert rec['confidence_factors']['soil_suitability'] > 0.7
    
    @pytest.mark.integration
    @pytest.mark.agricultural
    async def test_crop_selection_with_challenging_conditions(self, problematic_soil_data):
        """Test crop selection with challenging soil conditions."""
        
        request_data = {
            'farm_id': problematic_soil_data['farm_id'],
            'location': {'latitude': 42.0, 'longitude': -93.6},
            'soil_data': problematic_soil_data['soil_data'],
            'field_observations': problematic_soil_data['field_observations']
        }
        
        with patch('recommendation_engine.src.services.weather_service.WeatherService') as mock_weather:
            mock_weather.return_value.get_current_weather.return_value = {
                'temperature_f': 70.0,
                'precipitation_inches': 0.5  # Recent rain
            }
            
            from recommendation_engine.src.api.routes import generate_crop_recommendations
            
            result = await generate_crop_recommendations(request_data)
            
            # Should handle challenging conditions gracefully
            assert result is not None
            assert 'warnings' in result
            assert len(result['warnings']) > 0
            
            # Should recommend soil improvement practices
            assert any('soil improvement' in warning.lower() for warning in result['warnings'])
            
            # Confidence should be lower due to challenging conditions
            assert result['confidence_score'] < 0.8


class TestFertilizerRecommendationWorkflow:
    """Test fertilizer recommendation workflow."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_fertilizer_strategy_workflow(self, iowa_corn_farm_data):
        """Test complete fertilizer strategy workflow."""
        
        request_data = {
            'farm_id': iowa_corn_farm_data['farm_id'],
            'crop_plan': {
                'primary_crop': 'corn',
                'yield_goal_bu_per_acre': 180,
                'planted_acres': 250,
                'planting_date': date(2024, 5, 1)
            },
            'soil_data': iowa_corn_farm_data['soil_data'],
            'management_history': iowa_corn_farm_data['management_history'],
            'economic_constraints': {
                'fertilizer_budget_total': 18000.00,
                'current_prices': {
                    'urea_per_ton': 420.00,
                    'dap_per_ton': 580.00,
                    'potash_per_ton': 380.00,
                    'anhydrous_ammonia_per_ton': 520.00
                }
            },
            'market_conditions': {
                'corn_price_per_bushel': 4.25,
                'price_volatility': 'moderate'
            }
        }
        
        # Mock external price data
        with patch('data_integration.src.services.market_service.MarketService') as mock_market:
            mock_market.return_value.get_current_prices.return_value = {
                'corn': 4.25,
                'fertilizer_prices': request_data['economic_constraints']['current_prices']
            }
            
            from recommendation_engine.src.api.routes import generate_fertilizer_strategy
            
            result = await generate_fertilizer_strategy(request_data)
            
            # Validate economic optimization
            assert result['economic_analysis']['expected_roi_percent'] > 200
            assert result['fertilizer_strategy']['total_cost'] <= request_data['economic_constraints']['fertilizer_budget_total']
            
            # Validate agricultural accuracy
            n_program = result['fertilizer_strategy']['nitrogen_program']
            assert 120 <= n_program['total_n_rate_lbs_per_acre'] <= 180  # Reasonable N rate
            assert n_program['legume_credit_lbs_per_acre'] > 0  # Should account for previous soybean
            
            # Should include timing recommendations
            assert len(n_program['application_timing']) >= 2  # Split application
            
            # Validate cost calculations
            total_cost = sum([
                result['fertilizer_strategy']['nitrogen_program']['cost_per_acre'],
                result['fertilizer_strategy']['phosphorus_program']['cost_per_acre'],
                result['fertilizer_strategy']['potassium_program']['cost_per_acre']
            ])
            assert total_cost > 0
            assert total_cost < 200  # Reasonable per-acre cost
    
    @pytest.mark.integration
    @pytest.mark.agricultural
    async def test_fertilizer_workflow_with_manure(self, iowa_corn_farm_data):
        """Test fertilizer workflow with manure application."""
        
        request_data = {
            'farm_id': iowa_corn_farm_data['farm_id'],
            'crop_plan': {
                'primary_crop': 'corn',
                'yield_goal_bu_per_acre': 170
            },
            'soil_data': iowa_corn_farm_data['soil_data'],
            'manure_application': {
                'type': 'dairy_manure',
                'rate_tons_per_acre': 20,
                'application_date': date(2024, 3, 15),
                'analysis': {
                    'total_nitrogen_percent': 0.5,
                    'available_nitrogen_percent': 0.25,
                    'phosphorus_percent': 0.2,
                    'potassium_percent': 0.4
                }
            }
        }
        
        from recommendation_engine.src.api.routes import generate_fertilizer_strategy
        
        result = await generate_fertilizer_strategy(request_data)
        
        # Should account for manure nutrients
        n_program = result['fertilizer_strategy']['nitrogen_program']
        assert 'manure_n_credit_lbs_per_acre' in n_program
        assert n_program['manure_n_credit_lbs_per_acre'] > 0
        
        # Total fertilizer N should be reduced due to manure credit
        assert n_program['fertilizer_n_needed_lbs_per_acre'] < n_program['total_n_rate_lbs_per_acre']
        
        # Should include manure in reasoning
        assert 'manure' in result['reasoning'].lower()


class TestSoilManagementWorkflow:
    """Test soil management workflow."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_soil_health_assessment_workflow(self, problematic_soil_data):
        """Test complete soil health assessment and improvement workflow."""
        
        request_data = {
            'farm_id': problematic_soil_data['farm_id'],
            'soil_data': problematic_soil_data['soil_data'],
            'field_observations': problematic_soil_data['field_observations'],
            'management_goals': {
                'primary_goal': 'improve_soil_health',
                'timeline': '3_years',
                'budget_per_acre': 150.00
            },
            'current_practices': {
                'tillage_system': 'conventional',
                'cover_crops_used': False,
                'crop_rotation': ['corn', 'corn']  # Continuous corn
            }
        }
        
        from recommendation_engine.src.api.routes import generate_soil_management_plan
        
        result = await generate_soil_management_plan(request_data)
        
        # Should provide comprehensive soil health assessment
        assert 'soil_health_assessment' in result
        assert result['soil_health_assessment']['current_score'] < 6.0  # Poor soil
        assert len(result['soil_health_assessment']['limiting_factors']) >= 2
        
        # Should recommend multiple improvement practices
        assert 'recommendations' in result
        assert len(result['recommendations']) >= 3
        
        # Should include lime application for acidic soil
        lime_rec = next((rec for rec in result['recommendations'] 
                        if rec['practice'] == 'lime_application'), None)
        assert lime_rec is not None
        assert lime_rec['priority'] == 'high'
        assert lime_rec['details']['rate_tons_per_acre'] > 0
        
        # Should recommend organic matter improvement
        om_rec = next((rec for rec in result['recommendations'] 
                      if 'organic_matter' in rec['practice']), None)
        assert om_rec is not None
        
        # Should include implementation timeline
        assert 'implementation_timeline' in result
        assert 'year_1' in result['implementation_timeline']
        
        # Should provide expected outcomes
        assert 'expected_outcomes' in result
        assert result['expected_outcomes']['soil_ph_target'] > result['soil_data']['ph']
    
    @pytest.mark.integration
    @pytest.mark.agricultural
    async def test_lime_requirement_calculation_workflow(self):
        """Test lime requirement calculation workflow."""
        
        acidic_soil_data = {
            'farm_id': 'test_acidic_farm',
            'soil_data': {
                'ph': 5.2,  # Acidic
                'soil_texture': 'silt_loam',
                'organic_matter_percent': 3.0,
                'buffer_ph': 6.8,  # SMP buffer pH
                'test_date': date(2024, 3, 15)
            },
            'target_crops': ['corn', 'soybean'],
            'target_ph': 6.5
        }
        
        from recommendation_engine.src.api.routes import calculate_lime_requirement
        
        result = await calculate_lime_requirement(acidic_soil_data)
        
        # Should calculate appropriate lime rate
        assert 'lime_recommendation' in result
        lime_rec = result['lime_recommendation']
        
        assert lime_rec['lime_needed_tons_per_acre'] > 0
        assert lime_rec['lime_needed_tons_per_acre'] <= 5.0  # Reasonable range
        assert lime_rec['expected_ph_change'] > 0
        
        # Should specify lime type and application timing
        assert 'lime_type' in lime_rec
        assert 'application_timing' in lime_rec
        assert 'incorporation_required' in lime_rec
        
        # Should provide cost estimate
        assert 'cost_estimate_per_acre' in lime_rec
        assert lime_rec['cost_estimate_per_acre'] > 0


class TestCrossServiceIntegration:
    """Test integration between multiple services."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_weather_soil_crop_integration(self, iowa_corn_farm_data, sample_weather_data):
        """Test integration between weather, soil, and crop services."""
        
        # Mock weather service
        with patch('data_integration.src.services.weather_service.WeatherService') as mock_weather:
            mock_weather.return_value.get_current_weather.return_value = sample_weather_data['current']
            mock_weather.return_value.get_forecast.return_value = sample_weather_data['forecast']
            
            # Mock soil service
            with patch('data_integration.src.services.soil_service.SoilDataService') as mock_soil:
                mock_soil.return_value.get_soil_survey_data.return_value = {
                    'soil_series': 'Clarion',
                    'drainage_class': 'well_drained'
                }
                
                request_data = {
                    'farm_id': iowa_corn_farm_data['farm_id'],
                    'location': iowa_corn_farm_data['location'],
                    'soil_data': iowa_corn_farm_data['soil_data']
                }
                
                from recommendation_engine.src.api.routes import generate_integrated_recommendations
                
                result = await generate_integrated_recommendations(request_data)
                
                # Should integrate data from multiple sources
                assert 'weather_context' in result
                assert 'soil_context' in result
                assert 'crop_recommendations' in result
                
                # Weather should influence recommendations
                weather_context = result['weather_context']
                assert 'current_conditions' in weather_context
                assert 'forecast_summary' in weather_context
                
                # Should provide integrated advice
                assert 'integrated_advice' in result
                advice = result['integrated_advice']
                assert len(advice) > 0
                
                # Advice should consider multiple factors
                advice_text = ' '.join(advice).lower()
                assert 'weather' in advice_text or 'soil' in advice_text
    
    @pytest.mark.integration
    @pytest.mark.performance
    async def test_workflow_performance(self, iowa_corn_farm_data, performance_timer):
        """Test workflow performance requirements."""
        
        request_data = {
            'farm_id': iowa_corn_farm_data['farm_id'],
            'location': iowa_corn_farm_data['location'],
            'soil_data': iowa_corn_farm_data['soil_data']
        }
        
        # Mock external services for consistent timing
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={'mocked': True})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            from recommendation_engine.src.api.routes import generate_crop_recommendations
            
            performance_timer.start()
            result = await generate_crop_recommendations(request_data)
            performance_timer.stop()
            
            # Should complete within 3 seconds
            assert performance_timer.elapsed < 3.0
            
            # Should still provide quality results despite time constraint
            assert result is not None
            assert result['confidence_score'] >= 0.7
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_handling_and_fallbacks(self, iowa_corn_farm_data):
        """Test error handling and fallback mechanisms."""
        
        request_data = {
            'farm_id': iowa_corn_farm_data['farm_id'],
            'location': iowa_corn_farm_data['location'],
            'soil_data': iowa_corn_farm_data['soil_data']
        }
        
        # Simulate external service failures
        with patch('data_integration.src.services.weather_service.WeatherService') as mock_weather:
            mock_weather.return_value.get_current_weather.side_effect = Exception("Weather API Error")
            
            with patch('data_integration.src.services.soil_service.SoilDataService') as mock_soil:
                mock_soil.return_value.get_soil_survey_data.side_effect = Exception("Soil API Error")
                
                from recommendation_engine.src.api.routes import generate_crop_recommendations
                
                result = await generate_crop_recommendations(request_data)
                
                # Should handle errors gracefully
                assert result is not None
                
                # Should indicate reduced confidence due to missing data
                assert result['confidence_score'] < 0.8
                
                # Should include warnings about missing data
                assert 'warnings' in result
                assert len(result['warnings']) > 0
                
                # Should still provide basic recommendations based on soil data
                assert 'recommendations' in result
                assert len(result['recommendations']) > 0


class TestDataConsistencyAndValidation:
    """Test data consistency and validation across services."""
    
    @pytest.mark.integration
    @pytest.mark.agricultural
    async def test_agricultural_data_consistency(self, iowa_corn_farm_data):
        """Test consistency of agricultural data across services."""
        
        # Test that soil pH is consistently interpreted
        soil_data = iowa_corn_farm_data['soil_data']
        
        from recommendation_engine.src.services.soil_management_service import SoilManagementService
        from recommendation_engine.src.services.crop_recommendation_service import CropRecommendationService
        
        soil_service = SoilManagementService()
        crop_service = CropRecommendationService()
        
        # Both services should interpret pH consistently
        soil_assessment = soil_service.assess_soil_ph(soil_data['ph'])
        crop_suitability = crop_service.evaluate_ph_suitability('corn', soil_data['ph'])
        
        # pH interpretations should be consistent
        if soil_assessment['status'] == 'optimal':
            assert crop_suitability['ph_suitability'] >= 0.8
        elif soil_assessment['status'] == 'acidic':
            assert crop_suitability['ph_suitability'] < 0.8
            assert 'acidic' in crop_suitability['limitations']
    
    @pytest.mark.integration
    @pytest.mark.agricultural
    async def test_unit_consistency_across_services(self):
        """Test that units are consistent across all services."""
        
        # Test nitrogen rate units
        from recommendation_engine.src.services.fertilizer_recommendation_service import FertilizerRecommendationService
        from recommendation_engine.src.services.crop_recommendation_service import CropRecommendationService
        
        fertilizer_service = FertilizerRecommendationService()
        crop_service = CropRecommendationService()
        
        # Both should use lbs/acre for nitrogen
        n_rec = fertilizer_service.calculate_nitrogen_rate({
            'crop_type': 'corn',
            'yield_goal': 180,
            'soil_data': {'organic_matter_percent': 3.5}
        })
        
        crop_rec = crop_service.get_nitrogen_requirements('corn', 180)
        
        # Units should be consistent
        assert 'lbs_per_acre' in n_rec['units'] or 'lbs/acre' in str(n_rec)
        assert 'lbs_per_acre' in crop_rec['units'] or 'lbs/acre' in str(crop_rec)
        
        # Values should be in reasonable range
        assert 80 <= n_rec['total_n_rate_lbs_per_acre'] <= 220
        assert 80 <= crop_rec['nitrogen_requirement_lbs_per_acre'] <= 220