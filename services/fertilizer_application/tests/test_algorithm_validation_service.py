"""
Comprehensive tests for Algorithm Validation Service.

This test suite covers:
- Cross-validation functionality
- Statistical validation
- Performance validation
- Field validation
- Expert validation
- Outcome validation
- Performance tracking
- Improvement recommendations
- Integration with sophisticated method selection service
"""

import pytest
import asyncio
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

from src.services.algorithm_validation_service import (
    AlgorithmValidationService, ValidationType, ValidationStatus,
    ValidationResult, PerformanceMetrics, ImprovementRecommendation
)
from src.services.sophisticated_method_selection_service import (
    SophisticatedMethodSelectionService, OptimizationResult, OptimizationObjective
)
from src.models.application_models import (
    ApplicationRequest, FieldConditions, CropRequirements, FertilizerSpecification,
    ApplicationMethodType, FertilizerForm, EquipmentType, EquipmentSpecification
)


class TestAlgorithmValidationService:
    """Test suite for AlgorithmValidationService."""
    
    @pytest.fixture
    def validation_service(self):
        """Create validation service instance."""
        return AlgorithmValidationService()
    
    @pytest.fixture
    def sample_test_data(self):
        """Create sample test data for validation."""
        return [
            {
                'field_size_acres': 100.0,
                'soil_type_encoded': 1,
                'drainage_class_encoded': 1,
                'slope_percent': 2.0,
                'irrigation_available': True,
                'crop_type_encoded': 1,
                'growth_stage_encoded': 1,
                'target_yield': 180.0,
                'fertilizer_type_encoded': 1,
                'fertilizer_form_encoded': 1,
                'equipment_count': 2,
                'equipment_types_encoded': 1,
                'weather_conditions_encoded': 0,
                'historical_success_rate': 0.8,
                'optimal_method_encoded': 1,
                'predicted_method': 'broadcast',
                'actual_method': 'broadcast',
                'efficiency_score': 0.75,
                'cost_per_acre': 25.0,
                'method_type_encoded': 1
            },
            {
                'field_size_acres': 200.0,
                'soil_type_encoded': 2,
                'drainage_class_encoded': 2,
                'slope_percent': 5.0,
                'irrigation_available': False,
                'crop_type_encoded': 2,
                'growth_stage_encoded': 2,
                'target_yield': 50.0,
                'fertilizer_type_encoded': 1,
                'fertilizer_form_encoded': 2,
                'equipment_count': 1,
                'equipment_types_encoded': 2,
                'weather_conditions_encoded': 0,
                'historical_success_rate': 0.85,
                'optimal_method_encoded': 2,
                'predicted_method': 'band',
                'actual_method': 'band',
                'efficiency_score': 0.80,
                'cost_per_acre': 30.0,
                'method_type_encoded': 2
            }
        ]
    
    @pytest.fixture
    def sample_application_request(self):
        """Create sample application request."""
        return ApplicationRequest(
            field_conditions=FieldConditions(
                field_size_acres=150.0,
                soil_type='loam',
                drainage_class='well',
                slope_percent=3.0,
                irrigation_available=True
            ),
            crop_requirements=CropRequirements(
                crop_type='corn',
                growth_stage='V8',
                target_yield=200.0
            ),
            fertilizer_specification=FertilizerSpecification(
                fertilizer_type='NPK',
                form=FertilizerForm.GRANULAR,
                npk_ratio='20-20-20'
            ),
            available_equipment=[
                EquipmentSpecification(
                    equipment_type=EquipmentType.SPREADER,
                    capacity_tons=5.0,
                    efficiency_rating=0.8
                )
            ]
        )
    
    @pytest.fixture
    def sample_optimization_result(self):
        """Create sample optimization result."""
        return OptimizationResult(
            optimal_method=ApplicationMethodType.BROADCAST,
            objective_value=0.85,
            confidence_score=0.90,
            alternative_solutions=[
                (ApplicationMethodType.BAND, 0.80),
                (ApplicationMethodType.SIDEDRESS, 0.75)
            ],
            optimization_time_ms=150.0,
            algorithm_used="Machine Learning (Random Forest + Neural Network)",
            convergence_info={"ml_models_used": ["efficiency_rf", "cost_rf"]}
        )
    
    @pytest.mark.asyncio
    async def test_comprehensive_validation_success(self, validation_service, sample_test_data):
        """Test comprehensive validation with successful results."""
        validation_types = [
            ValidationType.CROSS_VALIDATION,
            ValidationType.STATISTICAL_VALIDATION,
            ValidationType.PERFORMANCE_VALIDATION
        ]
        
        results = await validation_service.validate_algorithm_comprehensive(
            "test_algorithm",
            sample_test_data,
            validation_types
        )
        
        assert len(results) == 3
        assert all(isinstance(result, ValidationResult) for result in results)
        assert all(result.algorithm_name == "test_algorithm" for result in results)
        assert all(result.validation_id is not None for result in results)
        assert all(result.timestamp is not None for result in results)
    
    @pytest.mark.asyncio
    async def test_cross_validation(self, validation_service, sample_test_data):
        """Test cross-validation functionality."""
        # Mock cross-validation scores directly
        mock_scores = np.array([0.8, 0.85, 0.82, 0.88, 0.83])
        
        with patch('sklearn.model_selection.cross_val_score', return_value=mock_scores):
            with patch('sklearn.model_selection.train_test_split') as mock_split:
                with patch('sklearn.metrics.accuracy_score', return_value=0.836):
                    # Mock train_test_split to return consistent arrays
                    mock_split.return_value = (
                        np.array([[100.0, 1, 1, 2.0, True, 1, 1, 180.0, 1, 1, 2, 1, 0, 0.8]]),
                        np.array([[200.0, 2, 2, 5.0, False, 2, 2, 50.0, 1, 2, 1, 2, 0, 0.85]]),
                        np.array([1]),
                        np.array([2])
                    )
                    
                    result = await validation_service._cross_validation("test_algorithm", sample_test_data)
                
                assert result.validation_type == ValidationType.CROSS_VALIDATION
                assert result.algorithm_name == "test_algorithm"
                # Check that the result has the expected structure
                assert result.score >= 0.0
                assert result.score <= 1.0
                assert result.confidence_interval[0] <= result.confidence_interval[1]
                assert 'mean_accuracy' in result.metrics
                assert 'std_accuracy' in result.metrics
    
    @pytest.mark.asyncio
    async def test_statistical_validation(self, validation_service, sample_test_data):
        """Test statistical validation functionality."""
        result = await validation_service._statistical_validation("test_algorithm", sample_test_data)
        
        assert result.validation_type == ValidationType.STATISTICAL_VALIDATION
        assert result.algorithm_name == "test_algorithm"
        assert result.score >= 0.0
        assert result.score <= 1.0
        assert 'accuracy' in result.metrics
        assert 'precision' in result.metrics
        assert 'recall' in result.metrics
        assert 'f1_score' in result.metrics
        assert result.confidence_interval[0] < result.confidence_interval[1]
    
    @pytest.mark.asyncio
    async def test_performance_validation(self, validation_service, sample_test_data):
        """Test performance validation functionality."""
        with patch.object(validation_service.sophisticated_service, 'select_optimal_method_sophisticated') as mock_select:
            # Mock optimization result
            mock_result = OptimizationResult(
                optimal_method=ApplicationMethodType.BROADCAST,
                objective_value=0.85,
                confidence_score=0.90,
                alternative_solutions=[],
                optimization_time_ms=100.0,
                algorithm_used="test",
                convergence_info={}
            )
            mock_select.return_value = mock_result
            
            result = await validation_service._performance_validation("test_algorithm", sample_test_data)
            
            assert result.validation_type == ValidationType.PERFORMANCE_VALIDATION
            assert result.algorithm_name == "test_algorithm"
            assert result.metrics['avg_response_time_ms'] > 0
            assert result.metrics['samples_tested'] > 0
            assert result.confidence_interval[0] <= result.confidence_interval[1]
    
    @pytest.mark.asyncio
    async def test_field_validation(self, validation_service, sample_test_data):
        """Test field validation functionality."""
        result = await validation_service._field_validation("test_algorithm", sample_test_data)
        
        assert result.validation_type == ValidationType.FIELD_VALIDATION
        assert result.algorithm_name == "test_algorithm"
        assert result.score >= 0.0
        assert result.score <= 1.0
        assert 'avg_field_score' in result.metrics
        assert 'data_quality_scores' in result.metrics
        assert 'samples_validated' in result.metrics
    
    @pytest.mark.asyncio
    async def test_expert_validation(self, validation_service, sample_test_data):
        """Test expert validation functionality."""
        result = await validation_service._expert_validation("test_algorithm", sample_test_data)
        
        assert result.validation_type == ValidationType.EXPERT_VALIDATION
        assert result.algorithm_name == "test_algorithm"
        assert result.score >= 0.0
        assert result.score <= 1.0
        assert 'avg_expert_score' in result.metrics
        assert 'expert_scores' in result.metrics
        assert 'samples_reviewed' in result.metrics
    
    @pytest.mark.asyncio
    async def test_outcome_validation(self, validation_service, sample_test_data):
        """Test outcome validation functionality."""
        result = await validation_service._outcome_validation("test_algorithm", sample_test_data)
        
        assert result.validation_type == ValidationType.OUTCOME_VALIDATION
        assert result.algorithm_name == "test_algorithm"
        assert result.score >= 0.0
        assert result.score <= 1.0
        assert 'avg_outcome_score' in result.metrics
        assert 'outcome_scores' in result.metrics
        assert 'samples_tracked' in result.metrics
    
    @pytest.mark.asyncio
    async def test_track_performance_metrics(self, validation_service, sample_application_request, sample_optimization_result):
        """Test performance metrics tracking."""
        user_feedback = {"satisfaction_score": 4.5}
        
        metrics = await validation_service.track_performance_metrics(
            "test_algorithm",
            sample_application_request,
            sample_optimization_result,
            user_feedback
        )
        
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.algorithm_name == "test_algorithm"
        assert metrics.accuracy_score == sample_optimization_result.confidence_score
        assert metrics.response_time_ms == sample_optimization_result.optimization_time_ms
        assert metrics.user_satisfaction_score == 4.5
        assert metrics.timestamp is not None
        assert len(validation_service.performance_history) > 0
    
    @pytest.mark.asyncio
    async def test_generate_improvement_recommendations(self, validation_service):
        """Test improvement recommendations generation."""
        # Create mock validation results
        validation_results = [
            ValidationResult(
                validation_id="test_id_1",
                validation_type=ValidationType.CROSS_VALIDATION,
                algorithm_name="test_algorithm",
                status=ValidationStatus.FAILED,
                score=0.65,  # Below threshold
                confidence_interval=(0.60, 0.70),
                metrics={"mean_accuracy": 0.65},
                recommendations=["Accuracy below threshold"],
                validation_time_ms=100.0,
                timestamp=datetime.utcnow(),
                details={}
            )
        ]
        
        # Create mock performance history
        performance_history = [
            PerformanceMetrics(
                algorithm_name="test_algorithm",
                accuracy_score=0.70,
                precision_score=0.70,
                recall_score=0.70,
                f1_score=0.70,
                response_time_ms=2500.0,  # Above threshold
                throughput_per_second=0.4,
                error_rate=0.30,
                user_satisfaction_score=3.5,
                timestamp=datetime.utcnow(),
                sample_size=1
            )
        ]
        
        recommendations = await validation_service.generate_improvement_recommendations(
            "test_algorithm",
            validation_results,
            performance_history
        )
        
        assert len(recommendations) > 0
        assert all(isinstance(rec, ImprovementRecommendation) for rec in recommendations)
        assert all(rec.algorithm_name == "test_algorithm" for rec in recommendations)
        
        # Check for specific recommendations based on failed validations
        recommendation_types = [rec.improvement_type for rec in recommendations]
        assert "Model Training" in recommendation_types or "Performance Optimization" in recommendation_types
    
    @pytest.mark.asyncio
    async def test_implement_algorithm_improvement(self, validation_service):
        """Test algorithm improvement implementation."""
        recommendation = ImprovementRecommendation(
            recommendation_id="test_rec_id",
            algorithm_name="test_algorithm",
            improvement_type="Model Training",
            priority="High",
            description="Test improvement",
            expected_impact=0.15,
            implementation_effort="Medium",
            validation_required=True,
            timestamp=datetime.utcnow()
        )
        
        validation_service.improvement_recommendations.append(recommendation)
        
        with patch.object(validation_service.sophisticated_service, 'train_ml_models') as mock_train:
            mock_train.return_value = {"status": "success"}
            
            result = await validation_service.implement_algorithm_improvement(recommendation)
            
            assert result['recommendation_id'] == "test_rec_id"
            assert result['algorithm_name'] == "test_algorithm"
            assert result['implementation_status'] == 'completed'
            assert 'timestamp' in result
    
    @pytest.mark.asyncio
    async def test_get_validation_summary(self, validation_service):
        """Test validation summary retrieval."""
        # Add some mock data
        validation_service.validation_results.extend([
            ValidationResult(
                validation_id="test_id_1",
                validation_type=ValidationType.CROSS_VALIDATION,
                algorithm_name="test_algorithm",
                status=ValidationStatus.PASSED,
                score=0.85,
                confidence_interval=(0.80, 0.90),
                metrics={"mean_accuracy": 0.85},
                recommendations=[],
                validation_time_ms=100.0,
                timestamp=datetime.utcnow(),
                details={}
            )
        ])
        
        validation_service.performance_history.extend([
            PerformanceMetrics(
                algorithm_name="test_algorithm",
                accuracy_score=0.85,
                precision_score=0.85,
                recall_score=0.85,
                f1_score=0.85,
                response_time_ms=150.0,
                throughput_per_second=6.67,
                error_rate=0.15,
                user_satisfaction_score=4.5,
                timestamp=datetime.utcnow(),
                sample_size=1
            )
        ])
        
        summary = await validation_service.get_validation_summary("test_algorithm", 30)
        
        assert summary['algorithm_name'] == "test_algorithm"
        assert summary['period_days'] == 30
        assert summary['total_validations'] >= 1
        assert summary['total_performance_records'] >= 1
        assert summary['avg_validation_score'] > 0
        assert summary['avg_accuracy'] > 0
        assert summary['avg_response_time_ms'] > 0
        assert 'timestamp' in summary
    
    def test_data_quality_assessment(self, validation_service):
        """Test data quality assessment functionality."""
        # Test with good data
        good_data = {
            'field_size_acres': 100.0,
            'soil_type': 'loam',
            'crop_type': 'corn',
            'fertilizer_type': 'NPK'
        }
        
        quality_score = validation_service._assess_data_quality(good_data)
        assert 0.0 <= quality_score <= 1.0
        assert quality_score > 0.5  # Should be reasonably high for good data
        
        # Test with poor data
        poor_data = {
            'field_size_acres': None,
            'soil_type': None,
            'crop_type': '',
            'fertilizer_type': None
        }
        
        poor_quality_score = validation_service._assess_data_quality(poor_data)
        assert poor_quality_score < quality_score
    
    def test_agricultural_soundness_assessment(self, validation_service):
        """Test agricultural soundness assessment."""
        # Test with reasonable agricultural data
        sound_data = {
            'field_size_acres': 100.0,
            'target_yield': 180.0,
            'soil_type': 'loam'
        }
        
        soundness_score = validation_service._assess_agricultural_soundness(sound_data)
        assert 0.0 <= soundness_score <= 1.0
        assert soundness_score > 0.5  # Should be reasonably high for sound data
        
        # Test with unreasonable data
        unsound_data = {
            'field_size_acres': 50000.0,  # Unreasonably large
            'target_yield': 1000.0,      # Unreasonably high
            'soil_type': 'invalid_type'   # Invalid soil type
        }
        
        unsound_score = validation_service._assess_agricultural_soundness(unsound_data)
        assert unsound_score < soundness_score
    
    def test_create_request_from_test_data(self, validation_service):
        """Test creating ApplicationRequest from test data."""
        test_data = {
            'field_size_acres': 150.0,
            'soil_type': 'clay_loam',
            'drainage_class': 'moderate',
            'slope_percent': 3.0,
            'irrigation_available': True,
            'crop_type': 'soybean',
            'growth_stage': 'R2',
            'target_yield': 50.0,
            'fertilizer_type': 'NPK',
            'equipment_capacity': 5.0,
            'equipment_efficiency': 0.8
        }
        
        request = validation_service._create_request_from_test_data(test_data)
        
        assert isinstance(request, ApplicationRequest)
        assert request.field_conditions.field_size_acres == 150.0
        assert request.field_conditions.soil_type == 'clay_loam'
        assert request.crop_requirements.crop_type == 'soybean'
        assert request.fertilizer_specification.fertilizer_type == 'NPK'
        assert len(request.available_equipment) == 1
    
    @pytest.mark.asyncio
    async def test_validation_with_empty_data(self, validation_service):
        """Test validation with empty test data."""
        with pytest.raises(Exception):
            await validation_service.validate_algorithm_comprehensive(
                "test_algorithm",
                [],
                [ValidationType.CROSS_VALIDATION]
            )
    
    @pytest.mark.asyncio
    async def test_validation_with_invalid_algorithm_name(self, validation_service, sample_test_data):
        """Test validation with invalid algorithm name."""
        results = await validation_service.validate_algorithm_comprehensive(
            "",
            sample_test_data,
            [ValidationType.STATISTICAL_VALIDATION]
        )
        
        # Should still work but with empty algorithm name
        assert len(results) == 1
        assert results[0].algorithm_name == ""
    
    def test_validation_thresholds(self, validation_service):
        """Test validation thresholds configuration."""
        thresholds = validation_service.validation_thresholds
        
        assert 'min_accuracy' in thresholds
        assert 'min_precision' in thresholds
        assert 'min_recall' in thresholds
        assert 'min_f1_score' in thresholds
        assert 'max_response_time_ms' in thresholds
        assert 'min_user_satisfaction' in thresholds
        assert 'max_error_rate' in thresholds
        
        # Check that thresholds are reasonable
        assert 0.0 <= thresholds['min_accuracy'] <= 1.0
        assert 0.0 <= thresholds['min_precision'] <= 1.0
        assert 0.0 <= thresholds['min_recall'] <= 1.0
        assert 0.0 <= thresholds['min_f1_score'] <= 1.0
        assert thresholds['max_response_time_ms'] > 0
        assert 0.0 <= thresholds['min_user_satisfaction'] <= 5.0
        assert 0.0 <= thresholds['max_error_rate'] <= 1.0


