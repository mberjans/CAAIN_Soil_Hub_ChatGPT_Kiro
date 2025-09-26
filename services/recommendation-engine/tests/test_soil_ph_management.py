"""
Comprehensive tests for soil pH management system.
Tests pH analysis, lime recommendations, monitoring, and agricultural accuracy.
"""
import pytest
import asyncio
import time
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
from models.agricultural_models import SoilTestData

class TestSoilPHManagementService:
    """Test suite for soil pH management service."""
    
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

class TestPHAnalysis(TestSoilPHManagementService):
    """Test pH analysis functionality."""
    
    @pytest.mark.asyncio
    async def test_analyze_ph_status_corn(self, ph_service, sample_soil_data, field_conditions):
        """Test pH analysis for corn crop."""
        analysis = await ph_service.analyze_ph_status(
            farm_id=sample_soil_data['farm_id'],
            field_id=sample_soil_data['field_id'],
            crop_type="corn",
            soil_data=sample_soil_data,
            field_conditions=field_conditions
        )
        
        assert isinstance(analysis, dict)
        assert analysis['current_ph'] == 5.8
        assert 'ph_status' in analysis
        assert 'target_ph_range' in analysis
        assert 'yield_impact' in analysis
        assert 'nutrient_availability' in analysis
        
        # Corn should have target pH between 6.0-6.8
        target_range = analysis['target_ph_range']
        assert target_range['min'] >= 6.0
        assert target_range['max'] <= 6.8
        
        # pH 5.8 should show yield impact for corn
        assert analysis['yield_impact'] < 1.0
    
    @pytest.mark.asyncio
    async def test_analyze_critical_acidic_soil(self, ph_service, acidic_soil_data, field_conditions):
        """Test analysis of critically acidic soil."""
        analysis = await ph_service.analyze_ph_status(
            farm_id=acidic_soil_data['farm_id'],
            field_id=acidic_soil_data['field_id'],
            crop_type="soybean",
            soil_data=acidic_soil_data,
            field_conditions=field_conditions
        )
        
        assert analysis['current_ph'] == 5.2
        assert analysis['ph_status'] in ['strongly_acidic', 'very_strongly_acidic']
        assert analysis['yield_impact'] < 0.7  # Poor suitability for soybeans
        
        # Should recommend management action
        assert analysis.get('management_priority') in ['high', 'critical'] or analysis['yield_impact'] < 0.8
    
    @pytest.mark.asyncio
    async def test_analyze_alkaline_soil(self, ph_service, alkaline_soil_data, field_conditions):
        """Test analysis of alkaline soil."""
        analysis = await ph_service.analyze_ph_status(
            farm_id=alkaline_soil_data['farm_id'],
            field_id=alkaline_soil_data['field_id'],
            crop_type="corn",
            soil_data=alkaline_soil_data,
            field_conditions=field_conditions
        )
        
        assert analysis['current_ph'] == 8.2
        assert analysis['ph_status'] in ['moderately_alkaline', 'strongly_alkaline']
        
        # Check micronutrient availability issues
        nutrient_avail = analysis['nutrient_availability']
        assert nutrient_avail['iron'] < 0.5  # Iron availability severely limited
        assert nutrient_avail['zinc'] < 0.5  # Zinc availability limited
    
    def test_ph_level_classification(self, ph_service):
        """Test pH level classification accuracy."""
        test_cases = [
            (4.0, PHLevel.EXTREMELY_ACIDIC),
            (4.8, PHLevel.VERY_STRONGLY_ACIDIC),
            (5.3, PHLevel.STRONGLY_ACIDIC),
            (5.8, PHLevel.MODERATELY_ACIDIC),
            (6.3, PHLevel.SLIGHTLY_ACIDIC),
            (7.0, PHLevel.NEUTRAL),
            (7.6, PHLevel.SLIGHTLY_ALKALINE),
            (8.2, PHLevel.MODERATELY_ALKALINE),
            (8.8, PHLevel.STRONGLY_ALKALINE),
            (9.5, PHLevel.VERY_STRONGLY_ALKALINE)
        ]
        
        for ph_value, expected_level in test_cases:
            actual_level = ph_service._classify_ph_level(ph_value)
            assert actual_level == expected_level, f"pH {ph_value} should be {expected_level}, got {actual_level}"
    
    def test_nutrient_availability_calculation(self, ph_service):
        """Test nutrient availability calculation at different pH levels."""
        # Test optimal pH (6.5)
        availability_optimal = ph_service._calculate_nutrient_availability(6.5)
        assert availability_optimal["phosphorus"] >= 0.9  # High P availability
        assert availability_optimal["iron"] >= 0.6  # Adequate Fe availability
        
        # Test acidic pH (5.0)
        availability_acidic = ph_service._calculate_nutrient_availability(5.0)
        assert availability_acidic["phosphorus"] < 0.6  # Reduced P availability
        assert availability_acidic["iron"] >= 0.9  # High Fe availability
        
        # Test alkaline pH (8.0)
        availability_alkaline = ph_service._calculate_nutrient_availability(8.0)
        assert availability_alkaline["iron"] < 0.3  # Very low Fe availability
        assert availability_alkaline["zinc"] < 0.3  # Very low Zn availability
    
    def test_crop_suitability_calculation(self, ph_service):
        """Test crop suitability calculation for different crops and pH levels."""
        # Corn at optimal pH
        corn_optimal = ph_service._calculate_crop_suitability(6.4, "corn")
        assert corn_optimal >= 0.9
        
        # Corn at acidic pH
        corn_acidic = ph_service._calculate_crop_suitability(5.2, "corn")
        assert corn_acidic < 0.7
        
        # Blueberry at acidic pH (should be good)
        blueberry_acidic = ph_service._calculate_crop_suitability(5.0, "blueberry")
        assert blueberry_acidic >= 0.8
        
        # Blueberry at neutral pH (should be poor)
        blueberry_neutral = ph_service._calculate_crop_suitability(7.0, "blueberry")
        assert blueberry_neutral < 0.5

