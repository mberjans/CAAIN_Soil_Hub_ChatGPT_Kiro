"""
Tests for Cover Crop and Mulch Optimization Service

Comprehensive test suite for the cover crop and mulch performance optimization service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date
from uuid import uuid4
from decimal import Decimal

from src.services.cover_crop_mulch_optimization_service import (
    CoverCropMulchOptimizationService,
    OptimizationObjective,
    OptimizationAlgorithm,
    OptimizationResult,
    SpeciesOptimizationRequest,
    MulchOptimizationRequest,
    PerformanceOptimizationInsight
)
from src.services.cover_management_service import (
    CoverCropSpecies,
    MulchMaterial,
    CoverCropType,
    MulchType
)
from src.models.practice_effectiveness_models import (
    PerformanceMeasurement,
    PerformanceMetric
)

class TestCoverCropMulchOptimizationService:
    """Test suite for the optimization service."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return CoverCropMulchOptimizationService()
    
    @pytest.fixture
    def mock_cover_crop_species(self):
        """Create mock cover crop species for testing."""
        return [
            CoverCropSpecies(
                species_id=uuid4(),
                common_name="Crimson Clover",
                scientific_name="Trifolium incarnatum",
                crop_type=CoverCropType.LEGUME,
                nitrogen_fixation=True,
                biomass_production_lbs_per_acre=3000,
                root_depth_inches=12,
                cold_tolerance_f=10,
                drought_tolerance=6,
                seeding_rate_lbs_per_acre=15,
                termination_methods=["mowing", "herbicide", "tillage"],
                benefits=["nitrogen fixation", "erosion control", "weed suppression"]
            ),
            CoverCropSpecies(
                species_id=uuid4(),
                common_name="Annual Ryegrass",
                scientific_name="Lolium multiflorum",
                crop_type=CoverCropType.GRASS,
                nitrogen_fixation=False,
                biomass_production_lbs_per_acre=4000,
                root_depth_inches=18,
                cold_tolerance_f=20,
                drought_tolerance=7,
                seeding_rate_lbs_per_acre=25,
                termination_methods=["herbicide", "tillage"],
                benefits=["biomass production", "erosion control", "soil structure"]
            )
        ]
    
    @pytest.fixture
    def mock_mulch_materials(self):
        """Create mock mulch materials for testing."""
        return [
            MulchMaterial(
                material_id=uuid4(),
                material_name="Wheat Straw",
                mulch_type=MulchType.ORGANIC,
                cost_per_cubic_yard=Decimal("15.00"),
                application_rate_inches=3,
                moisture_retention_percent=25,
                weed_suppression_percent=80,
                decomposition_rate_months=12,
                soil_health_benefits=["organic matter", "erosion control", "temperature moderation"]
            ),
            MulchMaterial(
                material_id=uuid4(),
                material_name="Wood Chips",
                mulch_type=MulchType.ORGANIC,
                cost_per_cubic_yard=Decimal("25.00"),
                application_rate_inches=4,
                moisture_retention_percent=30,
                weed_suppression_percent=90,
                decomposition_rate_months=24,
                soil_health_benefits=["long-term organic matter", "pathogen suppression", "carbon sequestration"]
            )
        ]
    
    @pytest.fixture
    def field_characteristics(self):
        """Create field characteristics for testing."""
        return {
            "soil_type": "clay_loam",
            "climate_zone": "6a",
            "field_size_acres": 40,
            "soil_quality_score": 0.8,
            "moisture_availability": 0.7,
            "temperature_suitability": 0.9,
            "ph_level": 6.8,
            "organic_matter_percent": 3.5,
            "slope_percent": 2,
            "drainage_class": "well_drained"
        }
    
    @pytest.fixture
    def mock_performance_measurements(self):
        """Create mock performance measurements for testing."""
        return [
            PerformanceMeasurement(
                implementation_id=uuid4(),
                measurement_date=date.today(),
                metric_type=PerformanceMetric.WATER_SAVINGS,
                metric_value=Decimal("15.5"),
                metric_unit="percent",
                measurement_method="sensor",
                measurement_source="automated",
                confidence_level=0.9,
                notes="Water savings measurement",
                baseline_value=Decimal("10.0"),
                improvement_percent=55.0
            ),
            PerformanceMeasurement(
                implementation_id=uuid4(),
                measurement_date=date.today(),
                metric_type=PerformanceMetric.SOIL_HEALTH,
                metric_value=Decimal("8.2"),
                metric_unit="score",
                measurement_method="lab_test",
                measurement_source="laboratory",
                confidence_level=0.8,
                notes="Soil health assessment",
                baseline_value=Decimal("6.5"),
                improvement_percent=26.2
            )
        ]
    
    @pytest.mark.asyncio
    async def test_initialize_service(self, service):
        """Test service initialization."""
        with patch.object(service, '_initialize_optimization_engine') as mock_engine, \
             patch.object(service, '_initialize_ml_models') as mock_ml:
            
            mock_engine.return_value = {"engine": "test_engine"}
            mock_ml.return_value = {"models": "test_models"}
            
            await service.initialize()
            
            assert service.initialized is True
            assert service.optimization_engine is not None
            assert service.ml_models is not None
    
    @pytest.mark.asyncio
    async def test_cleanup_service(self, service):
        """Test service cleanup."""
        service.initialized = True
        service.cover_management_service = AsyncMock()
        service.practice_effectiveness_service = AsyncMock()
        service.performance_monitoring_service = AsyncMock()
        
        await service.cleanup()
        
        assert service.initialized is False
        service.cover_management_service.cleanup.assert_called_once()
        service.practice_effectiveness_service.cleanup.assert_called_once()
        service.performance_monitoring_service.cleanup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_optimize_cover_crop_species(self, service, mock_cover_crop_species, field_characteristics):
        """Test cover crop species optimization."""
        # Mock the cover management service
        service.cover_management_service = AsyncMock()
        service.cover_management_service._load_cover_crop_database.return_value = mock_cover_crop_species
        
        # Create request
        request = SpeciesOptimizationRequest(
            field_id=uuid4(),
            field_characteristics=field_characteristics,
            optimization_objectives=[OptimizationObjective.MAXIMIZE_WATER_SAVINGS],
            constraints={}
        )
        
        # Mock helper methods
        with patch.object(service, '_filter_species_by_field_characteristics') as mock_filter, \
             patch.object(service, '_apply_species_constraints') as mock_constraints, \
             patch.object(service, '_run_species_optimization') as mock_optimize, \
             patch.object(service, '_apply_ml_optimization') as mock_ml:
            
            mock_filter.return_value = mock_cover_crop_species
            mock_constraints.return_value = mock_cover_crop_species
            mock_optimize.return_value = mock_cover_crop_species[:1]
            mock_ml.return_value = mock_cover_crop_species[:1]
            
            result = await service.optimize_cover_crop_species(request)
            
            assert len(result) == 1
            assert result[0].common_name == "Crimson Clover"
            mock_filter.assert_called_once()
            mock_constraints.assert_called_once()
            mock_optimize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_optimize_mulch_materials(self, service, mock_mulch_materials, field_characteristics):
        """Test mulch material optimization."""
        # Mock the cover management service
        service.cover_management_service = AsyncMock()
        service.cover_management_service._load_mulch_database.return_value = mock_mulch_materials
        
        # Create request
        request = MulchOptimizationRequest(
            field_id=uuid4(),
            field_characteristics=field_characteristics,
            optimization_objectives=[OptimizationObjective.MAXIMIZE_WATER_SAVINGS],
            constraints={}
        )
        
        # Mock helper methods
        with patch.object(service, '_filter_materials_by_field_characteristics') as mock_filter, \
             patch.object(service, '_apply_material_constraints') as mock_constraints, \
             patch.object(service, '_run_material_optimization') as mock_optimize, \
             patch.object(service, '_apply_ml_material_optimization') as mock_ml:
            
            mock_filter.return_value = mock_mulch_materials
            mock_constraints.return_value = mock_mulch_materials
            mock_optimize.return_value = mock_mulch_materials[:1]
            mock_ml.return_value = mock_mulch_materials[:1]
            
            result = await service.optimize_mulch_materials(request)
            
            assert len(result) == 1
            assert result[0].material_name == "Wheat Straw"
            mock_filter.assert_called_once()
            mock_constraints.assert_called_once()
            mock_optimize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_comprehensive_optimization(self, service, mock_cover_crop_species, mock_mulch_materials, field_characteristics):
        """Test comprehensive optimization generation."""
        # Mock the optimization methods
        with patch.object(service, 'optimize_cover_crop_species') as mock_species, \
             patch.object(service, 'optimize_mulch_materials') as mock_mulch, \
             patch.object(service, '_generate_performance_predictions') as mock_predictions, \
             patch.object(service, '_perform_economic_analysis') as mock_economics, \
             patch.object(service, '_create_optimized_implementation_plan') as mock_plan, \
             patch.object(service, '_calculate_optimization_confidence') as mock_confidence:
            
            mock_species.return_value = mock_cover_crop_species[:1]
            mock_mulch.return_value = mock_mulch_materials[:1]
            mock_predictions.return_value = {"water_savings": {"predicted_percent": 25}}
            mock_economics.return_value = {"total_cost": 1000, "roi_percent": 15}
            mock_plan.return_value = {"phases": ["preparation", "implementation"]}
            mock_confidence.return_value = 0.8
            
            result = await service.generate_comprehensive_optimization(
                uuid4(),
                field_characteristics,
                [OptimizationObjective.MAXIMIZE_WATER_SAVINGS]
            )
            
            assert isinstance(result, OptimizationResult)
            assert len(result.optimized_cover_crops) == 1
            assert len(result.optimized_mulch_materials) == 1
            assert result.confidence_score == 0.8
            assert result.optimization_objective == OptimizationObjective.MAXIMIZE_WATER_SAVINGS
    
    @pytest.mark.asyncio
    async def test_generate_performance_insights(self, service, mock_performance_measurements):
        """Test performance insights generation."""
        field_id = uuid4()
        
        # Mock insight generation methods
        with patch.object(service, '_analyze_performance_trends') as mock_trends, \
             patch.object(service, '_analyze_optimization_effectiveness') as mock_effectiveness, \
             patch.object(service, '_generate_ml_insights') as mock_ml, \
             patch.object(service, '_generate_species_insights') as mock_species, \
             patch.object(service, '_generate_mulch_insights') as mock_mulch:
            
            mock_trends.return_value = [
                PerformanceOptimizationInsight(
                    field_id=field_id,
                    insight_type="performance_trend",
                    insight_description="Water savings trend is improving",
                    confidence_score=0.8,
                    supporting_data={"trend": "improving"},
                    recommended_actions=["Continue current practices"],
                    expected_impact="Maintained water conservation"
                )
            ]
            mock_effectiveness.return_value = []
            mock_ml.return_value = []
            mock_species.return_value = []
            mock_mulch.return_value = []
            
            insights = await service.generate_performance_insights(
                field_id,
                mock_performance_measurements,
                []
            )
            
            assert len(insights) == 1
            assert insights[0].insight_type == "performance_trend"
            assert insights[0].confidence_score == 0.8
    
    @pytest.mark.asyncio
    async def test_optimize_implementation_timing(self, service, mock_cover_crop_species, mock_mulch_materials, field_characteristics):
        """Test implementation timing optimization."""
        field_id = uuid4()
        
        # Mock timing analysis methods
        with patch.object(service, '_analyze_planting_windows') as mock_planting, \
             patch.object(service, '_analyze_termination_timing') as mock_termination, \
             patch.object(service, '_analyze_mulch_timing') as mock_mulch_timing, \
             patch.object(service, '_create_integrated_schedule') as mock_schedule, \
             patch.object(service, '_assess_timing_risks') as mock_risks:
            
            mock_planting.return_value = {"optimal_planting_dates": ["September 15-30"]}
            mock_termination.return_value = {"optimal_termination_dates": ["April 15-30"]}
            mock_mulch_timing.return_value = {"optimal_application_dates": ["After termination"]}
            mock_schedule.return_value = {"phases": ["preparation", "planting"]}
            mock_risks.return_value = {"risk_level": "moderate"}
            
            timing_plan = await service.optimize_implementation_timing(
                field_id,
                mock_cover_crop_species,
                mock_mulch_materials,
                field_characteristics
            )
            
            assert timing_plan["field_id"] == field_id
            assert "planting_windows" in timing_plan
            assert "termination_timing" in timing_plan
            assert "mulch_timing" in timing_plan
            assert "integrated_schedule" in timing_plan
            assert "risk_assessment" in timing_plan
    
    @pytest.mark.asyncio
    async def test_filter_species_by_field_characteristics(self, service, mock_cover_crop_species, field_characteristics):
        """Test species filtering by field characteristics."""
        with patch.object(service, '_is_climate_suitable') as mock_climate, \
             patch.object(service, '_is_soil_compatible') as mock_soil, \
             patch.object(service, '_meets_field_size_requirements') as mock_size:
            
            mock_climate.return_value = True
            mock_soil.return_value = True
            mock_size.return_value = True
            
            result = await service._filter_species_by_field_characteristics(
                mock_cover_crop_species,
                field_characteristics
            )
            
            assert len(result) == len(mock_cover_crop_species)
            mock_climate.assert_called()
            mock_soil.assert_called()
            mock_size.assert_called()
    
    @pytest.mark.asyncio
    async def test_apply_species_constraints(self, service, mock_cover_crop_species):
        """Test species constraint application."""
        constraints = {
            "budget_limit": 1000,
            "available_equipment": ["drill", "sprayer"],
            "labor_hours_available": 40
        }
        
        with patch.object(service, '_estimate_species_cost') as mock_cost, \
             patch.object(service, '_is_equipment_compatible') as mock_equipment, \
             patch.object(service, '_estimate_labor_requirements') as mock_labor:
            
            mock_cost.return_value = Decimal("500")
            mock_equipment.return_value = True
            mock_labor.return_value = 20
            
            result = await service._apply_species_constraints(
                mock_cover_crop_species,
                constraints
            )
            
            assert len(result) == len(mock_cover_crop_species)
            mock_cost.assert_called()
            mock_equipment.assert_called()
            mock_labor.assert_called()
    
    @pytest.mark.asyncio
    async def test_run_species_optimization(self, service, mock_cover_crop_species, field_characteristics):
        """Test species optimization algorithm."""
        objectives = [OptimizationObjective.MAXIMIZE_WATER_SAVINGS]
        
        with patch.object(service, '_calculate_species_score') as mock_score:
            mock_score.return_value = 8.5
            
            result = await service._run_species_optimization(
                mock_cover_crop_species,
                objectives,
                field_characteristics
            )
            
            assert len(result) <= 3  # Should return top 3
            mock_score.assert_called()
    
    @pytest.mark.asyncio
    async def test_generate_performance_predictions(self, service, mock_cover_crop_species, mock_mulch_materials, field_characteristics):
        """Test performance prediction generation."""
        result = await service._generate_performance_predictions(
            mock_cover_crop_species,
            mock_mulch_materials,
            field_characteristics
        )
        
        assert "water_savings" in result
        assert "soil_health_improvement" in result
        assert "biomass_production" in result
        assert "nitrogen_contribution" in result
        assert "weed_suppression" in result
        
        # Check that predictions have confidence scores
        for key, prediction in result.items():
            assert "confidence" in prediction
            assert 0 <= prediction["confidence"] <= 1
    
    @pytest.mark.asyncio
    async def test_perform_economic_analysis(self, service, mock_cover_crop_species, mock_mulch_materials, field_characteristics):
        """Test economic analysis generation."""
        result = await service._perform_economic_analysis(
            mock_cover_crop_species,
            mock_mulch_materials,
            field_characteristics
        )
        
        assert "total_implementation_cost" in result
        assert "cost_per_acre" in result
        assert "cover_crop_costs" in result
        assert "mulch_costs" in result
        assert "total_benefits" in result
        assert "roi_percent" in result
        assert "payback_period_years" in result
        assert "net_present_value" in result
        
        # Check that costs are positive
        assert result["total_implementation_cost"] > 0
        assert result["cost_per_acre"] > 0
    
    @pytest.mark.asyncio
    async def test_create_optimized_implementation_plan(self, service, mock_cover_crop_species, mock_mulch_materials, field_characteristics):
        """Test optimized implementation plan creation."""
        result = await service._create_optimized_implementation_plan(
            mock_cover_crop_species,
            mock_mulch_materials,
            field_characteristics
        )
        
        assert "preparation_phase" in result
        assert "implementation_phase" in result
        assert "management_phase" in result
        assert "termination_phase" in result
        assert "optimization_features" in result
        
        # Check that phases have required fields
        for phase in ["preparation_phase", "implementation_phase", "management_phase", "termination_phase"]:
            assert "duration_weeks" in result[phase] or "duration_months" in result[phase]
            assert "activities" in result[phase]
    
    @pytest.mark.asyncio
    async def test_calculate_optimization_confidence(self, service, mock_cover_crop_species, mock_mulch_materials, field_characteristics):
        """Test optimization confidence calculation."""
        result = await service._calculate_optimization_confidence(
            mock_cover_crop_species,
            mock_mulch_materials,
            field_characteristics
        )
        
        assert 0 <= result <= 1
        assert isinstance(result, float)
    
    @pytest.mark.asyncio
    async def test_analyze_performance_trends(self, service, mock_performance_measurements):
        """Test performance trend analysis."""
        field_id = uuid4()
        
        result = await service._analyze_performance_trends(field_id, mock_performance_measurements)
        
        assert isinstance(result, list)
        # Should generate insights if enough data points
        if len(mock_performance_measurements) >= 2:
            assert len(result) > 0
            for insight in result:
                assert isinstance(insight, PerformanceOptimizationInsight)
                assert insight.field_id == field_id
    
    @pytest.mark.asyncio
    async def test_analyze_planting_windows(self, service, mock_cover_crop_species, field_characteristics):
        """Test planting window analysis."""
        result = await service._analyze_planting_windows(
            mock_cover_crop_species,
            field_characteristics,
            None
        )
        
        assert "optimal_planting_dates" in result
        assert "weather_considerations" in result
        assert "soil_temperature_requirements" in result
        assert "moisture_requirements" in result
    
    @pytest.mark.asyncio
    async def test_analyze_termination_timing(self, service, mock_cover_crop_species, field_characteristics):
        """Test termination timing analysis."""
        result = await service._analyze_termination_timing(
            mock_cover_crop_species,
            field_characteristics,
            None
        )
        
        assert "optimal_termination_dates" in result
        assert "termination_methods" in result
        assert "weather_considerations" in result
        assert "cash_crop_planting_window" in result
    
    @pytest.mark.asyncio
    async def test_analyze_mulch_timing(self, service, mock_mulch_materials, field_characteristics):
        """Test mulch timing analysis."""
        result = await service._analyze_mulch_timing(
            mock_mulch_materials,
            field_characteristics,
            None
        )
        
        assert "optimal_application_dates" in result
        assert "weather_considerations" in result
        assert "soil_conditions" in result
        assert "equipment_requirements" in result
    
    @pytest.mark.asyncio
    async def test_create_integrated_schedule(self, service):
        """Test integrated schedule creation."""
        planting_windows = {"optimal_planting_dates": ["September 15-30"]}
        termination_timing = {"optimal_termination_dates": ["April 15-30"]}
        mulch_timing = {"optimal_application_dates": ["After termination"]}
        
        result = await service._create_integrated_schedule(
            planting_windows,
            termination_timing,
            mulch_timing
        )
        
        assert "phase_1_preparation" in result
        assert "phase_2_planting" in result
        assert "phase_3_management" in result
        assert "phase_4_termination" in result
        assert "phase_5_mulching" in result
        
        # Check that phases have activities
        for phase in result.values():
            assert "activities" in phase
    
    @pytest.mark.asyncio
    async def test_assess_timing_risks(self, service):
        """Test timing risk assessment."""
        planting_windows = {"optimal_planting_dates": ["September 15-30"]}
        termination_timing = {"optimal_termination_dates": ["April 15-30"]}
        mulch_timing = {"optimal_application_dates": ["After termination"]}
        
        result = await service._assess_timing_risks(
            planting_windows,
            termination_timing,
            mulch_timing,
            None
        )
        
        assert "weather_risks" in result
        assert "timing_risks" in result
        assert "mitigation_strategies" in result
        assert "risk_level" in result
        
        assert isinstance(result["weather_risks"], list)
        assert isinstance(result["timing_risks"], list)
        assert isinstance(result["mitigation_strategies"], list)
    
    # Test helper methods
    
    def test_is_climate_suitable(self, service):
        """Test climate suitability check."""
        species = CoverCropSpecies(
            species_id=uuid4(),
            common_name="Test Species",
            scientific_name="Test species",
            crop_type=CoverCropType.LEGUME,
            nitrogen_fixation=True,
            biomass_production_lbs_per_acre=3000,
            root_depth_inches=12,
            cold_tolerance_f=15,
            drought_tolerance=6,
            seeding_rate_lbs_per_acre=15,
            termination_methods=["mowing"],
            benefits=["test"]
        )
        
        # Test different climate zones
        assert service._is_climate_suitable(species, "5a") is True
        assert service._is_climate_suitable(species, "6b") is True
        assert service._is_climate_suitable(species, "7a") is True
        assert service._is_climate_suitable(species, "8b") is True
    
    def test_estimate_species_cost(self, service):
        """Test species cost estimation."""
        species = CoverCropSpecies(
            species_id=uuid4(),
            common_name="Test Species",
            scientific_name="Test species",
            crop_type=CoverCropType.LEGUME,
            nitrogen_fixation=True,
            biomass_production_lbs_per_acre=3000,
            root_depth_inches=12,
            cold_tolerance_f=15,
            drought_tolerance=6,
            seeding_rate_lbs_per_acre=20,
            termination_methods=["mowing"],
            benefits=["test"]
        )
        
        cost = service._estimate_species_cost(species)
        expected_cost = Decimal("50.00")  # 20 * 2.50
        assert cost == expected_cost
    
    def test_estimate_material_cost(self, service):
        """Test material cost estimation."""
        material = MulchMaterial(
            material_id=uuid4(),
            material_name="Test Material",
            mulch_type=MulchType.ORGANIC,
            cost_per_cubic_yard=Decimal("20.00"),
            application_rate_inches=3,
            moisture_retention_percent=25,
            weed_suppression_percent=80,
            decomposition_rate_months=12,
            soil_health_benefits=["test"]
        )
        
        cost = service._estimate_material_cost(material)
        expected_cost = Decimal("2.00")  # 20.00 * 0.1
        assert cost == expected_cost
    
    def test_estimate_labor_requirements(self, service):
        """Test labor requirements estimation."""
        species = CoverCropSpecies(
            species_id=uuid4(),
            common_name="Test Species",
            scientific_name="Test species",
            crop_type=CoverCropType.LEGUME,
            nitrogen_fixation=True,
            biomass_production_lbs_per_acre=3000,
            root_depth_inches=12,
            cold_tolerance_f=15,
            drought_tolerance=6,
            seeding_rate_lbs_per_acre=20,
            termination_methods=["mowing"],
            benefits=["test"]
        )
        
        labor = service._estimate_labor_requirements(species)
        assert isinstance(labor, float)
        assert labor > 0
    
    def test_is_equipment_compatible(self, service):
        """Test equipment compatibility check."""
        species = CoverCropSpecies(
            species_id=uuid4(),
            common_name="Test Species",
            scientific_name="Test species",
            crop_type=CoverCropType.LEGUME,
            nitrogen_fixation=True,
            biomass_production_lbs_per_acre=3000,
            root_depth_inches=12,
            cold_tolerance_f=15,
            drought_tolerance=6,
            seeding_rate_lbs_per_acre=20,
            termination_methods=["mowing"],
            benefits=["test"]
        )
        
        available_equipment = ["drill", "sprayer", "mower"]
        compatible = service._is_equipment_compatible(species, available_equipment)
        assert isinstance(compatible, bool)
    
    @pytest.mark.asyncio
    async def test_calculate_species_score(self, service, mock_cover_crop_species, field_characteristics):
        """Test species score calculation."""
        objectives = [OptimizationObjective.MAXIMIZE_WATER_SAVINGS]
        
        score = await service._calculate_species_score(
            mock_cover_crop_species[0],
            objectives,
            field_characteristics
        )
        
        assert isinstance(score, float)
        assert score >= 0
    
    @pytest.mark.asyncio
    async def test_calculate_material_score(self, service, mock_mulch_materials, field_characteristics):
        """Test material score calculation."""
        objectives = [OptimizationObjective.MAXIMIZE_WATER_SAVINGS]
        
        score = await service._calculate_material_score(
            mock_mulch_materials[0],
            objectives,
            field_characteristics
        )
        
        assert isinstance(score, float)
        assert score >= 0