class TestValidationIntegration:
    """Integration tests for validation system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_validation_workflow(self):
        """Test complete validation workflow from start to finish."""
        validation_service = AlgorithmValidationService()
        
        # Create comprehensive test data
        test_data = [
            {
                'field_size_acres': 100.0,
                'soil_type_encoded': 1,
                'drainage_class_encoded': 1,
                'slope_percent': 2.0,
                'irrigation_available': True,
                'crop_type_encoded': 1,
                'growth_stage_encoded': 1,
                'target_yield': 180.0,
                'fertilizer_type_encoded': 1,
                'fertilizer_form_encoded': 1,
                'equipment_count': 2,
                'equipment_types_encoded': 1,
                'weather_conditions_encoded': 0,
                'historical_success_rate': 0.8,
                'optimal_method_encoded': 1,
                'predicted_method': 'broadcast',
                'actual_method': 'broadcast',
                'efficiency_score': 0.75,
                'cost_per_acre': 25.0,
                'method_type_encoded': 1
            }
        ]
        
        # Perform comprehensive validation
        validation_results = await validation_service.validate_algorithm_comprehensive(
            "integration_test_algorithm",
            test_data,
            [
                ValidationType.CROSS_VALIDATION,
                ValidationType.STATISTICAL_VALIDATION,
                ValidationType.PERFORMANCE_VALIDATION,
                ValidationType.FIELD_VALIDATION,
                ValidationType.EXPERT_VALIDATION,
                ValidationType.OUTCOME_VALIDATION
            ]
        )
        
        # Verify all validation types were performed
        validation_types_performed = [result.validation_type for result in validation_results]
        expected_types = [
            ValidationType.CROSS_VALIDATION,
            ValidationType.STATISTICAL_VALIDATION,
            ValidationType.PERFORMANCE_VALIDATION,
            ValidationType.FIELD_VALIDATION,
            ValidationType.EXPERT_VALIDATION,
            ValidationType.OUTCOME_VALIDATION
        ]
        
        for expected_type in expected_types:
            assert expected_type in validation_types_performed
        
        # Generate improvement recommendations
        recommendations = await validation_service.generate_improvement_recommendations(
            "integration_test_algorithm",
            validation_results,
            []
        )
        
        # Verify recommendations were generated
        assert isinstance(recommendations, list)
        
        # Get validation summary
        summary = await validation_service.get_validation_summary("integration_test_algorithm", 1)
        
        # Verify summary contains expected data
        assert summary['algorithm_name'] == "integration_test_algorithm"
        assert summary['total_validations'] >= 6  # All validation types
        assert summary['avg_validation_score'] > 0
    
    @pytest.mark.asyncio
    async def test_performance_tracking_integration(self):
        """Test performance tracking integration."""
        validation_service = AlgorithmValidationService()
        
        # Create sample request and result
        request = ApplicationRequest(
            field_conditions=FieldConditions(
                field_size_acres=150.0,
                soil_type='loam',
                drainage_class='well',
                slope_percent=3.0,
                irrigation_available=True
            ),
            crop_requirements=CropRequirements(
                crop_type='corn',
                growth_stage='V8',
                target_yield=200.0
            ),
            fertilizer_specification=FertilizerSpecification(
                fertilizer_type='NPK',
                form=FertilizerForm.GRANULAR,
                npk_ratio='20-20-20'
            ),
            available_equipment=[
                EquipmentSpecification(
                    equipment_type=EquipmentType.SPREADER,
                    capacity_tons=5.0,
                    efficiency_rating=0.8
                )
            ]
        )
        
        result = OptimizationResult(
            optimal_method=ApplicationMethodType.BROADCAST,
            objective_value=0.85,
            confidence_score=0.90,
            alternative_solutions=[],
            optimization_time_ms=150.0,
            algorithm_used="test_algorithm",
            convergence_info={}
        )
        
        # Track performance multiple times
        for i in range(5):
            user_feedback = {"satisfaction_score": 4.0 + i * 0.1}
            await validation_service.track_performance_metrics(
                "performance_test_algorithm",
                request,
                result,
                user_feedback
            )
        
        # Verify performance history
        assert len(validation_service.performance_history) == 5
        
        # Get performance summary
        summary = await validation_service.get_validation_summary("performance_test_algorithm", 1)
        
        assert summary['total_performance_records'] == 5
        assert summary['avg_user_satisfaction'] > 4.0
        assert summary['avg_response_time_ms'] > 0