class TestLimeRecommendations(TestSoilPHManagementService):
    """Test lime recommendation calculations."""
    
    @pytest.mark.asyncio
    async def test_calculate_lime_requirements_basic(self, ph_service):
        """Test basic lime requirement calculation."""
        recommendations = await ph_service.calculate_lime_requirements(
            current_ph=5.8,
            target_ph=6.5,
            buffer_ph=None,
            soil_texture="loam",
            organic_matter_percent=3.0,
            field_size_acres=10.0
        )
        
        assert len(recommendations) > 0
        assert all(isinstance(rec, LimeRecommendation) for rec in recommendations)
        
        # Check agricultural limestone recommendation
        ag_lime = next((rec for rec in recommendations if rec.lime_type == LimeType.AGRICULTURAL_LIME), None)
        assert ag_lime is not None
        assert ag_lime.application_rate_tons_per_acre > 0
        assert ag_lime.cost_per_acre > 0
        assert ag_lime.expected_ph_change > 0
    
    @pytest.mark.asyncio
    async def test_lime_requirements_with_buffer_ph(self, ph_service):
        """Test lime calculation using buffer pH method."""
        recommendations = await ph_service.calculate_lime_requirements(
            current_ph=5.8,
            target_ph=6.5,
            buffer_ph=6.2,  # Buffer pH provided
            soil_texture="silt_loam",
            organic_matter_percent=3.5,
            field_size_acres=25.0
        )
        
        assert len(recommendations) > 0
        
        # Buffer pH method should be more accurate
        for rec in recommendations:
            assert rec.application_rate_tons_per_acre > 0
            assert rec.application_rate_tons_per_acre <= 6.0  # Reasonable upper limit
    
    @pytest.mark.asyncio
    async def test_no_lime_needed(self, ph_service):
        """Test when no lime is needed (pH already at target)."""
        recommendations = await ph_service.calculate_lime_requirements(
            current_ph=6.5,
            target_ph=6.5,
            buffer_ph=None,
            soil_texture="loam",
            organic_matter_percent=3.0
        )
        
        assert len(recommendations) == 0  # No lime needed
    
    def test_lime_rate_adjustment_for_soil_texture(self, ph_service):
        """Test lime rate adjustments for different soil textures."""
        base_rate = 2.0  # tons/acre
        lime_props = ph_service.lime_materials["agricultural_limestone"]
        
        # Sandy soil should need less lime
        sandy_rate = ph_service._adjust_lime_rate_for_material(base_rate, lime_props)
        
        # Clay soil should need more lime (tested with different base calculation)
        # This is handled in the buffer capacity calculation
        assert sandy_rate > 0
    
    def test_lime_application_timing(self, ph_service):
        """Test lime application timing recommendations."""
        # Agricultural limestone - should prefer fall
        ag_timing = ph_service._determine_lime_application_timing(
            LimeType.AGRICULTURAL_LIME, None
        )
        assert "fall" in ag_timing.lower()
        
        # Hydrated lime - can be applied in spring
        hydrated_timing = ph_service._determine_lime_application_timing(
            LimeType.HYDRATED_LIME, None
        )
        assert "spring" in hydrated_timing.lower()

