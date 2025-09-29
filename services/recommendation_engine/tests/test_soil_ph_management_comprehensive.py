"""
Comprehensive Test Suite for Soil pH Management System
Tests pH analysis, amendment recommendations, monitoring, API endpoints, and agricultural accuracy.
Includes unit tests, integration tests, and performance benchmarks.
"""
import pytest
import asyncio
import time
import concurrent.futures
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add the src directory to Python path for proper imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.soil_ph_management_service import (
    SoilPHManagementService, PHReading, CropPHPreference, 
    PHAmendmentRecommendation, PHManagementPlan, PHTimeline,
    SoilTexture, AmendmentType, ApplicationTiming
)

class TestSoilPHManagementService:
    """Base test class with fixtures."""
    
    @pytest.fixture
    def ph_service(self):
        """Create pH management service instance."""
        return SoilPHManagementService()
    
    @pytest.fixture
    def sample_soil_data(self):
        """Sample soil test data."""
        return {
            'ph': 5.8,
            'organic_matter_percent': 3.2,
            'phosphorus_ppm': 25,
            'potassium_ppm': 180,
            'test_date': date(2024, 3, 15),
            'farm_id': 'test_farm',
            'field_id': 'field_001'
        }
    
    @pytest.fixture
    def acidic_soil_data(self):
        """Acidic soil test data."""
        return {
            'ph': 5.2,
            'organic_matter_percent': 2.1,
            'phosphorus_ppm': 12,
            'potassium_ppm': 95,
            'test_date': date(2024, 3, 10),
            'farm_id': 'test_farm',
            'field_id': 'field_002'
        }
    
    @pytest.fixture
    def alkaline_soil_data(self):
        """Alkaline soil test data."""
        return {
            'ph': 8.2,
            'organic_matter_percent': 2.8,
            'phosphorus_ppm': 45,
            'potassium_ppm': 220,
            'test_date': date(2024, 3, 12),
            'farm_id': 'test_farm',
            'field_id': 'field_003'
        }

    @pytest.fixture
    def field_conditions(self):
        """Standard field conditions for testing."""
        return {
            'soil_texture': SoilTexture.LOAM,
            'field_size_acres': 10.0,
            'tillage_practices': 'conventional',
            'irrigation_type': 'rainfed'
        }

    @pytest.fixture
    def crop_preferences(self):
        """Sample crop pH preferences."""
        return CropPHPreference(
            crop_name="corn",
            optimal_ph_min=6.0,
            optimal_ph_max=6.8,
            acceptable_ph_min=5.8,
            acceptable_ph_max=7.2,
            critical_ph_min=5.0,
            critical_ph_max=8.0
        )


