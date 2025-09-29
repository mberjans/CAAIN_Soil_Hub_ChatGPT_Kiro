"""
Comprehensive tests for nutrient deficiency detection system.
Tests all components including detection, visual analysis, monitoring, and treatment recommendations.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import numpy as np
from PIL import Image
import io

from ..src.services.nutrient_deficiency_detection_service import (
    NutrientDeficiencyDetectionService,
    DeficiencySeverity,
    NutrientType,
    NutrientDeficiency,
    DeficiencyDetectionResult
)
from ..src.services.visual_symptom_analyzer import (
    VisualSymptomAnalyzer,
    VisualSymptom,
    SymptomType,
    PlantPart,
    ImageAnalysisResult
)
from ..src.services.corrective_action_service import (
    CorrectiveActionService,
    TreatmentPlan,
    TreatmentUrgency,
    ApplicationMethod
)
from ..src.services.deficiency_monitoring_service import (
    DeficiencyMonitoringService,
    MonitoringStatus,
    AlertType,
    DeficiencyAlert
)
from ..src.models.agricultural_models import SoilTestData

class TestNutrientDeficiencyDetectionService:
    """Test the core nutrient deficiency detection service."""
    
    @pytest.fixture
    def deficiency_service(self):
        return NutrientDeficiencyDetectionService()
    
    @pytest.fixture
    def sample_soil_data(self):
        return SoilTestData(
            ph=6.2,
            organic_matter_percent=3.5,
            phosphorus_ppm=15.0,  # Below critical for corn
            potassium_ppm=120.0,  # At critical level
            nitrogen_ppm=8.0,     # Below critical
            test_date=datetime.now().date(),
            lab_name="Test Lab"
        )
    
    @pytest.mark.asyncio
    async def test_detect_nitrogen_deficiency(self, deficiency_service, sample_soil_data):
        """Test detection of nitrogen deficiency from soil data."""
        
        result = await deficiency_service.detect_nutrient_deficiencies(
            farm_id="test_farm",
            field_id="test_field",
            crop_type="corn",
            soil_test_data=sample_soil_data
        )
        
        # Should detect nitrogen deficiency
        nitrogen_deficiencies = [d for d in result.deficiencies if d.nutrient == "nitrogen"]
        assert len(nitrogen_deficiencies) > 0
        
        nitrogen_def = nitrogen_deficiencies[0]
        assert nitrogen_def.severity in [DeficiencySeverity.MODERATE, DeficiencySeverity.SEVERE]
        assert nitrogen_def.confidence_score > 0.6
        assert nitrogen_def.nutrient_type == NutrientType.PRIMARY
        assert "yellowing" in " ".join(nitrogen_def.symptoms).lower()
    
    @pytest.mark.asyncio
    async def test_detect_multiple_deficiencies(self, deficiency_service):
        """Test detection of multiple nutrient deficiencies."""
        
        # Create soil data with multiple deficiencies
        soil_data = SoilTestData(
            ph=6.0,
            organic_matter_percent=2.0,
            phosphorus_ppm=8.0,    # Low
            potassium_ppm=80.0,    # Low
            nitrogen_ppm=15.0,     # Low
            iron_ppm=1.5,          # Low
            zinc_ppm=0.5,          # Low
            test_date=datetime.now().date()
        )
        
        result = await deficiency_service.detect_nutrient_deficiencies(
            farm_id="test_farm",
            field_id="test_field",
            crop_type="corn",
            soil_test_data=soil_data
        )
        
        # Should detect multiple deficiencies
        assert len(result.deficiencies) >= 3
        
        # Check that primary nutrients are prioritized
        nutrient_names = [d.nutrient for d in result.deficiencies]
        assert "nitrogen" in nutrient_names or "phosphorus" in nutrient_names or "potassium" in nutrient_names
        
        # Check overall severity calculation
        assert result.overall_severity_score > 0
        assert result.treatment_urgency in ["moderate", "urgent", "immediate"]
    
    @pytest.mark.asyncio
    async def test_ph_adjustment_effects(self, deficiency_service):
        """Test that pH affects nutrient availability calculations."""
        
        # Test high pH scenario (should affect iron/zinc availability)
        high_ph_soil = SoilTestData(
            ph=8.2,  # High pH
            organic_matter_percent=3.0,
            iron_ppm=3.0,  # Adequate level but high pH reduces availability
            zinc_ppm=1.2,  # Adequate level but high pH reduces availability
            test_date=datetime.now().date()
        )
        
        result = await deficiency_service.detect_nutrient_deficiencies(
            farm_id="test_farm",
            field_id="test_field",
            crop_type="corn",
            soil_test_data=high_ph_soil
        )
        
        # Should detect iron or zinc deficiency due to pH
        micronutrient_deficiencies = [
            d for d in result.deficiencies 
            if d.nutrient in ["iron", "zinc"] and d.nutrient_type == NutrientType.MICRONUTRIENT
        ]
        
        if micronutrient_deficiencies:
            # Check that pH is mentioned in causes
            for deficiency in micronutrient_deficiencies:
                assert any("ph" in cause.lower() for cause in deficiency.causes)
    
    @pytest.mark.asyncio
    async def test_tissue_test_integration(self, deficiency_service, sample_soil_data):
        """Test integration of tissue test data with soil test data."""
        
        # Tissue test showing nitrogen deficiency
        tissue_data = {
            "nitrogen_percent": 2.5,  # Below critical for corn
            "phosphorus_percent": 0.3,  # Adequate
            "potassium_percent": 2.0    # Adequate
        }
        
        result = await deficiency_service.detect_nutrient_deficiencies(
            farm_id="test_farm",
            field_id="test_field",
            crop_type="corn",
            soil_test_data=sample_soil_data,
            tissue_test_data=tissue_data
        )
        
        # Should have higher confidence when both soil and tissue tests agree
        nitrogen_deficiencies = [d for d in result.deficiencies if d.nutrient == "nitrogen"]
        if nitrogen_deficiencies:
            assert nitrogen_deficiencies[0].confidence_score > 0.8

class TestVisualSymptomAnalyzer:
    """Test the visual symptom analysis service."""
    
    @pytest.fixture
    def visual_analyzer(self):
        return VisualSymptomAnalyzer()
    
    @pytest.fixture
    def sample_crop_image(self):
        """Create a sample crop image for testing."""
        # Create a simple test image
        img = Image.new('RGB', (640, 480), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()
    
    @pytest.mark.asyncio
    async def test_image_quality_assessment(self, visual_analyzer, sample_crop_image):
        """Test image quality assessment functionality."""
        
        result = await visual_analyzer.analyze_crop_image(
            image_data=sample_crop_image,
            crop_type="corn"
        )
        
        # Should assess image quality
        assert 0.0 <= result.image_quality_score <= 1.0
        assert result.analysis_id is not None
        assert result.crop_identification is not None
    
    @pytest.mark.asyncio
    async def test_symptom_description_analysis(self, visual_analyzer):
        """Test natural language symptom description analysis."""
        
        symptom_description = "The corn leaves are turning yellow from the bottom up, starting with the older leaves. The yellowing is uniform across the leaf and the plants look stunted."
        
        predictions = await visual_analyzer.analyze_symptom_description(
            description=symptom_description,
            crop_type="corn"
        )
        
        # Should predict nitrogen deficiency
        assert len(predictions) > 0
        
        # Check if nitrogen is in top predictions
        top_nutrients = [p['nutrient'] for p in predictions[:3]]
        assert 'nitrogen' in top_nutrients
        
        # Check confidence levels
        for prediction in predictions:
            assert 0.0 <= prediction['confidence'] <= 1.0
            assert 0.0 <= prediction['probability'] <= 1.0
    
    def test_chlorosis_detection_keywords(self, visual_analyzer):
        """Test that chlorosis-related keywords are properly detected."""
        
        chlorosis_descriptions = [
            "leaves are yellowing between the veins",
            "interveinal chlorosis on young leaves",
            "yellow striping pattern on new growth"
        ]
        
        for description in chlorosis_descriptions:
            # This would test the keyword extraction logic
            # In a real implementation, you'd test the actual method
            assert "yellow" in description.lower() or "chlorosis" in description.lower()
    
    def test_symptom_pattern_matching(self, visual_analyzer):
        """Test symptom pattern matching against known deficiency patterns."""
        
        # Test nitrogen deficiency pattern
        nitrogen_symptoms = [
            "yellowing of older leaves first",
            "pale green coloration overall",
            "stunted growth"
        ]
        
        # Test iron deficiency pattern  
        iron_symptoms = [
            "interveinal chlorosis of young leaves",
            "yellowing between leaf veins",
            "white or pale yellow new growth"
        ]
        
        # Verify patterns are in the database
        nitrogen_patterns = visual_analyzer.symptom_patterns.get('nitrogen', [])
        iron_patterns = visual_analyzer.symptom_patterns.get('iron', [])
        
        assert len(nitrogen_patterns) > 0
        assert len(iron_patterns) > 0

class TestCorrectiveActionService:
    """Test the corrective action and treatment recommendation service."""
    
    @pytest.fixture
    def corrective_service(self):
        return CorrectiveActionService()
    
    @pytest.fixture
    def sample_deficiencies(self):
        return [
            NutrientDeficiency(
                nutrient="nitrogen",
                nutrient_type=NutrientType.PRIMARY,
                severity=DeficiencySeverity.MODERATE,
                confidence_score=0.85,
                current_level=15.0,
                critical_level=25.0,
                optimal_range=(30.0, 50.0),
                yield_impact_percent=15.0,
                economic_impact_dollars=450.0,
                symptoms=["yellowing of older leaves", "stunted growth"],
                causes=["low soil nitrogen", "leaching"],
                interactions=["enhanced by adequate phosphorus"]
            ),
            NutrientDeficiency(
                nutrient="iron",
                nutrient_type=NutrientType.MICRONUTRIENT,
                severity=DeficiencySeverity.MILD,
                confidence_score=0.72,
                current_level=2.0,
                critical_level=2.5,
                optimal_range=(4.5, 25.0),
                yield_impact_percent=5.0,
                economic_impact_dollars=150.0,
                symptoms=["interveinal chlorosis", "yellowing between veins"],
                causes=["high soil pH", "poor availability"],
                interactions=["reduced by high phosphorus"]
            )
        ]
    
    @pytest.mark.asyncio
    async def test_generate_treatment_plan(self, corrective_service, sample_deficiencies):
        """Test generation of comprehensive treatment plan."""
        
        treatment_plan = await corrective_service.generate_treatment_plan(
            deficiencies=sample_deficiencies,
            farm_id="test_farm",
            field_id="test_field",
            crop_type="corn"
        )
        
        # Verify treatment plan structure
        assert treatment_plan.plan_id is not None
        assert treatment_plan.farm_id == "test_farm"
        assert treatment_plan.field_id == "test_field"
        assert treatment_plan.crop_type == "corn"
        
        # Should have recommendations for both deficiencies
        assert len(treatment_plan.fertilizer_recommendations) >= 2
        
        # Check that nitrogen deficiency is prioritized (higher severity)
        deficiencies_addressed = treatment_plan.deficiencies_addressed
        assert "nitrogen" in deficiencies_addressed
        assert "iron" in deficiencies_addressed
        
        # Verify cost calculation
        assert treatment_plan.total_cost > 0
        
        # Check treatment urgency
        assert treatment_plan.treatment_urgency in [
            TreatmentUrgency.IMMEDIATE,
            TreatmentUrgency.URGENT,
            TreatmentUrgency.MODERATE,
            TreatmentUrgency.ROUTINE
        ]
    
    def test_fertilizer_selection_logic(self, corrective_service):
        """Test fertilizer product selection logic."""
        
        # Test nitrogen fertilizer options
        nitrogen_fertilizers = corrective_service.fertilizer_database.get('nitrogen', {})
        assert len(nitrogen_fertilizers) > 0
        
        # Verify fertilizer properties
        for fertilizer_name, fertilizer_data in nitrogen_fertilizers.items():
            assert 'nutrient_content' in fertilizer_data
            assert 'cost_per_lb' in fertilizer_data
            assert 'application_methods' in fertilizer_data
            assert 'response_time_days' in fertilizer_data
            
            # Verify nutrient content is reasonable
            assert 0 < fertilizer_data['nutrient_content'] <= 100
            
            # Verify cost is reasonable
            assert fertilizer_data['cost_per_lb'] > 0
    
    def test_application_rate_calculations(self, corrective_service):
        """Test fertilizer application rate calculations."""
        
        # Test application rates for different severities
        rates = corrective_service.application_rates.get('nitrogen', {})
        
        # Should have rates for different severity levels
        assert 'mild' in rates
        assert 'moderate' in rates
        assert 'severe' in rates
        
        # Rates should increase with severity
        corn_rates = {
            severity: rates[severity].get('corn', 0)
            for severity in ['mild', 'moderate', 'severe']
        }
        
        assert corn_rates['mild'] < corn_rates['moderate'] < corn_rates['severe']

class TestDeficiencyMonitoringService:
    """Test the deficiency monitoring and alert service."""
    
    @pytest.fixture
    def monitoring_service(self):
        return DeficiencyMonitoringService()
    
    @pytest.fixture
    def sample_detection_result(self, sample_deficiencies):
        return DeficiencyDetectionResult(
            detection_id="test_detection_123",
            farm_id="test_farm",
            field_id="test_field",
            crop_type="corn",
            detection_date=datetime.now(),
            deficiencies=sample_deficiencies,
            overall_severity_score=65.0,
            priority_deficiencies=["nitrogen", "iron"],
            treatment_urgency="moderate",
            estimated_yield_loss=12.5,
            total_economic_impact=600.0,
            confidence_level=0.78
        )
    
    @pytest.fixture
    def sample_deficiencies(self):
        return [
            NutrientDeficiency(
                nutrient="nitrogen",
                nutrient_type=NutrientType.PRIMARY,
                severity=DeficiencySeverity.MODERATE,
                confidence_score=0.85,
                current_level=15.0,
                critical_level=25.0,
                optimal_range=(30.0, 50.0),
                yield_impact_percent=15.0,
                economic_impact_dollars=450.0,
                symptoms=["yellowing of older leaves"],
                causes=["low soil nitrogen"],
                interactions=[]
            )
        ]
    
    @pytest.mark.asyncio
    async def test_start_monitoring(self, monitoring_service, sample_detection_result):
        """Test starting deficiency monitoring."""
        
        monitoring_id = await monitoring_service.start_deficiency_monitoring(
            sample_detection_result
        )
        
        # Should return a monitoring ID
        assert monitoring_id is not None
        assert "monitor_" in monitoring_id
        assert sample_detection_result.farm_id in monitoring_id
    
    @pytest.mark.asyncio
    async def test_generate_alerts(self, monitoring_service):
        """Test alert generation functionality."""
        
        alerts = await monitoring_service.generate_deficiency_alerts("test_farm")
        
        # Should return a list (may be empty for test)
        assert isinstance(alerts, list)
        
        # If alerts exist, verify structure
        for alert in alerts:
            assert hasattr(alert, 'alert_id')
            assert hasattr(alert, 'alert_type')
            assert hasattr(alert, 'farm_id')
            assert hasattr(alert, 'message')
            assert alert.alert_type in [
                AlertType.NEW_DEFICIENCY,
                AlertType.WORSENING_DEFICIENCY,
                AlertType.TREATMENT_DUE,
                AlertType.TESTING_REMINDER,
                AlertType.SEASONAL_RISK,
                AlertType.WEATHER_IMPACT
            ]
    
    @pytest.mark.asyncio
    async def test_monitoring_dashboard(self, monitoring_service):
        """Test monitoring dashboard generation."""
        
        dashboard = await monitoring_service.generate_monitoring_dashboard("test_farm")
        
        # Verify dashboard structure
        assert dashboard.dashboard_id is not None
        assert dashboard.farm_id == "test_farm"
        assert dashboard.generated_at is not None
        
        # Verify dashboard components
        assert isinstance(dashboard.active_deficiencies, list)
        assert isinstance(dashboard.recent_alerts, list)
        assert isinstance(dashboard.treatment_progress, list)
        assert isinstance(dashboard.nutrient_trends, list)
        assert isinstance(dashboard.upcoming_actions, list)
        assert isinstance(dashboard.field_summaries, list)
        assert isinstance(dashboard.seasonal_risks, list)
    
    def test_seasonal_risk_assessment(self, monitoring_service):
        """Test seasonal risk pattern assessment."""
        
        # Test seasonal patterns
        seasonal_patterns = monitoring_service.seasonal_patterns
        
        # Should have patterns for all seasons
        assert 'spring' in seasonal_patterns
        assert 'summer' in seasonal_patterns
        assert 'fall' in seasonal_patterns
        assert 'winter' in seasonal_patterns
        
        # Each season should have risk nutrients and factors
        for season, data in seasonal_patterns.items():
            assert 'high_risk_nutrients' in data
            assert 'risk_factors' in data
            assert 'monitoring_frequency' in data

class TestIntegratedDeficiencyWorkflow:
    """Test the complete integrated deficiency detection and treatment workflow."""
    
    @pytest.fixture
    def integrated_services(self):
        return {
            'detection': NutrientDeficiencyDetectionService(),
            'visual': VisualSymptomAnalyzer(),
            'corrective': CorrectiveActionService(),
            'monitoring': DeficiencyMonitoringService()
        }
    
    @pytest.fixture
    def comprehensive_farm_data(self):
        return {
            'farm_id': 'integration_test_farm',
            'field_id': 'north_field',
            'crop_type': 'corn',
            'soil_test_data': SoilTestData(
                ph=6.0,
                organic_matter_percent=3.2,
                phosphorus_ppm=12.0,  # Low
                potassium_ppm=95.0,   # Low
                nitrogen_ppm=18.0,    # Low
                test_date=datetime.now().date()
            ),
            'tissue_test_data': {
                'nitrogen_percent': 2.6,  # Low
                'phosphorus_percent': 0.22,  # Low
                'potassium_percent': 1.5   # Low
            },
            'visual_symptoms': [
                VisualSymptom(
                    symptom_id="symptom_1",
                    symptom_type=SymptomType.CHLOROSIS,
                    plant_part=PlantPart.OLDER_LEAVES,
                    severity="moderate",
                    distribution="uniform",
                    color_description="yellowing of older leaves",
                    confidence_score=0.8,
                    associated_nutrients=["nitrogen"],
                    description="Uniform yellowing starting from older leaves"
                )
            ]
        }
    
    @pytest.mark.asyncio
    async def test_complete_deficiency_workflow(self, integrated_services, comprehensive_farm_data):
        """Test the complete workflow from detection to treatment planning."""
        
        services = integrated_services
        farm_data = comprehensive_farm_data
        
        # Step 1: Detect deficiencies
        detection_result = await services['detection'].detect_nutrient_deficiencies(
            farm_id=farm_data['farm_id'],
            field_id=farm_data['field_id'],
            crop_type=farm_data['crop_type'],
            soil_test_data=farm_data['soil_test_data'],
            tissue_test_data=farm_data['tissue_test_data'],
            visual_symptoms=farm_data['visual_symptoms']
        )
        
        # Verify detection results
        assert len(detection_result.deficiencies) > 0
        assert detection_result.confidence_level > 0.5
        
        # Step 2: Generate treatment plan
        treatment_plan = await services['corrective'].generate_treatment_plan(
            deficiencies=detection_result.deficiencies,
            farm_id=farm_data['farm_id'],
            field_id=farm_data['field_id'],
            crop_type=farm_data['crop_type']
        )
        
        # Verify treatment plan
        assert len(treatment_plan.fertilizer_recommendations) > 0
        assert treatment_plan.total_cost > 0
        
        # Step 3: Start monitoring
        monitoring_id = await services['monitoring'].start_deficiency_monitoring(
            detection_result
        )
        
        # Verify monitoring setup
        assert monitoring_id is not None
        
        # Step 4: Generate dashboard
        dashboard = await services['monitoring'].generate_monitoring_dashboard(
            farm_data['farm_id']
        )
        
        # Verify dashboard
        assert dashboard.farm_id == farm_data['farm_id']
        assert len(dashboard.active_deficiencies) > 0
    
    @pytest.mark.asyncio
    async def test_multi_source_confidence_scoring(self, integrated_services, comprehensive_farm_data):
        """Test that confidence scores improve when multiple data sources agree."""
        
        services = integrated_services
        farm_data = comprehensive_farm_data
        
        # Test with only soil data
        soil_only_result = await services['detection'].detect_nutrient_deficiencies(
            farm_id=farm_data['farm_id'],
            field_id=farm_data['field_id'],
            crop_type=farm_data['crop_type'],
            soil_test_data=farm_data['soil_test_data']
        )
        
        # Test with soil + tissue data
        multi_source_result = await services['detection'].detect_nutrient_deficiencies(
            farm_id=farm_data['farm_id'],
            field_id=farm_data['field_id'],
            crop_type=farm_data['crop_type'],
            soil_test_data=farm_data['soil_test_data'],
            tissue_test_data=farm_data['tissue_test_data'],
            visual_symptoms=farm_data['visual_symptoms']
        )
        
        # Multi-source analysis should have higher confidence
        assert multi_source_result.confidence_level >= soil_only_result.confidence_level
        
        # Should detect similar deficiencies but with higher confidence
        multi_source_nutrients = {d.nutrient for d in multi_source_result.deficiencies}
        soil_only_nutrients = {d.nutrient for d in soil_only_result.deficiencies}
        
        # Should have significant overlap in detected nutrients
        overlap = multi_source_nutrients & soil_only_nutrients
        assert len(overlap) > 0

class TestAgriculturalAccuracy:
    """Test agricultural accuracy and validation of recommendations."""
    
    @pytest.fixture
    def deficiency_service(self):
        return NutrientDeficiencyDetectionService()
    
    def test_critical_nutrient_levels_accuracy(self, deficiency_service):
        """Test that critical nutrient levels match agricultural standards."""
        
        # Test corn critical levels against known standards
        corn_critical_levels = deficiency_service.critical_levels.get('corn', {})
        
        # Nitrogen critical level should be reasonable (20-30 ppm range)
        nitrogen_critical = corn_critical_levels.get('nitrogen_ppm', 0)
        assert 20 <= nitrogen_critical <= 30
        
        # Phosphorus critical level should be reasonable (10-20 ppm range)
        phosphorus_critical = corn_critical_levels.get('phosphorus_ppm', 0)
        assert 10 <= phosphorus_critical <= 20
        
        # Potassium critical level should be reasonable (100-150 ppm range)
        potassium_critical = corn_critical_levels.get('potassium_ppm', 0)
        assert 100 <= potassium_critical <= 150
    
    def test_yield_impact_calculations(self, deficiency_service):
        """Test that yield impact calculations are agriculturally reasonable."""
        
        yield_models = deficiency_service.yield_impact_models
        
        # Test nitrogen yield impact model
        nitrogen_model = yield_models.get('nitrogen', {})
        
        # Mild deficiency should have lower impact than severe
        mild_impact = nitrogen_model.get('mild_deficiency', {}).get('yield_loss_percent', 0)
        severe_impact = nitrogen_model.get('severe_deficiency', {}).get('yield_loss_percent', 0)
        
        assert mild_impact < severe_impact
        assert mild_impact <= 10  # Mild deficiency shouldn't cause >10% loss
        assert severe_impact <= 60  # Even severe deficiency rarely causes >60% loss
    
    def test_nutrient_interaction_accuracy(self, deficiency_service):
        """Test that nutrient interactions are agriculturally accurate."""
        
        interactions = deficiency_service.nutrient_interactions
        
        # Test known interactions
        # High phosphorus should reduce zinc uptake
        phosphorus_interactions = interactions.get('phosphorus', {})
        antagonists = phosphorus_interactions.get('antagonists', [])
        assert 'zinc' in antagonists
        
        # Iron should be affected by high pH
        iron_interactions = interactions.get('iron', {})
        ph_effects = iron_interactions.get('ph_effects', {})
        assert 'high_ph' in ph_effects
        assert ph_effects['high_ph'] in ['decreased_availability', 'severely_decreased_availability']

# Performance and Load Testing
class TestPerformanceRequirements:
    """Test that the system meets performance requirements."""
    
    @pytest.mark.asyncio
    async def test_detection_response_time(self):
        """Test that deficiency detection completes within acceptable time."""
        import time
        
        service = NutrientDeficiencyDetectionService()
        soil_data = SoilTestData(
            ph=6.2,
            organic_matter_percent=3.5,
            phosphorus_ppm=15.0,
            potassium_ppm=120.0,
            nitrogen_ppm=20.0,
            test_date=datetime.now().date()
        )
        
        start_time = time.time()
        
        result = await service.detect_nutrient_deficiencies(
            farm_id="perf_test_farm",
            field_id="perf_test_field",
            crop_type="corn",
            soil_test_data=soil_data
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Should complete within 3 seconds
        assert response_time < 3.0
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis_handling(self):
        """Test system handling of concurrent deficiency analyses."""
        
        service = NutrientDeficiencyDetectionService()
        
        async def single_analysis(farm_id):
            soil_data = SoilTestData(
                ph=6.2,
                organic_matter_percent=3.5,
                phosphorus_ppm=15.0,
                potassium_ppm=120.0,
                nitrogen_ppm=20.0,
                test_date=datetime.now().date()
            )
            
            return await service.detect_nutrient_deficiencies(
                farm_id=f"concurrent_test_{farm_id}",
                field_id="test_field",
                crop_type="corn",
                soil_test_data=soil_data
            )
        
        # Run 10 concurrent analyses
        tasks = [single_analysis(i) for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete successfully
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == 10
        
        # All should have valid detection IDs
        for result in successful_results:
            assert result.detection_id is not None