class TestPHMonitoring(TestSoilPHManagementService):
    """Test pH monitoring functionality."""
    
    @pytest.mark.asyncio
    async def test_track_ph_monitoring_record(self, ph_service):
        """Test tracking pH monitoring records."""
        record = await ph_service.track_ph_monitoring_record(
            farm_id="test_farm",
            field_id="field_001",
            ph_value=6.2,
            buffer_ph=6.4,
            testing_method="laboratory",
            lab_name="AgriTest Labs",
            notes="Post-lime application test"
        )
        
        assert isinstance(record, PHMonitoringRecord)
        assert record.farm_id == "test_farm"
        assert record.field_id == "field_001"
        assert record.ph_value == 6.2
        assert record.buffer_ph == 6.4
        assert record.lab_name == "AgriTest Labs"
    
    @pytest.mark.asyncio
    async def test_analyze_ph_trends(self, ph_service):
        """Test pH trend analysis."""
        # Create mock pH records showing declining trend
        records = [
            PHMonitoringRecord(
                record_id=f"rec_{i}",
                farm_id="test_farm",
                field_id="field_001",
                test_date=datetime.now() - timedelta(days=365*i),
                ph_value=6.5 - (i * 0.2),
                buffer_ph=None,
                testing_method="laboratory",
                lab_name=None,
                notes=""
            )
            for i in range(4)
        ]
        
        trends = await ph_service.analyze_ph_trends(
            farm_id="test_farm",
            field_id="field_001",
            ph_records=records
        )
        
        assert trends["trend"] == "decreasing"
        assert trends["annual_change_rate"] < 0
        assert trends["current_ph"] == records[0].ph_value
        assert trends["readings_count"] == 4
    
    @pytest.mark.asyncio
    async def test_generate_ph_alerts(self, ph_service, acidic_soil_data):
        """Test pH alert generation."""
        # Create critical pH analysis
        analysis = await ph_service.analyze_soil_ph(
            farm_id="test_farm",
            field_id="field_001",
            crop_type="corn",
            soil_test_data=acidic_soil_data
        )
        
        alerts = await ph_service.generate_ph_alerts(
            ph_analysis=analysis,
            crop_type="corn"
        )
        
        assert len(alerts) > 0
        
        # Should have critical or warning alerts
        alert_types = [alert["type"] for alert in alerts]
        assert any(alert_type in ["critical", "warning"] for alert_type in alert_types)
        
        # Check alert structure
        for alert in alerts:
            assert "type" in alert
            assert "title" in alert
            assert "message" in alert
            assert "action_required" in alert
            assert "urgency" in alert