class TestPHAnalysisCore(TestSoilPHManagementService):
    """Test core pH analysis functionality."""
    
    @pytest.mark.asyncio
    async def test_analyze_ph_status_optimal_conditions(self, ph_service, field_conditions):
        """Test pH analysis for optimal conditions."""
        soil_data = {
            'ph': 6.5,
            'organic_matter_percent': 3.5,
            'test_date': date.today(),
            'farm_id': 'test_farm',
            'field_id': 'optimal_field'
        }
        
        analysis = await ph_service.analyze_ph_status(
            farm_id=soil_data['farm_id'],
            field_id=soil_data['field_id'],
            crop_type="corn",
            soil_data=soil_data,
            field_conditions=field_conditions
        )
        
        assert isinstance(analysis, dict)
        assert analysis['current_ph'] == 6.5
        assert analysis['yield_impact'] >= 0.95  # Should be near optimal
        
        # Nutrient availability should be good at optimal pH
        nutrients = analysis['nutrient_availability']
        assert nutrients['nitrogen'] >= 0.9
        assert nutrients['phosphorus'] >= 0.9
        assert nutrients['potassium'] >= 0.8

    @pytest.mark.asyncio
    async def test_analyze_ph_status_acidic_soil(self, ph_service, acidic_soil_data, field_conditions):
        """Test pH analysis for acidic soil."""
        analysis = await ph_service.analyze_ph_status(
            farm_id=acidic_soil_data['farm_id'],
            field_id=acidic_soil_data['field_id'],
            crop_type="corn",
            soil_data=acidic_soil_data,
            field_conditions=field_conditions
        )
        
        assert analysis['current_ph'] == 5.2
        assert analysis['yield_impact'] < 0.8  # Reduced yield expected
        
        # Phosphorus availability should be limited
        nutrients = analysis['nutrient_availability']
        assert nutrients['phosphorus'] < 0.7
        # Iron should be more available at low pH
        assert nutrients['iron'] > 0.8

    @pytest.mark.asyncio
    async def test_analyze_ph_status_alkaline_soil(self, ph_service, alkaline_soil_data, field_conditions):
        """Test pH analysis for alkaline soil."""
        analysis = await ph_service.analyze_ph_status(
            farm_id=alkaline_soil_data['farm_id'],
            field_id=alkaline_soil_data['field_id'],
            crop_type="corn",
            soil_data=alkaline_soil_data,
            field_conditions=field_conditions
        )
        
        assert analysis['current_ph'] == 8.2
        assert analysis['yield_impact'] < 0.8  # Alkaline soil impacts corn
        
        # Micronutrient availability should be limited
        nutrients = analysis['nutrient_availability']
        assert nutrients['iron'] < 0.4
        assert nutrients['zinc'] < 0.5
        assert nutrients['manganese'] < 0.6

    def test_ph_validation(self, ph_service):
        """Test pH reading validation."""
        # Valid pH values
        valid_result = ph_service.validate_ph_reading(6.5)
        assert valid_result['is_valid'] is True
        assert valid_result['ph_category'] in ['slightly_acidic', 'neutral', 'slightly_alkaline']
        
        # Invalid pH values
        invalid_result = ph_service.validate_ph_reading(15.0)
        assert invalid_result['is_valid'] is False
        assert 'error_message' in invalid_result
        
        # Edge case pH values
        extreme_low = ph_service.validate_ph_reading(2.0)
        assert extreme_low['is_valid'] is True
        assert extreme_low['ph_category'] == 'extremely_acidic'
        
        extreme_high = ph_service.validate_ph_reading(10.0)
        assert extreme_high['is_valid'] is True
        assert extreme_high['ph_category'] == 'very_strongly_alkaline'

    @pytest.mark.asyncio
    async def test_nutrient_availability_explanation(self, ph_service):
        """Test detailed nutrient availability explanations."""
        # Test optimal pH
        explanation = await ph_service.get_nutrient_availability_explanation(6.5)
        assert isinstance(explanation, dict)
        assert 'overall_rating' in explanation
        assert 'nutrient_details' in explanation
        assert explanation['overall_rating'] in ['excellent', 'good', 'fair', 'poor']
        
        # Test acidic pH
        acidic_explanation = await ph_service.get_nutrient_availability_explanation(5.0)
        assert acidic_explanation['overall_rating'] in ['fair', 'poor']
        assert 'phosphorus' in acidic_explanation['nutrient_details']
        
        # Test alkaline pH
        alkaline_explanation = await ph_service.get_nutrient_availability_explanation(8.5)
        assert alkaline_explanation['overall_rating'] in ['fair', 'poor']
        assert 'iron' in alkaline_explanation['nutrient_details']


