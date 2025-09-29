"""
Comprehensive Test Suite for Soil Fertility Assessment
Tests for soil health scoring, improvement planning, and tracking.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, date, timedelta
from typing import List, Dict

from ..src.services.soil_fertility_assessment_service import (
    SoilFertilityAssessmentService, SoilHealthScore, FertilizationGoal
)
from ..src.services.soil_improvement_planning_service import SoilImprovementPlanningService
from ..src.services.soil_health_tracking_service import SoilHealthTrackingService
from ..src.models.agricultural_models import SoilTestData


class TestSoilFertilityAssessmentService:
    """Test soil fertility assessment functionality."""
    
    @pytest.fixture
    def fertility_service(self):
        """Create fertility assessment service instance."""
        return SoilFertilityAssessmentService()
    
    @pytest.fixture
    def sample_soil_test_data(self):
        """Create sample soil test data."""
        return SoilTestData(
            ph=6.2,
            organic_matter_percent=3.1,
            phosphorus_ppm=22.0,
            potassium_ppm=165.0,
            nitrogen_ppm=8.0,
            cec_meq_per_100g=18.5,
            test_date=date(2024, 3, 15),
            lab_name="Test Lab"
        )
    
    @pytest.fixture
    def sample_field_characteristics(self):
        """Create sample field characteristics."""
        return {
            'size_acres': 80.0,
            'soil_texture': 'silt_loam',
            'drainage_class': 'well_drained',
            'slope_percent': 2.0,
            'compaction_issues': False,
            'erosion_signs': 'none',
            'bulk_density': 1.3
        }
    
    @pytest.mark.asyncio
    async def test_comprehensive_soil_fertility_assessment(
        self, 
        fertility_service, 
        sample_soil_test_data, 
        sample_field_characteristics
    ):
        """Test comprehensive soil fertility assessment."""
        
        assessment = await fertility_service.assess_comprehensive_soil_fertility(
            soil_test_data=sample_soil_test_data,
            crop_type='corn',
            field_characteristics=sample_field_characteristics
        )
        
        # Verify assessment structure
        assert 'assessment_id' in assessment
        assert 'soil_health_score' in assessment
        assert 'nutrient_analysis' in assessment
        assert 'biology_assessment' in assessment
        assert 'improvement_recommendations' in assessment
        assert 'confidence_level' in assessment
        
        # Verify soil health score
        soil_health = assessment['soil_health_score']
        assert isinstance(soil_health, SoilHealthScore)
        assert 0 <= soil_health.overall_score <= 100
        assert 0 <= soil_health.nutrient_score <= 100
        assert 0 <= soil_health.biological_score <= 100
        assert 0 <= soil_health.physical_score <= 100
        assert 0 <= soil_health.chemical_score <= 100
        
        # Verify limiting factors and strengths are identified
        assert isinstance(soil_health.limiting_factors, list)
        assert isinstance(soil_health.strengths, list)
    
    def test_soil_health_score_calculation(self, fertility_service, sample_soil_test_data, sample_field_characteristics):
        """Test soil health score calculation components."""
        
        # Test nutrient score calculation
        nutrient_score = fertility_service._calculate_nutrient_score(sample_soil_test_data)
        assert 0 <= nutrient_score <= 100
        
        # Test chemical score calculation
        chemical_score = fertility_service._calculate_chemical_score(sample_soil_test_data)
        assert 0 <= chemical_score <= 100
        
        # Test physical score calculation
        physical_score = fertility_service._calculate_physical_score(
            sample_soil_test_data, sample_field_characteristics
        )
        assert 0 <= physical_score <= 100
        
        # Test biological score calculation
        biological_score = fertility_service._calculate_biological_score(sample_soil_test_data)
        assert 0 <= biological_score <= 100
    
    def test_nutrient_level_scoring(self, fertility_service):
        """Test individual nutrient level scoring."""
        
        # Test optimal range
        optimal_score = fertility_service._score_nutrient_level(25.0, (20, 40), 'phosphorus')
        assert optimal_score == 100.0
        
        # Test deficient level
        deficient_score = fertility_service._score_nutrient_level(8.0, (20, 40), 'phosphorus')
        assert deficient_score < 80.0
        
        # Test excessive level
        excessive_score = fertility_service._score_nutrient_level(100.0, (20, 40), 'phosphorus')
        assert excessive_score < 100.0
    
    def test_ph_level_scoring(self, fertility_service):
        """Test pH level scoring."""
        
        # Test optimal pH
        optimal_ph_score = fertility_service._score_ph_level(6.5)
        assert optimal_ph_score == 100.0
        
        # Test acidic pH
        acidic_ph_score = fertility_service._score_ph_level(5.0)
        assert acidic_ph_score < 70.0
        
        # Test alkaline pH
        alkaline_ph_score = fertility_service._score_ph_level(8.5)
        assert alkaline_ph_score < 70.0
    
    @pytest.mark.asyncio
    async def test_trend_analysis_with_historical_data(
        self, 
        fertility_service, 
        sample_soil_test_data, 
        sample_field_characteristics
    ):
        """Test trend analysis with historical soil test data."""
        
        # Create historical data
        historical_data = [
            SoilTestData(
                ph=6.0,
                organic_matter_percent=2.8,
                phosphorus_ppm=18.0,
                potassium_ppm=150.0,
                test_date=date(2022, 3, 15)
            ),
            SoilTestData(
                ph=6.1,
                organic_matter_percent=2.9,
                phosphorus_ppm=20.0,
                potassium_ppm=158.0,
                test_date=date(2023, 3, 15)
            )
        ]
        
        assessment = await fertility_service.assess_comprehensive_soil_fertility(
            soil_test_data=sample_soil_test_data,
            crop_type='corn',
            field_characteristics=sample_field_characteristics,
            historical_data=historical_data
        )
        
        # Verify trend analysis is included
        assert assessment['trend_analysis'] is not None
        trend_analysis = assessment['trend_analysis']
        
        # Should show improving trends for organic matter and phosphorus
        assert 'organic_matter_percent' in trend_analysis
        assert 'phosphorus_ppm' in trend_analysis


class TestSoilImprovementPlanningService:
    """Test soil improvement planning functionality."""
    
    @pytest.fixture
    def planning_service(self):
        """Create planning service instance."""
        return SoilImprovementPlanningService()
    
    @pytest.fixture
    def sample_soil_health_score(self):
        """Create sample soil health score."""
        return SoilHealthScore(
            overall_score=65.0,
            nutrient_score=70.0,
            biological_score=55.0,  # Low - needs organic matter
            physical_score=68.0,
            chemical_score=75.0,
            improvement_potential=25.0,
            limiting_factors=['low_organic_matter', 'compaction'],
            strengths=['adequate_nutrients', 'good_ph']
        )
    
    @pytest.fixture
    def sample_goals(self):
        """Create sample fertilization goals."""
        return [
            FertilizationGoal(
                goal_id='goal_1',
                goal_type='organic_matter',
                target_value=4.0,
                current_value=3.1,
                timeline_years=3,
                priority=8,
                description='Increase organic matter to 4%',
                measurement_criteria=['organic_matter_percent']
            ),
            FertilizationGoal(
                goal_id='goal_2',
                goal_type='chemical_reduction',
                target_value=25.0,  # 25% reduction
                current_value=0.0,
                timeline_years=2,
                priority=6,
                description='Reduce synthetic fertilizer use by 25%',
                measurement_criteria=['fertilizer_application_rate']
            )
        ]
    
    @pytest.mark.asyncio
    async def test_comprehensive_improvement_plan_creation(
        self, 
        planning_service, 
        sample_soil_health_score, 
        sample_goals
    ):
        """Test comprehensive improvement plan creation."""
        
        field_characteristics = {
            'size_acres': 120.0,
            'soil_texture': 'silt_loam',
            'drainage_class': 'well_drained'
        }
        
        improvement_plan = await planning_service.create_comprehensive_improvement_plan(
            farm_id='test_farm',
            field_id='test_field',
            soil_health_score=sample_soil_health_score,
            goals=sample_goals,
            field_characteristics=field_characteristics
        )
        
        # Verify plan structure
        assert improvement_plan.plan_id is not None
        assert improvement_plan.farm_id == 'test_farm'
        assert improvement_plan.field_id == 'test_field'
        assert len(improvement_plan.goals) == 2
        
        # Verify recommendations are provided
        assert len(improvement_plan.organic_amendments) > 0
        assert len(improvement_plan.cover_crop_recommendations) > 0
        assert improvement_plan.fertilizer_optimization is not None
        
        # Verify timeline is created
        assert len(improvement_plan.implementation_timeline) > 0
        
        # Verify benefits and costs are calculated
        assert len(improvement_plan.expected_benefits) > 0
        assert len(improvement_plan.cost_analysis) > 0
    
    @pytest.mark.asyncio
    async def test_organic_amendment_recommendations(
        self, 
        planning_service, 
        sample_soil_health_score, 
        sample_goals
    ):
        """Test organic amendment recommendations."""
        
        field_characteristics = {
            'size_acres': 80.0,
            'soil_texture': 'silt_loam',
            'drainage_class': 'well_drained'
        }
        
        amendments = await planning_service._recommend_organic_amendments(
            sample_soil_health_score,
            sample_goals,
            field_characteristics,
            budget_constraints={'total_budget': 5000.0}
        )
        
        # Should recommend amendments for low biological score
        assert len(amendments) > 0
        
        # Should include compost for organic matter goal
        compost_recommended = any(
            amendment.get('type') == 'compost' for amendment in amendments
        )
        assert compost_recommended
        
        # Verify amendment details
        for amendment in amendments:
            assert 'type' in amendment
            assert 'application_rate' in amendment
            assert 'cost_estimate' in amendment
            assert 'expected_benefits' in amendment
    
    @pytest.mark.asyncio
    async def test_budget_constraint_handling(
        self, 
        planning_service, 
        sample_soil_health_score, 
        sample_goals
    ):
        """Test handling of budget constraints."""
        
        field_characteristics = {
            'size_acres': 200.0,  # Large field
            'soil_texture': 'silt_loam'
        }
        
        # Test with tight budget
        tight_budget = {'total_budget': 1000.0}
        
        amendments_tight = await planning_service._recommend_organic_amendments(
            sample_soil_health_score,
            sample_goals,
            field_characteristics,
            budget_constraints=tight_budget
        )
        
        # Test with generous budget
        generous_budget = {'total_budget': 10000.0}
        
        amendments_generous = await planning_service._recommend_organic_amendments(
            sample_soil_health_score,
            sample_goals,
            field_characteristics,
            budget_constraints=generous_budget
        )
        
        # Should recommend more/better amendments with higher budget
        total_cost_tight = sum(
            amendment.get('cost_estimate', 0) for amendment in amendments_tight
        )
        total_cost_generous = sum(
            amendment.get('cost_estimate', 0) for amendment in amendments_generous
        )
        
        assert total_cost_tight <= tight_budget['total_budget']
        assert total_cost_generous <= generous_budget['total_budget']
        assert len(amendments_generous) >= len(amendments_tight)


class TestSoilHealthTrackingService:
    """Test soil health tracking functionality."""
    
    @pytest.fixture
    def tracking_service(self):
        """Create tracking service instance."""
        return SoilHealthTrackingService()
    
    @pytest.fixture
    def historical_soil_data(self):
        """Create historical soil test data."""
        return [
            SoilTestData(
                ph=6.0,
                organic_matter_percent=2.5,
                phosphorus_ppm=15.0,
                potassium_ppm=140.0,
                test_date=date(2021, 3, 15)
            ),
            SoilTestData(
                ph=6.1,
                organic_matter_percent=2.7,
                phosphorus_ppm=18.0,
                potassium_ppm=150.0,
                test_date=date(2022, 3, 15)
            ),
            SoilTestData(
                ph=6.2,
                organic_matter_percent=2.9,
                phosphorus_ppm=20.0,
                potassium_ppm=158.0,
                test_date=date(2023, 3, 15)
            )
        ]
    
    @pytest.fixture
    def current_soil_data(self):
        """Create current soil test data."""
        return SoilTestData(
            ph=6.3,
            organic_matter_percent=3.2,
            phosphorus_ppm=24.0,
            potassium_ppm=165.0,
            test_date=date(2024, 3, 15)
        )
    
    @pytest.mark.asyncio
    async def test_soil_health_progress_tracking(
        self, 
        tracking_service, 
        historical_soil_data, 
        current_soil_data
    ):
        """Test soil health progress tracking."""
        
        improvement_goals = [
            {
                'goal_type': 'organic_matter',
                'target_value': 4.0,
                'timeline_years': 3
            }
        ]
        
        progress = await tracking_service.track_soil_health_progress(
            farm_id='test_farm',
            field_id='test_field',
            historical_data=historical_soil_data,
            current_data=current_soil_data,
            improvement_goals=improvement_goals
        )
        
        # Verify progress tracking structure
        assert 'tracking_id' in progress
        assert 'trends' in progress
        assert 'alerts' in progress
        assert 'goal_progress' in progress
        assert 'practice_effectiveness' in progress
        assert 'overall_trajectory' in progress
        
        # Verify trends are calculated
        trends = progress['trends']
        assert len(trends) > 0
        
        # Should detect improving trend in organic matter
        om_trend = next(
            (trend for trend in trends if trend.parameter == 'organic_matter_percent'), 
            None
        )
        assert om_trend is not None
        assert om_trend.trend_direction == 'improving'
        assert om_trend.rate_of_change > 0
    
    def test_time_series_creation(self, tracking_service, historical_soil_data, current_soil_data):
        """Test time series data creation."""
        
        time_series = tracking_service._create_time_series(
            historical_soil_data, current_soil_data
        )
        
        # Verify time series structure
        assert 'ph' in time_series
        assert 'organic_matter_percent' in time_series
        assert 'phosphorus_ppm' in time_series
        assert 'potassium_ppm' in time_series
        
        # Verify data points
        assert len(time_series['organic_matter_percent']) == 4  # 3 historical + 1 current
        
        # Verify chronological order
        om_data = time_series['organic_matter_percent']
        dates = [point[0] for point in om_data]
        assert dates == sorted(dates)  # Should be in chronological order
    
    @pytest.mark.asyncio
    async def test_trend_calculation(self, tracking_service):
        """Test parameter trend calculation."""
        
        # Create test data with clear improving trend
        test_data = [
            (datetime(2021, 3, 15), 2.5),
            (datetime(2022, 3, 15), 2.7),
            (datetime(2023, 3, 15), 2.9),
            (datetime(2024, 3, 15), 3.2)
        ]
        
        trend = await tracking_service._calculate_parameter_trend(
            'organic_matter_percent', test_data
        )
        
        assert trend is not None
        assert trend.parameter == 'organic_matter_percent'
        assert trend.trend_direction == 'improving'
        assert trend.rate_of_change > 0
        assert 0 <= trend.confidence_level <= 1
        assert trend.projected_value_1yr > trend.current_value
    
    @pytest.mark.asyncio
    async def test_alert_generation(self, tracking_service):
        """Test soil health alert generation."""
        
        # Create declining trend data
        declining_data = [
            (datetime(2021, 3, 15), 6.5),
            (datetime(2022, 3, 15), 6.2),
            (datetime(2023, 3, 15), 5.9),
            (datetime(2024, 3, 15), 5.6)
        ]
        
        trend = await tracking_service._calculate_parameter_trend('ph', declining_data)
        
        # Should detect declining trend
        assert trend.trend_direction == 'declining'
        assert trend.rate_of_change < 0
        
        # This would trigger an alert in the full implementation


class TestSoilFertilityIntegration:
    """Integration tests for complete soil fertility workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_soil_fertility_workflow(self):
        """Test complete workflow from assessment to tracking."""
        
        # Initialize services
        fertility_service = SoilFertilityAssessmentService()
        planning_service = SoilImprovementPlanningService()
        tracking_service = SoilHealthTrackingService()
        
        # Step 1: Initial soil assessment
        soil_test_data = SoilTestData(
            ph=6.0,
            organic_matter_percent=2.8,
            phosphorus_ppm=18.0,
            potassium_ppm=145.0,
            test_date=date(2024, 3, 15)
        )
        
        field_characteristics = {
            'size_acres': 100.0,
            'soil_texture': 'silt_loam',
            'drainage_class': 'well_drained'
        }
        
        assessment = await fertility_service.assess_comprehensive_soil_fertility(
            soil_test_data=soil_test_data,
            crop_type='corn',
            field_characteristics=field_characteristics
        )
        
        assert assessment is not None
        assert 'soil_health_score' in assessment
        
        # Step 2: Create improvement goals
        goals = [
            FertilizationGoal(
                goal_id='integration_goal_1',
                goal_type='organic_matter',
                target_value=3.5,
                current_value=2.8,
                timeline_years=2,
                priority=8,
                description='Increase organic matter',
                measurement_criteria=['organic_matter_percent']
            )
        ]
        
        # Step 3: Create improvement plan
        improvement_plan = await planning_service.create_comprehensive_improvement_plan(
            farm_id='integration_farm',
            field_id='integration_field',
            soil_health_score=assessment['soil_health_score'],
            goals=goals,
            field_characteristics=field_characteristics
        )
        
        assert improvement_plan is not None
        assert len(improvement_plan.organic_amendments) > 0
        assert len(improvement_plan.implementation_timeline) > 0
        
        # Step 4: Simulate progress tracking after 1 year
        updated_soil_data = SoilTestData(
            ph=6.1,
            organic_matter_percent=3.0,  # Improved
            phosphorus_ppm=20.0,
            potassium_ppm=150.0,
            test_date=date(2025, 3, 15)
        )
        
        progress = await tracking_service.track_soil_health_progress(
            farm_id='integration_farm',
            field_id='integration_field',
            historical_data=[soil_test_data],
            current_data=updated_soil_data,
            improvement_goals=[goal.dict() for goal in goals]
        )
        
        assert progress is not None
        assert 'trends' in progress
        assert len(progress['trends']) > 0
        
        print("Integration test completed successfully!")
        print(f"Initial soil health score: {assessment['soil_health_score'].overall_score}")
        print(f"Improvement plan created with {len(improvement_plan.organic_amendments)} amendments")
        print(f"Progress tracking shows {len(progress['trends'])} parameter trends")


if __name__ == "__main__":
    # Run specific test for debugging
    import asyncio
    
    async def run_integration_test():
        test_instance = TestSoilFertilityIntegration()
        await test_instance.test_complete_soil_fertility_workflow()
    
    asyncio.run(run_integration_test())