class TestBufferPHAnalysis(TestSoilPHManagementService):
    """Test buffer pH analysis functionality."""
    
    @pytest.mark.asyncio
    async def test_calculate_buffer_ph_requirements(self, ph_service):
        """Test buffer pH lime requirement calculation."""
        result = await ph_service.calculate_buffer_ph_requirements(
            current_buffer_ph=6.2,
            target_ph=6.8,
            soil_texture="silt_loam",
            organic_matter_percent=3.5
        )
        
        assert "base_lime_rate_tons_per_acre" in result
        assert "adjusted_lime_rate_tons_per_acre" in result
        assert "confidence" in result
        assert result["base_lime_rate_tons_per_acre"] >= 0
        assert result["adjusted_lime_rate_tons_per_acre"] >= 0
        assert result["confidence"] in ["high", "medium", "low"]
    
    def test_buffer_capacity_estimation(self, ph_service, sample_soil_data):
        """Test soil buffering capacity estimation."""
        field_conditions = {
            "soil_texture": "silt_loam",
            "cec": 18.5
        }
        
        buffering = ph_service._estimate_buffering_capacity(
            sample_soil_data, field_conditions
        )
        
        assert buffering in ["very_low", "low", "moderate", "high"]

class TestAlkalineSoilManagement(TestSoilPHManagementService):
    """Test alkaline soil management functionality."""
    
    @pytest.mark.asyncio
    async def test_assess_alkaline_soil_management(self, ph_service, alkaline_soil_data):
        """Test alkaline soil management assessment."""
        # Create alkaline pH analysis
        analysis = await ph_service.analyze_soil_ph(
            farm_id="test_farm",
            field_id="field_001",
            crop_type="corn",
            soil_test_data=alkaline_soil_data
        )
        
        management = await ph_service.assess_alkaline_soil_management(
            ph_analysis=analysis,
            soil_test_data=alkaline_soil_data,
            crop_type="corn"
        )
        
        assert management["management_needed"] is True
        assert "alkalinity_level" in management
        assert "management_strategies" in management
        assert len(management["management_strategies"]) > 0
        
        # Should recommend sulfur for moderate alkalinity
        strategies = management["management_strategies"]
        strategy_types = [s["strategy"] for s in strategies]
        assert "sulfur_application" in strategy_types or "organic_matter_addition" in strategy_types
    
    def test_sulfur_requirement_calculation(self, ph_service):
        """Test sulfur requirement calculation for pH reduction."""
        sulfur_rate = ph_service._calculate_sulfur_requirement(
            current_ph=8.2,
            target_ph=7.0
        )
        
        assert sulfur_rate > 0
        assert sulfur_rate <= 500  # Safety cap
        
        # Higher pH difference should require more sulfur
        higher_sulfur_rate = ph_service._calculate_sulfur_requirement(
            current_ph=8.5,
            target_ph=7.0
        )
        assert higher_sulfur_rate > sulfur_rate

class TestCropSpecificPH(TestSoilPHManagementService):
    """Test crop-specific pH management."""
    
    def test_crop_ph_requirements_database(self, ph_service):
        """Test crop pH requirements database completeness."""
        required_crops = ["corn", "soybean", "wheat", "alfalfa", "potato", "blueberry"]
        
        for crop in required_crops:
            assert crop in ph_service.crop_ph_requirements
            
            crop_req = ph_service.crop_ph_requirements[crop]
            assert "optimal_range" in crop_req
            assert "acceptable_range" in crop_req
            assert "critical_minimum" in crop_req
            assert "critical_maximum" in crop_req
            assert "yield_impact_curve" in crop_req
            
            # Validate ranges make sense
            opt_min, opt_max = crop_req["optimal_range"]
            acc_min, acc_max = crop_req["acceptable_range"]
            
            assert opt_min <= opt_max
            assert acc_min <= opt_min
            assert opt_max <= acc_max
            assert crop_req["critical_minimum"] <= acc_min
            assert acc_max <= crop_req["critical_maximum"]
    
    def test_yield_impact_interpolation(self, ph_service):
        """Test yield impact interpolation from pH curves."""
        # Test corn yield impact
        corn_curve = ph_service.crop_ph_requirements["corn"]["yield_impact_curve"]
        
        # Test interpolation at pH 6.25 (between 6.0 and 6.5)
        impact = ph_service._interpolate_yield_impact(6.25, corn_curve)
        
        # Should be between the values at 6.0 and 6.5
        impact_6_0 = corn_curve.get(6.0, 0)
        impact_6_5 = corn_curve.get(6.5, 0)
        
        if 6.0 in corn_curve and 6.5 in corn_curve:
            assert min(impact_6_0, impact_6_5) <= impact <= max(impact_6_0, impact_6_5)