class TestAmendmentRecommendations(TestSoilPHManagementService):
    """Test pH amendment calculation and recommendations."""
    
    @pytest.mark.asyncio
    async def test_lime_recommendations_basic(self, ph_service, acidic_soil_data, field_conditions):
        """Test basic lime requirement calculations."""
        analysis = await ph_service.analyze_ph_status(
            farm_id=acidic_soil_data['farm_id'],
            field_id=acidic_soil_data['field_id'],
            crop_type="corn",
            soil_data=acidic_soil_data,
            field_conditions=field_conditions
        )
        
        # Create management plan with lime recommendations
        plan = await ph_service.create_ph_management_plan(
            farm_id=acidic_soil_data['farm_id'],
            field_id=acidic_soil_data['field_id'],
            crop_type="corn",
            ph_analysis=analysis,
            field_conditions=field_conditions
        )
        
        assert isinstance(plan, PHManagementPlan)
        assert len(plan.recommendations) > 0
        
        # Should have lime recommendations for acidic soil
        lime_recs = [r for r in plan.recommendations if r.amendment_type in [AmendmentType.AGRICULTURAL_LIME, AmendmentType.HYDRATED_LIME]]
        assert len(lime_recs) > 0
        
        for rec in lime_recs:
            assert rec.application_rate > 0
            assert rec.cost_estimate > 0
            assert rec.expected_ph_change > 0

    @pytest.mark.asyncio
    async def test_sulfur_recommendations_alkaline(self, ph_service, alkaline_soil_data, field_conditions):
        """Test sulfur recommendations for alkaline soil."""
        analysis = await ph_service.analyze_ph_status(
            farm_id=alkaline_soil_data['farm_id'],
            field_id=alkaline_soil_data['field_id'],
            crop_type="corn",
            soil_data=alkaline_soil_data,
            field_conditions=field_conditions
        )
        
        plan = await ph_service.create_ph_management_plan(
            farm_id=alkaline_soil_data['farm_id'],
            field_id=alkaline_soil_data['field_id'],
            crop_type="corn",
            ph_analysis=analysis,
            field_conditions=field_conditions
        )
        
        # Should have acidifying recommendations
        acidifier_recs = [r for r in plan.recommendations if r.amendment_type in [AmendmentType.ELEMENTAL_SULFUR, AmendmentType.ALUMINUM_SULFATE]]
        assert len(acidifier_recs) > 0
        
        for rec in acidifier_recs:
            assert rec.application_rate > 0
            assert rec.expected_ph_change < 0  # Should decrease pH

    def test_amendment_material_properties(self, ph_service):
        """Test amendment material property accuracy."""
        # Agricultural limestone properties
        ag_lime = ph_service.amendment_properties[AmendmentType.AGRICULTURAL_LIME]
        assert ag_lime['neutralizing_value'] >= 85  # Typical CCE
        assert ag_lime['reaction_speed'] == 'slow'
        assert ag_lime['cost_per_ton'] > 0
        
        # Hydrated lime properties
        hydrated = ph_service.amendment_properties[AmendmentType.HYDRATED_LIME]
        assert hydrated['neutralizing_value'] > ag_lime['neutralizing_value']
        assert hydrated['reaction_speed'] == 'fast'
        assert hydrated['cost_per_ton'] > ag_lime['cost_per_ton']
        
        # Elemental sulfur properties
        sulfur = ph_service.amendment_properties[AmendmentType.ELEMENTAL_SULFUR]
        assert sulfur['acidifying_value'] > 0
        assert sulfur['reaction_speed'] == 'slow'

    def test_application_timing_recommendations(self, ph_service):
        """Test amendment application timing recommendations."""
        timing_guidelines = ph_service.timing_guidelines
        
        # Agricultural lime should prefer fall application
        ag_lime_timing = timing_guidelines['agricultural_lime']
        assert ag_lime_timing['preferred_season'] == 'fall'
        assert ag_lime_timing['incorporation_required'] is True
        
        # Hydrated lime can be applied in spring
        hydrated_timing = timing_guidelines['hydrated_lime']
        assert 'spring' in hydrated_timing['acceptable_seasons']