class TestOptimizationModels:
    """Test optimization data models."""
    
    def test_optimization_objective_enum(self):
        """Test optimization objective enum."""
        assert OptimizationObjective.MAXIMIZE_WATER_SAVINGS == "maximize_water_savings"
        assert OptimizationObjective.MAXIMIZE_SOIL_HEALTH == "maximize_soil_health"
        assert OptimizationObjective.MINIMIZE_COST == "minimize_cost"
        assert OptimizationObjective.MAXIMIZE_BIOMASS == "maximize_biomass"
        assert OptimizationObjective.MAXIMIZE_NITROGEN_FIXATION == "maximize_nitrogen_fixation"
        assert OptimizationObjective.BALANCED_OPTIMIZATION == "balanced_optimization"
    
    def test_optimization_algorithm_enum(self):
        """Test optimization algorithm enum."""
        assert OptimizationAlgorithm.GENETIC_ALGORITHM == "genetic_algorithm"
        assert OptimizationAlgorithm.SIMULATED_ANNEALING == "simulated_annealing"
        assert OptimizationAlgorithm.PARTICLE_SWARM == "particle_swarm"
        assert OptimizationAlgorithm.GRADIENT_DESCENT == "gradient_descent"
        assert OptimizationAlgorithm.MULTI_OBJECTIVE == "multi_objective"
    
    def test_optimization_result_model(self):
        """Test optimization result model."""
        result = OptimizationResult(
            field_id=uuid4(),
            optimization_objective=OptimizationObjective.MAXIMIZE_WATER_SAVINGS,
            algorithm_used=OptimizationAlgorithm.MULTI_OBJECTIVE,
            optimized_cover_crops=[],
            optimized_mulch_materials=[],
            performance_predictions={},
            economic_analysis={},
            implementation_plan={},
            confidence_score=0.8
        )
        
        assert result.confidence_score == 0.8
        assert result.optimization_objective == OptimizationObjective.MAXIMIZE_WATER_SAVINGS
        assert result.algorithm_used == OptimizationAlgorithm.MULTI_OBJECTIVE
        assert isinstance(result.optimization_timestamp, datetime)
    
    def test_species_optimization_request_model(self):
        """Test species optimization request model."""
        request = SpeciesOptimizationRequest(
            field_id=uuid4(),
            field_characteristics={"soil_type": "clay_loam"},
            optimization_objectives=[OptimizationObjective.MAXIMIZE_WATER_SAVINGS],
            constraints={"budget_limit": 1000}
        )
        
        assert request.field_characteristics["soil_type"] == "clay_loam"
        assert OptimizationObjective.MAXIMIZE_WATER_SAVINGS in request.optimization_objectives
        assert request.constraints["budget_limit"] == 1000
    
    def test_mulch_optimization_request_model(self):
        """Test mulch optimization request model."""
        request = MulchOptimizationRequest(
            field_id=uuid4(),
            field_characteristics={"soil_type": "clay_loam"},
            optimization_objectives=[OptimizationObjective.MAXIMIZE_WATER_SAVINGS],
            constraints={"budget_limit": 1000}
        )
        
        assert request.field_characteristics["soil_type"] == "clay_loam"
        assert OptimizationObjective.MAXIMIZE_WATER_SAVINGS in request.optimization_objectives
        assert request.constraints["budget_limit"] == 1000
    
    def test_performance_optimization_insight_model(self):
        """Test performance optimization insight model."""
        insight = PerformanceOptimizationInsight(
            field_id=uuid4(),
            insight_type="performance_trend",
            insight_description="Water savings trend is improving",
            confidence_score=0.8,
            supporting_data={"trend": "improving"},
            recommended_actions=["Continue current practices"],
            expected_impact="Maintained water conservation"
        )
        
        assert insight.insight_type == "performance_trend"
        assert insight.confidence_score == 0.8
        assert insight.supporting_data["trend"] == "improving"
        assert len(insight.recommended_actions) == 1
        assert isinstance(insight.created_at, datetime)