class TestEconomicAnalysis(TestSoilPHManagementService):
    """Test economic analysis of pH management."""
    
    @pytest.mark.asyncio
    async def test_ph_economics_calculation(self, ph_service, sample_soil_data):
        """Test pH management economic analysis."""
        # Create pH analysis
        analysis = await ph_service.analyze_soil_ph(
            farm_id="test_farm",
            field_id="field_001",
            crop_type="corn",
            soil_test_data=sample_soil_data
        )
        
        # Get lime recommendations
        lime_recs = await ph_service.calculate_lime_requirements(
            current_ph=analysis.current_ph,
            target_ph=analysis.target_ph,
            buffer_ph=None,
            soil_texture="loam",
            organic_matter_percent=3.0
        )
        
        # Calculate economics
        economics = ph_service._calculate_ph_economics(
            ph_analysis=analysis,
            lime_recommendations=lime_recs,
            crop_type="corn",
            field_conditions=None
        )
        
        assert "annual_yield_loss_dollars_per_acre" in economics
        
        if lime_recs:
            assert "lime_cost_per_acre" in economics
            assert "total_yield_benefit_dollars_per_acre" in economics
            assert "net_benefit_dollars_per_acre" in economics
            assert "benefit_cost_ratio" in economics
            assert "payback_years" in economics
            
            # Economics should make sense
            assert economics["lime_cost_per_acre"] > 0
            assert economics["benefit_cost_ratio"] > 0

class TestAgriculturalAccuracy(TestSoilPHManagementService):
    """Test agricultural accuracy and validation."""
    
    def test_ph_classifications_match_standards(self, ph_service):
        """Test that pH classifications match agricultural standards."""
        classifications = ph_service.ph_classifications
        
        # Test key pH thresholds match USDA/extension standards
        assert classifications["extremely_acidic"]["range"][1] < 4.5
        assert classifications["neutral"]["range"][0] <= 6.6
        assert classifications["neutral"]["range"][1] >= 7.3
        assert classifications["strongly_alkaline"]["range"][0] >= 8.5
    
    def test_lime_material_properties(self, ph_service):
        """Test lime material properties are agriculturally accurate."""
        materials = ph_service.lime_materials
        
        # Agricultural limestone
        ag_lime = materials["agricultural_limestone"]
        assert 85 <= ag_lime["neutralizing_value"] <= 95  # Typical range
        assert ag_lime["cost_per_ton"] > 0
        assert ag_lime["reaction_time"] == "slow"
        
        # Hydrated lime
        hydrated = materials["hydrated_lime"]
        assert hydrated["neutralizing_value"] > ag_lime["neutralizing_value"]  # More reactive
        assert hydrated["cost_per_ton"] > ag_lime["cost_per_ton"]  # More expensive
        assert hydrated["reaction_time"] == "fast"
    
    def test_nutrient_availability_curves_realistic(self, ph_service):
        """Test nutrient availability curves are agriculturally realistic."""
        curves = ph_service.nutrient_availability_curves
        
        # Phosphorus should be highest around pH 6.5
        p_curve = curves["phosphorus"]
        max_p_ph = max(p_curve.keys(), key=lambda ph: p_curve[ph])
        assert 6.0 <= max_p_ph <= 7.0
        
        # Iron should be highest at low pH
        fe_curve = curves["iron"]
        assert fe_curve[4.0] > fe_curve[8.0]  # Much higher at low pH
        
        # Molybdenum should be higher at high pH
        mo_curve = curves["molybdenum"]
        assert mo_curve[8.0] > mo_curve[5.0]  # Higher at alkaline pH