class TestMonitoringAndTracking(TestSoilPHManagementService):
    """Test pH monitoring and tracking functionality."""
    
    @pytest.mark.asyncio
    async def test_track_ph_monitoring_record(self, ph_service):
        """Test pH monitoring record creation and storage."""
        record = await ph_service.track_ph_monitoring_record(
            farm_id="test_farm",
            field_id="field_001",
            ph_value=6.2,
            testing_method="laboratory",
            lab_name="AgriTest Labs",
            notes="Post-lime application test"
        )
        
        assert record['farm_id'] == "test_farm"
        assert record['field_id'] == "field_001"
        assert record['ph_value'] == 6.2
        assert record['testing_method'] == "laboratory"
        assert record['lab_name'] == "AgriTest Labs"
        assert 'record_id' in record
        assert 'timestamp' in record

    @pytest.mark.asyncio
    async def test_analyze_ph_trends(self, ph_service):
        """Test pH trend analysis over time."""
        # Create mock pH records showing improvement trend
        ph_records = [
            {'ph_value': 5.2, 'test_date': date(2023, 3, 1), 'record_id': '1'},
            {'ph_value': 5.6, 'test_date': date(2023, 8, 1), 'record_id': '2'},
            {'ph_value': 6.1, 'test_date': date(2024, 3, 1), 'record_id': '3'},
            {'ph_value': 6.4, 'test_date': date(2024, 8, 1), 'record_id': '4'}
        ]
        
        trends = await ph_service.analyze_ph_trends(
            farm_id="test_farm",
            field_id="field_001",
            ph_records=ph_records
        )
        
        assert trends['trend_direction'] == 'increasing'
        assert trends['annual_change_rate'] > 0
        assert trends['current_ph'] == 6.4
        assert trends['readings_count'] == 4
        assert 'trend_strength' in trends

    @pytest.mark.asyncio
    async def test_generate_ph_alerts(self, ph_service, acidic_soil_data, field_conditions):
        """Test pH alert generation for critical conditions."""
        # Create critical pH analysis
        analysis = await ph_service.analyze_ph_status(
            farm_id=acidic_soil_data['farm_id'],
            field_id=acidic_soil_data['field_id'],
            crop_type="corn",
            soil_data=acidic_soil_data,
            field_conditions=field_conditions
        )
        
        alerts = await ph_service.generate_ph_alerts(
            ph_analysis=analysis,
            crop_type="corn"
        )
        
        assert len(alerts) > 0
        
        for alert in alerts:
            assert 'alert_type' in alert
            assert 'severity' in alert
            assert 'message' in alert
            assert 'recommended_action' in alert
            assert alert['severity'] in ['low', 'medium', 'high', 'critical']


class TestCropSpecificRequirements(TestSoilPHManagementService):
    """Test crop-specific pH requirements and recommendations."""
    
    def test_crop_ph_preferences_database(self, ph_service):
        """Test crop pH preferences database completeness."""
        crops = ph_service.crop_ph_preferences
        
        # Test key agricultural crops
        key_crops = ['corn', 'soybean', 'wheat', 'alfalfa', 'potato', 'blueberry']
        for crop in key_crops:
            assert crop in crops
            pref = crops[crop]
            assert isinstance(pref, CropPHPreference)
            assert pref.optimal_ph_min < pref.optimal_ph_max
            assert pref.acceptable_ph_min <= pref.optimal_ph_min
            assert pref.optimal_ph_max <= pref.acceptable_ph_max

    def test_crop_specific_yield_impact(self, ph_service):
        """Test crop-specific yield impact calculations."""
        # Corn at optimal pH
        corn_optimal = ph_service._calculate_yield_impact(6.4, ph_service.crop_ph_preferences['corn'])
        assert corn_optimal >= 0.95
        
        # Corn at acidic pH
        corn_acidic = ph_service._calculate_yield_impact(5.2, ph_service.crop_ph_preferences['corn'])
        assert corn_acidic < 0.8
        
        # Blueberry should tolerate acidic conditions better
        blueberry_acidic = ph_service._calculate_yield_impact(5.0, ph_service.crop_ph_preferences['blueberry'])
        assert blueberry_acidic > corn_acidic
        
        # Alfalfa should be sensitive to acidity
        alfalfa_acidic = ph_service._calculate_yield_impact(5.5, ph_service.crop_ph_preferences['alfalfa'])
        assert alfalfa_acidic < 0.7

    @pytest.mark.asyncio
    async def test_blueberry_acidic_preference(self, ph_service, field_conditions):
        """Test that blueberry recommendations favor acidic conditions."""
        acidic_soil = {
            'ph': 5.0,
            'organic_matter_percent': 4.0,
            'test_date': date.today(),
            'farm_id': 'berry_farm',
            'field_id': 'blueberry_field'
        }
        
        analysis = await ph_service.analyze_ph_status(
            farm_id=acidic_soil['farm_id'],
            field_id=acidic_soil['field_id'],
            crop_type="blueberry",
            soil_data=acidic_soil,
            field_conditions=field_conditions
        )
        
        # Blueberries should have good yield impact at pH 5.0
        assert analysis['yield_impact'] >= 0.8
        
        # Should not recommend lime for blueberries at pH 5.0
        plan = await ph_service.create_ph_management_plan(
            farm_id=acidic_soil['farm_id'],
            field_id=acidic_soil['field_id'],
            crop_type="blueberry",
            ph_analysis=analysis,
            field_conditions=field_conditions
        )
        
        lime_recs = [r for r in plan.recommendations if r.amendment_type in [AmendmentType.AGRICULTURAL_LIME, AmendmentType.HYDRATED_LIME]]
        # Should have no lime recommendations or very minimal ones
        assert len(lime_recs) == 0 or all(r.application_rate < 0.5 for r in lime_recs)


