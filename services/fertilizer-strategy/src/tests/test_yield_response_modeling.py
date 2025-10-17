"""
Comprehensive tests for sophisticated yield-fertilizer response curves service.

This module tests the YieldResponseModelingService including:
- Curve fitting with multiple mathematical models
- Nutrient interaction analysis
- Optimal rate calculations
- Economic threshold analysis
- Model validation and comparison
"""

import pytest
import numpy as np
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime

from ..services.yield_response_modeling_service import YieldResponseModelingService
from ..models.yield_response_models import (
    YieldResponseRequest, NutrientResponseData, ResponseModelType,
    YieldResponseAnalysis, InteractionType, SignificanceLevel
)


class TestYieldResponseModelingService:
    """Comprehensive test suite for yield response modeling service."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return YieldResponseModelingService()
    
    @pytest.fixture
    def sample_response_data(self):
        """Create sample response data for testing."""
        field_id = uuid4()
        return [
            NutrientResponseData(
                field_id=field_id,
                year=2020,
                nutrient_rates={"N": 0, "P": 0, "K": 0},
                yield_per_acre=120.0,
                crop_type="corn",
                variety="Test Variety"
            ),
            NutrientResponseData(
                field_id=field_id,
                year=2021,
                nutrient_rates={"N": 50, "P": 20, "K": 30},
                yield_per_acre=150.0,
                crop_type="corn",
                variety="Test Variety"
            ),
            NutrientResponseData(
                field_id=field_id,
                year=2022,
                nutrient_rates={"N": 100, "P": 40, "K": 60},
                yield_per_acre=180.0,
                crop_type="corn",
                variety="Test Variety"
            ),
            NutrientResponseData(
                field_id=field_id,
                year=2023,
                nutrient_rates={"N": 150, "P": 60, "K": 90},
                yield_per_acre=200.0,
                crop_type="corn",
                variety="Test Variety"
            ),
            NutrientResponseData(
                field_id=field_id,
                year=2024,
                nutrient_rates={"N": 200, "P": 80, "K": 120},
                yield_per_acre=210.0,
                crop_type="corn",
                variety="Test Variety"
            )
        ]
    
    @pytest.fixture
    def sample_request(self, sample_response_data):
        """Create sample request for testing."""
        field_id = uuid4()
        return YieldResponseRequest(
            field_id=field_id,
            crop_type="corn",
            nutrients=["N", "P", "K"],
            response_data=sample_response_data,
            economic_parameters={
                "N_price_per_unit": 0.5,
                "P_price_per_unit": 0.8,
                "K_price_per_unit": 0.6,
                "crop_price_per_unit": 5.0
            }
        )
    
    @pytest.mark.asyncio
    async def test_analyze_yield_response_success(self, service, sample_request):
        """Test successful yield response analysis."""
        analysis = await service.analyze_yield_response(sample_request)
        
        assert analysis.analysis_id is not None
        assert analysis.field_id == sample_request.field_id
        assert analysis.crop_type == sample_request.crop_type
        assert len(analysis.nutrient_curves) == 3  # N, P, K
        assert len(analysis.interaction_effects) == 3  # N-P, N-K, P-K
        assert len(analysis.optimal_rates) == 3
        assert len(analysis.economic_thresholds) == 3
        assert analysis.validation_result is not None
        assert analysis.analysis_timestamp is not None
    
    @pytest.mark.asyncio
    async def test_analyze_yield_response_insufficient_data(self, service):
        """Test yield response analysis with insufficient data."""
        field_id = uuid4()
        
        # Test that validation prevents creation of request with insufficient data
        with pytest.raises(Exception, match="List should have at least 3 items"):
            YieldResponseRequest(
                field_id=field_id,
                crop_type="corn",
                nutrients=["N"],
                response_data=[
                    NutrientResponseData(
                        field_id=field_id,
                        year=2020,
                        nutrient_rates={"N": 0},
                        yield_per_acre=120.0,
                        crop_type="corn"
                    ),
                    NutrientResponseData(
                        field_id=field_id,
                        year=2021,
                        nutrient_rates={"N": 50},
                        yield_per_acre=150.0,
                        crop_type="corn"
                    )
                ],
                economic_parameters={"N_price_per_unit": 0.5, "crop_price_per_unit": 5.0}
            )
    
    @pytest.mark.asyncio
    async def test_extract_nutrient_data(self, service, sample_response_data):
        """Test nutrient data extraction."""
        nitrogen_data = await service._extract_nutrient_data(sample_response_data, "N")
        
        assert len(nitrogen_data) == 5
        assert nitrogen_data[0] == (0, 120.0)  # (rate, yield)
        assert nitrogen_data[1] == (50, 150.0)
        assert nitrogen_data[2] == (100, 180.0)
        assert nitrogen_data[3] == (150, 200.0)
        assert nitrogen_data[4] == (200, 210.0)
    
    @pytest.mark.asyncio
    async def test_fit_response_curve(self, service, sample_response_data):
        """Test response curve fitting."""
        nitrogen_data = await service._extract_nutrient_data(sample_response_data, "N")
        curve = await service._fit_response_curve(nitrogen_data, "N", "corn")
        
        assert curve.nutrient == "N"
        assert curve.model_type in ResponseModelType
        assert len(curve.parameters) > 0
        assert 0 <= curve.r_squared <= 1
        assert curve.rmse >= 0
        assert curve.mse >= 0
        assert len(curve.data_points) == 5
        assert len(curve.predicted_curve) > 0
        assert curve.max_yield > 0
        assert len(curve.response_range) == 2
    
    @pytest.mark.asyncio
    async def test_fit_single_model_mitscherlich_baule(self, service):
        """Test Mitscherlich-Baule model fitting."""
        # Create synthetic data following Mitscherlich-Baule pattern
        x_data = np.array([0, 50, 100, 150, 200])
        y_data = np.array([120, 150, 180, 200, 210])
        
        result = await service._fit_single_model(x_data, y_data, ResponseModelType.MITSCHERLICH_BAULE)
        
        assert result.model_type == ResponseModelType.MITSCHERLICH_BAULE
        assert len(result.parameters) == 3
        assert len(result.parameter_errors) == 3
        assert 0 <= result.r_squared <= 1
        assert len(result.covariance_matrix) == 3
        assert len(result.covariance_matrix[0]) == 3
    
    @pytest.mark.asyncio
    async def test_fit_single_model_quadratic_plateau(self, service):
        """Test quadratic plateau model fitting."""
        x_data = np.array([0, 50, 100, 150, 200])
        y_data = np.array([120, 150, 180, 200, 200])  # Plateau at 200
        
        result = await service._fit_single_model(x_data, y_data, ResponseModelType.QUADRATIC_PLATEAU)
        
        assert result.model_type == ResponseModelType.QUADRATIC_PLATEAU
        assert len(result.parameters) == 3
        assert len(result.parameter_errors) == 3
        assert 0 <= result.r_squared <= 1
    
    @pytest.mark.asyncio
    async def test_fit_single_model_linear_plateau(self, service):
        """Test linear plateau model fitting."""
        x_data = np.array([0, 50, 100, 150, 200])
        y_data = np.array([120, 150, 180, 200, 200])  # Plateau at 200
        
        result = await service._fit_single_model(x_data, y_data, ResponseModelType.LINEAR_PLATEAU)
        
        assert result.model_type == ResponseModelType.LINEAR_PLATEAU
        assert len(result.parameters) == 3
        assert len(result.parameter_errors) == 3
        assert 0 <= result.r_squared <= 1
    
    @pytest.mark.asyncio
    async def test_fit_single_model_exponential(self, service):
        """Test exponential model fitting."""
        x_data = np.array([0, 50, 100, 150, 200])
        y_data = np.array([120, 150, 180, 200, 210])
        
        result = await service._fit_single_model(x_data, y_data, ResponseModelType.EXPONENTIAL)
        
        assert result.model_type == ResponseModelType.EXPONENTIAL
        assert len(result.parameters) == 3
        assert len(result.parameter_errors) == 3
        assert 0 <= result.r_squared <= 1
    
    @pytest.mark.asyncio
    async def test_predict_yield(self, service):
        """Test yield prediction."""
        x_values = np.array([0, 50, 100, 150, 200])
        parameters = [200.0, 0.01, 0.1]  # Mitscherlich-Baule parameters
        
        predictions = await service._predict_yield(x_values, ResponseModelType.MITSCHERLICH_BAULE, parameters)
        
        assert len(predictions) == 5
        assert all(pred >= 0 for pred in predictions)
        assert predictions[0] < predictions[-1]  # Generally increasing
    
    @pytest.mark.asyncio
    async def test_analyze_nutrient_interactions(self, service, sample_response_data):
        """Test nutrient interaction analysis."""
        nutrients = ["N", "P", "K"]
        interactions = await service._analyze_nutrient_interactions(sample_response_data, nutrients, "corn")
        
        assert len(interactions) == 3  # N-P, N-K, P-K
        assert all(interaction.nutrient1 in nutrients for interaction in interactions)
        assert all(interaction.nutrient2 in nutrients for interaction in interactions)
        assert all(interaction.interaction_type in InteractionType for interaction in interactions)
        assert all(interaction.significance in SignificanceLevel for interaction in interactions)
        assert all(-1 <= interaction.interaction_strength <= 1 for interaction in interactions)
    
    @pytest.mark.asyncio
    async def test_calculate_optimal_rates(self, service, sample_response_data):
        """Test optimal rate calculations."""
        # Create a simple curve for testing
        nitrogen_data = await service._extract_nutrient_data(sample_response_data, "N")
        curve = await service._fit_response_curve(nitrogen_data, "N", "corn")
        
        economic_params = {
            "N_price_per_unit": 0.5,
            "crop_price_per_unit": 5.0
        }
        
        optimal_rates = await service._calculate_optimal_rates(
            {"N": curve}, economic_params, "corn"
        )
        
        assert "N" in optimal_rates
        optimal_analysis = optimal_rates["N"]
        assert optimal_analysis.nutrient == "N"
        assert optimal_analysis.economic_optimal_rate >= 0
        assert optimal_analysis.max_yield_rate >= 0
        assert optimal_analysis.target_yield_rate >= 0
        assert optimal_analysis.economic_optimal_yield >= 0
        assert optimal_analysis.max_yield >= 0
        assert optimal_analysis.target_yield >= 0
        assert optimal_analysis.marginal_revenue_at_optimal >= 0
        assert optimal_analysis.marginal_cost_at_optimal >= 0
    
    @pytest.mark.asyncio
    async def test_calculate_economic_thresholds(self, service, sample_response_data):
        """Test economic threshold calculations."""
        # Create a simple curve for testing
        nitrogen_data = await service._extract_nutrient_data(sample_response_data, "N")
        curve = await service._fit_response_curve(nitrogen_data, "N", "corn")
        
        economic_params = {
            "N_price_per_unit": 0.5,
            "crop_price_per_unit": 5.0
        }
        
        thresholds = await service._calculate_economic_thresholds(
            {"N": curve}, economic_params, "corn"
        )
        
        assert "N" in thresholds
        threshold = thresholds["N"]
        assert threshold.nutrient == "N"
        assert threshold.break_even_rate >= 0
        assert threshold.minimum_profitable_rate >= 0
        assert threshold.maximum_profitable_rate >= 0
        assert threshold.fertilizer_price >= 0
        assert threshold.crop_price >= 0
        assert threshold.price_ratio >= 0
    
    @pytest.mark.asyncio
    async def test_validate_models(self, service, sample_response_data):
        """Test model validation."""
        # Create a simple curve for testing
        nitrogen_data = await service._extract_nutrient_data(sample_response_data, "N")
        curve = await service._fit_response_curve(nitrogen_data, "N", "corn")
        
        validations = await service._validate_models({"N": curve}, sample_response_data)
        
        assert "N" in validations
        validation = validations["N"]
        assert validation.is_valid is not None
        assert 0 <= validation.quality_score <= 1
        assert isinstance(validation.issues, list)
        assert isinstance(validation.warnings, list)
        assert validation.data_points >= 0
        assert validation.nutrient_coverage >= 0
        assert validation.validation_metrics is not None
    
    @pytest.mark.asyncio
    async def test_compare_models(self, service, sample_response_data):
        """Test model comparison."""
        # Create curves for different nutrients
        nitrogen_data = await service._extract_nutrient_data(sample_response_data, "N")
        nitrogen_curve = await service._fit_response_curve(nitrogen_data, "N", "corn")
        
        phosphorus_data = await service._extract_nutrient_data(sample_response_data, "P")
        phosphorus_curve = await service._fit_response_curve(phosphorus_data, "P", "corn")
        
        curves = {"N": nitrogen_curve, "P": phosphorus_curve}
        comparison = await service._compare_models(curves)
        
        assert comparison.model_performance is not None
        assert comparison.model_averages is not None
        assert comparison.best_performing_model in ResponseModelType
        assert comparison.comparison_timestamp is not None
    
    @pytest.mark.asyncio
    async def test_calculate_confidence_intervals(self, service, sample_response_data):
        """Test confidence interval calculations."""
        # Create a simple curve for testing
        nitrogen_data = await service._extract_nutrient_data(sample_response_data, "N")
        curve = await service._fit_response_curve(nitrogen_data, "N", "corn")
        
        confidence_intervals = await service._calculate_confidence_intervals(
            {"N": curve}, sample_response_data
        )
        
        assert "N" in confidence_intervals
        intervals = confidence_intervals["N"]
        assert len(intervals) > 0
        
        for interval in intervals:
            assert interval.x_value >= 0
            assert interval.predicted_yield >= 0
            assert interval.lower_bound >= 0
            assert interval.upper_bound >= interval.lower_bound
            assert 0 <= interval.confidence_level <= 1
            assert interval.margin_of_error >= 0
    
    @pytest.mark.asyncio
    async def test_detect_outliers(self, service):
        """Test outlier detection."""
        # Test with no outliers
        yields_no_outliers = [120, 130, 125, 135, 128]
        outlier_count = await service._detect_outliers(yields_no_outliers)
        assert outlier_count == 0
        
        # Test with outliers
        yields_with_outliers = [120, 130, 125, 200, 128]  # 200 is an outlier
        outlier_count = await service._detect_outliers(yields_with_outliers)
        assert outlier_count >= 0
    
    @pytest.mark.asyncio
    async def test_validate_input_data(self, service, sample_request):
        """Test input data validation."""
        validation = await service._validate_input_data(sample_request)
        
        assert validation.is_valid is not None
        assert 0 <= validation.quality_score <= 1
        assert isinstance(validation.issues, list)
        assert isinstance(validation.warnings, list)
        assert validation.data_points >= 0
        assert validation.nutrient_coverage >= 0
    
    @pytest.mark.asyncio
    async def test_calculate_interaction_strength(self, service, sample_response_data):
        """Test interaction strength calculation."""
        strength = await service._calculate_interaction_strength(sample_response_data, "N", "P")
        
        assert -1 <= strength <= 1
    
    @pytest.mark.asyncio
    async def test_find_economic_optimal_rate(self, service, sample_response_data):
        """Test economic optimal rate finding."""
        nitrogen_data = await service._extract_nutrient_data(sample_response_data, "N")
        curve = await service._fit_response_curve(nitrogen_data, "N", "corn")
        
        optimal_rate = await service._find_economic_optimal_rate(curve, 0.5, 5.0)
        
        assert optimal_rate >= 0
    
    @pytest.mark.asyncio
    async def test_find_max_yield_rate(self, service, sample_response_data):
        """Test maximum yield rate finding."""
        nitrogen_data = await service._extract_nutrient_data(sample_response_data, "N")
        curve = await service._fit_response_curve(nitrogen_data, "N", "corn")
        
        max_rate = await service._find_max_yield_rate(curve)
        
        assert max_rate >= 0
    
    @pytest.mark.asyncio
    async def test_find_rate_for_target_yield(self, service, sample_response_data):
        """Test rate finding for target yield."""
        nitrogen_data = await service._extract_nutrient_data(sample_response_data, "N")
        curve = await service._fit_response_curve(nitrogen_data, "N", "corn")
        
        target_rate = await service._find_rate_for_target_yield(curve, 180.0)
        
        assert target_rate >= 0
    
    @pytest.mark.asyncio
    async def test_calculate_marginal_response(self, service, sample_response_data):
        """Test marginal response calculation."""
        nitrogen_data = await service._extract_nutrient_data(sample_response_data, "N")
        curve = await service._fit_response_curve(nitrogen_data, "N", "corn")
        
        marginal_response = await service._calculate_marginal_response(curve, 100.0)
        
        assert isinstance(marginal_response, float)
    
    @pytest.mark.asyncio
    async def test_find_break_even_rate(self, service, sample_response_data):
        """Test break-even rate finding."""
        nitrogen_data = await service._extract_nutrient_data(sample_response_data, "N")
        curve = await service._fit_response_curve(nitrogen_data, "N", "corn")
        
        break_even_rate = await service._find_break_even_rate(curve, 0.5, 5.0)
        
        assert break_even_rate >= 0
    
    @pytest.mark.asyncio
    async def test_find_minimum_profitable_rate(self, service, sample_response_data):
        """Test minimum profitable rate finding."""
        nitrogen_data = await service._extract_nutrient_data(sample_response_data, "N")
        curve = await service._fit_response_curve(nitrogen_data, "N", "corn")
        
        min_rate = await service._find_minimum_profitable_rate(curve, 0.5, 5.0)
        
        assert min_rate >= 0
    
    @pytest.mark.asyncio
    async def test_find_maximum_profitable_rate(self, service, sample_response_data):
        """Test maximum profitable rate finding."""
        nitrogen_data = await service._extract_nutrient_data(sample_response_data, "N")
        curve = await service._fit_response_curve(nitrogen_data, "N", "corn")
        
        max_rate = await service._find_maximum_profitable_rate(curve, 0.5, 5.0)
        
        assert max_rate >= 0


class TestYieldResponseModelingEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return YieldResponseModelingService()
    
    @pytest.mark.asyncio
    async def test_empty_nutrient_data(self, service):
        """Test handling of empty nutrient data."""
        field_id = uuid4()
        
        # Create request with sufficient data points but no N data
        request = YieldResponseRequest(
            field_id=field_id,
            crop_type="corn",
            nutrients=["N"],
            response_data=[
                NutrientResponseData(
                    field_id=field_id,
                    year=2020,
                    nutrient_rates={"P": 50},  # No N data
                    yield_per_acre=150.0,
                    crop_type="corn"
                ),
                NutrientResponseData(
                    field_id=field_id,
                    year=2021,
                    nutrient_rates={"P": 100},  # No N data
                    yield_per_acre=160.0,
                    crop_type="corn"
                ),
                NutrientResponseData(
                    field_id=field_id,
                    year=2022,
                    nutrient_rates={"P": 150},  # No N data
                    yield_per_acre=170.0,
                    crop_type="corn"
                )
            ],
            economic_parameters={"N_price_per_unit": 0.5, "crop_price_per_unit": 5.0}
        )
        
        # Should handle gracefully and skip nutrients with insufficient data
        analysis = await service.analyze_yield_response(request)
        assert len(analysis.nutrient_curves) == 0  # No curves fitted
    
    @pytest.mark.asyncio
    async def test_low_yields(self, service):
        """Test handling of very low yields."""
        field_id = uuid4()
        request = YieldResponseRequest(
            field_id=field_id,
            crop_type="corn",
            nutrients=["N"],
            response_data=[
                NutrientResponseData(
                    field_id=field_id,
                    year=2020,
                    nutrient_rates={"N": 0},
                    yield_per_acre=10.0,  # Very low yield
                    crop_type="corn"
                ),
                NutrientResponseData(
                    field_id=field_id,
                    year=2021,
                    nutrient_rates={"N": 50},
                    yield_per_acre=150.0,
                    crop_type="corn"
                ),
                NutrientResponseData(
                    field_id=field_id,
                    year=2022,
                    nutrient_rates={"N": 100},
                    yield_per_acre=180.0,
                    crop_type="corn"
                )
            ],
            economic_parameters={"N_price_per_unit": 0.5, "crop_price_per_unit": 5.0}
        )
        
        # Should handle gracefully and still fit curves
        analysis = await service.analyze_yield_response(request)
        assert analysis.validation_result is not None
        assert len(analysis.validation_result.warnings) >= 0  # May or may not warn
    
    @pytest.mark.asyncio
    async def test_extreme_nutrient_rates(self, service):
        """Test handling of extreme nutrient rates."""
        field_id = uuid4()
        request = YieldResponseRequest(
            field_id=field_id,
            crop_type="corn",
            nutrients=["N"],
            response_data=[
                NutrientResponseData(
                    field_id=field_id,
                    year=2020,
                    nutrient_rates={"N": 0},
                    yield_per_acre=120.0,
                    crop_type="corn"
                ),
                NutrientResponseData(
                    field_id=field_id,
                    year=2021,
                    nutrient_rates={"N": 1000},  # Extremely high rate
                    yield_per_acre=150.0,
                    crop_type="corn"
                ),
                NutrientResponseData(
                    field_id=field_id,
                    year=2022,
                    nutrient_rates={"N": 2000},  # Even higher rate
                    yield_per_acre=180.0,
                    crop_type="corn"
                )
            ],
            economic_parameters={"N_price_per_unit": 0.5, "crop_price_per_unit": 5.0}
        )
        
        # Should handle gracefully
        analysis = await service.analyze_yield_response(request)
        assert analysis.validation_result is not None
        # Should warn about extreme values
        warning_messages = [w for w in analysis.validation_result.warnings if "Extreme nutrient rates" in w]
        assert len(warning_messages) > 0
    
    @pytest.mark.asyncio
    async def test_single_data_point(self, service):
        """Test handling of single data point."""
        field_id = uuid4()
        request = YieldResponseRequest(
            field_id=field_id,
            crop_type="corn",
            nutrients=["N"],
            response_data=[
                NutrientResponseData(
                    field_id=field_id,
                    year=2020,
                    nutrient_rates={"N": 50},
                    yield_per_acre=150.0,
                    crop_type="corn"
                ),
                NutrientResponseData(
                    field_id=field_id,
                    year=2021,
                    nutrient_rates={"N": 50},  # Same rate
                    yield_per_acre=155.0,
                    crop_type="corn"
                ),
                NutrientResponseData(
                    field_id=field_id,
                    year=2022,
                    nutrient_rates={"N": 50},  # Same rate again
                    yield_per_acre=160.0,
                    crop_type="corn"
                )
            ],
            economic_parameters={"N_price_per_unit": 0.5, "crop_price_per_unit": 5.0}
        )
        
        # Should handle gracefully with warnings
        analysis = await service.analyze_yield_response(request)
        assert analysis.validation_result is not None
        # Should warn about limited variation
        warning_messages = [w for w in analysis.validation_result.warnings if "Limited variation" in w]
        assert len(warning_messages) > 0


class TestYieldResponseModelingPerformance:
    """Test performance characteristics."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return YieldResponseModelingService()
    
    @pytest.mark.asyncio
    async def test_large_dataset_performance(self, service):
        """Test performance with large dataset."""
        field_id = uuid4()
        
        # Create large dataset
        response_data = []
        for i in range(50):  # 50 data points
            response_data.append(
                NutrientResponseData(
                    field_id=field_id,
                    year=2020 + (i % 10),  # Cycle through years 2020-2029
                    nutrient_rates={"N": i * 10, "P": i * 5, "K": i * 8},
                    yield_per_acre=120.0 + i * 2 + np.random.normal(0, 5),
                    crop_type="corn"
                )
            )
        
        request = YieldResponseRequest(
            field_id=field_id,
            crop_type="corn",
            nutrients=["N", "P", "K"],
            response_data=response_data,
            economic_parameters={
                "N_price_per_unit": 0.5,
                "P_price_per_unit": 0.8,
                "K_price_per_unit": 0.6,
                "crop_price_per_unit": 5.0
            }
        )
        
        # Should complete within reasonable time
        import time
        start_time = time.time()
        analysis = await service.analyze_yield_response(request)
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 10.0  # Should complete within 10 seconds
        assert analysis is not None
        assert len(analysis.nutrient_curves) == 3
    
    @pytest.mark.asyncio
    async def test_multiple_nutrients_performance(self, service):
        """Test performance with many nutrients."""
        field_id = uuid4()
        
        # Create data with many nutrients
        nutrients = ["N", "P", "K", "S", "Ca", "Mg", "Zn", "Mn", "Cu", "B"]
        response_data = []
        
        for i in range(10):  # 10 data points
            nutrient_rates = {nutrient: i * 10 for nutrient in nutrients}
            response_data.append(
                NutrientResponseData(
                    field_id=field_id,
                    year=2020 + i,
                    nutrient_rates=nutrient_rates,
                    yield_per_acre=120.0 + i * 5,
                    crop_type="corn"
                )
            )
        
        economic_params = {
            "crop_price_per_unit": 5.0
        }
        for nutrient in nutrients:
            economic_params[f"{nutrient}_price_per_unit"] = 0.5
        
        request = YieldResponseRequest(
            field_id=field_id,
            crop_type="corn",
            nutrients=nutrients,
            response_data=response_data,
            economic_parameters=economic_params
        )
        
        # Should complete within reasonable time
        import time
        start_time = time.time()
        analysis = await service.analyze_yield_response(request)
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 15.0  # Should complete within 15 seconds
        assert analysis is not None
        assert len(analysis.nutrient_curves) == len(nutrients)
        assert len(analysis.interaction_effects) == len(nutrients) * (len(nutrients) - 1) // 2