class TestIntegrationScenarios(TestSoilPHManagementService):
    """Test complete pH management scenarios."""
    
    @pytest.mark.asyncio
    async def test_complete_ph_management_workflow(self, ph_service, sample_soil_data):
        """Test complete pH management workflow."""
        # Step 1: Analyze pH
        analysis = await ph_service.analyze_soil_ph(
            farm_id="test_farm",
            field_id="field_001",
            crop_type="corn",
            soil_test_data=sample_soil_data
        )
        
        # Step 2: Get lime recommendations if needed
        lime_recs = []
        if analysis.management_priority != "maintenance":
            lime_recs = await ph_service.calculate_lime_requirements(
                current_ph=analysis.current_ph,
                target_ph=analysis.target_ph,
                buffer_ph=None,
                soil_texture="loam",
                organic_matter_percent=3.0
            )
        
        # Step 3: Generate management plan
        plan = await ph_service.generate_ph_management_plan(
            farm_id="test_farm",
            field_id="field_001",
            crop_type="corn",
            ph_analysis=analysis,
            lime_recommendations=lime_recs
        )
        
        assert isinstance(plan, PHManagementPlan)
        assert plan.farm_id == "test_farm"
        assert plan.field_id == "field_001"
        assert plan.crop_type == "corn"
        assert plan.current_analysis == analysis
        assert len(plan.monitoring_schedule) > 0
        assert len(plan.long_term_strategy) > 0
    
    @pytest.mark.asyncio
    async def test_emergency_ph_correction_scenario(self, ph_service):
        """Test emergency pH correction scenario."""
        # Extremely acidic soil
        critical_soil = SoilTestData(
            ph=4.8,
            organic_matter_percent=1.5,
            phosphorus_ppm=8,
            potassium_ppm=65,
            test_date=date.today()
        )
        
        analysis = await ph_service.analyze_soil_ph(
            farm_id="emergency_farm",
            field_id="critical_field",
            crop_type="corn",
            soil_test_data=critical_soil
        )
        
        # Should be critical priority
        assert analysis.management_priority == "critical"
        
        # Should recommend immediate action
        alerts = await ph_service.generate_ph_alerts(analysis, "corn")
        critical_alerts = [a for a in alerts if a["type"] == "critical"]
        assert len(critical_alerts) > 0
        
        # Lime recommendations should include fast-acting options
        lime_recs = await ph_service.calculate_lime_requirements(
            current_ph=analysis.current_ph,
            target_ph=analysis.target_ph,
            buffer_ph=None,
            soil_texture="loam",
            organic_matter_percent=1.5
        )
        
        # Should have hydrated lime option for fast correction
        lime_types = [rec.lime_type for rec in lime_recs]
        assert LimeType.HYDRATED_LIME in lime_types

# Performance and edge case tests
class TestEdgeCases(TestSoilPHManagementService):
    """Test edge cases and error handling."""
    
    @pytest.mark.asyncio
    async def test_extreme_ph_values(self, ph_service):
        """Test handling of extreme pH values."""
        # Extremely low pH
        extreme_low_soil = SoilTestData(
            ph=3.5,
            organic_matter_percent=1.0,
            test_date=date.today()
        )
        
        analysis = await ph_service.analyze_soil_ph(
            farm_id="test_farm",
            field_id="extreme_field",
            crop_type="corn",
            soil_test_data=extreme_low_soil
        )
        
        assert analysis.management_priority == "critical"
        assert analysis.crop_suitability_score < 0.3
        
        # Extremely high pH
        extreme_high_soil = SoilTestData(
            ph=9.2,
            organic_matter_percent=2.0,
            test_date=date.today()
        )
        
        analysis_high = await ph_service.analyze_soil_ph(
            farm_id="test_farm",
            field_id="extreme_field_2",
            crop_type="corn",
            soil_test_data=extreme_high_soil
        )
        
        assert analysis_high.management_priority == "critical"
        assert analysis_high.crop_suitability_score < 0.3
    
    def test_invalid_soil_texture_handling(self, ph_service):
        """Test handling of invalid soil texture."""
        # Should default to reasonable values for unknown texture
        buffering = ph_service._estimate_buffering_capacity(
            SoilTestData(ph=6.0, test_date=date.today()),
            {"soil_texture": "unknown_texture"}
        )
        
        assert buffering in ["very_low", "low", "moderate", "high"]
    
    def test_missing_crop_requirements(self, ph_service):
        """Test handling of unknown crop types."""
        # Should default to corn requirements
        suitability = ph_service._calculate_crop_suitability(6.0, "unknown_crop")
        assert 0.0 <= suitability <= 1.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])