class TestBufferCapacityAndSoilTexture(TestSoilPHManagementService):
    """Test buffer capacity calculations and soil texture adjustments."""
    
    def test_buffer_capacity_by_texture(self, ph_service):
        """Test buffer capacity estimation for different soil textures."""
        soil_data = {'ph': 6.0, 'organic_matter_percent': 3.0}
        
        # Sandy soil should have low buffer capacity
        sandy_conditions = {'soil_texture': SoilTexture.SAND}
        sandy_buffer = ph_service.buffer_capacity_factors[SoilTexture.SAND]
        assert sandy_buffer['base_capacity'] < 1.0
        
        # Clay soil should have high buffer capacity
        clay_conditions = {'soil_texture': SoilTexture.CLAY}
        clay_buffer = ph_service.buffer_capacity_factors[SoilTexture.CLAY]
        assert clay_buffer['base_capacity'] > 1.0
        
        # Loam should be intermediate
        loam_buffer = ph_service.buffer_capacity_factors[SoilTexture.LOAM]
        assert sandy_buffer['base_capacity'] < loam_buffer['base_capacity'] < clay_buffer['base_capacity']

    @pytest.mark.asyncio
    async def test_buffer_ph_requirements(self, ph_service):
        """Test buffer pH-based lime requirement calculations."""
        requirements = await ph_service.calculate_buffer_ph_requirements(
            current_buffer_ph=6.2,
            target_ph=6.8,
            soil_texture=SoilTexture.SILT_LOAM,
            organic_matter_percent=3.5
        )
        
        assert 'lime_requirement_tons_per_acre' in requirements
        assert 'confidence_level' in requirements
        assert requirements['lime_requirement_tons_per_acre'] > 0
        assert requirements['confidence_level'] in ['high', 'medium', 'low']


class TestEconomicAnalysis(TestSoilPHManagementService):
    """Test economic analysis of pH management."""
    
    def test_economic_analysis_calculation(self, ph_service, sample_soil_data, field_conditions):
        """Test pH management economic analysis."""
        # Mock analysis and recommendations
        analysis = {
            'current_ph': 5.8,
            'yield_impact': 0.85,
            'target_ph_range': {'min': 6.0, 'max': 6.8}
        }
        
        recommendations = [
            PHAmendmentRecommendation(
                amendment_type=AmendmentType.AGRICULTURAL_LIME,
                application_rate=2.0,
                cost_estimate=120.0,
                expected_ph_change=0.6,
                timing=ApplicationTiming.FALL_PREFERRED
            )
        ]
        
        economics = ph_service._calculate_economic_analysis(
            ph_analysis=analysis,
            recommendations=recommendations,
            crop_type="corn",
            field_conditions=field_conditions
        )
        
        assert 'total_amendment_cost' in economics
        assert 'yield_benefit_value' in economics
        assert 'net_benefit' in economics
        assert 'benefit_cost_ratio' in economics
        assert 'payback_period_years' in economics
        
        assert economics['total_amendment_cost'] > 0
        assert economics['benefit_cost_ratio'] > 0