class TestOptimizationIntegration:
    """Test optimization service integration."""
    
    @pytest.mark.asyncio
    async def test_service_integration(self):
        """Test integration between optimization service and other services."""
        service = CoverCropMulchOptimizationService()
        
        # Mock all dependencies
        with patch('src.services.cover_crop_mulch_optimization_service.CoverManagementService') as mock_cover, \
             patch('src.services.cover_crop_mulch_optimization_service.PracticeEffectivenessService') as mock_effectiveness, \
             patch('src.services.cover_crop_mulch_optimization_service.PracticePerformanceMonitoringService') as mock_monitoring:
            
            mock_cover_instance = AsyncMock()
            mock_cover_instance.initialize.return_value = None
            mock_cover_instance.cleanup.return_value = None
            mock_cover.return_value = mock_cover_instance
            
            mock_effectiveness_instance = AsyncMock()
            mock_effectiveness_instance.initialize.return_value = None
            mock_effectiveness_instance.cleanup.return_value = None
            mock_effectiveness.return_value = mock_effectiveness_instance
            
            mock_monitoring_instance = AsyncMock()
            mock_monitoring_instance.initialize.return_value = None
            mock_monitoring_instance.cleanup.return_value = None
            mock_monitoring.return_value = mock_monitoring_instance
            
            await service.initialize()
            
            assert service.initialized is True
            assert service.cover_management_service is not None
            assert service.practice_effectiveness_service is not None
            assert service.performance_monitoring_service is not None
            
            await service.cleanup()
            
            assert service.initialized is False
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in optimization service."""
        service = CoverCropMulchOptimizationService()
        
        # Test initialization error
        with patch.object(service, '_initialize_optimization_engine', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                await service.initialize()
        
        # Test optimization error
        service.initialized = True
        service.cover_management_service = AsyncMock()
        
        with patch.object(service, '_filter_species_by_field_characteristics', side_effect=Exception("Test error")):
            request = SpeciesOptimizationRequest(
                field_id=uuid4(),
                field_characteristics={},
                optimization_objectives=[OptimizationObjective.MAXIMIZE_WATER_SAVINGS],
                constraints={}
            )
            
            with pytest.raises(Exception):
                await service.optimize_cover_crop_species(request)
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test service performance under load."""
        service = CoverCropMulchOptimizationService()
        service.initialized = True
        service.cover_management_service = AsyncMock()
        
        # Mock all methods to return quickly
        with patch.object(service, '_filter_species_by_field_characteristics') as mock_filter, \
             patch.object(service, '_apply_species_constraints') as mock_constraints, \
             patch.object(service, '_run_species_optimization') as mock_optimize, \
             patch.object(service, '_apply_ml_optimization') as mock_ml:
            
            mock_filter.return_value = []
            mock_constraints.return_value = []
            mock_optimize.return_value = []
            mock_ml.return_value = []
            
            # Create multiple concurrent requests
            tasks = []
            for i in range(10):
                request = SpeciesOptimizationRequest(
                    field_id=uuid4(),
                    field_characteristics={"soil_type": f"soil_{i}"},
                    optimization_objectives=[OptimizationObjective.MAXIMIZE_WATER_SAVINGS],
                    constraints={}
                )
                tasks.append(service.optimize_cover_crop_species(request))
            
            # Execute all requests concurrently
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 10
            assert all(isinstance(result, list) for result in results)