"""
Test suite for Water Savings Calculator Service

Comprehensive tests for water savings calculation functionality,
including practice-specific calculations, cost-benefit analysis,
and agricultural validation.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal
from uuid import uuid4, UUID
from datetime import date, timedelta

from src.services.water_savings_calculator import WaterSavingsCalculator
from src.models.drought_models import (
    WaterSavingsRequest,
    WaterSavingsResponse,
    ConservationPractice,
    ConservationPracticeType,
    SoilHealthImpact,
    EquipmentRequirement
)


class TestWaterSavingsCalculator:
    """Test suite for Water Savings Calculator service."""

    @pytest.fixture
    def calculator(self):
        """Create water savings calculator instance."""
        return WaterSavingsCalculator()

    @pytest.fixture
    def sample_field_id(self):
        """Sample field ID for testing."""
        return uuid4()

    @pytest.fixture
    def sample_conservation_practices(self):
        """Sample conservation practices for testing."""
        return [
            ConservationPractice(
                practice_id=uuid4(),
                practice_name="Cover Crops",
                practice_type=ConservationPracticeType.COVER_CROPS,
                description="Plant cover crops to improve soil health and water retention",
                implementation_cost=Decimal("10.00"),  # $10 per acre
                water_savings_percent=20.0,
                soil_health_impact=SoilHealthImpact.POSITIVE,
                equipment_requirements=[
                    EquipmentRequirement(
                        equipment_type="Seeder",
                        equipment_name="No-till drill",
                        availability=True,
                        rental_cost_per_day=Decimal("200.00")
                    )
                ],
                implementation_time_days=3,
                maintenance_cost_per_year=Decimal("2.00"),  # $2 per acre per year
                effectiveness_rating=8.5
            ),
            ConservationPractice(
                practice_id=uuid4(),
                practice_name="No-Till Farming",
                practice_type=ConservationPracticeType.NO_TILL,
                description="Eliminate tillage to reduce soil disturbance and water loss",
                implementation_cost=Decimal("15.00"),  # $15 per acre
                water_savings_percent=15.0,
                soil_health_impact=SoilHealthImpact.HIGHLY_POSITIVE,
                equipment_requirements=[
                    EquipmentRequirement(
                        equipment_type="Planter",
                        equipment_name="No-till planter",
                        availability=True,
                        purchase_cost=Decimal("50000.00")
                    )
                ],
                implementation_time_days=5,
                maintenance_cost_per_year=Decimal("3.00"),  # $3 per acre per year
                effectiveness_rating=9.0
            )
        ]

    @pytest.fixture
    def sample_water_savings_request(self, sample_field_id, sample_conservation_practices):
        """Sample water savings request for testing."""
        return WaterSavingsRequest(
            field_id=sample_field_id,
            current_water_usage=Decimal("100000.00"),  # 100,000 gallons for 40 acres = 2,500 gallons/acre/year
            proposed_practices=sample_conservation_practices,
            implementation_timeline="phased",
            cost_constraints=Decimal("10000.00"),
            effectiveness_assumptions={
                "cover_crops": 0.9,
                "no_till": 0.95
            }
        )

    @pytest.mark.asyncio
    async def test_initialization(self, calculator):
        """Test calculator initialization."""
        await calculator.initialize()
        assert calculator.initialized is True
        assert calculator.calculation_models is not None
        assert "practice_models" in calculator.calculation_models
        assert "cost_models" in calculator.calculation_models

    @pytest.mark.asyncio
    async def test_calculate_water_savings_success(self, calculator, sample_water_savings_request):
        """Test successful water savings calculation."""
        await calculator.initialize()
        
        with patch.object(calculator, '_get_field_characteristics') as mock_field:
            mock_field.return_value = {
                "field_id": sample_water_savings_request.field_id,
                "field_size_acres": 40.0,
                "soil_type": "clay_loam",
                "slope_percent": 2.5,
                "drainage_class": "moderate",
                "climate_zone": "temperate",
                "current_irrigation_type": "sprinkler",
                "organic_matter_percent": 3.2,
                "water_source": "groundwater",
                "energy_cost_per_kwh": 0.12
            }
            
            result = await calculator.calculate_water_savings(sample_water_savings_request)
            
            assert isinstance(result, WaterSavingsResponse)
            assert result.field_id == sample_water_savings_request.field_id
            assert result.current_usage == sample_water_savings_request.current_water_usage
            assert result.projected_savings > Decimal("0")
            assert result.savings_percentage > 0
            assert "implementation_cost" in result.cost_benefit_analysis
            assert "annual_savings" in result.cost_benefit_analysis
            assert "roi_percentage" in result.cost_benefit_analysis
            assert "timeline_preference" in result.implementation_timeline
            assert "phases" in result.implementation_timeline
            assert len(result.monitoring_recommendations) > 0

    @pytest.mark.asyncio
    async def test_cost_benefit_analysis(self, calculator, sample_water_savings_request):
        """Test cost-benefit analysis calculations."""
        await calculator.initialize()
        
        with patch.object(calculator, '_get_field_characteristics') as mock_field:
            mock_field.return_value = {
                "field_id": sample_water_savings_request.field_id,
                "field_size_acres": 40.0,
                "soil_type": "clay_loam",
                "slope_percent": 2.5,
                "drainage_class": "moderate",
                "climate_zone": "temperate",
                "current_irrigation_type": "sprinkler",
                "organic_matter_percent": 3.2,
                "water_source": "groundwater",
                "energy_cost_per_kwh": 0.12
            }
            
            result = await calculator.calculate_water_savings(sample_water_savings_request)
            cost_benefit = result.cost_benefit_analysis
            
            # Verify cost-benefit analysis structure
            assert "implementation_cost" in cost_benefit
            assert "annual_savings" in cost_benefit
            assert "roi_percentage" in cost_benefit
            assert "payback_period_years" in cost_benefit
            assert "investment_grade" in cost_benefit
            assert "recommendation" in cost_benefit
            
            # Verify reasonable values
            assert cost_benefit["implementation_cost"] > Decimal("0")
            assert cost_benefit["annual_savings"] > Decimal("0")
            assert cost_benefit["roi_percentage"] >= 0
            assert cost_benefit["payback_period_years"] > 0
            assert cost_benefit["investment_grade"] in ["A+", "A", "B+", "B", "C"]

    @pytest.mark.asyncio
    async def test_implementation_timeline_generation(self, calculator, sample_water_savings_request):
        """Test implementation timeline generation."""
        await calculator.initialize()
        
        with patch.object(calculator, '_get_field_characteristics') as mock_field:
            mock_field.return_value = {
                "field_id": sample_water_savings_request.field_id,
                "field_size_acres": 40.0,
                "soil_type": "clay_loam",
                "slope_percent": 2.5,
                "drainage_class": "moderate",
                "climate_zone": "temperate",
                "current_irrigation_type": "sprinkler",
                "organic_matter_percent": 3.2,
                "water_source": "groundwater",
                "energy_cost_per_kwh": 0.12
            }
            
            result = await calculator.calculate_water_savings(sample_water_savings_request)
            timeline = result.implementation_timeline
            
            # Verify timeline structure
            assert "timeline_preference" in timeline
            assert "phases" in timeline
            assert "total_duration" in timeline
            assert "critical_path" in timeline
            
            # Verify phases
            assert len(timeline["phases"]) > 0
            for phase in timeline["phases"]:
                assert "phase" in phase
                assert "practices" in phase
                assert "start_date" in phase
                assert "duration_days" in phase
                assert "priority" in phase

    @pytest.mark.asyncio
    async def test_monitoring_recommendations(self, calculator, sample_water_savings_request):
        """Test monitoring recommendations generation."""
        await calculator.initialize()
        
        with patch.object(calculator, '_get_field_characteristics') as mock_field:
            mock_field.return_value = {
                "field_id": sample_water_savings_request.field_id,
                "field_size_acres": 40.0,
                "soil_type": "clay_loam",
                "slope_percent": 2.5,
                "drainage_class": "moderate",
                "climate_zone": "temperate",
                "current_irrigation_type": "sprinkler",
                "organic_matter_percent": 3.2,
                "water_source": "groundwater",
                "energy_cost_per_kwh": 0.12
            }
            
            result = await calculator.calculate_water_savings(sample_water_savings_request)
            recommendations = result.monitoring_recommendations
            
            # Verify recommendations structure
            assert len(recommendations) > 0
            assert all(isinstance(rec, str) for rec in recommendations)
            
            # Verify specific recommendations are included
            recommendation_text = " ".join(recommendations).lower()
            assert "soil moisture" in recommendation_text
            assert "water usage" in recommendation_text
            assert "crop health" in recommendation_text

    @pytest.mark.asyncio
    async def test_get_water_savings_history(self, calculator, sample_field_id):
        """Test getting water savings history."""
        await calculator.initialize()
        
        start_date = date.today() - timedelta(days=365)
        end_date = date.today()
        
        with patch.object(calculator, '_get_historical_data') as mock_historical:
            mock_historical.return_value = [
                {
                    "date": start_date,
                    "water_usage": Decimal("10000"),
                    "water_savings": Decimal("2000"),
                    "savings_percentage": 20.0,
                    "cost_benefit": {"roi_percentage": 25.0, "payback_years": 4.0},
                    "timeline": {"implementation_status": "completed"},
                    "monitoring": ["Soil moisture tracking"]
                }
            ]
            
            history = await calculator.get_water_savings_history(sample_field_id, start_date, end_date)
            
            assert len(history) > 0
            assert all(isinstance(h, WaterSavingsResponse) for h in history)
            assert all(h.field_id == sample_field_id for h in history)

    @pytest.mark.asyncio
    async def test_calculation_models_loading(self, calculator):
        """Test that calculation models are loaded correctly."""
        await calculator.initialize()
        
        models = calculator.calculation_models
        
        # Verify practice models structure
        assert "practice_models" in models
        practice_models = models["practice_models"]
        
        # Verify specific practice types are included
        assert "cover_crops" in practice_models
        assert "no_till" in practice_models
        assert "mulching" in practice_models
        assert "irrigation_efficiency" in practice_models
        
        # Verify each practice model has required fields
        for practice_type, model in practice_models.items():
            assert "base_savings_percent" in model
            assert isinstance(model["base_savings_percent"], (int, float))
            assert model["base_savings_percent"] > 0
        
        # Verify cost models structure
        assert "cost_models" in models
        cost_models = models["cost_models"]
        assert "water_cost_per_gallon" in cost_models
        assert "energy_cost_per_kwh" in cost_models
        assert "maintenance_cost_percent" in cost_models


class TestAgriculturalValidation:
    """Agricultural validation tests for water savings calculations."""

    @pytest.fixture
    def calculator(self):
        """Create water savings calculator instance."""
        return WaterSavingsCalculator()

    @pytest.mark.asyncio
    async def test_cover_crop_water_savings_accuracy(self, calculator):
        """Test cover crop water savings calculations against agricultural standards."""
        await calculator.initialize()
        
        # Test with typical cover crop scenario
        request = WaterSavingsRequest(
            field_id=uuid4(),
            current_water_usage=Decimal("100000"),  # 100,000 gallons for 40 acres = 2,500 gallons/acre/year
            proposed_practices=[
                ConservationPractice(
                    practice_id=uuid4(),
                    practice_name="Winter Cover Crop",
                    practice_type=ConservationPracticeType.COVER_CROPS,
                    description="Winter rye cover crop",
                    implementation_cost=Decimal("10.00"),  # $10 per acre (more realistic)
                    water_savings_percent=20.0,
                    soil_health_impact=SoilHealthImpact.POSITIVE,
                    equipment_requirements=[],
                    implementation_time_days=2,
                    maintenance_cost_per_year=Decimal("2.00"),  # $2 per acre per year
                    effectiveness_rating=8.0
                )
            ],
            implementation_timeline="seasonal"
        )
        
        with patch.object(calculator, '_get_field_characteristics') as mock_field:
            mock_field.return_value = {
                "field_id": request.field_id,
                "field_size_acres": 40.0,
                "soil_type": "clay_loam",
                "slope_percent": 2.5,
                "drainage_class": "moderate",
                "climate_zone": "temperate",
                "current_irrigation_type": "sprinkler",
                "organic_matter_percent": 3.2,
                "water_source": "groundwater",
                "energy_cost_per_kwh": 0.12
            }
            
            result = await calculator.calculate_water_savings(request)
            
            # Verify savings are within expected range for cover crops (15-25%)
            assert 15 <= result.savings_percentage <= 25
            
            # Verify cost-benefit analysis shows positive ROI
            assert result.cost_benefit_analysis["roi_percentage"] > 0
            assert result.cost_benefit_analysis["payback_period_years"] < 10

    @pytest.mark.asyncio
    async def test_no_till_water_savings_accuracy(self, calculator):
        """Test no-till water savings calculations against agricultural standards."""
        await calculator.initialize()
        
        # Test with no-till scenario
        request = WaterSavingsRequest(
            field_id=uuid4(),
            current_water_usage=Decimal("100000"),  # 100,000 gallons for 40 acres = 2,500 gallons/acre/year
            proposed_practices=[
                ConservationPractice(
                    practice_id=uuid4(),
                    practice_name="No-Till Conversion",
                    practice_type=ConservationPracticeType.NO_TILL,
                    description="Convert to no-till farming",
                    implementation_cost=Decimal("15.00"),  # $15 per acre (more realistic)
                    water_savings_percent=15.0,
                    soil_health_impact=SoilHealthImpact.HIGHLY_POSITIVE,
                    equipment_requirements=[],
                    implementation_time_days=5,
                    maintenance_cost_per_year=Decimal("3.00"),  # $3 per acre per year
                    effectiveness_rating=9.0
                )
            ],
            implementation_timeline="phased"
        )
        
        with patch.object(calculator, '_get_field_characteristics') as mock_field:
            mock_field.return_value = {
                "field_id": request.field_id,
                "field_size_acres": 40.0,
                "soil_type": "clay_loam",
                "slope_percent": 2.5,
                "drainage_class": "moderate",
                "climate_zone": "temperate",
                "current_irrigation_type": "sprinkler",
                "organic_matter_percent": 3.2,
                "water_source": "groundwater",
                "energy_cost_per_kwh": 0.12
            }
            
            result = await calculator.calculate_water_savings(request)
            
            # Verify savings are within expected range for no-till (10-20%)
            assert 10 <= result.savings_percentage <= 20
            
            # Verify investment grade is reasonable (no-till is often a long-term investment)
            assert result.cost_benefit_analysis["investment_grade"] in ["A", "B+", "B", "C"]

    @pytest.mark.asyncio
    async def test_soil_type_impact_on_savings(self, calculator):
        """Test that different soil types produce appropriate water savings."""
        await calculator.initialize()
        
        soil_types = ["sand", "sandy_loam", "loam", "clay_loam", "clay"]
        results = []
        
        for soil_type in soil_types:
            request = WaterSavingsRequest(
                field_id=uuid4(),
                current_water_usage=Decimal("100000"),  # 100,000 gallons for 40 acres = 2,500 gallons/acre/year
                proposed_practices=[
                    ConservationPractice(
                        practice_id=uuid4(),
                        practice_name="Cover Crops",
                        practice_type=ConservationPracticeType.COVER_CROPS,
                        description="Winter cover crop",
                        implementation_cost=Decimal("10.00"),  # $10 per acre
                        water_savings_percent=20.0,
                        soil_health_impact=SoilHealthImpact.POSITIVE,
                        equipment_requirements=[],
                        implementation_time_days=2,
                        maintenance_cost_per_year=Decimal("2.00"),  # $2 per acre per year
                        effectiveness_rating=8.0
                    )
                ],
                implementation_timeline="seasonal"
            )
            
            with patch.object(calculator, '_get_field_characteristics') as mock_field:
                mock_field.return_value = {
                    "field_id": request.field_id,
                    "field_size_acres": 40.0,
                    "soil_type": soil_type,
                    "slope_percent": 2.5,
                    "drainage_class": "moderate",
                    "climate_zone": "temperate",
                    "current_irrigation_type": "sprinkler",
                    "organic_matter_percent": 3.2,
                    "water_source": "groundwater",
                    "energy_cost_per_kwh": 0.12
                }
                
                result = await calculator.calculate_water_savings(request)
                results.append((soil_type, result.savings_percentage))
        
        # Verify that clay soils show higher savings than sandy soils
        clay_result = next(r[1] for r in results if r[0] == "clay")
        sand_result = next(r[1] for r in results if r[0] == "sand")
        
        assert clay_result > sand_result, "Clay soils should show higher water savings than sandy soils"


class TestPerformanceRequirements:
    """Performance tests for water savings calculator."""

    @pytest.fixture
    def calculator(self):
        """Create water savings calculator instance."""
        return WaterSavingsCalculator()

    @pytest.mark.asyncio
    async def test_calculation_response_time(self, calculator):
        """Test that calculations complete within acceptable time limits."""
        await calculator.initialize()
        
        import time
        
        request = WaterSavingsRequest(
            field_id=uuid4(),
            current_water_usage=Decimal("10000"),
            proposed_practices=[
                ConservationPractice(
                    practice_id=uuid4(),
                    practice_name="Cover Crops",
                    practice_type=ConservationPracticeType.COVER_CROPS,
                    description="Winter cover crop",
                    implementation_cost=Decimal("50.00"),
                    water_savings_percent=20.0,
                    soil_health_impact=SoilHealthImpact.POSITIVE,
                    equipment_requirements=[],
                    implementation_time_days=2,
                    maintenance_cost_per_year=Decimal("10.00"),
                    effectiveness_rating=8.0
                )
            ],
            implementation_timeline="seasonal"
        )
        
        with patch.object(calculator, '_get_field_characteristics') as mock_field:
            mock_field.return_value = {
                "field_id": request.field_id,
                "field_size_acres": 40.0,
                "soil_type": "clay_loam",
                "slope_percent": 2.5,
                "drainage_class": "moderate",
                "climate_zone": "temperate",
                "current_irrigation_type": "sprinkler",
                "organic_matter_percent": 3.2,
                "water_source": "groundwater",
                "energy_cost_per_kwh": 0.12
            }
            
            start_time = time.time()
            result = await calculator.calculate_water_savings(request)
            end_time = time.time()
            
            calculation_time = end_time - start_time
            
            # Verify calculation completes within 2 seconds
            assert calculation_time < 2.0, f"Calculation took {calculation_time:.2f}s, exceeds 2s limit"
            
            # Verify result is valid
            assert isinstance(result, WaterSavingsResponse)
            assert result.projected_savings > Decimal("0")