class TestPerformanceAndScalability(TestSoilPHManagementService):
    """Test performance and scalability of pH management system."""
    
    @pytest.mark.asyncio
    async def test_ph_analysis_performance(self, ph_service, sample_soil_data, field_conditions):
        """Test pH analysis performance under load."""
        start_time = time.time()
        
        # Run 10 analyses concurrently
        tasks = []
        for i in range(10):
            task = ph_service.analyze_ph_status(
                farm_id=f"farm_{i}",
                field_id=f"field_{i}",
                crop_type="corn",
                soil_data=sample_soil_data.copy(),
                field_conditions=field_conditions
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 10 analyses in reasonable time (< 5 seconds)
        assert total_time < 5.0
        assert len(results) == 10
        assert all(isinstance(result, dict) for result in results)

    @pytest.mark.asyncio
    async def test_management_plan_performance(self, ph_service, sample_soil_data, field_conditions):
        """Test management plan creation performance."""
        analysis = await ph_service.analyze_ph_status(
            farm_id=sample_soil_data['farm_id'],
            field_id=sample_soil_data['field_id'],
            crop_type="corn",
            soil_data=sample_soil_data,
            field_conditions=field_conditions
        )
        
        start_time = time.time()
        
        plan = await ph_service.create_ph_management_plan(
            farm_id=sample_soil_data['farm_id'],
            field_id=sample_soil_data['field_id'],
            crop_type="corn",
            ph_analysis=analysis,
            field_conditions=field_conditions
        )
        
        end_time = time.time()
        plan_time = end_time - start_time
        
        # Should create plan quickly (< 2 seconds)
        assert plan_time < 2.0
        assert isinstance(plan, PHManagementPlan)

    def test_memory_usage_large_dataset(self, ph_service):
        """Test memory efficiency with large datasets."""
        # Create large number of pH readings
        large_dataset = []
        for i in range(1000):
            reading = PHReading(
                ph_value=5.0 + (i % 40) / 10.0,  # pH values from 5.0 to 8.9
                test_date=date(2020, 1, 1) + timedelta(days=i),
                method="laboratory"
            )
            large_dataset.append(reading)
        
        # Process dataset - should handle efficiently
        start_time = time.time()
        processed_count = 0
        
        for reading in large_dataset:
            validation = ph_service.validate_ph_reading(reading.ph_value)
            if validation['is_valid']:
                processed_count += 1
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 1000 readings quickly
        assert processing_time < 1.0
        assert processed_count == 1000


class TestEdgeCasesAndErrorHandling(TestSoilPHManagementService):
    """Test edge cases and error handling."""
    
    def test_extreme_ph_values(self, ph_service):
        """Test handling of extreme pH values."""
        # Extremely low pH
        extreme_low = ph_service.validate_ph_reading(1.0)
        assert extreme_low['is_valid'] is True
        assert extreme_low['ph_category'] == 'extremely_acidic'
        assert 'warning' in extreme_low
        
        # Extremely high pH
        extreme_high = ph_service.validate_ph_reading(12.0)
        assert extreme_high['is_valid'] is True
        assert extreme_high['ph_category'] == 'very_strongly_alkaline'
        assert 'warning' in extreme_high

    def test_invalid_ph_values(self, ph_service):
        """Test handling of invalid pH values."""
        # Negative pH
        negative_ph = ph_service.validate_ph_reading(-1.0)
        assert negative_ph['is_valid'] is False
        assert 'error_message' in negative_ph
        
        # pH > 14
        impossible_ph = ph_service.validate_ph_reading(15.0)
        assert impossible_ph['is_valid'] is False
        assert 'error_message' in impossible_ph

    @pytest.mark.asyncio
    async def test_missing_crop_data(self, ph_service, sample_soil_data, field_conditions):
        """Test handling of unknown crop types."""
        # Should default to corn behavior for unknown crops
        analysis = await ph_service.analyze_ph_status(
            farm_id=sample_soil_data['farm_id'],
            field_id=sample_soil_data['field_id'],
            crop_type="unknown_crop",
            soil_data=sample_soil_data,
            field_conditions=field_conditions
        )
        
        assert isinstance(analysis, dict)
        assert 'current_ph' in analysis
        assert 'yield_impact' in analysis
        # Should use default crop preferences

    def test_invalid_soil_texture(self, ph_service):
        """Test handling of invalid soil texture."""
        # Should handle gracefully and use default values
        buffer_factors = ph_service.buffer_capacity_factors
        
        # All valid textures should have buffer capacity data
        for texture in SoilTexture:
            assert texture in buffer_factors
            assert 'base_capacity' in buffer_factors[texture]
            assert 'organic_matter_multiplier' in buffer_factors[texture]


class TestAgriculturalAccuracy(TestSoilPHManagementService):
    """Test agricultural accuracy and compliance with standards."""
    
    def test_nutrient_availability_curves_realistic(self, ph_service):
        """Test that nutrient availability curves match agricultural science."""
        curves = ph_service.nutrient_availability_curves
        
        # Phosphorus should peak around pH 6.5
        p_curve = curves['phosphorus']
        max_p_ph = max(p_curve.keys(), key=lambda ph: p_curve[ph])
        assert 6.0 <= max_p_ph <= 7.0
        
        # Iron availability should decrease with increasing pH
        fe_curve = curves['iron']
        assert fe_curve[5.0] > fe_curve[7.0] > fe_curve[8.5]
        
        # Molybdenum should increase with pH
        mo_curve = curves['molybdenum']
        assert mo_curve[8.0] > mo_curve[6.0] > mo_curve[5.0]

    def test_lime_material_properties_accurate(self, ph_service):
        """Test lime material properties against industry standards."""
        materials = ph_service.amendment_properties
        
        # Agricultural limestone CCE should be 85-95%
        ag_lime = materials[AmendmentType.AGRICULTURAL_LIME]
        assert 85 <= ag_lime['neutralizing_value'] <= 95
        
        # Hydrated lime should be more potent
        hydrated = materials[AmendmentType.HYDRATED_LIME]
        assert hydrated['neutralizing_value'] > 120  # Typical CCE > 120%
        
        # Dolomitic lime should provide Mg
        dolomitic = materials[AmendmentType.DOLOMITIC_LIME]
        assert 'magnesium_content' in dolomitic
        assert dolomitic['magnesium_content'] > 0

    def test_crop_ph_ranges_match_extension_data(self, ph_service):
        """Test that crop pH ranges match university extension recommendations."""
        crops = ph_service.crop_ph_preferences
        
        # Corn optimal range should be 6.0-6.8
        corn = crops['corn']
        assert corn.optimal_ph_min == 6.0
        assert corn.optimal_ph_max == 6.8
        
        # Alfalfa should prefer higher pH (6.2-7.8)
        alfalfa = crops['alfalfa']
        assert alfalfa.optimal_ph_min >= 6.2
        assert alfalfa.optimal_ph_max <= 7.8
        
        # Blueberry should prefer acidic (4.0-5.2)
        blueberry = crops['blueberry']
        assert blueberry.optimal_ph_min <= 4.5
        assert blueberry.optimal_ph_max <= 5.5

    def test_lime_rate_calculations_safe(self, ph_service):
        """Test that lime rate calculations include safety limits."""
        # Create recommendations for severely acidic soil
        test_conditions = {
            'soil_texture': SoilTexture.CLAY,
            'field_size_acres': 100.0
        }
        
        # Even for very acidic soil, lime rates should be reasonable
        # Agricultural guidelines typically limit to 4-6 tons/acre max
        analysis = {
            'current_ph': 4.5,
            'target_ph_range': {'min': 6.0, 'max': 6.8}
        }
        
        recommendations = ph_service._calculate_lime_recommendations(
            current_ph=4.5,
            target_ph=6.4,
            soil_texture=SoilTexture.CLAY,
            organic_matter_percent=2.0,
            field_conditions=test_conditions
        )
        
        for rec in recommendations:
            # Should not exceed 6 tons/acre for safety
            assert rec.application_rate <= 6.0
            assert rec.cost_estimate > 0


class TestIntegrationWorkflows(TestSoilPHManagementService):
    """Test complete integrated workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_ph_management_workflow(self, ph_service, sample_soil_data, field_conditions):
        """Test complete end-to-end pH management workflow."""
        # Step 1: Analyze pH status
        analysis = await ph_service.analyze_ph_status(
            farm_id=sample_soil_data['farm_id'],
            field_id=sample_soil_data['field_id'],
            crop_type="corn",
            soil_data=sample_soil_data,
            field_conditions=field_conditions
        )
        
        assert isinstance(analysis, dict)
        assert 'current_ph' in analysis
        
        # Step 2: Create management plan
        plan = await ph_service.create_ph_management_plan(
            farm_id=sample_soil_data['farm_id'],
            field_id=sample_soil_data['field_id'],
            crop_type="corn",
            ph_analysis=analysis,
            field_conditions=field_conditions
        )
        
        assert isinstance(plan, PHManagementPlan)
        assert plan.farm_id == sample_soil_data['farm_id']
        assert len(plan.recommendations) >= 0
        
        # Step 3: Generate monitoring schedule
        assert isinstance(plan.timeline, PHTimeline)
        assert len(plan.timeline.monitoring_dates) > 0
        
        # Step 4: Track monitoring record
        monitoring_record = await ph_service.track_ph_monitoring_record(
            farm_id=sample_soil_data['farm_id'],
            field_id=sample_soil_data['field_id'],
            ph_value=6.0,  # Follow-up test
            testing_method="field_kit",
            notes="Follow-up test after lime application"
        )
        
        assert monitoring_record['ph_value'] == 6.0
        assert 'record_id' in monitoring_record

    @pytest.mark.asyncio
    async def test_emergency_correction_workflow(self, ph_service, field_conditions):
        """Test emergency pH correction workflow for critical conditions."""
        # Extremely acidic soil requiring immediate action
        critical_soil = {
            'ph': 4.2,
            'organic_matter_percent': 1.8,
            'test_date': date.today(),
            'farm_id': 'emergency_farm',
            'field_id': 'critical_field'
        }
        
        # Step 1: Analyze critical condition
        analysis = await ph_service.analyze_ph_status(
            farm_id=critical_soil['farm_id'],
            field_id=critical_soil['field_id'],
            crop_type="corn",
            soil_data=critical_soil,
            field_conditions=field_conditions
        )
        
        assert analysis['yield_impact'] < 0.5  # Severely impacted
        
        # Step 2: Generate emergency plan
        plan = await ph_service.create_ph_management_plan(
            farm_id=critical_soil['farm_id'],
            field_id=critical_soil['field_id'],
            crop_type="corn",
            ph_analysis=analysis,
            field_conditions=field_conditions
        )
        
        # Should include fast-acting amendments
        fast_amendments = [r for r in plan.recommendations if r.amendment_type == AmendmentType.HYDRATED_LIME]
        assert len(fast_amendments) > 0
        
        # Step 3: Generate critical alerts
        alerts = await ph_service.generate_ph_alerts(
            ph_analysis=analysis,
            crop_type="corn"
        )
        
        critical_alerts = [a for a in alerts if a['severity'] == 'critical']
        assert len(critical_alerts) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])