"""
API Integration Tests for Fertilizer Optimization

Tests end-to-end API workflows for the fertilizer optimization system.
"""

import pytest
import sys
import os
from datetime import date

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services'))

# Assuming Flask app for testing; adjust import based on actual app structure
try:
    from app import app  # Replace with actual app import if different
except ImportError:
    # Fallback if app is not directly importable
    from services.fertilizer_application.src.api.app import app


class TestOptimizationWorkflow:
    """Test end-to-end optimization workflow."""

    @pytest.mark.integration
    def test_end_to_end_optimization(self):
        """Test complete optimization workflow: POST /optimize -> verify response -> check reasonableness."""
        with app.test_client() as client:
            # Sample data for fertilizer optimization
            data = {
                'farm_id': 'test_farm_001',
                'crop_plan': {
                    'primary_crop': 'corn',
                    'yield_goal_bu_per_acre': 180,
                    'planted_acres': 250,
                    'planting_date': date(2024, 5, 1).isoformat()
                },
                'soil_data': {
                    'ph': 6.5,
                    'organic_matter_percent': 3.0,
                    'phosphorus_ppm': 25,
                    'potassium_ppm': 150,
                    'nitrogen_lbs_per_acre': 50
                },
                'management_history': {
                    'previous_crop': 'soybean',
                    'tillage_system': 'conventional',
                    'fertilizer_history': {
                        'last_year_n_rate': 140,
                        'last_year_p_rate': 40,
                        'last_year_k_rate': 80
                    }
                },
                'economic_constraints': {
                    'fertilizer_budget_total': 18000.00,
                    'current_prices': {
                        'urea_per_ton': 420.00,
                        'dap_per_ton': 580.00,
                        'potash_per_ton': 380.00
                    }
                },
                'market_conditions': {
                    'corn_price_per_bushel': 4.25,
                    'price_volatility': 'moderate'
                }
            }

            # Send POST request to /optimize
            response = client.post('/optimize', json=data)

            # Verify response status
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Parse response
            result = response.get_json()
            assert result is not None, "Response should contain JSON data"

            # Verify response structure
            assert 'fertilizer_strategy' in result, "Response should include 'fertilizer_strategy'"
            assert 'economic_analysis' in result, "Response should include 'economic_analysis'"
            assert 'recommendations' in result, "Response should include 'recommendations'"

            # Check fertilizer strategy details
            strategy = result['fertilizer_strategy']
            assert 'nitrogen_program' in strategy, "Should include nitrogen program"
            assert 'phosphorus_program' in strategy, "Should include phosphorus program"
            assert 'potassium_program' in strategy, "Should include potassium program"

            # Verify nitrogen program
            n_program = strategy['nitrogen_program']
            assert 'total_n_rate_lbs_per_acre' in n_program, "Should specify total N rate"
            assert 100 <= n_program['total_n_rate_lbs_per_acre'] <= 200, "N rate should be reasonable for corn"
            assert 'application_timing' in n_program, "Should include application timing"
            assert len(n_program['application_timing']) >= 1, "Should have at least one application timing"

            # Verify phosphorus and potassium programs
            p_program = strategy['phosphorus_program']
            assert 'total_p_rate_lbs_per_acre' in p_program, "Should specify total P rate"
            assert p_program['total_p_rate_lbs_per_acre'] >= 0, "P rate should be non-negative"

            k_program = strategy['potassium_program']
            assert 'total_k_rate_lbs_per_acre' in k_program, "Should specify total K rate"
            assert k_program['total_k_rate_lbs_per_acre'] >= 0, "K rate should be non-negative"

            # Check economic analysis
            economic = result['economic_analysis']
            assert 'expected_roi_percent' in economic, "Should include ROI calculation"
            assert economic['expected_roi_percent'] > 0, "ROI should be positive"
            assert 'total_cost' in economic, "Should include total cost"
            assert economic['total_cost'] <= data['economic_constraints']['fertilizer_budget_total'], "Cost should not exceed budget"

            # Verify recommendations list
            recommendations = result['recommendations']
            assert isinstance(recommendations, list), "Recommendations should be a list"
            assert len(recommendations) > 0, "Should have at least one recommendation"

            for rec in recommendations:
                assert 'fertilizer_type' in rec, "Each recommendation should specify fertilizer type"
                assert 'amount' in rec, "Each recommendation should specify amount"
                assert rec['amount'] > 0, "Fertilizer amount should be positive"
                assert 'timing' in rec, "Each recommendation should specify timing"
                assert 'reasoning' in rec, "Each recommendation should include reasoning"
                assert len(rec['reasoning']) > 20, "Reasoning should be detailed"

            # Additional reasonableness checks
            # Total cost per acre should be reasonable
            total_cost_per_acre = economic['total_cost'] / data['crop_plan']['planted_acres']
            assert 50 <= total_cost_per_acre <= 300, "Cost per acre should be in reasonable range"

            # Ensure no negative values in key metrics
            assert strategy['total_cost'] >= 0, "Total strategy cost should be non-negative"
            assert n_program['total_n_rate_lbs_per_acre'] >= 0, "N rate should be non-negative"
            assert p_program['total_p_rate_lbs_per_acre'] >= 0, "P rate should be non-negative"
            assert k_program['total_k_rate_lbs_per_acre'] >= 0, "K rate should be non-negative"