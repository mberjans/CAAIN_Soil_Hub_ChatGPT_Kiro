"""
Comprehensive tests for the Sophisticated Method Selection Service.

Tests cover:
- Machine learning algorithms
- Multi-criteria optimization
- Constraint satisfaction
- Fuzzy logic and uncertainty handling
- Historical data integration
- Performance validation
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from src.services.sophisticated_method_selection_service import (
    SophisticatedMethodSelectionService,
    OptimizationObjective,
    OptimizationConstraints,
    UncertaintyLevel,
    MethodSelectionFeatures
)
from src.models.application_models import (
    ApplicationRequest, ApplicationMethodType, FertilizerForm, EquipmentType,
    FieldConditions, CropRequirements, FertilizerSpecification, EquipmentSpecification
)


class TestSophisticatedMethodSelectionService:
    """Test suite for sophisticated method selection service."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return SophisticatedMethodSelectionService()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample application request."""
        return ApplicationRequest(
            field_conditions=FieldConditions(
                field_size_acres=100.0,
                soil_type="loam",
                drainage_class="well_drained",
                slope_percent=2.0,
                irrigation_available=True,
                access_roads=["main_road", "field_access"]
            ),
            crop_requirements=CropRequirements(
                crop_type="corn",
                growth_stage="vegetative",
                target_yield=180.0,
                nutrient_requirements={"nitrogen": 150, "phosphorus": 60, "potassium": 120},
                application_timing_preferences=["early_season", "mid_season"]
            ),
            fertilizer_specification=FertilizerSpecification(
                fertilizer_type="npk",
                form=FertilizerForm.GRANULAR,
                solubility=0.8,
                release_rate="slow",
                cost_per_unit=0.5,
                unit="lbs/acre"
            ),
            available_equipment=[
                EquipmentSpecification(
                    equipment_type=EquipmentType.SPREADER,
                    equipment_name="Broadcast Spreader",
                    capacity=500.0,
                    capacity_unit="lbs",
                    efficiency_rating=0.8
                )
            ]
        )
    
    @pytest.fixture
    def sample_constraints(self):
        """Create sample optimization constraints."""
        return OptimizationConstraints(
            max_cost_per_acre=30.0,
            min_efficiency_score=0.7,
            max_environmental_impact="moderate",
            equipment_availability=["spreader", "broadcaster"],
            field_access_limitations=[],
            timing_constraints=[]
        )
    
    @pytest.mark.asyncio
    async def test_ml_method_selection(self, service, sample_request):
        """Test machine learning method selection."""
        # Mock the base service
        with patch.object(service.base_service, 'select_application_methods') as mock_base:
            mock_response = MagicMock()
            mock_response.recommended_methods = [
                MagicMock(method_type=ApplicationMethodType.BROADCAST),
                MagicMock(method_type=ApplicationMethodType.BAND),
                MagicMock(method_type=ApplicationMethodType.SIDEDRESS)
            ]
            mock_base.return_value = mock_response
            
            # Test ML method selection
            result = await service._ml_method_selection(
                MethodSelectionFeatures(
                    field_size_acres=100.0,
                    soil_type_encoded=1,
                    drainage_class_encoded=1,
                    slope_percent=2.0,
                    irrigation_available=1,
                    crop_type_encoded=1,
                    growth_stage_encoded=1,
                    target_yield=180.0,
                    fertilizer_type_encoded=1,
                    fertilizer_form_encoded=1,
                    equipment_count=1,
                    equipment_types_encoded=1,
                    weather_conditions_encoded=0,
                    historical_success_rate=0.8,
                    cost_constraint=30.0,
                    environmental_constraint=0.5
                ),
                [ApplicationMethodType.BROADCAST, ApplicationMethodType.BAND],
                OptimizationObjective.MAXIMIZE_EFFICIENCY,
                OptimizationConstraints()
            )
            
            assert result.optimal_method in [ApplicationMethodType.BROADCAST, ApplicationMethodType.BAND]
            assert result.objective_value >= 0.0
            assert result.confidence_score > 0.0
            assert result.algorithm_used == "Machine Learning (Random Forest + Neural Network)"
            assert len(result.alternative_solutions) <= 2
    
    @pytest.mark.asyncio
    async def test_multi_criteria_optimization(self, service, sample_request):
        """Test multi-criteria optimization."""
        available_methods = [ApplicationMethodType.BROADCAST, ApplicationMethodType.BAND]
        
        result = await service._multi_criteria_optimization(
            sample_request,
            available_methods,
            OptimizationObjective.BALANCED_OPTIMIZATION,
            OptimizationConstraints()
        )
        
        assert result.optimal_method in available_methods
        assert result.objective_value >= 0.0
        assert result.confidence_score > 0.0
        assert result.algorithm_used == "Multi-criteria Optimization (Scipy SLSQP)"
        assert "success" in result.convergence_info
        assert "final_weights" in result.convergence_info
    
    @pytest.mark.asyncio
    async def test_constraint_satisfaction_selection(self, service, sample_request, sample_constraints):
        """Test constraint satisfaction selection."""
        available_methods = [ApplicationMethodType.BROADCAST, ApplicationMethodType.BAND, ApplicationMethodType.FOLIAR]
        
        result = await service._constraint_satisfaction_selection(
            sample_request,
            available_methods,
            sample_constraints
        )
        
        assert result.optimal_method in available_methods
        assert result.objective_value >= 0.0
        assert result.confidence_score > 0.0
        assert result.algorithm_used == "Constraint Satisfaction"
        assert "satisfied_methods" in result.convergence_info
        assert "total_constraints" in result.convergence_info
    
    @pytest.mark.asyncio
    async def test_fuzzy_logic_selection(self, service, sample_request):
        """Test fuzzy logic selection with uncertainty handling."""
        available_methods = [ApplicationMethodType.BROADCAST, ApplicationMethodType.BAND]
        
        # Test with different uncertainty levels
        for uncertainty_level in [UncertaintyLevel.LOW, UncertaintyLevel.MEDIUM, UncertaintyLevel.HIGH]:
            result = await service._fuzzy_logic_selection(
                sample_request,
                available_methods,
                uncertainty_level
            )
            
            assert result.optimal_method in available_methods
            assert result.objective_value >= 0.0
            assert result.confidence_score > 0.0
            assert result.algorithm_used.startswith("Fuzzy Logic")
            assert uncertainty_level.value in result.algorithm_used
            assert "uncertainty_level" in result.convergence_info
            assert "uncertainty_factor" in result.convergence_info
    
    @pytest.mark.asyncio
    async def test_ensemble_decision_making(self, service):
        """Test ensemble decision making."""
        # Create mock results
        results = [
            MagicMock(
                optimal_method=ApplicationMethodType.BROADCAST,
                objective_value=0.8,
                confidence_score=0.9,
                algorithm_used="Machine Learning",
                optimization_time_ms=100.0
            ),
            MagicMock(
                optimal_method=ApplicationMethodType.BAND,
                objective_value=0.7,
                confidence_score=0.8,
                algorithm_used="Multi-criteria Optimization",
                optimization_time_ms=150.0
            )
        ]
        
        result = await service._ensemble_decision_making(
            results,
            OptimizationObjective.BALANCED_OPTIMIZATION,
            UncertaintyLevel.MEDIUM
        )
        
        assert result.optimal_method in [ApplicationMethodType.BROADCAST, ApplicationMethodType.BAND]
        assert result.objective_value >= 0.0
        assert result.confidence_score > 0.0
        assert result.algorithm_used == "Ensemble Decision Making"
        assert result.optimization_time_ms == 250.0  # Sum of individual times
        assert "algorithms_used" in result.convergence_info
        assert "individual_confidences" in result.convergence_info
    
    @pytest.mark.asyncio
    async def test_select_optimal_method_sophisticated(self, service, sample_request, sample_constraints):
        """Test the main sophisticated method selection function."""
        # Mock the base service
        with patch.object(service.base_service, 'select_application_methods') as mock_base:
            mock_response = MagicMock()
            mock_response.recommended_methods = [
                MagicMock(method_type=ApplicationMethodType.BROADCAST),
                MagicMock(method_type=ApplicationMethodType.BAND)
            ]
            mock_base.return_value = mock_response
            
            result = await service.select_optimal_method_sophisticated(
                sample_request,
                objective=OptimizationObjective.BALANCED_OPTIMIZATION,
                constraints=sample_constraints,
                uncertainty_level=UncertaintyLevel.MEDIUM,
                use_ml=True,
                use_optimization=True,
                use_fuzzy_logic=True
            )
            
            assert result.optimal_method in [ApplicationMethodType.BROADCAST, ApplicationMethodType.BAND]
            assert result.objective_value >= 0.0
            assert result.confidence_score > 0.0
            assert result.optimization_time_ms > 0.0
            assert result.algorithm_used == "Ensemble Decision Making"
            assert len(result.alternative_solutions) <= 2
    
    @pytest.mark.asyncio
    async def test_feature_extraction(self, service, sample_request):
        """Test feature extraction for ML models."""
        features = await service._extract_features(sample_request)
        
        assert isinstance(features, MethodSelectionFeatures)
        assert features.field_size_acres == 100.0
        assert features.soil_type_encoded >= 0
        assert features.crop_type_encoded >= 0
        assert features.equipment_count == 1
        assert features.target_yield == 180.0
    
    def test_categorical_encoding(self, service):
        """Test categorical feature encoding."""
        # Test encoding new categories
        encoded = service._encode_categorical('soil_type', 'clay')
        assert isinstance(encoded, int)
        assert encoded >= 0
        
        # Test encoding same category again
        encoded2 = service._encode_categorical('soil_type', 'clay')
        assert encoded == encoded2
        
        # Test encoding different category
        encoded3 = service._encode_categorical('soil_type', 'sandy')
        assert encoded3 != encoded
    
    def test_uncertainty_factor_calculation(self, service):
        """Test uncertainty factor calculation."""
        assert service._get_uncertainty_factor(UncertaintyLevel.LOW) == 1.0
        assert service._get_uncertainty_factor(UncertaintyLevel.MEDIUM) == 0.8
        assert service._get_uncertainty_factor(UncertaintyLevel.HIGH) == 0.6
        assert service._get_uncertainty_factor(UncertaintyLevel.VERY_HIGH) == 0.4
    
    def test_environmental_score_calculation(self, service):
        """Test environmental score calculation."""
        assert service._get_environmental_score('very_low') == 1.0
        assert service._get_environmental_score('low') == 0.8
        assert service._get_environmental_score('moderate') == 0.6
        assert service._get_environmental_score('high') == 0.4
        assert service._get_environmental_score('very_high') == 0.2
        assert service._get_environmental_score('unknown') == 0.6  # Default
    
    @pytest.mark.asyncio
    async def test_ml_model_training(self, service):
        """Test ML model training with sample data."""
        training_data = [
            {
                'field_size_acres': 100.0,
                'soil_type_encoded': 1,
                'drainage_class_encoded': 1,
                'slope_percent': 2.0,
                'irrigation_available': 1,
                'crop_type_encoded': 1,
                'growth_stage_encoded': 1,
                'target_yield': 180.0,
                'fertilizer_type_encoded': 1,
                'fertilizer_form_encoded': 1,
                'equipment_count': 1,
                'equipment_types_encoded': 1,
                'weather_conditions_encoded': 0,
                'historical_success_rate': 0.8,
                'efficiency_score': 0.8,
                'cost_per_acre': 25.0,
                'method_type_encoded': 1
            }
        ] * 10  # Create 10 samples
        
        result = await service.train_ml_models(training_data)
        
        assert "efficiency_rf_cv_score" in result
        assert "cost_rf_cv_score" in result
        assert "method_classifier_cv_score" in result
        assert result["training_samples"] == 10
    
    @pytest.mark.asyncio
    async def test_historical_data_update(self, service):
        """Test historical data update."""
        outcome_data = {
            'application_id': 'test_app_123',
            'method_used': 'broadcast',
            'algorithm_used': 'ml',
            'predicted_efficiency': 0.8,
            'predicted_cost': 25.0,
            'actual_efficiency': 0.75,
            'actual_cost': 27.0,
            'farmer_satisfaction': 0.8
        }
        
        # Test adding outcome data
        service.historical_data = []  # Reset
        await service.update_historical_data(outcome_data)
        
        assert len(service.historical_data) == 1
        assert service.historical_data[0]['application_id'] == 'test_app_123'
        
        # Test data limit (keep only 1000 records)
        service.historical_data = [outcome_data] * 1001
        await service.update_historical_data(outcome_data)
        
        assert len(service.historical_data) == 1000
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self, service, sample_request):
        """Test that performance requirements are met (<2s method selection)."""
        start_time = time.time()
        
        # Mock the base service
        with patch.object(service.base_service, 'select_application_methods') as mock_base:
            mock_response = MagicMock()
            mock_response.recommended_methods = [
                MagicMock(method_type=ApplicationMethodType.BROADCAST),
                MagicMock(method_type=ApplicationMethodType.BAND)
            ]
            mock_base.return_value = mock_response
            
            result = await service.select_optimal_method_sophisticated(
                sample_request,
                objective=OptimizationObjective.BALANCED_OPTIMIZATION,
                constraints=OptimizationConstraints(),
                uncertainty_level=UncertaintyLevel.MEDIUM
            )
            
            elapsed_time = time.time() - start_time
            
            assert elapsed_time < 2.0, f"Method selection took {elapsed_time:.2f}s, exceeds 2s requirement"
            assert result.optimization_time_ms < 2000, f"Optimization time {result.optimization_time_ms}ms exceeds 2000ms requirement"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling in sophisticated method selection."""
        # Test with invalid request
        invalid_request = ApplicationRequest(
            field_conditions=FieldConditions(field_size_acres=-1.0),  # Invalid field size
            crop_requirements=CropRequirements(crop_type="invalid_crop"),
            fertilizer_specification=FertilizerSpecification(fertilizer_type="invalid"),
            available_equipment=[]
        )
        
        # Mock the base service to return empty recommendations
        with patch.object(service.base_service, 'select_application_methods') as mock_base:
            mock_response = MagicMock()
            mock_response.recommended_methods = []
            mock_base.return_value = mock_response
            
            with pytest.raises(ValueError, match="No suitable methods found"):
                await service.select_optimal_method_sophisticated(invalid_request)
    
    @pytest.mark.asyncio
    async def test_algorithm_combinations(self, service, sample_request):
        """Test different combinations of algorithms."""
        # Mock the base service
        with patch.object(service.base_service, 'select_application_methods') as mock_base:
            mock_response = MagicMock()
            mock_response.recommended_methods = [
                MagicMock(method_type=ApplicationMethodType.BROADCAST),
                MagicMock(method_type=ApplicationMethodType.BAND)
            ]
            mock_base.return_value = mock_response
            
            # Test ML only
            result_ml = await service.select_optimal_method_sophisticated(
                sample_request,
                use_ml=True,
                use_optimization=False,
                use_fuzzy_logic=False
            )
            assert result_ml.algorithm_used == "Ensemble Decision Making"
            
            # Test optimization only
            result_opt = await service.select_optimal_method_sophisticated(
                sample_request,
                use_ml=False,
                use_optimization=True,
                use_fuzzy_logic=False
            )
            assert result_opt.algorithm_used == "Ensemble Decision Making"
            
            # Test fuzzy logic only
            result_fuzzy = await service.select_optimal_method_sophisticated(
                sample_request,
                use_ml=False,
                use_optimization=False,
                use_fuzzy_logic=True
            )
            assert result_fuzzy.algorithm_used == "Ensemble Decision Making"


class TestHistoricalDataService:
    """Test suite for historical data service."""
    
    @pytest.fixture
    def historical_service(self):
        """Create historical data service instance."""
        from src.services.historical_data_service import HistoricalDataService, OutcomeData, OutcomeType
        return HistoricalDataService()
    
    @pytest.fixture
    def sample_outcome_data(self):
        """Create sample outcome data."""
        return OutcomeData(
            application_id="test_app_123",
            method_used=ApplicationMethodType.BROADCAST,
            algorithm_used="ml_algorithm",
            predicted_efficiency=0.8,
            predicted_cost=25.0,
            actual_efficiency=0.75,
            actual_cost=27.0,
            yield_impact=0.05,
            farmer_satisfaction=0.8,
            environmental_impact="moderate",
            outcome_type=OutcomeType.SUCCESS,
            notes="Test application",
            timestamp=datetime.utcnow()
        )
    
    @pytest.mark.asyncio
    async def test_outcome_data_structure(self, sample_outcome_data):
        """Test outcome data structure."""
        assert sample_outcome_data.application_id == "test_app_123"
        assert sample_outcome_data.method_used == ApplicationMethodType.BROADCAST
        assert sample_outcome_data.algorithm_used == "ml_algorithm"
        assert sample_outcome_data.predicted_efficiency == 0.8
        assert sample_outcome_data.actual_efficiency == 0.75
        assert sample_outcome_data.outcome_type == OutcomeType.SUCCESS
    
    def test_performance_analysis_structure(self):
        """Test performance analysis data structure."""
        from src.services.historical_data_service import PerformanceAnalysis
        
        analysis = PerformanceAnalysis(
            algorithm_name="test_algorithm",
            total_applications=100,
            success_rate=0.85,
            average_efficiency=0.8,
            average_cost=25.0,
            average_satisfaction=0.8,
            performance_trend="improving",
            confidence_score=0.9,
            recommendations=["Good performance"]
        )
        
        assert analysis.algorithm_name == "test_algorithm"
        assert analysis.total_applications == 100
        assert analysis.success_rate == 0.85
        assert analysis.performance_trend == "improving"
        assert len(analysis.recommendations) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])